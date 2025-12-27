---
title: unp&chapter7 套接字选项
author: xyx
date: 2025-12-08 13:33:00 +0800
categories: [justxyx, net-programming]
tags:
math: true
---

## 7.2 getsockopt 和setsockopt 函数

### 1. 函数原型

```c
// 设置套接字选项
int setsockopt(int sockfd, int level, int optname,
               const void *optval, socklen_t optlen);

// 获取套接字选项
int getsockopt(int sockfd, int level, int optname,
               void *optval, socklen_t *optlen);
```

#### 参数说明

| 参数 | 含义 |
|------|------|
| `sockfd` | 套接字描述符 |
| `level` | 选项层级，如 `SOL_SOCKET`, `IPPROTO_TCP`, `IPPROTO_IP` |
| `optname` | 选项名称，如 `SO_REUSEADDR`, `TCP_NODELAY` 等 |
| `optval` | 指向存放/设置选项值的缓冲区 |
| `optlen` | 选项值长度（输入长度或输出长度） |

---

### 2. 常用选项示例

#### 2.1 套接字级（SOL_SOCKET）

| optname        | optval 类型          | 功能说明 |
|----------------|----------------------|----------|
| SO_REUSEADDR   | int (bool)           | 允许重用本地地址/端口（TIME_WAIT 时也能 bind） |
| SO_REUSEPORT   | int (bool)           | 多 socket 绑定同一 IP:port，提升并发 accept 性能（Linux 3.9+） |
| SO_KEEPALIVE   | int (bool)           | 启用 TCP keepalive 心跳机制 |
| SO_LINGER      | struct linger        | close() 时等待/丢弃未发送数据行为控制 |
| SO_BROADCAST   | int (bool)           | UDP socket 允许发送广播报文 |
| SO_DEBUG       | int (bool)           | 启用调试（几乎不用） |
| SO_DONTROUTE   | int (bool)           | 不经过路由，直发数据（rare） |
| SO_OOBINLINE   | int (bool)           | 将 OOB（urgent）数据放入普通数据流中 |
| SO_RCVBUF      | int                  | 设置接收缓冲区大小 |
| SO_SNDBUF      | int                  | 设置发送缓冲区大小 |
| SO_RCVLOWAT    | int                  | 接收低水位，影响可读条件 |
| SO_SNDLOWAT    | int                  | 发送低水位，影响可写条件 |
| SO_RCVTIMEO    | struct timeval       | recv 超时（阻塞超时退出） |
| SO_SNDTIMEO    | struct timeval       | send 超时 |
| SO_ERROR       | int (getsockopt)     | 获取 pending 错误并清除 |
| SO_TYPE        | int (getsockopt)     | 获取 socket 类型（STREAM/DGRAM 等） |
| SO_ACCEPTCONN  | int (getsockopt)     | 是否在 listen 状态（只读） |


#### 2.2 TCP 层（IPPROTO_TCP）

| optname         | 类型             | 功能说明 |
|-----------------|------------------|----------|
| TCP_NODELAY     | int (bool)       | 禁用 Nagle，小包立即发送 |
| TCP_CORK        | int (bool)       | 延迟发送，等待更多数据合并包 |
| TCP_MAXSEG      | int              | 设置 MSS |
| TCP_QUICKACK    | int (bool)       | 启用快速 ACK |
| TCP_DEFER_ACCEPT| int (秒)         | accept 前等待对端发送数据 |
| TCP_INFO        | struct tcp_info  | 获取 TCP 状态统计（只读） |
| TCP_KEEPIDLE    | int (秒)         | keepalive 发起之前的空闲时间 |
| TCP_KEEPINTVL   | int (秒)         | 每次 keepalive 之间的间隔 |
| TCP_KEEPCNT     | int              | keepalive 重试次数 |
| TCP_LINGER2     | int (秒)         | orphan socket 在 FIN_WAIT2 的寿命 |
| TCP_WINDOW_CLAMP| int              | 限制通告窗口大小 |


#### 2.3 IP 层（IPPROTO_IP）

