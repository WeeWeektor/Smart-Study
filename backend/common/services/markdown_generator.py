from typing import Optional, Any


class MarkdownHelper:
    """
    Клас для генерації Markdown/HTML розмітки для уроків.
    """

    @staticmethod
    def image(url: str, alt_text: str = "Image") -> str:
        """Генерує розмітку для картинки."""
        return f"![{alt_text}]({url})\n"

    @staticmethod
    def video(url: str, title: str = "Video") -> str:
        """
        Генерує HTML тег <video> для вбудовування плеєра.
        """
        return (
            f'\n<video controls width="100%" preload="metadata">\n'
            f'  <source src="{url}" type="video/mp4">\n'
            f'  [{title}]({url})\n'
            f'</video>\n\n'
            f'*[🔗 Відкрити відео окремо]({url})*\n'
        )

    @staticmethod
    def audio(url: str, title: str = "Audio") -> str:
        """Генерує HTML тег <audio>."""
        return (
            f'\n<audio controls style="width: 100%;">\n'
            f'  <source src="{url}" type="audio/mpeg">\n'
            f'  [{title}]({url})\n'
            f'</audio>\n\n'
        )

    @staticmethod
    def file_link(url: str, title: str = "Document", file_type: str = "file") -> str:
        """
        Генерує посилання на скачування файлу з іконкою.
        Підходить для PDF, DOCX, PPTX...
        """
        icons = {
            'document': '📄',
            'presentation': '📊',
            'link': '🔗',
            'archive': '📦',
            'file': '📎'
        }
        icon = icons.get(file_type, '📎')
        return f"\n### {icon} [{title}]({url})\n"

    @staticmethod
    def code_block(code: str, language: str = "text") -> str:
        """Генерує блок коду."""
        return f"\n```{language}\n{code}\n```\n"

    @staticmethod
    def text(content: str) -> str:
        """Просто повертає текст."""
        return f"{content}\n\n"

    @classmethod
    def generate_block(cls, block_type: str, data: Any, url: Optional[str] = None) -> str:
        """
        Метод-диспетчер.
        Приймає тип блоку, дані (текст/налаштування) та URL (якщо це файл).
        """
        if block_type == 'text':
            return cls.text(str(data))

        elif block_type == 'code':
            language = data.get('language', 'text') if isinstance(data, dict) else 'text'
            code_content = data.get('code', '') if isinstance(data, dict) else str(data)
            return cls.code_block(code_content, language)

        if not url:
            return ""

        if block_type == 'image':
            return cls.image(url)
        elif block_type == 'video':
            return cls.video(url)
        elif block_type == 'audio':
            return cls.audio(url)
        elif block_type == 'presentation':
            return cls.file_link(url, title="Завантажити презентацію", file_type='presentation')
        elif block_type == 'document':
            return cls.file_link(url, title="Завантажити документ", file_type='document')
        elif block_type == 'link':
            link_url = data if isinstance(data, str) else url
            return cls.file_link(link_url, title="Корисне посилання", file_type='link')

        return ""
