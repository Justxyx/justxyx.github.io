---
title: unp&chapter5 客户端&服务器程序示例
author: xyx
date: 2025-12-02 13:33:00 +0800
categories: [justxyx, net-programming]
tags:
math: true
---

## 5.1 - 5.5 代码示例

```c
// server 端
#include "unp.h"

int main() {
    int listenfd, connfd;
    pid_t chilpid;
    socklen_t clilen;
    struct sockaddr_in cliaddr,servaddr;

    listenfd = Socket(AF_INET, SOCK_STREAM, 0);

    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(SERV_PORT);

    Bind(listenfd, (SA *)&servaddr, sizeof(servaddr));

    Listen(listenfd, LISTENQ);

    for (;;) {
        clilen = sizeof(cliaddr);
        connfd = Accept(listenfd, (SA *) &cliaddr, &clilen);

        if ((chilpid = Fork()) == 0) {
            Close(listenfd);
            str_echo(connfd);
            exit(0);
        }
        Close(connfd);
    }
}

void
str_echo(int sockfd)
{
	ssize_t		n;
	char		line[MAXLINE];

	heartbeat_serv(sockfd, 1, 5);

	for ( ; ; ) {
		if ( (n = Readline(sockfd, line, MAXLINE)) == 0)
			return;		/* connection closed by other end */

		Writen(sockfd, line, n);
	}
}
```

```c
// client 端
#include "unp.h"

int main(int argc, char **argv) {
    int sockfd;
    struct sockaddr_in servaddr;

    if (argc != 2)
        err_quit("usage: tcpcli <IPaddress>");

    sockfd = Socket(AF_INET, SOCK_STREAM, 0);

    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(SERV_PORT);
    Inet_pton(AF_INET, argv[1], &servaddr.sin_addr);

    Connect(sockfd, (SA *)&servaddr, sizeof(servaddr));

    str_cli(stdin, sockfd);

    exit(0);
}

void
str_cli(FILE *fp, int sockfd)
{
	char			sendline[MAXLINE];
	struct args		args;
	struct result	result;

	while (Fgets(sendline, MAXLINE, fp) != NULL) {

		if (sscanf(sendline, "%ld%ld", &args.arg1, &args.arg2) != 2) {
			printf("invalid input: %s", sendline);
			continue;
		}
		Writen(sockfd, &args, sizeof(args));

		if (Readn(sockfd, &result, sizeof(result)) == 0)
			err_quit("str_cli: server terminated prematurely");

		printf("%ld\n", result.sum);
	}
}
```

## 5.6 正常启动


---

### 1. 输出解析

```
ps -e -o pid,ppid,tty,stat,args,wchan | grep tcp
10311 10182 pts/2    S    ./tcpserv01                 inet_csk_accept
10487 10249 pts/3    S+   ./tcpclien01 127.0.0.1      wait_woken
10488 10311 pts/2    S    ./tcpserv01                 wait_woken
10849 10182 pts/2    S+   grep --color=auto tcp       pipe_wait
```

#### 列含义：

* PID = 进程号
* PPID = 父进程号
* TTY = 所属终端
* STAT = 状态（S = 阻塞，R = 运行，+ = 前台进程）
* WCHAN = 内核阻塞点（进程当前挂起在哪个函数）

---

#### 服务器进程：

1. **10311 → 父 tcpserv01（监听进程）**

   * PPID = 10182 (bash)
   * TTY = pts/2
   * STAT = S → 阻塞
   * WCHAN = inet_csk_accept → 正在 accept() 阻塞，等待客户端连接

2. **10488 → 子 tcpserv01（处理某客户端）**

   * PPID = 10311（父服务器进程）
   * TTY = pts/2
   * STAT = S → 阻塞
   * WCHAN = wait_woken → 阻塞在 read/write 等操作，等待客户端数据

#### 客户端进程：

1. **10487 → tcpclien01**

   * PPID = 10249（bash/另一个终端）
   * TTY = pts/3
   * STAT = S+ → 阻塞且在前台
   * WCHAN = wait_woken → 阻塞在 read() 或 write()，等待服务器回应

#### grep 进程：

* 10849 → grep 自己，被列出来，无需关注

---

### 2. 父子关系和阻塞状态总结

```
bash(10182, pts/2)
└── tcpserv01(10311, pts/2)        ← 监听进程，阻塞在 accept()
     └── tcpserv01(10488, pts/2)   ← 子进程，阻塞在等待客户端数据

bash(10249, pts/3)
└── tcpclien01(10487, pts/3)       ← 客户端，阻塞在等待服务器回应
```

---

### 3. 关键理解

* 监听进程阻塞在 accept() → 新客户端来时才返回
* 子进程阻塞在 read()/write() → 处理客户端数据
* 客户端阻塞在 read()/write() → 等待服务器回应

### 4. 每行 wchan 含义

#### 10311 ./tcpserv01 → inet_csk_accept
- 表示 TCP 服务器进程在等待 `accept()` 的连接请求。
- `inet_csk_accept` 是内核函数，专门处理 TCP 套接字的连接队列。
- 也就是说，这个服务器进程在 **被动等待客户端连接**。

