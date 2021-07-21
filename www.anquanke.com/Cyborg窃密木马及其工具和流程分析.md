> 原文链接: https://www.anquanke.com//post/id/153702 


# Cyborg窃密木马及其工具和流程分析


                                阅读量   
                                **335579**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t018827a00bed87f14d.jpg)](https://p4.ssl.qhimg.com/t018827a00bed87f14d.jpg)

## 背景介绍

日前收到一封带附件的邮件，该附件没有VT的上传记录，在自己搭的沙箱里测试，显示超时，而且虚拟机动态行为监测有异常。所以决定对样本进行分析。

[![](https://p0.ssl.qhimg.com/t0113bcb865c14a8d7b.png)](https://p0.ssl.qhimg.com/t0113bcb865c14a8d7b.png)

分析完毕后，发现这是一个前期免杀工作比较充分，而Payload实体功能却不甚完善的恶意代码。所以Po出分析过程以及部分与这个样本有关联的信息，仅供各位读者参考。



## 0x01 样本分析

样本进程树：

```
Order Updates.exe
----CDS.exe
--------Crypted.exe
------------PasswordFox.exe
------------Iepv.exe
------------mailpv.exe
```

### 1. Order Updates.exe

```
文件名称:    Order Updates.exe
文件大小:    3,550 KB (3,635,200 字节)
文件时间:    2018-07-15 11:00:19
时 间 戳:    
文件 MD5:    4323C548B9AF8FA95F006954F5DE98A5
```

通过IDA进行分析，发现该样本是一个自解压文件，将文件后缀修改为rar，想法得到印证。

[![](https://p1.ssl.qhimg.com/t01d1e69b6ca83671b6.png)](https://p1.ssl.qhimg.com/t01d1e69b6ca83671b6.png)

[![](https://p2.ssl.qhimg.com/t01cba15ad1e10d4945.png)](https://p2.ssl.qhimg.com/t01cba15ad1e10d4945.png)

动态调试样本时确认样本不带参数创建子进程CDS.exe。

[![](https://p1.ssl.qhimg.com/t01abd57885319598bd.png)](https://p1.ssl.qhimg.com/t01abd57885319598bd.png)

### 2. CDS.exe

```
文件名称:    CDS.exe
文件大小:    396 KB (406,016 字节)
文件时间:    2018-07-16 10:20:29
时 间 戳:    54DA7209-&gt;2015-02-11 05:03:05
文件 MD5:    424BF196DEAEB4DDCAFB78E137FA560A
```

最新VT查杀结果如下：

[![](https://p3.ssl.qhimg.com/t0118d9c598407efccf.png)](https://p3.ssl.qhimg.com/t0118d9c598407efccf.png)

静态分析Main函数，我们可以看到CDS.exe样本是一个标准的MFC应用程序，

[![](https://p5.ssl.qhimg.com/t0151f34ec54723c560.png)](https://p5.ssl.qhimg.com/t0151f34ec54723c560.png)

该样本的主要功能为：将自解压文件释放的c.dat读取并解密，写入crypted.exe。Cds.exe 通过CDocument、CFile和CDocmanager类提供的各种方法对文件进行操作。

[![](https://p1.ssl.qhimg.com/t012b256906391c1f00.png)](https://p1.ssl.qhimg.com/t012b256906391c1f00.png)

[![](https://p3.ssl.qhimg.com/t01ef46633907fc3d2b.png)](https://p3.ssl.qhimg.com/t01ef46633907fc3d2b.png)

[![](https://p5.ssl.qhimg.com/t01b530924694548e7b.png)](https://p5.ssl.qhimg.com/t01b530924694548e7b.png)

动态调试时，确认程序调用了lua，加载了很多加密和散列算法。

[![](https://p0.ssl.qhimg.com/t012177134dc7b23067.png)](https://p0.ssl.qhimg.com/t012177134dc7b23067.png)

加密算法导入完毕后，该样本选择了Blowfish算法对文件进行解密。并首先完成字符串解密，获取加密过的文件名和要释放的文件名：

[![](https://p5.ssl.qhimg.com/t0155284ff5f6143147.png)](https://p5.ssl.qhimg.com/t0155284ff5f6143147.png)

样本提供了两种解密数据的保存方式，取决于传进的字符串指针是否相同。

[![](https://p4.ssl.qhimg.com/t015076b6ebb47836e8.jpg)](https://p4.ssl.qhimg.com/t015076b6ebb47836e8.jpg)

[![](https://p1.ssl.qhimg.com/t01cb435be04e1fc235.png)](https://p1.ssl.qhimg.com/t01cb435be04e1fc235.png)

下图为解密前后的缓冲区的内容。<br>[![](https://p2.ssl.qhimg.com/t011f5cd1748d4e4818.png)](https://p2.ssl.qhimg.com/t011f5cd1748d4e4818.png)

[![](https://p0.ssl.qhimg.com/t019439a4684c8ce596.png)](https://p0.ssl.qhimg.com/t019439a4684c8ce596.png)

解密完毕后会将数据写入crypted.exe，然后通过设置EOF的方式删除最后8个字节，读取fs.setting文件，获得“false”的配置信息后，创建子进程。

### 3. crypted.exe

```
文件名称:    crypted.exe
文件大小:    366 KB (374,784 字节)
文件时间:    2018-07-16 11:35:20
时 间 戳:    5B4AC69F-&gt;2018-07-15 11:59:27
文件 MD5:    3678C20BC19439B0A07378D6B0405ABB
```

从分析结果来看，crypted.exe 是一个由c#编写的典型窃密木马。它主要有以下功能模块：

**通信模块**

代码如下所示：默认SMTP通信，还支持ftp和php post的方法。

[![](https://p3.ssl.qhimg.com/t0154be96b8efee8fac.png)](https://p3.ssl.qhimg.com/t0154be96b8efee8fac.png)

**键盘记录模块**

设置键盘消息钩子，监控击键操作。

[![](https://p3.ssl.qhimg.com/t01ffd6868aaeb0cebf.png)](https://p3.ssl.qhimg.com/t01ffd6868aaeb0cebf.png)

**密码窃取模块**

窃取多种主机软件密码，还包括各种游戏、付费软件的CD-Key

[![](https://p0.ssl.qhimg.com/t01944d7d8922d2a854.png)](https://p0.ssl.qhimg.com/t01944d7d8922d2a854.png)

**屏幕信息窃取模块**

定时截取屏幕，窃取主机信息

[![](https://p1.ssl.qhimg.com/t017be9caa28a147289.png)](https://p1.ssl.qhimg.com/t017be9caa28a147289.png)

另外，程序还会收集主机信息，剪贴板内容等隐私信息。

** 动态调试**

下图为样本的main函数：

[![](https://p3.ssl.qhimg.com/t01dca81c8dd816b4e9.png)](https://p3.ssl.qhimg.com/t01dca81c8dd816b4e9.png)

代码显示，程序运行时首先会弹窗，同时这个样本还有很未完成开发的类，所以我认为该程序尚处于开发和调试过程。

[![](https://p1.ssl.qhimg.com/t01a2bfb6ab4aeac986.png)](https://p1.ssl.qhimg.com/t01a2bfb6ab4aeac986.png)

程序会创建键盘消息钩子，记录击键信息，并创建几个线程，执行Cyber.X， Cyber.Y， Cyber.Z， Cyber.Srceeny和Cyber.C方法。<br>
方法和功能对应如下表：

```
方法               功能
Cyber.X            获取窗口信息并回传
Cyber.Y            获取主机名并回传
Cyber.Z            窃取密码并回传
Cyber.Srceeny      截屏并回传
Cyber.C            获取剪贴板信息并回传
```

回传信息的方法是：调用通信模块（transfer函数），并默认通过邮件协议发送图片内容，调试时的局部变量如下所示：

[![](https://p0.ssl.qhimg.com/t0185db26a7afce46a0.png)](https://p0.ssl.qhimg.com/t0185db26a7afce46a0.png)

需要重点说的是密码窃取模块的内容，从代码定义的类名中，我们可以大致了解样本要窃取信息的对象：

[![](https://p3.ssl.qhimg.com/t012e1f4e152adb5cfe.png)](https://p3.ssl.qhimg.com/t012e1f4e152adb5cfe.png)

在上述窃取对象中，firefox密码，邮件客户端密码和IE浏览器密码是通过调用工具窃取得到的，具体代码如下：

[![](https://p0.ssl.qhimg.com/t01aed50785057e8721.png)](https://p0.ssl.qhimg.com/t01aed50785057e8721.png)

其他两个工具的释放和调用方法同上图相类似。<br>
其他密码的窃取则多是通过解析存放密码的文件或注册表键值得到的：

[![](https://p2.ssl.qhimg.com/t0107e7d2a55d4d78be.png)](https://p2.ssl.qhimg.com/t0107e7d2a55d4d78be.png)

[![](https://p2.ssl.qhimg.com/t015c1ac63ef5e75682.png)](https://p2.ssl.qhimg.com/t015c1ac63ef5e75682.png)

至此样本行为分析完毕。



## 0x02 关联分析和总结

从样本分析结果来看，该样本母体为一个自解压文件，可以将任意需要的组件打包压缩，所以如果发现类似样本在VT上没有查询记录，也不足为奇。CDS.exe等组件则是一个可以灵活配置解压对象和解压算法的工具，只需要调换payload，修改配置文件即可在该层次上完成免杀操作。因为解密操作完成前的payload，此时可以是任意文件格式，无法被杀毒软件识别。虽然此次解密后的payload能在落地运行的第一时间被部分杀软查杀，但是分析结果表明，这是一个功能仍不完善的不完全版本。<br>
通过对CDS.exe以及payload的特征进行关联分析，找到了一些样本：<br>[![](https://p0.ssl.qhimg.com/t011c4b60bcf88e4f80.png)](https://p0.ssl.qhimg.com/t011c4b60bcf88e4f80.png)<br>
通过样本关联分析和其他的情报碰撞，发现这样一个情况：mail.2sqpa.com这个邮件服务器在7月中旬以前被攻击者较为频繁地使用，但是近期有类似行为的恶意代码已经开始使用其他邮件地址和通信方式传递信息，而且丰富功能的同时，也已经开始做混淆和免杀处理。所以我认为这应该是一个活动时间较短的恶意代码家族，根据根据样本注释代码中的“Cyborg”字样，决定沿用作者对该软件的这一命名。
