> 原文链接: https://www.anquanke.com//post/id/86706 


# 【技术分享】如何获取TrustedInstaller权限


                                阅读量   
                                **331509**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blogspot.co.uk
                                <br>原文地址：[https://tyranidslair.blogspot.co.uk/2017/08/the-art-of-becoming-trustedinstaller.html](https://tyranidslair.blogspot.co.uk/2017/08/the-art-of-becoming-trustedinstaller.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0146ea974df492dd89.jpg)](https://p5.ssl.qhimg.com/t0146ea974df492dd89.jpg)

<br>

****

译者：[**我来学英语**](http://bobao.360.cn/member/contribute?uid=1264882569)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

**这篇文章将带你了解TI的本质是什么，进一步探索如何在powershell和NtObjectManager模块的帮助下获取TI权限，以便在操作系统中完成任何你想要的操作。**

如果你曾管理过windows系统，那么你应该知道trustedInstaller（TI）组的概念，大部分对系统文件和注册表的操作都需要TI组权限。举个例子，你可以看一下System32文件夹下的文件的属性，在安全选项下TI和文件Owner可以删除和修改文件（甚至管理员都不能），所以你不能直接对安全选项进行修改。

[![](https://p1.ssl.qhimg.com/t01ff94b579d483715b.png)](https://p1.ssl.qhimg.com/t01ff94b579d483715b.png)

然而，如果你查看本地用户和组选项你是没办法找到TI用户或组的。这篇文章将带你了解TI组的本质，然后进一步学习，如何在Powershell和NtObjectManager模块的帮助下获得TI组权限，以便在操作系统中完成任何你想要的操作。<br>

<br>

**什么是TrustedInstaller**

如果TI既不是用户又不是组那它又是什么？查询ACL会给我们一些启示。你可以使用Get-Acl命令来读取一个文件的安全描述，同时我们可以列出TI信息。

[![](https://p0.ssl.qhimg.com/t012dc825f4b04d6944.png)](https://p0.ssl.qhimg.com/t012dc825f4b04d6944.png)

从上图可以看到在IdentityReference项中我们看到了TI组，并且它有一个NT SERVICE的前缀。因此，它是一个Windows 服务SID，这是在Vista中加入的特性，这个特性允许操作系统上运行的每一项服务都有一个用来进行权限检查的组。通过这种机制，操作系统不必承担增加独立真实的组的额外开销。<br>

SID本身是服务名的大写表示的SHA1值，下面这段代码就可以计算真实的SID值：



```
$name = "TrustedInstaller"
# Calculate service SID
$bytes = [Text.Encoding]::Unicode.GetBytes($name.ToUpper())
$sha1 = [System.Security.Cryptography.SHA1]::Create()
$hash = $sha1.ComputeHash($bytes)
$rids = New-Object UInt32[] 5
[Buffer]::BlockCopy($hash, 0, $rids, 0, $hash.Length)
[string]::Format("S-1-5-80-`{`0`}`-`{`1`}`-`{`2`}`-`{`3`}`-`{`4`}`", `
$rids[0], $rids[1], $rids[2], $rids[3], $rids[4])
```

当然，你大可不必自己去实现这个方法，NTDLL中有一个RtlCreateServiceSid方法可以做到这一点，同时LSASS中也能把服务名转换成SID。也就是说，当系统资源被更改时，一个名为TrustedInstall的系统服务一定会被运行。我们使用SC模块也能发现这一点。<br>

[![](https://p5.ssl.qhimg.com/t0137a2dc4934a989e9.png)](https://p5.ssl.qhimg.com/t0137a2dc4934a989e9.png)

如果开启TI服务并查看Access Token，我们可以看到TI组被启用。<br>

[![](https://p0.ssl.qhimg.com/t01760ddf161adfc2f7.png)](https://p0.ssl.qhimg.com/t01760ddf161adfc2f7.png)

到这里背景知识就介绍完了，假如我们是管理员，该如何利用TrustedInstaller呢？<br>

<br>

**成为TrustedInstaller**

如果你搜索过如何删除TI拥有的资源，你一般会得到这样的结果：它会告诉你首先要获取文件或者密钥的所有权，然后再更改DACL来添加管理员组。这是因为即使是兼容IFileOperation UAC COM的组件通常也不会自动运行，并且会弹出下面这个对话框：

[![](https://p3.ssl.qhimg.com/t017b89edbc2a7ad4cc.png)](https://p3.ssl.qhimg.com/t017b89edbc2a7ad4cc.png)

改变系统文件的权限实在不是个好主意，如果你做错了你会将操作系统暴露给EOP，尤其是对目录来说。资源管理器可以轻松地更改所有子文件和文件夹的安全属性为初始值。当然，TI会阻止你这么做的，但是总有些人出于某些目的而想要这么做。<br>

你也许会想，我可以把当前用户添加到TI组中。不幸的是像NetLocalGroupAddMembers这样的LSASS api不使用SID，修改注册表值NT SERVICETrustedInstaller同样无效。因为它根本就不是一个真实的组，它是使用其他方法来创建的。也许你可以通过念一段神奇的咒语来完成这件事，或者至少使用底层的RPC调用，但我认为这么做不太值得。

因此，修改TI服务设置的最快方法是通过改变设置来运行一个其他的二进制文件。奇怪的是，TI服务使得系统上的文件很难被随意修改，但是它却不保护它自己，修改它的操作可以以一个普通管理员的权限完成。所以你可以使用下面的命令来删除任意文件

```
sc config TrustedInstaller binPath= "cmd.exe /C del pathtofile"
```

启动TI服务，咻的一声文件就没了。这条命令能够生效的另一个原因是，TI不是一个Protected Process Light (PPL)，这也是一件奇怪的事情，因为TI组被赋予了删除和停止PPL服务的权限。我把这一点向MSRC[指出](https://bugs.chromium.org/p/project-zero/issues/detail?id=997)过（并且Alex lonescu在2013年也[这么做](http://www.alex-ionescu.com/?p=116)了），但是微软并没有采取任何措施去修复。看起来微软也并不认为PPL是一个安全边界。

上述操作做完之后你必须把TI服务恢复到原来的状态，否则像Windows Update之类的服务就没法正常工作了。由于TI服务有一个token，那么我们是否可以借用这个token来创建一个新进程呢？<br>

作为管理员，我们可以调用SeDebugPrivilege函数来打开TI进程和它的token。然后我们就可以做任何事情了，试一下吧：

[![](https://p0.ssl.qhimg.com/t01a3b7da05fb432365.png)](https://p0.ssl.qhimg.com/t01a3b7da05fb432365.png)

这很简单，是时候来尝试一下TI的其他操作了。<br>

[![](https://p5.ssl.qhimg.com/t0115a146b1173cf398.png)](https://p5.ssl.qhimg.com/t0115a146b1173cf398.png)

好吧，看起来我们没法通过使用这个token创建或者模拟一个进程，这可不太好。在上图底部我们可以看到原因。我们只有TOKEN_QUERY的权限，但是我们至少需要TOKEN_DUPLICATE权限来获取一个创建新进程所需要的token。检查token的安全描述，使用Process Hacker来查看为什么我们的访问权限这么低（我们甚至连READ_CONTROL权限都没有）。<br>

[![](https://p5.ssl.qhimg.com/t015ba8530e3913a481.png)](https://p5.ssl.qhimg.com/t015ba8530e3913a481.png)

可以看到，管理员组只有TOKEN_QUERY权限。这一点与我们通过token获得的访问权限是一致的。你可能想知道为什么SeDebugPrivilege没有生效，因为调试权限仅仅绕过了进程和线程对象的安全检查，它并不会对token进行任何操作，因为我们没法获得它的帮助。看起来有点麻烦，但是是否就没有除了修改服务二进制这种暴力操作以外的其他方法来达到目的了呢？<br>

当然不是了。有一些例子可以说明我们如何让类似于TI的服务运行起来，一般来说，可以先安装一个服务来运行代码，然后窃取TI令牌，最后再创建新进程。很容易理解，如果我想创建一个服务，我只需要修改Trusted Installer服务。<br>

因此，有两种很简单的方法来绕过这种权限限制，并且不需要任何新的或者修改过的或者注入过代码的服务。我们首先来看创建新进程的问题。一个进程的父进程会调用CreateProcess，对于UAC来说，这将提升子进程的权限，这看起来有些奇怪。为了支持微软所介绍的Vista中的最小权限原则，通过创建新进程时都会显式指定一个父进程，以便权限提升后的进程仍然是调用者的子进程。

通常在开启了UAC的情况下，你可以显示指定子新进程的token。然而，如果你没有指定token，新进程就会从父进程处继承token。因此，我们这么做的唯一要求是获得父进程句柄的PROCESS_CREATE_PROCESS权限。由于我们已经有SeDebugPrivilege权限了，我们就可以获取TI进程的完整权限，当然也包括创建它的子进程的权限。这么做的额外好处是，内核中创建进程的代码甚至会直接为调用者分配正确的会话ID，这样就可以创建交互式进程了。我们利用这种特性，在当前桌面上通过New-Win32Process使用TI服务的token创建了任意进程，并且通过-ParentProcess参数将进程对象传递进去。<br>

[![](https://p2.ssl.qhimg.com/t01a545b9d9a2bcaefe.png)](https://p2.ssl.qhimg.com/t01a545b9d9a2bcaefe.png)

在不创建新进程的情况下模拟token也很有用。有没有方法实现呢？有。我们可以使用NtImpersonateThread API，它允许从现有的线程中捕获上下文，并且可以应用到另一条线程中。模拟上下文工作的过程是，内核首先尝试捕获该线程的token，如果线程没有token，那么内核将通过模拟来复制与线程相关进程的token。而NtImpersonateThread API的美妙之处在于，设置父进程时不需要访问token的权限，它只需要THREAD_DIRECT_IMPERSONATION模拟访问一个线程，这一点我们只需要使用SeDebugPrivilege就可以做到。因此，可以通过以下步骤来获得一个不产生新进程的模拟线程：

**以至少PROCESS_QUERY_INFORMATION的权限打开一个进程，枚举其线程**

**以THREAD_DIRECT_IMPERSONATION权限打开进程中的第一条线程**

**调用NtImpersonate Thread来获取一个模拟token**

[![](https://p3.ssl.qhimg.com/t014725de379ebf30df.png)](https://p3.ssl.qhimg.com/t014725de379ebf30df.png)

现在，只要其他线程不去设置主线程的模拟token（并且你也不要在分离出的线程上做任何事情），那么你的PowerShell控制台就是拥有TI组的状态。<br>

<br>

**总结**

**希望这篇文章能给你一些启示，了解什么是TrustedInstaller，掌握以管理员身份获取TI组token的方法**，当然，获取TI组token这种操作在正常情况下是做不到的。这种方法适用于现代Windows操作系统上的不同系统服务，如果你想与它们的资源进行交互来进行测试的话，比如使用沙箱工具来获取它们所拥有的资源时，你就可以用到本文所提到的方法。


