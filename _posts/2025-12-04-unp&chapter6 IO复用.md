---
title: unp&chapter6 IO复用
author: xyx
date: 2025-12-04 13:33:00 +0800
categories: [justxyx, net-programming]
tags:
math: true
---

## 6.1 概述 （select poll epoll)

```c
// 每次循环都要重新设置 fd 集合
// O(n) 扫描所有 fd
//简单、跨平台

#include <stdio.h>
#include <sys/select.h>
#include <unistd.h>

int main() {
    fd_set rfds;
    int maxfd = 0; // 最大 fd
    int stdin_fd = STDIN_FILENO;

    while (1) {
        FD_ZERO(&rfds);
        FD_SET(stdin_fd, &rfds);
        if (stdin_fd > maxfd) maxfd = stdin_fd;

        int ret = select(maxfd + 1, &rfds, NULL, NULL, NULL);
        if (ret > 0) {
            if (FD_ISSET(stdin_fd, &rfds)) {
                char buf[128];
                int n = read(stdin_fd, buf, sizeof(buf)-1);
                buf[n] = 0;
                printf("read from stdin: %s", buf);
            }
        }
    }
    return 0;
}

```

```c
//使用 pollfd 数组
//每次调用仍然遍历数组（O(n)）
//可以方便处理多个 fd，扩展比 select 好
#include <stdio.h>
#include <poll.h>
#include <unistd.h>

int main() {
    struct pollfd fds[1];
    fds[0].fd = STDIN_FILENO;
    fds[0].events = POLLIN;

    while (1) {
        int ret = poll(fds, 1, -1); // 阻塞
        if (ret > 0) {
            if (fds[0].revents & POLLIN) {
                char buf[128];
                int n = read(fds[0].fd, buf, sizeof(buf)-1);
                buf[n] = 0;
                printf("read from stdin: %s", buf);
            }
        }
    }
    return 0;
}
```

```c
//内核维护活跃 fd 列表
//只处理就绪事件，O(1)
//可以轻松扩展到上万 fd，适合高并发服务器
//支持 LT / ET 模式，可控制触发策略
#include <stdio.h>
#include <sys/epoll.h>
#include <unistd.h>

int main() {
    int epfd = epoll_create1(0);
    struct epoll_event ev;

    ev.events = EPOLLIN;
    ev.data.fd = STDIN_FILENO;
    epoll_ctl(epfd, EPOLL_CTL_ADD, STDIN_FILENO, &ev);

    struct epoll_event events[10];

    while (1) {
        int n = epoll_wait(epfd, events, 10, -1); // 阻塞
        for (int i = 0; i < n; i++) {
            if (events[i].data.fd == STDIN_FILENO) {
                char buf[128];
                int r = read(STDIN_FILENO, buf, sizeof(buf)-1);
                buf[r] = 0;
                printf("read from stdin: %s", buf);
            }
        }
    }
    return 0;
}
```

## 6.2 I/O模型

略

## 6.3 select 函数

### 概览

##### 1. **Berkeley 内核 vs SVR4 的行为**

- Berkeley 内核（BSD 系列）

    - select() 如果被信号中断，会返回 -1 并设置 errno = EINTR。

    - 内核不会自动重启 select()。

- SVR4 / System V 系列

    - select() 默认也会被信号中断，但如果在安装信号处理函数时指定了 SA_RESTART 标志，内核会尝试自动重启被中断的系统调用，包括 select()。

    - 如果没有指定 SA_RESTART，行为与 BSD 类似，也会返回 EINTR。

##### 2. **SA_RESTART 的作用**

```c
struct sigaction sa;
sa.sa_handler = handler;
sa.sa_flags = SA_RESTART;
sigemptyset(&sa.sa_mask);
sigaction(SIGINT, &sa, NULL);
```

- 表示当信号触发时，如果某些可重启的系统调用被中断（如 read(), write(), select() 等），内核会自动重新执行，而不是返回 EINTR。

- 并不是所有系统调用都能自动重启，行为仍然可能依赖平台。

##### 3. **信号中断与系统调用**

在 UNIX/Linux 下，阻塞系统调用在信号到来时可能返回 -1 并设置 errno = EINTR。常见的阻塞调用包括：

