---
title: unp&chapter3 套接字简述
author: xyx
date: 2025-11-21 13:33:00 +0800
categories: [justxyx, net-programming]
tags:
math: true
---

## 3.2 套接字地址结构

### ipv4 结构


```c
struct sockaddr_in
  {
    __SOCKADDR_COMMON (sin_);
    in_port_t sin_port;			    /* Port number.  */
    struct in_addr sin_addr;		/* Internet address.  */

    /* Pad to size of `struct sockaddr'.  */
    unsigned char sin_zero[sizeof (struct sockaddr) -
			   __SOCKADDR_COMMON_SIZE -
			   sizeof (in_port_t) -
			   sizeof (struct in_addr)];
  };


typedef uint32_t in_addr_t;
typedef uint16_t in_port_t;
struct in_addr
  {
    in_addr_t s_addr;
  };

```

注意点：
1. struct sockaddr_in中的IP地址有两种访问方式：serv.sin_addr（结构体）和 serv.sin_addr.s_addr（整数）。尽管两者指向同一块内存，但它们的C语言数据类型完全不同。这是最关键的区别，因为编译器对结构体类型和整数类型的处理方式截然不同。在函数调用时（如 inet_pton或 bind），必须传入函数所期望的特定类型的指针或值。错误地混用类型（例如，需要整数却传入了结构体）将导致编译错误或未定义行为。因此，绝大多数需要直接操作IP地址数值的场景（如设置、比较），都应使用 serv.sin_addr.s_addr这个整数形式，以确保类型正确和程序健壮性。
2. 为什么`struct in_addr sin_addr' 要有一层包装？ 包装 struct in_addr 的目的，是建立一种跨所有协议族的统一抽象：“地址不是一个原始值，而是一个可替换、可扩展、具有专用语义的对象”。

### 通用套接字地址结构

```c
struct sockaddr
  {
    __SOCKADDR_COMMON (sa_);	/* Common data: address family and length.  */
    char sa_data[14];		/* Address data.  */
  };
```

**为什么要通用地址结构？ 下面这段伪码给出， 即使sa_data[14] 装不下ipv6地址**

```c
int bind(int sockfd, const struct sockaddr *addr, socklen_t addrlen);


switch (addr->sa_family) {
    case AF_INET:      // IPv4
        struct sockaddr_in *addr4 = (struct sockaddr_in *)addr;
        process_ipv4_bind(sockfd, addr4, addrlen);
        break;
    case AF_INET6:     // IPv6
        struct sockaddr_in6 *addr6 = (struct sockaddr_in6 *)addr;
        process_ipv6_bind(sockfd, addr6, addrlen);
        break;
    case AF_UNIX:      // Unix Domain Socket
        struct sockaddr_un *addr_un = (struct sockaddr_un *)addr;
        process_unix_bind(sockfd, addr_un, addrlen);
        break;
    default:
        return -EAFNOSUPPORT;
}
```

### ipv6 结构

```c
struct sockaddr_in6
  {
    __SOCKADDR_COMMON (sin6_);
    in_port_t sin6_port;	/* Transport layer port # */
    uint32_t sin6_flowinfo;	/* IPv6 flow information */
    struct in6_addr sin6_addr;	/* IPv6 address */
    uint32_t sin6_scope_id;	/* IPv6 scope-id */
  };
```

### 新的通用套接字地址结构

    sockaddr_storage 是为了解决 IPv6 出现后，旧 sockaddr 不够大、对齐不安全、无法通用的问题，因此系统引入新的“通用套接字地址”结构。所有网络代码应使用它来兼容 IPv4/IPv6。

```c
struct sockaddr_storage
  {
    __SOCKADDR_COMMON (ss_);	/* Address family, etc.  */
    char __ss_padding[_SS_PADSIZE];
    __ss_aligntype __ss_align;	/* Force desired alignment.  */
  };
```

## 3.3 值—结果参数

**理解套接字 API 中参数的传递方式（值/结果/值—结果），尤其是地址结构如何在进程和内核之间流动，以及为什么要这样设计。**

