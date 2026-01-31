from asgiref.sync import sync_to_async
from django.utils import timezone

from common.services import mongo_repo
from common.utils import validate_uuid, sanitize_input, error_response
from courses.models import Test, UserCourseEnrollment, TestAttempt


async def submit_test_attempt(user_id, test_id, test_type: str, user_answers: list):
    try:
        user_id = validate_uuid(user_id)
        test_id = validate_uuid(test_id)
        user_answers = sanitize_input(user_answers)
    except ValueError as e:
        return error_response(str(e), status=400)

    try:
        test, enrollment = await _get_test_and_enrollment(user_id, test_id, test_type)
    except (Test.DoesNotExist, UserCourseEnrollment.DoesNotExist):
        return error_response("Test or Enrollment not found", status=404)
    except ValueError as e:
        return error_response(str(e), status=400)

    mongo_document = await sync_to_async(mongo_repo.get_document_by_id)("questions_data_for_test", test.test_data_ids)

    if not mongo_document:
        return error_response("Test data not found", status=404)

    questions_list = mongo_document.get('questions', [])
    calculation_result = _calculate_score_and_details(test, questions_list, user_answers)

    attempt = await _create_attempt_entry(
        user_id, test, enrollment, test_type, calculation_result
    )

    if test_type in ["course_test", "module_test"] and enrollment:
        await _update_course_progress(user_id, test_id, enrollment, calculation_result['passed'])

    return {
        "id": str(attempt.id),
        "score": calculation_result['total_score'],
        "max_score": calculation_result['max_score'],
        "passed": calculation_result['passed'],
        "percent": round(calculation_result['user_percent'], 2),
        "questions_result": calculation_result['response_details'],
    }


async def _get_test_and_enrollment(user_id, test_id, test_type: str):
    """
    Повертає кортеж (test, enrollment). Enrollment може бути None для публічних тестів.
    """
    enrollment = None

    if test_type == "course_test":
        test = await Test.objects.select_related("course").aget(id=test_id)
        enrollment = await UserCourseEnrollment.objects.aget(
            user_id=user_id, course_id=test.course_id
        )

    elif test_type == "module_test":
        test = await Test.objects.select_related("module__course").aget(id=test_id)
        enrollment = await UserCourseEnrollment.objects.aget(
            user_id=user_id, course_id=test.module.course_id
        )

    elif test_type == "public":
        test = await Test.objects.aget(id=test_id)

    else:
        raise ValueError("Invalid test type")

    return test, enrollment


def _calculate_score_and_details(test, questions_list: list, user_answers: list) -> dict:
    """
    Синхронна функція для порівняння відповідей і підрахунку балів.
    """
    mongo_map = {q['order']: q for q in questions_list}

    show_answers = getattr(test, 'show_correct_answers', False)

    total_score = 0.0
    max_score = sum(float(q.get('points', 0)) for q in questions_list)

    processed_details = []
    response_details = []

    for ans in user_answers:
        order = ans.get('order')
        selected = ans.get('selected_options', [])

        question_data = mongo_map.get(order)
        if not question_data:
            continue

        correct = question_data.get('correct_answers', [])
        points = float(question_data.get('points', 0))

        is_correct = set(selected) == set(correct)
        awarded = points if is_correct else 0.0
        total_score += awarded

        db_detail = {
            "order": order,
            "question_text": question_data.get('questionText'),
            "selected_choices": selected,
            "is_correct": is_correct,
            "points_awarded": awarded,
            "max_points": points
        }
        processed_details.append(db_detail)

        if show_answers:
            frontend_detail = db_detail.copy()
            frontend_detail["correct_choices"] = correct
            frontend_detail["explanation"] = question_data.get('explanation')
            response_details.append(frontend_detail)

    pass_threshold_percent = getattr(test, 'pass_score', 0.0)
    user_percent = (total_score / max_score * 100) if max_score > 0 else 0.0
    passed = user_percent >= pass_threshold_percent

    return {
        "total_score": total_score,
        "max_score": max_score,
        "user_percent": user_percent,
        "passed": passed,
        "processed_details": processed_details,
        "response_details": response_details
    }


async def _create_attempt_entry(user_id, test, enrollment, test_type, result: dict):
    """
    Створення запису про спробу в БД.
    """
    if test_type == "public":
        prev_attempts_count = await TestAttempt.objects.filter(
            user_id=user_id, test=test
        ).acount()
    else:
        prev_attempts_count = await TestAttempt.objects.filter(
            enrollment=enrollment, test=test
        ).acount()

    attempt_number = prev_attempts_count + 1

    attempt = await TestAttempt.objects.acreate(
        enrollment=enrollment,
        user_id=user_id if test_type == "public" else None,
        test=test,
        score=result['total_score'],
        passed=result['passed'],
        attempt_number=attempt_number,
        attempt_details=result['processed_details'],
        completed_at=timezone.now()
    )
    return attempt


async def _update_course_progress(user_id, test_id, enrollment, is_passed):
    """
    Оновлення прогресу користувача на курсі.
    """
    from courses.services.course_by_user import update_enrollment_progress_sync
    await sync_to_async(update_enrollment_progress_sync)(
        user_id=user_id,
        course_id=str(enrollment.course_id),
        element_id=str(test_id),
        time_spent_seconds=0,
        element_type="test",
        is_completed=is_passed,
        finished_course=False,
    )
