<# setup_kivy.ps1
Automatizza l’installazione e l’avvio dell’app Kivy con Python 3.11 su Windows.
Esegui da PowerShell nella root del progetto: 
    powershell -ExecutionPolicy Bypass -File .\setup_kivy.ps1
#>

$ErrorActionPreference = "Stop"

function Write-OK($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-INFO($msg)  { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-WARN($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-ERR($msg)   { Write-Host "[ERR] $msg" -ForegroundColor Red }

# 0) Vai nella cartella dello script (root progetto)
Set-Location -Path $PSScriptRoot

# 1) Verifica Python Launcher e versione 3.11
Write-INFO "Verifico installazioni Python..."
try {
    $pyList = & py -0p 2>$null
} catch {
    Write-ERR "Python Launcher non trovato. Installa Python 3.11 da https://www.python.org/downloads/release/python-3119/ (spuntare 'Add python.exe to PATH')."
    exit 1
}

if ($pyList -notmatch "3\.11") {
    Write-ERR "Non trovo Python 3.11. Installa da: https://www.python.org/downloads/release/python-3119/"
    Write-Host $pyList
    exit 1
}
Write-OK "Python 3.11 rilevato."

# 2) Crea venv se non esiste
$venvDir = ".venv_kivy"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
if (!(Test-Path $venvPython)) {
    Write-INFO "Creo virtualenv $venvDir con Python 3.11..."
    & py -3.11 -m venv $venvDir
    Write-OK "Virtualenv creato."
} else {
    Write-INFO "Virtualenv già presente: $venvDir"
}

# 3) Aggiorna pip/setuptools/wheel nel venv
Write-INFO "Aggiorno pip/setuptools/wheel..."
& $venvPython -m pip install -U pip setuptools wheel
Write-OK "pip/setuptools/wheel aggiornati."

# 4) Installa Kivy nel venv (base)
Write-INFO "Installo Kivy 2.3.0..."
& $venvPython -m pip install "kivy[base]==2.3.0"
Write-OK "Kivy installato."

# 5) Requisiti opzionali da mobile_kivy/requirements.txt (se presente)
$reqFile = "mobile_kivy\requirements.txt"
if (Test-Path $reqFile) {
    Write-INFO "Installo requirements aggiuntivi da $reqFile..."
    & $venvPython -m pip install -r $reqFile
    Write-OK "Requisiti aggiuntivi installati."
} else {
    Write-WARN "File $reqFile non trovato (ok, non è obbligatorio)."
}

# 6) Avvia l’app mobile
$entry = "mobile_kivy\main.py"
if (!(Test-Path $entry)) {
    Write-ERR "File di avvio $entry non trovato. Hai creato la cartella mobile_kivy?"
    Write-Host "Se no, esegui prima:  python make_mobile_kivy.py"
    exit 1
}

Write-INFO "Avvio app mobile con l'interprete del venv..."
& $venvPython $entry
