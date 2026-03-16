from typing import Literal
from uuid import UUID

from common.services import move_supabase_files_batch
from courses.models import Module
from courses.services import validate_lesson_data
from courses.services.lesson_actions_service import convert_to_markdown, create_lesson, update_path_in_markdown_content
from courses.services.module_actons_service import create_module, update_module
from courses.services.structure_course_module_action_service import save_files_in_supabase, delete_files_from_supabase
from courses.services.test_actions_service import create_test, update_path_in_mongo_questions_data


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

    # TODO оновлення в монго шляху для курс тесту
    for item in all_elem_to_delete:
        if item.get('type') == 'module':
            from courses.services.module_actons_service import remove_module
            await remove_module(item.get('module_id'))
        elif item.get('type') == 'course-test':
            from courses.services.test_actions_service import remove_test
            await remove_test(item.get('test_id'), test_type="course")

    for item in elem_to_update_or_create:
        if item.get('type') == 'module':
            await _process_module(item, owner, courseId, files)

        elif item.get('type') == 'course-test':
            await _process_test(item, owner, parent_type="course", parent_id=courseId, course_id=courseId, files=files)


async def _process_module(structure, owner, course_id, files):
    """Обробляє створення або оновлення модуля та його вмісту (уроків/тестів)"""
    module_id = structure.get('module_id')
    action = structure.get('action')
    new_order = structure.get('order', None)
    module_data = {**structure, "course_id": course_id}

    if module_id and action == 'update':
        old_order = await update_module(module_id, module_data)

        if old_order != new_order:
            old_p_l, new_p_l = f"lesson_file_m{old_order}_", f"lesson_file_m{new_order}_"
            old_p_t, new_p_t = f"question_image_m{old_order}_", f"question_image_m{new_order}_"

            await move_supabase_files_batch(course_id, "lesson", old_p_l, new_p_l)
            await move_supabase_files_batch(course_id, "module-test", old_p_t, new_p_t)

            await update_path_in_markdown_content(module_id=module_id, old_prefix=old_p_l, new_prefix=new_p_l)
            await update_path_in_mongo_questions_data(old_prefix=old_p_t, new_prefix=new_p_t, module_id=module_id)

    elif action == 'create' or not module_id:
        module = await create_module(module_data, course_id)
        module_id = str(module.id)
        new_order = int(module.order)
        structure['module_id'] = module_id

    child_item_to_delete = [item for item in structure.get('moduleStructure', []) if item.get('action') == 'delete']
    child_item_to_update_or_create = sorted(
        [item for item in structure.get('moduleStructure', []) if item.get('action') != 'delete'],
        key=lambda item: int(item.get('order', 0)),
        reverse=False
    )

    for child in child_item_to_delete:
        await _process_structure_module_child(child, course_id, module_id, module_data, new_order, owner, files)
    for child in child_item_to_update_or_create:
        await _process_structure_module_child(child, course_id, module_id, module_data, new_order, owner, files)


async def _process_structure_module_child(child, course_id, module_id, module_data, module_order, owner, files):
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

    # TODO lesson / test дописати
    # TODO перевірити за blcok в уроках
    # TODO Test this logic
    if child.get('type') == 'lesson' and child.get('action') == 'update':
        l_id = child.get('lesson_id')
        new_l_order = child.get('order')

        from courses.models import Lesson
        old_lesson = await Lesson.objects.filter(id=l_id).only('order').aget()
        old_l_prefix = f"lesson_file_m{module_order}_l{old_lesson.order}_"
        new_l_prefix = f"lesson_file_m{module_order}_l{new_l_order}_"

        if old_lesson.order != new_l_order:
            await move_supabase_files_batch(course_id, "lesson", old_l_prefix, new_l_prefix)

    if child.get('type') == 'module-test' and child.get('action') == 'update':
        t_id = child.get('test_id')
        new_t_order = child.get('order')

        from courses.models import Test
        old_test = await Test.objects.filter(id=t_id).only('order').aget()
        old_t_prefix = f"question_image_m{module_order}_t{old_test.order}_"
        new_t_prefix = f"question_image_m{module_order}_t{new_t_order}_"

        if old_test.order != new_t_order:
            await move_supabase_files_batch(course_id, "module-test", old_t_prefix, new_t_prefix)
            await update_path_in_mongo_questions_data(old_t_prefix, new_t_prefix, module_id)

    if child_type == 'module-test':
        await _process_test(child, owner, parent_type="module", parent_id=module_id, course_id=course_id,
                            files=files)
    elif child_type == 'lesson':
        await _process_lesson(child, module_id, course_id, files, module_order)


async def _process_lesson(lesson_data, module_id, course_id, files, module_order):
    """Обробляє створення або оновлення одного уроку"""
    lesson_id = lesson_data.get('lesson_id')
    action = lesson_data.get('action')
    lesson_payload = {**lesson_data, "module_id": str(module_id)}

    content = None
    if len(lesson_data.get('contentBlocks', [])) > 0 or len(lesson_data.get('singleContentData', [])) > 0:
        content = await convert_to_markdown(
            lesson=lesson_data,
            files=files,
            courseId=course_id,
            lesson_id=lesson_id,
            module_order=module_order
        )

    if action == 'update' and lesson_id:
        from courses.services.lesson_actions_service import update_lesson
        await update_lesson(lesson_id, lesson_payload, module_id, contentData=content)
    elif action == 'create' or not lesson_id:
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

    old_questions_data = []

    if action == 'update' and test_id:
        from courses.services.test_actions_service import update_test
        _, old_questions_data = await update_test(test_payload, test_id, parent_type, all_new_questions_data=False)
    elif action == 'create' or not test_id:
        await create_test(parent_type, owner, test_payload)

    if 'questions' in test_data:
        test_type = f"{parent_type}-test"
        await _question_image_upload(test_data['questions'], files, course_id, test_type, action, old_questions_data)


async def _question_image_upload(questionList, files, courseId, type_test, action, old_questions_data):
    old_images_map = {
        q.get('order'): q.get('image_url')
        for q in old_questions_data
        if q.get('image_url')
    }

    for question in questionList:
        order = question.get('order')
        question_image_key = question.get('imageFileKey')
        file = files.get(question_image_key) if question_image_key else None
        if file:
            if action == 'update':
                old_file_name = old_images_map.get(order)
                if old_file_name:
                    await _safe_delete_from_sup(courseId, type_test, old_file_name)

            await save_files_in_supabase(
                courseId=courseId,
                file=file,
                file_name=question_image_key,
                type_data=type_test
            )

        elif action == 'update' and order in old_images_map:
            if not question.get('image_url') and not question.get('imageFileKey'):
                old_file_name = old_images_map.get(order)
                await _safe_delete_from_sup(courseId, type_test, old_file_name)


async def _safe_delete_from_sup(courseId, type_data, file_name):
    try:
        await delete_files_from_supabase(
            courseId=courseId,
            type_data=type_data,
            file_names=file_name
        )
    except Exception as e:
        print(f"Delete failed: {e}")