- select(), poll()

- accept()

- read(), write()

- sleep()（不同系统行为略有差异）

```c
int safe_select(int nfds, fd_set *readfds, fd_set *writefds, fd_set *exceptfds, struct timeval *timeout) {
    int n;
    do {
        n = select(nfds, readfds, writefds, exceptfds, timeout);
    } while (n < 0 && errno == EINTR);
    return n;
}
```

### 描述符就绪条件

**满足下列四个条件中的任何一个时，一个套接字准备好读。**

a) 该套接字接收缓冲区中的数据字节数大于等于套接字接收缓冲区低水位标记的当前大小。对这样的套接字执行读操作不会阻塞并将返回一个大于0的值（也就是返回准备好读入的数据）。我们可以使用SO_RCVLOWAT 套接字选项设置该套接字的低水位标记。对于TCP和UDP套接字而言，其默认值为1。

b) 该连接的读半部关闭（也就是接收了FIN的TCP连接）。对这样的套接字的读操作将不阻塞并返回0（也就是返回EOF）。

c) 该套接字是一个监听套接字且已完成的连接数不为0。对这样的套接字的accept 通常不会阻塞，不过我们将在15.6节讲解accept 可能阻塞的一种时序条件。

d) 其上有一个套接字错误待处理。对这样的套接字的读操作将不阻塞并返回-1（也就是返回一个错误），同时把errno 设置成确切的错误条件。这些待处理错误 （pending error）也可以通过指定SO_ERROR 套接字选项调用getsockopt 获取并清除。

**下列四个条件中的任何一个满足时，一个套接字准备好写。**

a) 该套接字发送缓冲区中的可用空间字节数大于等于套接字发送缓冲区低水位标记的当前大小，并且或者该套接字已连接，或者该套接字不需要连接（如UDP套接字）。这意味着如果我们把这样的套接字设置成非阻塞（第16章），写操作将不阻塞并返回一个正值（如由传输层接受的字节数）。我们可以使用SO_SNDLOWAT 套接字选项来设置该套接字的低水位标记。对于TCP和UDP套接字而言，其默认值通常为2048。

b) 该连接的写半部关闭。对这样的套接字的写操作将产生SIGPIPE 信号（5.12节）。

c) 使用非阻塞式connect 的套接字已建立连接，或者connect 已经以失败告终。
    当套接字被设置为非阻塞并执行 connect() 时，TCP 的三次握手会在后台进行，而 connect() 不会等待握手完成，而是立即返回 -1 并设置 errno = EINPROGRESS，表示连接正在建立中。这时连接既没有成功，也没有失败，只是处于处理中状态（握手中），进程需要通过 select、poll 或 epoll 等机制等待连接完成的通知。
    当连接过程结束时，无论连接最终是成功还是失败，套接字都会变为可写，因此“可写”事件只是表示 connect 已经完成，而不是直接表示连接成功。内核不会告诉你结果，需要由应用程序通过 getsockopt(fd, SOL_SOCKET, SO_ERROR, ...) 查询连接状态：如果 SO_ERROR 为 0，表示连接成功，否则错误值表示连接失败。这样可以准确判断非阻塞 connect 的结果。

d) 其上有一个套接字错误待处理。对这样的套接字的写操作将不阻塞并返回-1（也就是返回一个错误），同时把errno 设置成确切的错误条件。这些待处理的错误也可以通过指定SO_ERROR 套接字选项调用getsockopt 获取并清除。

### 带外标记

    略

## select 的最大描述符数 

    略

## 6.4 str_cli 函数（修订版）


**客户的套接字上的三个条件处理如下：**

(1) 如果对端TCP发送数据，那么该套接字变为可读，并且read 返回一个大于0的值（即读入数据的字节数）。

(2) 如果对端TCP发送一个FIN（对端进程终止），那么该套接字变为可读，并且read 返回0（EOF）。

(3) 如果对端TCP发送一个RST（对端主机崩溃并重新启动），那么该套接字变为可读，并且read 返回-1，而errno 中含有确切的错误码。

