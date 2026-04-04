from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def currency_eur(value):
    if value in (None, ""):
        return ""

    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value

    if amount == amount.to_integral():
        formatted = f"{amount:,.0f}"
    else:
        formatted = f"{amount:,.2f}"

    return f"{formatted.replace(',', ' ')} EUR"
