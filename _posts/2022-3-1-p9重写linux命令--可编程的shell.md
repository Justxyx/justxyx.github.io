---
title: p9重写linux命令-可编程的shell
author: xyx
date: 2022-3-1 20:33:00 +0800
categories: [justxyx, system-programming]
tags: 
math: true
---

# 1. 一个完整的shell命令行解析器

main.c
```shell

#include "smsh.h"
#define	DFL_PROMPT	"> "

/**
 * 1.next_cmd   从流中读入下一条命令
 * 2. splitline  将一个字符串分解为一个字符串数组 并返回
 * 3. execute 来运行这个命令
 */

int main(){
    char *cmdline,*prompt,**arglist;
    int result;
    void setup();

    prompt = DFL_PROMPT;
    setup();   // 关信号

    while ((cmdline = next_cmd(prompt,stdin)) != NULL){
        if ((arglist = splitline(cmdline)) != NULL){
            result = execute(arglist);
            freelist(arglist);
        }
        free(cmdline);
    }
    return 0;
}

void setup(){
    signal(SIGINT,SIG_IGN);
    signal(SIGQUIT,SIG_IGN);
}

void fatal(char *s1,char *s2,int n){
    fprintf(stderr,"Error:%s,%s\n",s1,s2);
    exit(n);
}



```

execute.c

```c
//
// Created by xm on 2022/3/1.
//

#include	<stdio.h>
#include	<stdlib.h>
#include	<unistd.h>
#include	<signal.h>
#include	<sys/wait.h>



int execute(char *argv[]){
    int pid;
    int child_info = -1;

    if  (argv[0] == NULL){
        return 0;
    }
    if  ((pid = fork()) == -1){
        perror("fork");
    } else if  (pid == 0){
        signal(SIGINT,SIG_DFL);
        signal(SIGQUIT,SIG_DFL);
        execvp(argv[0],argv);
        perror("cannot execute command");
        exit(1);
    } else {
        if  (wait(&child_info) == -1)
            perror("wait");
    }
    return child_info;
}
```

smsh.h
```c
//
// Created by xm on 2022/3/1.
//

#ifndef LINUX_SMSH_H
#define LINUX_SMSH_H

#define	YES	1
#define	NO	0

char	*next_cmd();
char	**splitline(char *);
void	freelist(char **);
void	*emalloc(size_t);
void	*erealloc(void *, size_t);
int	execute(char **);
void	fatal(char *, char *, int );

int	process();

#endif //LINUX_SMSH_H

```

