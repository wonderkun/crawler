> 原文链接: https://www.anquanke.com//post/id/101894 


# Dreambot与ISFB前生今世


                                阅读量   
                                **77692**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Jerome Cruz，文章来源：www.fortinet.com
                                <br>原文地址：[https://www.fortinet.com/blog/threat-research/dreambot-2017-vs-isfb-2013.html](https://www.fortinet.com/blog/threat-research/dreambot-2017-vs-isfb-2013.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t012068566341bacdba.jpg)](https://p3.ssl.qhimg.com/t012068566341bacdba.jpg)



## 一.写在前面的话

最近，我们收到了一份编译并打包好了的恶意软件样本 ，我们发现，它包含了 一个Dreambot/Ursnif版本的木马，其中汇编日期为2017年10月10日，这表明现有的Dreambot版本可能正在使用一种全新的droppers打包方式。<br>
从过去几年Gozi，ISFB和Mirai等僵尸网络泄露的一些源代码显示，它可能是其中一个的变种。<br>
Dreambot是Gozi后裔ISFB的一个分支（2006年首次观察到),后者又使用了2000年Urnsif的代码。这些木马家族之间共享一些二十年前创建的代码。大部分代码正在被重用，许多代码也只是发生了一些小改动。<br>
其中泄露的ISFB 2013木马中包含许多有关如何构建和配置僵尸网络的文档以及大多数组件的源码。我们接下来分析分析。



## 二. ISFB Bot 2013概述

在泄露的样本中发现有一个readme.txt（用俄语写），详细描述了ISFB的功能。根据该文档，ISFB是一个旨在嗅探和操纵受害者计算机上的HTTP流量的bot。bot做了三件事情：请求接收配置，请求命令，并将数据和文件发送回CnC。<br>
bot接受配置并执行以下操作之一：“NEWGRAB”，“SCREENSHOT”，“PROCESS”，“FILE”，“HIDDEN”，“POST”和“VIDEO”。例如：
- “NEWGRAB” – 将网页上指定的文字替换为另一个文字。
- “SCREENSHOT” – 截取指定页面的屏幕截图。
- “PROCESS” – 当受害者请求配置页面时请求另一个页面，例如，访问某个Twitter用户页面的请求被重定向到不同的Twitter用户页面。bot每个配置的详细信息都可以泄露的源代码中在Format.txt文件中找到。
除了上面介绍的功能，bot还会执行一些命令。这些命令包括：<br>
GET_CERTS – 导出并发送存储在Windows系统中的证书。<br>
GET_COOKIES – 从Firefox，Internet Explorer和Flash SOL文件收集Cookie，将它们与其目录结构一起打包并发送到服务器。<br>
CLR_COOKIES – 从Firefox，Internet Explorer和Flash SOL文件中删除Cookie。<br>
readme.txt文件中有这些命令的完整列表。

### <a class="reference-link" name="Dreambot%202017%E6%A6%82%E8%BF%B0"></a>Dreambot 2017概述

除了ISFB的上述主要功能之外，Dreambot还通过TOR网络连接了CnC的主机。并对用来请求配置的URL的数据进行了更改，稍后我们会对其分析。



## 三.ISFB 2013架构

ISFB bot代码库由两个主要部分组成：Dropper和用于32位和64位机器的bot客户端DLL。<br>
Dropper是包含在泄漏源码中的Crm.exe文件，它包含打包的DLL映像。它将这些DLL复制到系统文件夹中，并使用AppCertDLLs注册表项或自动运行注册表项来注册它们，然后将它们注入explorer.exe进程和所有正在运行的Web浏览器中。<br>
bot客户端DLL也会被dropper注入到explorer.exe和任何正在运行的浏览器中，例如Chrome，IE和Firefox。根据readme.txt的说明，可知bot DLL的职责上分为两部分——“解析器”和“服务器”。<br>
“解析器”是在受感染的浏览器中运行的代码。它拦截HTTP然后向服务器发送命令、配置文件和数据的请求。<br>
“服务器”在explorer.exe中执行，如文件操作，启动程序和更新操作。

### <a class="reference-link" name="%E7%BC%96%E8%AF%91%E5%92%8C%E6%89%93%E5%8C%85"></a>编译和打包

为了编译ISFB bot DLL并将它们打包到dropper中，恶意软件作者使用了一个名为FJ.exe的程序。它首先通过将它们与apLib（可选）包装在一起，然后将它们附加到文件中来。ISFB的构建说明了client32.dll和client64.dll文件已加入public.key和client.ini并输出到client / 32 / 64.dll。然后Crm.exe与这些client32.dll和client64.dll文件连接并输出到installer.exe。

