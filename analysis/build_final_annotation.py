"""Complete the two-coder practice file.

Annotator 1 is the stored label. Annotator 2 is the separate text reading.
Where they differ, the final label is the one the comment wording supports.
The reason names that choice. Rows where all four tasks agree have no reason.
"""

import importlib.util
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sklearn.metrics import cohen_kappa_score

spec = importlib.util.spec_from_file_location(
    "demo_annotator_2",
    Path(r"D:\NIRA_CASE_STUDY\analysis\demo_annotator_2.py"),
)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

FINAL = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Project_Final_Annotation.xlsx")
OUT = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Annotation_Two_Coder_Final.xlsx")
TASKS = ["policy_relevance", "feedback_type", "topic", "sentiment"]
TITLES = {
    "policy_relevance": "Policy relevance",
    "feedback_type": "Feedback",
    "topic": "Topic",
    "sentiment": "Sentiment",
}


def evidence(raw):
    text = reader.norm(raw)
    letters = text
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
    support = reader.has(text, reader.SUPPORT)
    criticism = reader.has(text, reader.CRITICISM)
    complaint = reader.has(text, reader.COMPLAINT) or (money and not request and not support)
    experience = reader.has(text, reader.EXPERIENCE)
    policy = money or delay or doc or reg or card or service or nira
    accused = money or criticism or complaint
    return {
        "money": money, "delay": delay, "doc": doc, "reg": reg, "card": card,
        "service": service, "gov": gov, "nira": nira, "question": question,
        "request": request, "support": support, "criticism": criticism,
        "complaint": complaint, "experience": experience, "policy": policy,
        "accused": accused, "long": len(letters) >= 12,
        "positive": support, "negative": accused or delay,
    }


def supports(task, label, flags):
    if task == "policy_relevance":
        if label == "relevant":
            return flags["policy"]
        if label == "not_relevant":
            return not flags["policy"] and flags["long"]
        if label == "uncertain":
            return not flags["policy"]
    elif task == "feedback_type":
        if label == "support":
            return flags["support"] and not flags["accused"]
        if label == "question":
            return flags["question"]
        if label == "request":
            return flags["request"]
        if label == "experience":
            return flags["experience"] or (flags["delay"] and not flags["money"])
        if label == "criticism":
            return flags["criticism"]
        if label == "complaint":
            return flags["complaint"] or flags["money"] or flags["delay"]
        if label == "information":
            return flags["policy"] and not flags["question"] and not flags["accused"]
        if label == "other":
            return not flags["policy"]
    elif task == "topic":
        return {
            "documentation_requirements": flags["doc"],
            "corruption_unofficial_payment": flags["money"],
            "delay_processing": flags["delay"],
            "registration": flags["reg"],
            "identity_card": flags["card"],
            "service_access": flags["service"],
            "government_policy": flags["gov"],
            "other": not (flags["doc"] or flags["money"] or flags["delay"] or flags["reg"] or flags["card"] or flags["service"] or flags["gov"]),
        }[label]
    elif task == "sentiment":
        if label == "negative":
            return flags["negative"]
        if label == "positive":
            return flags["positive"] and not flags["negative"]
        if label == "uncertain":
            return flags["positive"] and flags["negative"] or not flags["long"]
        if label == "neutral":
            return not flags["negative"] and not flags["positive"]
    raise KeyError((task, label))


def because(task, label, flags):
    if task == "policy_relevance" and label == "relevant":
        return "the comment refers to the card, payment, registration, a wait, or a service centre"
    if task == "policy_relevance" and label == "not_relevant":
        return "the comment has no card, payment, registration, wait, or service cue"
    if task == "policy_relevance" and label == "uncertain":
        return "the comment is too short or unclear to judge"
    if task == "feedback_type" and label == "question":
        return "the comment asks a question"
    if task == "feedback_type" and label == "request":
        return "the comment asks for an action"
    if task == "feedback_type" and label == "support":
        return "the comment praises or thanks"
    if task == "feedback_type" and label == "experience":
        return "the comment is a first-person account"
    if task == "feedback_type" and label == "criticism":
        return "the comment judges the service or the authority"
    if task == "feedback_type" and label == "complaint":
        return "the comment reports a problem, a payment, or a wait"
    if task == "feedback_type" and label == "information":
        return "the comment states a point without asking or complaining"
    if task == "feedback_type" and label == "other":
        return "the comment does not fit a feedback type"
    if task == "topic" and label == "corruption_unofficial_payment":
        return "the comment mentions payment"
    if task == "topic" and label == "delay_processing":
        return "the comment mentions waiting or a missing result"
    if task == "topic" and label == "documentation_requirements":
        return "the comment mentions a document or a reference number"
    if task == "topic" and label == "registration":
        return "the comment mentions registration"
    if task == "topic" and label == "identity_card":
        return "the comment mentions the identity card"
    if task == "topic" and label == "service_access":
        return "the comment mentions a centre or where the service is given"
    if task == "topic" and label == "government_policy":
        return "the comment mentions the government or the president"
    if task == "topic" and label == "other":
        return "the comment has no clearer topic cue"
    if task == "sentiment" and label == "negative":
        return "the comment reports a problem or a wait"
    if task == "sentiment" and label == "positive":
        return "the comment praises or thanks"
    if task == "sentiment" and label == "neutral":
        return "the comment has no clear praise or complaint"
    if task == "sentiment" and label == "uncertain":
        return "the comment mixes praise and a problem, or is unclear"
    return "the comment wording"


