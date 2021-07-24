> 原文链接: https://www.anquanke.com//post/id/239246 


# Hvv样本合集分析（二）- Golang恶意样本分析


                                阅读量   
                                **225325**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01f1358cf0abebebc1.jpg)](https://p0.ssl.qhimg.com/t01f1358cf0abebebc1.jpg)



## 概述

由于golang的跨平台性，以及golang框架的复杂性所带来的免杀效果，现在越来越多的攻击者/红队开始使用golang开发恶意样本，这里做一个小结，记录下

此文章总结了hvv期间攻击者利用golang加载cs的一些样本，故也可以称之为“CobaltStrike的多种加载方式”

样本基本都来源于微步社区，确定为hvv期间攻击队使用样本。



## 样本分析

### <a class="reference-link" name="golang%E5%8F%8D%E8%B0%83%E8%AF%95"></a>golang反调试

还原golang符号之后，在main_main入口的地方看到有一个main_sandbox_CheckForPass函数，很明显这是一个检测虚拟环境的函数。

[![](https://p3.ssl.qhimg.com/t0165cc406b333c52c5.png)](https://p3.ssl.qhimg.com/t0165cc406b333c52c5.png)

该函数里面的第一个函数checkThreadBook疑似判断是否在微步沙箱中：

[![](https://p4.ssl.qhimg.com/t010ddeaf2fc819e33b.png)](https://p4.ssl.qhimg.com/t010ddeaf2fc819e33b.png)

此外，程序还有可能进行CPU检查、内存检测、启动检测、启动时间检测等

[![](https://p4.ssl.qhimg.com/t01490bc3495f4bd368.png)](https://p4.ssl.qhimg.com/t01490bc3495f4bd368.png)

若经过检测代码运行在虚拟环境中，程序则会直接退出：

[![](https://p5.ssl.qhimg.com/t01c25d4b5f172013a4.png)](https://p5.ssl.qhimg.com/t01c25d4b5f172013a4.png)

手动调试之后，将这个验证过掉，然后F9运行，同时监控该文件行为

[![](https://p3.ssl.qhimg.com/t01862359238680b82e.png)](https://p3.ssl.qhimg.com/t01862359238680b82e.png)

程序在tmp目录下释放并加载了两个PE，其中_install.exe是恶意模块，TencentMeeting是带有签名的正常腾讯会议安装包。

[![](https://p5.ssl.qhimg.com/t01a68be631021b73e1.png)](https://p5.ssl.qhimg.com/t01a68be631021b73e1.png)

程序加载恶意模块的时候同时会启动腾讯会议的安装包以迷惑用户：

[![](https://p3.ssl.qhimg.com/t01ba36ddd5b01c70fd.png)](https://p3.ssl.qhimg.com/t01ba36ddd5b01c70fd.png)

恶意模块依旧由golang编译而成，和第一层的Dropper类似，该组件执行时也会先进行虚拟环境检测：

[![](https://p2.ssl.qhimg.com/t013a29939f38820773.png)](https://p2.ssl.qhimg.com/t013a29939f38820773.png)

接着解码一段base64的数据得到后续的shellcode

[![](https://p2.ssl.qhimg.com/t01ee43f982cb1a11c7.png)](https://p2.ssl.qhimg.com/t01ee43f982cb1a11c7.png)

重新开辟内存空间，并将解密之后的shellcode拷贝过去：

[![](https://p4.ssl.qhimg.com/t01ded47e0badbb078a.png)](https://p4.ssl.qhimg.com/t01ded47e0badbb078a.png)

解密后的shellcode是CobaltStrike的远控模块，直接尝试在shellcode头部设置执行断点，成功命中：

[![](https://p5.ssl.qhimg.com/t0191ef2d1c2f6d0af3.png)](https://p5.ssl.qhimg.com/t0191ef2d1c2f6d0af3.png)

开辟内存空间，填充shellcode之后修改该片内存的可执行属性

[![](https://p4.ssl.qhimg.com/t016aad306fe756fd4f.png)](https://p4.ssl.qhimg.com/t016aad306fe756fd4f.png)

解密多个C2循环请求

[![](https://p2.ssl.qhimg.com/t01339259b0e45cf6b8.png)](https://p2.ssl.qhimg.com/t01339259b0e45cf6b8.png)

关于CobaltStrike远控模块的详细分析，可以参考笔者之前的文章。

### <a class="reference-link" name="golang%E5%8A%A0%E8%BD%BDCS"></a>golang加载CS

087b3490d320adb9d719139dd521e934<br>
WeChat1.exe

原始样本由golang编写，样本运行后，首先将会解析并请求一个干净的地址：[http://www.shibor.org/shibor/web/DataService.jsp](http://www.shibor.org/shibor/web/DataService.jsp) 以判断网络是否连通：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0158fd3a967f14f23c.png)

循环请求该地址，直到请求成功才会跳转到后面执行：

[![](https://p1.ssl.qhimg.com/t019ab7ace17513d1e8.png)](https://p1.ssl.qhimg.com/t019ab7ace17513d1e8.png)

若请求成功，程序则会将预定义的base64字符串作为参数传递到main_build中，并且在该函数中解码加载该段base64字符串

[![](https://p2.ssl.qhimg.com/t01a2f052ab013a4c8a.png)](https://p2.ssl.qhimg.com/t01a2f052ab013a4c8a.png)

解码之后的shellcode由CobaltStrike生成，请求C2：www.microport.com

[![](https://p4.ssl.qhimg.com/t01b4cab00bfd5baad9.png)](https://p4.ssl.qhimg.com/t01b4cab00bfd5baad9.png)

[![](https://p2.ssl.qhimg.com/t019111500d5f01b320.png)](https://p2.ssl.qhimg.com/t019111500d5f01b320.png)

### <a class="reference-link" name="golang%E7%99%BD%E5%8A%A0%E9%BB%91"></a>golang白加黑

23aaa6e9c289f61737e12671c70a098a<br>
五一劳动节职工福利名单(1)(1).zip

一个比较经典的golang加载器，原始程序为压缩包，内含了一个exe文件和两个”jpg”文件，且在hvv一开始，就同时被传到了微步和vt，可以说是打响了hvv的第一枪。

[![](https://p3.ssl.qhimg.com/t01ec35a6a5e0fa81bd.png)](https://p3.ssl.qhimg.com/t01ec35a6a5e0fa81bd.png)

压缩包解压之后可见exe文件仿冒了WORD图标

[![](https://p3.ssl.qhimg.com/t0199ddf97191bff103.png)](https://p3.ssl.qhimg.com/t0199ddf97191bff103.png)

通过十六进制查看工具可知这里的两个jpg文件实则都是PE文件

[![](https://p4.ssl.qhimg.com/t017adab754e94452ee.png)](https://p4.ssl.qhimg.com/t017adab754e94452ee.png)

五一劳动节职工福利名单.exe运行之后，首先会判断 [c:/windows/tapi/crashreport.dll](/windows/tapi/crashreport.dll) 是否存在，若存在则说明已经感染，若不存在，则会分别将当前目录的name.jpg和name2.jpg拷贝为yyexternal.exe和crashreport.dll

[![](https://p1.ssl.qhimg.com/t01505c7ac4e1a8df62.png)](https://p1.ssl.qhimg.com/t01505c7ac4e1a8df62.png)

通过搜索引擎可知yyexternal.exe为YY客户端程序，这里很明显是一个白加黑的执行逻辑

[![](https://p4.ssl.qhimg.com/t01514a7806e2913ca6.png)](https://p4.ssl.qhimg.com/t01514a7806e2913ca6.png)

程序在将文件拷贝到tapi目录下并重命名之后，则会加载yyexternal.exe，由该程序去调用恶意dll

[![](https://p4.ssl.qhimg.com/t017aa882750609c81e.png)](https://p4.ssl.qhimg.com/t017aa882750609c81e.png)

在白exe加载该恶意dll时，会调用名为 InitBugReport 的导出函数：

[![](https://p0.ssl.qhimg.com/t01b9352bb16534c6f9.png)](https://p0.ssl.qhimg.com/t01b9352bb16534c6f9.png)

在InitBugReport函数中，首先会从byte_100277A8开始的地方，步长为4取值赋值给esi所指的内存，取出来的数据总长度为0x0f97

[![](https://p3.ssl.qhimg.com/t01ce74d1cafc82e307.png)](https://p3.ssl.qhimg.com/t01ce74d1cafc82e307.png)

将待解密的数据取出来之后，程序将会对前0x7cc的数据进行异或计算，然后开辟一个7cc的内存空间，将解密之后的shellcode拷贝过去，最后通过call eax的方式加载到shellcode中执行。

[![](https://p4.ssl.qhimg.com/t01b3e8baf66ffab1f3.png)](https://p4.ssl.qhimg.com/t01b3e8baf66ffab1f3.png)

调试器加载YY主程序，并直接对LoadLibrary设置断点，找到加载crashreport.dll的地方

[![](https://p2.ssl.qhimg.com/t011e4da94273e62397.png)](https://p2.ssl.qhimg.com/t011e4da94273e62397.png)

返回回来找到InitBugReport函数的入口点并F7进入

[![](https://p4.ssl.qhimg.com/t019093601019abde95.png)](https://p4.ssl.qhimg.com/t019093601019abde95.png)

成功解密shellcode，这里可以看出来是CobaltStrike的shellcode

[![](https://p3.ssl.qhimg.com/t017f71e4b2a3ec8ec6.png)](https://p3.ssl.qhimg.com/t017f71e4b2a3ec8ec6.png)

连接C2并尝试从C2下载后续cs远控组件实现对用户主机的完全控制。

[![](https://p3.ssl.qhimg.com/t01c40285673d610a08.png)](https://p3.ssl.qhimg.com/t01c40285673d610a08.png)

### <a class="reference-link" name="golang%E7%A1%AC%E7%BC%96%E7%A0%81"></a>golang硬编码

c54eb668cf76a37bf28f95c173770adf<br>
skylarinst-winc(10.199.1.19_80).exe

样本最早由4月2日上传到微步社区，应该属于hvv开始前的试探

[![](https://p0.ssl.qhimg.com/t019ee700debe26c0d3.png)](https://p0.ssl.qhimg.com/t019ee700debe26c0d3.png)

此样本依旧由golang编写，逻辑较为简单，在入口点，程序会将rdata段的部分数据拷贝过来，将其转换为byte之后再格式化为hex数据

[![](https://p5.ssl.qhimg.com/t018c668c25c8d4bac9.png)](https://p5.ssl.qhimg.com/t018c668c25c8d4bac9.png)

拷贝过去的数据其实就是cs payload的hex形式，攻击者将其编码为了字符串并存储在文件中以躲避检测

[![](https://p4.ssl.qhimg.com/t01a5c69be6e2e18ed2.png)](https://p4.ssl.qhimg.com/t01a5c69be6e2e18ed2.png)

直接将这部分数据拷贝出来解码即可到的完整的cs shellcode，并且在末尾看到C2：149.248.18.93

[![](https://p4.ssl.qhimg.com/t013ef8ec0bdc8a5bd7.png)](https://p4.ssl.qhimg.com/t013ef8ec0bdc8a5bd7.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012ab80b8b0b5c117b.png)

虽然该样本比较简单，但是根据微步的信息，可知样本最开始上传到VT的时候，报毒是很少的，不过各大厂商都比较给力，及时补充了查杀特征，笔者根据cs的加载方式，关联到了一个类似的恶意样本：131e4a3511e4e8e5f9436da4d45484d6，该样本最近才上传，但是VT查杀已经较多。

[![](https://p0.ssl.qhimg.com/t01bb889d62d107f0d4.png)](https://p0.ssl.qhimg.com/t01bb889d62d107f0d4.png)

不同的是，此样本用了cdn进行通信，暂时无法确定此类加载是统一框架生成还是同一个攻击者/队伍使用

[![](https://p4.ssl.qhimg.com/t01f1c3f934a5eeb4ab.png)](https://p4.ssl.qhimg.com/t01f1c3f934a5eeb4ab.png)
