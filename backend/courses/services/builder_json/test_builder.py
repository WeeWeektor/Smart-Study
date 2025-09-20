def build_public_test_json(test, owner, questions_data):
    return {
        "test": {
            "id": getattr(test, "id", None),
            "title": getattr(test, "title", ""),
            "description": getattr(test, "description", ""),
            "category": getattr(test, "category", ""),
            "level": getattr(test, "level", ""),
            "time_limit": getattr(test, "time_limit", 0),
            "count_attempts": getattr(test, "count_attempts", 0),
            "pass_score": getattr(test, "pass_score", 0),
            "randomize_questions": getattr(test, "randomize_questions", False),
            "show_correct_answers": getattr(test, "show_correct_answers", True),
            "test_data_ids": getattr(test, "test_data_ids", ""),
            "is_public": getattr(test, "is_public", False),
            "owner": {
                "id": getattr(owner, "id", None),
                "name": getattr(owner, "name", ""),
                "surname": getattr(owner, "surname", ""),
                "email": getattr(owner, "email", ""),
                "profile_picture": getattr(owner, "profile_picture", None),
            },
            "questions": questions_data["questions"],
        }
    }


def build_course_test_json(test, course, questions_data):
    return {
        "test": {
            "id": getattr(test, "id", None),
            "title": getattr(test, "title", ""),
            "description": getattr(test, "description", ""),
            "time_limit": getattr(test, "time_limit", 0),
            "count_attempts": getattr(test, "count_attempts", 0),
            "pass_score": getattr(test, "pass_score", 0),
            "randomize_questions": getattr(test, "randomize_questions", False),
            "show_correct_answers": getattr(test, "show_correct_answers", True),
            "test_data_ids": getattr(test, "test_data_ids", ""),
            "order": getattr(test, "order", False),
            "is_public": getattr(test, "is_public", False),
            "course": {
                "id": getattr(course, "id", None),
                "title": getattr(course, "title", ""),
                "course owner": getattr(course, "owner_id", ""),
                "is_published": getattr(course, "is_published", False),
                "course version": getattr(course, "version", None),
            },
            "questions": questions_data["questions"],
        }
    }


def build_module_test_json(test, module, questions_data):
    return {
        "test": {
            "id": getattr(test, "id", None),
            "title": getattr(test, "title", ""),
            "description": getattr(test, "description", ""),
            "time_limit": getattr(test, "time_limit", 0),
            "count_attempts": getattr(test, "count_attempts", 0),
            "pass_score": getattr(test, "pass_score", 0),
            "randomize_questions": getattr(test, "randomize_questions", False),
            "show_correct_answers": getattr(test, "show_correct_answers", True),
            "test_data_ids": getattr(test, "test_data_ids", ""),
            "order": getattr(test, "order", False),
            "is_public": getattr(test, "is_public", False),
            "module": {
                "id": getattr(module, "id", None),
                "course": getattr(module, "course", ""),
                "title": getattr(module, "title", ""),
                "is_published": getattr(module.course, "is_published", False),
                "description": getattr(module, "description", None),
            },
            "questions": questions_data["questions"],
        }
    }
