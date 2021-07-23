> 原文链接: https://www.anquanke.com//post/id/162102 


# 瞄准中亚政治实体：针对Octopus恶意软件新样本的技术分析


                                阅读量   
                                **121791**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/octopus-infested-seas-of-central-asia/88200/](https://securelist.com/octopus-infested-seas-of-central-asia/88200/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01bd7a435e650448cf.jpg)](https://p5.ssl.qhimg.com/t01bd7a435e650448cf.jpg)

## 一、概述

在过去的两年中，我们持续在监测一个针对中亚用户和外交实体的网络间谍活动，该活动使用的语言为俄文。我们将这一恶意活动背后的组织命名为DustSquad。我们监测到该组织在过去开展了4起恶意活动，在活动中使用了Android和Windows的恶意软件，我们此前已经向部分客户提供了这4起恶意活动的情报报告。在本文中，我们主要分析一个名为Octopus的恶意Windows恶意程序，该恶意程序主要针对外交实体。

该恶意程序最初是由ESET于2017年发现，他们在一些弃用的C&amp;C服务器上找到了0ct0pus3.php脚本，该恶意程序也因此而得名。同时，我们也开始监控这一恶意软件，并使用基于相似性算法的Kaspersky Attribution Engine，发现了Octopus与DustSquad组织具有关联，并在2018年4月公布这一成果。根据我们的监测结果，可以追溯到2014年针对前苏联中亚共和国和阿富汗的恶意活动。

Octopus使用了Delphi作为其编程语言，这是非常罕见的。除了这一恶意软件之外，还有俄语的Zebrocy（由Sofacy组织编写）、印地语的DroppingElephant和土耳其语的StrongPity。尽管我们发现有主机同时感染了Zebrocy和Octopus，但由于没有发现二者之间存在任何相似性，因此认为这两个恶意软件是无关的。



## 二、新样本简述

2018年4月，我们发现了一个新的Octopus样本，该样本伪装为哈萨克斯坦反对派政治团体的通信软件。恶意软件被打包为ZIP文件，名称为dvkmailer.zip，其时间戳为2018年2-3月。其中DVK表示哈萨克斯坦民主选择（Kazakhstan Democratic Choice），这是一个在该国被禁止的反对派政党。该党俄语名称（Демократический Выбор Казахстана）的首字母缩写为ДВК，转换成英文即为DVK。该政党广泛使用Telegram进行通信，并使得Telegram成为哈萨克斯坦暗中禁用的一个软件，这一禁令也成为该国的一大热门话题。这一Dropper伪装成俄语界面的Telegram Messenger。

而针对本次发现的新样本，我们目前没有找到它是冒充了哪一款软件。事实上，我们认为这次的样本并没有冒充其他软件。该木马使用了第三方Delphi库，包括基于JSON实现C&amp;C通信的Indy和用于压缩的TurboPower Abbrevia（ sourceforge.net/projects/tpabbrevia ）。恶意软件通过修改系统注册表来实现持久化。其服务器端是将.php脚本部署在不同国家的商业服务器上。Kaspersky Lab将Octopus木马检测为Trojan.Win32.Octopus.gen。



## 三、技术分析

攻击者利用哈萨克斯坦对Telegram的禁令，将该恶意Dropper推动成为替代Telegram的通信软件，提供给反对派使用。

Telegram messenger以最简单的方式建立网络模块持久性，并启动该模块：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104635/181012-octopus-1.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104635/181012-octopus-1.png)

尽管我们清楚，该恶意软件是使用了某种形式的社会工程，但目前无法确认具体的分发方式。此前，这一恶意组织曾使用过鱼叉式网络钓鱼来传播恶意软件。

### <a class="reference-link" name="3.1%20Dropper"></a>3.1 Dropper

MD5哈希值： 979eff03faeaeea5310df53ee1a2fc8e

名称：dvkmailer.zip

压缩包内容：

CsvHelper.dll（d6e813a393f40c7375052a15e940bc67） 合法.NET CSV文件解析器

Telegram Messenger.exe（664a15bdc747c560c11aa0cf1a7bf06e） 持久化和启动工具

TelegramApi.dll（87126c8489baa8096c6f30456f5bef5e） 网络模块

Settings.json（d41d8cd98f00b204e9800998ecf8427e） 空文件

### <a class="reference-link" name="3.2%20%E5%90%AF%E5%8A%A8%E7%A8%8B%E5%BA%8F"></a>3.2 启动程序

MD5哈希值：664a15bdc747c560c11aa0cf1a7bf06e

文件名：Telegram Messenger.exe

PE时间戳：2018.03.18 21:34:12 （GMT）

链接器版本：2.25（Embarcadero Delphi）

