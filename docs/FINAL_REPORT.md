# Quantifying the Digital Policy Feedback Loop

## Question and data

The study asks how public Facebook comments on posts about Somalia's National Identification and Registration Authority can be described, classified, and placed next to inventoried institutional communications. The working corpus contains 5292 comments under 19 source posts. The annotated file contains 3500 comments, which is 66.1% of the corpus. Every annotated key matches a raw comment. 1199 of those rows have an annotation id. 2301 labeled rows do not.

`collection_date` is the time the comment file was collected. `publication_date_register` is the researcher-verified publication date of the source post. The two dates are not substitutes.

## Annotation

All 3,500 annotation keys match a raw comment. Text match on the joined rows: 3475 exact, 12 whitespace only, and 13 character differences. The annotated share is no longer about 22 to 23 percent of every post, because the file now covers 3,500 comments.

The four supervised tasks are `policy_relevance`, `feedback_type`, `topic`, and `sentiment`. `actor` is stored in the file and is not one of those tasks. No class was merged.

| field | n_classes | largest_class | largest_n | smallest_class | smallest_n | largest_share_of_annotated |
| --- | --- | --- | --- | --- | --- | --- |
| actor | 5 | uncertain | 1721 | official | 63 | 0.492 |
| feedback_type | 8 | complaint | 822 | information | 73 | 0.235 |
| policy_relevance | 3 | relevant | 2573 | uncertain | 241 | 0.735 |
| sentiment | 4 | negative | 1775 | uncertain | 120 | 0.507 |
| topic | 8 | other | 964 | documentation_requirements | 33 | 0.275 |

Shares use the 3,500 labeled comments as the denominator.

## Unsupervised topics

The cited topic run is `20261111_3500`. It compares LDA, NMF, LSA, and clustering models that use AfriBERTa and AfroXLMR. All of them were fit on the 5,292 comments. Manual topic labels were not a training target. The comparison removes 56 grammatical tokens listed in `config/somali_function_words.csv`. The selected model is the coverage-eligible candidate with the highest c_npmi. Coverage-eligible means a topic was assigned to at least 80 percent of the 5,292 comments. Somali-trained encoders were in that pool and were not selected, because their coherence was lower.

Selected model: NMF (k=4). Coherence c_npmi: 0.084. Diversity: 0.950. Coverage: 0.985. Unassigned comments: 81. The cited model is a bag-of-words model, not a Somali-trained encoder.

The previous cited run, `20261019_topic_models_function_words`, selected LDA k=6 with coherence 0.023. That run stays saved and is not the cited solution.

| topic_id | n_comments | provisional_term_label |
| --- | --- | --- |
| 2 | 3824 | nira \| dadka \| somalia |
| 1 | 616 | lacag \| hadaba \| meel |
| 3 | 387 | allah \| masha \| guul |
| 0 | 384 | madaxweyne \| mudane \| guuleyso |

The labels above are the model's own top terms. They are not validated names of policy themes. Coherence does not confirm that a topic is a public-policy theme.

## Supervised classification

Each task compared five models on a stratified split of the 3,500 labeled comments: 70 percent train, 10 percent validation, and 20 percent test, with seed 42. The split is 2,450 / 350 / 700. The selected model is the one with the highest validation macro-F1. The test split was scored after selection and was not used to choose the model.

| task | selected_model | validation_macro_f1 | test_macro_f1 | test_weighted_f1 | test_accuracy |
| --- | --- | --- | --- | --- | --- |
| policy_relevance | logistic_regression | 0.687 | 0.665 | 0.840 | 0.837 |
| feedback_type | logistic_regression | 0.646 | 0.701 | 0.737 | 0.734 |
| topic | complement_nb | 0.669 | 0.578 | 0.679 | 0.691 |
| sentiment | complement_nb | 0.687 | 0.641 | 0.780 | 0.793 |

The TF-IDF classifiers use letter tokens and word bigrams. They do not use the function-word list, because that list was applied only to the topic models. The fifth model is logistic regression on the multilingual embeddings. Its score does not show that those embeddings understand Somali.

The performance result is the held-out test macro-F1 in the table above. The label written for each of the 5,292 comments is a prediction from the selected model after it was refit on the 3,500 labeled rows.

## Corpus predictions and comment comparison

The selected model for each task was refit on all 3,500 labeled comments and then applied to all 5,292 comments. The refit has seen the labels that a held-out test is meant to hide, so the agreement below is not the performance result. The performance result remains the test macro-F1 in the table above.

| task | selected_model | heldout_test_macro_f1 | refit_agreement_macro_f1 | refit_agreement_accuracy |
| --- | --- | --- | --- | --- |
| policy_relevance | logistic_regression | 0.665 | 0.937 | 0.965 |
| feedback_type | logistic_regression | 0.701 | 0.910 | 0.916 |
| topic | complement_nb | 0.578 | 0.931 | 0.935 |
| sentiment | complement_nb | 0.641 | 0.897 | 0.936 |

The comment sample contains 30 unique comments: 10 annotated, 10 unlabeled, and 10 further comments. Overlap between the samples is 0. Every comment receives a prediction. The third sample is not a separate dataset. It is ten further comments drawn from the rows that were not already sampled. The unsupervised topic columns come from notebook 04 and use a different label space from the manual topic classes.

Predicted labels are model output. They were not manually corrected.

## Events and the feedback-loop claim

No inventoried communication is classed as a direct response to a source post or to a comment. Shared topic and nearby dates remain comparisons.

Posts classed as thematically related: 4. Posts classed as temporally associated: 1. Posts classed as unlinked or unresolved: 14. Posts classed as directly linked: 0.

