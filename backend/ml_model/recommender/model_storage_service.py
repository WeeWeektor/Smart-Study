import os
import pickle
from typing import Dict, Any, Optional

from smartStudy_backend import settings


class ModelStorageService:
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_model', 'recommender', 'data', 'course_matrix.pkl')

    @classmethod
    def save_model(cls, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(cls.MODEL_PATH), exist_ok=True)
        with open(cls.MODEL_PATH, 'wb') as f:
            pickle.dump(data, f)
        print(f"ML Model trained and saved to {cls.MODEL_PATH}")

    @classmethod
    def load_model(cls) -> Optional[Dict[str, Any]]:
        if not os.path.exists(cls.MODEL_PATH):
            return None

        try:
            with open(cls.MODEL_PATH, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
