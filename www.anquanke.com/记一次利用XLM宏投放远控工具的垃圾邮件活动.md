> 原文链接: https://www.anquanke.com//post/id/178366 


# 记一次利用XLM宏投放远控工具的垃圾邮件活动


                                阅读量   
                                **210219**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t012edb6ca6f443cd7e.jpg)](https://p4.ssl.qhimg.com/t012edb6ca6f443cd7e.jpg)



五月假期后上班的前几天，发现了一个很有意思的邮件，附件是一个xls文档。依稀记得这个文档在5月5号前后VT上并没有多少家杀软报毒。在虚拟机中打开文档，呈现了这样的界面。

[![](https://p4.ssl.qhimg.com/t0122978f612a756291.png)](https://p4.ssl.qhimg.com/t0122978f612a756291.png)

想要看一下宏代码，却发现alt+F11或者oletools等工具并不能提取出宏代码。一时之间还以为OLE流中有精心构造的数据可以出发漏洞并造成RCE，然而用windbg调了半天EXCEL.EXE，发现msiexec并不是由shellcode执行的，而是EXCEL代码本身的逻辑。后来经过[银雁冰](https://www.anquanke.com/member/117972)的提示，在文档隐藏的workbook中找打了解开问题的答案：文档的作者有意隐藏了其他workbook，并在其中嵌入了XLM（excel 4.0）宏。

[![](https://p1.ssl.qhimg.com/t013c394a9fc53ab0da.png)](https://p1.ssl.qhimg.com/t013c394a9fc53ab0da.png)

所以服务器的cykom2应该是一个msi安装包，将该文件下载解压即可分析。



## cykom2

文件下载并解压，内部文件目录如下所示：

[![](https://p4.ssl.qhimg.com/t01fadc059772521830.png)](https://p4.ssl.qhimg.com/t01fadc059772521830.png)

先看一下main函数。

[![](https://p0.ssl.qhimg.com/t017725d04799fa67a7.png)](https://p0.ssl.qhimg.com/t017725d04799fa67a7.png)

初步看，这个样本会检查系统是否运行foundation这个服务，如果有该服务运行，停止服务并删除。

这个函数中有很多sub_411C60的函数调用，我们来看一下这个函数

[![](https://p1.ssl.qhimg.com/t01c3d2078db8b8c9c7.png)](https://p1.ssl.qhimg.com/t01c3d2078db8b8c9c7.png)

[![](https://p3.ssl.qhimg.com/t017c7b88a6fcdb73ef.png)](https://p3.ssl.qhimg.com/t017c7b88a6fcdb73ef.png)

分析结果表明，这个函数的行为类似于GetProcAddress(LoadLibrary(), char*pProc);函数定义是这样的：函数传进两个参数，第一个是函数名移位异或加密的值，另一个是选择函数所在dll在函数体switch结构中的case值。然后通过解析进程PEB，再调用LoadLibrary_EAT函数获取dll映象基址。然后按照PE文件在内存中的加载结构解析export table，将到处函数名移位异或加密并与第一个参数匹配。为方便阅读，特提取分析该样本的虚拟机的kernel32.dll的IMAGE_EXPORT_DIRECTORY结构体如下：

[![](https://p4.ssl.qhimg.com/t016219c9dcf61565d9.png)](https://p4.ssl.qhimg.com/t016219c9dcf61565d9.png)

我们再回头看一下LoadLibrary_EAT函数：

为方便阅读，代码已经加了注释，同样是采用遍历export name table，匹配加密的key的方式获取kernel32!LoadLibraryA()的地址，并用它获取待加载dll的基址。

[![](https://p4.ssl.qhimg.com/t01618bea320e86095e.png)](https://p4.ssl.qhimg.com/t01618bea320e86095e.png)

所以给Main函数的代码做完梳理之后，是这样的：

[![](https://p0.ssl.qhimg.com/t01a96ddb1ca27b53ee.png)](https://p0.ssl.qhimg.com/t01a96ddb1ca27b53ee.png)

[![](https://p3.ssl.qhimg.com/t012583e88c32109530.png)](https://p3.ssl.qhimg.com/t012583e88c32109530.png)

从上面的main函数来看，这个样本是一个downloader，主要行为是：从服务器下载文件，解密并释放到Mircosofts_HeLP目录下，命名为wsus.exe，并启动进程或创建服务以完成样本的落地。下面看动态调试：

拼接临时文件目录并下载临时文件：

[![](https://p5.ssl.qhimg.com/t01b631eb479e04596b.png)](https://p5.ssl.qhimg.com/t01b631eb479e04596b.png)

[![](https://p5.ssl.qhimg.com/t01c895b941ef6e0ce4.png)](https://p5.ssl.qhimg.com/t01c895b941ef6e0ce4.png)

[![](https://p5.ssl.qhimg.com/t01090c278d2d8f6f0b.png)](https://p5.ssl.qhimg.com/t01090c278d2d8f6f0b.png)

[![](https://p0.ssl.qhimg.com/t0109af176985836a88.png)](https://p0.ssl.qhimg.com/t0109af176985836a88.png)

然后申请一段内存，然后把下载的内容释放到缓存当中，并使用RC4解密，利用gey5453gdfygre作为Key构造的Sbox如下所示：

[![](https://p0.ssl.qhimg.com/t01e96ea154df25cc58.png)](https://p0.ssl.qhimg.com/t01e96ea154df25cc58.png)

解密后的文件如下所示：

[![](https://p5.ssl.qhimg.com/t016b0461d2a630728e.png)](https://p5.ssl.qhimg.com/t016b0461d2a630728e.png)

然后将缓存释放到wsus.exe中，并加载。如果当前用户没有管理员权限，则启动进程，反之，则注册服务或开机启动项。

[![](https://p1.ssl.qhimg.com/t016afcf5fa57fea4eb.png)](https://p1.ssl.qhimg.com/t016afcf5fa57fea4eb.png)

[![](https://p5.ssl.qhimg.com/t013e70ae2fdf754328.png)](https://p5.ssl.qhimg.com/t013e70ae2fdf754328.png)

[![](https://p5.ssl.qhimg.com/t013e70ae2fdf754328.png)](https://p5.ssl.qhimg.com/t013e70ae2fdf754328.png)

由于创建服务的启动类型为auto start，所以wsus.exe中一定有一个SCM去管理服务的启动过程。



## Wsus.exe

数字签名如下：

[![](https://p2.ssl.qhimg.com/t013accffa88efa0c6d.png)](https://p2.ssl.qhimg.com/t013accffa88efa0c6d.png)

Wsus.exe作为服务启动，所以样本代码中应该有一个SCManger。所以，在静态分析时找到了SCM的代码：

[![](https://p2.ssl.qhimg.com/t0134daed72b5a1f029.png)](https://p2.ssl.qhimg.com/t0134daed72b5a1f029.png)

[![](https://p3.ssl.qhimg.com/t019ad44168ce0df1d9.png)](https://p3.ssl.qhimg.com/t019ad44168ce0df1d9.png)

所以服务函数应该是sub_402A10。

[![](https://p0.ssl.qhimg.com/t01d776a16579d86d38.png)](https://p0.ssl.qhimg.com/t01d776a16579d86d38.png)

StartAddress函数

[![](https://p2.ssl.qhimg.com/t01630c69686fcfa4bf.png)](https://p2.ssl.qhimg.com/t01630c69686fcfa4bf.png)

[![](https://p1.ssl.qhimg.com/t01c2348ea9ef258e06.png)](https://p1.ssl.qhimg.com/t01c2348ea9ef258e06.png)

上面的代码表明，wsus.exe的代码中，有一个SCM，会创建线程执行线程，线程的一部分行为是：用 –nogui参数执行自身。

随着深入的静态分析，发现这个样本是一个重新编译的FlawedAmmyy<br>
RAT工具。原因在于代码作者在编写样本时，大量使用和修改了Ammyy Admin<br>
V3的代码，。鉴于二进制文件的静态分析中有很多麻烦的类和虚函数的标记工作，为了更彻底地分析样本，需要通过动态调试和部分源代码的参考，完成类和虚表的标记。

[![](https://p4.ssl.qhimg.com/t01890227c9d450a75d.png)](https://p4.ssl.qhimg.com/t01890227c9d450a75d.png)

在对程序的类和部分虚表进行标记后，WinMain函数的结构就比较明显了。

[![](https://p1.ssl.qhimg.com/t01fff84bb15ce8050b.png)](https://p1.ssl.qhimg.com/t01fff84bb15ce8050b.png)

[![](https://p1.ssl.qhimg.com/t014a6010d3c8f96ce6.png)](https://p1.ssl.qhimg.com/t014a6010d3c8f96ce6.png)

[![](https://p5.ssl.qhimg.com/t0165a9fab7a19a5614.png)](https://p5.ssl.qhimg.com/t0165a9fab7a19a5614.png)

[![](https://p0.ssl.qhimg.com/t0188f7f2b1eaed8ff6.png)](https://p0.ssl.qhimg.com/t0188f7f2b1eaed8ff6.png)

Main函数的主要行为通过解析参数并根据参数内容配置，启动服务。（前文中关于SCM代码的部分）

服务信息配置完毕后，启动自身。

[![](https://p1.ssl.qhimg.com/t013726d9b6be5cea0c.png)](https://p1.ssl.qhimg.com/t013726d9b6be5cea0c.png)

以nogui参数启动后，仍然执行main函数，检查服务配置。并解密出要连接的地址。

[![](https://p2.ssl.qhimg.com/t01bd5f4b5878efdedc.png)](https://p2.ssl.qhimg.com/t01bd5f4b5878efdedc.png)

这个函数的伪代码如下：

[![](https://p0.ssl.qhimg.com/t011945488d4dc97012.png)](https://p0.ssl.qhimg.com/t011945488d4dc97012.png)

实际调试时，该地址已失效，所以无法成功建立连接。

[![](https://p1.ssl.qhimg.com/t014c6308886ce297be.png)](https://p1.ssl.qhimg.com/t014c6308886ce297be.png)

如能成功连接远程服务器，样本会采集主机信息并生成上线包，并根据回包的命令在受害主机执行动作：

[![](https://p5.ssl.qhimg.com/t017ff1542745257ff8.png)](https://p5.ssl.qhimg.com/t017ff1542745257ff8.png)

[![](https://p1.ssl.qhimg.com/t0112659ea5a057da40.png)](https://p1.ssl.qhimg.com/t0112659ea5a057da40.png)

代码静态分析和源代码比对如下所示：

[![](https://p4.ssl.qhimg.com/t01a7faf7e0fc643997.png)](https://p4.ssl.qhimg.com/t01a7faf7e0fc643997.png)

由于篇幅问题，其他内容这里就不便贴出来了。



## 小结

从整个攻击流程看，攻击者用含有XLM宏的文档作为入口，MSI安装包作为中间节点，投放FlawedAMMYY远控工具的行为，符合TA505这个黑产组织的特点。从样本时间戳和文件创建时间来看，这一波攻击应该是从五月份开始的，而仅仅十天，C2就失活了，这是我没有想到的。从文档的内容看，大概率是在中国投放的了，由于没有更多的渠道，这批垃圾邮件，在中国投放了多少，以及这是不是TA505准备在中国境内活动的信号，我也无从得知。如果有人感兴趣，并且手上有相关资源，倒是可以深入探究一下。



## IoC

xls文档 ADDE5C61F5397A807C23B5DFC30D89E8<br>
cykom2 91C338FC7194375FF5E71F9681C0A74B<br>
wsus.exe F48CBE8773334E97FC8FA6FCA39B0A85

链接地址：<br>
slemend[.]com/sykom2<br>
5.149.254.25/1[.]tmp<br>
169.239.129[.]103



### <a class="reference-link" name="%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5"></a>参考链接

[https://github.com/KbaHaxor/Ammyy-v3](https://github.com/KbaHaxor/Ammyy-v3)<br>[https://brica.de/alerts/alert/public/1249375/si-lab-flawedammyy-leveraging-undetected-xlm-macros-as-an-infection-vehicle/](https://brica.de/alerts/alert/public/1249375/si-lab-flawedammyy-leveraging-undetected-xlm-macros-as-an-infection-vehicle/)
