from asgiref.sync import sync_to_async

from common.utils import error_response, sanitize_input, validate_uuid, success_response
from courses.models import Course
from courses.services.cache_service import invalidate_author_cache
from courses.utils import course_structure_create_or_update


async def course_patch_service(course_id, request_user, request_data, files, raw_form):
    """
    Централізований сервіс для редагування курсу.
    Повертає response об'єкт або викликає Exception.
    """
    change_info = str(raw_form.get('change_info_course', 'false')).lower() == 'true'
    change_structure = str(raw_form.get('change_structure_course', 'false')).lower() == 'true'

    if not change_info and not change_structure:
        return error_response('No data to update', status=400)

    data = {k: sanitize_input(v) if isinstance(v, str) else v for k, v in request_data.items()}
    cover_file = files.get('cover_image') if files else None

    uuid_obj = validate_uuid(course_id)
    course = await sync_to_async(Course.objects.select_related('details').get)(pk=uuid_obj)

    structure_was_updated = False

    if change_structure:
        if course.is_published:
            from courses.services.course_actions_service import update_published_course_with_structure
            await update_published_course_with_structure(course)

        await course_structure_create_or_update(
            data.get('courseStructure', []),
            request_user,
            course_id,
            files
        )
        structure_was_updated = True

    if change_info:
        from courses.services.course_actions_service import update_course
        response = await update_course(course, data, cover_file)

        if response.get('status_code') == 400 and structure_was_updated:
            return success_response({
                "data": "Course structure updated successfully.",
                "course_id": str(course.id)
            })

        if response.status_code == 200:
            await invalidate_author_cache(
                author_id=str(request_user.id),
                instance_type="courses",
                instance_type_cache="courses_get"
            )
        return response

    return success_response({
        "data": "Course structure updated successfully.",
        "course_id": str(course.id)
    })
