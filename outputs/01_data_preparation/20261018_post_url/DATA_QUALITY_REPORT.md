# Data-quality report — Notebook 01

Run id: `20261018_post_url`

This report was produced by `notebooks/01_Data_Preparation.ipynb`. Source files were not modified.

## Raw corpus

- File: `NIRA_Facebook_Datasets_5292.csv`
- Rows: 5292
- Columns: comment_id, comment, platform, post_url, collection_date
- Blank comments: 0
- Exact duplicate rows: 0
- Source posts after stripping URL whitespace: 19
- `comment_id` values are unique within a post, but only 1013 distinct identifiers exist across 5292 rows.
- Rows whose exact text also appears under another post: 15. These were retained.
- Rows with outer whitespace in `post_url`: 212.
- Collection timestamps: 19, from 2026-07-23 07:50:00 to 2026-08-08 23:21:00.
- Collection dates are not publication dates.
- Comment length in characters: minimum 15, median 55.0, maximum 1430.
- Comments under 30 characters: 1024.
- Comments containing Arabic script: 7.
- Comments containing styled Latin letters: 5.
- Comments matching a phone-like pattern: 11. Values are not printed in this report.

## Annotated subset

- File: `Annotation Dataset\NIRA_Annotation_Master_1199_Modeling_final.xlsx`
- Rows: 1199. All four classification fields are populated.
- Keys matched to the raw corpus on stripped URL plus `comment_id`: 1199.
- Unmatched keys: 0.
- Text comparison: {'exact': 1174, 'content_difference': 13, 'newline_or_whitespace': 12}.
- Annotated share of raw comments: 0.2266.
- Annotated share within posts ranges from 0.219 to 0.233.
- About 22.7% of comments are annotated, and every post is represented at roughly 22–23%. The gap between annotated rows is not a single fixed stride. No sampling protocol is stored in the project files, so the design cannot be confirmed.
- The 1,199 annotated records are a matched subset of the 5,292 raw comments. They are not a separate population.

## Publication workbook

- Sheets: Post Register, Response Register, Read Me and Limitations.
- Post register rows: 19. Response register rows: 5.
- URL matches: 19 of 19 register posts, covering 5292 comments.
- The Post Register column post_url matches all 19 stripped URLs in the raw corpus. Every comment can be attached to exactly one post_id. The join is a URL match. It does not independently verify the publication dates.
- The workbook read-me states that summaries reflect details described by the user and are not independent verification of the original posts. evidence_status remains user-described or unresolved. publication_verification_status and verification_method are not columns in this workbook. NB8_STEP4_V2_Post_Register.csv and NB8_STEP4_V3_Post_Register.csv are not in the project folder. POST_17 and POST_18 still carry unresolved content notes.

## Preprocessing decision

comment_original keeps the file text. comment_whitespace_normalized collapses whitespace only. Case, Somali spelling, and tokens are unchanged at this stage.

No modelling text was created beyond whitespace normalisation. Spelling normalisation, stopword removal, and translation were not applied.
