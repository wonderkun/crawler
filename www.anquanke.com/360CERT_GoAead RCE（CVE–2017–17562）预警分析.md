> 原文链接: https://www.anquanke.com//post/id/91454 


# 360CERT：GoAead RCE（CVE–2017–17562）预警分析


                                阅读量   
                                **130164**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t012a97d114cb81644b.jpg)](https://p4.ssl.qhimg.com/t012a97d114cb81644b.jpg)

> 报告来源：360网络安全响应中心
报告作者：MerJerson,云袭2001
更新日期：2017年12月19日

## 0x00 背景介绍

12月12日，MITRE披露一枚GoAhead的漏洞，编号为CVE-2017-17562，受影响的GoAhead，如果启用CGI动态链接，会有远程代码执行的危险。GoAhead广泛应用于嵌入式设备中。360CERT经过评估，确认该漏洞属于高危，建议用户尽快进行修复。



## 0x01 技术细节

定位到漏洞位置：cgi.c:cgiHandler()，其中envp分配一个数组，并由HTTP请求参数中的键值对进行填充，这个过程中只是对REMOTE_HOST和HTTP_AUTHORIZATION进行过滤，导致攻击者可以利用其他cgi进程的任意环境变量。

[![](https://cert.360.cn/static/fileimg/CVE-2017-17562_2_1513684308.png)](https://cert.360.cn/static/fileimg/CVE-2017-17562_2_1513684308.png)

envp填充完成后，会通过launchCgi进行调用，进行启动cgi进程。

[![](https://cert.360.cn/static/fileimg/CVE-2017-17562_3_1513684315.png)](https://cert.360.cn/static/fileimg/CVE-2017-17562_3_1513684315.png)



## 0x02 漏洞验证

[![](https://cert.360.cn/static/fileimg/CVE-2017-17562_4_1513684323.png)](https://cert.360.cn/static/fileimg/CVE-2017-17562_4_1513684323.png)

上面也提到了，因为过滤不完善，恶意的envp被传入launchCgi进行执行，这时我们需要知道cgiPath（我们的payload路径）。这个问题不大，Linux procfs文件系统，可以使用LD_PRELOAD=/proc/self/fd/0进行引用stdin，他将指向我们写入的临时文件。在HTTP请求时加入**?LD_PRELOAD=/proc/self/fd/0**便可。

[![](https://cert.360.cn/static/fileimg/CVE-2017-17562_5_1513684332.jpg)](https://cert.360.cn/static/fileimg/CVE-2017-17562_5_1513684332.jpg)

正常的效果如上图所示。但是有一个问题，攻击的时候我们需要指定一个cgi进程执行我们的LD_PRELOAD，这无疑提高了该漏洞的攻击成本。



## 0x03 影响范围

[![](https://cert.360.cn/static/fileimg/CVE-2017-17562_6_1513684340.png)](https://cert.360.cn/static/fileimg/CVE-2017-17562_6_1513684340.png)

根据360CERT的QUAKE全网资产检索系统评估，全网有数百万设备运行着GoAhead服务，考虑到嵌入式设备更新的滞后性，受该漏洞影响的设备较广。



## 0x04 修补建议

360CERT建议使用GoAhead产品的用户，检查当前应用版本，如果是易受攻击版本，请尽快更新相关补丁。



## 0x05 时间线

2017年12月12日 漏洞披露

2017年12月18日 360CERT进行跟进分析

2017年12月19日 360CERT发布预警



## 0x06 参考链接

[https://www.elttam.com.au/blog/goahead/?t=1&amp;cn=ZmxleGlibGVfcmVjcw%3D%3D&amp;refsrc=email&amp;iid=00814eaead1646519e0079bc88160394&amp;uid=854872895356411904&amp;nid=244](https://www.elttam.com.au/blog/goahead/?t=1&amp;cn=ZmxleGlibGVfcmVjcw%3D%3D&amp;refsrc=email&amp;iid=00814eaead1646519e0079bc88160394&amp;uid=854872895356411904&amp;nid=244)

[https://security-tracker.debian.org/tracker/CVE-2017-17562](https://security-tracker.debian.org/tracker/CVE-2017-17562)

[https://vulners.com/exploitdb/EDB-ID:43360](https://vulners.com/exploitdb/EDB-ID:43360)
