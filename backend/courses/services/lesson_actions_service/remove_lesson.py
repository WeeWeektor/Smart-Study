from asgiref.sync import sync_to_async

from common.utils import supabase
from courses.models import Lesson
from courses.services.structure_course_module_action_service import remove_data_from_structure
from smartStudy_backend import settings


async def remove_lesson(lesson_id, course_id, module_order, module_structure, module_id):
    target_lesson = None
    for item in module_structure.get('structure', []):
        if str(item.get('lesson_id')) == str(lesson_id):
            target_lesson = item
            break

    if target_lesson:
        lesson_order = target_lesson.get('order')

        await delete_lesson_files_by_prefix(course_id, module_order, lesson_order)

    await remove_data_from_structure(
        target_type="module",
        target_id=str(module_id),
        filter_data={"lesson_id": str(lesson_id)}
    )

    await Lesson.objects.filter(pk=lesson_id).adelete()


async def delete_lesson_files_by_prefix(course_id, module_order, lesson_order):
    """
    Видаляє всі файли уроку (і блоки _b0, і одинарні _single) за префіксом.
    """
    bucket_name = settings.SUPABASE_COURSES_COVER_PICTURES_BUCKET
    folder_path = f"{course_id}/lesson"
    file_prefix = f"lesson_file_m{module_order}_l{lesson_order}_"

    try:
        bucket = supabase.storage.from_(bucket_name)

        files_in_folder = await sync_to_async(bucket.list)(
            path=folder_path,
            options={"search": file_prefix}
        )

        if not files_in_folder:
            return

        files_to_remove = [
            f"{folder_path}/{f['name']}"
            for f in files_in_folder
            if f['name'].startswith(file_prefix)
        ]

        if files_to_remove:
            await sync_to_async(bucket.remove)(files_to_remove)

    except Exception as e:
        print(f"Error deleting files by prefix: {e}")
