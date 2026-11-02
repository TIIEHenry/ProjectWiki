# 变更记录

- `archive` 和 `move` 拒绝含符号链接的搬迁路径与携带受保护工具文件的目录；失败回滚只撤销已完成的步骤，保留其他写入者的文件，并报告未回滚的写入。执行后检查无法运行时保留写入记录。

按版本记录文档系统的规则、模板和工具有哪些变化，以及接入项目升级时要注意什么。不记开发过程。

## 未发布

- 修复合并提交中新改动漏计、普通分支变动重复计数，以及链接和 frontmatter 多行内容误判。

- 提醒并发读取计划和待处理项的历史，减少大量文件时的等待；保留各文件和观察组原有的历史扫描范围。

- 修复子目录项目的历史文档改动漏计，以及正文同名字段、英文计划状态和正文改序被误判为机械改动。

- 修复暂存文档纯移动误清零复核欠账；同一次提醒复用接入提交历史，避免逐个计划重复查询。

### 仓库结构

- 仓库只包含文档系统本身：规范、模板、工具和测试。根目录不再按接入项目运转，撤掉了根 `dev/`（计划、路线图、待处理项）和 `archive/`。接入效果由 [NoteBox 参考项目](demo/README.md) 演示和验证。
- 开发流程从 `dev/workflow.md` 移到 [docs/guides/workflow.md](docs/guides/workflow.md)，写成给接入项目的指南。
- 还没做的事改记在 [TODO.md](TODO.md)。

- 规范去重：工具说明拆成三份，都在 `scripts/wiki/` 里，随工具复制到接入项目：[工具入口](scripts/wiki/README.md)写命令和钩子安装，[配置与规则](scripts/wiki/reference.md)是按规则名检索的登记表，[工具读取的写法](scripts/wiki/formats.md)是状态行、核对行、需求条目、审查问题、待处理项和编号分配的权威正文。[自动化设计](docs/design/automation.md)只保留取舍理由。这三份只链接 `scripts/wiki/` 里的文件，复制后链接不会失效。

### 规则与模板

