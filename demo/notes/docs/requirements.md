# 标题校验需求

范围：notes 模块。状态：当前有效。

输入是 Python 字符串；输出是去除首尾空白后的字符串。归一化后长度为 1–60 个 Unicode 码点，满足条件时保持其余内容不变。

- 空输入或全空白输入：抛出 `ValueError("title is empty")`。
- 超过 60 个码点：抛出 `ValueError("title is too long")`。
- 恰好 60 个码点：接受。
- 当前内部换行保留，不作单行限制。是否增加该限制仍待评估，工作入口见 [路线图](../../dev/roadmap.md)；当前契约尚未改变。

全局原则见 [P-INPUT](../../docs/principles/product.md#p-input保留输入意图)。验收用例见 [测试](../tests/test_title.py)。