#### 10487 ./tcpclien01 → wait_woken
- 客户端进程在等待内核唤醒。
- `wait_woken` 表示内核已经安排好事件，进程处于 **可唤醒睡眠状态**（`TASK_INTERRUPTIBLE` 或 `TASK_UNINTERRUPTIBLE`）。
- 典型情况：客户端正在等待 TCP 发送/接收完成或等待连接完成。

#### 10488 ./tcpserv01 → wait_woken
- 同样是服务器进程，但这个线程可能在 **等待某个内核事件**（例如数据到达）。
- 在 TCP 服务器中，这通常是 `accept()` 返回前或 `recv()` 等待数据时的状态。

#### 10849 grep → pipe_wait
- `pipe_wait` 表示进程正在等待 **管道/缓冲区可用**。
- 在这里，是因为 `grep` 输出经过管道（例如在终端或被管道传输），内核检查管道缓冲区时，如果缓冲区满或者空就会进入等待。
- 总结：`pipe_wait` 并不是 TCP 特有，只是 `grep` 暂时挂起等待 I/O。

#### 总结
- `wchan` 指出 **进程在内核中睡眠的地方**，不一定是“进程在做的事情”，而是 **它在等待内核某个事件/资源的函数**。

#### 常见的 TCP 相关 wchan
- `inet_csk_accept` → 等待新连接
- `tcp_poll` / `tcp_wait_for_connect` → 等待 TCP 建立或数据
- `wait_woken` → 内核可唤醒等待
- `pipe_wait` → 等待管道缓冲区

#### wchan 与多线程

在 Linux 中，每个线程实际上都是一个轻量级进程（LWP, light-weight process），它们有独立的线程 ID（TID）。因此：

- 每个线程都有自己的 `wchan` 字段，可以通过 `ps -o pid,tid,wchan,comm` 或 `cat /proc/<tid>/wchan` 查看。
- `wchan` 表示线程当前在 **内核中等待的函数地址**，与进程类似。

> 注意：这里的“看到”是指可以用命令查看线程的阻塞点，但不是线程内部栈信息，只是它阻塞在哪个内核函数。


## 5.7 正常终止

    客户端进程退出时，内核自动关闭其打开的套接字，触发 TCP 发送 FIN 给服务器，服务器 TCP 接收到 FIN 后使阻塞的 read 返回 0，应用层得知客户端已关闭发送方向，从而可以处理完数据并关闭套接字，完成 TCP 四次挥手，连接最终关闭。

### 流程

(1) 当我们键入EOF字符时，fgets 返回一个空指针，于是str_cli 函数（图5-5）返回。

(2) 当str_cli 返回到客户的main 函数（图5-4）时，main 通过调用exit 终止。

(3) 进程终止处理的部分工作是关闭所有打开的描述符，因此客户打开的套接字由内核关闭。这导致客户TCP发送一个FIN给服务器，服务器TCP则以ACK响应，这就是TCP连接终止序列的前半部分。至此，服务器套接字处于CLOSE_WAIT状态，客户套接字则处于FIN_WAIT_2状态（图2-4和图2-5）。

(4) 当服务器TCP接收FIN时，服务器子进程阻塞于readline 调用（图5-3），于是readline 返回0。这导致str_echo 函数返回服务器子进程的main 函数。

(5) 服务器子进程通过调用exit 来终止（图5-2）。

(6) 服务器子进程中打开的所有描述符随之关闭。由子进程来关闭已连接套接字会引发TCP连接终止序列的最后两个分节：一个从服务器到客户的FIN和一个从客户到服务器的ACK（图2-5）。至此，连接完全终止，客户套接字进入TIME_WAIT状态。

(7) 进程终止处理的另一部分内容是：在服务器子进程终止时，给父进程发送一个SIGCHLD 信号。这一点在本例中发生了，但是我们没有在代码中捕获该信号，而该信号的默认行为是被忽略。既然父进程未加处理，子进程于是进入僵死状态。我们可以使用ps 命令验证这一点。

### rst & fin 解析

    客户端进程退出 -> 自动关闭socket 链接 -> 进程调用 closefd -> 触发fin

| 特性 | FIN | RST |
|------|-----|-----|
| 含义 | 对端正常关闭发送 | 对端异常终止/拒绝连接 |
| TCP 状态机 | 进入 CLOSE_WAIT / FIN_WAIT_2 | 直接进入 CLOSED |
| read 返回 | 0 (EOF) | -1, errno=ECONNRESET |
| write 行为 | 可以继续发送数据 | 失败，errno=ECONNRESET |
| 应用层感知 | 可优雅处理 EOF | 需要异常处理 |

## 5.8 POSIX信号处理

### Unix/Linux 信号处理概览

#### 1️⃣ 信号处理动作 (Signal Handling)

##### 核心作用
- 定义信号发生时应该做什么  

##### 核心结构：struct sigaction

