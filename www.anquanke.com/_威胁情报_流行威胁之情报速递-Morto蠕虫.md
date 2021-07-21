> 原文链接: https://www.anquanke.com//post/id/86029 


# 【威胁情报】流行威胁之情报速递-Morto蠕虫


                                阅读量   
                                **92895**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t016d82fc03f9a99a47.png)](https://p5.ssl.qhimg.com/t016d82fc03f9a99a47.png)



**威胁概述**



Morto恶意代码家族是一种内网传播的蠕虫，最早于2011年被趋势科技披露。360威胁情报中心的监测显示在国内该家族到目前都非常活跃，需要网络安全管理员引起重视进行处理。

通过对该家族所使用的C&amp;C域名的监控，我们看到最近一个月中该恶意代码的感染情况如下图：

[![](https://p5.ssl.qhimg.com/t01117d457b9000ec97.png)](https://p5.ssl.qhimg.com/t01117d457b9000ec97.png)

感染的IP分布大致如下：

[![](https://p5.ssl.qhimg.com/t018b362192f893dd2c.png)](https://p5.ssl.qhimg.com/t018b362192f893dd2c.png)

其中在国内各省份的感染分布状态如下：

[![](https://p3.ssl.qhimg.com/t01c1c48992c09ba0e8.png)](https://p3.ssl.qhimg.com/t01c1c48992c09ba0e8.png)



**威胁情报**



以下是威胁相关的情报，读者可以根据需要进行对应的处理，360所有支持威胁情报的产品（天眼、NGSOC、智慧防火墙等）都已经内置了检测。

[![](https://p0.ssl.qhimg.com/t01d1398560d3b614a3.png)](https://p0.ssl.qhimg.com/t01d1398560d3b614a3.png) 

**技术分析**



整体而言，恶意代码分为三个部分，maindrop，loader，payload。

<br>

**maindrop**



该模块主要用于运行环境初始化，相应模块的释放。

通过IDA加载之后发现样本的导入函数表如下，通常样本为了防止研究员分析会采取动态函数的方式获取需要调用的API的地址，使用Loadlibrary/GetProAddress的方式加载，但是这个地方发现导入函数中并不包含这两个基本的函数。

[![](https://p2.ssl.qhimg.com/t0180bba840a2818c21.png)](https://p2.ssl.qhimg.com/t0180bba840a2818c21.png)

因此怀疑该样本使用了shellcode中常用的API获取方式，即通过fs获取kernel32基地址，并解析该dll导出函数的方式获取必要的API。

分析代码之后发现，该函数确实通过fs这个寄存器获取了当前进程加载的dll信息，并从中遍历出kernel32的地址。

[![](https://p1.ssl.qhimg.com/t017a52f56dc9cd5542.png)](https://p1.ssl.qhimg.com/t017a52f56dc9cd5542.png)

可以看到获取对应的基地址之后通过解析其导出表获取对应的函数，如下图所示：

[![](https://p4.ssl.qhimg.com/t01877aef70c846a5f8.png)](https://p4.ssl.qhimg.com/t01877aef70c846a5f8.png)

之后解密并运行，如下图所示创建以下几个注册表项，并释放出Loader clb.dll。

[![](https://p0.ssl.qhimg.com/t011822af138b7c6dcb.png)](https://p0.ssl.qhimg.com/t011822af138b7c6dcb.png)

其中上述的注册表HKLM\SYSTEM\WPA\md中保存了对应加密版的payloader，可以看到其长度为444402。

[![](https://p0.ssl.qhimg.com/t017a19383cbc603ae8.png)](https://p0.ssl.qhimg.com/t017a19383cbc603ae8.png)

之后maindrop开启一个regedit.exe进程。

<br>

**loader**



注册表进程默认的情况下会加载clb.dll这个dll，maindrop之前在windows目录下已经释放了同名的恶意clb.dll，由于Windows的dll加载机制，此处将导致regedit进程将恶意的clb.dll加载。

[![](https://p2.ssl.qhimg.com/t0100802aa3a93cde5c.png)](https://p2.ssl.qhimg.com/t0100802aa3a93cde5c.png)[![](https://p4.ssl.qhimg.com/t0100802aa3a93cde5c.png)](https://p4.ssl.qhimg.com/t0100802aa3a93cde5c.png)

clb.dll运行之后会从HKLM\SYSTEM\WPA\md中解密出对应的payload并加载运行，之后会创建以下两个文件，cache实际为一个loader。

C:WINDOWSOffline Web Pagescache.txt

C:WINDOWSsystem32Sens32.dll

<br>

**payload**

payload主要用于和远程进行通信并实现RDP扫描。

<br>

**杀软对抗**

运行之后针对主流杀软做了相应的监控。

Ekrn，avguard，360rp，zhudongfangyu，RavMonD，kxescore，KVSrvXP，ccSvcHst，avgwdsvc，MsMpEng，vsserv，mcshield，fsdfwd，GDFwSvc，coreServiceShell，avp，MPSvc，PavFnSvr，knsdave，AvastSvc，avpmapp，SpySweeper，K7RTScan，SavService，Vba32Ldr，scanwscs，NSESVC.EXE，FortiScand，FPAVServer，a2service，freshclam，cmdagent，ArcaConfSV，ACAAS

 下图为其中对360的监控代码：

[![](https://p0.ssl.qhimg.com/t01e38934b30ce6288a.png)](https://p0.ssl.qhimg.com/t01e38934b30ce6288a.png)



**C&amp;C通信**



在更新线程里，蠕虫尝试连接内置的硬编码域名，所下图所示，不同变种会有所区别。 

[![](https://p5.ssl.qhimg.com/t0160dff2f63774fd19.png)](https://p5.ssl.qhimg.com/t0160dff2f63774fd19.png)

和CC的通讯是通过DNS查询实现的，对内置的域名进行DNS查询，查询类型为DNS_TYPE_TEXT，通过这种方式实现和C&amp;C的通讯。

[![](https://p2.ssl.qhimg.com/t012c10f355b086c4c0.png)](https://p2.ssl.qhimg.com/t012c10f355b086c4c0.png)

服务器返回加密后的数据，具体如下，由于调试的样本没有接收到对应的返回包，此处引用Symantec的图片。

[![](https://p5.ssl.qhimg.com/t01ca9988a646cd6597.png)](https://p5.ssl.qhimg.com/t01ca9988a646cd6597.png)

解密加密的数据包，获取对应的操作指令。

[![](https://p5.ssl.qhimg.com/t013abc3477074b33cd.png)](https://p5.ssl.qhimg.com/t013abc3477074b33cd.png)

解密数据包后，根据服务端下发的指令执行相关操作，如下图所示的开启新线程，cmd执行，注册表写入等操作。 

[![](https://p5.ssl.qhimg.com/t01bb155953c77143ed.png)](https://p5.ssl.qhimg.com/t01bb155953c77143ed.png)

[![](https://p5.ssl.qhimg.com/t01811185d7017a0f1c.png)](https://p5.ssl.qhimg.com/t01811185d7017a0f1c.png)

[![](https://p1.ssl.qhimg.com/t0183d17614b01e20ef.png)](https://p1.ssl.qhimg.com/t0183d17614b01e20ef.png)



**RDP暴力破解**



Morto的传播主要通过RDP协议登录并进行弱口令爆破实现。

样本开启一个专用于爆破的线程，在线程里循环随机生成一个目标IP，检查合法性后尝试对其进行爆破。使用到的用户名如下：

1,123,a,actuser,adm,admin,admin1,admin2,administrator,aspnet,backup,console,david,guest,john,owner,owner,root,server,sql,support,support_388945a0,sys,test,test1,test2,test3,user,user1,user2,user3,user4,user5

使用的弱密码如下：

!@#$,!@#$%,!@#$%^,!@#$%^&amp;*,%u%,%u%1,%u%111111,%u%12,%u%123,%u%1234,%u%123456,0,000000,1,111,1111111111,1111111,111222,112233,11223344,12,121212,123,123123,123321,1234,12344321,12345,123456,1234567,12345678,123456789,1234567890,1234qwer,1313,1314520,159357,168168,1QAZ,1q2w3e,1qaz2wsx,2010,2011,2012,2222,222222223,31415926,369,4321,520,520520,654321,666666,7,7777,7777777,77777777,789456,888888,88888888,987654,987654321999999,PASSWORD,Password,aaaa,abc,abc123,abcd,abcd1234,admin,admin123,computer,dragon,iloveyou,letmein,pass,password,princess,qazwsx,rockyou,root,secret,server,super,test,user,zxcvbnm

[![](https://p3.ssl.qhimg.com/t01e900b05c2b781eae.png)](https://p3.ssl.qhimg.com/t01e900b05c2b781eae.png)

开启RDP登录：

[![](https://p4.ssl.qhimg.com/t01a019bea31428af5d.png)](https://p4.ssl.qhimg.com/t01a019bea31428af5d.png)

 

在RDP登陆成功后，尝试使用管理员账号执行以下操作，执行感染操作，由于a.dll样本使用的是rundll32.exe进行启动，因此首先通过r.reg将rundll32.exe设置为administrator以便与后续样本dll的执行。

[![](https://p0.ssl.qhimg.com/t018cd5122edfe6dbff.png)](https://p0.ssl.qhimg.com/t018cd5122edfe6dbff.png)

木马中RDP的协议采用了开源代码实现，经过代码对比，应该是采用了rdesktop早期版本实现：

[![](https://p2.ssl.qhimg.com/t01c3b3bf326a10af67.png)](https://p2.ssl.qhimg.com/t01c3b3bf326a10af67.png)

[![](https://p1.ssl.qhimg.com/t01fd512dc0bea6e219.png)](https://p1.ssl.qhimg.com/t01fd512dc0bea6e219.png)



**总结**



作为一个曝光6年却依然活动的蠕虫，Morto还是有一定的技术特点，如通过clb加载恶意dll，C&amp;C采用DNS查询的方式进行通信，payload通过注册表保存（应该算是早期无文件样本的雏形了）等。这个蠕虫的流行也时刻提醒我们无论在什么环境，弱口令都是企业内部安全需要关注的一大问题。

<br>

**参考引用**



https://www.mysonicwall.com/sonicalert/searchresults.aspx?ev=article&amp;id=367

https://www.symantec.com/connect/blogs/morto-worm-sets-dns-record

https://www.f-secure.com/v-descs/worm_w32_morto_a.shtml

<br style="text-align: left">
