---
title: p12 Linux高性能服务器编程-- libevent 库
author: xyx
date: 2022-4-20 20:33:00 +0800
categories: [C++, linux-os]
tags: 
math: true
---


## 1. demo1 libevent 的使用 常规事件

### write 客户端

```c
//
// Created by xm on 2022/4/24.
//

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <fcntl.h>
#include <event2/event.h>

void write_cb(evutil_socket_t fd, short what ,void *arg){
    // 写管道
    char buf[1024];
    static int num = 0;
    sprintf(buf,"hello word %d \n",num++);
    write(fd,buf, strlen(buf) + 1);

    sleep(1);
}

// 读管道
int main(int argc,const char* argv[]){

    // open file
    int fd = open("myfifo",O_WRONLY|O_NONBLOCK);
    if (fd == -1){
        perror("open error1111111");
        exit(1);
    }

    // 创建base
    struct event_base *base = NULL;
    base = event_base_new();

    // 创建事件
    struct event* ev = NULL;
    ev = event_new(base,fd,EV_WRITE | EV_PERSIST, write_cb,NULL);  // EV_PERSIST 可持续读 与 just 读一次

    // 添加事件
    event_add(ev,NULL);

    // 事件循环
    event_base_dispatch(base);

    // 释放资源
    event_free(ev);
    event_base_free(base);
    close(fd);

    return 0;
}
```

### read 服务器端

```c
//
// Created by xm on 2022/4/24.
//

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <fcntl.h>
#include <event2/event.h>

void read_cb(evutil_socket_t fd, short what ,void *arg){
    // 读管道
    char buf[1024];
    int len = read(fd,buf,sizeof(buf));
    printf("read event: &s");
    printf("data len = %d, buf = %s\n",len,buf);
    sleep(1);
}

// 读管道
int main(int argc,const char* argv[]){
    unlink("myfifo");
    mkfifo("myfifo",0644);

    // open file
    int fd = open("myfifo",O_RDONLY|O_NONBLOCK);
    if (fd == -1){
        perror("open error");
    }

    // 创建base
    struct event_base *base = NULL;
    base = event_base_new();

    // 创建事件
    struct event* ev = NULL;
    ev = event_new(base,fd,EV_READ | EV_PERSIST, read_cb,NULL);

    // 添加事件
    event_add(ev,NULL);

    // 事件循环
    event_base_dispatch(base);

    // 释放资源
    event_free(ev);
    event_base_free(base);
    close(fd);

    return 0;
}
``` 


## 2. buffer 事件

### 服务器端

```c
//
// Created by xm on 2022/4/24.
//

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <fcntl.h>
#include <event2/event.h>
#include <arpa/inet.h>
#include <event2/listener.h>
#include <event2/bufferevent.h>

// 读回调
void read_cb(struct bufferevent *bev,void *arg){
    char buf[1024] = {0};
    bufferevent_read(bev,buf,sizeof(buf));
    printf("client say : %s\n",buf);

    char *p = "我是服务器 我已经成功的接收到你发送的数据";
    bufferevent_write(bev,p,strlen(p)+1);

    sleep(1);
}

// 写回调
void write_cb(struct bufferevent *bev,void *arg){
    printf(" 我是服务器  我已经成功把数据写回客户端");
}

// 事件回调
void event_cb(struct bufferevent *bev,short events,void *arg){
    if (events & BEV_EVENT_EOF){
        printf("connection closed\n");
    } else if (events & BEV_EVENT_ERROR){
        printf("some other error\n");
    }

    bufferevent_free(bev);
    printf("资源已经被释放");
}

// 监听器回调函数
void cb_listerer(struct evconnlistener *listener,evutil_socket_t fd,struct sockaddr *addr,int len,void *ptr){
    printf("connect new client\n");
    struct event_base *base = (struct event_base*) ptr;

    // 添加新事件
    struct bufferevent *bev;
    bev = bufferevent_socket_new(base,fd,BEV_OPT_CLOSE_ON_FREE);

    // bufferevent 缓冲区设置回调
    bufferevent_setcb(bev,read_cb,write_cb,event_cb,NULL);

    // 启用bufferevent 的 读缓冲
    bufferevent_enable(bev,EV_READ);
}

int main(){
    struct sockaddr_in serv;
    memset(&serv,0,sizeof(serv));
    serv.sin_port = htonl(9876);
    serv.sin_family = AF_INET;
    serv.sin_addr.s_addr = htonl(INADDR_ANY);

    struct event_base *base;
    base = event_base_new();

    struct evconnlistener *listerer; // 监听器
    /*
     * 为什么要传递两个base参数？   cb_listerer（void *ptr） 用来接收第二个base
     */
    listerer = evconnlistener_new_bind(base,cb_listerer,base,LEV_OPT_CLOSE_ON_FREE | LEV_OPT_REUSEABLE,36,
                                       (struct sockaddr*)&serv,sizeof(serv));  // LEV_OPT_REUSEABLE 端口复用   36  链接上限


    // 启动循环监听
    event_base_dispatch(base);
    evconnlistener_free(listerer);
    event_base_free(base);
    return 0;
}
```

