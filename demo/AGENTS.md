# NoteBox 开发约束

- 当前需求、原则和设计在 `docs/` 与 `notes/docs/`。`dev/` 记录待办与实施过程；`archive/` 保存历史，不能直接当作当前规则。
- 标题必须按 Unicode 码点计数，去除首尾空白后为 1–60 个字符（需求 NB-01）。不允许静默截断用户输入。
- 稳定知识面向人类阅读，写清具体对象、适用条件和行为，避免 AI 套话、翻译腔与未解释的内部简称。
- 新建文档路径不得含空格、`#`、`%` 或括号；复制模板后改成具体主题名。状态和版本写在正文，不把它们写进稳定知识的文件名。
- 整页归档到 `archive/<原相对路径>`，保持文件名与目录；目标已存在时停止，不覆盖。用 `python3 scripts/wiki/wiki.py archive <路径> --root .` 预览，再加 `--apply --expect <plan_sha256>` 执行，不手工移动文件和改链接。新建前检查对应历史，命中后判断恢复、延续或新主题，不把同名历史当作永久禁名。
- 改标题处理时，先读 [模块入口](notes/README.md) 与 [模块需求](notes/docs/requirements.md)，核对受影响的设计和测试。
- 标题错误信息（`ValueError` 的文字）只在 [模块需求](notes/docs/requirements.md) 里写一遍；改了代码里的信息却没改需求时，`check` 会报 `reconcile-missing-in-doc`。
- 修改实现后运行 `python3 scripts/wiki/wiki.py verify --root .`，它运行 `docs/wiki.json` 里登记的测试。计划的验证记录直接用它的输出，不手写命令结果；失败时记录具体失败，不能声称已通过。
- Wiki 检索默认聚焦有效内容。普通 `rg` 通过 `.ignore` 排除归档；需要历史时可用 `rg --no-ignore '关键词' archive/`。`grep -R` 不读取 `.ignore`，常规查询可加 `--exclude-dir=archive`。
- 当前知识变化时原位更新对应正文；不为每次提交新建计划，也不机械改写状态页。
- 发现问题或想法但拿不准放哪里、要不要做时，写进 `dev/inbox/<类型>/`（例子见 [待处理项](dev/inbox/README.md)），不要直接改 `docs/`。处理完时写明去向，状态改为"已完成"，再用 `archive` 归档。
- 状态行、核对行、需求条目和审查问题的写法以 `scripts/wiki/formats.md` 为准；提交里新增 `human:` 名字时钩子会给出 `[user]` 提醒，Agent 不得把自己写成 `human:`。
- 按 ProjectWiki 接入指南安装 Git 钩子后，每次提交都会运行文档提醒，配置在 `docs/wiki.json` 的 `remind`。看到 `[agent]` 提醒，就更新 `notes/docs/` 或模块入口，或者在提交信息最后一段写 `Docs-Reviewed: notes <理由>`；看到 `[user]` 提醒，先向用户确认需求或决策变更。不得用 `--no-verify` 跳过钩子。
- 改变标题计数等已有决定时，先写新的决策记录替代旧记录，并在同一次改动中更新本文件、项目需求、模块需求与设计、故障维护指南中仍写着旧规则的地方。按链接和关键词（如"码点"）两种方式查找。

更多约定见 [开发规范](docs/standards/development.md)。接续已有工作才需要读 [开发入口](dev/INDEX.md)。