| optname                    | 类型                 | 功能说明 |
|----------------------------|----------------------|----------|
| IP_TTL                     | int                  | 设置 IPv4 TTL |
| IP_TOS                     | int                  | 设置 IPv4 TOS/DSCP 优先级 |
| IP_HDRINCL                 | int (bool)           | raw socket 表示含 IP 头 |
| IP_OPTIONS                 | 二进制               | 设置 IPv4 options（基本废弃） |
| IP_MULTICAST_IF            | struct in_addr       | 指定多播发送接口 |
| IP_MULTICAST_TTL           | u_char               | 多播 TTL 跳数限制 |
| IP_MULTICAST_LOOP          | u_char               | 本机是否接收自己发的多播包 |
| IP_ADD_MEMBERSHIP          | struct ip_mreq       | 加入多播组 |
| IP_DROP_MEMBERSHIP         | struct ip_mreq       | 离开多播组 |
| IP_BLOCK_SOURCE            | struct ip_mreq_source| 阻塞特定源地址的多播 |
| IP_UNBLOCK_SOURCE          | struct ip_mreq_source| 解除阻塞多播源 |
| IP_ADD_SOURCE_MEMBERSHIP   | struct ip_mreq_source| 加入 SSM 源特定多播 |
| IP_DROP_SOURCE_MEMBERSHIP  | struct ip_mreq_source| 离开 SSM 源特定多播 |
| IP_PKTINFO（Linux）        | struct in_pktinfo    | 接收时获取目标 IP 和入接口信息 |

#### 2.4 IPv6 层选项


| optname               | 类型                       | 功能说明 |
|-----------------------|----------------------------|----------|
| IPV6_V6ONLY           | int (bool)                 | 是否只接受 IPv6，不接受 IPv4-mapped |
| IPV6_MULTICAST_IF     | unsigned int（接口索引）   | 多播发送接口 |
| IPV6_MULTICAST_HOPS   | int                        | 多播 hop limit |
| IPV6_MULTICAST_LOOP   | int (bool)                 | 是否本机 loop back 多播包 |
| IPV6_JOIN_GROUP       | struct ipv6_mreq           | 加入 IPv6 多播组 |
| IPV6_LEAVE_GROUP      | struct ipv6_mreq           | 离开 IPv6 多播组 |
| IPV6_RECVPKTINFO      | int (bool)                 | 获取目的地址和入接口信息 |
| IPV6_RECVHOPLIMIT     | int (bool)                 | 获取 IPv6 hop limit |
| IPV6_RECVHOPOPTS      | int (bool)                 | 获取 hop-by-hop 选项 |
| IPV6_RECVRTHDR        | int (bool)                 | 获取路由头 |
| IPV6_RECVDSTOPTS      | int (bool)                 | 获取目的选项 |
| IPV6_RECVPATHMTU      | int (bool)                 | PMTU 信息 |
| IPV6_PATHMTU          | struct ip6_mtuinfo         | 查询 PMTU |

---

### 3. 使用示例

```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <unistd.h>

int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return -1;
    }

    // 设置 TCP_NODELAY
    int flag = 1;
    setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));

    // 获取发送缓冲区大小
    int sndbuf;
    socklen_t len = sizeof(sndbuf);
    getsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &sndbuf, &len);
    printf("send buffer size: %d\n", sndbuf);

    close(sockfd);
    return 0;
}
```

---

### 4. 注意事项

1. **选项生效粒度**  
   - 大部分套接字选项仅对指定套接字有效，不影响系统全局。
   - 某些全局 TCP 参数（如 `tcp_window_scaling`）无法通过套接字直接覆盖。

2. **数据类型匹配**  
   - 必须与选项对应，如 `int`, `struct linger`, `struct timeval`。

3. **调用顺序**  
   - 必须在 `socket()` 之后使用，某些选项最好在 `bind()` 或 `connect()` 前设置。

---

### 5. 总结

- **`setsockopt()`** → 设置单个套接字的行为  
- **`getsockopt()`** → 查询单个套接字的参数  
- **作用范围** → 单个 socket（全局内核参数除外）  
- **常用场景** → 调整缓冲区、关闭 Nagle、保持活跃连接、延迟关闭等  

## 7.3 检查选项是否受支持并获取默认值

示例:

