# 标题校验失败的处理

范围：标题模块。状态：当前有效。

## 标题看起来不空，但返回空标题错误

先检查输入是否只有空格、制表符或换行。模块在校验前调用 `str.strip()`。对照 [需求](../../notes/docs/requirements.md) 与 [实现](../../notes/src/title.py)，不要通过放宽空标题规则绕过问题。

## 屏幕上少于 60 个字符，仍然超过上限

当前按 Unicode 码点计数，组合字符或 emoji 可能占多个码点。见 [计数决策](../../notes/docs/decisions/unicode-length.md)。如需改变规则，先明确兼容性与范围。

## 验证修复

从 `demo/` 运行模块测试，命令见 [开发规范](../standards/development.md)。新增能复现实际问题的用例，并记录验证对象与结果。
