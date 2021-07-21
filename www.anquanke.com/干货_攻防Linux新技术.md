> 原文链接: https://www.anquanke.com//post/id/83129 


# 干货：攻防Linux新技术


                                阅读量   
                                **117255**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.sentinelone.com/blog/breaking-and-evading/](https://www.sentinelone.com/blog/breaking-and-evading/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01aedfde7d53ed1c0e.jpg)](https://p0.ssl.qhimg.com/t01aedfde7d53ed1c0e.jpg)

任何恶意软件研究的重点一般都是预期攻击可能针对的地方或它已经在攻击的地方,从而制定和实施新的防御技术。通过逆向工程了一些最近的Linux恶意软件样本,我发现了一个有趣的新技术,我认为它很重要所以想和大家一起分享。一个攻击者已经登录到一个蜜罐并尝试下载我以前从未见过的文件。加载文件到 [IDA Pro](https://www.hex-rays.com/products/ida/) ,得到提示“SHT table size or offset is invalid. Continue? ” 这是对于可执行文件正常的,所以没什么好担心的。然而,收到此消息之后,我收到一个没见过的新警告;

[![](https://p3.ssl.qhimg.com/t01d98416788991193e.png)](https://p3.ssl.qhimg.com/t01d98416788991193e.png)

这引起了Linux的可执行文件ELF在IDA Pro中装载失败——阻止我加载二进制文件进行分析。使用 [ELFTemplate](https://github.com/strazzere/010Editor-stuff/blob/master/Templates/ELFTemplate.bt)从 [010Editor](http://www.sweetscape.com/010editor/)中打开该文件之后,我们很容易看到发生了什么事情;

[![](https://p5.ssl.qhimg.com/t0178b95409b9b30ee9.png)](https://p5.ssl.qhimg.com/t0178b95409b9b30ee9.png)

其中一个程序的头文件指向实际的文件之外。这很容易解决,只需归零这一部分从而允许IDA Pro加载样例。有趣的是,事实证明这是一个无效的二进制文件,有部分错位了因为该文件被截短过。然而,此错误信息引导我下载路径并试图重建这个错误文件——这很简单。具体步骤使用十六进制编辑器比较容易实现;
<li>
从ELF文件头部脱去所有部分
</li>
<li>
找到一个ELF文件不允许加载的程序头
</li>
<li>
使这个程序头这部分发生偏移指向文件之外
</li>
只要找不到其余的部分文件头,IDA Pro就将无法加载。把个过程编成脚本之后,我决定使用其他反汇编器和调试器测试几个方案。 Radare(R2),Hopper和lldb处理的二进制文件完全没有问题—— 但是GDB不认文件格式;

[![](https://p0.ssl.qhimg.com/t012244bcac18692002.png)](https://p0.ssl.qhimg.com/t012244bcac18692002.png)

然后进一步分析,我想看看除了作为一种反汇编技术,如果也作为一种抗分析抗模糊技术能不能用。当时的想法是,如果我用几个反汇编程序就这么容易找到这个问题所在,那么可能一些防病毒应用程序可能在自己的解析引擎中有同样的问题。

在这里我从Linux / XorDDos家族抓了检测到的相对完善恶意软件样本;

 

[![](https://p1.ssl.qhimg.com/t01d0d66b48b6bb81d4.png)](https://p1.ssl.qhimg.com/t01d0d66b48b6bb81d4.png)

[https://www.virustotal.com/en/file/0a9e6adcd53be776568f46c3f98e27b6869f63f9c356468f0d19f46be151c01a/analysis/](https://www.virustotal.com/en/file/0a9e6adcd53be776568f46c3f98e27b6869f63f9c356468f0d19f46be151c01a/analysis/)

他们刚刚发现,9种不同的引擎(2种出自同一家公司?所以我应该说是10种)没能够检测到同样的恶意软件。这我很感兴趣因为我在Linux恶意软件方面是新人,我会假设,这些引擎很容易地检测到恶意软件,这样一个简单的改变不会是如此简单的逃逸技术。

看起来攻击反汇编程序和引擎监制太容易了—— 所以我想看看整个样例库,看看是否有人偶然发现并实施这项技术。使用如下相当简单的 [YARA](https://plusvic.github.io/yara/)规则,我能找到6000个使用这一方法的样例。幸运的是,这些样例中,几乎每一个都是用来保护它自己的代码的商用Android保护壳。

虽然我们还没有看到任何在外面使用这种技术的恶意行为,但是在外面可能有许多其他类似的招数。这是一个良好的开端,寻找看看可能被恶意隐藏的ELF文件并加以分析,最后最好是用脚本发布出来,人们就能够监测这种技术并在未来使用类似的技术。

在之前发布的文章中,我已经通知没能检测到略作修改的恶意软件的Hex-Rays和那10个引擎。生成和修复这些修改后的二进制文件的脚本代码可以在github找到。

YARA规则:

[![](https://p0.ssl.qhimg.com/t01796708d57f35e36f.png)](https://p0.ssl.qhimg.com/t01796708d57f35e36f.png)
