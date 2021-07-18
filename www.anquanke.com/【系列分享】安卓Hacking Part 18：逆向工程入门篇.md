
# 【系列分享】安卓Hacking Part 18：逆向工程入门篇


                                阅读量   
                                **100263**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/android-hacking-and-security-part-18-introduction-to-reverse-engineering/](http://resources.infosecinstitute.com/android-hacking-and-security-part-18-introduction-to-reverse-engineering/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85774/t01f59f76986292f90a.jpg)](./img/85774/t01f59f76986292f90a.jpg)**

****

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

在计算领域中，逆向工程是指理解某些系统的运行机制并重用这些信息来做某些事情的过程。这种方式同样适用于Android应用程序。许多情况下，我们都需要对Android应用进行逆向工程。

阅读他人的代码

查找代码中的漏洞

搜索硬编码在代码中的敏感数据

恶意软件分析

修改现有应用程序的功能

<br>

**反编译与反汇编**

反编译是将软件的二进制代码转换为文本格式的、编写软件源代码所用的高级语言代码的过程，因为高级语言具有更高的可读性。

不过，反汇编器却不会将二进制转换为高级语言文本：它只是字节到文本的一对一转换，并提供指令助记符，虽然这样也有助于理解代码，但是与直接阅读高级语言源码相比难度要更大一些。

<br>

**从Java生成DEX文件**

为了介绍Android应用程序的逆向过程，首先需要了解如何构建应用程序。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e8a1b457e5f9a0de.png)

如上图所示，

1.	开发人员用Java编程语言编写源代码，这些文件的扩展名“.java”。

2.	这些java文件被提交给“javac”编译器，由它生成“.class”文件。

3.	这些类文件被提交给“dx”工具，以生成“.dex”文件。

4.	然后，“.dex”文件以及其他资源被打包为“.apk”文件，最后放入Dalvik虚拟机中运行。

要想查看所生成的dex文件的结构的话，我们可以使用010Editor。

在我们继续学习之前，请下载以下工具： 

010Editor

dex template

您可以从下面的链接下载010编辑器： 

[http://www.sweetscape.com/010editor/](http://www.sweetscape.com/010editor/) 

你可以从下面的链接来下载“dex 模板”：

<br>

**下载链接**

1.解压APK文件。在*nix系统中我们可以使用unzip命令进行解压。

2.使用010 Editor打开classes.dex。

3.加载下载的dex模板。

下图是010editor显示一个dex文件。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0122e179fd13aeadcf.png)

关于dex文件格式及其工作原理的详细信息，请参阅以下链接。

[https://source.Android.com/devices/tech/dalvik/dex-format.html](https://source.Android.com/devices/tech/dalvik/dex-format.html) 

逆向Android应用程序：

现在让我们讨论如何针对Android应用程序进行逆向工程。

**1.反汇编Android应用程序**

可以使用名为APKTOOL的工具获取smali版本的代码。这一点我们在本系列的前面的文章中已经介绍过了。

以下是对Android应用程序进行逆向工程，并使用APKTOOL获取smali代码的具体步骤。

第1步.从以下链接下载APKTOOL

[http://ibotpeaches.github.io/Apktool/](http://ibotpeaches.github.io/Apktool/) 

第2步.运行以下命令获取smali版本的代码。

```
apktool d [app] .apk
```

第3步.为了重新编译应用程序，我们只需要修改选项"b"，让它指向存放修改的代码的文件夹的路径即可。

```
apktool.bat b [path to the target folder]
```

**2.解压Android应用程序**

在本节中，我们将讨论反编译Android应用程序的两种方法。

使用dex2jar和jad来反编译Android应用程序：

首先，让我们看看如何使用dex2jar和jad来反编译Android应用程序。

步骤1：解压apk文件

如下图所示，目标APK文件位于我当前的文件夹中。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016c816dc79241270c.png)

让我们将apk文件的扩展名改为ZIP，如下所示。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015d2868988f067e2d.png)

现在，我们可以使用unzip命令进行解压了，具体如下所示。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e894e2b68c72188e.png)

步骤2：dex2jar上场

