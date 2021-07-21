> 原文链接: https://www.anquanke.com//post/id/179999 


# GeForce Experience OS 命令注入


                                阅读量   
                                **188575**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者rhinosecuritylabs，文章来源：rhinosecuritylabs.com
                                <br>原文地址：[https://rhinosecuritylabs.com/application-security/nvidia-rce-cve-2019-5678/](https://rhinosecuritylabs.com/application-security/nvidia-rce-cve-2019-5678/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0114ad91f5c523b510.jpg)](https://p4.ssl.qhimg.com/t0114ad91f5c523b510.jpg)



## 0x01 漏洞概述

在这篇文章中，我将分享我是如何发现可利用NVIDIA GeForce Experience (GFE)来造成远程代码执行漏洞，版本号小于3.19的GFE均存在该漏洞。这个漏洞被分配编号： CVE-2019-5678。用户访问攻击者控制的站点，轻敲几下键盘，用户的主机就会被控制。用户启动GFE时，有一个名为”Web Helper”的本地服务也会启动，并且该服务存在命令注入漏洞。

### <a class="reference-link" name="0x01.1%20NVIDIA%20GFE"></a>0x01.1 NVIDIA GFE

英伟达官方网站是这样描述GeForce Experience的：”让您的驱动程序时刻保持最新状态、一键优化游戏设置，还可与朋友们录制游戏视频、捕捉游戏画面和直播。”很容易可以看出它是一个辅助应用，附加在英伟达产品中，以帮助用户细化功能。



## 0x02 漏洞挖掘

### <a class="reference-link" name="0x02.1%20%E5%8F%91%E7%8E%B0%E6%BC%8F%E6%B4%9E"></a>0x02.1 发现漏洞

MWR Labs曾发表一篇关于GFE LPE漏洞的[文章](https://labs.mwrinfosecurity.com/advisories/nvidia-geforce-experience-lpe/)，GFE会开启一个本地API服务器，用户可以通过它来控制GFE的各个方面。例如，当用户更改GFE GUI界面的某些设置时，很有可能是调用了该本地的API。了解到这点，我觉得应该深入探究一下这个API，看看是否有其他有趣的功能。GFE开启的这个服务器是基于NodeJS Express框架的，在”C:Program Files (x86)NVIDIA CorporationNvNode”中可以找到许多它的源文件。

如需发送有效的请求，HTTP标头中必须附有一个启动时随机生成的token值，储存在”%LOCALAPPDATA%NVIDIA CorporationNvNodenodejs.json”中，该文件还包含一个随机开放的端口。文件名为静态，不会改变，因此研究者可以轻易地在本地电脑中找到。下图展示了其中的内容：

[![](https://p2.ssl.qhimg.com/t01e2525426432e84af.webp)](https://p2.ssl.qhimg.com/t01e2525426432e84af.webp)

### <a class="reference-link" name="0x02.2%20%E6%A0%87%E5%A4%B4%E6%B5%8B%E8%AF%95"></a>0x02.2 标头测试

首先，我测试是否可以绕过表头的身份验证机制并发送有效的请求。在`index.js : 185`中可以看到，它只是将用户发送的标头与本地的token进行对比，如果失败则返回403。

[![](https://p4.ssl.qhimg.com/t01b683c33774a86757.png)](https://p4.ssl.qhimg.com/t01b683c33774a86757.png)

然而我没有找到Bypass的方法，因为这过于直接。但我还发现其他有趣的东西，它使用了CORS。在`index.js : 185`中标头“Access-Control-Allow-Origin”被设置为”*”并应用于所有请求。这意味着如果用户token值发生泄露，可以从其他Origin发送请求给服务器例如攻击者控制的网站。此外，攻击者还可以通过XHR请求发送自定义安全标头的请求。

### <a class="reference-link" name="0x02.3%20API%E6%B5%8B%E8%AF%95"></a>0x02.3 API测试

考虑到这点，我开始测试能否通过成功发送请求来造成代码执行。我全局搜索”exec”，最后在NvAutoDownload.js中找到了该函数：

[![](https://p1.ssl.qhimg.com/t01f879fd27f13a7619.webp)](https://p1.ssl.qhimg.com/t01f879fd27f13a7619.webp)

从上面这段代码你可以看到，用户发送POST请求给“/gfeupdate/autoGFEInstall/”，并将Content-Type设置为”text/*”，然后将POST过来的文本内容直接插入到”req.text”再通过childproc函数，并作为操作系统命令执行。我拦截正常的请求，测试修改内容以确保它可以正常运行。

[![](https://p4.ssl.qhimg.com/t01171d263b1ff3521d.webp)](https://p4.ssl.qhimg.com/t01171d263b1ff3521d.webp)

上图的请求可以打开”calc.exe”。这本身也没有多大的问题，因为真实情况下攻击者完全不知道token是多少。所以下一步就是测试是否有办法读取储存token的文件。



## 0x03 Exploitation

前面我们已经讨论过可以通过浏览器来实施攻击，简单地说这是由于错误的的CORS策略。如要攻击成功仍需拿到受害者的token。我想到了解决办法，可以诱导用户上传储存token的文件。这听起来有些天方夜谭，但由于储存token的文件路径及名称是静态的，所以这非常容易实现，只要引诱用户按几个键就可以实现命令注入。

### <a class="reference-link" name="0x03.1%20%E6%94%BB%E5%87%BB%E6%AD%A5%E9%AA%A4"></a>0x03.1 攻击步骤

在Chrome中可以通过键盘按键复制任意内容到剪切板，Firefox则有些不同需要鼠标的配合。在Chrome浏览器中只需按三个键”CTRL+V+Enter”，即可成功利用。

按键功能：
1. “CTRL” – 将储存token文件的路径“％LOCALAPPDATA％ NVIDIA Corporation NvNode nodejs.json”复制到剪切板，同时还会打开文件上传的窗口并选择传文件。
1. “V” – 粘贴剪切板内容到上传路径处。
1. “Enter” – 上传nodejs.json文件，同时读取文件内容。
1. 然后，将token值组合到XHR请求中，并且发送请求给GFE API端点，最后造成命令执行。
攻击演示：

[![](https://rhinosecuritylabs.com/wp-content/uploads/2019/06/RCE-GIF.gif)](https://rhinosecuritylabs.com/wp-content/uploads/2019/06/RCE-GIF.gif)

## 0x04 小结

这个攻击确实需要用户的交互，但交互量非常小，欺骗用户按几个按钮不是什么难事。这个漏洞的真正问题是本地服务器的API端点运行所有Origin发送跨源资源共享请求，这意味如果token发送泄漏，则可以通过浏览器对受害者本地电脑的GFE任意API端点发送XHR请求。

命令注入漏洞在最新版的GFE（3.19）中已修复，请立即升级！NVIDIA的修复方法似乎值是将造成命令注入的端点直接删除。它们没有修复宽松的CORS策略，并且仍把nodejs.json文件存放在静态位置。所以我们仍然可以用这篇文章讲的方法与GFE API端点交互。

如果你不使用GFE，最好将它卸装。我已将这篇文章的概念证明文件上传至[GitHub](https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2019-5678)，如有兴趣可自行下载研究。
