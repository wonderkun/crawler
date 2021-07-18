
# Anubis新的网络钓鱼活动


                                阅读量   
                                **759875**
                            
                        |
                        
                                                                                    



[![](./img/199543/t01b40e23b3d659c63d.jpg)](./img/199543/t01b40e23b3d659c63d.jpg)



导读：自从[2018](https://news.sophos.com/en-us/2018/08/14/anubis-is-back-are-you-prepared/)年[7](https://news.sophos.com/en-us/2018/08/14/anubis-is-back-are-you-prepared/)[月](https://news.sophos.com/en-us/2018/08/14/anubis-is-back-are-you-prepared/)首次撰写有关Anbuis的文章以来，Anubis的恶意下载程序的新版本会定期出现在GooglePlay市场和第三方应用程序商店中。成功安装和激活后，这些应用程序将在等待一段时间后下载并激活其恶意代码。这个简单但极其恶性的技巧可以使恶意软件躲避GooglePlay商店的防御机制。以下是2018至2019年Anubis伪装的恶意下载程序，其在金融服务、汽车服务、社交应用服务、游戏服务等各层面都有覆盖。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_m17e6dbe8.jpg)

图1-1Anubis恶意下载程序

Anubis功能异常强大，自身结合了钓鱼、远控、勒索木马等功能，其完全可以作为间谍软件。而且Anubis影响范围很大，活跃在93个不同的国家，针对全球378个银行及金融机构。通过伪造覆盖页面、键盘记录以及截屏等不同手段窃取目标应用程序的登录凭证。远程控制窃取用户隐私数据、加密用户文件并进行勒索。



## Anubis活动时间线：

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/ueditor/20200224/1582523611182144.png)



## 新Anubis活动

近期Anubis试图通过网络钓鱼电子邮件传播病毒，此特定电子邮件会要求用户下载发票，当用户打开电子邮件链接时将下载APK文件。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_m7c4f82e7.png)

图1-2 网络钓鱼电子邮件

恶意应用首次运行通过伪装AndroidSecurity（系统安全服务）来请求开启可访问性服务，获取监控用户操作以及窗口的权限。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_m81fc467.png)

图1-3 请求开启可访问性服务

同其它通过伪造的覆盖网页窃取用户登录凭证的木马不同，Anubis使用Android的可访问性服务执行键盘记录，通过键盘记录用户的登录信息。键盘记录器可以跟踪点击、聚焦、文本编辑三种不同的事件。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_1c31d399.png)

图1-4 监控的三种事件

该恶意软件还可以获取受感染用户屏幕的截图，这是获取受害者凭据的另一种方法。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_a3daf0.png)

图1-5 屏幕截图

该恶意软件使用了一项非常有趣的技术来确定应用程序是否在沙盒环境中运行，即通过传感器计算步数。如果受感染的设备属于真实的，则该人迟早会四处走动，从而增加了计步值。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_m5f32737.png)

图1-6 通过传感器计算步数



## Anubis远控及勒索行为

Anubis实时保持与服务器的连接，通过在上传信息的头部加入用户详细的设备信息来标识每个用户。

从服务器：http：//c**js .su//o1o/a3.php获取远控指令执行窃取数据、加密用户文件，截取屏幕、录音等恶意行为并监控用户设备正在运用的应用及进程，一旦发现包含目标应用，就会在原始应用程序上覆盖伪造的登录页面，以捕获用户的凭据。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_m5636e8e.png)

图2-1 与服务器交互



## 指令功能列表：



|startrat=

获取正在运行的应用及进程，一旦包含目标应用，Anubis就会在原始应用程序上覆盖伪造的登录页面，以捕获用户的凭据。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_m672669bd.png)

图2-2 覆盖伪造登录页面

使用对称加密算法加密用户设备外部存储目录、/mnt、/mount、/sdcard、/storage目录下所有文件。并以.AnubisCrypt拼接文件路径作为已加密文件标志。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_m1ef0a557.png)

图2-3 加密用户文件

加载勒索页面，通过加密用户文件来勒索比特币。

[![](./img/199543/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.96weixin.com/word/2020-02-24/202002241352014292885929_html_1a8dcc7e.png)

图2-4 加载勒索页面

除此之外Anubis会通过可访问性服务的模拟点击功能绕过GoogleProtect及授予应用敏感权限。通过隐藏图标、开启设备管理器、阻止用户进入应用详细页面防止自身被卸载。为了躲避检测，在Telegram和Twitter网页请求中对服务器地址进行编码，通过解析响应的HTML内容，获取C＆C服务器。该恶意软件功能齐全且未来可能会不断更新自身功能来达到更多需求，用户需提高警惕降低被感染的风险。



## 服务器功能表：



## 样本信息：

文件名：Fattura002873.apk

包名：wocwvy.czyxoxmbauu.slsa.rihynmfwilxiqz

MD5：c027ec0f9855529877bc0d57453c5e86



## 部分目标应用程序：

com.bankaustria.android.olb<br>
com.bmo.mobile<br>
com.cibc.android.mobi<br>
com.rbc.mobile.android<br>
com.scotiabank.mobile<br>
com.bankinter.launcher<br>
com.kutxabank.android<br>
com.tecnocom.cajalaboral<br>
com.dbs.hk .dbsmbanking<br>
com.FubonMobileClient<br>
com.hangseng.rbmobile<br>
com.MobileTreeApp<br>
com.mtel.androidbea
