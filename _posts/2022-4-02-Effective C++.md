---
title: Effective C++
author: xyx
date: 2022-4-02 20:33:00 +0800
categories: [C++, effective]
tags: 
math: true
---

## 03 尽可能使用const

### 1. 底层与底层指针

> 书中的说法可能会好理解一点，出现在*号左边，表示被指物是常量。const 出现在*号的右边，表示指针是常量。

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

3. **如果返回类型为内置类型，那么改动函数返回值从来就不合法**

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
