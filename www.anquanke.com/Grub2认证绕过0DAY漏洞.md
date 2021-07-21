> 原文链接: https://www.anquanke.com//post/id/83131 


# Grub2认证绕过0DAY漏洞


                                阅读量   
                                **95643**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://hmarco.org/bugs/CVE-2015-8370-Grub2-authentication-bypass.html](http://hmarco.org/bugs/CVE-2015-8370-Grub2-authentication-bypass.html)

译文仅供参考，具体内容表达以及含义原文为准

**内容:**

**1.描述。**

**2.影响。**

**3.关于该漏洞。**

**4.利用(POC)。**

**5.APT如何利用这个0-day。**

**6.修复。**

**7.讨论。**

 描述:

在Grub2上发现一枚0day漏洞。版本从1.98(十二月,2009)到2.02(十二月,2015)受到影响。该漏洞可以在某些情况下被利用,允许本地攻击者绕过任何认证(明文密码或Hash)。因此,攻击者可以控制计算机。

grub2是大多数Linux系统使用的一种常用嵌入式系统使用的引导程序。这一漏洞可造成数不胜数的设备受到影响。<br> 如图所示,在Debain 7.5 中我们成功的利用了该漏洞,在qemu下成功get shell。



我是否会受到影响?<br>

你应当赶紧检查你的系统是否存在该漏洞,当Grub访问你的用户名的时候,按退格键28次。如果你的设备重新启动或者你能够get shell,那么你的设备以及被感染了。<br>



影响:<br>

攻击者成功利用此漏洞可以获得一个Grub的rescue shell,Grub的rescue shell是一个非常高权限的shell,有如下权限:<br>

权限的提升:攻击者在不知道有效用户名和密码的情况下进行身份验证。攻击者已经全面进入GRUB“控制台”(grub rescue)。<br>

信息披露:攻击者可以加载特定的内核以及initramfs(例如USB),然后在一个更舒适的环境,将整盘复制或者安装一个rootkit。<br>

拒绝服务攻击:攻击者可以破坏任何数据包括grub本身。即使在这种情况下,磁盘加密,攻击者仍然可以覆盖它,处罚DOS。



关于该漏洞:<br>

故障(bug)发生在GRUB代码1.98以后的版本(十二月,2009)。由提交记录b391bdb2f2c5ccf29da66cecdbfb7566656a704d引入,影响grub_password_get()函数。<br>

有两个函数都受到同一个整数下溢漏洞影响。grub_username_get()和grub_password_get()分别位于grub-core/normal/auth.c 以及 lib/crypto.c 。除了grub_username_get()调用了函数printf()以外，这两个函数基本是一样的。这里描述的PoC是基于grub_username_get()来get shell的。<br>

下面是grub_username_get()功能:



```
static int
grub_username_get (char buf[], unsigned buf_size)
`{`
  unsigned cur_len = 0;
  int key;
  while (1)
    `{`
      key = grub_getkey ();
      if (key == 'n' || key == 'r')
        break;
      if (key == 'e')
        `{`
          cur_len = 0;
          break;
        `}`
      if (key == 'b')  // Does not checks underflows !!
        `{`
          cur_len--; // Integer underflow !!
          grub_printf ("b");
          continue;
        `}`
      if (!grub_isprint (key))
        continue;
      if (cur_len + 2 &lt; buf_size)
        `{`
          buf[cur_len++] = key; // Off-by-two !!
          grub_printf ("%c", key);
        `}`
    `}`
  grub_memset( buf + cur_len, 0, buf_size - cur_len); // Out of bounds overwrite
  grub_xputs ("n");
  grub_refresh ();
  return (key != 'e');
`}`
```

故障是由于 cur_len 变量递减没有检查范围造成的。



利用(POC)

利用integer underflow可以导致off-by-two 或越界写的漏洞。前一个漏洞会覆盖用户名 buf以下的两个字节(grub_auth_check_authentication()中的局部变量local),但这部分内存没有任何有用的信息可以用来实施攻击，事实上这里只是内存对齐的padding。

后一个是一个越界写,这个很有趣,因为它允许在下面的用户名缓冲区以下写零。这是因为grub_memset()函数试图将所有的未使用的用户名缓冲区设置为零。代码需要计算第一个未使用的字节的地址和需要置0的缓冲区的长度。这些计算的结果作为grub_memset()的函数参数传递:

```
grub_memset (buf + cur_len, 0, buf_size - cur_len);
```

例如,用户缓冲区,键入“root”作为用户名,cur_len为5,以及grub_memset()函数清除(设置为0)字节从5到1024-5(用户名和密码的缓冲区1024字节)的内存。这种编程方式是相当的健壮的。例如,如果输入的用户名被存储在一个干净的1024字节数组中,那么我们可以将整个1024个字节和有效的用户名进行比较,而不是比较两个字符串。这可以防止一些侧信道攻击,比如时间差攻击。

