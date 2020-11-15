---
title: tensorflow2.0+keras环境配置
author: xyx
date: 2020-11-11 20:19:00 +0800
categories: [justxyx, deep-learning]
tags: 
math: true

---
## Anaconda 的下载与配置
- 下载 
  略
- 环境变量的配置
  环境变量–>点到系统变量中的Path–>编辑
  增加两个，如下图所示，选择自己的安装路径。
  <img src="/assets/img/dee"></img>
  <img src="assets/img/deep-learning/tensorflow2.0+keras环境配置/a1.png">

## tensorflow2.0与keras安装

- 创建自己的TensorFlow环境
  1. conda info --envs # 查有几个可用环境，此处显示有6个环境，在D:\Anaconda3\envs目录下
  2. conda create -n tf2.0 python=3.6 # 创建新环境，tf2.0是创的新环境名字，-n为name缩写
  3. conda activate tf2.0 # 激活你新创建的环境，base就会变成tf2.0

- 安装TensorFlow环境
  1. pip install tensorflow==2.0 -i https://pypi.douban.com/simple #从国内网站下载快
  2. pip install matplotlib notebook keras sklearn -i https://pypi.douban.com/simple #安装开发中常用库，-i表示用指定网址（这里一起安装，包括安装keras，但此处会默认给你安装最新版本，会出现版本错误，只需用下面命令降低版本即可
  3.  pip install keras==2.3.1 #降低成2.3.1版本

- 测试
    python
    import tensorflow as tf
    import keras


  