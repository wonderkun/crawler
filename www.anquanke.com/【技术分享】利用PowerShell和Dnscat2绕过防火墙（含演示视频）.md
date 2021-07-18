
# 【技术分享】利用PowerShell和Dnscat2绕过防火墙（含演示视频）


                                阅读量   
                                **144954**
                            
                        |
                        
                                                                                                                                    ![](./img/85764/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85764/t01e3528c0f3d2a31a8.jpg)](./img/85764/t01e3528c0f3d2a31a8.jpg)**

****

翻译：[pwn_361](http://bobao.360.cn/member/contribute?uid=2798962642)

稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

想象一下这种情况，渗透测试人员对目标内网的一台服务器进行测试时，如果该服务器只允许一些特定服务的流量出站，其它出站流量都被防火墙屏蔽时，测试人员使用正常的命令和控制服务方法就可能无法有效控制目标。在这种情况下，测试人员还有一个最后的选择–通过DNS建立命令和控制服务。

使用DNS建立命令和控制服务，实际上就是将C2通信数据嵌入到DNS查询数据中，DNS查询数据穿越互联网DNS分层结构最终到达一个权威DNS服务器，而该DNS权威服务器正好就是你的C2服务器。然后，C2服务器将应答数据嵌入到DNS响应数据中，该DNS响应数据最终被转发给C2客户端，完成数据交互。

Ron Bowes写的[dnscat2](https://github.com/iagox86/dnscat2)在信息安全相关应用中是一个好用的DNS隧道工具。dnscat2通过一个预共享密钥支持通信加密、认证，并支持多个同时会话，和SSH有相似的隧道、命令shell，并支持大多数流行的DNS查询类型(TXT,MX,CNAME,A,AAAA)。dnscat2客户端采用C语言编写，服务器端采用ruby语言编写。

最近，我使用PowerShell脚本重写了[dnscat2客户端](https://github.com/lukebaggett/dnscat2-powershell)的所有功能，不仅如此，我还添加了一些PowerShell特有的功能，因此，现在我们有了一个PowerShell版的dnscat2客户端。PowerShell在攻击者和渗透测试人员中非常流行，这是因为它非常好用，而且由于它支持大多数版本的Windows系统，因此它还存在不错的通用性。在这篇文章中，我将给大家展示如何同时使用dnscat2工具和PowerShell脚本绕过防火墙。

dnscat2除了支持常见的DNS服务器，它也可以将DNS查询数据直接发送到dnscat2服务器，这对我们的测试很有用。在这篇文章中我们的示例只使用了本地连接，不过，你也可以使用DNS权威服务器。

[![](./img/85764/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f379812b6d88e2b4.png)

<br>

**安装**

[在dnscat2的“README.md”文件中，对于如何安装dnscat2服务](https://github.com/iagox86/dnscat2#server)，Ron Bowes提供了相应的教程。当服务安装好以后，你可以使用类似于下面的命令开启该服务：

[![](./img/85764/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0113c9a4af48f37a1a.png)

由于nslookup命令使用的时序DNS事务ID值在最初并不是随机的，因此为了PowerShell客户端能正常工作，需要使用“–no-cache”参数。

同时，为了使用dnscat2-Powershell脚本，目标Windows机器需要支持PowerShell 2.0以上版本。dnscat2-Powershell函数可以通过下面的脚本和命令来加载：

[![](./img/85764/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018e1e0de77e93b8b1.png)

还有一种方法，你可以在PowerShell控制台中使用下面的命令，远程下载并加载脚本：

[![](./img/85764/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01085255a832228196.png)

脚本加载以后，运行下面的命令，开启dnscat2-Powershell服务：

[![](./img/85764/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015384a703356c7a39.png)

“Start-Dnscat2”是dnscat2-Powershell中主函数的名称，它的功能是与服务器建立一个命令会话。 在服务器一端的控制台，你可以远程直接在客户机上执行不同的命令。如下面视频所示：



如果你不想使用命令会话，你也可以使用“Start-Dnscat2”的一些参数，如“-Eexec”，“-ExecPS”，“-Console”。

<br>

**Powershell特性**

我给dnscat2-Powershell脚本添加了一些额外的、和Powershell相关的功能。例如，你可以通过下面的命令，开启一个远程交互式的Powershell会话：

[![](./img/85764/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011d459fdb0f1ca375.png)

你也可以通过给“Start-Dnscat2”传递“-ExecPS”参数，直接开启这个功能。此时，客户端将接收来自服务器端的输入，然后将这个输入数据传递给Invoke-Expression，并返回Invoke-Expression的输出结果。在整个客户端的生命期内，该变量都会保存着。这个功能让攻击者使用一些Powershell工具成为了可能，如PowerSploit。

此外，通过DNS，使用下面的命令，也可以将Powershell脚本直接加载到客户端的内存中，文件无需存盘：

[![](./img/85764/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fe9a247596a0b7cd.png)

如上图，该脚本文件的16进制编码将会被存储在$var变量中。然后，这个变量中的16进制数据可以被转换为一个字符串，并以Powershell函数的形式加载。类似地，需要加载下面的命令：

[![](./img/85764/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0183a7b498b7118d9f.png)

上面的命令会将存储在$var变量中的数组写到/tmp/var文件中。在写这篇文章时，这两个功能都是新加入的，目前还存在一些稳定性问题，对于较小的脚本可能会更稳定一些。

在下面的视频中，我开启了一个远程PowerShell会话，并展示了如何通过DNS加载其它PowerShell脚本。我们的示例是PowerSploit中的Get-Keystrokes脚本。



<br>

**加密**

默认情况下，所有的通信都是加密的。不过可以通过给“Start-Dnscat2”传递“-NoEncryption”参数关闭它，同时，在开启服务端时需要添加“-e open”命令。在不使用通信加密时，所有dnscat2数据包会采用简单的16进制编码，对于那些了解dnscat2协议的人，可能会很容易的恢复出通信数据。通过预共享密钥的认证方法，可以有效阻止中间人攻击。

<br>

**隧道**

dnscat2支持隧道功能，类似于SSH的本地端口转发。dnscat2服务器端开启一个本地监听，然后所有发到这个端口的数据都会经过DNS隧道，到达dnscat2客户端，最后再转发到另一个主机的一个端口上。例如，一个dnscat2客户端所在的内部网络中，有一个SSH服务器，当攻击者需要连接该SSH服务器时，就可能考虑使用该方法。如下面视频所示：



<br>

**躲避探测**

探测DNS隧道的方法有很多。如检查出站DNS查询的长度、监控来自特殊主机的DNS查询频率、检查是否包含那些不常用的查询类型等等。

通过使用“Start-Dnscat2”的“-Delay”和“-MaxRandomDelay”参数，在客户端发送数据包时，设置一个固定的或随机的延时，可有效躲避一些探测。同时，在正常通信时，该延时长短还可以通过“delay &lt;milliseconds&gt;”命令进行修改。

这有助于防止某些系统使用基于频率的分析探测方法。同时，对DNS查询请求设置一个数据传输的最大长度，这对DNS隧道本身是有好处的。如果你想更隐蔽，你可以通过“-MaxPacketSize”参数将最大请求长度设置短一些。

很多DNS隧道使用了TXT、CNAME、或MX查询类型，这是由于处理这些查询的响应过程相对简单，及它们具有比较长的响应数据长度。但是这些不是最常见的查询类型，因此，当这些查询很频繁时，一些IDS可能会发起报警。A和AAAA查询是最常见的，因此，使用这两类查询通常能逃避IDS检测。“Start-Dnscat2”的“-LookupTypes ”参数可用于向客户端传递一个有效的查询类型列表，客户端将从这个列表中随机选择一种类型，并以这种类型发送数据。

下在的视频显示的是这三个选项的组合，及选项的修改对数据传输速度的影响：



<br>

**结论**

使用DNS建立数据传输隧道具有一些实际的好处。最大的好处是，它可以在出站流量限制很严的情况下给攻击者提供一个SHELL控制环境，不过，它的缺点就是数据传输速度可能会比较慢。现在，我们有了PowerShell版的dnscat2客户端，渗透测试人员可以容易的使用基于DNS的C2服务，及熟悉的PowerShell工具。
