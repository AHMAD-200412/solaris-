from django import template

register = template.Library()

@register.filter
def smart_money(value):
    value = float(value)

    if value >= 1_000_000:
        millions = value / 1_000_000
        if millions.is_integer():
            return f"{int(millions)} مليون"
        return f"{millions:.1f} مليون"

    elif value >= 1_000:
        thousands = value / 1_000
        if thousands.is_integer():
            return f"{int(thousands)} ألف"
        return f"{thousands:.0f} ألف"

    else:
        return f"{int(value)} دينار"


@register.filter
def full_money(value):
    try:
        value = int(float(value))
    except (ValueError, TypeError):
        return value

    millions = value // 1_000_000
    remainder = value % 1_000_000

    thousands = remainder // 1_000
    dinars = remainder % 1_000

    parts = []

    if millions:
        parts.append(f"{millions} مليون")

    if thousands:
        parts.append(f"{thousands} ألف")

    if dinars:
        parts.append(f"{dinars} دينار")

    if not parts:
        return "0 دينار"

    return " و".join(parts)