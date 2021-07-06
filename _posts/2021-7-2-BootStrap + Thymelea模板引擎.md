---
title: SpringBoot + BootStrap + Thymelea模板引擎
author: xyx
date: 2021-7-2 20:33:00 +0800
categories: [justxyx, java]
tags: 
math: true

---

# SpringBoot快速启动项目
## 两类跳转方式
* 传统方式
~~~java
@Controller
public class TestController {
    @RequestMapping("/test")
    public String test1(Model model){
        model.addAttribute("msg","这是一个跳转的演示页面");
        model.addAttribute("users", Arrays.asList("user1","user2"));
        return "demo";
    }
}
~~~

* Configuration 跳转
~~~java
@Configuration
public class MyMvcConfig implements WebMvcConfigurer{
    @Override
    public void addViewControllers(ViewControllerRegistry registry) {
        registry.addViewController("/").setViewName("index");
        registry.addViewController("/index.html").setViewName("demo");
    }
}
~~~

## restful风格
~~~java
@Controller
@ResponseBody
public class RestfulController {
    @RequestMapping("/restful/{id}")
    public Integer restful(@PathVariable("id") Integer id){
        System.out.println(id);
        return id;
    }
}
~~~

# BootStrap

[官网](https://v3.bootcss.com/getting-started/)

在线导入
~~~java

 最新版本的 Bootstrap 核心 CSS 文件 -->
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">

 可选的 Bootstrap 主题文件（一般不用引入） -->
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap-theme.min.css" integrity="sha384-6pzBo3FDv/PJ8r2KRkGHifhEocL+1X2rVCTTkUfGk7/0pbek5mMa1upzvWbrUbOZ" crossorigin="anonymous">

 最新的 Bootstrap 核心 JavaScript 文件 -->
<script src="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js" integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd" crossorigin="anonymous"></script>

~~~ 


# Thymelea模板引擎

模板引擎的作用就是我们来写一个页面模板，比如有些值呢，是动态的，我们写一些表达式。而这些值，从哪来呢，我们来组装一些数据，我们把这些数据找到。然后把这个模板和这个数据交给我们模板引擎，模板引擎按照我们这个数据帮你把这表达式解析、填充到我们指定的位置，然后把这个数据最终生成一个我们想要的内容给我们写出去，这就是我们这个模板引擎，不管是jsp还是其他模板引擎，都是这个思想，




### 1.导入pom文件

~~~java
    <!--thymeleaf模板引擎-->
    <!-- https://mvnrepository.com/artifact/org.thymeleaf/thymeleaf-spring5 -->
    <dependency>
        <groupId>org.thymeleaf</groupId>
        <artifactId>thymeleaf-spring5</artifactId>
    </dependency>
    <dependency>
        <groupId>org.thymeleaf.extras</groupId>
        <artifactId>thymeleaf-extras-java8time</artifactId>
    </dependency>
~~~
***结论:只要需要使用thymeleaf，只需要导入对应的依赖就可以了!我们将html放在我们的templates目录下即可***

### 2.导入约束

~~~html
<html lang="en"  xmlns:th="http://www.thymeleaf.org">
~~~

### 3.取值

~~~java
    // 直接取值
    @RequestMapping("/test")
    public String test(Model model){
        model.addAttribute("msg","Hello_SpringBoot");
        return "demo";
    }


    // 遍历取值
    @RequestMapping("/test2")
    public String  test2(Model model){
        model.addAttribute("users", Arrays.asList("zhoujielun","linjunjie"));
        return "demo";
~~~

~~~html
直接取值
<body>
    <p th:text="${msg}"></p>
</body>

遍历取值
<body>
    <p th:each="user:${users}" th:text="${user}"></p>
</body>

~~~


### 4.更改所有链接


***href src等，只更改本地链接，只要涉及到路径就要更改***
~~~java 

    <!-- Bootstrap core CSS -->
    <link th:href="@{/css/bootstrap.min.css}" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link th:href="@{/css/signin.css}"  rel="stylesheet">

    <img class="mb-4" th:src="@{/img/bootstrap-solid.svg}" alt="" width="72" height="72">
~~~

### 5.表单的提交与接收

 表单的提交 前端部分
~~~html
<form class="form-signin" th:action="@{/user/login}">
    <img class="mb-4" th:src="@{/img/bootstrap-solid.svg}" alt="" width="72" height="72">
    <h1 class="h3 mb-3 font-weight-normal">Please sign in</h1>
    <label class="sr-only">Username</label>
    <input type="text" name="Username" class="form-control" placeholder="Username" required="" autofocus="">
    <label class="sr-only">Password</label>
    <input type="password" name="Password" class="form-control" placeholder="Password" required="">
    <div class="checkbox mb-3">
</form>
~~~


# Thymelea常见语法

 ~~~java
//   # 如果msg不为空，则显示提示消息
  <p style="color: #bd2130" th:text="${msg}" th:th:if="${not #strings.isEmpty(msg)}"></p>
~~~