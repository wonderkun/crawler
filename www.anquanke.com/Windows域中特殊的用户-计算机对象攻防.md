> 原文链接: https://www.anquanke.com//post/id/196833 


# Windows域中特殊的用户-计算机对象攻防


                                阅读量   
                                **1132520**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t010595b031d9e81bcf.jpg)](https://p4.ssl.qhimg.com/t010595b031d9e81bcf.jpg)



当普通的计算机加入域中时，使用ADExplorer查看该计算机的属性：

[![](https://p3.ssl.qhimg.com/t01e7c51a692c9c0ffe.png)](https://p3.ssl.qhimg.com/t01e7c51a692c9c0ffe.png)

可以看到属性中包含了该计算机的名字($结尾)，创建者的sid，最后密码设置时间，说明在计算机加入域的过程中，windows域为其创建了密码，用于建立与域控之间的安全通道。

如果我们拿到一台域内计算机，并没有域账号登录，此时可以切换到system权限，klist

[![](https://p0.ssl.qhimg.com/t016ff7a74d6c6ebc01.png)](https://p0.ssl.qhimg.com/t016ff7a74d6c6ebc01.png)

可以看到已经有票证在里边，这里其实就是利用的计算机对象的票证，我们可以利用该票证查看域内的管理员，域控，域用户等等信息。

如何查看计算机对象的密码呢，可以借助mimikatz，有两种查看方式：

privilege::debug

sekurlsa::logonPasswords

[![](https://p3.ssl.qhimg.com/t010ec463dc4defc5d2.png)](https://p3.ssl.qhimg.com/t010ec463dc4defc5d2.png)

或者

privilege::debug

token::elevate

lsadump::secrets

[![](https://p5.ssl.qhimg.com/t01c4fda1a9820d4e52.png)](https://p5.ssl.qhimg.com/t01c4fda1a9820d4e52.png)

可以看到计算机对象的密码是120个字符，240字节，有时候密码包含不可见字符，会以十六进制形式显示，类似于如下所示：

[![](https://p0.ssl.qhimg.com/dm/1024_287_/t0158209631d05b5dcf.png)](https://p0.ssl.qhimg.com/dm/1024_287_/t0158209631d05b5dcf.png)

有时候虚拟机中的计算机切换到以前快照，由于当前计算机密码和域控中保存的密码不一致导致建立安全通道失败

[![](https://p0.ssl.qhimg.com/t018daecfaeba3e94af.png)](https://p0.ssl.qhimg.com/t018daecfaeba3e94af.png)

解决的方法大致分为以下几种：
1. 重新加入域
1. 修改及计算机对象密码，使计算机对象密码与域控中保存的密码相同。
第一种方法可能导致计算机中数据丢失，下边介绍第二种方法，修改计算机对象的密码。

官方提供修改计算机对象密码的工具有两种：

reset-ComputerMachinePassword

nltest /sc_change_pwd:galaxy.local

以上两种工具只能在已建立安全通道的情况下修改密码且只能修改随机密码，密码用户不能指定。

分析nltest，发现最后调用了netlogon服务，具体地，就是调用了c:\\windows\system32\netlogon.dll的NlChangePassword函数。

[![](https://p5.ssl.qhimg.com/dm/1024_574_/t019249578832b92062.png)](https://p5.ssl.qhimg.com/dm/1024_574_/t019249578832b92062.png)

通过调用函数NlGenerateRandomBits产生随机密码，因为netlogon服务在lsass进程中，我们使用windbg进行双机调试，在RtlUnicodeString上下断点，修改SourceString内存值为我们想要的密码，比如这里为120个a：

[![](https://p2.ssl.qhimg.com/dm/1024_318_/t01a0afc56bd2cfe2f7.png)](https://p2.ssl.qhimg.com/dm/1024_318_/t01a0afc56bd2cfe2f7.png)

成功修改客户机与域控中计算机对象密码为120个a。

[![](https://p3.ssl.qhimg.com/t017ea025bcc1cf98c9.png)](https://p3.ssl.qhimg.com/t017ea025bcc1cf98c9.png)

下边介绍计算机对象在域渗透中的应用：
1. 维持权限，隐藏后门
默认情况下，计算机对象的密码每30天修改一次，但这是客户端自己设置的，并不受域控影响，我们可以设置计算机对象一直不修改密码

[![](https://p0.ssl.qhimg.com/dm/1024_418_/t012acd95752ac1a9d3.png)](https://p0.ssl.qhimg.com/dm/1024_418_/t012acd95752ac1a9d3.png)

修改DisablePasswordChange为1可以禁止计算机自己修改密码，修改MaximumPasswordAge可以更改默认更新密码的间隔。

这样下次我们想登陆进来的时候可以直接用计算机对象的密码创建白银票据登陆系统：

[![](https://p0.ssl.qhimg.com/dm/1024_524_/t013492c617f7e84009.png)](https://p0.ssl.qhimg.com/dm/1024_524_/t013492c617f7e84009.png)
1. 提权到域控
如果计算机对象在一些高权限的组，那么就可以获取该组的权限。

比如如下计算机test1在域管理员

[![](https://p5.ssl.qhimg.com/t018d94b39bb79b583c.png)](https://p5.ssl.qhimg.com/t018d94b39bb79b583c.png)

那么我们就可以hash传递，使用test1的身份获取访问域控的权限。

[![](https://p0.ssl.qhimg.com/dm/1024_498_/t01f639540dcf3335c0.png)](https://p0.ssl.qhimg.com/dm/1024_498_/t01f639540dcf3335c0.png)

这个常用在对邮箱服务器的攻击上，因为邮箱服务器默认属于Exchange Trusted Subsystem组，对整个域具有写DACL的权限，默认可以拿到域控的权限。
1. 利用计算机创建者身份
使用普通域用户test将test1计算机加入域，查看test1的属性，mS-DS-CreatorSID可以看到创建者的sid：

[![](https://p4.ssl.qhimg.com/t016c2f57ed8b3ec797.png)](https://p4.ssl.qhimg.com/t016c2f57ed8b3ec797.png)

查看test1计算机的DACL：

[![](https://p4.ssl.qhimg.com/dm/1024_314_/t014a5dc26611f8a232.png)](https://p4.ssl.qhimg.com/dm/1024_314_/t014a5dc26611f8a232.png)

可以看到多了重置密码的权限（更改密码需要原来的密码才能更改，比较鸡肋，重置密码可以在不知道原来密码的情况下重置密码）。如果我们拿到了test用户的权限，就可以使用重置密码的权限重置test1计算机的密码，如果test1在高权限的组中，可以完全获得该组的权限（见情况2）

注意：此处重置的是域控中的计算机对象的密码，并没有重置客户端密码，这会导致信任关系失败。

使用以下命令可以重置计算机对象的密码为特定值：

Set-ADAccountPassword test1$ –NewPassword (ConvertTo-SecureString -AsPlainText –String “aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa” -force)
1. 打印机漏洞
微软的spoolsv.exe注册了一个服务和若干个rpc。允许认证用户远程调用，其中RemoteFindFirstPrinterChangeNotificationEx这个函数运行传进一个unc路径，打印机服务就会去请求该unc路径。由于打印机是以system权限运行的（打印机spooler服务运行在system权限下），所以我们访问打印机rpc，迫使打印机服务向我们发起请求拿到的net-ntlm hash是机器用户hash。这样我们就拿到了使任意计算机（域控、邮件服务器对象）向任意机器发起SMB认证的权限。如果我们控制了一台无约束委派的计算机，就可以实现完全控制整个域的目的。
1. CVE-2018-8581
这个漏洞最终可以实现邮箱服务器对象向任意用户发起基于HTTP的NTLM认证，由于HTTP到LDAP可以实现中间人攻击，我们可以中继到域控，利用邮箱服务器的writeDACL特性，可以同步域内用户hash。



## 参考资料：

[https://adsecurity.org/?p=2753](https://galaxylab.com.cn/go/?url=https://adsecurity.org/?p=2753)

[https://adsecurity.org/?p=280](https://galaxylab.com.cn/go/?url=https://adsecurity.org/?p=280)

[https://adsecurity.org/?p=2011](https://galaxylab.com.cn/go/?url=https://adsecurity.org/?p=2011)

[https://ired.team/offensive-security-experiments/active-directory-kerberos-abuse/pass-the-hash-with-machine-accounts](https://galaxylab.com.cn/go/?url=https://ired.team/offensive-security-experiments/active-directory-kerberos-abuse/pass-the-hash-with-machine-accounts)

[https://blog.netspi.com/machineaccountquota-is-useful-sometimes/](https://galaxylab.com.cn/go/?url=https://blog.netspi.com/machineaccountquota-is-useful-sometimes/)

本文由 Galaxy Lab 作者：[杨明强](https://galaxylab.com.cn/author/56/) 发表，其版权均为 Galaxy Lab 所有，文章内容系作者个人观点，不代表 Galaxy Lab 对观点赞同或支持。如需转载，请注明文章来源。
