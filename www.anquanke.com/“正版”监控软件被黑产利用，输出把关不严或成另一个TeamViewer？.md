> 原文链接: https://www.anquanke.com//post/id/197266 


# “正版”监控软件被黑产利用，输出把关不严或成另一个TeamViewer？


                                阅读量   
                                **1100794**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t018a2875b87dd2ea2e.png)](https://p3.ssl.qhimg.com/t018a2875b87dd2ea2e.png)



## 概述

近日，奇安信病毒响应中心在日常跟踪黑产团伙过程中，发现了一个利用正规监控软件窃取用户信息，甚至监控聊天记录的黑客团伙，由于正规监控软件带有数字签名，杀软一般不会对其进行查杀，从而达到免杀的效果。

样本在执行过程中会在从远程服务器下载远控客户端安装程序，通过消息操作实现客户端自动化安装，安装成功后主进程则会连接远程服务器。可以实现屏幕监控、流量监控、屏幕录像、监控上网行为、软件管理、访问控制、文档备份、下发文件等复杂功能，同时其释放的驱动注册了进程回调来保护主进程不被结束。

基于奇安信的多维度大数据关联分析，我们已经发现国内有用户中招，为了防止危害进一步扩散，我们对该黑产团伙进行了披露，并给出解决方案。



## 样本分析
<td style="width: 94.95pt;" valign="top">**文件名**</td><td style="width: 138.55pt;" valign="top">**MD5**</td><td style="width: 86.75pt;" valign="top">**编译时间**</td><td style="width: 94.05pt;" valign="top">**功能**</td>
<td style="width: 94.95pt;" valign="top">**大富豪累充5000资源.xls**</td><td style="width: 138.55pt;" valign="top">f6cd269ec61fb16e1a48cf2761698c6b</td><td style="width: 86.75pt;" valign="top">2019-08-08</td><td style="width: 94.05pt;" valign="top">可执行文件，从远程服务器下载服务端并安装</td>

样本由易语言编写，下载逻辑如下

[![](https://p4.ssl.qhimg.com/t018c29efec3f1dd1bb.png)](https://p4.ssl.qhimg.com/t018c29efec3f1dd1bb.png)

下载链接如下hXXp://154.223.144.182/setup_wid_caijy@foreign.exe，安装包名称较为特殊，初步怀疑为渠道包。

自动化安装逻辑

[![](https://p3.ssl.qhimg.com/t01f5afae6213accd97.png)](https://p3.ssl.qhimg.com/t01f5afae6213accd97.png)

安装包手动打开界面如下

[![](https://p5.ssl.qhimg.com/t014c5effda129d75e9.png)](https://p5.ssl.qhimg.com/t014c5effda129d75e9.png)

将相关文件释放到C:\Program Files\Common Files\NSEC目录下，由于NsecRTS.exe对该目录做了保护，普通权限下是观察不到有文件存在

[![](https://p3.ssl.qhimg.com/t01ed98d91d18614216.png)](https://p3.ssl.qhimg.com/t01ed98d91d18614216.png)

[![](https://p5.ssl.qhimg.com/t01a49dc4b6c380d133.png)](https://p5.ssl.qhimg.com/t01a49dc4b6c380d133.png)

NsecRTS.exe启动后会请求并解析[http://cloud.nsecsoft.com:8987/ndns/caijy@foreign](http://cloud.nsecsoft.com:8987/ndns/caijy@foreign)下的数据

[![](https://p3.ssl.qhimg.com/t0135491298b2b5b752.png)](https://p3.ssl.qhimg.com/t0135491298b2b5b752.png)

数据如下

[![](https://p4.ssl.qhimg.com/t015434d45bc73e7110.png)](https://p4.ssl.qhimg.com/t015434d45bc73e7110.png)

获取需要连接的IP地址，之后连接该IP的18987和28987端口，由于控制功能过多，这里我们只挑选其中几个做简单的介绍，不同的功能会使用不同的端口进行通讯。

实时截屏功能，每隔三秒截一次图并发送到主控端。图像保存在了C:\SmartSnap\日期\目录下，且受到保护，只能使用高权限软件查看

[![](https://p5.ssl.qhimg.com/t01208854cca61dc802.png)](https://p5.ssl.qhimg.com/t01208854cca61dc802.png)

[![](https://p4.ssl.qhimg.com/t01ed544dabf0db3c2e.png)](https://p4.ssl.qhimg.com/t01ed544dabf0db3c2e.png)

收集信息模块在PCinfo.dll中，向远程服务器上传非常详细的本机信息。硬件设备、系统账号、系统版本、磁盘大小等信息

[![](https://p5.ssl.qhimg.com/t0135e9ad194d0310c6.png)](https://p5.ssl.qhimg.com/t0135e9ad194d0310c6.png)

同时该远控的自我保护能力很强，其驱动模块（nFsFlt32.sys）创建了进程回调并注册minifilter，用于保护NsecRTS.exe进程不会被结束

[![](https://p5.ssl.qhimg.com/t01c55af9a4353af89d.png)](https://p5.ssl.qhimg.com/t01c55af9a4353af89d.png)

其他驱动模块还注册了关机回调，防删除

[![](https://p1.ssl.qhimg.com/t01cb612e70d638b41c.png)](https://p1.ssl.qhimg.com/t01cb612e70d638b41c.png)

结上所述，如果想要彻底删除该远控需要卸载与其相关的驱动模块或者清除内核回调之后结束进程删除文件。

上述分析的文件都带有数字签名

[![](https://p5.ssl.qhimg.com/t019edf494c73e50801.png)](https://p5.ssl.qhimg.com/t019edf494c73e50801.png)

签名文件显示为“山东安在信息技术有限责任公司”，访问其官网发现是一家专注于终端安全管理系统的信息安全公司。旗下主打ping32终端管理软件，我们猜测该样本应该是ping32终端管理软件的客户端。

通过搜索引擎搜索，我们发现早在2019年4-5月份时就有国内用户在某安全社区中反馈这个问题

[![](https://p0.ssl.qhimg.com/t0193b388a992fb6602.png)](https://p0.ssl.qhimg.com/t0193b388a992fb6602.png)

由于相关文件被隐藏，样本上传不上来，导致问题一直没有受到重视。

[![](https://p3.ssl.qhimg.com/t0185805206707cebfa.png)](https://p3.ssl.qhimg.com/t0185805206707cebfa.png)



## 关联分析

对154.223.144.182进行关联分析，发现了一批同源样本
<td style="width: 94.95pt;" valign="top">**文件名**</td><td style="width: 138.55pt;" valign="top">**MD5**</td><td style="width: 86.75pt;" valign="top">**编译时间**</td><td style="width: 94.05pt;" valign="top">**编译器**</td>
<td style="width: 94.95pt;" valign="top">**邮件群发V5.3_破解版 (1)**</td><td style="width: 138.55pt;" valign="top">2c9635988357cc241ebd7372ac4f3f33</td><td style="width: 86.75pt;" valign="top">2019-08-08 16:02:58</td><td style="width: 94.05pt;" valign="top">E语言</td>
<td style="width: 94.95pt;" valign="top">** **</td><td style="width: 138.55pt;" valign="top">72151487badd30f7939734acf9db2d8c</td><td style="width: 86.75pt;" valign="top">2019-04-27 20:03:27</td><td style="width: 94.05pt;" valign="top">E语言</td>
<td style="width: 94.95pt;" valign="top">**2019.11.28.exe**</td><td style="width: 138.55pt;" valign="top">648071200c452d4c71f35d439fdc08a9</td><td style="width: 86.75pt;" valign="top">1972-12-25 05:33:23</td><td style="width: 94.05pt;" valign="top">E语言</td>
<td style="width: 94.95pt;" valign="top">**昨晚约的高一学妹居然还是处MP4ks.exe**</td><td style="width: 138.55pt;" valign="top">9d6960afc0c2e31ba9b71a891e72a5d2</td><td style="width: 86.75pt;" valign="top">2019-10-09 16:09:05</td><td style="width: 94.05pt;" valign="top">E语言</td>
<td style="width: 94.95pt;" valign="top">**杏彩国际.exe**</td><td style="width: 138.55pt;" valign="top">c55b93f8c062c0adb7595bd07906aca8</td><td style="width: 86.75pt;" valign="top">2019-10-09 15:46:43</td><td style="width: 94.05pt;" valign="top">E语言</td>
<td style="width: 94.95pt;" valign="top">** **</td><td style="width: 138.55pt;" valign="top">3d9580f52c57ed907a551ca0620ba749</td><td style="width: 86.75pt;" valign="top">2019-07-19 14:28:39</td><td style="width: 94.05pt;" valign="top">E语言</td>
<td style="width: 94.95pt;" valign="top">** **</td><td style="width: 138.55pt;" valign="top">039883d4442527a98ae56971a28922fc</td><td style="width: 86.75pt;" valign="top">1992-06-19 22:22:17</td><td style="width: 94.05pt;" valign="top">Delf</td>
<td style="width: 94.95pt;" valign="top">** **</td><td style="width: 138.55pt;" valign="top">1b619b1e24c8e16e0d21585c1ca42b6c</td><td style="width: 86.75pt;" valign="top">2019-10-07 17:34:32</td><td style="width: 94.05pt;" valign="top">E语言</td>
<td style="width: 94.95pt;" valign="top">** **</td><td style="width: 138.55pt;" valign="top">18418c5f02c68716ea1437835b43ad9c</td><td style="width: 86.75pt;" valign="top">2019-08-08 16:01:17</td><td style="width: 94.05pt;" valign="top">E语言</td>
<td style="width: 94.95pt;" valign="top">**激活码.exe**</td><td style="width: 138.55pt;" valign="top">547c64aa1509c82287f19ec03afaf9ec</td><td style="width: 86.75pt;" valign="top">2019-07-16 19:17:45</td><td style="width: 94.05pt;" valign="top">E语言</td>

通过对下载的文件名和行为进行分类可以分为两大类

@foreign类样本，样本名称都带“@foreign”字符串。
<td style="width: 417.7pt;" valign="top">**ITW**</td>
<td style="width: 417.7pt;" valign="top">**hxxp://154.223.144.182/setup_wid_caijy@foreign.exe**</td>
<td style="width: 417.7pt;" valign="top">**hxxp://154.223.144.182/setup_wid_lanhai@foreign.exe**</td>
<td style="width: 417.7pt;" valign="top">**hxxp://154.223.144.182/setup_wid_caisjt@foreign.exe**</td>

IP类样本，样本名称中直接包含IP地址
<td style="width: 417.7pt;" valign="top">**ITW**</td>
<td style="width: 417.7pt;" valign="top">**hxxp://154.223.144.182/setup_ip_47.75.159.1.exe**</td>
<td style="width: 417.7pt;" valign="top">**hxxp://154.223.144.182/setup_ip_47.52.210.77.exe**</td>

之所以要这么分类是因为这两类样本的行为细节上略有不同，区别在于：

@foreign类的样本在连接远程服务器时会先向cloud.nsecsoft.com安在官网的子域名发起请求解析返回数据，从而得到远程服务器的地址，请求的后缀与安装包的名称有关

[![](https://p4.ssl.qhimg.com/t014c3ec2a4f5d53708.png)](https://p4.ssl.qhimg.com/t014c3ec2a4f5d53708.png)

奇安信监控到的访问量如下

[![](https://p1.ssl.qhimg.com/t018cefc8fd75f03413.png)](https://p1.ssl.qhimg.com/t018cefc8fd75f03413.png)

而IP类的样本则没有这个行为，会直接连接内置的IP地址。

**故我们推测@foreign类的样本应为安在公司内部渠道包或者给特定用户定制的功能，**

除此之外，该团伙还会使用第三只眼监控软件
<td style="width: 94.95pt;" valign="top">**文件名**</td><td style="width: 138.55pt;" valign="top">**MD5**</td><td style="width: 86.75pt;" valign="top">**编译时间**</td><td style="width: 94.05pt;" valign="top">**编译器**</td>
<td style="width: 94.95pt;" valign="top">**最新APP每天更新：“AV，小说，黄漫，直播，乱伦，SM，制服，.com**</td><td style="width: 138.55pt;" valign="top">a89785a82157ff6c5213d5f01d17a4c3</td><td style="width: 86.75pt;" valign="top">2019-09-12 14:50:07</td><td style="width: 94.05pt;" valign="top">E语言</td>

请求的URL：

hxxp://154.223.144.182/562299111a.exe

手动打开界面如下

[![](https://p4.ssl.qhimg.com/t01c3592911688641bb.png)](https://p4.ssl.qhimg.com/t01c3592911688641bb.png)

为了进一步探寻起源，研判利用正规监控软件这一方案的可行性，我们以“产品经理”的身份联系了山东安在公司的客服。

[![](https://p1.ssl.qhimg.com/t016a238ab779b30463.png)](https://p1.ssl.qhimg.com/t016a238ab779b30463.png)

经过一番询问，需要我们提供公司名称、联系方式和姓名才会给我们发软件的下载地址，我们只提供了虚构的姓氏和公司名就得到了软件的下载地址

[![](https://p1.ssl.qhimg.com/t018a840b9075ffac1b.png)](https://p1.ssl.qhimg.com/t018a840b9075ffac1b.png)

可见，客服咨询这一块的步骤形同摆设，客服并不会对测试软件的人的信息进行核实。

软件启动时会提示输入许可证或者进行试用，试用时间为7天。试用注册的过程中唯一重点就是要输入手机的验证码，其余项可以随意填写，手机号支持中国、美国、新加坡、日本。**经过我们测试，同一个手机号竟然可以在不同的机器上重复注册**。

[![](https://p2.ssl.qhimg.com/t0167e04b47fa603807.png)](https://p2.ssl.qhimg.com/t0167e04b47fa603807.png)

注册成功之后弹出主控端界面。该系统比国内黑产常用的Ghost、大灰狼以及其相关变种的功能多出不少。

[![](https://p4.ssl.qhimg.com/t017cc568571ca3a3be.png)](https://p4.ssl.qhimg.com/t017cc568571ca3a3be.png)

生成客户端，客户端名称：“setup_ip_192.168.13.128.exe”属于上述的IP类样本，从侧面印证了@foreign类的样本的确是特殊渠道生成的。具体特殊在哪或许只有安在公司自己知道。

综上所述，黑产得到ping32软件后可以将其破解自己无限使用，也可以通过地下论坛购买手机号和对应的验证码进行注册试用，有钱的话也可以将其买下来，都可以达到持续使用的效果。



## 总结

之前我们也披露过使用TeamView作为远控来收集用户信息的黑产团伙“零零狗”，可见出于经济上的考虑，大部分的黑产团伙都会选择开源或者现有的远程控制工具，只有少数的黑产团伙自成体系，选择购买或者制作免杀效果较好的软件进行攻击活动。同样的在企业这一方面，我们通过简单的问答就可以获取到这种内核级别的监控软件，同时在注册时存在一些小“Bug”，可以被黑产团伙利用，这从侧面反映了企业有些环节的不足和敷衍、相关人员安全意识淡薄。

奇安信病毒响应中心提醒用户不要点击来源不明的邮件和可执行文件，同时提高个人的安全意识，从而可以防止用户隐私信息被盗取的风险，奇安信病毒响应中心会持续对黑产团伙进行挖掘和追踪。

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对该家族的精确检测。



## IOC

MD5：

f6cd269ec61fb16e1a48cf2761698c6b

2c9635988357cc241ebd7372ac4f3f33

648071200c452d4c71f35d439fdc08a9

9d6960afc0c2e31ba9b71a891e72a5d2

c55b93f8c062c0adb7595bd07906aca8

3d9580f52c57ed907a551ca0620ba749

039883d4442527a98ae56971a28922fc

1b619b1e24c8e16e0d21585c1ca42b6c

18418c5f02c68716ea1437835b43ad9c

547c64aa1509c82287f19ec03afaf9ec

a89785a82157ff6c5213d5f01d17a4c3

Host：

154.223.144.182

C2：

103.100.210.28:18987

103.100.210.28:28987

47.244.201.71:18987

47.244.201.71:28987

47.56.189.69:18987

47.56.189.69:28987

47.75.159.1:18987

47.75.159.1:28987

47.52.210.77:18987

47.52.210.77:28987
