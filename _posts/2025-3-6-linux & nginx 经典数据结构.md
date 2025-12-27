---
title: linux & nginx 经典数据结构
author: xyx
date: 2025-3-6 13:33:00 +0800
categories: [justxyx, nginx]
tags:
math: true
---


## 1. ngx_str_t

```c
typedef struct {
    size_t      len;
    u_char     *data;
} ngx_str_t;
```

## 2. ngx_list_part_t

// 分段链表

```c
typedef struct ngx_list_part_s  ngx_list_part_t;

struct ngx_list_part_s {
    void             *elts;  // 数组的起始地址
    ngx_uint_t        nelts; // 已经使用了多少个数组元素 必须小于nalloc
    ngx_list_part_t  *next;   // 下一个ngx_list_part_t 地址
};


typedef struct {
    ngx_list_part_t  *last; // 指向链表最后一个元素
    ngx_list_part_t   part; // 指向首个元素
    size_t            size;  // 每个数组元素的大小
    ngx_uint_t        nalloc; // 最多可以存储多少个数组元素
    ngx_pool_t       *pool; // 内存池
} ngx_list_t;
```

示例：
```c
#include <ngx_config.h>
#include <ngx_core.h>
#include <stdio.h>

// 自定义结构体
typedef struct {
    int id;
    ngx_str_t name;
} my_struct_t;

int main() {
    ngx_pool_t *pool;
    ngx_list_t *list;
    my_struct_t *item;
    ngx_uint_t i;
    ngx_list_part_t *part;

    // 初始化 Nginx 的核心模块
    if (ngx_strerror_init() != NGX_OK) {
        fprintf(stderr, "Failed to initialize ngx_strerror\n");
        return 1;
    }

    // 创建一个内存池
    pool = ngx_create_pool(4096, NULL); // 4096 是内存池的初始大小
    if (pool == NULL) {
        fprintf(stderr, "Failed to create memory pool\n");
        return 1;
    }

    // 创建一个 ngx_list_t 结构，每个元素的大小为 sizeof(my_struct_t)
    list = ngx_list_create(pool, 5, sizeof(my_struct_t)); // 每个节点最多 5 个元素
    if (list == NULL) {
        fprintf(stderr, "Failed to create list\n");
        ngx_destroy_pool(pool);
        return 1;
    }

    // 添加元素到列表中
    for (i = 0; i < 7; i++) { // 添加 7 个元素，测试节点自动扩展
        item = ngx_list_push(list);
        if (item == NULL) {
            fprintf(stderr, "Failed to push element to list\n");
            ngx_destroy_pool(pool);
            return 1;
        }

        item->id = i;
        item->name.len = snprintf(NULL, 0, "Item %d", i) + 1; // 计算字符串长度
        item->name.data = ngx_palloc(pool, item->name.len);   // 1. ngx_list_push 会为 ngx_list_t 中的元素分配内存，但这个内存只包含 my_struct_t 结构体本身。
                                                              // 如果 my_struct_t 中有指针（如 ngx_str_t 的 data 字段），ngx_list_push 不会为指针指向的内容分配内存。
        snprintf((char *)item->name.data, item->name.len, "Item %d", i); // 赋值
    }

    // 遍历列表中的元素
    part = &list->part;
    i = 0;

    while (part != NULL) {
        item = part->elts;
        for (ngx_uint_t j = 0; j < part->nelts; j++) {
            printf("List element %ui: id=%d, name=%.*s\n",
                   i, item[j].id, (int)item[j].name.len, item[j].name.data);
            i++;
        }
        part = part->next;
    }

    // 销毁内存池
    ngx_destroy_pool(pool);

    return 0;
}
```

## 3.ngx_table_elt_t

```c
typedef struct {
    ngx_uint_t        hash;         // 键的哈希值
    ngx_str_t         key;          // 键（字符串）
    ngx_str_t         value;        // 值（字符串）
    u_char           *lowcase_key;  // 键的小写形式（用于不区分大小写的比较）
} ngx_table_elt_t;
```

