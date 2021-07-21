> 原文链接: https://www.anquanke.com//post/id/218404 


# 利用 macOS Dock 实现运行代码的执行


                                阅读量   
                                **214401**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者specterops，文章来源：posts.specterops.io
                                <br>原文地址：[https://posts.specterops.io/are-you-docking-kidding-me-9aa79c24bdc1](https://posts.specterops.io/are-you-docking-kidding-me-9aa79c24bdc1)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t016fc5688c6d9f2486.jpg)](https://p2.ssl.qhimg.com/t016fc5688c6d9f2486.jpg)



## 背景

我最近感兴趣的一个方向是macOS的持久化（persistence）。具体地说，我一直在研究底层用户通过修改文件可以影响到用户交互的方法。常用的一种交互方法是`Dock`。

经过研究，我注意到一个控制苹果Dock可见表示的属性表文件（Plist）。这里没有什么突破性的发现，因为最终用户通过图形用户界面（GUI）经常修改这个`plist`。在检查了`plist`中的值之后，我想知道是否可以更改这些值，将一个有效的应用程序替换为一个运行恶意代码的应用程序。

这项研究的结果保存在[`PersistentJXA项目`](https://github.com/D00MFist/PersistentJXA) 的`DockPersist.js`文件中。它会实现用我们的恶意应用程序替换Safari或Chrome。我关注于Safari和Chrome是因为它们很有可能出现在用户的Dock中。但是，请注意，这个攻击适用于任何应用程序。一旦终端用户点击Safari或Chrome图标，它就会运行我们的恶意应用程序。这个持久性方法类似于Windows上的Link （. Lnk）文件，因为Dock图标也属于应用程序的快捷方式的一种。

这个持久化方法需要将我们的恶意应用程序上传到目标程序中。我更喜欢在`Mythic`代理中使用upload函数将应用程序保存在目标上。

修改`plist`后，可以立即重新加载Dock。但是这会给用户带来一次简短的屏幕闪烁。或者您可以等到重新启动时，假的恶意应用程序才出现在Dock中，因为修改过后的`plist`文件在重新启动后仍然存在。



## 使用方法

### <a class="reference-link" name="%E8%AE%BE%E7%BD%AE"></a>设置

这种持久化方法需要将恶意应用程序上传到目标，有许多种方法可以绕过`Gatekeeper`的保护，允许我们将恶意应用程序上传到目标程序中。您可以：

1.压缩应用程序包，在一个`Mythic`代理（Apfell或Poseidon）中使用`upload`命令，然后解压缩到目的地<br>
2.压缩应用程序包，使用`curl`下载压缩程序包，然后解压缩到目的地<br>
3.压缩应用程序包，使用base64编码加密，再base64解码保存到目标上，然后解压缩到目的地

我在Automator中创建了一个PoC应用程序。它试图不产生任何提示的打开Safari，然后它运行我们的恶意有效载荷。

[![](https://p1.ssl.qhimg.com/t0144211d313bd485e2.png)](https://p1.ssl.qhimg.com/t0144211d313bd485e2.png)

为了不引起终端用户的注意，我用Safari罗盘图标替换了默认的自动图标。当然，可以利用`Xcode`创建更复杂的应用程序。

[![](https://p5.ssl.qhimg.com/t01b909da29c16d9bbd.png)](https://p5.ssl.qhimg.com/t01b909da29c16d9bbd.png)

接下来，我压缩应用程序包并将其上传。在解压缩到`/Users/Shared/`之后，我们可以在满足先决条件的情况下重点调用持久化方法。

注意:由于`plist`的二进制格式，自动实现要求伪应用程序命名为`Google Chrome`或“Safari”，并位于`/Users/Shared/`。可以修改`Safari64`和`Chrome64`变量来改变这个位置。

### <a class="reference-link" name="%E8%B0%83%E7%94%A8%E7%9A%84%E6%8C%81%E4%B9%85%E6%80%A7"></a>调用的持久性

将脚本导入`Apfell`代理。

[![](https://p2.ssl.qhimg.com/t01ca54da7d6057d378.png)](https://p2.ssl.qhimg.com/t01ca54da7d6057d378.png)

调用`DockPersist`函数。该函数接受三个参数：应用程序名称（Safari或Google Chrome）、Bundle ID和立即重新加载Dock的配置选项。

注意:Bundle ID在`Info.plist`中。具体位置在`/usr/libexec/PlistBuddy -c 'Print CFBundleIdentifier' ~/FakeApp/Safari.app/Contents/Info.plist`

[![](https://p0.ssl.qhimg.com/t0171e804bd8589f4ab.png)](https://p0.ssl.qhimg.com/t0171e804bd8589f4ab.png)



## 检测

Crescendo是一个快速捕捉单个主机上事件的好工具，它是macOS的实时事件查看器。Crescendo的一个优秀特性是它利用了苹果的端点安全框架（ESF）。ESF是系统扩展框架的一部分，它是一个API，会监视系统事件以发现潜在的恶意活动。拿那些来自Windows端的工具来说，它是一个针对macOS的Windows有限事件跟踪器（ETW）。

使用Crescendo，我们可以很容易地查看我们创建的，持久化的文件和进程。

以下ESF事件会映射到Crescendo中：

ES_EVENT_TYPE_AUTH_EXEC = process::exec<br>
ES_EVENT_TYPE_NOTIFY_EXIT = process::exit<br>
ES_EVENT_TYPE_NOTIFY_CREATE = file::create<br>
ES_EVENT_TYPE_NOTIFY_KEXTLOAD = process:kext::load<br>
ES_EVENT_TYPE_NOTIFY_MOUNT = file::mount<br>
ES_EVENT_TYPE_NOTIFY_UNLINK = file::unlink<br>
ES_EVENT_TYPE_NOTIFY_RENAME = file::rename<br>
ES_EVENT_TYPE_NOTIFY_UIPC_CONNECT = network::ipcconnect<br>
ES_EVENT_TYPE_NOTIFY_FORK = process::fork

注意:虽然Crescendo目前没有捕获`ES_EVENT_TYPE_NOTIFY_MMAP``ES_EVENT_TYPE_NOTIFY_WRITE``ES_EVENT_TYPE_NOTIFY_EXEC`等事件，但是它捕获到了许多这个持久化方法的其他事件。对于其他事件的报道，我强烈建议使用Xorrior的[Appmon](https://bitbucket.org/xorrior/appmon/src/master/)工具。

下面的内容主要关注持久化方法的执行，实际的恶意应用程序结构将根据攻击者开发的内容而有所不同。

首先，`plutil`将`Dock plist`转换为XML语言。XML格式更容易操作。

[![](https://p1.ssl.qhimg.com/t0168bb6f94604885b6.png)](https://p1.ssl.qhimg.com/t0168bb6f94604885b6.png)

此外，用`temp9876`文件记录进程创建。

`DockPersist.j`s在`/private/tmp/`目录下创建一个随机命名的文件。脚本修改`plist`转换出的XML文件版本号后，将其保存在这个随机文件中。在这个例子中，`temp0wsn4p`以XML格式包含了恶意的`plist`文件，因此我们用在Dock中正确加载所需的二进制格式版本覆盖了该文件。

[![](https://p3.ssl.qhimg.com/t01d1c8f39590b3e1bd.png)](https://p3.ssl.qhimg.com/t01d1c8f39590b3e1bd.png)

接下来，`DockPersist.js`删除位于`~/Library/Preferences/com.apple.dock.plist`中现有的`plist`。

[![](https://p5.ssl.qhimg.com/t0137bbe854945229a8.png)](https://p5.ssl.qhimg.com/t0137bbe854945229a8.png)

ESF以二进制格式保存新的恶意`plist`到 `~/Library/Preferences/com.apple.dock.plist`。

[![](https://p5.ssl.qhimg.com/t01eca56df9dc612793.png)](https://p5.ssl.qhimg.com/t01eca56df9dc612793.png)

最后，由于我们在函数调用中指定了重新加载Dock，因此将调用`killall`。

[![](https://p0.ssl.qhimg.com/t01a441b4f35066fcda.png)](https://p0.ssl.qhimg.com/t01a441b4f35066fcda.png)



## 正常执行

您可能想知道的问题是，既然我们已经知道了ESF如何捕获已知的恶意行为，那么ESF如何表示正常的执行呢？

作为常规操作的一部分，`cfprefsd` （Core Foundation Preferences Daemon）将在`com.apple.dock.plist`上触发`file::rename`事件。当用户通过GUI手动更改Dock时，也会触发这些事件。

[![](https://p0.ssl.qhimg.com/t0127f32c45e92067f2.png)](https://p0.ssl.qhimg.com/t0127f32c45e92067f2.png)



## 躲避检测

对手可以执行`plist`修改任务，并将修改后的plist上传到`dock plist`，以减少攻击痕迹。但是，这仍然会导致`file::rename`事件的产生，该事件不会使用我们在标准执行中确定的`cfprefsd`进程。在`cfprefsd`进程之外修改`plist`可能是识别恶意行为的一个很好的出发点。

[![](https://p5.ssl.qhimg.com/t01599c616452fd69a6.png)](https://p5.ssl.qhimg.com/t01599c616452fd69a6.png)



## 视觉效果

PoC的执行会导致在Dock中出现两个Safari实例。

[![](https://p2.ssl.qhimg.com/t013319f30f579fd57c.png)](https://p2.ssl.qhimg.com/t013319f30f579fd57c.png)

第一个Safari是恶意应用程序，它位于plist的`persistent-apps`部分，第二个Safari是真正的Safari，它位于plist的`recent-apps`部分。



## 一些通过Osascript留下的攻击证据

在深入研究ESF日志之后，我注意到一些有趣的条目被写到`SQLite`数据库中。如果对手在使用`osascript`，可能会注意到`osascript`有一个缓存数据库`~/Library/Caches/com.apple.osascript/Cache.db`

在使用SQLite的DB浏览器检查这个数据库时，我注意到`cfurl_cache_response`表包含我们的`Mythic`服务器IP地址和一个简短的`GET`请求日志，该请求连接C2服务器。该缓存为调查取证人员提供了宝贵的证据。

[![](https://p5.ssl.qhimg.com/t01ea8f2837b9f380bb.png)](https://p5.ssl.qhimg.com/t01ea8f2837b9f380bb.png)

使用`sqlite3`命令行工具也可以查看这些条目。

[![](https://p3.ssl.qhimg.com/t01b4ae11c2d05fa08f.png)](https://p3.ssl.qhimg.com/t01b4ae11c2d05fa08f.png)



## 结论

这篇文章展示了一个类似于Windows上的`. LNK`文件的持久化方法。我希望所展示的持久化IoC能够帮助开发人员对该技术进行检测。如果您遇到这个持久化方法创建的上面没有提到的任何其他IoC，请告诉我。



## 参考内容

[https://posts.specterops.io/detection-engineering-using-apples-endpoint-security-framework-affdbcb18b02](https://posts.specterops.io/detection-engineering-using-apples-endpoint-security-framework-affdbcb18b02)

[https://medium.com/red-teaming-with-a-blue-team-mentaility/taking-the-macos-endpoint-security-framework-for-a-quick-spin-802a462dba06](https://medium.com/red-teaming-with-a-blue-team-mentaility/taking-the-macos-endpoint-security-framework-for-a-quick-spin-802a462dba06)

[https://attack.mitre.org/techniques/T1547/009/](https://attack.mitre.org/techniques/T1547/009/)

[https://developer.apple.com/documentation/endpointsecurity?language=objc](https://developer.apple.com/documentation/endpointsecurity?language=objc)

[https://github.com/SuprHackerSteve/Crescendo](https://github.com/SuprHackerSteve/Crescendo)

[https://bitbucket.org/xorrior/appmon/src/master/](https://bitbucket.org/xorrior/appmon/src/master/)

[https://sqlitebrowser.org/](https://sqlitebrowser.org/)

[https://eclecticlight.co/2017/07/06/sticky-preferences-why-trashing-or-editing-them-may-not-change-anything/](https://eclecticlight.co/2017/07/06/sticky-preferences-why-trashing-or-editing-them-may-not-change-anything/)
