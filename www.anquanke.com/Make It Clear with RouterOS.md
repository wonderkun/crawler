> 原文链接: https://www.anquanke.com//post/id/172862 


# Make It Clear with RouterOS


                                阅读量   
                                **228783**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t016d7b14929fd61036.jpg)](https://p4.ssl.qhimg.com/t016d7b14929fd61036.jpg)



作者：Larryxi@360GearTeam

## 0x00 再续前言

天才少年“Diving to the deep water”的[言论](https://github.com/j0nathanj/Publications/blob/master/35C3_From_Zero_to_Zero_Day/From_Zero_to_Zero_Day.pdf)让我打了个机灵，于是想看看大型一点的IoT项目上的安全问题，就这样我和[Bug Hunting in RouterOS](https://github.com/tenable/routeros/blob/master/bug_hunting_in_routeros_derbycon_2018.pdf)相遇了。议题中介绍了RouterOS的版本架构、历史研究和开发者后门，作者通过对通信解析的逆向介绍了客户端命令传递至后端的处理过程，最后组合漏洞链完成RCE的利用。不久之后，作者还写了[一篇](https://medium.com/tenable-techblog/make-it-rain-with-mikrotik-c90705459bc6)文章蜻蜓点水地补充了一点小细节和提供了利用开发的架构工具，也有同学对整个议题的内容深入[分析](https://www.anquanke.com/post/id/162457)了一番。

但我向来是一个喜欢知道为什么的人，而且如果要深入[挖掘](https://www.anquanke.com/post/id/146857)的话，作者没有多讲的逆向过程还是需要我们自己上下求索的，本文结合开发者后门提供的便利调试环境，主要对后端命令的分发过程和议题中触发漏洞message的字段处理及漏洞修复进行了逆向分析，而通信流量的编码和加解密过程以及Web端调用后台程序的过程需花另一篇幅逆向介绍，还请各位大拿海涵。



## 0x01 探索后门

议题PPT中上来就介绍如何开启开发者“后门”，这一步其实为了方便后续的调试与逆向，因为stable的不同[版本](https://mikrotik.com/download/archive)使开启方法略有不同，本小节以6.38.4和6.42.4为例简要介绍下方法，环境的搭建可自行[搜索](https://www.cnblogs.com/v5captain/p/9445700.html)。

### 6.38.4

下载[routeros-x86-6.38.4.npk](https://download.mikrotik.com/routeros/6.38.4/routeros-x86-6.38.4.npk)，binwalk解包即可看到squashfs-root的文件系统。需要开启后门的话，按照[PPT](https://github.com/tenable/routeros/blob/master/bug_hunting_in_routeros_derbycon_2018.pdf)中的说法，需要在原始的文件系统here/flash/nova/etc/下新建一个devel-login文件。做法是使用centos的镜像安全启动原RouterOS系统，自动或手动挂载文件系统，新建至根目录的软链接：

[![](https://p4.ssl.qhimg.com/t019e9dafc1c70aed70.png)](https://p4.ssl.qhimg.com/t019e9dafc1c70aed70.png)

顺便简要看一下在/nova/bin/login处理用户登录过程中存在开发者后门的原因，在程序初始化的过程中有一点判断用户名是否为devel的逻辑，如果是且通过sub_804E052函数的判断则把用户名更换为admin：

[![](https://p3.ssl.qhimg.com/t01182d25a2c2ff5666.png)](https://p3.ssl.qhimg.com/t01182d25a2c2ff5666.png)

继续跟进函数中，有目录的拼接并判断特殊文件是否存在：

[![](https://p0.ssl.qhimg.com/t01cf0d06a62f2e0a4d.png)](https://p0.ssl.qhimg.com/t01cf0d06a62f2e0a4d.png)

nv::getAllDirs对搜索的目录有简单的包装，如此可知如果使用ftp上传，使/flash/nova/etc/devel-login文件存在就能通过校验：

[![](https://p5.ssl.qhimg.com/t01e313039d8fa0d6a5.png)](https://p5.ssl.qhimg.com/t01e313039d8fa0d6a5.png)

所以当我们使用devel用户名和admin的密码登录成功后，即可获取到返回的shell：

[![](https://p0.ssl.qhimg.com/t0150181e61cbdda2d9.png)](https://p0.ssl.qhimg.com/t0150181e61cbdda2d9.png)

自带的shell还是功能受限的busybox，这时候可以利用同样的思路，ftp上传一个功能齐全的busybox（不能太新不然会段错误），加权限后即可大展身手了：

[![](https://p5.ssl.qhimg.com/t018d0e0681a8a040df.png)](https://p5.ssl.qhimg.com/t018d0e0681a8a040df.png)

### 6.42.4

对于[6.42.4](https://download.mikrotik.com/routeros/6.42.4/routeros-x86-6.42.4.npk)这样的高版本系统，作者在[Make It Rain with MikroTik](https://medium.com/tenable-techblog/make-it-rain-with-mikrotik-c90705459bc6)文章中提到了RouterOS会在系统的启动脚本S12defconf中执行/rw/DEFCONF的文件内容，控制该文件就能开启后门shell了，原文中专门录屏展示整个开telnetd的过程，此处不赘述。



## 0x02 流量解密

首先查看监听的端口来寻找可能存在的攻击面，80端口自然是第一考察对象：

**[![](https://p5.ssl.qhimg.com/t010aac5f0a22932751.png)](https://p5.ssl.qhimg.com/t010aac5f0a22932751.png)**

Web口登录过程中使用 Content-Type: text/plain;charset=UTF-8 Header，认证成功之后使用 Content-Type: msg ，并且从抓包上看都是向 /jsproxy POST加密过后的数据包。正如PPT所讲整个过程可在客户端的 /webfig/master-min-xxxxxxxxxxxx.js 中知晓，认证和会话密钥的生成用的是[MS-CHAP-2](https://tools.ietf.org/html/rfc3079#page-9)协议，但在[ChallengeResponse](https://tools.ietf.org/html/rfc2759#section-8.5)时对PasswordHash的padding做了些更改：

[![](https://p3.ssl.qhimg.com/t01273935893f506e71.png)](https://p3.ssl.qhimg.com/t01273935893f506e71.png)

在认证过程中使用的编码是UTF-8，可以在前端调试或者后端找到相应的处理逻辑：

[![](https://p0.ssl.qhimg.com/t01b9ebe00754b3abbc.png)](https://p0.ssl.qhimg.com/t01b9ebe00754b3abbc.png)

登录成功之后，前端至后端的message以buffer或json的形式传递，其字段值的类型还会对字段名的类型和编码有影响，同样也可以在前端代码中略见：** **

**[![](https://p1.ssl.qhimg.com/t0198dc2f689bcdfe24.png)](https://p1.ssl.qhimg.com/t0198dc2f689bcdfe24.png)**

对于[WinBox](https://wiki.mikrotik.com/wiki/Manual:Winbox)通信的binary形式的message的格式也是类似的。作者提供了[jsproxy_pcap_parser](https://github.com/tenable/routeros/tree/master/jsproxy_pcap_parser)和[winbox_pcap_parser](https://github.com/tenable/routeros/tree/master/winbox_pcap_parser)工具分别解析这两者的流量，就让我们先站在巨人的肩膀上，以后有机会再结合前后端对流量的包装进行详解。



## 0x03 消息处理

消息流量的传递处理对于后端程序来说有些RPC的意味， 0xff0001 数组中的system num决定调用哪个二进制文件，数组中的handler指定了处理函数，还有 0xff0007 字段的command则代表具体要执行的命令，下面分别对 /nova/bin/www 和 /nova/bin/mproxy 程序的消息处理过程进行逆向。

### /nova/bin/www

PPT中提到 /nova/bin 下面的二进制文件都可以通过HTTP或Winbox来触发到，CVE-2018-1156的[PoC](https://github.com/tenable/routeros/tree/master/poc/cve_2018_1156)也是如此，向 /jsproxy POST json信息的sysyetm num为55，对应地起后端程序 /nova/bin/licupgr 处理。

在 /nova/bin/www 程序中对于有 /jsproxy 的请求，其会先将 /nova/lib/www/jsproxy.p 作为Servlet进行动态加载：

[![](https://p5.ssl.qhimg.com/t0156029e4550d3cd46.png)](https://p5.ssl.qhimg.com/t0156029e4550d3cd46.png)

在 JSProxyServlet::JSProxyServlet 的初始化过程中，找到虚表中的 JSProxyServlet::doPost 为处理POST请求函数，在具体判断 Content-Type Header的内容后传递至 JSSession::processMessage ，通过调试可知解密完消息后传递至 threadExchangeMessage 函数，在线程间通过信号量传递消息：

[![](https://p0.ssl.qhimg.com/t01d1b69b000a782dd2.png)](https://p0.ssl.qhimg.com/t01d1b69b000a782dd2.png)

而在www程序 Looper::Looper 初始化过程中，有对 /ram/novasock 的socket添加：

[![](https://p4.ssl.qhimg.com/t019dedcc7a717e6948.png)](https://p4.ssl.qhimg.com/t019dedcc7a717e6948.png)

所以推测 /nova/bin/www 对 /jsproxy 传递来的消息，会通过 /ram/novasock 传递给 /nova/bin/loader ，由后者根据对 /nova/etc/loader/system.x3 的解析来调用后端程序处理：

[![](https://p3.ssl.qhimg.com/t011bf27e0309861f5d.png)](https://p3.ssl.qhimg.com/t011bf27e0309861f5d.png)

综上只是结合调试信息，对由system num调用后端程序的过程进行了大致推理，作者还提供了[parse_x3](https://github.com/tenable/routeros/tree/master/parse_x3)工具来解析系统号对应的程序，感兴趣的同学可以深入跟踪分析下。而消息中的handler和command会在新起的程序中处理，下小节以 /nova/bin/mproxy 为例进行分析。

### /nova/bin/mproxy

mproxy 直接监听的是8291端口，虽然没有 loader 分发命令的过程，但其处理消息的流程和其他后端程序类似。这里依旧使用CVE-2018-14847的[PoC](https://github.com/tenable/routeros/tree/master/poc/cve_2018_14847)构建调用命令，查看[解密](https://github.com/tenable/routeros/tree/master/winbox_pcap_parser)后传递的message：

[![](https://p5.ssl.qhimg.com/t019a78fd77e76df5db.png)](https://p5.ssl.qhimg.com/t019a78fd77e76df5db.png)

然后在PPT中提到的漏洞触发点下断点，进行栈回溯即可快速看到整个的调用链：

[![](https://p2.ssl.qhimg.com/t01e919f8c79c6fe7f7.png)](https://p2.ssl.qhimg.com/t01e919f8c79c6fe7f7.png)

跟踪可知在函数 sub_8055048 处判断system number是否为2：

[![](https://p5.ssl.qhimg.com/t01a03f88ca4d4c2c0c.png)](https://p5.ssl.qhimg.com/t01a03f88ca4d4c2c0c.png)

与 nv::Looper::addHandler 的逻辑相似，在 nv::Looper::dispatchMessage 中处理正确的handler后调用 nv::Handler::handle ，其中涉及到的 bff0005 字段代表 nv::isReplyExpected ：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b002fc6102522a95.png)

nv::Handler::handle 函数中间接调用了 nv::policies::is_allowed 来判断command是否具有相应的policy：

[![](https://p4.ssl.qhimg.com/t01a129736cf59a380a.png)](https://p4.ssl.qhimg.com/t01a129736cf59a380a.png)

在 set_policy 对应command为0时确实不需要任何认证即可调用：

[![](https://p3.ssl.qhimg.com/t0153e4497c261e4959.png)](https://p3.ssl.qhimg.com/t0153e4497c261e4959.png)

真正去处理command的函数 nv::Handler::handleCmd 实则是个大的switch-case，其把未知的命令传递给 nv::Handler::cmdUnknown 处理：

[![](https://p0.ssl.qhimg.com/t013342736b64b1ee60.png)](https://p0.ssl.qhimg.com/t013342736b64b1ee60.png)

对于handler 2其偏移76对应函数 sub_8052934 ，也是个小型的switch-case处理未知的命令，由此可探索更多的攻击面，下一小节会分析未知命令中存在的漏洞原理。

[![](https://p0.ssl.qhimg.com/t01a882559b06b8e1ac.png)](https://p0.ssl.qhimg.com/t01a882559b06b8e1ac.png)



## 0x04 漏洞分析

本小节以6.38.4为例，结合PPT中两个提及的漏洞，主要逆向分析message所需字段的原因。

### CVE-2018-1156

[CVE-2018-1156](https://github.com/tenable/routeros/tree/master/poc/cve_2018_1156)是一个需要认证的 /nova/bin/licupgr 文件的溢出，对应的System Number为55，其初始化过程中没有 nv::Looper::addHandler 的操作，直接在对应偏移处找到覆盖的 nv::Handler::cmdUnknown 来处理不同的command：

[![](https://p1.ssl.qhimg.com/t01a8694d1c27df9dd6.png)](https://p1.ssl.qhimg.com/t01a8694d1c27df9dd6.png)

跟进可知command 1和4均能到达目标的溢出函数 sub_804AC9E ，同时还需要传递 bool_id_7 参数：

[![](https://p1.ssl.qhimg.com/t018bf1f6ddd007c752.png)](https://p1.ssl.qhimg.com/t018bf1f6ddd007c752.png)

剩下 string_id_1 username 和 string_id_2 password 参数导致sprintf的溢出就显而易见了：

[![](https://p1.ssl.qhimg.com/t0172770b3964f4ec1f.png)](https://p1.ssl.qhimg.com/t0172770b3964f4ec1f.png)

### CVE-2018-14847

[CVE-2018-14847](https://github.com/tenable/routeros/tree/master/poc/cve_2018_14847)是一个无需认证利用目录穿越实现任意文件读取的漏洞，在拿到用户凭据user.dat文件后，使用写文件操作开启系统后门。对应的 /nova/bin/mproxy 文件在初始化过程中有和前文照应的 nv::Looper::addHandler 和 nv::policies::set_policy 操作：

[![](https://p3.ssl.qhimg.com/t01f1864141aa35fbd1.png)](https://p3.ssl.qhimg.com/t01f1864141aa35fbd1.png)

System number和handler均为2，在处理command 7中将文件路径和 /home/web/webfig/ 拼接传递至 nv::findFile 函数，就算是没有找到文件，其还会返回原始拼接的文件路径：

[![](https://p1.ssl.qhimg.com/t01c684a6dd416acb05.png)](https://p1.ssl.qhimg.com/t01c684a6dd416acb05.png)

随后其打开文件路径，并设置 u32_id_2 为文件的大小：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010941f347ba077089.png)

函数返回前还有对 0xFE0001 sessionid的设置：

[![](https://p2.ssl.qhimg.com/t01dee139e41c6c7fb1.png)](https://p2.ssl.qhimg.com/t01dee139e41c6c7fb1.png)

在处理完command返回消息调用 nv::Handler::replyMessage 的过程中，也有对 0xFF0006 RequestId的处理：

[![](https://p1.ssl.qhimg.com/t013581e6dceaa2bd82.png)](https://p1.ssl.qhimg.com/t013581e6dceaa2bd82.png)

在处理command 4时首先会验证sessionid的合法性：

[![](https://p5.ssl.qhimg.com/t01a6407c640df763df.png)](https://p5.ssl.qhimg.com/t01a6407c640df763df.png)

最终根据 u32_id_2 的大小从session打开的fd中读取文件数据：

[![](https://p1.ssl.qhimg.com/t01f7eb5f7a5cf614f7.png)](https://p1.ssl.qhimg.com/t01f7eb5f7a5cf614f7.png)



## 0x05 对比修复

### CVE-2018-1156

根据官方的[公告](https://blog.mikrotik.com/security/security-issues-discovered-by-tenable.html)可知这个溢出漏洞在[6.42.7](https://download.mikrotik.com/routeros/6.42.7/routeros-x86-6.42.7.npk)版本中完成修复，其使用 snprintf 函数来限制过长的用户输入：

[![](https://p0.ssl.qhimg.com/t01c085daaa85f4cecd.png)](https://p0.ssl.qhimg.com/t01c085daaa85f4cecd.png)

### CVE-2018-14847

我们还是聚焦于CVE-2018-14847这个利用目录穿越读取任意文件的漏洞，因为读取得到账号密码才能进行后一步的[BTW](https://github.com/tenable/routeros/tree/master/poc/bytheway)攻击。从官方的[公告](https://blog.mikrotik.com/security/winbox-vulnerability.html)可知6.29 至 6.42的current版本在6.42.1中完成修复，我这里就使用6.42.4和6.38.4进行对比。

使用[PoC](https://github.com/tenable/routeros/tree/master/poc/cve_2018_14847)直接去打 6.42.4 得到 File size is 0 的返回，初步推断在第一步获取文件大小时可能被直接返回了。通过对 /nova/bin/mproxy 的调试和bindiff分析，发现 6.42.4 在抵达handler 2 command 7的结构虽有改动但逻辑没有变化：

[![](https://p3.ssl.qhimg.com/t01f7e758d10cc994c6.png)](https://p3.ssl.qhimg.com/t01f7e758d10cc994c6.png)

调试可知 string_id_1 在经过 tokenize 函数的处理后，没能通过 sub_8051B80 的校验最终报错返回了。 tokenize 函数主要是把字符串 //./.././.././../etc/passwd 分解为 `{`“.”, “..”, “.”, “..”, “.”, “..”, “etc”, “passwd”`}` 这样的vector string。对于 6.42.4 patch的关键就在于 sub_8051B80 函数了：

[![](https://p2.ssl.qhimg.com/t0183c708f2febecb7f.png)](https://p2.ssl.qhimg.com/t0183c708f2febecb7f.png)

大致的逻辑就是遇到 “.” 就删除，遇到 “larry”, “..” 就一起删除这两项，但在删除后的遍历操作中如果遇到 “..” 打头，则认为是存在目录穿越的利用，无法通过校验。

反观 6.38.4 中的对应逻辑，也是不允许 “..” 打头，但没有照顾到 “.” ，就产生了作者使用 ./../ 的绕过方式：

[![](https://p2.ssl.qhimg.com/t016f62130514cb28c3.png)](https://p2.ssl.qhimg.com/t016f62130514cb28c3.png)

由于command 4的读取任意文件需要command 7打开文件的fd和返回的session id，一旦读取的文件路径无法通过校验，后续操作自然无法成功利用了。



## 0x06 总结哈子
1. 全文看下来虽说是逆向分析但难免有些钻牛角尖，局部的逆向是为了快速分析理解漏洞，全局的逆向分析则为了理解程序后端逻辑和寻找攻击面，也不可能锱铢必较。
1. 大体可以看出两点攻击面，一是自定义消息的处理解析，而是后端程序未知命令的处理逻辑。
1. 最近也有一篇RouterOS SMB服务溢出利用的[Write Up](https://medium.com/@maxi./finding-and-exploiting-cve-2018-7445-f3103f163cc1)，其将注意力放在了不是默认开启的SMB服务上，并快速使用dumb fuzz出crash也是个不错的尝试思路。