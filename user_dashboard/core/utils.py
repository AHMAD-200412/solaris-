from decimal import Decimal


def format_iqd(amount):
    """
    يحول الأرقام إلى صيغة عراقية سهلة.

    9500000 -> 9.5 مليون دينار
    9000000 -> 9 مليون دينار
    650000  -> 650 ألف دينار
    25000   -> 25 ألف دينار
    950     -> 950 دينار
    """

    if amount is None:
        return "0 دينار"

    amount = Decimal(amount)

    if amount >= 1_000_000:
        value = amount / Decimal("1000000")

        if value == int(value):
            value = int(value)
        else:
            value = round(float(value), 1)

        return f"{value} مليون دينار"

    elif amount >= 1000:
        value = amount / Decimal("1000")

        if value == int(value):
            value = int(value)
        else:
            value = round(float(value), 1)

        return f"{value} ألف دينار"

    else:
        return f"{int(amount)} دينار"