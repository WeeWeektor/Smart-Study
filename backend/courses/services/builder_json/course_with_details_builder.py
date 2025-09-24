def build_course_json_success(course, course_details, course_owner, structure=None):
    return {
        "course": {
            "id": getattr(course, "id", None),
            "title": getattr(course, "title", ""),
            "description": getattr(course, "description", ""),
            "category": getattr(course, "category", ""),
            "owner": {
                "id": getattr(course_owner, "id", None),
                "name": getattr(course_owner, "name", ""),
                "surname": getattr(course_owner, "surname", ""),
                "email": getattr(course_owner, "email", ""),
                "profile_picture": getattr(course_owner, "profile_picture", None),
            },
            "cover_image": getattr(course, "cover_image", ""),
            "is_published": getattr(course, "is_published", False),
            "created_at": getattr(course, "created_at", None),
            "published_at": getattr(course, "published_at", None),
            "updated_at": getattr(course, "updated_at", None),
            "version": getattr(course, "version", None),
            "details": {
                "total_modules": getattr(course_details, "total_modules", 0),
                "total_lessons": getattr(course_details, "total_lessons", 0),
                "total_tests": getattr(course_details, "total_tests", 0),
                "time_to_complete": getattr(course_details, "time_to_complete", None),
                "course_language": getattr(course_details, "course_language", ""),
                "rating": float(getattr(course_details, "rating", 0.0)),
                "level": getattr(course_details, "level", ""),
                "number_completed": getattr(course_details, "number_completed", 0),
                "number_of_active": getattr(course_details, "number_of_active", 0),
                "feedback_count": getattr(course_details, "feedback_count", 0),
                "feedback_summary": getattr(course_details, "feedback_summary", {}),
            },
            "structure_ids": str(getattr(course, "structure_ids")) if getattr(course, "structure_ids") else None,
            "structure": structure if structure else {},
        }
    }
