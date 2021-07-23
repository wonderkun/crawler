> 原文链接: https://www.anquanke.com//post/id/86939 


# 【漏洞预警】Linux PIE/stack 内存破坏漏洞(CVE–2017–1000253)预警


                                阅读量   
                                **153999**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01e1da99e79b74498c.png)](https://p0.ssl.qhimg.com/t01e1da99e79b74498c.png)



**0x00 事件描述**



2015年4月14日，Michael Davidson发现 **PIE（Position Independent Executable）**机制允许将一部分应用程序的数据段放置在超过预留的内存区域，可能会造成内存越界，进而导致提权，并在Linux Source Tree上提交了补丁a87938b2e246b81b4fb713edb371a9fa3c5c3c86。

同年5月， Linux 3.10.77版本更新了该补丁，但是并没有对该问题的重要性作出准确的评估，故许多发行版很长一段时间里没有更新该补丁，导致漏洞一直存在。

2017年9月26日，OSS-SEC邮件组中发布了与该漏洞相关的信息，并表示该漏洞编号为**CVE-2017-1000253**。同时，相关受影响的Linux发行版也发布了该漏洞相关的更新补丁。

经过360CERT评估，该漏洞可利用风险等级高，可用于Linux操作系统恶意本地提权root，建议受影响用户尽快完成相应更新。



**0x01 事件影响面**



**影响等级**

**漏洞风险等级高，影响范围广。**

**影响版本**

2017年09月13日前发行的 CentOS 7 全版本（版本1708前）

2017年08月01日前发行的 Red Hat Enterprise Linux 7 全版本（版本7.4前）

所有版本的CentOS 6 和 Red Hat Enterprise Linux 6

**修复版本**

Kernel 3.10.0-693 以及之后的版本

**具体的发行版：**

Debian wheezy 3.2.71-1

Debian jessie 3.16.7-ckt11-1

Debian (unstable) 4.0.2-1

SUSE Linux Enterprise Desktop 12 SP2

SUSE Linux Enterprise Desktop 12 SP3

SUSE Linux Enterprise Server 12 GA

SUSE Linux Enterprise Server 12 SP1

SUSE Linux Enterprise Server 12 SP2

SUSE Linux Enterprise Server 12 SP3

Red Hat Enterprise MRG 2 3.10.0-693.2.1.rt56.585.el6rt

Red Hat Enteprise Linux for Realtime 3.10.0-693.rt56.617



**0x02 漏洞信息**



Linux环境下，如果应用程序编译时有“**-pie**”编译选项，则**load_elf_binary()**将会为其分配一段内存空间，但是**load_elf_ binary()**并不考虑为整个应用程序分配足够的空间，导致**PT_LOAD**段超过了**mm-&gt;mmap_base**。在x86_64下，如果越界超过128MB，则会覆盖到程序的栈，进而可能导致权限提升。 官方提供的内存越界的结果图：

[![](https://p3.ssl.qhimg.com/t01a22042a50239fd84.jpg)](https://p3.ssl.qhimg.com/t01a22042a50239fd84.jpg)

官方补丁提供的方法是计算并提供应用程序所需要的空间大小，来防止内存越界。



**0x03 修复方案**



强烈建议所有受影响用户，及时进行安全更新，可选方式如下：

相关Linux发行版已经提供了安全更新，请通过 **yum** 或 **apt-get **的形式进行安全更新。

自定义内核的用户，请自行下载对应源码补丁进行安全更新。

补丁地址：[https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a87938b2e246b81b4fb713edb371a9fa3c5c3c86](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a87938b2e246b81b4fb713edb371a9fa3c5c3c86)



**0x04 时间线**



**2015-04-14** Michael Davidson提交漏洞补丁，并被接受

**2017-09-26 **OSS-SEC邮件组公布漏洞信息

**2017-09-27** 360CERT发布预警通告



**0x05 参考资料**



[https://www.qualys.com/2017/09/26/cve-2017-1000253/cve-2017-1000253.txt](https://www.qualys.com/2017/09/26/cve-2017-1000253/cve-2017-1000253.txt)

[https://access.redhat.com/security/vulnerabilities/3189592](https://access.redhat.com/security/vulnerabilities/3189592)

[https://security-tracker.debian.org/tracker/CVE-2017-1000253](https://security-tracker.debian.org/tracker/CVE-2017-1000253)

[https://www.suse.com/security/cve/CVE-2017-1000253/](https://www.suse.com/security/cve/CVE-2017-1000253/)

[https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a87938b2e246b81b4fb713edb371a9fa3c5c3c86](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a87938b2e246b81b4fb713edb371a9fa3c5c3c86)
