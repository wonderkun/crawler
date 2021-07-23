> 原文链接: https://www.anquanke.com//post/id/210192 


# 如何使用Unicode字符进行SQL注入


                                阅读量   
                                **169376**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Davuluri Lahari Rama Sai，文章来源：medium.com
                                <br>原文地址：[https://medium.com/bugbountywriteup/sql-injection-using-unicode-characters-8d360ead379c](https://medium.com/bugbountywriteup/sql-injection-using-unicode-characters-8d360ead379c)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01f9d5403292178db1.png)](https://p2.ssl.qhimg.com/t01f9d5403292178db1.png)



想知道你对应用程序的正常SQL注入payload为什么没有生效吗？答案可能是目标应用程序使用了特殊的字符编码。

我们在对使用Moodle作为LMS(学习管理系统)后台的应用程序进行渗透测试的时候发现了此漏洞。Moodle LMS默认使用Unicode对数据进行转换，他们这样做的初衷是为了便于数据清理。但是同时也给攻击者提供了机会，攻击者可以绕过这些过滤器成功实现SQL攻击。

在我看来，利用Unicode进行SQL注入并不是常见的SQL注入案例。因为您永远无法通过如单引号、用于注释的双连字符、用于注释的//(/*)、等于符号等特殊字符来正面服务器后端存在问题。相反，Unicode的单引号、双连字符、其他注释字符、大括号、等于符号等则可以在当前场景中使用。但这种攻击方式比较局限，如果换一个Unicode字符集就有可能不会受到该漏洞的影响。

现在，让我逐步介绍我是如何发现并利用该漏洞的。

## 步骤1：观察应用程序的cookie

Cookies在披露应用程序背景的详细信息方面发挥着至关重要的作用。我首先是在该系统中发现了一些有趣的cookie：

[![](https://p1.ssl.qhimg.com/t0195944c71f17443dc.png)](https://p1.ssl.qhimg.com/t0195944c71f17443dc.png)

通过这些cookie，我们可以明确的知道该系统的后台使用的是Moodle LMS。

### <a class="reference-link" name="Moodle%20LMS"></a>Moodle LMS

Moodle是一个用PHP编写的免费开源的学习管理系统（LMS）。<br>
开发人员使用Moodle在线创建一个私人学习空间，其中充满了有趣的活动和资料，为管理员提供了对所有数据管理的完全控制权。包括如何在系统中添加管理员、老师、学生。



## 步骤2：访问Moodle的管理页面

根据[Moodle框架](https://docs.moodle.org/39/en/Moodle_site_moodle_directory)的[文件结构](https://docs.moodle.org/39/en/Moodle_site_moodle_directory)，我尝试直接访问该系统的管理页面。经过分析我发现在本系统中，Moodle的管理页面在”/moodle7102”这个路径下（包含了所使用的Moodle版本），所以在默认情况下，管理页面就在”moodle”路径下。

本次分析的Moodle具体环境如下：<br>
Moodle版本为1.9.11<br>
Unicode字符集功能开启<br>
数据库mssql 的版本是13.0.5426.0<br>
PHP版本为：5.2.5



## 步骤3：枚举Unicode字符

通过在Moodle管理平台获取到的信息我们可以确定在该系统中使用了Unicode字符集处理数据。Unicode的[统一](https://www.compart.com/en/unicode)标准为每个字符提供一个唯一的编号，与平台、设备、应用程序或语言无关。

因此，当您将Unicode字符传递给非Unicode数据类型（如char，varchar）时，SQL隐式将Unicode字符转换为与其最相似的非Unicode同源字形。

### <a class="reference-link" name="%E9%AA%8C%E8%AF%81%E6%BC%8F%E6%B4%9E%E5%8F%82%E6%95%B0"></a>验证漏洞参数

要验证输入字段/参数是否容易受到SQL注入的影响，请注意以下我使用的payload：

```
Search Field Value: %%’%%%%v___
Material Fetched: You’ve been Hacked
```

在这里，我们给出了多个’%’字符，但是都被应用程序过滤掉了。并以名称中包含了’v的记录进行响应。这说明我们提供的单引号不能够截断该系统的SQL查询。

为了枚举出哪种类型的Unicode字符字符可以帮助构建有效的payload，可以在文本输入框中输入UTF-8、UTF-16、UTF-32的单引号，看是否会返回数据库错误。

```
Search Field Value: test＇
Material Fetched: 0 results
```

[![](https://p2.ssl.qhimg.com/t01302d1fc184c978c9.png)](https://p2.ssl.qhimg.com/t01302d1fc184c978c9.png)

我们最终使用UTF-8的单引号成功获取到了数据库错误，现在，我们可以使用全局[字符表](https://www.utf8-chartable.de/)中的UTF-8字符来构建有效的payload。

此外，还可以根据应用程序的行为从应用程序中枚举这些值，包括分隔符（如空格）以获得极大的准确性。编码后的payload可以直接提供给代理工具（如BurpSuite）进行拦截请求。

[![](https://p3.ssl.qhimg.com/t01ab60dc3cc7d2d2ce.png)](https://p3.ssl.qhimg.com/t01ab60dc3cc7d2d2ce.png)

[![](https://p1.ssl.qhimg.com/t01f48b3a403c84f2b0.png)](https://p1.ssl.qhimg.com/t01f48b3a403c84f2b0.png)

[![](https://p1.ssl.qhimg.com/t01e807f78329f8cde8.png)](https://p1.ssl.qhimg.com/t01e807f78329f8cde8.png)

[![](https://p1.ssl.qhimg.com/t01404f9864a3edb538.png)](https://p1.ssl.qhimg.com/t01404f9864a3edb538.png)



## 步骤4：构建payload

如果基于union和基于错误回显的SQL注入都失败了，那么我们将无法获取最新的信息。在这种情况下，应用程序所返回的错误信息就没有太大的帮助，因为不会有太多的信息泄露。为了尝试基于UNION的SQL注入，UNION命令没有在响应中显示查询的输出。

所以，让我们为MYSQL构建一个基本的Blind SQL Injection payload进行验证：

```
＇ ＡＮＤ １＝１－－ (TRUE Statement)
＇ ＡＮＤ １＝０－－ (FALSE Statement)
```

或如下所示的基于时间的简单payload：

```
＇ ＷＡＩＴＦＯＲ ＤＥＬＡＹ ＇０：０：１５＇－－ (sleep for 15 seconds)
```

成功了！ 我现在可以进一步利用数据库并转储数据。

这是一个示例，在该示例中，我可以验证DB Server的数据库名称。由于当前数据库是MSSQL，因此下面是我构造的payload。我已经屏蔽了数据库名称以解决隐私问题，但是请注意，在整个payload（包括空格）中应使用相同的Unicode字符。

[![](https://p4.ssl.qhimg.com/t01349314e9f66d4965.png)](https://p4.ssl.qhimg.com/t01349314e9f66d4965.png)

[![](https://p2.ssl.qhimg.com/t01f4044d7b067b1d3c.png)](https://p2.ssl.qhimg.com/t01f4044d7b067b1d3c.png)
