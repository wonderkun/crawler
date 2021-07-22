> 原文链接: https://www.anquanke.com//post/id/151203 


# 在Redis中构建Lua虚拟机的稳定攻击路径


                                阅读量   
                                **158406**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t019df4428febd5802e.png)](https://p0.ssl.qhimg.com/t019df4428febd5802e.png)

本文描述了如何在Redis中构建Lua虚拟机的稳定攻击路径。文中用到的具体利用代码已上传至A-Team的github。全文都是干货，推荐收藏慢慢阅读哦~

声明：本文由Dengxun[@360](https://github.com/360) A-Team原创，仅用于研究交流，不恰当使用会造成危害，否则后果自负。



## 前言

Exploit编写的原因，是工作中遇到了多个运行低版本的未认证redis，且均跑在root权限下。因为目标端口系内网映射的关系，覆写ssh key的攻击没有成功。而原本没有使用计划任务服务（计划任务需要任务文件为600的权限）也未能成功。经过评估后认为高权限的低版本的redis的lua虚拟机有已知漏洞，值得投入较大的精力编写攻击代码。

鉴于目标保密因素，大部分环节使用与目标相近的vps环境进行说明。



## 目标

围绕实战目标，编写高可用性，高稳定性，能反复利用的Exploit。



## 准备工作

### <a class="reference-link" name="%E5%89%8D%E7%BD%AE%E7%9F%A5%E8%AF%86"></a>前置知识
1. Elf64文件结构基础知识
1. gdb, debuginfo,redis,lua基础知识
1. C语言基础知识
### <a class="reference-link" name="%E4%BF%A1%E6%81%AF%E6%94%B6%E9%9B%86"></a>信息收集

通过redis的info和eval两个命令查询版本和编译信息，为本地实验环境的搭建做准备工作。

[![](https://p5.ssl.qhimg.com/t017075b18d57f94613.jpg)](https://p5.ssl.qhimg.com/t017075b18d57f94613.jpg)

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83%E6%9E%84%E5%BB%BA"></a>环境构建
1. 根据目标内核版本信息，创建centos6的虚拟机或vps
1. 安装与目标接近的gcc版本
<li>安装和编译与目标相同的redis版本，附下载地址[http://download.redis.io/releases/redis-2.6.16.tar.gz](http://download.redis.io/releases/redis-2.6.16.tar.gz)
</li>
1. 安装gdb和glibc-debuginfo
### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E7%AE%80%E4%BB%8B"></a>漏洞简介

利用程序使用了两个漏洞，一个是FORLOOP操作码未验证数据类型导致读取内存指针；另一个是UpVal处理时的内存破坏。因为Lua漏洞的细节在其他文档中详细介绍，本文就不再赘述。Corsix的文档是其中介绍的比较详细的一篇，可以[点击这里](https://gist.github.com/corsix/6575486)先行阅读。



## 公开Exploit的困境

当我下载了很多Poc以及Exp之后，我发现事情远远没有我想象的这么简单，与之相反，工作陷入了困境。我的意思绝不是说这些代码不好，相反，作者都很好的反映了漏洞原理，给了我巨大的帮助。我的困境主要体现在以下几点：
1. 32位和64位的巨大差异。最为明显的是需要用一个TString结构“假装“一个LClosure结构，64位CPU内存对应后比32位环境多出了一个需要伪造的8字节指针。
1. 硬编码的地址或偏移。 有不少使用硬编码偏移量作为寻址方法，这导致了不能在我的测试环境运行，真实更不敢尝试。
1. 不支持的攻击链。 更多Lua的本身的研究文章（非redis的）提出使用位置CClosure结构修改成员指针lua_CFunction f以调用os_execute（这个函数是os.execute的原型）完成逃逸。这是一个稳定的方法，然而只能针对使用了空置os（os = nil）配置lua虚拟机的场景。Redis在编译之初就根本没有编译os系列函数。
1. 利用成功立即崩溃的攻击链。 比较典型的是用jmp_buf机制夺取rip的战术，中间一旦出错或者目标不能出网等复杂情况就失去了二次的机会了。
### <a class="reference-link" name="tonumber%E5%87%BD%E6%95%B0"></a>tonumber函数

这是一个不能更普通的函数，功能是将字符串表示的数字按照指定的进位（如8进制）进行转换。用法也很简单，tonumber(“1245”, 8)。让我们来看看它的具体实现：

[![](https://p4.ssl.qhimg.com/t01edb284405c6e0777.jpg)](https://p4.ssl.qhimg.com/t01edb284405c6e0777.jpg)

可以看到当进制不指定为10，且在2到36之间时，函数会调用libc函数strtoul进行实际的转换操作，齐后判断结果进行返回。把该函数和libc中system函数的定义进行对比：

`unsigned long strtoul(const char *nptr,char **endptr,int base);`

`intsystem(char *command);`

可以发现，两个函数第一个参数均为字符串指针，而我们知道，在x86_64中函数调用的参数传递是优先使用寄存器的。也就是说，假如strtoul实际指向的是（参见GOT表相关知识）system函数的话，并不会因为堆栈平衡而出错。纵观tonumber的函数实现也非常简单，替换后不会引起其他内存访问违例。

总结tonumber作为目标的三点好处：
1. 流程简单，不易出错
1. 调用的glibc函数strtoul和system非常“兼容“
1. 整个程序仅在此对strtoul有调用，不会引起其他功能出错


## 踩雷

### <a class="reference-link" name="%E5%86%99%E5%86%85%E5%AD%98%E4%B8%AD%E7%9A%84%E5%9D%91"></a>写内存中的坑

本文虽然忽略了读写内存细节，但是在构造攻击链之前，必须提一提这个写内存的坑。内存写操作最终是由setobj宏完成的，代码如下：

[![](https://p0.ssl.qhimg.com/t014aa0e32632b347da.jpg)](https://p0.ssl.qhimg.com/t014aa0e32632b347da.jpg)

其中o2-&gt;value包含我们要写入的指针，而o2-&gt;tt是数字变量的4字节类型码，这里是0x03。正是这个可能不可控（目前没有做控制尝试）的值破坏了目标地址后面四个字节，而这在改写got项时对程序的稳定性时致命的：[![](https://p1.ssl.qhimg.com/t016a623ba61b49d569.jpg)](https://p1.ssl.qhimg.com/t016a623ba61b49d569.jpg)

当你覆写strtoul的got项后，后面的pthread_mutex_unlock指针被覆盖成了0x7fff00000003，当调用它时redis立马crash了。

目前的解决方法是先读出一些列的got项内容，在覆写strtoul时对后续的表项进行修复。

### <a class="reference-link" name="%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E7%9A%84%E5%9D%91"></a>垃圾回收的坑

Lua有自己的垃圾回收机制。因为我们在写内存中使用了“假的“Table结构，而这些解构进行回收时很容易引起崩溃。所以我在写内存的lua脚本函数中添加了正确的表项引用，同时反复使用了collectgrabage停用垃圾回收机制，防止服务崩溃。



## 获取重要指针

redis-server是没有地址随机化的，我们攻击链的起点就定在了0x400000这里（假如你要攻击的程序有地址随机化，请自行通过其他内存结构获取基地址，此不在本文的讨论范围内）。

Elf64结构解析寻址细节请参考相关文档，这里只给出基本路径：

Elf64_Ehdr-&gt; Elf64_Phdr[] (偏移;大小) -&gt; Elf64_Dyn _DYNAMIC -&gt;Elf64_Rela[]、Elf64_Sym[]、STRTAB[]（名称字符串数组）-&gt; strtoul[@got](https://github.com/got)

strtoul[@got](https://github.com/got)是第一个重要指针，接下来我们通过调用tonumber函数使这个got项被strtoul的真实地址填充，以此获取strtoul的内存地址：

调用tonumber -&gt; strtoul[@got](https://github.com/got) -&gt;strtoul[@glibc](https://github.com/glibc)

以此为起点，就可以搜索glibc了，路径如下：

strtoul[@glibc](https://github.com/glibc)-&gt; glibc(基地址) -&gt; Elf64_Ehdr -&gt; Elf64_Phdr[] (偏移;大小)-&gt; Elf64_Dyn _DYNAMIC-&gt;Elf64_Sym[]、STRTAB[]-&gt; system[@glibc](https://github.com/glibc)

关于glibc中_DYNAMIC[]和system地址还有个坑值得一提，有的系统上是个偏移地址，有的系统上直接使一个内存地址，这点需要根据大小分开处理。



## 命令执行之路

完事具备，结合之前的内容，思路就很清晰了：
<li>获取strtoul[@got](https://github.com/got)，system[@glibc](https://github.com/glibc)
</li>
1. 备份strtoul[@got](https://github.com/got)之后的got条目址直到NULL
1. 写入system[@glibc](https://github.com/glibc)到strtoul[@got](https://github.com/got)并恢复保持的got条目
1. 通过eval“tonumber(‘uname –a’, 8)” 0执行系统命令


## 结果

附上vps和目标利用截图:

[![](https://p1.ssl.qhimg.com/t016e80fde4564c7fb2.jpg)](https://p1.ssl.qhimg.com/t016e80fde4564c7fb2.jpg)

[![](https://p5.ssl.qhimg.com/t01f6c2cf0724fe96d0.jpg)](https://p5.ssl.qhimg.com/t01f6c2cf0724fe96d0.jpg)

具体利用代码已上传至A-Team的github，[点击此处获取](https://github.com/360-A-Team/redis_lua_exploit)



## 思考

在实际渗透测试中，需要的利用程序都应尽量具有高可用性、高稳定性、高复用性三个特性。通常而言，安全研究人员找到漏洞并验证漏洞以及提出修复方案，而攻击者眼里只有有效的利用代码才能达到目的。两者目的的差异导致了对利用代码要求的不同。

事实上当前大部分漏洞想要稳定有效的利用具有相当的困难，导致了很多运行有漏洞的旧版本服务软件的设备在很长时间均安然无恙，从而未得到重视成为网络安全的边缘地带。

在本例中我花了整整一周时间去完成攻击代码，这正是一些因为不怀好意而耐心充足的攻击者具备的显著特点。个人认为红队工作中扮演这样的攻击者是具有一定意义的。



## 后记

动态获取，got修复，tonumber反复调用，完美了吗？

然而，事实再一次教育了我。在Centos7+最新gcc的编译版本上，仍然出现了got被破坏成0x7fff00000003而造成的访问违例。原因是因为在写完system地址后，代码立即调用了strtoul[@got](https://github.com/got)后面一个表项的函数，而这时这个地址还没来得及修复好。

有点颓然和沮丧，可能换一个写内存方式或者完全控制o2-&gt;tt成员才能彻底解决这个问题。

由于我的任务已经完成了，这个问题，自有后来人吧。

审核人：yiwang   编辑：边边
