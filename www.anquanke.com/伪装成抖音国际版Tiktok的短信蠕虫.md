> 原文链接: https://www.anquanke.com//post/id/212758 


# 伪装成抖音国际版Tiktok的短信蠕虫


                                阅读量   
                                **132173**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0195db8a66ae7fb695.jpg)](https://p1.ssl.qhimg.com/t0195db8a66ae7fb695.jpg)



**概述：**

近期安全员监测到一款仿冒Tiktok的短信蠕虫，该短信蠕虫最明显的特点就是针对Android系统版本高于6.0以上的设备，由于Android版本的更新迭代，现在大部分设备已经更新到较高的版本，通过不完全统计，Android系统版本6.0以上的设备已经超过了80%，这也促使恶意程序要适配更高版本的设备，因此该仿冒Tiktok的短信蠕虫如果传播开，可以覆盖更大面积的设备。



## 1．样本运行流程

应用首次运行检测并申请大量敏感权限，如果未能授予权限，则重复申请，直至申请敏感权限成功，进而开启恶意服务器获取通讯录联系人，并遍历联系人发送指定短信内容，短信包容包含该类恶意程序，程序正常进入后，则是通过大量广告谋取利益。

[![](https://p2.ssl.qhimg.com/t018fb294b62a27cac6.png)](https://p2.ssl.qhimg.com/t018fb294b62a27cac6.png)

图1 样本运行流程图



## 2．样本详细信息

### **2.1 盗版程序详细信息：**
<td data-row="1">程序名称</td><td data-row="1"></td><td data-row="1">Tiktok Pro</td><td data-row="1"></td>
<td data-row="2">程序包名</td><td data-row="2"></td><td data-row="2">com.benstokes.pathakschook</td><td data-row="2"></td>
<td data-row="3">程序MD5</td><td data-row="3"></td><td data-row="3">B028D2A6FA96FB493991700F5B0410D3</td><td data-row="3"></td>
<td data-row="4">签名信息</td><td data-row="4"></td><td data-row="4">C=debugging</td><td data-row="4"></td>
<td data-row="5">签名MD5</td><td data-row="5"></td><td data-row="5">C13F92D0397DA7423A4142BFA9A5873E</td><td data-row="5"></td>
<td data-row="6">图标</td><td data-row="6"></td><td data-row="6">[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011c222f3cc0daf765.png)</td><td data-row="6"></td>

### **2.2 正版程序详细信息：**
<td data-row="1">程序名称</td><td data-row="1"></td><td data-row="1">TikTok</td><td data-row="1"></td>
<td data-row="2">程序包名</td><td data-row="2"></td><td data-row="2">com.ss.android.ugc.trill</td><td data-row="2"></td>
<td data-row="3">程序MD5</td><td data-row="3"></td><td data-row="3">78ACEACF4BB02D19174A2801F32257EC</td><td data-row="3"></td>
<td data-row="4">签名信息</td><td data-row="4"></td><td data-row="4">CN=Micro Cao, OU=ByteDance, O=ByteDance, L=Beijing, ST=Beijing, C=CN</td><td data-row="4"></td>
<td data-row="5">签名MD5</td><td data-row="5"></td><td data-row="5">AEA615AB910015038F73C47E45D21466</td><td data-row="5"></td>
<td data-row="6">图标</td><td data-row="6"></td><td data-row="6">[![](https://p0.ssl.qhimg.com/t01b74c2ee952dbde2f.png)](https://p0.ssl.qhimg.com/t01b74c2ee952dbde2f.png)</td><td data-row="6"></td>



## 3．技术原理分析

程序启动后首先判断通讯录、短信、定位等敏感权限是否打开，未打开则一一动态申请，权限开启后，程序启动恶意服务，后台私自获取用户通讯录联系人，接着遍历所有联系人并发送指定的短信内容，短信内容即为提醒用户更新最新版Tiktok，并附有链接，实则下载该恶意程序，程序主要通过广告盈利，即通过该恶意蠕虫，一传十，十传百，从而让更多人的手机成为肉鸡，来浏览设定好的广告并谋取利益。

### **3.1 程序启动初始化**

程序启动判断是否开启敏感权限，如果开启，则启动恶意服务，后台获取通讯录联系人，群发包含该恶意程序的短信。

[![](https://p5.ssl.qhimg.com/t013fdbee08889e5df5.png)](https://p5.ssl.qhimg.com/t013fdbee08889e5df5.png)

图2 程序启动初始化

启动时申请的权限：

[![](https://p1.ssl.qhimg.com/t01d83e5a7a7e3c6bc8.png)](https://p1.ssl.qhimg.com/t01d83e5a7a7e3c6bc8.png)

[![](https://p5.ssl.qhimg.com/t01904add2cfc38229d.png)](https://p5.ssl.qhimg.com/t01904add2cfc38229d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017de741705df99900.png)

图3 程序初始化申请的权限

### **3.2 用户登录仿冒Tiktok**

程序虽然设置了登录界面，但是用户输入的账户密码并未上传，这也说明了该程序的最终目的就是通过广告盈利。

[![](https://p2.ssl.qhimg.com/t01ee775fc075a1e935.png)](https://p2.ssl.qhimg.com/t01ee775fc075a1e935.png)

[![](https://p1.ssl.qhimg.com/t01327fd0fa8b06dc39.png)](https://p1.ssl.qhimg.com/t01327fd0fa8b06dc39.png)

[![](https://p4.ssl.qhimg.com/t015da3941acc398f04.png)](https://p4.ssl.qhimg.com/t015da3941acc398f04.png)

图4 通过更真实的界面伪装自己

### **3.3 获取通讯录群发短信**

恶意服务开启后，后台获取去通讯录联系人，遍历通讯录联系人发送指定短信，短信中包含该恶意程序链接。

获取通讯录联系人：

[![](https://p0.ssl.qhimg.com/t01bd00cd5fe2f5cb65.png)](https://p0.ssl.qhimg.com/t01bd00cd5fe2f5cb65.png)

图5 获取通讯录联系人

筛选后将通讯录联系人保存在数组中备用：

[![](https://p0.ssl.qhimg.com/t01fd0cdf8565a932f5.png)](https://p0.ssl.qhimg.com/t01fd0cdf8565a932f5.png)

遍历通讯录联系人发送指定短信内容：

[![](https://p1.ssl.qhimg.com/t0136cb854357cf1b4c.png)](https://p1.ssl.qhimg.com/t0136cb854357cf1b4c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016fe59db7db678925.png)

图6 遍历联系人准备发送短信

解密要发送的短信内容：

[![](https://p0.ssl.qhimg.com/t01265aee3f533a72fd.png)](https://p0.ssl.qhimg.com/t01265aee3f533a72fd.png)

[![](https://p1.ssl.qhimg.com/t01eb12edeefde75bbd.png)](https://p1.ssl.qhimg.com/t01eb12edeefde75bbd.png)

图7 发送带有恶意程序链接的传播短信

解密后字符串：

Enjoy Tiktok Videos and also make CreativeVideos again. Now Tiktok is only Available in (Tiktok pro) SoDownload from below.

Link: http://t***.cc/Tiktok pro

[![](https://p4.ssl.qhimg.com/t01734add9a9ec20c40.png)](https://p4.ssl.qhimg.com/t01734add9a9ec20c40.png)

图8 待发送短信截图

下载应用详细信息：
<td data-row="1">程序名称</td><td data-row="1"></td><td data-row="1">Tiktok Pro</td><td data-row="1"></td>
<td data-row="2">MD5</td><td data-row="2"></td><td data-row="2">EDB563FDCAB0AB0580FDEEFAD6FFF9AD</td><td data-row="2"></td>
<td data-row="3">包名</td><td data-row="3"></td><td data-row="3">com.benstokes.pathakschook</td><td data-row="3"></td>
<td data-row="4">所有者</td><td data-row="4"></td><td data-row="4">C=debugging</td><td data-row="4"></td>
<td data-row="5">证书MD5</td><td data-row="5"></td><td data-row="5">C13F92D0397DA7423A4142BFA9A5873E</td><td data-row="5"></td>
<td data-row="6">图标</td><td data-row="6"></td><td data-row="6">[![](https://p0.ssl.qhimg.com/t016bfc864746921ce6.png)](https://p0.ssl.qhimg.com/t016bfc864746921ce6.png)</td><td data-row="6"></td>

### **3.4 通过广告获利**

程序包含applovin和google广告，程序主要目的就是通过群发短信，让更多的人安装盗版的Tiktok，进而通过内置的广告获利：

广告模块：

[![](https://p5.ssl.qhimg.com/t01db61bddf57e8558a.png)](https://p5.ssl.qhimg.com/t01db61bddf57e8558a.png)

图9 程序嵌入的广告模块

AppLovin广告模块：

[![](https://p1.ssl.qhimg.com/t01c50f07c14bfb328a.png)](https://p1.ssl.qhimg.com/t01c50f07c14bfb328a.png)

[![](https://p1.ssl.qhimg.com/t01e92a43dd2a8988c9.png)](https://p1.ssl.qhimg.com/t01e92a43dd2a8988c9.png)

[![](https://p3.ssl.qhimg.com/t01504e043fbd06cb35.png)](https://p3.ssl.qhimg.com/t01504e043fbd06cb35.png)

图10 AppLovin广告模块



## 4．情报挖掘溯源

短信包含地址：http://t***.cc/Tiktokpro

短地址域名：t***.cc

域名对应IP:157.***.***.153 美国纽约州 纽约

[![](https://p2.ssl.qhimg.com/t01e6ff3ec21a63014b.png)](https://p2.ssl.qhimg.com/t01e6ff3ec21a63014b.png)

真实下载地址：https://raw.gi******nt.com/newtiktokpro/login/master/Tiktok%20pro.apk。

下载地址域名：raw.gi******nt.com。

域名对应IP：151.***.**.133 美国。

[![](https://p5.ssl.qhimg.com/t01910609ebda015fd6.png)](https://p5.ssl.qhimg.com/t01910609ebda015fd6.png)



## 5．IOCs

### **文件SHA1：**

6FAA034AB2F1154825A50897A2ACE54FBE87B3C1

324005D7DC633F89EA6108FA072B6C83F3EAF4FC

CFE7DCE6C4039FE709091703D2C1EE8071564999

11CD5C4C5F37D80A9DD3BBF6B1CB532F6C58370D

BAB55B26C840F0FA233E36A6C966EFBF4BA64E74

A0D4F9D00FDB903DCAD27E0A07623571CF2FDF54

25E27DB61F2E0C035CB4E16FA0D75002E7F07E26

DE72D4A582D4872168E6F4AD4DD03EC6E544B243

F8996B8DA8C4FA4084757FF171FE886E50015B84

CE62651512A26324CB50CF731B2D5A0BFEFA9B8F

### **C2**

t***.cc

raw.gi******nt.com
