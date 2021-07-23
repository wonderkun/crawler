> 原文链接: https://www.anquanke.com//post/id/238861 


# KimSuky样本分析思路分享


                                阅读量   
                                **425041**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01975e6d218a82acd1.jpg)](https://p2.ssl.qhimg.com/t01975e6d218a82acd1.jpg)



## 概述

KimSuky是总部位于朝鲜的APT组织，根据卡巴的情报来看，至少2013年就开始活跃至今。该组织专注于针对韩国智囊团以及朝鲜核相关的目标。KimSuky有不少别名，包括Velvet Chollima, Black Banshee, Thallium, Operation Stolen Pencil等。[malpedia](https://malpedia.caad.fkie.fraunhofer.de/actor/kimsuky)上有关于KimSuky的详细介绍。

关于KimSuky，笔者之前写过[一篇文章](https://www.anquanke.com/post/id/219593#h2-13)对该组织的常见攻击手法进行了浅析。近期在对该组织的样本收集分析时也发现了不少以前没见过的样本，在本文中，将对一例以新冠疫情为诱饵的恶意样本进行详细分析。



## 样本信息

样本最开始来源于[bazaar.abuse.ch](https://bazaar.abuse.ch/sample/70fa2300d7932ab901c19878bf109bdd9e078e96380879ca2ce2c3f9fc5c7665/)，在bazaar上该样本已经被打上了Amadey、APT、Thallium三个标签。上面已经说过，Thallium是KimSuky的别名，背后的运营人员疑似为KimSuky的成员，国内很少有厂商将Thallium单独拿出来分析，笔者为了命名统一，还是将该样本归类到了KimSuky。

[![](https://p5.ssl.qhimg.com/t0191050fe40c73c84e.png)](https://p5.ssl.qhimg.com/t0191050fe40c73c84e.png)

原始样本md5：90a59c16d670fd77d710516299533834<br>
样本类型：doc<br>
样本利用方式：宏代码利用<br>
样本文件名：Pyongyang stores low on foreign goods amid North Korean COVID-19 paranoia.doc

原始样本以朝鲜平壤地区的疫情为诱饵，向对此话题感兴趣的人士发起攻击，暂未定位到具体的受害目标，原始样本通过设置颜色在正文上面加上一层遮挡物以诱导用户启用宏：

[![](https://p4.ssl.qhimg.com/t01285a921e4765ad36.png)](https://p4.ssl.qhimg.com/t01285a921e4765ad36.png)

宏代码启用之后，遮挡物消失，文档正文正常显示以掩护恶意代码执行。

宏代码运行之后主要是执行两个功能
1. 去掉遮挡物让用户以为打开的是正常文档
<li>从C2：hxxps://www[.]rabadaun.com/wordpress/wp-content/themes/TEMP.so 下载TEMP.so到本地加载执行。<br>[![](https://p0.ssl.qhimg.com/t010ed2321fa513c44e.png)](https://p0.ssl.qhimg.com/t010ed2321fa513c44e.png)
</li>
下载的TEMP.so为exe文件，md5为：f160c057fded2c01bfdb65bb7aa9dfcc

加载的后续payload主要有两个可疑行为
<li>创建C:\ProgramData\a7963\目录并将自身拷贝过去<br>[![](https://p3.ssl.qhimg.com/t01ca98ad9b0054007a.png)](https://p3.ssl.qhimg.com/t01ca98ad9b0054007a.png)
</li>
<li>循环对C2服务器186[.]122.150.170:80 发起网络请求<br>[![](https://p5.ssl.qhimg.com/t0142d213b229940076.png)](https://p5.ssl.qhimg.com/t0142d213b229940076.png)
</li>
此样本由MFC编写，样本运行后会通过一个超大循环以延迟关键代码执行，起到一定的反检测作用，这里是个for循环，循环变量每次自增1，循环条件是变量小于0x0BAADBEEF，循环体是给ebp+var_18变量自增1。循环一共会执行3131948783次，所以程序加载后，在恶意代码执行起来之前会有一个明显的停顿。

[![](https://p5.ssl.qhimg.com/t01bfb486a8c46fb889.png)](https://p5.ssl.qhimg.com/t01bfb486a8c46fb889.png)

循环执行完毕，程序通过VirtualProtect更改0x422548到0x42A548的内存属性为0x40（可读可写可执行）

[![](https://p4.ssl.qhimg.com/t01564a95baa6dfa6ac.png)](https://p4.ssl.qhimg.com/t01564a95baa6dfa6ac.png)

更改完成之后，程序会在00401070函数中对这片内存进行解密。<br>
解密算法如下，程序首先将刚才更改了内存属性的数据的起始地址0x422548赋值给eax

[![](https://p4.ssl.qhimg.com/t01394203655f2e69c9.png)](https://p4.ssl.qhimg.com/t01394203655f2e69c9.png)

赋值给eax之后，程序首先会清空esi，然后通过自增esi和eax+esi的方式对这片内存中的每个字节进行操作，第一次执行时，程序会将eax+esi的值赋给bl并且将bl与4330c0处的值进行异或计算，计算的值存储到bl中。

[![](https://p5.ssl.qhimg.com/t010202a211c633e2f3.png)](https://p5.ssl.qhimg.com/t010202a211c633e2f3.png)

异或之后，程序会将bl的值进行not运算，运算之后的值依旧在bl寄存器中，此时，程序再将bl与4330c1的值进行异或，异或的值放入bl寄存器。

[![](https://p2.ssl.qhimg.com/t01e22b75371749c723.png)](https://p2.ssl.qhimg.com/t01e22b75371749c723.png)

第二次异或之后，程序会将bl的值放回原位以替代原数据，同时自增esi，计算下一个字节的值。这里程序一共会将0x77E6大小的值以同样的方法进行计算解密出后面的shellcode。

[![](https://p4.ssl.qhimg.com/t01307581d8f84182aa.png)](https://p4.ssl.qhimg.com/t01307581d8f84182aa.png)

解密完成之后，EnumChildWindows的回调函数EnumFunc已经被替换为了解密后的代码

[![](https://p4.ssl.qhimg.com/t01402b7a09c48decf5.png)](https://p4.ssl.qhimg.com/t01402b7a09c48decf5.png)

直接在00427068处设置断点过来

[![](https://p2.ssl.qhimg.com/t01529cf8bfe54b518b.png)](https://p2.ssl.qhimg.com/t01529cf8bfe54b518b.png)

解密出来的这段shellcode主要是一个loader，用于解密后续的payload继续执行，程序会用如下的字符串和程序的数据解密出一个PE

[![](https://p1.ssl.qhimg.com/t01bd46caa8f9a75a07.png)](https://p1.ssl.qhimg.com/t01bd46caa8f9a75a07.png)

动态解密API地址

[![](https://p4.ssl.qhimg.com/t015c0276dcf2f6aac4.png)](https://p4.ssl.qhimg.com/t015c0276dcf2f6aac4.png)

4255C8函数再次通过和之前一样的手法，执行一个大循环以延迟程序执行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a61f82833c7dff3f.png)

程序在00423827处重新创建自身进程

[![](https://p1.ssl.qhimg.com/t017ca97ce6509e5066.png)](https://p1.ssl.qhimg.com/t017ca97ce6509e5066.png)

接着程序通过ZwResumeThread、ZwSetContexThread这一套进行傀儡进程注入

[![](https://p1.ssl.qhimg.com/t0188e40df2d9604f48.png)](https://p1.ssl.qhimg.com/t0188e40df2d9604f48.png)

最后通过ZwResumeThread恢复目标进程执行

[![](https://p2.ssl.qhimg.com/t0118944927032f4ca3.png)](https://p2.ssl.qhimg.com/t0118944927032f4ca3.png)



## 傀儡进程注入

注入的进程为Amadey恶意软件，程序中的字符串均已加密，程序定义了一个字符串a7963b909152f8ebc3ec69b1dee2b255a9678a5用于动态解密其他字符串

[![](https://p0.ssl.qhimg.com/t0159c879a316092b83.png)](https://p0.ssl.qhimg.com/t0159c879a316092b83.png)

程序会调用这个解密函数解密出一系列杀软文件名并判断是否存在这些杀软文件名

[![](https://p0.ssl.qhimg.com/t01f08d09282d4e2e9c.png)](https://p0.ssl.qhimg.com/t01f08d09282d4e2e9c.png)

这里程序主要是检测是否存在0A和0B所对应的杀软，也就是Norton和Sophos，如果检测到这两款杀软程序就跳转到函数最后，不继续执行此函数功能。

[![](https://p4.ssl.qhimg.com/t012c1f3e6be43835ac.png)](https://p4.ssl.qhimg.com/t012c1f3e6be43835ac.png)

当前函数继续执行，则会解密拼接出C:\ProgramData\a7963\tlworker.exe路径并创建文件句柄

[![](https://p5.ssl.qhimg.com/t0176c4b60bb785a1c5.png)](https://p5.ssl.qhimg.com/t0176c4b60bb785a1c5.png)

创建目标文件夹

[![](https://p3.ssl.qhimg.com/t01f71f3f8f4ae2a371.png)](https://p3.ssl.qhimg.com/t01f71f3f8f4ae2a371.png)

创建文件，然后在004016f2函数将自身写入到C:\ProgramData\a7963\tlworker.exe文件中

[![](https://p0.ssl.qhimg.com/t011fc2aff3d6c37a83.png)](https://p0.ssl.qhimg.com/t011fc2aff3d6c37a83.png)

接下来，程序创建进程，通过cmd指令将上面的路径写入到启动项中以实现本地持久化

[![](https://p5.ssl.qhimg.com/t01f3b905056db096fa.png)](https://p5.ssl.qhimg.com/t01f3b905056db096fa.png)

### <a class="reference-link" name="%E7%BD%91%E7%BB%9C%E8%AF%B7%E6%B1%82%E6%A8%A1%E5%9D%97"></a>网络请求模块

程序解密出请求C2：196.122.150.107

[![](https://p1.ssl.qhimg.com/t01f2c5b3da792b8b25.png)](https://p1.ssl.qhimg.com/t01f2c5b3da792b8b25.png)

接着程序开始解密请求路径和参数，首先是解密出请求路径cc/index.php

[![](https://p1.ssl.qhimg.com/t01e8af53cca5cdd9b8.png)](https://p1.ssl.qhimg.com/t01e8af53cca5cdd9b8.png)

接着解密出id参数并且通过获取系统目录和磁盘信息以计算出id

[![](https://p1.ssl.qhimg.com/t01861bce80b36ec3f5.png)](https://p1.ssl.qhimg.com/t01861bce80b36ec3f5.png)

同样的，指定当前的样本版本

[![](https://p3.ssl.qhimg.com/t0139791eb70ae4e64e.png)](https://p3.ssl.qhimg.com/t0139791eb70ae4e64e.png)

程序会通过类似的方法拼接一系列参数，包括是否为管理员权限、操作系统版本信息、计算机名和杀软信息等，最后拼接出的请求信息如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018d25fce34beb23e8.png)

一切准备就绪之后，获取目标主机地址准备请求：

[![](https://p5.ssl.qhimg.com/t01cf05b32ecc572e3b.png)](https://p5.ssl.qhimg.com/t01cf05b32ecc572e3b.png)

通过post的方式将数据send到C2

[![](https://p4.ssl.qhimg.com/t012aadc9f32eb93954.png)](https://p4.ssl.qhimg.com/t012aadc9f32eb93954.png)

数据发送之后，程序会根据服务器返回执行对应的操作，并且休眠1分钟重复进行请求，也就是最开始在行为分析中看到的循环请求。由于末尾的跳转是jmp，并且中间并没有跳转可以跳出循环，说明这里是永真循环，程序执行到这里，功能已经执行完毕，后续则需要服务器返回执行。

[![](https://p0.ssl.qhimg.com/t0160506a7851262f7f.png)](https://p0.ssl.qhimg.com/t0160506a7851262f7f.png)

由于目前服务器已经没有返回，无法对后续操作进行深入分析。但是根据攻击者所使用的Amadey恶意软件和钓鱼的内容，基本可以确定这是东亚APT组织KimSuky针对韩国用户的攻击活动。
