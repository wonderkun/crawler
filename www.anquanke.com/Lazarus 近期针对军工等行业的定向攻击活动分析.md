> 原文链接: https://www.anquanke.com//post/id/243392 


# Lazarus 近期针对军工等行业的定向攻击活动分析


                                阅读量   
                                **78262**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01caf0cf7ba3d85e90.jpg)](https://p1.ssl.qhimg.com/t01caf0cf7ba3d85e90.jpg)



## 一、概述

Lazarus组织为境外大型APT组织，是当前活跃度最高的APT组织之一。该组织实力强劲，其攻击目标涵盖政府、国防、研究中心、金融、能源、航空航天、运输、加密货币等诸多具有高经济价值的行业领域，并且擅长针对不同行业实施精准的社会工程学攻击。

微步情报局近期通过威胁狩猎系统监测到Lazarus组织针对国防军工行业的攻击活动，结合以往该组织针对军工行业的攻击活动，一并分析有如下发现：
1. 攻击者在此次攻击活动中冒充德国军工企业“莱茵金属”公司，以“工作要求”为主题向目标投递带有恶意宏的诱饵文档，Lazarus组织经常以目标所在行业头部企业的招聘信息为诱饵进行攻击活动；
1. 此外还以韩国军工企业“大宇造船”相关话题为诱饵进行攻击；
1. 诱饵文档中的恶意宏利用多阶段组件来执行恶意行为，最终加载执行远控模块，实现对目标主机的远程控制；
1. 攻击者将事先入侵的站点作为C2通信服务器，这在Lazarus以往的攻击活动中经常看到；
1. 结合该组织以往攻击活动样本分析，从执行流程上看具有高度相似性，但细节有一定程度变化，表明攻击者在持续开发并优化其攻击组件；
1. 微步情报局通过对相关样本、IP和域名的溯源分析，提取多条相关IOC用于威胁情报检测。微步在线威胁感知平台TDP、本地威胁情报管理平台TIP、威胁情报云API、主机威胁检测与响应平台OneEDR、互联网安全接入服务OneDNS等均已支持对此次攻击事件和团伙的检测。


## 二、详情

### **2.1 伪装“莱茵金属”公司工作要求**

诱饵文档以德国军工企业“莱茵金属”工作要求为主题，诱导用户启用宏。
<td class="ql-align-center" data-row="1">**诱饵文档名称**</td><td class="ql-align-center" data-row="1">**SHA256**</td><td class="ql-align-center" data-row="1">**创建时间**</td>
<td class="ql-align-center" data-row="2">rheinmetall_job_requirements.doc</td><td class="ql-align-center" data-row="2">e6dff9a5f74fff3a95e2dcb48b81b05af5cf5be73823d56c10eee80c8f17c845</td><td class="ql-align-center" data-row="2">2021-03-29 22:22:00</td>
<td class="ql-align-center" data-row="3">rheinmetall_job_requirements.doc</td><td class="ql-align-center" data-row="3">ffec6e6d4e314f64f5d31c62024252abde7f77acdd63991cb16923ff17828885</td><td class="ql-align-center" data-row="3">2021-03-29 07:22:00</td>

[![](https://p0.ssl.qhimg.com/t0170853d205bb69a4c.png)](https://p0.ssl.qhimg.com/t0170853d205bb69a4c.png)

图[1].含有宏的诱饵文档

莱茵金属公司（Rheinmetall）是德国一家战斗车辆武器配件及防卫产品制造商，现为德国国内最大的军工企业集团，业务遍及全世界。攻击者假冒该公司名义疑似为针对其所在行业公司进行钓鱼攻击。

当启用宏后，恶意宏将文档内容修改为看似正常的文字图片内容。

[![](https://p3.ssl.qhimg.com/t015654371aa86f1df0.png)](https://p3.ssl.qhimg.com/t015654371aa86f1df0.png)

图[2].启用宏后的诱饵文档

[![](https://p2.ssl.qhimg.com/t01dd444e0569aa7d01.png)](https://p2.ssl.qhimg.com/t01dd444e0569aa7d01.png)

图[3].执行流程图

### **2.2 以韩国企业“大宇造船”相关话题为诱饵**

攻击者以“大会决议草案”为主题作为诱饵文档进行攻击，诱导用户启用宏，文档内容大意是反对韩国政府出售“大宇造船厂”的相关内容。
<td class="ql-align-center" data-row="1">**文档名称**</td><td class="ql-align-center" data-row="1">결의대회초안.doc（大会决议草案）</td>
<td class="ql-align-center" data-row="2">**SHA256**</td><td class="ql-align-center" data-row="2">0193bd8bcbce9765dbecb288d46286bdc134261e4bff1f3c1f772d34fe4ec695</td>
<td class="ql-align-center" data-row="3">**作者信息**</td><td class="ql-align-center" data-row="3">William</td>
<td class="ql-align-center" data-row="4">**创建时间**</td><td class="ql-align-center" data-row="4">2021-03-31 00:01:00</td>

[![](https://p4.ssl.qhimg.com/t0154d23d801b76eeb0.png)](https://p4.ssl.qhimg.com/t0154d23d801b76eeb0.png)

图[4].启用宏前后

“大宇造船”是韩国三大造船公司之一，也是韩国的主要军工企业。攻击者以该公司相关话题为诱饵进行攻击，疑似针对相关行业人士进行定向攻击。

[![](https://p2.ssl.qhimg.com/t01c24a425a80125751.png)](https://p2.ssl.qhimg.com/t01c24a425a80125751.png)

图[5].执行流程图



## 三、样本分析

### **3.1 伪装“莱茵金属”公司工作要求样本**

从文档信息中可以看到其codepage为朝鲜语。

[![](https://p4.ssl.qhimg.com/t01a2f6d89ce7ef24c7.png)](https://p4.ssl.qhimg.com/t01a2f6d89ce7ef24c7.png)

图[6].诱饵文档的摘要信息

执行恶意宏后，在目标主机创建目录C:\Drivers，用于释放恶意模块。

[![](https://p5.ssl.qhimg.com/t01a0b8d1daa030fbdb.png)](https://p5.ssl.qhimg.com/t01a0b8d1daa030fbdb.png)

图[7].诱饵文档中的恶意宏

利用系统组件在此目录释放执行后门模块。
<td class="ql-align-center" data-row="1">**所释放文件**</td><td class="ql-align-center" data-row="1">**文件来源**</td>
<td class="ql-align-center" data-row="2">DriverGFE.tmp</td><td class="ql-align-center" data-row="2">保存Base64编码的PE文件数据的前2个字节</td>
<td class="ql-align-center" data-row="3">DriverGFXCoin.tmp</td><td class="ql-align-center" data-row="3">保存Base64编码的PE文件数据的后面数据</td>
<td class="ql-align-center" data-row="4">DriverUpdateFx.exe</td><td class="ql-align-center" data-row="4">由系统组件certutil.exe拷贝而来</td>
<td class="ql-align-center" data-row="5">DriverCPHS.tmp</td><td class="ql-align-center" data-row="5">使用cmd /b指令将DriverGFE.tmp和DriverGFXCoin.tmp合并，并将两者删除</td>
<td class="ql-align-center" data-row="6">DriverGFE.tmp（第二次）</td><td class="ql-align-center" data-row="6">使用DriverUpdateFx.exe（certutil.exe）解码，保存为DriverGFE.tmp，即最终的后门模块。</td>

之后利用系统组件mavinject.exe将恶意模块DriverGFE.tmp注入到系统进程explorer.exe中执行。
<td class="ql-align-center" data-row="1">mavinject.exe [PID] /injectrunning c:\Drivers\DriverGFX.tmp</td>

攻击者在以上的执行流程中使用多种系统组件来完成恶意行为，在一定程度上规避了一些安全产品的检测。

后门模块文件信息：
<td class="ql-align-center" data-row="1">**文件名称**</td><td class="ql-align-center" data-row="1">DriverGFX.tmp</td>
<td class="ql-align-center" data-row="2">**MD5**</td><td class="ql-align-center" data-row="2">1417f890248f193bb241f6b458ae4a97</td>
<td class="ql-align-center" data-row="3">**SHA1**</td><td class="ql-align-center" data-row="3">b2dfcbd8c3966ebed9275db7b14e359412db9963</td>
<td class="ql-align-center" data-row="4">**SHA256**</td><td class="ql-align-center" data-row="4">5c206b4dc2d3a25205176da9a1129c9f814c030a7bac245e3aaf7dd5d3ca4fbe</td>
<td class="ql-align-center" data-row="5">**文件格式**</td><td class="ql-align-center" data-row="5">PE64 DLL</td>
<td class="ql-align-center" data-row="6">**文件大小**</td><td class="ql-align-center" data-row="6">132608 字节 (129.50 KB)</td>
<td class="ql-align-center" data-row="7">**编译时间**</td><td class="ql-align-center" data-row="7">2021/03/29 22:20:32</td>

恶意模块被注入执行后，将会在主机设置计划任务以建立持久性机制。

[![](https://p4.ssl.qhimg.com/t012378b15de37df566.png)](https://p4.ssl.qhimg.com/t012378b15de37df566.png)

图[8].后门模块DllMain反汇编代码片段

将主机上设置的计划任务名称伪装成“Office Feature Updates Task”，调用系统组件rundll32.exe来执行后门模块的导出函数updateCache。

[![](https://p1.ssl.qhimg.com/t01a0d995c6d6c785fb.png)](https://p1.ssl.qhimg.com/t01a0d995c6d6c785fb.png)

图[9].在主机上建立的计划任务

在导出函数updateCache中，每隔10分钟从服务器https://wicall.ir/logo.png请求下载分发其他恶意模块数据。

[![](https://p2.ssl.qhimg.com/t016ac9e4fa9148c0fc.png)](https://p2.ssl.qhimg.com/t016ac9e4fa9148c0fc.png)

图[10].从服务器下载数据的后门模块

成功从服务器下载恶意模块数据后，将会在内存中展开执行。

[![](https://p1.ssl.qhimg.com/t01e563560c4d13ca72.png)](https://p1.ssl.qhimg.com/t01e563560c4d13ca72.png)

图[11].在内存中加载执行恶意模块

### **3.2 以韩国企业“大宇造船”相关话题为诱饵样本**

诱饵文档携带的恶意宏得到执行后，首先会弹出一个消息框，待用户点击之后才会继续执行流程，其使用Base64将所使用字符串解码，在主机Temp目录释放相关文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017ed6c0fb7cb749d0.png)

图[12].诱饵文档中的恶意宏

使用函数WIA_ConvertImage 将所释放的image003.png转换为存储恶意hta数据的image003.zip，之后使用系统组件mshta.exe来加载执行image003.zip。

[![](https://p2.ssl.qhimg.com/t01da47240cdf2ad0c0.png)](https://p2.ssl.qhimg.com/t01da47240cdf2ad0c0.png)

图[13].包含WIA_ConvertImage函数的恶意宏

[![](https://p0.ssl.qhimg.com/t011716e00ed11c6b54.png)](https://p0.ssl.qhimg.com/t011716e00ed11c6b54.png)

图[14].将image003.png转换为image003.zip

在image003.zip中，嵌入了经过混淆的javascript脚本代码，执行后解码出恶意模块数据保存到主机目录执行C:/Users/Public/Downloads/Winvoke.exe并运行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c820a8b6427bd894.png)

图[15].在javascript中释放木马模块

Winvoke.exe中添加了大量无效的系统调用以混淆执行流程，其通过下图中的算法以密钥“*$LvOAgHyZ)dM”从.KDATA区段中解密出核心RAT模块，并在内存中加载执行。

[![](https://p2.ssl.qhimg.com/t0150d91bb2a00038cf.png)](https://p2.ssl.qhimg.com/t0150d91bb2a00038cf.png)

图[16].Winvoke.exe中的异或解密算法

RAT模块执行后，首先创建互斥体“Microsoft32”，确保木马不会重复运行，之后解密出3组配置C2服务器，其中2个C2服务器配置是相同的。

http://www.jinjinpig.co.kr/Anyboard/skin/board.php

http://mail.namusoft.kr/jsp/user/eam/board.jsp

http://mail.namusoft.kr/jsp/user/eam/board.jsp

[![](https://p5.ssl.qhimg.com/t011db70d3137b622b2.png)](https://p5.ssl.qhimg.com/t011db70d3137b622b2.png)

图[17].RAT模块中配置的C2服务器

接着异或解密出lnk文件名“Visor 2010 Launcher.lnk ”，在主机开机启动目录生成lnk文件运行木马模块，以建立持久性机制。

[![](https://p2.ssl.qhimg.com/t01c43d09c9dd104169.png)](https://p2.ssl.qhimg.com/t01c43d09c9dd104169.png)

图[18].生成的lnk文件

之后与C2服务器以HTTP协议通信，通信数据使用RC4算法加密。

[![](https://p2.ssl.qhimg.com/t013c90723e46709de5.png)](https://p2.ssl.qhimg.com/t013c90723e46709de5.png)

图[19].以HTTP协议与C2服务器通信

可响应C2服务器以下指令：
<td class="ql-align-center" data-row="1">**指令代码**</td><td class="ql-align-center" data-row="1">**功能**</td>
<td class="ql-align-center" data-row="2">1111</td><td class="ql-align-center" data-row="2">更新与C2服务器通信间隔时间</td>
<td class="ql-align-center" data-row="3">1234</td><td class="ql-align-center" data-row="3">创建线程执行Shellcode代码</td>
<td class="ql-align-center" data-row="4">3333</td><td class="ql-align-center" data-row="4">退出并卸载木马</td>
<td class="ql-align-center" data-row="5">4444</td><td class="ql-align-center" data-row="5">检查指定服务器端口是否可连接</td>
<td class="ql-align-center" data-row="6">8877</td><td class="ql-align-center" data-row="6">下载文件</td>
<td class="ql-align-center" data-row="7">8888</td><td class="ql-align-center" data-row="7">下载并执行文件</td>
<td class="ql-align-center" data-row="8">9876</td><td class="ql-align-center" data-row="8">退出木马进程</td>
<td class="ql-align-center" data-row="9">9999</td><td class="ql-align-center" data-row="9">CmdShell</td>

每个指令执行完毕后会有Success、FAIL或执行结果作为回显数据，使用RC4加密后，伪装成文件类型数据头(test.gif)，回传给C2服务器。

[![](https://p3.ssl.qhimg.com/t013c69fd859e9d990c.png)](https://p3.ssl.qhimg.com/t013c69fd859e9d990c.png)

图[20].向C2服务器回传数据

此外，我们还看到一些同类型的诱饵文档样本，虽然从文档内容上来看没有明确的指向性，但其作者信息、文档创建时间、嵌入的恶意宏以及最终执行的RAT模块均与上述样本类似，属同源样本，推测为针对企业特定人员攻击。
<td class="ql-align-center" data-row="1">**文档名称**</td><td class="ql-align-center" data-row="1">**SHA256**</td><td class="ql-align-center" data-row="1">**作者信息**</td><td class="ql-align-center" data-row="1">**创建时间**</td>
<td class="ql-align-center" data-row="2">참가신청서양식.doc</td><td class="ql-align-center" data-row="2">（报名表格式）</td><td class="ql-align-center" data-row="2">f1eed93e555a0a33c7fef74084a6f8d06a92079e9f57114f523353d877226d72</td><td class="ql-align-center" data-row="2">William</td><td class="ql-align-center" data-row="2">2021-03-31 00:01:00</td>
<td class="ql-align-center" data-row="3">생활비지급.doc</td><td class="ql-align-center" data-row="3">（生活费支付）</td><td class="ql-align-center" data-row="3">79e15cc02c6359cdb84885f6b84facbf91f6df1254551750dd642ff96998db35</td><td class="ql-align-center" data-row="3">William</td><td class="ql-align-center" data-row="3">2021-04-18 23:11:00</td>
<td class="ql-align-center" data-row="4">test3.doc</td><td class="ql-align-center" data-row="4">a6ed3fe39d0956182c0ba9b57966cb8ae84ea029aa8d726f5bef9e7637f549f8</td><td class="ql-align-center" data-row="4">William</td><td class="ql-align-center" data-row="4">2021-04-18 23:11:00</td>

这些样本以“报名表格式”、“生活费支付”、“简历”等相关内容为诱饵进行攻击，其整体执行流程与上述样本相似。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014dbb0fc76b0ded2a.png)

图[21].风格一致的诱饵文档



## 四、关联分析

Lazarus擅长使用社会工程学方案进行攻击，在去年曾针对航空企业进行过以“DreamJob”为名的攻击活动。该活动与冒充“莱茵金属”公司所使用的社会工程学方案如出一辙，都是向目标发送特定行业公司的职位说明相关诱饵文档进行攻击。

在去年4月份，该组织曾以美国军工企业“诺思罗普·格鲁曼”（Northrop Grumman）和“通用电气”相关工作岗位信息作为诱饵针对军工企业进行攻击。
<td class="ql-align-center" data-row="1">**诱饵文档文件名**</td><td class="ql-align-center" data-row="1">**SHA256**</td>
<td class="ql-align-center" data-row="2">Northrop Grumman.doc</td><td class="ql-align-center" data-row="2">f188eec1268fd49bdc7375fc5b77ded657c150875fede1a4d797f818d2514e88</td>
<td class="ql-align-center" data-row="3">Northrop Grumman.doc</td><td class="ql-align-center" data-row="3">e2c3913d7e1dee8eae919b8852baf20cf8572852a033fc33eeed2c075a84edd0</td>
<td class="ql-align-center" data-row="4">(HR)2020-2021 General Dynamics Job Information and Opportunities_GD-HR-202011839432.pdf</td><td class="ql-align-center" data-row="4">bdf9fffe1c9ffbeec307c536a2369eefb2a2c5d70f33a1646a15d6d152c2a6fa</td>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0180dd5a55bc90db27.png)

图[22].诱饵文档截图

当时所使用的恶意宏与此次攻击活动中出现的恶意宏有较大区别，但两者均遵循了同一个规则，即使用多种系统组件进行打包、解包、执行等恶意操作，以尽可能的规避一些安全产品的检测。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f535de5c54a091a3.png)

图[23].使用多种系统组件从C2服务器下载恶意载荷

Lazarus还经常批量入侵站点，将失陷站点作为C2通信服务器，这在Lazarus大多数攻击活动中都曾出现过。在去年的针对军工企业的攻击活动中，就曾入侵一家疑似在线教育网站作为C2通信服务器，其管理后台存在弱口令缺陷，这可能是Lazarus可以成功入侵的原因之一。

[![](https://p2.ssl.qhimg.com/t014ab3ef0cc1663589.png)](https://p2.ssl.qhimg.com/t014ab3ef0cc1663589.png)

图[24].被 Lazarus 入侵的站点存在弱口令缺陷

攻击者在此次攻击活动中使用的RAT模块与多起以往攻击活动中的样本具有关联性，例如Lazarus经常在RAT模块中配置3组C2服务器（即使重复），使用特定算法解密。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0194fb48d8599a5936.png)

图[25].RAT模块中配置的C2服务器

以及高度相似的内存加载PE模块部分。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013b5ebb2651967a3d.png)

图[26].内存加载PE模块反汇编代码对比



## 五、结论

Lazarus APT组织一直保持着很高的活跃度，窃取高价值情报和获取经济利益是其主要攻击目的，为了提升攻击有效性，Lazarus一直在持续开发并改进其工具集以及军火库。

利用社会工程学方案攻击是Lazarus的显著特征之一，在近两年的时间内，该组织进行了多起类似方案的攻击活动，譬如“DreamJob”、“针对安全研究人员的攻击”等。在这些攻击活动中，Lazarus展现了其极强的耐心以及行动保障能力。社会工程学攻击将会在以后的攻击活动中越来越突出，微步情报局会对相关攻击活动持续进行跟踪，及时发现安全威胁并快速响应处置。

关注“微步在线研究响应中心” 公众号可查看完整文章，公众号内回复“la”，可获取完整 PDF（含 IOC） 版报告 。

### 附录-微步情报局

微步情报局由精通木马分析与取证技术、Web 攻击技术、溯源技术、大数据、AI 等安 全技术的资深专家组成。
