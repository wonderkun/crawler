> 原文链接: https://www.anquanke.com//post/id/194271 


# GitLab：通过路径遍历搞定管理员账户


                                阅读量   
                                **1258700**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者gitlab，文章来源：about.gitlab.com
                                <br>原文地址：[https://about.gitlab.com/blog/2019/11/29/shopping-for-an-admin-account/](https://about.gitlab.com/blog/2019/11/29/shopping-for-an-admin-account/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01c9c47ed9201ce766.jpg)](https://p1.ssl.qhimg.com/t01c9c47ed9201ce766.jpg)



## 0x00 前言

随着规模的不断扩大，现在大多数web应用都不再单打独斗，需要依赖其他应用来实现其完整功能。根据对端API的具体情况，我们可以通过各种方式来调用其他web应用。在本文中，我们将讨论web应用对REST API的调用以及存在的一些安全风险。

Representational State Transfer（表述性状态传递，简称[REST](https://de.wikipedia.org/wiki/Representational_State_Transfer)）是基于HTTP的一种协议，可以使用各种HTTP方法（如GET/POST/PUT/DELETE）来与远程API端点交互。

两个web应用通过REST交互时可能存在一些问题，下面我们来看一个具体案例（GitLab），了解其中的安全风险。



## 0x01 GitLab客户登录口

GitLab通过[customers.gitlab.com](https://customers.gitlab.com/)对外提供各种增值服务，比如GitLab的订阅服务（subscription）以及CI分钟数购买等。`customers`源码不对外公开，因此下面我会使用一些相关的代码片段来演示问题所在。

`customers`站点需要与`gitlab.com` API交互，以便`gitlab.com`获取相关信息（比如客户已购买的CI分钟数）。这里`customers`会使用[HTTParty](https://github.com/jnunemaker/httparty)向`gitlab.com` API发起HTTP请求。

PUT请求如下所示：

```
def put(path, *args)
      options = valid_options(args)

      HTTParty.put(full_url(path), options)
    end

private

    def full_url(path)
      URI.join(BASE_URL, path).to_s
    end
```

对`put`方法的调用如下所示：

```
response = Client::GitlabApp.put("/api/v4/namespaces/#`{`@namespace_id`}`", body: @attrs.to_json, token: API_TOKEN)
```

在上述代码中，`Client::GitlabApp`用来更新`gitlab.com`上的订阅。当客户将订阅从一个命名空间移动到另一个命名空间时，就会执行该操作。用户可以控制`[@namespace_id](https://github.com/namespace_id)`参数，但无法控制PUT操作的payload（即`body: [@attrs](https://github.com/attrs).to_json`）。`API_TOKEN`为`gitlab.com` API对应的访问令牌，具备`admin`权限。这里调用`Client::GitlabApp.put`时存在安全隐患：攻击者可以将`[@namespace_id](https://github.com/namespace_id)`参数的值设置为`../other/path`，遍历`gitlab.com` API上的路径，从而可以跳出`/api/v4/namespace/`的限制，访问其他API端点。

这种类型的攻击称为路径（或者目录）遍历攻击，是非常常见的一种问题。当代码中使用了路径参数时（如文件系统访问或者解压归档文件时），就有可能发生这种情况。



## 0x02 攻击影响

当我们考虑该漏洞的影响以及利用方式时，情况会变得更有趣一些。由于我们无法控制PUT操作的payload（`[@attrs](https://github.com/attrs).to_json`），大家可能直观上会认为该遍历漏洞的影响范围非常有限。在REST中，PUT操作用来更新已有的资源。通常情况下，待更新的资源属性会通过HTTP请求的body段来发送（这里也就是经过JSON编码的`[@attrs](https://github.com/attrs)`）。

`gitlab.com`上的API端点采用[Grape](http://www.ruby-grape.org/)实现，在[参数处理](https://github.com/ruby-grape/grape#parameters)过程中，任何PUT/POST参数会与基于路径的GET参数合并，生成`params`哈希。这意味着除了PUT操作中的`body: [@attrs](https://github.com/attrs).to_json` payload之外，我们还可以使用未经过滤的`[@namespace_id](https://github.com/namespace_id)`参数。我们不仅可以使用`../`方式遍历API端点，还可以将`?some_attribute=our_value`附加到`[@namespace_id](https://github.com/namespace_id)`，从而在API端点上注入属性。因此除了路径遍历之外，我们还可以在API端点上实现任意参数注入。将这两点结合起来后，我们就可以发起威力巨大的攻击。



## 0x03 漏洞利用

如前文所述，我们已经可以在`gitlab.com` API上使用`admin`令牌在请求中实现路径遍历及属性注入，因此我们已经掌握了非常强大且通用的攻击方法。当我们在GitLab的`staging`环境中调查及验证该问题时，发现可以通过这种方式将常规账户提升至`admin`。实际使用的payload非常简单：`../users/&lt;userID&gt;?admin=true`，该payload会向`https://gitlab.com/api/v4/users/&lt;userID&gt;?admin=true`地址发起PUT请求。

在`staging`环境中，漏洞利用payload如下所示（使用Chrome开发者工具）：

[![](https://p0.ssl.qhimg.com/t01c0e9c250fe5eb31d.png)](https://p0.ssl.qhimg.com/t01c0e9c250fe5eb31d.png)

攻击成功后，我们能看到一个专属图标，此时目标账户就可以访问`admin`页面：

[![](https://p2.ssl.qhimg.com/t01a39bbbfdc5ad2f56.png)](https://p2.ssl.qhimg.com/t01a39bbbfdc5ad2f56.png)

这里我们使用的是GitLab Bronze订阅的“Change linked Group”功能来完成修改操作。这种攻击方式也可以配合已购买的CI分钟来使用，我们只需要花费8美元，再配合数次点击操作，就能变成`gitlab.com`上的`admin`。



## 0x04 缓解措施

我们的[Fulfillment Backend Team](https://about.gitlab.com/handbook/engineering/development/growth/be-fulfillment/)迅速解决了该问题。现在应用会将`[@namespace_id](https://github.com/namespace_id)`参数限制为数字值，此外我们还采取了其他纵深防御措施来防御路径遍历及类似攻击。



## 0x05 总结

现代应用在通过API调用使用后端服务时，可能会出现一些安全风险，本文就是一个非常典型的案例。将路径遍历漏洞与API调用中的属性注入技术结合起来后，攻击者就可以造成非常严重的影响。即便该问题位于`customers.gitlab.com`的代码库中，攻击者还是可以利用该缺陷在`gitlab.com`上提升用户权限。
