from asgiref.sync import async_to_sync
from celery import shared_task

from courses.services.cache_service import invalidate_all_course_recommendations_cache


@shared_task
def train_course_recommendations():
    from ml_model.recommender import courses_recommender
    courses_recommender.train()

    async_to_sync(invalidate_all_course_recommendations_cache)()

    return "Recommendations retrained"
