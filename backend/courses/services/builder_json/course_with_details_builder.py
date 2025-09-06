def build_course_json_success(course, course_details, course_owner):
    return {
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "category": course.category,
            "owner": {
                "id": course_owner.id,
                "name": course_owner.name,
                "surname": course_owner.surname,
                "email": course_owner.email,
                "profile_image": course_owner.profile_image if hasattr(course_owner, 'profile_image') else None,
            },
            "cover_image": course.cover_image if course.cover_image else "",
            "is_published": course.is_published,
            "created_at": course.created_at,
            "published_at": course.published_at if course.published_at else None,
            "updated_at": course.updated_at,
            "version": course.version,
            "details": {
                "course_structure": course_details.course_structure,
                "total_modules": course_details.total_modules,
                "total_lessons": course_details.total_lessons,
                "total_tests": course_details.total_tests,
                "time_to_complete": course_details.time_to_complete,
                "course_language": course_details.course_language,
                "rating": float(course_details.rating),
                "level": course_details.level,
                "number_completed": course_details.number_completed,
                "number_of_active": course_details.number_of_active,
                "feedback_count": course_details.feedback_count,
                "feedback": course_details.feedback,
            }
        }
    }


def build_course_json_failure(course):
    return {
        "course": {
            "id": getattr(course, "id", None),
            "title": getattr(course, "title", ""),
            "description": getattr(course, "description", ""),
            "category": getattr(course, "category", ""),
            "owner": {
                "id": getattr(course, "owner_id", None),
                "data": {}
            },
            "cover_image": getattr(course, "cover_image", ""),
            "is_published": getattr(course, "is_published", False),
            "created_at": getattr(course, "created_at", None),
            "published_at": getattr(course, "published_at", None),
            "updated_at": getattr(course, "updated_at", None),
            "version": getattr(course, "version", None),
            "details": {}
        }
    }