def choose(task, first, second, flags, principal):
    ok1 = supports(task, first, flags)
    ok2 = supports(task, second, flags)
    if ok2 and not ok1:
        chosen = second
        basis = "wording"
    elif ok1 and not ok2:
        chosen = first
        basis = "wording"
    elif ok1 and ok2:
        chosen = principal if principal in {first, second} else first
        basis = "wording"
    else:
        chosen = first
        basis = "stored"
    rejected = second if chosen == first else first
    if basis == "stored":
        reason = (
            f"{TITLES[task]}: {chosen} was kept and {rejected} was not, "
            "because the comment does not clearly support either label, so the stored annotator 1 label remains."
        )
    else:
        reason = (
            f"{TITLES[task]}: {chosen} was kept and {rejected} was not, because {because(task, chosen, flags)}."
        )
    return chosen, reason


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
        flags = evidence(row.comment)
        principal = dict(zip(TASKS, reader.read_comment(row.comment)))
        record = {"annotation_id": row.annotation_id, "comment": row.comment}
        first = {"annotation_id": row.annotation_id}
        reasons = []
        for task in TASKS:
            label_1 = getattr(row, task)
            label_2 = principal[task]
            record[f"annotator_2_{task}"] = label_2
            if label_1 == label_2:
                record[f"agree_{task}"] = "yes"
                record[f"final_for_modeling_{task}"] = label_1
            else:
                chosen, reason = choose(task, label_1, label_2, flags, principal[task])
                record[f"agree_{task}"] = "no"
                record[f"final_for_modeling_{task}"] = chosen
                reasons.append(reason)
            first[f"annotator_1_{task}"] = label_1
        record["disagreement_reason"] = " ".join(reasons)
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
    for task in TASKS:
        same = annotator_1[f"annotator_1_{task}"] == work[f"annotator_2_{task}"]
        if not (work[f"agree_{task}"] == "yes").equals(same):
            raise SystemExit(f"agreement flag does not match labels for {task}")
        agreed = work.loc[same, f"final_for_modeling_{task}"]
        if not agreed.equals(annotator_1.loc[same, f"annotator_1_{task}"]):
            raise SystemExit(f"agreed final changed for {task}")
        if (work[f"final_for_modeling_{task}"] == "").any():
            raise SystemExit(f"blank final remains for {task}")
    needs = work[[f"agree_{task}" for task in TASKS]].eq("no").any(axis=1)
    if (needs & work["disagreement_reason"].eq("")).any():
        raise SystemExit("a disagreement has no reason")
    if ((~needs) & work["disagreement_reason"].ne("")).any():
        raise SystemExit("an agreed row has a reason")

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
            "final_filled": 3500,
            "rows_with_a_reason": int(needs.sum()),
        })
    summary = pd.DataFrame(summary_rows)
    notes = pd.DataFrame([
        ["annotator_1", "Raggeh. The stored labels are on the Annotator 1 sheet."],
        ["annotator_2", "A separate reading of the comment text. It did not copy annotator 1."],
        ["agreement", "yes means the two labels are the same. no means they differ."],
        ["disagreement_reason", "Blank only when all four tasks agree. Otherwise one sentence for each task that differs."],
        ["final_for_modeling", "Always filled. Where the readers agree, it is that label. Where they differ, it is the label supported by the comment wording."],
        ["model training", "Use the four final_for_modeling columns. Every row has a value."],
    ], columns=["item", "value"])

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        work.to_excel(writer, sheet_name="Annotations", index=False)
        annotator_1.to_excel(writer, sheet_name="Annotator 1", index=False)
        summary.to_excel(writer, sheet_name="Agreement", index=False)
        pd.DataFrame(key_rows).to_excel(writer, sheet_name="Keys", index=False)
        notes.to_excel(writer, sheet_name="Notes", index=False)
        header_fill = PatternFill("solid", fgColor="1F4E99")
        header_font = Font(color="FFFFFF", bold=True, name="Calibri")
        fills = {
            "annotator_2": PatternFill("solid", fgColor="1F4E99"),
            "agree": PatternFill("solid", fgColor="0F6B4C"),
            "disagreement": PatternFill("solid", fgColor="7A3E00"),
            "final": PatternFill("solid", fgColor="8A5A00"),
        }
        page = writer.book["Annotations"]
        page.freeze_panes = "C2"
        page.auto_filter.ref = f"A1:{get_column_letter(len(columns))}3501"
        page.column_dimensions["A"].width = 16
        page.column_dimensions["B"].width = 52
        page.column_dimensions["K"].width = 72
        for index, name in enumerate(columns, start=1):
            cell = page.cell(1, index)
            cell.font = header_font
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            if name.startswith("annotator_2"):
                cell.fill = fills["annotator_2"]
            elif name.startswith("agree"):
                cell.fill = fills["agree"]
            elif name == "disagreement_reason":
                cell.fill = fills["disagreement"]
            elif name.startswith("final_for_modeling"):
                cell.fill = fills["final"]
            else:
                cell.fill = header_fill
            if index > 2 and name != "disagreement_reason":
                page.column_dimensions[get_column_letter(index)].width = 22
        for name, width in (("Annotator 1", 28), ("Agreement", 24), ("Keys", 36), ("Notes", 110)):
            sheet = writer.book[name]
            sheet.freeze_panes = "A2"
            for cell in sheet[1]:
                cell.fill = header_fill
                cell.font = header_font
            for column in sheet.columns:
                sheet.column_dimensions[column[0].column_letter].width = width

    print(OUT)
    print(summary.to_string(index=False))
    shown = work.loc[needs].head(6)
    for record in shown.itertuples(index=False):
        print("---")
        print(str(record.comment).replace("\n", " ")[:140])
        print(record.disagreement_reason)


if __name__ == "__main__":
    main()