- 返回值主要用于状态或单一数据

- 值—结果参数才是理解套接字 API 参数设计的关键


### 1. 值、结果、值—结果参数的概念

| 名称 | 传入前 | 传回后 | 举例 | 用途 |
|------|--------|--------|-------|-------|
| 值参数（value argument） | 调用者提供的“输入值” | 函数不会修改它 | socket(), connect() 的参数 | 输入 |
| 结果参数（result argument） | 调用时内容无所谓 | 调用后函数写入结果 | accept() 的 *addr | 输出 |
| 值—结果参数（value–result argument） | 调用前需要传入初始值 | 调用后函数也会修改它 | accept() 的 *addrlen | 输入 + 输出 |

- **值参数（Value）**：  
  函数只读传入的数据，调用后实参不变。

- **结果参数（Result / Output）**：  
  函数通过指针修改实参的值，返回结果给调用者。

- **值—结果参数（Value-Result / In-Out）**：  
  函数既参考原值，又返回修改结果。  
  **典型例子**：`getsockname()`, `accept()`, `recvfrom()` 等。

> 这是理解套接字 API 参数设计的基础，也是 C 语言网络编程中常见模式。

---

### 2. 套接字地址结构传递方向

  TCP/UDP 套接字 API 之所以有很多看起来奇怪的 sockaddr 传入传出方式，其实根本原因只有一个：地址结构在不同调用中要么是“你告诉内核目标地址”，要么是“内核告诉你实际地址”，API 必须准确表达这个方向关系。
  整个 socket API 的设计都是围绕 “地址” 在 用户 ↔ 内核 之间的流向 来组织的。

- **用户进程 → 内核**：用户告诉内核自己要操作哪个地址  
  - 函数：`bind()`、`connect()`、`sendto()`

- **内核 → 用户进程**：内核返回实际地址信息  
  - 函数：`accept()`、`recvfrom()`、`getsockname()`、`getpeername()`

> 这种区分帮助理解函数的参数是“输入”“输出”还是“输入输出”。

---

### 3. 设计理念

- **保持统一接口**：所有 socket 地址通过 `struct sockaddr*` 传递，无论 IPv4/IPv6。
- **兼顾可扩展性**：通过值—结果参数模式，函数可以同时返回多种信息（如长度、地址等）。
- **类型安全和 ABI 兼容**：用结构体封装 IP 地址、端口、flow info 等，方便系统调用处理。


## 3.4 字节排序函数

```c
0x12345678

// 大端
地址 0x00: 0x12
地址 0x01: 0x34
地址 0x02: 0x56
地址 0x03: 0x78

// 小端
地址 0x00: 0x78
地址 0x01: 0x56
地址 0x02: 0x34
地址 0x03: 0x12
```

- 大端 = 写数字的时候从左到右（高位先写）
- 小端 = 写数字的时候从右到左（低位先写）


**网络协议规定的标准字节顺序为大端字节序，用于 在网络上发送数据**
**在那些与网际协议所用字节序（大端）相同的系统中，这四个函数通常被定义为空宏。**


```c
/*
 * 字节序转换函数说明（来自 UNP 3.4 节）
 *
 * 函数：
 *   uint16_t htons(uint16_t host16bitvalue);
 *   uint32_t htonl(uint32_t host32bitvalue);
 *     ——返回对应的“网络字节序”值（Network Byte Order = 大端）
 *
 *   uint16_t ntohs(uint16_t net16bitvalue);
 *   uint32_t ntohl(uint32_t net32bitvalue);
 *     ——返回对应的“主机字节序”值（Host Byte Order）
 *
 * 函数名中的字母含义：
 *   h = host（主机字节序）
 *   n = network（网络字节序）
 *   s = short（原指 16 位整型：TCP/UDP 端口号）
 *   l = long  （原指 32 位整型：IPv4 地址）
 *
 * “short / long” 命名来自 4.2BSD 在 Digital VAX 架构上的历史遗留。
 * 在当年，short = 16 bit，long = 32 bit。
 *
 * 即使在 64 位平台（例如 Digital Alpha）上，C 语言 long 是 64 bit，
 * 但 htonl()/ntohl() 仍然只处理 32 位数据（主要用于 IPv4）。
 *
 * 总结：
 *   htons / ntohs 处理 16 位数据；
 *   htonl / ntohl 处理 32 位数据；
 *   与当前 CPU 是 32 位、64 位无关，与 C 的 long 类型宽度也无关。
 *
 * 调用这些函数的意义：
 *   无论主机是大端还是小端，都能保证正确的网络协议数据格式。
 */
 ```

 ## 3.5 字节操纵函数

    不太推荐使用strings 头文件了， 除非你在维护非常老的 BSD/Linux 代码。


