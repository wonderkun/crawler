> 原文链接: https://www.anquanke.com//post/id/83055 


# WI-FI有毒 — 教你如何建立一个邪恶的网络接入点


                                阅读量   
                                **128985**
                            
                        |
                        
                                                                                    



**[![](https://p4.ssl.qhimg.com/t01760c304ecbeb2675.jpg)](https://p4.ssl.qhimg.com/t01760c304ecbeb2675.jpg)**

**        免责声明:本文旨在分享技术进行安全学习,禁止非法利用。**

        本文中我将完整的阐述如何通过建立一个非常邪恶的网络接入点来使得用户进行自动文件下载。整个过程中我将使用Kali NetHunter 2.0 来运行 Nexus 9,并使用TP-LINK TLWN722N (150Mbps 版本)作为我的二级网络接口。

<br>

工具(下载地址见文末):

**        Mana **– 恶意接入点工具包。它能够实现比Karma (Freebuf相关介绍:http://www.freebuf.com/articles/77055.html)攻击的更高级版本,相对而言最显著的变化就是Mana可以响应其他的AP广播,而不是像Karma这样只是探测设备,但其最终的目标仍然还是欺骗用户连接到自己设置的AP上。此外,它还有许多新奇的邪恶的AP欺骗技巧。

        (关于该工具的详细内容,建议可以看看Defcon 22 Talk 的内容,该工具就是在这里发布的。https://cyberarms.wordpress.com/2014/10/16/mana-tutorial-the-intelligent-rogue-wi-fi-router/)

**        BackdoorFactory BDFProxy**—— 被用于通过中间人攻击快速写入恶意payload。

**<br>**

**一个错误的开始**

        这里由于我也希望可以向受害者提供互联网接入,从而可以在他们下载时部署我的后门,所以我还需要 Nexus 9的另一个wifi接口。权衡之后,我选择了低功耗并且能与kali兼容的TP-LINK TLWN722N(支持数据包注入)。

        打开kali的NetHunter工具,以下是其导航目录:

[![](https://p0.ssl.qhimg.com/t0192e6c3274e35b960.jpg)](https://p0.ssl.qhimg.com/t0192e6c3274e35b960.jpg)

        Kali NetHunter 自带的Mana已经安装并准备好了,但是我并不能一键启动。

        这时我就想,我是不是做错了什么?

        而当我开始选择BDF选项时,甚至还出现了一个bdfproxy.cfg窗口。

[![](https://p5.ssl.qhimg.com/t01868b9011af9a92e5.jpg)](https://p5.ssl.qhimg.com/t01868b9011af9a92e5.jpg)



        即使是在我从eth0 切换到了 wlan1 并且反复检查了配置文件中的dhcpd 设置后,它仍不能正常运行,而且无法在日志中找到任何有关Mana 或者BDFProxy的记录。

        于是我只好跑去玩了会游戏—。—

**<br>**

**配置**

        接下来我进入了Mana的文件夹好好的摸索了一番:

[![](https://p5.ssl.qhimg.com/t01e4a6fe7c6789bf1e.jpg)](https://p5.ssl.qhimg.com/t01e4a6fe7c6789bf1e.jpg)

        啊哈,start-nat-simple-bdf-lollipop.sh 貌似有点戏,打开看看:

[![](https://p2.ssl.qhimg.com/t018b762087d17be291.jpg)](https://p2.ssl.qhimg.com/t018b762087d17be291.jpg)

        实际上,令人感到奇怪的是这文件的一切操作看起来都很简单。我永远都不知道在使用新工具的时候会发生什么事。这些操作是给设备分配一些变量,开启转发功能,启动一个接入点和DHCP,修改iptables的配置。

这里有提到一些配置文件,必须确保它们没有任何问题。

        第一个是 /etc/mana-toolkit/hostapd-karma.confg:

[![](https://p2.ssl.qhimg.com/t01a933460b3a883158.jpg)](https://p2.ssl.qhimg.com/t01a933460b3a883158.jpg)

        然后检查 /etc/mana-toolkit/dhcpd.conf:

[![](https://p4.ssl.qhimg.com/t011e5b9ba6419b4e98.jpg)](https://p4.ssl.qhimg.com/t011e5b9ba6419b4e98.jpg)

        看起来我们正在使用谷歌的DNS,并且客户端的ip设置在10.0.0.0/24范围内。

        继续检查在 /etc/bdfproxy/bdfproxy.cfg 下的BDFProxy配置文件(以下截图是配置文件中的主要部分):

[![](https://p1.ssl.qhimg.com/t014b2cc2d6610d96a8.jpg)](https://p1.ssl.qhimg.com/t014b2cc2d6610d96a8.jpg)

        看起来这里很有问题,这里配置的IP是反向Shells (192.168.1.168 和192.168.1.16) 需要连接的目的地址。根据dhcpd.conf (DNS配置)的设置,我们当前的设置是不正确的,我们应该在dhcpd.conf中指定路由器的IP, 使得所有的客户机指向10.0.0.1

        可以使用SED命令来进行更换:

        看下修改配置前后两个文件的差别:

[![](https://p1.ssl.qhimg.com/t01f8c9413b607716f8.jpg)](https://p1.ssl.qhimg.com/t01f8c9413b607716f8.jpg)

        可以看到所有的192.168.1.16都改成了10.0.0.1

**<br>**

**启动这台机器**

        现在是时候启用Mana了:

[![](https://p1.ssl.qhimg.com/t017c8e9dd9d2de5bc2.png)](https://p1.ssl.qhimg.com/t017c8e9dd9d2de5bc2.png)

        打开一个新的终端并启动BDFProxy:



[![](https://p3.ssl.qhimg.com/t011240cf5e23d91386.png)](https://p3.ssl.qhimg.com/t011240cf5e23d91386.png)

        BDFProxy开启后,它就会创建一个 Metasploit源文件。一开始该文源件存在的地方并不明显—— 不在/etc/bdfproxy/,而是在 /usr/share/bdfproxy/bdfproxy_msf_resource.rc

        该源文件将可以帮助我们处理反向Shells的链接,这时打开另一台终端,启动Metasploit工具:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01466f96907b998277.png)

        被Metasploit启动后,我们可以看到该源文件被加载了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011b97ae10b34b6943.jpg)

        这里我被卡了一下,虽然一切看起来都是正常的——Mana创建了一个AP,我可以连接并访问网络,通过Mana设置的 Iptables 可以正确的将我的流量从80端口转发到 BDFProxy正在监听的8080端口。但问题是BDFProxy是一个不透明的代理连接(mitmproxy下实际上是失败的),在我用笔记本电脑测试机连接到这个恶意AP时,我在所有的HTTP连接时都得到了这个错误:

        HttpError('Invalid HTTP request form (expected: absolute, got: relative)',)

        这时,我才发现我忘了修改bdfproxy.cfg的默认设置:

[![](https://p1.ssl.qhimg.com/t01d6c26c4d059f1b32.png)](https://p1.ssl.qhimg.com/t01d6c26c4d059f1b32.png)

        需要将其改为:



[![](https://p5.ssl.qhimg.com/t01f6929cdf2256a40f.png)](https://p5.ssl.qhimg.com/t01f6929cdf2256a40f.png)

        在此之后,bdfproxy.cfg将能够正常工作。我将我的笔记本连接到AP上,然后通过HTTP进行文件下载。我尝试下载了 Audacity、也测试下载了 Putty 和 PSFTP。

        在下载时,BDFProxy会hook这些下载请求,然后自动将恶意代码插入到这些下载的工具中。

[![](https://p4.ssl.qhimg.com/t01f220018c294aa049.jpg)](https://p4.ssl.qhimg.com/t01f220018c294aa049.jpg)

        对于可执行文件的格式,它不仅适用于Windows EXE/ PE的,而且在Linux ELF和Mach-O下也可以(这意味着你可以使用OS X!) ,Very cool stuff。

**<br>**

**BDF Proxy 是怎样进行工作的,做了什么?**

        在BDFProxy的配置文件/etc/bdfproxy/bdfproxy.cfg中你可以看到为了支持该可执行架构,其各个部分都包含了PATCH_TYPE和PATCH_METHOD:

[![](https://p3.ssl.qhimg.com/t0116d2224d64cdd912.png)](https://p3.ssl.qhimg.com/t0116d2224d64cdd912.png)

        在让被注入了恶意代码的工具运行时我遇到了一些问题。这里我建议所有遇到该问题的人可以进行apt-get更新以及通过使用不同的 PATCH_TYPE 和

        PATCH_METHOD 选项。

        而在对这些选项进行深入时,必须要理解 BDFProxy 是怎样将我们的shellcode 增加到二进制文件的。这里我们还要先了解什么是二进制文件中的代码空区,SecureIdeas blog(https://blog.secureideas.com/2015/05/patching-binaries-with-backdoor-factory.html)中利用BDF注入二进制文件的一篇文章对其进行了最简洁的解释:

**        代码空区是代码编译的产物。在某些时间中,代码编译器不得不通过填充一系列的0×00字节来填充某些区域。因此BDF 可以重写恶意代码到这些代码空区,并且因为是利用的已存在的空间,所以在你使用BDF时,不会发现文件的大小有变化。**

**<br>**

**补丁类型/修补方法**

        在BDFProxy中我们已经可以了解到PATCH _TYPEs 和 PATCH_METHODs的不同:



[![](https://p5.ssl.qhimg.com/t01542e992b6892e41d.png)](https://p5.ssl.qhimg.com/t01542e992b6892e41d.png)

**OnionDuke?**

        我没有用过onionduke攻击方法,也没有理由/欲望去对Tor出口节点进行投毒。这就是说,onionduke并不仅仅是被用于作为攻击向量。如果你的投毒目标有提防在下载文件时被做手脚,并且会对下载文件进行检查,这时使用onionduke攻击就会是一个不错的选择!

        更多关于onionduke攻击的说明,请看2015黑帽大会上,BDF/BDFProxy 工具的作者的ppt!(https://www.blackhat.com/docs/us-15/materials/us-15-Pitts-Repurposing-OnionDuke-A-Single-Case-Study-Around-Reusing-Nation-State-Malware-wp.pdf)

        关于oninonduke攻击,Freebuf之前有过相关的报道也可进行参考:http://www.freebuf.com/news/52056.html

        看完文章,赶快自己动手体验一下那种biubiu的快感吧!小编很懒,所以实战测试就交给你们咯—。—

**<br>**

**工具地址:**

**        Mana:**https://github.com/sensepost/mana

**        BackdoorFactory BDFProxy:**https://github.com/secretsquirrel/BDFProxy
