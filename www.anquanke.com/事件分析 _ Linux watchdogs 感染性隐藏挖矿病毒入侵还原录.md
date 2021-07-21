> 原文链接: https://www.anquanke.com//post/id/171523 


# 事件分析 | Linux watchdogs 感染性隐藏挖矿病毒入侵还原录


                                阅读量   
                                **337523**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/dm/1024_569_/t0161d11377ff4c91d5.jpg)](https://p3.ssl.qhimg.com/dm/1024_569_/t0161d11377ff4c91d5.jpg)



## 一、背景

近日，腾讯云安全团队监测到部分云上及外部用户机器存在安全漏洞被入侵，同时植入 watchdogs 挖矿病毒，出现 crontab 任务异常、系统文件被删除、CPU 异常等情况，并且会自动感染更多机器。攻击者主要利用 Redis 未授权访问入侵服务器并通过内网扫描和 known_hosts 历史登录尝试感染更多机器。（对此，腾讯云安全团队第一时间发布了病毒预警——[预警 | 中招 watchdogs 感染性挖矿病毒，如何及时止损？](https://mp.weixin.qq.com/s/lyXHI3zEE8cujn3r6Su_mw)）

相较于过去发现的挖矿病毒，这次的挖矿病毒隐藏性更高，也更难被清理。服务器被该病毒入侵后将严重影响业务正常运行甚至导致奔溃，给企业带来不必要的损失。



## 二、脚本分析

首先，可以直接从crontab任务中看到异常的任务项：

[![](https://p3.ssl.qhimg.com/t0155346aa2d73b43fc.png)](https://p3.ssl.qhimg.com/t0155346aa2d73b43fc.png)

该crontab任务实现从 hxxps://pastebin.com/raw/sByq0rym 下载shell脚本并执行，shell脚本内容为：

[![](https://p4.ssl.qhimg.com/t01c5e3bcab61ac529c.png)](https://p4.ssl.qhimg.com/t01c5e3bcab61ac529c.png)

该脚本实现从 hxxps://pastebin.com/raw/tqJjUD9d 下载文件，文件内容为经过base64编码处理；

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01285ede33cd9c7940.png)

base64解码后为shell脚本，shell脚本主要功能如下：

1. 修改环境变量，将常见的可执行文件目录添加到系统路径中，确保脚本中的shell命令正常执行；同时再次覆写crontab任务。

[![](https://p2.ssl.qhimg.com/t01e1eec1cae7743f02.png)](https://p2.ssl.qhimg.com/t01e1eec1cae7743f02.png)

2. 清理其他恶意程序，如“kworkerds”，“ddgs”等挖矿程序；同时通过chattr -i等命令解锁和清理相关系统文件

[![](https://p5.ssl.qhimg.com/t016703c9d39e633c6c.png)](https://p5.ssl.qhimg.com/t016703c9d39e633c6c.png)

<!--[endif]-->3. 根据系统信息下载对应恶意程序执行；黑客主要通过将恶意程序伪装成图片上传hxxp://thyrsi.com图床站点，shell脚本下载hxxp://thyrsi.com/t6/672/1550667515×1822611209.jpg保存为/tmp/watchdogs文件，赋予可执行权限后执行该恶意程序；

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f125b377a2ded17a.png)

4. 再进一步横向扩展感染，检查本地 ssh 凭证，遍历/root/.ssh/known_hosts文件中的IP地址，利用默认公钥认证方式进行SSH连接，执行恶意命令横向扩展感染；

[![](https://p0.ssl.qhimg.com/t01f36215970e84e51d.png)](https://p0.ssl.qhimg.com/t01f36215970e84e51d.png)

5. 最后清空系统日志等文件，清理入侵痕迹。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eeadc3d82c0ad3bc.png)

通过bash脚本我们可以得知关键文件为其中的watchdogs文件。

进一步通过top命令未见异常进程，而CPU空闲率为100%，但又明显感觉到机器运行迟缓。

[![](https://p1.ssl.qhimg.com/t013cc67056f36607ef.png)](https://p1.ssl.qhimg.com/t013cc67056f36607ef.png)

进一步通过vmstat进行确认，可以发现CPU使用率95%以上，由此可以推断存在隐藏进程，并且hook了相关readdir 等方法，具体案例我们在以前的文章已经做过分析。

[安全研究 | Linux 遭入侵，挖矿进程被隐藏案例分析](https://mp.weixin.qq.com/s/1AF5cgo_hJ096LmX7ZHitA)

[![](https://p3.ssl.qhimg.com/t01c44296023fc23233.png)](https://p3.ssl.qhimg.com/t01c44296023fc23233.png)

进一步分析watchdogs文件，可以清楚看到病毒释放了/usr/local/lib/libioset.so的动态链接库并将路径写入/etc/ld.so.preload来实现了进程的隐藏，与我们上面的推测是一致的。具体可见样本分析部分。

## 三、样本分析

### **样本 watchdogs**

主要功能：

1.获取当前进程id，写入/tmp/.lsdpid文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0175c2310b5e95fc54.png)

2. 拷贝 /tmp/watchdogs至/usr/sbin/watchdogs路径，并将watchdogs添加至启动项及服务项

[![](https://p4.ssl.qhimg.com/t01f9db761e330c9f88.png)](https://p4.ssl.qhimg.com/t01f9db761e330c9f88.png)

[![](https://p3.ssl.qhimg.com/t01f6e7b7ba0e3f5a24.png)](https://p3.ssl.qhimg.com/t01f6e7b7ba0e3f5a24.png)

3. 释放libioset.so文件至/usr/local/lib/libioset.so，并将该so文件路径写入/etc/ld.so.preload，同时删除/usr/local/lib/libioset.c文件

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eb211e0318b9cdfe.png)<!--[endif]--><br>
4. 访问ident.me获取机器IP

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t01f39d975dfd80675f.png)](https://p3.ssl.qhimg.com/t01f39d975dfd80675f.png)<!--[endif]-->

5. 设置定时任务，定时从 [https://pastebin.com/raw/sByq0rym](https://pastebin.com/raw/sByq0rym) 上获取shell执行脚本

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p4.ssl.qhimg.com/t01297ddc49b2e4ed5f.png)](https://p4.ssl.qhimg.com/t01297ddc49b2e4ed5f.png)<!--[endif]-->

6. 写入/tmp/ksoftirqds、/tmp/config.json，执行ksoftirqds后删除

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014b171b213e601b83.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p5.ssl.qhimg.com/t01bddd73b4f5335c8d.png)](https://p5.ssl.qhimg.com/t01bddd73b4f5335c8d.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t01dd6c0939e3912341.png)](https://p3.ssl.qhimg.com/t01dd6c0939e3912341.png)<!--[endif]-->

7. 删除生成的相关文件

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0113da86dd62d3515c.png)<!--[endif]-->

8. 访问 [https://pastebin.com/raw/C4ZhQFrH](https://pastebin.com/raw/C4ZhQFrH) 检查更新

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p1.ssl.qhimg.com/t01b4cc5fcdbfe96f09.png)](https://p1.ssl.qhimg.com/t01b4cc5fcdbfe96f09.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

### <!-- [if !vml]-->[![](https://p5.ssl.qhimg.com/t011b15b43032d60648.png)](https://p5.ssl.qhimg.com/t011b15b43032d60648.png) **样本 libioset.so**

64位程序中，恶意样本会释放出libioset.c文件，采用源码编译的方式生成libioset.so文件，而32位程序则直接释放出libioset.so文件

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012d0e4380b689dd76.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p0.ssl.qhimg.com/t01ae9695bf59c5ee43.png)](https://p0.ssl.qhimg.com/t01ae9695bf59c5ee43.png)<!--[endif]-->

libioset.so主要功能为hook删除、查看等系统命令函数，过滤掉watchdogs等相关信息，导致ls、rm等命令对该恶意程序无效，该so文件导出函数如下所示

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p5.ssl.qhimg.com/t016ec1e0545803a186.png)](https://p5.ssl.qhimg.com/t016ec1e0545803a186.png)<!--[endif]-->

例如，readdir64函数中，加载了libc.so.6

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p4.ssl.qhimg.com/t01e0a85e4e2b17f445.png)](https://p4.ssl.qhimg.com/t01e0a85e4e2b17f445.png)<!--[endif]-->

获取原始函数地址

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p2.ssl.qhimg.com/t0198511e318791d9d7.png)](https://p2.ssl.qhimg.com/t0198511e318791d9d7.png)<!--[endif]-->

如果调用该函数的进程不是ksoftirqds或watchdogs，则过滤掉所有包含恶意程序相关的结果。

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p5.ssl.qhimg.com/t01ff84852ca83e7ae6.png)](https://p5.ssl.qhimg.com/t01ff84852ca83e7ae6.png)<!--[endif]-->

unlink函数同样进行了过滤，导致无法清除恶意程序相关的LD_PRELOAD、libioset.so等。

该恶意程序同样隐藏了CPU信息和网络连接信息，如下所示：

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p1.ssl.qhimg.com/t01054c37e1753aa9ce.png)](https://p1.ssl.qhimg.com/t01054c37e1753aa9ce.png)<!--[endif]-->

当调用fopen打开/proc/stat时，返回伪造的信息

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p2.ssl.qhimg.com/t01f5a76bc2b2116d2b.png)](https://p2.ssl.qhimg.com/t01f5a76bc2b2116d2b.png)<!--[endif]-->

当调用fopen打开/proc/net/tcp或/proc/net/tcp6时，同样进行过滤

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p5.ssl.qhimg.com/t01b76e1c5227350dfb.png)](https://p5.ssl.qhimg.com/t01b76e1c5227350dfb.png)<!--[endif]-->

## 四、流程还原

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p0.ssl.qhimg.com/t01ae9000770b607e1b.png)](https://p0.ssl.qhimg.com/t01ae9000770b607e1b.png)<!--[endif]-->

**基于上面的脚本和ELF样本分析可以发现整体入侵和感染流程大概为：**

1. 通过Redis未授权访问漏洞入侵机器并修改crontab任务；或者通过遍历known_hosts中的连接历史进行横向扩展；

2. crontab任务执行bash脚本，进行相关清理和下载执行恶意程序watchdogs并横向扩展：

<!-- [if !supportLists]-->a)      <!--[endif]-->覆写crontab任务；

<!-- [if !supportLists]-->b)      <!--[endif]-->清理其他恶意程序；

<!-- [if !supportLists]-->c)      <!--[endif]-->解锁删除相关系统文件；

<!-- [if !supportLists]-->d)      <!--[endif]-->下载执行watchdogs；

