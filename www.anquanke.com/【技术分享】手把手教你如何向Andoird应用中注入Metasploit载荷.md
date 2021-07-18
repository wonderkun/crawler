
# 【技术分享】手把手教你如何向Andoird应用中注入Metasploit载荷


                                阅读量   
                                **132942**
                            
                        |
                        
                                                                                                                                    ![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentestlab.blog
                                <br>原文地址：[https://pentestlab.blog/2017/03/13/injecting-metasploit-payloads-into-android-applications/](https://pentestlab.blog/2017/03/13/injecting-metasploit-payloads-into-android-applications/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85734/t014b88d14cc4352692.jpg)](./img/85734/t014b88d14cc4352692.jpg)**

****

翻译：[pwn_361](http://bobao.360.cn/member/contribute?uid=2798962642)

稿费：100RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

为了渗透用户的实际设备，将合法的安卓应用程序作为一个木马来使用是有可能的。正好，现在Metasploit框架已经有了这样的能力。可以将Metasploit载荷注入到Android应用(APK)中，该过程可以手动完成，也可以自动完成。这篇文章将主要探讨自动注入过程。当然，如果时间宽裕，使用手动方法也是可以考虑的。

<br>

**生成载荷**

可以使用Metasploit生成安卓渗透载荷，并将文件存储为APK格式，如下图所示：

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013290eb3625f28923.png)

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f9471821c52c6c57.png)

<br>

**将载荷注入到APK中**

将刚才生成的载荷注入到一个安卓应用中之前，需要先有一个目标安卓应用程序(APK文件)。如果该应用已经安装在手机中，那么这篇文章“[Retrieving APK Files](https://pentestlab.blog/2017/01/30/retrieving-apk-files/)”可以当作从手机中提取APK文件的一个指南，当然，也可以从谷歌应用商店中直接下载应用。

有很多公开的脚本可以将Metasploit载荷注入到一个安卓应用中。然而，在某些特定的场景中，为了创建、并自动注入Metasploit载荷，也可以使用msfvenom工具，如下图示例所示：

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016c54bf15143ca1e1.png)

Msfvenom会对该应用程序进行反编译，然后会找到可以注入载荷的钩子点。进一步，它会利用可用于后渗透活动的附加权限使该应用程序的Android清单文件染毒。下图为输出结果：

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aaba0f407bba41ae.png)

当然，使用Msfvenom执行载荷注入不是本文的主要目的，在本文中，我们使用[apkinjector](https://github.com/jbreed/apkinjector)工具执行载荷注入活动，其它可以用于此目的的脚本还有以下几个：

1.[Metasploit APK Embed Payload](https://github.com/xc0d3rz/metasploit-apk-embed-payload)

2.[APK Payload Injector](https://github.com/SkullTech/apk-payload-injector)

3.[Backdoor APK](https://github.com/dana-at-cp/backdoor-apk)

注意：为了演示目的，在这篇文章中，我们使用了一个真实的安卓应用程序，并起了一个显著的名称“target.apk”。

Apkinjector将会使用apktool工具完全反编译目标安卓应用程序，并将载荷注入到程序中，然后，Apkinjector会重新编译应用程序，并签名。下图是Apkinjector部分解码过程：

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cffb1a3f157ffabd.png)

Apkinjector将会尝试在文件中注入载荷，并再次使用apktool工具编译应用程序，并对应用程序签名。如下图：

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0162a4c897c8186b4b.png)

当然，为了收到载荷成功执行后返回的信息，我们还需要开启一个Metasploit监听：

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019bf49303591db0d9.png)

然后，目标用户在他的手机中安装、并打开了修改过的APK，于是，该载荷会被执行，并会返回一个Meterpreter会话。<br>

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ebf632a2902fb71f.png)

在成功返回Meterpreter会话以后，存在很多可以使用的命令，可用于检查目标设备是否已经root、或下载联系人列表、接收该手机的短信消息、或者使用手机相机拍个照片。所有这些活动依赖该安卓应用程序(被注入了载荷)的权限，它已经在安卓清单文件中定义了。

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01378c5263b6508a37.png)

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012578dec9563affd3.png)

<br>

**载荷免杀**

如果目标设备中安装了反病毒软件，有可能会造成载荷在设备中被阻止，无法运行。不过，在[APKwash](https://github.com/jbreed/apkwash)工具的帮助下，避开杀毒软件是有可能的。该脚本为了避开杀毒软件，会修改所有字符串和文件结构，然后利用apktool工具重建安装包。

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fb141c7bc4589f65.png)

免杀效果可以通过将APK上传到nodistribute.com网站来验证：

[![](./img/85734/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b38d8571165ade52.png)

从上表中可知，只有卡巴斯基一个安全厂商有能力探测到该恶意APK，这增加了该恶意APK成功的可能性。其它工具，如Veil和Shelter也可用于高效的免杀。
