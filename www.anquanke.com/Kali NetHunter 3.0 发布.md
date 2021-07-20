> 原文链接: https://www.anquanke.com//post/id/83266 


# Kali NetHunter 3.0 发布


                                阅读量   
                                **253022**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.offensive-security.com/kali-nethunter/nethunter-3-0-released/](https://www.offensive-security.com/kali-nethunter/nethunter-3-0-released/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t014a79775304417540.png)](https://p4.ssl.qhimg.com/t014a79775304417540.png)

       ** Android 移动渗透测试平台**

        NetHunter 已被积极地开发了一年有余。而从它的上一个版本看来，它简直是经历了一次彻底的变革。我们在 v3.0 版本上花了一点时间，全面翻修了 NetHunter，使它拥有了更加优美的接口和更加充分运转的功能集合。

        通过由 binkybear、fattire 和 jmingov 领导的 NetHunter 社区中令人惊喜的工作，我们现在可以很自豪很自信地说，NetHunter 是一款稳定的、商业级的移动渗透测试平台。所以，我们对今天NetHunter 3.0 的发布感到非常兴奋——让游戏开始吧！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-main-menu.png)

 

**        Kali NetHunter 3.0 有什么新颖之处**

        **NetHunter Android 应用的重新编写**

        NetHunter Android 应用被完全重新设计，并变得更加“以应用为中心”。我们加入了许多新的特性和攻击实例，以及一大堆社区驱动的bug修复。NetHunter 应用现已趋于成熟，已经成为了一个帮助应对各种复杂攻击的实用工具。此外，它现在还能让你独立地管理你的 Kali chroot，包括在需要时重建和删除 chroot。你也可以选择在你的 chroot 中安装独立的 metapackages，不过默认的 kali-nethunter metapackage 是包含所有的基本必需品的。

        **支持 Android 5.0 Lollipop 和 Android 6.0 Marshmallow**

        是的，你没听错。NetHunter 现在支持 Marshmallow（Android AOSP 6.x）的适用设备了——尽管我们并不一定是“最新即最好”理论的粉丝。我们最爱的设备依然是一加手机（OnePlus One phone），这是出于对尺寸、CPU/RAM 资源和Y型电缆充电支持的综合考虑。

 

        **针对新设备的全新构建脚本和更简易的整合**

        我们对应用的重新编写还包括了生成图像的代码，我们将它完全移植到了 Python，并且显著地优化了构建时间。构建程序现在可以构建不含内置 Kali chroot 的小型 NetHunter 图像（~70MB）——允许你之后通过这个应用下载 chroot。

        我们同时也使在那些 NetHunter 能运行的新设备上创建端口变得更加容易。我们发现有几个感兴趣的 PR 们已经开始考虑对 Galaxy 设备的支持问题了……

 

        **精彩的 NetHunter 文件编制**

        也许我们对这个文件编制有点偏爱，或许它只是“不错”而不是“精彩”…… 不过它确实比之前优秀了很多，你可以在 [NetHunter Github Wiki](https://github.com/offensive-security/kali-nethunter/wiki) 的表格中一探究竟。这里面还有关于下载、构建、安装NetHunter的主题，还包括关于每一条NetHunter攻击实例和特性的速览。



        **NetHunter Linux Root Toolkit 安装程序**

        我们推出了新的 NetHunter 安装程序，用于在 Linux 或 OSX 上运行。这个安装程序是由一套 Bash 脚本构建而成的，你可以利用它在支持的一加或 Nexus 设备上解锁和快速存储安装 NetHunter 图像。让我们欢迎由 jmingov 开发的 [NetHunter LRT](https://github.com/offensive-security/nethunter-LRT)。

 

        **下载 NetHunter 3.0**

        要想获取 NetHunter Zip of Joy（与[Kali ISO of Doom](https://www.offensive-security.com/kali-linux/kali-linux-iso-of-doom/)相对），进入 the Offensive Security NetHunter 的下载页面，为你的设备下载图像。注意一些 Nexus 图像有 Lollipop 和 Marshmallow 的双重特征。一旦你下载完毕后，请访问 [NetHunter Wiki](https://github.com/offensive-security/kali-nethunter/wiki) 查看安装说明。

        下载链接：[https://www.offensive-security.com/kali-linux-nethunter-download/](https://www.offensive-security.com/kali-linux-nethunter-download/)。

 

       ** 是 OSCP ？再努力一把，赢取 NetHunter 设备**

        几天前我们发布了一篇关于“[成为OSCP意味着什么](https://www.offensive-security.com/offsec/what-it-means-to-be-oscp/)”的博文。如果你有 OSCP 认证并想获得赢取一加 NetHunter 设备的机会，那么来阅读我们之前的那篇博文吧！

 

       ** NetHunter 3.0 Image Gallery**

        如果不放一些截图可以难以引起大家的兴趣和重视，那么，请尽情享受吧！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-vnc.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-services.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-searchsploit.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-nmap.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-mpc.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-mitm-03.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-mitm-02.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-mitm-01.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-menu.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-mana.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-macchanger.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-home.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-hid.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-duckhunter.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-commands.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-chroot-02.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-chroot-01.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.offensive-security.com/wp-content/uploads/2016/01/nethunter-badusb.png)
