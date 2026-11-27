"""Simple agreement file for Raggeh and Sodal.

Where the two labels match, that label is the final.
Where they differ, Raggeh's label is the final.
The final is therefore Raggeh's label on every row.
"""
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

FINAL = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Project_Final_Annotation.xlsx")
SODAL = Path(r"C:\Users\xaale\Downloads\NIRA_Sodal_Annotated.xlsx")
OUT = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Simple_Agreement_Final.xlsx")
TASKS = ["policy_relevance", "feedback_type", "topic", "sentiment"]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def kappa(left, right):
    n = len(left)
    labels = sorted(set(left) | set(right))
    po = sum(a == b for a, b in zip(left, right)) / n
    pe = sum((left.count(label) / n) * (right.count(label) / n) for label in labels)
    return 1.0 if pe == 1 else round((po - pe) / (1 - pe), 3)


def col_index(ref):
    letters = "".join(ch for ch in ref if ch.isalpha())
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_sodal(path):
    rows = []
    with zipfile.ZipFile(path) as zf, zf.open("xl/worksheets/sheet1.xml") as handle:
        for event, elem in ET.iterparse(handle, events=("end",)):
            if elem.tag != "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row":
                continue
            values = {}
            for cell in elem.findall("m:c", NS):
                text = "".join(node.text or "" for node in cell.findall(".//m:t", NS))
                if not text and cell.attrib.get("t") != "inlineStr":
                    value = cell.find("m:v", NS)
                    text = "" if value is None or value.text is None else value.text
                values[col_index(cell.attrib.get("r", ""))] = text
            if values:
                width = max(values) + 1
                rows.append([values.get(i, "") for i in range(width)])
            elem.clear()
    width = max(len(row) for row in rows)
    header = rows[0]
    body = [row + [""] * (width - len(row)) for row in rows[1:]]
    return pd.DataFrame(body, columns=header)


def main():
    raise SystemExit(
        "The project annotation is Annotation Dataset/NIRA_Project_Final_Annotation.xlsx."
    )
    raggeh = pd.read_csv(FINAL, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    sodal = read_sodal(SODAL)
    merged = raggeh.merge(sodal, on="annotation_id", suffixes=("_raggeh", "_sodal"))
    if len(merged) != 3500:
        raise SystemExit(f"join has {len(merged)} rows")
    if not (merged["comment_raggeh"] == merged["comment_sodal"]).all():
        raise SystemExit("comment text differs")

    rows = []
    for record in merged.itertuples(index=False):
        item = {"annotation_id": record.annotation_id, "comment": record.comment_raggeh}
        for task in TASKS:
            first = getattr(record, task)
            second = getattr(record, f"annotator_2_{task}_sodal").strip()
            item[f"annotator_1_{task}"] = first
            item[f"annotator_2_{task}"] = second
            item[f"agree_{task}"] = "yes" if first == second else "no"
            item[f"final_{task}"] = first
        rows.append(item)

    columns = ["annotation_id", "comment"]
    for task in TASKS:
        columns += [f"annotator_1_{task}", f"annotator_2_{task}", f"agree_{task}", f"final_{task}"]
    work = pd.DataFrame(rows)[columns]
    for task in TASKS:
        if not (work[f"final_{task}"] == work[f"annotator_1_{task}"]).all():
            raise SystemExit(f"final changed for {task}")

    summary = []
    for task in TASKS:
        agree = work[f"agree_{task}"] == "yes"
        summary.append({
            "task": task,
            "n": 3500,
            "n_agree": int(agree.sum()),
            "n_disagree": int((~agree).sum()),
            "percent_agreement": round(float(agree.mean()), 3),
            "cohens_kappa": kappa(work[f"annotator_1_{task}"].tolist(), work[f"annotator_2_{task}"].tolist()),
        })
    notes = pd.DataFrame(
        [
            ["annotator_1", "Raggeh. The project file is NIRA_Project_Final_Annotation.xlsx."],
            ["annotator_2", "Sodal, from NIRA_Sodal_Annotated.xlsx."],
            ["agree", "yes means both wrote the same label. no means they wrote different labels."],
            ["final", "The final is Raggeh's label on every row. Where they agree, that is also Sodal's label. Where they differ, Raggeh's label is kept."],
            ["four tasks", "policy relevance, feedback type, topic, and sentiment."],
            ["actor", "Sodal did not code actor. It is not in this file."],
        ],
        columns=["item", "value"],
    )

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        work.to_excel(writer, sheet_name="Annotations", index=False)
        pd.DataFrame(summary).to_excel(writer, sheet_name="Agreement", index=False)
        notes.to_excel(writer, sheet_name="Notes", index=False)
        page = writer.book["Annotations"]
        page.freeze_panes = "C2"
        page.auto_filter.ref = "A1:R3501"
        page.column_dimensions["A"].width = 16
        page.column_dimensions["B"].width = 56
        header_font = Font(color="FFFFFF", bold=True, name="Calibri")
        fills = {
            "annotator_1": PatternFill("solid", fgColor="1F4E99"),
            "annotator_2": PatternFill("solid", fgColor="2458A8"),
            "agree": PatternFill("solid", fgColor="0F6B4C"),
            "final": PatternFill("solid", fgColor="8A5A00"),
        }
        for index, name in enumerate(columns, start=1):
            cell = page.cell(1, index)
            cell.font = header_font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            if name.startswith("final"):
                cell.fill = fills["final"]
            elif name.startswith("agree"):
                cell.fill = fills["agree"]
            elif name.startswith("annotator_2"):
                cell.fill = fills["annotator_2"]
            else:
                cell.fill = fills["annotator_1"]
            if index > 2:
                page.column_dimensions[get_column_letter(index)].width = 24
        for row in page.iter_rows(min_row=2, max_row=3501, min_col=2, max_col=2):
            cell = row[0]
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cell.data_type = "s"
        for name, width in (("Agreement", 24), ("Notes", 110)):
            sheet = writer.book[name]
            sheet.freeze_panes = "A2"
            sheet.column_dimensions["A"].width = 22
            sheet.column_dimensions["B"].width = width

    print(OUT)
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()
