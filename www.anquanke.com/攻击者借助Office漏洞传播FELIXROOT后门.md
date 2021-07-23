> 原文链接: https://www.anquanke.com//post/id/153243 


# 攻击者借助Office漏洞传播FELIXROOT后门


                                阅读量   
                                **131066**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2018/07/microsoft-office-vulnerabilities-used-to-distribute-felixroot-backdoor.html](https://www.fireeye.com/blog/threat-research/2018/07/microsoft-office-vulnerabilities-used-to-distribute-felixroot-backdoor.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t011627b2c2800075f4.png)](https://p2.ssl.qhimg.com/t011627b2c2800075f4.png)

## 一、攻击活动细节

2017年9月，在针对乌克兰的攻击活动中FireEye发现了FELIXROOT后门这款恶意载荷，并将其反馈给我们的情报感知客户。该攻击活动使用了一些恶意的乌克兰银行文档，其中包含一个宏，用来下载FELIXROOT载荷并将其投递给攻击目标。

最近FireEye观察到有新的攻击活动中用到了同样的FELIXROOT后门。在这次攻击活动中，武器化的诱骗文档涉及到与环境保护研讨会相关的话题，利用了两个已知的Microsoft Office漏洞（[CVE-2017-0199](https://www.fireeye.com/blog/threat-research/2017/04/cve-2017-0199-hta-handler.html)以及[CVE-2017-11882](https://www.fireeye.com/blog/threat-research/2017/12/targeted-attack-in-middle-east-by-apt34.html)）来将后门程序释放到受害者主机上并加以执行，攻击活动流程图如图1所示。

[![](https://p3.ssl.qhimg.com/t01d7376c5d61000597.png)](https://p3.ssl.qhimg.com/t01d7376c5d61000597.png)

图1. 攻击流程图

恶意软件借助俄语文档（如图2所示）进行传播，文档用到了已知的Microsoft Office漏洞利用技术。在此次攻击活动中，我们观察到攻击者利用CVE-2017-0199以及CVE-2017-11882漏洞来传播恶意软件。所使用的恶意文档名为“Seminar.rtf”，文档利用CVE-2017-0199漏洞从`193.23.181.151`这个地址处（如图3所示）下载第二阶段所使用的攻击载荷，所下载的文档包含了CVE-2017-11882漏洞利用技术。

[![](https://p0.ssl.qhimg.com/t0152550bcf7da8717c.png)](https://p0.ssl.qhimg.com/t0152550bcf7da8717c.png)

图2. 诱饵文档

[![](https://p5.ssl.qhimg.com/t012f84e774253f6993.png)](https://p5.ssl.qhimg.com/t012f84e774253f6993.png)

图3. Seminar.rtf文档中的URL信息（十六进制数据）

图4表明第一个载荷正尝试下载攻击第二阶段所使用的Seminar.rtf。

[![](https://p5.ssl.qhimg.com/t0166002c2ab3b7fb05.png)](https://p5.ssl.qhimg.com/t0166002c2ab3b7fb05.png)

图4. 下载第二阶段所使用的Seminar.rtf

下载的Seminar.rtf文档中包含一个二进制文件，通过公式编辑器将可执行文件释放到`%temp%`目录中。该文件将可执行文件释放到`%temp%`目录（MD5：78734CD268E5C9AB4184E1BBE21A6EB9），后者用来下载并执行FELIXROOT释放器组件（MD5：92F63B1227A6B37335495F9BCB939EA2）。

释放出来的可执行文件（MD5：78734CD268E5C9AB4184E1BBE21A6EB9）在PE（Portable Executable）覆盖区中包含经过压缩处理的FELIXROOT释放器组件。当该文件被执行时会创建两个文件：指向`%system32%\rundll32.exe`路径的一个LNK文件以及FELIXROOT加载器组件。LNK文件会被移动到启动目录中。LNK文件中包含用来执行FELIXROOT加载器组件的命令，如图5所示：

[![](https://p2.ssl.qhimg.com/t0130aaaf87518553be.png)](https://p2.ssl.qhimg.com/t0130aaaf87518553be.png)

图5. LNK文件中包含的命令

内置的后门组件使用了自定义加密算法进行加密。该文件会直接在内存中解密并执行，不涉及到落盘操作。



## 二、技术细节

成功利用漏洞后，释放器组件会执行并释放加载器组件。加载器组件借助`RUNDLL32.EXE`来执行。后门组件会被加载到内存中，只包含一个导出函数。

后门中包含的字符串经过自定义的加密算法进行加密处理，加密算法为XOR（异或）算法，采用了4字节的密钥。ASCII字符串对应的解密逻辑如图6所示。

[![](https://p0.ssl.qhimg.com/t0158741f0160c33d74.png)](https://p0.ssl.qhimg.com/t0158741f0160c33d74.png)

图6. ASCII解密过程

Unicode字符串的解密逻辑如图7所示。

[![](https://p5.ssl.qhimg.com/t018e14b1c5aed88c82.png)](https://p5.ssl.qhimg.com/t018e14b1c5aed88c82.png)

图7. Unicode解密过程

执行起来后，后门会创建一个新的线程，然后休眠10分钟，接着确认自身是否由`RUNDLL32.EXE`使用`#1`参数启动，如果条件满足，则后门会在执行命令与控制（C2）网络通信操作之前先进行初始的系统信息收集。为了收集系统信息，后门通过`ROOTCIMV2`命名空间连接到Windows Management Instrumentation（WMI）。

整个操作过程如图8所示：

[![](https://p5.ssl.qhimg.com/t011f2b21accf7e3c17.png)](https://p5.ssl.qhimg.com/t011f2b21accf7e3c17.png)

图8. 后门组件初始执行流程

从`ROOTCIMV2`及`RootSecurityCenter2`命名空间中引用的类如表1所示：

|**WMI命名空间**
|------
|Win32_OperatingSystem
|Win32_ComputerSystem
|AntiSpywareProduct
|AntiVirusProduct
|FirewallProduct
|Win32_UserAccount
|Win32_NetworkAdapter
|Win32_Process

表1. 引用的类

### <a class="reference-link" name="WMI%E5%8F%8A%E6%B3%A8%E5%86%8C%E8%A1%A8"></a>WMI及注册表

用到的WMI查询语句如下所示：

```
SELECT Caption FROM Win32_TimeZone
SELECT CSNAME, Caption, CSDVersion, Locale, RegisteredUser FROM Win32_OperatingSystem
SELECT Manufacturer, Model, SystemType, DomainRole, Domain, UserName FROM Win32_ComputerSystem
```

后门会读取注册表相关键值信息，收集管理员权限提升信息及代理信息。

1、查询`SOFTWAREMicrosoftWindowsCurrentVersionPoliciesSystem`路径中的`ConsentPromptBehaviorAdmin`及`PromptOnSecureDesktop`表项值；

2、查询`SoftwareMicrosoftWindowsCurrentVersionInternet Settings`路径中的`ProxyEnable`、`Proxy:(NO)`、`Proxy`及`ProxyServer`表项值。

FELIXROOT后门的功能如表2所示。每条命令都会在独立的线程中执行。

|**命令**|**描述**
|------
|0x31|通过WMI及注册表收集系统指纹信息
|0x32|释放文件并加以执行
|0x33|远程Shell
|0x34|终止与C2服务器的连接
|0x35|下载并运行批处理脚本
|0x36|下载文件到本地
|0x37|上传文件

表2. FELIXROOT后门命令

使用图6及图7的解密方法后，我们从内存中提取出了每条命令执行后的日志信息，如图9所示。

[![](https://p2.ssl.qhimg.com/t01f6d2d56319c17e71.png)](https://p2.ssl.qhimg.com/t01f6d2d56319c17e71.png)

图9. 命令执行后的日志

### <a class="reference-link" name="%E7%BD%91%E7%BB%9C%E9%80%9A%E4%BF%A1"></a>网络通信

FELIXROOT会通过HTTP与HTTPS POST协议与C2服务器通信。通过网络发送的数据经过加密处理，采用自定义的数据结构。所有的数据都经过AES加密，转换为Base64数据然后再发送给C2服务器（如图10所示）。

[![](https://p0.ssl.qhimg.com/t015c11d242a1a4b49a.png)](https://p0.ssl.qhimg.com/t015c11d242a1a4b49a.png)

图10. 发送给C2服务器的POST请求

Request及Response数据包头部中的其他所有字段（如`User-Agents`、`Content-Type`及`Accept-Encoding`）都经过XOR加密处理，可以在恶意软件中找到。恶意软件调用Windows API获取计算机名、用户名、卷序列号、Windows版本、处理器架构以及其他两个值（分别为“1.3”以及“KdfrJKN”）。“KdfrJKN”这个值可能是个标识符，可以在文件内部的JSON对象中找到（如图11所示）。

[![](https://p2.ssl.qhimg.com/t01a68ef8cd0865dbde.png)](https://p2.ssl.qhimg.com/t01a68ef8cd0865dbde.png)

图11. 每次通信中所使用的主机信息

FELIXROOT后门在C2通信中用到了3个参数，每个参数都可以提供关于目标主机的一些信息（如表3所示）。

|**参数**|**描述**
|------
|‘u=’|该参数包含目标主机信息，具体格式为：`&lt;Computer Name&gt;, &lt;User Name&gt;, &lt;Windows Versions&gt;, &lt;Processor Architecture&gt;, &lt;1.3&gt;, &lt; KdfrJKN &gt;, &lt;Volume Serial Number&gt;`
|‘&amp;h=’|该参数包含执行的命令及具体结果
|‘&amp;p=’|该参数包含与C2服务器有关的数据信息

表3. FELIXROOT后门参数

### <a class="reference-link" name="%E5%8A%A0%E5%AF%86%E7%AE%97%E6%B3%95"></a>加密算法

发送给C2服务器的所有数据都经过AES加密处理，通过`IbindCtx`接口使用HTTP或者HTTPS协议进行传输。每次通信所使用的AES密钥都不相同，该密钥经过两个RSA公钥的加密处理。FELIXROOT所使用的RSA密钥如图12及图13所示，AES加密参数如图14所示。

[![](https://p4.ssl.qhimg.com/t01e98246113c34dc54.png)](https://p4.ssl.qhimg.com/t01e98246113c34dc54.png)

图12. RSA公钥1

[![](https://p1.ssl.qhimg.com/t012f709864257131db.png)](https://p1.ssl.qhimg.com/t012f709864257131db.png)

图13. RSA公钥2

[![](https://p1.ssl.qhimg.com/t01b88f8f49057556da.png)](https://p1.ssl.qhimg.com/t01b88f8f49057556da.png)

图14. AES加密参数

加密处理后，发往C2的密文还会经过Base64编码。发送给服务器的数据结构体如图15所示，C2通信中对应的数据结构如图16所示。

[![](https://p0.ssl.qhimg.com/t01c7aa9096e59cc465.png)](https://p0.ssl.qhimg.com/t01c7aa9096e59cc465.png)

图15. 用来将数据发送至服务器的结构体

[![](https://p3.ssl.qhimg.com/t0128e190647e20dd1b.png)](https://p3.ssl.qhimg.com/t0128e190647e20dd1b.png)

图16. 发往C2服务器数据结构样例

后门使用`CryptBinaryToStringA`函数将该结构体数据转换为Base64编码。

FELIXROOT后门包含若干条命令，用于不同的任务。每项任务执行完毕后，恶意软件会在执行下一项任务前睡眠1分钟。一旦所有任务执行完毕，恶意软件会跳出循环，删除数据缓冲区，然后清除目标主机上的所有痕迹，包含如下清痕操作：

1、从启动目录中删除LNK文件；

2、删除`HKCUSoftwareClassesApplicationsrundll32.exeshellopen`注册表项；

3、从系统中删除释放器组件。



## 三、总结

CVE-2017-0199以及CVE-2017-11882是目前我们最常见到的两个漏洞。攻击者通常会越来越广泛地利用这些漏洞发动攻击，直至漏洞再无可用之处为止，因此各个单位必须确保他们处于足够的防护中。在本文成文时，FireEye Multi Vector Execution（MVX）引擎已经能正确识别并阻止此类安全威胁。我们建议所有行业保持警惕，因为此次攻击活动的肇事者很有可能会扩大他们的攻击范围。



## 四、附件

### IOC

|MD5哈希值|样本
|------
|11227ECA89CC053FB189FAC3EBF27497|Seminar.rtf
|4DE5ADB865B5198B4F2593AD436FCEFF|Seminar.rtf
|78734CD268E5C9AB4184E1BBE21A6EB9|Zam&lt;随机数&gt;.doc
|92F63B1227A6B37335495F9BCB939EA2|FELIXROOT Dropper
|DE10A32129650849CEAF4009E660F72F|FELIXROOT Backdoor

表4. FELIXROOT IOC

### 网络IOC

```
217.12.104.100/news
217.12.204.100:443/news
193.23.181.151/Seminar.rtf
Accept-Encoding: gzip, deflate
content-Type: application/x-www-form-urlencoded
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.2)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.2)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.2)
Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.2)
```

### 配置文件

版本1：

```
`{`"1" : "https://88.198.13.116:8443/xmlservice","2" : "30","4" : "GufseGHbc","6" : "3", "7" : “http://88.198.13.116:8080/xmlservice"`}`

```

版本2：

```
`{`"1" : "https://217.12.204.100/news/","2" : "30","4" : "KdfrJKN","6" : "3", "7" : "http://217.12.204.100/news/"`}`
```

### FireEye检测结果

|MD5|产品|特征|操作
|------
|11227ECA89CC053FB189FAC3EBF27497|NX/EX/AX|Malware.Binary.rtf|阻止
|4DE5ADB865B5198B4F2593AD436FCEFF|NX/EX/AX|Malware.Binary.rtf|阻止
|78734CD268E5C9AB4184E1BBE21A6EB9|NX/EX/AX|Malware.Binary|阻止
|92F63B1227A6B37335495F9BCB939EA2|NX/EX/AX|FE_Dropper_Win32_FELIXROOT_1|阻止
|DE10A32129650849CEAF4009E660F72F|NX/EX/AX|FE_Backdoor_Win32_FELIXROOT_2|组织
|11227ECA89CC053FB189FAC3EBF27497|HX|IOC|警告
|4DE5ADB865B5198B4F2593AD436FCEFF|HX|IOC|警告

表5. FireEye检测结果
