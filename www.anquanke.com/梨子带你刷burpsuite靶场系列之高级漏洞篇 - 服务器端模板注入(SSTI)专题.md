> 原文链接: https://www.anquanke.com//post/id/246293 


# 梨子带你刷burpsuite靶场系列之高级漏洞篇 - 服务器端模板注入(SSTI)专题


                                阅读量   
                                **46885**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t011796028579bdd09e.png)](https://p3.ssl.qhimg.com/t011796028579bdd09e.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 高级漏洞篇介绍

> 相对于服务器端漏洞篇和客户端漏洞篇，高级漏洞篇需要更深入的知识以及更复杂的利用手段，该篇也是梨子的全程学习记录，力求把漏洞原理及利用等讲的通俗易懂。



## 高级漏洞篇 – 服务器端模板注入(SSTI)专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AB%AF%E6%A8%A1%E6%9D%BF%E6%B3%A8%E5%85%A5(SSTI)%EF%BC%9F"></a>什么是服务器端模板注入(SSTI)？

SSTI就是攻击者利用原生模板语法将恶意payload注入到可以在服务器端执行的模板中的过程。模板引擎就是将固定的模板与可变化的数据结合构建网页，当模板引擎将用户输入直接与固定模板拼接时可能存在SSTI漏洞。注入的恶意payload甚至可以控制服务器，所以服务端的漏洞危害比客户端的漏洞大很多。

### <a class="reference-link" name="SSTI%E6%BC%8F%E6%B4%9E%E6%98%AF%E5%A6%82%E4%BD%95%E4%BA%A7%E7%94%9F%E7%9A%84%EF%BC%9F"></a>SSTI漏洞是如何产生的？

就像Sql注入一样，并没有将语句和数据区分开，导致他们被当成一个整体了，SSTI也是，并没有将模板与数据区分开，就可能导致我注入的数据也可能会变成模板的一部分甚至其他的代码部分被执行。举个例子，我们要批量发送邮件，只需要替换收件人，使用twig模板引擎的语句像这样<br>`$output = $twig-&gt;render("Dear `{`first_name`}`,", array("first_name" =&gt; $user.first_name) );`<br>
我们看到这里并不会导致SSTI漏洞，因为它将模板和数据区分开了，不会被当成一个整体解析。但是如果像这样<br>`$output = $twig-&gt;render("Dear " . $_GET['name']);`<br>
直接将输入拼接成一整个字符串去解析，这就很容易导致SSTI漏洞。有的时候这样使用模板是为了方便特权用户，但是一旦这种方式被攻击者知道就可能会发起精心设计的攻击。

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%9E%84%E9%80%A0SSTI%E6%94%BB%E5%87%BB%EF%BC%9F"></a>如何构造SSTI攻击？

<a class="reference-link" name="%E6%8E%A2%E6%B5%8B"></a>**探测**

burp介绍，最简单的方法就是fuzz测试，通过像这样的使用模糊模板语句<br>`$`{``{`&lt;%[%'"`}``}`%\`<br>
如果服务器返回了相关的异常语句则说明服务器可能在解析模板语法，然而ssti漏洞会出现在两个不同的上下文中，并且需要使用各自的检测方法来进一步检测ssti漏洞

**<a class="reference-link" name="%E7%BA%AF%E6%96%87%E5%AD%97%E4%B8%8A%E4%B8%8B%E6%96%87"></a>纯文字上下文**

有的模板引擎会将模板语句渲染成HTML，例如Freemarker<br>`render('Hello' + username) --&gt; Hello Apce`<br>
因为会渲染成HTML，所以这还可以导致XSS漏洞。但是模板引擎会自动执行数学运算，的，所以如果我们输入一个运算，例如<br>`http://vulnerable-website.com/?username=$`{`7*7`}``<br>
如果模板引擎最后返回Hello 49则说明存在SSTI漏洞。而且不同的模板引擎的数学运算的语法有些不同，还需要查阅相关资料的。

**<a class="reference-link" name="%E4%BB%A3%E7%A0%81%E4%B8%8A%E4%B8%8B%E6%96%87"></a>代码上下文**

我们关注这样一段代码，同样是用来生成邮件的

```
greeting = getQueryParameter('greeting')
engine.render("Hello `{``{`"+greeting+"`}``}`", data)
```

上面代码通过获取静态查询参数greeting的值然后再填充到模板语句中，但是就像sql注入一样，如果我们提前将双花括号闭合，然后就可以注入自定义的语句了。



## 识别

当我们探测到潜在的SSTI漏洞后，我们下一步就是要识别使用的是哪一款模板引擎了。比较常见的做法可以是故意触发报错即可知道，例如输入无效的表达式&lt;%=foobar%&gt;，然后得到这样的报错信息

```
(erb):1:in `&lt;main&gt;': undefined local variable or method `foobar' for main:Object (NameError)
from /usr/lib/ruby/2.5.0/erb.rb:876:in `eval'
from /usr/lib/ruby/2.5.0/erb.rb:876:in `result'
from -e:4:in `&lt;main&gt;'

```

从上面得知使用的是基于Ruby的ERB引擎。但是如果这种方法不生效怎么办，我们可以通过执行不同语法的数学运算观察结果，burp直接给了一张很详细的图

[![](https://p2.ssl.qhimg.com/t0150b4c4ba453e7459.png)](https://p2.ssl.qhimg.com/t0150b4c4ba453e7459.png)

有的时候相同的payload可能会有两种响应，比如`{``{`7*’7’`}``}`在Twig中会的到49，而在Jinja2中会得到7777777。



## 利用

在我们确定目标使用的模板引擎后，我们想要成功发动SSTI攻击往往需要以下步骤
- 阅读模板引擎语法、安全文档、已知利用文章
- 探索环境
- 构造自定义利用
### <a class="reference-link" name="%E9%98%85%E8%AF%BB"></a>阅读

**<a class="reference-link" name="%E5%AD%A6%E4%B9%A0%E5%9F%BA%E7%A1%80%E6%A8%A1%E6%9D%BF%E8%AF%AD%E6%B3%95"></a>学习基础模板语法**

学习基本语法、关键函数和变量处理是非常关键的，连这些都不会，就也没办法编写相应的payload了。比如如果我们知道了使用的是基于python的Mako模板引擎，我们可以编写这样的payload。

```
&lt;%
import os
x=os.popen('id').read()
%&gt;
$`{`x`}`
```

我们可以看到就是利用最基础的语法写的，所以这个环节也是很关键的。这段代码可以在非沙箱环境中实现远程代码执行，包括读取、编辑或删除任意文件。下面我们通过两道靶场来深入理解

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%9F%BA%E7%A1%80SSTI"></a>配套靶场1：基础SSTI**

题目告诉我们模板引擎是ERB，然后我们去查一下ERB的文档发现语法为

[![](https://p3.ssl.qhimg.com/t0102db199499e05ae0.png)](https://p3.ssl.qhimg.com/t0102db199499e05ae0.png)

然后我们将表达式模板语句写到message参数中，使用常用的数学表达式来进行检测

[![](https://p1.ssl.qhimg.com/t017ea0557c0efa5f11.png)](https://p1.ssl.qhimg.com/t017ea0557c0efa5f11.png)

说明模板引擎会去执行表达式，然后通过搜索引擎查到ruby语言执行操作系统命令的函数是system()，于是我们就可以在模板表达式中执行操作系统命令了

[![](https://p5.ssl.qhimg.com/t01d370629539314d83.png)](https://p5.ssl.qhimg.com/t01d370629539314d83.png)

我们看到模板引擎成功地执行了ls命令，看到了我们要删除的文件，于是执行删除命令即可

[![](https://p4.ssl.qhimg.com/t0187808780012518bb.png)](https://p4.ssl.qhimg.com/t0187808780012518bb.png)

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%9F%BA%E7%A1%80SSTI(%E4%B8%8A%E4%B8%8B%E6%96%87%E4%B8%BA%E4%BB%A3%E7%A0%81)"></a>配套靶场2：基础SSTI(上下文为代码)**

首先我们登录用户，然后在用户设置里发现了一个修改显示的名称的功能，于是我们搜索了一下Tornado模板引擎的语法，然后构造如下payload

[![](https://p4.ssl.qhimg.com/t01b67d76640ae0baa8.png)](https://p4.ssl.qhimg.com/t01b67d76640ae0baa8.png)

然后我们随便发表一个评论，看一下显示的名称有没有变化

[![](https://p2.ssl.qhimg.com/t01c0839214817ffa5e.png)](https://p2.ssl.qhimg.com/t01c0839214817ffa5e.png)

说明这里存在ssti漏洞，然后就可以用类似的语法删除指定文件了

[![](https://p1.ssl.qhimg.com/t01c15af931c1c76204.png)](https://p1.ssl.qhimg.com/t01c15af931c1c76204.png)

然后在评论区刷新以后就会执行payload了

[![](https://p1.ssl.qhimg.com/t01b654cd775aecd47a.png)](https://p1.ssl.qhimg.com/t01b654cd775aecd47a.png)

**<a class="reference-link" name="%E4%BA%86%E8%A7%A3%E5%AE%89%E5%85%A8%E6%96%87%E6%A1%A3"></a>了解安全文档**

有时候官方文档除了会提供模板引擎的基础语法外，还会设置很多警示项以帮助开发者提高系统安全性，但是往往这些警示项也会为攻击者提供思路。例如ERB引擎的安全文档指出可以列出所有目录，然后按如下方式读取任意文件

```
&lt;%= Dir.entries('/') %&gt;
&lt;%= File.open('/example/arbitrary-file').read %&gt;
```

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E6%96%87%E6%A1%A3%E5%8F%91%E5%8A%A8SSTI%E6%94%BB%E5%87%BB"></a>配套靶场：利用文档发动SSTI攻击**

首先因为题目中没有告诉我们这是哪一款模板引擎，所以我们要让它们使用的模板语句故意报错，从报错信息中我们一般可以知道使用的是哪种模板引擎，在编辑模板的$`{``}`模板表达式中随便输入些什么，就会触发报错

[![](https://p0.ssl.qhimg.com/t011cbdefa093c5dc16.png)](https://p0.ssl.qhimg.com/t011cbdefa093c5dc16.png)

然后我们就可以对症下药了，我们需要去查阅一下相关的文档，看看有没有相关警示项，我们直接去搜freemarker ssti，找到一个利用内置函数执行os命令，payload模板如下<br>`&lt;#assign ex="freemarker.template.utility.Execute"?new()&gt; $`{`ex("[payload]")`}``<br>
于是我们在编辑模板的地方将payload写入模板表达式

[![](https://p4.ssl.qhimg.com/t0158518b98bd2e0d0c.png)](https://p4.ssl.qhimg.com/t0158518b98bd2e0d0c.png)

这样当模板引擎执行表达式的时候就会执行删除命令了

[![](https://p3.ssl.qhimg.com/t0186a89bf827beb0a0.png)](https://p3.ssl.qhimg.com/t0186a89bf827beb0a0.png)

**<a class="reference-link" name="%E6%9F%A5%E6%89%BE%E5%B7%B2%E7%9F%A5%E5%88%A9%E7%94%A8%E6%96%87%E7%AB%A0"></a>查找已知利用文章**

顾名思义，就是当知道使用的是哪种模板引擎后可以利用搜索引擎查找是否有前人总结的漏洞利用方法，这样可以节约很多查阅文档的时间

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E5%B7%B2%E7%9F%A5%E5%88%A9%E7%94%A8%E6%96%87%E7%AB%A0%E5%8F%91%E5%8A%A8%E6%9C%AA%E7%9F%A5%E8%AF%AD%E8%A8%80%E7%9A%84SSTI%E6%94%BB%E5%87%BB"></a>配套靶场：利用已知利用文章发动未知语言的SSTI攻击**

因为不知道使用的是哪一款模板引擎，所以我们需要输入各种版本的错误模板表达式以触发报错

[![](https://p5.ssl.qhimg.com/t017361dd0292d26851.png)](https://p5.ssl.qhimg.com/t017361dd0292d26851.png)

然后我们就利用搜索引擎查找一下有没有相关的现成的利用方式，搜到了一个知名的payload模板

```
wrtz`{``{`#with "s" as |string|`}``}`
  `{``{`#with "e"`}``}`
    `{``{`#with split as |conslist|`}``}`
      `{``{`this.pop`}``}`
      `{``{`this.push (lookup string.sub "constructor")`}``}`
      `{``{`this.pop`}``}`
      `{``{`#with string.split as |codelist|`}``}`
        `{``{`this.pop`}``}`
        `{``{`this.push "return require('child_process').exec('[payload]');"`}``}`
        `{``{`this.pop`}``}`
        `{``{`#each conslist`}``}`
          `{``{`#with (string.sub.apply 0 codelist)`}``}`
            `{``{`this`}``}`
          `{``{`/with`}``}`
        `{``{`/each`}``}`
      `{``{`/with`}``}`
    `{``{`/with`}``}`
  `{``{`/with`}``}`
`{``{`/with`}``}`
```

因为是通过传入GET参数传入payload，所以我们需要将整个payload做一个URL编码

[![](https://p5.ssl.qhimg.com/t01ec575d3d76e3182b.png)](https://p5.ssl.qhimg.com/t01ec575d3d76e3182b.png)

<a class="reference-link" name="%E6%8E%A2%E7%B4%A2"></a>**探索**

如果我们通过查找资料已经找不到有效的攻击手段了怎么办，下一步就是探索环境并尝试发现有权访问的所有对象。很多模板引擎存在如”self”和”environment”之类的对象，该类对象包含该类模板引擎支持的所有对象、方法和属性，利用这些因素可以生成很多意想不到的对象。例如基于Java的模板语言可以使用以下注入列出环境中的所有变量<br>`$`{`T(java.lang.System).getenv()`}``<br>
Burp Pro中的Intruder已经内置了用于暴力破解变量名的词表。

**<a class="reference-link" name="%E5%BC%80%E5%8F%91%E8%80%85%E6%8F%90%E4%BE%9B%E7%9A%84%E5%AF%B9%E8%B1%A1"></a>开发者提供的对象**

有时候网站会包含一些内置的和开发人员定制的对象，这些对象往往可能会暴露一些敏感的方法，还是要借助文档或文章的帮助。并且SSTI也不是总能远程执行命令的，有时候可以进行目录遍历等同样高风险的攻击获取敏感数据的访问权限。

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E9%80%9A%E8%BF%87%E5%BC%80%E5%8F%91%E8%80%85%E6%8F%90%E4%BE%9B%E7%9A%84%E5%AF%B9%E8%B1%A1%E5%88%A9%E7%94%A8SSTI%E8%A7%A6%E5%8F%91%E4%BF%A1%E6%81%AF%E6%B3%84%E6%BC%8F"></a>配套靶场：通过开发者提供的对象利用SSTI触发信息泄漏**

先用fuzz字符串($`{``{`&lt;%[%’”`}``}`%)触发报错判断模板引擎的类型

[![](https://p0.ssl.qhimg.com/t01e6b5e8a86f9e6ef1.png)](https://p0.ssl.qhimg.com/t01e6b5e8a86f9e6ef1.png)

经过查阅文档得知，有一个内置的模板标签`{`% debug %`}`，可以显示调试信息

[![](https://p4.ssl.qhimg.com/t0156cf517cffb60c4b.png)](https://p4.ssl.qhimg.com/t0156cf517cffb60c4b.png)

然后又查阅文档得知，`{``{`settings.SECRET_KEY`}``}`表达式可以查看指定的环境变量

[![](https://p4.ssl.qhimg.com/t012b9afad228d1dfe0.png)](https://p4.ssl.qhimg.com/t012b9afad228d1dfe0.png)

我们就顺利地知道了指定的环境变量值

[![](https://p2.ssl.qhimg.com/t0173cf1571cceb7337.png)](https://p2.ssl.qhimg.com/t0173cf1571cceb7337.png)

**<a class="reference-link" name="%E6%9E%84%E9%80%A0%E8%87%AA%E5%AE%9A%E4%B9%89%E5%88%A9%E7%94%A8"></a>构造自定义利用**

有时候通过现有的公开的利用方式无法触发ssti漏洞，比如模板引擎防止在沙箱环境中，此时需要审计每个功能点的可利用性来发现隐藏的漏洞点

**<a class="reference-link" name="%E4%BD%BF%E7%94%A8%E5%AF%B9%E8%B1%A1%E9%93%BE%E6%9E%84%E9%80%A0%E8%87%AA%E5%AE%9A%E4%B9%89%E5%88%A9%E7%94%A8"></a>使用对象链构造自定义利用**

通过查阅文档，观察不同对象返回的对象和可用的方法可以构造一条对象引用链，从而发现不易发现的ssti漏洞点，就像反序列化的工具链一样。例如，在基于Java的模板引擎Velocity中，可以访问名为class的ClassTool对象。研究文档表明可以链接class.inspect()方法和class.type属性来获取对任意对象的引用。如下所示<br>`$class.inspect("java.lang.Runtime").type.getRuntime().exec("bad-stuff-here")`

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%9C%A8%E6%B2%99%E7%AE%B1%E7%8E%AF%E5%A2%83%E4%B8%AD%E5%8F%91%E5%8A%A8SSTI%E6%94%BB%E5%87%BB"></a>配套靶场：在沙箱环境中发动SSTI攻击**

首先我们通过查阅资料知道对象类下面有一个getClass()方法，该方法会返回当前对象的内存管理(runtime)类，然后一路查找下去，可以构造如下利用链

[![](https://p3.ssl.qhimg.com/t0199106296aefb8b61.png)](https://p3.ssl.qhimg.com/t0199106296aefb8b61.png)

然后我们转一下ASCII就能得到要提交的文件内容了

[![](https://p4.ssl.qhimg.com/t01608d7e7745bba4f2.png)](https://p4.ssl.qhimg.com/t01608d7e7745bba4f2.png)

**<a class="reference-link" name="%E4%BD%BF%E7%94%A8%E5%BC%80%E5%8F%91%E8%80%85%E6%8F%90%E4%BE%9B%E7%9A%84%E5%AF%B9%E8%B1%A1%E6%9E%84%E9%80%A0%E5%AF%B9%E8%B1%A1%E9%93%BE"></a>使用开发者提供的对象构造对象链**

有时候即使有很多文档，但是没有有效的对象可以用来构造对象链，如果开发者针对当前目标创建了特定的对象，则可以通过不断观察它们并尝试构造漏洞。下面我们通过一道靶场来深入理解。

**<a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E8%87%AA%E5%AE%9A%E4%B9%89%E5%88%A9%E7%94%A8%E5%8F%91%E5%8A%A8SSTI%E6%94%BB%E5%87%BB"></a>配套靶场：自定义利用发动SSTI攻击**

我们看到用户页面有一个功能点使用模板引擎，发现开发者提供的是user对象，现在需要基于user对象来构造漏洞，先看一下上传头像功能点，上传一个无效的图片文件触发报错

[![](https://p0.ssl.qhimg.com/t0156f57886690f51c7.png)](https://p0.ssl.qhimg.com/t0156f57886690f51c7.png)

从报错信息来看，我们知道有两个文件，一个是/home/carlos/User.php，一个是/home/carlos/avatar_upload.php，前者先不管，后面可能有用，后者中包含User对象的setAvatar方法，这个方法需要两个参数，一个是文件路径，一个是类型，我们知道修改显示名称功能点处有对User对象的控制权，所以我们选择利用这个控制权执行setAvatar方法，将我们想读取的文件读取出来，于是进行如下操作

[![](https://p1.ssl.qhimg.com/t010b7c2e1f19f847f8.png)](https://p1.ssl.qhimg.com/t010b7c2e1f19f847f8.png)

[![](https://p5.ssl.qhimg.com/t01e31d4fcd2f64cfbb.png)](https://p5.ssl.qhimg.com/t01e31d4fcd2f64cfbb.png)

执行完setAvatar方法后需要刷新一下页面才能在第二个包的响应中看到我们要读取的文件，下面我们用类似的方法读取一下/home/carlos/User.php文件，看看里面有没有可利用的东西

[![](https://p2.ssl.qhimg.com/t010cf816497bfee620.png)](https://p2.ssl.qhimg.com/t010cf816497bfee620.png)

我们找到了这个函数，这个函数可以删除当前设置的头像文件，那么如果我们把头像文件设置为目标文件，则可以利用这个函数删除它。

[![](https://p2.ssl.qhimg.com/t0102f4f0c84d1baa9e.png)](https://p2.ssl.qhimg.com/t0102f4f0c84d1baa9e.png)



## 如何缓解SSTI攻击？

避免引入SSTI漏洞的最简单方法之一是始终使用“无逻辑”模板引擎，如Mustache，除非绝对必要。尽可能将逻辑层与渲染层分离，可以大大减少面临最危险的基于模板的攻击的风险。另一种措施是仅在沙盒环境中执行用户的代码，在该环境中，潜在危险的模块和功能已被完全删除。但是沙箱也会存在被绕过的风险。最后，另一种补充方法是通过在封闭的Docker容器中部署模板环境来部署沙箱。



## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之高级漏洞篇 – 服务器端模板注入(SSTI)专题的全部内容啦，本专题主要讲了SSTI的形成原理，以及包括探测、识别、利用(阅读、探索、构建自定义攻击)多个步骤讲解如何发现并利用SSTI漏洞，最后介绍了如何缓解这类攻击等，感兴趣的同学可以在评论区进行讨论，嘻嘻嘻。
