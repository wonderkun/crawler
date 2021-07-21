> 原文链接: https://www.anquanke.com//post/id/221632 


# KONNI APT组织伪装安全功能应用的攻击活动剖析


                                阅读量   
                                **233523**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01eac4d19531e13476.jpg)](https://p5.ssl.qhimg.com/t01eac4d19531e13476.jpg)



## 概述：

KONNI是一类远控木马病毒，很早之前就由思科Talos团队披露过。在2014年的时候就开始活跃起来了。针对的主要攻击对象有俄罗斯、韩国等地区。在PaloAlto团队的研究中发现此类木马病毒家族与Nokki有很多相似之处，疑似这个与东亚的APT组织存在关联性。此后Konni被当做疑似具有东亚背景的APT组织。

暗影实验室根据捕获的样本发现，此样本仿冒安全软件，以检测用户设备安全情况为诱饵，诱导用户使用此软件。用户安装应用之后向主控地址请求远控命令，获取用户联系人、短信、应用安装列表等信息，将获取的隐私信息上传到服务器。



## 1. 样本信息

**MD5：**0ce1648ff7553189e5b5db2252e27fd5

**包名：**com.json

**应用名：**AoneSmmitz

**安装图标：**

[![](https://p0.ssl.qhimg.com/t0184861280fe5a8ef6.png)](https://p0.ssl.qhimg.com/t0184861280fe5a8ef6.png)



## 2. 恶意行为综述

该程序一款仿冒检测手机漏洞的安全软件。用户运行后提示用户这个工具是检测设备漏洞的工具，当用户点击检测选项，提示用户此设备安全。其实际行为是向指定远控发送请求，获取一个txt远控文件，txt远控文件当中包含远控指令，根据远控指令获取用户包括短信、联系人、应用安装列表等用户隐私数据，将获取的用户隐私数据上传到指定服务器。



## 3. 运行流程图

** 仿冒安全软件，诱导用户下载安装，用户安装后，仿冒安全功能诱导用户使用，开启电源锁常驻后台运行，向服务器请求远控指令，执行远控指令，获取用户短信、联系人、应用安装列表、sd卡文件名称等信息，将获取的隐私信息上传到服务器。**

[![](https://p1.ssl.qhimg.com/t01e66ae01e7fed0b7a.png)](https://p1.ssl.qhimg.com/t01e66ae01e7fed0b7a.png)

**图3-1 程序运行流程图**



## 4. 技术原理分析

### **4.1 仿冒安全应用**

仿冒安全软件AoneSmmitz诱导用户安装，当用户打开软件，提示用户这个工具是检测用户设备有没有漏洞的工具，当用户点击开始检测，返回用户的是您的设备无安全漏洞。从功能上仿冒安全软件，让用户放松警惕。

仿冒AoneSmmitz应用：

[![](https://p4.ssl.qhimg.com/t019ad3b1fff74c8e40.png)](https://p4.ssl.qhimg.com/t019ad3b1fff74c8e40.png)

**图4-1 仿冒AoneSmmitz软件**

提示用此工具为检测设备漏洞工具：

[![](https://p0.ssl.qhimg.com/t01310e6049465c8c32.png)](https://p0.ssl.qhimg.com/t01310e6049465c8c32.png)

**图4-2提示检测漏洞**

向用户反馈经检测结果，设备无漏洞：

[![](https://p0.ssl.qhimg.com/t01df787f6c9373bc3f.png)](https://p0.ssl.qhimg.com/t01df787f6c9373bc3f.png)

**图4-3 反馈设备无漏洞信息**

### **4.2 程序加载运行**

恶意程序在诱导用户安装完成之后，向主控地址请求远控文本。获取用户IMEI、系统版本信息，用来区别用户的唯一性。设置电源锁，当屏幕处于关闭状态时，保障恶意程序的监听服务处于监听状态，确保对用户处于一直监听状态。

**1）向主控地址请求远控文本，请求之后向用户反馈远控文件。主控地址是：http://cloudsec***service.net/。**

**初始化地址：**

[![](https://p4.ssl.qhimg.com/t0111f340d3decdc74e.png)](https://p4.ssl.qhimg.com/t0111f340d3decdc74e.png)

**图4-4 初始化地址**

向主控地址发送txt文本请求：

[![](https://p1.ssl.qhimg.com/t0136f4943bd7d0fed6.png)](https://p1.ssl.qhimg.com/t0136f4943bd7d0fed6.png)

**图4-5 向主控发送远控文本请求**

获取用户IMEI、设备系统版本等信息，用来区别用户的唯一性：

[![](https://p3.ssl.qhimg.com/t01399f2ec7a64de48d.png)](https://p3.ssl.qhimg.com/t01399f2ec7a64de48d.png)

**图4-6 获取用户IMEI等信息**

2）设置电源锁，当屏幕处于关闭状态时，保障恶意程序的监听服务处于监听状态，确保对用户处于一直监听状态。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d231e7d589f25da4.png)

**图4-7 开启电源锁**

### **4.3 远程控制**

恶意程序向服务器请求远控文件之后获取远控文件，恶意程序根据远控文件当中的内容来区分远控指令。获取用户通讯录、获取用户短信、获取外部存储器文件目录、获取已安装应用列表数据等隐私数据。将获取的用户隐私信息上传到指定服务器。

**4.3.1 获取信息**

1）请求的远控文件，解析远控指令。

请求的远控文件：

http://cloudsecur***ervice.net/json/files/To_5063967640744206.txt

[![](https://p4.ssl.qhimg.com/t01e65ae098a613ee2f.png)](https://p4.ssl.qhimg.com/t01e65ae098a613ee2f.png)

图4-8 请求远控文件

读取远控文件，解析远控指令：

[![](https://p4.ssl.qhimg.com/t01abe1d8776d27e465.png)](https://p4.ssl.qhimg.com/t01abe1d8776d27e465.png)

图4-9 解析远控指令

2）恶意程序的远控指令。

指令列表：
<td data-row="1">**远控指令**</td><td data-row="1"></td><td data-row="1">**远控指令的意义**</td><td data-row="1"></td>
<td data-row="2">del_file</td><td data-row="2"></td><td data-row="2">删除指定文件</td><td data-row="2"></td>
<td data-row="3">del_sms</td><td data-row="3"></td><td data-row="3">删除指定短信</td><td data-row="3"></td>
<td data-row="4">download</td><td data-row="4"></td><td data-row="4">下载文件</td><td data-row="4"></td>
<td data-row="5">get_account</td><td data-row="5"></td><td data-row="5">获取用户账户信息</td><td data-row="5"></td>
<td data-row="6">get_app</td><td data-row="6"></td><td data-row="6">采集用户安装的所有APP信息</td><td data-row="6"></td>
<td data-row="7">get_contact</td><td data-row="7"></td><td data-row="7">获取联系人数据</td><td data-row="7"></td>
<td data-row="8">get_keylog</td><td data-row="8"></td><td data-row="8">获取键盘记录数据</td><td data-row="8"></td>
<td data-row="9">get_sdcard</td><td data-row="9"></td><td data-row="9">获得sd卡的文件目录</td><td data-row="9"></td>
<td data-row="10">get_sms</td><td data-row="10"></td><td data-row="10">获取短信内容</td><td data-row="10"></td>
<td data-row="11">get_time</td><td data-row="11"></td><td data-row="11">获取时间</td><td data-row="11"></td>
<td data-row="12">get_user</td><td data-row="12"></td><td data-row="12">获取手机基本系信息如IMEI、用户手机号、OSType、OSAPI</td><td data-row="12"></td>
<td data-row="13">open_app</td><td data-row="13"></td><td data-row="13">打开APP</td><td data-row="13"></td>
<td data-row="14">open_dlg</td><td data-row="14"></td><td data-row="14">弹框</td><td data-row="14"></td>
<td data-row="15">open_web</td><td data-row="15"></td><td data-row="15">打开网页</td><td data-row="15"></td>
<td data-row="16">screen</td><td data-row="16"></td><td data-row="16">截屏</td><td data-row="16"></td>
<td data-row="17">send_sms</td><td data-row="17"></td><td data-row="17">发送短信</td><td data-row="17"></td>
<td data-row="18">uninstall_app</td><td data-row="18"></td><td data-row="18">卸载APP</td><td data-row="18"></td>
<td data-row="19">upload</td><td data-row="19"></td><td data-row="19">上传文件</td><td data-row="19"></td>
<td data-row="20">volume</td><td data-row="20"></td><td data-row="20">获取文件系统主目录</td><td data-row="20"></td>

3）解析远控文件当中的远控指令，当指令是get_contact，将bGetContract的值设置为true，当bGetContract的值为true时，获取用户联系人数据。

**设置bGetContract的值为true：**

[![](https://p3.ssl.qhimg.com/t01169037085f01db93.png)](https://p3.ssl.qhimg.com/t01169037085f01db93.png)

**图4-11 设置bGetContract的值**

获取用户联系人数据。

[![](https://p5.ssl.qhimg.com/t017bdf160ea3a30d54.png)](https://p5.ssl.qhimg.com/t017bdf160ea3a30d54.png)

**图4-12 获取用户联系人数据**

4）解析远控文件当中的远控指令，当指令是bGetSms，将bGetSms的值设置为true，当bGetSms的值为true时，获取用户短信。

**设置bGetSms的值为true：**

[![](https://p3.ssl.qhimg.com/t01e28deab5a9beeb0b.png)](https://p3.ssl.qhimg.com/t01e28deab5a9beeb0b.png)

**图4-13 设置bGetSms的值为true**

获取用户短信。

[![](https://p4.ssl.qhimg.com/t01196e53ffd0d726b9.png)](https://p4.ssl.qhimg.com/t01196e53ffd0d726b9.png)

**图4-14 获取用户短信**

5）解析远控文件当中的远控指令，当指令是get_app，将bGetApp的值设置为true，当bGetApp的值为true时，获取用户安装的应用程序信息。

**设置bGetApp的值为true：**

[![](https://p4.ssl.qhimg.com/t01fe05a67e850da9a4.png)](https://p4.ssl.qhimg.com/t01fe05a67e850da9a4.png)

**图4-15 设置设置bGetApp的值为true**

获取用户安装的应用程序信息。

[![](https://p3.ssl.qhimg.com/t014fe4a48eaefd5102.png)](https://p3.ssl.qhimg.com/t014fe4a48eaefd5102.png)

**图4-16 获取用户安装的应用程序信息**

6）解析远控文件当中的远控指令，当指令是get_sdcard，将get_sdcard的值设置为true，当get_sdcard的值为true时，获取用户sd卡目录。

**设置get_sdcard的值为true:**

[![](https://p5.ssl.qhimg.com/t01aec4fb303d65375a.png)](https://p5.ssl.qhimg.com/t01aec4fb303d65375a.png)

**图4-17 设置get_sdcard的值为true**

获取用户sd卡目录。

[![](https://p1.ssl.qhimg.com/t013d7fe06e3f1e4800.png)](https://p1.ssl.qhimg.com/t013d7fe06e3f1e4800.png)

**图4-18 获取用户sd目录**

7）解析远控文件当中的远控指令，当指令是get_account，将get_account的值设置为true，当get_account的值为true时，获取用户账户信息。

**设置get_account的值为true：**

[![](https://p3.ssl.qhimg.com/t016c71c51898891b89.png)](https://p3.ssl.qhimg.com/t016c71c51898891b89.png)

**图4-19 设置get_account的值为true**

获取用户账号信息。

[![](https://p3.ssl.qhimg.com/t016db96dde81ad0b32.png)](https://p3.ssl.qhimg.com/t016db96dde81ad0b32.png)

**图4-20 获取用户账号信息**

**4.3.2 上传信息**

1）解析远控文件当中的远控指令，当指令是upload，将bUpload的值设置为true，当bUpload的值为true时，获取用户隐私信息。

设置bUpload的值为true：

[![](https://p2.ssl.qhimg.com/t01e3c15c840a4c9e1d.png)](https://p2.ssl.qhimg.com/t01e3c15c840a4c9e1d.png)

**图4-21 设置bUpload的值为true**

获取用户隐私信息：

[![](https://p4.ssl.qhimg.com/t0136ff60f50034c356.png)](https://p4.ssl.qhimg.com/t0136ff60f50034c356.png)

**图4-22 获取用户隐私信息**

2）上传用户隐私信息，上传地址是http://cloudsec****service.net/json/up.php。

上传用户IMEI等信息。

[![](https://p3.ssl.qhimg.com/t010a2639365257c641.png)](https://p3.ssl.qhimg.com/t010a2639365257c641.png)

**图4-23 上传IMEI等信息**

上传用通信录信息。

[![](https://p1.ssl.qhimg.com/t01522398752f29ef43.png)](https://p1.ssl.qhimg.com/t01522398752f29ef43.png)

**图4-24 上传用户通讯录**

上传用户短信信息。

[![](https://p3.ssl.qhimg.com/t01d5bc13a5ce8ffdd0.png)](https://p3.ssl.qhimg.com/t01d5bc13a5ce8ffdd0.png)

**图4-25 上传用户短信信息**

上传用户安装应用列表信息。

[![](https://p2.ssl.qhimg.com/t016a59135d16bcf4db.png)](https://p2.ssl.qhimg.com/t016a59135d16bcf4db.png)

**图4-26 上传用户应用列表信息**



## 5. 扩展分析

### **5.1 样本信息**
<td class="ql-align-justify" data-row="1">MD5</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">包名</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">通讯地址</td><td data-row="1"></td>
<td class="ql-align-justify" data-row="2">0ce1648ff7553189e5b5db2252e27fd5</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">com.json</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">http://cloudse***tyservice.net/</td><td data-row="2"></td>

### **5.2 样本域名信息**
<td data-row="1">域名</td><td data-row="1"></td><td data-row="1">IP</td><td data-row="1"></td><td data-row="1">归属地</td><td data-row="1"></td>
<td data-row="2">http://cloud***trityservice.net/</td><td data-row="2"></td><td data-row="2">​27.255.79.205</td><td data-row="2"></td><td data-row="2">韩国 ehost数据中心</td><td data-row="2"></td>



## 6. 安全建议
1. 安全类软件，建议去正规的应用市场下载、去官方下载。
1. 在手机当中安装必要的安全软件，并保持安全软件更新。
1. 关注“暗影安全实验室”微信公众号，我们将持续关注安全事件。