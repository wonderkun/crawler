> 原文链接: https://www.anquanke.com//post/id/85770 


# 【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 4）


                                阅读量   
                                **99753**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：improsec.com
                                <br>原文地址：[https://improsec.com/blog//windows-kernel-shellcode-on-windows-10-part-4-there-is-no-code](https://improsec.com/blog//windows-kernel-shellcode-on-windows-10-part-4-there-is-no-code)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p0.ssl.qhimg.com/t01eb3879cd70e32f3f.jpg)](https://p0.ssl.qhimg.com/t01eb3879cd70e32f3f.jpg)**

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**



**传送门**

[**【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 1）**](http://bobao.360.cn/learning/detail/3575.html)

[******【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 2）**](http://bobao.360.cn/learning/detail/3593.html)

[**【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 3）******](http://bobao.360.cn/learning/detail/3624.html)



**0x00 前言**

本文是对之前3篇关于Windows内核shellcode的补充。你能阅读之前的文章，part1，part2和part3。

在我之前的文章中有个假设是能够在内核上下文中执行任意汇编代码。从一个write-what-where漏洞得到这个是可能的，且经常来自于内存池溢出，它需要一个内核读写原语和绕过KASLR。如果我们只想使用读写原语来执行数据攻击，我们可以省略绕过KASLR。本文描述了3中方法，每种都可以转化为数据攻击，而不是shellcode。

在我们开始之前，需要一个内核读写原语，幸运的是，在我之前的一篇文章中介绍了如何在Windows 10周年纪念版或更新版本中滥用tagWnd结构。基于这个利用技术，任何其他的内核读写原语都能实现。还应该注意的是tagWnd利用原语没有被win32k系统调用过滤机制阻止，因此在IE和Edge中都能使用。

<br>

**0x01 窃取令牌**

令牌窃取的shellcode在第一篇文章中有介绍，通过从GS寄存器中获取KTHREAD的地址。在这里我们遇到一个问题，因为我们不能使用一个读原语读取这个。很幸运，我们能在tagWnd对象中找到，Windows 10没有发布tagWnd的符号，但是ReactOS有Windows XP 32位的这个结构的描述，因此我们希望翻译为我们自己的。TagWnd对象起始于下面的结构：

[![](https://p5.ssl.qhimg.com/t01b2e8e64b39d69d58.png)](https://p5.ssl.qhimg.com/t01b2e8e64b39d69d58.png)

下面是THRDESKHEAD的结构：

[![](https://p1.ssl.qhimg.com/t01a9dbfdfb509de204.png)](https://p1.ssl.qhimg.com/t01a9dbfdfb509de204.png)

在其中包含了另一个THROBJHEAD结构：

[![](https://p5.ssl.qhimg.com/t010e3992b318ddb631.png)](https://p5.ssl.qhimg.com/t010e3992b318ddb631.png)

第二个参数指向THREADINFO结构：

[![](https://p4.ssl.qhimg.com/t01272d505b7a39f60d.png)](https://p4.ssl.qhimg.com/t01272d505b7a39f60d.png)

W32THREAD结构如下：

[![](https://p0.ssl.qhimg.com/t011b2141edd5a790d6.png)](https://p0.ssl.qhimg.com/t011b2141edd5a790d6.png)

这意味着我们能得到一个指向ETHREAD的指针。总结下，我们使用用户模式下映射的桌面堆泄露了tagWnd对象的地址。从tagWnd对象的地址看，我们使用读原语来读取偏移0x10处的DWORD值，以便得到THREADINFO结构的指针。然后我们读取偏移0处的值，得到ETHREAD的指针。Windbg显示如下：

[![](https://p1.ssl.qhimg.com/t0169c6b6a8ea3c8d32.png)](https://p1.ssl.qhimg.com/t0169c6b6a8ea3c8d32.png)

在这个例子中，tagWnd对象位于0xfffff1b0407afe90，在两次读取后，我们有了KTHREAD，但是为了证明它，我们读取其偏移0x220处的值，以为那是EPROCESS的地址，然后我们能验证。

现在，我们有方法读取EPROCESS的地址了。实现如下：

[![](https://p2.ssl.qhimg.com/t011e0e027b770a3a9d.png)](https://p2.ssl.qhimg.com/t011e0e027b770a3a9d.png)

窃取令牌的shellcode如下：

[![](https://p5.ssl.qhimg.com/t018f19c8513950009d.png)](https://p5.ssl.qhimg.com/t018f19c8513950009d.png)

从汇编转化为数据读写的步骤如下：

获取父进程的PID

定位父进程的EPROCESS

定位系统进程的EPROCESS

覆写父进程的令牌

第一步很简单，只要读取当前EPROCESS的偏移0x3E0：

[![](https://p2.ssl.qhimg.com/t01fa1d4c8b2fc997c1.png)](https://p2.ssl.qhimg.com/t01fa1d4c8b2fc997c1.png)

接下来，遍历EPROCESS，直到在偏移0x2E8处找到PPID：

[![](https://p4.ssl.qhimg.com/t01afdbe15c5d86ff49.png)](https://p4.ssl.qhimg.com/t01afdbe15c5d86ff49.png)

然后是系统进程的EPROCESS：

[![](https://p4.ssl.qhimg.com/t01acf3298187d485fd.png)](https://p4.ssl.qhimg.com/t01acf3298187d485fd.png)

最后得到令牌的地址，并在父进程中的EPROCESS覆写它：

[![](https://p4.ssl.qhimg.com/t01409064c15db88919.png)](https://p4.ssl.qhimg.com/t01409064c15db88919.png)

运行，手动修改tagWnd的cbwndExtra字段，模拟一个write-what-where漏洞，得到如下结果：

[![](https://p0.ssl.qhimg.com/t016235b5cd45194282.png)](https://p0.ssl.qhimg.com/t016235b5cd45194282.png)

因此不需要执行内核shellcode也能做到同样的事。

<br>

**0x02 编辑ACL**

第二个方法是编辑winlogon.exe进程的安全描述符中的DACL的SID，以及当前进程的MandatoryPolicy。这允许程序注入一个线程到winlogon.exe进程中，并且以SYSTEM权限运行一个cmd.exe。shellcode如下：

[![](https://p0.ssl.qhimg.com/t01f3811da63ff931ad.png)](https://p0.ssl.qhimg.com/t01f3811da63ff931ad.png)

下面是转化的步骤：

找到当前进程的EPROCESS

找到winlogon进程的EPROCESS

修改winlogon的DACL

修改当前进程的令牌

我们和之前一样找到当前进程的EPROCESS：

[![](https://p1.ssl.qhimg.com/t01624722f258363cab.png)](https://p1.ssl.qhimg.com/t01624722f258363cab.png)

然后，我们通过搜索名字找到winlogon进程的EPROCESS：

[![](https://p1.ssl.qhimg.com/t019a2e2ecc9d3b47c3.png)](https://p1.ssl.qhimg.com/t019a2e2ecc9d3b47c3.png)

然后在安全描述符的偏移0x48处修改winlogon进程的DACL：

[![](https://p2.ssl.qhimg.com/t01b726d748a6cf6e43.png)](https://p2.ssl.qhimg.com/t01b726d748a6cf6e43.png)

因为利用原语只能读写QWORD，我们在0x48处读取整个QWORD并修改它，然后写回。最后我们使用相同方法修改当前进程的令牌：

[![](https://p1.ssl.qhimg.com/t01d4d656111d06ff31.png)](https://p1.ssl.qhimg.com/t01d4d656111d06ff31.png)

运行PoC，再次手动修改tagWnd的cbwndExtra字段，模拟一个write-what-where漏洞，得到如下结果：

[![](https://p2.ssl.qhimg.com/t01f4cac1a88630a4a0.png)](https://p2.ssl.qhimg.com/t01f4cac1a88630a4a0.png)

<br>

**0x03 开启特权**

最后一个技术是开启父进程中所有的特权，汇编代码如下：

[![](https://p3.ssl.qhimg.com/t018c1347eb08dfbe0b.png)](https://p3.ssl.qhimg.com/t018c1347eb08dfbe0b.png)

第一部分的代码是窃取令牌的shellcode，首先找到当前进程的EPROCESS，然后使用它找到父进程的EPROCESS，代码如下：

[![](https://p2.ssl.qhimg.com/t01d5f21ae100617286.png)](https://p2.ssl.qhimg.com/t01d5f21ae100617286.png)

接下来找令牌，忽略参考位，在偏移0x48处设置0xFFFFFFFFFFFFFFFF：

[![](https://p0.ssl.qhimg.com/t013837b2941db72235.png)](https://p0.ssl.qhimg.com/t013837b2941db72235.png)

再次手动修改tagWnd的cbwndExtra字段，模拟一个write-what-where漏洞，得到如下结果：

[![](https://p1.ssl.qhimg.com/t01af30dfbcd49f4e74.png)](https://p1.ssl.qhimg.com/t01af30dfbcd49f4e74.png)

运行PoC，因为高特权级我们能注入到winlogon中：

[![](https://p2.ssl.qhimg.com/t018a3df57f64803b38.png)](https://p2.ssl.qhimg.com/t018a3df57f64803b38.png)

<br>

**0x04 结语**

上述包含了内核shellcode到数据攻击的转化，对于将标准特权提升到SYSTEM，不需要执行内核shellcode，也不需要绕过KASLR。

<br>



**传送门**

[**【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 1）**](http://bobao.360.cn/learning/detail/3575.html)

[******【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 2）**](http://bobao.360.cn/learning/detail/3593.html)

[**【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 3）******](http://bobao.360.cn/learning/detail/3624.html)

<br>
