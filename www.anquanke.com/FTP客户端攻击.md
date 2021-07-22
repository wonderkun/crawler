> 原文链接: https://www.anquanke.com//post/id/103782 


# FTP客户端攻击


                                阅读量   
                                **139381**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Danny Grander，文章来源：
                                <br>原文地址：[https://snyk.io/blog/attacking-an-ftp-client/](https://snyk.io/blog/attacking-an-ftp-client/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01ed68f2b3b493dc7b.png)](https://p1.ssl.qhimg.com/t01ed68f2b3b493dc7b.png)



## 引言

我们经常会听到HTTP客户端（如Web浏览器）被恶意网页内容利用的漏洞，这里没有什么新奇的。但是如果FTP客户端本身存在可被利用的漏洞？ FTP客户端被其连接到的恶意服务器锁定。<br>
本文将展示一个有趣的路径遍历漏洞，漏洞发现者已于2017年11月向多家受影响的供应商披露了此漏洞。此漏洞影响多个应用程序和库，允许FTP服务器在本地文件系统中创建或覆写任何文件。正如您在下面的细节中将看到的，此漏洞由于缺少验证，不仅影响FTP客户端，还影响许多其他应用程序和库，如Java，npm等。



## 漏洞

Ok，让我们一窥究竟！我们想要编写一个将远程FTP文件夹的内容下载到本地文件夹的功能。我们知道FTP协议本身并不提供下载文件夹的命令，但我们可以结合其他几个命令来实现此功能。<br>
我们可以：<br>
1、列出远程文件夹中的所有文件（LIST或NLST FTP命令）<br>
2、对于上面列表结果的每个文件：下载文件并将其保存到本地文件夹（GET或MGET FTP命令）<br>
使用Apache commons-net库执行此行为的一些Java代码示例如下：

```
private void downloadDirectory(FTPClient ftpClient, String remoteDir, String localDir) throws IOException
`{`
FTPFile[] subFiles = ftpClient.listFiles(remoteDir);
for (FTPFile aFile : subFiles)
`{`
if (!aFile.isDirectory())
`{`
String remoteFile = ftpClient.printWorkingDirectory() + File.separator + aFile.getName();
String localFile = localDir + File.separator + aFile.getName();

   OutputStream downloadedStream = new BufferedOutputStream(new FileOutputStream(new File(localFile)));
   boolean success = ftpClient.retrieveFile(remoteFile, downloadedStream);
   outputStream.close();
`}`
`}`
`}`
```

上面的代码遍历服务器返回的每个文件，并将其下载到本地目标文件夹中。假设远程文件夹中的第一个文件名passwd，我们的本地目标文件夹是/var/data/sync/，那么我们最终会将文件下载到/var/data/sync/passwd。<br>
但是如果此时连接的FTP服务器是恶意的，LIST命令得到的响应不是passwd文件名，而是../../../../etc/passwd。上面的代码最终会将文件放入/var/data/sync/../../../../etc/passwd，实际上新下载的文件会覆盖/ etc / passwd。

你可能会说，../../../../etc/passwd不是一个有效的文件名，事实确实如此。但RFC并没有说它不是。从技术上讲，文件名的有效性是交给客户端和服务器去验证的，文件系统无从知晓。例如，基于Windows的FTP服务器对LIST命令的响应如下所示：

```
05-26-95 10:57AM 143712 $LDR$",
"05-20-97 03:31PM 681 .bash_history",
"12-05-96 05:03PM &lt;DIR&gt; absoft2",
"11-14-97 04:21PM 953 AUDITOR3.INI",
"05-22-97 08:08AM 828 AUTOEXEC.BAK",
"01-22-98 01:52PM 795 AUTOEXEC.BAT",
"05-13-97 01:46PM 828 AUTOEXEC.DOS",
"12-03-96 06:38AM 403 AUTOTOOL.LOG",
"12-03-96 06:38AM &lt;DIR&gt; 123xyz",
"01-20-97 03:48PM &lt;DIR&gt; bin",
"05-26-1995 10:57AM 143712 $LDR$", 
```

而基于unix的，看起来像这样：

```
"zrwxr-xr-x 2 root root 4096 Mar 2 15:13 zxbox",
"dxrwr-xr-x 2 root root 4096 Aug 24 2001 zxjdbc",
"drwxr-xr-x 2 root root 4096 Jam 4 00:03 zziplib",
"drwxr-xr-x 2 root 99 4096 Feb 23 30:01 zzplayer",
"drwxr-xr-x 2 root root 4096 Aug 36 2001 zztpp",
"-rw-r--r-- 1 14 staff 80284 Aug 22 zxJDBC-1.2.3.tar.gz",
"-rw-r--r-- 1 14 staff 119:26 Aug 22 2000 zxJDBC-1.2.3.zip",
"-rw-r--r-- 1 ftp no group 83853 Jan 22 2001 zxJDBC-1.2.4.tar.gz",
"-rw-r--r-- 1ftp nogroup 126552 Jan 22 2001 zxJDBC-1.2.4.zip",
"-rw-r--r-- 1 root root 111325 Apr -7 18:79 zxJDBC-2.0.1b1.tar.gz",
"drwxr-xr-x 2 root root 4096 Mar 2 15:13 zxbox",
```

实际上，还有很多其他的文件系统格式，下面是apache commons-net库支持的列表：

`OS400, AS400, L8, MVS, NETWARE, NT, OS2, UNIX, VMS, MACOS_PETER`

因此，典型的FTP客户端不会验证文件名，而是原样返回它们供发人员验证。

不用说，开发人员忽略了此项验证。不信可以查看一下github上托管的项目或StackOverflow 、 CodeJava上的代码片段。



## 案例研究：Apache HIVE

Apache Hive是一个基于Apache Hadoop构建的数据仓库软件项目，用于提供数据汇总、查询和分析。Hive提供了一个类似SQL的界面来查询与Hadoop集成的各种数据库和文件系统中的数据。除此之外，它还支持使用COPY-FROM-FTP命令从FTP服务器复制数据。

```
COPY FROM FTP host [USER user [PWD password]] [DIR directory] [FILES files_wildcard]
[TO [LOCAL] target_directory] [options]
options:
OVERWRITE | NEW
SUBDIR
SESSIONS num
```

从代码中,我们看到调用了retrieveFileList()函数。

```
Run COPY FROM FTP command
*/
Integer run(HplsqlParser.Copy_from_ftp_stmtContext ctx) `{`
trace(ctx, “COPY FROM FTP”);
initOptions(ctx);
ftp = openConnection(ctx);
if (ftp != null) `{`
Timer timer = new Timer();
timer.start();
if (info) `{`
info(ctx, “Retrieving directory listing”);
`}`
retrieveFileList(dir);
timer.stop();
if (info) `{`
info(ctx, “Files to copy: “ + Utils.formatSizeInBytes(ftpSizeInBytes) + “, “ + Utils.formatCnt(fileCnt, “file”) + “, “ + Utils.formatCnt(dirCnt, “subdirectory”, “subdirectories”) + “ scanned (“ + timer.format() + “)”);
`}`
if (fileCnt &gt; 0) `{`
copyFiles(ctx);
`}`
`}`
return 0;
`}`
```

在retrieveFileList函数内部，我们可以看到服务器返回的文件名直接加在了目录的后面没有经过任何验证（名称=目录+名称;）。该文件被添加到队列中，等待下载。

```
void retrieveFileList(String dir) `{`
if (info) `{`
if (dir == null || dir.isEmpty()) `{`
info(null, “ Listing the current working FTP directory”);
`}`
else `{`
info(null, “ Listing “ + dir);
`}`
`}`
try `{`
FTPFile[] files = ftp.listFiles(dir);
ArrayList&lt;FTPFile&gt; dirs = new ArrayList&lt;FTPFile&gt;();
for (FTPFile file : files) `{`
String name = file.getName();
if (file.isFile()) `{`
if (filePattern == null || Pattern.matches(filePattern, name)) `{`

 if (dir != null &amp;&amp; !dir.isEmpty()) `{`
   if (dir.endsWith("/")) `{`
     name = dir + name;
   `}`
   else `{`
     name = dir + "/" + name;
   `}`
 `}`
 if (!newOnly || !isTargetExists(name)) `{`
   fileCnt++;
   ftpSizeInBytes += file.getSize();
   filesQueue.add(name);
   filesMap.put(name, file);
 `}`
`}`
```

之后，在downloader线程中，客户端从队列中取出文件直接进行下载。

```
java.io.File targetLocalFile = null;
File targetHdfsFile = null;
if (local) `{`
targetLocalFile = new java.io.File(targetFile);
if (!targetLocalFile.exists()) `{`
targetLocalFile.getParentFile().mkdirs();
targetLocalFile.createNewFile();
`}`
out = new FileOutputStream(targetLocalFile, false /*append*/);
`}`
```

一个可能的攻击是覆盖root用户的ssh authorized_keys文件，以超级用户身份登录客户端。假设Apache Hive连接到我们的FTP服务器，每天下载一些商用数据。为了执行攻击，我们修改FTP服务器，将恶意路径遍历文件名发送回客户端。例如，可以用../../../../../../../home/root/.ssh/authorized_keys响应LIST命令。<br>
当Hive以root身份执行这条语句，root的authorized_keys ssh文件将被攻击者已知的文件覆盖。

上述漏洞已披露给Apache基金会。

时间线：



[![](https://p3.ssl.qhimg.com/t010e893fb68d5c6744.png)](https://p3.ssl.qhimg.com/t010e893fb68d5c6744.png)

Apache Hive项目的详细信息也于4/4/2018发布在CVE数据库中。

CVE-2018-1315：如果FTP服务器遭到入侵，HPL / SQL中的“COPY FROM FTP”语句可以写入任意位置 严重程度：中等

供应商：Apache软件基金会

受影响的版本：Hive 2.1.0至2.3.2

描述：当使用Hive的HPL / SQL扩展运行“COPY FROM FTP”语句时，被入侵或恶意FTP服务器可能会导致文件被写入到运行该命令的集群中的任意位置。这是因为HPL / SQL中的FTP客户端代码不验证下载代码的目标位置。该漏洞

不影响hive cli用户和hiveserver2用户，因为hplsql是单独的命令行脚本，需要以不同方式调用。

缓解：使用Hive 2.1.0到2.3.2的HPL / SQL的用户应该升级到2.3.3。 或者，通过其他方式禁用HPL / SQL的使用。



## 总结

本文概述了由于FTP服务器的数据未正确验证而导致的某些FTP客户端应用程序和库所具有的漏洞。过去也发生过类似的问题。 例如，在2002年，MITRE的一位首席信息安全工程师Steve Christey发现多个FTP客户端存在同样问题，包括本机linux FTP客户端和wget。

对输入进行验证至关重要（而不只是为了安全）。 作为一名开发人员，关注普通人如何使用我们的API是非常容易的，但预期攻击者可能产生的意外输入同样重要。 处理来自FTP服务器的目录列表时，请确保过滤以/或包含..开头的文件名。
