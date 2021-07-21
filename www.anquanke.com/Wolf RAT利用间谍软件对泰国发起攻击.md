> 原文链接: https://www.anquanke.com//post/id/207185 


# Wolf RAT利用间谍软件对泰国发起攻击


                                阅读量   
                                **110183**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01130502b2ddc5313e.jpg)](https://p5.ssl.qhimg.com/t01130502b2ddc5313e.jpg)



**导读：**日前泰国用户及设备正在遭受Wolf间谍软件的攻击。经研究表明该恶意软件与WolfRAT有关。该恶意软件是基于DenDroid恶意软件的升级版本，其代码主要是通过对DenDroid恶意软件及网络上大量公共开源代码进行复制粘贴而成。该恶意软件通常伪装成一些合法服务应用，如GoogleService，GooglePlay、AdobeFlash插件进行传播。

暗影安全实验室对最新版Wolf间谍软件进行了分析，该恶意软件安装启动后在获取了用户设备敏感权限的情况下上传用户大量敏感信息、对用户通话记录进行录音、对用户设备进行录屏监控用户行为、其目前主要针对WhatsApp，FacebookMessenger和Line等社交软件进行截屏，窃取WhatsApp，FacebookMessenger和Line社交软件的通信信息。且该恶意软件可随时从服务器获取恶意软件更新包更新其恶意代码。

**[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017774b3195c9b6ae9.png)**

**[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01524cb9058800247f.png)**

**[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c6b914eb6e792d41.png)**

**图1-1恶意软件图标**



## 1.运行流程

恶意程序安装运行后会弹框请求大量敏感权限，如果用户不授予这些敏感权限，程序将无法获取用户大量敏感信息。之后该恶意软件便隐藏图标，在后台隐匿执行恶意行为。

[![](https://p2.ssl.qhimg.com/t01c9e1dbd5838634c5.png)](https://p2.ssl.qhimg.com/t01c9e1dbd5838634c5.png)

图2-1 恶意程序运行流程图



## 2.样本对比

Wolf间谍软件主要基于DenDroi恶意软件开发的，DenDroi恶意程序最初于2014年出现。源代码于2015年被泄漏。

[![](https://p2.ssl.qhimg.com/t01e122e348384dd156.png)](https://p2.ssl.qhimg.com/t01e122e348384dd156.png)

图2-2 Wolf与DenDroi恶意软件文件对比

此外该恶意软件还拥有屏幕录像功能。此功能是使用另一个开源软件包com.serenegiant实现的。

[![](https://p3.ssl.qhimg.com/t0100ae35a22644cad7.png)](https://p3.ssl.qhimg.com/t0100ae35a22644cad7.png)

图2-3 Wolf中使用了com.serenegiant开源软件包

恶意软件经历了几代更新，最新版本的恶意软件增加了com.jaredrummler和com.serenegiant包，用于实现执行shell指令以及录屏功能，不仅如此，主体程序中还增加了截屏、录音、录像以及监听通知消息的功能。

[![](https://p3.ssl.qhimg.com/t0108b72ee851bcdc35.png)](https://p3.ssl.qhimg.com/t0108b72ee851bcdc35.png)

图2-4 Wolf旧版本与新版本对比

我们根据旧版本和新版本Wolf间谍软件的服务器地址找到了该间谍软件的控制后台：旧版本的标题为”WolfIntelligence”,从这一点可以证明此间谍软件与WolfRAT有关联。

[![](https://p3.ssl.qhimg.com/t01064333c8cfff62ec.png)](https://p3.ssl.qhimg.com/t01064333c8cfff62ec.png)

图2-5 旧版本Wolf间谍软件控制后台

[![](https://p2.ssl.qhimg.com/t017502e0afadd6ea33.png)](https://p2.ssl.qhimg.com/t017502e0afadd6ea33.png)

图2-6新版本Wolf间谍软件控制后台



## 3.技术分析

恶意软件在执行恶意行为前检测应用是否在模拟机环境下运行。

[![](https://p3.ssl.qhimg.com/t01d0aa66c31259c462.png)](https://p3.ssl.qhimg.com/t01d0aa66c31259c462.png)

图2-7 检测模拟机环境

接着配置完参数设置后，获取并上传用户通讯录、通话记录、短信、账户、图片、设备等信息。

[![](https://p4.ssl.qhimg.com/t01dd8f301caa8d1a28.png)](https://p4.ssl.qhimg.com/t01dd8f301caa8d1a28.png)

图2-8 窃取用户敏感信息

获取用户通话记录：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b0bc4d105d69ab9e.png)

图2-9 获取用户通话记录

上传用户通话记录，应用在上传用户通话记录信息时会带上“getCallHistory”命令标识。

[![](https://p3.ssl.qhimg.com/t018b9ed562e4cdd1a8.png)](https://p3.ssl.qhimg.com/t018b9ed562e4cdd1a8.png)

图2-10 上传通话记录

获取用户联系人信息：

[![](https://p0.ssl.qhimg.com/t013e5ea9804d49ff4b.png)](https://p0.ssl.qhimg.com/t013e5ea9804d49ff4b.png)

图2-11 获取用户联系人信息

上传用户设备联系人信息：应用在上传用户联系人信息时会带上“getContacts”命令标识。

[![](https://p3.ssl.qhimg.com/t017db9cc7742168834.png)](https://p3.ssl.qhimg.com/t017db9cc7742168834.png)

图2-12上传用户联系人信息

执行shell指令“dumpsysactivity”，检测用户设备应用运行状态，如果检测到WhatsApp、Facebook、Line应用的某界面处于活跃状态，对这些界面进行截屏。

[![](https://p2.ssl.qhimg.com/t01bdd0d9376a7d8747.png)](https://p2.ssl.qhimg.com/t01bdd0d9376a7d8747.png)

图2-13 检测WhatsApp、Facebook、Line组件运行状态

恶意软件想通过截屏操作获取用户设备WhatsApp、Facebook、Line社交软件的通信信息。将截取的图片保存在mnt/sdcard/System/screenshots/CAP.png目录下。

[![](https://p5.ssl.qhimg.com/t014cd95a1d80ed3976.png)](https://p5.ssl.qhimg.com/t014cd95a1d80ed3976.png)

图2-14 对WhatsApp、Facebook、Line应用进行截屏

### **3.1远程控制**

在获取并上传用户设备通讯录、通话记录、短信等敏感信息后，恶意程序与服务器通信。并下发远控指令。

[![](https://p0.ssl.qhimg.com/t01f509cca3d53eee94.png)](https://p0.ssl.qhimg.com/t01f509cca3d53eee94.png)

图2-15 服务器下发指令数据包

指令列表：
<td data-row="1">指令</td><td data-row="1">功能</td>
<td class="ql-align-justify" data-row="2">mediaAlert</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">获取并播放铃声</td><td data-row="2"></td>
<td class="ql-align-justify" data-row="3">mediavolumeup</td><td data-row="3"></td><td class="ql-align-justify" data-row="3">调节设备音量，调高音量</td><td data-row="3"></td>
<td class="ql-align-justify" data-row="4">mediavolumedown</td><td data-row="4"></td><td class="ql-align-justify" data-row="4">调节设备音量，降低音量</td><td data-row="4"></td>
<td class="ql-align-justify" data-row="5">ringervolumeup</td><td data-row="5"></td><td class="ql-align-justify" data-row="5">调高音量回放</td><td data-row="5"></td>
<td class="ql-align-justify" data-row="6">ringervolumedown</td><td data-row="6"></td><td class="ql-align-justify" data-row="6">调低音量回放</td><td data-row="6"></td>
<td class="ql-align-justify" data-row="7">screenon</td><td data-row="7"></td><td class="ql-align-justify" data-row="7">设置电源锁，保持屏幕开启，防止设备休眠的方式</td><td data-row="7"></td>
<td class="ql-align-justify" data-row="8">recordcalls</td><td data-row="8"></td><td class="ql-align-justify" data-row="8">设置recordcalls参数</td><td data-row="8"></td>
<td class="ql-align-justify" data-row="9">settimeout</td><td data-row="9"></td><td class="ql-align-justify" data-row="9">设置settimeout参数</td><td data-row="9"></td>
<td class="ql-align-justify" data-row="10">intercept</td><td data-row="10"></td><td class="ql-align-justify" data-row="10">设置intercept参数</td><td data-row="10"></td>
<td class="ql-align-justify" data-row="11">sendtext</td><td data-row="11"></td><td class="ql-align-justify" data-row="11">发送指定内容短信给指定联系人</td><td data-row="11"></td>
<td class="ql-align-justify" data-row="12">sendcontacts</td><td data-row="12"></td><td class="ql-align-justify" data-row="12">向用户联系人发送短信</td><td data-row="12"></td>
<td class="ql-align-justify" data-row="13">callnumber</td><td data-row="13"></td><td class="ql-align-justify" data-row="13">拨打电话给指定联系人</td><td data-row="13"></td>
<td class="ql-align-justify" data-row="14">deletecalllognumber</td><td data-row="14"></td><td class="ql-align-justify" data-row="14">删除指定号码通讯录</td><td data-row="14"></td>
<td class="ql-align-justify" data-row="15">openwebpage</td><td data-row="15"></td><td class="ql-align-justify" data-row="15">打开指定url网页</td><td data-row="15"></td>
<td class="ql-align-justify" data-row="16">updateapp</td><td data-row="16"></td><td class="ql-align-justify" data-row="16">从指定服务器下载apk文件更新应用</td><td data-row="16"></td>
<td class="ql-align-justify" data-row="17">promptupdate</td><td data-row="17"></td><td class="ql-align-justify" data-row="17">临时更新应用</td><td data-row="17"></td>
<td class="ql-align-justify" data-row="18">promptuninstall</td><td data-row="18"></td><td class="ql-align-justify" data-row="18">卸载应用</td><td data-row="18"></td>
<td class="ql-align-justify" data-row="19">changedirectory(</td><td data-row="19"></td><td class="ql-align-justify" data-row="19">更改配置文件下需要获取文件信息的的参数值更改为以下外部存储下的以下文件或目录：System”, “System Media”, “Saved Files”, “Recent Media”, “Temporary</td><td data-row="19"></td>
<td class="ql-align-justify" data-row="20">uploadfiles</td><td data-row="20"></td><td class="ql-align-justify" data-row="20">上传/storage/emulated/0/System/Calls、/storage/emulated/0/System/Audio、/storage/emulated/0/System/Videos、/storage/emulated/0/System/Pictures目录下文件</td><td data-row="20"></td>
<td class="ql-align-justify" data-row="21">deletefiles</td><td data-row="21"></td><td class="ql-align-justify" data-row="21">删除/storage/emulated/0/System/Calls文件</td><td data-row="21"></td>
<td class="ql-align-justify" data-row="22">getbrowserhistory</td><td data-row="22"></td><td class="ql-align-justify" data-row="22">未获取浏览器记录</td><td data-row="22"></td>
<td class="ql-align-justify" data-row="23">getbrowserbookmarks</td><td data-row="23"></td><td class="ql-align-justify" data-row="23">未获取浏览器书签</td><td data-row="23"></td>
<td class="ql-align-justify" data-row="24">getcallhistory</td><td data-row="24"></td><td class="ql-align-justify" data-row="24">获取并上传通话记录信息</td><td data-row="24"></td>
<td class="ql-align-justify" data-row="25">getcontacts</td><td data-row="25"></td><td class="ql-align-justify" data-row="25">获取并上传联系人信息</td><td data-row="25"></td>
<td class="ql-align-justify" data-row="26">getWhatsApp</td><td data-row="26"></td><td class="ql-align-justify" data-row="26">获取并上传WhatsApp信息</td><td data-row="26"></td>
<td class="ql-align-justify" data-row="27">getinboxsms</td><td data-row="27"></td><td class="ql-align-justify" data-row="27">获取并上传用户短信箱信息</td><td data-row="27"></td>
<td class="ql-align-justify" data-row="28">getsentsms</td><td data-row="28"></td><td class="ql-align-justify" data-row="28">获取并上传用户已发送短信息</td><td data-row="28"></td>
<td class="ql-align-justify" data-row="29">deletesms</td><td data-row="29"></td><td class="ql-align-justify" data-row="29">删除用户设备上指定的短信息</td><td data-row="29"></td>
<td class="ql-align-justify" data-row="30">getuseraccounts</td><td data-row="30"></td><td class="ql-align-justify" data-row="30">获取并上传用户账号信息</td><td data-row="30"></td>
<td class="ql-align-justify" data-row="31">getinstalledapps</td><td data-row="31"></td><td class="ql-align-justify" data-row="31">获取并上传已安装应用信息</td><td data-row="31"></td>
<td class="ql-align-justify" data-row="32">httpflood</td><td data-row="32"></td><td class="ql-align-justify" data-row="32">Socket通信</td><td data-row="32"></td>
<td class="ql-align-justify" data-row="33">openapp</td><td data-row="33"></td><td class="ql-align-justify" data-row="33">启动指定应用</td><td data-row="33"></td>
<td class="ql-align-justify" data-row="34">opendialog</td><td data-row="34"></td><td class="ql-align-justify" data-row="34">打开指定内容的dialog框</td><td data-row="34"></td>
<td class="ql-align-justify" data-row="35">uploadpictures</td><td data-row="35"></td><td class="ql-align-justify" data-row="35">上传用户设备图片</td><td data-row="35"></td>
<td class="ql-align-justify" data-row="36">transferbot</td><td data-row="36"></td><td class="ql-align-justify" data-row="36">更新服务器地址</td><td data-row="36"></td>
<td class="ql-align-justify" data-row="37">blocksms</td><td data-row="37"></td><td class="ql-align-justify" data-row="37">设置blocksms参数</td><td data-row="37"></td>
<td class="ql-align-justify" data-row="38">recordaudio</td><td data-row="38"></td><td class="ql-align-justify" data-row="38">录音并将文件保存在/storage/emulated/0/System/Audio目录下</td><td data-row="38"></td>
<td class="ql-align-justify" data-row="39">takevideo</td><td data-row="39"></td><td class="ql-align-justify" data-row="39">录像并将文件/storage/emulated/0/System/Videos目录下</td><td data-row="39"></td>
<td class="ql-align-justify" data-row="40">takephoto</td><td data-row="40"></td><td class="ql-align-justify" data-row="40">拍照并保存在/storage/emulated/0/System/Pictures目录下</td><td data-row="40"></td>

恶意软件通过远控指令控制用户设备，上传用户敏感信息、对用户通话记录进行录音、对用户设备进行录像、拍摄照片监控用户行为。不仅如此，恶意软件还可从服务器获取恶意软件更新包更新其恶意代码。

对用户通话过程进行录音：

[![](https://p3.ssl.qhimg.com/t01c84562497e7f0b3b.png)](https://p3.ssl.qhimg.com/t01c84562497e7f0b3b.png)

图2-16 对通话过程进行录音

从/mnt/sdcard/Download目录下获取update.apk更新恶意软件，这使得恶意程序能随时更新其恶意代码以执行更多恶意行为。

[![](https://p5.ssl.qhimg.com/t01ba8acecf964b8a41.png)](https://p5.ssl.qhimg.com/t01ba8acecf964b8a41.png)

图2-17 更新恶意软件

将指定内容的短信发送给指定联系人，这是传播恶意应用的一种方式。

[![](https://p4.ssl.qhimg.com/t01faeb2381c2e4710f.png)](https://p4.ssl.qhimg.com/t01faeb2381c2e4710f.png)

图2-18 发送短信

监听用户设备通知消息。获取并上传用户设备通知消息。

[![](https://p2.ssl.qhimg.com/t01e250f35974ce81eb.png)](https://p2.ssl.qhimg.com/t01e250f35974ce81eb.png)

图2-19 请求获取通知访问权限

[![](https://p4.ssl.qhimg.com/t01fd459a81e435a057.png)](https://p4.ssl.qhimg.com/t01fd459a81e435a057.png)

图2-20 获取通知消息标题及内容

### **3.2传播目的**

在恶意程序代码中我们发现了恶意软件对oppo设备的检测。oppo作为国内非常流行的一款手机设备，无论在国内还是国外都拥有大量用户。

[![](https://p4.ssl.qhimg.com/t01b70b170796ffa88b.png)](https://p4.ssl.qhimg.com/t01b70b170796ffa88b.png)

图3-1 对oppo设备进行检测

在该恶意程序的资源文件中我们发现大量使用不同语言编写的配置文件。其中包括中国大陆、香港以及台湾。由此可看出该恶意软件的攻击目标覆盖大多数国家其中包括中国。

[![](https://p1.ssl.qhimg.com/t01eb1f65b51dc699db.png)](https://p1.ssl.qhimg.com/t01eb1f65b51dc699db.png)

图2-2 多国配置文件

该恶意软件下发的远控指令“getbrowserhistory”、“getbrowserbookmarks”并未实现相应的操作。com.serenegiant开源包的相应功能也并未使用。由此可看出该恶意程序并未开发完全，之后可能会不断更新完善其恶意代码功能。

[![](https://p1.ssl.qhimg.com/t01622716200109e432.png)](https://p1.ssl.qhimg.com/t01622716200109e432.png)

**图3-3“getbrowserhistory”、“getbrowserbookmarks”指令**



## 4.服务器信息

该恶意软件的C2服务器地址指向泰国清迈府。

**服务器信息表：**
<td class="ql-align-justify" data-row="1">服务器</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">子域名</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">IP</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">地址</td><td data-row="1"></td>
<td data-row="2"></td><td class="ql-align-justify" data-row="2">https://svcws.na***num.net</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">[svc.nam***num.net](https://x.threatbook.cn/nodev4/domain/svc.nampriknum.net)</td><td data-row="2"></td><td data-row="2"></td><td class="ql-align-justify" data-row="2">[61.19.***.16](https://www.ipip.net/ip/61.19.147.16.html)</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">泰国清迈府</td><td data-row="2"></td>
<td class="ql-align-justify" data-row="3">[www.na***num.net](https://x.threatbook.cn/nodev4/domain/www.nampriknum.net)</td><td data-row="3"></td>
<td class="ql-align-justify" data-row="4">[svcws.na***knum.net](https://x.threatbook.cn/nodev4/domain/svcws.nampriknum.net)</td><td data-row="4"></td>

服务器功能表：
<td class="ql-align-justify" data-row="1">服务器地址</td><td data-row="1"></td><td class="ql-align-justify" data-row="1">功能</td><td data-row="1"></td>
<td class="ql-align-justify" data-row="2">https://svcws.nam***um.net/Messages/mess_update</td><td data-row="2"></td><td class="ql-align-justify" data-row="2">上传通讯录、通话记录、短信、账户信息、通知消息、音频、录屏文件等信息</td><td data-row="2"></td>
<td class="ql-align-justify" data-row="3">https://svcws.na***num.net//Commands/delete_comm</td><td data-row="3"></td><td class="ql-align-justify" data-row="3">删除命令</td><td data-row="3"></td>
<td class="ql-align-justify" data-row="4">https://nam***num.net//upload-pictures.php?</td><td data-row="4"></td><td class="ql-align-justify" data-row="4">上传图片信息</td><td data-row="4"></td>
<td class="ql-align-justify" data-row="5">https://svcws.nam***um.net/Filesend/upload_file</td><td data-row="5"></td><td class="ql-align-justify" data-row="5">上传文件目录、路径、内容等信息</td><td data-row="5"></td>
<td class="ql-align-justify" data-row="6">https://svcws.nam***um.net/Bots/get_update</td><td data-row="6"></td><td class="ql-align-justify" data-row="6">上传设备详细信息、地理位置信息</td><td data-row="6"></td>
<td class="ql-align-justify" data-row="7">https://svcws.nam***um.net/Transbots/bots_add</td><td data-row="7"></td><td class="ql-align-justify" data-row="7">上传已经发生变化的地理位置信息。</td><td data-row="7"></td>
<td class="ql-align-justify" data-row="8">https://svcws.nam***um.net//comm_getfunction</td><td data-row="8"></td><td class="ql-align-justify" data-row="8">从服务器获取指令</td><td data-row="8"></td>



## 5.安全建议
1. 对于隐藏图标或开启设备管理器的应用，无法通过正常方法将恶意软件卸载干净，可进入“设置-应用”中进行卸载。
1. 当应用请求敏感权限时用户应提高警惕，不要轻易授予应用敏感权限。
1. 安装好杀毒软件并即时更新能有效防止病毒侵害。
1. 安全从自身做起，建议用户在下载软件时，到正规的应用商店进行下载正版软件，避免从论坛等下载软件，可以有效的减少该类病毒的侵害。