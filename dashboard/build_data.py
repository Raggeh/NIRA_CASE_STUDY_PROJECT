"""Build dashboard/data.js from the saved project outputs. Does not refit models."""

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:\NIRA_CASE_STUDY")
OUT = ROOT / "dashboard" / "data.js"
PHONE = re.compile(
    r"(?i)(?:\+?252[\s\-]?\d[\d\s\-]{6,}\d|\btell\s*:\s*\+?\d[\d\s\-]+|\b\d{10,15}\b)"
)

eda = json.loads((ROOT / "outputs/02_eda/20261018_eda/eda_findings.json").read_text(encoding="utf-8"))
posts = pd.read_csv(ROOT / "outputs/02_eda/20261018_eda/eda_post_summary.csv")
timeline = pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/post_timeline.csv")
periods = pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/posts_by_event_period.csv")
period_summary = pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/event_period_summary.csv")
period_shares = pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/predicted_label_shares_by_event_period.csv")
linkage = pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/linkage_class_counts.csv")
responses = pd.read_csv(ROOT / "outputs/07_events_timeline/20261019_events/response_inventory_timeline.csv")
selection = json.loads(
    (ROOT / "outputs/04_topic_modeling/20261019_topic_models_function_words/topic_model_selection.json").read_text(encoding="utf-8")
)
topic_comparison = pd.read_csv(
    ROOT / "outputs/04_topic_modeling/20261019_topic_models_function_words/topic_model_comparison.csv"
)
topic_terms = pd.read_csv(
    ROOT / "outputs/04_topic_modeling/20261019_topic_models_function_words/selected_topic_terms.csv"
)
validation = pd.read_csv(ROOT / "outputs/05_model_development/20261019_supervised/validation_scores.csv")
heldout = pd.read_csv(ROOT / "outputs/05_model_development/20261019_supervised/heldout_test_scores.csv")
selected = json.loads(
    (ROOT / "outputs/05_model_development/20261019_supervised/selected_models.json").read_text(encoding="utf-8")
)
refit = pd.read_csv(ROOT / "outputs/06_results_predictions/20261019_predictions/refit_agreement.csv")
distribution = pd.read_csv(ROOT / "outputs/06_results_predictions/20261019_predictions/label_distribution_comparison.csv")
sample = pd.read_csv(ROOT / "outputs/06_results_predictions/20261019_predictions/comment_comparison_sample.csv")
overlap = json.loads(
    (ROOT / "outputs/06_results_predictions/20261019_predictions/sample_overlap.json").read_text(encoding="utf-8")
)
lengths = pd.read_csv(ROOT / "outputs/02_eda/20261018_eda/eda_length_summary.csv")
text_match = pd.read_csv(ROOT / "outputs/03_annotation/20261018_annotation/annotation_text_match_counts.csv")
corrections = pd.read_csv(ROOT / "outputs/03_annotation/20261018_annotation/annotation_corrections.csv")
balance = pd.read_csv(ROOT / "outputs/03_annotation/20261018_annotation/annotation_class_balance.csv")

if len(sample) != 30 or sample["record_key"].nunique() != 30:
    raise SystemExit(f"Expected 30 unique comparison comments, found {len(sample)}")
if set(selected["tasks"]) != {"policy_relevance", "feedback_type", "topic", "sentiment"}:
    raise SystemExit("Selected supervised tasks changed.")

joined = posts.merge(
    timeline[["post_id", "linkage_class", "comparison_response_ids", "policy_topic"]],
    on="post_id",
    how="left",
).merge(
    periods[["post_id", "event_period"]],
    on="post_id",
    how="left",
)
joined["publication_date_register"] = joined["publication_date_register"].astype(str).str.slice(0, 10)

