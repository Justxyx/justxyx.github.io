---
title: Effective C++ p7 模板与泛型编程
author: xyx
date: 2022-7-06 20:33:00 +0800
categories: [C++, effective]
tags: 
math: true
---

## 41. 了解隐式接口和编译器多态

对于类而言：

- 显式接口
- 运行时多态

对于模板而言：

- 隐式接口
- 编译时多态

### 1.编译时期多态与运行时期多态：

- 编译时期多态，类似于函数重载，哪一个重载函数被调用。
- 运行时期多态， 哪一个虚函数被绑定。

### 2. 显示接口 与 隐式接口

显示接口：

- 通常显式接口有函数的签名(也就是函数名称、参数类型、返回类型)构成。

    ```cpp
    class Widget{
    public:
        Widget();
        virtual ~Widget();
        virtual std::size_t size() const;
        virtual void normalize();
        void swap(Widget& other);
    };
    ```

- 隐式接口： 它并不基于函数签名式，而是由有效表达式组成。

    ```cpp
    template<typename T>
    void doProcessing(T & w){
        if(w.size() > 10 & w != someNestyWidget){}
    }
    ```

    1. 它必须提供一个叫做size()的成员函数，该函数返回一个整数值
    2. 它必须支持一个叫做operator!=的函数，用来比较两个对象

    然而，实际上这个两个约束都不需要满足。T必须支持成员函数，但是这个函数也可以从基类继承。这个函数不一定返回int，它唯一要做的是返回一个类型为X的对象，而X对象加上一个int(10的类型)必须能够调用一个operator>。同理，T并不需要支持operator!=。**可以看出，隐式接口仅仅是由一组有效表达式组成**。

### 3. 总结

- 类和模板都支持接口(interface)和多态
- 对类而言接口是显式的，以函数前面为中心。多态是通过vritual函数发生在运行期
- 对模板参数而言，接口是隐式的，是基于有效表达式的。多态则是通过模板具现化和函数重新解析发生于编译期

## 42. 了解typename 的双重意义

### 1. 在下列情况猴子那个，typename 与 class 是等价的。

```cpp
template<class T>
class Widget{};

template<typename T>
class Widget{};
```

### 2. 特殊情况说明

- 从属名称
    template 内出现的名称如果依赖某个template参数， 就称之为从属名称。

- 非从属名称
    不依赖与任何template参数的名称。

```cpp
template<typename C>
void print2nd(const C& container)
{
C::const_iterator *x;  // 从属名称
int s;      // 非从属名称
...
}
```

我们认为 C::const_iterator 表示容器 C 的迭代器类型，因此上述代码定义一个该迭代器类型的指针。但是这是一种先入为主的思想。如果 C::const_iterator 不是一个类型呢？比如恰巧有个 static 成员变量被命名为 const_iterator，或如果 x 碰巧是个 global 变量名称？那样的话上述代码就不再是声明一个 local 变量，而是一个相乘动作。

因此，C++有个规则解决这种歧义：**如果解析器在 template 中遭遇一个嵌套从属名称，它便假设这个名称不是个类型，除非你告诉它是。**所以缺省情况下嵌套从属名称不是类型。那么怎么告诉它是一个类型，当然就是 typename 了，所以上述代码应该像这样：

```cpp
template<typename C>
void print2nd(const C& container)
{
typename C::const_iterator *x;
...
}
```

因此，规则是：除了下面 2 个例外，任何时候当你想要在 template 中指涉一个嵌套从属类型名称，就必须在紧临它的前一个位置放上关键字 typename：

1. typename 不可出现在 base classes list 内的嵌套从属名称之前
2. typename 也不可出现在成员初始值列表中作为 base class 修饰符

## 43.学会处理模板化基类内的名称

一个程序， 他能传送不同的信息到不同的公司去， 信息的传送方式有两种， 明传送与加密传送。 其代码可以写成如下部分：

```cpp
class CompanyA {
public:
    void sendClearText (const string &str) {cout << "ConpanyA:" << str << endl;};
    void sendEncrypted(const string &str) {cout << "CompanyA:" << str << endl;};
};

class CompanyB {
public:
    void sendClearText (const string &str) {cout << "CompanyB:" << str << endl;};
    void sendEncrypted(const string &str) {cout << "CompanyB:" << str << endl;};
};

template<typename T>
class MsgSender {
public:
    void sendClear(const string &str) {
        T t;
        t.sendClearText(str);
    }

    void sendSecret(const string &str) {
        T t;
        t.sendClearText(str);
    }
};
```

### 1. 加一个日志系统试试

该函数无法通过编译

```cpp
template<typename T>
class LogMsgSender : public MsgSender<T>{
public:
    void sendClearMsg (string &str) {
        // 写log
        sendClear(str);
        // 写log
    } 
};
```

原因如下， MsgSender 可能存在特化：

```cpp
class CompanC {
public:
    void sendEncrypted(const string &str) {
        cout << "CompanyC:" << str << endl;
    }
};

template<>
class MsgSender<CompanC> {
public:
    void sendSecret(const string &str) {
        CompanC c;
        c.sendEncrypted("hey");
    }
};
```

