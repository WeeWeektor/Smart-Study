from typing import Literal

from courses.services.lesson_actions_service import convert_to_markdown
from courses.services.module_actons_service import create_module
from courses.services.structure_course_module_action_service import save_files_in_supabase
from courses.services.test_actions_service import create_test


async def course_structure(courseStructure: list, owner, courseId, files=None):
    print("courseStructure", courseStructure)
    for structure in courseStructure:
        if structure['type'] == 'module':
            module = await create_module({**structure, "course_id": courseId}, courseId)

            for moduleStructure in structure['moduleStructure']:
                if moduleStructure['type'] == 'module-test':
                    await create_test("module", owner, {**moduleStructure, "module_id": str(module.id)})
                    await _question_image_upload(moduleStructure['questions'], files, courseId, 'module-test')

                elif moduleStructure['type'] == 'lesson':
                    content = await convert_to_markdown(lesson=moduleStructure, files=files, courseId=courseId)
                    # await create_lesson(owner, {**moduleStructure, "module_id": str(module.id)}, contentData=content)

                    # TODO при створені курсу якщо курс був створений а на моменті створення модуля все впало через не прописане імя модуля курс не повинен створюватись або має створюватись падати і продовжувати створюватись з моменту якого впав модуль

        elif structure['type'] == 'course-test':
            await create_test("course", owner, {**structure, "course_id": courseId})
            await _question_image_upload(structure['questions'], files, courseId, 'course-test')


async def _question_image_upload(questionList, files, courseId, type_test: Literal['course-test', 'module-test']):
    for question in questionList:
        questionImageKey = question['imageFileKey'] if 'imageFileKey' in question else None
        if questionImageKey:
            file = files.get(questionImageKey)
            await save_files_in_supabase(
                courseId=courseId,
                file=file,
                file_name=questionImageKey,
                type_data=type_test
            )
