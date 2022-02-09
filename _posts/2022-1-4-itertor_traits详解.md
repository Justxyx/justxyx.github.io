---
title: itertor_traits详解
author: xyx
date: 2022-1-04 20:33:00 +0800
categories: [C++, cpp-base]
tags: 
math: true
---

## 1. 算法如何知道迭代器数据类型？

~~~c
typedef bidirectional_iterator_tag iteraotr_category;
typedef T value_type;
typedef Ptr pointer;
typedef Ref reference;
typedef ptrdiff_t defference_type;
~~~

很简单 直接点即可

~~~c

algorithm(I first,T last){
    I::pointer  
}
~~~

## 问题2 那要是传入的是指针而不是class呢？

1.
~~~c

algorithm(I first,T last){
    typename iterator_traits<T>::value_type vaue_type;
}
~~~

2. 
~~~c
template<class T>
struct iterator_traits{
    typename iterator_traits<T>::value_type vaue_type;
}
~~~

3. 针对指针特化
~~~c
template<class T>
struct iterator_traits<T*>{
    typename T vaue_type;
}
~~~

4. 针对const 特化
~~~c
template<class T>
struct iterator_traits<const T*>{
    typename T vaue_type;    //  不可返回const T  变量无法赋值
}
~~~