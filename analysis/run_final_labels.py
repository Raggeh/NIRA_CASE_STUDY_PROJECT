"""Fit the saved pipeline on the final labels. Older result folders stay in place."""
import update_labeled_3500 as job

job.RUN = "20261125_final"
job.main()
