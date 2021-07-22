> 原文链接: https://www.anquanke.com//post/id/181483 


# Donot团伙（APT-C-35）移动端新攻击框架工具分析


                                阅读量   
                                **268638**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01fd7bd5b1dd9da3cd.jpg)](https://p3.ssl.qhimg.com/t01fd7bd5b1dd9da3cd.jpg)



## 背景介绍

肚脑虫(APT-C-35)，由奇安信高级威胁研究团队持续跟踪发现并命名，其主要针对巴基斯坦等南亚地区国家进行网络间谍活动的组织。该组织主要针对政府机构等领域进行攻击，其中以窃取敏感信息为主。

自第一次发现该组织的攻击活动以来，奇安信威胁情报中心对该组织一直保持着持续跟踪，近期发现了其包名为com.tencent.mm(微信包名)最新的移动样本，相比于之前发现的Donot(肚脑虫)移动端程序，此次发现的程序对其代码结构进行了调整，但其C&amp;C和功能方面依然保持了之前Donot(肚脑虫)的风格。

同时在此期间也发现了在早期版本框架基础上修改的新样本，主要是对获取C&amp;C的方式做了改变，其舍弃硬编码C&amp;C方式，利用Google Docs(谷歌在线文档编辑系统)的方式来灵活改变C&amp;C信息。



## 诱饵分析

此次发现的名为” SafeShareV67”的移动app使用了腾讯微信包名（com.tencent.mm），其通过使用正规app的包名来伪装自己，其真实意图还未可知。同时对其代码框架分析，发现此次结构调整非常大，也对部分功能代码进行了混淆。可以大致判定此样本是经过精心准备的。

[![](https://p5.ssl.qhimg.com/t011a8cd8ac7d351338.png)](https://p5.ssl.qhimg.com/t011a8cd8ac7d351338.png)

并且发现该样本上传地印度:

[![](https://p1.ssl.qhimg.com/t01a57fbe447ed907a6.png)](https://p1.ssl.qhimg.com/t01a57fbe447ed907a6.png)



## 一．样本分析

我们所分析的样本基本信息如下：
<td valign="top" width="113">文件名称</td><td valign="top" width="398">SafeShareV67.apk</td>
<td valign="top" width="113">软件名称</td><td valign="top" width="398">Android Database Library</td>
<td valign="top" width="113">软件包名</td><td valign="top" width="398">com.tencent.mm</td>
<td valign="top" width="113">MD5</td><td valign="top" width="398">7BB0B6EB3383BE5CEC4B2EABF273C7F9</td>
<td valign="top" width="113">安装图标</td><td valign="top" width="398"></td>

### 1.1 样本行为描述

该恶意样本名称为“Android Database Library”（其包名为微信包名），通过伪装为Android数据库组件来诱骗用户安装使用，从而可以进一步实施恶意行为；样本运行后会弹出是否开启辅助功能设置框，并会隐藏自身图标，使用户放松警惕，从而达到保护自身的目的；恶意样本在用户手机运行后，会定时从固定服务端获取远程控制指令，从而实现不同的恶意功能，其相关的远控操作有：获取用户手机通话记录信息、获取用户手机通讯录信息、获取用户手机短信息、获取App输入的内容信息、获取外置存储卡文件列表信息、获取用户手机已安装软件列表等；恶意软件会将获取的用户信息保存在本地文件夹下，并上传至服务器。

### 1.2 样本基本信息

样本安装图标：

[![](https://p0.ssl.qhimg.com/t01c3988f1aab9a593f.png)](https://p0.ssl.qhimg.com/t01c3988f1aab9a593f.png)

运行界面：

[![](https://p3.ssl.qhimg.com/t01a7ffb50e56bc8c96.png)](https://p3.ssl.qhimg.com/t01a7ffb50e56bc8c96.png)

#### 1.2.1 样本申请权限列表

[![](https://p1.ssl.qhimg.com/t012f85f9245d180c47.png)](https://p1.ssl.qhimg.com/t012f85f9245d180c47.png)

### 1.3 详细分析过程

#### 1.3.1 诱骗用户运行并误导用户此程序为正常程序

通过伪装为Android数据库组件来诱导用户点击”OK”，同时跳转到系统的辅助功能界面，然后在后台运行程序。这样操作能误导用户认为此程序是一个android组件程序。

[![](https://p5.ssl.qhimg.com/t01d328194b4d0d8b83.png)](https://p5.ssl.qhimg.com/t01d328194b4d0d8b83.png)

#### 1.3.2 隐藏图标保护自身

样本运行以后则会隐藏删除自身图标，使用户放松警惕，从而达到保护自身的目的。

[![](https://p2.ssl.qhimg.com/t01166ed4967265e6df.png)](https://p2.ssl.qhimg.com/t01166ed4967265e6df.png)

#### 1.3.3 根据服务端下发的控制指令，进行相关的恶意操作

恶意样本在手机中运行后，会定时从服务端获取远程控制指令，从而实现不同的恶意功能，其相关的远控操作有：获取用户手机通话记录信息、获取用户手机通讯录信息、获取用户手机短信息、获取App输入的内容信息、获取外置存储卡文件列表信息、获取用户手机已安装软件列表等；恶意软件会将获取的用户信息保存在本地文件夹下，并上传至服务器。

1）定时从服务器中获取远控指令信息：

[![](https://p3.ssl.qhimg.com/t015cbcaa604c1c7ffd.png)](https://p3.ssl.qhimg.com/t015cbcaa604c1c7ffd.png)

2）对指令信息进行解析并下发对应的指令操作：

[![](https://p2.ssl.qhimg.com/t0146c5977eb4c636af.png)](https://p2.ssl.qhimg.com/t0146c5977eb4c636af.png)

3）相关的指令操作：
<td valign="top" width="77">指令</td><td valign="top" width="376">指令功能</td>
<td valign="top" width="77">Call</td><td valign="top" width="376">获取用户手机通话记录信息</td>
<td valign="top" width="77">CT</td><td valign="top" width="376">获取用户手机通讯录信息</td>
<td valign="top" width="77">SMS</td><td valign="top" width="376">获取用户手机短信息</td>
<td valign="top" width="77">Key</td><td valign="top" width="376">获取App输入的内容信息</td>
<td valign="top" width="77">Tree</td><td valign="top" width="376">获取外置存储卡文件列表信息</td>
<td valign="top" width="77">AC</td><td valign="top" width="376">获取Account信息</td>
<td valign="top" width="77">Net</td><td valign="top" width="376">获取WiFi、设备厂商等信息</td>
<td valign="top" width="77">CR</td><td valign="top" width="376">设置用户手机电话通话录音</td>
<td valign="top" width="77">LR</td><td valign="top" width="376">设定特定时间段录音</td>
<td valign="top" width="77">FS</td><td valign="top" width="376">文件上传开关</td>
<td valign="top" width="77">GP</td><td valign="top" width="376">获取地理位置信息</td>
<td valign="top" width="77">PK</td><td valign="top" width="376">获取用户手机已安装软件列表</td>
<td valign="top" width="77">CE</td><td valign="top" width="376">获取日历事件信息</td>
<td valign="top" width="77">Wapp</td><td valign="top" width="376">获取whatsapp聊天信息</td>

指令Call：获取用户手机通话记录信息

[![](https://p5.ssl.qhimg.com/t019880d43b3275ce25.png)](https://p5.ssl.qhimg.com/t019880d43b3275ce25.png)

指令CT：获取手机通讯录信息

[![](https://p3.ssl.qhimg.com/t0191fd0d04bab6d121.png)](https://p3.ssl.qhimg.com/t0191fd0d04bab6d121.png)

指令SMS：获取用户手机短信息

[![](https://p1.ssl.qhimg.com/t018d9b29929a542ead.png)](https://p1.ssl.qhimg.com/t018d9b29929a542ead.png)

[![](https://p0.ssl.qhimg.com/t015e00f805cc3bdf03.png)](https://p0.ssl.qhimg.com/t015e00f805cc3bdf03.png)

指令Key：获取App输入的内容信息

[![](https://p1.ssl.qhimg.com/t0132b8f0526aa2163c.png)](https://p1.ssl.qhimg.com/t0132b8f0526aa2163c.png)

指令Tree：获取外置存储卡文件列表信息

[![](https://p3.ssl.qhimg.com/t01541ac64a4caf03b0.png)](https://p3.ssl.qhimg.com/t01541ac64a4caf03b0.png)

[![](https://p3.ssl.qhimg.com/t01c240aba16250d997.png)](https://p3.ssl.qhimg.com/t01c240aba16250d997.png)

指令AC：获取Account信息

[![](https://p4.ssl.qhimg.com/t01a93507b2afc4bb98.png)](https://p4.ssl.qhimg.com/t01a93507b2afc4bb98.png)

指令Net：获取WiFi、设备厂商等信息

[![](https://p3.ssl.qhimg.com/t01309e762bb2da88f7.png)](https://p3.ssl.qhimg.com/t01309e762bb2da88f7.png)

[![](https://p5.ssl.qhimg.com/t0145fa7b60a4d1f3bc.png)](https://p5.ssl.qhimg.com/t0145fa7b60a4d1f3bc.png)

指令CR：设置用户手机电话通话录音

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017a581a0a95054030.png)

指令LR：设定特定时间段录音

[![](https://p5.ssl.qhimg.com/t01afef4e6b5e52c119.png)](https://p5.ssl.qhimg.com/t01afef4e6b5e52c119.png)

指令FS：文件上传开关

[![](https://p2.ssl.qhimg.com/t01fb4edbe2a837e34e.png)](https://p2.ssl.qhimg.com/t01fb4edbe2a837e34e.png)

指令GP：获取地理位置信息

[![](https://p3.ssl.qhimg.com/t015d6c195909bee982.png)](https://p3.ssl.qhimg.com/t015d6c195909bee982.png)

指令PK：获取用户手机已安装软件列表

[![](https://p3.ssl.qhimg.com/t01ab5cc30ab69d33c9.png)](https://p3.ssl.qhimg.com/t01ab5cc30ab69d33c9.png)

指令CE：获取日历事件信息

[![](https://p2.ssl.qhimg.com/t01dd1d26234f5ae1fd.png)](https://p2.ssl.qhimg.com/t01dd1d26234f5ae1fd.png)

指令Wapp：获取whatsapp聊天信息

[![](https://p5.ssl.qhimg.com/t01103c414cd909e793.png)](https://p5.ssl.qhimg.com/t01103c414cd909e793.png)



## 二．老框架新方式

近期奇安信红雨滴团队捕获到了Donot（肚脑虫）移动样本在老框架上利用Google Docs(谷歌在线文档编辑系统)的方式来获取C&amp;C信息，此方法能更灵活的改变C&amp;C信息。同时奇安信红雨滴团队在第一时间对其利用方式进行了披露：

[![](https://p4.ssl.qhimg.com/t01a2b0a802e8339c6a.png)](https://p4.ssl.qhimg.com/t01a2b0a802e8339c6a.png)

样本信息：
<td valign="top" width="113">文件名称</td><td valign="top" width="398">1278a5f65fc0c4a3babffcf1117db1c0.apk</td>
<td valign="top" width="113">软件名称</td><td valign="top" width="398">Sikh Net</td>
<td valign="top" width="113">软件包名</td><td valign="top" width="398">com.system.android.sikhnet</td>
<td valign="top" width="113">MD5</td><td valign="top" width="398">1278A5F65FC0C4A3BABFFCF1117DB1C0</td>
<td valign="top" width="113">安装图标</td><td valign="top" width="398">[![](https://p5.ssl.qhimg.com/t01ba26c43694ef1418.png)](https://p5.ssl.qhimg.com/t01ba26c43694ef1418.png)</td>

其样本的代码框架沿用了最早期的版本，如下图所示：

[![](https://p2.ssl.qhimg.com/t01be357d71973de478.png)](https://p2.ssl.qhimg.com/t01be357d71973de478.png)

其主要在获取C&amp;C的方式进行了改变，早期样本都是直接硬编码C&amp;C信息，而新捕获到的样本利用Google Docs(谷歌在线文档编辑系统)的方式来获取C&amp;C信息，这样就能灵活修改C&amp;C信息。此种方式获取C&amp;C信息，是Donot家族系列中首次使用。

最新获取C&amp;C方式:

[![](https://p0.ssl.qhimg.com/t010b3fa9bd3ce8b678.png)](https://p0.ssl.qhimg.com/t010b3fa9bd3ce8b678.png)

早期的硬编码写入C&amp;C方式：

[![](https://p0.ssl.qhimg.com/t01c9ff88dab0e7ba8a.png)](https://p0.ssl.qhimg.com/t01c9ff88dab0e7ba8a.png)

使用浏览器访问https://docs.google.com/uc?id=0B1RDq_Zx683GbDVBTmpWbFFuaDg后，则会提示保存file.txt的文件。

[![](https://p2.ssl.qhimg.com/t01b2218e410379c0bf.png)](https://p2.ssl.qhimg.com/t01b2218e410379c0bf.png)

下载file.txt后，发现其保存了其真实的远控服务器信息(151.236.11.222:50240)。

[![](https://p1.ssl.qhimg.com/t01fe6dcb5671ae32e9.png)](https://p1.ssl.qhimg.com/t01fe6dcb5671ae32e9.png)



## 三．工具演进

近期捕获的Donot（肚脑虫）样本与之前的历史框架进行比对发现，其框架在近期做了较大的调整。同时在最新发现的样本中，发现其在早期版本中利用Google Docs(谷歌在线文档编辑系统)的方式来获取C&amp;C信息。

代码对比：

早期版本：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f00e9554d5d0e262.png)

演变版本：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ccae1012b5cdb481.png)

新版本：

[![](https://p0.ssl.qhimg.com/t013491e091bdfebdc6.png)](https://p0.ssl.qhimg.com/t013491e091bdfebdc6.png)



## 总结

从本次捕获到的Donot（肚脑虫，APT-C-35）APT样本来看，该APT团伙依然以巴基斯坦相关人士作为首要攻击目标。通过其对代码框架的改变及在老版本利用Google Docs的方式来看，或许近期将发起新一波的网络间谍活动。

奇安信威胁情报中心红雨滴团队将继续关注Donot APT组织的最新进展。



## IOC

MD5：

7BB0B6EB3383BE5CEC4B2EABF273C7F9

103CFBC4F61DD642F9F44B8248545831

1278A5F65FC0C4A3BABFFCF1117DB1C0



## C&amp;C

whynotworkonit.top

genwar.drivethrough.top

151.236.11.222:50240
