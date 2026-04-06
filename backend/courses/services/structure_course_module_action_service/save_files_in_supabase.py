from typing import Literal

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from common.services import validate_picture_file, validate_video_file, validate_audio_file, validate_document_file, \
    validate_presentation_file
from common.utils import supabase
from smartStudy_backend import settings

VALIDATORS_MAP = {
    'image': validate_picture_file,
    'video': validate_video_file,
    'audio': validate_audio_file,
    'document': validate_document_file,
    'presentation': validate_presentation_file,
}


async def save_files_in_supabase(
        courseId,
        file,
        file_name,
        type_data: Literal['course-test', 'module-test', 'lesson'],
        type_file: Literal['video', 'image', 'document', 'presentation', 'audio'] = 'image'
):
    validator = VALIDATORS_MAP.get(type_file)

    if validator:
        try:
            await sync_to_async(validator)(file)
        except ValidationError as e:
            raise ValidationError(f"{_('File validation error:')} {str(e)}")

    file_path = f"{courseId}/{type_data}/{file_name}"

    try:
        file.seek(0)
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
