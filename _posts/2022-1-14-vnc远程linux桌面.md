---
title: vnc 远程linux桌面  ubuntu 18.04
author: xyx
date: 2022-1-14 20:33:00 +0800
categories: [justxyx, others]
tags: 
math: true
---


1. 更新
`sudo apt-get update`

2. 安装

`sudo apt install gnome-panel gnome-settings-daemon metacity nautilus gnome-terminal ubuntu-desktop`

3. vnc

`sudo apt-get install vnc4server`

`sudo vncserver`

4. sudo vi ~/.vnc/xstartup

```c
#!/bin/sh
export XKL_XMODMAP_DISABLE=1
export XDG_CURRENT_DESKTOP="GNOME-Flashback:GNOME"
export XDG_MENU_PREFIX="gnome-flashback-"
gnome-session --session=gnome-flashback-metacity --disable-acceleration-check &
```

5. 重启

`sudo vncserver -kill :1 #杀掉原桌面进程，输入命令（其中的:1是桌面号）`

解决refuse问题

`vncserver -geometry 1920x1080 :2 -localhost no `