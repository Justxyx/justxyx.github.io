
**状态码解释**
```json
{
    "code": 400    // 失败
    "code": 300    // 没有权限 请登录 返回后台管理登录界面
    "code": 200    // 成功
}
```

为方便测试，本项目提供云服务接口： 
`http://106.55.20.195:8086`


# 1. 成果

## 1.1 添加成果接口  （⭐️后台接口，需要登录）

1.方式

> **接口定义**： http://localhost:8080/addAchievements
> **请求方式**： Post
> **Content-Type**:  application/json       

2. form表单字段：

```java
     String resultName;   // 名称
     String patentCode;   // 编号
     String resultStage;  // 成果时期
     String turnWay;
     double supplyPrice;   // 价格
     String keyWords;
     String inventionPerson;
     String introduction;
     String contactName;
     String contactMobile;
     String contactEmail;
     String contactAddress;
     String dataSource;
     String industryName;
```

**基本与现有成果页面字段一一对应，时间由后台自动生成，如下**
![p1](/Users/xiaoyingxiong/blog/justxyx.github.io/assets/ims/2022.01/p4.png)

3. 返回内容


成功

```json
{
    "code": 200,
    "msg": "achievements 添加成功",
    "count": 0,
    "data": null
}
```

失败

```json
{
    "code": 400,
    "msg": "achievements 添加失败",
    "count": 0,
    "data": null
}
```

没有权限
```json
{
code: 300,
msg: "没有权限，请登录",
count: -1,
data: null
}
```


## 1.2 查询成果接口

1. 方式

> **接口定义**： http://localhost:8080/findAllAchievements/cureentPage/pageSize
> **请求方式**： Get

|字段名|字段含义|备注|
|-|-|-|
|cureentPage|当前页面||
|pageSize|页面大小||

2. 示例
`url:http://localhost:8080/findAllAchievements/1/1`

```json

{
code: 200,
msg: "查询成功",
count: -1,
data: {
resultName: "植物硒系列成果专利转让",
patentCode: "CN201410165494.9",
resultStage: "成熟期",
turnWay: "技术转让;",
supplyPrice: 50,
keyWords: "植物硒",
inventionPerson: "汪超 ",
introduction: "本发明公开了一种富硒发芽米骨酱及其制备方法。该方法通过富硒糙米发芽转化法将无机硒转化为主要以含硒蛋白的形式存在于有机体中的有机硒；利用微生物发酵降解骨头中的蛋白质、多糖，使部分钙从结合态变为游离态；采用复合动物骨原料提升胶原蛋白、氨基酸、核苷酸等营养物质的含量；将骨头集中起来进行加工成营养保健品不仅可以变废为宝，还解决了废弃骨头造成环境污染等问题。",
contactName: "杨磊",
contactMobile: "18971681181",
contactEmail: "18971681181@163.com",
contactAddress: "武汉市南湖李家墩一村特1号",
dataSource: "湖北工业大学",
checkTime: "2021-06-09T14:57:19.000+08:00",
industryName: "农、林、牧、渔业,制造业,",
id: 180,
examine: 0
}
}
```


3. 提供前端分页数据

```c
pageNo: 1,  // 当前页面
pageSize: 1, // 每页显示条数
totalPage: 38, // 共有几页
rows: 38   // 共条数
```

4. 几点说明 
`examine` 为保留字段 审核用 
`examine` 为服务器自动生成上传时间
`id` 为主键 数据库自增

## 1.3 根据id查询成果

1. 方式

> **接口定义**： http://localhost:8080/findAchievementsById/id
> **请求方式**： Get

|字段名|字段含义|备注|
|-|-|-|
|id|成果id||

2. 示例

url:http://localhost:8080/findAchievementsById/180

含义： 查询id编号为180的成果详细信息

3. 返回

**成功**

```json
{
code: 200,
msg: "查询成功",
count: -1,
data: {
resultName: "植物硒系列成果专利转让",
patentCode: "CN201410165494.9",
resultStage: "成熟期",
turnWay: "技术转让;",
supplyPrice: 50,
keyWords: "植物硒",
inventionPerson: "汪超 ",
introduction: "本发明公开了一种富硒发芽米骨酱及其制备方法。该方法通过富硒糙米发芽转化法将无机硒转化为主要以含硒蛋白的形式存在于有机体中的有机硒；利用微生物发酵降解骨头中的蛋白质、多糖，使部分钙从结合态变为游离态；采用复合动物骨原料提升胶原蛋白、氨基酸、核苷酸等营养物质的含量；将骨头集中起来进行加工成营养保健品不仅可以变废为宝，还解决了废弃骨头造成环境污染等问题。",
contactName: "杨磊",
contactMobile: "18971681181",
contactEmail: "18971681181@163.com",
contactAddress: "武汉市南湖李家墩一村特1号",
dataSource: "湖北工业大学",
checkTime: "2021-06-09T14:57:19.000+08:00",
industryName: "农、林、牧、渔业,制造业,",
id: 180,
examine: 0
}
}
```

