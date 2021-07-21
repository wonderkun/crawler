> 原文链接: https://www.anquanke.com//post/id/87224 


# 【技术分享】看我如何利用Ruby原生解析器漏洞绕过SSRF过滤器


                                阅读量   
                                **94267**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：edoverflow.com
                                <br>原文地址：[https://edoverflow.com/2017/ruby-resolv-bug/](https://edoverflow.com/2017/ruby-resolv-bug/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t019515fcae2a4dde81.jpg)](https://p3.ssl.qhimg.com/t019515fcae2a4dde81.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：100RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、简介**

****

我在Ruby的**Resolv::getaddresses**中发现了一个漏洞，利用这个漏洞，攻击者可以绕过多个SSRF（Server-Side Request Forgery，服务端请求伪造）过滤器。诸如GitLab以及HackerOne之类的应用程序会受此漏洞影响。这份公告中披露的所有报告细节均遵循HackerOne的[漏洞披露指南](https://www.hackerone.com/disclosure-guidelines)。

此漏洞编号为[CVE-2017-0904](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2017-0904)。

<br>

**二、漏洞细节**

``

**`Resolv::getaddresses`**的执行结果与具体的操作系统有关，因此输入不同的IP格式时，该函数可能会返回空值。在防御SSRF攻击时，常用的方法是使用黑名单机制，而利用这个漏洞可以绕过这种机制。

实验环境为：

环境1：`ruby 2.3.3p222 (2016-11-21) [x86_64-linux-gnu]`

环境2：`ruby 2.3.1p112 (2016-04-26) [x86_64-linux-gnu]`

在环境1中的实验结果如下所示：

```
irb(main):002:0&gt; Resolv.getaddresses("127.0.0.1")
=&gt; ["127.0.0.1"]
irb(main):003:0&gt; Resolv.getaddresses("localhost")
=&gt; ["127.0.0.1"]
irb(main):004:0&gt; Resolv.getaddresses("127.000.000.1")
=&gt; ["127.0.0.1"]
```

在环境2中的实验结果如下所示：

```
irb(main):008:0&gt; Resolv.getaddresses("127.0.0.1")
=&gt; ["127.0.0.1"]
irb(main):009:0&gt; Resolv.getaddresses("localhost")
=&gt; ["127.0.0.1"]
irb(main):010:0&gt; Resolv.getaddresses("127.000.000.1")
=&gt; []
```

在最新稳定版的Ruby中我们也能复现这个问题：

```
$ ruby -v
ruby 2.4.3p201 (2017-10-11 revision 60168) [x86_64-linux]
$ irb
irb(main):001:0&gt; require 'resolv'
=&gt; true
irb(main):002:0&gt; Resolv.getaddresses("127.000.001")
=&gt; []
```

**<br>**

**三、PoC**

```
irb(main):001:0&gt; require 'resolv'
=&gt; true
irb(main):002:0&gt; uri = "0x7f.1"
=&gt; "0x7f.1"
irb(main):003:0&gt; server_ips = Resolv.getaddresses(uri)
=&gt; [] # The bug!
irb(main):004:0&gt; blocked_ips = ["127.0.0.1", "::1", "0.0.0.0"]
=&gt; ["127.0.0.1", "::1", "0.0.0.0"]
irb(main):005:0&gt; (blocked_ips &amp; server_ips).any?
=&gt; false # Bypass
```



**四、根本原因**



接下来我们来分析导致这个漏洞的根本原因。

我在代码片段中添加了一些注释语句，以便读者理顺代码逻辑。

`getaddresses`函数的输入参数（`name`）为待解析的某个地址，在函数内部，该参数会传递给`each_address`函数。

```
# File lib/resolv.rb, line 100
def getaddresses(name)
  ret = []
  each_address(name) `{`|address| ret &lt;&lt; address`}` # Here!
  return ret
end
```

`each_address` 函数内部通过`@resolvers`来处理`name`。

```
# File lib/resolv.rb, line 109
def each_address(name)
    if AddressRegex =~ name
      yield name
      return
    end
    yielded = false
    @resolvers.each `{`|r| # Here!
      r.each_address(name) `{`|address|
        yield address.to_s
        yielded = true
      `}`
      return if yielded
    `}`
end
```

```
# File lib/resolv.rb, line 109
def initialize(resolvers=[Hosts.new, DNS.new])
    @resolvers = resolvers
end
```

进一步跟下去，`initialize`实际的初始化代码如下所示（我保留了源代码中的注释语句，这些语句能提供许多有价值的信息）：

```
# File lib/resolv.rb, line 308
##
# Creates a new DNS resolver.
#
# +config_info+ can be:
#
# nil:: Uses /etc/resolv.conf.
# String:: Path to a file using /etc/resolv.conf's format.
# Hash:: Must contain :nameserver, :search and :ndots keys.
# :nameserver_port can be used to specify port number of nameserver address.
#
# The value of :nameserver should be an address string or
# an array of address strings.
# - :nameserver =&gt; '8.8.8.8'
# - :nameserver =&gt; ['8.8.8.8', '8.8.4.4']
#
# The value of :nameserver_port should be an array of
# pair of nameserver address and port number.
# - :nameserver_port =&gt; [['8.8.8.8', 53], ['8.8.4.4', 53]]
#
# Example:
#
#   Resolv::DNS.new(:nameserver =&gt; ['210.251.121.21'],
#                   :search =&gt; ['ruby-lang.org'],
#                   :ndots =&gt; 1)

# Set to /etc/resolv.conf ¯_(ツ)_/¯
def initialize(config_info=nil)
  @mutex = Thread::Mutex.new
  @config = Config.new(config_info)
  @initialized = nil
end
```

这些代码表明，**`Resolv::getaddresses`**的执行结果与具体操作系统有关，当输入不常见的IP编码格式时，`getaddresses`就会返回一个空的`ret`值。

<br>

**五、缓解措施**



我建议弃用**`Resolv::getaddresses`**，选择`Socket`库。

```
irb(main):002:0&gt; Resolv.getaddresses("127.1")
=&gt; []
irb(main):003:0&gt; Socket.getaddrinfo("127.1", nil).sample[3]
=&gt; "127.0.0.1"
```

Ruby Core开发团队也给出了相同的建议：

“如果待解析地址由操作系统的解析器负责解析，那么检查地址的正确方式是使用操作系统的解析器，而非使用`resolv.rb`。比如，我们可以使用socket库的`Addrinfo.getaddrinfo`函数。

——Tanaka Akira”

```
% ruby -rsocket -e '
as = Addrinfo.getaddrinfo("192.168.0.1", nil)
p as
p as.map `{`|a| a.ipv4_private? `}`
'
[#&lt;Addrinfo: 192.168.0.1 TCP&gt;, #&lt;Addrinfo: 192.168.0.1 UDP&gt;, #&lt;Addrinfo: 192.168.0.1 SOCK_RAW&gt;]
[true, true, true]
```

**<br>**

**六、受影响的应用及gem**



### 

**6.1 GitLab社区版及企业版**

相关报告请参考[此处链接](https://hackerone.com/reports/215105)。

[Mustafa Hasan](https://hackerone.com/strukt)在提交给HackerOne的[报告](https://hackerone.com/reports/135937)中描述了GitLab的一个[SSRF漏洞](https://gitlab.com/gitlab-org/gitlab-ce/issues/17286)，利用本文介绍的这个漏洞，可以轻松绕过前面的补丁。GitLab引入了一个排除列表（即黑名单），但会先使用`Resolv::getaddresses`来解析用户提供的地址，然后将解析结果与排除列表中的值进行比较。这意味着用户再也不能使用诸如`http://127.0.0.1`以及`http://localhost/`这样的地址，这些地址正是Mustafa Hasan在原始报告中提到的地址。绕过排除列表限制后，我就可以扫描GitLab的内部网络。

[![](https://p3.ssl.qhimg.com/t011f83224f32f36cd5.png)](https://p3.ssl.qhimg.com/t011f83224f32f36cd5.png)

[![](https://p5.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p5.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)

[![](https://p1.ssl.qhimg.com/t01ad401dbfbd66c6ed.png)](https://p1.ssl.qhimg.com/t01ad401dbfbd66c6ed.png)

GitLab提供了新的补丁：

[https://about.gitlab.com/2017/11/08/gitlab-10-dot-1-dot-2-security-release/](https://about.gitlab.com/2017/11/08/gitlab-10-dot-1-dot-2-security-release/)

**6.2 private_address_check**

相关报告请参考[此处链接](https://github.com/jtdowney/private_address_check/issues/1)。

[private_address_check](https://github.com/jtdowney/private_address_check)是[John Downey](https://twitter.com/jtdowney)开发的一个Ruby gem，可以用来防止SSRF攻击。真正的过滤代码位于`lib/private_address_check.rb`文件中。private_address_check的工作原理是先使用`Resolv::getaddresses`来解析用户提供的URL地址，然后将返回值与黑名单中的值进行对比。这种场景中，我可以使用GitLab案例中用过的技术再一次绕过这个过滤器。

```
# File lib/private_address_check.rb, line 32
def resolves_to_private_address?(hostname)
  ips = Resolv.getaddresses(hostname)
  ips.any? do |ip| 
    private_address?(ip)
  end
end
```

HackerOne在“Integrations”页面中使用了**private_address_check**来防止SSRF攻击，因此HackerOne也会受这种绕过技术[影响](https://hackerone.com/reports/287245)。

该页面地址为：

`[https://hackerone.com/`{`BBP`}`/integrations](https://hackerone.com/%7BBBP%7D/integrations) `

[![](https://p3.ssl.qhimg.com/t0193bc7f52c02e5465.png)](https://p3.ssl.qhimg.com/t0193bc7f52c02e5465.png)

[![](https://p5.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)](https://p5.ssl.qhimg.com/t01a42eb0d8e6abd673.gif)[![](https://p0.ssl.qhimg.com/t01b3c94bfd88230e9b.png)](https://p0.ssl.qhimg.com/t01b3c94bfd88230e9b.png)

不幸的是，我无法利用这个SSRF漏洞，因此这个问题只是一个过滤器绕过问题。HackerOne还是鼓励我提交问题报告，因为他们会把任何潜在的安全问题纳入考虑范围，而这个绕过技术正好落在这类问题中。

private_address_check在[0.4.0版](https://github.com/jtdowney/private_address_check/commit/58a0d7fe31de339c0117160567a5b33ad82b46af)中修复了这个漏洞。

<br>

**七、不受影响的应用及gem**

****

**7.1 ssrf_filter**

[Arkadiy Tetelman](https://twitter.com/arkadiyt)开发的[ssrf_filter](https://github.com/arkadiyt/ssrf_filter)不受此漏洞影响，因为这个gem会检查返回的值是否为空。

```
# File lib/ssrf_filter/ssrf_filter.rb, line 116
raise UnresolvedHostname, "Could not resolve hostname '#`{`hostname`}`'" if ip_addresses.empty?
```

```
irb(main):001:0&gt; require 'ssrf_filter'
=&gt; true
irb(main):002:0&gt; SsrfFilter.get("http://127.1/")
SsrfFilter::UnresolvedHostname: Could not resolve hostname '127.1'
  from /var/lib/gems/2.3.0/gems/ssrf_filter-1.0.2/lib/ssrf_filter/ssrf_filter.rb:116:in `block (3 levels) in &lt;class:SsrfFilter&gt;'
  from /var/lib/gems/2.3.0/gems/ssrf_filter-1.0.2/lib/ssrf_filter/ssrf_filter.rb:107:in `times'
  from /var/lib/gems/2.3.0/gems/ssrf_filter-1.0.2/lib/ssrf_filter/ssrf_filter.rb:107:in `block (2 levels) in &lt;class:SsrfFilter&gt;'
  from (irb):2
  from /usr/bin/irb:11:in `&lt;main&gt;'
```

**7.2 faraday-restrict-ip-addresses**

[Ben Lavender](https://github.com/bhuga)开发的[faraday-restrict-ip-addresses](https://rubygems.org/gems/faraday-restrict-ip-addresses/versions/0.1.1)也不受此漏洞影响，其遵循了Ruby Code开发团队提供的建议。

```
# File lib/faraday/restrict_ip_addresses.rb, line 61
def addresses(hostname)
      Addrinfo.getaddrinfo(hostname, nil, :UNSPEC, :STREAM).map `{` |a| IPAddr.new(a.ip_address) `}`
    rescue SocketError =&gt; e
      # In case of invalid hostname, return an empty list of addresses
      []
end
```

**<br>**

**八、总结**



感谢[Tom Hudson](https://twitter.com/TomNomNom)以及[Yasin Soliman](https://twitter.com/SecurityYasin)在挖掘这个漏洞过程中提供的帮助。

[John Downey](https://twitter.com/jtdowney)以及[Arkadiy Tetelman](https://twitter.com/arkadiyt)的反应都非常敏锐。John Downey第一时间提供了修复补丁，Arkadiy Tetelman帮我理清了为何他们开发的gem不受此问题影响。
