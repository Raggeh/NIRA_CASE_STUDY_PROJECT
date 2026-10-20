"""NIRA research dashboard. Reads saved outputs and does not refit models."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nira_data import GROUP_NAMES, TASK_NAMES, load, model_name

st.set_page_config(page_title="NIRA Research Dashboard", page_icon="N", layout="wide")

PALETTE = ["#0b4f86", "#1d6fb8", "#3d97d4", "#7ec8f8", "#9fd4f5", "#d5ebf8"]


@st.cache_data(show_spinner=False)
def data():
    # Reload when the saved-output loader changes. Do not reuse an older cache.
    return load()


def ink():
    return "#d7e8f6" if st.session_state.get("theme") == "dark" else "#0e2a43"


def layout(figure, height=320):
    figure.update_layout(
        height=height,
        margin=dict(l=8, r=12, t=40, b=8),
        font=dict(family="Poppins", size=13, color=ink()),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="rgba(29,111,184,0.15)")
    return figure


def bar_chart(labels, values, title, horizontal=False):
    if horizontal:
        figure = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color="#1d6fb8"))
    else:
        figure = go.Figure(go.Bar(x=labels, y=values, marker_color="#1d6fb8"))
    figure.update_layout(title=dict(text=title, font=dict(size=16)))
    figure = layout(figure, 280 if horizontal else 320)
    if horizontal:
        figure.update_yaxes(type="category")
    else:
        figure.update_xaxes(type="category")
    return figure


def kpis(items):
    cards = []
    for icon, value, label in items:
        cards.append(
            f'<article class="kpi" style="box-sizing:border-box;padding:26px 22px 22px 44px;min-height:168px;">'
            f'<span class="mi">{icon}</span><b>{value}</b><small>{label}</small></article>'
        )
    st.markdown(f'<div class="kpi-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def hero(kicker, title, text, icon):
    st.markdown(
        f"""
        <div class="hero">
          <p class="kicker"><span class="hero-icon mi">{icon}</span>{kicker}</p>
          <h1>{title}</h1>
          <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def guide(items):
    with st.container(border=True):
        st.markdown('<span class="guide-mark"></span>', unsafe_allow_html=True)
        st.markdown(":material/info: **What this page shows**")
        for icon, text in items:
            st.markdown(f":material/{icon}: {text}")


def section(icon, title):
    st.markdown(f"### :material/{icon}: {title}")