```c
#include "unp.h"

union val {
    int				    i_val;
    long				l_val;
    struct linger		linger_val;
    struct timeval	    timeval_val;
} val;

struct sock_opts {
    const char *opt_str;
    int opt_level;
    int opt_name;
    char *(*opt_val_str)(union val*, int);
};

static char	*sock_str_flag(union val *, int);
static char	*sock_str_int(union val *, int);
static char	*sock_str_linger(union val *, int);
static char	*sock_str_timeval(union val *, int);

static struct sock_opts sockOpts[] = {
{ "SO_BROADCAST",		SOL_SOCKET,	SO_BROADCAST,	sock_str_flag },
{ "SO_DEBUG",			SOL_SOCKET,	SO_DEBUG,		sock_str_flag },
{ "SO_DONTROUTE",		SOL_SOCKET,	SO_DONTROUTE,	sock_str_flag },
{ "SO_ERROR",			SOL_SOCKET,	SO_ERROR,		sock_str_int },
{ "SO_KEEPALIVE",		SOL_SOCKET,	SO_KEEPALIVE,	sock_str_flag },
{ "SO_LINGER",			SOL_SOCKET,	SO_LINGER,		sock_str_linger },
{ "SO_OOBINLINE",		SOL_SOCKET,	SO_OOBINLINE,	sock_str_flag },
{ "SO_RCVBUF",			SOL_SOCKET,	SO_RCVBUF,		sock_str_int },
{ "SO_SNDBUF",			SOL_SOCKET,	SO_SNDBUF,		sock_str_int },
{ "SO_RCVLOWAT",		SOL_SOCKET,	SO_RCVLOWAT,	sock_str_int },
{ "SO_SNDLOWAT",		SOL_SOCKET,	SO_SNDLOWAT,	sock_str_int },
{ "SO_RCVTIMEO",		SOL_SOCKET,	SO_RCVTIMEO,	sock_str_timeval },
{ "SO_SNDTIMEO",		SOL_SOCKET,	SO_SNDTIMEO,	sock_str_timeval },
{ "SO_REUSEADDR",		SOL_SOCKET,	SO_REUSEADDR,	sock_str_flag }
};

int main(int argc, char **argv) {
    int fd;
    socklen_t len;
    struct sock_opts *ptr;

    for (ptr = sockOpts; ptr->opt_str != NULL; ++ptr) {
        printf("%s: \n", ptr->opt_str);
        if (ptr->opt_val_str == NULL)
            printf("undefined\n");
        else {
            switch (ptr->opt_level) {
                case SOL_SOCKET:
                case IPPROTO_IP:
                case IPPROTO_TCP:
                    fd = Socket(AF_INET, SOCK_STREAM, 0);
                    break;
                case IPPROTO_SCTP:
                    fd = Socket(AF_INET, SOCK_SEQPACKET, IPPROTO_SCTP);
                default:
                    err_quit("Can't create fd for level %d\n", ptr->opt_level);
            }

            len = sizeof(val);
            if (getsockopt(fd, ptr->opt_level, ptr->opt_name, &val, &len) == -1) {
                err_ret("get sockopt error\n");
            } else {
                printf("default = %s \n", (*ptr->opt_val_str)(&val, len));
            }

            close(fd);
        }
    }
    exit(0);
}

static char	strres[128];

static char	*
sock_str_flag(union val *ptr, int len)
{
    if (len != sizeof(int))
        snprintf(strres, sizeof(strres), "size (%d) not sizeof(int)", len);
    else
        snprintf(strres, sizeof(strres),
                 "%s", (ptr->i_val == 0) ? "off" : "on");
    return(strres);
}

static char	*
sock_str_int(union val *ptr, int len)
{
    if (len != sizeof(int))
        snprintf(strres, sizeof(strres), "size (%d) not sizeof(int)", len);
    else
        snprintf(strres, sizeof(strres), "%d", ptr->i_val);
    return(strres);
}

static char	*
sock_str_linger(union val *ptr, int len)
{
    struct linger	*lptr = &ptr->linger_val;

    if (len != sizeof(struct linger))
        snprintf(strres, sizeof(strres),
                 "size (%d) not sizeof(struct linger)", len);
    else
        snprintf(strres, sizeof(strres), "l_onoff = %d, l_linger = %d",
                 lptr->l_onoff, lptr->l_linger);
    return(strres);
}

static char	*
sock_str_timeval(union val *ptr, int len)
{
    struct timeval	*tvptr = &ptr->timeval_val;

    if (len != sizeof(struct timeval))
        snprintf(strres, sizeof(strres),
                 "size (%d) not sizeof(struct timeval)", len);
    else
        snprintf(strres, sizeof(strres), "%ld sec, %ld usec",
                 tvptr->tv_sec, tvptr->tv_usec);
    return(strres);
}
```