```c
struct sigaction {
    void     (*sa_handler)(int);               // 普通信号处理函数
    void     (*sa_sigaction)(int, siginfo_t*, void*); // 带额外信息的处理函数
    sigset_t   sa_mask;                        // 处理该信号期间临时阻塞的信号集
    int        sa_flags;                        // 标志位（SA_RESTART, SA_SIGINFO等）
    void     (*sa_restorer)(void);             // 一般不用
};
```

- `sa_handler`：普通信号处理函数  
- `sa_sigaction`：带附加信息的处理函数，需要 `SA_SIGINFO`  
- `sa_mask`：处理信号期间临时阻塞的信号  
- `sa_flags`：标志位（如 `SA_RESTART` 自动重启被中断的系统调用）  

##### 核心函数：sigaction()

```c
int sigaction(int signum, const struct sigaction *act, struct sigaction *oldact);
```

- `signum`：信号编号（如 `SIGINT`, `SIGCHLD`）  
- `act`：新动作  
- `oldact`：保存原动作（可 NULL）  

##### 示例：捕获 SIGINT（Ctrl-C）

```c
#include <stdio.h>
#include <signal.h>
#include <unistd.h>

void handler(int signo) {
    printf("捕获到 SIGINT，但程序继续运行！\n");
}

int main() {
    struct sigaction sa;
    sa.sa_handler = handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;

    sigaction(SIGINT, &sa, NULL);  // 安装信号处理函数

    while (1) {
        printf("程序运行中...\n");
        sleep(2);
    }

    return 0;
}
```

- **效果**：按 Ctrl-C 不会退出，打印提示信息  

---

#### 2️⃣ 信号屏蔽 / 阻塞 (Signal Masking)

##### 核心作用

- 控制进程在某段时间内是否接收特定信号  

##### 全局屏蔽字：sigprocmask()

```c
int sigprocmask(int how, const sigset_t *set, sigset_t *oldset);
```

- `how`：
  - `SIG_BLOCK`：加入屏蔽集合  
  - `SIG_UNBLOCK`：从屏蔽集合移除  
  - `SIG_SETMASK`：设置新的屏蔽字  
- `set`：要屏蔽/解除的信号集合  
- `oldset`：保存旧屏蔽字（可 NULL）  

##### 信号集合操作函数

| 函数 | 功能 |
|------|------|
| `sigemptyset(&set)` | 清空集合，不屏蔽任何信号 |
| `sigfillset(&set)` | 屏蔽所有信号 |
| `sigaddset(&set, signo)` | 添加信号到集合 |
| `sigdelset(&set, signo)` | 从集合移除信号 |

##### 示例：阻塞 SIGINT

```c
#include <stdio.h>
#include <signal.h>
#include <unistd.h>

int main() {
    sigset_t set, oldset;
    sigemptyset(&set);
    sigaddset(&set, SIGINT);

    // 阻塞 SIGINT
    sigprocmask(SIG_BLOCK, &set, &oldset);

    printf("SIGINT 被屏蔽，按 Ctrl-C 不会中断程序\n");
    sleep(5);

    // 恢复屏蔽字
    sigprocmask(SIG_SETMASK, &oldset, NULL);
    printf("SIGINT 恢复，按 Ctrl-C 可以中断程序\n");
    sleep(5);

    return 0;
}
```

- **效果**：
  - 前 5 秒 Ctrl-C 无效  
  - 恢复后 Ctrl-C 可终止程序  

---

#### 3️⃣ 总结

| 模块 | 功能 | 核心接口 | 示例用途 |
|------|------|----------|----------|
| **信号处理动作** | 信号发生时做什么 | `sigaction` | 捕获 SIGINT 打印提示，捕获 SIGCHLD 回收子进程 |
| **信号屏蔽/阻塞** | 控制信号什么时候可以生效 | `sigprocmask` + sigset_t | 在关键区阻塞信号，防止中断，保证安全 |

**一句话理解**：  
**动作 + 屏蔽 = 完整信号处理**  
动作定义“信号发生时做什么”，屏蔽定义“信号什么时候可以生效”。

### unp 函数概览

```c
Sigfunc *
signal(int signo, Sigfunc *func)
{
	struct sigaction	act, oact;

	act.sa_handler = func;
	sigemptyset(&act.sa_mask);
	act.sa_flags = 0;
	if (signo == SIGALRM) {
#ifdef	SA_INTERRUPT
		act.sa_flags |= SA_INTERRUPT;	/* SunOS 4.x */
#endif
	} else {
#ifdef	SA_RESTART
		act.sa_flags |= SA_RESTART;		/* SVR4, 44BSD */
#endif
	}
	if (sigaction(signo, &act, &oact) < 0)
		return(SIG_ERR);
	return(oact.sa_handler);
}
/* end signal */

Sigfunc *
Signal(int signo, Sigfunc *func)	/* for our signal() function */
{
	Sigfunc	*sigfunc;

	if ( (sigfunc = signal(signo, func)) == SIG_ERR)
		err_sys("signal error");
	return(sigfunc);
}
```

### 总结

    信号处理函数长期有效，信号在处理期间自动阻塞，默认不排队，通过 sigprocmask 可在关键区主动屏蔽信号保护程序执行。

