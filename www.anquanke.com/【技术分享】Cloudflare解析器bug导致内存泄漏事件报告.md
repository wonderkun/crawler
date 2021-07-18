
# 【技术分享】Cloudflare解析器bug导致内存泄漏事件报告


                                阅读量   
                                **89317**
                            
                        |
                        
                                                                                                                                    ![](./img/85557/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：cloudflare.com
                                <br>原文地址：[https://blog.cloudflare.com/incident-report-on-memory-leak-caused-by-cloudflare-parser-bug/](https://blog.cloudflare.com/incident-report-on-memory-leak-caused-by-cloudflare-parser-bug/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85557/t01e2b4bd1cbc302705.jpg)](./img/85557/t01e2b4bd1cbc302705.jpg)**

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：260RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**0x00 前言**

上星期五，来自谷歌[Project Zero](https://googleprojectzero.blogspot.co.uk/)组织的[Tavis Ormandy](https://twitter.com/taviso)联系Cloudflare，报告了我们的边界服务器的一个安全问题。他看到经过Cloudflare的一些HTTP请求返回了崩溃的网页。

它出现在一些不寻常的情况下，在下面我将详细介绍，我们的边界服务器运行时缓冲区越界了，并返回了隐私信息，如 HTTP cookies，认证令牌，HTTP POST体和其他敏感数据的内存。并且有些数据会被搜索引擎缓存。

为了避免怀疑，Cloudflare客户的SSL私钥没有泄漏。Cloudflare总是通过一个隔离的Nginx实例来结束SLL连接，因此不受这个bug影响。

我们快速的确认了这个问题，并关闭了3个Cloudflare功能（[邮件混淆](https://support.cloudflare.com/hc/en-us/articles/200170016-What-is-Email-Address-Obfuscation-)，[服务端排除](https://support.cloudflare.com/hc/en-us/articles/200170036-What-does-Server-Side-Excludes-SSE-do-)和[自动HTTPs重写](https://support.cloudflare.com/hc/en-us/articles/227227647-How-do-I-use-Automatic-HTTPS-Rewrites-)），这些都用来了相同的HTML解析器链，会导致泄漏。这样在一个HTTP响应中就不会有内存返回了。

因为这个bug的严重性，来自San Francisco和 London的软件工程师、信息安全和操作的交叉功能团队充分了解了潜在的原因，为了降低内存泄漏的影响，和谷歌和其他搜索引擎团队一起将缓存的HTTP响应移除了。

拥有一个全球化的团队，每12小时为间隔，每天24小时交替解决这个问题。团队持续的努力确保了问题的圆满解决。作为服务的一个优势是这个bug从报告到解决，花了几分钟到几小时，而不是几个月。针对这样的bug部署修复方案的工业标准通常是3个月；我们在小于7个小时就圆满解决，47分钟内就缓解了bug。

这个bug是严重的，因为泄漏的内存包含了隐私信息，并且还会被搜索引擎缓存。我们还没有发现这个bug的漏洞利用或者它们存在的报告。

影响最大的时期是2月13日到2月18号，通过Cloudflare的每3,300,000个HTTP请求中约有1个可能导致内存泄漏（约为请求的0.00003％）。

我们感谢它由世界顶级安全研究团队发现并报告给我们。

本文很长，但是作为我们的传统，我们倾向于对我们的服务出现的问题保持开放和技术上的详细描述。

<br>

**0x01 运行时解析并修改HTML**

很多Cloudflare服务依赖通过我们的边界服务器时解析和修改HTML页面。例如，我们能通过修改HTML页面来插入谷歌分析标签，安全的重写http://链接为https://，排除来自机器人的部分页面，模糊电子邮件地址，启用AMP等。

为了修改页面，我们需要读取并解析HTML以发现需要修改的元素。因为在Cloudflare的早期，我们已经使用了用Ragel编写的解析器。一个独立的.rl文件包含一个HTML解析器，被用来在Cloudflare平台修改HTML。

大约一年前，我们认为Ragel解析器维护起来太复杂，并且我们开始写一个新的解析器（cf-html）来替代它。这个解析器能正确处理HTML5，而且非常非常快且易维护。

我们首先将这个解析器用于自动HTTP重写功能，并一直慢慢地迁移cf-html替换Ragel。

Cf-html和老的Ragel解析器都作为Nginx模块实现，并编译到我们的Nginx构建中。这个Nginx过滤模块解析包含HTML响应的缓冲区（内存块），做出必要的修改，并将缓冲区传递给下一个过滤模块。

这样，引起内存泄漏的bug在我们的Ragel解析器中已存在多年，但是因为我们内部Nginx使用缓冲区的方式，并没有内存泄漏。Cf-html巧妙的改变了缓冲去，导致在cf-html中不会有问题。

因为我们知道了这个bug是由激活cf-html引起的（但是之前我们知道为什么），我们禁用了使用它的3个功能。Cloudflare每个功能都有一个相应的功能标志，我们称之为全局杀手。我们在收到问题细节报告后的47分钟时启用了邮件混淆的全局杀手，并在3小时5分钟后关闭了自动HTTP重写。邮件混淆功能在2月13号已经修改了，并且是内存泄漏的原因，因此禁用它快速地阻止了几乎所有的内存泄漏。

在几秒内，这些功能在全球范围内被禁用。我们确定没有通过测试URI来泄漏内存，并且谷歌的二次校验也一样。

然后，我们发现了第三个功能（服务端排除）也有这个漏洞，但是没有全局杀手开关（它非常老，在全局杀手之前实现）。我们为服务端排除实现了一个全局杀手，并全球部署补丁。从发现服务端排除是个问题到部署补丁只花了3个小时。然而，服务端排除很少使用，且只针对对恶意的IP地址才激活。

<br>

**0x02 bug的根因**

Ragel代码转化为C代码，然后编译。这个C代码使用经典的C方法，指向HTML文档的指针被解析，并且Ragel自身给用户提供了针对这些指针大量的控制权。因为一个指针错误导致的bug的产生。



```
/* generated code */
if ( ++p == pe )
    goto _test_eof;
```

bug的根因是，使用等于运算符来校验是否到达缓冲区的末端，并且指针能够步过缓冲去末端。这是熟知的缓冲去溢出。使用&gt;=代替==来做检验，将跳过缓冲区末端。这个等于校验由Ragel自动生成，不是我们编写的代码。意味着我们没有正确的使用Ragel。

我们编写的Ragel代码包含了一个bug，其能引起指针越界且给了等号校验造成缓冲区溢出的能力。

下面是Ragel代码的一段代码，用来获取HTML &lt;script&gt;标签中的一个属性。第一行说的是它试图找到更多以空格，正斜杠或&gt;结尾的unquoted_attr_char。（:&gt;&gt;是连接符）



```
script_consume_attr := ((unquoted_attr_char)* :&gt;&gt; (space|'/'|'&gt;'))
&gt;{ ddctx("script consume_attr"); }
@{ fhold; fgoto script_tag_parse; }
$lerr{ dd("script consume_attr failed");
       fgoto script_consume_attr; };
```

如果一个属性格式良好，则Ragel解析器跳转到@{}代码块。如果解析属性失败（就是我们今天讨论的bug的开始），那么到$lerr{}。

举个例子，在实际情况下（细节如下），如果web页面以错误的HTML标签结尾，如：

```
&lt;script type=
```

$lerr{ }块将执行，并且缓冲去将溢出。这个例子中$lerr执行dd(“script consume_attr failed”);（这是个调试语句），然后执行fgoto script_consume_attr;（转移到script_consume_attr去解析下一个属性）。

从我们的分析中看，这样错误的标签出现在大约0.06%的网站中。

如果你观察仔细，你可能已经注意到@{ }也是一个fgoto，但是在它之前执行了fhold，并且$lerr{ }没有。它没有fhold导致了内存泄漏。

在内部，生成的C代码有一个指针p，指向HTML文档中正在检测的字符。Fhold等价于p–，并且是必要的。因为当错误条件发生时，p将指向导致script_consume_attr失败的字符。

并且它非常重要，因为如果这个错误条件发生在包含HTML文档的缓冲区的末尾，则p将在文档末端的后面（p将是pe+1），且达到缓冲区末尾的校验将失败，p将在缓冲去外部运行。

添加一个fhold到错误处理函数中，能解决这个问题。

<br>

**0x03 为什么**

上面解释了指针如何运行超过缓冲区的末尾，但是问题内部为什么没有显示。毕竟，这个代码在生产环境上已经稳定很多年了。

回到上面定义的script_consume_attr:



```
script_consume_attr := ((unquoted_attr_char)* :&gt;&gt; (space|'/'|'&gt;'))
&gt;{ ddctx("script consume_attr"); }
@{ fhold; fgoto script_tag_parse; }
$lerr{ dd("script consume_attr failed");
       fgoto script_consume_attr; };
```

当解析器解析超过字符范围时会发生什么，当前被解析的缓冲区是否是最后一个缓冲区是不同的。如果它不是最后一个缓冲区，那么没必要使用$lerr，因为解析器不知道是否会发生错误，因为剩余的属性可能在下一个缓冲区中。

但是如果这是最后一个缓冲区，那么$lerr被执行。下面是代码末尾如何跳过了文件末尾且运行内存。

解析函数的入口点是ngx_http_email_parse_email（名字是古老的，它不止做了邮件解析的事）。



```
ngx_int_t ngx_http_email_parse_email(ngx_http_request_t *r, ngx_http_email_ctx_t *ctx) {
    u_char  *p = ctx-&gt;pos;
    u_char  *pe = ctx-&gt;buf-&gt;last;
    u_char  *eof = ctx-&gt;buf-&gt;last_buf ? pe : NULL;
```

你能看到p指向缓冲区的第一个字符，pe是缓冲区后的字符，且pe设置为eof。如果这是这个链中的最后一个缓冲区（有boolean last_buf表示），否者为NULL。

当老的和新的解析器在请求处理时同时存在，这类缓冲区将传给上面的函数。



```
(gdb) p *in-&gt;buf
$8 = {
  pos = 0x558a2f58be30 "&lt;script type="",
  last = 0x558a2f58be3e "",
  [...]
  last_buf = 1,
  [...]
}
```

上面是数据，last_buf是1。当新的解析器不存在时，最后一个缓冲区包含的数据如下：



```
(gdb) p *in-&gt;buf
$6 = {
  pos = 0x558a238e94f7 "&lt;script type="",
  last = 0x558a238e9504 "",
  [...]
  last_buf = 0,
  [...]
}
```

最后的空缓冲区（pos和last都是NULL且last_buf=1）接着那个缓冲区，但是如果缓冲区是空的，ngx_http_email_parse_email不会被调用。

因此，只有当老的解析器存在是，最后一个缓冲区包含的数据才有last_buf是0。这意味着eof将是NULL。现在当试图在缓冲区末尾处理一个不完整的script_consume_attr。$ lerr将不会被执行，因为解析器相信（因为last_buf）可能有更多的数据来了。

当两个解析器都存在时，情况是不同的。 last_buf为1，eof设置为pe，$ lerr代码运行。下面是生成的代码：



```
/* #line 877 "ngx_http_email_filter_parser.rl" */
{ dd("script consume_attr failed");
              {goto st1266;} }
     goto st0;
[...]
st1266:
    if ( ++p == pe )
        goto _test_eof1266;
```

解析器解析完字符，而试图执行script_consume_attr， p将是pe。因为没有fhold（这将做p–），当代码跳转到st1266， p增加将超过pe。

然后不会跳转到_test_eof1266（在这将执行EOF校验），并且将超过缓冲区末尾，试图解析HTML文档。

因此，bug潜伏了多年，直到在NGINX过滤器模块之间传递的缓冲区的内部风水随着cf-html的引入而改变。

<br>

**0x04 继续寻找bug**

在1960和1970年代，IBM的研究展示了bug集中在易错模块中。因为我们在Ragel生成的代码中找到了一个讨厌的指针溢出，所以将谨慎的去查找其他的bug。

信息安全团队的一部分人开始模糊测试生成的代码，来查找潜在的指针溢出。另一个团队使用恶意构造的web网页构建测试用例。软件工程师团队开始手动排查代码问题。

决定在生成的代码中为每个访问的指针显式添加校验，并且计入任何发生的错误。生成的错误被反馈到我们的全局错误记录基础结构，用于分析。



```
#define SAFE_CHAR ({
    if (!__builtin_expect(p &lt; pe, 1)) {
        ngx_log_error(NGX_LOG_CRIT, r-&gt;connection-&gt;log, 0, "email filter tried to access char past EOF");
        RESET();
        output_flat_saved(r, ctx);
        BUF_STATE(output);
        return NGX_ERROR;
    }
    *p;
})
我们
```

看到日志如下：

```
2017/02/19 13:47:34 [crit] 27558#0: *2 email filter tried to access char past EOF while sending response to client, client: 127.0.0.1, server: localhost, request: "GET /malformed-test.html HTTP/1.1”
```

每行日志表示一个HTTP请求，可能有泄漏的内存。通过记录问题发生的频率，我们希望得到在错误存在时HTTP请求泄漏内存的次数的统计。

为了针对内存泄漏，下面的东西必须正确：

最后一个缓冲区包含的数据必须以以恶意格式的脚本或者img标签结束

缓冲区必须小于4K长度（否则Nginx可能崩溃）

用户必须开启邮件混淆（因为她同时使用新旧解析器）。

…或者自动HTTPs重写/服务端排除（使用了新解析器）组合另一个使用老的解析器的功能。…并且服务端排除只有在客户端IP具有较差的信誉（即它对大多数访问者不起作用）时才执行。

那就解释了为什么缓冲区溢出导致了内存泄漏的发生的情况如此少。

此外，邮件模糊功能（使用两个解析器，并会使错误发生在大多数Cloudflare网站上）仅在2月13日（Tavis报告的前四天）启用。

涉及的三个功能按如下顺序推出。内存可能泄漏的最早的日期是2016-09-22。

2016-09-22 Automatic HTTP Rewrites 启用

2017-01-30 Server-Side Excludes 整合新的解析器

2017-02-13 Email Obfuscation 部分整合新的解析器

2017-02-18 Google 报告问题给Cloudflare且泄漏结束

最大的潜在威胁发生在2月13号开始的4天内，因为自动HTTP重写没有被广泛使用，服务端排除只对恶意的IP地址才有效。

<br>

**0x05 Bug的内部影响**

Cloudflare在边界机器上面运行了多个独立的进程，且提供了进程和内存隔离。内存泄漏来自与一个基于Nginx的进程（处理HTTP）。它有一个独立的进程堆处理SSL，图片压缩和缓存，意味着我们很很快判断我们客户的SSL私钥没有泄漏。

然而，内存空间的泄漏包含了敏感信息。泄漏的信息中明显的一个是用于在Cloudflare机器之间安全连接的私钥。

当处理客户网站HTTP请求时，我们的边界机器在机架内，在数据中心内，以及用于记录，缓存和从源Web服务器检索网页的数据中心之间相互通信。

为了响应对互联网公司的监控活动的高度关注，我们决定在2013年加密Cloudflare机器之间的所有连接，以防止这样的攻击，即使机器坐在同一机架。

泄漏的私钥是用于此机器加密的私钥。在Cloudflare内部还有少量的密钥用于认证。

<br>

**0x06 外部影响和缓存清除**

更关心的事实是大量的Cloudflare客户的HTTP请求存在于转储的内存中。这意味着隐私信息泄露了。

这包括HTTP头，POST数据（可能包含密码），API调用的JSON，URI参数，Cookie和用于身份认证的其他敏感信息（例如API密钥和OAuth令牌）。

因为Cloudflare运行大型共享基础架构，因此对易受此问题影响的Cloudflare网站的HTTP请求可能会泄露不相关的其他Cloudflare站点的信息。

另一个问题是，Google（和其他搜索引擎）通过其正常的抓取和缓存过程缓存了一些泄漏的内存。我们想要确保在公开披露问题之前从搜索引擎缓存中清除这些内存，以便第三方无法搜索敏感信息。

我们倾向是尽快得到错误的消息，但我们认为我们有责任确保搜索引擎缓存在公开宣布之前被擦除。

信息安全团队努力在搜索引擎缓存中识别已泄漏内存并清除内存的URI。在Google，Yahoo，Bing和其他人的帮助下，我们发现了770个已被缓存且包含泄漏内存的独特的URI。770个独特的URI涵盖161个唯一域。泄漏的内存已经在搜索引擎的帮助下清除。

我们还进行其他搜索，寻找在像Pastebin这样的网站上可能泄漏的信息，且没有找到任何东西。

<br>

**0x07 一些课题**

新的HTML解析器的工程师一直担心影响我们的服务，他们花了几个小时来验证它不包含安全问题。

不幸的是，这是一个古老的软件且包含一个潜在的安全问题，而这个问题只出现于我们在迁移抛弃它的过程。我们的内部信息安全团队现在正在进行一个项目，以模糊测试旧软件的方式寻找潜在的其他安全问题。

<br>

**0x08 时间点细节**

我们非常感谢Google的同事就此问题与我们联系，并通过其解决方案与我们密切合作。所有这些都没有任何报告,表明外界的各方已经确定了问题或利用它。

所有时间均为UTC时间。

2017-02-18 0011 来自Tavis Ormandy的推特寻求Cloudflare的联系方式 

2017-02-18 0032 Cloudflare 收到来自谷歌的bug细节 

2017-02-18 0040 多个团队汇集在San Francisco 

2017-02-18 0119 全球范围内关闭邮件混淆功能 

2017-02-18 0122 London团队加入 

2017-02-18 0424 自动HTTPs重写功能关闭 

2017-02-18 0722 实现针对cf-html解析器的关闭开关，并全球部署

2017-02-20 2159 SAFE_CHAR 修复部署

2017-02-21 1803 自动HTTPs重写，服务端排除和邮件混淆重启功能
