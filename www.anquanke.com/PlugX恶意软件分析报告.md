> 原文链接: https://www.anquanke.com//post/id/98166 


# PlugX恶意软件分析报告


                                阅读量   
                                **143081**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者LUIS ROCHA，文章来源：countuponsecurity.com/
                                <br>原文地址：[ https://countuponsecurity.com/2018/02/04/malware-analysis-plugx/](https://countuponsecurity.com/2018/02/04/malware-analysis-plugx/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01ae87aaa697f0b9b4.png)](https://p4.ssl.qhimg.com/t01ae87aaa697f0b9b4.png)



## 写在前面的话

PlugX恶意软件家族一直都让我非常感兴趣，因此我打算在这篇文章中对其中的一个变种版本进行分析。我在网上搜索相关研究报告的时候，偶然间发现了Fabien Perigaud的研究，并从中了解到了一个老版本的PlugX构建器。接下来，我便搭建了实验环境，并对PlugX攻击活动进行了深入分析。<br>
在这篇文章中，我将跟大家简单介绍一下关于这个PlugX Builder（构建器）的概况，并对恶意软件的安装过程以及C2流量进行分析和研究。



## PlugX介绍

现在有很多网络犯罪组织都会在其有针对性的攻击活动中使用PlugX，很多人也将其称之为KORPLUG、SOGU或DestroyRAT，它是一种模块化的后门，而它则需要依靠那些已签名的合法可执行程序去加载恶意代码来实现运行。PlugX一般由三大组件构成：一个DLL文件、一个加密过的二进制文件和一个已签名的合法可执行程序（使用DLL搜索顺序劫持技术来加载恶意软件）。接下来，我们先看看PlugX构建器的大致情况。<br>
我们所得到的Builder样本为英文版本（MD5： 6aad032a084de893b0e8184c17f0376a），代码日期为2013年8月份，其中包含了功能丰富的模块化指令以及控制接口，可支持的恶意操作如下：
1. 构建Payload，配置攻击并设置受感染主机所要进行的操作，与控制服务器进行通信；
1. 代理连接，构建C2通信模块；
1. 设置持久化感染以及相关属性；
1. 设置一个需要注入Payload的进程（或多个）；
1. 为C2回调定义计划任务；
1. 启用键盘记录以及屏幕截图功能；
<li>管理所有的受感染系统；<br>
针对每一台被感染的系统，攻击者可以利用多种方式来与系统进行交互并实现远程控制，其中涉及到下列功能模块：</li>
1. 磁盘模块，允许攻击者写入、读取、上传、下载和执行文件；
1. 网络浏览器模块，允许攻击者浏览网络通信流量并通过SMB连接到网络内的其他系统；
1. 进程模块，可用于枚举、终止和加载进程；
1. 服务模块，允许攻击者枚举、启动、停止或修改系统服务；
1. 注册表模块，允许攻击者浏览注册表，并创建、删除和修改注册表键；
1. Netstat模块，允许攻击者枚举TCp和UDP网络连接以及相关进程；
1. 截图模块，允许攻击者进行屏幕截图；
1. 控制插件，允许攻击者查看或移除对受感染主机的控制；
1. Shell模块，允许攻击者拿到受感染系统的命令行Shell；
1. PortMap模块，允许攻击者建立端口转发规则；
1. SQL模块，允许攻击者连接SQL服务器并执行SQL语句；
1. 选项模块，允许攻击者关闭、重启、锁定或注销受感染设备；
键盘记录模块，可获取每一个进程的键盘按键数据；<br>
下图显示的是Plug-X的C2接口：<br>[![](https://p0.ssl.qhimg.com/t0114b5d978c1491960.png)](https://p0.ssl.qhimg.com/t0114b5d978c1491960.png)<br>
这样一来，我们就可以利用Builder的功能来定义不同的C2命令、控制密码、IP地址、安装属性和注入代码等等，并构建我们自己的Payload。这个版本Builder(LZ 2013-8-18)所生成的PlugX代码是一种自提取的RAR文档，其中包含了三份文件，运行自提取RAR文档之后将会选择性地在目录中存放这三份文件。我们的测试场景中，目录为“%AUTO%/RasTls”，文件分别为：一个来自卡巴斯基反病毒解决方案的已签名合法可执行程序，文件名为“avp.exe”（MD5：e26d04cecd6c7c71cfbb3f335875bc31），其功能是实现DLL搜索顺序劫持。当“avp.exe”运行时将会加载第二个文件-“ushata.dll”（MD5：728fe666b673c781f5a018490a7a412a），这是PlugX构建器制作的一个DLL，而这个文件将会加载第三个文件-“ushata.DLL.818”（MD5 ：21078990300b4cdb6149dbd95dff146f），该文件包含了经过混淆处理和封装的Shellcode。<br>[![](https://p5.ssl.qhimg.com/t016216cff7ba886009.png)](https://p5.ssl.qhimg.com/t016216cff7ba886009.png)<br>
其中，DLL搜索顺序劫持使用的API为Kernel32.LoadLibrary：<br>[![](https://p3.ssl.qhimg.com/t010be79dd6f54aa17d.png)](https://p3.ssl.qhimg.com/t010be79dd6f54aa17d.png)<br>
“ushata.dll”为DLL入口点，其中包含的代码负责验证目标系统日期是否大于或等于20130808，如果条件符合，它将会把恶意内容注入到内存中（调用“ushata.DLL.818”），并使用Kernel32.VirtualProtect API来修改内存地址分段权限（RWX），其中“ushata.DLL.818”文件中包含了经过混淆处理的Shellcode，下图显示的是部分Shellcode：<br>[![](https://p5.ssl.qhimg.com/t014da77fc21c3c90c7.png)](https://p5.ssl.qhimg.com/t014da77fc21c3c90c7.png)<br>
Shellcode会使用一种自定义的算法来进行解封装，下图显示的是解封装后的Shellcode：<br>[![](https://p3.ssl.qhimg.com/t01e9a1df15ccccaf36.png)](https://p3.ssl.qhimg.com/t01e9a1df15ccccaf36.png)<br>
Shellcode首先会通过访问线程信息块（TIB）来定位kernel32.dll的地址，而TIB中包含了指向进程环境块（PEB）结构体的指针。下图显示的是部分用于搜索kernel32.dll的Shellcode代码段：<br>[![](https://p0.ssl.qhimg.com/t012c4934cb7a752e8c.png)](https://p0.ssl.qhimg.com/t012c4934cb7a752e8c.png)<br>
搜索到kernel32.dll之后，代码会读取它的输出表，并定位相应的Windows API。接下来，Shellcode会使用LZNT1算法（利用ntdll.dll.RtlDecompressBuffer API）向内存中解压一个DLL（偏移量0x784，MD5为333e2767c8e575fbbb1c47147b9f9643）。这个DLL文件中包含的PE头替换成了“XV“值，而存储在PE头签名中的信息可以帮助我们恢复出恶意DLL：<br>[![](https://p1.ssl.qhimg.com/t01d3b7113c109a8c17.png)](https://p1.ssl.qhimg.com/t01d3b7113c109a8c17.png)<br>
接下来，Payload将会开始执行各种不同的操作以实现持久化感染。在Windows 7以及更高版本的Windows平台中，PlugX会创建一个名叫“%ProgramData%RasTl”的目录，其中“RasTl”是构建器中设置的安装名称。接下来，它会使用SetFileAttributesW API来将文件夹属性修改为“SYSTEM|HIDDEN”，然后将之前提到的那三个组件拷贝到这个目录中，并将所有的文件属性修改为“SYSTEM|HIDDEN”。<br>[![](https://p3.ssl.qhimg.com/t017fd15912e1b6b583.png)](https://p3.ssl.qhimg.com/t017fd15912e1b6b583.png)<br>
Payload还会修改已创建目录和文件的时间戳，修改的源数据需要使用SetFileTime API从ntdll.dll中获取。<br>[![](https://p4.ssl.qhimg.com/t01bd5509e21f6d3607.png)](https://p4.ssl.qhimg.com/t01bd5509e21f6d3607.png)<br>
它还会创建一个名叫“RasTl”的服务，其中的ImagePath指向的是“%ProgramData%RasTlavp.exe”。<br>[![](https://p0.ssl.qhimg.com/t017d1e4f1ad4869c96.png)](https://p0.ssl.qhimg.com/t017d1e4f1ad4869c96.png)<br>
如果恶意软件无法启动刚刚安装的服务，它会删除该服务并在注册表中实现持久化感染机制（通过RegSetValueExW API将注册表键“HKLMSOFTWAREClassesSOFTWAREMicrosoftWindowsCurrentVersionRunRasTls”的值修改为“C:ProgramDataRasTlsavp.exe”）。<br>[![](https://p5.ssl.qhimg.com/t01f00c1eca50622483.png)](https://p5.ssl.qhimg.com/t01f00c1eca50622483.png)<br>
如果Builder选项开启了键盘记录功能，它将会创建一个文件（文件名随机，例如“%ProgramData%RasTlrjowfhxnzmdknsixtx”）来存储键盘按键信息。如果Payload带有屏幕截图功能的话，它还会创建一个名叫“%ProgramData%RasTl RasTlScreen”的文件夹来存储JPG截图文件，文件格式为”&lt;datetime&gt;.jpg”。Payload还会创建文件“%ProgramData%DEBUG.LOG”来存储恶意软件在安装和执行过程中的输出以及调试信息（使用了OutputDebugString API）。



## 恶意软件的运行

为了完成自己的目标，恶意代码首先会创建一个新的“svchost.exe”实例，然后向svchost.exe进程地址空间中注入恶意代码（使用进程Hollowing技术）。下图显示的是进程Hollowing技术的第一个阶段，其中Payload以“挂起”状态创建了一个新的“svchost.exe”实例。<br>[![](https://p4.ssl.qhimg.com/t01d1f0ab44c3b2e9bc.png)](https://p4.ssl.qhimg.com/t01d1f0ab44c3b2e9bc.png)<br>
然后使用WriteProcessMemory API来注入恶意Payload：<br>[![](https://p3.ssl.qhimg.com/t01875bad4788342efa.png)](https://p3.ssl.qhimg.com/t01875bad4788342efa.png)<br>
现在主进程仍然处于挂起状态，但是之后它会调用SetThreadContext API来改变其状态，并最终调用ResumeThread API来执行恶意代码。除此之外，如果又需要的话这个恶意软件还能够绕过用户账户控制（UAC）。<br>
接下来，我们还要弄清楚整个过程中恶意软件所采用的配置信息。为了导出配置数据，我们需要使用Immunity Debugger和一个Python API。这里我们需要将“plugx_dumper.py”文件复制到Immunity Debugger安装路径下的“PyCommands”文件夹中，然后把调试器挂接到受感染进程（例如“svchost.exe”）并运行插件。接下来，插件便会导出配置信息并提取出解压后的DLL。<br>[![](https://p5.ssl.qhimg.com/t01c1d576396bccd870.png)](https://p5.ssl.qhimg.com/t01c1d576396bccd870.png)<br>
我们可以看到，这个解析器能够寻找到注入的Shellcode，通过解码配置信息之后，我们能够导出攻击者所注入的DLL文件，而其中则包含了恶意软件的核心功能代码。<br>
接下来我们分析一下恶意软件的网络流量数据。我们通过分析发现，PlugX控制器使用了多种网络协议。网络流量中包含一个16字节长度的Header，随后跟着的便是Payload。Header采用了自定义程序进行编码，而Payload的编码和压缩使用的是LZNT1.下图显示的是反编译后的自定义编码程序：<br>[![](https://p4.ssl.qhimg.com/t01fdd40147d5da37d9.png)](https://p4.ssl.qhimg.com/t01fdd40147d5da37d9.png)<br>
在下图中，左手边显示的是编码和压缩前的数据包，右手边是编码和压缩后的数据包，大家可以对比一下：<br>[![](https://p3.ssl.qhimg.com/t01862cada5975bbe91.png)](https://p3.ssl.qhimg.com/t01862cada5975bbe91.png)<br>
接下来，恶意软件会使用WSASend API来发送流量数据：<br>[![](https://p0.ssl.qhimg.com/t010abd4433eb3736c1.png)](https://p0.ssl.qhimg.com/t010abd4433eb3736c1.png)<br>
捕捉到流量数据之后，我们可以观察到相同的数据：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c3bcc376e2bf0ac8.png)<br>
在控制器端，当数据包到达之后，Header将会被解码，随后便会对Payload进行解码和解压缩。最终的输出结果如下图所示：<br>[![](https://p4.ssl.qhimg.com/t011611658df66212a2.png)](https://p4.ssl.qhimg.com/t011611658df66212a2.png)<br>
下图显示的是我们所捕捉到的其中一个数据包，我们使用了一个小型的Python脚本来对其进行解密：<br>[![](https://p0.ssl.qhimg.com/t01256a38eda79f839a.png)](https://p0.ssl.qhimg.com/t01256a38eda79f839a.png)



## 总结

在这篇文章中，我们对PlugX的功能进行了简单分析，并研究了它的攻击和感染机制、经过混淆处理的Shellcode、持久化机制以及它所使用的进程Hollowing技术。接下来，我们还对恶意软件跟C2服务器的通信方式以及网络流量数据进行了研究。希望本文的研究内容可以给大家平时在分析恶意软件的时候提供帮助。



## 参考资料
1. [http://circl.lu/assets/files/tr-12/tr-12-circl-plugx-analysis-v1.pdf](http://circl.lu/assets/files/tr-12/tr-12-circl-plugx-analysis-v1.pdf)
1. [https://www.pwc.co.uk/cyber-security/pdf/cloud-hopper-annex-b-final.pdf](https://www.pwc.co.uk/cyber-security/pdf/cloud-hopper-annex-b-final.pdf)
1. [https://info.contextis.com/acton/attachment/24535/f-030c/1/-/-/-/-/PlugX%20-%20Payload%20Extraction.pdf](https://info.contextis.com/acton/attachment/24535/f-030c/1/-/-/-/-/PlugX%20-%20Payload%20Extraction.pdf)
1. [http://tracker.h3x.eu/info/290](http://tracker.h3x.eu/info/290)