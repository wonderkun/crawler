> 原文链接: https://www.anquanke.com//post/id/164558 


# 通过一道pwn题探究_IO_FILE结构攻击利用


                                阅读量   
                                **277085**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_653_/t01375513390a339682.jpg)](https://p3.ssl.qhimg.com/dm/1024_653_/t01375513390a339682.jpg)



## 前言

前一段时间学了IO-file的知识，发现在CTF中IO_file也是一个常考的知识点，这里我就来总结一下IO_file的知识点，顺便可以做一波笔记。首先讲一下IO_file的结构体，然后其利用的方法，最后通过一道HITB-XCTF 2018 GSEC once的题目来加深对IO_file的理解。



## libc2.23 版本的IO_file利用

这是一种控制流劫持技术，攻击者可以利用程序中的漏洞覆盖file指针指向能够控制的区域，从而改写结构体中重要的数据，或者覆盖vtable来控制程序执行流。

### <a name="IO_file%E7%BB%93%E6%9E%84%E4%BD%93"></a>IO_file结构体

在ctf中调用setvbuf()，stdin、stdout、stderr结构体一般位于libc数据段，其他大多数的FILE 结构体保存在堆上，其定义如下代码：

FILE结构体会通过struct _IO_FILE *_chain链接成一个链表，64位程序下其偏移为0x60，链表头部用_IO_list_all指针表示。如下图所示

[![](https://p5.ssl.qhimg.com/t0178bac12173a5daf7.png)](https://p5.ssl.qhimg.com/t0178bac12173a5daf7.png)

IO_file结构体外面还被一个IO_FILE_plus结构体包裹着，其定义如下

其中包含了一个重要的虚表*vtable，它是IO_jump_t 类型的指针,偏移是0xd8，保存了一些重要的函数指针，我们一般就是改这里的指针来控制程序执行流。其定义如下

### <a name="%E5%88%A9%E7%94%A8%E6%96%B9%E6%B3%95%EF%BC%88FSOP%EF%BC%89"></a>利用方法（FSOP）

这是利用程序中的漏洞（如unsorted bin attack）来覆盖_IO_list_all(全局变量)来使链表指向一个我们能够控制的区域，从而改写虚表*vtable。通过调用 _IO_flush_all_lockp()函数来触发,，该函数会在下面三种情况下被调用：

1：当 libc 执行 abort 流程时。

2：当执行 exit 函数时。当执行流从 main 函数返回时

3：当执行流从 main 函数返回时

当 glibc 检测到内存错误时，会依次调用这样的函数路径：malloc_printerr -&gt;

libc_message-&gt;__GI_abort -&gt; _IO_flush_all_lockp -&gt; _IO_OVERFLOW

要让正常控制执行流，还需要伪造一些数据，我们看下代码

这时我们伪造 fp-&gt;_mode = 0， fp-&gt;_IO_write_ptr &gt; fp-&gt;_IO_write_base就可以通过验证



## 新版本下的利用

新版本（libc2.24以上）的防御机制会检查vtable的合法性，不能再像之前那样改vatable为堆地址，但是_IO_str_jumps是一个符合条件的 vtable，改 vtable为 _IO_str_jumps即可绕过检查。其定义如下

其中 IO_str_overflow 函数会调用 FILE+0xe0处的地址。这时只要我们将虚表覆盖为 IO_str_jumps将偏移0xe0处设置为one_gadget即可。

还有一种就是利用io_finish函数，同上面的类似， io_finish会以 IO_buf_base处的值为参数跳转至 FILE+0xe8处的地址。执行 fclose（ fp）时会调用此函数，但是大多数情况下可能不会有 fclose（fp），这时我们还是可以利用异常来调用 io_finish，异常时调用 IO_OVERFLOW

是根据IO_str_overflow在虚表中的偏移找到的， 我们可以设置vtable为IO_str_jumps-0x8异常时会调用io_finish函数。



## 具体题目（HITB-XCTF 2018 GSEC once）

### <a name="1%E3%80%81%E5%85%88%E7%AE%80%E5%8D%95%E8%BF%90%E8%A1%8C%E4%B8%80%E4%B8%8B%E7%A8%8B%E5%BA%8F%EF%BC%8C%E6%9F%A5%E7%9C%8B%E4%BF%9D%E6%8A%A4"></a>1、先简单运行一下程序，查看保护

主要开启了CANARY和NX保护，不能改写GOT表

[![](https://p0.ssl.qhimg.com/t013cb9eedf667c88e2.png)](https://p0.ssl.qhimg.com/t013cb9eedf667c88e2.png)

[![](https://p3.ssl.qhimg.com/t013ed3bb61b468382f.png)](https://p3.ssl.qhimg.com/t013ed3bb61b468382f.png)

### <a name="2%E3%80%81ida%E6%89%93%E5%BC%80%EF%BC%8C%E5%8F%8D%E7%BC%96%E8%AF%91"></a>2、ida打开，反编译

这里当输入一个不合法的选项时，就会输出puts的地址，用于泄露libc的基地址。

[![](https://p1.ssl.qhimg.com/t01a228a6e7c49fbc04.png)](https://p1.ssl.qhimg.com/t01a228a6e7c49fbc04.png)

第一个函数是创建一个chunk保存数据

[![](https://p2.ssl.qhimg.com/t017d69532000f5751d.png)](https://p2.ssl.qhimg.com/t017d69532000f5751d.png)

[![](https://p1.ssl.qhimg.com/t01f9a8ad6e30ec487a.png)](https://p1.ssl.qhimg.com/t01f9a8ad6e30ec487a.png)

第二个函数和第三个函数只能执行一次，有个任意地址写漏洞，这时我们可以利用第二个函数改写off_202038+3d为_IO_list_all-0x10，然后分别执行第三和第一个函数，最后_IO_list_all就会指向0x555555757040的位置

[![](https://p0.ssl.qhimg.com/t01780b64dccb76ecba.png)](https://p0.ssl.qhimg.com/t01780b64dccb76ecba.png)

[![](https://p0.ssl.qhimg.com/t0136320d614a0955c8.png)](https://p0.ssl.qhimg.com/t0136320d614a0955c8.png)

第四个函数主要是对堆块的操作，我们可以利用利用这个函数伪造一个_IO_FILE结构

[![](https://p2.ssl.qhimg.com/t01a84722a85dd7e615.png)](https://p2.ssl.qhimg.com/t01a84722a85dd7e615.png)

### <a name="3%E3%80%81%E5%85%B7%E4%BD%93%E8%BF%87%E7%A8%8B"></a>3、具体过程

1、泄露libc，输入一个“6”即可得到puts函数的地址，然后酸算出libc基地址

2、利用任意地址写改写_IO_list_all为堆的地址

[![](https://p1.ssl.qhimg.com/t01529a0a870e8cb0ea.png)](https://p1.ssl.qhimg.com/t01529a0a870e8cb0ea.png)

3、这时只要我们再利用第四个函数伪造__IO_FILE结构体，改写vtable为_IO_str_jumps，file+0xe0设置

为one_gadget

[![](https://p2.ssl.qhimg.com/t01e67fbcf093b58b10.png)](https://p2.ssl.qhimg.com/t01e67fbcf093b58b10.png)

4、输入“5”，执行exit()函数触发one_gadget

[![](https://p1.ssl.qhimg.com/t01cb28656665d64071.png)](https://p1.ssl.qhimg.com/t01cb28656665d64071.png)



## 小结

这个是我个人总结出来的IO_file结构的一些知识点，写得还不够全，如有写得不对的地方，欢迎大牛指正。



## 完整EXP
