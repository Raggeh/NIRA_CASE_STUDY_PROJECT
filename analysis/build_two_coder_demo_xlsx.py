"""Practice workbook with three working groups.

Annotations sheet: annotator 2 labels, agreement, and the final labels used
for model training. Annotator 1 stays on its own sheet so the working view
stays narrow.
"""

from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sklearn.metrics import cohen_kappa_score

FINAL = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Project_Final_Annotation.xlsx")
OUT = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Annotation_Two_Coder_Practice_v2.xlsx")
TASKS = ["policy_relevance", "feedback_type", "topic", "sentiment"]


def main():
    raise SystemExit(
        "The project annotation is Annotation Dataset/NIRA_Project_Final_Annotation.xlsx."
    )
    source = pd.read_csv(FINAL, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if len(source) != 3500:
        raise SystemExit(f"expected 3500 rows, found {len(source)}")

    work_rows = []
    first_rows = []
    key_rows = []
    for row in source.itertuples(index=False):
        record = {"annotation_id": row.annotation_id, "comment": row.comment}
        first = {"annotation_id": row.annotation_id}
        for task in TASKS:
            label_1 = getattr(row, task)
            label_2 = getattr(row, f"annotator_2_{task}")
            record[f"annotator_2_{task}"] = label_2
            record[f"agree_{task}"] = "yes" if label_1 == label_2 else "no"
            record[f"final_for_modeling_{task}"] = label_1 if label_1 == label_2 else ""
            first[f"annotator_1_{task}"] = label_1
        record["disagreement_reason"] = ""
        work_rows.append(record)
        first_rows.append(first)
        key_rows.append({
            "annotation_id": row.annotation_id,
            "comment_id": row.comment_id,
            "post_url": row.post_url,
            "actor_1": row.actor,
        })

    columns = ["annotation_id", "comment"]
    columns += [f"annotator_2_{task}" for task in TASKS]
    columns += [f"agree_{task}" for task in TASKS]
    columns.append("disagreement_reason")
    columns += [f"final_for_modeling_{task}" for task in TASKS]
    work = pd.DataFrame(work_rows)[columns]
    annotator_1 = pd.DataFrame(first_rows)
    keys = pd.DataFrame(key_rows)

    summary_rows = []
    for task in TASKS:
        agree = work[f"agree_{task}"] == "yes"
        summary_rows.append({
            "task": task,
            "n": 3500,
            "n_agree": int(agree.sum()),
            "n_disagree": int((~agree).sum()),
            "percent_agreement": round(float(agree.mean()), 3),
            "cohens_kappa": round(float(cohen_kappa_score(annotator_1[f"annotator_1_{task}"], work[f"annotator_2_{task}"])), 3),
            "final_filled": int((work[f"final_for_modeling_{task}"] != "").sum()),
            "final_pending": int((work[f"final_for_modeling_{task}"] == "").sum()),
        })
    summary = pd.DataFrame(summary_rows)
    notes = pd.DataFrame([
        ["annotator_1", "Raggeh. Labels are on the Annotator 1 sheet."],
        ["annotator_2", "Sodal. Labels are the annotator_2 columns. This reading did not copy annotator 1."],
        ["annotator_2_blind", "yes"],
        ["agreement", "yes means the two labels match. no means they differ."],
        ["model training", "Train on the four final_for_modeling columns. Fill the yellow cells before training."],
        ["disagreement_reason", "Leave blank when every agree column is yes. When one is no, write one short reason for the final label."],
        ["actor", "Only annotator 1 has an actor label. It is on the Keys sheet and is not a training task."],
    ], columns=["item", "value"])

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        work.to_excel(writer, sheet_name="Annotations", index=False)
        annotator_1.to_excel(writer, sheet_name="Annotator 1", index=False)
        summary.to_excel(writer, sheet_name="Agreement", index=False)
        keys.to_excel(writer, sheet_name="Keys", index=False)
        notes.to_excel(writer, sheet_name="Notes", index=False)
        header_fill = PatternFill("solid", fgColor="1F4E99")
        header_font = Font(color="FFFFFF", bold=True, name="Calibri")
        group_fills = {
            "annotator_2": PatternFill("solid", fgColor="1F4E99"),
            "agree": PatternFill("solid", fgColor="0F6B4C"),
            "final": PatternFill("solid", fgColor="8A5A00"),
        }
        pending_fill = PatternFill("solid", fgColor="FFF4CC")
        annotations = writer.book["Annotations"]
        annotations.freeze_panes = "C2"
        annotations.auto_filter.ref = f"A1:{get_column_letter(len(columns))}3501"
        annotations.column_dimensions["A"].width = 16
        annotations.column_dimensions["B"].width = 56
        for index, name in enumerate(columns, start=1):
            cell = annotations.cell(1, index)
            cell.font = header_font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            if name.startswith("annotator_2"):
                cell.fill = group_fills["annotator_2"]
            elif name.startswith("agree"):
                cell.fill = group_fills["agree"]
            elif name.startswith("final_for_modeling"):
                cell.fill = group_fills["final"]
            else:
                cell.fill = header_fill
            if index > 2:
                annotations.column_dimensions[get_column_letter(index)].width = 20
        final_indexes = [columns.index(f"final_for_modeling_{task}") + 1 for task in TASKS]
        for excel_row, record in enumerate(work.itertuples(index=False), start=2):
            values = list(record)
            for column in final_indexes:
                if values[column - 1] == "":
                    annotations.cell(excel_row, column).fill = pending_fill
        for name, width in (("Annotator 1", 24), ("Agreement", 24), ("Keys", 36), ("Notes", 88)):
            page = writer.book[name]
            page.freeze_panes = "A2"
            for cell in page[1]:
                cell.fill = header_fill
                cell.font = header_font
            for column in page.columns:
                page.column_dimensions[column[0].column_letter].width = width

    print(OUT)
    print("columns", columns)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
