> 原文链接: https://www.anquanke.com//post/id/245538 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 - 访问控制漏洞与越权专题


                                阅读量   
                                **37798**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t015d87b0e62a79b765.png)](https://p2.ssl.qhimg.com/t015d87b0e62a79b765.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 服务器端漏洞篇介绍

> burp官方说他们建议初学者先看服务器漏洞篇，因为初学者只需要了解服务器端发生了什么就可以了



## 服务器端漏洞篇 – 访问控制漏洞与越权专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%EF%BC%9F"></a>什么是访问控制？

访问控制，又叫授权，就是明确你有做哪些事的权限，在Web应用的上下文中，访问控制取决于身份验证和会话管理
- 身份验证(authentication) – 确认你是不是你
- 会话管理(session management) – 管理同一用户正在发出哪些HTTP请求
- 访问控制(authorization) – 明确你能不能做这个能不能做那个
访问控制的漏洞的重点不在于实现访问控制策略的技术手段，而是访问控制策略制定的严谨性，往往相关的漏洞都是因为访问控制策略制定上的疏忽导致在利用技术手段实现它的时候会让攻击者利用这个疏忽进行访问控制策略的破坏

### <a class="reference-link" name="%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%E5%AE%89%E5%85%A8%E6%A8%A1%E5%9E%8B"></a>访问控制安全模型

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%E5%AE%89%E5%85%A8%E6%A8%A1%E5%9E%8B%EF%BC%9F"></a>什么是访问控制安全模型？

所谓模型，就是通过长时间的沉淀归纳出的一些规范、模式之类的产物，那么什么是访问控制安全模型呢？就是出于安全的目的设计的用于规范访问控制策略的模型，下面我们来介绍几种比较成熟的访问控制安全模型

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%8C%96%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6"></a>程序化访问控制

程序化访问控制就是利用一个权限矩阵来存储用户权限，然后再把这个矩阵存放在数据库中，因为是利用矩阵这种数据结构存储权限，所以它可以存储角色、组、单个用户的权限，可以做到很细致的访问控制。

### <a class="reference-link" name="%E8%87%AA%E4%B8%BB%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6(DAC)"></a>自主访问控制(DAC)

自主访问控制是资源所有者可以自主定义资源的访问控制权限，因为每个资源的访问控制权限都要所有者进行配置，所以这种模型设计上可能会非常复杂

### <a class="reference-link" name="%E5%BC%BA%E5%88%B6%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6(MAC)"></a>强制访问控制(MAC)

不同于DAC，MAC是所有资源的访问控制权限均统一分配，任何用户都无法对其进行配置，这类模型一般应用于安全级别非常高的应用系统如军事，能源等关键基础设施领域。

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E8%A7%92%E8%89%B2%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6(RBAC)"></a>基于角色访问控制(RBAC)

应用系统将用户根据职责划分成不同的角色或用户组中，然后将资源的访问控制权限分配给用户组就可以了，如果需要取消某个用户的访问控制权限，直接将该用户踢出角色或用户组即可，当应用系统角色数量恰到好处时，该模型是最有效的。

### <a class="reference-link" name="%E4%BB%8E%E7%94%A8%E6%88%B7%E8%A7%92%E5%BA%A6%EF%BC%8C%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%E5%8F%AF%E4%BB%A5%E5%88%86%E4%B8%BA%E5%93%AA%E5%87%A0%E7%B1%BB%EF%BC%9F"></a>从用户角度，访问控制可以分为哪几类？

从用户角度，访问控制可以分为
- 垂直访问控制
- 水平访问控制
- 上下文相关访问控制
### <a class="reference-link" name="%E5%9E%82%E7%9B%B4%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6"></a>垂直访问控制

大家先理解一下这个垂直啊，就是上下级嘛，所以该类访问控制主要是限制对不同类型用户之间的访问控制权限，比如管理员可以创建用户啊，修改应用系统配置啊，而普通用户不行，通常情况下，采取这种访问控制策略可以实现职责分离及最小特权。

### <a class="reference-link" name="%E6%B0%B4%E5%B9%B3%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6"></a>水平访问控制

区别于垂直，水平的概念就是同一类型的用户之间的访问控制权限，比如我只能看到我自己的账号信息，你只能看到你的。

### <a class="reference-link" name="%E4%B8%8A%E4%B8%8B%E6%96%87%E7%9B%B8%E5%85%B3%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6"></a>上下文相关访问控制

上下文相关，也比较好理解，就是应用系统根据应用系统的状态或者与用户之间的交互对访问控制权限做限制，该访问控制策略可以应用于防止以错乱的顺序执行功能。

### <a class="reference-link" name="%E5%9E%82%E7%9B%B4%E6%8F%90%E6%9D%83"></a>垂直提权

垂直越权就是当前用户可以使用其他类型用户的功能，比如普通用户可以使用管理员的功能。

### <a class="reference-link" name="%E6%9C%AA%E5%8F%97%E4%BF%9D%E6%8A%A4%E7%9A%84%E5%8A%9F%E8%83%BD"></a>未受保护的功能

有时候应用系统并未对一些敏感页面做访问控制限制，就可能导致垂直提权，比如管理界面只会通过管理员账户界面链接到，但是如果我们已经知道了管理界面的路径，我们可以直接用普通用户身份进入管理界面，那么我们怎么知道一些敏感路径呢，可以从一些文件中泄漏出来，比如robots.txt等。<br>
因为很多敏感路径可以通过目录扫描的方式获得，所以有些应用程序将这些路径修改为不易猜解的路径，但是他们会将入口点放在前端文件中，这让这种看似安全的防护手段形同虚设。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E6%9C%AA%E5%8F%97%E4%BF%9D%E6%8A%A4%E7%9A%84%E7%AE%A1%E7%90%86%E5%91%98%E5%8A%9F%E8%83%BD"></a>配套靶场1：未受保护的管理员功能

因为刚讲了这个知识点嘛，就访问一下robots.txt文件

[![](https://p3.ssl.qhimg.com/t01caab4823515612a3.png)](https://p3.ssl.qhimg.com/t01caab4823515612a3.png)

哦？好家伙，我们发现了敏感路径，这不就成了嘛，然后我们访问该路径

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017a920ffc26d062a0.png)

我们发现虽然我们现在是普通用户，但是因为找到了敏感路径而可以访问到管理面板，我们就可以删除指定用户了

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%88%A9%E7%94%A8%E4%B8%8D%E6%98%93%E7%8C%9C%E8%A7%A3URL%E7%9A%84%E6%9C%AA%E5%8F%97%E4%BF%9D%E6%8A%A4%E7%9A%84%E7%AE%A1%E7%90%86%E5%91%98%E5%8A%9F%E8%83%BD"></a>配套靶场2：利用不易猜解URL的未受保护的管理员功能

知识点讲了，所以我们f12看看前端文件有没有泄漏什么敏感路径

[![](https://p1.ssl.qhimg.com/t013e9389c80bf96d05.png)](https://p1.ssl.qhimg.com/t013e9389c80bf96d05.png)

我们看到了js里有这一段逻辑判断当前用户是否是管理员，如果是就链接到管理界面，唉，但是这段逻辑写在了前端就可以被所有人看到，再复杂的URL也形同虚设，我们找到管理面板路径以后就像上一题一样操作就可以了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013b01d197063ed9e9.png)

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E5%8F%82%E6%95%B0%E7%9A%84%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%E6%89%8B%E6%AE%B5"></a>基于参数的访问控制手段

有的应用程序通过URL参数值来实现访问控制，比如这样的URL

```
https://insecure-website.com/login/home.jsp?admin=true
https://insecure-website.com/login/home.jsp?role=1
```

这样的访问控制手段相信大家肯定能看出来是非常脆弱的了

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E7%94%B1%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0%E6%8E%A7%E5%88%B6%E7%9A%84%E7%94%A8%E6%88%B7%E8%A7%92%E8%89%B2"></a>配套靶场1：由请求参数控制的用户角色

我们登录给定的用户，发现Cookie有这样的字段

[![](https://p0.ssl.qhimg.com/t01923342489db68f20.png)](https://p0.ssl.qhimg.com/t01923342489db68f20.png)

从图中来看我们可以猜到应用系统就是通过这个参数判断是否为管理员的，于是我们将它改为true后即可触发垂直提前进入管理面板

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c2b4efa4597c8ebc.png)

然后还是同样的操作，删除指定用户

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%8F%AF%E4%BB%A5%E5%9C%A8%E7%94%A8%E6%88%B7%E9%85%8D%E7%BD%AE%E4%B8%AD%E4%BF%AE%E6%94%B9%E8%A7%92%E8%89%B2"></a>配套靶场2：可以在用户配置中修改角色

我们登录用户，发现修改邮箱功能点的响应是这样的

[![](https://p0.ssl.qhimg.com/t016476b4bd4c8dd8d5.png)](https://p0.ssl.qhimg.com/t016476b4bd4c8dd8d5.png)

我们看到响应中会显示roleid，我们尝试在请求json中将roleid修改成2试试

[![](https://p3.ssl.qhimg.com/t01f019812338541204.png)](https://p3.ssl.qhimg.com/t01f019812338541204.png)

我们发现roleid也是可以改的，我们就可以进入管理面板了

[![](https://p5.ssl.qhimg.com/t012e48b7e274cf2eb8.png)](https://p5.ssl.qhimg.com/t012e48b7e274cf2eb8.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0166b6b314b1575a18.png)

然后我们就能删除指定用户了

### <a class="reference-link" name="%E9%85%8D%E7%BD%AE%E9%94%99%E8%AF%AF%E5%AF%BC%E8%87%B4%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%E7%AD%96%E7%95%A5%E8%A2%AB%E7%A0%B4%E5%9D%8F"></a>配置错误导致访问控制策略被破坏

有的应用程序通过基于角色的访问控制策略限制用户对URL的访问，但是如果应用程序接受非标准的HTTP头部字段，比如X-Original-URL和X-Rewrite-URL，这类头部字段可以覆盖要请求的URL，然后应用程序仅在前端对URL进行校验，如果利用这类头部字段覆盖请求URL，可以很轻松地绕过前端校验转而请求本不允许访问的URL。<br>
如果访问控制策略仅限制某种HTTP请求方法，则攻击者可以尝试修改为其他请求方法绕过该策略，比如将POST换成GET，这一点不太好理解，下面我们通过两个配套靶场来深入讲解。

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E5%8F%AF%E4%BB%A5%E7%BB%95%E8%BF%87%E5%9F%BA%E4%BA%8EURL%E7%9A%84%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6"></a>配套靶场1：可以绕过基于URL的访问控制

刚讲过的知识点，我们通过X-Original-URL覆盖请求URL，可以很容易绕过前端校验进入管理面板

[![](https://p1.ssl.qhimg.com/t0165cbbddcd4ff4f8f.png)](https://p1.ssl.qhimg.com/t0165cbbddcd4ff4f8f.png)

应用程序会对每一个请求进行校验，所以我们删除指定用户也是需要这样绕过

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011839f31c01967833.png)

这样我们就可以成功删除指定用户了

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E5%8F%AF%E4%BB%A5%E7%BB%95%E8%BF%87%E5%9F%BA%E4%BA%8E%E6%96%B9%E6%B3%95%E7%9A%84%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6"></a>配套靶场2：可以绕过基于方法的访问控制

首先我们登录管理员账号，进入管理面板拦截提升carlos权限的请求，发到repeater中

[![](https://p4.ssl.qhimg.com/t01564f62a97c166e64.png)](https://p4.ssl.qhimg.com/t01564f62a97c166e64.png)

然后我们登录普通用户，替换session

[![](https://p2.ssl.qhimg.com/t01d24f8dc28bed7036.png)](https://p2.ssl.qhimg.com/t01d24f8dc28bed7036.png)

发现并不能成功实现垂直提权，我们尝试修改请求方法为POSTX

[![](https://p2.ssl.qhimg.com/t01e90d322dac0f892e.png)](https://p2.ssl.qhimg.com/t01e90d322dac0f892e.png)

发现响应会有不同的提示，提示缺少参数，那应该就是URL参数吧，于是我们尝试修改为GET请求方法，右键”Change request method”修改

[![](https://p2.ssl.qhimg.com/t012ae9df33011d87e2.png)](https://p2.ssl.qhimg.com/t012ae9df33011d87e2.png)

返回302，说明我们成功绕过了，于是我们将参数值修改为目标用户即可将其提升为管理员权限

### <a class="reference-link" name="%E6%B0%B4%E5%B9%B3%E6%8F%90%E6%9D%83"></a>水平提权

水平提权就是同类型用户之间可以不受访问控制策略的限制访问资源，比如我本来只能看到我的账户信息，但是水平提权可以让我看到其他人的账户信息，有的应用程通过URL参数值来定位当前查看的账户，通过修改该参数即可实现水平提权<br>
有时候可能URL参数值并不能预测，比如采用全局唯一标识符(GUID)，但是我们可以在一些地方找到其他用户的GUID，这样依然可以实现水平提权查看其他用户的资源<br>
虽然有的应用系统会将不合时宜的请求重定向，但是没准重定向的响应中会泄漏一些目标用户的信息，也是可以实现水平提权的

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA1%EF%BC%9A%E7%94%B1%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0%E6%8E%A7%E5%88%B6%E7%9A%84%E7%94%A8%E6%88%B7ID"></a>配套靶场1：由请求参数控制的用户ID

首先我们登录给定的账号，发现这样的请求参数

[![](https://p0.ssl.qhimg.com/t01ff607fdde0ea1ffc.png)](https://p0.ssl.qhimg.com/t01ff607fdde0ea1ffc.png)

我们试着把请求参数id修改为目标用户

[![](https://p3.ssl.qhimg.com/t01f073b740138933c8.png)](https://p3.ssl.qhimg.com/t01f073b740138933c8.png)

发现可以实现水平提权看到目标用户的API Key

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA2%EF%BC%9A%E7%94%B1%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0%E6%8E%A7%E5%88%B6%E7%9A%84%E4%B8%8D%E5%8F%AF%E9%A2%84%E6%B5%8B%E7%9A%84%E7%94%A8%E6%88%B7ID"></a>配套靶场2：由请求参数控制的不可预测的用户ID

我们登录给定的账号，发现请求参数值换成了GUID

[![](https://p0.ssl.qhimg.com/t01b257e141156b404d.png)](https://p0.ssl.qhimg.com/t01b257e141156b404d.png)

但是我们发现在评论区可以看到别的用户的GUID，我们就可以找到目标用户的GUID，替换一下

[![](https://p2.ssl.qhimg.com/t012c0ad0f630b64be5.png)](https://p2.ssl.qhimg.com/t012c0ad0f630b64be5.png)

然后我们就获取到目标用户的API Key了

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA3%EF%BC%9A%E7%94%B1%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0%E6%8E%A7%E5%88%B6%E7%9A%84%E5%9C%A8%E9%87%8D%E5%AE%9A%E5%90%91%E4%B8%AD%E6%B3%84%E9%9C%B2%E6%95%B0%E6%8D%AE%E7%9A%84%E7%94%A8%E6%88%B7ID"></a>配套靶场3：由请求参数控制的在重定向中泄露数据的用户ID

我们想往常一样修改ID值为目标用户名，会发生重定向

[![](https://p5.ssl.qhimg.com/t0100743f2425faa1d5.png)](https://p5.ssl.qhimg.com/t0100743f2425faa1d5.png)

但是我们还是可以在响应中找到泄漏的API Key

[![](https://p4.ssl.qhimg.com/t0123baf11b301e5883.png)](https://p4.ssl.qhimg.com/t0123baf11b301e5883.png)

我们成功解决该题

### <a class="reference-link" name="%E4%BB%8E%E6%B0%B4%E5%B9%B3%E5%88%B0%E5%9E%82%E7%9B%B4%E6%8F%90%E6%9D%83"></a>从水平到垂直提权

从上面我们知道水平提权可以通过某种方式看到其他用户的信息，但是如果看到的是管理账号的登录凭证即可由水平提权上升到垂直提权

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E7%94%B1%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0%E6%8E%A7%E5%88%B6%E7%9A%84%E6%B3%84%E6%BC%8F%E5%AF%86%E7%A0%81%E7%9A%84%E7%94%A8%E6%88%B7ID"></a>配套靶场：由请求参数控制的泄漏密码的用户ID

我们先登录给定的用户，发现响应中会显示用户的密码

[![](https://p1.ssl.qhimg.com/t01dda5743f10975ae9.png)](https://p1.ssl.qhimg.com/t01dda5743f10975ae9.png)

然后我们把id修改为administrator，就可以在响应中得到它的密码

[![](https://p0.ssl.qhimg.com/t01edff94b6be7fe53a.png)](https://p0.ssl.qhimg.com/t01edff94b6be7fe53a.png)

然后就能登录它然后删除指定用户了

### <a class="reference-link" name="%E4%B8%8D%E5%AE%89%E5%85%A8%E7%9A%84%E7%9B%B4%E6%8E%A5%E5%AF%B9%E8%B1%A1%E5%BC%95%E7%94%A8(IDOR)"></a>不安全的直接对象引用(IDOR)

IDOR全称是Insecure redirect object reference

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFIDOR%EF%BC%9F"></a>什么是IDOR？

IDOR就是应用程序仅根据用户输入直接引用对应的对象，这就很容易导致异常情况发生。通常IDOR还能导致水平提权和垂直提权

### <a class="reference-link" name="%E7%9B%B4%E6%8E%A5%E5%BC%95%E7%94%A8%E6%95%B0%E6%8D%AE%E5%BA%93%E5%AF%B9%E8%B1%A1%E7%9A%84IDOR%E6%BC%8F%E6%B4%9E"></a>直接引用数据库对象的IDOR漏洞

首先我们看一下这样一个URL，通过参数值来访问不同账号的页面<br>`https://insecure-website.com/customer_account?customer_number=132355`<br>
后端数据库通过参数customer_number定位用户，通过修改它的值实现访问不同用户的页面，因为可能访问到其他同类型用户也可能访问到特权用户，所以这是一个可能触发水平提权和垂直提权的例子

### <a class="reference-link" name="%E7%9B%B4%E6%8E%A5%E5%BC%95%E7%94%A8%E9%9D%99%E6%80%81%E6%96%87%E4%BB%B6%E7%9A%84IDOR%E6%BC%8F%E6%B4%9E"></a>直接引用静态文件的IDOR漏洞

有时候敏感信息会被保存在服务器上的静态文件中，而且如果文件名遵循如递增等规律的话，如这样的URL<br>`https://insecure-website.com/static/12144.txt`<br>
如果应用程序仅通过这些有一定规律文件名的文件保存用户的敏感信息的话，攻击者就可以简单通过修改文件名获取其他用户的敏感信息

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E4%B8%8D%E5%AE%89%E5%85%A8%E7%9A%84%E7%9B%B4%E6%8E%A5%E5%AF%B9%E8%B1%A1%E5%BC%95%E7%94%A8"></a>配套靶场：不安全的直接对象引用

在首页我们发现一个在线聊天的功能点，然后我们点击”View transcript”，发现会下载一个txt文件，编号为2，那么我们将其改为1试试

[![](https://p4.ssl.qhimg.com/t01b7961abb103517f8.png)](https://p4.ssl.qhimg.com/t01b7961abb103517f8.png)

我们看到了历史聊天记录中存有指定用户的密码，我们就可以成功登录该用户

### <a class="reference-link" name="%E5%A4%9A%E6%AD%A5%E9%AA%A4%E6%B5%81%E7%A8%8B%E4%B8%AD%E7%9A%84%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%E6%BC%8F%E6%B4%9E"></a>多步骤流程中的访问控制漏洞

有的应用程序需要多个步骤才能实现某个重要功能，比如更新用户详细信息的管理功能
- 加载表单
- 提交修改
- 预览修改并确认
但是应用程序可能并未对所有步骤实施访问控制策略，所以可能会出现攻击者跳过前两步而直接通过修改第三步的某些数据就使用该功能

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E6%9F%90%E4%B8%80%E6%AD%A5%E9%AA%A4%E6%B2%A1%E6%9C%89%E5%AE%9E%E6%96%BD%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%E7%AD%96%E7%95%A5%E7%9A%84%E5%A4%9A%E6%AD%A5%E9%AA%A4%E6%B5%81%E7%A8%8B"></a>配套靶场：某一步骤没有实施访问控制策略的多步骤流程

首先我们登录administrator用户，然后把给用户提升权限的请求发到repeater中，并替换为普通用户的cookie字段，即可实现垂直提权，步骤与之前某一题目相似，过程略

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8EReferer%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6"></a>基于Referer访问控制

有的应用程序仅通过识别Referer头部字段来判断发起请求的入口，如果某个敏感功能点仅通过识别Referer进行访问控制则可以通过篡改该字段值绕过该访问控制策略

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%9F%BA%E4%BA%8EReferer%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6"></a>配套靶场：基于Referer访问控制

我们先登录administrator用户，把给carlos提权的请求发到repeater中，发现referer是这样的

[![](https://p3.ssl.qhimg.com/t016d1a5d0b1999db3d.png)](https://p3.ssl.qhimg.com/t016d1a5d0b1999db3d.png)

然后我们将cookie替换为普通用户的，就可以把目标用户提权了

[![](https://p0.ssl.qhimg.com/t0115e60e7ddb235a30.png)](https://p0.ssl.qhimg.com/t0115e60e7ddb235a30.png)

然后我们就成功解决这道题了

### <a class="reference-link" name="%E5%9F%BA%E4%BA%8ELocation%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6"></a>基于Location访问控制

有的应用程序通过Location头部字段实施访问控制策略，这里的Location是地理位置，通常可以通过VPN等工具伪造Location绕过该策略

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E9%98%B2%E6%AD%A2%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6%E7%AD%96%E7%95%A5"></a>如何防止访问控制策略

burp给出了以下 几点防护建议
- 切勿仅通过混淆文件名进行访问控制
- 非公开资源默认情况下应该拒绝访问
- 尽可能使用单个应用程序范围的机制来执行访问控制
- 在代码中应该声明每个允许访问的资源的访问控制权限，其他资源均默认拒绝访问
- 严格审计并测试访问控制策略，确保其设计上没有明显的缺陷


## 总结

以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 – 访问控制漏洞与越权专题的全部内容啦，本文主要介绍了访问控制模型以及常见的破坏访问控制策略的例子，脆弱的访问控制策略会给应用程序带来非常严重的后果，所以本专题也是非常重要的一个专题，大家如果有任何问题，欢迎在评论区讨论哦，嘻嘻嘻。
