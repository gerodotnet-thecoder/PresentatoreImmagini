@echo off
cd /d "%~dp0"
echo Sicurezza Portabilita' - Esecuzione nella cartella locale
echo Creazione dell'ambiente virtuale...
python -m venv .venv
echo Installazione di PyQt6...
.venv\Scripts\python.exe -m pip install PyQt6
echo.
echo =========================================
echo Setup Completato!
echo Per avviare il programma fai un doppio clic su:  AVVIAMI.vbs
echo =========================================
