# day1 
## 前言
- 字节转换
  - 8 bit = 1 B 
  - 1024 B =1 KB 
  - 1024 KB =1 MB 
  - 1024 MB =1 GB 
  - 1024 GB = 1 TB 
- 常用的dos命令

<img src="/assets/img/java/p1.png"></img>
   
- java的编写与编译
    利用dos编译源文件
    ```
    javac HelloWorld.java
    java HelloWorld
    ```
- 标识符的命名要求
  + 标识符可以包含 英文字母26个(区分大小写) 、 0-9数字 、 $（美元符号） 和 _（下划线） 
  + 标识符不能以数字开头。 
  + 标识符不能是关键字。 
- 命名规范 
  - 类名规范：首字母大写，后面每个单词首字母大写（大驼峰式）。 
  - 方法名规范： 首字母小写，后面每个单词首字母大写（小驼峰式）。 
  - 变量名规范：全部小写。 
## 常量与变量细节
### 常量
<img src="/assets/img/java/p2.png"></img>

### 变量 
四类八种基本数据类型：
<img src="/assets/img/java/p3.png"></img>
几个标记特殊的表达方式
~~~ java
//对于float和long类型来说，字母后缀F和L不要丢掉。
long num = 300000000000L
float num = 2.5F
~~~

# day2
## 数据的类型转换
- 自动转换
  转换规则如下，由小自动填充到大
  ~~~java
  //byte、short、char‐‐>int‐‐>long‐‐>float‐‐>double
        int i = 1;  
        double d = 2.5;   
    //int类型和double类型运算，结果是double类型    
   //int类型会提升为double类型    
        double e = d+i;
- 强制转换
  将 **取值范围大的类型** 强制转换成 **取值范围小的类型** 。
 转换格式如下：
    ~~~ java
    //数据类型 变量名 = （数据类型）被转数据值
    //double类型数据强制转成int类型，直接去掉小数点。
    int i = (int)1.5;
- 几点注意
  ~~~ java
  short i = 1;
  i = i +1; //编译报错
  i = (short)(i+1) //编译成功
  ~~~
  对此解释如下： s和1做运算的时候，1是int类型，s会被提升为int类型      s+1后的结果是int类型，将结果在赋值会short类型时发生错误        short内存2个字节，int类型4个字节        必须将int强制转成short才能完成赋值 

## 几类运算符小结
- ++运算
  - 独立运算时，前++与后++没有区别
- ***混合运算时*** 区别明显
  - 变量 前++ ：变量a自己加1，将加1后的结果赋值给b，也就是说a先计算。a和b的结果都是2。
    ~~~ java
        int a = 1;     
        int b = ++a;     
        //System.out.println(a);
        //计算结果是2     
        //System.out.println(b);
        //计算结果是2 
    ~~~
  - 变量后++ ，变量a先把自己的值1，赋值给变量b，此时变量b的值就是1，变量a自己再加1。a的结果是2，b 的结果是1。
    ~~~java
        int a = 1;     
        int b = a++;     
        //System.out.println(a);
        //计算结果是2     
        //System.out.println(b);
        //计算结果是1 
    ~~~
- +运算符在字符串中表示拼接
- ！表示取反操作
- 三元运算符的基本格式
  ```int i = (1==2 ? 100 : 200); ```

## 方法（函数）的定义与调用
基本格式
```
修饰符 返回值类型 方法名 （参数列表）｛
    代码...              
    return ;       
}
```
调用
```
方法名 （参数列表）
```
几点注意：
- 方法必须定义在一类方法之外
- 方法不能定义在另一个方法的里面
## jshell 简单介绍
方便快捷编写代码，jdk9特性
<img src="/assets/img/java/p4.jpg"></img>
