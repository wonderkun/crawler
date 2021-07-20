> 原文链接: https://www.anquanke.com//post/id/87022 


# 【技术分享】SQL注入：如何通过Python CGIHTTPServer绕过CSRF tokens


                                阅读量   
                                **166357**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：cobalt.io
                                <br>原文地址：[https://blog.cobalt.io/bypassing-csrf-tokens-with-pythons-cgihttpserver-to-exploit-sql-injections-18f95e6152ff](https://blog.cobalt.io/bypassing-csrf-tokens-with-pythons-cgihttpserver-to-exploit-sql-injections-18f95e6152ff)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01330d9edd1cf0a7c3.png)](https://p2.ssl.qhimg.com/t01330d9edd1cf0a7c3.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：110RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

在[Burp](https://portswigger.net/burp)上，我们可以使用多种方法来配置**宏（macro）**，以绕过HTML表单上的**CSRF tokens**，这样一来，我们就可以使用Burp Active Scans、Burp Intruder、Burp Repeater，甚至也可以使用Burp Proxy进行渗透测试。我们也可以找到专为Intruder模块设计的Grep-Extract以及pitchfork攻击类型。当然，如果我们愿意的话，也可以开发自己的Burp Extension。[Sqlmap](https://github.com/sqlmapproject/sqlmap)上也有**-csrf-token**以及**-csrf-url**参数来应付类似场景，如果不使用这些命令，我们可以按照之前描述的方法来配置Burp，然后在sqlmap中通过-proxy参数与Burp配合使用。

在本文中，我们会介绍另一种办法，那就是使用python中的[**CGIHTTPServer**](https://pentesterslife.wordpress.com/2017/09/11/python-for-pentesters-the-practical-version/)来完成这一任务。



**二、实验环境**

我们构造了一个非常简单的PHP/mysql环境，登录后，你可以访问某个受限区域。你可以访问[此链接](https://gitlab.com/0x4ndr3/blog_post_csrf_bypass_with_cgihttpserver.git)获取实验所用的PHP代码，以便在其他场景做些修改或调整。不要在意代码细节，毕竟我并不是PHP专家，只是热衷于搭建满足需求的测试环境而已。实验环境有助于我们理解测试过程，在现实场景中寻找真正目标。

实验所用的CSRF tokens为一串随机生成的SHA256散列字符串，每个HTTP请求都对应一个不同的tokens。

[![](https://p4.ssl.qhimg.com/t01c6b3fdf969e80b0e.png)](https://p4.ssl.qhimg.com/t01c6b3fdf969e80b0e.png)



**三、面临的问题**

不经过特殊配置时，Burp不会检测到这个问题。

[![](https://p1.ssl.qhimg.com/t0182f74e653c1efdd7.png)](https://p1.ssl.qhimg.com/t0182f74e653c1efdd7.png)

同理，没有使用-csrf-token参数时，sqlmap也无能为力：

[![](https://p2.ssl.qhimg.com/t01ccc88fcb61eead88.png)](https://p2.ssl.qhimg.com/t01ccc88fcb61eead88.png)

我使用了–technique、–dbms以及-p参数来加快扫描速度。由于这是一个简单的基于布尔值的SQL注入（boolean-based SQLi），我们只需要使用默认的-level 1参数即可。但我们需要将-risk设置为3，因为只有使用较高的风险数值，我们才能测试OR类型的SQL注入（OR boolean-based SQLi）场景。OR类型的SQL注入非常危险，因为这种语句可以使任何条件的结果为真。比如，在使用WHERE子句的UPDATE或DELETE语句中，使用这种注入方式，你很有可能会不小心更新数据库中所有用户的密码，或者导出用户的凭据表，而这正是你在渗透测试中应该尽力避免的结果。

在sqlmap中，我们可以使用–csrf-token=”mytoken”参数检测到OR类型的SQL注入：

[![](https://p2.ssl.qhimg.com/t0109f10cc438e25012.png)](https://p2.ssl.qhimg.com/t0109f10cc438e25012.png)

由于这是一个登录验证表单，很明显会对应一条SELECT语句，这意味着使用最高的风险等级3不会带来任何风险。

当然，如果你有有效的凭据（实际渗透测试中你很难具备这个条件），此时该场景也会受AND类型的SQL注入（AND boolean-based SQLi）影响。然而，即使我拥有有效的凭据，我首先还是会使用另一个（有效的）用户名来寻找可用的OR类型SQLi，以免不小心锁定账户（如果存在账户锁定机制的话）。

在sqlmap中，我们可以使用**–csrf-token=”mytoken”**来检测AND类型的SQL注入：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01627b4d2dd3056994.png)



**四、使用CGIHTTPServer**

创建如下CGI脚本：

[![](https://p3.ssl.qhimg.com/t01cf0b9cfe76e10ad3.png)](https://p3.ssl.qhimg.com/t01cf0b9cfe76e10ad3.png)

我们将该脚本命名为mask.py，存放在xxx/cgi-bin/目录中，同时请确保.py文件为可执行文件。创建该文件后，我们需要在xxx目录中运行python -m CGIHTTPServer命令。默认情况下，服务器会在8000/tcp端口上监听。

[![](https://p4.ssl.qhimg.com/t01457b86e98d4422fa.png)](https://p4.ssl.qhimg.com/t01457b86e98d4422fa.png)

首先，使用正确的密码测试这个服务器：

[![](https://p3.ssl.qhimg.com/t0176bf4739483b07b1.png)](https://p3.ssl.qhimg.com/t0176bf4739483b07b1.png)

然后，测试一下错误的密码：

[![](https://p3.ssl.qhimg.com/t017f3abc3e2d7dd613.png)](https://p3.ssl.qhimg.com/t017f3abc3e2d7dd613.png)

现在，无需特殊配置，我们就可以使用Burp以及sqlmap来检测SQL注入漏洞。

[![](https://p4.ssl.qhimg.com/t0145f0c6fa917d7f20.png)](https://p4.ssl.qhimg.com/t0145f0c6fa917d7f20.png)

这就好像我们添加了一个中间层，可以简化CSRF tokens给我们测试过程所带来的复杂度，现在我们无需刻意去提交这个token信息了。



**五、参考文献**

[1] [Sqlmap](https://github.com/sqlmapproject/sqlmap/blob/master/doc/README.pdf)

[2] [另外我们还可以使用Mechanizer来完成类似功能，以便扫描器能够检测到响应数据中存在的差异。](http://mechanize.readthedocs.io/en/latest/browser_api.html#the-response)

[3] [Burp宏](https://portswigger.net/burp/help/options_sessions_macroeditor.html)

[4] 对渗透测试人员较为实用的[Python代码](https://pentesterslife.wordpress.com/2017/09/11/python-for-pentesters-the-practical-version/)
