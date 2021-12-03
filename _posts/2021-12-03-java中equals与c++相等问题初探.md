---
title: java中equals与c++相等问题初探
author: xyx
date: 2021-12-03 13:33:00 +0800
categories: [C++, cpp-base]
tags:
math: true
---


## java判等问题

~~~java
public class User {
    private int age;
    private String name;

    public User(int age, String name) {
        this.age = age;
        this.name = name;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return age == user.age && Objects.equals(name, user.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(age, name);
    }
}
~~~



```java
 public class test {
    public static void main(String[] args) {
        User u1 = new User(12,"xx");
        User u2 = new User(12,"xx");
        System.out.println(u1 == u2);   // == 只判断内存地址是否相同
        System.out.println(u1.hashCode());  // 5173
        System.out.println(u2.hashCode());   // 5173
        System.out.println(u1.equals(u2));  // equals 判断值是否相同
    }
}
```

- == 问题
java中`==` 只判断两对象地址是否相同。

- equals
重写equals方法，逐一对比成员属性，相等就判true。

- hashcode
既然有了equals方法，为什么还要hashcode方法？
慢！ 逐一对比的equals方法，很慢。直接用hashcode对比散列值，快的一匹。但是注意，***equals 对等的两个对象，hashcode值一定相等，但是hashcode相等的不一定equals**
所以在比较对象时，一般先比较hashcode ，再判等，提高效率。


## C++ 判等问题

C++ 由于有取址符，所以较好比较同一对象是否相等。

判断两个对象是否相等，重载运算符即可。

```c
bool operator==(const User &u1,const User &u2){
    return (u1.age == u2.age) && (u1.name == u2.name);
}
```