[![](https://p3.ssl.qhimg.com/t014ccc3ed86fea925c.png)](https://p3.ssl.qhimg.com/t014ccc3ed86fea925c.png)<br>
其中ISFB使用了“连接文件”（或“FJ”），这些“FJ”_ADDON_DESCRIPTOR被插入在PE头后面，在所有剩余的PE段头之后，留下0x28字节的空隙，即sizeof（IMAGE_SECTION_HEADER）的值或一个PE头的大小。<br>
2013年泄露的Gozi-ISFB源代码显示了这个_ADDON_DESCRIPTOR结构和ADDON_MAGIC，如下所示：#define ADDON_MAGIC ‘FJ’

```
typedef struct _ADDON_DESCRIPTOR
`{`
USHORT Magic; //addon_MAGIC值
USHORT NumberHashes; //名称的散列阵列
ULONG ImageRva; //RVA填充图像
ULONG ImageSize; //图像大小
ULONG ImageId; // 填充图像ID的图像名称(CRC32)
ULONG Flags; //添加标志
ULONG Hash[0];
`}` ADDON_DESCRIPTOR, *PADDON_DESCRIPTOR;
```

[![](https://p0.ssl.qhimg.com/t014afd55d18fd0d1b1.jpg)](https://p0.ssl.qhimg.com/t014afd55d18fd0d1b1.jpg)<br>
要检索指向加入数据的指针，只需将ImageRVA添加到恶意软件的图像库。这样数据就会被追加到文件的末尾。

### <a class="reference-link" name="Dreambot%202017%E6%9E%B6%E6%9E%84"></a>Dreambot 2017架构

Dreambot的体系结构大致符合ISFB的原型。但是，在注入代码后，explorer.exe向CnC发出请求。另一个变化是，这个新的dropper将自己的一个副本放入一个随机命名的文件夹中的％AppData％。bot DLL不会被丢弃，而是直接注入内存。

### <a class="reference-link" name="%E7%BC%96%E8%AF%91%E5%B9%B6%E6%89%93%E5%8C%85Dreambot2017"></a>编译并打包Dreambot2017

Dreambot使用一个新的’连接’程序，使用’J1’而不是’FJ’，并使用以下结构：<br><code>typedef struct `{`<br>
DWORD j1_magic;<br>
DWORD flags;  //填充aplib<br>
DWORD crc32_name;<br>
DWORD addr;<br>
DWORD size;<br>
`}` isfb_fj_elem ;</code><br>
该结构与’FJ’_ADDON_DESCRIPTOR非常相似，但是这些字段在某些地方进行了交换。尽管考虑了新的结构，但它的功能仍然是获取FJ插件数据，

[![](https://p5.ssl.qhimg.com/t0105e0711e6e00d51a.jpg)](https://p5.ssl.qhimg.com/t0105e0711e6e00d51a.jpg)<br>
Maciej Kotowicz的论文“ISFB，Still Live and Kicking”详细介绍了这种新结构以及如何从2016年的样本中解析出来作为静态配置的INI。论文附录也包括用来解析反编译的伪代码。感兴趣可以去看看。



## 四.ISFB URL请求字符串

可以在泄漏的源代码中找到的文件cschar.h中找到ISFB请求参数的原型。例如：

```
define szRequestFmt_src
_T("soft=1&amp;version=%u&amp;user=%08x%08x%08x%08x&amp;server=%u&amp;id=%u&amp;crc=%x")
```

[![](https://p1.ssl.qhimg.com/t012ffb78f3412ef21f.png)](https://p1.ssl.qhimg.com/t012ffb78f3412ef21f.png)<br>**dreambot2017URL请求**

[![](https://p1.ssl.qhimg.com/t01f8f5b7f4efe135fa.png)](https://p1.ssl.qhimg.com/t01f8f5b7f4efe135fa.png)



## 展望2018及未来

我相信这个僵尸网络工具包平台可能会继续发展，它的代码库将继续纳入更多成员，但无论他怎么变化。我们都将制定更好的对策，并提高我们跟踪和防御此僵尸网络能力。

谢谢Margarette Joven对这个样本和关于dropper和packers的研究。



## IOC

87dec0ca98327e49b326c2d44bc35e5b5ecc5a733cdbb16aeca7cba9471a098e
