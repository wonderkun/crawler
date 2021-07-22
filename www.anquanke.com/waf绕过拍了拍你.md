> 原文链接: https://www.anquanke.com//post/id/212272 


# waf绕过拍了拍你


                                阅读量   
                                **226922**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t0126297310b2ec652d.png)](https://p2.ssl.qhimg.com/t0126297310b2ec652d.png)



## 前言

一个安静的下午，和往常一样，逛着各大安全论坛，翻看新出的漏洞资讯，等待着下班。然而，一声不同寻常的微信消息提示音突然在我耳边响起。我立马打开微信看看是谁在这个时候找我。

[![](https://p3.ssl.qhimg.com/t01b9cf2319b0ad10d6.png)](https://p3.ssl.qhimg.com/t01b9cf2319b0ad10d6.png)

妹子的要求不敢拒绝，身为菜鸡的我准备立马去学习一波waf绕过姿势。

[![](https://p1.ssl.qhimg.com/t01ba1c8ca8c5537efc.png)](https://p1.ssl.qhimg.com/t01ba1c8ca8c5537efc.png)



## 知己知彼，了解什么是waf

身为一名合格的渗透测试人员，想要绕过waf，我们就先得先了解什么是waf。

Waf = Web Application Firewall ，web应用防火墙，简单来说就是在http协议层面对我们的数据包进行检测，如果发现了可能是带有攻击性的语句，就会进行拦截。

[![](https://p4.ssl.qhimg.com/t01235e48e642df8606.png)](https://p4.ssl.qhimg.com/t01235e48e642df8606.png)

为了不让waf发现我们的意图，我们通常可以利用以下几种方式绕过waf检测



## 对抗规则绕过

原理：匹配不到恶意语句就不会拦截。

**对关键字进行不同编码**

**对关键字进行大小写变换**

**通过其他语义相同的关键字替换**

除了通过编码等价替换等方式绕过检测，我们还能配合目标特性实现绕过检测

**配合Windows特性**

[![](https://p3.ssl.qhimg.com/t011909551745eeaf2b.png)](https://p3.ssl.qhimg.com/t011909551745eeaf2b.png)

[![](https://p2.ssl.qhimg.com/t01240b1bfc8f85cd4b.png)](https://p2.ssl.qhimg.com/t01240b1bfc8f85cd4b.png)

[![](https://p1.ssl.qhimg.com/t01e9302e14d56f2bcc.png)](https://p1.ssl.qhimg.com/t01e9302e14d56f2bcc.png)

**配合Linux特性**

[![](https://p1.ssl.qhimg.com/t0104bc9a6262417377.png)](https://p1.ssl.qhimg.com/t0104bc9a6262417377.png)

[![](https://p1.ssl.qhimg.com/t014c82161992724ed5.png)](https://p1.ssl.qhimg.com/t014c82161992724ed5.png)

[![](https://p0.ssl.qhimg.com/t016c46e5a222cec34d.png)](https://p0.ssl.qhimg.com/t016c46e5a222cec34d.png)

[![](https://p5.ssl.qhimg.com/t016cb8a6353979a35a.png)](https://p5.ssl.qhimg.com/t016cb8a6353979a35a.png)

Shell反弹也可以配合特性使用

**配合Mysql特性**

/**/数据库注释符，中间部分被注释，可用于截断关键字，干扰waf匹配

//*!*//内联注释，中间部分继续执行，mysql特有

%0a换行与#单行注释符配合使用

**配合过滤代码或漏洞本身**

关键字被过滤，双写关键字

通过chr()函数变换关键字

通过base_convert() 函数变换关键字

## http协议绕过

原理：理解不了恶意语句就不会拦截

**Content-Type绕过**

有的waf 识别到Content-Type类型为multipart/form-data后，会将它认为是文件上传请求，从而不检测其他种类攻击只检测文件上传，导致被绕过。

**HTTP请求方式绕过**

waf在对危险字符进行检测的时候，分别为post请求和get请求设定了不同的匹配规则，请求被拦截，变换请求方式有几率能绕过检测

Ps:云锁/安全狗安装后默认状态对post请求检测力度较小，可通过变换请求方式绕过

**参数污染绕过**

由于http协议允许同名参数的存在，同时waf的处理机制对同名参数的处理方式不同，造成“参数污染”。不同的服务器搭配会对传递的参数解析出不同的值。配合waf与中间件对参数解析位置不同，可能绕过waf。

**解析特性绕过**

原理：利用waf与后端服务器的解析不一致。

Iis5.0-6.0解析漏洞

Iis7.5解析漏洞(php.ini开启fix_pathinfo)

apache解析漏洞

nginx解析漏洞(php.ini开启fix_pathinfo)

**多Content-Disposition绕过**

请求包中包含多个Content-Disposition时，中间件与waf取值不同 。

[![](https://p4.ssl.qhimg.com/t0140a43c6aee494b5a.png)](https://p4.ssl.qhimg.com/t0140a43c6aee494b5a.png)

**解析兼容性绕过**

在http协议中，标准的文件名的形式为filename=”1.php”,但是web容器会在解析协议时做一些兼容，文件上传时，有的waf只按照标准协议去解析，解析不到文件名，从而被绕过。

**keep-alive（Pipeline）绕过**

原理:http请求头部中有Connection这个字段，建立的tcp连接会根据此字段的值来判断是否断开，我们可以手动将此值置为keep-alive，然后在http请求报文中构造多个请求，将恶意代码隐藏在第n个请求中，从而绕过waf。

[![](https://p5.ssl.qhimg.com/t017870cb158094de88.png)](https://p5.ssl.qhimg.com/t017870cb158094de88.png)

发送两个请求，但绕过失败，被云锁拦截，此种方法现在基本失效。

[![](https://p1.ssl.qhimg.com/t0124484f4baeb4b43f.png)](https://p1.ssl.qhimg.com/t0124484f4baeb4b43f.png)

**分块传输绕过**

原理:分块编码传输将关键字and,or,select ,union等关键字拆开编码，绕过waf等安全设备的检测，但无法绕过代码本身的检测。

[![](https://p0.ssl.qhimg.com/t011d9466331b4b034a.png)](https://p0.ssl.qhimg.com/t011d9466331b4b034a.png)

**修改编码方式：Charset绕过**

原理:大部分的WAF默认用UTF8编码检测，修改编码方式可能会绕过waf，例如设置charset为ibm037

[![](https://p1.ssl.qhimg.com/t01556277e3845c1b25.png)](https://p1.ssl.qhimg.com/t01556277e3845c1b25.png)



## Waf检测限制绕过

原理：超出waf检测能力部分不会拦截

**参数溢出**

原理:通过增加传递得参数数量，达到waf检测上限，超出的参数就可绕过waf了。可绕一些轻量级waf，如phpstudy自带waf。

设置拦截关键字

[![](https://p1.ssl.qhimg.com/t0130f75c39f801184f.png)](https://p1.ssl.qhimg.com/t0130f75c39f801184f.png)

添加参数数量，成功绕过。

[![](https://p0.ssl.qhimg.com/t01247faf63cb63a5d7.png)](https://p0.ssl.qhimg.com/t01247faf63cb63a5d7.png)

**缓冲区溢出**

原理:当服务器可以处理的数据量大于waf时，这种情况可以通过发送大量的垃圾数据将 WAF 溢出，从而绕过waf。



## 网络结构绕过

原理：不经过安全设备就不会拦截

**源ip绕过**

原理：直接对源地址发起攻击，流量不会经过waf，从而成功绕过。

正常访问流量

[![](https://p5.ssl.qhimg.com/t01a2bc2ca917145445.png)](https://p5.ssl.qhimg.com/t01a2bc2ca917145445.png)

攻击者流量

[![](https://p2.ssl.qhimg.com/t0189bef78014f156e6.png)](https://p2.ssl.qhimg.com/t0189bef78014f156e6.png)

**同网段/ssrf绕过**

同理, 因同网段的流量属于局域网，可能不经过waf的检测

[![](https://p5.ssl.qhimg.com/t014204fdb2f2b278ad.png)](https://p5.ssl.qhimg.com/t014204fdb2f2b278ad.png)

通过服务器A自身或B的ssrf漏洞，从网络内部发起攻击流量

[![](https://p1.ssl.qhimg.com/t01d6175ad024217e16.png)](https://p1.ssl.qhimg.com/t01d6175ad024217e16.png)



## 学以致用（云锁绕过实战）

为了在帮妹子绕过的时候不掉链子，咱们还是简单的来过一过云锁，看看学到的方法到底在实际情况中有没有利用价值

### **环境介绍**

环境： mysql+apache+php

云锁版本：公有云版Linux_3.1.20.15

更新日期：2020-04-27

测试过程 为了更好的模拟攻击，下面是为测试编写的18行代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e378b8288bf1d139.png)

首先判断判断注入点，and 1=1 ，看来出师不利，被拦截了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f6592ae6cf4ed5db.png)

修改payload
<td data-row="1">**大小写AnD 1=1拦截**</td>
<td data-row="2">大小写+内敛</td><td data-row="2">/!**ANd**/ 1=1</td><td data-row="2">拦截</td>

尝试变换一下and的形式，waf没有继续拦截，应该是使用正则匹配到了关键字
<td data-row="1">**Axnxd不拦截**</td>
<td data-row="2">等价替换</td><td data-row="2">&amp;&amp;1</td><td data-row="2">不拦截</td>

看来常用的内敛注释+普通注释无法绕过云锁对关键字的匹配

[![](https://p1.ssl.qhimg.com/t01c12bf01a71ad33b1.png)](https://p1.ssl.qhimg.com/t01c12bf01a71ad33b1.png)

我们先fuzz一下看看哪些关键字被拦截了，经过测试可以看到，大部分字符单独存在不会被拦截。

例如 order by 被拦截既不是order 触发了waf,也不是by，是它们的组合触发了waf。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011ae1abac010a6d20.png)

### **姿势一 规则对抗绕过**

原理:注释+换行绕过

既然如此，这里我们可以通过

\1. 使用%23将后面的内容给注释掉

\2. 使用%0a将后面的内容进行换行，使后面的sql语句逃出注释就能继续执行了

遇到关键函数被拦截，就在其中插入注释与换行。

在数据库中查询情况如下图所示

[![](https://p3.ssl.qhimg.com/t019c8db3b25ada25e4.png)](https://p3.ssl.qhimg.com/t019c8db3b25ada25e4.png)

使用order by判断出存在2列

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0135662f42eb5542a4.png)

使用相同方法查询出用户名和数据库

[![](https://p5.ssl.qhimg.com/t015d3fe4f1c2b6f316.png)](https://p5.ssl.qhimg.com/t015d3fe4f1c2b6f316.png)

知道当前数据库名称后，可以利用information_schema数据库获取当前数据库中存在的表。如下图所示

[![](https://p1.ssl.qhimg.com/t01da2af8527365089a.png)](https://p1.ssl.qhimg.com/t01da2af8527365089a.png)

接下来就是列名与dump数据

[![](https://p2.ssl.qhimg.com/t01f4b47702b7af2ac7.png)](https://p2.ssl.qhimg.com/t01f4b47702b7af2ac7.png)

### **姿势二 http协议绕过**

既然waf拦截组合，那我们通过分块传输将关键字分块

首先将请求方式变为post并抓包，修改数据包为分段传输格式

注意:这里Transfer-Encoding:的值设为x chunked而不是chunked

构造sql语句判断字段数

[![](https://p4.ssl.qhimg.com/t018624466509983025.png)](https://p4.ssl.qhimg.com/t018624466509983025.png)

分割union select查询出数据库

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0158d2dc53a5647718.png)

成功爆出表名

[![](https://p5.ssl.qhimg.com/t01c6eb174032d3df62.png)](https://p5.ssl.qhimg.com/t01c6eb174032d3df62.png)

后面继续构造sql语句爆出列名与详细数据

[![](https://p4.ssl.qhimg.com/t011d19539cc25595a6.png)](https://p4.ssl.qhimg.com/t011d19539cc25595a6.png)



## 再回正题（zzzcmsV1.7.5前台rce）

激动的心，颤抖的手，怀着忐忑的心情，打算告诉妹子我准备好了，点开她的头像，拍了拍她

[![](https://p5.ssl.qhimg.com/t01f87f0879f8f12254.png)](https://p5.ssl.qhimg.com/t01f87f0879f8f12254.png)

只需要拿下站点，她可能会表示感谢请我吃一顿饭，然后…

[![](https://p2.ssl.qhimg.com/t01375968360739eec0.png)](https://p2.ssl.qhimg.com/t01375968360739eec0.png)

我们打开了站点，先根据妹子提供poc，先执行一波phpinfo，无法执行

[![](https://p2.ssl.qhimg.com/t01f09531700a33c3e4.png)](https://p2.ssl.qhimg.com/t01f09531700a33c3e4.png)

进一步测试执行其他命令也返回了403，应该是被waf拦了

[![](https://p4.ssl.qhimg.com/t0113bdfa1dd5c8d0c5.png)](https://p4.ssl.qhimg.com/t0113bdfa1dd5c8d0c5.png)

fuzz一波发现关键函数和一些常用命令被拦的拦，过滤的过滤，反正就是都没成功执行

[![](https://p4.ssl.qhimg.com/t011c7fee36a258264d.png)](https://p4.ssl.qhimg.com/t011c7fee36a258264d.png)

黑盒无果，准备审计一波源码

根据版本官网提供的源码定位到了如下过滤函数的位置，跟踪danger_key，看看都过滤了什么

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f67799f86e8d5000.png)

不看不知道，一看吓一跳，啥东西，这开发绝对是作了宁错杀也不可放过的准备（php都给给过滤了，怪不得phpinfo都没法执行）

分析了下这个函数，关键字被替换为*，单引号和双引号被转义，只要不出现关键字单引号和双引号就OK了

[![](https://p1.ssl.qhimg.com/t0131db757a1b0de339.png)](https://p1.ssl.qhimg.com/t0131db757a1b0de339.png)

经过一番咨询，大佬告诉我还有array_map这个函数也可以执行命令，光有函数还不行，常用命令也被拦截，为了执行命令，首先把phpinfo从32进制转换为10进制

[![](https://p3.ssl.qhimg.com/t010f63cafc8ff86bef.png)](https://p3.ssl.qhimg.com/t010f63cafc8ff86bef.png)

再通过php中的base_convert函数，再把10进制转为32进制，这样就能绕过waf与网站本身的检测，一箭双雕，构造好的poc如下

通过构造好的poc，我们成功执行phpinfo命令

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0115f834aaa51e3462.png)

接下来的通过相同操作将一句话copy进网站根目录，成功拿到shell

拿到shell心情美滋滋！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016e5caaef07080785.png)



## 总结

见招拆招， Impossible ==&gt; I’m possible
