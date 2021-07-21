> 原文链接: https://www.anquanke.com//post/id/85286 


# 【木马分析】DeriaLock勒索木马最新变种分析


                                阅读量   
                                **73885**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p4.ssl.qhimg.com/t0114a6fdaef89b0552.png)](https://p4.ssl.qhimg.com/t0114a6fdaef89b0552.png)**

****

**作者：**[**胖胖秦******](http://bobao.360.cn/member/contribute?uid=353915284)

**预估稿费：300RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**0x0 简述**

最近出现了一种名为DeriaLock的新型勒索者木马，在最初版本中，DeriaLock只是一个屏幕锁,在其最新变种中, DeriaLock在屏幕锁的基础上加入了文件加密的功能,被加密的文件后缀为.deria。

从显示的勒索界面上,我们发现DeriaLock要求受害者在有限的24小时支付30美元的赎金,否则被加密的文件会被删除,如果你强行退出DeriaLock,被加密的文件也会被删除。

DeriaLock由.NET4.5编写,通过时间戳,可以知道,最新变种的更新时间为2016年12月26号。

[![](https://p1.ssl.qhimg.com/t01d3b50f7d4584f7c5.png)](https://p1.ssl.qhimg.com/t01d3b50f7d4584f7c5.png)

<br>

**0x1 对抗分析**



出于强度的考虑, DeriaLock对关键的函数与变量进行了混淆。

[![](https://p0.ssl.qhimg.com/t01df21521b2728af08.png)](https://p0.ssl.qhimg.com/t01df21521b2728af08.png)

对引用到的字符串进行了加密

[![](https://p0.ssl.qhimg.com/t0129cf816baef85fdb.png)](https://p0.ssl.qhimg.com/t0129cf816baef85fdb.png)

经过分析与反混淆后,DeriaLock由以下5个类组成: 

**Decrypt:**解密文件

**Encrypt:**加密文件

**KillProc:**结束进程

**Main:**程序入口点

**ShowFile:**显示被加密文件

<br>

**0x2 锁屏分析**



在Main的FormLoad函数中, DeriaLock会创建多个计时器,调用KillProcess类的方法对系统进程进行枚举并结束指定列表的进程。

[![](https://p1.ssl.qhimg.com/t01eb75621cc6b7ec72.png)](https://p1.ssl.qhimg.com/t01eb75621cc6b7ec72.png)

定时器方法:

[![](https://p4.ssl.qhimg.com/t017fb7603fd40341bb.png)](https://p4.ssl.qhimg.com/t017fb7603fd40341bb.png)

定时器的时间间隔是1ms,所以在配置差的电脑上会略显卡顿。

[![](https://p3.ssl.qhimg.com/t014916a90cc36b7b41.png)](https://p3.ssl.qhimg.com/t014916a90cc36b7b41.png)

由上可知,DeriaLock在结束explorer.exe进行锁屏之后还对许多系统配置进程与进程管理软件进行了监控，阻止受害者恢复锁屏。

<br>

**0x3 加密分析**



在加密之前, DeriaLock会计算本机特征码,以确保测试时自己的电脑不被加密。

[![](https://p1.ssl.qhimg.com/t014d3078909ce08930.png)](https://p1.ssl.qhimg.com/t014d3078909ce08930.png)

不同于其他勒索木马只加密特定后缀的文件,DeriaLock会对指定目录下的所有文件进行加密。



```
C:UsersUserNameDocuments
C:UsersUserNameMusic
C:UsersUserNamePictures
C:UsersUserNameDownloads
C:UsersUserNameDesktop
D:
```

DeriaLock使用标准的AES256算法对文件进行加密

[![](https://p5.ssl.qhimg.com/t0194e463bf4c860b5d.png)](https://p5.ssl.qhimg.com/t0194e463bf4c860b5d.png)

KEY和IV向量都是由一个固定的字符串经过SHA512计算生成。

[![](https://p0.ssl.qhimg.com/t015ac3637613ad7d4d.png)](https://p0.ssl.qhimg.com/t015ac3637613ad7d4d.png)

<br>

**0x4 解密分析**



有意思的一点是, DeriaLock在服务器上拥有一个全局的解锁指令,在Main初始时会创建一个定时器,而这个定时器的作用就是轮询这个指令,如果指令为1，所有被锁屏的电脑都会解锁

[![](https://p5.ssl.qhimg.com/t01a309875cc8b216a7.png)](https://p5.ssl.qhimg.com/t01a309875cc8b216a7.png)

值得注意的是,解锁指令只是删除自启动,并创建explorer.exe,同时退出自身,被加密过的文件并不会得到解密。

[![](https://p3.ssl.qhimg.com/t01bea653c942d25753.png)](https://p3.ssl.qhimg.com/t01bea653c942d25753.png)

当你支付赎金之后, DeriaLock会在服务器上添加一个ID.txt文件,其中ID是你的特征码,里面保存着密码,密码与你输入的密码进行比对,正确的话就调用DeCrypt类对文件进行解密。

[![](https://p2.ssl.qhimg.com/t0114ee503deb03acb3.png)](https://p2.ssl.qhimg.com/t0114ee503deb03acb3.png)

以上是正常的解密流程,如果你不幸被DeriaLock加密了,也不用担心, DeriaLock是可解的。

通过之前的分析我们可以得知DeriaLock使用AES256对文件进行加密,并且KEY和IV都是唯一的,现在让我们再看看KEY的生成过程.

[![](https://p2.ssl.qhimg.com/t019c39856c77b0bd3b.png)](https://p2.ssl.qhimg.com/t019c39856c77b0bd3b.png)

IV的生成过程和KEY的是一样的，唯一不同的长度,所以我们完全可以自己写一个解密程序对程序进行解密。

在加密文件时, DeriaLock会连接远程服务器更新其最新版本的,并写入自启。

[![](https://p1.ssl.qhimg.com/t01039d3bea3f0ea34d.png)](https://p1.ssl.qhimg.com/t01039d3bea3f0ea34d.png)

所以我们可以 强制关闭计算机,同时挂上WINPE盘,在启动盘里运行我们的解密工具,对文件进行解密。

<br>

**0x5结论**



由于DeriaLock刚出现不久,加密的强度和广度还不够,对于专业的安全人员来说,可以实现自解密,但对于广大的普通用户来说,保持良好的上网习惯和安装杀毒软件还是有一定必要性的。
