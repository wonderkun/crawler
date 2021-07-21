> 原文链接: https://www.anquanke.com//post/id/86681 


# 【病毒分析】新勒索病毒变种GlobeImposter（江湖骗子）分析


                                阅读量   
                                **178801**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fortinet.com
                                <br>原文地址：[http://blog.fortinet.com/2017/08/05/analysis-of-new-globeimposter-ransomware-variant](http://blog.fortinet.com/2017/08/05/analysis-of-new-globeimposter-ransomware-variant)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01a0aec07e6ea05f7a.jpg)](https://p4.ssl.qhimg.com/t01a0aec07e6ea05f7a.jpg)

译者：[an0nym0u5](http://bobao.360.cn/member/contribute?uid=578844650)

预估稿费：160RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**引子**

****

在过去的几天里，FortiGuard实验室捕捉到一些JS脚本，基于我的分析，这些脚本被用来传播新勒索病毒变种GlobeImposter（江湖骗子），我选择了其中一个文件并进行了快速分析，我分析的病毒变种版本为726。图1展示了我们捕捉到的JS文件的一部分，可以看到以“IMG_”开头的文件都是GlobeImposter病毒的下载程序。

 [![](https://p2.ssl.qhimg.com/t016d083ef3deaf4722.png)](https://p2.ssl.qhimg.com/t016d083ef3deaf4722.png)

图1 捕捉到的JS文件列表



**下载并执行JS**

****

当JS文件“IMG_8798.js”被执行时它会从站点“[http://wendybull.com.au/87wefhi??JWbXSIl=JWbXSIl](http://wendybull.com.au/87wefhi??JWbXSIl=JWbXSIl)”同步下载GlobeImposter病毒并执行，下载的文件名为87wefhi.txt.exe，接下来分析一下该病毒文件在受害者主机的运作机制。当GlobeImposter运行时会动态往一个堆空间注入代码，然后创建标记为“CREATE_SUSPENDED”的子进程，创建这个挂起子进程后它的代码会被之前注入堆空间的代码替换掉，当子进程处于继续执行状态时注入到堆空间的代码会被执行，这是GlobeImposter功能模块的主要行为，图2展示了GlobeImposter病毒执行时的进程树。

 [![](https://p5.ssl.qhimg.com/t0187689666a6f45038.png)](https://p5.ssl.qhimg.com/t0187689666a6f45038.png)

图2 进程树

初始进程通过调用“继续执行线程”来执行它的子进程然后退出，以下所有的分析都是关于该子进程的。



**GlobeImposter病毒子进程**

****

首先，该子进程调用API函数**SetThreadExecutionState**并传值0x80000041H给它，有了参数值0x80000041H，勒索病毒在加密文件时Windows系统就不会睡眠，当勒索病毒子进程完成加密后会再次调用SetThreadExecutionState函数并传值0x80000000。为了加大被破解的难度，该病毒代码的大部分字符串参数还有API部分都做了加密，当运行时再动态解密。再就是解密被排除在外的文件夹和文件扩展名，这个版本中该病毒设置了两个不被加密的列表，当病毒遍历受害者主机上的所有文件夹及文件时会跳过这两个列表中的文件夹和文件扩展名在该列表中的文件。以下是不会被加密的列表：

不会被加密的文件夹列表（共44个）：

Windows, Microsoft, Microsoft Help, Windows App Certification Kit, Windows Defender, ESET, COMODO, Windows NT, Windows Kits, Windows Mail, Windows Media Player, Windows Multimedia Platform, Windows Phone Kits, Windows Phone Silverlight Kits, Windows Photo Viewer, Windows Portable Devices, Windows Sidebar, WindowsPowerShell, Temp, NVIDIA Corporation, Microsoft.NET, Internet Explorer, Kaspersky Lab, McAfee, Avira, spytech software, sysconfig, Avast, Dr.Web, Symantec, Symantec_Client_Security, system volume information, AVG, Microsoft Shared, Common Files, Outlook Express, Movie Maker, Chrome, Mozilla Firefox, Opera, YandexBrowser, ntldr, Wsus, ProgramData.

不会被加密的文件扩展名（共170个）：

.$er .4db .4dd .4d .4mp .abs .abx .accdb .accdc .accde .accdr .accdt .accdw .accft .adn .adp .aft .ahd .alf .ask .awdb .azz .bdb .bib .bnd .bok .btr .cdb .cdb .cdb .ckp .clkw .cma .crd .daconnections .dacpac .dad .dadiagrams .daf .daschema .db .db-shm .db-wa .db2 .db3 .dbc .dbf .dbf .dbk .dbs .dbt .dbv .dbx .dcb .dct .dcx .dd .df1 .dmo .dnc .dp1 .dqy .dsk .dsn .dta .dtsx .dx .eco .ecx .edb .emd .eq .fcd .fdb .fic .fid .fi .fm5 .fmp .fmp12 .fmps .fo .fp3 .fp4 .fp5 .fp7 .fpt .fzb .fzv .gdb .gwi .hdb .his .ib .idc .ihx .itdb .itw .jtx .kdb .lgc .maq .mdb .mdbhtm .mdf .mdn .mdt .mrg .mud .mwb .myd .ndf .ns2 .ns3 .ns4 .nsf .nv2 .nyf .oce .odb .oqy .ora .orx .owc .owg .oyx .p96 .p97 .pan .pdb .pdm .phm .pnz .pth .pwa .qpx .qry .qvd .rctd .rdb .rpd .rsd .sbf .sdb .sdf .spq .sqb .sq .sqlite .sqlite3 .sqlitedb .str .tcx .tdt .te .teacher .tmd .trm .udb .usr .v12 .vdb .vpd .wdb .wmdb .xdb .xld .xlgc .zdb .zdc



**重定位和启动组**

****

再往后，病毒进程会自复制到“**%AllUserProfile%Public**”路径下，并在受害者的Windows主机注册表中添加新文件到启动组中，这可以实现病毒在系统启动时自动执行。图3表示GlobeImposter病毒已经添加进了Windows注册表的启动组中（….RunOnceCerificatesCheck）。

 [![](https://p3.ssl.qhimg.com/t010c12edade287d7c8.png)](https://p3.ssl.qhimg.com/t010c12edade287d7c8.png)

图3 Windows注册表中的启动组



**准备工作**

****

为了防止受害者从磁盘区阴影复制服务中恢复被加密的文件，GlobeImposter病毒在一个可执行批处理文件中调用了

```
vssadmin.exe Delete Shadows /All /Quiet
```

以删除所有的阴影磁盘卷，在该批处理文件中又清理了保存在系统注册表中和**%UserProfile%DocumentsDefault.rdp**文件中的远程桌面信息，在文件加密工作完成后批处理文件又会被调用一次，图4展示了批处理文件的内容：

 [![](https://p4.ssl.qhimg.com/t018084861571e10a21.png)](https://p4.ssl.qhimg.com/t018084861571e10a21.png)

图4 批处理文件

下一步，该病毒会初始化加密相关的密钥、数据等，用2048位的RSA算法加密文件，密钥相关的部分数据保存在新创建的文件“**%AllUserProfile%Public`{`hex numbers`}` **“中，`{`hex numbers`}`名来源于受害者主机的硬件信息。



**加密文件之前做了什么**

****

GlobeImposter病毒在加密文件之前会杀掉一些运行中的进程并产生一个html文件，这是开始加密文件之前的最后两步。该病毒通过调用**taskkill.exe**来杀掉运行中的名字包含”sql“、”outlook“、”ssms“、”postgre“、”1c“、”excel“、”word“等的进程，杀掉的这些进程可能会释放它们在使用的一些文件，这将导致GlobeImposter病毒会加密更多的文件。图5展示了以上过程的伪代码：

 [![](https://p1.ssl.qhimg.com/t0184328430dfee7d1a.png)](https://p1.ssl.qhimg.com/t0184328430dfee7d1a.png)

图5 杀掉匹配的进程

随后在文件被加密的文件夹下会产生一个HTML文件，该文件随后会被清除，这个HTML文件告知受害者系统文件已被加密并提供了如何支付以获取解密文件的方法，这个HTML文件包含一个私有ID和该可执行程序的解密信息。当你访问支付页面时这个私有ID会发往服务器，攻击者通过这个ID来识别你并生成解密密钥，图6是这个HTML文件内容的截图：

 [![](https://p0.ssl.qhimg.com/t016cf8c6ae99028d61.png)](https://p0.ssl.qhimg.com/t016cf8c6ae99028d61.png)

图6 RECOVER-FILES-726.html 内容



**加密文件进程**

****

当GlobeImposter病毒开始加密文件时，它会扫描受害者主机所有分区的文件并进行加密，当然之前提到的在被排除列表中的文件及文件夹不在加密范围之内，在读取文件后利用RSA算法开始加密文件内容并覆盖掉文件原来的内容，私有ID也会在被加密文件的内容里。图7展示了加密文件内容：

 [![](https://p0.ssl.qhimg.com/t01e6b37ebbb4e12cc2.png)](https://p0.ssl.qhimg.com/t01e6b37ebbb4e12cc2.png)

图7 加密的config.sys文件内容

GlobeImposter病毒会追加”..726“序号到每一个加密过的文件名来标识哪些文件进行过加密，下图8表明病毒将调用API MoveFileExW来重命名加密文件。

 [![](https://p2.ssl.qhimg.com/t0128e7537f92650b84.png)](https://p2.ssl.qhimg.com/t0128e7537f92650b84.png)

图8 重命名加密文件

图9展示了python安装目录文件夹下被加密的文件（包括可执行文件）：

 [![](https://p5.ssl.qhimg.com/t012b45c357528faeba.png)](https://p5.ssl.qhimg.com/t012b45c357528faeba.png)

图9 python文件夹下被加密的文件



**RECOVER-FILES-726.html分析**

****

图10是RECOVER-FILES-726.html文件展示了如何进入支付页面：

 [![](https://p3.ssl.qhimg.com/t01902068ffb80c9dd8.png)](https://p3.ssl.qhimg.com/t01902068ffb80c9dd8.png)

图10 打开RECOVER-FILES-726.html文件



**解决方法**

****

通过以上分析我们了解了GlobeImposter病毒在受害者主机上下载并加密文件的过程，我们也发现很多JS样本正在扩散该勒索病毒，由于该病毒使用了2048位的RSA算法来加密文件因此在没有解密密钥的情况下很难解密那些被加密的文件。

1）JS文件中用于下载GlobeImposter病毒的URL已经被FortiGuard的web拦截服务列为“恶意网站“

2）JS文件被FortiGuard的反病毒服务识别为**JS/GlobeImposter.A!tr**

3）下载的GlobeImposter病毒被FortiGuard的反病毒服务识别为**W32/GlobeImposter.A!tr**



**病毒样本**

****

URL：

hxxp://wendybull.com.au/87wefhi??JWbXSIl=JWbXSIl

样本SHA256：

IMG_8798.js

3328B73EF04DEA21145186F24C300B9D727C855B2A4B3FC3FBC2EDC793275EEA

87wefhi.txt.exe

10AA60F4757637B6B934C8A4DFF16C52A6D1D24297A5FFFDF846D32F55155BE0
