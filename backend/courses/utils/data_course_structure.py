from typing import Literal

from courses.services import validate_lesson_data
from courses.services.lesson_actions_service import convert_to_markdown, create_lesson
from courses.services.module_actons_service import create_module
from courses.services.structure_course_module_action_service import save_files_in_supabase
from courses.services.test_actions_service import create_test


async def course_structure_create_or_update(courseStructure: list, owner, courseId, files=None):
    """
        Редагування структури курсу:
        Створює нові елементи або оновлює існуючі на основі наявності ID.
    """
    for structure in courseStructure:
        structure_type = structure.get('type')

        if structure_type == 'module':
            await _process_module(structure, owner, courseId, files)

        elif structure_type == 'course-test':
            await _process_test(structure, owner, parent_type="course", parent_id=courseId, course_id=courseId,
                                files=files)


async def _process_module(structure, owner, course_id, files):
    """Обробляє створення або оновлення модуля та його вмісту (уроків/тестів)"""
    module_id = structure.get('module_id')
    module_data = {**structure, "course_id": course_id}

    if module_id:
        pass
        # TODO await update_module(module_id, module_data)
    else:
        module = await create_module(module_data, course_id)
        module_id = str(module.id)
        structure['module_id'] = module_id

    for child in structure.get('moduleStructure', []):
        child_type = child.get('type')

        if child_type == 'module-test':
            await _process_test(child, owner, parent_type="module", parent_id=module_id, course_id=course_id,
                                files=files)

        elif child_type == 'lesson':
            await _process_lesson(child, module_id, course_id, files)


async def _process_lesson(lesson_data, module_id, course_id, files):
    """Обробляє створення або оновлення одного уроку"""
    lesson_id = lesson_data.get('lesson_id')
    lesson_payload = {**lesson_data, "module_id": str(module_id)}

    validate_lesson_data(lesson_payload)
    content = await convert_to_markdown(lesson=lesson_data, files=files, courseId=course_id)

    if lesson_id:
        pass
        # TODO await update_lesson(lesson_id, lesson_payload, contentData=content)
    else:
        await create_lesson(lesson_payload, contentData=content)


async def _process_test(test_data, owner, parent_type: Literal["module", "course"], parent_id, course_id, files):
    """
    Універсальний обробник для тестів.
    Підходить як для тестів курсу (course-test), так і для тестів модуля (module-test).
    """
    test_id = test_data.get('test_id')
    test_payload = {**test_data, f"{parent_type}_id": str(parent_id)}

    if test_id:
        pass
        # TODO await update_test(parent_type, owner, test_id, test_payload)
    else:
        await create_test(parent_type, owner, test_payload)

    if 'questions' in test_data:
        test_type = f"{parent_type}-test"
        await _question_image_upload(test_data['questions'], files, course_id, test_type)


async def _question_image_upload(questionList, files, courseId, type_test):
    if not files:
        return

    for question in questionList:
        questionImageKey = question.get('imageFileKey')
        if questionImageKey:
            file = files.get(questionImageKey)
            if file:
                await save_files_in_supabase(
                    courseId=courseId,
                    file=file,
                    file_name=questionImageKey,
                    type_data=type_test
                )