这就是为什么不能通过编译的原因， **它知道base class template 有可能被特化， 而那个特化的版本可能不提供和一般template相同的接口**。

### 2. 解决办法

```cpp
template<typename T>
class LogMsgSender : public MsgSender<T>{
public:
    void sendClearMsg (string &str) {
        // 写log

        // 1.
        this->sendClear(str);
        
        // 2.
        using MsgSender<T>::sendClear;
        sendClear;
        
        // 3.
        MsgSender<T>::sendClear(str);
        
        
        // 写log
    }
};
```

## 44. 将与参数无关的代码抽离 templates

模板提供的是编译期的多态，即使你的代码看起来非常简洁短小，生成的二进制文件也可能包含大量的冗余代码。 **因为模板每次实例化都会生成一个完整的副本**,所以其中与模板参数无关的部分会造成代码膨胀.

### 1.对于非模板参数产生的代码膨胀

```cpp
// 典型例子
template <typename T, std::size_t n>
class Matrix {
  public:
    void invert();
};

Matrix<double, 5> m1;
Matrix<double, 10> m2;
//会具现两份非常相似的代码，除了一个参数5，一个参数10
```

改进：

```cpp
template <typename T>
class MatrixBase {
  protected:            // protected 保证只有本类/子类本身可以调用
    void invert(std::size_t n);
}

template<typename T, std::size_t n>
class Matrix : private MatrixBase<T> { // private继承，derived 和base不是is-a关系，
                                       // base只是帮助实现derived 
  private:
    using MatrixBase<T>::invert;       // derived class 会掩盖template base class的
                                       // 函数
                    
  public:
    inline void invert() { this->invert(n);}
}
```

### 2.对模板参数产生的代码膨胀

- int 和 long 在多数平台都是一样的底层实现，然而模板却会实例化为两份，因为它们类型不同

- List<int >, List<const int >, List<double *>的底层实现也是一样的。但因为指针类型不同，也会实例化为多份模板类 如果某些成员函数操作强型指针(T*)，应该令它们调用另一个操作无类型指针(void*)的函数，后者完成实际工作。

## 45. 运用成员函数模板接受所有兼容类型

留坑。

## 46. 需要类型转换时请为模板定义非成员函数

可以结合条款24看。一个如24的demo：

```cpp
template<typename T>
class Rational {
public:
    Rational(const T &i = 12, const T &j = 13) : i(i),j(j) {}

private:
    int i;
    int j;
};

template<typename T>
const Rational<T> operator* (const Rational<T> &lhs,
                             const Rational<T> &rhs){
    cout << "opreator * has been success" << endl;
}    

int main () {
    Rational<int> oneHalf(1, 2);
    Rational<int> oneThird(1, 3);
    auto p = oneHalf * oneThird;  // 编译通过

    auto p2 = oneHalf * 3;  // 编译失败 报错
}
```

**template 实参推导过程中从不将隐式类型转换函数纳入考虑**

模板化的Rational 与非模板化的版本不同， 将 oneHalf 传递给 operator*时，它将 T 推断为 int，因此期待第二个参数也为 Rational，但是第二个参数为 int，前面我们说了，template 实参推导过程中从不将隐式类型转换函数纳入考虑。因此编译错误那么解决办法是什么？


### 1. 方案1

在 class template 将其声明为 friend，从而具现化一个 operator*，具现化后就可以不受 template 的限制了：

```cpp
template<typename T>
class Rational {
public:
    Rational(const T &i = 12, const T &j = 13) : i(i),j(j) {}
    friend const Rational operator*(const Rational<T> &lhs,
                                    const Rational<T> &rhs);
private:
    int i;
    int j;
};
```

**编译通过， 但链接错误**。

如果上面只有函数声明，而函数定义在类外，那么会报链接错误。当传入第一个参数 oneHalt 时，会具现化 Rational<int>，编译器也就知道了我们要调用传入两个 Rational<int>的版本，但是那个函数只在类中进行了声明，并没有定义，不能依赖类外的 operator* template 提供定义，我们必须自己定义，所以会出现链接错误。

### 2.方案2

```cpp
template<typename T>
class Rational {
public:
    Rational(const T &i = 12, const T &j = 13) : i(i),j(j) {}
    friend 
    const Rational<T> operator* (const Rational<T> &lhs,
                                 const Rational<T> &rhs){
        cout << "opreator * has been success" << endl;
    }
private:
    int i;
    int j;
};
```

这样看起来有点像是 member 函数，但是因为 friend 关键字，所以实际是 non-member 函数，如果去掉 friend 关键字，就成了 member 函数，但是此时参数也只能有 1 个，就不能实现所有参数的隐式转换.

**上面的代码可能还有一个问题，虽然有 friend，上述函数仍是隐式的 inline。如果函数实体代码量较大，可以令 operator*不做任何事，只调用一个定义与 class 外部的辅助函数**.

### 3.总结

当我们编写一个class template时， 请它所提供值“一次tempalte相关的”函数支持“所有参数之隐式类型转换”时， 请将那些函数定义为“class template 内部的friend函数”。

## 47. 请使用traits classes 表现类型信息

留坑

## 48. 认识template 元编程

留坑