def apply_theme():
    mode = "dark" if st.session_state.get("theme") == "dark" else "light"
    st.markdown(
        """
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Material+Symbols+Rounded" />
        <style>
        .stApp { background: #f3f8fc; overflow-x: hidden; }
        [data-testid="stMainBlockContainer"] {
          padding-top: 0.35rem !important;
          max-width: none !important;
          width: 100% !important;
        }
        .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp button, .stApp label,
        .stApp a, .stApp li, .stApp input, [data-testid="stMarkdownContainer"],
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stCaptionContainer"],
        .hero, .hero h1, .hero p, .brand-title, .brand-sub, .author-name, .author-note, .side-label, .kpi, .kpi b, .kpi small {
          font-family: "Poppins", sans-serif !important;
        }
        .mi, .hero-icon, [data-testid="stIconMaterial"], .material-symbols-rounded {
          font-family: "Material Symbols Rounded" !important;
          font-weight: normal !important;
          font-style: normal !important;
          letter-spacing: normal !important;
          line-height: 1;
        }
        [data-testid="stSidebar"] {
          background: linear-gradient(180deg, #0c4f86 0%, #08345c 100%);
          width: 248px !important;
          min-width: 248px !important;
          overflow-x: hidden;
          overflow-y: auto;
        }
        [data-testid="stSidebarHeader"] {
          height: auto !important;
          min-height: 0 !important;
          padding: 4px 8px 0 !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] a {
          color: #e8f4fc;
        }
        [data-testid="stSidebarContent"] {
          display: flex; flex-direction: column; height: auto; min-height: 100%;
          max-height: none; overflow: visible; padding: 4px 10px 12px; box-sizing: border-box;
        }
        [data-testid="stSidebarNav"] {
          order: 4; flex: 0 0 auto; min-height: 0; max-height: none;
          overflow: visible; padding: 2px 0 8px;
        }
        [data-testid="stSidebarNav"] ul { display: flex; flex-direction: column; gap: 4px; margin: 0; padding: 0; }
        [data-testid="stSidebarNav"]::-webkit-scrollbar { width: 8px; }
        [data-testid="stSidebarNav"]::-webkit-scrollbar-thumb { background: rgba(232, 244, 252, 0.45); border-radius: 8px; }
        [data-testid="stSidebarNav"] a {
          border-radius: 12px;
          border: 1px solid rgba(214, 232, 248, 0.45);
          padding: 0.38rem 0.7rem;
          background: rgba(6, 32, 58, 0.28);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] { background: #1d6fb8; border-color: #7ec8f8; }
        [data-testid="stSidebarNav"] a, [data-testid="stSidebarNav"] a span { font-size: 15px !important; }
        [data-testid="stSidebarNav"] a [data-testid="stIconMaterial"] { font-size: 18px !important; }
        .hero {
          background: linear-gradient(120deg, #0b4f86 0%, #1d7ed6 58%, #7ec8f8 130%);
          color: white; border-radius: 18px; border-top-left-radius: 22px; border-top-right-radius: 22px;
          padding: 22px 26px 18px; margin-bottom: 12px;
          position: relative; overflow: hidden;
        }
        .hero:after {
          content: ""; position: absolute; right: -24px; top: -40px; width: 120px; height: 120px;
          border-radius: 50%; background: rgba(255,255,255,0.12);
        }
        .hero .kicker { letter-spacing: 0.08em; font-size: 12px; opacity: 0.9; margin: 0 0 6px; }
        .hero h1 { margin: 0 0 8px; font-size: 30px; letter-spacing: -0.03em; line-height: 1.15; }
        .hero p { margin: 0; max-width: 820px; font-size: 15px; line-height: 1.45; color: rgba(255,255,255,0.94); }
        .hero-icon { font-size: 20px; vertical-align: -3px; margin-right: 8px; }
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 8px 0 14px; }
        .kpi { background: white; border: 1px solid #d5e8f6; border-radius: 16px; padding: 26px 22px 22px 44px !important; min-height: 168px !important; height: auto !important; box-sizing: border-box !important; box-shadow: 0 8px 20px rgba(12, 79, 134, 0.05); overflow: visible; }
        .kpi .mi { color: #1d6fb8; font-size: 20px; display: block; line-height: 1; margin-bottom: 11px; }
        .kpi b { display: block; margin: 0; font-size: 28px; color: #0b4f86; line-height: 1.1; }
        .kpi small { display: block; margin-top: 4px; color: #3e627f; font-size: 13px; line-height: 1.3; }
        [data-testid="stMetric"] {
          background: white; border: 1px solid #d5e8f6; border-radius: 16px;
          padding: 12px 16px 14px !important; min-height: 96px; height: auto !important; overflow: visible !important;
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"] { overflow: visible !important; }
        [data-testid="stMetricLabel"] p { font-size: 13px !important; margin-top: 2px !important; }
        [data-testid="stMetricValue"] { line-height: 1.1; padding-bottom: 0; font-size: 28px !important; }
        [data-testid="stMain"] [data-testid="stElementContainer"]:has([data-testid="stMetric"]),
        [data-testid="stMain"] [data-testid="stElementContainer"]:has([data-testid="stMetric"]) > div {
          height: auto !important; overflow: visible !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:not(:has(.guide-mark)) {
          background: white; border: 1px solid #d5e8f6; border-radius: 20px; padding: 26px 24px 22px 44px !important;
        }
        div[data-testid="stAlert"], div[data-testid="stNotification"] {
          background: #e7f4fc !important; color: #0e3d66 !important; border: 0 !important; border-left: 4px solid #2b8fd6 !important;
        }
        .guide-mark { display: none; }
        [data-testid="stVerticalBlockBorderWrapper"]:has(.guide-mark) { border-left: 4px solid #2b8fd6 !important; }
        [data-testid="stVerticalBlock"]:has(.guide-mark):not(:has([data-testid="stVerticalBlock"])) {
          border-top-left-radius: 18px !important;
          border-top-right-radius: 18px !important;
          padding: 14px 16px 12px !important;
        }
        [data-testid="stVerticalBlock"]:has(.guide-mark):not(:has([data-testid="stVerticalBlock"])) [data-testid="stMarkdownContainer"] p {
          font-size: 14px !important;
          line-height: 1.4;
        }
        [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stMain"] [data-testid="stCaptionContainer"] p { font-size: 14px; line-height: 1.4; }
        [data-testid="stMain"] h3 { font-size: 18px; margin-top: 0.15rem; }
        [data-testid="stSidebar"] { position: relative; }
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarUserContent"] > div,
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] { display: contents; }
        [data-testid="stSidebar"] [data-testid="stMarkdown"],
        [data-testid="stSidebar"] [data-testid="stMarkdown"] > div,
        [data-testid="stSidebar"] [data-testid="stElementContainer"] { height: auto !important; min-height: 0; overflow: visible !important; }
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.brand-block),
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.brand-block) > div,
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.brand-block) [data-testid="stMarkdown"],
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.brand-block) [data-testid="stMarkdown"] > div {
          height: auto !important; min-height: 44px !important; overflow: visible !important;
        }
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.brand-block) { order: 1; flex: 0 0 auto; }
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.theme-label) { order: 2; flex: 0 0 auto; }
        [data-testid="stSidebar"] [data-testid="stLayoutWrapper"] { order: 3; flex: 0 0 auto; margin: 6px 0 2px; }
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.author-block),
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.author-block) > div,
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.author-block) [data-testid="stMarkdown"],
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.author-block) [data-testid="stMarkdown"] > div {
          height: auto !important; min-height: 96px !important; overflow: visible !important;
        }
        [data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.author-block) {
          order: 5; flex: 0 0 auto; margin-top: 0; padding: 12px 2px 8px;
          border-top: 1px solid rgba(214, 232, 248, 0.28);
        }
        .brand-block { display: flex; gap: 8px; align-items: center; min-height: 44px; padding: 0 2px 2px; }
        .logo-n, .avatar { display: grid; place-items: center; color: white; font-weight: 700; flex: 0 0 auto; }
        .logo-n { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(145deg, #7ec8f8, #1d6fb8); font-size: 16px; }
        [data-testid="stSidebar"] .brand-title { margin: 0; font-size: 16px !important; font-weight: 700; line-height: 1.15; color: white; }
        [data-testid="stSidebar"] .brand-sub, [data-testid="stSidebar"] .author-note { margin: 2px 0 0; color: #d5e9f8 !important; font-size: 12px !important; }
        [data-testid="stSidebar"] .side-label { margin: 10px 0 0; color: #9ec8e8 !important; font-size: 11px !important; letter-spacing: 0.14em; font-weight: 700; }
        [data-testid="stSidebar"] .stButton button {
          border-radius: 999px; min-height: 40px; font-size: 15px; padding: 8px 14px !important;
        }
        [data-testid="stSidebar"] button [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] button [data-testid="stMarkdownContainer"] p {
          overflow: visible !important; text-overflow: clip !important; white-space: nowrap !important; width: auto !important;
        }
        [data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] { background: transparent; color: #e8f4fc; border: 1px solid rgba(232,244,252,0.45); }
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] { background: #1d6fb8; color: white; border: 0; }
        .author-block { padding-bottom: 8px; }
        .author-row { display: flex; align-items: center; gap: 10px; margin-top: 8px; }
        .avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(145deg, #7ec8f8, #1d6fb8); font-size: 13px; }
        [data-testid="stSidebar"] .author-name { margin: 0; font-size: 15px !important; font-weight: 700; color: white; }
        .theme-flag { display: none; }
        .stApp:has(.theme-dark) { background: #0d2233; color: #e7f3fb; }
        .stApp:has(.theme-dark) [data-testid="stAppViewContainer"],
        .stApp:has(.theme-dark) [data-testid="stMain"],
        .stApp:has(.theme-dark) [data-testid="stHeader"] { background: #0d2233; }
        .stApp:has(.theme-dark) .kpi,
        .stApp:has(.theme-dark) [data-testid="stMetric"],
        .stApp:has(.theme-dark) [data-testid="stVerticalBlockBorderWrapper"] { background: #14324a; border-color: #2a5d86; }
        .stApp:has(.theme-dark) .kpi b, .stApp:has(.theme-dark) .kpi small { color: #e7f3fb; }
        .stApp:has(.theme-dark) [data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
        .stApp:has(.theme-dark) [data-testid="stMain"] h3,
        .stApp:has(.theme-dark) [data-testid="stMetricValue"],
        .stApp:has(.theme-dark) [data-testid="stMetricLabel"],
        .stApp:has(.theme-dark) [data-testid="stCaptionContainer"] p,
        .stApp:has(.theme-dark) [data-testid="stWidgetLabel"] p,
        .stApp:has(.theme-dark) [data-testid="stRadio"] label,
        .stApp:has(.theme-dark) [data-testid="stTextInput"] label,
        .stApp:has(.theme-dark) [data-testid="stMultiSelect"] label { color: #e7f3fb; }
        .stApp:has(.theme-dark) div[data-testid="stAlert"],
        .stApp:has(.theme-dark) div[data-testid="stNotification"] { background: #e7f4fc !important; color: #0e3d66 !important; }
        .stApp:has(.theme-dark) div[data-testid="stAlert"] p,
        .stApp:has(.theme-dark) div[data-testid="stAlert"] span,
        .stApp:has(.theme-dark) div[data-testid="stNotification"] p { color: #0e3d66 !important; }
        .stApp:has(.theme-dark) .hero, .stApp:has(.theme-dark) .hero p, .stApp:has(.theme-dark) .hero h1 { color: white; }
        .page-classification { display: none; }
        .stApp:has(.page-classification) .kpi b { font-size: 22px; }
        .stApp:has(.page-classification) .kpi small { font-size: 13px; }
        .stApp:has(.page-classification) .hero h1 { font-size: 30px; }
        .stApp:has(.page-classification) .hero p { font-size: 15px; }
        .stApp:has(.page-classification) .hero .kicker { font-size: 13px; }
        .stApp:has(.page-classification) h3 { font-size: 18px; }
        @media (max-width: 800px) {
          .hero h1 { font-size: 24px; }
          .hero p { font-size: 14px; }
          .kpi b { font-size: 22px; }
          [data-testid="stSidebarNav"] { max-height: none; }
          [data-testid="stSidebarNav"] a, [data-testid="stSidebarNav"] a span { font-size: 15px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="theme-flag theme-{mode}"></div>', unsafe_allow_html=True)


def overview():
    bundle = data()
    eda = bundle["eda"]
    selection = bundle["topic_selection"]
    hero(
        "NIRA · RESEARCH DASHBOARD",
        "National ID Policy Feedback",
        "Saved results for the Facebook comment corpus: annotation, topic models, classifiers, and the response register.",
        "home",
    )
    guide([
        ("database", "Raw comments, manual annotations, and model predictions are three different counts."),
        ("category", "The cited topic model is the function-word LDA run, not the earlier NMF run."),
        ("sync", "A shared topic or a nearby date is a comparison. It is not evidence that one item caused the next."),
    ])
    kpis([
        ("database", f"{eda['raw_comments']:,}", "Raw Facebook comments"),
        ("edit_note", f"{eda['annotated_comments']:,}", "Manually annotated"),
        ("model_training", f"{bundle['n_predictions']:,}", "Comments with a prediction"),
        ("category", str(selection["n_topics"]), "Cited LDA topics"),
        ("campaign", str(eda["source_posts"]), "Source posts"),
        ("link_off", str(bundle["period_definition"]["directly_linked_posts"]), "Directly linked posts"),
    ])
    section("calendar_month", "When the comments were collected, and when the posts were published")
    st.caption("Collection day is the day the file was gathered. Publication year comes from the researcher-verified register, not from the collection timestamp.")
    left, right = st.columns(2)
    days = eda["collection_days"]
    years = eda["publication_year_comment_counts"]
    left.plotly_chart(
        bar_chart([row["collection_day"] for row in days], [row["n_comments"] for row in days], "Comments by collection day"),
        width="stretch",
    )
    right.plotly_chart(
        bar_chart([str(row["publication_year"]) for row in years], [row["n_comments"] for row in years], "Comments by source-post publication year"),
        width="stretch",
    )
    section("category", "Cited topic sizes")
    terms = bundle["topic_terms"].sort_values("n_comments", ascending=False)
    st.plotly_chart(
        bar_chart(
            [f"Topic {int(row.topic_id)}" for row in terms.itertuples()],
            [int(row.n_comments) for row in terms.itertuples()],
            f"{selection['selected_family']} {selection['selected_setting']} · {selection['unassigned_comments']:,} comments unassigned",
        ),
        width="stretch",
    )
    section("mood", "Sentiment: manual labels and full-corpus predictions")
    st.caption("The left series is the 1,199 manual labels. The right series is the selected model applied to all 5,292 comments. Predicted labels are not ground truth.")
    sentiment = bundle["distribution"].loc[bundle["distribution"]["task"] == "sentiment"].copy()
    manual = sentiment.loc[sentiment["scope"] == "manual_annotated"]
    predicted = sentiment.loc[sentiment["scope"] == "refit_prediction_on_all_comments"]
    figure = go.Figure()
    figure.add_bar(name="Manual · 1,199", x=manual["label"], y=manual["n"], marker_color="#0b4f86")
    figure.add_bar(name="Predicted · 5,292", x=predicted["label"], y=predicted["n"], marker_color="#7ec8f8")
    figure.update_layout(
        barmode="group",
        height=420,
        margin=dict(l=16, r=16, t=48, b=64),
        title=dict(text="Sentiment counts", font=dict(size=16, family="Poppins", color=ink()), x=0, xanchor="left", y=0.98, yanchor="top"),
        legend=dict(orientation="h", yanchor="top", y=-0.18, x=0, xanchor="left", font=dict(size=14, family="Poppins")),
        font=dict(family="Poppins", size=14, color=ink()),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    figure.update_xaxes(showgrid=False, automargin=True)
    figure.update_yaxes(gridcolor="rgba(29,111,184,0.15)", automargin=True)
    st.plotly_chart(figure, width="stretch")
    section("account_tree", "Model used for each supervised task")
    cards = st.columns(4)
    for column, (task, model) in zip(cards, bundle["winners"].items()):
        body = bundle["selected"]["tasks"][task]
        with column.container(border=True):
            st.caption(TASK_NAMES[task])
            st.markdown(f"**{model_name(model)}**")
            st.caption(f"Validation macro-F1 {body['validation_macro_f1']:.3f}")
            st.caption(f"Test macro-F1 {body['test_macro_f1']:.3f}")
    with st.expander("Methodological limits"):
        st.markdown(
            f"- Only {eda['annotated_comments']:,} of {eda['raw_comments']:,} comments have a manual label "
            f"({eda['annotated_share_of_raw'] * 100:.1f} percent), because the time available for manual annotation was limited. "
            "The other 4,093 comments were not annotated and have predictions only.\n"
            "- No stance task was annotated or modelled.\n"
            f"- BERTopic uses {bundle['embedding']['model_name']}. "
            "That embedding does not show that the model understands Somali.\n"
            f"- {bundle['embedding']['limitation']}\n"
            "- Directly linked posts in the response register: "
            f"{bundle['period_definition']['directly_linked_posts']}. Pre/post shares are descriptive.\n"
            "- A codebook and a second coder are not part of the saved study files."
        )


def exploration():
    bundle = data()
    quality = bundle["quality"]
    hero(
        "DATA EXPLORATION",
        "What the files contain",
        "The raw file has five columns. Collection time and publication date are kept apart. Repeated comment IDs were not deleted.",
        "query_stats",
    )
    guide([
        ("table", "Dimensions, missing cells, and the duplicate-identifier check."),
        ("straighten", "Comment length from the saved length summary."),
        ("filter_alt", "The 19 posts can be filtered. Full comment text is not listed here."),
    ])
    kpis([
        ("database", f"{quality['raw_rows']:,}", "Rows in the raw file"),
        ("view_column", str(len(quality["columns"])), "Raw columns"),
        ("check", str(quality["blank_comments"]), "Blank comments"),
        ("content_copy", str(quality["full_row_duplicates"]), "Exact duplicate rows"),
    ])
    section("table", "Missing cells in the raw file")
    missing = pd.DataFrame(
        [{"column": name, "empty_cells": count} for name, count in quality["empty_cells_by_column"].items()]
    )
    st.dataframe(missing, width="stretch", hide_index=True)
    section("key", "Identifier check")
    st.info(quality["decision_comment_id"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Unique comment_id values", f"{quality['unique_comment_id']:,}")
    c2.metric("Rows whose comment_id also appears elsewhere", f"{quality['duplicate_comment_id_rows']:,}")
    c3.metric("Duplicate comment_id inside one post", quality["within_post_duplicate_comment_id"])
    st.caption(quality["decision_collection_date"])
    section("straighten", "Comment length")
    length = quality["comment_char_len"]
    kpis([
        ("straighten", f"{length['median']:.0f}", "Median characters"),
        ("short_text", f"{quality['comments_under_30_characters']:,}", "Under 30 characters"),
        ("notes", f"{quality['comments_over_280_characters']:,}", "Over 280 characters"),
        ("call", str(quality["comments_with_phone_like_pattern"]), "Phone-like patterns, redacted"),
    ])
    section("calendar_month", "Collection days")
    days = bundle["eda"]["collection_days"]
    st.plotly_chart(
        bar_chart([row["collection_day"] for row in days], [row["n_comments"] for row in days], "Collection is not publication"),
        width="stretch",
    )
    section("public", "Platform")
    platforms = bundle["quality"]["platform_values"]
    st.plotly_chart(bar_chart(list(platforms), list(platforms.values()), "Platform values in the raw file"), width="stretch")
    section("list_alt", "19 source posts")
    posts = bundle["posts"].copy()
    classes = sorted(posts["linkage_class"].dropna().unique())
    chosen = st.multiselect("Linkage class", classes, default=classes)
    query = st.text_input("Search post, account, or period")
    view = posts.loc[posts["linkage_class"].isin(chosen)] if chosen else posts.iloc[0:0]
    if query:
        blob = view.fillna("").astype(str).agg(" ".join, axis=1)
        view = view.loc[blob.str.contains(query, case=False, na=False)]
    show = view[
        [
            "post_id",
            "publication_date_register",
            "account_name_register",
            "n_comments",
            "n_annotated",
            "event_period",
            "linkage_class",
        ]
    ]
    post_word = "post" if len(show) == 1 else "posts"
    st.caption(f"{len(show)} {post_word} · {int(show['n_comments'].sum()) if len(show) else 0:,} comments in this filter")
    st.dataframe(show, width="stretch", hide_index=True)
    if len(show):
        st.plotly_chart(
            bar_chart(show["post_id"].tolist(), show["n_comments"].tolist(), "Comments in the filtered posts", horizontal=True),
            width="stretch",
        )
    section("forum", "Representative comments")
    st.caption("These 30 excerpts are the saved comparison sample. Phone-like text is redacted. The full raw comment file is not shown on this page.")
    sample = bundle["sample"].copy()
    sample["group"] = sample["sample_group"].map(GROUP_NAMES)
    comment_query = st.text_input("Search the 30 excerpts", key="explore_search")
    if comment_query:
        sample = sample.loc[sample["excerpt"].str.contains(comment_query, case=False, na=False)]
    st.dataframe(sample[["post_id", "group", "excerpt"]], width="stretch", hide_index=True)


def topics():
    bundle = data()
    selection = bundle["topic_selection"]
    prior = bundle["prior_topic_selection"]
    hero(
        "TOPIC MODELING",
        f"Cited model: {selection['selected_family']} {selection['selected_setting']}",
        selection["selection_rule"] + " Manual topic labels were not the training target.",
        "category",
    )
    guide([
        ("emoji_events", "LDA k=6 is the cited model because it had the highest coherence among coverage-eligible candidates."),
        ("compare", "NMF, LDA, and BERTopic from the function-word run are in one comparison table."),
        ("abc", "Top terms are statistical word forms, not confirmed policy-theme names."),
    ])
    kpis([
        ("category", str(selection["n_topics"]), "Topics in the cited model"),
        ("verified", f"{selection['coherence_c_npmi']:.3f}", "Coherence c_npmi"),
        ("pie_chart", f"{selection['coverage'] * 100:.1f}%", "Coverage"),
        ("help", f"{selection['unassigned_comments']:,}", "Unassigned comments"),
    ])
    section("table_chart", "Candidates in the cited run")
    comparison = bundle["topic_comparison"].copy()
    families = ["All families"] + sorted(comparison["family"].unique())
    family = st.selectbox("Model family", families)
    shown = comparison if family == "All families" else comparison.loc[comparison["family"] == family]
    shown = shown.copy()
    shown["status"] = shown.apply(
        lambda row: "Selected"
        if row["family"] == selection["selected_family"] and row["setting"] == selection["selected_setting"]
        else ("Coverage-eligible" if row["coverage"] >= 0.8 else "Below 80 percent coverage"),
        axis=1,
    )
    chart = shown.sort_values("coherence_c_npmi")
    colors = ["#0b4f86" if status == "Selected" else "#7ec8f8" if status == "Coverage-eligible" else "#d5ebf8" for status in chart["status"]]
    figure = go.Figure(
        go.Bar(
            x=chart["coherence_c_npmi"],
            y=chart["family"] + " " + chart["setting"],
            orientation="h",
            marker_color=colors,
            hovertemplate="%{y}<br>c_npmi %{x:.3f}<extra></extra>",
        )
    )
    figure.update_layout(title=dict(text="Coherence in the filtered comparison", font=dict(size=16)), xaxis_title="c_npmi")
    st.plotly_chart(layout(figure, 360), width="stretch")
    st.dataframe(shown, width="stretch", hide_index=True)
    section("abc", "Cited topic terms and sizes")
    terms = bundle["topic_terms"].sort_values("n_comments", ascending=False)
    columns = st.columns(3)
    for index, row in enumerate(terms.itertuples(index=False)):
        with columns[index % 3].container(border=True):
            st.caption(f"Topic {int(row.topic_id)} · {int(row.n_comments):,} comments")
            st.write(row.top_terms)
    topic_choice = st.selectbox(
        "Representative comments for one cited topic",
        ["All cited topics"] + [str(int(topic)) for topic in sorted(bundle["examples"]["topic_id"].unique())],
    )
    examples = bundle["examples"].copy()
    if topic_choice != "All cited topics":
        examples = examples.loc[examples["topic_id"] == int(topic_choice)]
    st.dataframe(examples[["topic_id", "post_id", "excerpt"]], width="stretch", hide_index=True)
    with st.expander("How this differs from the manual topic labels"):
        st.markdown(
            f"- The six topics above were discovered from all {selection['comments_in_corpus']:,} comments.\n"
            "- The supervised topic task uses eight manual categories. Those categories were not the topic-model target.\n"
            f"- BERTopic in this run covered {comparison.loc[comparison['family'] == 'BERTopic', 'coverage'].iloc[0] * 100:.1f} percent, "
            "so it was not coverage-eligible.\n"
            f"- An earlier run, `{selection['prior_run']}`, selected {prior['selected_family']} {prior['selected_setting']} "
            f"with coherence {prior['coherence_c_npmi']:.3f}. Its top terms were mostly function words. It is not the cited solution.\n"
            f"- {selection['language_limitation']}"
        )


def classification():
    st.markdown('<div class="page-classification"></div>', unsafe_allow_html=True)
    bundle = data()
    winners = bundle["winners"]
    hero(
        "CLASSIFICATION",
        "Four tasks, selected on validation macro-F1",
        "The test split was scored after the model was chosen. Labels on all 5,292 comments come from a refit on the 1,199 annotated rows.",
        "account_tree",
    )
    guide([
        ("compare_arrows", "Agreement between the 1,199 human labels and the predictions on those same comments."),
        ("bar_chart", "Validation scores for the five compared models."),
        ("grid_on", "Held-out precision, recall, F1, and the test confusion matrix."),
    ])
    section("compare_arrows", "Agreement with the human labels")
    st.warning("These matches are on the 1,199 annotated comments only. The model was refit on those labels first, so this agreement is not the test score. The other 4,093 comments have a prediction and no human label.")
    labeled = int(bundle["eda"]["annotated_comments"])
    agreement = bundle["refit"].copy()
    agreement["Task"] = agreement["task"].map(TASK_NAMES)
    agreement["Model"] = agreement["selected_model"].map(model_name)
    agreement["Matching comments"] = agreement["refit_agreement_accuracy"].map(lambda value: f"{int(round(value * labeled)):,} of {labeled:,}")
    agreement["Accuracy"] = agreement["refit_agreement_accuracy"].map(lambda value: f"{value:.3f}")
    agreement["Agreement macro-F1"] = agreement["refit_agreement_macro_f1"].map(lambda value: f"{value:.3f}")
    agreement["Test macro-F1"] = agreement["heldout_test_macro_f1"].map(lambda value: f"{value:.3f}")
    st.dataframe(
        agreement[["Task", "Model", "Matching comments", "Accuracy", "Agreement macro-F1", "Test macro-F1"]],
        width="stretch",
        hide_index=True,
    )
    task = st.selectbox("Task", list(TASK_NAMES), format_func=lambda key: TASK_NAMES[key])
    winner = winners[task]
    score = bundle["heldout"].loc[bundle["heldout"]["task"] == task].iloc[0]
    kpis([
        ("account_tree", model_name(winner), "Selected model"),
        ("verified", f"{score['validation_macro_f1']:.3f}", "Validation macro-F1"),
        ("science", f"{score['test_macro_f1']:.3f}", "Test macro-F1"),
        ("target", f"{score['test_accuracy']:.3f}", "Test accuracy"),
    ])
    splits = bundle["splits"].loc[bundle["splits"]["task"] == task]
    st.caption(
        "Split for this task: "
        + ", ".join(f"{row.split} {int(row.n_rows)}" for row in splits.itertuples())
        + f". Seed {bundle['selected']['seed']}. Test labels were not used to select the model."
    )
    section("bar_chart", f"Validation macro-F1 · {TASK_NAMES[task]}")
    rows = bundle["validation"].loc[bundle["validation"]["task"] == task].sort_values("macro_f1")
    colors = ["#0b4f86" if model == winner else "#c5dff3" for model in rows["model"]]
    figure = go.Figure(
        go.Bar(
            x=rows["macro_f1"],
            y=[model_name(model) for model in rows["model"]],
            orientation="h",
            marker_color=colors,
            text=rows["macro_f1"].map(lambda value: f"{value:.3f}"),
            textposition="outside",
            hovertemplate="%{y}<br>macro-F1 %{x:.3f}<extra></extra>",
        )
    )
    figure.update_layout(xaxis_title="Validation macro-F1", xaxis_range=[0, 0.8], title=dict(text="Blue bar is the selected model", font=dict(size=16)))
    st.plotly_chart(layout(figure, 280), width="stretch")
    scores = bundle["validation"].loc[bundle["validation"]["task"] == task].copy()
    scores["model_name"] = scores["model"].map(model_name)
    scores["role"] = scores["model"].map(lambda model: "Selected" if model == winner else "Compared")
    st.dataframe(scores[["model_name", "macro_f1", "weighted_f1", "accuracy", "role"]], width="stretch", hide_index=True)
    section("grid_on", "Held-out precision, recall, and F1 for the selected model")
    metrics = bundle["class_metrics"].loc[bundle["class_metrics"]["task"] == task].copy()
    metrics = metrics.loc[~metrics["label"].isin(["macro avg", "weighted avg"])]
    st.dataframe(metrics[["label", "precision", "recall", "f1", "support"]], width="stretch", hide_index=True)
    matrix = bundle["matrices"][task]
    heat = go.Figure(
        go.Heatmap(
            z=matrix.values,
            x=[f"Predicted {name}" for name in matrix.columns],
            y=[f"Manual {name}" for name in matrix.index],
            colorscale=[[0, "#e7f5fd"], [1, "#0b4f86"]],
            text=matrix.values,
            texttemplate="%{text}",
            hovertemplate="%{y}<br>%{x}<br>Count %{z}<extra></extra>",
            showscale=False,
        )
    )
    heat.update_layout(title=dict(text=f"Test confusion · {TASK_NAMES[task]} · {model_name(winner)}", font=dict(size=16)))
    st.plotly_chart(layout(heat, 360), width="stretch")
    section("label", "Manual labels beside full-corpus predictions")
    part = bundle["distribution"].loc[bundle["distribution"]["task"] == task]
    manual = part.loc[part["scope"] == "manual_annotated"]
    predicted = part.loc[part["scope"] == "refit_prediction_on_all_comments"]
    grouped = go.Figure()
    grouped.add_bar(name="Manual · 1,199", x=manual["label"], y=manual["n"], marker_color="#0b4f86")
    grouped.add_bar(name="Predicted · 5,292", x=predicted["label"], y=predicted["n"], marker_color="#7ec8f8")
    grouped.update_layout(
        barmode="group",
        height=460,
        margin=dict(l=16, r=16, t=64, b=110),
        title=dict(text=TASK_NAMES[task], font=dict(size=16, family="Poppins", color=ink()), x=0, xanchor="left", y=0.98, yanchor="top"),
        legend=dict(orientation="h", yanchor="top", y=-0.38, x=0, xanchor="left"),
        font=dict(family="Poppins", size=13, color=ink()),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    grouped.update_xaxes(showgrid=False, tickangle=-30, automargin=True)
    grouped.update_yaxes(gridcolor="rgba(29,111,184,0.15)", automargin=True)
    st.plotly_chart(grouped, width="stretch")
    section("forum", "30 comments, side by side")
    overlap = bundle["overlap"]
    st.caption(f"{overlap['unique_record_keys']} unique comments. Overlap between the three groups is {overlap['overlap_between_samples']}.")
    sample = bundle["sample"].copy()
    sample["group"] = sample["sample_group"].map(GROUP_NAMES)
    choice = st.radio("Comment group", ["All 30", "Annotated 10", "Unlabeled 10", "Further 10"], horizontal=True)
    group_key = {
        "Annotated 10": "annotated_manual_vs_predicted",
        "Unlabeled 10": "unlabeled_raw_with_prediction",
        "Further 10": "additional_predicted_comments",
    }.get(choice)
    if group_key:
        sample = sample.loc[sample["sample_group"] == group_key]
    query = st.text_input("Search the 30 comments", key="class_search")
    if query:
        sample = sample.loc[sample["excerpt"].str.contains(query, case=False, na=False)]
    manual_col = {
        "policy_relevance": "manual_policy_relevance",
        "feedback_type": "manual_feedback_type",
        "topic": "manual_topic",
        "sentiment": "manual_sentiment",
    }[task]
    pred_col = {
        "policy_relevance": "pred_policy_relevance",
        "feedback_type": "pred_feedback_type",
        "topic": "pred_topic",
        "sentiment": "pred_sentiment",
    }[task]
    table = sample[["post_id", "group", "excerpt", manual_col, pred_col]].rename(
        columns={manual_col: "Manual label", pred_col: "Prediction"}
    )
    st.caption(f"{len(table)} comments shown")
    st.dataframe(table, width="stretch", hide_index=True)


def feedback_loop():
    bundle = data()
    posts = bundle["posts"].set_index("post_id")
    hero(
        "FEEDBACK LOOP",
        "Communication, comments, and later notices",
        "The register can place a post beside a later notice. It does not show that the notice caused a change in the comments.",
        "sync",
    )
    guide([
        ("timeline", "The dated comparison around RESP_001, plus the wider response inventory."),
        ("link", "Linkage class is thematic, temporal, or unresolved. Direct links are zero."),
        ("warning", "POST_17 and POST_18 captions come from researcher screenshots. POST_08 stays dated 2026-07-06."),
    ])
    def post_line(post_id):
        row = posts.loc[post_id]
        return f"{post_id} · {row['publication_date_register']} · {int(row['n_comments']):,} comments · {row['linkage_class']}"

    a, b, c, d = st.columns(4)
    a.container(border=True).markdown(f"**{post_line('POST_01')}**\n\nThematic comparison with RESP_001. The SONNA page does not name this post.")
    b.container(border=True).markdown("**RESP_001 · 2025-11-03**\n\nSONNA. The Director General addresses night queues. This is an inventory notice, not a direct reply.")
    c.container(border=True).markdown(f"**{post_line('POST_09')}**\n\nSame registered date as RESP_001. A shared date is not a cause.")
    d.container(border=True).markdown(f"**{post_line('POST_04')}**\n\nThematic comparison with RESP_001 and RESP_002. No direct response is established.")
    st.caption(f"**RESP_002 · 2025-11-10.** NIRA notice. It names no corpus post. {post_line('POST_08')} remains unlinked.")
    if bundle["figure"].exists():
        st.image(str(bundle["figure"]), width="stretch")
    else:
        st.warning("The feedback-loop figure file is not in the saved outputs.")
    section("link", "Linkage classes")
    st.plotly_chart(
        bar_chart(bundle["linkage"]["linkage_class"].tolist(), bundle["linkage"]["n_posts"].tolist(), "Posts by linkage class"),
        width="stretch",
    )
    st.dataframe(bundle["linkage"], width="stretch", hide_index=True)
    section("date_range", "Counts around RESP_001")
    definition = bundle["period_definition"]
    st.warning(f"{definition['event_definition']} Date basis: {definition['date_basis']}. Collection date was not used. This split is not an effect of the notice.")
    st.plotly_chart(
        bar_chart(
            bundle["period_summary"]["event_period"].tolist(),
            bundle["period_summary"]["n_comments"].tolist(),
            "Comments by publication period of the source post",
        ),
        width="stretch",
    )
    st.dataframe(bundle["period_summary"], width="stretch", hide_index=True)
    section("pie_chart", "Predicted shares by period")
    st.caption("These shares describe the selected model. They do not measure an effect of RESP_001.")
    share_task = st.selectbox("Predicted task", list(TASK_NAMES), format_func=lambda key: TASK_NAMES[key], key="share_task")
    periods = ["All periods"] + bundle["period_shares"]["event_period"].drop_duplicates().tolist()
    period = st.selectbox("Period", periods)
    shares = bundle["period_shares"].loc[bundle["period_shares"]["task"] == share_task].copy()
    if period != "All periods":
        shares = shares.loc[shares["event_period"] == period]
    figure = go.Figure(
        go.Bar(
            x=shares["event_period"] + " · " + shares["label"],
            y=shares["share"],
            marker_color="#1d6fb8",
            hovertemplate="%{x}<br>share %{y:.3f}<br>n %{customdata}<extra></extra>",
            customdata=shares["n"],
        )
    )
    figure.update_layout(yaxis_title="Share of comments in the period", title=dict(text=TASK_NAMES[share_task], font=dict(size=16)))
    st.plotly_chart(layout(figure, 340), width="stretch")
    st.dataframe(shares[["event_period", "label", "n", "denominator", "share", "label_source"]], width="stretch", hide_index=True)
    section("article", "Response inventory")
    st.dataframe(
        bundle["responses"][["response_id", "source", "date", "title", "url", "evidence_status"]],
        width="stretch",
        hide_index=True,
    )
    section("screenshot", "Captions that were not recovered by the automated fetch")
    for row in bundle["source_posts"].itertuples(index=False):
        with st.container(border=True):
            st.markdown(f"**{row.post_id}**")
            st.write(row.result)
            st.caption(row.facebook_fetch)
    with st.expander("Evidence limits"):
        st.markdown(
            "- No inventoried communication is classed as a direct response to a source post or to a comment.\n"
            "- POST_17 reel audio was not transcribed.\n"
            "- POST_08 keeps the registered publication date 2026-07-06 and stays unlinked.\n"
            "- Complaint and request patterns in the period charts are predicted labels, not a new manual coding of those periods."
        )


def quality():
    bundle = data()
    quality = bundle["quality"]
    relation = bundle["relation"]
    hero(
        "DATA QUALITY",
        "Checks recorded with the files",
        "The raw file and the annotation workbook were not overwritten. A repeated comment ID is not treated as a duplicate row.",
        "verified",
    )
    guide([
        ("fact_check", "Missing cells, exact duplicates, and the comment-ID rule."),
        ("edit_note", "Annotation match, the ANN_0031 register, and prediction coverage."),
        ("settings", "The modelling seed and the checks that are absent."),
    ])
    kpis([
        ("database", f"{quality['raw_rows']:,}", "Raw rows"),
        ("check", str(quality["blank_comments"]), "Blank comments"),
        ("content_copy", str(quality["full_row_duplicates"]), "Exact duplicate rows"),
        ("key", str(quality["within_post_duplicate_comment_id"]), "Within-post duplicate IDs"),
    ])
    section("fact_check", "Validation status")
    status = pd.DataFrame(
        [
            ["Raw rows", quality["raw_rows"], "raw_quality_summary.json"],
            ["Blank comments", quality["blank_comments"], "raw_quality_summary.json"],
            ["Exact duplicate rows", quality["full_row_duplicates"], "raw_quality_summary.json"],
            ["Within-post duplicate comment_id", quality["within_post_duplicate_comment_id"], "raw_quality_summary.json"],
            ["Within-post duplicate comment text", quality["within_post_duplicate_comment_text"], "raw_quality_summary.json"],
            ["Unmatched annotation keys", relation["unmatched_annotation_keys"], "annotation_relation.json"],
            ["Prediction rows", bundle["n_predictions"], "corpus_predictions.csv"],
            ["Topic-assignment rows", int(bundle["assignment_counts"]["n_comments"].sum()), "topic_assignments.csv"],
            ["Random seed", bundle["selected"]["seed"], "selected_models.json"],
            ["Codebook file", relation["codebook_file_present"], "annotation_relation.json"],
            ["Second coder", relation["inter_annotator_agreement_available"], "annotation_relation.json"],
        ],
        columns=["check", "recorded_result", "source"],
    )
    status["recorded_result"] = status["recorded_result"].map(lambda value: "Yes" if value is True else "No" if value is False else str(value))
    st.dataframe(status, width="stretch", hide_index=True)
    st.info(quality["decision_comment_id"])
    section("fact_check", "Annotation text match")
    match_labels = {
        "exact": "Exact match",
        "content_difference": "Content difference",
        "newline_or_whitespace": "Spacing difference",
    }
    kpis([
        ("fact_check", f"{int(row.n_comments):,}", match_labels.get(row.text_match_status, row.text_match_status))
        for row in bundle["text_match"].itertuples(index=False)
    ])
    st.caption(relation["decision"])
    correction = bundle["corrections"].iloc[0]
    st.warning(
        f"{correction['annotation_id']} sentiment is registered as moving from {correction['original_value']} to {correction['corrected_value']} "
        f"on {correction['corrected_on']}. {correction['reason']} The original workbook was not changed, and the models were not retrained."
    )
    section("model_training", "Coverage of saved model outputs")
    left, right = st.columns(2)
    left.plotly_chart(
        bar_chart(
            ["Annotated and predicted", "Predicted only"],
            [bundle["n_predicted_annotated"], bundle["n_predictions"] - bundle["n_predicted_annotated"]],
            "Prediction file",
        ),
        width="stretch",
    )
    right.plotly_chart(
        bar_chart(
            bundle["assignment_counts"]["assignment_status"].astype(str).tolist(),
            bundle["assignment_counts"]["n_comments"].tolist(),
            "Topic-assignment status",
        ),
        width="stretch",
    )
    section("translate", "Language and contact details")
    raw = bundle["lengths"].loc[bundle["lengths"]["group"] == "raw_corpus"].iloc[0]
    st.write(
        f"{int(raw['phone_like'])} raw comments matched a phone pattern and are redacted on this dashboard. "
        f"Arabic script: {int(raw['arabic_script'])}. Styled Latin: {int(raw['styled_latin'])}. "
        "Embedding scores do not show that the multilingual model understands Somali."
    )
    section("balance", "Manual label balance inside the 1,199")
    st.caption("Each row is one annotated field. The largest class is the most common manual label in that field. Actor was annotated and was not one of the four modelled tasks.")
    balance = bundle["balance"]
    st.dataframe(balance, width="stretch", hide_index=True)
    st.plotly_chart(
        bar_chart(balance["field"].astype(str).tolist(), balance["largest_share_of_annotated"].tolist(), "Share of the largest manual class"),
        width="stretch",
    )


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
        """,
        unsafe_allow_html=True,
    )
    mode = st.session_state.theme
    light, dark = st.sidebar.columns(2)
    choose = None
    if light.button(":material/light_mode: Light", key="theme_light", type="primary" if mode == "light" else "secondary", width="stretch"):
        choose = "light"
    if dark.button(":material/dark_mode: Dark", key="theme_dark", type="primary" if mode == "dark" else "secondary", width="stretch"):
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
          <p class="author-note">Research dashboard for NIRA policy feedback.</p>
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
