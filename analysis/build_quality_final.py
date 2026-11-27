"""One-sheet final. The final is always one of the two human labels.

Agreed rows keep the shared label. Disagreed rows keep the label the comment
supports. Raggeh remains only when the comment gives both labels the same support.
"""
import sys
from pathlib import Path

import pandas as pd
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(r"D:\NIRA_CASE_STUDY\analysis")))
import build_two_annotator_file as base

OUT = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Project_Final_Annotation.xlsx")
TITLES = base.TITLES

POLICY = (
    "nira", "niira", "kaar", "kaadh", "aqoons", "aqonsi", "national id",
    "lacag", "laaluush", "laalush", "dollar", "dolar", "doolar",
    "basaboor", "baasaboor", "passport", "diiwaan", "diwan", "xarun",
    "xafiis", "howlwadaag", "ma haayo", "ma hayo", "waxba ma", "bilood",
)
PRAISE = ("mahadsan", "bogaadin", "guuleys", "gules", "wacan", "mashall", "mash all", "waa sax", "sax weye")
PROBLEM = ("dhib", "ma haayo", "ma hayo", "waxba ma", "ma helin", "ma rabo", "been", "qalad", "culeys", "qasab", "laaluush", "lacag")
QUESTION = ("maxaa", "maxay", "sidee", "goorma", "gorma", "gome", "miyaa", "halkee", "intee", "immisa", "yaase")
REQUEST = ("fadlan", "please", "hala ", "ha loo", "keen", "kena", "sii kar", "malagu", "malugu")
PERSON = ("waxaan", "aniga", "anigu", "anigaa", "ayaan")
GOV = ("madaxweyn", "madaxwen", "madaxwayn", "dowlad", "dawlad", "xukuum", "wasaar", "wasiir", "siyaasad")
CARD = ("kaar", "kaadh", "aqoons", "aqonsi", "national id")
MONEY = ("lacag", "laaluush", "laalush", "dollar", "dolar", "doolar", "15$", "$")
DELAY = ("bilood", "bilod", "sugaya", "sugay", "ilaa hada", "ilaa iyo hada", "wali", "weli", "ma haayo", "waxba ma")
DOC = ("basaboor", "baasaboor", "passport", "warqad", "waraaq", "shahaad", "dokument", "lambark")
REG = ("diiwaan", "diwan", "isdiiwan", "registr")
SERVICE = ("xarun", "xafiis", "howlwadaag", "xarunta", "degmo", "dagmo", "goob")
FEEDBACK_RANK = ["complaint", "question", "request", "criticism", "support", "experience", "information", "other"]
TOPIC_RANK = [
    "corruption_unofficial_payment", "delay_processing", "documentation_requirements",
    "registration", "identity_card", "service_access", "government_policy", "other",
]


def text_of(raw):
    return base.reader.norm(raw)


def has(text, phrases):
    return any(phrase in text for phrase in phrases)


def asked(raw, text):
    return "?" in raw or "\u061f" in raw or has(text, QUESTION)


def policy_cue(raw, text):
    return has(text, POLICY) or base.reader.has_id(text) or "$" in raw


def praise(text):
    return has(text, PRAISE)


def problem(raw, text):
    return has(text, PROBLEM) or "$" in raw or has(text, MONEY) or has(text, DELAY)


def score_policy(label, raw, text):
    cue = policy_cue(raw, text)
    letters = "".join(ch for ch in text if ch.isalpha())
    short = len(letters) < 12
    if label == "relevant":
        return 2 if cue else 0
    if label == "not_relevant":
        return 0 if cue or short else 2
    if label == "uncertain":
        if short:
            return 2
        return 1 if cue else 0
    return 0


def score_feedback(label, raw, text):
    question = asked(raw, text)
    request = has(text, REQUEST)
    complaint = problem(raw, text) or has(text, ("nagala", "iga cun", "diidan"))
    criticism = has(text, ("been", "qalad", "culeys", "qasab", "musuq"))
    support = praise(text)
    experience = has(text, PERSON)
    if label == "question":
        return 2 if question else 0
    if label == "request":
        return 2 if request and not complaint else 0
    if label == "complaint":
        return 2 if complaint else 0
    if label == "criticism":
        return 2 if criticism and not complaint else (1 if criticism else 0)
    if label == "support":
        return 2 if support and not complaint else 0
    if label == "experience":
        return 2 if experience and not complaint else 0
    if label == "information":
        return 1 if not question and not complaint and not support and not request else 0
    if label == "other":
        return 0 if question or complaint or support or request or experience else 1
    return 0


