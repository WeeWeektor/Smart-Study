from typing import List, Optional, Dict, Any

import pandas as pd

from ml_model.recommender.course_db_service import CourseDBService
from ml_model.recommender.ml_trainer_service import MLTrainerService
from ml_model.recommender.model_storage_service import ModelStorageService


class CourseRecommender:
    def __init__(self):
        self._model_cache = None

    def train(self):
        """Оркестратор процесу тренування."""
        raw_data = CourseDBService.get_training_data()
        if not raw_data:
            print("No courses found for training.")
            return

        model_data = MLTrainerService.build_matrix(raw_data)
        ModelStorageService.save_model(model_data)
        self._model_cache = model_data

    def _get_model_data(self) -> Optional[Dict[str, Any]]:
        """Лениве завантаження моделі (Singleton pattern для даних)."""
        if self._model_cache is not None:
            return self._model_cache

        data = ModelStorageService.load_model()

        if data and 'df' in data:
            df = data['df']
            if 'level_int' not in df.columns or not pd.api.types.is_numeric_dtype(df['level_int']):
                print("Model schema mismatch. Triggering retraining...")
                self.train()
                return self._model_cache

        self._model_cache = data
        return data

    def get_recommendations(self, course_id: int, status: str = 'passed', limit: int = 6) -> List[int]:
        """Основний метод отримання рекомендацій."""

        data = self._get_model_data()

        if not data:
            return CourseDBService.get_popular_courses_ids(limit)

        indices = data.get('indices')
        cosine_sim = data.get('cosine_sim')
        df = data.get('df')

        if course_id not in indices:
            return CourseDBService.get_popular_courses_ids(limit)

        try:
            idx = indices[course_id]

            current_course_row = df.loc[df['id'] == course_id]
            if current_course_row.empty:
                return CourseDBService.get_popular_courses_ids(limit)

            current_level = int(current_course_row['level_int'].values[0])

            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

            sim_scores = sim_scores[1:]

            recommended_indices = []

            for i, score in sim_scores:
                candidate_id = df.iloc[i]['id']
                candidate_level = int(df.iloc[i]['level_int'])

                if status == 'failed':
                    if candidate_level <= current_level:
                        recommended_indices.append(candidate_id)
                else:
                    if candidate_level >= current_level:
                        recommended_indices.append(candidate_id)

                if len(recommended_indices) >= limit:
                    break

            if not recommended_indices:
                recommended_indices = [df.iloc[score[0]]['id'] for score in sim_scores[:limit]]

            return recommended_indices

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return CourseDBService.get_popular_courses_ids(limit)


courses_recommender = CourseRecommender()
