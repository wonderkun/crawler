> 原文链接: https://www.anquanke.com//post/id/84696 


# 【技术分享】从甲方的角度谈谈WAF测试方法


                                阅读量   
                                **217558**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0129a3db013a4b6019.jpg)](https://p2.ssl.qhimg.com/t0129a3db013a4b6019.jpg)



作者：[lewisec_com ](http://bobao.360.cn/member/contribute?uid=2778418248)****

稿费：300RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**0X01 测试思路**

**环境搭建 **

服务器：使用DVWA搭建一套包含各类漏洞的网站，并开启access日志以供分析。DVWA搭建过程不细说。

WAF：反向代理部署，将DVWA服务器做反向代理后映射出VS IP。测试时所有payload发送至VS IP，经WAF处理后交给DVWA服务器。

测试方法：客户端构造payload提交给VS IP，服务器查看access日志。如被有效识别并过滤，access日志应没有相关内容。

<br>

**0X02 OWASP TOP10 常规防御**

**SQLi **

get型注入：http://10.44.100.18/dvwa/vulnerabilities/sqli/?id=22&amp;Submit=Submit#的参数id可以注入，构造payload提交即可。

post型注入：DVWA登录过程用burpsuite抓包，即可构造post型注入。

**XSS **

反射型XSS和存储型XSS在DVWA中都有，构造payload即可。

CSRF、command injection、Brute Foce、File upload等等方式，DVWA都有了，不细说。

漏掉的是SSRF、反序列化、structs、心脏滴血，这些攻击在当前版本的DVWA中是没有设计的，需要单独考虑。

<br>

**0X03 绕过技术的防御**

除了最常见攻击手法的防御以外，WAF还应该具备识别变形的Payload的能力。 

目前国内外商业WAF可以识别99%以上的常规攻击手段，区别主要就体现在对各类编码后的变形Payload的分析能力上。 

这里面又区分成了两大类思路。

**思路一：**

WAF抓取到HTTP包后，做多重解码，将每重解码的结果提取正则，与特征库进行匹配。各家能解码的层数会有区别。F5的ASM可以支持最多5层并且允许用户手工设定层数。其他家虽不可指定解码层数，但都具备响应能力。

**思路二：**

考虑到正则匹配容易误报漏报，有厂家放弃了这种分析模式，转而做语义分析。长亭科技的SqlChop就是如此，详情可阅读[SQLChop – 一个新型 SQL 注入检测引擎 ](https://blog.chaitin.com/sqlchop-the-sqli-detection-engine/)

在测试中，需要手工对payload做编码变形。详细说来：

SQLi变形

urlencode编码：别小看这种常见的绕过方法，有厂家的WAF还真检测不出来。

unicode编码

关键字大小写替换：这个比较常规了，基本是没有检测不到的。

关键字转为十六进制

关键字用反引号引起来

关键字用/#! #/注释引起来

关键字用/##/注释截断：select转为sel/**/ect

关键字用%00截断

提交的HTTP包中，将x-originating-IP 改为127.0.0.1

提交的HTTP包中，将X-remote-addr 改为127.0.0.1

SQLMAP的各类TAMPER，挨个试一试吧

XSS变形

XSS变形最多，WAF漏报也是最严重的。谁让HTML可利用的标签那么多呢。 

这一块的测试，有赖于测试者平时收集各类XSS payload 的量。我仅列出一部分常见的以供参考： 



```
&lt;embed/src=//goo.gl/nlX0P&gt; 
&lt;object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgiSGVsbG8iKTs8L3NjcmlwdD4="&gt; 
&lt;a onmouseover="window.onerror=;throw 1&gt; 
&lt;svg&gt;&lt;script&gt;varmyvar="YourInput";&lt;/script&gt;&lt;/svg&gt; 
&lt;s%00c%00r%00%00ip%00t&gt;confirm(0);&lt;/s%00c%00r%00%00ip%00t&gt; 
&lt;script&gt;//@cc_on!(1)/*@cc_on~(2)@*/&lt;/script&gt; 
&lt;marquee/onstart=confirm(2)&gt;/ 
&lt;a/onmouseover[x0b]=location='x6Ax61x76x61x73x63x72x69x70x74x3Ax61x6Cx65x72x74x28x30x29x3B'&gt;XSS
```

文件包含绕过

```
data:text/plain;base64,ZGF0YTp0ZXh0L3BsYWluLDw/cGhwIHN5c3RlbSgnY2F0IC92YXIvd3d3L0ZpbGVJbmNsdWRlLnBocCcpPz4=
```

文件上传绕过<br>

文件上传绕过主要考虑几个方面：

123.php.123

123.asp;.gif

as.php%00.gif

文件开头添加GIF89a

burpsuite抓包修改Content-Type: image/jpeg

<br>

**0X04 扫描器防御能力**

WAF应具备根据数据包特征识别扫描器的能力，并加以阻止。常见的扫描器，如WVS、SQLMAP、Netsparker、havij、Appscan都应该拿来实际测试WAF的反映。 

需要说明的一点是，WAF不仅要拦截扫描器发来的数据包，还应在日志中注明，攻击者使用何种扫描器。这对运维人员分析日志很有帮助。 

例如，实际测试中，Imperva对SQLMAP和Netsparker都可以准确识别。而F5的ASM则可以准确识别WVS和SQLMAP。FortiWeb则不具备这个能力。

<br>

**0X05 Webshell防御**

**webshell拦截**

文件上传防御难免百密一疏，普通的webshell上传后，攻击者必然要通过与webshell通信，开展后续渗透。WAF必须有能力识别通信内容，并及时阻断。很多webshell的通信内容是经过base64编码的，WAF必须具备解码后准确分析的能力。 

测试方法很简单，在服务器上放好测试的webshell，客户端通过WAF后访问webshell，执行重要的操作，如：dir、ls、net user等系统命令；连接操作数据库；上传下载文件等。 

这项测试需要收集大量常用webshell，用于覆盖常见webshell的识别。Github上有一个项目收集了各种格式的webshell，妈妈再也不担心我找不到shell啦。 

[Github webshell collect](https://github.com/tennc/webshell)

**一句话拦截**

如果服务器安装有杀毒软件，常见webshell是可以被查杀的。大马能拦住，小马当然也不能放过。一句话木马可是杀软无力识别的。 

防御一句话，其实防御的是菜刀以及各种版本的菜刀与一句话的通信。 

这里要重点说两款工具： 

cknife：[[项目地址]](https://github.com/Chora10/Cknife)，这把刀可以自定义各种通信方式和php执行函数用于绕过waf检测。实际测试下来，的确很多家waf的默认策略对自定义模式拦截无力。 

antSword：[[项目地址]](https://github.com/antoor/antSword/releases)，修改版的菜刀，也很好用。

<br>

**0X06 暴力破解及其他杂项**

**暴力破解 **

WAF必须具备识别工具自动爆破密码的能力，其实判断的原理不难，分析请求某个文件的某几个参数的频率即可。用BurpSuite测一测就知道。在WAF上需要手工配置防爆破的策略，指明请求的URI、用户需要输入的参数名、访问阈值条件。 

F5 ASM在判断暴力破解行为时，会判断会话有效性，造成这里有个bug，使用burpsuite爆密码时ASM根本拦不住。开了售前ticket查了半天，联系研发才闹明白是判断机制设计所致，自然也就无法修改了。

**机器访问 **

为了防止薅羊毛，WAF必须具备能力，根据用户自定义的URI、参数名、源IP/目的IP、目的URL等条件，拦截超出正常频率的机器访问行为。 

这项测试非常考验设备的自定义程度，而Imperva在自定义策略的灵活性上，遥遥领先其他友商，无愧于Gartner第一象限的位置。自定义程度越高，策略越灵活，防御效果越好，对甲方工程师的技术要求也就越高。很多传统行业的甲方工程师由于不熟悉攻防，对HTTP没研究那么深，自定义策略反而成了工作的负担。在和Imperva工程师交流时多次看到其他同行发来的邮件，询问某某场景下实现某功能，应该如何配置。我觉得如果不懂HTTP，WAF干脆就不要玩了，纯粹是给自己找负担。从白帽子的角度来说，目标网站有WAF不可怕，渗透还是要坚持的，万一对方不懂HTTP呢。

**指定参数拦截 **

在post表单中，安全基线要求代码必须判断用户输入内容是否合理。比如，手机号一项，必须提交13/15/17/18开头的11位纯数字。如果编码时实现该需求，一行正则匹配就搞定。但是你不能保证每个程序猿都是勤奋的。所以，用WAF帮助站点实现该需求是必备功能要求。 

WAF必须具备识别制定URI的指定参数，提交的数据格式。这一项也是将各厂家区分开的重要指标。

**命令注入 **

WAF还必须具备识别命令注入攻击的能力，这一项DVWA是提供了测试功能的。之所以重点拿出来说，是因为Imperva、F5 ASM在这里都存在明显的疏漏。常见系统命令，这两家的WAF都不能在默认策略下准确识别。这一点我很奇怪，明明特征库里是有这一类特征的，可为何检出率如此低？

<br>

**0X07 设备自身安全**

WAF除了要保护目标网站的安全性之外，自身的安全性也不可或缺。别不信，FortiWeb的5.5.3版本就存在CSRF漏洞。国产主流的漏洞扫描产品，除了绿盟也都存在CSRF漏洞。 

另外，要使用NMAP等各种工具扫描设备开放的端口，看看有没有什么服务存在已知漏洞。

第三，设备登录入口必须支持连续登录失败X次后拦截登录请求的功能，防止被爆破。 

第四，设备web端会使用类似jQuery等库，而第三方库是有各种已知漏洞的，查到CVE后逐个验证下漏洞是否存在。 

第五，开个WVS扫一扫页面吧，看看有没有什么明显的漏洞。

<br>

**0X08 自学习**

商业WAF相比自研WAF，最大的优势在于自学习功能。商业WAF拥有多项专利技术，可以根据web应用的访问行为和流量，自动学习用户正常访问行为特征，据此建立防御策略。Imperva在这方面技术领先很多，专利也最多。如果用好了自学习功能，WAF的漏过能够很大程度上的改善。 

但是，凡事没有绝对。WAF的自学习功能最大的困扰是误报。Web应用的功能非常复杂，请求方式千奇百怪，机器学习算法再精妙，也不可能百分百还原所有用户正常行为。一旦误判，大量的误报拦截会让管理员叫苦不迭。 

实际测试下来，个人感觉自学习功能更多时候是厂商拿来做宣传的噱头和控标的一个指标项，但是实际在生产环境中使用它，最好还是慎之又慎，就连厂商工程师都不建议使用，你敢给领导打保票背这个雷吗？ 

但是自学习功能并非是聋子的耳朵–摆设。自学习最大的用处其实是分析用户行为的工具。用这个功能连续监控一个月之后，哪个URL被访问次数最多，用户的请求方法与行为是什么，可以通过自动报告一览无余。有了这个报告，后续在做Web应用调优、访客行为分析、判断误报等方面还是很有用的。

<br>

**0X09 第三方测试工具**

除了上述各种手工测试项目，还可以使用第三方开源工具测试WAF的拦截能力。这里推荐两个工具。 

**第一：**碳基体的测试工具：[[项目地址]](https://github.com/tanjiti/WAFTest) 

这款工具是用perl写的，在t文件夹下已经写好了很多测试脚本，这些脚本可以把攻击payload放在http协议的各个字段提交，用于测试WAF在不同http参数的识别能力。具体用法不多说了，碳基体写的非常清楚。 

这里想说两点： 

1. X-Forwared-For是很多WAF会漏过的点。 

2. 没有哪家WAF可以百分百拦截所有测试脚本。换句话说，测出来漏过的地方，需要WAF上手工配置策略，白帽子们也可以在渗透时自由发挥了。

**第二：**Ironbee项目：[[项目地址] ](https://github.com/ironbee/waf-research)

Ironbee是一款开源waf，这个项目是测试拦截率的攻击，也是用perl写的。同样的，baseline-detection目录下的脚本，也不是默认策略可以百分百识别的。

<br>

**0X10 管理与维护**

WAF除了要满足低误报低漏报，还必须人性化易管理。下面的几个功能点，是从管理员角度出发测试的内容。 

设备操作日志：WAF的所有管理员操作必须留存日志备查。 

管理员权限分割：管理员必须不能删除和操作设备日志，管理与审计权限必须分立。 

误报后的快速例外：WAF会出现超过50%的误报，出现误报后，设备必须支持快速且简便的例外策略生成。 

日志包含完整http的request和response，高亮显示违规内容。 

日志可导出：WAF的日志必须支持以标准syslog格式导出，既可以与SIEM联动，也可以让管理员手工分析。 

多种形式的报表展现：包括但不限于自定义源地址、目的地址、攻击手法、规则、日期时间等条件的自由组合生成报表。 

流量可视化展现：统计每个站点流量、统计指定源的流量、统计点击次数，可视化展现。

<br>

**0X11 写在最后**

写这篇文章的初衷，绝非为某个品牌站台，或者贬损某个品牌。我在写作的过程中尽量避免带有个人感情色彩，尽量保持对品牌的中立性。任何WAF都是众多开发人员的辛苦结晶，每家都有自己独到的地方，也难免存在疏漏。希望通过甲方安全人员的和厂商研发人员的共同努力，把WAF完善的更好更易用。

受限于自己技术能力，测试方法和测试内容难免有遗漏或错误，希望读者反馈指正，本人博客：[www.lewisec.com](http://www.lewisec.com)。