- 接入后的文档开发流程默认以共享流程为准。旧要求不因已有或更严格就保留，接入时迁移冲突规则、原入口与读取方；必要例外在原入口说明触发条件和理由。日常技能遇到未迁移冲突时处理接入缺口，不临时叠加两套流程或静默绕过当前指令、钩子。规范、模板、示例与五项技能使用同一适配规则。
- 共享流程区分默认目录示例与项目实际登记：审查沿用匹配 `reviews` 的位置，归档使用项目选定的历史根和索引；只有 `--summary` 才向已存在的索引追加摘要。已有目录和编号可以继续使用，不据此保留旧文档流程。
- 增加供接入项目按需使用的文档审查、文档整理和知识沉淀技能，唯一正文分别在 `scripts/wiki/skills/review-docs/`、`organize-docs/` 和 `capture-knowledge/` 的 `SKILL.md` 中。完整复制 `scripts/wiki/` 时一并提供，模板和示例以短任务表导航；不新增每任务或每提交的必做步骤，不代表宿主已原生安装。
- 增加接入技能 `scripts/wiki/skills/adopt-projectwiki/SKILL.md`，用于给用户指定项目首次接入或补齐未完成的接入。首次从源仓库打开，复制完整 `scripts/wiki/` 后可从目标项目本地打开；源仓库只提供模板、工具和完整指南，写入对象是目标项目。不包含自动升级或未经授权的提交、推送、全局配置与执行套件操作，按路径读取不代表宿主已原生安装。
- 增加随完整 `scripts/wiki/` 复制的同步文档与提交技能，唯一正文在 `scripts/wiki/skills/sync-docs-and-commit/SKILL.md`，由 ProjectWiki 提供，在接入项目中使用该项目的入口、配置和 Git 工作区完成收尾。升级时保留 `skills/` 并合并 Agent 入口中的按需导航；只在用户要求同步文档并提交、收尾提交时读取，按实际影响与授权处理，不为收尾补造计划或重复进度。`AGENTS.md` 的阅读入口不代表宿主已原生发现技能，需要原生调用时另行登记和验证。
- 增加文档系统与执行套件共用开发入口的绑定约定：复用任务、执行与协调记录、待处理项、验证和归档的实际来源，按职责关联计划、任务状态与槽位；升级时同步消费者，不新增任务账或配置字段。模板提供可选绑定节，NoteBox 展示轻量来源映射；未运行套件的检查不作为执行通过证据。
- 状态页作为协调摘要时改为按需使用的短视图，只保留当前任务链接、跨模块依赖与待决事项，协调需求消失后停用。升级时优先删去重复进度、将历史流水移出当前总览，取消逐提交更新；只有现有计划和模块入口无法承担协调用途时才评估保留或模块拆分，不默认逐模块建页或为拆分增加映射配置。执行套件用于调度、恢复、并发控制、交接或验收追踪的记录按实际读取契约保留，包含必要的固定入口和已有映射；调整前同步迁移读取方并验证，不因文件名或套件目录一概删除或豁免。
- 接入时分别处理已有内容和流程规则：正文、编号与历史优先登记；默认每次执行的要求逐条核对，去掉等效重复，保留的项目流程写明触发条件和理由。普通修复在未改变文档契约、未达累计复核阈值时，可以只提交代码和测试。
- 新功能与行为变化按协作、风险、契约和交接需要决定是否补充设计或计划，轻量变化可以只写需求条目和测试。修复理由留提交信息，持续约束写设计或适合的代码注释，需要长期解释替代方案的重要选择才写 ADR。原则补充流程过重的迹象与逐提交要求的频率成本。
- 单次 `docs-not-updated` 改为 `[info]` 提示，未达累计阈值时不要求更新文档或填写 `Docs-Reviewed`；达到 `threshold` 才要求复核，达到 `block_at` 才阻断。已有正文失实时仍须当次更新。升级工具时同步更新项目的 Agent 规则，去掉每条提示都必须写 trailer 的旧要求。
- 计划和审查的状态行可以写负责人 `负责：agent:<名字>`；模板已加这一项。
- 写作规范新增：排查类指南按症状组织；跨模块契约写明提供方和消费方；术语表的写法；截图、原型和线框的引用方式，并要求用文字写出结论。
- 项目 AGENTS 模板新增：拿不准放哪里时写进 `dev/inbox/<类型>/`。项目概览模板新增可选的产品边界表。
- 计划和决策记录在标题下第一行写状态。
- 需求条目带编号、状态和验收子编号，设计、计划和测试按编号引用。
- 不能由命令证明的需求验收项可以标记为人工验证，并用 `验收核对：<编号>，agent:<名字>，YYYY-MM-DD。` 记录核对人和日期；模板、文档模型和参考项目按同一写法维护。
- 审查放在一个日期目录里，每条问题一个小节，核对、方案和签收写进问题小节。
- 知识页可以写核对行和复核期限，核对人写成 `human:` 或 `agent:`。
- 验证记录用 `verify` 生成；归档先预览再用 `--apply` 执行。
- 设计原则区分不变量、可配置的默认约定和需要人工判断的规则：不变量固定为错误，默认约定按实际结构配置；不能由工具判断的规则仍按共享流程和规范执行。已有内容优先登记格式，不为通过检查改写。
- 决策模板只保留现行约束与入口，不记录一次改动同步了哪些文件；已有决策记录移除开发流水和未解释的外部项目名称。
- 新建文档检查会拒绝影响归档链接改写的空格、`#`、`%` 和括号，提示模板占位名（`plan.md`、`decision.md`、`inbox-item.md`）及状态或版本词，并报告只差大小写的同目录冲突。暂存检查不检查归档根下的路径和不改文件名的移动，旧文件名不妨碍归档。
- 项目模板的 `docs/wiki.json` 默认在 `verify` 里登记文档检查，复制模板和 `scripts/wiki/` 后就能运行 `verify`。审查模板的状态改为默认值"执行中"。
- 项目模板和参考项目的配置给 `dev/plans`、`dev/inbox/*` 和 `dev/reviews/*` 设了目录文件数预算。
- 待处理项有了结束方式：写明去向，状态改为"已完成"，然后归档。模板、生命周期和 demo 收件箱说明已同步。
- 项目模板不再引用 ProjectWiki 自己的 `docs/`，改为指向随工具复制的 `scripts/wiki/formats.md`。
- 需求编号和审查路号的分配规则：并行分支撞号时后合并的一方改号；审查路号由负责汇总的人分配。
- 设计原则不再一概禁止日期前缀：日期只能表示不再改变的时间点，例如审查目录的开始日期。
- 状态行决策补充：已经用 frontmatter 记状态的项目可以登记字段名，工具从没有状态行的页面读这个字段，两处都写时以状态行为准并核对是否一致。新写的页面仍用状态行。
- 需求编号在一个需求范围内唯一：一个仓库里有几套各自编号的需求时，在配置里分组登记，不为全局唯一改号。
- 暂存检查的不变量改为"只读取捕获的 Git 索引，以及登记的相邻仓库在检查开始时的 HEAD 提交"，见[跨仓库链接决策](docs/decisions/cross-repo-links.md)。设计原则、自动化设计、文档模型、写作规范和接入指南同步更新；项目模板的配置默认排除 `scripts/wiki/**`。
- 设计原则：只对新文件提出的要求用登记的接入提交划出存量，不把新规则关进专门的子目录。生命周期页新增两种实际出现过的失效方式：为避开归档提醒把已实现的计划标成"当前有效"，以及新规则只在以工具命名的子目录里生效。
- 接入指南：旧仓库登记接入起点；已有 frontmatter 状态时登记字段，不在每篇里补写第二处状态；`remind` 在接入时累计的历史欠账，在接入提交里逐组核对并清零，不永久调高 `block_at`；几套需求编号冲突时分组，不关闭追踪。
- 新增 `scripts/wiki/workflow.md`：随工具复制的开发流程规则权威正文（需求到验证的顺序、决定变化时同步文档、审查分工、生命周期与归档），接入项目的 `AGENTS.md` 链接它、不再整段抄写。接入指南第 3 步新增"旧目录去向"表（`docs/systems`、`docs/architecture`、`docs/reference`、`docs/modules`、`docs/templates`、`dev/progress` 等过程目录和 Agent 操作手册的建议去向），补充停用说明写法和过渡表只做导航的约束。
- 计划的状态行新增固定写法关键词 `原因` / `Reason`：阻塞的计划写 `状态：阻塞。原因：等待 X 的接口评审。`。`check` 新增 `plan-blocked-no-reason`（阻塞但没写原因）和 `plan-status-current`（计划误用决策记录的"当前有效"状态），接入起点之前的旧文件不报；`templates/plan.md` 的状态行说明已同步。
- 新增可选配置 `size_limits`（`page_chars` 默认 100000、`line_chars` 默认 10000、`ignore` 路径模式）：非归档文档超页面上限且未登记 `max_chars` 时警告 `page-oversized`，有行超行上限时每篇警告一次 `line-oversized`；命中 `ignore` 或归档角色不报，接入起点之前的存量大文件照常报。新增 `entry-duplicate` 警告：同目录的 `AGENTS.md` 与 `CLAUDE.md` 去掉首尾空白后逐字相同、长度超过 200 字符时，提示保留一份、另一份改成 `@AGENTS.md` 导入。
- 新增 `trace-requirements-location`（警告）：`requirements.files` 匹配到的需求文件落在过程根或归档根时，提示用 `move` 搬到知识根下，因为需求在被废止前都是现行知识。新增 `trace-all-manual`（警告）：已实现或已验证、至少 2 条验收、且验收全部只有人工验证没有测试引用的需求。

