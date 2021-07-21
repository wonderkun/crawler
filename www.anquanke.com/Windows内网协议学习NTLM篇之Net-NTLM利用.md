> 原文链接: https://www.anquanke.com//post/id/194069 


# Windows内网协议学习NTLM篇之Net-NTLM利用


                                阅读量   
                                **1311401**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01da0b6cd153e1bc69.jpg)](https://p0.ssl.qhimg.com/t01da0b6cd153e1bc69.jpg)



作者：daiker@360RedTeam

## 0x00 前言

在上一篇文章[Windows内网协议学习NTLM篇之发起NTLM请求](https://www.anquanke.com/post/id/193493)里面,讲了12种发起NTLM请求的方式。这篇文章接着上文，主要讲解拿到NTLM 请求之后的进一步利用。有Net-NTLM Hash的破解(v1 和 v2)以及Relay到支持NTLM SSP的协议，事实上，只要是支持NTLM SSP的协议，都可以Relay过去，本文主要讲的是几种比较常遇到，且能达到命令执行效果的，SMB,EWS,LDAP。



## 0x01 Net-NTLM Hash的破解

### <a name="header-n7"></a>1. Net-NTLM v1 的破解

先上结论。只要获取到Net-NTLM v1，都能破解为NTLM hash。与密码强度无关。

具体操作如下。
1. 修改Responder.conf里面的Challenge为1122334455667788(使用[SpiderLabs版本](https://github.com/SpiderLabs/Responder)的 话默认是1122334455667788，但该版本已经停止更新了，建议使用[lgandx版本](https://github.com/lgandx)，这一版本默认为Random，需要修改)
[![](https://p1.ssl.qhimg.com/t01c9e547013813141e.png)](https://p1.ssl.qhimg.com/t01c9e547013813141e.png)
1. 将type2里面的NTLMSSPNEGOTIATEEXTENDED_SESSIONSECURITY位置0。
如果知道发来的请求一定是SMB 协议的话，Responder里面加上–lm参数即可，

[![](https://p5.ssl.qhimg.com/t01f906b672474d267b.png)](https://p5.ssl.qhimg.com/t01f906b672474d267b.png)

其他协议就得去找改协议发送type2 处的代码，修改NegoFlags位。

比如Http协议的话，需要修改packets.py里面的NTLM_Challenge类。

原来是NegoFlags的值是\x05\x02\x89\xa2，改成\x05\x02\x81\xa2

[![](https://p1.ssl.qhimg.com/t01b394c527f0f43bf6.png)](https://p1.ssl.qhimg.com/t01b394c527f0f43bf6.png)

[![](https://p4.ssl.qhimg.com/t01174dff12d5f3c840.png)](https://p4.ssl.qhimg.com/t01174dff12d5f3c840.png)
1. 然后获取到Net-NTLM v1。再使用[ntlmv1-multi](https://github.com/evilmog/ntlmv1-multi)里面的ntlmv1.py转换.
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0158930effb9bc017c.png)

获取到Net-NTLM v1是win10::WIN10-1:F1586DA184365E9431C22EF206F5A2C918659E1B1FD7F64D:F1586DA184365E9431C22EF206F5A2C918659E1B1FD7F64D:1122334455667788

[![](https://p4.ssl.qhimg.com/t01bd2d587368f77213.png)](https://p4.ssl.qhimg.com/t01bd2d587368f77213.png)

转化完的格式就是NTHASH:F1586DA184365E9431C22EF206F5A2C918659E1B1FD7F64D
1. 再将转化完的格式用[crack.sh](https://crack.sh/get-cracking/)破解即可。
[![](https://p3.ssl.qhimg.com/t0128e4dc2b42b21b4f.png)](https://p3.ssl.qhimg.com/t0128e4dc2b42b21b4f.png)

[![](https://p3.ssl.qhimg.com/t0120d1a440723430c4.png)](https://p3.ssl.qhimg.com/t0120d1a440723430c4.png)



下面简要探究下原理，如果没有兴趣的可以直接跳过。看下一小节。

之前在[NTLM基础介绍](https://www.anquanke.com/post/id/193149)里面有简单介绍了下Net-NTLM v1的加密方式

将 16字节的NTLM hash空填充为21个字节，然后分成三组，每组7字节，作为3DES加密算法的三组密钥，加密Server发来的Challenge。 将这三个密文值连接起来得到response。

但是在实践中发现，加密方式的表述是有点问题的，或者说是不完整的。上面的只是Net-NTLM v1的一种加密方式，Net-NTLM v1还有另外一种加密方式。我们下面来探讨下这两种加密方式以及利用

（1）加密方式1

就是前面提到的那种。
1. 将 16字节的NTLM hash空填充为21个字节，然后分成三组，每组7字节
1. 将三组(每组7字节)经过运算后作为DES加密算法的密钥
运算的细节是每组七个字节再转化为8小组，每个小组7个比特位。然后7个比特位进行奇偶校验后算出第8个比特位，刚好是1个字节，8个小组，每小组一个字节，凑成8个字节的密钥。
1. 加密Server Challenge
1. 将这三个密文值连接起来得到response。
在Responder如果想获取到这种加密方式的话，要加上参数–lm(仅限于smb 协议)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d63b93995c878fbe.png)

那这种加密方式存在什么问题呢。

总共三组，每组8个字节作为key，加密Server Challenge获取response。

每组可以分开计算，已知加密内容和加密后的密文算key。使用des算法，key是八个字节。

我们控制Server Challenge为1122334455667788，然后建立从key到response的彩虹表。就可以在知道response的情况下获取key。所幸[crack.sh](https://crack.sh/get-cracking/)这个网站已经帮我们弄好了，在Challenge为1122334455667788的情况下。一分钟之内就能获取ntlm hash，而且是免费的。这也是我们为啥要把Challenge设置为1122334455667788，而不是随机。

具体操作是

[![](https://p5.ssl.qhimg.com/t0132880b94410dae2c.png)](https://p5.ssl.qhimg.com/t0132880b94410dae2c.png)

使用[ntlmv1-multi](https://github.com/evilmog/ntlmv1-multi)里面的ntlmv1.py转换.然后复制NTHASH:E0F8C5B5E45247B4175698B99DBB5557CCD9241EA5A55CFB到[crack.sh](https://crack.sh/get-cracking/)破解，填上邮箱，等到一分钟左右就能收到ntlm hash了。

（2）加密方式2

跟第一种加密方式基本一样。最本质的区别就在于，第一种加密方式的加密内容是Server Challenge。而这种加密方式是拼接8字节Server Challenge和8字节Client Challenge后，求其MD5，然后取MD5值的前8字节做为加密内容。

我们可以控制Server Challenge为固定的值，但是没法控制Client Challenge的值。也就是说我们没法控制加密的内容为固定的值。

第一种是加密的内容为固定的1122334455667788的话，我们只需要建立从key到response的映射就行。而这种加密方式的话。加密的内容也是不固定的，计算的成本高多了。

在Responder默认获取到的就是这种加密方式(没有加–lm)

[![](https://p3.ssl.qhimg.com/t0106c862f031974d12.png)](https://p3.ssl.qhimg.com/t0106c862f031974d12.png)

使用[ntlmv1-multi](https://github.com/evilmog/ntlmv1-multi)里面的ntlmv1-ssp.py转换.

[![](https://p1.ssl.qhimg.com/t013c756e1e531eb39e.png)](https://p1.ssl.qhimg.com/t013c756e1e531eb39e.png)

到[crack.sh](https://crack.sh/get-cracking/)破解。这种方式要钱的，而且还不一定能解的出来。

[![](https://p0.ssl.qhimg.com/t0194963a9bb9eb3931.png)](https://p0.ssl.qhimg.com/t0194963a9bb9eb3931.png)

总而言之，这种加密方式不好破解，其实我们也可以不让客户端不用这种加密方式，就使用第一种加密方式。且看下面的分析。

在我们的Responder加上–lm的情况下获取到的Net-NTLM v1 hash是采用第一种加密方式，但是只针对smb协议有效，在我的测试中，即使加了–lm参数，收到的请求是Http协议的情况底下，拿到的Net-NTLM v1也是采用第二种加密方式，我们不好破解。所以我又去研究了下什么情况底下采用第一种加密方式，什么情况底下采用第二种加密方式。

在这篇[文章](%5bhttp:/d1iv3.me/2018/12/08/LM-Hash%E3%80%81NTLM-Hash%E3%80%81Net-NTLMv1%E3%80%81Net-NTLMv2%E8%AF%A6%E8%A7%A3/%5d(http:/d1iv3.me/2018/12/08/LM-Hash%E3%80%81NTLM-Hash%E3%80%81Net-NTLMv1%E3%80%81Net-NTLMv2%E8%AF%A6%E8%A7%A3/))里面有提及到,当ntlm的flag位NTLMSSPNEGOTIATEEXTENDED_SESSIONSECURITY置为1的情况底下，会采用第二种加密方式，否则就会采用第一种加密方式，我们可以看下impacket里面计算Net-NTLM v1的相关代码

[![](https://p4.ssl.qhimg.com/t01376b1881628d8ad2.png)](https://p4.ssl.qhimg.com/t01376b1881628d8ad2.png)

可以很清楚的看到，当NTLMSSPNEGOTIATEEXTENDED_SESSIONSECURITY位置为1的时候，加密的内容不是server challenge，而是md5 hash 运算过的server challeng+client challent的前8位。也就是说是第二种加密方式。

那NTLMSSPNEGOTIATEEXTENDEDSESSIONSECURITY flag来自于哪里呢。我们知道ntlm分为type1，type2，type3。计算response就在type 3里面，NTLMSSPNEGOTIATEEXTENDEDSESSIONSECURITY flag位就来自于type2。而type 2 里面的内容正常就是我们返回给客户端的。

[![](https://p4.ssl.qhimg.com/t016cddbd93eb8d60d9.png)](https://p4.ssl.qhimg.com/t016cddbd93eb8d60d9.png)

也就是说，客户端选择加密方式1还是加密方式2，这个是由我们可以控制的。只需要我们把NTLMSSPNEGOTIATEEXTENDED_SESSIONSECURITY位置为0，那么客户端就会选择加密方式1.并且Server Challenge为1122334455667788的情况下。我们用crack.sh快速免费有效得破解。获取到用户的NTLM Hash。

那怎么将NTLMSSPNEGOTIATEEXTENDEDSESSIONSECURITY位置为0，我们一般都是使用现成的工具Resonder来获取Net-NTLM Hash。之前说过加上–lm参数就可以将NTLMSSPNEGOTIATEEXTENDEDSESSIONSECURITY位置为0。

这个时候还有一个小问题没有解决，那就是Resonder加上–lm，为什么只针对smb 协议有效。其他协议无效。

我去读了下Responder的代码。

[![](https://p1.ssl.qhimg.com/t0101984f741e7c2ec8.png)](https://p1.ssl.qhimg.com/t0101984f741e7c2ec8.png)

加上–lm参数之后，调用的模块就是SMB1LM

[![](https://p5.ssl.qhimg.com/t019e464c3364166988.png)](https://p5.ssl.qhimg.com/t019e464c3364166988.png)

发现她用的是老板本的smb实现。而这个版本的实现是在smb 协商版本的时候就将challenge返回，并且将NTLMSSPNEGOTIATEEXTENDED_SESSIONSECURITY置为0.

[![](https://p1.ssl.qhimg.com/t014dadb355e086e791.png)](https://p1.ssl.qhimg.com/t014dadb355e086e791.png)

而且也仅仅是实现了smb协议，并没有实现其他协议。

但是完全可以不用老板本的smb实现。这里面最本质的地方在于NTLMSSPNEGOTIATEEXTENDED_SESSIONSECURITY置为0.而这个flag位并不一定需要用到旧版本的smb才能置位。只需要修改NTLM SSP里面的flag位就行

在各个协议里面的NTLM SSP里面，修改flag位，我们找到Responder里面type2的NTLM SSP的flag位赋值的地方即可。

Responder里面的NTLM SSP实现没有通用性。比如smb部分的实现，在packets.py里面的SMBSession1Data类里面。

[![](https://p1.ssl.qhimg.com/t01bfe01fc9856d1f83.png)](https://p1.ssl.qhimg.com/t01bfe01fc9856d1f83.png)

默认是0xe2898215(跟图里面不一样?大端小端)

[![](https://p1.ssl.qhimg.com/t0107ee39758fe5b30c.png)](https://p1.ssl.qhimg.com/t0107ee39758fe5b30c.png)

NTLMSSPNEGOTIATEEXTENDED_SESSIONSECURITY对应的是第13位，改为0，也就是0xe2818215

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cae0c8fdc7a179d7.png)

改下就行

[![](https://p3.ssl.qhimg.com/t012278654999b55d28.png)](https://p3.ssl.qhimg.com/t012278654999b55d28.png)

http的话在packets.py里面的NTLM_Challenge类里面

[![](https://p3.ssl.qhimg.com/t01d039cfd2e1e7e262.png)](https://p3.ssl.qhimg.com/t01d039cfd2e1e7e262.png)

Responder的NTLM SSP没有通用性，这个挺难受的，其他协议的话，大家自己找吧。跟下代码挺快的。

### <a name="header-n95"></a>2. Net-NTLM v2的破解

Net-NTLM v2 现在也没有什么比较好用的破解方式，一般就是利用hashcat 离线爆破明文密码，能不能跑出来就看字典里面有没有了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016e6e65ccb92d13aa.png)

使用hashcat进行字典破解

```
hashcat -m 5600  win10::TEST:1122334455667788:622DED0816CFF5A0652209F20A7CF17A:0101000000000000C0653150DE09D201532C07A7DEE654B8000000000200080053004D004200330001001E00570049004E002D00500052004800340039003200520051004100460056000400140053004D00420033002E006C006F00630061006C0003003400570049004E002D00500052004800340039003200520051004100460056002E0053004D00420033002E006C006F00630061006C000500140053004D00420033002E006C006F00630061006C0007000800C0653150DE09D2010600040002000000080030003000000000000000010000000020000067840C88904F15E659858A3CBA35EBEF61A38EC88C5E3D26B968F1C20C9ACAC10A001000000000000000000000000000000000000900220063006900660073002F003100370032002E00310036002E003100300030002E0031000000000000000000 /tmp/password.dic --force
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01350d78343be40c3f.png)



## 0x02 Relay

在Net-NTLM Hash的破解里面，如果是v1的话，拿到Net-NTLM就相当于拿NTLM HASH.这个时候就没有Relay的必要性了，但是在实际中遇到的例子往往不会是v1，而是v2。这个时候密码强度高一点，基本就跑不出来了，这种情况底下，不妨试一试Relay。

### <a name="header-n101"></a>1. Relay2SMB

能直接relay到smb服务器，是最直接最有效的方法。可以直接控制该服务器(包括但不限于在远程服务器上执行命令，上传exe到远程命令上执行，dump 服务器的用户hash等等等等)。

主要有两种场景
1. 工作组环境
这个实用性比较差。在工作组环境里面，工作组中的机器之间相互没有信任关系，每台机器的账号密码Hash只是保存在自己的SAM文件中，这个时候Relay到别的机器，除非两台机器的账号密码一样(如果账号密码一样，我为啥不直接pth呢)，不然没有别的意义了，这个时候的攻击手段就是将机器reflect回机子本身。因此微软在ms08-068中对smb reflect到smb 做了限制。这个补丁在CVE-2019-1384(Ghost Potato)被绕过。将在下篇文章里面详细讲。
1. 域环境
域环境底下域用户的账号密码Hash保存在域控的 ntds.dit里面。如下没有限制域用户登录到某台机子，那就可以将该域用户Relay到别人的机子，或者是拿到域控的请求，将域控Relay到普通的机子，比如域管运维所在的机子。(为啥不Relay到其他域控，因为域内就域控默认开启smb签名)

下面演示使用几款工具在域环境底下，从域控relay到普通机器执行命令
1. impacket 的底下的smbrelayx.py
[![](https://p4.ssl.qhimg.com/t012ee0b80cc466abc8.png)](https://p4.ssl.qhimg.com/t012ee0b80cc466abc8.png)
1. impacket 的底下的ntlmrelayx.py
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0131dd776b88b153cf.png)
1. Responder底下的MultiRelay.py
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cfa61118515bacf1.png)

[![](https://p5.ssl.qhimg.com/t01555e8f7ad44b8772.png)](https://p5.ssl.qhimg.com/t01555e8f7ad44b8772.png)

### <a name="header-n119"></a>2. Relay2EWS

Exchange的认证也是支持NTLM SSP的。我们可以relay的Exchange，从而收发邮件，代理等等。在使用outlook的情况下还可以通过homepage或者下发规则达到命令执行的效果。而且这种Relay还有一种好处，将Exchange开放在外网的公司并不在少数，我们可以在外网发起relay，而不需要在内网，这是最刺激的。

下面演示通过[NtlmRelayToEWS](https://github.com/Arno0x/NtlmRelayToEWS.git)(事实上，工具挺多的。其他的大家可以上github自己找)来实现Relay2ews

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016228fd46b9b7958d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0152a4e3074346a7d0.png)

配合homepage 能够实现命令执行的效果

homepage的简易demo代码如下

```
&lt;html&gt;
&lt;head&gt;
&lt;meta http-equiv="Content-Language" content="en-us"&gt;
&lt;meta http-equiv="Content-Type" content="text/html; charset=windows-1252"&gt;
&lt;title&gt;Outlook&lt;/title&gt;
&lt;script id=clientEventHandlersVBS language=vbscript&gt;
&lt;!--
Sub window_onload()
Set Application = ViewCtl1.OutlookApplication
Set cmd = Application.CreateObject("Wscript.Shell")
cmd.Run("calc")
End Sub
--&gt;

&lt;/script&gt;
&lt;/head&gt;

&lt;body&gt;
&lt;object classid="clsid:0006F063-0000-0000-C000-000000000046" id="ViewCtl1" data="" width="100%" height="100%"&gt;&lt;/object&gt;
&lt;/body&gt;
&lt;/html&gt;
```

放置于web服务器。在[NtlmRelayToEWS](https://github.com/Arno0x/NtlmRelayToEWS.git) 里面通过-u 参数指定。

[![](https://p3.ssl.qhimg.com/t01e6b7ccae1f57ce6b.png)](https://p3.ssl.qhimg.com/t01e6b7ccae1f57ce6b.png)

[![](https://p0.ssl.qhimg.com/t01bc4bfb843ea2e34d.png)](https://p0.ssl.qhimg.com/t01bc4bfb843ea2e34d.png)

### <a name="header-n126"></a>3. Relay2LDAP

不管是杀伤力巨大的8581还是1040。Relay到ldap都在里面发挥着巨大的作用。

relay 到ldap的话，能干嘛呢

这里着重介绍三种通用性比较强的利用思路。这三种在impacket里面的ntlmrelayx都有实现。(这三种通用性比较强而已，实际中这个的利用比较灵活，需要通过 nTSecurityDescriptor分析用户在域内对哪些acl有权限，什么权限。关于acl怎么深入利用,这里不再展开，后面在ldap篇会详细说明)

[![](https://p2.ssl.qhimg.com/t017117828f8c01b60b.png)](https://p2.ssl.qhimg.com/t017117828f8c01b60b.png)
1. 高权限用户
如果NTLM发起用户在以下用户组
- Enterprise admins
- Domain admins
- Built-in Administrators
- Backup operators
- Account operators
那么就可以将任意用户拉进该组，从而使该用户称为高权限用户，比如域管

[![](https://p5.ssl.qhimg.com/t01bc457194a9aa7632.png)](https://p5.ssl.qhimg.com/t01bc457194a9aa7632.png)

[![](https://p2.ssl.qhimg.com/t01751ce0909a4a4ec4.png)](https://p2.ssl.qhimg.com/t01751ce0909a4a4ec4.png)
1. write-acl 权限
如果发起者对域有write-acl 权限，那么就可以在域内添加两台acl

```
'DS-Replication-Get-Changes'     = 1131f6aa-9c07-11d1-f79f-00c04fc2dcd2
'DS-Replication-Get-Changes-All' = 1131f6ad-9c07-11d1-f79f-00c04fc2dcd2
```

acl的受托人可以是任意用户，从而使得该用户可以具备dcsync的权限

这个案例的典型例子就是Exchange Windows Permissions组，我们将在下一篇介绍8581的 时候详细说下这个用户组的权限。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b9e86c52ee600cc1.png)

[![](https://p1.ssl.qhimg.com/t01165b695e6341bce5.png)](https://p1.ssl.qhimg.com/t01165b695e6341bce5.png)
1. 普通用户权限
在server2012r2之后，如果没有以上两个权限。可以通过设置基于资源的约束委派。

在NTLM发起者属性msDS-AllowedToActOnBehalfOfOtherIdentity里面添加一条ace,可以让任何机器用户和服务用户可以控制该用户(NTLM发起者)。

[![](https://p1.ssl.qhimg.com/t013e49b57a8d1f7df9.png)](https://p1.ssl.qhimg.com/t013e49b57a8d1f7df9.png)



## 0x03 引用

[LM-Hash、NTLM-Hash、Net-NTLMv1、Net-NTLMv2详解](http://d1iv3.me/2018/12/08/LM-Hash%E3%80%81NTLM-Hash%E3%80%81Net-NTLMv1%E3%80%81Net-NTLMv2%E8%AF%A6%E8%A7%A3/)

[The NTLM Authentication Protocol and Security Support Provider](http://davenport.sourceforge.net/ntlm.html)
