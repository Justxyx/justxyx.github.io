---
title: pytorch+cuda环境配置
author: xyx
date: 2021-5-7 20:33:00 +0800
categories: [justxyx, deep-learning]
tags: 
math: true

---


### 第一个问题 
- 问：conda安装的cudatoolkit, cudnn与在主机上安装的cuda, cudnn有何关系？
- 答： anaconda 的 cudatoolkit 不包含完整安装cuda的全部文件，只是包含了用于 tensorflow，pytorch，xgboost 和 Cupy 等所需要的共享库文件。一般情况下会直接调用anaconda的cudatoolkit工具包。
**简单来说， 就是会先找conda虚拟环境里面的 cuda 配置** 

### 第二个问题 
 看浙大罗博士的Rid网课， 因为是18年网课，配置python2.7 加 pytorch。  用conda 一直装不上 。  看了一下conda 默认下载源里面基本没有python2.7 的内容了。 只能试着装python 3.7 的跑一跑。 希望不会有向下兼容的版本问题。

 ### 第三个问题 win10 怎么像linux 一样查看先看运行情况
 ~~~java
 C:\Windows\System32\cmd.exe -> cmd 

 nvidia-smi
~~~