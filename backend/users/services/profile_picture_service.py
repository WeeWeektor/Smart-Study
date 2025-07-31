import uuid
import time
from django.core.exceptions import ValidationError
from smartStudy_backend import settings
from users.user_utils import supabase


def handle_profile_picture(user_profile, profile_picture):
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if profile_picture.content_type not in allowed_types:
        raise ValidationError("Непідтримуваний тип файлу. Дозволені: JPEG, PNG, GIF, WebP.")

    if profile_picture.size > 5 * 1024 * 1024:
        raise ValidationError("Розмір файлу перевищує 5MB.")

    if user_profile.profile_picture:
        try:
            folder_path = f"usersavatarts/{user_profile.user.id}/"
            files = supabase.storage.from_(settings.SUPABASE_BUCKET).list(folder_path)
            if files:
                file_paths = [f"{folder_path}{file['name']}" for file in files]
                supabase.storage.from_(settings.SUPABASE_BUCKET).remove(file_paths)
        except Exception:
            pass

    file_extension = profile_picture.name.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4()}_{int(time.time())}.{file_extension}"
    file_path = f"usersavatarts/{user_profile.user.id}/{unique_filename}"

    try:
        supabase.storage.from_(settings.SUPABASE_BUCKET).upload(
            path=file_path,
            file=profile_picture.read(),
            file_options={
                "content-type": profile_picture.content_type,
                "upsert": "true"
            }
        )
        public_url = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(file_path)
        user_profile.profile_picture = public_url
        user_profile.save()
    except Exception as e:
        raise ValidationError(f"Помилка при завантаженні файлу в Supabase: {str(e)}")