```c
#include "unp.h"

void
str_cli(FILE *fp, int sockfd)
{
    int     maxfdp1;
    fd_set  rset;
    char    sendline[MAXLINE], recvline[MAXLINE];

    FD_ZERO(&rset);
    for ( ; ; ) {
        FD_SET(fileno(fp), &rset);
        FD_SET(sockfd, &rset);
        maxfdp1 = max(fileno(fp), sockfd) + 1;
        Select(maxfdp1, &rset, NULL, NULL, NULL);

        if (FD_ISSET(sockfd, &rset)) {  /* socket is readable */
            if (Readline(sockfd, recvline, MAXLINE) == 0)
                err_quit("str_cli: server terminated prematurely");
            Fputs(recvline, stdout);
        }

        if (FD_ISSET(fileno(fp), &rset)) {  /* input is readable */
            if (Fgets(sendline, MAXLINE, fp) == NULL)
                return;     /* all done */
            Writen(sockfd, sendline, strlen(sendline));
        }
    }
}
```

## 6.5 批量输入

    不要一行一行发送，小数据交互要批量输入，否则性能完全受 RTT 限制。

## 6.6　shutdown 函数

```c
/*
0	SHUT_RD	关闭读方向
1	SHUT_WR	关闭写方向
2	SHUT_RDWR	同时关闭读写
*/
#include <sys/socket.h>
int shutdown(int sockfd, int howto);
```

#### shutdown() 的各模式行为

`shutdown(int sockfd, int how)` 用于关闭 TCP 连接的某一方向数据流。参数 `how` 定义关闭方式：  
- `SHUT_RD`：关闭读方向，丢弃接收缓冲区数据并拒绝后续数据。对端继续发数据仍会成功，但本进程无法再读，读操作返回 0（EOF）。本地仍可继续发送数据。很少用，一般用于强制忽略数据流。
- `SHUT_WR`：关闭写方向，发送 FIN 给对端，表示我方不再发送数据，对端读到 EOF；但本地仍可读，对端还能继续向我方发数据，实现半关闭（half-close）。  
- `SHUT_RDWR`：读写双向同时关闭，相当于先 `SHUT_RD` 再 `SHUT_WR`，本地不再收发数据，对端看到我方 FIN 并最终结束连接流程。适用于完全终止。

#### shutdown() 与 close() 的区别

    shutdown() 是协议层行为，close() 是资源层行为。

`shutdown()` 作用于 **TCP 协议层**，改变的是连接状态，比如发送 FIN、进入 CLOSE_WAIT/TIME_WAIT，它只是告诉对端“我不发了/我不收了”，此时本进程的 socket **句柄仍然存在**，仍可使用 `select()`、`getsockopt()` 或继续读数据，实现 TCP 半关闭，不释放本地资源。而 `close()` 作用于 **资源层**，关闭的是文件描述符，引用计数减 1 为 0 时释放 socket 内核结构，彻底回收资源，对于进程而言该 socket 已不存在，无法再进行读写，因此无法继续发送数据。也就是说：**shutdown 控制连接方向，close 释放本地资源**。

`close()` 关闭文件描述符，当引用计数归零时释放 socket 并中断整个连接：它会同时关闭读写方向、清理资源，并可能立即发送 RST（特别是缓冲未读数据或 SO_LINGER 配置情况下）；程序失去对该 socket 的所有控制。而 `shutdown()` 只影响 TCP 流方向，不关闭文件描述符，用于半关闭通信，允许保持连接状态继续收或发，支持优雅关闭（FIN）。简而言之：`shutdown()`=协议层方向关闭；`close()`=释放 FD 并结束连接生命周期。

## 6.7 str_cli 函数（再修订版）

