> 原文链接: https://www.anquanke.com//post/id/226575 


# 剖析xmlDecoder反序列化


                                阅读量   
                                **222976**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t012a95cf07a4cc9aba.png)](https://p5.ssl.qhimg.com/t012a95cf07a4cc9aba.png)



一直想写个代码审计的文章，和大腿们交流下思路，正好翻xxe的时候看到一个jdk自带的xmlDecoder反序列化，很具有代表性，就来写一下，顺带翻一下源码。

为什么选这个呢，因为ta让weblogic栽了俩跟头，其他都是手写了几个洞，被人发现了，weblogic是调用的东西存在一些问题，有苦没处说啊，下面剖析下xmlDecoder是怎么反序列化的。



## 前期准备

这次使用的是idea来调试代码，下面是用到一些快捷键：

Idea中用到的debug快捷键：

F7 进入到代码，

Alt+shift+F7 强制进入代码

Atl+F9 执行跳到下一个断点处

F8 下一步

代码中有提到invoke(class, method)方法：

拿例子说话：

methodName.invoke(owner,args)

其中owner为某个对象，methodName为需要执行的方法名称，Object[]  args执行方法参数列表。

楼主使用的jdk版本：

1.8.0_151



## 敲黑板开始了

先整一个完整的xml文件，注意箭头的地方，后面会是个小坑。

[![](https://p2.ssl.qhimg.com/t013841912c8cdc3231.png)](https://p2.ssl.qhimg.com/t013841912c8cdc3231.png)

使用java代码解析xml文件。

[![](https://p2.ssl.qhimg.com/t01de94c9966baae13f.png)](https://p2.ssl.qhimg.com/t01de94c9966baae13f.png)

重点在Object s2 = xd.readObject();这行代码，打断点跟一下源码。

Debug模式启动：

[![](https://p1.ssl.qhimg.com/t0118934adaa3b8c7a8.png)](https://p1.ssl.qhimg.com/t0118934adaa3b8c7a8.png)

进入方法，是个三目运算：

[![](https://p5.ssl.qhimg.com/t01352c68f20a4346d3.png)](https://p5.ssl.qhimg.com/t01352c68f20a4346d3.png)

进入方法：

注：从这里开始，可以进行打断点，第一次跟不对的时候，下次再debug的时间alt+f9快速跳到断点处。

[![](https://p5.ssl.qhimg.com/t0118e193765b19c80e.png)](https://p5.ssl.qhimg.com/t0118e193765b19c80e.png)

打个断点，进入方法：

[![](https://p0.ssl.qhimg.com/t01c6124ad944e40ea8.png)](https://p0.ssl.qhimg.com/t01c6124ad944e40ea8.png)

[![](https://p0.ssl.qhimg.com/t01a5781b1d1640e281.png)](https://p0.ssl.qhimg.com/t01a5781b1d1640e281.png)

SAXParserImpl中有一些配置，其中的xmlReader是前面已经设置过了，是接口对象new的实现类，我们看的是实现类，这里有idea可以自动进行跳入对应的实现类的方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d6bb3a3072da90ff.png)

父类：

注：Super：调用父类的写法，有super的类必定继承（extend）了其他类。

[![](https://p2.ssl.qhimg.com/t01054838152b88bc1b.png)](https://p2.ssl.qhimg.com/t01054838152b88bc1b.png)

进入父类：

[![](https://p2.ssl.qhimg.com/t019e617fb7e696a0a6.png)](https://p2.ssl.qhimg.com/t019e617fb7e696a0a6.png)

跟进：

[![](https://p0.ssl.qhimg.com/t0137be2fcb7c8e555c.png)](https://p0.ssl.qhimg.com/t0137be2fcb7c8e555c.png)

继续跟进，跳到XML11Configuration的parse（）方法：

[![](https://p5.ssl.qhimg.com/t01600bcfd8cd9cd612.png)](https://p5.ssl.qhimg.com/t01600bcfd8cd9cd612.png)

一些配置：

[![](https://p0.ssl.qhimg.com/t01cce49c480d018724.png)](https://p0.ssl.qhimg.com/t01cce49c480d018724.png)

F7继续跟进：会进入本类的parse方法。

[![](https://p5.ssl.qhimg.com/t0101345cbbfe6c9996.png)](https://p5.ssl.qhimg.com/t0101345cbbfe6c9996.png)

[![](https://p0.ssl.qhimg.com/t017d75e79d96466896.png)](https://p0.ssl.qhimg.com/t017d75e79d96466896.png)

进入XMLDocumentFragmentScannerImpl后，会看到有方法中进行了do`{``}`while`{``}`方法，其中的next方法是重点。

[![](https://p4.ssl.qhimg.com/t01f06ec8f4600fbec1.png)](https://p4.ssl.qhimg.com/t01f06ec8f4600fbec1.png)

跟进，跳到XMLDocumentScannerImpl的next()：

[![](https://p0.ssl.qhimg.com/t01678e6a0adf26eee8.png)](https://p0.ssl.qhimg.com/t01678e6a0adf26eee8.png)

进入next()方法：

在do`{``}`while`{``}`里循环多次。

[![](https://p1.ssl.qhimg.com/t011566ccc156491c3e.png)](https://p1.ssl.qhimg.com/t011566ccc156491c3e.png)

注：下面的显示台有变量的值，可以看到代码中变量值的变化。

[![](https://p3.ssl.qhimg.com/t0127b2f4dedcd882b7.png)](https://p3.ssl.qhimg.com/t0127b2f4dedcd882b7.png)

继续跟进：

[![](https://p4.ssl.qhimg.com/t0111a02ab093e320c2.png)](https://p4.ssl.qhimg.com/t0111a02ab093e320c2.png)

可以看到解析xml文件的时候有解析到calc字符，继续跟进。

[![](https://p3.ssl.qhimg.com/t01a037d5360ded1475.png)](https://p3.ssl.qhimg.com/t01a037d5360ded1475.png)

[![](https://p3.ssl.qhimg.com/t019b47b8e3451c2879.png)](https://p3.ssl.qhimg.com/t019b47b8e3451c2879.png)

[![](https://p1.ssl.qhimg.com/t01ec7b7d21ebf29a38.png)](https://p1.ssl.qhimg.com/t01ec7b7d21ebf29a38.png)

ProcessBuilder这个类在xml文件中有申明，然后到了invoke，成功执行命令。

这一块代码建议亲自跟一下，会跟到很底层的东西，楼主在这一块卡了好长时间。

[![](https://p1.ssl.qhimg.com/t01a0706fcb073f8b2e.png)](https://p1.ssl.qhimg.com/t01a0706fcb073f8b2e.png)

[![](https://p3.ssl.qhimg.com/t01eec1886128ee6c2e.png)](https://p3.ssl.qhimg.com/t01eec1886128ee6c2e.png)

这次是借助了idea进行了代码的跟踪，待到能手点方法跟踪代码的那天就是楼主神功大成之日！嘎嘎嘎~

记得好多开发大牛说过，想进步，多看看jdk源码，看懂ta，打遍天下无敌手！（后面一句我吹的）

代码审计的时候不一定能搭的起环境来，基本功还是很重要的，看jdk源码就是一个很好的练习的方法。

用jdk自带的洞来练习代码审计的好处就是，可以使用idea帮助寻找跳转方法，不会有跟不下去的时候，门槛会降低很多；再有cms会有很多奇奇怪怪的写法，出现了洞的话最后还是一些基本的写法，楼主建议还是从基础的洞来入手，没有那么高的复杂度。



## 编辑利用程序

写一个方法，将xml文件拼接起来，还记得开头提到的小坑么

注：楼主最喜欢这种洞了，就像网站本身就给开了个后门一样。

[![](https://p1.ssl.qhimg.com/t016a3d7fac20016fb0.png)](https://p1.ssl.qhimg.com/t016a3d7fac20016fb0.png)

Main方法调用，试试ping命令。

[![](https://p5.ssl.qhimg.com/t016cad691c1bd9a6df.png)](https://p5.ssl.qhimg.com/t016cad691c1bd9a6df.png)

[![](https://p2.ssl.qhimg.com/t012b1ef7db56813e89.png)](https://p2.ssl.qhimg.com/t012b1ef7db56813e89.png)

将方法中的代码放在jsp文件中，就可以接收请求参数了，楼主已经在用了，各位大佬可以定制下。



## 更近一步

数据不回显？
<li>dnslog外带，这里有个坑，能带的字符串长度有限制，中间不能有特殊符号，可以在命令中对数据进行加密切割，分段传输。
防御方法：对doslog进行域名加黑，在攻击者探测阶段就失败。
绕过：自建dns。
</li>
<li>在服务器开启nc监听，在目标服务器访问nc服务器的端口，进行nc通信，将信息外带出来。
防御方法：在服务器监听新开启的通信。
</li>
1. 复写父类方法，使执行有输出（有难度）。
参考以上方法和冰蝎的方法可以编写定制化一个webshell工具。



## 结尾

想想类似的洞？嘿嘿嘿~
