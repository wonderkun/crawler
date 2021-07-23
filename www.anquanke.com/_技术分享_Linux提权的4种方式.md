> 原文链接: https://www.anquanke.com//post/id/85002 


# 【技术分享】Linux提权的4种方式


                                阅读量   
                                **122312**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：hackingarticles
                                <br>原文地址：[http://www.hackingarticles.in/4-ways-get-linux-privilege-escalation/](http://www.hackingarticles.in/4-ways-get-linux-privilege-escalation/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01c594a44f86182c0d.jpg)](https://p5.ssl.qhimg.com/t01c594a44f86182c0d.jpg)



**翻译：**[**唯爱依1314**](http://bobao.360.cn/member/contribute?uid=1009682630)

**稿费：90RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



当你在攻击受害者的电脑时即使你拥有了一个shell，依然可能会有一些拒绝执行指令的限制。为了获得目标主机的完整控制权限，你需要在未授权的地方绕过权限控制。这些权限可以删除文件，浏览私人信息，或者安装并非受害者希望的软件例如计算机病毒。Metasploit 拥有各种使用不同技术的exploits在受害者电脑上尝试获取系统级权限。除此之外，这里还有一些在linux下使用的脚本。当你尝试在目标机器上提升权限时可能会很有用。通常它们的目的是枚举系统信息而不是给出具体的vulnerabilities/exploits。这种类型的脚本将会为你节省很多时间。

在Linux下使用payload并且开启反向连接的multi/handler，一旦你侵入了受害者的电脑马上使用下列脚本提升权限。

<br>

**LinEnum**

可以列举系统设置并且高度总结的linux本地枚举和权限提升检测脚本

**隐私访问：**判断当前用户是否能够用空口令使用sudo命令,root用户的家目录能否访问。

**系统信息：**主机名，网络详情，当前IP等等。

**用户信息：**当前用户，列出所有包含uid/gid的用户信息，列出有root权限的用户，检查密码hash是否保存在/etc/passwd。

**内核和发行版详细信息**

```
Git clone https://github.com/rebootuser/LinEnum.git
```

[![](https://p0.ssl.qhimg.com/t015ae5df38a308f1da.png)](https://p0.ssl.qhimg.com/t015ae5df38a308f1da.png)

一旦你从上面的链接下载了这个脚本，你就可以在终端中简单的通过./LinEnum.sh来运行它。随后它将存储所有获取的数据和系统详细信息。

[![](https://p2.ssl.qhimg.com/t01884fa7e76b1dfe15.png)](https://p2.ssl.qhimg.com/t01884fa7e76b1dfe15.png)

<br>

**Linuxprivchecker**

枚举系统设置和执行一些提升权限的检查。它由python实现，用来对被控制的系统提供建议的exploits。在下面的链接下载

[http://www.securitysift.com/download/linuxprivchecker.py](http://www.securitysift.com/download/linuxprivchecker.py)

下载完后在终端中只需要使用 python linuxprivchecke.py 命令就可以使用，它将会枚举文件和目录的权限和内容。这个脚本和LinEnum工作方式一样而且在关于系统网络和用户方面搜寻的很详细。

[![](https://p3.ssl.qhimg.com/t01506b5dfcd0ebd539.png)](https://p3.ssl.qhimg.com/t01506b5dfcd0ebd539.png)

<br>

**Linux Exploit Suggester**

它基于操作系统的内核版本号。这个程序会执行“uname -r”来得到系统内核版本号。然后返回一个包含了可能exploits的列表。另外它还可以使用“-k”参数手工指定内核版本。

它是一个不同于以上工具的Perl脚本。使用下列命令下载这个脚本。

```
git clone https://github.com/PenturaLabs/Linux_Exploit_Suggester.git
```

[![](https://p3.ssl.qhimg.com/t01a84770e85957b4c4.png)](https://p3.ssl.qhimg.com/t01a84770e85957b4c4.png)

如果你知道内核版本号就可以在终端中直接使用下列命令：

```
./Linux_Exploit_Suggester.pl -k 3.5
```

如果不知道就输入./Linux_Exploit_Suggester.pl uname –r 来获得内核版本号然后使用上面的命令并把版本号替换成你自己的。然后它就会给出建议的exploits列表。

[![](https://p0.ssl.qhimg.com/t01110dc325429a74e4.png)](https://p0.ssl.qhimg.com/t01110dc325429a74e4.png)

<br>

**Unix-Privesc-checker**

在UNIX系统上检测权限提升向量的shell脚本。它可以在UNIX和Linux系统上运行。寻找那些错误的配置可以用来允许未授权用户提升对其他用户或者本地应用的权限。

它被编写为单个shell脚本所以可以很容易上传和执行。它可以被普通用户或者root用户执行。当它发现一个组可写(group-writable)的文件或目录时，它只标记一个问题如果这个组包含了超过一个的非root成员。

使用下列命令下载



```
Git clone https://github.com/pentestmonkey/unix-privesc-check.git
```

把它解压然后执行

```
unix-privesc-check standard
```



[![](https://p3.ssl.qhimg.com/t0130c483cb70c107ec.png)](https://p3.ssl.qhimg.com/t0130c483cb70c107ec.png)

你可以通过我提供的这些图片来更好的学习我是如何使用这些工具的。也可以使用另一个命令达到相同的目的。

```
unix-privesc-check detailed
```

[![](https://p0.ssl.qhimg.com/t017598a2ae44ae4655.png)](https://p0.ssl.qhimg.com/t017598a2ae44ae4655.png)
