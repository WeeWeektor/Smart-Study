from asgiref.sync import sync_to_async
from django.core.cache import caches
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from common import LocalizedView
from common.decorators import login_required_async
from courses.models import Course, CourseVersion


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CountAllPublishedCourses(LocalizedView):
    @login_required_async
    async def get(self, request):
        CACHE_TIMEOUT = 60 * 60 * 4
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
