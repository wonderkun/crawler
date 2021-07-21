> 原文链接: https://www.anquanke.com//post/id/84885 


# 【技术分享】Gmail帐号劫持漏洞（含演示视频）


                                阅读量   
                                **244804**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securityfuse
                                <br>原文地址：[blog.securityfuse.com/2016/11/gmail-account-hijacking-vulnerability.html](blog.securityfuse.com/2016/11/gmail-account-hijacking-vulnerability.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0146bcc8be49763d3a.png)](https://p4.ssl.qhimg.com/t0146bcc8be49763d3a.png)

**翻译：**[**twittered******](http://bobao.360.cn/member/contribute?uid=245645961)

**稿费：90RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版******](http://bobao.360.cn/contribute/index)**在线投稿**

**<br>**

**介绍**

Gmail 允许全世界各地的使用者使用多个邮箱去关联他们的Gmail，Gmail也允许一个邮箱使用多个地址，向这些邮箱发送的邮件会被汇集到同一个邮箱。说实话，这两种模式在身份确认上存在风险，为绕过认证提供了机会。他和添加一个新的绑定相似，只不过我是一个攻击者，我可以通过邮箱所有权的验证劫持电子邮箱地址，还可以用它发出邮件。

<br>

**技术细节**

在你点击了Gmail的设置按钮之后，你会看到两个模块，其中一个叫做 " Account and Import "（账户和导入）&gt;”send mail as”(用这个地址发送邮件)你可以选择让上面的模块生效。这其中有一个脆弱的逻辑漏洞，允许我劫持Gmail的邮件地址。所有和Gmail SMTP有关系的邮箱都存在这个问题。他可能是@gmail.com , @googlemail.com或者是@googleemail.com等等。总所周知，Gmail会告诉我们邮件是否被发送成功。举例来说，如果我们发送的邮件地址是不存在的，或者这个地址无法连接网络，Gmail会给我们一个包含状态的通知信息，告诉我们为什么Gmail没有投递成功。

为了劫持一个邮箱，应包含以下因素之一，以确保成功：

1. 收件人的SMTP下线了

2. 收件人已停用他的电子邮件

3. 收件人不存在

4. 收件人存在，但是阻止了投递

5. 可能存在的其他状况

上诉情况，收件人无法从我们的地址收到任何邮件，而我们只需要一个包含有退回通知的邮件。返回的邮件会说：“您的邮件由于如下原因未能成功投递。～～”，它也会包含一个验证代码以及激活链接，这是用来关联那个无法访问的邮箱的。现在，验证代码可以用来验证和确认电子邮件地址的所权，这实际上破坏了验证的流程。同样的流程也适用于电子邮件的转发部分，我们发现它也是容易被攻击的。我们所需的就是一个无法接受到我们邮件的邮箱，就像上文提到的。

[![](https://p1.ssl.qhimg.com/t01832d6447245dbfa2.png)](https://p1.ssl.qhimg.com/t01832d6447245dbfa2.png)

上面的图片清晰的显示了Gmail发回了一个邮件，它包含关联无法访问邮箱的验证代码以及激活链接。

假设有这样一个场景，攻击者可以欺骗受害者停用他的邮箱账户，或者欺骗受害者关闭他的邮箱地址，这样受害者就收不到外部邮件了。一旦完成，攻击者可以通过Gmail包含验证码的电子邮件来劫持受害者邮箱，此外，转发部分的认证也会被攻击。

流程：

1.攻击者尝试获取xyz@gmail.com 的绑定权限

2.Google给xyz@gmail.com发送邮件来认证

3.xyz@gmail.com无法收到邮件，所以邮件被退回Google

4.谷歌给攻击者返回一个发送失败的通知，而在这个通知中，包含了验证码和验证链接

5.攻击者通过验证码或者链接取得xyz@gmail.com的所有权

有了权限之后，我可以使用它发送电子邮件，也可以作为一个别名使用。

<br>

**演示视频**





**<br>**

**时间轴**

10月20日—报告给谷歌

10月20日—收到确认

11月1日—报告发布

<br>

**写在最后**

令人悲哀的是，这样一个漏洞我们竟然没有得到报酬，但是Google认可我们的研究，并同意在漏洞名人堂上列出。

[https://bughunter.withgoogle.com/characterlist/23](https://bughunter.withgoogle.com/characterlist/23)

[https://bughunter.withgoogle.com/profile/c0f2a725-a6af-4f6d-af41-67bcbdbe37b2](https://bughunter.withgoogle.com/profile/c0f2a725-a6af-4f6d-af41-67bcbdbe37b2)