几点说明：
1. union 说明  
`union` 的所有成员共享同一块内存，大小等于最大成员大小；写入任意成员都会覆盖同一片存储，只能按对应类型读取。用于 socket 时可统一容纳不同 sockopt 返回类型（int、struct linger、struct timeval 等）。

2. sizeof 用法差异  
`getsockopt()` 的 `optval` 是输出缓冲，用户提供的是“最大可写空间”，因此可用 `sizeof(union)`，内核写入实际数据并更新 `optlen`；`setsockopt()` 的 `optval` 是输入数据，必须用实际成员大小 `sizeof(member)`，让内核准确读取参数，不能用 `sizeof(union)`。

3. `union` 的大小 = 最大成员大小（含对齐），无论写哪个成员、写了什么值，大小都不变。

## 7.5　通用套接字选项

#### 7.5.5　SO_KEEPALIVE 套接字选项

    SO_KEEPALIVE 打开保活机制，具体探测时间默认由 sysctl 决定；如果要自定义时间，需要使用 TCP_KEEPIDLE 等 per-socket 选项覆盖默认配置。

```c
// linux 系统tcp 保活机制
root>sysctl -a | grep tcp_keepalive
net.ipv4.tcp_keepalive_intvl = 75
net.ipv4.tcp_keepalive_probes = 9
net.ipv4.tcp_keepalive_time = 7200

// socket fd 配置保活机制
    /* 打开 TCP keepalive 功能 */
    if (setsockopt(sockfd, SOL_SOCKET, SO_KEEPALIVE,
                   &yes, sizeof(yes)) < 0) {
        perror("setsockopt SO_KEEPALIVE");
        return 1;
    }
```

#### 7.5.6　SO_LINGER 套接字选项

示例：
```c
int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    struct linger ling;

    /*
     1) 默认行为（不设置 SO_LINGER）or l_onoff = 0（默认行为）
        - close() 立即返回
        - 内核后台继续发送缓冲区数据
        - 正常 FIN 关闭
        - 内核会等发送缓冲区的数据发完，再发 FIN。
    */
    // close(sockfd);

    /*
    2) l_onoff = 1, l_linger = 0
        - close() 立即返回
        - 丢弃发送缓冲区数据
        - 直接发送 RST 强制关闭连接
    */
    ling.l_onoff  = 1;
    ling.l_linger = 0;
    setsockopt(sockfd, SOL_SOCKET, SO_LINGER,
            &ling, sizeof(ling));
    // close(sockfd);

    /*
    3) l_onoff = 1, l_linger > 0
        - close() 阻塞最多 l_linger 秒
        - 等待数据发送并收到对端 ACK
        - 发送 FIN 并收到对端 ACK 后 close() 才返回
        - 若超时未完成上述确认 → 发送 RST 强制关闭
    */
    ling.l_onoff  = 1;
    ling.l_linger = 5;
    setsockopt(sockfd, SOL_SOCKET, SO_LINGER,
            &ling, sizeof(ling));
    close(sockfd);

    return 0;
    }

```

1. 这里有一个基本原则：设置SO_LINGER 套接字选项后，close 的成功返回只是告诉我们先前发送的数据（和FIN）已由对端TCP确认，而不能告诉我们对端应用进程是否已读取数据。如果不设置该套接字选项，那么我们连对端TCP是否确认了数据都不知道。
2. 让客户知道服务器已读取其数据的一个方法是改为调用shutdown （并设置它的第二个参数为SHUT_WR ）而不是调用close ，并等待对端close 连接的当地端（服务器端）
3. 获知对端应用进程已读取我们的数据的另外一个方法是使用应用级确认 （application-level acknowledge，简称应用ACK （application ACK））

