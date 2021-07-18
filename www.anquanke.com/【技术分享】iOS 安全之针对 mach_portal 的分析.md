
# 【技术分享】iOS 安全之针对 mach_portal 的分析


                                阅读量   
                                **155180**
                            
                        |
                        
                                                                                                                                    ![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85908/t0156d1e0acd61df92a.jpg)](./img/85908/t0156d1e0acd61df92a.jpg)**

****

作者：[shrek_wzw@360涅槃团队](http://bobao.360.cn/member/contribute?uid=1224214662)

预估稿费：800RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一.	背景**

Google Project Zero的Ian Beer在12月中旬放出了在iOS 10.*上获取root shell的利用代码，意大利的Luca在此基础上添加了KPP绕过，实现了iOS 10.*的越狱。本文将结合mach_portal的源码对其利用的三个漏洞进行分析，并对每一个步骤进行说明。

mach_portal利用的漏洞都源于XNU内核对Mach Port的处理不当，相信这也是mach_portal名称的由来。XNU内核提供了多种进程间通信（IPC）的方法，Mach IPC就是其中的一种。Mach IPC基于消息传递的机制来实现进程间通信，关于Mach IPC的消息传递在众多书籍和文章中都有介绍，在此就不再赘述。我们这里介绍Mach Port。

Mach消息是在端口（Port）之间进行传递。一个端口只能有一个接收者，而可以同时有多个发送者。向一个端口发送消息，实际上是将消息放在一个消息队列中，直到消息能被接收者处理。

内核中有两个重要的结构，ipc_entry和ipc_object。ipc_entry是一个进程用于指向一个特定ipc_object的条目，存在于各个进程的ipc entry table中，各个进程间相互独立。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c2c67d99c92cef80.png)

ipc_object就是ipc port或者ipc port set，实际上代表的就是一个消息队列或者一个内核对象（task，thread等等），Mach消息的传递就是通过ipc port的消息队列。ipc_object在内核中是全局的，一个ipc_object可以由不同进程间的ipc_entry同时引用。平常我们在编写代码时得到的Mach Port是一个32位无符号整型数，表示的是ipc_entry在ipc entry table中的索引值。经过MIG的转换后，在内核中，就可以从ipc_port得到实际的内核对象，例如convert_port_to_task等等。具体可以参考XNU源码和《Mac OS X Internals: A Systems Approach》，对于Mach IPC的相关数据结构有更为详细的说明。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012ad1bcc6ed61721a.png)

<br>

**二.	漏洞详情**

mach_portal利用了三个漏洞，CVE-2016-7637、CVE-2016-7644、CVE-2016-7661。下面将对这三个漏洞的进行分析。

**1.	CVE-2016-7637**

漏洞说明：内核对于ipc_entry的user reference处理不当，使得ipc_entry被释放后重用，导致特权port可能被替换成攻击者控制的port。（GPZ Issue 959）

漏洞分析：当一个进程接收到带有port的mach message时，函数调用的流程如下。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0173a2916a954a7314.png)

在ipc_right_copyout函数中，会将port right复制到当前task的ipc entry table中。ipc_entry的ie_bits的含义如下图。ie_bits的低16位为user reference，表示的当前ipc_entry的引用数量，最大值为0xFFFF。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01634fbffe86a97bc5.png)

当ipc_right_copyout处理 MACH_PORT_TYPE_SEND的port时，代码如下

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016f56645aa30462fa.png)

可以看到，user references的值不会超过MACH_PORT_UREFS_MAX-1 = 0xFFFE。考虑这样一种场景，当前进程收到一个ool ports descriptor消息，当这条ool ports descriptor消息因为不符合接收进程的标准而被销毁时，以mach_msg_server为例，会调用mach_msg_destroy释放消息中带有的所有port right，如图。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d5d0ce536d070e8d.png)

ool ports descriptor被销毁时，会调用mach_msg_destroy_port释放每一个port right，更下层的函数会调用ipc_right_dealloc减少port对应的ipc_entry的一个引用（urefs）。当urefs等于0时，这个ipc_entry就会被释放到free list中，表示当前entry已经处于空闲状态，可以被申请用于指向另一个ipc_object。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a8b7112ecb75e5c0.png)

