---
title:  基础库不匹配导致的dlcose core 问题
author: xyx
date: 2025-4-24 13:33:00 +0800
categories: [justxyx, system-programming]
tags:
math: true
---

## 1. 问题概述

```c
(gdb) bt
#0  0x00007ffff604e8bd in sigprocmask () from /usr/lib/libc.so.6
#1  0x00007ffff604f898 in abort () from /usr/lib/libc.so.6
#2  0x000000000041eb7d in death (sig=11, info=<optimized out>, addr=<optimized out>)
    at src/wafd.c:603
#3  <signal handler called>
#4  0x0000000000000000 in ?? ()
#5  0x00007ffff7fe9ce1 in ?? () from /lib64/ld-linux-x86-64.so.2
#6  0x00007ffff7fe9f0e in ?? () from /lib64/ld-linux-x86-64.so.2
#7  0x00007ffff614909f in _dl_catch_exception () from /usr/lib/libc.so.6
#8  0x00007ffff614912f in _dl_catch_error () from /usr/lib/libc.so.6
#9  0x00007ffff74c3985 in ?? () from /usr/lib/libdl.so.2
#10 0x00007ffff74c33b3 in dlclose () from /usr/lib/libdl.so.2
```

简单描述就是： 多线程加载同一个动态库， 加载 & 运行都正常。 动态库dlclose 时出现core， 如上图所示。
第一排查方向以为是句柄多次卸载问题， 后续debug 发现并非是此问题。

后来抽空想了一下，既然该二进制是以jemalloc 分配&释放内存， dlclose 时候走到ld & libc.so.6 中的时候就应该察觉到 是链接库异常不匹配导致的。

## 2. 问题根因

A 动态库编译时候链接的是libjemalloc.so.2， 而A动态库运行时会加载B动态库（该动态库为外部获取， 不可利用libjemalloc.so.2 重新编译）， 导致A 动态库dlose 时core

```shell
// A 动态库链接
root>ldd ./absorb_star.so
        libpthread.so.0 => /opt/nsfocus/lib64/local/libpthread.so.0 (0x00007ffff7be8000)
        libjemalloc.so.2 => /opt/nsfocus/lib64/local/libjemalloc.so.2 (0x00007ffff774e000)

// B 动态库链接
root>ldd ./libstar.so 
        libc.so.6 => /usr/lib/libc.so.6 (0x00007ffff766b000)
```

- ​​A 动态库 (absorb_star.so)​​ 链接了 libjemalloc.so.2（自定义内存分配器）。
​
- B 动态库 (libstar.so)​​ 链接了系统默认的 libc.so.6（使用 glibc 的 malloc/free）。
​
### 根本原因

    ​问题现象​​：当 A 动态库卸载（dlclose）时，发生 ​​Core Dump​​。

​1. 内存分配器冲突​​

- ​A 库​​ 使用 jemalloc 分配内存（如线程局部存储、锁、内部数据结构）。
- B库​​ 使用 glibc 的 malloc/free。
- 当 dlclose 卸载 A 库时，jemalloc 会尝试释放其管理的内存，但部分内存可能已被 B 库用 glibc 的 free 错误释放，导致 ​​双重释放（Double Free）​​ 或 ​​内存访问越界​​。

2. 符号劫持（Symbol Interposition）​​

- jemalloc 会覆盖 glibc 的 malloc/free 等符号。
- 如果 B 库内部假设使用 glibc 的实现，但实际调用了 jemalloc 的版本，可能导致 ​​未定义行为​​。

## 3. 扩展聊聊 jemalloc

| 特性               | libjemalloc.so.2                                   | libc.so.6 (glibc)                          |
|--------------------|---------------------------------------------------|--------------------------------------------|
| **线程优化**       | 每个线程独立内存池，减少锁竞争                     | 全局锁管理，多线程性能较差                 |
| **内存碎片**       | 通过分配大小分类（Size Classes）减少碎片           | 碎片化较严重，长期运行可能内存泄漏         |
| **扩展功能**       | 支持内存统计、泄漏检测、性能调优接口               | 仅提供基础 malloc/free/calloc/realloc       |
| **符号覆盖**       | 默认劫持 malloc/free 等符号，替换glibc实现         | 原生实现，无劫持行为                       |
| **依赖关系**       | 需显式链接（-ljemalloc）或 LD_PRELOAD 加载         | 所有程序默认链接，无需额外操作             |


###  一个二进制， 运行的过程中可以连接 libjemalloc.so.2  也可以连接 libc.so.6 ，

```shell
// 1. 实现方案
# 编译时不链接 jemalloc，保持动态选择能力
# 不加 -ljemalloc，避免固化依赖关系。
# 添加 -ldl 以支持运行时动态库加载。
gcc -o my_program my_program.c -ldl -lpthread

// 2. 创建软链接指向目标分配器
# 默认使用 jemalloc
sudo ln -sf /opt/nsfocus/lib64/local/libjemalloc.so.2 /usr/local/lib/libcurrent_malloc.so

# 切换为 glibc 时
sudo ln -sf /usr/lib/libc.so.6 /usr/local/lib/libcurrent_malloc.so

// 3. 通过 LD_PRELOAD 加载目标分配器
#!/bin/bash
# run_program.sh

# 强制预加载当前选择的分配器
export LD_PRELOAD="/usr/local/lib/libcurrent_malloc.so"

# 启动程序
./my_program

// 4. 重启进程完成切换​
# 切换到 jemalloc
sudo ln -sf /opt/nsfocus/lib64/local/libjemalloc.so.2 /usr/local/lib/libcurrent_malloc.so
pkill my_program  # 结束旧进程
./run_program.sh  # 启动新进程

# 切换到 glibc
sudo ln -sf /usr/lib/libc.so.6 /usr/local/lib/libcurrent_malloc.so
pkill my_program
./run_program.sh

```

## 4. 一个题外话, 部分 libpthread 库导致gdb attach 不可用问题

```c
// 异常情况
Reading symbols from /opt/nsfocus/lib64/local/libpthread.so.0...(no debugging symbols found)...done.
warning: Unable to find libthread_db matching inferior's thread library, thread debugging will not be available.

// 正常情况
Reading symbols from /opt/nsfocus/lib64/local/libpthread.so.0...done.
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/usr/lib/libthread_db.so.1".
```

- 根本原因​​：
GDB 依赖 libthread_db.so.1 来调试线程，但该库必须与目标程序的 libpthread.so.0 ​​版本严格匹配​​。若版本不兼容，GDB 无法解析线程状态。 后面略 ~

