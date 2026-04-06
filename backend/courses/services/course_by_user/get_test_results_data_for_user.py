from asgiref.sync import sync_to_async
from django.db.models import Q

from common.utils import validate_uuid
from courses.models import UserCourseEnrollment, Test, TestAttempt
from courses.serializers import CourseTestSummarySerializer


async def get_test_results_data_for_user(course_id, user):
    course_id = validate_uuid(course_id)

    enrollment = await UserCourseEnrollment.objects.aget(user=user, course_id=course_id)

    results_data = await sync_to_async(_get_test_results_data)(enrollment, course_id)

    serializer = CourseTestSummarySerializer(results_data, many=True)

    return serializer.data


def _get_test_results_data(enrollment, course_id):
    tests = Test.objects.filter(
        Q(course_id=course_id) | Q(module__course_id=course_id)
    ).values(
        'id', 'title', 'module_id', 'pass_score', 'count_attempts'
    ).order_by('module__order', 'order')

    if not tests:
        return []

    test_ids = [t['id'] for t in tests]

    attempts = TestAttempt.objects.filter(
        enrollment=enrollment,
        test__id__in=test_ids
    ).values('test_id', 'score', 'passed')

    attempts_by_test = {}
    for attempt in attempts:
        t_id = attempt['test_id']
        if t_id not in attempts_by_test:
            attempts_by_test[t_id] = []
        attempts_by_test[t_id].append(attempt)

    final_results = []
    for test in tests:
        test_attempts = attempts_by_test.get(test['id'], [])

        attempts_used = len(test_attempts)

        is_passed = any(a['passed'] for a in test_attempts)

        best_score = max([a['score'] for a in test_attempts]) if test_attempts else 0.0

        final_results.append({
            'id': test['id'],
            'title': test['title'],
            'module_id': test['module_id'],
            'score': best_score,
            'pass_score': test['pass_score'],
            'passed': is_passed,
            'attempts_used': attempts_used,
            'max_attempts': test['count_attempts']
        })

    return final_results
