> 原文链接: https://www.anquanke.com//post/id/84882 


# 【技术分享】Burp Suite插件开发之SQL注入检测（已开源）


                                阅读量   
                                **236021**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01b83322a258d25900.png)](https://p3.ssl.qhimg.com/t01b83322a258d25900.png)

****

**作者：**[**bsmali4******](http://bobao.360.cn/member/contribute?uid=561536297)

**稿费：400RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆<strong><strong><strong><strong>[<strong>网页版**](http://bobao.360.cn/contribute/index)</strong></strong></strong></strong></strong>**在线投稿**

**<br>**

**前言**

前段时间和某师傅了解到。现在漏洞越来越难挖，但有些老司机总能挖到别人挖不到的漏洞。于是就问了下，大概是什么类型的漏洞，他说是盲注。好吧，的确是，尤其是延时注入,这类东西真的不好测试。好多次我在sqlmap下面都没有测出来。挖洞来说还是burp用的比较居多吧，看过很多被动式扫描平台，本来也想做一个，但是觉得竟然有burp这等web神器，太喜欢他的抓包重放功能了，简直不能太赞，想想搞什么被动式扫描，我直接做成一个burp插件集成起来就ok了，于是有了本篇文章。

<br>

**详情**

本文以mysql抛砖引玉，其他类型的数据库也是类似的道理。我在设计的时候，不考虑用sqlmapapi，不是说他不好，sqlmap的强大性，我们有目共睹，这点不用怀疑。我在尝试寻找一种通用的检测注入的方法，发现注入的几种类型，包括报错注入,盲注之类的。最后想了一种比较通用的检测注入的方法，延时注入。

mysql中延时注入的话有几个函数。sleep,benchmark之类。只是简单的演示下sleep

[![](https://p4.ssl.qhimg.com/t012c3838710d29cad8.png)](https://p4.ssl.qhimg.com/t012c3838710d29cad8.png)

[![](https://p4.ssl.qhimg.com/t0104795a801b984e62.png)](https://p4.ssl.qhimg.com/t0104795a801b984e62.png)

可以看到，延时20秒才会出效果。其实大部分的盲注和显错注入都可以用这个来检测。既然要打造一款burp插件，那么肯定要了解burp api。

官方文档   [https://portswigger.net/burp/extender/api/index.html](https://portswigger.net/burp/extender/api/index.html)

burpapi还是比较简单易懂的，我们的想法很简单，就是通过调用burp  api来解析流量，然后构造好payload，最后来发包，通过比较时间差来判断这到底是不是一个注入。当然了，延时注入之类的检测，和网络稳定性的关系还是蛮大的。在这里我们不考虑网络的原因，还是旨在抛砖引玉，带大家体验一下burp插件的开发过程。

下载好burp api文件之后，有几个java文件，我们在同一目新建一个BurpExtender.java，让其实现IBurpExtender, IScannerCheck。

实现IScannerCheck类之后，实现 doPassiveScan函数。我们的检测操作就放在这个函数里面。

画了一个简单的思维导图

[![](https://p5.ssl.qhimg.com/t013990181fcd676899.png)](https://p5.ssl.qhimg.com/t013990181fcd676899.png)

FuzzVul.java里面有两个函数，checkGet和checkPost函数，我按照http协议类型分的，这里面又分为几种，按不同的编码方式，我们不仅仅满足于检测sql注入，像xss啊，乃至于imagemagick,其实都是可以检测的。所以在不同的编码下面多设置几个检测函数，像xml类型，我们可以用来检测xxe，上传文件类型，我们还可以用来检测上传绕过啊，imagemagick这些，反正可以做的地方很多，扯远了。



```
BurpExtender.java
package burp;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.http.entity.ContentType;
import bsmali4.FuzzVul;
public class BurpExtender implements IBurpExtender, IScannerCheck `{`
public IBurpExtenderCallbacks callbacks;
public IExtensionHelpers helpers;
public PrintWriter stdout;
public void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks) `{`
this.callbacks = callbacks;
stdout = new PrintWriter(callbacks.getStdout(), true);
this.helpers = callbacks.getHelpers();
callbacks.setExtensionName("Time-based sqlinject checks");
callbacks.registerScannerCheck(this);
System.out.println("Loaded Time-based sqlinject checks");
`}`
@Override
public int consolidateDuplicateIssues(IScanIssue existingIssue,
IScanIssue newIssue) `{`
// TODO Auto-generated method stub
return 0;
`}`
// 主动式扫描
@Override
public List&lt;IScanIssue&gt; doActiveScan(
IHttpRequestResponse baseRequestResponse,
IScannerInsertionPoint insertionPoint) `{`
// TODO Auto-generated method stub
return null;
`}`
// 被动式扫描
@Override
public List&lt;IScanIssue&gt; doPassiveScan(
IHttpRequestResponse baseRequestResponse) `{`
String method = this.helpers.analyzeRequest(baseRequestResponse)
.getMethod();
String url = this.helpers.analyzeRequest(baseRequestResponse).getUrl()
.toString();
if (!url.contains("google.com")) `{`
if (method != null &amp;&amp; method.trim().equals("POST")) `{`
FuzzVul.checkPost(baseRequestResponse, helpers, stdout);//post检测函数
`}` else if (method.trim().equals("GET")) `{`
FuzzVul.checkGet(baseRequestResponse, helpers, stdout);//get检测函数
`}`
`}`
return null;
`}`
`}`
BurpExtender.java我们前面讲过，重点是doPassiveScan函数。调用了FuzzVul工具类，
FuzzVul.java
public static void checkPost(IHttpRequestResponse baseRequestResponse,
IExtensionHelpers helpers, PrintWriter stdout) `{`
List&lt;String&gt; headerStrings = new ArrayList&lt;String&gt;();
List&lt;IParameter&gt; parameters = new ArrayList&lt;IParameter&gt;();
URL url = helpers.analyzeRequest(baseRequestResponse).getUrl();
byte contenttype = helpers.analyzeRequest(baseRequestResponse)
.getContentType();
headerStrings = helpers.analyzeRequest(baseRequestResponse)
.getHeaders();
parameters = helpers.analyzeRequest(baseRequestResponse)
.getParameters();
…..
switch (contenttype) `{`
case IRequestInfo.CONTENT_TYPE_URL_ENCODED:
checkURLENCODEDPost(baseRequestResponse, helpers, stdout);
break;
……
/* URL_ENCODED类型 */
private static void checkURLENCODEDPost(
IHttpRequestResponse baseRequestResponse,
IExtensionHelpers helpers, PrintWriter stdout) `{`
SQLINJECT.checkPostSqlinject(baseRequestResponse, helpers, stdout);`}`
```

最终的检测函数还是放在SQLINJECT.checkPostSqlinject中。在构造payload之前，我们需要初始化payload，加载常见的payload的，这里我们遇到一个需求，按照之前的设置，当我们开启burp监听的时候，所有的流量都会自动经过一次doPassiveScan函数，我们针对每一次http请求，不可能每个请求都初始化一次payload，我的想法是放在一个全局变量中，但是问题会来的，多次调用，某些原因导致全局变量的数据收到影响，显然这种方式不好。我想到了一种设计模式，单例模式。于是我先定义一个变量



```
static List&lt;String&gt; payloads;
// 初始化payloads
public static List&lt;String&gt; initpayload(boolean refresh) `{`
if (refresh) `{`
payloads = null;
`}`
if (payloads != null)
return payloads;
else `{`
payloads = new ArrayList&lt;String&gt;();
// payloads.add("' xor sleep()#");
int timeout = 5;
payloads.add("' and sleep(" + timeout + “)#");
…
return payloads;
`}`
`}`
```

熟悉的单例模式，这样做的话有很多好处，如果你想刷新payloads的数据，直接传initpayload(True)就行了，如果不刷新，只需要加载一次就好了，这么写的好处不言而喻。

后面就是解析流量之类的，



```
List&lt;String&gt; headerStrings = new ArrayList&lt;String&gt;();
List&lt;IParameter&gt; parameters = new ArrayList&lt;IParameter&gt;();
List&lt;HttpParameter&gt; Httpparameter = new ArrayList&lt;HttpParameter&gt;();// 参数list
URL url = helpers.analyzeRequest(baseRequestResponse).getUrl();
headerStrings = helpers.analyzeRequest(baseRequestResponse)
.getHeaders();//获取http头信息，包含ua,cookie之类的
parameters = helpers.analyzeRequest(baseRequestResponse)
.getParameters();//获取提交参数，其中也会自动包括cookie
```

解析好流量之后，就是发送http数据包了，由于十分喜欢python的requests模块，所以我将java的httpclient简单的封装了一下，使用起来比较舒服。



```
Thread t1 = new Thread() `{`
public void run() `{`
httpPost.doPost();
`}`;
`}`;
t1.start();
try `{`
t1.join();
`}` catch (InterruptedException e) `{`
e.printStackTrace();
`}`
//stdout.println(httpPost.getResContent());
long endTime = System.currentTimeMillis();
if ((endTime - startTime) &gt; TIMEOUT) `{`
   stdout.println("===========================================");stdout.println("=========this**found**a**sqlinject=========");
`}`
```

大致思路就是这样，最后代码已经上传到github上面。可以提供给大家下载学习，当然也欢迎大家一起来完善这些模块，包括我前面说的xss之类的，其实都是可以做的。

<br>

**效果测试**

由于最近一直在看ctf，（我是菜鸟），所以找了几个ctf环境测试，效果棒棒哒。

[![](https://p3.ssl.qhimg.com/t019b256254876c0585.png)](https://p3.ssl.qhimg.com/t019b256254876c0585.png)

post注入

[![](https://p2.ssl.qhimg.com/t01d259a6eacd6e14ee.png)](https://p2.ssl.qhimg.com/t01d259a6eacd6e14ee.png)

[![](https://p0.ssl.qhimg.com/t013b48a81d3bd8e51c.png)](https://p0.ssl.qhimg.com/t013b48a81d3bd8e51c.png)

[![](https://p3.ssl.qhimg.com/t0193478de7d4e2ff97.png)](https://p3.ssl.qhimg.com/t0193478de7d4e2ff97.png)

然后，用这个插件检测了某位师傅挖的某个src的盲注，也检测出来了， 效果还是比较满意的。不过还有很多功能需要继续去完善,比如xss这些。

插件安装，如果想自己编译安装的话，直接编译下面源代码，或者直接在extender下添加jar插件

[![](https://p2.ssl.qhimg.com/t017a828c3806de771a.png)](https://p2.ssl.qhimg.com/t017a828c3806de771a.png)

<br>

**项目地址: **[**https://github.com/bsmali4/checkSql******](https://github.com/bsmali4/checkSql)


