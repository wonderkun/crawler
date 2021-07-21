> 原文链接: https://www.anquanke.com//post/id/82438 


# 涅槃团队：Xcode幽灵病毒存在恶意下发木马行为


                                阅读量   
                                **75027**
                            
                        |
                        
                                                                                    



**[![](https://p2.ssl.qhimg.com/t013f44452fe4cae463.jpg)](https://p2.ssl.qhimg.com/t013f44452fe4cae463.jpg)**

**本文是 360 Nirvan Team 团队针对 XcodeGhost 的第二篇分析文章。**

我们还原了恶意iOS应用与C2服务器的通信协议，从而可以实际测试受感染的iOS应用有哪些恶意行为。

最后，我们分析了攻击的发起点：Xcode，分析了其存在的弱点，以及利用过程，并验证了该攻击方法。

**一、恶意行为与C2服务器**

**1、通信密钥分析**

恶意程序将其与服务器通信的数据做了加密，如下图所示：

[![](https://p4.ssl.qhimg.com/t0175c8dac8b444b329.jpg)](http://image.3001.net/images/20150919/14426696147299.png!small)

密钥的计算方法：

[![](https://p4.ssl.qhimg.com/t01e5b36ac4bdd9a618.jpg)](http://image.3001.net/images/20150919/14426696469639.png!small)

通过分析，密钥为：stringWi，生成密钥的方式比较有迷惑性。



**2、恶意行为分析**

**恶意行为一：做应用推广**

方法是：首先检测用户手机上是否安装了目标应用，如果目标应用没有安装，则安装相应应用，其中目标应用由C2服务器控制。

我们逆向了恶意代码与C2服务器的通信协议，搭建了一个测试的C2服务器。然后通过C2服务器可以控制客户端安装第三方应用（演示应用为测试应用，不代表恶意软件推广该应用），见视频：

这是第一个针对 XcodeGhost 能力的视频演示

**恶意行为二：伪造内购页面**

相关代码如下：

[![](https://p5.ssl.qhimg.com/t012ba3bb27518b1680.jpg)](http://image.3001.net/images/20150919/14426697401379.png!small)

**恶意行为三：通过远程控制，在用户手机上提示‍**

[![](https://p3.ssl.qhimg.com/t01c62a9c17b97da306.jpg)](http://image.3001.net/images/20150919/14426697613458.png!small)

**二、Xcode 的弱点及利用**

**1、Xcode 的利用过程描述**

Xcode 中存在一个配置文件，该配置文件可以用来控制编译器的链接行为，在受感染的Xcode中，该文件被修改，从而在链接阶段使程序链接含有恶意代码的对象文件，实现向正常iOS应用中注入恶意代码的目的。

被修改的文件内容如下：

[![](https://p2.ssl.qhimg.com/t01ed13c0921f6d06e2.jpg)](http://image.3001.net/images/20150919/14426699431537.png!small)

从上图可以看到，程序会链接恶意对象文件 CoreService。

从链接过程的Log中可以看到其实如何影响链接过程的：

[![](https://p3.ssl.qhimg.com/t018e8c7dedea157e25.jpg)](http://image.3001.net/images/20150919/14426699915994.png!small)

**注：实际上可以让CoreService从文件系统中消失，且在链接Log中没有任何额外信息。**

通过在配置文件中添加的链接选项，在工程的编译设置中无法看到，这就增加隐蔽性：

[![](https://p1.ssl.qhimg.com/t0114c707ef53d441c9.jpg)](http://image.3001.net/images/20150919/14426700188547.png!small)



**2、对恶意代码 CoreService 的分析**

首先 CoreService 的文件类型为：Object，即对象文件。

查看 CoreService 中的符号，可以看到：

[![](https://p1.ssl.qhimg.com/t01e7dd603592dd988c.jpg)](http://image.3001.net/images/20150919/14426700682031.png!small)

导入的符号有：

[![](https://p0.ssl.qhimg.com/t01d87afcf47642e214.jpg)](http://image.3001.net/images/20150919/14426700943791.png!small)



**3、验证概念**



首先编写一个ObjC的类，测试如下图：

[![](https://p0.ssl.qhimg.com/t016797971027d7f2c7.jpg)](http://image.3001.net/images/20150919/1442670122913.png!small)

[![](https://p1.ssl.qhimg.com/t01a0374cf22d3d18a0.jpg)](http://image.3001.net/images/20150919/14426701234764.png!small)

制作出对象文件ProteasInjector.o，然后用这个文件替换掉CoreService文件，编译程序，然后反汇编，结果如下：

[![](https://p5.ssl.qhimg.com/t012d9b44987e2063b1.jpg)](http://image.3001.net/images/20150919/14426701628862.png!small)

可以看到代码被注入到应用中。
