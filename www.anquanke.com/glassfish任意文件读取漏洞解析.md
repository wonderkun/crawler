> 原文链接: https://www.anquanke.com//post/id/83306 


# glassfish任意文件读取漏洞解析


                                阅读量   
                                **122070**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01400bd0aeef78d353.jpg)](https://p3.ssl.qhimg.com/t01400bd0aeef78d353.jpg)

        昨天播报转载了一篇PKAV写的有关glassfish的文章，今天360安全播报初步分析一下此漏洞。大家看完以后应该会茅舍顿开。

        这个漏洞其实就是很多年以前出现的unicode编码漏洞,早期的webSphere、tomcat都出现过这种问题,其实就unicode编码缺陷导致同一代码的多重含义,导致操作系统对代码的错误解析,一个典型的例子就是%c0%ae会被识别为./,具体可以参考[https://www.owasp.org/index.php/Canonicalization,_locale_and_Unicode#Description](https://www.owasp.org/index.php/Canonicalization,_locale_and_Unicode#Description)

        所以glassfish这个poc实际上就是../../../../../../../../../../../etc/passwd,所以关于这个漏洞基本上没什么好说的了,很老的东西了。13年作者在wooyun就发过类似漏洞,不过是绕过webSphere的,可以读取任意配置文集,下载class代码,道理其实是一样的[http://wooyun.org/bugs/wooyun-2013-047523](http://wooyun.org/bugs/wooyun-2013-047523)。通过这种方法可以读取任意文件,这里附上读取admin后台配置文件截图

[![](https://p4.ssl.qhimg.com/t01703b3f3a309461fe.png)](https://p4.ssl.qhimg.com/t01703b3f3a309461fe.png)



        并且可以下载任意代码,如图



[![](https://p2.ssl.qhimg.com/t01577ba67b793bfa34.png)](https://p2.ssl.qhimg.com/t01577ba67b793bfa34.png)



        关于利用实际上还可以变形,例如

```
http://192.168.147.148:4848/theme/META-INF/%c0.%c0./%c0.%c0./%c0.%c0./%c0.%c0./%c0.%c0./domains/domain1/config/admin-keyfile
```



[![](https://p3.ssl.qhimg.com/t01a445a336072e07f7.png)](https://p3.ssl.qhimg.com/t01a445a336072e07f7.png)



**        修复方法:**

        其实很简单,过滤unicode解码之后的字符串防止出现”.”,”/”等就可以了,不管是程序代码还是waf规则,都是这样做。其实还是云服务提供商的waf没有过滤严谨,因为waf完全有能力去解码url,然后配置waf规则做过滤。
