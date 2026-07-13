# Using powershell

## 1. vim/nano alternative

The easiest way is to either use VSCode: ```code <file_name>```

Or use notepad: ```notepad <file_name>```

*Note about LF and CTRF syntax: in oder to use git bash to run .sh files, we must ensure the files uses LF. We can change this directly in vscode in the bottom left corner of the IDE.*

## 2. Running .sh files with git bash

Note: the default path for bash for powershell is ```C:\Users\STVN\AppData\Local\Microsoft\WindowsApps\bash.exe```, which is the WSL/Windows bash path.

What we actually want to use it the GIT bash at: ```C:\Program Files\Git\bin\bash.exe```

So either we run by calling this executable directly, or we can make an alias called ```gitbash``` that points to the executable by doing so: ```Set-Alias gitbash "C:\Program Files\Git\bin\bash.exe"``` in a powershell ```$PROFILE``` file.

Therefor, from now we can run an .sh file comfortably using ```gitbash <file_name>```