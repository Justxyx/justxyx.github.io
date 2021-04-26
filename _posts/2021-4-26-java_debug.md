---
title: java_debug
author: xyx
date: 2021-4-26 20:33:00 +0800
categories: [justxyx, java]
tags: 
math: true

---

记录一下学习过程中的bug，做好记录。

## SSM框架

### 2021.4.6

- 问题描述 
  根据b站整合SSM三大框架， 代码完全一下，但就是运行报错同时Tomcat运行不起来。 后来查了一下， 首先是target 输出目录下，配置文件读入都爆红，特别是数据库配置文件读取直接报错显示不能解析文件。 这就很奇怪。

- 问题解析
  自己偷懒，直接复制文档配置文件，虽然路径什么都是一样，但是idea解析这些配置文件还是会有bug。 在文件编辑区没有问题，但是在target输出目录下一看就会发现爆红错误。

- 解决方案
  idea -> setting 
  <img src="/justxyx.github.io/assets/img/2021.4.26/1619413461.jpg">
  
  清理缓存重启即可。
