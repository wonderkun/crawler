> 原文链接: https://www.anquanke.com//post/id/204510 


# pipePotato：一种新型的通用提权漏洞


                                阅读量   
                                **773178**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">12</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t0187ae05ab8d67c627.jpg)](https://p0.ssl.qhimg.com/t0187ae05ab8d67c627.jpg)



作者：xianyu &amp; daiker

## 0x00 影响

本地提权，对于任意windows Server 2012以上的windows server版本(win8以上的某些windows版本也行)，从Service用户提到System 用户，在windows Server 2012，windows Server 2016，windows Server 2019全补丁的情况都测试成功了。



## 0x01 攻击流程

[![](https://p3.ssl.qhimg.com/t01ac4f91025ff47bbe.gif)](https://p3.ssl.qhimg.com/t01ac4f91025ff47bbe.gif)

演示基于server 2019
- laji.exe. msf 生成的正常木马
- pipserver.exe 命名管道服务端，注册命名管道
- spoolssClient.exe 打印机rpc调用客户端
首先，攻击者拥有一个服务用户，这里演示采用的是IIS服务的用户。攻击者通过pipeserver.exe注册一个名为pipexpipespoolss的恶意的命名管道等待高权限用户来连接以模拟高权限用户权限，然后通过spoolssClient.exe迫使system用户来访问攻击者构建的恶意命名管道，从而模拟system用户运行任意应用程序



## 0x02 漏洞成因

spoolsv.exe 进程会注册一个 rpc 服务,任何授权用户可以访问他，RPC 服务里面存在一个函数 RpcRemoteFindFirstPrinterChangeNotificationEx

[![](https://p0.ssl.qhimg.com/t01821f023750f036c1.jpg)](https://p0.ssl.qhimg.com/t01821f023750f036c1.jpg)

[https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/eb66b221-1c1f-4249-b8bc-c5befec2314d](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/eb66b221-1c1f-4249-b8bc-c5befec2314d)

[![](https://p4.ssl.qhimg.com/t01b25d3622f25f7a03.png)](https://p4.ssl.qhimg.com/t01b25d3622f25f7a03.png)

pszLocalMachine 可以是一个 UNC 路径(\host)，然后 system 用户会访问 \hostpipespoolss,

[![](https://p5.ssl.qhimg.com/t011b500cbb67eecf63.png)](https://p5.ssl.qhimg.com/t011b500cbb67eecf63.png)

[![](https://p1.ssl.qhimg.com/t011de1e8a84a3ce3c4.png)](https://p1.ssl.qhimg.com/t011de1e8a84a3ce3c4.png)

在文档 [https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/9b3f8135-7022-4b72-accb-aefcc360c83b里面](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-rprn/9b3f8135-7022-4b72-accb-aefcc360c83b%E9%87%8C%E9%9D%A2)

server name 是这样规范的

```
SERVER_NAME = "\" host "" | ""

```

如果 SERVER_NAME 是 \127.0.0.1 ,system用户会访问 \127.0.0.1pipespoolss

[![](https://p5.ssl.qhimg.com/t010b1d4affbb38fd95.png)](https://p5.ssl.qhimg.com/t010b1d4affbb38fd95.png)

问题是，如果 SERVER_NAME 是\127.0.0.1/pipe/xx,system用户会访问\127.0.0.1pipexxxpipespoolss，这个命名管道并没有注册，攻击者就可以注册这个命名管道。

[![](https://p5.ssl.qhimg.com/t01f5742409a28ab83a.png)](https://p5.ssl.qhimg.com/t01f5742409a28ab83a.png)

[![](https://p5.ssl.qhimg.com/t01b420baccca7597a9.png)](https://p5.ssl.qhimg.com/t01b420baccca7597a9.png)

当 system 用户访问这个命名管道(pipexpipespoolss)，我们就能模拟system 用户开启一个新的进程。

[![](https://p0.ssl.qhimg.com/t01327dc02530a7f428.png)](https://p0.ssl.qhimg.com/t01327dc02530a7f428.png)

[![](https://p2.ssl.qhimg.com/t01c9973219a8cea7c9.png)](https://p2.ssl.qhimg.com/t01c9973219a8cea7c9.png)



## 0x03 时间线

2019年12月5日 向MSRC进行反馈，分配编号`VULN-013177` `CRM:0279000283```

[![](https://p1.ssl.qhimg.com/t011c9569f5db6ffe4b.jpg)](https://p1.ssl.qhimg.com/t011c9569f5db6ffe4b.jpg)

2019年12月5日 分配Case编号 `MSRC Case 55249`

[![](https://p0.ssl.qhimg.com/t013b7ee084eddc620c.jpg)](https://p0.ssl.qhimg.com/t013b7ee084eddc620c.jpg)

2019年12月15日 向MSRC发邮件询求进度，微软2019年12月18日回复

[![](https://p0.ssl.qhimg.com/t01495717942210e6ee.jpg)](https://p0.ssl.qhimg.com/t01495717942210e6ee.jpg)

[![](https://p3.ssl.qhimg.com/t01c277fe1aa4948f40.jpg)](https://p3.ssl.qhimg.com/t01c277fe1aa4948f40.jpg)

2019年12月27日 MSRC 回信认为impersonate的权限需要administrator或者等同用户才拥有，Administrator-to-kernel并不是安全问题。事实上，所有的service 用户(包括local service，network service 都具备这个权限)。我们向MSRC发邮件反馈此事

```
the account used to impersonate the named pipe client use the SeImpersonatePrivilege. The SeImpersonatePrivilege is only available to accounts that have administrator or equivalent privileges. Per our servicing criteria: Administrator-to-kernel is not a security boundary.
```

[![](https://p4.ssl.qhimg.com/t0171974e696ba36218.jpg)](https://p4.ssl.qhimg.com/t0171974e696ba36218.jpg)

[![](https://p2.ssl.qhimg.com/t01567806d5a299b309.jpg)](https://p2.ssl.qhimg.com/t01567806d5a299b309.jpg)

2019年12月28日 MSRC 回信会处理，至今没有回信

[![](https://p3.ssl.qhimg.com/t013a5aafc6c86694e5.jpg)](https://p3.ssl.qhimg.com/t013a5aafc6c86694e5.jpg)

2020年5月6日 在安全客上披露