| 调用方式                                | 本端发送行为                 | 本端接收行为        | TCP状态变化                    | 典型用途与效果                                      |
|-----------------------------------------|------------------------------|---------------------|---------------------------------|-----------------------------------------------------|
| shutdown(fd, SHUT_RD)                   | 不发送任何 FIN               | 停止接收数据        | 不进入 Close 流程              | 忽略对端数据，仅继续发送数据                        |
| shutdown(fd, SHUT_WR)                   | 发送 FIN（半关闭写方向）     | 继续接收数据        | 进入 FIN_WAIT_1 -> FIN_WAIT_2  | 常用于让对端知道数据发送完毕，等待对端返回/关闭     |
| close()（默认 SO_LINGER）               | 如果无数据立即发送 FIN       | 不再接收数据        | 正常关闭四次挥手                | 常规关闭方式，内核确保发送缓冲数据后关闭            |
| close() + SO_LINGER(1,0)                | 直接发送 RST（不走挥手）     | 不再接收数据        | 直接复位连接                   | 强制关闭，丢弃未发送数据，对端收到 ECONNRESET       |
| close() + SO_LINGER(1,>0)               | 阻塞等待最多 linger 秒发送FIN | 不再接收数据        | 阻塞关闭直到超时或完成挥手      | 确保数据可靠发送完成，否则超时失败返回               |


#### 7.5.8　SO_RCVBUF 和SO_SNDBUF 套接字选项


##### 1. 定义与作用
SO_RCVBUF：TCP 接收缓冲区大小（内核存放对端发来的数据）  
SO_SNDBBUF：TCP 发送缓冲区大小（内核缓存待发送的数据）  
它们决定 TCP 滑动窗口上限，影响吞吐、拥塞控制、延迟及应用是否阻塞。  
核心：不是用户态 buffer，而是 TCP 协议栈的内核缓冲区。

##### 2. 大小调整原则（重要）
设置值 ≠ 实际生效值。  
SO_SNDBUF：设置值会翻倍（TCP headroom + 内核策略）  
SO_RCVBUF：设置值近似使用，但仍受系统最大限制  
getsockopt() 返回值才是实际值  
示例：setsockopt(8KB) → 实际可能为 16KB。

##### 3. 自动调整机制
现代 Linux 启用 TCP 自动调优（auto tuning），根据 RTT、带宽、拥塞动态调整 buffer。  
多数情况下无需手动设置。  
高性能网络中固定 buffer 会限制自动调优能力，降低吞吐。

##### 4. 影响点
吞吐量：buffer 越大 → 窗口越大 → 吞吐越高（特别是 BDP 网络）。  
阻塞行为：send() 是否阻塞看 sndbuf 是否满；recv() 是否阻塞看 rcvbuf 是否空。  
内存占用：每个连接都有独立的 send/recv buffer。

##### 5. 注意事项
系统最大值限制：
/proc/sys/net/core/rmem_max  
/proc/sys/net/core/wmem_max  
超过最大值会被内核截断。  
SO_SNDBUF 会影响通告窗口，决定对端发送速度。  
TCP_NODELAY 不改变 buffer，只影响 Nagle。  
UDP buffer 满会直接丢包。

##### 6. 正确理解 send()
误区：send() 成功代表数据发到网络。  
实际：send() → 写入发送缓冲 → 内核异步发送。  
小 sndbuf：send() 阻塞或返回 EAGAIN。  
send() 成功仅代表写入 sndbuf，不代表对端收到。

##### 7. 正确理解 recv()
数据从网络进 rcvbuf，再由 recv() 取出。  
大 RCVBUF 能更好抗抖动，支持批量读取。  
只要数据在 rcvbuf 中，应用慢不会丢数据（TCP）。

##### 8. 实战建议
普通服务器：不设置，使用自动调优：
net.ipv4.tcp_rmem  
net.ipv4.tcp_wmem  
高 BDP 网络：需要手动设置 SO_SNDBUF + SO_RCVBUF：
BDP ≈ 带宽 * RTT  
示例：1Gbps * 50ms ≈ 6.25MB buffer。

##### 9. 常见误区
send() 成功不等于对端收到。  
buffer 大小不是应用 buffer。  
实际值不等于设置值（send buffer 会翻倍）。  
Windows/Linux 行为不同。  
常规网络不建议手动设置。

##### 10. 面试金句
SO_SNDBUF 和 SO_RCVBUF 控制 TCP 内核缓冲大小，决定滑动窗口上限，从而影响吞吐和阻塞行为。  
现代 Linux 支持自动调优，除非高 BDP 网络，否则不建议手动设置。  
实际生效值不同于设置值，SNDBUF 会翻倍并受内核限制。  
send() 写入内核缓冲，不代表发到网络。

#### 7.5.9　SO_RCVLOWAT 和SO_SNDLOWAT 套接字选项

