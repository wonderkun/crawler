> 原文链接: https://www.anquanke.com//post/id/170390 


# TA505组织利用Excel 4.0宏针对银行机构的最新攻击活动分析


                                阅读量   
                                **157006**
                            
                        |
                        
                                                                                    



![](https://p5.ssl.qhimg.com/t01cc13bf67e2965ce3.png)



## 背景

2018年12月，360威胁情报中心捕获到多个利用Excel 4.0宏针对银行机构的攻击样本。钓鱼文档为携带恶意Excel 4.0宏的Office Excel文档，并通过它下载执行最终的后门程序。采用Excel 4.0宏有利于躲避安全软件的检测，对此我们曾做过相关的详细研究，相关报告可以参考：[https://ti.360.net/blog/articles/excel-macro-technology-to-evade-detection](https://ti.360.net/blog/articles/excel-macro-technology-to-evade-detection)。

360威胁情报中心经过溯源和关联后确认，这是TA505组织针对银行机构最新的攻击行动。并且基于对攻击者的画像，我们猜测TA505组织可能来自东欧地区以俄语为主要语言的国家。TA505组织由Proofpoint<sup>[1]</sup>在2017年9月首次命名，其相关活动可以追溯到2014年。该组织主要针对银行金融机构，采用大规模发送恶意邮件的方式进行攻击，并以传播Dridex、Locky等恶意样本而臭名昭著。这些年来，尽管已针对该组织采取了多次行动，比如通过打击Dridex<sup>[2]</sup><sup>[3]</sup>和Necurs等僵尸网络来削弱其影响，但都只起到了暂时性的效果<sup>[5]</sup><sup>[6]</sup><sup>[7]</sup>。

2018年3月，TA505组织被发现使用Necurs僵尸网络来传播FlawedAmmyy<sup>[8]</sup>远控后门程序。本月初，Proofpoint发表的另外一篇文章指出该组织使用的全新恶意软件，并将其命名为ServHelper<sup>[9]</sup>。360威胁情报中心此次捕获的后门与ServHelper非常相似，不过在入侵的过程中采用了更加难以检测的Excel 4.0宏。

![](https://p1.ssl.qhimg.com/t016a0e946be06a569d.png)

样本在VirusTotal上的检测情况



## 时间线

360威胁情报中心整理了与TA505组织相关的时间线如下：

![](https://p1.ssl.qhimg.com/t01bcedc049c3baab68.png)



## 攻击过程

360威胁情报中心捕获到多个攻击不同银行机构的恶意邮件，包括标准银行（南非）、智利银行、Bank of Maharashtra（印度）、Banca Fideuram私人银行（意大利）、Kotak Mahindra私人银行（印度）和RMB Private Bank（南非）。通过对这些邮件的分析，我们发现攻击者使用通过VPS服务搭建的或疑似被攻陷的邮件服务器来发送恶意邮件。根据公开资料查询结果表明，其中部分邮件服务器疑似位于乌克兰、摩尔多瓦和俄罗斯。这里以发往标准银行的邮件为例，还原攻击的过程。

含有恶意Excel 4.0宏的文档作为附件被发送到目标邮箱。样例中的邮件看似来自光纤网络供应商（Hiawatha Broadband Communications），其正文催促目标必须在当日内处理完毕那些未完成的支付交易。由于正文与目标的日常工作有较高的相关性，因此恶意附件容易被诱使打开：

![](https://p1.ssl.qhimg.com/t0123c5e526d1f0b24e.png)

Excel文档被打开后，其展示的迷惑性内容将误导用户启用宏功能，从而执行恶意的Excel 4.0宏代码：

![](https://p0.ssl.qhimg.com/t017e2a4514bfc8708d.png)

恶意的Excel 4.0宏代码位于隐藏的表单中，以避免引起受害用户的注意。该隐藏表单的名字由俄语组成：

![](https://p3.ssl.qhimg.com/t018161d8c24af301d4.png)

恶意的宏代码从hxxp://office365advance.com/update下载样本并执行，并同时试图打开记事本程序，以掩盖其背后的恶意行为：

![](https://p0.ssl.qhimg.com/t014c7e26d65b95273c.png)



## 样本分析

### Dropper（Update）

从office365advance.com下载的Update（MD5：53F7BE945D5755BB628DEECB71CDCBF2）是一个MSI文件，内含一个Nullsoft安装包。该文件有数字签名，不过目前该签名已被吊销：

![](https://p4.ssl.qhimg.com/t0110a44b5f3f9a264e.png)

Nullsoft安装包内含有两个文件，分别是后门程序（htpd.dat）和启动该后门的VBS脚本：

![](https://p4.ssl.qhimg.com/t010111145ea9053793.png)

Nullsoft安装脚本在运行时，会把htpd.dat和rds.vbs释放到%temp% 目录，随后创建help.bat文件并写入“rundll32.exe $TEMP\htpd.dat, bogus”：

![](https://p2.ssl.qhimg.com/t01ef646fe9e3686be6.png)

随后执行rds.vbs 脚本，该脚本会运行help.bat 从而加载后门程序（htpd.dat）。

### Backdoor（htpd.dat）

htpd.dat（MD5：272C036924BC9B8F44D6158220303A23）是一个动态链接库文件，主要功能在导出函数“bogus”中实现：

![](https://p5.ssl.qhimg.com/t0196b8f4f1b6849eb9.png)

当导出函数“bogus”被执行时，它会创建两个线程。其中一个用于同C&amp;C服务器通信，另外一个负责处理从该服务器获取的远程指令。在通信的过程中该后门采用HTTPS，并硬编码“asdgdgYss455”到参数key中：

![](https://p1.ssl.qhimg.com/t0192fc5c22e20fbc2f.png)

攻击者可以通过远程指令执行以下操作：
<td valign="top" width="158">**命令**</td><td valign="top" width="350">**功能**</td>
<td valign="top" width="158">**shell**</td><td valign="top" width="350">开启远程shell</td>
<td valign="top" width="158">**nop**</td><td valign="top" width="350">保持同C&amp;C服务器的连接</td>
<td valign="top" width="158">**slp**</td><td valign="top" width="350">设置睡眠时间</td>
<td valign="top" width="158">**load**</td><td valign="top" width="350">下载并执行EXE文件</td>
<td valign="top" width="158">**loaddll**</td><td valign="top" width="350">下载并执行DLL文件</td>
<td valign="top" width="158">**selfkill**</td><td valign="top" width="350">自删除</td>

![](https://p3.ssl.qhimg.com/t0191e50f9d8b4246d9.png)



## 溯源与关联

360威胁情报中心通过对样本的详细分析后发现，此次攻击的幕后团伙是TA505组织，部分关联依据如下。

在捕获的相似后门中，样本回连的C&amp;C服务器包括pointsoft[.]pw，这与Proofpoint<sup>[9]</sup>对TA505的描述一致。通过360威胁情报中心数据平台对C&amp;C服务器进行查询，也成功关联到了TA505组织：

![](https://p4.ssl.qhimg.com/t012a4f7ae7f819e08c.png)

该后门采用HTTPS与C2通信，并设置参数key的值为“asdgdgYss455”，该特殊值同样被TA505组织使用过。另外，通信过程中参数名称和顺序也是相同的：

![](https://p1.ssl.qhimg.com/t010df5f55fe85c27c8.png)

最后，后门指令和功能也与TA505使用的ServHelper RAT匹配。

### 攻击者画像

由于根据公开数据查询到的结果表明相关邮件服务器疑似位于乌克兰、摩尔多瓦和俄罗斯境内，邮件附件内隐藏的宏表单语言说明这些文档由俄语的Office软件创建，且该组织曾使用的Dridex恶意软件被溯源到东欧地区，因此我们猜测TA505组织可能来自东欧地区以俄语为主要语言的国家。



## 总结

TA505组织从被发现到现在已有近5年的时间，期间虽有多次针对该组织的打击行动，但可惜均未达到斩草除根的效果。尽管其发送的恶意邮件数量已有大幅下滑，但仍有一定的规模。另外这也不排除是其主动为之的策略，以避免被过度关注从而成为首要打击的对象。从捕获的样本来看，TA505的攻击目标不再局限于欧洲的银行机构，其重心似乎转向了南非、印度等发展中国家，而私人银行也成为其主要攻击对象。

从Dridex的复杂度、演化路径<sup>[7]</sup>及该组织曾使用的其它多类样本来看，TA505组织持续不断的在技术上投入以保证其攻击的有效性。本次捕获的后门更像是用于甄别受害者目标环境，并为后续攻击提供条件基础。随着攻击面的收敛，后续样本的捕获难度会不断加大。

相对于使用Office 0day，利用Excel 4.0宏需要更多的用户交互以完成攻击。虽然这会降低其攻击的成功率，但可以通过更有针对性的邮件内容和更具迷惑性的文档信息来弥补。此外，这类攻击具有很好的成本优势，因此仍被许多攻击组织大量采用。企业用户应尽可能小心打开来源不明的文档，如有需要可通过打开Office文档中的：文件-选项-信任中心-信任中心设置-宏设置，来禁用一切宏代码执行：

![](https://p4.ssl.qhimg.com/t01c5a96f354ebc3b1f.png)

目前，基于360威胁情报中心的威胁情报数据的全线产品，包括360威胁情报平台（TIP）、天眼高级威胁检测系统、360 NGSOC等，都已经支持对此类攻击的精确检测。



## IOC
<td valign="top" width="442">**Key String**</td>
<td valign="top" width="442">aSDGsdgo445</td>
<td valign="top" width="442">asdgdgYss455</td>
<td valign="top" width="442">**C2**</td>
<td valign="top" width="442">vesecase.com</td>
<td valign="top" width="442">afsssdrfrm.pw</td>
<td valign="top" width="442">pointsoft.pw</td>
<td valign="top" width="442">**Download URL**</td>
<td valign="top" width="442">hxxp://office365advance.com/update</td>
<td valign="top" width="442">hxxp://office365homepod.com/genhost</td>
<td valign="top" width="442">hxxp://add3565office.com/rstr</td>
<td valign="top" width="442">**Excel and eml samples**</td>
<td valign="top" width="442">9c35e9aa9255aa2214d704668b039ef6</td>
<td valign="top" width="442">44dad70d844f6696fc148a7330df4b21</td>
<td valign="top" width="442">fee0b31cc956f083221cb6e80735fcc5</td>
<td valign="top" width="442">4c400910031ee3f12d9958d749fa54d5</td>
<td valign="top" width="442">2e0d13266b45024153396f002e882f15</td>
<td valign="top" width="442">26f09267d0ec0d339e70561a610fb1fd</td>
<td valign="top" width="442">09e4f724e73fccc1f659b8a46bfa7184</td>
<td valign="top" width="442">18c2adfc214c5b20baf483d09c1e1824</td>
<td valign="top" width="442">8cd3b60b167de2897aa6abf75b643d48</td>
<td valign="top" width="442">2cb8e5d871f5d6c1a8d88b1fb7372eb0</td>
<td valign="top" width="442">e9130a2551dd030e3c0d7bb48544aaea</td>
<td valign="top" width="442">9b0cc257a245f04bcd3766750335ad0c</td>
<td valign="top" width="442">9888d1109d6d52e971a3a3177773efaa</td>
<td valign="top" width="442">be021b903653aa4b2d4b99f3dbc986f0</td>
<td valign="top" width="442">2036a9e088d16e8ac35614946034b1a5</td>
<td valign="top" width="442">ef5741c4b96ef9498357dc4d33498163</td>
<td valign="top" width="442">e84f6742f566ccaa285c4f2b8d20a77c</td>
<td valign="top" width="442">**Backdoor**</td>
<td valign="top" width="442">53F7BE945D5755BB628DEECB71CDCBF2</td>
<td valign="top" width="442">5B7244C47104F169B0840440CDEDE788</td>
<td valign="top" width="442">E00499E21F9DCF77FC990400B8B3C2B5</td>
<td valign="top" width="442">272C036924BC9B8F44D6158220303A23</td>
<td valign="top" width="442">C6774C1417BE2E8B7D14BAD13911D04B</td>
<td valign="top" width="442">cc29adb5b78300b0f17e566ad461b2c7</td>
<td valign="top" width="442">**数字签名**</td>
<td valign="top" width="442">Name: “VAL TRADEMARK TWO LIMITED”</td>
<td valign="top" width="442">Serial number:6e 91 95 0d d1 1f df 27 96 83 df b2 b4 9b 2f 47</td>
<td valign="top" width="442">Thumbprint:39 ca 0e 49 d4 01 77 4b 2b bf ea 16 27 60 7e 6e 6b dc 07 6f</td>
<td valign="top" width="442">Name: MASTER LIM LTD</td>
<td valign="top" width="442">Serial number:00 8e 3e 9a 2f e7 3c 91 98 5b 4f 90 d5 95 77 cd 6c</td>
<td valign="top" width="442">Thumbprint:26 0c 8d 47 00 3c a3 8a f0 54 53 f5 96 7a 8e 03 85 7f 04 88</td>



## 参考链接
1. https://www.proofpoint.com/us/threat-insight/post/threat-actor-profile-ta505-dridex-globeimposter
<li>
<a name="_Ref535485608"></a>https://www.secureworks.com/research/dridex-bugat-v5-botnet-takeover-operation</li>
<li>
<a name="_Ref535485659"></a>https://www.justice.gov/opa/pr/bugat-botnet-administrator-arrested-and-malware-disabled</li>
<li>
<a name="_Ref535486251"></a>https://www.proofpoint.com/us/threat-insight/post/necurs-botnet-outage-crimps-dridex-and-locky-distribution</li>
<li>
<a name="_Ref535486348"></a>https://www.symantec.com/connect/blogs/dridex-financial-trojan-aggressively-spread-millions-spam-emails-each-day</li>
<li>
<a name="_Ref535486349"></a>https://www.symantec.com/connect/blogs/necurs-mass-mailing-botnet-returns-new-wave-spam-campaigns</li>
<li>
<a name="_Ref535486351"></a>https://securelist.com/dridex-a-history-of-evolution/78531/</li>
<li>
<a name="_Ref535487371"></a>https://www.proofpoint.com/us/threat-insight/post/leaked-ammyy-admin-source-code-turned-malware</li>
<li>
<a name="_Ref535487762"></a>https://www.proofpoint.com/us/threat-insight/post/servhelper-and-flawedgrace-new-malware-introduced-ta505</li>
1. https://ti.360.net/