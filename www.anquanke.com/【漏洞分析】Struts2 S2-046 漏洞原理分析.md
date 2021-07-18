
# 【漏洞分析】Struts2 S2-046 漏洞原理分析


                                阅读量   
                                **212193**
                            
                        |
                        
                                                                                    



**[![](./img/85776/t015e03143e49da28a1.jpg)](./img/85776/t015e03143e49da28a1.jpg)**

**传送门**

[**【重大漏洞预警】Struts 2 远程代码执行漏洞(S2-045S2-046) (含PoC)******](http://bobao.360.cn/learning/detail/3571.html)

[**【漏洞分析】Strust2 S2-046 远程代码执行漏洞两个触发点分析**](http://bobao.360.cn/learning/detail/3639.html)

**<br>**

**作者：hezi@360GearTeam**

**背景介绍**

Struts2又爆了一个等级为高危的漏洞—S2-046，仔细一看，S2-046和S2-045的漏洞触发点一样，利用方式不一样。不过也因为S2-046和S2-045触发点相同，所以之前通过升级或者打补丁方式修补S2-045漏洞的小伙伴们就不用紧张了，如果是仅针对Content-Type做策略防护的话，还需要对Content-Disposition也加一下策略。当然最好的方式还是升级到最新版。

S2-046漏洞的利用条件是在S2-045的基础上的。S2-046基本利用条件有两点：

1. Content-Type 中包含multipart/form-data

2. Content-Disposition中filename包含OGNL语句

这里解释一下Content-Disposition。Content-disposition 是 MIME 协议的扩展，当浏览器接收到请求头时，它会激活文件下载对话框，请求头中的文件名会自动填充到对应的文本框中。

S2-046有两个利用方式，一个是Content-Disposition的filename存在空字节，另一个是Content-Disposition的filename不存在空字节。其中，当Content-Disposition的filename不存在空字节并想要利用成功的话，还需要满足以下两个条件：

a.	Content-Length 的长度值需超过Struts2允许上传的最大值(2M)，如图。

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a42648543d49a21b.png)

b．数据流需要经过JakartaStreamMultiPartRequest。(需在struts.xml添加配置: &lt;constant name="struts.multipart.parser" value="jakarta-stream" /&gt;)

需要注意的是，在Struts使用Jakarta默认配置时，数据流并没有经过JakartaStreamMultiPartRequest。根据官方解释，在Struts 2.3.20以上的版本中，Struts2才提供了可选择的通过Streams实现Jakarta组件解析的方式。在Struts 2.3.20以上的版本中，通过Jakarta组件实现Multipart解析的流程可以有两种，一种是默认的Jakarta组件，一种是在struts.xml中主动配置&lt;constant name="struts.multipart.parser" value="jakarta-stream" /&gt;。而只有在struts.xml中添加了相应配置，数据流才会经过JakartaStreamMultiPartRequest。

下图分别为Struts 2.3.8和Struts 2.3.24.1的multipart部分的源码包。可以看到Struts 2.3.24.1比Struts 2.3.8新增了一个文件JakartaStreamMultiPartRequest。所以，如果构造的poc中Content-Disposition的filename不存在空字节，则它的影响版本为2.3.20以上的版本。

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01068cf13ea31af7a0.png)

<br>

**源码分析**

以下源码分析基于Struts 2.3.24.1，我们根据利用方式不同分析下这两个数据流的执行过程。

**Content-Disposition的filename存在空字节**

对上传的文件解析

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c3997faa33e2243f.png)

创建拦截器后解析header，如图：Content-Type和Content-Disposition都在此解析。

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e0562667da336973.png)

Filename从Content-Disposition获取。

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01545c8e317a0d2d8b.png)

解析到filename后，会对文件名进行检查，若Content-Disposition的filename存在空字节时，则会抛出异常。如图。

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01db196e938d202f79.png)

最后进入到触发点。

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0161822dcc1a05878f.png)

**Content-Disposition的filename不存在空字节**

这个利用方式有一个条件是Content-Length 的长度需超过Struts允许上传的最大长度，并且数据流要经过JakartaStreamMultiPartRequest，这是因为JakartaStreamMultiPartRequest和JakartaMultiPartRequest对Content-Length的异常处理方式不一样。当数据经过JakartaStreamMultiPartRequest时，判断长度溢出后，进入addFileSkippedError()，如下图。这里注意，addFileSkippedError有一个参数为itemStream.getName，会对filename进行检查，如果filename中存在空字节， 则和上一个利用方法的数据流一样，在checkFileName()就抛出异常，不会再进入到addFileSkippedError()了。

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015c49f7f9a9829e60.png)

跟进addFileSkippedError()可以看到， buildErrorMessage()抛出异常时调用了filename，这个filename就是通过Content-Disposition传递的filename。而buildErrorMessage()就是漏洞触发点，传递来的filename被解析，形成了漏洞。

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01db8fddc7da00c282.png)

而在JakartaMultiPartRequest数据流中，在判断长度后，抛出的异常中并没有包含文件名解析，如下图。所以漏洞就不会被触发了。

[![](./img/85776/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bc776d091c2b4f23.png)

<br>

**个人感想**

相同的触发点采用不同的绕过方式，这种事情已经不是第一次发生了。因为Struts2的交互性和扩展性，同一个触发点有可能有多个绕过方式。而这种漏洞的产生，也告诉我们，想要拿全cve，不仅要关注官方的patch，也要对数据流有比较全面的了解。以上分析为个人分析，感谢360GearTeam小伙伴们的支持。

<br>

**参考文献**

1. [https://community.hpe.com/t5/Security-Research/Struts2-046-A-new-vector/ba-p/6949723#](https://community.hpe.com/t5/Security-Research/Struts2-046-A-new-vector/ba-p/6949723#) 

2. [http://bobao.360.cn/learning/detail/3571.html](http://bobao.360.cn/learning/detail/3571.html) 

3. [http://struts.apache.org/docs/s2-046.html](http://struts.apache.org/docs/s2-046.html) 

4. [https://github.com/apache/struts/commit/352306493971e7d5a756d61780d57a76eb1f519a](https://github.com/apache/struts/commit/352306493971e7d5a756d61780d57a76eb1f519a) 

<br>





**传送门**

[**【重大漏洞预警】Struts 2 远程代码执行漏洞(S2-045S2-046) (含PoC)******](http://bobao.360.cn/learning/detail/3571.html)

**[【漏洞分析】Strust2 S2-046 远程代码执行漏洞两个触发点分析](http://bobao.360.cn/learning/detail/3639.html)**


