from datetime import timedelta

from asgiref.sync import sync_to_async
from django.utils import timezone
from django.utils.translation import gettext as _

from common.services import mongo_repo
from common.utils import success_response, error_response, parse_time_str
from courses.services import validate_category_level
from courses.services.course_actions_service import upload_course_cover_image


async def update_course(course, data: dict, cover_file: object | None) -> dict:
    """Оновлення курсу власником курсу"""

    validate_category_level(data)

    updated_course_fields, updated_course_meta_fields, to_publish = update_fields(course, data)
    cover_file, cover_updated_fields = await update_course_cover_image(course, cover_file)

    updated_course_fields.extend(cover_updated_fields)

    if updated_course_fields or updated_course_meta_fields:
        return await save_course(course, updated_course_fields, updated_course_meta_fields, cover_file, to_publish)
    elif to_publish:
        from courses.services.course_actions_service import publish_course
        await publish_course(course)
        return success_response({"data": "Course published successfully.",
                                 "course_id": str(course.id)})
    else:
        return error_response(message=_("No changes detected to update the course."))


async def save_course(course,
                      updated_course_fields: list,
                      updated_course_meta_fields: list,
                      cover_file: object | None,
                      publish: bool
                      ) -> dict:
    course.updated_at = timezone.now()
    updated_course_fields.append("updated_at")

    if updated_course_meta_fields:
        await sync_to_async(course.details.save)(update_fields=updated_course_meta_fields)

    await sync_to_async(course.save)(update_fields=updated_course_fields)

    if publish:
        from courses.services.course_actions_service import publish_course
        await publish_course(course)

    return success_response({"data": "Course updated successfully.",
                             "cover_image": str(cover_file) if cover_file else None,
                             "course_id": str(course.id),
                             "publish": course.is_published
                             })


def update_fields(course, data: dict) -> tuple[list, list, bool]:
    """Оновлення полів курсу та метаданих курсу"""
    updated_course_fields = []
    updated_course_meta_fields = []
    to_publish = False

    for field, value in data.items():
        if hasattr(course, field) and getattr(course, field) != value:
            if field == 'is_published':
                if str(value).lower() == 'true':
                    to_publish = True
                else:
                    setattr(course, field, False)
                    updated_course_fields.append(field)
            else:
                setattr(course, field, value)
                updated_course_fields.append(field)
        elif hasattr(course.details, field):
            field_value = getattr(course.details, field)
            if isinstance(field_value, timedelta) and isinstance(value, str):
                value = parse_time_str(value)
            if field_value != value:
                setattr(course.details, field, value)
                updated_course_meta_fields.append(field)

    return updated_course_fields, updated_course_meta_fields, to_publish


async def update_course_cover_image(course, cover_file: object | None) -> tuple[object | None, list]:
    """Оновлення обкладинки курсу"""
    updated_fields = []

    if not cover_file:
        return None, updated_fields

    file_name = getattr(course, "cover_image", None)
    if file_name:
        file_name = file_name.split('.')
        file_name = f'{file_name[3]}.{file_name[4].replace("?", "")}'

    if file_name != str(cover_file):
        cover_file = await upload_course_cover_image(course, cover_file)
        course.cover_image = cover_file
        updated_fields.append("cover_image")
    else:
        cover_file = None

    return cover_file, updated_fields


async def update_published_course_with_structure(course):
    """Асинхронне оновлення курсу:
        - створює snapshot (версію)
        - знімає з публікації
    """
    await sync_to_async(course.update_version)()
    course.is_published = False
    course.published_at = None

    course_structure = await sync_to_async(mongo_repo.get_document_by_id)("course_structures", course.structure_ids)
    new_structure = await sync_to_async(mongo_repo.insert_document)("course_structures", course_structure)
    course.structure_ids = new_structure

    await sync_to_async(course.save)(update_fields=['is_published', 'published_at', 'structure_ids'])
    return success_response({"data": "Create version snapshot and unpublished course"})
