from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

from .hinglish_map import normalize_hinglish


MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
MODEL_PATH = MODEL_DIR / "scam_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"


SCAM_TYPES = ["Bank Fraud", "KYC Scam", "Lottery Scam", "Tech Support Scam", "Legitimate"]


@dataclass
class PredictionResult:
    text: str
    label: str
    risk_score: float
    scam_type: str
    confidence: float
    top_keywords: List[Tuple[str, float]]
    feature_contributions: Dict[str, float]


class ScamPredictor:
    def __init__(self) -> None:
        self.model: Optional[LogisticRegression] = None
        self.vectorizer: Optional[TfidfVectorizer] = None

    def ensure_loaded(self) -> None:
        if self.model is not None and self.vectorizer is not None:
            return
        if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
            raise FileNotFoundError(
                "Model artifacts not found. Please run train_model.py to train the model."
            )
        self.model = joblib.load(MODEL_PATH)
        self.vectorizer = joblib.load(VECTORIZER_PATH)

    @staticmethod
    def _basic_clean(text: str) -> str:
        """
        Basic cleaning consistent with training:
        - Hinglish normalization
        - Lowercasing
        - Remove non-alphanumeric characters (except spaces)
        """
        import re

        if not text:
            return ""
        text = normalize_hinglish(text)
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def predict(self, text: str) -> PredictionResult:
        self.ensure_loaded()
        assert self.model is not None and self.vectorizer is not None

        cleaned = self._basic_clean(text)
        X = self.vectorizer.transform([cleaned])

        proba = self.model.predict_proba(X)[0]
        classes = list(self.model.classes_)
        # Assuming "scam" is one of the labels
        if "scam" in classes:
            scam_idx = classes.index("scam")
        else:
            # Fallback to positive class index
            scam_idx = int(np.argmax(proba))

        scam_proba = float(proba[scam_idx])
        label = "scam" if scam_proba >= 0.5 else "legitimate"
        risk_score = round(scam_proba * 100, 2)

        # Scam type inference using simple keyword heuristics
        scam_type = self._infer_scam_type(cleaned, label)

        # Compute feature contributions from logistic regression coefficients
        feature_names = np.array(self.vectorizer.get_feature_names_out())
        if isinstance(self.model, LogisticRegression):
            # Binary classification – use coefficients for "scam" class
            coef = self.model.coef_[scam_idx]
        else:
            coef = np.zeros_like(feature_names, dtype=float)

        # Contribution = coefficient * tfidf value
        x_vec = X.toarray()[0]
        contributions = coef * x_vec
        feature_contrib_map: Dict[str, float] = {
            feature_names[i]: float(contributions[i])
            for i in range(len(feature_names))
            if contributions[i] != 0.0
        }

        # Select top contributing unigrams (features without spaces)
        unigram_contrib = {k: v for k, v in feature_contrib_map.items() if " " not in k}
        sorted_keywords = sorted(
            unigram_contrib.items(), key=lambda kv: abs(kv[1]), reverse=True
        )
        top_keywords = sorted_keywords[:10]

        confidence = scam_proba if label == "scam" else 1.0 - scam_proba

        return PredictionResult(
            text=text,
            label=label,
            risk_score=risk_score,
            scam_type=scam_type,
            confidence=round(float(confidence), 3),
            top_keywords=top_keywords,
            feature_contributions=feature_contrib_map,
        )

    @staticmethod
    def _infer_scam_type(cleaned_text: str, label: str) -> str:
        if label != "scam":
            return "Legitimate"

        text = cleaned_text.lower()
        if any(word in text for word in ["kyc", "update kyc", "re kyc"]):
            return "KYC Scam"
        if any(word in text for word in ["lottery", "kbc", "prize", "reward"]):
            return "Lottery Scam"
        if any(word in text for word in ["anydesk", "teamviewer", "remote access", "technical support"]):
            return "Tech Support Scam"
        if any(
            word in text
            for word in [
                "account",
                "bank",
                "sbi",
                "hdfc",
                "icici",
                "suspended",
                "blocked",
                "debit card",
                "credit card",
            ]
        ):
            return "Bank Fraud"
        return "Bank Fraud"


_global_predictor: Optional[ScamPredictor] = None


def get_predictor() -> ScamPredictor:
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = ScamPredictor()
    return _global_predictor