#### 1️⃣ 信号处理函数的持久性
- 使用 `sigaction` 安装的信号处理函数一旦安装，就会一直有效，直到显式更改。
- 早期系统中，信号处理函数在执行一次后会自动恢复默认，需要重复安装。

#### 2️⃣ 信号阻塞行为
- 当信号处理函数正在运行时，该信号会被自动阻塞，避免重入。
- 安装处理函数时，通过 `sa_mask` 可以指定**额外要阻塞的信号**。
- 如果 `sa_mask` 为空集，则除了当前捕获的信号外，没有其他信号被阻塞。

#### 3️⃣ 信号递交与排队
- Unix 默认信号**不排队**：被阻塞期间产生的同一信号无论发生多少次，解除阻塞后通常只递交一次。
- POSIX 实时信号提供了排队机制，但普通信号仍是非排队、非可靠的。

#### 4️⃣ 临界区保护
- 可使用 `sigprocmask` 有选择地阻塞或解除阻塞信号。
- 这样在关键代码区段中，可以防止特定信号打断，从而保证数据安全和执行完整性。

## 5.9 处理SIGCHLD 信号

    设置僵死（zombie）状态的目的是维护子进程的信息，以便父进程在以后某个时候获取。这些信息包括子进程的进程ID、终止状态以及资源利用信息（CPU时间、内存使用量等等）。

### 处理僵死进程

```c
// server 端添加信号处理函数
void
sig_chld(int signo)
{
    pid_t	pid;
    int		stat;

    while ( (pid = waitpid(-1, &stat, WNOHANG)) > 0) {
        printf("child %d terminated\n", pid);
    }
    return; // 过在信号处理函数里显式写 return;，我们就能在调试器（gdb）中看到信号处理函数的返回点，从而判断：哪一个信号处理函数返回时导致了系统调用被 EINTR 中断。
}

void main() {
        ...
        Signal(SIGCHLD, sig_chld);
        for (;;) {
        }
        ...
}
```

(1) 我们键入EOF字符来终止客户。客户TCP发送一个FIN给服务器，服务器响应以一个ACK。
(2) 收到客户的FIN导致服务器TCP递送一个EOF给子进程阻塞中的readline ，从而子进程终止。
(3) 当SIGCHLD 信号递交时，父进程阻塞于accept 调用。sig_chld 函数（信号处理函数）执行，其wait 调用取到子进程的PID和终止状态，随后是printf 调用，最后返回。
(4) 既然该信号是在父进程阻塞于慢系统调用（accept ）时由父进程捕获的，内核就会使accept 返回一个EINTR 错误（被中断的系统调用）。而父进程不处理该错误（图5-2），于是中止。（**glibc 默认对慢系统调用启用了自动重启（SA_RESTART）， 在 Ubuntu 18.04（glibc 2.27）以及更现代的 Linux 系统 中，父进程在 accept() 被 SIGCHLD 中断时 不会终止。**）

### 处理被中断的系统调用

适用于慢系统调用的基本规则是：当阻塞于某个慢系统调用的一个进程捕获某个信号且 相应信号处理函数返回时，该系统调用可能 返回一个EINTR 错误。有些 **内核自动重启某些被中断的系统调用。**（SA_RESTART）

**因此你看到的写法是经典的、可移植的、可靠的写法**：

```c
for ( ; ; ) {
    clilen = sizeof(cliaddr);
    if ( (connfd = accept(listenfd, (SA *) &cliaddr, &clilen)) < 0) {
        if (errno == EINTR)
            continue;  /* back to for() —— 重试 accept */
        else
            err_sys("accept error");
    }

    /* 正常获得连接，跳出循环 */
    break;
}
```

## 5.10 wait 和waitpid 函数

