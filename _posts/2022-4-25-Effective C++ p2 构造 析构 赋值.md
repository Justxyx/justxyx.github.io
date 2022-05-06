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

## 6 若不想使用编译器自动生成的函数，就明确拒绝

使用 private  或者 delete （C++11）

```c
class Fu{
public:
    Fu(int i, int j) : i(i), j(j) {};
//    Fu() = delete;
    Fu(Fu&) = delete;
    Fu& operator=(Fu&) = delete;
    // 或者
private:
    Fu();
private:
    int i;
    int j;

};
```

## 07. 为多态的基类声明virtual析构函数

### 1. 为基类声明virtual 析构函数

当派生类对象经由一个基类指针被删除，而该基类带有一个 non-virtual 析构函数，结果未定义——实际执行时通常发生的是对象的 derived 成分没有销毁。**即局部销毁**，造成资源泄露。（ 因此，不要继承一个没有 virtual析构函数的基类）

### 2. class 不作为基类的时候，不要将析构函数声明为virtual

增大内存开销

### 3. 有纯虚函数的class不能被实例化，那么，如果希望拥有抽象的class，但手头并没有 pure virtual 函数，定义一个virtual析构函数

```
class Demo{
public:
    virtual ~Demo() = 0;  // 申明为纯虚函数
};
Demo::~Demo() {}   // 需要定义
```

**注意，基类需要定义析构函数，即使他是纯析构函数，因为在子类的析构销毁中，会向上调用父类的析构销毁，必须要定义**。


## 08 析构函数中不要吐出异常

不要在析构函数中加入异常处理单元。 有异常的函数应该交给客户自己选择。


## 09 绝对不要在构造和析构的过程中调用virtual函数 ⭐️

哪怕嵌套调用也不行

## 10 重载运算符最好返回自身引用 reference *this

先想明白一个问题 为什么要返回引用 ？  

再看这个表达式 `A = B = C`


