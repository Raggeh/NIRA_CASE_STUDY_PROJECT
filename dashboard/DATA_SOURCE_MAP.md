# NIRA Streamlit dashboard

The application is `dashboard/streamlit_app.py`. It reads saved outputs through `dashboard/nira_data.py` and does not refit models or overwrite the raw CSV or the annotation workbook.

`NIRA_Research_Dashboard_Cleaned_FIXED.py` is not in this project. The Google Colab notebook `NIRA_Google_Colab.ipynb` already launches `dashboard/streamlit_app.py`.

Backup of the previous application:

- `dashboard/backup/streamlit_app_before_redesign.py`
- `dashboard/backup/nira_data_before_redesign.py`

## Data sources

| Artifact | Path | Page | What it supplies | Rows / status |
| --- | --- | --- | --- | --- |
| EDA findings | `outputs/02_eda/20261018_eda/eda_findings.json` | Overview, Exploration | 5,292 comments, 1,199 annotated, 19 posts, collection days, publication years | Loaded |
| Post summary | `outputs/02_eda/20261018_eda/eda_post_summary.csv` | Exploration, Feedback | Per-post counts and publication dates | 19 posts |
| Length summary | `outputs/02_eda/20261018_eda/eda_length_summary.csv` | Exploration, Quality | Median length, short comments, phone-like count | Raw and annotated groups |
| Raw quality | `outputs/01_data_preparation/20261018_content_review/raw_quality_summary.json` | Exploration, Quality | Missing cells, duplicates, platform, date rule | 5,292 rows, 0 blank, 0 exact duplicates |
| Annotation relation | `outputs/03_annotation/20261018_annotation/annotation_relation.json` | Quality | Match counts, no codebook, no second coder | 1,199 keys matched |
| Text match | `outputs/03_annotation/20261018_annotation/annotation_text_match_counts.csv` | Quality | Exact, spacing, and content differences | Loaded |
| Correction register | `outputs/03_annotation/20261018_annotation/annotation_corrections.csv` | Quality | ANN_0031 sentiment register | Original file unchanged |
| Class balance | `outputs/03_annotation/20261018_annotation/annotation_class_balance.csv` | Quality | Largest and smallest manual class by field | Loaded |
| Cited topic selection | `outputs/04_topic_modeling/20261019_topic_models_function_words/topic_model_selection.json` | Overview, Topics | LDA k=6 | Cited solution |
| Topic comparison | `outputs/04_topic_modeling/20261019_topic_models_function_words/topic_model_comparison.csv` | Topics | NMF, LDA, BERTopic | BERTopic below 80% coverage |
| Topic terms | `outputs/04_topic_modeling/20261019_topic_models_function_words/selected_topic_terms.csv` | Overview, Topics | Six term lists and sizes | Loaded |
| Topic examples | `outputs/04_topic_modeling/20261019_topic_models_function_words/selected_topic_examples.csv` | Topics | Representative excerpts | Phone-like text redacted |
| Topic assignments | `outputs/04_topic_modeling/20261019_topic_models_function_words/topic_assignments.csv` | Quality | Assigned 5,076, unassigned 216 | 5,292 rows |
| Prior topic run | `outputs/04_topic_modeling/20261019_topic_models/topic_model_selection.json` | Topics | Earlier NMF k=6 | Kept, not cited |
| Embedding note | `outputs/04_topic_modeling/20261019_topic_models/embedding_model.json` | Overview, Classification | MiniLM model name and limit | Not an XLM-RoBERTa result |
| Selected models | `outputs/05_model_development/20261019_supervised/selected_models.json` | Overview, Classification, Quality | Winners, seed 42 | Test not used for selection |
| Validation scores | `outputs/05_model_development/20261019_supervised/validation_scores.csv` | Classification | Five models, four tasks | Loaded |
| Held-out scores | `outputs/05_model_development/20261019_supervised/heldout_test_scores.csv` | Classification | Test macro-F1 and accuracy | Loaded |
| Classification report | `outputs/05_model_development/20261019_supervised/heldout_classification_reports.json` | Classification | Precision, recall, F1, support | Selected models only |
| Confusion matrices | `outputs/05_model_development/20261019_supervised/test_confusion_*.csv` | Classification | Test counts | Four tasks |
| Split sizes | `outputs/05_model_development/20261019_supervised/split_sizes.csv` | Classification | 839 / 120 / 240 | Loaded |
| Corpus predictions | `outputs/06_results_predictions/20261019_predictions/corpus_predictions.csv` | Overview, Quality | Prediction coverage | 5,292 unique keys, 1,199 annotated |
| Label distribution | `outputs/06_results_predictions/20261019_predictions/label_distribution_comparison.csv` | Overview, Classification | Manual versus predicted counts | Loaded |
| Refit agreement | `outputs/06_results_predictions/20261019_predictions/refit_agreement.csv` | Classification | Not a test score | Loaded |
| Comparison sample | `outputs/06_results_predictions/20261019_predictions/comment_comparison_sample.csv` | Exploration, Classification | 30 excerpts | No group overlap |
| Post timeline | `outputs/07_events_timeline/20261019_events/post_timeline.csv` | Exploration, Feedback | Linkage and evidence status | 19 posts |
| Period tables | `outputs/07_events_timeline/20261019_events/event_period_summary.csv` and `predicted_label_shares_by_event_period.csv` | Feedback | Pre, event day, post | Descriptive, not causal |
| Response inventory | `outputs/07_events_timeline/20261019_events/response_inventory_timeline.csv` | Feedback | RESP_001 to RESP_005 | Loaded |
| Source check | `outputs/07_events_timeline/20261019_source_check/source_check.json` | Feedback | POST_17 and POST_18 screenshot captions | Audio not transcribed |
| Feedback figure | `outputs/07_events_timeline/20261019_events/figures/feedback_loop_sequence.png` | Feedback | Sequence figure | Loaded |

