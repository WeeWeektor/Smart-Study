from common.services import get_all_objects_recursive
from common.utils import supabase
from courses.models import Lesson
from courses.services.structure_course_module_action_service import remove_data_from_structure, \
    delete_files_from_supabase
from smartStudy_backend import settings


async def remove_lesson(lesson_id, course_id, module_order, module_structure, module_id):
    for item in module_structure.get('structure', []):
        lesson_order = item.get('order', None)
        lesson_content_type = item.get('content_type', None)

        if lesson_content_type == "custom":
            bucket = supabase.storage.from_(settings.SUPABASE_COURSES_COVER_PICTURES_BUCKET)
            file_to_delete_inc = f"lesson_file_m{module_order}_l{lesson_order}_b"
            all_files = await get_all_objects_recursive(f"{course_id}/lesson/", bucket)

            file_names = []
            for file in all_files:
                if file_to_delete_inc in file:
                    file_names.append(file.split("/")[-1])

            if file_names:
                await delete_files_from_supabase(course_id, "lesson", file_names)

        else:
            file_to_delete_inc = f"lesson_file_m{module_order}_l{lesson_order}_single"
            await delete_files_from_supabase(course_id, "lesson", file_to_delete_inc)

    await remove_data_from_structure(
        target_type="module",
        target_id=str(module_id),
        filter_data={"lesson_id": str(lesson_id)}
    )

    await Lesson.objects.filter(pk=lesson_id).adelete()