def score_topic(label, raw, text):
    cues = {
        "corruption_unofficial_payment": has(text, MONEY) or "$" in raw,
        "delay_processing": has(text, DELAY),
        "documentation_requirements": has(text, DOC),
        "registration": has(text, REG),
        "identity_card": has(text, CARD) or base.reader.has_id(text),
        "service_access": has(text, SERVICE),
        "government_policy": has(text, GOV),
    }
    if label == "other":
        return 0 if any(cues.values()) else 1
    return 2 if cues.get(label, False) else 0


def score_sentiment(label, raw, text):
    bad = problem(raw, text)
    good = praise(text)
    letters = "".join(ch for ch in text if ch.isalpha())
    short = len(letters) < 12
    if label == "negative":
        return 2 if bad and not (good and not bad) else (2 if bad else 0)
    if label == "positive":
        return 2 if good and not bad else 0
    if label == "uncertain":
        if short or (good and bad):
            return 2
        return 0
    if label == "neutral":
        return 1 if not bad and not good else 0
    return 0


def score(task, label, raw, text):
    return {
        "policy_relevance": score_policy,
        "feedback_type": score_feedback,
        "topic": score_topic,
        "sentiment": score_sentiment,
    }[task](label, raw, text)


def because(task, label, raw, text):
    if task == "policy_relevance" and label == "uncertain" and policy_cue(raw, text):
        return "the comment mentions a document or the service, and uncertain is the closer of the two labels"
    return {
        ("policy_relevance", "relevant"): "the comment refers to the card, a payment, registration, a document, or a service centre",
        ("policy_relevance", "not_relevant"): "the comment does not refer to the identity service",
        ("policy_relevance", "uncertain"): "the comment is too short or unclear to call it relevant",
        ("feedback_type", "complaint"): "the comment reports a problem, a payment, or a wait",
        ("feedback_type", "criticism"): "the comment judges the service or an authority",
        ("feedback_type", "question"): "the comment asks a question",
        ("feedback_type", "request"): "the comment asks for an action",
        ("feedback_type", "support"): "the comment praises or thanks",
        ("feedback_type", "experience"): "the comment is a first-person account",
        ("feedback_type", "information"): "the comment states a point",
        ("feedback_type", "other"): "the comment does not fit a clearer feedback type",
        ("topic", "corruption_unofficial_payment"): "the comment mentions money or a bribe",
        ("topic", "delay_processing"): "the comment mentions a wait or a missing result",
        ("topic", "documentation_requirements"): "the comment mentions a document",
        ("topic", "registration"): "the comment mentions registration",
        ("topic", "identity_card"): "the comment mentions the identity card",
        ("topic", "service_access"): "the comment mentions a centre or a place of service",
        ("topic", "government_policy"): "the comment mentions the government or the president",
        ("topic", "other"): "the comment has no clearer topic",
        ("sentiment", "negative"): "the comment reports a problem or a complaint",
        ("sentiment", "positive"): "the comment praises or thanks",
        ("sentiment", "neutral"): "the comment has no praise and no complaint",
        ("sentiment", "uncertain"): "the comment is too short, or it both praises and complains",
    }[(task, label)]


def tie_break(task, first, second):
    order = {
        "feedback_type": FEEDBACK_RANK,
        "topic": TOPIC_RANK,
        "sentiment": ["negative", "positive", "neutral", "uncertain"],
        "policy_relevance": ["relevant", "not_relevant", "uncertain"],
    }[task]
    rank = {label: index for index, label in enumerate(order)}
    return first if rank[first] <= rank[second] else second


def choose(task, first, second, raw):
    if first == second:
        return first, ""
    text = text_of(raw)
    left = score(task, first, raw, text)
    right = score(task, second, raw, text)
    if left > right:
        chosen = first
    elif right > left:
        chosen = second
    elif left == 0 and right == 0:
        chosen = first
        rejected = second
        return chosen, (
            f"{TITLES[task]}: {chosen} was kept and {rejected} was not, "
            "because the comment does not separate the two labels, so Raggeh's label remains."
        )
    else:
        chosen = tie_break(task, first, second)
    rejected = second if chosen == first else first
    who = "Raggeh" if chosen == first else "Sodal"
    return chosen, (
        f"{TITLES[task]}: {chosen} was kept and {rejected} was not, "
        f"because {because(task, chosen, raw, text)}. {who}'s label was kept."
    )