如果消息中带有同一个port的0x10000个descriptor，那么在处理这个消息时就会使得当前这个port对应的ipc_entry的user reference到达上限0xFFFE。当被销毁时，这个ipc_entry就会被释放0x10000次，进而进入free list。然而，用户空间并不知道这个ipc_entry已经被释放，因为用户空间的进程保留的仅仅是一个32位的整型索引。当尝试用这个索引去访问ipc entry table对应位置的ipc entry时，就会出现问题。

攻击方式：利用这个漏洞，可以使高权限进程中的特权port的ipc_entry被释放，然后再利用我们拥有receive right的port重新占位（需要处理ipc_entry的generation number），使得原先发送到特权port的消息都会被发送到我们拥有receive right的port上，形成port消息的中间人攻击。

利用方法（macOS提权，Ian Beer提供的PoC的攻击流程）：

（1）攻击目标是com.apple.CoreServices.coreservicesd服务（mach_portal的目标不同），launchd拥有这个服务的send right。

（2）攻击者通过漏洞使得launchd拥有的send right被释放。

（3）然后再利用launchd注册大量的服务，期望这些服务的port的ipc_entry会重用之前被释放的send right。 

（4）这样，当任意进程通过bootstrap port尝试查找coreservicesd的服务端口时，launchd就会将攻击者拥有receive right的端口发送给它。

（5）攻击者的进程拥有coreservicesd的send right。可以通过中间人（MiTM）的方式，来监听任意进程与coreservicesd的通信。

（6）通过获取root进程的task port，来得到root shell。

**2.	CVE-2016-7644**

漏洞说明：在调用set_dp_control_port时，缺乏锁机制导致的竞争条件，可能造成ipc_entry指向被释放的ipc_port，形成UAF。（GPZ Issue 965）

漏洞分析：

set_dp_control_port源码如下

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01de2608b3c2e8e852.png)

在调用ipc_port_release_send释放port的send right的时候，没有加锁。两个线程通过竞争条件，可以释放掉一个port的两个reference，使得ipc_entry指向被释放的ipc port。

利用方法（mach_portal）：

(1)	set_dp_control_port的第一个参数是host_priv，需要通过root权限的task获取

(2)	攻击者分配一个拥有receive right的port，插入send right引用（ipc_entry）。

(3)	利用port descriptor消息将这个port发送给自己，使内核拥有一个这个port的send right引用。

(4)	调用set_dp_control_port将这个port设置为dynamic_pager_control_port，拥有一个send right。

(5)	利用mach_port_deallocate释放自己的send right。这时，这个port的包含两个send right计数：port descriptor和dynamic_pager_control_port。包含三个引用计数：ipc_entry，port descriptor和dynamic_pager_control_port。

(6)	利用两个线程触发set_dp_control_port的竞争条件漏洞，使得引用数减少2。这时，这个port的send right计数为0，引用计数为1。但是仍然有两个指针指向这个port：ipc_entry，port descriptor。

(7)	再销毁之前发送的port descriptor消息，释放最后一个引用，使ipc_port被释放。形成ipc_entry指向一个被释放的ipc_port，利用其它数据占位这个被释放的ipc_port，即形成UAF。 

**3.	CVE-2016-7661**

漏洞说明：powerd对于DEAD_NAME通知的处理存在缺陷，导致攻击者指定的port在powerd进程中被释放，形成拒绝服务或port替换。（GPZ Issue 976）

漏洞分析：漏洞的详细分析参照Ian Beer的漏洞报告。这里简单说明一下漏洞的成因。

powerd进程创建pmServerMachPort用于接收相关的服务消息，同时在这个port上允许接收DEAD_NAME的通知。当接收到一条msgid为MACH_NOTIFY_DEAD_NAME时，就会从消息中的not_port字段取出port的值，然后调用mach_port_deallocate进行销毁。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01046f641998895bfe.png)

之所以会造成漏洞，是因为这个DEAD_NAME通知的消息是简单消息（simple message）。简单消息的传递并不涉及底层ipc_port的引用计数的修改，这里的not_port仅仅是一个整型的数据，这就表示攻击者可以向mach_port_deallocate提供任意的port参数。如果这个port参数正好是powerd进程中合法的一个port，就会导致port的释放，例如当前进程的task port。一旦task port被异常释放掉，后续的一些以task port作为参数的函数调用极有可能失败。这时，若缺乏对失败函数的检查，就可能导致powerd进程崩溃。

