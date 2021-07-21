> 原文链接: https://www.anquanke.com//post/id/86045 


# 【技术分享】AppleScript：macos下隐藏的钓鱼威胁


                                阅读量   
                                **103771**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：duo.com
                                <br>原文地址：[https://duo.com/blog/the-macos-phishing-easy-button-applescript-dangers](https://duo.com/blog/the-macos-phishing-easy-button-applescript-dangers)

译文仅供参考，具体内容表达以及含义原文为准

**![](https://p0.ssl.qhimg.com/t010dc3598b806cb106.png)**

****

翻译：[**running_wen**](http://bobao.360.cn/member/contribute?uid=345986531)

**预估稿费：120RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**AppleScript介绍**

AppleScript是从Mac OS 7(1991年)开始Mac OS就原生支持的脚步语言。Mac OS中很多系统软件，尤其是有UI界面的系统软件，都有AppleScript的身影，其他很多地方也有它的身影，自然而然，功能强大毫不含糊。

AppleScript在家庭类用户、专业类用户中很流行，它很好地衔接了OS本身的功能与第三方应用能提供的功能。为了AppleScript创建应用、系统服务更加快捷，Apple甚至从Mac OS 10.4就开始加入了支持拖拽开发的[**Automator**](https://en.wikipedia.org/wiki/List_of_macOS_components#Automator)（可快速创建工作流）软件。

<br>

**AppleScript的魅力**

AppleScript现在仍然还留着，主要就是用它创建UI驱动的脚本工作流和独立应用，很容易。对于那些支持AppleScript的应用，直接使用[**display dialog**](https://developer.apple.com/library/content/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/DisplayDialogsandAlerts.html)就可以获取用户输入，并呈现出来。

例如，我们可以为系统中的Mail应用创建一个脚本，得到特定的邮件发送者发送的邮件内容，AppleScript脚本负责弹出输入框获取用户希望查询的发送者的名字或者邮箱地址，效果如图1所示：

![](https://p4.ssl.qhimg.com/t014cd34b3ff3f96103.png)

图1 AppleScript特定发送者邮件内容查询

对应的AppleScript代码如下：

```
tell application "Mail" to activate 
tell application "Mail" to display dialog "Please enter the email address to search for..." 
default answer "" with icon 1 with title "Mail"
```

可以Mac OS中的** **[**Script Editor**](https://en.wikipedia.org/wiki/AppleScript_Editor)来执行上面的代码，Script Editor位于mac下的“/Applications/Utilities/Script Editor.app”，执行如图2所示：

![](https://p0.ssl.qhimg.com/t01d3d1e044f442013e.png)

图2 Script Editor运行脚本

除了Apple的核心服务外，还有很多第三方应用支持AppleScript脚本。例如，我们可以利用脚本实现搜索浏览器书签中的URL。如图3所示，弹出输入URL的对话框：

![](https://p3.ssl.qhimg.com/t01e2ff4a6e40d166f3.png)

图3 AppleScript接收书签查询内容

<br>

**AppleScript脚本利用**

从上面的例子可以看出，由于图标看着正常，容易让人认为这些对话框是正常应用的一部分，从而不怀疑其真实性，然而事实是它是由不相关的脚本产生的。这对于一部分人，开发脚本工作流比较便捷。这使得开发者能更多的关注应用的功能与逻辑实现，而不用过多的关注UI元素。然而，不难现象，这也很容易造成麻烦。

如图4所示，我们让LastPass弹出提示用户输入密码的对话框，其图片为LastPass的图标，上面的文字由我们控制。不论用户选择OK或者Cancel，接收的密码都没有发送给LastPass。相反，我们的脚本接收了用户输入的明文密码与用户名。攻击者可以进一步利用获取的账户获取LastPass中的信息。

![](https://p3.ssl.qhimg.com/t01e9b0bc8e8c78941b.png)

图4 AppleScript实现提示用户输入密码

另外一个场景是，利用同样的方式，欺骗用户输入Mac OS系统账户信息，在用户为管理员时进行提权，或者以受害者的身份运行应用，发送获取的信息到CC服务器。此外还可以诱骗用户输入Apple ID信息。

<br>

**更高水平的AppleScript钓鱼**

要想钓鱼成功实施，只要满足用户对正常应用的期望即可，这样就不会怀疑弹出提示框的真实性。最新的Touchbar MacBook Pro引入了Touch ID传感器，随之用户认证的流程也发生了变化。利用AppleScript在Touchbar MacBook Pro下的钓鱼攻击，其中一种操作序列如下：

1. 让System Preferences弹出告警对话框（System Preferences用户使用较多）；

2. 告警提示会话过期，需要重新认证。告警也可以仅仅在用户打开应用的时候弹出，这样用户会认为是打开应用导致弹出了提示；

3. 攻击者使用Touch ID的图标显示第二个对话框，让用户看着和正常的Touch ID提示没有区别，以欺骗用户输入账户信息；

4. 一旦用户输入了账户信息，攻击者保存相应信息，以供后面利用；

5. 受害者并不会看到任何其他的Touch ID行为，因为此时用户本来就不需要重新认证；

6. 钓鱼完成，账户信息被保存。



整个流程如图5所示：

![](https://p0.ssl.qhimg.com/t013778dba1cea54d9d.gif)

图5 Touchbar MacBook Pro下钓鱼

<br>

**结论**

在我们看来，攻击者很容易借助任何支持ApppleScript的应用来弹出提示用户输入敏感信息的输入框，如密码、双因素认证码等信息。

由于系统并没有提示，用户无法很好的区分弹出的对话框并不是应用本身弹出的提示。如果macos能在非授权AppleScript脚本与其他应用交互，弹出告警框之前需要用户进行授权，就是不错的安全实践。
