---
title: Mysql的时间类型与java的插入删除
author: xyx
date: 2021-8-31 13:33:00 +0800
categories: [justxyx, java]
tags:
math: true
---

## 项目背景

人脸识别项目，希望对每个识别结果存储到数据库中，供查询展示。这就必然涉及到了 Mysql 数据库中的时间戳。关于 Mysql 中的时间类型字段，刚开始上面给出的方案是直接存储一个 long 的毫秒值，这就意味着无法在 sql 查询中使用到内置的时间函数，对以后的条件查询带来很大的麻烦。所以，还是切用 Mysql 内置的时间类型字段。

`顺便说一句，很简单的一个java字段与Mysql数据库字段的对应，百度出来的那些文档我真是服了，你抄我我抄你，还TM不能用`

---

- DATE
  只有日期部分，没有时间部分，不考虑。

- TIMESTAMP
  2038 年到头，不考虑。
  不过多说一句，TIMESTAMP 在 Java.sql 中有对应的字段可以直接封装。
  下面提到的 DATETIME 也是用的 TIMESTAMP 封装的。

- DATETIME
  有日期部分，也有时间部分，不过对应的方法大多数已经过期了，只能用 getTime（）方法转为毫秒值在用 Date（）函数格式化操作。

## 测试步骤

### 1. 数据库建表，datetime 字段

```sql
CREATE TABLE `timetest` (
`time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8
```

### 2. Mybatis 查询时间

Mysql datetime 字段 对应 java 中 Timestamp 字段

```java
		List<TestTime> testTimes = timeTestMapper.find();
		Timestamp times = testTimes.get(0).getTimes();
		long time = times.getTime();
		SimpleDateFormat sdf = new SimpleDateFormat("yy-MM-dd HH:mm:ss");
		String format = sdf.format(times);
		System.out.println(format);
```

### 3. Mybatis 添加当前时间到数据库

```java
		long l = System.currentTimeMillis();
		Timestamp timestamp = new Timestamp(l);
		timeTestMapper.add(timestamp);
```


## 时区问题
在数据库连接的时候在意过时区问题，可是后来查询还是有6小时时差。。。

改成过后的url ：
  `url: jdbc:mysql://192.xxx.1.4:3306/face_system?&serverTimezone=Asia/Shanghai&`