现在，导航到dex2jar所在的文件夹，并运行以下命令。这将生成一个新的jar文件，具体如下所示。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01326db9e1a8e5a7f1.png)

步骤3：使用unzip命令从新生成的jar文件中提取“.class”文件。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01077f82d2b25e84d4.png)

上面的步骤将会创建一些文件夹，这些文件夹的名称与APK工具包名称类似。

这里为com.isi.securelogin

导航到.class文件所在的文件夹，如下所示。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01db4d46e5ade43826.png)

现在，我们需要反编译它们，以获得.java文件。

步骤4：使用JAD反编译器将.class文件解压为Java：

Jad是一个流行的java反编译器。

您可以通过下面的链接下载jad。

[http://www.varaneckas.com/jad](http://www.varaneckas.com/jad) 

现在，将我们提取的所有类文件作为输入提供给jad，具体如下所示。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015f164e1f405ddc4e.png)

它将在同一个文件夹下面生成.java文件，具体如下所示。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01baa31e6e22793527.png)

<br>

**使用dex2jar和JD-GUI解压Android应用程序**

本节介绍如何使用dex2jar和JD-GUI反编译应用程序。这种方法和以前的方法之间的唯一区别，就是使用JD-GUI代替了JAD。

您可以从下面的链接下载JD-GUI。

[http://jd.benow.ca](http://jd.benow.ca) 

**步骤1：解压apk文件**

让我们将apk文件的扩展名更改为ZIP，如下所示。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0154385e33d881be88.png)

现在，我们可以使用unzip命令了，具体如下所示。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c5ca1ba6bcc174e8.png)

**步骤2：使用dex2jar**

就像前面那样，导航到dex2jar所在的文件夹，并运行以下命令。这将生成一个新的jar文件，如下所示。

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015b04b203b0bc306a.png)

**步骤3：现在，使用JD-GUI打开这个新生成的jar文件，如下所示。**

[![](./img/85774/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0173345286112a105b.png)

这样就能得到反编译的Java代码了。

<br>

**传送门**

[**安卓 Hacking Part 1：应用组件攻防（连载）**](http://bobao.360.cn/learning/detail/122.html)

[**安卓 Hacking Part 2：Content Provider攻防（连载）**](http://bobao.360.cn/learning/detail/127.html)

[**安卓 Hacking Part 3：Broadcast Receivers攻防（连载）**](http://bobao.360.cn/learning/detail/126.html)

[**安卓 Hacking Part 4：非预期的信息泄露（边信道信息泄露）**](http://bobao.360.cn/learning/detail/133.html)

[**安卓 Hacking Part 5：使用JDB调试Java应用**](http://bobao.360.cn/learning/detail/138.html)

[**安卓 Hacking Part 6：调试Android应用**](http://bobao.360.cn/learning/detail/140.html)

[**安卓 Hacking Part 7：攻击WebView**](http://bobao.360.cn/learning/detail/142.html)

[**安卓 Hacking Part 8：Root的检测和绕过**](http://bobao.360.cn/learning/detail/144.html)

[**安卓 Hacking Part 9：不安全的本地存储：Shared Preferences**](http://bobao.360.cn/learning/detail/150.html)

[**安卓 Hacking Part 10：不安全的本地存储**](http://bobao.360.cn/learning/detail/152.html)

[**安卓 Hacking Part 11：使用Introspy进行黑盒测试**](http://bobao.360.cn/learning/detail/154.html)

[**安卓 Hacking Part 12：使用第三方库加固Shared Preferences**](http://bobao.360.cn/learning/detail/156.html)

[**安卓 Hacking Part 13：使用Drozer进行安全测试**](http://bobao.360.cn/learning/detail/158.html)

[**安卓 Hacking Part 14：在没有root的设备上检测并导出app特定的数据**](http://bobao.360.cn/learning/detail/161.html)

[**安卓 Hacking Part 15：使用备份技术黑掉安卓应用**](http://bobao.360.cn/learning/detail/169.html)

[**安卓 Hacking Part 16：脆弱的加密**](http://bobao.360.cn/learning/detail/174.html)

[**安卓 Hacking Part 17：破解Android应用**](http://bobao.360.cn/learning/detail/179.html)
