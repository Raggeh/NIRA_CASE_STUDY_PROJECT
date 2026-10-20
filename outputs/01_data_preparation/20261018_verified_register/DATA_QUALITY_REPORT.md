# Data-quality report — Notebook 01

Run id: `20261018_verified_register`

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
- The Post Register column post_url matches all 19 stripped URLs in the raw corpus. Every comment can be attached to exactly one post_id.
- The workbook records all 19 publication dates and post URLs as researcher-verified. POST_08, POST_10, and POST_17 are marked as explicitly confirmed on 2026-10-18. POST_08 is dated 2026-07-06. A confirmed URL or date does not establish a direct government response. POST_17 still has conflicting content descriptions. POST_18 still has no recovered post content.
- Changes since run 20261018_post_url: [{'post_id': 'POST_17', 'field': 'account_name', 'previous': 'Telefishinka Qaranka Soomaaliyeed (workbook metadata; may be mismatched)', 'current': 'Telefishinka Qaranka Soomaaliyeed'}, {'post_id': 'POST_18', 'field': 'account_name', 'previous': 'NIRA Somalia (reported metadata; content not provided in available notes)', 'current': 'NIRA Somalia'}, {'post_id': 'POST_08', 'field': 'publication_date', 'previous': '2026-07-07', 'current': '2026-07-06'}]
- Content still limited: ['POST_17', 'POST_18']

## Preprocessing decision

comment_original keeps the file text. comment_whitespace_normalized collapses whitespace only. Case, Somali spelling, and tokens are unchanged at this stage.

No modelling text was created beyond whitespace normalisation. Spelling normalisation, stopword removal, and translation were not applied.
