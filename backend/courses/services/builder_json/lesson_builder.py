def build_lesson_json(lesson):
    return {
        "lesson": {
            "id": getattr(lesson, "id", None),
            "module_id": getattr(lesson, "module_id", None),
            "title": getattr(lesson, "title", ""),
            "description": getattr(lesson, "description", ""),
            "content_type": getattr(lesson, "content_type", ""),
            "content": getattr(lesson, "content", ""),
            "order": getattr(lesson, "order", 1),
            "duration": getattr(lesson, "duration", None).total_seconds() if getattr(lesson, "duration", None) else 0,
        }
    }
