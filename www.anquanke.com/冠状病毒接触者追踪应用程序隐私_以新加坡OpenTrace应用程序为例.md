> 原文链接: https://www.anquanke.com//post/id/216695 


# 冠状病毒接触者追踪应用程序隐私：以新加坡OpenTrace应用程序为例


                                阅读量   
                                **229481**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Douglas J. Leith, Stephen Farrell，文章来源：scss.tcd.ie
                                <br>原文地址：[https://www.scss.tcd.ie/Doug.Leith/pubs/opentrace_privacy.pdf](https://www.scss.tcd.ie/Doug.Leith/pubs/opentrace_privacy.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01761bd164f6fcdf3e.jpg)](https://p3.ssl.qhimg.com/t01761bd164f6fcdf3e.jpg)



本文报告了新加坡OpenTrace应用程序传输到后端服务器的实际数据的分析结果，以评估对用户隐私的影响。已经对OpenTrace应用程序以及在新加坡部署的相关封闭式SourceTraceTogether应用程序的一个版本进行了初步研究。发现使用Google的Firebase Analytics服务意味着OpenTrace发送的数据有可能允许Google随时间跟踪用户手机（基于IP）的位置。还发现OpenTrace将用户电话号码存储在Firebase Authentication服务中。

Firebase身份验证的这种使用会给Google带来明显的潜在利益冲突，而Google的主要业务是基于收集用户个人数据进行广告宣传。此外，即使用户位于其他国家/地区，Firebase Authenticationservice也会在美国数据中心处理其数据。最后，注意到OpenTraceire依赖于存储在GoogleCloud服务中的单个长期密钥，因此很容易泄露此密钥。计划在未来进一步研究此应用程序和类似应用程序的隐私，安全性和有效性，但强烈建议任何打算使用基于OpenTrace的应用程序的人在部署之前解决这些重要问题。



## 0x01 Introduction

目前，人们对使用移动应用程序来促进Covid-19接触追踪非常感兴趣。例如，更有效和可扩展的接触者跟踪可以使许多国家当前采取的锁定措施更加迅速地放宽。

确保接触者跟踪应用程序维护用户隐私已被广泛认为是一个主要问题。从隐私的角度来看，基于蓝牙的接近度检测方法很有吸引力，因为它们避免了记录或共享用户位置的需要。但是，在实施这些方法时需要格外小心，以确保实际实现隐私目标。此外，对已开发应用程序的独立评估对于验证隐私声明和建立用户对应用程序确实可以安全使用的信心都很重要。在本报告中朝着这个方向迈出了第一步。评估由新加坡TraceTogether / OpenTrace应用程序传输到后端服务器的实际数据，以评估用户隐私。

移动应用已在多个国家/地区用于协助管理Covid-19感染防御。这些应用程序中的大多数要么用于控制人员的活动，要么用于帮助人员根据观察到的症状对其健康进行初步的自我评估，而不是用于接触者追踪。前者的一个著名例子是中国卫生法规应用程序，而后者的一个例子是西班牙自我评估应用程序。值得注意的是，某些国家/地区使用集中式的手机位置跟踪功能，从而避免了使用专门的应用程序来控制人员移动的需求，例如：台湾的“电子围栏”。在韩国，有关受感染者访问的位置的信息已公开提供，这促使开发显示此信息的应用程序，例如Corona 100m应用。

相反，在Covid-19爆发的最初阶段，新加坡政府开发了TraceTogether应用程序，并使用该应用程序直接协助了接触者追踪。 TraceTogether应用程序使用蓝牙广播信标，同时还记录从相邻手机接收到的信标的信号强度。由于接收到的信号强度是接近程度的粗略指标，当一个人被检测到被感染时，他们手机上记录的数据可以用来识别其他人 可能在发现他们感染的前一段时间接近。在欧洲，也已经提出了基于蓝牙的合同跟踪方法，例如。分散式隐私保护近距离跟踪（DP-3T），而苹果和谷歌已经建立合作伙伴关系，以开发基于蓝牙的合同跟踪API。但是，这些举措目前还处于初期阶段，而新加坡TraceTogether应用程序已经部署并投入运行，加上称为OpenTrace的开源版本，现已发布。因此，TraceTogether / OpenTrace当前是人们关注的焦点。

发现OpenTrace应用程序使用Google的Firebase服务来存储和管理用户数据。这意味着处理由该应用程序共享的数据涉及两个主要方面，即Google（运行Firebase服务的人）和运行OpenTrace应用程序本身的卫生机构（或其他机构）。作为Firebase的所有者，Google可以访问该应用程序通过Firebase传输的所有数据，但可以过滤OpenTrace运营商可以使用的数据，例如仅显示汇总统计信息。

OpenTrace应用程序会定期将遥测数据发送到Firebase Analytics服务。该数据用链接到移动手机的永久性标识符标记，以便可以将来自同一手机的消息链接在一起。此外，消息还必须包含手机IP地址（或上游网关的IP地址），可用作使用现有geoIP服务进行位置定位的粗略代理。请注意，Firebase Analytics文档指出“ Analytics会从以下位置获取位置数据用户的IP地址”。因此，手机发送的数据有可能随时间推移跟踪其位置。许多研究表明，随着时间的推移链接的位置数据可用于取消匿名处理：这并不奇怪，因为例如可以从此类位置数据推断用户的工作和住所位置（基于用户主要在哪里消费） （白天和晚上的时间），并且当与其他数据结合使用时，该信息会很快变得十分清晰。

Firebase Analytics文档指出：“使用旧版本可防止查看报告的任何人推断个人用户的受众特征，兴趣或位置” 。假设这是有效的（请注意，随着时间的推移，去匿名方法应用于位置数据的有效性还远远不够明确），那么运行OpenTrace应用的卫生机构将无法推断出各个用户的位置。因此，主要的隐私问题在于Google自己保留大致的位置数据。值得注意的是，当可以从收集到的数据中推断出位置历史时，即使该推断不是由收集数据的组织做出的，也可能由共享数据的其他方做出。这包括商业合作伙伴（他们可能会将其与他们拥有的其他数据相关联）和国家机构，以及通过数据违规进行披露。

鉴于此，并且由于潜在使用合同竞标应用程序进行大规模人口追踪是媒体上突出显示的主要隐私问题之一，因此建议禁用OpenTrace中的Firebase Analytics，以避免将消息定期传输给Google。

OpenTrace要求用户输入他们的电话号码才能使用该应用程序，并且此号码存储在Firebase上，并可以向卫生机构显示。将电话号码链接到用户的真实身份相对容易（在某些司法管辖区，购买模拟卡时必须提供ID），因此这引起了直接的隐私问题。 BlueTrace白皮书指出，用户电话号码的存储是可选的，而可以使用推送通知。因此，是否要求用户电话号码（或其他标识符）的决定实际上取决于卫生当局对有效管理接触者跟踪的要求。例如，由于经由蓝牙的接近度跟踪的近似性质，OpenTrace数据很可能仅是接触者跟踪中使用的许多信息源之一，并且组合来自不同源的数据可能需要使用标识符（例如电话号码）。结果可能是隐私与接触追踪有效性之间的直接权衡。

假设需要记录电话号码或类似标识符，则OpenTrace为此使用Firebase身份验证服务。 Firebase身份验证的这种使用会给Google带来明显的潜在利益冲突，该Google的主要业务是基于用户个人数据的收集来做广告。此外，Google持有的数据不必存储在应用程序用户所在的国家/地区。特别是，Firebase隐私文档指出，OpenTrace使用的Firebase身份验证服务始终在美国数据中心内处理其数据。考虑到成功的接触者跟踪应用程序将被一个国家中的很大一部分人使用，因此使用Firebase身份验证可能意味着其电话号码可能可供美国各州机构使用。这些考虑因素表明，可能值得考虑更改OpenTrace，以利用避免将用户电话号码存储外包给Google的后端基础结构。



## 0x02 Threat Model

要注意，将用户数据传输到后端服务器本质上不是隐私入侵。例如，共享用户设备型号/版本的详细信息以及设备的地区/国家/地区的详细信息可能很有用，并且如果此数据对于许多用户来说是通用的，则这几乎不会带来隐私风险，因为数据本身无法轻松地链接回特定用户。

但是，当数据可以绑定到特定用户时，就会出现问题。发生这种情况的一种常见方式是，当应用程序首次安装/启动时生成一个长随机字符串，然后将其与其他数据一起传输。然后，随机字符串充当应用程序实例的标识符（因为没有其他应用程序共享相同的字符串值），并且当在多个传输中使用相同的标识符时，它允许这些传输跨时间绑定在一起。

将一系列传输链接到应用程序实例并不能明确显示用户的真实身份。但是，通常可以轻松地对数据进行匿名处理。发生这种情况的一种方式是，如果应用程序直接询问用户详细信息（例如电话号码，facebook登录）。但是，使用应用程序的传输始终包含用户设备（或更可能是上游NAT网关）的IP地址这一事实，也可能间接发生这种情况。如前所述，IP地址通过现有的geoIP服务充当用户位置的粗略代理，许多研究表明，随着时间的推移链接的位置数据可用于取消匿名。这里的一个相关因素是发送更新的频率，例如每天记录一次IP地址位置的可能性要比每隔几分钟记录一次的可能性小得多。

考虑到这些问题，在本研究中尝试回答的两个主要问题是：（i）应用程序直接请求哪些明确的标识数据；（ii）应用程序传输至后端服务器的数据是否可能允许跟踪应用实例的IP地址随时间变化。



## 0x03 Measurement Setup

### <a class="reference-link" name="A.%E6%9F%A5%E7%9C%8B%E5%8A%A0%E5%AF%86%E7%9A%84Web%E8%BF%9E%E6%8E%A5%E7%9A%84%E5%86%85%E5%AE%B9"></a>A.查看加密的Web连接的内容

感兴趣的所有网络连接均已加密。为了检查连接的内容，通过控制的WiFi接入点（AP）路由手机流量配置此AP以使用mitmdump作为代理，并调整防火墙设置以将所有WiFi流量重定向到mitmdump，以便代理透明简而言之，当OpenTrace应用启动新的Web连接时，mitmdump代理会假装为目标服务器，并为目标服务器出示伪造的证书。这允许mitmdump解密流量。然后，它会创建与实际目标服务器的向前连接，并充当中介，在记录流量时在应用程序和目标服务器之间中继请求及其答复。该设置如下图所示。

[![](https://pic.downk.cc/item/5f54cc6a160a154a671a1fab.png)](https://pic.downk.cc/item/5f54cc6a160a154a671a1fab.png)

使用此设置时遇到的直接困难是，应用程序在启动新连接时对接收到的服务器证书的真实性进行检查，并在这些检查失败时中止连接。为了规避这些检查，使用植根电话并使用Frida快速修补OpenTrace应用程序和Google Play服务（该应用程序用来管理其建立的大多数连接），以使用始终报告的虚拟功能替换相关的Java证书验证功能。验证检查已通过。由于Google Play服务是封闭源代码且被混淆（由于反编译字节码会产生带有随机类和变量名的Java字节码），加上要使用自定义的证书检查代码（因此标准的取消固定方法失败），因此需要做的大部分工作都在于推导要修补的功能。因此，实现OpenTrace的取消固定是一个相当费力的手动过程。

### <a class="reference-link" name="B.%E4%BD%BF%E7%94%A8%E7%9A%84%E7%A1%AC%E4%BB%B6%E5%92%8C%E8%BD%AF%E4%BB%B6"></a>B.使用的硬件和软件

手机：运行Android 9的Google Pixel2。使用Magisk v19.1和Magisk Manager v7.1.2以及运行Frida Server v12.5.2 root。笔记本电脑：运行Mojav10.14.6，运行Frida 12.8.20和mitmproxy v5.0.1的Apple Macbook。使用USB以太网适配器，可将便携式计算机连接到电缆调制解调器，然后连接到互联网。笔记本使用其内置的互联网共享功能进行配置，以充当WiFi AP来通过有线连接路由无线流量。然后，将笔记本防火墙配置为通过将bridge100 inetproto tcp上的rdr pass规则添加到任何端口80、443-&gt; 127.0.0.1port 8080，将接收到的WiFi流量重定向到在端口8080上进行监听的mitmproxy。听筒也通过USB连接到便携式计算机并将其用作控制通道（此连接上没有路由数据通信）安装OpenTrace应用并使用Frida进行动态修补。即，使用theadb外壳，在手机上启动Frida服务器，然后通过Frida客户端从笔记本电脑进行控制。

### <a class="reference-link" name="C.%E6%B5%8B%E8%AF%95%E8%AE%BE%E8%AE%A1"></a>C.测试设计

由于OpenTrace应用程序仅支持单个用户交互流程，因此测试设计非常简单。即，在首次启动时，将短暂显示启动屏幕，然后显示包含单个“I want to help”按钮的信息屏幕。按下此按钮后，用户将转到第二个屏幕，该屏幕概述了OpenTrace的工作方式，并具有一个标有“ Great !!!”的单个按钮。按下此按钮，要求用户输入他们的电话号码，并且再次只有一个标记为“获取OTP”的按钮。然后，将用户带到一个屏幕，在该屏幕上要求他们输入已发短信给提供的数字的6位代码。按下“验证”按钮后，如果此代码有效，则会通过几个屏幕引导用户，然后要求提供所需的权限（蓝牙，位置，禁用应用程序的电池优化，访问存储），然后到达主屏幕。之后显示，请参见下图。此主屏幕上有无法使用的帮助和共享应用程序按钮，以及仅在确认用户已感染Covid-19并向观察到的蓝牙数据上载到Firebase上托管的应用程序后端服务器后才按下的按钮。

[![](https://pic.downk.cc/item/5f54cc7b160a154a671a2444.png)](https://pic.downk.cc/item/5f54cc7b160a154a671a2444.png)

因此，测试包括记录在安装和启动应用程序时发送的数据，然后在这些屏幕之间导航，直到到达主屏幕。在主屏幕（可能是应用程序的主要操作模式）上闲置时，由应用程序发送的数据也会被记录。还尝试调查按上载功能后发送的数据，但发现该功能失败并显示错误。对代码进行检查表明该上载功能不完整。

尽管主要兴趣是开源OpenTraceapp，但该应用程序显然来自新加坡卫生服务所使用的closed-sourceTraceTogether应用程序，因此还尝试收集TraceTogether应用程序的数据以与OpenTrace应用程序生成的数据进行比较TraceTogether的最新版本（v1.6.1）限于新加坡电话号码，因此在测试中，使用了较早的版本（v1.0.33）没有此限制。

### <a class="reference-link" name="D.%E5%9C%A8%E7%BD%91%E7%BB%9C%E8%BF%9E%E6%8E%A5%E4%B8%AD%E6%9F%A5%E6%89%BE%E6%A0%87%E8%AF%86%E7%AC%A6"></a>D.在网络连接中查找标识符

通过手动检查提取了网络连接中的潜在标识符。基本上，网络消息中存在的，在消息之间保持不变的任何值都被标记为潜在标识符。将看到，几乎所有感兴趣的值都与Google Play服务中的Firebase API相关联。因此，尝试从Firebase隐私政策和其他公共文档中找到观察值性质的更多信息，以及将它们与已知软件和设备标识符（例如，手机的Google广告标识。



## 0x04 Google Firebase

OpenTrace使用Google的Firebase服务提供其服务器后端。这意味着，至少有两个参与方处理该应用程序共享的数据，即Google（运行Firebase服务基础结构）和运行OpenTrace应用程序本身的卫生机构（或其他机构）。作为Firebase的所有者，Google可以访问该应用程序通过Firebase传输的所有数据，但可以过滤OpenTrace运营商可以使用的数据，例如仅显示汇总统计信息。

OpenTrace使用Firebase身份验证，FirebaseFunctions，Firebase存储和Firebase Analytics（也称为Google Analytics for Firebase）服务。该应用程序具有Crashlytics和Firebase远程配置的挂钩，但是此处研究的版本并未主动使用这两个服务。

在启动应用程序时使用Firebase身份验证服务来记录用户输入的电话号码，并通过向用户发送代码后输入验证码来进行验证。输入的电话号码由Firebase记录并链接到Firebase标识符。

Firebase Functions允许OpenTrace应用通过将请求发送到指定的网址来在Google的云平台上调用用户定义的Javascript函数的执行。 TheOpenTrace应用程序使用此服务生成tempID，以通过蓝牙进行广播并上传记录的tempID，当用户感染Covid-19时。 FirebaseStorage用于保存上传的tempID。 tempID是使用存储在Google Cloud的Secret Manager服务中的密钥通过可逆加密（请参见下文）生成的，并由FirebaseFunctions上托管的OpenTrace getTempIDs函数进行访问。

[![](https://pic.downk.cc/item/5f54cc89160a154a671a2788.png)](https://pic.downk.cc/item/5f54cc89160a154a671a2788.png)

上图显示了Firebase函数日志记录的示例，OpenTrace应用程序的操作员可以看到该示例。此细粒度的记录数据显示了各个函数调用以及时间和用户进行的调用（uid值是Firebase身份验证使用的用户标识符，因此可以直接链接到用户的电话号码）。<br>
该应用程序可以记录各种用户事件，并使用Firebase Analytics将这些事件记录到后端服务器。

Firebase隐私文档概述了在API操作期间与Google交换的一些信息。本隐私权文档未说明Firebase Storage记录的内容，但指出Firebase身份验证记录用户的电话号码和IP地址。此外，Firebase Analytics还使用许多标识符，包括：（i）用户可重置的移动广告ID “允许开发人员和营销人员跟踪广告目的的活动。它们还用于增强投放和定位功能。” ，（ii）一个Android ID，它是“ 64位数字（表示为十六进制字符串），对于应用程序签名密钥，用户和设备的每种组合都是唯一的” ，（iii）实例ID “为每个实例提供唯一的标识符”和“一旦生成实例ID，库就会定期将有关应用程序和运行设备的信息发送到Firebase后端。 ” ，（iv）一个“用于在整个Google Analytics（分析）中计算用户指标”的Analytics（分析）应用实例ID。

Firebase Analytics文档指出：“只要您使用FirebaseSDK，就无需编写任何其他代码即可自动收集许多用户属性”，包括年龄，性别，兴趣，语言，国家/地区以及其他设备信息。它还指出“ Analytics从用户的IP地址获取位置数据”。

[![](https://pic.downk.cc/item/5f54cc9c160a154a671a2b74.png)](https://pic.downk.cc/item/5f54cc9c160a154a671a2b74.png)

上图显示了Firebase Analytics提供给OpenTrace应用程序操作员的数据示例。可以看到每个设备的事件数据可用，例如显示何时在设备上启动OpenTrace，何时查看OpenTrace等。

Google在运行Firebase服务期间收集的数据不必与应用程序用户所在的国家/地区存储在一起。 Firebase隐私文档指出：“除非服务或功能提供了数据位置选择，否则Firebase可能会在Google或其代理商维护设施的任何地方处理和存储您的数据”。它还指出：“一些Firebase服务仅从美国数据中心运行。因此，这些服务仅在美国处理数据”，并且看起来这些服务包括FirebaseAuthentication，OpenTrace用来存储用户电话号码。

重要的是要注意，只有backendFirebase服务的用户才能使用Google收集的此数据的过滤版本。 Firebase Analytics文档指出：“应用阈值是为了防止任何查看areport的人推断个人用户的人口统计信息，兴趣或位置” 。



## 0x05 Cryptography

OpenTrace中使用的tempId在Bluetoothbeacon中传输，是Firebase用户标识符的加密形式，可以使用Firebase身份验证服务将其链接到用户电话号码，并带有两个时间戳，指示tempID有效的时间间隔（以减轻重放）攻击。

在OpenTrace中，加密基于存储在Google Cloud的Secret Manager服务中的一个长期对称秘密。加密是可逆的，因此，在知道此机密的情况下，可以从观察到的tempID中恢复用户标识符和时间戳。因此，当检测到某人感染了Covid-19时，卫生部门可以解密在其手机上的应用程序所观察到的tempID信标，以获取已接近该感染者的人员的电话号码。如果发生数据泄露并泄露了机密，则蓝牙信标中观察到的任何tempID记录也可以由第三方解密。确保仅解密与与Covid-19测试为阳性的用户相关联的tempId可以解密的替代设计似乎更为可取。添加用于密钥更新和其他密钥管理的准备也很重要，而OpenTrace当前不提供这种准备。



## 0x06 Measurements of Data Transmitted by OpenTrace App

### <a class="reference-link" name="A.%E5%88%9D%E5%A7%8B%E5%90%AF%E5%8A%A8%E6%97%B6%E5%8F%91%E9%80%81%E7%9A%84%E6%95%B0%E6%8D%AE"></a>A.初始启动时发送的数据

安装并首次启动后，OpenTrace应用程序会建立许多网络连接。请注意，除了启动应用程序外，没有与用户进行任何交互，尤其是没有用户同意共享信息。

该应用程序在首次启动时会初始化Firebase，并生成以下POST请求（忽略标准/无趣的参数s / header）：

[![](https://pic.downk.cc/item/5f54ccad160a154a671a2e80.png)](https://pic.downk.cc/item/5f54ccad160a154a671a2e80.png)

参数“ key”的值被硬连线到应用程序中，以允许其访问Firebase，对于该应用程序的所有实例也是如此。同样，X-Android-Cert标头是应用程序的SHA1hash，“ appId”是Google应用程序标识符，并且对于该应用程序的所有实例而言都是相同的。该应用程序发出的许多网络请求中都出现了“关键”参数和X-Android-Cert，但为节省空间，此后就省略了。 “ fid”值似乎是上面讨论的Firebase实例ID。这会唯一标识该应用程序的当前实例，但会在更改后重新安装该应用程序（即删除该应用程序然后重新安装）。此请求的响应将回显fid值，并包含两个令牌，这些令牌似乎用于标识当前会话。接下来，OpenTrace尝试获取Crashlytics的设置：

[![](https://pic.downk.cc/item/5f54ccba160a154a671a31be.png)](https://pic.downk.cc/item/5f54ccba160a154a671a31be.png)

“ instance”参数不同于fid，它的值在应用程序全新安装时会发生变化。类似地，X-CRASHLYTICS-INSTALLATION-ID值在全新安装时也会发生变化。这两个值似乎用于标识Crashlytics（和theapp）的实例。 “显示版本”参数是应用程序源代码中BuildConfig.java中的OpenTrace版本名称值，并且对于该应用程序的所有副本均相同。目前尚不清楚X-CRASHLYTICS-DEVELOPER-TOKEN，X CRASHLYTICS-API-KEY和图标哈希值是什么，但是在重新安装应用程序时观察到它们保持不变，因此似乎与应用程序实例无关。由于尚未在Firebaseserver后端中配置Crashlytics，因此对settings.crashlytics.com的请求响应为“ 403 Forbidden”。OpenTrace现在首次调用Firebase Analytics：

[![](https://pic.downk.cc/item/5f54ccc8160a154a671a34fd.png)](https://pic.downk.cc/item/5f54ccc8160a154a671a34fd.png)

第一个请求似乎在询问有关配置更改的消息，响应为“ 304 Not Modified”。第二个请求上传有关应用程序内事件的信息（请参见下文以进行进一步讨论）。这两个请求都包含一个app实例ID值，该值可将它们链接在一起（以及后续的分析请求）。第二个请求还包含Firebase fid值。此外，第二个请求包含手机设置应用程序的Google / Ads部分报告的设备Google Advertising ID（1d2635f5-2af7-4fb3-86e …）。除非由用户手动重置，否则该值将无限期存在，包括在新安装的OpenTrace中，因此从本质上讲是该设备及其用户的强标识符。第二个请求的主体包含许多其他值。有些识别出该应用程序的版本，因此并不敏感，但是其他值的出处对作者而言是未知的。

### <a class="reference-link" name="B.%E8%BE%93%E5%85%A5%E7%94%B5%E8%AF%9D%E5%8F%B7%E7%A0%81%E5%90%8E%E5%8F%91%E9%80%81%E7%9A%84%E6%95%B0%E6%8D%AE"></a>B.输入电话号码后发送的数据

初始启动后，在前两个信息屏幕中导航不会产生任何网络连接。在此屏幕上，应用程序要求用户输入他们的电话号码。完成此操作后，按按钮进行以下网络连接。第一个连接将电话号码发送到Firebase：

[![](https://pic.downk.cc/item/5f54ccd7160a154a671a3817.png)](https://pic.downk.cc/item/5f54ccd7160a154a671a3817.png)

目前尚不清楚如何生成X-Goog-Spatula值，但它似乎至少部分由base64编码的信息组成，因为base64解码会产生“ 6？io.bluetrace.opentrace？KuS + 2eTwbmFXe / 8epaO9wF8yVTE =”，然后是其他二进制数据。

Firebase现在向输入的电话号码发送6位数的代码文本，OpenTrace应用要求用户输入此代码。输入代码将生成以下网络连接：

[![](https://pic.downk.cc/item/5f54cce6160a154a671a3b78.png)](https://pic.downk.cc/item/5f54cce6160a154a671a3b78.png)

X-Goog-Spatula标头值与之前的请求相同，因此可用于将它们链接在一起（也许是一种简短的会话ID）。 AM5PThB …值来自对第一个请求的响应，并可能以服务器可以解码的方式对6位数的值进行编码，以便与用户输入的值进行比较。

正确的6位数代码的响应会告知应用程序Firebase使用的用户ID值yEszgPWm …（在Firebase仪表板上可见并直接链接到用户电话号码），以及许多其他值，包括在以下请求的主体中使用的似乎是用户标识符/身份验证令牌：

[![](https://pic.downk.cc/item/5f54cd5a160a154a671a597f.png)](https://pic.downk.cc/item/5f54cd5a160a154a671a597f.png)

响应中包含用户先前输入的电话号码以及用户ID值yEszgPWm …，有时还包含时间戳（可能与帐户创建等相关联）。此时，已在Firebase上成功创建/验证了该用户的帐户，并且现在使用OpenTrace Firebase Functions服务请求一批tempID：

[![](https://pic.downk.cc/item/5f54cd67160a154a671a5d12.png)](https://pic.downk.cc/item/5f54cd67160a154a671a5d12.png)

响应为json的14KB：

[![](https://pic.downk.cc/item/5f54cd77160a154a671a6061.png)](https://pic.downk.cc/item/5f54cd77160a154a671a6061.png)

然后，OpenTrace调用由Firebase Functions托管的getHandshakePin函数：

[![](https://pic.downk.cc/item/5f54cd82160a154a671a632d.png)](https://pic.downk.cc/item/5f54cd82160a154a671a632d.png)

并且响应包含操作该应用程序的健康服务需要提供给用户的PIN，以确认他们应要求该应用程序将观察到的tempID上载到Firebase Storage。

### <a class="reference-link" name="C.%E6%8E%88%E4%BA%88%E6%9D%83%E9%99%90%E6%97%B6%E5%8F%91%E9%80%81%E7%9A%84%E6%95%B0%E6%8D%AE"></a>C.授予权限时发送的数据

输入并验证电话号码后，该应用会询问用户使用蓝牙，位置以及禁用OpenTrace电池优化的权限。这些动作不会生成任何网络连接。最后，OpenTrace要求获得访问手机上文件存储的权限。授予此权限后，OpenTrace将再次调用[https://europe-west1-opentracetest-4167b.cloudfunctions.net/getTempIDs](https://europe-west1-opentracetest-4167b.cloudfunctions.net/getTempIDs) 并接收另一批tempID作为响应。

### <a class="reference-link" name="D.%E9%97%B2%E7%BD%AE%E5%9C%A8%E4%B8%BB%E5%B1%8F%E5%B9%95%E4%B8%8A%E6%97%B6%E5%8F%91%E9%80%81%E7%9A%84%E6%95%B0%E6%8D%AE"></a>D.闲置在主屏幕上时发送的数据

一旦完成OpenTrace的启动，它将在主屏幕上处于空闲状态，直到用户使用为止，并且在这种操作模式下，它会花费大量时间。大约每小时观察到一次OpenTrace与Firebase Analytics建立了一对连接。这与Firebase Analytics文档一致，该文档指出“当客户端库发现有一个小时的本地数据时，将对分析数据进行批处理并发送出去。”和“在具有Play服务的Android设备上，这一个小时的计时器适用于所有使用Firebase Analytics的应用程序。”这对的第一个连接是：

[![](https://pic.downk.cc/item/5f54cd90160a154a671a66f0.png)](https://pic.downk.cc/item/5f54cd90160a154a671a66f0.png)

似乎正在检查更新，响应为“ 304 Not Modifified”。

第二个连接也连接到app-measurement.com并显示为发送遥测数据，记录用户与该应用的交互。当配置为详细日志记录时，Firebase会将上传的数据的详细信息写入手机日志中，可以使用“ adb logcat”命令通过与手机的USB连接进行检查。一个典型的条目日志条目开始如下：

[![](https://pic.downk.cc/item/5f54cd9f160a154a671a6a84.png)](https://pic.downk.cc/item/5f54cd9f160a154a671a6a84.png)

检查通过网络传输到Firebase的消息显示以下部分形式：

[![](https://pic.downk.cc/item/5f54cdc1160a154a671a71fc.png)](https://pic.downk.cc/item/5f54cdc1160a154a671a71fc.png)

在其中可以标识日志中的许多值，包括firebase实例ID，应用实例ID，可重设设备ID（Google广告ID）。每个手机日志条目还包括以下格式的一系列用户属性值：<br>
随后是一系列的事件条目，形式为:

[![](https://pic.downk.cc/item/5f54cdcf160a154a671a7546.png)](https://pic.downk.cc/item/5f54cdcf160a154a671a7546.png)

后面是表单的事件条目序列:

[![](https://pic.downk.cc/item/5f54cddd160a154a671a77db.png)](https://pic.downk.cc/item/5f54cddd160a154a671a77db.png)

并且也可以在OpenTrace发送给Firebase Analytics的邮件正文中进行标识。

### <a class="reference-link" name="E.TraceTogether%E5%8F%91%E9%80%81%E7%9A%84%E6%95%B0%E6%8D%AE%EF%BC%88v1.0.33%EF%BC%89"></a>E.TraceTogether发送的数据（v1.0.33）

使用了新加坡政府当前使用的封闭式源跟踪总计应用程序重复了上述分析。总之，观察到与OpenTrace相似的行为，但有以下差异：

1）首次启动后，未观察到TraceTogether从Firebase下载tempID。大概这些至少是在应用程序本地生成的。

2）TraceTogether调用asia-east2-govtech-tracer.cloudfunctions.net/getBroadcastMessage， 即调用托管在Firebase Functions上但在OpenTrace中不存在的get BroadcastMessage函数。

3）TraceTogether调用了firebaseremoteconfig.googleapis.com，因此大概利用了Firebase远程配置服务（如前所述，OpenTrace中有用于此的hook，但这些hook未激活）。



## 0x07 Sumarry and Conclusion

已经对OpenTrace应用程序以及在新加坡部署的相关封闭式SourceTraceTogether应用程序的一个版本进行了初步研究。发现使用Google的Firebase Analytics服务意味着OpenTrace发送的数据有可能允许Google随时间跟踪用户手机（基于IP）的位置。还发现OpenTrace将用户电话号码存储在Firebase Authentication服务中。 Firebase身份验证的这种使用会给Google带来明显的潜在利益冲突，而Google的主要业务是基于收集用户个人数据进行广告宣传。此外，即使用户位于其他国家/地区，Firebase Authenticationservice也会在美国数据中心处理其数据。最后，注意到OpenTraceire依赖于存储在GoogleCloud服务中的单个长期密钥，因此很容易泄露此密钥。计划在未来几周内进一步研究此应用程序和类似应用程序的隐私，安全性和有效性，但强烈建议任何打算使用基于OpenTrace的应用程序的人在部署之前解决这些重要问题。

有三个主要发现：

1）OpenTrace应用程序使用Google的Firebase服务来存储和管理用户数据。这意味着处理从该应用程序传输的数据涉及两个主要方面，即Google和运行OpenTrace应用程序本身的卫生机构。发现OpenTrace使用Firebase Analytics遥测技术意味着OpenTrace发送的数据有可能允许Google随时间跟踪用户手持设备（基于IP）的位置。因此，建议修改OpenTrace以禁用Firebase Analytics。

2）OpenTrace当前还要求用户提供电话号码才能使用该应用程序，并使用Firebase身份验证服务来验证和存储输入的电话号码。询问用户电话号码（或其他标识符）的决定可能反映了追踪者希望主动呼叫已测试为阳性的接触者。其他的设计让这些接触者意识到阳性测试，将其后操作留给接触者。这可能表明在隐私和接触者跟踪的有效性之间进行了直接权衡。如果认为需要存储电话号码，建议更改OpenTrace以避免为此使用Firebase身份验证。

3）OpenTrace中使用的可逆加密依赖于存储在Google Cloud服务中的单个长期密钥，因此很容易泄露此密钥。
