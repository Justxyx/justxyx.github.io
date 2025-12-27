---
title: Linux配置mysql并开启远程访问
author: xyx
date: 2022-7-30 20:33:00 +0800
categories: [justxyx, tools]
tags: 
math: true
---


> 每次在服务器上配置mysql开启远程服务都有问题，这次写下来下次按照这个来配置吧。

## 1. 安装mysql

```yaml
#更新apt-get库
sudo apt-get update

#安装mysql
sudo apt-get install mysql-server
```

## 2. 初始化配置

```yaml
sudo mysql_secure_installation
#有很多配置项，按照需求选择，建议
#1
VALIDATE PASSWORD PLUGIN can be used to test passwords...
Press y|Y for Yes, any other key for No: N 

#2
Please set the password for root here...
New password: 
Re-enter new password: 

#3
By default, a MySQL installation has an anonymous user,
allowing anyone to log into MySQL without having to have
a user account created for them...
Remove anonymous users? (Press y|Y for Yes, any other key for No) : N 

#4
Normally, root should only be allowed to connect from
'localhost'. This ensures that someone cannot guess at
the root password from the network...
Disallow root login remotely? (Press y|Y for Yes, any other key for No) : Y 

#5
By default, MySQL comes with a database named 'test' that
anyone can access...
Remove test database and access to it? (Press y|Y for Yes, any other key for No) : N 

#6
Reloading the privilege tables will ensure that all changes
made so far will take effect immediately.
Reload privilege tables now? (Press y|Y for Yes, any other key for No) : Y 
```

## 3. 配置远程连接

```yaml
sudo mysql -uroot -p

use mysql;

select host,user,plugin from user;

#更改root用户为全地址可连接
update user set host='%' , plugin='mysql_native_password' where user='root';

flush privileges;
```

## 4. 修改配置文件

```yaml
vim /etc/mysql/mysql.conf.d/mysqld.cnf

#更改连接地址
bind-address            = 0.0.0.0
```

## 5. 重启服务

```yaml
service mysql restart
```

连接测试
```cpp
mysql -h 192.168.0.xxx -P 3306 -u root -p
```

按道理来说这样配置就可以了 但是连接的时候如果出现密码错误 按照下面改密码

## 6. 密码更改问题

```yaml
# 报错
ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using passwor:yes)
```

1.  修改配置文件 跳过密码验证

    ```yaml
    [mysqld]
    #
    # * Basic Settings
    #
    skip-grant-tables    //  加上这一行 跳过密码验证
    user            = mysql
    pid-file        = /var/run/mysqld/mysqld.pid
    socket          = /var/run/mysqld/mysqld.sock
    port            = 3306
    basedir         = /usr
    datadir         = /var/lib/mysql
    tmpdir          = /tmp
    lc-messages-dir = /usr/share/mysql
    skip-external-locking
    ```

2. 重启mysql

3. use mysql

4. 更新密码

    `update mysql.user set authentication_string=password('123456') where user='root' ;`

5. 把跳过密码验证去掉

6. 重启mysql
