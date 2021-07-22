> 原文链接: https://www.anquanke.com//post/id/147455 


# GraphQL安全总结与测试技巧


                                阅读量   
                                **272210**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://blog.doyensec.com/
                                <br>原文地址：[https://blog.doyensec.com/2018/05/17/graphql-security-overview.html](https://blog.doyensec.com/2018/05/17/graphql-security-overview.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01c3e425090c9ae19c.jpg)](https://p0.ssl.qhimg.com/t01c3e425090c9ae19c.jpg)



## 前言

在当今GraphQL技术越来越受欢迎的情况下，我们总结了一些关于它的常见安全错误和测试要点



## 什么是GraphQL

GraphQL是由Facebook开发并于2015年公开发布的数据查询语言。它是REST API的替代品。<br>
虽然你可能很少在网站中看见GraphQL，但很可能你已经在使用它了，因为一些大的科技巨头都已在使用，例如Facebook，GitHub，Pinterest, Twitter, HackerOne甚至更多。

### <a class="reference-link" name="%E5%87%A0%E4%B8%AA%E6%8A%80%E6%9C%AF%E5%85%B3%E9%94%AE%E7%82%B9"></a>几个技术关键点

1.GraphQL给API提供了完整的数据和可理解的描述，并使客户能够精确地查询他们的需求。查询的结果总是你想要的。

2.典型的REST API需要从多个URL进行加载，但GraphQL API可以在单个请求中获取应用程序所需的所有数据。

3.GraphQL API根据类型和字段进行组织，而不是终端。您可以从单个终端访问所有数据的全部功能。

4.GraphQL是强类型的，以确保应用程序只查询可能出现的情况并提供明确而有帮助的错误。

5.新的字段和类型可以添加到GraphQL API，而不会影响现有的查询。不使用的字段可以被工具弃用并隐藏。

### <a class="reference-link" name="%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86"></a>工作原理

在开始深入研究GraphQL的安全领域之前，我们简要回顾它的工作原理。其官方文档写得很好。<br>
一个GraphQL查询如下所示：

<a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E7%9A%84GraphQL%E6%9F%A5%E8%AF%A2"></a>**基本的GraphQL查询**

```
query`{`
    user`{`
        id
        email
        firstName
        lastName
    `}`
`}`
```

<a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E7%9A%84GraphQL%E5%93%8D%E5%BA%94"></a>**基本的GraphQL响应**

响应结果则是json类型：

```
`{`
    "data": `{`
        "user": `{`
            "id": "1",
            "email": "paolo@doyensec.com",
            "firstName": "Paolo",
            "lastName": "Stagno"
        `}`
    `}`
`}`
```



## 安全测试技巧

由于Burp Suite不能够解析GraphQL语法，因此我建议使用graphql-ide，这是一个基于Electron的应用程序，允许您编辑和发送请求至GraphQL终端;<br>
我还编写了一个小python脚本：GraphQL_Introspection.py，它列举了一个GraphQL端点，以便提取文档。该脚本对于检查GraphQL模式寻找信息泄露，隐藏数据和不可访问的字段非常有用。<br>
该工具将生成类似于以下内容的HTML报告：<br>[![](https://p2.ssl.qhimg.com/t011493687277778696.png)](https://p2.ssl.qhimg.com/t011493687277778696.png)<br>
作为一个渗透者，我建议寻找发送给<br>`/graphql`或`/graphql.php`的请求，因为这些是通常的GraphQL终端的名称; 您还应搜索`/ graphiql`，`graphql/console/`，在线的可与后端交互的GraphQL IDE，以及`/graphql.php?debug=1`（带有附加错误报告的调试模式），因为它们可能会被开发人员留下，并且开放。

在测试应用程序时，验证是否可以在没有一般授权令牌标头的情况下发出请求：<br>[![](https://p0.ssl.qhimg.com/t015effebdc2ccb5f16.png)](https://p0.ssl.qhimg.com/t015effebdc2ccb5f16.png)

由于GraphQL框架没有提供任何数据保护的手段，因此需要开发人员按照文档中的说明实施访问控制：

```
“However, for a production codebase, delegate authorization logic to the business logic layer”.
```

这就可能会出错，因此验证是否可以没有通过正确的认证或者授权而从服务器请求整个底层数据库非常的重要。

### <a class="reference-link" name="%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE"></a>未授权访问

当使用GraphQL构建应用程序时，开发人员必须将数据映射到他们选择的数据库技术中进行查询。这非常容易引入安全漏洞，导致访问控制被破坏，不安全的对象直接引用甚至SQL或NoSQL进行注入。<br>
作为攻击实现的一个示例，以下请求/响应表明我们可以获得平台的任何用户的数据（通过ID参数循环访存），同时转储密码哈希值：<br>
查询：

```
query`{`
    user(id: 165274)`{`
        id
        email
        firstName
        lastName
        password
    `}`
`}`
```

响应

```
`{`
    "data": `{`
        "user": `{`
            "id": "165274",
            "email": "johndoe@mail.com",
            "firstName": "John",
            "lastName": "Doe"
            "password": "5F4DCC3B5AA765D61D8327DEB882CF99"
        `}`
    `}`
`}`
```

### <a class="reference-link" name="%E4%BF%A1%E6%81%AF%E6%B3%84%E9%9C%B2"></a>信息泄露

另一件你需要去核对的点是当你引入非法字符查询时，是否会引起信息泄露

```
`{`
    "errors": [
        `{`
            "message": "Invalid ID.",
            "locations": [
                `{`
                    "line": 2,
                    "column": 12
                `}`
                "Stack": "Error: invalid IDn at (/var/www/examples/04-bank/graphql.php)n"
                  ]
        `}`
    ]
`}`
```

### <a class="reference-link" name="GraphQL%20SQL%E6%B3%A8%E5%85%A5"></a>GraphQL SQL注入

即使GraphQL是强类型的，SQL/NoSQL注入仍然是可能的，因为GraphQL只是客户端应用程序和数据库之间的一个层。这个问题可能存在于为了查询数据库而从GraphQL查询中获取变量的层中，未正确清理的变量导致较为简单的SQL注入。在Mongodb的情况下，NoSQL注入可能并不那么简单，因为我们不能控制类型（例如将字符串转换为数组，请参阅PHP MongoDB注入）。

```
mutation search($filters Filters!)`{`
    authors(filter: $filters)
    viewer`{`
        id
        email
        firstName
        lastName
    `}` 
`}`

`{`
    "filters":`{`
        "username":"paolo' or 1=1--"
        "minstories":0
    `}`
`}`
```

### <a class="reference-link" name="%E5%B5%8C%E5%A5%97%E6%9F%A5%E8%AF%A2"></a>嵌套查询

谨防嵌套查询！它们可以允许恶意客户端通过过度复杂的查询来执行DoS（拒绝服务）攻击，这些查询会占用服务器的所有资源：

```
query `{`
 stories`{`
  title
  body
  comments`{`
   comment
   author`{`
    comments`{`
     author`{`
      comments`{`
       comment
       author`{`
        comments`{`
         comment
         author`{`
          comments`{`
           comment
           author`{`
            name
           `}`
          `}`
         `}`
        `}`
       `}`
      `}`
     `}`
    `}`
   `}`
  `}`
 `}`
`}`
```

针对DoS的简单修复方式可以是设置超时，最大深度或查询复杂度阈值。<br>
请记住，在PHP GraphQL实现中：

```
1.复杂性分析默认是禁用的
2.限制查询深度默认情况下处于禁用状态
3.Introspection是默认启用的。这意味着任何人都可以通过发送包含元字段类型和模式的特殊查询来完整描述您的模式
```



## 结尾

GraphQL是一项新的有趣的技术，可用于构建安全的应用程序。但由于开发人员负责实施访问控制，因此应用程序很容易出现经典的Web漏洞，如Broken Access Controls，不安全的直接对象引用，跨站点脚本（XSS）和经典注入漏洞。<br>
就像任何技术一样，基于GraphQL的应用程序可能会像这个实际例子那样容易出现开发实现错误：

```
“By using a script, an entire country’s (I tested with the US, the UK and Canada) possible number combinations can be run through these URLs, and if a number is associated with a Facebook account, it can then be associated with a name and further details (images, and so on).”
```

[@voidsec](https://github.com/voidsec)



## 参考链接

[https://en.wikipedia.org/wiki/GraphQL](https://en.wikipedia.org/wiki/GraphQL)<br>[https://dev-blog.apollodata.com/the-concepts-of-graphql-bc68bd819be3](https://dev-blog.apollodata.com/the-concepts-of-graphql-bc68bd819be3)<br>[https://graphql.org/learn/](https://graphql.org/learn/)<br>[https://www.howtographql.com/](https://www.howtographql.com/)<br>[https://www.hackerone.com/blog/the-30-thousand-dollar-gem-part-1](https://www.hackerone.com/blog/the-30-thousand-dollar-gem-part-1)<br>[https://hackerone.com/reports/291531](https://hackerone.com/reports/291531)<br>[https://labs.detectify.com/2018/03/14/graphql-abuse/](https://labs.detectify.com/2018/03/14/graphql-abuse/)<br>[https://medium.com/the-graphqlhub/graphql-and-authentication-b73aed34bbeb](https://medium.com/the-graphqlhub/graphql-and-authentication-b73aed34bbeb)<br>[http://www.petecorey.com/blog/2017/06/12/graphql-nosql-injection-through-json-types/](http://www.petecorey.com/blog/2017/06/12/graphql-nosql-injection-through-json-types/)<br>[https://webonyx.github.io/graphql-php/](https://webonyx.github.io/graphql-php/)