## 3.6 inet_aton、inet_addr 和 inet_ntoa 函数

  inet_pton 和 htonl 都用于网络编程中处理数据的网络字节序，但作用不同：inet_pton 用于将文本形式的 IP 地址（如 "192.168.1.1"）转换成网络字节序的二进制表示，方便填入 sockaddr_in 等结构中；而 htonl 用于将主机字节序的整数（如 IP 地址的整数表示或其他 32 位数值）转换为网络字节序，用于在不同字节序的主机之间保持数据一致。简单来说，inet_pton 是 格式转换，htonl 是 字节序转换。

| API        | 功能                         | 方向            | 是否推荐                   |
|------------|------------------------------|-----------------|----------------------------|
| inet_aton  | 字符串 → IPv4 二进制地址     | 文本 → 网络序   | 推荐（更安全）             |
| inet_addr  | 字符串 → IPv4 二进制地址     | 文本 → 网络序   | 不推荐（错误码冲突）       |
| inet_ntoa  | IPv4 二进制地址 → 字符串     | 网络序 → 文本   | 不推荐（返回静态区）       |


1. inet_aton 函数有一个没写入正式文档中的特征：如果addrptr指针为空，那么该函数仍然对输入的字符串执行有效性检查，但是不存储任何结果。
2. inet_addr 有严重漏洞， 不推荐使用。
3. inet_ntoa 函数将一个32位的网络字节序二进制IPv4地址转换成相应的点分十进制数串。由该函数的返回值所指向的字符串驻留在静态内存中。这意味着该函数是不可重入的

**现代网络编程强烈建议使用 inet_pton / inet_ntop ~**

```c

int main() {
    const char *ip_str = "192.168.1.100";
    struct in_addr addr;

    // 转换字符串 → 网络地址
    int ret = inet_aton(ip_str, &addr);
```

## 3.7 inet_pton 和 inet_ntop函数

    现代网络编程推荐 inet_pton / inet_ntop，兼容性更好，更安全。

```c
int main() {
    char ipv4_str[] = "192.168.1.100";
    char ipv6_str[] = "2001:db8::1";
    struct in_addr addr4;
    struct in6_addr addr6;
    char buf[INET6_ADDRSTRLEN];

    // IPv4: 文本 -> 二进制
    if (inet_pton(AF_INET, ipv4_str, &addr4) != 1) {
        printf("inet_pton IPv4 error\n");
        return 1;
    }

    // IPv4: 二进制 -> 文本
    if (inet_ntop(AF_INET, &addr4, buf, sizeof(buf)) == NULL) {
        printf("inet_ntop IPv4 error\n");
        return 1;
    }
```

## 3.8 

    略

## 3.9 readn、writen 和 readline 函数

### 核心现象

- `read(fd, buf, n)` / `write(fd, buf, n)` **不保证一次就读或写 n 个字节**。
- 返回的字节数可能 **小于请求的数量**，这不是出错。
- 原因：内核中套接字缓冲区可能已达到极限。

---

### 具体情况

| 操作  | 阻塞状态        | 可能返回情况 |
|-------|----------------|---------------|
| `read`  | 阻塞或非阻塞  | 返回 < n 字节（TCP 收到的数据不足 n 字节） |
| `write` | 阻塞          | 通常写完 n 字节（除非缓冲区满） |
| `write` | 非阻塞        | 可能返回 < n（缓冲区满，只写入部分字节） |

