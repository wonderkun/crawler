> 原文链接: https://www.anquanke.com//post/id/171431 


# Drupal SA-CORE-2019-003 远程命令执行分析


                                阅读量   
                                **183564**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01d40452187d5e4509.png)](https://p4.ssl.qhimg.com/t01d40452187d5e4509.png)

本文作者：Rico @腾讯安全云鼎实验室

## 漏洞背景

2 月 20 日 Drupal 官方披露了一个 Drupal 的远程命令执行漏洞：

[https://www.drupal.org/sa-core-2019-003](https://www.drupal.org/sa-core-2019-003)

漏洞的触发条件为开启了 RESTful Web Services，且允许 POST / PATCH 请求。

根据 Drupal 的配置，此漏洞可能不需要任何权限即可触发，但普适性不高。一旦该漏洞被利用，攻击者则可以直接在 Web 服务器上执行任意 PHP 代码，造成服务器被入侵、用户信息泄露等后果。

腾讯云不受该漏洞影响，此漏洞爆发后，腾讯云安全团队第一时间进行跟踪分析，且对云上客户进行预警通知。



## 漏洞定位

漏洞通告指出了 Drupal 8 在开启了 RESTful Web Services 模块，同时允许了 PATCH / POST 方法请求后，可以造成代码执行漏洞。

根据 commit log [注1] 可以定位到漏洞的触发原因在于反序列化的操作：

[![](https://p0.ssl.qhimg.com/t019e5f2a8cc3938861.png)](https://p0.ssl.qhimg.com/t019e5f2a8cc3938861.png)

可以推测应该是在进行 REST API 操作的过程中，options 参数的内容带入到 unserialize 函数导致的。通过 diff 可以发现 LinkItem.php 和 MapItem.php 都受到影响，这里从 LinkItem 来向上挖掘漏洞点。

查看 coremoduleslinksrcPluginFieldFieldTypeLinkItem.php：

[![](https://p4.ssl.qhimg.com/t0118666be44d862dcd.png)](https://p4.ssl.qhimg.com/t0118666be44d862dcd.png)

梳理了其整个调用链，从 REST 请求开始，先通过用户传入的 JSON 的 _links.type 获取了其对应的 Entity，再获取 Entity 内的 Fields 列表，遍历这个列表得到 key，从用户传入的 JSON 内取出 key，拼接成为 field_item:key 的形式（过程略），最终在 getDefinition 内查找了 definitions 数组内的字段定义，得到一个对应的 Field 的实例对象，过程大体如下：

[![](https://p4.ssl.qhimg.com/t01b8d8915c0bd0ce77.png)](https://p4.ssl.qhimg.com/t01b8d8915c0bd0ce77.png)

接着 FieldNormalizer 的 denormalize 方法调用了 Field 的 setValue 方法。

[![](https://p5.ssl.qhimg.com/t01ac295e2caea8c6aa.png)](https://p5.ssl.qhimg.com/t01ac295e2caea8c6aa.png)

也就是说，我们如果可以将 $field_item 控制为 LinkItem 或者 MapItem，即可触发反序列化。



## 触发点构造

我们在 Drupal 后台配置好 RESTful Web Service 插件，选择一个可以进行 POST 的操作。

为了尽可能模拟网站管理员的配置，我们这里允许对于 /user/register 的 POST 操作。

于情于理，用户注册处必然可以作为匿名用户来进行操作。开启 /user/register ：

[![](https://p5.ssl.qhimg.com/t0154ad5b141f876fe1.png)](https://p5.ssl.qhimg.com/t0154ad5b141f876fe1.png)

设置允许匿名用户利用 POST 来访问 /user/register 。

[![](https://p5.ssl.qhimg.com/t015f86e4c7180da512.png)](https://p5.ssl.qhimg.com/t015f86e4c7180da512.png)

上文中提到，我们需要一个 Entity 内存在 LinkItem Field。通过对 Entity 的查找，定位到 MenuLinkContent 和 Shortcut 使用了 LinkItem，利用 Shortcut 来进行进一步的测试。

[![](https://p1.ssl.qhimg.com/t015230336ca725fd69.png)](https://p1.ssl.qhimg.com/t015230336ca725fd69.png)

Shortcut 的 _links.type 为 [http://127.0.0.1/rest/type/shortcut/default](http://127.0.0.1/rest/type/shortcut/default) 。

向 /user/register 发送 POST 请求，同时在 PHPStorm 内将断点下在

coremoduleshalsrcNormalizerFieldItemNormalizer.php 的 denormalize 函数：

[![](https://p5.ssl.qhimg.com/t01352a79b86ddf30e1.png)](https://p5.ssl.qhimg.com/t01352a79b86ddf30e1.png)

可以发现，在调用 setValue 方法的现场，$field_item 为 LinkItem。跟入 setValue 方法（图 2），根据逻辑，如果 $values 为一个数组。且 $values[‘options’] 存在，那么就执行反序列化操作。我们修改 payload 为即可触发反序列化。

[![](https://p4.ssl.qhimg.com/t0131bee23a5e71bb7c.png)](https://p4.ssl.qhimg.com/t0131bee23a5e71bb7c.png)

#### <a class="reference-link" name="%E9%AA%8C%E8%AF%81%E8%A7%86%E9%A2%91%EF%BC%9A"></a>验证视频：

攻击者利用此反序列化可以在服务器上执行任意代码，利用此漏洞在服务器上弹出计算器的视频如下：

[![](https://p5.ssl.qhimg.com/t01ce0a7b0f42431ce2.gif)](https://p5.ssl.qhimg.com/t01ce0a7b0f42431ce2.gif)



## 安全建议

#### <a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E6%96%B9%E6%A1%88%E5%A6%82%E4%B8%8B%EF%BC%9A"></a>修复方案如下：
1. Drupal 8.6.x 版本升级到 8.6.10 版本
1. Drupal 8.5.x 或更早期版本版本升级到 8.5.11 版本
1. Drupal 7 暂无更新
#### <a class="reference-link" name="%E7%BC%93%E8%A7%A3%E6%8E%AA%E6%96%BD%E5%A6%82%E4%B8%8B%EF%BC%9A"></a>缓解措施如下：
1. 禁用 RESTful Web Services 模块
1. 配置服务器不允许 POST/PATCH 请求
注1：

[https://github.com/drupal/core/commit/24b3fae89eab2b3951f17f80a02e19d9a24750f5](https://github.com/drupal/core/commit/24b3fae89eab2b3951f17f80a02e19d9a24750f5)

腾讯安全云鼎实验室 关注云主机与云内流量的安全研究和安全运营。利用机器学习与大数据技术实时监控并分析各类风险信息，帮助客户抵御高级可持续攻击；联合腾讯所有安全实验室进行安全漏洞的研究，确保云计算平台整体的安全性。相关能力通过腾讯云开放出来，为用户提供黑客入侵检测和漏洞风险预警等服务，帮助企业解决服务器安全问题。