```c
#include "unp.h"

void
str_cli(FILE *fp, int sockfd)
{
    int     maxfdp1, stdineof;
    fd_set  rset;
    char    buf[MAXLINE];
    int     n;

    stdineof = 0;                /* 标记标准输入是否已经EOF，用来区分正常/异常结束 */
    FD_ZERO(&rset);
    for ( ; ; ) {
        if (stdineof == 0)       /* 只要stdin未EOF，就监听stdin的可读事件 */
            FD_SET(fileno(fp), &rset);

        FD_SET(sockfd, &rset);   /* 始终监听socket的可读事件 */
        maxfdp1 = max(fileno(fp), sockfd) + 1;
        Select(maxfdp1, &rset, NULL, NULL, NULL);

        /* ---- socket可读事件 ---- */
        if (FD_ISSET(sockfd, &rset)) {
            /* 用read读取原始字节缓冲，不使用fgets避免stdio缓冲干扰select判断 */
            if ( (n = Read(sockfd, buf, MAXLINE)) == 0) {
                /*
                 * socket读到EOF，即对端发送FIN。
                 * 若此时stdin也已EOF(我们已发送FIN)，则为正常关闭；
                 * 否则说明服务器在我们输入没结束前提前终止，属于异常。
                 */
                if (stdineof == 1)
                    return;         /* 正常终止 */
                else
                    err_quit("str_cli: server terminated prematurely");
            }

            /* 将收到的数据写到stdout，同样用write避免缓冲问题 */
            Write(fileno(stdout), buf, n);
        }

        /* ---- stdin可读事件 ---- */
        if (FD_ISSET(fileno(fp), &rset)) {
            /* 用read读stdin数据，不用fgets，避免缓冲影响select */
            if ( (n = Read(fileno(fp), buf, MAXLINE)) == 0) {
                /*
                 * stdin读到EOF(用户Ctrl+D)，表示不再发送数据。
                 * 设置标志，并调用shutdown(SHUT_WR)发送FIN，实现TCP半关闭：
                 *   关闭写方向/保留读方向，继续接收服务器数据。
                 */
                stdineof = 1;                        /* 标记stdin已EOF */
                Shutdown(sockfd, SHUT_WR);           /* 发送FIN(关闭写方向) */
                FD_CLR(fileno(fp), &rset);           /* 不再监听stdin */
                continue;
            }

            /* stdin有数据则写入socket，继续交互 */
            Writen(sockfd, buf, n);
        }
    }
}
```

**两点说明**：
1. 使用半关闭机制:stdineof, 它是一个状态机开关，控制什么时候停止监听 stdin。TCP 半关闭会产生一个“正常 EOF”。
2. 使用 read 读 stdin 能避免 libc 行缓冲影响 select 事件，使 select 触发与实际可读数据一致。
    ```shell
    // stdin 可读 ≠ fgets() 已经能读到数据
    // fgets() 使用了 stdio 的缓冲（buffer）
    [用户输入]  1 2 3
                   <cursor>
    select() 返回：可读
    fgets()：拿不到数据，因为用户还没按回车
    ```

## 6.8 TCP回射服务器程序（修订版）

