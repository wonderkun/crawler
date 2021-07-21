> 原文链接: https://www.anquanke.com//post/id/244084 


# 聊聊 Synology NAS Audio Station 套件未授权 RCE 调试及 EXP 构造


                                阅读量   
                                **237782**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0129ad2f7f4081f1ad.jpg)](https://p2.ssl.qhimg.com/t0129ad2f7f4081f1ad.jpg)



作者：fenix@知道创宇404实验室**<br>**

## 前言

> 群晖科技（Synology）自始便专注于打造高效能、可靠、功能丰富且绿色环保 NAS 服务器，是全球少数几家以单纯的提供网络存储解决方案获得世界认同的华人企业[【1】](https://www.synology.com/)。

2021 年 5 月 27 日，HITB 2021（阿姆斯特丹）会议上分享了 Synology NAS 的多个漏洞[【2】](https://conference.hitb.org/hitbsecconf2021ams/materials/D1T2%20-%20A%20Journey%20into%20Synology%20NAS%20-%20QC.pdf)，Synology Calendar、Media Server、Audio Station 等套件中的漏洞可通过 Web 服务入口远程利用。Audio Station 套件的漏洞成因为 `audiotransfer.cgi` 存在缓冲区溢出，远程攻击者可构造特殊数据包，然后利用该漏洞以 root 权限在目标设备执行任意命令。

Synology 在产品安全性上还是很负责的，对于安全漏洞提供最高达 `10000$` 的赏金，近几年公开的漏洞中严重并且有详情的也不多，比如之前的《CVE-2017-11151 – Synology Photo Station Unauthenticated Remote Code Execution》 [【3】](https://www.seebug.org/vuldb/ssvid-96331)。

Audio Station 这个漏洞品相着实有点好，经验证发现无需认证即可利用，虽然开了 ASLR 也不需要爆破，一个请求即可实现稳定 RCE。

写篇文章记录一下， 等年纪大了，还能回头看看 🙂



## 环境搭建

Synology DS3615xs / DSM 5.2-5592 / Audio Station 5.4-2860

安装好黑群晖后，在应用商店安装 Audio Station 套件即可，DSM 5.2 的最新版 Audio Station 也存在漏洞。

[![](https://p1.ssl.qhimg.com/t01496bcafbc1f5db07.png)](https://p1.ssl.qhimg.com/t01496bcafbc1f5db07.png)



## 漏洞分析

漏洞触发流程如下（图片来自会议 PPT）：

[![](https://p3.ssl.qhimg.com/t01c8ea6ba5e872efe2.png)](https://p3.ssl.qhimg.com/t01c8ea6ba5e872efe2.png)

PoC 很容易构造，栈上没有指针需要恢复，一路畅通无阻，直接可控 PC。

[![](https://p5.ssl.qhimg.com/t01001d763d0bf23f6d.png)](https://p5.ssl.qhimg.com/t01001d763d0bf23f6d.png)



## 调试及 EXP 构造

X86 架构，只开了 NX 保护，ASLR 为半随机，Payload 中不能包含 `'\x00'`、`'/'`。

[![](https://p5.ssl.qhimg.com/t01c82a8e0e34923864.png)](https://p5.ssl.qhimg.com/t01c82a8e0e34923864.png)

本程序有 `popen()` 的符号 ，不需要 `return-to-libc`。

[![](https://p4.ssl.qhimg.com/t010e973e3d19e10f96.png)](https://p4.ssl.qhimg.com/t010e973e3d19e10f96.png)

接下来进入调试环节，我们知道 Web 服务器收到客户端的请求后通过环境变量和标准输入（Stdin）将数据传递给 CGI 程序, CGI 程序执行后通过标准输出（stdout）返回结果。因此调试的时候就有两种方法，1：gdb attach 到 Web 服务程序，然后 `set follow-fork-mode child`；2：设置好环境变量，直接运行 CGI。为了避免 Web 服务程序带来的干扰，如对特殊字符编码解码处理，我们先通过手动设置环境变量的方式来调试：

[![](https://p4.ssl.qhimg.com/t01ac74c62cdcc43fde.png)](https://p4.ssl.qhimg.com/t01ac74c62cdcc43fde.png)

可以看到，已经劫持执行流到 popen 了，现在思考一下参数传递的问题。<br>
popen 的函数原型如下：

```
FILE *popen(const char *command, const char *type);

The popen() function opens a process by creating a pipe, forking,
and invoking the shell.  Since a pipe is by definition
unidirectional, the type argument may specify only reading or
writing, not both; the resulting stream is correspondingly read-
only or write-only.

The command argument is a pointer to a null-terminated string
containing a shell command line.  This command is passed to
/bin/sh using the -c flag; interpretation, if any, is performed
by the shell.

The type argument is a pointer to a null-terminated string which
must contain either the letter 'r' for reading or the letter 'w'
for writing.
```

第二个参数很好处理：

```
In [7]: open('./audiotransfer.cgi', 'rb').read().index(b'r\x00')
Out[7]: 2249
```

第一个参数是命令字符串的地址，可以将其放到栈上，前面加一些 `';'` 作为命令滑板，然后 Payload 给一个大概的栈地址即可。此外，CGI 程序崩溃对 Web 服务没啥影响，可以爆破。

到这里就结束了吗？还有一个惊喜。

请求的 `User-Agent` 存到了堆上，由于 ASLR 为 1，通过 `brk()`分配的内存空间不会随机化，因此这是一个固定地址。

[![](https://p2.ssl.qhimg.com/t01437a21ccd461cc05.png)](https://p2.ssl.qhimg.com/t01437a21ccd461cc05.png)

将命令字符串放到 `User-Agent`，调整 Payload，成功获取到 root shell。

[![](https://p1.ssl.qhimg.com/t018e2896751276d58c.png)](https://p1.ssl.qhimg.com/t018e2896751276d58c.png)

然后就是 gdb attach 到 Web 服务程序进行实际漏洞利用调试了，可使用以下代码替换 `audiotransfer.cgi` ，方便确认 Payload 是否被修改，以及通过 `/proc/$pid/stat` 得到父进程的 pid。

```
#include&lt;stdio.h&gt;
#include&lt;stdlib.h&gt;

int main() `{`
    printf("%s", getenv("REQUEST_URI"));
    printf("%s", getenv("HTTP_USER_AGENT"));
    sleep(1000000);
`}`
```

[![](https://p0.ssl.qhimg.com/t012067855d9f8ede09.png)](https://p0.ssl.qhimg.com/t012067855d9f8ede09.png)



## 影响范围

通过 ZoomEye 网络空间搜索引擎对关键字 app:”Synology NAS storage-misc httpd” 进行搜索，共发现 10154041 条 Synology NAS 的 IP 历史记录，主要分布在中国、德国[【4】](https://www.zoomeye.org/searchResult?q=app%3A%22Synology%20NAS%20storage-misc%20httpd%22)。安装了Audio Station 套件且版本 `&lt; 6.5.4-3367` 的会受到该漏洞影响。

[![](https://p3.ssl.qhimg.com/t019b692737246a5d0a.png)](https://p3.ssl.qhimg.com/t019b692737246a5d0a.png)

从 ZoomEye 随机抽取 10000 的目标进行漏洞检测，成功率为 `127/10000`。

[![](https://p3.ssl.qhimg.com/t015d0106146d558380.png)](https://p3.ssl.qhimg.com/t015d0106146d558380.png)



## 致谢

Synology 官方没有发布该漏洞的安全公告，之前的文章引用了错误的链接及影响版本，实际影响版本为 `&lt; 6.5.4-3367`（修复版本），感谢 swing 师傅指正 🙂



## 相关链接

【1】: Synology 官网

[https://www.synology.com/](https://www.synology.com/)

【2】: A Journey into Synology NAS

[https://conference.hitb.org/hitbsecconf2021ams/materials/D1T2%20-%20A%20Journey%20into%20Synology%20NAS%20-%20QC.pdf](https://conference.hitb.org/hitbsecconf2021ams/materials/D1T2%20-%20A%20Journey%20into%20Synology%20NAS%20-%20QC.pdf)[/https://conference.hitb.org/hitbsecconf2021ams/materials/D1T2%20-%20A%20Journey%20into%20Synology%20NAS%20-%20QC.pdf](//conference.hitb.org/hitbsecconf2021ams/materials/D1T2%20-%20A%20Journey%20into%20Synology%20NAS%20-%20QC.pdf)

【3】: Synology Photo Station Unauthenticated Remote Code Execution

[https://www.seebug.org/vuldb/ssvid-96331](https://www.seebug.org/vuldb/ssvid-96331)[/https://www.seebug.org/vuldb/ssvid-96331](//www.seebug.org/vuldb/ssvid-96331)

【4】: ZoomEye 网络空间搜索引擎

[https://www.zoomeye.org/searchResult?q=app%3A%22Synology%20NAS%20storage-misc%20httpd%22](https://www.zoomeye.org/searchResult?q=app%3A%22Synology%20NAS%20storage-misc%20httpd%22)[/https://www.zoomeye.org/searchResult?q](//www.zoomeye.org/searchResult?q)
