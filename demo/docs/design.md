# 项目设计

对应需求：NB-01。

范围：NoteBox。状态：当前有效。

标题校验由 [notes 模块](../notes/README.md) 提供。调用方传入字符串，模块返回去除首尾空白后的标题，或抛出 `ValueError`。调用方负责将错误呈现给用户。

当前没有跨模块调用方。将来增加存储模块时，应在此登记消费方，并让新模块入口指向标题契约；不能复制一份标题规则分别维护。

实现、边界条件和测试入口见 [模块设计](../notes/docs/design.md)。关于字符计数的取舍见 [Unicode 计数决策](../notes/docs/decisions/unicode-length.md)。
