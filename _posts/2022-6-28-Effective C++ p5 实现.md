---
title: Effective C++ p5 实现
author: xyx
date: 2022-6-28 20:33:00 +0800
categories: [justxyx, c-cpp]
tags: 
math: true
---

## 26. 尽可能的延后变量定义出现的时间

一点说明：

```cpp
Person p("xx",13); // 构造函数
Person p2("zz",13); // 构造函数
Person p4(p);    // 拷贝构造
Person p3 = p2; // 拷贝构造 这个很奇怪
p2 = p;     // 赋值构造
```

尽可能使用：

```cpp
// 良好的习惯
Object o(o2);
Object o = o2 ;  // 其实这个也是拷贝构造

// 不好的习惯
Object o;
o = o2;  // 先构造在赋值 效率低
```

## 27. 

    没看懂后面补坑

## 28. 避免返回handle 指向对象内部成分

### 1. 先看下面这一个例子

```cpp
class Demozz {
public:
    Demozz() {
        v = new vector<int>;
        for (int i = 0; i < 5; ++i) {
            v->push_back(i);
        }
    }

    ~Demozz() {
        delete v;
    }
    vector<int>* getV() const {
        return v;
    }

private:
    vector<int> *v;
};
```

```cpp
int main() {
    Demozz d;
    vector *v = d.getV();  // getV 成员函数为const 但是其还是会改变v
}
```

### 2. 给成员函数返回值加上const会不会好一点 ？

```cpp
    Demozz d;
    const vector<int> *v = d.getV();
```

会解决一部分问题，但是还有一个很严重的问题无法解决，即v为空指针问题，看下述讲解。

### 3. 加了const，为什么还是会有问题

```cpp
class Demo2 {
public:
    Demozz getD () {
        Demozz d;
        return d;
    }
};
```

```cpp
    Demo2 d;
    const vector<int> *v = d.getD().getV();   // 报错 v为空指针
    for (const auto &item : *v)
        cout << item << endl;
```

`d.getD`作用于一个临时变量`temp`上。 `temp` 随函数`getD`的返回而销毁. v指向一个空指针。

### 4. 总结

**避免handle（包括引用，指针迭代器等）指向对象内部**。

## 29. 为了异常安全的努力是值得的

一个切换背景图片的程序,看代码：

```cpp
class Menu{
Mutex mutex; //提供多线程互斥访问
Image *bg; //背景图片
int changeCount; //切换背景计数
public:
void changeBg(istream& sr);
};

void Menu::changeBg(istream& src){
lock(&mutex);
delete bg;
++changeCount;
bg = new Image(src);
unlock(&mutex);
}
```

该代码的两个不异常安全的点：

1.  若`new Image` 发生异常，那么 mutex 锁将不会被解锁。

2. 背景图片已经被删除，而且count 计数器已经增加。

### 1.异常安全函数的3个保证

1. 基本承诺：抛出异常后，对象仍然处于合法（valid）的状态。但不确定处于哪个状态（对于前面的例子，如果发生异常，PrettyMenu 可以继续拥有原背景图像，或是令它拥有某个“缺省”的背景图像，但客户无法确定）

2. 强烈保证：如果抛出了异常，状态并不会发生发生任何改变。就像没调用这个函数一样

3. 不抛掷保证：这是最强的保证，函数总是能完成它所承诺的事情（作用于内置类型身上的所有操作都提供 nothrow 保证。这是异常安全代码中一个必不可少的关键基础）

### 2. 为Menu 提供强烈保证

```cpp
class Menu{
shared_ptr<Image> bg;
...
};
void Menu::changeBg(istream& src){
Lock m1(&mutex); //Lock 以对象管理资源  条款14
bg.reset(new Image(src));   // 条款13 用智能指针来管理
++changeCount;
}
```

1. Lock 类来管理，可以自动的通过析构函数来解锁。
2. 用智能指针可以保证背景图片的管理，要么换，要么不换。`bg.reset(new Image(src))`可以看成一个原子操作（个人理解）
3. 注意，上述实现只能为 PrettyMenu 对象提供“强烈保证”，不能提供完美（即全局状态）的“强烈保证”。比如 Image 构造函数中移动了 istream& src 的读指针然后再抛出异常，那么系统还是处于一个被改变的状态。 这是一种对整个系统的副作用，**类似的副作用还包括数据库操作，因为没有通用的办法可以撤销数据库操作。 不过这一点可以忽略，我们暂且认为它提供了完美的强烈保证**。

### 3. copy and swap 技术

原则： 为你打算修改的对象做出一个副本，然后在那副本上做一切必要的修改。若有任何修改动作抛出了异常，原对象仍然保持为改变状态。带所有改变都成功后，做出一个不抛出异常的swap动作。

```cpp
struct PMImpl {
    shared_ptr<Image> bgImages;
    int imageCounts;
}

class Menue {
private:
    Mutex mutex;
    shared_ptr<bgImages> pImpl;
}

void Menud::changeImage (istream &imgsrc) {
    using namespace std;
    Lock m(mutex);
    shared_ptr<PMImpl> pNew(new PMImpl(*pImpl));
    pNew->bgImages.reset(imgSrc);
    ++ pNew->imageCounts;
    swap(pImpl,pNew);
}
```

### 4. 总结一下：

1. 异常安全的函数分为三类：基本型，强烈形，不抛出异常形。
2. 强烈保证往往可以以`copy and swap`实现。
3. 异常安全保证往往只用提供到其所调用的各个函数的异常安全的最低保证。

## 30. inlining 的里里外外

略

## 31. 将文件间的编译依存关系降到最低

1. 源代码：

```cpp
class Person{
public:
...
private:
std::string theName; //实现细目
Date theBirthDate; //实现细目
Address theAddress; //实现细目
};
```

但是如此却会在 Person 定义文件和其含入文件之间形成了一种编译依存关系。如果这些头文件中有任何一个被改变，或这些文件所依赖的其它头文件有任何改变。那么每个含入 Person class 的文件就得重新编译，任何使用 Person class 的文件也必须重新编译。这样的连串编译依存关系会对许多项目造成难以形容的灾难你可能会想着将实现细目分开.

2. 改进

```cpp
class Person{
public:
Person(string& name);
string name() const;
private:
shared_ptr<PersonImpl> pImpl;
};

Person::Person(string& name): pImpl(new PersonImpl(name)){}

string Person::name(){
return pImpl->name();
}
```

将实现与接口分离。