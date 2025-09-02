import uuid
import time
import logging

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.utils.translation import gettext

from smartStudy_backend import settings
from users.services.file_validation_service import validate_file_security
from users.user_utils import supabase


async def handle_profile_picture(user_profile, profile_picture):
    validate_file_security(profile_picture)

    user_id = await sync_to_async(lambda: user_profile.user.id)()

    if user_profile.profile_picture:
        try:
            await delete_profile_picture(user_id, delete_folder=False)
        except (FileNotFoundError, ValidationError, Exception) as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"{gettext("Unable to delete previous photo:")} {str(e)}")

    file_extension = profile_picture.name.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4()}_{int(time.time())}.{file_extension}"
    file_path = f"usersavatarts/{user_id}/{unique_filename}"

    try:
        file_content = await sync_to_async(profile_picture.read)()
        bucket = supabase.storage.from_(settings.SUPABASE_BUCKET)

        await sync_to_async(bucket.upload)(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": profile_picture.content_type,
                "upsert": "true"
            }
        )
        public_url = await sync_to_async(bucket.get_public_url)(file_path)
        user_profile.profile_picture = public_url
        await sync_to_async(user_profile.save)()
    except Exception as e:
        raise ValidationError(f"{gettext("Failed to upload file:")} {str(e)}")


async def delete_profile_picture(user_id, delete_folder=False):
    try:
        folder_path = f"usersavatarts/{user_id}/"
        bucket = supabase.storage.from_(settings.SUPABASE_BUCKET)

        files = await sync_to_async(bucket.list)(folder_path)
        if files:
            file_paths = [f"{folder_path}{file['name']}" for file in files]
            await sync_to_async(bucket.remove)(file_paths)

        if delete_folder:
            await sync_to_async(bucket.remove)([folder_path])

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"{gettext("Error when deleting a file from Supabase:")} {str(e)}")
        raise ValidationError(f"{gettext("Unable to delete profile photo:")} {str(e)}")
