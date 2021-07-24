> 原文链接: https://www.anquanke.com//post/id/176470 


# Drupal漏洞组合拳：通过恶意图片实现一键式RCE


                                阅读量   
                                **211029**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者thezdi，文章来源：thezdi.com
                                <br>原文地址：[https://www.thezdi.com/blog/2019/4/11/a-series-of-unfortunate-images-drupal-1-click-to-rce-exploit-chain-detailed](https://www.thezdi.com/blog/2019/4/11/a-series-of-unfortunate-images-drupal-1-click-to-rce-exploit-chain-detailed)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01aad1734b07755949.jpg)](https://p5.ssl.qhimg.com/t01aad1734b07755949.jpg)



## 一、前言

最近Drupal公布了两个关键补丁，支持7.x及8.x版本。在这个安全更新中修复了一些bug，最开始这些bug已提交到我们的[针对性漏洞激励计划](https://www.zerodayinitiative.com/blog/2018/7/24/announcing-the-targeted-incentive-program-a-special-award-for-special-targets)（TIP）中。利用这些漏洞有可能实现代码执行，但攻击者先要将3个恶意的“图像”上传到目标服务器上，然后诱导通过身份认证的网站管理员按照攻击者精心设计的方式操作，最终实现代码执行。由于攻击过程不够平滑，因此尚不足以获得TIP奖项。然而，这些bug的确能在针对性攻击中发挥作用，因此我们通过正常的ZDI流程购买了这些bug。大家可以参考[此视频](https://youtu.be/GT5LCO7D3SE)了解这些bug的整体利用过程。

这两个bug可以组合使用，实现一键式代码执行。漏洞编号分别为ZDI-19-130以及ZDI-19-291，由Sam Thomas（<a>@_s_n_t</a>）发现。攻击者可以在账户注册过程中，将攻击图像当成个人资料图像上传，也可以在评论中上传图像。已禁用用户注册以及用户评论功能的Drupal站点不受这些攻击方式影响，但我们还是建议用户将Drupal服务器更新到最新版本。

ZDI-19-130是一个PHP反序列化漏洞，可以让我们利用站点Admin实现RCE，ZDI-19-291是一个持久型跨站脚本漏洞，攻击者可以利用该漏洞强迫管理员发送恶意请求，触发ZDI-19-130。

ZDI-19-130的利用原理基于Thomas今年早些时候在Black Hat上做的一次[演讲](https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf)（[白皮书](https://cdn2.hubspot.net/hubfs/3853213/us-18-Thomas-It's-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-....pdf)），大家也可以观看Thomas在BSidesMCR上关于该主题的[演讲](https://www.youtube.com/watch?v=GePBmsNJw6Y)。在演讲中，Thomas详细介绍了通过Phar归档文件触发PHP反序列化漏洞的一种新方法。PHP Phar归档文件的metadata（元数据）实际上会以PHP序列化对象的形式存储，在Phar归档文件上的文件操作会触发服务器在已存储的元数据上执行`unserialization()`操作，最终导致代码执行。

另一方面，ZDI-19-291是处理已上传文件的文件名过程中存在的一个漏洞，该漏洞与PCRE（Perl Compatible Regular Expression，Perl兼容的正则表达式）有关。当用户上传内文件时，Drupal会使用PRCE来修改文件名，避免文件名出现重复。Drupal的某次[commit](https://github.com/drupal/drupal/commit/1df3cfffefefc93ed2d29041d148938d08bb9d4e#diff-4e0145abc1f82e6483c217eea8f84333R906)中包含一个PCRE bug，如果多次上传文件，Drupal就会删除文件的扩展名，导致攻击者可以上传任意HTML文件，该bug已存在8年之久。



## 二、简要回顾

### <a class="reference-link" name="PHP%E5%AF%B9%E8%B1%A1%E6%B3%A8%E5%85%A5"></a>PHP对象注入

2009年iPhone 3GS发布，在同一年，Stefan Esser（[ROP](https://www.owasp.org/images/f/f6/POC2009-ShockingNewsInPHPExploitation.pdf)的代码复用技术来进一步利用。随后，Esser创造了一个专业术语：[Property Oriented Programming](https://www.owasp.org/images/9/9e/Utilizing-Code-Reuse-Or-Return-Oriented-Programming-In-PHP-Application-Exploits.pdf)（面向属性编程）。在Esser公布研究成果之前，PHP对象反序列化漏洞大多数情况下只用于拒绝服务场景或者难以利用的内存破坏场景。

与ROP的首次问世一样，POP利用链构造过程需要手动操作且非常繁琐，当时并没有太多工具或者参考文献可用。我了解的唯一一份参考资料是由Johannes Dahse等人在2014年发表的关于自动化生成POP链的[研究成果](https://www.ei.rub.de/media/emma/veroeffentlichungen/2014/09/10/POPChainGeneration-CCS14.pdf)。遗憾的是，他们并没有公开相应的工具。

### <a class="reference-link" name="PHP%E5%88%A9%E7%94%A8%E6%A0%87%E5%87%86%E5%8C%96"></a>PHP利用标准化

轮到[PHPGGC](https://github.com/ambionics/phpggc)（PHP Generic Gadget Chains）登场，这个库于2017年6月公布，是类似于[ysoserial](https://github.com/frohoff/ysoserial) Java反序列化漏洞的payload库。随着PHP框架和库的流行，在PHP自动加载功能的帮助下，PHP反序列化漏洞现在利用起来已经非常容易。



## 三、漏洞分析

### <a class="reference-link" name="%E7%AC%AC%E4%B8%80%E9%98%B6%E6%AE%B5%EF%BC%9AZDI-19-291"></a>第一阶段：ZDI-19-291

如下PHP代码片段可以用来测试Drupal源代码。根据源代码中的注释，如下代码段会尝试删除文件名中值小于0x02的ASCII控制字符，将其替换为下划线字符（`_`）。代码中使用了`/u`修饰符，因此PHP引擎会将PCRE表达式以及相应的字符串当成UTF-8编码字符。我们推测PCRE表达式中加入这个修饰符是为了兼容UTF-8。

[![](https://p4.ssl.qhimg.com/t0131c66d6431be4d79.png)](https://p4.ssl.qhimg.com/t0131c66d6431be4d79.png)

**UTF-8**

一般人都认为UTF-8字符占2个字节，实际上UTF-8可以占1~4个字节。设计UTF-8时需要向后兼容ASCII字符集，因此，在1字节代码点(code point)范围内，UTF-8与ASCII（0x00到0x7F）相同。0x80到0xF4用于编码多字节UTF-8代码点。根据RFC3629，有效的UTF-8字符串中永远不存在C0、C1、F5~FF这几个值。

**测试结果**

[![](https://p0.ssl.qhimg.com/t011e801cd7db39d4db.png)](https://p0.ssl.qhimg.com/t011e801cd7db39d4db.png)

由于`\xFF`字节无效，并且`\x80`字节没有有效的前导字节，因此PHP会抛出`PREG_BAD_UTF8_ERROR`错误，将每个[文档](https://secure.php.net/manual/en/function.preg-replace.php)的`$basename`变量值设为`NULL`。

在源代码中，调用`preg_replace()`后Drupal并没有执行任何错误检查操作。当用户两次将包含无效UTF-8字符的文件名上传至Drupal时，Drupal将调用该函数，将`$basename`变量当成空字符串。最后，该函数会返回`$destination`，而该变量的值会被设置为`_.$counter++`。

[![](https://p2.ssl.qhimg.com/t014d3d176078acb320.png)](https://p2.ssl.qhimg.com/t014d3d176078acb320.png)

根据这个代码逻辑，攻击者可以将一个GIF图像当成个人资料图像，通过用户注册操作上传到Drupal网站，使目标网站删除该文件的扩展名。现在Drupal会将该图像存放到如下路径：

```
/sites/default/files/pictures/&lt;YYYY-MM&gt;/_0

```

而正常情况下，正确的存放路径为：

```
/sites/default/files/pictures/&lt;YYYY-MM&gt;/profile_pic.gif

```

虽然Drupal会检查上传的用户资料图像，但攻击者只要在带有`.gif`扩展名的HTML文件开头附加“GIF”字符就能通过检查。

攻击者还可以通过评论编辑器上传恶意GIF文件。在这种情况下，图像的存放路径为`/sites/default/files/inline-images/_0`。然而，在默认配置的Drupal环境中，攻击者在发表评论前需要注册一个用户账户。

图像文件通常不会搭配`Content-Type`头，因此攻击者可以利用这种方式将恶意GIF/HTML文件上传到Drupal服务器，然后使用匹配的`type`，诱导浏览器以HTML网页形式渲染这些文件。利用方式如下：

[![](https://p1.ssl.qhimg.com/t01cdecf87231fb8f31.png)](https://p1.ssl.qhimg.com/t01cdecf87231fb8f31.png)

总之，攻击者最终可以在目标Drupal网站上实现持久型XSS。攻击者可能利用该漏洞，诱导具备管理员权限的用户访问某个恶意链接，发起恶意请求，从而利用第二阶段漏洞。大家可以访问[此处](https://github.com/thezdi/PoC/blob/master/Drupal/drupal_xss_rce.zip)下载PoC代码。

### <a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%AE%B5%EF%BC%9AZDI-19-130"></a>第二阶段：ZDI-19-130

ZDI-19-130是一个反序列化bug，可以通过位于`/admin/config/media/file-system`网址的`file_temporary_path`请求参数触发。攻击者可以指定`phar://`流，将`file_temporary_path`参数指向恶意的Phar归档文件（该文件需要在第二阶段攻击前上传至Drupal服务器）。

`system_check_directory()`是处理该请求的回调函数。根据Thomas的研究成果，`!is_dir($directory)`文件操作并不足以触发PHP反序列化存放在Phar归档文件中的metadata。利用POP链利用技术，攻击者可以使用精心构造的Phar归档文件，在web服务器的上下文中执行任意代码。

[![](https://p0.ssl.qhimg.com/t0138ef15222fac15a6.png)](https://p0.ssl.qhimg.com/t0138ef15222fac15a6.png)

### <a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E9%98%B6%E6%AE%B5%EF%BC%9APolyglot%E6%96%87%E4%BB%B6"></a>第二阶段：Polyglot文件

在利用ZDI-19-130之前，我们需要将Phar文件上传到目标服务器上。攻击者可以在用户注册过程中，将一个JPEG/Phar类型的polyglot文件作为个人资料图像上传来完成该任务。下图就是一个JPEG/Phar类型的polyglot图像（已被转码，原图参考[此处](https://static1.squarespace.com/static/5894c269e4fcb5e65a1ed623/t/5be22702b8a0453302db6862/1541547931080/blog-ZDI-CAN-7232-cat.jpg?format=300w)），当与ZDI-19-130漏洞配合使用时，该文件就会在目标服务器上执行`cat /etc/passwd`命令。

[![](https://p1.ssl.qhimg.com/t017750165bc0d6241d.jpg)](https://p1.ssl.qhimg.com/t017750165bc0d6241d.jpg)

与JAR文件类似，Phar文件是一种归档文件，各种组件被打包到单个归档文件中。在PHP规范中，可以使用不同的归档格式来打包文件。在本文的漏洞利用场景中，我们使用的是基于TAR的Phar归档格式。

为了创建polyglot文件，攻击者首先需要选择一个JPEG图像载体，然后将基于TAR的恶意Phar文件全部存放到JPEG文件开头处的JPEG注释段中。当解释成TAR格式文件时，JPEG文件的图像开始段标记以及注释段标记会稍微与第一个文件名冲突。当修复TAR文件校验和后，只要存储在TAR/Phar归档文件中的第一个文件与包含POP链payload的Phar元数据组件文件不对应，这种冲突就不会对漏洞利用造成影响。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%BF%87%E7%A8%8B%E6%80%BB%E7%BB%93"></a>利用过程总结

回顾一下，攻击者首先必须将ZDI-19-130 JPEG/Phar polyglot图像文件上传到目标服务器上，确定已上传图像的位置。然后，攻击者必须两次上传ZDI-19-291 GIF/HTML图像XSS，使服务器在保存图像文件时删除文件扩展名。最后，攻击者必须诱导网站管理员访问托管在目标服务器上的ZDI-19-291 GIF/HTML，通过适当的`type`属性，使浏览器以HTML页面渲染该图像，从而触发第二阶段的漏洞利用。如果一切顺利，攻击者可以在web服务器上实现代码执行，返回一个shell（参考前面的演示视频）。



## 四、总结

Thomas展示了一种新的攻击方法，为攻击者打开了崭新的大门。除非PHP决定修改Phar文件的处理流程，否则开发者在使用文件操作符处理用户可控的数据时要格外小心。许多人认为将用户可控的数据传递给文件操作符（如`is_dir()`）不是高风险的操作，因此我们估计将来会出现利用该方法的其他漏洞。随着POP链利用工具的不断完善，PHP反序列化漏洞现在利用起来也非常容易。软件厂商应当借此机会考虑不再使用`serialize()`，迁移到更为安全的`json_encode()`方案。

虽然这些bug并没有赢得TIP奖项，但对漏洞研究而言依然非常重要。如果大家对TIP计划感兴趣，可以经常翻一下我们的博客，关注目标清单有什么改动。我们的总奖金已经累计超过1,000,000美元，应该足以吸引您的目光。

另外，大家可以关注我的[推特](https://twitter.com/trendytofu)，[获取](https://twitter.com/thezdi)最新的漏洞利用技术及安全补丁信息。
