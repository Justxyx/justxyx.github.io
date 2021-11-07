---
title: java中的流详解
author: xyx
date: 2021-10-4 13:33:00 +0800
categories: [justxyx, java]
tags:
math: true
---

# 字节流 OutputStream / InputStream

**万物皆可字节流** `OutputStream`

## 1. 文件输出流

```java
            File file = new File("temp1.log");
            FileOutputStream fos = new FileOutputStream(file);
            fos.write("你好啊".getBytes());
            fos.close();
```

## 2. byte 字节详解

`byte` 的存储范围为 -128 到 127.
`byte` 数组如何存储 汉字等大于 127 的字符 ？
**_答案为 byte 数组_** 3 字节存储一个汉字字符

```java
        String str = "你好好";
      byte[] bytes = str.getBytes();
      System.out.println(bytes.length);  //9
      for (byte aByte : bytes) {
          System.out.print(aByte);   // -28,-67,-96,-27,-91,-67,-27,-91,-67,
          System.out.print(",");
      }
      ~~~
```

## 3. 文件输入流

文件输入流的两种读取方式

1. 读取每个字节

```java
        int i;
        while ((i = fileInputStream.read()) != -1){
            System.out.println(i);
        }
```

**_对于每个负数，i 都会自动转换为 byte 的补码整数，暂时我也不知道为什么要这样做 ， 也就是说， 每个 i 都为正数，当读取到-1 时， 循环跳出_**

2. 一次读取多个字节

**len 为 byte 长度**

```java
        byte[] b = new byte[2];
        int len;
        while ((len =  fileInputStream.read(b)) != -1){
            String s = new String(b);
            System.out.println(s);
        }

```

# 字符流 Reader/Writer

## 1.为什么引入字符流？

当使用字节流读取文本文件时，可能会有一个小问题。就是遇到中文字符时，可能不会显示完整的字符，那是因为
一个中文字符可能占用多个字节存储。所以 Java 提供一些字符流类，以字符为单位读写数据，专门用于处理文本文
件。

## 2. FileReader

**跟 FileOutputStream 类似，没什么好写的 贴两段代码 GG**

```java
        FileReader fr = new FileReader("temp1.log");
//        int b;
//        while ((b = fr.read()) != -1){
//            System.out.print((char) b);
//        }

        char[] c = new char[2];
        int b;

        while ((b=fr.read(c)) != -1){
            System.out.println(new String(c,0,b));
        }
    }
```

## 3.FileWriter

```java
        File file = new File("a.log");
        FileWriter fw = new FileWriter(file);
        fw.write("你好啊");
        fw.flush();
```

## flush 与 close

因为内置缓冲区的原因，如果不关闭输出流，无法写出字符到文件中。但是关闭的流对象，是无法继续写出数据
的。如果我们既想写出数据，又想继续使用流，就需要 flush 方法了。

- flush ：刷新缓冲区，流对象可以继续使用。
- close :先刷新缓冲区，然后通知系统释放资源。流对象不可以再被使用了。

# Buffer 缓冲流

较简单，直接贴代码。

```java
        FileOutputStream fos = new FileOutputStream("buffer.txt");
        BufferedOutputStream bfos = new BufferedOutputStream(fos);
        bfos.write("你好啊".getBytes());
        bfos.flush();

        FileInputStream fis = new FileInputStream("buffer.txt");
        BufferedInputStream bfis = new BufferedInputStream(fis);

        int b;
        byte[] c = new byte[2];
        while ( (b = bfis.read(c)) != -1){
            System.out.println(new String(c));
        }

```

# 序列化

## 1. 序列化对象

```java
        User user = new User("xx ", "xxx", 13);

        FileOutputStream fos = new FileOutputStream("user.txt");
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(fos);
        objectOutputStream.writeObject(user);
        objectOutputStream.close();
        fos.close();
```

## 2. 反序列化对象

```java
        FileInputStream fis = new FileInputStream("user.txt");
        ObjectInputStream objectInputStream = new ObjectInputStream(fis);
        User o = (User) objectInputStream.readObject();
        System.out.println(o);
```

# 总结

- 万物皆可字节流
  `OutputStream` :顶层父类
  `InputStrea` ： 顶层父类

- 字符流
  `Writer` : 顶层父类
  `Reader` ； 顶层父类

- 缓冲流
  **可包装字符流，也可以包装字节流**

包装字节流

```java
        FileOutputStream fos = new FileOutputStream("buffer.txt");
        BufferedOutputStream bfos = new BufferedOutputStream(fos);
```

- 序列化与反序列化对象

```java
        FileOutputStream fos = new FileOutputStream("user.txt");
        ObjectOutputStream objectOutputStream = new ObjectOutputStream(fos);
```
