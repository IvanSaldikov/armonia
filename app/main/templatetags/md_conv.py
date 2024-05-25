from django import template
from django.template.defaultfilters import stringfilter

from chats.utils.formatter import FormatterUtils

register = template.Library()


@register.filter
@stringfilter
def render_markdown(value):
    return FormatterUtils.convert_text_to_md(text=value)