```c
/* include fig01 */
#include    "unp.h"

int
main(int argc, char **argv)
{
    int                 i, maxi, maxfd, listenfd, connfd, sockfd;
    int                 nready, client[FD_SETSIZE];
    ssize_t             n;
    fd_set              rset, allset;
    char                buf[MAXLINE];
    socklen_t           clilen;
    struct sockaddr_in  cliaddr, servaddr;

    listenfd = Socket(AF_INET, SOCK_STREAM, 0);  
    // 创建TCP监听socket (IPv4, TCP)

    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family      = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port        = htons(SERV_PORT);
    // 初始化本地地址结构，绑定任意IP+固定端口

    Bind(listenfd, (SA *) &servaddr, sizeof(servaddr));
    // 绑定地址结构到listenfd

    Listen(listenfd, LISTENQ);
    // 开始监听，进入 LISTEN 状态

    maxfd = listenfd;          /* initialize */
    // 当前 select 能看到的最大描述符，初始为 listenfd

    maxi = -1;                 /* index into client[] array */
    // client[] 有效最大下标，初始无客户端

    for (i = 0; i < FD_SETSIZE; i++)
        client[i] = -1;        /* -1 indicates available entry */
    // 初始化 client[] 数组，记录每个客户端socket，不使用 = -1

    FD_ZERO(&allset);
    FD_SET(listenfd, &allset);
    // 把 listenfd 放进select监控集合 allset，代表要监控新连接
/* end fig01 */

/* include fig02 */
    for ( ; ; ) {  // 主事件循环
        rset = allset;      /* structure assignment */
        // select 每次修改 rset，所以每次都先赋值一份
        // rset 是本轮实际监听的集合

        nready = Select(maxfd+1, &rset, NULL, NULL, NULL);
        // 阻塞等待：监听read事件
        // 返回可读的fd数量

        if (FD_ISSET(listenfd, &rset)) {    /* new client connection */
            // 如果 listen socket 可读，表明有新的连接到来

            clilen = sizeof(cliaddr);
            connfd = Accept(listenfd, (SA *) &cliaddr, &clilen);
            // 接受新连接，返回新的连接socket

#ifdef  NOTDEF
            printf("new client: %s, port %d\n",
                    Inet_ntop(AF_INET, &cliaddr.sin_addr, 4, NULL),
                    ntohs(cliaddr.sin_port));
#endif
            // 打印新连接信息（被编译选项禁用）

            for (i = 0; i < FD_SETSIZE; i++)
                if (client[i] < 0) {
                    client[i] = connfd; /* save descriptor */
                    break;
                }
            // 在 client[] 找一个空位保存新客户端fd

            if (i == FD_SETSIZE)
                err_quit("too many clients");
            // 达到同时客户端上限，直接退出

            FD_SET(connfd, &allset);    /* add new descriptor to set */
            // 监控新连接的读事件

            if (connfd > maxfd)
                maxfd = connfd;         /* for select */
            // 更新最大 fd 值

            if (i > maxi)
                maxi = i;               /* max index in client[] array */
            // 更新 client 数组有效范围

            if (--nready <= 0)
                continue;               /* no more readable descriptors */
            // 已处理完本次所有事件
        }

        for (i = 0; i <= maxi; i++) {   /* check all clients for data */
            // 遍历所有客户端，看是否有数据可读

            if ( (sockfd = client[i]) < 0)
                continue;
            // -1 表示槽位未使用，跳过

            if (FD_ISSET(sockfd, &rset)) {
                // 客户端socket有数据可读

                if ( (n = Read(sockfd, buf, MAXLINE)) == 0) {
                        /*4connection closed by client */
                    // Read=0 表示对端正常关闭(EOF)

                    Close(sockfd);
                    FD_CLR(sockfd, &allset);
                    client[i] = -1;
                    // 清理该客户端

                } else
                    Writen(sockfd, buf, n);
                    // 回射：直接把客户端发来的数据原样写回去

                if (--nready <= 0)
                    break;              /* no more readable descriptors */
                // 本轮事件处理完，跳出循环
            }
        }
    }
}
/* end fig02 */
```

### 拒绝服务型攻击（简明说明 + 两段伪码）

**要点一句话**：旧实现用 `readline()` 等换行，会在内部循环阻塞并可能被单字节慢速客户端挂住（DoS）；新版用 `read()` 按字节流处理，不等待换行，因此不会产生该类挂死问题。  
（书中有段文字把 `readline` 的行为直接套到 `read` 上，容易引起误解——实际代码已改为 `read`，不存在原来的 DoS。）

---

#### 易受攻击的（行式 / readline）伪码 — **危险**

```c
// 每个客户端在同一执行线程/流程中按行处理
while (connection_open) {
    // readline 内部会循环 read()，直到读到 '\n' 或 EOF 才返回
    line = readline(connfd);   // 阻塞，直到遇到 '\n'
    if (line == NULL) break;
    writen(connfd, line);
}
```

- 攻击：客户端只发送 1 字节（非换行），然后睡眠 -> readline 在内部继续 read() 等待换行 -> 应用层停在该连接的 readline 上 -> 在单线程/错误的调度下可能导致服务不可用（DoS）。

#### 安全的（字节流 / read）伪码 — 无此问题

```c
// select/循环 或 每连接独立处理，直接按字节流读写
while (connection_open) {
    n = read(connfd, buf, MAXLINE);  // 读到多少返回多少（不等换行）
    if (n == 0) break;               // 对端关闭
    writen(connfd, buf, n);          // 立即回显已读到的数据
}
```

- 特点：read() 只返回内核已有的字节，不会等待换行；即使客户端只发 1 字节并睡眠，服务器也能立刻处理并继续为其它连接服务，不会被单个慢连接“挂住”。

