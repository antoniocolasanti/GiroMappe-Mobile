import zipfile, pathlib, datetime
HERE = pathlib.Path(__file__).parent
OUT = HERE / f"GiroMappe_Tkinter_FULL_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for p in HERE.rglob("*"):
        if p.name == OUT.name: continue
        z.write(p, p.relative_to(HERE))
print(f"Creato ZIP: {OUT}")
