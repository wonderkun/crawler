> 原文链接: https://www.anquanke.com//post/id/246158 


# 海莲花的CobaltStrike加载器


                                阅读量   
                                **155421**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t014dc3ecbcb7dc73f3.jpg)](https://p5.ssl.qhimg.com/t014dc3ecbcb7dc73f3.jpg)



## 概述

海莲花（OceanLotus）APT团伙是一个高度组织化的、专业化的境外国家级黑客组织，其最早由红雨滴团队发现并披露。该组织至少自2012年4月起便针对中国政府、科研院所、海事机构、海域建设、航运企业等相关重要领域展开了有组织、有计划、有针对性的长时间不间断攻击。

最近几个月又是海莲花活动的高峰期，在对样本一一分析之后，笔者发现大多数样本都会层层解密，最后加载CobaltStrike的Beacon。



## 样本分析

### <a class="reference-link" name="%E6%A0%B7%E6%9C%AC%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF"></a>样本基本信息

样本md5：edf7dc76776cd05ecf1bc190ae591654<br>
样本于6月3日首次上传到VT，由于海莲花的样本一般情况下都会修改文件时间戳，所以无法从CreateTime获取有用的信息：

[![](https://p0.ssl.qhimg.com/t0164ca80538d1f0ce5.png)](https://p0.ssl.qhimg.com/t0164ca80538d1f0ce5.png)

有意思的是，vt厂商大多数检出为CobaltStrike相关的样本：

[![](https://p5.ssl.qhimg.com/t01893252416433b71c.png)](https://p5.ssl.qhimg.com/t01893252416433b71c.png)

### <a class="reference-link" name="%E5%A4%96%E5%B1%82%E5%8A%A0%E8%BD%BD%E5%99%A8%E5%88%86%E6%9E%90"></a>外层加载器分析

比较遗憾的是此次并未捕获到诱饵文件，原始样本为32位dll，dll恶意代码执行入口为DllMain，由于dll中暂无其他的信息，暂时无法推测加载模式是白利用还是非PE直接加载。

[![](https://p1.ssl.qhimg.com/t0117a67ec88233af6c.png)](https://p1.ssl.qhimg.com/t0117a67ec88233af6c.png)

样本外层是一个loader，功能非常简单：读取名为W5X8T4的资源表项并为其分配内存空间，最后call edi执行资源中的代码：

[![](https://p2.ssl.qhimg.com/t017be9701d0522ac70.png)](https://p2.ssl.qhimg.com/t017be9701d0522ac70.png)

如下所示：

[![](https://p1.ssl.qhimg.com/t018a309bebac5587c3.png)](https://p1.ssl.qhimg.com/t018a309bebac5587c3.png)

### <a class="reference-link" name="%E8%B5%84%E6%BA%90shellcode%E5%88%86%E6%9E%90"></a>资源shellcode分析

资源的shellcode加载之后，有大量的混淆代码，和海莲花之前的样本类似

[![](https://p5.ssl.qhimg.com/t0138fc415e5d57a7f6.png)](https://p5.ssl.qhimg.com/t0138fc415e5d57a7f6.png)

第一个call中主要是调用CreateThread启动一个新线程：

[![](https://p3.ssl.qhimg.com/t014d88fcb1ca5e3f2b.png)](https://p3.ssl.qhimg.com/t014d88fcb1ca5e3f2b.png)

该线程主要用于启动服务：

[![](https://p0.ssl.qhimg.com/t01bf8798fb315f1d1e.png)](https://p0.ssl.qhimg.com/t01bf8798fb315f1d1e.png)

线程创建完成之后，程序将会加载所需dll，并依次获取函数的的地址。<br>
加载动态库：

[![](https://p5.ssl.qhimg.com/t01b30d1ac4f8869eba.png)](https://p5.ssl.qhimg.com/t01b30d1ac4f8869eba.png)

获取API地址：

[![](https://p1.ssl.qhimg.com/t016c283fd17dcbe7d0.png)](https://p1.ssl.qhimg.com/t016c283fd17dcbe7d0.png)

这部分代码都不用管，直接跳过即可，所有API地址获取完成之后，程序将会设置异常处理

[![](https://p0.ssl.qhimg.com/t0140cc0990916416bc.png)](https://p0.ssl.qhimg.com/t0140cc0990916416bc.png)

接着处理svchost.exe的路径，方便之后启动并注入该进程：

[![](https://p1.ssl.qhimg.com/t01beaba9b4e0d79176.png)](https://p1.ssl.qhimg.com/t01beaba9b4e0d79176.png)

继续加载动态库：

[![](https://p4.ssl.qhimg.com/t0169c14fda8b13488f.png)](https://p4.ssl.qhimg.com/t0169c14fda8b13488f.png)

获取api地址：

[![](https://p3.ssl.qhimg.com/t01c2884a2eaaf72c42.png)](https://p3.ssl.qhimg.com/t01c2884a2eaaf72c42.png)

创建svchost进程

[![](https://p2.ssl.qhimg.com/t0161231c75d3abbc77.png)](https://p2.ssl.qhimg.com/t0161231c75d3abbc77.png)

创建成功之后，通过GetProcessID获取目标进程ID：

[![](https://p0.ssl.qhimg.com/t0195571252a7947ba8.png)](https://p0.ssl.qhimg.com/t0195571252a7947ba8.png)

通过VirtualAllocEx在目标进程中开辟内存空间

[![](https://p5.ssl.qhimg.com/t01dadb2317b08b3112.png)](https://p5.ssl.qhimg.com/t01dadb2317b08b3112.png)

第二段内存空间：

[![](https://p3.ssl.qhimg.com/t0185d3227fcb8be79a.png)](https://p3.ssl.qhimg.com/t0185d3227fcb8be79a.png)

分配完成之后，通过WriteProcessMemory先向第二次分配的内存空间写入指定的shellcode：

[![](https://p4.ssl.qhimg.com/t01b40f89724691208d.png)](https://p4.ssl.qhimg.com/t01b40f89724691208d.png)

写入完成之后如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c79412f9429a9200.png)

接着创建进程快照，查找被注入的4B4进程，找到之后OpenThread打开线程对象

[![](https://p2.ssl.qhimg.com/t012ac7d100c254bc54.png)](https://p2.ssl.qhimg.com/t012ac7d100c254bc54.png)

暂停目标线程

[![](https://p3.ssl.qhimg.com/t01e1fea365e22eb2d3.png)](https://p3.ssl.qhimg.com/t01e1fea365e22eb2d3.png)

接着向D0000写入代码，代码关键是：<br>
mov eax,0xe0000<br>
call eax<br>
执行e0000处的代码

[![](https://p2.ssl.qhimg.com/t0196445806ed3b47ed.png)](https://p2.ssl.qhimg.com/t0196445806ed3b47ed.png)

通过结构体设置新线程执行的目标函数：

[![](https://p1.ssl.qhimg.com/t019c7a1177ec2f57f0.png)](https://p1.ssl.qhimg.com/t019c7a1177ec2f57f0.png)

最后ResumeThread，成功调用shellcode

[![](https://p4.ssl.qhimg.com/t01f5fc5eaa492ad069.png)](https://p4.ssl.qhimg.com/t01f5fc5eaa492ad069.png)

要调试shellcode，可以附加目标进程调试该段shellcode，不过该样本的shellcode比较简单，可以不用那么麻烦，直接设置eip也可以成功调试。

[![](https://p1.ssl.qhimg.com/t01c25139a0196203ee.png)](https://p1.ssl.qhimg.com/t01c25139a0196203ee.png)

该段shellcode主要只有两个call，第一个call ebx会解密出cs的Beacon后门并加载，加载之后将Beacon的DllEntryPoint地址赋值给eax通过call eax再次调用。

[![](https://p4.ssl.qhimg.com/t01d9225e8996ad4008.png)](https://p4.ssl.qhimg.com/t01d9225e8996ad4008.png)

第一个call首先会VirtualAlloc分配内存空间，然后将shellcode拷贝到该地址处：

[![](https://p5.ssl.qhimg.com/t0136b76f34d226680d.png)](https://p5.ssl.qhimg.com/t0136b76f34d226680d.png)

通过VirtualProtect更改shellcode的可执行属性：

[![](https://p5.ssl.qhimg.com/t019be4ad4388759a0e.png)](https://p5.ssl.qhimg.com/t019be4ad4388759a0e.png)

接着call 到指定的地址执行，call过来的shellcode地址就是dll entrypoint<br>
call调用之后，程序还会将该地址（[ebp-0x34]）赋值给eax，等下call eax再次调用

[![](https://p3.ssl.qhimg.com/t01df584f593133ab52.png)](https://p3.ssl.qhimg.com/t01df584f593133ab52.png)

将该段内存dump出来，跳转到01f75cb0这个入口点，笔者使用了IDA7.5的拉取符号功能，这里自动识别出了DllEntryPoint函数

[![](https://p0.ssl.qhimg.com/t012da56a8c285e3d0c.png)](https://p0.ssl.qhimg.com/t012da56a8c285e3d0c.png)

从通过参数序列，很容易就找到具体的DllMain函数

[![](https://p4.ssl.qhimg.com/t011a4f5c1497d5b08e.png)](https://p4.ssl.qhimg.com/t011a4f5c1497d5b08e.png)

根据DllMain的代码，感觉很像是CobaltStrike的远控模块，于是笔者找到了之前分析过的cs模块，对比之后可以确认该样本为CobaltStrike生成：

[![](https://p0.ssl.qhimg.com/t0129e1e4e16d88e440.png)](https://p0.ssl.qhimg.com/t0129e1e4e16d88e440.png)

解密请求C2

[![](https://p0.ssl.qhimg.com/t010c6330b6941df347.png)](https://p0.ssl.qhimg.com/t010c6330b6941df347.png)

解密请求头：

[![](https://p5.ssl.qhimg.com/t01d9c996f41ccbe743.png)](https://p5.ssl.qhimg.com/t01d9c996f41ccbe743.png)

通过InternetOpen请求C2：185[.]225[.]19[.]22

[![](https://p1.ssl.qhimg.com/t0120a89e4be3672fd0.png)](https://p1.ssl.qhimg.com/t0120a89e4be3672fd0.png)

该ip关联域名：impeplaism.info<br>
该域名已经有OceanLotus标签

[![](https://p2.ssl.qhimg.com/t0192625efe07dcf121.png)](https://p2.ssl.qhimg.com/t0192625efe07dcf121.png)
