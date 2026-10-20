const DATA = window.NIRA;
const MODELS = {
  complement_nb: "Complement naive Bayes",
  logistic_regression: "Logistic regression",
  linear_svc: "Linear SVC",
  multinomial_nb: "Multinomial naive Bayes",
  embedding_logistic: "Embedding logistic regression",
};
const TASKS = {
  policy_relevance: "Policy relevance",
  feedback_type: "Feedback type",
  topic: "Manual topic",
  sentiment: "Sentiment",
};
const GROUPS = {
  annotated_manual_vs_predicted: "Annotated: manual versus predicted",
  unlabeled_raw_with_prediction: "Unlabeled raw comments",
  additional_predicted_comments: "Further predicted comments",
};
const PAGES = [
  ["overview", "Overview", "home"],
  ["exploration", "Data Exploration", "query_stats"],
  ["topics", "Topics", "category"],
  ["classification", "Classification", "account_tree"],
  ["loop", "Feedback Loop", "sync"],
  ["quality", "Data Quality", "verified"],
];
const esc = (value) => String(value ?? "—").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
const num = (value) => Number(value).toLocaleString("en-US");
const f1 = (value) => Number(value).toFixed(3);
const pct = (value) => `${(Number(value) * 100).toFixed(1)}%`;
const modelName = (key) => MODELS[key] || key;
const blank = (value) => (value === null || value === undefined || value === "" ? "—" : esc(value));
const page = () => {
  const name = (location.hash || "#overview").slice(1);
  return PAGES.some(([id]) => id === name) ? name : "overview";
};

