> 原文链接: https://www.anquanke.com//post/id/208568 


# Linux容器安全：通过`/proc/pid/root`目录来实现权限提升


                                阅读量   
                                **189552**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者labs.f-secure，文章来源：labs.f-secure.com
                                <br>原文地址：[https://labs.f-secure.com/blog/abusing-the-access-to-mount-namespaces-through-procpidroot/](https://labs.f-secure.com/blog/abusing-the-access-to-mount-namespaces-through-procpidroot/)

译文仅供参考，具体内容表达以及含义原文为准

![](https://p3.ssl.qhimg.com/t01b8b3dea71f47ade1.png)



## 前言

容器是指一个与主机系统相隔离的工作区域，本质是一种特殊的进程。在Linux操作系统中运行相关容器时（例如Docker与LXC），会使用到多个Linux命名空间来隔离资源以实现虚拟化。基于这个前提，有关容器和命名空间的安全研究大部分都集中在`容器逃逸`这一层面。但是在某些特定场景下，攻击者能够通过滥用容器和Linux命名空间在目标主机上实现权限提升。这篇文章中我们展示了在处于`容器ROOT用户+主机非ROOT权限`场景下时，如何借用默认权限且不带有`--privileged`参数运行的Docker容器在主机层面来实现权限提升。此外，我们还将分享一些关于`symlink(符号链接)`在命名空间场景下的利用方法。



## 什么是名称空间（namespaces）？

截至目前，Linux内核公开了7个命名空间。它们可用来隔离主机与容器两者的相关资源以实现虚拟化。简要描述如下：

<tr class="md-end-block md-focus-container" style="box-sizing: border-box; break-inside: avoid; break-after: auto; border-top: 1px solid #dfe2e5; margin: 0px; padding: 0px;"><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; font-weight: bold; border-top-style: solid; border-right-style: solid; border-left-style: solid; border-top-color: #dfe2e5; border-right-color: #dfe2e5; border-left-color: #dfe2e5; text-align: left; margin: 0px;">命名空间</th><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; font-weight: bold; border-top-style: solid; border-right-style: solid; border-left-style: solid; border-top-color: #dfe2e5; border-right-color: #dfe2e5; border-left-color: #dfe2e5; text-align: left; margin: 0px;">作用介绍</th></tr>|------

在这里我们主要讨论 `Mount namespace`与`User namespace`，前者允许一组进程拥有它们独自的系统文件视图；而后者则允许进程用户临时提升到root权限来完成某些操作，只要这些操作仅影响到各自的命名空间即可。

`Mount namespace`可通过`/proc/pid/root`目录或`/proc/pid/cwd`目录来访问。这些目录可使`Mount namespace`和`PID namespace`中的父进程临时查看另一个进程中`Mount namespace`内的文件。这种访问方式比较神奇不过有一些限制，例如，即使通过`nodev`参数挂载了 `/proc`目录，设置用户位操作无法执行但当前`设备文件`仍然可用。



## 通过Docker容器进行提权

让我们确定一个前提：nodev参数并没有使用。

在这个前提下，我们假设有一个攻击者已拿到某个Docker容器的root权限，而在该Docker容器对应的主机上拥有一个非root权限的shell。Docker容器不使用`User namespace`。容器内的root用户对于容器外具有root访问权限。但是Docker会从容器内的root用户中删除一堆功能，以确保它们不会影响容器之外的任何数据。

默认情况下，Docker容器举有以下功能：

`cap_chown、cap_dac_override、cap_fowner、cap_fsetid、cap_kill、cap_setgid、cap_setuid、cap_setpcap`<br>`cap_net_bind_service、cap_net_raw、cap_sys_chroot、cap_mknod、cap_audit_write、cap_setfcap + eip`

这些功能大多数都很难被滥用，例如，虽然`cap_kill`允许容器内的root用户终止它可以查询到的所有进程，但是它受`PID namespace`限制，所以实际上仅允许杀死容器中的进程。但是，由于容器具有`cap_mknod`能力，因此允许容器内的root用户创建`块设备文件`。`设备文件`是用于访问`基础硬件`和`内核模块`的特殊文件。例如，`/dev/sda`设备文件提供系统磁盘上原始数据的读取权限。

Docker通过在容器中设置禁止读写块设备的Cgroup策略，确保不会从容器内部滥用块设备文件。

但是，如果在容器内创建了块设备文件，则容器外部的用户可以通过`/proc/pid/root/`目录访问该块设备文件，有一个限制就是该进程必须属于容器内外的同一用户。

下面的截图展示了一个攻击示例。左图是攻击者控制的举有root用户的容器，右图是攻击者控制的非root权限的shell。

![](https://p1.ssl.qhimg.com/t019a59cdeee7a0f6bc.png)

在右图中，我们读取`/etc/shadow`中的root账户用户密码来证实当前对系统拥有完全的访问权限。解决方案是可以通过禁用容器中的root用户或者通过`--cap-drop=MKNOD`参数启动Docker容器来防止这种攻击。



## 扩大symlink（符号链接）漏洞危害

`/proc/pid/root`目录在`Mount Namespace`下的另一种利用思路是它可用来配合符号链接漏洞，为了更好的说明此问题的严重性，我们首先描述`User namespace`与`Mount namespace`之间的关系。

`User namespace`的作用是将其内部的UID映射到其它`User namespace`中。在进程创建命名空间时就决定了这一映射关系。`User namespace`的常见用法是将容器内部的`UID 0`映射到容器外部的普通用户。这种映射方式比较神奇，因为容器中`User namespace`中的操作`UID 0`实际上是root，但是在该容器之外的`UID 0`是常规用户。将`User namespace`与`Mount namespace`结合使用的一个神奇之处就在于它允许普通用户通过绑定挂载的方式实现对`Mount namespace`中的文件系统进行控制。例如这一场景，进程想在其命名空间中更改其系统用户名，但它们对`/etc/passwd`文件没有写权限，因为这样做需要容器之外的root权限。但是，它们可以使用挂载目录的方式将任意文件和目录链接到`/etc`路径。

回到主题，在常规操作下，可以通过`apt remove 包名`的方式来删除Debian系统中的软件包，有一些软件包在删除时需要进行额外的清理操作，假设某个软件包被以root权限来执行命令`rm –rf /home/*/.config/programX`以清除相关用户配置文件。此种场景存在一个明显的`符号链接漏洞`，用户可以将其`.config`目录通过符号链接到任何指定目录，从而删除文件系统上任何名为`programX`的文件或者文件夹。尽管这是一个漏洞场景，但是删除名为`programX`的文件或文件夹不太可能造成太大的危害，尤其是在卸载程序时。

请注意，无法创建从`/home/user/.config/programX`路径到例如`/etc/password`路径的符号链接，因为在这种情况下`rm`仅会删除符号链接本身。与`.config`符号链接时的结果不同是因为`programX`位于上述路径的末尾。

使用`User + Mount namespace`，我们可以在`.config`目录上使用符号链接将脚本欺骗到我们自己的`Mount namespace`中。在这之中，我们可以控制文件系统，例如可以创建从`programX`目录到`/etc/`目录的挂载。这种目录挂载方式不是符号链接因此`rm`命令很显然能操作此目录。

下面的截图展示了上述的攻击理论。左图是具有root用户特权的模拟卸载脚本，右图是非root权限主机上的攻击者。首行的`unshare –r –m`命令来创建 `User namespace + Mount namespace`并进入对应的容器。

![](https://p0.ssl.qhimg.com/t01e8000fb312938adb.png)

在左图执行模拟卸载脚本运行之前，右图中需要执行完毕第一个`ls`命令之前的所有命令，此外，模拟卸载脚本执行时，进程和名称空间必须在同一主机上运行。<br>
由于此方法可以用来扩大符号链接漏洞的影响范围，因此建议的解决此问题的方法是修复符号链接漏洞。可以添加一些缓解措施，例如，可以通过其自己的`PID namespace`运行`rm -rf`命令，从而通过`/proc/pid/root`隐藏对`Mount namespace`的访问。



## 总结

在相关研究公布之前一些容器技术就已经被投入使用。因此，开发人员很难完整掌握在容器内提供root权限的安全隐患以及特定功能增加时对安全隐患的影响。<br>
希望这篇文章能够抛砖引玉，对在不建议在Docker容器中提供root权限以及命名空间如何影响现有漏洞等场景提供一些思路。
