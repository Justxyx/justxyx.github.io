---
title: Linux高性能服务器编程--高级io
author: xyx
date: 2022-4-6 20:33:00 +0800
categories: [C++, linux-os]
tags: 
math: true
---

## 0. pipe 与 dup

### 1. pipe

默认为阻塞，
` int socketpair(int domain, int type, int protocol, int sv[2]);`

### 2. dup 

```c
int dup(int oldfd);
int dup2(int oldfd, int newfd);
```

### 3.demo

```c
int main(int argc,char *argv[]){
    if (argc<=2){
        printf("argc error");
        return -1;
    }

    const char* ip = argv[1];
    int port = atoi(argv[2]);

    struct sockaddr_in address;
    bzero(&address,sizeof(address));
    address.sin_family = AF_INET;
    inet_pton(AF_INET,ip,&address.sin_addr);
    address.sin_port = htons(port);

    int sock = socket(PF_INET,SOCK_STREAM,0);
    assert(sock >= 0);

    int ret = bind(sock,(struct sockaddr*)&address,sizeof(address));
    assert(ret != -1);

    ret = listen( sock, 5 );
    assert( ret != -1 );

    struct sockaddr_in client;
    socklen_t client_addrlength = sizeof(client);
    int connfd = accept(sock,(struct sockaddr*)&client,&client_addrlength);
    if (connfd < 0){
        perror("accept error");
    } else{
        close(STDOUT_FILENO);
        dup(connfd);
        printf("abcd\n");
        close(connfd);
    }
    close(sock);
    return 0;
}
```


## 1. readv 与 writev

readv: 将数据从文件描述符读到分散的内存块中。
writev: 将多块分散的内存数据一并写入到文件描述符中。

**上面这么说可能有点抽象，这样举个例子比较好理解，Web服务器解析到一个请求后，要响应一个状态行、多个头部字段、以及返回的html文档内容。前两块可以放置在一块内存中，html文档放在另外一块内存中。我们并不需要将两个部分的内容拼接再发送，而是可以使用writev将他们同时写出**。

### 一个demo，web服务器上的集中写

```c
// readv 核心代码
struct iovec iv[2];
iv[0].iov_base = header_buf;
iv[0].iov_len = strlen(header_buf);
iv[1].iov_base = file_buf;
iv[1].iov_len = strlen(file_buf);
```

完整代码：
```c
int main(int argc,char *argv[]){
    if (argc <= 3){
        printf("argc nums error");
        return 1;
    }

    const char* ip = argv[1];   // ip
    int port = atoi(argv[2]);  // 端口
    const char* file_name = argv[3];     // 目标文件

    struct sockaddr_in address;
    bzero(&address,sizeof(address));
    address.sin_family = AF_INET;
    inet_pton(AF_INET,ip,&address.sin_addr);   // ip地址转换函数  绑定ip
    address.sin_port = htons(port);         // 绑定端口

    int sock = socket(PF_INET,SOCK_STREAM,0);   // tcp 链接sock
    assert(sock >- 0);

    int ret = bind(sock,(struct sockaddr*)&address,sizeof(address));  // sockt 与ip端口绑定
    assert(ret != -1);

    ret = listen(sock,5);  // 开始监听
    assert(ret != -1);

    struct sockaddr_in client;  // 客户端sockt
    socklen_t client_addrlength = sizeof(client);
    int connfd = accept(sock,(struct sockaddr*)&client,&client_addrlength);
    if (connfd < 0){
        printf("errno is %d\n",errno);
    } else{
        char header_buf[BUFFER_SIZE];
        char *file_buf;
        struct stat file_stat;
        bool valid = true;
        int len = 0;
        if (stat(file_name,&file_stat) < 0){
            valid = false;
        } else{
            if (S_ISDIR(file_stat.st_mode)){
                valid = false;    // 目标文件是一个目录
            }else if (file_stat.st_mode & S_IROTH) // 当前用户有读取目标文件的权限
            {
                int fd = open(file_name,O_RDONLY);
                file_buf = new char[file_stat.st_size+1];
                memset(file_buf,'\0',file_stat.st_size+1);  // 初始化
                if (read(fd,file_buf,file_stat.st_size +1) < 0){
                    valid = false;
                }
            } else{
                valid = false;
            }
        }

        //如果目标文件夹有效，则发送正常的http应答
        if (valid){
            ret = snprintf( header_buf, BUFFER_SIZE-1, "%s %s\r\n", "HTTP/1.1", status_line[0] );
            len += ret;
            ret = snprintf( header_buf + len, BUFFER_SIZE-1-len,
                            "Content-Length: %d\r\n", file_stat.st_size );
            len += ret;
            ret = snprintf( header_buf + len, BUFFER_SIZE-1-len, "%s", "\r\n" );

            struct iovec iv[2];
            iv[0].iov_base = header_buf;
            iv[0].iov_len = strlen(header_buf);
            iv[1].iov_base = file_buf;
            iv[1].iov_len = strlen(file_buf);
            ret = writev(connfd,iv,2);
        } else{
            ret = snprintf( header_buf, BUFFER_SIZE-1, "%s %s\r\n", "HTTP/1.1", status_line[1] );
            len += ret;
            ret = snprintf( header_buf + len, BUFFER_SIZE-1-len, "%s", "\r\n" );
            send( connfd, header_buf, strlen( header_buf ), 0 );
        }
        close(connfd);
        delete[] file_buf;
    }
    close(sock);
    return 0;
}
```


