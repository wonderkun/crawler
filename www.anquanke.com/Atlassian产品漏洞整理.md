> 原文链接: https://www.anquanke.com//post/id/197665 


# Atlassian产品漏洞整理


                                阅读量   
                                **901652**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01b8a59d4fd9a4dd8d.png)](https://p3.ssl.qhimg.com/t01b8a59d4fd9a4dd8d.png)



## Atlassian简介

以下来自Atlassian中文官方微信公众号。

> 关于Atlassian：全球领先的软件开发和协作平台，为全球11万家企业提供创新的力量。全球前100强公司有超过90%的企业都在使用Atlassian的产品。其明星软件Jira Software为全球敏捷团队的首选软件开发工具，帮助开发团队规划、追踪和发布世界一流的软件。Atlassian的Marketplace拥有数千款不同功能的应用程序，可帮助您自定义和扩展Atlassian的功能。
Atlassian的全球客户包括：HSBC、摩根士丹利、耐飞、宝马、奔驰、耐克、Oracle、GSK，Airbnb、CSIRO、特斯拉、Autodesk、eBay、丰田等。
Atlassian的中国客户包括：百度、华为、联想、滴滴、京东、360企业安全、小米、顺丰、摩拜、招商银行、民生银行、中信银行、平安证券、泰康人寿、中华保险、众安保险等。

### <a class="reference-link" name="%E5%8F%82%E8%80%83"></a>参考
- [Atlassian：一家没有销售团队，不靠融资做到百亿美元市值的技术公司](https://mp.weixin.qq.com/s/EqlK9WjFpYndjqohC6LuCg)
- [Atlassian 这家公司的产品为什么这么火？](https://www.zhihu.com/question/20721319)
- [协同软件供应商Atlassian估值超30亿美元](https://mp.weixin.qq.com/s/jHxzaSN6GcFkpyA03j4lWA)
- [非典型硅谷式创业 科技公司Atlassian的奇迹](https://mp.weixin.qq.com/s/ypynzvRyD3nFUkFenE5BQg)
- [中国移动通信研究院：为什么选择Atlassian项目管理及协作工具](https://mp.weixin.qq.com/s/1SudKlnZdMc5TG-goK8B1w)
- [Atlassian中国封面人物 | 李晓东，打造民生银行软件工程平台](https://mp.weixin.qq.com/s/Y7sOihxHPEceM_6w8G1o9w)
- [拐点临近 – 美国国防部 Atlassian 应用程序的扩展之路](https://mp.weixin.qq.com/s/A23MCCOEAU9pGvhYG_qg9Q)


## Atlassian核心产品简介

Atlassian服务端软件主要有
- Jira（缺陷跟踪管理系统。该系统主要用于对工作中各类问题、缺陷进行跟踪管理）
- Confluence（企业知识管理与协同软件，也可以用于构建企业WiKi）
- Bitbucket（Git代码托管解决方案）
其中最著名的是Jira和Confluence。很多大厂包括(Apache的issue)用Jira跟踪bug和漏洞，也有很多大厂用Confluence作为一个在线协作文档编写的工具。



## Jira相关背景知识

背景知识主要内容翻译自官方文档。

### <a class="reference-link" name="WebWork"></a>WebWork

Jira使用MVC框架WebWork（不同于Struts 2）来处理用户发起的WEB请求。每个请求都是使用WebWork action来处理，在其中又使用了其他的utility and Manager classes来完成一个任务。

作为响应返回给客户端的HTML大部分都是View层的JSP生成的。<br>
URL中的”.jspa”后缀标识其后端对应的是一个JSP文件。

在Jira中，URL到Java类的映射关系是通过Webwork 1.x框架来完成的。其文档可以参考：[http://opensymphony.com/webwork_old/src/docs/manual](http://opensymphony.com/webwork_old/src/docs/manual)

而在Confluence, Bamboo and Crowd中，已经被Webwork 2所取代。

classes和URL的对应关系在actions.xml文件中声明了

```
src/webapp/WEB-INF/classes/actions.xml
```

其典型的样子大概长这样：

```
&lt;!-- Workflow Transitions --&gt;
    &lt;action name="admin.workflow.ViewWorkflowTransition" alias="ViewWorkflowTransition" roles-required="admin"&gt;
        &lt;view name="success"&gt;/secure/admin/views/workflow/viewworkflowtransition.jsp&lt;/view&gt;

        &lt;command name="moveWorkflowFunctionUp" alias="MoveWorkflowFunctionUp"&gt;
            &lt;view name="error"&gt;/secure/admin/views/workflow/viewworkflowtransition.jsp&lt;/view&gt;
            &lt;view name="success"&gt;/secure/admin/views/workflow/viewworkflowtransition.jsp&lt;/view&gt;
        &lt;/command&gt;

        &lt;command name="moveWorkflowFunctionDown" alias="MoveWorkflowFunctionDown"&gt;
            &lt;view name="error"&gt;/secure/admin/views/workflow/viewworkflowtransition.jsp&lt;/view&gt;
            &lt;view name="success"&gt;/secure/admin/views/workflow/viewworkflowtransition.jsp&lt;/view&gt;
        &lt;/command&gt;
    &lt;/action&gt;
```

详细参考：<br>[https://developer.atlassian.com/server/jira/platform/webwork/](https://developer.atlassian.com/server/jira/platform/webwork/)

注意几点：
- 每个action都有一个`alias`属性，其实就是你在浏览器看到的URL的一部分。而`name`属性就是这个alias对应的Java类。
- command元素的name属性可以在URL中加上`!commandName`作为其后缀，然后需要在对应的Action类中实现`doCommandName()`方法。
- 如果action中没有指定`roles-required`的值，则此action需要自行处理其权限问题，否则此action可以被任意用户访问。
Command元素是可选的，如果同一个Action需要处理多个交互，就会用到command。一般带有command的URL长这样：

```
SomeAction!myCommand.jspa
```

然后其在Action类中是这样实现的。

```
public String doMyCommand() `{`

    // implement the command logic here

    return "someview";
`}`
```

当没有指定command的时候，Action中对应的处理方法是：`doExecute`

原文讲得很清楚，看原文就可以了。

### <a class="reference-link" name="Jira%E7%99%BB%E5%BD%95%E8%AE%A4%E8%AF%81%E6%A1%86%E6%9E%B6(Seraph)"></a>Jira登录认证框架(Seraph)

Seraph是一个开源认证框架，主要由Atlassian开发和维护。<br>
Jira、Confluence的登录认证是都由Seraph来负责的。<br>
Seraph是通过Servlet的Filter实现的。

Seraph的功能只是用来在给定一个Web请求的情况下，将该请求与特定用户相关联。它支持多种认证方式：
- HTTP Basic认证
- 基于表单的认证：基于Cookie、(ie. redirect to an internal or external login form), and looking up credentials already stored in the user’s session (e.g. a cookie set by a SSO system).
Seraph本身并不进行用户管理，它只是检查请求中的登录凭证，然后将用户管理的功能（查找某用户，查看某用户的密码是否正确）指派给Jira的用户管理系统（内置的Crowd）处理。Crowd本来是Atlassian的身份管理及单点登录工具。而Jira and Confluence都内置了一部分Crowd的核心模块，用于统一的用户管理。

如果想将单点登录（SSO）功能集成到Jira中，需要实现一个[自定义的Seraph authenticator](https://docs.atlassian.com/atlassian-seraph/2.6.1-m1/sso.html)。很多客户也都是这样做的，因为Jira本身并没有集成单点登录系统。如果将Crowd集成到Jira中，参考：[https://confluence.atlassian.com/crowd/integrating-crowd-with-atlassian-jira-192625.html](https://confluence.atlassian.com/crowd/integrating-crowd-with-atlassian-jira-192625.html)

Seraph 由几个核心元素组成：
<li>Security Service<br>
Security services用于确定特定的HTTP请求需要哪些角色的权限。<br>
Seraph有两个security services：the `Path` service and the `WebWork` service.<br>
其中Path Service 用于对URL paths进行安全限定，可通过其自己的xm文件进行配置：seraph-paths.xml。<br>
受限，在security-config.xml配置文件中需要有这样的配置：
<pre><code class="lang-xml hljs">&lt;service class="com.atlassian.seraph.service.PathService"&gt;
  &lt;init-param&gt;
      &lt;param-name&gt;config.file&lt;/param-name&gt;
      &lt;param-value&gt;/seraph-paths.xml&lt;/param-value&gt;
  &lt;/init-param&gt;
&lt;/service&gt;
</code></pre>
然后seraph-paths.xml中定义了特定url请求所需要的对应角色：
<pre><code class="lang-xml hljs">&lt;seraph-paths&gt;
  &lt;!-- You can configure any number of path elements --&gt;
  &lt;path name="admin"&gt;
      &lt;url-pattern&gt;/admin/*&lt;/url-pattern&gt;
      &lt;role-name&gt;myapp-administrators, myapp-owners&lt;/role-name&gt;
  &lt;/path&gt;
&lt;/seraph-paths&gt;
</code></pre>
比如上面这个配置就定义了`/admin/*`这样的url就必须myapp-administrators，myapp-owners这样角色的用户可以访问。
</li>
另外WebWork Service需要用actions.xml配置文件来进行配置（前面已经提到了）：

```
&lt;action name="project.AddProject" roles-required="admin"&gt;
    &lt;view name="input"&gt;/secure/admin/views/addproject.jsp&lt;/view&gt;
&lt;/action&gt;
```

比如上面这个就表示`/secure/admin/views/addproject.jsp`这个url请求的需要admin角色才能操作。
- Interceptor：用于在一些安全事件（登录、注销）的前后执行的一些代码。在Servlet规范下是不可能做的。比如用户登录之后，记录上次登录的日期；用户注销之后清理一些资源；记录用户登录失败的次数。
<li>Authenticator<br>
Authenticator用于对用户进行认证（authenticate） , 对用户进行登录、注销等操作，以及检查他们的角色权限。</li>
- Controller：进行全局的安全控制开关。
- Role Mapper
### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E9%85%8D%E7%BD%AESeraph"></a>如何配置Seraph

可以在两个地方配置Seraph：

<a class="reference-link" name="%E9%80%9A%E8%BF%87seraph-config.xml%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6"></a>**通过seraph-config.xml配置文件**

Seraph的核心是通过seraph-config.xml来进行配置的。通常放在web应用的`WEB-INF/classes`目录下。

```
&lt;security-config&gt;
  &lt;parameters&gt;
    &lt;init-param&gt;
      &lt;!--
      the URL to redirect to when the user tries to access a protected resource (rather than clicking on
        an explicit login link). Most of the time, this will be the same value as 'link.login.url'.
      - if the URL is absolute (contains '://'), then redirect that URL (for SSO applications)
      - else the context path will be prepended to this URL

      If '$`{`originalurl`}`' is present in the URL, it will be replaced with the context-relative URL that the user requested.
      This gives SSO login pages the chance to redirect to the original page
      --&gt;
      &lt;param-name&gt;login.url&lt;/param-name&gt;
      &lt;param-value&gt;/login.jsp?os_destination=$`{`originalurl`}`&lt;/param-value&gt;
      &lt;!-- &lt;param-value&gt;http://example.com/SSOLogin?target=$`{`originalurl`}`&lt;/param-value&gt;--&gt;
    &lt;/init-param&gt;
    &lt;init-param&gt;
      &lt;!--
      the URL to redirect to when the user explicitly clicks on a login link (rather than being redirected after
        trying to access a protected resource). Most of the time, this will be the same value as 'login.url'.
      - same properties as login.url above
      --&gt;
      &lt;param-name&gt;link.login.url&lt;/param-name&gt;
      &lt;param-value&gt;/secure/Dashboard.jspa?os_destination=$`{`originalurl`}`&lt;/param-value&gt;
      &lt;!-- &lt;param-value&gt;http://mycompany.com/SSOLogin?target=$`{`originalurl`}`&lt;/param-value&gt;--&gt;
    &lt;/init-param&gt;
    &lt;init-param&gt;
      &lt;!-- URL for logging out.
      - If relative, Seraph just redirects to this URL, which is responsible for calling Authenticator.logout().
      - If absolute (eg. SSO applications), Seraph calls Authenticator.logout() and redirects to the URL
      --&gt;
      &lt;param-name&gt;logout.url&lt;/param-name&gt;
      &lt;param-value&gt;/secure/Logout!default.jspa&lt;/param-value&gt;
      &lt;!-- &lt;param-value&gt;http://mycompany.com/SSOLogout&lt;/param-value&gt;--&gt;
    &lt;/init-param&gt;

    &lt;!-- The key that the original URL is stored with in the session --&gt;
    &lt;init-param&gt;
      &lt;param-name&gt;original.url.key&lt;/param-name&gt;
      &lt;param-value&gt;os_security_originalurl&lt;/param-value&gt;
    &lt;/init-param&gt;
    &lt;init-param&gt;
      &lt;param-name&gt;login.cookie.key&lt;/param-name&gt;
      &lt;param-value&gt;seraph.os.cookie&lt;/param-value&gt;
    &lt;/init-param&gt;
    &lt;!-- Specify 3 characters to make cookie encoding unique for your application, to prevent collisions
    if more than one Seraph-based app is used.
    &lt;init-param&gt;
      &lt;param-name&gt;cookie.encoding&lt;/param-name&gt;
      &lt;param-value&gt;xYz&lt;/param-value&gt;
    &lt;/init-param&gt;
    --&gt;
    &lt;!-- Basic Authentication can be enabled by passing the authentication type as a configurable url parameter.
    With this example, you will need to pass http://mycompany.com/anypage?os_authType=basic in the url to enable Basic Authentication --&gt;
    &lt;init-param&gt;
        &lt;param-name&gt;authentication.type&lt;/param-name&gt;
        &lt;param-value&gt;os_authType&lt;/param-value&gt;
    &lt;/init-param&gt;
  &lt;/parameters&gt;

  &lt;!-- Determines what roles (permissions) a user has. --&gt;
  &lt;rolemapper class="com.atlassian.myapp.auth.MyRoleMapper"/&gt;

  &lt;!-- A controller is not required. If not specified, security will always be on
  &lt;controller class="com.atlassian.myapp.setup.MyAppSecurityController" /&gt;
  --&gt;

  &lt;!-- Logs in users. Must be overridden for SSO apps --&gt;
  &lt;authenticator class="com.atlassian.seraph.auth.DefaultAuthenticator"/&gt;


  &lt;services&gt;
    &lt;!-- Specifies role requirements for accessing specified URL paths --&gt;
    &lt;service class="com.atlassian.seraph.service.PathService"&gt;
      &lt;init-param&gt;
        &lt;param-name&gt;config.file&lt;/param-name&gt;
        &lt;param-value&gt;/seraph-paths.xml&lt;/param-value&gt;
      &lt;/init-param&gt;
    &lt;/service&gt;

    &lt;!-- Specifies role requirements to execute Webwork actions --&gt;
    &lt;service class="com.atlassian.seraph.service.WebworkService"&gt;
      &lt;init-param&gt;
        &lt;param-name&gt;action.extension&lt;/param-name&gt;
        &lt;param-value&gt;jspa&lt;/param-value&gt;
      &lt;/init-param&gt;
    &lt;/service&gt;
  &lt;/services&gt;

  &lt;interceptors&gt;
    &lt;!-- &lt;interceptor class="com.atlassian.myapp.SomeLoginInterceptor"/&gt; --&gt;
  &lt;/interceptors&gt;
&lt;/security-config&gt;
```

<a class="reference-link" name="%E9%80%9A%E8%BF%87%E8%BF%87%E6%BB%A4%E5%99%A8%EF%BC%88Filters%EF%BC%89"></a>**通过过滤器（Filters）**

与Seraph相关的，有两个Filter（`com.atlassian.seraph.filter.LoginFilter`，`com.atlassian.seraph.filter.SecurityFilter`），和一个Servlet（`com.atlassian.seraph.logout.LogoutServlet`）是必需放在`WEB-INF/web.xml`中的。

```
&lt;filter&gt;
    &lt;filter-name&gt;login&lt;/filter-name&gt;
    &lt;filter-class&gt;com.atlassian.seraph.filter.LoginFilter&lt;/filter-class&gt;
&lt;/filter&gt;

&lt;filter&gt;
    &lt;filter-name&gt;security&lt;/filter-name&gt;
    &lt;filter-class&gt;com.atlassian.seraph.filter.SecurityFilter&lt;/filter-class&gt;
&lt;/filter&gt;

&lt;filter-mapping&gt;
    &lt;filter-name&gt;login&lt;/filter-name&gt;
    &lt;url-pattern&gt;/*&lt;/url-pattern&gt;
&lt;/filter-mapping&gt;

&lt;filter-mapping&gt;
    &lt;filter-name&gt;security&lt;/filter-name&gt;
    &lt;url-pattern&gt;/*&lt;/url-pattern&gt;
&lt;/filter-mapping&gt;

&lt;servlet&gt;
    &lt;servlet-name&gt;logout&lt;/servlet-name&gt;
    &lt;servlet-class&gt;com.atlassian.seraph.logout.LogoutServlet&lt;/servlet-class&gt;
&lt;/servlet&gt;

&lt;servlet-mapping&gt;
    &lt;servlet-name&gt;logout&lt;/servlet-name&gt;
    &lt;url-pattern&gt;/logout&lt;/url-pattern&gt;
&lt;/servlet-mapping&gt;
```

### <a class="reference-link" name="Jira%E7%9A%84%E8%AE%A4%E8%AF%81%EF%BC%88authentication%EF%BC%89%E6%96%B9%E5%BC%8F"></a>Jira的认证（authentication）方式

The Jira Server platform, Jira Software Server, and Jira Service Desk Server REST APIs有以下几种认证方式：

<a class="reference-link" name="OAuth"></a>**OAuth**

使用Jira产生的Token来进行认证，虽然实现不太方便，但是比较安全。<br>
具体参考：[https://developer.atlassian.com/server/jira/platform/oauth/](https://developer.atlassian.com/server/jira/platform/oauth/)

<a class="reference-link" name="HTTP%20Basic%E8%AE%A4%E8%AF%81"></a>**HTTP Basic认证**

其实就是在HTTP请求头中加上一个HTTP请求头，这种方式没那么安全，但是在脚本中或者命令行掉REST接口比较好用。<br>
具体参考：[https://developer.atlassian.com/server/jira/platform/basic-authentication/](https://developer.atlassian.com/server/jira/platform/basic-authentication/)<br>
比如CURL就可以这样用：

```
curl -u username:password -X GET -H "Content-Type: application/json" http://localhost:8080/rest/api/2/issue/createmeta
```

curl会自动帮你把提供的用户名密码计算加到Header中。

或者你也可以自己计算好之后，把它作为一个HTTP头来请求。

其实就是把`username:password`进行base64编码，然后加到`Authorization: Basic `{`base64`}``即可。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0195280d674b240275.png)

对应到代码中是：

atlassian-jira-software-7.13.0-standalone/atlassian-jira/WEB-INF/lib/atlassian-seraph-3.0.3.jar!/com/atlassian/seraph/filter/HttpAuthFilter.class

继承自PasswordBasedLoginFilter

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0196cb4aaf69484b03.png)

即先解码base64，然后传入username和password，返回一个UserPasswordPair对象。

```
new UserPasswordPair(creds.getUsername(), creds.getPassword(), false);
```

<a class="reference-link" name="%E9%AA%8C%E8%AF%81%E7%A0%81(CAPTCHA)"></a>**验证码(CAPTCHA)**

多次连续登陆失败之后，就会出现验证码。

<a class="reference-link" name="%E5%9F%BA%E4%BA%8ECookie%E7%9A%84%E8%AE%A4%E8%AF%81"></a>**基于Cookie的认证**

就是用Cookie来进行认证。对应到代码中是：

atlassian-jira-software-7.13.0-standalone/atlassian-jira/WEB-INF/lib/atlassian-seraph-3.0.3.jar!/com/atlassian/seraph/filter/LoginFilter.class

继承自PasswordBasedLoginFilter

[![](https://p5.ssl.qhimg.com/t018790b0635acb3e2c.png)](https://p5.ssl.qhimg.com/t018790b0635acb3e2c.png)

### <a class="reference-link" name="%E8%A1%A8%E5%8D%95token%E7%9A%84%E5%A4%84%E7%90%86%EF%BC%88%E9%98%B2CSRF%EF%BC%89"></a>表单token的处理（防CSRF）

[https://developer.atlassian.com/server/jira/platform/form-token-handling/](https://developer.atlassian.com/server/jira/platform/form-token-handling/)

想要对某个Action进行 xsrf token验证，需要进行以下步骤：

1、首先定位到某个Action具体执行的方法，一般默认是doExecute()

2、在这个方法前加上注解：`[@com](https://github.com/com).atlassian.jira.security.xsrf.RequiresXsrfCheck`

如果在自动化脚本中，可以使用以下HTTP头来绕过反CSRF校验机制：

```
X-Atlassian-Token: no-check
```

在Jira的java代码中生成token的方法为：

```
import com.atlassian.jira.security.xsrf.XsrfTokenGenerator;

XsrfTokenGenerator xsrfTokenGenerator = ComponentManager.getComponentInstanceOfType(XsrfTokenGenerator.class);
String token = xsrfTokenGenerator.generateToken(request);
```



## Jira历史漏洞

### <a class="reference-link" name="%5BCVE-2019-8442%5D%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF%E6%B3%84%E9%9C%B2%E6%BC%8F%E6%B4%9E"></a>[CVE-2019-8442]敏感信息泄露漏洞

问题在于`CachingResourceDownloadRewriteRule`:

官方issues：

[https://jira.atlassian.com/browse/JRASERVER-69241](https://jira.atlassian.com/browse/JRASERVER-69241)

官方描述：

> The CachingResourceDownloadRewriteRule class in Jira before version 7.13.4, and from version 8.0.0 before version 8.0.4, and from version 8.1.0 before version 8.1.1 allows remote attackers to access files in the Jira webroot under the META-INF directory via a lax path access check.

CNNVD描述：

> Atlassian Jira 7.13.4之前版本、8.0.4之前版本和8.1.1之前版本中的CachingResourceDownloadRewriteRule类存在安全漏洞。远程攻击者可利用该漏洞访问Jira webroot中的文件。

相应插件下载：

[http://central.maven.org/maven2/org/tuckey/urlrewritefilter/4.0.3/urlrewritefilter-4.0.3.jar](http://central.maven.org/maven2/org/tuckey/urlrewritefilter/4.0.3/urlrewritefilter-4.0.3.jar)

其实在lib目录下有。

`UrlRewriteFilter`

> It is a very powerful tool just like Apache’s mod_rewrite.

bug bounty作者描述漏洞细节：

> the application takes input from the user, and uses it to build a file path to which the user is forwarded. Since the user controls a part of that path, they may be able to direct themselves to sensitive files, like /META-INF/*, application code, or configuration files, which may contain passwords.

只是把用户提供的url在服务端重写了一下，只能访问一些META-INF目录下的配置文件，不能访问jsp源码。<br>
参考：[https://www.cnblogs.com/dennisit/p/3177108.html](https://www.cnblogs.com/dennisit/p/3177108.html)

<a class="reference-link" name="Demo"></a>**Demo**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01df115290a218434e.png)

然而并不能访问`WEB-INF`目录下的文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01df76621b4876c608.png)

这个漏洞危害较低，看看就好。

confluence之前爆过这个urlrewrite.xml的任意配置文件读取漏洞：

[https://www.exploit-db.com/exploits/39170](https://www.exploit-db.com/exploits/39170)

不过应该后来一起被修复了。

有人提供了一份[源码](https://github.com/moink635/mysource/blob/master/jira-project/jira-components/jira-core/src/main/java/com/atlassian/jira/plugin/webresource/CachingResourceDownloadRewriteRule.java)，从注释里看，这里就是为了防止路径穿越的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012dc44caa8407205d.png)

### <a class="reference-link" name="%5BCVE-2019-8444%5D%E5%AD%98%E5%82%A8%E5%9E%8BXSS"></a>[CVE-2019-8444]存储型XSS

影响版本：version &lt; 7.13.6、8.0.0 &lt;= version &lt; 8.3.2

出在评论的地方。

Demo：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d59c3ca9c08cf950.png)

更多信息参考Talos的博客：

[https://blog.talosintelligence.com/2019/09/vuln-spotlight-atlassian-jira-sept-19.html](https://blog.talosintelligence.com/2019/09/vuln-spotlight-atlassian-jira-sept-19.html)

### <a class="reference-link" name="%5BCVE-2018-13404%5DVerifyPopServerConnection%E5%8A%9F%E8%83%BDSSRF"></a>[CVE-2018-13404]VerifyPopServerConnection功能SSRF

需要管理员权限才能触发。

这个功能是为了验证邮件服务器的连接的开放性，但是没有对可访问的IP和端口进行限制。这里`/secure/admin/VerifySmtpServerConnection!add.jspa`接收了`serverName`和`port`参数，服务端可以向用户指定的`serverName`和`port`发起TCP请求，导致了SSRF。

参考了一下Jira的开发文档，知道了一般url后缀对应的是do某方法，然后url前面的是对应的Java的类，所以可以在<br>`atlassian-jira-software-7.13.0-standalone/atlassian-jira/WEB-INF/atlassian-bundled-plugins/jira-mail-plugin-10.0.13.jar!/com/atlassian/jira/plugins/mail/webwork/VerifySmtpServerConnection#doAdd`<br>
下断点。

[![](https://p5.ssl.qhimg.com/t01f56eb42f9c52af8a.jpg)](https://p5.ssl.qhimg.com/t01f56eb42f9c52af8a.jpg)

最终在`atlassian-jira-software-7.13.0-standalone/atlassian-jira/WEB-INF/atlassian-bundled-plugins/base-hipchat-integration-plugin-7.10.3.jar!/javax/mail/Service#connect`<br>
调用

```
connected = this.protocolConnect(host, port, user, password);
```

完成TCP请求。

参考：[https://docs.oracle.com/javaee/7/api/javax/mail/Service.html#connect-java.lang.String-int-java.lang.String-java.lang.String-](https://docs.oracle.com/javaee/7/api/javax/mail/Service.html#connect-java.lang.String-int-java.lang.String-java.lang.String-)

### <a class="reference-link" name="%5BCVE-2019-11581%5D%E6%9C%AA%E6%8E%88%E6%9D%83%E6%9C%8D%E5%8A%A1%E7%AB%AF%E6%A8%A1%E6%9D%BF%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E"></a>[CVE-2019-11581]未授权服务端模板注入漏洞

这个漏洞是Jira爆出的影响力较大的漏洞，是未授权RCE。但是由于这个出漏洞的功能并不是Jira默认开启的，所以影响有限。<br>
详情参考：[https://mp.weixin.qq.com/s/d2yvSyRZXpZrPcAkMqArsw](https://mp.weixin.qq.com/s/d2yvSyRZXpZrPcAkMqArsw)

### <a class="reference-link" name="%5BCVE-2019-8451%5D%E6%9C%AA%E6%8E%88%E6%9D%83SSRF%E6%BC%8F%E6%B4%9E"></a>[CVE-2019-8451]未授权SSRF漏洞

在漏洞的利用方面主要是利用了Jira在检查用户提供的url时可以通过`@`符进行绕过。在调试方面的困难点在于漏洞的触发需要加上特殊请求头`X-Atlassian-Token: no-check`。

详情参考：[https://mp.weixin.qq.com/s/_Tsq9p1pQyszJt2VaXd61A](https://mp.weixin.qq.com/s/_Tsq9p1pQyszJt2VaXd61A)

还有一个早前的比较著名的SSRF漏洞，一些bug hunters用这个漏洞攻击AWS获取其meta敏感信息。

### <a class="reference-link" name="%5BCVE-2017-9506%5DAtlassian%20OAuth%E6%8F%92%E4%BB%B6%E7%9A%84SSRF%E6%BC%8F%E6%B4%9E"></a>[CVE-2017-9506]Atlassian OAuth插件的SSRF漏洞

影响范围：

Atlassian OAuth插件1.3.0 &lt; version &lt; 1.9.12以及2.0.0 &lt; version &lt; 2.0.4

Jira和Confluence中都有这个插件。

Demo:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img-blog.csdnimg.cn/20190425111156491.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NhaXFpaXFp,size_16,color_FFFFFF,t_70)

官方修复commit:

[https://bitbucket.org/atlassian/atlassian-oauth/commits/cacd1a118fdc3dc7562d48110340b3de4f0b0af9](https://bitbucket.org/atlassian/atlassian-oauth/commits/cacd1a118fdc3dc7562d48110340b3de4f0b0af9)

调试：

根据文章中的描述，漏洞点在：`IconUriServlet`。

从jar包中找字符串：

```
grep -irn "iconuri" `find .|grep .jar`
```

然后定位到`atlassian-jira-6.4.14-standalone/atlassian-jira/WEB-INF/atlassian-bundled-plugins/atlassian-oauth-service-provider-plugin-1.9.8.jar!/com/atlassian/oauth/serviceprovider/internal/servlet/user/IconUriServlet.class的doGet()`<br>
下断点。

[![](https://img-blog.csdnimg.cn/20190425114801201.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NhaXFpaXFp,size_16,color_FFFFFF,t_70)](https://img-blog.csdnimg.cn/20190425114801201.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NhaXFpaXFp,size_16,color_FFFFFF,t_70)

可以看到，这里接收了`consumerUri`参数之后，直接对该url发起了请求。

参考：[http://dontpanic.42.nl/2017/12/there-is-proxy-in-your-atlassian.html](http://dontpanic.42.nl/2017/12/there-is-proxy-in-your-atlassian.html)



## Confluence

#### <a class="reference-link" name="Confluence%E7%9B%B8%E5%85%B3%E8%83%8C%E6%99%AF%E7%9F%A5%E8%AF%86"></a>Confluence相关背景知识

背景知识主要内容翻译自官方文档。

##### <a class="reference-link" name="Confluence%E7%9A%84Home%E7%9B%AE%E5%BD%95%E4%BB%A5%E5%8F%8A%E9%87%8D%E8%A6%81%E7%9B%AE%E5%BD%95%E8%AF%B4%E6%98%8E"></a>Confluence的Home目录以及重要目录说明

[https://confluence.atlassian.com/doc/confluence-home-and-other-important-directories-590259707.html](https://confluence.atlassian.com/doc/confluence-home-and-other-important-directories-590259707.html)
<li>
`bin/setenv.bat` 或者`bin/setenv.sh`文件：<br>
可用来编辑一些`CATALINA_OPTS`变量、内存设置、gc变量等系统属性。</li>
<li>
`confluence/WEB-INF/classes/confluence-init.properties`：<br>
在这里指定confluence的home目录。</li>
Confluence的Home目录是Confluence存储其配置信息、搜索索引和附件的目录。 “Home目录”也叫“数据目录”。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img-blog.csdnimg.cn/20190820173821952.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NhaXFpaXFp,size_16,color_FFFFFF,t_70)

其他文件及目录的介绍：
<li>
`confluence.cfg.xml`: 包含confluence的各种属性。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img-blog.csdnimg.cn/20190820181908595.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NhaXFpaXFp,size_16,color_FFFFFF,t_70)
</li>
<li>
`attachments/`: confluence上的所有附件都存在这里。如果想要更改，可以编辑`confluence.cfg.xml`文件的这个属性`attachments.dir`
</li>
<li>
`backups/`: 每日自动备份（或手动备份）的内容会存放在这里，文件名大概是：`daily-backup-YYYY_MM_DD.zip`这个样子。想要更改这个位置，可以编辑`confluence.cfg.xml`的这个属性`daily.backup.dir`。</li>
<li>
`bundled-plugins/`: 每次confluence重启的时候，都会重新从数据库中读取。所以，**删除这个目录下的文件并不能卸载这个插件！**
</li>
<li>
`database/`:主要是用于存储h2数据库文件。 如果使用外部数据库，比如mysql，就不会用到这个目录。<br>[![](https://img-blog.csdnimg.cn/20190820175656420.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NhaXFpaXFp,size_16,color_FFFFFF,t_70)](https://img-blog.csdnimg.cn/20190820175656420.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NhaXFpaXFp,size_16,color_FFFFFF,t_70)
</li>
<li>
`index/`: 应用程序大量使用Confluence索引进行内容搜索和最近更新的列表，这对于正在运行的Confluence实例至关重要。 如果此目录中的数据丢失或损坏，可以通过从Confluence中运行完整重新索引来恢复它。 此过程可能需要很长时间，具体取决于Confluence数据库存储的数据量。<br>[![](https://img-blog.csdnimg.cn/20190820175813436.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NhaXFpaXFp,size_16,color_FFFFFF,t_70)](https://img-blog.csdnimg.cn/20190820175813436.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2NhaXFpaXFp,size_16,color_FFFFFF,t_70)
</li>
<li>
`journal/`: [暂时不太清楚]</li>
<li>
`logs/`: confluence的应用日志。</li>
<li>
`plugin-cache/`: Confluence所有的插件都存放在数据库中，但为了能快速访问插件JARs中的类，于是把插件缓存到了这个目录下。当系统安装或者卸载插件的时候会更新这个目录。每次confluence重启的时候，都会重新从数据库中读取。所以，**删除这个目录下的文件并不能卸载这个插件！**<br>[![](https://img-blog.csdnimg.cn/20190820175911888.png)](https://img-blog.csdnimg.cn/20190820175911888.png)
</li>
<li>
`temp/`: 用于一些运行时的功能，比如exporting, importing, file upload and indexing。此目录中的文件是临时文件，可在Confluence关闭时被安全地删除。 Confluence中的daily job会删除不再需要的文件。也可以在`confluence.cfg.xml`文件中定义不同的temp目录，然后在`webwork.multipart.saveDir`属性中设置新的值</li>
<li>
`thumbnails/`: 存放图片文件的缩略图。</li>
<li>
`shared-home/`: 某些功能的缓存文件，比如Office文件以及PDF预览也放在这个目录下。也用于迁移到Data Center,。</li>
所有其他的数据，包括页面的内容，都是存放在数据库中的。

<a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%9B%B4%E6%94%B9Home%E7%9B%AE%E5%BD%95"></a>**如何更改Home目录**

当Confluence启动的时候，会去`confluence-init.properties`文件中寻找Home目录的位置。想要更改Home目录，需要编辑`confluence-init.properties`文件的`confluence.home`属性。

<a class="reference-link" name="License%E6%89%80%E5%9C%A8%E7%9B%AE%E5%BD%95"></a>**License所在目录**

Confluence的License写在其Home目录（也叫confluecne安装目录）的这个文件里

```
confluence.cfg.xml
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img-blog.csdnimg.cn/20190718105357743.png)

到时候更新这里就行了。

当试用Confluence的时候，默认会使用内嵌的H2 Database

参考：[https://confluence.atlassian.com/doc/embedded-h2-database-145098285.html](https://confluence.atlassian.com/doc/embedded-h2-database-145098285.html)

是以一个home目录下的`database/h2db.mv.db`文件形式存在。

### <a class="reference-link" name="Confluence%E5%8E%86%E5%8F%B2%E6%BC%8F%E6%B4%9E"></a>Confluence历史漏洞

<a class="reference-link" name="%5BCVE-2019-3396%5D%E6%9C%AA%E6%8E%88%E6%9D%83RCE"></a>**[CVE-2019-3396]未授权RCE**

Confluence的漏洞最早引起国内安全研究者的较大关注应该是那次Confluence的未授权RCE `CVE-2019-3396`。

这个功能“小工具连接器”是Confluence自带的。在对某些链接的预览功能的请求中存在一个隐藏参数`_template`，攻击者可插入payload造成文件读取，某些版本可以加载指定的任意模板造成代码执行。

深入的分析可以参考Lucifaer大佬的博文：[https://lucifaer.com/2019/04/16/Confluence%20%E6%9C%AA%E6%8E%88%E6%9D%83RCE%E5%88%86%E6%9E%90%EF%BC%88CVE-2019-3396%EF%BC%89/](https://lucifaer.com/2019/04/16/Confluence%20%E6%9C%AA%E6%8E%88%E6%9D%83RCE%E5%88%86%E6%9E%90%EF%BC%88CVE-2019-3396%EF%BC%89/)

<a class="reference-link" name="%5BCVE-2019-3398%5D%E8%B7%AF%E5%BE%84%E7%A9%BF%E8%B6%8A%E6%BC%8F%E6%B4%9E"></a>**[CVE-2019-3398]路径穿越漏洞**

搭建Confluence漏洞环境的过程中发现还是比较方便的，界面风格也比较喜欢，于是我熟悉了它家产品的环境搭建流程，申请license的过程中注册了Atlassian的账号，没想到一两个星期之后的一个晚上凌晨1点，我刚准备睡觉，睡前看了一眼我的Gmail，发现Atlassian给我发了一封邮件通知说Confluence有一个严重漏洞`CVE-2019-3398`的安全公告：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01daa1560b0f680f14.png)

于是连夜起来用前几天刚搭好还热乎的环境调试到第二天早上终于把PoC调试出来了。

这个漏洞的触发和payload插入是分开了。需要先通过上传附件的功能将webshell的内容和希望上传到的地方（通过路径穿越）设置好，然后再通过“下载全部附件”的功能把webshell复制到预先设置好的路径下，加载webshell执行任意命令。由于附件文件是存在于Confluence的Home目录下，上传webshell成功的前提是需要知道Confluence的自带Tomcat路径和Confluence的Home路径之间的相对关系，这样才能准确地通过`../`把webshell复制到Tomcat路径下被加载。

详情参考：[https://xz.aliyun.com/t/4854](https://xz.aliyun.com/t/4854)

<a class="reference-link" name="%5BCVE-2019-3394%5D%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF%E6%B3%84%E9%9C%B2%E6%BC%8F%E6%B4%9E"></a>**[CVE-2019-3394]敏感信息泄露漏洞**

Confluence有一个”导出到Word”的功能。而导出的文件内容是基于当前被导出的文档内容的。而这个文档中可以包含文字也可以包含图片。当包含图片时，这个图片的路径可以由用户通过路径穿越指定，导致了这个漏洞的产生。（其实这个导出的文件并不是标准的doc格式，只是微软的Office刚好可以打开而已，如果是用其他客户端可能出错打不开。）<br>
这个漏洞跟CVE-2019-3398有两点类似。第一点，都是需要两次请求才能完成漏洞利用。都是需要先设置好payload，然后再通过下载操作或者导出操作触发漏洞。第二点是payload都是通过路径穿越指定的。

详情参考：[https://mp.weixin.qq.com/s/puRrvfqWFVKvQ0hOoVs8lQ](https://mp.weixin.qq.com/s/puRrvfqWFVKvQ0hOoVs8lQ)

<a class="reference-link" name="%5BCVE-2019-3395%5DWebDAV%E6%8F%92%E4%BB%B6%E6%9C%AA%E6%8E%88%E6%9D%83SSRF%E6%BC%8F%E6%B4%9E"></a>**[CVE-2019-3395]WebDAV插件未授权SSRF漏洞**

用一句话描述就是，当向受影响的Confluence请求`/webdav`开头的url（这个功能是WebDAV插件提供的）时，用户可以指定任意Host请求头（如果Confluence在其与用户之间没有使用Nginx做反向代理验证这个Host头），然后Confluence会向这个Host发起请求，并将这个请求的响应返回给客户端。

详情参考：[https://mp.weixin.qq.com/s/URDaO5xZISL0Bosh1nzM7A](https://mp.weixin.qq.com/s/URDaO5xZISL0Bosh1nzM7A)

以上就是今年Confluence爆出来的重要漏洞了，如果再往前追溯，还可以找到之前的这个信息泄露漏洞。

<a class="reference-link" name="%5BCVE-2017-7415%5D%E6%9C%AA%E6%8E%88%E6%9D%83%E4%BF%A1%E6%81%AF%E6%B3%84%E9%9C%B2%EF%BC%88%E4%BD%8E%E7%89%88%E6%9C%AC%EF%BC%89"></a>**[CVE-2017-7415]未授权信息泄露（低版本）**

这个漏洞源于未对REST接口的页面diff功能做权限校验，匿名用户即可访问。<br>
exploit：<br>[https://github.com/allyshka/exploits/blob/c1f5f0dfa2494001e7c3cffabfbf0219b0e35e08/confluence/CVE-2017-7415/README.md](https://github.com/allyshka/exploits/blob/c1f5f0dfa2494001e7c3cffabfbf0219b0e35e08/confluence/CVE-2017-7415/README.md)

影响范围：

6.0.0 &lt;= version &lt; 6.0.7

cnnvd描述：

> Atlassian Confluence 6.0.7之前的6.x版本中存在安全漏洞。远程攻击者可利用该漏洞绕过身份验证，读取任意日志或页面。

直接一个请求：

```
/rest/tinymce/1/content/&lt;pageId&gt;/draft/diff
```

可访问任意博客/Pages页面。

比如：

这个页面：[http://cqq.com:8090/pages/viewpage.action?pageId=65546](http://cqq.com:8090/pages/viewpage.action?pageId=65546)

[![](https://p1.ssl.qhimg.com/t012bc3a6c04e17e052.png)](https://p1.ssl.qhimg.com/t012bc3a6c04e17e052.png)

本来需要登录才能访问

[![](https://p4.ssl.qhimg.com/t01d49db361e91c92e3.png)](https://p4.ssl.qhimg.com/t01d49db361e91c92e3.png)

而如果通过这个url去访问：

[http://cqq.com:8090/rest/tinymce/1/content/65546/draft/diff](http://cqq.com:8090/rest/tinymce/1/content/65546/draft/diff)

可以直接访问到

[![](https://p4.ssl.qhimg.com/t012b633e91901c5f32.png)](https://p4.ssl.qhimg.com/t012b633e91901c5f32.png)

<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E8%B0%83%E8%AF%95"></a>漏洞调试

查看代码：`confluence-6.0.6/plugins-osgi-cache/transformed-plugins/confluence-editor-6.0.6_1487721990000.jar!/com/atlassian/confluence/tinymceplugin/rest/PageResource#getDraftDiff`<br>
可以发现这个路径是允许匿名用户访问的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f6f244c3f2e31adf.png)

<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>漏洞修复

使用6.0.7版本进行测试。

不带Cookie的情况下，发现页面404了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01188ac678b0ceb936.png)

跟到对应的代码`atlassian-confluence-6.0.7/confluence/WEB-INF/atlassian-bundled-plugins/confluence-editor-6.0.7.jar!/com/atlassian/confluence/tinymceplugin/rest/PageResource#getDraftDiff`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d9ff1a55ab8a9e92.png)

增加了权限校验。若当前用户没有编辑当前页面的权限，则直接响应404。



## Bitbucket

### <a class="reference-link" name="Bitbucket%E5%8E%86%E5%8F%B2%E6%BC%8F%E6%B4%9E"></a>Bitbucket历史漏洞

Bitbucket最近比较重要的是以下两个漏洞。CVE-2019-15000 git的参数注入漏洞，和CVE-2019-3397。

<a class="reference-link" name="%5BCVE-2019-15000%5D%E5%8F%82%E6%95%B0%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E"></a>**[CVE-2019-15000]参数注入漏洞**

Bitbucket最近的漏洞不多，而且我对它也不是很熟悉。最近出的比较严重的漏洞还是`CVE-2019-15000`， 由于REST接口的diff功能未对`--`这种对于git命令有特殊意义的字符进行过滤，导致了git diff的参数注入，至少可以读取敏感文件的效果。详情参考：[https://mp.weixin.qq.com/s/3J-lA0CQylrq2ZY3ZEESiQ](https://mp.weixin.qq.com/s/3J-lA0CQylrq2ZY3ZEESiQ)

<a class="reference-link" name="%5BCVE-2019-3397%5D"></a>**[CVE-2019-3397]**

这个漏洞是由rips发现并分析的。利用这个漏洞需要管理员权限。<br>
详情参考：[https://blog.ripstech.com/2019/bitbucket-path-traversal-to-rce/](https://blog.ripstech.com/2019/bitbucket-path-traversal-to-rce/)

Bitbucket的漏洞可以跟gitlab等git服务解决方案的漏洞进行对比。如果今后它出漏洞很可能还是跟git参数命令相关的。<br>
下面提供一些git参数注入漏洞的例子：

<a class="reference-link" name="git%20ls-remote"></a>**git ls-remote**

比如Jenkins的Git Client插件的命令执行漏洞`CVE-2019-10392`，

```
git ls-remote -h --upload-pack=calc.exe HEAD
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d57315da44b239e7.png)

这个也是git ls-remote命令的参数注入漏洞：

[https://snyk.io/vuln/npm:git-ls-remote:20160923](https://snyk.io/vuln/npm:git-ls-remote:20160923)

<a class="reference-link" name="git%20grep"></a>**git grep**

```
git grep --open-files-in-pager=calc.exe master
```

参考：[https://www.leavesongs.com/PENETRATION/escapeshellarg-and-parameter-injection.html](https://www.leavesongs.com/PENETRATION/escapeshellarg-and-parameter-injection.html)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018493474aad0d0339.png)

感觉好几个是跟pager相关的。pager是用户指定的一个外部的执行diff、cat等功能的可执行文件的路径。

但是我在git log和git diff命令下没找到。

另外又看到几个git的参数注入的：

[https://staaldraad.github.io/post/2019-07-16-cve-2019-13139-docker-build/](https://staaldraad.github.io/post/2019-07-16-cve-2019-13139-docker-build/)

使用docker build命令的时候：

PoC：

```
docker build "git@g.com/a/b#--upload-pack=sleep 5;:"
```

实际上执行的命令是：

```
$ git init
$ git remote add git@g.com/a/b
$ git fetch origin "--upload-pack=sleep 5; git@g.com/a/b"
```

另外还有一个git submodule的命令执行：

```
https://staaldraad.github.io/post/2018-06-03-cve-2018-11235-git-rce/
```

利用git hooks实现路径穿越。

less读取文件：

`shift + e`，然后输入文件名即可读取这个文件。

[![](https://p2.ssl.qhimg.com/t016eace2ef4daad667.png)](https://p2.ssl.qhimg.com/t016eace2ef4daad667.png)

less执行命令：

[![](https://p2.ssl.qhimg.com/t0176ff5cb0acdee3ae.png)](https://p2.ssl.qhimg.com/t0176ff5cb0acdee3ae.png)

参考：

[https://docs.ioin.in/writeup/evi1cg.me/_archives_CVE_2017_8386_html/index.html](https://docs.ioin.in/writeup/evi1cg.me/_archives_CVE_2017_8386_html/index.html)

比如`git-receive-pack --help`命令就用到了less命令，可以用来读取文件和执行命令。

这个产品的漏洞挖掘需要对git的各种参数及其使用场景非常熟悉或有过深入的研究。可以从以下资料展开研究：
- [对基于Git的版本控制服务的通用攻击面的探索](https://data.hackinn.com/ppt/2019%E7%AC%AC%E4%BA%94%E5%B1%8A%E4%BA%92%E8%81%94%E7%BD%91%E5%AE%89%E5%85%A8%E9%A2%86%E8%A2%96%E5%B3%B0%E4%BC%9A/%E5%AF%B9%E5%9F%BA%E4%BA%8EGit%E7%9A%84%E7%89%88%E6%9C%AC%E6%8E%A7%E5%88%B6%E6%9C%8D%E5%8A%A1%E7%9A%84%E9%80%9A%E7%94%A8%E6%94%BB%E5%87%BB%E9%9D%A2%E7%9A%84%E6%8E%A2%E7%B4%A2.pdf)
- [hackerone上公开的gitlab漏洞](https://hackerone.com/reports/658013)
- [git命令文档说明](https://git-scm.com/docs/)


## Atlassian产品环境搭建

Atlassian家产品的环境搭建都比较类似。会自带一个Tomcat，然后具体产品作为其一个webapp存在。Github上有一份[带dockerfile的环境](https://github.com/TommyLau/docker-atlassian)，基本上Atlassian产品的环境都有了。

如果自己在Mac上或者Linux上搭建环境，可以用以下方式，以Jira为例，Confluence类似。找到具体的产品和版本号即可。

```
$ wget https://product-downloads.atlassian.com/software/jira/downloads/atlassian-jira-software-7.13.0.tar.gz
$ tar zxf atlassian-jira-software-7.13.0.tar.gz
$ cd atlassian-jira-software-7.13.0-standalone/
$ vi atlassian-jira/WEB-INF/classes/jira-application.properties #设置jira的Home目录，这里我设置为
#/home/cqq/jiraHome
$ mkdir /home/cqq/jiraHome  # 作为jira的安装目录(不手动创建目录也行，jira会自动创建)
$ conf/server.xml #修改端口，这里我改成8091，与Confluence的8090接近
$ bin/start-jira.sh #启动jira
```

若想调试，需要修改`bin/setenv.sh`:

```
CATALINA_OPTS="-Xrunjdwp:transport=dt_socket,suspend=n,server=y,address=12346 $`{`CATALINA_OPTS`}`"  # for debug

CATALINA_OPTS="$`{`GC_JVM_PARAMETERS`}` $`{`CATALINA_OPTS`}`"
export CATALINA_OPTS
```

如果觉得卡可以把允许的内存设置的大一些：

```
JVM_MINIMUM_MEMORY="4096m"
JVM_MAXIMUM_MEMORY="4096m"
```

安装时会选择数据库，如果图方便可以选择内置的h2数据库，也可以自己创建好对应的数据库之后，让Jira连接它即可。我尝试使用了postgresql数据库，可以参考：[https://blog.csdn.net/caiqiiqi/article/details/89021367](https://blog.csdn.net/caiqiiqi/article/details/89021367)

Bitbucket的设置调试和环境变量稍微有点区别：

下载：[https://product-downloads.atlassian.com/software/stash/downloads/atlassian-bitbucket-6.1.1.zip](https://product-downloads.atlassian.com/software/stash/downloads/atlassian-bitbucket-6.1.1.zip)

解压之后设置好`JAVA_HOME`环境变量，以及`BITBUCKET_HOME`环境变量，

[![](https://p4.ssl.qhimg.com/t018a20ac8da6300d39.png)](https://p4.ssl.qhimg.com/t018a20ac8da6300d39.png)

这个是到时候bitbucket的数据被安装到的目录。

```
vi bin/set-bitbucket-home.sh #设置JAVA_HOME，以及BITBUCKET_HOME环境变量
vi bin/_start-webapp.sh
# DEBUG="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=12346"
bin/start-bitbucket.sh  # 启动Bitbucket
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013f9563daece5049b.png)

Jira、Confluence、Bitbucket的历史版本下载：
- [https://www.atlassian.com/software/jira/download-archives](https://www.atlassian.com/software/jira/download-archives)
- [https://www.atlassian.com/software/confluence/download-archives](https://www.atlassian.com/software/confluence/download-archives)
- [https://www.atlassian.com/software/bitbucket/download-archives](https://www.atlassian.com/software/bitbucket/download-archives)
可以选择安装程序进行安装，也可以选择压缩文件解压到本地。

在安装过程中需要输入相应的licnese，如果只是用于测试，可以到Atlassian选择对应的产品，申请试用的license，有效期是一个月。

[https://my.atlassian.com/license/evaluation](https://my.atlassian.com/license/evaluation)



## Atlassian产品最新漏洞获取方式

Atlassian产品主要发布在官方公告和issues页面中。

官方公告一般发高危及以上的漏洞，其他的漏洞会先在issues里提交然后分配CVE编号(安全公告一般也是从issues中来的)。一般监控官方公告页面就可以了。如果想获取最新的可能的漏洞信息，而又不担心误报的话，可以监控issues页面，或者跟着NVD的邮件列表看看有没有Atlassian产品相关的。
<li>Jira官方公告页面：<br>[https://confluence.atlassian.com/jira/security-advisories-112853939.html](https://confluence.atlassian.com/jira/security-advisories-112853939.html)
</li>
<li>Confluence官方公告页面：<br>[https://confluence.atlassian.com/doc/confluence-security-overview-and-advisories-134526.html](https://confluence.atlassian.com/doc/confluence-security-overview-and-advisories-134526.html)
</li>
<li>Bitbucket官方公告页面：<br>[https://confluence.atlassian.com/bitbucketserver/bitbucket-server-security-advisories-776640597.html](https://confluence.atlassian.com/bitbucketserver/bitbucket-server-security-advisories-776640597.html)
</li>
issues页面:
- [https://jira.atlassian.com/browse/JRASERVER-69858?filter=13085](https://jira.atlassian.com/browse/JRASERVER-69858?filter=13085)


## Atlassian产品漏洞应急

根据这段时间跟进Atlassian产品的漏洞的经验，当一个jira或者confluence的cve出来的时候，可能当时只有漏洞描述，没有复现步骤，需要自己定位到漏洞点。

我一般是通过在相应产品目录下各种文本文件(包括jar包)搜索关键词(忽略大小写)

```
grep -rni "&lt;关键词&gt;或者关键&lt;path&gt;或者&lt;类名&gt;或者&lt;方法名&gt;" *
```

或者在其各种jar包中搜索关键字：

```
grep -rni "关键词" `find . -name *.jar`
```

或者通过strings工具判断某二进制文件中是否包含某关键词字符串。

可能在`WEB-INF/web.xml`中找到url对应的处理类：

比如我通过官方的描述，知道了CVE-2019-8446的触发点是`/rest/issueNav/1/issueTable`，那我就搜`/rest/issueNav`，然后在`WEB-INF/web.xml`中找到了对应的处理类/过滤器名

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010ccbb03544449f4a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0134c66d2c978bc22b.png)

然后根据过滤器的名字搜索类

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01578d4b04d03921cb.png)

再根据类名定位到具体的文件中，可能是jar包形式，也可能是.class文件形式。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01325301687ac66275.png)

然后再去IDEA中下断点。

还有一个办法就是直接去日志里查调用栈（如果有报错的话）

如果只知道一个关键方法的名字，可以先搜它在哪个jar包中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b30a6c9b81741df7.png)

确定jar包之后， 再用反编译工具将jar包反编译你成java代码，再搜索，确定其具体的路径，定位到具体的文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0193394e065c0e1781.png)



## 参考
- [Confluence中文版文档](https://www.cwiki.us/display/CONFLUENCEWIKI)
- [There is a proxy in your Atlassian Product! (CVE-2017-9506)](http://dontpanic.42.nl/2017/12/there-is-proxy-in-your-atlassian.html)
- [Jira Architecture overview](https://developer.atlassian.com/server/jira/platform/architecture-overview/)
- [Jira相关背景知识](https://blog.csdn.net/caiqiiqi/article/details/89927578)
- [Confluence相关背景知识](https://blog.csdn.net/caiqiiqi/article/details/96426205)
- [Bitbucket相关](https://blog.csdn.net/caiqiiqi/article/details/102799830)
- [Vulnerability Spotlight: Multiple vulnerabilities in Atlassian Jira](https://blog.talosintelligence.com/2019/09/vuln-spotlight-atlassian-jira-sept-19.html)
- [BitBucket服务器参数注入漏洞(CVE-2019-15000)](https://mp.weixin.qq.com/s/3J-lA0CQylrq2ZY3ZEESiQ)
- [Jira未授权SSRF漏洞(CVE-2019-8451)](https://mp.weixin.qq.com/s/_Tsq9p1pQyszJt2VaXd61A)
- [Jira未授权服务端模板注入漏洞(CVE-2019-11581)](https://mp.weixin.qq.com/s/d2yvSyRZXpZrPcAkMqArsw)
- [Confluence路径穿越漏洞(CVE-2019-3398)](https://xz.aliyun.com/t/4854)
- [Confluence未授权模板注入/代码执行(CVE-2019-3396)](https://caiqiqi.github.io/2019/11/03/Confluence%E6%9C%AA%E6%8E%88%E6%9D%83%E6%A8%A1%E6%9D%BF%E6%B3%A8%E5%85%A5-%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C-CVE-2019-3396/)
- [Confluence 未授权RCE分析（CVE-2019-3396）](https://lucifaer.com/2019/04/16/Confluence%20%E6%9C%AA%E6%8E%88%E6%9D%83RCE%E5%88%86%E6%9E%90%EF%BC%88CVE-2019-3396%EF%BC%89/)
- [Confluence Pre-Auth SSRF(CVE-2019-3395)](https://mp.weixin.qq.com/s/URDaO5xZISL0Bosh1nzM7A)
- [Confluence敏感信息泄露漏洞(CVE-2019-3394)](https://mp.weixin.qq.com/s/puRrvfqWFVKvQ0hOoVs8lQ)
- [Atlassian products in Docker](https://github.com/TommyLau/docker-atlassian)
- [http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201909-897](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201909-897)
- [http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201908-2216](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201908-2216)
- [http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201909-903](http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201909-903)
- [CVE-2017-9506 – SSRF](https://github.com/random-robbie/Jira-Scan)