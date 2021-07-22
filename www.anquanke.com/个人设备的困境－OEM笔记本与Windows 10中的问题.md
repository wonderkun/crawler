> 原文链接: https://www.anquanke.com//post/id/83657 


# 个人设备的困境－OEM笔记本与Windows 10中的问题


                                阅读量   
                                **73957**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://duo.com/assets/pdf/bring-your-own-dilemma.pdf](https://duo.com/assets/pdf/bring-your-own-dilemma.pdf)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p3.ssl.qhimg.com/t0168416c9c5fefa421.jpg)](https://p3.ssl.qhimg.com/t0168416c9c5fefa421.jpg)

**文章概述**

Bring Your Own Device(BYOD)是信息行业近年来火热的话题，作为一种新型的IT设备模式，BYOD可以更好的满足员工对于自由、个性化办公的需求，对企业而言，可有效降低移动信息化的投入成本。然而BYOD概念的出现让许多IT经理感到不安，BYOD意味着控制权的丧失、额外的安全风险、以及许多其它的未知风险。所以，BYOD的部署及管理工作至关重要。

所谓BYOD，指的是携带自己的设备办公，这些设备包括个人电脑、手机、平板等（而更多的情况指手机或平板这样的移动智能终端设备。）人们可以在机场、酒店和咖啡厅等地方登录公司邮箱和在线办公系统，办公条件将不受时间、地点、设备、人员、网络环境的限制，BYOD向人们展现了一个美好的未来办公场景。

大多数的公司都认为，员工使用家用笔记本电脑来连接公司的VPN网络是非常安全的。在很多情况下，如果只允许家用笔记本通过web浏览器来访问公司网络的话，通常情况下的确是安全的。‘

但是，如果你不知道如何确保这些设备在访问其他网络时的安全性，那么你又如何能够保证这些设备与公司网络进行连接时的安全呢？如果某位员工的笔记本电脑中存在安全隐患，那么他将会把这个安全威胁引向公司的敏感数据。尤其是，当员工通过开放的WiFi热点连接至公司网络时，这一问题就变得更加的明显了。

为了回答这一问题，Duo安全实验室的研究专家们对以下七款OEM笔记本电脑进行了测试：

• Lenovo Flex 3

• HP Envy

• HP Stream x360

• HP Stream

• Lenovo G50-80

• Acer Aspire F15 

• Dell Inspiron 14

**研究结果**

真相往往是丑陋的。研究人员在对这些笔记本电脑的通信流量进行分析时，无论安装的是Windows 8.1还是Windows 10，这些笔记本电脑中都存在着大量严重的安全问题。

**技术细节**

研究过程中的前两分钟