## 2. senfile 函数（零拷贝）

函数原型： `ssize_t sendfile(int out_fd, int in_fd, off_t *offset, size_t count);`

优势：Because this copying is done within the kernel,（完全在内核中）。

限制：out_fd must refer to a socket.  Since Linux 2.6.33 it can be any file.  in_fd 为文件，out_fd 为socket。

**sendfile几乎是专门为网络上传输文件而设计。**

## demo

```c

int main(int argc,char* argv[]){
    if (argc <= 3){
        printf("argc nums error");
        return 1;

        const char* ip = argv[1];
        int port = atoi(argv[2]);
        const char *file_name = argv[3];

        int filefd = open(file_name,O_RDONLY);
        assert(filefd > 0);
        struct stat stat_buf;
        fstat(filefd,&stat_buf);

        struct sockaddr_in address;
        bzero(&address,sizeof(address));
        address.sin_family = AF_INET;
        inet_pton(AF_INET,ip,&address.sin_addr);
        address.sin_port = htons(port);

        int sock = socket(PF_INET,SOCK_STREAM,0);
        assert(sock >= 0);

        int ret = bind(sock,(struct sockaddr*)&address,sizeof(address));
        assert(ret != -1);

        ret = listen(sock,5);
        assert(ret != -1);

        struct sockaddr_in client;
        socklen_t client_addrlength = sizeof(client);
        int connfd = accept(sock,(struct sockaddr*)&client,&client_addrlength);
        if (connfd < 0){
            printf("errno is");
        } else{
            sendfile(connfd,filefd,NULL,stat_buf.st_size);
            close(connfd);
        }
        close(sock);
        return 0;
    }
}
```


## 3. mmap 与 munmap函数

用于申请内存与释放内存，将这段内存可作为进程间通信的共享内存。暂略。


## 4. splice函数

两个文件描述符间的数据移动，**零拷贝操作**。  where one of the file descriptors must refer to a pipe.

### demo

一个零拷贝的回射服务器，将客户端发送的数据原样的返回客户端。

```c

int mian(int argc,char* argv[]){
    if (argc <= 2){
        return 1;
    }

    const char* ip = argv[1];
    int port = atoi(argv[2]);

    struct sockaddr_in address;
    bzero(&address,sizeof(address));
    address.sin_family = AF_INET;
    inet_pton(AF_INET,ip,&address.sin_addr);
    address.sin_port = htons(port);

    int sock = socket(PF_INET,SOCK_STREAM,0);
    assert(sock >= 0);
    int ret = bind(sock,(struct sockaddr*)&address,sizeof(address));
    assert(ret != -1);

    struct sockaddr_in client;
    socklen_t client_addrlength = sizeof(client);
    int connfd = accept(sock,(struct sockaddr*)&client,&client_addrlength);
    if (connfd < 0){
        printf("error");
    } else{
        int pipefd[2];
        assert(ret != -1);
        ret = pipe(pipefd);

        ret = splice(connfd,NULL,pipefd[1],NULL,32768,SPLICE_F_MORE|SPLICE_F_MOVE);
        assert(ret != -1);
        ret = splice( pipefd[0], NULL, connfd, NULL, 32768, SPLICE_F_MORE | SPLICE_F_MOVE );
        assert(ret != -1);
        close(connfd);
    }
    
    close(sock);
    return 0;
}
```

## 4. tee函数

两个管道间的文件描述符之间的复制数据。**零拷贝操作**。

## 5. fcntl函数

根据文件描述符更改属性 

略。

