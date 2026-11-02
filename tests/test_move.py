from __future__ import annotations

from test_wiki import ProjectFixture, wiki, SCRIPT


class MoveTests(ProjectFixture):
    # A misplaced current document and a document elsewhere that links to it.
    PAGE = "# Engine decision\n\n状态：当前有效。\n\n见 [需求](../../docs/engine-req.md#engine-req)。\n"
    LINKER = "# Engine req\n\n现行决策在 [这里](../dev/decisions/engine.md#engine-decision)。\n"

    def place_pair(self):
        self.config["roots"] = [
            {"path": "docs", "role": "knowledge"},
            {"path": "dev", "role": "process"},
            {"path": "archive", "role": "archive"},
        ]
        self.save_config()
        self.write("dev/decisions/engine.md", self.PAGE)
        self.write("docs/engine-req.md", self.LINKER)
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Req](engine-req.md)\n"
                                    "[Decision](../dev/decisions/engine.md)\n")

    def preview(self, source, destination):
        code, report = self.run_cli("move", source, destination)
        return code, report, report.get("plan_sha256")

    def test_preview_lists_moves_links_and_hashes_without_writing(self):
        """PW-45.1 PW-45.2"""
        self.place_pair()
        tree_before = {p.name for p in (self.root / "dev/decisions").iterdir()}
        code, report, plan = self.preview("dev/decisions/engine.md", "docs/decisions/engine.md")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["command"], "move-preview")
        self.assertEqual(report["destination"], "docs/decisions/engine.md")
        self.assertIn(plan, (report["plan_sha256"],))
        self.assertTrue(report["source_sha256"])
        self.assertEqual({x["direction"] for x in report["affected_links"]}, {"incoming", "outgoing"})
        # Preview writes nothing.
        self.assertTrue((self.root / "dev/decisions/engine.md").is_file())
        self.assertFalse((self.root / "docs/decisions/engine.md").exists())
        self.assertEqual({p.name for p in (self.root / "dev/decisions").iterdir()}, tree_before)

    def test_apply_moves_file_and_rewrites_incoming_and_outgoing_links(self):
        """PW-45.1 PW-45.2"""
        self.place_pair()
        code, preview, plan = self.preview("dev/decisions/engine.md", "docs/decisions/engine.md")
        self.assertEqual(code, 0, preview)
        code, report = self.run_cli("move", "dev/decisions/engine.md", "docs/decisions/engine.md",
                                    "--apply", "--expect", plan)
        self.assertEqual(code, 0, report)
        self.assertFalse((self.root / "dev/decisions/engine.md").exists())
        moved = (self.root / "docs/decisions/engine.md").read_text()
        # Outgoing link from the moved file now points at the new relative location.
        self.assertIn("../engine-req.md#engine-req", moved)
        # Incoming link in the linker file now points at the new location.
        self.assertIn("decisions/engine.md#engine-decision", (self.root / "docs/engine-req.md").read_text())
        self.assertEqual(report["after_check"], "passed")

    def test_directory_moves_as_a_whole_and_keeps_internal_links(self):
        """PW-45.1"""
        self.place_pair()
        self.write("dev/modules/engine/README.md",
                   "# Engine module\n\n状态：当前有效。\n\n子页 [细节](detail.md#detail)。\n")
        self.write("dev/modules/engine/detail.md", "# Detail\n\n回到 [模块](README.md#engine-module)。\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Req](engine-req.md)\n"
                                    "[Decision](../dev/decisions/engine.md)\n[Module](../dev/modules/engine/README.md)\n")
        code, preview, plan = self.preview("dev/modules/engine", "docs/modules/engine")
        self.assertEqual(code, 0, preview)
        self.assertEqual({"dev/modules/engine/README.md", "dev/modules/engine/detail.md"},
                         set(preview["documents_moved"]))
        code, report = self.run_cli("move", "dev/modules/engine", "docs/modules/engine",
                                    "--apply", "--expect", plan)
        self.assertEqual(code, 0, report)
        self.assertFalse((self.root / "dev/modules/engine").exists())
        # Internal relative link inside the directory is unchanged.
        self.assertIn("[细节](detail.md#detail)", (self.root / "docs/modules/engine/README.md").read_text())

    def test_hash_mismatch_refuses_without_writing(self):
        """PW-45.3"""
        self.place_pair()
        code, report = self.run_cli("move", "dev/decisions/engine.md", "docs/decisions/engine.md",
                                    "--apply", "--expect", "0" * 64)
        self.assertEqual(code, 1, report)
        self.assertIn("archive-plan-changed", self.rules(report))
        self.assertTrue((self.root / "dev/decisions/engine.md").is_file())
        self.assertFalse((self.root / "docs/decisions/engine.md").exists())

    def test_existing_destination_is_a_collision(self):
        """PW-45.4"""
        self.place_pair()
        self.write("docs/decisions/engine.md", "# Something else\n\n状态：当前有效。\n")
        code, report, plan = self.preview("dev/decisions/engine.md", "docs/decisions/engine.md")
        self.assertEqual(code, 1, report)
        self.assertIn("archive-collision", self.rules(report))

    def test_apply_rolls_back_when_commit_fails(self):
        """PW-45.5"""
        self.place_pair()
        code, preview, plan = self.preview("dev/decisions/engine.md", "docs/decisions/engine.md")
        self.assertEqual(code, 0, preview)
        before = (self.root / "dev/decisions/engine.md").read_bytes()
        linker_before = (self.root / "docs/engine-req.md").read_bytes()
        original = wiki.move_file_without_overwrite

        def fail_move(source, destination):
            raise OSError("simulated commit failure")

        from unittest import mock
        captured = wiki.Wiki(wiki.Snapshot(self.root), "docs/wiki.json")
        with mock.patch.object(wiki, "move_file_without_overwrite", side_effect=fail_move):
            report = wiki.move_apply(captured, "dev/decisions/engine.md", "docs/decisions/engine.md", plan)
        self.assertIn("archive-apply-failed", {f["rule"] for f in report["findings"]})
        self.assertEqual((self.root / "dev/decisions/engine.md").read_bytes(), before)
        self.assertEqual((self.root / "docs/engine-req.md").read_bytes(), linker_before)
        self.assertFalse((self.root / "docs/decisions/engine.md").exists())

    def test_directory_collision_and_partial_rollback_preserve_other_files(self):
        """PW-45.5 A destination created after preview is never treated as ours."""
        from unittest import mock
        self.place_pair()
        self.write("dev/batch/README.md", "# Original\n")
        source, dest = self.root / "dev/batch", self.root / "docs/batch"
        captured = wiki.Wiki(wiki.Snapshot(self.root))
        plan = wiki.move_report(captured, "dev/batch", "docs/batch")["plan_sha256"]
        mkdir = wiki.os.mkdir
        def collision(path, *args, **kwargs):
            if path == dest:
                mkdir(path)
                (dest / "README.md").write_text("# Other\n")
            return mkdir(path, *args, **kwargs)
        with mock.patch.object(wiki.os, "mkdir", side_effect=collision):
            result = wiki.move_apply(wiki.Wiki(wiki.Snapshot(self.root)), "dev/batch", "docs/batch", plan)
        self.assertIn("archive-apply-failed", self.rules(result))
        self.assertEqual((source / "README.md").read_text(), "# Original\n")
        self.assertEqual((dest / "README.md").read_text(), "# Other\n")

    def test_partial_move_rollback_refuses_source_collision(self):
        """PW-45.5 Rollback preserves a newly created source entry and reports writes."""
        from unittest import mock
        self.place_pair()
        self.write("dev/batch/a.md", "# Original\n")
        self.write("dev/batch/b.md", "# Second\n")
        source = self.root / "dev/batch"
        plan = wiki.move_report(wiki.Wiki(wiki.Snapshot(self.root)), "dev/batch", "docs/batch")["plan_sha256"]
        move = wiki.move_file_without_overwrite
        def fail_second(src, dst):
            if src == source / "b.md":
                (source / "a.md").write_text("# Other\n")
                raise OSError("injected failure")
            return move(src, dst)
        with mock.patch.object(wiki, "move_file_without_overwrite", side_effect=fail_second):
            result = wiki.move_apply(wiki.Wiki(wiki.Snapshot(self.root)), "dev/batch", "docs/batch", plan)
        self.assertIn("archive-rollback-failed", self.rules(result))
        self.assertTrue(result["writes"])
        self.assertEqual((source / "a.md").read_text(), "# Other\n")
        self.assertEqual((self.root / "docs/batch/a.md").read_text(), "# Original\n")

    def test_symlink_paths_and_protected_parent_are_rejected(self):
        """PW-45.7 PW-45.11 Neither command may escape root or carry tool inputs."""
        import tempfile
        self.place_pair()
        with tempfile.TemporaryDirectory() as external:
            (self.root / "dev/out").symlink_to(external, target_is_directory=True)
            code, result, _ = self.preview("docs/engine-req.md", "dev/out/engine-req.md")
            self.assertEqual(code, 1, result)
            self.assertIn("archive-unsafe-path", self.rules(result))
        code, result, _ = self.preview("docs", "dev/old-docs")
        self.assertEqual(code, 1, result)
        self.assertIn("move-source-protected", self.rules(result))
        code, result = self.run_cli("archive", "docs")
        self.assertEqual(code, 1, result)
        self.assertIn("move-source-protected", self.rules(result))

    def test_post_move_check_failure_keeps_write_report(self):
        """PW-45.12 A failed post-move check does not erase completed writes."""
        from unittest import mock
        self.place_pair()
        captured = wiki.Wiki(wiki.Snapshot(self.root))
        plan = wiki.move_report(captured, "dev/decisions/engine.md", "docs/decisions/engine.md")["plan_sha256"]
        with mock.patch.object(wiki, "check", side_effect=wiki.WikiError("input vanished")):
            result = wiki.move_apply(captured, "dev/decisions/engine.md", "docs/decisions/engine.md", plan)
        self.assertEqual(result["after_check"], "incomplete")
        self.assertTrue(result["writes"])
        self.assertIn("archive-after-check-failed", self.rules(result))
        self.assertTrue((self.root / "docs/decisions/engine.md").exists())

    def test_destination_symlink_added_after_preview_is_rejected(self):
        """PW-45.11 Recalculate path safety on apply."""
        import tempfile
        self.place_pair()
        code, preview, plan = self.preview("dev/decisions/engine.md", "docs/out/engine.md")
        self.assertEqual(code, 0, preview)
        with tempfile.TemporaryDirectory() as external:
            (self.root / "docs/out").symlink_to(external, target_is_directory=True)
            code, result = self.run_cli("move", "dev/decisions/engine.md", "docs/out/engine.md", "--apply", "--expect", plan)
            self.assertEqual(code, 1, result)
            self.assertIn("archive-unsafe-path", self.rules(result))
            self.assertTrue((self.root / "dev/decisions/engine.md").exists())
            self.assertFalse((__import__("pathlib").Path(external) / "engine.md").exists())

    def test_late_failure_rolls_back_rewritten_moved_file_and_directory(self):
        """PW-45.5 Restoring a rewritten moved entry must update its identity."""
        from unittest import mock
        for directory in (False, True):
            with self.subTest(directory=directory):
                self.place_pair()
                self.write("docs/INDEX.md", "# Index\n")
                if directory:
                    self.write("dev/batch/a.md", "# Batch\n\n[Req](../../docs/engine-req.md)\n")
                    self.write("docs/z-link.md", "# Link\n\n[Batch](../dev/batch/a.md)\n")
                    source, dest = "dev/batch", "docs/batch"
                    original = self.root / "dev/batch/a.md"
                else:
                    source, dest = "dev/decisions/engine.md", "docs/decisions/engine.md"
                    original = self.root / source
                before = original.read_bytes()
                captured = wiki.Wiki(wiki.Snapshot(self.root))
                plan = wiki.move_report(captured, source, dest)["plan_sha256"]
                replace = wiki.os.replace
                count = 0
                def fail_late(src, dst):
                    nonlocal count
                    if ".wiki-archive-" in str(src):
                        count += 1
                        if count == 2:
                            raise OSError("late failure")
                    return replace(src, dst)
                with mock.patch.object(wiki.os, "replace", side_effect=fail_late):
                    result = wiki.move_apply(captured, source, dest, plan)
                self.assertIn("archive-apply-failed", self.rules(result))
                self.assertNotIn("archive-rollback-failed", self.rules(result), result)
                self.assertEqual(original.read_bytes(), before)
                self.assertFalse((self.root / dest).exists())

    def test_archive_destination_inside_source_is_rejected(self):
        """PW-45.8 An archive root nested in its source cannot be moved into itself."""
        self.place_pair()
        self.config["roots"] = [{"path": "docs", "role": "knowledge"},
                                {"path": "dev", "role": "process"},
                                {"path": "dev/archive", "role": "archive"}]
        self.config["archive_root"] = "dev/archive"
        self.save_config()
        code, result = self.run_cli("archive", "dev")
        self.assertEqual(code, 1, result)
        self.assertIn("move-invalid", self.rules(result))
        self.assertTrue((self.root / "dev/decisions/engine.md").exists())

    def test_no_atomic_rename_falls_back_for_regular_files_only(self):
        """PW-45.4 Missing platform primitive must never use overwriting rename."""
        from unittest import mock
        self.write("dev/a.md", "# A\n")
        source, target = self.root / "dev/a.md", self.root / "dev/b.md"
        with mock.patch.object(wiki.ctypes, "CDLL", return_value=object()):
            wiki.move_file_without_overwrite(source, target)
            self.assertEqual(target.read_text(), "# A\n")
            source.write_text("# Other\n")
            with self.assertRaises(FileExistsError):
                wiki.move_file_without_overwrite(source, target)
            self.assertEqual(target.read_text(), "# A\n")
            with self.assertRaises(OSError):
                wiki.move_file_without_overwrite(self.root / "dev", self.root / "new-dir")

    def test_fallback_unlink_failure_preserves_foreign_or_reports_remaining_link(self):
        """PW-45.5 A failed hard-link move never deletes a replacement or hides a link."""
        from unittest import mock
        for replaced in (False, True):
            with self.subTest(replaced=replaced):
                self.place_pair()
                source = self.root / "dev/decisions/engine.md"
                destination = self.root / "docs/decisions/engine.md"
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.unlink(missing_ok=True)
                captured = wiki.Wiki(wiki.Snapshot(self.root))
                plan = wiki.move_report(captured, "dev/decisions/engine.md", "docs/decisions/engine.md")["plan_sha256"]
                real_unlink = wiki.os.unlink
                def fail_unlink(path, *args, **kwargs):
                    if path == source:
                        if replaced:
                            real_unlink(destination)
                            destination.write_text("# Other writer\n")
                        raise OSError("injected source unlink failure")
                    if path == destination:
                        raise OSError("injected cleanup failure")
                    return real_unlink(path, *args, **kwargs)
                with mock.patch.object(wiki.ctypes, "CDLL", return_value=object()), \
                     mock.patch.object(wiki.os, "unlink", side_effect=fail_unlink):
                    result = wiki.move_apply(captured, "dev/decisions/engine.md", "docs/decisions/engine.md", plan)
                self.assertIn("archive-rollback-failed", self.rules(result), result)
                self.assertTrue(any("created hard link" in item for item in result["writes"]))
                self.assertTrue(source.exists())
                self.assertTrue(destination.exists())
                if replaced:
                    self.assertEqual(destination.read_text(), "# Other writer\n")
                else:
                    self.assertEqual(source.stat().st_ino, destination.stat().st_ino)

    def test_destination_outside_registered_roots_is_refused(self):
        """PW-45.6"""
        self.place_pair()
        # tmp is excluded and under no registered root.
        code, report, _ = self.preview("dev/decisions/engine.md", "tmp/engine.md")
        self.assertEqual(code, 1, report)
        self.assertIn("move-destination-outside", self.rules(report))

    def test_protected_sources_cannot_move(self):
        """PW-45.7"""
        self.place_pair()
        self.config["generated_index"] = "docs/wiki-index.json"
        self.save_config()
        for source in ("docs/wiki.json", "docs/wiki-index.json"):
            code, report, _ = self.preview(source, "docs/moved.json")
            self.assertEqual(code, 1, (source, report))
            self.assertIn("move-source-protected", self.rules(report))

    def test_invalid_source_same_path_and_nested_destination(self):
        """PW-45.8"""
        self.place_pair()
        code, report, _ = self.preview("dev/decisions/missing.md", "docs/decisions/missing.md")
        self.assertIn("move-invalid", self.rules(report))
        code, report, _ = self.preview("dev/decisions/engine.md", "dev/decisions/engine.md")
        self.assertIn("move-invalid", self.rules(report))
        self.write("dev/modules/engine/README.md", "# Mod\n\n状态：当前有效。\n")
        code, report, _ = self.preview("dev/modules/engine", "dev/modules/engine/inner")
        self.assertIn("move-invalid", self.rules(report))

    def test_renaming_the_file_triggers_naming_checks(self):
        """PW-45.9"""
        self.place_pair()
        # Same name, only new directory: no new-path naming check, so an unsafe
        # character in the unchanged name is not re-flagged.
        code, report, _ = self.preview("dev/decisions/engine.md", "docs/decisions/engine.md")
        self.assertNotIn("name-unsafe-character", self.rules(report))
        # Changed filename with an unsafe character is flagged.
        code, report, _ = self.preview("dev/decisions/engine.md", "docs/decisions/new (draft).md")
        self.assertEqual(code, 1, report)
        self.assertIn("name-unsafe-character", self.rules(report))

    def test_archive_destination_points_to_archive_command(self):
        """PW-45.10"""
        self.place_pair()
        code, report, _ = self.preview("dev/decisions/engine.md", "archive/dev/decisions/engine.md")
        self.assertEqual(code, 1, report)
        self.assertIn("move-use-archive", self.rules(report))

    def test_restoring_from_archive_is_allowed(self):
        """PW-45.10"""
        self.place_pair()
        self.write("archive/docs/restored.md", "# Restored topic\n\n状态：当前有效。\n")
        self.write("docs/INDEX.md", "# Current\n\n[Work](../dev/INDEX.md)\n[Req](engine-req.md)\n"
                                    "[Decision](../dev/decisions/engine.md)\n")
        code, report, plan = self.preview("archive/docs/restored.md", "docs/restored.md")
        self.assertEqual(code, 0, report)
        self.assertNotIn("move-use-archive", self.rules(report))
        code, report = self.run_cli("move", "archive/docs/restored.md", "docs/restored.md",
                                    "--apply", "--expect", plan)
        self.assertEqual(code, 0, report)
        self.assertTrue((self.root / "docs/restored.md").is_file())
        self.assertFalse((self.root / "archive/docs/restored.md").exists())


if __name__ == "__main__":
    import unittest
    unittest.main()
