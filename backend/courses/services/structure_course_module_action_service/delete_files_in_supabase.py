from typing import Literal

from asgiref.sync import sync_to_async

from common.services.picture_service import logger
from common.utils import supabase
from smartStudy_backend import settings


async def delete_files_from_supabase(
        courseId,
        type_data: Literal['course-test', 'module-test', 'lesson'],
        file_names: str or [str]
):
    if isinstance(file_names, str):
        file_path = [f"{courseId}/{type_data}/{file_names}", ]
    else:
        file_path = [f"{courseId}/{type_data}/{file_name}" for file_name in file_names]

    try:
        bucket = supabase.storage.from_(settings.SUPABASE_COURSES_COVER_PICTURES_BUCKET)

        response = await sync_to_async(bucket.remove)(file_path)

        if not response:
            logger.warning(f"File not found or already deleted: {file_path}")

        return response

    except Exception as e:
        logger.error(f"Failed to delete file from Supabase: {str(e)}")
        return None
