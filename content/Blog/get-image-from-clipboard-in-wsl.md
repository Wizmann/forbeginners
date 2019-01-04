Date: 2019-01-04
Title: 在WSL中获取Windows剪贴板中的图片
Tags: 闲聊, WSL, powershell
Slug: get-image-from-clipboard-in-wsl.md

## 背景

Win10里面的WSL（Windows Subsystem For Linux)算是一个开发神器了，虽然功能不是100%完善，但是对于轻度开发已经足够了。现在我的日常开发，就是一个全屏CMD跑内部工具，一个全屏WSL跑tmux+vim。

（跑题了）

## 问题

之前的文章里，我有写到使用github做为图床，并且使用python脚本进行图片上传。但是仍有一点问题，就是之前的脚本只能上传文件，不能直接上传剪贴板里的图片。

## 解决

发现Windows里面有内置的访问剪贴板工具，但是只在powershell下可用。不过我们可以在WSL里直接调用exe文件（这点非常神奇），然后读出图片文件放入临时文件夹。然后我们再读出这个文件进行上传。

总的流程仍然是上传已有的图片文件，但是我们把它放在临时文件夹并隐藏了起来。看起来就是实现了WSL和Windows剪贴板的互操作。

```bash
#!/bin/bash

TMP=/mnt/c/Users/me/AppData/Local/Temp/
TMPWIN=C:\\Users\\me\\AppData\\Local\\Temp\\

ts=`date +"%Y-%m-%d_%H-%M-%S"`

echo "(Get-Clipboard -Format Image).Save(\"$TMPWIN\\$ts.png\")" | /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe &> /dev/null

if [ $? -ne 0 ]
   then
       echo "no image in clipboard"
   else
       python upload.py $TMP/$ts.png
   fi
```
