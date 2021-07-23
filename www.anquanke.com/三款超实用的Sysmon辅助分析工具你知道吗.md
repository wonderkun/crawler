> 原文链接: https://www.anquanke.com//post/id/182858 


# 三款超实用的Sysmon辅助分析工具你知道吗


                                阅读量   
                                **224580**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01104909485cd30957.png)](https://p0.ssl.qhimg.com/t01104909485cd30957.png)



做过应急响应的朋友，对Sysmon应该都比较熟悉了，它是一款强大的轻量级监控工具，由Windows Sysinternals出品的，Windows Sysinternals出品的一系列工具集中，有很多强大的工具，有兴趣的可以下载这款工具进行研究学习，如果对这款工具还不熟悉的，可以参考之前发的一篇文章：【工具】微软sysmon使用总结，也可以去官网下载使用手册学习

Sysmon用来监视和记录系统活动，并记录到windows事件日志，可以提供相关进程创建、网络连接和文件创建更改时间等详细信息，这篇文章给大家介绍三个非常实用的Sysmon辅助分析工具，这三款工具如下所示：

Sysmon View：Sysmon日志可视化工具

Sysmon Shell：Sysmon配置文件生成工具

Sysmon Box：Sysmon和网络捕获日志记录工具

Sysmon View

Sysmon View通过使用现有事件数据(例如可执行文件名称、会话GUID、事件创建时间等)对各种Sysmon事件进行逻辑分组和关联来帮助跟踪和可视化Sysmon日志，然后该工具重新排列此数据以供显示进多个视图

[![](https://p0.ssl.qhimg.com/t0147e472db71a7f69d.png)](https://p0.ssl.qhimg.com/t0147e472db71a7f69d.png)

使用方法

首先，使用内置的WEVTUtil工具将Sysmon事件导出到XML文件，使用命令如下所示：

WEVTUtil query-events “Microsoft-Windows-Sysmon/Operational” /format:xml /e:sysmonview &gt; eventlog.xml

导出后，运行Sysmon View并导入生成的eventlog.xml文件

(注意：文件只需要导入一次，后续运行Sysmon View不需要再次导入数据文件，只需要使用菜单File-&gt;Load existing data再次加载以前导入的数据即可)

所以的数据文件导入名为SysmonViewDB的SQLite数据库文件，该文件与Sysmon View可执行文件在同一个目录位置，可以与其他人共享此文件，只需将文件放到Sysmon View同目录位置并使用菜单File-&gt;Load existing data导入数据库文件即可

每次导入新的xml文件时，都会删除原来生成的数据库文件，并创建新的数据库文件，要保留以前导入的数据，可以将生成的数据库文件复制到其他位置或重命名为其他名字，以副本的形式保存

生成的数据库文件可以使用SQLite管理软件直接查询数据库文件数据，无需使用Sysmon View

Sysmon View工具包含四个视图菜单选项：Process View、Map View、All Events View，Hierarchy、下面我们来分别介绍这四个视图的作用

Process View

此视图只是帮助关注“运行会话”的摘要，例如，分析人员可以从可执行文件名（例如cmd.exe）或事件类型（例如网络事件）开始，从那里进一步过滤即可例如，应用于查找源自相同二进制文件但来自不同位置的运行会话。此视图利用进程GUID过滤每个会话“运行”的事件，选择任何正在运行的会话（来自GUID列表）将在简单的数据流视图中显示所有其他相关（相关）事件，使用时间排序事件。

只需双击视图中的任何事件即可访问Sysmon事件详细信息，例如，显示Process Creation事件的详细信息(事件ID 1)，显示，如下所示：

[![](https://p2.ssl.qhimg.com/t014c06e5fc364058d7.png)](https://p2.ssl.qhimg.com/t014c06e5fc364058d7.png)

Map View

在事件导入过程中，有一个地理定位IP地址的选项，如果设置，Sysmon View将尝试使用[https://ipstack.com/service](https://ipstack.com/service) 对网络目标进行地理定位，如下所示：

[![](https://p3.ssl.qhimg.com/t01a1978842aad3e349.png)](https://p3.ssl.qhimg.com/t01a1978842aad3e349.png)

ipstack.com可对目标IP地址进行地理定位，地图视图中，通过使用网络事件作为起点，可以轻松地在相关（相关）事件之间导航，同样，该工具可以使用正在运行的进程会话GUID来实现此目的。要浏览相关事件，请使用会话GUID的超链接，类似于流程视图的新视图将显示在包含所有相关会话事件的新窗口中，如下所示：

[![](https://p3.ssl.qhimg.com/t01272e12ab8c03bb01.png)](https://p3.ssl.qhimg.com/t01272e12ab8c03bb01.png)

All Events View

用于对所有Sysmon收集的事件数据进行完整搜索，还有助于查看与其他事件无关的事件，例如“已加载驱动程序”事件类型。除了事件详细信息之外，通过单击FID链接，仍然使用进程GUID提供相关事件之间的导航，如下所示：

[![](https://p0.ssl.qhimg.com/t01e5a940c37c6d431e.png)](https://p0.ssl.qhimg.com/t01e5a940c37c6d431e.png)

此外，所有事件视图支持按机器名称，事件类型或GUID的事件的类似枢轴（分组）排列，如下所示：

[![](https://p0.ssl.qhimg.com/t0108402aa3bd910024.png)](https://p0.ssl.qhimg.com/t0108402aa3bd910024.png)

多个分组级别也是可能的，如下所示：

[![](https://p3.ssl.qhimg.com/t01ffbae8c0b194b039.png)](https://p3.ssl.qhimg.com/t01ffbae8c0b194b039.png)

Hierarchy

显示进程父子层次级别关系，并标注进程是否已结束，如下所示：

[![](https://p4.ssl.qhimg.com/t011c12935142affa08.png)](https://p4.ssl.qhimg.com/t011c12935142affa08.png)

实例讲解

1.先安装Sysmon工具，具体的使用方法，可以参考Sysmon使用手册，网站链接：

[https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)

使用默认设置安装，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a010cc3fbd0e80ff.png)

2.使用WEVTUtil生成Sysmon的XML文件，如下所示：

[![](https://p1.ssl.qhimg.com/t01a1ec0ca40571254e.png)](https://p1.ssl.qhimg.com/t01a1ec0ca40571254e.png)

3.使用Sysmon View打开生成的eventlog.xml文件，如下所示：

[![](https://p4.ssl.qhimg.com/t014eba25fc234f6561.png)](https://p4.ssl.qhimg.com/t014eba25fc234f6561.png)

XML文件分析完成，如下所示：

[![](https://p0.ssl.qhimg.com/t012a4c533fadf6c43c.png)](https://p0.ssl.qhimg.com/t012a4c533fadf6c43c.png)

4.然后就可以开始分析了，查看进程信息，如下所示：

[![](https://p3.ssl.qhimg.com/t015a57b287fedc6007.png)](https://p3.ssl.qhimg.com/t015a57b287fedc6007.png)

后面的就按上面的方法进行分析就可以了

Sysmon Shell

很多人不会写Sysmon的配置文件，这款工具可以通过简单的GUI界面帮助编写和应用Sysmon XML配置，对很多人来说，应该是非常方便的一个工具，如下所示：

[![](https://p3.ssl.qhimg.com/t016251cdb14d50fe74.png)](https://p3.ssl.qhimg.com/t016251cdb14d50fe74.png)

除了导出Sysmon事件日志外，Sysmon Shell还可以用于探索Sysmon可用的各种配置选项，轻松应用和更新XML配置，简而言之：

1)Sysmon Shell可以加载Sysmon XML配置文件：当前版本支持所有Sysmon架构。（该工具不直接从注册表加载任何配置，仅从XML文件加载）。

2)可以将最终的XML导出/保存到文件中。

3)可以通过Sysmon.exe -c command直接调用（在安装Sysmon的同一文件夹中创建临时XML文件）来应用生成的XML配置文件，因此，如果使用此功能，Sysmon Shell将需要提升的权限（需要继承此权限）从Sysmon进程本身），应用配置的输出将显示在预览平台中（这是Sysmon生成的输出）

4)可以在保存在预览窗格中之前预览XML配置

5)最后一个选项卡（标记为“Logs Export”）可能会很方便地将Sysmon事件日志快速导出到XML，以后可以使用“Sysmon View”进行事件分析，导出有三个选项：

*仅出口

*导出并清除Sysmon事件日志

*导出，备份evtx文件并清除事件日志

该实用程序具有从Sysmon Sysinternals主页

([https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)获取的所有事件类型的说明](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)%E8%8E%B7%E5%8F%96%E7%9A%84%E6%89%80%E6%9C%89%E4%BA%8B%E4%BB%B6%E7%B1%BB%E5%9E%8B%E7%9A%84%E8%AF%B4%E6%98%8E)

Sysmon Shell 捆绑了许多由其他安全专业人员创建的Sysmon配置模板，如下所示：

[![](https://p2.ssl.qhimg.com/t0130c989ae74cc204e.png)](https://p2.ssl.qhimg.com/t0130c989ae74cc204e.png)

可以看到这款工具非常强大，里面有各种配置可以选择，实例讲解，我这边以进程创建为例，如下所示：

[![](https://p2.ssl.qhimg.com/t01f7523bb0b39af754.png)](https://p2.ssl.qhimg.com/t01f7523bb0b39af754.png)

导出Sysmon的配置文件，如下所示：

[![](https://p3.ssl.qhimg.com/t0180014a218e9303a6.png)](https://p3.ssl.qhimg.com/t0180014a218e9303a6.png)

Sysmon Box

是一款小实用程序，可以帮助构建捕获Sysmon和网络流量的数据库

[![](https://p5.ssl.qhimg.com/t01410e978fa1566a6e.png)](https://p5.ssl.qhimg.com/t01410e978fa1566a6e.png)

要运行Sysmon Box，请使用以下命令(Sysmon需要启动并与tshark一起运行)：

SysmonBox -in Wi-Fi

然后该工具将执行以下操作：

1)开始捕获流量(在后台使用tshark，这就是你必须指定捕获接口的原因)，完成后点击CTRL + C结束会话

2)然后，Sysmon Box将停止流量捕获，将所有捕获的数据包转储到文件，并使用EVT实用程序导出在会话的开始和结束时间之间记录的Sysmon日志

3)使用来自Sysmon的导入日志和捕获的流量构建Sysmon View数据库(备份现有)文件，您所要做的就是从同一文件夹运行Sysmon视图或将数据库文件(SysmonViewDB)放在与Sysmon View相同的文件夹中(保持数据包捕获在同一位置)

三款工具的下载地址：[https://github.com/nshalabi/SysmonTools，](https://github.com/nshalabi/SysmonTools%EF%BC%8C) 通过这三款辅助分析工具可以非常直观的查看sysmon的监控信息，对应急响应人员来说真的是太方便了，这三款工具功能还有很多，可以下载工具之后自行研究学习

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/-qjVKnDYnvEj7poEG2fkaw)
