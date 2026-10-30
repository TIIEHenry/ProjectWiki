# ProjectWiki 开发约定

本仓库是文档系统本身：规范在 `docs/`，模板在 `templates/`，检查工具在 `scripts/wiki/`，工具测试在 `tests/`。接入效果由 `demo/`（NoteBox 参考项目）演示和验证。根目录不按接入项目运转，没有 `dev/` 和 `archive/`，不建计划、路线图和归档。

## 必须直接遵守的规则

- 改的是系统本身。规则、模板、工具和 demo 必须一致：改一条规则时，在同一次改动中更新规范正文、`templates/` 里对应的模板和 `demo/` 里对应的示例。
- 规范正文写给接入项目的人和 Agent 看。用具体对象、动作、条件和结果表达，解释必要术语，删除 AI 套话、翻译腔和内部缩写。不在规范里写本仓库的开发过程。
- 同一条规则只在一处写正文，其他地方链接过去。工具的命令写在 `scripts/wiki/README.md`，配置和规则写在 `scripts/wiki/reference.md`，工具读取的固定写法（状态行、核对行、需求条目、审查问题、待处理项、编号分配）写在 `scripts/wiki/formats.md`。这三份随工具复制到接入项目，只能链接 `scripts/wiki/` 里的文件；`docs/` 讲理由时链接它们，不重写格式。
- 新建文档的路径不得含空格、`#`、`%` 或括号；命名细则见[文档模型](docs/design/document-model.md#文件命名)。
- 系统行为变化时，在同一次改动中更新 `docs/requirements/projectwiki.md` 里对应的需求条目。测试在说明文字里写验收编号。
- 推翻 `docs/decisions/` 里已有的设计取舍时，新增或改写对应的决策记录，并同步仍描述旧结论的规范正文。普通修改不写决策记录。
- 没做完的事写进 `TODO.md`，做完就删掉那一行。对接入项目有影响的变化写进 `CHANGELOG.md`。
- `tmp/` 是讨论草稿，不属于规范，不要从规范链接到它。
- 检查结果必须说明实际输入与范围。未检查、无法验证或只通过部分规则，不得写成全部通过。需要记录验证结果时用 `verify` 的输出，不手写命令结果和哈希。
- 保留其他协作者的未提交改动，不为完成本次工作清理无关内容。
- 提交时 Git 钩子会运行检查和文档提醒。看到 `[agent]` 提醒就更新对应文档，或者在提交信息最后一段写 `Docs-Reviewed: <名称> <理由>`；看到 `[user]` 提醒先向用户确认。不得用 `--no-verify` 跳过钩子。

## 按任务读取

| 情况 | 下一步 |
|---|---|
| 改文档系统的规则 | [设计原则](docs/principles/document-system.md)、[文档模型](docs/design/document-model.md)、[生命周期与归档](docs/design/lifecycle.md) |
| 改计划、决策、审查的流程 | [开发流程](docs/guides/workflow.md) |
| 写或改规范正文 | [写作规范](docs/standards/writing.md) |
| 改检查工具 | [工具入口](scripts/wiki/README.md)、[自动化设计](docs/design/automation.md)、`tests/`；规则和字段按名称在[配置与规则](scripts/wiki/reference.md)里搜索，不整篇读 |
| 改状态行、需求条目、审查问题等固定写法 | [工具读取的写法](scripts/wiki/formats.md)，同时改 `wiki.py` 的 `KEYWORDS` 和取值表 |
| 改模板或接入步骤 | [模板说明](templates/README.md)、[接入指南](docs/guides/adoption.md) |
| 改参考项目 | [NoteBox](demo/README.md) |
| 找还没做的事 | [待办](TODO.md) |

开始修改前，明确目标、适用约束、要改的位置和验证方法。发现未知项再定向补读，不必每次读全部文档。

## 验证

```bash
python3 scripts/wiki/wiki.py verify --root .
```

它依次运行 `docs/wiki.json` 里登记的工具测试、demo 测试、本仓库规范文档的 `check`、demo 和项目模板的 `check`，以及 demo 生成目录的 `index --check`。只需要其中几项时写名称，例如 `verify tests check`。根目录的 `docs/wiki.json` 只用来检查本仓库规范文档的链接和规则名对账，不代表本仓库是接入项目。开发规范见[开发规范](docs/standards/development.md)。
