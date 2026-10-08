import os
import joblib
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_DIR = os.environ.get("MODEL_DIR", os.path.join(PROJECT_ROOT, "models", "selected_model"))
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.joblib")


class ModelLoader:
    def __init__(self):
        self.model = None
        self.vectorizer = None

    def load(self) -> Tuple[object, object]:
        if self.model is not None and self.vectorizer is not None:
            return self.model, self.vectorizer

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model artifact not found at {MODEL_PATH}")
        if not os.path.exists(VECTORIZER_PATH):
            raise FileNotFoundError(f"Vectorizer artifact not found at {VECTORIZER_PATH}")

        self.vectorizer = joblib.load(VECTORIZER_PATH)
        self.model = joblib.load(MODEL_PATH)
        logger.info("Model and vectorizer loaded successfully.")
        return self.model, self.vectorizer


model_loader = ModelLoader()
