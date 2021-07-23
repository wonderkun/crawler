> 原文链接: https://www.anquanke.com//post/id/169517 


# 【缺陷周话】第18期：XPath 注入


                                阅读量   
                                **166980**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t018f340a7d36b3de57.jpg)](https://p1.ssl.qhimg.com/t018f340a7d36b3de57.jpg)



## 1、XPath 注入

XPath 是一种用来在内存中导航整个XML树的语言，它使用路径表达式来选取XML文档中的节点或者节点集。XPath 的设计初衷是作为一种面向 XSLT 和 XPointer 的语言,后来独立成了一种W3C标准。而 XPath 注入是指利用 XPath 解析器的松散输入和容错特性，能够在 URL、表单或其它信息上附带恶意的 XPath 查询代码，以获得权限信息的访问权并更改这些信息。XPath 注入与 SQL 注入类似，均是通过构造恶意的查询语句，对应用程序进行攻击。

本文以 JAVA 语言源代码为例，分析 XPath 注入漏洞产生的原因以及修复方法。 详见CWE ID 643: ImproperNeutralization of Data within XPath Expressions (‘XPath Injection’)(http://cwe.mitre.org/data/definitions/113.html)。

## 2、 XPath 注入的危害

由于 SQL 中存在权限的概念，所以在程序中和数据库方面都可以对数据库权限做分配和防护。而 XPath 中数据管理不受权限控制，在表单中提交恶意的 XPath 代码，就可获取到权限限制数据的访问权，并可修改这些数据。同样地，构造恶意查询获取到系统内部完整的XML 文档内容造成信息泄露。也可以在获取到XML文档内容后进行用户权限提升等。

从2016年1月至2019年1月，CVE 中共有10条漏洞信息与其相关。部分漏洞如下：

<th width="152">编号</th><th width="460">概述</th>
|------
<td width="100">CVE-2016-6272</td><td width="458">Epic MyChart 中的 XPath 注入漏洞允许远程攻击者通过 topic.asp 的 topic 参数访问包含静态显示字符串（如字段标签）的 XML 文档的内容。</td>
<td width="100">CVE-2016-9149</td><td width="458">Palo Alto NetworksPAN-OS 中的地址对象解析器在 5.0.20 之前，5.1.13 之前，6.0、6.1、6.1.15，7.0.x 以及7.1版本中，由于错误处理单引号字符，允许远程认证用户通过精心设计的字符串进行XPath注入攻击。</td>
<td width="100">CVE-2015-5970</td><td width="458">Novell ZENworksConfiguration Management (ZCM)11.3 和 11.4 中的 ChangePassword RPC 方法允许远程攻击者通过系统实体引用的格式错误构造查询语句进行XPath注入攻击，并读取任意文本文件。</td>



## 3、示例代码

示例源于Samate Juliet Test Suite for Java v1.3 (https://samate.nist.gov/SARD/testsuite.php)，源文件名：CWE643_Xpath_Injection__connect_tcp_01.java。

### 3.1缺陷代码

[![](https://p0.ssl.qhimg.com/t01901e9ef660fccb13.jpg)](https://p0.ssl.qhimg.com/t01901e9ef660fccb13.jpg)

[![](https://p5.ssl.qhimg.com/t010aa82dc54d067c3c.jpg)](https://p5.ssl.qhimg.com/t010aa82dc54d067c3c.jpg)

上述示例代码 51-63 行，程序进行 TCP 连接并读取 Socket 的数据，在130、131行对从 Socket 中读取到的数据进行处理，并在第138行中构造了 XPath 查询语句查询对应的节点。正常情况下（例如搜索用户名 guest，密码为 guestPassword 的用户），此代码所执行的查询如下所示：

> //users/user[name/text()=‘guest’ and pass/text()=’guestPassword’] /secret/text()

如果攻击者输入用户名 ‘ or 1=1，密码 ‘ or 1=1，则该查询会变成：

> //users/user[name/text()=”or 1=1 and pass/text()=”or 1=1]/secret/text()

附加条件 1′ or ‘1’=’1 会使 where 从句永远评估为 true，因此该查询在逻辑上将等同于一个更为简化的查询：

> //users/text()

这样就可以查询到文档中存储的所有用户节点的信息。

使用360代码卫士对上述示例代码进行检测，可以检出“XPath注入”缺陷，显示等级为“高”。从跟踪路径中可以分析出数据的污染源以及数据流向，在代码行第141行报出缺陷，如图1所示：

[![](https://p2.ssl.qhimg.com/dm/1024_627_/t01ca81a075b8d5caf0.jpg)](https://p2.ssl.qhimg.com/dm/1024_627_/t01ca81a075b8d5caf0.jpg)

图1：XPath 注入的检测示例

### 3.2 修复代码

[![](https://p4.ssl.qhimg.com/t019489e6e7eebdbedd.jpg)](https://p4.ssl.qhimg.com/t019489e6e7eebdbedd.jpg)

在上述修复代码中，第130、131行使用 ESAPI 对 Socket 中的值进行编码， encodeForXPath 的作用是为了将包含的 XML 特殊字符（&lt;、&gt;、&amp;、、”、’）替换为十六进制的转义序列。

使用360代码卫士对修复后的代码进行检测，可以看到已不存在“XPath注入”缺陷。如图2：

[![](https://p5.ssl.qhimg.com/dm/1024_619_/t01f99bcdd06ea80c0b.jpg)](https://p5.ssl.qhimg.com/dm/1024_619_/t01f99bcdd06ea80c0b.jpg)

图2：修复后检测结果



## 4 、如何避免 XPath 注入

要避免XPath注入，需要注意以下几点：

> （1）对用户的输入进行合理验证，对特殊字符（如&lt;、&gt;、’、”等）等进行转义。过滤可以在客户端和服务端两边实现，如果可能的话，建议两者同时进行过滤。
（2）创建一份安全字符白名单，确保 XPath 查询中由用户控制的数值完全来自于预定的字符集合，不包含任何 XPath 元字符。
（3）使用源代码静态分析工具，进行自动化的检测，可以有效的发现源代码中的 XPath 注入问题。
