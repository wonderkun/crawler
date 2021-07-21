> 原文链接: https://www.anquanke.com//post/id/83728 


# Petya到底是个什么鬼？


                                阅读量   
                                **94541**
                            
                        |
                        
                                                                                    



 

[![](https://p0.ssl.qhimg.com/t018d07e0e3316f6cfa.jpg)](https://p0.ssl.qhimg.com/t018d07e0e3316f6cfa.jpg)



上个月底,德国老牌安全厂商歌德塔发布安全报告,报告中指出出现了一种名为Petya的新型敲诈木马。那么这个新型的敲诈木马到底是怎么回事呢?

**木马概述**

木马本身其实技术上并不复杂:木马用C语言编写,通过修改系统所在磁盘包括主引导记录(MBR)在内的前63个扇区的数据,实现开机自动加载木马写入的恶意代码的目的。而后再强制引发系统重启,让计算机自动加载恶意代码,进而加密用户磁盘并展示敲诈界面。

如上所述,两句话就能说明白木马的原理,但实际应用起来给我们的感受却是:简单!粗暴!但————有效!

**代码分析**

重启前的前期准备工作

由于木马的主要传播途径来自于网盘分享,所以木马做的唯一的伪装就是在图标上————伪装成了一个自解压程序:

[![](https://blogs.360.cn/360safe/files/2016/04/000_%E5%9B%BE%E6%A0%87.png)](https://blogs.360.cn/360safe/files/2016/04/000_%E5%9B%BE%E6%A0%87.png)

除此之外就不再有其他的伪装了,直切主题————打开C盘,并通过DeviceIOControl获取到C盘所在的屋里磁盘。

[![](https://blogs.360.cn/360safe/files/2016/04/010_%E6%89%93%E5%BC%80C%E7%9B%98.png)](https://blogs.360.cn/360safe/files/2016/04/010_%E6%89%93%E5%BC%80C%E7%9B%98.png)

[![](https://blogs.360.cn/360safe/files/2016/04/020_%E8%8E%B7%E5%8F%96C%E7%9B%98%E6%89%80%E5%9C%A8%E7%A3%81%E7%9B%98.png)](https://blogs.360.cn/360safe/files/2016/04/020_%E8%8E%B7%E5%8F%96C%E7%9B%98%E6%89%80%E5%9C%A8%E7%A3%81%E7%9B%98.png)

获取到磁盘之后,以可读可写的模式打开磁盘(其实就是为了写入):

[![](https://blogs.360.cn/360safe/files/2016/04/060_%E5%86%99%E5%85%A5%E7%A3%81%E7%9B%98.png)](https://blogs.360.cn/360safe/files/2016/04/060_%E5%86%99%E5%85%A5%E7%A3%81%E7%9B%98.png)

万事俱备,只欠东风————开始正式的写入了。木马写入的全部数据集中在磁盘的前63个扇区内,分为四个部分:1.修改磁盘第1个扇区(0柱面,0磁头,1扇区)的512字节内容————即修改MBR;2.将后续扇区空闲部分全部写入字符“7”(即HEX数据0x37);3.第35个扇区开始填入总长度为8192字节(0x2000字节,即16个扇区的空间)的恶意代码;4.第55个扇区开始填入长度为512字节的配置数据。
<li>
修改MBR
</li>
[![](https://blogs.360.cn/360safe/files/2016/04/070_%E4%BF%AE%E6%94%B9MBR.png)](https://blogs.360.cn/360safe/files/2016/04/070_%E4%BF%AE%E6%94%B9MBR.png)
<li>
用“7”填补空闲空间
</li>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blogs.360.cn/360safe/files/2016/04/061_%E5%86%99%E5%85%A5%E5%85%A87.png)
<li>
写入恶意代码
</li>
[![](https://blogs.360.cn/360safe/files/2016/04/071_ShellCode1.png)](https://blogs.360.cn/360safe/files/2016/04/071_ShellCode1.png)
<li>
写入配置数据
</li>
[![](https://blogs.360.cn/360safe/files/2016/04/072_ShellCode2.png)](https://blogs.360.cn/360safe/files/2016/04/072_ShellCode2.png)
改写的都写完了,就剩重启了。木马并没有用最小儿科的手段去执行系统的shutdown命令,而是调用了一个ntdll中的ZwRaiseHardError函数触发硬件异常来制造蓝屏,以此达到强制重启的目的:
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blogs.360.cn/360safe/files/2016/04/080_%E8%A7%A6%E5%8F%91%E8%93%9D%E5%B1%8F%E9%87%8D%E5%90%AF.png)
分析暂停,我们来看看磁盘
一直到此处,我们将分析暂停,看看此时的磁盘————包括MBR的前63个扇区的数据均已被木马修改,加入了恶意代码。但磁盘分区本身还并未被实质性的破坏。我们用工具打开磁盘可以清楚的看到已经被修改的MBR和被加入的恶意代码:
[![](https://blogs.360.cn/360safe/files/2016/04/090_%E8%A2%AB%E4%BF%AE%E6%94%B9%E5%90%8EMBR.png)](https://blogs.360.cn/360safe/files/2016/04/090_%E8%A2%AB%E4%BF%AE%E6%94%B9%E5%90%8EMBR.png)
[![](https://blogs.360.cn/360safe/files/2016/04/091_%E7%AC%AC35%E6%89%87%E5%8C%BA%E5%BC%80%E5%A7%8BShellCode.png)](https://blogs.360.cn/360safe/files/2016/04/091_%E7%AC%AC35%E6%89%87%E5%8C%BA%E5%BC%80%E5%A7%8BShellCode.png)
细看被修改的MBR代码,会在一开始便将第34扇区(此处计数是从0开始,也就是文章之前所说的第35个扇区处)的数据循环载入内存中并执行:
[![](https://blogs.360.cn/360safe/files/2016/04/201_MBR%E4%BB%A3%E7%A0%81.png)](https://blogs.360.cn/360safe/files/2016/04/201_MBR%E4%BB%A3%E7%A0%81.png)
继续跑起来!看看重启之后的场景
OK,此时我们让木马继续,触发系统蓝屏之后自动重启,会出现一段磁盘修复信息:
[![](https://blogs.360.cn/360safe/files/2016/04/102_Repairing.png)](https://blogs.360.cn/360safe/files/2016/04/102_Repairing.png)
如上图所示,系统会提示你正在修复C盘所在的文件系统,并用全大写的字体警示用户(虽然用英文写这些所谓的“警示”内容在国内完全水土不服)————千万不要停止关机,一旦你关机了你的数据就全毁了!<br>        然而事实上呢?你不关机你的数据也全毁了————因为这段提示信息根本就不是系统原本的修复程序,而是木马自己写入的欺骗性提示。而下方显示的进度数值却是有真实意义的:这个进度恰恰是恶意代码在加密你磁盘的进度!下图是直接使用工具打开磁盘,从病毒修改的磁盘数据中找到的对应的文字:
[![](https://blogs.360.cn/360safe/files/2016/04/103_%E8%99%9A%E5%81%87%E4%BF%AE%E5%A4%8D%E4%BF%A1%E6%81%AF%E5%AF%B9%E5%BA%94%E7%A3%81%E7%9B%98%E6%95%B0%E6%8D%AE.png)](https://blogs.360.cn/360safe/files/2016/04/103_%E8%99%9A%E5%81%87%E4%BF%AE%E5%A4%8D%E4%BF%A1%E6%81%AF%E5%AF%B9%E5%BA%94%E7%A3%81%E7%9B%98%E6%95%B0%E6%8D%AE.png)
在所谓的“文件系统修复”完成后,用户面对的便是一个闪瞎双眼的骷髅图标(1.截图无法展示闪烁效果,实际看到的是红白颜色切换的闪烁;2.平心而论这个界面制作的还是挺精良的!⊙﹏⊙b)
[![](https://blogs.360.cn/360safe/files/2016/04/100_%E9%87%8D%E5%90%AF%E7%94%BB%E9%9D%A2.png)](https://blogs.360.cn/360safe/files/2016/04/100_%E9%87%8D%E5%90%AF%E7%94%BB%E9%9D%A2.png)
按要求“Press Any Key”之后进入正题!是不是很熟悉?去下个洋葱浏览器(Tor Browser)然后访问我指定的链接,输入你的个人解密编码并交钱,拿到解密秘钥,才能让系统恢复正常!
[![](https://blogs.360.cn/360safe/files/2016/04/101_%E5%A8%81%E8%83%81%E4%BF%A1%E6%81%AF.png)](https://blogs.360.cn/360safe/files/2016/04/101_%E5%A8%81%E8%83%81%E4%BF%A1%E6%81%AF.png)
和之前流行了多年的CTB-Locker如出一辙的敲诈手法,只不过这次不再是加密你的特定文件了,而是加密你的整个磁盘……
**关于防范和修复**
这个木马虽然很独具匠心的调用ZwRaiseHardError函数而非shutdown命令来重启系统,但毕竟整个木马的设计思路都是建立在修改系统MBR基础上的,所以对于大多带有主防功能且和MBR木马对抗了这么多年的安全软件来说,在修改MBR这一个动作上就已经可以拦截了。加之根据我们的监控该木马并没有在国内大规模爆发,所以只要大家安装有靠谱的安全软件,对Petya木马就不必太过于恐慌。
但当你没有使用安全软件进行防护的话……那就牵扯到修复问题了。这个就比较麻烦了。
<li>
如果你是意识流神操作
</li>
假设你的意识足够好,手速足够快。只是一时大意不慎中招。一定要记得赶在进入那个假的“文件系统修复”界面之前彻底关机(此处建议拔电源)。如果你做到了————恭喜!后面的步骤不会很复杂。你只需要找到一个PE系统,让你的机器从U盘引导进入PE系统,然后用里面的任何关于引导修复的工具去重建MBR即可。
[![](https://blogs.360.cn/360safe/files/2016/04/110_%E9%87%8D%E5%BB%BAMBR.png)](https://blogs.360.cn/360safe/files/2016/04/110_%E9%87%8D%E5%BB%BAMBR.png)
因为此时虽然恶意代码已经写入,但还没有开始加密磁盘,只要你重建了MBR,正常的系统MBR是不会执行木马写入的恶意代码的。所以那些恶意代码只会成为一大段代码尸体————静静的躺在你的磁盘里,永远不会被执行。当然,如果你连尸体都不想要,在重建MBR之后,再执行一下下面那个“清楚保留扇区”,那么连尸体都会帮你清理干净的。(^o^)/~
<li>
如果你是个信息安全达人
</li>
如果你有经常备份系统的习惯,那么不多废话了……按照上面的步骤重建MBR之后,还原系统就好了
<li>
如果你什么准备都没有
</li>
如果这样那很不幸,但即便如此你其实依然不用付赎金。因为和典型的CTB-Locker不同,这个木马并没有更改你的任何文件,而只是破坏了磁盘整体的文件索引。所以如果你真的有很重要的文件需要恢复,并且不是很在乎系统本身是否还能启动,那你完全可以自己动手:
[![](https://blogs.360.cn/360safe/files/2016/04/302_%E6%81%A2%E5%A4%8D%E6%96%87%E4%BB%B6.png)](https://blogs.360.cn/360safe/files/2016/04/302_%E6%81%A2%E5%A4%8D%E6%96%87%E4%BB%B6.png)
但如果你希望是把整个系统完好无损的还原出来,那就需要比较专业的工具和专业的方法了,所以去找专业的数据恢复服务更为省心一些。
<li>
顺便说一句
</li>
此处顺带说一句,最近国内也出现了一款类似的修改MBR的敲诈木马:
[![](https://blogs.360.cn/360safe/files/2016/04/00000.jpg)](https://blogs.360.cn/360safe/files/2016/04/00000.jpg)
如果是这个木马的话,只需要按照上面重建MBR的步骤,之后再加一步找回丢失的分区表即可完成修复————因为该木马只破坏了分区表,而并没有对文件索引下手:
[![](https://blogs.360.cn/360safe/files/2016/04/111_%E6%90%9C%E7%B4%A2%E5%88%86%E5%8C%BA.png)](https://blogs.360.cn/360safe/files/2016/04/111_%E6%90%9C%E7%B4%A2%E5%88%86%E5%8C%BA.png)
[![](https://blogs.360.cn/360safe/files/2016/04/112_%E6%90%9C%E7%B4%A2%E6%95%B4%E4%B8%AA%E7%A3%81%E7%9B%98.png)](https://blogs.360.cn/360safe/files/2016/04/112_%E6%90%9C%E7%B4%A2%E6%95%B4%E4%B8%AA%E7%A3%81%E7%9B%98.png)
[![](https://blogs.360.cn/360safe/files/2016/04/113_%E6%90%9C%E7%B4%A2%E5%88%B0%E4%B8%BB%E5%88%86%E5%8C%BA.png)](https://blogs.360.cn/360safe/files/2016/04/113_%E6%90%9C%E7%B4%A2%E5%88%B0%E4%B8%BB%E5%88%86%E5%8C%BA.png)
[![](https://blogs.360.cn/360safe/files/2016/04/114_%E4%BF%9D%E5%AD%98.png)](https://blogs.360.cn/360safe/files/2016/04/114_%E4%BF%9D%E5%AD%98.png)
[![](https://blogs.360.cn/360safe/files/2016/04/115_%E4%BF%9D%E5%AD%98%E6%9B%B4%E6%94%B9.png)](https://blogs.360.cn/360safe/files/2016/04/115_%E4%BF%9D%E5%AD%98%E6%9B%B4%E6%94%B9.png)

<footer>Posted in [样本分析](http://blogs.360.cn/360safe/category/virus/).
</footer>