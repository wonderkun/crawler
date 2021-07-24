> 原文链接: https://www.anquanke.com//post/id/107583 


# “360代码卫士” 帮助 Linux 内核发现多个安全漏洞（附技术分析）


                                阅读量   
                                **93135**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/dm/1024_536_/t01e96bd480ba50b900.jpg)](https://p0.ssl.qhimg.com/dm/1024_536_/t01e96bd480ba50b900.jpg)

**日前，360代码卫士“开源项目检测计划”发现了多个Linux内核的安全漏洞（CVE-2018-7566、CVE-2018-9858、CVE-2018-9865）, 并在第一时间将漏洞信息提交给了Linux内核组织，协助其进行漏洞修复。**

> 360开源项目检测计划是360代码卫士团队负责运营的一个公益计划，该计划旨在帮助开源项目提升代码安全质量，并通过知识分享让广大开发者关注和了解软件源代码安全问题，提高软件安全开发意识和技能。
截止目前，360开源项目检测计划已检测各类开源项目2200多个，测试代码超过3亿行，协助各类开源项目修复了众多源代码安全缺陷和漏洞，其中帮助开源项目修复的漏洞已有40多个被CVE收录。

[![](https://p0.ssl.qhimg.com/t01eb51bef65c315c4c.png)](https://p0.ssl.qhimg.com/t01eb51bef65c315c4c.png)

Linux内核组织已经对编号为CVE-2018-7566的漏洞完成了修复，下面是对该漏洞的简要技术分析。

CVE-2018-7566是ALSA（Advanced Linux Sound Architecture，高级Linux声音架构）的音序器核心未能对事件池进行正确初始化所引入的一个高危竞争条件漏洞，该漏洞的CVSS评分为7.8。下面结合源代码对该漏洞进行更详细的分析。

> <h3 id="" style="margin: 0px 0px 1rem; padding: 0px; font-family: Menlo, Monaco, 'Source Code Pro', Consolas, Inconsolata, 'Ubuntu Mono', 'DejaVu Sans Mono', 'Courier New', 'Droid Sans Mono', 'Hiragino Sans GB', 微软雅黑, monospace !important; font-weight: normal; color: #159957; line-height: 1.35; font-size: 18px;">什么是竞争条件</h3>
由于两个或者多个进程竞争使用不能被同时访问的资源，使得这些进程有可能因为时间上推进的先后原因而出现问题，这叫做竞争条件（Race Condition）。

该漏洞的触发点位于 `/sound/core/seq/seq_clientmgr.c`文件的 `snd_seq_write`函数中。如下所示，在该函数的1021行中，当第一次写操作发生并且事件池为空时，会调用 `snd_seq_pool_init`函数对事件池进行初始化。

[![](https://p5.ssl.qhimg.com/t0191d12ad0f650c49a.png)](https://p5.ssl.qhimg.com/t0191d12ad0f650c49a.png)

但是，如果攻击者通过并发地调用 `ioctl()`函数，恶意地对事件池的长度进行修改，那么就可能进一步的造成越界访问或者释放后再使用的安全问题。

Linux内核项目组对该漏洞进行了修复：通过引入互斥锁的机制，将 `snd_seq_pool_init`函数的调用保护起来，从而避免了竞争条件的发生。具体修复如下所示：

[![](https://p0.ssl.qhimg.com/t0114d47171127a1a8f.png)](https://p0.ssl.qhimg.com/t0114d47171127a1a8f.png)

> <h3 id="-1" style="margin: 0px 0px 1rem; padding: 0px; font-family: Menlo, Monaco, 'Source Code Pro', Consolas, Inconsolata, 'Ubuntu Mono', 'DejaVu Sans Mono', 'Courier New', 'Droid Sans Mono', 'Hiragino Sans GB', 微软雅黑, monospace !important; font-weight: normal; color: #159957; line-height: 1.35; font-size: 18px;">什么是互斥锁</h3>
在计算机科学中，如果两个或多个进程彼此之间没有直接的联系，但是由于要抢占使用某个临界区（critical section，不能被多个进程同时使用的资源，如打印机、变量）而产生制约关系，那么这种关系被称之为互斥（mutex）。而互斥锁（Mutex Lock）则是用来实现这种制约关系的数据结构。

## 

## 关于360代码卫士

“360代码卫士”是360企业安全集团旗下专注于软件源代码安全的产品线，能力涵盖了源代码缺陷检测、源代码合规检测、源代码溯源检测三大方向，分别解决软件开发过程中的安全缺陷和漏洞问题、代码编写的合规性问题、开源代码安全管控问题。“360代码卫士”系列产品可支持Windows、Linux、Android、AppleiOS、IBM AIX等平台上的源代码安全分析，支持的编程语言涵盖C、C++、C#、Objective-C、Java、JSP、JavaScript、PHP、Python等。目前360代码卫士已应用于上百家大型机构，帮助用户构建自身的代码安全保障体系，消减软件代码安全隐患。

### **当当当~别走~福利来啦~**

360代码安全实验室正在寻找漏洞挖掘安全研究员，针对常见操作系统、应用软件、网络设备、智能联网设备等进行安全研究、漏洞挖掘。

> 360代码安全实验室是360代码卫士的研究团队，专门从事源代码、二进制漏洞挖掘和分析的研究团队，主要研究方向包括：Windows/Linux/MacOS 操作系统、应用软件、开源软件、网络设备、IoT设备等。团队成员既有二进制漏洞挖掘高手，微软全球TOP100贡献白帽子，Pwn2own 2017 冠军队员，又有开源软件安全大拿，人工智能安全专家。实验室安全团队的研究成果获得微软、Adobe、各种开源组织等的60多次致谢。

如果你：

> 对从事漏洞研究工作充满热情
熟悉操作系统原理，熟悉反汇编，逆向分析能力较强
了解常见编程语言，具有一定的代码阅读能力
熟悉Fuzzing技术及常见漏洞挖掘工具
挖掘过系统软件、网络设备等漏洞者（有cve编号）优先
具有漏洞挖掘工具开发经验者优先

那么，你将得到：

> 白花花的**银子**——月薪20K-60K+年底双薪+项目奖，优秀者还有股票期权哦
暖心的**福利**——六险一金+各种补贴+下午茶+节假日礼品
**重点重点重点**——志同道合、暖心的我们

心动不如行动！无论你是经验丰富的**大咖儿**，还是志向从事安全研究的**菜鸟儿**，不要犹豫！

赶紧投简历到 **liubenjin@360.net** 吧！我会在3个工作日内找到你~