> 注意：在某些 Unix 系统中，写入管道超过 4096 字节也可能出现类似部分写入的情况。


### 扩展： readn、writen 和 readline

```c
// 保证尽量读完 n 字节。
// 遇到 EOF 可能返回不足字节数。
// 避免 TCP 分段导致的部分读取问题。
ssize_t readn(int fd, void *vptr, size_t n) {
    size_t nleft = n;
    ssize_t nread;
    char *ptr = vptr;

    while (nleft > 0) {
        if ((nread = read(fd, ptr, nleft)) < 0) {
            if (errno == EINTR)
                nread = 0; // 被信号中断，继续读
            else
                return -1; // 其他错误
        } else if (nread == 0)
            break; // EOF

        nleft -= nread;
        ptr += nread;
    }

    return (n - nleft); // 实际读取的字节数
}

// 保证尽量写完 n 字节。
// 对阻塞套接字通常一次就能写完；对非阻塞套接字可能分多次写。
// 解决 TCP 分段导致的部分写入问题。
ssize_t writen(int fd, const void *vptr, size_t n) {
    size_t nleft = n;
    ssize_t nwritten;
    const char *ptr = vptr;

    while (nleft > 0) {
        if ((nwritten = write(fd, ptr, nleft)) <= 0) {
            if (nwritten < 0 && errno == EINTR)
                nwritten = 0; // 被信号中断，继续写
            else
                return -1; // 其他错误
        }

        nleft -= nwritten;
        ptr += nwritten;
    }

    return n;
}

//一次读取一个字节，直到遇到换行符。
//适合文本协议。
//可以用缓冲区优化减少系统调用（UNP 里用 readline_buf）。
ssize_t readline(int fd, void *vptr, size_t maxlen) {
    char *ptr = vptr;
    ssize_t n, rc;
    char c;

    for (n = 1; n < maxlen; n++) {
        if ((rc = read(fd, &c, 1)) == 1) {
            *ptr++ = c;
            if (c == '\n')
                break;
        } else if (rc == 0) {
            if (n == 1)
                return 0; // EOF
            else
                break;
        } else {
            if (errno == EINTR)
                continue; // 被信号中断
            return -1;    // 其他错误
        }
    }

    *ptr = 0; // 字符串结尾
    return n;
}
```

### readline 函数的性能与安全注意事项


#### 1️⃣ 性能问题

- UNP 提供的 `readline` 函数是 **每读取一个字节就调用一次系统 `read`**。
- 这种实现非常低效，因此在源码中标注了：
  > “PAINFULLY SLOW（极端地慢）”

- 面对从套接字读取文本行的需求，使用 **标准 I/O 函数库（stdio）** 缓冲数据似乎很诱人，但存在潜在危险。

---

#### 2️⃣ stdio 缓冲的风险

    网络套接字不建议用 stdio

- stdio 缓冲机制是不可见的，程序无法直接察觉缓冲区中是否存有未处理的数据。
- 在客户端/服务器协议中，如果对端程序未严格遵循协议，缓冲区可能隐藏未预期的数据。
- **防御性编程原则**：
  - 应检查并修正网络数据传送中的异常情况
  - 尽量从缓冲区而非文本行角度处理数据
- 使用 stdio 缓冲虽然提升性能，但可能导致：
  - 数据被“悄悄”缓存
  - 程序无法检测未预期的数据
  - 出现隐蔽缺陷或安全问题

---

#### 3️⃣ 网络协议实例

- 常见基于文本行的协议：
  - **SMTP**、**HTTP**、**FTP**（控制连接）、**finger**
- 这些协议要求逐行处理，但推荐：
  - 先读取缓冲区数据
  - 检查缓冲区是否含完整行
  - 再提取文本行

---

#### 4️⃣ 编程建议

- 避免直接依赖文本行缓冲来读取数据。
- 编写程序时应：
  1. 从套接字读取缓冲区数据
  2. 按需解析文本行
  3. 处理可能的未预期数据

- 这样既保证性能，也保持协议的健壮性和防御性。