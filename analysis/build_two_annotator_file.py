"""Join Raggeh and Sodal, then choose a final only from those two labels.

Agreed cells keep the shared label. Disagreed cells keep the label the comment
wording supports. If both labels fit, or neither does, Raggeh's label remains.
No third label is created. This is not a third annotator.
"""
import importlib.util
import sys
import types
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

fake = types.ModuleType("sklearn")
fake_metrics = types.ModuleType("sklearn.metrics")
fake_metrics.cohen_kappa_score = lambda *a, **k: 0.0
sys.modules.setdefault("sklearn", fake)
sys.modules.setdefault("sklearn.metrics", fake_metrics)
spec = importlib.util.spec_from_file_location(
    "demo_reader_plain",
    Path(r"D:\NIRA_CASE_STUDY\analysis\demo_annotator_2.py"),
)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

FINAL = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Project_Final_Annotation.xlsx")
SODAL = Path(r"C:\Users\xaale\Downloads\NIRA_Sodal_Annotated.xlsx")
OUT = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Two_Annotator_Annotated.xlsx")
TASKS = ["policy_relevance", "feedback_type", "topic", "sentiment"]
TITLES = {
    "policy_relevance": "Policy relevance",
    "feedback_type": "Feedback",
    "topic": "Topic",
    "sentiment": "Sentiment",
}
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
TOPIC_ORDER = (
    "corruption_unofficial_payment",
    "delay_processing",
    "documentation_requirements",
    "registration",
    "identity_card",
    "service_access",
    "government_policy",
    "other",
)


def evidence(raw):
    text = reader.norm(raw)
    letters = "".join(ch for ch in text if ch.isalpha())
    money = reader.has(text, reader.MONEY) or "$" in raw
    delay = reader.has(text, reader.DELAY)
    doc = reader.has(text, reader.DOC)
    reg = reader.has(text, reader.REG)
    card = reader.has(text, reader.CARD) or reader.has_id(text)
    service = reader.has(text, reader.SERVICE)
    gov = reader.has(text, reader.GOV)
    nira = reader.has(text, reader.NIRA)
    question = "?" in raw or "\u061f" in raw or reader.has(text, reader.QUESTION)
    request = reader.has(text, reader.REQUEST)
    support = reader.has(text, reader.SUPPORT) or reader.has(text, ("wacan", "mash all", "gules", "mahadsanid"))
    criticism = reader.has(text, reader.CRITICISM)
    complaint = reader.has(text, reader.COMPLAINT) or (money and not request and not support)
    experience = reader.has(text, reader.EXPERIENCE)
    return {
        "money": money, "delay": delay, "doc": doc, "reg": reg, "card": card,
        "service": service, "gov": gov, "nira": nira, "question": question,
        "request": request, "support": support, "criticism": criticism,
        "complaint": complaint, "experience": experience,
        "policy": money or delay or doc or reg or card or service or nira,
        "accused": money or criticism or complaint,
        "long": len(letters) >= 12,
        "positive": support,
        "negative": (money or criticism or complaint) or delay,
    }


def supports(task, label, flags):
    if task == "policy_relevance":
        if label == "relevant":
            return flags["policy"]
        if label == "not_relevant":
            return (not flags["policy"]) and flags["long"]
        if label == "uncertain":
            return not flags["policy"]
    elif task == "feedback_type":
        return {
            "support": flags["support"] and not flags["accused"],
            "question": flags["question"],
            "request": flags["request"],
            "experience": flags["experience"] or (flags["delay"] and not flags["money"]),
            "criticism": flags["criticism"],
            "complaint": flags["complaint"] or flags["money"] or flags["delay"],
            "information": flags["policy"] and not flags["question"] and not flags["accused"],
            "other": not flags["policy"],
        }[label]
    elif task == "topic":
        cue = {
            "documentation_requirements": flags["doc"],
            "corruption_unofficial_payment": flags["money"],
            "delay_processing": flags["delay"],
            "registration": flags["reg"],
            "identity_card": flags["card"],
            "service_access": flags["service"],
            "government_policy": flags["gov"],
            "other": not any(flags[k] for k in ("doc", "money", "delay", "reg", "card", "service", "gov")),
        }[label]
        return cue
    elif task == "sentiment":
        if label == "negative":
            return flags["negative"]
        if label == "positive":
            return flags["positive"] and not flags["negative"]
        if label == "uncertain":
            return (flags["positive"] and flags["negative"]) or not flags["long"]
        if label == "neutral":
            return not flags["negative"] and not flags["positive"]
    raise KeyError((task, label))


