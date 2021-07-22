> 原文链接: https://www.anquanke.com//post/id/86472 


# 【技术分享】Source游戏中的远程代码执行漏洞的分析


                                阅读量   
                                **74488**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：oneupsecurity.com
                                <br>原文地址：[https://oneupsecurity.com/research/remote-code-execution-in-source-games](https://oneupsecurity.com/research/remote-code-execution-in-source-games)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t014630b8063217c38d.jpg)](https://p1.ssl.qhimg.com/t014630b8063217c38d.jpg)**

****

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=877906634)

预估稿费：140RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**0x00 前言**

****

Valve的Source SDK包含了一个缓冲区溢出漏洞，其导致在客户端和服务器上能执行任意代码。这个漏洞在射杀玩家时触发，其能导致加载特定的布娃娃模型(ragdoll model)。多个Source游戏在2017年6月更新修复了这个漏洞。包括[CS:GO](http://blog.counter-strike.net/index.php/2017/06/18895/), [TF2](http://store.steampowered.com/news/30157/), [Hl2:DM](http://store.steampowered.com/news/30120/), [Portal 2](http://store.steampowered.com/news/30443/), [L4D2](http://store.steampowered.com/news/30445/)。我们感谢Valve非常负责，并迅速处理了漏洞。Valve一天内就修复并发布了更新。





**0x01 缺少边界检查**

****

****函数nexttoken用于令牌化一个字符串。我们可以注意到， 只要找不到NULL字符或者分隔符sep，就会导致str这个buffer被复制到token这个buffer中。根本就没有边界检查。

```
const char *nexttoken(char *token, const char *str, char sep)
`{`
    ...
    while ((*str != sep) &amp;&amp; (*str != ''))
    `{`
        *token++ = *str++;
    `}`
    ...
`}`
```

出处链接：

[https://github.com/ValveSoftware/source-sdk-2013/blob/f56bb35301836e56582a575a75864392a0177875/mp/src/game/client/cdll_util.cpp#L744-L747](https://github.com/ValveSoftware/source-sdk-2013/blob/f56bb35301836e56582a575a75864392a0177875/mp/src/game/client/cdll_util.cpp#L744-L747)



**0x02 漏洞点**

当处理布娃娃模型数据时（如一个玩家被射杀），类CRagdollCollisionRulesPars的方法ParseKeyValue会被调用。这个方法调用nexttoken来令牌化那些待进一步处理的规则。通过构造一个超过256字符的collisionpair规则，缓冲区szToken就会溢出。因szToken存储在栈上，所以ParseKeyValue的返回地址将被覆盖。

```
class CRagdollCollisionRulesParse : public IVPhysicsKeyHandler
`{`
    virtual void ParseKeyValue( void *pData, const char *pKey, const char *pValue )
    `{`
        ...
        else if ( !strcmpi( pKey, "collisionpair" ) )
            ...
            char szToken[256];
            const char *pStr = nexttoken(szToken, pValue, ',');
            ...
    `}`
`}`
```

出处链接：

[https://github.com/ValveSoftware/source-sdk-2013/blob/f56bb35301836e56582a575a75864392a0177875/mp/src/game/shared/ragdoll_shared.cpp#L92-L95](https://github.com/ValveSoftware/source-sdk-2013/blob/f56bb35301836e56582a575a75864392a0177875/mp/src/game/shared/ragdoll_shared.cpp#L92-L95)



**0x03 绕过缓解措施**

****

[ASLR](https://en.wikipedia.org/wiki/Address_space_layout_randomization)（Address Space Layout Randomization, 地址空间布局配置随机加载）是针对内存破环漏洞的强有力的缓解措施，它会将可执行文件加载到内存中的地址随机化。这个功能是可选的，并且一个进程内所有加载到内存的可执行文件必须开启这个功能才能使其生效。

动态库steamclient.dll没有开启ASLR。这意味着steamclient.dll加载到内存中的地址是可预测的。这使得能方便地定位并使用可执行文件内存中的指令。



**0x04 收集ROP gadget**

[ROP](https://en.wikipedia.org/wiki/Return-oriented_programming)(Return Oriented Programming)是一种允许通过重用程序中已存在的指令来创建shellcode的技术。简言之，你能找到一系列retn指令结尾的指令。你把ROP链的第一条指令的地址插入到栈上，当函数返回地址被pop到指令寄存器时，指令就会被执行。因为x86和x64指令不需要内存对齐，任何地址都能作为指令，于是我们可以把指令指针指向一条指令的中间，这样就可以使用更多的指令。

Immunity Debugger插件[Mona](https://www.corelan.be/index.php/2011/07/14/mona-py-the-manual/)提供了查找gadget的工具。但是这个插件无法找到所有有用的gadget，如rep movs。



**0x05 启动cmd.exe**

****

由于payload的处理方式原因，NULL字符不能使用，并且大写字符需要转化为小写字符。这意味着我们的ROP gadget地址资源有限，我们的payload中其他数据也是。为了绕过这个，可以用一个gadget链来引导shellcode，用来定位内存中未修改的原始缓冲区。然后将未修改的payload通过rep movs gadget复制回栈。

Steamclient.dll导入了LoadLibraryA和GetProcAddressA。这使得我们能加载任意DLL到内存中，并且得到其他的导出函数。我们导入shell32.dll以获得ShellExecuteA函数，这个函数能启动其他程序。

为了第三方有时间更新游戏，PoC会在30天后发布。Source的开发者可以使用下面的[补丁](https://oneupsecurity.com/research/remote-code-execution-in-source-games?t=r#recommended-fix)。



**0x06 提供payload**

****

[![](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p2.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)Source引擎允许将自定义内容打包到地图文件中，通常情况下，这样可以用来在地图中添加一些额外的内容，比如声音或者文字。于是我们可以将布娃娃模型文件打包到一个地图文件中，而且使用与原始布娃娃模型文件一样的路径，但是使用的是我们的版本。

<br>

**0x07 修复建议**



为了防止缓冲区溢出发生，不要在缓冲区中存储它所容纳不了的过多的数据。nexttoken函数应该有一个token长度，来作为参数，这个参数用来进行边界检查。Source游戏的开发者可以使用下面的[补丁](https://oneupsecurity.com/research/blog/hl2-rce/nexttoken.patch)。为了缓解内存破环漏洞，就要为所有的模块开启ASLR。在构建过程中自动检查确保所有的模块开启了ASLR。可以使用chromium团队开发的checkbins.py工具来完成。另外，Source游戏应该被沙箱化以限制访问资源，并阻止新进程的启动。比如，当利用web浏览器的内存破环漏洞时经常会使用内核利用，因为用户层的浏览器进程是受限的，这就可以作为一个很好的沙箱化的例子。更多信息参考[chromium的沙箱实现](https://chromium.googlesource.com/chromium/src/+/master/docs/design/sandbox.md)。

下载补丁：

[https://oneupsecuritycdn-8266.kxcdn.com/static/blog/hl2-rce/nexttoken.patch](https://oneupsecuritycdn-8266.kxcdn.com/static/blog/hl2-rce/nexttoken.patch)

 

**0x08 总结**

视频游戏很容易成为漏洞利用的目标，这不仅是从技术上来说，从逻辑上来说也是这样。 因为视频游戏通常出现在员工的家中或者工作环境中，漏洞利用就可以能通过这种场景，进入到公司或者家中的私有网络。另外，在流行的视频游戏中发现一个远程代码执行漏洞可以用来创建僵尸网络或者传播勒索软件。

至于缓解措施嘛，游戏其实就不该安装在用于工作的设备中。游戏机器应该移到不受信的网络中，并且工作设备不应该连接到这个不受信的网络。

对那些Source的玩家而言，需要禁用第三方内容的下载以减少攻击面。通过命令cl_allowdownload 0 和 cl_downloadfilter all就可以实现禁用第三方内容下载。

另外，因为在Source SDK中发现了漏洞，我们可以推测，在其他的第三方模块很可能也是有漏洞的。但是如果我们对所有模块启用ASLR，这样就需要有内存泄漏漏洞才能利用了，从而加大了漏洞利用的难度。
