# Data-quality report — Notebook 01

Run id: `20261018_content_review`

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

- Sheets: Post Register, Response Register, Read Me and Limitations, Content Evidence Review.
- Post register rows: 19. Response register rows: 5.
- URL matches: 19 of 19 register posts, covering 5292 comments.
- The Post Register column post_url matches all 19 stripped URLs in the raw corpus. Every comment can be attached to exactly one post_id.
- The workbook records all 19 publication dates and post URLs as researcher-verified. POST_08 is dated 2026-07-06. POST_17 is recorded as likely identified at topic level: NIRA national-ID issuance through the Somali Embassy in Uganda, with an SNTV report dated 2025-12-25 and comments on the matched URL. The original Facebook media item was not directly retrieved. POST_18 is recorded as a probable Eid al-Fitr greeting inferred from comments and the 2026-03-19 date, the day before Eid on 2026-03-20. The original image and caption were not recovered. A confirmed URL or date does not establish a direct government response.
- Changes since run 20261018_verified_register: 10 field changes, limited to POST_17 and POST_18 content fields.
- Comment corroboration in the raw corpus: {'POST_17': {'n_comments': 73, 'phrase_hits': {'uganda': 3, 'safaarad': 2, 'embassy': 1}}, 'POST_18': {'n_comments': 64, 'phrase_hits': {'Ciidiina marabnee kaararka meel ku sheega': 1, 'Card ka nasiiya ciidina cune': 1, 'ciid': 17}}}
- Evidence filenames cited by the workbook but not present in the project folder: ['NIRA_Manual_Annotation_Dataset_Annotated_REVISED.csv', 'NIRA_AI_PreAnnotated_Sample_300.csv']

## Preprocessing decision

comment_original keeps the file text. comment_whitespace_normalized collapses whitespace only. Case, Somali spelling, and tokens are unchanged at this stage.

No modelling text was created beyond whitespace normalisation. Spelling normalisation, stopword removal, and translation were not applied.
