Set WshShell = CreateObject("WScript.Shell")
strPath = WScript.ScriptFullName
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.GetFile(strPath)
strFolder = objFSO.GetParentFolderName(objFile)

mainScript = strFolder & "\main.py"

WshShell.CurrentDirectory = strFolder
WshShell.Run "python.exe main.py", 0, False
