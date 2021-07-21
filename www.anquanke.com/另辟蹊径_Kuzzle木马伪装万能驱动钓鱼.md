> 原文链接: https://www.anquanke.com//post/id/147425 


# 另辟蹊径：Kuzzle木马伪装万能驱动钓鱼


                                阅读量   
                                **157837**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01fb990bb901c025b3.jpg)](https://p4.ssl.qhimg.com/t01fb990bb901c025b3.jpg)

近期，360核心安全团队监测到钓鱼网站大量传播主页劫持木马，诱导用户下载安装“万能驱动”软件后，偷偷在用户电脑上释放高隐蔽性的木马模块。通过深入的追踪，我们发现该劫持木马是Kuzzle木马团伙制作，目前看来他们不局限于使用bootkit方式来隐藏启动，本次监测到的木马结合社工和隐蔽的内核Rootkit技术试图突破杀软的防护。



## 传播过程

木马团伙专门用一个服务器来部署名为“万能驱动”的钓鱼网站，在上面放置诱导用户下载安装的链接。如下是该服务器使用的一个域名，该“万能驱动”网站页面高仿驱动精灵官网，实则是一个钓鱼网站，两款软件的名称和类型比较相近，极具迷惑性，木马团伙的仿冒意图明显。

[![](https://p3.ssl.qhimg.com/t011191f4abca9604cd.png)](https://p3.ssl.qhimg.com/t011191f4abca9604cd.png)

对该钓鱼网站的服务器进一步挖掘发现，该服务器使用多个域名来进行钓鱼，即钓鱼域名均指向同一服务器IP（222.***.51）。
<td valign="top" width="293">**钓鱼域名**</td>
<td valign="top" width="293">**rj.s****2.cn**</td>
<td valign="top" width="293">**rj.n*****c.cn**</td>
<td valign="top" width="293">**rj.b***x.cn**</td>
<td valign="top" width="293">**rj.q*********o.com**</td>
<td valign="top" width="293">**qd.e******6.cn**</td>
<td valign="top" width="293">**xp.l****0.com**</td>
<td valign="top" width="293">**win7.l****0.com**</td>

挖掘过程中发现，服务器首页为仿冒“驱动精灵”的官网钓鱼页面，此外服务器还部署了其他的钓鱼页面，均是仿冒常用电脑软件的下载页面，并且还会判断域名来控制返回给用户正常的或恶意的下载链接，进而提高其隐蔽性。

[![](https://p4.ssl.qhimg.com/t018ac761dd8b3fbde5.png)](https://p4.ssl.qhimg.com/t018ac761dd8b3fbde5.png)

上图页面是通过域名“qd.******6.cn”访问钓鱼服务器的“wnys.html”（万能钥匙下载页面），任意点击页面的位置将会弹出一个指向“百度”服务器的正常软件下载链接。然而，换一个域名访问相同的服务器页面如“http://rj.****2.cn/ wnys.html”，此时弹出的却是另外一个指向木马软件的下载链接。

从钓鱼网站下载的安装包是经过二次打包的程序，并且图标也做了欺骗性修改，一旦用户下载运行，就会先执行木马模块的释放流程，大概的运行流程如下图所示：

[![](https://p2.ssl.qhimg.com/t01b4028fb70103b45f.png)](https://p2.ssl.qhimg.com/t01b4028fb70103b45f.png)



## 样本分析

下面，我们从钓鱼网站下载的安装包开始，详细跟踪木马的感染过程。

[![](https://p5.ssl.qhimg.com/t0112f0d379c94c93ff.png)](https://p5.ssl.qhimg.com/t0112f0d379c94c93ff.png)

### 一、安装过程

首先，从静态看该安装包的大小比较大，原因是由于其在资源里包含了另外两个安装包文件，其中一个是正常的“驱动人生”安装包，另一个则是包含恶意模块的软件“FreeImage”。

双击安装包运行后，选择安装路径，然后点击下一步，首先样本会检测安全软件是否运行，如果用户电脑没有运行安全软件，则会直接偷偷安装恶意程序“FreeImage”，然后再运行正常的驱动人生程序，当用户看到驱动人生的安装界面时木马模块实际上已经安装完毕。

相反，如果检测过程中发现系统存在360安全卫士，就会弹出诱导信息，让用户手动关闭360安全卫士；如果不退出360安全卫士，就会反复弹出对话框直到用户放弃安装或者退出360安全卫士后进入上述安装流程。

[![](https://p0.ssl.qhimg.com/t010edf12b657fb273a.png)](https://p0.ssl.qhimg.com/t010edf12b657fb273a.png)

静默安装的恶意软件“FreeImage”是从开源项目改造而来，文件名为“FreeImage_292.exe”，以命令参数“-quiet”启动后就会释放恶意驱动模块“drvtmpl.sys”，并通过写注册表的方式直接注册该驱动服务。

为了使恶意驱动“drvtmpl.sys”优先于安全软件启动，恶意程序将驱动添加到“System Reserved”（系统保留）组，从ServiceGroupOrder的加载顺序可以看到“System Reserved”组位于第一启动顺序，这样保证驱动最优先启动。

除了注册关键的驱动服务以外，“FreeImage”安装包还释放了一些驱动运行过程中需要用到的加密资源。

[![](https://p2.ssl.qhimg.com/t01a212f51cc0b592e8.png)](https://p2.ssl.qhimg.com/t01a212f51cc0b592e8.png)

至此安装包的主要工作就完成了，在用户重启电脑后，系统就会自动以优先于安全软件的顺序启动运行恶意驱动“drvtmpl.sys”来完成后续的任务。

### 二、“drvtmpl.sys”驱动

“drvtmpl.sys”驱动是一个加载器，驱动启动后先注册一个“LoadImageNotify”模块加载回调，在回调函数里完成主要的工作。其主要任务是自我隐藏，在内存解密并加载后续的恶意驱动模块：surice.*（x86和x64扩展名不同）。

[![](https://p3.ssl.qhimg.com/t0119641554d5632eb4.png)](https://p3.ssl.qhimg.com/t0119641554d5632eb4.png)

1、自我隐藏

drvtmpl.sys主要是通过挂钩内核注册表对象回调和磁盘读写回调来隐藏自身，下图是重启前后的注册表对比，发现重启系统后，驱动服务drvtmpl的内容发生变化，注册表项伪装成了一个USB扩展驱动，此时使用ARK工具的HIVE解析功能也无法还原真实注册表信息。

[![](https://p1.ssl.qhimg.com/t01110462062ab270ac.png)](https://p1.ssl.qhimg.com/t01110462062ab270ac.png)

之所以会出现这种现象， 是因为drvtmpl.sys事先挂钩了注册表Hive对象的CmpFileWrite回调，在系统写入Hive文件之前进行拦截保护。

同时，驱动还挂钩磁盘驱动(disk.sys)的IRP读/写回调，挂钩的过程是在“classpnp.sys”驱动模块的加载空间寻找空闲位置，在该位置写入跳转到实际挂钩函数的代码，最后再将磁盘驱动的IRP读写回调修改成该地址，之所以这样做是因为想让磁盘读写回调的函数地址仍处于“classpnp.sys”驱动模块空间，由此绕过某些ARK工具的钩子检测。

[![](https://p3.ssl.qhimg.com/t01b20e4148c4a71a85.png)](https://p3.ssl.qhimg.com/t01b20e4148c4a71a85.png)

drvtmpl.sys主动调用ZwSetValueKey将自身服务的注册表项进行修改会触发挂钩函数的功能。HIVE的挂钩函数，使磁盘的Hive数据与内存中的不一致，干扰注册表编辑器的读取结果。磁盘驱动（disk.sys）IRP读/写回调函数的挂钩主要想保护两个对象。一个是system服务注册表对应的Hive文件，即“C:\Windows\System32\config\SYSTEM”，另一个则是“drvtmpl.sys”驱动本身。在挂钩函数里检查IO操作的位置是否落在受保护对象的范围，返回欺骗性数据。

使用PCHunter的Hive分析功能查看drvtmpl服务的注册表项，将会发送磁盘读的IRP请求，进入挂钩后的磁盘读例程，该例程检查到读磁盘的位置刚好落在“SYSTEM”文件中drvtmpl服务项的位置，于是返回给请求者虚假的注册信息。

当挂钩函数检测到读磁盘的位置为“drvtmpl.sys”驱动本身时，比如用Winhex访问该驱动，则会返回欺骗性数据（全为0）。

[![](https://p3.ssl.qhimg.com/t0131192bdd32c2711f.png)](https://p3.ssl.qhimg.com/t0131192bdd32c2711f.png)

2、解密shellcode加载surice.*内核模块

drvtmpl.sys利用shellcode来加载surice.*内核模块，该内核模块是一个被加密的驱动文件，在32位环境文件名是“surice.eda”， 64位下文件名是“surice.edi”。

drvtmpl.sys解密shellcode并执行后，读取“surice.eda”文件到内存，接着进行解密，解密的算法是根据传入的参数key进行一些简单的异或运算。

“surice.eda”文件解密后，在内存得到一个原始驱动程序，接着shellcode将驱动程序按照PE格式进行解析，拷贝节数据、修重定位表和填充IAT表，执行驱动程序的入口函数。

[![](https://p2.ssl.qhimg.com/t01fbf43fadc8395899.png)](https://p2.ssl.qhimg.com/t01fbf43fadc8395899.png)

### 三、“surice.*”驱动

shellcode加载“surice.*”驱动后，调用了该驱动的入口函数。surice.*的入口函数注册LoadImageNotify模块加载、CreateProcessNotify进程创建、CreateThreadNotify线程创建3种回调例程，后续的主要工作由3个回调例程协作完成。surice.*驱动是该木马的核心业务模块，主要负责向3环应用层环境注入shellcode,，用来解密并启动nestor.tga和nsuser.tga木马模块。

[![](https://p4.ssl.qhimg.com/t01e296556852b09532.png)](https://p4.ssl.qhimg.com/t01e296556852b09532.png)

1、线程创建回调例程

该例程的主要功能是向explorer.exe桌面进程注入shellcode，并且仅在第一次创建该进程时进行注入操作。注入的过程是先在桌面进程分配一段虚拟内存，同时将该地址存储在注册表Tcpip子健下的EchoMode字段，然后拷贝shellcode到该内存，并为其分配MDL映射到内核地址以便驱动在进程创建的回调例程里与shellcode通信。

注入shellcode代码后通过对explorer.exe的SendMessageW函数进行IAT Hook，获得shellcode的执行机会。

[![](https://p1.ssl.qhimg.com/t012ef19876255b3b10.png)](https://p1.ssl.qhimg.com/t012ef19876255b3b10.png)

2、进程创建回调例程

该例程的主要功能是在系统创建新进程时，通过检查桌面进程shellcode开始位置缓冲区中的进程列表（刚注入时为空，后由3环木马模块修改），来判断是否为需要劫持的浏览器进程。若为要劫持的浏览器进程，则设置全局标志来通知模块加载回调例程向该浏览器进程注入shellcode来启动劫持模块。进程列表，用分号“;”区分不同进程名。

[![](https://p1.ssl.qhimg.com/t013259369ee12fdd26.png)](https://p1.ssl.qhimg.com/t013259369ee12fdd26.png)

3、模块加载回调例程

该例程在全局标志g_flag_brower大于0且加载模块为ntdll.dll（创建进程加载的第一个模块）时进入劫持流程，劫持过程是通过修改浏览器程序的OEP使其跳转到注入的shellcode的入口点。

该例程往浏览器进程注入的shellcode实际上与线程创建回调例程往桌面进程注入的shellcode相同，不过在执行前修改了一下其中的一个路径参数，配置shellcode去解密加载另一个木马模块nsuser.tga（此模块由注入桌面进程的模块nestor.tga联网下载而来）。

除了注入shellcode到浏览器进程外，该例程还负责阻止安全软件往浏览器加载安全模块，使其失去对浏览器的保护功能。

[![](https://p5.ssl.qhimg.com/t0130f75969066f5d42.png)](https://p5.ssl.qhimg.com/t0130f75969066f5d42.png)

### 四、浏览器劫持

系统启动过程中驱动程序的准备工作完成后，后续的任务就主要交给3环的shellcode程序来完成。桌面进程的shellcode解密nestor.tga模块来负责控制管理、升级等功能，而浏览器进程的shellcode解密nsuser.tga模块实现劫持主页的功能。

1、nestor.tga模块

本模块运行后会联网进行更新检测，并下载相应的加密资源包进行解压，更新的接口需要带上特定的参数才能返回正常的更新信息。

[![](https://p3.ssl.qhimg.com/t015eed4f4b7d9bed88.png)](https://p3.ssl.qhimg.com/t015eed4f4b7d9bed88.png)

更新信息包含重要的字段时downloadurl和mainpage，一个是更新包的下载地址，另一个则是云控劫持的浏览器主页地址。下载地址对应的更新包包含加密的浏览器劫持模块nsuser.tga和劫持配置文件fpld.spc，具体的文件列表和对应功能如下所示。
<td valign="top" nowrap width="237">更新包文件</td><td valign="top" nowrap width="327">说明</td>

说明
<td valign="top" nowrap width="237">**fpld.spc**</td><td valign="top" nowrap width="327">浏览器劫持配置</td>

浏览器劫持配置
<td valign="top" nowrap width="237">**nestor.idx**</td><td valign="top" nowrap width="327">包含资源包文件列表的索引信息</td>

包含资源包文件列表的索引信息
<td valign="top" nowrap width="237">**nestor.tga**</td><td valign="top" nowrap width="327">注入桌面进程的更新、控制程序32位版</td>

注入桌面进程的更新、控制程序32位版
<td valign="top" nowrap width="237">**nestor.tgi**</td><td valign="top" nowrap width="327">注入桌面进程的更新、控制程序64位版</td>

注入桌面进程的更新、控制程序64位版
<td valign="top" nowrap width="237">**nshper.tga**</td><td valign="top" nowrap width="327">监控360安全防护产品</td>

监控360安全防护产品
<td valign="top" nowrap width="237">**nsupp.tgg**</td><td valign="top" nowrap width="327">负责拷贝资源包文件</td>

负责拷贝资源包文件
<td valign="top" nowrap width="237">**nsuser.tga**</td><td valign="top" nowrap width="327">注入浏览器进程的劫持程序</td>

注入浏览器进程的劫持程序
<td valign="top" nowrap width="237">**surice.eda**</td><td valign="top" nowrap width="327">更新的业务驱动32位版</td>

更新的业务驱动32位版
<td valign="top" nowrap width="237">**surice.edi**</td><td valign="top" nowrap width="327">更新的业务驱动64位版</td>

更新的业务驱动64位版

更新完资源后，根据程序的设定将会有一段潜伏期，若感染的时间不超过3天则不会运行浏览器劫持的流程。当时间超过3天，控制程序将读取劫持配置文件fpld.spc，根据其中的信息生成劫持列表填充到shellcode起始位置（如上文所述）。fpld.spc文件解密后的浏览器劫持列表如下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015f842fce81ab62af.png)

然后驱动层模块surice.*就会启动浏览器注入功能，进而启动nsuser.tga模块进行劫持。

2、nsuser.tga模块

本模块注入浏览器时，安全软件的保护模块也被卸载掉了，在此基础上对浏览器进行劫持就显得相对轻松。劫持浏览器主页的方式是利用浏览器的通用功能修改其命令行参数，使浏览器解析参数里附带一个url，实现在启动时打开的第一个页面（主页）为该url。

对于IE浏览器，本模块直接修改进程空间里的命令行。获取GetCommandLineA/ GetCommandLineW（这两个API的内部实现只是简单地返回一个保存命令行参数字符串及其长度的全局对象）的返回对象，将其中的命令行字符串指针指向新的命令行参数，并更新其字符串长度。IE浏览器启动时获取到的命令行参数就会包含要劫持的主页地址，从而浏览器的主页信息就被修改，并且不会留下痕迹。

而对于第三方的浏览器，考虑到其启动时获取命令行参数的方式可能不同，采取使用新命令行参数重新创建子进程的方式来进行主页劫持。

[![](https://p4.ssl.qhimg.com/t019499ffbf243c3074.png)](https://p4.ssl.qhimg.com/t019499ffbf243c3074.png)

## 感染分布

下面是此类木马4月份在全国各地区的传播情况分布图，传播的量级在10万以上，可以看出主要在沿海地区传播，其中广东省为重灾区：

[![](https://p5.ssl.qhimg.com/t01f8e4729d86522812.png)](https://p5.ssl.qhimg.com/t01f8e4729d86522812.png)

## 总结与查杀

Kuzzle木马团伙善于使用木马的手法来做流氓推广业务盈利，盗用知名公司的数字签名，感染VBR，钓鱼网站传播，RootKit保护技术，甚至还采用诱导用户退出安全软件的社工套路，不断的更新其木马的自我隐藏、自我保护的技术，最终在安全软件严防死守的夹缝中得以生存。从本例木马的执行框架来看，木马经过多层的伪装和隐藏，环环相扣，从传播到安装，经3环进入0环，又从0环渗透到3环，每一步都是精心策划，小心谨慎的绕过安全检测，还试图逃离安全人员的审查，尽可能的长期潜藏在用户电脑中牟利。

目前360已针对此类样本全面查杀，为用户电脑保驾护航，同时也提醒广大用户安装软件时使用正规的下载渠道，避免上当受骗。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0194be2f5e4113fc19.png)

## Hashs

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011962a2e76f35ad6a.png)
