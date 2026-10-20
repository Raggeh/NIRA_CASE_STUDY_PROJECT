"""Supervised model definitions shared by notebooks 05 and 06.

The four tasks stay separate. Model names and hyperparameters live here so the
selection pass and the later corpus-prediction pass use the same estimators.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import ComplementNB, MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

TOKEN_PATTERN = r"(?u)\b[^\W\d_]{2,}\b"
CLASSICAL_MODEL_NAMES = [
    "multinomial_nb",
    "complement_nb",
    "logistic_regression",
    "linear_svc",
]
EMBEDDING_MODEL_NAME = "embedding_logistic"


def make_tfidf():
    return TfidfVectorizer(
        token_pattern=TOKEN_PATTERN,
        lowercase=True,
        min_df=2,
        ngram_range=(1, 2),
    )


def make_classical_estimator(model_name, seed):
    if model_name == "multinomial_nb":
        return MultinomialNB()
    if model_name == "complement_nb":
        return ComplementNB()
    if model_name == "logistic_regression":
        return LogisticRegression(
            class_weight="balanced",
            max_iter=2000,
            random_state=seed,
        )
    if model_name == "linear_svc":
        return LinearSVC(class_weight="balanced", random_state=seed)
    raise KeyError(model_name)


def make_classical_pipeline(model_name, seed):
    return Pipeline([
        ("tfidf", make_tfidf()),
        ("clf", make_classical_estimator(model_name, seed)),
    ])


def make_embedding_estimator(seed):
    return LogisticRegression(
        class_weight="balanced",
        max_iter=2000,
        random_state=seed,
    )
