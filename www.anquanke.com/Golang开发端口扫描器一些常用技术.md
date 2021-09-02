> 原文链接: https://www.anquanke.com//post/id/252320 


# Golang开发端口扫描器一些常用技术


                                阅读量   
                                **19744**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01d43e9695a2132afa.jpg)](https://p2.ssl.qhimg.com/t01d43e9695a2132afa.jpg)



## 前言

Golang 是当前热门的语言之一，其拥有原生支持并发、对线程操作便捷、自身协程的轻量化等优点，使用其开发端口扫描器不仅开发过程高效，而且程序性能优秀。本文主要分享使用golang进行端口扫描器开发时可能涉及到的技术。



## Golang 简介

Go语言（或Golang）起源于2007年，并在2009年正式对外发布。Go是非常年轻的一门语言，它的主要目标是“兼具Python等动态语言的开发速度和C/C++等编译型语言的性能与安全性”。

Go语言是编程语言设计的又一次尝试，是对类C语言的重大改进，它不但能让你访问底层操作系统，还提供了强大的网络编程和并发编程支持。

Go语言的推出，旨在不损失应用程序性能的情况下降低代码的复杂性，具有“部署简单、并发性好、语言设计良好、执行性能好”等优势，目前国内诸多 IT 公司均已采用Go语言开发项目，其中包括Docker、Go-Ethereum、Thrraform 和 Kubernetes。

作为程序员，要开发出能充分利用硬件资源的应用程序是一件很难的事情。现代计算机都拥有多个核心，但是大部分编程语言都没有有效的工具让程序可以轻易利用这些资源。编程时需要写大量的线程同步代码来利用多个核，很容易导致错误。

Go语言正是在多核和网络化的时代背景下诞生的原生支持并发的编程语言。Go语言从底层原生支持并发，无需第三方库，开发人员可以很轻松地在编写程序时决定怎么使用CPU资源。

Go语言的并发是基于goroutine 的，goroutine类似于线程，但并非线程。可以将goroutine理解为一种虚拟线程。Go语言运行时会参与调度goroutine，并将goroutine合理地分配到每个CPU中，最大限度地使用 CPU性能。

多个goroutine 中，Go语言使用通道（channel）进行通信，通道是一种内置的数据结构，可以让用户在不同的 goroutine 之间同步发送具有类型的消息。这让编程模型更倾向于在goroutine之间发送消息，而不是让多个goroutine争夺同一个数据的使用权。



## 并发技术

无论是扫描器还是各种高并发web服务，都少不了使用到并发技术，而Golang原生支持了这一特性，这也是Golang被广泛使用在各种高并发场景的原因。

Go语言的并发机制运用起来非常简便，在启动并发的方式上直接添加了语言级的关键字就可以实现，和其他编程语言相比更加轻量。

下面来介绍几个概念：

## 

## 进程/线程

**进程**是程序在操作系统中的一次执行过程，系统进行资源分配和调度的一个独立单位。

**线程**是进程的一个执行实体，是CPU调度和分派的基本单位，它是比进程更小的能独立运行的基本单位。

一个进程可以创建和撤销多个线程，同一个进程中的多个线程之间可以并发执行。

### **并发/并行**

**并发：**把任务在不同的时间点交给处理器进行处理。在同一时间点，任务并不会同时运行。

**并行：**把每一个任务分配给每一个处理器独立完成。在同一时间点，任务一定是同时运行。

并发与并行并不相同，并发主要由切换时间片来实现“同时”运行，并行则是直接利用多核实现多线程的运行，Go程序可以设置使用核心数，以发挥多核计算机的能力。

### **协程/线程**

**协程：**独立的栈空间，共享堆空间，调度由用户自己控制，本质上有点类似于用户级线程，这些用户级线程的调度也是自己实现的。

**线程：**一个线程上可以跑多个协程，协程是轻量级的线程。

关于协程和线程的具体区别，可以参考线程和协程的区别的通俗说明一文。

### **Goroutine**

Goroutine 是 Go语言中的轻量级线程实现，由Go运行时（runtime）管理。Go程序会智能地将goroutine 中的任务合理地分配给每个CPU。

Go程序从main包的main() 函数开始，在程序启动时，Go程序就会为main() 函数创建一个默认的 goroutine。

Goroutine 的用法如下：

```
//go 关键字放在方法调用前新建一个 goroutine 并执行方法体
go GetThingDone(param1, param2);
//新建一个匿名方法并执行
go func(param1, param2) `{`
`}`(val1, val2)
//直接新建一个 goroutine 并在 goroutine 中执行代码块
go `{`
//do someting...
`}`
```

注：

a. 使用go关键字创建goroutine 时，被调用函数的返回值会被忽略

b. 如果需要在goroutine中返回数据，可以使用channel把数据从goroutine中作为返回值传出

所有goroutine 在 main()函数结束时会一同结束。

**runtime.GOMAXPROCS**

在Go语言程序运行时（runtime）实现了一个小型的任务调度器。这套调度器的工作原理类似于操作系统调度线程，Go程序调度器可以高效地将CPU资源分配给每一个任务。传统逻辑中，开发者需要维护线程池中线程与CPU核心数量的对应关系。同样的，Go地中也可以通过 runtime.GOMAXPROCS()函数做到，格式为：

一般情况下，可以使用runtime.NumCPU()查询CPU数量，并使用runtime.GOMAXPROCS()函数进行设置，例如：

Go 1.5 版本之前，默认使用的是单核心执行。从Go 1.5版本开始，默认执行上面语句以便让代码并发执行。



## Channel

一个channel是一个通信机制，它可以让一个goroutine通过它给另一个goroutine发送值信息。每个channel都有一个特殊的类型，也就是channels可发送数据的类型。

Go语言提倡使用通信的方法代替共享内存，当一个资源需要在goroutine之间共享时，通道在goroutine之间架起了一个管道，并提供了确保同步交换数据的机制。声明通道时，需要指定将要被共享的数据的类型。可以通过通道共享内置类型、命名类型、结构类型和引用类型的值或者指针。

在任何时候，同时只能有一个goroutine访问通道进行发送和获取数据。goroutine间通过通道就可以通信，通道像一个传送带或者队列，总是遵循先入先出（First In First Out）的规则，保证收发数据的顺序。

• 声明通道类型

```
var 通道变量 chan 通道类型
//通道类型：通道内的数据类型。
//通道变量：保存通道的变量。
```

• 创建通道

```
通道实例 := make(chan 数据类型)
//数据类型：通道内传输的元素类型。
//通道实例：通过make创建的通道句柄。
eg:
ch1 := make(chan int) // 创建一个整型类型的通道
ch2 := make(chan interface`{``}`) // 创建一个空接口类型的通道, 可以存放任意
```

• 使用通道发送数据

```
通道变量 &lt;- 值
//通道变量：通过make创建好的通道实例。
//值：可以是变量、常量、表达式或者函数返回值等。值的类型必须与ch通道的元素类型一致。
eg:
// 创建一个空接口通道
ch := make(chan interface`{``}`)
// 将0放入通道中
ch &lt;- 0
// 将hello字符串放入通道中
ch &lt;- "hello"
```

把数据往通道中发送时，如果接收方一直都没有接收，那么发送操作将持续阻塞直至数据被接收。

• 使用通道接收数据

a. 阻塞接收数据

阻塞模式接收数据时，将接收变量作为&lt;-操作符的左值，格式如下：

```
data := &lt;-ch
```

执行该语句时将会阻塞，直到接收到数据并赋值给 data 变量。

b. 非阻塞接收数据

使用非阻塞方式从通道接收数据时，语句不会发生阻塞，格式如下：

```
data, ok := &lt;-ch
//data：表示接收到的数据。未接收到数据时，data 为通道类型的零值。
//ok：表示是否接收到数据。
```

非阻塞的通道接收方法可能造成高的CPU占用，因此使用非常少。如果需要实现接收超时检测，可以配合 select 和计时器channel进行。

c. 接收任意数据，忽略接收的数据

阻塞接收数据后，忽略从通道返回的数据，格式如下：

```
&lt;-ch
```

执行该语句时将会发生阻塞，直到接收到数据，但接收到的数据会被忽略。这个方式实际上只是通过通道在goroutine间阻塞收发实现并发同步。

**sync.WaitGroup**

经常会看到以下代码：

```
func main()`{`
for i := 0; i &lt; 100 ; i++`{`
go fmt.Println(i)
`}`
time.Sleep(time.Second)
`}`
```

为了等待所有goroutine运行完毕，不得不在程序的末尾使用time.Sleep()来睡眠一段时间，等待其他线程充分运行，对于简单的代码这样做既方便也简单，但是遇到复杂的代码，无法估计运行时间时，就不能使用time.Sleep来等待所有goroutine运行完成了。

可以考虑使用管道来完成上述操作：

```
func main() `{`
c := make(chan bool, 100)
for i := 0; i &lt; 100; i++ `{`
go func(i int) `{`
fmt.Println(i)
c &lt;- true
`}`(i)
`}`
for i := 0; i &lt; 100; i++ `{`
&lt;-c
`}`
`}`
```

但是管道被设计出来不仅仅只是在这里用作简单的同步处理，假设我们有十万甚至更多的for循环，需要申请同样数量大小的管道出来，对内存是不小的开销。

sync.WaitGroup可以方便的解决这种情况：

```
func main() `{`
wg := sync.WaitGroup`{``}`
wg.Add(100)
for i := 0; i &lt; 100; i++ `{`
go func(i int) `{`
fmt.Println(i)
wg.Done()
`}`(i)
`}`
wg.Wait()
`}`
```

官方文档对WaitGroup的描述是：一个WaitGroup对象可以等待一组协程结束。

使用方法是：

1. main协程通过调用wg.Add(delta int) 设置worker协程的个数，然后创建worker协程；

2. worker协程执行结束以后，都要调用wg.Done()；

3. main协程调用 wg.Wait() 且被阻塞，直到所有worker协程全部执行结束后返回。

以端口扫描器中的代码片段为例：

```
//限制goroutine数量
ch = make(chan bool, goroutineNum)
func run()`{`
//...
for _, host := range ipList `{`
for _, port := range portList `{`
ch &lt;- true
wg.Add(1)
go scan(host, port)
`}`
`}`
wg.Wait()
`}`
func scan(host string, port int) `{`
//...
&lt;-ch
wg.Done()
`}`
```



## 通信技术

Golang提供了官方库net为网络I/O提供了一个便携式接口，包括TCP/IP，UDP，域名解析和Unix域套接字。

端口扫描与主机存活探测主要用到tcp、udp、arp与icmp协议。



## 常用函数

**func Dial**

```
func Dial(network, address string) (Conn, error)
//Dial 连接到指定网络上的地址。
eg:
Dial("tcp", "golang.org:http")
Dial("tcp", "192.0.2.1:http")
Dial("tcp", "198.51.100.1:80")
Dial("ip4:1", "192.0.2.1")
Dial("ip6:ipv6-icmp", "2001:db8::1")
Dial("ip6:58", "fe80::1%lo0")
```

已知网络是“tcp”，“tcp4”（仅IPv4），“tcp6”（仅IPv6），“udp”，“udp4”（仅IPv4），“udp6”（仅IPv6），“ip” ，“ip4”（仅限IPv4），“ip6”（仅限IPv6），“unix”，“unixgram”和“unixpacket”。

• 对于TCP和UDP网络，地址格式为“主机：端口”。主机必须是文字IP地址或可以解析为IP地址的主机名。该端口必须是文字端口号或服务名称。如果主机是文字IPv6地址，则必须将其放在方括号中，如“2001：db8 :: 1：80”或“fe80 :: 1％zone：80”中所示。

• 对于IP网络，网络必须是“ip”，“ip4”或“ip6”，后跟冒号和文字协议号或协议名称，地址格式为“主机”。主机必须是文字IP地址或带区域的文字IPv6地址。它取决于每个操作系统操作系统的行为如何使用不知名的协议编号，例如“0”或“255”。

对于Unix网络，地址必须是文件系统路径。

**func DialTimeout**

```
func DialTimeout(network, address string, timeout time.Duration) (Conn, error)
//DialTimeout与Dial相同，但需要超时。
```

在扫描器中，仅是为了探测端口或主机是否开放，所以需要设置连接超时，否则可能出现阻塞影响正常扫描的情况。

示例代码为：

```
//tcp探测端口是否开放
conn, err := net.DialTimeout("tcp", fmt.Sprintf("%s:%d", host, port), time.Duration(timeout)*time.Millisecond)
//icmp探测主机是否存活
conn, err := net.Dial("ip:icmp", host)
```

**func ParseCIDR**

```
func ParseCIDR(s string) (IP, *IPNet, error)
//ParseCIDR将s解析为CIDR表示法IP地址和前缀长度，如RFC 4632和RFC 4291中定义的“192.0.2.0/24”或“2001：db8 :: / 32”。
```

它返回由IP和前缀长度暗示的IP地址和网络。例如，ParseCIDR（“192.0.2.1/24”）返回IP地址192.0.2.1和网络192.0.2.0/24。

**func ParseIP**

```
func ParseIP(s string) IP
//ParseIP将s解析为IP地址，并返回结果。
```

字符串s可以采用点分十进制（“192.0.2.1”）或IPv6（“2001：db8 :: 68”）形式。如果s不是IP地址的有效文本表示，则ParseIP返回nil。

**func (*IPConn) SetReadDeadline**

```
func (c *IPConn) SetReadDeadline(t time.Time) error
//SetReadDeadline设置从流中读取信息的超时时间。
```

在扫描器中需要获取开放端口的banner时，常常需要从流中读取返回信息，若不设置超时，将会出现不可预估的阻塞情况。



## 一些示例

• 解析IP

对扫描器而言，用户传入的参数可以为192.168.1.1-255、192.168.1.1/24等，所以需要对ip进行解析：

```
if net.ParseIP(item) != nil `{`
ipList = append(ipList, item)
`}` else if ip, network, err := net.ParseCIDR(item); err == nil `{`
n, _ := network.Mask.Size()
ipSub := strings.Split(ip.Mask(network.Mask).String(), ".")
//...
`}` else if strings.Contains(item, "-") `{`
//...
`}` else `{`
return ipList, fmt.Errorf("%s is not an IP Address or CIDR Network", item)
`}`
```

利用net.ParseIP与net.ParseCIDR判断传入的是否为CIDR模式的地址，利用network.Mask.Size()可以获取192.168.1.1/24中的掩码大小值24。

**• tcp连接并读取banner**

```
var msg [128]byte
var str string
conn, err := net.DialTimeout("tcp", fmt.Sprintf("%s:%d", host, port), time.Duration(timeout)*time.Millisecond)
if err != nil `{`
return false, str
`}`
conn.SetReadDeadline((time.Now().Add(time.Millisecond * time.Duration(timeout))))
_, err = conn.Read(msg[0:])
```

使用SetReadDeadline设置读取超时，将128字节的返回信息读入msg [128]byte中

**• ping功能实现**

使用icmp协议连接实现ping功能的核心代码：

```
func ping(host string) `{`
conn, err := net.Dial("ip:icmp", host)
if err != nil `{`
fmt.Println(err.Error())
os.Exit(1)
`}`
defer conn.Close()
var msg [512]byte
msg[0] = 8
msg[1] = 0
msg[2] = 0
msg[3] = 0
msg[4] = 0
msg[5] = 13
msg[6] = 0
msg[7] = 37
msg[8] = 99
len := 9
check := checkSum(msg[0:len])
msg[2] = byte(check &gt;&gt; 8)
msg[3] = byte(check &amp; 0xff)
//fmt.Println(msg[0:len])
for i := 0; i &lt; 2; i++ `{`
_, err = conn.Write(msg[0:len])
if err != nil `{`
continue
`}`
conn.SetReadDeadline((time.Now().Add(time.Millisecond * 400)))
_, err := conn.Read(msg[0:])
if err != nil `{`
continue
`}`
//fmt.Println(msg[0 : 20+len])
//fmt.Println("Got response")
if msg[20+5] == 13 &amp;&amp; msg[20+7] == 37 &amp;&amp; msg[20+8] == 99 `{`
//host is up
fmt.Printf("%s open\n", ljust(host, 21))
openHostList = append(openHostList, host)
return
`}`
`}`
`}`
func checkSum(msg []byte) uint16 `{`
sum := 0
len := len(msg)
for i := 0; i &lt; len-1; i += 2 `{`
sum += int(msg[i])*256 + int(msg[i+1])
`}`
if len%2 == 1 `{`
sum += int(msg[len-1]) * 256
`}`
sum = (sum &gt;&gt; 16) + (sum &amp; 0xffff)
sum += (sum &gt;&gt; 16)
var answer uint16 = uint16(^sum)
return answer
`}`
```

**• 广播ARP识别主机厂家信息**

思路：

￮ 向内网广播ARP Request

￮ 监听并抓取ARP Response包，记录IP和Mac地址

￮ 发活跃IP发送MDNS和NBNS包，并监听和解析Hostname

￮ 根据Mac地址计算出厂家信息

ARP（Address Resolution Protocol），地址解析协议，是根据IP地址获取物理地址的一个TCP/IP协议。主机发送信息时将包含目标IP地址的ARP请求广播到网络上的所有主机，并接收返回消息，以此确定目标的物理地址。

当我们要向以太网中另一台主机发送IP数据时，本地会根据目的主机的IP地址在**ARP高速缓存**中查询相应的以太网地址，ARP高速缓存是主机维护的一个IP地址到相应以太网地址的**映射表**。如果查询失败，ARP会广播一个询问（op字段为1）目的主机硬件地址的报文，等待目标主机的响应。

因为ARP高速缓存有时效性，读取到目标主机的硬件地址后，最好发送一个ICMP包验证目标是否在线。当然也可以选择不从高速缓存里读取数据，而是直接并发发送arp包，等待在线主机回应ARP报文。

**发送arp请求后，只需要开启一个arp的监听goruntime，所有有返回arp response包的，就是内网在线的host，接受到一个arp的response后，就可以发起mdns和nbns包并等待hostname的返回。**

**mDNS：**往对方的**5353**端口和**01:00:5E:00:00:FB**的mac地址发送UDP的mdns（Multicast DNS）包，如果目标系统支持，回返回host name。详细协议介绍和报文格式可以查看维基百科的介绍。

**NBNS：**也是一个种常见的查看目标机器hostname的一种协议，和mDNS一样，传输层也是UDP，端口是在137。

我们可以通过目标主机的硬件地址，获取到设备的生产厂家信息，这样的话，即使遇到防御比较好的系统，我们无法获取到hostname，也能从厂家信息里获取一定的信息量。

厂家对应manuf指纹：

https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob_plain;f=manuf



## Reference

http://c.biancheng.net/golang/intro/

https://zhuanlan.zhihu.com/p/169426477

https://cloud.tencent.com/developer/section/1143223

https://github.com/timest/goscan/issues/1
