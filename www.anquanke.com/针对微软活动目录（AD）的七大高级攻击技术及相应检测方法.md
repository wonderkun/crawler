> 原文链接: https://www.anquanke.com//post/id/161815 


# 针对微软活动目录（AD）的七大高级攻击技术及相应检测方法


                                阅读量   
                                **532941**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Positive Technologies，文章来源：blog.ptsecurity.com
                                <br>原文地址：[http://blog.ptsecurity.com/2018/10/advanced-attacks-on-microsoft-active.html](http://blog.ptsecurity.com/2018/10/advanced-attacks-on-microsoft-active.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0126a3482da24605e5.png)](https://p4.ssl.qhimg.com/t0126a3482da24605e5.png)



## 一、概述

在过去的4年中，对微软活动目录（Microsoft Active Directory）的攻击一直都是Black Hat和Defcon会议关注的一大重点。演讲者们不断讲解新的攻击角度，分享他们的发现，同时也提出检测方法和防御方案。根据这些已有的信息，我认为IT部门已经完全可以构建一个安全的基础架构，并且该架构可以由安全部门来进行监控。但是，如果想要进行高质量的监控，那么还需要有良好的工具。这其实就像是一个军事基地：只在其周围建起守卫塔还不够，还需要派一些战士在守卫塔上面持续监控。



## 二、六个不容忽视的攻击方式

### <a class="reference-link" name="2.1%20%E5%93%88%E5%B8%8C%E5%80%BC%E4%BC%A0%E9%80%92"></a>2.1 哈希值传递

这种攻击方法受到NTLM架构的限制，NTLM是微软在20世纪90年代发布的一种身份验证协议。要登陆到远程主机，需要存储在计算机上的密码哈希值，用于身份验证过程。该哈希值可以从计算机上提取出来。

### <a class="reference-link" name="2.2%20Mimikatz"></a>2.2 Mimikatz

为了实现这一目的，法国的研究者Benjamin Delpy在2014年开发了Mimikatz，该实用程序允许从计算机内存中转储明文密码和NTLM哈希值。

### <a class="reference-link" name="2.3%20%E6%9A%B4%E5%8A%9B%E7%A0%B4%E8%A7%A3"></a>2.3 暴力破解

如果无法实现从主机提取凭据，那么攻击者也可以选择粗暴但是有效的密码猜测技术。

### <a class="reference-link" name="2.4%20net%20user/domain"></a>2.4 net user/domain

在进行攻击之前，攻击者实际上需要一个用户名字典。当任何域成员执行net user /domain命令之后，该命令就会返回AD域用户的完整列表。

### <a class="reference-link" name="2.5%20Kerberoasting%E6%94%BB%E5%87%BB"></a>2.5 Kerberoasting攻击

如果域使用了Kerberos作为身份验证协议，那么攻击者就可以尝试进行Kerberoasting攻击。在域上进行身份验证的任何用户，都可以请求Kerberos Ticket，用于访问服务（票证授予服务Ticket Granting Service）。TGS使用运行服务用户的密码哈希值进行加密。攻击者在请求TGS后，就可以对TGS进行离线的暴力破解，这一暴破过程不会受到任何阻止。如果成功，攻击者将获得运行服务账户的密码，而这一账户通常为特权账户。

### <a class="reference-link" name="2.6%20PSEXEC"></a>2.6 PSEXEC

在攻击者获得所需凭据之后，下一步就是要远程命令执行。使用Sysinternals中的PsExec实用程序可以轻松实现，这个实用程序非常有效，受到广大IT管理员和广大黑客的青睐。



## 三、盘点七大高级攻击技术

现在，我们将盘点7种能够实现Active Direction完全控制的黑客攻击方法。下图展现了攻击的四个步骤，而其中的每一步都对应着一套方法。

[![](https://4.bp.blogspot.com/-wyGTFZX6R8Q/W79M6b9s4iI/AAAAAAAAHWE/-SKihX7jN0AiK0bLy3GqqejudR7DDy1UQCLcBGAs/s640/bqlwufggd4wwixlwo6dsb5w66by.png)](https://4.bp.blogspot.com/-wyGTFZX6R8Q/W79M6b9s4iI/AAAAAAAAHWE/-SKihX7jN0AiK0bLy3GqqejudR7DDy1UQCLcBGAs/s640/bqlwufggd4wwixlwo6dsb5w66by.png)

让我们首先从侦查（Reconnaissance）开始。

### <a class="reference-link" name="3.1%20PowerView"></a>3.1 PowerView

PowerView是PowerSploit中的一部分，PowerSploit是一个用于渗透测试的PowerShell框架。PowerView支持Bloodhound，这是一种在AD中能对连接对象进行图形展现的工具。

[![](https://1.bp.blogspot.com/-AA3JIhXys5o/W79ZeaFeCtI/AAAAAAAAHY0/l7aPk1XY6NQawueUfmR-kKshIbV-TR4hgCLcBGAs/s640/mad1.png)](https://1.bp.blogspot.com/-AA3JIhXys5o/W79ZeaFeCtI/AAAAAAAAHY0/l7aPk1XY6NQawueUfmR-kKshIbV-TR4hgCLcBGAs/s640/mad1.png)

使用Bloodhound，可以实现以下内容：

1、查找所有域管理员账户；

2、查找登录到主机的域管理员；

3、使用域管理会话，查找从攻击者主机到目标主机的最短路径。

上面的第三条也说明，黑客需要对主机进行攻击，才能进入域管理员账户。这种方法显著减少了攻击者对域获得完全控制所需要的时间。

PowerView与允许在AD对象（例如net.exe）上获取数据的内置使用程序之间存在区别，其区别在于PowerView使用的是LDAP，而不是SAMR。要检测这一活动，我们可以借助域控制器事件1644。通过在注册表中添加相关值，可以启动该事件的记录：

```
HKEY_LOCAL_MACHINESYSTEMCurrentControlSetServicesNTDSDiagnostic\15 Field Engineering = 5
```

[![](https://3.bp.blogspot.com/-HO0C98Wf5sY/W79Z92LkNcI/AAAAAAAAHZM/ahdgkn8t6tsWFDpbrMrOTSZpP_s1TXoGgCLcBGAs/s400/ad1.png)](https://3.bp.blogspot.com/-HO0C98Wf5sY/W79Z92LkNcI/AAAAAAAAHZM/ahdgkn8t6tsWFDpbrMrOTSZpP_s1TXoGgCLcBGAs/s400/ad1.png)

[![](https://1.bp.blogspot.com/-3enF-kQMhQM/W79aJZDJzMI/AAAAAAAAHZQ/TqCjRioXrzgvjPVvyKQWxV_xgYq57MMkACLcBGAs/s400/ad2.png)](https://1.bp.blogspot.com/-3enF-kQMhQM/W79aJZDJzMI/AAAAAAAAHZQ/TqCjRioXrzgvjPVvyKQWxV_xgYq57MMkACLcBGAs/s400/ad2.png)

请注意，可能存在多种此类事件。同时，还有另外的一种方法，就是分析流量。由于LDAP是一种明文协议，因此所有查询都在流量中有所体现。

[![](https://1.bp.blogspot.com/-bdmUgfc-D30/W79aZBN2PeI/AAAAAAAAHZY/XLzJFEuCSGgMGW_QmlK8rDJA58GRNOf8QCLcBGAs/s640/ad3.png)](https://1.bp.blogspot.com/-bdmUgfc-D30/W79aZBN2PeI/AAAAAAAAHZY/XLzJFEuCSGgMGW_QmlK8rDJA58GRNOf8QCLcBGAs/s640/ad3.png)

该框架的另一个特性，是它仅使用PowerShell，并且不具有依赖关系。此外，PowerShell v5版本包含了一个高级审计选项，在实际检测工作中非常有用。事件4104中包含脚本内容，可以在其中搜索特定于PowerView的函数名称。

[![](https://1.bp.blogspot.com/-MAw0oipfGNg/W79apu0JzzI/AAAAAAAAHZk/xJJL3OwAShgQvqcJw31ojJ0t93KoQavogCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.13.42.png)](https://1.bp.blogspot.com/-MAw0oipfGNg/W79apu0JzzI/AAAAAAAAHZk/xJJL3OwAShgQvqcJw31ojJ0t93KoQavogCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.13.42.png)

### <a class="reference-link" name="3.2%20SPN%E6%89%AB%E6%8F%8F"></a>3.2 SPN扫描

这个实用程序可以替代Nmap。在攻击者知道AD中存在哪些用户和哪些组之后，他还需要有关服务的信息，这样才能对攻击目标具有一个全面的了解。

[![](https://4.bp.blogspot.com/-vGd943I2ERw/W79a4zH1VwI/AAAAAAAAHZo/D7Z-o8S4XqYxUztTuDRi21_RdRpmgN9owCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.14.43.png)](https://4.bp.blogspot.com/-vGd943I2ERw/W79a4zH1VwI/AAAAAAAAHZo/D7Z-o8S4XqYxUztTuDRi21_RdRpmgN9owCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.14.43.png)

通常，使用Nmap扫描端口可以得到这样的信息。但由于这些信息已经存储在AD中，所以攻击者直接从AD检索即可。查询结果如下所示：会返回包含服务类的服务主体名称SPN（该服务类针对每种服务类型是唯一的）、FQDN格式的主机名称和某些服务的端口。

[![](https://2.bp.blogspot.com/-bAGI7NJsc6Y/W79OG9_4biI/AAAAAAAAHW8/0Waa451bNjkCFqlPK8-ATCwEhlqwf_aOwCLcBGAs/s640/5bz8otu_w7hroldiqy0wscyut-g.png)](https://2.bp.blogspot.com/-bAGI7NJsc6Y/W79OG9_4biI/AAAAAAAAHW8/0Waa451bNjkCFqlPK8-ATCwEhlqwf_aOwCLcBGAs/s640/5bz8otu_w7hroldiqy0wscyut-g.png)

有关SPN的完整列表，请参阅 [https://adsecurity.org/?page_id=183](https://adsecurity.org/?page_id=183) 。

要检测SPN扫描，可以使用LDAP事件审核。

SPN扫描具有明显优于Nmap的优点，也就是准确度较高。使用Nmap时，需要连接到每个主机，并且将数据包发送到指定范围的端口，而SPN列表只是一个查询的结果。

### <a class="reference-link" name="3.3%20%E8%BF%9C%E7%A8%8B%E4%BC%9A%E8%AF%9D%E6%9E%9A%E4%B8%BE"></a>3.3 远程会话枚举

在横向移动阶段，有一个重要的任务，就是将用户与他们所登陆的计算机相匹配。攻击者这个时候已经拥有了用户凭据（哈希值或Kerberos Ticket），同时已经搜索到受漏洞影响的主机或具有域管理员会话的主机。

在这两种情况下，攻击者的后续动作都会是：寻找可攻击目标 —&gt; 对任意主机成功攻击 —&gt; 上传Mimikatz —&gt; 获得所需信息。

要检测此方案是否被使用，可以查询这两个事件：4624-成功登陆到远程系统（登录类型3）和命名管道为“srvsvc”的访问网络共享IPC$事件。

[![](https://2.bp.blogspot.com/-SaLEwklUSvc/W79bHgsXMYI/AAAAAAAAHZw/mybMQwXNs4ENM2HsuHLFo-1dHLPazprCwCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.15.41.png)](https://2.bp.blogspot.com/-SaLEwklUSvc/W79bHgsXMYI/AAAAAAAAHZw/mybMQwXNs4ENM2HsuHLFo-1dHLPazprCwCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.15.41.png)

在左图中的红色标出部分，展示了SMB连接，随后连接到管道“srcsvc”。该管道允许通过服务器服务远程协议进行交互。终端主机从管道接收各种管理信息，例如，可以是NetSessEnum的请求。这一请求会返回使用其IP地址和名称登录到远程系统的完整用户列表。

[![](https://3.bp.blogspot.com/-AXOVYjz1EgA/W79bP6LgpWI/AAAAAAAAHZ4/t20Eg6OosPYD8GFg4P642nfKSuKG5uoKACLcBGAs/s1600/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.16.14.png)](https://3.bp.blogspot.com/-AXOVYjz1EgA/W79bP6LgpWI/AAAAAAAAHZ4/t20Eg6OosPYD8GFg4P642nfKSuKG5uoKACLcBGAs/s1600/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.16.14.png)

通过MaxPatrol SIEM可以实现基于这两个事件与srvsvc相关性进行的检测。PT Network Attack Discovery可以基于流量分析进行类似的检测。

### <a class="reference-link" name="3.4%20Overpass-the-Hash"></a>3.4 Overpass-the-Hash

#### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%96%B9%E5%BC%8F"></a>攻击方式

Overpass-the-Hash实际上是Pass-the-Hash的升级版本。攻击者可以使用获得的NTLM哈希值进行Pass-the-Hash攻击。但由于这种攻击方式已经被大家知晓，并且容易被发现。所以产生了一种新的攻击向量——Overpass-the-Hash。

Kerberos协议专门用于防止用户密码通过任何方式在网络上发送。为避免这种情况，用户会在自己的计算机上使用密码哈希值来加密认证请求。密钥分发中心（Key Distribution Center，在域控制器上运行的特殊服务）会回复一个Ticket，以获取其他Ticket，因此这一过程也被称为票据授予票据（TGT，Ticket-Granting Ticket）。在完成这一过程之后，客户端的身份验证通过，并且在之后的10小时内都可以请求访问其他服务的Ticket。因此，如果攻击者对处于目标服务（例如ERP系统或数据库）的可信组中的用户的哈希值进行转储，那么攻击者就可以自行发出Ticket，并成功登录到目标服务。

[![](https://2.bp.blogspot.com/-IvRpCGrtBOA/W79b_2ZeWwI/AAAAAAAAHaM/B2q_E9k32WghmafF9fH111-lKjToxFPowCLcBGAs/s400/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.19.20.png)](https://2.bp.blogspot.com/-IvRpCGrtBOA/W79b_2ZeWwI/AAAAAAAAHaM/B2q_E9k32WghmafF9fH111-lKjToxFPowCLcBGAs/s400/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.19.20.png)

#### <a class="reference-link" name="%E6%A3%80%E6%B5%8B%E6%96%B9%E6%B3%95"></a>检测方法

如果黑客使用PowerShell版本的Mimikatz进行攻击，那么日志中的脚本信息将会有所帮助，因为Invoke-Mimikatz的特征非常明显。

[![](https://2.bp.blogspot.com/-O70D-5_-Q9s/W79bbXgG2zI/AAAAAAAAHZ8/njmteFTciAMK6YJiBK3FW0yz9UwGaoKZgCLcBGAs/s400/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.17.06.png)](https://2.bp.blogspot.com/-O70D-5_-Q9s/W79bbXgG2zI/AAAAAAAAHZ8/njmteFTciAMK6YJiBK3FW0yz9UwGaoKZgCLcBGAs/s400/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.17.06.png)

另一个检测手段，就是通过事件4688-创建一个对命令行进行扩展审计的进程。即使攻击者对二进制文件进行重命名，在命令行中也会包含命令，这对于Mimikatz来说非常有效。

[![](https://2.bp.blogspot.com/-H6d_DoLOhl4/W79bwVXbY7I/AAAAAAAAHaE/NrjA4gI7gf8jsnQW9i24Zy9IwIJ8DcY9QCLcBGAs/s400/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.18.26.png)](https://2.bp.blogspot.com/-H6d_DoLOhl4/W79bwVXbY7I/AAAAAAAAHaE/NrjA4gI7gf8jsnQW9i24Zy9IwIJ8DcY9QCLcBGAs/s400/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.18.26.png)

如果要通过分析流量来检测Overpass-the-Hash攻击，可以使用以下线索：Microsoft建议在现代的域中使用AES256加密方法对身份验证请求进行加密，而Mimikatz发送的身份验证请求数据都是采用过时的加密方式ARCFOUR对数据进行加密的。

[![](https://4.bp.blogspot.com/-yJy-wrSkkG4/W79b2TvIswI/AAAAAAAAHaI/YLnQMdVDM9MIcUOQv-sfhu67O8OFsLAbgCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.18.53.png)](https://4.bp.blogspot.com/-yJy-wrSkkG4/W79b2TvIswI/AAAAAAAAHaI/YLnQMdVDM9MIcUOQv-sfhu67O8OFsLAbgCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.18.53.png)

另外的一个特征是，Mimikatz发出的密钥算法套件（Cipher Suite）与合法域的套件不同，可以将此作为流量中的分析依据。

### <a class="reference-link" name="3.5%20%E9%BB%84%E9%87%91%E7%A5%A8%E6%8D%AE"></a>3.5 黄金票据

#### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%96%B9%E5%BC%8F"></a>攻击方式

黄金票据（Golden Ticket）是一个流行的攻击方法。

攻击者可以从名为krbtgt的特殊账户中获取密码的哈希值。回顾用户密码哈希值用于签署所有TGT的过程，我们发现在这一过程中，无需向密钥分发中心进行寻址。由于Golden Ticket实际上就是一个TGT，因此攻击者可以生成这一Ticket。随后，攻击者可以向AD中的任何服务无限次发送身份验证请求，最终能够不受限制地访问目标资源。这也就是“黄金票据”这一名称的由来。

[![](https://3.bp.blogspot.com/-lhBLuQT9gJQ/W79cIkvLvWI/AAAAAAAAHaU/1kPNrN_TNgUGmMS5mIE70jwJJUFxG58mACLcBGAs/s1600/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.20.08.png)](https://3.bp.blogspot.com/-lhBLuQT9gJQ/W79cIkvLvWI/AAAAAAAAHaU/1kPNrN_TNgUGmMS5mIE70jwJJUFxG58mACLcBGAs/s1600/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.20.08.png)

#### <a class="reference-link" name="%E6%A3%80%E6%B5%8B%E6%96%B9%E6%B3%95"></a>检测方法

事件4768是“TGT授予”，事件4769是“已授予AD中某些服务进行身份验证所需的服务Ticket”。

[![](https://1.bp.blogspot.com/-CyeOFNASFnc/W79cQkc7PII/AAAAAAAAHac/1w8M3Df7kLk_wKOrzTcpTsXsrOIQ_gcVQCLcBGAs/s1600/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.20.34.png)](https://1.bp.blogspot.com/-CyeOFNASFnc/W79cQkc7PII/AAAAAAAAHac/1w8M3Df7kLk_wKOrzTcpTsXsrOIQ_gcVQCLcBGAs/s1600/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.20.34.png)

在这种情况下，我们可以推测出正常行为与攻击行为之间的差异。尽管Golden Ticket不从域控制器中请求TGT（因为它自身就生成TGT），但是它必须要请求TGS。因此，如果我们发现获得的TGT和TGS有所不同，那么就能判断出正在受到Golden Ticket攻击。

MaxPatrol SIEM使用列表，记录所有已经发出的TGT和TGS，从而实现对该攻击方法的检测。

### <a class="reference-link" name="3.6%20WMI%E8%BF%9C%E7%A8%8B%E6%89%A7%E8%A1%8C"></a>3.6 WMI远程执行

#### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%96%B9%E5%BC%8F"></a>攻击方式

攻击者在目标主机进行身份验证和获得授权后，就可以远程执行任务。WMI是一个系统中的内置机制，非常适合这种场景。在过去的几年中，WMI被攻击者普遍使用，其原因就在于WMI具有模仿合法活动的能力。

下图演示了系统内置实用程序wmic的使用过程。攻击者向该实用程序提供要连接的主机地址、凭据、进程调用Create Operator以及要在远程主机上执行的命令。

[![](https://1.bp.blogspot.com/-Gwc7NSoX-GU/W79cXikQvVI/AAAAAAAAHag/3NyJbvAhy0EWnCamcdRuPZsDjgjgX9MrgCLcBGAs/s640/ad6.png)](https://1.bp.blogspot.com/-Gwc7NSoX-GU/W79cXikQvVI/AAAAAAAAHag/3NyJbvAhy0EWnCamcdRuPZsDjgjgX9MrgCLcBGAs/s640/ad6.png)

#### <a class="reference-link" name="%E6%A3%80%E6%B5%8B%E6%96%B9%E6%B3%95"></a>检测方法

通过检查远程登录事件4624，可以有效发现这类攻击。其中，一个重要的参数是登录ID。此外，还需要关注事件4688，该事件是“命令行创建进程”。在示例中，事件4688显示，创建的进程其父进程是WmiPrvSE.exe，这是一个用于远程管理的特殊WMI服务进程。我们可以看到发送的命令net user / add以及Logon ID，它与事件4624中的记载相同。由此，我们就可以准确地判断出该命令是从哪个主机下发的。

[![](https://2.bp.blogspot.com/-YgYk9HgQrKc/W79cdrm0j_I/AAAAAAAAHao/C_kCwfKCvZ8rW8F2RQfTjwRQaQ1-0uFawCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.21.30.png)](https://2.bp.blogspot.com/-YgYk9HgQrKc/W79cdrm0j_I/AAAAAAAAHao/C_kCwfKCvZ8rW8F2RQfTjwRQaQ1-0uFawCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.21.30.png)

同样，也有基于流量分析的检测方法，我们以实际样本为例。

我们可以清楚地看到Win32进程创建的关键词，以及它将要执行的命令行。下图所示的恶意软件与WannaCry以相同的方式分布在虚拟网络上，但后者并不是进行加密，而是执行了挖矿。恶意软件使用Mimikatz和EthernalBlue漏洞，对账户进行转储，并使用其登录到网络上可以访问的主机。通过WMI，恶意软件在这些主机上运行PowerShell，并且下载了PowerShell Payload，其中包含Mimikatz、EthernalBlue和挖矿程序。

[![](https://1.bp.blogspot.com/-q49n-NGgv5M/W79co4j8lzI/AAAAAAAAHa4/E39AMnpcuZ8cM61qNNBt5TvKeFMA-Do4wCLcBGAs/s640/ad7.png)](https://1.bp.blogspot.com/-q49n-NGgv5M/W79co4j8lzI/AAAAAAAAHa4/E39AMnpcuZ8cM61qNNBt5TvKeFMA-Do4wCLcBGAs/s640/ad7.png)

#### <a class="reference-link" name="%E5%AE%89%E5%85%A8%E5%BB%BA%E8%AE%AE"></a>安全建议

1、针对服务的账户，设置复杂的长密码（建议25位以上），这样攻击者就无法进行Kerberoasting攻击，因为理论上无法暴力破解此类密码。

2、启用PowerShell日志记录，有助于发现各类用于攻击AD的现代化工具。

3、将操作系统升级到Windows 10和Windows Server 2016。Microsoft在新版本操作系统中增加了名为Credential Guard的安全机制，可以有效防止对NTLM哈希值和Kerberos Ticket的转储。

4、实施基于角色的访问控制。如果将AD、DC、服务器和工作站管理员的权限都分配给同一个角色，无疑是有风险的。

5、每年进行两次AD管理员更换，在更换的同时重置krbtgt（用于签署TGT的账户）密码两次。其中，更改密码两次非常重要，因为系统会同时存储当前密码和先前密码。假设网络受到攻击，并且攻击者已经得到了Golden Ticket，更改密码会使攻击者的Ticket无效，必须要再次暴力破解密码。

6、使用及时更新数据库的安全防护工具，有助于发现当前正在进行的攻击行为。

### <a class="reference-link" name="3.7%20DCShadow"></a>3.7 DCShadow

#### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E6%96%B9%E5%BC%8F"></a>攻击方式

2018年1月24日，Benjamin Delpy和Vincent Le Toux在以色列的Microsoft BlueHat上发布了一个新的Mimikatz模块，用于实施DCShadow攻击。其攻击思路是，创建一个恶意域控制器，来复制AD域中的对象。研究人员定义了要进行成功复制所需要的最小Kerbero SPN集——只需要两个SPN。此外，他们还展示了一个特殊功能，可以进行强制复制。研究人员声称这种攻击方式无法被SIEM发现，一个伪造的域控制器不会向SIEM发送事件。这样一来，攻击者就可以在不为人知的情况下，使用AD和SIEM进行各种后续攻击操作。

攻击方案如下：

[![](https://2.bp.blogspot.com/-2ODGIeiVJ7M/W79dLGfB5kI/AAAAAAAAHbE/AU3H14nl58YwHK8LRKpBJgibOECBEBaNgCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.24.26.png)](https://2.bp.blogspot.com/-2ODGIeiVJ7M/W79dLGfB5kI/AAAAAAAAHbE/AU3H14nl58YwHK8LRKpBJgibOECBEBaNgCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.24.26.png)

这种方案，需要将两个SPN添加到发送攻击的系统中。其他域控制器需要这些SPN使用Kerberos进行身份验证以进行复制。由于规范中将域控制器表示为AD基类中的nTDSDSA类对象，因此应该创建这样的对象。最后，复制将由DRSReplicaAdd函数触发。

#### <a class="reference-link" name="%E6%A3%80%E6%B5%8B%E6%96%B9%E6%B3%95"></a>检测方法

下图是DCShadow在流量中的示例。通过对流量进行分析，我们可以清楚看到将新对象添加到域控制器方案，然后触发复制的过程。

[![](https://2.bp.blogspot.com/-7DvdAUggjLw/W79dXKJAF3I/AAAAAAAAHbI/MNqmFQNeCq4RiSOAce8pShvwZEeSBWvvgCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.25.18.png)](https://2.bp.blogspot.com/-7DvdAUggjLw/W79dXKJAF3I/AAAAAAAAHbI/MNqmFQNeCq4RiSOAce8pShvwZEeSBWvvgCLcBGAs/s640/%25D0%25A1%25D0%25BD%25D0%25B8%25D0%25BC%25D0%25BE%25D0%25BA%2B%25D1%258D%25D0%25BA%25D1%2580%25D0%25B0%25D0%25BD%25D0%25B0%2B2018-10-11%2B%25D0%25B2%2B17.25.18.png)

尽管发现该攻击方法的研究人员表示SIEM无法检测此类攻击，但我们还是找到了一种方法，能够发现网络上的可疑活动。

我们的关联中有一个合法的域控制器列表，它将在每次从域控制器进行复制时触发，而域控制器不在这个白名单之中。因此，安全人员可以进行调查，从而确认域控制器是由IT服务合法添加，还是遭受了DCShadow攻击后被添加。

DCShadow的攻击方式展现了一个新的攻击维度，也告诉我们，在信息安全的海洋中，防御者要时刻努力保持领先地位，展望未来，并能针对威胁迅速地采取行动。