**书中**：
接收低水位标记是让select 返回“可读”时套接字接收缓冲区中所需的数据量。对于TCP、UDP和SCTP套接字，其默认值为1。发送低水位标记是让select 返回“可写”时套接字发送缓冲区中所需的可用空间。对于TCP套接字，其默认值通常为2048

**实际**：
SO_RCVLOWAT 和 SO_SNDLOWAT 最初的设计目的，是控制 select() 或 poll() 对套接字“可读/可写”事件的触发条件。SO_RCVLOWAT 决定接收缓冲区中至少要有多少数据才认为“可读”，缺省为 1 字节；SO_SNDLOWAT 决定发送缓冲区中至少要有多少可用空间才认为“可写”，历史上 BSD/POSIX 对 TCP 的默认值约为 2048 字节，UDP/SCTP 为 1 字节。它们只影响内核在 I/O 多路复用中的 wakeup 时机，不影响 TCP 协议语义，也不会改变数据可靠性、窗口大小、吞吐能力等核心行为。简而言之：低水位标记是“事件触发阈值”，不是网络缓冲区大小参数。

在现代 Linux（2.4/2.6 以后）中，SO_SNDLOWAT 实际被固定为 1 字节，用户设置会被忽略或返回错误，因此 TCP 的“可写”事件触发条件始终是“只要有任意可用发送空间”，历史默认 2048 的逻辑只存在于书籍和早期 BSD 系统。SO_RCVLOWAT 在 Linux 中仍然有效，可以用于一些固定协议长度、避免频繁 wakeup 的场景（例如等一个完整消息再通知读），但常规网络应用通常不需要设置，现代 I/O 模型普遍使用非阻塞套接字 + 自己的读写缓冲策略，实现精细读写控制。综合来看，低水位标记属于传统 select 时代的调优技术，对网络行为影响有限，本质是事件触发阈值控制；在 Linux 上，不要依赖 SO_SNDLOWAT，只有 SO_RCVLOWAT 在特定协议中仍有价值。

不用 I/O 复用时，直接 `while (...) Writen(sockfd, buf, len)` 属于阻塞写模型，数据并不是直接发到网络，而是写入内核发送缓冲区，由 TCP 异步发送；这种写法依赖 TCP 的流量控制，缓冲区未满时 `write()` 会立即返回，一旦缓冲区被网络速度或对端读取速度拖慢而写满，write() 就会阻塞，程序卡在这里，无法处理其他事情。这种方式适合小数据量、简单交互程序（如 UNP 示例），因为写入量很小，不会真正填满缓冲区；但不适合高吞吐或需要并发控制的场景，因为应用层无法知晓“什么时候可以继续写”，无法实现 backpressure。如果想实现正确、可控的发送，必须使用 I/O 复用（select/poll/epoll）监听可写事件，并维护自己的发送队列，只有在内核缓冲区有空间时才继续写入。总结：不判断缓冲区直接写没有逻辑错误，但风险是阻塞；小程序没问题，真正做网络服务必须用 I/O 复用做写控制。

#### 7.5.11　SO_REUSEADDR 和SO_REUSEPORT 套接字选项

**SO_REUSEADDR** 说明如下：

##### 1. SO_REUSEADDR解决监听端口被子进程占用导致重启失败的问题 （这一点比较重要， 后面三点作为了解）

当 TCP 服务器运行时，通常流程是：

1. 父进程创建监听 socket：`fd_listen = socket()` → `bind(80)` → `listen()`
2. 收到连接后 `accept()`，创建连接 socket：`fd_conn`
3. `fork()` 派生子进程，子进程用 `fd_conn` 和客户端通信
4. **父进程退出**（故意重启），但子进程还保持 fd_conn 开着**

此时问题出现：  
虽然父进程已经终止，但子进程的 **fd_conn 本地端口仍是 80**，说明**端口仍“被占用”**。  
当父进程重新启动时，它再次尝试：  

```
fd_listen = socket()
bind(80)   ← 这里失败
```

默认情况下，`bind(80)` 会失败，因为系统认为：  
**“已有 socket 使用着本地端口 80”**（子进程的连接 socket）。

而如果在 `socket()` 和 `bind()` 之间调用：

```
setsockopt(fd_listen, SOL_SOCKET, SO_REUSEADDR, ...)
```

则允许这种情况：  
只要没有别的监听 socket 绑定 80，**即使存在旧连接占用该端口，也允许监听 socket 重新绑定端口**。  

因此服务器就能正常重启。  

