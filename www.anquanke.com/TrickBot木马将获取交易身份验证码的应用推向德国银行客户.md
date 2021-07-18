
# TrickBot木马将获取交易身份验证码的应用推向德国银行客户


                                阅读量   
                                **532323**
                            
                        |
                        
                                                                                    



[![](./img/202123/t01f06275055a27572e.png)](./img/202123/t01f06275055a27572e.png)



TrickBot银行木马最早于2016年首次出现在德国并将德国银行作为攻击目标，主要通过WEB注入虚假的银行网页及重定向功能窃取用户银行卡账户信息以盗取用户钱财。

最近暗影实验室获取到一个应用名为Avast Sicherheitskontrolle的恶意程序。经研究发现该恶意程序可能由TrickBot银行木马推送给受感染的用户。国外研究员CERT-Bund的推文证实了这一点

2019年9月，国外研究员CERT-Bund的推文表示当用户的台式机上感染了TrickBot木马时，TrickBot会询问用户移动设备操作系统（OS）的类型和电话号码。然后提示用户安装假冒的安全应用程序进一步感染受害者的移动设备。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01610b4953fa5da81d.png)

由于银行木马的攻击者可以简单地使用所窃取的凭据来访问受害者的在线银行帐户并进行汇款。作为对策，金融机构引入了各种第二因素认证（2FA）方法。一种在德国流行的第二因素认证方法称为移TAN（mTAN）。它是通过向客户端的移动设备发送包含一次性密码的SMS消息来实现的。仅在客户在浏览器中将TAN输入到在线银行网站后，才能授权交易。

所以TrickBot木马分发移动端恶意程序的主要目的是为了获取并使用所需的“交易身份验证号码（TAN）”以登录其在线银行网站。



## 1.样本信息

**MD5：**5c749c9fce8c41bf6bcc9bd8a691621b

**包名：**d2.d2.d2

**应用名：**AvastSicherheitskontrolle

**图标：**

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01510a001e545d29da.png)



## 2.攻击流程

TrickBot银行木马通过注入伪造的银行页面窃取用户登录凭证，然后通过诱导用户安装的移动端恶意app获取交易身份验证号码，两者结合便可转走用户银行资金。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0162aa13e2bd0afbc9.png)

图1-1攻击流程图



## 3.技术分析

### **3.1自身防护**

为了增加研究人员的分析难度以及保证其配置信息的安全。该恶意程序使用混淆器来扰乱其函数，类和变量的名称。并将其配置首选项文件内容利用AES算法全部加密。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01affc82d9567eb151.png)

图2-1加密的配置文件

该应用程序利用Android的KeyStore系统存储加密密钥，从而提高从设备中提取密钥的难度以防止他人轻易获取密钥。相比起将密钥存储在用户的数据空间或者是硬编码在代码中都更加安全。本地生成密钥对并保存在KeyStore文件中，随后提取密钥对。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f7195b862581f0df.png)

图2-2生成、提取密钥对

使用提取到的公钥包裹用随机数生成的AES加密密钥。AES加密密钥用于加密配置文件内容。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ce5b5a3ee83af846.png)

图2-3使用密钥对包裹、解包AES密钥

解密首选项配置文件内容如下：

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017fa5ff8be85175db.png)

图2-4解密的配置文件

利用对称加密和对称加密算法双重加密算法加密配置文件内容增加了逆向人员分析代码的难度。

为了保证程序的某些操作能够得到有效执行而不需要经过用户同意，该程序一启动便会请求用户开启辅助功能服务。Android的辅助功能服务最初是由Google开发的，目的是服务于有残障的用户。应用程序可以通过该项服务监控用户在设备上的任何操作，以及模拟用户与设备的交互如点击按钮。近年来，一些恶意Android应用程序在各种攻击情形下滥用了该项可访问性服务。

恶意程序可利用该项服务执行以下操作：
1. 防止用户卸载应用程序
1. 授予应用敏感权限
1. 设置应用为默认短信应用程序
1. 监视当前正在运行的应用程序
1. 获取屏幕上文字（是窃取用户登录凭证的一种手段）
[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ab0281867dff762a.png)

图2-5请求可访问性服务

该恶意程序主要通过可访问性服务执行按钮点击功能，如同意设置该应用为默认的SMS应用程序、同意卸载该应用程序。该应用程序在达到目的后可启动卸载自身机制。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_418_/t019e34f673dd213d2c.png)

图2-6模拟点击按钮

### **3.2远程控制**

该应用程序通过不同的action触发广播来保证服务的正常运行，且该应用主要通过加密短信和C＆C两种方式与服务器建立联系。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016431ba849566741d.png)

图2-7注册广播

不同的action对应启动不同的服务，以执行不同的任务。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0103306ec49b1f26d0.png)

图2-8不同action触发不同服务

**3.2.1C＆C控制**

当程序接收到由网络连接触发的广播时，启动远程交互服务。通过未加密的HTTP请求定期连接到其指定的服务器，并下发任务。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_284_/t0113151590145a67d5.png)

图2-9服务器交互

当它与服务器建立通信时，将从受害者设备中收集的数据通过一个JSON对象发送，收集到的数据可用于生成机器人的唯一标识符或用于在暗网出售。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017232af5d82c3f260.png)

图2-10获取的设备信息

