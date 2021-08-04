> 原文链接: https://www.anquanke.com//post/id/248666 


# 物联网设备常见的web服务器——uhttpd源码分析（二）


                                阅读量   
                                **24129**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t017d898302e4b73114.jpg)](https://p5.ssl.qhimg.com/t017d898302e4b73114.jpg)



## 0x00 前言

uHTTPd 是一个 OpenWrt/LUCI 开发者从头编写的 Web 服务器。 它着力于实现一个稳定高效的服务器，能够满足嵌入式设备的轻量级任务需求，且能够与 OpenWrt 的配置框架 (UCI) 整合。默认情况下它被用于 OpenWrt 的 Web 管理接口 LuCI。当然，uHTTPd 也能提供一个常规 Web 服务器所需要的所有功能。



## 0x01 简介

物联网设备常见的web服务器——uhttpd源码分析（一）：[https://www.freebuf.com/articles/network/269696.html](https://www.freebuf.com/articles/network/269696.html)



## 0x02 run_server函数

位置：main–&gt;run_server

```
static int run_server(void) 
`{` 
        uloop_init();//epoll等函数的初始化 
        uh_setup_listeners();//设置监听回调函数 
        uh_plugin_post_init();//插件初始化 
        uloop_run(); //uloop_run轮询处理定时器、进程、描述符事件等。 
        return 0; 
`}`
```

# <a class="reference-link" name="0x03%20uloop_init%E5%87%BD%E6%95%B0"></a>0x03 uloop_init函数

主要位置：main–&gt;run_server–&gt;uloop_init–&gt;uloop_init_pollfd

```
static int uloop_init_pollfd(void) 
`{` 
        if (poll_fd &gt;= 0) 
                return 0; 

        poll_fd = epoll_create(32); 
        if (poll_fd &lt; 0) 
                return -1; 

        fcntl(poll_fd, F_SETFD, fcntl(poll_fd, F_GETFD) | FD_CLOEXEC); 
        return 0; 
`}`
```

### <a class="reference-link" name="0x00%20epoll_create%E5%87%BD%E6%95%B0"></a>0x00 epoll_create函数

位置：main–&gt;run_server–&gt;uloop_init–&gt;uloop_init_pollfd–&gt;epoll_create

> <p>该函数生成一个epoll专用的文件描述符。它其实是在内核申请一空间，用来存放你想关注的socket fd上是否发生以及发生了什么事件。size就是你在这个epoll fd上能关注的最大socket fd数。这里最大数量为32。<br>
参考：<br>[https://blog.csdn.net/yusiguyuan/article/details/15027821](https://blog.csdn.net/yusiguyuan/article/details/15027821)</p>

### <a class="reference-link" name="0x01%20fcntl%E5%87%BD%E6%95%B0"></a>0x01 fcntl函数

位置：main–&gt;run_server–&gt;uloop_init–&gt;uloop_init_pollfd–&gt;fcntl

> <p>通过fcntl可以改变已打开的文件性质。fcntl针对描述符提供控制。参数fd是被参数cmd操作的描述符。<br>
参考：<br>[https://baike.baidu.com/item/fcntl/6860021?fr=aladdin](https://baike.baidu.com/item/fcntl/6860021?fr=aladdin)<br>[https://blog.csdn.net/qq_37414405/article/details/83690447](https://blog.csdn.net/qq_37414405/article/details/83690447)</p>



## 0x04 uh_setup_listeners函数

位置：main–&gt;run_server–&gt;uh_setup_listeners

```
void uh_setup_listeners(void) 
`{` 
        struct listener *l; 
        int yes = 1; 

        list_for_each_entry(l, &amp;listeners, list) `{` 
                int sock = l-&gt;fd.fd; 

                /* TCP keep-alive */ 
                if (conf.tcp_keepalive &gt; 0) `{` 
#ifdef linux 
                        int tcp_ka_idl, tcp_ka_int, tcp_ka_cnt, tcp_fstopn; 

                        tcp_ka_idl = 1; 
                        tcp_ka_cnt = 3; 
                        tcp_ka_int = conf.tcp_keepalive; 
                        tcp_fstopn = 5; 
                        /*检测网线非法断开*/ 
                        setsockopt(sock, SOL_TCP, TCP_KEEPIDLE,  &amp;tcp_ka_idl, sizeof(tcp_ka_idl)); 
                        setsockopt(sock, SOL_TCP, TCP_KEEPINTVL, &amp;tcp_ka_int, sizeof(tcp_ka_int)); 
                        setsockopt(sock, SOL_TCP, TCP_KEEPCNT,   &amp;tcp_ka_cnt, sizeof(tcp_ka_cnt)); 
                        setsockopt(sock, SOL_TCP, TCP_FASTOPEN,  &amp;tcp_fstopn, sizeof(tcp_fstopn)); 
#endif 

                        setsockopt(sock, SOL_SOCKET, SO_KEEPALIVE, &amp;yes, sizeof(yes)); 
                `}` 

                l-&gt;fd.cb = listener_cb;//accept接受数据函数就在listener_cb中 
                uloop_fd_add(&amp;l-&gt;fd, ULOOP_READ); 
        `}` 
`}`
```

> 最主要关注 l-&gt;fd.cb = listener_cb

### <a class="reference-link" name="0x00%20setsockopt%E5%87%BD%E6%95%B0"></a>0x00 setsockopt函数

位置：main–&gt;run_server–&gt;uloop_init–&gt;uloop_init_pollfd–&gt;epoll_create

> <p>int setsockopt(int sockfd, int level, int optname,const void *optval, socklen_t optlen);<br>
sockfd：标识一个套接口的描述字。<br>
level：选项定义的层次；支持SOL_SOCKET、IPPROTO_TCP、IPPROTO_IP和IPPROTO_IPV6。<br>
optname：需设置的选项。<br>
optval：指针，指向存放选项待设置的新值的缓冲区。<br>
optlen：optval缓冲区长度。<br>
主要是用来检查网络异常后的操作。<br>
参考：<br>[https://www.oschina.net/question/128542_2149349](https://www.oschina.net/question/128542_2149349)<br>[https://baike.baidu.com/item/setsockopt/10069288?fr=aladdin](https://baike.baidu.com/item/setsockopt/10069288?fr=aladdin)</p>



## 0x05 listener_cb函数

位置：main–&gt;run_server–&gt;uh_setup_listeners

> 当通过epoll有数据过来后，会去调用listener_cb函数，并执行accept函数去对应的数据。

```
static void listener_cb(struct uloop_fd *fd, unsigned int events) 
`{` 
        struct listener *l = container_of(fd, struct listener, fd);//获取struct listener结构体的起始地址 

        while (1) `{` 
                if (!uh_accept_client(fd-&gt;fd, l-&gt;tls))//accept接受数据,并设置对应的回调函数 
                        break; 
        `}` 
        /*如果连接数大于或等于最大连接数则执行删除对应的fd操作,最大连接数默认为100*/ 
        if (conf.max_connections &amp;&amp; n_clients &gt;= conf.max_connections) 
                uh_block_listener(l);//删除全局变量对应的fd,主要操作就是将对应的全局变量的fd设置为NULL,和设置事件的值 
`}`
```

### <a class="reference-link" name="0x00%20uh_accept_client%E5%87%BD%E6%95%B0"></a>0x00 uh_accept_client函数

位置：listener_cb–&gt;uh_accept_client

```
/*accept接受数据,并设置对应的回调函数*/ 
bool uh_accept_client(int fd, bool tls) 
`{` 
        static struct client *next_client; 
        struct client *cl; 
        unsigned int sl; 
        int sfd; 
        static int client_id = 0; 
        struct sockaddr_in6 addr; 

        if (!next_client) 
                next_client = calloc(1, sizeof(*next_client));//申请内存 

        cl = next_client; 

        sl = sizeof(addr); 
        sfd = accept(fd, (struct sockaddr *) &amp;addr, &amp;sl); 
        if (sfd &lt; 0) 
                return false; 

        set_addr(&amp;cl-&gt;peer_addr, &amp;addr);//addr拷贝到cl-&gt;peer_addr中 
        sl = sizeof(addr); 
        getsockname(sfd, (struct sockaddr *) &amp;addr, &amp;sl);//服务器端可以通过它得到相关客户端地址 
        set_addr(&amp;cl-&gt;srv_addr, &amp;addr); 

        cl-&gt;us = &amp;cl-&gt;sfd.stream; 
        if (tls) `{` 
                uh_tls_client_attach(cl); 
        `}` else `{` 
                cl-&gt;us-&gt;notify_read = client_ustream_read_cb;//读操作 
                cl-&gt;us-&gt;notify_write = client_ustream_write_cb;//写操作 
                cl-&gt;us-&gt;notify_state = client_notify_state;//通知状态 
        `}` 

        cl-&gt;us-&gt;string_data = true; 
        ustream_fd_init(&amp;cl-&gt;sfd, sfd);//将sfd赋值给cl中的fd,以便后续使用 

        uh_poll_connection(cl);//主要用来设置超时定时器 
        list_add_tail(&amp;cl-&gt;list, &amp;clients); 

        next_client = NULL; 
        n_clients++;//作用可以看listener_cb函数，主要作用是总共连接数 
        cl-&gt;id = client_id++; 
        cl-&gt;tls = tls; 

        return true; 
`}`
```

### <a class="reference-link" name="0x01%20calloc%E5%87%BD%E6%95%B0"></a>0x01 calloc函数

位置：listener_cb–&gt;uh_accept_client–&gt;calloc

> <p>void *calloc(size_t nitems, size_t size)<br>
分配所需的内存空间，并返回一个指向它的指针。malloc 和 calloc 之间的不同点是，malloc 不会设置内存为零，而 calloc 会设置分配的内存为零。<br>
参考：<br>[https://www.runoob.com/cprogramming/c-function-calloc.html](https://www.runoob.com/cprogramming/c-function-calloc.html)</p>

### <a class="reference-link" name="0x02%20accept%E5%87%BD%E6%95%B0"></a>0x02 accept函数

位置：listener_cb–&gt;uh_accept_client–&gt;accept

> <p>int accept(int sockfd,struct sockaddr **addr,socklen_t **addrlen);<br>
如果函数执行正确的话，将会返回新的套接字描述符，用于指向与当前通信的客户端发送或接收数据。<br>
参考：<br>[http://blog.chinaunix.net/uid-28595538-id-4919587.html](http://blog.chinaunix.net/uid-28595538-id-4919587.html)</p>

### <a class="reference-link" name="0x03%20getsockname%E5%87%BD%E6%95%B0"></a>0x03 getsockname函数

位置：listener_cb–&gt;uh_accept_client–&gt;getsockname<br>
int getsockname(int s, struct sockaddr **name, socklen_t **namelen);<br>
服务器端可以通过它得到相关客户端地址。<br>
参考：<br>[https://blog.csdn.net/qinrenzhi/article/details/94043263](https://blog.csdn.net/qinrenzhi/article/details/94043263)<br>[https://www.yiibai.com/unix_system_calls/getsockname.html](https://www.yiibai.com/unix_system_calls/getsockname.html)

### <a class="reference-link" name="0x04%20ustream_fd_init%E5%87%BD%E6%95%B0"></a>0x04 ustream_fd_init函数

位置：listener_cb–&gt;uh_accept_client–&gt;ustream_fd_init

```
void ustream_fd_init(struct ustream_fd *sf, int fd) 
`{` 
        struct ustream *s = &amp;sf-&gt;stream; 

        ustream_init_defaults(s); 

        sf-&gt;fd.fd = fd; 
        sf-&gt;fd.cb = ustream_uloop_cb; 
        s-&gt;set_read_blocked = ustream_fd_set_read_blocked; 
        s-&gt;write = ustream_fd_write; 
        s-&gt;free = ustream_fd_free; 
        s-&gt;poll = ustream_fd_poll; //读写操作 
        ustream_fd_set_uloop(s, false); 
`}`
```

> 通过ustream_fd_poll函数会调用uh_accept_client中的回调函数client_ustream_read_cb，真正读取客户端数据的是ustream_fd_poll函数，该函数使用read读取，而client_ustream_read_cb仅仅是操作read出来的数据。



## 0x06 client_ustream_read_cb函数

位置：listener_cb–&gt;uh_accept_client–&gt;client_ustream_read_cb

> 未完待续…