```c
/*
 * wait() 与 waitpid() 总结
 *
 * 一、wait()
 * -----------------------------------------------------------
 * 1. 原型:
 *      pid_t wait(int *status);
 *
 * 2. 行为:
 *      - 阻塞等待任意一个子进程退出
 *      - 返回退出子进程的 PID
 *      - 若 status 不为 NULL，填入子进程退出状态
 *
 * 3. 限制:
 *      - 只能等待“任意”子进程，无法指定 PID
 *      - 总是阻塞，无法非阻塞
 *
 *
 * 二、waitpid()
 * -----------------------------------------------------------
 * 1. 原型:
 *      pid_t waitpid(pid_t pid, int *status, int options);
 *
 * 2. 参数 pid:
 *      >0   ：等待指定 PID 的子进程
 *      -1   ：等待任意子进程（等价 wait）
 *      0    ：等待与本进程同组的任意子进程
 *      < -1 ：等待进程组 ID = |pid| 的子进程
 *
 * 3. options 常用值:
 *      0         ：阻塞等待
 *      WNOHANG   ：不阻塞，无子进程退出则立即返回 0
 *      WUNTRACED ：返回因 SIGSTOP 停止的子进程
 *      WCONTINUED：返回收到 SIGCONT 后继续的子进程
 *
 * 4. 优点:
 *      - 可等待特定子进程
 *      - 可非阻塞
 *      - 在 SIGCHLD 中使用更安全，可一次性回收多个僵尸
 *
 *
 * 三、返回值
 * -----------------------------------------------------------
 *   >0 ：某个子进程的 PID（成功）
 *    0 ：options 包含 WNOHANG 且没有子进程退出
 *   -1 ：错误（若无子进程，errno = ECHILD）
 *
 *
 * 四、解析 status 的宏
 * -----------------------------------------------------------
 *   WIFEXITED(status)      -> 子进程是否正常退出（exit）
 *   WEXITSTATUS(status)    -> 正常退出码
 *
 *   WIFSIGNALED(status)    -> 是否被信号终止
 *   WTERMSIG(status)       -> 终止它的信号编号
 *
 *   WIFSTOPPED(status)     -> 是否收到 SIGSTOP 等而停止
 *   WSTOPSIG(status)       -> 停止信号编号
 *
 *   WIFCONTINUED(status)   -> 是否因 SIGCONT 继续执行
 *
 *
 * 五、SIGCHLD 中的推荐写法（UNP 标准）
 * -----------------------------------------------------------
 *   使用 waitpid(-1, &status, WNOHANG) 循环回收所有子进程：
 *
 *   void sig_chld(int signo) {
 *       pid_t pid;
 *       int status;
 *
 *       while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
 *           printf("child %d terminated\n", pid);
 *       }
 *   }
 *
 *   - 原因：信号可能成批到来，如果只调用一次 wait/waitpid，
 *          可能剩下多个僵尸进程没有被回收。
 *
 *
 * 六、核心区别总结
 * -----------------------------------------------------------
 *   wait      ：只能阻塞等待任意子进程
 *   waitpid   ：可指定 PID，可非阻塞，是现代服务器的标准做法
 *
 *   一句话总结：
 *       waitpid(-1, &status, WNOHANG) 是并发服务器回收子进程的最佳实践。
 *
 */
```

### SIGCHLD 信号处理与僵尸进程问题分析

在 Unix/Linux 系统编程中，SIGCHLD 信号用于通知父进程子进程已经终止。然而，仅仅建立一个 SIGCHLD 信号处理函数并在其中调用一次 `wait()`，**并不能完全避免僵尸进程的产生**。下面我们详细分析其原因。

---

#### 1. 问题根源：Unix 信号的不排队特性

Unix 系统中的标准信号（非实时信号）具有**不排队**的特性：

- 每个信号由内核使用一个标志位表示，标记是否待递交。
- 如果同一个信号在处理函数执行期间再次产生，并不会累加或排队。
- 信号处理函数在执行期间，该信号被自动阻塞。

举例：

假设有 5 个子进程几乎同时退出，内核产生 5 次 SIGCHLD：

- 内核记录第一次 SIGCHLD：pending = 1
- 接下来的 4 次 SIGCHLD：pending 仍为 1（不会累加）
- 用户态只会收到一次 SIGCHLD，处理函数执行一次

此时，如果处理函数只调用一次 `wait()`：

```c
void sig_chld(int signo) {
    int status;
    wait(&status);  // 仅回收一个子进程
}
```

结果：

- 只回收一个子进程
- 剩下的 4 个子进程仍为僵尸
- SIGCHLD 不会再次触发处理函数（信号不排队）

---

#### 2. 不确定性：信号递交的时序依赖网络事件

SIGCHLD 的递交次数存在不确定性，具体表现如下：

- 在客户端和服务器同一主机运行时：可能只触发一次 SIGCHLD → 留下 4 个僵尸。
- 跨主机运行时：由于 TCP FIN 到达服务器的时机不同，SIGCHLD 可能触发 2 次、3 次或 4 次 → 仍有部分僵尸残留。
- 这表明 SIGCHLD 信号递交的行为依赖于系统调度、网络延迟和进程终止顺序，因此具有不确定性。

---

#### 3. 正确处理方法：循环回收所有僵尸进程

为了确保不会留下僵尸进程，UNP 推荐在 SIGCHLD 处理函数中使用 `waitpid` 搭配 `WNOHANG` 循环回收：

```c
#include <sys/wait.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>

void sig_chld(int signo) {
    int status;
    pid_t pid;

    // 循环回收所有已终止的子进程
    // 循环会 不断调用 waitpid，每次回收一个僵尸
    // 即使 SIGCHLD 只递交一次，也能清理掉所有已经退出的子进程
    while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
        printf("Child %d terminated\n", pid);
    }
}
```

说明：

- `waitpid(-1, &status, WNOHANG)`：非阻塞地等待任意子进程
- while 循环确保 **即使 SIGCHLD 只递交一次**，也能清理掉所有僵尸进程
- 避免了因为信号不排队导致的僵尸进程残留问题

---

#### 4. 小结

1. **不排队的信号**：标准 Unix 信号不会累加，SIGCHLD 只递交一次，不管有多少子进程退出。
2. **一次 wait() 不够**：处理函数调用一次 `wait()` 可能只回收一个子进程，剩余僵尸无法再触发处理函数。
3. **循环 waitpid 必须**：使用 `while (waitpid(-1, &status, WNOHANG) > 0)`，确保回收所有子进程。
4. **信号递交的不确定性**：SIGCHLD 被递交的次数取决于进程终止的时序和系统调度。

