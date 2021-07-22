> 原文链接: https://www.anquanke.com//post/id/153222 


# 如何查看macOS一个月前的进程执行记录


                                阅读量   
                                **162334**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：crowdstrike.com
                                <br>原文地址：[https://www.crowdstrike.com/blog/i-know-what-you-did-last-month-a-new-artifact-of-execution-on-macos-10-13/](https://www.crowdstrike.com/blog/i-know-what-you-did-last-month-a-new-artifact-of-execution-on-macos-10-13/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t013a335115fde09543.jpg)](https://p5.ssl.qhimg.com/t013a335115fde09543.jpg)

## 一、前言

数字取证分析人员在分析macOS时，很难获得关于程序执行的相关信息，但现在情况已有所改观。在macOS 10.13（High Sierra）中，Apple推出了CoreAnalytics，这是一种系统诊断机制，可以获取系统上执行过的Mach-O程序记录，时间跨度大约为1个月左右。CoreAnalytics可以为内部威胁调查任务以及应急事件响应提供许多非常有价值的信息，可以用于以下场景：

1、确定系统的使用时长，粒度以天为单位；

2、确定特定日期有哪些程序被运行过，是以前台还是以后台模式运行；

3、大致确定程序处于运行或活动状态的时长，也能大致给出程序启动或者以交互式前台方式运行的次数。

本文从技术角度大致介绍并分析了macOS 10.13中的CoreAnalytics机制，同时也介绍了如何将这类信息解析为更容易理解的格式，帮助调查人员分析取证。



## 二、概览

CoreAnalytics可以提供关于程序执行的历史纪录以及当前记录，基本上以天为单位。这些数据来自于两个源：

1、`/Library/Logs/DiagnosticReports/`目录中以`.core_analytics`为扩展名的文件，内容为JSON格式：解析前两条记录可以获得有关诊断过程的启动及结束时间戳信息，解析后面的数据可以获得诊断期间系统及应用的使用情况；

2、`/private/var/db/analyticsd/aggregates/`目录中文件名类似GUID的文件，内容为嵌套数组：在当前诊断过程期间，子系统将临时阶段性程序执行数据以聚合文件形式报告给数据分析守护程序。阶段性数据通常会在诊断周期结束时推送到`.core_analytics`文件中。

诊断周期由`.core_analytics`文件的前两行定义，分别确定诊断周期的开始及结束时间。每个诊断周期在在00:00:00 UTC后的系统首次休眠或者关闭时就会结束。前面提到过，在诊断周期结束时，当日的数据在提交到`.core_analytics`文件用作长期存储前，会先存放在聚合文件中。因此，CoreAnalytics无法用来确定程序运行的时间范围（只能大约给出24小时的时间区域）。

为了处理这种场景，我们编写了一个Python脚本（请访问我们的[GitHub](https://github.com/CrowdStrike/Forensics/tree/master/CoreAnalyticsParser)下载)，该脚本可以解析CoreAnalytics以及聚合文件，将结果写入到更加清晰的JSON或者CSV文件中。CoreAnalyticsParser脚本可以支持如下功能：

1、解析每个`.core_analytics`文件中记录的诊断周期开始及结束时间，并将其转换为UTC以及IOS8601时间；

2、从每个`.core_analytics`文件中提取与每条记录相关的可用字段；

3、将以秒数表示的原始值转换为更容易理解的`%H:%M:%S` `strftime`格式；

4、将与`comappleosanalyticsappUsage`子系统关联的聚合文件解析为每个 `.core_analytics`文件中该子系统所生成的相同字段。

在`.core_analytics`文件中某个应用的执行记录大致如下所示：

```
`{` ‘message’: `{` ‘activations’: 105,
‘activeTime’: 4250,
‘activityPeriods’: 12,
‘appDescription’: ‘com.google.Chrome ||| 67.0.3396.87 (3396.87)’,
‘foreground’: ‘YES’,
‘idleTimeouts’: 4,
‘launches’: 0,
‘powerTime’: 12537,
‘processName’: ‘Google Chrome’,
‘uptime’: 26110`}`,
‘name’: ‘comappleosanalyticsappUsage’,
‘uuid’: ‘4d7c9e4a-8c8c-4971-bce3-09d38d078849’`}`
```

表1. Google Chrome对应的CoreAnalytics记录样例

由CoreAnalyticsParser解析后，同一个记录会被解析成如下结果：

```
`{` ‘src_report’: ‘/path/to/Analytics_2018-06-29-173717_ML-C02PA037R9QZ.core_analytics’,
‘diag_start’: ‘2018-06-29T00:00:09Z’,
‘diag_end’: ‘2018-06-30T00:37:17.660000Z’,
‘name’: ‘comappleosanalyticsappUsage’,
‘uuid’: ‘4d7c9e4a-8c8c-4971-bce3-09d38d078849’,
‘processName’: ‘Google Chrome’,
‘appDescription’: ‘com.google.Chrome ||| 67.0.3396.87 (3396.87)’,
‘appName’: ‘com.google.Chrome’,
‘appVersion’: ‘67.0.3396.87 (3396.87)’,
‘foreground’: ‘YES’,
‘uptime’: ‘26110’,
‘uptime_parsed’: ‘7:15:10’,
‘powerTime’: ‘12537’,
‘powerTime_parsed’: ‘3:28:57’,
‘activeTime’: ‘4250’,
‘activeTime_parsed’: ‘1:10:50’,
‘activations’: ‘105’,
‘launches’: ‘0’,
‘activityPeriods’: ’12’,
‘idleTimeouts’: ‘4’`}`
```

表2. CoreAnalyticsParser脚本将图1中CoreAnalytics的结果解析成JSON数据

注意：如上解析结果为JSON格式数据，可以使用`-j`选项输出为JSON数据。默认情况下，解析脚本会将结果输出为CSV格式。

该脚本可以在实时系统上运行，也可以处理包含CoreAnalytics或者聚合文件的目录。



## 三、技术分析

### <a class="reference-link" name="CoreAnalytics%E6%96%87%E4%BB%B6"></a>CoreAnalytics文件

`.core_analytics`文件中包含JSON记录，这些记录可以表示程序执行历史及时间戳信息，时间戳可以划出历史数据所对应的特定诊断周期。这些文件位于`/Library/Logs/DiagnosticReports/`目录中，文件名采用`Analytics_YYYY_MM_DD_HHMMSS_&lt;systemname&gt;.core_analytics`格式。文件名中的时间戳基于的是系统的本地时间信息。在10.13版本之前，`DiagnosticReports`目录只包含程序故障及崩溃报告，现在，不论程序是否崩溃，该目录中都会包含与程序执行有关的数据。

负责生成和收集系统分析及诊断数据的守护程序同样会维护`/private/var/db/analyticsd`目录中已预先写好的CoreAnalytics文件信息。在该目录中，`currentConfiguration.json`文件貌似维护着一个字典集，对应与子系统相匹配的名称、UUID以及数据类型。

在`/private/var/db/analyticsd/journals`目录中，`da2-identity.json`文件包含最近生成的CoreAnalytics文件中的`_marker`记录列表。第一条记录通常会比当前可用的第一个CoreAnalytics文件要早上7-10天，最后一条记录对应最近写入后的报告。通常情况下，这些数据可以用来确认预期的所有`.core_analytics`文件都存在且未被篡改。

**定义诊断周期**

`.core_analytics`文件的首条记录包含一个时间戳字段，字段值对应诊断周期结束的时间。虽然时间戳以本地时间为基础，但带有时区信息。如果该字段值未被修改，则应当匹配该文件的上次修改时间戳。换句话说，只有在诊断周期结束后，`.core_analytics`文件才会被写入到这个目录中。

```
`{` ‘bug_type’: ‘211’,
‘os_version’: ‘Mac OS X 10.13.5 (17F77)’,
‘timestamp’: ‘2018-06-05 17:16:48.19 -0700’`}`
```

表3. `.core_analytics`文件的第一行记录，包含诊断周期结束时间戳信息

我们可以在以`_marker`开头的JSON记录中找到诊断周期的开始时间，即`startTimestamp`字段中的UTC时间戳。

```
`{` ‘_marker’: ”,
‘_preferredUserInterfaceLanguage’: ‘en’,
‘_userInterfaceLanguage’: ‘en’,
‘_userSetRegionFormat’: ‘US’,
‘startTimestamp’: ‘2018-06-05T00:19:13Z’,
‘version’: ‘1.0’`}`
```

表4. `.core_analytics`文件的第二行记录，包含诊断周期开始时间戳信息

CoreAnalytics文件基本上每天都会写入到`DiagnosticReports`目录中，并且在系统使用期间，两个记录文件的时间间隔基本上无缝连接。在诊断期间，如果系统处于睡眠或者关机状态，则不会生成CoreAnalytics文件。

|**诊断周期开始时间**|**诊断周期结束时间**
|------
|2018-06-08T01:51:23Z|2018-06-09T01:50:01.370000Z
|2018-06-10T16:49:09Z|2018-06-11T03:53:15.140000Z
|2018-06-11T03:53:14Z|2018-06-12T02:50:17.410000Z
|2018-06-12T02:50:17Z|2018-06-13T00:17:45.870000Z
|2018-06-13T00:17:45Z|2018-06-14T01:17:06.340000Z

表5. 系统连续使用几天时，`.core_analytics`文件之间无缝连接，当系统未激活时则会出现断档

根据我们对`/private/var/db/analyticsd/Library/Preferences/analyticsd.plist`这个二进制plist文件的分析结果，这些文件通常会在每天00:00:00 UTC时间后系统首次睡眠或关闭时在`DiagnosticReports`目录中生成。该plist文件以Unix Epoch格式记录了`.core_analytics`的上次提交时间以及下次提交时间。

```
Key: cadence
Type: String
Value:
`{` ‘bootToken’: 1530574585000000,
‘lastSubmission’: 1531256233,
‘nextSubmission’: 1531267200,
‘osVersion’: ’17E202′,
‘version’: 1`}`
```

表6. `analyticsd.plist`文件内容，包含上次提交及下次提交时间戳信息

然而我们的测试显示，报告通常会在提交时间过后的首次睡眠或者关机时写入。

**系统使用信息**

在时间戳及marker记录之后，`comappleosanalyticssystemUsage`子系统所生成的数据反映了系统的运行时长（以秒为单位）。该子系统可能会在主机睡眠或关闭后生成新的纪录。将这些记录中的`uptime`字段值加起来后就可以得到系统处于活跃状态下的总时间。`Uptime`字段非常简单，为`uptime`值的千位数。`activeTime`字段很有可能表示的是系统运行状态下被使用的时长（以秒为单位），如下两条记录所示，系统有两个阶段处于唤醒状态下（时长分别为4分钟以及40分钟），总时长为44分38秒，但使用时长仅为14分26秒。

```
`{` ‘message’: `{` ‘Uptime’: 0,
‘activations’: 2,
‘activeTime’: 42,
‘idleTimeouts’: 1,
‘uptime’: 247`}`,
‘name’: ‘comappleosanalyticssystemUsage’,
‘uuid’: ‘00866801-81a5-466a-a51e-a24b606ce5f1’`}`
`{` ‘message’: `{` ‘Uptime’: 2000,
        ‘activations’: 2,
        ‘activeTime’: 824,
        ‘idleTimeouts’: 1,
        ‘uptime’: 2431`}`,
‘name’: ‘comappleosanalyticssystemUsage’,
‘uuid’: ‘00866801-81a5-466a-a51e-a24b606ce5f1’`}`
```

表7. 反应系统使用状态的两条记录

接下来的两条记录分别为2小时的心跳记录一次1天的心跳记录。这些记录的作用尚未澄清，因为这些心跳记录似乎与诊断周期的时长或者任何程序的运行时间无关。`BogusFieldNotActuallyEverUsed`这个字段名很可能表示不仅该字段已被弃用，甚至这条数据本身已被弃用。

```
`{` ‘message’: `{` ‘BogusFieldNotActuallyEverUsed’: ‘null’, ‘Count’: 7`}`,
‘name’: ‘TwoHourHeartbeatCount’,
‘uuid’: ‘7ad14604-ce6e-45f3-bd39-5bc186d92049’`}``{` ‘message’: `{` ‘BogusFieldNotActuallyEverUsed’: ‘null’, ‘Count’: 1`}`,
‘name’: ‘OneDayHeartBeatCount’,
‘uuid’: ‘a4813163-fd49-44ea-b3e1-e47a015e629c’`}`
```

表8. 心跳记录

**应用使用信息**

后面开始的每一行都包含3个键：`name`、`uuid`以及`message`。`name`以及`uuid`键可以映射到生成该记录的特定子系统，`message`字段包含一个嵌套JSON记录，其中包含其他一些数据。我们所观察到的一些最为常见的子系统以及UUID值如下所示：

|**子系统名**|**UUID**
|------
|comappleosanalyticsappUsage|4d7c9e4a-8c8c-4971-bce3-09d38d078849
|comappleosanalyticssystemUsage|00866801-81a5-466a-a51e-a24b606ce5f1
|comappleosanalyticsMASAppUsage|0fd0693a-3d0a-48be-bdb2-528e18a3e86c
|TwoHourHeartbeatCount|7ad14604-ce6e-45f3-bd39-5bc186d92049
|OneDayHeartBeatCount|a4813163-fd49-44ea-b3e1-e47a015e629c

表9. 向守护程序报告数据的常见子系统及对应的UUID

我们的测试表明，这些UUID在运行macOS 10.13.4以及10.13.5系统上均保持一致，这表明UUID仅与子系统及子系统的版本有关，如果Apple将来修改子系统时，这些值可能也会发生改变。

`comappleosanalyticsappUsage`子系统会为执行的每个程序生成一条记录。

```
`{` ‘message’: `{` ‘activations’: 105,
‘activeTime’: 4250,
‘activityPeriods’: 12,
‘appDescription’: ‘com.google.Chrome ||| 67.0.3396.87 (3396.87)’,
‘foreground’: ‘YES’,
‘idleTimeouts’: 4,
‘launches’: 0,
‘powerTime’: 12537,
‘processName’: ‘Google Chrome’,
‘uptime’: 26110`}`,
‘name’: ‘comappleosanalyticsappUsage’,
‘uuid’: ‘4d7c9e4a-8c8c-4971-bce3-09d38d078849’`}`
```

表10. `comappleosanalyticsappUsage`子系统生成的`.core_analytics`示例记录

`message`下包含的9个字段可能会为分析人员的取证工作提供大量信息：

1、`activeTime`可能提供程序处于前台运行时的秒数；

2、`activityPeriods`可能提供程序被调到前台运行的次数；

3、`appDescription`直接来自于应用程序包中`Info.plist`的相关信息。如果`Info.plist`中的相关键值信息格式错误或者为空，这里字段的值则会显示为`???`；

在CoreAnalytics记录中存放的数据满足如下格式：

```
&lt;CFBundleIdentifier&gt; ||| &lt;CFBundleShortVersionString&gt; (&lt;CFBundleVersion&gt;)
```

表11. CoreAnalytics记录的数据格式

例如，`Google Chrome.app`的`Info.plist`文件中可以根据如下键值提取出所需的信息：

```
&lt;key&gt;CFBundleIdentifier&lt;/key&gt;
&lt;string&gt;com.google.Chrome&lt;/string&gt;
&lt;key&gt;CFBundleShortVersionString&lt;/key&gt;
&lt;string&gt;67.0.3396.99&lt;/string&gt;
&lt;key&gt;CFBundleVersion&lt;/key&gt;
&lt;string&gt;3396.99&lt;/string&gt;
```

表12. `Google Chrome.app`应用`Info.plist`中的相关键值

如果程序以独立的Mach-O可执行文件形式运行，或者`Info.plist`不可用、格式错误或者不完整，那么`appDescription`就会显示为`UNBUNDLED ||| ???`。

例如，GlobalProtect中`Info.plist`的`CFBundleVersion`键值就无法获取到：

```
com.paloaltonetworks.GlobalProtect ||| 4.0.2-19 (???)

```

表13. GlobalProtect的CoreAnalytics记录中对应的`appDescription`值

其他字段的意义如下：

4、`foreground`字段的值为`YES`或者`NO`，表示程序是否在前台运行；

5、`idleTimeouts`的含义目前尚未澄清；

6、`launches`可能表示的是诊断报告期间应用的启动次数。如果应用在诊断周期开始前启动，那么`launches`的值为0；

7、根据我们的测试结果，`powerTime`可能表示的是程序处于运行状态并消耗AC电源的时间（以秒为单位）；

8、`processName`的值来自于应用程序包中`Info.plist`文件的`CFBundleExecutable`键值；

举个例子，`Google Chrome.app`中`Info.plist`文件的该键值信息如下：

```
&lt;key&gt;CFBundleExecutable&lt;/key&gt;
&lt;string&gt;Google Chrome&lt;/string&gt;
```

表14. `Google Chrome.app`应用`Info.plist`中的`CFBundleExecutable`键值

如果程序为独立的Mach-O可执行文件，或者`Info.plist`不可用、格式错误或者不完整，这个字段仍然会在CoreAnalytics记录正确生成。根据我们的测试结果，目前我们尚未澄清守护程序获取该数据所使用的是哪个辅助来源。

如下所示，在某些情况下，`processName`字段将会留空。在这些场景中，我们实际上无法通过CoreAnalytics中推测执行的是哪个程序。

```
`{` ‘message’: `{` ‘activations’: 0,
‘activeTime’: 0,
‘activityPeriods’: 0,
‘appDescription’: ‘UNBUNDLED ||| ???’,
‘foreground’: ‘NO’,
‘idleTimeouts’: 0,
‘launches’: 2,
‘powerTime’: 0,
‘processName’: ”,
‘uptime’: 24`}`,
‘name’: ‘comappleosanalyticsappUsage’,
‘uuid’: ‘4d7c9e4a-8c8c-4971-bce3-09d38d078849’`}`
```

表15. 无名程序所对应的CoreAnalytics记录

9、`uptime`可能表示的是程序运行的总时长（以秒为单位），该数字并未包含系统睡眠或者关闭的时间。在诊断期间，某些程序（如Dock）的运行时间很可能与系统运行时间相近或完全匹配。在上文的**系统使用信息**部分中，两个`uptime`（247及2431）的总和与Dock应用的`uptime`值（2678）完全匹配，如下所示：

```
`{` ‘message’: `{` ‘activations’: 0,
‘activeTime’: 0,
‘activityPeriods’: 0,
‘appDescription’: ‘com.apple.dock ||| 1.8 (1849.16)’,
‘foreground’: ‘NO’,
‘idleTimeouts’: 0,
‘launches’: 0,
‘powerTime’: 0,
‘processName’: ‘Dock’,
‘uptime’: 2678`}`,
‘name’: ‘comappleosanalyticsappUsage’,
‘uuid’: ‘4d7c9e4a-8c8c-4971-bce3-09d38d078849’`}`
```

表16. Dock应用对应的CoreAnalytics记录

在我们的测试中，我们发现另一个子系统（即`comappleosanalyticsMASAppUsage`）往CoreAnalytics文件中写入了与Microsoft OneNote有关的记录。JSON嵌套数据中的键值与`comappleosanalyticsappUsage`子系统所写的键值有所不同。这条记录并没有使用一个`appDescription`字段，而是将`CFBundleIdentifier`和`CFBundleShortVersionString`（以及`CFBundleVersion`）写入`identifier`以及`version`字段中。除了`launches`之外，该记录还缺少其他所有字段。

```
`{` ‘message’: `{` ‘identifier’: ‘com.microsoft.onenote.mac’,
‘launches’: 1,
‘version’: ‘15.32 (15.32.17030400)’`}`,
‘name’: ‘comappleosanalyticsMASAppUsage’,
‘uuid’: ‘0fd0693a-3d0a-48be-bdb2-528e18a3e86c’`}`
```

表17. Microsoft OneNote对应的CoreAnalytics记录，由另一个子系统生成

可能其他子系统所生成的数据结构也会有所不同。

### <a class="reference-link" name="%E5%BD%92%E7%BA%B3%E5%BD%93%E5%A4%A9%E6%89%A7%E8%A1%8C%E6%95%B0%E6%8D%AE"></a>归纳当天执行数据

在诊断周期结束时，CoreAnalytics数据会被写入到文件中，在此之前我们有可能能恢复这些数据。

在数据提交并推送到当天的CoreAnalytics文件之前，`/private/var/db/analyticsd/aggregates/`目录充当了每个子系统的临时性暂存目录。每个子系统在该目录中都对应一个阶段性文件，文件名为子系统的UUID值。比如，`4d7c9e4a-8c8c-4971-bce3-09d38d078849`文件包含了1.0版`comappleosanalyticsappUsage`子系统所生成的报告数据（这些数据在00:00:00 UTC时间后的首次睡眠或者关机时会写入到`/Library/Logs/DiagnosticReports/`目录的CoreAnalytics文件中）。这些文件的内容似乎为嵌套数组，比如Google Chrome所对应的数组如下所示：

```
[ [‘Google Chrome’, ‘com.google.Chrome ||| 67.0.3396.99 (3396.99)’, ‘YES’],
[5660, 145, 0, 0, 5, 2, 1020]]
```

表18. Google Chrome所对应的聚合数据

这些值对应`comappleosanalyticsappUsage`子系统所生成的CoreAnalytics记录中的一些字段，具体如下：

```
[ [processName, appDescription, foreground],
[uptime, activeTime, launches, idleTimeouts, activations, activityPeriods, powerTime]]
```

表19. 聚合数据的数组结构

解析聚合文件中中数组的值，将其与上述字段一一对应后，我们现在就可以在当天分析数据被提交至CoreAnalytics文件前，分析当天应用的使用情况。



## 四、总结

CoreAnalytics可以为我们提供关于系统及应用程序使用情况的大量信息，程序执行历史跨度长达一个月的，可以在调查任务中起到关键作用，由于调查行为本身特性，证据往往无法在现场第一时间收集，此时能起到的作用也就更加明显。尽管Apple提供的官方文档可能会进一步澄清某些字段的用途及含义，研究人员可以以本文为基础，开始研究macOS系统上的应用活动数据。
