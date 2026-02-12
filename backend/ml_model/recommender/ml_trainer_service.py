import os
from typing import List, Dict, Any

import pandas as pd
from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from smartStudy_backend import settings


class MLTrainerService:
    LEVEL_MAPPING = {
        'beginner': 1,
        'intermediate': 2,
        'advanced': 3
    }

    @staticmethod
    def _load_stop_words() -> List[str]:
        stop_words_set = set(ENGLISH_STOP_WORDS)

        ua_file_path = os.path.join(settings.BASE_DIR, 'ml_model', 'data', 'stopwords_ua.txt')

        if os.path.exists(ua_file_path):
            try:
                with open(ua_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        cleaned_line = line.strip()
                        if not cleaned_line:
                            continue

                        words = cleaned_line.split()
                        stop_words_set.update(words)

            except IOError:
                print(f"Warning: Could not read stop words file at {ua_file_path}")

        custom_trash = ['курс', 'урок', 'навчання', 'online', 'course']
        stop_words_set.update(custom_trash)
        return list(stop_words_set)

    @classmethod
    def build_matrix(cls, courses_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Створює матрицю схожості на основі даних курсів."""
        if not courses_data:
            return {}

        df = pd.DataFrame(courses_data)

        df['content'] = df['title'] + " " + df['description']
        df['content'] = df['content'].fillna('')

        df['level_int'] = df['details__level'].map(cls.LEVEL_MAPPING).fillna(1).astype(int)

        combined_stop_words = cls._load_stop_words()
        tfidf = TfidfVectorizer(stop_words=combined_stop_words, max_features=5000)
        tfidf_matrix = tfidf.fit_transform(df['content'])

        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        return {
            'indices': pd.Series(df.index, index=df['id']).drop_duplicates(),
            'cosine_sim': cosine_sim,
            'df': df[['id', 'level_int']]
        }