**失败**

```json
{
code: 400,
msg: "查询失败",
count: -1,
data: null
}
```

## 1.4 根据id删除成果（⭐️后台接口，需要登录）

1. 方式

> **接口定义**： http://localhost:8080/deleteAchievementById/id
> **请求方式**： Get

|字段名|字段含义|备注|
|-|-|-|
|id|成果id||

2. 示例

url:http://localhost:8080/deleteAchievementById/180

含义： 删除id编号为180的成果

3. 返回

**成功**

```json
{
code: 200,
msg: "删除成功",
count: -1,
data: null
}
```

**失败**
```json
{
code: 400,
msg: "删除失败",
count: -1,
data: null
}
```

# 2 需求

## 2.1 添加需求 （⭐️后台接口，需要登录）


1.方式

> **接口定义**： http://localhost:8080/addDemand
> **请求方式**： Post
> **Content-Type**:  application/json       

2. form表单字段：

```java
     String title;
     String centerName;
     String memo;
     String keyWords;
     String contactName;
     String contactMobi;
     String contactEmail;
     String contactAddr;
     String industryName;
     String domainName;
     String cooperationWay;
     String technicalMatter;
     String technicalTarget;
     String existingSituation;
```

**基本与现有成果页面字段一一对应**


3. 返回内容


成功

```json
{
    "code": 200,
    "msg": "demand 添加成功",
    "count": 0,
    "data": null
}
```

失败

```json
{
    "code": 400,
    "msg": "demand 添加失败",
    "count": 0,
    "data": null
}
```


## 2.2 查询需求接口 

1. 方式

> **接口定义**： http://localhost:8080/findAllDemand/cureentPage/pageSize
> **请求方式**： Get

|字段名|字段含义|备注|
|-|-|-|
|cureentPage|当前页面||
|pageSize|页面大小||

2. 示例
`url:http://localhost:8080/findAllDemand/1/1`

```json
{
code: 200,
msg: "查询成功",
count: 35,
data: {
lists: [
{
title: "智能终端行业应用及物联网开发应用",
centerName: "科惠网荆州区域",
memo: "<p>手机，平板，车机，广告机，教育应用及各行业终端查询机的智能硬件。</p><p>物联网多平台应用，智能等各终端设备开发及应用。</p>",
keyWords: "智能终端 智能硬件 物联网设备",
contactName: "占生",
contactMobi: "13798526559",
contactEmail: "41173699@qq.com",
contactAddr: "荆州市监利市容城镇经济开发区发展大道特8号",
industryName: "制造业,信息传输、计算机服务和软件业,",
domainName: "电子信息,先进制造与自动化,高新技术服务,",
cooperationWay: "合作开发,研发平台,技术改造(设备、研发生产条件),",
technicalMatter: "<p>与各终端设备的通讯，适配及软件的开发和优化。</p>",
technicalTarget: "<p>实现所有智能终端设备万物互联，更快捷，更方便，更简单的用户体验。</p>",
existingSituation: "<p>现有千级无尘车间7000平方，百级无尘车间3000平方。</p><p>各种生产使用设备200余套，专业技术人员30余人，员工150余人。</p>",
id: 44,
examine: 0,
checkTime: "2021-06-11T01:16:12.000+08:00"
}
],
pageNo: 1,
pageSize: 1,
totalPage: 35,
rows: 35
}
}
```

## 2.3 根据id查询需求

> **接口定义**： http://localhost:8080/findDemandById/id
> **请求方式**： get

|字段名|字段含义|备注|
|-|-|-|
|id|需求id||

## 2.4 根据id删除需求 （⭐️后台接口，需要登录）


> **接口定义**： http://localhost:8080/deleteDemandById/id
> **请求方式**： get

|字段名|字段含义|备注|
|-|-|-|
|id|需求id||


# 3. 专家

## 3.1 添加专家 （⭐️后台接口，需要登录）


1. 方式
> **接口定义**： http://localhost:8080/addExpert
> **请求方式**： Post

2. 字段

```c
     String name;
     int sex;    // 1 男  0 女
     String mobile;
     String email;
     String address;
     String topDegree;
     String post;
     String serveWilling;
     String subjectName;
     String expertIntro;   // 专家描述信息
```

3. 返回值

 略 同上

 ## 3.2 查询专家接口

1. 方式

> **接口定义**： http://localhost:8080/findAllExpert/cureentPage/pageSize
> **请求方式**： Get

|字段名|字段含义|备注|
|-|-|-|
|cureentPage|当前页面||
|pageSize|页面大小||


## 3.3 根据id查询专家

> **接口定义**： http://localhost:8080/findExpertById/id
> **请求方式**： get

|字段名|字段含义|备注|
|-|-|-|
|id|专家id||

## 3.4 根据id删除专家 （⭐️后台接口，需要登录）


> **接口定义**： http://localhost:8080/deleteExperttById/id
> **请求方式**： get

