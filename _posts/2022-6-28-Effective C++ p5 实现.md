---
title: Effective C++ p5 实现
author: xyx
date: 2022-6-28 20:33:00 +0800
categories: [C++, effective]
tags: 
math: true
---

## 26. 尽可能的延后变量定义出现的时间

一点说明：

```cpp
Person p("xx",13); // 构造函数
Person p2("zz",13); // 构造函数
Person p3 = p2; // 拷贝构造
p2 = p;     // 赋值构造
```

尽可能使用：

```cpp
// 良好的习惯
Object o(o2);

// 不好的习惯
Object o;
o = o2;  // 先构造在赋值 效率低
```