from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from common.utils import validate_uuid
from courses.models import Course, CourseVersion


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CountAllPublishedCourses(LocalizedView):
    @login_required_async
    async def get(self, request):
        CACHE_TIMEOUT = 60 * 60 * 1
        cache = caches['courses_get']
        cache_key = 'CountAllPublishedCourses'

        cached_data = await sync_to_async(lambda: cache.get(cache_key, version=1))()
        if cached_data:
            return JsonResponse({'count': cached_data})

        count_published_courses = await sync_to_async(Course.objects.filter(is_published=True).count)()
        count_version_courses = await sync_to_async(CourseVersion.objects.count)()
        count = count_published_courses + count_version_courses

        await sync_to_async(lambda: cache.set(cache_key, count, CACHE_TIMEOUT, version=1))()

        return JsonResponse({'count': count})


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CountTeacherCourses(LocalizedView):
    @login_required_async
    async def get(self, request):
        is_owner = request.GET.get("owner").lower()
        author_id = request.GET.get("author")

        try:
            uuid_obj = validate_uuid(author_id)
        except ValidationError:
            return JsonResponse({'error': 'Invalid author ID'}, status=400)

        count_version_teacher_courses = await sync_to_async(
            CourseVersion.objects.filter(owner=uuid_obj).count)()

        if is_owner == 'true':
            count_teacher_courses = await sync_to_async(Course.objects.filter(owner=uuid_obj).count)()
            count_teacher_courses += count_version_teacher_courses
        else:
            count_teacher_courses = 0

        count_published_teacher_courses = await sync_to_async(
            Course.objects.filter(owner=uuid_obj, is_published=True).count)()

        count_published_teacher_courses += count_version_teacher_courses

        return JsonResponse({'allCourses': count_teacher_courses, 'publishedCourses': count_published_teacher_courses})
