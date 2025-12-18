from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def currency_tzs(value):
    """
    Format value as Tanzania Shillings
    Usage: {{ amount|currency_tzs }}
    """
    if value is None:
        return "TZS 0.00"
    
    try:
        # Handle different input types
        if isinstance(value, str):
            # Remove any non-numeric characters except decimal point and minus
            import re
            cleaned_value = re.sub(r'[^\d.-]', '', value)
            if not cleaned_value or cleaned_value in ['-', '.']:
                return "TZS 0.00"
            value = Decimal(cleaned_value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif hasattr(value, '__float__'):
            value = Decimal(str(float(value)))
        else:
            return "TZS 0.00"
        
        return f"TZS {value:,.2f}"
    except (ValueError, TypeError, Exception):
        return "TZS 0.00"

@register.filter
def time_since_activity(activity):
    """
    Get human-readable time since activity
    """
    if hasattr(activity, 'get_time_since'):
        return activity.get_time_since()
    return ""

@register.filter
def activity_icon(action):
    """
    Get appropriate icon for activity type
    """
    icons = {
        'create': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>',
        'update': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 10.12h-6.78l2.74-2.82c-2.73-2.7-7.15-2.8-9.88-.1-2.73 2.71-2.73 7.08 0 9.79s7.15 2.71 9.88 0C18.32 15.65 19 14.08 19 12.1h2c0 1.98-.88 4.55-2.64 6.29-3.51 3.48-9.21 3.48-12.72 0-3.5-3.47-3.53-9.11-.02-12.58 3.51-3.47 9.14-3.47 12.65 0L21 3v7.12zM12.5 8v4.25l3.5 2.08-.72 1.21L11 13V8h1.5z"/></svg>',
        'delete': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>',
        'payment': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>',
        'login': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
        'complaint': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/><path d="M12 8v4m0 4h.01" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
        'maintenance': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>',
        'booking': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/></svg>',
        'lease': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>',
        'document': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/></svg>',
    }
    return icons.get(action, '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"/></svg>')

@register.filter
def activity_color(action):
    """
    Get appropriate color class for activity type
    """
    colors = {
        'create': 'new',
        'update': 'update',
        'delete': 'delete',
        'payment': 'payment',
        'login': 'new',
        'logout': 'update',
        'complaint': 'warning',
        'maintenance': 'maintenance',
        'booking': 'booking',
        'lease': 'lease',
        'document': 'document',
    }
    return colors.get(action, 'default')