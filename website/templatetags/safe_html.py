import re

import bleach
from django import template
from django.utils.html import escape
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


_HTML_TAG_RE = re.compile(r'<[a-zA-Z][^>]*>')


@register.filter(is_safe=True)
def paragraphs(value):
    """Render text as paragraphs.

    Plain text from a textarea gets each non-empty line wrapped in its own
    <p>; text that is already HTML is just sanitised.
    """
    if not value:
        return ''
    if not _HTML_TAG_RE.search(value):
        lines = (line.strip() for line in value.splitlines())
        value = ''.join(f'<p>{escape(line)}</p>' for line in lines if line)
    return clean_html(value)
