# Wiki 检查工具

这个脚本检查已登记的文档入口、引用、页面长度和文档身份，输出可定位的问题。它不判断文章里的设计或业务结论是否正确。

需要 Python 3.10 或更新版本，不需要安装第三方库。检查暂存内容时还需要 Git。

## 常用命令

在项目根目录运行：

```bash
python3 scripts/wiki/wiki.py check --root .
python3 scripts/wiki/wiki.py check --root . --json
python3 scripts/wiki/wiki.py check --root . --staged
python3 scripts/wiki/wiki.py check-new docs/design/new-topic.md --root .
python3 scripts/wiki/wiki.py archive dev/plans/finished-work.md --root .
python3 scripts/wiki/wiki.py index --root .
python3 scripts/wiki/wiki.py doctor --root .
python3 scripts/wiki/wiki.py remind --root .
python3 scripts/wiki/wiki.py remind --root . --staged --message-file .git/COMMIT_EDITMSG
```

`--root` 选择项目根目录，配置默认是该目录下的 `docs/wiki.json`。可以用 `--config` 指定另一个相对配置路径。配置中的所有路径都相对于项目根目录。

`check`、`check-new`、`archive`、`doctor` 支持 `--json`。`index` 始终向标准输出打印 JSON，不写文件。若配置声明了 `generated_index`，`index --check` 会比较该文件与当前目录结果；文件不存在或内容不同就失败。相同输入产生相同目录，不加入运行日期。

## 配置

最小配置包含 `version`、`roots` 和 `entrypoints`：

```json
{
  "version": 1,
  "project_name": "Example",
  "roots": [
    {"path": "docs", "role": "knowledge"},
    {"path": "dev", "role": "process"},
    {"path": "archive", "role": "archive"}
  ],
  "entrypoints": ["README.md", "AGENTS.md", "docs/INDEX.md", "dev/INDEX.md"],
  "modules": [
    {"name": "notes", "path": "notes", "entry": "notes/README.md", "docs": "notes/docs"}
  ],
  "pages": [
    {"path": "AGENTS.md", "role": "entry", "max_chars": 8000}
  ],
  "exclude": ["tmp/**", "**/__pycache__/**"]
}
```

`modules`、`pages` 和 `exclude` 可以省略。示例中的 8000 是演示值，应根据实际任务调整。

- `roots` 登记知识、过程和历史目录。历史目录可以在第一次归档时创建，其余登记目录和必需入口必须存在。
- `modules` 登记模块路径和入口；小模块可以只有 README，省略 `docs` 字段。已有模块文档目录时再登记 `docs`。工具会发现未登记且未明确排除的 `docs/` 目录，独立前端或其他语言模块也需要登记。
- `pages` 为特定文件补充角色和字符预算。可选 `id` 与 `scope` 用于检查当前文档的身份冲突。省略 scope 时，模块内按模块归属，其余按项目归属；历史版本可以保留相同逻辑 ID。历史豁免按已登记历史根的路径判断，当前文件不能只把页面角色写成 `archive` 来降低检查级别。
- `exclude` 控制检查范围；它与给日常检索使用的 `.ignore` 是两套不同用途的规则。不要用检查排除规则把整个历史目录排除，否则无法核对历史链接。

文档正文不要求 frontmatter。当前版本不解析正文的流程状态，也不禁止操作指南使用复选框。

接入旧仓库时，可把仍在使用的嵌套历史目录继续登记为 `archive` 角色；它们仍参与分类、历史检查和忽略规则提示。新归档默认写入已登记的根 `archive/`；如果主目录使用别的名称，用可选 `archive_root` 明确指定。没有根 `archive/` 且只登记一个历史根时，使用该根。多个其他历史根并存时必须明确主目标，工具不猜测。

新建历史匹配只检查主目标下的完整原路径，不推断旧布局的对应关系。存在其他历史根时，`check-new` 及暂存新增页检查会明确提示仍需查询这些目录。

## 检查内容和边界

当前支持：

