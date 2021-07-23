> 原文链接: https://www.anquanke.com//post/id/85067 


# 【技术分享】打造您自己的Drozer模块，测试Android应用安全 ( 含演示视频）


                                阅读量   
                                **90186**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://blog.attify.com/2015/12/24/creating-your-own-drozer-module-for-android-application-testing/](http://blog.attify.com/2015/12/24/creating-your-own-drozer-module-for-android-application-testing/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0135e0c3d656636145.jpg)](https://p0.ssl.qhimg.com/t0135e0c3d656636145.jpg)

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：160RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**传送门**

[安卓Hacking Part 13:使用Drozer进行安全测试](http://bobao.360.cn/learning/detail/158.html)



**前言**

****

Drozer：Android应用程序安全评估框架

Drozer是一个基于Python的框架，可以用于实现Android应用程序测试的自动化。它由两部分组成：控制台和具有有限权限的Android代理。

Drozer基于客户端-服务器架构，其中客户端安装在本地，而服务器则是Android应用或代理。运行Android应用程序后，它会在端口31415上启动Drozer服务器，端口31415也是与客户端进行通信的端口。

为了启动Drozer，你只需要使用下列命令： 



```
adb forward tcp:31415 tcp:31415
drozer console connect
```

在默认情况下，它只有android.permission.INTERNET权限，所以需要从控制台接收命令。当然，我们也可以给Drozer代理增加其他权限，但如果漏洞只需要默认权限的话，则这样的漏洞的危害性会更严重一些。

[![](https://p4.ssl.qhimg.com/t01530821ca736a3f6a.png)](https://p4.ssl.qhimg.com/t01530821ca736a3f6a.png)

Drozer有一个非常大的优势，即模块化。这就允许用户对该框架的功能进行扩展：通过创建模块来实现漏洞研究和漏洞利用的自动化。

<br>

**Drozer模块入门** 



Drozer模块实际上就是Python类，最简单的情况下，只需要提供必须的元数据（对于所需的元数据，参见Drozer模块编写文档）和execute（）方法即可。另一个常见的方法是add_arguments（）方法，可以通过argparse来轻松解析命令行参数。

Drozer脚本的真正威力来自于它采用了Java的Reflection API，这样的话，就可以允许Python代码在Android的Dalvik VM上创建Java对象并与之交互了。同时，模块作者可以直接使用Android API中提供的所有对象和方法。反射可能是一个比较难以掌握的概念，所以需要通过一些具体的例子来进行说明。

下面，我们以一个收集设备信息的Drozer模块为例，来说明如何使用反射。android.os.BUILD对象可以用来提供设备硬件和操作系统方面的信息。首先，我们需要使用build = self.new（“android.os.Build”）在Python中实例化一个新的构建对象。

然后，我们就可以通过Python使用原生对象的任何功能了！例如，我们可以使用build.BOARD来访问设备主板的信息。若要查看完整的示例的话，请参阅来自Android Security Cookbook的由Keith Makan编写的ex.device.info模块。

编写自己的模块以实现Android安全测试自动化 

让我们通过一个简单的例子来说明如何创建Drozer模块。在本例中，我们将创建一个Drozer模块，让它根据用户提供的号码和消息去创建短信。（这个模块的效果等同于从Android shell中运行am start -a android.intent.action.MAIN –es“sms_body”“message”–es“address”“number”com.android.mms / .ui.ComposeMessageActivity 。）

这个模块中最棘手的部分是构建Intent。在Drozer中，其语法是 ：

```
intent = android.Intent(action=*action*, *additional arguments*)
```

在上面的代码中，我们的动作是android.intent.action.MAIN。我们还需要为intent（“com.android.mms”，“com.android.mms.ui.ComposeMessageActivity”）和extras（由Intent携带的命令）['string'，'address' ，str（arguments.number）]，['string'，'sms_body'，str（arguments.message）]]定义组件。extras的值由用户定义的命令行参数引入。

最后，我们还需要设置一个标志，以便可以在activity上下文['ACTIVITY_NEW_TASK']之外启动一个activity。

把它们放在一起，我们最终得到intent = android.Intent（action = act，component = cmp，extras = extr，flags = flg）。为了便于理解，这里我为构建Intent所需的每个参数创建了相应的变量。

[![](https://p2.ssl.qhimg.com/t01560e8fba1b696eb2.png)](https://p2.ssl.qhimg.com/t01560e8fba1b696eb2.png)

做好上述准备后，我们接下来需要启动Activity并传递Intent以创建短信。在Drozer中，这相当于self.getContext().startActivity(intent.buildIn(self))。

<br>

**安装和运行Drozer模块** 



在编写并保存模块（这里命名为ex.SMS.create）之后，需要先安装，然后才能使用该模块。Drozer推荐通过创建自己的repository来安装自定义模块，以防止将来升级出现问题。

若要创建repository并安装模块，您需要先进入Drozer控制台。您可以使用下列命令来创建repository：

```
module repository create /absolute-path-to-new-repo
```

然后，可以利用下列命令来安装模块：

```
module install /absolute/ex.SMS.create
```

当存在多个模块repository的时候，Drozer会要求您选择具体安装哪个repository。

最后，你可以利用下列命令来运行相应的模块：

```
run ex.SMS.create -n *telephone number* -m *message to send*
```

这个简单的模块可以进一步进行扩展，加入对用户输入和Intent的验证功能。或者，您也可以编写一个Drozer模块，来利用Android中的SMS重发漏洞（CVE-2014-8610）。

但不论是哪种情况，如果您计划使用Drozer并创建自己的模块，那么我都会强烈建议您安装mwrlabs.developer模块。此模块提供了一个交互式的shell，您可以使用它来测试Java对象的创建和交互。

现在，你已经为编写并共享Drozer模块做好了充分的准备，在它们的帮助下，你的Android应用程序测试工作将会变得更加轻松！

ex.SMS.create模块的完整代码：

```
from drozer import android
from drozer.modules import Module
 
class Create(Module):
 
    name = "Create an SMS"
    description = "A sample module to create an SMS"
    examples = """ run ex.SMS.create -n 1234567 -m "Hello, World!" """
    date = "2015-12-20"
    author = "Norman"
    license = "GNU GPL"
    path = ["ex","SMS"]
 
    def add_arguments(self, parser):
        parser.add_argument("-n", "--number", default=None, help="telephone number")
        parser.add_argument("-m", "--message", default=None, help="message")
 
    def execute(self, arguments):
        act = "android.intent.action.MAIN"
        cmp = ("com.android.mms", "com.android.mms.ui.ComposeMessageActivity")
        extr = [['string', 'address', str(arguments.number)],['string', 'sms_body', str(arguments.message)]] 
        flg = ['ACTIVITY_NEW_TASK'] 
 
        # Build Intent
        intent = android.Intent(action=act, component=cmp, extras=extr, flags=flg)
        # Start Activity
        self.getContext().startActivity(intent.buildIn(self))
```

**<br>**

**演示视频**







**传送门**

[安卓Hacking Part 13:使用Drozer进行安全测试](http://bobao.360.cn/learning/detail/158.html)


