> 原文链接: https://www.anquanke.com//post/id/96730 


# 以三星为例，如何对TrustZone进行逆向工程和漏洞利用（上篇）


                                阅读量   
                                **215766**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Daniel Komaromy，文章来源：medium.com
                                <br>原文地址：[https://medium.com/taszksec/unbox-your-phone-part-i-331bbf44c30c ； https://medium.com/taszksec/unbox-your-phone-part-ii-ae66e779b1d6](https://medium.com/taszksec/unbox-your-phone-part-i-331bbf44c30c%20%EF%BC%9B%20https://medium.com/taszksec/unbox-your-phone-part-ii-ae66e779b1d6)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01b6b07437c185ac51.png)](https://p5.ssl.qhimg.com/t01b6b07437c185ac51.png)

## 一、前言

本文主要讲解了如何对三星的TrustZone进行逆向工程和漏洞利用，受字数所限，将会分为上下两篇。在上篇中，主要涵盖了关于架构的基础知识。尽管这些基础知识都来源于公开的信息，并没有不为人知的内容，但它们却分布在各种出版物上，非常零碎，所以我想将其整合成完整且连贯的内容。本篇文章部分技术细节来源于Trustonic和三星的官方文档，部分来源于开源软件，还有一部分来源于此前研究者所公开的研究成果。<br>
在本系列的后面，我还对逆向工程的成果进行了总结，并详细展现我所发现的漏洞。



## 二、简介

目前，已经有很多关于TrustZone的研究。在去年以前，大家主要侧重于对高通和华为产品的研究工作。此前这些关于可信执行环境（TEE）的研究都有一个共同的主题，就是其单点失效的特点（Single-point-of-failure Nature）。在这些可信执行环境中，普遍缺乏对特权的分隔，这也就意味着某一个漏洞会直接导致整个系统的沦陷，甚至是反复沦陷。<br>
下面8篇漏洞详情，就是反复沦陷最好的证明，大家可以参考阅读：<br>[https://www.blackhat.com/docs/us-14/materials/us-14-Rosenberg-Reflections-on-Trusting-TrustZone.pdf](https://www.blackhat.com/docs/us-14/materials/us-14-Rosenberg-Reflections-on-Trusting-TrustZone.pdf)<br>[http://bits-please.blogspot.hu/2015/08/full-trustzone-exploit-for-msm8974.html](http://bits-please.blogspot.hu/2015/08/full-trustzone-exploit-for-msm8974.html)<br>[https://www.blackhat.com/docs/us-15/materials/us-15-Shen-Attacking-Your-Trusted-Core-Exploiting-Trustzone-On-Android-wp.pdf](https://www.blackhat.com/docs/us-15/materials/us-15-Shen-Attacking-Your-Trusted-Core-Exploiting-Trustzone-On-Android-wp.pdf)<br>[https://pacsec.jp/psj14/PSJ2014_Josh_PacSec2014-v1.pdf](https://pacsec.jp/psj14/PSJ2014_Josh_PacSec2014-v1.pdf)<br>[http://bits-please.blogspot.hu/2016/05/qsee-privilege-escalation-vulnerability.html](http://bits-please.blogspot.hu/2016/05/qsee-privilege-escalation-vulnerability.html)<br>[https://www.slideshare.net/GeekPwnKeen/nick-stephenshow-does-someone-unlock-your-phone-with-nose](https://www.slideshare.net/GeekPwnKeen/nick-stephenshow-does-someone-unlock-your-phone-with-nose)<br>[https://microsoftrnd.co.il/Press%20Kit/BlueHat%20IL%20Decks/GalBeniamini.pdf](https://microsoftrnd.co.il/Press%20Kit/BlueHat%20IL%20Decks/GalBeniamini.pdf)<br>[http://theroot.ninja/disclosures/TRUSTNONE_1.0-11282015.pdf](http://theroot.ninja/disclosures/TRUSTNONE_1.0-11282015.pdf)<br>
然而，三星所使用的可信执行环境则有所不同。三星的环境是由Trustonic开发，Trustonic是一个专注于研究可信操作系统的公司，他们对可信执行环境解决方案的研发已经进行了15年之久。尽管在去年，Trustonic已经将他们的TEE OS更名为Kinibi，但我还是更习惯使用“T-Base”作为可信执行环境的名称。同样，此前Trustonic公司曾使用过MobiCore和Giesecke&amp;Devrient这两个名称，尽管如今已经更名，但还是有一些地方会使用旧名称，请各位读者注意这一点。<br>
最近，我在Ekoparty安全大会上就这一主题发表了演讲，我的演讲主要聚焦于如何对T-base微内核的逆向工程，以及T-Base的内部工作原理，并没有侧重于讲解Trustlets提供的实际功能和攻击面。这里的Trustlets是指在可信执行环境中运行的“可信应用程序”，基本上都是安全的操作系统中的用户空间进程。<br>
我演讲的视频请参见： [https://www.youtube.com/watch?v=L2Mo8WcmmZo](https://www.youtube.com/watch?v=L2Mo8WcmmZo) 。<br>
我演讲的PPT请参见： [https://github.com/puppykitten/tbase](https://github.com/puppykitten/tbase) 。<br>
在我发表演讲的时候，三星还没有完成全部漏洞的修复工作，这也是为什么我会将演讲的重点放在逆向工程的原因之一。终于，他们已经在2018年1月的安全通告中，完成了最后一个漏洞的修复。终于，我们可以放心地讨论这些漏洞，我也要感谢大家的耐心等待。<br>
根据我的经验，如果你发现某个架构设计得很差，那么随之而来的很可能就是一些重大的漏洞，特别是在嵌入式领域。



## 三、三星的KNOX和T-Base

由于我的研究都是基于三星的环境下完成的，那么我要解决的第一个问题，就是可信执行环境如何与三星的KNOX安全架构结合在一起。这一点非常重要，因为在早期版本的TrustZone中，它几乎只用于进行数字版权管理（DRM），所以从终端用户的角度来看，对其进行攻击的意义并不是太大。而现在，时代已经改变。<br>
针对TrustZone技术，三星公司已经发布了非常多的文档。其中，有两篇文档已经详细说明了其所具有的功能，我在这里就不再赘述，大家可以参考阅读：<br>[http://developer.samsung.com/tech-insights/knox/platform-security](http://developer.samsung.com/tech-insights/knox/platform-security)<br>[http://developer.samsung.com/tech-insights/pay/device-side-security](http://developer.samsung.com/tech-insights/pay/device-side-security)<br>
可信执行环境主要有下面三种用途：
1. 将安全敏感功能移入可信执行环境。这样一来，即使安卓环境受到了威胁，也不会对可信执行环境产生影响。例如：KeyStore证书、数字版权管理、证书管理、可信PIN、可信UI、移动设备管理远程认证。
1. 可信执行环境会对安卓系统中的功能进行监管，以缓解对Trustlets的漏洞利用尝试。例如：TIMA任意内核模块认证绕过、基于Trustlets的Kill-Switch勒索病毒。
<li>仅允许从可信执行环境访问硬件设备，从而缓解针对硬件的攻击。例如：指纹传感器、用于非接触式支付的磁信号安全传输技术（MST）等。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-images-1.medium.com/max/1600/1*HEMRdK_N8O6hON056ZcH7A.jpeg)<br>
上述的所有内容，都有一个共同的特点：每一个功能都是由一个（或多个）Trustlet实现。这就充分说明，如果要对实际功能方面进行研究，我们应该关注Trustlet。但如果我们想要了解这些Trustlet的安全性（例如：在安全内核和不安全内核之间，它们是如何相互隔离的），我们就需要深入了解T-Base。<br>
在这里，我想要说明的是，尽管本文中涉及一些Trustlet的实际功能，但更多是用于向大家展现这些漏洞的存在。</li>


## 四、T-Base的结构

如果你想阅读厂商关于T-Base的介绍（更侧重于产品营销目的），请参考： [https://www.trustonic.com/solutions/trustonic-secured-platforms-tsp/](https://www.trustonic.com/solutions/trustonic-secured-platforms-tsp/) 。<br>
在最一开始，我们可以轻而易举地通过各种资料来熟知T-Base的结构——既有抽象层面的图示，又有大量的可用信息，同时还有三星和Trustonic共同公开的源代码可以参考。<br>
这一切的核心，是安卓进程（应用程序）通过世界共享内存（World Shared Memory）与Trustlet通信。剩下的只有安卓、Linux内核和T-Base内核所提供的抽象层与安全边界层。<br>
我们从T-Base架构的一张经典图示开始，来了解T-Base的结构。<br>[![](https://cdn-images-1.medium.com/max/1600/1*CXuy2VftWnEIM8G0PCOEQw.jpeg)](https://cdn-images-1.medium.com/max/1600/1*CXuy2VftWnEIM8G0PCOEQw.jpeg)

### <a class="reference-link" name="4.1%20ATF%EF%BC%9AARM%E5%8F%AF%E4%BF%A1%E5%9B%BA%E4%BB%B6"></a>4.1 ATF：ARM可信固件

首先，我们需要在硬件层面上，连接安全的世界（与不安全的世界。这一点是通过ARM上的SMC指令（Secure Monitor Call）来实现的，它会将执行过程从安全世界切换到不安全世界，就像是SVC将执行过程从EL0切换到EL1一样。但是，我们并没有真正地使用这样的指令跳转到一个安全世界EL1中的Handler，而是执行跳转到所谓的监视模式（Monitor Mode，ARM的EL3）之中。就像是一个代理，其目标是将安全世界与不安全世界之间的SMC组织起来。在Trustonic中，它并不是T-Base的一部分，而是单独实现的。关于ARM EL的更多信息，请参考：[http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.ddi0488d/CHDHJIJG.html](http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.ddi0488d/CHDHJIJG.html) 。<br>
三星（包括其他使用Trustonic的厂商，例如部分使用联发科芯片的小米手机）就在使用ATF（ARM可信固件）来实现监控模式。上述实现基本上是参考了ARM的开源文档。此外，Quarkslab针对ATF逆向方面写了一篇非常不错的文章，大家可以参考阅读：<br>[https://blog.quarkslab.com/reverse-engineering-samsung-s6-sboot-part-i.html](https://blog.quarkslab.com/reverse-engineering-samsung-s6-sboot-part-i.html)<br>[https://blog.quarkslab.com/reverse-engineering-samsung-s6-sboot-part-ii.html](https://blog.quarkslab.com/reverse-engineering-samsung-s6-sboot-part-ii.html)<br>
需要注意的一点是，Linux内核不仅要使用SMC调用（通过ATF）来到达T-Base，并且T-Base内核还借助于SMC调用来实现与ATF的通信。上述内容实际上是一个黑盒问题，我们并不知道其具体原理，将会在下一篇文章中进一步学习探讨。<br>
在这里，我要补充一句，不仅ATF会借助SMC调用来到达T-Base，有些SMC调用也可以让ATF实现命令。其中一部分是开源ATF代码中包含的命令，一部分是厂商自定义的命令。但这些并不是此次研究的重点。

### <a class="reference-link" name="4.2%20T-Base%EF%BC%9A%E5%BE%AE%E5%86%85%E6%A0%B8"></a>4.2 T-Base：微内核

在图中的右侧，就是我们的安全世界，T-Base也在安全世界中。起初，我们认为共包含三个部分：微内核、安全驱动和Trustlet。但在后续研究中，我们意识到这个假设是错误的。图中的“运行管理（Runtime Management）”，实际上既不是Trustlet，也不是驱动，更不是微内核。关于这一点会在本篇文章的后面进行介绍。现在，我们假设在T-Base操作系统中，如果一件事不是由Trustlet和安全驱动来完成，那就一定是微内核完成的。<br>
因此，在我们研究Trustlet之前，我们想首先了解如何通过微内核来实现对Trustlet的管理（例如加载）。<br>
为了充分掌握原理，我们必须对微内核进行逆向工程。三星将T-Base固件存储在一个不显眼的位置——打包在sboot映像中。Gal Beniamini已经发表过一种用来提取该映像的方法，详情请参考他博客文章中“Kinibi Revocation”一节：[https://googleprojectzero.blogspot.hu/2017/07/trust-issues-exploiting-trustzone-tees.html](https://googleprojectzero.blogspot.hu/2017/07/trust-issues-exploiting-trustzone-tees.html) ，在本篇文章后面，也会详细进行介绍。<br>
尽管我们必须进行逆向才能知道微内核实现Trustlet管理的具体方式，但我们可以通过公开的文档了解到微内核相当多的管理接口。<br>
T-Base将其称为MobiCore控制协议（MCP）接口（MCI）。这是建立在SMC调用之上的，接下来我们就做具体的分析。<br>
至此，如果你已经阅读了Gal的文章，那么想必就一定知道，在三星S8之前，T-Base并没有在Trustlet加载过程中被用于回滚保护。

### <a class="reference-link" name="4.3%20T-Base%EF%BC%9ASMC%E5%BF%AB%E9%80%9F%E8%B0%83%E7%94%A8"></a>4.3 T-Base：SMC快速调用

如果你已经习惯了其他的可信执行环境实现，你可能会希望每个管理功能（例如：加载Trustlet、与Trustlet共享内存、打开到Trustlet的连接等）都能是另一个微内核实现的管理程序调用，可以通过将正确的参数传递给SMC调用来直接触发，就像Linux中的ioctl调用一样。<br>
实际上，Trustonic采取了一种完全不同的方式，保证了微内核“微”的这一特点。这一实现，可以从Linux内核源代码中详细了解，具体请参阅drivers/gud/gud-exynos8890/MobiCoreDriver/*.c。<br>
（附注：源代码中，驱动程序文件夹名称为“gud”，就是因为原来的公司名称是“Giesecke and Devrient”。）<br>
在Linux内核中，总共有5个SMC快速调用。其中，MC_FC_INIT用于配置队列，MC_FC_INFO可以从T-Base中获取版本信息等信息，MC_FC_SWAP_CPU可用于将T-Base移动到特定的CPU核心中，MC_FC_YIELD和MC_FC_NSIQ用于调度T-Base的运行。<br>
fastcall.c源代码如下：

```
/* fast call init */
union mc_fc_init `{`
    union mc_fc_generic as_generic;
    struct `{`
        u32 cmd;
        u32 base;
        u32 nq_info;
        u32 mcp_info;
    `}` as_in;
    struct `{`
        u32 resp;
        u32 ret;
        u32 flags;
        u32 rfu;
    `}` as_out;
`}`;

/* fast call info parameters */
union mc_fc_info `{`
    union mc_fc_generic as_generic;
    struct `{`
        u32 cmd;
        u32 ext_info_id;
        u32 rfu[2];
    `}` as_in;
    struct `{`
        u32 resp;
        u32 ret;
        u32 state;
        u32 ext_info;
    `}` as_out;
`}`;

#ifdef TBASE_CORE_SWITCHER
/* fast call switch Core parameters */
union mc_fc_swich_core `{`
    union mc_fc_generic as_generic;
    struct `{`
        u32 cmd;
        u32 core_id;
        u32 rfu[2];
    `}` as_in;
    struct `{`
        u32 resp;
        u32 ret;
        u32 state;
        u32 ext_info;
    `}` as_out;
`}`;
#endif
```

fastcall2.c源代码如下：

```
int mc_fc_nsiq(void)
`{`
    union mc_fc_generic fc;
    int ret;

    memset(&amp;fc, 0, sizeof(fc));
    fc.as_in.cmd = MC_SMC_N_SIQ;
    mc_fastcall(&amp;fc);
    ret = convert_fc_ret(fc.as_out.ret);
    if (ret)
        mc_dev_err("failed: %dn", ret);

    return ret;
`}`

int mc_fc_yield(void)
`{`
    union mc_fc_generic fc;
    int ret;

    memset(&amp;fc, 0, sizeof(fc));
    fc.as_in.cmd = MC_SMC_N_YIELD;
    mc_fastcall(&amp;fc);
    ret = convert_fc_ret(fc.as_out.ret);
    if (ret)
        mc_dev_err("failed: %dn", ret);

    return ret;
`}`
```

这些命令都是通过_smc()函数来执行，该函数的作用是将参数存储在寄存器中，并生成一个SMC。<br>
所以我们知道，如果我们想根据VBAR的设置来寻找T-Base微内核的SMC处理程序，那我们应该只能找到这一简单的实现，后面必须要对微内核中未记录的解决方案进行逆向工程，来确定代码实际处理MCP命令的位置所在。<br>
当然，上述过程也不是完整的，Linux内核需要在T-Base被响应时得到通知。实际上，这一点是通过中断来实现的：内核驱动在系统上注册一个终端，T-Base通过MC_FC_INIT命令获知到中断的发生。

### <a class="reference-link" name="4.4%20T-Base%EF%BC%9AMobiCore%E6%8E%A7%E5%88%B6%E5%8D%8F%E8%AE%AE"></a>4.4 T-Base：MobiCore控制协议

MCP是基于共享缓冲区的协议，因此SMC唯一可以做的，就是设置MCP队列，通知T-Base队列中有新的输入，并安排在安全世界中运行。其中，有两个队列：命令队列是不安全世界可以加载MCP命令的地方；通知队列是不安全世界可以加载Trustlet标识符的地方，以便通知特定的Trustlet有一条命令在等待它。<br>
MCP命令的作用在于：我们可以加载/挂起/恢复Trustlet，并且可以映射/取消映射其他共享内存到Trustlet实例的地址空间。MCP命令列表可以在Linux内核源代码中找到，具体请参见drivers/gud/gud-exynos8890/MobiCoreDriver/mci/mcimcp.h。

```
/** Possible MCP Command IDs
 * Command ID must be between 0 and 0x7FFFFFFF.
 */
enum cmd_id `{`
    /** Invalid command ID */
    MC_MCP_CMD_ID_INVALID        = 0x00,
    /** Open a session */
    MC_MCP_CMD_OPEN_SESSION        = 0x01,
    /** Close an existing session */
    MC_MCP_CMD_CLOSE_SESSION    = 0x03,
    /** Map WSM to session */
    MC_MCP_CMD_MAP            = 0x04,
    /** Unmap WSM from session */
    MC_MCP_CMD_UNMAP        = 0x05,
    /** Prepare for suspend */
    MC_MCP_CMD_SUSPEND        = 0x06,
    /** Resume from suspension */
    MC_MCP_CMD_RESUME        = 0x07,
    /** Get MobiCore version information */
    MC_MCP_CMD_GET_MOBICORE_VERSION    = 0x09,
    /** Close MCP and unmap MCI */
    MC_MCP_CMD_CLOSE_MCP        = 0x0A,
    /** Load token for device attestation */
    MC_MCP_CMD_LOAD_TOKEN        = 0x0B,
    /** Check that TA can be loaded */
    MC_MCP_CMD_CHECK_LOAD_TA    = 0x0C,
    /** Map multiple WSMs to session */
    MC_MCP_CMD_MULTIMAP        = 0x0D,
    /** Unmap multiple WSMs to session */
    MC_MCP_CMD_MULTIUNMAP        = 0x0E,
`}`;
```

尽管该功能非常简单，但不意味着以安全的方式来实现该功能也是非常简单的。事实上，几乎所有的安卓可信执行环境厂商，都存在安全问题，更多详情可以参见UCSB研究人员发表的《BOOMERANG》文章：[https://www.cs.ucsb.edu/~vigna/publications/2017_NDSS_Boomerang.pdf](https://www.cs.ucsb.edu/~vigna/publications/2017_NDSS_Boomerang.pdf) 。<br>
从Linux内核的角度来看，这些功能是通过实现mc_user_fops操作（该操作在drivers/gud/gud-exynos8890/MobiCoreDriver/user.c中定义）的/dev/mobicore设备节点过程中暴露的。

### <a class="reference-link" name="4.5%20T-Base%EF%BC%9ATrustlet%E5%92%8C%E5%AE%89%E5%85%A8%E9%A9%B1%E5%8A%A8"></a>4.5 T-Base：Trustlet和安全驱动

接下来，让我们一起来看看Trustlet。首先要提到的是，在去年，Gal Beniamini的一篇博客文章（ [https://googleprojectzero.blogspot.hu/2017/07/trust-issues-exploiting-trustzone-tees.html](https://googleprojectzero.blogspot.hu/2017/07/trust-issues-exploiting-trustzone-tees.html) ）中对T-Base Trustlet的实现给出了非常棒的观点，我觉得大家有必要首先阅读一下。<br>
更详细的内容，请继续阅读本文。<br>
根据Tim Newsham此前的研究（ [http://thenewsh.blogspot.hu/2015/02/disassembling-mobicore-trustlets.html](http://thenewsh.blogspot.hu/2015/02/disassembling-mobicore-trustlets.html) ），我们知道，Trustlet二进制文件可以在设备的/system/app/mcRegistry或/data/app/mcRegistry中找到，或者从三星FOTA映像中装载了sim2img的system.img的APP目录下找到。<br>
我们还需要知道MobiCore加载器格式（MCLF，Truslet和安全驱动的文件格式）：在内核源代码中，请查看诸如gud/gud-exynos8890/MobiCoreDriver/mci/mcloadformat.h这样路径下的源文件。这是一个由Gassan Idriss编写的IDA加载程序，可供参考：[https://github.com/ghassani/mclf-ida-loader/blob/master/mclf_loader.py](https://github.com/ghassani/mclf-ida-loader/blob/master/mclf_loader.py) 。此外，Tim Newsham还写了另一套工具（ [http://pastebin.com/ea7BG6cj](http://pastebin.com/ea7BG6cj) ； [http://pastebin.com/DPwcmrK2](http://pastebin.com/DPwcmrK2) ），用于将MCLF转换成ELF。<br>
在Trustlet中区分驱动非常简单，可以根据MCLF中的版本字段来判断。或者还有一种更快的方法：名称以“ffffffff00”开头的是Trustlet，名称以“ffffffffd0”开头的是安全驱动。另一方面，由于这些名称是以他们的UUID命名的，而不是一个有意义的名字，因此想要知道哪些二进制文件中隐藏了什么功能并不容易。我们可以使用逆向工程的方式来实现这一点。<br>
尽管其加载过程是在不安全世界中进行的解析，但MCLF格式在安卓内核源代码中还是有意义的，但更令人惊讶的是，所谓的tlApi和drApi也在某些来源中被定义。我不知道这是否是一个错误的定义，并且也不是在每个发布的三星内核源代码中都能找到该路径，但至少我在GitHub的源代码中发现了一个存在的样例。<br>
这些是Trustlet与安全驱动分别用来与T-Base微内核通信的API。其中包括与不安全世界中应用程序进行交互的功能、允许安全世界中进程（Trustlet/安全驱动）相互通信的功能，以及对通常由内核处理的功能的调用（例如映射内存地址空间）。<br>
正如Tim Newsham和Gal Beniamini的博客文章中所述，Trustlet通过一个调用门（Call-Gate，类似于ELF的GOT，除了对所有API调用都有单个跳转目标之外）调用这些API。也就是说，这些调用并没有编译成Trustlet二进制文件。由此，我们就又产生了另一个资料都未能解答的疑问——这些API实际上都在哪里，并且是如何实现的？我们可以推测，这些API实际上会以某种方式被SVC调用包装，并在T-Base微内核中实现系统调用处理程序。但我们并不清楚其中的细节。同样，我们也没有tlApi或drApi中所有调用的信息。此外，Tim的博客文章是几年之前写的，其中所列出的API调用列表也是不完整的。<br>
关于安全驱动，除了这些头文件之外，我没有找到太多的公开资料。就目前而言，理解了安全驱动能够访问各种硬件就已经足够了。此外，加密驱动会与加密引擎进行通信。安全SPI驱动一方面会通过SPI接口与指纹传感器进行通信，另一方面通过SPI接口与安全支付的嵌入式安全元件（Samsung Pay）进行通信。上述所提及内容，均在三星官方文档（ [http://developer.samsung.com/tech-insights/pay/device-side-security](http://developer.samsung.com/tech-insights/pay/device-side-security) ）中有详细说明。<br>
关于Trustlet和tlApi，我们可以找到一些公开信息，例如Trustonic的Jan-Erik Ekberg的演示（ [https://usmile.at/sites/default/files/androidsecuritysymposium/presentations2015/Ekberg_AndroidAndTrustedExecutionEnvironments.pdf](https://usmile.at/sites/default/files/androidsecuritysymposium/presentations2015/Ekberg_AndroidAndTrustedExecutionEnvironments.pdf) ）。根据他PPT上面的一张截图，我们可以看到：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn-images-1.medium.com/max/1600/1*n-P9Os70tRUlZIyHt9HeQw.png)<br>
Trustlet的基本行为非常简单。在IPC部分（与安全驱动通信）有些复杂，但就接口的Trustlet而言，只有tlApi调用tlApi_callDriver()，其工作原理与Linux的ioctl有些相似，它将一个命令ID和一个指向命令结构的指针作为参数。这里也是，并没有在Linux内核源代码中体现，但我们在GitHub上却至少可以找到一个源代码是使用了这样的头文件。<br>
如果你已经阅读了Jan-Erik的幻灯片，你应该已经了解到有一个名为GP（Global Platform）的标准化可信执行环境，它为不同的可信执行环境创建了一个通用的API。Trustonic支持GP标准，因此他们也有相应的API可以实现通用标准。他们所做的，就是增加了一些特性，将相应内容变成T-Base特定的API。然而比较不错的是，三星似乎在Trustlet中使用了传统的API，所以我们不用担心这一点。



## 五、T-Base与安卓

现在，我们来研究安卓层面。这里仍然有Trustonic编写的代码，他们创建了一个用户控件守护进程mcDriverDaemon，向用户空间的应用程序开放接口。由于某种原因，以前版本的代码曾经开源过，因此理解这个驱动程序的驱动就变得非常简单。<br>
这个守护进程通过libMcClient.so访问内核设备节点，其命令清晰地映射到MCP命令中，请参考： [https://github.com/Trustonic/trustonic-tee-user-space](https://github.com/Trustonic/trustonic-tee-user-space) 。<br>
Trustonic这一设计目的在于，只有mcDriverDaemon能够访问设备节点，并且通过UNIX本地套接字开放接口。Trustonic将该接口命名为TLC（Trustlet连接器）。<br>
在三星的具体场景下，这一情况更为复杂。一方面，设备节点使用DAC和MAC（SELinux）进行限制，但仍有许多特权进程可以对其进行访问，其中有一些无需通过mcDriverDaemon即可对其进行操作。同样，UNIX本地套接字只能由特权进程访问。事实上，三星想要分为直接（libtlc_direct_comm.so）和代理（libtlc_proxy_comm.so）这两种方式，但有一些进程同时使用了这两种方式。<br>
至此，我们的研究过程还并不完整。很显然，三星使用这样的配置，使得安卓系统中一些TrustZone支持的功能能够完全在特权模式下进行，例如system_server。但还有一种功能，可以将特权进程扩展到应用程序中，完全无需权限，或是可以通过常规的应用程序来获取到权限。<br>
这是通过将Binder接口添加到各种特权进程中来实现的。安卓会借助API来允许进程在其Binder接口上进行访问控制，因此我们非常希望三星也能够实现这一点。但是，我们必须要深入进行逆向工程，因为目前没有相关文档或相关的现有技术。<br>
Gal曾经写过一个otp_server代理。同样，还有很多其他的代理。举例来说，这个例子是针对Samsung Pay场景下实现的： [https://www.blackhat.com/docs/eu-17/materials/eu-17-Ma-How-Samsung-Secures-Your-Wallet-And-How-To-Break-It.pdf](https://www.blackhat.com/docs/eu-17/materials/eu-17-Ma-How-Samsung-Secures-Your-Wallet-And-How-To-Break-It.pdf) 。在我们的研究中，我专注于使用tlc_server，目前暂时还没有尝试过其他情况。



## 六、与Trustlet的通信

在对这一架构的细节进行研究的过程中，我们注意到一个明显的漏洞。<br>
尽管我们已经知道如何在安卓中设置WSM（TCI缓冲区）来向一个Trustlet发送命令，但是我们并不知道该命令的固定格式，也没有找到任何用于实现常见任务的指导（或者相关的库）。那从事实上看，每一个Trustlet都有自己的方式吗？<br>
尽管目前，公开资料中并没有用于Trustlet通信的通用命令结构，但是Trustonic可能会与合作商分享开发人员指南。那对于我们来说，就只能通过逆向工程来实现了。<br>
剧透警告：在最后，通过对Trustlet进行逆向，我发现三星Trustlet的命令看上去是使用了通用头部格式，但实际上不一定是通用的。并且，对于Trustlet之间的命令有效载荷，它并不会扩展到任意种类的标准结构。



## 七、小结

接下来，让我们回顾一下该结构的各个层级：
1. 三星Sboot遵循ATF模型。Sboot会加载EL3固件（ATF）和操作系统运行在安全世界的EL0+EL1（T-Base）。在加载完成后，bootloader会将处理器切换成不安全世界模式，并加载应用程序，当然也会加载安卓系统。
1. ATF会捕获到全部世界中EL1的SMC调用，并在二者之间进行代理。
1. Linux内核会设置用作MCP命令队列和通知队列的共享缓冲区，并通过快速调用（在寄存器中传递带有参数的SMC指令）来初始化与T-Base微内核的通信。
1. Linux内核使用另一个快速调用来通知（进行调度）T-Base。T-Base使用Linux内核中注册的中断，在处理命令完成后通知不安全世界。
1. Linux内核实现了MCP，这些命令允许通过Trustlet实例来加载并共享内存，并通过/dev/mobicore和/dev/mobicore-user设备的ioctl接口对外开放。它包括在WSM范围之内的完整性检查，用于确保用户空间无法请求可能导致不安全世界内部Linux内核损坏/内核特权提升的内存区域。（此前发现，这种健全性的检查是不充分的。）
1. libMcClient.so库负责ioctl接口的用户空间实现。
1. 用户空间进程通过不同的libtlc_*共享库来实现对库的利用。拥有足够特权的进程，可以直接使用能够加载libMcClient.so的变体，其他进程需要通过mcDriverDaemon来获得访问权限。在这里，通过普通的UNIX套接字暴露了MCP接口，但后面增加了健全性检查，就可以防止客户端进行类似于Linux内核的非法MCP行为。
1. 套接字仍然受MAC和DAC机制的限制，因此非特权应用程序无法访问它们。而与之相反，三星增加了各种代理进程（比如tlc_server），通过Binder进一步暴露了mcDriverDaemon接口，从而允许具有足够权限的应用程序通过访问特定的Binder界面的方式来与T-Base进行交互，以及加载Trustlet并与之通信。


## 八、T-Base映像提取

要提取所有嵌入到Sboot映像中的T-Base固件（例如：微内核、运行时间管理器、tlLibrary、加密驱动等），需要使用字符串标记“t-base”来查找提取表：

```
ROM:00147000 tbase_extract_table DCB "t-base ",0     ; descriptor struct:
ROM:00147000                                         ;     char name[8]
ROM:00147000                                         ;     int offset
ROM:00147000                                         ;     int size
ROM:00147000                                         ;     char padding[0x10]
ROM:00147000                                         ;
ROM:00147000                                         ; real start offset: 0x132000
ROM:00147000                                         ;
ROM:00147000                                         ; Mtk: 0-&gt;0x147000 -&gt; the Microkernel image itself -&gt; go back 0x15000 from "t-base"
ROM:00147000                                         ; Image_h: 0x147000 -&gt; 0x148000 -&gt; so that's this
ROM:00147000                                         ; Rtm: 0x148000 -&gt; RTM is the Run-Time Manager (aka S0CB)
ROM:00147000                                         ;
ROM:00147000                                         ; drcrypt: 0x167000 -&gt; MCLF file (Crypto Driver)
ROM:00147000                                         ; tlproxy: 0x17A000 -&gt; MCLF file (SFS Trustlet)
ROM:00147000                                         ; sth2: 0x17B000    -&gt; MCLF file (SFS Driver)
ROM:00147000                                         ; mclib: 0x183000   -&gt; tlLib (runtime library for Trustlets and Drivers)
ROM:00147008                 DCD 0
ROM:0014700C                 DCD 0x5D000
ROM:00147010                 ALIGN 0x20
ROM:00147020 aMtk            DCB "mtk    ",0
ROM:00147028                 DCD 0
ROM:0014702C                 DCD 0x15000
ROM:00147030                 ALIGN 0x20
ROM:00147040 aImage_h        DCB "image_h",0
ROM:00147048                 DCD 0x15000
ROM:0014704C                 DCD unk_1000
ROM:00147050                 ALIGN 0x20
ROM:00147060 aRtm            DCB "rtm    ",0
ROM:00147068                 DCD 0x16000
ROM:0014706C                 DCD 0x1F000
ROM:00147070                 ALIGN 0x20
ROM:00147080 aDrcrypt        DCB "drcrypt",0
ROM:00147088                 DCD 0x35000
ROM:0014708C                 DCD 0x13000
ROM:00147090                 ALIGN 0x20
ROM:001470A0 aTlproxy        DCB "tlproxy",0
ROM:001470A8                 DCD 0x48000
ROM:001470AC                 DCD 0x1000
ROM:001470B0                 DCD 0
ROM:001470B4                 DCD 0
ROM:001470B8                 DCD 0
ROM:001470BC                 DCD 0
ROM:001470C0 aSth2           DCB "sth2   ",0
ROM:001470C8                 DCD 0x49000
ROM:001470CC                 DCD unk_8000
ROM:001470D0                 ALIGN 0x20
ROM:001470E0 aMclib          DCB "mclib  ",0
ROM:001470E8                 DCD 0x51000
ROM:001470EC                 DCD unk_C000
ROM:001470F0                 ALIGN 0x1000
ROM:00148000 S0CB_HDR        DCB "S0CB",0            ; Rtm offset points here
ROM:00148005                 DCB 0x10, 0, 0
ROM:00148008                 DCD unk_C000
ROM:0014800C                 DCD dword_D000
ROM:00148010                 DCD 0
ROM:00148014                 DCD 0x11960
ROM:00148018                 DCD 0xB295
ROM:0014801C                 DCD 0x3F
ROM:00148020                 DCD 0x6A
ROM:00148024 aMccb           DCB "MCCB",0
ROM:00148029                 DCD 0
ROM:0014802D                 DCD 0
```



## 九、T-Base SMC

目前，我已经确定了以下T-Base与通过ATF调用的SMC的对应关系：<br>
0x1：从不安全世界中进行快速调用，并通过ATF返回到不安全世界中；<br>
0xB2000002：将VBAR值发送给ATF（因此ATF知道SMC处理程序的位置）；<br>
0xB2000003：写入字符（用于通过ATF记录消息）；<br>
0xB2000004：将T-Base初始化状态发送给ATF。

```
ROM:00133054 tbase_smc_send_VBAR                     ; CODE XREF: config_tbase_and_tell_aft_the_vbar+E↑p
ROM:00133054                 LDR             R0, =0xB2000002
ROM:00133058                 MOV             R1, #1
ROM:0013305C                 LDR             R2, =0x7F00000 ; normal VBAR address
ROM:00133060                 SMC             #0
ROM:00133064                 BX              LR
ROM:00133064 ; End of function tbase_smc_send_VBAR
ROM:00133064
ROM:00133068
ROM:00133068 ; =============== S U B R O U T I N E =======================================
ROM:00133068
ROM:00133068 ; Attributes: noreturn
ROM:00133068
ROM:00133068 tbase_smc_fastcall_status_then_ret_to_nonSW
ROM:00133068                                         ; CODE XREF: sub_1343AA:loc_1354C8↓p
ROM:00133068                                         ; translate_MSMBase_to_VA+46↓p
ROM:00133068                 LDR             R0, =0xB2000004
ROM:0013306C                 MOV             R1, #1
ROM:00133070                 MOV             R2, #1
ROM:00133074                 SMC             #0
ROM:00133078                 LDR             R0, =0x2000001
ROM:0013307C                 SMC             #0
ROM:00133080
ROM:00133080 loc_133080                              ; CODE XREF: tbase_smc_fastcall_status_then_ret_to_nonSW:loc_133080↓j
ROM:00133080                 B               loc_133080
ROM:00133080 ; End of function tbase_smc_fastcall_status_then_ret_to_nonSW
ROM:00133080
ROM:00133084
ROM:00133084 ; =============== S U B R O U T I N E =======================================
ROM:00133084
ROM:00133084
ROM:00133084 tbase_smc_fastcall_status               ; CODE XREF: sub_1343AA+31C6↓p
ROM:00133084                 LDR             R0, =0xB2000004
ROM:00133088                 MOV             R1, #1
ROM:0013308C                 MOV             R2, #3
ROM:00133090                 SMC             #0
ROM:00133094                 BX              LR
ROM:00133094 ; End of function tbase_smc_fastcall_status
ROM:00133094
ROM:00133098
ROM:00133098 ; =============== S U B R O U T I N E =======================================
ROM:00133098
ROM:00133098
ROM:00133098 tbase_smc_fastcall_print
ROM:00133098                 MOV             R2, R0
ROM:0013309C                 LDR             R0, =0xB2000003
ROM:001330A0                 MOV             R1, #1
ROM:001330A4                 SMC             #0
ROM:001330A8                 BX              LR
ROM:001330A8 ; End of function tbase_smc_fastcall_print

(...)
```



## 十、T-Base系统调用

```
.tbase_mem_data:07F0D86C ; ===========================================================================
.tbase_mem_data:07F0D86C
.tbase_mem_data:07F0D86C ; Segment type: Pure data
.tbase_mem_data:07F0D86C                 AREA .tbase_mem_data, DATA, ALIGN=0
.tbase_mem_data:07F0D86C                 ; ORG 0x7F0D86C
.tbase_mem_data:07F0D86C syscall_table   DCD svc_0_nop+1         ; DATA XREF: invoke_syscall_from_table+40↑o
.tbase_mem_data:07F0D86C                                         ; invoke_syscall_from_table:syscall_table_ptr↑o
.tbase_mem_data:07F0D870                 DCD svc_1_init_process+1
.tbase_mem_data:07F0D874                 DCD svc_2_nop+1
.tbase_mem_data:07F0D878                 DCD svc_3_nop+1
.tbase_mem_data:07F0D87C                 DCD svc_4+1             ; Did not find this invoked anywhere in `{`RTM,tlLib`}`
.tbase_mem_data:07F0D880                 DCD svc_5_start_process+1
.tbase_mem_data:07F0D884                 DCD svc_exit+1
.tbase_mem_data:07F0D888                 DCD svc_mmap+1
.tbase_mem_data:07F0D88C                 DCD svc_8_munmap+1
.tbase_mem_data:07F0D890                 DCD svc_9_start_thread+1
.tbase_mem_data:07F0D894                 DCD svc_A_stop_thread+1
.tbase_mem_data:07F0D898                 DCD svc_B_return_0xD+1
.tbase_mem_data:07F0D89C                 DCD svc_C_modify_thread_registers+1
.tbase_mem_data:07F0D8A0                 DCD svc_D_mprotect+1
.tbase_mem_data:07F0D8A4                 DCD svc_E_resume_thread+1
.tbase_mem_data:07F0D8A8                 DCD svc_F+1
.tbase_mem_data:07F0D8AC                 DCD svc_10_set_thread_prio+1
.tbase_mem_data:07F0D8B0                 DCD svc_11_ipc+1
.tbase_mem_data:07F0D8B4                 DCD svc_12_int_attach+1
.tbase_mem_data:07F0D8B8                 DCD svc_13_int_detach+1
.tbase_mem_data:07F0D8BC                 DCD svc_14_sigwait+1
.tbase_mem_data:07F0D8C0                 DCD svc_15_signal+1
.tbase_mem_data:07F0D8C4                 DCD svc_16+1            ; Did not find this invoked anywhere in `{`RTM,tlLib`}`
.tbase_mem_data:07F0D8C8                 DCD svc_tbase_smc_fastcall_input+1
.tbase_mem_data:07F0D8CC                 DCD svc_18_log_char+1
.tbase_mem_data:07F0D8D0                 DCD svc_19_get_secure_timestamp+1
.tbase_mem_data:07F0D8D4                 DCD svc_1A_control+1    ; includes a lot, such as:
.tbase_mem_data:07F0D8D4                                         ; - driver shmem map/unmap
.tbase_mem_data:07F0D8D4                                         ; - get/set exception info
.tbase_mem_data:07F0D8D4                                         ; - get MCP queue info
.tbase_mem_data:07F0D8D4                                         ; - get IPCH phys address values
.tbase_mem_data:07F0D8D4                                         ; - cache control
.tbase_mem_data:07F0D8D4                                         ; - virt2phys, phys2virt translation
.tbase_mem_data:07F0D8D4                                         ; - set custom fastcall, call custom fastcall
.tbase_mem_data:07F0D8D4                                         ;
.tbase_mem_data:07F0D8D4                                         ; Known sub-handlers:
.tbase_mem_data:07F0D8D4                                         ;
.tbase_mem_data:07F0D8D4                                         ; -0x8F: getting/setting fastcall configuration values
.tbase_mem_data:07F0D8D4                                         ;     - 0xC: get S0CB PA
.tbase_mem_data:07F0D8D4                                         ;     - 0xA: notify (nSW - trigger interrupt)
.tbase_mem_data:07F0D8D4                                         ;     - 0xB: notify driver (drTriggerIntr)
.tbase_mem_data:07F0D8D4                                         ;     - 0xD: get fc_init perm flags
.tbase_mem_data:07F0D8D4                                         ;     - 0x1: set exception info
.tbase_mem_data:07F0D8D4                                         ;     - 0x2: get fault info
.tbase_mem_data:07F0D8D4                                         ;     - 0x4,0x5,0x6,0x7: get MCP queue info
.tbase_mem_data:07F0D8D4                                         ; (mci_buffer_addr, nq_length, mcp_queue_addr, mcp_queue_len)
.tbase_mem_data:07F0D8D4                                         ;     - 0x9: map mcp cmd queue (in kernel)
.tbase_mem_data:07F0D8D4                                         ; -0x90 -&gt; more control
.tbase_mem_data:07F0D8D4                                         ;     - 5: read info for exception
.tbase_mem_data:07F0D8D4                                         ;     - 7: translate VA to PA
.tbase_mem_data:07F0D8D4                                         ; -0x91 virt-to-phys and also virt-to-phys64
.tbase_mem_data:07F0D8D4                                         ; -0x92 -&gt;  I-cache clean/invalidate, D-cache clean/invalidate
.tbase_mem_data:07F0D8D4                                         ; -0x81:map, 0x83: unmap, 0x85:map.
.tbase_mem_data:07F0D8D4                                         ;  - Difference in 81/85: map in
```



## 十一、RTM IPC

请注意，在这里我们称RTM为“S0CB”，是由于其文件格式的魔术值（Magic Value）。根据Sboot固件中的提示，更加准确的一个名称应该是RTM（Run Time Manager，运行时间管理器）。<br>
这是T-Base中一个强大的用户空间进程，始终最先启动，并负责启动和管理所有其他进程（Trustlet）。与Linux上的init类似，它负责三个功能：
1. 实现MCP；
1. 当请求从不安全世界到达时，通知Trustlet；
<li>实现T-Base的IPC机制。<br>
其中，MCP命令都可以从公开渠道获知。对于IPC，前12个IPC命令可以在这里找到源代码：[https://searchcode.com/codesearch/view/42497996/](https://searchcode.com/codesearch/view/42497996/) 。在这里，我参考了相关的命名约定，对于其余部分，具体如下：</li>
```
/** Possible message types/event types of the system. */
typedef enum `{`
    MSG_NULL = 0,  // Used for initializing state machines
    /***************/
    MSG_RQ                  = 1,  /**&lt; Request; client -&gt; server;  */
    MSG_RS                  = 2,  /**&lt; Response; server -&gt; client */
    MSG_RD                  = 3,  /**&lt; Ready; server -&gt; IPCH */
    MSG_NOT                 = 4,  /**&lt; Notification; client -&gt; IPCH; */
    MSG_CLOSE_TRUSTLET      = 5,  /**&lt; Close Trustlet; MSH -&gt; IPCH; IPCH -&gt; all servers */
    MSG_CLOSE_TRUSTLET_ACK  = 6,  /**&lt; Close Trustlet Ack; servers -&gt; IPCH */
    MSG_MAP                 = 7,  /**&lt; Map; driver &lt;-&gt; IPCH; */
    MSG_ERR_NOT             = 8,  /**&lt; Error Notification;  EXCH/SIQH -&gt; IPCH; */
    MSG_CLOSE_DRIVER        = 9,  /**&lt; Close driver; MSH -&gt; IPCH; IPCH -&gt; driver */
    MSG_CLOSE_DRIVER_ACK    = 10, /**&lt; Close driver Ack; driver -&gt; IPCH; IPCH -&gt; MSH */
    MSG_GET_DRIVER_VERSION  = 11, /**&lt; GetDriverVersion; client &lt;--&gt; IPCH */
    MSG_GET_DRAPI_VERSION   = 12, /**&lt; GetDrApiVersion; driver &lt;--&gt; IPCH */
    MSG_SET_NOTIFICATION_HANDLER    = 13, // Driver &lt;-&gt; IPCH
    MSG_DRV_NOT                     = 15, // Driver -&gt; Trustlet
    MSG_SET_FASTCALL_HANDLER        = 16, // Driver &lt;-&gt; IPCH
    MSG_GET_CLIENT_ROOT_AND_SP_ID   = 17, // Driver &lt;-&gt; IPCH
    MSG_CALL_FASTCALL               = 25, // DRIVER -&gt; IPCH -&gt; Kernel
    MSG_GET_CLI_UUID                = 26, // Driver &lt;-&gt; IPCH
    MSG_RQ_2                        = 27, // Client -&gt; Server
    MSG_MAP_VA_DIRECT               = 31, // DRIVER &lt;-&gt; IPCH
    MSG_MAP_PY_DIRECT               = 32, // DRIVER &lt;-&gt; IPCH
    MSG_UNMAP_PY_DIRECT             = 33, // DRIVER &lt;-&gt; IPCH
    MSG_GET_MEM_TYPE                = 34, // DRIVER &lt;-&gt; IPCH
    MSG_UNMAP_VA_DIRECT             = 35 // DRIVER &lt;-&gt; IPCH
`}` message_t;
```



## 十二、tlApi

```
ROM:07D0BE38 tlApi_syscall_table DCD tlApiNOP+1          ; 0
ROM:07D0BE38                 DCD tlApiGetVersion+1   ; 1
ROM:07D0BE38                 DCD tlApiGetMobicoreVersion+1; 2
ROM:07D0BE38                 DCD tlApiGetPlatformInfo+1; 3
ROM:07D0BE38                 DCD tlApiExit+1         ; 4
ROM:07D0BE38                 DCD tlApiLogvPrintf+1   ; 5
ROM:07D0BE38                 DCD tlApiWaitNotification+1; 6
ROM:07D0BE38                 DCD tlApiNotify+1       ; 7
ROM:07D0BE38                 DCD tlApi_callDriver+1  ; 8
ROM:07D0BE38                 DCD tlApiWrapObjectExt+1; 9
ROM:07D0BE38                 DCD tlApiUnwrapObjectExt+1; 10
ROM:07D0BE38                 DCD tlApiGetSuid+1      ; 11
ROM:07D0BE38                 DCD tlApiSecSPICmd+1    ; 12
ROM:07D0BE38                 DCD tlApiCrAbort+1      ; 13
ROM:07D0BE38                 DCD tlApiRandomGenerateData+1; 14
ROM:07D0BE38                 DCD tlApiGenerateKeyPair+1; 15
ROM:07D0BE38                 DCD tlApiCipherInitWithData+1; 16
ROM:07D0BE38                 DCD tlApiCipherUpdate+1 ; 17
ROM:07D0BE38                 DCD tlApiCipherDoFinal+1; 18
ROM:07D0BE38                 DCD tlApiSignatureInitWithData+1; 19
ROM:07D0BE38                 DCD tlApiSignatureUpdate+1; 20
ROM:07D0BE38                 DCD tlApiSignatureSign+1; 21
ROM:07D0BE38                 DCD tlApiSignatureVerify+1; 22
ROM:07D0BE38                 DCD tpiApiMessageDigestInitWithData+1; 23
ROM:07D0BE38                 DCD tlApiMessageDigestUpdate+1; 24
ROM:07D0BE38                 DCD tlApiMessageDigestDoFinal+1; 25
ROM:07D0BE38                 DCD tlApiGetVirtMemType+1; 26
ROM:07D0BE38                 DCD tlApiDeriveKey+1    ; 27
ROM:07D0BE38                 DCD tlApiMalloc+1       ; 28
ROM:07D0BE38                 DCD tlApiRealloc+1      ; 29
ROM:07D0BE38                 DCD tlApiFree+1         ; 30
(...)
ROM:07D0BE38                 DCD tlApiGetIDs+1       ; 43
(...)
ROM:07D0BE38                 DCD tlApiRandomGenerateData_wrap+1; 83
ROM:07D0BE38                 DCD tlApiCrash+1        ; 84
ROM:07D0BE38                 DCD tlApiEndorse+1      ; 85
ROM:07D0BE38                 DCD tlApiTuiGetScreenInfo+1; 86
ROM:07D0BE38                 DCD tlApiTuiOpenSession+1; 87
ROM:07D0BE38                 DCD tlApiTuiCloseSession+1; 88
ROM:07D0BE38                 DCD tlApiTuiSetImage+1  ; 89
ROM:07D0BE38                 DCD tlApiTuiGetTouchEvent+1; 90
ROM:07D0BE38                 DCD tlApiTuiGetTouchEventsLoop+1; 91
ROM:07D0BE38                 DCD tlApiDrmProcessContent+1; 92
ROM:07D0BE38                 DCD tlApiDrmOpenSession+1; 93
ROM:07D0BE38                 DCD tlApiDrmCloseSession+1; 94
ROM:07D0BE38                 DCD tlApiDrmCheckLink+1 ; 95
ROM:07D0BE38                 DCD tlApiDeriveKey_wrapper+1; 96
ROM:07D0BE38                 DCD tlApiUnwrapObjectExt_wrapper+1; 97
ROM:07D0BE38                 DCD tlApiGetSecureTimestamp+1; 98
```



## 十三、drApi

```
ROM:07D0C114 ; int drApi_syscall_table[62]
ROM:07D0C114 drApi_syscall_table DCD drApiGetVersion+1   ; 0
ROM:07D0C114                                         ; DATA XREF: get_syscall_fn+30↑o
ROM:07D0C114                                         ; ROM:off_7D0A9F8↑o
ROM:07D0C114                 DCD drApiExit+1         ; 1
ROM:07D0C114                 DCD drApiMapPhys+1      ; 2
ROM:07D0C114                 DCD drApiUnmap+1        ; 3
ROM:07D0C114                 DCD drApiMapPhysPage4KBWithHardware+1; 4
ROM:07D0C114                 DCD drApiMapClient+1    ; 5
ROM:07D0C114                 DCD drApiMapClientAndParams+1; 6
ROM:07D0C114                 DCD drApiAddrTranslateAndCheck+1; 7
ROM:07D0C114                 DCD drApiGetTaskid+1    ; 8
ROM:07D0C114                 DCD drApiTaskidGetThreadid+1; 9
ROM:07D0C114                 DCD drApiGetLocalThreadId+1; 10
ROM:07D0C114                 DCD drApiStartThread+1  ; 11
ROM:07D0C114                 DCD drApiStopThread+1   ; 12
ROM:07D0C114                 DCD drApiResumeThread+1 ; 13
ROM:07D0C114                 DCD drApiThreadSleep+1  ; 14
ROM:07D0C114                 DCD drApiSetThreadPriority+1; 15
ROM:07D0C114                 DCD drApiIntrAttach+1   ; 16
ROM:07D0C114                 DCD drApiIntrDetach+1   ; 17
ROM:07D0C114                 DCD drApiWaitForIntr+1  ; 18
ROM:07D0C114                 DCD drApiTriggerIntr+1  ; 19
ROM:07D0C114                 DCD drApiIpcWaitForMessage+1; 20
ROM:07D0C114                 DCD drApiIpcCallToIPCH+1; 21
ROM:07D0C114                 DCD drApiIpcSignal+1    ; 22
ROM:07D0C114                 DCD drApiIpcSigWait+1   ; 23
ROM:07D0C114                 DCD drApiNotify+1       ; 24
ROM:07D0C114                 DCD drApiSystemCtrl+1   ; 25
ROM:07D0C114                 DCD sub_7D0A2CE+1       ; 26
ROM:07D0C114                 DCD drApiVirt2Phys+1    ; 27
ROM:07D0C114                 DCD drApiCacheDataClean+1; 28
ROM:07D0C114                 DCD drApiCacheDataCleanAndInvalidate+1; 29
ROM:07D0C114                 DCD drApiNotifyClient+1 ; 30
ROM:07D0C114                 DCD drApiThreadExRegs+1 ; 31
ROM:07D0C114                 DCD drApiInstallFc+1    ; 32
ROM:07D0C114                 DCD drApiIpcUnknownMessage+1; 33
ROM:07D0C114                 DCD drApiIpcUnknownException+1; 34
ROM:07D0C114                 DCD drApiGetPhysMemType+1; 35
ROM:07D0C114                 DCD drApiGetClientRootAndSpId+1; 36
ROM:07D0C114                 DCD drApiCacheDataCleanRange+1; 37
ROM:07D0C114                 DCD drApiCacheDataCleanAndInvalidateRange+1; 38
ROM:07D0C114                 DCD drApiMapPhys64+1    ; 39
ROM:07D0C114                 DCD drApiMapPhys64_2+1  ; 40
ROM:07D0C114                 DCD drApiVirt2Phys64+1  ; 41
ROM:07D0C114                 DCD drApiGetPhysMemType64+1; 42
ROM:07D0C114                 DCD drApiUpdateNotificationThread+1; 43
ROM:07D0C114                 DCD drApiRestartThread+1; 44
ROM:07D0C114                 DCD drApiGetSecureTimestamp+1; 45
ROM:07D0C114                 DCD drApiFastCall+1     ; 46
ROM:07D0C114                 DCD drApiGetClientUuid+1; 47
ROM:07D0C114                 DCD sub_7D0A2AC+1       ; 48
ROM:07D0C114                 DCD drApiMapVirtBuf+1   ; 49
ROM:07D0C114                 DCD drApiUnmapPhys2+1   ; 50
ROM:07D0C114                 DCD drApiMapPhys2+1     ; 51
ROM:07D0C114                 DCD drApiUnmapVirtBuf2+1; 52
ROM:07D0C114                 DCD sub_7D07D76+1       ; 53
ROM:07D0C114                 DCD sub_7D0A558+1       ; 54
ROM:07D0C114                 DCD sub_7D0A574+1       ; 55
ROM:07D0C114                 DCD sub_7D0A5D6+1       ; 56
ROM:07D0C114                 DCD sub_7D0A738+1       ; 57
ROM:07D0C114                 DCD sub_7D0A1BA+1       ; 58
ROM:07D0C114                 DCD sub_7D0A1C8+1       ; 59
ROM:07D0C114                 DCD sub_7D0A5F4+1       ; 60
ROM:07D0C114                 DCD sub_7D0A60C+1       ; 61
```



## 十四、沙盒机制
1. 内核和RTM都会维持其自身到Trustlet或驱动的进程实例映射，并维持进程的虚拟地址空间映射。
1. 内核会对SVC调用者的类型进行检查，限制于驱动。RTM也会对IPC调用者的类型进行检查，同样限制于驱动。上述并不是一个核心机制，但必须针对每个案例正确执行。这一点，类似于Linux上的access_ok()检查。
1. 这二者共同防止了将其他Trustlet的虚拟内存或任何物理内存（包括不安全世界）映射到驱动的可能性。但驱动仍然不能映射RWX内存，也不能在自己的代码页映射任何内容。
1. 驱动程序可以使用SVC，从内核获取并得到发出当前请求Trustlet的UUID。这样可以用来过滤哪些客户端（Trustlet）应该被允许访问驱动的功能。
1. 驱动可以使用SVC，将不安全世界或安全世界的物理内存映射到其地址空间，也可以使用SVC来注册自定义的快速调用处理器，使其能够直接从安全世界的EL1执行代码。实际上，这使得驱动拥有和安全世界EL1一样的特权。


## 十五、漏洞利用缓解措施（Trustlet和驱动）
1. 分为RX代码页和RW数据页；
1. 使栈/bss段/堆之间没有界限；
1. 映射到Trustlet的WSM和映射到驱动的Trustlet内存，应该存储于独立的内存区域中；
1. 关闭Stack Canaries保护机制，关闭ASLR保护机制。
原文链接：<br>
[1] [https://medium.com/taszksec/unbox-your-phone-part-i-331bbf44c30c](https://medium.com/taszksec/unbox-your-phone-part-i-331bbf44c30c)<br>
[2] [https://medium.com/taszksec/unbox-your-phone-part-ii-ae66e779b1d6](https://medium.com/taszksec/unbox-your-phone-part-ii-ae66e779b1d6)