def because(task, label, flags):
    if task == "policy_relevance" and label == "uncertain" and flags["long"]:
        return "the comment has no card, payment, registration, wait, or service cue"
    reasons = {
        ("policy_relevance", "relevant"): "the comment refers to the card, payment, registration, a wait, or a service centre",
        ("policy_relevance", "not_relevant"): "the comment has no card, payment, registration, wait, or service cue",
        ("policy_relevance", "uncertain"): "the comment is too short or unclear to judge",
        ("feedback_type", "question"): "the comment asks a question",
        ("feedback_type", "request"): "the comment asks for an action",
        ("feedback_type", "support"): "the comment praises or thanks",
        ("feedback_type", "experience"): "the comment is a first-person account",
        ("feedback_type", "criticism"): "the comment judges the service or an authority",
        ("feedback_type", "complaint"): "the comment reports a problem, a payment, or a wait",
        ("feedback_type", "information"): "the comment states a point without asking or complaining",
        ("feedback_type", "other"): "the comment does not fit a feedback type",
        ("topic", "corruption_unofficial_payment"): "the comment mentions payment",
        ("topic", "delay_processing"): "the comment mentions waiting or a missing result",
        ("topic", "documentation_requirements"): "the comment mentions a document or a reference number",
        ("topic", "registration"): "the comment mentions registration",
        ("topic", "identity_card"): "the comment mentions the identity card",
        ("topic", "service_access"): "the comment mentions a centre or where the service is given",
        ("topic", "government_policy"): "the comment mentions the government or the president",
        ("topic", "other"): "the comment has no clearer topic cue",
        ("sentiment", "negative"): "the comment reports a problem or a wait",
        ("sentiment", "positive"): "the comment praises or thanks",
        ("sentiment", "neutral"): "the comment has no clear praise or complaint",
        ("sentiment", "uncertain"): "the comment mixes praise and a problem, or is unclear",
    }
    return reasons[(task, label)]


def preferred_policy(first, second, flags):
    pair = {first, second}
    if pair == {"not_relevant", "uncertain"}:
        return "not_relevant" if flags["long"] else "uncertain"
    return None


def choose(task, first, second, flags):
    ok1 = supports(task, first, flags)
    ok2 = supports(task, second, flags)
    if task == "policy_relevance" and ok1 and ok2 and preferred_policy(first, second, flags):
        chosen = preferred_policy(first, second, flags)
        basis = "wording"
    elif task == "topic" and ok1 and ok2:
        rank = {label: index for index, label in enumerate(TOPIC_ORDER)}
        chosen = first if rank[first] <= rank[second] else second
        basis = "wording"
    elif ok2 and not ok1:
        chosen = second
        basis = "wording"
    elif ok1 and not ok2:
        chosen = first
        basis = "wording"
    else:
        chosen = first
        basis = "primary"
    rejected = second if chosen == first else first
    who = "Raggeh" if chosen == first else "Sodal"
    if basis == "primary":
        reason = (
            f"{TITLES[task]}: {chosen} was kept and {rejected} was not, "
            "because the comment does not separate the two labels, so Raggeh's label remains."
        )
    else:
        reason = (
            f"{TITLES[task]}: {chosen} was kept and {rejected} was not, "
            f"because {because(task, chosen, flags)}. {who}'s label was kept."
        )
    return chosen, reason


