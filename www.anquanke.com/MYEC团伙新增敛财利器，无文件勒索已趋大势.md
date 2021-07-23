> 原文链接: https://www.anquanke.com//post/id/188287 


# MYEC团伙新增敛财利器，无文件勒索已趋大势


                                阅读量   
                                **549509**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01971c3aac6ac3efb4.jpg)](https://p4.ssl.qhimg.com/t01971c3aac6ac3efb4.jpg)



## 概述

奇安信病毒响应中心在日常的样本监控中发现，MYEC团伙新增了敛财利器，开始朝着基于无文件落地型的勒索软件方向发展，通过伪装成马来西亚税务局的诱饵Word文档执行宏代码，宏执行powershell，从远程服务器上下载powershell加密模块并调用，最后弹出勒索框，由于其执行全过程没有二进制文件落地，给取证分析溯源带来了极大的困难。

为防止国内企业中招，结合相关线索，我们将其命名为“MYEC”黑客团伙，并对其进行披露。



## 详细分析

样本概要
<td style="width: 72.0pt;" valign="top">MD5</td><td style="width: 181.5pt;" valign="top">2ad6ed0c04e522b60721dc46b2381a9f</td>
<td style="width: 72.0pt;" valign="top">文件名</td><td style="width: 181.5pt;" valign="top">Panduan_Kemaskini.doc</td>
<td style="width: 72.0pt;" valign="top">文件类型</td><td style="width: 181.5pt;" valign="top">Doc</td>
<td style="width: 72.0pt;" valign="top">创建时间</td><td style="width: 181.5pt;" valign="top">2019-10-07 02:54:00</td>
<td style="width: 72.0pt;" valign="top">保存用户名</td><td style="width: 181.5pt;" valign="top">Soo, Zing Zhao</td>

捕获的样本（Panduan_Kemaskini.doc）通过鱼叉邮件的形式投递，文档内容伪装成马来西亚税务局免费个人资料指南诱导用户启用宏。内容如下：

[![](https://p3.ssl.qhimg.com/t019ce40d64faa9de62.png)](https://p3.ssl.qhimg.com/t019ce40d64faa9de62.png)

从诱饵文件中提取到宏，执行经过混淆的powershell命令

[![](https://p5.ssl.qhimg.com/t01f04535e934699a8a.png)](https://p5.ssl.qhimg.com/t01f04535e934699a8a.png)

从C2下载下一阶段的payload脚本

hxxp://ec2-52-220-60-155.ap-southeast-1.compute.amazonaws.com/kk.ps1，power shell脚本免杀效果如下

[![](https://p0.ssl.qhimg.com/t012a3bf5d59e38be0b.png)](https://p0.ssl.qhimg.com/t012a3bf5d59e38be0b.png)

核心逻辑被混淆

[![](https://p2.ssl.qhimg.com/t01b5df3d3aebee799c.png)](https://p2.ssl.qhimg.com/t01b5df3d3aebee799c.png)

解混淆运行之后，寻找固定目录下的指定后缀文件

*.doc,*.docx,*.xls,*xlsx,*.ppt,*.pptx,*.pdf, y0uR_D@ta.txt

接着从微软的TechNet库中（https://gallery.technet.microsoft.com/EncryptDecrypt-files-use-65e7ae5d/file/165403/14/FileCryptography.psm1）下载powershell加密模块，保存到C:\Users\Public\ll.psm1，ll.psm1如下

[![](https://p2.ssl.qhimg.com/t01699d7b51da004c11.png)](https://p2.ssl.qhimg.com/t01699d7b51da004c11.png)

导出函数功能如下
<td style="width: 134.3pt;" valign="top">New-CryptographyKey</td><td style="width: 309.7pt;" valign="top">根据命令行参数随机生成加密算法（AES，DES，RC2）的key</td>
<td style="width: 134.3pt;" valign="top">Protect-File</td><td style="width: 309.7pt;" valign="top">加密文件</td>
<td style="width: 134.3pt;" valign="top">Unprotect-File</td><td style="width: 309.7pt;" valign="top">解密文件</td>

接着生成AESkey，加密文件，文件后缀取决于执行什么算法，该样本使用AES加密文件，则加密后缀为.AES，拼接URL并访问

hxxp://ec2-52-220-60-155.ap-southeast-1.compute.amazonaws.com\本机用户名\Base64加密后的key，所以理论上讲如果安装了类似于天眼的流量监控系统的话，可以捕捉到AESkey明文，并且解密文件。同时下载勒索信以及生成勒索框的图片

[![](https://p2.ssl.qhimg.com/t01b5896bcdf616e3b9.png)](https://p2.ssl.qhimg.com/t01b5896bcdf616e3b9.png)

生成勒索框

[![](https://p1.ssl.qhimg.com/t01f06fd010b148e000.png)](https://p1.ssl.qhimg.com/t01f06fd010b148e000.png)

勒索框内容如下，中间为勒索信的内容

[![](https://p5.ssl.qhimg.com/t01fa8c08f6c3567abf.png)](https://p5.ssl.qhimg.com/t01fa8c08f6c3567abf.png)

勒索信内容如下

[![](https://p0.ssl.qhimg.com/t01ee700d5659ae75cc.png)](https://p0.ssl.qhimg.com/t01ee700d5659ae75cc.png)



## 同源分析

通过关联分析，我们发现了该团伙的两个同源样本。

样本经过Boxedapp加壳，里面实际上是一个.net写的勒索病毒,经过分析.net样本修改自开源勒索项目Hidden-tear

[![](https://p5.ssl.qhimg.com/t0121275120eba60154.png)](https://p5.ssl.qhimg.com/t0121275120eba60154.png)

该样本同样会向远程服务器上传AES的密钥

[![](https://p4.ssl.qhimg.com/t014a1a9e53785c2860.png)](https://p4.ssl.qhimg.com/t014a1a9e53785c2860.png)

其中salt和password在加密文件时被使用

[![](https://p5.ssl.qhimg.com/t014c8e142367c0ced2.png)](https://p5.ssl.qhimg.com/t014c8e142367c0ced2.png)

而salt和password都是经过GenerateRandomSalt函数生成随机数进行处理的

[![](https://p0.ssl.qhimg.com/t015f6e81edf3a60d04.png)](https://p0.ssl.qhimg.com/t015f6e81edf3a60d04.png)

同理，如果能捕捉到流量，则可以进行解密。该样本同样会弹出相应的勒索框

[![](https://p4.ssl.qhimg.com/t01844893b093eb085d.png)](https://p4.ssl.qhimg.com/t01844893b093eb085d.png)

有趣的是在另一个同源样本的PDB中<br>
C:\Users\Illegear\Desktop\svchost\obj\x86\Debug\$safeprojectname$.pdb

Illegear是马来西亚的一个笔记本品牌，说明该团伙很有可能位于马来西亚。

经过深度的挖掘，我们发现去年曾经出现过一款名为blank的勒索软件，其加密算法、解密算法和随机数生成代码以及函数名与同源样本高度相似，左为blank，右为同源样本

FileEncrypt函数比较：

[![](https://p2.ssl.qhimg.com/t01bc5d3577430a1427.png)](https://p2.ssl.qhimg.com/t01bc5d3577430a1427.png)

FileDecrypt函数比较

[![](https://p1.ssl.qhimg.com/t0139c59b077195e76e.png)](https://p1.ssl.qhimg.com/t0139c59b077195e76e.png)

GenerateRandomSalt函数比较

[![](https://p4.ssl.qhimg.com/t0154b5980300c7f326.png)](https://p4.ssl.qhimg.com/t0154b5980300c7f326.png)

Blank勒索病毒的PDB：

C:\Users\Lenovo\source\repos\Blank\Blank\obj\Debug\Blank.pdb

其PDB结构上与同源样本也有相似之处。但是还无法完全确认Blank勒索病毒是MYEC团伙所为，也有可能该团伙抄袭了Blank勒索的相关代码。这里我们只提供一个思路供社区参考



## 总结

MYEC团伙本次使用的无文件落地型勒索的代码并不如大火的FTCODE勒索成熟，但这无疑代表着勒索病毒往无文件落地方向发展的一个大趋势：脚本免杀效果好，可复用性高，摆脱了以往基于可执行文件的运行方式。随之而来的就是廉价和轻量化，外加当今恶意软件投放服务越来越成熟，除了传统的投放服务（僵尸网络），第三方投放服务的兴起必将会促使一些脚本小子加入该行业。可以预见将来基于脚本的勒索病毒会越来越多，不同勒索相互代码复用率也会越来越高，这无疑加大了安全研究人员的分析和溯源难度。

目前奇安信集团全线产品，包括天眼、SOC、态势感知、威胁情报平台，支持对涉及MYEC黑客团伙的攻击活动检测。奇安信天擎终端防护产品内置的EDR检测机制通过恶意代码的行为分析，支持对该组织此类非落地样本的检测和查杀。



## IOC

文件MD5

2ad6ed0c04e522b60721dc46b2381a9f

f7354b15e4fa981d770de4cfb6f0149e

c8a597d2ff2a5dc475949e2c223399e4

b5c259af5eb7b4eca8d131ffc6866bdd

9f570a53629d10aaa6aa97b71b4e8b70

C2

52.220.60.155:80

HOST

ec2-52-220-60-155.ap-southeast-1.compute.amazonaws.com

勒索软件相关信息

邮箱：[naned@mail-card.net](mailto:naned@mail-card.net)

BitCoin钱包：

Q43hBguYNfRCSyEBLMKhJwXxunvMahTMFC

s4C6MPmpk4AXNVVUWtfG6JWvjPfENVv8k5
