
# 【技术分享】勒索软件Spora以离线方式感染——无需与控制服务器通信


                                阅读量   
                                **75472**
                            
                        |
                        
                                                                                                                                    ![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securingtomorrow.mcafee.com
                                <br>原文地址：[https://securingtomorrow.mcafee.com/mcafee-labs/spora-ransomware-infects-offline-without-talking-control-server/](https://securingtomorrow.mcafee.com/mcafee-labs/spora-ransomware-infects-offline-without-talking-control-server/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85594/t01f668e0b4cb2d4e64.jpg)](./img/85594/t01f668e0b4cb2d4e64.jpg)

翻译：[华为未然实验室](http://bobao.360.cn/member/contribute?uid=2794169747)

预估稿费：110RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**传播方式**





Spora是一款勒索软件，其会加密受害者的文件，受害者想要解密文件就必须支付赎金。该勒索软件通过大量垃圾邮件在短时间内感染了众多计算机。其有一个非常特殊的特性——以离线方式感染。

垃圾邮件中有一个.zip文件，其中包含一个用于逃避某些电子邮件扫描器的检测及最大限度扩大其传播范围的HTA（HTML应用程序）文件。邮件内容精心设计，目的是使用社会工程技术引诱受害者。该HTA文件还通过使用rtf.hta和doc.hta双扩展来欺骗用户。如果文件扩展名在受害者的机器上隐藏，那么他们将只看到第一个扩展名，并可能受骗打开文件。<br>

垃圾邮件如下所示：

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013bdc597ef7f9538a.png)

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a36365bd6670d90d.png)

HTA文件的内容：

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0134aa231ad85f81b2.png)

在运行时，HTA文件在%Temp%文件夹中释放一个JavaScript文件。随后，JavaScript在％TEMP％中提取一个带有随机名称的可执行文件（在本例中为：goodtdeaasdbg54.exe）并执行。

HTA文件还提取并执行一个损坏的.docx文件，并返回一个错误来分散受害者的注意力：

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011ce1617797ed347c.jpg)

**<br>**

**分析**



Goodtdeaasdbg54.exe使用UPX打包工具打包，并包含有效载荷（Spora）。其首先检查此文件的副本是否在内存中运行。如果没有，则其创建一个互斥体。Spora使用互斥对象来避免多次感染系统。

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ea4b9548002fe607.png)

Spora检查系统中可用的逻辑驱动器：

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019be83a3936befc2a.png)

一旦资源可用，Spora立即搜索要加密的文件，但会规避“windows”、“Program files”及“games”。

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01956c98ecbc1e5c94.png)

Spora从目标系统中删除卷影副本，从而使用户无法恢复加密的文件。要删除卷影副本，Spora使用命令“vssadmin.exe Delete Shadows /All /Quiet”。该勒索软件使用vssadmin.exe实用程序静默删除计算机上的所有卷影副本。

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01562b11523fda6e57.png)

其还在根驱动器创建.lnk文件以及.key和.lst文件。

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017a67946b97e747a9.png)

Spora还会删除注册表值，以删除快捷方式图标。

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011b4a922e7d11f564.png)

**加密过程**

第1步：它为每个文件生成一个随机的“文件不同而各异的AES”对称密钥。

第2步：Spora生成本地公 – 私密钥对。

第3步：第2步生成的公钥将加密“文件不同而各异的AES”密钥，并将其附加到加密文件。

第4步：在加密所有文件后，Spora生成唯一的AES对称密钥。

第5步：第2步中生成的私钥被复制到.key文件中，并被第4步中生成的唯一AES密钥加密。

第6步：最后，通过解密公钥（如下所述）并将其附加到.key文件来加密唯一的AES密钥。

恶意软件作者的公钥使用硬编码AES密钥嵌入在恶意软件可执行文件中。解密的公钥：

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dfa420546df99d53.png)

只有恶意软件作者持有的私钥才能进行解密。付款完成后，作者才可能向受害者提供私有RSA密钥来解密在.key文件中附加的加密的AES密钥。解密的AES密钥将解密剩余的.key文件，其中包含用户的私有RSA密钥。整个过程有点复杂、冗长，但通过使用该方案，Spora就无需从控制服务器获取密钥，就可以脱机工作。

<br>

**密钥文件**



Spora加密六种类型的文件扩展名：

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b5d1c00d11aebe61.png)

.key文件名包含以下格式的信息：

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0153282cb45a50ce61.png)

并使用替换方法对所有这些信息进行编码。

在我们的例子中，US736-C9XZT-RTZTZ-TRHTX-HYYYY.KEY转换为：

美国作为地区。

字符“736C9”表示MD5哈希的开始。

10个加密的office文件（第1类）

两个加密的PDF（第2类）

零加密CorelDraw / AutoCAD / Photoshop文件（第3类）

零加密数据库文件（第4类）

25个加密图像（第5类）

15个加密存档（第6类）

.key文件的解码机制：

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01afdead9663503c9a.png)

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ddee5b8882186cf1.png)

**<br>**

**赎金消息**



以下是俄语和英语版的赎金说明：

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e7a335488edd7152.png)

Spora给受害者提供若干方案，期限不同，价格不同。

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013e2b36141edd5773.png)

[![](./img/85594/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01eb60e9634d8a7fea.png)

分析中使用的哈希值：

a159ef758075c9fb64d3f06ff4b40a72e1be3061

0c1007ba3ef9255c004ea1ef983e02efe918ee59
