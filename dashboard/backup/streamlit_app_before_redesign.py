"""NIRA research dashboard. Reads saved outputs and does not refit models."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nira_data import GROUP_NAMES, TASK_NAMES, load, model_name

st.set_page_config(page_title="NIRA Research Dashboard", page_icon="N", layout="wide")


@st.cache_data(show_spinner=False)
def data():
    return load()


def score_chart(frame, task, winner):
    rows = frame.loc[frame["task"] == task].sort_values("macro_f1")
    colors = ["#1d6fb8" if model == winner else "#c5dff3" for model in rows["model"]]
    figure = go.Figure(
        go.Bar(
            x=rows["macro_f1"],
            y=[model_name(model) + (" · used" if model == winner else "") for model in rows["model"]],
            orientation="h",
            marker_color=colors,
            text=rows["macro_f1"].map(lambda value: f"{value:.3f}"),
            textposition="outside",
        )
    )
    figure.update_layout(
        height=250,
        margin=dict(l=10, r=48, t=8, b=8),
        font=dict(family="Poppins", size=18, color=ink()),
        xaxis_title="Validation macro-F1",
        xaxis_range=[0, 0.75],
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def count_chart(labels, values, title):
    figure = go.Figure(go.Bar(x=labels, y=values, marker_color="#1d6fb8"))
    figure.update_layout(
        title=dict(text=title, font=dict(family="Poppins", size=18)),
        font=dict(family="Poppins", size=18, color=ink()),
        height=300,
        margin=dict(l=10, r=10, t=48, b=10),
        yaxis_title="Comments",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure


def ink():
    return "#d7e8f6" if st.session_state.get("theme") == "dark" else "#0e2a43"


def apply_theme():
    mode = "dark" if st.session_state.get("theme") == "dark" else "light"
    st.markdown(
        """
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" />
        <style>
        .stApp { background: #f3f8fc; }
        [data-testid="stMainBlockContainer"] {
          padding-top: 3.4rem !important;
        }
        .stApp,
        .stApp p,
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp button,
        .stApp label,
        .stApp a,
        .stApp li,
        .stApp input,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"],
        [data-testid="stCaptionContainer"],
        .hero,
        .hero h1,
        .hero p,
        .hero .author,
        .brand-title,
        .brand-sub,
        .author-name,
        .author-note,
        .side-label {
          font-family: "Poppins", sans-serif !important;
        }
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        .hero-icon {
          font-family: "Material Symbols Rounded" !important;
        }
        [data-testid="stSidebar"] {
          background: linear-gradient(180deg, #0c4f86 0%, #08345c 100%);
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] a {
          color: #e8f4fc;
        }
        [data-testid="stSidebarNav"] ul {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        [data-testid="stSidebarNav"] a {
          border-radius: 22px;
          border: 1px solid rgba(214, 232, 248, 0.55);
          padding: 0.72rem 0.95rem;
          background: rgba(6, 32, 58, 0.28);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
          background: #1d6fb8;
          border-color: #7ec8f8;
        }
        .hero {
          background: linear-gradient(120deg, #0d4f86 0%, #2f92d8 62%, #7ec8f8 140%);
          color: white;
          border-radius: 28px;
          padding: 28px 32px 24px;
          margin-bottom: 18px;
          position: relative;
          overflow: hidden;
        }
        .hero:after {
          content: "";
          position: absolute;
          right: -30px;
          top: -50px;
          width: 180px;
          height: 180px;
          border-radius: 50%;
          background: rgba(255,255,255,0.12);
        }
        .hero .kicker {
          letter-spacing: 0.12em;
          font-size: 16px;
          opacity: 0.85;
          margin: 0 0 8px;
        }
        .hero h1 { margin: 0 0 10px; font-size: 48px; letter-spacing: -0.03em; }
        .hero p { margin: 0; max-width: 820px; font-size: 22px; line-height: 1.5; color: rgba(255,255,255,0.92); }
        .hero .author {
          display: inline-block;
          margin-top: 16px;
          border: 1px solid rgba(255,255,255,0.4);
          border-radius: 999px;
          padding: 8px 14px;
          font-size: 18px;
        }
        [data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] {
          background: white;
          border: 1px solid #d5e8f6;
          border-radius: 18px;
          padding: 8px 10px;
        }
        div[data-testid="stAlert"],
        div[data-testid="stNotification"] {
          background: #e7f4fc !important;
          color: #0e3d66 !important;
          border: 0 !important;
          border-left: 4px solid #2b8fd6 !important;
        }
        .guide-mark { display: none; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.guide-mark) {
          border-left: 4px solid #2b8fd6 !important;
          margin-bottom: 16px;
        }
        .hero-icon {
          font-family: "Material Symbols Rounded";
          font-size: 20px;
          vertical-align: -3px;
          margin-right: 8px;
          font-weight: normal;
          font-style: normal;
        }
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stMain"] [data-testid="stCaptionContainer"] p {
          font-size: 21px;
          line-height: 1.5;
        }
        [data-testid="stMain"] h3 {
          font-size: 30px;
        }
        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricLabel"] label {
          font-size: 18px;
        }
        div[data-testid="stAlert"] p {
          font-size: 20px;
          line-height: 1.5;
        }
        [data-testid="stSidebarNav"] a,
        [data-testid="stSidebarNav"] a span {
          font-size: 24px !important;
          border-radius: 22px;
        }
        [data-testid="stSidebarNav"] a [data-testid="stIconMaterial"] {
          font-size: 26px !important;
        }
        [data-testid="stSidebar"] p {
          font-size: 16px;
        }
        [data-testid="stSidebar"] { position: relative; }
        [data-testid="stSidebarContent"] {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarUserContent"] > div,
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
          display: contents;
        }
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.brand-block) {
          order: 1;
          overflow: visible;
          padding-bottom: 6px;
        }
        [data-testid="stSidebar"] [data-testid="stLayoutWrapper"] {
          order: 2;
          margin-top: 28px;
        }
        [data-testid="stSidebarNav"] { order: 3; }
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.author-block) {
          order: 4;
          margin-top: auto;
          margin-bottom: 28px;
        }
        .brand-block {
          display: flex;
          gap: 12px;
          align-items: center;
          padding: 4px 4px 2px;
        }
        .logo-n, .avatar {
          display: grid;
          place-items: center;
          flex: 0 0 auto;
          color: white;
          font-weight: 700;
        }
        .logo-n {
          width: 48px;
          height: 48px;
          border-radius: 14px;
          background: linear-gradient(145deg, #7ec8f8, #1d6fb8);
          font-size: 24px;
        }
        [data-testid="stSidebar"] .brand-title {
          margin: 0;
          font-size: 22px !important;
          font-weight: 750;
          line-height: 1.15;
          color: white;
        }
        [data-testid="stSidebar"] .brand-sub,
        [data-testid="stSidebar"] .author-note {
          margin: 2px 0 0;
          color: #d5e9f8 !important;
          font-size: 15px !important;
          line-height: 1.35;
        }
        [data-testid="stSidebar"] .side-label {
          margin: 12px 0 0;
          color: #9ec8e8 !important;
          font-size: 13px !important;
          letter-spacing: 0.14em;
          font-weight: 700;
        }
        [data-testid="stSidebar"] .stButton button {
          border-radius: 999px;
          min-height: 42px;
          font-size: 16px;
        }
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
          background: transparent;
          color: #e8f4fc;
          border: 1px solid rgba(232, 244, 252, 0.45);
        }
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
          background: #1d6fb8;
          color: white;
          border: 0;
        }
        .author-row { display: flex; align-items: center; gap: 10px; }
        .avatar {
          width: 44px;
          height: 44px;
          border-radius: 50%;
          background: linear-gradient(145deg, #7ec8f8, #1d6fb8);
          font-size: 16px;
        }
        [data-testid="stSidebar"] .author-name {
          margin: 0;
          font-size: 18px !important;
          font-weight: 700;
          color: white;
        }
        .theme-flag { display: none; }
        .stApp:has(.theme-dark) { background: #0d2233; color: #e7f3fb; }
        .stApp:has(.theme-dark) [data-testid="stAppViewContainer"],
        .stApp:has(.theme-dark) [data-testid="stMain"],
        .stApp:has(.theme-dark) [data-testid="stHeader"] { background: #0d2233; }
        .stApp:has(.theme-dark) [data-testid="stMetric"],
        .stApp:has(.theme-dark) [data-testid="stVerticalBlockBorderWrapper"] {
          background: #14324a;
          border-color: #2a5d86;
        }
        .stApp:has(.theme-dark) [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
        .stApp:has(.theme-dark) [data-testid="stMain"] h3,
        .stApp:has(.theme-dark) [data-testid="stMetricValue"],
        .stApp:has(.theme-dark) [data-testid="stMetricLabel"],
        .stApp:has(.theme-dark) [data-testid="stMetricLabel"] p,
        .stApp:has(.theme-dark) [data-testid="stCaptionContainer"] p,
        .stApp:has(.theme-dark) [data-testid="stWidgetLabel"] p,
        .stApp:has(.theme-dark) [data-testid="stRadio"] label,
        .stApp:has(.theme-dark) [data-testid="stTextInput"] label {
          color: #e7f3fb;
        }
        .stApp:has(.theme-dark) div[data-testid="stAlert"],
        .stApp:has(.theme-dark) div[data-testid="stNotification"] {
          background: #e7f4fc !important;
          color: #0e3d66 !important;
        }
        .stApp:has(.theme-dark) div[data-testid="stAlert"] p,
        .stApp:has(.theme-dark) div[data-testid="stAlert"] span,
        .stApp:has(.theme-dark) div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
        .stApp:has(.theme-dark) div[data-testid="stNotification"] p {
          color: #0e3d66 !important;
        }
        .stApp:has(.theme-dark) .hero,
        .stApp:has(.theme-dark) .hero p,
        .stApp:has(.theme-dark) .hero h1 { color: white; }
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        .hero-icon,
        [data-testid="stSidebarNav"] [data-testid="stIconMaterial"] {
          font-family: "Material Symbols Rounded" !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="theme-flag theme-{mode}"></div>', unsafe_allow_html=True)


def hero(kicker, title, text, icon):
    st.markdown(
        f"""
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded" />
        <div class="hero">
          <p class="kicker"><span class="hero-icon material-symbols-rounded">{icon}</span>{kicker}</p>
          <h1>{title}</h1>
          <p>{text}</p>
          <span class="author">Author: Ahmed Abdi Rage</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_guide(items):
    with st.container(border=True):
        st.markdown('<span class="guide-mark"></span>', unsafe_allow_html=True)
        st.markdown(":material/info: **What this page shows**")
        for icon, text in items:
            st.markdown(f":material/{icon}: {text}")


def section(icon, title):
    st.markdown(f"### :material/{icon}: {title}")


def overview():
    bundle = data()
    eda = bundle["eda"]
    hero(
        "NIRA · RESEARCH DASHBOARD",
        "National ID Policy Feedback",
        "A clear view of public comments about Somalia’s national ID policy and NIRA services: topics, models, and the feedback loop in one place.",
        "home",
    )
    page_guide([
        ("database", "The corpus size: 5,292 comments, 19 posts, and 1,199 annotated comments."),
        ("model_training", "The one model used for each of the four classification tasks."),
        ("bookmark", "Where the selected topic model and the feedback-loop comparison are recorded."),
    ])
    section("database", "Corpus size")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Raw Facebook comments", f"{eda['raw_comments']:,}")
    c2.metric("Source posts", eda["source_posts"])
    c3.metric("Annotated comments", f"{eda['annotated_comments']:,}")
    c4.metric("Annotated share", f"{eda['annotated_share_of_raw'] * 100:.1f}%")
    section("model_training", "Models used on all 5,292 comments")
    cards = st.columns(4)
    for column, (task, model) in zip(cards, bundle["winners"].items()):
        with column.container(border=True):
            st.caption(TASK_NAMES[task])
            st.markdown(f"**{model_name(model)}**")
            st.caption("Selected model")
    left, right = st.columns(2)
    selection = bundle["topic_selection"]
    left.info(
        f":material/category: The cited topic model is {selection['selected_family']} {selection['selected_setting']} "
        f"on all {selection['comments_in_corpus']:,} comments, after {selection['function_words_removed']} "
        "function words were removed. NMF and BERTopic stay in the comparison. BERTopic covered 49.1 percent "
        "and was not eligible."
    )
    right.warning(
        ":material/sync: The dates can show a thematic sequence around RESP_001. Directly linked posts are 0. "
        "Shared topic and a shared date are comparisons, not a cause."
    )


def exploration():
    bundle = data()
    eda = bundle["eda"]
    hero("DATA EXPLORATION", "What the files contain", "Collection dates and publication dates answer different questions. The publication date comes from the researcher-verified register.", "query_stats")
    page_guide([
        ("calendar_month", "Comment counts by collection day and by the publication year of the source post."),
        ("straighten", "Comment length and the count of phone-like comments."),
        ("list_alt", "All 19 posts, with the number of comments and the linkage class."),
    ])
    section("calendar_month", "Collection day and publication year")
    left, right = st.columns(2)
    days = eda["collection_days"]
    years = eda["publication_year_comment_counts"]
    left.plotly_chart(count_chart([row["collection_day"] for row in days], [row["n_comments"] for row in days], "Collection days"), width="stretch")
    right.plotly_chart(count_chart([str(row["publication_year"]) for row in years], [row["n_comments"] for row in years], "Publication year of the source post"), width="stretch")
    raw = bundle["lengths"].loc[bundle["lengths"]["group"] == "raw_corpus"].iloc[0]
    section("straighten", "Comment length")
    a, b, c = st.columns(3)
    a.metric("Median characters", f"{raw['median_chars']:.0f}")
    b.metric("Under 30 characters", f"{int(raw['under_30_chars']):,}")
    c.metric("Phone-like comments", int(raw["phone_like"]))
    section("list_alt", "19 source posts")
    show = bundle["posts"][["post_id", "publication_date_register", "account_name_register", "n_comments", "n_annotated", "event_period", "linkage_class"]]
    st.dataframe(show, width="stretch", hide_index=True)


def topics():
    bundle = data()
    selection = bundle["topic_selection"]
    hero(
        "TOPIC MODELING",
        f"{selection['selected_family']} {selection['selected_setting']} is the cited model",
        selection["selection_rule"] + " Manual topic labels were not the training target.",
        "category",
    )
    page_guide([
        ("emoji_events", "Why LDA with 6 topics was selected: highest coherence among models covering at least 80 percent."),
        ("table_chart", "Every NMF, LDA, and BERTopic candidate, including those that were not selected."),
        ("abc", "The six word lists. They are statistical terms, not confirmed theme names."),
    ])
    st.success(
        ":material/emoji_events: "
        f"{selection['selected_family']} {selection['selected_setting']} · coherence {selection['coherence_c_npmi']:.3f} · "
        f"coverage {selection['coverage'] * 100:.1f}%. Unassigned comments: {selection['unassigned_comments']:,} of "
        f"{selection['comments_in_corpus']:,}. Terms are statistical word forms, not validated theme names."
    )
    section("table_chart", "Every candidate")
    comparison = bundle["topic_comparison"].copy()
    comparison["status"] = comparison.apply(
        lambda row: "Selected" if row["family"] == "LDA" and row["setting"] == "k=6" else ("Compared" if row["coverage"] >= 0.8 else "Below 80 percent coverage"),
        axis=1,
    )
    st.dataframe(comparison, width="stretch", hide_index=True)
    section("abc", "Six LDA topics")
    columns = st.columns(3)
    for index, row in bundle["topic_terms"].reset_index(drop=True).iterrows():
        with columns[index % 3].container(border=True):
            st.caption(f":material/abc: Topic {int(row['topic_id'])} · {int(row['n_comments']):,} comments")
            st.write(row["top_terms"])


def classification():
    bundle = data()
    winners = bundle["winners"]
    hero(
        "CLASSIFICATION",
        "Four tasks, five models, one model used",
        "Each task was compared on validation macro-F1. The test set was scored once, after the winner was chosen. The winner was then refit on all 1,199 annotated rows and applied to all 5,292 comments.",
        "account_tree",
    )
    page_guide([
        ("bar_chart", "Validation macro-F1 for all five models on each task. The blue bar is the model that was used."),
        ("compare_arrows", "The held-out test score beside refit agreement. Refit agreement is not the test score."),
        ("label", "Manual labels for 1,199 comments beside the selected model’s labels for all 5,292."),
        ("forum", "The 30-comment comparison. The three groups do not overlap."),
    ])
    section("account_tree", "The model used for each task")
    cards = st.columns(4)
    for column, (task, model) in zip(cards, winners.items()):
        score = bundle["heldout"].loc[bundle["heldout"]["task"] == task].iloc[0]
        with column.container(border=True):
            st.caption(TASK_NAMES[task])
            st.markdown(f"**{model_name(model)}**")
            st.caption(f"Used on all 5,292 · test macro-F1 {score['test_macro_f1']:.3f}")
    section("bar_chart", "All five models on the validation split")
    charts = st.columns(2)
    for index, task in enumerate(TASK_NAMES):
        charts[index % 2].plotly_chart(score_chart(bundle["validation"], task, winners[task]), width="stretch")
        charts[index % 2].caption(TASK_NAMES[task])
    section("table_chart", "Validation scores")
    scores = bundle["validation"].copy()
    scores["model_name"] = scores["model"].map(model_name)
    scores["task_name"] = scores["task"].map(TASK_NAMES)
    scores["role"] = scores.apply(lambda row: "Selected and used" if row["model"] == winners[row["task"]] else "Compared", axis=1)
    st.dataframe(
        scores[["task_name", "model_name", "macro_f1", "weighted_f1", "accuracy", "role"]],
        width="stretch",
        hide_index=True,
    )
    section("compare_arrows", "Held-out test beside refit agreement")
    st.warning(":material/compare_arrows: Refit agreement is not the test score. It is calculated after training again on all 1,199 labeled rows. The 4,093 unlabeled comments cannot be scored for correctness.")
    refit = bundle["refit"].merge(bundle["heldout"][["task", "validation_macro_f1"]], on="task")
    refit["task_name"] = refit["task"].map(TASK_NAMES)
    refit["model_name"] = refit["selected_model"].map(model_name)
    st.dataframe(
        refit[["task_name", "model_name", "validation_macro_f1", "heldout_test_macro_f1", "refit_agreement_macro_f1", "refit_agreement_accuracy"]],
        width="stretch",
        hide_index=True,
    )
    section("label", "Manual labels beside the selected model")
    left, right = st.columns(2)
    for column, scope, title in (
        (left, "manual_annotated", "Manual labels, 1,199"),
        (right, "refit_prediction_on_all_comments", "Selected model on all 5,292"),
    ):
        column.markdown(f"**{title}**")
        part = bundle["distribution"].loc[bundle["distribution"]["scope"] == scope].copy()
        part["task_name"] = part["task"].map(TASK_NAMES)
        column.dataframe(part[["task_name", "label", "n", "share"]], width="stretch", hide_index=True)
    section("grid_on", "Test confusion matrices for the models that were used")
    grid = st.columns(2)
    for index, task in enumerate(TASK_NAMES):
        matrix = pd.read_csv(bundle["root"] / f"outputs/05_model_development/20261019_supervised/test_confusion_{task}.csv", index_col=0)
        grid[index % 2].markdown(f"**{TASK_NAMES[task]} · {model_name(winners[task])}**")
        grid[index % 2].dataframe(matrix, width="stretch")
    section("forum", "30 comments, side by side")
    overlap = bundle["overlap"]
    st.write(
        f"{overlap['unique_record_keys']} unique comments. Overlap between the three groups is {overlap['overlap_between_samples']}. "
        "Every comment has a prediction from the selected model for that task."
    )
    sample = bundle["sample"].copy()
    sample["group"] = sample["sample_group"].map(GROUP_NAMES)
    choice = st.radio(
        "Comment group",
        ["All 30", "Annotated 10", "Unlabeled 10", "Further 10"],
        horizontal=True,
    )
    group_key = {
        "Annotated 10": "annotated_manual_vs_predicted",
        "Unlabeled 10": "unlabeled_raw_with_prediction",
        "Further 10": "additional_predicted_comments",
    }.get(choice)
    if group_key:
        sample = sample.loc[sample["sample_group"] == group_key]
    query = st.text_input("Search the 30 comments")
    if query:
        sample = sample.loc[sample["excerpt"].str.contains(query, case=False, na=False)]
    st.caption(f"{len(sample)} of 30 comments shown")
    table = pd.DataFrame({
        "Post": sample["post_id"],
        "Group": sample["group"],
        "Annotated": sample["is_annotated"].map(lambda value: "Yes" if value else "No"),
        "Comment": sample["excerpt"],
        "Manual policy relevance": sample["manual_policy_relevance"],
        f"Predicted policy relevance · {model_name(winners['policy_relevance'])}": sample["pred_policy_relevance"],
        "Manual feedback type": sample["manual_feedback_type"],
        f"Predicted feedback type · {model_name(winners['feedback_type'])}": sample["pred_feedback_type"],
        "Manual topic": sample["manual_topic"],
        f"Predicted topic · {model_name(winners['topic'])}": sample["pred_topic"],
        "Manual sentiment": sample["manual_sentiment"],
        f"Predicted sentiment · {model_name(winners['sentiment'])}": sample["pred_sentiment"],
        "LDA topic": sample["unsupervised_topic_id"],
        "LDA terms": sample["unsupervised_topic_terms"],
    })
    st.dataframe(table, width="stretch", hide_index=True)


def feedback_loop():
    bundle = data()
    hero("FEEDBACK LOOP", "A sequence the dates can hold", "The labels below are the register’s linkage class. None says that one item caused the next.", "sync")
    page_guide([
        ("timeline", "The dated comparison: POST_01, RESP_001, POST_09, POST_04, and RESP_002."),
        ("link", "Linkage class: thematic, same-day, or unlinked. Directly linked posts are 0."),
        ("date_range", "Pre-event, event-day, and post-event counts. The date is the post’s publication date."),
        ("pie_chart", "Predicted label shares by period. They do not measure an effect of RESP_001."),
    ])
    section("timeline", "Dated comparison")
    a, b, c, d = st.columns(4)
    a.container(border=True).markdown(":material/campaign: **POST_01 · 27 Oct 2025**\n\nUniversal Somali TV. Queues, hours, and fees. 1,013 comments.\n\nThematic comparison with RESP_001. The SONNA page does not name POST_01.")
    b.container(border=True).markdown(":material/account_balance: **RESP_001 · 3 Nov 2025**\n\nSONNA. The Director General addresses night queues.\n\nSame-day temporal link with POST_09, 212 comments.")
    c.container(border=True).markdown(":material/campaign: **POST_04 · 4 Nov 2025**\n\n505 comments about alleged unofficial payments.\n\nThematic comparison with RESP_001 and RESP_002.")
    d.container(border=True).markdown(":material/account_balance: **RESP_002 · 10 Nov 2025**\n\nNIRA. Wadajir day-and-night center. Names no corpus post.")
    st.image(str(bundle["figure"]), width="stretch")
    section("link", "Linkage classes")
    st.dataframe(bundle["linkage"], width="stretch", hide_index=True)
    section("date_range", "Pre-event and post-event")
    st.warning(":material/date_range: This split is not an effect of RESP_001. A comment inherits the publication date of its source post. Collection date is not used.")
    st.dataframe(bundle["period_summary"], width="stretch", hide_index=True)
    section("article", "Posts the register names beside an inventory row")
    named = bundle["named_posts"][["post_id", "publication_date", "n_comments", "linkage_class", "comparison_response_ids"]]
    st.dataframe(named, width="stretch", hide_index=True)
    section("pie_chart", "Predicted label shares by period")
    st.caption(":material/pie_chart: These shares describe the selected model in each period. They do not measure an effect of RESP_001.")
    shares = bundle["period_shares"].copy()
    shares["task"] = shares["task"].map(lambda task: TASK_NAMES.get(task, task))
    st.dataframe(shares[["event_period", "task", "label", "n", "share"]], width="stretch", hide_index=True)


def quality():
    bundle = data()
    hero("DATA QUALITY", "What was checked and what stays limited", "The raw file and the annotation workbook were not overwritten. Predictions are model output, not corrected ground truth.", "verified")
    page_guide([
        ("fact_check", "Text match for the 1,199 annotated comments: 1,174 exact, 12 spacing or line breaks, and 13 content differences."),
        ("space_bar", "The 12 spacing comments stayed in training. Whitespace was collapsed before the model saw them."),
        ("edit_note", "The registered correction for ANN_0031. The original file was not changed and the models were not retrained."),
        ("balance", "How common each manual label is inside the 1,199."),
    ])
    section("fact_check", "Text match")
    columns = st.columns(3)
    for column, row in zip(columns, bundle["text_match"].itertuples(index=False)):
        column.metric(row.text_match_status, f"{int(row.n_comments):,}")
    st.caption(":material/space_bar: The 12 spacing comments stayed in training. Whitespace was collapsed before the model saw them.")
    correction = bundle["corrections"].iloc[0]
    st.warning(
        f":material/edit_note: {correction['annotation_id']} sentiment was registered from {correction['original_value']} to {correction['corrected_value']} "
        f"on {correction['corrected_on']}. {correction['reason']} The original workbook was not changed, and the models were not retrained."
    )
    raw = bundle["lengths"].loc[bundle["lengths"]["group"] == "raw_corpus"].iloc[0]
    left, right = st.columns(2)
    left.markdown(":material/key: **Identifiers**")
    left.write("comment_id restarts inside each post. The join key is the stripped post URL plus the comment id. Collection date is the collection time, never the publication date.")
    right.markdown(":material/translate: **Language**")
    right.write(
        f"{int(raw['phone_like'])} raw comments matched a phone pattern and are redacted. Arabic script: {int(raw['arabic_script'])}. "
        f"Styled Latin: {int(raw['styled_latin'])}. Embedding scores do not show that the multilingual model understands Somali."
    )
    section("balance", "Annotated class balance")
    st.dataframe(bundle["balance"], width="stretch", hide_index=True)


def render_sidebar():
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    st.sidebar.markdown(
        """
        <div class="brand-block">
          <span class="logo-n">N</span>
          <div>
            <p class="brand-title">NIRA Dashboard</p>
            <p class="brand-sub">Digital Policy Feedback</p>
          </div>
        </div>
        <p class="side-label">THEME</p>
        <span class="theme-buttons"></span>
        """,
        unsafe_allow_html=True,
    )
    mode = st.session_state.theme
    light, dark = st.sidebar.columns(2)
    choose = None
    if light.button(
        ":material/light_mode: Light",
        key="theme_light",
        type="primary" if mode == "light" else "secondary",
        width="stretch",
    ):
        choose = "light"
    if dark.button(
        ":material/circle: Dark",
        key="theme_dark",
        type="primary" if mode == "dark" else "secondary",
        width="stretch",
    ):
        choose = "dark"
    if choose and choose != st.session_state.theme:
        st.session_state.theme = choose
        st.rerun()
    st.sidebar.markdown(
        """
        <div class="author-block">
          <p class="side-label">AUTHOR</p>
          <div class="author-row">
            <span class="avatar">AR</span>
            <p class="author-name">Ahmed Abdi Rage</p>
          </div>
          <p class="author-note">Simple research dashboard for NIRA policy feedback.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


render_sidebar()
apply_theme()

navigation = st.navigation(
    [
        st.Page(overview, title="Overview", icon=":material/home:", default=True),
        st.Page(exploration, title="Data Exploration", icon=":material/query_stats:"),
        st.Page(topics, title="Topics", icon=":material/category:"),
        st.Page(classification, title="Classification", icon=":material/account_tree:"),
        st.Page(feedback_loop, title="Feedback Loop", icon=":material/sync:"),
        st.Page(quality, title="Data Quality", icon=":material/verified:"),
    ]
)
navigation.run()