def kappa(left, right):
    n = len(left)
    labels = sorted(set(left) | set(right))
    po = sum(a == b for a, b in zip(left, right)) / n
    pe = 0.0
    for label in labels:
        pe += (sum(a == label for a in left) / n) * (sum(b == label for b in right) / n)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


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
    header, body = rows[0], [row + [""] * (width - len(row)) for row in rows[1:]]
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
    kept = {task: {"agree": 0, "Raggeh": 0, "Sodal": 0} for task in TASKS}
    for record in merged.itertuples(index=False):
        flags = evidence(record.comment_raggeh)
        item = {"annotation_id": record.annotation_id, "comment": record.comment_raggeh}
        reasons = []
        for task in TASKS:
            first = getattr(record, task)
            second = getattr(record, f"annotator_2_{task}_sodal").strip()
            item[f"annotator_1_{task}"] = first
            item[f"annotator_2_{task}"] = second
            if first == second:
                item[f"agree_{task}"] = "yes"
                item[f"final_for_modeling_{task}"] = first
                kept[task]["agree"] += 1
            else:
                chosen, reason = choose(task, first, second, flags)
                item[f"agree_{task}"] = "no"
                item[f"final_for_modeling_{task}"] = chosen
                reasons.append(reason)
                kept[task]["Raggeh" if chosen == first else "Sodal"] += 1
        item["disagreement_reason"] = " ".join(reasons)
        rows.append(item)

    columns = ["annotation_id", "comment"]
    columns += [f"annotator_1_{task}" for task in TASKS]
    columns += [f"annotator_2_{task}" for task in TASKS]
    columns += [f"agree_{task}" for task in TASKS]
    columns.append("disagreement_reason")
    columns += [f"final_for_modeling_{task}" for task in TASKS]
    work = pd.DataFrame(rows)[columns]

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
            "disagreed_final_raggeh": kept[task]["Raggeh"],
            "disagreed_final_sodal": kept[task]["Sodal"],
        })
    definitions = pd.DataFrame(
        [
            ["policy_relevance", "relevant", "The comment is about the national ID, the card, registration, payment, a wait, documents, or a service centre."],
            ["policy_relevance", "not_relevant", "The comment is about something other than that service."],
            ["policy_relevance", "uncertain", "The comment is too short or too unclear to judge."],
            ["feedback_type", "complaint", "The writer reports a problem, a charge, or a wait."],
            ["feedback_type", "criticism", "The writer judges the service or an authority."],
            ["feedback_type", "experience", "The writer gives a first-person account."],
            ["feedback_type", "information", "The writer states a point without asking or complaining."],
            ["feedback_type", "question", "The writer asks a question."],
            ["feedback_type", "request", "The writer asks for an action."],
            ["feedback_type", "support", "The writer praises or thanks."],
            ["feedback_type", "other", "None of the feedback types above."],
            ["topic", "corruption_unofficial_payment", "Money, a fee, or a bribe."],
            ["topic", "delay_processing", "Waiting or a missing result."],
            ["topic", "documentation_requirements", "Papers, a passport, or a reference number."],
            ["topic", "registration", "Registering or the register."],
            ["topic", "identity_card", "The identity card itself."],
            ["topic", "service_access", "A centre, office, district, or where the service is given."],
            ["topic", "government_policy", "The government, the president, or the policy itself, when no more specific topic above is present."],
            ["topic", "other", "No topic above."],
            ["sentiment", "negative", "A problem, a charge, or a wait."],
            ["sentiment", "positive", "Praise or thanks."],
            ["sentiment", "neutral", "No praise and no complaint."],
            ["sentiment", "uncertain", "Too short to judge, or both praise and a problem."],
            ["actor", "Raggeh only", "Sodal did not code actor. The Keys sheet keeps Raggeh's actor label."],
        ],
        columns=["task", "label", "definition"],
    )
    notes = pd.DataFrame(
        [
            ["annotator_1", "Raggeh. The project file is NIRA_Project_Final_Annotation.xlsx."],
            ["annotator_2", "Sodal. Labels from NIRA_Sodal_Annotated.xlsx. The comments were not changed."],
            ["agreement", "yes means the two labels are the same. no means they differ."],
            ["final_for_modeling", "Where they agree, the shared label. Where they differ, the label whose definition the comment supports. If both fit, or neither does, Raggeh's label remains. The final is always one of the two labels."],
            ["disagreement_reason", "Blank when all four tasks agree. Otherwise one sentence for each task that differs."],
            ["actor", "Not coded by Sodal. See the Keys sheet."],
            ["model training", "Do not train on this file until the final columns are accepted. The current thesis still uses Raggeh's labels."],
        ],
        columns=["item", "value"],
    )
    keys = merged[["annotation_id", "comment_id", "post_url", "actor"]].rename(columns={"actor": "actor_raggeh"})

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        work.to_excel(writer, sheet_name="Annotations", index=False)
        pd.DataFrame(summary).to_excel(writer, sheet_name="Agreement", index=False)
        definitions.to_excel(writer, sheet_name="Definitions", index=False)
        keys.to_excel(writer, sheet_name="Keys", index=False)
        notes.to_excel(writer, sheet_name="Notes", index=False)
        page = writer.book["Annotations"]
        page.freeze_panes = "C2"
        page.auto_filter.ref = "A1:T3501"
        widths = {"A": 16, "B": 56, "S": 78}
        for letter, width in widths.items():
            page.column_dimensions[letter].width = width
        for index in range(3, 20):
            page.column_dimensions[get_column_letter(index)].width = 24
        header_font = Font(color="FFFFFF", bold=True, name="Calibri")
        fills = {
            "annotator_1": PatternFill("solid", fgColor="1F4E99"),
            "annotator_2": PatternFill("solid", fgColor="1F4E99"),
            "agree": PatternFill("solid", fgColor="0F6B4C"),
            "disagreement_reason": PatternFill("solid", fgColor="7A3E00"),
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
            elif name == "disagreement_reason":
                cell.fill = fills["disagreement_reason"]
            else:
                cell.fill = fills["annotator_1"]
        for row in page.iter_rows(min_row=2, max_row=3501, min_col=2, max_col=2):
            cell = row[0]
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cell.data_type = "s"
        for name, width in (("Agreement", 22), ("Definitions", 88), ("Keys", 36), ("Notes", 110)):
            sheet = writer.book[name]
            sheet.freeze_panes = "A2"
            sheet.column_dimensions["A"].width = 28
            sheet.column_dimensions["B"].width = width

    print(OUT)
    print(pd.DataFrame(summary).to_string(index=False))
    needs = work[[f"agree_{task}" for task in TASKS]].eq("no").any(axis=1)
    print("reasons", int(needs.sum()), "blank reasons on disagreements", int((needs & work["disagreement_reason"].eq("")).sum()))
    print("blank finals", int(work[[f"final_for_modeling_{task}" for task in TASKS]].eq("").any(axis=1).sum()))


if __name__ == "__main__":
    main()
