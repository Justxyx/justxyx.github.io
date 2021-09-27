---
title: Http Servlet 协议
author: xyx
date: 2021-9-23 13:33:00 +0800
categories: [justxyx, java]
tags:
math: true
---

## http

### 1. http 协议分类

- 请求协议
  客户端发给服务端
- 响应协议
  服务端发送给客户端

- 查看方式
  ![p1](/assets/img/some/p3.png)

### 2. http 协议特点

1. 支持客户/服务器模式。
2. 简单快速:客户向服务器请求服务时，只需传送请求方法和路径。请求方法常用的有 GET、POST。每种方法规定了客户与服务器联系的类型不同。由于 HTTP 协议简单，使得 HTTP 服务器的程序规模小，因而通信速度很快。
3. 灵活:HTTP 允许传输任意类型的数据对象。传输的类型由 Content-Type 加以标记。
4. 无连接:无连接是表示每次连接只处理一个请求。服务器处理完客户的请求，并收到客户的应答后，即断开连接。采用这种方式可以节省传输时间。
   HTTP1.1 版本后支持可持续连接。通过这种连接,就有可能在建立一个 TCP 连接后,发送请求并得到回应，然后发送更多的请求并得到更多的回应.通过把建立和释放 TCP 连接的开销分摊到多个请求上，则对于每个请求而言，由于 TCP 而造成的相对开销被大大地降低了。而且，还可以发送流水线请求,也就是说在发送请求 1 之后的回应到来之前就可以发送请求 2.也可以认为，一次连接发送多个请求，由客户机确认是否关闭连接
5. 无状态:HTTP 协议是无状态协议。无状态是指协议对于事务处理没有记忆能力。缺少状态意味着如果后续处理需要前面的信息，则它必须重传，这样可能导致每次连接传送的数据量增大。另一方面，在服务器不需要先前信息时它的应答就较快。

### 3. http 请求协议

组成部分： `请求行` `请求头` `请求正文`

**Get 请求相应协议**

```xml
GET /?username=zhangsan HTTP/1.1  //  请求行

// 请求头
Host: www.baidu.com
Connection: keep-alive
Cache-Control: max-age=0
sec-ch-ua: "Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Cookie:


// 请求正文
Get 请求没有请求正文
```

**Post 请求相应协议**

![p2](/assets/img/some/p4.png)

4. Http 响应协议
   组成部分: `响应行` `消息报头` `响应正文`

```xml
HTTP/1.1 200 OK    // 响应行， 状态码以及状态码描述

// 响应报头
Access-Control-Expose-Headers: Trace-ID
Cache-Control: public
Connection: keep-alive
Content-Encoding: gzip
Content-Security-Policy-Report-Only: object-src 'none'; script-src 'self' 'unsafe-inline' 'unsafe-eval' 'report-sample' wappass.baidu.com:* passport.baidu.com:*  wappass.bdimg.com:* passport.bdimg.com:* ppui-static-wap.cdn.bcebos.com:* ppui-static-pc.cdn.bcebos.com:* hm.baidu.com:* fe.bdimg.com:* msg.baidu.com:* pdc.baidu.com:* img.baidu.com:* openapi.baidu.com:* res.wx.qq.com:* qqq.gtimg.cn:* s.bdstatic.com:* ufosdk.baidu.com:* qapm.baidu.com:* libs.baidu.com:* ext.baidu.com:* apps.baidu.com:* s3.pstatp.com:* tb2.bdstatic.com:* b.bdstatic.com:* msg.baidu.com:* www.baidu.com:* po.srf.baidu.com:* pan.baidu.com:* play.baidu.com:* tb1.bdstatic.com:* dup.baidustatic.com:* static.tieba.baidu.com:* gss2.bdstatic.com:* blob: baiduboxapp: bootupbaiduhd: ; report-uri https://report-uri.baidu.com/report?app=passport;
Content-Type: text/html
Date: Thu, 23 Sep 2021 04:44:21 GMT
Expires: 0
Last-Modified: Thu, 23 Sep 2021 04:44:21 4SepGMT
P3p: CP=" OTI DSP COR IVA OUR IND COM "
Pragma: public
Referrer-Policy: no-referrer-when-downgrade, strict-origin-when-cross-origin
Server: BWS
Set-Cookie: logTraceID=f33a56a27f78c3c8c58c1bf7a49acccc31c9ead3b4dd6ec69d; expires=Fri, 24-Sep-2021 04:44:21 GMT; path=/; domain=passport.baidu.com
Strict-Transport-Security: max-age=31536000
Trace-Id: DCB94201
Tracecode: 26611052130668178186092312
Traceid: 1632372261245837901808966557358883510761
Vary: Accept-Encoding
Transfer-Encoding: chunked
```

