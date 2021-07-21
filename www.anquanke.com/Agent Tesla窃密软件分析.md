> 原文链接: https://www.anquanke.com//post/id/227736 


# Agent Tesla窃密软件分析


                                阅读量   
                                **192478**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0128a2cea52b1621c6.jpg)](https://p4.ssl.qhimg.com/t0128a2cea52b1621c6.jpg)



## 一. Agent Tesla 的前世今生

2014年，Agent Tesla 首次出现在一个土耳其语网站上，被作为一个键盘记录产品进行出售。虽然网站声称该产品仅向用户提供合法服务，但其所提供的绕过杀软、秘密捆绑程序和敏感文件传输等功能与窃密木马相比也不遑多让，甚至更为精密，因此人们更倾向于认为它是一种专门用来窃密的软件。后来，Agent Tesla 逐渐开始在地下论坛和黑客社区流行起来，售价一般从 15 美元到 69 美元不等，往往通过比特币等方式交易。

[![](https://p3.ssl.qhimg.com/t014ead347ceac88684.png)](https://p3.ssl.qhimg.com/t014ead347ceac88684.png)

如今，Agent Tesla 历经多次代码改进，功能不断增强，已经成为能够盗取浏览器、FTP、VPN、邮箱和 WIFI 等多种敏感信息的专业窃密软件。

在传播方式上，Agent Tesla 主要通过携带多种格式附件（如 ZIP、CAB、MSI、IMG 和 Office 文件等）的钓鱼邮件或垃圾邮件进行传播，并支持 smtp、ftp、http 等多种协议的数据回传；在分析对抗上，Agent Tesla 使用多种手段进行免杀、反调试和反虚拟机，大大增加了安全人员对其分析的难度；在用户使用层面，Agent Tesla 提供了易于配置的页面，使用者能够根据自身情况方便地选择所需要的木马功能，如多种方式实现持久化，UAC 设置，强行关闭杀毒软件进程等。

[![](https://p1.ssl.qhimg.com/t01c4dbceca8dff7e81.png)](https://p1.ssl.qhimg.com/t01c4dbceca8dff7e81.png)

在攻击目标行业选择上，Agent Tesla 的攻击波及互联网，教育，银行，电信，医药和制造业等，于 2020 年初扩展到对能源行业的攻击。

[![](https://p1.ssl.qhimg.com/t01229e5c8bff57fb2a.png)](https://p1.ssl.qhimg.com/t01229e5c8bff57fb2a.png)

时至今日，Agent Tesla 仍然活跃。如在 2020 年初，多个黑客组织被披露使用 Agent Tesla 以 COVID-19 为主题对政府和医疗组织进行网络钓鱼活动。其中德勤 CTI 观察到一次以“COVID-19”名义的网络钓鱼攻击。在钓鱼攻击中，黑客使用 Agent Tesla 木马针对位于日本和加拿大的医学研究机构开展 IP 信息窃取。经过德勤 CTI 研究员分析，在攻击过程中黑客会向攻击对象发送名为“COVID-19 供应商通告”或“疫情咨询” 等钓鱼邮件。这些钓鱼邮件中含有一份伪装为“COVID-19 供应商通告.zip”的木马文件，用户一旦点击该文件，Agent Tesla 木马程序会被自动加载到受害者的计算机上，从而窃取当前医疗研究成果。

又如在 2020 年中旬，Gorgon APT 针对印度 MSME 行业利用 Agent Tesla 进行窃密。研究人员观察到针对印度境内 MSME（小型、中小型企业）企业的网络钓鱼活动，恶意文档以 COVID-19 为主题。攻击过程为：受害者打开“ face mask order.doc”后，RTF 触发 CVE-2017-11882 漏洞执行任意代码；在 RTF 文件中包含两个恶意 ole 对象，第一个是可执行文件即 ServerCrypted.vbs 脚本；第二个为 Equation.3 exploit (CVE-2017-11882) 和运行 ServerCrypted.vbs 的脚本；成功利用后，脚本将会下载两个扩展名为 .jpg 的文件，其中一个为 PowerShell 脚本，会在内存中加载 DLL；第二个文件为 Agent Tesla 的有效负载。

2020 年下旬，Agent Tesla 攻击依旧倾向于印度地区，另外美国和巴西也是其主要针对的国家，攻击的目标行业除了之前的金融服务和一些公共单位之外，也包含互联网服务提供商（ISP），因为 ISP 持有可用于获取对其他帐户和服务访问权限的电子邮件或其他重要个人数据。这对于后续攻击具有重要意义。



## 二. 样本分析

如前文所述，Agent Tesla 的主要传播方式为钓鱼邮件——攻击者通常会采用社会工程学，针对其目标投递具有诱惑性的邮件、文档或者压缩包。在过去的几个月中，我们观察到大量攻击者以新冠疫情即“COVID-19”或“2019-nCov”为主题的邮件传播 Agent Tesla 木马。

[![](https://p4.ssl.qhimg.com/t0172f9b0fd7a18c0ff.png)](https://p4.ssl.qhimg.com/t0172f9b0fd7a18c0ff.png)

相关邮件一般包含恶意链接地址，或者其邮件附件为 Agent Tesla 的恶意载荷，诱骗受害者点击。部分样本还会通过宏文档或者带有漏洞的 office 文档进行下载执行。其中，常见的利用漏洞如 CVE-2017-11882、CVE-2017-8570 和 CVE-2017-0199 等，详情如下表所示：
<td data-row="1">**文档名称**</td><td data-row="1">**利用的漏洞**</td><td data-row="1">**漏洞说明**</td><td data-row="1">**危害**</td>
<td data-row="2">COVID 19 NEW ORDER FACE MASKS.doc.rtf</td><td data-row="2">CVE-2017-11882</td><td data-row="2">基于堆栈的缓冲区溢出漏洞</td><td data-row="2">漏洞允许攻击者运行任意代码以提供有效负载</td>
<td data-row="3">COVID-19 SUSPECTED AFFECTED VESSEL.doc COVID-19 measures for FAIRCHEM STEED Voyage (219152).doc</td><td data-row="3">CVE-2017-8570</td><td data-row="3">Microsoft Office的远程代码执行漏洞</td><td data-row="3">漏洞允许攻击者下载 .NET 有效负载</td>
<td data-row="4">RFQ REF NS326413122017.docx</td><td data-row="4">CVE-2017-0199</td><td data-row="4">利用OFFICE OLE对象链接技术</td><td data-row="4">Microsoft HTA 应用程序（mshta.exe）加载恶意攻击者下载并执行有效负载</td>

在此，我们对一个典型的 Agent Tesla 木马样本进行分析，发现其主要行为如下：

1. 首先利用远程模板注入的方式，远程下载一个包含 CVE-2017-11882 漏洞的 doc 文档。

[![](https://p5.ssl.qhimg.com/t01fb6e76b4dd9e7d01.png)](https://p5.ssl.qhimg.com/t01fb6e76b4dd9e7d01.png)

2. 文档运行后，将自动触发漏洞执行代码，并使用 API 函数 URLDownloadToFileW 从指定的 URL http://75.127.1.211/system/regasm.exe 下载攻击载荷，并保存到到 C:\Users\Public\regasm.exe 文件中。

[![](https://p5.ssl.qhimg.com/t0189fb5e0f0347df08.png)](https://p5.ssl.qhimg.com/t0189fb5e0f0347df08.png)

3. 打开文件后，发现诱饵文件内容为乱码。

[![](https://p4.ssl.qhimg.com/t0168c8009ccd0ecfd9.png)](https://p4.ssl.qhimg.com/t0168c8009ccd0ecfd9.png)

4. 攻击载荷将首先加载文件中的资源文件，表面上看是一张 png 格式的图片。

[![](https://p2.ssl.qhimg.com/t0140b2e7f8643ffcb0.png)](https://p2.ssl.qhimg.com/t0140b2e7f8643ffcb0.png)

[![](https://p5.ssl.qhimg.com/t01d5d567edab1f7434.png)](https://p5.ssl.qhimg.com/t01d5d567edab1f7434.png)

5. 深入分析发现，资源文件中存在待执行的隐藏代码，木马将会在解密后继续运行相关代码。

[![](https://p5.ssl.qhimg.com/t01668bfcbc5e0bfc0d.jpg)](https://p5.ssl.qhimg.com/t01668bfcbc5e0bfc0d.jpg)

6. 木马将根据设置，从3种方式中选择1种进行持久化，包括自启动目录、注册表和计划任务等。

[![](https://p5.ssl.qhimg.com/t01a29e0c993765f995.jpg)](https://p5.ssl.qhimg.com/t01a29e0c993765f995.jpg)

7. 之后，木马将继续从资源文件中读取内容，并通过解密释放出真正的 Agent Tesla 主体文件。

[![](https://p2.ssl.qhimg.com/t0115814d0163c8e2d1.jpg)](https://p2.ssl.qhimg.com/t0115814d0163c8e2d1.jpg)

解密函数如下：

[![](https://p1.ssl.qhimg.com/t01563bf938e251fe5a.jpg)](https://p1.ssl.qhimg.com/t01563bf938e251fe5a.jpg)

木马主体将通过定时器进行函数调用，如使用全局 Hook 的方式进行键盘记录：

[![](https://p5.ssl.qhimg.com/t01bc4451f7a853f674.png)](https://p5.ssl.qhimg.com/t01bc4451f7a853f674.png)

获取屏幕并截图：

[![](https://p5.ssl.qhimg.com/t0167bbabf9be957098.png)](https://p5.ssl.qhimg.com/t0167bbabf9be957098.png)

8. 木马可通过多种协议进行传输。

SMTP：

[![](https://p3.ssl.qhimg.com/t01c101b802a844971e.png)](https://p3.ssl.qhimg.com/t01c101b802a844971e.png)

HTTP：

[![](https://p1.ssl.qhimg.com/t019d9b87e5f601a3a9.png)](https://p1.ssl.qhimg.com/t019d9b87e5f601a3a9.png)

FTP：

[![](https://p4.ssl.qhimg.com/t0190241fb142c9304f.png)](https://p4.ssl.qhimg.com/t0190241fb142c9304f.png)

9. 通过 SMTP 相关代码中的内容，我们能够获取到受害者的邮件信息，分析发现大多数是蜜罐和分析人员的测试环境，当然也存在少部分真正的失陷主机。

[![](https://p4.ssl.qhimg.com/t013a81daa2c07feaa5.png)](https://p4.ssl.qhimg.com/t013a81daa2c07feaa5.png)

10. 我们结合其他样本分析结果，对会被 Agent Tesla 窃取信息的相关软件进行总结，详情如下表所示。
<td data-row="1">**软件类型**</td><td data-row="1">**软件名称**</td>
<td data-row="2">**浏览器客户端**</td><td data-row="2">360 Browser、Comodo Dragon、Coccoc、7Star、Kometa、Orbitum、Yandex Browser、Opera Browser、Sleipnir 6、Coowon、Brave、Sputnik、Chromium、Uran、QIP Surf、Cool Novo、Epic Privacy、Vivaldi、Torch Browser、Chedot、Liebao Browser、CentBrowser、Iridium Browser、Amigo、Elements Browser、Citrio、Google Chrome、Mozilla Firefox、 Microsoft IE、Apple、Safari、SeaMonkey、 ComodoDragon、FlockBrowser、SRWarelron、UC browser</td>
<td data-row="3">**邮件客户端**</td><td data-row="3">Microsoft Office、Outlook. Mozilla Thunderbird. Foxmail、Opera Mail、PocoMail、Eudora</td>
<td data-row="4">**FTP客户端**</td><td data-row="4">FileZill、WS FTP、WinSCP、CoreFTP、FlashFXP、SmartFTP、FTPCommander</td>
<td data-row="5">**动态DNS**</td><td data-row="5">DynDNS、No-IP</td>
<td data-row="6">**视频聊天**</td><td data-row="6">Paltalk、Pidgin</td>
<td data-row="7">**下载管理**</td><td data-row="7">Internet Download Manager、 JDownloader</td>



## 三. 总结

虽然 Agent Tesla 整体结构比较简单，而且已经有6年的历史，但它依旧是当前最流行的恶意软件之一。近年来经过不断的更新迭代，其功能也在不断完善，在免杀和分析对抗上也日渐复杂，同时结合了社会工程学，显著提升了防范的难度，相信这款商业窃密软件在之后也会更加活跃，我们建议通过采用以下措施，对相关威胁进行检测与防范：
1. 及时更新计算机安全补丁和软件；
1. 加强企业内部员工信息安全意识，规范安全操作；
1. 谨慎点击邮件附件，链接等；
1. 推荐使用微步在线威胁检测平台进行威胁检测，第一时间发现相关威胁。


## 四. 附录

### IOCs
1. 569b60fd57a93368c07a0e91dfb640c9e1fceed9a17f00760147d241fd9ce9e4
1. 6b666afdd5b7af512ce3aedc252405dd4f36b853aa4b19738a8ad8ee116e8e63
1. 5bc915e290024f61c9e29d5b5fb056ce46cf0582de0e27d7010446affe16c159
1. caeecccb50242129b5031161fcbc2f29e565c6646ac69042647621210e1a9121
1. 8940739b0fcb021a2bfa9542590169742e74a425e2c9fbd731d823a9a75a1655
1. 103project@epazote-lu.com
### 参考链接
1. https://labs.sentinelone.com/agent-tesla-old-rat-uses-new-tricks-to-stay-on-top/
1. https://malwatch.github.io/posts/agent-tesla-malware-analysis/#distribution-methods
1. https://www.seqrite.com/blog/gorgon-apt-targeting-msme-sector-in-india/
1. https://unit42.paloaltonetworks.com/covid-19-themed-cyber-attacks-target-government-and-medical-organizations/


## 关于微步在线研究响应团队

微步情报局，即微步在线研究响应团队，负责微步在线安全分析与安全服务业务，主要研究内容包括威胁情报自动化研发、高级 APT 组织&amp;黑产研究与追踪、恶意代码与自动化分析技术、重大事件应急响应等。
