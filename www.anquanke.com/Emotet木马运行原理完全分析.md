> 原文链接: https://www.anquanke.com//post/id/87440 


# Emotet木马运行原理完全分析


                                阅读量   
                                **105935**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d3fd6aee2d052703.jpg)

作者：[浪子_三少](http://bobao.360.cn/member/contribute?uid=2671394893)

预估稿费：1000RMB

**（本篇文章享受双倍稿费 活动链接请**[**点击此处**](https://www.anquanke.com/post/id/87276)**）**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

## 

## 钓鱼邮件

最近公司收到一些钓鱼木马邮件，内容形式如下：

[![](https://p5.ssl.qhimg.com/t0197bf237f977008db.png)](https://p5.ssl.qhimg.com/t0197bf237f977008db.png)

## 感染Doc文档

邮件里有个链接，当点开链接后会下载一个doc文档，打开文档会发现有宏代码

[![](https://p0.ssl.qhimg.com/t01b06cd9638274ff46.png)](https://p0.ssl.qhimg.com/t01b06cd9638274ff46.png)

经过一些列解密后会执行shell执行宏命令，打印出这个信息出来后发现，原来执行了powershell命令

[![](https://p1.ssl.qhimg.com/t01d9bc38c7b05abde8.png)](https://p1.ssl.qhimg.com/t01d9bc38c7b05abde8.png)

是从网络url中下载一些文件并且 StartProcess，看来这才是真正的木马，下载的是一个exe，名字是随机的四个字符的exe名字。

[![](https://p2.ssl.qhimg.com/t010d1dfc267af4358e.png)](https://p2.ssl.qhimg.com/t010d1dfc267af4358e.png)

## 木马分析

下面就开始分析这个木马，用ollydbg加载木马，在Winmain函数入口点下断点：

[![](https://p4.ssl.qhimg.com/t013a81ec0a78756f3c.png)](https://p4.ssl.qhimg.com/t013a81ec0a78756f3c.png)

F9飞一次，停在了入口，慢慢 F8单步，木马直接到了0300149C的地址

[![](https://p5.ssl.qhimg.com/t01b1ed27190c007261.png)](https://p5.ssl.qhimg.com/t01b1ed27190c007261.png)

F7继续进入函数：

进入函数不久木马一直两个代码间循环，无法继续往下走，

（1）    循环起止1.

[![](https://p0.ssl.qhimg.com/t019b90d0189f113880.png)](https://p0.ssl.qhimg.com/t019b90d0189f113880.png)

（2）    循环往上跳

[![](https://p4.ssl.qhimg.com/t01874040aa04529fa8.png)](https://p4.ssl.qhimg.com/t01874040aa04529fa8.png)

当我们f9的时候一直不能跳出循环，我们通过IDA查看发现他做了一个时间判断故意为了防止被分析做了一个时间开关，这个时间有点太大了。

[![](https://p3.ssl.qhimg.com/t01f98377fc5d84c726.png)](https://p3.ssl.qhimg.com/t01f98377fc5d84c726.png)

我们直接修改EIP到循环外的地址，跳过这个循环。

[![](https://p0.ssl.qhimg.com/t01f18c6c24f61702da.png)](https://p0.ssl.qhimg.com/t01f18c6c24f61702da.png)

继续往下走。

[![](https://p5.ssl.qhimg.com/t01aae2e12ad97f5632.png)](https://p5.ssl.qhimg.com/t01aae2e12ad97f5632.png)

下面有Call VirtualProtect,而这个VirtualProtect把刚才分配的地址改写成PAGE_EXECUTE_READWRITE的属性，也就是变成一个可读写可执行的代码页。

[![](https://p4.ssl.qhimg.com/t015d96aea3b1242815.png)](https://p4.ssl.qhimg.com/t015d96aea3b1242815.png)

下面就到了木马对内置的加密代码的解密了，可以明显看到原始数据被加密了。

[![](https://p3.ssl.qhimg.com/t011bd63f5092cfc45f.png)](https://p3.ssl.qhimg.com/t011bd63f5092cfc45f.png)

解密完后我们可以看到内存地址内容了，

[![](https://p0.ssl.qhimg.com/t014c2638ee5db2f440.png)](https://p0.ssl.qhimg.com/t014c2638ee5db2f440.png)

到此这个函数就执行完毕，返回到入口函数位置后，下面有个cal [3011744] 实际上是前面函数内解密分配的shellcode函数 。

[![](https://p4.ssl.qhimg.com/t017653a061768f7cdc.png)](https://p4.ssl.qhimg.com/t017653a061768f7cdc.png)

实际上是call 001AA618,进入函数

[![](https://p5.ssl.qhimg.com/t013bd7785bcc25c957.png)](https://p5.ssl.qhimg.com/t013bd7785bcc25c957.png)

再次进入就进入真正的函数位置了

[![](https://p0.ssl.qhimg.com/t0100cda630d8dd708e.png)](https://p0.ssl.qhimg.com/t0100cda630d8dd708e.png)

## Shellcode

很明显字符串 75 73 65 72 33 32用字节码写出来，作者做了一些免杀处理。

在shellcode遇到第一个函数这个函数call 001AA008,函数的功能是查找木马的导入表找到LoadLibraryA函数和GetProcAddress这两个函数地址

[![](https://p0.ssl.qhimg.com/t017d981ecb42e6b78b.png)](https://p0.ssl.qhimg.com/t017d981ecb42e6b78b.png)

[![](https://p2.ssl.qhimg.com/t019ddd83c1649a2c83.png)](https://p2.ssl.qhimg.com/t019ddd83c1649a2c83.png)

接下来就是通过LoadLibrary 和GetProcAddress函数动态获取一些API的地址，

[![](https://p4.ssl.qhimg.com/t011c2c53c2e7674ba2.png)](https://p4.ssl.qhimg.com/t011c2c53c2e7674ba2.png)

[![](https://p5.ssl.qhimg.com/t01a2c71985831a1ae8.png)](https://p5.ssl.qhimg.com/t01a2c71985831a1ae8.png)

一共要获取几十个函数的地址，这块我们跳过去,F9一路飞到地址001AB4EF

[![](https://p3.ssl.qhimg.com/t01d6d53e9f9f8007f7.png)](https://p3.ssl.qhimg.com/t01d6d53e9f9f8007f7.png)

这个函数直接调用函数下面的地址，继续 F8单步到001AB50F

[![](https://p4.ssl.qhimg.com/t014f008e16de66d128.png)](https://p4.ssl.qhimg.com/t014f008e16de66d128.png)

继续F7进入001AB50F函数

[![](https://p0.ssl.qhimg.com/t018746f88cbe3535a2.png)](https://p0.ssl.qhimg.com/t018746f88cbe3535a2.png)

在这里他会判断木马目录下有没有apfHQ文件，所以我们事先需要生成一个apfHQ文件在目录下，空文件也行，这个过程完毕后就进入了01AA408函数。

[![](https://p5.ssl.qhimg.com/t017d0d6787a378f687.png)](https://p5.ssl.qhimg.com/t017d0d6787a378f687.png)

[![](https://p5.ssl.qhimg.com/t01b61e4890dd0b9d5b.png)](https://p5.ssl.qhimg.com/t01b61e4890dd0b9d5b.png)

继续往1AA408函数内部F7，会经过一些列的RegisterClassEx， CreateWinodws、GetMssage等窗口函数后就进入了1AA108函数

[![](https://p0.ssl.qhimg.com/t016b7da04f32a37407.png)](https://p0.ssl.qhimg.com/t016b7da04f32a37407.png)

继续F7进入1AA108函数，在进入函数不久，木马会去取一个内存数据，并且判断4550 “PE”这个标志位

[![](https://p2.ssl.qhimg.com/t0120e8339ccbacafd6.png)](https://p2.ssl.qhimg.com/t0120e8339ccbacafd6.png)

接下来调用 GetStartUpInfo，取得当前进程的启动信息

[![](https://p5.ssl.qhimg.com/t01d2665fae1e4696e9.png)](https://p5.ssl.qhimg.com/t01d2665fae1e4696e9.png)

然后接续获得当前进程的命令行参数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01123ba8a48eb4d7ae.png)

然后调用CreateProcess 来把自己作为子进程创建起来，而且创建标志位是CREATE_SUSPENDED

0x00000004

是以悬挂进程的方式创建子进程

[![](https://p1.ssl.qhimg.com/t01e8dd053343a5c0b1.png)](https://p1.ssl.qhimg.com/t01e8dd053343a5c0b1.png)

然后继续通过GetThreadContext函数获得子进程的线程上下文

[![](https://p5.ssl.qhimg.com/t01b7a141442a3d1a6c.png)](https://p5.ssl.qhimg.com/t01b7a141442a3d1a6c.png)

然后在子进程的0x400000的地址远程分配一个大小0xC00大小的内存，内存属性0x40,即读写可执行的属性内存PAGE_EXECUTE_READWRITE  0x40

[![](https://p4.ssl.qhimg.com/t0177444e2cee8ac18c.png)](https://p4.ssl.qhimg.com/t0177444e2cee8ac18c.png)

接下来木马就会使用ZwWriteVirtualMemory函数往子进程的0x400000地址写入大小0x400的数据，通过查看写入的数据发现是个pe头

[![](https://p3.ssl.qhimg.com/t01d7ea4bfbd228d961.png)](https://p3.ssl.qhimg.com/t01d7ea4bfbd228d961.png)

下面就是pe头数据

[![](https://p1.ssl.qhimg.com/t01312e9c4814c9310f.png)](https://p1.ssl.qhimg.com/t01312e9c4814c9310f.png)

## 提取PE文件

然后木马会解析这个内存里的pe文件的各个节.text .data .rdata 等等节段，通过ZwWriteVirtualMemory函数分别往子进程的相应内存里远程写入数据。

[![](https://p2.ssl.qhimg.com/t01f68994c79dd19c29.png)](https://p2.ssl.qhimg.com/t01f68994c79dd19c29.png)

分别写完数据后，然后改写子进程pe加载器的子进程的执行加载的首地址为0x400000

[![](https://p2.ssl.qhimg.com/t012bc90a856be596f1.png)](https://p2.ssl.qhimg.com/t012bc90a856be596f1.png)

然后使用SetThreadContext设置子进程的当前线程EIP 指向0x408FE5

[![](https://p1.ssl.qhimg.com/t01e761e2e3f92c058c.png)](https://p1.ssl.qhimg.com/t01e761e2e3f92c058c.png)

最后调用ResumeThread函数恢复子进程的线程继续执行

[![](https://p0.ssl.qhimg.com/t01d017bc8fa7fb5625.png)](https://p0.ssl.qhimg.com/t01d017bc8fa7fb5625.png)

最后父进程退出，子进程开始干一些真正的盗取行为，到此我们可以知道木马是通过创建子自身子进程通过GetThreadContext、ZwWriteVirtualMemory、SetThreadContext、ResumeThread,来实现hook方法达到隐藏真实pe的目的来增加分析人员的分析难度，他的真PE文件加密存贮在数据段中解密后如下：

[![](https://p0.ssl.qhimg.com/t015cc96719d715e73b.png)](https://p0.ssl.qhimg.com/t015cc96719d715e73b.png)

## PE文件分析

接下来我们就来讲解这个从内存里扣出来的pe文件到底怎么工作的。Emotet在入口点，通过hash对比去查找ntdll.dll,kernel32.dll的模块句柄，而不是通过我们常用的方法GetMoudleHanlde()的方法去获取句柄，

[![](https://p2.ssl.qhimg.com/t01f1b14f02dd7e240b.png)](https://p2.ssl.qhimg.com/t01f1b14f02dd7e240b.png)

看看serverlog_search_moudle这个函数的实现，在函数内部使用了[[[FS:[30]+0xc]+0xc]+0x30]的方法去获取模块的名字，在ring3层FS寄存器指向的是线程环境块，0x30的偏移即指向PEB(进程环境块)，PEB的0xc就是指向LDR表，后面的偏移就是从LDR表中获取模块的BaseName,计算相应的hash对比去从LDR表中获取模块的句柄。

[![](https://p0.ssl.qhimg.com/t013b1db67313ba1d50.png)](https://p0.ssl.qhimg.com/t013b1db67313ba1d50.png)

获取了模块首地址后，通过解密.data节段的加密导入表来获取相应的函数地址

[![](https://p4.ssl.qhimg.com/t0195352677aa1a5640.png)](https://p4.ssl.qhimg.com/t0195352677aa1a5640.png)

下面是获取到的ntdll的对应函数表

[![](https://p0.ssl.qhimg.com/t013d05fec755b24da4.png)](https://p0.ssl.qhimg.com/t013d05fec755b24da4.png)

下面是获取的kernel32的对应函数表

[![](https://p0.ssl.qhimg.com/t014f5813026be16c73.png)](https://p0.ssl.qhimg.com/t014f5813026be16c73.png)

接下来就进入了init初始化的工作

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010337b42e26408ae5.png)

首先会创建一个事件加一个互斥体

[![](https://p5.ssl.qhimg.com/t013f95e2ad63cff443.png)](https://p5.ssl.qhimg.com/t013f95e2ad63cff443.png)

当这个mutex互斥体之前不存在时会再次把自身进程启动一遍，如果互斥体存在就进入的工作的函数里，这样也是为了多进程的方式。

当进入工作函数server_get_info_and_timer时，就表示木马已经开始真正的工作了。

## PE文件工作分析

工作初期木马会再次获取他所需的函数表，方式类似之前不再赘诉，他要获取advapi32.dll、ole32.dll、shell32.dll、crypt32.dll、urlmon.dll、wininet.dll的所需函数，如下：

[![](https://p0.ssl.qhimg.com/t0135de27f5da510f37.png)](https://p0.ssl.qhimg.com/t0135de27f5da510f37.png)

[![](https://p3.ssl.qhimg.com/t01d98dd739b5fa57d4.png)](https://p3.ssl.qhimg.com/t01d98dd739b5fa57d4.png)

[![](https://p2.ssl.qhimg.com/t014c131181f303ae5d.png)](https://p2.ssl.qhimg.com/t014c131181f303ae5d.png)

[![](https://p5.ssl.qhimg.com/t015c6e41d857022348.png)](https://p5.ssl.qhimg.com/t015c6e41d857022348.png)

[![](https://p2.ssl.qhimg.com/t01f8677341ebf294fc.png)](https://p2.ssl.qhimg.com/t01f8677341ebf294fc.png)

然后木马会获取windows目录，然后计算系统目录所在的磁盘的磁盘id。

[![](https://p5.ssl.qhimg.com/t0167bddc9acc16ec5c.png)](https://p5.ssl.qhimg.com/t0167bddc9acc16ec5c.png)

接下来就是取当前电脑的电脑+磁盘id的组合，并且根据磁盘id来计算当前电脑所要生成的服务程序的名字。

[![](https://p4.ssl.qhimg.com/t01f00248126533cdf2.png)](https://p4.ssl.qhimg.com/t01f00248126533cdf2.png)

服务的名字是根据之前磁盘id， 在字符串”agent,app,audio,bio,bits,cache,card,cart,cert,com,

crypt,dcom,defrag,device,dhcp,dns,event,evt,flt,gdi,group,

help,home,host,info,iso,launch,log,logon,lookup,man,math,

mgmt,msi,ncb,net,nv,nvidia,proc,prop,prov,provider,reg,rpc,

screen,search”中计算出对应的字符来填充组合成所要生成的服务名和exe的名字。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01968bed627e904b13.png)

得到本木马服务的exe名字后就计算系统目录里的木马exe的crc的值

[![](https://p5.ssl.qhimg.com/t0143709d17762fd34e.png)](https://p5.ssl.qhimg.com/t0143709d17762fd34e.png)

[![](https://p3.ssl.qhimg.com/t01b282c965f249f5ec.png)](https://p3.ssl.qhimg.com/t01b282c965f249f5ec.png)

接下来就是获取电脑名，并且会将电脑中的非0-9、a-z、A-Z的字符替换成X,并且最多只获取16个字符的名字，然后和磁盘id组合起来

[![](https://p3.ssl.qhimg.com/t015ed16120e38f1f0f.png)](https://p3.ssl.qhimg.com/t015ed16120e38f1f0f.png)

接着木马就会使用CreateTimerQueueTimer函数创建一个Timer计时器，

[![](https://p1.ssl.qhimg.com/t01091d76ff53542fed.png)](https://p1.ssl.qhimg.com/t01091d76ff53542fed.png)

流程就进入了serverlog_posturl_timer函数空间

[![](https://p3.ssl.qhimg.com/t016f277c64a4efae96.png)](https://p3.ssl.qhimg.com/t016f277c64a4efae96.png)

根据当前的运行状态执行同的逻辑，case 1：时表示木马正准备初始化，然后设置状态为2，定时器执行到case 2：时就会将本木马exe创建成一个windows服务，服务名就是之前计算出来的service_name, 然后设置成状态3，进入case 3：会填充一些IP地址与端口

IP地址和端口直接写死在.data节，可以看到内存里内置了很多IP与端口，0x1BB即433端口，1F90即8080端口

[![](https://p1.ssl.qhimg.com/t01397e0c5c06fc38ed.png)](https://p1.ssl.qhimg.com/t01397e0c5c06fc38ed.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0152b98299dc6d06ee.png)

Case 3还会初始化加密上下文

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d6c010d8d292c123.png)

使用的rsa算法，导入了内存里的publickey，0x13即RSA_CSP_PUBLICKEYBLOB

[![](https://p5.ssl.qhimg.com/t0143e538827e06968d.png)](https://p5.ssl.qhimg.com/t0143e538827e06968d.png)

Case 3执行完毕会设置成状态4，下次定时器的时候就进入case 4，case 4会把枚举当前电脑的进程信息，木马的exe的crc，电脑名磁盘id填充到待加密的缓冲区

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01baf977d3c059f8e2.png)

然后对以上进行加密，再post到服务器的433端口

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b18227c5866d3f6e.png)

注意在发送到433之前，木马有进行了一次rsa加密

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0175a05c40428b7ae6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f72745efc255a413.png)

然后使用post的方式发送到服务器的433端口。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a37ca68ddfddc913.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0140fb18b7333910c1.png)

然后木马通过InternetReadFile

[![](https://p2.ssl.qhimg.com/t01a169f24643293c4b.png)](https://p2.ssl.qhimg.com/t01a169f24643293c4b.png)

函数获取服务器的返回结果，这个结果会执行各种流程，其中有一个流程是从远程服务器去下载exe，并且执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018ed42c088d800fde.png)

如果有更新的木马会调用start_download_exe函数去实现自我更新

[![](https://p2.ssl.qhimg.com/t017786b2945cadb33e.png)](https://p2.ssl.qhimg.com/t017786b2945cadb33e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0172e636e5a0dc813a.png)

到此基本上木马所有主要工作流程都已经分析完毕。