> **一句话总结**：  
> 为防止僵尸进程，SIGCHLD 处理函数必须循环回收所有终止的子进程，单次 wait() 或 waitpid() 调用不足以保证安全。

### 总结

(1) 当fork 子进程时，必须捕获SIGCHLD 信号；

(2) 当捕获信号时，必须处理被中断的系统调用；

(3) SIGCHLD 的信号处理函数必须正确编写，应使用waitpid 函数以免留下僵死进程。

## 5.11 accept 返回前连接中止

### 三次握手完成后客户端 RST 导致 accept() 返回错误

在 TCP 服务器中，一个连接完成三次握手后会进入内核维护的 **已完成连接队列（accept queue）**。此时连接已经建立成功，但服务器应用层尚未调用 accept() 来取出该连接。

如果客户端在这个时刻突然发送 **RST**（例如程序崩溃、异常退出、复位连接等），那么这个连接已在完成队列中但又被对端中止。如何处理这种情况根据不同系统有不同的策略。

###  BSD 系列系统的行为

在 FreeBSD、macOS 等 BSD 系统中：

- 内核会在 TCP 层静默丢弃这种已建立但被 RST 的连接。
- 服务器应用层完全不会察觉该连接。
- accept() 不会返回错误，就像该连接从未出现过一样。

###  SVR4 / POSIX 系统的行为

在 SVR4、Solaris 以及部分符合 POSIX 的系统中：

- 已完成队列中的连接在客户端发送 RST 后仍保留一个“已中止”的记录。
- 当服务器应用层调用 accept() 时，内核发现该连接已经被中止。
- 因此，accept() 返回错误。

POSIX 明确规定此时必须返回：

- **ECONNABORTED**（software caused connection abort）

###  为什么必须返回 ECONNABORTED，而不是 EPROTO？

早期 SVR4 内核返回 EPROTO，但此错误还用于 Streams 子系统的“致命协议错误”。  
如果客户端主动复位连接也返回 EPROTO，服务器将无法区分：

- 是否应该继续 accept()
- 是否出现真正的协议致命问题

因此 POSIX 选择使用 ECONNABORTED，使服务器能够安全地忽略这种中止。

###  服务器正确的处理方式

服务器应当忽略 ECONNABORTED，然后继续循环调用 accept()：

```c
    for (;;) {
        socklen_t len = sizeof(cliaddr);
        int connfd = accept(listenfd, (struct sockaddr *)&cliaddr, &len);
        if (connfd < 0) {
            if (errno == ECONNABORTED)
                continue;   // 忽略并继续
            else
                err_sys("accept error");
        }
        handle(connfd);
    }
```

###  总结

- 即使三次握手已完成，客户端仍可能在 accept 前 RST 连接。
- BSD 系统静默丢弃，应用不可见。
- POSIX 系统使 accept 返回 ECONNABORTED。
- 服务器必须忽略 ECONNABORTED 并继续 accept()。
- 这是编写健壮网络服务器的基本要求。

## 5.12 服务器进程终止

    现在启动我们的客户/服务器对，然后杀死服务器子进程。这是在模拟服务器进程崩溃的情形

当FIN到达套接字时，客户正阻塞在fgets 调用上。客户实际上在应对两个描述符——套接字和用户输入，它不能单纯阻塞在这两个源中某个特定源的输入上（正如目前编写的str_cli 函数所为），而是应该阻塞在其中任何一个源的输入上。事实上这正是select 和poll 这两个函数的目的之一，我们将在第6章中讨论它们。我们在6.4节重新编写str_cli 函数之后，一旦杀死服务器子进程，客户就会立即被告知已收到FIN。

有一个问题之前一直在纠结：**该示例是服务器不够健壮还是客户端程序不够健壮？**， 答案显而易见：客户端程序不够健壮。不是服务器逻辑返回 RST，是 TCP 协议栈返回 RST， 所以这不是“服务器不够健壮”，而是你让服务器暴死导致的一种必然协议行为。客户在收到 FIN 后，仍然正常写数据，但没有检测服务器已经终止，也没有处理 RST 和 SIGPIPE，所以表现为“傻乎乎继续写 → 崩掉”。 **epoll/select 并不能“解决”FIN/RST 问题，它们只是让客户端能够及时发现连接已终止，从而做出正确处理，从应用层上“更健壮”。**

```c
// client 读入读出函数示例
void
str_cli(FILE *fp, int sockfd)
{
	char	sendline[MAXLINE], recvline[MAXLINE];

	while (Fgets(sendline, MAXLINE, fp) != NULL) {

		Writen(sockfd, sendline, strlen(sendline));

		if (Readline(sockfd, recvline, MAXLINE) == 0)
			err_quit("str_cli: server terminated prematurely");

		Fputs(recvline, stdout);
	}
}
```