举例
```c
#include <ngx_config.h>
#include <ngx_core.h>
#include <stdio.h>

int main_2() {
    ngx_pool_t *pool;
    ngx_table_elt_t *header;

    // 初始化 Nginx 的核心模块
    if (ngx_strerror_init() != NGX_OK) {
        fprintf(stderr, "Failed to initialize ngx_strerror\n");
        return 1;
    }

    // 创建一个内存池
    pool = ngx_create_pool(4096, NULL); // 4096 是内存池的初始大小
    if (pool == NULL) {
        fprintf(stderr, "Failed to create memory pool\n");
        return 1;
    }

    // 分配一个 ngx_table_elt_t 结构
    header = ngx_palloc(pool, sizeof(ngx_table_elt_t));
    if (header == NULL) {
        fprintf(stderr, "Failed to allocate ngx_table_elt_t\n");
        ngx_destroy_pool(pool);
        return 1;
    }

    // 设置键
    header->key.data = (u_char *)"Content-Type";
    header->key.len = sizeof("Content-Type") - 1;

    // 设置值
    header->value.data = (u_char *)"text/html";
    header->value.len = sizeof("text/html") - 1;

    // 计算键的哈希值
    header->hash = ngx_hash_key(header->key.data, header->key.len);

    // 生成键的小写形式
    header->lowcase_key = ngx_palloc(pool, header->key.len);
    if (header->lowcase_key == NULL) {
        fprintf(stderr, "Failed to allocate lowcase_key\n");
        ngx_destroy_pool(pool);
        return 1;
    }
    ngx_strlow(header->lowcase_key, header->key.data, header->key.len);

    // 打印结果
    printf("Key: %.*s\n", (int)header->key.len, header->key.data);
    printf("Value: %.*s\n", (int)header->value.len, header->value.data);
    printf("Hash: %u\n", header->hash);
    printf("Lowcase Key: %.*s\n", (int)header->key.len, header->lowcase_key);

    // 销毁内存池
    ngx_destroy_pool(pool);

    return 0;
}
```


## 4. ngx_buf_t  

```c
typedef struct ngx_buf_s  ngx_buf_t;

struct ngx_buf_s {
    u_char          *pos;           // 当前读取位置
    u_char          *last;          // 当前写入位置
    off_t            file_pos;      // 文件中的读取位置
    off_t            file_last;     // 文件中的写入位置

    u_char          *start;         // 缓冲区的起始位置
    u_char          *end;           // 缓冲区的结束位置
    ngx_buf_tag_t    tag;           // 缓冲区标签（用于标识缓冲区的用途  缓冲区对应模块等）
    ngx_file_t      *file;          // 文件指针（如果缓冲区表示文件）
    ngx_buf_t       *shadow;        // 指向另一个缓冲区的指针（用于链式缓冲区）

    unsigned         temporary:1;   // 是否为临时缓冲区
    unsigned         memory:1;      // 是否为内存缓冲区
    unsigned         mmap:1;        // 是否为内存映射缓冲区
    unsigned         recycled:1;    // 是否可回收
    unsigned         in_file:1;     // 是否表示文件内容
    unsigned         flush:1;       // 是否需要刷新
    unsigned         sync:1;        // 是否需要同步
    unsigned         last_buf:1;    // 是否为最后一个缓冲区
    unsigned         last_in_chain:1; // 是否为链中的最后一个缓冲区
    unsigned         last_shadow:1; // 是否为最后一个影子缓冲区
    unsigned         temp_file:1;   // 是否为临时文件
};
```

举例：

