Set WshShell = CreateObject("WScript.Shell")
' Ottiene la cartella in cui si trova esattamente questo file vbs (ovunque l'utente lo sposti)
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' Imposta la cartella di lavoro in modo da non sbagliare se il vbs viene lanciato da link o in altre modalità
WshShell.CurrentDirectory = strPath
' Esegue pythonW.exe direttamente dal venv locale, senza passare da activate.bat che non ama essere spostato
WshShell.Run "cmd.exe /c "".venv\Scripts\pythonw.exe main.py""", 0, False
