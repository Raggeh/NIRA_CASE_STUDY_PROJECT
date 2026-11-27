"""Read the project annotation workbook and attach raw comment keys.

The only annotation file is Annotation Dataset/NIRA_Project_Final_Annotation.xlsx.
The four task columns are the final_ columns in that workbook. comment_id and
post_url are not stored in the workbook, so they are taken from the raw corpus
when the comment text identifies one raw row. A comment string that appears on
more than one post is tied to the row already marked annotated in the final
prediction file. The redacted phone row keeps the record key already stored in
the content-review mismatch register. No Raggeh-only label file is read.
"""
import xml.etree.ElementTree as ET
import zipfile
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "Annotation Dataset" / "NIRA_Project_Final_Annotation.xlsx"
RAW = ROOT / "NIRA_Facebook_Datasets_5292.csv"
LABELED_KEYS = (
    ROOT
    / "outputs/06_results_predictions/20261125_final/corpus_predictions.csv"
)
MISMATCH = (
    ROOT
    / "outputs/01_data_preparation/20261125_final/text_mismatch_register.csv"
)
TASKS = ["policy_relevance", "feedback_type", "topic", "sentiment"]
REDACTED = "[PHONE NUMBER REDACTED]"


def col_index(ref):
    n = 0
    for ch in ref:
        if ch.isalpha():
            n = n * 26 + ord(ch) - 64
        else:
            break
    return n - 1


def normalize(text):
    return " ".join(str(text).replace("\r", " ").replace("\n", " ").split())


def read_workbook(path=FINAL):
    rows = []
    with zipfile.ZipFile(path) as zf, zf.open("xl/worksheets/sheet1.xml") as handle:
        for event, elem in ET.iterparse(handle, events=("end",)):
            if not elem.tag.endswith("row"):
                continue
            values = {}
            for cell in elem:
                if not cell.tag.endswith("c"):
                    continue
                text = "".join(node.text or "" for node in cell.iter() if node.tag.endswith("t"))
                values[col_index(cell.attrib.get("r", ""))] = text
            if values:
                width = max(values) + 1
                rows.append([values.get(i, "") for i in range(width)])
            elem.clear()
    width = max(len(row) for row in rows)
    frame = pd.DataFrame(
        [row + [""] * (width - len(row)) for row in rows[1:]],
        columns=rows[0],
    )
    if len(frame) != 3500 or frame["annotation_id"].nunique() != 3500:
        raise SystemExit("The final workbook is not 3,500 unique annotation ids.")
    return frame


