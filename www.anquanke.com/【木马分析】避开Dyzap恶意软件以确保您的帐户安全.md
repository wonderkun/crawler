
# 【木马分析】避开Dyzap恶意软件以确保您的帐户安全


                                阅读量   
                                **88053**
                            
                        |
                        
                                                                                                                                    ![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fortinet.com
                                <br>原文地址：[http://blog.fortinet.com/2017/02/22/keep-your-account-safe-by-avoiding-dyzap-malware](http://blog.fortinet.com/2017/02/22/keep-your-account-safe-by-avoiding-dyzap-malware)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85762/t0172155a0e951d910e.jpg)](./img/85762/t0172155a0e951d910e.jpg)**

****

翻译：[啦咔呢](http://bobao.360.cn/member/contribute?uid=79699134)

稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**介绍**

Dyzap属于一种恶意软件，被设计来从大型目标应用程序窃取保密信息，方式是在普通浏览器安装“man in the browser”。FortiGuard研究人员最近发现了该木马病毒的一种新变体。窃取的信息可能包括但不限于在被感染系统上存储的系统信息和应用凭证。在本博客中，我们将解释恶意软是件如何窃取用户帐户，充当键盘记录器，并与其C＆C服务器进行通信。

<br>

**窃取流程**

Dyzap的目标是从超过一百个的应用程序中窃取信息，其中包括浏览器，FTP应用程序等。 

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011b9e9f699a4d6665.png)

图1：主要窃取流程

为了从不同类型的应用程序窃取数据，Dyzap通过不同的方式处理它们。这使得它可以从数据库，注册表中，或者从受感染机器上应用程序安装的文件中窃取数据。图2显示了一些目标应用程序，如Fossamail，Postbox和其他。

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015775a7317f3b6d7b.png)

图2：恶意软件试图窃取的应用程序的一部分

为了更好地理解Dyzap能够采用的不同方式，我们选择了四个应用程序，并分析了Dyzap如何从它们那里获得登录凭据。以下所有分析均在Windows 7 32位下进行。在其他操作系统中引用的路径可能不同。

<br>

**Chrome家族**

Dyzap的主要例程之一是从sqlite3数据库文件中窃取登录信息。例如，Chromium将登录信息存储在名为“Login Data”或“Web Data”的文件中。使用图3所示的代码片段和硬编码文件路径，它可以尽可能搜索刚才提到的目录中所包含的文件。如果文件存在，它将内容复制到临时文件中以供进一步操作。

要获取登录信息，它首先要验证目标是SQlite3文件。接下来，它查找一个“独特的”字符串模式以从“登录”表中提取登录信息。最后，它使用字符串模式“password_value”，“username_value”和“original_url”提取用户帐户，如图4所示。

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e825c0b5b5ee0634.png)

图3：Dyzap在硬编码目录中查找文件

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a33a45a7dc4695d7.png)

图4：Dyzap通过硬编码字符串查找登录信息

Chrome家族中的其他浏览器重复了类似的窃取例程，这些浏览器包括： Comodo Dragon，MapleStudio，Chrome，Nichrome，RockMelt，Spark，Chromium，Titan浏览器，Torche，Yandex，Epic隐私浏览器，CocCoc浏览器，Vivaldi，Comodo Chromodo，Superbird ，Coowon，Mustang浏览器，360浏览器，CatalinaGroup Citrio，Chrome SxS，Orbitum，Iridium和Opera。

<br>

**Firefox家族**

对于Firefox家族的浏览器，Dyzap搜索signons.sqlite和login.json文件来查找和窃取凭据。login.json的名称带着误导性，它实际上是一个sqlite数据库，包括所有保存的用户名和密码。这些浏览器包括Firefox，IceDragon，Safari，K-Melon，SeaMonkey，Flok，Thunderbird，BlackHawk，Postbox，Cyberfox和Pale Moon。

**<br>**

**Far FTP**

除了从数据库文件窃取之外，Dyzap恶意软件还尝试从注册表中收集一些FTP应用程序的私密信息。例如，在Far FTP中，恶意软件简单地搜索以下路径，如图5所示：



```
HKCU  Software  Far  Plugins  FTP  Hosts
HKCU  Software  Far2  Plugins  FTP  Hosts
```

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0154952b45fe0ac41d.png)