POST_09 shares the registered date of the inventoried SONNA item RESP_001, 2025-11-03. POST_01 and POST_04 are topic comparisons with named inventory rows. The register already says those comparisons do not establish causality.

That named comparison is drawn in `outputs/07_events_timeline/20261019_events/figures/feedback_loop_sequence.png`. Reading left to right, the boxes are POST_01 on 27 October 2025, RESP_001 and POST_09 on 3 November 2025, POST_04 on 4 November 2025, and RESP_002 on 10 November 2025. The arrow from POST_01 to RESP_001 is thematic, and the SONNA page does not name POST_01. The arrow between RESP_001 and POST_09 is temporal because the dates match. The arrow from RESP_001 to POST_04 is the next day and is thematic. The arrow from POST_04 to RESP_002 is thematic, and the NIRA page names no corpus post. The dashed line is publication order. Directly linked posts in the figure are 0. POST_03 and POST_12 are also thematically related, but the register does not name RESP_001 or RESP_002 for them, so they are not drawn.

The dashboard split uses RESP_001 on 2025-11-03 as the event. A comment inherits the publication date of its source post. Comments on posts published before that day are pre-event: 9 posts and 3,236 comments, of which 734 are annotated. POST_09 is the event day: 212 comments, of which 48 are annotated. Comments on posts published after that day are post-event: 9 posts and 1,844 comments, of which 417 are annotated. `collection_date` is not used. The split is saved in `outputs/07_events_timeline/20261019_events/event_period_summary.csv` and `comments_by_event_period.csv`. Predicted label shares by period are saved beside those files. They describe the model output in each period. They do not measure an effect of RESP_001.

On 2026-10-19 the five inventory pages were opened. All five titles match the inventory. RESP_001 is dated 3 November 2025 and says the Director General addressed social media images of night queues; it does not name a Facebook URL from this corpus. RESP_002 is dated 10 November 2025 and describes the Wadajir day-and-night center. RESP_003 is dated 22 September 2025 and describes the Heliwaa center. RESP_004 lists 30 July 2025, while the notice body says 29 July 2025, and the bank measure is stated to start on 1 September 2025. RESP_005 is dated 1 January 2026 and says the domestic-travel ID requirement was postponed to 1 March 2026. None of these pages names a source post in the corpus, so no post is classed as directly linked. The check is saved in `outputs/07_events_timeline/20261019_source_check/source_check.json`.

POST_17 and POST_18 captions were not returned by the automated page fetch. The researcher then supplied screenshots of the open posts. The POST_17 Reel caption reads: "Safaaradda Soomaaliya ee dalka Uganda oo bilowday inay bixiso Kaarka Aqoonsiga Qaranka ee NIRA." The POST_18 caption, dated March 19 on the screen, reads: "Ciid Mubarak! Hay'adda NIRA waxa ay shacabka Soomaaliyeed iyo guud ahaan ummadda Islaamka ugu hambalyaynaysaa Munaasabadda Barakaysan ee Ciidul-Fidriga." The graphic also reads CIID MUBAARAK. The reel audio was not transcribed. The screenshots are stored in `evidence/post_screenshots/`.

POST_10 has a confirmed publication date of 2025-10-18. The policy claim in that post remains reported post content.

## Figures

The figures are saved from the tables above in `outputs/08_results_visualization/20261019_figures/figures/`.

| file | reads_as |
| --- | --- |
| topic_coherence.png | c_npmi for every topic-model candidate on 5,292 comments |
| selected_topic_sizes.png | Comment counts for the selected topic model |
| validation_macro_f1.png | Validation macro-F1 for five models on four tasks |
| heldout_and_refit_macro_f1.png | Held-out test macro-F1 beside refit agreement |
| label_share_comparison.png | Manual and predicted label shares, with denominators in the title |
| post_timeline_volume.png | Comment counts by post. Color is the linkage class, not a causal result |
| feedback_loop_sequence.png | Named comparison around RESP_001. Arrows are linkage class, not a cause. Saved in the events figures folder |

## Limits

- The labeled file has 3,500 rows joined to the raw corpus. 1,199 rows have an annotation id. 2,301 labeled rows do not.
- The four supervised tasks were retrained on those 3,500 rows. Seed 42. Selection used validation macro-F1 only.
- Comments are short, mostly Somali, and written in informal Latin script. A few comments use Arabic script. Coherence and embedding distance are statistical descriptions, not a language-understanding test.
- The largest classes are `relevant`, `complaint`, `other`, and `negative`. Macro-F1 gives equal weight to rare classes, including classes with few test rows.
- Twenty-five annotation strings differ from the raw comment. Training used the raw working-corpus text. One difference is a redacted phone number. Excerpts in the sample redact phone-like strings.
- The performance number is the held-out test macro-F1. The 5,292 predicted labels come from a model refit on every labeled row, so their agreement with the manual labels is not a second test score.
- A shared topic, a nearby date, or a large predicted class is not evidence that an institution responded to a comment.

## Files

- Data preparation: `outputs/01_data_preparation/20261018_content_review/`
- Exploratory analysis: `outputs/02_eda/20261018_eda/`
- Annotation audit: `outputs/03_annotation/20261018_annotation/`
- Topic models: `outputs/04_topic_modeling/20261019_topic_models_function_words/`
- Earlier topic run, kept for comparison: `outputs/04_topic_modeling/20261019_topic_models/`
- Supervised comparison: `outputs/05_model_development/20261019_supervised/`
- Predictions: `outputs/06_results_predictions/20261019_predictions/`
- Events and the pre-event, event-day, and post-event split: `outputs/07_events_timeline/20261019_events/`
- Page check: `outputs/07_events_timeline/20261019_source_check/`
- Figures: `outputs/08_results_visualization/20261019_figures/`

