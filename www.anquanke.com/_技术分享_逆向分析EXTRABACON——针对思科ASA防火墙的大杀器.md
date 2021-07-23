> 原文链接: https://www.anquanke.com//post/id/84596 


# 【技术分享】逆向分析EXTRABACON——针对思科ASA防火墙的大杀器


                                阅读量   
                                **104956**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://zerosum0x0.blogspot.jp/2016/09/reverse-engineering-cisco-asa-for.html](http://zerosum0x0.blogspot.jp/2016/09/reverse-engineering-cisco-asa-for.html)

译文仅供参考，具体内容表达以及含义原文为准

**背景知识**

2016年8月13日，一个名为“The Shadow Brokers”（影子经纪人）的黑客组织声称自己入侵了Equation Group（方程式组织）的计算机系统，并成功窃取到了大量的机密信息以及黑客工具。随后，“The Shadow Brokers”黑客组织将大部分泄漏文件（60%）公布在了网上，其中就包含有针对多款网络设备的漏洞利用代码。根据卡巴斯基实验室在去年发布的安全公告，方程式组织是一个高度复杂的黑客组织，而该组织被认为是美国国家安全局的一个下属部门。

**安全研究专家在对泄漏文件的内容进行了分析之后，发现了一个针对思科ASA防火墙设备的远程代码执行漏洞（一个0 day漏洞）。方程式组织将针对该漏洞的漏洞利用工具命名为了“EXTRABACON”。**需要注意的是，目前很多企业或组织都将思科ASA防火墙作为了他们网络系统的主防火墙，所以EXTRABACON的出现也引起了业内的广泛关注。

**<br>**

**关于EXTRABACON**

**思科ASA系列防火墙，思科PIX防火墙，以及思科防火墙服务模块的SNMP代码中存在一个缓冲区溢出漏洞，而在EXTRABACON的帮助下，攻击者就可以利用这个漏洞来对目标设备发动攻击。**感兴趣的用户可以访问思科公司所发布的安全公告来了解受此漏洞（CVE-2016-6366）影响的完整设备名单。

下面这张图片大致描述了该漏洞的利用过程：

