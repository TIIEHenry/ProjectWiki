# 可复制模板

先复制 `project/` 内的文件到目标仓库，替换所有 `【待填：…】`，删除不适用内容，再填写 `docs/wiki.json`。模板配置的 `verify` 只登记了文档检查，复制 `scripts/wiki/` 后就能运行 `verify`；项目自己的测试和构建命令按[接入指南](../docs/guides/adoption.md#11-登记验证命令与对账)补上。模板配置不含 `remind`，因为代码与文档的对应关系只能按目标项目填写；按[接入指南](../docs/guides/adoption.md#8-设置文档同步提醒)补上，并安装 Git 钩子。在真实模块旁按需复制 `module/`，把模块路径登记到配置中。归档根 `archive/` 可在首次归档时建立。

首次接入或补齐未完成的接入，可按[接入技能](../scripts/wiki/skills/adopt-projectwiki/SKILL.md)处理用户指定的目标项目。首次从源仓库打开；复制完整 `scripts/wiki/` 后可从目标项目本地打开，源仓库仍提供按需读取的模板与完整接入指南。

完整复制 `scripts/wiki/` 时保留整个 `skills/`。项目模板的 `AGENTS.md` 用短任务表指向接入、审查、整理、知识沉淀与同步文档提交技能，只在需要时读取，不复制正文或增加每任务必做步骤；宿主原生发现方式见[接入指南](../docs/guides/adoption.md#4-编写关键入口)。

采用执行套件时，填写项目模板开发入口里的可选绑定节，根 `AGENTS.md` 沿该入口读取实际任务来源；职责与验证方法见[共用开发入口](../scripts/wiki/workflow.md#与执行套件共用开发入口)。不采用时删除该节，不增建空任务、队列或槽位记录。

小项目可在 `docs/overview.md` 的三个小节中分别维护需求、原则和设计。内容增长后再拆页；不要为通过检查创建空文档。接入旧项目时，按[流程清理步骤](../docs/guides/adoption.md#1-阅读-projectwiki-并调查目标项目)核对原有要求，再合并模板。接入后默认遵循[共享流程](../scripts/wiki/workflow.md#共享流程与项目适配)；保留有效内容和路径不表示保留原有流程，项目例外按共享流程适配。

| 模板 | 使用时机 |
|---|---|
| [项目最小组](project/README.md) | 首次接入 |
| [模块最小组](module/README.md) | 模块需要独立知识入口 |
| [需求](requirements.md) | 写带编号、状态和可测试验收条件的需求 |
| [实施计划](plan.md) | 工作需要步骤、验收或跨会话交接 |
| [决策记录](decision.md) | 重要取舍需要长期解释 |
| [待办条目](inbox-item.md) | 记录尚待分诊的问题或建议 |
| [审查入口](review/README.md) 与 [分路文件](review/route.md) | 一次审查：问题、核对、方案、签收都写在这两类文件里 |

`plan.md`、`decision.md` 和 `inbox-item.md` 的第一行状态要保留格式 `状态：<值>。`，检查工具靠它识别计划是否结束、决定是否被替代、待处理项是否已处理，可用的值见[工具读取的写法](../scripts/wiki/formats.md#计划决策记录和待处理项的状态行)。复制到接入项目的模板只在纯文本里提到 `scripts/wiki/formats.md`，不链接 ProjectWiki 自己的 `docs/`，因为接入项目里没有这些文件。`plan.md`、`decision.md`、`inbox-item.md` 按需复制；普通局部修复可在现有任务或提交记录中保存目标、依据和验证结果。轻量行为变化也可以只维护需求条目和测试，是否增加设计、计划或 ADR 按[影响范围](../docs/guides/workflow.md#开始工作)判断。

审查复制 `review/README.md` 到 `dev/reviews/<开始日期>-<主题>/README.md`，每一路复制一份 `review/route.md`。只有修复跨多条问题、需要单独排期时，才在同一目录用 `plan.md` 建 `plan-<主题>.md`，并加一行"覆盖问题：r01-1、r02-3"。

正文先写对象、规则与依据，区分当前事实、目标和猜测。写验证结果时填写真实命令与验证对象；模板里的空位不能作为证据。复制占位模板后改成具体主题名；文件名、类型目录和预算可以调整，原文应让未参加项目讨论的人也能理解。命名和新建检查的完整规则见 ProjectWiki 的[文档模型](../docs/design/document-model.md#文件命名)。

可运行的完整示例见 [NoteBox](../demo/README.md)。工具和接入步骤见 ProjectWiki 的 [接入指南](../docs/guides/adoption.md)。
