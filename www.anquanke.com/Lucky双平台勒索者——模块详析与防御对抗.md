> 原文链接: https://www.anquanke.com//post/id/166720 


# Lucky双平台勒索者——模块详析与防御对抗


                                阅读量   
                                **199282**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01f41686abbc437f0c.png)](https://p0.ssl.qhimg.com/t01f41686abbc437f0c.png)

作者：360企业安全·华南基地

lucky是一款具备超强传播能力的勒索者，360威胁情报中心最早监测到该样本于2018-11-03开始在互联网络活动，通过多种漏洞利用组合进行攻击传播，同时支持 Windows和Linux两种操作系统平台，加密算法采用高强度的RAS+AES算法。同时该样本还会进行挖矿木马的种植。仅在2018年11月内，已监测到受影响的机构和个人约1000例左右。



## 传播模块分析

Lucky模块之一为.conn，该模块与Satan(勒索者）的传播模块基本上一致，主要利用以下漏洞进行攻击。
<td valign="top" width="539">横向攻击手法&amp;漏洞利用</td>
<td valign="top" width="539">Apache Struts2远程代码执行漏洞</td>
<td valign="top" width="539">CVE-2018-1273漏洞</td>
<td valign="top" width="539">Tomcat web管理后台弱口令爆破</td>
<td valign="top" width="539">系统账户弱口令爆破</td>
<td valign="top" width="539">JBoss反序列化漏洞(CVE-2013-4810)</td>
<td valign="top" width="539">JBoss默认配置漏洞(CVE-2010-0738)</td>
<td valign="top" width="539">Weblogic WLS 组件漏洞（CVE-2017-10271）</td>
<td valign="top" width="539">Apache Struts2远程代码执行漏洞S2-045</td>
<td valign="top" width="539">Apache Struts2远程代码执行漏洞S2-057</td>
<td valign="top" width="539">Windows SMB远程代码执行漏洞MS17-010</td>

通过分析Conn模块发现在该Linux样本中发现了大量“.exe”的字样，可以确定该样本是个跨平台攻击样本，通过Web应用漏洞对Windows、Linux服务器进行无差别、无缝隙的攻击。

[![](https://p1.ssl.qhimg.com/t01aba38539e59b1a51.png)](https://p1.ssl.qhimg.com/t01aba38539e59b1a51.png)

### 主要利用的漏洞

#### 1. Apache Struts2远程代码执行漏洞

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c63b9983375b275d.png)

#### **2****．**CVE-2018-1273**漏洞**

针对Windows系统，利用CVE-2018-1273漏洞上传fast.exe病毒Downloader至C盘根目录下，下载地址为：hxxp://111.90.158.225/d/fast.exe，截至目前能下载到该样本( MD5: fae322a3ec89c70cb45115779d52cf47)。

[![](https://p0.ssl.qhimg.com/t01e016174cf0c40986.png)](https://p0.ssl.qhimg.com/t01e016174cf0c40986.png)

针对Linux系统 ，利用CVE-2018-1273漏洞上传/d/ft32和/d/ft64病毒Downloader至服务器，下载地址分别为hxxp://111.90.158.225/d/ft32和 hxxp://111.90.158.225/d/ft64。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0185bd3f0cdd8d6de4.png)

#### 3.Tomcat管理后台弱口令爆破

[![](https://p1.ssl.qhimg.com/t01adfa8896cd36503a.png)](https://p1.ssl.qhimg.com/t01adfa8896cd36503a.png)

#### 4. 尝试爆破系统账户和密码

另外，除了Tomcat的弱口令爆破，还会去尝试爆破系统账户和密码。

[![](https://p4.ssl.qhimg.com/t01b16a914edb16f2fd.png)](https://p4.ssl.qhimg.com/t01b16a914edb16f2fd.png)

#### 5.JBoss反序列化漏洞利用

[![](https://p2.ssl.qhimg.com/t015b4bcfd602b96809.png)](https://p2.ssl.qhimg.com/t015b4bcfd602b96809.png)

#### 6.JBoss默认配置漏洞

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f3dd60b1867d871f.png)

#### 7．Weblogic WLS 组件漏洞

[![](https://p1.ssl.qhimg.com/t01ce256610f5f99e38.png)](https://p1.ssl.qhimg.com/t01ce256610f5f99e38.png)

#### 8.Struts2远程执行S2-057漏洞

[![](https://p1.ssl.qhimg.com/t0134216f97d40e15cf.png)](https://p1.ssl.qhimg.com/t0134216f97d40e15cf.png)

#### 9.Struts2远程执行S2-045

根据目标OS执行不同的恶意命令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012307070a9f63d9b7.png)

#### 10．Windows SMB远程代码执行漏洞MS17-010（永恒之蓝）<br>
Conn模块会通过永恒之蓝工具进行横向移动。

### Linux勒索部分分析

Lucky勒索者会加密以下后缀名的文件：

bak zip sql mdf ldf myd myi dmp xls doc txt ppt csv rtf pdf db vdi vmdk vmx tar gz pem pfx cer ps

[![](https://p0.ssl.qhimg.com/t012ae6061757b99fba.png)](https://p0.ssl.qhimg.com/t012ae6061757b99fba.png)

加密过程中发现为以下目录则直接返回跳过：

/bin, /boot, /sbin , /tmp, /etc, /etc, /lib

[![](https://p4.ssl.qhimg.com/t0103953dc4dfe5517c.png)](https://p4.ssl.qhimg.com/t0103953dc4dfe5517c.png)

病毒使用RSA+AES 的加密方式对文件进行加密。

[![](https://p3.ssl.qhimg.com/t01dd787edab5395671.png)](https://p3.ssl.qhimg.com/t01dd787edab5395671.png)

最后生成加密勒索信息,并将文件名改成[nmare@cock.li]+文件名 + Session + lucky后缀

[![](https://p2.ssl.qhimg.com/t01d0bd25c9191d97ac.png)](https://p2.ssl.qhimg.com/t01d0bd25c9191d97ac.png)

再将被加密文件的数量、大小、session等信息上传到C2地址为111.90.158.225的服务器上。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01507e0e5a49c1f68f.png)



## Fast模块分析

上文说到，针对windows平台，会在c:\释放一个文件fast.exe, 该文件其实是一个Downloader，分别去下载conn.exe和srv.exe到C：\Program Files\Common File\System目录下然后调用ShellExecute去执行该文件。

[![](https://p1.ssl.qhimg.com/t019c3f8f4e4268a1fe.png)](https://p1.ssl.qhimg.com/t019c3f8f4e4268a1fe.png)



## Conn模块分析

Conn主要的功能是负责windows平台上的横向移动, 使用到的漏洞和上文中提到的一致，首先Conn会从资源中释放出永恒之蓝攻击模块和Mimikatz（mmkt.exe）到C:\Users\All Users目录下，如下图。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010d58ed70abce07ca.png)

动态调试结果如下。

[![](https://p0.ssl.qhimg.com/t018b072ac31acfb187.png)](https://p0.ssl.qhimg.com/t018b072ac31acfb187.png)

当释放完永恒之蓝攻击模块后，将会先启动 mmkt.exe获取到windows账户密码，用于新起线程进行攻击工作，其中线程一启动永恒之蓝攻击模块, 如果是64位系统，则使用down64.dll 作为payload 来使用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012899bf73d24573c5.png)

该payload会下载fast.exe。

[![](https://p0.ssl.qhimg.com/t019fa885a5ecfb0e7d.png)](https://p0.ssl.qhimg.com/t019fa885a5ecfb0e7d.png)

线程二进行web服务的攻击。

[![](https://p4.ssl.qhimg.com/t01ac003cc1e12048dc.png)](https://p4.ssl.qhimg.com/t01ac003cc1e12048dc.png)

以下是conn.exe使用到的Weblogic ,Struts2, JBoss等漏洞攻击 payload，详细的漏洞攻击情况已在上面漏洞版面讲述，就不再赘述了。

[![](https://p3.ssl.qhimg.com/t01d7de8a855bda8eaf.png)](https://p3.ssl.qhimg.com/t01d7de8a855bda8eaf.png)



## Srv模块分析

首先该模块会去读一下版本配置文件，检测一遍是否要更新。当前分析时最新版本为1.13。

[![](https://p3.ssl.qhimg.com/t0192d431fa80785b94.png)](https://p3.ssl.qhimg.com/t0192d431fa80785b94.png)

接着下载cpt.exe 和mn32.exe到C:\Program Files\Common Files\System目录下并执行。

[![](https://p3.ssl.qhimg.com/t017f9a5048c9b28d97.png)](https://p3.ssl.qhimg.com/t017f9a5048c9b28d97.png)

执行完上述逻辑后，然后判断参数一，是否等于1或者2，如果参数一等于1则调用StartServiceCtrlDispatcherA函数启动服务的回调函数, 如果参数一等于2，再判断参数二的参数是install还是removesrv，分别为安装服务和卸载服务的功能。

[![](https://p5.ssl.qhimg.com/t01cbf6086c2ebfbae5.png)](https://p5.ssl.qhimg.com/t01cbf6086c2ebfbae5.png)

创建的服务名称叫作Logs Servic指向srv本身。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aa468a42e870ecda.png)

最后获取系统信息后拼接参数向服务端发送系统配置等信息。

http://111.90.158.225/token.php?sys=&amp;c_type=&amp;dis_type&amp;num=&amp;ver=

[![](https://p0.ssl.qhimg.com/t01e10852e78fd857c7.png)](https://p0.ssl.qhimg.com/t01e10852e78fd857c7.png)



## Cpt模块分析

Cpt为windows版本的勒索加密者逻辑和linux的一样，首先它尝试关闭一些数据库服务及进程以解除文件占用，方便对文件进行加密。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f2f4781231c9c8a3.png)

cpt.exe主要感染以下类型文件：

.bak.sql.mdf.ldf.myd.myi.dmp.xls.xlsx.docx.pptx.eps.txt.ppt.csv.rtf.pdf.db.vdi.vmdk.vmx.pem.pfx.cer.psd

[![](https://p0.ssl.qhimg.com/t01cd33aa6433558352.png)](https://p0.ssl.qhimg.com/t01cd33aa6433558352.png)

不加密含有如下字符串的路径：

windows , python2 , python3 , microsoft games , boot , i386 , intel , dvd maker ,recycle ,jdk ,lib ,libs ,allusers ,360rec ,360sec ,360sand ,favorites ,common files ,internet explorer ,msbuild ,public ,360downloads ,windows defen ,windows mail ,windows media pl ,windows nt ,windows photo viewer ,windows sidebar ,default user

通过该排除路径的信息，我们猜测该勒索者为国人制作。

同样windows版本的勒索加密部分和linux一样也是lucky后缀。

[![](https://p3.ssl.qhimg.com/t0186f7b0e0bfa37aec.png)](https://p3.ssl.qhimg.com/t0186f7b0e0bfa37aec.png)

同样加密算法采用AES+RSA加密。

[![](https://p3.ssl.qhimg.com/t01840c11fd622aeeeb.png)](https://p3.ssl.qhimg.com/t01840c11fd622aeeeb.png)

最后将session ID 文件个数，文件大小，系统，等等信息上报到服务端。

[![](https://p1.ssl.qhimg.com/t01895d4d4ecd5db2a5.png)](https://p1.ssl.qhimg.com/t01895d4d4ecd5db2a5.png)



## Mn2模块分析

该模块是挖矿木马使用了如下开源代码。

[https://github.com/alloyproject/xmrig/blob/master/src/core/ConfigLoader_platform.h](https://github.com/alloyproject/xmrig/blob/master/src/core/ConfigLoader_platform.h)

[![](https://p0.ssl.qhimg.com/t01ecca7cf733479e75.png)](https://p0.ssl.qhimg.com/t01ecca7cf733479e75.png)

挖矿木马的矿池地址如下：

[![](https://p1.ssl.qhimg.com/t0139624f388d93ec0d.png)](https://p1.ssl.qhimg.com/t0139624f388d93ec0d.png)



## 总结&amp;防御策略

该样本使用多种漏洞攻击组合，进行勒索和挖矿等行为，应给系统和应用打全补丁切断传播途径，关闭不必要的网络共享端口，关闭异常的外联访问。

### **附录IOC：**

样本说明：

文件名：.conn

MD5：84DDEE0187C61D8EB4348E939DA5A366

文件名: .crypt

MD5：D1AC4B74EE538DAB998085E0DFAA5E8D

文件名: srv

MD5：E7897629BA5B2D74418D9A9B6157AE80

文件名: cpt.exe

MD5：36E34E763A527F3AD43E9C30ACD276FF

文件名: mn2.exe

MD5：D1AC4B74EE538DAB998085E0DFAA5E8D

文件名：ft32

MD5：8D3C8045DF750419911C6E1BF493C747

文件名：ft64

MD5：E145264CFFA3C01A93871B27A4F569CC

C2 地址:

111.90.158.225
