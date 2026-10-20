# Topic model report

Run: 20261019_topic_models

Corpus: 5292 comments from raw_corpus_working.csv. Manual topic labels were not used.

Comments with fewer than two letter-tokens: 11. Those comments are unassigned.

Embedding model: paraphrase-multilingual-MiniLM-L12-v2. This does not establish that the model understands Somali.

## Selection

The selected model is the coverage-eligible candidate with the highest c_npmi. Coverage-eligible means a topic was assigned to at least 80 percent of the 5,292 comments.

Selected model: NMF (k=6).
Coherence c_npmi: 0.058336388322863635.
Topic diversity: 0.7833333333333333.
Coverage: 0.9788359788359788.
Unassigned comments: 112.

The topic labels in selected_topic_terms.csv are the model's top terms. They are not validated theme names.
