> 原文链接: https://www.anquanke.com//post/id/195016 


# 多种姿势openrasp命令执行绕过


                                阅读量   
                                **1603400**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t012b1bfb13be0028d0.png)](https://p3.ssl.qhimg.com/t012b1bfb13be0028d0.png)



## 概述

随着Web应用攻击手段变得复杂，基于请求特征的防护手段，已经不能满足企业安全防护需求。Gartner在2014年提出了应用自我保护技术（RASP）的概念，即将防护引擎嵌入到应用内部，不再依赖外部防护设备。OpenRASP是该技术的开源实现，可以在不依赖请求特征的情况下，准确的识别代码注入、反序列化等应用异常，很好的弥补了传统设备防护滞后的问题。（来自官网：[https://rasp.baidu.com/](https://rasp.baidu.com/) 的介绍）



## 安装配置

从[https://packages.baidu.com/app/openrasp/release/](https://packages.baidu.com/app/openrasp/release/) 此处我们下载最新版本1.2.3。选择rasp-java.zip。下载后[https://rasp.baidu.com/doc/install/manual/spring-boot.html](https://rasp.baidu.com/doc/install/manual/spring-boot.html) 参考此文档配置springboot版本。为实验方便我们只需配置单机版本。[https://dwz.cn/HS4sCdfL](https://dwz.cn/HS4sCdfL) 开启拦截参考此处。此处我们将所有的命令执行设置为block。springboot文件从此处下载 链接：[https://pan.baidu.com/s/1SHB4LLLFl67SCKSxB1rQ0w](https://pan.baidu.com/s/1SHB4LLLFl67SCKSxB1rQ0w) 提取码：po1e

[![](https://p1.ssl.qhimg.com/t014c0072d5339de1a5.png)](https://p1.ssl.qhimg.com/t014c0072d5339de1a5.png)

[![](https://p0.ssl.qhimg.com/t01f23992f6175b3737.png)](https://p0.ssl.qhimg.com/t01f23992f6175b3737.png)



# <a class="reference-link" name="%E6%B5%8B%E8%AF%95"></a>测试

开启服务后，访问[http://127.0.0.1:8877/hello2?a=ping%20baidu.com](http://127.0.0.1:8877/hello2?a=ping%20baidu.com) 和 [http://127.0.0.1:8877/hello3](http://127.0.0.1:8877/hello3) 可以看到都会正常拦截。

[![](https://p3.ssl.qhimg.com/t01491c26055ba21334.png)](https://p3.ssl.qhimg.com/t01491c26055ba21334.png)

其中代码如下，hello2介绍参数执行命令，hello3内部执行命令均会被拦截。

[![](https://p4.ssl.qhimg.com/t01649cad01627306c1.png)](https://p4.ssl.qhimg.com/t01649cad01627306c1.png)

[![](https://p3.ssl.qhimg.com/t017271b8086c1ed718.png)](https://p3.ssl.qhimg.com/t017271b8086c1ed718.png)



## 绕过方式1

访问[http://127.0.0.1:8877/hello1?a=ping%20baidu.com](http://127.0.0.1:8877/hello1?a=ping%20baidu.com) 可以看到正常返回。

[![](https://p4.ssl.qhimg.com/t01f8b6d3e43337beb8.png)](https://p4.ssl.qhimg.com/t01f8b6d3e43337beb8.png)

后台执行命令成功。

[![](https://p3.ssl.qhimg.com/t01ac10803258221394.png)](https://p3.ssl.qhimg.com/t01ac10803258221394.png)

代码如下：

[![](https://p0.ssl.qhimg.com/t01dc7788570e51eced.png)](https://p0.ssl.qhimg.com/t01dc7788570e51eced.png)

此处我们开启一个线程来执行命令。下面看看为什么能够绕过。我们开启debug

[![](https://p2.ssl.qhimg.com/t018d126b69c61be775.png)](https://p2.ssl.qhimg.com/t018d126b69c61be775.png)

[![](https://p1.ssl.qhimg.com/t010a53b4b32407df45.png)](https://p1.ssl.qhimg.com/t010a53b4b32407df45.png)

我们在ProcessBuilderHook.java的checkCommand处打断点。因为此处是check的开始。这里具体在哪个checkCommand打断点取决于你的环境。

然后跟进去下面的checkCommand，然后跟进doCheckWithoutRequest

[![](https://p1.ssl.qhimg.com/t010620905c9ec2154d.png)](https://p1.ssl.qhimg.com/t010620905c9ec2154d.png)

然后再跟进doRealCheckWithoutRequest

[![](https://p2.ssl.qhimg.com/t01228cdc1c4908184c.png)](https://p2.ssl.qhimg.com/t01228cdc1c4908184c.png)

然后再跟进CheckerManager.check

[![](https://p3.ssl.qhimg.com/t01912847d699f567c3.png)](https://p3.ssl.qhimg.com/t01912847d699f567c3.png)

依次跟进checkParam-&gt;JS.Check。发现在此处返回为null。

[![](https://p1.ssl.qhimg.com/t015b50f2aa1ec9675f.png)](https://p1.ssl.qhimg.com/t015b50f2aa1ec9675f.png)

而<br>
results = V8.Check(type.getName(), params.getByteArray(), params.size(),new Context(checkParameter.getRequest()), type == Type.REQUEST, (int) Config.getConfig().getPluginTimeout());

此处是jni调用c++,然后解析js文件。所以我们直接看js文件。

[![](https://p0.ssl.qhimg.com/t01f9bf549fb763f913.png)](https://p0.ssl.qhimg.com/t01f9bf549fb763f913.png)

发rasp会判断请求url是否为空来判断是否校验。我们将 return clean；注释掉，发现能够拦截，我们用线程的方式启动请求context中没有url。所以能绕过。<br>
此处建议：如果没有url，也要校验命令执行的内容，匹配危险命令则拦截或者记录。而不是应该判断url是否为空来判断。

[![](https://p4.ssl.qhimg.com/t015578b29e12ab4991.png)](https://p4.ssl.qhimg.com/t015578b29e12ab4991.png)



## 绕过方式二

绕过方式二比较暴力简单。

我们访问[http://127.0.0.1:8877/hello4](http://127.0.0.1:8877/hello4) 可以看到正常返回。

[![](https://p4.ssl.qhimg.com/t01fcaad9a7c52390a1.png)](https://p4.ssl.qhimg.com/t01fcaad9a7c52390a1.png)

代码如下

[![](https://p1.ssl.qhimg.com/t0168b5d5dac419be30.png)](https://p1.ssl.qhimg.com/t0168b5d5dac419be30.png)

我们直接使用反射的方式。修改rasp的HookHandler类的变量enableHook设置为false。而这个变量是全局的开关。所以我们只需重新关闭这个开关就可以使rasp失效。实现全局绕过。

[![](https://p5.ssl.qhimg.com/t010d049f4e198825d2.png)](https://p5.ssl.qhimg.com/t010d049f4e198825d2.png)

我们再访问[http://127.0.0.1:8877/hello3](http://127.0.0.1:8877/hello3), 确实没有被拦截。

建议：反射Hook的时候开发者没有考虑到应用程序也能访问rasp的方法和变量。应该把com.baidu.* 开头的也要加入反射hook的黑名单中，只开放一些自己自己需要用的反射方法。



## 后记

openrasp是一款非常优秀的软件，并且对此的研究越来越火。也是未来的发展方向。但是本身的额外的引入的代码又对程序产生了影响。
