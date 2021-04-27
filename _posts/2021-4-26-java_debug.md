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

### 2021.4.26

- 问题描述 
  根据b站整合SSM三大框架， 代码完全一下，但就是运行报错同时Tomcat运行不起来。 后来查了一下， 首先是target 输出目录下，配置文件读入都爆红，特别是数据库配置文件读取直接报错显示不能解析文件。 这就很奇怪。

- 问题解析
  自己偷懒，直接复制文档配置文件，虽然路径什么都是一样，但是idea解析这些配置文件还是会有bug。 在文件编辑区没有问题，但是在target输出目录下一看就会发现爆红错误。

- 解决方案
  idea -> setting 
  <img src="/assets/img/2021.4.26/1619413461.jpg">
  
  清理缓存重启即可。

### 2021.4.27
- 问题描述

  整合SSM框架， tomcat 服务器成功启动， 8080 端口访问默认 index.jsp 页面报错404. WEB-INF  下的所有资源都访问不了。
- 问题原因
  Project Structure 里面， Facets 目录下爆红 。 Web Resource 目录爆红，不能识别。 WEB-INF 文件夹都没有亮起来。
- 解决方案 
  重新配置路径即可。
  <img src="/assets/img/2021.4.26/UID1(5G}CDL1E9W]DJY~GI9.png">
  

