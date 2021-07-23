> 原文链接: https://www.anquanke.com//post/id/84250 


# 使用Flash, PDF 和 Silverlight进行内容劫持的POC项目


                                阅读量   
                                **87529**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://github.com/nccgroup/CrossSiteContentHijacking](https://github.com/nccgroup/CrossSiteContentHijacking)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01684c3ab20ce9ec8d.jpg)](https://p5.ssl.qhimg.com/t01684c3ab20ce9ec8d.jpg)

[![](https://p4.ssl.qhimg.com/t01fa9ef6bfc12d9970.png)](https://p4.ssl.qhimg.com/t01fa9ef6bfc12d9970.png)

 

**证书**

 

证书发布在AGPL(想要了解更多信息,可以阅读许可证书)。

 

**简介**********

 

这个项目可以为以下概念提供一个证明:

 

利用网站的不安全的策略文件(crossdomain.xml或clientaccesspolicy.xml)，通过阅读其内容找到漏洞进行利用。

 

利用不安全的文件上传功能——不对文件内容进行检查，或允许上传SWF或PDF文件而在下载过程中没有Content-Disposition头信息。在这个场景中,创建的SWF,XAP或PDF文件在上传时可能会带有任何扩展，例如上传.JPG文件到目标网站。然后, “Object File”的值应该设置为上传文件的URL，从而来阅读目标网站的内容。

 

利用CVE-2011-2461漏洞（详细信息参见参考文献）。

 

利用网站中不安全的HTML5跨源资源共享(CORS)头文件。

 

注意:.XAP文件可以重命名为其他扩展，但是它们已经不能跨域加载了。所以Silverlight寻找文件扩展是基于提供的URL而忽略了它是不是.XAP。这就给我们带来了利用的方法,如果一个网站允许用户在实际的文件名称后使用“;”或“/”来添加一个“.XAP”扩展，我们就可以利用它来进行攻击。

 

**用法**

 

利用一个不安全的策略文件:1)控制web 服务器的内容劫持目录；2)在浏览器里浏览index.html页面(该页面会重定向到ContentHijackingLoader.html)；3)更改html页面中的“Object File”字段为“Object”目录(“xfa-manual-ContentHijacking.pdf”已经不能使用)中的合适对象。

 

利用一个不安全的文件上传/下载功能:1)上传一个“Object”目录中的对象文件到受害者的服务器上。当上传到另一个域时这些文件还可以重命名为另一个扩展名 (由于通常情况下来自另外一个域中的修改扩展名的Silverlight XAP文件不可用，所以首先使用Flash，然后使用PDF)；2)将“Object File”字段设置为上传文件的位置。

 

利用CVE- 2011 – 24611漏洞：1) 将“Object File”字段设置为易攻击的文件；2) 从下拉列表的“Type”字段中选择“Flash CVE- 2011 – 2461 Only”。

 

利用一个不安全的CORS策略:1)将 “Object File”字段设置为本地的“ContentHijacking.html文件。如果可以在你的目标域中上传一个HTML文件,那么你可以利用XSS问题，这比使用CORS更容易。

 

注意:.XAP文件可以重命名为其他扩展，但是它们已经不能跨域加载了。所以Silverlight寻找文件扩展是基于提供的URL而忽略了它是不是.XAP。这就给我们带来了利用的方法,如果一个网站允许用户在实际的文件名称后使用“;”或“/”来添加一个“.XAP”扩展，我们就可以利用它来进行攻击。

 

注意:当Silverlight跨域请求一个.XAP文件时,内容类型必须为:应用程序/ x-silverlight-app。

 

注意:PDF文件只能用于Adobe Reader查看器(不适用于Chrome和Firefox的内置PDF查看器)。

 

注意:阅读静态内容或公开访问的数据并不是一个问题。从你的报告中去除假阳性结果是很重要的。另外,在“Access-Control-Allow-Origin”头文件中单独使用一个通配符——“*”字符也不是一个问题。

 

使用示例：

 

在带有Adobe Reader的IE中：

https://15.rs/ContentHijacking/ContentHijackingLoader.html?

objfile=https://15.rs/ContentHijacking/objects/ContentHijacking.pdf&amp;objtype=pdf&amp;target=https://0me.me/&amp;postdata=param1=foobar&amp;logmode=all&amp;regex=owasp.*&amp;isauto=1

 