下面通过一个典型的 TCP 并发服务器实验，观察当服务器子进程被强制杀死时，TCP 四次挥手与 RST 产生的具体过程。服务器与客户端均运行在同一台主机上，基于 UNIX 网络编程环境。

#### 一、实验步骤与事件顺序

##### (1) 正常连接建立与回射
启动服务器与客户端，客户端输入一行文本，服务器子进程回射这行数据。连接建立正常，交互正常。

流程：
1. 客户端键入文本
2. str_cli 调用 writen() 发送数据
3. 服务器子进程回射数据
4. 客户端 readline() 读取数据

连接状态：ESTABLISHED

---

##### (2) 强制终止服务器子进程
使用 kill 命令终止服务器子进程。当子进程被 kill 时，内核自动关闭所有文件描述符，包括该 TCP 连接对应的 socket。

关闭 socket 导致：
- 服务器 TCP 发送 FIN
- 客户端 TCP 回复 ACK

这就是 TCP 正常终止的前半部分（三次挥手的前两步）。

注意：即使是 kill，只要关闭由进程持有的 socket，TCP 行为仍然是“正常关闭”。

---

##### (3) 父进程接收 SIGCHLD
子进程退出后，内核向父进程发送 SIGCHLD。父进程的信号处理函数执行 waitpid() 清理子进程避免僵尸进程。

信号事件不会干扰 TCP 状态机。

---

##### (4) 客户端仍在阻塞状态
客户端此时阻塞在 fgets() 等待用户再次输入，应用层没有意识到 FIN 已经到达。

TCP 层逻辑：
- 收到 FIN → 服务器不再发送数据
- 但客户端仍可继续发送数据

客户端 socket 状态：CLOSE-WAIT

---

##### (5) 使用 netstat 观察状态
在另一个终端执行：

netstat -an

可看到客户端进入 CLOSE-WAIT。

服务器 socket 已消失，因为子进程已退出。

---

#### 二、继续输入数据：出现 RST

##### (6) 客户端再次输入数据
用户输入 another line，客户端调用 writen() 继续发送数据。

为什么 TCP 允许发送？
- FIN 只表示“对端发送方向关闭”
- TCP 支持半关闭（half-close）
- 不影响另一端发送数据

TCP 设计允许：
一方关闭自己写方向，但仍可读取对方发送的数据。

---

##### (7) 服务器返回 RST
服务器进程已经不存在，socket 已关闭。当服务器 TCP 收到数据但找不到对应 socket 时，发送 RST。

行为：
- 收到数据 → 无 socket → RST

可用 tcpdump 验证。

---

##### (8) 客户端看不到 RST
客户端代码中，writen() 后立即调用 readline()。

由于之前 FIN 已被 TCP 层缓存，readline() 立即返回 0（EOF），因此应用层不会看到 ECONNRESET。

原因：
- FIN → read 返回 0（EOF）
- RST → 需要下一次 I/O 才暴露错误
- 此时 readline 已返回 EOF

客户端错误打印：
server terminated prematurely

并退出，关闭所有描述符。

---

#### 三、核心行为总结

##### 1. FIN 与 RST 的关系
子进程被 kill → socket close → FIN
客户端继续发送 → 服务器发送 RST

所以可能出现：
FIN → RST

---

##### 2. 客户端可见行为顺序
客户端看到的是：
第一次读：EOF（来自 FIN）
RST 不会影响第一次 read 行为

---

##### 3. TCP 状态变化
客户端：
ESTABLISHED
→ 收到 FIN → CLOSE-WAIT
→ close → LAST-ACK/CLOSED

服务器：
socket 已删除

---

#### 四、结论

    kill 触发 close(fd)，close(fd) 触发 FIN，这是 TCP 的正常关闭路径。只有当 FIN 后对方继续发数据，而本端没有进程接收时，才会返回 RST。

- 子进程被 kill 后，TCP 会正常发送 FIN
- FIN 只表示“发送方向关闭”，并不阻止对端写
- 客户端可以继续发送数据
- 服务器 socket 不存在时会返回 RST
- 应用层可能先看到 EOF，再看到 RST
- 正确处理 EOF 和异常终止是网络编程必须考虑的问题

该示例展示了 TCP 半关闭行为、进程异常退出影响，以及 FIN 与 RST 的细微区别。

## 5.13 SIGPIPE 信号

当一个进程向某个已收到RST的套接字执行写操作时，内核向该进程发送一个SIGPIPE 信号。该信号的默认行为是终止进程，因此进程必须捕获它以免不情愿地被终止。

当向一个无法接收数据的套接字执行写操作时，内核会返回错误并发送 SIGPIPE 信号。具体来说，如果对端已经关闭接收端（例如连接被完全关闭、对端发送了 RST），写操作的数据无法送达，write()/send() 会立即返回 -1，errno 设为 EPIPE，同时内核向进程发送 SIGPIPE 信号（默认会终止进程）。如果本地已经关闭了写半部（调用了 shutdown(sock, SHUT_WR) 或套接字已关闭），继续执行写操作也会产生同样的行为：返回 -1、设置 EPIPE 并触发 SIGPIPE。需要明确的是，仅仅收到对端发送的 FIN（即对端关闭其写半部、连接处于半关闭状态）不会影响本地的写操作，本地仍然可以继续发送数据，不会产生 SIGPIPE 信号。

