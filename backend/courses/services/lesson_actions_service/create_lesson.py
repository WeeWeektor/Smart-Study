from asgiref.sync import sync_to_async

from courses.models import Lesson
from courses.services.structure_course_module_action_service import add_data_to_structure


async def create_lesson(data: dict, contentData: str) -> object:
    if contentData == '':
        raise ValueError("Content data is required to create a lesson.")

    data_to_create_lesson = {
        "module_id": data.get("module_id"),
        "title": data.get("title").strip(),
        "description": data.get("description").strip(),
        "content_type": data.get("typeCategory"),
        "content": contentData,
        "order": data.get("order", 1),
        "duration": data.get("duration"),
    }

    created_lesson = await sync_to_async(Lesson.objects.create)(**data_to_create_lesson)

    await add_data_to_structure(
        target_type="module",
        target_id=data.get("module_id"),
        structure_type="lesson",
        structure_data={
            "lesson_id": str(created_lesson.id),
            "title": created_lesson.title,
            "order": created_lesson.order
        },
    )

    from courses.services.cache_service import invalidate_cached_instance_by_id
    await invalidate_cached_instance_by_id(
        instance_id=created_lesson.id,
        instance_type_cache="courses_get",
        instance_type="lesson",
    )

    return created_lesson
