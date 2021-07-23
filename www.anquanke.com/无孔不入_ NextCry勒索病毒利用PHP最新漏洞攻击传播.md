> 原文链接: https://www.anquanke.com//post/id/193365 


# 无孔不入： NextCry勒索病毒利用PHP最新漏洞攻击传播


                                阅读量   
                                **1080225**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01f9ca1d4c9f28d5e8.png)](https://p5.ssl.qhimg.com/t01f9ca1d4c9f28d5e8.png)



## 概述

近日，奇安信病毒响应中心在日常样本监控过程中发现NextCry Ransomware的新进入渠道，其正在利用PHP-fpm远程代码执行漏洞（CVE-2019-11043）针对Linux服务器发起攻击尝试入侵。

NextCry勒索是一种新型勒索软件，该勒索由Python编写并使用PyInstall打包成Linux ELF二进制文件，采用RSA-2048和AES-256-CBC算法加密指定目录下的文件，无法解密，从勒索名可以看出，作者试图致敬2017年的WannaCry勒索蠕虫。

基于奇安信威胁情报中心的多维度大数据关联分析，目前该勒索主要攻击安装有Nextcloud软件的服务器，不排除后面会扩大攻击范围，为了避免恐慌情绪产生，我们披露此次攻击事件的部分细节，并给出解决方案。



## 漏洞分析

Nextcloud是一款开源的用于创建网络硬盘的客户端-服务器软件，常被用来搭建私有云盘，类似于我们熟知的Dropbox。

CVE-2019-11043是一个十月底刚被披露出来的PHP相关漏洞，相应的技术细节已经公开，利用此漏洞可以非常简单稳定在受影响的服务器上远程执行任意命令，在启用PHP-Fpm的Nginx服务器上运行某些版本的PHP 7有可能受到攻击。没有运行Nginx服务器理论上则不会产生影响，但值得关注的是Nextcloud软件默认情况下开启Nginx服务器，所以几乎所有的基于Nextcloud的云盘都会受到影响，这或许是攻击者选择Nextcloud的原因，Nextcloud官方在第一时间已经发布公告。

[![](https://p2.ssl.qhimg.com/t01834b332475df301d.png)](https://p2.ssl.qhimg.com/t01834b332475df301d.png)

漏洞出现在fpm_main.c中，当path_info被%0a字符截断时，值会被归零：

[![](https://p1.ssl.qhimg.com/t01554bdde2647ca824.png)](https://p1.ssl.qhimg.com/t01554bdde2647ca824.png)

由于path_info可控，通过将指针地址归零，从而将_fcgi_data_seg结构体中的pos指针归零，控制FCGI_PUTENV函数的结果：

[![](https://p3.ssl.qhimg.com/t01ad88407a6437f63e.png)](https://p3.ssl.qhimg.com/t01ad88407a6437f63e.png)

通过分析FCGI_PUTENV的内部实现，我们发现只要构造合理的数据包，就可以控制PHP任意全局变量：

[![](https://p0.ssl.qhimg.com/t0175a713042236a1fb.png)](https://p0.ssl.qhimg.com/t0175a713042236a1fb.png)

一旦攻击者控制了PHP全局变量，便可以在相应目录下包含NextCry勒索程序，进而执行勒索。



## 样本分析
<td style="width: 97.55pt;" valign="top">文件名称</td><td style="width: 286.05pt;" valign="top">nextcry</td>
<td style="width: 97.55pt;" valign="top">文件类型</td><td style="width: 286.05pt;" valign="top">Linux ELF</td>

通过对PyInstaller解出来的pyc进行反编译后得到了勒索的源代码，从mian函数中可以看出，一旦入侵成功之后，便会读取nextcloud的配置文件来搜索Nextcloud文件共享并同步数据目录

[![](https://p0.ssl.qhimg.com/t01bb07f0c43c5771e9.png)](https://p0.ssl.qhimg.com/t01bb07f0c43c5771e9.png)

之后开始使用AES加密文件，并使用内置RSA公钥加密AES密钥

[![](https://p1.ssl.qhimg.com/t0132c13dcc7e900bb7.png)](https://p1.ssl.qhimg.com/t0132c13dcc7e900bb7.png)

将加密后的AES密钥保存到keys.ENC文件中，最后生成勒索信index.php

[![](https://p5.ssl.qhimg.com/t01cc3f5617e980ebd1.png)](https://p5.ssl.qhimg.com/t01cc3f5617e980ebd1.png)

勒索信如下，要求支付0.025比特币，目前无法在不支付赎金的情况下解密。

[![](https://p5.ssl.qhimg.com/t0198d235fd7facf1d8.png)](https://p5.ssl.qhimg.com/t0198d235fd7facf1d8.png)



## 结论

奇安信威胁情报中心目前已经检测到有用户中招，请网站管理员更新PHP软件包并更新Nginx配置文件，将相关项改为：

[![](https://p4.ssl.qhimg.com/t0165912bf5996ddaad.png)](https://p4.ssl.qhimg.com/t0165912bf5996ddaad.png)

目前奇安信集团全线产品，包括天擎、天眼、SOC、态势感知、威胁情报平台，支持对涉及相关攻击活动的检测和相关勒索病毒的查杀。



## IOC

MD5：

8c6ed96e6df3d8a9cda39aae7e87330c

勒索比特币钱包地址：1K1wwHCUpmsKTuDh9TagfJ4h2bKMxLkjpY

联系邮箱：aksdkja0sdp@ctemplar.com



## 参考链接

[1] https://help.nextcloud.com/t/urgent-security-issue-in-nginx-php-fpm/62665

[2] https://paper.seebug.org/1063/

[3] https://blog.qualys.com/webappsec/2019/10/30/php-remote-code-execution-vulnerability-cve-2019-11043
