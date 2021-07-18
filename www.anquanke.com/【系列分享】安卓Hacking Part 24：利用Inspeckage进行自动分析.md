
# 【系列分享】安卓Hacking Part 24：利用Inspeckage进行自动分析


                                阅读量   
                                **134294**
                            
                        |
                        
                                                                                                                                    ![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/android-hacking-and-security-part-24-automated-analysis-with-inspeckage/#article](http://resources.infosecinstitute.com/android-hacking-and-security-part-24-automated-analysis-with-inspeckage/#article)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85839/t0127fe73337bf7a900.jpg)](./img/85839/t0127fe73337bf7a900.jpg)**

****

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**概述 **

在本系列的前一篇文章中，我们讨论了如何使用AndBug来“钩住”给定Android应用程序中的类和方法。在本文中，我们将讨论另一个非常有用的实用程序Inspeckage。Inspeckage是一个Xposed模块，可用于Android应用程序的动态分析。无论是在恶意软件分析方面，还是在渗透测试领域，Inspeckage都具有突出的特点，因此该软件的前途将一片光明。Inspeckage还带有一个内置的网络服务器，可以使用简洁优美的GUI来执行所有操作。

<br>

**配置Inspeckage**

如果您以前已经使用过Xposed Framework的话，那么对您来说Inspeckage的设置将易如反掌。

1.	在已经取得root权限的设备上下载并安装Xposed Framework。

2.	接下来，启动Xposed应用程序，如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b8d45e1f3a727e4c.png)

3.	点击Modules按钮，这里应该什么都没有，因为我们还没有安装任何模块。

4.	现在，我们可以从下面链接下载安装Inspeckage模块了。

    [http://repo.xposed.info/module/mobi.acpm.inspeckage](http://repo.xposed.info/module/mobi.acpm.inspeckage) 

    另一种方法是使用Xposed App的下载选项并搜索Inspeckage，如下所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ceda5b54a5e63f53.png)

我们可以点击这个模块，这时将会看到以下窗口。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018bcd296f154d205b.png)

点击“Download”按钮，如果下载成功则出现“Install”按钮，如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a026eceaeac5660e.png)

点击“Install”按钮，安装应用程序。您需要接受Inspeckage在此过程中请求的权限。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01443ae85052731dac.png)

上图表明Inspeckage已成功安装。

5.	现在，导航到Xposed应用程序，然后再次单击Modules，您应该看到刚才安装的新模块，具体如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011436a633c73535a4.png)

选中上图右侧的复选框，执行软重启，使更改生效。为此，我们可以导航到Xposed中的Framework功能，并点击Soft Reboot按钮来完成，如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b60e80182271e1fe.png)

重新启动后，点击Xposed模块中的Inspeckage模块，您将看到以下窗口。在这里，我们可以看到设备上安装的应用程序列表。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f1528806f61962b5.png)

我们也可以选择待分析的应用程序。我选择了一个名为“Secure Store”的应用程序，这是我专门创建的一个易受攻击的应用程序。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0153d3c8dd64eaa2b7.png)

单击“Launch App”并浏览应用程序的全部功能。在运行目标应用程序时，Inspeckage将监视应用程序执行的各种调用。我们还可以通过指定类名和方法名来钩住方法，然后观察传递的参数及返回值。这方面的内容，我们将在本文后面部分进行具体介绍。

此外，上述窗口中还有一些地址，它们可用于访问用户界面，具体如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e917093e67e4a1f2.png)

访问用户界面时我们会发现，这里有许多不同的部分，具体如上图所示。在本文的下面几节中，我们会针对上面标出的那些部分展开详细的介绍。

我们可以看到与应用程序有关的基本信息，其中包括备份属性，包名称和数据目录位置。有趣的是，点击“Tree View”按钮可以了解应用程序的应用程序目录中有什么文件可用，如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bf09844a6d4b5a66.png)

接下来，点击“Package information”部分将会显示应用程序使用的组件清单。在本例中，我们有一个导出activity和三个非导出activity。我们也可以使用“Start Activity”功能强制启动activity。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b413b1d0652d2599.png)

另外，我们还可以看到应用程序当前使用的权限，如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01864dfd03480a197f.png)

接下来，让我们转到SQLite部分。它能够显示应用程序是否执行了SQLite查询，如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0161bc1bf632b9fa49.png)

如果有可用的提供者的话，我们也可以使用“Query Provider”功能来查询内容提供者。

做了标记的下一部分是“Shared Preferences”。Inspeckage会分别显示读调用和写调用。下图表明应用程序使用共享首选项在“userdata.xml”文件中存储“auth token”。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01058b5d046956e439.png)

之后，应用程序会读取前面存储的令牌，这可以从下图中标记为27的条目中看到。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015e94f5690d39f932.png)

接下来，我们来考察WebView部分。Inspeckage还发现，目标应用程序正在使用WebView addJavaScriptInterface，它的作用是充当JavaScript与Java交互的桥梁。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011fc3de058164def1.png)

