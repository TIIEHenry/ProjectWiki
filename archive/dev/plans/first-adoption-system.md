# 首版接入系统

状态：已完成。范围：ProjectWiki 主文档、工具、模板和参考项目。完成日期：2026-10-28。原位置：`dev/plans/first-adoption-system.md`。

## 目标与依据

实现[项目需求](../../../docs/requirements/projectwiki.md)，让其他项目的 Agent 能阅读本仓库后建立同样的文档体系。目录与行为遵守[设计原则](../../../docs/principles/document-system.md)。

## 步骤

- [x] 整理两个现有项目的文档与自动化经验。
- [x] 确认根 docs/dev/archive、当前知识原位维护和关键规则内联。
- [x] 建立可运行参考项目及可复制模板。
- [x] 完成 ProjectWiki 自身的介绍、设计和接入文档。
- [x] 完成只读检查、新建历史检查和整页归档预览。
- [x] 验证暂存快照、路径、锚点、模块和归档冲突的反例。
- [x] 在临时目录复制模板，验证实际接入。
- [x] 核对人类可读性、命令、引用与最终结果。

## 验收

主项目、demo 和复制后的模板通过各自的文档检查；参考代码测试通过；工具反例测试能够发现错误；接入说明只描述已实现能力。原参考仓库不作修改。

## 协作范围

主持负责根入口、docs、dev 和归档说明；自动化席位负责 scripts 与 tests；Sol 负责 demo 与 templates。外部讨论席位提供只读评审，原 tmp 草案保留。

## 验证记录

检查器版本：`0.1.0`。验证在 ProjectWiki 根目录运行，测试设置 `PYTHONDONTWRITEBYTECODE=1`；Python 命令使用 `-B` 避免产生缓存。

| 验证 | 实际结果 |
|---|---|
| `python3 -B -m unittest discover -s tests -v` | 28 项通过，覆盖暂存快照、角色降级、越根链接、文件与目录区别、冲突和零写入预览 |
| `python3 -B -m unittest discover -s demo/notes/tests -v` | 5 项通过；此后仅修改示例文档，源码未变 |
| `python3 -B scripts/wiki/wiki.py check --root demo --json` | 19 篇，无错误、无警告 |
| `python3 -B scripts/wiki/wiki.py index --root demo --check` | 退出码 0，生成目录一致 |
| 临时目录复制项目模板与工具 | 7 篇，无错误、无警告；新建路径检查通过 |
| 再复制模块模板并登记模块与工具入口 | 10 篇，无错误、无警告 |
| 临时项目的普通 `rg` 与显式 `rg --no-ignore ... archive/` | 普通搜索仅命中当前文档，显式搜索能够命中历史 |
| 本计划的 `archive` 预览 | 原文件名保持不变，目标无冲突，列出所属导航与出链的定向修改，未写入文件 |
| `doctor --root .` | 精确归档忽略规则存在；hook/build 为 unknown，保留 1 条警告 |

主项目的最终文档检查在本计划及讨论记录归档后执行，结果保存在[最终文档检查报告](first-adoption-system/final-document-checks.json)。归档移动由主持按预览手工完成，不能记为工具已经支持自动写入。

被测代码与配置的原文保存在[验证输入包](first-adoption-system/verification-inputs.zip)，对应[SHA-256 清单](first-adoption-system/verification-inputs.json)。源码和配置快照不包括之后写入的本记录。当前仓库未初始化 Git；暂存检查反例均在测试创建的临时 Git 仓库中运行，不代表本仓库已经启用提交钩子。

## 后续事项

自动归档写入见[待处理请求](../../../dev/inbox/request/archive-apply.md)。旧布局的历史对应、复杂流程状态校验、任意宿主接入推断与历史告警基线管理保持待评估状态，第一版不得把它们报告为已支持。真实外部项目接入与预算校准见[路线图](../../../dev/roadmap.md)。
