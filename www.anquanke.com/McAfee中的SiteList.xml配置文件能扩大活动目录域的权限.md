> 原文链接: https://www.anquanke.com//post/id/83427 


# McAfee中的SiteList.xml配置文件能扩大活动目录域的权限


                                阅读量   
                                **84617**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://github.com/tfairane/HackStory/blob/master/McAfeePrivesc.md](https://github.com/tfairane/HackStory/blob/master/McAfeePrivesc.md)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p1.ssl.qhimg.com/t01beccd16b0ae3e1ff.jpg)](https://p1.ssl.qhimg.com/t01beccd16b0ae3e1ff.jpg)



在做测试员的实习工作期间，我找到了一个很棒的方法，可以在Active Directory 域（活动目录域）中实现privesc脚本。我借用了一名员工的笔记本电脑和他的低权限的McAfee帐号，准备来实现这一功能。在这台笔记本上装有McAfee Virusscan Enterprise 8.8版本软件。

McAfee能给用户提供一个这样的功能：用户可通过McAfee来自定义进行服务器的更新，同时用户可通过HTTP或SMB连接到这些服务器。（路径是：C:ProgramDataMcAfeeCommon Framework）Sitelist.xml配置文件中包含着大量的信息，比如：信息凭证，内部服务器的名字等等。

[![](https://p2.ssl.qhimg.com/t012e15a34960a1746a.png)](https://p2.ssl.qhimg.com/t012e15a34960a1746a.png)

接下来，我们可以在所使用的McAfee杀毒服务中，查看相关的用户权限。

[![](https://p4.ssl.qhimg.com/t0194618ad3668704fc.png)](https://p4.ssl.qhimg.com/t0194618ad3668704fc.png)

不幸的是，由于该笔记本上的AV（McAfee Virusscan Enterprise ：McAfee公司推出的一款杀毒软件，具有防病毒+ 防火墙的功能，能阻止恶意软件入侵PC。）占用了GUI（Graphical User Interface，图形用户界面，简称GUI）的密码，使得我无法对该文件进行编辑。为了解决这一问题，我重新下载了McAfee软件，并把它装在了自己的Windows虚拟机中，同时将之前SiteList.xml中的sesame系统框架文件拷贝了过来。

在完成上述操作之后，离成功就不远了。我编辑的那个文件，能让我实现这样一个功能：我可以将用户的一个HTTP请求进行重定向，强制将其连接到我原先设置好的，任意一个服务器上，从而我就能冒名地对这些请求进行回应。SiteList.xml文件如下图所示：

[![](https://p2.ssl.qhimg.com/t010c7cf4f209f156b9.png)](https://p2.ssl.qhimg.com/t010c7cf4f209f156b9.png)

之后，我点击进入了McAfee AV ，将它和相应的响应器进行了更新，从而可以查看相关的矩阵信息。

OMG，我做到了。现在，我已经将活动目录域的权限扩大了。可以通过登录域名控制台，访问该主机域内的所有工作站。

这样，任务就完成了！
