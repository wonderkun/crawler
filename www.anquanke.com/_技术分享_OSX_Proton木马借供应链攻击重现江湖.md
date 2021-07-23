> 原文链接: https://www.anquanke.com//post/id/87063 


# 【技术分享】OSX/Proton木马借供应链攻击重现江湖


                                阅读量   
                                **86210**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：welivesecurity.com
                                <br>原文地址：[https://www.welivesecurity.com/2017/10/20/osx-proton-supply-chain-attack-elmedia/](https://www.welivesecurity.com/2017/10/20/osx-proton-supply-chain-attack-elmedia/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01172b27e4a94fb01a.png)](https://p4.ssl.qhimg.com/t01172b27e4a94fb01a.png)



译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

几个小时之前，ESET研究人员注意到，El媒体播放器软件的制造商Eltima竟然在自家的官方网站上发布了一个含有OSX/Proton恶意软件的版本。ESET对恶意软件进行核实之后，立即联系了Eltima，他们的反应非常迅速，并在整个事件中一直与我们保持良好的沟通。

**<br>**

**时间线**

2017-10-19：木马程序被核实

2017-10-19美国东部时间上午10:35：通过电子邮件通知Eltima

2017-10-19美国东部时间上午2:25：Eltima确认了这一问题，并启动补救工作

2017-10-19美国东部时间下午3:10：Eltima确认其基础设施已经清理完毕，并重新提供正常的应用程序 

**<br>**

**我被黑了吗？**

根据ESET的建议，最近下载过Elmedia Player软件的所有用户，可以通过检查自己的计算机上面是否存在下面的任意文件或目录，来确认是否受到本次木马事件的影响：



```
/tmp/Updater.app/
/Library/LaunchAgents/com.Eltima.UpdaterAgent.plist
/Library/.rand/
/Library/.rand/updateragent.app/
```

如果机器中发现了上述任何一个文件或目录的话，则表明被植入特洛伊木马的Elmedia播放器已被执行，并且系统很可能已经感染了OSX/Proton。

如果您是在10月19日美国东部时间下午3点15分之前下载并运行过该软件的话，那么您的系统很可能已经被感染了。

据我们所知，只有从Eltima网站下载的相应版本中才含有特洛伊木马程序。但是，内置的自动更新机制似乎没有受到此次事件的影响。 

**<br>**

**恶意软件的payload到底对受感染的系统有何影响？**

OSX/Proton是一款具有强大的数据窃取功能的后门软件。它能够常驻系统，并窃取以下内容：

1.    操作系统详细信息：硬件序列号（IOPlatformSerialNumber）、当前用户的全称、主机名、系统完整性保护状态（csrutil status）、网关信息（route -n get default | awk ‘/gateway/ `{` print $2 `}`’）和当前时间和时区

2.    Chrome、Safari、Opera和Firefox等浏览器的相关信息：历史记录、Cookie、书签、登录数据等。

3.    加密数字货币钱包： 

        Electrum钱包: ~/.electrum/wallets

        Bitcoin Core钱包: ~/Library/Application Support/Bitcoin/wallet.dat

        Armory钱包: ~/Library/Application Support/Armory

4.    SSH保密数据（所有.ssh内容）

5.    macOS的keychain数据，这是通过改进版的chainbreaker窃取的

6.    Tunnelblick VPN配置（~/Library/Application Support/Tunnelblick/Configurations）

7.    GnuPG数据（~/.gnupg）

8.    1Password数据（~/Library/Application Support/1Password 4 and ~/Library/Application Support/1Password 3.9）

9.    所有已安装应用程序的清单 

**<br>**

**如何清理我的系统？**

像这种管理员帐户被黑的情况，重装系统是摆脱恶意软件的唯一可靠方法。此外，由于上一节中介绍的数据已经被窃，所以受害者还应做好相应的补救措施。

Mac平台上的供应链攻击

去年，Mac平台上的Bittorrent客户端程序Transmission被滥用，曾经两度传播恶意软件，第一次传播的是勒索软件OSX/KeRanger，第二次传播的是窃取密码的木马软件OSX/Keydnap。今年，视频转码程序Handbrake又被发现捆绑了OSX/Proton。

今天，ESET发现了另一款流行的Mac软件也被用于传播OSX/Proton，它就是Elmedia的媒体播放器——截止今年夏天，该软件的用户已经超过了10万：

[![](https://p2.ssl.qhimg.com/t0116dffda98146b79a.png)](https://p2.ssl.qhimg.com/t0116dffda98146b79a.png)

**<br>**

**技术分析**

OSX/Proton是一款在地下论坛中以套件形式出售的RAT。在今年年初，Sixgill曾经对其进行过简单的介绍，后来Thomas Reed、Amit Serper和Patrick Wardle分别对其进行了更加深入的分析。

在本次的Eltima特洛伊木马软件案例中，攻击者为Elmedia Player和Proton构建了一个带有签名的包装器。实际上，根据我们的观察，这个包装器好像使用了实时的重新打包和签名技术，并且使用的都是同一个合法的Apple Developer ID。下面按照历史顺序给出了已知的样本。据Eltima和ESET称，他们正在与Apple合作，废除这个为恶意应用程序签名的Developer ID。（苹果公司已经吊销了这个证书。）

（下面的时间都是按照EDT时区计时的）

正常的应用程序:

[![](https://p4.ssl.qhimg.com/t01536f6c4181c3307d.png)](https://p4.ssl.qhimg.com/t01536f6c4181c3307d.png)

被植入木马的应用程序:

[![](https://p5.ssl.qhimg.com/t015400d9c51933719b.png)](https://p5.ssl.qhimg.com/t015400d9c51933719b.png)

首先，包装器启动了存放在该应用程序的Resources文件夹中的真正的Elmedia Player应用程序：

[![](https://p0.ssl.qhimg.com/t0107ec802c0c225e0b.png)](https://p0.ssl.qhimg.com/t0107ec802c0c225e0b.png)

最后，提取并启动了OSX/Proton：

[![](https://p5.ssl.qhimg.com/t0180d3f3fd35feac2a.png)](https://p5.ssl.qhimg.com/t0180d3f3fd35feac2a.png)

OSX/Proton展示了一个伪造的Authorization窗口来获得root权限：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016e7bf6812e28fa4c.png)

**持久性**

在受害者输入密码后，OSX/Proton会为所有用户添加一个LaunchAgent，从而获得持久性。它会在系统中创建下列文件：



```
/Library/LaunchAgents/com.Eltima.UpdaterAgent.plist
/Library/.rand/updateragent.app
```



```
$ plutil -p /Library/LaunchAgents/com.Eltima.UpdaterAgent.plist
 
`{`
 
  "ProgramArguments" =&gt; [
 
    0 =&gt; "/Library/.rand/updateragent.app/Contents/MacOS/updateragent"
 
  ]
 
  "KeepAlive" =&gt; 1
 
  "RunAtLoad" =&gt; 1
 
  "Label" =&gt; "com.Eltima.UpdaterAgent"
 
`}`
```



**后门命令**

前面说过，OSX/Proton是一个具有强大信息窃取功能的后门程序。根据我们的观察，其后门组件支持以下命令：

**archive     使用zip归档文件**

**copy          在本地复制文件**

**create      在本地创建目录或文件**

**delete       在本地删除文件**

**download          从URL下载文件**

**file_search       搜索文件（执行find / -iname "%@" 2&gt; /dev/null）**

**force_update   带有数字签名验证的自我更新**

**phonehome**

**remote_execute      执行.zip文件或给定的shell命令中的二进制文件**

**tunnel       使用22或5900端口创建SSH隧道**

**upload      将文件上传到C＆C服务器** 



**C＆C服务器**

Proton使用的C＆C域名模仿自合法的Eltima域名，这种做法跟Handbrake的差不多：

[![](https://p5.ssl.qhimg.com/t01bf6c73cd870df63f.png)](https://p5.ssl.qhimg.com/t01bf6c73cd870df63f.png)



**IOCs**

**URL**

在受到感染的程序被发现时，分发木马程序的URL为： 

hxxps://mac[.]eltima[.]com/download/elmediaplayer.dmg

hxxp://www.elmedia-video-player.com/download/elmediaplayer.dmg

**C＆C服务器**

eltima[.]in / 5.196.42.123 (domain registered 2017-10-15)

**哈希值**

**[![](https://p5.ssl.qhimg.com/t0129c92b66b9fe8aa1.png)](https://p5.ssl.qhimg.com/t0129c92b66b9fe8aa1.png)**
