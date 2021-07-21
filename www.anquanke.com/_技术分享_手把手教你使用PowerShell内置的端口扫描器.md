> 原文链接: https://www.anquanke.com//post/id/86241 


# 【技术分享】手把手教你使用PowerShell内置的端口扫描器


                                阅读量   
                                **218929**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pen-testing.sans.org
                                <br>原文地址：[https://pen-testing.sans.org/blog/2017/03/08/pen-test-poster-white-board-powershell-built-in-port-scanner](https://pen-testing.sans.org/blog/2017/03/08/pen-test-poster-white-board-powershell-built-in-port-scanner)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01da95b2f5ddf008db.png)](https://p3.ssl.qhimg.com/t01da95b2f5ddf008db.png)

****

翻译：[h4d35](http://bobao.360.cn/member/contribute?uid=1630860495)

预估稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**引言**

想做端口扫描，NMAP是理想的选择，但是有时候NMAP并不可用。有的时候仅仅是想看一下某个端口是否开放。在这些情况下，PowerShell确实能够大放异彩。接下来我们聊聊如何使用PowerShell实现基本的端口扫描功能。

[![](https://p3.ssl.qhimg.com/t0182503ddbb6e33a91.png)](https://p3.ssl.qhimg.com/t0182503ddbb6e33a91.png)

<br>

**本文中用到的PowerShell命令**

**PowerShell端口扫描器：针对单个IP的多个端口的扫描**

```
1..1024 | % `{`echo ((new-object Net.Sockets.TcpClient).Connect("10.0.0.100",$_)) "Port $_ is open!"`}` 2&gt;$null
```

**Test-Netconnection 针对某IP段中单个端口的扫描**

```
foreach ($ip in 1..20) `{`Test-NetConnection -Port 80 -InformationLevel "Detailed" 192.168.1.$ip`}`
```

**针对某IP段 &amp; 多个端口的扫描器**

```
1..20 | % `{` $a = $_; 1..1024 | % `{`echo ((new-object Net.Sockets.TcpClient).Connect("10.0.0.$a",$_)) "Port $_ is open!"`}` 2&gt;$null`}`
```

**PowerShell测试出口过滤器**

```
1..1024 | % `{`echo ((new-object Net.Sockets.TcpClient).Connect("allports.exposed",$_)) "Port $_ is open!" `}` 2&gt;$null
```

为了仅用一行PowerShell命令实现一个端口扫描器，我们需要组合3个不同的组件：创建一系列对象、循环遍历每个对象、将每个对象的信息输出到屏幕。在PowerShell中，我们可以利用好其面向对象的特性来帮助我们实现此过程。

<br>

**PowerShell端口扫描器**

```
1..1024 | % `{`echo ((new-object Net.Sockets.TcpClient).Connect("10.0.0.100",$_)) "Port $_ is open!"`}` 2&gt;$null
```

[![](https://p3.ssl.qhimg.com/t01e71df8ac4ec500e5.png)](https://p3.ssl.qhimg.com/t01e71df8ac4ec500e5.png)

**命令分解**

1）1..1024 – 创建值为从1到1024的一系列变量

2）| – 管道运算符，将上述对象传递给循环体

3）% – 在PowerShell中，%是foreach对象的别名，用来开始一个循环。循环体为接下来使用大括号`{``}`括起来的内容

4）echo – 将输出打印至屏幕

5）new-object Net.Sockets.TcpClient – 新建一个.Net TcpClient类的实例，它允许我们和TCP端口之间建立socket连接

6）.Connect("10.0.0.100",$_)) – 调用TcpClient类的Connect函数，参数为10.0.0.100和端口$_。其中$_这个变量表示当前对象，即本轮循环中的数字（1..1024）

7）"Port $_ is open!") – 当程序发现一个开放的端口时，屏幕打印『Port # is open!』

8）2&gt;$null – 告诉PowerShell遇到任何错误都不显示

上述示例中扫描的端口是1-1024，但是可以很容易改成如（22..53）、(8000..9000)等端口范围。

在PowerShell中另外一种可用的方法是使用Test-NetConnection命令。该命令使用方法差不多，还能够输出更多有用的信息。

<br>

**Test-NetConnection 针对某IP段中单个端口的扫描**

```
foreach ($ip in 1..20) `{`Test-NetConnection -Port 80 -InformationLevel "Detailed" 192.168.1.$ip`}`
```

[![](https://p1.ssl.qhimg.com/t01bba3f57eafc8229f.png)](https://p1.ssl.qhimg.com/t01bba3f57eafc8229f.png)

Test-NetConnection的最大的不足是：该命令是在4.0版本的PowerShell中才引入的。

**命令分解**

1）foreach ($ip in 1..20) `{``}` – 循环遍历数字1到20

2）Test-NetConnection – Test-Connection是一个用来测试不同种类的网络连接的工具

3）-Port 80 – 检查80端口是否可用

4）-InformationLevel "Detailed" – 提供详细的输出信息

5）192.168.1.$ip – 针对列表中的IP地址，依次尝试向80端口发起连接。在本例中，变量$ip从1循环至20

当然，构建一个可以遍历多个系统的多个端口的扫描器也是可行的。

<br>

**针对某IP段 &amp; 多个端口的扫描器**

```
1..20 | % `{` $a = $_; 1..1024 | % `{`echo ((new-object Net.Sockets.TcpClient).Connect("10.0.0.$a",$_)) "Port $_ is open!"`}` 2&gt;$null`}`
```

[![](https://p4.ssl.qhimg.com/t01746b0847826606b3.png)](https://p4.ssl.qhimg.com/t01746b0847826606b3.png)

这一版本的扫描器会对10.0.0.1-20IP段的1-1024端口进行扫描。注意，这可能需要花费较长时间才能完成扫描。一种更有效的方法是手动指定目标端口，比如接下来介绍的：

<br>

**针对某IP段 &amp; 多个端口的扫描器v2**

```
1..20 | % `{` $a = $_; write-host "------"; write-host "10.0.0.$a"; 22,53,80,445 | % `{`echo ((new-object Net.Sockets.TcpClient).Connect("10.0.0.$a",$_)) "Port $_ is open!"`}` 2&gt;$null`}`
```

[![](https://p4.ssl.qhimg.com/t014f71fddabea9bdc7.png)](https://p4.ssl.qhimg.com/t014f71fddabea9bdc7.png)

<br>

**额外奖励 – 测试出口过滤**

许多安全的网络环境会开启出口流量过滤控制，以限制对某些服务的出口协议的访问。这对于提升HTTP/HTTPS/DNS通道的安全性是有好处的，原因之一就在于此。然而，当需要识别出可替代的出站访问时，我们可以在内网中使用PowerShell来评估网络防火墙上的出口过滤器。

**PowerShell测试出口过滤器**

```
1..1024 | % `{`echo ((new-object Net.Sockets.TcpClient).Connect("allports.exposed",$_)) "Port $_ is open" `}` 2&gt;$null
```

[![](https://p4.ssl.qhimg.com/t019f0796220a3ba5bb.png)](https://p4.ssl.qhimg.com/t019f0796220a3ba5bb.png)

有关PowerShell出口测试的更多信息，请参考Beau Bullock在*Black Hills Information Security中发表的文章：[http://www.blackhillsinfosec.com/?p=4811](http://www.blackhillsinfosec.com/?p=4811) 

<br>

**结论**

PowerShell是一个强大的工具，一旦在Windows环境启用了PowerShell，则几乎可以用PS完成任何事情。大家如果有其他相关的PowerShell独门绝技，欢迎留言评论。
