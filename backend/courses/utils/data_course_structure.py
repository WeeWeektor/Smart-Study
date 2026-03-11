from typing import Literal
from uuid import UUID

from courses.models import Module
from courses.services import validate_lesson_data
from courses.services.lesson_actions_service import convert_to_markdown, create_lesson
from courses.services.module_actons_service import create_module, update_module
from courses.services.structure_course_module_action_service import save_files_in_supabase
from courses.services.test_actions_service import create_test


async def course_structure_create_or_update(courseStructure: list, owner, courseId, files=None):
    """
        Редагування структури курсу:
        Створює нові елементи або оновлює існуючі на основі наявності ID.
    """
    all_elem_to_delete = [item for item in courseStructure if item.get('action') == 'delete']
    elem_to_update_or_create = sorted(
        [item for item in courseStructure if item.get('action') != 'delete'],
        key=lambda item: int(item.get('order', 0)),
        reverse=False
    )

    # for item in all_elem_to_delete:
    #     if item.get('action', '') == 'delete':
    #         if item.get('type') == 'module':
    #             from courses.services.module_actons_service import remove_module
    #             await remove_module(item.get('module_id'))
    #         elif item.get('type') == 'course-test':
    #             from courses.services.test_actions_service import remove_test
    #             await remove_test(item.get('test_id'), test_type="course")

    for item in elem_to_update_or_create:
        if item.get('type') == 'module':
            await _process_module(item, owner, courseId, files)

        elif item.get('type') == 'course-test':
            await _process_test(item, owner, parent_type="course", parent_id=courseId, course_id=courseId, files=files)


async def _process_module(structure, owner, course_id, files):
    """Обробляє створення або оновлення модуля та його вмісту (уроків/тестів)"""
    module_id = structure.get('module_id')
    action = structure.get('action')
    module_order = structure.get('order', None)
    module_data = {**structure, "course_id": course_id}

    if module_id and action == 'update':
        await update_module(module_id, module_data)
    elif action == 'create' or not module_id:
        module = await create_module(module_data, course_id)
        module_id = str(module.id)
        structure['module_id'] = module_id

    for child in structure.get('moduleStructure', []):
        child_action = child.get('action')
        child_type = child.get('type')

        if child_action == 'delete':
            if child_type == 'lesson':
                from courses.services.lesson_actions_service import remove_lesson
                if module_order is None:
                    module_order = await (Module.objects
                                          .filter(id=module_id)
                                          .values_list("order", flat=True)
                                          .aget())

                await remove_lesson(child.get('lesson_id'), course_id, module_order, module_data, module_id)
            elif child_type == 'module-test':
                from courses.services.test_actions_service import remove_test
                await remove_test(UUID(child.get('test_id')), test_type="module")
            continue

        if child_type == 'module-test':
            await _process_test(child, owner, parent_type="module", parent_id=module_id, course_id=course_id,
                                files=files)
        elif child_type == 'lesson':
            await _process_lesson(child, module_id, course_id, files)


async def _process_lesson(lesson_data, module_id, course_id, files):
    """Обробляє створення або оновлення одного уроку"""
    lesson_id = lesson_data.get('lesson_id')
    action = lesson_data.get('action')
    lesson_payload = {**lesson_data, "module_id": str(module_id)}

    content = None
    # TODO Test all scenarios for convert to markdown
    # TODO duration приходить '00:00:00' і оновлюється такими даними - перевірити фронт
    if lesson_data.get('contentBlocks') is not None or lesson_data.get('singleContentData') is not None:
        content = await convert_to_markdown(lesson=lesson_data, files=files, courseId=course_id)

    if action == 'update' and lesson_id:
        from courses.services.lesson_actions_service import update_lesson
        await update_lesson(lesson_id, lesson_payload, module_id, contentData=content)
    elif action == 'create' and not lesson_id:
        validate_lesson_data(lesson_payload)
        await create_lesson(lesson_payload, contentData=content)


async def _process_test(test_data, owner, parent_type: Literal["module", "course"], parent_id, course_id, files):
    """
    Універсальний обробник для тестів.
    Підходить як для тестів курсу (course-test), так і для тестів модуля (module-test).
    """
    test_id = test_data.get('test_id')
    action = test_data.get('action')
    test_payload = {**test_data, f"{parent_type}_id": str(parent_id)}

    if action == 'update' and test_id:
        from courses.services.test_actions_service import update_test
        await update_test(test_payload, test_id, parent_type, all_new_questions_data=False)
    elif action == 'create' and not test_id:
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