### 客户端

```c
//
// Created by xm on 2022/4/24.
//

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <string.h>
#include <fcntl.h>
#include <event2/event.h>
#include <arpa/inet.h>
#include <event2/listener.h>
#include <event2/bufferevent.h>

// 读回调
void read_cb(struct bufferevent *bev,void *arg){
    char buf[1024] = {0};
    bufferevent_read(bev,buf,sizeof(buf));
    printf("client say : %s\n",buf);

    char *p = "我是客户端我已经成功的接收到你发送的数据";
    bufferevent_write(bev,p,strlen(p)+1);

    sleep(1);
}

// 写回调
void write_cb(struct bufferevent *bev,void *arg){
    printf(" 我是客户端  我已经成功把数据发送给服务器");
}

// 事件回调
void event_cb(struct bufferevent *bev,short events,void *arg){
    if (events & BEV_EVENT_EOF){
        printf("connection closed\n");
    } else if (events & BEV_EVENT_ERROR){
        printf("some other error\n");
    }

    bufferevent_free(bev);
    printf("资源已经被释放");
}

// 监听器回调函数
void cb_listerer(struct evconnlistener *listener,evutil_socket_t fd,struct sockaddr *addr,int len,void *ptr){
    printf("connect new client\n");
    struct event_base *base = (struct event_base*) ptr;

    // 添加新事件
    struct bufferevent *bev;
    bev = bufferevent_socket_new(base,fd,BEV_OPT_CLOSE_ON_FREE);

    // bufferevent 缓冲区设置回调
    bufferevent_setcb(bev,read_cb,write_cb,event_cb,NULL);

    // 启用bufferevent 的 读缓冲
    bufferevent_enable(bev,EV_READ);
}

void read_terminal(evutil_socket_t fd,short what,void *arg){
    char buf[1024];
    int len = read(fd,buf,sizeof(buf));

    struct  bufferevent *bev = (struct bufferevent*) arg;
    bufferevent_write(bev,buf,len+1);
}

int main(){


    struct event_base *base;
    base = event_base_new();

    int fd = socket(AF_INET,SOCK_STREAM,0);

    // 通信的fd放到bufferevent中
    struct bufferevent *bev = NULL;
    bev = bufferevent_socket_new(base,fd,BEV_OPT_CLOSE_ON_FREE);

    struct sockaddr_in serv;
    memset(&serv,0,sizeof(serv));
    serv.sin_port = htonl(9876);
    serv.sin_family = AF_INET;
    inet_pton(AF_INET,"127.0.0.1",&serv.sin_addr);

    // 链接到服务器
    bufferevent_socket_connect(bev,(struct sockaddr*)&serv,sizeof(serv));

    // 设置回调
    bufferevent_setcb(bev,read_cb,write_cb,event_cb,NULL);

    // 创建事件
    struct event *ev = event_new(base,STDIN_FILENO,EV_READ | EV_PERSIST,read_terminal,bev);


    // 添加事件
    event_add(ev,NULL);
    event_base_dispatch(base);
    event_free(ev);
    event_base_free(base);


    return 0;
}
```