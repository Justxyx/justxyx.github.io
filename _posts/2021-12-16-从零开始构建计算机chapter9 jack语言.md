---
title: 从零开始构建计算机chapter9_jack语言
author: xyx
date: 2021-12-16 20:33:00 +0800
categories: [justxyx, computer-system-structure]
tags: 
math: true
---

## 一个由jack语言编写的类

类，方法，函数（类似于java中的静态函数），构造函数

```java
class Fraction{
    field int nemerator,denomeinator;  // 成员变量
    // 构造函数
    constructor Fraciotn new(int a,int b){
        let nemerator = a;
        let denomeinator = b;
        do reduce();
        return this;
    }

    // 方法
    method void reduce(){
        var int g;
        let g = Fraction.gcd(numerator,denominator);
        if  (g>1){
            let numerator = numerator / g;
            let denominator = denominator /g;
            return ;
        }
    }

    // 函数
    function int gcd(int a, int b){
        var int r;
        /*
        计算最大公约数
        */
        return a;
    }
}