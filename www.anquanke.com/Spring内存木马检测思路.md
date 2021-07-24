> 原文链接: https://www.anquanke.com//post/id/239868 


# Spring内存木马检测思路


                                阅读量   
                                **144215**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01cf9b2555dd0196dc.png)](https://p0.ssl.qhimg.com/t01cf9b2555dd0196dc.png)



## 一、内存马概念介绍

木马或是内存马，都是攻击者在“后门阶段”的一种利用方式。按攻击者的攻击套路顺序，“后门阶段”一般是在攻击者“拿到访问权”或是“提权”之后的下一步动作，也叫“权限维持”。

业界通常将木马的种类划分成“有文件马”和“无文件马”两类。“有文件马”也就是我们常见的“二进制木马、网马”；“无文件马”是无文件攻击的一种方式，其常见的类型有：内存马、隐蔽恶意代码启动等。



## 二、Spring可利用点

[![](https://p1.ssl.qhimg.com/t0142fca09e80448bb7.jpg)](https://p1.ssl.qhimg.com/t0142fca09e80448bb7.jpg)

从上面可以看到通过getHandler获取HandlerExecutionChain,获取处理器适配器HandlerAdapter执行HandlerAdapter处理一系列的操作，如：参数封装，数据格式转换，数据验证等操作。

然后执行handler

ha.handle(processedRequest, response, mappedHandler.getHandler());

最后返回直接结果。

获取Handler过程中发现会从AbstractHandlerMethodMapping#lookupHandlerMethod（）方法获取对应MappingRegistry() 中的HandlerMethod。

MappingRegistry有对应的开放的注册方法：

[![](https://p4.ssl.qhimg.com/t0194c871b11349f495.jpg)](https://p4.ssl.qhimg.com/t0194c871b11349f495.jpg)

如此便可以使用springContext动态注入HandlerMethod。

注入代码：

[![](https://p0.ssl.qhimg.com/t01bd21f00a71f4d255.jpg)](https://p0.ssl.qhimg.com/t01bd21f00a71f4d255.jpg)

ThreatClass：

[![](https://p3.ssl.qhimg.com/t016f7a7a67e0834b11.png)](https://p3.ssl.qhimg.com/t016f7a7a67e0834b11.png)

内存马注入后执行任意命令：

[![](https://p2.ssl.qhimg.com/t0168d109b6c6dffe19.png)](https://p2.ssl.qhimg.com/t0168d109b6c6dffe19.png)



## 三、检测思路

流程图：

[![](https://p0.ssl.qhimg.com/t01c975a226685df4e0.png)](https://p0.ssl.qhimg.com/t01c975a226685df4e0.png)

1、使用java Agent探针动态注入防御agent到应用进程中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0179328160968acfdb.jpg)

2、被注入的agent（符合jvm规范），JVM会回调agentmain方法并注入Instrumentation。Instrumentation中有一个api能够加载出运行时JVM中所有的class

```
public Class[] getAllLoadedClasses() `{`

    return this.getAllLoadedClasses0(this.mNativeAgent);

`}`

private native Class[] getAllLoadedClasses0(long var1);
```

3、拿到运行时的类根据高风险父类、接口、注解做扫描，把扫描到的类反编译为明文的java文件

[![](https://p0.ssl.qhimg.com/t018e94e026d3d5c7b4.jpg)](https://p0.ssl.qhimg.com/t018e94e026d3d5c7b4.jpg)

4、发现明显的敏感操作

```
Runtime.getRuntime().exec()

cmd.exe /c

/bin/bash -c
```

且磁盘源class文件不存在

URL url = clazz.getClassLoader().getResource(classNamePath);

url为空磁盘上没有对应文件。

证明此classs就是内存木马并记录

5、卸载自身实例

风险父类

org.springframework.web.method.HandlerMethod

风险接口

org.springframework.web.HttpRequestHandler

风险注解

org.springframework.stereotype.Controller

org.springframework.web.bind.annotation.RestController

org.springframework.web.bind.annotation.RequestMapping

org.springframework.web.bind.annotation.GetMapping

org.springframework.web.bind.annotation.PostMapping

org.springframework.web.bind.annotation.PatchMapping

org.springframework.web.bind.annotation.PutMapping

org.springframework.web.bind.annotation.Mapping
