---
title: Effective C++ p1 让自己习惯C++
author: xyx
date: 2022-4-02 20:33:00 +0800
categories: [C++, effective]
tags: 
math: true
---

## 03 尽可能使用const

### 1. 底层与底层指针

> 书中的说法可能会好理解一点，出现在`*`号左边，表示被指物是常量。const 出现在`*`号的右边，表示指针是常量。

### 2. 迭代器的const指针

```c
vector<int> vec(10,1);

const vector<int>::iterator iter = vec.begin();  // 类似于 T * const 指针
//        --iter;  // 错误 为const 指针 不能改变
*iter = 10; // 正确

vector<int>::const_iterator ite2 = vec.begin();  // 类似于 const T * 指针
-- ite2;  // 正确
```

### 3. const成员函数（重点）

**如果两个成员函数只是常量性不同，则可以被重载**。

```c
    class TextBlock{
    public:
        const char& operator[](size_t position) const{
            return text[position];
        }
        char& operator[](size_t position){
            return text[position];
        }
    private:
    public:
        TextBlock(const string &text) : text(text) {}
    private:
        string text;
    };

    void test01(){
        TextBlock tb("Hello");
        const TextBlock ctb("Hello word");

        cout << tb[0];  // right
        tb[0] = 'c' ; // right

        cout << ctb[0];  // right
//        ctb[0] = 'x';  // flase
    };
```

1. `const char& method() const{}` 与 `char& method(){}`

    这两者函数是可以重载的，有点奇怪其实。 `const Demo d1` 调用 const成员函数，非const实例调用非const成员函数，这样一想好像也很说得通。

2. `non-const opertor[]`返回的是 `reference to char`, 而不是`char`
    所以`tb[0] = 'x'` 可以通过。

3. **如果返回类型为内置类型，那么改动函数返回值从来就不合法**,例如返回值是 `char` 而不是 `&char`

#### const成员函数的两个阵营

- bitwise const
    不改变一个成员的一个bit

- logical constness
    如下代码所示

```c
    class CTextBoloc{
    public:
        // 不太懂这里为什么不加const，加了const就无法改变。在上一个版本中不加const 编译器会直接报错。
        // 个人猜测，该成员函数不会改变成员，也就是指针pText的值，所以加不加都没报错。
        char& operator[](size_t position) const{
            return pText[position];
        }
    private:
        char *pText;
    public:
        CTextBoloc(char *pText) : pText(pText) {}
    };

    void test02(){
        const CTextBoloc cctb("hello");
        char *pc = &cctb[0];
        *pc = 'J';
    }
```

解释一下：
    **一个更改了指针所指物的成员函数，虽然不能算是const，但是如果只有指针（而非所其所指物）隶属于对象，那么称次函数为bitwise const不会引发编译器异议。**

#### 在const 成员函数内，成员函数也可被更改

**mutable**关键字

```c
    class CTextBoloc2{
    private:
        char* pText;
        mutable size_t textLength;
        mutable bool lengthIsValid;
    public:
        CTextBoloc2() {}
        size_t length() const{
            lengthIsValid = true;
        }
    };
```

## 04 确定对象使用前已被初始化

### 1. 永远在使用对象之前将它初始化

### 2. 对于类

1. 确保每一个构造函数豆浆对象的每一个成员初始化

2. 不要混淆**赋值** 与 **初始化**


    ```c
    // 赋值构造函数
    ABEntry::ABEntry(string &name, string &theAddress, list<PhoneNUmber> &phone) {
        // 这些都是赋值 而非初始化
        theName = name;
        theAddress = theAddress;
        thePhones = phone;
        numTimesConsulted = 0;
    }
    // 初始化构造函数
    ABEntry::ABEntry(const string &theName, const string &theAddress, const list<PhoneNUmber> &thePhones,
                    int numTimesConsulted) : theName(theName), theAddress(theAddress), thePhones(thePhones),
                                            numTimesConsulted(numTimesConsulted) {}
    ```

3. 赋值与初始化

    - 初始化的效率更高
    - 对于内置对象，初始化与赋值的成本相同

4. 有多个构造函数

    可以合理的在初值列中遗漏那些**赋值表现像初始化一样好**的成员变量

5. 成员初始化次序
    与变量次序相同


