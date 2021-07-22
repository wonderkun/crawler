> 原文链接: https://www.anquanke.com//post/id/193995 


# “Adobe Flash Player”木马惊现新变种


                                阅读量   
                                **1186755**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01d33a0ce0cd839b36.jpg)](https://p0.ssl.qhimg.com/t01d33a0ce0cd839b36.jpg)



最近暗影安全实验室在日常监测中发现了一款新的木马病毒Ginp，虽然他和前两周发布的反间谍之旅004报告中描述的“Flash Player”木马病毒名称很相似都带有“Flash Player”,但是他们却属于不同病毒家族。

该恶意软件的最初版本可以追溯到2019年6月初，它伪装成“Google Play Verificator”应用程序。当时，Ginp是一个简单的短信窃取器，其目的只是将用户手机接收和发出的短信副本发送到C2服务器。

在2019年8月，一个新版本发布了，增加了银行木马特有的功能。这个恶意软件被伪装成假冒的“Adobe Flash Player”应用程序，恶意软件代码增强了反混淆能力。Ginp较前两周发布的“Flash Player”木马病毒相比除了具有木马病毒惯用的远控获取用户联系人列表、短信列表等隐私信息的特性外，还通过注册易访问性服务监控用户设备，自动授权应用敏感权限，加载网页覆盖特定应用程序页面，目的是窃取登录凭证信息。



## 1. 样本信息

MD5：1EA4002F712DE0D9685D3618BA2D0A13

程序名称：Adobe Flash Player

程序包名：solution.rail.forward

安装图标：

[![](https://p0.ssl.qhimg.com/t01b3282a0c9670100d.png)](https://p0.ssl.qhimg.com/t01b3282a0c9670100d.png)



## 2. 详细分析

恶意软件第一次在设备上启动时，它会隐藏图标并要求受害者提供无障碍服务特权。

[![](https://p4.ssl.qhimg.com/t01778352bbfb35cfc3.png)](https://p4.ssl.qhimg.com/t01778352bbfb35cfc3.png)

一旦用户授予请求的可访问性服务特权，Ginp首先自动授予自己额外的权限，以便能够执行某些敏感的高权限操作，而不需要受害者的任何进一步操作。完成后，恶意程序就可以正常工作了，可以接收命令并执行覆盖攻击。

检测配置信息，并将信息发送至服务器。以方便控制端根据配置信息来判断可以在受害者机器上执行哪些操作。

[![](https://p0.ssl.qhimg.com/t013eaf249c0117063c.png)](https://p0.ssl.qhimg.com/t013eaf249c0117063c.png)

图 2-1 获取应用配置信息

监控服务器响应状态，获取C2服务器下发的指令，窃取用户联系人列表、短信列表等信息。发送指定短信内容到指定联系人，目的是传播恶意软件。

[![](https://p2.ssl.qhimg.com/t016a99ab07db526163.png)](https://p2.ssl.qhimg.com/t016a99ab07db526163.png)

图2-2 获取C2服务器指令

指令列表：

表2-1 指令列表
<td valign="top" width="242">指令</td><td valign="top" width="327">功能</td>
<td valign="top" width="242">SENT_SMS</td><td valign="top" width="327">从C2获取指定短信内容发送至指定号码</td>
<td valign="top" width="242">NEW_URL</td><td valign="top" width="327">更新C2 URL</td>
<td valign="top" width="242">KILL</td><td valign="top" width="327">停止服务</td>
<td valign="top" width="242">PING_DELAY</td><td valign="top" width="327">更新ping请求之间的间隔时间</td>
<td valign="top" width="242">ALL_SMS</td><td valign="top" width="327">获取所有短信信息</td>
<td valign="top" width="242">DISABLE_ACCESSIBILITY</td><td valign="top" width="327">停止阻止用户禁用可访问性服务</td>
<td valign="top" width="242">ENABLE_ACCESSIBILITY</td><td valign="top" width="327">防止用户禁用可访问性服务</td>
<td valign="top" width="242">ENABLE_HIDDEN_SMS</td><td valign="top" width="327">设置恶意软件为默认短信应用程序</td>
<td valign="top" width="242">DISABLE_HIDDEN_SMS</td><td valign="top" width="327">移除恶意软件作为默认短信应用程序</td>
<td valign="top" width="242">ENABLE_CC_GRABBER</td><td valign="top" width="327">启用谷歌播放覆盖</td>
<td valign="top" width="242">DISABLE_CC_GRABBER</td><td valign="top" width="327">禁止谷歌播放覆盖</td>
<td valign="top" width="242">ENABLE_EXTENDED_INJECT</td><td valign="top" width="327">启动覆盖攻击</td>
<td valign="top" width="242">DISABLE_EXTENDED_INJECT</td><td valign="top" width="327">禁止覆盖攻击</td>
<td valign="top" width="242">START_DEBUG</td><td valign="top" width="327">启动调试</td>
<td valign="top" width="242">STOP_DEBUG</td><td valign="top" width="327">停止调试</td>
<td valign="top" width="242">START_PERMISSIONS</td><td valign="top" width="327">启动对短信权限的请求</td>
<td valign="top" width="242">GET_CONTACTS</td><td valign="top" width="327">获取所有联系人信息</td>
<td valign="top" width="242">SEND_BULK_SMS</td><td valign="top" width="327">发送指定短信到多个号码</td>
<td valign="top" width="242">UPDATE_APK</td><td valign="top" width="327">下载安装应用</td>

通过可访问性服务AccessibilityService，监控用户设备操作事件。

[![](https://p4.ssl.qhimg.com/t019f4a9325297afc57.png)](https://p4.ssl.qhimg.com/t019f4a9325297afc57.png)

图2-3 监控用户设备

执行以下操作 :

（1）更新应用列表，自动下载安装软件：从服务器获取需要下载的应用链接、下载应用并打开安装界面，当监测到系统弹出安装界面时，遍历节点，通过perforAcmtion执行点击同意授权。

[![](https://p4.ssl.qhimg.com/dm/1024_478_/t0193896d25791691d3.png)](https://p4.ssl.qhimg.com/dm/1024_478_/t0193896d25791691d3.png)

图2-4 请求安装界面

（2）自动授予高敏感权限：申请接收发送读取短信权限，当监测到系统弹框请求权限时，遍历节点，通过perforAcmtion执行点击同意授权。

[![](https://p3.ssl.qhimg.com/t01b0c0b06ea22a05b6.png)](https://p3.ssl.qhimg.com/t01b0c0b06ea22a05b6.png)

图2-5 自动授权、安装软件

（3）自我保护，防止被删除：当监测到用户打开的界面包含“force”强制停止、“app info”应用列表时，程序退出到HOME界面，所以用户无法通过查看应用列表卸载该软件。

[![](https://p1.ssl.qhimg.com/t01b1c4453c538284aa.png)](https://p1.ssl.qhimg.com/t01b1c4453c538284aa.png)

图2-6 打开HOME界面

（4）覆盖攻击：监测用户打开的应用，从服务器获取网页覆盖目标应用，该服务器模拟真实的应用程序页面进行覆盖，以窃取用户登录凭证。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f1ac78fee424adbf.png)

图2-7 覆盖目标应用

目标软件：
- Google Play
- Facebook
- Instagram
- Whatsapp
- Chrome
- Skype
- Twitter
- Snapchat
下面的截图显示了在覆盖攻击时收集了什么类型的信息:

[![](https://p3.ssl.qhimg.com/t015f2609f7b5eb159b.png)](https://p3.ssl.qhimg.com/t015f2609f7b5eb159b.png)

图2-8 覆盖攻击网页

设置恶意软件为默认短信应用程序。监控用户短信收发情况。

[![](https://p2.ssl.qhimg.com/t01c9cdbae9d061ecbc.png)](https://p2.ssl.qhimg.com/t01c9cdbae9d061ecbc.png)

图2-9 监听用户短信



## 3. 服务器地址

表3-1 服务器地址
<td valign="top" width="284">服务器地址</td><td valign="top" width="284">功能</td>
<td valign="top" width="284">[http://64.**.51.107/api2/ping.php](http://64.44.51.107/api2/ping.php)</td><td valign="top" width="284">主控</td>
<td valign="top" width="284">[http://64.**.51.107/api2](http://64.44.51.107/api2)</td><td valign="top" width="284">加载覆盖网页</td>
<td valign="top" width="284">[http://64.**.51.107/api2/sms.php](http://64.44.51.107/api2/sms.php)</td><td valign="top" width="284">上传短信信息</td>



## 4. 同源样本

监测中发现的服务器地址相同的样本。虽然该木马病毒暂时的目标是一些社交软件，但是它可能正在更新另一个新版本的恶意软件将目标转向于银行，用于窃取用户更加敏感的信息，如：银行卡信息、信用卡信息，以获取利益。

表4-1 同源样本
<td valign="top" width="92">应用名称</td><td valign="top" width="133">包名</td><td valign="top" width="343">MD5</td>
<td valign="top" width="92">Google Play Verificator</td><td valign="top" width="133">sing.guide.false</td><td valign="top" width="343">0ee075219a2dfde018f17561467272633821d19420c08cba14322cc3b93bb5d5</td>
<td valign="top" width="92">Google Play Verificator</td><td valign="top" width="133">park.rather.dance</td><td valign="top" width="343">087a3beea46f3d45649b7506073ef51c784036629ca78601a4593759b253d1b7</td>
<td valign="top" width="92">Adobe Flash Player</td><td valign="top" width="133">ethics.unknown.during</td><td valign="top" width="343">5ac6901b232c629bc246227b783867a0122f62f9e087ceb86d83d991e92dba2f</td>
<td valign="top" width="92">Adobe Flash Player</td><td valign="top" width="133">com.pubhny.hekzhgjty</td><td valign="top" width="343">14a1b1dce69b742f7e258805594f07e0c5148b6963c12a8429d6e15ace3a503c</td>
<td valign="top" width="92">Adobe Flash Player</td><td valign="top" width="133">sentence.fancy.humble</td><td valign="top" width="343">78557094dbabecdc17fb0edb4e3a94bae184e97b1b92801e4f8eb0f0626d6212</td>



## 5. 安全建议

Ø 由于恶意软件对自身进行了保护，用户通过正常方式无法卸载。可采取以下方式卸载。

（1）将手机连接电脑，在控制端输入命令：adb shell pm uninstall 包名。

（2）进入手机/data/data目录或/data/app目录，卸载文件名带有该应用包名的文件夹，应用将无法运用。

（3）安装好杀毒软件，能有效识别已知病毒。

Ø 很多攻击者会通过短信传播恶意软件，所以用户不要轻易点击带有链接的短信。

Ø 坚持去正规应用商店或官网下载软件，谨慎从论坛或其它不正规的网站下载软件。

Ø 关注”暗影安全实验室”公众号，获取最新实时移动安全状态，避免给您造成损失和危害。

更多精彩文章请关注我们的微信公众号

[![](https://p3.pstatp.com/large/pgc-image/b8c96a6f1590430bbdc6c2bd7bd62782)](https://p3.pstatp.com/large/pgc-image/b8c96a6f1590430bbdc6c2bd7bd62782)