function hero(icon, kicker, title, text) {
  return `<section class="hero">
    <p class="kicker"><span class="mi">${icon}</span>${esc(kicker)}</p>
    <h1>${esc(title)}</h1>
    <p>${esc(text)}</p>
  </section>`;
}
function guide(items) {
  return `<aside class="panel guide"><p class="guide-title"><span class="mi">info</span>What this page shows</p>${items.map(([icon, text]) => `<p><span class="mi">${icon}</span>${esc(text)}</p>`).join("")}</aside>`;
}
function heading(icon, title) {
  return `<h2><span class="mi">${icon}</span>${esc(title)}</h2>`;
}
function metric(icon, label, value) {
  return `<article class="panel metric"><span class="mi">${icon}</span><b>${value}</b><span>${esc(label)}</span></article>`;
}
function table(headers, rows) {
  return `<div class="panel table-wrap"><table><thead><tr>${headers.map((header) => `<th>${esc(header)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr class="${row.winner ? "winner" : ""}">${row.cells.map((cell) => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}
const charts = [];
function chart(labels, values, title, horizontal = false) {
  const id = `chart-${charts.length}`;
  charts.push({ id, labels, values, title, horizontal });
  return `<div id="${id}" class="chart"></div>`;
}
function groupedChart(labels, series, title) {
  const id = `chart-${charts.length}`;
  charts.push({ id, labels, series, title, grouped: true });
  return `<div id="${id}" class="chart chart-tall"></div>`;
}
function drawCharts() {
  const ink = document.documentElement.dataset.theme === "dark" ? "#e7f3fb" : "#0e2a43";
  charts.forEach((spec) => {
    const node = document.getElementById(spec.id);
    if (!node || !window.Plotly) return;
    const traces = spec.grouped
      ? spec.series.map(([name, values, color]) => ({ type: "bar", name, x: spec.labels, y: values, marker: { color } }))
      : [spec.horizontal
        ? { type: "bar", orientation: "h", x: spec.values, y: spec.labels, marker: { color: "#1d6fb8" } }
        : { type: "bar", x: spec.labels, y: spec.values, marker: { color: "#1d6fb8" } }];
    Plotly.newPlot(node, traces, {
      title: { text: spec.title, font: { size: 16, family: "Poppins", color: ink }, x: 0, xanchor: "left" },
      barmode: spec.grouped ? "group" : "relative",
      height: spec.grouped ? 420 : spec.horizontal ? Math.max(280, spec.labels.length * 28) : 320,
      margin: spec.grouped ? { l: 16, r: 16, t: 48, b: 64 } : { l: 8, r: 12, t: 40, b: 8 },
      font: { family: "Poppins", size: 14, color: ink },
      plot_bgcolor: "rgba(0,0,0,0)",
      paper_bgcolor: "rgba(0,0,0,0)",
      legend: spec.grouped ? { orientation: "h", yanchor: "top", y: -0.18, x: 0, xanchor: "left", font: { size: 14, family: "Poppins" } } : { orientation: "h" },
      xaxis: { showgrid: false, automargin: true },
      yaxis: { gridcolor: "rgba(29,111,184,0.15)", automargin: true },
    }, { responsive: true, displayModeBar: true });
  });
}

function renderOverview() {
  const selected = DATA.overview.selected_models;
  const topic = DATA.topics.selection;
  const direct = (DATA.loop.linkage.find((row) => row.linkage_class === "directly linked") || { n_posts: 0 }).n_posts;
  const sentiment = DATA.classification.distribution.filter((row) => row.task === "sentiment");
  const manual = sentiment.filter((row) => row.scope === "manual_annotated");
  const predicted = sentiment.filter((row) => row.scope === "refit_prediction_on_all_comments");
  return `${hero("home", "NIRA · RESEARCH DASHBOARD", "National ID Policy Feedback", "Saved results for the Facebook comment corpus: annotation, topic models, classifiers, and the response register.")}
    ${guide([
      ["database", "Raw comments, manual annotations, and model predictions are three different counts."],
      ["category", "The cited topic model is the function-word LDA run, not the earlier NMF run."],
      ["sync", "A shared topic or a nearby date is a comparison. It is not evidence that one item caused the next."],
    ])}
    <div class="metrics metrics-6">
      ${metric("database", "Raw Facebook comments", num(DATA.overview.raw_comments))}
      ${metric("edit_note", "Manually annotated", num(DATA.overview.annotated_comments))}
      ${metric("model_training", "Comments with a prediction", num(DATA.overview.raw_comments))}
      ${metric("category", "Cited LDA topics", num(topic.n_topics))}
      ${metric("campaign", "Source posts", num(DATA.overview.source_posts))}
      ${metric("link_off", "Directly linked posts", num(direct))}
    </div>
    ${heading("calendar_month", "When the comments were collected, and when the posts were published")}
    <p class="muted">Collection day is the day the file was gathered. Publication year comes from the researcher-verified register, not from the collection timestamp.</p>
    <div class="split">
      <article class="panel">${chart(DATA.exploration.collection_days.map((row) => row.collection_day), DATA.exploration.collection_days.map((row) => row.n_comments), "Comments by collection day")}</article>
      <article class="panel">${chart(DATA.exploration.publication_years.map((row) => String(row.publication_year)), DATA.exploration.publication_years.map((row) => row.n_comments), "Comments by source-post publication year")}</article>
    </div>
    ${heading("category", "Cited topic sizes")}
    <article class="panel">${chart([...DATA.topics.terms].sort((a, b) => b.n_comments - a.n_comments).map((row) => `Topic ${row.topic_id}`), [...DATA.topics.terms].sort((a, b) => b.n_comments - a.n_comments).map((row) => row.n_comments), `${topic.selected_family} ${topic.selected_setting} · ${num(topic.unassigned_comments)} comments unassigned`)}</article>
    ${heading("mood", "Sentiment: manual labels and full-corpus predictions")}
    <p class="muted">The left series is the 1,199 manual labels. The right series is the selected model applied to all 5,292 comments. Predicted labels are not ground truth.</p>
    <article class="panel">${groupedChart(
      [...new Set([...manual, ...predicted].map((row) => row.label))],
      [
        ["Manual · 1,199", [...new Set([...manual, ...predicted].map((row) => row.label))].map((label) => (manual.find((row) => row.label === label) || { n: 0 }).n), "#0b4f86"],
        ["Predicted · 5,292", [...new Set([...manual, ...predicted].map((row) => row.label))].map((label) => (predicted.find((row) => row.label === label) || { n: 0 }).n), "#7ec8f8"],
      ],
      "Sentiment counts",
    )}</article>
    ${heading("account_tree", "Model used for each supervised task")}
    <div class="cards-4">${Object.entries(selected).map(([task, model]) => {
      const score = DATA.classification.heldout.find((row) => row.task === task);
      return `<article class="panel card"><p class="eyebrow">${esc(TASKS[task])}</p><h3>${esc(modelName(model))}</h3><p>Validation macro-F1 ${f1(score.validation_macro_f1)}</p><p>Test macro-F1 ${f1(score.test_macro_f1)}</p></article>`;
    }).join("")}</div>
    <details class="expander" open>
      <summary>Methodological limits</summary>
      <ul>
        <li>Only ${num(DATA.overview.annotated_comments)} of ${num(DATA.overview.raw_comments)} comments have a manual label (${(DATA.overview.annotated_share * 100).toFixed(1)} percent), because the time available for manual annotation was limited. The other 4,093 comments were not annotated and have predictions only.</li>
        <li>No stance task was annotated or modelled.</li>
        <li>BERTopic uses paraphrase-multilingual-MiniLM-L12-v2. That embedding does not show that the model understands Somali.</li>
        <li>Embedding scores do not establish that the multilingual model understands Somali.</li>
        <li>Directly linked posts in the response register: ${num(direct)}. Pre/post shares are descriptive.</li>
        <li>A codebook and a second coder are not part of the saved study files.</li>
      </ul>
    </details>`;
}

function renderExploration() {
  const raw = DATA.exploration.lengths.find((row) => row.group === "raw_corpus");
  return `${hero("query_stats", "DATA EXPLORATION", "What the files contain", "The raw file has five columns. Collection time and publication date are kept apart. Repeated comment IDs were not deleted.")}
    ${guide([
      ["table", "Dimensions, missing cells, and the duplicate-identifier check."],
      ["straighten", "Comment length from the saved length summary."],
      ["filter_alt", "The 19 posts can be filtered. Full comment text is not listed here."],
    ])}
    <div class="metrics">
      ${metric("database", "Rows in the raw file", num(raw.n_comments))}
      ${metric("view_column", "Raw columns", "5")}
      ${metric("check", "Blank comments", "0")}
      ${metric("content_copy", "Exact duplicate rows", "0")}
    </div>
    ${heading("table", "Missing cells in the raw file")}
    ${table(["Column", "Empty cells"], ["comment_id", "comment", "platform", "post_url", "collection_date"].map((name) => ({ cells: [name, "0"] })))}
    ${heading("key", "Identifier check")}
    <article class="callout">comment_id is unique within each stripped post_url and restarts at 1 on every post. Global repetition is not sufficient evidence of a duplicate comment. No rows were removed.</article>
    <div class="cards-3">
      ${metric("key", "Unique comment_id values", "1,013")}
      ${metric("content_copy", "Rows whose comment_id also appears elsewhere", "4,279")}
      ${metric("check", "Duplicate comment_id inside one post", "0")}
    </div>
    <p class="muted">Each of the 19 posts has a single collection timestamp. These values describe data collection, not source-post publication.</p>
    ${heading("straighten", "Comment length")}
    <div class="metrics">
      ${metric("straighten", "Median characters", num(raw.median_chars))}
      ${metric("short_text", "Under 30 characters", num(raw.under_30_chars))}
      ${metric("notes", "Over 280 characters", num(raw.over_280_chars))}
      ${metric("call", "Phone-like patterns, redacted", num(raw.phone_like))}
    </div>
    ${heading("calendar_month", "Collection days")}
    <article class="panel">${chart(DATA.exploration.collection_days.map((row) => row.collection_day), DATA.exploration.collection_days.map((row) => row.n_comments), "Collection is not publication")}</article>
    ${heading("public", "Platform")}
    <article class="panel">${chart(["Facebook"], [raw.n_comments], "Platform values in the raw file")}</article>
    ${heading("list_alt", "19 source posts")}
    <div id="post-tools"></div>`;
}

function renderTopics() {
  const selection = DATA.topics.selection;
  return `${hero("category", "TOPIC MODELING", `Cited model: ${selection.selected_family} ${selection.selected_setting}`, `${selection.selection_rule} Manual topic labels were not the training target.`)}
    ${guide([
      ["emoji_events", "LDA k=6 is the cited model because it had the highest coherence among coverage-eligible candidates."],
      ["compare", "NMF, LDA, and BERTopic from the function-word run are in one comparison table."],
      ["abc", "Top terms are statistical word forms, not confirmed policy-theme names."],
    ])}
    <article class="callout"><strong><span class="mi">emoji_events</span>${esc(selection.selected_family)} ${esc(selection.selected_setting)} · coherence ${f1(selection.coherence_c_npmi)} · coverage ${pct(selection.coverage)}</strong><br>Unassigned comments: ${num(selection.unassigned_comments)} of ${num(selection.comments_in_corpus)}. Terms are statistical word forms, not validated theme names.</article>
    <div class="metrics">
      ${metric("category", "Topics in the cited model", num(selection.n_topics))}
      ${metric("verified", "Coherence c_npmi", f1(selection.coherence_c_npmi))}
      ${metric("pie_chart", "Coverage", pct(selection.coverage))}
      ${metric("help", "Unassigned comments", num(selection.unassigned_comments))}
    </div>
    ${heading("table_chart", "Candidates in the cited run")}
    <article class="panel">${chart(
      DATA.topics.comparison.map((row) => `${row.family} ${row.setting}`),
      DATA.topics.comparison.map((row) => row.coherence_c_npmi),
      "Coherence in the filtered comparison",
      true,
    )}</article>
    ${table(["Family", "Setting", "Topics", "Coherence", "Diversity", "Coverage", "Status"], DATA.topics.comparison.map((row) => {
      const winner = row.family === "LDA" && row.setting === "k=6";
      const eligible = Number(row.coverage) >= 0.8;
      return { winner, cells: [esc(row.family), esc(row.setting), num(row.n_topics), f1(row.coherence_c_npmi), f1(row.topic_diversity), pct(row.coverage), winner ? "Selected" : eligible ? "Compared" : "Below 80 percent coverage"] };
    }))}
    ${heading("abc", "Cited topic terms and sizes")}
    <div class="topics">${[...DATA.topics.terms].sort((a, b) => b.n_comments - a.n_comments).map((row) => `<article class="panel card"><p class="eyebrow">Topic ${esc(row.topic_id)} · ${num(row.n_comments)} comments</p><h3>${esc(row.top_terms)}</h3></article>`).join("")}</div>
    <details class="expander">
      <summary>How this differs from the manual topic labels</summary>
      <ul>
        <li>The six topics above were discovered from all ${num(selection.comments_in_corpus)} comments.</li>
        <li>The supervised topic task uses eight manual categories. Those categories were not the topic-model target.</li>
        <li>BERTopic in this run covered ${pct(DATA.topics.comparison.find((row) => row.family === "BERTopic").coverage)}, so it was not coverage-eligible.</li>
        <li>${esc(selection.language_limitation)}</li>
      </ul>
    </details>`;
}

function renderClassification() {
  const winners = DATA.overview.selected_models;
  const winner = winners[selectedTask];
  const score = DATA.classification.heldout.find((row) => row.task === selectedTask);
  const taskRows = DATA.classification.validation.filter((row) => row.task === selectedTask).sort((a, b) => a.macro_f1 - b.macro_f1);
  const matrix = DATA.classification.confusion[selectedTask];
  const scopes = [["manual_annotated", "Manual labels, 1,199"], ["refit_prediction_on_all_comments", "Selected model on all 5,292"]];
  return `${hero("account_tree", "CLASSIFICATION", "Four tasks, selected on validation macro-F1", "The test split was scored after the model was chosen. Labels on all 5,292 comments come from a refit on the 1,199 annotated rows.")}
    ${guide([
      ["compare_arrows", "Agreement between the 1,199 human labels and the predictions on those same comments."],
      ["bar_chart", "Validation scores for the five compared models."],
      ["grid_on", "Held-out precision, recall, F1, and the test confusion matrix."],
    ])}
    ${heading("compare_arrows", "Agreement with the human labels")}
    <article class="callout"><strong>These matches are on the 1,199 annotated comments only.</strong> The model was refit on those labels first, so this agreement is not the test score. The other 4,093 comments have a prediction and no human label.</article>
    ${table(["Task", "Model", "Matching comments", "Accuracy", "Agreement macro-F1", "Test macro-F1"], DATA.classification.refit.map((row) => ({ cells: [esc(TASKS[row.task]), esc(modelName(row.selected_model)), `${num(Math.round(row.refit_agreement_accuracy * 1199))} of 1,199`, f1(row.refit_agreement_accuracy), f1(row.refit_agreement_macro_f1), f1(row.heldout_test_macro_f1)] })))}
    <label class="field">Task
      <select id="task-select">${Object.entries(TASKS).map(([key, label]) => `<option value="${key}" ${key === selectedTask ? "selected" : ""}>${esc(label)}</option>`).join("")}</select>
    </label>
    <div class="metrics">
      ${metric("account_tree", "Selected model", modelName(winner))}
      ${metric("verified", "Validation macro-F1", f1(score.validation_macro_f1))}
      ${metric("science", "Test macro-F1", f1(score.test_macro_f1))}
      ${metric("target", "Test accuracy", f1(score.test_accuracy))}
    </div>
    <p class="muted">Seed 42. Test labels were not used to select the model. Split for every task: train 839, validation 120, test 240.</p>
    ${heading("bar_chart", `Validation macro-F1 · ${TASKS[selectedTask]}`)}
    <article class="panel">${chart(taskRows.map((row) => modelName(row.model)), taskRows.map((row) => row.macro_f1), "Blue bar is the selected model", true)}</article>
    ${heading("table_chart", "Validation scores")}
    ${table(["Model", "Macro-F1", "Weighted-F1", "Accuracy", "Role"], taskRows.slice().reverse().map((row) => ({ winner: row.model === winner, cells: [esc(modelName(row.model)), f1(row.macro_f1), f1(row.weighted_f1), pct(row.accuracy), row.model === winner ? "Selected" : "Compared"] })))}
    ${heading("grid_on", "Test confusion matrix for the model that was used")}
    <article class="panel"><h3>${esc(TASKS[selectedTask])} · ${esc(modelName(winner))}</h3><div class="table-wrap"><table><thead><tr><th>Manual</th>${matrix.labels.map((label) => `<th>${esc(label)}</th>`).join("")}</tr></thead><tbody>${matrix.rows.map((row, index) => `<tr><td>${esc(matrix.labels[index])}</td>${row.map((cell) => `<td>${num(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table></div></article>
    ${heading("label", "Manual labels beside full-corpus predictions")}
    <div class="split">${scopes.map(([scope, title]) => `<div><h3>${esc(title)}</h3>${table(["Label", "Comments", "Share"], DATA.classification.distribution.filter((row) => row.scope === scope && row.task === selectedTask).map((row) => ({ cells: [esc(row.label), num(row.n), pct(row.share)] })))}</div>`).join("")}</div>
    ${heading("forum", "30 comments, side by side")}
    <p class="muted">${num(DATA.classification.overlap.unique_record_keys)} unique comments. Overlap between the three groups is ${num(DATA.classification.overlap.overlap_between_samples)}. Every comment has a prediction from the selected model for that task.</p>
    <div class="chips" id="group-filters">
      <button class="chip is-on" data-group="all" type="button">All 30</button>
      <button class="chip" data-group="annotated_manual_vs_predicted" type="button">Annotated 10</button>
      <button class="chip" data-group="unlabeled_raw_with_prediction" type="button">Unlabeled 10</button>
      <button class="chip" data-group="additional_predicted_comments" type="button">Further 10</button>
    </div>
    <input class="search" id="comment-search" placeholder="Search the 30 comments" aria-label="Search the 30 comments">
    <p class="muted" id="comment-count"></p>
    <div id="comment-list"></div>`;
}

function commentRows(rows) {
  const field = { policy_relevance: "policy_relevance", feedback_type: "feedback_type", topic: "topic", sentiment: "sentiment" }[selectedTask];
  return table(
    ["Post", "Group", "Excerpt", "Manual label", "Prediction"],
    rows.map((row) => ({ cells: [esc(row.post_id), esc(GROUPS[row.sample_group]), esc(row.excerpt), blank(row.manual[field]), blank(row.predicted[field])] })),
  );
}

function bindPosts() {
  const host = document.querySelector("#post-tools");
  if (!host) return;
  const classes = [...new Set(DATA.exploration.posts.map((row) => row.linkage_class))].sort();
  let chosen = new Set(classes);
  host.innerHTML = `<div class="chips" id="link-filters">${classes.map((name) => `<button class="chip is-on" type="button" data-link="${esc(name)}">${esc(name)}</button>`).join("")}</div>
    <input class="search" id="post-search" placeholder="Search post, account, or period" aria-label="Search post, account, or period">
    <p class="muted" id="post-count"></p>
    <div id="post-table"></div>
    <div id="post-chart"></div>`;
  const draw = () => {
    const query = document.querySelector("#post-search").value.trim().toLowerCase();
    const rows = DATA.exploration.posts.filter((row) => chosen.has(row.linkage_class) && `${row.post_id} ${row.account_name_register} ${row.event_period}`.toLowerCase().includes(query));
    const total = rows.reduce((sum, row) => sum + Number(row.n_comments), 0);
    document.querySelector("#post-count").textContent = `${rows.length} ${rows.length === 1 ? "post" : "posts"} · ${num(total)} comments in this filter`;
    document.querySelector("#post-table").innerHTML = table(["Post", "Date", "Account", "Comments", "Annotated", "Period", "Linkage"], rows.map((row) => ({ cells: [esc(row.post_id), esc(row.publication_date_register), esc(row.account_name_register), num(row.n_comments), num(row.n_annotated), esc(row.event_period), esc(row.linkage_class)] })));
    const chartHost = document.querySelector("#post-chart");
    chartHost.innerHTML = rows.length ? `<article class="panel"><div id="filtered-posts" class="chart"></div></article>` : "";
    if (rows.length && window.Plotly) {
      Plotly.newPlot("filtered-posts", [{ type: "bar", orientation: "h", x: rows.map((row) => row.n_comments), y: rows.map((row) => row.post_id), marker: { color: "#1d6fb8" } }], {
        title: { text: "Comments in the filtered posts", font: { size: 16, family: "Poppins" }, x: 0, xanchor: "left" },
        height: Math.max(280, rows.length * 28),
        margin: { l: 8, r: 12, t: 40, b: 8 },
        font: { family: "Poppins", size: 14 },
        plot_bgcolor: "rgba(0,0,0,0)",
        paper_bgcolor: "rgba(0,0,0,0)",
        xaxis: { showgrid: false, automargin: true },
        yaxis: { showgrid: false, automargin: true, type: "category" },
      }, { responsive: true, displayModeBar: true });
    }
  };
  host.querySelectorAll("[data-link]").forEach((button) => {
    button.addEventListener("click", () => {
      const name = button.dataset.link;
      if (chosen.has(name) && chosen.size > 1) chosen.delete(name);
      else chosen.add(name);
      button.classList.toggle("is-on", chosen.has(name));
      draw();
    });
  });
  document.querySelector("#post-search").addEventListener("input", draw);
  draw();
}

function renderLoop() {
  const cards = [
    ["campaign", "POST_01 · 27 Oct 2025", "Universal Somali TV. Queues, hours, and fees. 1,013 comments. Thematic comparison with RESP_001. The SONNA page does not name POST_01."],
    ["account_balance", "RESP_001 · 3 Nov 2025", "SONNA. The Director General addresses night queues. Same-day temporal link with POST_09, 212 comments."],
    ["campaign", "POST_04 · 4 Nov 2025", "505 comments about alleged unofficial payments. Thematic comparison with RESP_001 and RESP_002."],
    ["account_balance", "RESP_002 · 10 Nov 2025", "NIRA. Wadajir day-and-night center. Names no corpus post."],
  ];
  return `${hero("sync", "FEEDBACK LOOP", "Communication, comments, and later notices", "The register can place a post beside a later notice. It does not show that the notice caused a change in the comments.")}
    ${guide([
      ["timeline", "The dated comparison: POST_01, RESP_001, POST_09, POST_04, and RESP_002."],
      ["link", "Linkage class: thematic, same-day, or unlinked. Directly linked posts are 0."],
      ["date_range", "Pre-event, event-day, and post-event counts. The date is the post’s publication date."],
      ["pie_chart", "Predicted label shares by period. They do not measure an effect of RESP_001."],
    ])}
    ${heading("timeline", "Dated comparison")}
    <div class="cards-4">${cards.map(([icon, title, text]) => `<article class="panel card"><p class="eyebrow"><span class="mi">${icon}</span>${esc(title)}</p><p>${esc(text)}</p></article>`).join("")}</div>
    <img class="figure" style="margin-top:14px" alt="Feedback-loop sequence around RESP_001" src="../outputs/07_events_timeline/20261019_events/figures/feedback_loop_sequence.png">
    ${heading("link", "Linkage classes")}
    ${table(["Class", "Posts"], DATA.loop.linkage.map((row) => ({ cells: [esc(row.linkage_class), num(row.n_posts)] })))}
    ${heading("date_range", "Pre-event and post-event")}
    <article class="callout"><strong>This split is not an effect of RESP_001.</strong> A comment inherits the publication date of its source post. Collection date is not used.</article>
    ${table(["Period", "Posts", "Comments", "Annotated"], DATA.loop.periods.map((row) => ({ cells: [esc(row.event_period), num(row.n_posts), num(row.n_comments), num(row.n_annotated)] })))}
    ${heading("article", "Posts the register names beside an inventory row")}
    ${table(["Post", "Date", "Comments", "Class", "Compared with"], DATA.loop.named_posts.map((row) => ({ cells: [esc(row.post_id), esc(row.publication_date), num(row.n_comments), esc(row.linkage_class), esc(row.comparison_response_ids)] })))}
    ${heading("pie_chart", "Predicted label shares by period")}
    <p class="muted">These shares describe the selected model in each period. They do not measure an effect of RESP_001.</p>
    ${table(["Period", "Task", "Label", "Comments", "Share"], DATA.loop.shares.map((row) => ({ cells: [esc(row.event_period), esc(TASKS[row.task] || row.task), esc(row.label), num(row.n), pct(row.share)] })))}`;
}

function renderQuality() {
  const correction = DATA.quality.corrections[0];
  const raw = DATA.exploration.lengths.find((row) => row.group === "raw_corpus");
  return `${hero("verified", "DATA QUALITY", "What was checked and what stays limited", "The raw file and the annotation workbook were not overwritten. Predictions are model output, not corrected ground truth.")}
    ${guide([
      ["fact_check", "Text match for the 1,199 annotated comments: 1,174 exact, 12 spacing or line breaks, and 13 content differences."],
      ["space_bar", "The 12 spacing comments stayed in training. Whitespace was collapsed before the model saw them."],
      ["edit_note", "The registered correction for ANN_0031. The original file was not changed and the models were not retrained."],
      ["balance", "How common each manual label is inside the 1,199."],
    ])}
    ${heading("fact_check", "Text match")}
    <div class="cards-3">${DATA.quality.text_match.map((row) => metric("fact_check", row.text_match_status, num(row.n_comments))).join("")}</div>
    <p class="muted"><span class="mi">space_bar</span>The 12 spacing comments stayed in training. Whitespace was collapsed before the model saw them.</p>
    <article class="callout"><strong><span class="mi">edit_note</span>${esc(correction.annotation_id)} sentiment</strong><br>${esc(correction.original_value)} was registered as ${esc(correction.corrected_value)} on ${esc(correction.corrected_on)}. ${esc(correction.reason)} The original workbook was not changed, and the models were not retrained.</article>
    <div class="split">
      <article class="panel card"><h3><span class="mi">key</span>Identifiers</h3><p>comment_id restarts inside each post. The join key is the stripped post URL plus the comment id. Collection date is the collection time, never the publication date.</p></article>
      <article class="panel card"><h3><span class="mi">translate</span>Language</h3><p>${num(raw.phone_like)} raw comments matched a phone pattern and are redacted. Arabic script: ${num(raw.arabic_script)}. Styled Latin: ${num(raw.styled_latin)}. Embedding scores do not show that the multilingual model understands Somali.</p></article>
    </div>
    ${heading("balance", "Annotated class balance")}
    ${table(["Field", "Classes", "Largest", "Count", "Smallest", "Count"], DATA.quality.balance.map((row) => ({ cells: [esc(row.field), num(row.n_classes), esc(row.largest_class), num(row.largest_n), esc(row.smallest_class), num(row.smallest_n)] })))}`;
}

let selectedTask = "policy_relevance";
const RENDER = { overview: renderOverview, exploration: renderExploration, topics: renderTopics, classification: renderClassification, loop: renderLoop, quality: renderQuality };

function bindComments() {
  const list = document.querySelector("#comment-list");
  if (!list) return;
  const count = document.querySelector("#comment-count");
  const search = document.querySelector("#comment-search");
  let group = "all";
  const draw = () => {
    const query = search.value.trim().toLowerCase();
    const rows = DATA.classification.comments.filter((row) => (group === "all" || row.sample_group === group) && row.excerpt.toLowerCase().includes(query));
    list.innerHTML = commentRows(rows);
    count.textContent = `${rows.length} of 30 comments shown`;
  };
  document.querySelectorAll("#group-filters .chip").forEach((button) => {
    button.addEventListener("click", () => {
      group = button.dataset.group;
      document.querySelectorAll("#group-filters .chip").forEach((item) => item.classList.toggle("is-on", item === button));
      draw();
    });
  });
  search.addEventListener("input", draw);
  draw();
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem("nira-theme", theme);
  document.querySelectorAll(".theme-switch [data-theme]").forEach((button) => button.classList.toggle("is-on", button.dataset.theme === theme));
}

function render() {
  const current = page();
  charts.length = 0;
  document.body.classList.toggle("page-classification", current === "classification");
  document.title = `${PAGES.find(([id]) => id === current)[1]} · NIRA Research Dashboard`;
  document.querySelector("#nav").innerHTML = PAGES.map(([id, label, icon]) => `<button class="nav-btn ${current === id ? "is-on" : ""}" data-page="${id}" type="button"><span class="mi">${icon}</span>${esc(label)}</button>`).join("");
  document.querySelector("#page").innerHTML = RENDER[current]();
  drawCharts();
  document.querySelectorAll(".nav-btn").forEach((button) => button.addEventListener("click", () => { location.hash = button.dataset.page; }));
  const taskSelect = document.querySelector("#task-select");
  if (taskSelect) taskSelect.addEventListener("change", () => { selectedTask = taskSelect.value; render(); });
  bindComments();
  bindPosts();
}

document.querySelectorAll(".theme-switch [data-theme]").forEach((button) => button.addEventListener("click", () => applyTheme(button.dataset.theme)));
applyTheme(localStorage.getItem("nira-theme") || "light");
window.addEventListener("hashchange", render);
render();
