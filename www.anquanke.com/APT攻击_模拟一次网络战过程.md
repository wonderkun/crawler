> 原文链接: https://www.anquanke.com//post/id/103265 


# APT攻击:模拟一次网络战过程


                                阅读量   
                                **137571**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">11</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01825159fb6dd14144.png)](https://p3.ssl.qhimg.com/t01825159fb6dd14144.png)

鱼竿：<br>
基于golang语言的CHAOS远程后门(作者是巴西的开源爱好者)<br>[https://github.com/tiagorlampert/CHAOS](https://github.com/tiagorlampert/CHAOS)

鱼钩：<br>
ngrok(可以利用github账号登陆注册)<br>[https://ngrok.com/](https://ngrok.com/)

鱼饵：<br>
洋葱路由<br>
([http://www.theonionrouter.com/](http://www.theonionrouter.com/))<br>
匿名网络空间<br>
([https://www.upload.ee/](https://www.upload.ee/))<br>
彩蛋：<br>
钓鱼攻击配置用到的exp<br>
(word宏利用、浏览器插件利用)<br>
匿名邮箱<br>
([http://www.yopmail.com/](http://www.yopmail.com/))<br>
([https://mytemp.email/](https://mytemp.email/))<br>
匿名网上冲浪和洋葱共享<br>
（内详）<br>
在线匿名的获得一个美帝电话号<br>
（内详）<br>
渗透测试环境系统和平台

## 详细安装

【鱼竿】后门在kali上的安装：

<a class="reference-link" name="Install%20dependencies%20(You%20need%20Golang%20and%20UPX%20package%20installed)"></a>**Install dependencies (You need Golang and UPX package installed)**

$ apt install golang upx-ucl -y

<a class="reference-link" name="Clone%20this%20repository"></a>**Clone this repository**

$ git clone [https://github.com/tiagorlampert/CHAOS.git](https://github.com/tiagorlampert/CHAOS.git)

<a class="reference-link" name="Go%20into%20the%20repository"></a>**Go into the repository**

$ cd CHAOS

## 运行

$ go run CHAOS.go<br>
成功运行后如图：<br>[![](https://p3.ssl.qhimg.com/t01ec3446dcce1b3607.jpg)](https://p3.ssl.qhimg.com/t01ec3446dcce1b3607.jpg)<br>
【鱼钩】外网环境布置(ngrok)：<br>
注册ngrok，否则无法使用tcp转发模块，可以使用github便捷登陆<br>[https://dashboard.ngrok.com/user/signup](https://dashboard.ngrok.com/user/signup)<br>[![](https://p4.ssl.qhimg.com/t01b73eacf43e3a6781.jpg)](https://p4.ssl.qhimg.com/t01b73eacf43e3a6781.jpg)<br>
在kali中下载并放置于运行目录:<br>[![](https://p2.ssl.qhimg.com/t015a92eff6ec8bc90b.jpg)](https://p2.ssl.qhimg.com/t015a92eff6ec8bc90b.jpg)<br>
添加token目的是使用tcp模块：<br>[https://dashboard.ngrok.com/get-started](https://dashboard.ngrok.com/get-started)

将这行代码复制并且在kali中执行<br>[![](https://p0.ssl.qhimg.com/t01d522cce49a92001a.jpg)](https://p0.ssl.qhimg.com/t01d522cce49a92001a.jpg)<br>[![](https://p2.ssl.qhimg.com/t010c2e8c12d5ec0490.jpg)](https://p2.ssl.qhimg.com/t010c2e8c12d5ec0490.jpg)<br>
开启ngrok为自己开启一条外网通道：<br>
./ngrok tcp 4444<br>[![](https://p4.ssl.qhimg.com/t01c47ae26484d4674f.jpg)](https://p4.ssl.qhimg.com/t01c47ae26484d4674f.jpg)<br>[![](https://p3.ssl.qhimg.com/t016f7153a0298d41a9.jpg)](https://p3.ssl.qhimg.com/t016f7153a0298d41a9.jpg)<br>
标记的两个需要注意是域名和端口，以我的例子为[0.tcp.ngrok.io]和[19413]<br>
下一步ping出[0.tcp.ngrok.io]的ip地址，以上这一种利用同样适用于各类python开发的远程后门和msf都适用，甚至windows的RAT也非常适用，是一个非常便捷的端口转发技巧：<br>[![](https://p2.ssl.qhimg.com/t01e663680f14cffbc9.jpg)](https://p2.ssl.qhimg.com/t01e663680f14cffbc9.jpg)<br>
标记好这个ip地址后，进入chaos操作：<br>
选择1制作一个payload<br>[![](https://p0.ssl.qhimg.com/t01f980f8731d89faaa.jpg)](https://p0.ssl.qhimg.com/t01f980f8731d89faaa.jpg)<br>
填入刚刚ping出的ip:<br>[![](https://p1.ssl.qhimg.com/t017b3664de8147d686.jpg)](https://p1.ssl.qhimg.com/t017b3664de8147d686.jpg)<br>
端口写刚刚标记的端口:<br>[![](https://p2.ssl.qhimg.com/t01cdc633ed2e247505.jpg)](https://p2.ssl.qhimg.com/t01cdc633ed2e247505.jpg)<br>
为自己的后门写个具有欺骗性的名字，并加壳，然后启动tcp监听返回的shell：<br>[![](https://p1.ssl.qhimg.com/t01dc5af3b95a8f112b.jpg)](https://p1.ssl.qhimg.com/t01dc5af3b95a8f112b.jpg)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a4462e6f9b5e44ad.jpg)<br>
监听的本地端口写4444，因为我们刚才转发的就是本机4444端口作为监听端口,至此后门布置完成，也就是你的鱼竿和鱼钩已经准备好了，<br>
【鱼饵】接下来就是放置鱼饵：<br>
后门在chaos的目录下面，我们把它通过洋葱路由上传到网络空间，<br>[![](https://p0.ssl.qhimg.com/t01026ac2aeb195ce81.jpg)](https://p0.ssl.qhimg.com/t01026ac2aeb195ce81.jpg)<br>
上传好以后就会有下载链接，这一步就不赘述了：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018c1bd35f9ac2379b.jpg)<br>
使用洋葱路由就是为了匿名化，当然这个网络空间对于国内用户可能会网速过慢或者下载不成功，所以我这里也建议你做好跳板以后利用exp或者你自己的0day1day刷一些服务器选择一台合适的服务器作为网络空间(针对目标的地区选择，考虑法律因素和该地区监管追查能力)，但原则是隐藏好自己，可以多利用非本土的网络和公共的网络(无cctv录像监控，将移动电脑放进书包不要电脑包，或者直接使用公共无监管电脑，公共wifi，甚至是黑网吧人流大而杂的网络区域，使用live系统，加密你的硬盘等等这些在本篇不做赘述)进行，所以这一步就是将后门放置在公共网络空间[http://公共空间/后门.exe](http://%E5%85%AC%E5%85%B1%E7%A9%BA%E9%97%B4/%E5%90%8E%E9%97%A8.exe)<br>
我们先来看一下当受害人执行了后门以后的利用：<br>[![](https://p2.ssl.qhimg.com/t01994f89ab9cd93742.jpg)](https://p2.ssl.qhimg.com/t01994f89ab9cd93742.jpg)<br>
help可以看到这款后门可以进行的操作：<br>[![](https://p2.ssl.qhimg.com/t017e8339d480f8793e.jpg)](https://p2.ssl.qhimg.com/t017e8339d480f8793e.jpg)<br>
你可以看到受害者机器是我的win10专业版64位的电脑，当然光从这里我只能看出win10，其它是我自己知道的：<br>[![](https://p3.ssl.qhimg.com/t016d63413efbb56dbf.jpg)](https://p3.ssl.qhimg.com/t016d63413efbb56dbf.jpg)<br>
我们可以执行上传或者下载以及打开url和将后门添加到启动项的操作进行持久的访问，<br>[![](https://p1.ssl.qhimg.com/t016482fbf336125e3e.jpg)](https://p1.ssl.qhimg.com/t016482fbf336125e3e.jpg)<br>
这样等受害者机器重启也就可以获得持续的权限，我的机子装了防护软件是腾讯管家，特效全开病毒库最新，所以是不是咱们不小心把绕过杀软的技巧也一并get了呢，接下来我们在腾讯管家的流量防火墙看看tcp连接信息：<br>[![](https://p4.ssl.qhimg.com/t010b6628b6ffa35182.jpg)](https://p4.ssl.qhimg.com/t010b6628b6ffa35182.jpg)<br>
我构建的木马名称是explorer.exe，可以看到连接的流量是在美国的服务器上，通过这样的转发攻击的过程就显的隐蔽多了。<br>
手笨，没咋写过文章，这篇文章花了大概两个多小时，哈哈也算比较用心了，希望你们能喜欢，在这么久的时间段我将后门再次放入查杀检测，结果如下<br>[![](https://p5.ssl.qhimg.com/t0164f100d4d83b741a.jpg)](https://p5.ssl.qhimg.com/t0164f100d4d83b741a.jpg)<br>
接下来是附送的彩蛋，只可意yi会kan不jiu可dong言传：<br>
word宏利用<br>[![](https://p4.ssl.qhimg.com/t01dcaa4382018f75d1.jpg)](https://p4.ssl.qhimg.com/t01dcaa4382018f75d1.jpg)<br>[![](https://p1.ssl.qhimg.com/t01c3f3e8d5e1f13dd7.jpg)](https://p1.ssl.qhimg.com/t01c3f3e8d5e1f13dd7.jpg)<br>[![](https://p4.ssl.qhimg.com/t01a5e45ae59ad19153.jpg)](https://p4.ssl.qhimg.com/t01a5e45ae59ad19153.jpg)<br>[![](https://p3.ssl.qhimg.com/t01bf1a7556a13844eb.jpg)](https://p3.ssl.qhimg.com/t01bf1a7556a13844eb.jpg)<br>
github:

[https://github.com/flagellantX/wordexploit/blob/master/coding](https://github.com/flagellantX/wordexploit/blob/master/coding)

浏览器插件攻击：<br>
利用hfs+ngrok构建一个建议的网络服务器<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f45209d8316d5255.jpg)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ada65488330fa182.jpg)<br>
受害者访问该url后会自动下载执行后门，图中测试的是我构造的一段exp，写文章的时候测试点开把整个机子都搞奔溃了，万幸浏览器恢复文章没丢，不然近三个小时的磕碰手打就没了。<br>
github:

[https://github.com/flagellantX/BrowserKiller.git](https://github.com/flagellantX/BrowserKiller.git)

匿名邮件：[http://www.yopmail.com/en/](http://www.yopmail.com/en/)<br>[![](https://p3.ssl.qhimg.com/t011d41219589ad0c4b.jpg)](https://p3.ssl.qhimg.com/t011d41219589ad0c4b.jpg)

<a class="reference-link" name="%E4%BD%A0%E5%86%99%E5%85%A5%E4%B8%80%E4%B8%AA%E5%90%8D%E5%AD%97%E4%BB%A5%E5%90%8E%E5%B0%B1%E5%8F%AF%E4%BB%A5%E5%88%A9%E7%94%A8%E5%AE%83%E6%94%B6%E5%8F%91%E9%82%AE%E4%BB%B6%EF%BC%8C%E9%80%9A%E8%BF%87%E6%B4%8B%E8%91%B1%E6%B5%8F%E8%A7%88%E5%99%A8%E4%BD%BF%E7%94%A8%E5%AE%83%EF%BC%8C%E8%BF%99%E6%A0%B7%E5%AD%90%E7%9A%84%E8%AF%9D%E4%B8%8D%E5%AE%B9%E6%98%93%E9%80%9A%E8%BF%87%E9%82%AE%E7%AE%B1%E5%8F%8D%E8%BF%BD%E8%B8%AA%E3%80%82"></a>你写入一个名字以后就可以利用它收发邮件，通过洋葱浏览器使用它，这样子的话不容易通过邮箱反追踪。

匿名网上冲浪和洋葱共享：<br>
需要linux机器的ip是墙外ip（那种软件用一下）<br>
([https://www.parrotsec.org/download-full.fx](https://www.parrotsec.org/download-full.fx))<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01358a56c7447168d9.jpg)<br>[![](https://p3.ssl.qhimg.com/t013aacc17ae2a0d72f.jpg)](https://p3.ssl.qhimg.com/t013aacc17ae2a0d72f.jpg)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016847eb92365b3800.jpg)<br>[![](https://p2.ssl.qhimg.com/t0145ba2f40f46dc088.jpg)](https://p2.ssl.qhimg.com/t0145ba2f40f46dc088.jpg)<br>[![](https://p3.ssl.qhimg.com/t0122a172531a84632b.jpg)](https://p3.ssl.qhimg.com/t0122a172531a84632b.jpg)

<a class="reference-link" name="%E5%B0%86%E9%9C%80%E8%A6%81%E5%85%B1%E4%BA%AB%E7%9A%84%E6%96%87%E4%BB%B6%E6%8B%96%E5%85%A5%E5%90%8E%E4%BC%9A%E7%94%9F%E6%88%90%E4%B8%80%E4%B8%AA%E6%B4%8B%E8%91%B1%E9%93%BE%E6%8E%A5%E5%8D%B3%E5%AE%8C%E6%88%90%E3%80%82"></a>将需要共享的文件拖入后会生成一个洋葱链接即完成。

电话号：<br>
([https://www.textnow.com/signup](https://www.textnow.com/signup))<br>
([https://mytemp.email/](https://mytemp.email/))<br>
([https://www.allareacodes.com/area_code_listings_by_state.htm](https://www.allareacodes.com/area_code_listings_by_state.htm))<br>[![](https://p3.ssl.qhimg.com/t0177a507c6d6270213.jpg)](https://p3.ssl.qhimg.com/t0177a507c6d6270213.jpg)<br>
利用匿名邮箱完成注册<br>[![](https://p2.ssl.qhimg.com/t0142208d87454d1c62.jpg)](https://p2.ssl.qhimg.com/t0142208d87454d1c62.jpg)<br>[![](https://p2.ssl.qhimg.com/t018f3125b06e343922.jpg)](https://p2.ssl.qhimg.com/t018f3125b06e343922.jpg)<br>
选择一个区号填入注册你的号码<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01365674f0afc61d8e.jpg)<br>
完成

## [![](https://p4.ssl.qhimg.com/t01708fbb339951d07b.jpg)](https://p4.ssl.qhimg.com/t01708fbb339951d07b.jpg)[![](https://p4.ssl.qhimg.com/t01708fbb339951d07b.jpg)](https://p4.ssl.qhimg.com/t01708fbb339951d07b.jpg)

渗透测试环境系统和平台:<br>
VMware Download:<br>[https://www.vmware.com/products/workstation-pro.html](https://www.vmware.com/products/workstation-pro.html)<br>
VirtualBox Download:<br>[https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)<br>
Kali Linux Download:<br>[https://www.kali.org/downloads/](https://www.kali.org/downloads/)<br>
DVWA/Metasploitable:<br>[https://sourceforge.net/projects/metasploitable/files/Metasploitable2/](https://sourceforge.net/projects/metasploitable/files/Metasploitable2/)<br>
bWAP Download:<br>[https://www.vulnhub.com/entry/bwapp-bee-box-v16,53/](https://www.vulnhub.com/entry/bwapp-bee-box-v16,53/)<br>
Windows 10 Download:

[https://www.microsoft.com/en-us/software-download/windows10](https://www.microsoft.com/en-us/software-download/windows10)

补充：<br>
文中涉及到的url点击攻击别忘了使用链接缩短或者结合xss的伪装欺骗。

持续控制并将木马添加到了启动项，如果重新配置环境会丢失shell的话，提供一个办法就是使用完kali以后将它挂起，这样第二次使用就都还在了，想要真正的持续访问你需要改一些东西太复杂了下次文章说啦。

朋友跟我反映CHAOS不可以控制多个机器，我提供一个办法就是生成后门的时候不同机器针对不同端口，例如A机器监听4444，B机器的后门重新生成，监听5555，的确是有些繁琐，不太适用于那些功能强大的RAT点对点多台控制。

这次实施的模拟攻击，我把鱼竿选择了CHAOS框架，我今晚都在关注它的绕过杀软能力和持久性，大致总结一下我观察到的后门特点：<br>
每次生成的后门当下可以[未知]风险的身份绕过腾讯管家全特效<br>
报毒后不进行主动扫描并不会被查杀<br>
主动扫描后清除了后门任然没有丢掉权限可以执行任何提权命令<br>
重点是再次全盘扫描后提示本机无毒<br>
本次测试的安全防护软件有腾讯管家和国外的科摩多均无法检测出此后门，但是在360卫士云查杀下该后门会被检测出。<br>[![](https://p5.ssl.qhimg.com/t01004b4e88924bc145.jpg)](https://p5.ssl.qhimg.com/t01004b4e88924bc145.jpg)<br>[![](https://p4.ssl.qhimg.com/t01b358104ea12510ad.jpg)](https://p4.ssl.qhimg.com/t01b358104ea12510ad.jpg)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a2e5debac1fa029e.jpg)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bf2ebcff8225333a.jpg)<br>
结语：文章不够直观的话我会做视频教程在我的微博[@flagellantX](https://github.com/flagellantX)，如果文章中有错误和不足可以直接指出，可喷可踩，但是有好的攻击思路和更好的利用模式以及匿名技巧等等这些都可以跟我交流，我非常欢迎你跟我一起探讨共同进步。
