---
title: Libevent 源码分析
author: xyx
date: 2022-5-16 20:33:00 +0800
categories: [justxyx, net-programming]
tags: 
math: true
---


## 1. 源码组织结构

- event.h

    主要结构体event的声明

- xxx-internal.h

    内部数据结构，对外不可见

- event.c

    libevent框架爱，event整体框架的代码实现

- 对系统IO多路复用机制的封装

    1. epoll.c
    2. select.c
    3. devpoll.c
    4. kqueue.c

- 定时事件管理

    min-heap.h  一个事件为key的小根堆结构

- 信号管理
    signal.c 对信号的处理

- 辅助功能函数

    evtuil.h  evtuil.c  一些辅助函数，类似`socket pair` 和一些时间操作函数

- 日志

    log.h log.c

- 基本数据结构  `compat/sys`下

    1. queue.h  是libevent基本数据结构的实现
    2. _libevent_time.h  对于时间操作结构体的定义

- 实时网络库

    http 与 evdns   http服务器与dns服务器

## 2. Libevent核心：event

### 2.1 基本结构

**核心点在于，1.要么是IO事件，2.要么是信号事件，3.要么是超时事件，本例前面暂时用超时事件来说明，因为其比较简单**。

event.h p121行

```c
#ifndef EVENT_NO_STRUCT
struct event {
    /*
    以下三个字段，都是双向链表节点指针 
    libevent 用双向链表保存IO事件与信号事件
    */
	TAILQ_ENTRY (event) ev_next;   // io事件在链表中的位置
	TAILQ_ENTRY (event) ev_active_next; // libevent将所有激活事件放入active list 中
	TAILQ_ENTRY (event) ev_signal_next; // 信号事件

	unsigned int min_heap_idx;	// 小根堆的索引  对超时事件的管理

	struct event_base *ev_base;   // 该事件所属反应堆的实例

	int ev_fd;   // io事件绑定fd  信号事件绑定signal
	short ev_events;  //  三种事件  IO事件   信号事件 超时事件 
	short ev_ncalls;   // 事件就绪执行时，调用ev_callback的次数
	short *ev_pncalls;	/* Allows deletes in callback */

	struct timeval ev_timeout;   // 超时时间 对超时事件的管理

	int ev_pri;		/* smaller numbers are higher priority */

	void (*ev_callback)(int, short, void *arg);   // 回调函数 函数原型：void (*ev_callback)(int fd, short events, void *arg)
	void *ev_arg;

	int ev_res;		/* result passed to event callback */  当前激活事件的类型
	int ev_flags;
};
```

ev_flags:
```c
#define EVLIST_TIMEOUT 0x01 // event在time堆中 
#define EVLIST_INSERTED 0x02 // event在已注册事件链表中 
#define EVLIST_SIGNAL 0x04 // 未见使用 
#define EVLIST_ACTIVE 0x08 // event在激活链表中 
#define EVLIST_INTERNAL 0x10 // 内部使用标记 
#define EVLIST_INIT 0x80 // event 已被初始化
```

### 2.2 libevent 对event 的管理

每当有event事件转为就绪态时，libevent 就会把它移入到activa event list 中。

### 2.3 事件设置的函数接口 

要向libevent添加一个事件，肯定需要首先设置event对象，libevent提供的函数有以下三种：

1. `event_set`

    - 函数接口`void event_set(struct event *, int, short, void (*)(int, short, void *), void *);`
    - 函数原型：
    - 参数设置：
        1. fd  ev绑定的文件描述符或者信号 对于定时事件，**设置为-1即可**
        2. 事件类型，EV_REAS|EV_PERSIST|EV_SIGNAL 等
        3. 回调函数

2. `event_base_set`

    - 函数接口`int event_base_set(struct event_base *, struct event *);`
    - 如果进程中存在多个event_base，则可以指定event设置不同的event_base

3. `event_priority_set`
    设置优先级

例如，`evtimer_set`函数底层调用的是`event_set`封装的函数，其具体如下：

```c
#define evtimer_set(ev, cb, arg)	event_set(ev, -1, 0, cb, arg)
```


## 3. 事件处理框架

## 3.1 event_base

### 3.2 基本结构

event-internal p49
```c
struct event_base {
    // 可调用evsel->add(evbase, ev)，
	const struct eventop *evsel;  // evsel 指向全局变量static const struct eventop *eventops[] 中的一个 
	void *evbase;
	int event_count;		/* counts number of total events */
	int event_count_active;	/* counts number of active events */

	int event_gotterm;		/* Set to terminate loop */
	int event_break;		/* Set to terminate loop immediately */

	/* active event management */
	struct event_list **activequeues;  // 二级指针 下面有注释详解
	int nactivequeues;

	/* signal handling info */
	struct evsignal_info sig; // 管理信号结构体

	struct event_list eventqueue;  // 链表 所有已经注册的event时间指针
	struct timeval event_tv;  // 事件管理变量 last wait time

	struct min_heap timeheap;  // 管事定时事件的小根堆

	struct timeval tv_cache;  // 时间管理变量
};
```

1. activequeues 是一个二级指针，前面讲过 libevent 支持事件优先级，因此你可以把它
看作是数组，其中的元素 activequeues[priority]是一个链表，链表的每个节点指向一个优先
级为 priority 的就绪事件 event。
2. eventqueue，链表，保存了所有的注册事件 event 的指针。
3. sig 信号结构体
4. event_tv 与 tv_cache 时间管理变量
5. timeheap 是管理定时事件的小根堆，将在后面定时事件处理时专门讲解；
6. event_tv 和 tv_cache 是 libevent 用于时间管理的变量，将在后面讲到；


event-internal p37

```c

struct eventop {
	const char *name;
	void *(*init)(struct event_base *);  // 初始化
	int (*add)(void *, struct event *);  // 注册事件
	int (*del)(void *, struct event *);  // 删除事件
	int (*dispatch)(struct event_base *, void *, struct timeval *);  // 事件分发
	void (*dealloc)(struct event_base *, void *);   // 注销 释放资源
	/* set if we need to reinitialize the event base */
	int need_reinit;
};
```

### 3.3 创建和初始化 event_base

### 3.4 函数接口

**对于定时事件，这些函数调用timer_heap管理接口执行插入和删除操作，对于IO事件与Signal事件，调用`eventop`操作。

```c
int event_add(struct event *ev, const struct timeval *timeout); 
int event_del(struct event *ev); 
int event_base_loop(struct event_base *base, int loops); 
void event_active(struct event *event, int res, short events); 
void event_process_active(struct event_base *base);
```

1. event_add
    event.c p730


