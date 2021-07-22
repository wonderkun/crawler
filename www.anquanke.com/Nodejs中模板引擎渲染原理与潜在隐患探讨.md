> 原文链接: https://www.anquanke.com//post/id/229301 


# Nodejs中模板引擎渲染原理与潜在隐患探讨


                                阅读量   
                                **205785**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01e7bf7e281cfecae9.png)](https://p0.ssl.qhimg.com/t01e7bf7e281cfecae9.png)



## 一、背景

此前，无恒实验室成员在对nodejs原型链污染漏洞进行梳理时，发现原型链污染漏洞可结合模板引擎的渲染达到远程命令执行的效果。为什么原型链污染能结合模板引擎能达到这样的效果？模板引擎究竟是如何工作的？除了原型链污染，还有其他方式也能达到同样的效果吗？带着这样的疑问，无恒实验室成员决定对nodejs模板引擎的内在机制进行一些探索。



## 二、Nodejs模板引擎现状

目前JavaScript生态圈里面的模板引擎非常之多，各引擎的实现原理及特性都不尽相同，很难找到一款功能丰富、书写简单、前后端共用的模板引擎，因此有开发者设立了一个根据不同需求挑选不同引擎的网站garann.github.io/template-chooser。

[![](https://p3.ssl.qhimg.com/t014de87a495e9f1132.png)](https://p3.ssl.qhimg.com/t014de87a495e9f1132.png)

根据npm的官方数据，目前较受欢迎的模板引擎下载量分别如图2所示。无恒实验室根据已有的服务端引擎框架，挑选了目前下载量较大，开发者常用的几种模板引擎进行分析，发现模板引擎的渲染原理基本上都差不多，只是在一些细节的处理方式不太一致。

[![](https://p3.ssl.qhimg.com/t01214a2e07b7260a9f.png)](https://p3.ssl.qhimg.com/t01214a2e07b7260a9f.png)



## 三、引擎使用方式

大多数模板渲染引擎在工作时基本都对外提供了一个render函数，这个函数一般至少需要两个参数，一个是渲染的模板template，一般都为字符串，另一个是要被渲染进模板的数据data，以object（即键值对）的形式传入。render函数一般都具有以下的形式：

[![](https://p5.ssl.qhimg.com/t012ff829a23820a2a0.png)](https://p5.ssl.qhimg.com/t012ff829a23820a2a0.png)

以下面的ejs渲染代码为例，“./views/index.ejs”为模板文件的位置，`{`message: ‘test’`}`为要渲染进模板中的数据：

[![](https://p3.ssl.qhimg.com/t01719935b827a41fef.png)](https://p3.ssl.qhimg.com/t01719935b827a41fef.png)

其中，“./views/test.ejs”文件内容如下：

[![](https://p1.ssl.qhimg.com/t017d20356eff84394a.png)](https://p1.ssl.qhimg.com/t017d20356eff84394a.png)

渲染结果如下，将message对应的值test渲染进模板中。

[![](https://p3.ssl.qhimg.com/t016c1bfdf95c963cdd.png)](https://p3.ssl.qhimg.com/t016c1bfdf95c963cdd.png)

在render函数中，除了这两个参数之外，多数模板引擎还提供了可控制渲染特性的参数options，用来对模板对渲染特性进行控制，比如是否开启调试功能，是否开启缓存机制，是否打印报错信息，以ejs为例， 可通过设置compileDebug来开启调试语句。

[![](https://p0.ssl.qhimg.com/t013544f35ae7f6b1a5.png)](https://p0.ssl.qhimg.com/t013544f35ae7f6b1a5.png)



## 四、引擎渲染机制

基本上所有模板引擎的渲染机制都包含两个步骤：

步骤一：根据模板数据进行定位与分割，根据各模板定义的特殊符号找到要被替换的数据。

步骤二：根据提供的键值对和定位的结果进行值的替换、拼接，最终得到渲染的结果。

[![](https://p2.ssl.qhimg.com/t0107bbc4ea4b09c5f5.png)](https://p2.ssl.qhimg.com/t0107bbc4ea4b09c5f5.png)

在本次的分析中，无恒实验室主要对Mustache和ejs两种引擎的渲染机制进行阐述，其他引擎的渲染过程大致相同。

**4.1 定位**

大多数渲染引擎都规定了要被替换的数据必须被某些符号所包裹，比如Mustache默认的符号是 `{``{` `}``}` ，而ejs默认的符号是&lt;%= %&gt;，因此引擎在工作时，首先要在传入的模板字符串中寻找到这些特殊符号。这一步不同引擎实现方式不同，如Mustache，Nunjucks是通过词法解析也就是采用字符扫描的方式对模板字符串进行扫描，从而定位特殊符号的位置，以如下Mustache的渲染代码为例：

[![](https://p1.ssl.qhimg.com/t012741ff0e9b7378bb.png)](https://p1.ssl.qhimg.com/t012741ff0e9b7378bb.png)

Mustache相应的定位代码如下，其中scanner负责对模板字符串进行扫描，扫描的结果为会存入多个token对象中。

[![](https://p3.ssl.qhimg.com/t01629ae8b4f10154bf.png)](https://p3.ssl.qhimg.com/t01629ae8b4f10154bf.png)

最终会对每一个扫描到的token进行分类和相应值、位置的存储，并放入到tokens中供后续的使用。

[![](https://p5.ssl.qhimg.com/t013ee0fa495184e889.png)](https://p5.ssl.qhimg.com/t013ee0fa495184e889.png)

示例模板字符串“whoareyou `{``{`title`}``}`”的扫描结果如下所示，“whoareyou ”会被标记为text类型，也就是纯文本，而”titile”会被标记为name类型，是要被替换的数据。

[![](https://p4.ssl.qhimg.com/t01f337444373c47ece.png)](https://p4.ssl.qhimg.com/t01f337444373c47ece.png)

而ejs则是直接通过正则匹配的方式，循环定位特殊符号的位置。最终模板引擎可根据特殊符号的位置找到要被替换的原始数据，以对如下的模板字符串进行定位为例：

[![](https://p5.ssl.qhimg.com/t0179f1b10e502c3a9f.png)](https://p5.ssl.qhimg.com/t0179f1b10e502c3a9f.png)

ejs会调用parsteTemplateText函数进行定位，其中this.templateText为原始的模板字符串，this.regex为指定的特殊符号（也就是ejs指定的’&lt;%’、’%&gt;’等），接下来则会通过while循环不断匹配将原始模板字符串分割。

[![](https://p4.ssl.qhimg.com/t016d74208885a3a70f.png)](https://p4.ssl.qhimg.com/t016d74208885a3a70f.png)

最终分割示例模板字符串的结果如下所示，可以看到要被替换的数据message已经被定位出来了。

[![](https://p0.ssl.qhimg.com/t01ee10bb16b38d2493.png)](https://p0.ssl.qhimg.com/t01ee10bb16b38d2493.png)

**4.2 替换**

在定位到要被替换的原始数据后，模板引擎则开始根据输入对原始数据进行替换操作。这一步不同引擎的替换方式也不一样。Mustache（包括Handlebars）的替换方式非常简单粗暴，就是直接替换，代码如下所示：

[![](https://p2.ssl.qhimg.com/t01f2703cf404896fbc.png)](https://p2.ssl.qhimg.com/t01f2703cf404896fbc.png)

如上所示，如果检测到token为name类型，也就是要被替换的类型，则调用escapedValue函数，该函数中会调用lookup，根据token找到对应的值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fc5890f1d08345cd.png)

context.lookup最终会寻找到对应的title的值，也就是joe。

[![](https://p0.ssl.qhimg.com/t017dcbeadcb7b7e326.png)](https://p0.ssl.qhimg.com/t017dcbeadcb7b7e326.png)

Pug, Nunjucks, ejs等引擎的替换过程就略显麻烦，ejs的render函数中，会先调用handleCache函数。

[![](https://p2.ssl.qhimg.com/t01114ac3a47ec7ade7.png)](https://p2.ssl.qhimg.com/t01114ac3a47ec7ade7.png)

把如下的代码拎出来，可以看到handleCache(opts, template)的结果是一个匿名函数

[![](https://p5.ssl.qhimg.com/t01105f2d009bd363e4.png)](https://p5.ssl.qhimg.com/t01105f2d009bd363e4.png)

而result就是最终的渲染结果，这也就意味着，ejs的具体渲染过程是由函数进行控制的，最终会等价于：

[![](https://p5.ssl.qhimg.com/t01fdfa964b2a5942d0.png)](https://p5.ssl.qhimg.com/t01fdfa964b2a5942d0.png)

而在handleCache函数中，这个匿名函数是经过compile编译而来的。

[![](https://p2.ssl.qhimg.com/t019d8c86e5a7ff8a51.png)](https://p2.ssl.qhimg.com/t019d8c86e5a7ff8a51.png)

跟进compile函数中，可以看到最终调用了Function函数构造器动态构造了一个匿名函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01915c0bbe6b96797d.png)

以上面的ejs示例代码为例，渲染引擎最终构造的匿名函数如下所示，通过__append得到最终要渲染的模板数据，这里同样会采用escapeFn防止xss，可以看到ejs的处理过程，实际上也是根据定位分割的结果进行处理拼接的过程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0148fb023f735df3db.png)



## 五、ejs模板引擎远程代码执行漏洞(CVE-2020-35772)

从上面的分析可以看到，ejs的渲染，是通过 **“动态生成函数代码 -&gt; 生成匿名函数 -&gt; 调用匿名函数”** 的方式去实现的（实际上Nunjucks, pug等许多引擎都是这么实现的），而这种方式是相当危险的，一旦动态生成的函数代码中存在用户可控的部分，恶意用户就可以在匿名函数中插入恶意代码并且会被渲染引擎所执行，最终导致远程代码执行漏洞。之前GYCTF2020 Ez_Express的题就是利用了ejs的这种特性。

其利用原理如下，ejs在渲染时会获取渲染选项的某些值拼接进函数代码中，其中就包括动态拼接outputFunctionName这个选项的值进函数代码中，但是ejs的作者从一开始就禁止了用户对渲染选项中outputFunctionName进行操控，同样也包括其他的选项。既然无法从正面进行操控，可以利用javascript的原型链污染，往Object中注入outputFunctionName属性进而操控。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014f6e68aa09d3820e.png)

**5.1 渲染选项的污染**

能不能不通过原型链污染的方式注入恶意代码？

来看看ejs渲染的入口函数render，其接受三个参数，第一个是template，为模板字符串，第二个为data，一般会是用户可控的数据，第三个为渲染选项opts，这个渲染选项可控制匿名函数代码的生成。

[![](https://p3.ssl.qhimg.com/t015e8743e6190b8fc1.png)](https://p3.ssl.qhimg.com/t015e8743e6190b8fc1.png)

ejs为了保持可用性，允许第二个参数（一般是用户可控参数）使用一些渲染选项，但是这些选项是有限定的，在代码中被utils.shallowCopyFromList(opts, data, _OPTS_PASSABLE_WITH_DATA)函数所限定，“_OPTS_PASSABLE_WITH_DATA”指定了可控制的范围，该范围如下：

[![](https://p5.ssl.qhimg.com/t0156db01268ad4e16b.png)](https://p5.ssl.qhimg.com/t0156db01268ad4e16b.png)

最终这些渲染选项会进入到compile函数也就是匿名函数代码生成的过程中，也就是说，若用户数据能够控制传入的data选项，那么恶意用户就能污染opts中的“delimiter”， “scope”， “context”，“debug”，“compileDebug”， “client”，“_with”，“rmWhitespace”，“strict”，“filename”， “async”。

[![](https://p2.ssl.qhimg.com/t019f3c9859ad2254d4.png)](https://p2.ssl.qhimg.com/t019f3c9859ad2254d4.png)

**5.2 匿名函数代码的生成**

那么这些可污染选项，能对匿名函数代码的生成造成什么影响呢？继续跟进渲染引擎发现，匿名函数代码在动态生成的过程中，由三部分构成，分别是prepended, this.source, append三部分，而这三个部分的代码又受到了渲染选项的影响

[![](https://p3.ssl.qhimg.com/t0180662e53ec8cc0bd.png)](https://p3.ssl.qhimg.com/t0180662e53ec8cc0bd.png)

逐步跟进匿名函数代码的生成，首先可以看到outputFunctionName, localsName, destructuredLocals这个几个渲染选项可影响prepended代码的生成，但是这些选项都不在可控的范围内。

[![](https://p1.ssl.qhimg.com/t01fed6c9347f8ded85.png)](https://p1.ssl.qhimg.com/t01fed6c9347f8ded85.png)

继续跟进函数代码的生成过程，如下所示，compileDebug是在可控范围内，filename也在可控范围内，但是filename被JSON.stringify进行转换了，无法逃逸出来，因此也无法污染函数代码。

[![](https://p2.ssl.qhimg.com/t013b48840f743ef44d.png)](https://p2.ssl.qhimg.com/t013b48840f743ef44d.png)

接下来继续跟进，可以看到在如下的代码中，compileDebug和filename都是我们可控的，并且最后filename也被直接拼接进匿名函数的代码中，因此在这里就可以通过控制filename选项注入恶意的代码。

[![](https://p1.ssl.qhimg.com/t0120c025fd8e56f35c.png)](https://p1.ssl.qhimg.com/t0120c025fd8e56f35c.png)

**5.3 恶意代码的注入**

直接编写如下的代码，看看最终生成的匿名函数的源码是怎么样的。

[![](https://p2.ssl.qhimg.com/t010084ca00aa44ca25.png)](https://p2.ssl.qhimg.com/t010084ca00aa44ca25.png)

如下所示，可以看到/etc/passwd最终被插入到一个注释的行中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01202c8b84cf795623.png)

此时对payload进行修改，加入换行符逃逸注释。

[![](https://p1.ssl.qhimg.com/t0176639ea1d2f5e85a.png)](https://p1.ssl.qhimg.com/t0176639ea1d2f5e85a.png)

得到的结果结果如下，可以看到通过换行符已经成功逃逸了注释，但是，对于这样一个函数，其正常的流程走到try的代码块时，除非出现异常，否则的话直接走到return代码就执行结束了，压根不会走到我们注入的代码。除非能触发异常继续走下去，但是看try块里面的代码，基本没有可触发异常的逻辑。

[![](https://p2.ssl.qhimg.com/t01a34cd9d812bda059.png)](https://p2.ssl.qhimg.com/t01a34cd9d812bda059.png)

**5.4 finally逃逸try catch限制**

在常见的编程语言中，try catch实际上还可以再接一个finally，无论最终try cath如何，都会走到finally中的代码块，但是return的情况下，还能执行finally吗，paylaod如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01997a5cc3dae03b19.png)

来看看最终生成的代码:

[![](https://p3.ssl.qhimg.com/t0142c9623b227bdece.png)](https://p3.ssl.qhimg.com/t0142c9623b227bdece.png)

试了一下，还是能走到finally代码块的，最终注入的代码被引擎所执行

[![](https://p1.ssl.qhimg.com/t015f52609eac85dee5.png)](https://p1.ssl.qhimg.com/t015f52609eac85dee5.png)

实际上，采用动态生成函数进行渲染的引擎中，除了ejs，还有pug，nunjuck等，那么其他引擎是否也存在同样的问题？无恒实验室也对其他的模板引擎进行了分析，发现其他引擎虽然也采用了这种方式进行渲染，但是较好的控制住了渲染选项对函数代码的影响。

**5.5 影响版本**

在实际的测试过程中，发现在较老的ejs版本上，并不存在该漏洞，影响版本范围为:<br>
2.7.2（包括2.7.2）到最新版(3.1.5)。

**5.6 利用难度**

如上的漏洞实际上要求服务端的代码直接拿用户可控的json数据进行渲染，包括key和value。对于正常的服务端框架来说，框架中间件是能将传入的json数据转换为json对象的，比较少有开发会直接拿整个json数据进行渲染，但是也存在研发直接使用JSON.parse解析用户数据进行模板渲染的用法。

**5.7 临时修复方案**

发现了该漏洞之后，无恒实验室及时与ejs的作者取得联系，ejs的作者阐述这实际上属于模板引擎本身的特性，用户可控的json数据不应该被直接传入进行使用，暂无提供修复版本的计划。

无恒实验室对该问题进行披露，希望能够帮助受影响的业务避免潜在的安全风险。若有线上业务代码符合漏洞的触发条件，因目前ejs暂无修复的版本，无恒实验室提供如下的几个临时的修复方案：
- ○ 若无版本要求，建议使用不在影响范围内的版本，如2.7.1。
- ○ 若在受影响版本范围内，建议不直接获取用户的json数据进行模板渲染。
- ○ 若需要直接获取用户数据进行模板渲染，确保用户数据中不存在compileDebug和filename选项或者这些选项的值不可控。可采用如下的安全检测函数。
[![](https://p4.ssl.qhimg.com/t014339b8ad6ee2735c.png)](https://p4.ssl.qhimg.com/t014339b8ad6ee2735c.png)



## 六、结束语

开源对于软件的发展具有重大的意义，许多企业的业务中或多或少都引入了开源的第三方依赖，使企业可以更关注于业务的发展。但是在引入第三方依赖的同时，也不可避免地引入开源代码中的安全漏洞，这些安全漏洞往往能对业务造成致命的打击。随着越来越多的第三方依赖漏洞被披露，越来越多的企业也开始重视第三方依赖的安全性。

无恒实验室致力于为公司业务保驾护航，亦极为重视第三方依赖对业务安全的影响，在检测公司引入的第三方依赖安全性的同时，无恒实验室也着力于挖掘第三方依赖中未曾被披露的漏洞与安全隐患，给出靠谱修复方案与防御措施，并将持续与业界共享研究成果，协助企业业务避免遭受安全风险，亦望能与业内同行共同合作，为网络安全行业的发展做出贡献。



## 关于无恒实验室：

无恒实验室是由字节跳动资深安全研究人员组成的专业攻防研究实验室，实验室成员具备极强的实战攻防能力，研究领域覆盖渗透测试、APP安全、隐私保护、IoT安全、无线安全、漏洞挖掘等多个方向。实验室成员为字节跳动各项业务保驾护航的同时，不断钻研攻防技术与思路，发表多篇高质量论文和演讲，发现大量影响面广的0day漏洞。无恒实验室希望以最为稳妥和负责的方式降低网络安全问题对企业的影响，同时，通过实验室的技术沉淀、产品研发，致力于保障字节跳动旗下业务与产品的用户安全，让世界更加美好更加安全！

加入无恒实验室：[https://security.bytedance.com/static/lab/index.html](https://security.bytedance.com/static/lab/index.html)
