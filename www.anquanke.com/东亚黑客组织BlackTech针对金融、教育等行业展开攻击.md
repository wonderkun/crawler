> 原文链接: https://www.anquanke.com//post/id/262276 


# 东亚黑客组织BlackTech针对金融、教育等行业展开攻击


                                阅读量   
                                **116589**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0199f993a8e3599c84.jpg)](https://p3.ssl.qhimg.com/t0199f993a8e3599c84.jpg)



## 一、概述

BlackTech是一个主要针对东亚地区的商业间谍组织，其活动可追溯至2010年，其攻击的目标行业包含金融、政府、科技、教育、体育和文化等，其目的是窃取机密数据（各种账密、机密文件等）和获取经济利益。该组织主要使用鱼叉式网络钓鱼邮件进行攻击，惯用Plead、TSCookie、Gh0st、Bifrose等木马。

近期，微步情报局通过微步在线威胁情报云监测到BlackTech在多次攻击活动中使用的后门木马，包含Windows版本和Linux版本，多数杀毒引擎较难查杀，经过分析有如下发现：
1. BlackTech在近期的攻击活动中使用了多数杀毒引擎较难查杀的后门木马，这表明该组织的武器库在持续丰富和变化。
1. BlackTech在近期的攻击活动中涉及的目标为金融、教育等行业。
1. 在针对Windows平台的攻击中，BlackTech使用的后门木马是由Gh0st源码修改而来，具备RAT能力。
1. 在针对Linux平台的攻击中，BlackTech使用的后门木马有两种类型，一种是Bifrose后门木马；另一种是用Python编写打包成的木马具备上传文件、下载文件、执行命令等功能。
1. 微步在线通过对相关样本、IP 和域名的溯源分析，提取多条相关 IOC ，可用于威胁情报检测。微步在线威胁感知平台 TDP 、本地威胁情报管理平台 TIP 、威胁情报云 API 、互联网安全接入服务 OneDNS 、主机威胁检测与响应平台 OneEDR 、威胁捕捉与诱骗系统 HFish 蜜罐等均已支持对此次攻击事件和团伙的检测。


## 二、详情

微步情报局监测到东亚黑客组织BlackTech近期攻击活动频繁，攻击目标包括中国地区的互联网金融、互联网教育等行业。根据近期捕获的BlackTech组织使用的后门木马，微步情报局发现该组织的武器库在持续丰富和变化，在Windows平台上使用由Gh0st源码修改而来的后门木马，在Linux平台上使用Bifrose后门木马，多数杀毒引擎较难查杀。另外在Linux平台还使用Python编写打包的后门木马。而在IT资产方面，BlackTech组织依旧保留了之前的特点，即经常租用中国、日本等地的服务器作为C&amp;C服务器，在近期攻击活动中也复用了部分在过往攻击活动中使用的资产。

### **2.1 为什么归因到东亚黑客组织BlackTech？**

微步情报局近期捕获两个低杀毒引擎检出的Bifrose后门木马。经过分析，这两个后门木马在代码特征上基本一致，然后提取代码特征进行威胁狩猎寻找历史样本，发现历史样本及IT资产属于BlackTech组织。另外，这两个后门木马所使用的IT资产位于中国、日本，与BlackTech组织的特点相符。结合受害者信息综合分析，微步情报局对于将这两个Bifrose后门木马归因于BlackTech组织有较高的信心。

### **2.2 关联分析，未知Python木马与BlackTech的关系**

对BlackTech组织近期使用的IT资产进行排查，其中通过C&amp;C [cache8754.myssldomains.com](https://www.virustotal.com/gui/domain/cache8754.myssldomains.com)关联到一个用Python编写打包的木马8764c735d2dbc4ab83b43eaa63e78c78（MD5）。经过分析，此后门木马是BlackTech组织的新武器。

对C&amp;C [cache8754.myssldomains.com](https://www.virustotal.com/gui/domain/cache8754.myssldomains.com)进行IT资产维度分析：

[![](https://p4.ssl.qhimg.com/t01927844960629dd85.png)](https://p4.ssl.qhimg.com/t01927844960629dd85.png)

[cache8754.myssldomains.com](https://www.virustotal.com/gui/domain/cache8754.myssldomains.com)曾被解析为以下IP地址：
<td class="ql-align-center" data-row="1">2020-10-28</td><td class="ql-align-center" data-row="1">154.204.60.xx</td>
<td class="ql-align-center" data-row="2">2020-08-12</td><td class="ql-align-center" data-row="2">104.238.160.xx</td>
<td class="ql-align-center" data-row="3">2020-07-01</td><td class="ql-align-center" data-row="3">154.209.234.xx</td>
<td class="ql-align-center" data-row="4">2020-06-23</td><td class="ql-align-center" data-row="4">193.187.118.xx</td>

其中193.187.118.xx可以关联到[rt37856cache.work***news.com](https://www.virustotal.com/gui/domain/rt37856cache.workdaynews.com)，而www.work***news.com是Python编写打包的木马8764c735d2dbc4ab83b43eaa63e78c78（MD5）的C&amp;C（样本分析请见后文）。而这两个域名在字符特征上也十分相似，均使用cache关键词。

### **2.3 关联分析，未知Windows木马与BlackTech的关系**

IP 103.40.112.228是BlackTech组织使用过的IT资产，近期微步情报局捕获到使用该IP作为C&amp;C的Windows版本木马9061ff3f23735feddcc51d66f1647f9d（MD5），此木马是由Gh0st源码修改而来，而BlackTech组织也使用过由Gh0st源码修改过的后门木马。综合分析，微步情报局推测此Windows木马也是BlackTech组织使用的木马。

下面，微步情报局将对近期BlackTech组织使用的后门木马进行详细分析，包括Windows木马、Bifrose木马以及Python木马。



## 三、样本分析

BlackTech具备Windows和Linux多平台的攻击能力，近期发现在Windows平台上使用由Gh0st源码修改而来的后门木马，在Linux平台上使用Bifrose后门木马，多数杀毒引擎较难查杀，另外在Linux平台还使用Python编写打包的后门木马。下面微步情报局将对这三种类型样本进行深入分析。

### **3.1 Windows **

**3.1.1类Gh0st样本分析**

类Gh0st样本基本信息如下：
<td class="ql-align-center" data-row="1">文件名称</td><td class="ql-align-center" data-row="1">vsvss.exe</td>
<td class="ql-align-center" data-row="2">SHA256</td><td class="ql-align-center" data-row="2">c75113a4fdd9086f611b20d153e8a882bc11c0256c92468ed39adf0c43972284</td>
<td class="ql-align-center" data-row="3">SHA1</td><td class="ql-align-center" data-row="3">9763350d2dc9b9ab86c31929ce406f5935a7d4ec</td>
<td class="ql-align-center" data-row="4">MD5</td><td class="ql-align-center" data-row="4">9061ff3f23735feddcc51d66f1647f9d</td>
<td class="ql-align-center" data-row="5">样本大小</td><td class="ql-align-center" data-row="5">244.50 KB (250368 bytes)</td>
<td class="ql-align-center" data-row="6">样本格式</td><td class="ql-align-center" data-row="6">PE32+ executable for MS Windows (GUI) Mono/.Net assembly</td>
<td class="ql-align-center" data-row="7">PDB信息</td><td class="ql-align-center" data-row="7">D:\windows2000测试 x86 x64 v1.3\svchost-全功能-加密1205\x64\Release\svchost.pdb</td>
<td class="ql-align-center" data-row="8">C2</td><td class="ql-align-center" data-row="8">103.40.112.228</td>

1、样本入口初始化回连C2字符串，代码如下：

[![](https://p2.ssl.qhimg.com/t0127ae6ead24c6f847.png)](https://p2.ssl.qhimg.com/t0127ae6ead24c6f847.png)

2、获取包括计算机名、用户名、内存信息、CPU信息在内的系统信息作为上线包。

[![](https://p5.ssl.qhimg.com/t013eb88facd51a25ec.png)](https://p5.ssl.qhimg.com/t013eb88facd51a25ec.png)

[![](https://p1.ssl.qhimg.com/t01b02d8a71a34e6109.png)](https://p1.ssl.qhimg.com/t01b02d8a71a34e6109.png)

3、样本上线完成以后，循环获取控制端指令，然后通过“CKernelManager”类调用各类指令执行，截图如下：

[![](https://p1.ssl.qhimg.com/t01b264c3e03a0cb6f0.png)](https://p1.ssl.qhimg.com/t01b264c3e03a0cb6f0.png)

4、功能列表如下：

[![](https://p4.ssl.qhimg.com/t017b6b04123682d098.png)](https://p4.ssl.qhimg.com/t017b6b04123682d098.png)

5、指令表
<td class="ql-align-center" data-row="1">指令</td><td class="ql-align-center" data-row="1">功能</td>
<td class="ql-align-center" data-row="2">1</td><td class="ql-align-center" data-row="2">文件操作</td>
<td class="ql-align-center" data-row="3">40</td><td class="ql-align-center" data-row="3">Shell</td>
<td class="ql-align-center" data-row="4">50</td><td class="ql-align-center" data-row="4">端口映射</td>
<td class="ql-align-center" data-row="5">63</td><td class="ql-align-center" data-row="5">UltraPortmapManager</td>

6、该样本整体风格和gh0st一致，为gh0st变种木马。例如两者的文件操作功能代码：

[![](https://p5.ssl.qhimg.com/t0105df5d389cf39494.png)](https://p5.ssl.qhimg.com/t0105df5d389cf39494.png)

7、除此之外，样本中存在“CFileManager”、“CKernelManager”、“CShellManager”等几乎和gh0st源码一致的类名定义。

### **3.2 Linux**

**3.2.1 Bifrose后门木马分析如下**

样本基本信息如下：
<td class="ql-align-center" data-row="1">文件名称</td><td class="ql-align-center" data-row="1">initkernel.dat</td>
<td class="ql-align-center" data-row="2">SHA256</td><td class="ql-align-center" data-row="2">af8301a821cf428dd3d8d52e5f71548b43ba712de2f12a90d49d044ce2a3ba93</td>
<td class="ql-align-center" data-row="3">SHA1</td><td class="ql-align-center" data-row="3">87d042bac542d2f23282bda4643b0c56538dfe98</td>
<td class="ql-align-center" data-row="4">MD5</td><td class="ql-align-center" data-row="4">bb6a5e4690768121d9bffcd82dd20d8f</td>
<td class="ql-align-center" data-row="5">样本大小</td><td class="ql-align-center" data-row="5">31.46 KB (32216 bytes)</td>
<td class="ql-align-center" data-row="6">样本格式</td><td class="ql-align-center" data-row="6">ELF 64-bit</td>
<td class="ql-align-center" data-row="7">C2</td><td class="ql-align-center" data-row="7">opensshd.com</td>

1、木马运行之后先使用内置编码数据初始化一个用于解密兑换的数组。

[![](https://p3.ssl.qhimg.com/t01efce841dddd8aecc.png)](https://p3.ssl.qhimg.com/t01efce841dddd8aecc.png)

2、随后发起https网络通信，C&amp;C地址opensshd.com直接采用硬编码数据存储。

[![](https://p0.ssl.qhimg.com/t01ccc3cd8a7067c7fe.png)](https://p0.ssl.qhimg.com/t01ccc3cd8a7067c7fe.png)

[![](https://p1.ssl.qhimg.com/t01592d8e9b5475b5ea.png)](https://p1.ssl.qhimg.com/t01592d8e9b5475b5ea.png)

3、通过前面初始化的兑换数组解密C&amp;C服务器返回指令，分发执行远控指令，包含常见的文件操作、下载执行等功能。执行结果通过日志字符串发送告知C&amp;C服务器。

[![](https://p5.ssl.qhimg.com/t017dd532e3ec972ecb.png)](https://p5.ssl.qhimg.com/t017dd532e3ec972ecb.png)、

其指令表如下：
<td class="ql-align-center" data-row="1">指令（解析后）</td><td class="ql-align-center" data-row="1">描述</td>
<td class="ql-align-center" data-row="2">137</td><td class="ql-align-center" data-row="2">创建目录</td>
<td class="ql-align-center" data-row="3">198</td><td class="ql-align-center" data-row="3">结束木马进程。</td>
<td class="ql-align-center" data-row="4">247</td><td class="ql-align-center" data-row="4">更换本地用于解密的兑换数组</td>
<td class="ql-align-center" data-row="5">246</td><td class="ql-align-center" data-row="5">执行/bin/sh目录下程序</td>
<td class="ql-align-center" data-row="6">139</td><td class="ql-align-center" data-row="6">查找目标文件</td>
<td class="ql-align-center" data-row="7">138</td><td class="ql-align-center" data-row="7">删除文件</td>
<td class="ql-align-center" data-row="8">143</td><td class="ql-align-center" data-row="8">重命名文件</td>
<td class="ql-align-center" data-row="9">132</td><td class="ql-align-center" data-row="9">下载写入文件</td>
<td class="ql-align-center" data-row="10">133、134</td><td class="ql-align-center" data-row="10">修改写入目标文件</td>
<td class="ql-align-center" data-row="11">135</td><td class="ql-align-center" data-row="11">关闭文件</td>
<td class="ql-align-center" data-row="12">130、21、248</td><td class="ql-align-center" data-row="12">测试</td>
<td class="ql-align-center" data-row="13">131</td><td class="ql-align-center" data-row="13">文件时间修改</td>

**3.2.2 Python编写打包的后门木马分析**

样本基本信息如下：
<td class="ql-align-center" data-row="1">文件名称</td><td class="ql-align-center" data-row="1">[axisdev](https://www.virustotal.com/gui/search/name:axisdev)</td>
<td class="ql-align-center" data-row="2">SHA256</td><td class="ql-align-center" data-row="2">76bf5520c19d469ae7fdc723102d140a375bb32f64b0065470238e6c29ac2518</td>
<td class="ql-align-center" data-row="3">SHA1</td><td class="ql-align-center" data-row="3">8a1d27f22ecb365d6d0591fab30734598163ff03</td>
<td class="ql-align-center" data-row="4">MD5</td><td class="ql-align-center" data-row="4">8764c735d2dbc4ab83b43eaa63e78c78</td>
<td class="ql-align-center" data-row="5">样本大小</td><td class="ql-align-center" data-row="5">8.04 MB (8432384 bytes)</td>
<td class="ql-align-center" data-row="6">样本格式</td><td class="ql-align-center" data-row="6">ELF 64-bit</td>
<td class="ql-align-center" data-row="7">C2</td><td class="ql-align-center" data-row="7">www.workdaynews.com</td>

1、多引擎反馈该样本为python编写的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01879c18f119c4ca34.png)

2、在段信息中发现pydata section，这个是pyinstaller打包python程序为可执行程序的特点。

[![](https://p2.ssl.qhimg.com/t0176b17379fd6f8766.png)](https://p2.ssl.qhimg.com/t0176b17379fd6f8766.png)

3、从样本中提取pydata段的数据，再使用pyinstxtractor.py对该数据进行解析；

提取pydata段数据的命令 objcopy –only-section=pydata axisdev pydata；

使用pyinstxtractor.py解析pydata段数据；

解包后找到agent.pyc，即为源程序编码后的程序。

[![](https://p4.ssl.qhimg.com/t011b20856bd6bb06cf.png)](https://p4.ssl.qhimg.com/t011b20856bd6bb06cf.png)

4、对agent.pyc程序进行解码分析。

执行命令uncompyle6 agent.pyc &gt; agent.py。

对agent.py进行分析：

[![](https://p1.ssl.qhimg.com/t01048e47b22efa8479.png)](https://p1.ssl.qhimg.com/t01048e47b22efa8479.png)

agent函数名及功能如下：
<td class="ql-align-justify" data-row="1">函数名</td><td class="ql-align-center" data-row="1">功能</td>
<td class="ql-align-center" data-row="2">get_install_dir</td><td class="ql-align-center" data-row="2">获取安装目录</td>
<td class="ql-align-center" data-row="3">is_installed</td><td class="ql-align-center" data-row="3">获取安装目录</td>
<td class="ql-align-center" data-row="4">get_consecutive_failed_connections</td><td class="ql-align-center" data-row="4">获取连续连接失败</td>
<td class="ql-align-center" data-row="5">update_consecutive_failed_connections</td><td class="ql-align-center" data-row="5">记录连续连接失败</td>
<td class="ql-align-center" data-row="6">get_UID</td><td class="ql-align-center" data-row="6">获取UID</td>
<td class="ql-align-center" data-row="7">server_hello</td><td class="ql-align-center" data-row="7">向server请求命令</td>
<td class="ql-align-center" data-row="8">send_output</td><td class="ql-align-center" data-row="8">发送输出到server</td>
<td class="ql-align-center" data-row="9">expand_path</td><td class="ql-align-center" data-row="9">扩展路径中的环境变量和元字符</td>
<td class="ql-align-center" data-row="10">Runcmd</td><td class="ql-align-center" data-row="10">运行shell命令并返回输出</td>
<td class="ql-align-center" data-row="11">Python</td><td class="ql-align-center" data-row="11">运行python命令或者python文件并返回输出</td>
<td class="ql-align-center" data-row="12">cd</td><td class="ql-align-center" data-row="12">变更当前路径</td>
<td class="ql-align-center" data-row="13">upload</td><td class="ql-align-center" data-row="13">上传本地文件到server</td>
<td class="ql-align-center" data-row="14">download</td><td class="ql-align-center" data-row="14">下载文件</td>
<td class="ql-align-center" data-row="15">persist</td><td class="ql-align-center" data-row="15">实现持久化</td>
<td class="ql-align-center" data-row="16">clean</td><td class="ql-align-center" data-row="16">卸载本agent</td>
<td class="ql-align-center" data-row="17">exit</td><td class="ql-align-center" data-row="17">退出本agent</td>
<td class="ql-align-center" data-row="18">zip</td><td class="ql-align-center" data-row="18">压缩文件目录或文件</td>

其接受的命令如下：
<td class="ql-align-center" data-row="1">cd</td><td class="ql-align-center" data-row="1">变更当前路径</td>
<td class="ql-align-center" data-row="2">upload</td><td class="ql-align-center" data-row="2">上传本地文件到server</td>
<td class="ql-align-center" data-row="3">download</td><td class="ql-align-center" data-row="3">下载文件</td>
<td class="ql-align-center" data-row="4">clean</td><td class="ql-align-center" data-row="4">卸载本agent</td>
<td class="ql-align-center" data-row="5">persist</td><td class="ql-align-center" data-row="5">实现持久化</td>
<td class="ql-align-center" data-row="6">exit</td><td class="ql-align-center" data-row="6">退出本agent</td>
<td class="ql-align-center" data-row="7">zip</td><td class="ql-align-center" data-row="7">压缩文件目录或文件</td>
<td class="ql-align-center" data-row="8">python</td><td class="ql-align-center" data-row="8">运行python命令或者python文件并返回输出</td>
<td class="ql-align-center" data-row="9">help</td><td class="ql-align-center" data-row="9">列出支持的命令</td>

5、C&amp;C配置

根据代码，agent会读取config中的C&amp;C。由于agent通过import 引入config文件，因此这个config文件在pyinstxtractor.py提取数据的依赖目录里面，即config.pyc。

[![](https://p1.ssl.qhimg.com/t01d6240cb2b9685c50.png)](https://p1.ssl.qhimg.com/t01d6240cb2b9685c50.png)

对config.pyc进行解码分析，提取 C&amp;C地址www.workdaynews.com。

[![](https://p1.ssl.qhimg.com/t0192fd5f289a68a9da.png)](https://p1.ssl.qhimg.com/t0192fd5f289a68a9da.png)

6、持久化技术分析

该agent意图实现持久化，对持久化技术进行分析：

[![](https://p2.ssl.qhimg.com/t01bbad236f4e506e60.png)](https://p2.ssl.qhimg.com/t01bbad236f4e506e60.png)

（1）创建路径 ~/.ares；

（2）复制agent到路径之下；

（3）添加权限 chmod +x；

（4）添加自启动配置文件~/.config/autostart/ares.desktop ~/.bashrc（Linux）；

（5）windows下添加注册表。

reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /f /v ares /t REG_SZ /d “%s”‘ % agent_path

**3.2.3 ATT&amp;CK**
<td data-row="1">技术ID</td><td data-row="1">技术实现</td>
<td data-row="2">TA0003，[T1547](https://attack.mitre.org/techniques/T1547).001 [Registry Run Keys / Startup Folder](https://attack.mitre.org/techniques/T1547/001)</td><td data-row="2">Linux平台下添加自启动配置文件~/.config/autostart/ares.desktop</td>
<td data-row="3">TA0003，[T1547](https://attack.mitre.org/techniques/T1547).001 [Registry Run Keys / Startup Folder](https://attack.mitre.org/techniques/T1547/001)</td><td data-row="3">Windows平台下添加注册表reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /f /v ares /t REG_SZ /d “%s”‘ % agent_path</td>
<td data-row="4">TA003，[T1546](https://attack.mitre.org/techniques/T1546).004 [.bash_profile and .bashrc](https://attack.mitre.org/techniques/T1546/004)</td><td data-row="4">Linux平台下添加自启动配置到~/.bashrc</td>



## 四、总结

根据上述分析结果，微步在线情报局认为东亚黑客组织BlackTech是一个经验丰富、成熟度较高、威胁度较高的黑客组织。在近期的攻击活动中该组织使用了多数杀毒引擎较难查杀的Bifrose后门木马，这表明该组织的武器库在持续丰富和变化。由于该组织近期的攻击目标均为中国的金融、教育等行业的企业，建议相关行业的企业提高安全意识、注意防护。