滥用出界改写,攻击者可以按退格键来下溢cur_len变量,产生很大的值。这个值是用来计算起始地址的。

**memset destination address = **buf + cur_len

在这一点上,出现了一个二次溢出,该值与用户名缓冲区所在的基地址的增加的值无法完整保存在一个32位变量中。因此,我们需要实现的第一个下溢和第二个上溢出来计算目标地址,grub_memset()函数将开始设置为零缓冲:



```
cur_len--; // Integer Underflow
grub_memset (buf + cur_len, 0, buf_size - cur_len);// Integer Overflow
```

下面的例子有助于理解我们如何利用这个。假设用户缓冲区位于地址0x7f674,攻击者按一次退格键（cur_len 下溢变成0xFFFFFFFF）计算结果就是：

```
grub_memset(0x7f673,0,1025);
```

第一个参数是: (buf+cur_len) = (0x7f674+0xFFFFFFFF) = (0x7f674-1) = 0x7f673,第二个参数:用于填充内存的常量，在这里是0,和第三个参数是填充的字节数:(buf_size-cur_len)=(1024 -(- 1))= 1025。因此,整个用户名缓冲区(1024)加上缓冲区下的第一个字节将被设置为零。

因此,退格键的数目(不引入任何用户名),就是用户名缓冲区以下会被置0的字节数目。

现在,我们能够覆盖在用户名以下的任意数量的字节,我们需要找到一个合适的内存地址,我们可以用零覆盖。看看当前栈帧显，我们可以覆盖函数grub_memset()函数的返回地址。下面的图片草图勾画了堆栈内存布局:

[![](https://p0.ssl.qhimg.com/t01605cd3b0eeccf19e.png)](https://p0.ssl.qhimg.com/t01605cd3b0eeccf19e.png)

grub2:重定向控制流

如上图所示,该grub_memset()函数的返回地址是从用户名缓冲区以下16字节开始的。换句话说,如果我们按退格键17次,我们将覆盖返回地址的高字节。如此一来，函数就会返回到0x00eb53e8，而不是0x07eb53e8。当grub_memset()结束,控制流重定向到的0x00eb53e8地址会导致重启。同样的,如果我们按退格键18、19或20次,在所有的情况下重新启动系统。

这样一来,我们就能够重定向控制流。

我们将能跳往的代码做一个详细分析:0x00eb53e8,0x000053e8和0x000000e8,因为他们跳至代码重新启动计算机,是没有办法控制的执行流程。

尽管它似乎很难建立一个成功的攻击,只是跳到0x0。我们将展示如何实现这个。

跳到0x0会有什么东西吗？

地址0x0属于处理器的IVT(中断向量表)。它包含了各种各样的指针的形式段:偏移量。

[![](https://p0.ssl.qhimg.com/t01e6f592201ba7b919.png)](https://p0.ssl.qhimg.com/t01e6f592201ba7b919.png)

在这个启动顺序的早期阶段,处理器和执行框架不具备完全的功能。下一步的执行环境的一个规则的过程是主要的差异:

<br>

l处理器处于“保护模式”。grub2在开始的时候启用该种模式。

l未启用虚拟内存。

l无内存保护。内存是可读/写/执行。没有NX/DEP。

l处理器执行32位指令集,即使在64位架构中。

l自修改代码是由处理器自动处理的:“如果“写”影响了一个预取指令,指令队列是无效的。”

l没有堆栈溢出保护(SSP)。

l没有地址空间布局随机化(ASLR)。

<br>

因此,跳到0x0本身并不会陷入陷阱,但我们需要控制执行流到达目标函数,grub_rescue_run()，其中就包含了Grub2 Rescue Shell的主循环。

当跳到0x0的时候那些是我们可控的？

[![](https://p4.ssl.qhimg.com/t011565e2ed6b28b8a2.png)](https://p4.ssl.qhimg.com/t011565e2ed6b28b8a2.png)

grub_username_get() 的主“while”循环结束时,用户点击任一[回车]或[退出]键。寄存器%ebx会包含上次输入的健的值(或0x8 0XD，分别表示enter或esc的 ASCII码)。寄存器%esi持有的cur_len变量的值。<br>

 指令指针指向0x0地址。% ESI寄存器包含值28(按28次退格键),然后点[回车](%ebx = = 0xb)。



IVT逆向<br>

如果处理器的状态是一个总结上表,在IVT的代码实现类似memcpy(),复制0x%esi到0x0所指的地址0x0 %esi(到它自己)。因此,IVT是自修改代码,我们可以选择我们要复制的代码块。<br>

下列顺序显示的代码序列实际执行寄存器%esi的值—28(0xffffffe4):

[![](https://p0.ssl.qhimg.com/t012a3e75f500e47fdb.png)](https://p0.ssl.qhimg.com/t012a3e75f500e47fdb.png)



 ———-

[![](https://p5.ssl.qhimg.com/t0186d38e740310f6a9.png)](https://p5.ssl.qhimg.com/t0186d38e740310f6a9.png)

在第三次迭代中,生成的代码在0x0007包含一个retw指令。通过%ESP指针的值是0xe00c。所以,当retw指令执行,执行流程跳转到0xe00c。这个地址属于功能grub_rescue_run():<br>

[![](https://p3.ssl.qhimg.com/t0164ec0d76292582cb.png)](https://p3.ssl.qhimg.com/t0164ec0d76292582cb.png)

    在这一点上,GRUB2是在 grub rescue函数,这是一个强大的shell。<br>

[![](https://p2.ssl.qhimg.com/t01bcd5acbc6a6a11b5.png)](https://p2.ssl.qhimg.com/t01bcd5acbc6a6a11b5.png)

幸运的是,内存受到了轻微的修改,它可以使用所有GRUB的功能。只是,第一中断IVT的载体已被修改,因为现在的处理器处于保护模式下,IVT不再被使用。



继续深入<br>

虽然我们到达GRUB2 rescue功能函数,我们并不能真正的得到认证。如果我们回到“normal”的模式,这种模式是Grub菜单和完整的编辑功能,GRUB将申请一个有效的用户名和密码。所以,我们可以直接键入grub2的命令,甚至包括新的模块来添加新的 GRUB功能,部署恶意软件到系统中或从Linux上运行一个完整的bash shell启动一个更舒适自由的环境。在Linux中运行bash,我们可以使用grub2的命令如Linux,initrd或者insmod。<br>

虽然使用grub2的命令来运行一个Linux内核部署恶意软件是完全可能的,我们发现,一个简单的解决方案是修补RAM中GRUB2的代码,从而总是认证然后回到“normal”模式。这样的想法,是修改条件检用户是否已经通过身份验证或者没有没有通过。这个功能是grub-core/normal/auth.c文件中的_authenticated()函数。

[![](https://p1.ssl.qhimg.com/t01708a61466c3da09d.png)](https://p1.ssl.qhimg.com/t01708a61466c3da09d.png)

我们的目标是用nop指令覆盖条件。<br>

这种修改是通过使用GRUB2 rescue 命令write_word。然后,一切都准备好了回到grub2的正常模式。换句话说,我们可以进入“编辑模式”并且grub2不会询问用户或密码。

[![](https://p3.ssl.qhimg.com/t012a09b2295be3ffbf.png)](https://p3.ssl.qhimg.com/t012a09b2295be3ffbf.png)

APT如何利用这个0-day?<br>

物理访问是一个“进阶”的特征,归结到系统(或内部)。一个APT的主要目标是窃取敏感信息或者成为网络间谍。下面只是一个很简单的例子,一个APT可以感染系统并能够持久后方窃取用户数据。以下总结了系统配置:<br>

BIOS和UEFI有密码保护。<br>

GRUB2编辑模式受到密码保护。<br>

外部禁用:光盘,DVD,USB,网络引导,PXE…<br>

用户数据加密(本地)。

[![](https://p5.ssl.qhimg.com/t0181119133cfced055.png)](https://p5.ssl.qhimg.com/t0181119133cfced055.png)

<br>

        引导系统概述。

正如前面所述,我们的目标是窃取用户的数据。由于数据是加密的,我们所使用的策略是感染系统并等待用户解密数据(通过登录系统),然后直接获取信息。

<br>

配置使用恶意软件的环境

通过如前面所示的修复GRUB2,我们可以很容易地编辑linux项来加载Linux内核并得到一个root shell。这是一个古老的但仍然可用的把戏,仅仅通过加init=/bin/bash到linux项,我们就能得到一个root Linux shell,从而得到一个更好用的环境来部署我们的恶意软件。

[![](https://p0.ssl.qhimg.com/t010b9d42a9e8d21b3c.png)](https://p0.ssl.qhimg.com/t010b9d42a9e8d21b3c.png)

请注意,由于/bin/bash是运行的第一道进程,系统日志监护程序没有运行,因此,日志不会被记录。也就是说,该访问将不能被普通的Linux监测程序检测到。

部署恶意软件并获取持续性

为了显示你可以通过利用这种0-Day Grub2漏洞做多少事情,我们已经开发出一个简单的PoC。该PoC是一种改进的Firefox库,它可以创建新的进程,并在53端口对一个控制服务器运行一个逆向shell。显然,这只是一个简单的例子,实际的恶意软件将更加隐秘地获取信息。

修改后的库上传到[virustotal](https://www.virustotal.com/),其中报告55个工具中0 infections/virus 。 Firefox是使用Internet的web浏览器,并且向HTTP和DNS端口发送请求,所以它并不会提防我们使用这些端口与恶意软件通信。

为了感染系统,我们简单地把我们的修改版的libplc4.so库插入USB,然后替换原来的版本。我们必须安装具有写权限的系统并安装USB,如下图所示:

[![](https://p1.ssl.qhimg.com/t01e52feb8a8cf4e9c4.png)](https://p1.ssl.qhimg.com/t01e52feb8a8cf4e9c4.png)

当任何用户执行Firefox浏览器,一个逆向shell将被调用。此时用户的所有数据会被解密,使我们能够窃取任何种类的用户信息。下面的图片显示了用户Bob(目标用户)使用Firefox,而用户Alice(攻击者)如何完全获取到Bob的数据。

[![](https://p0.ssl.qhimg.com/t01cade5eac912b178e.png)](https://p0.ssl.qhimg.com/t01cade5eac912b178e.png)

要完成持续性的部分,值得一提的是使用驻留在/ boot分区的,且默认情况下是不加密的一个简单内核的修改版本,我们就可以提权部署一个更持久的恶意软件。只有你想不到的没有做不到的。

<br>

修复

该漏洞通过阻止cur_len溢出就很容易修复。主要的厂商都已经意识到了这个漏洞。顺便说一句,我们已经在主要的GRUB2 Git库创建了下面的“紧急补丁”:



```
From 88c9657960a6c5d3673a25c266781e876c181add Mon Sep 17 00:00:00 2001
From: Hector Marco-Gisbert &lt;hecmargi@upv.es&gt;
Date: Fri, 13 Nov 2015 16:21:09 +0100
Subject: [PATCH] Fix security issue when reading username and password
  This patch fixes two integer underflows at:
    * grub-core/lib/crypto.c
    * grub-core/normal/auth.c
Signed-off-by: Hector Marco-Gisbert &lt;hecmargi@upv.es&gt;
Signed-off-by: Ismael Ripoll-Ripoll &lt;iripoll@disca.upv.es&gt;
---
 grub-core/lib/crypto.c  | 2 +-
 grub-core/normal/auth.c | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
diff --git a/grub-core/lib/crypto.c b/grub-core/lib/crypto.c
index 010e550..524a3d8 100644
--- a/grub-core/lib/crypto.c
+++ b/grub-core/lib/crypto.c
@@ -468,7 +468,7 @@ grub_password_get (char buf[], unsigned buf_size)
      break;
    `}`
-      if (key == 'b')
+      if (key == 'b' &amp;&amp; cur_len)
    `{`
      cur_len--;
      continue;
diff --git a/grub-core/normal/auth.c b/grub-core/normal/auth.c
index c6bd96e..5782ec5 100644
--- a/grub-core/normal/auth.c
+++ b/grub-core/normal/auth.c
@@ -172,7 +172,7 @@ grub_username_get (char buf[], unsigned buf_size)
      break;
    `}`
-      if (key == 'b')
+      if (key == 'b' &amp;&amp; cur_len)
    `{`
      cur_len--;
      grub_printf ("b");
--
1.9.1
```

修复GRUB 2.02:



```
$ git clone git://git.savannah.gnu.org/grub.git grub.git
$ cdgrub.git
$ wget http://hmarco.org/bugs/patches/0001-Fix-CVE-2015-8370-Grub2-user-pass-vulnerability.patch
$ git apply 0001-Fix-CVE-2015-8370-Grub2-user-pass-vulnerability.patch
```



讨论

此漏洞的利用已经成功了,因为我们关于这个bug的所有组成部分做了非常深入的分析。可以看出,成功的利用取决于很多因素:BIOS版本,GRUB版本,RAM容量,还有内存布局的修改。而且每个系统都需要深入的分析来构建特定的漏洞。

还有,我们没有使用的是:grub_memset()函数可以被滥用,从而将存储块设置为零而且不跳到0x0,且用户名和密码缓冲器可以用于存储有效载荷。

此外,在更复杂的攻击下(那些需要更大的有效载荷),使用键盘仿真装置将非常有用,例如[Teensy device](https://www.pjrc.com/teensy/)。我们可以记录攻击序列所按下的键,并在目标系统上重播它们。

幸运的是,这里介绍的利用GRUB2漏洞的方法是不通用的,但也有其他的替代可以为你所用。在这里我们只介绍一种适合我们的。