[![](https://p5.ssl.qhimg.com/t0129a55867ba351919.png)](https://p5.ssl.qhimg.com/t0129a55867ba351919.png)

** 关于EXTRABACON模块的一些信息：**

1.     用于接收SNMP数据包的接口必须配置并启用SNMP协议。在上图所显示的实例中，SNMP协议只在思科ASA防火墙的管理接口中启用了。随后，攻击者必须利用这个网络接口来发动攻击，因为其他的接口（无论是外部接口还是内部接口）是无法触发这个漏洞的。

2.     如果想要成功利用这个漏洞，那么攻击者必须要知道SNMP社区字符串。

3.     只有直接发送至目标系统的网络流量才能用来触发这个漏洞。

4.     这个漏洞只能通过IPv4流量来触发。

5.     SNMP v1，SNMP v2c，以及SNMP v3都会受到该漏洞的影响。

6.     攻击者可以利用这个漏洞来在目标设备中实现任意代码执行，获取目标系统的完整控制权，甚至是重载受影响的系统。

7.     思科ASA系列防火墙软件都会受到该漏洞影响。

<br>

**EXTRABACON的运行机制**

首先，我们需要了解一下EXTRABACON的运行机制，弄清楚这个漏洞是如何被利用的。

**这个远程漏洞利用工具可以通过向ASA设备发送一个精心设计的SNMP数据包来引起栈缓冲区溢出。**安全研究专家认为，如果SNMP数据包来自内部网络的话，将可以直接攻击默认配置的ASA防火墙，而来自外部网络的数据包在某些情况下也可以成功攻击设备。

<br>

**劫持的执行**

如果要利用32位环境下的x86缓冲区溢出漏洞，首先就是控制EIP（指令指针）寄存器。在x86架构下，CALL指令会将当前的EIP地址压入栈中，然后RET指令会将该值弹出栈，并跳转到该地址。由于我们已经引起了栈溢出，我们就可以根据自己的需要来修改返回地址了。

在shellcode_asa843.py文件中，我们可以看到如下信息：



```
my_ret_addr_len = 4
my_ret_addr_byte = "xc8x26xa0x09"
my_ret_addr_snmp = "200.38.160.9"
```

这是ASA 8.4(3)版本中的一个偏移量-0x09a026c8。这是一个典型的栈缓冲区溢出漏洞利用，我的直觉告诉我，我应该可以重写RET地址，而这里应该有一个JMP ESP地址（跳转到栈指针）。果然，我的直觉没错：

[![](https://p0.ssl.qhimg.com/t01c32ebee1af508961.png)](https://p0.ssl.qhimg.com/t01c32ebee1af508961.png)

存在漏洞的文件为“lina”，这是一个ELF文件，当你可以使用“objdump”的时候，你还需要IDA吗？

**<br>**

**第一阶段：“Finder”**

方程式组织的shellcode在攻击时主要分成三个步骤。当我们跳转到JMP ESP地址之后，我们将会在“finder”shellcode中找到我们的指令指针。

finder_len = 9

finder_byte = "x8bx7cx24x14x8bx07xffxe0x90"

finder_snmp = "139.124.36.20.139.7.255.224.144"

这段代码可以在栈中找到指令指针，并且跳转到目标地址。指针中包含有攻击的第二步操作代码地址。

[![](https://p0.ssl.qhimg.com/t01c51a4165c7dcea2c.png)](https://p0.ssl.qhimg.com/t01c51a4165c7dcea2c.png)

我们并不打算对其进行深入地调查分析，因为似乎ASA防火墙每个版本都使用的是相同的固定偏移量。

**<br>**

**第二阶段：“Preamble”**

在对Python源码进行了分析之后，我们找出了负责第二阶段攻击的代码：



```
wrapper = sc.preamble_snmp
if self.params.msg:
    wrapper += "." + sc.successmsg_snmp
wrapper += "." + sc.launcher_snmp
wrapper += "." + sc.postscript_snmp
```

我们可以暂时忽略successmsg_snmp，先看看下面这段代码：

[![](https://p2.ssl.qhimg.com/t01bb47a0ca471c0f0c.png)](https://p2.ssl.qhimg.com/t01bb47a0ca471c0f0c.png)

虽然一眼看过去这段代码似乎进行了很多操作，但实际上这些都是很简单的操作。

1.     用0xa5a5a5a5来对一个“安全”返回地址进行了异或运算。实际上这是没有任何必要的，因为这种类型的异或运算到处都是，而且shellcode中可以还包含空字节数据。

2.     修复了EBP寄存器中的堆溢出问题。

3.     保存修复后的寄存器（PUSHA＝push all）

4.     栈中保存有指向攻击第三阶段的payload指针。

5.     调用payload，然后返回。

6.     恢复之前所保存的寄存器状态（POPA＝pop all）

7.     shellcode返回“安全”地址，仿佛一切都没有发生过。

在我们“安全”返回之前，代码会调用一个函数。在对这个函数进行了分析之后，我们就可以找到寄存器被清空的原因了。

[![](https://p1.ssl.qhimg.com/t01c445a3e7a2e9bccb.png)](https://p1.ssl.qhimg.com/t01c445a3e7a2e9bccb.png)

这些寄存器都被“栈溢出”给破坏了，如果我们不修复寄存器的值，程序将会崩溃。

**<br>**

**第三阶段：“Payload”**

攻击的第三阶段才是最神奇的地方。Shellcode也的确完成了它该做的事，即生成shell，而且方程式组织的黑客也非常聪明。**我们修改了两个函数－pmcheck()和admauth()，让它们的返回值永远为“true”。这样一来，我们就可以在不知道密码的情况下登陆ASA管理员账户了。**

在攻击的第三阶段中，涉及到了两个payload：payload_PMCHECK_DISABLE_byte和payload_AAAADMINAUTH_DISABLE_byte。这两个shellcode执行的是相同的功能，只是各自的偏移量不同，而且两者有很多代码重用的部分。

方程式组织的PMCHECK_DISABLE shellcode如下:

[![](https://p3.ssl.qhimg.com/t01633de99e8c200343.png)](https://p3.ssl.qhimg.com/t01633de99e8c200343.png)

其执行步骤如下：

1.     首先，系统调用mprotect()函数之后，会将内存页面标记为read、write、或者exec。

2.     接下来，让我们把目光放到这段代码的底部。Shellcode的最后三行表示“总是返回true”。

3.     调用指令会将当前地址压入栈中。

4.     修复代码的地址会被存入esi寄存器中。

5.     rep指令会将esi寄存器中的四字节信息（ecx寄存器）拷贝到edi寄存器中。

下面这段C语言代码实现了相同的功能：



```
const void *PMCHECK_BOUNDS = 0x954c000;
const void *PMCHECK_OFFSET = 0x954cfd0;
 
const int32_t PATCH_BYTES = 0xc340c031;
 
sys_mprotect(PMCHECK_BOUNDS, 0x1000, PROT_READ | PROT_WRITE | PROT_EXEC);
*PMCHECK_OFFSET = PATCH_BYTES;
```

在此情况下，PMCHECK_BYTES将会永远返回“true”值。



```
xor eax, eax   ; set eax to 0  -- 31 c0
inc eax        ; increment eax -- 40
ret            ; return        -- c3
```

没错，这段代码只是为了向内存中写入四个字节的数据，但是汇编代码却如此冗长。

 

**找出偏移量**

现在我们已经成功逆向了shellcode了，那么在将漏洞利用代码修改为针对新版本的思科ASA产品时，我们就可以利用其中的偏移量来实现代码更新了。

RET Smash

**我们可以将RET smash地址修改为了“ff e4”（随机选取的JMP ESP地址）。你将会发现，ASA 9.2(3)中的实际操作指令并不存在任何问题。**

[![](https://p3.ssl.qhimg.com/t01c5aaa21678c0db9a.png)](https://p3.ssl.qhimg.com/t01c5aaa21678c0db9a.png)

**<br>**

**安全返回地址**

在shellcode执行完毕之后，将会跳转到这个安全的返回地址。正如我们之前所提到的，这部分代码在IDA中并不会被识别为一个功能函数。**8.4(3)版本中的偏移量为0xad457e33^0xa5a5a5a5= 0x8e0db96**

[![](https://p1.ssl.qhimg.com/t01e85c26ec16fc69ea.png)](https://p1.ssl.qhimg.com/t01e85c26ec16fc69ea.png)

其中包含有一个单独的签名信息：

[![](https://p3.ssl.qhimg.com/t01e1526ffd85a2035f.png)](https://p3.ssl.qhimg.com/t01e1526ffd85a2035f.png)

我们的安全返回地址偏移量为0x9277386。

**<br>**

**身份验证函数**

实际上，想要找到pmcheck()和admauth()的偏移量是非常容易的。8.4(3)版本中的偏移量并不是与0xa5a5a5a5异或得到的，但是与sys_mprotect()对齐的内存页面地址却仍是这样计算的。我们可以dump出8.4(3)版本中的pmcheck()函数：

[![](https://p1.ssl.qhimg.com/t01488ef2aaf30c5fc9.png)](https://p1.ssl.qhimg.com/t01488ef2aaf30c5fc9.png)

接下来，我们就可以使用[Python ROPGadget](https://github.com/JonathanSalwan/ROPgadget)工具来搜索特定的字节数据了。

[![](https://p4.ssl.qhimg.com/t01083cfb38148b34f4.png)](https://p4.ssl.qhimg.com/t01083cfb38148b34f4.png)

**<br>**

**总结**

目前，我们已经编写好了一个Python脚本，这个脚本可以根据ASA防火墙设备的版本来自动转换漏洞利用代码版本。当然了，我们永远不能百分之百信任这些软件工具，所以我们还需要在各个版本平台上一一进行测试。

除此之外，我们也将Python脚本转换成了Ruby版本，所以渗透测试人员也可以在Metasploit中使用这些代码。我们的Metasploit模块将会包含Shadow Broker所有最新的shellcode，请大家保持关注！
