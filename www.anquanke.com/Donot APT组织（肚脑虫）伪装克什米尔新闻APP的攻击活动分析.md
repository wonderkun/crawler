> 原文链接: https://www.anquanke.com//post/id/186254 


# Donot APT组织（肚脑虫）伪装克什米尔新闻APP的攻击活动分析


                                阅读量   
                                **344294**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t01583bb4527d50902e.png)](https://p5.ssl.qhimg.com/t01583bb4527d50902e.png)



## 背景

Donot“肚脑虫”（APT-C-35）是疑似具有南亚背景的APT组织，由奇安信威胁情报中心红雨滴团队（@RedDrip7）持续跟踪发现并命名，其主要针对巴基斯坦等南亚地区国家进行网络间谍活动。

该APT组织主要针对政府机构等领域进行攻击，以窃取敏感信息为主要目的。该APT组织除了以携带Office漏洞或者恶意宏的鱼叉邮件进行恶意代码的传播之外，还格外擅长利用安卓APK进行恶意代码传播。

近期，随着印巴在克什米尔地区（Kashmir）冲突的不断升级，具有南亚背景的APT团伙纷纷采用该地区冲突相关信息作为诱饵针对巴基斯坦进行攻击活动。奇安信威胁情报中心刚曝光了摩诃草在PC端利用克什米尔相关信息为诱饵的攻击活动[1]，同样具有南亚背景的Donot APT组织也不甘示弱开始展开其在移动端的攻击火力。奇安信红雨滴团队在捕获Donot 移动端新样本的第一时间便对其进行了披露。

[![](https://p3.ssl.qhimg.com/t013d96595408f02891.png)](https://p3.ssl.qhimg.com/t013d96595408f02891.png)

## 样本信息
<td valign="top" width="113">文件名称</td><td valign="top" width="398">KNS Lite</td>
<td valign="top" width="113">软件名称</td><td valign="top" width="398">KNS Lite</td>
<td valign="top" width="113">软件包名</td><td valign="top" width="398">com.newlite.sapp</td>
<td valign="top" width="113">MD5</td><td valign="top" width="398">497A67D28058A781681F20E32B7B3D6A</td>
<td valign="top" width="113">安装图标</td><td valign="top" width="398">[![](https://p4.ssl.qhimg.com/t01e8935ffe306ef002.png)](https://p4.ssl.qhimg.com/t01e8935ffe306ef002.png)</td>



## 诱饵分析

此次发现的Donot新样本通过仿冒Kashmir News Service（克什米尔新闻服务）的APP“KNS”，诱骗用户安装使用。

克什米尔新闻服务公司KNS是查谟和克什米尔的第一家在线新闻机构，成立于2002年1月，现已成为该州首屈一指，可信赖的双语，英语和乌尔都语新闻机构。

近期，印巴两军在克什米尔军事对峙线附近再度爆发了摩擦战，根据巴方披露的消息，本次交战已造成3名巴基斯坦士兵和5名印军士兵死亡。而随着克什米尔局势的“循环上升”，全世界的焦点无疑都集中在“克什米尔”，因此Donot新的诱饵通过仿冒Kashmir News Service（克什米尔新闻服务）其目的显而易见。

诱饵APP图标：

[![](https://p5.ssl.qhimg.com/t019c30cacbf3fce5ff.png)](https://p5.ssl.qhimg.com/t019c30cacbf3fce5ff.png)

样本运行截图：

[![](https://p4.ssl.qhimg.com/t01ae535c44f06893b6.png)](https://p4.ssl.qhimg.com/t01ae535c44f06893b6.png)

Google商城正版APP截图：

[![](https://p5.ssl.qhimg.com/t0176484939af0e3c79.png)](https://p5.ssl.qhimg.com/t0176484939af0e3c79.png)

Kashmir News Service（克什米尔新闻服务）官网截图：

[![](https://p5.ssl.qhimg.com/t01bd79529b609f0212.png)](https://p5.ssl.qhimg.com/t01bd79529b609f0212.png)



## 样本分析

### 样本行为描述

此次新发现的Donot样本，其在代码结构上并没有过多的改变，恶意代码功能方面也没有增加额外的功能。而与以往的不同之处，在于对诱饵文件的“包装”以及恶意APP的功能完整性方面的“用心”。

恶意APP运行以后，并没有以往的隐藏自身图标，而是通过仿冒Kashmir News Service（克什米尔新闻服务）展现给用户一个完整的新闻APP功能，从而达到欺骗用户放心使用，更加安全的保存了自身。

样本运行以后会在后台，通过最新服务端（[mangasiso.top](https://www.virustotal.com/gui/search/behaviour_network%3A%22mangasiso.top%22)）下发15种远控指令，其远控操作有：获取用户手机通话记录信息、获取用户手机通讯录信息、获取用户手机短信息、获取外置存储卡文件列表信息、获取WiFi、设备厂商等信息、获取用户地理位置信息、获取用户手机已安装软件列表等。

远控指令列表：
<td valign="top" width="184">指令下发服务器</td><td valign="top" width="52">指令</td><td valign="top" width="317">指令功能</td>
<td rowspan="15" valign="top" width="184">      [mangasiso.top](https://www.virustotal.com/gui/search/behaviour_network%3A%22mangasiso.top%22)</td><td valign="top" width="52">Call</td><td valign="top" width="317">获取用户手机通话记录信息</td>





[mangasiso.top](https://www.virustotal.com/gui/search/behaviour_network%3A%22mangasiso.top%22)
<td valign="top" width="52">CT</td><td valign="top" width="317">获取用户手机通讯录信息</td>
<td valign="top" width="52">SMS</td><td valign="top" width="317">获取用户手机短信息</td>
<td valign="top" width="52">Key</td><td valign="top" width="317">获取App输入的内容信息</td>
<td valign="top" width="52">Tree</td><td valign="top" width="317">获取外置存储卡文件列表信息</td>
<td valign="top" width="52">AC</td><td valign="top" width="317">获取Account信息</td>
<td valign="top" width="52">Net</td><td valign="top" width="317">获取WiFi、设备厂商等信息</td>
<td valign="top" width="52">CR</td><td valign="top" width="317">设置用户手机电话通话录音</td>
<td valign="top" width="52">LR</td><td valign="top" width="317">设定特定时间段录音</td>
<td valign="top" width="52">FS</td><td valign="top" width="317">文件上传开关</td>
<td valign="top" width="52">GP</td><td valign="top" width="317">获取地理位置信息</td>
<td valign="top" width="52">PK</td><td valign="top" width="317">获取用户手机已安装软件列表</td>
<td valign="top" width="52">BW</td><td valign="top" width="317">获取chrome书签列表</td>
<td valign="top" width="52">CE</td><td valign="top" width="317">获取日历事件信息</td>
<td valign="top" width="52">Wapp</td><td valign="top" width="317">获取whatsapp聊天信息</td>

程序运行流程图：

[![](https://p5.ssl.qhimg.com/t0178b294f2534e2c38.png)](https://p5.ssl.qhimg.com/t0178b294f2534e2c38.png)

### 详细代码分析

通过访问Kashmir News Service（克什米尔新闻服务）官方新闻链接，诱骗用户：

[![](https://p5.ssl.qhimg.com/t01a0e0bb33660c4407.png)](https://p5.ssl.qhimg.com/t01a0e0bb33660c4407.png)

[![](https://p3.ssl.qhimg.com/t010bfe5a570181ac22.png)](https://p3.ssl.qhimg.com/t010bfe5a570181ac22.png)

加载Youtube新闻视频，进一步伪装自己：

[![](https://p5.ssl.qhimg.com/t01e7e7150318adbcff.png)](https://p5.ssl.qhimg.com/t01e7e7150318adbcff.png)

[![](https://p0.ssl.qhimg.com/t01ce3bdb04737a0b79.png)](https://p0.ssl.qhimg.com/t01ce3bdb04737a0b79.png)

通过服务端（[mangasiso.top](https://www.virustotal.com/gui/search/behaviour_network%3A%22mangasiso.top%22)）下发15种远控指令，对用户手机进行后台操控，获取用户手机信息：

获取控制指令：

[![](https://p1.ssl.qhimg.com/t018079cf5507274bdf.png)](https://p1.ssl.qhimg.com/t018079cf5507274bdf.png)

远控指令：

[![](https://p2.ssl.qhimg.com/t014599d3821aaca43e.png)](https://p2.ssl.qhimg.com/t014599d3821aaca43e.png)

指令“Call”:获取用户手机通话记录信息：

[![](https://p3.ssl.qhimg.com/t0159c8f3aeea1eb54e.png)](https://p3.ssl.qhimg.com/t0159c8f3aeea1eb54e.png)

[![](https://p0.ssl.qhimg.com/t01ada5cdc510392b6b.png)](https://p0.ssl.qhimg.com/t01ada5cdc510392b6b.png)

指令“CT”：获取用户手机通讯录信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01081b52ea5c0029d4.png)

指令“SMS”：获取用户手机短信息：

[![](https://p3.ssl.qhimg.com/t01c1209a0fe6e3f5f6.png)](https://p3.ssl.qhimg.com/t01c1209a0fe6e3f5f6.png)

指令“Key”：获取App输入的内容信息：

[![](https://p4.ssl.qhimg.com/t01034136824ed9d58d.png)](https://p4.ssl.qhimg.com/t01034136824ed9d58d.png)

指令“Tree”：获取外置存储卡文件列表信息：

[![](https://p4.ssl.qhimg.com/t011c6bf0737ba3c94d.png)](https://p4.ssl.qhimg.com/t011c6bf0737ba3c94d.png)

[![](https://p2.ssl.qhimg.com/t0164811ddac234d467.png)](https://p2.ssl.qhimg.com/t0164811ddac234d467.png)

指令“AC”：获取Account信息：

[![](https://p4.ssl.qhimg.com/t01120673c758aee603.png)](https://p4.ssl.qhimg.com/t01120673c758aee603.png)

指令“Net”：获取WiFi、设备厂商等信息：

[![](https://p2.ssl.qhimg.com/t015cb86bfd97b81c35.png)](https://p2.ssl.qhimg.com/t015cb86bfd97b81c35.png)

指令“CR”：设置用户手机电话通话录音：

[![](https://p2.ssl.qhimg.com/t016d30ef514fbfc6f1.png)](https://p2.ssl.qhimg.com/t016d30ef514fbfc6f1.png)

指令“LR”：设定特定时间段录音：

[![](https://p3.ssl.qhimg.com/t01fd4be223b10eb817.png)](https://p3.ssl.qhimg.com/t01fd4be223b10eb817.png)

指令“FS”：文件上传开关：

[![](https://p4.ssl.qhimg.com/t017f4c6f01c57cc892.png)](https://p4.ssl.qhimg.com/t017f4c6f01c57cc892.png)

指令“GP”：获取地理位置信息：

[![](https://p2.ssl.qhimg.com/t01749a2efcb2c445bb.png)](https://p2.ssl.qhimg.com/t01749a2efcb2c445bb.png)

指令“PK”：获取用户手机已安装软件列表：

[![](https://p1.ssl.qhimg.com/t0156847fb858ba9689.png)](https://p1.ssl.qhimg.com/t0156847fb858ba9689.png)

指令“CE”：获取日历事件信息：

[![](https://p2.ssl.qhimg.com/t0165fe78265d33ec87.png)](https://p2.ssl.qhimg.com/t0165fe78265d33ec87.png)

指令“Wapp”：获取whatsapp聊天信息：

[![](https://p4.ssl.qhimg.com/t0161104ec13309c6ad.png)](https://p4.ssl.qhimg.com/t0161104ec13309c6ad.png)

获取到的部分信息进行上传：

[![](https://p0.ssl.qhimg.com/t01ca2dc4a303fd5b11.png)](https://p0.ssl.qhimg.com/t01ca2dc4a303fd5b11.png)

[![](https://p3.ssl.qhimg.com/t0109a15966b7030a0e.png)](https://p3.ssl.qhimg.com/t0109a15966b7030a0e.png)

[![](https://p5.ssl.qhimg.com/t016eeb4b6e369915bc.png)](https://p5.ssl.qhimg.com/t016eeb4b6e369915bc.png)



## 同源分析及代码变迁

经过我们对于Donot的持续跟踪与研究，每当巴以政治局势紧张的时候，Donot便会异常的活跃，仅2019年我们发现，Donot在移动端已进行三次改变，不论是框架结构、代码功能、伪装方式都进行了一系列的变迁。

### 2019年红雨滴团队Donot跟踪历史

红雨滴团队在今年陆续发现并公布了Donot团伙所使用的一系列数字武器：

[![](https://p0.ssl.qhimg.com/t0167a0d7e1513cebb4.png)](https://p0.ssl.qhimg.com/t0167a0d7e1513cebb4.png)

[![](https://p2.ssl.qhimg.com/t01ca7883d068762c74.png)](https://p2.ssl.qhimg.com/t01ca7883d068762c74.png)

[![](https://p0.ssl.qhimg.com/t01b9a514233c9613b6.png)](https://p0.ssl.qhimg.com/t01b9a514233c9613b6.png)

### Donot代码结构演变

Donot原始代码结构：

[![](https://p4.ssl.qhimg.com/t01afb03ad94388ef54.png)](https://p4.ssl.qhimg.com/t01afb03ad94388ef54.png)

Donot StealJob结构：

[![](https://p3.ssl.qhimg.com/t01199983b1beae31d0.png)](https://p3.ssl.qhimg.com/t01199983b1beae31d0.png)

本次Donot代码结构：

[![](https://p3.ssl.qhimg.com/t018292cc130bfc7708.png)](https://p3.ssl.qhimg.com/t018292cc130bfc7708.png)



## 总结

Donot APT组织（APT-C-35）自2017年被奇安信威胁情报中心披露后[2]，一直高度活跃，并且持续升级自己的武器库，从最初的EHDevel框架到yty框架，从PC端到移动端，都展示了该组织的高持续性与高技术性。奇安信威胁情报中心红雨滴团队将持续保持对该团伙的高度跟踪。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对此类攻击的精确检测。



## IOC

诱饵APK MD5：

497A67D28058A781681F20E32B7B3D6A

C2地址：

[mangasiso.top](https://www.virustotal.com/gui/search/behaviour_network%3A%22mangasiso.top%22)



## 参考链接
<li>
[https://ti.qianxin.com/blog/articles/capricorn-gang-uses-public-platform-to-distribute-c&amp;c-configuration-attacks/](https://ti.qianxin.com/blog/articles/capricorn-gang-uses-public-platform-to-distribute-c&amp;c-configuration-attacks/)<a name="_Ref18940200"></a>
</li>
<li>
[https://ti.qianxin.com/blog/articles/pakistan-targeted-apt-campaign/](https://ti.qianxin.com/blog/articles/pakistan-targeted-apt-campaign/)<a name="_Ref17821152"></a>
</li>
1. [https://ti.qianxin.com/blog/articles/donot-gang-mobile-new-attack-framework-tool-analysis/](https://ti.qianxin.com/blog/articles/donot-gang-mobile-new-attack-framework-tool-analysis/)
1. [https://ti.qianxin.com/blog/articles/stealjob-new-android-malware-used-by-donot-apt-group/](https://ti.qianxin.com/blog/articles/stealjob-new-android-malware-used-by-donot-apt-group/)