## 6.9 pselect 函数

    如果你想让信号唤醒 select，就不要阻塞信号；如果你要同时避免信号在 select 之前到达被处理掉，就必须让“解除信号屏蔽 + 进入 select”是原子操作，单独用 sigprocmask 和 select 做不到，所以有了 pselect。

### select & pselect 区别

#### 信号来了必须唤醒 select

- 语义：当 select 正在阻塞时，如果有信号到来，select 必须立即返回（通常返回 -1 并设置 errno = EINTR）。
- 只关心 select 阻塞期间的唤醒。
- 不关心信号是否在 select 调用之前已经到达。
- ⚠️ 竞态：如果信号在 select 调用之前已经到达并被处理了，select 可能永远阻塞 → lost/missed wakeup。

```c
sigprocmask(SIG_UNBLOCK, &mask); // 信号不阻塞
select(...);  // 如果此时信号来了，返回 EINTR
```

#### select 必须感知到信号事件

- 语义：无论信号何时到来（select 之前还是期间），select 都能知道信号发生过，并能在返回后处理（比如中断或做某些动作）。
- 关心所有时间点的信号，不会“丢掉”。
- ✅ 保证：select 调用之前信号不会丢失 & select 调用期间信号能唤醒
- 实现复杂，需要 pselect 或 ppoll，单独用 sigprocmask + select 不行。

```c
sigprocmask(SIG_BLOCK, &mask); // 阻塞信号
pselect(..., &mask);           // 原子解除阻塞 + 等待
```

### 竞态问题

    当程序的正确性依赖于多个操作执行的相对时间顺序，而这种顺序无法保证时，就可能出现错误，这种情况叫竞态条件（race condition）。
    在程序里，“两个事件或操作发生的顺序不确定”，可能导致程序结果不对，就是竞态。

### select 的竞态问题

```c
时间 --->

情况 A: 信号在 select 前
[ sigprocmask解除 ] --> [ 信号到达并处理 ] --> [ select阻塞 ] --> 阻塞可能永远不返回

情况 B: 信号在 select中
[ sigprocmask解除 ] --> [ select阻塞 ] --> [ 信号到达打断 select ] --> select返回EINTR
```

## 6.10 poll 函数

`poll` 是 POSIX 标准提供的多路 I/O 复用接口，用来同时监视 **多个文件描述符** 是否可读、可写或出现异常。

相比 `select`：
- 不受文件描述符数量限制（`select` 有 `FD_SETSIZE` 限制）
- 使用更现代的数据结构，更方便动态管理大量描述符

---

### 1. 函数原型

```c
#include <poll.h>

int poll(struct pollfd *fds, nfds_t nfds, int timeout);
```

#### 参数说明

| 参数       | 说明 |
|------------|------|
| `fds`      | `struct pollfd` 数组，每个元素描述一个文件描述符和感兴趣的事件 |
| `nfds`     | 数组长度（监控多少个文件描述符） |
| `timeout`  | 等待时间（毫秒）：<br> 0 = 不阻塞<br> -1 = 阻塞直到事件发生<br> >0 = 阻塞指定毫秒 |

---

### 2. struct pollfd 结构

```c
struct pollfd {
    int   fd;         // 文件描述符
    short events;     // 关注的事件
    short revents;    // 发生的事件，由内核填写
};
```

#### 常用事件

| 宏          | 含义                     |
|-------------|-------------------------|
| `POLLIN`    | 可读（读不会阻塞）       |
| `POLLOUT`   | 可写（写不会阻塞）       |
| `POLLERR`   | 错误发生                 |
| `POLLHUP`   | 对端挂起（关闭连接）     |
| `POLLNVAL`  | fd 无效                  |

---

### 3. 基本用法示例

```c
#include <stdio.h>
#include <poll.h>
#include <unistd.h>

int main() {
    struct pollfd fds[1];
    fds[0].fd = 0;           // 标准输入
    fds[0].events = POLLIN;  // 关注可读事件

    int ret = poll(fds, 1, 5000); // 等待 5 秒

    if (ret == -1) {
        perror("poll");
    } else if (ret == 0) {
        printf("timeout\n");
    } else {
        if (fds[0].revents & POLLIN) {
            char buf[100];
            int n = read(0, buf, sizeof(buf)-1);
            if (n > 0) {
                buf[n] = '\0';
                printf("input: %s\n", buf);
            }
        }
    }

    return 0;
}
```

