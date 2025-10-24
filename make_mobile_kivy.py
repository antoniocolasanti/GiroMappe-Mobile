# make_mobile_kivy.py
import os, pathlib, textwrap

ROOT = pathlib.Path(__file__).resolve().parent
MOB = ROOT / "mobile_kivy"
(MOB / "screens").mkdir(parents=True, exist_ok=True)
(MOB / "widgets").mkdir(parents=True, exist_ok=True)

files = {
    "requirements.txt": "kivy==2.3.0\n",
    "di_bridge.py": r'''
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]  # cartella che contiene 'app/'
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.config.di import build_db, build_use_cases
_db = None
_uc = None
def get_uc():
    global _db, _uc
    if _uc is None:
        _db = build_db()
        _uc = build_use_cases(_db)
    return _uc
''',
    "widgets/__init__.py": "",
    "widgets/toast.py": r'''
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
def toast(message: str, duration: float = 2.0):
    lbl = Label(text=message, size_hint=(None, None), padding=(12, 8),
                color=(1,1,1,1), bold=True)
    lbl.texture_update()
    w, h = lbl.texture_size
    lbl.size = (w+24, h+16)
    lbl.pos = (Window.width/2 - lbl.width/2, 40)
    from kivy.base import EventLoop
    parent = EventLoop.window
    parent.add_widget(lbl)
    def _rm(*_):
        if parent and lbl in parent.children:
            parent.remove_widget(lbl)
    Clock.schedule_once(_rm, duration)
''',
    "screens/__init__.py": "from .home import HomeScreen\nfrom .calendar import CalendarScreen\nfrom .form import FormScreen\nfrom .appointments import AppointmentsScreen\n",
    "screens/home.py": "from kivy.uix.screenmanager import Screen\n\nclass HomeScreen(Screen):\n    pass\n",
    "screens/calendar.py": r'''
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty, ListProperty, ObjectProperty
from mobile_kivy.di_bridge import get_uc
from mobile_kivy.widgets.toast import toast

class CalendarScreen(Screen):
    date = StringProperty("2025-10-23")
    office = StringProperty("")
    solo_liberi = BooleanProperty(True)
    offices = ListProperty([])
    slots = ListProperty([])
    selected_slot = ObjectProperty(None, allownone=True)

    def on_pre_enter(self, *args):
        uc = get_uc()
        try:
            self.offices = uc["slot_repo"].offices()
            if not self.offices:
                self.offices = ["Sportello A", "Sportello B"]
            if not self.office:
                self.office = self.offices[0]
        except Exception:
            self.offices = ["Sportello A", "Sportello B"]
            if not self.office:
                self.office = self.offices[0]
        self.load_slots()

    def load_slots(self, *_):
        uc = get_uc()
        slots = uc["get_slots"](self.date.strip(), self.office.strip())
        if self.solo_liberi:
            slots = [s for s in slots if (s.capacity or 0) > (s.booked_count or 0)]
        self.slots = [{
            "id": s.id, "time": s.time, "office": s.office,
            "cap": s.capacity, "booked": s.booked_count,
            "ai": bool(s.is_ai_suggested)
        } for s in slots]

    def suggest_ai(self):
        uc = get_uc()
        uc["suggest_slots"](self.date.strip(), self.office.strip(), top_n=None)
        self.load_slots()
        toast("Suggerimenti AI aggiornati")

    def proceed(self):
        if not self.selected_slot:
            toast("Seleziona uno slot")
            return
        form = self.manager.get_screen("form")
        form.prefill_from_slot(self.date, self.office, self.selected_slot)
        self.manager.current = "form"
''',
    "screens/form.py": r'''
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from mobile_kivy.di_bridge import get_uc
from mobile_kivy.widgets.toast import toast

class FormScreen(Screen):
    slot_id = NumericProperty(0)
    date = StringProperty("")
    office = StringProperty("")
    user_name = StringProperty("")
    user_surname = StringProperty("")
    email = StringProperty("")
    cf = StringProperty("")
    notes = StringProperty("")
    last_app = ObjectProperty(None, allownone=True)

    def prefill_from_slot(self, date, office, slot_dict):
        self.date = date
        self.office = office
        self.slot_id = int(slot_dict.get("id"))

    def submit(self):
        if not self.user_name.strip() or not self.user_surname.strip():
            return toast("Nome e Cognome sono obbligatori")
        if "@" not in self.email:
            return toast("Email non valida")
        if len(self.cf.strip()) != 16:
            return toast("Codice Fiscale deve avere 16 caratteri")

        uc = get_uc()
        payload = {
            "user_name": self.user_name.strip(),
            "user_surname": self.user_surname.strip(),
            "email": self.email.strip(),
            "codice_fiscale": self.cf.strip().upper(),
            "date": self.date, "time": "", "office": self.office,
            "slot_id": self.slot_id, "notes": self.notes.strip(),
        }
        sl = uc["slot_repo"].by_id(self.slot_id)
        if sl:
            payload["time"] = sl.time

        try:
            app = uc["book_appointment"](payload)
        except Exception as ex:
            return toast(f"Errore: {ex}")

        self.last_app = app
        toast(f"Prenotazione #{app.id} creata")
        self.user_name = self.user_surname = self.email = self.cf = self.notes = ""
        self.manager.current = "appointments"
''',
    "screens/appointments.py": r'''
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
from mobile_kivy.di_bridge import get_uc
from mobile_kivy.widgets.toast import toast

class AppointmentsScreen(Screen):
    items = ListProperty([])

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        uc = get_uc()
        apps = uc["list_appointments"]()
        self.items = [{
            "id": a.id, "name": f"{a.user_name} {a.user_surname}",
            "email": a.email, "date": a.date, "time": a.time,
            "office": a.office, "status": a.status
        } for a in apps]

    def action(self, app_id: int, op: str):
        uc = get_uc()
        try:
            if op == "confirm":
                uc["appointment_repo"].update_status(app_id, "confirmed")
            elif op == "cancel":
                uc["appointment_repo"].update_status(app_id, "canceled")
            elif op == "checkin":
                uc["checkin"](app_id)
            else:
                return
        except Exception as ex:
            return toast(f"Errore: {ex}")
        toast(f"OK: {op}")
        self.refresh()
''',
    "mobile.kv": r'''
#:kivy 2.3.0

<HomeScreen>:
    name: "home"
    BoxLayout:
        orientation: "vertical"
        padding: 10
        spacing: 8
        Label:
            text: "GiroMappe (Mobile)"
            font_size: "22sp"
            bold: True
            size_hint_y: None
            height: self.texture_size[1] + 12
        Button:
            text: "Calendar"
            on_release: app.sm.current = "calendar"
        Button:
            text: "Nuova prenotazione (Calendar → Form)"
            on_release: app.sm.current = "calendar"
        Button:
            text: "Appuntamenti"
            on_release: app.sm.current = "appointments"

<CalendarScreen>:
    name: "calendar"
    BoxLayout:
        orientation: "vertical"
        padding: 10
        spacing: 8
        BoxLayout:
            size_hint_y: None
            height: "40dp"
            spacing: 8
            TextInput:
                text: root.date
                hint_text: "YYYY-MM-DD"
                on_text: root.date = self.text
            Spinner:
                text: root.office or "Ufficio"
                values: root.offices
                on_text: root.office = self.text; root.load_slots()
            CheckBox:
                id: cb
                active: root.solo_liberi
                size_hint_x: None
                width: "30dp"
                on_active: root.solo_liberi = self.active; root.load_slots()
            Label:
                text: "Solo liberi"
                size_hint_x: None
                width: self.texture_size[0] + 8
        BoxLayout:
            size_hint_y: None
            height: "40dp"
            spacing: 8
            Button:
                text: "Suggerisci (AI)"
                on_release: root.suggest_ai()
            Button:
                text: "Carica"
                on_release: root.load_slots()
            Button:
                text: "Prosegui"
                on_release: root.proceed()
            Button:
                text: "Home"
                on_release: app.sm.current = "home"
        RecycleView:
            viewclass: "BoxLayout"
            id: rv
            data: [ {"orientation": "horizontal", "size_hint_y": None, "height": "38dp",
                     "children": [
                        Label(text=f"[b]{('*' if s['ai'] else '')}[/b] {s['time']}  ({s['booked']}/{s['cap']})", markup: True, size_hint_x: .7),
                        Button(text="Seleziona", size_hint_x: .3, on_release=lambda w, sid=s['id']: setattr(root, 'selected_slot', s))
                     ]} for s in root.slots ]
            RecycleBoxLayout:
                default_size: None, dp(38)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'

<FormScreen>:
    name: "form"
    BoxLayout:
        orientation: "vertical"
        padding: 10
        spacing: 8
        Label:
            text: "Prenotazione"
            font_size: "20sp"
            bold: True
            size_hint_y: None
            height: self.texture_size[1] + 8
        GridLayout:
            cols: 2
            row_default_height: "40dp"
            size_hint_y: None
            height: self.minimum_height
            Label: text: "Nome"
            TextInput: text: root.user_name; on_text: root.user_name = self.text
            Label: text: "Cognome"
            TextInput: text: root.user_surname; on_text: root.user_surname = self.text
            Label: text: "Email"
            TextInput: text: root.email; on_text: root.email = self.text
            Label: text: "Codice Fiscale"
            TextInput: text: root.cf; on_text: root.cf = self.text
            Label: text: "Note"
            TextInput: text: root.notes; on_text: root.notes = self.text
        BoxLayout:
            size_hint_y: None
            height: "40dp"
            spacing: 8
            Button:
                text: "Invia"
                on_release: root.submit()
            Button:
                text: "Annulla"
                on_release: app.sm.current = "calendar"
            Button:
                text: "Home"
                on_release: app.sm.current = "home"

<AppointmentsScreen>:
    name: "appointments"
    BoxLayout:
        orientation: "vertical"
        padding: 10
        spacing: 8
        BoxLayout:
            size_hint_y: None
            height: "40dp"
            spacing: 8
            Button: text: "Refresh"; on_release: root.refresh()
            Button: text: "Home"; on_release: app.sm.current = "home"
        RecycleView:
            id: rv2
            viewclass: "BoxLayout"
            data: [ {"orientation": "horizontal", "size_hint_y": None, "height": "44dp",
                     "children": [
                        Label(text=f"#{it['id']} {it['name']} — {it['date']} {it['time']} [{it['status']}]", size_hint_x: .6),
                        Button(text:"Conferma", size_hint_x:.13, on_release=lambda w, i=it['id']: root.action(i, 'confirm')),
                        Button(text:"Annulla",  size_hint_x:.13, on_release=lambda w, i=it['id']: root.action(i, 'cancel')),
                        Button(text:"Check-in", size_hint_x:.14, on_release=lambda w, i=it['id']: root.action(i, 'checkin')),
                     ]} for it in root.items ]
            RecycleBoxLayout:
                default_size: None, dp(44)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
''',
    "main.py": r'''
import pathlib
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.lang import Builder
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
'''
}

for rel, content in files.items():
    p = MOB / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

print("OK: cartella 'mobile_kivy' creata con tutti i file.")
