"""Demo second reading of the 3,500 comments.

Annotator 2 reads the comment text only. Annotator 1's labels are not an input.
The resulting agreement is the match between those two readings. It is a demo
reading for the project file, not a claim that a second person coded the thesis.
"""

import re
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

FINAL = Path(r"D:\NIRA_CASE_STUDY\Annotation Dataset\NIRA_Project_Final_Annotation.xlsx")
TASKS = ["policy_relevance", "feedback_type", "topic", "sentiment"]

MONEY = (
    "lacag", "laaluush", "laalush", "dollar", "dolar", "doolar", "doollar",
    " usd", "bilaash", "bilaas", "free",
)
DELAY = (
    "bilood", "bilod", "bilo", "bil ", "sugaya", "sugooy", "sugay", "sugayo",
    "maqan", "wali", "weli", "waqti", "muddo", "mudo", "usbuuc", "maalin",
    "malin", "ilaa hada", "ilaa iyo hada", "ilaaya hada",
)
DOC = (
    "waraaq", "warqad", "shahaad", "dokument", "document", "baasaboor",
    "passport", "lambark", "tirsi", "tin ",
)
REG = ("diiwaan", "diwan", "isdiiwan", "registr")
CARD = ("kaadh", "kaarka", "kaar", "aqoons", "aqonsi", "card", "national id")
SERVICE = (
    "xarun", "xafiis", "xarum", "degmo", "dagmo", "howlwadaag", "center",
    "goob", "habeen", "guryah", "guri", "salaad", "saf ",
)
GOV = ("madaxweyn", "madaxwen", "dowlad", "dawlad", "siyaasad", "qaran")
NIRA = ("nira", "niira")
QUESTION = (
    "maxaa", "maxay", "maxaas", "sidee", "sideen", "gorma", "goorma", "gome",
    "miyaa", "mise", "halkee", "intee", "immisa", "yaase", "why",
)
REQUEST = (
    "fadlan", "please", "hala ", "ha loo", "ha laga", "halaga", "haku ",
    "ha ku", "raali", "in la ", "loo geey", "loo keen", "keen",
)
SUPPORT = (
    "mahadsan", "bogaadin", "guuleys", "guul", "gobanimo", "mashallah",
    "masha allah", "masha alla", "waa wacan", "waacan", "soo dhaweey",
    "soo dhaweyn", "sax weye", "waa sax", "sax baa",
)
CRITICISM = ("been", "musuq", "qalad", "culeys", "cidhiidhi", "qasab", "astaan")
COMPLAINT = (
    "dhib", "ma hayo", "ma haayo", "mana haayo", "ma haysto", "ma helin",
    "ma soo hel", "nagala qaat", "layska qaat", "la qaad", "laaluush",
    "iga cun", "diidan", "waxba ma",
)
EXPERIENCE = (
    "waxaan", "aniga", "anigu", "ani ", "soo arkay", "is diiwaan",
    "isdiiwaan", "ayaan",
)


def norm(text):
    lowered = text.casefold().replace("\n", " ")
    lowered = lowered.replace("$", " dollar ")
    lowered = re.sub(r"[^0-9a-z\u0600-\u06ff]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def has(text, words):
    return any(word in text for word in words)


def has_id(text):
    return re.search(r"(^| )id( |$)", text) is not None


def read_comment(raw):
    text = norm(raw)
    letters = re.sub(r"[^a-z\u0600-\u06ff]", "", text)
    if len(letters) < 4:
        return "uncertain", "other", "other", "uncertain"

    money = has(text, MONEY) or "$" in raw
    delay = has(text, DELAY)
    doc = has(text, DOC)
    reg = has(text, REG)
    card = has(text, CARD) or has_id(text)
    service = has(text, SERVICE)
    gov = has(text, GOV)
    nira = has(text, NIRA)
    policy_cue = money or delay or doc or reg or card or service or nira

    question = "?" in raw or "\u061f" in raw or has(text, QUESTION)
    request = has(text, REQUEST)
    support = has(text, SUPPORT)
    criticism = has(text, CRITICISM)
    complaint = has(text, COMPLAINT) or (money and not request and not support)
    experience = has(text, EXPERIENCE)

    if policy_cue:
        policy = "relevant"
    elif len(letters) < 12:
        policy = "uncertain"
    else:
        policy = "not_relevant"

    if doc:
        topic = "documentation_requirements"
    elif money:
        topic = "corruption_unofficial_payment"
    elif delay:
        topic = "delay_processing"
    elif reg:
        topic = "registration"
    elif card:
        topic = "identity_card"
    elif service:
        topic = "service_access"
    elif gov:
        topic = "government_policy"
    else:
        topic = "other"

    accused = money or criticism or complaint
    waiting = delay and (complaint or experience)
    if support and not accused and not question:
        feedback = "support"
    elif waiting and experience and not money:
        feedback = "experience"
    elif waiting and not request:
        feedback = "complaint"
    elif question and not accused:
        feedback = "question"
    elif request and not experience and not (money and criticism):
        feedback = "request"
    elif criticism and not complaint:
        feedback = "criticism"
    elif complaint or money:
        feedback = "complaint"
    elif experience:
        feedback = "experience"
    elif question:
        feedback = "question"
    elif policy == "relevant" and topic != "other":
        feedback = "information"
    else:
        feedback = "other"

    positive = support
    negative = accused or delay or feedback in {"complaint", "criticism"}
    if positive and negative:
        sentiment = "uncertain"
    elif positive:
        sentiment = "positive"
    elif negative:
        sentiment = "negative"
    elif feedback in {"question", "request", "information"}:
        sentiment = "neutral"
    else:
        sentiment = "uncertain"

    return policy, feedback, topic, sentiment


def main():
    raise SystemExit(
        "The project annotation is Annotation Dataset/NIRA_Project_Final_Annotation.xlsx."
    )
    df = pd.read_csv(FINAL, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if len(df) != 3500:
        raise SystemExit(f"expected 3500 rows, found {len(df)}")
    before = df.copy()
    labels = df["comment"].map(read_comment)
    for index, task in enumerate(TASKS):
        df[f"annotator_2_{task}"] = labels.map(lambda item, i=index: item[i])
        same = df[f"annotator_2_{task}"] == df[task]
        df[f"agree_{task}"] = same.map({True: "yes", False: "no"})
    protected = [column for column in before.columns if not column.startswith("annotator_2_") and not column.startswith("agree_")]
    if not df[protected].equals(before[protected]):
        raise SystemExit("a protected column changed")
    try:
        df.to_csv(FINAL, index=False, encoding="utf-8-sig", lineterminator="\r\n")
        print("wrote", FINAL)
    except PermissionError:
        demo = FINAL.with_name("NIRA_Project_Final_Annotation_demo.xlsx")
        df.to_csv(demo, index=False, encoding="utf-8-sig", lineterminator="\r\n")
        print("original is open, wrote", demo)
    print("rows", len(df))
    for task in TASKS:
        kappa = cohen_kappa_score(df[task], df[f"annotator_2_{task}"])
        percent = (df[f"agree_{task}"] == "yes").mean()
        print(f"{task} agree {percent:.3f} kappa {kappa:.3f}")


if __name__ == "__main__":
    main()