---

### 4. 与 select 对比

| 特性             | `select`                    | `poll`                     |
|-----------------|----------------------------|----------------------------|
| 文件描述符限制    | 受 `FD_SETSIZE` 限制       | 没有固定限制              |
| 数据结构         | fd_set + 宏操作            | struct pollfd 数组        |
| 可扩展性         | 数组必须固定大小           | 可以动态分配数组           |
| 使用复杂度       | fd_set 需要清零/设置/检查   | 数组初始化 + 检查 revents |
| 支持事件类型      | 可读、可写、异常           | 可读、可写、异常、挂起等  |

---

### 5. 适用场景

- 监控大量文件描述符（几百到几千）
- 需要更灵活的事件类型（挂起、错误、无效 fd）
- 想避免 `select` 的 `FD_SETSIZE` 限制

---

### 6. 注意事项

1. `poll` 和 `select` 都会修改传入的数组/结构，下一次调用前需要重新设置  
2. 超时时间单位是毫秒  
3. 对于高性能网络服务器，如果文件描述符非常多，可能会使用 **`epoll`（Linux）或 `kqueue`（BSD/Mac）** 替代 `poll`

## 6.11　TCP回射服务器程序（再修订版）

```c
/* include fig01 */
#include	"unp.h"
#include	<limits.h>		/* for FOPEN_MAX */

int
main(int argc, char **argv)
{
	int					i, maxi, listenfd, connfd, sockfd;
	int					nready;
	ssize_t				n;
	char				buf[MAXLINE];
	socklen_t			clilen;
	struct pollfd		client[FOPEN_MAX];
	struct sockaddr_in	cliaddr, servaddr;

	listenfd = Socket(AF_INET, SOCK_STREAM, 0);

	bzero(&servaddr, sizeof(servaddr));
	servaddr.sin_family      = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port        = htons(SERV_PORT);

	Bind(listenfd, (SA *) &servaddr, sizeof(servaddr));

	Listen(listenfd, LISTENQ);

	client[0].fd = listenfd;
	client[0].events = POLLRDNORM;
	for (i = 1; i < FOPEN_MAX; i++)
		client[i].fd = -1;		/* -1 indicates available entry */
	maxi = 0;					/* max index into client[] array */
/* end fig01 */

/* include fig02 */
	for ( ; ; ) {
		nready = Poll(client, maxi+1, INFTIM);

		if (client[0].revents & POLLRDNORM) {	/* new client connection */
			clilen = sizeof(cliaddr);
			connfd = Accept(listenfd, (SA *) &cliaddr, &clilen);
#ifdef	NOTDEF
			printf("new client: %s\n", Sock_ntop((SA *) &cliaddr, clilen));
#endif

			for (i = 1; i < FOPEN_MAX; i++)
				if (client[i].fd < 0) {
					client[i].fd = connfd;	/* save descriptor */
					break;
				}
			if (i == FOPEN_MAX)
				err_quit("too many clients");

			client[i].events = POLLRDNORM;
			if (i > maxi)
				maxi = i;				/* max index in client[] array */

			if (--nready <= 0)
				continue;				/* no more readable descriptors */
		}

		for (i = 1; i <= maxi; i++) {	/* check all clients for data */
			if ( (sockfd = client[i].fd) < 0)
				continue;
			if (client[i].revents & (POLLRDNORM | POLLERR)) {
				if ( (n = read(sockfd, buf, MAXLINE)) < 0) {
					if (errno == ECONNRESET) {
							/*4connection reset by client */
#ifdef	NOTDEF
						printf("client[%d] aborted connection\n", i);
#endif
						Close(sockfd);
						client[i].fd = -1;
					} else
						err_sys("read error");
				} else if (n == 0) {
						/*4connection closed by client */
#ifdef	NOTDEF
					printf("client[%d] closed connection\n", i);
#endif
					Close(sockfd);
					client[i].fd = -1;
				} else
					Writen(sockfd, buf, n);

				if (--nready <= 0)
					break;				/* no more readable descriptors */
			}
		}
	}
}
/* end fig02 */
```