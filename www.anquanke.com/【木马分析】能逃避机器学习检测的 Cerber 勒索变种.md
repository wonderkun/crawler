
# 【木马分析】能逃避机器学习检测的 Cerber 勒索变种


                                阅读量   
                                **87776**
                            
                        |
                        
                                                                                                                                    ![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85856/t0181feb58a3b4fc993.jpg)](./img/85856/t0181feb58a3b4fc993.jpg)**

****

作者：[黑鸟](http://bobao.360.cn/member/contribute?uid=2730021436)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**摘要**

CERBER勒索家族已经被发现通过一种新技术来逃避检测：使用了一种新的方法用加载出来的程序来逃避机器学习检测技术。其被设计为把一个二进制文件掏空，然后把CERBER的代码替换进去，再使用其他手段加载运行。

<br>

**行为分析**

勒索软件通常通过电子邮件传播，这些新的CERBER变体也不例外。电子邮件里面可以用各种各样的程序进行勒索软件的传播 。

比如邮件里面包含一个链接指向一个自解压的文件，该文件已经上传到攻击者控制的一个Dropbox账户里面，被攻击目标接着就会自动下载然后打开里面的程序，将会入侵整个系统。

下面的流程图大概说明了该变种的运行过程。

[![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d78e932e046185ef.jpg)

下载下来的自解压文件包含下面3个文件，VBS文件，DLL和1454KB的配置文件。在用户电脑中三个文件名字都会不一样，这里用他们的hash标注。<br>

[![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012bbbc7bd235da3ff.jpg)

自解压文件是exe后缀，双击之后会自动做上面流程图的事情，sfx*为关键参数

[![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fd6d68fc9f46eba6.jpg)

一开始vbs脚本是通过WSH运行，脚本反过来通过rundll32.exe与DLL的名字文件8ivq.dll作为它的参数来加载DLL文件，写的很简单明了。

[![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d5cf572e09adc6e9.jpg)

DLL文件非常的简单明了。所有的操作都是为了读1454KB的配置文件，先解密一部分配置文件，且无论解密与否都得一直运行着。

下图为DLL文件获取同一目录下文件名为“x”的配置文件，打开并读取相关字段并解密

[![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d421b18166b5ad67.jpg)

DLL文件没有包含文件或加密；然而，配置文件x中的代码在解密后是恶意的。

根据下图可以判断出x文件的开始地址

[![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016c4f8879ca8a2550.jpg)

文件x含有加载各种配置设置，加载出来的程序会去查找是否在虚拟机中运行，或者是否在沙箱中运行，是否有分析工具在机子中运行，或一些AV产品在运行，只要检测到就停止运行。

下面是样本的一些检测产品名称：

**分析工具**

Msconfig

Sandboxes

Regedit

Task Manager

Virtual Machines

Wireshark

**杀毒软件**

360

AVG

Bitdefender

Dr. Web

Kaspersky

Norton

Trend Micro

一般主流的加载payload是注入代码给另一个程序，而在这种情况下，注入代码是整个Cerber的二进制文件，并且其可以注入到下面的任何进程



```
C:WindowsMicrosoft.NETFrameworkv2.0.50727csc.exe
C:WindowsMicrosoft.NETFrameworkv2.0.50727regasm.exe
C:WindowsMicrosoft.NETFrameworkv4.0.30319csc.exe
C:WindowsSysWow64WerFault.exe
C:WindowsSystem32WerFault.exe
```

可以看一下双击自解压文件后的效果，双击最左边，出来右边一堆东西，过了一会各种弹窗

[![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012e76f8a6474711ff.jpg)

[![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a1a7d6d08c67a99a.jpg)

[![](./img/85856/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018fd09c59f10a10cf.jpg)

很明显的cerber勒索

<br>

**机器学习和逃逸**

接下来来到重点，Cerber已经被早一些的安全解决方案给阻止了，将Cerber运行在一个正常程序（与加载程序的做法一样）可以帮助逃避行为监控，但是为什么重新将Cerber加入压缩包并使用单独一个加载器来变得更麻烦呢？Cerber的早期版本已经有代码注入的例子了，它可以模仿成一个普通程序，并且能更好的模仿程序的行为，所以为什么单独加载是必要的呢？

答案在于通过机器学习行业来解决安全问题。机器学习行业已经创造出一种基于特征而不是签名的方法来主动防御恶意文件。重新打压缩包和加载机制被Cerber利用后可以造成对于静态机器学习方法出现问题——也就是说，该方法分析文件不会有任何的执行或仿真。

自解压文件和简单明了的文件对于静态机器学习方法来说是个问题。所有自解压文件无论其内容怎么样，可能结构看起来相似。仅仅只有解压二进制文件这样的功能可能不足以判断是恶意的，换句话说，Cerber被打压缩包的行为可以说是用来设计成专门用来逃避机器学习文件检测的。对于所有新的恶意软件对抗技术，等效的规避技术是很必要创建出来的。

这个新的逃避技术成功将使用多层防护的反恶意软件给绕过了。Cerber有对其他技术的弱点。举个例子，有解压缩。DLL 文件将容易的给他创建一个对多模式；如果压缩包是可疑的，那么如果压缩内容有存档的话能够更易于识别。有各种各样的解决方案可以防止这类变种的危害，只要不是过度依赖机器学习的软件，还是可以保护客户免受这些威胁的。

<br>

**样本hash**

```
VBS:09ef4c6b8a297bf4cf161d4c12260ca58cc7b05eb4de6e728d55a4acd94606d4a61eb7c8D
配置文件:7a6bc9e3eb2b42e7038a0850c56e68f3fec0378b2738fe3632a7e4c
DLL:e3e5d9f1bacc4f43af3fab28a905fa4559f98e4dadede376e199360d14b39153
自解压:f4dbbb2c4d83c2bbdf4faa4cf6b78780b01c2a2c59bc399e5b746567ce6367dd
```

这是我个人第一次发文章，如有错误请指正，随便再次强调大家不要随便下载或点开链接，这玩意是过现在的杀软的，防也防不住，发这篇文章也是希望机器学习技术能够发展的越来越好，扼杀勒索软件，个人也是勒索软件的受害者，才走上了这条路，QQ群：566327591，没几个人，啥都会点，都能讨论，谢谢大家

<br>

**参考链接**

[https://blog.trendmicro.com/trendlabs-security-intelligence/cerber-starts-evading-machine-learning/](https://blog.trendmicro.com/trendlabs-security-intelligence/cerber-starts-evading-machine-learning/) 
