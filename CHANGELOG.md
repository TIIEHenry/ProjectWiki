# 变更记录

按版本记录文档系统的规则、模板和工具有哪些变化，以及接入项目升级时要注意什么。不记开发过程。

## 未发布

### 仓库结构

- 仓库只包含文档系统本身：规范、模板、工具和测试。根目录不再按接入项目运转，撤掉了根 `dev/`（计划、路线图、待处理项）和 `archive/`。接入效果由 [NoteBox 参考项目](demo/README.md) 演示和验证。
- 开发流程从 `dev/workflow.md` 移到 [docs/guides/workflow.md](docs/guides/workflow.md)，写成给接入项目的指南。
- 还没做的事改记在 [TODO.md](TODO.md)。

- 规范去重：工具说明拆成三份，都在 `scripts/wiki/` 里，随工具复制到接入项目：[工具入口](scripts/wiki/README.md)写命令和钩子安装，[配置与规则](scripts/wiki/reference.md)是按规则名检索的登记表，[工具读取的写法](scripts/wiki/formats.md)是状态行、核对行、需求条目、审查问题、待处理项和编号分配的权威正文。[自动化设计](docs/design/automation.md)只保留取舍理由。这三份只链接 `scripts/wiki/` 里的文件，复制后链接不会失效。

### 规则与模板

- 计划和审查的状态行可以写负责人 `负责：agent:<名字>`；模板已加这一项。
- 写作规范新增：排查类指南按症状组织；跨模块契约写明提供方和消费方；术语表的写法；截图、原型和线框的引用方式，并要求用文字写出结论。
- 项目 AGENTS 模板新增：拿不准放哪里时写进 `dev/inbox/<类型>/`。项目概览模板新增可选的产品边界表。
- 计划和决策记录在标题下第一行写状态。
- 需求条目带编号、状态和验收子编号，设计、计划和测试按编号引用。
- 不能由命令证明的需求验收项可以标记为人工验证，并用 `验收核对：<编号>，agent:<名字>，YYYY-MM-DD。` 记录核对人和日期；模板、文档模型和参考项目按同一写法维护。
- 审查放在一个日期目录里，每条问题一个小节，核对、方案和签收写进问题小节。
- 知识页可以写核对行和复核期限，核对人写成 `human:` 或 `agent:`。
- 验证记录用 `verify` 生成；归档先预览再用 `--apply` 执行。
- 设计原则新增"规则分强弱"：不变量固定为错误，默认约定由项目在配置里调整，建议只靠评审；已有内容优先登记格式，不为通过检查改写。
- 决策模板只保留现行约束与入口，不记录一次改动同步了哪些文件；已有决策记录移除开发流水和未解释的外部项目名称。
- 新建文档检查会拒绝影响归档链接改写的空格、`#`、`%` 和括号，提示模板占位名（`plan.md`、`decision.md`、`inbox-item.md`）及状态或版本词，并报告只差大小写的同目录冲突。暂存检查不检查归档根下的路径和不改文件名的移动，旧文件名不妨碍归档。
- 项目模板的 `docs/wiki.json` 默认在 `verify` 里登记文档检查，复制模板和 `scripts/wiki/` 后就能运行 `verify`。审查模板的状态改为默认值"执行中"。
- 项目模板和参考项目的配置给 `dev/plans`、`dev/inbox/*` 和 `dev/reviews/*` 设了目录文件数预算。
- 待处理项有了结束方式：写明去向，状态改为"已完成"，然后归档。模板、生命周期和 demo 收件箱说明已同步。
- 项目模板不再引用 ProjectWiki 自己的 `docs/`，改为指向随工具复制的 `scripts/wiki/formats.md`。
- 需求编号和审查路号的分配规则：并行分支撞号时后合并的一方改号；审查路号由负责汇总的人分配。
- 设计原则不再一概禁止日期前缀：日期只能表示不再改变的时间点，例如审查目录的开始日期。

### 工具

- `check`：状态行、需求追踪、审查记录、核对行、目录文件数预算、存量问题基线、文档与代码的名单对账（`reconcile`）、计划负责人格式（`owner-format`）、没有入口的页面和资产（`orphan-page`、`orphan-asset`，警告）。没有登记 `archive` 角色目录时照常运行，只是不做历史匹配；`archive` 和 `archive --summary` 报告 `input-unavailable`。
- `remind`：提交时提醒同步文档，提醒长期未更新或已结束未归档的计划，提醒到期的复核期限，列出执行中和阻塞的计划及负责人。
- `archive --apply --expect <plan_sha256>`：执行与预览相同的归档计划，改写链接，可在历史索引加一行。先准备所有改写内容，提交阶段失败时尝试逆序回滚；强制终止仍可能留下中间状态。归档目录时，计划哈希覆盖目录里实际移动的每一项（包括非 Markdown、被排除和未跟踪的文件及空目录），预览后有任何变化就拒绝执行；预览用 `other_files_moved` 列出这些文件。目的地是空目录、或上级路径是文件时，预览就报告 `archive-collision`。
- `verify`：运行登记的验证命令，输出验证记录。
- `index --write`：写生成目录。
- `export-okf`：导出 Open Knowledge Format v0.2 bundle。
- 需求追踪：`requirements.id_pattern` 可以登记项目自己的需求编号格式，例如 `REQ-AUTH-001` 或 `FR-1.2`；`requirements` 里的未知字段现在会报告 incomplete。
- `remind --staged`：改动文件和行数从启动时捕获的索引与 HEAD 对象计算，不再重新读取实时索引；只读取对象 ID 变化的文件。仓库里有符号链接或子模块时照常运行，这些路径计为改动但不计行数。
- `remind --staged` 新增 `[user]` 提醒 `human-claim-added`：暂存的 Markdown 新增了写着 `human:<名字>` 的行时，请提交者向用户确认。
- `remind` 新增待处理项提醒 `inbox-stale`、`inbox-finished-not-archived`、`inbox-no-status`，路径默认 `dev/inbox/*/*.md`，可用 `remind.inbox` 修改，天数沿用 `plan_stale_days`。
- `check` 新增 `trace-check-not-manual` 警告：验收核对记录只代替标了人工验证的条目，写在其他条目下不再消除 `trace-no-test`。
- 关键词集中在 `wiki.py` 的 `KEYWORDS` 表里，解析正则由它生成，测试核对它和 `formats.md` 一致。审查判定不再识别 `hold`、`weaken`、`drop`，改用 `confirmed`、`narrowed`、`rejected`。

### 参考项目

- NoteBox 登记了 `verify` 和一份 `reconcile`（模块需求里的错误信息与 `title.py` 对账），新增带表格的 `archive/INDEX.md`，审查目录写了负责人。

升级注意：配置新增的字段都是可选的，旧配置不改也能运行。升级后第一次运行 `check` 可能多出 `orphan-page`、`orphan-asset` 警告，它们不会让检查失败；确实不需要入口的路径登记在 `orphan_ignore` 里。复制新版 `scripts/wiki/` 时，`reference.md` 和 `formats.md` 要一起复制；链接到旧 `scripts/wiki/README.md#…` 小节的文档改链到 `reference.md`。审查问题用了 `hold`、`weaken`、`drop` 判定的，改成对应的 `confirmed`、`narrowed`、`rejected`。用验收核对记录代替测试的非人工验收条目，会重新出现 `trace-no-test`：补测试，或者确认命令证明不了后加人工验证标记。
