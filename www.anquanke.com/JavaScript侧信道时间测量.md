> 原文链接: https://www.anquanke.com//post/id/170268 


# JavaScript侧信道时间测量


                                阅读量   
                                **214148**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01bb92ad9d51dbf63b.jpg)](https://p2.ssl.qhimg.com/t01bb92ad9d51dbf63b.jpg)



## 前言

最近因为需求，需要测量JavaScript单个函数的执行时间，但由于精度问题，遇到了各种各样的问题，在此做简单记录。



## JavaScript高精度时间函数

首先得明确，JavaScript单个函数执行时间应该是微秒级的，所以必须需要高精度。那么第一反应自然是查找是否有相关函数，以往的时间函数`new Date().getTime()`肯定是不够了，因为其精度为毫秒级，测量函数执行时间，得到的结果必然为0。<br>
这里我们查阅手册，将目光定位到`performance.now()`<br>
我们不妨做个测试

```
let n = 0;
while (n&lt;10000)`{`
  console.log((new Date()).getTime());
  n = n+1;
`}`
```

得到结果

[![](https://p3.ssl.qhimg.com/t01d1759eaed883180b.png)](https://p3.ssl.qhimg.com/t01d1759eaed883180b.png)

而对于

```
let n = 0;
while (n&lt;10000)`{`
  console.log(performance.now());
  n = n+1;
`}`
```

得到结果

[![](https://p2.ssl.qhimg.com/t01b5990a568adcc7a3.png)](https://p2.ssl.qhimg.com/t01b5990a568adcc7a3.png)

我们可以轻易的看出，这里进行一次循环大概是0.04ms，而精度在ms级的`new Date().getTime()`已经无能为力



## 精度失灵

既然确定了`performance.now()`，不妨在Chrome进行测试

[![](https://p1.ssl.qhimg.com/t01e714f258ffaa603c.png)](https://p1.ssl.qhimg.com/t01e714f258ffaa603c.png)

我们可以轻松测量出`crypto.getRandomValues(new Uint8Array(10))`的运行时间大概为0.1ms

但由于可能存在误差，我尝试运行1000次，却出现了问题

[![](https://p1.ssl.qhimg.com/t01e36941a8be8595aa.png)](https://p1.ssl.qhimg.com/t01e36941a8be8595aa.png)

竟然出现了大量的0

我又在我虚拟机里的Chrome运行

[![](https://p2.ssl.qhimg.com/t0159901e5072456162.png)](https://p2.ssl.qhimg.com/t0159901e5072456162.png)

这是什么原因？对比之后发现

虚拟机

[![](https://p1.ssl.qhimg.com/t01b4d65b192f2a307c.png)](https://p1.ssl.qhimg.com/t01b4d65b192f2a307c.png)

而物理机

[![](https://p2.ssl.qhimg.com/t01507004d6b85645f8.png)](https://p2.ssl.qhimg.com/t01507004d6b85645f8.png)

查阅Chrome的Updates (2018)

由于高精度的时间可应用于重大漏洞speculative execution side-channel attack(`https://spectreattack.com/`)

所以各大主流浏览器做出了安全措施

例如FireFox、Safari，将`performance.now()`精度降低为1ms

[![](https://p2.ssl.qhimg.com/t018af0fe0030df7abd.png)](https://p2.ssl.qhimg.com/t018af0fe0030df7abd.png)

[![](https://p3.ssl.qhimg.com/t01ce70cc899e8f67f8.png)](https://p3.ssl.qhimg.com/t01ce70cc899e8f67f8.png)

而Chrome改为100微秒并加入了抖动

[![](https://p4.ssl.qhimg.com/t01bf5d7d1fa12a1fe1.png)](https://p4.ssl.qhimg.com/t01bf5d7d1fa12a1fe1.png)

所以这也不难解释，为什么Chrome 71版本得到这么多0，相比FireFox、Safari，能得到数据，已经算是仁慈了



## 柳暗花明

那么怎么进行高精度测量呢？不能因为浏览器的不支持，我们就不完成需求吧~

这里查阅文章发现

```
https://link.springer.com/chapter/10.1007/978-3-319-70972-7_13
```

一文中进行了JavaScript侧信道测量时间的介绍

由于精度问题，例如

```
var start = performance.now();
func()
var end = performance.now();
```

会使得`start = end`,这样测量出来只能为0，而作者很巧妙的使用了`wait_edge()`

```
function wait_edge()
`{`
    var next,last = performance.now();
    while((next = performance.now()) == last)
    `{``}`
    return next;
`}`
```

这样一来就可以到下一次performance.now()的时候再继续

那么问题又来了，中间空转的时间怎么办呢？

作者又使用了`count_edge()`进行了空转次数探测

```
function count_edge()
`{`
    var last = performance.now(),count = 0;
    while(performance.now() == last) count++;
    return count;
`}`
```

那么怎么把空转次数的单次时间测量出来呢？这里作者又设计了`calibrate()`

```
function calibrate()
`{`
    var counter = 0,next;
    for(var i=0;i&lt;10;i++)
    `{`
        next = wait_edge();
        counter += count_edge();
    `}`
    next = wait_edge();
    return (wait_edge() - next)/(counter/10.0);
`}`
```

假设我们要测量函数fuc()，即可如下编写即可

```
function measure()
`{`
    var start = wait_edge();
    fuc();
    var count = count_edge();
    return (performance.now()-start)-count*calibrate();
`}`
```

即结束减去开始的时间，再减去中间空转的时间。

我们再来用chrome 71测试一下

[![](https://p3.ssl.qhimg.com/t018d9a0ec0ba260a59.png)](https://p3.ssl.qhimg.com/t018d9a0ec0ba260a59.png)

和之前的`performance.now()`对比

[![](https://p3.ssl.qhimg.com/t01e36941a8be8595aa.png)](https://p3.ssl.qhimg.com/t01e36941a8be8595aa.png)

显然误差已经控制在了0.01ms，即10微秒内，这是我们能接受的

当然，在FireFox这种ms级的更有成就感，因为之前的结果都是0，但是用这样的方法，可以测量了

FireFox:

[![](https://p3.ssl.qhimg.com/t0187fdccacdaa477a7.png)](https://p3.ssl.qhimg.com/t0187fdccacdaa477a7.png)

[![](https://p4.ssl.qhimg.com/t012750d64fd8cc004d.png)](https://p4.ssl.qhimg.com/t012750d64fd8cc004d.png)



## 测试与结论

我以`crypto.getRandomValues(new Uint8Array(n));`为例测试

用`performance.now()`的结果和`measure()`进行做差比较，不难发现

### <a class="reference-link" name="Chrome"></a>Chrome

在Chrome 57版本下，差异仅在10微秒以内。(注：结果由`performance.now()`经过进制转换输出)

[![](https://p2.ssl.qhimg.com/t01499140458d6ca947.png)](https://p2.ssl.qhimg.com/t01499140458d6ca947.png)

[![](https://p0.ssl.qhimg.com/t0132cd12f4a35cd268.png)](https://p0.ssl.qhimg.com/t0132cd12f4a35cd268.png)

而在Chrome 71版本下，差异却达到了50微秒以内(注：结果由`performance.now()`经过进制转换输出)

[![](https://p5.ssl.qhimg.com/t01507004d6b85645f8.png)](https://p5.ssl.qhimg.com/t01507004d6b85645f8.png)

[![](https://p1.ssl.qhimg.com/t010ea11090b72a5868.png)](https://p1.ssl.qhimg.com/t010ea11090b72a5868.png)

原因也很明显，因为71版本的`performance.now()`降低了精度，并且加入了抖动，导致许多`end-start`的值为0

那么我们在71版本下直接测试侧信道方式得到的时间

[![](https://p2.ssl.qhimg.com/t01528284731e929316.png)](https://p2.ssl.qhimg.com/t01528284731e929316.png)

不难发现，其实在71版本下计算差是没有意义的，因为`performance.now()`的精度已经变为100微秒

所以做差得到的值基本是侧信道方式测得的结果。

所以我们基本可以确定，这样的方式在目前chrome版本可以得到比`performance.now()`更高精度的时间测量

但我们的目的肯定不局限于Chrome，我们再看看Firefox

### <a class="reference-link" name="Firefox"></a>Firefox

对于Firefox就更过分了,通过`performance.now()`测量高精度时间直接变成了不可能，因为精度被调整成了毫秒级，所以`end-start`的值都变为了0

[![](https://p3.ssl.qhimg.com/t01ca7fc6b5033fa7b9.png)](https://p3.ssl.qhimg.com/t01ca7fc6b5033fa7b9.png)

而对于侧信道测量方式

[![](https://p1.ssl.qhimg.com/t019ddcf076aff45e62.png)](https://p1.ssl.qhimg.com/t019ddcf076aff45e62.png)

我们依旧还是可以测量出许多微秒级的时间



## 后记

这样的方式可以有效突破浏览器的高精度函数毫秒级的限制，甚至对于一些特定攻击依旧奏效。

若有更好的方式还请大佬不吝赐教~



## 参考链接

[https://zhuanlan.zhihu.com/p/32629875](https://zhuanlan.zhihu.com/p/32629875)

[https://link.springer.com/chapter/10.1007/978-3-319-70972-7_13](https://link.springer.com/chapter/10.1007/978-3-319-70972-7_13)
