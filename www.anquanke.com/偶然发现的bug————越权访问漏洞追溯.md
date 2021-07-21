> 原文链接: https://www.anquanke.com//post/id/158149 


# 偶然发现的bug————越权访问漏洞追溯


                                阅读量   
                                **162692**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01d4b25e185e9f5c79.jpg)](https://p2.ssl.qhimg.com/t01d4b25e185e9f5c79.jpg)

> 因为经常需要做一些小的demo，所以掌握一个快速开发框架是十分重要的，我比较习惯使用yii2，而就在写demo的过程中，最后使用脚本自动化测试的时候，偶然间发现了不登陆竟然也可以执行逻辑代码，这也就是这篇文章的起源。



## 简单介绍

大家都知道，框架基本都是基于`mvc`框架的，`yii2`也不例外，每个框架都有自己封装好的访问控制代码组件，很多人（也包括我自己）在使用的时候，是不会去具体查看究竟是怎么实现的，这也就可能会导致版本更替，或者版本更新了以后，还按照默认写法来做访问控制，最终导致了越权漏洞的产生。<br>
在yii中，所有的逻辑代码都写在控制器中，而每一个操作又叫动作，所以在yii中，一个控制器的大概结构就是：

```
class SiteController extends Controller
`{`
    public function actionIndex()
    `{`
        return $this-&gt;render('index');
    `}`

    public function actionLogin()
    `{`
        .........
        return $this-&gt;render('index');
    `}`
`}`
```



## csrf的防御

> 为什么要先讲讲csrf的防御呢？因为我了解访问控制，就是从这里开始的。前面的几篇文章分析的cms，也有很多都没有实现csrf校验，也算是提供一个比较好的实现方法。

在所有使用yii开发的系统，默认都是开启了`csrf token`防御验证的，而具体实现这个校验的途径，就是使用了一个叫做`beforeacton`的特殊动作，这个动作会在该控制器的任意动作执行之前执行。<br>
我们具体跟进看一下所有控制器的父类里面的实现：<br>[![](https://p1.ssl.qhimg.com/t01bd59e2968fdd3029.png)](https://p1.ssl.qhimg.com/t01bd59e2968fdd3029.png)可以看到，这里`csrf`有两个关键的点：

```
$this-&gt;enableCsrfValidation
!Yii::$app-&gt;getRequest()-&gt;validateCsrfToken()
```

上面的是配置，开发者是可以在控制器当中关闭配置来关闭`csrf`验证的，下面则是验证`csrf token`的函数，我们继续跟进一下：<br>[![](https://p1.ssl.qhimg.com/t016c1fa86373392258.png)](https://p1.ssl.qhimg.com/t016c1fa86373392258.png)通过简单的查看，可以看到具体的实现代码，这样就可以实现对开发者和访问者都透明化的处理，既不会干扰开发者写正常的逻辑代码，也不会影响访问者的操作，可以说是比较经典的实现`csrf`校验的方法。



## 访问控制的实现

在`yii2.0.3`版本之前，如果控制器的所有动作都是需要登陆的，那就可以在`beforeaction`中直接写上控制代码，例如：<br>[![](https://p3.ssl.qhimg.com/t012d4e82180a81e88a.png)](https://p3.ssl.qhimg.com/t012d4e82180a81e88a.png)但是就是这样的默认写法，在前几天测试的时候却出现了问题。

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E6%B5%8B%E8%AF%95%EF%BC%9A"></a>简单测试

我们简单写一个`demo`测试一下，其中的`action`和`beforeaction`如下图：<br>[![](https://p4.ssl.qhimg.com/t01463555b66e717467.png)](https://p4.ssl.qhimg.com/t01463555b66e717467.png)然后尝试访问一下site/test这个动作，按理说这个时候是不会显示123的，应该渲染index所对应的模板文件<br>[![](https://p5.ssl.qhimg.com/t0119d8d1f4baaf7fcd.png)](https://p5.ssl.qhimg.com/t0119d8d1f4baaf7fcd.png)但是实际情况确实仍旧会打印出来123，这就说明test这个动作还是执行了，越权漏洞也就产生了，如果控制器内部有一些危险的动作，加上这个越权漏洞危害还是比较巨大的。

### <a class="reference-link" name="%E8%B5%84%E6%96%99%E6%9F%A5%E6%89%BE"></a>资料查找

经过在github上的搜索，发现这个问题在`issue`中是有人提到过的，并且官方给出了解决方案。<br>[![](https://p3.ssl.qhimg.com/t0122319886d37bdb78.png)](https://p3.ssl.qhimg.com/t0122319886d37bdb78.png)

### <a class="reference-link" name="%E5%AF%B9%E6%AF%94%E5%88%86%E6%9E%90"></a>对比分析

可以看到，解决方案是在`redirect`后面紧接上执行`send`函数，那我们就来看一下现在这两个函数：<br>[![](https://p4.ssl.qhimg.com/t01d79dfd9e7854e4f0.png)](https://p4.ssl.qhimg.com/t01d79dfd9e7854e4f0.png)<br>[![](https://p5.ssl.qhimg.com/t019f076c757420050e.png)](https://p5.ssl.qhimg.com/t019f076c757420050e.png)<br>
根据大概的函数名，可以看出来`redirect`函数只是向浏览器发送了一个302的响应码，这其实在安全中就和只做了前端验证是一样的操作，所以是非常危险的，那我们继续追踪一下`send`函数，他又是怎么弥补这个问题的呢？<br>[![](https://p5.ssl.qhimg.com/t015287384f76c6a20b.png)](https://p5.ssl.qhimg.com/t015287384f76c6a20b.png)send函数实现了强制发送302跳转的功能，并且在最后关闭了当前的连接，这样就能确保越权不在产生，其实总结一下：

```
redirect =&gt; echo "&lt;script&gt;window.location.href=xxx;&lt;/script&gt;";
redirect+send =&gt; echo "&lt;script&gt;window.location.href=xxx;&lt;/script&gt;";die();
```

就大概相当于这样，所以道理是非常浅显易懂的，但是由于封装了很多层，所以可能不是很好看出来。



## 后记

所以不论是在开发或者是在做安全的过程中，重视开发文档都是非常重要的，严格的实现协议，严格的按照开发文档实现逻辑，会减少很多漏洞的产生。
