> 原文链接: https://www.anquanke.com//post/id/86570 


# 【DEFCON】看我如何黑掉投票机


                                阅读量   
                                **95115**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：horner.tj
                                <br>原文地址：[https://blog.horner.tj/post/hacking-voting-machines-def-con-25](https://blog.horner.tj/post/hacking-voting-machines-def-con-25)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0146c1d797baad35c8.png)](https://p5.ssl.qhimg.com/t0146c1d797baad35c8.png)

****

译者：[**myswsun**](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：180RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**0x00 前言**

DEFCON 25是我第一次参加DEFCON安全会议，并且它非常精彩。**有个First-time Village称为“Voting Village”。你可以在其中享受侵入各种投票注册机的乐趣。**我的朋友Sean和我在会议通告中看到了这个Village。我们决定花30分钟在演讲前观察下每个人的进展。我们没想到，这最终变成了针对投票机的长达8小时的hacking活动。

<br>

**0x01 目标机器**

我们决定选择[ExpressPoll 5000](http://www.essvote.com/products/5/11/electronic-poll-books/expresspoll-5000%C2%AE/)投票注册机，因为还没人取得进展。

[![](https://p3.ssl.qhimg.com/t011e5840640e16f099.png)](https://p3.ssl.qhimg.com/t011e5840640e16f099.png)

它使用古老的PCMCIA/CF插槽来传输数据，并保存了各种各样的数据库文件。幸运的是，village提供了大量的PCMCIA卡和PCMCIA的USB转换器，因此我们能使用它作为我们的存储设备。

<br>

**0x02 常规发现**

下面是我们在exploit这个设备时发现的有用的东西的列表：

**它运行于Windows CE5.0**

**ExpressPoll软件是一个包含程序集名ExPoll的.NET应用**

**ExpressPoll软件使用WinForms作为UI**

**Bootloader是特有的**

**处理器的架构是ARM**

**数据库文件存储在内存卡上（稍后有更多细节）**

<br>

**0x03 Exploit**

我们测试了几种exploit方式，如常规方式：缓冲区溢出，Windows关键方式，网络exploit等。下面我们来针对这些方式逐一讲解。

<br>

**0x04 任意固件注入**

当内存卡插入到机器中，bootloader首先检查文件NK.BIN。如果能找到这个文件，它将试图将它加载到RAM中，并且不使用签名验证来引导它。然后固件被刷进去了，直到下次启动都有效。

NK.BIN文件是通常与ExpressPoll软件捆绑一起作为Windows CE 5.0的更新，但是攻击者能上传并运行任意自定义的NT kernel和Linux image（目前还没测试）。

我们在ExpressPoll 5000上面测试了这个，非常确定，它无错加载了我们的Windows CE：

[![](https://p4.ssl.qhimg.com/t014c50dd7fe2185ba0.png)](https://p4.ssl.qhimg.com/t014c50dd7fe2185ba0.png)

<br>

**0x05 任意Bootloader注入**

和固件注入exploit非常类似，bootloader也会在启动时检查更新，文件名为EBOOT.BIN。它也是没有签名验证就加载了，但是我们得不到能成功运行于机器上的bootloader。然而，bootloader注入是确认有效的，因为我们放入EBOOT.BIN文件的bootloader确实刷入了，并且在没有内存卡的情况下重启了。这意味着我们摸索到了一些东西。

<br>

**0x06 .NET .resources文件覆盖**

当ExpressPoll软件由“启动ExpressPoll”按钮启动时，它读取内存卡中的文件ExPoll.resources。这是定义应用使用的资源的文件，如字符串、图片、按钮、布局等。它可以用于覆盖和自定义注册过程（例如，增加自己的专属logo）。

这个系统的弱点是按钮（也可以是其他的UI元素）可以被覆盖为不同的操作，如运行存储在内存卡(mount到了类似/Storage Card的目录)中的可执行文件或者运行命令。

如果找到了ExPoll.resources文件，首先将它加载到内存中，将其用于本次会话，并将它拷贝到设备的内存中，因此它再次被使用了。

这个漏洞可以通过创建一个随机的.NET .resources文件（名为ExPoll.resources）并拷贝到内存卡中来确认。我们将内存卡从机器中弹出，按“启动ExpressPoll”按钮，它出错了。哇！！！它加载了那个文件。不过，由于它也被拷贝到内存中，如果文件是损坏的它将会出错（你不能看到“启动ExpressPoll”按钮）。还有，在我们的设备中这种状态下没有出现任何图像。

<br>

**0x07 漏洞**

和上面的exploit一起，我们找到了很多安全漏洞可以导致多种类型的攻击。

<br>

**0x08 硬编码用户名和密码**

当你启动ExpressPoll软件时，你需要输入一个数字和用户名/密码。

有一组用户名/密码硬编码到软件中总是能有效：

**用户名：1**

**密码：1111**

<br>

**0x09 未加密的SQLite3 数据库**

当启动ExpressPoll软件时，它在内存卡中查找文件PollData.db3。这是一个标准的未加密的SQLite3数据库文件，包括了所有的信息。投票，会议，选手，所有的一切。使用这个信息，攻击者能够采用多种类型的攻击：

**数据exfiltration**

例如，攻击者能使用包含空的数据库的内存卡，当注册投票时默默的换卡，获取整个投票者的数据库（包括名字，地址，SSN后4位，签名和其他）。

**伪造投票者信息**

例如，攻击者能使用假的投票者的信息迷惑伪造数据库（如改变签名等），并在注册时将它植入机器中。

**其他攻击**

当你能访问整个数据库时，想象力是无限的。

[![](https://p3.ssl.qhimg.com/t015bdea3229926f386.png)](https://p3.ssl.qhimg.com/t015bdea3229926f386.png)

<br>

**0x0A 打开USB端口**

这个威胁不大，但是还是存在威胁。攻击者能够插拔任意的USB设备（如USB Rubber Ducky 或 LAN Turtle）来发起攻击。我已经测试了下，用我的Bash Bunny来通过垃圾邮件将一个字符“a”无限循环发送到其中一个文本框中，试图触发缓冲区溢出并使.NET应用程序崩溃（但是它不起作用）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011b30ec9ba3abd132.png)

<br>

**0x0B 默认的WinCE web服务器**

默认的Windows CE服务器的开放端口是80，其可能是个安全隐患。使用这个服务器没能得到啥，因此需要进一步研究。

<br>

**0x0C 尝试其他攻击**

我们尝试了其他攻击，但是都无效。

<br>

**0x0D 内存溢出**

使用Bash Bunny，我写了个payload，来无限循环发送一个字符“a”到一个文本框中，并将它插入机器等了约一个小时。时间到了，机器变卡了，但是没有崩溃。

<br>

**0x0E 再次内存溢出**

使用上述的SQLite3数据库中的ConsolidationMaps表，将map image大小修改为大于1GB，并加载它。也没如预期导致.NET应用退出。它出错了（因为malloc()分配失败）但是没有崩溃。它会重启。

<br>

**0x0F 安装Grub（差点有效）**

我们试图为ARM架构创建一个Grub映像，但是我们不能在village关闭前完成构建。如果你能访问一个ARM Grub映像和ExpressPoll5000，那么尝试使用EBOOT.BIN的方式安装它。如果有效请告诉我。