在进行用户交互之前，启动程序会检查同一目录中是否存在名为TelegramApi.dll的文件（在FormCreate()函数实现）。如果存在，启动程序会将网络模块复制到启动（Startup）目录中，重命名为Java.exe并运行。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104634/181012-octopus-2.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104634/181012-octopus-2.png)

Delphi Visual Component Library（VCL）程序基于表单元素（Form Elements）的事件处理程序。这些程序非常大（大约2.6MB，包含12000多个函数），但所有这些代码主要用于处理可视化组件和运行时库（Run-time Library）。只有3个定义的处理程序用于控制Octopus启动程序内的元素。

1、FormCreate()：在进行用户活动之前，作为构造函数运行。通过Startup目录，保证网络模块的持久性，并运行网络模块。

2、Button1Click()：显示资源管理器对话框窗口，以选择“发送文件”。

3、DateTimePicker1Click()：显示日历，以选择“发送日期”。

“发送邮件”的按钮没有其对应的处理程序，因此这一启动程序假装是另一种通信软件，实际上没有任何作用。其原因可能在于恶意软件还没有编写完成，毕竟通过该软件发送的信息，实际上很可能是有价值的。我们认为，该恶意软件很可能是匆忙编写而成的，攻击者受到时间的限制，决定跳过通信功能。

### <a class="reference-link" name="3.3%20%E7%BD%91%E7%BB%9C%E6%A8%A1%E5%9D%97"></a>3.3 网络模块

C&amp;C通信方案：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104632/181012-octopus-3.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104632/181012-octopus-3.png)

MD5哈希值：87126c8489baa8096c6f30456f5bef5e

文件名：TelegramApi.dll

PE时间戳：2018.02.06 11:09:28 （GMT）

链接器版本：2.25（Embarcadero Delphi）

尽管具有文件扩展名，但该网络模块实际上是一个可移植可执行文件，该文件不依赖于其他文件，并非动态链接库。第一个样本中会检查用户临时文件夹中是否存在名称为1?????????.*的文件，如果找到则会将这些文件删除。然后，在Application Data目录中创建一个.profiles.ini文件，用于存储恶意软件的日志。

HTTP请求与响应内容如下：

1、（请求）GET /d.php?check

（响应）JSON “ok”

2、（请求）GET /d.php?servers

（响应）JSON域名

3、（请求）GET /i.php?check=

（响应）JSON “ok”

4、（请求）POST /i.php?query=

（响应）JSON响应代码或命令取决于POST的数据

第一阶段的.php脚本检查连接，并获取C&amp;C域名：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-4.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-4.png)

所有网络模块都包含来自不同国家的IP地址，这些地址以硬编码形式保存，全部属于购买的商用服务器。攻击者只需要在其中部署第一阶段的.php脚本，它将检查连接，并使用HTTP GET请求获取实际的C&amp;C服务器域名。

在进行初始连通性检查后，恶意软件会收到带有实际C&amp;C域名的JSON：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-5.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-5.png)

然后，网络模块检查被感染用户的ID（以硬编码形式保存）：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-6.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-6.png)

在检查被感染用户32位的ID之后，使用HTTP POST请求，将收集到的数据发送到C&amp;C服务器。从编程角度来看，这个ID非常奇怪，因为恶意软件是用其系统数据的MD5哈希值作为标识用户身份的“指纹”。

在HTTP POST请求中，查看到经过Base64编码后的用户数据：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-7.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-7.png)

与C&amp;C服务器的所有通信，都基于JSON格式的数据和HTTP协议。为此，恶意软件编写者使用了Indy项目（ indyproject.org ）中公开的一些库，同时还使用了第三方工具TurboPower Abbrevia（ sourceforge.net/projects/tpabbrevia ）进行压缩。

在发送所有初始HTTP GET请求后，恶意软件开始收集JSON格式的系统数据。其中包括系统中所有驱动器磁盘名称和大小、计算机名称、用户名、Windows目录、主机IP等。有一个有趣的字段是“vr”，其值为2.0，似乎是其通信协议中加入了恶意软件的版本信息。

“id”字段中保存被感染主机的指纹信息，恶意软件主动使用WMI（Windows Management Instrumentation）获取信息。该木马使用以下参数运行WMIC.exe：

```
C:WINDOWSsystem32wbemWMIC.exe computersystem get Name /format:list
C:WINDOWSsystem32wbemWMIC.exe os get installdate /format:list
C:WINDOWSsystem32wbemWMIC.exe path CIM_LogicalDiskBasedOnPartition get Antecedent,Dependent
```

随后，该模块计算ID的MD5哈希值，作为被感染主机的最终ID。“act”字段用于对通信阶段进行编号（初始的指纹识别过程编号为0）。在此之后，HTTP POST控制服务器返回一个JSON `{`“rt”:”30″`}`，客户端继续通过HTTP POST方式发送下一个“act”：

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-8.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/10/12104631/181012-octopus-8.png)

