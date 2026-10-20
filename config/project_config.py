"""Shared configuration for the NIRA digital policy feedback project.

Source files are read-only. Analysis code must not overwrite them.
Collection dates and publication dates are different fields and must not be substituted for each other.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_CORPUS_CSV = PROJECT_ROOT / "NIRA_Facebook_Datasets_5292.csv"
ANNOTATION_XLSX = (
    PROJECT_ROOT
    / "Annotation Dataset"
    / "NIRA_Annotation_Master_1199_Modeling_final.xlsx"
)
PUBLICATION_XLSX = PROJECT_ROOT / "Publication Date Verification.xlsx"

RANDOM_SEED = 42

EXPECTED_RAW_N = 5292
EXPECTED_ANNOTATION_N = 1199
EXPECTED_N_POSTS = 19

RAW_COLUMNS = [
    "comment_id",
    "comment",
    "platform",
    "post_url",
    "collection_date",
]

ANNOTATION_COLUMNS = [
    "annotation_id",
    "comment_id",
    "comment",
    "platform",
    "post_url",
    "collection_date",
    "collection_date_original",
    "policy_relevance",
    "feedback_type",
    "topic",
    "sentiment",
    "actor",
    "annotation_status",
]

CLASSIFICATION_TARGETS = [
    "policy_relevance",
    "feedback_type",
    "topic",
    "sentiment",
]