与服务器端交互，下发指令。服务器地址：http://mc***ft365.com/。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d4beb70e5188cac6.png)

图2-11C&amp;C远控结构

**指令列表：**
<td class="ql-align-justify">**指令**</td><td class="ql-align-justify">**功能**</td>
<td class="ql-align-justify">1</td><td class="ql-align-justify">更新C＆C服务器的地址</td>
<td class="ql-align-justify">2</td><td class="ql-align-justify">更新服务唤醒间隔</td>
<td class="ql-align-justify">3、7、10、14</td><td class="ql-align-justify">更改配置信息</td>
<td class="ql-align-justify">4</td><td class="ql-align-justify">使用可访问性服务卸载应用</td>
<td class="ql-align-justify">5</td><td class="ql-align-justify">锁定屏幕</td>
<td class="ql-align-justify">6</td><td class="ql-align-justify">使用可访问性服务成为默认的短信应用</td>
<td class="ql-align-justify">8</td><td class="ql-align-justify">发送指定内容的短信给指定的号码</td>
<td class="ql-align-justify">11</td><td class="ql-align-justify">加载网页</td>
<td class="ql-align-justify">12</td><td class="ql-align-justify">窃取设备上的图片</td>
<td class="ql-align-justify">13</td><td class="ql-align-justify">上传图片</td>

恶意程序为了保证有充足的时间来窃取到交易身份验证号码，通常在程序启动并请求用户授权后加载一些页面或锁定屏幕来延迟用户发现其不正常行为的时间。

该应用的锁定屏幕包括两个部分：
1. 从预定义URL加载的背景图片。该背景图像可能包含伪造的“软件正在更新”屏幕。
1. 锁定活动，这是显示在屏幕顶部的透明窗口，其中包含“正在加载”光标。该屏幕持续显示在屏幕上，并阻止用户使用导航按钮。
**3.2.2短信控制**

当程序接收到由android.provider.Telephony.SMS_RECEIVED动作促发的广播时，应用程序通过短信与服务端建立连接。

为了窃取SMS消息中的交易身份验证号码，应用程序会将自身更改为短信默认程序。这样应用可以随意操作短信、删除短信以保证短信内容只有攻击者才能看见。获取并解析用户设备接收的短信内容。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011dd0bfd0831308d4.png)

图2-12获取用户设备接收的短信信息

在下图中，我们可以看到一个发送到服务器的数据包，其中包含收集的设备信息以及用户的SMS数据。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c7a94d5c9e6ada0f.png)

图2-13上传用户设备信息以及短信信息

通过短信与服务器建立联系，解析短信指令执行相应任务。攻击者会在自身发送的短信内容中用”Freischaltcode”字符串作为标记。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_430_/t01db0dad8456ada433.png)

图2-14短信远控结构

服务端发送的短信通过RSA非对称加密算法加密，解密的私钥硬编码在代码中。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0124f67f73bd9e6aec.png)

图2-15 解密的私钥硬编码在代码中

**短信指令列表：**
<td class="ql-align-justify">**指令**</td><td class="ql-align-justify">**功能**</td>
<td class="ql-align-justify">http://</td><td class="ql-align-justify">更新服务器地址</td>
<td class="ql-align-justify">sms://</td><td class="ql-align-justify">将接收到的SMS发回给发件人</td>
<td class="ql-align-justify">2</td><td class="ql-align-justify">更改服务启动间隔时间</td>
<td class="ql-align-justify">3</td><td class="ql-align-justify">将短信内容插入本地数据库</td>
<td class="ql-align-justify">4</td><td class="ql-align-justify">更改配置信息</td>

程序内部会注册默认短信程序监听器，当该恶意软件成功成为默认的SMS应用程序，它将以俄语发送“ 应用程序已被替换 ”的SMS消息到服务器。如果原始SMS应用程序已还原，它将发送“ 该应用程序返回其原始位置” 的SMS消息到服务器。且该sms消息电话号码字段被标记标记为“内部”

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_123_/t01d5c681d440ae1c0c.png)

图2-16 发送俄语sms消息至C&amp;C

发送到C&amp;C的sms消息。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c30b2c25f7a49e41.png)

图2-17 发送sms信息至服务器

### **3.3恶意程序变体**

在应对德国的银行停止使用基于SMS的身份验证，转而使用专用于2FA方案的pushTAN应用程序（使用针对用户的推送通知，其中包含交易明细和交易身份验证号码）情况时。由于Android的应用程序沙箱阻止一个应用程序访问其他应用程序的数据。专为德国银行量身定制的较新版本恶意程序使用了以下两种方式获取交易身份验证号码（TAN）。

使用Android MediaRecorder类捕获屏幕视频或截屏。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0167a80184fdabdb3d.png)

图3-1录屏

使用可访问性服务遍历每个可访问性节点所包含的文本数据，其中包含屏幕上所有对象的文本数据如文本框里的文字。

[![](./img/202123/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013afc19490ad7dd5a.png)

图3-2遍历节点



## 4.总结

通过PC端恶意程序分发移动端恶意程序的情况并不是第一次出现。为了获取利益攻击者会不断更新其攻击手段。用户应提高应对恶意程序的警惕性，当一个应用没有任何理由请求开启可访问性服务时就应该立即阻断卸载该应用，以免设备被恶意程序感染。
