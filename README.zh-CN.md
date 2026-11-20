# ProjectWiki

[English](README.md) · **中文**

ProjectWiki 是一套放进代码仓库的文档系统，供开发者和编码 Agent 共同使用。它包括：组织文档的规范、接入步骤、可复制的模板，以及一个只依赖 Python 标准库的检查工具。

它面向人和 Agent 需要依靠项目文档的场景：新成员理解项目，Agent 定位修改范围，开发者维护接口与设计，协作者接续任务，维护者追溯历史决定。接入的项目可以是单模块工具，也可以由多种构建系统组成。

中文介绍，2 分 46 秒。

https://github.com/user-attachments/assets/df0ff5c5-ed0a-4155-8e2e-a23cac87e7be

英文介绍，2 分 46 秒。

https://github.com/user-attachments/assets/2fd09db3-88b2-48fd-bfba-666e4d086294

## 接入后的目录

接入后，项目把三类内容分开存放：当前有效的知识、进行中的开发记录和历史。

| 路径 | 内容 |
|---|---|
| `AGENTS.md` | 适用于整个项目的硬规则，以及按任务指向应读页面的路由表 |
| `docs/` | 当前知识：需求、原则、设计、规范、指南和决策记录，原位修订 |
| `dev/` | 开发过程：路线图、计划、审查和待处理项 |
| `archive/` | 已结束的过程材料和整篇失效的文档，保持原相对路径 |
| `<模块>/README.md`、`<模块>/docs/` | 模块入口和只属于这个模块的知识，放在源码旁边 |

`docs/`、`dev/`、`archive/` 三个根目录并列。完整的例子见 [NoteBox 参考项目](demo/README.md)。本仓库是文档系统本身，不按接入项目运转：没有 `dev/` 和 `archive/`，根目录只有规范、模板、检查工具和测试。

## 规则概要

- 当前知识、过程记录和历史分开保存。已确认但尚未实现的需求仍属于知识，任务进度不改变需求本身的效力。
- 上下文按任务逐层提供。项目入口提供全局硬规则和阅读路由，模块入口提供模块的职责与契约，专题页提供细节，源码和测试用于确认代码的实际行为。项目为入口页设定字符预算，页面超出预算时检查失败。
- 同一主题只有一份权威正文，其他页面链接过去，不复述。影响整个项目、忽略后会导致错误的规则同时直接写在 `AGENTS.md` 里，遵守它不依赖 Agent 继续打开链接。
- 当前知识原位修订，修订历史由 Git 保存。只有所记录的工作已经结束，或整篇不再适用时，文档才归档。
- 控制文档数量。新内容写成已有文件里的一节；只有它有自己的生命周期，或者需要多人同时写时才单独成文。收件箱这类一条一个文件的记录，必须同时规定每条怎样结束。
- 流程按影响展开。普通修复可以只改代码和测试，在提交信息里说明依据。出现重要取舍、跨模块契约变化、数据迁移或协作交接时，再补设计、计划和决策记录。

这些规则的理由见[设计原则](docs/principles/document-system.md)。

## 检查工具

`scripts/wiki/wiki.py` 是单个 Python 文件，需要 Python 3.10 或更新版本，不需要第三方库；检查暂存内容和提交提醒还需要 Git。项目在 `docs/wiki.json` 里登记文档根目录、入口页、模块和页面预算，工具按这份配置工作。

- `check` 检查登记的入口页是否存在、本地链接和锚点是否有效、页面是否超出预算，以及状态行、需求条目和审查记录是否符合工具读取的写法。项目登记了需求时，`check` 还统计有多少验收条目被测试按编号引用，并对已实现的需求里既没有测试引用、也没有标人工验证的验收条目给出警告。
- Git 钩子对暂存快照运行 `check`。代码有改动而为它登记的文档没有改动时，`remind` 在提交时提醒。提醒只依赖 Git，所以用任何 Agent 工具或手工 `git commit` 都能看到。
- `archive` 和 `move` 先给出预览，再执行并改写受影响的链接。
- `baseline` 记录旧仓库已有的问题，之后只有新问题会让检查失败。

工具不判断文章里的设计或业务结论是否正确。检查无法完成时报告为 incomplete，不报告为通过。工具只在命令明确要求时写文件（`archive --apply`、`move --apply`、`index --write`、`export-okf`），`verify` 会运行项目登记的命令。工具不暂存、不提交，Git 钩子也不改文件。

接入的项目复制整个 `scripts/wiki/` 目录。除检查工具外，目录里还有 Git 钩子，说明命令、规则和写法的文档，以及指导 Agent 完成接入、对照实现审查文档等任务的技能。

## 试一下

在本仓库根目录检查参考项目：

```bash
python3 scripts/wiki/wiki.py check --root demo
```

输出的第一行是 `check: passed (0 errors, 0 warnings)`。

## 给项目接入

接入从小处开始：在项目里选一项功能修改和一项维护任务，只建立这两项任务用得到的页面。仍然有效的文档在原位登记，不必先搬动或改写。步骤见[接入指南](docs/guides/adoption.md)。也可以让编码 Agent 按[接入技能](scripts/wiki/skills/adopt-projectwiki/SKILL.md)完成：告诉它本仓库的位置和要接入的项目。

## 语言

ProjectWiki 用中文编写，中文页是权威正文。理解和接入需要的部分另有英文版：

| 中文 | 英文 |
|---|---|
| `docs/` 下的规范 | [`docs/en/`](docs/en/INDEX.md)：设计原则、设计文档、接入指南、开发流程和写作规范 |
| `scripts/wiki/` 下的工具说明和技能 | [`scripts/wiki/en/`](scripts/wiki/en/README.md)，随检查工具一起复制到接入项目 |
| `templates/` 下的模板 | [`templates/en/`](templates/en/README.md)，使用英文关键词 |
| `demo/` 里的 NoteBox 参考项目 | [`demo-en/`](demo-en/README.md) |

需求、决策记录、变更记录、待办和 ProjectWiki 自身的开发约定只有中文版。英文页与中文页不一致时，以中文页为准。

检查工具能读两种语言的文档：它读取的每个关键词和状态值都有中文和英文两种写法，例如 `状态：执行中。` 和 `Status: active.`，全部列在[工具读取的写法](scripts/wiki/formats.md)里。工具用英文报告问题，其中的示例用中文写法；`verify` 生成的验证记录是中文。

## 从哪里开始

| 你要做什么 | 阅读入口 |
|---|---|
| 理解这些规则的理由 | [设计原则](docs/principles/document-system.md) |
| 给一个项目接入 | [接入指南](docs/guides/adoption.md)、[接入技能](scripts/wiki/skills/adopt-projectwiki/SKILL.md) |
| 看一个完整实例 | [NoteBox 参考项目](demo/README.md) |
| 理解 ADR、计划、路线图和审查的分工 | [开发流程](docs/guides/workflow.md) |
| 创建或审查文档 | [中文技术文档规范](docs/standards/writing.md) |
| 运行检查工具或查一条规则 | [工具入口](scripts/wiki/README.md)、[配置与规则](scripts/wiki/reference.md)、[工具读取的写法](scripts/wiki/formats.md) |
| 查找全部规范文档 | [规范导航](docs/INDEX.md) |
| 修改 ProjectWiki 本身 | [开发约定](AGENTS.md)、[待办](TODO.md)、[变更记录](CHANGELOG.md) |

## 许可证

ProjectWiki 以 [MIT 许可证](LICENSE)发布。
