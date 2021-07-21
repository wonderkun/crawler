> 原文链接: https://www.anquanke.com//post/id/161272 


# Flare-On 2018 writeup（下）


                                阅读量   
                                **129635**
                            
                        |
                        
                                                                                    



## malware skillz

全能型后门，从LaunchAccelerator.exe开始分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015a2a96a7d15e170c.png)

程序先修改注册表，复制自身自运行

[![](https://p2.ssl.qhimg.com/t01e1679bb7b7b813ea.jpg)](https://p2.ssl.qhimg.com/t01e1679bb7b7b813ea.jpg)

然后释放下载后门的代码，载入内存运行

[![](https://p5.ssl.qhimg.com/t01eac458b0b30c8890.png)](https://p5.ssl.qhimg.com/t01eac458b0b30c8890.png)

后门下载器加载库函数从ldr链表中遍历模块和模块函数，使用Hash来获取API定位，此后的API都用这种方法遍历，由于是病毒经典使用方法，可以搜到hash表，没有搜索到的可以动态修改hash参数来取结果

[https://www.scriptjunkie.us/files/kernel32.dll.txt](https://www.scriptjunkie.us/files/kernel32.dll.txt)

[![](https://p4.ssl.qhimg.com/t017659fefc4e8847bd.png)](https://p4.ssl.qhimg.com/t017659fefc4e8847bd.png)

后门下载器搜索了必要的库函数，通过DNSQuery_A中查询到的DNS附加数据，夹带了加密的PE文件

然后解密，并运行到指定的函数

直接运行起来，可以发现通过DNS查询到的数据解密后会有弹窗[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01155ba65efe86c64f.png)

并在桌面上放了一个crackme.exe

[![](https://p3.ssl.qhimg.com/t0136edcece1a14d755.png)](https://p3.ssl.qhimg.com/t0136edcece1a14d755.png)

从pcap.pcap中dump出网包中的DNS数据，将DNS查询数据用网包数据覆盖得到真正的后门文件，后门下载器会运行到他的导出函数Shiny

[![](https://p0.ssl.qhimg.com/t0115976a35753778df.png)](https://p0.ssl.qhimg.com/t0115976a35753778df.png)

[![](https://p4.ssl.qhimg.com/t015166da98a7c9925f.jpg)](https://p4.ssl.qhimg.com/t015166da98a7c9925f.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01716f074894bced8f.png)

该函数查询当前eip的位置，搜索到自身的PE头，获取所有Sector相关的信息，重新加载到申请的内存页中，并从Dll入口点开始运行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016a627403653641b2.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e16198c801f8566f.png)

[![](https://p5.ssl.qhimg.com/dm/1024_305_/t0140fb4edc84a62b92.png)](https://p5.ssl.qhimg.com/dm/1024_305_/t0140fb4edc84a62b92.png)

对必要资源初始化和库函数定位后，后门开始连接主控机，并等待交互[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0177383901320658b8.png)

后门主要的流程从ShakeAndInitAes开始，连接主控机后，主控机和肉鸡各生成一个随机数以商定之后的AES通讯密码

此后由主控机发出请求，肉鸡执行对应命令，如果检测到数据异常则断开socket重新握手商定

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0168da68b274017b4d.png)

所有收发包都由统一规则进行封装，封装大致格式

[![](https://p1.ssl.qhimg.com/t019ac382af0d1bbb2f.png)](https://p1.ssl.qhimg.com/t019ac382af0d1bbb2f.png)

对原始数据进行了AES加密和Zlib压缩操作，并加入一些信息以及校验头，标明了长度、包类型、当前包AES_IV、hash等其他校验冗余信息

[![](https://p4.ssl.qhimg.com/t01909cfed18b7f6419.png)](https://p4.ssl.qhimg.com/t01909cfed18b7f6419.png)

通过对网包的复原和回放、解码可以发现，肉鸡A被感染后通过TCP 9443与主控机通信，主要经历了握手、上报了Malware各类版本、获取计算机名、磁盘、列目录、文件信息、ping主机、http请求、SMB广播控制

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0132ff305a2b42e3a3.png)

肉鸡A在感染受控过程中通过SMB2协议对病毒文件进行广播，感染肉鸡B，并通过肉鸡A接管肉鸡B，通过SMB2协议建立命名管道进行交互，交互数据的打包解包方式和TCP方式一致

[![](https://p4.ssl.qhimg.com/t019229c4df72bdeb9d.jpg)](https://p4.ssl.qhimg.com/t019229c4df72bdeb9d.jpg)

肉鸡B受控经历了一些磁盘、文件信息上报，并通过肉鸡A写入了Cryptor.exe，并执行Cryptor.exe level9.crypt level9.zip，然后执行删除相关文件，最后通过FTP上传level9.crypt

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c070b5c690dbd6c3.png)

将level9.crypt从网包中dump，可以看出已经被Cryptor.exe加密了，取得Cryptor.exe，为.Net编写的文件加密程序，de4dot反混淆后整理

[![](https://p5.ssl.qhimg.com/t0117679042c02a11b8.png)](https://p5.ssl.qhimg.com/t0117679042c02a11b8.png)

程序对原始文件进行Hash计算、将文件名长度、文件名、文件Hash作为文件头进行AES加密，最后在加密数据头部加上cryptar及github版本

AES加密会从github一项目获取信息作为文件加密AES的Key和IV，可以发现github项目最新版本已经不是level9.crypt的版本从网吧或者git中拿当时版本的信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0141b082df1d4bdf79.png)

[![](https://p4.ssl.qhimg.com/t01e89c88b627bd431c.png)](https://p4.ssl.qhimg.com/t01e89c88b627bd431c.png)

获取20180810的信息对level9.crypt进行AES解密，得到level9.zip文件

该zip包被加密了，密码需要在肉鸡A和主控机的通信中寻找

[![](https://p5.ssl.qhimg.com/t01252a2bce3c4425e2.png)](https://p5.ssl.qhimg.com/t01252a2bce3c4425e2.png)

搜索zip敏感字，找到密码really_long_password_to_prevent_cracking

解压zip包，取得一张空白图片和一个并没有任何作用的exe

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0196494bdefd02ffc7.png)

上色，取得flag

recover_these_messages_lost_in_the_colorful_bits@flare-on.com



## Suspicious Floppy Disk

拿到floppy.img，得到一系列文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017d1f94c04efab624.png)

可以发现大概为dos系统盘，和原版img进行比较，多了infohelp.exe、key.dat等文件

使用dosbox+ida5.5对infohelp.exe进行调试，由于是16位程序，无法使用F5插件，掏出王爽老师的汇编书籍温习一下16位x86汇编，然后在调试时，地址前加上对应的段名。

可以发现大致行为是输入password，将输入的password写入password.dat然后打开message.dat显示失败信息

[![](https://p2.ssl.qhimg.com/t01e6d2b643871f965d.png)](https://p2.ssl.qhimg.com/t01e6d2b643871f965d.png)

ida对该文件进行逆向，可以发现[![](https://p3.ssl.qhimg.com/t01d59120dd40df5dd9.png)](https://p3.ssl.qhimg.com/t01d59120dd40df5dd9.png)

程序由16位Watcoom编译，使用对应的watcom编译带调试符号的库，并制作FLIRT signature的签名文件，ida识别出大部分函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01dc599d7e4f5a22f9.png)

程序由sub_10000作为入口主要流程如下

```
printf("input pw")
scanf("%s", &amp;pw)
fopen("key.dat")
fwrite(pw)
fclose()
fopen("message.dat")
fread()
fclose()
printf(msg)
```

所以这个程序并没有直接藏有密码信息

使用WinHex发现了镜像中还有一些碎片文件可以通过特征恢复，但并没有什么发现，进一步观察发现镜像的mbr和原版dos相比被篡改了其中一段

[![](https://p1.ssl.qhimg.com/dm/1024_293_/t012f5a07cfe6b18b87.jpg)](https://p1.ssl.qhimg.com/dm/1024_293_/t012f5a07cfe6b18b87.jpg)

使用vm+ida对更改的mbr进行调试，起始流程如下

```
0:0x7c00:

memcpy &amp;mbr_cpy_600h, &amp;mbr_7c00h, 0x200

-&gt; 0x662

 

0:0x662h

memcpy 0:0x800, &amp;tmp.dat, 0x6000

call tmp.dat sub_0

-&gt; 0:0x800

 

0:0x800 (tmp.dat sub_0:)

0:0x413 -= 0x0020 (0:0x413 = 0x025d)

0:0x6ff3 = 0x9740

memcpy 9740:0, 0:0x843(&amp;tmp.dat+0x43, NICK RULES ~ NICK RULES), 0x5eb0

0x9740:0x5e5a = dw 0xca000117 (real int 13h)

0x9740:0x5e6f = db 0

0:0x200 = dw 0xca000117 (real int 13h)

0:0x4c = dw 0x97400012 (int 13h hook to 0x9740: 0x12)

-&gt; ret 0:0x671
```

篡改的mbr加载了tmp.dat中的函数，对0:0x4c地址的数据进行改写了，然后解码恢复原版mbr继续运行

0:0x4c这个地址正是int 13h中断服务函数地址，篡改后的地址为0x97400012[![](https://mmbiz.qpic.cn/mmbiz_png/PUubqXlrzBRibLqeYTYcu8v428n5FwQQdpU3zbiaMSF4O3uS41u9ec5lic3HABtxicWq4LkStOFbJuv4dot0RKP4HA/640?wx_fmt=png)](https://p5.ssl.qhimg.com/t01ed5372f0c99902ee.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01111dfbda6b26757a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b83ca59a5866aa79.jpg)

查阅资料，这种在mbr将系统服务进行hook的技术在bootkit很常用，由于预先于操作系统、应用程序加载所以很难被查杀

[![](https://p4.ssl.qhimg.com/t017c5ca56f23a650be.png)](https://p4.ssl.qhimg.com/t017c5ca56f23a650be.png)

继续跟进，可以发现进入伪造的int 13h函数会先记录int 13h所有的参数并执行真正的系统服务，然后对参数进行比对进入相应的handler，主要是读扇区时，hook解码原版mbr以及在打开message.dat文件时会call tmp.dat中的函数，写扇区时也会有对应的handler

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0142a3572879a9d817.png)

由img中的参数得知LBA=0x200 *  【柱面 * 36    +   磁头*18   +   扇区  –  1 】，经过计算可以发现cx = 0x2111, dh = 1, al = 1时正好对应message.dat，读取该文件时执行事先加载tmp.dat中的函数

界面如下[![](https://mmbiz.qpic.cn/mmbiz_png/PUubqXlrzBRibLqeYTYcu8v428n5FwQQdqJ2LljbKL1EjHg19mgLtT61bpQGkWhRJBcxUwBe3Df9QQqDOR9clTQ/640?wx_fmt=png)](https://p4.ssl.qhimg.com/t01dbdefda7ffe3e4fd.png)[![](https://p1.ssl.qhimg.com/t01966add706c7ddacb.png)](https://p1.ssl.qhimg.com/t01966add706c7ddacb.png)

也就是通过Infohelp.exe作为触发器，当输入密码打开message.dat显示不正确的信息时，实际被hook到另一个解密程序，通过跟踪恢复出这个handler[![](https://mmbiz.qpic.cn/mmbiz_png/PUubqXlrzBRibLqeYTYcu8v428n5FwQQd1VqrW9iaELOU6EzdEec0icn7C8KddjwO7ibzTxDjb7ibxGoT5DoibIZCb2w/640?wx_fmt=png)](https://p3.ssl.qhimg.com/t01ed5372f0c99902ee.png)[![](https://p5.ssl.qhimg.com/t01c890ee7b068b7fda.png)](https://p5.ssl.qhimg.com/t01c890ee7b068b7fda.png)

通过infohelp输入完密码后对key.dat写扇区的hook handler，先取得密码，然后在读取message.dat时执行真正的密码检查函数，并返回结果

由于这个bootkit对vm的bios兼容性不好，并不能进入dos系统执行infohelp（bochs据说可以正常运行和调试），我在int 13h进行其他服务时，修改了参数以触发解密程序

解密程序如下 [![](https://p3.ssl.qhimg.com/t013b685ce5ec2b2013.png)](https://p3.ssl.qhimg.com/t013b685ce5ec2b2013.png)

[![](https://p1.ssl.qhimg.com/t0144bc9de7aa60b1b8.png)](https://p1.ssl.qhimg.com/t0144bc9de7aa60b1b8.png)

查阅wiki资料，这是one-instruction set computer (oisc)，subleq的软件仿真，本来旨在于只支持一种指令的低成本芯片，也同时给逆向带来麻烦

在python中重构subleq的仿真环境

[![](https://p3.ssl.qhimg.com/t01c7da449839c7fda3.jpg)](https://p3.ssl.qhimg.com/t01c7da449839c7fda3.jpg)

参考网上关于Flare-on 2017，11题类似的subleq题解，进行侧信道攻击，通过不同密码输入的cpu titk、pc graph等手段，除了发现密码中输入了@会大大增加计算量以外并没有明显发现

然后进行数据流分析，追踪密码的流向，对读写密码的敏感位置进行标记，得到巨量的操作一时没有总结出规律

[![](https://p2.ssl.qhimg.com/t015a73ea2b4ff9204a.png)](https://p2.ssl.qhimg.com/t015a73ea2b4ff9204a.png)

最后这段程序也是由出题者编写的编译器编译的，本着编译本身有一些规律，参考去年11题官解，对subleq进行命令组合

[![](https://p4.ssl.qhimg.com/t01b7dba0be18fcf892.png)](https://p4.ssl.qhimg.com/t01b7dba0be18fcf892.png)

去年官解并没有把所有的指令定义列出，不断尝试和摸索中定义了以下指令

[![](https://p0.ssl.qhimg.com/t01d64e3853d508b059.png)](https://p0.ssl.qhimg.com/t01d64e3853d508b059.png)

其中最难的是subleq通过指令修改了自身指令，这种情况通过指令操作的target address写入了已经识别为指令的地址区域列出，进一步可以发现这些自身修改的指令主要用于指针操作*(%a) = %b, %b = *(%a), jmp *(%a)等操作，可以理解通过修改自身指令替换简单mov中的操作地址，来实现指针访问

[![](https://p2.ssl.qhimg.com/t0161f213f8aaf471a8.png)](https://p2.ssl.qhimg.com/t0161f213f8aaf471a8.png)

反编译器的设计思路是先区分指令区、数据区（通过运行的实际情况可以覆盖大多数），标记subleq基础指令（如 subleq s,d,t / subleq z,d / subleq z,z等），基础指令由3个操作数构成，通过区分源、目标、跳转地址是否为零是否相等区分出不同的基础指令，包括数据也认为是一种特殊指令，保存

[![](https://p2.ssl.qhimg.com/t01292408972c29efd3.png)](https://p2.ssl.qhimg.com/t01292408972c29efd3.png)

然后将简单指令组合成复合指令，复合指令一般会以基础指令的固定组合重复多次，并且意义明显，如mov或者跳转操作

[![](https://p1.ssl.qhimg.com/t015b811afbb3c900c1.png)](https://p1.ssl.qhimg.com/t015b811afbb3c900c1.png)

然后将指令解析成对应的LikeC，并分别生成具有完全标签和自动简化标签的两个文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f8a2dbc2fa595ce8.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011a9b160831929923.png)



防止因为一些指针跳转，无法找到对应指令位置的情况，然后对LikeC进行静态分析

这段subleq程序大致如下[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cb4e4bf7ce7ed865.png)

查阅资料，这又是一个vm，oisc的另一种rssb[![](https://p2.ssl.qhimg.com/t01acee4d75bc889455.png)](https://p2.ssl.qhimg.com/t01acee4d75bc889455.png)

同样的进行侧信道和数据流分析，一时没有掌握到规律，在编写一个反汇编器

rssb比subleq还要抽象，基础指令只有一条rssb x，但是x有几个特殊值[![](https://mmbiz.qpic.cn/mmbiz_png/PUubqXlrzBRibLqeYTYcu8v428n5FwQQd0sTWwhj9qSPz6B7Zsy96C8cJZ6UCxVDsVdTvSdAmB5PficZNzyU57lg/640?wx_fmt=png)](https://p4.ssl.qhimg.com/t01ed5372f0c99902ee.png)[![](https://p2.ssl.qhimg.com/t01358986c0c24210a6.png)](https://p2.ssl.qhimg.com/t01358986c0c24210a6.png)

x为-2时代表返回，-1只填补位置，0为当前程序指针，1为rssb累加器，2为常0寄存器，6为输出寄存器

当然这个是由本题的编译器定义的，并不一定通用，类似subleq反汇编器一样，合并基础指令为复合指令如下

[![](https://p1.ssl.qhimg.com/t01d64e3853d508b059.png)](https://p1.ssl.qhimg.com/t01d64e3853d508b059.png)

生成对应的rssb解析文件和LikeC（带完整标签/自动简化标签）

[![](https://p3.ssl.qhimg.com/t016a39f950caa54542.png)](https://p3.ssl.qhimg.com/t016a39f950caa54542.png)[![](https://p2.ssl.qhimg.com/t0116ebfd080a6c2b9f.png)](https://p2.ssl.qhimg.com/t0116ebfd080a6c2b9f.png)

进行静态分析，还原，关键函数如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e973b9f1937a7ac0.png)[![](https://p0.ssl.qhimg.com/t01e309d3ee2bffb8d2.png)](https://p0.ssl.qhimg.com/t01e309d3ee2bffb8d2.png)[![](https://p4.ssl.qhimg.com/t01409d4afd4b44ad70.png)](https://p4.ssl.qhimg.com/t01409d4afd4b44ad70.png)

可以发现@作为检查密码的结尾字符，而最后的密码校验方式是自定义hash算法与预定的hash表比对

hash计算公式如下

```
for i in range(15):
    hash[i] = (((key[i+1]-32) &lt;&lt; 7 + (k[i]-32)) ^ (i * 33) + magicsum) &amp; 0xffff
```

其中magicsum是所有密码的ascii和加3072乘密码长度

```
magicsum = 3072 * len(key) + sum(key)
```

由于magicsum不得知，key也不知到，只有期望的hash表，magicsum只能为0~0xffff

进行枚举倒推key[]，然后检查magicsum是否符合约定并打印

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d875342ce9cc1f8e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011bb78a3dc9a349cc.png)

[![](https://p2.ssl.qhimg.com/t01a5d03f193f37d2b4.png)](https://p2.ssl.qhimg.com/t01a5d03f193f37d2b4.png)

找到明文数据Av0cad0_Love_2018@flare-on.com，至此Flare-on5完成



### Easter Egg

彩蛋关，malware skillz关卡中通过DNS协议下载的crackme

[![](https://p0.ssl.qhimg.com/t01e52a07f7e885a5c5.png)](https://p0.ssl.qhimg.com/t01e52a07f7e885a5c5.png)

程序带壳，上来pushad，esp定律，下esp写入断点F9

停在OEP 0x401000，dump源程序

[![](https://p5.ssl.qhimg.com/t019adbb8cb23e8f82a.png)](https://p5.ssl.qhimg.com/t019adbb8cb23e8f82a.png)

拖入IDA

[![](https://p2.ssl.qhimg.com/t01f9b5aa597b714849.png)](https://p2.ssl.qhimg.com/t01f9b5aa597b714849.png)

程序混淆了字符串和控制流结构

大致流程是分别putc：Password:

然后getc，一位一位校验

然后输出校验结果，一般password一位字符的校验程序如下，由于所有的字符处理都是线性处理，先设置输入password为’\x00’ * 40然后在关键的比较位置下bp取出jz的比较值

如比较值为0xc8，正确输入时应为0x00，则意味着该位password实际应该为(char) (0x00-0xc8)，即’8’

[![](https://p0.ssl.qhimg.com/t01ba3279295395c4ba.png)](https://p0.ssl.qhimg.com/t01ba3279295395c4ba.png)

解出所有的password位：83cbeb65375d4a1263c2e28bc9cf4f8a8c8f834e

[![](https://p3.ssl.qhimg.com/t01a5a57aeaf8fe0919.png)](https://p3.ssl.qhimg.com/t01a5a57aeaf8fe0919.png)
