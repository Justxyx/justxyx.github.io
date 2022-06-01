---
title: Effective C++ p3 资源管理
author: xyx
date: 2022-5-11 20:33:00 +0800
categories: [C++, effective]
tags: 
math: true
---

## 13. 以对象管理资源

申请一块动态内存后，可能会发生泄露，其原因无非以下几点：

- 忘记delete

- 有delete，但是提前returnle

- 抛出异常了

所以，最好的解决方法就是，使用对象来管理资源，包括下列两个关键性的想法：

1. 获得资源后立刻放进管理对象

2. 管理对象运用的对象确保资源会被释放。**如条款8中提到的 析构函数抛出异常**

简单说一下两类智能指针，`auto_ptr` 和 `shared_ptr`.

1. `auto_ptr`现在基本不用了，主要原因是其在拷贝构造与拷贝赋值中，会将原始的对象的指针置为NULL，拷贝后的对象获得这唯一指针。这设计...enm...。确实保证了任何时候只有一根指针。

2. `shared_ptr`,聪明多了，会有计数器。所以推荐使用`shred_ptr`.

3. 最重要的一个问题，上述两智能指针都未对数组指针有优化，其`delete p`动作，而不是`delete p[]`动作，关键是**编译器还不报错**。这个问题的解释为：vector 和 string 基本可以替代数组的大部分大部分要求了，如果你非要智能指针来管理数组指针，推荐使用别的。

## 14. 在资源管理类中小心copying行为

```cpp
class Lock{
public:
    Lock(Mutex *mutex):mutex(mutex){
        lock(mutex);
    }
    ~Lock(){
        Unlock(mutex);
    }
private:
    Mutex *mutex;
}
```

利用上述代码，给代码段加锁，下述代码是可以的：

```cpp
Mutex m;
Lock lock(&mutex);
```

那如果复制呢？

```cpp
Lock lock2(&mutex);
```

上述代码不可以这样简单直接复制。对于资源管理类中的copying，一般有下面几条建议：

1. 禁止复制，最简单直接，将默认拷贝构造设置为private或者 `=delete c++11`.

2. 对底层数据使用“引用计数法”，即记录该资源引用的次数，可以用`shared_ptr`.不过有一点需要格外注意一点，**本例中如果使用`shared_ptr`智能指针来引用mutex 成员变量，那么该类就不需要额外的析构函数**。为什么？在条例5中说到过，class 会自动调用no_static成员变量的析构函数，即本类会自动调用shared_ptr智能指针的析构函数。还有一个小问题，shared_ptr智能指针默认的析构函数是删除该资源，不过幸运的是我们可以给该智能指针指定一个删除器。针对本例，我们要的不是删除锁而是释放锁，所以我们要求的是删除器解除该锁。

3. 对底部资源进行深拷贝

4. 对底部资源进行转移，例如`auto_ptr`.

## 15. 在资源管理类中提供对原始资源的访问

这个没看懂

## 16. 成对使用new 和 delete 要采取相同的形式

对于数组，`string *s = new string[5];` 会发生什么 ？

string 的构造函数将会被调用5次。

`delete s` 与 `delete s[]` 区别：
两者都会删除5个string大小的内存区域，但是，**前者只会调用一次析构函数**。

多以，结论：new时使用[]，delete 时也要delete[]。

## 17 以独立的语句将newed对象置入智能指针

现有函数接口：
`void processWidget(shared_ptr<Widget> pw,int priority);`

1. 调用1

    `processWidget(new Widget,prioryit())`, 错误，shared_ptr构造函数是`explict`的。

2. 调用2

    `processWidget(shared_ptr<Wiget>(new Wiget),prioryit())`

    **可能会发生资源泄露**。编译器的调用步骤可能是：
    - new Wiget
    - priority()
    - shared_ptr的构造函数
    如果对priority()的函数调用失败，那么new Wiget的构造就会产生资源泄露。

3. 调用3 正确调用

    - `shared_ptr<Wiget>  p(new Wiget);`.   
    - `processWidget(p,prioryit())`;

总结一下，用独立的new 对象存储在智能指针中，如果不这么做，一单有异常抛出，会产生难以察觉的资源泄露。

