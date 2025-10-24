# mobile_kivy/di_bridge.py
import sys, pathlib, os

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config.di import build_db, build_use_cases

_db = None
_uc = None

def _mobile_db_path():
    # Se siamo in ambiente Android (rilevato da env var di python-for-android)
    if "ANDROID_ARGUMENT" in os.environ:
        try:
            from kivy.app import App
            base = pathlib.Path(App.get_running_app().user_data_dir)
        except Exception:
            base = pathlib.Path.home() / ".giro_mappe_mobile"
        base.mkdir(parents=True, exist_ok=True)
        return str(base / "giro_mappe.db")
    # desktop → usa settings (o GIROMAPPE_DB_PATH se lo setti)
    return None

def get_uc():
    global _db, _uc
    if _uc is None:
        # opzionale override per Android
        mobile_db = _mobile_db_path()
        if mobile_db:
            os.environ["GIROMAPPE_DB_PATH"] = mobile_db
        _db = build_db()
        _uc = build_use_cases(_db)
    return _uc
