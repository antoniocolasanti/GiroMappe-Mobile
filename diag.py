# mobile_kivy/diag.py
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from mobile_kivy.di_bridge import get_uc
uc = get_uc()
print("OK: use_cases keys ->", sorted(uc.keys()))
slots = uc["get_slots"]("2025-10-23", "Sportello A")
print("SLOTS:", [(s.id, s.time, s.capacity, s.booked_count, bool(s.is_ai_suggested)) for s in slots])
print("DB PATH:", __import__("app.config.settings").config.settings.settings.db_path)
