> 原文链接: https://www.anquanke.com//post/id/181794 


# CVE‑2019‑1132：利用Windows 0day的攻击活动


                                阅读量   
                                **204928**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者welivesecurity.com，文章来源：welivesecurity
                                <br>原文地址：[https://www.welivesecurity.com/2019/07/10/windows-zero-day-cve-2019-1132-exploit/](https://www.welivesecurity.com/2019/07/10/windows-zero-day-cve-2019-1132-exploit/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0177c6a13633be4aa9.jpg)](https://p5.ssl.qhimg.com/t0177c6a13633be4aa9.jpg)



## 0x00 前言

2019年6月，ESET研究人员发现攻击者利用一个0day漏洞对东欧地区发起攻击。

攻击者滥用了Windows系统中的一个本地权限提升漏洞，更具体一点是`win32k.sys`组件中对NULL指针解引用（dereference）的一个漏洞。我们在发现并分析这个漏洞利用技术后，就第一时间反馈给MSRC，MSRC及时修复了漏洞并发布了安全补丁。

该漏洞影响如下Windows版本：

```
Windows 7 for 32-bit Systems Service Pack 1
Windows 7 for x64-based Systems Service Pack 1
Windows Server 2008 for 32-bit Systems Service Pack 2
Windows Server 2008 for Itanium-Based Systems Service Pack 2
Windows Server 2008 for x64-based Systems Service Pack 2
Windows Server 2008 R2 for Itanium-Based Systems Service Pack 1
Windows Server 2008 R2 for x64-based Systems Service Pack 1
```

本文重点关注该漏洞的技术细节及利用方式。在另一篇文章中，我们将深入分析这个恶意样本及其他相关信息。



## 0x01 漏洞利用

这几年来研究人员公布了Windows `win32k.sys`组件的几个漏洞，与这些漏洞类似，此次攻击者利用的也是弹出菜单对象。我们在2017年也[分析](https://www.welivesecurity.com/2017/05/09/sednit-adds-two-zero-day-exploits-using-trumps-attack-syria-decoy/)过Sednit攻击组织利用过的本地提权漏洞，当时攻击者利用的也是菜单对象，与此次攻击方法非常类似。

漏洞利用过程中创建了两个窗口，分别用于第一及第二漏洞利用阶段。对于第一个窗口，漏洞利用程序会使用`CreatePopupMenu`以及`AppendMenu`函数来创建弹出菜单对象并追加菜单项。此外，利用程序还会设置`WH_CALLWNDPROC`以及`EVENT_SYSTEM_MENUPOPUPSTART`类型的hook。

随后利用程序会使用`TrackPopupMenu`函数来显示该菜单。此时hook `EVENT_SYSTEM_MENUPOPUPSTART`对应的代码会被执行。该代码会向目标菜单依次发送`MN_SELECTITEM`、`MN_SELECTFIRSTVALIDITEM`以及`MN_OPENHIERARCHY`消息，尝试打开菜单中第一个可用项。

下一个步骤对触发漏洞来说非常重要。漏洞利用程序必须及时抓住初始菜单已创建、且子菜单即将创建的时机。为了完成该任务，利用程序专门包含某些代码，用来处理在`WH_CALLWNDPROC` hook中的`WM_NCCREATE`消息。当利用代码检测到系统处于该状态时，就会向第一个菜单发送`MN_CANCELMENUS`（`0x1E6`）消息，取消该菜单。然而，该菜单对应的子菜单依然即将会被创建。

现在如果我们在内核模式中观察这个子菜单对象，可以看到`tagPOPUPMENU‑&gt;ppopupmenuRoot`的值等于`0`。该状态允许攻击者在这个内核结构中使用该元素作为NULL指针执行dereference操作。利用代码会在`0x00`地址处分配一个新页，而该地址会被内核当成一个`tagPOPUPMENU`对象（如图1所示）。

[![](https://p4.ssl.qhimg.com/t0173c5fa54458101e1.png)](https://p4.ssl.qhimg.com/t0173c5fa54458101e1.png)

图1. `tagPOPUPMENU`内核结构

此时攻击者会使用第二个窗口。这里漏洞利用的主要目标是翻转第二个窗口`tagWND`结构中的`bServerSideWindowProc`位，成功翻转后内核模式中就会执行`WndProc`过程。

为了完成该任务，攻击者会调用`user32.dll`库中未导出的`HMValidateHandle`函数，泄露第二个窗口`tagWND`结构的内核内存地址。随后利用程序会在NULL页构造一个虚假的`tagPOPUPMENU`对象，向子菜单发送`MN_BUTTONDOWN`消息。

完成该操作后，内核最终会执行`win32k!xxxMNOpenHierarchy`函数。

[![](https://p3.ssl.qhimg.com/t012649831eb774a551.png)](https://p3.ssl.qhimg.com/t012649831eb774a551.png)

图2. `win32k!xxxMNOpenHierarchy`函数的反汇编代码

该函数会将NULL页面上构造的对象传递给`win32k!HMAssignmentLock`，而`win32k!HMAssignmentLock`函数在经过几次调用后，会调用`win32k!HMDestroyUnlockedObject`函数，后者会设置`bServerSideWindowProc`位。

[![](https://p4.ssl.qhimg.com/t01fd240ad5a971a621.png)](https://p4.ssl.qhimg.com/t01fd240ad5a971a621.png)

图3. `win32k!HMDestroyUnlockedObject`函数的反汇编代码

现在一切准备就绪，利用代码会向第二个窗口发送特定的消息，以便在内核模式中执行`WndProc`。

在最后一个攻击步骤中，利用代码会使用系统令牌替换当前进程的令牌。

微软已发布安全补丁，在`win32k!xxxMNOpenHierarchy`函数添加了针对NULL指针的检查过程。

[![](https://p3.ssl.qhimg.com/t01b2f3d9a888569988.png)](https://p3.ssl.qhimg.com/t01b2f3d9a888569988.png)

图4. `win32k.sys`打补丁前（左图）后（右图）的代码对比



## 0x02 总结

这个漏洞利用技术只适用于老版本的Windows系统，因为从Windows 8开始，用户进程再也不能映射NULL页面。微软将这种缓解措施一并移植到了基于x64架构的Windows 7系统中。

如果大家还在使用32位的Windows 7 Service Pack 1，可以考虑更新到最新版的操作系统。Windows 7 Service Pack 1的扩展支持将于[2020年1月14日](http://windows.microsoft.com/en-us/windows/lifecycle)结束，这意味着后续Windows 7用户无法获得关键安全更新，因此像这样的漏洞永远不会被官方修复。



## 0x03 IoC

<th style="text-align: left;">SHA-1哈希</th><th style="text-align: left;">ESET检测特征</th>
|------
<td style="text-align: left;">CBC93A9DD769DEE98FFE1F43A4F5CADAF568E321</td><td style="text-align: left;">Win32/Exploit.CVE-2019-1132.A</td>