攻击方法（mach_portal）：

(1)	powerd进程以root权限运行

(2)	mach_portal的目的是导致powerd进程崩溃，再其重新启动后向launchd注册服务时，通过port中间人攻击，窃取其task port来获取host priv port。

(3)	具体的攻击方式如分析中所述，向powerd进程的服务端口发送DEAD_NAME通知消息，以0x103作为not_port的数值（在大多数情况下，0x103是mach_task_self的返回值），这就会导致powerd进程调用mach_port_deallocate释放掉自身的task port。

(4)	在调用io_ps_copy_powersources_info时，powerd进程就会通过vm_allocate，以task port作为参数尝试分配内存。由于task port已经被释放，这时vm_allocate分配内存失败。

(5)	powerd缺少对于返回值的检测，就会访问一个非法的地址指针，导致powerd进程崩溃。

<br>

**三.	mach_portal源码文件**

mach_portal包含了在10.*的设备上获取root shell的代码。下面简单说明一下源码中比较重要的各个文件的作用。

**cdhash.c：**计算MachO文件的CodeDirectory SHA1 Hash

**disable_protections.c：**将mach_portal进程提权至root，绕过沙盒的限制

**drop_payload.c：**处理iosbinpack中的可执行文件，socket监听端口，生成shell

**jailbreak.c：**越狱流程入口

**kernel_memory_helpers.c：**获取kernel task port后，内核读写的接口封装

**kernel_sploit.c：**set_dp_control_port竞争条件的利用，用于获取kernel task port

**offset.c：**包含设备以及系统相关的偏移量的初始化

**patch_amfid.c：**利用amfid的exception port来绕过代码签名

**sandbox_escape.c：**利用ipc_entry urefs和powerd的漏洞，获得host priv port，进一步攻击内核

**unsandboxer.c：**利用bootstrap port在父子进程之间的继承，监听子进程和launchd的通信，获取子进程的pid，通过提权，使mach_portal的子进程也绕过沙盒

<br>

**四.	mach_portal攻击流程**

****

mach_portal实现越狱的过程可以分为两个部分。第一个部分是利用上文提到的三个漏洞组合，获取到kernel task port，能够实现内核任意读写。第二部分是对于一些保护机制的绕过，包括沙盒、代码签名等等，由于仅仅是纯数据的修改，并不涉及任何代码片段的patch，不会触发KPP。

**第一部分：**

1.	利用漏洞 1 — CVE-2016-7637 释放launchd拥有的iohideventsystem port，实现MiTM。

2.	利用漏洞 3 — CVE-2016-7661 触发powerd崩溃，使得powerd将其task port发送给我们，得到拥有root权限的task port。

3.	利用powerd的task port，获取host priv port，触发漏洞 2 — CVE-2016-7644，实现内核exploit。

4.	通过内核exploit获得kernel task port，实现内核地址空间的任意读写。

**第二部分：**

1.	得到内核空间的任意读写权限后，就能够实现对任意进程地址空间的任意读写（能够从proc list得到任意进程的task port）。

2.	利用内核读写将本进程（mach_portal）的credential设置成kernproc的credential，实现提权和沙盒的绕过。

3.	将containermanagerd的credential也设置成kernproc的credential。

4.	将kernel task port设置成host special port 4，便于其他工具通过host_get_special_port获取kernel task port。

5.	恢复第一部分中用于中间人攻击的launchd的iohideventsystem的port为原始的port，并再次触发powerd崩溃，修复powerd进程对于iohideventsystem的send right。

6.	利用amfid的task port，调用task_set_exception_ports，将amfid的exception port设置成我们拥有receive right的port，并修改amfid的导入表，将MISValidateSignatureAndCopyInfo的导入地址设置成非法的地址。这样，当进行代码签名验证的时候，就会触发异常并将异常信息发送到我们的端口。我们对异常信息进行处理，并自行计算MachO CodeDirectory的SHA1 Hash后将其写入amfid的地址空间，最后修复amfid中引起异常的线程的状态。成功绕过amfid的代码签名检查，可以执行任意未签名的MachO文件。

