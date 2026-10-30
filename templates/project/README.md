# 【待填：项目名称】

【待填：项目为谁解决什么问题，当前范围是什么。】

- 当前知识：[知识入口](docs/INDEX.md)。
- 开发与接续：[开发入口](dev/INDEX.md)。
- Agent 约束：[AGENTS.md](AGENTS.md)。

## 本地运行与验证

【待填：环境前提、工作目录、可直接执行的命令、成功与失败的表现。】

Wiki 工具由 ProjectWiki 提供。复制 `scripts/wiki/` 后，在本仓库运行 `python3 scripts/wiki/wiki.py verify --root .`；它运行 `docs/wiki.json` 的 `verify` 里登记的全部命令，模板默认只有文档检查。工具的命令、配置和固定写法分别见 `scripts/wiki/` 里的 `README.md`、`reference.md` 和 `formats.md`。