comments = []
for row in sample.itertuples(index=False):
    excerpt = PHONE.sub("[PHONE REDACTED]", str(row.excerpt))
    comments.append(
        {
            "post_id": row.post_id,
            "is_annotated": bool(row.is_annotated),
            "sample_group": row.sample_group,
            "excerpt": excerpt,
            "manual": {
                "policy_relevance": None if pd.isna(row.manual_policy_relevance) else row.manual_policy_relevance,
                "feedback_type": None if pd.isna(row.manual_feedback_type) else row.manual_feedback_type,
                "topic": None if pd.isna(row.manual_topic) else row.manual_topic,
                "sentiment": None if pd.isna(row.manual_sentiment) else row.manual_sentiment,
            },
            "predicted": {
                "policy_relevance": row.pred_policy_relevance,
                "feedback_type": row.pred_feedback_type,
                "topic": row.pred_topic,
                "sentiment": row.pred_sentiment,
            },
            "unsupervised_topic_id": None if pd.isna(row.unsupervised_topic_id) else int(row.unsupervised_topic_id),
            "unsupervised_topic_terms": row.unsupervised_topic_terms,
        }
    )

confusion = {}
for task in ["policy_relevance", "feedback_type", "topic", "sentiment"]:
    frame = pd.read_csv(ROOT / f"outputs/05_model_development/20261019_supervised/test_confusion_{task}.csv", index_col=0)
    confusion[task] = {"labels": list(frame.columns), "rows": frame.values.tolist()}

payload = {
    "author": "Ahmed Abdi Rage",
    "overview": {
        "raw_comments": int(eda["raw_comments"]),
        "annotated_comments": int(eda["annotated_comments"]),
        "source_posts": int(eda["source_posts"]),
        "annotated_share": float(eda["annotated_share_of_raw"]),
        "selected_topic": f"{selection['selected_family']} {selection['selected_setting']}",
        "selected_models": {task: body["model"] for task, body in selected["tasks"].items()},
    },
    "exploration": {
        "collection_days": eda["collection_days"],
        "publication_years": eda["publication_year_comment_counts"],
        "lengths": lengths.to_dict(orient="records"),
        "posts": joined.sort_values("publication_date_register").to_dict(orient="records"),
        "annotated_share_min": float(eda["annotated_share_by_post_min"]),
        "annotated_share_max": float(eda["annotated_share_by_post_max"]),
    },
    "topics": {
        "selection": selection,
        "comparison": topic_comparison.to_dict(orient="records"),
        "terms": topic_terms.to_dict(orient="records"),
    },
    "classification": {
        "selection_rule": selected,
        "validation": validation.to_dict(orient="records"),
        "heldout": heldout.to_dict(orient="records"),
        "refit": refit.to_dict(orient="records"),
        "distribution": distribution.to_dict(orient="records"),
        "confusion": confusion,
        "comments": comments,
        "overlap": overlap,
    },
    "loop": {
        "linkage": linkage.to_dict(orient="records"),
        "periods": period_summary.to_dict(orient="records"),
        "responses": responses[["response_id", "source", "date", "title"]].to_dict(orient="records"),
        "shares": period_shares.to_dict(orient="records"),
        "named_posts": timeline.loc[
            timeline["comparison_response_ids"].fillna("").str.len() > 0,
            ["post_id", "publication_date", "account_name", "n_comments", "linkage_class", "comparison_response_ids", "policy_topic"],
        ].to_dict(orient="records"),
    },
    "quality": {
        "text_match": text_match.to_dict(orient="records"),
        "corrections": corrections.to_dict(orient="records"),
        "balance": balance.to_dict(orient="records"),
        "phone_like_raw": int(lengths.loc[lengths["group"] == "raw_corpus", "phone_like"].iloc[0]),
        "arabic_raw": int(lengths.loc[lengths["group"] == "raw_corpus", "arabic_script"].iloc[0]),
        "styled_latin_raw": int(lengths.loc[lengths["group"] == "raw_corpus", "styled_latin"].iloc[0]),
    },
}

OUT.write_text("window.NIRA = " + json.dumps(payload, ensure_ascii=False) + ";\n", encoding="utf-8")
print(f"comments {len(comments)} models {payload['overview']['selected_models']}")
