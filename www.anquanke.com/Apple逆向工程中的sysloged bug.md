> 原文链接: https://www.anquanke.com//post/id/83375 


# Apple逆向工程中的sysloged bug


                                阅读量   
                                **69802**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://reverse.put.as/2016/01/22/reversing-apples-syslogd-bug/](https://reverse.put.as/2016/01/22/reversing-apples-syslogd-bug/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01db36c099f4be2fa5.jpg)](https://p0.ssl.qhimg.com/t01db36c099f4be2fa5.jpg)

两天前,苹果公司(Apple)发布了OS X El Capitan(Mac OS)的10.11.3更新版,同时更新了Yosemite和Mavericks两款Mac操作系统的安全服务。(Yosemite:OS X Yosemite(优胜美地)是2014年6月苹果在全球开发者大会—WWDC 2014,发布的新一代Mac操作系统,版本号为10.10;Mavericks:OS X Mavericks(冲浪湾)是苹果在2013年WWDC发布的OS X 操作系统,版本号为10.9)在发布的公告中,Apple提到了其中存在的9个安全问题。他们之中的大多数都涉及内核或IOKit驱动。最后一个是关于syslog的内存泄漏问题。当黑客攻入某一台Mac时,它可让黑客利用Mac中的root特权来实施管制代码执行(arbitrary code execution)。我对这个bug很感兴趣的原因是,它涉及到了一个叫 syslog日志维护进程。

这篇文章介绍的是如何找到该漏洞并进行防护。非常不幸的是,对于安全服务更新的说明,苹果公司只是一笔带过,并没有给出更多具体的描述。比如:在默认的OS X安装程序中,是否存在该bug,会被黑客利用;或是需要某些特定条件,才能利用该bug。苹果公司对这些疑问都没有给出相应的说明。接下来我们将会看到,在默认的OS X安装程序中,根本无法利用该bug。

苹果公司都对许多OS X中组件的源代码进行了开源,但很多时候,这些源代码在发布时间上,都会有明显的推迟。于是我们需要使用二进制的diff命令,来找出更新文件和漏洞文件之间的差异。我们通常选用的工具是BinDiff,但也有另一种选择,就是由Joxean Koret开发的工具—Diaphora。这两者都需要用到IDA(IDA:源码恢复反汇编静态分析工具,是一个极好的反汇编工具。)而在本文中,我们将会用到的是Diaphora。为此,我们需要一个漏洞文件的副本和补丁文件的副本。最简单的获取方法就是:在更新安装之前,将syslogd日志文件进行复制。(该文件所在路径:/usr/sbin/syslogd)(通常在虚拟机上,保存每个版本的快照,也是一个不错的选择)或是从El Capitan,Yosemite,Mavericks的更新安装包中提取新的文件。本文将会重点介绍Yosemite文件。

生成一个数据库,并比较其存储内容,这就是Diaphora的工作原理。通过Diaphora,对10.11.2和10.11.3两个版本的syslogd文件进行比较,我们会得到下面这样一个警告:

