---
title: 重写linux命令05_stty
author: xyx
date: 2022-1-04 20:33:00 +0800
categories: [C++, linux-os]
tags: 
math: true
---


## 1. 设备也是文件

### 1.1 设备也具有文件名

设备文件一般存在在`/dev`目录下。

```c
(base) root@xm-System-Product-Name:/home/xm/xyx/linux_os# ls /dev/
autofs           i2c-1     loop23        pts       tty18  tty40  tty63      ttyS27   vcsa1
block            i2c-2     loop24        random    tty19  tty41  tty7       ttyS28   vcsa2
bsg              i2c-3     loop25        rfkill    
```

### 1.2 终端就像文件

- `tty`命令 告知用户终端文件名

```c
(base) root@xm-System-Product-Name:/home/xm/xyx/linux_os# tty
/dev/pts/1
```

- 向终端输入who

```c
(base) root@xm-System-Product-Name:/home/xm/xyx/linux_os# who > /dev/pts/1
xm       :0           2022-01-04 09:48 (:0)
xm       pts/1        2022-01-04 11:40 (192.168.2.103)
```

### 1.3 设备的文件属性

```c
