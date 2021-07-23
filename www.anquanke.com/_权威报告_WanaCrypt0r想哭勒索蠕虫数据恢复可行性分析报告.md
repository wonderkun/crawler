> 原文链接: https://www.anquanke.com//post/id/86125 


# 【权威报告】WanaCrypt0r想哭勒索蠕虫数据恢复可行性分析报告


                                阅读量   
                                **187666**
                            
                        |
                        
                                                                                    



**[![](https://p0.ssl.qhimg.com/t01b37c2ba500592fac.png)](https://p0.ssl.qhimg.com/t01b37c2ba500592fac.png)**

**360追日团队官网：**[**http://zhuiri.360.cn/**](http://zhuiri.360.cn/)** **

**<br>**

**第一章	前言**

近日，360互联网安全中心发现全球多个国家和地区的机构及个人电脑遭受到了一款新型勒索软件攻击，并于5月12日国内率先发布紧急预警。该款勒索软件在短时间内在全球范围内爆发了广泛的攻击活动，据不完全统计，它在爆发后的几个小时内就迅速攻击了99个国家的近万台设备，并在大量企业组织和个人间蔓延。外媒和多家安全公司将其命名为“WanaCrypt0r”（直译：“想哭勒索蠕虫”）。

通常，常规的勒索病毒是一种趋利明显的恶意程序，它会使用非对称加密算法加密受害者电脑内的重要文件并以此来进行勒索，向受害者索要赎金，除非受害者交出勒索赎金，否则被加密的文件无法被恢复。而新型勒索软件的“想哭勒索蠕虫”尤其致命，它利用了窃取自美国国家安全局的黑客工具EternalBlue（直译：“永恒之蓝”）实现了全球范围内的快速传播，在短时间内造成了巨大损失。继5月12日WanaCrypt0r全球攻击爆发以来，360核心安全部门对该勒索蠕虫保持了高度关注，部门各团队紧密协作，首家发布了一系列针对该蠕虫的查杀、免疫和文件恢复解决方案。

**360核心安全部门追日团队深入分析病毒原理，发现了其加密数据最精准的恢复技术，使用此技术360在全球独家发布了“想哭勒索蠕虫数据恢复工具”帮助病毒受害者恢复被蠕虫加密文件，可以达到目前最全最快的数据恢复效果，我们希望本篇技术报告可以帮助大家了解该蠕虫的核心技术原理，并对恢复被加密数据的可行性做进一步探讨。**

<br>

**第二章	加密文件核心流程分析**

蠕虫释放一个加密模块到内存，直接在内存加载该DLL。DLL导出一个函数TaskStart用于启动整个加密的流程。

程序动态获取文件系统和加密相关的API函数，以此来躲避静态查杀。

[![](https://p4.ssl.qhimg.com/t014d8d80b1f9963009.png)](https://p4.ssl.qhimg.com/t014d8d80b1f9963009.png)

**1.	加密入口**

调用SHGetFolderPathW获取了桌面和文档文件夹的路径，调用10004A40函数获得非当前用户的桌面和文档文件夹，分别调用EncryptFolder对文件夹进行加密操作

[![](https://p0.ssl.qhimg.com/t013f6f3ed8270a8f22.png)](https://p0.ssl.qhimg.com/t013f6f3ed8270a8f22.png)

从Z倒序遍历盘符直到C，遍历两次，第一次遍历本地盘符（跳过光驱），第二次遍历移动盘符，分别调用EncryptFolder对文件夹进行加密操作

[![](https://p2.ssl.qhimg.com/t0141ddf0509345e98f.png)](https://p2.ssl.qhimg.com/t0141ddf0509345e98f.png)

**2.	文件遍历**

EncryptFolder函数是一个递归函数，递归遍历文件夹，按照下图的描述搜集文件信息：

[![](https://p3.ssl.qhimg.com/t011ba80bc24761b151.png)](https://p3.ssl.qhimg.com/t011ba80bc24761b151.png)

遍历过程中排除的路径或者文件夹名称：

去除路径中盘符或主机名后进行比较

\Intel

\ProgramData

\WINDOWS

\Program Files

\Program Files (x86)

\AppData\Local\Temp

\Local Settings\Temp

文件夹名称（完全相等）

Temporary Internet Files

This folder protects against ransomware. Modifying it will reduce protection

Content.IE5

其中有一个很有意思的目录名“ This folder protects against ransomware. Modifying it will reduce protection”，通过Google查询，发现其是国外的一款名为ransomfree的勒索防御软件创建的防御目录。

在遍历文件的过程中，会获取文件信息（大小等），并且根据后缀名使用下表的规则对文件进行分类（type）：

[![](https://p0.ssl.qhimg.com/t011679a97d5a648e09.png)](https://p0.ssl.qhimg.com/t011679a97d5a648e09.png)

type列表1：

```
".doc",".docx",".xls",".xlsx",".ppt",".pptx",".pst",".ost",".msg",".eml",".vsd",".vsdx",".txt",".csv",".rtf",".123",".wks",".wk1",".pdf",".dwg",".onetoc2",".snt",".jpeg",".jpg"
```

type列表2：

```
".docb",".docm",".dot",".dotm",".dotx",".xlsm",".xlsb",".xlw",".xlt",".xlm",".xlc",".xltx",".xltm",".pptm",".pot",".pps",".ppsm",".ppsx",".ppam",".potx",".potm",".edb",".hwp",".602",".sxi",".sti",".sldx",".sldm",".sldm",".vdi",".vmdk",".vmx",".gpg",".aes",".ARC",".PAQ",".bz2",".tbk",".bak",".tar",".tgz",".gz",".7z",".rar",".zip",".backup",".iso",".vcd",".bmp",".png",".gif",".raw",".cgm",".tif",".tiff",".nef",".psd",".ai",".svg",".djvu",".m4u",".m3u",".mid",".wma",".flv",".3g2",".mkv",".3gp",".mp4",".mov",".avi",".asf",".mpeg",".vob",".mpg",".wmv",".fla",".swf",".wav",".mp3",".sh",".class",".jar",".java",".rb",".asp",".php",".jsp",".brd",".sch",".dch",".dip",".pl",".vb",".vbs",".ps1",".bat",".cmd",".js",".asm",".h",".pas",".cpp",".c",".cs",".suo",".sln",".ldf",".mdf",".ibd",".myi",".myd",".frm",".odb",".dbf",".db",".mdb",".accdb",".sql",".sqlitedb",".sqlite3",".asc",".lay6",".lay",".mml",".sxm",".otg",".odg",".uop",".std",".sxd",".otp",".odp",".wb2",".slk",".dif",".stc",".sxc",".ots",".ods",".3dm",".max",".3ds",".uot",".stw",".sxw",".ott",".odt",".pem",".p12",".csr",".crt",".key",".pfx",".der"
```

**3.	文件处理队列**

WanaCrypt0r为了能尽快的加密其认为重要的用户文件，设计了一套复杂的优先级队列。

队列优先级：

i.	对type2（满足后缀列表1）进行加密（小于0x400的文件会降低优先级）

ii.	对type3（满足后缀列表2）进行加密（小于0x400的文件会降低优先级）

iii.	处理剩下的文件（小于0x400的文件），或者其他一些文件

**4.	加密逻辑**

加密过程采用RSA+AES的方式完成，其中RSA加密过程使用了微软的CryptoAPI，AES代码则静态编译到DLL中。加密流程如下图所示：

[![](https://p4.ssl.qhimg.com/t011ee1e8583702cd19.png)](https://p4.ssl.qhimg.com/t011ee1e8583702cd19.png)

使用的密钥概述：

[![](https://p4.ssl.qhimg.com/t011cebbd73307cf42c.png)](https://p4.ssl.qhimg.com/t011cebbd73307cf42c.png)

加密后的文件格式示意：

[![](https://p0.ssl.qhimg.com/t01c1c97ffadd952a15.png)](https://p0.ssl.qhimg.com/t01c1c97ffadd952a15.png)

值得注意的是，在加密过程中，程序会随机选取一部分文件使用内置的RSA公钥来进行加密，这里的目的是解密程序提供的免费解密部分文件功能。

[![](https://p5.ssl.qhimg.com/t0184c97d9beb3bd02b.png)](https://p5.ssl.qhimg.com/t0184c97d9beb3bd02b.png)

能免费解密的文件路径在文件f.wnry中，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01334ad8de759cd275.png)

**5.	随机数填充**

在完成加密之后，WanaCrypt0r会对其认为重要的文件进行随机数填充，然后将文件移动到指定的临时文件夹目录然后删除。此举用于对抗文件恢复类软件，同时兼顾加密文件的速度。

被随机数填充的文件需要满足以下几点：

在特殊目录（桌面，我的文档，用户文件夹）

文件小于200M

文件后缀在type列表1

填充的逻辑：

如果文件小于0x400,直接覆盖对应长度的随机数。

如果文件大于0x400,对文件距离末尾0x400处进行覆盖。

再次重定位文件指针到文件头，以0x40000大小的缓冲区为单位向写随机数直到文件末尾。

[![](https://p2.ssl.qhimg.com/t0190edb57e8f98fbb3.png)](https://p2.ssl.qhimg.com/t0190edb57e8f98fbb3.png)

[![](https://p3.ssl.qhimg.com/t0193e91184ce6790ac.png)](https://p3.ssl.qhimg.com/t0193e91184ce6790ac.png)

**6.	文件删除操作**

WanaCrypt0r首先尝试将样本移动到临时文件夹，生成一个临时文件，然后再尝试多种方法删除文件。

当采用遍历磁盘的方式加密文件的时候，会在当前盘符生成“$RECYCLE”+ 全局自增量+”.WNCYRT”(eg： "D:\$RECYCLE\1.WNCRYT")的临时文件。特别的，当盘符为系统盘（eg：C）时，使用的是系统的临时目录（%temp%）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018566e74d505fe4c2.png)

之后进程以固定时间间隔启动taskdl.exe来删除临时文件夹下的文件。

<br>

**第三章	数据恢复可行性分析**

根据对WannaCry蠕虫的执行逻辑进行分析，该蠕虫在加密线程中会对满足条件的文件用随机数或0x55进行覆写，从而彻底破坏文件的结构并防止数据被恢复，但是只限定于特定的文件夹和特定的后缀名。也就是说该蠕虫只对满足条件的文件进行了写覆写操作，受害者机器上仍然有很多的文件未被覆写，这就为数据恢复提供了可能。

在删除线程中，蠕虫是先将源文件通过MoveFileEx函数移动到其创建的临时文件夹下，最后统一进行删除。在这个过程中源文件的文件名会发生改变，常规数据恢复软件不知道这个文件操作逻辑，导致大部分文件无法恢复，只能恢复小部分文件，恢复数据效果极差。

另一方面，因为删除操作和加密操作在不同的线程中，受用户环境的影响，线程间的条件竞争可能存在问题，从而导致移动源文件的操作失败，使得文件在当前位置被直接删除，在这种情况下被加密的文件有很大概率可以进行直接恢复。但是满足这种情形的文件毕竟是少数，如果采用常规数据恢复软件则只能恢复少量此类文件。

根据以上分析，我们发现了除系统盘外的文件，用我们精细化处理的方法进行数据恢复，被加密的文件其实是有很大概率可以完全恢复的。据此360开发了专门的恢复工具2.0版，以期帮助在此次攻击中广大的受害者恢复加密数据：

[http://dl.360safe.com/recovery/RansomRecovery.exe?from=360zhuiri](http://dl.360safe.com/recovery/RansomRecovery.exe?from=360zhuiri) 

继14日凌晨360全球首家发布恢复工具，为病毒受害者抢救了部分文件后。此次更新发布2.0版工具进一步挖掘病毒加密逻辑漏洞，清除病毒防止二次感染，并利用多重算法深度关联出可恢复文件并对受害者的文件进行免费解密，一站式解决蠕虫勒索软件带来的破坏，最大程度低保护了用户的数据安全，成功率遥遥领先于其他数据恢复类产品！

[![](https://p1.ssl.qhimg.com/t0150fc609a6c455090.jpg)](https://p1.ssl.qhimg.com/t0150fc609a6c455090.jpg)

<br>

**第四章	总结**

WannaCry蠕虫的大规模爆发得益于其利用了MS-17-010漏洞，使得其在传统的勒索病毒的基础上具备了自我复制、主动传播的特性。在除去攻击荷载的情况下，勒索病毒最重要的是其勒索技术框架。勒索文件加密技术是使用非对称加密算法RSA-2048加密AES密钥，然后每个文件使用一个随机AES-128对称加密算法加密，在没有私钥和密钥的前提下要穷尽或破解RSA-2048和AES-128加密算法，按目前的计算能力和技术是不可破解的。但是作者在处理文件加密过程中的一些疏漏，大大增加了我们恢复文件的可能性，如果第一时间及时抢救，用户是能够恢复大部分数据的。

另外由于勒索赎金交付技术是使用的比特币，比特币具有匿名性，比特币地址的生成无需实名认证，通过地址不能对应出真实身份，比特币地址的同一拥有者的不同账号之间也没有关联。所以基于加密算法的不可破解特性和比特币的匿名特性，勒索病毒这类趋利明显的恶意攻击仍然会长时间流行，大家仍需要提高警惕。

<br>

**360追日团队（Helios Team）**

360 追日团队（Helios Team）是360公司高级威胁研究团队，从事APT攻击发现与追踪、互联网安全事件应急响应、黑客产业链挖掘和研究等工作。团队成立于2014年12月，通过整合360公司海量安全大数据，实现了威胁情报快速关联溯源，独家首次发现并追踪了三十余个APT组织及黑客团伙，大大拓宽了国内关于黑客产业的研究视野，填补了国内APT研究的空白，并为大量企业和政府机构提供安全威胁评估及解决方案输出。

**已公开APT相关研究成果**

[![](https://p1.ssl.qhimg.com/t01145db6017e6d3037.png)](https://p1.ssl.qhimg.com/t01145db6017e6d3037.png)

**联系方式**

**邮箱：360zhuiri@360.cn**

微信公众号：360追日团队

扫描下方二维码关注微信公众号

[![](https://p1.ssl.qhimg.com/t016b2dd452d92d8e0f.png)](https://p1.ssl.qhimg.com/t016b2dd452d92d8e0f.png)
