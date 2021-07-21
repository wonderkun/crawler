> 原文链接: https://www.anquanke.com//post/id/153402 


# seacms v6.61 审计深入思考


                                阅读量   
                                **177891**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01a296ca526259cedc.jpg)](https://p2.ssl.qhimg.com/t01a296ca526259cedc.jpg)

> 前几天跟了一下有关cve-2018-14421，seacms最新版后台getshell，发现整个漏洞利用的核心，是绕过了一个黑名单过滤，后续发现很多地方都使用了这个函数，又发现了一条可以利用的攻击链，这里简单分析一下。



## 核心过滤代码

有关cve-2018-14421的具体分析可以看我之前在安全客发的文章，[文章地址](https://www.anquanke.com/post/id/152764).<br>
其实这个cve的核心就是绕过了在`/include/main.class.php`里面的`parseif`函数，这段代码原来的作用是在渲染模板的时候，处理一些简单的if逻辑，但是过滤却没有写好，导致了只要有任何一个在模板中的变量可控，就可以导致任意代码执行。

```
foreach($iar as $v)`{`
            $iarok[] = str_ireplace(array('unlink','opendir','mysqli_','mysql_','socket_','curl_','base64_','putenv','popen(','phpinfo','pfsockopen','proc_','preg_','_GET','_POST','_COOKIE','_REQUEST','_SESSION','_SERVER','assert','eval(','file_','passthru(','exec(','system(','shell_'), '@.@', $v);
        `}`
```



## 在原来的利用场景寻找可控的模板变量

在原来的输出点，将所有的模板变量打印出来以后，可以看到所有需要渲染的模板变量。 [![](https://p1.ssl.qhimg.com/t010640f9746969aa6b.png)](https://p1.ssl.qhimg.com/t010640f9746969aa6b.png)<br>
然后就可以参照变量的输入过滤流程，来一步步分析，但是经过简单的分析，除了上个cve使用的pic变量，其余的变量都不可控，所以这个页面的利用链失败。



## 寻找新的利用点

首先全局搜索了一下调用了parseif这个函数的位置，在找有关的模板变量。<br>
进过一番查找，我们发现了`video/index.php`这个文件。<br>[![](https://p2.ssl.qhimg.com/t0147c32b39273ab663.png)](https://p2.ssl.qhimg.com/t0147c32b39273ab663.png)还是一样，先将所有的模板变量全都打印出来，方便我们查找。<br>[![](https://p3.ssl.qhimg.com/t0175f95b9b9c6f27c2.png)](https://p3.ssl.qhimg.com/t0175f95b9b9c6f27c2.png)然后就依次对每个模板变量进行溯源，但是在直接可控的变量中，并没有发现可以注入代码的地方，因此思路转向了间接注入代码<br>
最后找到了一个关键的模板变量``{`playpage:from`}``



## 变量追踪

他在`video/index.php`中是这么处理的：<br>[![](https://p4.ssl.qhimg.com/t01c84b41b2abb22948.png)](https://p4.ssl.qhimg.com/t01c84b41b2abb22948.png)由上图可以看出，这个变量间接来自于数据库中的`v_playdata`这个字段的值<br>
然后可以直接去后台添加影片的地方，具体查看这个值是如何被加入数据库的<br>[![](https://p0.ssl.qhimg.com/t0146662c92075b4600.png)](https://p0.ssl.qhimg.com/t0146662c92075b4600.png)可以看到这个变量是根据v_playfrom和v_playurl两个变量处理得来的<br>
然后我们具体去查看这两个变量具体是什么<br>[![](https://p4.ssl.qhimg.com/t01d2ba0d2bc79fceea.png)](https://p4.ssl.qhimg.com/t01d2ba0d2bc79fceea.png)发现是播放来源，这个是个多选列表，于是思路变成添加一个带有恶意代码的播放来源，然后选择这个来源，从而注入恶意代码<br>[![](https://p5.ssl.qhimg.com/t016fde4f345f9c6140.png)](https://p5.ssl.qhimg.com/t016fde4f345f9c6140.png)<br>[![](https://p0.ssl.qhimg.com/t01690a8411cecc56a9.png)](https://p0.ssl.qhimg.com/t01690a8411cecc56a9.png)<br>
来源名称为注入的代码：

```
`{`if:1)$GLOBALS['_G'.'ET'][a]($GLOBALS['_G'.'ET'][b]);die();//`}``{`end if`}`
```

其余的参数可以随便写

然后发现并没有过滤，完全可以直接注入恶意代码<br>
然后我们在添加影片的时候，选择这个来源，并且抓包<br>[![](https://p1.ssl.qhimg.com/t019a1be3556d3bdd8e.png)](https://p1.ssl.qhimg.com/t019a1be3556d3bdd8e.png)<br>
发现前端进行了过滤，v_playfrom[1]截取了部分内容，我们用payload将其补充完整

```
`{`if:1)$GLOBALS['_G'.'ET'][a]($GLOBALS['_G'.'ET'][b]);die();//`}``{`end if`}`
```



## 漏洞利用

先在管理影片页面，查看刚才添加的影片id，然后访问页面

```
seacms/video/index.php?6-0-0.html&amp;a=assert&amp;b=phpinfo();
```

（其中的6为影片id）<br>[![](https://p1.ssl.qhimg.com/t01ca1639532f09de9a.png)](https://p1.ssl.qhimg.com/t01ca1639532f09de9a.png)<br>
可以看到代码已经执行，从而完成漏洞利用



## 数据流梳理

[![](https://p4.ssl.qhimg.com/t01b41e5fba310002af.png)](https://p4.ssl.qhimg.com/t01b41e5fba310002af.png)



## 总结

感觉这种攻击利用链可能还存在，核心函数过滤不好确实会导致很多问题，这也给我们在平时开发敲响了警钟，一些复用很多的关键过滤函数必须要做好。
