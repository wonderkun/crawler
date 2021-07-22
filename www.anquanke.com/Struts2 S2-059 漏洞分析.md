> 原文链接: https://www.anquanke.com//post/id/214843 


# Struts2 S2-059 漏洞分析


                                阅读量   
                                **240719**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01442c2c78e5497aa1.png)](https://p1.ssl.qhimg.com/t01442c2c78e5497aa1.png)

## 一、前言

2020年8月13日,Apache官方发布了一则公告,该公告称Apache Struts2使用某些标签时,会对标签属性值进行二次表达式解析,当标签属性值使用了`%`{`skillName`}``并且`skillName`的值用户可以控制,就会造成`OGNL`表达式执行。



## 二、漏洞复现

我这里选用的测试环境 `Tomcat 7.0.72`、`Java 1.8.0_181`、`Struts 2.2.1`,受影响的标签直接使用官网公告给出的例子

```
&lt;s:url var="url" namespace="/employee" action="list"/&gt;&lt;s:a id="%`{`payload`}`" href="%`{`url`}`"&gt;List available Employees&lt;/s:a&gt;
```

测试漏洞URL

`http://localhost:8088/S2-059.action?payload=%25`{`3*3`}``

在`s2-029`中由于调用了`completeExpressionIfAltSyntax`方法会自动加上`"%`{`" + expr + "`}`"`,所以`payload`不用带`%`{``}``,在`s2-029`的`payload`里加上`%`{``}``就是`s2-059`的`payload`,具体原因看下面的分析。



## 三、漏洞分析

根据官网公告的漏洞描述及上面的测试过程可以知道,这次漏洞是由于标签属性值进行二次表达式解析产生的。`struts2 jsp` 标签解析是`org.apache.struts2.views.jsp.ComponentTagSupport`类的`doStartTag`和`doEndTag`方法。`debug`跟下 `doStartTag`方法。

[![](https://p3.ssl.qhimg.com/t0176cd97c795b7dcea.png)](https://p3.ssl.qhimg.com/t0176cd97c795b7dcea.png)

跟下`populateParams`方法

`org/apache/struts2/views/jsp/ui/AnchorTag.class`

[![](https://p2.ssl.qhimg.com/t010915fdc636890a76.png)](https://p2.ssl.qhimg.com/t010915fdc636890a76.png)

这里又去调用了父类的`populateParams`方法,接着调用`org/apache/struts2/views/jsp/ui/AbstractUITag.class`类的`populateParams`方法

[![](https://p0.ssl.qhimg.com/t016a7c65dccc4a4101.png)](https://p0.ssl.qhimg.com/t016a7c65dccc4a4101.png)

可以看到这里有给setId赋值,跟下setId方法,`org/apache/struts2/components/UIBean.class`

[![](https://p0.ssl.qhimg.com/t01f19000edd2ac8fa2.png)](https://p0.ssl.qhimg.com/t01f19000edd2ac8fa2.png)

由于id不为null,会执行`this.findString`方法,接着跟下.`org/apache/struts2/components/Component.class`

[![](https://p1.ssl.qhimg.com/t01efcbf185a39021c8.png)](https://p1.ssl.qhimg.com/t01efcbf185a39021c8.png)

[![](https://p1.ssl.qhimg.com/t01bed0ff7afa14fae3.png)](https://p1.ssl.qhimg.com/t01bed0ff7afa14fae3.png)

`altSyntax`默认开启, 所以`this.altSyntax()`会返回`true`,`toType`的值传过来是`String.class`,`if`条件成立会执行到`TextParseUtil.translateVariables('%', expr, this.stack)`

[![](https://p4.ssl.qhimg.com/t0132061b15660572b7.png)](https://p4.ssl.qhimg.com/t0132061b15660572b7.png)

可以看到这里是首先截取去掉`%`{``}``字符,然后从`stack`中寻找`payload`参数,传输的`payload`参数是`%`{`3*2`}``,这里会得到这个值。

执行完`populateParams`方法可以得知这个方法是对属性进行初始化赋值操作。接着跟下`start`方法

[![](https://p4.ssl.qhimg.com/t01d33014fb5e11e677.png)](https://p4.ssl.qhimg.com/t01d33014fb5e11e677.png)

`org/apache/struts2/components/Anchor.class`的`start`方法调用了父类`org/apache/struts2/components/ClosingUIBean.class`的`start`方法

[![](https://p2.ssl.qhimg.com/t01c8ce66d7ce3f5ca8.png)](https://p2.ssl.qhimg.com/t01c8ce66d7ce3f5ca8.png)

在接着跟下`org/apache/struts2/components/UIBean.class$evaluateParams`方法

[![](https://p3.ssl.qhimg.com/t01617407803e8ff7e2.png)](https://p3.ssl.qhimg.com/t01617407803e8ff7e2.png)

接着调用了`populateComponentHtmlId`方法

[![](https://p3.ssl.qhimg.com/t01facea5db3d2738e5.png)](https://p3.ssl.qhimg.com/t01facea5db3d2738e5.png)

在看下`findStringIfAltSyntax`方法的实现

`org/apache/struts2/components/Component.class$findStringIfAltSyntax`

[![](https://p5.ssl.qhimg.com/t0165c27619081098c5.png)](https://p5.ssl.qhimg.com/t0165c27619081098c5.png)

可以看到这里又执行了一次`TextParseUtil.translateVariables`方法.

[![](https://p2.ssl.qhimg.com/t01b14a42b79591856d.png)](https://p2.ssl.qhimg.com/t01b14a42b79591856d.png)

整个过程跟`S2-029`和`S2-036`漏洞产生的原因一样,都是由标签属性二次表达式解析造成漏洞。分析完漏洞产生原因后,我查看了`UIBean class`相关代码,并没有发现除`id`外其它标签属性值可以这样利用。



## 四、总结

此次漏洞需要开启`altSyntax`功能,只能是在标签`id`属性中存在表达式,并且参数还可以控制,这种场景在实际开发中非常少见,危害较小。



## 五、参考链接

[https://cwiki.apache.org/confluence/display/WW/S2-059](https://cwiki.apache.org/confluence/display/WW/S2-059)

[http://blog.topsec.com.cn/struts2%e6%bc%8f%e6%b4%9es2-029%e5%88%86%e6%9e%90/](http://blog.topsec.com.cn/struts2%e6%bc%8f%e6%b4%9es2-029%e5%88%86%e6%9e%90/)