<!-- [if !supportLists]-->e)      <!--[endif]-->横向扫描其他机器；

<!-- [if !supportLists]-->f)       <!--[endif]-->清理相关文件和痕迹。

3. watchdogs执行实现写开机启动、服务项并释放动态链接库实现隐藏，同时释放执行挖矿程序：

<!-- [if !supportLists]-->a)      <!--[endif]-->获取进程ID写/tmp/.lsdpid；

<!-- [if !supportLists]-->b)      <!--[endif]-->将/tmp目录下的watchdogs复制到/usr/sbin/目录并加入开机启动项和服务项；

<!-- [if !supportLists]-->c)      <!--[endif]-->释放libioset.so并写入/etc/ld.so.preload实现进程等隐藏；

<!-- [if !supportLists]-->d)      <!--[endif]-->访问ident.me获取机器外网IP；

<!-- [if !supportLists]-->e)      <!--[endif]-->再次覆写crontab任务；

<!-- [if !supportLists]-->f)       <!--[endif]-->释放挖矿程序ksoftirqds和配置文件config.json并执行；

<!-- [if !supportLists]-->g)      <!--[endif]-->删除相关生成的文件并检查更新。

最终完成了一个漏洞利用到植入挖矿程序，同时隐藏和横向感染的过程。

而相对与过去我们分析过的隐藏进程的挖矿病毒，在该病毒释放的动态链接库中同步对unlink函数进行了过滤，过滤名称同时包含ld.so.preload和libioset.so，而同时由于删除、查看等系统命令函数也受过滤影响，就导致通过常规自带的方法无法直接删除libioset.so或者修改ld.so.preload解除恶意进程的隐藏，只能通过busybox 来实现对这些文件的删除清理。

