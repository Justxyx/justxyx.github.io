---
title: Effective C++ p2 构造 析构 赋值
author: xyx
date: 2022-4-025 20:33:00 +0800
categories: [C++, effective]
tags: 
math: true
---


## 05. 了解C++默认编写调用了哪些函数 ⭐️

编译器常规生成

```c
class Empte{
public:
    Empte() {}  // 默认构造
    Empte(const Empte &rhs){} // 拷贝构造
    ~Empte(){};  // 默认析构
    Empte &operator=(const Empte &rhs){} // 赋值构造
};
```

借上述代码只想说明两个问题：

1. 拷贝构造与赋值构造（编译器创造的版本）只是单纯的将non-static成员变量拷贝到目标对象。
2. 如果用户自己声明了构造函数，编译器将不再为它创建默认的构造函数。

**一个不太理解的小bug**

```c
class Empty{
public:
    string &name;
    string &pwd;

    Empty(string &name, string &pwd) : name(name), pwd(pwd) {}
};

int main(){
    string s1("jay");
    string s2("pwd");


    Empty empty(s1,s2); 
    Empty empty1 = empty;  //书中写的 编译器拒绝生成 "="  因为有reference  但是实际中可用。。。
    cout << empty1.name << endl;

}
```


