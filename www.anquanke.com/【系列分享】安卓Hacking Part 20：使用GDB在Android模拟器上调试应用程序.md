
# 【系列分享】安卓Hacking Part 20：使用GDB在Android模拟器上调试应用程序


                                阅读量   
                                **121883**
                            
                        |
                        
                                                                                                                                    ![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/android-hacking-and-security-part-20-debugging-apps-on-android-emulator-using-gdb/#article](http://resources.infosecinstitute.com/android-hacking-and-security-part-20-debugging-apps-on-android-emulator-using-gdb/#article)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85819/t01d2a0541813adbb2d.jpg)](./img/85819/t01d2a0541813adbb2d.jpg)**

****

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

在本文中，我们将介绍如何对运行在已经取得root权限的Android设备或模拟器上的进程进行调试。调试进程是一个非常重要的任务，因为通过这种方式，我们就能在应用程序中查找内存损坏等安全漏洞。

<br>

**准备工作**

1.设置一个Android模拟器

2.	安装NDK – 可以从下面的链接进行下载 

[http://developer.android.com/tools/sdk/ndk/index.html](http://developer.android.com/tools/sdk/ndk/index.html) 

然后，我们要做些什么呢？

其实我们要做的事情并不复杂：

1.	在模拟器上设置GDB服务器

2.	从客户端连接到GDB服务器

3.	开始调试

好了，让我们开始吧。

<br>

**使用GDB在Android模拟器上调试APP**

第一步是将gdb服务器推送到模拟器上。我们希望能够从设备中的任何位置访问它，为此，一种方法是将其放在/ system / bin目录下。

我们首先使用“adb”获取设备上的shell，并运行“mount”命令，具体如下所示。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014d8ed59ac06b21fb.png)

从上图可以看出，在这里/ system是以“ro”权限进行安装的。因为我们需要在这里写一些文件，所以我们需要用“rw”重新安装它，具体命令如下所示。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e82d8498b2fbc628.png)

现在我们来看看“mount”命令。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0189194d9a2da6a60f.png)

不知您是否注意到了，现在/system分区是以"rw"权限挂载的。

下面，我们将gdbserver推送到模拟器。

导航到NDK目录并寻找ARM二进制代码所在位置。在我的机器中，它位于“prebuilt / android-arm”目录下面，如下所示。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bf03043a336982a2.png)

使用“adb push”命令将gdbserver推送到模拟器上。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0126064784d1570bff.png)

为了验证是否上传成功，请使用“adb”在设备上获取shell，并键入以下命令。

```
“gdbserver –help”
```

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dbd11cda3ba64a7d.png)

从上图可以看出，gdb服务器一切正常。

我们还可以检查gdbserver的版本，具体命令如下图所示。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018b13de1c7e6f8883.png)

我们可以看到，目标进程的进程ID是1234。

下图显示了如何使用gdbserver附加到这个进程。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014d19f62d53e346bf.png)

注意：我们也可以使用以下命令直接挂接到该程序中。

```
gdbserver:8888 [filename] [arguments]
```

现在，gdbserver正在运行。一旦运行完成，我们需要使用“adb forward”转发端口8888，具体如下所示。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0155f0363d313f26e5.png)

完成上述所有步骤后，我们就可以启动预编译的gdb客户端了。

我们可以使用下图中的命令来启动预编译的gdb客户端，如下所示。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01549d236db64d9bac.png)

从上图可以看出，我们会得到一个gdb控制台。现在，我们需要连接到运行在模拟器上的gdbserver实例上，具体方法如下所示。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01033ba22ce35e4a55.png)

好极了！ 我们现在终于可以与目标进程进行交互了。让我们列出寄存器清单。

[![](./img/85819/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016103d33a9f9f6f8c.png)

至于你可以用本文介绍的配置来做什么，那就要看你的想象力了。在后面的文章中，我将为读者演示如何使用相同的配置，通过GDB在NDK应用程序中探测内存损坏漏洞。

<br>

传送门

[](http://bobao.360.cn/learning/detail/122.html)

[安卓 Hacking Part 1：应用组件攻防（连载）](http://bobao.360.cn/learning/detail/122.html)

[安卓 Hacking Part 2：Content Provider攻防（连载）](http://bobao.360.cn/learning/detail/127.html)

[安卓 Hacking Part 3：Broadcast Receivers攻防（连载）](http://bobao.360.cn/learning/detail/126.html)

[安卓 Hacking Part 4：非预期的信息泄露（边信道信息泄露）](http://bobao.360.cn/learning/detail/133.html)

[安卓 Hacking Part 5：使用JDB调试Java应用](http://bobao.360.cn/learning/detail/138.html)

[安卓 Hacking Part 6：调试Android应用](http://bobao.360.cn/learning/detail/140.html)

[安卓 Hacking Part 7：攻击WebView](http://bobao.360.cn/learning/detail/142.html)

[安卓 Hacking Part 8：Root的检测和绕过](http://bobao.360.cn/learning/detail/144.html)

[安卓 Hacking Part 9：不安全的本地存储：Shared Preferences](http://bobao.360.cn/learning/detail/150.html)

[安卓 Hacking Part 10：不安全的本地存储](http://bobao.360.cn/learning/detail/152.html)

[安卓 Hacking Part 11：使用Introspy进行黑盒测试](http://bobao.360.cn/learning/detail/154.html)

[安卓 Hacking Part 12：使用第三方库加固Shared Preferences](http://bobao.360.cn/learning/detail/156.html)

[安卓 Hacking Part 13：使用Drozer进行安全测试](http://bobao.360.cn/learning/detail/158.html)

[安卓 Hacking Part 14：在没有root的设备上检测并导出app特定的数据](http://bobao.360.cn/learning/detail/161.html)

[安卓 Hacking Part 15：使用备份技术黑掉安卓应用](http://bobao.360.cn/learning/detail/169.html)

[安卓 Hacking Part 16：脆弱的加密](http://bobao.360.cn/learning/detail/174.html)

[安卓 Hacking Part 17：破解Android应用](http://bobao.360.cn/learning/detail/179.html)

[安卓 Hacking Part 18：逆向工程入门篇](http://bobao.360.cn/learning/detail/3648.html)

[**安卓 Hacking Part 19：NoSQL数据库不安全的数据存储**](http://bobao.360.cn/learning/detail/3653.html)


