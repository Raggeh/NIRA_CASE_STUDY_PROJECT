"""Copy the 20261111 topic-model tables into the dashboard schema.

The source run stays in NIRA_CASE_STUDY_PROJECT. This script does not refit
models and does not copy embedding files.
"""

import json
from pathlib import Path

import pandas as pd

SRC = Path(r"D:\NIRA_CASE_STUDY_PROJECT\outputs\04_topic_modeling\20261111_3500")
DST = Path(r"D:\NIRA_CASE_STUDY\outputs\04_topic_modeling\20261111_3500")
FAMILY = {
    "nmf": "NMF",
    "lda": "LDA",
    "lsa": "LSA",
    "kmeans": "K-means",
    "agglomerative": "Agglomerative",
    "hdbscan": "HDBSCAN",
    "bertopic": "BERTopic",
}


def setting(row):
    name = str(row["model"])
    parts = name.split("_k")
    if len(parts) == 2 and parts[1].isdigit():
        label = "k=" + parts[1]
        if row["encoder"] == "bag_of_words":
            return label
        return f"{row['encoder']} {label}"
    return str(row["encoder"])


def main():
    DST.mkdir(parents=True, exist_ok=True)
    selected = json.loads((SRC / "topic_model_selection.json").read_text(encoding="utf-8"))
    winner = selected["winner"]
    payload = {
        "selected_family": "NMF",
        "selected_setting": "k=4",
        "n_topics": int(winner["n_topics"]),
        "coherence_c_npmi": winner["coherence_c_npmi"],
        "topic_diversity": winner["topic_diversity"],
        "coverage": winner["coverage"],
        "outlier_share": winner["outlier_share"],
        "unassigned_comments": int(winner["unassigned_comments"]),
        "comments_in_corpus": int(winner["comments_in_corpus"]),
        "function_words_removed": selected["function_words_removed"],
        "function_word_file": "config/somali_function_words.csv",
        "prior_run": "20261019_topic_models_function_words",
        "selection_rule": selected["selection_rule"],
        "manual_labels_used_as_training_target": False,
        "somali_trained_encoder": False,
        "run_id": "20261111_3500",
        "language_limitation": (
            "The cited model is NMF on bag-of-words counts after the project function-word list was removed. "
            "AfriBERTa and AfroXLMR were in the comparison and had lower c_npmi, so they were not selected. "
            "Coherence does not confirm a public-policy theme. A Somali-trained encoder in the comparison "
            "is not evidence that the cited model understands Somali."
        ),
    }
    (DST / "topic_model_selection.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    comparison = pd.read_csv(SRC / "topic_model_comparison.csv")
    comparison["family"] = comparison["family"].map(FAMILY)
    comparison["setting"] = comparison.apply(setting, axis=1)
    columns = [
        "model",
        "family",
        "setting",
        "encoder",
        "somali_trained_encoder",
        "n_topics",
        "coherence_c_npmi",
        "topic_diversity",
        "coverage",
        "outlier_share",
        "unassigned_comments",
        "comments_in_corpus",
    ]
    comparison[columns].to_csv(DST / "topic_model_comparison.csv", index=False)
    if comparison.duplicated(["family", "setting"]).any():
        raise ValueError("A family and setting pair is not unique.")

    terms = pd.read_csv(SRC / "selected_topic_terms.csv").rename(columns={"terms": "top_terms"})
    terms["provisional_term_label"] = terms["top_terms"].map(
        lambda text: " | ".join(part.strip() for part in str(text).split("|")[:3])
    )
    terms.to_csv(DST / "selected_topic_terms.csv", index=False)

    examples = pd.read_csv(SRC / "top4_examples.csv")
    examples["rank_in_topic"] = examples.groupby("topic_id").cumcount() + 1
    examples[["topic_id", "rank_in_topic", "record_key", "post_id", "excerpt"]].to_csv(
        DST / "selected_topic_examples.csv", index=False
    )

    assignments = pd.read_csv(SRC / "topic_assignments.csv")
    assignments["assignment_status"] = assignments["topic_id"].map(
        lambda value: "unassigned" if int(value) < 0 else "assigned"
    )
    if len(assignments) != 5292:
        raise ValueError(f"Expected 5,292 assignments, found {len(assignments)}")
    unassigned = int((assignments["topic_id"] < 0).sum())
    if unassigned != int(winner["unassigned_comments"]):
        raise ValueError(f"Unassigned count {unassigned} does not match the selection file.")
    assignments.to_csv(DST / "topic_assignments.csv", index=False)
    print(f"wrote {DST} unassigned={unassigned} models={len(comparison)}")


if __name__ == "__main__":
    main()
