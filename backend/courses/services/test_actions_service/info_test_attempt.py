from django.core.exceptions import ObjectDoesNotExist

from common.utils import error_response, success_response, validate_uuid
from courses.models import Test, TestAttempt


async def history_and_config(test_id, user, test_type):
    test_id = validate_uuid(test_id)

    try:
        test = await Test.objects.aget(id=test_id)

        if test_type == "public":
            attempts_qs = TestAttempt.objects.filter(
                test_id=test_id,
                user=user
            )
        else:
            attempts_qs = TestAttempt.objects.filter(
                test_id=test_id,
                enrollment__user=user
            )

        attempts = [
            attempt async for attempt in attempts_qs.order_by('-started_at')
        ]

        max_attempts = getattr(test, 'count_attempts', 0)
        show_correct_answers = getattr(test, 'show_correct_answers', False)
        randomize_questions = getattr(test, 'randomize_questions', False)

        attempts_used = len(attempts)
        is_unlimited = not max_attempts

        can_attempt = True
        remaining_attempts = None

        if not is_unlimited:
            remaining_attempts = max(0, max_attempts - attempts_used)
            can_attempt = remaining_attempts > 0

        history_data = [
            {
                "id": str(a.id),
                "attempt_number": a.attempt_number,
                "score": a.score,
                "passed": a.passed,
                "started_at": a.started_at,
                "completed_at": a.completed_at,
            }
            for a in attempts
        ]

        return success_response({
            "history": history_data,
            "config": {
                "can_attempt": can_attempt,
                "show_correct_answers": show_correct_answers,
                "randomize_questions": randomize_questions,
                "attempts_used": attempts_used,
                "max_attempts": max_attempts if not is_unlimited else "unlimited",
                "remaining_attempts": remaining_attempts if not is_unlimited else "unlimited"
            }
        })

    except ObjectDoesNotExist:
        return error_response("Test not found", status=404)
    except Exception as e:
        return error_response(str(e), status=500)
