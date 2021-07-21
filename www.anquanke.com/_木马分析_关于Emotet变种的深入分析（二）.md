> 原文链接: https://www.anquanke.com//post/id/86132 


# 【木马分析】关于Emotet变种的深入分析（二）


                                阅读量   
                                **110964**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fortinet.com
                                <br>原文地址：[http://blog.fortinet.com/2017/05/09/deep-analysis-of-new-emotet-variant-part-2](http://blog.fortinet.com/2017/05/09/deep-analysis-of-new-emotet-variant-part-2)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p5.ssl.qhimg.com/t01ffedf82256029513.jpg)](https://p5.ssl.qhimg.com/t01ffedf82256029513.jpg)**

****

翻译：[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**稿费：140RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**传送门**

[**【木马分析】关于Emotet变种的深入分析（一）**](http://bobao.360.cn/learning/detail/3877.html)

**<br>**

**一、背景**

本文是FortiGuard实验室对Emotet最新变种深入分析的第二篇文章。在第一篇文章中，我们分析了如何绕过服务端的反调试和反分析技术，从C&amp;C服务器上下载3~4个恶意模块（.dll文件）。在第一篇中，我们只分析了其中一个模块（我将其命名为“module2”）。在这篇文章中，我们会分析其他模块的工作流程。

<br>

**二、从微软Outlook PST文件中窃取邮件地址**

正如我在第一篇文章中介绍的那样，我们正在分析的第一个模块（我将其命名为“module1”）在某个线程函数（ThreadFunction）中完成加载，模块的主要功能是读取PST文件，遍历所有的Outlook账户。PST文件是微软Outlook中个人文件夹所对应的文件，保存了用户的电子邮件信息、日历、任务以及其他项目。PST文件通常位于计算机中的“DocumentsOutlook Files”目录，如图1所示：

[![](https://p5.ssl.qhimg.com/t0126d15b37da6204de.png)](https://p5.ssl.qhimg.com/t0126d15b37da6204de.png)

图1. PST文件

微软提供了一套名为MAPI（Microsoft Outlook Messaging API，微软Outlook消息API）的API函数，开发者可以使用MAPI来处理PST文件。module1中使用了MAPI。

一旦module1文件运行起来，它会创建一个临时文件，用来存储已窃取的Outlook相关信息，包括Outlook版本信息、电子邮件地址等。接下来module1会加载某些MAPI函数。module1加载和使用MAPI的方式如图2所示。

[![](https://p4.ssl.qhimg.com/t01b6dbae8b72c49f8c.png)](https://p4.ssl.qhimg.com/t01b6dbae8b72c49f8c.png)

图2. 加载MAPI函数

接下来，该模块会根据计算机上的Outlook账户，读取所有的PST文件，遍历每个账户的每个文件夹中（如收件箱、已删除邮件、垃圾邮件、已发送邮件等）带有未读标识的所有邮件信息。该模块会窃取每封未读邮件中的发件人姓名和邮件地址。Facebook发给我的一封通知邮件如图3所示：

[![](https://p5.ssl.qhimg.com/t018bb15d8b945578d8.png)](https://p5.ssl.qhimg.com/t018bb15d8b945578d8.png)

图3. 未读邮件示例

对于图3所示的这封未读邮件，module1窃取的具体信息如图4所示。其中“Facebook”代表的是发件人名字，而“notification+kr4yxeragnmn@facebookmail.com”代表的是发件人邮箱地址。

[![](https://p5.ssl.qhimg.com/t018f6f398140f39031.png)](https://p5.ssl.qhimg.com/t018f6f398140f39031.png)

图4. 保存在内存缓冲区中的已窃取的邮件信息

正如我之前提到的，已窃取的数据会保存在一个临时文件中，本例中，该文件名为“AE74.tmp”。当module1准备加密已窃取的信息并将该信息发往服务器时就会读取这个文件。加密前的数据如图5所示，该数据读取自“AE74.tmp”文件。

[![](https://p1.ssl.qhimg.com/t011fe8104237cf9fdf.png)](https://p1.ssl.qhimg.com/t011fe8104237cf9fdf.png)

图5. 加密前的数据

你可以看到，这个数据中包含Outlook版本以及已窃取的邮件信息。加密完成后，module1会通过POST请求将该数据发往C&amp;C服务器。WireShark抓取的对应报文如图6所示。

[![](https://p4.ssl.qhimg.com/t01f413f3033dc43da4.png)](https://p4.ssl.qhimg.com/t01f413f3033dc43da4.png)

图6. 发往C&amp;C服务器的加密数据

<br>

**三、使用C&amp;C服务器模板发送垃圾邮件**

这是Emotet恶意软件四个模块中最大的一个模块（我将其命名为“module4”）。该模块的主要功能是向已窃取的邮件地址发送垃圾邮件。当该模块在线程中执行时，它会调用CoCreateGuid函数生成一个GUID，然后使用base64算法对GUID进行编码，将其作为cookie值发往C&amp;C服务器。服务器的响应报文中包含加密的垃圾邮件信息以及目标邮件地址。如下两张图分别代表C&amp;C服务器返回的响应报文以及解密后的报文内容。

[![](https://p4.ssl.qhimg.com/t0132564193bbb5cd42.png)](https://p4.ssl.qhimg.com/t0132564193bbb5cd42.png)

图7. 发往C&amp;C服务器的GUID以及收到的响应报文

[![](https://p1.ssl.qhimg.com/t01593384086dbad407.png)](https://p1.ssl.qhimg.com/t01593384086dbad407.png)

图8. 解密后的垃圾邮件模板以及邮件地址

一旦module4收到解密后的数据，它会解析出数据中包含的垃圾邮件模板以及目标邮件地址。module4支持25端口（常规端口）以及587端口（SSL）上的SMTP协议。图9显示了module4如何使用SMTP协议散布垃圾邮件，图10显示了Wireshark中抓取的报文内容，图11显示了邮件客户端中收到的垃圾邮件。

[![](https://p3.ssl.qhimg.com/t0189a5a8d6e04e9282.png)](https://p3.ssl.qhimg.com/t0189a5a8d6e04e9282.png)

图9. 生成SMTP报文的相关代码和数据

[![](https://p4.ssl.qhimg.com/t010cec32988ab2c697.png)](https://p4.ssl.qhimg.com/t010cec32988ab2c697.png)

图10. Wireshark中抓取的垃圾邮件

[![](https://p5.ssl.qhimg.com/t01a570cb0c487d977d.png)](https://p5.ssl.qhimg.com/t01a570cb0c487d977d.png)

图11. 邮件客户端中收到的垃圾邮件

如图11所示，你可以看到垃圾邮件试图诱骗邮件接收者访问某个URL，该URL指向某个恶意Word文档。图12显示了该文档在VirusTotal上的检测结果。

[![](https://p4.ssl.qhimg.com/t01dc3e994c9ae379dd.png)](https://p4.ssl.qhimg.com/t01dc3e994c9ae379dd.png)

图12. VirusTotal上的反病毒软件检测结果

<br>

**四、总结**

通过深入分析Emotet最新变种，我们可以发现该变种重点在于从受害者设备上窃取邮件相关数据，然后利用该设备以及已收集的邮件地址发送垃圾邮件，进而传播其他恶意软件。

需要注意的是，在我的分析过程中，我发现服务端的反调试技术时而有效，时而无效。

FortiGuard Webfilter服务已将该恶意软件的垃圾邮件中的相关URL标记为恶意网站，所下载的Word文档也被FortiGuard反病毒服务标记为WM/Agent.DEA!tr.dldr。

<br>

**五、四个模块的总结**

Module1（大小为1c000H）：从Outlook PST文件中窃取邮件地址以及收件人名称。

Module2（大小为32000h）：从已安装的Office Outlook、IncrediMail、Group Mail、MSN Messenger、Mozilla ThunderBird等软件中窃取凭证信息。该模块的分析可以参考之前的那篇文章。

Module3（大小为70000h）：窃取浏览器中已保存的信息。该模块比较简单，我不再赘述。

Module4（大小为0F0000h）：通过发送垃圾邮件传播其他恶意软件。

<br>

**六、攻击指示器（IoC）**

**URL地址：**

```
hxxp:// hand-ip.com/Cust-Document-5777177439/
```

**样本SHA256哈希值：**



```
ORDER.-Document-7023299286.doc：
D8CFE351DAA5276A277664630F18FE1E61351CBF3B0A17B6A8EF725263C0CAB4
```



**七、参考资料**

[https://support.office.com/en-us/article/Introduction-to-Outlook-Data-Files-pst-and-ost-6d4197ec-1304-4b81-a17d-66d4eef30b78](https://support.office.com/en-us/article/Introduction-to-Outlook-Data-Files-pst-and-ost-6d4197ec-1304-4b81-a17d-66d4eef30b78) 

[https://support.microsoft.com/en-us/help/287070/how-to-manage-.pst-files-in-microsoft-outlook](https://support.microsoft.com/en-us/help/287070/how-to-manage-.pst-files-in-microsoft-outlook) 

[https://msdn.microsoft.com/en-us/library/office/cc765775(v=office.14).aspx](https://msdn.microsoft.com/en-us/library/office/cc765775(v=office.14).aspx) 

<br>



**传送门**

[**【木马分析】关于Emotet变种的深入分析（一）**](http://bobao.360.cn/learning/detail/3877.html)

<br>
