> 原文链接: https://www.anquanke.com//post/id/169435 


# Windows 注册表取证分析


                                阅读量   
                                **270960**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者fireeye，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2019/01/digging-up-the-past-windows-registry-forensics-revisited.html](https://www.fireeye.com/blog/threat-research/2019/01/digging-up-the-past-windows-registry-forensics-revisited.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01cb1867cfb1efdc8d.png)](https://p3.ssl.qhimg.com/t01cb1867cfb1efdc8d.png)



## 前言

作为应急响应和风险评估任务的一部分，FireEye顾问在对计算机网络进行取证分析时经常使用Windows注册表数据。这对于发现恶意活动和确定哪些数据可能被窃取很有帮助。注册表中存在很多不同类型的数据，可以提供程序执行、应用程序设置、恶意软件持久性和其他有价值工件的证据。

对过去发生的攻击进行取证分析可能比较困难。高级持续性威胁(APT)攻击者经常使用反取证技术来隐藏自己，这使得应急响应变得更加困难。为了给我们的顾问提供最好的工具，我们重新审查了我们现有的注册表取证分析技术，并确定了恢复历史和已删除的注册表数据的新方法。我们重点分析以下已知的历史注册表数据源：
- 注册表事务日志（registry transaction log）(.LOG)
- 事务型注册表事务日志（Transactional registry transaction log）(.TxR)
- 注册表hive文件中的删除项
- 系统备份的hive文件(REGBACK)
- 通过系统恢复（System Restore）备份的hive文件


## Windows注册表格式

Windows注册表是由多个hive文件组成的。hive文件是二进制文件，包含一个简单的文件系统，其中包括很多个cell，用于存储键、值、数据和相关的元数据。hive文件按照4KB的页面大小(也称为bin)进行读取和写入。

有关Windows注册表hive格式的详细说明，请查看[论文](http://sentinelchicken.com/data/TheWindowsNTRegistryFileFormat.pdf)和[GitHub页面](https://github.com/msuhanov/regf/blob/master/Windows%20registry%20file%20format%20specification.md)。



## 注册表事务日志(.LOG)

为了最大限度地提高注册表的可靠性，Windows可以在对注册表文件执行写入操作时使用事务日志。日志保存在被写入hive文件之前写入注册表的数据。事务日志在由于锁定或损坏而无法直接对hive文件进行写入操作时使用。

日志记录被保存到对应的注册表hive文件的同一文件夹中。它的文件名和hive文件相同，后缀为.LOG。Windows可能使用多个日志，在这种情况下将使用.LOG1和.LOG2后缀。

有关事务日志格式的详细信息，请查看[GitHub页面](https://github.com/msuhanov/regf/blob/master/Windows%20registry%20file%20format%20specification.md#format-of-transaction-log-files)。

注册表事务日志最初在Windows 2000中引入。在原始事务日志格式中，数据总是在事务日志开始处写入。一个位图（Bitmap）被用于指示日志中有哪些页面，页面按顺序排列。由于文件开始处经常被覆盖，所以很难从这些日志中恢复旧数据。因为每次使用时都会将不同数量的数据写入事务日志，所以旧的页面可能保留在多个不同用途的文件中。但页面的位置必须通过在当前hive文件中搜索类似的页面来进行推断，并且完全恢复数据的可能性很小。

在Windows8.1中引入了一种新的注册表事务日志格式。尽管新日志的使用方式不变，但有了不同的格式。新日志的工作方式类似于环形缓冲（ring buffer），日志中最旧的数据被新数据覆盖。新日志格式中的每个项都包含一个序列号和注册表偏移量，因此很容易确定写入的顺序和页面的写入位置。由于改变了日志格式，数据被覆盖的频率要低得多，所以通常能够从这些日志文件中恢复旧的事务。

可以恢复的数据量取决于注册表的活动。对实际的系统的事务日志的测试表明可以恢复几天至几周内的数据。现实环境中可恢复性可能相差很大。频繁操作注册表(比如Windows Update)会显著缩小可恢复范围。

尽管新的日志格式包含更多可恢复的信息，但是将一组注册表页转换为有用的数据是相当困难的。首先，它需要跟踪注册表中的所有页面，并确定在特定的写入操作中可能发生了哪些改变。为了评估它是否包含唯一的数据，还需要确定这种变化是否会产生某些在后续版本的hive文件中不存在的东西。

目前我们处理注册表事务文件的方法：
1. 对所有写入按序号降序排序，以便优先处理最新的写入。
1. 解析已分配和未分配的cell，以便查找已分配和删除的项。
1. 与原始hive文件中的项进行对比。所有不存在的项都被标记为已删除（deleted）和已记录（logged）。


## 事务日志示例

如图1，我们在Run键下创建一个注册表值，当用户登录到系统时启动malware.exe（恶意软件）。

[![](https://p1.ssl.qhimg.com/t01254d468e53ff5111.png)](https://p1.ssl.qhimg.com/t01254d468e53ff5111.png)

不久之后，从系统中删除恶意软件。在删除之前，注册表值被覆盖。

[![](https://p1.ssl.qhimg.com/t0127dc565c09e544a8.png)](https://p1.ssl.qhimg.com/t0127dc565c09e544a8.png)

虽然已删除的值仍然存在于hive文件中，但是现有的取证工具将无法恢复原始数据，因为它被覆盖了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019dc26c04642e97aa.png)

但在这种情况下，数据仍然存在于事务日志中，并且可以恢复。

[![](https://p0.ssl.qhimg.com/t011a4a1b261a42ce9d.png)](https://p0.ssl.qhimg.com/t011a4a1b261a42ce9d.png)



## 事务型注册表事务日志(.Txr)

除了事务日志文件外，还有事务型注册表子系统使用的日志。应用程序可以利用事务型注册表精确地执行组合的注册表操作。这是应用安装程序最常用的方法，因为它简化了失败操作回滚（rollback）。

事务型注册表日志使用CLFS(通用日志文件系统, Common Log File System)格式。日志保存在`&lt;hive&gt;&lt;GUID&gt;.TxR.&lt;number&gt;.regtrans-ms`格式的文件中。对于用户hive文件，这些文件保存在与hive文件相同的文件夹中，并在用户注销时被清除。但对于系统来说，则保存在`%SystemRoot%System32configTxR`中，并且不会自动清除。所以通常可以从系统事务型日志中恢复历史数据。

事务型日志的格式没有很好的文档记录。Microsoft提供了[CLFS日志和API的概述](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/introduction-to-the-common-log-file-system)。

通过实验，我们能够确定基本的记录格式。我们可以识别用于创建和删除注册表项的记录以及注册表值的写入和删除。日志项中包含相关的键路径、值名、数据类型和数据。有关事务日志记录格式的详细信息，请查看本文附录。

虽然注册表事务日志中的很多数据对于入侵调查并不是很有价值，但在某些情况下，这些数据被证明是有用的。特别是，我们发现计划任务的创建和删除使用了注册表事务。通过分析注册表事务日志，我们能够找到攻击者在活动系统上创建计划任务的证据。任何其他位置都不存在这些数据。

在Windows 8.1和Windows Vista上都能观察到计划任务使用事务型注册表进行操作；Windows 10上的计划任务没有这种行为。暂不清楚为什么Windows 10的行为不同。



## 事务型注册表示例

在本例中，我们创建一个计划任务。计划任务周期性地运行恶意软件。

[![](https://p1.ssl.qhimg.com/t01e0b5706bd24d244e.png)](https://p1.ssl.qhimg.com/t01e0b5706bd24d244e.png)

保存有关计划任务的信息到注册表中。

[![](https://p0.ssl.qhimg.com/t0182b4b833ab7edc08.png)](https://p0.ssl.qhimg.com/t0182b4b833ab7edc08.png)

由于计划任务是通过事务型注册表操作写入注册表的，所以在事务型注册表事务日志中可以获取数据的副本。从系统中删除计划任务后，数据能够保留在日志中。

[![](https://p0.ssl.qhimg.com/t01e5a58454bf87b7ef.png)](https://p0.ssl.qhimg.com/t01e5a58454bf87b7ef.png)



## 恢复已删除项

除了事务日志之外，我们还分析了从注册表hive文件中恢复已删除项的方法。我们首先对目前取证工具常用的一些技术进行了深入分析，希望找出一种更准确的方法。

恢复已删除项需要解析注册表hive文件中的cell。这是相对简单的。FireEye有许多工具可以读取原始注册表hive文件，通过cell解析相关的键、值和数据。恢复已删除的数据则要复杂得多，因为删除元素时会丢失一些信息。需要采取更复杂的办法来处理由此导致的混淆。

在解析cell时，只有一个公共字段：cell的大小（size）。有些类型的cell包含魔数（magic number）标识符，用于确定它们的类型。但是，其他类型的cell(如数据和值列表)没有标识符；它们的类型必须通过相邻的cell引用来推断。此外，cell内的数据大小可能与cell大小不同。根据cell类型，可能需要相关cell的信息来确定数据大小。

注册表元素（element）被删除时，其cell被标记为未分配。由于cell不会立即被覆盖，因此通常可以从注册表cell中恢复已删除的元素。然而，未分配的cell可能与相邻的未分配cell合并，以便最大限度地提高遍历效率。这使得恢复已删除的cell变得更加复杂，因为cell的大小可能已经被修改。这导致不能很好地确定原来的cell大小，必须通过检查cell的内容来间接确定。



## 恢复已删除项的现有方法

通过对公开的资料和源代码的分析，我们了解了从注册表hive文件中恢复已删除元素的现有方法。常见的方法如下：
1. 查找所有未分配的cell，查找已删除的键cell。
1. 从已删除的键中查找引用的已删除值。
1. 查找剩下的所有未分配的cell，查找未引用的已删除值cell。
1. 从所有已删除的值中查找引用的数据cell。
我们实现了一种类似的算法来测试它的有效性。虽然这个简单的算法能够恢复许多已删除的注册表元素，但它有一些重大缺陷。一个主要问题是无法通过已删除cell验证任何引用。由于引用的cell可能已经被多次覆盖或重用，我们的程序在识别值和数据时经常出错，导致错误的结果和无效的输出。

我们还将程序输出与常用的注册表取证工具进行比较。尽管我们的程序包含大部分相同的输出，但是很明显，常用的注册表取证工具能够恢复更多的数据。特别是，它们能够从尚未覆盖的已分配cell的空闲空间中恢复已删除的元素。

另外，我们发现孤立的已分配cell也被认为是已删除的。尚不清楚为什么注册表hive文件中会存在未引用的已分配cell，因为所有引用的cell在删除的同时都应该被标记未分配的。可能是某些类型的故障导致已删除的cell没有被标记为未分配的。

通过实验，我们发现现有的注册表工具能够执行更好的验证，结果少了误报（false positive）。但是，我们还发现在很多情况下，这些工具产生了不正确的删除值关联，并输出了无效数据。这种情况在多次重复使用cell时可能会出现，如果不仔细检查，这些引用可能看起来是有效的。



## 一种恢复已删除项的新方法

考虑到算法还能改进，我们进行了重新设计，以最大的准确性和效率恢复已删除的注册表元素。经过多次试验和改进，我们最终得到了一种新的算法，可以准确地恢复已删除的注册表元素，同时最大限度地提高性能。这是通过发现和跟踪注册表hive文件中的所有cell以执行更好的验证、处理cell闲置空间以及发现孤立的键和值来实现的。测试结果与现有的注册表取证工具非常匹配，但具有更好的验证和更少的误报。

以下是改进算法的总结：
1. 对所有已分配和未分配的cell执行基本解析。尽可能确定cell类型和数据大小。
<li>枚举所有已分配cell并执行以下操作：
<ul>
1. 对于已分配键，请查找引用的值列表、类名和安全记录。填充引用cell的数据大小。验证键的父级以确定键是否是孤立的。
1. 对于已分配值，查找引用的数据并填充数据大小。
</ul>
</li>
1. 将所有已分配cell闲置空间定义为未分配的cell。
1. 枚举已分配键并尝试查找值列表中显示的已删除值。并尝试在值列表闲置空间中查找旧的已删除值引用。
1. 枚举未分配cell并尝试查找已删除的键cell。
1. 枚举未分配键，并尝试定义引用的类名、安全记录和值。
1. 枚举未分配cell并尝试查找未引用的已删除值cell。
1. 枚举未分配值并尝试查找引用的数据cell。


## 恢复删除元素的示例

下面的示例演示我们的恢复删除项的算法是如何执行更准确的数据恢复并避免误报的。图8展示了一个常用注册表取证工具未能正确恢复数据示例：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011795d6977b242342.png)

可以看到从这个键恢复的ProviderName是乱码，因为它引用了一个被覆盖的位置。当我们删除的注册表恢复工具运行在同一个hive文件上时，它会识别数据已被覆盖，并且不会输出乱码。图9中的`data_present`字段的值为0，表示无法从hive文件中恢复已删除的数据。

正确的注册表数据:

```
Key: CMI-CreateHive`{`2A7FB991-7BBE-4F9D-B91E-7CB51D4737F5`}`
     ControlSet002ControlClass`{`4D36E972-E325-11CE-BFC1-08002BE10318`}`019
Value: ProviderName  Type: REG_SZ  (value_offset=0x137FE40) (data_size=20)
     (data_present=0) (data_offset=0x10EAF68) (deleted_type=UNALLOCATED)
```



## 注册表备份

Windows有一个定期备份系统注册表hive文件的简单机制。hive文件由一个名为RegIdleBackup的计划任务备份，默认情况下，该任务每10天运行一次。备份的文件存储在`%SystemRoot%System32configRegBack`中。只有最近的备份存储在此位置。这对于调查系统上最近的活动很有用。

RegIdleBackup功能在Windows Vista中首次引入。从那时起，Windows的所有版本有这个功能，但它在Windows 10系统上默认不运行，即使手动运行也不会创建备份，原因尚不清楚。

除了RegBack之外，系统还原（System Restore）也会备份注册表数据。默认情况下，每当软件安装或卸载(包括Windows更新)时，都会创建系统还原快照。所以，系统恢复快照通常至少每月创建一次。虽然已知一些APT组织可以操作系统还原快照，但如果在攻击者活动时拍摄快照，则通常可以找到攻击者历史活动的证据。系统还原快照包含所有注册表hive文件，包括系统和用户hive文件。

维基百科关于[系统还原（System Restore）](https://en.wikipedia.org/wiki/System_Restore)的介绍。

处理系统还原快照中的hive文件可能具有挑战性，因为系统上可能存在许多快照，因此需要处理大量数据，而且通常快照之间的cell只存在有微小的变化。处理大量快照的一种策略是构建一个表示注册表cell的结构，然后对每个快照重复处理。以前结构中不存在的任何内容都可以被适当地认为是已删除和已记录的。



## 结论

注册表可以为取证分析提供大量数据。有了大量的已删除数据和历史数据来源，就可以在调查期间收集到更完整的攻击者活动。随着攻击者不断提高技术水平并改进他们的行动，调查人员将不得不进行调整以便发现并防御他们。



## 附录 – 事务型注册表事务日志(.TxR)格式

包含以下格式的记录：

<th style="text-align: left;">Offset（偏移值）</th><th style="text-align: left;">Field（字段）</th><th style="text-align: left;">Size（大小）</th>
|------
<td style="text-align: left;">0</td><td style="text-align: left;">Magic number(魔数) (0x280000)</td><td style="text-align: left;"></td>
<td style="text-align: left;">…</td><td style="text-align: left;"></td><td style="text-align: left;"></td>
<td style="text-align: left;">12</td><td style="text-align: left;">Record size</td><td style="text-align: left;">4</td>
<td style="text-align: left;">16</td><td style="text-align: left;">Record type (1)</td><td style="text-align: left;">4</td>
<td style="text-align: left;">20</td><td style="text-align: left;">Registry operation type(注册表操作类型)</td><td style="text-align: left;">2</td>
<td style="text-align: left;">…</td><td style="text-align: left;"></td><td style="text-align: left;"></td>
<td style="text-align: left;">40</td><td style="text-align: left;">Key path size(键路径大小)</td><td style="text-align: left;">2</td>
<td style="text-align: left;">42</td><td style="text-align: left;">Key path size repeated</td><td style="text-align: left;">2</td>

魔数总是0x280000。

记录大小包括标头（header）。

记录类型总是1。

操作类型1是创建键。

操作类型2是删除键。

操作类型3-8为写入或删除值。尚不清楚不同的类型的含义。

键路径大小在偏移值40处，并在偏移量42处重复。所有注册表操作类型都是这样。

对于注册表项的写入和删除操作，键路径位于偏移值72处。

对于注册表值写入和删除操作，存在以下数据：

<th style="text-align: left;">Offset（偏移值）</th><th style="text-align: left;">Field（字段）</th><th style="text-align: left;">Size（大小）</th>
|------
<td style="text-align: left;">56</td><td style="text-align: left;">Value name size</td><td style="text-align: left;">2</td>
<td style="text-align: left;">58</td><td style="text-align: left;">Value name size repeated</td><td style="text-align: left;">2</td>
<td style="text-align: left;">…</td><td style="text-align: left;"></td><td style="text-align: left;"></td>
<td style="text-align: left;">72</td><td style="text-align: left;">Data type</td><td style="text-align: left;">4</td>
<td style="text-align: left;">76</td><td style="text-align: left;">Data size</td><td style="text-align: left;">4</td>

值记录的数据在偏移值88处开始。它包含键路径，后面跟着值名或者数据。如果数据大小不为零，则记录为值写入操作；否则为值删除操作。