在任何支持SWF的浏览器中：

http://15.rs/ContentHijacking/ContentHijackingLoader.html?

objfile=http://0me.me/ContentHijacking/objects/ContentHijacking.swf&amp;objtype=flash&amp;target=http://0me.me/&amp;postdata=&amp;logmode=result&amp;regex=&amp;isauto=1

 

**解决安全问题的一般建议**

 

允许上传的文件类型应该只局限于那些对于业务功能是必要的类型。

 

应用程序应该对上传到服务器的任何文件执行过滤和内容检查。并且，在将文件提供给其他用户之前应该进行彻底的扫描和验证。如果发现有疑问,应该丢弃。

 

对静态文件的响应添加“Content-Disposition: Attachment”和“X-Content-Type-Options:nosniff”头信息，这可以保护网站应对基于Flash或pdf的跨站点内容劫持攻击。建议将这种做法实施到所有文件上,从而应对所有模块中的文件下载风险。尽管这种方法并不能使网站完全避免使用Silverlight或类似对象的攻击,但是它可以减轻使用Adobe Flash和PDF对象的风险,特别是允许上传PDF文件时。

 

如果Flash / PDF(crossdomain.xml)或Silverlight(clientaccesspolicy.xml)的跨域策略文件没有使用，或者没有使用Flash和Silverlight应用程序与网站进行交流的业务需求，那么应该将这些跨域策略文件删除。

 

应该限制跨域访问在一个最小的集合中，这个集合只包含那些受信任的域和有访问需求的域。当使用通配符时访问策略被认为是脆弱的或不安全的，特别是在“uri”属性值中存在通配符。

 

任何用于Silverlight应用程序的“crossdomain.xml”文件都是脆弱的,因为它只能在域属性中接受一个通配符(“*”字符)。

 

应该禁止Corssdomain.xml和clientaccesspolicy.xml文件访问浏览器缓存。这使得网站能够容易更新文件或在必要时限制对Web服务的访问。一旦客户端访问策略文件时受到了检查, 对浏览器会话而言它仍然有效的，不能访问缓存对终端用户的影响是最小的。基于目标网站的内容和策略文件的安全性和复杂性，这可以作为一个低的信息风险问题提出。

 

应该将CORS头文件修复为仅支持静态或公开访问数据。另外,“Access-Control-Allow-Origin”头文件应该只包含授权地址。其它CORS头文件,例如“Access-Control-Allow-Credentials”应该只在需要时使用。CORS头文件中的条目，比如“Access-Control-Allow-Methods”或“Access-Control-Allow-Headers” 在它们不需要时应该修复或者删除。

 

注意:使用“Referer”头文件并不能称为一种解决方案,因为可以设置这个头文件发送一个POST请求，从而使用Adobe Reader和PDF(详见“objects”目录中的“xfa-manual-ContentHijacking.pdf”文件)。（更新: Adobe已经解决了设置“Referer”头文件问题,除非你可以找到其他方法）。

 

**项目主页**

 

可以在下面的链接看到项目的最新更新/帮助：

https://github.com/nccgroup/CrossSiteContentHijacking

 

**作者**

 

Soroush Dalili(@irsdl) （来自NCC组织）

 

**参考文献**

 

上传一个JPG文件可能导致跨域数据劫持(客户端攻击)!

https://soroush.secproject.com/blog/2014/05/even-uploading-a-jpg-file-can-lead-to-cross-domain-data-hijacking-client-side-attack/

 

多个PDF漏洞——Steroids上的文本和图片

http://insert-script.blogspot.co.at/2014/12/multiple-pdf-vulnerabilites-text-and.html

 

HTTP通信和Silverlight安全

http://msdn.microsoft.com/en-gb/library/cc838250(v=vs.95).aspx

 

跨域和Silverlight客户端访问策略文件的解释

http://www.devtoolshed.com/explanation-cross-domain-and-client-access-policy-files-silverlight

 

跨域策略文件规范

http://www.adobe.com/devnet/articles/crossdomain_policy_file_spec.html

 

为HTTP流媒体设置一个crossdomain.xml文件

http://www.adobe.com/devnet/adobe-media-server/articles/cross-domain-xml-for-streaming.html

 

在google.com上利用CVE- 2011 – 2461

http://blog.mindedsecurity.com/2015/03/exploiting-cve-2011-2461-on-googlecom.html

 

 




