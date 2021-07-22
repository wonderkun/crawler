> 原文链接: https://www.anquanke.com//post/id/86701 


# 【技术分享】EternalBlue与Trojan[DDoS]/Win32.Nitol.M的“狼狈为奸”


                                阅读量   
                                **133011**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0187185b478dd0ae50.jpg)](https://p2.ssl.qhimg.com/t0187185b478dd0ae50.jpg)



**前言**



2017年4月被匿名黑客“影子经纪人”公布了第二批NSA武器，其中就包含了"EternalBlue"——MS17-010漏洞，5月中旬该漏洞的自动化利用工具如雨后春笋般在地下黑产出现并迅速传播，目前为止安天捕风监控捕获到的"EternalBlue"自动化利用工具已经已有多套（见图1-1 工具集合），这也证实国外某黑客“NSA工具公布意味着黑客平民化开始”的警告言论。

[![](https://p0.ssl.qhimg.com/t012bdc2f74497352c9.png)](https://p0.ssl.qhimg.com/t012bdc2f74497352c9.png)

图1-1 工具集合

"EternalBlue"自动化工具的出现伊始就已经实现漏洞与各类型病毒结合。从早期监控捕获到的"EternalBlue"与Gh0st远控的为虎作伥实现RAT（**Remote Accass Trojan**）自动化种植感染，到现在的"EternalBlue"与Nitol.M的狼狈为奸实现DDoS botnet快速自动化拓展“肉鸡”，都警示着：互联网安全形势越发严峻，为互联网安全保驾护航更是任重而道远。

<br>

**基本信息**

****[![](https://p2.ssl.qhimg.com/t01dc5f1ff0b09052d1.png)](https://p2.ssl.qhimg.com/t01dc5f1ff0b09052d1.png)

表1-1 样本基本信息

**传播方式**

****

2017-08-14 08:41:54，安天-捕风监控到一则木马感染事件（见图3-1 监控捕获数据），并自动获取相关hfs（HTTP Files Server）目录下的样本数据。发现hfs里面还存放有"EternalBlue"自动化利用工具（见图3-2 hfs数据），经过IDA分析x86.dll样本得知利用该工具感染的病毒正是**Trojan[DDoS]/Win32.Nitol.M**被控端木马（见图3-3 木马下载url地址），即**http://***.***.166.83:5999/hw1.exe**的**Trojan[DDoS]/Win32.Nitol.M**样本可以通过该工具利用MS17-010漏洞进行自动化“肉鸡”拓展。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0176e093b15cea4f3e.png)

图3-1 监控捕获数据

[![](https://p3.ssl.qhimg.com/t013294e60fd3e038a3.png)](https://p3.ssl.qhimg.com/t013294e60fd3e038a3.png)

图3-2 hfs数据

[![](https://p0.ssl.qhimg.com/t019a3025c932b61ad3.png)](https://p0.ssl.qhimg.com/t019a3025c932b61ad3.png)

图3-3 木马下载url地址

**样本详细分析**

****

因为DDoS botnet的Nitol家族源码早已开源化，所以互联网上出现很多根据源码改进的变种版本，Trojan[DDoS]/Win32.Nitol.M就是其中之一，主要实现DDoS攻击类型有syn flood、udp flood、icmp flood、tcp flood、dns flood、cc flood。

**1)样本备份与创建服务**

样本运行会通过检查服务名称".Net CLR"（该服务名称是Nitol家族默认服务名称）存在与否来验证样本是否初次运行。见图4-1 检查服务名称：

[![](https://p0.ssl.qhimg.com/t01dc950ae2db58de04.png)](https://p0.ssl.qhimg.com/t01dc950ae2db58de04.png)

图4-1 检查服务名称

**2)如果服务名不存在，则进行样本备份和创建服务实现样本自启动而长期驻留受害系统。**

见图4-2 样本备份及自启动设置：

[![](https://p5.ssl.qhimg.com/t01d3064a84baabf441.png)](https://p5.ssl.qhimg.com/t01d3064a84baabf441.png)

图4-2 样本备份及自启动设置

**3)配置解密获取C2并创建连接。**

在配置解密上**Trojan[DDoS]/Win32.Nitol.M**同样继承Nitol家族系列的风格，使用**base64 + 凯撒位移 + 异或三重算法**进行加密。

见图4-3 C2配置解密：

[![](https://p2.ssl.qhimg.com/t013dc32159520e9932.png)](https://p2.ssl.qhimg.com/t013dc32159520e9932.png)

图4-3 C2配置解密

**4)获取系统配置信息。**

获取系统版本和CPU配置及内存信息作为向C2发送的首包内容，并实时等待接收C2远程指令，见图4-4 bot与C2通讯交互：

[![](https://p4.ssl.qhimg.com/t01bc98e215faac9365.png)](https://p4.ssl.qhimg.com/t01bc98e215faac9365.png)

图4-4 bot与C2通讯交互

**5)解析并执行C2的远程指令。**

当接收到C2的远程指令是首先对指令类型进行识别鉴定，然后分类执行（见图4-5 识别鉴定指令类型）。

[![](https://p4.ssl.qhimg.com/t0121b6ad5a626f5a75.png)](https://p4.ssl.qhimg.com/t0121b6ad5a626f5a75.png)

图4-5 识别鉴定指令类型

远程指令类型主要包含有DDoS Attack、Stop Attack、Download Files、CMD Shell、Delete Service，见表4-1指令类型数据表：

[![](https://p5.ssl.qhimg.com/t01b85c348571458027.png)](https://p5.ssl.qhimg.com/t01b85c348571458027.png)

表4-1 指令类型数据表

**6)DDoS攻击指令协议解析。**

该变种的DDoS Attack攻击有syn flood、udp flood、icmp flood、tcp flood、dns flood、cc flood 6种攻击类型，见图4-6 DDoS攻击类型。攻击类型协议整理见表4-2 攻击类型协议表：

[![](https://p5.ssl.qhimg.com/t0132c637c10258c947.png)](https://p5.ssl.qhimg.com/t0132c637c10258c947.png)

图4-6  DDoS攻击类型

[![](https://p1.ssl.qhimg.com/t01a6d31a986b397a95.png)](https://p1.ssl.qhimg.com/t01a6d31a986b397a95.png)

表4-2攻击类型协议表



**攻击情报**

****

结合7月21日捕获到的同家族版本进行监控获取的攻击情报中得知，近一个月中共发起579次攻击，185起攻击事件，主要使用攻击类型为syn flood占57.3%,cc flood(http flood)占28.6%，icmp flood占11.9%，tcp flood占2.2%，表4-3 受害者Top30列出被攻击次数top30的部分攻击情报，攻击情报概览见图4-7 Trojan[DDoS]/Win32.Nitol.M攻击情报概览。

表4-3 受害者Top30

[![](https://p3.ssl.qhimg.com/t011f079dc58347707d.png)](https://p3.ssl.qhimg.com/t011f079dc58347707d.png)

[![](https://p0.ssl.qhimg.com/t016ee17e0f9fd10d7f.png)](https://p0.ssl.qhimg.com/t016ee17e0f9fd10d7f.png)

[![](https://p5.ssl.qhimg.com/t018f460d8a18fd841c.png)](https://p5.ssl.qhimg.com/t018f460d8a18fd841c.png)

[![](https://p2.ssl.qhimg.com/t01a034d68b6fdc5333.png)](https://p2.ssl.qhimg.com/t01a034d68b6fdc5333.png)

图4-7 Trojan[DDoS]/Win32.Nitol.M攻击情报概览

**总结**<br>

****

因为独木难支，所以任何一个botnet家族都不会对互联网形成足够大的威胁，但是如果结合漏洞的自动化利用工具迅速拓展botnet的“肉鸡”量，再加上多个botnet组团攻击将会对互联网造成极大的危害。从安天-捕风监控到的历次高流量攻击事件都是多个botnet家族联合发起攻击。据了解，目前网上流传的“EternalBlue”自动化漏洞利用工具，通过IP网段自动化批量扫描每天仍旧能入侵大量设备并植入病毒，也就侧面说明还有很多设备尚未升级系统及修补漏洞补丁。因此，安天作为国内网络安全尽责的守护者之一，提醒广大同行警惕新型botnet的兴起，同时也提醒广大互联网用户安全、健康上网，安装杀毒、防毒软件（参考1 安天智甲工具）并及时升级系统和修补设备漏洞！



**参考资料**



[http://www.antiy.com/tools.html](http://www.antiy.com/tools.html)

MD5:c7d0827b6224b86f0a90fa42a8d39edd
