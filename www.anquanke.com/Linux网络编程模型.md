> 原文链接: https://www.anquanke.com//post/id/207952 


# Linux网络编程模型


                                阅读量   
                                **166673**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01583a46eb13e19a22.png)](https://p1.ssl.qhimg.com/t01583a46eb13e19a22.png)



因为最近在找开源网络组件的漏洞，将自己遇到的linux网络编程问题做个总结，也巩固一下自己的网络基础知识，我做的就是总结和归纳，很多知识都是直接使用参考链接中的代码和描述，感觉描述不清楚的，建议直接看参考链接中大佬的文章，描述不正确的，直接可以联系我，我做改正。

写这个文章看了很多大佬的文章，大佬的文章，基本有3个特点

```
1. 全部理论介绍，理论特别详细，但是没有具体实现代码，有的可能也只是伪码
2. 是基本全是代码，理论基本没有，但是代码又不全，看不到效果
3. 形象比喻，各种绘声绘影的描述网络模型，但是代码一行没有
```

本文主旨是`show me the code`，废话不多，能用代码描述的尽力不多bb，每个模型，我都简要的做了描述，之后使用简单的代码来做指导，并且代码可以使用，[开源代码](https://github.com/xinali/LinuxNetworkModel)，你可以编译执行，观察效果，之后再结合一点理论，自然而然也就大概理解了。等你了解了，这些基础，再去使用什么`libev/libuv`的库，相对来说也就简单多了。<br>
这单纯的只是一个基础，没有涉及到网络组件漏洞挖掘，大佬勿喷

`Linux`的`5`种网络模型(`I/O`模型)

```
1) 阻塞I/O blocking I/O
2) 非阻塞I/O nonblocking I/O
3) 复用I/O I/O multiplexing (select/poll/epoll) (主用于TCP)
4) 信号驱动I/O signal driven I/O (主用于UDP)
5) 异步I/O asynchronous I/O
```

我尽我所能的把上面的每个模型，包括其中每个利用点，都说一下，除了目前业界实现不完全的异步I/O



## 阻塞模型

这是最基础，最简单的linux网络模型, 下面利用简单的一幅图描述网络阻塞模型的原理

```
server
                                           |
                                          bind
                                           |
                                         listen
                                           |
                                         accept
                                           |
                                      阻塞直到客户端连接
                                           |
        client                             |
           |                               |
        connect ----建立连接完成3次握手----&gt;  |
           |                               |
         write   --------数据(请求)------&gt; read
           |                               |
           |                             处理请求
           |                               |
         read   &lt;---------应答----------  write
           |                               |
         close                           close
```

阻塞模型最大的弊端就是`server`启动之后一直阻塞，直到`client`端发送请求为止，什么也不干<br>
这样极大的浪费了网络资源，所以这种的一般只适合本地的文件读取，写入操作，不适合做网络应用

实现的源码

`server.c`

```
do 
`{`
    struct sockaddr_in server_addr, client_addr;
    unsigned char client_host[256];
    memset((void*)client_host, 0, sizeof(client_host));
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) 
    `{`
        handle_error("socket");
        break;
    `}`
    memset((void*)&amp;server_addr, 0, sizeof(struct sockaddr_in));
    server_addr.sin_family = AF_INET; /* ipv4 tcp packet */
    server_addr.sin_port = htons(SERVER_PORT); /* convert to network byte order */
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(server_fd, (SA*)&amp;server_addr, sizeof(struct sockaddr_in)) == -1)
    `{`
        handle_error("bind");
        break;
    `}`

    if (listen(server_fd, 32) == -1)
    `{`
        handle_error("listen");
        break;
    `}`
    printf("waiting for connect to server...n");
    int client_fd;
    int client_addr_len = sizeof(struct sockaddr_in);
    if ((client_fd = accept(server_fd, (SA*)&amp;client_addr, 
                                (socklen_t*)&amp;client_addr_len)) == -1)
    `{`
        handle_error("accept");
        break;
    `}`
    printf("connection from %s, port %dn", 
                inet_ntoa(client_addr.sin_addr), 
                ntohs(client_addr.sin_port));
    write(client_fd, SEND_MSG, sizeof(SEND_MSG));

`}` while (0);
```

客户端<br>`client.c`

```
do
`{`
    struct sockaddr_in server_addr;
    memset((void*)&amp;server_addr, 0, sizeof(struct sockaddr_in));
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_family = AF_INET;
    char buf_write[READ_MAX_SIZE] = SEND_2_SERVER_MSG;
    char buf_read[WRITE_MAX_SIZE];
    memset(buf_read, 0, sizeof(buf_read));

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1)
    `{`
        handle_error("socket");
        break;
    `}`
    if (inet_aton(SERVER_HOST, (struct in_addr*)&amp;server_addr.sin_addr) == 0)
    `{`
        handle_error("inet_aton");
        break;
    `}`
    if (connect(server_fd, (const SA*)&amp;server_addr, sizeof(struct sockaddr_in)) == -1)
    `{`
        handle_error("client connect to server");
        break;
    `}`
    printf("Connect successfully...n");

    ssize_t write_size = write(server_fd, buf_write, strlen(buf_write));
    if (write_size == -1)
    `{`
        handle_error("write");
        break;
    `}`
    ssize_t recv_size = read(server_fd, buf_read, sizeof(buf_read));
    if (recv_size == -1)
    `{`
        handle_error("read");
        break;
    `}`
    printf("recv data: %s size: %ldn", buf_read, recv_size);
`}` while (0);
```

为了提高网络阻塞模型的效率，在服务器端可以使用`fork`子进程来完成<br>
大概的原理图

```
server端
                          +----------+
                          | listenfd |
                          |          |
connect ----------------&gt; |  connfd  |
            ^             +----------+
            |                  |
            |                  | fork 子进程处理
            |                  |
            |             +----------+
            |             | listenfd |
            |             |          |
            +------------ |  connfd  |
                          +----------+

```

这种模型，客户端感受不到，只需要更改服务器端代码即可

```
do
`{`
    struct sockaddr_in server_addr, client_addr;
    unsigned char client_host[256];
    memset((void *)client_host, 0, sizeof(client_host));
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1)
    `{`
        handle_error("socket");
        break;
    `}`
    memset((void *)&amp;server_addr, 0, sizeof(struct sockaddr_in));
    server_addr.sin_family = AF_INET;   /* ipv4 tcp packet */
    server_addr.sin_port = htons(SERVER_PORT); /* convert to network byte order */
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(server_fd, (SA *)&amp;server_addr, sizeof(struct sockaddr_in)) == -1)
    `{`
        handle_error("bind");
        break;
    `}`
    if (listen(server_fd, LISTEN_BACKLOG) == -1)
    `{`
        handle_error("listen");
        break;
    `}`
    for (;;)
    `{`
        printf("waiting for connect to server...n");
        int client_fd;
        int client_addr_len = sizeof(struct sockaddr_in);
        if ((client_fd = accept(server_fd, (struct sockaddr *)&amp;client_addr,
                                    (socklen_t *)&amp;client_addr_len)) == -1)
        `{`
            handle_error("accept");
            break;
        `}`
        printf("connection from %s, port %dn",
                inet_ntoa(client_addr.sin_addr),
                ntohs(client_addr.sin_port));
        // child process to handle client_fd
        if (0 == fork())
        `{`
            close(server_fd); /* child process close listening server_fd */
            write(client_fd, SEND_2_CLIENT_MSG, sizeof(SEND_2_CLIENT_MSG));
            close(client_fd); /* child process close client_fd */
            exit(0);
        `}`
        else /* parent process close client_fd */
            close(client_fd);
    `}`
`}` while (0);
```

多次启动客户端，服务器端，大概是这样

```
➜  LinuxNetwork ./block_server_fork
waiting for connect to server...
connection from 127.0.0.1, port 41458
waiting for connect to server...
connection from 127.0.0.1, port 41459
waiting for connect to server...
```

即使使用`fork`来提升效率，但是`fork`模式，依然有两个致命的缺点

```
1）用 fork() 的问题在于每一个 Connection 进来时的成本太高,如果同时接入的并发连接数太多容易进程数量很多,进程之间的切换开销会很大,同时对于老的内核(Linux)会产生雪崩效应。 
2）用 Multi-thread 的问题在于 Thread-safe 与 Deadlock 问题难以解决，另外有 Memory-leak 的问题要处理,这个问题对于很多程序员来说无异于恶梦,尤其是对于连续服务器的服务器程序更是不可以接受。
```

所以为了提高效率，又提出了以下的非阻塞模型



## 非阻塞模型

直接单独使用这种模型很少用到，因为基本上是一个线程只能同时处理一个`socket`，效率低下，<br>
很多都是结合了下面的`I/O`复用来使用，<br>
所以大概了解一下代码，知道原理即可，借用`UNIX`网络编程书中的一句话

```
进程把一个套接字设置成非阻塞是在通知内核：
当所有请求的I/Ocaozuo非得吧本进程投入睡眠才能完成时，不要把本进程投入睡眠，而是返回一个错误
```

样例代码

`standard_no_block_server.c`

```
do
`{`
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1)
    `{`
        handle_error("socket");
        break;
    `}`
    last_fd = server_fd;
    server_addr.sin_family = AF_INET; 
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;
    bzero(&amp;(server_addr.sin_zero), 8); 

    if (bind(server_fd, (SA *)&amp;server_addr, sizeof(SA)) == -1)
    `{`
        handle_error("bind");
        break;
    `}`
    if (listen(server_fd, LISTEN_BACKLOG) == -1)
    `{`
        handle_error("listen");
        break;
    `}`
    if ((client_fd = accept(server_fd, 
                        (SA *)&amp;client_addr,
                            (socklen_t*)&amp;sin_size)) == -1)
    `{`
        handle_error("accept");
        break;
    `}`

    fcntl(last_fd, F_SETFL, O_NONBLOCK); 
    fcntl(client_fd, F_SETFL, O_NONBLOCK);  
    for (; ;)
    `{`
        for (int i = server_fd; i &lt;= last_fd; i++)
        `{`
            printf("Round number %dn", i);
            if (i == server_fd)
            `{`
                sin_size = sizeof(struct sockaddr_in);
                if ((client_fd = accept(server_fd, (SA *)&amp;client_addr,
                                    (socklen_t*)&amp;sin_size)) == -1)
                `{`
                    handle_error("accept");
                    continue;
                `}`
                printf("server: got connection from %sn",
                        inet_ntoa(client_addr.sin_addr));
                fcntl(client_fd, F_SETFL, O_NONBLOCK);
                last_fd = client_fd;
            `}`
            else
            `{`
                ssize_t recv_size = read(client_fd, buf_read, READ_MAX_SIZE);
                if (recv_size &lt; 0)
                `{`
                    handle_error("recv");
                    break;
                `}`
                if (recv_size == 0)
                `{`
                    close(client_fd);
                    continue;
                `}`
                else
                `{`
                    buf_read[recv_size] = '';
                    printf("The string is: %s n", buf_read);
                    if (write(client_fd, SEND_2_CLIENT_MSG, strlen(SEND_2_CLIENT_MSG)) == -1)
                    `{`
                        handle_error("send");
                        continue;
                    `}`
                `}`
            `}`
        `}`
    `}`
`}` while (0);

```

缺点就是使用大量的`CPU`轮询时间，浪费了大量的宝贵的服务器`CPU`资源



## I/O复用

无论是阻塞还是单纯的非阻塞模型，最致命的缺点就是效率低，在处理大量请求时，无法满足使用需求<br>
所以就需要用到接下来介绍的各种`I/O`复用方式了

### <a class="reference-link" name="select"></a>select

`select`方式简单点来说就是一个用户线程，一次监控多个`socket`，显然要比简单的单线程单`socket`速度要快很多很多。<br>
这部分主要来源于参考链接-`Linux编程之select`<br>
无论是以后讲到的`poll`还是`epoll`，原理和`select`基本相同，所以这里简单用一个流程图来表述一下`select`使用

```
User Thread           Kernel 
           |                    |
           |       select       |
         socket ------------&gt;   + 
           |                    | 
      block|                    | 等待数据
           |       Ready        | 
           +  &lt;---------------- +
           |                    |
           |      Request       | 拷贝数据
           +    ------------&gt;   +
           |                    | 
           |      Response      |
           +    &lt;------------   +
```

从流程上来看，使用`select`函数进行IO请求和同步阻塞模型没有太大的区别，甚至还多了添加监视`socket`，以及调用`select`函数的额外操作，效率更差。但是，使用`selec`t以后最大的优势是用户可以在一个线程内同时处理多个`socket`的`I/O`请求。用户可以注册多个`socket`，然后不断地调用`select`读取被激活的`socket`，即可达到在同一个线程内同时处理多个`I/O`请求的目的。而在同步阻塞模型中，必须通过多线程的方式才能达到这个目的。

`select`伪码

```
`{`
    select(socket);
    while(1) 
    `{` 
        sockets = select(); 
        for(socket in sockets) 
        `{` 
            if(can_read(socket)) 
            `{` 
                read(socket, buffer); 
                process(buffer); 
            `}` 
        `}` 
    `}` 
`}`
```

`select`语法

```
#include &lt;sys/select.h&gt;
#include &lt;sys/time.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;unistd.h&gt;
int select(int maxfdp, fd_set *readset, fd_set *writeset, fd_set *exceptset,struct timeval *timeout);
```

参数说明：<br>`maxfdp`：被监听的文件描述符的总数，它比所有文件描述符集合中的文件描述符的最大值大1，因为文件描述符是从0开始计数的；<br>`readfds/writefds/exceptset`：分别指向可读、可写和异常等事件对应的描述符集合。<br>`timeout`:用于设置`select`函数的超时时间，即告诉内核`select`等待多长时间之后就放弃等待。`timeout == NULL`表示等待无限长的时间<br>`timeval`结构体定义如下：

```
struct timeval
`{` 
    long tv_sec;   /*秒 */
    long tv_usec;  /*微秒 */
`}`;
```

返回值：超时返回0;失败返回`-1`；成功返回大于`0`的整数，这个整数表示就绪描述符的数目。<br>`select`使用时有几个比较重要的宏

```
int  FD_ISSET(int fd, fd_set *set); -&gt; 测试fd是否在set中
void FD_SET(int fd, fd_set *set); -&gt; 添加fd进set中
void FD_ZERO(fd_set *set); -&gt; 将set置零
```

给出一个案例来详细说明`select`的使用

`select_server.c`

```
do
`{`
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1)
    `{`
        handle_error("socket");
        break;
    `}`

    memset((void*)&amp;server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(SERVER_PORT);

    if (-1 == bind(server_fd, 
                (struct sockaddr*)&amp;server_addr, 
                sizeof(server_addr)))
    `{`
        handle_error("bind");
        break;
    `}`

    if (-1 == listen(server_fd, LISTEN_BACKLOG))
    `{`
        handle_error("listen");
        break;
    `}`

    maxfd = server_fd; 
    maxi = -1;
    for (i = 0; i &lt; FD_SETSIZE; i++)
        client[i] = -1; 
    FD_ZERO(&amp;allset);
    FD_SET(server_fd, &amp;allset);

    for (;;)
    `{`
        rset = allset;
        nready = select(maxfd + 1, &amp;rset, NULL, NULL, NULL);

        if (FD_ISSET(server_fd, &amp;rset))
        `{`
            clilen = sizeof(client_addr);
            client_fd = accept(server_fd, (SA*)&amp;client_addr, &amp;clilen);

            printf("connection from %s, port %dn", 
                inet_ntoa(client_addr.sin_addr), 
                ntohs(client_addr.sin_port));

            for (i = 0; i &lt; FD_SETSIZE; i++)
            `{`
                if (client[i] &lt; 0)
                `{`
                    client[i] = client_fd;
                    break;
                `}`
            `}`
            if (i == FD_SETSIZE)
            `{`
                handle_error("too many clients");
                break;
            `}`

            FD_SET(client_fd, &amp;allset); 
            if (client_fd &gt; maxfd)
                maxfd = client_fd; 
            if (i &gt; maxi)
                maxi = i; 

            if (--nready &lt;= 0)
                continue; /* no more readable descriptors */
        `}`

        for (i = 0; i &lt;= maxi; i++)
        `{`
            if ((monitfd = client[i]) &lt; 0)
                continue;
            if (FD_ISSET(monitfd, &amp;rset))
            `{`
                // 请求关闭连接
                if ((n = read(monitfd, buf_read, READ_MAX_SIZE)) == 0)
                `{`
                    printf("client[%d] aborted connectionn", i);
                    close(monitfd);
                    client[i] = -1;
                `}`
                // 发生错误
                if (n &lt; 0)
                `{`
                    printf("client[%d] closed connectionn", i);
                    close(monitfd);
                    client[i] = -1;
                    handle_error("read");
                    break;
                `}`
                else // 发送数据给客户端
                `{`
                    printf("Client: %sn", buf_read);
                    write(monitfd, buf_write, strlen(buf_write));
                `}`

                if (--nready &lt;= 0)
                    break;
            `}`
        `}`
    `}`
`}` while (0);
```

编译&amp;运行

```
➜  LinuxNetwork make 

➜  LinuxNetwork ./select_server
connection from 127.0.0.1, port 35767 
Client: Hello, message from client. 
client[0] aborted connection 
Client: Hello, message from client.

➜  LinuxNetwork ./client 
Connect successfully...
recv data: Hello, message from server. size: 27
```

最后，来说一下`select`的缺点

```
1、单个进程可监视的fd数量被限制，即能监听端口的大小有限。一般来说这个数目和系统内存关系很大，具体数目可以cat/proc/sys/fs/file-max察看。32位机默认是1024个。64位机默认是2048.
2、 对socket进行扫描时是线性扫描，即采用轮询的方法，效率较低：当套接字比较多的时候，每次select()都要通过遍历FD_SETSIZE个Socket来完成调度,不管哪个Socket是活跃的,都遍历一遍。这会浪费很多CPU时间。如果能给套接字注册某个回调函数，当他们活跃时，自动完成相关操作，那就避免了轮询，这正是epoll与kqueue做的。
3、需要维护一个用来存放大量fd的数据结构，这样会使得用户空间和内核空间在传递该结构时复制开销大。
```

### <a class="reference-link" name="poll"></a>poll

`poll`的机制与`select`类似，与`select`在本质上没有多大差别，管理多个描述符也是进行轮询，根据描述符的状态进行处理，但是`poll`没有最大文件描述符数量的限制。`poll`和`select`同样存在一个缺点就是，包含大量文件描述符的数组被整体复制于用户态和内核的地址空间之间，而不论这些文件描述符是否就绪，它的开销随着文件描述符数量的增加而线性增大。

跟`select`基本相同，直接看一下源码

`poll_server.c`

```
do
`{`
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1)
    `{`
        handle_error("socket");
        break;
    `}`
    bzero(&amp;server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(10086);

    if (-1 == bind(server_fd, (SA *)&amp;server_addr, sizeof(server_addr)))
    `{`
        handle_error("bind");
        break;
    `}`

    if (-1 == listen(server_fd, LISTEN_BACKLOG))
    `{`
        handle_error("listen");
        break;
    `}`

    // index 0 存储服务端socket fd
    client[0].fd = server_fd;
    client[0].events = POLLRDNORM;
    for (i = 1; i &lt; OPEN_MAX; i++)
        client[i].fd = -1; /* -1 indicates available entry */
    maxi = 0;              /* max index into client[] array */
                            /* end fig01 */
    for (;;)
    `{`
        nready = poll(client, maxi + 1, -1);

        // 客户端连接请求
        if (client[0].revents &amp; POLLRDNORM)
        `{`
            clilen = sizeof(client_addr);
            client_fd = accept(server_fd, (SA *)&amp;client_addr, &amp;clilen);
            printf("connection from %s, port %dn", 
                inet_ntoa(client_addr.sin_addr), 
                ntohs(client_addr.sin_port));

            // 加入监控集合
            for (i = 1; i &lt; OPEN_MAX; i++)
            `{`
                if (client[i].fd &lt; 0)
                `{`
                    client[i].fd = client_fd; /* save descriptor */
                    break;
                `}`
            `}`
            if (i == OPEN_MAX)
            `{`
                handle_error("too many clients");
                break;
            `}`

            // 设置新fd events可读
            client[i].events = POLLRDNORM;
            if (i &gt; maxi)
                maxi = i; /* max index in client[] array */

            if (--nready &lt;= 0)
                continue; /* no more readable descriptors */
        `}`

        // 轮询所有使用中的事件
        for (i = 1; i &lt;= maxi; i++)
        `{`
            if ((monitfd = client[i].fd) &lt; 0)
                continue;

            if (client[i].revents &amp; (POLLRDNORM | POLLERR))
            `{`
                if ((n = read(monitfd, buf_read, READ_MAX_SIZE)) &lt; 0)
                `{`
                    if (errno == ECONNRESET)
                    `{`
                        printf("client[%d] aborted connectionn", i);
                        close(monitfd);
                        client[i].fd = -1;
                    `}`
                    else
                        printf("read error");
                `}`
                else if (n == 0)
                `{`
                    printf("client[%d] closed connectionn", i);
                    close(monitfd);
                    client[i].fd = -1;
                `}`
                else
                `{`
                    printf("Client: %sn", buf_read);
                    write(monitfd, buf_write, strlen(buf_write));
                `}`

                if (--nready &lt;= 0)
                    break;
            `}`
        `}`
    `}`
`}` while (0);
```

`poll`解决了`select`使用中`socket`数目的限制，但是`poll`也存在着和`select`一样的致命缺点，需要浪费大量的cpu时间去轮询监控的`socket`，随着监控的`socket`数目增加，性能线性增加，所以为了解决这个问题，`epoll`被开发出来了

### <a class="reference-link" name="epoll"></a>epoll

`epoll`是`poll`的升级版本，拥有`poll`的优势，而且不需要轮询来消耗不必要的`cpu`，极大的提高了工作效率<br>
目前`epoll`存在两种工作模式
<li>
`LT`(`level triggered`，水平触发模式)是缺省的工作方式，并且同时支持`block`和`non-block socket`。在这种做法中，内核告诉你一个文件描述符是否就绪了，然后你可以对这个就绪的`fd`进行`I/O`操作。如果你不作任何操作，内核还是会继续通知你的，所以，这种模式编程出错误可能性要小一点。比如内核通知你其中一个fd可以读数据了，你赶紧去读。你还是懒懒散散，不去读这个数据，下一次循环的时候内核发现你还没读刚才的数据，就又通知你赶紧把刚才的数据读了。这种机制可以比较好的保证每个数据用户都处理掉了。</li>
<li>
`ET`(`edge-triggered`，边缘触发模式)是高速工作方式，只支持`no-block socket`。在这种模式下，当描述符从未就绪变为就绪时，内核通过`epoll`告诉你。然后它会假设你知道文件描述符已经就绪，并且不会再为那个文件描述符发送更多的就绪通知，等到下次有新的数据进来的时候才会再次出发就绪事件。简而言之，就是内核通知过的事情不会再说第二遍，数据错过没读，你自己负责。这种机制确实速度提高了，但是风险相伴而行。</li>
`epoll`使用时需要使用到的API和相关数据结构

```
//用户数据载体
typedef union epoll_data `{`
   void    *ptr;
   int      fd;
   uint32_t u32;
   uint64_t u64;
`}` epoll_data_t;
//fd装载入内核的载体
 struct epoll_event `{`
     uint32_t     events;    /* Epoll events */
     epoll_data_t data;      /* User data variable */
 `}`;

 /* 创建一个epoll的句柄，size用来告诉内核需要监听的数目一共有多大。当创建好epoll句柄后，
它就是会占用一个fd值，所以在使用完epoll后，必须调用close()关闭，否则可能导致fd被耗尽。*/
int epoll_create(int size);  

/*epoll的事件注册函数*/
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event); 

/*等待事件的到来，如果检测到事件，就将所有就绪的事件从内核事件表中复制到它的第二个参数events指向的数组*/
int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);
```

`epoll`的事件注册函数`epoll_ctl`，第一个参数是`epoll_create`的返回值，第二个参数表示动作，使用如下三个宏来表示：

```
POLL_CTL_ADD    //注册新的fd到epfd中；
EPOLL_CTL_MOD    //修改已经注册的fd的监听事件；
EPOLL_CTL_DEL    //从epfd中删除一个fd；
```

其中结构体`epoll_event`中`events`的值

```
EPOLLIN     //表示对应的文件描述符可以读（包括对端SOCKET正常关闭）；
EPOLLOUT    //表示对应的文件描述符可以写；
EPOLLPRI    //表示对应的文件描述符有紧急的数据可读（这里应该表示有带外数据到来）；
EPOLLERR    //表示对应的文件描述符发生错误；
EPOLLHUP    //表示对应的文件描述符被挂断；
EPOLLET     //将EPOLL设为边缘触发(Edge Triggered)模式，这是相对于水平触发(Level Triggered)来说的。
EPOLLONESHOT//只监听一次事件，当监听完这次事件之后，如果还需要继续监听这个socket的话，需要再次把这个socket加入到EPOLL队列里。
```

了解了基本情况，那么直接来看基本的案例代码

`epoll_server.c`

```
do
`{`
    int client_fd, sockfd, epfd, nfds;
    ssize_t n;
    char buf_write[READ_MAX_SIZE] = SEND_2_CLIENT_MSG;
    char buf_read[WRITE_MAX_SIZE];
    memset(buf_read, 0, sizeof(buf_read));

    socklen_t clilen;
    //声明epoll_event结构体的变量,ev用于注册事件,数组用于回传要处理的事件
    struct epoll_event ev, events[20];
    //生成用于处理accept的epoll专用的文件描述符
    epfd = epoll_create(256);
    struct sockaddr_in client_addr;
    struct sockaddr_in server_addr;
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    // 设置为非阻塞
    fcntl(server_fd, F_SETFL, O_NONBLOCK);
    if (server_fd == -1)
    `{`
        handle_error("socket");
        break;
    `}`
    //把socket设置为非阻塞方式
    //setnonblocking(server_fd);

    //设置与要处理的事件相关的文件描述符
    ev.data.fd = server_fd;
    //设置要处理的事件类型
    ev.events = EPOLLIN | EPOLLET;
    //注册epoll事件
    epoll_ctl(epfd, EPOLL_CTL_ADD, server_fd, &amp;ev);

    bzero(&amp;server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(10086);
    if (-1 == bind(server_fd, (SA *)&amp;server_addr, sizeof(server_addr)))
    `{`
        handle_error("bind");
        break;
    `}`
    if (-1 == listen(server_fd, LISTEN_BACKLOG))
    `{`
        handle_error("listen");
        break;
    `}`

    for (;;)
    `{`
        //等待epoll事件的发生
        nfds = epoll_wait(epfd, events, 20, 500);
        if (nfds == -1)
        `{`
            handle_error("epoll_wait");
            break;
        `}`
        //处理所发生的所有事件
        for (int i = 0; i &lt; nfds; ++i)
        `{`
            // server_fd 事件
            if (events[i].data.fd == server_fd)
            `{`
                client_fd = accept(server_fd, (SA *)&amp;client_addr, &amp;clilen);
                if (client_fd == -1)
                `{`
                    handle_error("accept");
                    break;
                `}`
                fcntl(client_fd, F_SETFL, O_NONBLOCK);
                printf("connection from %s, port %dn",
                        inet_ntoa(client_addr.sin_addr),
                        ntohs(client_addr.sin_port));
                //设置用于读操作的文件描述符
                ev.data.fd = client_fd;
                //设置用于注测的读操作事件
                ev.events = EPOLLIN | EPOLLET;
                //注册ev
                epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &amp;ev);
            `}`
            else if (events[i].events &amp; EPOLLIN) //已连接用户，并且收到数据，那么进行读入。
            `{`
                if ((sockfd = events[i].data.fd) &lt; 0)
                    continue;
                if ((n = read(sockfd, buf_read, READ_MAX_SIZE)) &lt; 0)
                `{`
                    // 删除sockfd
                    epoll_ctl(epfd, EPOLL_CTL_DEL, sockfd, NULL);
                    if (errno == ECONNRESET)
                    `{`
                        close(sockfd);
                        events[i].data.fd = -1;
                    `}`
                    else
                    `{`
                        handle_error("read");
                        break;
                    `}`
                `}`
                else if (n == 0)
                `{`
                    // 删除sockfd
                    epoll_ctl(epfd, EPOLL_CTL_DEL, sockfd, NULL);
                    close(sockfd);
                    events[i].data.fd = -1;
                `}`
                else
                `{`
                    //设置用于写操作的文件描述符
                    ev.data.fd = sockfd;
                    //设置用于注测的写操作事件
                    ev.events = EPOLLOUT | EPOLLET;
                    //修改sockfd上要处理的事件为EPOLLOUT
                    epoll_ctl(epfd, EPOLL_CTL_MOD, sockfd, &amp;ev);
                    printf("Client: %sn", buf_read);
                `}`
            `}`
            else if (events[i].events &amp; EPOLLOUT) // 如果有数据发送
            `{`
                sockfd = events[i].data.fd;
                write(sockfd, buf_write, strlen(buf_write));
                //设置用于读操作的文件描述符
                ev.data.fd = sockfd;
                //设置用于注测的读操作事件
                ev.events = EPOLLIN | EPOLLET;
                //修改sockfd上要处理的事件为EPOLIN
                epoll_ctl(epfd, EPOLL_CTL_MOD, sockfd, &amp;ev);
            `}`
        `}`
    `}`
`}` while (0);
```

编译&amp;执行

```
➜  LinuxNetwork make 

➜  LinuxNetwork ./epoll_server
connection from 127.0.0.1, port 50640
Client: Hello, message from client.

➜  LinuxNetwork ./client 
Connect successfully...
recv data: Hello, message from server. size: 27
```

比较`epoll`的代码和`poll`代码最大的区别，在监控所有`socket`的过程中，并不需要不断的轮询监控的`socket`去检查其状态，效率有了巨大的提升<br>
介绍完`epoll`的语法和相关实现，现在来看`epoll`优势

```
1. 支持一个进程打开大数目的socket描述符
2. IO效率不随FD数目增加而线性下降
3. 使用mmap加速内核与用户空间的消息传递(这个需要阅读epoll实现源码)
```



## 信号驱动

信号驱动式`I/O`是指进程预先告知内核，使得当某个描述符上发生某事时，内核使用信号通知相关进程

主要用于`UDP`数据通信,其用到的`API`

```
#include &lt;signal.h&gt;
typedef void (*sighandler_t)(int);
sighandler_t signal(int signum, sighandler_t handler);        

int sigaction(int signum, const struct sigaction *act,     
             struct sigaction *oldact);
```

其中`sigaction`结构体

```
struct sigaction `{`
  void     (*sa_handler)(int);                           // 信号处理函数
  void     (*sa_sigaction)(int, siginfo_t *, void *);    // 同上, 某些OS实现时联合体
  sigset_t   sa_mask;                                    // 信号掩码, 用于屏蔽信号
  int        sa_flags;                                   // 设置标志
  void     (*sa_restorer)(void);                         // 不是为应用准备的,见sigreturn(2)
`}`;
```

其中设置标志，使用`fcntl`函数

```
#include &lt;unistd.h&gt;
#include &lt;fcntl.h&gt;
int fcntl(int fd, int cmd, ... /* arg */ );
```

这里没有看到特别大的用处，直接给一个案例代码，以后遇到再细说

`sigio_server.c`

```
int server_fd;

void do_sigio(int sig)
`{`
    char buf_read[READ_MAX_SIZE];
    memset((void *)buf_read, 0, sizeof(buf_read));
    struct sockaddr_in client_addr; 
    unsigned int clntLen; 
    int recvMsgSize; 
    do 
    `{`
        clntLen = sizeof(client_addr);
        if ((recvMsgSize = recvfrom(server_fd, 
                                buf_read, 
                                READ_MAX_SIZE, 
                                MSG_WAITALL,
                                (SA *)&amp;client_addr, 
                                &amp;clntLen)) &lt; 0)
        `{`
            if (errno != EWOULDBLOCK)
            `{`
                handle_error("recvfrom");
                break;
            `}`
        `}`
        else
        `{`
            printf("connection from %s, port %d, data: %sn", 
                    inet_ntoa(client_addr.sin_addr), 
                    ntohs(client_addr.sin_port), buf_read);
            if (sendto(server_fd, 
                       SEND_2_CLIENT_MSG, 
                       strlen(SEND_2_CLIENT_MSG), 
                       0, 
                       (SA *)&amp;client_addr, 
                       sizeof(client_addr)) != strlen(SEND_2_CLIENT_MSG))
            `{`
                handle_error("sendto");
                break;
            `}`
        `}`
    `}` while (0);
`}`

int main()
`{`
    server_fd = -1;
    do
    `{`
        struct sockaddr_in server_addr;
        server_fd = socket(AF_INET, SOCK_DGRAM, 0);
        if (server_fd == -1)
        `{`
            handle_error("socket");
            break;
        `}`

        bzero((char *)&amp;server_addr, sizeof(server_addr));
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(SERVER_PORT);
        server_addr.sin_addr.s_addr = INADDR_ANY;

        if (-1 == bind(server_fd, (SA *)&amp;server_addr, sizeof(server_addr)))
        `{`
            handle_error("bind");
            break;
        `}`

        struct sigaction sigio_action;
        memset(&amp;sigio_action, 0, sizeof(sigio_action));
        sigio_action.sa_flags = 0;
        sigio_action.sa_handler = do_sigio;
        if (sigfillset(&amp;sigio_action.sa_mask) &lt; 0) 
        `{`
            handle_error("sigfillset");
            break;
        `}`
        sigaction(SIGIO, &amp;sigio_action, NULL);
        if (-1 == fcntl(server_fd, F_SETOWN, getpid()))
        `{`
            handle_error("fcntl_setdown");
            break;
        `}`

        int flags;
        flags = fcntl(server_fd, F_GETFL, 0);
        if (flags == -1)
        `{`
            handle_error("fcntl_getfl");
            break;
        `}`
        flags |= O_ASYNC | O_NONBLOCK;
        fcntl(server_fd, F_SETFL, flags);
        for (; ;)
        `{`
            printf("waiting ...n");
            sleep(3);
        `}`
        close(server_fd);
    `}` while (0);
    return 0;
`}`
```

编译及运行

```
➜  LinuxNetwork make 

➜  LinuxNetwork ./sigio_server
waiting...
connection from 127.0.0.1, port 58119, data: Hello, message from server. 

➜  LinuxNetwork ./client_udp 
recv data: Hello, message from server. size: 27
```



## 异步I/O

目前该方面的技术还不够成熟，对于我们寻找网络组件方面的漏洞，帮助不大，这里略过了<br>
套用知乎上的一个大佬说的

```
glibc的aio有bug, 
Linux kernel的aio只能以O_DIRECT方式做直接IO,libeio也是beta阶段。
epoll是成熟的，但是epoll本身是同步的。
```



## 总结

至此我们简单的将`Linux`目前用到的网络模型做了介绍，每个模型，都使用了相关的代码来做案例，需要重点关注的是`I/O`复用的部分，平时碰到的可能会比较多。

介绍完这些，为我们以后挖掘网络组件方面的漏洞做了一些基础铺垫。接下来可以来挖网络组件的洞了



## 参考链接

[使用libevent和libev提高网络应用性能——I/O模型演进变化史](https://blog.csdn.net/hguisu/article/details/38638183)

[io模型详述](https://www.jianshu.com/p/486b0965c296)

[unix网络编程源码](http://www.cs.cmu.edu/afs/cs/academic/class/15213-f00/unpv12e/tcpcliserv/)

[Linux编程之select](https://www.cnblogs.com/skyfsm/p/7079458.html)

[IO多路复用之poll总结](https://www.cnblogs.com/anker/p/3261006.html)

[Linux编程之epoll](https://www.cnblogs.com/skyfsm/p/7102367.html)

[深入理解IO复用之epoll](https://zhuanlan.zhihu.com/p/87843750)

[demo sigio c example](https://man7.org/tlpi/code/online/diff/altio/demo_sigio.c.html)

[UDP Echo Server c example](http://cs.baylor.edu/~donahoo/practical/CSockets/code/UDPEchoServer-SIGIO.c)

[信号与信号驱动IO](https://evil-crow.github.io/signal_io/)

[linux下的异步IO（AIO）是否已成熟？](zhihu.com/question/26943558)
