> 原文链接: https://www.anquanke.com//post/id/146062 


# 一起涉及多个DDoS僵尸网络样本的攻击事件追踪


                                阅读量   
                                **132305**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t0175b2f42ca25b4fb0.jpg)](https://p0.ssl.qhimg.com/t0175b2f42ca25b4fb0.jpg)

## 一．背景

近期任子行蜜网系统监测到一起涉及利用多个僵尸木马传播进行DDoS攻击的安全事件。木马样本涉及Windows与Linux两个平台，通过对样本的分析，发现这几个样本编写风格都不一样，但是硬编码在程序中的C&amp;C均指向同一个IP地址。推测这一系列木马的传播者通过购买不同的DDoS木马进行传播，从而构建自己的僵尸网络进行DDoS攻击牟利。其中有两个样本所属家族为XorDDoS和ChinaZ。最后通过一系列的分析，将该威胁定性为小黑客组建僵尸网络进行DDoS攻击事件，同时追踪到了恶意代码传播者的个人信息，包括姓名、QQ号码、手机号、邮箱、微信等。



## 二．相关样本分析

### 2.1样本一分析：

**2.1.1样本基本信息**
<td style="width: 72.5500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: 1.0000pt solid #4f81bd; border-bottom: 1.0000pt solid #ffffff; background: #4f81bd;" valign="top" width="120">文件名</td><td style="width: 378.2500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: 1.0000pt solid #4f81bd; border-bottom: 1.0000pt solid #ffffff; background: #4f81bd;" valign="top" width="630">gy.exe</td>

gy.exe

文件类型

PE x86
<td style="width: 72.55pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="120">样本SHA256</td><td style="width: 378.25pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="630">892833AB52DAA816918041670519EB6351AE7EC2DB7AF2C97F3AB5EE214DA173<u></u></td>

892833AB52DAA816918041670519EB6351AE7EC2DB7AF2C97F3AB5EE214DA173<u></u>
<td style="width: 72.5500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="120">样本源</td><td style="width: 378.2500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="630">[http://123.160.10.16:3097/gy.exe](http://123.160.10.16:3097/gy.exe)</td>

[http://123.160.10.16:3097/gy.exe](http://123.160.10.16:3097/gy.exe)
<td style="width: 72.55pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="120">传播方式</td><td style="width: 378.25pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="630">SSH爆破后，远程下载执行</td>

SSH爆破后，远程下载执行
<td style="width: 72.5500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="120">C&amp;C</td><td style="width: 378.2500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="630">web.liancanmou.xyz:6006（180.97.220.35:6006）</td>

web.liancanmou.xyz:6006（180.97.220.35:6006）
<td style="width: 72.55pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="120">所属家族</td><td style="width: 378.25pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="630">XorDDoS</td>

XorDDoS

 

**2.1.2样本行为**

该样本首先会执行安装逻辑，包括拷贝自身到Windows目录，然后将自身注册为服务，最后自删除自己，安装完成。接着注册为服务的木马会开始进入功能逻辑，通过爆破局域网来感染传播，与C&amp;C建立通讯后，等待C&amp;C下发指令。

 [![](https://p0.ssl.qhimg.com/t017a74a45c56d5d940.png)](https://p0.ssl.qhimg.com/t017a74a45c56d5d940.png)

### 

**2.1.3样本详细分析**

**（1）整体逻辑**

[![](https://p4.ssl.qhimg.com/t013fd6de7229c4ff0c.png)](https://p4.ssl.qhimg.com/t013fd6de7229c4ff0c.png)

 

**（2）拷贝到Windows目录**

生成6个字符的随机进程名拷贝到Windows目录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0199a5303e82a157d7.png)

**（3）创建服务**

服务名：Abcdef Hijklmno Qrstuvwx Abcd

服务描述：Abcdefgh Jklmnopqr Tuvwxya Cdefghij Lmn

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0115856b43f74b8a66.png)[![](https://p0.ssl.qhimg.com/t01364238852d364db0.png)](https://p0.ssl.qhimg.com/t01364238852d364db0.png)

[![](https://p4.ssl.qhimg.com/t016ecaed810627e18e.png)](https://p4.ssl.qhimg.com/t016ecaed810627e18e.png)

自启动[![](https://p0.ssl.qhimg.com/t01929e6c1d68835ae8.png)](https://p0.ssl.qhimg.com/t01929e6c1d68835ae8.png)

 

**（4）自删除**

构建“/c del C:UsersxxxDesktopgy.exe &gt; nul”参数，使用ShellExecuteExA创建删除自身的进程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011389e3e135ba03a5.png)

[![](https://p0.ssl.qhimg.com/t01d83b569f6a85532f.png)](https://p0.ssl.qhimg.com/t01d83b569f6a85532f.png)

 

#### <!-- [if !supportLists]-->**（5）<!--[endif]-->从资源释放hra33.dll并加载**

从资源释放文件在文件头加上PE文件头两个字节“MZ”。

[![](https://p3.ssl.qhimg.com/t019baa424b1297c053.png)](https://p3.ssl.qhimg.com/t019baa424b1297c053.png)

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01073f290f7ea9e0a2.png)

 

从释放的文件更新当前木马服务中的资源

[![](https://p0.ssl.qhimg.com/t0182d129cf99f755c6.png)](https://p0.ssl.qhimg.com/t0182d129cf99f755c6.png)

#### **（6）爆破感染局域网**

内置字典

[![](https://p2.ssl.qhimg.com/t01e045d6f964388a0e.png)](https://p2.ssl.qhimg.com/t01e045d6f964388a0e.png)

 

爆破成功后会拷贝自身到admin$\、C：、D:、E：以及F:等路径下，并创建计划任务，2分钟后执行。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0107a4699973e71003.png)

 

**（7）远控功能部分**

与C&amp;C建立通讯

[![](https://p1.ssl.qhimg.com/t0102f34be4d744cf30.png)](https://p1.ssl.qhimg.com/t0102f34be4d744cf30.png)

解密出C&amp;C地址为web.liancanmou.xyz:6006

[![](https://p5.ssl.qhimg.com/t01c85defbaba21ee9e.png)](https://p5.ssl.qhimg.com/t01c85defbaba21ee9e.png)

 

**发送上线信息**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01cb1a4f3ce4f12e1b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015d6c38fbd5494b5b.png)

**远程下载执行**

[![](https://p0.ssl.qhimg.com/t01e87a7fda4624d2ad.png)](https://p0.ssl.qhimg.com/t01e87a7fda4624d2ad.png)

**更新**

[![](https://p2.ssl.qhimg.com/t018e25e257eff009f5.png)](https://p2.ssl.qhimg.com/t018e25e257eff009f5.png)

##### 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013d2ede1f6ad2d3b8.png)

使用iexplorer打开指定网页

**[![](https://p0.ssl.qhimg.com/t019ec652b8d5127c00.png)](https://p0.ssl.qhimg.com/t019ec652b8d5127c00.png)**

 

**卸载**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011f273c40da68a1da.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d96e1bc24ba119d7.png)

 

**DDoS攻击模块**

[![](https://p1.ssl.qhimg.com/t0150739cbf9f7ef4fc.png)](https://p1.ssl.qhimg.com/t0150739cbf9f7ef4fc.png)

 [![](https://p5.ssl.qhimg.com/t012d0989fedbbb98f3.png)](https://p5.ssl.qhimg.com/t012d0989fedbbb98f3.png)

 

**2.1.4 关联分析**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01581f47521a909470.png)

该IP对应的位置在新乡电信机房，访问[http://123.160.10.16:3097/gy.exe](http://123.160.10.16:3097/gy.exe)下载样本。

 

通过VT Graph关联分析该样本早在2018-05-08已经被发现了，与本次捕获到的样本分析结果是一致的。

[![](https://p1.ssl.qhimg.com/t014327cc188c816760.png)](https://p1.ssl.qhimg.com/t014327cc188c816760.png)

 

### 2.2样本二分析：

**2.2.1样本基本信息**
<td style="width: 71.8000pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: 1.0000pt solid #4f81bd; border-bottom: 1.0000pt solid #ffffff; background: #4f81bd;" valign="top" width="119">文件名</td><td style="width: 370.1500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: 1.0000pt solid #4f81bd; border-bottom: 1.0000pt solid #ffffff; background: #4f81bd;" valign="top" width="616">33</td>

33
<td style="width: 71.8000pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="119">文件类型</td><td style="width: 370.1500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="616">ELF x64</td>

ELF x64
<td style="width: 71.8pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="119">样本SHA256</td><td style="width: 370.15pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="616">4A2FB58342D549347D32E54C3DA466A19BFD66364825AC7F2257995356F09AFD</td>

4A2FB58342D549347D32E54C3DA466A19BFD66364825AC7F2257995356F09AFD
<td style="width: 71.8000pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="119">样本源</td><td style="width: 370.1500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="616">http://180.97.220.35:3066/33</td>

http://180.97.220.35:3066/33
<td style="width: 71.8pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="119">传播方式</td><td style="width: 370.15pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="616">SSH爆破，远程下载执行</td>

SSH爆破，远程下载执行
<td style="width: 71.8000pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="119">C&amp;C</td><td style="width: 370.1500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="616">jch.liancanmou.xyz（180.97.220.35）</td>

jch.liancanmou.xyz（180.97.220.35）
<td style="width: 71.8pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="119">所属家族</td><td style="width: 370.15pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="616">Linux.DDOS.Flood</td>

Linux.DDOS.Flood

 

**2.2.2样本行为**

该样本代码编写十分简单，获取本地信息回传CNC上线，等待CNC的DDoS指令。

[![](https://p5.ssl.qhimg.com/t016ad55ed54ae71eab.png)](https://p5.ssl.qhimg.com/t016ad55ed54ae71eab.png)

 

**2.2.3样本详细分析**

**（1）整体逻辑**

[![](https://p4.ssl.qhimg.com/t018240adf8660514de.png)](https://p4.ssl.qhimg.com/t018240adf8660514de.png)

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d13de7be1b686b3a.png)

 

**（2）与C2建立通讯**

**创建连接套接字**

C&amp;C地址为 jch.liancanmou.xyz:52527

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a87280b30558e5b6.png)

木马通讯协议

[![](https://p4.ssl.qhimg.com/t0108925a9e6144bd2e.png)](https://p4.ssl.qhimg.com/t0108925a9e6144bd2e.png)

 

**（3）DDoS功能**
<td style="width: 95.6500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: 1.0000pt solid #4f81bd; border-bottom: 1.0000pt solid #ffffff; background: #4f81bd;" valign="top" width="159">DDoS类型</td>
<td style="width: 95.6500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="159">SYN Flood</td>
<td style="width: 95.65pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="159">UDP Flood</td>
<td style="width: 95.6500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="159">ICMP Flood</td>
<td style="width: 95.65pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="159">DNS Flood</td>
<td style="width: 95.6500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="159">GET Flood</td>

 并没有用到反射放大攻击，只是一般的flood攻击。

[![](https://p5.ssl.qhimg.com/t0167df75c165cc0bbb.png)](https://p5.ssl.qhimg.com/t0167df75c165cc0bbb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dcd6494b00c55ac4.png)

**2.2.4关联分析**

通过VT分析发现该样本与a.lq4444.com这个域名相关，而该域名曾用于Linux/Elknot这个家族。通过VT显示，a.lq4444.com这个域名与9个样本相关。

[![](https://p2.ssl.qhimg.com/t01459cf7db7ff4a900.png)](https://p2.ssl.qhimg.com/t01459cf7db7ff4a900.png)

### 2.3样本三分析
<td style="width: 72.9500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: 1.0000pt solid #4f81bd; border-bottom: 1.0000pt solid #ffffff; background: #4f81bd;" valign="top" width="121">文件名</td><td style="width: 373.0000pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: 1.0000pt solid #4f81bd; border-bottom: 1.0000pt solid #ffffff; background: #4f81bd;" valign="top" width="621">32</td>

32
<td style="width: 72.9500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="121">文件类型</td><td style="width: 373.0000pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="621">ELF x86</td>

ELF x86
<td style="width: 72.95pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="121">样本SHA256</td><td style="width: 373pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="621">74D4776A76AD3BCB578C9757D9F18A6ADFFE8802C43E5E59B14C4E905664733D</td>

74D4776A76AD3BCB578C9757D9F18A6ADFFE8802C43E5E59B14C4E905664733D
<td style="width: 72.9500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="121">样本源</td><td style="width: 373.0000pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="621">http://180.97.220.35:3066/32</td>

http://180.97.220.35:3066/32
<td style="width: 72.95pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="121">传播方式</td><td style="width: 373pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="621">SSH爆破，远程下载执行</td>

SSH爆破，远程下载执行
<td style="width: 72.9500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="121">C&amp;C</td><td style="width: 373.0000pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="621">jch.liancanmou.xyz</td>

jch.liancanmou.xyz
<td style="width: 72.9500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="121">所属家族</td><td style="width: 373.0000pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="621">Linux.DDoS.Flood</td>

Linux.DDoS.Flood

 样本三与样本二代码是一样的，区别是样本三被编译为x86架构，样本二被编译为x64架构。



### 2.4样本四分析：

**2.4.1样本基本信息**
<td style="width: 70.9500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: 1.0000pt solid #4f81bd; border-bottom: 1.0000pt solid #ffffff; background: #4f81bd;" valign="top" width="118">文件名</td><td style="width: 386.7500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: 1.0000pt solid #4f81bd; border-bottom: 1.0000pt solid #ffffff; background: #4f81bd;" valign="top" width="644">Linux4.7</td>

Linux4.7
<td style="width: 70.9500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="118">文件类型</td><td style="width: 386.7500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="644">ELF x86</td>

ELF x86
<td style="width: 70.95pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="118">样本SHA256</td><td style="width: 386.75pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="644">DBC7FC7748BD201C54B2A0189396F3101C18127A715E480C8CB808F07137822A</td>

DBC7FC7748BD201C54B2A0189396F3101C18127A715E480C8CB808F07137822A
<td style="width: 70.9500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="118">样本源</td><td style="width: 386.7500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="644">[http://180.97.220.35:3066/Linux4.7](http://180.97.220.35:3066/Linux4.7)</td>

[http://180.97.220.35:3066/Linux4.7](http://180.97.220.35:3066/Linux4.7)
<td style="width: 70.95pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="118">传播方式</td><td style="width: 386.75pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="644">SSH爆破，远程下载执行</td>

SSH爆破，远程下载执行
<td style="width: 70.9500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: 1.0000pt solid #4f81bd; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="118">C&amp;C</td><td style="width: 386.7500pt; padding: 0.0000pt 5.4000pt 0.0000pt 5.4000pt; border-left: none; border-right: 1.0000pt solid #4f81bd; border-top: none; border-bottom: 1.0000pt solid #4f81bd; background: #b8cce4;" valign="top" width="644">wwt.liancanmou.xyz（180.97.220.35）</td>

wwt.liancanmou.xyz（180.97.220.35）
<td style="width: 70.95pt; padding: 0pt 5.4pt; border-left: 1pt solid #4f81bd; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="118">所属家族</td><td style="width: 386.75pt; padding: 0pt 5.4pt; border-left: none; border-right: 1pt solid #4f81bd; border-top: none; border-bottom: 1pt solid #4f81bd;" valign="top" width="644">ChinaZ</td>

ChinaZ

 

**2.4.2样本行为**

<!-- [if !supportLists]-->（1）<!--[endif]-->该样本通过SSH爆破被拷贝到/tmp目录下并开始运行

<!-- [if !supportLists]-->（2）<!--[endif]-->将自身注册为服务

<!-- [if !supportLists]-->（3）<!--[endif]-->拷贝自身到其他目录

<!-- [if !supportLists]-->（4）<!--[endif]-->设置定时任务

<!-- [if !supportLists]-->（5）<!--[endif]-->修改刷新iptables后，尝试连接到远程主机。

<!-- [if !supportLists]-->（6）<!--[endif]-->它会删除/etc/resolv.conf并保存初始安装和下载的配置数据（Config.ini）

<!-- [if !supportLists]-->（7）<!--[endif]-->通过发送用户名信息连接到C&amp;C，作为一个bot与C&amp;C建立通讯

<!-- [if !supportLists]-->（8）<!--[endif]-->C&amp;C主要发送带目标IP地址作为参数的DDoS命令到bot机器进行DDoS攻击

 

**VT行为分析：**

[![](https://p2.ssl.qhimg.com/t01e6d6405f8079e8a8.png)](https://p2.ssl.qhimg.com/t01e6d6405f8079e8a8.png)



**2.4.3样本详细分析**

写入脚本到/etc/init.d/%s/与/etc/rc%d.d/S90%s路径下

[![](https://p5.ssl.qhimg.com/t01be587730801182e0.png)](https://p5.ssl.qhimg.com/t01be587730801182e0.png)

 

设置定时任务

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f9fe99296b6ab370.png)

控制网卡接口

[![](https://p4.ssl.qhimg.com/t018c11f8ccca581e1d.png)](https://p4.ssl.qhimg.com/t018c11f8ccca581e1d.png)

以前缀为.chinaz文件名拷贝到/tmp目录

[![](https://p3.ssl.qhimg.com/t015473bfb11242f96b.png)](https://p3.ssl.qhimg.com/t015473bfb11242f96b.png)

安装完成后会重启计算机

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fa4cfa0bf0547fe8.png)

DDoS相关的一些指纹，其中包含一个QQ号码：2900570290

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0187c6e3b7918edbec.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a05e1353d26e590b.png)

 

## 三．事件分析

### 3.1事件关联分析

以liancanmou.xyz这个域名为起点，结合样本分析与VT Graph关联分析形成以下关联图，可以确定123.160.10.16、180.97.220.35以及123.249.9.157这三个IP是用于作为木马的CNC地址以及木马分发地址。在2018年5月24日域名liancanmou.xyz从指向123.249.9.157被换位指向180.97.220.35这个IP。

[![](https://p3.ssl.qhimg.com/t01e23fd8ae791e19ee.png)](https://p3.ssl.qhimg.com/t01e23fd8ae791e19ee.png)

 

PassiveDNS相关信息
<td rowspan="6" valign="top" width="175">liancanmou.xyz</td><td valign="top" width="143">180.97.220.35</td><td valign="top" width="288">江苏镇江 (电信) IDC服务器</td><td valign="top" width="103">2018-5-24</td>



江苏镇江 (电信) IDC服务器
<td valign="top" width="143">123.249.9.157</td><td valign="top" width="288">贵州省黔西南布依族苗族自治州 电信IDC机房 电信</td><td valign="top" width="103">2018-05-22</td>

贵州省黔西南布依族苗族自治州 电信IDC机房 电信
<td valign="top" width="143">123.160.10.16</td><td valign="top" width="288">河南省新乡市 电信</td><td valign="top" width="103">2018-05-14</td>

河南省新乡市 电信
<td valign="top" width="143">123.249.9.15</td><td valign="top" width="288">贵州省黔西南布依族苗族自治州 电信IDC机房 电信</td><td valign="top" width="103">2018-05-11</td>

贵州省黔西南布依族苗族自治州 电信IDC机房 电信
<td valign="top" width="143">123.249.79.250</td><td valign="top" width="288">贵州省黔西南布依族苗族自治州 电信IDC机房 电信</td><td valign="top" width="103">2018-04-27</td>

贵州省黔西南布依族苗族自治州 电信IDC机房 电信
<td valign="top" width="143">103.248.220.196</td><td valign="top" width="288">中国香港 IDC机房</td><td valign="top" width="103">2018-04-22</td>

中国香港 IDC机房
<td rowspan="2" valign="top" width="175">wwt.liancanmou.xyz</td><td valign="top" width="143">180.97.220.35</td><td valign="top" width="288">江苏镇江 (电信) IDC服务器</td><td valign="top" width="103">2018-05-22</td>

180.97.220.35

2018-05-22
<td valign="top" width="143">123.160.10.16</td><td valign="top" width="288">河南省新乡市 电信</td><td valign="top" width="103">2018-05-11</td>

河南省新乡市 电信
<td valign="top" width="175">jch.liancanmou.xyz</td><td valign="top" width="143">180.97.220.35</td><td valign="top" width="288">江苏镇江 (电信) IDC服务器</td><td valign="top" width="103">2018-05-21</td>

180.97.220.35

2018-05-21
<td valign="top" width="175">web.liancanmou.xyz</td><td valign="top" width="143">123.249.9.157</td><td valign="top" width="288">贵州省黔西南布依族苗族自治州 电信IDC机房 电信</td><td valign="top" width="103">2018-05-14</td>

123.249.9.157

2018-05-14
<td rowspan="4" valign="top" width="175">www.liancanmou.xyz</td><td valign="top" width="143">123.249.9.157</td><td valign="top" width="288">贵州省黔西南布依族苗族自治州 电信IDC机房 电信</td><td valign="top" width="103">2018-04-19</td>

123.249.9.157

2018-04-19
<td valign="top" width="143">123.249.9.15</td><td valign="top" width="288">贵州省黔西南布依族苗族自治州 电信IDC机房 电信</td><td valign="top" width="103">2018-04-27</td>

贵州省黔西南布依族苗族自治州 电信IDC机房 电信
<td valign="top" width="143">123.249.79.250</td><td valign="top" width="288">贵州省黔西南布依族苗族自治州 电信IDC机房 电信</td><td valign="top" width="103">2018-04-27</td>

贵州省黔西南布依族苗族自治州 电信IDC机房 电信
<td valign="top" width="143">103.248.220.196</td><td valign="top" width="288">中国香港 IDC机房</td><td valign="top" width="103">2018-04-19</td>

中国香港 IDC机房

### 3.2事件溯源

**3.2.1域名注册信息**

[![](https://p2.ssl.qhimg.com/t01f925c9b0926ed525.png)](https://p2.ssl.qhimg.com/t01f925c9b0926ed525.png)



**3.2.2个人信息**

[![](https://p5.ssl.qhimg.com/t01f0974d12ef63768c.png)](https://p5.ssl.qhimg.com/t01f0974d12ef63768c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0136d5ad936cce4b36.png)



## 四．IoCs

liancanmou.xyz

web.liancanmou.xyz

jch.liancanmou.xyz

wwt.liancanmou.xyz

wwv.liancanmou.xyz

[www.liancanmou.xyz](http://www.liancanmou.xyz)

[http://180.97.220.35:3066/Linux4.7](http://180.97.220.35:3066/Linux4.7)

[http://123.160.10.16:3097/gy.exe](http://123.160.10.16:3097/gy.exe)

[http://180.97.220.35:3066/33](http://180.97.220.35:3066/33)

[http://180.97.220.35:3066/32](http://180.97.220.35:3066/32)

180.97.220.35

123.249.9.157

123.160.10.16

123.249.9.15

123.249.79.250

103.248.220.196

180.97.220.35

123.160.10.16

180.97.220.35

123.249.9.157

123.249.9.157

123.249.9.15

123.249.79.250

103.248.220.196

892833AB52DAA816918041670519EB6351AE7EC2DB7AF2C97F3AB5EE214DA173

4A2FB58342D549347D32E54C3DA466A19BFD66364825AC7F2257995356F09AFD

74D4776A76AD3BCB578C9757D9F18A6ADFFE8802C43E5E59B14C4E905664733D

DBC7FC7748BD201C54B2A0189396F3101C18127A715E480C8CB808F07137822A