[![](https://p2.ssl.qhimg.com/t0139287ec3eeb0cf97.png)](https://p2.ssl.qhimg.com/t0139287ec3eeb0cf97.png)

上图显示,这两个文件极其的相似,要求我们要找出其中最细微的差别。而到目前为止,我们只发现了一个变化,它的输出过程如下:

[![](https://p1.ssl.qhimg.com/t01254844d39e200d70.png)](https://p1.ssl.qhimg.com/t01254844d39e200d70.png)

这实在是很微妙的差别。类似的源代码如下:

reallocf(pointer, value + 4);

类似补丁文件代码:

reallocf(pointer, value * 4 + 4);

El Capitan 10.11.2的syslogd源代码包可在后面这个地址下载到(https://www.opensource.apple.com/tarballs/syslog/syslog-322.tar.gz)。定位这个函数的最简单方法就是,调用grep函数,来查找到这样一个字符串:“add_lockdown_session: realloc failedn”,点击syslogd.tproj/dbserver.c.,进行查看。该函数的源代码如下:

[![](https://p0.ssl.qhimg.com/t0149a93888754b3158.png)](https://p0.ssl.qhimg.com/t0149a93888754b3158.png)

利用上述函数实现的功能,我们可以更容易地对漏洞进行研究。补丁是放在分配了大小的reallocf()中。当触发漏洞时,fd变量就会被写入锁定会话的fds数组中。在reallocf()中分配的内存空间是错误的,因为它只是为一些锁定会话提供了内存空间,而并不是为每一个会话提供足够的内存空间。下图展示的是来自Zimperium的分析,完美地展示了堆溢出和堆损坏的过程。

[![](https://p3.ssl.qhimg.com/t0178aecbc6d11e5735.png)](https://p3.ssl.qhimg.com/t0178aecbc6d11e5735.png)

在他的示例中,进行第三次连接时,就发生了堆损坏。而在我的测试中,多次连接之后,才会发生堆损坏。(相比于Zimperium,在我绝大部分的测试时间里,都遇到了这种系统崩溃的情况,并且是在不同情况下的测试中发生的,但同时我也对OS X进行了测试)。

开发人员在编写这页代码时,犯了一个小错误。通过简单地添加一组括号就能解决该错误。

[![](https://p0.ssl.qhimg.com/t01adc7d47cf128726b.png)](https://p0.ssl.qhimg.com/t01adc7d47cf128726b.png)

Tip:C语言的功能是很强大,但作为一个开发人员,犯了这种语言错误,就可以说是很不应该的了。

到此,我们就已经知道了这个漏洞在哪儿,以及如何进行修复。接下来的问题就是,我们如何实现这个功能。以下是部分添加锁定会话的调用图:

[![](https://p2.ssl.qhimg.com/t0131eeec8e8ac1b9a6.png)](https://p2.ssl.qhimg.com/t0131eeec8e8ac1b9a6.png)

从最初的函数名来判断,该漏洞攻击可以通过本地(unix socket)或是通过TCP socket远程实现。在安全公告中,提到的是来自本地用户的攻击。官方是说,可在/System/Library/LaunchDaemons/com.apple.syslogd.plist路径下进行查看配置。我们只能对syslog unix socket进行了研究:

[![](https://p3.ssl.qhimg.com/t0196e6db5b6ba90b76.png)](https://p3.ssl.qhimg.com/t0196e6db5b6ba90b76.png)

这表明,除非用户操作不当,才会产生漏洞。而一般情况下,在OS X的默认配置中是不存在漏洞的。 不幸的是,苹果公司在公告中并没有提到这一点。这就让人感到很滑稽。特别是对于那些还在用着无法更新的老系统的苹果用户来说,更是如此。我们需要进行更深层次的研究,弄清怎么样才能在OS X中激活这一特性。因而我们尝试着复制这个漏洞。远程acceptmsg tcp()函数看似是一个不错的选择。在查看了源代码之后,我们会发现,该函数实现的一个有趣功能:

[![](https://p5.ssl.qhimg.com/t0190fa2b8a231c67d3.png)](https://p5.ssl.qhimg.com/t0190fa2b8a231c67d3.png)

这个就是能够激活远程功能的函数,它能让我们获得漏洞代码。“#ifdef”的功能是,让我们可以通过检查二进制,来校对我们是否将其转换为最终的二进制。

[![](https://p3.ssl.qhimg.com/t016cb59d583c5bc9d1.png)](https://p3.ssl.qhimg.com/t016cb59d583c5bc9d1.png)

将远程函数remote_init()的结果进行分开输出,表明只有tcp()函数是被编译了的。这就意味着我们能在本地或者远程,根据用户配置的相关信息,利用tcp嵌套函数来获取漏洞代码。远程tcp函数负责创建和绑定监听接口,即:一个叫做acceptmsg tcp的函数。我们在第一张使用了多线程优化技术(Grand Central Dispatch)的图中可以看到

[![](https://p5.ssl.qhimg.com/t01eee24fcd8389c41a.png)](https://p5.ssl.qhimg.com/t01eee24fcd8389c41a.png)

然而,我们仍就不知道如何激活远程功能。下一步就是研究下远程init函数。它有两个方面的内容,其中最有趣的是初始化模块init modules()。

[![](https://p4.ssl.qhimg.com/t010dfef2f47cb23bc0.png)](https://p4.ssl.qhimg.com/t010dfef2f47cb23bc0.png)

如果当攻击目标不是iOS模拟器,或是远程局部变量决定默认设置的启用状态时,远程模块提供的支持就能够被编译成二进制的syslodg文件。其默认值为零,这意味着远程功能默认为是禁用的。这就是另一个证据,证明在默认的OS X配置中不存在漏洞。

最后,初始化模块被主函数调用。我们在主函数中可以找到,如何激活这一特性的最后线索。

[![](https://p3.ssl.qhimg.com/t01894a6d7b1dd1fd04.png)](https://p3.ssl.qhimg.com/t01894a6d7b1dd1fd04.png)

在主函数中,我们发现一些有趣的事情,并能够最终确定OS X的默认安装程序是否真的存在漏洞。首先,我们可以看出:以上代码实现的就是,可在嵌入式操作系统中,启用默认的远程功能,比如在Apple TV中就有该功能。在iPhone中,如果你想使用这一功能,那么还要进行一个选项配置。最后一个是非法远程命令行选项,它的功能是在任何的苹果操作系统中,都可以启用远程特性。

为了激活这个功能,我们需要编辑syslogd运行的配置文件(建立在这个路径下:/System/Library/LaunchdDaemons/com.apple.syslogd.plist,通常为二进制格式,但可以使用plutil转换,将文件名转换为xml1。)程序说明和接口字键的修改如下:

[![](https://p0.ssl.qhimg.com/t01b4199b420ad6a6d6.png)](https://p0.ssl.qhimg.com/t01b4199b420ad6a6d6.png)

因为运行选项控制着接口,就需要我们对含有远程监听syslogd的接口,进行配置。(定义了一个ASL远程203端口)在重新定义功能和载入syslogd文件之后,我们就可以连接到203端口了。

[![](https://p0.ssl.qhimg.com/t012ee6b071c6f0f3eb.png)](https://p0.ssl.qhimg.com/t012ee6b071c6f0f3eb.png)

漏洞是通过使用watch命令来触发。如果我们在带有锁定会话的代码中,加上一个代码调试器和一个代码断点, 当我们使用watch命令时,在断点处就无法进行代码修改,命令也无法执行。这个代码实现的就是这个功能。

[![](https://p5.ssl.qhimg.com/t01770c179974c2de16.png)](https://p5.ssl.qhimg.com/t01770c179974c2de16.png)

watch解锁只在该会话的一个地方进行了设置:

[![](https://p3.ssl.qhimg.com/t011beaaa558979502f.png)](https://p3.ssl.qhimg.com/t011beaaa558979502f.png)

会话锁定标识是该会话模块中的唯一会话参数传递标识。

我们终于可以得出结论:为什么在安全公告中会提到本地用户了。

[![](https://p3.ssl.qhimg.com/t0154e0c6d2ea7d003b.png)](https://p3.ssl.qhimg.com/t0154e0c6d2ea7d003b.png)

这意味着会话锁定标识只设置在了本地连接中,而不在远程tcp连接中。这就是我们在OS X syslogd文件中要实现的特性。远程调用函数acceptmsg()很好地说明了这一点。

[![](https://p0.ssl.qhimg.com/t01c3b3a352ab1d1e39.png)](https://p0.ssl.qhimg.com/t01c3b3a352ab1d1e39.png)

结论为:即使用户配置了远程功能,在OS X中也没有代码路径来触发这个bug。测试这个bug的唯一方法就是,添加syslogd文件(或者打补丁)以及删除上述条件(我们也可以在会话中打补丁,这要更容易些。)接下来,我们就只需要一台小型的tcp服务器,能给203端口发送连接请求和watch命令。但最终,syslogd文件会失效。

当然,要进一步研究这个漏洞,也不是很容易的事。因为我们还没有完全掌握fd这个变量的用法。一旦错误使用,它就会对原来的数组进行重新分配,导致日志文件出错。

最后一点是,El Capitan中的漏洞已经被修复了,而在Yosemite和Mavericks更新的安全服务中,该漏洞还没有被修复。我们之前所见的是,在El Capitan中没有相应漏洞代码的执行路径,但奇怪的是,在以前的旧版本上,也没有打代码补丁。在很多时候,苹果公司的安全维护措施,实在是让人感到费解。

文章行至结尾,我们可以得出结论:在OS X的这个漏洞(sysloged bug)上,实在没有太多让人兴奋的兴奋点,同时对于iOS开发来说,这也不算是一个很大的障碍。它只是一个有趣的反向工程和一次源代码分析训练而已,能够帮助我们在OS X上更好地理解漏洞带来的威胁。如果苹果公司能在其安全服务公告中,披露更多的相关细节,我们也就没必要来进行这次代码训练了。

感谢pmsac和qwertyoruiop对草案发布评审工作的支持,并提供了开发讨论的机会。

另注:生成调用图的工具是来自http://www.scitools.com. 。它是在浏览和审核大型项目时,可以给予你很大帮助的一款工具。
