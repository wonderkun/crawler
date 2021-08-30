> 原文链接: https://www.anquanke.com//post/id/251883 


# A-Journey-into-Synology-NAS-系列——群晖NAS介绍


                                阅读量   
                                **27385**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t0114a0d4fa50481a90.jpg)](https://p1.ssl.qhimg.com/t0114a0d4fa50481a90.jpg)



## 前言

之前花过一段时间研究群晖的`NAS`设备，并发现了一些安全问题，同时该研究内容入选了安全会议`POC2019`和`HITB2021AMS`。网上关于群晖`NAS`设备安全研究的公开资料并不多，因此基于议题[《Bug Hunting in Synology NAS》](https://www.powerofcommunity.net/poc2019/Qian.pdf)和[《A Journey into Synology NAS》](https://conference.hitb.org/files/hitbsecconf2021ams/materials/D1T2%20-%20A%20Journey%20into%20Synology%20NAS%20-%20QC.pdf)，将之前的一些内容展开，如果有对群晖`NAS`设备感兴趣的同学，希望对你们有所帮助。

本系列文章的目的是介绍一些关于群晖`NAS`设备的基本信息、请求处理的相关机制和常见攻击面等，以及实际发现的部分安全问题，让读者对群晖`NAS`设备有个大体的认识，并知道如何去对设备进行安全分析，而不会聚焦于某个具体漏洞的利用细节。本系列文章大概会分为以下几个部分：
- 群晖环境搭建
<li>自定义服务分析，包括`findhostd`和`iscsi_snapshot_comm_core`
</li>
<li>
`HTTP`请求处理流程，和常见的攻击面分析</li>


## 群晖NAS介绍

`NAS` (`Network Attached Storage`)，即网络附属存储，是一种特殊的数据存储设备，包含一些必要的器件如`RAID`、磁盘驱动器或可移动的存储介质，和内嵌的操作系统，用于将分布、独立的数据整合并集中管理，同时提供远程访问、共享、备份等功能。简单地可以理解为”联网的磁盘阵列”，并同时具备硬盘存储和网盘存储的优势。

群晖是一家致力于提供网络存储服务器(`NAS`)服务的公司，被认为是中小企业和家庭`NAS`领域的长期领导者。群晖`NAS`的主要产品线包括`DiskStation`、`FlashStation`和`RackSation`，其中`DiskStation`是适合我们日常使用的桌面型号。针对每个产品线，都提供了不同的系列来满足不同的要求。

此外，群晖还提供了适用于每一个`NAS`的操作系统`DiskStation Manager` (`DSM`)。它是一个基于`Linux`的、网页界面直观的操作系统，提供了丰富的功能包括文件共享、文件同步和数据备份等，以在各个方面提供更好的灵活性和可用性。



## 环境搭建

在了解了群晖`NAS`的基本信息后，需要有一个目标设备来进行测试。目前，常见的有两种方式，如下。
- 直接购买一个群晖`NAS`设备，即”白群晖”，其功能完整，比较方便配置和使用
- 组装一个设备，或购买一个厂商的`NAS`设备，并安装群晖的`DSM`系统，即”黑群晖”，其拥有大部分的功能，对于测试而言是足够的
除了上述两种方式，`NAS`社区还提供了另一种方式，即创建一个群晖虚拟机。这种方式更适合于测试用途(比如想测试不同的`DSM`版本)，因此下面主要对这种方式进行介绍。

> 这里仅是出于安全研究的目的，如果有实际使用需要，建议购买群晖官方`NAS`设备。

### <a class="reference-link" name="%E5%AE%89%E8%A3%85DSM%206.2.1"></a>安装DSM 6.2.1

创建一个群晖虚拟机，主要需要如下两个文件。目前社区提供了针对不同`NAS`型号和不同`DSM`版本的`loader`，最新的`loader`版本适用于`DSM 6.2.1`，注意在安装时最好选择和`loader`对应的`NAS`型号及`DSM`版本。经测试，`ds918`系列的`loader`支持升级到`DSM 6.2.3`，即可以在先安装`DSM 6.2.1`版本后再手动升级到`DSM 6.2.3`。
- 群晖官方提供的[`DSM`文件](https://archive.synology.com/download/Os/DSM)(`pat`文件)
<li>社区提供的[loader](https://mega.nz/#F!yQpw0YTI!DQqIzUCG2RbBtQ6YieScWg!yYwWkABb)
</li>
> 关于`loader`是否可以升级以及是否成功升级等信息可参考[这里](https://xpenology.com/forum/forum/78-dsm-updates-reporting/)

以`VMware Workspace`为例，创建群晖虚拟机需要先加载`synoboot`引导，再安装对应的`DSM`。由于下载的引导文件为`img`格式，这里可以先将其转换为`vmdk`格式，方式如下。
- 使用软件`StarWind Converter`进行转换
<li>使用`qemu-img`命令进行转换
<pre><code class="lang-shell hljs">$ qemu-img convert -f raw -O vmdk synoboot.img synoboot.vmdk
</code></pre>
</li>
之后正常创建`VMware`虚拟机，并使用之前转换得到的`vmdk`文件。其中，**在选择安装引导的磁盘类型时，一定要选择`SATA`类型**，选择`SCSI`的话可能会造成后续引导无法识别或启动。创建完毕后，再正常添加额外的硬盘，用于数据存储。启动虚拟机后，通过`Web Assistant`或`Synology Assistant`进行安装和配置，完成之后就可以通过浏览器成功访问`NAS`虚拟机了。

> `Synology Assistant`是一个客户端软件，用于在局域网内搜索和管理对应的`NAS`设备。

[![](https://p4.ssl.qhimg.com/t0181f50ac4abb28cdf.png)](https://p4.ssl.qhimg.com/t0181f50ac4abb28cdf.png)

之后，可以通过手动更新的方式将其升级到`DSM 6.2.3`版本。前面提到过，通过这种方式只能得到`DSM 6.2.3`版本的虚拟机，而目前群晖`DSM`的最新版本包括`DSM 6.2.4`和`DSM 7.0`，无法通过这种方式安装。不过，可以基于刚创建的`NAS`虚拟机，借助群晖提供的`Virtual Machine Manager`套件来安装`DSM 6.2.4`或`DSM 7.0`版本的虚拟机。

### <a class="reference-link" name="%E5%AE%89%E8%A3%85DSM%206.2.4/DSM%207.0"></a>安装DSM 6.2.4/DSM 7.0

群晖套件`Virtual Machine Manager`，通过一个集中且规范的接口集成了多种虚拟化解决方案，可以让用户在`NAS`上轻松创建、运行和管理多台虚拟机，当然也包括群晖的虚拟`DSM`。

[![](https://p4.ssl.qhimg.com/t0111238875ffd6eadd.png)](https://p4.ssl.qhimg.com/t0111238875ffd6eadd.png)

简单而言，可以先创建一个`DSM 6.2.3`版本的虚拟机，然后在该虚拟机内部，借助`Virtual Machine Manager`套件再安装一个或多个`virtual DSM`。其中，在安装`virtual DSM`时，需要保证对应的存储空间格式为`Brtfs`，可以通过额外添加一个硬盘(容量尽量大一点，比如`40G`或以上)的方式，新增加存储空间时选择`SHR(Brtfs)`即可。另外，一个`Virtual Machine Manager`里面似乎只提供了一个`Virtual DSM`的免费`License`，因此如果安装了多个`Virtual DSM`的话，多个虚拟实例无法同时启动。这里通过切换虚拟实例的方式来避免这一问题，对于安全测试而言足够了。

[![](https://p5.ssl.qhimg.com/t01ac1dc1c80fc2b595.png)](https://p5.ssl.qhimg.com/t01ac1dc1c80fc2b595.png)

> 由于目前`DSM 7.0`还在测试阶段，一些功能或特性不是特别稳定或成熟，因此本系列文章还是以`DSM 6.1`/`DSM6.2`版本为主。

### <a class="reference-link" name="%E7%BE%A4%E6%99%96%E5%9C%A8%E7%BA%BFDemo"></a>群晖在线Demo

群晖官方也提供了供在线体验的[`DSM`实例](https://demo.synology.com/en-global/dsm)，包括`DSM 6.2.4`和`DSM 7.0`版本。当然，你也可以基于该坏境去进行安全分析与测试，不过可能会有一些限制比如无法使用`SSH`访问`shell`等，或者其他顾虑等等。

### <a class="reference-link" name="%E5%B7%A5%E5%85%B7%E5%AE%89%E8%A3%85"></a>工具安装

群晖`NAS`上提供了`SSH`功能，开启后可以访问底层`Linux shell`，便于后续的调试与分析等。此外，群晖还提供了一个名为`Diagnosis Tool`的套件，其包含很多工具，如`gdb`和`gdbserver`等，便于对程序进行调试。通常，可以通过套件中心搜索并安装该套件，如果在套件中心中无法找到该套件的话，可以通过在`shell`命令行采用命令`synogear install`进行安装，如下。

```
$ sudo -i    # 切换到root用户
$ synogear install  # 安装套件
```



## 设备指纹

群晖`NAS`主要是用在远程访问的场景下，此时唯一的入口是通过`5000/http`(`5001/https`)进行访问(暂不考虑使用`QuickConnect`或其他代理的情形)。使用设备搜索引擎如`shodan`查找暴露在公网上的设备，如下。可以看到，确实只有少量的端口可以访问。

[![](https://p3.ssl.qhimg.com/t0115c241d7853329cd.png)](https://p3.ssl.qhimg.com/t0115c241d7853329cd.png)

为了进一步地知道目标设备的`DSM`版本、安装的套件和对应的版本等信息，需要获取更精细的设备指纹。通过分析，发现在`index`页面中存在对应的线索。具体地，`index`页面中存在一些`css`链接，表明有哪些内置的模块和安装的第三方套件。同时，其中也包含一些`NAS`特有的脚本链接。根据上述信息，可以构建一些`query`用于更准确地查找群晖`NAS`设备。

```
Port: 5000/5001 # default
Shodan query: html:"SYNO.Core.Desktop.SessionData"
```

[![](https://p4.ssl.qhimg.com/t01e83e2ed5810deced.png)](https://p4.ssl.qhimg.com/t01e83e2ed5810deced.png)

另外，在每个链接后面还有一个参数`v`，其表示最后更改时间的时间戳，即对应构建时的时间戳。以如下链接为例，时间戳`1589235146`可转换为时间`2020-05-12 06:12:26`。通过在[群晖镜像仓库](https://archive.synology.com/download/Os/DSM)中查找各`DSM`版本发布的时间，可以推测该`DSM`版本为`6.2.3-25426`。类似地，`AudioStation`套件的版本为`6.5.6-3377`。

```
webapi/entry.cgi?api=SYNO.Core.Desktop.SessionData&amp;version=1&amp;method=getjs&amp;SynoToken=&amp;v=1589235146
```

进一步地，可以通过访问`http://&lt;host&gt;:&lt;port&gt;/ssdp/desc-DSM-eth0.xml`, 获取设备的具体型号、版本以及序列号等信息。

> 通常，设备搜索引擎只会探测`http://&lt;host&gt;:&lt;port&gt;/`下的默认页面，对于该二级页面没有进行探测。

```
&lt;deviceType&gt;urn:schemas-upnp-org:device:Basic:1&lt;/deviceType&gt;
&lt;friendlyName&gt;VirtualDSM (VirtualDSM)&lt;/friendlyName&gt;
&lt;manufacturer&gt;Synology&lt;/manufacturer&gt;
&lt;manufacturerURL&gt;http://www.synology.com&lt;/manufacturerURL&gt;
&lt;modelDescription&gt;Synology NAS&lt;/modelDescription&gt;
&lt;modelName&gt;VirtualDSM&lt;/modelName&gt;
&lt;modelNumber&gt;VirtualDSM 6.2-25556&lt;/modelNumber&gt;
&lt;modelURL&gt;http://www.synology.com&lt;/modelURL&gt;
&lt;modelType&gt;NAS&lt;/modelType&gt;
&lt;serialNumber&gt;xxxxxx&lt;/serialNumber&gt;
&lt;UDN&gt;xxxxxx&lt;/UDN&gt;
```



## 相关事件/研究

近年来，有一些关于群晖的安全事件，其中包括：
- 在`2018`年的`GeekPwn`比赛中，来自长亭科技的安全研究员攻破了群晖`DS115j`型号`NAS`设备，成功获取了设备上的`root`权限；
- 在`Pwn2Own Tokyo 2020`比赛中，有2个团队攻破了群晖`DS418Play`型号`NAS`设备，均成功拿到了设备上的`root shell`。
同时，也有一些安全研究人员对群晖设备进行了分析，感兴趣的可以看看。
- [Network Attached Security: Attacking a Synology NAS](https://www.nccgroup.com/ae/about-us/newsroom-and-events/blogs/2017/april/network-attached-security-attacking-a-synology-nas/)
- [SOHOpelessly Broken 2.0 – Security Vulnerabilities in Network Accessible Services](https://www.ise.io/casestudies/sohopelessly-broken-2-0/index.html)
- [Vulnerability Spotlight: Multiple vulnerabilities in Synology SRM (Synology Router Manager)](https://blog.talosintelligence.com/2020/10/vulnerability-spotlight-multiple.html)
- [Vulnerability Spotlight: Multiple vulnerabilities in Synology DiskStation Manager](https://blog.talosintelligence.com/2021/04/vuln-spotlight-synology-dsm.html)


## 小结

本文首先对群晖`NAS`进行了简单介绍，然后给出了如何搭建群晖`NAS`环境的方法，为后续的安全分析做准备。同时，对设备指纹进行了简单讨论，并介绍了与群晖`NAS`相关的一些安全事件/安全研究等。后续文章将对群晖`NAS`设备上的部分服务、功能或套件等进行分析，并分享一些实际发现的安全问题。



## 相关链接
- [DSM 6.1.x Loader](https://xpenology.com/forum/topic/6253-dsm-61x-loader/)
- [各版本引导下载](https://mega.nz/#F!yQpw0YTI!DQqIzUCG2RbBtQ6YieScWg!yYwWkABb)
- [群晖镜像/套件下载](https://archive.synology.com/download)
- [Bug Hunting in Synology NAS](https://www.powerofcommunity.net/poc2019/Qian.pdf)
- [A Journey into Synology NAS](https://conference.hitb.org/files/hitbsecconf2021ams/materials/D1T2%20-%20A%20Journey%20into%20Synology%20NAS%20-%20QC.pdf)