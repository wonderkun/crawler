> 原文链接: https://www.anquanke.com//post/id/84674 


# 【技术分享】海康威视网络摄像机远程访问发现XXE漏洞


                                阅读量   
                                **148695**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://medium.com/@iraklis/an-unlikely-xxe-in-hikvisions-remote-access-camera-cloud-d57faf99620f?swoff=true](https://medium.com/@iraklis/an-unlikely-xxe-in-hikvisions-remote-access-camera-cloud-d57faf99620f?swoff=true)

译文仅供参考，具体内容表达以及含义原文为准

<br style="text-align: left">

[![](https://p5.ssl.qhimg.com/t01bb7cb6463e6983c5.png)](https://p5.ssl.qhimg.com/t01bb7cb6463e6983c5.png)



当我想从我的Elisa Live 网络摄像机上获取管理员权限时，却在后台系统里发现了XXE漏洞。相机的制造商是网络摄像机市场的巨头海康威视。

随着物联网技术的发展，关于其安全性的隐患也逐渐被暴露出来，简单再google上进行一下搜索，就可发现近年间相关领域发布了数百篇论文和白皮书。

大约两个月以前的一个周末，我想研究一下网络摄像机，于是在亚马逊上买了一个比较便宜的，这个摄相机没有任何已知的安全漏洞。上面写着Elisa Live 1280×720像素高清网络摄像机。

我会尽量用简洁的话语来写这篇文章，所以我会将重点放在XXE的发现过程上，我不会写我研究相机的每个详细步骤，只写和发现XXE有关的部分。

**关于摄像机**

这是一台由海康威视贴牌生产的RC8221 型号摄像机，海康威视公司是一家总资产达200亿美元的公司，是监控产品行业的市场领导者，约占整个市场的20%份额。Elisa是一家芬兰公司，为用户查看摄像机的实时数据提供云服务。

渐渐地我发现，如果不通过他们的云服务平台，你就不能访问摄像机。换句话说，摄像机的数据要被上传到他们的后台系统中然后你再通过网页或者手机应用访问这些数据。

**初步尝试**

我通过它的以太网接口把摄像机连接到我的实验室，并且开始拦截网络流量。如果你曾经想做与物联网设备有关的实验，我强烈建议不要急于把设备连接进互联网。一些设备安装了旧的或者不安全的固件，我们需要首先检查是否有更新。

Wireshark泄露了两个有趣的未加密调用，如【图-1】：

 

[![](https://p3.ssl.qhimg.com/t01d581ecb29891284b.png)](https://p3.ssl.qhimg.com/t01d581ecb29891284b.png)



图1：向www.hik-online.com发出的POST请求

这是一个向 www.hik-online.com网站发出的Post请求，看起来是一个base 64编码后的密码，我们把它记录下来稍后分析。另一个是一个从amazon S3存储中下载更新的Get请求，如【图2】。我们可以从这里下载固件。

[![](https://p1.ssl.qhimg.com/t0132f5e88553ccf42c.png)](https://p1.ssl.qhimg.com/t0132f5e88553ccf42c.png)

 图2： 从S3中下载更新的GET 请求

**（不能）访问我的摄像机**

Nmap快速扫描可以显示一些开放端口，包括一个带有登陆页面的网页服务。我用一些海康威视常用的默认用户名和密码尝试登陆，但很快就知道这样是没用的。验证证书的控制器受http摘要认证机制保护，这是这个固件独有的特点。

利用binwalk和[hiktools](https://github.com/aloz77/hiktools)[1]分析固件，我提取到了一些有趣的信息，但其中并没有任何关于http认证的信息。Root密码是hiklinux，以下是/etc/passwd的内容，如【图3】，仅供参考。



[![](https://p1.ssl.qhimg.com/t018ba6baf6439fe8cb.png)](https://p1.ssl.qhimg.com/t018ba6baf6439fe8cb.png)

图3：/etc/passwd的内容 



SSH的端口是关闭的，所有我没法利用这个弱密码，但是我注意到，我在升级之前进行的第一次扫描的时候SSH的端口是没关闭的。<br style="text-align: left">

<br style="text-align: left">

**访问摄像机**

回到第一个POST请求中我们可以看到，它包括一个Base64编码的字符串。但解码之后是一堆乱码。密钥就在固件的某个地方，只是需要我们去寻找。我没有核实是否这个密码是摄像机用来对服务器进行身份验证的，或者是摄像机启动后提交给海康威视的密码。

我不得不承认对自己的进展有点灰心，花了两天时间基本没有什么发现。我便浏览了海康威视的网站，结果发现了这个：



这是一个漏洞悬赏，让我们试试POST请求。

由于这是一个XML的post请求，我首先就尝试用SYSTEM entity来请求本地或外部文件，如【图4】。本地文件读取并没有凑效，所以我创建了一个VPS等待传入连接，发现成功了，如【图5】：

 

[![](https://p4.ssl.qhimg.com/t0102f6a8bb15a1d70b.png)](https://p4.ssl.qhimg.com/t0102f6a8bb15a1d70b.png)

 图4：尝试XML实体注入攻击<br>

<br style="text-align: left">

[![](https://p0.ssl.qhimg.com/t015f731844f49fd9e0.png)](https://p0.ssl.qhimg.com/t015f731844f49fd9e0.png)

****

图5：VPS收到连接**<br style="text-align: left">**

这就有意思了啊，既然我们可以使用系统实体加载外部文件，何不尝试通过恶意DTD回传文件内容呢。例如，/etc/hosts文件。

**[XXEinjector](https://github.com/enjoiz/XXEinjector)[2]****.**是一个不错的工具，它可以自动完成这一过程，如【图6】。

[![](https://p4.ssl.qhimg.com/t0173f64c56ce1ca503.png)](https://p4.ssl.qhimg.com/t0173f64c56ce1ca503.png)

图6：使用XXEinjector读取任意文件<br>

成功了。我们可以在服务器上读取任意文件。但是Tomcat服务器运行于什么权限呢？我成功读取了/etc/shadow文件的内容，所以一定是root权限。

在这个时候，我停下来向海康威视披露得到调查结果的过程。如果我是心怀不轨的黑客，我可能会继续入侵10个服务器（hik-online.com分布在全球的存在漏洞的其他api服务器）。如果Tomcat的数据库连接字符串不通往任何地方，可做更多的事情，例如寻找适用硬编码的证书或密钥连接其他服务器的脚本。

访问10万台以上的网络摄像机将不是什么难事！

服务器漏洞是http://www.hik-online.com/后端系统的一部分——海康威视提供的通过Web访问你的PVR和相机服务。

 

**与供应商的交流过程和奖励**

****

**· **2016年8月6日  ：发送第一封邮件到危险品研究中心

**· **2016年8月16日：危险品研究中心没有回应，又发送了一封快捷邮件

**· **2016年9月6日  ：重新给海康威视营销和公关联系人发了一封邮件

**· **2016年9月7日  ：危险品研究中心确认接收并要求发送更多信息

**· **2016年9月8日  ：海康威视修复了漏洞，并要求我重新测试

**· **2016年9月25日：收到我的奖励，一个价值69美元的网络摄像机。

**结论**

如果你接受XML的内容，请确认没有XXE漏洞。还要确保你做任何事都使用HTTPS协议，这样还是可以确保自身的信息安全的。

 

**附**

hiktools     ：   [https://github.com/aloz77/hiktools](https://github.com/aloz77/hiktools) 

XXEinjector :  [https://github.com/enjoiz/XXEinjector](https://github.com/enjoiz/XXEinjector)


