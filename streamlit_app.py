"""Root entry for Streamlit Community Cloud.

The pages stay in dashboard/streamlit_app.py. Cloud can see this root file.
The dashboard folder is placed on the import path so nira_data can be imported.
"""
import importlib.util
import sys
from pathlib import Path

DASHBOARD = Path(__file__).resolve().parent / "dashboard"
dashboard_path = str(DASHBOARD)
if dashboard_path not in sys.path:
    sys.path.insert(0, dashboard_path)

spec = importlib.util.spec_from_file_location("nira_dashboard", DASHBOARD / "streamlit_app.py")
module = importlib.util.module_from_spec(spec)
sys.modules["nira_dashboard"] = module
spec.loader.exec_module(module)