结论：  
**所有 TCP 服务器都应该开启 `SO_REUSEADDR`，以避免父进程重启时因子进程占用端口导致 bind 失败。**

**核心逻辑其实就是**

你要彻底理解，就必须接受下面这句话：

> 一个 TCP 本地端口可以同时被一个监听 socket 和多个已建立连接 socket 使用。

但内核默认认为：

> 如果已有连接 socket在使用端口，这个端口对新的 bind 是“占用”状态。

除非你告诉它：

> 我知道这样是安全的，请允许我复用这个端点 —— 这就是 SO_REUSEADDR 的含义。

**SO_REUSEADDR 的作用就是：改变 bind 冲突的规则。**



##### 2. 在同一端口上启动同一服务器的多个实例（不同本地IP）

- 可在同一端口上启动同一服务的多个实例，只要每个实例绑定不同的本地IP。
- 典型场景：使用 IP 别名托管多个 HTTP 站点。
- 示例：
  - 主 IP：198.69.10.2  
  - 别名：198.69.10.128、198.69.10.129
  - 三个 HTTP 服务器绑定：
    1. INADDR_ANY:80（通配 IP，默认服务器）
    2. 198.69.10.128:80
    3. 198.69.10.129:80
- 注意：
  - 绑定相同 IP + 端口仍不允许。
  - 有些系统不允许通配地址绑定后再绑定更明确 IP，通配地址绑定的服务器应最后启动。

---

##### 3. 单个进程绑定同一端口到多个套接字（不同本地IP）

- 一个进程可以将同一端口绑定到多个套接字，但每次必须指定不同的本地IP。
- 适用场景：
  - UDP 服务器希望知道客户端请求的目的 IP。
- TCP 通常不需要，因为可通过 `getsockname()` 获取连接的本地 IP。
- 对于多目的主机只服务部分地址的 TCP 服务器，也可采用此方法。

---

##### 4. 完全重复绑定（通常仅支持 UDP）

- 同一 IP + 端口可以绑定到多个套接字（UDP 支持）。
- 典型用途：多播/广播 UDP，允许同一主机上同一个应用多个副本运行。
- 数据报递送规则：
  - 多播/广播地址：每个匹配套接字收到一份副本
  - 单播地址：只递送给一个套接字，选择哪个由系统实现决定
- TCP 不支持此特性。

---

#### 总结表

| 用途 | 要求 | 适用场景 | 注意事项 |
|------|------|----------|----------|
| (1) 重启绑定端口 | 无论旧连接存在 | TCP 服务器重启 | 必须设置 SO_REUSEADDR |
| (2) 多实例绑定同端口 | 不同本地 IP | 多站点 HTTP 服务 | 完全重复绑定不允许；通配地址应最后启动 |
| (3) 单进程绑定多套接字 | 每个套接字不同本地 IP | UDP 服务器 | TCP 一般不使用 |
| (4) 完全重复绑定 | IP+端口允许重复 | UDP 多播/广播 | TCP 不支持；数据报按套接字分发 |


**SO_REUSEPORT** 说明如下：

SO_REUSEPORT 在早期 Unix 系统支持有限，而且用途比 SO_REUSEADDR 更进阶，它允许多个套接字完全绑定同一 IP+端口并由内核自动分发连接，实现负载均衡，而 SO_REUSEADDR 主要解决 TCP 服务器重启、旧连接占用端口以及多 IP 绑定的问题，因此在《UNPv1》的 7.5.11 小节中作者只讲了 SO_REUSEADDR，没有单独说明 SO_REUSEPORT。

SO_REUSEPORT（又称 port reuse）允许多个套接字或线程/进程同时绑定同一 IP+端口，每个套接字独立 accept()，内核会在新连接到来时自动分配给其中一个套接字，实现负载均衡，同时避免惊群（thundering herd）问题；相比之下，SO_REUSEADDR 主要用于允许 TCP 服务器重启时绑定已被旧连接占用的端口或绑定不同本地 IP，但不能解决多线程/多进程监听同一端口时的负载均衡和惊群问题。

SO_REUSEPORT 在 Linux 上是从 内核 2.6.27 开始支持的，它允许多个进程或线程同时绑定同一 IP+端口，内核自动分配连接并实现负载均衡，从而避免惊群问题；相比之下，SO_REUSEADDR 早期就支持，用于端口重用或多 IP 绑定，但不能实现多线程/多进程监听同端口的负载均衡。