### 工具

- 需求追踪取消缺少设计引用的警告；需求条目和测试可以独立完成追踪，不新增豁免字段。已有文档、计划和测试中的编号仍会检查，验收测试与证据检查继续执行。
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
- 配置里没有 `remind` 时，`remind` 和 commit-msg 钩子只给出 `remind-not-configured` 警告，退出码为 0。可以先装钩子，再写提醒配置。
- 配置顶层、`remind` 和 `remind.watch` 的未知字段报告 incomplete。例如把 `dir_budgets` 写成 `dir_budget`、把 `plan_stale_days` 写成 `plan_stale_day`，或在 watch 条目里多写 `doc`。
- 关键词集中在 `wiki.py` 的 `KEYWORDS` 表里，解析正则由它生成，测试核对它和 `formats.md` 一致。审查判定不再识别 `hold`、`weaken`、`drop`，改用 `confirmed`、`narrowed`、`rejected`。
- `check` 在大仓库上变快：链接行号原来对每个链接从文件开头重新数换行，耗时随页面长度平方增长；现在线性增长，同一篇文档的链接也只解析一次。在一个 5493 篇文档的接入项目上，`check` 从约 60 秒降到约 12 秒；另一个 1983 篇的项目从约 11 秒降到约 3.5 秒。
- 脚注定义 `[^名称]: …` 不再被当成引用式链接定义。原来脚注正文的第一个词会被当作链接目标，报出 `broken-link`；现在脚注正文里的普通链接照常检查。
- 配置新增 `repos`：登记相邻仓库后，指向它们的跨仓库相对链接会检查目标文件和锚点；仓库没检出时只警告 `repo-not-checked-out`，报告的 `coverage.repos` 写出状态。`check --require-repos` 要求登记的仓库都读得到。暂存检查读相邻仓库在检查开始时的 HEAD 提交，不读它们的工作区。
- 没初始化的子模块不再让指向它的链接报断链，改为每个子模块一条 `repo-not-checked-out` 警告，`coverage.submodules` 列出状态。
- `broken-link` 和越出项目根的 `unsupported-link` 在多写或少写一层 `../` 就能打开时，消息里写出改后的链接。提示不进基线指纹。
- 新增警告 `unregistered-markdown`：不在任何登记的根、模块、页面或入口里的 Markdown 不被检查，报告的 `coverage.unregistered_markdown` 写出数量和前 20 个路径。
- 配置新增 `status_frontmatter`：登记一个 frontmatter 字段名后，没有状态行的计划和决策记录从这个字段取状态；两处都写且类别不同时警告 `status-mismatch`，字段值无法识别时警告 `status-unknown`。
- 配置新增 `adopted_at`：登记接入时的提交后，那时已有的文件不报 `status-missing`、`plan-no-status`、`orphan-page`、`orphan-asset`、`trace-plan-scope`，不计入 `dir-budget`，旧审查目录只查问题编号重复。旧计划和待处理项的生命周期提醒合并成一条 `legacy-lifecycle`，`remind --all` 逐篇列出。链接等其余规则对旧文件照常检查。
- `requirements` 可以写成分组数组，每组有 `name`、`files`、`tests`、可选的 `id_pattern` 和 `docs`。编号只在组内查重，引用按文档所属的组解析。写成一个对象的旧配置照常运行。
- 工作区检查跳过 Git 忽略的未跟踪文件和目录，例如 Gradle 的 `build/` 和 `.gradle/`。报告的 `coverage.git_ignored` 写明是否应用了忽略规则；不在 Git 工作区里时读取全部文件，文本输出会说明这一点。
- `remind`（不带 `--staged`）在 Git 工作区里检查当前生效的钩子：pre-commit 或 commit-msg 缺失、不可执行或没有调用对应命令时，给出 `[user]` 警告 `hooks-not-installed`，写明两种装法；不是 Git 工作区、钩子目录无法按 ProjectWiki 钩子识别，或运行在钩子里（`--staged`）时不提醒。退出码仍为 0。
- `check --staged` 和 `remind --staged` 在配置文件既不在索引也不在 HEAD 里（项目还没提交接入）时，不再报 `input-unavailable`、退出码 2，改为给 `config-not-committed` 警告、`result` 为 `not_checked`、退出码 0，不拦提交；配置在 HEAD 里却从索引删除仍报 incomplete。接入脚本因此可以在同一个提交里一起提交配置和钩子。
- `remind --staged --message-file` 读到的 `Docs-Reviewed` 名字不是任何 `remind.watch` 的组名时，给出 `[agent]` 警告 `review-trailer-unknown-group` 并列出已有组名，这些名字不清零计数；逗号分隔的多个名字只对不存在的告警。
- `remind` 的观察组计数不再被接入提交清零：第一次把配置文件加入仓库的提交（以及配置的 `adopted_at`）算接入提交，它改到 `watch.docs` 不清零、接入时一次性引入的代码也不计入累计量；只有提交信息里 `Docs-Reviewed` 写了组名才清零。判断文档是否"被更新"时区分实质改动：只改 Markdown 链接目标、只改 `updated`/`created`/`date`/`status`/`phase` 等 frontmatter 字段、只改 `状态：` 行、纯重命名或移动都不算更新。`plan-stale` 和 `inbox-stale` 的天数也从最后一次实质改动算起（这里 `状态：` 行算实质），往回最多看 30 次提交。判断只看本次提交对该文件的改动行，上千文件的大提交一次 `git diff-tree` 处理完。
- `remind` 新增 `plan-idle`：状态是草案或阻塞的计划，超过 `remind.plan_idle_days`（可选配置，正整数，默认 60）天没有实质改动时提醒；接入起点之前的旧计划并入 `legacy-lifecycle` 汇总。`remind` 列出阻塞的计划时一并显示状态行里的原因。
- 新增 `move <源> <目标>` 命令：把放错位置的文档或目录搬到任意已登记的根（knowledge/process/archive）或模块文档目录下，复用 `archive` 的预览、`plan_sha256`、入链出链改写、回滚和执行后 `check`。只换目录时不做新建命名检查，改了文件名时按 `check-new` 命名规则检查。目标在归档根里时提示改用 `archive`；源是配置、基线、生成目录或历史索引时拒绝。拒绝情形分别报 `move-invalid`、`move-destination-outside`、`move-source-protected`、`move-use-archive`。
- `check --json` 的 `coverage` 新增 `requirements`：按需求分组给出需求数、验收数、被测试引用的验收数、只有人工验证的验收数、两者都没有的验收数，以及各状态的需求数（没分组时组名为 `default`）；文本输出在汇总里加一行。`verify.commands` 的条目新增可选字段 `kind`（`test`/`check`/`build`），`verify` 输出新增布尔字段 `code_tests_registered`，所运行的命令里没有任何 `kind` 为 `test` 时写明"未登记代码测试：本记录只证明所登记的检查命令，不证明代码"。
- `dir_budgets`：一个目录命中多个模式时，改为按最具体（字符串最长）的模式判断，只报一次，不再依赖配置里的模式顺序。

