import logging
import time
import uuid

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext

from common.services import validate_picture_file_security
from common.utils import supabase
from smartStudy_backend import settings

logger = logging.getLogger(__name__)


def _get_bucket(instance_type: str):
    """Вибір бакету залежно від типу"""
    if instance_type == "user":
        return supabase.storage.from_(settings.SUPABASE_USERS_PROFILE_PICTURES_BUCKET)
    elif instance_type == "course":
        return supabase.storage.from_(settings.SUPABASE_COURSES_COVER_PICTURES_BUCKET)
    else:
        raise ValidationError(gettext("Unsupported instance type"))


async def handle_picture(instance, picture, instance_type: str, picture_field: str):
    """
    Завантажує фото (для User або Course).
    :param instance: модель (user_profile чи course)
    :param picture: файл
    :param instance_type: 'user' або 'course'
    :param picture_field: назва поля у моделі ('picture', 'image' тощо)
    """
    validate_picture_file_security(picture)

    instance_id = await sync_to_async(lambda: instance.id)()
    current_picture = getattr(instance, picture_field, None)

    if current_picture:
        try:
            await delete_picture(instance_id, instance_type, delete_folder=False)
        except (FileNotFoundError, ValidationError, Exception) as e:
            logger.warning(f"{gettext('Unable to delete previous photo:')} {str(e)}")

    file_extension = picture.name.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4()}_{int(time.time())}.{file_extension}"
    file_path = f"{instance_id}/{unique_filename}"

    try:
        file_content = await sync_to_async(picture.read)()
        bucket = _get_bucket(instance_type)

        await sync_to_async(bucket.upload)(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": picture.content_type,
                "upsert": "true"
            }
        )
        public_url = await sync_to_async(bucket.get_public_url)(file_path)

        setattr(instance, picture_field, public_url)
        await sync_to_async(instance.save)()
    except Exception as e:
        raise ValidationError(f"{gettext('Failed to upload file:')} {str(e)}")


async def delete_picture(instance_id, instance_type: str, delete_folder=False):
    """
    Видаляє фото (User або Course).
    :param instance_id: id моделі
    :param instance_type: 'user' або 'course'
    :param delete_folder: чи видаляти всю папку
    """
    try:
        folder_path = f"{instance_id}/"
        bucket = _get_bucket(instance_type)

        files = await sync_to_async(bucket.list)(folder_path)
        if files:
            file_paths = [f"{folder_path}{file['name']}" for file in files]
            await sync_to_async(bucket.remove)(file_paths)

        if delete_folder:
            await sync_to_async(bucket.remove)([folder_path])

    except Exception as e:
        logger.error(f"{gettext('Error when deleting a file from Supabase:')} {str(e)}")
        raise ValidationError(f"{gettext('Unable to delete image:')} {str(e)}")