#### 7.6 IPv4套接字选项 （简要了解）

IPv4 套接字选项（通过 setsockopt/getsockopt 设置）主要用于控制 TCP/UDP 套接字在 IPv4 网络上的行为，包括 IP 层和传输层相关参数。常见功能包括：

1. **IP 地址和多播控制**
   - IP_TTL：设置 IP 报文的生存时间（Time To Live）。
   - IP_MULTICAST_IF：指定多播发送的本地接口。
   - IP_MULTICAST_TTL / IP_MULTICAST_LOOP：控制多播报文的生存时间和是否环回。

2. **接收和发送缓冲区**
   - SO_RCVBUF / SO_SNDBUF：设置接收和发送缓冲区大小。
   - 影响吞吐量和性能。

3. **IP 分片和选项**
   - IP_HDRINCL：允许应用程序自己构造 IP 头（raw socket 用）。
   - IP_DONTFRAG：禁止 IP 分片。

4. **组播和广播相关**
   - IP_ADD_MEMBERSHIP / IP_DROP_MEMBERSHIP：加入或离开多播组。
   - SO_BROADCAST：允许发送广播数据报。

5. **其他控制**
   - IP_PKTINFO：接收数据包时获得目的 IP 和接收接口信息。
   - IP_RECVTTL、IP_RECVTOS：接收报文的 TTL 和服务类型信息。

> 总结：IPv4 套接字选项主要用于控制 IP 层行为、缓冲区大小、广播/多播操作以及报文元信息，应用程序可根据需求调整套接字性能和功能。

#### 7.9 TCP套接字选项

TCP_MAXSEG 用于设置或获取 TCP 连接允许的最大报文段长度（MSS），可控制每个 TCP 数据段大小以避免 IP 分片；TCP_NODELAY 用于禁用 Nagle 算法，使小数据包可以立即发送，减少延迟，适用于实时通信或高频小数据传输场景。


#### 7.11 fcntl 函数

fcntl 是 Unix/Linux 提供的 通用文件控制接口，用于操作文件描述符的属性或行为。它既可以用于普通文件，也可以用于套接字。
网络编程常用用途：非阻塞套接字，结合 select 或 poll 实现异步 I/O  && close-on-exec 标志：避免子进程继承不必要的文件描述符。


```c
int main() {
    int sockfd;
    struct sockaddr_in servaddr;

    // 1. 创建 TCP 套接字
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // ===========================
    // 2. 设置非阻塞模式
    // ===========================
    int flags = fcntl(sockfd, F_GETFL, 0);   // 获取当前文件状态标志
    if (flags < 0) {
        perror("fcntl F_GETFL");
        exit(EXIT_FAILURE);
    }
    flags |= O_NONBLOCK;                     // 设置非阻塞标志
    if (fcntl(sockfd, F_SETFL, flags) < 0) { // 更新文件状态标志
        perror("fcntl F_SETFL");
        exit(EXIT_FAILURE);
    }
    // 说明：非阻塞套接字在 read/write/connect 时不会阻塞，结合 select/poll 可以实现异步 I/O

    // ===========================
    // 3. 设置 close-on-exec 标志
    // ===========================
    flags = fcntl(sockfd, F_GETFD);         // 获取文件描述符标志
    if (flags < 0) {
        perror("fcntl F_GETFD");
        exit(EXIT_FAILURE);
    }
    flags |= FD_CLOEXEC;                     // 设置 close-on-exec
    if (fcntl(sockfd, F_SETFD, flags) < 0) {
        perror("fcntl F_SETFD");
        exit(EXIT_FAILURE);
    }
    // 说明：设置 FD_CLOEXEC 后，当调用 exec 系列函数创建子进程时，sockfd 会自动关闭
    // 避免子进程继承不必要的文件描述符

    // ===========================
    // 4. 绑定和连接示例（可选）
    // ===========================
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(8080);
    servaddr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (connect(sockfd, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0) {
        if (errno == EINPROGRESS) {
            // 非阻塞套接字 connect 尚未完成，可以使用 select/poll 检测可写事件
            printf("Connection in progress (non-blocking)\n");
        } else {
            perror("connect");
            exit(EXIT_FAILURE);
        }
    }

    printf("Socket setup complete.\n");

    close(sockfd);
    return 0;
}
```