splitline.c
```c
//
// Created by xm on 2022/3/1.
//



#include	<stdio.h>
#include	<stdlib.h>
#include	<string.h>
#include	"smsh.h"


char * next_cmd(char *prompt, FILE *fp)
{
    char	*buf ; 				/* the buffer		*/
    int	bufspace = 0;			/* total size		*/
    int	pos = 0;			/* current position	*/
    int	c;				/* input char		*/

    printf("%s", prompt);				/* prompt user	*/
    while( ( c = getc(fp)) != EOF ) {

        /* need space? */
        if( pos+1 >= bufspace ){		/* 1 for \0	*/
            if ( bufspace == 0 )		/* y: 1st time	*/
                buf = emalloc(BUFSIZ);
            else				/* or expand	*/
                buf = erealloc(buf,bufspace+BUFSIZ);
            bufspace += BUFSIZ;		/* update size	*/
        }

        /* end of command? */
        if ( c == '\n' )
            break;

        /* no, add to buffer */
        buf[pos++] = c;
    }
    if ( c == EOF && pos == 0 )		/* EOF and no input	*/
        return NULL;			/* say so		*/
    buf[pos] = '\0';
    return buf;
}

/**
 **	splitline ( parse a line into an array of strings )
 **/
#define	is_delim(x) ((x)==' '||(x)=='\t')

char ** splitline(char *line)
/*
 * purpose: split a line into array of white-space separated tokens
 * returns: a NULL-terminated array of pointers to copies of the tokens
 *          or NULL if line if no tokens on the line
 *  action: traverse the array, locate strings, make copies
 *    note: strtok() could work, but we may want to add quotes later
 */
{
    char	*newstr();
    char	**args ;
    int	spots = 0;			/* spots in table	*/
    int	bufspace = 0;			/* bytes in table	*/
    int	argnum = 0;			/* slots used		*/
    char	*cp = line;			/* pos in string	*/
    char	*start;
    int	len;

    if ( line == NULL )			/* handle special case	*/
        return NULL;

    args     = emalloc(BUFSIZ);		/* initialize array	*/
    bufspace = BUFSIZ;
    spots    = BUFSIZ/sizeof(char *);

    while( *cp != '\0' )
    {
        while ( is_delim(*cp) )		/* skip leading spaces	*/
            cp++;
        if ( *cp == '\0' )		/* quit at end-o-string	*/
            break;

        /* make sure the array has room (+1 for NULL) */
        if ( argnum+1 >= spots ){
            args = erealloc(args,bufspace+BUFSIZ);
            bufspace += BUFSIZ;
            spots += (BUFSIZ/sizeof(char *));
        }

        /* mark start, then find end of word */
        start = cp;
        len   = 1;
        while (*++cp != '\0' && !(is_delim(*cp)) )
            len++;
        args[argnum++] = newstr(start, len);
    }
    args[argnum] = NULL;
    return args;
}

/*
 * purpose: constructor for strings
 * returns: a string, never NULL
 */
char *newstr(char *s, int l)
{
    char *rv = emalloc(l+1);

    rv[l] = '\0';
    strncpy(rv, s, l);
    return rv;
}

void
freelist(char **list)
/*
 * purpose: free the list returned by splitline
 * returns: nothing
 *  action: free all strings in list and then free the list
 */
{
    char **cp = list;
    while( *cp )
        free(*cp++);
    free(list);
}

void * emalloc(size_t n)
{
    void *rv ;
    if ( (rv = malloc(n)) == NULL )
        fatal("out of memory","",1);
    return rv;
}
void * erealloc(void *p, size_t n)
{
    void *rv;
    if ( (rv = realloc(p,n)) == NULL )
        fatal("realloc() failed","",1);
    return rv;
}
```



# 2. shell 编程

## 2.1 一个简单的例子来了解shell编程

```shell
BOOK=/home/xm/test01/phonebook.data
echo find what name in phonebook
read NAME
if grep $NAME $BOOK > /tmp/pb.tmp
then
        echo Entries for $NAME
        cat /tmp/pb.tmp
else
        echo No entries for $NAME
fi
rm /tmp/pb.tmp
```

1. 变量
    定义了 NAME 与 BOOK 两个变量。 用前缀`$`来取得变量。

2. 用户输入
    read命令告诉shell 从标准输入得到一个字符串

3. 控制
    if  else 

## 2.2 shell 的流程控制

### 一个demo：

```shell

if date|grep Fri
then 
echo time for backup. Insert tape and press enter
read x
tar cvf /dev/tape/home
fi
```

> 在date中查找字符串Fri，如果找到则命令成功，如果失败则命令失败。


### 程序如何表示成功？

grep 程序调用函数`exit(0)` 表示成功。 所有Unix程序都0退出表示成功。

diff 命令用来比较两个文本文件，相同返回0；

```c
ls
who
if diff filel file1.bak
then 
    echo no differences found,removing backup
    rm file1.bak
else 
    echo backup differs,making it read-only
    chmod -w file1.bak
fi
date
```


### if 是如何工作的

1. shell 运行if之后的命令
2. shell 检查命令exit状态
3. exit的状态为0，意味着成功，非0意味着失败
4. 如果成功，shell执行then部分代码
5. 如果失败，shell执行else部分代码
6. 关键字fi标识if块的结束



# 3. 自己编写的shell 终端如何处理shell脚本（有点类似编译原理）


shell 脚本先略

