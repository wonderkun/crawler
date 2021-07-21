> 原文链接: https://www.anquanke.com//post/id/84980 


# 【技术分享】域渗透之使用CrackMapExec拿到我们想要的东西（一）


                                阅读量   
                                **170097**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：byt3bl33d3r
                                <br>原文地址：[https://byt3bl33d3r.github.io/getting-the-goods-with-crackmapexec-part-1.html](https://byt3bl33d3r.github.io/getting-the-goods-with-crackmapexec-part-1.html)

译文仅供参考，具体内容表达以及含义原文为准

****

**[![](https://p1.ssl.qhimg.com/t0111da8ca85a2772d3.jpg)](https://p1.ssl.qhimg.com/t0111da8ca85a2772d3.jpg)**

**翻译：**[**hac425**](http://bobao.360.cn/member/contribute?uid=2553709124)

**稿费：120RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**传送门**

[**【技术分享】域渗透之使用CrackMapExec拿到我们想要的东西（二）******](http://bobao.360.cn/learning/detail/3228.html)

<br>

**前言**



这是一系列的介绍CrackMapExec的很多功能的文章。下面是对CrackMapExec这个工具的一个概况性的介绍。

它是一个后渗透工具,像Veil-Pillage, smbexec一样

它是一种在域渗透过程中使各种渗透测试框架联合起来的 "胶水 "

可以完全并行的在同一时间连接,攻击多台主机.

它有一个内部数据库可以用来存储获得的凭据,同时来追踪具有管理员权限的用户.

它的功能是基于多种现有的工具

它是"安全": 该工具做的所有事情不是通过在内存中运行,就是使用各种 WinApi或者是windows的一些内建工具.

第一部分会介绍一些基础知识包括:使用凭据, dump凭据,以及使用payload模块来执行命令.

<br>

**探索目标网络环境**

探索目标网络环境显然是非常重要的,进入内网,你想干的第一件是应该是搞清楚目标内网中到底有些什么.

[![](https://p3.ssl.qhimg.com/t012b748860594b989f.gif)](https://p3.ssl.qhimg.com/t012b748860594b989f.gif)

在上面我们给CWE(CrackMapExec)提供了一个 192.168.0.0/24的参数,这样他就会去扫描整个C段的主机信息.可以看到最后他发现了5台位于LAB域中的主机.默认情况下他会使用100线程,我们可以使用 -t 参数来指定线程数.

到目前为止,我们已经知道了我们的目标网络中到底有些什么东西.一旦我们拿到了一些用户凭据(这里假定已经拿到了一个普通域用户的账号密码,在实际的域渗透过程中,这也是很简单的.),我们就会想知道我们能访问什么.首先我们来侦查下:

[![](https://p1.ssl.qhimg.com/t01fa2ce8131559a56a.gif)](https://p1.ssl.qhimg.com/t01fa2ce8131559a56a.gif)

这里我们使用拿到的凭据,登录到目标机器并且使用了 –pass-pol 参数,这会把域密码策略给dump下来.从输出中我们可以看到没有账号锁定阈值或持续时间.所以我们不需要担心帐户锁定,下面我们来试试在所有c段使用这个凭据去认证下,看看能拿到什么样的成果.

[![](https://p0.ssl.qhimg.com/t01d8f763367b0b8276.gif)](https://p0.ssl.qhimg.com/t01d8f763367b0b8276.gif)

接下来让我们来列出所有的共享.

[![](https://p0.ssl.qhimg.com/t01eb12e3b489af3eca.gif)](https://p0.ssl.qhimg.com/t01eb12e3b489af3eca.gif)

程序的输出给出了所以共享的名称以及你使用的凭据对他们的权限.同时注意到192.168.0.12的右边显示了黄色的＂Pwn3d!＂这意味着我们在这台机器上拥有管理员权限．

<br>

**Dump SAM哈希并且执行命令**

目前为止我们已经有了192.168.0.12这台机器上的管理员权限，首先我们看看谁登录到了这台机器上：

[![](https://p1.ssl.qhimg.com/t0162bbf3ebc6e56713.gif)](https://p1.ssl.qhimg.com/t0162bbf3ebc6e56713.gif)

看起来好像域管理员登录到了这台机器上．我们来检验下

[![](https://p5.ssl.qhimg.com/t01e1543062b2093d2c.gif)](https://p5.ssl.qhimg.com/t01e1543062b2093d2c.gif)

如果使用　-x　来执行命令的话，程序会默认使用WMI来执行命令（这里我们使用了一个–exec-method参数来指定使用smbexec方式来执行命令，这将允许我们以系统权限来执行命令．），我使用了一个net user Administrator /domain命令来验证该用户是否在 域管理员组中．在继续干其他事情之前我们先把本地机器的hash给dump下来．

[![](https://p3.ssl.qhimg.com/t0122f2142aa5c74026.gif)](https://p3.ssl.qhimg.com/t0122f2142aa5c74026.gif)

现在我们已经拿到了很多hash，我们可以在之后使用 -H参数来进行 hash传递攻击（这些拿到的hash会被存储到CWE的数据库以及logs目录下),但是如果能拿到明文密码那就更好了．但是问题是现在这台机器是一台win10的机器，因而我们不能从内存中dump明文密码，但是真的不能吗？其实我们可以通过创建UseLogonCredential注册表键值来重新启用WDigest，接着我们就可以从 LSA内存中dump明文密码了．

[![](https://p1.ssl.qhimg.com/t012cc06c3d4c2be9e4.gif)](https://p1.ssl.qhimg.com/t012cc06c3d4c2be9e4.gif)

现在我们只需要等着用户注销然后重新登录，就可以dump用户的明文密码了．当然我们可以强制让某个用户下线，比如下面让yomama用户下线了．

[![](https://p0.ssl.qhimg.com/t01399e973cee693ef5.gif)](https://p0.ssl.qhimg.com/t01399e973cee693ef5.gif)

<br>

**Payload 模块**

用户可以自己来创建模块，程序自带的模块位于 modules目录下．因为此时我们需要明文密码所以我们使用mimikatz模块，使用 -m 参数指定模块路径.

[![](https://p3.ssl.qhimg.com/t01fd999f227fc39f12.gif)](https://p3.ssl.qhimg.com/t01fd999f227fc39f12.gif)

好,现在我们已经拿到了域管理员的账号密码了.

其中有些模块需要一些参数,我们可以使用-o来指定

[![](https://p5.ssl.qhimg.com/t01e418f96717a7f710.png)](https://p5.ssl.qhimg.com/t01e418f96717a7f710.png)

如果要查看模块的说明可以使用 –module-info

[![](https://p5.ssl.qhimg.com/t01fb76e0a0813d63eb.png)](https://p5.ssl.qhimg.com/t01fb76e0a0813d63eb.png)

显然所有的这些功能都可以同时对多台主机使用.

<br>

**总结**

本文介绍了CME的基本用法,使用CME可以简化我们的工作,尽可能的少做些重复性的工作.

**<br>**

**传送门**

[**【技术分享】域渗透之使用CrackMapExec拿到我们想要的东西（二）******](http://bobao.360.cn/learning/detail/3228.html)




