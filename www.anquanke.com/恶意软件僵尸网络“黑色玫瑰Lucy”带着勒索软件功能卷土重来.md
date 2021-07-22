> 原文链接: https://www.anquanke.com//post/id/204629 


# 恶意软件僵尸网络“黑色玫瑰Lucy”带着勒索软件功能卷土重来


                                阅读量   
                                **266949**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者David Bisson ，文章来源：https://securityintelligence.com/
                                <br>原文地址：[https://securityintelligence.com/news/black-rose-lucy-malware-botnet-returns-with-ransomware-capabilities/](https://securityintelligence.com/news/black-rose-lucy-malware-botnet-returns-with-ransomware-capabilities/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0182f0909ea8241437.jpg)](https://p0.ssl.qhimg.com/t0182f0909ea8241437.jpg)

据安全研究人员称，“黑玫瑰Lucy”恶意软件僵尸网络已将勒索软件功能纳入其攻击工具包。

就在前不久，一名Android恶意软件研究人员通过推文曝光了一个名叫“黑色玫瑰Lucy”的恶意软件僵尸网络。而根据CheckPoint的最新研究，最新版本的恶意软件僵尸网络“黑色玫瑰Lucy”带着勒索软件功能卷土重来了。在此之后，CheckPoint安全公司便立刻收集到了一些该恶意软件的样本，并发现该恶意软件现在会伪装成视频播放器等多媒体类应用程序来感染用户。在这种伪装的外壳之下，恶意软件将会试图引诱目标用户启用辅助性服务（Accessibility Services）以尽可能减少安装勒索软件Payload时所需要的用户交互。除此之外，恶意软件还使用了两个命令来让目标设备保持屏幕常亮以及WiFi连接。

当该恶意软件与其四台命令控制（C&amp;C）服务器之一成功建立连接之后，恶意软件将会接收到一个名叫“Key”的响应字符串。接下来，恶意软件将会是哟ing一个服务来获取受感染设备的目录数组。通过利用这些信息，“黑色玫瑰Lucy”将会对数组中存储的所有文件及目录进行加密，并同时将勒索信息显示给目标用户，而且攻击者竟然还将显示的勒索信息伪装成了来自美国联邦调查局（FBI）的通知。这条信息将告知目标用户，执法人员在其设备上发现了色情内容，并要求目标用户支付500美元的罚款，以便调查人员撤销对他们的调查，或者是减轻其罪行。



## 黑色玫瑰Lucy

恶意软件“黑色玫瑰Lucy”早在2018年被CheckPoint安全公司的研究人员发现时，并没有嵌入有勒索软件的功能。<br>[![](https://p0.ssl.qhimg.com/t01b464d5829c619d6b.png)](https://p0.ssl.qhimg.com/t01b464d5829c619d6b.png)<br>
当时，这个勒索软件及服务（MaaS）僵尸网络依赖于两个组件来实现其而已功能。Lucy加载器即是其第一个组件，它可以作为远程控制仪表盘来将受感染设备合并到僵尸网络中，并在目标设备上安装其他的恶意软件Payload。而第二个元素就是“黑色玫瑰Lucy”的Dropper针对的是Android设备，它可以收集目标Android设备的信息，并通过从僵尸网络的命令控制服务器接收二级恶意软件来进一步感染目标设备。



## 如何保护企业免受“黑色玫瑰Lucy”的感染

安全专业人员可以利用强大的安全策略来强制实施移动安全最佳实践方案，从而帮助各子企业和组织抵御恶意软件“黑色玫瑰Lucy”的攻击。这些指导原则应该包括限制员工可以在其工作设备上安装应用程序的位置和开发人员的类型等。此外，信息安全人员可以考虑使用由人工智能（AI）驱动的工具来辅助应付复杂的威胁。
