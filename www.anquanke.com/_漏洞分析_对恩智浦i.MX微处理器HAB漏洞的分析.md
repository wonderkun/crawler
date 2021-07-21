> 原文链接: https://www.anquanke.com//post/id/86528 


# 【漏洞分析】对恩智浦i.MX微处理器HAB漏洞的分析


                                阅读量   
                                **108563**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://blog.quarkslab.com/vulnerabilities-in-high-assurance-boot-of-nxp-imx-microprocessors.html](https://blog.quarkslab.com/vulnerabilities-in-high-assurance-boot-of-nxp-imx-microprocessors.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t015aaa6c3e0ff3f158.jpg)](https://p1.ssl.qhimg.com/t015aaa6c3e0ff3f158.jpg)

作者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**



恩智浦（NXP）半导体公司生产的[i.MX](http://www.nxp.com/products/microcontrollers-and-processors/arm-processors/i.mx-applications-processors:IMX_HOME)系列应用处理器的安全启动特性中存在两个漏洞，这两个漏洞由Quarkslab的两名研究人员Guillaume Delugré和Kévin Szkudłapski发现，本文对这两个漏洞的技术细节做了具体分析。

攻击者可以利用这两个漏洞破坏安全启动过程，从而绕过代码签名认证，实现在启用了HAB（High Assurance Boot）特性的i.MX应用处理器上加载并运行任意代码。有12款i.MX系列处理器受这些漏洞影响。

研究人员于2016年9月发现这些漏洞并将漏洞报告给厂商，在2017年5月19日的举办[高通移动安全峰会](https://qct-qualcomm.secure.force.com/QCTConference/GenericSitePage?eventname=2017Security&amp;page=Summit%20Information)上，Quarkslab与NXP联合[公布](http://www.nxp.com/support/support/documentation:DOCUMENTATION)了本文介绍的技术细节。2017年3月，我们向4个国家的计算机应急小组（CERTs）通报了相关漏洞信息。

NXP公布了一份工程简报以及两份勘误文件（分别为EB00854、ERR010872以及ERR0108873），对这两个漏洞做了简要的介绍，同时也介绍了受影响的处理器型号清单、相应的解决方案以及可能的缓解措施。

在下文中，我们会向大家介绍i.MX处理器的相关特性以及影响这些特性的具体漏洞细节。

<br>

**二、背景介绍**

****

NXP半导体公司生产的i.MX系列处理器是基于ARM的应用处理器，广泛应用于汽车、工业以及电子消费市场中的SoC（System on a Chip）系统。微控制器最早由飞思卡尔（Freescale）半导体公司研发，该公司在2015年被NXP收购，给NXP带来各种面向安全的特性，包括安全及加密启动特性、篡改检测特性、为各种加密算法设计的硬件加速特性、片上及片外安全存储特性、实时安全时钟特性以及基于硬件的随机数生成器特性。

在产品中使用i.MX处理器的厂商需要自己启动这些特性，某些情况下，处理器被设置为锁定状态，此时这些安全特性无法被禁用。

如果读者感兴趣的话，可以使用几种开发板来体验i.MX处理器的安全特性。我们使用基于i.MX6的SabreLite开发板发现了这些漏洞，开发板如下所示：

 [![](https://p4.ssl.qhimg.com/t0197bc1797043f98b1.png)](https://p4.ssl.qhimg.com/t0197bc1797043f98b1.png)

**2.1 何为安全启动**

当处于关机状态的系统被启动后，设备会通过安全启动（secure boot）过程将系统引导到一个已知的健康状态。安全启动过程通常会涉及许多原生代码的执行过程，这些原生代码被封装到多个二进制文件中，设备会加载这些二进制文件，验证文件的可靠性，保证文件未被篡改，然后按顺序运行这些文件，最终将系统引导至厂商或者用户预期的状态。通常情况下，设备会使用具有合法数字签名的二进制程序来完成这一任务，在执行过程中，设备会检查下一个运行的二进制程序的完整性以及真实性，如果验证通过，就会将控制权交给下一个二进制程序。

[![](https://p2.ssl.qhimg.com/t01d34442311593c6fe.png)](https://p2.ssl.qhimg.com/t01d34442311593c6fe.png)

如果设备在已知健康状态下被启动，并且引导过程中执行的一系列程序都已通过有效签名认证，那么当最后一个程序执行后，设备会认为此时自身处于健康并且受信的状态中。然而，如果在安全启动执行链中，某一个程序无法验证下一个程序的有效性，那么最终得到的系统状态将不再被信任。

通常情况下，这条信任链的源头由核心加密密钥（签名及加密密钥）以及存储在片上只读内存（on-chip read only memory）中的原始可信固件（bootrom）这两类因素共同决定。

启用了安全启动特性的系统会以某种方式锁住这条信任链，使实际接触到设备的最终用户、下游厂商、集成商或者攻击者无法通过禁用安全启动特性来篡改设备安全性。这项特性通常用于数字版权管理（DRM）和知识产权保护中，也可以用来防止恶意代码或其他未授权软件在设备上运行。

**2.2 High Assurance Boot（HAB）**

HAB（High Assurance Boot）是NXP在i.MX处理器中实现的安全启动特性。这项特性内置于片上ROM中，负责加载初始程序镜像（通常为启动介质中第一阶段的bootloader）。

HAB使用公开密钥加密算法（具体来说是RSA算法）来对启动时执行的镜像进行验证。镜像厂商已经在离线状态下使用私钥对镜像数据进行签名，i.MX处理器会从该镜像的某个部位中提取签名信息，然后使用相应的公钥信息对签名进行验证。

这条信任链的根节点依赖于一组RSA密钥对，这组密钥对名为SRKs（Super Root Keys，超级根密钥），用于防止设备加载并使用由潜在攻击者提供的任意公钥来运行恶意镜像，恶意镜像使用了攻击者自己的私钥进行签名。此外，它也能优化紧缺的一次性可编程硬件资源。合法的私钥由证书颁发机构（CA）签发，用来对镜像进行签名，对应的公钥哈希表存储在一次性可编程硬件中。对于支持安全启动特性的i.MX处理器而言，这是一种隐藏的ROM以及电子可编程保险丝（electrically programmable fuses，eFuses）。

在启动时，HAB bootrom会从CSF（Command Sequence File）中加载SRK表，计算哈希值，将计算结果与存储在SRK fues中的值进行对比。如果哈希值匹配，那么安全启动过程就会继续检查镜像是否经过正确的私钥签名。启动过程失败或者出现任何错误，处理器就会进入恢复（recovery）模式，在这个模式下，设备可以使用串行下载协议（Serial Download Protocol，SDP）通过UART或者USB端口安全加载启动镜像。

供应商使用代码签名工具（Code Signing Tools，CST）以X.509证书形式提供公钥。HAB特性以API形式与启动镜像代码对接，CSF中的命令可以调用这些API。CSF中包含HAB在安全启动过程中执行的有所命令，也包含SRK表以及证书及签名，以验证待加载运行的那些镜像。

 [![](https://p4.ssl.qhimg.com/t016727b85749855165.png)](https://p4.ssl.qhimg.com/t016727b85749855165.png)

上图为HAB信任链，NXP在“使用HABv4的i.MX50、i.MX53及i.MX 6系列处理器中的安全启动”[文档](http://www.nxp.com/docs/en/application-note/AN4581.pdf)中（AN4581）详细介绍了整个过程。

**2.3 串行下载协议（SDP）******

bootrom支持一种名为串行下载协议（Serial Download Protocol，SDP）的恢复模式，在这种模式下，设备可以通过USB或者UART端口加载启动镜像。

为了实现这一功能，bootrom在HID的基础上实现了带有一些简单命令的小型USB协议：

1、从内存中读取1个单字（READ REGISTER）

2、往内存中写入1个单字（WRITE REGISTER）

3、将启动镜像写入内存（WRITE FILE）

4、写入并执行一组DCD命令（DCD WRITE）

5、执行内存中已加载的启动镜像（JUMP ADDRESS）

当设备被锁定在安全模式下时，会有一系列检查过程，以保证bootrom免受未经允许的内存访问以及未经签名的代码执行，这些检查过程包括：

1、使用白名单方式检查检查访问的内存是否位于许可的范围内。

2、以同一个白名单检查访问的DCD内存范围是否位于许可的范围内。

3、JUMP ADDRESS在执行启动镜像前会先检查启动镜像签名。

<br>

**三、漏洞分析**

****

我们对编译好的一个bootrom进行分析然后发现了这些漏洞。

我们对代码的功能进行了理解，在这个基础上修改了代码中函数的名称，这些名称可能与源代码中真实的函数名不一致。

用来描述函数位置的地址与bootrom镜像有关，这个镜像的MD5值为945cfc9f525a378102dd24b5eb1b41cf。

我们的实验设备是一个处于锁定状态下的Sabrelite开发板，我们通过一个功能型利用代码，绕过了开发板的HAB安全启动过程，从而证实了漏洞的有效性。

InversePath生产的[USB Armory](https://inversepath.com/usbarmory)也受这些漏洞影响，该厂商研发了相应的PoC程序来演示这些漏洞。

**3.1 X.509证书解析中的栈缓冲区溢出漏洞（CVE-2017-7932）**

bootrom的X.509证书解析器中存在一个栈缓冲区溢出漏洞，当解析器加载攻击者构造的一个证书时就会触发这个漏洞。

安全启动中的控制流遵循如下步骤：

1、从存储设备中或者在恢复模式下通过USB接口获取中断向量表（Interrupt Vector Table，IVT）。

2、执行DCD命令。

3、执行CSF命令，这些命令负责安全启动的完整性。当设备处于信任模式下时，这一阶段所执行的CSF命令通常如下：

（1）安装SRK类型的RSA公钥，其SHA256哈希必须与SRK fuses中已写入的哈希值完全一致。

（2）使用经SRK签名的X.509证书安装CSFK公钥。

（3）使用CSFK认证CSF。

（4）安装公钥以验证启动镜像。

（5）使用之前安装的密钥验证启动镜像。

4、执行下一阶段的bootloader。

设备使用INSTALL_KEY这个CSF命令完成密钥安装过程。设备会加载并验证不同的密钥，每个密钥的验证由上一个已安装的密钥来完成（信任链的根节点为SRK fuses）。

当设备安装一个X.509类型的公钥时，hab_csf_cmd_install_key函数（其地址位于0xB5C0处）会找到负责导入X.509证书的插件，然后以下述方式调用：

```
mod_x509-&gt;load_key (x509_parse_certificate)
mod_x509-&gt;verify_key (x509_verify_certificate_signature)
```



因此，设备在验证证书签名之前就已经解析了整个证书。由于INSTALL_KEY命令可以先于任何验证命令执行，因此，攻击者无需篡改启动镜像或者将设备切换到恢复模式，就可以触发X.509解析器中存在的漏洞。

HAB bootrom使用了自定义的ASN.1以及X.509解析库，当解析X.509证书中的扩展属性时，HAB错误调用了某个ASN.1库函数，导致漏洞存在。

asn1_extract_bit_string函数（位于0xE796处）使用了内部函数asn1_deep_copy_element_data（位于0xEF20处）来拷贝一个位串（bit string）对象的内容。

HAB会递归调用这种方法，将ASN.1对象的内容复制到以参数形式传递进来的一个输出缓冲区中。这个函数的一个特殊之处在于，它没有使用任何一个输入参数来保存输出缓冲区的值。相反，当调用者将NULL指针作为输出缓冲区传递给该函数时，函数就会返回所需的缓冲区大小，这一点与Windows API非常类似。

在使用asn1_extract_bit_string函数时，首先我们得先传入一个NULL参数，获得所需的缓冲区大小，再使用malloc分配所需的内存，然后使用新分配的缓冲区再次调用这个函数。

X.509规范将keyUsage扩展描述为一个位串对象，包含如下9个位：

```
KeyUsage ::= BIT STRING `{`
  digitalSignature		(0),
  nonRepudiation       	(1),
  keyEncipherment         	(2),
  dataEncipherment       	(3),
  keyAgreement            	(4),
  keyCertSign            		(5),
  cRLSign                 		(6),
  encipherOnly            	(7),
  decipherOnly            	(8) `}`
```

当设备解析证书扩展属性时，如果证书中包含keyUsage字段，那么设备就会将一个指针指向栈上的一个32位整数，将其作为输出缓冲区，然后直接调用asn1_extract_bit_string函数。

然后keyUsage扩展属性中的一个大于4字节的位串对象就会导致栈缓冲区溢出。

当asn1_extract_bit_string函数返回时，bootrom代码发现返回的大小值没有大于4字节，但此时复制操作已经完成。之后调用函数返回，将其返回地址从栈中弹出，这样攻击者就可以重定向PC寄存器，执行任意代码。

攻击者可以控制写入栈中的数据的大小及内容（即证书所包含的位串的大小及内容）。

负责解析X.509证书扩展属性的存在漏洞的代码如下图所示：

 [![](https://p4.ssl.qhimg.com/t017ba8533e1adaab1f.png)](https://p4.ssl.qhimg.com/t017ba8533e1adaab1f.png)

**3.2 SDP恢复模式中的缓冲区溢出漏洞（CVE-2017-7936）**

WRITE FILE命令处理程序中的内存检查过程存在漏洞，攻击者可以利用该漏洞实现任意代码执行。

对于USB报文，串行下载协议（SDP）使用了如下几个字段：

1、type（命令类型）

2、address（读取或写入的内存地址）

3、format（用于READ REGISTER以及WRITE REGISTER，其大小以比特表示）

4、data_count（用于WRITE FILE以及DCD WRITE，其大小以字节表示）

5、data（WRITE REGISTER所使用的数据）

在信任模式下，当处理DCD WRITE以及WRITE FILE命令时，hab_check_target函数（位于0x753C处）会检查位于address以及address + data_count之间的内存区域。

这个函数有3个参数：

1、内存的类型（0x0F表示内存，0Xf0表示硬件寄存器，0x55表示其他类型的内存）。

2、待检查的内存的基址。

3、内存区域的大小（以字节表示）。

根据待检查的内存的不同类型，函数会使用一份包含安全内存区域的白名单来检查该内存区域。

然而，这个函数并没有被正确调用，原因在于内存大小参数（来自于data_count字段）会被除以8，设备认为这是一个以比特来表示的大小值，而实际上data_count字段是以字节来表示的，这样一来，该函数只会检查目标内存中的一小部分区域。

之所以存在这个问题，原因可能是设备在处理这些命令时，逻辑上与处理READ/WRITE REGISTER命令时混淆了，后者所使用的format字段恰好是用比特来表示的。

因此，bootrom会检查[ address : address + data_count / 8 ]这个范围的内存是否正确，而实际上数据被复制到[ address, address + data_count ]这个范围的内存中。

当主机通过USB发送数据时，这个错误就会导致缓冲区溢出。

存在漏洞的代码片段如下所示：

 [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ef6ea1debb45b16f.png)

**<br>**

**四、时间线**

****

2016年9月1日：向NXP报告漏洞。

2016年9月2日：NXP表示已收到漏洞报告。

2016年9月8日：NXP请求X.509漏洞的PoC代码。

2016年9月9日：将i.MX6 bootrom X.509的漏洞利用代码发送给NXP。

2016年9月16日：NXP请求SDP漏洞的PoC代码。

2016年9月16日：将i.MX6 USB恢复模式的漏洞利用代码发送给NXP。

2017年2月20日：向高通移动安全峰会2017提交Quarkslab的演讲摘要文档。

2017年3月11日：高通询问Quarkslab是否愿意与NXP一起联合演讲，我们给出了肯定的答复。

2017年3月21日：在QMSS2017演讲摘要文档中简要提及了i.MX处理器安全启动特性中存在的漏洞。

2017年3月22日：InversePath向Quarkslab通告部分漏洞信息。

2017年3月22日：发邮件给NXP PSIRT、CERT-FR（法国）、CERT-NL（荷兰）、CERT-Bund（德国）以及ICS-CERT（美国），通告漏洞情况及部分细节。

2017年3月23日：InversePath确认i.MX53中存在x.509漏洞，并公布了一份安全公告[草案](https://github.com/inversepath/usbarmory/blob/master/software/secure_boot/Security_Advisory-Ref_QBVR2017-0001.txt)。

2017年3月23日：QMSS 2017演讲摘要文档从网站上移除，进行细节上的修正。

2017年3月24日：InversePath撤销已发布的安全公告。

2017年3月23日：NXP向QMSS发送一份修正摘要文档，其中没有提及i.MX处理器。

2017年3月24日：QMSS 2017网站上公布了修正版的摘要文档。

2017年3月24日：Quarkslab向InversePath、CERTs以及NXP发送邮件，以协调后续的公告事宜。Quarkslab告知各方会在5月19日的QMSS演讲之后，将细节公布在博客中，但如果漏洞信息已公开，这个时间点有可能会提前。

2017年5月1日：ICS-CERT询问Quarkslab是否原因推迟60天发布公告，因为他们想通过国土安全信息网络发布NXP的安全公告，时间上希望协调一致。

2017年5月2日：Quarkslab认为，这些问题向上千个私人团体公告后再推迟60天向公众公告貌似没有任何好处。询问ICS-CERT推迟公告的具体目的。

2017年5月5日：ICS-CERT回复说NXP希望给客户更多的时间调整受影响的产品，同时漏洞的公布过程也会变得更加可控。

2017年5月10日：Quarkslab回复ICS-CERT，认为推迟60天公布对受影响的组织降低安全风险而言没有任何好处，计划于5月19日（QMSS 2017上发表联合演讲）后的1周内发布文章介绍漏洞细节。

2017年5月19日：Quarkslab与NXP在QMSS 2017发表联合演讲。

2017年5月19日：在QMSS 2017的面对面会议上，NXP要求Quarkslab推迟60天公布漏洞细节。NXP表示这是客户的请求，并告诉Quarkslab他们已经通告所有客户，通告中涉及所有受影响的i.MX产品。Quarkslab要求NXP提供通告文档以及他们通知客户的具体证据，以评估是否需要落实该请求。此外，Quarkslab要求NXP向其转发NXP客户延迟公告的请求。

2017年5月22日：NXP表示，他们于4月27日向客户发布了公告，于4月21日向Auto ISAC组织公布了一个安全公告，帮助ICS CERT制作用于国土安全信息网络的安全公告。NXP提供了通知客户的截图以及本文中提到过的工程简报以及勘误文档。

2017年5月30日：收到所有文档后，Quarkslab同意本文推迟到2017年7月18日再发表，并向所有组织（CERTs、NXP以及InversePath）通报了这一决定。

2017年6月5日：InversePath重新发布了之前于3月23日发布过的初步安全公告。

2017年6月6日：ICS-CERT为这些漏洞分配了CVE编号。

2017年7月19日：本文发表。



**五、参考资料**

****

[1][http://www.nxp.com/products/microcontrollers-and-processors/arm-processors/i.mx-applications-processors:IMX_HOME](http://www.nxp.com/products/microcontrollers-and-processors/arm-processors/i.mx-applications-processors:IMX_HOME)

 [2][https://qct-qualcomm.secure.force.com/QCTConference/GenericSitePage?eventname=2017Security&amp;page=Summit%20Information](https://qct-qualcomm.secure.force.com/QCTConference/GenericSitePage?eventname=2017Security&amp;page=Summit%20Information)

 [3][http://www.nxp.com/support/support/documentation:DOCUMENTATION](http://www.nxp.com/support/support/documentation:DOCUMENTATION)

 [4][https://boundarydevices.com/product/sabre-lite-imx6-sbc/](https://boundarydevices.com/product/sabre-lite-imx6-sbc/)

 [5][http://www.nxp.com/docs/en/application-note/AN4581.pdf](http://www.nxp.com/docs/en/application-note/AN4581.pdf)

 [6][https://inversepath.com/usbarmory](https://inversepath.com/usbarmory)

 [7][https://github.com/inversepath/usbarmory/blob/master/software/secure_boot/Security_Advisory-Ref_QBVR2017-0001.txt](https://github.com/inversepath/usbarmory/blob/master/software/secure_boot/Security_Advisory-Ref_QBVR2017-0001.txt)