在笔记本首次启动的时候，用户需要对笔记本的系统进行一些相关配置，其中也包括网络信息的设置。当配置完成之后，笔记本就可以进行联网通信了（具体下图所示）。设备所采用的协议为本地链路多播名称解析（LLMNR），有关这部分的具体信息可查看[RFC 4795](https://tools.ietf.org/rfc/rfc4795.txt)获取。

[![](https://p0.ssl.qhimg.com/t01c1576e00f14aca5d.png)](https://p0.ssl.qhimg.com/t01c1576e00f14aca5d.png)

通过DNS服务，设备就可以对本地网络中的主机名进行解析。但是与其他情况不同的是，我们在研究过程中使用的是IPv6。不幸的是，这仍然会使我们的Windwos笔记本处于安全风险之中，因为设备所连接的本地网络实际上是一个开放网络，就像咖啡店的免费Wi-Fi一样。

如果攻击者入侵了这一本地网络（或者咖啡店的Wi-Fi网络），那么攻击者就可以伪造DNS的查询相应信息，并且将攻击者的计算机伪装成指定的DNS服务器或者代理服务器。这样一来，攻击者就可以直接获取到目标用户的身份验证信息（明文），或者直接将用户重定向至钓鱼网站，然后获取用户所输入的敏感信息。

**IPv4世界中的IPv6**

众所周知，我们现在可使用的IPv4地址资源越来越少了。而且随着物联网设备的出现，也使得IPv6成为了现实。为了帮助我们目前的网络系统从IPv4向IPv6的过渡，现在也有很多种技术可以实现这一点。但不幸的是，在这些技术种，实际上并非所有技术都是安全的。

无论是哪一种技术，如果我们无法妥善地解决网络边缘设备的安全问题，那么攻击者就可以进行各种各样的中间人攻击。如果你只打算在家里使用你的笔记本电脑，而且你也认为你的路由器和互联网服务提供商可以帮助你抵御这种类型的攻击，那么我只能说你真的是过分自信了。

**第三方安全防护软件**

所有参与研究的笔记本电脑中，均安装有McAfee的反病毒产品。但是研究人员发现，McAfee反病毒软件会打开系统的6646端口。这个端口只会在系统启动之后短暂开启几分钟，然后就关闭了。但是在设备进行联网通信时，它又会自动开启。这种操作实际上是一种不安全的行为。

[![](https://p4.ssl.qhimg.com/t01eb643d89cdb87ef2.png)](https://p4.ssl.qhimg.com/t01eb643d89cdb87ef2.png)

**结论**

从网络安全的角度出发，这些笔记本电脑其实都还没有真正地准备好。除了HP Stream x360之外，其他受测试的笔记本电脑都表现得十分的糟糕。这些型号的笔记本电脑中没有哪一台是已经真正准备好去迎接现实世界中的安全挑战的。如果我们对笔记本电脑的操作系统进行重新配置，并且删除其中的一些软件，那么这台笔记本的安全性能将会得到大幅度提升。当然了，毕竟我们还没有办法能够保证你的笔记本电脑是绝对安全的。除此之外，我们还必须保持系统和软件的更新，在每一次安装升级补丁之后，你还需要确保这些升级程序没有修改你系统中的相应隐私设置。

**基本设置**

**1.    卸载McAfee，设置Windows Defender**

最重要的事情需要放在第一步来完成，对于那些不是微软签名版的计算机而言，请卸载McAfee。首先，在左下方的搜索栏中输入“Settings（设置）”，然后系统便会打开设置界面。选择“System（系统）”，点击“Apps&amp;features（程序和功能）”。然后在界面的搜索框中输入“McAfee”，系统将会显示有关McAfee的相关信息。选择“McAfee”，然后点击“Uninstall（卸载）”。

[![](https://p4.ssl.qhimg.com/t01a14d0a2983d754a0.png)](https://p4.ssl.qhimg.com/t01a14d0a2983d754a0.png)

在你点击了“卸载”按钮之后，系统将会弹出一个提示框并询问你是否需要继续。在这里我们需要注意的是，你必须确保McAfee的所有相关文件已经全部从你的计算机系统中删除了，其中也包括注册表中的相关设置。所以我们不仅要将文件删除，还要将注册表中的表项清理干净。

[![](https://p2.ssl.qhimg.com/t01d363ff173ebcccf1.png)](https://p2.ssl.qhimg.com/t01d363ff173ebcccf1.png)

在操作系统安装完成之后，屏幕的右下角将会弹出一个小的提示框，并提示用户“当前系统中没有安装反病毒软件，你需要使用Windows Defender”。点击提示信息之后，Windows Defender的界面将会显示在屏幕中，并且图标会立刻变绿。

[![](https://p4.ssl.qhimg.com/t01aacd4e33252e258a.png)](https://p4.ssl.qhimg.com/t01aacd4e33252e258a.png)

如果你还没有对计算机进行扫描的话，程序颜色将变成黄色。在你进行扫描之前，请点击“Update（更新）”按钮来进行更新。

[![](https://p3.ssl.qhimg.com/t01fa437d017bb1d2bd.png)](https://p3.ssl.qhimg.com/t01fa437d017bb1d2bd.png)

在我们进行完更新之后，我们就可以使用Windows Defender来扫描我们的计算机了。如果用户愿意的话，它还可以定时对系统进行自动扫描。在所有的设置完成之后，用户还需要重启计算机才能使设置生效。

**2.    修改防火墙设置**

在进行这一步操作之前，我假设大家已经将McAfee卸载了，因为如果你没有卸载McAfee，那么你的设置过程中将会出现错误。现在，请大家点击“开始”图标，然后选择“控制面板”，有关Windows防火墙的设置会出现在页面的底部。点击之后，你将会看到：

[![](https://p3.ssl.qhimg.com/t01bfcbca25f03ab537.png)](https://p3.ssl.qhimg.com/t01bfcbca25f03ab537.png)

在“控制面板”的左侧，你可以看到“Change notification settings（修改通知设置）”选项。点击之后，在公共网络设置选项中，勾选““Block all incoming connections, including those in the list of allowed app(阻止所有与未在允许程序列表中的程序的连接)”

[![](https://p3.ssl.qhimg.com/t01743d76f7ddbc7faa.png)](https://p3.ssl.qhimg.com/t01743d76f7ddbc7faa.png)

现在，防火墙的设置界面将会出现一个巨大的红色禁止图标：

[![](https://p0.ssl.qhimg.com/t01058eb8a14dd767b2.png)](https://p0.ssl.qhimg.com/t01058eb8a14dd767b2.png)

操作已经完成了！请重启系统，然后尽情使用吧！

**PDF下载地址：[https://yunpan.cn/cYtbsF6w6Mh9A](https://yunpan.cn/cYtbsF6w6Mh9A) （提取码：0a10）**
