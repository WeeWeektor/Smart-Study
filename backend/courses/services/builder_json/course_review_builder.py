def build_course_review_json(review):
    user_data = {
        "id": str(review.user_id),
        "name": "",
        "surname": "",
        "profile_picture": None
    }

    if hasattr(review, 'user') and review.user:
        user_data["name"] = getattr(review.user, "name", "")
        user_data["surname"] = getattr(review.user, "surname", "")
        if hasattr(review.user, "profile") and review.user.profile.profile_picture:
            user_data["profile_picture"] = str(review.user.profile.profile_picture)

    return {
        "id": str(review.id),
        "course_id": str(review.course_id),
        "comment": review.comment,
        "created_at": review.created_at.isoformat() if review.created_at else "",
        "rating": review.rating,
        "user": user_data,
        "is_verified": review.is_verified
    }
