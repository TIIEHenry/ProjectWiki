# [TODO: project name]

[TODO: whose problem the project solves, what the problem is, and what the current scope is.]

- Current knowledge: [knowledge entry](docs/INDEX.md).
- Development and continuing work: [development entry](dev/INDEX.md).
- Agent constraints: [AGENTS.md](AGENTS.md).

## Running and verifying locally

[TODO: environment prerequisites, the working directory, commands that can be run directly, and what success and failure look like.]

The wiki tool is provided by ProjectWiki. After copying `scripts/wiki/`, run `python3 scripts/wiki/wiki.py verify --root .` in this repository; it runs all the commands registered in `verify` of `docs/wiki.json`, and the template has only the document check by default. The tool's commands, configuration, fixed formats, and development workflow are in `README.md`, `reference.md`, `formats.md`, and `workflow.md` under `scripts/wiki/en/`.