- 必需入口、模块入口、登记目录与未登记的 `docs/` 目录。
- 常见内联链接、引用式链接和图片路径。相对路径只按当前文档位置解析，不回退到仓库根目录。
- 路径大小写、ATX 标题锚点、重复标题后缀、显式 HTML `id` 或 `name` 锚点。
- `AGENTS.md`、`CLAUDE.md` 中独立一行的 `@相对路径` 导入。其他宿主语法不在覆盖范围内。
- 页面总字符数，包括长行、表格和代码块。
- 同一作用域下重复的当前文档 ID。

代码块和行内代码中的链接示例不会被当成实际引用。源码和测试引用检查路径存在性；当前版本不核对源码符号。Markdown 锚点采用工具中固定的标题规则，并有重复标题、中文标题和显式锚点测试；不承诺支持所有渲染器扩展。

当前文档的断链、缺锚点、超预算和身份冲突会失败。相对本地链接逃出所选项目根时，当前文档报错，历史文档告警。本机绝对路径提示可移植性问题；必需导入无法验证时会失败。历史文档中的断链作为告警保留，因为旧源码或旧契约可能已不在当前版本中。

工具不检查外部网址是否可访问，不判断引用的业务含义，不验证任意执行脚本或业务契约，不把通过形式检查描述为知识完全正确。

## 暂存检查

`check --staged` 先读取 Git 索引中的路径、文件模式和对象 ID，再按捕获的对象 ID 读取配置、正文及链接目标。工作区里的未暂存修复或新增文件不会参与这次检查，随后发生的索引变化也不会替换已经捕获的输入。

工具同时捕获 HEAD 作为新增路径比较基线。没有首个提交时，基线为空，报告写明 `unborn`。对这次索引中新出现的文档，会在同一索引快照中查找 `archive/<完整原路径>`；历史命中保留为提示，不因同名阻止恢复或新建。比较的是路径新增，不推断文本主题是否相同，也不把重命名自动视为新的知识身份。

没有 Git 仓库、存在未合并索引项、配置没有暂存或必需输入无法读取时，命令返回 `incomplete` 和非零退出码。它不会退回工作区继续检查。子模块内部文档或其他不支持的文件模式也不会冒充已经验证。

报告包含输入快照、工具版本、配置哈希、覆盖目录和未检查事项。暂存快照使用索引清单的 SHA-256 标识；这不是 Git commit 或 tree ID。工作区检查标明 `working-tree`，用于编辑反馈，不声称工作区是原子快照。

## 新建和归档

`check-new` 检查当前目标是否已存在，并查找 `archive/<完整原路径>` 上的文件。对应父目录存在不算同名文档。历史同名作为提示，供创建者判断恢复、延续还是新主题；不会仅因历史里出现过标准文档名就永久禁用该名称。

`archive` 只预览一份完整 Markdown 文档：保留原文件名与目录结构，列出目标、源内容哈希，以及受影响入链和出链的机械改写候选。目标已存在时失败，即使字节相同也不自动认定为已完成。它不决定该主题是否退役，不新增跳转页，不改链接，不搬文件，也没有 `--apply`。

历史证据与当前导航可能需要不同的链接处理。预览里的路径变更只是候选，需要结合引用用途判断。原出链目标不存在或无法定位时，只报告警告，不提供一个看似可修复的新路径。切出活文件中的历史片段、并发写入恢复和自动归档暂不实现。

`index` 输出包含当前和历史页的全量机器目录，每条记录标注 `role`。生成当前知识导航或默认检索集合时，调用方应过滤历史角色。`check-new`、`archive`、`index`、`doctor` 使用工作区；`check --staged` 和 `remind --staged` 使用暂存快照，输出会明确标识这一区别。

`doctor` 检查配置、明确的根历史忽略规则，以及当前 Git 钩子目录中的 ProjectWiki 钩子；其他钩子管理器和构建任务报告为 `unknown`。普通 `rg` 可以遵守 `.ignore`；任意 `grep`、`git grep` 或显式文件读取不受这项规则保证。这里的忽略是默认降噪，不是访问限制。

## 提交时的文档提醒

