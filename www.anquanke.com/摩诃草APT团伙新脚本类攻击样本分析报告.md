> 原文链接: https://www.anquanke.com//post/id/93307 


# 摩诃草APT团伙新脚本类攻击样本分析报告


                                阅读量   
                                **122144**
                            
                        |
                        
                                                                                    



> “摩诃草”组织，又称Hangover、Viceroy Tiger、Patchwork、Dropping Elephant、MONSOON，国内其他安全厂商也称其为白象、丰收行动。
该组织是一个以长期针对中国、巴基斯坦及其他部分南亚国家从事网络间谍活动的APT组织。从2013年5月16日由国外安全厂商Norman首次曝光以来，该组织的网络攻击活动异常的活跃，并被国内外不少安全厂商相继发现其攻击事件和使用的恶意代码。
360公司也曾在2016年8月4日发布了《摩诃草组织（APT-C-09）来自南亚的定向攻击威胁》一文<sup>【1】</sup>，详细介绍了该组织发起的历史4次攻击行动，并对其历史使用的攻击工具和基础设施的关联性进行比较和总结。
“摩诃草”组织主要针对我国的政府机构、科研教育领域以及军事领域的目标人员进行攻击，其主要使用鱼叉攻击，也使用基于即时通讯工具和社交网络作为恶意代码的投递途径。其攻击使用的恶意代码主要针对Windows系统，历史也出现过针对其他平台的恶意代码。
360威胁情报中心在近期对“摩诃草”组织的攻击活动监测过程中，发现其投入使用的新的攻击样本，我们决定发布此篇子分析报告，揭露该组织最新的攻击技术细节。



## 背景概述

“摩诃草”组织的攻击活动从2013年5月16日首次曝光以来，其历史的攻击行动及使用的攻击工具和资源也被国内外安全厂商多次揭露，但从360威胁情报中心对该组织的持续监测显示，该组织的攻击行动从未停止，并持续保持着一个比较高的频度活跃。

自我们上一次公开发布“摩诃草”组织的完整分析报告，已经过去了一年多，我们发现该组织在过去一年依然延续了过去的一些攻击模式，但使用的攻击工具和恶意代码还是出现了一些显著变化。

我们发现，“摩诃草”组织最近发起了一次可能是针对东欧部分国家的攻击事件，并使用了其新制作的一些基于脚本的攻击恶意代码文件，和过去常见的采用诱导漏洞文档类的攻击载荷手法出现了一些明显变化，并且已经有部分乌克兰用户遭受此类攻击并被植入远控木马。

目前我们尚不能确定该攻击事件背后的攻击动机，但为了预防该组织在未来的攻击行动中进一步大规模使用该类攻击恶意代码，我们决定披露其部分技术细节并预警，以便能更好的防御其未来使用该类攻击技术。

下面我们将重点分析“摩诃草”组织最新的脚本类攻击恶意代码技术。

## 基于脚本的攻击载荷投放

在“摩诃草”组织最新制作的攻击恶意代码中，我们发现其主体模块使用JS和PowerShell脚本进行编写，并利用多次解密、拼接来释放和加载下一阶段的攻击载荷。

下图为该恶意代码的结构和执行流程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0125e6b8385d4b68c0.jpg)

### <a name="_Toc502736859"></a>Dropper JS – dog.js

Dropper JS是一个96KB的脚本，其会释放一个中间JS脚本。其前面部分为hex形式的附加数据被作为注释语句存放；后面的脚本会先获取当前正在执行脚本的路径，并读取自身文件数据，找到前面注释的附加数据拼接起来，转换成二进制形式，保存到”%temp%\laksasokpaslkak.js”，最后通过WScript容器执行这个脚本。

