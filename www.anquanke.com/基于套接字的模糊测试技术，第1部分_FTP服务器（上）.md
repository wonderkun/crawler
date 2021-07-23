> 原文链接: https://www.anquanke.com//post/id/227120 


# 基于套接字的模糊测试技术，第1部分：FTP服务器（上）


                                阅读量   
                                **93111**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Antonio Morales，文章来源：securitylab.github.com
                                <br>原文地址：[https://securitylab.github.com/research/fuzzing-sockets-FTP](https://securitylab.github.com/research/fuzzing-sockets-FTP)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01d7019a86ea5383c8.jpg)](https://p1.ssl.qhimg.com/t01d7019a86ea5383c8.jpg)



在这篇文章中，我将分享基于套接字的模糊测试研究成果。其中，我们将以三个广泛使用的FTP服务器为例，详细介绍模糊测试的具体过程，以及在这些过程中发现的安全漏洞。

之所以选择FTP协议，是基于以下原因：
1. FTP是使用最广泛的网络协议之一，历史悠久。
1. 它使用了并行通信通道（包括命令通道和数据通道）。
1. 这是一个交互式的文件服务器，允许在服务器端修改文件。
1. 这是一个纯文本协议，原则上并不是模糊测试的最佳选择（我喜欢挑战！）。
此外，我们还将介绍一些修改源代码相关的技巧，以便能够通过AFL++对涉及套接字的软件进行模糊测试。



## 选择的服务器和测试结果

首先，我利用SHODAN API从可用的开源FTP服务器中选择最相关的FTP服务器。在这里，我选择了漏洞曝光数量最多的FTP服务器：
1. Pure-FTPd： 最流行的Linux ftpd。
1. BFtpd：嵌入式系统中非常流行的ftpd。
1. ProFtpd：三者中历史最悠久，但仍然比较流行的Linux ftpd。
经过努力，我挖掘出了以下漏洞：

软件 CVE类型

Pure-FTPd CVE-2019-20176 listdir中的堆栈耗尽漏洞（远程DoS）。

Pure-FTPd CVE-2020-9274 在别名链表中发现未初始化的指针。

Pure-FTPd 未分配 pw_pgsql_connect中的SQL sanitizer破坏漏洞。

Pure-FTPd CVE-2020-9365 在pure_strcmp中发现OOB读取漏洞。

Bftpd CVE-2020-6162 在hidegroups_init()中发现OOB读取漏洞。

Bftpd CVE-2020-6835 多个int-to-bool类型转换漏洞，导致堆溢出。

ProFTPd CVE-2020-9272 在mod_cap中发现OOB读取漏洞。

ProFTPd CVE-2020-9273 数据传输期间内存池中存在UAF漏洞。 



## 模糊测试技巧

当你想对使用套接字获取输入的软件进行模糊测试时，通常首先要对源代码进行一些必要的修改，以方便进行模糊测试。当输入是基于文件的时候，模糊测试过程通常是很简单的，比如像libpng、libjpg等图像库就是如此。在这些情况下，我们几乎无需修改目标源代码。

然而，当处理联网的交互式服务器（如FTP服务器）时，我们发送的请求（上传、下载、并行任务等）可能会引起各种系统状态的变化，这时模糊测试就不是那么简单了。

对于这种情况，一个可能的方法是利用类似Preeny的库。Preeny是一套预加载的库，有助于简化模糊测试和“pwning”任务。除此之外，我们还可以利用Preeny对软件进行de-socket处理，也就是把套接字数据流重定向至stdin和stdout，或反之。

虽然Preeny使用方便，但它的de-socket功能可能无法满足处理模糊测试目标的特殊性所需的精细度。因为每一个软件都是独一无二的，所以，在对软件进行模糊测试时，我们往往希望对如何以及在何处影响输入和进程状态进行细粒度地控制，以确保达到所需的覆盖范围。因此，我通常选择手动修改源代码的方法，这使我在处理极端情况时具有更大的灵活性。 

下面是一些实用的技巧，以帮助您在使用基于套接字的模糊测试技术处理本文涉及的FTP案例时，解决常见的各种挑战。



## 套接字

我们的FTP模糊测试将主要集中在命令通道上，也就是用来传输FTP命令和接收命令响应的通道。

在Linux的情况下，将网络端点支持的文件描述符转换成文件支持的文件描述符通常是非常简单的，不用重写太多的代码。

[![](https://p3.ssl.qhimg.com/t018df82b007abf2d9e.png)](https://p3.ssl.qhimg.com/t018df82b007abf2d9e.png)

在这种情况下，inputFile是当前的AFL文件([input_path]/.cur_input)，我们将其作为一个自定义参数进行传递。

[![](https://p4.ssl.qhimg.com/t015278ba6f91caa02a.png)](https://p4.ssl.qhimg.com/t015278ba6f91caa02a.png)

AFL命令行如下所示： 

_afl-fuzz -t 1000 -m none -i ‘./AFL/afl_in’ -o ‘./AFL/afl_out’ -x ./AFL/dictionaries/basic.dict — ./src/pure-ftpd -S 5000 -dd @@_

这些变更意味着无法调用某些网络API函数了，如getockname和getnameinfo函数（如果调用的话，我们会得到一个ENOTSOCK错误）。所以，我把这些函数的调用注释掉，并把它们的相关结果变量进行硬编码处理。

[![](https://p2.ssl.qhimg.com/t01b6172acb8e0be262.png)](https://p2.ssl.qhimg.com/t01b6172acb8e0be262.png)

同时，我们也不能使用网络fd相关的操作，如send(3)，所以，我们必须求助于较底层的、与网络无关的API，如write(2)。

[![](https://p1.ssl.qhimg.com/t010d784776d9bbda08.png)](https://p1.ssl.qhimg.com/t010d784776d9bbda08.png)

到目前为止，我们只处理了命令通道，但我们还需要确保数据通道接收数据，这样上传和下载功能才能在我们模糊测试过程中发挥作用。

对于文件上传，我使用getrandom(2)来返回随机的文件数据。

[![](https://p5.ssl.qhimg.com/t016d048410e722856b.png)](https://p5.ssl.qhimg.com/t016d048410e722856b.png)

对于文件下载，我们可以直接将文件内容写入stderr。

[![](https://p5.ssl.qhimg.com/t01a1e3b376c99dd5f0.png)](https://p5.ssl.qhimg.com/t01a1e3b376c99dd5f0.png)

因为我们想继续使用stdin和stderr，所以，必须避免关闭数据通道代码中的STDOUT_FILENO(1)和STDERR_FILENO(2)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ae640286c27caeab.png)

除此之外，我们还需要修改依赖外部库的读/写函数，例如OpenSSL：

[![](https://p5.ssl.qhimg.com/t01e07e1c3e204d2c24.png)](https://p5.ssl.qhimg.com/t01e07e1c3e204d2c24.png)



## 修改文件系统调用

因为我们要最大限度地提高发现漏洞的概率，所以删除某些系统调用（如unlink(2)）是很有帮助的。这样可以防止Fuzzer误删文件。 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bdb413ead7a13007.png)

同样，我们也要删除对rmdir(2) (Linux中的目录删除函数) 的所有调用。

[![](https://p5.ssl.qhimg.com/t0168c32e7dd2ebf7c7.png)](https://p5.ssl.qhimg.com/t0168c32e7dd2ebf7c7.png)

由于Fuzzer最终可能会修改文件夹权限，所以定期恢复原始权限是很重要的，因为这样可以避免Fuzzer被卡住。

[![](https://p2.ssl.qhimg.com/t019ab77ee8fbda38b8.png)](https://p2.ssl.qhimg.com/t019ab77ee8fbda38b8.png)



## 事件处理

分析多个事件组合时，通常需要修改事件处理函数。例如，下面我用对FUZZ_poll的调用代替了对poll的调用：

[![](https://p0.ssl.qhimg.com/t01e6741b4149b6988d.png)](https://p0.ssl.qhimg.com/t01e6741b4149b6988d.png)

这个函数的功能非常简单，就是根据RAND_MAX/10和RAND_MAX/5的概率递增fds[0].revents和fds[1].revents的值。

[![](https://p2.ssl.qhimg.com/t0125e1a5406bfd005a.png)](https://p2.ssl.qhimg.com/t0125e1a5406bfd005a.png)

通常来说，我们会希望完全删除或替换无用的事件轮询代码，因为它不会增加我们的覆盖范围，只会带来不必要的复杂性。在下面的示例中，我们为此注释掉了一个无用的select(2)调用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01242df22d84a9f775.png)

我们还必须考虑到数据通道和命令通道之间的并发事件交织的任何情况。CVE-2020-9273就是发生这种情况的一个很好的例子。这个漏洞是通过向命令通道发送特定的命令序列而触发的，同时数据传输也在进行。为了应对这种情况，我编写了一个fuzzer函数：fuzzer_5tc2函数，其作用是将提供给它的字典中的字符串送入fuzzer。 

[![](https://p3.ssl.qhimg.com/t010efce3072ee0edf5.png)](https://p3.ssl.qhimg.com/t010efce3072ee0edf5.png)



## 再见了，fork函数

大多数Linux网络服务器软件都采用多进程架构。其中，父服务器进程监听客户端连接，并为每个连接派生一个子进程。这种机制也为有特权的父进程与其子进程之间的特权分离提供了机会，因为子进程可以在不影响父进程的情况下放弃特权。

然而，AFL无法处理多进程应用，因为它只会检测父进程生成的信号。出于这个原因，我们需要将多进程应用程序转化为单进程应用程序。这意味着，我们必须禁用任何fork(2)调用。

在某些情况下，软件本身已经提供了这种功能。例如，下面是ProFTPd中的nofork选项：

nofork选项可以防止proftpd使用fork(2)系统调用，从而把proftpd变成一个单进程服务器。

$ ./configure –enable-devel=coredump:nodaemon:nofork:profile:stacktrace …

在没有这些选项的情况下，为了避免fork(2)，我们只需删除实际的fork(2)调用，并硬编码返回值0，代码就会沿着预期的子进程执行路径继续执行：

[![](https://p1.ssl.qhimg.com/t015f3cad8ad705885e.png)](https://p1.ssl.qhimg.com/t015f3cad8ad705885e.png)



## 小结

在本文中，我们为读者介绍了在基于套接字的模糊测试过程中，修改源代码中与套接字、文件系统调用、事件处理以及fork函数相关的代码的各种技巧，在下一篇文章中，我们将继续为读者介绍更多的精彩内容。