def main():
    raise SystemExit(
        "The project annotation is Annotation Dataset/NIRA_Project_Final_Annotation.xlsx."
    )
    raggeh = pd.read_csv(base.FINAL, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    sodal = base.read_sodal(base.SODAL)
    merged = raggeh.merge(sodal, on="annotation_id", suffixes=("_raggeh", "_sodal"))
    if len(merged) != 3500 or not (merged["comment_raggeh"] == merged["comment_sodal"]).all():
        raise SystemExit("the two files do not join")

    rows = []
    unclear = 0
    kept = {task: {"Raggeh": 0, "Sodal": 0} for task in base.TASKS}
    for record in merged.itertuples(index=False):
        item = {"annotation_id": record.annotation_id, "comment": record.comment_raggeh}
        reasons = []
        for task in base.TASKS:
            first = getattr(record, task)
            second = getattr(record, f"annotator_2_{task}_sodal").strip()
            chosen, reason = choose(task, first, second, record.comment_raggeh)
            if chosen not in {first, second}:
                raise SystemExit("a third label was created")
            item[f"annotator_1_{task}"] = first
            item[f"annotator_2_{task}"] = second
            item[f"agree_{task}"] = "yes" if first == second else "no"
            item[f"final_{task}"] = chosen
            if reason:
                reasons.append(reason)
                if "does not separate" in reason:
                    unclear += 1
                else:
                    kept[task]["Raggeh" if chosen == first else "Sodal"] += 1
        item["disagreement_reason"] = " ".join(reasons)
        rows.append(item)

    columns = ["annotation_id", "comment"]
    for task in base.TASKS:
        columns += [f"annotator_1_{task}", f"annotator_2_{task}", f"agree_{task}", f"final_{task}"]
    columns.append("disagreement_reason")
    work = pd.DataFrame(rows)[columns]
    needs = work[[f"agree_{task}" for task in base.TASKS]].eq("no").any(axis=1)
    if (needs & work["disagreement_reason"].eq("")).any() or ((~needs) & work["disagreement_reason"].ne("")).any():
        raise SystemExit("reasons do not match the disagreements")

    summary = []
    for task in base.TASKS:
        agree = work[f"agree_{task}"] == "yes"
        summary.append({
            "task": task,
            "n": 3500,
            "n_agree": int(agree.sum()),
            "n_disagree": int((~agree).sum()),
            "percent_agreement": round(float(agree.mean()), 3),
            "cohens_kappa": base.kappa(work[f"annotator_1_{task}"].tolist(), work[f"annotator_2_{task}"].tolist()),
        })
    summary.append({
        "task": "rule",
        "n": "",
        "n_agree": "",
        "n_disagree": "",
        "percent_agreement": "",
        "cohens_kappa": "Where the two labels match, that label is the final. Where they differ, the final is the one of those two labels that the comment supports. Raggeh remains only when the comment supports both equally. No third label is used.",
    })

    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        work.to_excel(writer, sheet_name="Annotations", index=False)
        pd.DataFrame(summary).to_excel(writer, sheet_name="Agreement", index=False)
        agreement = writer.book["Agreement"]
        agreement.freeze_panes = "A2"
        agreement.column_dimensions["A"].width = 22
        agreement.column_dimensions["F"].width = 88
        page = writer.book["Annotations"]
        page.freeze_panes = "C2"
        page.auto_filter.ref = "A1:S3501"
        page.row_dimensions[1].height = 32
        page.column_dimensions["A"].width = 16
        page.column_dimensions["B"].width = 52
        page.column_dimensions["S"].width = 78
        header_font = Font(color="FFFFFF", bold=True, name="Calibri")
        fills = {"annotator_1": "1F4E99", "annotator_2": "2458A8", "agree": "0F6B4C", "final": "8A5A00", "disagreement_reason": "7A3E00"}
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
            "The final is their shared label when they agree. "
            "When they differ, the final is the one of those two labels that the comment supports. "
            "A reported problem beats a general judgement. "
            "Raggeh's label remains only when the comment supports both labels equally.",
            "NIRA", width=280, height=110,
        )
        for row in page.iter_rows(min_row=2, max_row=3501, min_col=2, max_col=2):
            cell = row[0]
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cell.data_type = "s"

    print(OUT)
    print("unclear cells", unclear)
    for task in base.TASKS:
        agree = work[f"agree_{task}"] == "yes"
        print(task, "agree", int(agree.sum()), "kappa", base.kappa(work[f"annotator_1_{task}"].tolist(), work[f"annotator_2_{task}"].tolist()), "kept", kept[task])
    show = {"ANN_0009", "ANN_0051", "ANN_0943", "ANN_1652", "ANN_2234", "ANN_0017"}
    for row in work.itertuples(index=False):
        if row.annotation_id in show:
            print("\n", row.annotation_id, repr(row.comment[:150]))
            print(" ", row.final_policy_relevance, row.final_feedback_type, row.final_topic, row.final_sentiment)
            print(" ", row.disagreement_reason[:360])


if __name__ == "__main__":
    main()