```c
void
str_cli(FILE *fp, int sockfd)
{
	char	sendline[MAXLINE], recvline[MAXLINE];

	while (Fgets(sendline, MAXLINE, fp) != NULL) {

        Writen(sockfd, sendline, strlen(sendline));  // 对端发送 FIN 后仍可写（半关闭状态）

        sleep(1);

        Writen(sockfd, sendline, strlen(sendline));  // 对端已发送 RST，再写将触发 EPIPE/SIGPIPE

		if (Readline(sockfd, recvline, MAXLINE) == 0)
			err_quit("str_cli: server terminated prematurely");

		Fputs(recvline, stdout);
	}
}
```

### 总结

    SIGPIPE 信号是 UNIX 网络编程模型中不可忽视的一部分。其语义包含了：

1. 使用 TCP 半关闭机制的设计理念
2. TCP 中的“有序结束” vs “异常中止”
3. 系统层面避免错误传播的哲学
4. UNIX 管道与网络程序错误处理的统一机制
5. 应用程序应当显式处理网络异常

在现代网络服务器中，“忽略 SIGPIPE 并通过 errno 判断错误”是最常见的方式。

## 5.14 服务器主机崩溃

### 当服务器主机崩溃时会发生什么（服务器不可达）

当服务器主机 **直接崩溃**（不是正常关机）时，已有 TCP 连接不会收到任何 FIN 或 RST，因为操作系统没有机会正常关闭套接字。当客户端继续发送数据时，行为如下：

1. **客户端发送数据并等待响应**  
   `writen()` 将数据交给客户端 TCP，客户端阻塞在 `readline()` 等待服务器回射。

2. **服务器无响应**  
   客户端 TCP **持续重传**该数据分节，试图收到服务器的 ACK。源自 Berkeley 的 TCP 实现通常会重传 12 次，总计约等待 9 分钟左右。

3. **最终放弃并返回错误**  
   如果服务器仍无响应，客户端 TCP 放弃重传，并返回错误给应用层。根据情况不同可能返回：
   - **ETIMEDOUT**：服务器没有任何响应，超时。
   - **EHOSTUNREACH** 或 **ENETUNREACH**：中间路由器返回 ICMP "destination unreachable" 消息。

因此，当服务器发生崩溃时，并不会立即导致客户端收到错误，而是客户端 TCP 在多次重传无果后才判断连接失败。

### 总结
1. 尽管我们的客户最终还是会发现对端主机已崩溃或不可达，不过有时候我们需要比不得不等待9分钟更快地检测出这种情况。所用方法就是对readline 调用设置一个超时，我们将在14.2节讨论这一点。
2. 如果我们不主动向它发送数据也想检测出服务器主机的崩溃，那么需要采用另外一个技术，也就是我们将在7.5节讨论的SO_KEEPALIVE 套接字选项。

## 5.16 服务器主机关机

    SYN 发到未监听端口时：如果主机在线，立即返回 RST；如果主机不在线，则重传超时或收到 ICMP 不可达。

Unix系统关机时，init 进程通常先给所有进程发送SIGTERM 信号（该信号可被捕获），等待一段固定的时间（往往在5～20秒），然后给所有仍在运行的进程发送SIGKILL 信号（该信号不能被捕获）。这么做留给所有运行的进程一小段时间来清除和终止。如果我们不捕获SIGTERM 信号并终止，我们的服务器将由SIGKILL 信号终止。 ⑤ 当服务器子进程终止时，它的所有打开着的描述符都被关闭，随后发生的步骤与5.12节中讨论过的一样。正如那一节所述，我们必须在客户中使用select 或poll 函数，使得服务器进程的终止一经发生，客户就能检测到。



略

## 5.18 数据格式

直接发送 C 原生类型或结构体跨网络是有风险的，会受到字节序、类型大小和结构布局差异影响。安全做法是使用文本传输或定义统一的外部二进制数据格式。

### 问题来源

在 TCP 通信中直接发送结构体存在隐患：不同平台的字节序（大小端）、对齐方式、类型大小不一致，导致同样的结构在网络上解析出不同结果。尤其在跨平台或跨编译器场景下，这些差异会造成数据错乱、解析失败，调试成本极高。

### 解决方案

最简单可靠的方法是使用文本协议：把数据序列化为字符串发送，例如通过 sprintf() 格式化发送 "12345\n"，接收端使用 scanf() 或 strtol() 解析。字符串形式天然规避了字节序和对齐差异，实现跨平台稳定通信。

### 开源项目的常见方式

成熟项目普遍避免直接传结构体，转而采用协议格式。例如 Nginx 使用严格定义的二进制协议和网络序（big-endian），并手工序列化字段，确保在任何平台解析一致；Redis 选择纯文本协议（RESP），简单、可读、跨平台自然无差异。这些方案都强调“协议优先”，而不是依赖编译器内存布局。