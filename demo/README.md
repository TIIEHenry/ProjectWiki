# NoteBox 示例项目

NoteBox 为笔记提供标题校验。示例包含可运行的小模块，以及需求、原则、设计、开发记录和归档之间的关系。它用于演示文档系统，未提供持久化或网络服务。

- 查当前知识：从 [知识入口](docs/INDEX.md) 开始。
- 修改标题规则：从 [标题模块](notes/README.md) 开始。
- 接续工作：从 [开发入口](dev/INDEX.md) 开始。
- 接入其他项目时，先阅读 ProjectWiki 的接入指南；本示例目录可以独立复制。

在 `demo/` 下运行：

```sh
python3 -m unittest discover -s notes/tests -v
```

示例仓库保持 `docs/`、`dev/`、`archive/` 并列。`notes/docs/` 保存模块知识。已结束的计划在 `archive/dev/plans/`；当前标题规则原位维护，修订历史交给 Git。
