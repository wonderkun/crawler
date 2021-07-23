> 原文链接: https://www.anquanke.com//post/id/86057 


# ​【技术分享】Android App常见安全问题演练分析系统-DIVA-Part2


                                阅读量   
                                **102117**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/cracking-damn-insecure-and-vulnerable-app-diva-part-2/](http://resources.infosecinstitute.com/cracking-damn-insecure-and-vulnerable-app-diva-part-2/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01a8dac4a2381431a0.jpg)](https://p0.ssl.qhimg.com/t01a8dac4a2381431a0.jpg)





翻译：[**houjingyi233**](http://bobao.360.cn/member/contribute?uid=2802394681)

**预估稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**传送门**

[**【技术分享】Android App常见安全问题演练分析系统-DIVA-Part1**](http://bobao.360.cn/learning/detail/3048.html)



APK下载：[http://payatu.com/wp-content/uploads/2016/01/diva-beta.tar.gz](http://payatu.com/wp-content/uploads/2016/01/diva-beta.tar.gz) 

源代码下载：[https://github.com/payatu/diva-android](https://github.com/payatu/diva-android)

前一部分我们讨论了不安全的日志输出、硬编码问题和不安全的数据存储。这一部分我们继续讨论android app中其它的常见安全问题。

<br>

**VII. 问题4 ：输入验证问题**

在APP中点击“7. INPUT VALIDATION ISSUES – PART 1”。如果你知道用户名，你就能取得与之相关的数据。我们的目标是在不知道用户名的情况下获取所有的数据。点击之后你会看到下面的activity页面。

[![](https://p4.ssl.qhimg.com/t0183b5214a3414c4de.png)](https://p4.ssl.qhimg.com/t0183b5214a3414c4de.png)

由于它具有搜索功能，我的第一个假设是应用程序可能会根据用户输入从数据库中搜索某些内容。会存在SQL注入漏洞么？？？我们需要测试一下。这次我们来做一个黑盒测试而不是先看代码。让我们输入一个单引号，看看应用程序的响应。

[![](https://p0.ssl.qhimg.com/t0195ca7eb8cbb84f96.png)](https://p0.ssl.qhimg.com/t0195ca7eb8cbb84f96.png)

看起来没有什么反应，但是在logcat中我找到了下面的条目。

[![](https://p2.ssl.qhimg.com/t0192ca0fb318b67fae.png)](https://p2.ssl.qhimg.com/t0192ca0fb318b67fae.png)

好消息!可能存在SQL注入。从上面的错误可以看出，程序使用SQL查询从SQLite数据库中获取信息，而我们输入的单引号造成语句中单引号没有配对，从而出错。我们再加一个单引号，看看app有什么反应。

[![](https://p0.ssl.qhimg.com/t0112d2f9162a064b20.png)](https://p0.ssl.qhimg.com/t0112d2f9162a064b20.png)

看起来程序正在搜索输入的数据，没有产生SQL错误。为了进一步确认，我们再加一个单引号，看看是否会引发SQL错误。

[![](https://p4.ssl.qhimg.com/t01fe1e614f26dcc3d3.png)](https://p4.ssl.qhimg.com/t01fe1e614f26dcc3d3.png)

logcat中再次看到了下面的结果。

[![](https://p5.ssl.qhimg.com/t019b3e5d760d8cc0e3.png)](https://p5.ssl.qhimg.com/t019b3e5d760d8cc0e3.png)

完美!现在确认了SQL注入，奇数个单引号会导致SQL错误，当引号刚好匹配时SQL查询正好会执行。下一步呢？我们使用一个总是返回true的字符串来得到数据库中的数据。

```
1’ or ‘1’ != ‘2
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011de7d84edcbf0b71.png)

如图所示，通过执行恶意的SQL查询我们能够得到应用数据库中的所有数据。下面是导致问题的SQLInjectionActivity.class中的一部分代码。

[![](https://p0.ssl.qhimg.com/t016b66129d4cee3e1a.png)](https://p0.ssl.qhimg.com/t016b66129d4cee3e1a.png)

下面这句代码正是导致问题的罪魁祸首，app接收了用户的输入，没有经过验证就直接加入到SQL查询语句中。

```
cr = mDB.rawQuery("SELECT * FROM sqliuser WHERE user = '" + srchtxt.getText().toString() + "'", null);
```

  在app中点击“8. INPUT VALIDATION ISSUES – PART 2”。这个activity的功能是显示用户输入的网页。如图，当你输入www.baidu.com它会使用一个webview去加载这个页面。

[![](https://p2.ssl.qhimg.com/t018745d66c3f784695.png)](https://p2.ssl.qhimg.com/t018745d66c3f784695.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015ef918558e0263c9.png)

 我们的目标是使用此功能访问设备上的敏感信息。先来看看它的源代码，在InputValidation2URISchemeActivity.java中。

[![](https://p3.ssl.qhimg.com/t0153029b9943b6961a.png)](https://p3.ssl.qhimg.com/t0153029b9943b6961a.png)

程序使用loadUrl方法加载用户输入的URL，这个方法也可以加载本地文件。我们创建一个1.txt，在里面写上123。

 

[![](https://p1.ssl.qhimg.com/t0199658ef77ca3c291.png)](https://p1.ssl.qhimg.com/t0199658ef77ca3c291.png)

把这个文件传到sdcard上。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0140611d6c57478124.png)

使用file:///格式来读取文件。

[![](https://p2.ssl.qhimg.com/t01666ede6a8f223191.png)](https://p2.ssl.qhimg.com/t01666ede6a8f223191.png)

成功读取了文件内容。

在app中点击“13. INPUT VALIDATION ISSUES – PART 3”。这个程序要求输入一个密码，我们的目标是在不知道密码的情况下让程序崩溃。

[![](https://p1.ssl.qhimg.com/t019fd431282aefa663.png)](https://p1.ssl.qhimg.com/t019fd431282aefa663.png)

我们一次性多输入一些字符串，程序就会崩溃并退出。我输入了一串a，现在让我们用adb logcat命令查看在logcat中是否有对我们有用的信息。

[![](https://p0.ssl.qhimg.com/t01ddbf8dd2909d9714.png)](https://p0.ssl.qhimg.com/t01ddbf8dd2909d9714.png)

从上面logcat中可以看出，很显然崩溃是因为CPU试图跳转到61616160地址处发生的，a的ASCII值就是0x61。我们来看看InputValidation3Activity.java中的源代码。

[![](https://p3.ssl.qhimg.com/t01d210267eff373242.png)](https://p3.ssl.qhimg.com/t01d210267eff373242.png)

 <br>

这个校验是在native层做的，来看看divajni.c。

  

[![](https://p4.ssl.qhimg.com/t016f88f21d6433f63e.png)](https://p4.ssl.qhimg.com/t016f88f21d6433f63e.png)

[![](https://p5.ssl.qhimg.com/t0107c61f240b8de81e.png)](https://p5.ssl.qhimg.com/t0107c61f240b8de81e.png)

Buffer的大小是20，由于strcpy函数缺少边界检查导致缓冲区溢出，程序崩溃。理论上来讲这个漏洞还可以继续进一步利用，如果大家有兴趣深入研究的话可以参考这篇文章[ARM栈溢出攻击实践：从虚拟环境搭建到ROP利用](http://www.freebuf.com/articles/terminal/107276.html)。

<br>

**VIII 问题 5：访问控制问题**

在APP中点击“9.ACCESS CONTROL ISSUES – PART 1”。你会看到下面的界面。    

[![](https://p1.ssl.qhimg.com/t018384ea2ca1b3b12a.png)](https://p1.ssl.qhimg.com/t018384ea2ca1b3b12a.png)

我们可以通过点击上述活动中显示的“VIEW API CREDENTIALS”按钮访问API凭据。

[![](https://p2.ssl.qhimg.com/t013d14c0568d410b2b.png)](https://p2.ssl.qhimg.com/t013d14c0568d410b2b.png)

我们的目标是在不点击此按钮的情况下访问这些信息。看看AndroidManifest.XML文件中与Vendor API Credentials activity相关的信息。

  

[![](https://p4.ssl.qhimg.com/t012bd830e72e0dd7af.png)](https://p4.ssl.qhimg.com/t012bd830e72e0dd7af.png)

如果你注意到以上的信息，你就会发现activity是通过intent filter“保护”的。intent filter不应该被作为一种保护机制。当intent filter和像activity这样的组件一起使用时，组件是被暴露在外的。这里的activity可以被其它应用从外部加载，这是非常不安全的。我们可以通过终端中下面的命令来验证。

[![](https://p2.ssl.qhimg.com/t018c2a40198888a007.png)](https://p2.ssl.qhimg.com/t018c2a40198888a007.png)

上面的命令通过-a参数指定intent。虽然adb shell am start jakhar.aseem.diva/.APICredsActivity命令也能起到同样的作用，但是这是一种更普遍的方式。

在APP中点击“10.ACCESS CONTROL ISSUES – PART 2”。你会看到下面的界面。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019f2d95ad5278938d.png)

如果你是注册用户，你就能访问tweeter API的凭据。我们的目标是在不注册的情况下访问它。再次看看AndroidManifest.XML文件。

[![](https://p5.ssl.qhimg.com/t0135fe3657ef0345af.png)](https://p5.ssl.qhimg.com/t0135fe3657ef0345af.png)

看起来和前面并没有什么区别。我们试试下面的命令看看能否成功。

[![](https://p2.ssl.qhimg.com/t0152742e4e0321898e.png)](https://p2.ssl.qhimg.com/t0152742e4e0321898e.png)

当我们运行上述命令之后会看到下面的界面。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0149475ed2615cdf8d.png)

看来程序还有一些额外的检查。让我们看看源代码文件APICreds2Activity.java。

[![](https://p1.ssl.qhimg.com/t01a4d773db388d956d.png)](https://p1.ssl.qhimg.com/t01a4d773db388d956d.png)

可以看出，当我们用ADB命令启动intent时需要一个额外的布尔类型参数。下面这一行解析字符串chk_pin。

```
boolean bcheck=i.getBooleanExtra(getString(R.string.chk_pin),true);
```

我们可以在strings.xml中查找它实际对应的值。

[![](https://p2.ssl.qhimg.com/t01a0bb89fd9aa231e2.png)](https://p2.ssl.qhimg.com/t01a0bb89fd9aa231e2.png)

下一行是检查check_pin值是否为false。这个条件是用来验证用户是否已经注册的，可以从AccessControl2Activity.java的以下代码中看出。

[![](https://p0.ssl.qhimg.com/t0186dc8deaa5fc190e.png)](https://p0.ssl.qhimg.com/t0186dc8deaa5fc190e.png)

如果用户已经注册，check_pin会被设置为false，否则被设置为true。当check_pin被设置为false时，应用程序没有进行其它检查。所以，让我们尝试将这个额外的参数传递给intent，看看它是否有效。

[![](https://p2.ssl.qhimg.com/t013b986374bb105bac.png)](https://p2.ssl.qhimg.com/t013b986374bb105bac.png)

-ez参数传递一个类型为boolean的键值对。运行上述命令将显示以下内容。

[![](https://p0.ssl.qhimg.com/t0149ba6be55af7bd12.png)](https://p0.ssl.qhimg.com/t0149ba6be55af7bd12.png)

和前面一样，adb shell am start -n jakhar.aseem.diva/.APICreds2Activity -ez check_pin false也是可以的。

在APP中点击“11.ACCESS CONTROL ISSUES – PART 3”。你会看到下面的界面。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e74b0ce337718028.png)

我们输入一个新的PIN码。一旦你这样做，将出现一个新的按钮，如下所示。

[![](https://p4.ssl.qhimg.com/t014959c6c1bacc4ca5.png)](https://p4.ssl.qhimg.com/t014959c6c1bacc4ca5.png)

点击这个按钮，它将启动一个新的activity，如下所示。

[![](https://p1.ssl.qhimg.com/t012928a7457576bb4f.png)](https://p1.ssl.qhimg.com/t012928a7457576bb4f.png)

我们可以通过输入之前设置的PIN来访问私人笔记。

[![](https://p4.ssl.qhimg.com/t017b643deff3fbcc88.png)](https://p4.ssl.qhimg.com/t017b643deff3fbcc88.png)

我们的目标是在不输入PIN码的情况下访问这些内容。AndroidManifest.XML文件显示程序注册了一个content provider，并且android:exported属性为true。

[![](https://p4.ssl.qhimg.com/t01ca5346c27f98f60e.png)](https://p4.ssl.qhimg.com/t01ca5346c27f98f60e.png)

Content Providers使用以content://开头的URI来表示。我们需要找到访问数据的URI。首先使用apktool反编译apk得到smail代码。<br>

[![](https://p1.ssl.qhimg.com/t0122f023f5a37aeab6.png)](https://p1.ssl.qhimg.com/t0122f023f5a37aeab6.png)

在smail代码目录下搜索包含content://字符串的所有文件。

   

[![](https://p4.ssl.qhimg.com/t010c0e6a6c80b0a0ff.png)](https://p4.ssl.qhimg.com/t010c0e6a6c80b0a0ff.png)

正如我们在AndroidManifest.XML文件中看到的那样，content provider被导出，因此我们可以在没有任何明确许可的情况下查询它。<br>

[![](https://p1.ssl.qhimg.com/t01fe0c674c07760dda.png)](https://p1.ssl.qhimg.com/t01fe0c674c07760dda.png)

<br>

**IX问题 6：硬编码**

前面我们已经研究过一个硬编码问题了。在APP中点击“12. HARDCODING ISSUES – PART 2”。你会看到下面的界面。

[![](https://p4.ssl.qhimg.com/t01f0ddf67240a298ea.png)](https://p4.ssl.qhimg.com/t01f0ddf67240a298ea.png)

我们的目标是找到vendor key并提交给程序。下面是Hardcode2Activity. class中和这个activity相关的反编译代码。有许多工具可以直接得到反编译apk得到java代码，常用的有jadx、JEB、GDA等等。这里我用的是JEB。

[![](https://p1.ssl.qhimg.com/t012724e19124f982ae.png)](https://p1.ssl.qhimg.com/t012724e19124f982ae.png)

看起来这个activity在加载时创建了DivaJni class的一个对象。查看其它文件发现有一个叫做DivaJni.class的文件。

[![](https://p2.ssl.qhimg.com/t01c49a91bd74209202.png)](https://p2.ssl.qhimg.com/t01c49a91bd74209202.png)

程序加载了一个名为divajni的库，解压apk进入lib目录。对于每种架构，都有一个libdivajni.so的实例。随便找一个运行strings命令，看看我们是否可以找到什么有趣的东西。

[![](https://p1.ssl.qhimg.com/t0109f370e74b862295.png)](https://p1.ssl.qhimg.com/t0109f370e74b862295.png)

在windows系统下运行这个命令可以使用SysinternalsSuite中的strings.exe。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0180d11d1618a8ebaa.png)

olsdfgad;lh这个字符串看起来很有趣，我们来试试。

[![](https://p3.ssl.qhimg.com/t01874cd3bde089da5a.png)](https://p3.ssl.qhimg.com/t01874cd3bde089da5a.png)

我们找到了这个key。很显然，将字符串硬编码在so文件中也同样是不安全的。

这个APP中的全部漏洞就讲解完了，希望能为大家学习android应用程序漏洞带来帮助。

<br>



**传送门**

**[【技术分享】Android App常见安全问题演练分析系统-DIVA-Part1](http://bobao.360.cn/learning/detail/3048.html)**
