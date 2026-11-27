# NIRA Streamlit dashboard

The application is `dashboard/streamlit_app.py`. It reads saved outputs through `dashboard/nira_data.py` and does not refit models or overwrite the raw CSV or the annotated file.

`NIRA_Research_Dashboard_Cleaned_FIXED.py` is not in this project. The Google Colab notebook `NIRA_Google_Colab.ipynb` already launches `dashboard/streamlit_app.py`.

## Data sources

| Artifact | Path | Page | What it supplies | Rows / status |
| --- | --- | --- | --- | --- |
| EDA findings | `outputs/02_eda/20261125_final/eda_findings.json` | Overview, Exploration | 5,292 comments, 3,500 annotated, 19 posts, collection days, publication years | Loaded |
| Post summary | `outputs/02_eda/20261125_final/eda_post_summary.csv` | Exploration, Feedback | Per-post counts and publication dates | 19 posts |
| Length summary | `outputs/02_eda/20261125_final/eda_length_summary.csv` | Exploration, Quality | Median length, short comments, phone-like count | Raw corpus, 5,292 comments |
| Annotation link | `outputs/01_data_preparation/20261125_final/annotation_linked.csv` | Quality | 3,500 final labels joined to the working corpus | From `NIRA_Project_Final_Annotation.xlsx` |
| Raw quality | `outputs/01_data_preparation/20261125_final/raw_quality_summary.json` | Exploration, Quality | Missing cells, duplicates, platform, date rule | 5,292 rows, 0 blank, 0 exact duplicates |
| Annotation relation | `outputs/03_annotation/20261125_final/annotation_relation.json` | Quality | Final labels from NIRA_Project_Final_Annotation.xlsx | 3,500 keys matched |
| Text match | `outputs/03_annotation/20261125_final/annotation_text_match_counts.csv` | Quality | Exact, spacing, and content differences | 3,475 exact, 12 spacing, 13 content |
| Correction register | `outputs/03_annotation/20261125_final/annotation_corrections.csv` | Quality | No correction-register row | Every annotated row has an annotation id |
| Class balance | `outputs/03_annotation/20261125_final/annotation_class_balance.csv` | Quality | Largest and smallest class by field | 3,500 rows |
| Cited topic selection | `outputs/04_topic_modeling/20261125_final/topic_model_selection.json` | Overview, Topics | NMF k=4 | Cited solution |
| Topic comparison | `outputs/04_topic_modeling/20261125_final/topic_model_comparison.csv` | Topics | LDA, NMF, LSA, and embedding models | NMF k=4 cited |
| Topic terms | `outputs/04_topic_modeling/20261125_final/selected_topic_terms.csv` | Overview, Topics | Four term lists and sizes | Loaded |
| Topic examples | `outputs/04_topic_modeling/20261125_final/selected_topic_examples.csv` | Topics | Representative excerpts | Phone-like text redacted |
| Topic assignments | `outputs/04_topic_modeling/20261125_final/topic_assignments.csv` | Quality | Assigned 5,211, unassigned 81 | 5,292 rows |
| Embedding note | `outputs/04_topic_modeling/20261125_final/embedding_model.json` | Overview, Classification | MiniLM model name and limit | Not an XLM-RoBERTa result |
| Selected models | `outputs/05_model_development/20261125_final/selected_models.json` | Overview, Classification, Quality | Winners, seed 42 | Test not used for selection |
| Validation scores | `outputs/05_model_development/20261125_final/validation_scores.csv` | Classification | Five models, four tasks | Loaded |
| Held-out scores | `outputs/05_model_development/20261125_final/heldout_test_scores.csv` | Classification | Test macro-F1 and accuracy | Loaded |
| Classification report | `outputs/05_model_development/20261125_final/heldout_classification_reports.json` | Classification | Precision, recall, F1, support | Selected models only |
| Confusion matrices | `outputs/05_model_development/20261125_final/test_confusion_*.csv` | Classification | Test counts | Four tasks |
| Split sizes | `outputs/05_model_development/20261125_final/split_sizes.csv` | Classification | 2,450 / 350 / 700 | Loaded |
| Corpus predictions | `outputs/06_results_predictions/20261125_final/corpus_predictions.csv` | Overview, Quality | Prediction coverage | 5,292 unique keys, 3,500 annotated |
| Label distribution | `outputs/06_results_predictions/20261125_final/label_distribution_comparison.csv` | Overview, Classification | Annotated versus predicted counts | Loaded |
| Refit agreement | `outputs/06_results_predictions/20261125_final/refit_agreement.csv` | Classification | Not a test score | Loaded |
| Comparison sample | `outputs/06_results_predictions/20261125_final/comment_comparison_sample.csv` | Exploration, Classification | 30 excerpts | No group overlap |
| Post timeline | `outputs/07_events_timeline/20261125_final/post_timeline.csv` | Exploration, Feedback | Linkage and evidence status | 19 posts |
| Period tables | `outputs/07_events_timeline/20261125_final/event_period_summary.csv` and `predicted_label_shares_by_event_period.csv` | Feedback | Pre, event day, post | 2,141 / 140 / 1,219 annotated |
| Response inventory | `outputs/07_events_timeline/20261125_final/response_inventory_timeline.csv` | Feedback | RESP_001 to RESP_005 | Loaded |
| Source check | `outputs/07_events_timeline/20261125_final/source_check.json` | Feedback | POST_17 and POST_18 screenshot captions | Audio not transcribed |
| Feedback figure | `outputs/07_events_timeline/20261125_final/figures/feedback_loop_sequence.png` | Feedback | Sequence figure | Loaded |

## Changes

- Kept the six pages and the blue Poppins layout, with a shorter header and KPI cards that wrap.
- Sidebar brand, theme switch, six icon links, and the author block stay in one column. The nav can scroll.
- Added charts for collection day, publication year, topic size, sentiment, model coherence, validation scores, confusion, period counts, and predicted shares.
- Added filters for posts, topic family, classification task, comment group, and event period.
- Added the quality checks, seed, and the statement that a repeated `comment_id` is not a duplicate row. The current annotation file has no correction-register row.
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
| Overview | Loaded. Counts 5,292, 3,500 annotated, 5,292 predictions, 4 cited topics, 19 posts, 0 direct links. |
| Data Exploration | Loaded. Missing cells are 0. Exact duplicates are 0. Within-post duplicate IDs are 0. Search `POST_08` returned 1 post and 236 comments. |
| Topics | Loaded. The cited model is NMF k=4. |
| Classification | Reads `outputs/05_model_development/20261125_final`. Policy test macro-F1 is 0.693. |
| Feedback Loop | Loaded. POST_08 date 2026-07-06, POST_17 qualifier, and the sequence figure are present. |
| Data Quality | The status table shows 5,292 raw rows. The annotation file has no correction-register row. |
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
- The cited topic model is NMF k=4 in `outputs/04_topic_modeling/20261125_final`. LDA k=6 was compared and was not selected.
