# Data preparation — final annotation link

Run id: `20261125_final`

The annotation source is `Annotation Dataset/NIRA_Project_Final_Annotation.xlsx`.
The four task columns are the final labels from that workbook.
The raw working corpus was read and not modified:
`outputs/01_data_preparation/20261125_final/raw_corpus_working.csv`.

- Annotated rows: 3,500. Every row has an annotation id.
- Keys matched to the working corpus: 3,500. Unmatched keys: 0.
- Text comparison: 3,475 exact, 12 spacing only, 13 content differences.
- One content difference is a phone number redacted in the annotation workbook.
- Actor is not a column in the final workbook.
- Annotated share of the 5,292 comments: 66.1%.
- Annotated share within posts ranges from 65.3% to 66.3%.
- `collection_date` on the linked rows is the raw collection timestamp, not a publication date.
