> 原文链接: https://www.anquanke.com//post/id/85000 


# 【技术分享】域渗透之使用CrackMapExec拿到我们想要的东西（二）


                                阅读量   
                                **126282**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：byt3bl33d3r
                                <br>原文地址：[https://byt3bl33d3r.github.io/getting-the-goods-with-crackmapexec-part-2.html](https://byt3bl33d3r.github.io/getting-the-goods-with-crackmapexec-part-2.html)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t018a40c04a1c44d8d7.jpg)](https://p1.ssl.qhimg.com/t018a40c04a1c44d8d7.jpg)**

****

**翻译：**[**hac425**](http://bobao.360.cn/member/contribute?uid=2553709124)

**稿费：80RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**传送门**

[**【技术分享】域渗透之使用CrackMapExec拿到我们想要的东西（一）**](http://bobao.360.cn/learning/detail/3216.html)



**前言**

在第一部分我们讲过的基础知识：

使用凭证

dump凭据

执行命令

使用payload模块

在第二部分我们将介绍CME的内部数据库以及如何使用 metasploit和 Empire来拿到shell.

<br>

**数据库**

CME的内部数据库可以通过使用cme_db.py脚本进行查询，两件事情会自动记录到数据库中：

CME所访问到的所有主机

拥有管理员权限的每台主机上的所有可获取的凭据

此外CME还会记录哪些凭据对哪些主机具有管理员权限。这项功能是非常有用的,因为在一个大型的网络环境中,我们可以拿到的凭据的数量是十分大的,如果完全人工分析,工作量会非常大.

使用hosts 命令我们可以查看所有我们交互过的主机

[![](https://p1.ssl.qhimg.com/t01717e426e77c006a8.png)](https://p1.ssl.qhimg.com/t01717e426e77c006a8.png)

这个的输出会返回所有我们交互过的主机以及每台机器上我们已经获得的管理员凭据数目.如果我们想查看某台特定主机的凭据信息可以把主机名或者ip地址传递给 hosts命令.

[![](https://p3.ssl.qhimg.com/t014788b9b340018641.png)](https://p3.ssl.qhimg.com/t014788b9b340018641.png)

同时我们还可以查询每个已获得的凭据对哪些机器具有管理员权限.我们可以使用: creds命令来概览下:

[![](https://p0.ssl.qhimg.com/t01cae5e1c89db6081a.png)](https://p0.ssl.qhimg.com/t01cae5e1c89db6081a.png)

输出返回凭据的ID，类型，用户名，密码以及该凭据具有管理员权限的机器的数量。要了解详细情况我们可以直接把 用户名 作为参数传递给 creds命令.

[![](https://p2.ssl.qhimg.com/t01629e652180ecf68c.png)](https://p2.ssl.qhimg.com/t01629e652180ecf68c.png)

<br>

**拿到所有的shell**

在第一部分中我们已经拿到了域管理员权限,我们就能拿到所有东西的shell啦!首先介绍如和拿到meterpreter session.

先来看看meterpreter_inject模块的说明.

[![](https://p2.ssl.qhimg.com/t01663c7a0d49426fc4.png)](https://p2.ssl.qhimg.com/t01663c7a0d49426fc4.png)

现在我们在每台机器上运行meterpreter_inject模块,然后设置LHOST和LPORT参数( 设为我们在 handler中设置的一样)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01740069e91a9509be.gif)

然后shell就到我们的metasploit中了…..

[![](https://p4.ssl.qhimg.com/t01442ae18846bd7653.png)](https://p4.ssl.qhimg.com/t01442ae18846bd7653.png)

接下来介绍如何使用Empire获取所有的shell,首先看看模块的说明

[![](https://p4.ssl.qhimg.com/t01d7cacbd55a5d29d0.png)](https://p4.ssl.qhimg.com/t01d7cacbd55a5d29d0.png)

empire_agent_exec模块需要Empire监听器的名称,然后使用Empire's RESTful API 来生成一个合法的加载器.首先启动Empire RESTful API

[![](https://p0.ssl.qhimg.com/t011ebfab7b6deaf657.png)](https://p0.ssl.qhimg.com/t011ebfab7b6deaf657.png)

(你需要在cme.conf文件中配置 Empire RESTful API的host ,用户名,密码来对Empire RESTful API进行认证)

然后创建一个名为CMETest的监听器

[![](https://p2.ssl.qhimg.com/t01b053efc6f81e5101.png)](https://p2.ssl.qhimg.com/t01b053efc6f81e5101.png)

准备工作已经搞定,下面来接shell吧……

[![](https://p0.ssl.qhimg.com/t017f9d718ccee856ab.gif)](https://p0.ssl.qhimg.com/t017f9d718ccee856ab.gif)

这里我使用了一个 -id 的参数指定了管理员的凭据,因为前面CME会把所有的凭据都存到数据库中,所以当我们指定 CredID 时他们会从后端数据库自动到指定的凭据来验证指定的机器！接着使用了LISTENER参数指定了Empire监听器的名称,然后CME会自动的去连接Empire RESTful API,生成加载器并且执行他,整个过程都是自动化的.下面来看看我们的shell

[![](https://p3.ssl.qhimg.com/t01728c5a980352c607.png)](https://p3.ssl.qhimg.com/t01728c5a980352c607.png)

<br>

**总结**

在这里介绍了如何在大型网络环境中使用CWE,通过使用这款工具可以节省我们很多时间。



**<br>**

**传送门**

[**【技术分享】域渗透之使用CrackMapExec拿到我们想要的东西（一）**](http://bobao.360.cn/learning/detail/3216.html)