`remind` 提醒开发者或 Agent 在代码变化后核对文档。它不依赖任何 Agent 宿主：数据只来自 Git 历史、暂存区和提交信息，由 Git 钩子触发，所以无论用 Kiro、Claude Code、Codex、Cursor 还是手工 `git commit`，提交时都会看到同样的提醒。

在配置中加入 `remind`：

```json
"remind": {
  "watch": [
    {"name": "notes", "code": ["notes/src/*"], "docs": ["notes/docs/*", "notes/README.md"]}
  ],
  "threshold": {"commits": 10, "lines": 300},
  "block_at": {"commits": 30},
  "ask_user": ["docs/requirements.md", "docs/principles/*", "notes/docs/decisions/*"]
}
```

- `watch`：一组代码路径和对应文档。模式用 `fnmatch` 语法，`*` 可以跨目录。
- `threshold`：从上次更新这些文档以来，累计提交次数或改动行数达到任一值时提醒。
- `block_at`：可选。累计量达到这个值后，新的提交如果继续改代码、又没有更新或复核文档，就会失败。不配置时永远只提醒。
- `ask_user`：改动这些文件时，提醒 Agent 先向用户确认，除非用户已经要求这项修改。
- `decisions`：可选，决策记录的位置，默认是 `docs/decisions/*` 与 `*/docs/decisions/*`。

计数的起点是最近一次满足下列任一条件的提交：改了该组文档，或者提交信息带有 `Docs-Reviewed: <名称> <理由>` 这一行（Git trailer，写在提交信息最后一段）。确实复核过、文档不用改时，用这一行清零。没有写理由的 trailer 不清零。多个名称可用逗号分隔。

运行方式：

| 命令 | 用途 | 退出码 |
|---|---|---|
| `remind` | 会话开始时汇总各组累计量 | 只提醒，始终为 0；没有 Git 或配置时为 2 |
| `remind --staged --message-file <文件>` | 提交时检查暂存的改动和待提交的信息 | 超过 `block_at` 且本次继续改代码未复核时为 1，否则为 0 |

提交时会报告：

- `docs-not-updated`：本次改了代码，对应文档没改，也没有复核 trailer。
- `docs-review-due` / `docs-review-overdue`：累计量达到提醒值或拦截值。
- `decision-sync`：本次改了决策记录，列出链接到它、但本次没有改动的现行文档。没有链接、直接复述结论的文档列不出来，仍需按关键词搜索。
- `ask-user`：本次改了 `ask_user` 中的文件。

每条提醒以 `[agent]` 或 `[user]` 开头：前者由 Agent 自己处理，后者需要告诉用户。工具不判断文档内容是否与代码一致。

### 安装 Git 钩子

仓库附带两个 POSIX shell 钩子：`hooks/pre-commit` 运行 `check --staged`，`hooks/commit-msg` 运行 `remind --staged`。项目没有其他钩子时，每个 clone 执行一次：

```bash
git config core.hooksPath scripts/wiki/hooks
```

已经使用 husky、pre-commit 等钩子工具时，不要覆盖它们的配置，把下面两条命令加进现有的 pre-commit 与 commit-msg 钩子：

```bash
python3 scripts/wiki/wiki.py check --staged --root .
python3 scripts/wiki/wiki.py remind --staged --message-file "$1" --root .
```

钩子默认把仓库顶层作为项目根。项目根是子目录时设置 `WIKI_ROOT`；Python 不叫 `python3` 时设置 `PYTHON`。`doctor` 会检查当前生效的钩子目录里这两个钩子是否存在、可执行并调用了对应命令。它检查不了其他钩子管理器，也无法阻止 `git commit --no-verify`，所以 Agent 规则里要写明不要跳过钩子。

## 退出码和测试

- `0`：所执行的检查通过，可能带告警。
- `1`：检查发现确定错误。
- `2`：输入、配置或命令无法完成验证。

运行行为测试：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

测试在临时目录建立示例项目和 Git 索引，覆盖工作区已修复但暂存仍错误、配置或目标未暂存、索引变化、合并冲突、路径与锚点、新建历史提示、归档冲突和预览零写入。测试不初始化或提交当前仓库。
