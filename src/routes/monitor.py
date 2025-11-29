from fastapi import APIRouter
import json
from pathlib import Path
from src.config.settings import settings

router = APIRouter()

@router.get("/drift")
def drift():
    p = Path(settings.drift_reports_dir) / "drift_metrics.json"
    if not p.exists():
        return {"status": "no_report"}
    return json.loads(p.read_text())

