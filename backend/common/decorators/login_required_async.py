from functools import wraps

from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from common.utils import error_response


def login_required_async(func):
    @wraps(func)
    async def wrapper(view, request, *args, **kwargs):
        is_auth = await sync_to_async(lambda: request.user.is_authenticated)()
        if not is_auth:
            return error_response(_('The user is not authorized.'), 401)
        return await func(view, request, *args, **kwargs)

    return wrapper
