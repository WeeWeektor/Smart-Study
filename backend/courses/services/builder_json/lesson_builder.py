def build_lesson_json(lesson):
    return {
        "lesson": {
            "id": getattr(lesson, "id", None),
            "title": getattr(lesson, "title", ""),
            # "description": getattr(test, "description", ""),
            # "time_limit": getattr(test, "time_limit", 0),
            # "count_attempts": getattr(test, "count_attempts", 0),
            # "pass_score": getattr(test, "pass_score", 0),
            # "randomize_questions": getattr(test, "randomize_questions", False),
            # "show_correct_answers": getattr(test, "show_correct_answers", True),
            # "test_data_ids": getattr(test, "test_data_ids", ""),
            # "order": getattr(test, "order", False),
            # "is_public": getattr(test, "is_public", False),
            # "module": {
            #     "id": getattr(module, "id", None),
            #     "course": getattr(module, "course", ""),
            #     "title": getattr(module, "title", ""),
            #     "is_published": getattr(module.course, "is_published", False),
            #     "description": getattr(module, "description", None),
            # },
            # "questions": questions_data["questions"],
        }
    }
