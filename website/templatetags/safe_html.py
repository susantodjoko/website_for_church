import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'b', 'i', 'u', 's',
    'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'blockquote', 'pre', 'code',
    'a', 'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span',
    'hr',
]

_ALLOWED_ATTRS = {
    'a':   ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height', 'style'],
    'td':  ['colspan', 'rowspan'],
    'th':  ['colspan', 'rowspan'],
    '*':   ['class'],
}


@register.filter(is_safe=True)
def clean_html(value):
    """Sanitise rich-text HTML from Summernote before rendering."""
    if not value:
        return ''
    cleaned = bleach.clean(
        value,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        strip=True,
    )
    return mark_safe(cleaned)
