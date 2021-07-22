> 原文链接: https://www.anquanke.com//post/id/171156 


# Snapd Ubuntu 提权分析


                                阅读量   
                                **230935**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t0164baea72433b9d65.png)](https://p4.ssl.qhimg.com/t0164baea72433b9d65.png)

作者：merjerson@360CERT

## 0x00 背景

做过脚本的同学都知道提权的苦楚。

平时在做定向渗透，溯源反制的时候，经常遇到进得去，系统却拿不下来的情况。

14号看到 Snap &lt; 2.37.1 提权漏洞，测了下，异常好用。在 ubuntu 18.04之后版本默认安装，只需要有文件写入权限和python环境，即可完美提权。几个vps一打一个准。

想了想，最末分析过的 linux 平台漏洞还是 “脏牛”。近半年多一直在搞其他方面，许久没做漏洞分析了，正好有个提权漏洞换换脑子。



## 0x01 linux提权姿势梳理

首先梳理一下 linux 提权的种类。我所知道的所有提权思路有这么几种：
- 内核漏洞利用
- 服务、程序漏洞利用
- 权限配置不当
### <a name="header-n24"></a>内核漏洞利用

内核漏洞利用是最常见的提权方式，渗透提权的时候首先想到的就是查看系统版本、内核版本。根据环境找提权 exp。

内核漏洞利用的常规利用方式，有这么几步：
- 通过漏洞将 payload 打入到内核模式下
- 操纵内存数据，比如将用户空间映射到内核空间
- 启动新权限的shell，获得root权限
这种提权方法，需要找到对应内核版本的漏洞利用工具，并且具有运行利用工具的能力。

即使能够运行工具，也不一定完全提权成功。许多公开的漏洞利用工具都不稳定。运行提权工具有可能造成目标主机宕机重启。

### <a name="header-n43"></a>服务、程序漏洞利用

权限具有继承性，高权限运行的服务、程序，他的执行能力也是高权限。一些web服务，数据库应用，系统服务组件往往都在高权限下运行。

例如，运维人员通常使用root权限运行mysql。这时可以尝试使用mysql提权漏洞，将低权限的mysql用户提权至mysql root 权限。

mysql 本身具有 shell 执行环境。系统root身份运行的mysql，其 mysql root 权限接近系统 root。

### <a name="header-n50"></a>权限配置不当

这种要具体情况具体分析，常见的比如：
- 弱口令
- suid配置错误
- sudo权限滥用
- 路径配置不当
- 配置不当的Cron jobs 等
这部分，可以参照这篇 [blog](https://sushant747.gitbooks.io/total-oscp-guide/privilege_escalation_-_linux.html)。

本次分析的snap提权漏洞，属于root权限运行的服务漏洞。

snapd 在使用api的时候，身份鉴权存在问题，允许地权限用户调用高权限api，从而造成提权。

一篇完整的漏洞分析必须要包括:
- 漏洞背景
- 漏洞成因分析
- 漏洞上下文分析
- 利用方式分析
- 补丁分析
- 漏洞验证
- 安全建议
下面是正文



## 0x02 漏洞背景

snap是一个Linux系统上的包管理软件。在Ubuntu18.04后默认预安装到了系统中。

snapd 是负责管理本地安装服务与在线应用商店通信的程序，随着snap一起安装，并且在root权限下运行，这是提权的基本条件。

[![](https://p1.ssl.qhimg.com/t0162588fce22a9c512.jpg)](https://p1.ssl.qhimg.com/t0162588fce22a9c512.jpg)

根据官方描述，服务进程snapd中提供的REST API服务对请求客户端身份鉴别存在问题，从而导致了提权。Chris Moberly 已经公开了[细节](https://shenaniganslabs.io/2019/02/13/Dirty-Sock.html)。



## 0x03 漏洞成因分析

[漏洞相关的更改](https://github.com/snapcore/snapd/commit/a819ae713446a1c7f75df15c3c5d0de4d4a49332#diff-99646ddbf38051ac9a98fe1a75423b86)：

漏洞位置在：

```
func ucrednetGet(remoteAddr string) (pid uint32, uid uint32, socket string, err error) `{`
    pid = ucrednetNoProcess
    uid = ucrednetNobody
    for _, token := range strings.Split(remoteAddr, ";") `{`
        var v uint64
        if strings.HasPrefix(token, "pid=") `{`
            if v, err = strconv.ParseUint(token[4:], 10, 32); err == nil `{`
                pid = uint32(v)
            `}` else `{`
                break
            `}`
        `}` else if strings.HasPrefix(token, "uid=") `{`
            if v, err = strconv.ParseUint(token[4:], 10, 32); err == nil `{`
                uid = uint32(v)
            `}` else `{`
                break
            `}`
        `}`
        if strings.HasPrefix(token, "socket=") `{`
            socket = token[7:]
        `}`

    `}`
    if pid == ucrednetNoProcess || uid == ucrednetNobody `{`
        err = errNoID
    `}`

    return pid, uid, socket, err
`}`
```

该函数，对 remoteAddr进行分割，标志符为 “;” ，将分割后得到的数组，for 循环。通过 HasPrefix 判别内容，对pid、uid、socket进行赋值。

这里存在一个问题： for循环中，有可能会对变量重复赋值。Split分割后的数组，如果存在多个 uid= 开头的值，则 uid 的值将被后者覆盖。

例如，”uid=1000;pid=1100;uid=0″，通过 ; 进行分割，得到[‘uid=1000′,’pid=1100′,’uid=0’]，该数组在迭代的时候：

```
`}` else if strings.HasPrefix(token, "uid=") `{`
    if v, err = strconv.ParseUint(token[4:], 10, 32); err == nil `{`
        uid = uint32(v)
    `}` else `{`
        break
    `}`
`}`
```

第一次执行到这里的时候，uid被赋值为1000，因为后面还有一个以uid为开头的值（uid=0），所以程序还会进入这个代码段，将uid 重置为0。这是，漏洞形成的基本逻辑。

如果是发漏洞预警，分析到这里已经可以了。但如果是做漏洞研究，还远远不够，还要进行漏洞上下文和利用技术分析。



## 0x04 漏洞上下文分析

除了找到漏洞成因，还要知道”漏洞从哪来，到哪去”。

### <a name="header-n130"></a>从哪来：

漏洞逻辑函数：

```
func ucrednetGet(remoteAddr string) (pid int32, uid uint32, socket string, err error) `{`
    pid = ucrednetNoProcess
    uid = ucrednetNobody
    for _, token := range strings.Split(remoteAddr, ";") `{`
        var v uint64
......
```

漏洞处理函数，ucrednetGet() ，传入变量为 remoteAddr，该变量即是Split处理对象。则查找该函数调用关系。

[![](https://p2.ssl.qhimg.com/t01627f6b639c83a9ee.jpg)](https://p2.ssl.qhimg.com/t01627f6b639c83a9ee.jpg)

可以看到有n多调用，在api.go 文件中，有丰富逻辑代码。随进入分析。

ucrednetGet() 被重命名为 postCreateUserUcrednetGet() 和 runSnapctlUcrednetGet(), 查看调用逻辑：

```
func getUsers(c *Command, r *http.Request, user *auth.UserState) Response `{`
    _, uid, _, err := postCreateUserUcrednetGet(r.RemoteAddr)
    if err != nil `{`
        return BadRequest("cannot get ucrednet uid: %v", err)
    `}`
    if uid != 0 `{`
        return BadRequest("cannot get users as non-root")
    `}`
......
```

postCreateUserUcrednetGet() 传入的参数为 r.RemoteAddr 。r 为 http.Request对象。由此可得，漏洞逻辑代码，处理的对象来自，http.Request.RemoteAddr ，即：

传入漏洞逻辑函数 ucrednetGet() 的参数 remoteAddr 为 http.Request.RemoteAddr。

查了下，http.Request.RemoteAddr 为 go 内建结构，之后查看 go [代码](https://github.com/golang/go)。

这里，分析了go中整个 SockaddrUnix 调用过程。这里只简单写下要点：
- coon.go:123 声明 RemoteAddr()，调用Conn.conn.RemoteAddr()
- coon.go:27 声明结构体 Conn，其中 conn 为 net.Conn
- net.go:221 声明net.conn.RemoteAddr(),返回c.fd.raddr,c 为 conn指针
- net.go:164 声明conn结构体，fd 为 netFD 指针
- fd_unix.go:19 声明 netFD 结构体。
- fd_unix.go:45 声明 setAddr 函数，对 netFD.raddr进行赋值， 此处即为漏洞传入参数 RemoteAddr，首次声明位置。 找到这里还不够，我们需要知道这个传入的值，究竟从哪来的。
- file_unix.go:66 调用 setAddr() :fd.setAddr(laddr, raddr),第二个参数，是我们需找的。
- file_unix.go:60 设置raddr：addr := fd.addrFunc()(rsa)
- sock_posi.go:92 声明 addrFunc(),可以看到根据套接字族设定进行不同的操作，返回sockaddrToXXX
```
func (fd *netFD) addrFunc() func(syscall.Sockaddr) Addr `{`
  switch fd.family `{`
  case syscall.AF_INET, syscall.AF_INET6:
      switch fd.sotype `{`
      case syscall.SOCK_STREAM:
          return sockaddrToTCP
      case syscall.SOCK_DGRAM:
          return sockaddrToUDP
      case syscall.SOCK_RAW:
          return sockaddrToIP
      `}`
  case syscall.AF_UNIX:
      switch fd.sotype `{`
      case syscall.SOCK_STREAM:
          return sockaddrToUnix
      case syscall.SOCK_DGRAM:
          return sockaddrToUnixgram
      case syscall.SOCK_SEQPACKET:
          return sockaddrToUnixpacket
      `}`
  `}`
  return func(syscall.Sockaddr) Addr `{` return nil `}`
  `}`
```
- 查阅[资料](http://man7.org/linux/man-pages/man7/unix.7.html)，原来 AF_UNIX 用于进程间通信，绑定的文件，可以通过 sockaddrToUnix 取得。下面是说明：
> <p>…….<br>
Address format<br>
A UNIX domain socket address is represented in the following<br>
structure:</p>
<p>struct sockaddr_un `{`<br>
sa_family_t sun_family;               /* AF_UNIX */<br>
char        sun_path[108];            /* pathname */<br>
`}`;</p>
<p>The sun_family field always contains AF_UNIX.  On Linux sun_path is<br>
108 bytes in size; see also NOTES, below.</p>
<p>Various systems calls (for example, bind(2), connect(2), and<br>
sendto(2)) take a sockaddr_un argument as input.  Some other system<br>
calls (for example, getsockname(2), getpeername(2), recvfrom(2), and<br>
accept(2)) return an argument of this type.</p>
<p>Three types of address are distinguished in the sockaddr_un struc‐<br>
ture:</p>
<p>*  pathname: a UNIX domain socket can be bound to a null-terminated<br>
filesystem pathname using bind(2).  When the address of a pathname<br>
socket is returned (by one of the system calls noted above), its<br>
length is</p>
offsetof(struct sockaddr_un, sun_path) + strlen(sun_path) + 1
<p>and sun_path contains the null-terminated pathname.  (On Linux,<br>
the above offsetof() expression equates to the same value as<br>
sizeof(sa_family_t), but some other implementations include other<br>
fields before sun_path, so the offsetof() expression more portably<br>
describes the size of the address structure.)</p>
<p>For further details of pathname sockets, see below.<br>
……</p>
- unixsock_posix.go:52 定义了 sockaddrToUnix(),可以看到，是通过 syscall.SockaddrUnix获得的绑定文件名。
分析到这里，RemoteAddr 怎么来的我们算整明白了：根据不同的套接字族，返回不同的地址。如果是通过 AF_UNIX 创建的套接字，将返回绑定的文件名。

### <a name="header-n188"></a>到哪去

那么，哪里调用了存在漏洞的函数？该漏洞有多大影响呢？

之前看到，漏洞函数在api.go 中进行调用：

[![](https://p5.ssl.qhimg.com/t01627f6b639c83a9ee.jpg)](https://p5.ssl.qhimg.com/t01627f6b639c83a9ee.jpg)

ucrednetGet 重命名为 postCreateUserUcrednetGet, 在postCreateUser有调用：

```
......
func postCreateUser(c *Command, r *http.Request, user *auth.UserState) Response `{`
    _, uid, _, err := postCreateUserUcrednetGet(r.RemoteAddr)
    if err != nil `{`
        return BadRequest("cannot get ucrednet uid: %v", err)
    `}`
    if uid != 0 `{`
        return BadRequest("cannot use create-user as non-root")
    `}`
......
```

而该函数，对应的是创建本地用户的API：

```
......
    createUserCmd = &amp;Command`{`
        Path: "/v2/create-user",
        POST: postCreateUser,
    `}`
......
```

了解下 snap API：

[API 文档](https://github.com/snapcore/snapd/wiki/REST-API)

[![](https://p4.ssl.qhimg.com/t01d75e94de87bf8a07.jpg)](https://p4.ssl.qhimg.com/t01d75e94de87bf8a07.jpg)

功能是创建本地用户，使用权限是root。结合漏洞会将uid 覆盖为 0（root）的可能，则该漏洞可以通过调用api，创建用户，如果 sudoer 设置为true，则创建的为特权用户。



## 0x05 漏洞利用分析

之上，将漏洞分析的明明白白。此时其实可以自己写出exp：
- 创建 AF_UNIX 族套接字
- 绑定一个文件，文件名为;uid=0,“;”用于截取字符串，获取覆盖uid的能力。
- 调用API，且sudoer 设为true
- snapd在鉴权的时候会获取远程地址，如果是 AF_UNIX 类型套接字。将返回绑定的文件，触发漏洞。
- 鉴权的到uid=0，认为是root权限调用，执行生成本地用户操作，且调用API，且sudoer=true，则生成的用户具有特权。
漏洞作者给的 [exp](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv1.py)，确实是这么写的。



## 0x06 补丁分析

[![](https://p5.ssl.qhimg.com/t010affe16f3fa8f235.png)](https://p5.ssl.qhimg.com/t010affe16f3fa8f235.png)

漏洞修补的很粗暴，之前：

```
return fmt.Sprintf("pid=%s;uid=%s;socket=%s;%s", wa.pid, wa.uid, wa.socket, wa.Addr)
```

现在定义了一个结构体 ucrednet ，并且现在

```
return fmt.Sprintf("pid=%d;uid=%d;socket=%s;", un.pid, un.uid, un.socket)
```

不再返回 wa.Addr ，即不再处理远程连接地址。通过 AF_UNIX 套接字向RemoteAddr 注入文本已经行不通。从而修补了漏洞。



## 0x07 漏洞验证

[![](https://p1.ssl.qhimg.com/t0194c3e28737c22459.jpg)](https://p1.ssl.qhimg.com/t0194c3e28737c22459.jpg)

漏洞十分的好用，snap &lt; 2.37.1 以下版本均受影响。

因为在ubuntu 18.04 以后版本，默认安装 snap ，并且测试时发现，一些vps 供应商 Ubuntu 16.04 同样默认安装snap。

以下vps服务商的 ubuntu 安装镜像均存在问题：
- 腾讯云
- 谷歌云
- 亚马逊云
- vultr
- 搬瓦工
- ……
除了阿里云外，一打一个准。阿里云ubuntu 镜像中，不带有snap，是我测的主机中，唯一不受漏洞影响的云服务商。



## 0x08 安全建议

修补很简单，将 snap 升级到最新版就好了。

有 ubuntu vps 的同学，建议查看一下自己主机上snap的版本。



## 0x09 后记

很多漏洞作者，都会公布漏洞详情。建议做漏洞分析的同学，不要先去看漏洞详情。成长的过程在于对漏洞的摸索。

拿着分析文章，看一步调一步。没有太大意义，沉淀不了自己的经验。

本次分析的snap漏洞，唯一卡住的地方，是套接字那里。去看漏洞作者详细分析，才知道原来还有 AF_UNIX 用于本地进程通信。这个是我知识盲区，卡在这确实没办法。

ps：其实整篇下来，最难得部分是逆 go 的net标准库。（笑
