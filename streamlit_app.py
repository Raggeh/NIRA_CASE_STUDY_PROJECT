"""Root entry for Streamlit Community Cloud.

The pages stay in dashboard/streamlit_app.py. Cloud can see this root file.
"""
import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parent / "dashboard" / "streamlit_app.py"),
    run_name="__main__",
)
