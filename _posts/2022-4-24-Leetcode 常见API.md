---
title: LeetCode 常见API
author: xyx
date: 2022-4-24 20:33:00 +0800
categories: [C++, leetcode]
tags: 
math: true
---

> 主要记录一些常见的小细节，int 转 str.str 转 int等。  C++实现。

- int 转 str

    ```cpp
    int i = 12;
    string s = to_string(i);
    ```

- str 转 int
    ```
    string s("0123");
    int i = atoi(s.c_str());
    ```