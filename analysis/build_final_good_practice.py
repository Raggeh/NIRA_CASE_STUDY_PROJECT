"""One-sheet final file: both annotators, agreement, reason, and final."""
import sys
from pathlib import Path

import pandas as pd
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(r"D:\NIRA_CASE_STUDY\analysis")))
import build_two_annotator_file as rule

OUT = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Final_Good_Practice.xlsx")


def main():
    raise SystemExit(
        "The project annotation is Annotation Dataset/NIRA_Project_Final_Annotation.xlsx."
    )
    raggeh = pd.read_csv(rule.FINAL, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    sodal = rule.read_sodal(rule.SODAL)
    merged = raggeh.merge(sodal, on="annotation_id", suffixes=("_raggeh", "_sodal"))
    if len(merged) != 3500 or not (merged["comment_raggeh"] == merged["comment_sodal"]).all():
        raise SystemExit("the two files do not join on the same 3,500 comments")

    rows = []
    for record in merged.itertuples(index=False):
        flags = rule.evidence(record.comment_raggeh)
        item = {"annotation_id": record.annotation_id, "comment": record.comment_raggeh}
        reasons = []
        for task in rule.TASKS:
            first = getattr(record, task)
            second = getattr(record, f"annotator_2_{task}_sodal").strip()
            chosen, reason = (first, "") if first == second else rule.choose(task, first, second, flags)
            if chosen not in {first, second}:
                raise SystemExit(f"third label created for {record.annotation_id} {task}")
            item[f"annotator_1_{task}"] = first
            item[f"annotator_2_{task}"] = second
            item[f"agree_{task}"] = "yes" if first == second else "no"
            item[f"final_{task}"] = chosen
            if first != second:
                reasons.append(reason)
        item["disagreement_reason"] = " ".join(reasons)
        rows.append(item)

    columns = ["annotation_id", "comment"]
    for task in rule.TASKS:
        columns += [
            f"annotator_1_{task}",
            f"annotator_2_{task}",
            f"agree_{task}",
            f"final_{task}",
        ]
    columns.append("disagreement_reason")
    work = pd.DataFrame(rows)[columns]
    needs = work[[f"agree_{task}" for task in rule.TASKS]].eq("no").any(axis=1)
    if (needs & work["disagreement_reason"].eq("")).any() or ((~needs) & work["disagreement_reason"].ne("")).any():
        raise SystemExit("reasons do not match disagreements")

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        work.to_excel(writer, sheet_name="Annotations", index=False)
        page = writer.book["Annotations"]
        page.freeze_panes = "C2"
        page.auto_filter.ref = "A1:S3501"
        page.row_dimensions[1].height = 32
        page.column_dimensions["A"].width = 16
        page.column_dimensions["B"].width = 52
        page.column_dimensions["S"].width = 78
        header_font = Font(color="FFFFFF", bold=True, name="Calibri")
        fills = {
            "annotator_1": "1F4E99",
            "annotator_2": "2458A8",
            "agree": "0F6B4C",
            "final": "8A5A00",
            "disagreement_reason": "7A3E00",
        }
        for index, name in enumerate(columns, start=1):
            cell = page.cell(1, index)
            cell.font = header_font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            if name == "disagreement_reason":
                key = name
            elif name.startswith("final"):
                key = "final"
            elif name.startswith("agree"):
                key = "agree"
            elif name.startswith("annotator_2"):
                key = "annotator_2"
            else:
                key = "annotator_1"
            cell.fill = PatternFill("solid", fgColor=fills[key])
            if 2 < index < 19:
                page.column_dimensions[get_column_letter(index)].width = 22
        page.cell(1, 19).comment = Comment(
            "Blank when Raggeh and Sodal agree on all four tasks. "
            "Otherwise one sentence for each task that differs. "
            "The final is the shared label when they agree. "
            "When they differ, it is the one of their two labels that the comment wording supports. "
            "If the wording does not separate them, Raggeh's label remains.",
            "NIRA",
            width=280,
            height=120,
        )
        for row in page.iter_rows(min_row=2, max_row=3501, min_col=2, max_col=2):
            cell = row[0]
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cell.data_type = "s"

    print(OUT)
    for task in rule.TASKS:
        agree = work[f"agree_{task}"] == "yes"
        print(
            task,
            int(agree.sum()),
            int((~agree).sum()),
            round(float(agree.mean()), 3),
            rule.kappa(work[f"annotator_1_{task}"].tolist(), work[f"annotator_2_{task}"].tolist()),
        )
    print("reason rows", int(needs.sum()), "blank finals", int(work[[c for c in columns if c.startswith("final")]].eq("").any(axis=1).sum()))


if __name__ == "__main__":
    main()
