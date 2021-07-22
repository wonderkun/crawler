> 原文链接: https://www.anquanke.com//post/id/85681 


# 【技术分享】Java RMI 反序列化漏洞检测工具的编写


                                阅读量   
                                **466656**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">10</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p2.ssl.qhimg.com/t01fdc0cbc0a08fabf3.png)](https://p2.ssl.qhimg.com/t01fdc0cbc0a08fabf3.png)**

****

作者：[小天之天](http://bobao.360.cn/member/contribute?uid=1432256886)

预估稿费：400RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**成因**

反序列化的漏洞已经有一段时间，针对weblogic，jboss的测试代码也已经非常成熟，但是发现针对RMI服务的测试停留在ysoserial阶段，只能通过执行命令来监听反弹linux shell，近期看了某位大牛写的关于RMI利用的代码，需要通过远程加载jar包来反弹shell，可是如果那台存在漏洞的主机不能出外网就不能反弹shell，通过私聊得知，大牛太忙没时间写。



**介绍**

Java RMI服务是远程方法调用（Remote Method Invocation）。它是一种机制，能够让在某个java虚拟机上的对象调用另一个Java虚拟机的对象的方法。

RMI传输过程必然会使用序列化和反序列化，如果RMI服务端端口对外开发，并且服务端使用了像Apache Commons Collections这类库，那么会导致远程命令执行。



**代码分析**

第一步:在固定的路径下，加载生成某个class文件；

第二步:加载生成的class文件执行命令，从而避免加载远程的jar文件，解决了主机不出外网照样可以反弹shell的问题。

**执行命令的代码**

[![](https://p3.ssl.qhimg.com/t012779fd363864c167.png)](https://p3.ssl.qhimg.com/t012779fd363864c167.png)

 New URL（ClaassPath）可以加载远程的jar包，此处加载的是本地的class文件，ErrorBaseExec类的do_exec方法来执行命令，从而需要先本地生成class文件。

**生成本地class的代码**

[![](https://p1.ssl.qhimg.com/t018df3b0cd5253526e.png)](https://p1.ssl.qhimg.com/t018df3b0cd5253526e.png)

调用FileOutputStream将byte数组write到本地路径生成ErrorBaseExec.class文件，

**byte数组生成**

[![](https://p0.ssl.qhimg.com/t01a3f51ab495424ce3.png)](https://p0.ssl.qhimg.com/t01a3f51ab495424ce3.png)

先将ErrorBaseExec.java文件，javac下成ErrorBaseExec.class文件，再将class文件解析成byte数组。其中ErrorBaseExec.java为了方便检测漏洞，会throw出包含8888的字符串，只要匹配到8888就说明存在漏洞



**漏洞测试**

漏洞测试代码attackRMI.jar支持cmd传参和不传参，测试结果分别如下:

[![](https://p4.ssl.qhimg.com/t01943221cf881cb4e5.png)](https://p4.ssl.qhimg.com/t01943221cf881cb4e5.png)

[![](https://p1.ssl.qhimg.com/t0134e7853e043a1d71.png)](https://p1.ssl.qhimg.com/t0134e7853e043a1d71.png)

为了国家网络以及企业的安全，对部分地区的部分IP段的1099和1090端口仅仅进行了漏洞测试和验证，并未进行控制或者窃取数据之类不道德不文明的行为，测试概况如下：

[![](https://p0.ssl.qhimg.com/t014b2afb08c723b831.png)](https://p0.ssl.qhimg.com/t014b2afb08c723b831.png)

为了方便安全运维人员进行漏洞验证性测试，请不要用来进行非法活动，测试工具如下:

链接: [https://pan.baidu.com/s/1jHPKh50](https://pan.baidu.com/s/1jHPKh50) 密码: 28ye
