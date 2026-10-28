# ProjectWiki 开发约定

本仓库提供可复用的项目文档系统。修改应同时考虑 ProjectWiki 自身、可复制模板和 `demo/` 的实际接入体验。

## 必须直接遵守的规则

- `docs/` 保存当前需求、原则、设计和开发规范；`dev/` 组织开发流程、计划与执行记录；根 `archive/` 保存历史。
- `module-structure.md`、需求和原则等持续有效的知识页原位修订，旧版交给 Git。任务完成不等于需求失效。
- 整页归档默认移动到 `archive/<原相对路径>`，保持文件名。目标存在时报告冲突，不覆盖历史。新建文档前检查 `archive/<原相对路径>`，区分恢复、重复创建和新主题复用路径，不因标准文件名重复而永久禁止创建。
- 日常检索优先当前文档。需要历史背景时可按任务自行搜索 `archive/`，无需额外确认。归档是信息分类，不是访问权限。
- 稳定知识须供人直接阅读。用具体对象、动作、条件和结果表达；解释必要术语；删除 AI 套话、翻译腔、内部缩写和开发流水。摘要说明内容，阅读条件写在导航链接旁。
- 关键规则直接写在本文件；链接补充详细规范。更改规则时同步核对本文件与权威正文，不能只改其中一处。
- 采用、替代或废止 ADR，或者设计、接口行为发生变化时，在同一次改动中更新仍描述旧结论的需求、原则、设计、模块入口和本文件条目。按链接和关键词两种方式查找受影响的文档。推翻已采用 ADR 的设计变更要补新 ADR，不能让设计页与 ADR 互相矛盾。详见[开发流程](dev/workflow.md#决定或设计变化时同步文档)。
- 开始任务时运行 `python3 scripts/wiki/wiki.py remind --root .`；没有 Git 仓库时它会报告 incomplete，表示提醒不可用，不能当作已通过。提交时 Git 钩子也会输出提醒。看到 `[agent]` 提醒，就更新对应文档，或者在提交信息最后一段写 `Docs-Reviewed: <名称> <理由>`；看到 `[user]` 提醒，除非用户已经要求这项修改，否则先向用户确认，并在总结里报告。不得用 `--no-verify` 跳过钩子。
- 普通修复可以复用现有任务或提交记录。涉及产品边界、接口、数据兼容或重要取舍时，先核对相关需求和设计，按影响补充计划或决策。
- 保留其他协作者的文件与未提交改动。只编辑分配给自己的范围，不为完成本次工作清理无关内容。
- 检查结果必须说明实际输入与范围。未检查、无法验证或仅通过部分规则，不得写成全部通过。归档工具首版只提供预览。

## 按任务读取

| 情况 | 下一步 |
|---|---|
| 建立或调整文档体系 | [设计原则](docs/principles/document-system.md)、[接入指南](docs/guides/adoption.md) |
| 写稳定知识 | [写作规范](docs/standards/writing.md) |
| 处理计划、路线图或 ADR | [开发流程](dev/workflow.md) |
| 修改检查器 | [自动化设计](docs/design/automation.md)、`scripts/wiki/`、`tests/` |
| 移动或归档文档 | [生命周期与归档](docs/design/lifecycle.md) |
| 接续已有任务 | [开发入口](dev/INDEX.md)及对应计划 |

开始修改前，应明确目标、适用约束、实现位置和验证方法。发现未知项再定向补读；无需为每项任务阅读全部文档。

## 验证

```bash
python3 scripts/wiki/wiki.py check --root .
python3 scripts/wiki/wiki.py check --root demo
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s demo/notes/tests -v
```

命令和测试影响范围见[开发规范](docs/standards/development.md)。在本机执行时继续遵守用户已有的命令执行约定。
