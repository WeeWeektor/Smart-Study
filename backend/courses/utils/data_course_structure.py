from typing import Literal

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.services import validate_picture_file_security
from common.utils import supabase
from courses.services.module_actons_service import create_module
from courses.services.test_actions_service import create_test
from smartStudy_backend import settings


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
                    pass

        elif structure['type'] == 'course-test':
            await create_test("course", owner, {**structure, "course_id": courseId})
            await _question_image_upload(structure['questions'], files, courseId, 'course-test')


async def _question_image_upload(questionList, files, courseId, type_test: Literal['course-test', 'module-test']):
    for question in questionList:
        questionImageKey = question['imageFileKey'] if 'imageFileKey' in question else None
        if questionImageKey:
            file = files.get(questionImageKey)
            await _save_files_in_supabase(
                courseId=courseId,
                file=file,
                file_name=questionImageKey,
                type_data=type_test
            )


async def _save_files_in_supabase(courseId, file, file_name,
                                  type_data: Literal['course-test', 'module-test', 'lesson']):
    validate_picture_file_security(file)

    file_path = f"{courseId}/{type_data}/{file_name}"

    try:
        file_content = await sync_to_async(file.read)()
        bucket = supabase.storage.from_(settings.SUPABASE_COURSES_COVER_PICTURES_BUCKET)

        await sync_to_async(bucket.upload)(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": file.content_type,
                "upsert": "true"
            }
        )
        public_url = await sync_to_async(bucket.get_public_url)(file_path)

        return public_url

    except Exception as e:
        raise ValidationError(f"{_('Failed to upload file:')} {str(e)}")
