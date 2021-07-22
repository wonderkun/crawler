> 原文链接: https://www.anquanke.com//post/id/189971 


# 印度APT组织攻击我国多个目标曝光


                                阅读量   
                                **931911**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t016716e572c96a1037.jpg)](https://p2.ssl.qhimg.com/t016716e572c96a1037.jpg)



2019年10月27日，推特@MisterCh0c发布一张照片，通过360CERT研究人员分析，发现该C2控制台隶属于印度网军“蔓灵花”组织（Bitter），该后台控制界面中暴露多个我国IP地址被控制上线。控制台界面显示了木马控制后台的主机信息界面，包括最后上线时间、主机版本信息、用户名称、电脑名称等。

[![](https://p403.ssl.qhimgs4.com/t01469f36974aff471f.png)](https://p403.ssl.qhimgs4.com/t01469f36974aff471f.png)

通过该控制页面，攻击者可以对目标继续下发任务，其功能特马如下：

[![](https://p403.ssl.qhimgs4.com/t013bc7853d72373b6e.png)](https://p403.ssl.qhimgs4.com/t013bc7853d72373b6e.png)

Audiodq：获取计算机基本信息，远程获取文件并执行

igfxsrvk：键盘hook

Kill：设置sleep文件开机自启

Lsap、lsapc、lsapcr：磁盘、文件等相关操作

MSAService7：采用C#编写，功能包括：文件创建拷贝删除与传输、进程的创建挂起结束及其相关信息、cmd命令、剪切板信息、计算机基本信息包括CPU信息，计算机名称、磁盘信息等。

[![](https://p403.ssl.qhimgs4.com/t0176e8b899a474460d.png)](https://p403.ssl.qhimgs4.com/t0176e8b899a474460d.png)

Winsvc：采用C语言编写的木马，功能与上边类似

Sleep：关机操作

regdl：设置Audiodq开机自启

该C2链接地址为：[http://lmhostsvc[.]net/healthne/，IP：162.222.215.134，](http://lmhostsvc%5B.%5Dnet/healthne/%EF%BC%8CIP%EF%BC%9A162.222.215.134%EF%BC%8C)

特马hash：FBC56C2DADAB05E78C995F57BF50BCE5。

数据回传路径：[http://lmhostsvc.net/healthne/accept.php?a=User-PC&amp;b=USER-PC&amp;c=Windows%207%20Professional&amp;d=adminadmin90059c37-1320-41a4-b58d-2b75a9850d2f1565536040965860&amp;e=abcd。](http://lmhostsvc.net/healthne/accept.php?a=User-PC&amp;b=USER-PC&amp;c=Windows%207%20Professional&amp;d=adminadmin90059c37-1320-41a4-b58d-2b75a9850d2f1565536040965860&amp;e=abcd%E3%80%82)

相关样本anyrun分析地址：[https://app.any.run/tasks/4c024e23-6738-470a-8676-b52e39462500/](https://app.any.run/tasks/4c024e23-6738-470a-8676-b52e39462500/)

通过分析，控制台页面展示的受害者有6台主机隶属于中国。

此次曝光的蔓灵花组织C2控制台仅仅揭露蔓灵花组织在我国攻击的冰山一角，早在2017年末2018年初，蔓灵花组织使用其常用的攻击手法攻击过我国多个部委、重要行业单位以及巴基斯坦在我国的工作人员，影响单位和人员较多，其使用的C2控制台与本次曝光的C2控制台完全一致。

蔓灵花（BITTER）APT组织是一个长期针对中国、巴基斯坦等国家进行攻击活动的APT组织。近两年来，蔓灵花APT组织并未更新其后台控制端以及特马的升级，国内外多个安全研究组织都通过其后台漏洞进入到C2控制界面，另外，弱口令问题、目录遍历问题等常见WEB问题在该C2控制台均有漏洞体现。通过蔓灵花如此频繁的攻击活动，我们可以看出印度网军在网络情报获取方面一直采取积极主动的网络攻击的方式攫取情报，我国是网络威胁中的受害者。

相关C2：

lmhostsvc[.]net

162.222.215.134
