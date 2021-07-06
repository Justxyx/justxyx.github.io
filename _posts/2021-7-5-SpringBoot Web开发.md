---
title: SpringBoot Web开发
author: xyx
date: 2021-7-5 20:33:00 +0800
categories: [justxyx, java]
tags: 
math: true

---

## 解决密码暴露问题的方法
~~~java
if (Username!= null && "123456".equals(Password)){
    // 登录成功
    return "redirect:/main.html";

登录成功后直接重定向转发
~~~

~~~java
利用MyMvcConfig接受main.html

registry.addViewController("main.html").setViewName("主页");
~~~

## 拦截器的设计与实现

1. 登录成功存储session
    ~~~java
    session.setAttribute("loginUser",username);
    ~~~

2. LoginHandlerInterceptor的设计
    ~~~java
    public class LoginHandlerInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        //登录成功之后应该有用户的session
        Object loginUser = request.getSession().getAttribute("loginUser");
        if(loginUser==null){
            request.setAttribute("msg","没有权限请先登录");
            request.getRequestDispatcher("/index.html").forward(request,response);
            return false;
        }else{
            return true;
        }
    }
    }
    ~~~

3. 注册到MyMvcConfig中，拦截与放行

~~~java
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new LoginHandlerInterceptor())
                .addPathPatterns("/**")
                .excludePathPatterns("/index.html","/","/user/login","/css/**","/js/**","/img/**");
    }
~~~

## 一个小问题
~~~java
 model.addAttribute("msg","用户名或者密码错误");
 与
 request.setAttribute("msg","没有权限请先登录");
 在前端html拿到msg消息时，都一样
 ~~~

 