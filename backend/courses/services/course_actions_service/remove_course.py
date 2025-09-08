import asyncio
import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.services import delete_profile_picture
from common.utils import success_response
from courses.models import CourseVersion, Lesson, Test, Course


async def remove_course(course):
    if course.is_published:
        raise ValidationError(_(
            "A published course cannot be deleted. Published courses can only be edited."
        ))

    course_id_str = str(course.id)
    course_title = course.title

    version_obj = await sync_to_async(
        lambda: CourseVersion.objects.filter(course_id=course.id).order_by('-version_number').first()
    )()

    def extract_ids(version_items, course_id=None):
        """Допоміжна функція для отримання PK з JSON"""
        ids = set()
        for item_json in version_items:
            for obj in json.loads(item_json):
                if course_id and obj['fields'].get('course') != course_id:
                    continue
                ids.add(obj['pk'])
        return ids

    course = await sync_to_async(
        lambda: Course.objects.prefetch_related(
            'modules',
            'modules__lessons',
            'course_tests',
            'modules__module_tests'
        ).get(pk=course.id)
    )()

    current_module_ids = {m.id for m in course.modules.values_list('id', flat=True)}
    current_lesson_ids = {l.id for m in course.modules.values_list('lessons', flat=True)
                          for l in m.lessons.values_list('id', flat=True)}
    current_course_test_ids = {ct.id for ct in course.course_tests.values_list('id', flat=True)}
    current_module_test_ids = {mt.id for m in course.modules.values_list('module_tests', flat=True)
                               for mt in m.module_tests.values_list('id', flat=True)}

    tasks = []
    if version_obj:
        version_data = version_obj.course_data

        modules_to_delete = current_module_ids - extract_ids(version_data.get('modules', []))
        lessons_to_delete = current_lesson_ids - extract_ids(version_data.get('lessons', []))
        course_tests_to_delete = current_course_test_ids - extract_ids(
            version_data.get('course_tests', []),
            course_id_str
        )
        module_tests_to_delete = current_module_test_ids - extract_ids(
            version_data.get('module_tests', []),
            course_id_str
        )

        delete_message = _("All draft data for the course has been deleted; the published version remains.")

    else:
        modules_to_delete = current_module_ids
        lessons_to_delete = current_lesson_ids
        course_tests_to_delete = current_course_test_ids
        module_tests_to_delete = current_module_test_ids

        delete_message = _("Course deleted successfully.")

        tasks += [
            sync_to_async(delete_profile_picture)(instance_id=course.id, instance_type="course", delete_folder=True)
        ]

    all_tests_to_delete = course_tests_to_delete | module_tests_to_delete

    tasks += [
        sync_to_async(course.modules.filter(id__in=modules_to_delete).delete)(),
        sync_to_async(Lesson.objects.filter(id__in=lessons_to_delete).delete)(),
        sync_to_async(Test.objects.filter(id__in=all_tests_to_delete).delete)(),
    ]

    if hasattr(course, 'details'):
        tasks.append(sync_to_async(course.details.delete)())

    await asyncio.gather(*tasks)

    await sync_to_async(course.delete)()

    return success_response({
        "message": delete_message,
        "course_id": course_id_str,
        "course_title": course_title
    })
