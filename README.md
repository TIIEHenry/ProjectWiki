# ProjectWiki

ProjectWiki 是一套放进代码仓库的文档系统，供开发者和编码 Agent 共同使用。它包括：组织文档的规范、接入步骤、可复制的模板，以及一个只依赖 Python 标准库的检查工具。

接入后的项目使用三个并列目录：`docs/` 保存需求、原则、设计和规范；`dev/` 组织开发流程与工作记录；`archive/` 保存已结束的过程材料及整体失效的文档。模块内部知识放在模块自己的 `docs/` 中。完整的例子见 [NoteBox 参考项目](demo/README.md)。

本仓库本身不按这套结构运转：根目录只有规范、模板、工具和测试。

## 从哪里开始

| 你要做什么 | 阅读入口 |
|---|---|
| 理解这套文档系统 | [设计原则](docs/principles/document-system.md) |
| 给一个项目接入 | [接入指南](docs/guides/adoption.md) |
| 看一个完整实例 | [NoteBox 参考项目](demo/README.md) |
| 理解 ADR、计划、路线图和审查的分工 | [开发流程](docs/guides/workflow.md) |
| 创建或审查文档 | [中文技术文档规范](docs/standards/writing.md) |
| 查找全部规范文档 | [规范导航](docs/INDEX.md) |
| 修改 ProjectWiki 本身 | [开发约定](AGENTS.md)、[待办](TODO.md)、[变更记录](CHANGELOG.md) |

## 检查示例

需要 Python 3.10 或更新版本。在本仓库根目录检查参考项目：

```bash
python3 scripts/wiki/wiki.py check --root demo
```

命令见[工具入口](scripts/wiki/README.md)，配置和规则见[配置与规则](scripts/wiki/reference.md)，状态行和需求条目等固定写法见[工具读取的写法](scripts/wiki/formats.md)。工具只在明确要求时写文件（`archive --apply`、`index --write`、`export-okf`），不暂存、不提交，Git 钩子也不改文件。
