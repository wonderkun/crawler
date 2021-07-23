> 原文链接: https://www.anquanke.com//post/id/231427 


# 谈谈Office Moniker类漏洞和公式编辑器类漏洞


                                阅读量   
                                **136543**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01df0ef15279f9c1f8.jpg)](https://p5.ssl.qhimg.com/t01df0ef15279f9c1f8.jpg)



在近几年出现的诸多office漏洞中，有两类漏洞是很值得谈谈的，第一类是Moniker导致的逻辑漏洞，第二类是公式编辑器漏洞。

对于第一类漏洞，其重点在于攻击者和微软安全团队之间的攻防过程，了解这类漏洞攻防过程对威胁追踪与研究较有益处：
1. 第一回合：CVE-2017-0199，用URL Moniker加载远程HTA文件实现远程代码执行；
1. 第二回合：CVE-2017-8570，用CompositeMoniker、FileMoniker、NewMoniker、scriptletfile实现远程代码执行；
1. 第三回合：CVE-2017-8759，用office文档加载.Net组件漏洞，实现远程代码执行；
1. 第四回合：CVE-2018-8174，用office文档加载IE VBScript组件漏洞，实现远程代码执行；
1. 第五回合：CVE-2020-0674，用office文档加载IE JavaScript组件漏洞，实现远程代码执行。
对于第二类漏洞，其难点在于对相似漏洞之间的区分。从CVE-2017-11882开始，到CVE-2018-0802，再到CVE-2018-0798，三个都是非常相似的漏洞，在静态层面不容易区分，本文将分享一个在动态层面区分它们的方法。

下面跟随笔者一起来看一下这两类漏洞。



## Moniker类漏洞

### <a class="reference-link" name="%E7%AC%AC%E4%B8%80%E5%9B%9E%E5%90%88%EF%BC%9ACVE-2017-0199"></a>第一回合：CVE-2017-0199

2017年4月7日，著名office漏洞研究员李海飞发布了一篇在野0day攻击预警，首度披露了CVE-2017-0199漏洞的在野攻击。随后，2017年4月11日和12日，FireEye连发两篇文章，披露了他们捕获到的CVE-2017-0199漏洞样本细节。后续的披露表明这几篇文章中披露的漏洞是一种借助URL Moniker特性加载远程hta文件的新型漏洞，这是一个由于开发者对office文件加载机制设计不合理导致的逻辑漏洞，且要求触发环境安装IE10/IE11。漏洞触发过程不需要用户交互，但在触发的过程中会弹出一个对话框，不点击或者点击任意该对话框的按钮都不影响执行过程，对话框样式如下：

[![](https://p2.ssl.qhimg.com/t01b9c0d381a6709a89.png)](https://p2.ssl.qhimg.com/t01b9c0d381a6709a89.png)

该漏洞的发现者之一李海飞曾经在Syscan360 2017会议上做过题为《Moniker Magic: Running Scripts Directly in Microsoft Office》的演讲，里面详细介绍了CVE-2017-0199的细节，包括：
1. 微软在CVE-2017-0199的补丁中修复了两个漏洞，分别是被在野利用的RTF URL Moniker加载远程HTA文件的远程代码执行漏洞，和李海飞独立发现的PPSX Script Moniker远程代码执行漏洞；
1. office安全团队在这两个漏洞的基础上设计了一类针对Moniker的黑名单机制，禁用了一些他们觉得不安全的Moniker。
Moniker本身是office的一个特性，可以用来链接一些本地或远程对象，其本身不属于漏洞，漏洞发生在office软件对远程链接的文件的执行策略上。譬如，如果远程加载的是一个Excel文件，直接打开没问题；但如果加载的是HTA文件和Script这类脚本文件时，直接执行就存在问题了，导致了漏洞。

### <a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E5%9B%9E%E5%90%88%EF%BC%9ACVE-2017-8570"></a>第二回合：CVE-2017-8570

在对CVE-2017-0199补丁的研究过程中，李海飞发现（上面也已经提到）：
- office安全团队在这CVE-2017-0199的补丁中设计了一类针对Moniker的黑名单机制，禁用了一些他们觉得不安全的Moniker。
于是他开始寻找那些还没有被禁用的Moniker，尝试用那些没有被禁用的Moniker构造出另一个逻辑漏洞，结果确实找到一个，即CVE-2017-8570。

在CVE-2017-0199中，用到的Moniker是下面这两个：

```
3050F4D8-98B5-11CF-BB82-00AA00BDCE0B // htafile
06290BD3-48AA-11D2-8432-006008C3FBFC // scriptlet(or ScriptMoniker)
```

而在CVE-2017-8570中，用到的Moniker是下面这几个：

```
00000309-0000-0000-C000-000000000046 // CompositeMoniker
00000303-0000-0000-C000-000000000046 // FileMoniker
ECABAFC6-7F19-11D2-978E-0000F8757E2A // NewMoniker
06290BD2-48AA-11D2-8432-006008C3FBFC // scriptletfile(or ScripletFactory)
```

可以看到CVE-2017-8570利用未被加入黑名单的Moniker绕过了CVE-2017-0199的补丁。

不过，许多分析过CVE-2017-8570的读者可能会观察到一个奇怪的现象：漏洞中触发时script脚本中的代码会被执行两次。这是为什么呢？原来，在这个漏洞的触发逻辑中，会涉及到wwlib.dll库中的一个函数调用，该函数内部会顺序调用ole32!CDefLink::BindToSource和ole32!CDefLink::Update两个函数，如下（以office 2010为例）：

[![](https://p3.ssl.qhimg.com/t01905a53b85eef8b17.png)](https://p3.ssl.qhimg.com/t01905a53b85eef8b17.png)

而这两个函数最终都会调用kernel32!CreateProcessW创建进程，所以script脚本中的代码会被执行两次。其中ole32!CDefLink::BindToSource创建进程的栈回溯如下：

```
0:000&gt; k 50
ChildEBP RetAddr  
0013a5b4 729cd2f5 kernel32!CreateProcessW
0013a63c 729cd5f7 wshom!CreateNewProcessW+0x6f
0013a69c 76da3e75 wshom!CWshShell::Exec+0x19a
0013a6bc 76da3cef OLEAUT32!DispCallFunc+0x165
0013a74c 729d0267 OLEAUT32!CTypeInfo2::Invoke+0x23f
...cut...
0013ae9c 7705b5dc comsvcs!CNewMoniker::BindToObject+0x14f
0013aed0 770c3cc6 ole32!CCompositeMoniker::BindToObject+0x105 [d:\w7rtm\com\ole32\com\moniker2\ccompmon.cxx @ 1104]
0013af3c 68ee87ce ole32!CDefLink::BindToSource+0x1bf [d:\w7rtm\com\ole32\ole232\stdimpl\deflink.cpp @ 4637]
0013af80 68a61429 wwlib!wdGetApplicationObject+0x69230 // 第一处调用
0013b010 68a23b2c wwlib!DllGetLCID+0x4753b3
...cut...
```

而ole32!CDefLink::Update创建进程的栈回溯如下：

```
0:000&gt; k 50
ChildEBP RetAddr  
0013a57c 729cd2f5 kernel32!CreateProcessW
0013a604 729cd5f7 wshom!CreateNewProcessW+0x6f
0013a664 76da3e75 wshom!CWshShell::Exec+0x19a
0013a684 76da3cef OLEAUT32!DispCallFunc+0x165
0013a714 729d0267 OLEAUT32!CTypeInfo2::Invoke+0x23f
...cut...
0013ae68 7705b5dc comsvcs!CNewMoniker::BindToObject+0x14f
0013ae9c 770c3c55 ole32!CCompositeMoniker::BindToObject+0x105 [d:\w7rtm\com\ole32\com\moniker2\ccompmon.cxx @ 1104]
0013af08 7710f7ee ole32!CDefLink::BindToSource+0x14e [d:\w7rtm\com\ole32\ole232\stdimpl\deflink.cpp @ 4611]
0013af30 7710f42a ole32!CDefLink::Update+0x62 [d:\w7rtm\com\ole32\ole232\stdimpl\deflink.cpp @ 5347]
0013af44 68ee8830 ole32!CDefLink::Update+0x33 [d:\w7rtm\com\ole32\ole232\stdimpl\deflink.cpp @ 2695]
0013af80 68a61429 wwlib!wdGetApplicationObject+0x69292 // 第二处调用 
0013b010 68a23b2c wwlib!DllGetLCID+0x4753b3
...cut...
```

### <a class="reference-link" name="%E7%AC%AC%E4%B8%89%E5%9B%9E%E5%90%88%EF%BC%9ACVE-2017-8759"></a>第三回合：CVE-2017-8759

在CVE-2017-8570漏洞被修复后，累计有如下这些Moniker被加入黑名单：

```
3050F4D8-98B5-11CF-BB82-00AA00BDCE0B // htafile
06290BD3-48AA-11D2-8432-006008C3FBFC // scriptlet(or ScriptMoniker)
00000309-0000-0000-C000-000000000046 // CompositeMoniker
00000303-0000-0000-C000-000000000046 // FileMoniker
ECABAFC6-7F19-11D2-978E-0000F8757E2A // NewMoniker
06290BD2-48AA-11D2-8432-006008C3FBFC // scriptletfile(or ScripletFactory)
```

在前面几个Moniker不能使用之后，攻击者又注意到了下面这个Moniker：

```
ecabb0c7-7f19-11d2-978e-0000f8757e2a // SOAPMoniker
```

SOAP Moniker可以用来加载一个远程的SOAP配置文件，当Word进程远程加载这个配置文件时，.Net组件会被加载用来解析对应的配置文件，并按照配置自动生成一个C#文件，再自动将该C#文件编译得到一个动态链接库并执行。攻击者借助.Net SOAP WSDL模块中的一个代码注入漏洞（CVE-2015-8759），将恶意脚本代码注入到了待编译的C#文件中，从而让编译得到的动态链接库包含恶意代码并自动执行。

从CVE-2017-8759开始，攻击者开始借助office组件与其他Windows组件之间的交互进行攻击。.Net的漏洞本身不属于office的范围，却可以借助office文档进行触发，这种攻击方式当时给笔者留下了深刻的印象。

### <a class="reference-link" name="%E7%AC%AC%E5%9B%9B%E5%9B%9E%E5%90%88%EF%BC%9ACVE-2018-8174"></a>第四回合：CVE-2018-8174

CVE-2017-8759被修复后，Moniker黑名单又得到了更新：

```
3050F4D8-98B5-11CF-BB82-00AA00BDCE0B // htafile
06290BD3-48AA-11D2-8432-006008C3FBFC // scriptlet(or ScriptMoniker)
00000309-0000-0000-C000-000000000046 // CompositeMoniker
00000303-0000-0000-C000-000000000046 // FileMoniker
ECABAFC6-7F19-11D2-978E-0000F8757E2A // NewMoniker
06290BD2-48AA-11D2-8432-006008C3FBFC // scriptletfile(or ScripletFactory)
ecabb0c7-7f19-11d2-978e-0000f8757e2a // SOAPMoniker
```

在上面这些Moniker都不可用之后，攻击者又想出了一种新的攻击方式：借助URL Moniker去加载远程html文件，这样就可以借助office加载IE漏洞。攻击者首先用URL Moniker+CVE-2014-6332的组合试了一下该方案的可行性，笔者追溯到的这方面的最早样本为2018年1月17日的下面这个文件（以及相关文件）：

```
// CVE-2014-6332
Document MD5: A9D3F7A1ACD624DE705CF27EC699B6B6
URL Moniker: hxxp://s.dropcanvas[.]com/1000000/940000/939574/akw.html
akw.html MD5: C40A128AE7AEFFA3C1720A516A99BBDF
```

到了2018年4月，攻击者终于按捺不住了，借助URL Moniker+IE VBScript 0day的方式对特定目标进行了攻击，这次攻击所用漏洞就是著名的CVE-2018-8174，相关样本如下：

```
// CVE-2018-8174
Document MD5: b48ddad351dd16e4b24f3909c53c8901
URL Moniker: hxxp://autosoundcheckers[.]com/s2/search[.]php?who=7
search.htm MD5: 15eafc24416cbf4cfe323e9c271e71e7
```

CVE-2018-8174出现后，微软安全团队并未直接将office加载VBScript脚本的功能进行限制。随后，在2018年7月，攻击者又借助另一个IE VBScript 0day（CVE-2018-8173），用相同的方式实施了攻击。

这下微软不淡定了，赶紧对Office加载VBScript脚本进行了限制。

### <a class="reference-link" name="%E7%AC%AC%E4%BA%94%E5%9B%9E%E5%90%88%EF%BC%9ACVE-2020-0674"></a>第五回合：CVE-2020-0674

故事到这里就结束了吗？当然没有。此时，微软依然没有限制office加载JavaScript脚本，所以IE浏览器的两个JavaScript引擎：JScript和JScript9依然可以通过此种方式进行攻击。

其一，据笔者所知，在2018年的天府杯上，针对office项目的攻击采用了URL Moniker + IE JScript9 0day的组合。

其二，2019年-2020年，由于几个JScript漏洞被相继披露，陆续有APT攻击组织使用URL Moniker + JScript 1day的方式实施攻击，相关样本如下：

```
// CVE-2020-0674
Document MD5: 90403dfafa3c573c49aa52c5fe511169
URL Moniker: hxxp://tsinghua.gov-mil[.]cn/images/A96961AA/36604/1836/65449576/ab8feee
ab8feee MD5: 1892D293030E81D0D1D777CB79A0FDBE

// CVE-2020-0968
Document MD5: 60981545a5007e5c28c8275d5f51d8f0
URL Moniker: hxxp://94.156.174[.]7/up/a1a.htm
a1a.htm MD5: 293916af3a30b3d7a0dc2949115859a6
```

于是微软在高版本office中（office2016及以上版本）也加入了对JScript9脚本和JScript脚本的加载限制。

至此，攻击者针对Moniker的所有尝试都被微软进行了封堵，此后未观察到针对Moniker的新攻击方式。



## 公式编辑器漏洞

2017年11月补丁日，国外安全公司_embedi发表了一篇《SKELETON IN THE CLOSET: MS Office vulnerability you didn’t know about》详细描述了他们发现office公式编辑器漏洞CVE-2017-11882的整个过程（笔者发现这家公司的官网已经挂了…）。

属于office公式编辑器漏洞的时代至此开启。

由于组件源码的丢失，微软的补丁开发人员花了较长时间来修复这一漏洞，并且以一种近乎炫技的方式，直接在二进制层面对程序作了修补，在没有重新编译源码的情况下修复了漏洞，并添加了ASLR支持。

然而，一时激起千层浪，CVE-2017-11882出现后，广大安全研究员蜂拥而至，都开始关注office公式编辑器这一组件，这直接导致微软在2018年1月的更新中砍掉了公式编辑器组件。

在第二次修复的诸多office公式编辑器漏洞中，有两个漏洞比较值得注意，这两个漏洞分别为CVE-2018-0802和CVE-2018-0798，三个漏洞并称为office公式编辑器漏洞领域的“三驾马车”，

由于笔者经常看到分析人员对这三个漏洞的样本进行误判，所以这里分享一种在动态层面区分这三个漏洞的方法。

首先跟随笔者来了解一下这三个漏洞的具体成因，下文中的汇编代码基于以下公式编辑器组件：

```
eqnedt32.exe 2000.11.9.0
```

在office中，公式编辑器的数据被存储在一个OLE文件的“Equation Native”流中，三个公式编辑器漏洞都是在处理这个流的数据时出现的问题。

[![](https://p3.ssl.qhimg.com/t01c53bc346d6f67fe7.png)](https://p3.ssl.qhimg.com/t01c53bc346d6f67fe7.png)

### <a class="reference-link" name="CVE-2017-11882"></a>CVE-2017-11882

首先来看一下CVE-2017-11882。

该漏洞的成因为：在读入“Equation Native”流中的Font Name Record数据时，在将Name拷贝到某个局部变量的时候没有对Name的长度做校验，从而造成栈缓冲区溢出，漏洞发生点如下图所示：

[![](https://p2.ssl.qhimg.com/t018e48343cf9a0aa79.png)](https://p2.ssl.qhimg.com/t018e48343cf9a0aa79.png)

从下图可以看出，函数给SrcStr变量分配的大小是0x24个字节，Name长度超过该大小就会造成栈溢出。

[![](https://p0.ssl.qhimg.com/t0160290d949bcbdd0e.png)](https://p0.ssl.qhimg.com/t0160290d949bcbdd0e.png)

CVE-2017-11882的触发逻辑如下所示：

[![](https://p4.ssl.qhimg.com/t01a7f3d6fb795e1c2b.png)](https://p4.ssl.qhimg.com/t01a7f3d6fb795e1c2b.png)

### <a class="reference-link" name="CVE-2018-0802"></a>CVE-2018-0802

再来看一下CVE-2018-0802。

该漏洞的成因为：在将“Equation Native”流中的Font Name Record数据拷贝到一个LOGFONT结构体（位于栈上）内的lfFaceName成员（它是一个以空结尾的char型字符串，最大长度为0x20，其中包含终止符NULL），没有对Name的长度做校验，从而造成栈缓冲区溢出，漏洞发生点如下图所示：

[![](https://p4.ssl.qhimg.com/t016fd6d328c58ef5ce.png)](https://p4.ssl.qhimg.com/t016fd6d328c58ef5ce.png)

CVE-2018-0802漏洞的触发路径和CVE-2017-11882有很大的重叠，下图可以做一个直观的比对：

[![](https://p4.ssl.qhimg.com/t01c2599832501abd70.png)](https://p4.ssl.qhimg.com/t01c2599832501abd70.png)

由于某些限制，CVE-2018-0802在未打CVE-2017-11882补丁的版本上只会造成crash，但在打了补丁的版本上可以实现远程代码执行。

### <a class="reference-link" name="CVE-2018-0798"></a>CVE-2018-0798

最后看一下CVE-2018-0798。

该漏洞的成因为：在读入“Equation Native”流中的Matrix Record数据时，存在一处while循环内的数据读取操作，由于未对Matrix的行和列两个参数进行校验，从而使攻击者可以控制由此计算得到的拷贝长度，导致栈缓冲区溢出：

[![](https://p2.ssl.qhimg.com/t01acd9e13ee5031ccc.png)](https://p2.ssl.qhimg.com/t01acd9e13ee5031ccc.png)

上述汇编片段描述了一个while循环，反汇编成伪代码如下，攻击者可以控制伪码中v2的大小，从而导致了数据读写越界：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01749ddb565d1df081.png)

上述代码位于sub_443F6C函数内，所以理论上只要调用sub_443F6C函数的地方均存在CVE-2018-0798漏洞。作为与之前两个漏洞的对比，在之前两个漏洞的基础上加入CVE-2018-0798的触发路径如下：

[![](https://p4.ssl.qhimg.com/t01f4430daef1e5a0b0.png)](https://p4.ssl.qhimg.com/t01f4430daef1e5a0b0.png)

### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E5%8C%BA%E5%88%86%E4%B8%89%E4%B8%AA%E5%85%AC%E5%BC%8F%E7%BC%96%E8%BE%91%E5%99%A8%E6%BC%8F%E6%B4%9E"></a>动态区分三个公式编辑器漏洞

以上笔者已经介绍了三个公式编辑器漏洞的成因，借助上述知识，很容易在调试器中确认特定样本使用的漏洞，判定方式如下：

```
// CVE-2017-11882
.text:00411655 C1 E9 02                shr     ecx, 2 // 获取此偏移处的ecx值，若ecx的值位于(0x20, 0x94]区间，即为CVE-2017-11882
.text:00411658 F3 A5                   rep movsd
.text:0041165A 8B C8                   mov     ecx, eax
.text:0041165C 83 E1 03                and     ecx, 3

// CVE-2018-0802
.text:00421E5B C1 E9 02                shr     ecx, 2 // 获取此偏移处的ecx值，若ecx的值大于0x94，即为CVE-2018-0802
.text:00421E5E F3 A5                   rep movsd
.text:00421E60 8B C8                   mov     ecx, eax
.text:00421E62 83 E1 03                and     ecx, 3
.text:00421E65 F3 A4                   rep movsb

// CVE-2018-0798
.text:00443F79 8D 04 45 02 00 00 00    lea     eax, ds:2[eax*2]
.text:00443F80 83 C0 07                add     eax, 7
.text:00443F83 C1 F8 03                sar     eax, 3
.text:00443F86 66 89 45 08             mov     [ebp+arg_0], ax // 获取此偏移处的eax值，若eax的值大于4，即为CVE-2018-0798
```

有些样本会同时满足上述两个或三个条件，因为这些样本中内嵌多个公式编辑器漏洞利用。

### <a class="reference-link" name="%E5%BB%B6%E4%BC%B8"></a>延伸

细心的读者会发现2020年极棒大赛上使用的某国产软件公式编辑器漏洞和CVE-2018-0798基本一样，有兴趣的读者可以自行对比研究。



## 参考链接

[https://www.mcafee.com/blogs/other-blogs/mcafee-labs/critical-office-zero-day-attacks-detected-wild/](https://www.mcafee.com/blogs/other-blogs/mcafee-labs/critical-office-zero-day-attacks-detected-wild/)<br>[https://www.fireeye.com/blog/threat-research/2017/04/cve-2017-0199-hta-handler.html](https://www.fireeye.com/blog/threat-research/2017/04/cve-2017-0199-hta-handler.html)<br>[https://www.fireeye.com/blog/threat-research/2017/04/cve-2017-0199_useda.html](https://www.fireeye.com/blog/threat-research/2017/04/cve-2017-0199_useda.html)<br>[https://0b3dcaf9-a-62cb3a1a-s-sites.googlegroups.com/site/zerodayresearch/Moniker_Magic_final.pdf](https://0b3dcaf9-a-62cb3a1a-s-sites.googlegroups.com/site/zerodayresearch/Moniker_Magic_final.pdf)<br>[http://justhaifei1.blogspot.com/2017/07/bypassing-microsofts-cve-2017-0199-patch.html](http://justhaifei1.blogspot.com/2017/07/bypassing-microsofts-cve-2017-0199-patch.html)<br>[https://www.fireeye.com/blog/threat-research/2017/09/zero-day-used-to-distribute-finspy.html](https://www.fireeye.com/blog/threat-research/2017/09/zero-day-used-to-distribute-finspy.html)<br>[https://securelist.com/root-cause-analysis-of-cve-2018-8174/85486/](https://securelist.com/root-cause-analysis-of-cve-2018-8174/85486/)<br>[https://ti.dbappsecurity.com.cn/blog/index.php/2020/07/13/sidewinder-new-attack-target-cn/](https://ti.dbappsecurity.com.cn/blog/index.php/2020/07/13/sidewinder-new-attack-target-cn/)<br>[https://ti.dbappsecurity.com.cn/blog/index.php/2020/09/18/operation-domino/](https://ti.dbappsecurity.com.cn/blog/index.php/2020/09/18/operation-domino/)<br>[https://support.microsoft.com/en-us/help/4058123/security-settings-for-com-objects-in-office](https://support.microsoft.com/en-us/help/4058123/security-settings-for-com-objects-in-office)<br>[https://www.anquanke.com/post/id/87311](https://www.anquanke.com/post/id/87311)<br>[https://www.anquanke.com/post/id/94210](https://www.anquanke.com/post/id/94210)<br>[https://www.freebuf.com/vuls/160409.html](https://www.freebuf.com/vuls/160409.html)
