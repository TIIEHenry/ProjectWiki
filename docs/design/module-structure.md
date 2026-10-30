# 目录与模块结构

本页描述 ProjectWiki 仓库自身的目录。接入项目的目录结构见[文档模型](document-model.md)和 [NoteBox 参考项目](../../demo/README.md)。目录变化时原位更新本页。

| 路径 | 职责 |
|---|---|
| `README.md` | 系统介绍与入口 |
| `AGENTS.md` | 开发这套系统时必须遵守的规则与阅读路由 |
| `TODO.md` | 系统还没做的事 |
| `CHANGELOG.md` | 对接入项目有影响的变化 |
| `docs/` | 系统规范：需求、原则、设计、开发流程、写作与开发规范、接入指南、设计取舍 |
| [`scripts/wiki/`](../../scripts/wiki/README.md) | 可复制的本地文档工具。`README.md` 是入口，`reference.md` 登记配置和规则，`formats.md` 是工具读取的固定写法的权威正文；三份随工具复制，只链接本目录里的文件 |
| `tests/` | 文档工具的反例与行为测试 |
| `templates/` | 接入时使用的最小模板 |
| `demo/` | 独立配置、可运行的 NoteBox 参考项目，演示接入后的完整结构 |
| `tmp/` | 讨论草稿，不进 Git，不属于规范 |

本仓库没有 `dev/` 和 `archive/`：系统的开发过程不按接入项目的方式记录，变化写在提交信息和 `CHANGELOG.md`，旧版本由 Git 保存。

## 规范的组织

`docs/requirements/` 说明系统要解决的问题与验收要求。`docs/principles/` 说明组织知识时必须保持的约束。`docs/design/` 解释接入后的结构与工具行为。`docs/guides/` 提供接入和日常开发的操作步骤。`docs/standards/` 规定写作要求和本仓库的开发要求。`docs/decisions/` 记录系统设计中的重要取舍。

## 参考项目边界

`demo/` 是独立项目样本，使用自己的 `docs/wiki.json`，用 `--root demo` 检查。根目录的 `docs/wiki.json` 只登记本仓库的规范文档，用来检查链接和工具说明的规则名对账，并排除 `demo/`、`templates/` 和 `tmp/`。

参考项目中的模块布局不限制接入项目。已有仓库可以继续使用 `core/`、`packages/` 或其他源码布局，只需登记模块入口与文档根。

## 工具与模板

检查器读取目标项目的配置，所有配置路径相对目标项目根目录。模板提供结构和写法，复制后必须替换示例目标、模块和验证命令。

其他项目的 Agent 应通过[接入指南](../guides/adoption.md)选择最小内容集合。已有有效文档可以直接登记，不需要先移动全部文件。
