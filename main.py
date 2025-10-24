# mobile_kivy/main.py
import sys, pathlib
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.lang import Builder

# ── Fix import package: aggiungi il project root al sys.path ───────────────────
HERE = pathlib.Path(__file__).resolve().parent        # .../RIEMPIGIROMAPPE/mobile_kivy
ROOT = HERE.parent                                    # .../RIEMPIGIROMAPPE
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ───────────────────────────────────────────────────────────────────────────────

# Ora l'import come package funziona:
from mobile_kivy.screens import HomeScreen, CalendarScreen, FormScreen, AppointmentsScreen

KV_PATH = pathlib.Path(__file__).with_name("mobile.kv")

class GiroMappeMobile(App):
    def build(self):
        if KV_PATH.exists():
            Builder.load_file(str(KV_PATH))
        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(HomeScreen())
        self.sm.add_widget(CalendarScreen())
        self.sm.add_widget(FormScreen())
        self.sm.add_widget(AppointmentsScreen())
        return self.sm

if __name__ == "__main__":
    GiroMappeMobile().run()