```c
#include <ngx_config.h>
#include <ngx_core.h>
#include <stdio.h>

int main() {
    ngx_pool_t *pool;
    ngx_buf_t *buf;

    // 初始化 Nginx 的核心模块
    if (ngx_strerror_init() != NGX_OK) {
        fprintf(stderr, "Failed to initialize ngx_strerror\n");
        return 1;
    }

    // 创建一个内存池
    pool = ngx_create_pool(4096, NULL); // 4096 是内存池的初始大小
    if (pool == NULL) {
        fprintf(stderr, "Failed to create memory pool\n");
        return 1;
    }

    // 分配一个 ngx_buf_t 结构
    buf = ngx_palloc(pool, sizeof(ngx_buf_t));
    if (buf == NULL) {
        fprintf(stderr, "Failed to allocate ngx_buf_t\n");
        ngx_destroy_pool(pool);
        return 1;
    }

    // 初始化缓冲区
    buf->start = ngx_palloc(pool, 1024); // 分配 1KB 的内存
    if (buf->start == NULL) {
        fprintf(stderr, "Failed to allocate buffer memory\n");
        ngx_destroy_pool(pool);
        return 1;
    }

    buf->pos = buf->start;
    buf->last = buf->start;
    buf->end = buf->start + 1024;
    buf->memory = 1; // 标记为内存缓冲区

    // 向缓冲区写入数据
    ngx_memcpy(buf->last, "Hello, Nginx!", sizeof("Hello, Nginx!") - 1);
    buf->last += sizeof("Hello, Nginx!") - 1;

    // 打印缓冲区内容
    printf("Buffer content: %.*s\n", (int)(buf->last - buf->pos), buf->pos);

    // 销毁内存池
    ngx_destroy_pool(pool);

    return 0;
}
```

## 5. ngx_chain_t

```c
typedef struct ngx_chain_s       ngx_chain_t;

struct ngx_chain_s {
    ngx_buf_t    *buf;  // 指向当前缓冲区的指针
    ngx_chain_t  *next; // 指向下一个链式缓冲区的指针
};


// 举例
#include <stdio.h>
#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_http.h>

int main() {
    ngx_pool_t *pool;
    ngx_chain_t *chain = NULL;
    ngx_chain_t *cl;
    ngx_buf_t *buf;
    ngx_uint_t i;

    // 初始化内存池
    pool = ngx_create_pool(4096, NULL);
    if (pool == NULL) {
        fprintf(stderr, "Failed to create memory pool\n");
        return 1;
    }

    // 创建并填充 ngx_chain_t 链表
    for (i = 0; i < 3; i++) {
        // 分配一个 ngx_chain_t 节点
        cl = ngx_alloc_chain_link(pool);
        if (cl == NULL) {
            fprintf(stderr, "Failed to allocate chain link\n");
            ngx_destroy_pool(pool);
            return 1;
        }

        // 分配一个 ngx_buf_t 数据块
        buf = ngx_calloc_buf(pool);
        if (buf == NULL) {
            fprintf(stderr, "Failed to allocate buffer\n");
            ngx_destroy_pool(pool);
            return 1;
        }

        // 填充数据块
        buf->pos = (u_char *)"Hello";
        buf->last = buf->pos + 5;
        buf->memory = 1; // 标记为内存数据

        // 将数据块添加到链表中
        cl->buf = buf;
        cl->next = chain;
        chain = cl;
    }

    // 遍历链表并打印数据
    cl = chain;
    while (cl != NULL) {
        printf("Data: %.*s\n", (int)(cl->buf->last - cl->buf->pos), cl->buf->pos);
        cl = cl->next;
    }

    // 销毁内存池
    ngx_destroy_pool(pool);

    return 0;
}
```

## 6. ngx_pool_t

```c
typedef struct ngx_pool_s ngx_pool_t;

struct ngx_pool_s {
    u_char              *last;      // 当前内存块的可用起始位置
    u_char              *end;       // 当前内存块的结束位置
    ngx_pool_t          *next;      // 指向下一个内存池的指针
    ngx_uint_t           failed;    // 当前内存池分配失败的次数
    size_t               max;       // 当前内存池的最大可分配大小
    ngx_pool_t          *current;   // 指向当前可用内存池的指针
    ngx_chain_t         *chain;     // 用于链式缓冲区的链表
    ngx_pool_large_t    *large;     // 指向大内存块的链表
    ngx_pool_cleanup_t  *cleanup;   // 指向清理回调函数的链表
    ngx_log_t           *log;       // 日志对象
};
```