[![](https://p5.ssl.qhimg.com/t013a36e667443fad3a.png)](https://p5.ssl.qhimg.com/t013a36e667443fad3a.png)

### <a name="_Toc502736860"></a>中间JS脚本 – laksasokpaslkak.js

该脚本会首先判断目标主机是否存在卡巴和NOD32程序，如果存在则脚本退出；如果不存在，会把脚本里的“dllData”和“code”两个数据一起写入到一个PowerShell脚本文件中，其名字为随机生成的5个字节。最后执行该PowerShell脚本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01367779e22bcb5c70.png)

### <a name="_Toc502736861"></a>随机名称PowerShell脚本

该PowerShell脚本以数组形式乱序放置Base64编码的数据，通过Base64解码并解压成PowerShell脚本后，采用了一种Bypass UAC的形式来执行该脚本。其使用的Bypass UAC技术在另一个APT组织“海莲花”的攻击工具中也曾使用<sup>【2】</sup>。其通过修改注册表键值劫持eventvwr.exe，调用SC命令创建一个服务，并指向解密后的PowerShell脚本。

[![](https://p4.ssl.qhimg.com/t019b1866d3e727db1a.png)](https://p4.ssl.qhimg.com/t019b1866d3e727db1a.png)

[![](https://p2.ssl.qhimg.com/t0181a601c82050dba9.png)](https://p2.ssl.qhimg.com/t0181a601c82050dba9.png)

### <a name="_Toc502736862"></a>PowerShell Loader

PowerShell Loader脚本也是随机生成的名字，其主要功能是加载主体远控模块。

该脚本从内存中加载payload，如下为加载代码流程：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0162bff21650b7f7f8.png)

其中“strexp”保存的为远控模块的文件数据，经过base64decode解码得到原始文件内容为一个DLL文件，其导出模块名为socksbot.dll。最后使用ReflectiveLoader技术加载。

通过对加载的部分代码分析，我们推测其可能参考了开源的代码实现<sup>【3】</sup>，并添加了在64位Windows系统下的兼容性代码。

## 远控模块分析

### <a name="_Toc502736864"></a>加载入口 – ReflectiveLoader

该函数首先获取当前函数的地址，然后往前搜索PE头部“MZ”标志以定位该DLL模块的基地址。

[![](https://p1.ssl.qhimg.com/t01a75311f5422cfc04.png)](https://p1.ssl.qhimg.com/t01a75311f5422cfc04.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01660530a575546661.png)

通过hash获取3个函数LoadLibrary、GetProcAddr、VirtualAlloc的地址。

[![](https://p3.ssl.qhimg.com/t01bbfd0e0fbbeda889.png)](https://p3.ssl.qhimg.com/t01bbfd0e0fbbeda889.png)

然后调用VirtualAlloc分配一片内存空间。

[![](https://p4.ssl.qhimg.com/t019c31d15de5842dc0.png)](https://p4.ssl.qhimg.com/t019c31d15de5842dc0.png)

把该DLL模块复制到新申请的内存中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e6f71725699a3ea0.png)

然后执行DllMain。

[![](https://p3.ssl.qhimg.com/t01304ab074e0bd7090.png)](https://p3.ssl.qhimg.com/t01304ab074e0bd7090.png)

### <a name="_Toc502736865"></a>执行入口 – DllMain

DllMain会首先获取一些硬件信息计算出机器码。机器码是根据驱动器信息、电脑名和用户名算出来的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015d0dab0405598496.png)

然后会获取GetProcAddress和LoadLibraryA的地址，并把sub_1000234A代码通过复写进程的方式注入svchost.exe宿主中，如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d22c73611eab983f.png)

[![](https://p1.ssl.qhimg.com/t018baf7ec2cd1f831b.png)](https://p1.ssl.qhimg.com/t018baf7ec2cd1f831b.png)

注入后的代码会初始化网络套接字，发送一次touch包，然后创建一个主线程函数，如下：

[![](https://p0.ssl.qhimg.com/t013f555856315b7b70.png)](https://p0.ssl.qhimg.com/t013f555856315b7b70.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017e5db2e54b61bbdb.png)

在主线程中会连接C&amp;C服务器地址5.8.88.64:80。

[![](https://p5.ssl.qhimg.com/t013bf5a442de7a8d60.png)](https://p5.ssl.qhimg.com/t013bf5a442de7a8d60.png)

### <a name="_Toc502736866"></a>控制协议

这里我们详细分析该远控模块使用的控制通信协议，其基于HTTP协议实现控制通信。
1. **touch包**
远控模块会发送touch数据包，其会根据机器码生成对应的php路径用作HTTP访问的请求路径，其将机器码和随机生成的密钥加密并附上密钥信息。

[![](https://p2.ssl.qhimg.com/t01c740a3857eaa37ef.png)](https://p2.ssl.qhimg.com/t01c740a3857eaa37ef.png)

[![](https://p4.ssl.qhimg.com/t01be48e143b887712e.png)](https://p4.ssl.qhimg.com/t01be48e143b887712e.png)

其具体算法实现如下：

计算后生成的机器码字符串是放到HTTP数据包的GET数据里，例如生成的字符串为j2ylvj50suxr8vzss17s3.php，那么加密后的机器码数据为j2ylvj50suxr8vzss17s3。其前16字节是机器码加密后的数据，从16字节开始到末尾是随机生成的密钥信息，密钥长度在5-16字节随机，数值的范围在0-35随机，然后通过编码成可见字符。

[![](https://p3.ssl.qhimg.com/t013d8ed2271c08ec5e.png)](https://p3.ssl.qhimg.com/t013d8ed2271c08ec5e.png)

当服务器接收到该字符串会采用如下方式解密还原机器码：
- 分割出加密的机器码和密钥
- 通过解密算法去解密前面16字节的机器码。
例如这里对j2ylvj50suxr8vzss17s3.php进行解密。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0160ca050b8fdbf875.png)

分割j2ylvj50suxr8vzs为加密的16字节机器码，s17s3为随机生成的密钥。解密算法如下。

[![](https://p4.ssl.qhimg.com/t013fa559aa9924c15d.png)](https://p4.ssl.qhimg.com/t013fa559aa9924c15d.png)

从而解密还原出原始的机器码：

[![](https://p5.ssl.qhimg.com/t0160fbed859d839168.png)](https://p5.ssl.qhimg.com/t0160fbed859d839168.png)

其随后构造成HTTP格式的数据包发送出去。

[![](https://p4.ssl.qhimg.com/t017a59e056c2781e35.png)](https://p4.ssl.qhimg.com/t017a59e056c2781e35.png)

如图为构造HTTP数据包的函数，UserAgent是通过ObtainUserAgentString函数生成的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fc0219099b669a12.png)
1. 指令下发
远控服务器是通过不同的HTTP状态码来下发控制指令，受控端会进行判断。

[![](https://p3.ssl.qhimg.com/t017db25074b19069df.png)](https://p3.ssl.qhimg.com/t017db25074b19069df.png)

在返回的HTTP数据包头中，Date字段中存放服务器返回的机器码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010cc7165952c424a6.png)

受控端会对服务器下发的控制信息进行解密，解密算法如下：

[![](https://p3.ssl.qhimg.com/t018356c06e9ea19e09.png)](https://p3.ssl.qhimg.com/t018356c06e9ea19e09.png)

其解密密钥为136字节。

```
EC1ABCB66F641126C2250C5CF26C9902BD53043EAAF5FE0374597261674FD732E2C0498A9FA06203C5641323C3B4DDCB5CD8A22A0EDCAE39A11D7E98A2B1B6276C595E7CC1E1A0C743B8C075416C7DB3CB509AB5059556E99D2818BDDDEEE508AC871474239CC4B5527A8AED49949D5A421C785484ED084F1FCD3D3CFD1D8D8B
```
1. 回传数据
受控端接受到控制服务器下发的指令后，会根据HTTP返回的状态码确定要执行的命令，例如返回码是203的时候就会上传执行，返回码是202的时候就会截屏和获取进程列表。

[![](https://p3.ssl.qhimg.com/t01ca7f528dcaaa5cc8.png)](https://p3.ssl.qhimg.com/t01ca7f528dcaaa5cc8.png)

并且上传数据按如下格式构造：

4个字节长度 + 1字节token + 加密后的内容。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018c4b79dc51be264d.png)

例如这里执行获取屏幕截屏和进程快照信息，并加密发送到控制服务器。

[![](https://p3.ssl.qhimg.com/t01b373a35e66d581df.png)](https://p3.ssl.qhimg.com/t01b373a35e66d581df.png)

### <a name="_Toc502736867"></a>功能小结

该远控模块实现了以下控制命令，包括：
- 上传执行脚本
- 上传执行PE
- 回传屏幕截屏
- 回传进程列表
其使用HTTP协议进行控制通信，采用这种控制协议也更便于攻击者使用Web页面来可视化控制和管理失陷主机，其HTTP协议通信步骤如下：
- 机器中木马后，会每隔不定时间间隔去连接C&amp;C服务器的80端口，根据HTTP协议发送touch包，发送的http数据包的GET数据中包括编码后的长度随机的机器码。
- 服务器收到touch包后，会记录下来最近一次活跃时间，判断是否在线。
- 服务器如果需要对受控端进行控制，就会回一个202或者203的HTTP状态码，下发指令。下发的指令是在http数据段里面，数据包格式为4个字节长度+1个字节token+加密后的内容。
- 受控端收到命令后，会判断服务器返回的http状态码，根据不同的状态码去解析数据包去执行不同的命名，然后把执行后的结果回传给服务器。
- 控制者可以通过对服务端的Web界面对受害者进行控制。
交互操作可以总结为如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015a3349588b6480e9.jpg)

## 关联分析与回溯

360威胁情报中心通过对PowerShell Loader脚本中的关键字搜索，发现了其在一个VPS主机上搭建的Web控制端页面。

[![](https://p0.ssl.qhimg.com/t01f27f91fe4c4ab53c.png)](https://p0.ssl.qhimg.com/t01f27f91fe4c4ab53c.png)

主控端的界面如下，最后一次测试时间应该在2017年6月，已经在近半年以前。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014d4d9b159151c733.png)

通过该Web管理后台可以对受控机器进行控制操作。

[![](https://p3.ssl.qhimg.com/t0171be2bb7668d4470.png)](https://p3.ssl.qhimg.com/t0171be2bb7668d4470.png)

另外一个Loots页面保存了控制端发送控制指令后的一些日志数据，包括执行命令、上传文件、截屏、下载文件、执行脚本的功能。

[![](https://p4.ssl.qhimg.com/t01e4d934a50494c0b0.png)](https://p4.ssl.qhimg.com/t01e4d934a50494c0b0.png)

我们从日志数据中找到了一个名为setup.js的脚本文件，其代码和我们分析的laksasokpaslkak.js的代码大致一样。

[![](https://p3.ssl.qhimg.com/t013b95894d404eb73e.png)](https://p3.ssl.qhimg.com/t013b95894d404eb73e.png)

通过把该脚本中的DLL数据用同样的方法解密出来后，发现和前面分析的远控模块socksbot.dll完全一样，其C&amp;C为46.166.163.243，与测试机IP 46.166.163.242属于同一网段。

[![](https://p2.ssl.qhimg.com/t018254341c0de43583.png)](https://p2.ssl.qhimg.com/t018254341c0de43583.png)

查询360威胁情报平台数据确定其属于“摩诃草”组织。

[![](https://p5.ssl.qhimg.com/t01d3d3b33ba9704019.png)](https://p5.ssl.qhimg.com/t01d3d3b33ba9704019.png)

我们可以看到测试机执行命令后的一些结果日志。

[![](https://p1.ssl.qhimg.com/t016f030337e3ed7b3a.png)](https://p1.ssl.qhimg.com/t016f030337e3ed7b3a.png)

执行ipconfig命令的结果。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fc822d3cedb17ab5.png)

我们还发现攻击者曾在测试机上测试上传其另外的远控木马程序和从远程地址下载恶意载荷。

[![](https://p1.ssl.qhimg.com/t01e7be066993310b40.png)](https://p1.ssl.qhimg.com/t01e7be066993310b40.png)

[![](https://p0.ssl.qhimg.com/t015537a591269a9dbf.png)](https://p0.ssl.qhimg.com/t015537a591269a9dbf.png)

这个Web版木马控制端程序的网站域名（yds.deckandpatio.ca）绑定的IP地址为91.235.129.203。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019465e215ec6dc2f7.png)

这个IP的别名为：vds8262.hyperhost.name。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0117ef5c1d9a526ae4.png)

我们发现其是在一个乌克兰的服务商上申请注册的VPS服务器，其服务商官网为https://hyperhost.ua/ru。而yds.deckandpatio.ca这个域名应该是其提供的一个免费的二级域名。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0123fb5631f09602b1.png)

## 总结

通过分析“摩诃草”组织最新制作并投入使用的攻击恶意代码，攻击者选择脚本类语言来重新实现攻击载荷的投放组件，可能源于其对开发工具的便利性和效率的倾向性。

虽然我们没有明确线索证实该次针对乌克兰人员的攻击事件中该类攻击脚本是如何诱导受陷用户下载和运行的，但根据其过去的攻击模式推测，其可能采用如下几种方式。
- 构造包含有恶意脚本的自解压执行的压缩包；
- 鱼叉攻击，并附带有包含恶意脚本的压缩包文件或附有恶意脚本压缩程序下载的钓鱼链接；
- 在社交网络上发送附有恶意脚本压缩程序下载的钓鱼链接；
也不排除其可能通过入侵网站，在页面植入恶意脚本代码的方式。

从“摩诃草”过去采用的攻击模式和使用的恶意代码技术来看，该组织比较偏好于使用脚本和C#来开发攻击工具的习惯。我们推测其更倾向于选择能够快速开发和实现攻击的方式，并且通过不断更新和变化的攻击工具来逃避检测和隐藏其攻击行径。攻击者还制作了可用于Web管理的控制后台程序来方便大规模管理和控制受陷主机。

从我们发现的攻击者注册的VPS服务器及其Web控制页面，攻击者发起新的攻击和使用新的恶意代码工具至少会提前半年进行准备和测试。

目前我们还无法推测其发起此次攻击事件的动机，可能是该组织针对东欧部分国家发起的定向攻击，也不排除是其发起的一次基于新制作的攻击武器的一次实战演练。所以我们在此对该类恶意代码的部分技术细节进行披露，以便于提前防御该组织在未来的攻击行动中进一步大规模使用该类攻击恶意代码。

## 参考链接

【1】2016.8.4 360威胁情报中心

[https://ti.360.net/blog/uploads/2017/09/21/6286ad3a711b98acf1fe49cafc3d1669.pdf](https://ti.360.net/blog/uploads/2017/09/21/6286ad3a711b98acf1fe49cafc3d1669.pdf)

【2】2017.11.30 360威胁情报中心

[https://ti.360.net/blog/articles/exploit-kit-in-oceanlotus-group/](https://ti.360.net/blog/articles/exploit-kit-in-oceanlotus-group/)

【3】PowerShell ReflectivePEInjection脚本

[https://github.com/clymb3r/PowerShell/blob/master/Invoke-ReflectivePEInjection/Invoke-ReflectivePEInjection.ps1](https://github.com/clymb3r/PowerShell/blob/master/Invoke-ReflectivePEInjection/Invoke-ReflectivePEInjection.ps1)



## IOC列表

C&amp;C服务器<br>
5.8.88.64<br>
文件名<br>
laksasokpaslkak.js<br>
互斥体<br>
Global\\[num]stp<br>
Global\\[num]nps<br>
解密密钥

```
EC1ABCB66F641126C2250C5CF26C9902BD53043EAAF5FE0374597261674FD732E2C0498A9FA06203C5641323C3B4DDCB5CD8A22A0EDCAE39A11D7E98A2B1B6276C595E7CC1E1A0C743B8C075416C7DB3CB509AB5059556E99D2818BDDDEEE508AC871474239CC4B5527A8AED49949D5A421C785484ED084F1FCD3D3CFD1D8D8B
```
