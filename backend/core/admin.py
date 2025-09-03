from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

admin.site.extra_head = format_html(
    '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,{}" />',
    'PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgdmlld0JveD0iMCAwIDMyIDMyIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iOCIgZmlsbD0iIzAyODRjNyIgLz4KPHBhdGggZD0iTTE2IDhMNiAxM0wxNiAxOEwyNiAxM0wxNiA4WiIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIvPgo8cGF0aCBkPSJNMTEgMTUuNVYyMC41QzExIDIwLjUgMTMuNSAyMi41IDE2IDIyLjVDMTguNSAyMi41IDIxIDIwLjUgMjEgMjAuNVYxNS41TDE2IDE4TDExIDE1LjVaIiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIi8+CjxyZWN0IHg9IjI1IiB5PSIxMyIgd2lkdGg9IjIiIGhlaWdodD0iNyIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgcng9IjEiLz4KPC9zdmc+'
)

admin.site.site_header = format_html(
    '<div style="display: flex; align-items: center; justify-content: center; color: white;">'
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" style="margin-right: 10px;">'
    '<rect width="32" height="32" rx="8" fill="#0284c7" />'
    '<path d="M16 8L6 13L16 18L26 13L16 8Z" fill="none" stroke="white"/>'
    '<path d="M11 15.5V20.5C11 20.5 13.5 22.5 16 22.5C18.5 22.5 21 20.5 21 20.5V15.5L16 18L11 15.5Z" fill="none" stroke="white"/>'
    '<rect x="25" y="13" width="2" height="7" fill="none" stroke="white" rx="1"/>'
    '</svg>'
    '<span style="color: white; font-weight: bold;">{}</span>'
    '</div>',
    _("Smart Study")
)
admin.site.index_title = _("Site administration")
admin.site.site_title = _("Smart Study")
