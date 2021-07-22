> 原文链接: https://www.anquanke.com//post/id/85735 


# 【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 3）


                                阅读量   
                                **89184**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：improsec.com
                                <br>原文地址：[https://improsec.com/blog//windows-kernel-shellcode-on-windows-10-part-3](https://improsec.com/blog//windows-kernel-shellcode-on-windows-10-part-3)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01eb3879cd70e32f3f.jpg)](https://p4.ssl.qhimg.com/t01eb3879cd70e32f3f.jpg)

****

翻译：[金乌实验室](http://bobao.360.cn/member/contribute?uid=2818394007)

预估稿费：100RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**[<strong style="font-size: 18px">**](http://bobao.360.cn/learning/detail/3575.html)</strong>

**<br>**

**传送门**

[**【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 1）**](http://bobao.360.cn/learning/detail/3575.html)

[******【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 2）**](http://bobao.360.cn/learning/detail/3593.html)

[**【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 4）**](http://bobao.360.cn/learning/detail/3643.html)



**前言**

这篇文章是Windows内核shellcode系列的第三篇，在这篇文章中我们探讨Cesar Cerrudo在2012年Black Hat上提出的三种方法中的最后一种方法—启用权限，我们专注于进程token中的权限。（本系列的第一篇文章探讨的是替换进程token，地址是[链接](https://improsec.com/blog/windows-kernel-shellcode-on-windows-10-part-1)；第二篇文章探讨的是清除ACL，地址是[链接](https://improsec.com/blog/windows-kernel-shellcode-on-windows-10-part-2)）。

<br>

**分析**

前两篇文章中使用的假设同样适用于本篇文章，即假设漏洞利用已获得任意内核模式代码执行，我们可以手动运行汇编代码。启用权限技术非常简单明了，但是应用却并不广泛。其理念是定位cmd.exe进程的token，或者是任何获得提升权限的进程，并修改已经启用的权限。

查看Token对象的结构，我们发现：

[![](https://p3.ssl.qhimg.com/t01b897b362706bbe6e.png)](https://p3.ssl.qhimg.com/t01b897b362706bbe6e.png)

_SEP_TOKEN_PRIVILEGES结构位于offset 0x40处，正如Cesar所描述的。深入探查后我们发现：

[![](https://p0.ssl.qhimg.com/t0135ce01ba48de41ac.png)](https://p0.ssl.qhimg.com/t0135ce01ba48de41ac.png)

仍然是完全相同的布局，因此可以得出这种技术的背景并没有改变。我们需要修改进程token中的offset 0x48，以启用所述进程的权限。

<br>

**The Shellcode**

我们用和前两次相同的方式开始，即从GS寄存器中找到KTHREAD，然后从KTHREAD的offset 0x220处找到EPROCESS：

[![](https://p4.ssl.qhimg.com/t015379dfc5e9f4546e.png)](https://p4.ssl.qhimg.com/t015379dfc5e9f4546e.png)

我想启用parent进程的权限，也就是cmd.exe进程。当我从一个独立的二进制启动漏洞利用时，我找到了cmd.exe的EPROCESS。方法如该系列的第一篇文章中描述的那样，parent进程的PID位于EPROCESS中的offset 0x3E0处：

[![](https://p4.ssl.qhimg.com/t01cdc1a1d96ee06bf0.png)](https://p4.ssl.qhimg.com/t01cdc1a1d96ee06bf0.png)

一旦我们找到了EPROCESS，我们就能在offset 0x358处找到指向token的指针，记住指针是一个快速引用，所以低4位应该被忽略。然后我们更改offset 0x48的值，以启用我们想要的所有权限：

[![](https://p3.ssl.qhimg.com/t01db92d56cffcdf124.png)](https://p3.ssl.qhimg.com/t01db92d56cffcdf124.png)

运行shellcode，从whoami / all得到以下输出：

[![](https://p0.ssl.qhimg.com/t011c81ce68fd85b7b2.png)](https://p0.ssl.qhimg.com/t011c81ce68fd85b7b2.png)

我们启用了很多权限，这里只列出了目前存在的权限。当我们启动子进程的时候，它继承了parent进程的权限，这意味着如果我们启动一个应用程序将代码注入到一个特权进程，例如winlogon.exe，我们可以创建一个新的SYSTEM integrity cmd.exe：

[![](https://p2.ssl.qhimg.com/t01a7d1e3e6c61a6321.png)](https://p2.ssl.qhimg.com/t01a7d1e3e6c61a6321.png)

我们能够使用可用的权限做更多的事情。完整的汇编代码可以在GitHub上找到 （地址）。

<br>

**结语**

至此，这个系列的文章就完结了。总结一句话就是，Cesar Cerrudo在2012年提出的想法和技术，只要做一些修改，在2017年仍然适用。

<br>



**传送门**

[**【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 1）**](http://bobao.360.cn/learning/detail/3575.html)

[******【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 2）**](http://bobao.360.cn/learning/detail/3593.html)

[**【技术分享】探索基于Windows 10的Windows内核Shellcode（Part 4）**](http://bobao.360.cn/learning/detail/3643.html)

<br>