```c
#include <ngx_config.h>
#include <ngx_core.h>
#include <stdio.h>

// 清理回调函数
void cleanup_handler(void *data) {
    printf("Cleanup handler: %s\n", (char *)data);
}

int main() {
    ngx_pool_t *pool;
    ngx_pool_cleanup_t *cln;
    char *data;

    // 初始化 Nginx 的核心模块
    if (ngx_strerror_init() != NGX_OK) {
        fprintf(stderr, "Failed to initialize ngx_strerror\n");
        return 1;
    }

    // 创建一个内存池
    pool = ngx_create_pool(4096, NULL);
    if (pool == NULL) {
        fprintf(stderr, "Failed to create memory pool\n");
        return 1;
    }

    // 分配内存
    data = ngx_palloc(pool, 1024);
    if (data == NULL) {
        fprintf(stderr, "Failed to allocate memory\n");
        ngx_destroy_pool(pool);
        return 1;
    }

    // 使用内存
    ngx_memcpy(data, "Hello, Nginx!", sizeof("Hello, Nginx!") - 1);
    printf("Data: %s\n", data);

    // 注册清理回调
    cln = ngx_pool_cleanup_add(pool, 0);
    if (cln == NULL) {
        fprintf(stderr, "Failed to add cleanup handler\n");
        ngx_destroy_pool(pool);
        return 1;
    }

    cln->handler = cleanup_handler;
    cln->data = "Memory pool is being destroyed.";

    // 销毁内存池
    ngx_destroy_pool(pool);

    return 0;
}
```

## 7. 锚点链表

```c
#include <stdio.h>
#include <stdlib.h>

/**
 * Linux 内核双向链表实现
 */

// 获取结构体成员的偏移量
#define offsetof(TYPE, MEMBER) ((size_t) &((TYPE *)0)->MEMBER)

/**
 * container_of - 通过结构体成员的指针获取整个结构体的指针
 * @ptr: 结构体成员的指针
 * @type: 结构体的类型
 * @member: 结构体中成员的名称
 */
#define container_of(ptr, type, member) ({          \
    typeof( ((type *)0)->member ) *__mptr = (ptr); \  // 获取成员指针的类型，并赋值给 __mptr
    (type *)( (char *)__mptr - offsetof(type, member) );})  // 计算结构体的起始地址

/**
 * list_entry - 通过链表节点获取包含它的结构体的指针
 * @ptr: 链表节点的指针
 * @type: 结构体的类型
 * @member: 结构体中链表节点的名称
 */
#define list_entry(ptr, type, member) container_of(ptr, type, member)

// 双向链表节点
struct list_head {
    struct list_head *next, *prev;
};

// 初始化链表头
#define LIST_HEAD(name) \
    struct list_head name = { &(name), &(name) }

/**
 * list_for_each_entry_safe - 安全地遍历链表
 * @pos: 当前遍历的节点指针（结构体类型）
 * @n: 下一个节点的指针（结构体类型）
 * @head: 链表的头节点
 * @member: 链表节点在结构体中的名称
 *  为什么是安全的？ 每次循环中，n 保存了下一个节点的指针，即使 pos 被删除，n 仍然可以用于更新 pos，继续遍历链表
 */
#define list_for_each_entry_safe(pos, n, head, member)               \
    for (pos = list_entry((head)->next, typeof(*pos), member),       \   // （head）是一个特殊的节点，它不包含有效数据
        n = list_entry(pos->member.next, typeof(*pos), member);      \
        &pos->member != (head);                                      \
        pos = n, n = list_entry(n->member.next, typeof(*n), member))

// 添加节点到链表尾部
void list_add_tail(struct list_head *new, struct list_head *head) {
    new->next = head;
    new->prev = head->prev;
    head->prev->next = new;
    head->prev = new;
}

// 从链表中删除节点
void list_del(struct list_head *entry) {
    entry->prev->next = entry->next;
    entry->next->prev = entry->prev;
    entry->next = entry->prev = NULL;
}

// 示例结构体，包含一个链表节点
struct my_struct {
    int data;
    struct list_head list;  // 链表节点
};

int main() {
    // 初始化链表头
    LIST_HEAD(my_list);

    // 添加一些节点到链表
    for (int i = 0; i < 5; i++) {
        struct my_struct *new_node = malloc(sizeof(struct my_struct));
        new_node->data = i;
        list_add_tail(&new_node->list, &my_list);  // 添加到链表尾部
    }

    // 遍历链表并打印数据
    printf("Original list:\n");
    struct my_struct *pos;
    list_for_each_entry_safe(pos, pos, &my_list, list) {
        printf("Data: %d\n", pos->data);
    }

    // 删除数据为 2 的节点
    printf("\nDeleting node with data = 2...\n");
    list_for_each_entry_safe(pos, pos, &my_list, list) {
        if (pos->data == 2) {
            list_del(&pos->list);  // 从链表中删除节点
            free(pos);             // 释放内存
            break;
        }
    }

    // 再次遍历链表并打印数据
    printf("\nList after deletion:\n");
    list_for_each_entry_safe(pos, pos, &my_list, list) {
        printf("Data: %d\n", pos->data);
    }

    // 释放剩余节点的内存
    list_for_each_entry_safe(pos, pos, &my_list, list) {
        list_del(&pos->list);
        free(pos);
    }

    return 0;
}
```

