> 原文链接: https://www.anquanke.com//post/id/83249 


# node.js远程内存泄露漏洞


                                阅读量   
                                **82402**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://nodesecurity.io/advisories/67](https://nodesecurity.io/advisories/67)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0177c34a02ccb7e186.png)](https://p2.ssl.qhimg.com/t0177c34a02ccb7e186.png)

**近日，在允许用户通过简单地发送ping数据帧，来分配内存的ws模块中发现存在着漏洞。该漏洞会拒绝用户发送数据的请求，使用户发送ping数据帧功能失效，在此之前，还会加大数据帧的负载。**

实际上，这就是漏洞的具体表现。但在模块中，ws通常将我们所要传入内存的所有数据进行相应的转换，这就是漏洞之所在。我们对所要发送数据的类型都没做任何检查。当你在nide.js中需要存储一个数字时，该漏洞就会自动给数字分配一个存储大量字节的字符串空间，从而加大内存的负载。

```
var x = new Buffer(100);
// vs
var x = new Buffer('100');
```



对于只有3个有效字节的数据，系统会分配100字节的存储空间。所以当服务器要接受一个1000字节的ping数据帧时，系统就会在原来未清零的100字节的空间基础上，将剩余的空间分配给1000字节的数据帧使用，这样就会造成数据混乱，从而形成内存存储漏洞。

```
var ws = require('ws')
var server = new ws.Server(`{` port: 9000 `}`)
var client = new ws('ws://localhost:9000')
client.on('open', function () `{`
  console.log('open')
  client.ping(50) // this makes the server return a non-zeroed buffer of 50 bytes
  client.on('pong', function (data) `{`
    console.log('got pong')
    console.log(data) // a non-zeroed out allocated buffer returned from the server
  `}`)
`}`)
```



有两个可以轻微地减轻这一漏洞影响的因素，它们分别是：

1.现代的任一操作系统内核在将内存页封装成为进程之前，都会对原来的内存页进行清零，从而为进入内存的新数据提供缓存空间。这就意味着，只有之前使用过的内存页和被node进程释放的数据页中的数据会被泄漏。

2.node.js通过在JavaScipt中产生一些大的内部缓冲区，并将这些大的缓冲区分为许多较小的可使用缓存块，来管理存储空间。由于会受到废弃数据的影响，这些缓存块并不存储在V8引擎上。这样做的好处就是，只有那些先前被分配作为缓冲区的内存页的数据才会被泄漏。

**引用：**

    https://github.com/websockets/ws/releases/tag/1.0.1<br>            https://github.com/nodejs/node-v0.x-archive/issues/4525
