from typing import Optional, Any, Dict, Union

from django.utils.translation import gettext as _


class MarkdownHelper:
    @staticmethod
    def text(content: str) -> str:
        if not content: return ""
        return f"{content}\n\n"

    @staticmethod
    def title(content: str) -> str:
        return f"# {content}\n\n"

    @staticmethod
    def description(content: str) -> str:
        return f"> {content}\n\n"

    @staticmethod
    def comment(content: str) -> str:
        return f"\n***{_('Методичний коментар')}:** {content}*\n\n"

    @staticmethod
    def image(url: str, alt_text: str = "Image") -> str:
        return f"\n![{alt_text}]({url})\n\n"

    @staticmethod
    def video(url: str, title: str = "Video") -> str:
        return (
            f'\n<video controls="controls" width="100%" preload="metadata">\n'
            f'  <source src="{url}" type="video/mp4">\n'
            f'  [{title}]({url})\n'
            f'</video>\n\n'
            f'*[🔗 {_("Відкрити відео окремо")}]({url})*\n\n'
        )

    @staticmethod
    def audio(url: str, title: str = "Audio") -> str:
        return (
            f'\n<audio controls="controls" style="width: 100%;">\n'
            f'  <source src="{url}" type="audio/mpeg">\n'
            f'  [{title}]({url})\n'
            f'</audio>\n\n'
        )

    @staticmethod
    def code_block(data: Union[Dict, str]) -> str:
        language = 'text'
        code = ''

        if isinstance(data, dict):
            language = data.get('language', 'text')
            code = data.get('code', '')
        else:
            code = str(data)

        return f"\n```{language}\n{code}\n```\n\n"

    @staticmethod
    def file_link(url: str, title: str, file_type: str = "file") -> str:
        icons = {
            'document': '📄',
            'presentation': '📊',
            'link': '🔗',
            'live': '🔴',
            'archive': '📦',
            'file': '📎'
        }
        icon = icons.get(file_type, '📎')
        return f"\n### {icon} [{title}]({url})\n\n"

    @classmethod
    def generate_block(cls, block_type: str, data: Any, url: Optional[str] = None) -> str:
        if not data and not url:
            return ""

        if block_type == 'title':
            return cls.title(str(data))

        if block_type == 'description':
            return cls.description(str(data))

        if block_type == 'comment':
            return cls.comment(str(data))

        if block_type in ['text', 'assignment']:
            prefix = f"### {_('Завдання')}:\n" if block_type == 'assignment' else ""
            return cls.text(f"{prefix}{str(data)}")

        if block_type == 'code':
            return cls.code_block(data)

        if block_type in ['link', 'live']:
            link_url = data if isinstance(data, str) else url
            link_title = _("Приєднатися до зустрічі") if block_type == 'live' else _("Корисне посилання")
            return cls.file_link(link_url, title=link_title, file_type=block_type)

        if not url:
            return ""

        if block_type == 'video':
            return cls.video(url, title=_("Відео уроку"))

        if block_type == 'audio':
            return cls.audio(url, title=_("Аудіозапис"))

        if block_type == 'image':
            return cls.image(url)

        if block_type == 'presentation':
            return cls.file_link(url, title=_("Завантажити презентацію"), file_type='presentation')

        if block_type == 'document':
            return cls.file_link(url, title=_("Завантажити документ"), file_type='document')

        return cls.text(str(data))