7.	为了能够监听端口，生成shell，需要子进程也拥有root权限、绕过沙盒。这里利用子进程创建时会从父进程继承bootstrap port的特点。首先调用task_set_special_port将自身的bootstrap port设置成新申请的fake bootstrap port，这时创建的所有子进程就会继承这个fake bootstrap port。父进程利用port中间人攻击的方法，监听子进程和launchd的通信，获取子进程的pid后，修改对应pid的内核proc结构的credential为kernproc的credential，实现子进程的提权和沙盒绕过。

8.	最后的部分，处理iosbinpack中的可执行文件的路径，设置权限。生成PATH环境变量的路径，创建socket绑定端口。在接收外部连接后，调用posixspawn运行bash，重定向标准输入、标准输出和标准错误至socket的fd，实现bind shell。这时，外部连接就能够通过nc连接对应的端口，以root的权限通过bash shell访问文件系统。

<br>

**五.	mach_portal部分利用细节**

下面将会详细说明其中内核利用部分一些比较重要的实现细节。盘古团队在1月5日的博客中也解释了这些细节（http://blog.pangu.io/mach-portal-details/），可以参考。结合mach_portal和XNU的源码，相信也能够有更好的理解。我这里只是抛砖引玉，阐述自己的理解。

**1.	ipc_entry索引复用**

触发CVE-2016-7637针对ipc_entry的漏洞时，涉及ipc_entry索引的复用。ipc_entry的索引就是用户空间观察到的mach port name，一个32位的整型。这个32位整型分为两部分，高24位（index）和低8位（generation number）。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fde5607cd0da15bd.png)

详情参见源码ipc_entry.c。当调用ipc_entry_alloc分配一个新的ipc_entry时，会从对应的ipc entry table的位置上取出ie_bits，在原来的generation number的基础上加上4。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e98ffb56971d5bf6.png)

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01044b88e039e95578.png)

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011b3ea7321dc09587.png)

同一个ipc_entry的name索引（高24位）始终不变。但generation number仅仅占用8位，因此这个ipc_entry被分配 256 / 4 = 64 次后，返回给用户空间的name就会相同，实现ipc_entry的复用。

mach_portal攻击launchd的代码见sandbox_escape.c。mach_portal攻击的是launchd进程拥有的com.apple.iohideventsystem的send right（mach port name）。操作launchd中的ipc_entry的分配和释放的代码见send_looper函数，调用一次send_looper函数，就会在launchd进程中申请一定数量的ipc_entry后再释放。

劫持流程如下：

①	mach_portal触发漏洞释放com.apple.iohideventsystem对应的ipc_entry后，这时ipc_entry位于free list的第一个。

②	调用send_looper向launchd发送0x100个port，就会首先占用目标ipc_entry，然后再从free list取出其他ipc_entry进行占用。

③	当这0x100个port被释放的时候，会按照在port descriptor消息中的顺序进行释放。我们的目标ipc_entry由于最先被释放，根据free list LIFO的特点，因此会位于free list第0x100左右的位置。（完成1次）

④	接下来的62次调用send_looper，发送0x200个port进行launchd进程的ipc_entry的分配和释放，可以保证目标ipc_entry在被释放后始终位于free list 0x100左右的位置。（完成62次）

⑤	最后我们向launchd注册大量app group的服务（由于iOS注册服务的限制，这里注册app group的服务），提供我们拥有receive right的port作为这些服务的port。经过3和4两个步骤后，已经完成了63次的分配和释放。当我们向launchd注册大量的服务时，相当于第64次进行ipc_entry的分配和释放，使得目标ipc_entry被成功复用，并且指向的是我们拥有receive right的port。

⑥	任意进程向launchd申请com.apple.iohideventsystem的port时，launchd就会将我们的port的发送给请求者进程。通过接收port上的消息，进行监听处理后，将其转发给真正的服务port，从而实现中间人攻击。

**2.	Port中间人攻击**

port消息的中间人攻击也是mach_portal的一个亮点。当我们劫持了launchd进程中的com.apple.iohideventsystem的对应的port后，任意进程向com.apple.iohideventsystem发送的消息都会经过我们拥有的port。