如果应用程序的API级别小于17，则可以利用这个远程代码来执行漏洞。

**<br>**

**添加钩子**

我们跳转到+ Hooks标签。这是一个非常有趣的部分，因为我们可以给特定的方法添加钩子，从而监视这个方法运行时会发生什么。

我们在应用程序中两个不同方法添加了钩子，并观察Inspeckage是如何进行处理的。

**<br>**

**情形1**

我们可以通过逆向应用程序来得到类名和方法名。在浏览此应用程序的源代码时，我们发现“isUserAlreadyLoggedIn”是一个看起来很有趣的方法。让我们添加一个钩子，如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0159df2c1986d95076.png)

我们指定了类名和方法名。如果你也想“钩住”构造函数，你就可以这样做。

现在运行应用程序，当应用程序调用此方法时，您应该会看到相应的参数和返回值，具体如下图所示。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01db04e68d0f43d485.png)

您可以看到，该方法返回“false”，但是它没有参数。

**<br>**

**情形2**

现在，我们来考察带有方法参数的例子。让我们删除现有的钩子，并添加一个新的钩子，如下所示（你可以同时拥有多个钩子）。这里“isLoggedIn”是方法名称，请注意，类名也不同。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013c8389b8c1ed3367.png)

一旦完成上述操作，我们需要再次运行应用程序，这样就应该能够看到参数以及返回值了。

[![](./img/85839/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015265c4e71e0b5420.png)

上图显示了传递给hooked方法的参数。我们也注意到有一个返回值为“true”。

<br>

**小结 **

毫无疑问,在Android应用程序的动态分析方面，Inspeckage模块是非常有用的。如果您正在分析恶意软件或进行渗透测试的话，Inspeckage能够帮您显著提高工作效率。作为Xposed模块，Inspeckage执行检查的方式绝对算得上强大和可靠的，因为它能够被分析的设备和目标应用程序的完全控制。

<br>

传送门

[](http://bobao.360.cn/learning/detail/122.html)

[安卓 Hacking Part 1：应用组件攻防（连载）](http://bobao.360.cn/learning/detail/122.html)

[安卓 Hacking Part 2：Content Provider攻防（连载）](http://bobao.360.cn/learning/detail/127.html)

[安卓 Hacking Part 3：Broadcast Receivers攻防（连载）](http://bobao.360.cn/learning/detail/126.html)

[安卓 Hacking Part 4：非预期的信息泄露（边信道信息泄露）](http://bobao.360.cn/learning/detail/133.html)

[安卓 Hacking Part 5：使用JDB调试Java应用](http://bobao.360.cn/learning/detail/138.html)

[安卓 Hacking Part 6：调试Android应用](http://bobao.360.cn/learning/detail/140.html)

[安卓 Hacking Part 7：攻击WebView](http://bobao.360.cn/learning/detail/142.html)

[安卓 Hacking Part 8：Root的检测和绕过](http://bobao.360.cn/learning/detail/144.html)

[安卓 Hacking Part 9：不安全的本地存储：Shared Preferences](http://bobao.360.cn/learning/detail/150.html)

[安卓 Hacking Part 10：不安全的本地存储](http://bobao.360.cn/learning/detail/152.html)

[安卓 Hacking Part 11：使用Introspy进行黑盒测试](http://bobao.360.cn/learning/detail/154.html)

[安卓 Hacking Part 12：使用第三方库加固Shared Preferences](http://bobao.360.cn/learning/detail/156.html)

[安卓 Hacking Part 13：使用Drozer进行安全测试](http://bobao.360.cn/learning/detail/158.html)

[安卓 Hacking Part 14：在没有root的设备上检测并导出app特定的数据](http://bobao.360.cn/learning/detail/161.html)

[安卓 Hacking Part 15：使用备份技术黑掉安卓应用](http://bobao.360.cn/learning/detail/169.html)

[安卓 Hacking Part 16：脆弱的加密](http://bobao.360.cn/learning/detail/174.html)

[安卓 Hacking Part 17：破解Android应用](http://bobao.360.cn/learning/detail/179.html)

[安卓 Hacking Part 18：逆向工程入门篇](http://bobao.360.cn/learning/detail/3648.html)

[**安卓 Hacking Part 19：NoSQL数据库不安全的数据存储**](http://bobao.360.cn/learning/detail/3653.html)

[**安卓 Hacking Part 20：使用GDB在Android模拟器上调试应用程序**](http://bobao.360.cn/learning/detail/3677.html)

[**安卓 Hacking Part 22：基于Cydia Substrate扩展的Android应用的钩子和补丁技术**](http://bobao.360.cn/learning/detail/3679.html)

[**安卓 Hacking Part 23：基于AndBug的Android应用调试技术**](http://bobao.360.cn/learning/detail/3681.html)
