# 标题校验设计

对应需求：NB-01。

范围：notes 模块。状态：当前有效。

`normalize_title` 位于 [src/title.py](../src/title.py)。函数先调用 `strip()`，再校验非空与 60 码点上限。它没有文件、网络或全局状态。

函数是当前唯一公开入口。调用方捕获 `ValueError` 后负责提示用户，不应在外部重新实现另一套截断或计数。

采用码点计数的原因与限制见 [字符计数决策](decisions/unicode-length.md)。需求见 [模块需求](requirements.md)，验证见 [测试](../tests/test_title.py)。
