"""Load the saved NIRA outputs for the Streamlit dashboard."""

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PHONE = re.compile(
    r"(?i)(?:\+?252[\s\-]?\d[\d\s\-]{6,}\d|\btell\s*:\s*\+?\d[\d\s\-]+|\b\d{10,15}\b)"
)
MODEL_NAMES = {
    "complement_nb": "Complement naive Bayes",
    "logistic_regression": "Logistic regression",
    "linear_svc": "Linear SVC",
    "multinomial_nb": "Multinomial naive Bayes",
    "embedding_logistic": "Embedding logistic regression",
}
TASK_NAMES = {
    "policy_relevance": "Policy relevance",
    "feedback_type": "Feedback type",
    "topic": "Manual topic",
    "sentiment": "Sentiment",
}
GROUP_NAMES = {
    "annotated_manual_vs_predicted": "Annotated: manual versus predicted",
    "unlabeled_raw_with_prediction": "Unlabeled raw comments",
    "additional_predicted_comments": "Further predicted comments",
}


def model_name(key):
    return MODEL_NAMES.get(key, key)


def load():
    eda = json.loads((ROOT / "outputs/02_eda/20261018_eda/eda_findings.json").read_text(encoding="utf-8"))
    posts = pd.read_csv(ROOT / "outputs/02_eda/20261018_eda/eda_post_summary.csv")
    timeline = pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/post_timeline.csv")
    periods = pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/posts_by_event_period.csv")
    topic_selection = json.loads(
        (ROOT / "outputs/04_topic_modeling/20261019_topic_models_function_words/topic_model_selection.json").read_text(encoding="utf-8")
    )
    selected = json.loads(
        (ROOT / "outputs/05_model_development/20261019_supervised/selected_models.json").read_text(encoding="utf-8")
    )
    sample = pd.read_csv(ROOT / "outputs/06_results_predictions/20261019_predictions/comment_comparison_sample.csv")
    if len(sample) != 30 or sample["record_key"].nunique() != 30:
        raise ValueError(f"Expected 30 unique comparison comments, found {len(sample)}")

    joined = posts.merge(
        timeline[["post_id", "linkage_class", "comparison_response_ids", "policy_topic"]],
        on="post_id",
        how="left",
    ).merge(periods[["post_id", "event_period"]], on="post_id", how="left")
    joined["publication_date_register"] = joined["publication_date_register"].astype(str).str.slice(0, 10)
    sample = sample.copy()
    sample["excerpt"] = sample["excerpt"].map(lambda text: PHONE.sub("[PHONE REDACTED]", str(text)))
    winners = {task: body["model"] for task, body in selected["tasks"].items()}
    return {
        "root": ROOT,
        "eda": eda,
        "posts": joined.sort_values("publication_date_register"),
        "lengths": pd.read_csv(ROOT / "outputs/02_eda/20261018_eda/eda_length_summary.csv"),
        "topic_selection": topic_selection,
        "topic_comparison": pd.read_csv(ROOT / "outputs/04_topic_modeling/20261019_topic_models_function_words/topic_model_comparison.csv"),
        "topic_terms": pd.read_csv(ROOT / "outputs/04_topic_modeling/20261019_topic_models_function_words/selected_topic_terms.csv"),
        "selected": selected,
        "winners": winners,
        "validation": pd.read_csv(ROOT / "outputs/05_model_development/20261019_supervised/validation_scores.csv"),
        "heldout": pd.read_csv(ROOT / "outputs/05_model_development/20261019_supervised/heldout_test_scores.csv"),
        "refit": pd.read_csv(ROOT / "outputs/06_results_predictions/20261019_predictions/refit_agreement.csv"),
        "distribution": pd.read_csv(ROOT / "outputs/06_results_predictions/20261019_predictions/label_distribution_comparison.csv"),
        "sample": sample,
        "overlap": json.loads((ROOT / "outputs/06_results_predictions/20261019_predictions/sample_overlap.json").read_text(encoding="utf-8")),
        "linkage": pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/linkage_class_counts.csv"),
        "period_summary": pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/event_period_summary.csv"),
        "period_shares": pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/predicted_label_shares_by_event_period.csv"),
        "named_posts": timeline.loc[timeline["comparison_response_ids"].fillna("").str.len() > 0],
        "text_match": pd.read_csv(ROOT / "outputs/03_annotation/20261018_annotation/annotation_text_match_counts.csv"),
        "corrections": pd.read_csv(ROOT / "outputs/03_annotation/20261018_annotation/annotation_corrections.csv"),
        "balance": pd.read_csv(ROOT / "outputs/03_annotation/20261018_annotation/annotation_class_balance.csv"),
        "figure": ROOT / "outputs/07_events_timeline/20261019_events/figures/feedback_loop_sequence.png",
    }
