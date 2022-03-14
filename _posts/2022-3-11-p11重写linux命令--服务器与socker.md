---
title: p11 重写linux命令--服务器与socket
author: xyx
date: 2022-3-11 20:33:00 +0800
categories: [C++, linux-os]
tags: 
math: true
---

# 1. 概览

Unix 怎么处理来自不同数据源的数据？

1. 磁盘与设备文件
    open命令链接，read write传递数据。

2. 管道
    pipe 命令创建，fork共享，read 与 write 传递。

3. Sockets
    用Socket，lisetn 和 connect 链接。 用read 和 write 传递数据。 


# 2. 从 bc 程序来推广

## 2.1 bc详解

### bc并不是一个计算器

bc在内部启动了一个dc的计算程序，通过管道与其进行通信。dc是一个基于栈的计算器。

### 从bc方法中得到的思想

1. 客户/服务器模型
    bc/dc程序是对客户/服务器模型的一个实例。dc提供计算服务，bc提供界面。

2. 双向通信
    客户/服务器模型，它要求一个进程既要跟另外一个进程的标准输入也要和它的标准输出通信。

3. 永久性服务
    bc不同于shell服务。shell 程序的每个命令都会创建一个新的进程。 **bc程序持续不断的和dc同一个实例进行通信** 他们之间的关系不同于标准函数中所使用的的函数调用返回机制。

**他们之间的关系不同于标准函数中所使用的的函数调用返回机制**。

### bc 的实现

```c
be_dc(int[],int[]);
be_bc(int[],int[]);
fatal()

int main(){
    int pid,todc[2],formdc[2];

    if (pipe(todc) == -1 || pipe(formdc) == -1)
        perror("pipe error");

    pid = fork();
    if (pid == -1)
        perror("fork error");

    if (pid == 0)
        be_dc(todc,formdc);
    else{
        be_bc(todc,formdc);
        wait(NULL);
    }
}

be_dc(int in[2],int out[2]){
    if (dup2(in[0],0) == -1)
        perror("dup2 error");
    close(in[0]);
    close(in[1]);

    if (dup2(out[1],1) == -1)
        perror("dup2 error");
    close(out[1]);
    close(out[0]);

    execlp("dc", "dc", "-", NULL );
    perror("dc error");
}


be_bc(int todc[2], int fromdc[2])
/*
 *	read from stdin and convert into to RPN, send down pipe
 *	then read from other pipe and print to user
 *	Uses fdopen() to convert a file descriptor to a stream
 */
{
    int	num1, num2;
    char	operation[BUFSIZ], message[BUFSIZ], *fgets();
    FILE	*fpout, *fpin, *fdopen();

    /* setup */
    close(todc[0]);			/* won't read from pipe to dc  */
    close(fromdc[1]);		/* won't write to pipe from dc */

    fpout = fdopen( todc[1],   "w" );	/* convert file desc-  */
    fpin  = fdopen( fromdc[0], "r" );	/* riptors to streams  */
    if ( fpout == NULL || fpin == NULL )
        fatal("Error convering pipes to streams");

    /* main loop */
    while ( printf("tinybc: "), fgets(message,BUFSIZ,stdin) != NULL ){

        /* parse input */
        if ( sscanf(message,"%d%[-+*/^]%d",&num1,operation,&num2)!=3){
            printf("syntax error\n");
            continue;
        }

        if ( fprintf( fpout , "%d\n%d\n%c\np\n", num1, num2,
                      *operation ) == EOF )
            fatal("Error writing");
        fflush(  fpout );
        if ( fgets( message, BUFSIZ, fpin ) == NULL )
            break;
        printf("%d %c %d = %s", num1, *operation , num2, message);
    }
    fclose(fpout);		/* close pipe		*/
    fclose(fpin);		/* dc will see EOF	*/
}

fatal( char *mess )
{
    fprintf(stderr, "Error: %s\n", mess);
    exit(1);
}

```

1. 两个进程，两个管道。为什么要两个管道？  一个管道又写又读，没办法协调。

2. fdopen() 与 fopen()。 前者打开文件描述符，后者打开文件名。

3. 可以像写文件一样向管道写入，读取。


