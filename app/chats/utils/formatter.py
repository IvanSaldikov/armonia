import re

import markdown
from django.utils.safestring import mark_safe


class FormatterUtils:
    link_pattern = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)

    @classmethod
    def convert_text_to_md(cls, text: str | None) -> str | None:
        if not text:
            return None
        md = markdown.Markdown(extensions=["fenced_code"])
        # text = text.replace("href", 'target="_blank" href')
        text = cls.link_pattern.sub(r"\1<a href='\2' target='_blank'>\3\4</a>", text)
        text = md.convert(text)
        return mark_safe(text)
