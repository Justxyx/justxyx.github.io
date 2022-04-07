---
title: p9 Linux高性能服务器编程-- IO复用
author: xyx
date: 2022-4-7 20:33:00 +0800
categories: [C++, linux-os]
tags: 
math: true
---

## 1. select系统调用

select系统调用的用途是，在指定时间内，监听用户感兴趣的文件描述符上的可读，可写和异常事件。

### 1. select API

- 函数原型

    ```c
    int select(int nfds, fd_set *readfds, fd_set *writefds,
    fd_set *exceptfds, struct timeval *timeout);
    ```

- nfds
    监听的文件描述符的总数。

- readfds writefds exceptfds
    可读，可写，异常事件对应的文件描述符集合。

- fd_set 结构
    fd_set仅包含一个整形数组，每位标记一个文件描述符。

- timeout
    设置超时时间