## 8. ngx_queue_t

#### 容器使用

| 方法/宏                          | 描述                                                                 |
|----------------------------------|----------------------------------------------------------------------|
| `ngx_queue_init(q)`              | 初始化一个空链表。                                                  |
| `ngx_queue_empty(q)`             | 检查链表是否为空。                                                  |
| `ngx_queue_insert_head(h, x)`    | 将节点 `x` 插入到链表 `h` 的头部。                                   |
| `ngx_queue_insert_tail(h, x)`    | 将节点 `x` 插入到链表 `h` 的尾部。                                   |
| `ngx_queue_insert(q, x)`         | 将节点 `x` 插入到节点 `q` 之后。                                     |
| `ngx_queue_head(h)`              | 获取链表 `h` 的第一个节点。                                         |
| `ngx_queue_last(h)`              | 获取链表 `h` 的最后一个节点。                                        |
| `ngx_queue_sentinel(h)`          | 获取链表 `h` 的哨兵节点（用于遍历结束判断）。                        |
| `ngx_queue_remove(x)`            | 将节点 `x` 从链表中移除。                                            |
| `ngx_queue_split(h, q, n)`       | 将链表 `h` 从节点 `q` 处拆分为两个链表，`n` 是拆分后的新链表。       |
| `ngx_queue_add(h, n)`            | 将链表 `n` 合并到链表 `h` 的尾部。                                   |
| `ngx_queue_middle(h)`            | 获取链表 `h` 的中间节点（用于快速查找中间节点）。                    |
| `ngx_queue_sort(h, cmp)`         | 对链表 `h` 进行排序，`cmp` 是自定义的比较函数。                      |         |

#### 元素使用

| 方法/宏                          | 描述                                                                 |
|----------------------------------|----------------------------------------------------------------------|
| `ngx_queue_next(q)`              | 获取节点 `q` 的下一个节点。                                          |
| `ngx_queue_prev(q)`              | 获取节点 `q` 的上一个节点。                                          |
| `ngx_queue_data(q, type, link)`  | 从节点 `q` 获取包含它的结构体指针。                                  |
|                                  | - `q`：`ngx_queue_t` 节点指针。                                      |
|                                  | - `type`：结构体类型。                                               |
|                                  | - `link`：`ngx_queue_t` 在结构体中的字段名。                         |
|ngx_queue_insert_after(q, x)|-|

## 9. ngx_array_t 

