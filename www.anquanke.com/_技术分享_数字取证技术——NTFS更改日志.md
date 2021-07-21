> 原文链接: https://www.anquanke.com//post/id/86265 


# 【技术分享】数字取证技术——NTFS更改日志


                                阅读量   
                                **172386**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：countuponsecurity.com
                                <br>原文地址：[https://countuponsecurity.com/2017/05/25/digital-forensics-ntfs-change-journal/](https://countuponsecurity.com/2017/05/25/digital-forensics-ntfs-change-journal/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p0.ssl.qhimg.com/t01017ce70b818b72c6.jpg)](https://p0.ssl.qhimg.com/t01017ce70b818b72c6.jpg)

翻译：[**华为未然实验室**](http://bobao.360.cn/member/contribute?uid=2794169747)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

去年，我写了一系列关于数字取证的[文章](https://countuponsecurity.com/2016/05/30/digital-forensics-ntfs-indx-and-journaling/)。我介绍了进行事件响应时可能有用的不同工件。在这些系列的最后一篇文章中，我介绍了用于存储有关目录中文件的元数据的NTFS INDX属性，及记录NTFS卷中发生的所有操作的$LogFile元数据文件。这两个工件都可以给研究人员提供关于攻击者活动的大量信息。然而，NTFS中还有一个特殊的文件——名为$UsnJrnl的更新序列号（USN）[日志文件](https://msdn.microsoft.com/en-us/library/windows/desktop/aa363798%28v=vs.85%29.aspx)，该文件中也包含有关发生在NTFS卷上的操作的大量历史信息。

虽然磁盘上会发生不同的文件操作，但在NTFS卷中，更改日志会记录文件创建、删除、加密、目录创建、删除等操作背后的[原因](https://msdn.microsoft.com/en-us/library/aa365722.aspx)。每个卷有一个USN更改日志——自Windows Vista起默认为启用状态，并被索引服务、文件复制服务（FRS）、远程安装服务（RIS）及远程存储等应用程序使用。不过，应用程序和管理员可以创建、删除及重新创建更改日志。更改日志文件存储在隐藏的系统文件$Extend$UsnJrnl中。[$UsnJrnl](http://forensicinsight.org/wp-content/uploads/2013/07/F-INSIGHT-Advanced-UsnJrnl-Forensics-English.pdf)文件包含两个备用数据流（ADS），$Max和the $J。$Max数据流包含有关更改日志的信息，如最大大小。$J数据流包含更改日志的内容，包含更改日期和时间、更改原因、MFT条目、MFT父条目等信息。该信息对于调查是有用的，比如，攻击者在组织内活动时为隐藏其踪迹而删除文件和目录的情形下。要获取更改日志文件，你需要对文件系统进行原始访问。

在实时系统上，你可以通过Windows命令提示符以管理员权限运行命令“fsutil usn queryjournal C:”来检查更改日志的大小和状态。“[fsutil](https://technet.microsoft.com/en-us/library/cc788042(WS.10).aspx)”命令也可用于[更改日志的大小](http://faq.attix5.com/index.php?View=entry&amp;EntryID=24)。你还可以使用来自Joakim Schicht的[RawCopy](https://github.com/jschicht/RawCopy)或[ExtractUsnJrnl](https://github.com/jschicht/ExtractUsnJrnl)等工具从实时系统获取更改日志文件。在这个特定系统中，更改日志的最大大小为0x2000000字节。

[![](https://p2.ssl.qhimg.com/t012b9d8a5d7474884d.png)](https://p2.ssl.qhimg.com/t012b9d8a5d7474884d.png)

现在，我们来快速练习一下如何从磁盘镜像获取更改日志文件。首先，我们使用“mmls”实用程序从磁盘镜像中查看分区表。然后，我们使用The Sleuth Kit中的“fls”来获取文件和目录列表，并使用grep搜索UsnJrnl字符串。如下图所示，“fls”的输出显示文件系统包含$UsnJrnl:$Max和$UsnJrnl:$J文件。我们对MFT条目号（84621）感兴趣。

[![](https://p4.ssl.qhimg.com/t01b4459a3ab60ddae7.png)](https://p4.ssl.qhimg.com/t01b4459a3ab60ddae7.png)

接下来，我们使用来自The Sleuth Kit的“istat”命令来看一下条目号84621的MFT记录属性。该MFT条目存储关于$ UsnJrnl的NTFS元数据。我们对属性部分感兴趣，更具体而言，我们正在寻找指向$DATA属性的标识符128。标识符128-37指向大小为32字节的[驻留](https://countuponsecurity.com/2015/11/10/digital-forensics-ntfs-metadata-timeline-creation/)$Max数据流。标识符128-38指向大小为40-GBytes的稀疏$J数据流。然后我们使用“icat”命令查看$Max数据流的内容，该数据流可以给出更改日志的最大大小，然后我们还使用“icat”将$J数据流导出到文件中。值得注意的是，更改日志是稀疏的。这意味着部分数据为零。然而，The Sleuth Kit的icat会提取全部大小的数据流。一个更有效率和更快速的工具是ExtractUsnJrnl，因为其只提取实际的数据。下图显示了提取更改日志文件所需的步骤。

[![](https://p4.ssl.qhimg.com/t019a8fdd309306a07b.png)](https://p4.ssl.qhimg.com/t019a8fdd309306a07b.png)

我们已将更改日志导出到一个文件中，所以我们将使用[UsnJrnl2Csv](https://github.com/jschicht/UsnJrnl2Csv)实用程序。该工具支持USN_RECORD_V2和USN_RECORD_V3，可以非常容易地从更改日志中解析和提取信息。输出将是一个CSV文件。下图显示了正在运行的工具。你只需浏览你获得的更改日志文件，并开始解析。

[![](https://p3.ssl.qhimg.com/t01f85e975c4f04483e.png)](https://p3.ssl.qhimg.com/t01f85e975c4f04483e.png)

该过程可能需要一些时间，完成后，你将获得一个包含日记记录的CSV文件。该文件可以方便地导入Excel。然后，基于原因和时间戳字段过滤。当你进行这样的分析时，你通常已有一些线索，已有一个可帮助你发现更多线索和结果的起点。在分析更改日志记录后，我们可以开始构建有关攻击者活动的事件时间表。下图显示了有关创建和删除的恶意文件的更改日志的事件时间表。这些结果可以作为危害指标，以便在环境中找到更多受损的系统。此外，对于每个文件，你都可以使用MFT条目号来尝试恢复已删除的文件。如果文件被删除的时间与镜像获取时间之间的间隔短暂，那么就有机会恢复已删除文件中的数据。

[![](https://p3.ssl.qhimg.com/t015a1a46063060c071.png)](https://p3.ssl.qhimg.com/t015a1a46063060c071.png)

更改日志包含不容忽视的大量信息。更改日志的另一个有趣的方面是随着其增长分配和释放空间，不像[$LogFile](https://countuponsecurity.com/2016/05/30/digital-forensics-ntfs-indx-and-journaling/)，记录不会被覆盖。这意味着我们可以在NTFS卷上的未分配空间中找到旧的日志记录。如何获得呢？PoorBillionaire编写的[USN Record Carver](https://github.com/PoorBillionaire/USN-Record-Carver)工具可以从二进制数据中挖出日志记录，从而可以恢复这些记录。

本文介绍了关于NTFS更改日志的一些介绍性概念、如何获取和解析该日志、如何创建事件的时间表。涉及的技术和工具并不新颖，但与当今的数字取证分析有关，并被广泛使用。
