> 原文链接: https://www.anquanke.com//post/id/86676 


# 【技术分享】如何使用Shodan及Go语言扫描多个目标


                                阅读量   
                                **97113**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：medium.com/@woj_ciech
                                <br>原文地址：[https://medium.com/@woj_ciech/scan-multiple-organizations-with-shodan-and-golang-bug-bounty-example-d994ba6a9587](https://medium.com/@woj_ciech/scan-multiple-organizations-with-shodan-and-golang-bug-bounty-example-d994ba6a9587)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t0115e78f3b86308d3d.jpg)](https://p4.ssl.qhimg.com/t0115e78f3b86308d3d.jpg)**

****

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

我使用Go语言开发了一段小脚本程序，这个程序可以根据给定的目标列表查询Shodan数据库。然后，我从Bugcrowd网站上搜集了所有的漏洞奖励项目，将这两者结合起来进一步研究。详细细节如下文所述。

<br>

**二、简介**

故事的开始源自于我的一个想法，我想学习一门新的语言，并研发与安全方面有关的程序。我选择使用Go（Golang）语言以及Shodan。我一直在思考的是为什么要使用多种工具来扫描一个目标，我们完全可以使用一个工具来扫描多个目标（作为一名安全研究员，我并没有一个明确的测试目标）。

让我们从头开始一步步讲解，如果有人不知道Shodan的话，下图就是Shodan的主页：

[![](https://p5.ssl.qhimg.com/t01e3e71c32532abcd7.png)](https://p5.ssl.qhimg.com/t01e3e71c32532abcd7.png)

备注：本次实验中，没有任何refrigerators服务被攻击或被关闭

除了webcams、refrigerators、[**SCADA系统**](https://threatpost.com/exposing-scada-systems-shodan-110910/74644/)、[**MMQT**](https://community.arm.com/iot/b/blog/posts/is-your-personal-information-available-via-public-mqtt-brokers)、磁盘挂载服务之外，Shodan还可以用来枚举子域名，因此在目标侦察中能发挥很大的作用。作为“世界上最可怕的搜索引擎”，我们可以在Shodan上使用诸如“port”、“city”、“hostname”或者“org”之类的过滤器来搜索目标，我想你应该知道这意味着什么。

<br>

**三、关于脚本**

这是我第一次接触Go语言。我很快就熟悉了这门语言（[**官方入门文档**](https://tour.golang.org/welcome/1)非常有用），然后就开始开发程序。万事开头难，不过StackOverflow在这个过程中发挥了很大作用。程序本身并不是个完美的作品，但对我来说仍然非常有意义。

脚本首先会读取包含目标名称的文件，一行代表一个目标，然后会向Shodan数据库发起请求。

用法如下：

```
./shodan hosts.txt
```

hosts.txt的内容如下：



```
Sony
Facebook
Dropbox
```

输出结果的计数值有点问题，不要理会这个信息。此外，我们并不关心smb、smtp或者dns服务，因此我请求了最常用的HTTP端口。最终的查询请求如下所示：

```
org:’Sony’ port:’80, 81, 443, 8000, 8001, 8008, 8080, 8083, 8443, 8834, 8888'
```

Sony并不是个精确的关键词，这个关键词可能对应如下信息：



```
Sony Network Communications
Sony Computer Entertainment America LLC
Sony Network Taiwan Limited
Sony Communication Network Corporation
Sony Pictures Entertainment
Sony Media Software and Services
```

[![](https://p5.ssl.qhimg.com/t0195d95003aeddf41b.png)](https://p5.ssl.qhimg.com/t0195d95003aeddf41b.png)

因此，脚本会向用户询问具体要扫描的目标。测试过程中非常重要的一点，就是不要误伤不在原定范围内或者不在漏洞奖励项目范围内的那些目标。

精确的请求示例如下所示：

[![](https://p0.ssl.qhimg.com/t0181966c7dce87e60e.png)](https://p0.ssl.qhimg.com/t0181966c7dce87e60e.png)

脚本会根据目标名称创建相应目录，HTTP响应数据会保存为与IP地址相对应的文件名。此外，我还添加了端口信息以及主机名信息（如果这类信息存在的话）。

典型输出结果如下所示：

[![](https://p4.ssl.qhimg.com/t01ad7533eb292763f9.png)](https://p4.ssl.qhimg.com/t01ad7533eb292763f9.png)

<br>

**四、意义所在**

我们这么做当然是想找到漏洞，许多陈旧的、被遗忘的或者没有更新的子域名经常会存在漏洞。Shodan可以从安全视图角度找到有趣的Web应用，这些应用可能会存在信息泄露漏洞或者其他或多或少的漏洞。为了证实这一点，我利用[goquery](https://github.com/PuerkitoBio/goquery)（函数细节如下所示）爬取了[官方漏洞奖励名单](https://bugcrowd.com/list-of-bug-bounty-programs)中的所有目标，然后将这些目标作为我的脚本的输入。



```
func bugcrowd() []string`{`
 doc, err := goquery.NewDocument("https://www.bugcrowd.com/bug-bounty-list/")
        if err != nil `{` // if cant connect
                log.Fatal(err)
        `}`
s := make([]string, 455 ) //slice of strings
doc.Find("td a").Each(func(index int, item *goquery.Selection) `{` //for every organization in "td a" (table)
     linkTag := item.Text() // get text
     s[index] = linkTag //put in to map
     `}`)
 return s // return slice of organizations
`}`
```

选取目标范围时我必须异常谨慎。如果某个目标范围内只有一个域名，那么我们不需要扫描，只要处理下一个目标就可以。

对于目标组织来说，只有允许我们测试它们的基础设置或者具备“*.domain”的那些目标才是我们的潜在测试对象。

<br>

**五、漏洞搜集**

完成目标公司的扫描任务后，稍加分析，我就在已扫描的网站上找到本地文件包含（LFI）漏洞，这个过程并没有花费太长时间。我已经反馈了这个漏洞，当漏洞被修复后，我会更新这篇文章，添加更多细节。

根据一个链接拓展另一个链接是非常重要的信息来源，根据这种方法，我发现了路径泄露、内部地址以及主机名等其他许多信息。此外，某些网站看起来已经有10年的历史，因此我们可以好好分析这些站点，尝试已知的攻击技巧。

此外，程序输出中还包含许多403、404或者401错误，我们可以在bash中使用如下命令删除这些错误信息：

```
find -exec grep -l ‘404’ `{``}` ;| xargs rm
```



**<br>**

**六、总结**

这个脚本可以用来查找漏洞奖励目标是否存在漏洞。我还记得某人找到过Apache中的Open Redirect（开放重定向）漏洞，利用这个漏洞扫描了漏洞奖励名单中的所有目标，然后报告了所有的问题。我所开发的工具的思想是“数量重于质量”（当然仅适用于本文讨论的情况），读者可以以此为据点，需要深入分析获取到的结果，以找到有价值的信息。我还没有分析所有的输出文件，但直觉上认为本地文件包含漏洞并不是唯一存在的一个漏洞。

大家可以访问[此链接](https://bugcrowd.com/list-of-bug-bounty-programs)下载完整的脚本。
