from asgiref.sync import sync_to_async

from courses.models import Lesson


async def update_path_in_markdown_content(module_id, old_prefix, new_prefix):
    lessons_content = await sync_to_async(lambda: list(Lesson.objects.filter(module_id=module_id).only('content', 'id')))()

    for lesson_content in lessons_content:
        if lesson_content.content and old_prefix in lesson_content.content:
            updated_content = lesson_content.content.replace(old_prefix, new_prefix)
            await sync_to_async(Lesson.objects.filter(id=lesson_content.id).update)(content=updated_content)
