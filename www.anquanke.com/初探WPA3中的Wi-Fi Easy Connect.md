> 原文链接: https://www.anquanke.com//post/id/150324 


# 初探WPA3中的Wi-Fi Easy Connect


                                阅读量   
                                **255108**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01466131adfba3d3d5.png)](https://p3.ssl.qhimg.com/t01466131adfba3d3d5.png)

前些日子，Wi-Fi联盟组织正式宣布推出新的安全标准WPA3，其通过从头设计来解决WPA2存在的技术缺陷，缓解如KRACK攻击和DEAUTH等无线攻击带来的影响。

WPA3为支持Wi-Fi的设备进行了重点改动，大大增强了配置、身份验证和加密等功能。该标准同样包括Person、Enterprise两种模式，同时还可以应用于物联网领域。

新标准带来的改进包括：
1. 对小型网络使用的 WPA3-Personal进行了优化，从而可以抵御字典攻击。与通过4次握手进行身份验证的WPA2不同，WPA3将使用同步身份验证（SAE），这种协议既可以加强密钥交换时的安全性，又可以保护数据流量。
1. 针对企业环境使用的WPA3-Enterprise改进了加密标准，将密码算法提升至192位。
1. Wi-Fi CERTIFIED Enhanced Open（增强型开放式网络）。针对被动窃听攻击，其对开放式网络提供了保护。Wi-Fi Enhanced Open基于OWE（Opportunistic Wireless Encryption），为每位用户提供单独的加密，以保证用户设备与接入点间的通信安全。
<li>发布了Wi-Fi Easy Connect，这是一种适用于WPA2和WPA3网络的新型连接协议，用户可以通过扫描QR码的形式将没有显示界面的设备添加至网络。<br>[![](https://p1.ssl.qhimg.com/t01a0bcec6849c3ce79.png)](https://p1.ssl.qhimg.com/t01a0bcec6849c3ce79.png)
</li>
本文讨论的重点便是Wi-Fi Easy Connect。



## 一、Wi-Fi 与 IEEE802.11

802.11标准是由美国电气和电子工程协会（Institute of Electrical and Electronics, IEEE）负责管理。由于其比较复杂，标准更新也非常缓慢，于是在众多设备制造商的推动下成立了Wi-Fi联盟。

Wi-Fi联盟的主要工作是确保所有具有Wi-Fi认证标志的产品能共同工作，当802.11协议出现任何模糊的概念时Wi-Fi联盟将给出推荐实现。另外，Wi-Fi联盟还允许供应商实现一些草案标准，最著名的例子是Wi-Fi保护访问（WPS）。

简单来说，大家常听见的 Wi-Fi 标准实际上是 IEEE 802.11 标准中的一个子集，其由 Wi-Fi 联盟负责管理。基于两套系统的密切相关，也常有人把 Wi-Fi 当做 IEEE 802.11 标准的同义术语。Wi-Fi 还经常被写成 WiFi 或 Wifi ，但是它们并没有被 Wi-Fi 联盟认可。同时，并不是每样符合IEEE 802.11的产品都申请了 Wi-Fi 联盟的认证，缺少 Wi-Fi 认证的产品也并不一定意味著不兼容Wi-Fi设备。



## 二、Wi-Fi Easy Connect简介

随着近些年来智能家居和物联网行业的高速发展，不再局限于笔记本电脑和手机，音响、门锁、插座、空调、窗帘等设备也都开始具有了Wi-Fi功能。这类新设备往往都没有用户界面，使得将其配置与Wi-Fi网络进行连接变得非常麻烦。由于没有标准化的配置和身份验证过程，许多厂商尝试自己来实现配置方案，这留下了许多安全隐患。

这其中较为有名的是由德州仪器（TI）在2012年由推出的配网技术Smart Config，其通过数据帧中未加密的组播字段和长度字段来传输编码后的网络配置信息。由于技术原理并不复杂，各个芯片厂商都有不同的实现及名称，如下图：￼￼￼[![](https://p4.ssl.qhimg.com/t015a454ba32ca0e28e.png)](https://p4.ssl.qhimg.com/t015a454ba32ca0e28e.png)

根据SmartConfig实现原理，配网信息编码后通过802.11数据帧传递，除了目标智能设备外，还可能会被周围的攻击者所捕获。如果攻击者能得到对应的编码表就能还原出Wi-Fi密码。在Defcon China上的议题“Passwords in the Air: Harvesting Wi-Fi Credentials from SmartCfg Provisioning”便展现了这一点。我已经写过一篇文章解读议题中的内容，这里不再赘述。（[https://www.anquanke.com/post/id/144865）](https://www.anquanke.com/post/id/144865%EF%BC%89)

Wi-Fi Easy Connect便是由Wi-Fi联盟提出的一个解决方案，其目标是让任何的Wi-Fi设备都可以便捷、安全地连接到Wi-Fi网络。可以认为是WPS（Wi-Fi Protected Setup ）的升级版。

在Wi-Fi Easy Connect中，可以通过一个拥有丰富功能的高级设备（手机、平板等）作为配置设备（Configurator），它将负责配置其他所有设备，包括配置初始的接入点。其他的都是待注册设备（Enrollee devices）。一旦配置设备连接到无线接入点，通过扫描待注册设备的二维码就可以让它们连上网络（也支持输入字符串的形式）。<br>
￼<br>
其表示有这些优势：
1. 为待入网设备提供标准化的方式。
1. 通过使用二维码和用户的设备来简化管理网络。
1. 适用于没有用户界面的设备
1. 通过公钥加密进行安全认证
1. 支持 WPA2 和 WPA3 网络
1. 替换AP时，无需将所有设备重新入网到新AP。


## 三、Wi-Fi Easy Connect连接过程

Wi-Fi Easy Connect中包含两个角色类型：Configurator 和 Enrollee。
- Configurator，可以是手机、平板等移动设备上的应用程序，AP的Web接口或应用程序接口。
- ￼Enrollee，除Configurator外的其他都是Enrollee
为了尽量减少交互的过程，Wi-Fi Easy Connect包含扫描二维码的方式。其中可以包括设备的安全密钥和唯一标志符等信息。任何可以扫描二维码的设备都可以轻松读取，消除了手动输入的负担。

最为常见的场景是：
1. 用户使用手机扫描目标设备的二维码后，会自动尝试与其建立安全连接。
1. 连接建立后，向目标设备传递Wi-Fi网络的配置信息。
1. 目标设备使用这些信息去尝试扫描，选择，连接到目标网络。
除此之外，也可以主动显示二维码，让待联网目标设备来扫描以连上网络。在官方的文档中给出了一个例子：酒店可以在房间里的电视上显示二维码，客人只需使用手机扫描该二维码就可以连接上酒店网络。如果双方都没有扫描或展示二维码的能力，还可以使用字符串的形式来建立连接。

使用Wi-Fi Easy Connect的连接过程如下：
<li>配置AP<br>
首先用户可以使用手机等设备扫描AP上的二维码，通过设备配置协议（Device Provisioning Protocol，DPP）来配置AP使其创建网络。<br>[![](https://p1.ssl.qhimg.com/t0118592b4a08a7ab4a.png)](https://p1.ssl.qhimg.com/t0118592b4a08a7ab4a.png)
</li>
<li>配置设备<br>
当网络建立后，就可以开始配置其他客户端设备了。同样可以通过扫描二维码的形式，每个设备都将获得自己特有的配置用以加入网络。同时，会生成属于该设备与网络间独特的安全证书，保护双方的通信。<br>[![](https://p2.ssl.qhimg.com/t01cb52d809c4eb2097.png)](https://p2.ssl.qhimg.com/t01cb52d809c4eb2097.png)
</li>
设备连接到网络<br>
一旦配置完成，设备就会使用得到的配置信息去尝试连接目标无线网络。<br>[![](https://p4.ssl.qhimg.com/t017af4dae58b1cf0f7.png)](https://p4.ssl.qhimg.com/t017af4dae58b1cf0f7.png)<br>
￼

## 四、Device Provisioning Protocol (DPP)

每当扫描二维码时都会通过DPP协议来完成后续配置过程。需要注意的是，enrollee既可以是等待连接网络的客户端设备，也可以是AP设备。

DPP的过程分为这几部：
<li>Bootstrapping<br>
该过程由扫描二维码或输入字符串触发，交换双方设备的公钥以及其他信息。在二维码中包含了设备的公钥，以及频道、MAC地址等信息，其通过通过编码压缩成为了base64uri的形式，如下图二维码的信息包含了一个公钥和频道1、36的信息：
<pre><code class="hljs makefile">DPP:C:81/1,115/36;K:MDkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDIgADM2206avxHJaHXgLMkq/24e0rsrfMP9K1Tm8gx+ovP0I=;;
</code></pre>
[![](https://p4.ssl.qhimg.com/t0164d441ba7f97cb1e.png)](https://p4.ssl.qhimg.com/t0164d441ba7f97cb1e.png)
</li>
<li>Authentication 与 Configuration<br>
Configurator和Enrollee使用DPP认证协议来建立安全连接。Enrollee从Configurator中获得配置信息，连接到目标AP或者自己成为AP。该配置信息由Wi-Fi网络的类型、SSID、凭证信息组成。凭证信息中可以包含一个由Configurator签署的连接器，其中含有设备的公钥、网络角色（客户端或AP）、组属性（用以确定是否允许建立网络连接），以及签名信息。这确保了连接器对每个设备是唯一的，没法被其他设备所使用。如果是用于AP的连接器，则可以确保没有其他AP可以伪装成该AP。</li>
<li>Network access<br>
客户端使用配置中的网络信息扫描目标AP，接着利用连接器使用Network Introduction Protocol协议去认证并建立连接。</li>
在Network Introduction Protocol中包含了这些过程：
- Enrollee客户端与AP确认连接器由Configurator签名
- 确认网络角色是互补的：客户端与AP建立建立
- 确认组属性是否匹配
- Enrollee客户端和AP基于连接器的公钥生成成对主密钥（PMK）
- Enrollee客户端与AP建立连接


## 五、总结

总的来说，Wi-Fi Easy Connect通过使用少量的交互来完成网络配置及建立连接工作，相比之前的方案更加简单而且安全，同时适用于没有交互界面的IoT设备。

由于该标准刚推出不久，还没有产品可以用来实际测试，仅以猜测的角度给出几个可能存在的攻击点：
<li>利用恶意二维码攻击用户手机<br>
在过去一些攻击利用案例教导我们不要随便扫描二维码。在这项应用普及之后，“扫描二维码可免费上网”会成为一个诱使用户的良好理由。</li>
<li>将用户设备连入恶意热点<br>
与使用WPS的按钮模式来偷偷连接网络相似，WEC同样假设了设备只可由拥有者所接触。由于WEC中可以通过二维码对客户端或AP进行快速配置，可以假想你的邻居在跑来串门时，通过扫描二维码将你的智能摄像头连接到他的无线网络中这样的攻击场景。相关设备厂商需要合理的考虑在网络初始化后限制二维码配网功能。</li>
<li>将恶意设备连入用户热点<br>
比如在用户家偷偷放置一个收集设备，想办法骗取用户扫描电子二维码从而使恶意设备连上用户网络。</li>


## 六、参考
1. [https://venturebeat.com/2018/06/25/wi-fi-alliance-introduces-wpa3-and-wi-fi-easy-connect/](https://venturebeat.com/2018/06/25/wi-fi-alliance-introduces-wpa3-and-wi-fi-easy-connect/)
1. [https://www.wi-fi.org/discover-wi-fi/wi-fi-easy-connect](https://www.wi-fi.org/discover-wi-fi/wi-fi-easy-connect)
文中有一些技术名词如Configurator、Enrollee等，目前还没有通用的翻译词汇，出于准确性的考虑使用了原文。

审核人：yiwang   编辑：边边
