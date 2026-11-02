# NoteBox 示例项目

NoteBox 为笔记提供标题校验。示例包含可运行的小模块，以及需求、原则、设计、开发记录和归档之间的关系。它用于演示文档系统，未提供持久化或网络服务。

- 查当前知识：从 [知识入口](docs/INDEX.md) 开始。
- 修改标题规则：从 [标题模块](notes/README.md) 开始。
- 接续工作：从 [开发入口](dev/INDEX.md) 开始。
- 接入其他项目时，先阅读 ProjectWiki 的接入指南；本示例目录可以独立复制。

在 `demo/` 下运行测试：

```sh
python3 -m unittest discover -s notes/tests -v
```

文档工具由 ProjectWiki 提供。单独复制本示例时，把 `scripts/wiki/` 一起复制到根目录，再运行 `python3 scripts/wiki/wiki.py verify --root .`；在 ProjectWiki 仓库里，从仓库根目录运行 `python3 scripts/wiki/wiki.py verify --root demo`。

给其他项目首次接入或补齐未完成的接入时，可使用 ProjectWiki 提供的接入技能：首次从源仓库的 `scripts/wiki/skills/adopt-projectwiki/SKILL.md` 打开，完整复制工具后从目标项目本地打开。源仓库提供模板与完整接入指南，写入对象是用户指定的目标项目；按路径打开技能不代表宿主已原生安装。

完整的 `scripts/wiki/skills/` 还提供文档审查、文档整理、知识沉淀与同步文档提交技能。Agent 按 `AGENTS.md` 的任务表读取，操作当前项目；示例不另存正文，也不要求每次任务或提交都调用。宿主原生技能发现需要另行登记和验证。

示例的文档开发流程默认遵循 `scripts/wiki/workflow.md`，项目业务约束保留在 `AGENTS.md` 和模块知识中；共享流程适配按其中“共享流程与项目适配”处理。

示例仓库保持 `docs/`、`dev/`、`archive/` 并列。`notes/docs/` 保存模块知识。已结束的计划在 `archive/dev/plans/`；当前标题规则原位维护，修订历史交给 Git。

这些示例文件不要求每项修改都照建一份。普通标题校验修复可以只修改代码和测试，在提交信息里解释依据；边界明确且没有重要契约或风险变化的新行为，用需求条目和测试追踪。契约或重要风险变化时补充相关设计，多步骤协作或交接时建立计划，需要长期解释的重要取舍写决策记录。
