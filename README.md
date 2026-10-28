# ProjectWiki

ProjectWiki 提供一套可放进代码仓库的文档结构、接入步骤、模板和本地检查工具，供开发者与编码 Agent 共同使用。

项目采用三个并列目录：`docs/` 保存需求、原则、设计和规范；`dev/` 组织开发流程与工作记录；`archive/` 保存已结束的过程材料及整体失效的文档。模块内部知识放在模块自己的 `docs/` 中。

## 从哪里开始

| 你要做什么 | 阅读入口 |
|---|---|
| 理解这套文档系统 | [设计原则](docs/principles/document-system.md) |
| 给另一个项目接入 | [接入指南](docs/guides/adoption.md) |
| 看一个完整实例 | [NoteBox 参考项目](demo/README.md) |
| 创建或审查文档 | [中文技术文档规范](docs/standards/writing.md) |
| 理解 ADR、plan、roadmap 的分工 | [开发流程](dev/workflow.md) |
| 查找全部现行文档 | [知识导航](docs/INDEX.md) |
| 修改 ProjectWiki 本身 | [当前工作](dev/INDEX.md)与[开发规范](docs/standards/development.md) |

接入项目的 Agent 应先读本文件和接入指南，检查目标仓库现状，再使用模板建立适合该项目的最小结构。现有文档优先复用，目录随内容增长展开。

## 检查示例

需要 Python 3.10 或更新版本。工具使用 Python 标准库。

```bash
python3 scripts/wiki/wiki.py check --root .
python3 scripts/wiki/wiki.py check --root demo
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s demo/notes/tests -v
```

实际支持的命令、检查范围与限制见[自动化设计](docs/design/automation.md)。本项目不会自动修改接入仓库、提交代码或迁移历史文件。
