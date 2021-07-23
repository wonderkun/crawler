> 原文链接: https://www.anquanke.com//post/id/195725 


# 利用Ubuntu的错误报告功能实现本地提权（LPE）


                                阅读量   
                                **1224238**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者github，文章来源：securitylab.github.com
                                <br>原文地址：[https://securitylab.github.com/research/ubuntu-whoopsie-daisy-overview](https://securitylab.github.com/research/ubuntu-whoopsie-daisy-overview)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01cd34f92ae310e7ca.jpg)](https://p4.ssl.qhimg.com/t01cd34f92ae310e7ca.jpg)



## 严重程度

这篇文章描述了在Ubuntu错误报告系统中发现的五个漏洞: CVE-2019-7307、CVE-2019-11476、CVE-2019-11481、CVE-2019-11484、CVE-2019-15790。其中 CVE-2019-11476和CVE-2019-11481两个漏洞是危害程度较低的本地拒绝服务漏洞，但剩余三个严重程度较高。当这些漏洞组合在一起时，允许本地无特权的攻击者可以读取系统上的任意文件。换句话说，它们组合在一起会造成一个只读的本地特权提升漏洞。这意味着攻击者可以利用这些漏洞来窃取重要信息，例如其他用户的SSH密钥。<br>
CVE-2019-15790，也可以在其他的攻击链中重复使用。它能够让攻击者可以获取他们可以启动（或重新启动）的进程的ASLR偏移量。虽然它本身作用并不是特别大，但是如果在系统服务中发现了内存破坏漏洞，那么就可以访问其ASLR偏移量，也就可以利用该漏洞。例如，我最初无法从CVE-2019-11484获取拒绝服务之外的任何东西，但是在CVE-2019-15790的帮助下，我能够执行代码。

现在，五个漏洞中的每一个的漏洞报告都可以在Ubuntu的漏洞跟踪站点上看到：

[CVE-2019-7307](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-7307): apport bug [1830858](https://bugs.launchpad.net/ubuntu/+source/apport/+bug/1830858)<br>[CVE-2019-11476](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-11476): whoopsie bug [1830863](https://bugs.launchpad.net/ubuntu/+source/whoopsie/+bug/1830863)<br>[CVE-2019-11481](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-11481): apport bug [1830862](https://bugs.launchpad.net/ubuntu/+source/apport/+bug/1830862)<br>[CVE-2019-11484](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-11484): whoopsie bug [1830865](https://bugs.launchpad.net/ubuntu/+source/whoopsie/+bug/1830865)<br>[CVE-2019-15790](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-15790): apport bug [1839795](https://bugs.launchpad.net/ubuntu/+source/apport/+bug/1839795).

前两个漏洞已于2019年7月9日修复。其余三个漏洞已于2019年10月29日修复。完整的LPE利用链依赖于CVE-2019-7307，该漏洞已于7月9日修复，所以10月29日修复的漏洞对于经常保持最新系统的人来说已经得到缓解，如果尚未更新补丁，请确保已升级到最新版本的apport和whoopsie。



## 概述

让我们回顾一下Ubuntu错误报告系统的架构。后续将通过3篇文章来介绍漏洞:

2019年12月17日：Ubuntu apport TOCTOU漏洞（CVE-2019-7307）<br>
2019年12月19日：Ubuntu apport PID回收漏洞（CVE-2019-15790）<br>
2019年12月23日：Ubuntu Whoopsie整数溢出漏洞（CVE-2019-11484）



## Ubuntu中的错误报告

为了方便理解漏洞,了解Ubuntu错误报告系统的架构是很有帮助的。它由几个不同的组件组成。如果你是Ubuntu用户，你可能熟悉这个组件:

[![](https://p0.ssl.qhimg.com/t01eee94f585644c274.png)](https://p0.ssl.qhimg.com/t01eee94f585644c274.png)

这个对话框是apport-gtk，尽管它是错误报告系统中最常见的组件，但从安全角度来看，它是我们最不感兴趣的。首先，它不具有特限提升，它只能读取当前用户拥有的错误报告。并且，在系统进程或另一个用户的进程崩溃的情况下，不会出现该对话框。其次，尽管有出现，它不负责上传错误报告。如果单击发送，它将在/var/crash目录中创建带有 .upload 扩展名的文件，作为报告应该上传的信号。

我们故意使程序崩溃，看看会发生什么：

```
kev@constellation:~$ sleep 60s &amp;
[1] 4268
kev@constellation:~$ kill -SIGSEGV 4268
kev@constellation:~$
[1]+  Segmentation fault      (core dumped) sleep 60s
kev@constellation:~$
```

在示例中，我启动了/bin/sleep，并使用kill造成Segmentation Fault的错误。下图表明了接下来发生的事情：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://securitylab.github.com/static/78fcc0b51d5f84c1918897a8e3f33187/ubuntu_crash_reporter_architecture.svg)

崩溃最初由内核处理。然后，内核读取core_pattern文件来确定他如何处理核心转储文件。在默认安装的Ubuntu中，core_pattern文件如下所示：

```
kev@constellation:~$ cat /proc/sys/kernel/core_pattern
|/usr/share/apport/apport %p %s %c %d %P
```

文件开头的管道符”|”表示内核应将核心转储文件传输到/usr/share/apport/apport， apport是Python程序，它以root运行（后面会删除权限）。它的工作是创建一个错误报告并将其写入/var/crash目录。在本例中，错误报告如下所示:

```
kev@constellation:~$ ls -l /var/crash/
total 32
-rw-r----- 1 kev whoopsie 32211 Oct 24 12:30 _bin_sleep.1001.crash
kev@constellation:~$
```

/var/crash目录是错误报告系统的通信中心。其他组件通过在/var/crash中写入文件来相互通信。apport-gtk和whoopsie会监控/var/crash目录下的新文件，whoopsie负责将错误报告上传到daisy.ubuntu.com，只有看到 .upload 后缀名的文件时才上传，也就是说当单击发送时，apport-gtk只创建一个扩展名为.upload的空文件。这时才触发whoopsie解析错误报告并上传到daisy.ubuntu.com。

### <a class="reference-link" name="%E9%94%99%E8%AF%AF%E6%8A%A5%E5%91%8A%E4%B8%AD%E7%9A%84%E5%AE%89%E5%85%A8%E7%95%8C%E9%99%90"></a>错误报告中的安全界限

我喜欢Ubuntu错误报告系统的设计方式。分成多个组件可以最大程度地减少需要使用root权限运行的代码量。我还喜欢UI组件apport-gtk没有连接到internet，这与Windows错误报告系统形成了有趣的对比，Windows错误报告系统在今年早些时候也具有权限提升漏洞: CVE-2019-0863，由Palo Alto Networks的Gal De Leon发现。在关于这个漏洞的 [文章](https://unit42.paloaltonetworks.com/tale-of-a-windows-error-reporting-zero-day-cve-2019-0863/)中，Gal De Leon解释说，负责上传错误报告的组件 wermger.exe是以系统权限运行。相反，在Ubuntu上，唯一以root身份运行的组件是apport。

我提供的图中用一些框来表示不同组件的权限级别。左边的apport-gtk表示当前用户运行，没有特殊权限。右边的apport以root用户身份运行，但不直接与UI或internet交互。中间的whoopsie是一个运行为“whoopsie”的守护进程，它是一个具有较少权限的系统用户。它与Internet（daisy.ubuntu.com）交互，但不与UI交互。

### <a class="reference-link" name="/var/crash%E5%B1%9E%E6%80%A7"></a>/var/crash属性

如上所述，/var/crash目录是错误报告系统的通信中心。要启用此功能，需要设置SGID和sticky位，如下所示：

```
kev@constellation:~$ ls -al /var/crash/
total 48
drwxrwsrwt  2 root whoopsie 12288 Oct 25 09:10 .
drwxr-xr-x 17 root root      4096 Jul 17 19:31 ..
-rw-r-----  1 kev  whoopsie 32211 Oct 24 12:30 _bin_sleep.1001.crash
kev@constellation:~$
```

该SGID位表示，在/var/crash写入的任何文件都属于whoopsie组，这造成whoopsie守护程序可以读取该文件。sticky位可防止其他用户删除或重命名不属于他们的错误报告。

### <a class="reference-link" name="%E9%94%99%E8%AF%AF%E6%8A%A5%E5%91%8A%E6%94%BB%E5%87%BB%E9%9D%A2"></a>错误报告攻击面

既然错误报告有一个良好的体系结构和明确的安全边界，那攻击面在哪里?最关键的组件是apport，因为它以root身份运行。粗略地看，它似乎没有攻击面，因为它是由内核调用的，并且不与UI或Internet直接交互。但是，在某些方面它和setuid二进制文件类似，因为它可以由任何用户调用。(你所要做的就是向一个进程发送一个SIGSEGV，就像我之前对/bin/sleep那样做。)它读取大量文件，其中一些是用户主目录中的配置文件。我在apport中发现的所有漏洞都涉及欺骗它使用root权限来读取我无权访问的文件,在（CVE-2019-7307和CVE-2019-15790）两个案例中，我还可以诱导它在错误报告中包含文件的内容。

在研究漏洞利用时，我发现Apport具有另一种类型的攻击面：timing(定时)，为了利用漏洞，我经常需要控制apport的时间，以便某些事件按特定顺序发生。首先，我发现可以通过观察apport访问的文件来观察apport的时间，并使用这些信息在正确的时间触发关键事件。其次，我发现了几种可以在apport执行期间暂停apport的方法。一种方法是获取/var/crash/.lock上的文件锁，这会导致apport在启动时暂停。另一个方法是向它发送SIGSTOP信号。能够向apport发送SIGSTOP信号是apport在执行期间取消特权的一个有趣结果。为了安全起见，Apport放弃特权：以root身份运行花费的时间越少越安全。但是，比较搞笑的是，这使我能够发送信号，如果它仍然是root，我就不能这样做。

从安全角度来看，whoopsie守护进程似乎相当乏味。它读取/var/crash中的错误报告并上传到daisy.ubuntu.com。它以whoopsie用户的身份运行，该用户几乎没有特权。实际上，我对whoopsie感兴趣的唯一原因是它可以读取所有错误报告，甚至包括由root进程生成的错误报告。CVE-2019-7307可以读取系统上的任何文件，并将其内容包含在错误报告中。但是该错误报告只能由root和whoopsie读取。我研究了是否可以欺骗whoopsie将错误报告上传到与daisy.ubuntu.com不同的URL，但得出结论表示这是不可能的，尤其是因为whoopsie在libcurl中使用了 CURLOPT_SSL_VERIFYPEER 上传选项，如<br>[whoopsie.c:326](http://bazaar.launchpad.net/~daisy-pluckers/whoopsie/trunk/view/698/src/whoopsie.c#L326)：

```
curl_easy_setopt (curl, CURLOPT_SSL_VERIFYPEER, verifypeer);
```

因此，为了完成漏洞利用链，我需要一种将代码作为whoopsie运行的方法，最终我通过CVE-2019-11484和CVE-2019-15790实现了这一目标。前者是whoopsie中的堆缓冲区溢出，是由/var/crash中创建恶意错误报告触发的。后者是apport中的一个信息泄露漏洞，它使我能够攻破whoopsie的ASLR。



## Timeline

2019-05-29：披露CVE-2019-7307（apport bug 1830858）<br>
2019-05-29：披露CVE-2019-11476（whoopsie bug 1830863）<br>
2019-05-29：披露CVE-2019-11481（apport bug 1830862）<br>
2019-05-29：披露CVE-2019-11484（whoopsie bug 1830865）<br>
2019-07-09：Ubuntu发布[2.20.9-0ubuntu7.7](https://launchpad.net/ubuntu/+source/apport/2.20.9-0ubuntu7.7)，它修复了CVE-2019-7307（apport bug 1830858）<br>
2019-07-09：Ubuntu发布[whoopsie 0.2.62ubuntu0.1](https://launchpad.net/ubuntu/+source/whoopsie/0.2.62ubuntu0.1)，修复了CVE-2019-11476（whoopsie bug 1830863）<br>
2019-08-12：披露CVE-2019-15790（apport bug 1839795）。<br>
2019-10-29：Ubuntu发布[whoopsie 0.2.62ubuntu0.2](https://launchpad.net/ubuntu/+source/whoopsie/0.2.62ubuntu0.2)，修复了CVE-2019-11484（whoopsie bug 1830865）。<br>
2019-10-29：Ubuntu发布[2.20.9-0ubuntu7.8](https://launchpad.net/ubuntu/+source/apport/2.20.9-0ubuntu7.8)，修复了CVE-2019-11481和CVE-2019-15790（apport bugs 1830862 and 1839795）。

本文翻译自GitHub Security Lab
