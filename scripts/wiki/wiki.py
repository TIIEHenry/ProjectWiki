#!/usr/bin/env python3
"""Small, dependency-free checks for a repository's Markdown wiki.

Supported Markdown: inline/reference links, images, ATX headings, explicit HTML
anchors, and standalone @path imports in AGENTS.md / CLAUDE.md. This is not a
Markdown renderer or a proof of the prose's correctness.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


VERSION = "0.1.0"
DEFAULT_CONFIG = "docs/wiki.json"
DEFAULT_EXCLUDES = {".git", ".venv", "venv", "node_modules", "__pycache__"}
ROOT_ROLES = {"knowledge", "process", "archive"}
PAGE_ROLES = ROOT_ROLES | {"entry", "redirect", "reference", "guide", "generated"}
DEFAULT_DECISION_PATTERNS = ["docs/decisions/*", "*/docs/decisions/*"]
REVIEW_TRAILER = "Docs-Reviewed"
HISTORY_SCAN_LIMIT = 2000
HOOK_MARKERS = {"pre-commit": "check --staged", "commit-msg": "remind --staged"}


class WikiError(Exception):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative_path(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise WikiError(f"Expected a repository-relative POSIX path, got {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value == ".":
        raise WikiError(f"Path must stay inside the selected root: {value}")
    return path.as_posix()


def under(path: str, directory: str) -> bool:
    return path == directory or path.startswith(directory.rstrip("/") + "/")


def run_git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=False
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise WikiError(f"Git snapshot unavailable: {message or 'git command failed'}")
    return result.stdout


class Snapshot:
    """Read one namespace; index reads use captured blob IDs, never the worktree."""

    def __init__(self, root: Path, staged: bool = False):
        self.root = root.resolve()
        self.staged = staged
        self.cache: dict[str, bytes] = {}
        self.entries: dict[str, tuple[str, str]] = {}
        self.repository = self.root
        self.identifier = "working-tree"
        self._workspace_files: set[str] | None = None
        self._index_files: set[str] = set()
        self._directories: set[str] | None = None
        self.head_oid: str | None = None
        self.added_files: set[str] = set()
        if not self.root.is_dir():
            raise WikiError(f"Root does not exist: {self.root}")
        if staged:
            self.repository = Path(
                run_git(self.root, "rev-parse", "--show-toplevel").decode().strip()
            ).resolve()
            try:
                prefix = self.root.relative_to(self.repository).as_posix()
            except ValueError as exc:
                raise WikiError("Selected root is outside the Git repository") from exc
            prefix = "" if prefix == "." else prefix + "/"
            head = subprocess.run(
                ["git", "-C", str(self.repository), "rev-parse", "--verify", "-q", "HEAD"],
                capture_output=True, check=False,
            )
            if head.returncode == 0:
                self.head_oid = head.stdout.decode("ascii").strip()
            elif head.returncode != 1:
                raise WikiError("Cannot capture HEAD for the added-document comparison")
            listing = run_git(self.repository, "ls-files", "--stage", "-z")
            self.identifier = "git-index-sha256:" + digest(listing)
            for item in listing.split(b"\0"):
                if not item:
                    continue
                meta, filename = item.split(b"\t", 1)
                mode, oid, stage = meta.decode("ascii").split()
                name = filename.decode("utf-8", "surrogateescape")
                if stage != "0":
                    raise WikiError(f"Unmerged index entry: {name}; resolve conflicts first")
                if name.startswith(prefix):
                    self.entries[name[len(prefix):]] = (mode, oid)
            self._index_files = set(self.entries)
            prior_files: set[str] = set()
            if self.head_oid:
                names = run_git(self.repository, "ls-tree", "-r", "--name-only", "-z", self.head_oid)
                for raw_name in names.split(b"\0"):
                    name = raw_name.decode("utf-8", "surrogateescape")
                    if name.startswith(prefix):
                        prior_files.add(name[len(prefix):])
            self.added_files = self._index_files - prior_files

    def files(self) -> set[str]:
        if self.staged:
            return self._index_files
        if self._workspace_files is None:
            paths: set[str] = set()
            for directory, dirs, files in os.walk(self.root, followlinks=False):
                dirs[:] = sorted(d for d in dirs if d not in DEFAULT_EXCLUDES)
                for name in files:
                    paths.add((Path(directory) / name).relative_to(self.root).as_posix())
            self._workspace_files = paths
        return self._workspace_files

    def exists(self, path: str) -> bool:
        # Exact names are used even on a case-insensitive host.
        files = self.files()
        if path in files or path == ".":
            return True
        if self._directories is None:
            self._directories = {
                parent.as_posix() for name in files for parent in PurePosixPath(name).parents
            }
        return path in self._directories

    def is_file(self, path: str) -> bool:
        if self.staged:
            return path in self.entries and self.entries[path][0] in {"100644", "100755"}
        return path in self.files() and (self.root / path).is_file()

    def read(self, path: str) -> bytes:
        path = relative_path(path)
        if path in self.cache:
            return self.cache[path]
        if self.staged:
            if path not in self.entries:
                raise WikiError(f"Not present in the Git index: {path}")
            mode, oid = self.entries[path]
            if mode not in {"100644", "100755"}:
                raise WikiError(f"Unsupported index file mode {mode}: {path}")
            data = run_git(self.repository, "cat-file", "blob", oid)
        else:
            target = self.root / path
            try:
                target.resolve().relative_to(self.root)
            except ValueError as exc:
                raise WikiError(f"File resolves outside the selected root: {path}") from exc
            try:
                data = target.read_bytes()
            except OSError as exc:
                raise WikiError(f"Cannot read {path}: {exc.strerror}") from exc
        self.cache[path] = data
        return data

    def text(self, path: str) -> str:
        try:
            return self.read(path).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise WikiError(f"File is not UTF-8: {path}") from exc


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    path: str
    message: str
    line: int | None = None


@dataclass(frozen=True)
class Link:
    target: str
    line: int
    kind: str = "markdown"


class Wiki:
    def __init__(self, snapshot: Snapshot, config_path: str = DEFAULT_CONFIG):
        self.snapshot = snapshot
        self.config_path = relative_path(config_path)
        raw = snapshot.read(self.config_path)
        self.config_hash = digest(raw)
        try:
            self.config = json.loads(raw)
        except (ValueError, UnicodeDecodeError) as exc:
            raise WikiError(f"Invalid JSON in {config_path}: {exc}") from exc
        if not isinstance(self.config, dict) or type(self.config.get("version")) is not int or self.config["version"] != 1:
            raise WikiError("Configuration must be an object with version: 1")
        self.roots = self._records("roots", required=True)
        self.modules = self._records("modules")
        self.pages = self._records("pages")
        self.entrypoints = self._paths("entrypoints", required=True)
        self.excludes = self.config.get("exclude", [])
        if not isinstance(self.excludes, list) or not all(isinstance(x, str) for x in self.excludes):
            raise WikiError("exclude must be an array of path patterns")
        seen_roots: set[str] = set()
        for root in self.roots:
            root["path"] = relative_path(root.get("path"))
            if root.get("role") not in ROOT_ROLES:
                raise WikiError(f"Invalid root role for {root['path']}")
            if root["path"] in seen_roots:
                raise WikiError(f"Root registered twice: {root['path']}")
            seen_roots.add(root["path"])
        seen_modules: set[str] = set()
        for module in self.modules:
            if not isinstance(module.get("name"), str) or not module["name"]:
                raise WikiError("Each module needs a non-empty name")
            if module["name"] in seen_modules:
                raise WikiError(f"Module registered twice: {module['name']}")
            seen_modules.add(module["name"])
            for field in ("path", "entry"):
                module[field] = relative_path(module.get(field))
            if "docs" in module:
                module["docs"] = relative_path(module["docs"])
        seen_pages: set[str] = set()
        for page in self.pages:
            page["path"] = relative_path(page.get("path"))
            if page["path"] in seen_pages:
                raise WikiError(f"Page registered twice: {page['path']}")
            seen_pages.add(page["path"])
            if page.get("role", "knowledge") not in PAGE_ROLES:
                raise WikiError(f"Unknown page role for {page['path']}")
            if "max_chars" in page and (type(page["max_chars"]) is not int or page["max_chars"] < 1):
                raise WikiError(f"max_chars must be a positive integer: {page['path']}")
            for key in ("id", "scope"):
                if key in page and (not isinstance(page[key], str) or not page[key]):
                    raise WikiError(f"{key} must be a non-empty string: {page['path']}")
        self.generated_index = self.config.get("generated_index")
        if self.generated_index is not None:
            self.generated_index = relative_path(self.generated_index)
            if not self.generated_index.endswith(".json"):
                raise WikiError("generated_index must be a JSON path, never a Markdown navigation page")
        self.page_map = {p["path"]: p for p in self.pages}
        for page in self.pages:
            if page.get("role") == "archive" and self.root_role(page["path"]) != "archive":
                raise WikiError(f"Page role archive requires a registered archive root: {page['path']}")
        self.primary_archive = self.config.get("archive_root")
        if self.primary_archive is not None:
            self.primary_archive = relative_path(self.primary_archive)
            if not any(r["path"] == self.primary_archive and r["role"] == "archive" for r in self.roots):
                raise WikiError("archive_root must identify a registered archive root")
        self.remind = self._remind_config(self.config.get("remind"))

    @staticmethod
    def _patterns(value: object, name: str, required: bool = False) -> list[str]:
        if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value) or (required and not value):
            raise WikiError(f"{name} must be {'a non-empty' if required else 'an'} array of path patterns")
        return value

    def _remind_config(self, raw: object) -> dict | None:
        if raw is None:
            return None
        if not isinstance(raw, dict):
            raise WikiError("remind must be an object")
        watches = raw.get("watch")
        if not isinstance(watches, list) or not watches or not all(isinstance(w, dict) for w in watches):
            raise WikiError("remind.watch must be a non-empty array of objects")
        names: set[str] = set()
        for watch in watches:
            name = watch.get("name")
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9._-]+", name):
                raise WikiError("Each remind.watch entry needs a name made of letters, digits, '.', '_' or '-'")
            if name in names:
                raise WikiError(f"remind.watch name registered twice: {name}")
            names.add(name)
            watch["code"] = self._patterns(watch.get("code"), f"remind.watch[{name}].code", required=True)
            watch["docs"] = self._patterns(watch.get("docs"), f"remind.watch[{name}].docs", required=True)

        def limits(value: object, name: str, required: bool) -> dict:
            if value is None and not required:
                return {}
            if not isinstance(value, dict) or not value or set(value) - {"commits", "lines"}:
                raise WikiError(f"{name} must be an object with commits and/or lines")
            for key, number in value.items():
                if type(number) is not int or number < 1:
                    raise WikiError(f"{name}.{key} must be a positive integer")
            return value

        return {
            "watch": watches,
            "threshold": limits(raw.get("threshold"), "remind.threshold", True),
            "block_at": limits(raw.get("block_at"), "remind.block_at", False),
            "ask_user": self._patterns(raw.get("ask_user", []), "remind.ask_user"),
            "decisions": self._patterns(raw.get("decisions", DEFAULT_DECISION_PATTERNS), "remind.decisions"),
        }

    def _records(self, name: str, required: bool = False) -> list[dict]:
        records = self.config.get(name, [])
        if not isinstance(records, list) or not all(isinstance(x, dict) for x in records):
            raise WikiError(f"{name} must be an array of objects")
        if required and not records:
            raise WikiError(f"{name} must not be empty")
        return records

    def _paths(self, name: str, required: bool = False) -> list[str]:
        paths = self.config.get(name, [])
        if not isinstance(paths, list) or (required and not paths):
            raise WikiError(f"{name} must be a non-empty array of paths")
        return [relative_path(p) for p in paths]

    def excluded(self, path: str) -> bool:
        if any(part in DEFAULT_EXCLUDES for part in PurePosixPath(path).parts):
            return True
        return any(
            fnmatch.fnmatchcase(path, pattern)
            or fnmatch.fnmatchcase(path + "/", pattern)
            or (pattern.endswith("/**") and path == pattern[:-3])
            for pattern in self.excludes
        )

    def root_role(self, path: str) -> str | None:
        matching = [r for r in self.roots if under(path, r["path"])]
        if matching:
            return max(matching, key=lambda r: len(r["path"]))["role"]
        return None

    def role(self, path: str) -> str:
        root_role = self.root_role(path)
        if root_role == "archive":
            return "archive"
        return self.page_map.get(path, {}).get("role", root_role or "knowledge")

    def scope(self, path: str) -> str:
        if "scope" in self.page_map.get(path, {}):
            return self.page_map[path]["scope"]
        matching = [m for m in self.modules if under(path, m["path"])]
        return max(matching, key=lambda m: len(m["path"]))["name"] if matching else "project"

    def registered(self, path: str) -> bool:
        return (
            path in self.entrypoints
            or path in self.page_map
            or self.root_role(path) is not None
            or any(path == m["entry"] or (m.get("docs") and under(path, m["docs"])) for m in self.modules)
        )

    def documents(self) -> list[str]:
        return sorted(
            p for p in self.snapshot.files()
            if p.lower().endswith((".md", ".markdown")) and not self.excluded(p) and self.registered(p)
        )

    def archive_root(self) -> str:
        roots = [r["path"] for r in self.roots if r["role"] == "archive"]
        if self.primary_archive:
            return self.primary_archive
        if "archive" in roots:
            return "archive"
        if len(roots) != 1:
            raise WikiError("Set archive_root to select a primary archive destination")
        return roots[0]

    def legacy_archives(self) -> list[str]:
        primary = self.archive_root()
        return [r["path"] for r in self.roots if r["role"] == "archive" and r["path"] != primary]


def without_code(text: str, inline: bool = True) -> str:
    output: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match and fence is None:
            fence = match.group(1)
            output.append("\n" if line.endswith("\n") else "")
        elif fence is not None:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            output.append("\n" if line.endswith("\n") else "")
        else:
            output.append(re.sub(r"(`+)(.+?)\1", lambda m: " " * len(m.group()), line) if inline else line)
    return "".join(output)


def target_part(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<"):
        end = raw.find(">")
        return raw[1:end] if end >= 0 else raw
    match = re.match(r"((?:\\.|[^\s])+)", raw)
    return re.sub(r"\\([()\[\] ])", r"\1", match.group(1)) if match else ""


def markdown_links(text: str, path: str) -> list[Link]:
    clean = without_code(text)
    definitions: dict[str, str] = {}
    lines = clean.splitlines(keepends=True)
    def_key = lambda value: " ".join(value.lower().split())
    for number, line in enumerate(lines):
        match = re.match(r"^ {0,3}\[([^\]]+)\]:\s*(.+)", line)
        if match:
            definitions[def_key(match.group(1))] = target_part(match.group(2))
            lines[number] = "\n" if line.endswith("\n") else ""
    clean = "".join(lines)
    found: list[Link] = []
    i = 0
    while i < len(clean):
        start = clean.find("[", i)
        if start < 0:
            break
        if start and clean[start - 1] == "\\":
            i = start + 1
            continue
        end, depth = start + 1, 1
        while end < len(clean) and depth:
            if clean[end] == "\\":
                end += 2
                continue
            depth += (clean[end] == "[") - (clean[end] == "]")
            end += 1
        if depth:
            break
        label = clean[start + 1:end - 1]
        line = clean.count("\n", 0, start) + 1
        if end < len(clean) and clean[end] == "(":
            cursor, depth = end + 1, 1
            while cursor < len(clean) and depth:
                if clean[cursor] == "\\":
                    cursor += 2
                    continue
                depth += (clean[cursor] == "(") - (clean[cursor] == ")")
                cursor += 1
            if not depth:
                found.append(Link(target_part(clean[end + 1:cursor - 1]), line))
                i = cursor
                continue
        elif end < len(clean) and clean[end] == "[":
            ref_end = clean.find("]", end + 1)
            if ref_end >= 0:
                key = def_key(clean[end + 1:ref_end] or label)
                found.append(Link(definitions.get(key, key), line, "markdown" if key in definitions else "missing-reference"))
                i = ref_end + 1
                continue
        elif def_key(label) in definitions:
            found.append(Link(definitions[def_key(label)], line))
        i = end
    if PurePosixPath(path).name in {"AGENTS.md", "CLAUDE.md"}:
        for number, line in enumerate(clean.splitlines(), 1):
            match = re.fullmatch(r"\s*@([^\s]+)\s*", line)
            if match:
                found.append(Link(match.group(1), number, "import"))
    return found


def heading_slug(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value).replace("`", "").lower().strip()
    value = "".join(c for c in value if c in "_-" or c.isspace() or unicodedata.category(c)[0] in "LN")
    return re.sub(r"\s", "-", value)


def anchors(text: str) -> set[str]:
    clean = without_code(text, inline=False)
    result = set(re.findall(r"<(?:a|[a-z][\w-]*)\b[^>]*\b(?:id|name)=[\"']([^\"']+)[\"']", clean, re.I))
    counts: dict[str, int] = {}
    heading_ids: set[str] = set()
    for line in clean.splitlines():
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            slug = heading_slug(match.group(1))
            count = counts.get(slug, 0)
            candidate = slug if count == 0 else f"{slug}-{count}"
            while candidate in heading_ids:
                count += 1
                candidate = f"{slug}-{count}"
            counts[slug] = count + 1
            heading_ids.add(candidate)
            result.add(candidate)
    return result


def resolve_link(source: str, target: str) -> tuple[str | None, str, str | None]:
    """Return local path, fragment, or an unsupported-path reason."""
    parsed = urlsplit(target)
    if parsed.netloc or (parsed.scheme and parsed.scheme != "file"):
        return None, "", None
    if parsed.scheme == "file" or target.startswith("/") or "\\" in target:
        return None, "", "Machine-absolute or root-absolute link; use a portable relative path"
    path = unquote(parsed.path)
    path = re.sub(r":\d+(?::\d+)?$", "", path)
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), path)) if path else source
    if resolved == ".." or resolved.startswith("../"):
        return None, "", "Link leaves the selected project root"
    return resolved, unquote(parsed.fragment), None


def check(wiki: Wiki) -> list[Finding]:
    findings: list[Finding] = []
    snap = wiki.snapshot
    required = set(wiki.entrypoints) | set(wiki.page_map)
    for module in wiki.modules:
        required.add(module["entry"])
        if "docs" in module:
            required.add(module["docs"])
    for root in wiki.roots:
        if root["role"] != "archive":
            required.add(root["path"])
    for path in sorted(required):
        if wiki.excluded(path):
            findings.append(Finding("required-excluded", "error", path, "Required path is excluded by configuration"))
        elif not snap.exists(path):
            findings.append(Finding("missing-entry", "error", path, "Required path is missing from this snapshot"))
    discovered = set()
    for path in snap.files():
        if wiki.excluded(path) or not path.lower().endswith((".md", ".markdown")):
            continue
        parts = PurePosixPath(path).parts
        for index, part in enumerate(parts[:-1]):
            if part == "docs":
                directory = "/".join(parts[:index + 1])
                if not wiki.registered(path):
                    discovered.add(directory)
    for path in sorted(discovered):
        findings.append(Finding("unregistered-docs", "error", path, "Documentation root is not registered or explicitly excluded"))
    if snap.staged:
        added_documents = sorted(set(wiki.documents()) & snap.added_files)
        added_current = [p for p in added_documents if wiki.role(p) != "archive"]
        if added_current:
            for path in added_current:
                historical = f"{wiki.archive_root()}/{path}"
                if snap.is_file(historical):
                    findings.append(Finding("historical-path-match", "warning", path, f"New in the captured index relative to captured HEAD; history exists at {historical}. Distinguish restoration, continuation, and a new topic."))
            if wiki.legacy_archives():
                findings.append(Finding("legacy-history-unmatched", "warning", wiki.config_path, "Added-path matching covers the primary archive only; legacy roots are classified and checked but their old layouts are not inferred: " + ", ".join(wiki.legacy_archives())))
    current_ids: dict[tuple[str, str], str] = {}
    for page in wiki.pages:
        path = page["path"]
        if page.get("id") and wiki.role(path) != "archive":
            key = (wiki.scope(path), page["id"])
            if key in current_ids:
                findings.append(Finding("duplicate-current-id", "error", path, f"Current ID also belongs to {current_ids[key]} in scope {key[0]}"))
            current_ids[key] = path
    anchor_cache: dict[str, set[str]] = {}
    for path in wiki.documents():
        severity = "warning" if wiki.role(path) == "archive" else "error"
        try:
            text = snap.text(path)
        except WikiError as exc:
            findings.append(Finding("unreadable", severity, path, str(exc)))
            continue
        budget = wiki.page_map.get(path, {}).get("max_chars")
        if budget and len(text) > budget:
            findings.append(Finding("page-budget", severity, path, f"{len(text)} characters exceeds max_chars={budget}"))
        for link in markdown_links(text, path):
            if link.kind == "missing-reference":
                findings.append(Finding("missing-reference", severity, path, f"Undefined reference link: {link.target}", link.line))
                continue
            if link.kind == "import" and (urlsplit(link.target).scheme or urlsplit(link.target).netloc):
                findings.append(Finding("unsupported-import", severity, path, f"Only a local standalone @path import is supported: {link.target}", link.line))
                continue
            target, fragment, problem = resolve_link(path, link.target)
            if problem:
                # Imports form a required loading edge; unsupported imports fail closed.
                level = severity if link.kind == "import" or problem == "Link leaves the selected project root" else "warning"
                findings.append(Finding("unsupported-link", level, path, f"{problem}: {link.target}", link.line))
                continue
            if target is None:
                continue
            if not snap.exists(target):
                findings.append(Finding("broken-link", severity, path, f"Target does not exist with exact case: {link.target}", link.line))
            elif fragment and target.lower().endswith((".md", ".markdown")):
                try:
                    if target not in anchor_cache:
                        anchor_cache[target] = anchors(snap.text(target))
                    if fragment not in anchor_cache[target]:
                        findings.append(Finding("broken-anchor", severity, path, f"ATX/explicit anchor does not exist: {link.target}", link.line))
                except WikiError as exc:
                    findings.append(Finding("unreadable-target", severity, path, str(exc), link.line))
    return findings


def report(wiki: Wiki, findings: list[Finding], command: str, **extra: object) -> dict:
    errors = sum(f.severity == "error" for f in findings)
    warnings = sum(f.severity == "warning" for f in findings)
    return {
        "command": command,
        "result": "failed" if errors else "passed_with_warnings" if warnings else "passed",
        "tool_version": VERSION,
        "snapshot": wiki.snapshot.identifier,
        "head_baseline": (wiki.snapshot.head_oid or "unborn") if wiki.snapshot.staged else None,
        "config": wiki.config_path,
        "config_sha256": wiki.config_hash,
        "coverage": {
            "roots": wiki.roots,
            "modules": [m["name"] for m in wiki.modules],
            "excluded": wiki.excludes,
            "not_checked": ["prose correctness", "arbitrary Markdown/host syntax", "runtime contract behavior", "external URLs"],
        },
        "errors": errors,
        "warnings": warnings,
        "findings": [asdict(f) for f in findings],
        **extra,
    }


def output_report(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(f"{result['command']}: {result['result']} ({result.get('errors', 0)} errors, {result.get('warnings', 0)} warnings)")
    print(f"Snapshot: {result['snapshot']}")
    for item in result.get("findings", []):
        location = item["path"] + (f":{item['line']}" if item.get("line") else "")
        print(f"{item['severity'].upper()} {item['rule']} {location}: {item['message']}")
    for key in ("source", "destination", "source_sha256", "history_match", "hooks", "git_hooks", "archive_ignore"):
        if key in result:
            print(f"{key}: {result[key]}")
    for item in result.get("watch_status", []):
        print(f"WATCH {item['name']}: {item['commits']} commits, {item['lines']} lines since {item['since'] or 'start of scanned history'}")
    for change in result.get("affected_links", []):
        print(f"LINK {change['path']}:{change['line']}: {change['target']} -> {change['suggested_target']} ({change['note']})")


def index_data(wiki: Wiki) -> dict:
    pages = []
    for path in wiki.documents():
        text = wiki.snapshot.text(path)
        title = re.search(r"^#\s+(.+)$", without_code(text, inline=False), re.M)
        page = {"path": path, "title": title.group(1).strip() if title else PurePosixPath(path).stem, "role": wiki.role(path), "scope": wiki.scope(path)}
        if wiki.page_map.get(path, {}).get("id"):
            page["id"] = wiki.page_map[path]["id"]
        pages.append(page)
    return {"version": 1, "project_name": wiki.config.get("project_name", ""), "pages": pages}


def new_path_report(wiki: Wiki, path: str) -> dict:
    path = relative_path(path)
    findings: list[Finding] = []
    if wiki.snapshot.exists(path):
        findings.append(Finding("current-path-occupied", "error", path, "Current path already exists; inspect it before creating another document"))
    archived = f"{wiki.archive_root()}/{path}"
    matched = wiki.snapshot.is_file(archived)
    if matched:
        findings.append(Finding("historical-path-match", "warning", path, f"History exists at {archived}; distinguish restoration, continuation, and a new topic. This does not reserve the filename forever."))
    if wiki.legacy_archives():
        findings.append(Finding("legacy-history-unmatched", "warning", path, "Exact history matching covers the primary archive only; inspect legacy roots separately: " + ", ".join(wiki.legacy_archives())))
    return report(wiki, findings, "check-new", source=path, history_match=archived if matched else None,
                  history_match_scope={"primary_root": wiki.archive_root(), "legacy_roots_not_matched": wiki.legacy_archives()})


def archive_report(wiki: Wiki, path: str) -> dict:
    path = relative_path(path)
    if not path.lower().endswith((".md", ".markdown")):
        raise WikiError("Archive preview currently supports a complete Markdown document only")
    if wiki.root_role(path) == "archive":
        raise WikiError("Source is already under an archive root")
    if path not in wiki.documents():
        raise WikiError("Source must be a registered, readable Markdown document")
    destination = f"{wiki.archive_root()}/{path}"
    findings: list[Finding] = []
    if wiki.snapshot.exists(destination):
        findings.append(Finding("archive-collision", "error", destination, "Archive target already exists; preview is incomplete and no overwrite is allowed, even if content matches"))
    affected = []
    for source in wiki.documents():
        text = wiki.snapshot.text(source)
        for link in markdown_links(text, source):
            target, fragment, problem = resolve_link(source, link.target)
            if source == path and (problem or link.kind == "missing-reference"):
                findings.append(Finding("archive-unresolved-link", "warning", source, f"Cannot propose a portable move for {link.target}: {problem or 'undefined reference'}", link.line))
            if problem or target is None or link.kind == "missing-reference":
                continue
            if source != path and target != path:
                continue
            if source == path and not wiki.snapshot.exists(target):
                findings.append(Finding("archive-unresolved-target", "warning", source, f"Existing target cannot be located: {link.target}", link.line))
                continue
            new_source = destination if source == path else source
            new_target = destination if target == path else target
            suggested = posixpath.relpath(new_target, posixpath.dirname(new_source) or ".")
            if fragment:
                suggested += "#" + fragment
            affected.append({"path": source, "line": link.line, "target": link.target, "suggested_target": suggested,
                             "note": "mechanical candidate only; classify navigation versus fixed historical evidence before applying"})
    return report(wiki, findings, "archive-preview", source=path, destination=destination,
                  source_sha256=digest(wiki.snapshot.read(path)), affected_links=affected,
                  writes=False, limitations=["whole-document preview only", "does not decide whether a topic is retired", "does not create redirects or rewrite any links", "no apply command"])


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def git_text(root: Path, *args: str) -> str:
    return run_git(root, "-c", "core.quotePath=false", *args).decode("utf-8", "surrogateescape")


def has_head(root: Path) -> bool:
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "-q", "HEAD"], capture_output=True, check=False)
    if result.returncode not in {0, 1}:
        raise WikiError("Git repository unavailable: " + result.stderr.decode("utf-8", "replace").strip())
    return result.returncode == 0


def parse_numstat(lines: list[str]) -> list[tuple[str, int]]:
    changes = []
    for line in lines:
        parts = line.split("\t", 2)
        if len(parts) == 3:
            added, deleted, path = parts
            size = (int(added) if added.isdigit() else 0) + (int(deleted) if deleted.isdigit() else 0)
            changes.append((path, size))
    return changes


def review_marks(values: list[str]) -> tuple[set[str], list[str]]:
    """Return watch names reviewed with a reason, and trailer values missing a reason."""
    reviewed: set[str] = set()
    incomplete: list[str] = []
    for value in values:
        names, _, reason = value.strip().partition(" ")
        if not names:
            continue
        if not reason.strip():
            incomplete.append(value.strip())
            continue
        reviewed.update(n for n in names.split(",") if n)
    return reviewed, incomplete


def message_trailers(root: Path, message_file: str) -> list[str]:
    try:
        text = Path(message_file).read_text(encoding="utf-8")
    except OSError as exc:
        raise WikiError(f"Cannot read commit message file: {exc.strerror}") from exc
    text = "".join(line for line in text.splitlines(keepends=True) if not line.startswith("#"))
    result = subprocess.run(["git", "-C", str(root), "interpret-trailers", "--parse"], input=text.encode("utf-8"),
                            capture_output=True, check=False)
    if result.returncode:
        raise WikiError("Cannot parse commit message trailers: " + result.stderr.decode("utf-8", "replace").strip())
    prefix = REVIEW_TRAILER.lower() + ":"
    return [line.split(":", 1)[1] for line in result.stdout.decode("utf-8", "replace").splitlines()
            if line.lower().startswith(prefix)]


def history_debt(wiki: Wiki) -> tuple[dict[str, dict], bool]:
    """Count code changes per watch since its docs last changed or were marked reviewed."""
    root = wiki.snapshot.root
    watches = wiki.remind["watch"]
    status = {w["name"]: {"commits": 0, "lines": 0, "since": None} for w in watches}
    if not has_head(root):
        return status, False
    output = git_text(root, "log", f"-n{HISTORY_SCAN_LIMIT}", "--relative", "--no-renames", "--numstat",
                      f"--format=%x1e%H%x1f%(trailers:key={REVIEW_TRAILER},valueonly,separator=%x1d)")
    open_names = set(status)
    scanned = 0
    for record in output.split("\x1e")[1:]:
        scanned += 1
        header, _, body = record.partition("\n")
        commit, _, trailer_text = header.partition("\x1f")
        reviewed, _ = review_marks(trailer_text.split("\x1d"))
        changes = parse_numstat(body.splitlines())
        for watch in watches:
            name = watch["name"]
            if name not in open_names:
                continue
            if name in reviewed or any(matches(path, watch["docs"]) for path, _ in changes):
                status[name]["since"] = commit[:12]
                open_names.discard(name)
                continue
            code = [size for path, size in changes if matches(path, watch["code"])]
            if code:
                status[name]["commits"] += 1
                status[name]["lines"] += sum(code)
        if not open_names:
            break
    return status, bool(open_names) and scanned >= HISTORY_SCAN_LIMIT


def over(value: dict, limit: dict) -> bool:
    return bool(limit) and any(value[key] >= number for key, number in limit.items())


def remind_report(wiki: Wiki, message_file: str | None = None) -> dict:
    if wiki.remind is None:
        raise WikiError("remind requires a remind section in configuration")
    snap = wiki.snapshot
    config = wiki.remind
    findings: list[Finding] = []
    status, truncated = history_debt(wiki)
    staged_changes: list[tuple[str, int]] = []
    reviewed: set[str] = set()
    if snap.staged:
        staged_changes = parse_numstat(git_text(snap.root, "diff", "--cached", "--relative", "--no-renames", "--numstat").splitlines())
        if message_file:
            reviewed, incomplete = review_marks(message_trailers(snap.root, message_file))
            for value in incomplete:
                findings.append(Finding("review-trailer-incomplete", "warning", message_file,
                                        f"[agent] '{REVIEW_TRAILER}: {value}' has no reason and does not reset the count. Write '{REVIEW_TRAILER}: <name> <reason>'."))
    staged_paths = [path for path, _ in staged_changes]
    for watch in config["watch"]:
        name = watch["name"]
        item = status[name]
        code = [size for path, size in staged_changes if matches(path, watch["code"])]
        docs_touched = any(matches(path, watch["docs"]) for path in staged_paths)
        if snap.staged and code and not docs_touched and name not in reviewed:
            findings.append(Finding("docs-not-updated", "warning", name,
                                    f"[agent] Code under {', '.join(watch['code'])} changed but {', '.join(watch['docs'])} did not. "
                                    f"If behavior, interfaces or rules changed, update those documents in this commit. "
                                    f"Otherwise add the trailer '{REVIEW_TRAILER}: {name} <reason>'."))
        if snap.staged and (docs_touched or name in reviewed):
            item.update(commits=0, lines=0, since="this commit")
        elif snap.staged and code:
            item["commits"] += 1
            item["lines"] += sum(code)
        due = over(item, config["threshold"])
        overdue = over(item, config["block_at"])
        counted = f"{item['commits']} commits and {item['lines']} changed lines since {item['since'] or 'the start of scanned history'}"
        if overdue:
            blocking = snap.staged and bool(code)
            findings.append(Finding("docs-review-overdue", "error" if blocking else "warning", name,
                                    f"[agent] {counted} reached block_at {config['block_at']}. Read the documents for {name}, "
                                    f"update them or add '{REVIEW_TRAILER}: {name} <reason>' to this commit message."))
        elif due:
            findings.append(Finding("docs-review-due", "warning", name,
                                    f"[agent] {counted} reached the reminder threshold {config['threshold']}. "
                                    f"Check that the documents for {name} still match the code."))
    if snap.staged:
        current = [p for p in wiki.documents() if wiki.role(p) != "archive"]
        for path in staged_paths:
            if matches(path, config["ask_user"]):
                findings.append(Finding("ask-user", "warning", path,
                                        "[user] This file states requirements, principles or decisions. Unless the user asked for this change, "
                                        "confirm it with the user before committing; otherwise report it in your summary."))
            if matches(path, config["decisions"]):
                linking = []
                for source in current:
                    if source == path or source in staged_paths:
                        continue
                    for link in markdown_links(snap.text(source), source):
                        target, _, problem = resolve_link(source, link.target)
                        if not problem and target == path:
                            linking.append(source)
                            break
                listed = ", ".join(linking[:10]) + (" ..." if len(linking) > 10 else "")
                findings.append(Finding("decision-sync", "warning", path,
                                        "[agent] A decision record changed. Update current documents that still state the old conclusion in this commit. "
                                        + (f"Linking documents not staged: {listed}. " if linking else "No unstaged current document links to it. ")
                                        + "Also search the decision's key terms; restatements without links are not listed."))
    return report(wiki, findings, "remind", watch_status=[{"name": n, **v} for n, v in status.items()],
                  history_scan_limit_reached=truncated,
                  limitations=["counts come from Git history and the captured index only", "does not judge whether document content matches code",
                               "trailers in the pending message are read only when --message-file is given"])


def hook_status(wiki: Wiki) -> dict[str, str] | str:
    root = wiki.snapshot.root
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-path", "hooks"], capture_output=True, check=False)
    if result.returncode:
        return "unknown: not a Git repository"
    directory = (root / result.stdout.decode().strip()).resolve()
    states: dict[str, str] = {}
    for name, marker in HOOK_MARKERS.items():
        hook = directory / name
        if not hook.is_file():
            states[name] = "missing"
        elif not os.access(hook, os.X_OK):
            states[name] = "not executable"
        elif "wiki.py" not in (text := hook.read_text(encoding="utf-8", errors="replace")) or marker not in text:
            states[name] = "present but does not call wiki.py " + marker
        else:
            states[name] = "installed"
    return states


def doctor_report(wiki: Wiki) -> dict:
    findings = [Finding("hook-coverage", "warning", wiki.config_path,
                        "Other hook managers and build tasks are unknown: only the active Git hooks directory is inspected for ProjectWiki hooks")]
    roots = [r["path"] for r in wiki.roots if r["role"] == "archive"]
    ignore = wiki.snapshot.text(".ignore").splitlines() if ".ignore" in wiki.snapshot.files() else []
    missing = [root for root in roots if f"/{root}/" not in [line.strip() for line in ignore]]
    if missing:
        findings.append(Finding("archive-default-search", "warning", ".ignore", f"No exact root exclusion for: {', '.join(missing)}. Ordinary rg may include historical text."))
    hooks = hook_status(wiki)
    if isinstance(hooks, dict):
        for name, state in hooks.items():
            if state != "installed":
                findings.append(Finding("hook-not-installed", "warning", name, f"Git {name} hook: {state}. See scripts/wiki/README.md for installation."))
        if wiki.remind is None:
            findings.append(Finding("remind-not-configured", "warning", wiki.config_path, "No remind section; commit-time documentation reminders are disabled"))
    return report(wiki, findings, "doctor", hooks="unknown: other hook managers and build tasks are not inspected",
                  git_hooks=hooks,
                  archive_ignore="exact configured rules found" if not missing else "incomplete",
                  limits=["ignore rules affect compatible default searches, not access permissions", "git grep, arbitrary grep and explicit reads are not covered",
                          "a hook file being installed does not prove it runs; --no-verify and other Git clients can skip it"])


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--version", action="version", version=VERSION)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("check", "check-new", "archive", "index", "doctor", "remind"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, default=Path.cwd())
        command.add_argument("--config", default=DEFAULT_CONFIG)
        command.add_argument("--json", action="store_true", help="Print structured report (index always emits JSON)")
        if name in {"check", "remind"}:
            command.add_argument("--staged", action="store_true", help="Read all inputs from captured Git index blobs")
        if name == "remind":
            command.add_argument("--message-file", help="Pending commit message, as passed to a commit-msg hook")
        if name in {"check-new", "archive"}:
            command.add_argument("path")
        if name == "index":
            command.add_argument("--check", action="store_true", help="Compare stdout index with configured generated_index")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        wiki = Wiki(Snapshot(args.root, getattr(args, "staged", False)), args.config)
        if args.command == "check":
            result = report(wiki, check(wiki), "check", documents_checked=len(wiki.documents()))
        elif args.command == "check-new":
            result = new_path_report(wiki, args.path)
        elif args.command == "archive":
            result = archive_report(wiki, args.path)
        elif args.command == "doctor":
            result = doctor_report(wiki)
        elif args.command == "remind":
            if args.message_file and not args.staged:
                raise WikiError("--message-file requires --staged")
            result = remind_report(wiki, args.message_file)
        else:
            encoded = json.dumps(index_data(wiki), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            if args.check:
                if not wiki.generated_index:
                    raise WikiError("index --check requires generated_index in configuration")
                if not wiki.snapshot.exists(wiki.generated_index) or wiki.snapshot.text(wiki.generated_index) != encoded:
                    result = report(wiki, [Finding("index-outdated", "error", wiki.generated_index, "Generated index differs; review index stdout before writing it")], "index-check")
                    output_report(result, args.json)
                    return 1
            else:
                print(encoded, end="")
            return 0
        output_report(result, args.json)
        return 1 if result["errors"] else 0
    except (WikiError, OSError, ValueError) as exc:
        result = {"command": args.command, "result": "incomplete", "tool_version": VERSION,
                  "snapshot": "git-index" if getattr(args, "staged", False) else "working-tree", "errors": 1, "warnings": 0,
                  "findings": [asdict(Finding("input-unavailable", "error", args.config, str(exc)))]}
        output_report(result, args.json)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
