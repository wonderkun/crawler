> 原文链接: https://www.anquanke.com//post/id/207065 


# PLC互联的安全分析


                                阅读量   
                                **94393**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t017ed1666f9b58028e.png)](https://p1.ssl.qhimg.com/t017ed1666f9b58028e.png)



## 01.前言

当前大多数PLC具有通信联网的功能，它使PLC与PLC 之间、PLC与上位计算机以及其他智能设备之间能够交换信息，形成一个统一的整体，实现分散集中控制。组网带来高效的工业生产控制及管理的同时也引入了一定的网络风险。以TCP连接为例，通过一个普通PLC的TCP连接指令（例如PLC内部的一个功能块实现）可以与另一个目标PLC建立连接，再通过数据发送指令可以发送特定的数据包给目标PLC，如果发的是一组恶意的指令可以造成对工艺破坏，而这样的破坏根本不依赖PC机，在PLC之间就可以进行。甚者可借助PLC的网络扫描程序及程序下载代码可以实现在一组PLC中传播恶意指令。下文以S7-1200为例进行实验。



## 02.实验环境

实验是在一组S7-1200 PLC上进行的，该款PLC集成PN口，具备TCP通信能力，S7-1200 PLC支持FBD/LAD/STL/SCL编程语言，可任选一种语言，使用下位机编程软件TIA（v13）进行逻辑编程，编程完毕执行下载，TIA将自动对代码进行编译、最终下载到PLC存储器中，PLC将加载代码进行执行。PLC中以“块”的概念对各类数据进行存储，使用到的块包括：OB 组织块，功能程序入口；FB 功能块，各种带有方法的类的集合；SFB/SFC 系统功能块，库函数与系统调用； FC 功能块，自定义功能； DB数据库，各类数据存放。

[![](https://p1.ssl.qhimg.com/t01ab3b3ba97474318a.png)](https://p1.ssl.qhimg.com/t01ab3b3ba97474318a.png)



## 03.建立IP扫描和TCP连接

在源PLC中的正常逻辑程序中加了一段IP扫描和建立TCP连接的代码，通过IP地址和端口号寻找目标PLC。这段代码中调用了西门子的两个系统函数TCON和TDISCON。TCON用来设置并建立TCP通信连接，参数CONNECT在这段程序中起很重要的作用，它是TCOM_PARAM数据类型的变量，我们主要需要配置ID（ID号可任意，但与其相关通信的都必须采用此ID号），CONNECT_TYPE：17，ACTIVE_EST：1（表示主动建立连接），LOCAL_TASP_ID，REM_TASP_ID：102（必须为102，表示为被连接的PLC的端口地址），REM_STADDR（IP扫描的起始地址）。我们为”data”.con_state设定初值为10，当PLC启动便会执行TCON去建立连接，当TCON函数的参数done为1表示已发现目标PLC并建立了TCP连接，然后进入到下一个过程状态（下一个状态我们定义为”data”.con_state=20，用于建立S7+通信连接）。否则执行TDISCON删除所设置的相应连接，同时IP地址加一，继续扫描直至找到目标。关于CONNECT参数，我们专门把它定义在一个data数据块中，以便于参数赋初值，如图所示：

[![](https://p0.ssl.qhimg.com/t0197db45c458b1b9ab.png)](https://p0.ssl.qhimg.com/t0197db45c458b1b9ab.png)

IP扫描及建立TCP连接的程序，采用PLC自带的SCL语言：

[![](https://p5.ssl.qhimg.com/t0142360f0acb477041.png)](https://p5.ssl.qhimg.com/t0142360f0acb477041.png)



## 04.数据传输

上一节提到的方法是搜索目标PLC，搜索到目标PLC后又如何将恶意代码传输给目标PLC，在s7-1200的编程软件中采用系统函数TSEND/TRCV实现PLC之间的数据传输，如建立S7连接、启/停PLC、数据块下载等，当然S7-1200是基于S7+协议，即将S7+的数据字段通过在s7-1200的编程软件用数组的方式组织起来，例如在源plc用一个DB数据块建立一个特定长度的message，用于存储特定功能的S7+数据字段，再通过TSEND函数发送给目标PLC。但我们需要事先定义好状态机，到某一个状态时TSEND函数的DATA参数指向特定的message，也就是说到不同的状态发送不同message。特定的message我们可以通过wireshark抓包分析得到，然后把它定义在指定的DB块中（创建一个数据类型为BYTE的数组，在启动值处输入必要的16进制码）。如下图：

[![](https://p4.ssl.qhimg.com/t01aa4267d3b7c77de4.png)](https://p4.ssl.qhimg.com/t01aa4267d3b7c77de4.png)

在我们的SCL程序反复多次调用了TSEND函数以及两次调用TRCV函数，因为会进行建立S7+连接、停止PLC、下载功能块、启动PLC等多个状态的转换，而每个状态过程实现需发送相对应的message。TSEND函数的作用是通过现有通信连接发送数据，发送数据需要在参数DATA指定发送区。也就是说引用指向发送区的指针，该发送区包含要发送数据的地址和长度，在该程序中我们的地址引用为数据块。TRCV函数的作用是通过现有通信连接接收数据，函数中参数EN_R 设置为值“1”时，才会启用数据接收。发送及接收协议message的程序如下图：

[![](https://p1.ssl.qhimg.com/t010e27e7d2175e0939.png)](https://p1.ssl.qhimg.com/t010e27e7d2175e0939.png)

[![](https://p3.ssl.qhimg.com/t01a191834fce3a489f.png)](https://p3.ssl.qhimg.com/t01a191834fce3a489f.png)

当把一个PLC感染过程的状态过程全部走完后，程序又跳回到状态”data”.con_state=0，执行TDISCON函数，终止此次TCP连接，进行IP扫描，地址自动加一，为下一个PLC感染目标做准备，当寻找到另外的一个目标后，又会循环执行感染程序。如下图：

[![](https://p4.ssl.qhimg.com/t01853d2625619412a9.png)](https://p4.ssl.qhimg.com/t01853d2625619412a9.png)

[![](https://p2.ssl.qhimg.com/t01639e50d54a8b4fe1.png)](https://p2.ssl.qhimg.com/t01639e50d54a8b4fe1.png)



## 05.实验结果

目标PLC被锁定之后，被注入恶意代码，实验中注入一个OB组织块，这个块采用梯形图编程，实现特定的功能，操纵寄存器地址Q0.0的输出值。和停止PLC功能操作一样，在源plc用一个DB数据块建立一个特定长度的message，用于存储OB组织块特定功能的S7+数据字段，再通过TSEND函数将数据发送目标PLC。

这样OB块和运行所需的DB块被注入，PLC将自动检测到新增的OB块并按照程序的逻辑进行运行，原有的逻辑功能不会受到影响，只是额外执行了某种任务而已。以下图片展示了PLC被感染蠕虫前后的项目树对比情况：

[![](https://p5.ssl.qhimg.com/t01f63fecd499c2f68a.png)](https://p5.ssl.qhimg.com/t01f63fecd499c2f68a.png)

[![](https://p5.ssl.qhimg.com/t01b47f61a4a73989b7.png)](https://p5.ssl.qhimg.com/t01b47f61a4a73989b7.png)

感染前后

使用TIA连接PLC可以很明显可以看出PLC中程序发生了变化，被注入了一个组织块OB6666（OB6666中的内容为我们编写的恶意程序）以及两个DB数据块。恶意程序可以操纵PLC的输出，我们实现的是让某个DO输出循环地开启2S后关闭2S。下图为我们操纵PLC输出的程序，展示的被操纵的数字量输出Q0.0：

[![](https://p5.ssl.qhimg.com/t012fbf4cea8d8c3ccd.png)](https://p5.ssl.qhimg.com/t012fbf4cea8d8c3ccd.png)



## 05.总结

针对PLC新型威胁研究，这种方法在国外早已发布，本文进行了复现测试。当然该攻击方式无需借助上位机，因此可以绕开杀毒软件的检测及工业防火墙的拦截，有一定的隐蔽性。但是这种攻击手段的也有一定局限性，例如支持完整tcp通讯功能块的PLC较少，在施耐德PLC中由TCP_OPEN库完成的，TCP OPEN的库是需要额外订购的，一般用户都不会采购，其他厂商提供这种需求的更加少。
