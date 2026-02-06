import json

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import error_response, sanitize_input, success_response
from courses.services.builder_json import build_course_review_json
from courses.services.cache_service import get_course_review_cache
from courses.services.course_review_actions_service import create_review_of_course


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CourseReviewView(LocalizedView):
    @login_required_async
    async def get(self, request):
        course_id = request.GET.get("course_id")
        if not course_id:
            return error_response(gettext("course_id parameter is required."), status=400)

        course_reviews = await get_course_review_cache(course_id)
        if isinstance(course_reviews, JsonResponse):
            return course_reviews

        return success_response({
            "course_id": course_id,
            "reviews": course_reviews
        })

    @login_required_async
    async def post(self, request):
        try:
            raw_data = json.loads(request.body)
        except json.JSONDecodeError:
            raw_data = json.loads(request.POST.get('data', '{}'))

        data = {}
        for k, v in raw_data.items():
            if isinstance(v, str):
                is_multiline_field = k in ['comment', 'description', 'content']
                data[k] = sanitize_input(v, multiline=is_multiline_field)
            else:
                data[k] = v

        print(data)

        try:
            review = await create_review_of_course(data, request.user)
            review_json = await sync_to_async(build_course_review_json)(review)
            return success_response({
                "message": gettext("Review created successfully."),
                "review": review_json
            })
        except ValidationError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response(f"{gettext("Error creating course review:")} {str(e)}", status=500)
