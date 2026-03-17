from asgiref.sync import sync_to_async

from courses.models import Lesson
from courses.services.structure_course_module_action_service import update_data_in_structure


async def update_lesson(lesson_id, lesson_payload, module_id, contentData=None):
    lesson = await Lesson.objects.aget(id=lesson_id)

    fields_to_update = _update_lesson_fields(lesson, lesson_payload)

    if contentData:
        lesson.content = contentData
        lesson.content_type = lesson_payload.get("typeCategory", lesson.content_type)
        fields_to_update.extend(["content", "content_type"])

    if fields_to_update:
        await sync_to_async(lesson.save)(update_fields=fields_to_update)

    if any(f in fields_to_update for f in ("title", "order", "content_type", "duration")):
        await update_data_in_structure(
            target_type="module",
            target_id=str(module_id),
            structure_data={
                "title": lesson.title,
                "order": lesson.order,
                "content_type": lesson.content_type,
                "duration": str(lesson.duration)
            },
            identifier_field="lesson_id",
            identifier_value=str(lesson_id)
        )

def _update_lesson_fields(lesson, data: dict) -> list:
    updated_fields = []

    for field, value in data.items():
        if hasattr(lesson, field) and getattr(lesson, field) != value:
            setattr(lesson, field, value)
            updated_fields.append(field)

    return updated_fields
