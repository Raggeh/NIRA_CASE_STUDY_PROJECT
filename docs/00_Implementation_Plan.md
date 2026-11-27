# Implementation plan

The current project uses `Annotation Dataset/NIRA_Project_Final_Annotation.xlsx` and the `20261125_final` output folders. Older annotation results are not part of this project.

## Verified

The raw corpus is `NIRA_Facebook_Datasets_5292.csv`: 5,292 rows, columns `comment_id`, `comment`, `platform`, `post_url`, `collection_date`. Platform is Facebook on every row. There are no blank comments and no exact duplicate rows. Nineteen source-post URLs remain after removing a leading space from 212 rows of one URL. The original URL text is kept.

`comment_id` restarts at 1 on every post. It is unique within a post and is not unique in the file (1,013 distinct identifiers). The working key is stripped URL plus `comment_id`. Fifteen rows repeat a comment string that also appears under a different post. Those rows were kept.

Each post has one collection timestamp. The timestamps fall on 23 July 2026, 24 July 2026, and 8 August 2026. They record collection time.

The annotated file is `Annotation Dataset/NIRA_Project_Final_Annotation.xlsx`. Training reads that workbook. The four task columns are its final labels. The file has 3,500 rows. Every row has an annotation id. `policy_relevance`, `feedback_type`, `topic`, and `sentiment` are populated on every row. All 3,500 records match a raw comment on the working key. Text is identical for 3,475 rows, differs only by line breaks or spacing for 12, and differs in characters for 13. One of those 13 is a phone number redacted in the annotation file and still present in the raw file.

Annotation covers every post at about 65–66% of that post's comments (3,500 / 5,292 = 66.1%). No sampling protocol is stored in the project.

`Publication Date Verification.xlsx` contains a 19-row post register, a 5-row response register, and a read-me sheet. The read-me states that the summaries were described by the user and are not independent verification.

## Incomplete or blocked

These items are absent from the project folder:

- `NB8_STEP4_V2_Post_Register.csv` and `NB8_STEP4_V3_Post_Register.csv`
- A publication-date sheet with `post_url_original`, `publication_verification_status`, and `verification_method`
- A written annotation codebook. Raggeh and Sodal labelled the four tasks, and that agreement is in `NIRA_Project_Final_Annotation.xlsx`. Actor was coded by the first annotator only and is not a column in that workbook.

The current crosswalk is `outputs/01_data_preparation/20261125_final/post_url_crosswalk.csv`. All 19 URLs still match the comment file and cover 5,292 comments. POST_08 remains 2026-07-06.

The workbook now includes a `Content Evidence Review` sheet. POST_17 is recorded as a likely topic-level description of NIRA card issuance through the Somali Embassy in Uganda, supported by an SNTV report dated 2025-12-25 and by comments on the matched URL. The original Facebook media item was not retrieved. POST_18 is recorded as a probable Eid al-Fitr greeting inferred from comments and from the 2026-03-19 date, the day before Eid on 2026-03-20. The original image and caption were not recovered. The raw corpus contains the comment phrases cited for both posts. Two filenames named in the verification basis, `NIRA_Manual_Annotation_Dataset_Annotated_REVISED.csv` and `NIRA_AI_PreAnnotated_Sample_300.csv`, are not in the project folder. The five response-register rows did not change.

A confirmed URL, date, or topic-level description does not establish a government response. Collection dates stay collection timestamps. The run to use is `20261125_final`.

## Completed runs

The current results to cite are the `20261125_final` folders, which use `NIRA_Project_Final_Annotation.xlsx`.

- `outputs/01_data_preparation/20261125_final/` — working corpus of 5,292 comments and the 3,500-row link from `NIRA_Project_Final_Annotation.xlsx`.
- `outputs/02_eda/20261125_final/`
- `outputs/03_annotation/20261125_final/`
- `outputs/04_topic_modeling/20261125_final/` — cited model NMF k=4. LDA k=6 was compared and was not selected.
- `outputs/05_model_development/20261125_final/` — five models per task. Selection used validation macro-F1. The test split was scored once after selection.
- `outputs/06_results_predictions/20261125_final/` — selected models refit on the 3,500 final labels and applied to 5,292 comments.
- `outputs/07_events_timeline/20261125_final/` — no post is classed as directly linked. Labeled counts are 2,141, 140, and 1,219.
- `docs/FINAL_REPORT.md`

## Notebook roles

| Notebook | Role | Depends on |
| --- | --- | --- |
| `02_EDA.ipynb` | Describe the 5,292 comments and, separately, the 3,500 annotated comments | Notebook 01 outputs |
| `03_Annotation.ipynb` | Document the observed label schema, quality, and the 25 text differences | Annotation file and linkage outputs |
| `04_Topic_Modeling.ipynb` | Compare unsupervised models on all 5,292 comments and select one from the scores | Working corpus |
| `05_Model_Development.ipynb` | For each of the four tasks, compare five models on the 3,500 annotated comments and select by validation macro-F1 | Annotated file, fixed seed, held-out test |
| `06_Results_and_Predictions.ipynb` | Refit each selected model on the 3,500 annotated comments, predict all 5,292 comments, then compare comments side by side | Selected models from notebook 05 |
| `07_Events_Timeline.ipynb` | Timeline and feedback-loop evidence | Saved in `outputs/07_events_timeline/20261125_final/` |
| `08_Results_Visualization.ipynb` | Figures tied to saved tables | Completed analysis outputs |
| `09_Final_Report.ipynb` | Methodology, results, limits, and conclusions | The notebooks above |

Topic modelling and supervised classification use the working corpus in `outputs/01_data_preparation/20261125_final/`. Event results are in `outputs/07_events_timeline/20261125_final/`. Publication dates stay the researcher-verified register values. POST_17 and POST_18 keep their qualifiers.

## Order of work

1. The working files and the 3,500-row annotation link are in `outputs/01_data_preparation/20261125_final/`.
2. Build exploratory analysis and the annotation notebook from those files.
3. Compare topic models on all 5,292 comments. Keep manual topic labels out of the unsupervised training target.
4. For each task (`policy_relevance`, `feedback_type`, `topic`, `sentiment`), compare five models on the 3,500 annotated comments. Select the model with the best validation macro-F1. The test split is scored after that choice and is not used to choose the model.
5. Refit each selected model on the 3,500 annotated comments and assign predicted labels to all 5,292 comments. Those predictions are model output. Then compare comments side by side, with the overlap between annotated and predicted rows disclosed.
6. Event results are in `outputs/07_events_timeline/20261125_final/`. Report publication dates as researcher-verified register values. Use POST_17 as a qualified embassy-service topic and POST_18 as a probable Eid greeting. Do not quote unrecovered Facebook captions. Do not treat a later official communication as a response unless the evidence class supports it.
7. Draw figures only from saved outputs, then write the report from those same outputs.

## Decisions already recorded

- No raw rows were deleted.
- Joins use `record_key` (stripped `post_url` plus `comment_id`).
- `comment_original` is the source text. `comment_whitespace_normalized` only collapses whitespace.
- Phone-like comments are flagged. Qualitative excerpts must redact them. Eleven comments matched the pattern used in notebook 01.
- The annotated records overlap the raw corpus. Comparisons have to state that overlap and the denominator.
- Supervised work uses five models on each of the four tasks. Selection uses validation macro-F1 on the 3,500 annotated comments. The selected model is then refit on those annotated comments and predicts all 5,292. Corpus predictions are not an independent test score.