## Changes

- Kept the six pages and the blue Poppins layout, with a shorter header and KPI cards that wrap.
- Sidebar brand, theme switch, six icon links, and the author block stay in one column. The nav can scroll.
- Added charts for collection day, publication year, topic size, sentiment, model coherence, validation scores, confusion, period counts, and predicted shares.
- Added filters for posts, topic family, classification task, comment group, and event period.
- Added the quality checks, ANN_0031 register, seed, and the statement that a repeated `comment_id` is not a duplicate row.
- Phone-like excerpts are redacted. Stance and XLM-RoBERTa are stated as absent rather than filled in.

## Bugs found and fixed

- The validation-status table mixed numbers and true/false values, so Arrow refused the column. Results are now text.
- The collection-day chart was drawn on a continuous date axis. Bars are now categorical.
- The sidebar label “THEME” was clipped by the measured markdown height. It is now its own block.
- A one-row post filter said “1 posts”. It now says “1 post”.

## Test report

Tested in the browser at `http://127.0.0.1:8502` on 19 October 2026.

| Check | Result |
| --- | --- |
| Overview | Loaded. Counts 5,292, 1,199, 5,292 predictions, 6 topics, 19 posts, 0 direct links. Model scores match the saved file. |
| Data Exploration | Loaded. Missing cells are 0. Exact duplicates are 0. Within-post duplicate IDs are 0. Search `POST_08` returned 1 post and 236 comments. |
| Topics | Loaded. LDA k=6 and BERTopic are on the page. No exception. |
| Classification | Loaded. Policy-relevance test macro-F1 0.491 is on the page. No exception. |
| Feedback Loop | Loaded. POST_08 date 2026-07-06, POST_17 qualifier, and the sequence figure are present. |
| Data Quality | Loaded after the Arrow fix. The status table shows 5,292 raw rows. ANN_0031 is on the page. |
| Dark theme | Main background became `#0d2233` and cards `#14324a`. |
| Mobile width 390 | No page-level horizontal scroll. KPI cards wrap. Sidebar collapses and can be opened; all six links remain available. |
| Phone numbers | No phone number was rendered in the checked page text. |

The script starts, and each page was opened. A filter was exercised on Data Exploration. The other filters were present in the page; they were not each clicked.

## Launch in Google Colab

Open `NIRA_Google_Colab.ipynb` from the project folder and run the cells in order. The notebook installs Streamlit, pandas, NumPy, and Plotly, checks the saved files, and starts:

```bash
streamlit run dashboard/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

On this computer:

```bash
python -m streamlit run dashboard/streamlit_app.py --server.port 8501
```

Then open `http://localhost:8501`.

## Limits that remain

- Stance was not annotated or modelled.
- No XLM-RoBERTa evaluation is stored. The embedding model is `paraphrase-multilingual-MiniLM-L12-v2`.
- The full raw comment file is not listed, because comments can contain phone numbers.
- Pre/post shares do not measure an effect of RESP_001.
- POST_17 and POST_18 captions come from researcher screenshots. The POST_17 reel audio was not transcribed.
- POST_08 remains 2026-07-06 and unlinked.
- The cited topic model is LDA k=6 from `20261019_topic_models_function_words`. The earlier NMF run is not the cited solution.
