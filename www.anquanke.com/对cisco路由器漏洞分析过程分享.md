> 原文链接: https://www.anquanke.com//post/id/251815 


# 对cisco路由器漏洞分析过程分享


                                阅读量   
                                **16262**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01b5103ee79a1c8bd9.jpg)](https://p2.ssl.qhimg.com/t01b5103ee79a1c8bd9.jpg)



本次分析目标靶机为实体机，由于分析对应的多个漏洞均有过官方修复记录，所以将固件刷回较低版本以实现分析及利用实验

ciscoRV34x系列产品以nginx作为中间件进行web服务处理

首先，从官方给固件中解析出文件系统后，分析对web请求的处理流程

以固件版本1.0.2.16为例

在www/cgi-bin/目录下存在3个cgi程序 `blockpage.cgi` `jsonrpc.cgi` `upload.cgi`

这次分析的漏洞成因也正是由于cgi程序处理不当导致的系统命令执行，

找到如何在web界面访问时使用这些程序，就必须要清楚对应请求的路由过程

在/etc/nginx/conf.d/目录下有nginx对应的一些配置文件，下面是一些会用到的配置内容，分别处理`jsonrpc`与`upload` ，

```
location /jsonrpc `{`
    include uwsgi_params;
    proxy_buffering off;
    uwsgi_modifier1 9;
    uwsgi_pass jsonrpc;
    uwsgi_read_timeout 3600;
    uwsgi_send_timeout 3600;
`}`
```

```
location /form-file-upload `{`
    include uwsgi_params;
    proxy_buffering off;
    uwsgi_modifier1 9;
    uwsgi_pass 127.0.0.1:9003;
    uwsgi_read_timeout 3600;
    uwsgi_send_timeout 3600;
`}`

location /upload `{`
    upload_pass /form-file-upload;
    upload_store /tmp/upload;
    upload_store_access user:rw group:rw all:rw;
    upload_set_form_field $upload_field_name.name "$upload_file_name";
    upload_set_form_field $upload_field_name.content_type "$upload_content_type";
    upload_set_form_field $upload_field_name.path "$upload_tmp_path";
    upload_aggregate_form_field "$upload_field_name.md5" "$upload_file_md5";
    upload_aggregate_form_field "$upload_field_name.size" "$upload_file_size";
    upload_pass_form_field "^.*$";
    upload_cleanup 400 404 499 500-505;
    upload_resumable on;
`}`
```

对应upload 与jsonrpc配置了对应路由

uWSGI是用于与其他服务器进行通信的本机二进制协议，

可以在/etc/uwsgi中找到对应的配置，设置了请求处理的对应端口以及对应程序

```
[uwsgi]
plugins = cgi
workers = 1
master = 1
uid = www-data
gid = www-data
socket=127.0.0.1:9003
buffer-size=4096
cgi = /www/cgi-bin/upload.cgi
cgi-allowed-ext = .cgi
cgi-allowed-ext = .pl
cgi-timeout = 300
ignore-sigpipe = true

[uwsgi]
plugins = cgi
workers = 4
master = 1
uid = www-data
gid = www-data
socket=127.0.0.1:9000
buffer-size=4096
cgi = /jsonrpc=/www/cgi-bin/jsonrpc.cgi
cgi-allowed-ext = .cgi
cgi-allowed-ext = .pl
cgi-timeout = 3600
ignore-sigpipe = true
```



## 漏洞分析

### <a class="reference-link" name="cve-2020-3451"></a>cve-2020-3451

<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%8E%9F%E7%90%86"></a>**漏洞原理**

1.0.0.33～1.0.01.20中，对**`/upload`**请求的处理由**`jsonrpc.cgi`** 处理

[![](https://p2.ssl.qhimg.com/t01531d38d15a4ea44d.png)](https://p2.ssl.qhimg.com/t01531d38d15a4ea44d.png)

在处理请求时有根据固件分析可得 v23由`fileparam`传入，

实际执行到 system(“cp path1 /tmp/www/fileparam”)

其中fileparam可控

[![](https://p1.ssl.qhimg.com/t01c55f3023c9bf1745.png)](https://p1.ssl.qhimg.com/t01c55f3023c9bf1745.png)

<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E9%AA%8C%E8%AF%81"></a>**漏洞验证**

路由器采用固件版本 1.0.02.16

[![](https://p0.ssl.qhimg.com/t01ad9b77970e070924.png)](https://p0.ssl.qhimg.com/t01ad9b77970e070924.png)

截取上传文件时包

[![](https://p0.ssl.qhimg.com/t018e39412ee380a803.png)](https://p0.ssl.qhimg.com/t018e39412ee380a803.png)

根据分析的得到命令执行注入点

[![](https://p5.ssl.qhimg.com/t01e86106c176cdc12d.png)](https://p5.ssl.qhimg.com/t01e86106c176cdc12d.png)

反弹shell

[![](https://p2.ssl.qhimg.com/t017a99d4fb3d744946.png)](https://p2.ssl.qhimg.com/t017a99d4fb3d744946.png)

[![](https://p1.ssl.qhimg.com/t01ee3e8f89f119e419.png)](https://p1.ssl.qhimg.com/t01ee3e8f89f119e419.png)

成功执行<br>
该漏洞属于对于传入参数没有仔细检查直接用于了命令传参，

<a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E6%96%B9%E6%B3%95"></a>**修复方法**

在传入参数之前进行一步检查

[![](https://p0.ssl.qhimg.com/t017a4b577df11ee831.png)](https://p0.ssl.qhimg.com/t017a4b577df11ee831.png)

阻拦了一些不正常字符的传入

### <a class="reference-link" name="CVE-2021-1520"></a>CVE-2021-1520

<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E6%88%90%E5%9B%A0"></a>**漏洞成因**

漏洞存在于一个perl脚本文件中，/usr/sbin/vpnTimer 用于处理向本地 9999端口的udp请求。

```
my ($socket,$message);

$socket = new IO::Socket::INET (
        LocalAddr =&gt; '127.0.0.1',
        LocalPort =&gt; '9999',
        Proto =&gt; 'udp',
) or die "ERROR in Socket Creation : $!\n";
```

主要处理函数

```
process_timer()
```

该函数完成工作是从udp请求包中获取message,

```
my $temp=substr($message,1,);
                    #print "$temp\n"; #contains connection name

                    if (index(substr($message,0,1),"+") == 0)`{`
                            #print "It is for ADD\n";
                        #Now, check if it is for TVPNC or S2S.
                        my $isTVPNC=`uci get strongswan.$temp`;
```

perl语言特性，“ 包含的字符作为命令执行，

所以，在上面的语句中很容易发现 获取到udp传输数据后如果数据以`+`开头，则取出`+`后，将后面的内容作为命令执行参数处理。

由与运行在root下，所以可以达成提权后的命令执行；

<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E9%AA%8C%E8%AF%81"></a>**漏洞验证**

先利用上面的漏洞拿到一个交互shell

[![](https://p1.ssl.qhimg.com/t01781f55b87c89af3d.png)](https://p1.ssl.qhimg.com/t01781f55b87c89af3d.png)

路由器中 nc是缩水后的，无法发送udp请求，

但是可以使用自带的python发送udp数据包，

[![](https://p4.ssl.qhimg.com/t0128e80305b0917fe0.png)](https://p4.ssl.qhimg.com/t0128e80305b0917fe0.png)

[![](https://p2.ssl.qhimg.com/t011b3a85f083f44aef.png)](https://p2.ssl.qhimg.com/t011b3a85f083f44aef.png)

root权限的命令执行

<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>**漏洞修复**

在process_timer()中增加了字符的过滤

```
my $regex = "^[+-][a-zA-Z][0-9a-zA-Z]+_[0-9a-zA-Z]+\$";
    if ($message =~ /$regex/) `{`
                        if ($log == 1) `{`
                            system("logger","-t VPN-timer","Message read: $message");
                        `}`
                        my $temp=substr($message,1,);
                        #print "$temp\n"; #contains connection name

                        if (index(substr($message,0,1),"+") == 0)`{`
                            #print "It is for ADD\n";
                            #Now, check if it is for TVPNC or S2S.
                            my $isTVPNC=`uci get strongswan.$temp`;
```

修复了传参错误的漏洞

### <a class="reference-link" name="cve-2021-1414"></a>cve-2021-1414

漏洞分析：

该漏洞触发在路由器设置SNMP时处理不当

抓包分析

[![](https://p1.ssl.qhimg.com/t013356d0578755ef01.png)](https://p1.ssl.qhimg.com/t013356d0578755ef01.png)

实际处理程序对应为jsonrpc.cgi

该路由器大部分操作都经由jsonrpc.cgi进行初步处理

[![](https://p5.ssl.qhimg.com/t013f9088068dd99860.png)](https://p5.ssl.qhimg.com/t013f9088068dd99860.png)

首先获取cookie等环境变量，然后分配内存空间将传入数据储存起来

接着进行Debug等信息的处理，对整体分析不重要，略过。

[![](https://p0.ssl.qhimg.com/t01a0fd258b17c586d0.png)](https://p0.ssl.qhimg.com/t01a0fd258b17c586d0.png)

判断cookie条件中的sub_142E8处理`sessionid`和`current-page`

判断contentype中 在sub_143C8处理判断类型后进入到sub_1499C

进一步跟进

[![](https://p0.ssl.qhimg.com/t0184541cae2a20dd5b.png)](https://p0.ssl.qhimg.com/t0184541cae2a20dd5b.png)

这里应该是通过判断参数决定如何下一步处理

根据抓包信息

[![](https://p1.ssl.qhimg.com/t016f939dab473b0ca0.png)](https://p1.ssl.qhimg.com/t016f939dab473b0ca0.png)

`"method":"set_snmp"`

确定到分支

[![](https://p1.ssl.qhimg.com/t017ff5288796dee9f5.png)](https://p1.ssl.qhimg.com/t017ff5288796dee9f5.png)

sub_12DF8判断session是否合法后进入处理环节

[![](https://p4.ssl.qhimg.com/t01aaccae96035f0c63.png)](https://p4.ssl.qhimg.com/t01aaccae96035f0c63.png)

一堆的导入函数，看名称应该是设置处理函数，问题应该出现在这里

查找函数来源库文件；

[![](https://p5.ssl.qhimg.com/t01a9c60bf695a3a626.png)](https://p5.ssl.qhimg.com/t01a9c60bf695a3a626.png)

我们的漏洞不是在这个统一的处理函数中，接下来去分析对应参数的实际函数

这个漏洞的关键字符是snmp，ZDI上有一些关于漏洞的具体描述

[![](https://p4.ssl.qhimg.com/t0143f54b13d76fddc1.png)](https://p4.ssl.qhimg.com/t0143f54b13d76fddc1.png)

根据这个再寻找对应的引用

已知该漏洞是命令执行类漏洞

寻找到popen()或者system之类的命令执行函数

[![](https://p4.ssl.qhimg.com/t0192c69177d4840aff.png)](https://p4.ssl.qhimg.com/t0192c69177d4840aff.png)

寻找可控参数，

其中v19参数来源

[![](https://p2.ssl.qhimg.com/t01e5f6ba29e1d488e3.png)](https://p2.ssl.qhimg.com/t01e5f6ba29e1d488e3.png)

[![](https://p0.ssl.qhimg.com/t01690f5e9efc86be82.png)](https://p0.ssl.qhimg.com/t01690f5e9efc86be82.png)

usmUserprivkey可以是我们传入的参数,且没有经过过滤。

发包验证：

[![](https://p2.ssl.qhimg.com/t0157d1725a0a3375b0.png)](https://p2.ssl.qhimg.com/t0157d1725a0a3375b0.png)

[![](https://p5.ssl.qhimg.com/t01a324aaa567b463b2.png)](https://p5.ssl.qhimg.com/t01a324aaa567b463b2.png)

### <a class="reference-link" name="CVE-2021-1472"></a>CVE-2021-1472

权限绕过，仅存在于1.0.03.20

```
location /form-file-upload `{`
    include uwsgi_params;
    proxy_buffering off;
    uwsgi_modifier1 9;
    uwsgi_pass 127.0.0.1:9003;
    uwsgi_read_timeout 3600;
    uwsgi_send_timeout 3600;
`}`

location /upload `{`
    set $deny 1;

        if ($http_authorization != "") `{`
                set $deny "0";
        `}`

        if (-f /tmp/websession/token/$cookie_sessionid) `{`
                set $deny "0";
        `}`

        if ($deny = "1") `{`
                return 403;
        `}`

    upload_pass /form-file-upload;
    upload_store /tmp/upload;
    ‘’‘’‘
    ’‘’‘’
`}`
```

对于/upload的请求增加了一步验证，假设$http_authorization不为空，就可以越过该验证

查找$http_authorization取来源值

[![](https://p0.ssl.qhimg.com/t018fa09b5b8690aa34.png)](https://p0.ssl.qhimg.com/t018fa09b5b8690aa34.png)

即在头部增加 Authorization 即可令$http_authorization不为空

验证

如果sessionid合法且正确

[![](https://p5.ssl.qhimg.com/t01866122b5caa209b4.png)](https://p5.ssl.qhimg.com/t01866122b5caa209b4.png)

返回200

如果sessionid被篡改

[![](https://p1.ssl.qhimg.com/t01f513fc1134ca911e.png)](https://p1.ssl.qhimg.com/t01f513fc1134ca911e.png)

返回403

增加Authorization头后

[![](https://p5.ssl.qhimg.com/t01d38396f51262821e.png)](https://p5.ssl.qhimg.com/t01d38396f51262821e.png)

返回200

可证明漏洞存在

这个漏洞属于想法与实际的差别，所以在下一个版本中就删除了

### <a class="reference-link" name="CVE-2021-1473"></a>CVE-2021-1473

影响版本 RV34X 1.0.3.20 0.3.20 &amp; below,

<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E6%88%90%E5%9B%A0"></a>**漏洞成因**

漏洞点在upload.cgi中，处理upload请求时

[![](https://p4.ssl.qhimg.com/t01d800a7e2986bc451.png)](https://p4.ssl.qhimg.com/t01d800a7e2986bc451.png)

[![](https://p5.ssl.qhimg.com/t0140ac8d91d608cda6.png)](https://p5.ssl.qhimg.com/t0140ac8d91d608cda6.png)

处理函数sub_124A4中，可控的sessionid未经过滤作为参数传给popen

进入到这个函数中

[![](https://p1.ssl.qhimg.com/t013a9bd4802cbe440a.png)](https://p1.ssl.qhimg.com/t013a9bd4802cbe440a.png)

对于不同的处理方法需要额外增添不同的参数绕过（**这一点很重要**）

[![](https://p2.ssl.qhimg.com/t013afc8bcb92142e6b.png)](https://p2.ssl.qhimg.com/t013afc8bcb92142e6b.png)

回头看`sessionid`的获取过程，a1对应传入的第一个参数v3

[![](https://p1.ssl.qhimg.com/t01b89a74e564f05067.png)](https://p1.ssl.qhimg.com/t01b89a74e564f05067.png)

[![](https://p1.ssl.qhimg.com/t019a39ec9352f6f8e6.png)](https://p1.ssl.qhimg.com/t019a39ec9352f6f8e6.png)

即以分号做间隔，从cookie中取出sessionid，然后通过v3=v12+10取出session

取出sessionid 之后并没有对sessionid作任何检查。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E9%AA%8C%E8%AF%81"></a>漏洞验证

由于不能用`;`借助以前漏洞分析时取得的shell作辅助来验证

[![](https://p4.ssl.qhimg.com/t01f6c6efbbea5e4143.png)](https://p4.ssl.qhimg.com/t01f6c6efbbea5e4143.png)

执行前&amp;执行后

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011f7ae7572dd9677e.png)

采用分段命令执行 反弹shell



## 总结

该设备历代漏洞大都属于直接的命令执行，找到通过找到对应执行命令，寻找可以植入的参数，从而发现并利用漏洞，<br>
对于这类设备的重点应该是先理清楚对应路由处理，然后寻找传入参数被使用时是否存在直接的命令执行或者是栈溢出等问题，进行下一步利用
