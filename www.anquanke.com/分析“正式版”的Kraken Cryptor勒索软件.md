> 原文链接: https://www.anquanke.com//post/id/164107 


# 分析“正式版”的Kraken Cryptor勒索软件


                                阅读量   
                                **139347**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Fortinet，文章来源：fortinet.com
                                <br>原文地址：[https://www.fortinet.com/blog/threat-research/analyzing-the-new-non-beta-version-of-the-kraken-cryptor-ransomw.html](https://www.fortinet.com/blog/threat-research/analyzing-the-new-non-beta-version-of-the-kraken-cryptor-ransomw.html)

译文仅供参考，具体内容表达以及含义原文为准

## 一、前言

[![](https://p4.ssl.qhimg.com/t01abbf7afb82f16c74.png)](https://p4.ssl.qhimg.com/t01abbf7afb82f16c74.png)

FortiGuard实验室最近检测到了新版本的Kraken Cryptor勒索软件，虽然这款变种配置文件中删除了beta标签，但依然存在许多bug，并且开发者仍然在不断修改该软件的基本功能。

这款勒索软件变种相对较新，仅从今年8月份开始传播。很明显这款勒索软件仍处于开发状态，开发者正往其中添加新的函数来改进其功能。然而，当我们分析最近的样本时，我们发现新版本的恶意软件仍然不太稳定，无法正常运行。恶意软件中充斥着代码错误，甚至还存在用于调试的消息框。在碰到多个不可用的版本后，我们最终找到了能够正常运行的一个样本。

在本文中，我们将分析能够“正常工作”的Kraken Cryptor勒索软件，这款软件仍在开发中，开发者试图使其功能上能够更加稳定。如果大家想了解这款勒索软件基本功能的详细信息，可以访问McAfee上个月发表的一篇[分析文章](https://securingtomorrow.mcafee.com/mcafee-labs/fallout-exploit-kit-releases-the-kraken-ransomware-on-its-victims)。



## 二、存在多个bug的2.1版

我们在11月上旬发现了2.1版，然后我们很快意识到这是一个存在bug的版本，在执行完毕后并不会感染我们的测试系统。之所以会发生这种情况，并不是因为样本中存在新的反分析功能，而只是因为样本会检查其配置文件中并不存在的一个标记（tag）。

[![](https://p2.ssl.qhimg.com/t01c9372b90818cd126.png)](https://p2.ssl.qhimg.com/t01c9372b90818cd126.png)

图1. Kraken Cryptor Ransomware V2.1中读取配置字段值的bug

这样会导致该函数永远返回false，强迫恶意软件调用一个自清除函数结束运行并自行删除。

找到存在bug的这个样本后，我们又在几个小时之后发现了标记为2.1版的另一个样本，其中删掉了我们刚刚发现的bug。然而，这个版本中包含另一个错误，在获取地理位置的函数中存在一个逻辑异常处理问题，导致离线安装功能被禁用。这个函数会连接到ipinfo[.]io/json来获取系统的地理位置信息。如果无法建立连接，则会捕获到异常，然后不会为地理位置变量赋任何值，导致读取配置数据失败。因此，这个版本只能在在线环境中运行。

另一个有趣的地方在于，样本中还包含一个异常调试消息。

[![](https://p5.ssl.qhimg.com/t012b4d8f4f650d4777.png)](https://p5.ssl.qhimg.com/t012b4d8f4f650d4777.png)

图2. Kraken Cryptor勒索软件中的调试消息对话框

有趣的是，我们在之前的v2.07版本中看到过一些MessageBox语句。然而2.1版本中的MessageBox语句数量更多。在过去的几天内，开发人员多次修改了Kraken Cryptor勒索软件的源代码，在传播过程中没有删除这些调试消息，甚至也没有删除无法执行的bug。

我们还发现在同一个版本的配置数据中存在不同的电子邮件，因此我们相信这两个样本可能由不同的开发者编译。在这个样本中我们只找到了middleeast[@]cock.li这个邮箱，而本文中我们分析的其他样本中的邮箱都为onionhelp[@]memeware[.]net。

[![](https://p0.ssl.qhimg.com/t01b41b137a7180d0bd.png)](https://p0.ssl.qhimg.com/t01b41b137a7180d0bd.png)

图3. 同一版本（2.1）不同样本中存在不同的邮箱



## 三、带有HelloWorld!特征的2..2版

分析存在bug的2.1版样本后，不久我们又发现了新的版本。更新版虽然离线安装功能依然处于禁用状态，但整体功能正常。其他所有功能与先前版本几乎完全相同，除了一个有趣的功能之外，这个功能可以在main函数的开头位置找到。

[![](https://p3.ssl.qhimg.com/t01adaa4dd58e1ae53a.png)](https://p3.ssl.qhimg.com/t01adaa4dd58e1ae53a.png)

图4. 动态编译HelloWorld!

现在样本中添加了经过动态编译和执行的一个HelloWorld!示例源码。开发者貌似正在把玩源代码。



## 四、2.1版后修改功能

### <a name="%E9%85%8D%E7%BD%AE%E4%BF%AE%E6%94%B9"></a>配置修改

这个新版样本在2.1版的配置文件的基础上新增了一个标签partner，该标签取代了旧版标签operate。

[![](https://p5.ssl.qhimg.com/t0161b9d7c902bb90f6.png)](https://p5.ssl.qhimg.com/t0161b9d7c902bb90f6.png)

图5. 配置中的partner字段及api字符串中的beta字段（于2.1版中删除）

我们还发现2.1版已从配置数据中删除了beta标签。在2.07版中，这个标签在配置数据中的值为1，表明当时样本仍处于beta版中。然而在2.1版中，样本在API查询字符串中会将这个字段的值设置为0，这意味着该样本与beta版有所不同。

配置数据中还存在另一个改动：help_voice。

[![](https://p5.ssl.qhimg.com/t01ed526ddc7749cc5c.png)](https://p5.ssl.qhimg.com/t01ed526ddc7749cc5c.png)

图6. 配置数据中的help_voice

通过这个配置文件，恶意软件会使用CScript来执行生成的Visual Basic脚本文件（.vbs），脚本文件的内容位于API标志中。运行脚本文件后，恶意样本会语音念出配置数据中预置的文本内容。

[![](https://p1.ssl.qhimg.com/t015811951cfe8c92d3.png)](https://p1.ssl.qhimg.com/t015811951cfe8c92d3.png)

图7. 执行CScript处理新创建的.vbs

最后一处改动就是skip_directories标签。恶意样本尝试跳过某些目录，以便加快加密过程。

在下图中，我们展示了2.07、2.1以及2.2版本间的不同的配置数据。红色方框高亮部分表示2.1版中跳过的某些目录。

[![](https://p5.ssl.qhimg.com/t01e1ddc16b33ef36c3.png)](https://p5.ssl.qhimg.com/t01e1ddc16b33ef36c3.png)

图8. 2.07、2.1以及2.2版之间的配置更改

在2.2版中，我们还发现配置中的price以及price_unit采用USD来结算，并没有采用BTC，这与之前的版本有所不同。

### <a name="%E5%88%A0%E9%99%A4anti-smb%E5%8F%8Aanti-rdp"></a>删除anti-smb及anti-rdp

module标签内容与2.04版存在较大不同，如下图所示。开发者从2.07版开始删除了反分析模块中关于smb及rdp方面的配置。这些配置最早源自于2.04版，恶意软件使用smb以及rdp标签来阻止被感染环境使用smb及rdp连接。然而，我们没有在2.1及2.2版中找到这些功能。

[![](https://p4.ssl.qhimg.com/t01fd1a15d8117e0dbd.png)](https://p4.ssl.qhimg.com/t01fd1a15d8117e0dbd.png)

图9. 2.04版中的模块配置

### <a name="%E5%8F%AF%E7%96%91%E7%9A%84SelfKill%E6%A3%80%E6%9F%A5"></a>可疑的SelfKill检查

我们还在这两个新版本中找到了另一个有趣的检查过程。Kraken现在会检查特定的用户名、特定的文件甚至特定的IP或者国家代码。如果满足这些条件，恶意软件会停止感染系统，执行自删除操作。

[![](https://p2.ssl.qhimg.com/t01efb8bb3058bf6e3e.png)](https://p2.ssl.qhimg.com/t01efb8bb3058bf6e3e.png)

图10. 可疑的SelfKill检查

比如，样本中出现的104.207.76[.]103这个IP地址隶属于意大利的那不勒斯地区。

[![](https://p2.ssl.qhimg.com/t0112fd8f03e8fca782.png)](https://p2.ssl.qhimg.com/t0112fd8f03e8fca782.png)

图11. 使用IPINFO api检查地理位置



## 五、总结

Fortiguard实验室发现了Kraken Cryptor勒索软件的最新版本，该版本从8月份以来一直处于开发状态中。在这个新版样本中，有些bug会导致恶意软件无法运行，或者会禁用老版样本中的一些功能。比如，离线文件加密模块现在会处于禁用状态。我们还发现虽然配置文件经过修改，但主要的功能并没有被大量修改。此外，我们发现虽然这个程序实际上仍处于“beta”状态（因为其中存在许多明显的错误），但开发者依然移除了程序的beta标签。

FortiGuard实验室会继续跟踪这个恶意软件家族。



## 六、解决方案

有以下解决方案能够保护Fortinet用户免受此类威胁：
- FortiGuard反病毒产品能够检测相关文件
- FortiGuard Web过滤服务能够阻止恶意URL及钓鱼URL


## 七、IoC

样本：

信息收集所使用的URL：