### 参考项目

- NoteBox 登记了 `verify` 和一份 `reconcile`（模块需求里的错误信息与 `title.py` 对账），新增带表格的 `archive/INDEX.md`，审查目录写了负责人。
- NoteBox 和项目模板的 `dir_budgets` 增加 `"dev/*": 50`，给 `dev/` 下其他子目录兜底预算；`demo/docs/wiki.json` 的 `tests` 命令加 `"kind": "test"`，让 demo 的验证记录如实标明已登记代码测试。

升级注意：配置新增的字段都是可选的，旧配置不改也能运行。升级后 `check` 可能多出一条 `unregistered-markdown` 警告，列出一直没被检查的 Markdown，复制来的 `scripts/wiki/*.md` 通常就在其中：在 `exclude` 里加 `scripts/wiki/**`，其余登记或排除。没初始化的子模块里的链接原来报 `broken-link`，现在变成警告，基线里对应的条目会出现 `baseline-stale`，重新生成基线即可。升级后第一次运行 `check` 可能多出 `orphan-page`、`orphan-asset` 警告，它们不会让检查失败；确实不需要入口的路径登记在 `orphan_ignore` 里。复制新版 `scripts/wiki/` 时，`reference.md` 和 `formats.md` 要一起复制；链接到旧 `scripts/wiki/README.md#…` 小节的文档改链到 `reference.md`。审查问题用了 `hold`、`weaken`、`drop` 判定的，改成对应的 `confirmed`、`narrowed`、`rejected`。用验收核对记录代替测试的非人工验收条目，会重新出现 `trace-no-test`：补测试，或者确认命令证明不了后加人工验证标记。顶层、`remind` 或 `remind.watch` 里有工具不认识的字段时，`check` 报告 incomplete。没有 `remind` 的仓库装上钩子后可以提交，commit-msg 只警告 `remind-not-configured`。用脚注的项目升级后，基线里由脚注产生的 `broken-link` 条目会变成 `baseline-stale`，重新生成基线即可；为了跳过构建目录而在本地改过 `DEFAULT_EXCLUDES` 的副本，可以撤掉这项改动，`exclude` 里的 `**/build/**` 等条目也可以删掉。链接指向被 Git 忽略的未跟踪文件时，升级后会报 `broken-link`：这类目标在其他克隆里本来就不存在，改成指向已跟踪的文件，或者去掉链接。复制新版 `scripts/wiki/` 时多了一份 `workflow.md`，和 README/reference/formats 一起复制，并在 `docs/wiki.json` 的 `pages` 登记 `{"path": "scripts/wiki/workflow.md", "role": "reference"}` 避免 `orphan-page`；`AGENTS.md` 里原本整段抄写的开发流程规则可改为链接它。之前为绕开"配置未提交时暂存检查退出码 2"而自己改写的钩子脚本可以去掉绕开逻辑。没装钩子的项目开工跑 `remind` 会看到 `hooks-not-installed`，按提示装一次。升级后 `check` 会对未登记 `max_chars` 的超大页面（默认超过 10 万字符）和超长行（默认超过 1 万字符）新增 `page-oversized`、`line-oversized` 警告，对状态是"阻塞"却没写 `原因：` 的计划报 `plan-blocked-no-reason`、对状态是"当前有效"的计划报 `plan-status-current`、对落在过程或归档根下的需求文件报 `trace-requirements-location`、对全人工验证的已实现/已验证需求报 `trace-all-manual`；没配 `adopted_at` 的旧仓库这些会对全部现行文件生效，可先配置 `adopted_at` 让接入前的文件豁免，再逐步清理。已做过接入提交的项目升级后 `remind` 的观察组计数会从"0 次"变为显示接入前累计的真实欠账，可能新出现 `docs-review-due`：逐组核对后用 `Docs-Reviewed: <组名> <理由>` 清零或更新文档。想让验证记录如实反映代码测试跑过，在 `verify.commands` 里给测试命令加 `"kind": "test"`。
