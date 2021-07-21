> 原文链接: https://www.anquanke.com//post/id/241811 


# 一路向北：Konni APT组织以“朝鲜局势”相关主题为诱饵对俄进行持续定向攻击活动


                                阅读量   
                                **146331**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01eac4d19531e13476.jpg)](https://p5.ssl.qhimg.com/t01eac4d19531e13476.jpg)



## 一、概述

Konni APT组织据悉由特定政府提供支持，自2014年以来一直持续活动。该组织经常使用鱼叉式网络钓鱼攻击手法，且经常使用与朝鲜相关的主题或社会热点作为诱饵，吸引用户查看并执行附件。

微步情报局近期通过威胁狩猎系统捕获到Konni APT组织利用朝鲜局势相关话题针对俄罗斯方向的攻击活动，分析有如下发现：
1. 攻击者以“关于制裁对朝鲜局势的影响”和“解决朝鲜危机的建议”等相关热点话题为诱饵进行鱼叉攻击。
1. 所投递恶意文档语言均为俄语，但部分文档编辑环境为朝鲜语，结合该组织的地缘因素分析，研判主要攻击目标为俄罗斯方向相关组织机构。
1. 文档中携带的恶意模块将会从服务器下载多阶段恶意载荷，最终加载执行后门远控模块，实现对目标主机的远程控制。
1. 根据多维度关联信息显示，本次攻击活动延续了该组织以往的攻击手法。
1. 微步在线通过对相关样本、IP和域名的溯源分析，提取多条相关 IOC ，可用于威胁情报检测。微步在线威胁感知平台TDP、本地威胁情报管理平台TIP、威胁情报云API、互联网安全接入服务 OneDNS 等均已支持对此次攻击事件和团伙的检测。


## 二、详情

在攻击者投递的恶意文档中，可以看到有文档的创建作者为SmallPig，这与攻击者所使用的C2服务器中的关键字“[dragon-pig](https://www.virustotal.com/gui/url/f740b4c99f83c48edbd3cda5afcdeaa8632f037cfa564756ba2aae5cd815001f)”、“[little-dragon](https://www.virustotal.com/gui/url/1995bf109577e292897a5e59bae78ef13642260379ff448637b8cbae72d049cf)”等类似，表示攻击者做了一定准备工作，并且疑似有统一的行动策划，两个文档的最后修改者均为PILOT，且有文档的代码页语言为朝鲜语。
<td class="ql-align-center" data-row="1">**文档名称**</td><td class="ql-align-center" data-row="1">**MD5**</td><td class="ql-align-center" data-row="1">**作者信息**</td><td class="ql-align-center" data-row="1">**代码页**</td>
<td class="ql-align-center" data-row="2">Овлиянии санкций на ситуацию в КНДР.doc（关于制裁对朝鲜局势的影响）</td><td class="ql-align-center" data-row="2">7b13aa205a32cccb8d149e72cadeaeb2</td><td class="ql-align-center" data-row="2">PILOT</td><td class="ql-align-center" data-row="2">俄语</td>
<td class="ql-align-center" data-row="3">Предложения по урегулированию Корейского кризиса.doc（解决朝鲜危机的建议）</td><td class="ql-align-center" data-row="3">61594306ad5492e1d61f4f42387066a7</td><td class="ql-align-center" data-row="3">SmallPig、PILOT</td><td class="ql-align-center" data-row="3">朝鲜语</td>

将文档文字颜色设置为难以阅读的灰色是该组织的特点之一，一旦用户启用宏后，会在携带的恶意宏中将文档的文字颜色设置为易于阅读的黑色，以迷惑用户。Konni一直在使用这种方法，可见对于诱导用户启用宏非常有效果。

[![](https://p3.ssl.qhimg.com/t016f7e9fe85ee6d78a.png)](https://p3.ssl.qhimg.com/t016f7e9fe85ee6d78a.png)

图1.启用宏前后对比

[![](https://p3.ssl.qhimg.com/t01103420f97b0ce212.png)](https://p3.ssl.qhimg.com/t01103420f97b0ce212.png)

图2.执行流程图



## 三、样本分析

在其中一份文档携带的恶意宏中，仅有3行脚本代码，主要功能为从自身文档文件中定位到js脚本代码写入到主机目录，之后再通过系统程序wscript来调用执行zx.js，同时在VBA中会将文档的文字颜色设置为黑色。

[![](https://p2.ssl.qhimg.com/t0142ee297889c84b59.png)](https://p2.ssl.qhimg.com/t0142ee297889c84b59.png)

图3.文档中的恶意宏

在文档文件的尾部，可以看到以“try”关键字起始的脚本代码，这些代码将会通过VBA写入到主机目录%USERPROFILE%\zx.js，主要功能为从服务器下载脚本代码，使用eval函数来执行。URL：http://dragon-pig.onlinewebshop.net/KB2999379.txt

[![](https://p4.ssl.qhimg.com/t01571b4aa54c6e864d.png)](https://p4.ssl.qhimg.com/t01571b4aa54c6e864d.png)

图4.文档中嵌入的脚本代码

在KB2999379.txt中，根据当前主机系统x86或x64分别从服务器下载对应版本的木马，保存到文件zx.tmp，再使用expand命令来解压，之后调用执行解压出来的zx.bat。

[![](https://p4.ssl.qhimg.com/t01d898e4e106f7f667.png)](https://p4.ssl.qhimg.com/t01d898e4e106f7f667.png)

图5. KB2999379.txt中的代码片段

接着在zw.bat中，执行解压出来的mslwer.dll用来绕过UAC，并调用执行install.bat。

[![](https://p0.ssl.qhimg.com/t0102858f4045e2bf98.png)](https://p0.ssl.qhimg.com/t0102858f4045e2bf98.png)

图6. zw.bat中的脚本代码片段

install.bat得到执行后，负责木马模块的持久化，其将木马模块mssvps.dll和木马配置文件mssvps.ini移动到系统目录%windir%\System32，在主机上安装名为“ComSysApp”的服务来启动木马模块mssvps.dll，实现持久化。

[![](https://p0.ssl.qhimg.com/t0142a8626b4e587f97.png)](https://p0.ssl.qhimg.com/t0142a8626b4e587f97.png)

图7. install.bat中的脚本代码片段

木马模块mssvps.dll中的字符串普遍为加密方式存储，以服务方式启动后，将会获取主机名称加密后作为感染ID。

注册表中HKEY_CURRENT_USER\Console中的MaxElapsed项表示木马更新C2配置的最大间隔时间，默认为2个小时，而MinElapsed项表示木马首次启动或者由于断网需要等待连接的时间，如果没有找到对应项，则会按照最小60秒来等待，等待结束后将会检查网络是否可连通，如果非连通状态将会继续等待。

[![](https://p3.ssl.qhimg.com/t01beee65e4cb4fab71.png)](https://p3.ssl.qhimg.com/t01beee65e4cb4fab71.png)

图8.检查网络连通性反汇编代码片段

等待结束后，将会分两种方式从配置文件中取出C2地址。
1. 从dat文件中直接取出C2地址；
1. 如果未能从dat文件中取到C2地址，则将会从mssvps.ini文件取出地址，与“/KB3000061.dat”拼接，下载之后从该dat文件中取出C2地址。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01863b882eab9141e0.png)

图9.使用UrlDownloadToFile从服务器下载文件KB3000061.dat

成功取出C2地址后，木马会先后两次调用cmd命令systeminfo和tasklisk来获取系统信息和主机进程列表，之后分别将上述数据以文件形式上传至C2服务器，以供攻击者进行环境侦察。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e6b4262b48e8a4e8.png)

图10.在WireShark中拦截到的上传系统信息数据包

在上传函数中，木马会判断上传文件类型，如果是以cab、zip、rar结尾的文件将会直接上传，否则将会使用cmd命令makecab来将目标文件压缩为cab文件再上传，两种方式均将文件转存为temp文件加密后再进行上传。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0137b29cfbe77d278f.png)

图11.上传函数中使用makecab命令压缩文件

此外，木马每次进行网络访问前，将会清除C2服务器相关的缓存。

[![](https://p2.ssl.qhimg.com/t01c5ef5bfc43edfb3c.png)](https://p2.ssl.qhimg.com/t01c5ef5bfc43edfb3c.png)

图12. 清除C2服务器相关缓存

将主机信息上传至C2服务器后，以参数值prefix =cc `{`index`}`为标识（index从0开始），依次循环从服务器取出攻击者所预设的远程指令来执行，直到将所有指令执行完毕。
<td class="ql-align-center" data-row="1">**host**</td><td class="ql-align-center" data-row="1">little-dragon.mypressonline.com</td><td class="ql-align-center" data-row="1">C2域名</td>
<td class="ql-align-center" data-row="2">**path**</td><td class="ql-align-center" data-row="2">dn.php</td><td class="ql-align-center" data-row="2">指令路径</td>
<td class="ql-align-center" data-row="3">**参数1**</td><td class="ql-align-center" data-row="3">client_id</td><td class="ql-align-center" data-row="3">主机ID（加密的主机名）</td>
<td class="ql-align-center" data-row="4">**参数2**</td><td class="ql-align-center" data-row="4">prefix</td><td class="ql-align-center" data-row="4">cc `{`index`}`,index从0起始</td>

之后再每隔10秒从服务器取出远程指令执行，截至分析时C2服务器已经无法正常连接。
<td class="ql-align-center" data-row="1">**host**</td><td class="ql-align-center" data-row="1">little-dragon.mypressonline.com</td><td class="ql-align-center" data-row="1">C2域名</td>
<td class="ql-align-center" data-row="2">**path**</td><td class="ql-align-center" data-row="2">dn.php</td><td class="ql-align-center" data-row="2">指令路径</td>
<td class="ql-align-center" data-row="3">**参数1**</td><td class="ql-align-center" data-row="3">client_id</td><td class="ql-align-center" data-row="3">主机ID（加密的主机名）</td>
<td class="ql-align-center" data-row="4">**参数2**</td><td class="ql-align-center" data-row="4">prefix</td><td class="ql-align-center" data-row="4">tt（固定值）</td>

该后门木马与以往Konni组织所使用的木马类似，可响应C2服务器远程指令包括CmdShell、文件上传/下载、更新C2配置文件、创建指定进程等，指令执行完毕后将会把结果暂存到主机temp目录，以文件形式加密上传至C2服务器，最终实现对目标计算机的远程控制。

[![](https://p3.ssl.qhimg.com/t01815df1b759f4e42a.png)](https://p3.ssl.qhimg.com/t01815df1b759f4e42a.png)

图13.响应远程指令反汇编代码片段

在另一个样本携带的恶意宏中，将Donwloader模块释放到主机目录%USERPROFILE%\pp.exe，执行时传入参数“bALWAoNAuAAkAV0A2mLpAX1A9zLjAXvAMzLtAXRA2zLfAXhAbNLCAXRA9mLCAX0A4zLWAXzAcNLYAX8A9zADAXRAcNLWAA==”，该参数为经过加密的C2服务器地址http://baboivan.scienceontheweb.net。

[![](https://p0.ssl.qhimg.com/t0126263b176b9275d0.png)](https://p0.ssl.qhimg.com/t0126263b176b9275d0.png)

图14. 文档中携带的恶意宏

与上面样本执行流程类似，同样通过判断系统32位或64位来下载指定版本木马，保存到目录% USERPROFILE%，之后再执行解压，最后执行解压出来的pp.bat，遗憾的是，分析时服务器已经无法正常连接，导致未能捕获到下阶段样本，但根据上下文信息，可以推断与上面样本使用的木马应该为同一类型。



## 四、关联分析

攻击者在此次攻击活动中使用的C2服务器均为动态域名，该组织经常使用此类域名作为C2服务器。

[![](https://p1.ssl.qhimg.com/t01d805ba4bf0167655.png)](https://p1.ssl.qhimg.com/t01d805ba4bf0167655.png)

图15. 攻击者使用的C2服务器

经过与该组织以往的攻击样本对比，发现此次攻击者在此次攻击活动中基本延续了以往的攻击手法，例如基本一致的字符串解密函数（左边为以往攻击活动，右边为本次攻击活动）。

[![](https://p5.ssl.qhimg.com/t01080ac0c9b518266e.png)](https://p5.ssl.qhimg.com/t01080ac0c9b518266e.png)

图16. 字符串解密函数对比

以及Downloader模块中如出一辙的执行流程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01198ce3eec2897684.png)

图17. 执行流程对比



## 五、结论

由此，我们判断此次攻击活动为Konni APT组织以往攻击活动的延续，其一直在对俄罗斯相关组织机构进行有针对性的攻击活动，并且在最近的攻击活动中复用了以往的攻击手法。

Konni组织惯用朝鲜相关热点话题为诱饵进行攻击活动，利用社会工程学技术针对特定组织机构实施各种APT攻击，且极具针对性，微步情报局将持续跟踪并分析该组织动向。

关注“微步在线研究响应中心” 公众号可查看完整文章，公众号内回复“KN”，可获取完整 PDF（含 IOC） 版报告 。

### **附录-微步情报局**

微步情报局由精通木马分析与取证技术、Web攻击技术、溯源技术、大数据、AI等安全技术的资深专家组成，对微步在线每天新增的百万级样本文件、千万级URL、PDNS、Whois数据进行实时的自动化分析、同源分析及大数据关联分析。