**响应正文封装在 Response 中**

### 消息头详解

**重定向与转发**
转发是服务器行为，重定向是客户端行为。转发耗时比重定向少。

`转发`——>客户浏览器发送 HTTP 请求——>web 服务器接受请求——>调用内部一个方法在容器内部完成请求处理和转发动作——>再将转发跳转到的那个网页资源返回给客户； 转发只能在同一个容器内完成 转发的时候浏览器地址是不会变的，在客户浏览器里只会显示第一次进入的那个网址或者路径，客户看不到这个过程，只是得到了想要的目标资源。转发行为浏览器只做了一次请求。（转发只能跳转一次）

`重定向`——>客户浏览器发送 HTTP 请求——>web 服务器接受请求后发送 302 状态码以及新的位置给客户浏览器——>客户浏览器发现是 302 响应，则自动再发送一个新的 HTTP 请求，请求指向新的地址（302：Found 临时移动，但资源只是临时被移动。即你访问网址 A，但是网址 A 因为服务器端的拦截器或者其他后端代码处理的原因，会被重定向到网址 B。）——>服务器根据此请求寻找资源发个客户；再客户浏览器中显示的是重定向之后的路径，客户可以看到地址的变化。重定向行为浏览器做了至少两次请求。（重定向可以跳转多次）

请求头

- Referer
  查看链接从哪里来的。

响应头

- Location
  用于重定向到一个新的页面

- Refresh
  自动跳转，以秒为单位进行。
  使用场景： 三秒后跳转到某一个页面。

## Tomcat

### 1. Tomcat 目录结构

![p2](/assets/img/some/p5.png)

### 2. Idea 集成 Tomcat

略

## Servlet

### 1. 原生 servlet

```java
@WebServlet("/test")
public class Severlet extends HttpServlet {
    @Override
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        System.out.println("xxxxxxxxxxxx");
    }
}
```

### 2. Servlet 生命周期

```java
@WebServlet("/test02")
public class Servlet01 extends HttpServlet {
    @Override
    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        System.out.println("Serlvet 被调用了");
    }

    @Override
    public void init() throws ServletException {
        System.out.println("servlet 初始化");
    }

    @Override
    public void destroy() {
        System.out.println("servlet 销毁了");
    }
}
```

### 3. HttpServletRequest

- 常用方法

```java
   protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        /**
         * HttpServletRequest 的常见方法
         * */

//        1. 请求地址
        String url = req.getRequestURL() + "";
        System.out.println(url);
        System.out.println("--------------------");

//        2. 请求部分路径， 从项目站点名开始，到？前面结束
        String requestURI = req.getRequestURI();
        System.out.println(requestURI);
        System.out.println("--------------------");

//        3. 请求参数字符串
        String queryString = req.getQueryString();
        System.out.println(queryString);
        System.out.println("--------------------");

//        4. 请求方式
        String method = req.getMethod();
        System.out.println(method);
        System.out.println("--------------------");

//        5. 当前协议版本
        String protocol = req.getProtocol();
        System.out.println(protocol);
        System.out.println("--------------------");

//        6. 上下文路径
        String contextPath = req.getContextPath();
        System.out.println(contextPath);
        System.out.println("____________________");

        /**
         * 获取请求参数
         */
//        1. 获取指定参数
        String username = req.getParameter("username");
        System.out.println(username);

//        2. 获取多个  同一个参数名有多个值
        String[] xxes = req.getParameterValues("xx");
        for (String xx : xxes) {
            System.out.println(xx);
        }
    }

```

