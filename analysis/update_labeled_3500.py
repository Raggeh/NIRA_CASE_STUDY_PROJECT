"""Recompute annotation-dependent results using the 3,500-row labeled file.

The raw CSV and the original 1,199 workbook are only read. Topic-model files
stay in place because they were fit on the 5,292 comment texts.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from supervised import (
    CLASSICAL_MODEL_NAMES,
    EMBEDDING_MODEL_NAME,
    make_classical_pipeline,
    make_embedding_estimator,
)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "NIRA_Facebook_Datasets_5292.csv"
ANN = ROOT / "Annotation Dataset" / "NIRA_Annotated_Master_3500.csv"
WORKING = ROOT / "outputs/01_data_preparation/20261018_content_review/raw_corpus_working.csv"
EMB = ROOT / "outputs/04_topic_modeling/20261019_topic_models/comment_embeddings.npy"
TOPICS = ROOT / "outputs/04_topic_modeling/20261019_topic_models_function_words/topic_assignments.csv"
EDA_POSTS = ROOT / "outputs/02_eda/20261018_eda/eda_post_summary.csv"
EDA_JSON = ROOT / "outputs/02_eda/20261018_eda/eda_findings.json"
PERIOD_POSTS = ROOT / "outputs/07_events_timeline/20261019_events/posts_by_event_period.csv"
SEED = 42
TASKS = ["policy_relevance", "feedback_type", "topic", "sentiment"]
RUN = "20261111_3500"


def record_key(frame, url_column="post_url"):
    url = frame[url_column].astype(str).str.strip().str.rstrip("/")
    comment_id = frame["comment_id"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return url + "||" + comment_id


def stored_key(frame):
    url = frame["post_url"].astype(str).str.strip()
    comment_id = frame["comment_id"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return url + "||" + comment_id


def score_labels(y_true, y_pred, labels):
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", labels=labels, zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", labels=labels, zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
    }


def fit_task(model_name, x_train, y_train, x_score, emb_train, emb_score):
    if model_name == EMBEDDING_MODEL_NAME:
        scaler = StandardScaler()
        clf = make_embedding_estimator(SEED)
        clf.fit(scaler.fit_transform(emb_train), y_train)
        return clf.predict(scaler.transform(emb_score))
    pipeline = make_classical_pipeline(model_name, SEED)
    pipeline.fit(x_train, y_train)
    return pipeline.predict(x_score)


def main():
    raw = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    ann = pd.read_csv(ANN, dtype=str, keep_default_na=False)
    working = pd.read_csv(WORKING, dtype=str, keep_default_na=False)
    raw["join_key"] = record_key(raw)
    raw["record_key"] = stored_key(raw)
    ann["join_key"] = record_key(ann)
    if len(raw) != 5292 or raw["record_key"].nunique() != 5292:
        raise SystemExit("Raw file is not 5,292 unique comments.")
    if len(ann) != 3500 or ann["join_key"].nunique() != 3500:
        raise SystemExit("Annotated file is not 3,500 unique comments.")
    if not set(ann["join_key"]).issubset(set(raw["join_key"])):
        raise SystemExit("Some annotated keys are missing from the raw file.")
    ann["record_key"] = ann["join_key"].map(raw.drop_duplicates("join_key").set_index("join_key")["record_key"])

    text = working.set_index("record_key")["comment_whitespace_normalized"].astype(str)
    post_id = working.set_index("record_key")["post_id"].astype(str)
    embeddings = np.load(EMB)
    if len(embeddings) != len(working):
        raise SystemExit("Embedding rows do not match the working corpus.")
    emb_by_key = {key: embeddings[i] for i, key in enumerate(working["record_key"].astype(str))}

    labeled_keys = set(ann["record_key"])
    corpus = raw.copy()
    corpus["model_text"] = corpus["record_key"].map(text)
    corpus["post_id"] = corpus["record_key"].map(post_id)
    corpus["is_annotated"] = corpus["record_key"].isin(labeled_keys)
    ann = ann.copy()
    ann["model_text"] = ann["record_key"].map(text)
    ann["post_id"] = ann["record_key"].map(post_id)
    ann["has_annotation_id"] = ann["annotation_id"].str.strip().ne("")
    if ann["model_text"].isna().any():
        raise SystemExit("A labeled row has no working text.")

    sup = ROOT / "outputs/05_model_development" / RUN
    pred = ROOT / "outputs/06_results_predictions" / RUN
    ann_out = ROOT / "outputs/03_annotation" / RUN
    eda_out = ROOT / "outputs/02_eda" / RUN
    event_out = ROOT / "outputs/07_events_timeline" / RUN
    for folder in (sup, pred, ann_out, eda_out, event_out):
        folder.mkdir(parents=True, exist_ok=True)

    validation_rows = []
    test_rows = []
    split_rows = []
    reports = {}
    selected = {}
    winners = {}
    for task in TASKS:
        y = ann[task].astype(str)
        labels = sorted(y.unique())
        index = np.arange(len(ann))
        trainval_index, test_index = train_test_split(index, test_size=0.20, random_state=SEED, stratify=y)
        train_index, val_index = train_test_split(
            trainval_index, test_size=0.125, random_state=SEED, stratify=y.iloc[trainval_index]
        )
        for part_name, part_index in (("train", train_index), ("validation", val_index), ("test", test_index)):
            split_rows.append({"task": task, "split": part_name, "n_rows": int(len(part_index))})
        x_train = ann.loc[train_index, "model_text"]
        x_val = ann.loc[val_index, "model_text"]
        y_train = y.iloc[train_index]
        y_val = y.iloc[val_index]
        emb_train = np.vstack([emb_by_key[key] for key in ann.loc[train_index, "record_key"]])
        emb_val = np.vstack([emb_by_key[key] for key in ann.loc[val_index, "record_key"]])
        task_scores = []
        for model_name in CLASSICAL_MODEL_NAMES + [EMBEDDING_MODEL_NAME]:
            pred_val = fit_task(
                model_name, x_train, y_train, x_val,
                emb_train, emb_val,
            )
            scored = score_labels(y_val, pred_val, labels)
            task_scores.append({"task": task, "model": model_name, **scored})
            print(task, model_name, round(scored["macro_f1"], 4), flush=True)
        score_frame = pd.DataFrame(task_scores).sort_values(
            ["macro_f1", "weighted_f1", "model"], ascending=[False, False, True]
        ).reset_index(drop=True)
        validation_rows.extend(score_frame.to_dict("records"))
        winner_name = score_frame.loc[0, "model"]
        winners[task] = winner_name
        x_test = ann.loc[test_index, "model_text"]
        emb_test = np.vstack([emb_by_key[key] for key in ann.loc[test_index, "record_key"]])
        y_test_pred = fit_task(winner_name, x_train, y_train, x_test, emb_train, emb_test)
        y_test = y.iloc[test_index]
        held_out = score_labels(y_test, y_test_pred, labels)
        test_rows.append({
            "task": task,
            "selected_model": winner_name,
            "validation_macro_f1": float(score_frame.loc[0, "macro_f1"]),
            "validation_weighted_f1": float(score_frame.loc[0, "weighted_f1"]),
            "test_macro_f1": held_out["macro_f1"],
            "test_weighted_f1": held_out["weighted_f1"],
            "test_accuracy": held_out["accuracy"],
            "test_used_for_selection": False,
        })
        matrix = confusion_matrix(y_test, y_test_pred, labels=labels)
        pd.DataFrame(matrix, index=labels, columns=labels).to_csv(sup / f"test_confusion_{task}.csv")
        reports[task] = classification_report(y_test, y_test_pred, labels=labels, output_dict=True, zero_division=0)
        selected[task] = {
            "model": winner_name,
            "validation_macro_f1": float(score_frame.loc[0, "macro_f1"]),
            "test_macro_f1": held_out["macro_f1"],
            "n_classes": len(labels),
            "classes": labels,
        }
        print("SELECTED", task, winner_name, round(held_out["macro_f1"], 4), flush=True)

    pd.DataFrame(validation_rows).to_csv(sup / "validation_scores.csv", index=False)
    pd.DataFrame(test_rows).to_csv(sup / "heldout_test_scores.csv", index=False)
    pd.DataFrame(split_rows).to_csv(sup / "split_sizes.csv", index=False)
    (sup / "heldout_classification_reports.json").write_text(json.dumps(reports), encoding="utf-8")
    (sup / "selected_models.json").write_text(json.dumps({
        "seed": SEED,
        "split": "stratified 70 percent train, 10 percent validation, 20 percent test",
        "selection_metric": "validation macro-F1",
        "test_used_for_selection": False,
        "labeled_rows": 3500,
        "rows_with_annotation_id": int(ann["has_annotation_id"].sum()),
        "rows_without_annotation_id": int((~ann["has_annotation_id"]).sum()),
        "model_text": "comment_whitespace_normalized from the raw working corpus",
        "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
        "language_limitation": "Embedding scores do not establish that the multilingual model understands Somali.",
        "tasks": selected,
    }, indent=2), encoding="utf-8")

    refit_rows = []
    distribution = []
    pred_frame = corpus[["record_key", "post_id", "is_annotated"]].copy()
    source_row = working.set_index("record_key")["source_row"].astype(str)
    pred_frame.insert(0, "source_row", pred_frame["record_key"].map(source_row))
    for task in TASKS:
        labels = sorted(ann[task].astype(str).unique())
        winner_name = winners[task]
        y_all = ann[task].astype(str)
        emb_all = np.vstack([emb_by_key[key] for key in ann["record_key"]])
        emb_corpus = np.vstack([emb_by_key[key] for key in corpus["record_key"]])
        pred_on_labeled = fit_task(winner_name, ann["model_text"], y_all, ann["model_text"], emb_all, emb_all)
        pred_corpus = fit_task(winner_name, ann["model_text"], y_all, corpus["model_text"], emb_all, emb_corpus)
        agreement = score_labels(y_all, pred_on_labeled, labels)
        test_row = next(row for row in test_rows if row["task"] == task)
        refit_rows.append({
            "task": task,
            "selected_model": winner_name,
            "heldout_test_macro_f1": test_row["test_macro_f1"],
            "refit_agreement_macro_f1": agreement["macro_f1"],
            "refit_agreement_accuracy": agreement["accuracy"],
            "note": "Calculated after refitting on all 3,500 labeled rows. This is not a held-out test score.",
        })
        pred_frame[f"pred_{task}"] = pred_corpus
        for scope, series, denom in (
            ("manual_annotated", y_all, len(y_all)),
            ("refit_prediction_on_annotated", pd.Series(pred_on_labeled), len(y_all)),
            ("refit_prediction_on_all_comments", pd.Series(pred_corpus), len(pred_corpus)),
        ):
            counts = pd.Series(series).astype(str).value_counts()
            for label, count in counts.items():
                distribution.append({
                    "task": task,
                    "scope": scope,
                    "label": label,
                    "n": int(count),
                    "denominator": int(denom),
                    "share": float(count) / float(denom),
                })
        print("REFIT", task, round(agreement["macro_f1"], 4), flush=True)
    pd.DataFrame(refit_rows).to_csv(pred / "refit_agreement.csv", index=False)
    pred_frame.to_csv(pred / "corpus_predictions.csv", index=False)
    pd.DataFrame(distribution).to_csv(pred / "label_distribution_comparison.csv", index=False)

    unlabeled = corpus.loc[~corpus["is_annotated"]].copy()
    comparison = []
    for task in TASKS:
        y = ann[task].astype(str)
        labels = sorted(y.unique())
        index = np.arange(len(ann))
        trainval_index, test_index = train_test_split(index, test_size=0.20, random_state=SEED, stratify=y)
        train_index, _val_index = train_test_split(
            trainval_index, test_size=0.125, random_state=SEED, stratify=y.iloc[trainval_index]
        )
        winner_name = winners[task]
        train_text = ann.loc[train_index, "model_text"]
        y_train = y.iloc[train_index]
        emb_train = np.vstack([emb_by_key[key] for key in ann.loc[train_index, "record_key"]])
        emb_unlabeled = np.vstack([emb_by_key[key] for key in unlabeled["record_key"]])
        emb_test = np.vstack([emb_by_key[key] for key in ann.loc[test_index, "record_key"]])
        emb_labeled = np.vstack([emb_by_key[key] for key in ann["record_key"]])
        unlabeled_pred = fit_task(
            winner_name, train_text, y_train, unlabeled["model_text"], emb_train, emb_unlabeled
        )
        pseudo_text = pd.concat([train_text, unlabeled["model_text"]], ignore_index=True)
        pseudo_y = pd.concat([y_train, pd.Series(unlabeled_pred)], ignore_index=True)
        emb_pseudo = np.vstack([emb_train, emb_unlabeled])
        pseudo_test = fit_task(winner_name, pseudo_text, pseudo_y, ann.loc[test_index, "model_text"], emb_pseudo, emb_test)
        pseudo_scores = score_labels(y.iloc[test_index], pseudo_test, labels)
        combined_text = pd.concat([ann["model_text"], unlabeled["model_text"]], ignore_index=True)
        combined_y = pd.concat([y, pd.Series(unlabeled_pred)], ignore_index=True)
        emb_combined = np.vstack([emb_labeled, emb_unlabeled])
        combined_pred = fit_task(winner_name, combined_text, combined_y, ann["model_text"], emb_combined, emb_labeled)
        combined_scores = score_labels(y, combined_pred, labels)
        original = next(row for row in test_rows if row["task"] == task)
        comparison.append({
            "task": task,
            "selected_model": winner_name,
            "original_test_macro_f1": original["test_macro_f1"],
            "pseudo_heldout_test_macro_f1": pseudo_scores["macro_f1"],
            "combined_agreement_macro_f1": combined_scores["macro_f1"],
            "unlabeled_rows": int(len(unlabeled)),
            "labeled_rows": 3500,
            "note": "Combined agreement uses the labeled rows in training. It is not a test score.",
        })
    pd.DataFrame(comparison).to_csv(pred / "comparison.csv", index=False)

    topic = pd.read_csv(TOPICS, dtype=str, keep_default_na=False).set_index("record_key")
    rng = np.random.RandomState(SEED)
    annotated_keys = corpus.loc[corpus["is_annotated"], "record_key"].to_numpy()
    unlabeled_keys = corpus.loc[~corpus["is_annotated"], "record_key"].to_numpy()
    picked = list(rng.choice(annotated_keys, 10, replace=False))
    picked += list(rng.choice(unlabeled_keys, 10, replace=False))
    remaining = corpus.loc[~corpus["record_key"].isin(picked), "record_key"].to_numpy()
    picked += list(rng.choice(remaining, 10, replace=False))
    groups = (["annotated_manual_vs_predicted"] * 10) + (["unlabeled_raw_with_prediction"] * 10) + (["additional_predicted_comments"] * 10)
    manual = ann.set_index("record_key")
    sample_rows = []
    for key, group in zip(picked, groups):
        row = corpus.loc[corpus["record_key"] == key].iloc[0]
        sample_rows.append({
            "record_key": key,
            "post_id": row["post_id"],
            "is_annotated": bool(row["is_annotated"]),
            "sample_group": group,
            **{f"pred_{task}": pred_frame.loc[pred_frame["record_key"] == key, f"pred_{task}"].iloc[0] for task in TASKS},
            **{f"manual_{task}": manual.loc[key, task] if key in manual.index else "" for task in TASKS},
            "excerpt": str(row["comment"])[:240],
            "unsupervised_topic_id": topic.loc[key, "topic_id"],
            "unsupervised_topic_terms": topic.loc[key, "topic_terms"],
        })
    sample = pd.DataFrame(sample_rows)
    if len(sample) != 30 or sample["record_key"].nunique() != 30:
        raise SystemExit("Sample is not 30 unique comments.")
    sample.to_csv(pred / "comment_comparison_sample.csv", index=False)
    (pred / "sample_overlap.json").write_text(json.dumps({
        "unique_record_keys": 30,
        "overlap_between_samples": 0,
    }), encoding="utf-8")

    raw_text = raw.set_index("record_key")["comment"].astype(str)
    ann_text = ann.set_index("record_key")["comment"].astype(str)
    exact = int((ann_text == raw_text.reindex(ann_text.index)).sum())
    ws = int((
        ann_text.str.replace(r"\s+", " ", regex=True).str.strip()
        == raw_text.reindex(ann_text.index).str.replace(r"\s+", " ", regex=True).str.strip()
    ).sum())
    pd.DataFrame([
        {"match": "exact", "n": exact},
        {"match": "newline_or_whitespace", "n": ws - exact},
        {"match": "content_difference", "n": len(ann) - ws},
    ]).to_csv(ann_out / "annotation_text_match_counts.csv", index=False)
    balance = []
    for field in TASKS + ["actor"]:
        counts = ann[field].astype(str).value_counts()
        balance.append({
            "field": field,
            "n_classes": int(counts.size),
            "largest_class": counts.index[0],
            "largest_n": int(counts.iloc[0]),
            "smallest_class": counts.index[-1],
            "smallest_n": int(counts.iloc[-1]),
            "largest_share_of_annotated": float(counts.iloc[0]) / float(len(ann)),
        })
    pd.DataFrame(balance).to_csv(ann_out / "annotation_class_balance.csv", index=False)
    (ann_out / "annotation_relation.json").write_text(json.dumps({
        "annotated_rows": 3500,
        "raw_rows": 5292,
        "annotated_share_of_raw_comments": 3500 / 5292,
        "keys_matched": 3500,
        "keys_unmatched": 0,
        "rows_with_annotation_id": int(ann["has_annotation_id"].sum()),
        "rows_without_annotation_id": int((~ann["has_annotation_id"]).sum()),
    }, indent=2), encoding="utf-8")
    pd.DataFrame([{"correction": "none in the 3500 file"}]).to_csv(ann_out / "annotation_corrections.csv", index=False)

    posts = pd.read_csv(EDA_POSTS)
    counts = ann.groupby("post_id").size()
    posts["n_annotated"] = posts["post_id"].map(counts).fillna(0).astype(int)
    posts["annotated_share_of_post"] = posts["n_annotated"] / posts["n_comments"]
    posts.to_csv(eda_out / "eda_post_summary.csv", index=False)
    findings = json.loads(EDA_JSON.read_text(encoding="utf-8"))
    findings["run_id"] = RUN
    findings["annotated_comments"] = 3500
    findings["annotated_share_of_raw"] = 3500 / 5292
    findings["annotated_share_by_post_min"] = float(posts["annotated_share_of_post"].min())
    findings["annotated_share_by_post_max"] = float(posts["annotated_share_of_post"].max())
    findings["rows_with_annotation_id"] = int(ann["has_annotation_id"].sum())
    findings["rows_without_annotation_id"] = int((~ann["has_annotation_id"]).sum())
    findings["dominant_labels"] = {
        row["field"]: {"label": row["largest_class"], "n_comments": row["largest_n"]}
        for row in balance
        if row["field"] != "actor"
    }
    (eda_out / "eda_findings.json").write_text(json.dumps(findings, indent=2), encoding="utf-8")

    period_posts = pd.read_csv(PERIOD_POSTS)
    period_posts = period_posts.merge(posts[["post_id", "n_annotated"]], on="post_id", how="left")
    summary = (
        period_posts.groupby("event_period", as_index=False)
        .agg(n_posts=("post_id", "nunique"), n_comments=("n_comments", "sum"), n_annotated=("n_annotated", "sum"))
    )
    summary.insert(0, "event_id", "RESP_001")
    summary.insert(1, "event_date", "2025-11-03")
    order = {"pre_event": 0, "event_day": 1, "post_event": 2}
    summary = summary.sort_values("event_period", key=lambda s: s.map(order))
    summary.to_csv(event_out / "event_period_summary.csv", index=False)
    period_by_post = period_posts.set_index("post_id")["event_period"]
    pred_frame["event_period"] = pred_frame["post_id"].map(period_by_post)
    shares = []
    for period_name, part in pred_frame.groupby("event_period"):
        for task in TASKS:
            counts = part[f"pred_{task}"].astype(str).value_counts()
            for label, count in counts.items():
                shares.append({
                    "event_period": period_name,
                    "task": task,
                    "label": label,
                    "n": int(count),
                    "denominator": int(len(part)),
                    "share": float(count) / float(len(part)),
                    "label_source": "refit prediction on the 3500 labeled rows, not a manual label and not an effect of the event",
                })
    pd.DataFrame(shares).to_csv(event_out / "predicted_label_shares_by_event_period.csv", index=False)

    print("wrote", RUN)
    print(pd.DataFrame(test_rows)[["task", "selected_model", "test_macro_f1"]].to_string(index=False))


if __name__ == "__main__":
    main()
