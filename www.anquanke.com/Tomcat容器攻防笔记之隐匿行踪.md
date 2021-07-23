> 原文链接: https://www.anquanke.com//post/id/225027 


# Tomcat容器攻防笔记之隐匿行踪


                                阅读量   
                                **170013**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01507eb625b357516d.jpg)](https://p2.ssl.qhimg.com/t01507eb625b357516d.jpg)



## 背景：

基于现阶段红蓝对抗强度的提升，诸如WAF动态防御、态势感知、IDS恶意流量分析监测、文件多维特征监测、日志监测等手段，能够及时有效地检测、告警甚至阻断针对传统通过文件上传落地的Webshell或需以文件形式持续驻留目标服务器的恶意后门。

结合当下形势，这次我们着重关注在Tomcat日志处理流程中，是否有可取巧的地方使得Tomcat不记录访问记录，进而达到隐匿行踪的效果。

声明 ：

由于传播或利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，此文仅作交流学习用途。

历史文章：

[Tomcat容器攻防笔记之Filter内存马](https://mp.weixin.qq.com/s/nPAje2-cqdeSzNj4kD2Zgw)<br>[Tomcat容器攻防笔记之Servlet内存马](https://mp.weixin.qq.com/s/rEjBeLd8qi0_t_Et37rAng)<br>[Tomcat容器攻防笔记之JSP金蝉脱壳](https://www.anquanke.com/post/id/224698)

## 一、Tomcat的日志类型

基于默认配置启动的Tomcat会在logs目录中产生以下五类日志：catalina、localhost、localhost_access、host-manager、manager
- catalina：记录了Catalina引擎的日志文件
- localhost：记录了Tomcat内部代码抛出的日志
- localhost_access: 记录了Tomcat的访问日志
- host-manager以及manager：记录的是Tomcat的webapps目录下manager的应用日志
既然是跟隐藏访问记录有关，本次对localhost_access日志的调用逻辑和调用流程进行调试学习



## 二、Tomcat记录访问日志的流程细节？

Tomcat是对客户端的请求完成响应后，再进行访问日志记录的。具体实现在CoyoteAdapter#service方法，下图第二个红框处。

[![](https://p3.ssl.qhimg.com/t0126b3ccb74fce47b9.png)](https://p3.ssl.qhimg.com/t0126b3ccb74fce47b9.png)

此处的Context变量其实是StandardContext，Host变量是StandardHost。然而，无论是StandardHost类还是StandardContext类，这两个容器实现类都继承于ContainerBase类。

[![](https://p4.ssl.qhimg.com/t015d9ba75a46a486f8.png)](https://p4.ssl.qhimg.com/t015d9ba75a46a486f8.png)

由于这两个子类，并没有重写自己的logAccess方法，因此这里调用的logAccess(request, response, time ,false)方法，其实是调用其父类ContainerBase的logAccess方法。

[![](https://p4.ssl.qhimg.com/t019391a824468c8fd8.png)](https://p4.ssl.qhimg.com/t019391a824468c8fd8.png)

代码逻辑很清晰，稍微说明一下调用顺序，Tomcat组件的日志记录是逐层回溯，从下往上调用的。

首先，从CoyoteAdapter#service()方法中，先由调用StandardContext实例的logAccess方法，所以上图的this第一次指代的是StandardContext自身，通过getAccessLog方法，获取StandardContext的日志记录对象。再调用log()方法，记录request、reponse、time中的信息。

那么当StandardContext调用完成日志记录后，进入下一个if逻辑。

通过StandContext.getParent方法，获取上级容器实现类StandardHost。如果有朋友好奇为什么是StandardHost的话，可以先了解一下Tomcat的Container架构，也可以阅读先前编写的文章。

当获取了上级容器实例后，再次调用logAccess方法，其实进入的是上图方法本身，直到达到最上级容器：this.getParent() == null 成立。

现在，我们了解了Tomcat调用日志记录的顺序，具体来看看细节。

[![](https://p4.ssl.qhimg.com/t0111276b8bdd13dd33.png)](https://p4.ssl.qhimg.com/t0111276b8bdd13dd33.png)

在Tomcat的/conf/server.xml的默认配置中，只存在localhost_access_log.txt用于记录请求的IP地址、时间、请求方式、URI、协议等信息。其中pattern字段决定日志的记录形式和记录内容。

对pattern字段内容感兴趣可查阅该官方链接：

[https://tomcat.apache.org/tomcat-7.0-doc/config/valve.html#Access_Logging](https://tomcat.apache.org/tomcat-7.0-doc/config/valve.html#Access_Logging)

该配置嵌于Host标签内，属于StandardHost类。可见默认情况，仅有StandardHost调用getAccessLog方法时返回日志记录对象。

[![](https://p0.ssl.qhimg.com/t017bb4cbc38c3d1c14.png)](https://p0.ssl.qhimg.com/t017bb4cbc38c3d1c14.png)

首先，this.accessLogScanComplete判断是否已完成配置文件中日志记录配置的扫描加载，如果扫描完成，则返回accessLog对象。若未扫描，则进行扫描加载。

在Tomcat的容器中，都有一个管道(PipeLine)及若干个阀（Valve），它们是容器类必须具备的模块，在容器对象生成时自动产生，Pipeline就像是每个容器的逻辑总线，在Pipeline上按照配置的顺序，加载各个valve并逐个调用，各个valve实现具体的功能逻辑。

而配置文件中的“org.apache.catalina.valves.AccessLogValve”，就是一个阀，实现日志记录的功能逻辑。

this.getPipeLine().getVales()方法获取当前管道中所有阀。通过else中的方法体，我们也可以了解到，可以自行编写继承于ValveBase类的阀，用于实现我们想要的功能，这里会通过判断阀的类型是否为AccessLog类型，获取管道中所有有关日志记录的阀实例，并保存到accessLog中，最后返回。

[![](https://p2.ssl.qhimg.com/t01aaddafe49818417a.png)](https://p2.ssl.qhimg.com/t01aaddafe49818417a.png)

当this.getAccessLog()的返回值accesssLog不为空时，是调用log方法实现日志记录。

[![](https://p3.ssl.qhimg.com/t018eaeb61ab9173d55.png)](https://p3.ssl.qhimg.com/t018eaeb61ab9173d55.png)

此处的this为accessLog自身，accessLog的类为AccessLogAdapter，真正的日记记录实现类，是其成员变量logs中的AccessLogValve，见下图。

[![](https://p1.ssl.qhimg.com/t0137fd81f538fc7739.png)](https://p1.ssl.qhimg.com/t0137fd81f538fc7739.png)

由于AccessLogValve并没有实现自己的log方法，在AccessLogAdapter#log中的log.log(request, response, time),调用的，其实是AccessLogValve的父类AbstractAccessLogValve的log方法。（org.apache.catalina.valves.AbstractAccessLogValve）

[![](https://p2.ssl.qhimg.com/t01c070fbbef44a0b30.png)](https://p2.ssl.qhimg.com/t01c070fbbef44a0b30.png)

在AbstractAccessLogValve#log方法中，满足逻辑条件，则最终记录日志信息。要想隐藏访问，避免记录入日志中，就要令这个log方法逻辑条件不成立。

在第一个IF条件中，改动前三个条件，会令该日志记录实现类失效，进而影响了正常功能，不建议改动。但后续2个条件，跟具体的request有关，并且是“或”判断，意味着，单独更改该类的成员属性condition和conditionIf不影响该类正常工作。

于是，我们可以通过改动this.condition和request.getAttribute(this.conditiion),或者this.conditionIf和request.getAttribute(this.conditiionIf)，令以上任一条件不成立，则第一个IF逻辑则无法进入，最终使得Tomcat不记录我们的访问记录。



## 三、实现行踪隐匿

经过前面分析，我们可以知道，日志记录，是在请求完成响应之后实施的。那么我们可以从Request中的MappingData获取StandardHost，通过Standardhost获取accessLog。

阅读过先前讲解Servlet内存马的朋友可能会好奇为何StandardService有MappingData，为何Request也有，MappingData作为记录映射关系的实例，也会最终传递给Request对象供其调用。

[![](https://p2.ssl.qhimg.com/t01e144eb7b8bee599e.png)](https://p2.ssl.qhimg.com/t01e144eb7b8bee599e.png)

因而我们无论是通过Filter、Servlet还是JSP，都拥有了ServletRequest对象。

但要注意的是，Tomcat采用的设计模式是门面模式，为了提高系统的独立性，将Request对象转换成了RequestFacade对象，转换之后，Request则不可见，用户操作的对象只能是RequestFacade。以此，通过门面实现了系统内部和外部操作对象的分离。

但是，因为门面实际上是为复杂的子系统为一个类提供一个简单的接口，对于RequestFacade对象而言，实际上完成操作的，仍然是Request对象，因而Request对象，自然而然会作为成员变量保存在RequestFacade对象之中。既然保存在其中，我们就可以通过Java的反射机制，越过访问控制权限，动态获取运行中实例的属性。

按照惯例，先把要导入的包说明一下：

```
&lt;%@ page import="org.apache.catalina.connector.Request" %&gt;
&lt;%@ page import="java.lang.reflect.Field" %&gt;
&lt;%@ page import="org.apache.catalina.mapper.MappingData" %&gt;
&lt;%@ page import="org.apache.catalina.core.StandardHost" %&gt;
&lt;%@ page import="org.apache.catalina.AccessLog" %&gt;
&lt;%@ page import="org.apache.catalina.valves.AbstractAccessLogValve" %&gt;
&lt;%@ page import="org.apache.catalina.core.AccessLogAdapter" %&gt;
```

获取Request对象。

```
Field requestF = request.getClass().getDeclaredField(“request”);
// requestFacade的request由protected修饰
requestF.setAccessible(true);
Request req = (Request) requestF.get(request);
```

获取MappingData和StandardHost：

```
MappingData mappingData = req.getMappingData();
StandardHost standardHost = (StandardHost) mappingData.host;
```

获取accesslog并赋值AccessLogValve.condition和Request.attributes :

```
AccessLogAdapter accessLog = (AccessLogAdapter) standardHost.getAccessLog();
    Field logsF = accessLog.getClass().getDeclaredField("logs");
    logsF.setAccessible(true);
    AccessLog[] logs = (AccessLog[]) logsF.get(accessLogAdapter);
    for( AccessLog log:logs )`{`
        ((AbstractAccessLogValve)log).setCondition("WhatEverYouWant");//任意填入
    `}`
request.setAttribute("WhatEverYouWant", "WhatEverYouWant");
```

PS：以上代码，可任意嵌入Filter、Servlet、JSP中，均可生效。

看看效果：

[![](https://p5.ssl.qhimg.com/t01f01039012325f75f.png)](https://p5.ssl.qhimg.com/t01f01039012325f75f.png)

[![](https://p2.ssl.qhimg.com/t01042c933cf600c4b5.png)](https://p2.ssl.qhimg.com/t01042c933cf600c4b5.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fd59bd1dd7326eab.png)
