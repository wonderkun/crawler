> 原文链接: https://www.anquanke.com//post/id/198483 


# Docker Registry代码泄露报告


                                阅读量   
                                **806735**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者unit42.paloaltonetworks.com，文章来源：paloaltonetworks
                                <br>原文地址：[https://unit42.paloaltonetworks.com/leaked-docker-code/](https://unit42.paloaltonetworks.com/leaked-docker-code/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01ea5b11d44af72917.png)](https://p4.ssl.qhimg.com/t01ea5b11d44af72917.png)



## 0x00 前言

在之前公布的[2020年春季云端威胁报告](http://go.paloaltonetworks.com/cloudthreatreport)中，我们侧重于DevOps实践内容，介绍了云端出现的一些错误配置情况。在研究过程中，我们发现由于云端的配置错误，导致大量DevOps服务（如SSH、数据库、代码仓库等）被暴露在互联网上。本文详细分析了来自Docker Registry的代码泄露问题，也分析了这种缺陷及其他不安全的错误配置架构如何影响组织的整体安全状态。

错误配置如同唾手可得的果实，是攻击者一直在寻找的切入点，可能会对整个云端架构造成安全风险。



## 0x01 Shift Left

“Shift Left”（左移）指的是在软件开发生命周期（SDLC）的早期阶段识别存在漏洞的代码、删除漏洞的一种安全实践。Shift Left的核心思想是尽早将安全措施集成到SDLC中，以便在到达生产阶段之前消除漏洞及bug。虽然Shift Left主要关注重点为应用程序的安全性，但这种概念同样可以应用到基础设施中。基础设施中的漏洞或者错误配置同样可以造成严重后果，甚至比应用漏洞更为危险。随着Infrastructure as Code（IaC，基础设施即代码）的日趋成熟，运维人员现在可以在创建基础设施之前，仔细检查其是否存在漏洞。

这里我们主要关注网络访问控制配置出现错误并且暴露在网上的Docker Registry。这些Registry包含应用源代码以及历史版本。当出现泄露时，攻击者可能窃取知识产权、注入恶意代码、劫持关键操作数据。我们总共找到了2,956个公开的应用，15,887个不同的应用版本。这些不安全Registry的所有者包括研究机构、零售商、新闻媒体组织以及科技公司。



## 0x02 Docker Registry

> 警告：由于Docker镜像中包含应用源代码及业务敏感数据，因此限制Docker Registry的访问权限、确保数据完整性至关重要。

[Docker镜像](https://github.com/moby/moby/blob/master/image/spec/v1.md)是包含文件的一个集合，可以作为单个[容器](https://www.docker.com/resources/what-container)（container）来部署。Docker镜像将应用代码、依赖库以及操作系统文件合并到一个捆绑包中，可以在操作系统无关的环境中独立运行。[Docker Registry](https://docs.docker.com/registry/)是用来存储及管理Docker镜像的服务器。在每个Docker Registry中，镜像会被规整到仓库（repository）中，每个仓库包含不同应用程序（比如httpd、nginx、WordPress）对应的各种镜像。仓库也可以保存同个应用的多个版本，使用不同的标签来标识不同的版本。因此，Docker Registry类似于适用于容器化应用的版本控制存储方案。Docker Registry主要支持3种操作（push镜像、pull镜像以及delete镜像），这些操作都有对应的[Registry API](https://docs.docker.com/registry/spec/api/)。

为了存储容器镜像，用户需要设置本地（on-premise）Registry服务器，或者使用基于云端的Registry服务。本地Registry可以使用官方的[Registry容器](https://github.com/docker/distribution)来快速创建。系统管理员负责存储架构、DevOps管道集成以及访问控制。大多数云服务服务商（比如[DockerHub](https://hub.docker.com/)、[Amazon Elastic Container Registry （ECR）](https://aws.amazon.com/ecr/)、[Azure Container Registry（ACR）](https://azure.microsoft.com/en-us/services/container-registry/)以及[Google Container Registry（GCR）](https://cloud.google.com/container-registry/)）都会提供受管Registry服务。基于云端的Registry通常会提供其他功能，比如GUI用户接口、漏洞扫描以及基于原生Docker Registry的集成访问控制。这些功能可以进一步简化Registry基础架构的管理及维护。



## 0x03 寻找不安全的Docker Registry

虽然Docker Registry服务器设置起来非常快速，但想要强化通信安全性、加强访问控制却需要额外进行配置。系统管理员可能会在无意中将Registry服务暴露在互联网中，没有部署正确的访问控制。在此次研究中，我们希望搜寻这些“错误配置的”Registry、探索被泄露的数据。需要注意的是，我们只收集了元数据，并没有尝试访问文件内容。

Docker Registry会在每个API响应头中包含一个`Docker-Distribution-API-Version`字段，即使服务器拒绝请求，返回`401`未授权状态码也一样。找到这个头部特征后，我们在[Shodan](https://www.shodan.io/)和[Censys](https://censys.io/)上搜索了暴露在互联网上的Docker Registry。虽然Docker Registry默认运行在`5000`（HTTP）或者`5001`（HTTPS）端口上，但实际上可能对应于任何端口。我们没有使用端口特征，而是在Shodan和Censys上使用头部特征来查找，这样能得到匹配各种端口的所有结果（总共超过300个端口）。我们搜索和识别不安全Registry的过程如图1所示。

[![](https://p4.ssl.qhimg.com/t01db59c6511c745cd7.png)](https://p4.ssl.qhimg.com/t01db59c6511c745cd7.png)

图1. 查找公开Docker Registry的过程

具体包括如下步骤：

1、使用Shodan和Censys的搜索API来寻找响应报文中包含`Docker-Distribution-API-Version`头部字段的服务器。

2、向这些服务器发送“[check version](https://docs.docker.com/registry/spec/api/#api-version-check)”请求，通过分析响应数据，确定有效的Docker Registry服务器。有效的Registry服务器可能会在`Docker-Distribution-API-Version`字段中返回版本号，比如`docker-distribution-api-version: registry/2.0`。`200`状态码代表Registry不需要身份认证，`401`状态码表示Registry需要用户在`WWW-Authenticate`头部字段中提交认证令牌。

3、向服务器发送“[list repository](https://docs.docker.com/registry/spec/api/#listing-repositories)”和“[list tag](https://docs.docker.com/registry/spec/api/#listing-image-tags)”请求，测试服务器是否允许pull操作。如果服务器返回`200`状态码，则表示允许pull操作。如果返回`401`或`403`状态码，则表示用户需要身份认证或者授权才能pull镜像。

4、向服务器发送“[blob upload](https://docs.docker.com/registry/spec/api/#pushing-an-image)”请求，配合随机的Repository名来测试服务器是否允许push操作。该请求可以让Registry初始化镜像上传过程。如果允许push操作，Registry会在`location`头部字段中返回上传URL，并且返回`202`状态码。随后我们使用“[cancel upload](https://docs.docker.com/registry/spec/api/#pushing-an-image)”请求来结束上传会话。如果服务器返回`204`状态码，则表示上传会话已成功取消。

5、向服务器发送“[image deletion](https://docs.docker.com/registry/spec/api/#deleting-an-image)”请求，配合随机repository名及随机镜像摘要来测试服务器是否允许删除操作。这样我们就可以通过检查状态码，在没有删除任何镜像的情况下，判断服务器是否允许删除操作。如果服务器允许该操作，但对应的镜像摘要并不存在，那么就会返回`400`状态码，错误信息为`DIGEST_IMVALID`。如果不允许删除操作，那么服务器就会返回`405`状态码，错误消息为`UNSUPPORTED`。



## 0x04 不安全Docker Registry报告

经过研究后，我们找到了在互联网上开放的941个Docker Registry，其中117个Registry不需要身份认证就可以访问。这些Registry中共包含2,956个repository、15,887个标签。在117个不安全的Registry中，有80个Registry允许pull操作，92个Registry允许push操作，7个Registry允许删除操作。在没有查看镜像内容的情况下，我们通过反向DNS查找或者TLS证书中的cname信息，成功识别出不安全Registry中约25% Registry的所有者。这些Registry的所有者包括研究机构、零售商、新闻媒体组织以及科技公司。某些开放的Registry中有超过50个repository和100个标签。通过所有源代码和历史标签，攻击者可以为目标系统量身定制攻击方法，发起攻击。如果允许push操作，攻击者可以将无害的应用替换为带有后门的应用，这些Registry可能会被用来托管恶意软件。如果允许删除操作，黑客可以加密或者删除镜像，要求受害者支付赎金。由于每个Registry通常会对应多个客户端，如果这些客户端从被污染的Registry执行镜像pull及运行操作，那么就存在被攻击风险。

我们对这些公开Registry的统计信息如图2到图5所示。图2显示了实现HTTPS协议或者身份认证头部的Registry占比，我们关注的是不需要认证头部的Registry。图3是维恩图，表示允许各种操作的不安全Registry数。图4表示暴露在互联网上的部分repository及标签。图5给出了不安全Registry中的repository数及标签数。这些Registry泄露的数据量惊人，更何况这些危险可能帮助攻击者实现横向移动，造成更大危害。

[![](https://p0.ssl.qhimg.com/t01d24bda826c977b57.png)](https://p0.ssl.qhimg.com/t01d24bda826c977b57.png)

图2. 不安全Registry中TLS及认证的占比

[![](https://p4.ssl.qhimg.com/t019f56eeb0f88039ad.png)](https://p4.ssl.qhimg.com/t019f56eeb0f88039ad.png)

图3. 不安全Registry允许的操作

[![](https://p3.ssl.qhimg.com/t01c21961058d2d2eca.png)](https://p3.ssl.qhimg.com/t01c21961058d2d2eca.png)

图4. 不安全repository及tag样例

[![](https://p5.ssl.qhimg.com/t019819d31e2185455b.png)](https://p5.ssl.qhimg.com/t019819d31e2185455b.png)

图5. 不安全Registry中的repository及标签数



## 0x05 总结

在本文中，我们研究了错误配置的Docker Registry，攻击者可以借机窃取机密数据、攻陷目标、打断正常业务。这种错误配置很容易补救，比如可以添加防火墙规则，阻止用户通过互联网访问Registry，在所有API请求中强制启用认证头等。然而，随着应用数量的不断增加、基础架构越来越复杂，保证安全性成了一项非常艰巨的任务。运维人员需要使用自动化工具来扫描漏洞、持续监控恶意活动。问题越早发现，生产环境中攻击者可利用的机会也就越少。
