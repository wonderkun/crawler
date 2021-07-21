> 原文链接: https://www.anquanke.com//post/id/212382 


# 微软认为CCleaner是潜在危险软件


                                阅读量   
                                **215512**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Lawrence Abrams，文章来源：https://www.bleepingcomputer.com
                                <br>原文地址：[https://www.bleepingcomputer.com/news/microsoft/microsoft-now-detects-ccleaner-as-a-potentially-unwanted-application/](https://www.bleepingcomputer.com/news/microsoft/microsoft-now-detects-ccleaner-as-a-potentially-unwanted-application/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://www.bleepstatic.com/content/hl-images/2020/07/29/ccleaner-defender.jpg?rand=1643454867)](https://www.bleepstatic.com/content/hl-images/2020/07/29/ccleaner-defender.jpg?rand=1643454867)



最近Windows Defender将CCleaner（一个Windows优化和注册表清理软件）判定为一个潜在的不需要(PUA,potentially unwanted application)的应用程序。CCleaner是一个垃圾文件清除工具，注册表清理器，是由Piriform开发的Windows性能优化实用程序。

2017年，Avast收购了CCleaner，CCleaner的用户对Avast产品一直以来存在的捆绑销售和促销活动现象存在一些担忧。

[![](https://www.bleepstatic.com/images/news/Microsoft/windows/ccleaner/pua/ccleaner-under-the-weather.jpg)](https://www.bleepstatic.com/images/news/Microsoft/windows/ccleaner/pua/ccleaner-under-the-weather.jpg)



在被收购之后，CCleaner的一些做法引发公众关注，比如说让用户无法禁用CCleaner的数据手机，强制自动更新程序等流氓做法。

[![](https://www.bleepstatic.com/images/news/software/c/ccleaner/5.46-forced-update/forum-post.png)](https://www.bleepstatic.com/images/news/software/c/ccleaner/5.46-forced-update/forum-post.png)



2019年，微软在微软社区论坛上暂时将CCleaner的网址列入黑名单，导致CCleaner的更新会出现一些问题。

[![](https://www.bleepstatic.com/images/news/Microsoft/m/microsoft-communities/ccleaner-ban/ccleaner-ban.jpg)](https://www.bleepstatic.com/images/news/Microsoft/m/microsoft-communities/ccleaner-ban/ccleaner-ban.jpg)

将其列为黑名单其实是处于微软的普遍观点，即注册表清除器和系统优化器对Windows系统弊大于利。



## 微软如今认定CCleaner属于PUA

在微软安全情报网站今天新增的威胁条目中，微软将CCleaner归类为PUA:Win32/CCleaner。

这个页面没有说明为什么微软现在将CCleaner分类为PUP/PUA，但微软已经声明，他们不支持注册表清理程序，他们不应该被使用。

一些产品，如CCleaner建议注册表需要定期维护或清理。但是，如果这些程序对注册表的清理不规范，可能会导致系统出现严重的问题，很有可能需要用户重新安装操作系统。微软不能保证不重新安装操作系统就能解决这些问题，因为注册表清理工具的效果的因应用程序而异。”微软曾在在2018年表态道。

另外，在微软的评估标准中也谈到了，如果一个应用程序存在“诱导”和“不准确地阐述”有关文件和注册表项的内容，则该软件很有可能会被列为PUA。该评估标准文档如下

```
软件不能误导或强迫你对你的设备做出决定。这被认为是限制你选择的行为。一般以下几类行为会被认定是误导和强迫行为：
1.夸大你的设备的健康状况
2.对文件、注册表项或设备上的其他项目做出误导或不准确的声明
3.以一种警告的方式声称你的设备的健康状况，并要求支付或某些操作，以换取解决所谓的问题
```

微软告诉BleepingComputer，这种检测只针对免费版本，因为它包含对其他软件的捆绑“服务”。

微软说，“我们的PUA保护旨在保护用户的生产力。无论任何软件，在安装过程中捆绑安装其他软件，如果这些被捆绑的软件不是由同一实体开发的，或者不是该软件运行所必需的，我们都会将其认定为PUA。

另一方面，CCleaner告诉BleepingComputer，他们认为这是一个不正确的检测，并试图与微软协商重新检测。

我们是在周二发现CCleaner被列为恶意软件，此前我们的客户报告说，在Windows Defender上安装CCleaner存在问题。我们认为这是一个错误的检测结果——我们正在与微软讨论，希望很快就能解决这个问题。
