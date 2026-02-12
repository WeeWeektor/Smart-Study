from celery import shared_task


@shared_task
def train_course_recommendations():
    from ml_model.recommender import courses_recommender

    courses_recommender.train()
    return "Recommendations retrained"
