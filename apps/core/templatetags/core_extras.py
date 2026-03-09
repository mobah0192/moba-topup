from django import template
from apps.core.utils.helpers import format_rupiah

register = template.Library()

@register.filter
def rupiah(value):
    """Template filter untuk format Rupiah"""
    return format_rupiah(value)

@register.filter
def status_badge(value):
    """Mengembalikan HTML badge berdasarkan status"""
    badges = {
        'pending': 'warning',
        'paid': 'info',
        'processing': 'primary',
        'completed': 'success',
        'failed': 'danger',
        'expired': 'secondary',
    }
    color = badges.get(value, 'secondary')
    return f'<span class="badge bg-{color}">{value}</span>'