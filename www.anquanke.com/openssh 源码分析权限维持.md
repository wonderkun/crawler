> 原文链接: https://www.anquanke.com//post/id/237497 


# openssh 源码分析权限维持


                                阅读量   
                                **141396**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01df66fc3652a07c1b.jpg)](https://p5.ssl.qhimg.com/t01df66fc3652a07c1b.jpg)



## 前言

​ 在渗透过程中我们拿下一台主机，往往需要一些权限维持后门手段，一般留后门手段如：增加超级用户、PROMPT_COMMAND变量、放置后门程序等等这些方法往往比较容易被发现，/etc/passwd是管理员的重点检查文件，PROMPT_COMMAND变量又需要管理员登录才能触发，后门程序也可能被管理员找到可疑进程发现，因此想到是否能重新安装openssh在其中中加入后门，而找了一圈分析openssh的文章资料发现又比较少，于是尝试自己分析一波，在openssh中加入后门



## 分析源码：

​ 首先通过github下载openssh的源码，而想要在ssh中加入后门就需要分析sshd的部分，我们可以在源代码中直接找到sshd.c文件，找到main函数浏览整个流程发现ssh用户验证主要在一个函数：

[![](https://p5.ssl.qhimg.com/t01cd54e99631bc0bd7.png)](https://p5.ssl.qhimg.com/t01cd54e99631bc0bd7.png)

​ 而参数ssh可以猜测ssh结构体保存了用户的验证信息，我们找到了ssh结构体的定义



## ssh 结构体：

[![](https://p4.ssl.qhimg.com/t01c4fd7ca99688d2a1.png)](https://p4.ssl.qhimg.com/t01c4fd7ca99688d2a1.png)

​ ssh结构体保存了所有的用户输入数据，包括套接字、密码、套接字、请求类型



## do_authentication2(ssh) 验证函数

[![](https://p0.ssl.qhimg.com/t01f6fa90120d2b0881.png)](https://p0.ssl.qhimg.com/t01f6fa90120d2b0881.png)

### `ssh_dispatch_init(ssh,fun) :`

​ 初始化 ssh-&gt;dispatch[] 数组为dispatch_protocol_error()函数,此函数记录日志并输出错误信息

### `ssh_dispatch_set(ssh,SSH2_MSG_SERVICE_REQUEST,fun):`

​ 定义ssh2_msg_service_request类型处理函数为input_service_requests()

### `ssh_dispatch_run_fatal() &amp;&amp; ssh_dispatch_run()`

[![](https://p3.ssl.qhimg.com/t015810c4bd74f7772b.png)](https://p3.ssl.qhimg.com/t015810c4bd74f7772b.png)

​ ssh_dispatch_run_fatal()调用ssh_dispatch_run()函数判断函数结果，失败则记录日志

​ ssh_dispatch_run(ssh,mode,done) 循环，直到验证成功退出循环，或者超过最大重试次数

​ ssh_packet_read_seqnr(ssh,type,seqnr)!=0 | ssh_packet_read_poll_seqnr(ssh,type,seqnr)

​ 获取socket收到的数据，存储在ssh结构体中,type保存收到的请求类型

​ **r = (*ssh-&gt;dispatch[type])(type,seqnr,ssh)**

​ 调用前面设置的函数处理数据，数据都在ssh结构体中,done指向ssh-&gt;authctxt-&gt;success 处理成功时处理函数会改变done的结果，done为True时循环结束

​ 继续跟进，sshd收到第一条请求时会调用函数 **input_service_request()**



## input_service_request(type,seq,ssh) 处理service_request

[![](https://p0.ssl.qhimg.com/t015509c3752becf40b.png)](https://p0.ssl.qhimg.com/t015509c3752becf40b.png)

```
sshpkt_get_cstring(ssh,&amp;service,null)     //获取请求类型，保存在&amp;service
strcmp(service,'ssh-userauth')     //判断如果成立则断开连接，并设置SSH2_MSG_USERAUTH_REQUESTS处理函数，也就是用户验证请求，根据此函数的内容，可以判断 sshd启动后收到请求触发设置auth_rquest处理函数
ssh_dispatch_set(ssh,SSH2_MSG_USERAUTH_REQUEST,&amp;input_userauth_requests)//设置验证处理函数，现在可以开始验证用户了
sshpkt_start(ssh,SSH2_MSG_SERVICE_ACCEPT) || sshpkt_put_cstring(ssh,service) || sshpkt_send(ssh) || ssh_packet_write_wait(ssh)         //如果strmcp没有成立，正常处理请求
```



## input_userauth_request(type,seq,ssh) 处理用户验证

[![](https://p1.ssl.qhimg.com/t01d3f795fff63b5524.png)](https://p1.ssl.qhimg.com/t01d3f795fff63b5524.png)

​ 通过method选择其中一个模式的处理函数，而method通过sshpkt_get_cstring()获取到，这里的method大概是通过客户端发送的数据包获取，

​ 查看authmethod_lookup函数最终的返回的最终结果：

```
&gt; m = authmethod_lookup(authctxt,method)`{`
&gt; return authmethods[i]
&gt; `}`
```

authmethod_lookup()函数最终返回为authmethods结构体中存储的结构体：

[![](https://p1.ssl.qhimg.com/t019f26ccce56d362ff.png)](https://p1.ssl.qhimg.com/t019f26ccce56d362ff.png)

可以猜测数组中的每一项都对应了openssh不同的验证模式，kdbint为keyboard_interactive模式、pubkey公私钥验证模式，而结构体都是类似的结构：

[![](https://p3.ssl.qhimg.com/t01b30e0ff7ef1aea01.png)](https://p3.ssl.qhimg.com/t01b30e0ff7ef1aea01.png)

m-&gt;userauth()调用了结构体中的函数，结构体中只有userauth_kbdint是函数，分析得出passwd验证模式的具体调用流程：

> m-&gt;userauth(ssh);
-&gt; userauth_passwd(ssh)[auth2-passwd.c]
-&gt; auth_passwd(ssh,passwd)[auth-passwd.c]
-&gt; sshpam_auth_passwd[auth-passwd.c]
​ userauth_finish(ssh,authenticated,method,null)

看到这一步可以想到修改流程中验证函数的返回值，绕过验证，但是经过测试，直接修改userauth_passwd()(auth2-passwd.c)的返回值为0， 并不能绕过验证并且会导致输入密码错误直接崩溃报错

[![](https://p2.ssl.qhimg.com/t0153cfa2689d0ef3ed.png)](https://p2.ssl.qhimg.com/t0153cfa2689d0ef3ed.png)

而修改sshpam_auth_passwd(authctxt,password)的返回值也没有达到效果

重新尝试分析keyboard-interactive模式调用流程，发现userauth_kbdint函数有两个（其他类型的同样）：

调用流程：

> m-&gt;userauth(ssh)
-&gt; userauth_kbdint(ssh)]auth2-kbdint.c] debug: keyboard-interactive devs;
-&gt; auth2_challenge(ssh,devs)[auth2-chall.c] debug: auth2_challenge: user=%s devs=%s
-&gt; kbdint_alloc(devs)
​ auth2_challenge_start(ssh)

此时，进入sshd debug模式，查看执行流程，发现在input_userauth_request()请求处理函数中，验证为keyboard-interactive模式，也就是debug2中的method值为keyboard……

而在之前测试过程中发现，重新编译后的sshd走的是keyboard-interactive模式，系统自带的sshd走的是password模式，经过对比sshd_config文件，发现启用了ChallengeResponseAuthentication ,可见当sshd_config中关闭challengeResponseAuthentication时sshd走的password模式验证。（需要开启UsePAM)

[![](https://p2.ssl.qhimg.com/t01710ac2563197600d.png)](https://p2.ssl.qhimg.com/t01710ac2563197600d.png)

至此在sshd_config中加入ChallengeResponseAuthentication no,我们再尝试修改sshpam_auth_passwd()函数可以实现绕过验证效果：

任意密码登录，至此我们再加入判断条件，就可以实现openssh后门



## sshpam_auth_passwd(authctxt,password) 修改函数加入后门

[![](https://p5.ssl.qhimg.com/t01034f3223197bd27d.png)](https://p5.ssl.qhimg.com/t01034f3223197bd27d.png)



## 参考资料

​ [https://man.openbsd.org/sshd.8](https://man.openbsd.org/sshd.8)<br>
​ [https://github.com/openssh/openssh-portable](https://github.com/openssh/openssh-portable)
