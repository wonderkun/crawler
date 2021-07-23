> 原文链接: https://www.anquanke.com//post/id/106853 


# Operation GhostSecret：在全球范围内窃取数据的攻击活动


                                阅读量   
                                **85655**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t013cc0f5b9c0385fea.png)](https://p4.ssl.qhimg.com/t013cc0f5b9c0385fea.png)



## 一、前言

McAfee高级威胁研究（ATR）团队的分析人员最近发现了在全球范围内肆虐的一场数据窃取攻击活动，包括关键基础设施、娱乐、金融、医疗保健以及电信在内的许多行业受到影响。此次攻击活动名为Operation GhostSecret，用到了多个植入体（implant）、工具以及一些恶意软件变种（这些变种与具有国家背景的网络组织Hidden Cobra有关）。攻击所用的基础设施目前仍处于活跃状态。在本文中，我们深入分析了此次攻击活动。此外还有一篇简要版的分析文章，大家可以访问[此链接](https://securingtomorrow.mcafee.com/mcafee-labs/global-malware-campaign-pilfers-data-from-critical-infrastructure-entertainment-finance-health-care-and-other-industries)查看。

根据我们对此次攻击活动的调查结果，我们发现攻击者使用了多种恶意软件植入体，其中包括某款未知的植入体，其功能与Bankshot类似。从3月18日到26日，我们观察到这款恶意软件在全球的各个区域中出现过。这款新型变种与Destover恶意软件的部分代码类似，而后者曾在2014年针对Sony Pictures的攻击活动中使用过。

此外ATR团队还发现了Proxysvc，这是之前未曾分析过的一款植入体，还有其他一些控制服务器，这些服务器与这些新型植入体有关并且仍处于活跃状态。根据我们对已提交的公开、私密信息以及安全产品提供的感知信息的分析结果，我们发现Proxysvc似乎总是伴随着2017年的Destover变种一起使用，并且从2017年年中以来一直处于未被发现的状态。

隐藏在Operation GhostSecret背后的攻击者使用了与之前威胁活动中相似的基础设施，包括植入体中FakeTLS所使用的SSL证书（之前Destover后门变种Escad也发现过这个特征，该变种曾在Sony Pictures攻击事件中出现过）。根据我们的技术分析、感知数据以及提交的数据，我们有十足的把握认为此次事件正是Hidden Cobra组织的杰作。在2018年3月，ATR团队发现了与该组织有关的攻击活动，当时攻击者的目标是土耳其银行。发现的这些样本应该是Operation GhostSecret第一阶段所使用的载荷。如果大家想进一步了解此次威胁事件在全球各方面的影响，请参考此篇[文章](https://securingtomorrow.mcafee.com/mcafee-labs/global-malware-campaign-pilfers-data-from-critical-infrastructure-entertainment-finance-health-care-and-other-industries)。



## 二、整体分析

McAfee ATR团队发现了一款收集数据的未知植入体，该植入体的活动时间为2018年2月中旬。这款植入体貌似是Hidden Cobra专属植入体的衍生物，功能上与Bankshot类似，并且代码上与Hidden Cobra的其他植入体有所重叠。然而这款变种并没有基于Bankshot衍生而来。分析可执行文件的rich header数据后，我们发现这两款植入体使用了不同的开发环境编译而成（PE rich header是Windows可执行文件中未公开描述的部分，包含用来识别创建该程序所使用的Microsoft编译器以及连接器的唯一信息。这些数据可以用来识别不同恶意软件变种之间的相似性，确定是否使用相同的研发环境）。根据我们对代码以及PE rich header的分析，我们认为Bankshot、Proxysvc以及Destover之类的植入体属于不同的家族，但代码及功能上与Hidden Cobra的现有工具有所重叠。



[![](https://p5.ssl.qhimg.com/t012dd1987ef26939d0.png)](https://p5.ssl.qhimg.com/t012dd1987ef26939d0.png)

图1. 2018年Bankshot植入体的PE rich header数据



[![](https://p0.ssl.qhimg.com/t01b95763e651342760.png)](https://p0.ssl.qhimg.com/t01b95763e651342760.png)

图2. 2018年2月新款植入体的PE rich header数据



[![](https://p1.ssl.qhimg.com/t0152ee5e422b46cf53.png)](https://p1.ssl.qhimg.com/t0152ee5e422b46cf53.png)

图3. Proxysvc.dll的PE rich header数据



当我们将2018年2月最新款植入体的PE rich header数据与2014年 Sony Pictures攻击事件之前出现的Backdoor.Escad（Destover）进行对比时，我们发现两者的特征相同。Destover变种在代码上与2015年的变种有85%的相似度，并且与我们之前分析过的Backdoor.Escad 变种包含相同的rich PE header特征。因此这款新型植入体很有可能是Destover组件的衍生品。我们确认该植入体并不是之前已知的Destover样本的直接复制品，相反，应该时Hidden Cobra使用了早期版本中的功能创建了一款混合的新型变种。



[![](https://p0.ssl.qhimg.com/t017d5cf0c461b0b29b.png)](https://p0.ssl.qhimg.com/t017d5cf0c461b0b29b.png)

图4. 2014年的Backdoor.Escad（哈希值：8a7621dba2e88e32c02fe0889d2796a0c7cb5144）

[![](https://p5.ssl.qhimg.com/t01dd4c4d79c2a9cdb9.png)](https://p5.ssl.qhimg.com/t01dd4c4d79c2a9cdb9.png)

图5. 2015年的Destover变种（哈希值：`7fe373376e0357624a1d21cd803ce62aa86738b6`）



2月14日，美国境内某个未知源提交了2月份的变种（哈希值：`fe887fcab66d7d7f79f05e0266c0649f0114ba7c`），变种编译时间为2天之前。这款韩语文件所使用的控制服务器的IP地址为`203.131.222.83`。这款变种与2017年的未知样本（哈希值：`8f2918c721511536d8c72144eabaf685ddc21a35`）基本一致，除了控制服务器地址有所不同以外。2017年样本使用的地址为`14.140.116.172`。这两款植入体都使用了FakeTLS以及PolarSSL，我们也在之前的Hidden Cobra植入体中看到过。自Sony Pictures攻击事件以来，植入体中已经开始使用PolarSSL库，并且这个库也是Backdoor.Destover的专用库。该植入体中包含一个自定义的控制服务器协议，可以通过443端口发送数据。这款植入体并没有使用标准的SSL协议来格式化数据包，而是使用自定义的格式，通过SSL来传输数据（这也是FakeTLS的名字由来）。该植入体的控制服务器流量与Backdoor.Escad几乎相同。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a500f289703213b7.png)

图6. Backdoor.Destover（2018年Destover变种）中的TLS流量



[![](https://p0.ssl.qhimg.com/t01217d4b3d43284f8d.png)](https://p0.ssl.qhimg.com/t01217d4b3d43284f8d.png)

图7. Backdoor.Escad中的TLS流量



进一步分析`14.140.116.172`这个IP地址后，我们发现整个基础设施中还涉及其他一些隐藏的组件。Proxysvc.dll包含一系列硬编码的IP地址（前面这个地址也包含在内），这些IP的归属地都为印度。虽然起了这个名字，但该组件并不是一个SSL代理，而是一个比较特别的数据收集以及后门安装组件，在443端口上监听连入的控制服务器连接。

Proxysvc最早是由美国境内的公开源以及私密源于3月22日提交样本。该组件的可执行释放程序于3月19日在韩国提交。根据McAfee的感知数据显示，3月16日至21日Proxysvc组件已经在野外处于活跃状态。我们的研究表明监听器组件主要在高等教育组织中出现，怀疑该组件与核心控制服务器基础设施有关。攻击者之所以选择这些目标来运行Proxysvc，是想弄清楚哪些系统已被感染，以便后续进一步连接到这些系统上。这些数据表明相关基础设施在被人们发现以前已经持续运行了一年多时间。ATR团队发现该组件已经在11个国家的系统上运行过。由于Proxysvc的功能有限，貌似它属于SSL监听器隐蔽网络的一部分，攻击者可以通过该网络收集信息，安装更为复杂的植入体或者其他基础设施。SSL监听器支持多个控制服务器连接，而不单单使用硬编码的地址清单。由于该组件不需要依赖硬编码的地址，只接受入站连接，因此控制服务依然可以隐藏在人们的眼皮下。



[![](https://p3.ssl.qhimg.com/t01765c8b7a9ecd9b8f.png)](https://p3.ssl.qhimg.com/t01765c8b7a9ecd9b8f.png)

图8. 3月份Proxysvc.dll所感染的系统数（按国别分类），来源：McAfee ATR团队



在2018年3月14日至18日期间，Destover的植入体变种在17个国家的组织中出现过。受影响的组织主要集中在电信、健康、金融、关键基础设施以及娱乐等行业。



[![](https://p0.ssl.qhimg.com/t01af318cc0662676cc.png)](https://p0.ssl.qhimg.com/t01af318cc0662676cc.png)

图9. 3月份Destover变种所感染的系统数，按国别分类。来源：McAfee ATR团队



## 三、控制服务器

进一步调查控制服务器基础架构后，我们发现了一个SSL证书`d0cb9b2d4809575e1bc1f4657e0eb56f307c7a76`，该证书与`203.131.222.83`这个控制服务器相关，2018年2月的植入体中用到了这个服务器。该服务器位于泰国曼谷的Thammasat大学，这个大学之前还托管过Sony Pictures攻击事件中相关植入体曾使用过的控制服务器。从Sony Pictures攻击事件起Hidden Cobra组织就用过这个SSL证书。对这个证书进行分析后，我们发现了还有其他控制服务器使用同样的PolarSSL证书。从McAfee感知数据中我们发现仍然有多个IP地址处于活跃状态，其中两个与2018年的Destover植入体变种处于同一个网络中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0183ed8147ad684a44.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b4322ad27190ed71.png)

图10&amp;11. 2018年3月15日至19日，Thammasat大学托管的控制服务器所感染的主机数。来源：McAfee ATR团队



## 四、植入体溯源

McAfee ATR团队发现的Destover变种来源于2015开发的代码。根据PE中的rich header信息，我们发现这些代码在2017年以及2018年的变种中又再次出现，这些变种使用了几乎相同的功能，只是修改了某些命令，但开发环境相同。

这两款植入体（`fe887fcab66d7d7f79f05e0266c0649f0114ba7c`以及`8f2918c721511536d8c72144eabaf685ddc21a35`）都是基于2015年的代码来开发。我们将2015年8月8日的植入体（`7fe373376e0357624a1d21cd803ce62aa86738b6`）与2018年的植入体对比，发现两者有83%的相似性。关键的几个异同点如下所述。



### <a class="reference-link" name="%E7%9B%B8%E4%BC%BC%E6%80%A7"></a>相似性

1、两款变种都使用`GetProcAddress`来动态导入API，包括使用`wtsapi32.dll`来收集所有活动的远程会话的用户及域名。

2、两款变种都包含各种功能，由控制服务器发送的命令ID来确定具体使用哪种功能。

3、两款恶意软件都包含相同的功能，具体如下：
- 列出目录中的文件
- 创建任意进程
- 将控制服务器返回的数据写入磁盘上的文件
- 收集所有驱动器的信息
- 收集所有进程的进程时间信息
- 将某个文件的内容发送给控制服务器
- 擦除并删除磁盘上的文件
- 设置植入体当前的工作目录
- 将磁盘空间信息发送给控制服务器
4、两款变种都使用批处理脚本从系统中删除自身对应的二进制文件

5、两款变种都可以在系统上运行命令，将结果输出到某个临时文件，然后将该文件的内容发送给控制服务器。



### <a class="reference-link" name="%E5%8C%BA%E5%88%AB%E7%82%B9"></a>区别点

2018年的变种并不包含2015年变种所具备的部分功能，具体如下：

1、以特定用户身份创建进程。

2、结束某个进程。

3、删除某个文件。

4、设置某个文件的时间属性。

5、获取当前的系统时间，将其发送给控制服务器。

6、读取磁盘上某个文件的内容。如果指定的文件路径为某个目录，则列出目录的内容。

7、设置文件的属性。

2015年的植入体并不包含需要连接的硬编码的IP地址，相反，该变种包含一个硬编码的`sockaddr_in`数据结构（偏移地址为二进制尾部前0x270字节处），与`connect()`配合使用，结构体的端口为443，IP地址为控制服务器所在的地址，如下所示：

```
193.248.247.59
196.4.67.45
```

这两个控制服务器都使用了PolarSSL证书`d0cb9b2d4809575e1bc1f4657e0eb56f307c7a76`。



## 五、Proxysvc

作为一款SSL监听器，Proxysvc乍看之下像是一款代理设置工具（以便在中间人攻击中劫持流量）。然而仔细分析这个样本后，我们发现它其实是一种植入体，使用基于SSL的HTTP协议来接收控制服务器返回的命令。

Proxysvc似乎充当了下载器角色，其主要功能是在不泄露攻击者控制服务器地址的前提下，向端点传播其他攻击载荷。该植入体包含一部分功能，可以进一步侦察或者安装后续载荷。虽然该植入体是一个服务形态的DLL，但也能以独立的进程形态来运行。



[![](https://p0.ssl.qhimg.com/t01030b4ef7dbfc2f55.png)](https://p0.ssl.qhimg.com/t01030b4ef7dbfc2f55.png)

图12. Proxysvc的`ServiceMain()`子函数



该植入体无法连接到控制服务器所在的IP地址或者URL地址，相反它只能接受来自控制服务器返回的命令。植入体绑定了443端口，在该端口上监听所有的连入请求。

[![](https://p2.ssl.qhimg.com/t014f68c7ef1b8b7cf2.png)](https://p2.ssl.qhimg.com/t014f68c7ef1b8b7cf2.png)

[![](https://p0.ssl.qhimg.com/t01b4c2dd08f845ac6c.png)](https://p0.ssl.qhimg.com/t01b4c2dd08f845ac6c.png)

图13&amp;14. Proxysvc绑定到特定端口



[![](https://p5.ssl.qhimg.com/t01130f68ce65b664e0.png)](https://p5.ssl.qhimg.com/t01130f68ce65b664e0.png)

图15. Proxysvc开始接受连接请求



在接受连接请求时，Proxysvc对控制服务器身份的检查过程比较有趣。它会将对方地址与一系列IP地址进行对比，确保如下地址没有发起连接请求。如果连接请求来自于如下地址，则Proxysvc会返回一个0响应（即ASCII字符“0”），然后关闭连接。

```
121.240.155.74
121.240.155.76
121.240.155.77
121.240.155.78
223.30.98.169
223.30.98.170
14.140.116.172
```



### **SSL监听器功能**

植入体接受控制服务器返回的基于HTTP协议的命令，解析HTTP头部中的Content-Type以及Content-Length 字段。如果HTTP Content-Type与下图中的值匹配，植入体就会执行控制服务器指定的命令：

```
Content-Type: 8U7y3Ju387mVp49A
```

[![](https://p5.ssl.qhimg.com/t01814b3e940f2db9fa.png)](https://p5.ssl.qhimg.com/t01814b3e940f2db9fa.png)

图16. 将HTTP Content-Type与某个值进行对比



**该植入体具备如下功能：**

1、将控制服务器返回的可执行文件写入某个临时文件中并加以执行。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010471971543982a45.png)

图17. Proxysvc将某个二进制文件写入临时目录中并加以执行



2、收集系统信息并将信息发送给控制服务器。所收集的系统信息包括如下内容：
- 端点的MAC地址
- 计算机名
- 从`HKLMSoftwareMicrosoftWindows NTCurrentVersion ProductName`注册表项所提取的产品名
- 将以上信息拼接成一个字符串，字符串格式为`MAC_Address|ComputerName|ProductName`，然后将该信息发送给控制服务器
3、使用当前系统时间戳，将控制服务器返回的HTTP请求保存到植入体所在目录的prx临时文件中。



## 六、主植入体分析

2018年2月的植入体包含各种功能，包括获取数据以及在受害者系统上执行任意执行。由于该植入体可以从控制服务器那接受非常多的命令结构，因此这是一个用于数据侦察以及提取的通用型框架，可以用于更高级的场景。比如，该植入体可以擦除并删除文件、执行其他植入体、从文件中读取数据等等。

植入体首先会动态加载API，以便执行恶意操作。所导入的库列表如下所示：

```
Kernel32.dll
Apvapi32.dll
Oleaut32.dll
Iphlpapi.dll
Ws2_32.dll
Wtsapi32.dll
Userenv.dll
Ntdll.dll
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0174de293514432d58.png)

图18. 主植入体动态加载API



在初始化阶段，植入体会收集基本的系统信息，通过443端口使用SSL协议将这些信息发送给硬编码的控制服务器（地址为`203.131.222.83`），这些信息包括：

1、系统区域设置中的国家/地区名称；

2、操作系统版本；

3、从`HKLMHARDWAREDESCRIPTIONSystemCentralProcessor ProcessorNameString`注册表中提取的处理器描述信息；

4、计算机名以及网络适配器信息；

5、从`C:`到`Z:`的磁盘驱动器空间信息，包括磁盘空间总量（按字节计算）以及可用的空间（按字节计算）等；

6、当前内存状态，包括物理内存总量（按字节计算）以及总的可用内存等；

7、基于当前远程会话所得到的域名以及用户名。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ffc39be4efdc5dc6.png)

图19. 使用Win32 WTS API获取域名以及用户名



### **数据侦察**

植入体通过SSL协议接受服务器返回的经过编码的命令。这些数据会被植入体解码然后提取正确的命令ID。正确的命令ID范围在0到0x1D之间。

[![](https://p0.ssl.qhimg.com/t012ea50d0a2a947152.png)](https://p0.ssl.qhimg.com/t012ea50d0a2a947152.png)

图20. 根据命令ID值跳转至正确的命令执行分支

根据收到的命令ID值，植入体可以执行如下操作：

1、收集系统信息，传递给控制服务器（与前面提到的基础信息收集功能相同）。

2、获取系统中所有驱动器的磁盘卷信息（从`A:`到`Z:`），传递给控制服务器。



[![](https://p5.ssl.qhimg.com/t012d93035147d419d8.png)](https://p5.ssl.qhimg.com/t012d93035147d419d8.png)

图21. 收集磁盘卷信息



3、列出某个目录中的文件。目录路径由控制服务器指定。

4、读取某个文件的内容，将其发送给控制服务器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0165170caeb3d5118f.png)

图22. 读取文件内容并将其发送给控制服务器



5、将控制服务器返回的数据写入指定的文件路径中。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0119839ef2dba6642a.png)

图23. 以0标志（不共享）打开文件句柄以便写入文件



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016f611949d7e0f155.png)

图24. 将控制服务器返回的数据写入文件



6、 根据控制服务器指定的文件路径创建新的进程。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01586bc62f43d3e649.png)

图25. 根据控制服务器指定的二进制路径创建新的进程



7、擦除并删除由控制服务器指定的文件。



[![](https://p3.ssl.qhimg.com/t01a84e14d7cccbba7f.png)](https://p3.ssl.qhimg.com/t01a84e14d7cccbba7f.png)

图26. 擦除并删除文件



使用`cmd.exe`执行系统上的某个二进制程序，将结果保存到某个临时文件中，然后读取该文件，将结果发送给控制服务器。所使用的命令行参数为：

```
cmd.exe /c “&lt;file_path&gt; &gt; %temp%PM*.tmp 2&gt;&amp;1”
```



[![](https://p2.ssl.qhimg.com/t010001d28bb976cb92.png)](https://p2.ssl.qhimg.com/t010001d28bb976cb92.png)

图27. 执行命令并将结果保存到临时文件中



8、获取当前运行的所有进程的信息。

[![](https://p2.ssl.qhimg.com/t01f81776f81c888fb1.png)](https://p2.ssl.qhimg.com/t01f81776f81c888fb1.png)

图28. 获取系统上所有进程的进程时间



[![](https://p5.ssl.qhimg.com/t01b06e9aa8c4b2fa40.png)](https://p5.ssl.qhimg.com/t01b06e9aa8c4b2fa40.png)

图29. 获取某个进程所对应的用户名以及域名



9、使用批处理文件实现自删除。



[![](https://p5.ssl.qhimg.com/t0127879a33681c107a.png)](https://p5.ssl.qhimg.com/t0127879a33681c107a.png)

图30. 创建批处理文件自删除



10、接收控制服务器返回的数据并保存为注册表项，注册表路径为：

```
HKLMSoftwareMicrosoftWindowsCurrentVersionTowConfigs Description
```

11、设置并获取植入体的当前工作目录。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fceb9e21af8ab500.png)

图31. 设置并获取植入体进程的当前工作目录



在植入体中，每个命令所对应的处理函数索引表如下所示：



[![](https://p0.ssl.qhimg.com/t0196124137bb6f10c8.png)](https://p0.ssl.qhimg.com/t0196124137bb6f10c8.png)

图32. 命令处理函数索引表



## 七、总结

根据分析结果，McAfee ATR团队发现了之前未发现过的一些组件，我们认为这些组件与Hidden Cobra密切相关，该组织一直并继续以全世界各地的组织为攻击目标。这些数据收集植入体的复杂程度越来越高，表明攻击者具备先进的攻击能力并一直在持续开发工具。我们调查后还发现与最近攻击活动有关的未知基础架构，这些攻击活动的服务器位于印度境内，使用了先进的植入体来创建隐蔽型网络，以收集数据并发起后续攻击。

随着调查的进一步深入，McAfee ATR团队会继续提供后续研究成果。

打击网络犯罪需要全世界范围内公共及私人部门的努力及合作。McAfee正与泰国政府当局合作，取缔Operation GhostSecret控制服务器基础设施，同时保留涉事系统以供执法机构进一步分析。通过与全球执法机构建立并维护合作伙伴关系，McAfee将与各位共同进步并不断成长。



## 八、IoC

McAfee将这款植入体标识为`Trojan-Bankshot2`。

相关IP地址为：

```
203.131.222.83
14.140.116.172
203.131.222.109
```

样本哈希值为：

```
fe887fcab66d7d7f79f05e0266c0649f0114ba7c
8f2918c721511536d8c72144eabaf685ddc21a35
33ffbc8d6850794fa3b7bccb7b1aa1289e6eaa45
```

[原文链接：https://securingtomorrow.mcafee.com/mcafee-labs/analyzing-operation-ghostsecrt-attack-seeks-to-steal-data-worldwide](https://securingtomorrow.mcafee.com/mcafee-labs/analyzing-operation-ghostsecret-attack-seeks-to-steal-data-worldwide)