def load_final_annotation():
    labels = read_workbook()
    raw = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    if len(raw) != 5292:
        raise SystemExit("Raw file is not 5,292 comments.")
    raw = raw.reset_index(drop=True)
    raw["source_order"] = raw.index
    raw["norm"] = raw["comment"].map(normalize)
    raw["record_key"] = (
        raw["post_url"].astype(str).str.strip()
        + "||"
        + raw["comment_id"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    )
    predictions = pd.read_csv(LABELED_KEYS, dtype=str, keep_default_na=False)
    labeled_keys = set(predictions.loc[predictions["is_annotated"].eq("True"), "record_key"])
    labels = labels.copy()
    labels["norm"] = labels["comment"].map(normalize)

    assigned = {}
    used = set()

    redacted = labels.index[labels["comment"].str.strip().eq(REDACTED)].tolist()
    if len(redacted) != 1:
        raise SystemExit("Expected one redacted phone row in the final workbook.")
    register = pd.read_csv(MISMATCH, dtype=str, keep_default_na=False)
    redacted_id = labels.at[redacted[0], "annotation_id"]
    key_row = register.loc[register["annotation_id"].eq(redacted_id)]
    if len(key_row) != 1:
        raise SystemExit("The redacted row has no single key in the mismatch register.")
    record_key = key_row.iloc[0]["record_key"]
    url, comment_id = record_key.rsplit("||", 1)
    raw_hit = raw.index[
        raw["post_url"].str.strip().str.rstrip("/").eq(url.rstrip("/"))
        & raw["comment_id"].str.strip().eq(comment_id)
    ]
    if len(raw_hit) != 1:
        raise SystemExit("The redacted row does not match one raw comment.")
    assigned[redacted[0]] = int(raw_hit[0])
    used.add(int(raw_hit[0]))

    raw_groups = {}
    for idx, text in raw["norm"].items():
        if int(idx) in used:
            continue
        raw_groups.setdefault(text, []).append(int(idx))
    ann_groups = {}
    for idx, text in labels["norm"].items():
        if idx in assigned:
            continue
        ann_groups.setdefault(text, []).append(idx)

    pending = []
    for text, ann_indexes in ann_groups.items():
        raw_indexes = raw_groups.get(text, [])
        chosen = raw_indexes
        if len(raw_indexes) > len(ann_indexes):
            chosen = [i for i in raw_indexes if raw.at[i, "record_key"] in labeled_keys]
        if len(chosen) == len(ann_indexes) and chosen:
            ann_indexes = sorted(ann_indexes, key=lambda i: labels.at[i, "annotation_id"])
            chosen = sorted(chosen, key=lambda i: int(raw.at[i, "source_order"]))
            for ann_i, raw_i in zip(ann_indexes, chosen):
                assigned[ann_i] = raw_i
                used.add(raw_i)
        else:
            pending.extend(ann_indexes)

    unused = [i for i in raw.index if int(i) not in used]
    unused_norm = [(int(i), raw.at[i, "norm"]) for i in unused]
    for ann_i in pending:
        text = labels.at[ann_i, "norm"]
        scored = []
        for raw_i, other in unused_norm:
            if abs(len(other) - len(text)) > 80:
                continue
            scored.append((SequenceMatcher(None, text, other).ratio(), raw_i))
        scored.sort(reverse=True)
        if len(scored) < 1 or scored[0][0] < 0.89:
            raise SystemExit(f"{labels.at[ann_i, 'annotation_id']} does not match one raw comment.")
        if len(scored) > 1 and scored[0][0] - scored[1][0] < 0.05:
            raise SystemExit(f"{labels.at[ann_i, 'annotation_id']} matches more than one raw comment.")
        raw_i = scored[0][1]
        assigned[ann_i] = raw_i
        used.add(raw_i)
        unused_norm = [(i, other) for i, other in unused_norm if i != raw_i]

    if len(assigned) != 3500 or len(set(assigned.values())) != 3500:
        raise SystemExit("The workbook did not join to 3,500 different raw comments.")

    out = labels.copy()
    for task in TASKS:
        column = f"final_{task}"
        if out[column].str.strip().eq("").any():
            raise SystemExit(f"{column} has an empty label.")
        out[task] = out[column].str.strip()
    raw_pos = pd.Series(assigned)
    picked = raw.loc[raw_pos.sort_index()].reset_index(drop=True)
    out = out.sort_index().reset_index(drop=True)
    if len(picked) != len(out):
        raise SystemExit("Join alignment failed.")
    out["comment_id"] = picked["comment_id"].astype(str).str.strip().to_numpy()
    out["post_url"] = picked["post_url"].astype(str).to_numpy()
    out["platform"] = picked["platform"].astype(str).to_numpy()
    out["collection_date"] = picked["collection_date"].astype(str).to_numpy()
    out["collection_date_original"] = picked["collection_date"].astype(str).to_numpy()
    out["annotation_status"] = "annotated"
    keep = [
        "annotation_id",
        "comment_id",
        "comment",
        "platform",
        "post_url",
        "collection_date",
        "collection_date_original",
        "policy_relevance",
        "feedback_type",
        "topic",
        "sentiment",
        "annotation_status",
    ]
    return out[keep]
