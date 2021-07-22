> 原文链接: https://www.anquanke.com//post/id/183153 


# OXID eShop两处漏洞分析


                                阅读量   
                                **153764**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ripstech，文章来源：blog.ripstech.com
                                <br>原文地址：[https://blog.ripstech.com/2019/oxid-esales-shop-software/](https://blog.ripstech.com/2019/oxid-esales-shop-software/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0107bba813595ee43b.png)](https://p2.ssl.qhimg.com/t0107bba813595ee43b.png)



## 0x00 前言

RIPS在OXID eShop软件中检测到了一个高危漏洞，未授权攻击者可以利用该漏洞在几秒之内远程接管使用默认配置的目标站点。此外管理面板中还存在另一个漏洞，攻击者可利用该漏洞获取服务器的远程代码执行（RCE）权限。这里建议用户尽快升级到最新版本。

OXID eShop是源自德国的一套电子商务内容管理系统，许多龙头企业（如Mercedes、BitBurger以及Edeka）都在使用企业版OXID eShop。在本文中我们将分析如何在默认配置的最新版OXID eShop（6.3.4）中，以未授权攻击者身份获得远程代码执行权限。

攻击过程可参考[此处视频](https://blog.ripstech.com/videos/oxid634_1.mp4)，大家可以访问[此处](https://demo.ripstech.com/scan/87/172)访问RIPS系统分析结果。



## 0x01 SQL注入漏洞

这款电子商务软件中存在一个SQL注入漏洞，可以通过未授权远程会话利用，利用过程无需依赖目标端进行特殊配置。

每当用户查看某款产品时，服务端就会通过_getVendorSelect()方法构造一个SQL查询语句，发送给底层数据库。

源文件：source/Application/Model/ArticleList.php

```
protected function _getVendorSelect($sVendorId)
  `{`
    ⋮
    if ($this-&gt;_sCustomSorting) `{`
      $sSelect .= " ORDER BY `{`$this-&gt;_sCustomSorting`}` "; // line 1087
    `}`
    return $sSelect;
  `}`
```

而服务端会在之前的代码中调用setCustomSorting()方法，设置_sCustomSorting属性，通过该属性构造出ORDER BY SQL语句（上述代码第1087行），随后这会成为攻击者的一个注入点。

源文件：source/Application/Component/Locator.php

```
$oIdList-&gt;setCustomSorting($oLocatorTarget-&gt;getSortingSql(  // line 131
    $oLocatorTarget-&gt;getSortIdent()));
```

在上述代码片段第131行，自定义排序属性值会被设置为getSortingSql()方法的返回值，而服务端会在FrontendController类的getSorting()方法中调用getSavedSorting()方法来设置这个值。

源文件：source/Application/Controller/FrontendController.php

```
public function getSorting($sortIdent)
  `{`
    ⋮
    if ($sorting = $this-&gt;getUserSelectedSorting()) `{`
    /*...*/
    `}` elseif (!$sorting = $this-&gt;getSavedSorting($sortIdent)) `{`        // line 1424
      $sorting = $this-&gt;getDefaultSorting();
    `}`
  /*...*/
  public function getSavedSorting($sortIdent)
  `{`
      $sorting = \OxidEsales\Eshop\Core\Registry::getSession()      // line 1430
                                                -&gt;getVariable('aSorting');
      /*...*/
      return $sorting[$sortIdent];
  `}`
```

从代码中可知，getSavedSorting()方法会访问OXID的内部会话对象（第1430行），提取aSorting值：这行代码的作用相当于直接读取PHP的会话变量$_SESSION[‘aSorting’]。攻击者可以控制这个变量，而该变量正是漏洞利用的关键点。该变量值会被写入1430行的$sorting变量，通过调用栈返回，最终以参数形式传递给前面提到的setCustomSorting()方法。

源文件：source/Application/Component/Widget/ArticleDetails.php

```
protected function _setSortingParameters()
    `{`
        $sSortingParameters = $this-&gt;getViewParameter('sorting');
        /*...*/
        list($sSortBy, $sSortDir) = explode('|', $sSortingParameters);
        $this-&gt;setItemSorting($this-&gt;getSortIdent(), $sSortBy, $sSortDir);
    `}`
    /*...*/
    public function setItemSorting($sortIdent, $sortBy, $sortDir = null)
    `{` 
        /*...*/
        $sorting[$sortIdent]['sortby'] = $sortBy;
        $sorting[$sortIdent]['sortdir'] = $sortDir ? $sortDir : null;
        \OxidEsales\Eshop\Core\Registry::getSession()        // line 912
                                       -&gt;setVariable('aSorting', $sorting);
```

接下来我们分析下攻击者如何控制该变量：在SQL查询语句构造完毕并发送至数据库之前，攻击者可以通过用户输入数据覆盖$_SESSION[‘aSorting’]变量。这个任务通过调用_setSortingParameters()方法来完成，该方法会在源码第901行获取用户可控的sorting参数，然后在904行调用setItemSorting()函数，在该函数中调用getSession()-&gt;setVariable()函数（第912行），最终将恶意用户的输入数据存储到$_SESSION[‘aSorting’]变量中。

最终被注入的SQL语句如下所示：

```
SELECT ... ORDER BY oxtitle ;INSERT INTO oxuser (...) VALUES (...);
```

这意味着攻击者可以利用会话变量作为媒介，直接注入ORDER BY这个SQL查询语句。由于底层数据库驱动默认设置为PDO，因此攻击者可以使用堆叠查询方式插入新的admin用户，设置用户密码。随后攻击者可以登录服务后端，继续漏洞利用过程。



## 0x02 利用Admin RCE

一旦攻击者获得后端服务访问权限，就可以利用服务端导入逻辑中的[PHP对象注入漏洞](https://blog.ripstech.com/2018/php-object-injection/)，提升至RCE（远程代码执行）权限。站点管理员可以通过上传CSV文件来导入文章，而CSV文件会被载入如下代码片段的data数组中。

源文件：source/Core/GenericImport/ImportObject/OrderArticle.php

```
protected function preAssignObject($shopObject, $data, $allowCustomShopId)`{`
    /*...*/
    $persParamValues = @unserialize($data['OXPERSPARAM']);      // line 30
```

在代码第30行，OXPERSPARAM列的值未经过滤就直接交给unserialize()函数来处理，因此存在PHP对象注入漏洞。如果大家想了解更多信息，可参考我们前面发表的PHP对象注入[文章](https://blog.ripstech.com/2018/php-object-injection/)，了解如何利用PHP对象注入实现远程代码执行，具体利用步骤可参考[此处视频](https://blog.ripstech.com/videos/oxid634_2.mp4)。



## 0x03 时间线
<td valign="bottom">日期</td><td valign="bottom">进展</td>
<td valign="top">2017年12月11日</td><td valign="top">报告OXID 4.10.6中存在SQL注入漏洞</td>
<td valign="top">2019年6月18日</td><td valign="top">首次与厂商联系</td>
<td valign="top">2019年6月19日</td><td valign="top">协商并同意加密沟通方式</td>
<td valign="top">2019年6月21日</td><td valign="top">发送漏洞细节</td>
<td valign="top">2019年6月17日</td><td valign="top">厂商告知会在7月30日发布补丁</td>
<td valign="top">2019年7月30日</td><td valign="top">厂商修复问题</td>



## 0x04 总结

远程攻击者可以组合利用本文介绍的OXID eShop两个漏洞完全接管目标站点，从这两个漏洞我们可以看到持续集成安全测试在减少敏感源代码风险中的重要作用。我们要感谢OXID安全团队，他们非常专业，在漏洞响应上也非常迅速。另外，我们强烈建议大家将所有OXID eShop产品更新至最新版。



## 0x05 相关资料
- [TYPO3 9.5.7: Overriding the Database to Execute Code](https://blog.ripstech.com/2019/typo3-overriding-the-database/)
- [Magento 2.3.1: Unauthenticated Stored XSS to RCE](https://blog.ripstech.com/2019/magento-rce-via-xss/)
- [A Salesmans Code Execution: PrestaShop 1.7.2.4](https://blog.ripstech.com/2018/prestashop-remote-code-execution/)
- [Privilege Escalation in 2.3M WooCommerce Shops](https://blog.ripstech.com/2018/woocommerce-php-object-injection/)
- [CubeCart 6.1.12 – Admin Authentication Bypass](https://blog.ripstech.com/2018/cubecart-admin-authentication-bypass/)