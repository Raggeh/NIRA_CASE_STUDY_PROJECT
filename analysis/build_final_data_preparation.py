"""Link the final annotation workbook to the working corpus.

Writes outputs/01_data_preparation/20261125_final/.
Does not modify the October working corpus or the raw CSV.
"""
import json
import re
from pathlib import Path

import pandas as pd

from load_final_annotation import TASKS, load_final_annotation

ROOT = Path(__file__).resolve().parents[1]
WORKING = ROOT / "outputs/01_data_preparation/20261125_final/raw_corpus_working.csv"
OUT = ROOT / "outputs/01_data_preparation/20261125_final"


def whitespace_norm(text):
    return re.sub(r"\s+", " ", str(text)).strip()


def classify_text(annotated_text, raw_text):
    if annotated_text == raw_text:
        return "exact", "texts are identical"
    if whitespace_norm(annotated_text) == whitespace_norm(raw_text):
        return "newline_or_whitespace", "difference is limited to line breaks or spacing"
    ann_norm = whitespace_norm(annotated_text)
    raw_norm = whitespace_norm(raw_text)
    if "REDACTED" in ann_norm:
        return "content_difference", "annotation redacts material that is present in the raw comment"
    if raw_norm in ann_norm or ann_norm in raw_norm:
        return "content_difference", "one version contains the other plus extra characters"
    if ann_norm.rstrip(".,!") == raw_norm.rstrip(".,!"):
        return "content_difference", "trailing punctuation differs"
    if abs(len(ann_norm) - len(raw_norm)) <= 2:
        return "content_difference", "small character-level difference"
    return "content_difference", "texts differ after whitespace normalisation"


def redact(text):
    return re.sub(r"\d[\d\s\-]{8,}\d", "[PHONE REDACTED]", str(text))


def main():
    labels = load_final_annotation()
    working = pd.read_csv(WORKING, dtype=str, keep_default_na=False)
    labels["record_key"] = (
        labels["post_url"].astype(str).str.strip()
        + "||"
        + labels["comment_id"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    )
    if labels["record_key"].nunique() != 3500:
        raise SystemExit("The final workbook did not produce 3,500 keys.")
    if not set(labels["record_key"]).issubset(set(working["record_key"])):
        raise SystemExit("Some final-annotation keys are missing from the working corpus.")

    keep = [
        "record_key",
        "source_row",
        "comment_original",
        "post_url_stripped",
        "post_id",
    ]
    linked = labels.merge(working[keep], on="record_key", how="left", validate="one_to_one")
    statuses = [
        classify_text(row.comment, row.comment_original)
        for row in linked.itertuples(index=False)
    ]
    linked["text_match_status"] = [item[0] for item in statuses]
    linked["text_difference_note"] = [item[1] for item in statuses]
    linked["raw_collection_date"] = linked["record_key"].map(
        working.set_index("record_key")["collection_date"]
    )
    counts = linked["text_match_status"].value_counts().to_dict()
    expected = {"exact": 3475, "newline_or_whitespace": 12, "content_difference": 13}
    if counts != expected:
        raise SystemExit(f"Text match counts changed: {counts}")

    out_cols = [
        "annotation_id",
        "record_key",
        "source_row",
        "comment_id",
        "post_url_stripped",
        "policy_relevance",
        "feedback_type",
        "topic",
        "sentiment",
        "annotation_status",
        "text_match_status",
        "text_difference_note",
        "collection_date",
        "collection_date_original",
        "raw_collection_date",
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    linked[out_cols].to_csv(OUT / "annotation_linked.csv", index=False, encoding="utf-8-sig")

    mismatch = linked.loc[linked["text_match_status"].ne("exact"), [
        "annotation_id",
        "record_key",
        "source_row",
        "text_match_status",
        "text_difference_note",
        "comment",
        "comment_original",
    ]].copy()
    mismatch["comment"] = mismatch["comment"].map(redact)
    mismatch["comment_original"] = mismatch["comment_original"].map(redact)
    mismatch = mismatch.rename(columns={"comment": "comment_redacted", "comment_original": "raw_comment_redacted"})
    mismatch.to_csv(OUT / "text_mismatch_register.csv", index=False, encoding="utf-8-sig")

    balance_rows = []
    for field in TASKS:
        counts_field = linked[field].value_counts()
        for label, n_comments in counts_field.items():
            balance_rows.append({
                "field": field,
                "label": label,
                "n_comments": int(n_comments),
                "share_of_annotated": float(n_comments) / 3500,
            })
    pd.DataFrame(balance_rows).to_csv(OUT / "annotation_label_counts.csv", index=False)

    by_post = linked.groupby("post_id").size()
    post_n = working.groupby("post_id").size()
    shares = (by_post / post_n.reindex(by_post.index)).astype(float)
    summary = {
        "run_id": "20261125_final",
        "annotation_file": "Annotation Dataset/NIRA_Project_Final_Annotation.xlsx",
        "raw_working_corpus": "outputs/01_data_preparation/20261125_final/raw_corpus_working.csv",
        "annotated_rows": 3500,
        "raw_rows": int(len(working)),
        "keys_matched": 3500,
        "keys_unmatched": 0,
        "text_match": {key: int(counts[key]) for key in expected},
        "annotated_share_of_raw": 3500 / 5292,
        "annotated_share_by_post_min": float(shares.min()),
        "annotated_share_by_post_max": float(shares.max()),
        "actor_column_present": False,
    }
    (OUT / "annotation_link_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "DATA_QUALITY_REPORT.md").write_text(
        "\n".join([
            "# Data preparation — final annotation link",
            "",
            "Run id: `20261125_final`",
            "",
            "The annotation source is `Annotation Dataset/NIRA_Project_Final_Annotation.xlsx`.",
            "The four task columns are the final labels from that workbook.",
            "The raw working corpus was read and not modified:",
            "`outputs/01_data_preparation/20261125_final/raw_corpus_working.csv`.",
            "",
            "- Annotated rows: 3,500. Every row has an annotation id.",
            "- Keys matched to the working corpus: 3,500. Unmatched keys: 0.",
            "- Text comparison: 3,475 exact, 12 spacing only, 13 content differences.",
            "- One content difference is a phone number redacted in the annotation workbook.",
            "- Actor is not a column in the final workbook.",
            f"- Annotated share of the 5,292 comments: {3500 / 5292:.1%}.",
            f"- Annotated share within posts ranges from {shares.min():.1%} to {shares.max():.1%}.",
            "- `collection_date` on the linked rows is the raw collection timestamp, not a publication date.",
            "",
        ]),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
