---
title: Wireshark 抓包工具详解
author: xyx
date: 2022-5-09 20:33:00 +0800
categories: [justxyx, others]
tags: 
math: true
---


## 1. 模式介绍

- 混杂模式
    所有经过本网卡的数据包 都会被抓到（不会验证mac地址，常用作监听作用）

- 普通模式
    只抓发给本机的包

- 更改模式
    捕获 -> 选项 -> 开启关闭混杂模式

## 2. 删选

- 根据Ip筛选

    `ip.src_host == 192.168.2.104 or ip.dst_host == 192.168.2.1`

    或者 

    `ip.addr == 192.168.2.104`

## 3. ARP 抓包

## 4. TCP 抓包