- 转发

1. 服务器端行为
2. 地址栏不发生变化
3. 从始至终都只有一个请求
4. request 数据可以共享

```java
//        1. 转发到请求
        req.getRequestDispatcher("/test02").forward(req,resp);
//        2. 转发到html
        req.getRequestDispatcher("login.html").forward(req,resp);
//        3. 转发到jsp
        req.getRequestDispatcher("login.jsp").forward(req,resp);
```

- 作用域

```java
        req.setAttribute("username","xxx");
        String username = (String) req.getAttribute("username");
```

**_把数据封装到 request 中，且作用域只在请求转发中有用_**
这样做的意义在哪 ？ 把数据传送给页面

1. 对于请求跳转来说，这样做的意义其实不大，一般也很少这样做。
2. 但对于转发到 html 和 jsp 页面，request 封装数据就很有意义，在页面中显示数据。

### 4.HttpServletResponse

- 输出

```java
//        1. 字符输出流
        PrintWriter writer = resp.getWriter();
        writer.write("hello 字符输出流");
//        2. 字节输出流
        ServletOutputStream outputStream = resp.getOutputStream();
        outputStream.write("hi".getBytes());
```

- 乱码问题

1. 设置服务器端编码格式
   response.setCharaterEncoding("UTF-8");

2. 设置客户端编码格式
   respone.setHeader("content-type","text/html;charset=UTF-8");

- 重定向
  服务端指导，客户端行为，地址栏会发生改变，作用域不共享。

  ```java
  resp.sendRedirect("test06");
  ```

- 重定向与转发的区别

![p2](/assets/img/some/p6.png)

## Cookie

Cookie 是**浏览器**提供的一种技术，通过服务器的程序能将一些只须保存在客户端，或者在客户端进行处理的数据，放在本地的计算机上，不需要通过网络传输，因而提高网页处理的效率，并且能够减少服务器的负载。但是，由于 Cookie 是服务器端保存在客户端的信息，所以其安全性也是很差的。例如常见的记住密码则可以通过 Cookie 来做。

### 1. cookie 的创建于发送

```java
        Cookie cookie = new Cookie("username", "password");
        resp.addCookie(cookie);
```

### 2. cookie 的获取

```java
        Cookie[] cookies = req.getCookies();
        if (cookies != null && cookies.length != 0){
            for (Cookie cookie : cookies) {
                System.out.println(cookie.getName());
                System.out.println(cookie.getValue());
            }
        }
```

### 3. cookie 的时间设置于删除

略

### 4. cookie 路径的设置

只有访问路径中包含 cookie 对象的 path 值，才可以获取 cookie 对象。

```java
        Cookie cookie = new Cookie("set", "xx");
        cookie.setPath("/xx/aa");
```

## HttpSession

session 无论客户端还是服务器端都可以感知到，若重新打开一个新的浏览器，则无法取得之前设置的 session，因为每一个 session 只保存在当前的浏览器当中，并在相关的页面取得。

Session 的作用就是为了标识一次会话，或者说确认一个用户;并且在一次会话（一个用户的多次请求）期间共享数据。我们可以通过 request.getSession()方法，来获取当前会话的 session 对象。

### 1. 常用方法

```java
        HttpSession session = req.getSession();

//        1.获得唯一会话标识符
        String id = session.getId();
        System.out.println(id);
        System.out.println("-------------");
//        2. 获取session创建时间
        long creationTime = session.getCreationTime();
        System.out.println(creationTime);
        System.out.println("-------------");
//        3. 获取最后一次访问时间
        long lastAccessedTime = session.getLastAccessedTime();
        System.out.println(lastAccessedTime);
        System.out.println("-------------");
//        4. 判断是否是新的session对象
        boolean aNew = session.isNew();
        System.out.println(aNew);
        ~~~
```

