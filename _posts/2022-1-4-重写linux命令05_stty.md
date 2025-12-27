---
title: 重写linux命令05_stty
author: xyx
date: 2022-1-04 20:33:00 +0800
categories: [justxyx, system-programming]
tags: 
math: true
---


## 对前面几章的一点总结

```c
int main(){
    char dirName[] = ".";
    DIR		*dir_ptr;		/* the directory */
    struct dirent	*direntp;		/* each entry	 */
    struct stat info;


    if ((dir_ptr = opendir(dirName)) == NULL){
        cout << "error" << endl;
    } else{
        while ((direntp = readdir(dir_ptr)) != NULL){
            cout << direntp->d_name << endl;
            stat(direntp->d_name,&info);
            cout << info.st_nlink  << endl;
        }
    }
}
```

1.  打开文件夹
    char dirName[] = ".";
    DIR		*dir_ptr;
    dir_ptr = opendir(dirName)  
    direntp->d_name

2. 文件与文件夹详情 
    struct stat info;
    stat(direntp->d_name,&info);   // 文件名与文件结构


## 1. 设备也是文件

### 1.1 设备也具有文件名

设备文件一般存在在`/dev`目录下。

```c
(base) root@xm-System-Product-Name:/home/xm/xyx/linux_os# ls /dev/
autofs           i2c-1     loop23        pts       tty18  tty40  tty63      ttyS27   vcsa1
block            i2c-2     loop24        random    tty19  tty41  tty7       ttyS28   vcsa2
bsg              i2c-3     loop25        rfkill    
```

### 1.2 终端就像文件

- `tty`命令 告知用户终端文件名

```c
(base) root@xm-System-Product-Name:/home/xm/xyx/linux_os# tty
/dev/pts/1
```

- 向终端输入who

```c
(base) root@xm-System-Product-Name:/home/xm/xyx/linux_os# who > /dev/pts/1
xm       :0           2022-01-04 09:48 (:0)
xm       pts/1        2022-01-04 11:40 (192.168.2.103)
```

### 1.3 设备的文件属性

`ls -li /dev/pts/2`

```c
xm@xm-System-Product-Name:~/xyx/linux_os$ ls -li /dev/pts/2
5 crw--w---- 1 xm tty 136, 2 Jan  4 13:28 /dev
```
解释：
拥有i-节点4    1 个链接   。

文件类型为c，表示该文件实际上是以字符为单位进行传送的设备。

在/dev/pts/2这个例子中，从终端进行数据传输的代码是在设备一进程表中编号为136
的子程序。该子程序接受一个整型参数。在/dev/pts/2 中,参数是2。136 和2这两个数被
称为设备的主设备号和从设备号。主设备号确定处理该设备实际的子程序，而从设备号被
作为参数传输到该子程序。

**内核首先找到文件描述的i-节点，该i-节点用户告诉内核的文件类型。**

- 磁盘文件

内核通过访问块分配表来读取文件

- 设备文件

内核通过调用设备驱动的write来读取数据


## 2 设备与文件

### 2.1 磁盘链接属性

- 1. 缓冲属性
磁盘链接具有缓冲这样的一个属性

关闭缓冲属性
```c
int s ;
s = fcntl(fd,F_GETFL);
s |= O_SYNC;
result = fcntl(fd,F_SETEL,s);
if (reslut == 1)
    perroe("setting SYNC");
```


- 2. 改为自动添加模式

```c
int s ;
s = fcntl(fd,F_GETFL);
s |= O_APPEND;
result = fcntl(fd,F_SETEL,s);
if (reslut == 1)
    perroe("setting SYNC");
```

- 3. 利用open控制文件描述

例如
`fd = open(FILE_NAME,O_WRONLY|O_APPEND|O_SYNC;`

### 2.2 终端链接属性

```c
stty -echo   // 关闭回显
stty rease X  // x为删除键
```

直接贴代码吧，比较好懂一点

```c
struct termios {
    tcflag_t        c_iflag;        /* input flags */
    tcflag_t        c_oflag;        /* output flags */
    tcflag_t        c_cflag;        /* control flags */
    tcflag_t        c_lflag;        /* local flags */
    cc_t            c_cc[NCCS];     /* control chars */
    speed_t         c_ispeed;       /* input speed */
    speed_t         c_ospeed;       /* output speed */
};

int main(){
    struct termios *attribs;
    int fd;
    // 获取属性
    int result = tcgetattr(fd,attribs);
    
    int when = TCSANOW;     
    // 修改属性后写入
    result = tcsetattr(fd,when,attribs);
```

## 3. 其他设备的链接

流程其实还是差不多
  
1. 读取驱动
2. 修改驱动
3. 写回驱动