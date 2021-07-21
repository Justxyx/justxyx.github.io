---
title: springboot+vue+websocket
author: xyx
date: 2021-7-21 13:33:00 +0800
categories: [justxyx, java]
tags:
math: true
---

本以为网上的教程会很多，没想到鱼龙混杂，很难找到一篇合适的，记录一下。

## pom

```java
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>
	<parent>
		<groupId>org.springframework.boot</groupId>
		<artifactId>spring-boot-starter-parent</artifactId>
		<version>2.5.2</version>
		<relativePath/> <!-- lookup parent from repository -->
	</parent>
	<groupId>com.xm</groupId>
	<artifactId>facesystem</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<name>facesystem</name>
	<description>Demo project for Spring Boot</description>
	<properties>
		<java.version>1.8</java.version>
	</properties>
	<dependencies>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-web</artifactId>
		</dependency>

		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>com.vaadin.external.google</groupId>
			<artifactId>android-json</artifactId>
			<version>0.0.20131108.vaadin1</version>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-websocket</artifactId>
		</dependency>
		<dependency>
			<groupId>org.slf4j</groupId>
			<artifactId>jul-to-slf4j</artifactId>
			<version>1.7.30</version>
		</dependency>
		<dependency>
			<groupId>org.projectlombok</groupId>
			<artifactId>lombok</artifactId>
			<version>1.18.18</version>
		</dependency>
		<dependency>
			<groupId>com.alibaba</groupId>
			<artifactId>fastjson</artifactId>
			<version>1.1.37</version>
		</dependency>
		<dependency>
			<groupId>commons-lang</groupId>
			<artifactId>commons-lang</artifactId>
			<version>2.6</version>
		</dependency>
		<!-- https://mvnrepository.com/artifact/cn.hutool/hutool-log -->
		<dependency>
			<groupId>cn.hutool</groupId>
			<artifactId>hutool-log</artifactId>
			<version>5.7.0</version>
		</dependency>




	</dependencies>

	<build>
		<plugins>
			<plugin>
				<groupId>org.springframework.boot</groupId>
				<artifactId>spring-boot-maven-plugin</artifactId>
			</plugin>
		</plugins>
	</build>

</project>
```

## WebSocketConfig

```java
package com.xm.facesystem.websocket;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.server.standard.ServerEndpointExporter;

@Configuration
public class WebSocketConfig {

    /**
     * websocket配置
     * @return
     */
    @Bean
    public ServerEndpointExporter serverEndpointExporter() {
        return new ServerEndpointExporter();
    }
}
```

## WebSocketServer

```java
package com.xm.facesystem.websocket;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.websocket.*;
import javax.websocket.server.ServerEndpoint;
import java.io.IOException;
import java.util.concurrent.CopyOnWriteArraySet;
import java.util.concurrent.atomic.AtomicInteger;

@ServerEndpoint(value = "/ws/asset")
@Component
public class WebSocketServer {

    @PostConstruct
    public void init() {
        System.out.println("websocket 加载");
    }
    private static Logger log = LoggerFactory.getLogger(WebSocketServer.class);
    private static final AtomicInteger OnlineCount = new AtomicInteger(0);
    // concurrent包的线程安全Set，用来存放每个客户端对应的Session对象。
    private static CopyOnWriteArraySet<Session> SessionSet = new CopyOnWriteArraySet<Session>();


    /**
     * 连接建立成功调用的方法
     */
    @OnOpen
    public void onOpen(Session session) {
        SessionSet.add(session);
        int cnt = OnlineCount.incrementAndGet(); // 在线数加1
        log.info("有连接加入，当前连接数为：{}", cnt);
        SendMessage(session, "连接成功");

    }

    /**
     * 连接关闭调用的方法
     */
    @OnClose
    public void onClose(Session session) {
        SessionSet.remove(session);
        int cnt = OnlineCount.decrementAndGet();
        log.info("有连接关闭，当前连接数为：{}", cnt);
    }

    /**
     * 收到客户端消息后调用的方法
     *
     * @param message
     *            客户端发送过来的消息
     */
    @OnMessage
    public void onMessage(String message, Session session) {
        log.info("来自客户端的消息：{}",message);
        SendMessage(session, "收到消息，消息内容："+message);
    }

    /**
     * 出现错误
     * @param session
     * @param error
     */
    @OnError
    public void onError(Session session, Throwable error) {
        log.error("发生错误：{}，Session ID： {}",error.getMessage(),session.getId());
        error.printStackTrace();
    }

    /**
     * 发送消息，实践表明，每次浏览器刷新，session会发生变化。
     * @param session
     * @param message
     */
    public static void SendMessage(Session session, String message) {
        try {
            session.getBasicRemote().sendText(String.format("%s (From Server，Session ID=%s)",message,session.getId()));
        } catch (IOException e) {
            log.error("发送消息出错：{}", e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 群发消息
     * @param message
     * @throws IOException
     */
    public static void BroadCastInfo(String message) throws IOException {
        for (Session session : SessionSet) {
            if(session.isOpen()){
                SendMessage(session, message);
            }
        }
    }

    /**
     * 指定Session发送消息
     * @param sessionId
     * @param message
     * @throws IOException
     */
    public static void SendMessage(String message,String sessionId) throws IOException {
        Session session = null;
        for (Session s : SessionSet) {
            if(s.getId().equals(sessionId)){
                session = s;
                break;
            }
        }
        if(session!=null){
            SendMessage(session, message);
        }
        else{
            log.warn("没有找到你指定ID的会话：{}",sessionId);
        }
    }

}
```

## NewsController

```java
package com.xm.facesystem.websocket;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;

@RestController
@RequestMapping("/news")
public class NewsController {

    @GetMapping("/send")
    public String send(){

//        Websocket.sendMessage("这是websocket群发消息！");
        try {
            WebSocketServer.BroadCastInfo("这是一个群发消息");
        } catch (IOException e) {
            e.printStackTrace();
        }
        return "发送消息成功";
    }


}
```

## websocket.vue

```html
<template>
  <div class="hello">
    <h1>测试webSocket</h1>
    <button @click="send">发消息</button>
  </div>
</template>

<script>
  export default {
    data() {
      return {
        websocketSend: "这是一个websocket的前端消息",
      };
    },
    name: "HelloWorld",
    props: {
      msg: String,
    },

    created() {
      // 页面创建生命周期函数
      this.initWebSocket();
    },
    destroyed: function () {
      // 离开页面生命周期函数
      this.websocketclose();
    },
    methods: {
      initWebSocket: function () {
        // WebSocket与普通的请求所用协议有所不同，ws等同于http，wss等同于https
        this.websock = new WebSocket("ws://127.0.0.1:8085/ws/asset");
        this.websock.onopen = this.websocketonopen;
        this.websock.onerror = this.websocketonerror;
        this.websock.onmessage = this.websocketonmessage;
        this.websock.onclose = this.websocketclose;
      },
      websocketonopen: function () {
        console.log("WebSocket连接成功");
      },
      websocketonerror: function () {
        console.log("WebSocket连接发生错误");
      },
      websocketonmessage: function (e) {
        console.log(e.data); // console.log(e);
      },
      websocketclose: function (e) {
        console.log("connection closed (" + e.code + ")");
      },
      send: function () {
        this.websock.send(this.websocketSend);
      },
    },
  };
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  h3 {
    margin: 40px 0 0;
  }
  ul {
    list-style-type: none;
    padding: 0;
  }
  li {
    display: inline-block;
    margin: 0 10px;
  }
  a {
    color: #42b983;
  }
</style>
```
