Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName)
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /c cd /d """ & strDir & """ && npx electron .", 0, False