在我们将/usr/local/lib/libioset.so文件清理后，就可以通过top命令看到执行的挖矿进程。

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p3.ssl.qhimg.com/t014e3f088c23237458.png)](https://p3.ssl.qhimg.com/t014e3f088c23237458.png)<!--[endif]-->

通过捕获的钱包地址查看黑客收益：

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p0.ssl.qhimg.com/t019da02f00867eb826.png)](https://p0.ssl.qhimg.com/t019da02f00867eb826.png)<!--[endif]-->

<!-- [if gte vml 1]&gt;-->

<!-- [if !vml]-->[![](https://p0.ssl.qhimg.com/t0195da12c410412517.png)](https://p0.ssl.qhimg.com/t0195da12c410412517.png)<!--[endif]-->

（数据来源：f2pool） 

该钱包总收益约为56.5门罗币，约合1.9万人民币，过去24小时内收益1.3门罗币，当前算力约为430KH/S。

 

## 五、修复建议和清理方法

### 修复建议

**Redis未授权访问：**

1、为 Redis 添加密码验证（重启Redis才能生效）；

2、禁止外网访问 Redis（重启Redis才能生效）；

3、以低权限运行Redis服务（重启Redis才能生效） 详细操作请参考：[http://bbs.qcloud.com/thread-30706-1-1.html](http://bbs.qcloud.com/thread-30706-1-1.html)。

**内网感染：**

1、建议不要将连接机器的私钥直接放在服务器上，如有必要建议添加密码；

2、建议通过有限的机器作为跳板机实现对其他内网机器的访问，避免所有机器的随意互联互通，跳板机不要部署相关可能存在风险的服务和业务。

### **挖矿木马清理方法**

1、删除恶意动态链接库/usr/local/lib/libioset.so；

2、排查清理/etc/ld.so.preload中是否加载1中的恶意动态链接库；

3、清理crontab异常项，删除恶意任务(无法修改则先执行5-a)；

4、kill 挖矿进程；

5、排查清理可能残留的恶意文件：

<!-- [if !supportLists]-->a)      <!--[endif]-->chattr -i /usr/sbin/watchdogs /etc/init.d/watchdogs /var/spool/cron/root /etc/cron.d/root；

<!-- [if !supportLists]-->b)      <!--[endif]-->chkconfig watchdogs off；

<!-- [if !supportLists]-->c)      <!--[endif]-->rm -f /usr/sbin/watchdogs /etc/init.d/watchdogs。

6、相关系统命令可能被病毒删除，可通过包管理器重新安装或者其他机器拷贝恢复；

7、由于文件只读且相关命令被hook，需要安装busybox通过busybox rm命令删除；

8、部分操作需要重启机器生效。

 

## 六、附录

### IOCs：

**样本**

1. aee3a19beb22527a1e0feac76344894c

2. c79db2e3598b49157a8f91b789420fb6

3. d6a146161ec201f9b3f20fbfd528f901

4. 39fa886dd1af5e5360f36afa42ff7b4e

**矿池地址**

xmr.f2pool.com:13531

**钱包地址**

46FtfupUcayUCqG7Xs7YHREgp4GW3CGvLN4aHiggaYd75WvHM74Tpg1FVEM8fFHFYDSabM3rPpNApEBY4Q4wcEMd3BM4Ava.teny

**URLs**

1. hxxps://pastebin.com/raw/sByq0rym

2. hxxps://pastebin.com/raw/tqJjUD9d

3. hxxp://thyrsi.com/t6/672/1550667515×1822611209.jpg

4. hxxp://ident.me

### 相关链接：

https://mp.weixin.qq.com/s/1AF5cgo_hJ096LmX7ZHitA

**本文作者：安全攻防组@腾讯安全云鼎实验室**

腾讯安全云鼎实验室专注云安全技术研究和云安全产品创新工作；负责腾讯云安全架构设计、腾讯云安全防护和运营工作；通过攻防对抗、合规审计搭建管控体系，提升腾讯云整体安全能力。 
