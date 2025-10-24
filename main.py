import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mobile_kivy.main import GiroMappeMobile

if __name__ == "__main__":
    GiroMappeMobile().run()