图5：从Far2注册表窃取

如果找到它们，Dyzap查询“Password”，“User”和“HostName”子项的值。以下表1是通过注册表寻找到的目标应用程序列表。然后恶意软件硬编码每个应用程序的注册表路径（可能包含私密信息）。

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011123ac682c7c4f0f.png)

表1：恶意软件尝试从其注册表窃取的应用程序

**<br>**

**Pidgin**

****

Dyzap的另一个功能是从存储在受感染机器上的登录凭据文件中窃取机密信息。例如，Pidgin是一个聊天程序，它允许用户同时在多个聊天网络上登录帐户。此应用程序在"%AppData%Roaming.purpleaccounts.xml."中的一个XML文件中保存账户登录的信息。Dyzap试图在可能的目录中通过搜索来找到* .xml文件（图6），然后将文件的副本发送到它的C＆C服务器上。

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012b3d12ba9e7197d4.png)

图6：找到目标文件的可能目录

下表显示恶意软件在搜索机密信息时搜索到的所有应用程序和相关文件。

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011627573e14e4ce1f.png)

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e1fe0ceb2bab8f87.png)

表2：恶意软件尝试从其组件文件中窃取的应用程序列表

**<br>**

**键盘记录功能**

在其键盘记录器组件中，恶意软件创建一个新线程以捕获所有键盘输入，剪贴板数据和窗口标题，如图8所示。所有被盗信息都保存到恶意软件在临时目录创建的％RANDOM-NUMBER％.Kdb文件中。为了hook到键盘，恶意软件调用SetWindowsHookExW()来捕获键盘输入。键盘记录器的结果也将与其他被盗信息一起上传到C＆C服务器。

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0112ef239478064e24.png)

图8：键盘挂钩线程

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b31b019916ac694e.png)

图9：监视低级别键盘输入事件的挂钩过程

<br>

**C＆C通信**

在从目标应用收集数据之后，将进行被盗信息的封包。数据以串行化的二进制格式发送到C＆C服务器。封包结构包含三个主要子结构，每个结构填充如表3所示的信息块：

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011a8883089461842c.png)

表3：信息块的基本结构

封包信息从硬编码标签开始。位于块1中的所有标签在图10中标示为B1。例如，数据包中的0x12和0x27显示为 x12  x00  x27  x00。随后，将硬编码字符串“PWSBin”附加到块2格式的标签（表4中的第1节）。在图10中，该部分显示为Tag1，Tag2，Type, Size和 Data。

该封包接着包含来自受感染机器所有收集的信息，分别包括用户名，计算机名称，域名以块2格式保存(窗体坐标在左上，右下)。接下来，它检查当前用户是否为admin，是否开启了用户安全标识，以及受感染的计算机是32位还是64位。然后它包含Windows主版本，次版本和产品类型，以及一个预初始化字节，四个标签在行（ x01， x00， x00， x00 ）中以块1的格式附加到数据包。

接着数据包以四个字节大小标示被盗数据—被恶意软件加密（A *）。互斥字符串类型，大小和数据，以及恶意软件使用系统时间创建的5字节随机字符串，以块2格式被添加（B *）。最后，被盗的加密数据及其大小以块3格式被添加（C *，D *）。有趣的是，每个被窃取的数据部分开头是一个字节，其表示一个索引列表的索引，指示了相应应用的数据位置。

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01030633e9af9fc9a4.png)

图10：HTTP请求内容发送到服务器

[![](./img/85762/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0158c82773a2c53daf.png)

表4：命令和控制流量摘要

<br>

**结论**

Dyzap是一个多任务恶意软件，不限于用一种方式窃取信息。已安装应用程序的本地文件及其注册表都不安全。但Dyzap不仅从应用程序收集数据。它也很好奇并且还可以收集您的键盘输入。当前版本现在功能强大，可以从许多应用程序中窃取信息。在本博客中，我们展示了如何进行数据窃取，以及恶意软件将所有收集的数据发送到C＆C服务器之前将其转换为合适的二进制格式的过程。

<br>

**示例信息**

MD5：eaa07a6113b142e26c83132716d1ab42

SHA256：9740f47b42b04c80d9d8983725c69920581a632df74d96434b6747a53bbd5048

Fortinet检测名称：W32/Generic.RCI！tr