| 方法名                | 参数含义                                                                 | 执行意义                                                                                   |
|-----------------------|--------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| `ngx_array_create`    | `p` 是内存池，`n` 是初始分配元素的最大个数，`size` 是每一个元素所占用的内存大小。 | 创建一个动态数组，并预分配 `n` 个大小为 `size` 的内存空间。                               |
| `ngx_array_init`      | `a` 是一个动态数组结构体的指针，`p` 是内存池，`n` 是初始分配元素的最大个数，`size` 是每一个元素所占用的内存大小。 | 初始化一个已经存在的动态数组，并预分配 `n` 个大小为 `size` 的内存空间。                   |
| `ngx_array_destroy`   | `a` 是一个动态数组结构体的指针。                                          | 销毁已经分配的数组元素空间和动态数组对象。注意：`ngx_array_destroy` 不会释放 `nginx_array_t` 结构体自身占用的内存。 |
| `ngx_array_push`      | `a` 是一个动态数组结构体的指针。                                          | 向当前 `a` 动态数组中添加一个元素，返回的是这个新添加元素的地址。注意：如果动态数组已经达到容量上限，会自动扩容。 |
| `ngx_array_push_n`    | `a` 是一个动态数组结构体的指针，`n` 是需要添加元素的个数。                 | 向当前 `a` 动态数组中添加 `n` 个元素，返回的是新添加这批元素中第一个元素的地址。          |


## 10. hash 表

```c
typedef struct {
    ngx_hash_elt_t  ​**buckets; // 散列桶数组
    ngx_uint_t        size;    // 散列桶的数量
} ngx_hash_t;

typedef struct {
    void             *value;   // 值
    u_short           len;     // 键的长度
    u_char            name[1]; // 键的字符串（柔性数组）
} ngx_hash_elt_t;

typedef struct {
    ngx_str_t         key;    // 键
    ngx_uint_t        key_hash; // 键的散列值
    void             *value;  // 值
} ngx_hash_key_t;

typedef struct {
    ngx_hash_t       *hash;         // 散列表
    ngx_hash_key_t   *keys;         // 键值对数组
    ngx_uint_t        max_size;     // 散列表的最大容量
    ngx_uint_t        bucket_size;  // 每个散列桶的大小
    ngx_pool_t       *pool;         // 内存池
    ngx_pool_t       *temp_pool;    // 临时内存池
} ngx_hash_init_t;


#include <stdio.h>
#include <ngx_config.h>
#include <ngx_core.h>

int main() {
    ngx_pool_t *pool;
    ngx_hash_t hash;
    ngx_hash_init_t hinit;
    ngx_hash_key_t keys[3];
    ngx_str_t key1 = ngx_string("key1");
    ngx_str_t key2 = ngx_string("key2");
    ngx_str_t key3 = ngx_string("key3");
    void *value1 = (void *)"value1";
    void *value2 = (void *)"value2";
    void *value3 = (void *)"value3";

    // 初始化内存池
    pool = ngx_create_pool(4096, NULL);
    if (pool == NULL) {
        fprintf(stderr, "Failed to create memory pool\n");
        return 1;
    }

    // 初始化键值对
    keys[0].key = key1;
    keys[0].key_hash = ngx_hash_key_lc(key1.data, key1.len);
    keys[0].value = value1;

    keys[1].key = key2;
    keys[1].key_hash = ngx_hash_key_lc(key2.data, key2.len);
    keys[1].value = value2;

    keys[2].key = key3;
    keys[2].key_hash = ngx_hash_key_lc(key3.data, key3.len);
    keys[2].value = value3;

    // 初始化散列表
    hinit.hash = &hash;
    hinit.key = ngx_hash_key_lc;
    hinit.max_size = 1024;
    hinit.bucket_size = 64;
    hinit.name = "test_hash";
    hinit.pool = pool;
    hinit.temp_pool = NULL;

    if (ngx_hash_init(&hinit, keys, 3) != NGX_OK) {
        fprintf(stderr, "Failed to initialize hash table\n");
        ngx_destroy_pool(pool);
        return 1;
    }

    // 查找键值对
    ngx_str_t find_key = ngx_string("key2");
    void *result = ngx_hash_find(&hash, ngx_hash_key_lc(find_key.data, find_key.len), find_key.data, find_key.len);

    if (result != NULL) {
        printf("Found: %s\n", (char *)result);
    } else {
        printf("Not found\n");
    }

    // 销毁内存池
    ngx_destroy_pool(pool);

    return 0;
}
```

## 11. 通配符的hash 表， 暂略

