> 原文链接: https://www.anquanke.com//post/id/86408 


# 【技术分享】方法虽老但依然有效：如何使用ZIP bomb来保护网站


                                阅读量   
                                **186699**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.haschek.at
                                <br>原文地址：[https://blog.haschek.at/2017/how-to-defend-your-website-with-zip-bombs.html](https://blog.haschek.at/2017/how-to-defend-your-website-with-zip-bombs.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p5.ssl.qhimg.com/t01ab9b077d15010c57.jpg)](https://p5.ssl.qhimg.com/t01ab9b077d15010c57.jpg)

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



我不知道你是否自己运营过一个网站或当过某个服务器的管理员，但如果你做过的话，你就会非常清楚地知道外面有多少坏人随时都在想着如何攻击你的网站或服务器。

想当初我还是十三岁的时候我就自己架设了我第一台服务器，那是一台小型服务器，运行的是Linux系统，并且还配置了SSH远程访问控制。当时每天都会有大量来自天朝和俄罗斯的IP地址会尝试连接或访问我这台可爱的服务器，因此我每天都得去检查服务器的运行日志，并将那些貌似想干坏事的IP地址报告给他们的互联网服务提供商（IPS）。值得一提的是，我当时假设服务器所用的设备就是一台老款的ThinkPad T21，而且显示屏都已经坏得差不多了，配置完成之后它就一直乖乖地躺在我床底下运行着。

实际上，如果你自己运行过一台配置了SSH远程访问的Linux服务器的话，你就知道每天会有多少条链接来尝试访问你的服务器了：

```
grep 'authentication failures' /var/log/auth.log
```

你从下图中看到，即使我禁用了服务器的密码身份验证，即使服务器运行在非标准端口上，每天仍然都会有成百上千次失败的登录尝试：

[![](https://p1.ssl.qhimg.com/t019692a5ae8f9314dd.png)](https://p1.ssl.qhimg.com/t019692a5ae8f9314dd.png)

<br>

**WordPress已经把我们都给毁了**

其实大家都知道，Web漏洞扫描工具明显出现的要比WordPress早，但由于WordPress的受欢迎程度如此之高，目前绝大多数的Web漏洞扫描工具都已经拥有扫描wp-admin目录错误配置或未修复插件等安全问题的功能了。

所以说，如果一个小型黑客组织想要通过入侵某网站来让大家都知道他们的话，他们首先肯定会下载一些这样的[漏洞扫描工具](http://rgaucher.info/beta/grabber/)，然后利用这些[工具](https://wpscan.org/)来对大量网站进行漏洞扫描测试，如果运气好的话他们很快就可以拿到目标网站后台服务器的访问权了。接下来要发生的事情，[你懂的](https://en.wikipedia.org/wiki/Website_defacement)…

下图显示的是通过[工具Nikto](https://github.com/sullo/nikto)扫描之后所生成的日志文件样本：

[![](https://p4.ssl.qhimg.com/t01be6c8e0a9d26ae92.png)](https://p4.ssl.qhimg.com/t01be6c8e0a9d26ae92.png)

为什么所有的网站管理员或服务器运维人员每天都需要处理大量包含扫描尝试的日志呢？看到这里想必你也应该清楚了。但让我们冷静下来好好想想，我们有没有什么办法可以对这种恶意尝试行为予以反击呢？

<br>

**有没有办法可以反击？**

在对IDS（入侵检测系统）和Fail2ban的实现过程进行了重新回顾之后，我突然想起来了很久以前非常流行的Zip bombs（Zip炸弹）。

<br>

**Zip炸弹是什么东西？**

Zip炸弹也被称作是死亡压缩包或解压缩炸弹，这是一种恶意文档（archive）文件，当某个程序或系统尝试读取这个文件时，它便会让目标发生崩溃。一般来说，攻击者会利用这种Zip炸弹来让反病毒软件崩溃，然后为传统病毒的感染扫清障碍。

实际上，Zip炸弹并不会劫持程序的正常运行过程，Zip炸弹允许目标程序按照其原有的运行机制运行下去，但这个压缩文件是攻击者精心制作的，而反病毒软件如果想要扫描这个压缩文件的话，就需要对其进行解压缩，但解压缩文件将需要花费大量的时间、磁盘空间和内存，因此变造成了程序崩溃或假死。

这样看来，我们就可以利用Zip炸弹来对付那些不断重复的请求数据了。如果你有一个数据全部是0的大型文本文件的话，那么它的压缩效果将是非常非常好的，但解压起来可就不一样了。你可以参考这个文件（42.zip）,它可以将一个大小为4500000GB的文件压缩成42字节。当你尝试查看文档内容时（即提取或解压缩），它便会耗光你的磁盘空间和内存。

<br>

**如何利用ZIp炸弹对付漏洞扫描工具？**

不幸的是，Web浏览器并不知道ZIP压缩文件是什么，但它们知道GZIP。

所以我们首先要使用数据“0”来创建一个大小为10GB的GZIP文件，你也可以进行多次压缩，不过这里为了方便演示就不进行这种操作了。

```
dd if=/dev/zero bs=1M count=10240 | gzip &gt; 10G.gzip
```

接下来，创建我们的Zip炸弹并检查其文件大小：

[![](https://p3.ssl.qhimg.com/t01d8db29c9ff879f34.png)](https://p3.ssl.qhimg.com/t01d8db29c9ff879f34.png)

如上图所示，我们生成的Zip炸弹大小为10MB，其实我们还可以把它压缩得更小，但这个压缩效率已经足够我们进行演示了。

既然现在我们已经创建好了我们的Zip炸弹，接下来我们还得设置一个PHP脚本来将这个Zip炸弹发送给客户端。



```
&lt;?php 
//prepare the client to recieve GZIP data. This will not be suspicious 
//since most web servers use GZIP by default 
header("Content-Encoding: gzip"); 
header("Content-Length: ".filesize('10G.gzip')); 
//Turn off output buffering 
if (ob_get_level()) ob_end_clean();
//send the gzipped file to the client 
readfile('10G.gzip');
```

一切搞定！接下来，我们就可以使用下面给出的方法来进行简单的防御了：



```
&lt;?php
$agent = lower($_SERVER['HTTP_USER_AGENT']);
//check for nikto, sql map or "bad" subfolders which only exist on wordpress
if (strpos($agent, 'nikto') !== false || strpos($agent, 'sqlmap') !== false || startswith($url, 'wp-') || startswith($url, 'wordpress') || startswith($url, 'wp/')) `{`
sendBomb();
exit();
`}`
function sendBomb() `{`
//prepare the client to recieve GZIP data. This will not be suspicious
//since most web servers use GZIP by default
header("Content-Encoding: gzip");
header("Content-Length: " . filesize('10G.gzip'));
//Turn off output buffering
if (ob_get_level()) ob_end_clean();
//send the gzipped file to the client
readfile('10G.gzip');
`}`
function startsWith($haystack, $needle) `{`
return (substr($haystack, 0, strlen($needle)) === $needle);
`}`
```

虽然上面给出的这个脚本不能用来防御那些高级攻击者，但它足以对付那些只知道通过修改漏洞扫描工具的参数来进行恶意扫描的脚本小子了。

当这个脚本被调用之后会发生什么呢？

[![](https://p0.ssl.qhimg.com/t01cc6baad61fdeb605.png)](https://p0.ssl.qhimg.com/t01cc6baad61fdeb605.png)

如果你使用了其他脚本/浏览器/设备来测试这项技术的话，请你一定要告诉我你的结果，我会在文章后面将你的结果添加进去，谢谢大家（@geek_at）。

[![](https://p2.ssl.qhimg.com/t01ae36bbc32994add4.png)](https://p2.ssl.qhimg.com/t01ae36bbc32994add4.png)

如果你是一个冒险主义者，你可以自己尝试一下…【[点我尝试](https://blog.haschek.at/tools/bomb.php)】（慎入）
