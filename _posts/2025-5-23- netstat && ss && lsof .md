---
title:  netstat && ss && lsof
author: xyx
date: 2025-5-23 13:33:00 +0800
categories: [justxyx, kernel]
tags:
math: true
---

## 1. 本地回环解析

| 地址         | 类型            | 可访问范围               | 典型用途                     |
|--------------|-----------------|--------------------------|-----------------------------|
| `127.0.0.1`  | IPv4 回环地址    | 仅本机                   | 本地开发、测试、数据库        |
| `localhost`  | 主机名   /etc/hosts 中有写       | 默认同 `127.0.0.1`        | 方便人类使用的回环地址别名     |
| `0.0.0.0`    | 通配地址 ：表示 ​​监听所有可用的网络接口​​（包括 127.0.0.1、物理网卡 IP、Docker 虚拟网卡等）。       | 所有网络接口（包括外部）   | 生产环境服务（如 Nginx、MySQL） |

## 2. netstat ss lsof 解析

```c
// nginx 进程
xm@hcss-ecs-4208:~$ ps -aux|grep nginx
root     21062  0.0  0.1  34316  2944 ?        Ss   May16   0:00 nginx: master process nginx
nobody   30756  0.0  0.2  39428  4196 ?        S    May19   0:00 nginx: worker process
```

### netstat

```shell
netstat -tulnp    # 查看监听端口（TCP/UDP）
netstat -anp      # 查看所有连接（包括 PID）
netstat -s        # 显示网络统计信息
```

```shell
xm@hcss-ecs-4208:~$ sudo netstat -tulnp
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:8080            0.0.0.0:*               LISTEN      21062/nginx: master 
```

### lsof

- 列出 ​​所有打开的文件​​（包括普通文件、目录、套接字、管道等）。
- 不仅限于网络，还能查看文件描述符（FD）泄漏问题。


```shell
lsof -i :80       # 查看占用 80 端口的进程
lsof -p 1234      # 查看 PID=1234 的进程打开的文件
lsof -u root      # 查看 root 用户打开的文件
lsof /var/log/syslog  # 查看谁在读写某个文件
```

```shell
xm@hcss-ecs-4208:~$ sudo lsof -i :8080
COMMAND   PID   USER   FD   TYPE   DEVICE SIZE/OFF NODE NAME
nginx   21062   root    6u  IPv4 22034413      0t0  TCP *:http-alt (LISTEN)  // master 进程
nginx   30756 nobody    6u  IPv4 22034413      0t0  TCP *:http-alt (LISTEN)  // worker 进程
nginx   30756 nobody    3u  IPv4 23323928      0t0  TCP hcss-ecs-4208:http-alt->111.46.57.97:54220 (CLOSE_WAIT)
nginx   30756 nobody    4u  IPv4 23324070      0t0  TCP hcss-ecs-4208:http-alt->111.46.57.97:54282 (ESTABLISHED)
```

### ss



```shell
ss -tulnp         # 查看监听端口（类似 netstat -tulnp）
ss -anp           # 查看所有连接（包括 PID）
ss -s             # 显示简要统计信息
ss -o state established '( dport = :80 or sport = :80 )'  # 过滤特定状态的连接
```

```shell
xm@hcss-ecs-4208:~$ sudo ss -tulnp
Netid       State         Recv-Q        Send-Q                Local Address:Port                 Peer                            
tcp         LISTEN        0             511                         0.0.0.0:8080                      0.0.0.0:*            users:(("nginx",pid=30756,fd=6),("nginx",pid=21062,fd=6))  
```


1. 为什么 ss 能显示 Worker 进程，而 netstat 不能？​
    ss（Socket Statistics）直接从内核获取套接字信息，能更精确地关联到所有持有套接字的进程（包括继承的 Worker 进程）。
    netstat 依赖 /proc/net 文件，默认只显示监听套接字的原始进程（Master），不主动追踪派生进程（Worker）。

2. ss 专用于查看 ​​套接字（socket）​​ 信息，是 netstat 的现代替代品。

3. **ss（Socket Statistics）默认会合并相同进程的 ​​IPv4 和 IPv6 监听套接字​​，优先显示 IPv6 信息（若存在双栈绑定）。**

    ```shell
    # 强制显示所有地址族（包括IPv4）
    ss -tulnp -f inet
    
    # 或同时显示IPv4和IPv6
    ss -tulnp -f inet -f inet6
    ```





    