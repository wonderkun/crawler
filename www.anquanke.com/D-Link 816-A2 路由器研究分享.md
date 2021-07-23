> 原文链接: https://www.anquanke.com//post/id/187034 


# D-Link 816-A2 路由器研究分享


                                阅读量   
                                **515413**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t013c6a51606c83e9d6.png)](https://p3.ssl.qhimg.com/t013c6a51606c83e9d6.png)

## 1. 设备基础信息

设备硬件: D-Link 816-A2固件版本: 1.11固件下载地址:  http://forums.dlink.com/index.php?topic=74118.0

## 2. 基础准备工作

### 2.1. 焊接UART接口获取shell

通过拆卸焊接UART接口并测量电压后可以得到如下图所示的UART接口线序。

[![](https://p0.ssl.qhimg.com/t01b8ae78cdb2c2576b.png)](https://p0.ssl.qhimg.com/t01b8ae78cdb2c2576b.png)

通过连接串口转换器后，可以使用任意串口管理软件连接转换器查看信息，通过串口可以看到D-Link路由器启动时的引导信息 等系统成功引导以后按下回车键就就可以拿到root权限的shell了。

[![](https://p4.ssl.qhimg.com/t012d4492f552ac9a81.png)](https://p4.ssl.qhimg.com/t012d4492f552ac9a81.png)

### 2.2. 上传测试工具

D-Link 816-A2路由器的busybox shell经过了裁剪，没有wget，curl，netcat等各种方便上传工具的命令，只能通过tftp命令进行上传。因此这边可以考虑通过上传一个针对路由器CPU架构静态编译的busybox后即可使用更多的通用命令了。# 在本机上用python运行tftp, 可以使用pip安装

```
sudo ptftpd -p 69 en7 -D ./static_tools
sudo ptftpd -r -p 69 en7 -D ./# 上传静态编译的mips工具
tftp -g -r mips/busybox.mipsel 192.168.0.200
tftp -g -r mips/gdbserver.mipsle 192.168.0.200# 赋予工具可执行权限
chmod +x ./*2.3. 打包系统文件
```

在上传了新的busybox后即可使用tar命令对原始的系统文件进行打包。在对打包数据进行回传后即可对程序进行调试和逆向分析了。

```
# 打包命令

./busybox-mipsel tar -cvf ./system_backup.tar / --exclude=proc --exclude=run -
-exclude=dev --exclude=mnt --exclude=sys# 回传打包的数据
# 在自己本机上运行
nc -l 8080 &gt; system_backup.tar# 在路由器上执行
./busybox-mipsel nc 192.168.0.200 8080 &lt; system_backup.tar
```

至此我们已经成功的获取到路由器的内部文件，可以进一步的堆路由器进行深入分析了。

## 3. D-Link web管理页面分析

D-Link的Web管理页面是由goahead进程提供的，该进程监听TCP的80端口并提供路由器的管理功能。

### 3.1 管理页面权限验证方法分析

D-Link的登录页面如下图所示。

[![](https://p5.ssl.qhimg.com/t011cff216dbf7d5ba4.png)](https://p5.ssl.qhimg.com/t011cff216dbf7d5ba4.png)

输入账号密码后，将会向goform/formLogin接口发送如下图所示的数据包进行验证。从数据包中可以看到关键的参数有username，password以及tokenid，其中username使用了base64进行编码，password则进行了某种加密。

[![](https://p4.ssl.qhimg.com/t01eb26bb8726bc50e8.png)](https://p4.ssl.qhimg.com/t01eb26bb8726bc50e8.png)

有趣的是在成功认证后，服务器并没有返回session或者Cookie相关的数据，仅仅返回了一个重定向到index页面的数据包。

[![](https://p0.ssl.qhimg.com/t01cbb906eec0371c9b.png)](https://p0.ssl.qhimg.com/t01cbb906eec0371c9b.png)

通过对goahead程序的goform/formLogin接口函数进行分析可以看到在验证过程中函数首先会从nvram中读取Login及Password等参数。

[![](https://p3.ssl.qhimg.com/t0143220be6b5a7d012.png)](https://p3.ssl.qhimg.com/t0143220be6b5a7d012.png)

随后调用websGetVar函数从我们发送的请求数据中获取username,password,tokenid参数的值。

[![](https://p0.ssl.qhimg.com/t0171430fe3179f65eb.png)](https://p0.ssl.qhimg.com/t0171430fe3179f65eb.png)

之后将解析完成的，账号密码信息与nvram中保存的账号密码信息进行比对。

[![](https://p4.ssl.qhimg.com/t0190ee41685ea04d1e.png)](https://p4.ssl.qhimg.com/t0190ee41685ea04d1e.png)

如下图所示，当判断认证成功时将会记录用户的IP地址至BSS区的变量load_host中并修改login变量为1，失败则会将1写入/etc/RAMConfig/confirmlogin文件中，并重定向用户到登录页面。

[![](https://p0.ssl.qhimg.com/t0147746c24ece04a6a.png)](https://p0.ssl.qhimg.com/t0147746c24ece04a6a.png)

在更新BSS区的变量load_host后则会检测lan口和wan口的状态并返回对应的登录页面，随后将0写入/etc/RAMConfig/confirmlogin文件中。

[![](https://p0.ssl.qhimg.com/t0133bd08dc3dde2749.png)](https://p0.ssl.qhimg.com/t0133bd08dc3dde2749.png)

通过上述的分析，实际上D-Link路由器在认证成功后仅仅记录了成功登录的用户IP地址，随后将是否需要验证登录的Flag文件内容设置为了0。随后我们可以看一下goahead程序对于不同的url请求所使用的Handler，根据不同的url路径goahead进程将使用不同的Handler进行处理。下面可以看到有两个全局Handler,websSecurityHandler和websDefaultHandler。

[![](https://p1.ssl.qhimg.com/t01c477834c89512251.png)](https://p1.ssl.qhimg.com/t01c477834c89512251.png)

首先我们对默认的全局Handler函数websDefaultHandler进行分析。websDefaultHandler会调用websValidateUrl函数对请求的url地址进行检测，主要的功能是对转义符号进行处理并避免’../’路径穿越的问题。

[![](https://p5.ssl.qhimg.com/t01611c9320105e1e1e.png)](https://p5.ssl.qhimg.com/t01611c9320105e1e1e.png)

随后以’\’为分割符，循环遍历url中的路径，根据../及正常路径计算路径深度，避免出现../越界的情况。若是websValidateUrl合法，则将继续进行后续处理。

[![](https://p5.ssl.qhimg.com/t011a04edb54e39d8a9.png)](https://p5.ssl.qhimg.com/t011a04edb54e39d8a9.png)

用户访问管理页面时D-Link对全局认证状态的检测过程就在websSecurityHandler这个全局hanlder中。该函数会首先判断是否启用了portal管理，如果未进行portal管理则首先对login变量进行检测，查看是否存在已登录过的管理主机。后续的代码根据是否存在已认证的管理主机进行了两段额外的处理，接下来我们首先分析不存在登录管理主机的情况。此时如果用户请求的是asp的页面，则只允许访问/dir_login.asp或/login_fail.asp页面，其他asp页面均会被重定向成/dir_login.asp页面。而针对已存在登录管理主机的情况则会检测最近两次请求的间隔是否小于0x258(600)毫秒，如果小于600毫秒也会同样将请求重定向至/dir_login.asp。

[![](https://p0.ssl.qhimg.com/t011aed5b0c66acff10.png)](https://p0.ssl.qhimg.com/t011aed5b0c66acff10.png)

接下来的代码是共通的处理逻辑，在上图中的代码执行完毕后，会再一次对访问间隔进行检测，如果间隔小于0x258(600)毫秒，则会清空load_host及login等变量。

[![](https://p0.ssl.qhimg.com/t01ebc37380cbf53237.png)](https://p0.ssl.qhimg.com/t01ebc37380cbf53237.png)

如果间隔正常的话，则会继续判断发送请求的主机IP是否与load_host变量中的IP一致，如果不一致则将请求重定向至/dir_login.asp页面。接下来还会对是否存在访问限制进检测，随后结束这个Handler，将请求交由后续Handler处理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015eb819a91c37b3ce.png)

下图是将判断portal管理模式之后的验证过程进行整理后的流程图，根据下面的流程图可以发现。在websSecurityHandler中主要是对ASP页面的请求进行了权限控制，认证方法也仅仅是检测了一下当前请求主机的IP地址是否与储存的管理主机的IP地址一致。而针对非ASP页面的请求则交由其他后续的Handler进行权限处理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01eb02cca5d56e43c1.png)

另一个重要的Hander就是websFormHandler，下面将对该Handler的主要判断部分进行分析，该函数首先检查了是否存在/etc/RAMConfig/tokenid这个文件。如果文件不存在则创建该文件并写入随机数字后读取，存在的话则读取其中的数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d9d887623453a0a2.png)

随后调用websGetVar函数获取goform请求中的tokenid参数，并调用websValueCheck对请求数据进行过滤后与文件中的数据进行比对，检查是否一致。

[![](https://p1.ssl.qhimg.com/t01c98667a7f586465d.png)](https://p1.ssl.qhimg.com/t01c98667a7f586465d.png)

WebsValueCheck函数会对请求的数值进行过滤。过滤的关键字如下图所示，如果请求的数据中包含如下图所示的关键字则不会继续执行该请求。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0149bb21690c5edbb6.png)

当tokenid及其他请求的参数全部合法后则代表验证通过，此时将会从符号中读取所请求的form名对应的Handler后跳转执行，如果请求的form在符号中不存在，则会返回form未定义的报错。

[![](https://p0.ssl.qhimg.com/t01b64b89e72c5a0b6b.png)](https://p0.ssl.qhimg.com/t01b64b89e72c5a0b6b.png)

这里就出现一个问题了，对应form的请求D-Link只对tokenid进行了校验，这也意味着只要知道了tokenid, 无需进行其他验证即可调用所有支持的form请求。根据最初对登录过程的分析，tokenid可以通过访问/dir_login.asp页面进行获取，这也导致了我们能够直接获取到tokenid，从而越权调用所有D-Link支持的form请求。

### 3.2 form越权漏洞利用

通过对goahead的main函数进行分析，发现了大量的form定义处理的函数注册。

[![](https://p5.ssl.qhimg.com/t01fc2bf331876044f3.png)](https://p5.ssl.qhimg.com/t01fc2bf331876044f3.png)

通过对一些列的函数进行分析后，发现了不少有趣的功能，例如下图所示的SystemCommand。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01348d49004ee9e1b8.png)

非常简单粗暴，直接传参command即可进行命令执行。

[![](https://p1.ssl.qhimg.com/t01c26b3b1c2152a78a.png)](https://p1.ssl.qhimg.com/t01c26b3b1c2152a78a.png)

类似的form有很多，通过对部分form进行分析后发现，除了远程命令执行外，还存在越权修改账号密码、查看系统日志、清空系统日志、重置设备等一系列的危险调用。

## 4. 固件升级流程分析

D-Link DIR-816的升级页面如下图所示。

[![](https://p1.ssl.qhimg.com/t016890e1208713738e.png)](https://p1.ssl.qhimg.com/t016890e1208713738e.png)

选择升级包后点击上传，将会把文件使用post的方式发送给/cgi-bin/upload.cgi接口。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016dff5d3105fde3b4.png)

根据之前对goahead的分析，cgi-bin目录所对应的Handler函数为websCgiHandler该函数最后会通过调用websLaunchCgiProc函数执行对应的cgi-bin文件。

[![](https://p5.ssl.qhimg.com/t01e428b9c3ceb42153.png)](https://p5.ssl.qhimg.com/t01e428b9c3ceb42153.png)

在websLaunchCgiProc函数中将会fork一个子进程，随后调用execve来执行cgi-bin文件。

[![](https://p3.ssl.qhimg.com/t0118b3d937ee22d768.png)](https://p3.ssl.qhimg.com/t0118b3d937ee22d768.png)

通过在fork函数处下断点。我们可以结合上图的代码间接的分析出execve函数的参数。

[![](https://p0.ssl.qhimg.com/t019bd1d061c2a68a73.png)](https://p0.ssl.qhimg.com/t019bd1d061c2a68a73.png)

POST请求的头部和尾部数据如下图所示。

[![](https://p2.ssl.qhimg.com/t0134ec58f5fff81d8c.png)](https://p2.ssl.qhimg.com/t0134ec58f5fff81d8c.png)

### 4.1 upload.cgi分析

通过对upload.cgi文件进行分析后发现，该文件会从环境变量中读取SERVER_SOFTWARE 及UPLOAD_FILENAME这两个变量。

[![](https://p0.ssl.qhimg.com/t0128da5eda93f4b3d5.png)](https://p0.ssl.qhimg.com/t0128da5eda93f4b3d5.png)

因此我们可以利用如下代码直接调用upload.cgi进行测试分析。
- SERVER_SOFTWARE=lbp_server UPLOAD_FILENAME=/var/cgiHNYyMd /etc_ro/web/cgi-bin/upload.cgi
命令执行后upload.cgi会将上传的固件进行解析随后写入flash中。

[![](https://p2.ssl.qhimg.com/t015e450376de5821b1.png)](https://p2.ssl.qhimg.com/t015e450376de5821b1.png)

接下来继续对upload.cgi进行分析，查看该程序实际执行了哪些操作。在代码头部有一系列的文字处理代码，用途是从我们发送的POST请求数据中提取文件内容，并保存到/var/image.img文件中。随后调用/bin/imgdecrypt命令对提取的固件进行解密操作。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e7fec53aceb8a169.png)

完成解密操作后，调用/bin/mtd_write命令将解压后的固件写入flash中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f602c6cefc4cede5.png)

upload.cgi的主要工作就是上面说明的这些，因此固件升级的核心部分就是/bin/imgdecrypt命令。

### 4.2 imgdecrypt分析

imgdecrypt比较有趣，他会根据自身文件名来判断执行镜像的解密或加密操作。

[![](https://p1.ssl.qhimg.com/t01795c9aaa9268084b.png)](https://p1.ssl.qhimg.com/t01795c9aaa9268084b.png)

在decrypt_firmare函数头部，首先会将0123456789ABCDEF字符串写入到栈中。

[![](https://p3.ssl.qhimg.com/t01e8dbbf6365fdd273.png)](https://p3.ssl.qhimg.com/t01e8dbbf6365fdd273.png)

随后调用sub_40266C函数计算用于解密镜像的key。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01735215da984c2762.png)

通过对在sub_40266C 函数进行分析后，可以发现改函数主要从地址0x403010处开始获取用于aes解密的key，iv等一系列的数据。随后调用decryptData函数进行解密。

[![](https://p5.ssl.qhimg.com/t0107e8de660d31e44e.png)](https://p5.ssl.qhimg.com/t0107e8de660d31e44e.png)

0x403010 地址处的数据如下图所示，成功利用下列数据解密后的key为C05FBF1936C99429CE2A0781F08D6AD8。后续的代码会将计算完的key在终端进行打印。

[![](https://p0.ssl.qhimg.com/t01bfcbecfa2bbfc907.png)](https://p0.ssl.qhimg.com/t01bfcbecfa2bbfc907.png)

打印出的key和aes解密结算的结果与之前计算的一致。

[![](https://p1.ssl.qhimg.com/t01fd90a04c8b8874f2.png)](https://p1.ssl.qhimg.com/t01fd90a04c8b8874f2.png)

随后程序会调用verify_image对镜像进行解密操作，相关的参数如下图所示。

[![](https://p0.ssl.qhimg.com/t01fb30b2c56454d2ce.png)](https://p0.ssl.qhimg.com/t01fb30b2c56454d2ce.png)

verify_image函数首先会判断镜像的头部是否为SHRS。通过对verify_image头部的代码进行分析后发现，该函数首先会判断image头部的magic是否为SHRS，

[![](https://p3.ssl.qhimg.com/t018354f7eb8944d39c.png)](https://p3.ssl.qhimg.com/t018354f7eb8944d39c.png)

随后从镜像中的第8~12个字节读取用于解密数据的长度字段，接着在镜像文件偏移量0x6dc开始获取加密的数据内容进行sha512校验，将结果与镜像偏移量0x9C处的sha512值进行比对。镜像头部的部分结构如下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018f597c9132a421bf.png)

在0x9C处存储了加密数据的sha512校验值。

[![](https://p2.ssl.qhimg.com/t017d9bef2dc074e97d.png)](https://p2.ssl.qhimg.com/t017d9bef2dc074e97d.png)

在0x5C处存储了原始数据的sha512校验值。

[![](https://p5.ssl.qhimg.com/t01aa268e493f2469b4.png)](https://p5.ssl.qhimg.com/t01aa268e493f2469b4.png)

当加密数据的SHA512值校验通过后，将会对加密数据调用decryptData进行解密，decryptData函数的参数如下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e33c19a9bfa17f77.png)

decryptData函数调用的参数值如下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0184ac5a0527663c0e.png)

解密完成后，将会计算解密后数据的SHA512值并从镜像0x5C处读取SHA512值并进行校验。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a3fdc8739be18966.png)

在完成了全部的校验值计算后会调用verifyMD对解密和加密的数据进行RSA签名验证。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01adec22e377e3927d.png)

当签名全部验证通过后，将会把解密后的镜像保存到/var/.firmware.orig文件中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0100912357a3bad57e.png)

随后回到upload.cgi中，调用/bin/mtd_write命令将解密后的镜像文件写入到flash中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012db3eb0f471fbea3.png)

至此固件升级的流程就分析完毕了，由于固件升级包使用了RSA签名校验，因此直接伪造固件升级包的难度很大，只能与其他漏洞相结合的方式实现写入自定义固件的效果。

## 5. 自定义固件写入研究

D-Link DIR-816 A2路由器的文件系统是直接加载在内存中的，每次重启后都会从flash中的kernel image里重新读取加载。这样的设计方式可以提升系统的健壮性，在避免异常断电造成的文件损坏的同时，也使得传统恶意程序无法驻留在路由器中。本章节主要为了方便后续的研究及对植入驻留型恶意程序的可行性进行探索，对该路由器刷写自定义固件的方法进行了探索及研究。

### 5.1 防砖准备工作

为了能够安全的进行固件写入测试，首先我们需要对flash中的固件进行备份，可以直接从flash中提取或是利用上一章节的方法从固件升级包中进行解密提取。下面是通过使用dd命令将MTD设备中的Kernel部分导出到web目录后进行下载备份的方法。PS: 有Flash编程器的可以免去后续这些麻烦，直接通过编程器从Flash中读取备份。使用DD命令直接从MTD设备中导出到路由器的web目录，随后即可通过网页http://192.168.0.1/mtd4_Kernel.dump直接下载cat /proc/mtd

```
------------------output------------------
dev: size erasesize name
mtd0: 00400000 00010000 "ALL"
mtd1: 00030000 00010000 "Bootloader"
mtd2: 00010000 00010000 "Config"
mtd3: 00010000 00010000 "Factory"
mtd4: 003b0000 00010000 "Kernel"
------------------------------------------/home/busybox.mipsel dd if=/dev/mtd4 of=/etc_ro/web/mtd4_Kernel.dump
------------------output------------------
7552+0 records in
7552+0 records out
3866624 bytes (3.7MB) copied, 1.412360 seconds, 2.6MB/s
------------------------------------------
```

备份完固件后若测试中出现系统异常，只要uboot部分没有被破坏，即可使用路由器uboot引导界面的第二个菜单功能，进行固件的刷写还原。通过配置tftp服务器及文件名称后即可通过tftp进行固件的还原。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cd3cd7511c6f6c02.png)

### 5.2 linux kernel image分析

由于我们的目的是修改路由器内核中打包的文件，实现篡改数据或植入恶意程序的目的，因此首先要对封装的Linux kernel image进行分析。首先使用binwalk对备份的kernel image进行分析可以发现这是一个uimage封装并使用lzma压缩的linux kernel image文件。下面的代码用于手动从uimage封装的文件中提取lzma压缩的kernel image文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01af167751cf983769.png)

根据uimage中image size字段的大小3772774字节。

dd if=mtd4_Kernel.dump of=kernel_image.lzma bs=1 skip=64 count=3772774此处遇到了一个坑，一定不能使用新版本的lzma去压缩，必须要使用特定版本的lzma工具才能正常解压和压缩。通过观察设备的启动过程可以发现设备是基于ralink的sdk进行开发的，因此我们也需要编译对应sdk中的lzma和xz等工具对镜像文件进行处理，否则再重打包镜像时会出现如下图所示的错误信息。

[![](https://p5.ssl.qhimg.com/t017211093d3c7fa5df.png)](https://p5.ssl.qhimg.com/t017211093d3c7fa5df.png)

可以在网上搜索MediaTek_ApSoC_SDK_4320_20150414.tar.bz2这个版本的SDK，经测试该SDK中的工具可以用于成功处理我们的这个镜像文件。使用编译好的lzma工具即可成功的解压该镜像文件，使用binwalk对解压后的文件进行分析可以看到该kernel image中有一个使用xz压缩的文件。基本上在linux kernel image中使用xz压缩的大多都是rootfs文件，也就是我们实际在路由器中看到的那些文件。

[![](https://p2.ssl.qhimg.com/t01c1a0047d0d892f81.png)](https://p2.ssl.qhimg.com/t01c1a0047d0d892f81.png)

由于linux kernel image本身是一个可执行文件，使用binwalk自动解压会导致提取出不属于xz部分的数据。[根据](https://github.com/addaleax/xz/blob/master/doc/xz-file-format.txt)xz文件格式的特征可以知道xz压缩文件有其特定的起始标识\xFD\x37\x7A\x58\x5A\x00和结束标识\x59\x5A通过对文件进行分析后，即可得到xz文件在镜像中的正确起始及结束地址，提取和解压的命令如下。

```
dd if=kernel_image of=root_fs.xz bs=1 skip=4763648 count=2384780# 查看xz文件的内容
```

```
~/IoT/tool/bin/xz -l root_fs.xz
------------------output------------------
Strms Blocks Compressed Uncompressed Ratio Check Filename
1 1 2,328.9 KiB 9,294.0 KiB 0.251 CRC32 root_fs.xz
------------------------------------------

# 解压xz文件
~/IoT/tool/bin/xz -d root_fs.xz
```

通过使用file命令可以得知解压后的xz数据是一个cpio归档文件，进一步查看后可以确认这个文件就是我们所需要修改的root_fs文件。

```
# 确认解压后的文件类型
file root_fs
------------------output------------------
root_fs: ASCII cpio archive (SVR4 with no CRC)
------------------------------------------

# 使用cpio命令查看归档的文件列表
cpio -tv -F root_fs|more
------------------output------------------
drwxrwxr-x 2 541 541 0 Aug 24 19:30 /sys
drwxrwxr-x 2 541 541 0 Aug 24 19:30 /mnt
drwxrwxr-x 2 541 541 0 Aug 24 19:30 /dev
crw--w--w- 1 root 541 240, 0 Aug 24 19:30 /dev/ac0
crw-rw---- 1 root 541 90, 8 Aug 24 19:30 /dev/mtd4
crw--w--w- 1 root 541 217, 0 Aug 24 19:30 /dev/spiS0
crw--w--w- 1 root 541 4, 64 Aug 24 19:30 /dev/ttyS0
brw-rw---- 1 root 541 31, 1 Aug 24 19:30 /dev/mtdblock1
brw-rw---- 1 root 541 31, 6 Aug 24 19:30 /dev/mtdblock6
crw--w--w- 1 root 541 251, 0 Aug 24 19:30 /dev/nvram
crw-rw-rw- 1 root 541 5, 2 Aug 24 19:30 /dev/ptmx
crw-rw-rw- 1 root 541 1, 3 Aug 24 19:30 /dev/null
crw--w--w- 1 root 541 218, 0 Aug 24 19:30 /dev/i2cM0
crw-rw---- 1 root 541 90, 1 Aug 24 19:30 /dev/mtd0ro
crw-rw-rw- 1 root 541 1, 2 Aug 24 19:30 /dev/kmem
crw--w--w- 1 root 541 253, 0 Aug 24 19:30 /dev/rdm0
brw-rw---- 1 root 541 31, 2 Aug 24 19:30 /dev/mtdblock2
------------------------------------------
```

下一步就是提取cpio中的文件了，提取命令如下。

```
创建目录rootfs
mkdir rootfs
cd rootfs
# 解压root_fs归档中的文件到rootfs目录中
cat ../root_fs | cpio -idmvH newc --no-absolute-filenames
```

```
# 成功解压后即可在目录中看到归档中的文件了。
ls -la
------------------output------------------
total 64
drwxr-xr-x 16 hack hack 4096 1月 16 11:55 .
drwxr-xr-x 4 hack hack 4096 1月 16 11:55 ..
drwxrwxr-x 2 hack hack 4096 1月 16 11:55 bin
drwxrwxr-x 3 hack hack 4096 1月 16 11:55 dev
drwxrwxr-x 2 hack hack 4096 1月 16 11:55 etc
drwxrwxr-x 9 hack hack 4096 1月 16 11:55 etc_ro
drwxrwxr-x 2 hack hack 4096 1月 16 11:55 home
lrwxrwxrwx 1 hack hack 11 1月 16 11:55 init -&gt; bin/busybox
drwxr-xr-x 4 hack hack 4096 1月 16 11:55 lib
drwxrwxr-x 2 hack hack 4096 8月 24 19:30 media
drwxrwxr-x 2 hack hack 4096 8月 24 19:30 mnt
drwxrwxr-x 2 hack hack 4096 8月 24 19:30 proc
drwxrwxr-x 2 hack hack 4096 1月 16 11:55 sbin
------------------------------------------
```

此时我们就可以在这个目录里对原始的文件进行任意的修改，或增加新的文件进去。不过需要注意的是DIR-816 A2路由器所使用的flash容量一共是4M,原始镜像已经几乎占满了所有的空间，因此很难在追加什么新大文件进去。

### 5.3 重打包linux kernel image

重打包的方法其实就是把解开分析rootfs的方法反着做一遍即可，此处会在进行cpio归档时遇到一个小问题，cpio归档时无法修改归档文件的路径信息，也就是说我们无法将rootfs目录下的文件路径信息修改为/。进入rootfs目录

```
cd rootfs# 归档rootfs下的所有文件
find . |cpio -H newc -o &gt; ../root_fs.cpio
```

```
# 查看归档的结果,可以发现文件归档的路径是相对路径。
cpio -tv -F ../root_fs.cpio|more
------------------output------------------
drwxr-xr-x 16 hack hack 0 Jan 16 11:55 .
drwxrwxr-x 2 hack hack 0 Jan 16 11:55 sbin
-rwxr-xr-x 1 hack hack 29541 Aug 24 19:29 sbin/internet.sh
-rwxr-xr-x 1 hack hack 3073 Aug 24 19:29 sbin/config-powersave.sh
lrwxrwxrwx 1 hack hack 14 Jan 16 11:55 sbin/poweroff -&gt; ../bin/busybox
-rwxr-xr-x 1 hack hack 7356 Aug 24 19:29 sbin/lan.sh
-rwxr-xr-x 1 hack hack 8981 Aug 24 19:29 sbin/virtual_server_dmz_s
------------------------------------------
```

此时有个小技巧，可以使用pax命令行工具进行重打包, 利用pax工具的-s参数将路径名进行替换操作。

使用pax打包rootfs目录，并对文件路径使用-s参数替换，替换语法和sed命令的替换方法相同。<br>
pax -w -x sv4cpio -s ‘/rootfs//’ rootfs &gt; root_fs.cpio

```
# 查看归档的结果,可以发现文件归档的路径已被改写为/目录。
cpio -tv -F root_fs.cpio|more
------------------output------------------
drwxrwxr-x 2 hack hack 0 Jan 16 11:55 /sbin
-rwxr-xr-x 1 hack hack 29541 Aug 24 19:29 /sbin/internet.sh
-rwxr-xr-x 1 hack hack 3073 Aug 24 19:29 /sbin/config-powersave.sh
lrwxrwxrwx 1 hack hack 14 Jan 16 11:55 /sbin/poweroff -&gt; ../bin/busybox
-rwxr-xr-x 1 hack hack 7356 Aug 24 19:29 /sbin/lan.sh
-rwxr-xr-x 1 hack hack 8981 Aug 24 19:29 /sbin/virtual_server_dmz_set2.sh
-rwxr-xr-x 1 hack hack 5120 Aug 24 19:29 /sbin/lan_web_filter.sh
-rwxr-xr-x 1 hack hack 1840 Aug 24 19:29 /sbin/portal_manage.sh
-rwxr-xr-x 1 hack hack 1143 Aug 24 19:29 /sbin/automount.sh
-rwxrwxr-x 1 hack hack 238 Aug 24 19:29 /sbin/pt_hotplug
------------------------------------------
```

在完成了上述准备工作后即可使用如下python脚本进行重打包。

```
# !/usr/bin/env python2
# coding=utf-8
import sys
import os
original_image_file = open("kernel_image", 'rb')
original_image_data = original_image_file.read()
original_xz_root_fs_start_offset = 0x48b000
original_root_fs_end_offset = 0x6d138c
original_root_fs_size = original_root_fs_end_offset - original_xz_root_fs_start_offset

working_folder = '/home/hack/IoT/D-Link_image'
root_fs_folder_name = 'rootfs'
xz_path = '/home/hack/IoT/tool/bin/xz'
lzma_path = '/home/hack/IoT/tool/bin/lzma'

# archive rootfs with cpio
cpio_archive_cmd = "cd %s ;pax -w -x sv4cpio -s '/%s//' %s &gt; root_fs.cpio" % (working_folder, root_fs_folder_name, root_fs_folder_name)
print("execute: %s" % cpio_archive_cmd)
os.popen(cpio_archive_cmd)

# compress rootfs with xz
xz_cmd = "cd %s ;%s --check=crc32 -z -c root_fs.cpio &gt; root_fs.cpio.xz" % (working_folder, xz_path)
print("execute: %s" % xz_cmd)
os.popen(xz_cmd)

# repack_image
new_image_name = 'kernel_image_hacked.img'
new_image = open(new_image_name, 'wb')
new_xz_root_fs_path = 'root_fs.cpio.xz'
new_xz_root = open(new_xz_root_fs_path, 'rb')
new_xz_root_data = new_xz_root.read()
if len(new_xz_root_data) &gt; original_root_fs_size:
print("new image is too big, exit")
sys.exit()

new_image_data = original_image_data[:original_xz_root_fs_start_offset]
new_image_data += new_xz_root_data + ('\x00' * (original_root_fs_size - len(new_xz_root_data)))
new_image_data += original_image_data[original_root_fs_end_offset:]
new_image.write(new_image_data)

# compress image with lzma
lzma_cmd = "cd %s ;rm kernel_image_hacked.img.lzma; %s -z kernel_image_hacked.img" % (working_folder, lzma_path)
print("execute: %s" % lzma_cmd)
os.popen(lzma_cmd)

# make uimage
mkimg_cmd = 'cd %s; mkimage -A MIPS -O Linux -T kernel -C lzma -n "Linux Kernel Image" -a 80000000 -e 8000C2F0 -d kernel_image_hacked.img.lzma kernel_image_hacked.uimg' % (working_folder)
os.popen(mkimg_cmd)
```

至此一个重新打包过的linux kernel image就制作完成了，我们可以直接使用uboot中刷写Linux Kernel的功能或是利用漏洞将文件上传到服务器后结合命令执行漏洞直接调用mtd_write命令进行linux kernel image的覆写操作。作为实验，我改写了hw_nat.sh文件，添加了从远端下载shell脚本自动执行的功能。

[![](https://p4.ssl.qhimg.com/t0171dc9d0373ddae11.png)](https://p4.ssl.qhimg.com/t0171dc9d0373ddae11.png)

这样在路由器启动时就会从tftp服务器中下载shell脚本并执行了。终于不用每次都手工上传gdbserver和busybox了@_@。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012c150d4d8a0ff078.png)

## 6. 总结

这篇文章主要分享的是我研究D-Link DIR-816 A2路由器的过程以及遇到的一些坑，希望这篇文章能够帮助到那些对IoT安全研究感兴趣或是苦于无从下手的同学们。这款路由器的安全问题还是比较多的，针对发现的安全漏洞我们也已于今年1月提交给了D-Link厂商。

PS: 设备中还存在疑似后门的开启telnet服务的特殊代码 ^ ^。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015cb269bd896697a4.png)

本文由 Galaxy Lab 作者：[小黑猪](http://galaxylab.com.cn/author/64/) 发表，其版权均为 Galaxy Lab 所有，文章内容系作者个人观点，不代表 Galaxy Lab 对观点赞同或支持。如需转载，请注明文章来源。
