import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.services import delete_picture, mongo_repo
from common.utils import success_response
from courses.models import CourseVersion, Lesson, Test, Course


def extract_ids(version_items, course_id=None):
    """Допоміжна функція для отримання PK з JSON"""
    ids = set()
    for item_json in version_items:
        for obj in json.loads(item_json):
            if course_id and obj['fields'].get('course') != course_id:
                continue
            ids.add(obj['pk'])
    return ids


def delete_data(course, modules_to_delete, lessons_to_delete, all_tests_to_delete):
    if modules_to_delete:
        course.modules.filter(id__in=modules_to_delete).delete()
    if lessons_to_delete:
        Lesson.objects.filter(id__in=lessons_to_delete).delete()
    if all_tests_to_delete:
        Test.objects.filter(id__in=all_tests_to_delete).delete()
    if hasattr(course, 'details') and course.details:
        course.details.delete()
    course.delete()


async def remove_course(course):
    if course.is_published:
        raise ValidationError(_(
            "A published course cannot be deleted. Published courses can only be edited."
        ))

    course_id_str = str(course.id)

    version_obj = await sync_to_async(
        lambda: CourseVersion.objects.filter(course_id=course.id)
        .order_by('-version_number')
        .first()
    )()

    course = await sync_to_async(
        lambda: Course.objects.prefetch_related(
            'modules__lessons',
            'course_tests',
            'modules__module_tests'
        ).get(pk=course.id)
    )()

    modules = list(course.modules.all())
    lessons = [lesson for m in modules for lesson in m.lessons.all()]
    module_tests = [mt for m in modules for mt in m.module_tests.all()]
    course_tests = list(course.course_tests.all())

    current_module_ids = {m.id for m in modules}
    current_lesson_ids = {le.id for le in lessons}
    current_course_test_ids = {ct.id for ct in module_tests}
    current_module_test_ids = {mt.id for mt in course_tests}

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

        await delete_picture(instance_id=course.id, instance_type="course", delete_folder=True)

        delete_message = _("Course deleted successfully.")

    all_tests_to_delete = course_tests_to_delete | module_tests_to_delete

    for test_id in all_tests_to_delete:
        test_obj = await sync_to_async(Test.objects.only('test_data_ids').get)(pk=test_id)
        if test_obj and test_obj.test_data_ids:
            await sync_to_async(
                mongo_repo.delete_document_by_id)("questions_data_for_test", str(test_obj.test_data_ids))

    await sync_to_async(mongo_repo.delete_document)("course_structures", str(course.structure_ids))

    await sync_to_async(delete_data)(course, modules_to_delete, lessons_to_delete, all_tests_to_delete)

    return success_response({
        "message": delete_message,
        "course_id": course_id_str
    })
