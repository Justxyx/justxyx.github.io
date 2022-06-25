---
title: Effective C++ p4 设计与声明
author: xyx
date: 2022-6-23 20:33:00 +0800
categories: [C++, effective]
tags: 
math: true
---


## 20.宁以pass-by-reference-to-const 替换 pass-by-value

### pass-by-reference-to-const 的好处

1. pass-by-value 会造成多次的无必要的析构，**拷贝构造**。

2. 继承中的多态问题，只有指针与引用可以多态使用。

```cpp
class Person {
    public:
        string name;
}

class Student :public Person {
    public:
        int age;
        void method() {

        }
}
```

```cpp
// pass-by-value 没有多态性 该调用时错误的
void test(Pserson p) {
    p.method();
}
```

## 21. 必须返回对象时，不必妄想返回reference

常见的必须返回对象的运算符函数：

```cpp
const Rational opeartor* (const RAtional &lhs, const Rational &rhs);
```

1. 使用stack 构造一个局部对象返回

    ```cpp
    const Rational& opeartor* (const RAtional &lhs, const Rational &rhs){
        return Rational(lhs.n + rhs.n);
    }
    ```

    reference 的本意是避免不必要的构造函数和析构函数，但是本例中不仅有构造和析构，而且在函数调用完成以后**局部对象就已经销毁**，reference指向一个销毁的局部对象，是错误的。

2. 使用heap 构造

    ```cpp
    const Rational& opeartor* (const RAtional &lhs, const Rational &rhs){
        return  *(new Rational(lhs.n + rhs.n));
    }
    还是有析构跟构造，最重要的是，什么时候销毁这个对象呢？ 会造成资源泄露。

3. 构造一个static 局部对象


    ```cpp
    const Rational& opeartor* (const RAtional &lhs, const Rational &rhs){
        static Rational r(lhs.n + rhs.n);
        return  r;
    }
    ```
    
    两个问题：
    - 多线程时，static Rational 是不安全的
    -  `Rational a,b,c,d;  if ((a*b) == (c*d)){} ` 该if判等永远是`true`.

## 22. 成员变量应该是private

**其实只有两种权限，private（提供封装） 和 其他 （不提供封装）**

- 切记将成员变量声明为private
- protected 并不比public 更具有封装性（这个很疑惑）

**假设有一个 public 成员变量，而我们最终取消了它。所以使用它的客户代码都会被破坏。因此，public 成员变量完全没有封装性。假设有一个 protected 变量，而我们最终取消了它，所有使用它的派生类都会被破坏。因此，protected 成员变量也缺乏封装性因此，从封装的角度看，只有 private 能提供封装性**。

## 23.宁以 non-member，non-friend 替换 member 函数

一个浏览器代码：

```cpp
class WebBrowser {
public:
    void clearCache();
    void claerCookies();
    void clearHistory();
}
```

如果想一个函数执行这所有功能，两种选择，一种member 函数，一种实现non-member函数：

```cpp
// 实现成员函数
void clearEverything() {
    clearCache();
    clearCookies();
    clearHistory();
}

// 非成员函数
void clearEverything(webBrowser &wb) {
    wb.clearCache();
    wb.claerCookies();
    wb.clearHistory();
}
```

**如何选择 ？ 用成员函数还是非成员函数？**.

如果某些东西被封装，它就不再可见。越多东西被封装，越少人可以看到它。越少人看到它，就有越大的弹性去变化它，**因为我们的改变仅仅直接影响看到改变的那些人事物**.
因此，对于对象内的代码。越少代码可以看到数据（也就是访问它），越多的数据可被封装，我们也就越能自由地改变对象数据。作为一种粗糙的测量，越多函数可访问它，数据的封装性就越低.

**如果要在一个 member 函数和一个 non-member，non-friend 函数之间做选择，而且两者提供相同机能，那么，导致较大封装性的是 non-member，non-friend 函数**

## 24.若所有参数都需要类型转换，请为此采用non-member函数

