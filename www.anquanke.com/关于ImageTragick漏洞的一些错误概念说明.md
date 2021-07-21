> 原文链接: https://www.anquanke.com//post/id/83904 


# 关于ImageTragick漏洞的一些错误概念说明


                                阅读量   
                                **80393**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://lcamtuf.blogspot.tw/2016/05/clearing-up-some-misconceptions-around.html](https://lcamtuf.blogspot.tw/2016/05/clearing-up-some-misconceptions-around.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t013490e3f46a9310ec.jpg)](https://p2.ssl.qhimg.com/t013490e3f46a9310ec.jpg)

近期,据媒体报道,ImageTragick软件中存在着漏洞,影响了用户的正常使用。同时,此报道也引起了大量网页开发人员的关注。他们正尝试通过解决一个远程代码执行变量的方式,来修复这一漏洞。

ImageTragick是一款广受欢迎的图片制作操作软件。它可以用来读、写和处理超过89种基本格式的图片文件,包括TIFF、JPEG、GIF以及PNG等等,具有一套功能强大且稳定的工具集。网页前端工作者通常用它来修改图片、转换图片格式或对一些发布在网络上的图片进行标注。无论你是否使用过这款软件,都应该对这一漏洞给予一定的关注。因为该漏洞的开发成本极低,极易被不法分子所利用。简单说,它其实就是在上世纪90年代出现过的安全漏洞的其中之一,即简单的shell命令行注入漏洞。而今天,随着技术的不断发展,在一些核心开发工具中,这种漏洞几乎已经不存在了。该漏洞与另一个影响深远的shell漏洞—Shellshock Bug(破壳漏洞)有着一定的相似之处。

即是说,我认为媒体关于此漏洞的报道,都忽视了其中重要的一点,即:即使开发人员修复了RCE向量(远程设备控制命令),这可能也无济于事。任何想通过ImageTragick来处理,已经被攻击者控制的图片的用户,都会面临巨大的安全隐患。

问题其实很简单:相较于ImageTragick展现出的优点,人们对于该软件中存在的这一漏洞,会感到有些惊讶。因为在软件开发人员看来。它实在过于“低级”。正是因为在设计之初,设计者没有考虑到命令行注入,这一历史悠久,但鲜为人知,具有严重威胁的安全漏洞的存在,而导致了今天这一情况的出现。几个月前,当人们还在讨论这一漏洞时,一位叫做Jodie Cunningham的研究员,就对该漏洞所使用的数据点进行了研究。Jodie采用开源的afl-fuzz工具对该软件的IM功能(Instant Messaging-即时通讯),进行了模糊测试,并且迅速找到了20多个其中存在的开发漏洞,以及大量能够进行拒绝服务攻击的漏洞。关于她的研究结果的样本,可在后面的网页里找到。([http://www.openwall.com/lists/oss-security/2014/12/24/1](http://www.openwall.com/lists/oss-security/2014/12/24/1))

Jodie所做的测试还可能仅仅停留在表面。在这之后,Hanno Boeck又找出了更多的bug。据我所知,Hanno找到这些bug,也仅仅是通过使用关闭shelf的模糊测试工具,并没有更多新的尝试。在这儿,我可以和你们打一个赌:由于缺乏一种对IM代码库进行重新设计的驱动力,此漏洞的持续趋势,在短期内将不会有改变。

对此,有如下几条关于使用ImageTragick的建议:

1. 如果你确实需要对一些安全信任度较低的图片,进行格式转换或尺寸缩小修改时,不要使用ImageMagick。将其转换为png库文件、jpeg-turbo库文件或gif库文件进行使用。这是一种很好的方法。同时你还可以在Chrome或Firefox浏览器中查看相关的源代码。这种实现方式将大大提高执行速度。

2. 如果你必须要使用ImageMagick对一些不受信任的图片进行处理,那么你就要考虑是否会遭到带有seccomp-bpf特性的沙盒代码的攻击,或另一种与其有着类似攻击机制的网络攻击,即:限制所有控件访问用户工作区,进而实施内核攻击。现在,我们所掌握的一些基本的沙盒防护技术,比如:Chroot(Change Root:改变程序执行时所参考的根目录位置)和UID 分离等,在面对此类攻击时,还无法取得太好的效果。

3. 如果以上两个办法都失效的话,那么就要果断地通过IM进行限制图片格式处理的设置。最低要求是要对每一个接收到的图片文件的标题进行检查,这也有助于当要调用代码自动识别功能函数时,可以明确地说明输入文件的格式。对于命令行调用功能,可通过如下代码实现:convert […other params…] — jpg:input-file.jpg jpg:output-file.jpg

在ImageMagick中所执行的JPEG、PNG和GIF格式文件的处理代码比PCX、TGA、SVG、PSD等其他格式文件的代码,要具有更好的稳定性。
