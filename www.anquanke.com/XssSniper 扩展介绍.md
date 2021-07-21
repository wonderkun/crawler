> 原文链接: https://www.anquanke.com//post/id/82335 


# XssSniper 扩展介绍


                                阅读量   
                                **116564**
                            
                        |
                        
                                                                                    



****

[![](https://p0.ssl.qhimg.com/t018262fecda093b701.jpg)](https://p0.ssl.qhimg.com/t018262fecda093b701.jpg)

**XssSniper 扩展介绍**

一直以来,隐式输出的DomXSS漏洞难以被传统的扫描工具发现,而XssSniper是依托于Chrome浏览器的扩展,通过动态解析可以快速准确的发现DomXSS漏洞。

此外,本扩展不仅可以发现隐式输出的XSS,还可以发现显示输出的DomXSS,反射式XSS,自动寻找JSONP的XSS,以及检测SOME漏洞(同源方法执行)。

<br>

**原理**

XSS检测原理

本扩展采用了两种方法去检测DOMXSS。

**第一种方法:FUZZ**

这种检测方法误报率非常低,只要是检测出来的一定都是都是存在漏洞的。但是代价是漏报率也比较高。 具体来说是在当前页面中创建一个隐形的iframe,在这个iframe中采用不同字符组合截断的payload去fuzz当前页面中的每个url参数,以及location.hash参数。如果payload执行,说明漏洞一定存在。

**第二种方法:监控js错误变化**

如果xss存在方式比较隐蔽,或者需要非常复杂的字符组合来截断的话,payload是无法正常执行的,然而尽管如此,payload可能会引发一些js语法异常,扩展只需要检测这些异常就可以。然后提示用户错误位置,错误内容,错误的行数,让用户手工去 因此以这种方式检测XSS,漏报少,但是代价是误报较高。

两种检测方式相互结合,取长补短。

<br>

**使用方法**

[![](https://p4.ssl.qhimg.com/t01990dc2b55a0b75f9.png)](https://p4.ssl.qhimg.com/t01990dc2b55a0b75f9.png)

打开控制面板

第一次使用的时候请手工更新一下策略,将测试目标填入列表中。tester并非是主动检测这些列表域名中的漏洞。而是在你浏览这些网站时,检测当前页面中的XSS漏洞。 所以,开启fuzz后,只需要正常浏览这些网站即可。

**第一种报警方式:payload直接执行**

如果在浏览过程中发现弹出了对话框,显示一个带有xss payload的url,如下图,说明该url可以触发XSS漏洞。

[![](https://p1.ssl.qhimg.com/t01399c9b305accfb94.png)](https://p1.ssl.qhimg.com/t01399c9b305accfb94.png)

按下F12打开console控制台,测试过的URL都会在里面显示。将刚刚对话框中显示的url+payload复制出来即可。

[![](https://p3.ssl.qhimg.com/t016f53dc380162477b.png)](https://p3.ssl.qhimg.com/t016f53dc380162477b.png)

**第二种报警方式:payload使js抛出异常**

如果在浏览页面时候右下角弹出如下告警,说明payload使js抛出了不同的异常。

[![](https://p4.ssl.qhimg.com/t01ce6f9520c9ab7631.png)](https://p4.ssl.qhimg.com/t01ce6f9520c9ab7631.png)

此时打开F12打开控制台,依照图示找到异常内容和触发异常的payload,另外还可以找到抛出异常的文件和行号,方便调试。

[![](https://p2.ssl.qhimg.com/t01e0ed00ac431c4b32.png)](https://p2.ssl.qhimg.com/t01e0ed00ac431c4b32.png)

**第三种告警:JSONP反射式XSS**

若发现如下告警,说明页面中使用的jsonp存在xss漏洞。url已经在提示中给出。

[![](https://p1.ssl.qhimg.com/t01e259892ffdc736c0.png)](https://p1.ssl.qhimg.com/t01e259892ffdc736c0.png)

**第四种告警:SOME漏洞**

当扩展发现当前页面中的参数在jsonp也出现时,就会给出以下告警,需要测试者手工确认页面参数能否影响jsonp的返回参数。

[![](https://p0.ssl.qhimg.com/t01af7f1b3caa97ad6c.png)](https://p0.ssl.qhimg.com/t01af7f1b3caa97ad6c.png)

        chrome商店地址：[https://chrome.google.com/webstore/detail/domxss-tester/pnhekakhikkhloodcedfcmfpjddcagpi?hl=zh-CN](https://chrome.google.com/webstore/detail/domxss-tester/pnhekakhikkhloodcedfcmfpjddcagpi?hl=zh-CN)
