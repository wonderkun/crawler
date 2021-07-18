
# Operation Poisoned News：针对香港用户的水坑攻击


                                阅读量   
                                **632702**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者trendmicro，文章来源：blog.trendmicro.com
                                <br>原文地址：[https://blog.trendmicro.com/trendlabs-security-intelligence/operation-poisoned-news-hong-kong-users-targeted-with-mobile-malware-via-local-news-links/](https://blog.trendmicro.com/trendlabs-security-intelligence/operation-poisoned-news-hong-kong-users-targeted-with-mobile-malware-via-local-news-links/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/202044/t01c43c8b3d8734a293.jpg)](./img/202044/t01c43c8b3d8734a293.jpg)



## 0x00 前言

研究人员最近发现了针对香港iOS用户的水坑攻击，攻击者在多个论坛上发布了恶意链接，这些链接指向的是各种新闻报道。当用户被诱导访问这些新闻站点时，攻击者还使用了隐蔽的`iframe`来加载并执行恶意代码，这些恶意代码中包含针对iOS 12.1及12.2系统的漏洞利用代码。如果用户使用存在漏洞的设备点击这些链接，就会下载一种全新的iOS恶意软件变种，我们将该变种标记为`lightSpy`（对应检测标识为`IOS_LightSpy.A`）。



## 0x01 恶意软件概览

这款恶意软件变种为模块化后门，允许攻击者远程执行shell命令、篡改被感染设备上的文件。攻击者可以监控目标用户设备，完全控制该设备。该后门包含多个模块，可以从被感染的设备中窃取数据，包括如下隐私数据：
- 连接过的Wi-Fi历史记录
- 联系人
- GPS位置
- 硬件信息
- iOS keychain
- 电话记录
- Safari及Chrome浏览器历史
- SMS消息
攻击者也会窃取目标设备上与用户网络环境有关的信息，包括：
- 可用的Wi-Fi网络
- 本地网络IP地址
攻击者也会针对某些即时通讯类应用，窃取相关信息，这些应用包括：
- Telegram
- QQ
- WeChat
经过研究后，我们还找到了针对Android设备的相似攻击团伙，该团伙曾在2019年活动过。指向恶意.APK文件的各种链接曾出现在与香港有关的Telegram频道中，攻击者声称这些链接为各种合法应用，但实际上指向的是恶意app，可以窃取设备信息、通信录以及SMS消息。我们将这个Android恶意软件家族称之为`dmsSpy`（并将`dmsSpy`的各种变种标记为`AndroidOS_dmsSpy.A.`）。

根据恶意软件的架构及功能，我们猜测此次攻击并没有针对特定用户，目标应该是尽可能多地感染移动设备，部署监控后门。根据恶意软件的传播方式，我们将此次攻击活动命名为“Operation Poisoned News”。

本文介绍了`lightSpy`及`dmsSpy`的整体功能及传播方式，大家可以访问[此处](https://documents.trendmicro.com/assets/Tech-Brief-Operation-Poisoned-News-Hong-Kong-Users-Targeted-with-Mobile-Malware-via-Local-News-Links.pdf)查看更多技术细节（比如IoC等）。



## 0x02 传播方式

2月19日，我们发现了针对iOS用户的水坑攻击 ，其中所使用的URL指向的是攻击者创建的恶意站点，该站点中包含指向不同站点的3个`iframe`，其中只有1个`iframe`可见，并且指向的是合法的新闻网站，这样用户就会误认为自己访问的是正常站点。另外两个不可见的`iframe`中，有一个用于网站分析，另一个指向的是托管iOS漏洞利用主脚本的站点。这3个`iframe`的代码片段如下：

[![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bf212e14c1c80c77.png)

图1. 恶意站点中包含3个`iframe`的HTML代码

攻击者将指向恶意站点的链接发布在香港居民常用的4个不同的论坛上。这些论坛为用户提供了移动端app，方便用户在移动设备上访问。攻击者在论坛的一般讨论板块中发表了诱导性新闻，使用了特定新闻报道的标题、相关图片，同时搭配了指向新闻站点的（虚假）链接。

攻击者使用新注册的账户在论坛上发表帖子，因此我们认为这些操作并不是通过正常账户来完成。攻击者使用的诱骗主题包括两性相关标题、点击欺诈式标题或者与COVID-19病毒有关的新闻。我们认为这些主题并非针对特定用户，而是以访问该站点的所有用户为目标。

[![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0131f25d92e8607a2e.png)

图2. 攻击者使用的新闻标题

[![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016cfcfddaf54b9bc0.png)

图3. 包含恶意站点链接的论坛帖子

除了使用上述技术外，我们还发现了第二类水坑站点。在这类攻击场景中，攻击者复制了合法网站，并注入了恶意`iframe`。根据我们的感知数据，攻击者从1月2日开始就在香港传播这类水坑攻击链接，然而我们并不知道这类链接的传播媒介。

[![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011b63f25896f1495b.png)

图4. 攻击者复制的新闻页面，其中包含恶意漏洞利用代码的`iframe`

这些攻击活动一直持续到3月20日，最近一次的帖子内容与香港的抗议活动日程表有关，然而帖子中的链接实际上会指向前面提到过的感染链路。

[![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018abd95ba31c2f212.png)

图5. 仿冒日程表的恶意网站链接



## 0x03 感染链

攻击者在此次活动中使用的漏洞会影响iOS 12.1及12.2系统，涉及到多款iPhone型号，从iPhone 6S到iPhone X，如下代码片段所示：

[![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bc7c8569cafa7971.png)

图6. 检查目标设备的代码

完整的漏洞利用链中包括被Apple悄悄修复的一个Safari漏洞（影响最新的多个iOS版本）以及一个自定义内核漏洞利用代码。当Safari浏览器渲染漏洞利用代码时，执行流会被导向到某个bug（Apple在新版iOS中修复了这个bug），从而会利用已知的一个内核bug，最终帮攻击者拿到root权限。这个内核bug对应的漏洞编号为[CVE-2019-8605](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-8605)，而被悄悄修复的Safari漏洞并没有对应的CVE编号，虽然[其他研究人员](https://twitter.com/qwertyoruiopz/status/1147308549330165760)曾提到过与该问题有关的信息。

当成功拿下目标设备后，攻击者就会安装未公开且比较复杂的一款间谍软件，用来维持对目标设备的控制权限并窃取信息。这款间谍软件使用了模块化设计架构，包含多个功能，比如：

1、模块升级功能；

2、针对每个模块的远程命令分派功能；

3、完整功能的shell命令模块。

这款间谍软件的大多数模块专为窃取数据设计，比如，恶意软件中包含针对Telegram及WeChat的信息窃取模块。恶意软件所使用的感染链及各种模块如下图所示：

[![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a1b458566febaffc.jpg)

图7. `lightSpy`感染链及模块

我们之所以将这款恶意软件命名为`lightSpy`，是因为模块管理器的名称为`light`。我们还发现恶意软件的`launchctl`模块使用了一个配置文件，该文件经过解码后包含指向`/androidmm/light`位置的一个URL，这表明恶意软件也存在适配Android系统的版本。



## 0x04 lightSpy概览

接下来我们简要分析一下`lightSpy`的功能及相关payload（由于篇幅所限，这里我们没有给出详细信息），我们在另一篇[文章](https://documents.trendmicro.com/assets/Tech-Brief-Operation-Poisoned-News-Hong-Kong-Users-Targeted-with-Mobile-Malware-via-Local-News-Links.pdf)中提供了更多细节。

当触发内核漏洞时，`payload.dylib`会下载多个模块，如下代码所示：

[![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017ec601cbf10ab4be.png)

图8. 下载的模块

以上模块中有些模块与启动及加载有关。比如，`launchctl`这款工具用来加载或卸载守护程序/agent，并且该工具会使用`ircbin.plist`作为参数。守护程序会运行`irc_loader`，该程序只是主恶意模块（`light`）的一个加载器（从名称中我们就可以推测这一点），但其中硬编码了C&amp;C服务器的地址。

`light`模块为恶意软件的主控制模块，可以加载及更新其他模块。剩下的模块用来窃取不同类型的数据，如下所示：

1、`dylib`：获取并上传基本信息，包括iPhone硬件信息、联系人、文本信息及通话记录。

2、`ShellCommandaaa`：在被感染设备上执行shell命令，获取的结果经过序列化处理后上传到特定服务器。

3、`KeyChain`：窃取并上传Apple KeyChain中包含的信息。

4、`Screenaaa`：使用被感染设备扫描并ping同一子网中的设备，ping结果上传到攻击者的服务器。

5、`SoftInfoaaa`：获取设备上的app及进程信息。

6、`FileManage`：在设备上执行文件系统相关操作。

7、`WifiList`：获取已保存的Wi-Fi信息（已保存的网络，Wi-Fi连接历史等）。

8、`browser`：从Chrome及Safari中获取浏览器历史记录。

9、`Locationaaa`：获取用户地理位置。

10、`ios_wechat`：获取与WeChat有关的信息，包括：账户信息、联系人、群组、消息及文件。

11、`ios_qq`：针对QQ应用，功能与`ios_wechat`类似。

12、`ios_telegram`：针对Telegram应用，功能与前两个模块类似。

这些模块组合在一起，可以帮助攻击者完全拿下目标设备控制权，窃取用户的大部分隐私信息。此次攻击活动针对的是香港应用市场中的多款常用聊天app，从中我们可知这也是攻击者的目标。



## 0x05 dmsSpy概览

前面提到过，`lightSpy`有个对应Android版本：`dmsSpy`。在2019年，攻击者在Telegram公共频道中以不同app形式来传播这些变种。虽然在此次研究过程中，这些链接均已失效，但我们还是拿到了其中一个样本。

我们拿到的样本为日历类app，其中包含香港区域的活动日程表。该应用中包含我们在恶意软件中经常看到的功能，比如请求敏感权限、将敏感信息传递给C&amp;C服务器等。这些信息中包含貌似无害的信息（如设备型号），但也包含其他敏感信息，如联系人、短信、用户地理位置及存储文件的文件名。`dmsSpy`同样会注册一个Receiver，用来读取新收到的SMS、运行USSD代码。

我们之所以能了解关于`dmsSpy`的更多信息，是因为开发者在应用的web框架中遗留了debug模式，因此我们可以窥探服务器所使用的API。根据这些API，我们能了解到尚未发现的其他功能，包括屏幕截图、安装APK文件等。

[![](./img/202044/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cb35534f8843458a.png)

图9. Web框架中泄露的API列表

我们认为这些攻击活动有所关联。`dmsSpy`的下载及命令控制服务器所使用的域名（`hkrevolution[.]club`）与“Poisoned News”在水坑攻击活动中iOS组件所使用的域名相同（但涉及到不同的子域名）。因此，我们认为这个Android攻击活动背后操作者与Poisoned News有关。



## 0x06 厂商回复

我们联系了本文提到的各种厂商，Tencent的回复如下：

> Trend Micro提供的这份报告表明，及时更新主机及移动设备操作系统非常重要。该报告中提到的漏洞影响iOS 12.1及12.2的Safari浏览器，Apple在新版iOS中修复了这些漏洞。
在我们的WeChat和QQ用户中，只有少部分用户仍在使用包含漏洞的iOS系统。我们已经提醒这些用户尽快升级到最新版iOS。
Tencent非常重视数据安全，会继续努力，确保我们的产品和服务构建在能够确保用户数据安全的强大平台之上。

我们通过Trend Micro的Zero Day Initiative（ZDI）平台通知了Apple。我们也联系了Telegram，但在本文发表时，我们尚未收到任何回复。
