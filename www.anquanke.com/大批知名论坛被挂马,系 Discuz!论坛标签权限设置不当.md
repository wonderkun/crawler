> 原文链接: https://www.anquanke.com//post/id/83919 


# 大批知名论坛被挂马,系 Discuz!论坛标签权限设置不当


                                阅读量   
                                **170007**
                            
                        |
                        
                                                                                    



近期360安全中心监测到国内多家知名网站论坛系统遭遇挂马,涉及一些访问量数十万甚至上百万的大型论坛,包括威锋网(360发出安全报警后迅速修复http://weibo.com/1645903643/Drz88eZpT)、腾讯穿越火线论坛、迅雷论坛、大众论坛、莱芜在线等,甚至连一些黑客“据点”也未能幸免,例如专门进行木马制售和免杀交流的小七论坛也遭遇同样手法的“黑吃黑”挂马([http://blogs.360.cn/360safe/2016/04/28/xiaoqi_forum_web_trojan/](http://blogs.360.cn/360safe/2016/04/28/xiaoqi_forum_web_trojan/))。目前,这些论坛中部分已经修复了问题,但仍有一些知名论坛存在严重风险,任意注册用户都可以轻松挂马,利用热门帖等途径向论坛的其他用户发起直接攻击。<br>

经过360安全中心调查,上述知名论坛被挂马攻击的漏洞全都是Flash漏洞。也就是说,当电脑使用老版本Adobe Flash Player的用户访问被挂马论坛时,如果没有专业安全软件保护,电脑在浏览挂马帖过程中就会自动下载运行木马。而这些被挂马的论坛,则都是使用了国内流行的Discuz!建站系统搭建的。那么Discuz!论坛和Flash挂马有什么关联呢?

原来,在Discuz!系统的论坛中,用户在发帖时可以通过[flash]标签,直接在帖子内嵌入来自任意网站的flash文件,这些flash文件在其他用户浏览对应的主题、帖子时,都是自动播放的,这一漏洞就给了攻击者非常便利,甚至非常定制化的攻击途径:攻击者只要将挂马的Flash文件直接嵌入论坛帖子中,等待贴主或任意访问论坛的用户打开帖子,攻击者就可以完全控制他们的电脑。

这一攻击形式相当灵活,对论坛进行挂马的攻击者既可以通过回帖到热门主题的方式,给论坛中的大量用户集中挂马,也可以针对对特定主题、特定内容、特定发帖人的帖子感兴趣的人做小范围“精准打击”,在不引起大部分人注意的前提下,对这些用户进行挂马,例如我们看到在腾讯穿越火线论坛的挂马案例中,有用户发帖称意外获得了礼包,紧接着就有挂马者随即跟进,在他的帖子下面挂马,使得贴主和其他围观群众被flash木马攻击。

360安全中心在研究后发现,Discuz!论坛针对自动播放的[flash]标签是默认关闭的,而这些受影响的管理员,则不约而同地开启了这个标签的功能,导致了这个标签,从而导致论坛被挂马。我们发现在这一设置上,论坛管理员似乎相当随性。

例如,在腾讯游戏的论坛群([http://gamebbs.qq.com)上有近百个不同游戏的独立论坛,而这些论坛由于使用了不同的设置(有些按照Discuz](http://gamebbs.qq.com%EF%BC%89%E4%B8%8A%E6%9C%89%E8%BF%91%E7%99%BE%E4%B8%AA%E4%B8%8D%E5%90%8C%E6%B8%B8%E6%88%8F%E7%9A%84%E7%8B%AC%E7%AB%8B%E8%AE%BA%E5%9D%9B%EF%BC%8C%E8%80%8C%E8%BF%99%E4%BA%9B%E8%AE%BA%E5%9D%9B%E7%94%B1%E4%BA%8E%E4%BD%BF%E7%94%A8%E4%BA%86%E4%B8%8D%E5%90%8C%E7%9A%84%E8%AE%BE%E7%BD%AE%EF%BC%88%E6%9C%89%E4%BA%9B%E6%8C%89%E7%85%A7Discuz)!的默认设置关闭了flash标签),并不是都存在问题。经过我们测试,其中穿越火线、枪神纪、逆战、FIFA、地下城与勇士、全职大师、QQ华夏等游戏论坛,以及腾讯手机管家论坛都开启了flash标签,受到论坛挂马问题的威胁,而其他一些子论坛如英雄联盟等则不受影响。

**CF****论坛挂马**

           我们以其中的一个页面为例来看下——《[分享] 这是小概率还是大概率,我懵逼了》:



[![](https://p3.ssl.qhimg.com/t01163a1e8216c7e699.png)](https://p3.ssl.qhimg.com/t01163a1e8216c7e699.png)

           而在这个帖子的五楼,有位名为“大苏打干活”的网友向楼主表示祝贺:



[![](https://p0.ssl.qhimg.com/t0135dc99590e633e89.png)](https://p0.ssl.qhimg.com/t0135dc99590e633e89.png)

           是啊!楼主运气果然了得,不仅获得了有序里的虚拟道具,还在帖子里活得了一个网页挂马。不仅是楼主,连我们都“懵逼”了。

           拿到swf文件之后,内部的恶意脚本代码并没有加密,ShellCode一目了然:



[![](https://p4.ssl.qhimg.com/t01452707d66a0189db.png)](https://p4.ssl.qhimg.com/t01452707d66a0189db.png)

           一旦用户中招,flash文件会从远端地址下载一个木马到本地:



[![](https://p2.ssl.qhimg.com/t015a790d6b6c4153a2.png)](https://p2.ssl.qhimg.com/t015a790d6b6c4153a2.png)

           木马会读取自身内容并复制到system32目录下:



[![](https://p2.ssl.qhimg.com/t01d65ad8e68232c9a6.png)](https://p2.ssl.qhimg.com/t01d65ad8e68232c9a6.png)

           并将其加载为服务项



[![](https://p5.ssl.qhimg.com/t01bb72454e82235dea.png)](https://p5.ssl.qhimg.com/t01bb72454e82235dea.png)

           而后再创建一个“善后”的vbs脚本来打扫战场。



[![](https://p3.ssl.qhimg.com/t012580ede24f3c79b5.png)](https://p3.ssl.qhimg.com/t012580ede24f3c79b5.png)



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01aa2391f5f78737e7.png)

           而木马一旦被加载为服务项,就变成了一个典型的Gh0st远控,等待着远端的指令。



[![](https://p4.ssl.qhimg.com/t01ee71dc64c1dd5466.png)](https://p4.ssl.qhimg.com/t01ee71dc64c1dd5466.png)

同时沦陷的还是迅雷论坛(http://bbs.xunlei.com/)



[![](https://p1.ssl.qhimg.com/t01fa3b436503213cc3.png)](https://p1.ssl.qhimg.com/t01fa3b436503213cc3.png)

而从挂马手法来看,很可能是同一个团伙所为,我们在《从果粉到黑吃黑:一个论坛挂马的奇异反转》([http://blogs.360.cn/360safe/2016/04/28/xiaoqi_forum_web_trojan/](http://blogs.360.cn/360safe/2016/04/28/xiaoqi_forum_web_trojan/))中,对这个挂马团伙做了分析。

**新****Flash****挂马类型**

           此外,这一波挂马中还出现了一批新型的挂马——刷流量Flash挂马。在大众论坛中,就看到了这样一个木马三连发的网友,其中第一个挂马和上面CF论坛是一样的,不再赘述。而后面两个回复中挂的,则是两个颇为新颖的挂马类型:



[![](https://p4.ssl.qhimg.com/t011c7d50b67f06f517.png)](https://p4.ssl.qhimg.com/t011c7d50b67f06f517.png)



[![](https://p3.ssl.qhimg.com/t01a1231c47fc6e18a0.png)](https://p3.ssl.qhimg.com/t01a1231c47fc6e18a0.png)

这两个swf文件严格的说并没有利用任何漏洞,而是很单纯的在flash文件中插入了一个“合法”的脚本:



[![](https://p0.ssl.qhimg.com/t0130fc1705e8695f07.png)](https://p0.ssl.qhimg.com/t0130fc1705e8695f07.png)



[![](https://p5.ssl.qhimg.com/t012245960cd82dc3af.png)](https://p5.ssl.qhimg.com/t012245960cd82dc3af.png)

           用户一旦访问了含有这两个Flash文件的页面,便会在后台静默的访问两个列表中的所有网站……

我们同时发现,另一流行论坛建站系统phpwind也受到该问题的影响,注册用户也可以在论坛主题和回帖中贴入直接播放的任意flash文件,导致挂马攻击的方式。

由于目前Flash漏洞的泛滥,360安全中心建议目前使用允许直接嵌入flash文件的各大论坛站点,尽快关闭Flash嵌入功能,同时建议Discuz!等论坛厂商,加入对嵌入Flash标签的“白名单”功能。对于普通用户,除了及时升级Flash版本外,安装360安全卫士并开启防护,也是在浏览论坛的同时保护自己的重要措施。
