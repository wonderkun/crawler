> 原文链接: https://www.anquanke.com//post/id/104801 


# 通过Hooking Chrome浏览器的SSL函数实现读取SSL通信数据


                                阅读量   
                                **120427**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者NYTROSECURITY，文章来源：https://nytrosecurity.com/
                                <br>原文地址：[https://nytrosecurity.com/2018/02/26/hooking-chromes-ssl-functions/](https://nytrosecurity.com/2018/02/26/hooking-chromes-ssl-functions/)

译文仅供参考，具体内容表达以及含义原文为准

## [![](https://p0.ssl.qhimg.com/t01902ca2dc0af6fa44.jpg)](https://p0.ssl.qhimg.com/t01902ca2dc0af6fa44.jpg)

## 前言

NetRipper可以用来捕获加密/解密数据的函数，然后把它们通过网络发送出去。这对于Firefox这种能够找到PR_Read和PR_Write这两个DLL导出函数的应用来说是很容易的，但对于Google Chrome这种没有导出SSL_Read和SSL_Write函数的就要难一些了。

当我们要拦截这种调用时，面临的最大问题是我们无法快速地从庞大的chrome.dll文件中找到相应的函数。于是我们不得不手动地在二进制文件里查找。但我们该怎么做到呢？



## Chrome的源码

为了达到目的，最好的选择可能是从Chrome的源码开始。这是Chrome的源码：[https://cs.chromium.org/](https://cs.chromium.org/) 。有了源码，查找分析就方便多了。

我们注意到Chrome使用了OpenSSL的分支boringssl，它的源码在这里：[https://cs.chromium.org/chromium/src/third_party/boringssl/](https://cs.chromium.org/chromium/src/third_party/boringssl/) 。

接下来，我们要找到SSL_read和 SSL_write这两个函数，我们很快发现它们在[ssl_lib.cc](https://cs.chromium.org/chromium/src/third_party/boringssl/src/ssl/ssl_lib.cc)文件中。

这是SSL_read：

```
int SSL_read(SSL *ssl, void *buf, int num) `{`
 int ret = SSL_peek(ssl, buf, num);
 if (ret &lt;= 0) `{`
 return ret;
 `}`
 // TODO(davidben): In DTLS, should the rest of the record be discarded? DTLS
 // is not a stream. See https://crbug.com/boringssl/65.
 ssl-&gt;s3-&gt;pending_app_data =
 ssl-&gt;s3-&gt;pending_app_data.subspan(static_cast&lt;size_t&gt;(ret));
 if (ssl-&gt;s3-&gt;pending_app_data.empty()) `{`
 ssl-&gt;s3-&gt;read_buffer.DiscardConsumed();
 `}`
 return ret;
`}`
```

这是SSL_write：

```
int SSL_write(SSL *ssl, const void *buf, int num) `{`
 ssl_reset_error_state(ssl);

if (ssl-&gt;do_handshake == NULL) `{`
 OPENSSL_PUT_ERROR(SSL, SSL_R_UNINITIALIZED);
 return -1;
 `}`

if (ssl-&gt;s3-&gt;write_shutdown != ssl_shutdown_none) `{`
 OPENSSL_PUT_ERROR(SSL, SSL_R_PROTOCOL_IS_SHUTDOWN);
 return -1;
 `}`

int ret = 0;
 bool needs_handshake = false;
 do `{`
 // If necessary, complete the handshake implicitly.
 if (!ssl_can_write(ssl)) `{`
 ret = SSL_do_handshake(ssl);
 if (ret &lt; 0) `{`
 return ret;
 `}`
 if (ret == 0) `{`
 OPENSSL_PUT_ERROR(SSL, SSL_R_SSL_HANDSHAKE_FAILURE);
 return -1;
 `}`
 `}`

ret = ssl-&gt;method-&gt;write_app_data(ssl, &amp;needs_handshake,
 (const uint8_t *)buf, num);
 `}` while (needs_handshake);
 return ret;
`}`
```

为什么我们要看这些代码？原因很简单：在二进制文件中，我们可能找到在源码中也能找到的东西，例如字符串和特定的值。

事实上前阵子我就提到了接下来我要介绍的部分内容，可能是在[这篇文章](http://www.rohitab.com/discuss/topic/41729-google-chrome-ssl-write-hook-openssl/)。但为了让大家不仅能在Chrome中，而且在其他工具如Putty，WinSCP中也会查找函数，我将涵盖所有这些方面。



## SSL_write函数

虽然SSL_read函数没有提供有用的信息，但我们可以从SSL_write函数开始,然后可以发现信息：

```
OPENSSL_PUT_ERROR(SSL, SSL_R_UNINITIALIZED);
```

这是OPENSSL_PUT_ERROR宏：

```
// OPENSSL_PUT_ERROR is used by OpenSSL code to add an error to the error
// queue.
#define OPENSSL_PUT_ERROR(library, reason) 
 ERR_put_error(ERR_LIB_##library, 0, reason, __FILE__, __LINE__)
```

这些信息很有用：
- ERR_put_error是一个函数调用
- reason是第二个参数，SSL_R-UNINITIALIZED情况下值是226（0xE2）
- _**FILE_**是真实文件名，ssl_lib.cc的完整地址
- _**LINE_**是ssl_lib.cc文件中的当前行号
这些信息能帮我们找到SSL_write函数。为什么呢？
- 我们知道了它是一个函数调用，所以参数（如reason,_**FILE** and **LINE_**）会被放到栈中（x86）
- 我们知道了reason （0xE2）
- 我们知道了_**FILE_** （ssl_lib.cc）
- 我们知道了_**LINE_** （在这个版本是1060，即0x424）
但是如果用的是别的版本呢？行号可能完全不同。这种情况下，我们需要看一下Chrome是如何使用boringSSL的。

我们可以在这里找到不同版本的源码：[https://chromium.googlesource.com/chromium/src.git](https://chromium.googlesource.com/chromium/src.git) 。例如，我现在用的是Version 65.0.3325.181 (Official Build) (32-bit)这个版本。我们可以在这找到源码：[https://chromium.googlesource.com/chromium/src.git/+/65.0.3325.181](https://chromium.googlesource.com/chromium/src.git/+/65.0.3325.181) 。接下来，我们要找到boringSSL的代码，但它好像不在这里面。无论如何，我们可以找到[DEPS](https://chromium.googlesource.com/chromium/src.git/+/65.0.3325.181/DEPS)这个很有帮助的文件，然后得到一些信息：

```
vars = `{`
...
 'boringssl_git':
 'https://boringssl.googlesource.com',
 'boringssl_revision':
 '94cd196a80252c98e329e979870f2a462cc4f402',
```

现在我们知道了这个版本的Chrome通过[https://boringssl.googlesource.com](https://boringssl.googlesource.com) 来获取boringSSL，使用的是这个版本：94cd196a80252c98e329e979870f2a462cc4f402。根据这些信息，我们就可以在[这里](https://boringssl.googlesource.com/boringssl/+/94cd196a80252c98e329e979870f2a462cc4f402) 准确地得到boringSSL的代码，这是[ssl_lib.cc](https://boringssl.googlesource.com/boringssl/+/94cd196a80252c98e329e979870f2a462cc4f402/ssl/ssl_lib.cc)文件。

我们看一下接下来要怎么才能找到SSL_write函数：
1. 在chrome.dll的只读部分（.rdata）中搜索“ssl_lib.cc”文件名。
1. 得到完整路径然后搜索引用
1. 查找所有字符串引用，根据“reason”和行号变量找到正确的结果。


## SSL_read函数

要找到SSl_write函数并不难因为它有OPENSSL_PUT_ERROR,但SSL_read没有。我们来看看SSL_read是怎样运行的然后跟踪一下。

我们很容易发现它调用了SSL_peek：

```
int ret = SSL_peek(ssl, buf, num);
```

SSL_peek将会调用ssl_read_impl函数：

```
int SSL_peek(SSL *ssl, void *buf, int num) `{`
 int ret = ssl_read_impl(ssl);
 if (ret &lt;= 0) `{`
 return ret;
 `}`
...
`}`
```

这个ssl_read_impl函数好像能提供一些有用的信息：

```
static int ssl_read_impl(SSL *ssl) `{`
 ssl_reset_error_state(ssl);

if (ssl-&gt;do_handshake == NULL) `{`
 OPENSSL_PUT_ERROR(SSL, SSL_R_UNINITIALIZED);
 return -1;
 `}`
...
`}`
```

通过搜索发现ssl_read_impl只被调用了两次，分别是SSL_peek函数和SSL_shutdown函数，于是找到SSL_peek函数就很容易了。找到SSL_peek函数后，SSL_read函数就在眼前了。



## 32位Chrome

现在我们知道怎么查找函数了，那么找到它们吧。

接下来我将会使用[x64dbg](https://x64dbg.com/)，但你也可以用别的工具。我们需要找到”Memory”标签然后查找chrome.dll。我们需要先做两件事：
- 在反汇编工具里打开代码区域，右击“.text”，然后选择“Follow in Disassembler”
- 打开dump窗口下的只读数据区域，右击“.rdata”，然后选择“Follow in Dump”
现在可以在dump窗口看到“ssl_lib.cc”字符串了，在窗口内右击，选择“Find Pattern”然后搜索ASCII字符串。可以看到一个搜索结果，双击它然后返回直到找到ssl_lib.cc的完整路径。右击路径的第一个字节，如下图所示，选择“Find References”，看看它在哪被调用了（OPENSSL_PUT_ERROR函数调用）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01921717a69268f22e.jpg)

看起来好像有多个引用，但我们可以一个一个找。结果如下图：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0143044efc22d2651c.jpg)

我们看看最后一个，看看它是怎样的：

```
6D44325C | 68 AD 03 00 00 | push 3AD |
6D443261 | 68 24 24 E9 6D | push chrome.6DE92424 | 6DE92424:"../../third_party/boringssl/src/ssl/ssl_lib.cc"
6D443266 | 6A 44          | push 44 |
6D443268 | 6A 00          | push 0 |
6D44326A | 6A 10          | push 10 |
6D44326C | E8 27 A7 00 FF | call chrome.6C44D998 |
6D443271 | 83 C4 14       | add esp,14 |

```

看起来和我们想象的一样，是一个有五个参数的函数调用。你可能知道参数在栈上是从右往左的，我们看下面：
1. push 3AD – 行号
1. push chrome.6DE92424 – 字符串，文件路径
1. push 44 – reason
1. push 0 – 一直是0的参数
1. push 10 – 第一个参数
1. call chrome.6C44D998 – 调用 ERR_put_error函数
1. add esp,14 – 清除栈
0x3AD表示行号是941，它在”ssl_do_post_handshake”内，所以我们不需要它。



### <a class="reference-link" name="SSL_write"></a>SSL_write

SSL_write函数在第1056（0x420）行和第1061（0x425）行调用了这个函数，所以我们需要在开始时通过push 420或者push 425来找到调用。通过结果我们只需要几秒就能找到它：

```
6BBA52D0 | 68 25 04 00 00 | push 425 |
6BBA52D5 | 68 24 24 E9 6D | push chrome.6DE92424 | 6DE92424:"../../third_party/boringssl/src/ssl/ssl_lib.cc"
6BBA52DA | 68 C2 00 00 00 | push C2 |
6BBA52DF | EB 0F          | jmp chrome.6BBA52F0 |
6BBA52E1 | 68 20 04 00 00 | push 420 |
6BBA52E6 | 68 24 24 E9 6D | push chrome.6DE92424 | 6DE92424:"../../third_party/boringssl/src/ssl/ssl_lib.cc"
6BBA52EB | 68 E2 00 00 00 | push E2 |
6BBA52F0 | 6A 00          | push 0 |
6BBA52F2 | 6A 10          | push 10 |
6BBA52F4 | E8 9F 86 8A 00 | call chrome.6C44D998 |
```

在这里我们看到都是函数调用，但是只提到第一个是优化了的。现在我们只需要返回直到找到类似函数开头的东西。虽然这可能不是其他函数的情况，但在我们的情况下是这样的，我们很容易通过经典函数序言找到它：

```
6BBA5291 | 55    | push ebp |
6BBA5292 | 89 E5 | mov ebp,esp |
6BBA5294 | 53    | push ebx |
6BBA5295 | 57    | push edi |
6BBA5296 | 56    | push esi |

```

在6BBA5291处设置一个断点，看看当我们用Chrome浏览一些HTTPS网站（为避免一些问题，不要浏览SPDY或HTTP/2.0的网站）时会发生什么。

下面是一个看看断点触发时我们可以从栈顶得到什么的例子：

```
06DEF274 6A0651E8 return to chrome.6A0651E8 from chrome.6A065291
06DEF278 0D48C9C0 ; First parameter of SSL_write (pointer to SSL)
06DEF27C 0B3C61F8 ; Second parameter, the payload
06DEF280 0000051C ; Third parameter, payload size
```

如果你右击第二个参数，然后选择“Follow DWORD in Dump”, 你应该可以看到类似下面的数据：

```
0B3C61F8 50 4F 53 54 20 2F 61 68 2F 61 6A 61 78 2F 72 65 POST /ah/ajax/re 
0B3C6208 63 6F 72 64 2D 69 6D 70 72 65 73 73 69 6F 6E 73 cord-impressions 
0B3C6218 3F 63 34 69 3D 65 50 6D 5F 66 48 70 72 78 64 48 ?c4i=ePm_fHprxdH
```



### <a class="reference-link" name="SSL_read"></a>SSL_read

现在来找SSL_read函数。我们发现来自一个来自ssl_read_implh函数对“OPENSSL_PUT_ERROR”的调用。这个调用发生在第962（0x3C2）行。我们再看下结果然后找到它，如下：

```
6B902FAC | 68 C2 03 00 00 | push 3C2 |
6B902FB1 | 68 24 24 35 6C | push chrome.6C352424 | 6C352424:"../../third_party/boringssl/src/ssl/ssl_lib.cc"
6B902FB6 | 68 E2 00 00 00 | push E2 |
6B902FBB | 6A 00          | push 0 |
6B902FBD | 6A 10          | push 10 |
6B902FBF | E8 D4 A9 00 FF | call chrome.6A90D998 |
```

现在我们应该很容易地找到函数的开始了。右击第一个指令（push EBP），转到“Find references”，然后“Selected Address(es)”。

[![](https://p0.ssl.qhimg.com/t012a76055a419803eb.jpg)](https://p0.ssl.qhimg.com/t012a76055a419803eb.jpg)

我们可以发现只有一个对函数的调用，而且应该是SSL_peek。找到SSL_peek的第一条指令然后重复同样的操作。我们只得到来自SSL_read对SSL_peek的调用这个结果。所以我们找到了。

```
6A065F52 | 55             | push ebp | ; SSL_read function
6A065F53 | 89 E5          | mov ebp,esp |
...
6A065F60 | 57             | push edi |
6A065F61 | E8 35 00 00 00 | call chrome.6A065F9B | ; Call SSL_peek
```

我们来设置一个断点，一个正常的调用我们可以看到下面的信息：

```
06DEF338 6A065D8F return to chrome.6A065D8F from chrome.6A065F52
06DEF33C 0AF39EA0 ; First parameter of SSL_read, pointer to SSL
06DEF340 0D4D5880 ; Second parameter, the payload
06DEF344 00001000 ; Third parameter, payload length
```

接下来右击第二个参数然后选择“Follow DWORD in Dump”，接着按“Execute til return”按钮。这时在dump窗口应该可以看到一些纯文本数据：

```
0D4D5880 48 54 54 50 2F 31 2E 31 20 32 30 30 20 4F 4B 0D HTTP/1.1 200 OK. 
0D4D5890 0A 43 6F 6E 74 65 6E 74 2D 54 79 70 65 3A 20 69 .Content-Type: i 
0D4D58A0 6D 61 67 65 2F 67 69 66 0D 0A 54 72 61 6E 73 66 mage/gif..Transf
```

所以我们同样成功地找到了。



## 结论

刚开始看起来可能觉得很难，但你也看到了，其实我们只要跟着源码走，还是很容易。这个方法应该适用于大多数开源应用。

x64版本应该是非常相似的，唯一的区别可能是汇编代码，这里我们不详细讲。

最后，请记住这种方法可能导致应用不稳定甚至可能奔溃。
