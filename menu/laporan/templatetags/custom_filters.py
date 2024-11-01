# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def rupiah(value):
    try:
        # Pastikan nilai adalah integer atau konversi float ke integer
        value = int(value)
        formatted_value = f"{value:,}".replace(",", ".")
        return formatted_value
    except (ValueError, TypeError):
        return value  # Jika ada error, tampilkan nilai aslinya