### 2. Jsessionid

Session 既然是为了标识一次会话，那么此次会话就应该有一个唯一的标志，这个标志就是 sessionld。
每当一次请求到达服务器，如果开启了会话(访问了 session)，服务器第一步会查看是否从客户端回传一个名为 JSESSIONID 的 cookie，如果没有则认为这是一次新的会话，会创建一个新的 session 对象，并用唯一的
sessionld 为此次会话做一个标志。如果有 JESSIONID 这个 cOoKIe 但传，服分命则云 N 掂 jE 分 210Nnceion t 会看是否含有 id 为 JSESSION 值的 session 对象，如果没有则认为是一个新的会话，重新创建一个新的 session 对象，
并标志此次会话;如果找到了相应的 session 对象，则认为是之前标志过的一次会话，返回该 session 对象，数据达到共享。
这里提到一个叫做 JSESSIONID 的 cookie，这是一个比较特殊的 cookie，当用户请求服务器时，如果访问了 session，则服务器会创建一个名为 JSESSIONID，值为获取到的 session(无论是获取到的还是新创建的)的 sessionld 的 cookie 对象，并添加到 response 对象中，响应给客户端，有效时间为关闭浏览器。
所以 Session 的底层依赖 Cookie 来实现。

### 3. request 域对象 与 session 对象

这两个好容易弄混。

```java
  // session 对象的存取
        session.setAttribute("xx","xx");
        Object xx = session.getAttribute("xx");
```

域对象在重定向中无效，在转发中有效。
session 在两者中都有效。

### 4. session 的对象销毁

```java
        // 1.设置session 的生命周期，时间为s，
        session.setMaxInactiveInterval(15);

//        2. 查看session最大时间周期
        int maxInactiveInterval = session.getMaxInactiveInterval();

//        3. 立即销毁
        session.invalidate();

//        4. 关闭浏览器

//        5. 关闭服务器
```

## ServletContext

每一个 web 应用都有且仅有一个 ServletContext 对象，又称 Application 对象，从名称中可知，该对象是与应用程序相关的。在 WEB 容器启动的时候，会为每一个 WEB 应用程序创建一个对应的 ServletContext 对象。

该对象有两大作用，第一、作为域对象用来共享数据，此时数据在整个应用程序中共享;第二、该对象中保存了当前应用程序相关信息。例如可以通过 getServerInfo()方法获取当前服务器信息，getRealPath(String path)获取资源的真实路径等。

### 1. 创建以及常用方法

```java
//        1. 直接通过request获取
        ServletContext servletContext1 = req.getServletContext();
//        2. 通过session获取
        ServletContext servletContext2 = req.getSession().getServletContext();
//        3. 直接获取
        ServletContext servletContext3 = req.getServletContext();
//        4. 通过servletConfig获取
        ServletContext servletContext4 = getServletConfig().getServletContext();

//        常用的两类方法：
//        1. 获取服务器版本信息
        ServletContext servletContext5 = req.getServletContext();
        String serverInfo = servletContext5.getServerInfo();

//        2. 获取项目真实路径
        String realPath = servletContext5.getRealPath("/");
```

### 2. ServletContext 域对象（不建议使用）

```java
        servletContext1.setAttribute("xx","xx");
        servletContext1.getAttribute("xx");
~~|
```

### 3.Servlet 三大域对象

1. request 域对象
   在一次请求中有效。请求转发有效，重定向失效。
2. session 域对象
   在一次会话中有效。请求转发和重定向都有效，session 销毁后失效。
3. servletContext 域对象
   在整个应用程序中有效。服务器关闭后失效。

如何选择？
**作用域越大，消耗的内存越多，所以在我们以后的开发中，request域对象使用的还是最多的**