此时，C&amp;C会发送包含执行命令的JSON，其命令包括上传文件、下载文件、获取屏幕截图以及在主机上查找*.rar文件。

### <a class="reference-link" name="3.4%20%E5%85%B6%E4%BB%96%E8%BD%AF%E4%BB%B6"></a>3.4 其他软件

除了木马本身，Octopus编写者还使用了密码转储实用程序fgdump。

从.php脚本中获取到最新样本（2017年-2018年期间发现）的硬编码IP和对应Web域名如下：

[![](https://p3.ssl.qhimg.com/t011e7477bfac5a2760.png)](https://p3.ssl.qhimg.com/t011e7477bfac5a2760.png)



## 四、结论

在2018年，一些恶意组织纷纷将目标对准了中亚的政治实体，其中包括IndigoZebra、Sofacy（使用Zebrocy恶意软件）和我们本文所分析的DustSquad（使用Octopus恶意软件）。我们发现，有一些特定的地区，几乎成为了所有恶意组织所针对的目标，就像是一个巨大的“威胁磁铁”。针对这些特定地区，攻击者们表现出极高的兴趣，并且不断有新组织投入对该地区的攻击活动当中，比如DustSquad就是一个这样的新型组织。



## 五、IoC

### <a class="reference-link" name="5.1%20%E6%81%B6%E6%84%8F%E6%96%87%E4%BB%B6%E5%93%88%E5%B8%8C%E5%80%BC"></a>5.1 恶意文件哈希值

87126c8489baa8096c6f30456f5bef5e

ee3c829e7c773b4f94b700902ea3223c

38f30749a87dcbf156689300737a094e

6e85996c021d55328322ce8e93b31088

7c0050a3e7aa3172392dcbab3bb92566

2bf2f63c927616527a693edf31ecebea

d9ad277eb23b6268465edb3f68b12cb2

### <a class="reference-link" name="5.2%20%E5%9F%9F%E5%90%8D%E5%92%8CIP%E5%9C%B0%E5%9D%80"></a>5.2 域名和IP地址

85.93.31.141

104.223.20.136

5.8.88.87

103.208.86.237

185.106.120.240

204.145.94.101

5.188.231.101

103.208.86.238

185.106.120.27

204.145.94.10

hovnanflovers.com

latecafe.in

certificatesshop.com

blondehairman.com

porenticofacts.com

### <a class="reference-link" name="5.3%20%E4%B8%8A%E4%BC%A0/%E4%B8%8B%E8%BD%BD%E6%96%87%E4%BB%B6%E7%9A%84%E8%BE%85%E5%8A%A9URL"></a>5.3 上传/下载文件的辅助URL

www.fayloobmennik.net/files/save_new.html

[http://uploadsforyou.com/download/](http://uploadsforyou.com/download/)

[http://uploadsforyou.com/remove/](http://uploadsforyou.com/remove/)

下列IoC已经不再使用，但可用于检测威胁：

031e4900715564a21d0217c22609d73f

1610cddb80d1be5d711feb46610f8a77

1ce9548eae045433a0c943a07bb0570a

3a54b3f9e9bd54b4098fe592d805bf72

546ab9cdac9a812aab3e785b749c89b2

5cbbdce774a737618b8aa852ae754251

688854008f567e65138c3c34fb2562d0

6fda541befa1ca675d9a0cc310c49061

73d5d104b34fc14d32c04b30ce4de4ae

88ad67294cf53d521f8295aa1a7b5c46

a90caeb6645b6c866ef60eb2d5f2d0c5

ae4e901509b05022bbe7ef340f4ad96c

ca743d10d27277584834e72afefd6be8

ce45e69eac5c55419f2c30d9a8c9104b

df392cd03909ad5cd7dcea83ee6d66a0

e149c1da1e05774e6b168b6b00272eb4

f625ba7f9d7577db561d4a39a6bb134a

fc8b5b2f0b1132527a2bcb5985c2fe6b

f7b1503a48a46e3269e6c6b537b033f8

4f4a8898b0aa4507dbb568dca1dedd38

### <a class="reference-link" name="5.4%20%E7%AC%AC%E4%B8%80%E9%98%B6%E6%AE%B5.php%E8%84%9A%E6%9C%AC%E4%B8%8B%E8%BD%BD%E6%BA%90"></a>5.4 第一阶段.php脚本下载源

148.251.185.168

185.106.120.46

185.106.120.47

46.249.52.244

5.255.71.84

5.255.71.85

88.198.204.196

92.63.88.142

### <a class="reference-link" name="5.5%20.php%E8%84%9A%E6%9C%AC%E8%BF%94%E5%9B%9E%E5%9F%9F%E5%90%8D"></a>5.5 .php脚本返回域名

giftfromspace.com

mikohanzer.website

humorpics.download

desperados20.es

prom3.biz.ua
