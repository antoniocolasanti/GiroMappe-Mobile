import sys, subprocess, pathlib
HERE = pathlib.Path(__file__).parent
ENTRY = HERE / "app" / "main.py"
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--name", "GiroMappe",
    "--noconfirm", "--onedir", "--clean",
    "--hidden-import", "sqlmodel",
    str(ENTRY),
]
print(" ".join(cmd))
subprocess.check_call(cmd)
print("Build completa. Cartella dist/GiroMappe")
