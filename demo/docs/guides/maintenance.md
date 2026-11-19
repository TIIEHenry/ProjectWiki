# 标题校验失败的处理

核对：agent:kiro，2026-10-28；agent:sol，2026-11-02；agent:opus，2026-11-06。复核期限：2027-04-28。

范围：标题模块。状态：当前有效。

## 标题看起来不空，但返回空标题错误

先检查输入是否只有空格、制表符或换行：`repr(value)` 只显示空白字符，并且 `value.strip() == ""`，就是这个原因。模块在校验前调用 `str.strip()`，见[实现](../../notes/src/title.py)。空标题必须报错是[需求 NB-01](../../notes/docs/requirements.md#nb-01-保存前校验标题) 的规定，不要通过放宽这条规则绕过问题。已知限制：`str.strip()` 不去除零宽空格（U+200B），只含零宽空格的标题会通过校验，见[输入边界审查 r01-1](../../dev/reviews/2026-10-28-title-input/r01-input-boundary.md#r01-1-只含零宽空格的标题会通过校验)。

## 屏幕上少于 60 个字符，仍然超过上限

显示的字符数和码点数可能不同。先保留原输入，对实际值运行 `print(len(value.strip()), [f"U+{ord(c):04X}" for c in value.strip()])`，按码点数判断，不凭屏幕显示。`repr(value)` 能显示制表符、换行和零宽字符（如 `\u200d`），显示不出组合符号，所以要看逐个码点。在 `demo/` 运行下面的样例，可以核对组合字符和 emoji 的计数结果：

```bash
python3 - <<'PYTHON'
import sys
sys.path.insert(0, "notes/src")
from title import normalize_title

for unit in ("e\u0301", "\U0001F469\u200d\U0001F4BB"):
    print(repr(unit), [f"U+{ord(c):04X}" for c in unit])
    for count in (60 // len(unit), 60 // len(unit) + 1):
        value = "  " + unit * count + "  "
        title = value.strip()
        try:
            result = normalize_title(value)
            assert result == title
            outcome = "accepted"
        except ValueError as error:
            outcome = str(error)
        print(len(title), outcome)
PYTHON
```

预期：`e\u0301` 是两个码点，长度 60 时接受、62 时返回 `title is too long`；`👩‍💻` 是三个码点，长度 60 时接受、63 时返回同一错误。实际输入去掉首尾空白后的码点数超过 60，就是这个原因；码点数没有超限仍然报错时，继续查调用方传入的值和异常来源。

依据：[normalize_title](../../notes/src/title.py) 先 `strip()` 再 `len()`；[验收测试](../../notes/tests/test_title.py)覆盖普通字符的边界和超限用例，组合字符和 emoji 只有上面的诊断样例，没有进测试。阈值 60 和码点计数是[模块需求 NB-01](../../notes/docs/requirements.md#nb-01-保存前校验标题) 的契约，为什么按码点计数见[计数决策](../../notes/docs/decisions/unicode-length.md)。

遇到别的“显示效果与校验结果不符”的问题，可以按同样顺序排查：先按契约确认预处理和计量单位，再看实际输入，围绕阈值构造边界用例。这个顺序是从本例机制推断的，没有在其他接口上验证；按字节或字素（接近用户感知字符的文本单位）计量的接口，`len()` 的结果不适用。按显示效果截断违反[保留输入意图](../principles/product.md#p-input保留输入意图)；在调用方另算一套长度违反[标题校验设计](../../notes/docs/design.md)和[计数决策](../../notes/docs/decisions/unicode-length.md)中调用方沿用同一计数规则的要求。是否改为按字素计数，见待分诊的[组合字符计数疑问](../../dev/inbox/bug/combining-character-count.md)。

## 验证修复

从 `demo/` 运行模块测试，命令见 [开发规范](../standards/development.md)。新增能复现实际问题的用例，并记录验证对象与结果。