|字段名|字段含义|备注|
|-|-|-|
|id|需求id||


# 4 通知公告

## 4.1 添加通知 （⭐️后台接口，需要登录）


1. 方式
> **接口定义**： http://localhost:8080/addNews/0
> **请求方式**： Post

2. 字段

```c
     String title;  // 标题
     String source;   // 来源
     String author;  // 作者
     String imgPath;   //  保留字段  oss 云服务器图片存储 暂无
     String content;   // 新闻内容  每段以<p></p> 标签包裹  方便前端分段显示
```

3. 返回值
    上同，暂略

## 4.2 通知查询

1. 方式
> **接口定义**： http://localhost:8080/findAllNews/0/pageNo/pageSize
> **请求方式**： Get

|字段名|字段含义|备注|
|-|-|-|
|cureentPage|当前页面||
|pageSize|页面大小||

2. 示例

url: http://localhost:8080/findAllNews/0/1/1

返回：

~~~json
{
code: 200,
msg: "查询成功",
count: 36,
data: {
lists: [
{
id: 47,
title: "通知公告__中国科协等13部门关于举办2021年全国科普日活动的通知",
time: "2022-01-07T13:55:17.000+08:00",
source: "锐科技",
author: "周杰伦",
imgPath: null,
content: "<p>2021全国科普日主题为：百年再出发，迈向高水平科技自立自强。定于9月11-17日在全国各地集中开展。各地各部门可根据全国活动主题，结合工作实际拟定活动副主题，主题宣传活动贯穿全年。 </p><p>（一）围绕建党百年，回望创新发展。围绕建党百年，结合党史学习教育，回顾科技创新、科学普及在党和国家事业发展、社会文明进步和人民生活水平提升等方面取得的辉煌成就，立足新起点，展望和谋划科普服务高质量发展的新征程。 </p><p>（二）弘扬科学精神，激发科学梦想。弘扬科学精神，传播科学知识、激发科学梦想、涵养创新生态，在全社会营造热爱科学、尊重创新的环境，推动形成崇尚科学的风尚，为实现高水平科技自立自强提供基础支撑。</p>",
type: 0,
examine: 0
}
],
pageNo: 1,
pageSize: 1,
totalPage: 36,
rows: 36
}
}
~~~


## 4.3 根据id查询通知

> **接口定义**： http://localhost:8080/findNewsById/id
> **请求方式**： get

|字段名|字段含义|备注|
|-|-|-|
|id|通知id||

## 4.4 根据id删除通知 （⭐️后台接口，需要登录）


> **接口定义**： http://localhost:8080/deleteNewsById/id
> **请求方式**： get

|字段名|字段含义|备注|
|-|-|-|
|id|通知id||




# 5 科技资讯

## 5.1 添加资讯 （⭐️后台接口，需要登录）


1. 方式
> **接口定义**： http://localhost:8080/addNews/1
> **请求方式**： Post

2. 字段

```c
     String title;  // 标题
     String source;   // 来源
     String author;  // 作者
     String imgPath;   //  保留字段  oss 云服务器图片存储 暂无
     String content;   // 新闻内容  每段以<p></p> 标签包裹  方便前端分段显示
```

3. 返回值
    上同，暂略


## 5.2 资讯查询

1. 方式
> **接口定义**： http://localhost:8080/findAllNews/1/pageNo/pageSize
> **请求方式**： Get

|字段名|字段含义|备注|
|-|-|-|
|cureentPage|当前页面||
|pageSize|页面大小||

## 5.3 根据id查询资讯

> **接口定义**： http://localhost:8080/findNewsById/id
> **请求方式**： get

|字段名|字段含义|备注|
|-|-|-|
|id|资讯id||

## 5.4 根据id删除资讯 （⭐️后台接口，需要登录）


> **接口定义**： http://localhost:8080/deleteNewsById/id
> **请求方式**： get

|字段名|字段含义|备注|
|-|-|-|
|id|资讯id||


# 6. 后台管理

## 6.1 登录
1. 方式
> **接口定义**： http://localhost:8080/login
> **请求方式**： Post

2. 字段

|字段名|字段含义|备注|
|-|-|-|
|name|用户名|默认为:root|
|password|密码|默认为:password|


3. 登录成功后返回cookie给浏览器
**所有的后台管理接口都需要登录后才能调用,如未登录则报返回300状态码**

4. 返回内容

成功

```json
{
    "code": 200,
    "msg": "登录成功",
    "count": -1,
    "data": null
}
```

用户名错误
```json
{
    "code": 400,
    "msg": "用户名错误",
    "count": -1,
    "data": null
}
```

密码错误
```json
{
    "code": 400,
    "msg": "密码错误",
    "count": -1,
    "data": null
}
```

## 6.2 一点备注

提供一个通用接口，获得cookie

> **接口定义**： http://localhost:8080/test
> **请求方式**： get

获得cookie后浏览器即可访问所有后台接口，方便开发。

