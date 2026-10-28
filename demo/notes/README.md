# 标题模块

本模块去除标题首尾空白，校验长度，并返回可供调用方保存的标题。它不保存数据。

| 什么时候读 | 正文 |
|---|---|
| 修改行为、边界或错误处理 | [需求](docs/requirements.md) |
| 修改职责或字符计数方式 | [设计](docs/design.md) |
| 确认当前实现 | [normalize_title](src/title.py) |
| 复现边界或验证修改 | [测试](tests/test_title.py) |

全局约束见 [产品与设计原则](../docs/principles/product.md)。标题超限时必须报错，不允许静默截断。
