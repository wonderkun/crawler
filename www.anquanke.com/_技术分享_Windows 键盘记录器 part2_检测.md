> 原文链接: https://www.anquanke.com//post/id/86404 


# 【技术分享】Windows 键盘记录器 part2：检测


                                阅读量   
                                **118891**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：eyeofrablog.wordpress.com
                                <br>原文地址：[https://eyeofrablog.wordpress.com/2017/06/27/windows-keylogger-part-2-defense-against-user-land/](https://eyeofrablog.wordpress.com/2017/06/27/windows-keylogger-part-2-defense-against-user-land/)

译文仅供参考，具体内容表达以及含义原文为准

![](https://p2.ssl.qhimg.com/t01512b10ff94e60f8c.jpg)

****

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

传送门

[【技术分享】Windows 键盘记录器 part1：应用层方法](http://bobao.360.cn/learning/detail/4084.html)

**<br>**

**0x00 前言**

回顾[**第一部分**](http://bobao.360.cn/learning/detail/4084.html)，我们总结了4种Windows用户模式的键盘记录的方法，今天我们将分析每种技术的检测方式。

测试机器：

![](https://p0.ssl.qhimg.com/t017fbd7f4aa0e86c78.png)

<br>

**0x01 SetWindowsHookEx**

当我们使用SetWindowsHookEx注册消息钩子时，系统将我们的钩子处理函数保存在钩子链（是一个指针列表）中。因为我们能注册任何消息类型的钩子，因此，每种消息类型都有一个钩子链。因此我们的目标是：

**系统内存中钩子链的位置（WH_KEYBOARD和WH_KEYBOARD_LL）**

**如何找到钩子的进程名**

对于钩子链的位置，可以参考如下：

```
nt!_ETHREAD + 0x0 =&gt; nt!_KTHREAD + 0x088 =&gt; nt!_TEB + 0x40 =&gt; win32k!tagTHREADINFO + 0xCC =&gt; win32k!tagDESKTOPINFO + 0x10 =&gt; win32k!tagHOOK
```

每个结构都很清楚（感谢Windows符号）。Offset值是我的测试机器的，不同的Windows版本和构建版本会不同（ntoskrnl和win32k.sys）。

从nt!_ETHREAD看，它一定是一个GUI线程。我们能从explorer.exe中得到GUI线程，或者自己创建。

在上面，我们能得到系统所有的全局钩子链的位置。这个有16个tagHOOK的数组指针，数组索引是WH_*消息类型的值（实际上是index=WH_*+1）。如果条目是空，我们能找到一个全局钩子链。

![](https://p4.ssl.qhimg.com/t018307cd6fa553dda4.png)

从tagHook中的_THRDESKHEAD看，我们能得到设置钩子的进程的tagTHREADINFO。因此我们能得到进程ID和进程名：

```
processIdOfHooker = PsGetProcessId(IoThreadToProcess((PETHREAD)(*pCurHook-&gt;head.pti)));
```

扫描结果：

![](https://p1.ssl.qhimg.com/t0160fb6612db4c8929.jpg)

好了，查找Windows全局消息钩子可以了。那么本地钩子怎么办？

下面是本地钩子：

```
nt!_ETHREAD + 0x0 =&gt; nt!_KTHREAD + 0x088 =&gt; nt!_TEB + 0x40 =&gt; win32k!tagTHREADINFO + 0x198 =&gt;  win32k!tagHOOK
```

和全局钩子很相似，但是你能看见本地钩子链的位置是在进程的tagTHREADINFO结构体中的，它是进程相关的。tagDESKTOPINFO中的钩子链是相同桌面下所有进程的。

<br>

**0x02 轮询**

我确实不知道怎么扫描这种方式。为什么？因为它直接从内部结构读取键的状态，似乎没有方式来检测。

![](https://p5.ssl.qhimg.com/t01f20ff345e7c6596c.jpg)

针对GetAsyncKeyState(), GetKeyboardState() API hook？可以，我们可以通过API来检测，但是我不想用它，因为针对系统所有进程全局APIhook不是个好方法。使用API HOOK，我们能检查频率和键盘记录键的范围。

<br>

**0x03 Raw Input**

我从分析user32.dll中的RegisterRawInputDevices函数开始。这个API将调用win32k.sys中的NtUserRegisterRawInputDevices。

![](https://p3.ssl.qhimg.com/t0160cc53bf77993f78.jpg)

在一些检查之后，进入_RegisterRawInputDevices

![](https://p2.ssl.qhimg.com/t017f20dcf3d6a9eb20.jpg)

![](https://p5.ssl.qhimg.com/t019292ec679d9d83b8.jpg)

这里非常清楚。PsGetCurrentProcessWin32Process返回win32k!tagPROCESSINFO结构体。使用WinDbg查看偏移0x1A4：

![](https://p2.ssl.qhimg.com/t01f15063a37f4b5a74.png)

有个指针指向win32k!tagPROCESS_HID_TABLE。

20-34行，验证注册的数据（HID请求）。

36-47行，如果不存在分配HID表。意味着，如果tagPROCESSINFO-&gt;pHidTable为空，进程中没有注册设备。

48-71行，设置HID请求到HID表中。

剩下的就是更新标志和重启HID设备。

让我们看下SetProcDeviceRequest函数：

![](https://p4.ssl.qhimg.com/t01d91ab06ddd32b1f2.jpg)

系统分配一个HID请求，将它插入到HID表中

![](https://p2.ssl.qhimg.com/t01bf4a036088ce7453.png)

这里有2个HID请求的列表，分别是InclusionList, UsagePageList and ExclusionList。插入哪个列表取决于调用RegisterRawInputDevices的tagRAWINPUTDEVICE的dwFlags值。

![](https://p3.ssl.qhimg.com/t0166afbebfb90f6d43.jpg)

对于键盘记录，我使用RIDEV_NOLEGACY | RIDEV_INPUTSINK标志，因此是InclusionList。最后一个结构体是win32k!tagPROCESS_HID_REQUEST

![](https://p0.ssl.qhimg.com/t01ee7ede4c176885f4.png)

能看到usUsagePage, usUsage and spwndTarget是tagRAWINPUTDEVICE的参数。

对于原始输入的检测：

1. 枚举系统所有的进程

2. 针对每个进程，遍历pID -&gt; PEPROCESS -&gt; tagPROCESSINFO -&gt; tagPROCESS_HID_TABLE -&gt; tagPROCESS_HID_REQUEST

3. 如果我们找到usUsagePage = 1的条目（通常是桌面控制）和usUsage = 6（键盘），这个进程就是用来键盘记录的。

扫描结果：

![](https://p4.ssl.qhimg.com/t01ac191f7ec1b37f43.jpg)

<br>

**0x04 Direct Input**

当检测direct input时，我发现了注册钩子进程中的一些有趣的特征。

![](https://p1.ssl.qhimg.com/t0136acc47becc845f7.jpg)

![](https://p0.ssl.qhimg.com/t015bb286f6f98dc3f1.jpg)

针对MSIAfterburner.exe，我发现了一些与direct input(Mutant, Section, Key)相关的句柄。从运行的线程中，我们也能发现DINPUT8.dll（微软DirectInput库）。

对于direct input的检测：

1. 枚举系统所有进程

2. 对于每个进程，枚举所有的mutant、section、key，以匹配句柄特征

3. 如果所有的特征都匹配了，我们得到进程的所有的线程的起始地址。如果起始地址在DINPUT8.DLL的地址空间中，则找到了键盘记录。

扫描结果：

![](https://p0.ssl.qhimg.com/t01bf606ac970edf41a.jpg)

<br>

**0x05 总结**

总结扫描方式如下：

![](https://p3.ssl.qhimg.com/t015f62936b7ab4052a.png)

传送门

[【技术分享】Windows 键盘记录器 part1：应用层方法](http://bobao.360.cn/learning/detail/4084.html)


