> 原文链接: https://www.anquanke.com//post/id/221705 


# Xray爬虫如何联动到Goby


                                阅读量   
                                **242782**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t0128e803dfaf2921ca.png)](https://p0.ssl.qhimg.com/t0128e803dfaf2921ca.png)



**前言：** Xray有多香想必大家应该是知道的（上星期在做某演练的时候就用Xray扫到了不少洞）。所以，当时看见Github上有联动Xray的需求，就尝试着写了此插件。本次讲的会稍微仔(啰)细(嗦)一点，希望通过此次分享，大家也能动起手来尝试写出更多的、有趣的插件。



## 0x001 插件效果

### <a class="reference-link" name="1.1%20web%E7%88%AC%E8%99%AB"></a>1.1 web爬虫

对目标进行资产测绘后，进入IP详情页：

[![](https://p3.ssl.qhimg.com/t015428e013c4d3970d.png)](https://p3.ssl.qhimg.com/t015428e013c4d3970d.png)

或进入Web检测页：

[![](https://p5.ssl.qhimg.com/t01e4db2462197ef634.jpg)](https://p5.ssl.qhimg.com/t01e4db2462197ef634.jpg)

```
注：web检测的Xray入口目前只有开发版才有。
```

这里借用一下Corp0ra1大佬之前在社区技术分享 | Goby食用指南之红蓝对抗中用的图：

[![](https://p0.ssl.qhimg.com/t01f263beaca934a91e.png)](https://p0.ssl.qhimg.com/t01f263beaca934a91e.png)

### <a class="reference-link" name="1.2%20%E7%94%9F%E6%88%90%E6%8A%A5%E5%91%8A"></a>1.2 生成报告

如果扫到了漏洞，会生成一个类似Xray的报告(代码写的很烂…)，按照时间先后，最新扫到的洞会在最上面。

[![](https://p2.ssl.qhimg.com/t0191aa928cfd9ee9fa.gif)](https://p2.ssl.qhimg.com/t0191aa928cfd9ee9fa.gif)



## 0x02 开发流程

### <a class="reference-link" name="2.1%20%E7%A1%AE%E5%AE%9A%E9%9C%80%E8%A6%81%E7%94%A8%E5%88%B0%E7%9A%84Goby%20API"></a>2.1 确定需要用到的Goby API

首先，我们需要用户手动输入Xray的路径，因此需要设置contributes.configuration：

```
"contributes": `{`
    "configuration": `{`
      "XrayPATH": `{`
        "type": "string",
        "default": "",
        "description": "请输入Xray的路径",
        "fromDialog": true //该配置参数是否可以通过读取文件路径设置
      `}`,
      ...
      ...
    `}`
`}`
```

其次我们要在Goby探测完资产后，在IP详情页面的banner上显示出我们的插件，因此需要设置contributes.view.ipDetail.bannerTop：

```
"views": `{`
      "ipDetail": `{`
        "bannerTop": [
          `{`
            "command": "Xray_crawler",//注册命令的名称
            "title": "Xray-crawler",//在按钮中显示的文字
            "icon": "src/assets/img/Xray.ico",
            "visible": "Xray_crawler_visi" //控制自定义组件是否显示的命令，返回true显示，返回false不显示
          `}`
        ]
      `}`
 `}`
```

如果Xray扫到了漏洞，我们还需要查看报告。稍加思索发现放在更多下拉菜单相对比较合适，于是需要设置contributes.view.scanRes.moreOptions：

```
"scanRes": `{`
        "moreOptions": [
          `{`
            "command": "Xray_Report",
            "title": "Xray Report",
            "icon": "src/assets/img/Xray.ico"
          `}`
        ]
      `}`
```

到这里，我们插件的自定义的视图入口点就算基本写好了，以上这些都可以在GobyExtension中找到，而且有更多的视图入口点和更加详细的说明。

### <a class="reference-link" name="2.2%20API%E8%B0%83%E7%94%A8"></a>2.2 API调用

通过Goby.getConfiguration获取上面的插件配置项

```
let config = Goby.getConfiguration();//通过config.XrayPATH.default就可以获取到用户输入的Xray路径
```

我们在上面设置了**xray_crawler**命令，由于**xray_crawler**要触发的命令基本都是照搬的官方MSF Sploit插件代码，这里就不再叙述了，有兴趣的可以看看MSF Sploit代码。

这里着重讲讲我们设置的另一个命令——**xray_Report**，实现原理主要是用node.js的fs模块读取Xray生成的json格式的报告，再传入html页面中进行处理。

```
//extension.js
let cp = require('child_process');
const os = require('os');
const path = require('path');
const fs = require('fs');
//导入的一些node.js内置模块
function activate(content) `{`
  let identical = `{`
    "web": true,
    "http": true,
    "https": true, //只有这些协议插件才会显示，同理可以对一些端口啊什么的做过滤
  `}`;
  let config = Goby.getConfiguration();

  Goby.registerCommand('Xray_Report', function () `{`  //注册要执行的命令，也就是contributes.view.scanRes.moreOptions[0].command的值
    let json_file = path.dirname(config.XrayPATH.default) + "/Goby" //设置要读取的json报告的路径，在Xray_crawler命令中设置了会在Xray的路径下生成一个名为Goby的文件夹用来存放Xray生成的json格式的报告
    var filesList = []; //filesList 列表用来存放生成的json文件名
    var info = []; //存放json文件中的内容
    readFileList(json_file, filesList);// 百度了个读取指定路径下的文件并返回列表的函数
    filesList.forEach(function (v) `{`
      var data = fs.readFileSync(v, 'utf-8')
      if (data.charAt(data.length - 1) == ']') `{` //判断json文件的最后一个字符是不是']'
        jsondata = JSON.parse(data);//Xray正常扫完某个url，生成的json报告由[]包裹
      `}` else `{`
        jsondata = JSON.parse(data + ']');//url未扫完但是已经扫到了漏洞，咱们手动给它闭合一下
      `}`
      jsondata.forEach((v, k) =&gt; `{`
        info.push(v)
      `}`);
    `}`);
    var infoBase64 = new Buffer.from(JSON.stringify(info)).toString('base64');//因为有比较多的特殊字符，咱们base64编码一下
    if (info &amp;&amp; info.length &gt; 0) `{`
      let path = __dirname + "/xReport.html?info=" + infoBase64;//传入到html页面
      Goby.showIframeDia(path, "Xray_Report", "960", "500");
    `}` else `{`
      Goby.showInformationMessage("Xray暂未产生报告！");
    `}`
  `}`);
  Goby.registerCommand('Xray_crawler_visi', function (content) `{`
    if (identical[content.protocol]) return true;//对协议名称进行判断
    return false;
  `}`);
`}`
```

### <a class="reference-link" name="2.3%20html%E9%A1%B5%E9%9D%A2%E7%9A%84%E5%A4%84%E7%90%86"></a>2.3 html页面的处理

官方插件中使用的是 layui 框架进行开发，由于html的那些布局啊，样式啊，实在不太会，好在现在有很多框架，并且一些不是很复杂的需求可以百度，咱不求优雅，只求至少能实现需求……接下来就是处理传过来的info数据了。

首先需要处理传过来的info信息，可以直接copy官方文档提供的代码，只需要注意base64解码一下:

```
&lt;script src="assets/js/jquery.base64.js"&gt;&lt;/script&gt;
function decode(str) `{`
      var debase64 = $.base64.decode(str);
      return debase64;
    `}`
function GetIframeQueryString(name, id) `{`
      var reg = new RegExp('(^|&amp;)' + name + '=([^&amp;]*)(&amp;|$)', 'i');//正则匹配'info=xxxxx'
      var r = window.parent.document.getElementById(id).contentWindow.location.search.substr(1).match(reg);
      //r[0]:info=xxx  r[1]:""  r[2]:xxx
      if (r != null) `{`
        return decode(r[2]);//base64解码一下
      `}`
      return null;
    `}`
let results = JSON.parse(GetIframeQueryString("info", "Goby-iframe"));
```

拿到了results就可以方便的将内容输出到html页面中的表格了，接下来就是一些前端的布局和样式了，由于不太会，也说不清，就不误人子弟了! (捂脸)。<br>
在以上所以内容都完成后，就可以进行打包以及发布了~ ，由于用的官方的代码，也没引入其他模块，所以直接压缩就完事了~

### <a class="reference-link" name="2.4%20%E4%B8%80%E4%BA%9B%E6%8A%80%E5%B7%A7"></a>2.4 一些技巧

建议使用1.7.199版本的开发版Goby，此版本的信息打印的十分详细，更加方便调试:

[![](https://p3.ssl.qhimg.com/t018eed4d130fcb6b32.jpg)](https://p3.ssl.qhimg.com/t018eed4d130fcb6b32.jpg)

也可以在extension.js同级目录下新建一个test.js用来测试、打印信息，比如上文中的文件读取，然后再用node执行就可以比较方便的进行调试，省去了重启Goby这一操作。

```
//test.js
const path = require('path');
const fs = require('fs');
function readFileList(dir, filesList = []) `{`
    const files = fs.readdirSync(dir);
    files.forEach((item, index) =&gt; `{`
        if (item.indexOf('.json') != -1) `{`
            var fullPath = path.join(dir, item);
            const stat = fs.statSync(fullPath);
            if (stat.isDirectory()) `{`
                readFileList(path.join(dir, item), filesList);  //递归读取文件
            `}` else `{`
                filesList.push(fullPath);
            `}`
        `}`
    `}`);
    return filesList.reverse();
`}`
let json_file = '/Users/go0p/Tools/Xray/Goby';
var filesList = [];
var info = []
readFileList(json_file, filesList);
console.log(filesList);
filesList.forEach(function (v) `{`
    var data = fs.readFileSync(v, 'utf-8')
    if (data.charAt(data.length - 1) == ']') `{`
        jsondata = JSON.parse(data);
    `}` else `{`
        jsondata = JSON.parse(data + ']');
    `}`
    jsondata.forEach((v, k) =&gt; `{`
        info.push(v)
    `}`);
`}`);
console.log(info);
var infoBase64 = new Buffer.from(JSON.stringify(info)).toString('base64');
console.log(infoBase64);
```

```
./src
├── assets
├── extension.js
├── xReport.html
└── test.js

1 directory, 3 files

$ node test.js //进行测试，查看打印信息
```

```
1.7.199开发版下载 https://gobies.org/docs.html#Getstarted
```



## 0x03 完结撒花

在社区表哥们建议下，后面我有迭代过两次，修复了wins下报告问题并加入rad浏览器爬虫。高级版的Xray对rad进行了深度融合，使用—browser-crawler配合插件只用开一个terminal/cmd 窗口真的太香了。社区版Xray联动rad需要设置Xray路径、rad路径、rad执行参数及Xray被动代理服务器，具体操作可到扩展程序Details查看。

写文章要比开发插件难多了，开发过程中可以多看看Goby官方的开发文档，发现可复用的代码可以Copy借鉴一下，调试过程中可以多使用开发者工具下断点调试，或者直接把信息打印出来。

文章来自Goby社区成员：go0p，转载请注明出处。<br>
下载Goby内测版，请关注公众号：Gobysec<br>
下载Goby正式版，请访问官网：[http://gobies.org](http://gobies.org)

[![](https://p2.ssl.qhimg.com/t01369892ed7aa40ccf.jpg)](https://p2.ssl.qhimg.com/t01369892ed7aa40ccf.jpg)
