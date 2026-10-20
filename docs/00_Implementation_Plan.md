# Implementation plan

Audit date: 18 October 2026. The current data-preparation run is `outputs/01_data_preparation/20261018_content_review/`. Source files were not modified.

## Verified

The raw corpus is `NIRA_Facebook_Datasets_5292.csv`: 5,292 rows, columns `comment_id`, `comment`, `platform`, `post_url`, `collection_date`. Platform is Facebook on every row. There are no blank comments and no exact duplicate rows. Nineteen source-post URLs remain after removing a leading space from 212 rows of one URL. The original URL text is kept.

`comment_id` restarts at 1 on every post. It is unique within a post and is not unique in the file (1,013 distinct identifiers). The working key is stripped URL plus `comment_id`. Fifteen rows repeat a comment string that also appears under a different post. Those rows were kept.

Each post has one collection timestamp. The timestamps fall on 23 July 2026, 24 July 2026, and 8 August 2026. They record collection time.

The annotation file is `Annotation Dataset/NIRA_Annotation_Master_1199_Modeling_final.xlsx`: 1,199 rows. `policy_relevance`, `feedback_type`, `topic`, and `sentiment` are populated on every row. All 1,199 records match a raw comment on the working key. Text is identical for 1,174 rows, differs only by line breaks or spacing for 12, and differs in characters for 13. One of those 13 is a phone number redacted in the annotation file and still present in the raw file. Collection timestamps agree to the minute on every matched key.

Annotation covers every post at about 22–23% of that post's comments (1,199 / 5,292 = 22.7%). The spacing of annotated rows is uneven. No sampling protocol is stored in the project.

`Publication Date Verification.xlsx` contains a 19-row post register, a 5-row response register, and a read-me sheet. The read-me states that the summaries were described by the user and are not independent verification.

## Incomplete or blocked

These items are absent from the project folder:

- `NB8_STEP4_V2_Post_Register.csv` and `NB8_STEP4_V3_Post_Register.csv`
- A publication-date sheet with `post_url_original`, `publication_verification_status`, and `verification_method`
- A written annotation codebook and any second-coder or agreement file
- Notebooks 02 through 09, topic models, classifiers, corpus-wide predictions, figures, and a final report

The current crosswalk is `outputs/01_data_preparation/20261018_content_review/post_url_crosswalk.csv`. All 19 URLs still match the comment file and cover 5,292 comments. Publication dates and URLs are unchanged from the previous run. POST_08 remains 2026-07-06.

The workbook now includes a `Content Evidence Review` sheet. POST_17 is recorded as a likely topic-level description of NIRA card issuance through the Somali Embassy in Uganda, supported by an SNTV report dated 2025-12-25 and by comments on the matched URL. The original Facebook media item was not retrieved. POST_18 is recorded as a probable Eid al-Fitr greeting inferred from comments and from the 2026-03-19 date, the day before Eid on 2026-03-20. The original image and caption were not recovered. The raw corpus contains the comment phrases cited for both posts. Two filenames named in the verification basis, `NIRA_Manual_Annotation_Dataset_Annotated_REVISED.csv` and `NIRA_AI_PreAnnotated_Sample_300.csv`, are not in the project folder. The five response-register rows did not change.

A confirmed URL, date, or topic-level description does not establish a government response. Collection dates stay collection timestamps. Earlier runs remain on disk; this run is the one to use.

## Completed runs

Notebooks 01–09 have been executed. The runs to cite are:

- `outputs/01_data_preparation/20261018_content_review/`
- `outputs/02_eda/20261018_eda/`
- `outputs/03_annotation/20261018_annotation/`
- `outputs/04_topic_modeling/20261019_topic_models/` — NMF with k=6 selected by c_npmi among coverage-eligible models. BERTopic was run and covered 49.4 percent of comments, so it was not eligible.
- `outputs/05_model_development/20261019_supervised/` — five models per task. Selection used validation macro-F1. The test split was scored once after selection.
- `outputs/06_results_predictions/20261019_predictions/` — selected models refit on 1,199 labels and applied to 5,292 comments. The comment sample has 30 unique keys.
- `outputs/07_events_timeline/20261019_events/` — no post is classed as directly linked.
- `outputs/08_results_visualization/20261019_figures/`
- `outputs/09_final_report/20261019_report/FINAL_REPORT.md` and `docs/FINAL_REPORT.md`

## Notebook roles

| Notebook | Role | Depends on |
| --- | --- | --- |
| `02_EDA.ipynb` | Describe the 5,292 comments and, separately, the 1,199 labels | Notebook 01 outputs |
| `03_Annotation.ipynb` | Document the observed label schema, quality, and the 25 text differences | Annotation file and linkage outputs |
| `04_Topic_Modeling.ipynb` | Compare unsupervised models on all 5,292 comments and select one from the scores | Working corpus |
| `05_Model_Development.ipynb` | For each of the four tasks, compare up to five models on the 1,199 labels and select by held-out macro-F1 | Annotated subset, fixed seed, held-out test |
| `06_Results_and_Predictions.ipynb` | Refit each selected model on the 1,199 labels, predict all 5,292 comments, then compare comments side by side | Selected models from notebook 05 |
| `07_Events_Timeline.ipynb` | Timeline and feedback-loop evidence | Use run `20261018_content_review`; keep POST_17 and POST_18 qualifiers |
| `08_Results_Visualization.ipynb` | Figures tied to saved tables | Completed analysis outputs |
| `09_Final_Report.ipynb` | Methodology, results, limits, and conclusions | The notebooks above |

Topic modelling and supervised classification can proceed from the working corpus. Event analysis should use run `20261018_content_review`, report publication dates as researcher-verified register values, and keep the POST_17 and POST_18 qualifiers visible.

## Order of work

1. Notebook 01 was re-run as `20261018_content_review` after the publication workbook added the Content Evidence Review sheet. Working files are in `outputs/01_data_preparation/20261018_content_review/`.
2. Build exploratory analysis and the annotation notebook from those files.
3. Compare topic models on all 5,292 comments. Keep manual topic labels out of the unsupervised training target.
4. For each task (`policy_relevance`, `feedback_type`, `topic`, `sentiment`), compare up to five models on the 1,199 labeled comments. Select the model with the best validation macro-F1. The test split is scored after that choice and is not used to choose the model.
5. Refit each selected model on the 1,199 labeled comments and assign predicted labels to all 5,292 comments. Those predictions are model output. Then compare comments side by side, with the overlap between annotated and predicted rows disclosed.
6. Build the event notebook on run `20261018_content_review`. Report publication dates as researcher-verified register values. Use POST_17 as a qualified embassy-service topic and POST_18 as a probable Eid greeting. Do not quote unrecovered Facebook captions. Do not treat a later official communication as a response unless the evidence class supports it.
7. Draw figures only from saved outputs, then write the report from those same outputs.

## Decisions already recorded

- No raw rows were deleted.
- Joins use `record_key` (stripped `post_url` plus `comment_id`).
- `comment_original` is the source text. `comment_whitespace_normalized` only collapses whitespace.
- Phone-like comments are flagged. Qualitative excerpts must redact them. Eleven comments matched the pattern used in notebook 01.
- The annotated records overlap the raw corpus. Comparisons have to state that overlap and the denominator.
- Supervised work uses five models on each of the four tasks. Selection uses validation macro-F1 on the 1,199 labeled comments. The selected model is then refit on those labeled comments and predicts all 5,292. Corpus predictions are not an independent test score.
