# 标题校验需求

范围：notes 模块。状态：当前有效。

每条需求以编号开头，下面第一行是状态，验收条件逐条带子编号。测试在说明文字里写验收编号，设计页用"对应需求："引用。

### NB-01 保存前校验标题

状态：已验证。

输入是 Python 字符串，输出是去除首尾空白后的字符串。

- NB-01.1 去除首尾空白后，其余内容保持不变，包括内部换行。
- NB-01.2 空输入或全空白输入抛出 `ValueError("title is empty")`。
- NB-01.3 恰好 60 个 Unicode 码点时接受。
- NB-01.4 超过 60 个码点时抛出 `ValueError("title is too long")`，不截断。

证据：[验收测试](../tests/test_title.py)，运行 `python3 -m unittest discover -s notes/tests -v`。

### NB-02 标题只允许一行

状态：提出。

是否拒绝内部换行还没有决定，评估工作见[路线图](../../dev/roadmap.md)。在本条变为已接受之前，NB-01.1 仍然有效，内部换行保留。

全局原则见 [P-INPUT](../../docs/principles/product.md#p-input保留输入意图)。
