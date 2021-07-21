> 原文链接: https://www.anquanke.com//post/id/204935 


# Squid中的内存泄漏和UAF漏洞详解


                                阅读量   
                                **266076**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者synacktiv，文章来源：synacktiv.com
                                <br>原文地址：[https://www.synacktiv.com/posts/exploit/memory-leak-and-use-after-free-in-squid.html](https://www.synacktiv.com/posts/exploit/memory-leak-and-use-after-free-in-squid.html)

译文仅供参考，具体内容表达以及含义原文为准

![](https://p1.ssl.qhimg.com/t013f535d4610db6f39.jpg)



几个月前，Synacktiv团队对开源项目Squid进行了安全评估。这篇博客文章描述了在审核期间发现的一些漏洞细节。



## CVE-2019-18679：摘要认证中的信息泄露

当配置为使用摘要式身份验证方案时，Squid会使用407 Proxy Authentication Required状态代码响应不包含Proxy-Authorization标头的请求。

![](https://p5.ssl.qhimg.com/t018f4e73818b33ce27.jpg)

在响应中包含一个Proxy-Authenticate-HTTP头，向客户端提供对其进行身份验证所需的信息。即使不看源代码，我们也能注意到生成的随机数有些奇怪。如果我们对它进行base64解码并将其打印为QWORDS，则会得到可疑的东西，这看起来像一个内存地址：

![](https://p0.ssl.qhimg.com/t0169b9d0df14e4e5c9.png)

让我们更仔细地看一下Squid中的摘要实现。此nonce由auth/Config.cc中定义的authenticatedigestnoncew函数生成。

![](https://p5.ssl.qhimg.com/t01254b633bb0252158.png)

在（1）处，我们可以注意到newnonce-&gt;noncedata.self包含newnonce对象的地址。

在生成之后，这个随机数对象由authenticatedigestnoncenoncenb64函数编码，然后包含在代理授权HTTP响应头中。

![](https://p2.ssl.qhimg.com/t011f4fbe536307c1f6.png)

该authenticateDigestNonceNonceb64()函数仅返回对象的键值。该nonce-&gt;key字符串在authDigestNonceEncode中进行初始化，且authDigestNonceEncode只对非数据结构执行base64编码，而不进行任何形式的哈希运算：

![](https://p4.ssl.qhimg.com/t0115565663c4af21f0.png)

由于_digest_nonce_data包含指向digest_nonce_h对象的指针，因此我们可以在Proxy-Authorization HTTP头部中获取它。

![](https://p5.ssl.qhimg.com/t0105453a23b9821b7b.png)

我们可以通过构造恰当的信息复杂度，在Squid的日志中进行检查。

![](https://p2.ssl.qhimg.com/t017ef9f82ca3c257a9.png)

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

这给了我们一个很好的机会来绕过ASLR。

在我们之前，另一位研究人员报告了此漏洞，并在2019年11月发布的Squid 4.9中修复该漏洞。

但是，修复方式有些奇怪，他们没有从__digest_nonce_data中删除digest_nonce_h指针，而是决定使用MD5对结构体进行哈希处理并将结果返回给用户。

![](https://p5.ssl.qhimg.com/t01a83eaa5477063005.png)

但是，如果攻击者想确定用于计算MD5摘要的每个组件的值，则有可能对MD5摘要执行脱机暴力攻击检索digest_nonce_h指针。<br>
让我们回顾一下这些组件。

creationtime是__digest_nonce_data中的第一个字段，它是用户已知的摘要对象创建的时间戳（以秒为单位）。

另一个要确定的字段是randomdata，由Mersenne Twister PRNG生成的uint32_t值。

![](https://p4.ssl.qhimg.com/t01be84c93249fac3d7.png)

当用当前时间戳（以秒为单位）生成第一个nonce时，是以PRNG作为种子的。因此，要确定randomdata，攻击者将需要知道：<br>
• Squid自启动以来处理的第一个请求的时间戳，<br>
• Squid自启动以来生成的随机数。<br>
但是，可以通过利用一个漏洞使Squid服务器崩溃，就可以确定这两个值，因为PRNG是在crash后的第一个请求当做种子植入的。

这将导致攻击者对MD5摘要进行暴力攻击以检索digest_nonce_h指针，从而绕过ASLR。

在x86_64Linux上，用户地址空间是从0到1&lt;&lt;47（0x80000000000）。由于digest_nonce_h对象的分配总是与0x10字节对齐，因此bruteforce的整个密钥空间大小是47-4=43位。考虑到现代密码破解机每秒可以计算2720亿MD5哈希，一次完整的暴力攻击大约需要30秒。

在Squid 4.10中对该漏洞进行了静默修补，把digest_nonce_h指针从结构体中删除。



## CVE-2020-11945：摘要验证中的UAF

所述的digest_nonce_h结构定义auth/digest/Config.h。

![](https://p4.ssl.qhimg.com/t01e12746d0a4ec0ae5.png)

由于客户端可能并行发送多个请求，nonce对象包含一个引用计数器。如今，使用有符号的16位整数存储引用计数器似乎相当危险，因为它可能会溢出，触发UAF漏洞。

让我们看看这里的情况是否如此。

通过查看代码，我们了解到该引用计数器的定义如下：

创建nonce对象时实例化为1，

当Squid接收到使用nonce的新请求时，它将增加1，

当请求完成时，即当基础的UserRequest对象被销毁时，它将递减1，

当nonce被视为过期时，它将递减1，这意味着：

o 随机数到期日期已到，

o 随机数被用来发送更多的请求，该请求超过了授权阈值（在nonce_max_count配置设置中设置），

o 随机数的使用方式存在问题，例如，随请求发送的随机数与前一个计数不匹配。

当计数器为0时，nonce对象被释放

因此，如果我们在serRequest对象进行垃圾回收之前执行了足够的请求使计数器溢出，则我们应该能够触发一个Use-After-Free漏洞。

### <a class="reference-link" name="%E8%A7%A6%E5%8F%91%E6%BC%8F%E6%B4%9E"></a>触发漏洞

首先，我们通过向Squid发送以下HTTP请求来生成新的随机数：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

在Squid的日志中，我们可以观察到随机数的创建（具有正确的信息复杂度）：

![](https://p1.ssl.qhimg.com/t012ffedb3115b3dd87.png)

然后，我们建立了大量的TCP会话。一旦所有这些都达到建立的状态，我们便开始构造HTTP请求：

• 他们的nonce是之前创建的

• 它们的参数“response”是十六进制中任意选择的128位字（用于身份验证失败）。

![](https://p4.ssl.qhimg.com/t019ac0ab160c83c9d8.png)

思路是是输入引用计数器增加但身份验证失败的代码片段，从而防止对象的“nonce count”增加。因此，使用此代码片段可以任意增加引用计数器触发整数溢出。

![](https://p2.ssl.qhimg.com/t01a81012ecc51e312e.png)

由于负责递减引用计数器authDigestNonceUnink的函数在值为负时不执行操作，因此我们只需要并行发送32768个请求。

![](https://p0.ssl.qhimg.com/t0139a311615f782282.png)

然后，我们可以使用单个请求将计数器一直增加到-1。

![](https://p0.ssl.qhimg.com/t01694a229dc340672f.png)

此时我们有一个nonce对象，其引用计数器为-1。为了实现UAF，我们需要两种请求：

• 一个可以控制生命周期nonce的请求A，

• 请求B，它将引用计数器增加到1，然后在完成后释放对象。

对于请求A，我们可以使用nonce成功地执行对受控制服务器请求的身份验证。然后，在服务器端，我们可以任意延迟响应，这将有效地防止Squid破坏关联的UserRequest对象。

对于请求B，不能使用用于增加引用计数器的相同类型的请求。实际上，当一个nonce对象在从缓存中删除之前就被删除（这基本上是有效nonce的列表），Squid会崩溃，并出现一个失败的断言。

![](https://p3.ssl.qhimg.com/t014b997b4e5160e777.png)

因此，我们需要authDigestNoncePurge在释放随机数对象之前调用该函数。

![](https://p5.ssl.qhimg.com/t01d9b71e77be6281d3.png)

通过跟踪调用authDigestNoncePurge的代码路径，我们可以找到两种从缓存中删除nonce的方法：

• 等待随机数到期，

• 通过使用无效的nonce计数（例如0）来使nonce无效。

第二个当然更方便，所以这就是我们要用的。

现在我们只需要：

执行2个请求A，将引用计数器递增为1

![](https://p2.ssl.qhimg.com/t01d58b1026e86a0266.png)

• 执行1个请求B，将计数器增加到2，然后将其从缓存中删除后，将其减少到1。

![](https://p0.ssl.qhimg.com/t0150fab953c2718878.png)

• 关闭请求A，将计数器减为0，从而释放随机数对象，

![](https://p0.ssl.qhimg.com/t015f3aa7fa5e9514ce.png)

遗憾的是，事情的发展并非如我们预期的那样。我们释放了nonce对象，但并没有执行 free函数。实际上，在Squid中的Digest实现中，digest_nonce_h对象被分配到名为MemPoolMalloc的分配池中。

要正确释放nonce分配，需要触发池中分配回收机制。在Squid的默认配置中，这可以通过分配和释放至少300个nonce对象（通过用任意nonce发送B请求）来完成。

![](https://p4.ssl.qhimg.com/t012bc090da01473aac.png)

此时，存在一个UserRequest对象，该对象具有指向之前digest_nonce_h的悬挂指针。当最后一个UserRequest被销毁时，将使用该悬挂指针调用authDigestNonceUnlink函数。

如果我们关闭最后一个请求，而不事先执行任何喷射操作，则很可能在自由执行期间中止程序。

![](https://p5.ssl.qhimg.com/t018e2786d074136a15.png)

总而言之，我们在启用了摘要身份验证模块的Squid4.8默上成功触发了UAF。但是，在发送有效身份验证之前，很难确保nonce计数的值为-1，因此不太可能在野外利用此漏洞。


