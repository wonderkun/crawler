> 原文链接: https://www.anquanke.com//post/id/177815 


# 部分魔兽争霸地图被Lucky勒索软件感染


                                阅读量   
                                **179573**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01ea4b2fa41a77f69f.jpg)](https://p2.ssl.qhimg.com/t01ea4b2fa41a77f69f.jpg)



刚刚过去的“五一”小长假里，各大景区“汹涌”的人山人海，想必让很多选择留在家中打游戏的玩家都庆幸自己躲过了一劫。不过，游戏世界里却也未必安宁，就在五一节前，360安全大脑拦截并查杀了一款通过《魔兽争霸3》游戏地图进行传播的新型蠕虫病毒，玩家一旦在游戏平台中选择了带有该蠕虫的地图，蠕虫就会感染玩家的计算机。



## 魔兽争霸地图或均受牵连

特别需要注意的是，面对该蠕虫病毒的威胁，广大玩家可别低估病毒的传染能力。根据360安全大脑追踪发现，该蠕虫在入侵得手后，会进一步感染玩家魔兽争霸中的其它正常游戏地图。这就意味着，若你的小伙伴中毒不自知，还邀你组局开黑，当你进入了游戏房间，你的地图也会随之中招。因此如若不及时查杀，病毒可能在最短时间内造成大面积感染。

经过360安全大脑的深度溯源分析，发现蠕虫作者使用的C&amp;C域名带有lucky2048字样，故将此蠕虫病毒命名为“Lucky蠕虫”。360安全大脑在监测到这一新型病毒后，已第一时间实现了全面查杀，因此“Lucky蠕虫”的活跃度在五一节假日这一用户玩游戏的高峰时段就有了非常明显地跌落。

所以，对于安装有360安全卫士（拥有360安全大脑的支持）的电脑用户而言，即便玩了《魔兽争霸3》，也不必担心电脑会受到“Lucky蠕虫”的入侵。

[![](https://p0.ssl.qhimg.com/t017577d747e69057de.png)](https://p0.ssl.qhimg.com/t017577d747e69057de.png)

Lucky蠕虫整体工作流程



## 解刨“蠕虫”母体 全面分析攻击原理

某个被感染的“Green Circle塔防三国”地图结构如下，其中主脚本“war3map.j”被插入一句代码以触发执行嵌入的脚本“initrb”（“File00000028.xxx”），该脚本即为被利用的魔兽地图漏洞攻击代码，主要功能是释放并执行lucky蠕虫模块“MX.txt”（“File00000029.exe”，实际上是个DLL程序）。

[![](https://p4.ssl.qhimg.com/t01ecf232af31ae3dac.jpg)](https://p4.ssl.qhimg.com/t01ecf232af31ae3dac.jpg)

脚本“war3map.j”在主函数末尾插入了一句调用代码，用来执行“initrb”漏洞代码：

[![](https://p2.ssl.qhimg.com/t01e5b2ebf260f7446a.jpg)](https://p2.ssl.qhimg.com/t01e5b2ebf260f7446a.jpg)

“initrb”漏洞攻击代码其实早在去年就有人公开披露过，只不过现在被不法分子用来传播蠕虫病毒获取“肉鸡”（参考：“hxxps://www.52pojie.cn/thread-718808-1-1.html”）。该代码主要利用了脚本变量的类型转换漏洞实现了任意内存读写，进而劫持魔兽争霸3主程序去加载运行蠕虫模块“MX.txt”。

[![](https://p4.ssl.qhimg.com/t016dcec072afde0667.jpg)](https://p4.ssl.qhimg.com/t016dcec072afde0667.jpg)

此漏洞形成的原因是当脚本中的全局变量和局部变量同名时，会将全局变量转成局部变量，从而造成全局变量的引用指针发生了意外转换。如下全局整型数组变量“Memory”在某过程函数中被重新定义成了一个局部的整型变量，导致全局变量“Memory”地址变成0，从而可以索引进程空间所有的内存地址范围，进而用来实现任意内存读写。

[![](https://p3.ssl.qhimg.com/t018d2d77094afb64d2.jpg)](https://p3.ssl.qhimg.com/t018d2d77094afb64d2.jpg)

该漏洞影响了《魔兽争霸3》的多个历史版本，攻击代码中对此也做了相应的兼容性检测。

[![](https://p5.ssl.qhimg.com/t01783e154c97955893.jpg)](https://p5.ssl.qhimg.com/t01783e154c97955893.jpg)

蠕虫模块“MX.txt”是一个加了VMP强壳保护的DLL程序，被《魔兽争霸3》游戏进程加载运行后，主要的工作流程分成3个部分，分别是感染正常的魔兽地图、安装持久化后门和远程控制。

### 1、感染地图

该蠕虫在感染用户正常地图时首先释放魔兽“MPQ”格式的API库文件“SFmpq.dll”，使用该文件可以方便的操作“MPQ”格式的地图资源。

[![](https://p3.ssl.qhimg.com/t017e50676c717002b2.jpg)](https://p3.ssl.qhimg.com/t017e50676c717002b2.jpg)

然后去《魔兽争霸3》安装路径的地图目录下寻找所有的“*.w3x”格式的地图，并使用MPQ库API来操作这些地图文件的内部脚本资源。

[![](https://p3.ssl.qhimg.com/t017ef9a9a67eb61b79.jpg)](https://p3.ssl.qhimg.com/t017ef9a9a67eb61b79.jpg)

该类地图文件的主运行脚本为“war3map.j”，于是该蠕虫找到该脚本位置，准备往其中插入漏洞利用代码和蠕虫程序本身。

[![](https://p1.ssl.qhimg.com/t019cda087765357ad2.jpg)](https://p1.ssl.qhimg.com/t019cda087765357ad2.jpg)

找到“war3map.j”的主函数尾位置，然后插入一行调用代码以执行真正的漏洞利用脚本“initrb”，接着将内置的“initrb”脚本添加到目标地图文件中，脚本代码与前述一致。

[![](https://p5.ssl.qhimg.com/t01429672369b64ff1d.jpg)](https://p5.ssl.qhimg.com/t01429672369b64ff1d.jpg)

除了漏洞利用脚本外，还往目标地图中添加蠕虫病毒母体本身，进行自我复制。

[![](https://p0.ssl.qhimg.com/t011ab11d0daa90277b.jpg)](https://p0.ssl.qhimg.com/t011ab11d0daa90277b.jpg)

### 2、安装持久化后门

此蠕虫病毒进行持久化主要是根据云控配置联网下载两张经过处理的图片，并进一步解密出后门模块安装到用户系统中潜伏。

云控配置的存放地址有3个（其中最后一个无法访问），首先连接“hxxp://umsdfyuwlp.tk”，该地址正常访问的时候应该是这样：

[![](https://p0.ssl.qhimg.com/t015cb7f4af3c10564b.jpg)](https://p0.ssl.qhimg.com/t015cb7f4af3c10564b.jpg)

但是由于该蠕虫感染传播的速度太快，可能作者自己也没有想到，此服务器很快就负担不起上十万的访问请求了，于是该服务器的常态返回结果如下：

[![](https://p4.ssl.qhimg.com/t010a092c14d67ae393.jpg)](https://p4.ssl.qhimg.com/t010a092c14d67ae393.jpg)

不过没关系，这个服务器处理不过来，病毒作者机智的准备了另外一个利用公共设施的服务地址“hxxps://lucky2048.github.io”，由于该地址使用的是Github专门为个人用户提供的博客服务器，自带了负载均衡，再也不必操心“肉鸡”一下收割太多的问题了。

[![](https://p4.ssl.qhimg.com/t0195a81dcd50256092.jpg)](https://p4.ssl.qhimg.com/t0195a81dcd50256092.jpg)

获取了这些云控配置后，对其进行分割和解密，最终得到3个信息字段如下，包括一个ip地址和两个图片下载地址，其中后两个图片地址包含的是与本节持久化相关的模块，第一个ip地址在下面的远程控制功能使用。

[![](https://p3.ssl.qhimg.com/t0188f5751993734fa1.jpg)](https://p3.ssl.qhimg.com/t0188f5751993734fa1.jpg)

当病毒检测到系统中的后门模块不存在时，就会下载对应的“1.gif”或者“2.gif”图片来进行安装。每张图片均在数据尾部附加了一个压缩过的PE文件，数据组织格式采用很常见的木马套路：“图片数据”+“0x033E0F0D”标志头+“压缩数据长度”+“zlib压缩数据”。

[![](https://p0.ssl.qhimg.com/t01783027a72eefd0ba.jpg)](https://p0.ssl.qhimg.com/t01783027a72eefd0ba.jpg)

“1.gif”图片解压后得到的模块是一个伪装成“Windows Media Player”的后门程序，经过分析发现，目前该模块的功能基本上和蠕虫病毒母体重合，只是少了其中感染魔兽地图的功能。如下可见该后门模块伪装成“Windows Media Player”程序并设置了隐藏和自启动。

[![](https://p2.ssl.qhimg.com/t01c30c568787f47a68.jpg)](https://p2.ssl.qhimg.com/t01c30c568787f47a68.jpg)

“2.gif”图片解压后得到的模块是该蠕虫母体本身，最终会拷贝一份到魔兽安装目录下为“war3*.flt”（*为随机字符），并且当检测到该目录不存在该flt文件时会重新安装。之所以命名为flt文件是因为《魔兽争霸3》主程序War3.exe在启动时会自动加载运行该目录下的“*.flt”插件模块。

[![](https://p5.ssl.qhimg.com/t01cfcfa03682e35d4a.jpg)](https://p5.ssl.qhimg.com/t01cfcfa03682e35d4a.jpg)

另外蠕虫母体还会释放一个加载器“rundll*.exe”到魔兽安装目录下，该加载器的主要功能其实就仅仅是加载运行蠕虫母体本身，辅助其持久化地运行在用户系统中。

[![](https://p3.ssl.qhimg.com/t01381dab0c47f53d56.jpg)](https://p3.ssl.qhimg.com/t01381dab0c47f53d56.jpg)

### 3、远程控制

从云控配置里解密出第一个字段数据，当前配置解密出的数据为字符串“999”，但经过分析该字段被当作一个ip地址来连接远程控制服务器，只不过目前此地址无效。

[![](https://p3.ssl.qhimg.com/t019ea9a5d64e53fdca.jpg)](https://p3.ssl.qhimg.com/t019ea9a5d64e53fdca.jpg)

使用该ip地址加上固定的一个端口号“19730”，从而构造出远程控制服务器的connect地址结构体参数，但是由于ip地址“999”无效导致当前无法连接成功，不过作者可以随时更改Github上的配置来收割这些中招的“肉鸡”。

[![](https://p4.ssl.qhimg.com/t016aa670862bd8f7de.jpg)](https://p4.ssl.qhimg.com/t016aa670862bd8f7de.jpg)

若成功上线，将进入异步的远控控制码处理流程，如下可见包含“1001”、“1002”等多个控制码处理过程。

[![](https://p1.ssl.qhimg.com/t01118a680976a840ec.jpg)](https://p1.ssl.qhimg.com/t01118a680976a840ec.jpg)

经过调试分析后整理该远控的功能列表如下，发现是个非常精简的“迷你版”远控，或许该作者别有用心，只需要特定的几个控制功能。

[![](https://p5.ssl.qhimg.com/t01fc66364e5bc973ac.jpg)](https://p5.ssl.qhimg.com/t01fc66364e5bc973ac.jpg)

本蠕虫病毒利用已知的游戏客户端漏洞进行大规模的传播后门木马，游戏用户可能在正常玩游戏过程中没有任何防备的情况下就不知不觉中招了，并且该病毒还会主动感染其他正常的游戏地图，进行主动的传播扩散，大大增加游戏用户互相感染的速度。中招后该病毒在用户机器上安装释放后门远控程序，然后等待时机成熟便可以通过修改放在公共设施Github上的配置来控制成千上万的“肉鸡”用户。

继WannaCry勒索病毒利用“永恒之蓝”漏洞核武器进行全球大范围爆发后，360安全大脑再次拦截了一款同样通过漏洞核武器进行大规模传播感染的“Lucky”蠕虫病毒。黑客利用已知的公开漏洞进行大规模的网络攻击早已成为新的安全常态，此次事件虽然在作者还未进行大规模收割“肉鸡”用户造成更大的危害之前就被360安全大脑成功拦截，但安全不可松懈，建议广大的网民及时前往“weishi.360.cn”，安装最新版本的360安全卫士，可以在用户游戏期间进行有效的防御和病毒查杀，全方位保护用户安全。

[![](https://p3.ssl.qhimg.com/t01e5a0b3e281e22770.jpg)](https://p3.ssl.qhimg.com/t01e5a0b3e281e22770.jpg)

## IOCs

[![](https://p1.ssl.qhimg.com/t01adf88327b675201d.png)](https://p1.ssl.qhimg.com/t01adf88327b675201d.png)