我们当前拥有com.apple.iohideventsystem的真实port，通过劫持port接收到的消息需要继续转发给真正的服务port，以维持系统的正常运行。攻击者的目的是从发送的消息中监听所有可能被发送出来的task port，并在这些task port上调用task_get_special_port函数，尝试获取host priv port，只要成功获取，目标（触发下一阶段的竞争条件漏洞需要host priv port）就以达到，见inspect_port函数。

具体实现见sandbox_escape.c的do_service_mitm函数。函数流程如下：

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014bc61602abdf4686.png)

**3.	跨zone的port UAF利用**

set_dp_control_port的竞争条件漏洞的利用代码位于kernel_sploit.c文件中，目标是获取kernel task port。总体流程如下：

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01877f8c41361dde15.png)

由于ipc_port位于独立的ipc.ports zone中，因此无法按照过往的heap spray的方式进行kalloc zone占位利用。

首先通过分配大量的port并使得其中0x20个middle port通过set_dp_control_port漏洞减少其引用数。这时，当前进程的ipc_entry状态如下（便于理解，port处于连续位置）：

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01482d3eb935775fd4.png)

一个port的引用数为1，但是被两个指针指向。释放ool ports descriptor后并触发mach zone gc后，内存状态如下：

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01566f2cee3d685277.png)

发送包含host priv port的ool ports descriptor消息。内核对于mach msg中MACH_MSG_OOL_PORTS_DESCRIPTOR的处理代码见ipc_kmsg_copyin_ool_ports_descriptor函数，内核会调用kalloc重新分配页面，这时被攻击者释放的pages就会被重新使用，并填充ool ports descriptor的消息。内核会将对应位置的mach port name转化成对应的内核对象指针，如下图代码所示。在mach_portal的利用中，这里的object就是host priv port的内核ipc_port。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0110ab34b11a03d505.png)

这时，内存的状态处于下图的类似状态（简图），在ool ports descriptor的特定位置设置host priv port name，其余port保持为0。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f40867a19bdceca8.png)

具体到每一个ipc_port块所对应的情况如下：

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0159744e334a8e29a0.png)

ip_context是ipc_port可以在用户空间访问的变量。用户空间可以通过调用mach_port_get_context得到，通过mach_port_set_context进行设置。

[![](./img/85908/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01185adc476d34e28d.png)

通过在悬垂的ipc_port指针上调用mach_port_get_context，就会将上图中绿色部分的host priv port的指针返回给用户空间，实现了内核信息泄露。

因为host priv port和kernel task port都是在系统启动阶段分配，并且时间临近，因此在host priv port的地址附近，可能存在kernel task port。mach_portal就根据这个特点进行猜测，将可能的地址数值通过mach_port_set_context，设置到悬垂的ipc_port指针指向的区域中，修改原有的ool ports message的对象指针。

最后，mach portal在用户空间接收这些被修改的ool ports message。与内核接收MACH_MSG_OOL_PORTS_DESCRIPTOR时的处理（port_name To object_ptr）相反，内核会将port地址转换成port name返回给用户空间（object_ptr To port_name）。如果这些猜测的地址中包含真正的kernel task port的地址，那么用户空间就会从ool ports message中得到其对应的port name。通过pid_for_task检查得到的task port的pid是否为0，即可判断是否成功获取了kernel task port。

<br>

**References**

1.XNU 3248.60.10 [https://opensource.apple.com/tarballs/xnu/xnu-3248.60.10.tar.gz](https://opensource.apple.com/tarballs/xnu/xnu-3248.60.10.tar.gz) 

2.	CVE-2016-7637 By Ian Beer [https://bugs.chromium.org/p/project-zero/issues/detail?id=959](https://bugs.chromium.org/p/project-zero/issues/detail?id=959) 

3.	CVE-2016-7644 By Ian Beer [https://bugs.chromium.org/p/project-zero/issues/detail?id=965](https://bugs.chromium.org/p/project-zero/issues/detail?id=965) 

4.	CVE-2016-7661 By Ian Beer [https://bugs.chromium.org/p/project-zero/issues/detail?id=976](https://bugs.chromium.org/p/project-zero/issues/detail?id=976) 

5.	Mac OS X Internals: A Systems Approach

6.	mach portal漏洞利用的一些细节 by Pangu [http://blog.pangu.io/mach-portal-details/](http://blog.pangu.io/mach-portal-details/) 
