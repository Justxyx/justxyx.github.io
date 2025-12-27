---
title: Effective C++ p4 设计与声明
author: xyx
date: 2022-6-23 20:33:00 +0800
categories: [justxyx, c-cpp]
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

基础类如下：

```cpp
class Rational {
public:
    RAtional(int numerator = 0,
            int denominator = 1);
    int numerator () const;
    int denominator () const; 
private:
}
```

如果想为该类支撑起诸如加法，乘法的运算，那么该使用 **member** or **no_member** 函数 ？

### 使用member函数

```cpp
class Rational {
public:
    const Rational operator* (const Rational &rhs) const;
}
```

```cpp
Rational oneEighth(1,8);
Rational oneHalf(1,2);
Rational result = oneHalf * oneEighth;  // 正确
result = result * oneEighth;        // 正确

result = oneHalf * 2;   // 正确
result = 2 * oneHalf;   // 错误
```

`result = oneHalf * 2` 的逻辑可以转换为：

```cpp
const Rational temp(2);
result = oneHalf * temp;
```

前提是该构造函数为 **no-explicit**构造函数。

**但是用上述方法，member 函数来使用，其加法不满足交换律，这也不是我们想看到的**。

### 使用no_member函数

```cpp
class Rational {
    ...
}
const Rational operator* (const Rational &lhs,
                            const Rational &rhs)
{
    ...
}
```

使用no-member函数即可完美解决上述问题。


## 25 考虑写出一个不抛出异常的swap

深拷贝问题：

```cpp
// 可结合条款11查看
class Person {
public:
    Person(string names) {
        name = new string(names);
    }
    
    Person(Person &p) {
        name = new string(*p.name);
    }
    
    Person& operator=(const Person p){  // 拷贝赋值一定要注意
        if (this == &p)
            return *this;
        string *temp = p.name;
        name = new string(*p.name);
        delete temp;
        return *this;
    }

private:
    string *name;
};
```

### 一个由编译器构造的类 其swap是如何完成的？

```cpp
namespace std {
    template<class T>
    void swap(T &a, T &b) {
        T temp(a);  // 拷贝构造
        a = b;    // 拷贝赋值
        b = temp; // 拷贝赋值
    }
}
```

### point to implementtation (pimpl写法)

> 以一个指针指向数据

```cpp
class WidgeImpl {
private:
    string ss;
    vecotr<int> v;  // 总之很多数据    
}
```

```cpp
class Widet {
public:
    Widet(const Widet &rhs){} // 拷贝构造

    Widet& operator =(cosnt Widet &rhs) { // 赋值构造
        ...
        *pImpl = *(rhs.pImpl);  // 这个可以见条款11和12 深浅拷贝
        ...
    }
private:
    WidgeImpl *pImpl;
}
```

**可以试想一下，如果用编译器自带的swap函数，会构造多次Widet 的构造函数与析构函数，而我们想要的，仅仅是交换 Widet的两个数据指针而已**。

### 如果改进该类的swap函数？

```cpp
class Widet {
public:
    void swap(Widet &others) {
        using std::swap;
        swap(pImpl,others.pImpl);
    }
private:
    WidgeImpl *pImpl;
}

namespace std {
    template<>
    void swap<Widet> (Widet &a, Widet &b) {
        a.swap(b);
    }
}

```

### 那如果 Widet 是模板类呢 ？

下面的类是合法的：

```cpp
template <class T>
class WidetImpl {
private:
    T a;
    int b;
};

template <class T>
class Widet {
public:
    void swap(Widet<T> &other) {
        using std::swap;
        swap(p,other.p);
    }
private:
    WidetImpl<T> *p;
};
```

但是在std中却不合法：

```cpp
namespace std {
    template <class T>
    void swap<Widet<t>> (Widet &a, Widet &b) {
        a.swap(b);
    }
}
```

**不要在企图在std中新加东西**。

所以，我们应该如何做才好呢 ？ 新加命名空间并写出 non-member的swap函数：

```cpp
namespace xm {

template <class T>
Widet {   
}

template <class T>
void swap(Widet<T> &a, Widet<T> &b) {
    a.swap(b);
}

}
```

## 解释一下 `using std::swap` 与 命名空间 xm
 
会首先查找 xm 命名空间内的swap 函数， 如果没有合适的，就会向上寻找std 中偏特化版本的std::swap; 切记不可直接使用`std::swap(a,b)`,该用法会直接强制使用std默认的swap版本。
