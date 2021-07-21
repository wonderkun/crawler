> 原文链接: https://www.anquanke.com//post/id/150881 


# RAMpage攻击：再次利用安卓RowHammer漏洞


                                阅读量   
                                **119039**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：thehackernews.com
                                <br>原文地址：[https://thehackernews.com/2018/06/android-rowhammer-rampage-hack.html](https://thehackernews.com/2018/06/android-rowhammer-rampage-hack.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01e3fb7f3d9e867d56.png)](https://p4.ssl.qhimg.com/t01e3fb7f3d9e867d56.png)

研究人员发现了一种新的攻击技术，黑客利用这种技术可以绕过当前基于DMA的Rowhammer攻击的补丁。RAMpage即CVE-2018-9442可以使没有权限的安卓APP利用之前泄漏的Drameer攻击获取root权限。Drameer攻击是针对安卓设备DRAM Rowhammer硬件漏洞的攻击变种。



## DRAM RowHammer漏洞

自2012年起，Rowhammer漏洞是新一代DRAM（dynamic random access memory，动态随机存取存储器）芯片的硬件可靠性问题，当快速、重复访问一行内存时会造成邻接行的位（比特）翻转，比如比特值从1变成0或从0变成1。

2015年，Google Project Zero的安全研究人员成功证明了利用该硬件漏洞在有漏洞的Windows和Linux主机上进行权限提升的方法。谷歌的研究人员还介绍了一种双侧Rowhammer攻击，这种攻击可以增加两侧位翻转到概率。

触发Rowhammer漏洞非常简单，但成功地利用该漏洞有点难，因为内存中大多数的位是与攻击者无关的，而这些无关位的翻转可能会导致内存破坏。在DRAM中随机的位置上读取或写入数据是不足以导致目标内存页位翻转的。[![](https://p5.ssl.qhimg.com/t01d81d3685b7ce5ea8.png)](https://p5.ssl.qhimg.com/t01d81d3685b7ce5ea8.png)

想要成功地利用Rowhammer，攻击者必须能够诱使系统加载目标内存页到DRAM中与攻击者所有的物理内存行邻接的行中。

目前已有的Rowhammer攻击有GLitch、Throwhammer、Nethammer等。
1. Glitch：该技术使用嵌入的GPU来实施针对安卓设备的Rowhammer攻击。
1. Throwhammer：利用已知的DRAM漏洞利用使用远程直接内存访问（remote direct memory access，RDMA）信道通过网卡发起攻击，这是第一个基于网络的远程Rowhammer攻击方式。
1. Nethammer：也是一个基于网络的远程Rowhammer攻击方法。在处理网络请求时通过未缓存的内存或flush指令来攻击系统。


## Drammer攻击

Drammer攻击是2年前发现的第一个安卓设备上针对DRAM芯片的现实Rowhammer攻击的例子。任意的恶意APP不需要任何权限和软件漏洞就可以利用Drammer攻击。

[![](https://p4.ssl.qhimg.com/t015e8e13eb8eb6ad26.png)](https://p4.ssl.qhimg.com/t015e8e13eb8eb6ad26.png)

Drammer攻击依赖DMA（direct memory access）缓存，这是由安卓主内存管理器ION提供的。因为DMA允许APP在不经过任何CPU缓存的情况下访问内存，因此可以高效地、重复地访问内存中的特定行。

ION在许多的内核内堆上组织内存池，其中kmalloc heap是用来分配物理上连续的内存的，这让攻击者可以轻易地知道虚拟内存与真实的物理内存是如何映射的。<br>
ION内存管理器的直接访问和连续内存分配这两个特征是Drammer攻击成功的关键。

### <a class="reference-link" name="Google%E5%AF%B9%E5%9F%BA%E4%BA%8ERowhammer%E6%94%BB%E5%87%BB%E7%9A%84%E7%BC%93%E8%A7%A3%E6%8E%AA%E6%96%BD"></a>Google对基于Rowhammer攻击的缓解措施

2016年，在Drammer攻击的细节公开后，Google发布了针对安卓设备的更新，在更新中关闭了负责连续内存分配的ION组件（kmalloc heap）来缓解Rowhammer漏洞带来的风险。<br>
在关闭了连续堆后，运行在安卓设备上的APP和应用进程依靠ION内存管理器的另一个内核内堆——system heap，这是用来在DRAM中随机的物理位置上进行内存分配。<br>
除了非连续的内存分配外，系统堆还会通过分配到lowmem和highmem zone的方式将内核内存和用户内存分割开，这也是为了保证安全的考虑。



## RAMpage攻击和Rowhammer补丁绕过

Google研究人员提出的缓解技术可以有效地防止攻击者执行双边Rowhammer攻击。

但有一个安全团队称发现了4种rowhammer攻击的变种可以让安装在目标设备上的恶意应用获取root权限，并绕过当前缓解措施从其他的APP中窃取隐私信息。

在论文中，研究人员称第一个RAMpage variant (r0)变种是可靠的Drammer实施，表明关闭持续内存分配并不能预防基于Rowhammer的权限提升攻击。

按照下面的三个步骤就可以用RAMpage r0变种完成类Drammer利用：
<li>耗尽系统堆。研究人员发现如果应用故意耗尽了ION的内部池，另一个内存分配算法buddy allocator就会负责分配进程。因为buddy allocator的主要目的就是减小内存分片，最终会提供连续的页分配。<br>
为了增加这种利用的可能性，攻击者还绕过了system heap使用的zone隔离机制。为了强制加载内存页到kernel所在的lowmem分配，攻击者持续分配内存直至没有剩余的highmem。一旦这样，kernel就会服务于随后来自lowmem的请求，允许攻击者找出物理内存中的位翻转。</li>
1. 减小缓存池。通过使用Flip Feng Shui利用向量，攻击者可以诱使kernel在有漏洞的页面存储页表。这一步是为了将system heap池的物理内存释放会kernel，这间接地会使ION子系统释放预先分配的缓存的内存，包括有漏洞的页中的行。
1. Root手机。实施以上两步骤后，诱使操作系统加载与攻击者所有页非常邻近的目标内存页，然后攻击者实施基于DMA的rowhammer攻击的步骤找出可利用的chunk，开发root利用。
研究人员在运行最新安卓版本（7.1.1）的LG G4手机上进行了POC验证。<br>
如果系统受影响，POC利用可以完全控制设备并访问设备上的所有文件，包括系统上保存的密码和敏感数据。

其他三个变种允许攻击者绕过保护系统内存的特定部分的防护措施，更加偏理论，实践价值不高。这三个变种分别是：
1. ION-to-ION (Varint r1)
1. CMA-to-CMA attack (Varint r2)
1. CMA-to-system attack (Varint r3)


## GuardION：缓解措施

在论文中，研究人员讨论了目前的缓解技术在防御RAMpage变种上的有效性，并引入了新的解决方案——GuardION。[![](https://p1.ssl.qhimg.com/t016837de981830f82a.png)](https://p1.ssl.qhimg.com/t016837de981830f82a.png)

GuardION是基于软件的防御措施，可以用guard row隔离DMA缓存达到防御rowhammer攻击的方式。

GuardION代码需要以补丁的形式安装在Android操作系统中，补丁会以注入空row（guard）的方式来隔离敏感缓存，使敏感内存区物理上与恶意row隔开。

GuardION提供的隔离技术使攻击者不能使用未缓存的DMA分配来翻转kernel或用户区APP使用的内存中的位。GuardION可以保护所有已知的Rowhammer攻击向量，目前没有相关技术可以绕过。但安装GuardION会对设备的性能产生一些影响。



## 影响

所有2012年以后的安卓设备都受到rampage攻击的影响。而且无法检测是否利用了rampage攻击，因为利用不会在传统的日志文件中留下任何踪迹。

研究人员称，如果只从可信源下载APP，应该就不用担心会受到RAMpage攻击了。

论文地址：[https://vvdveen.com/publications/dimva2018.pdf](https://vvdveen.com/publications/dimva2018.pdf)

审核人：yiwang   编辑：边边
