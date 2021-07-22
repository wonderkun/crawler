> 原文链接: https://www.anquanke.com//post/id/83218 


# 再说VS竞技游戏平台的那些事


                                阅读量   
                                **111574**
                            
                        |
                        
                                                                                    



        你或许还记得我们今年9月份时发的这篇博客:《[VS竞技游戏平台刷流量木马说明](http://blogs.360.cn/360safe/2015/09/24/about_flow_trojan_in_vs_game_platform/)》,惊闻VS竞技游戏平台的母公司“广州唯思软件股份有限公司”最近挂牌上市了。<br>

[![](https://p4.ssl.qhimg.com/t015b6d6b421dffcec1.png)](http://blogs.360.cn/360safe/files/2015/12/01%E4%B8%8A%E5%B8%82.png)

        照理说公司挂牌上市了,意味着要面对更大的市场,要对更多的投资者负责,做事也该更谨慎些。于是我就想看看,之前的刷流量问题是否已经有所收敛了。于是我又从官网下载了一个最新的客户端回来做了个测试:<br>

[![](https://p3.ssl.qhimg.com/t010d9abd58d4fae19a.png)](http://blogs.360.cn/360safe/files/2015/12/02%E5%AE%89%E8%A3%85%E5%8C%85.png)**        **

**        00000000b 再试VS平台**<br>

        其实再试的心情还是很复杂的,还是希望这个曾在自己大学期间令我们废寝忘食的游戏平台能回归到往日的天真。无惊无险的安装之后,我登录了自己多年未曾登陆的一个小号,仿佛是又回到了那个“网吧五连坐,从来没赢过”的年代:<br>

[![](https://p2.ssl.qhimg.com/t014d4c4593a7dd33cc.png)](http://blogs.360.cn/360safe/files/2015/12/04%E7%99%BB%E5%BD%95.png)        但就在这时,一个大大的浏览器窗口把我拉回了现实————这个浏览器是什么鬼……<br>

[![](https://p2.ssl.qhimg.com/t0153fe96cfac9e0b70.png)](http://blogs.360.cn/360safe/files/2015/12/03%E5%AE%89%E8%A3%85720%E6%B5%8F%E8%A7%88%E5%99%A8.png)

<br>

**        00000001b 原来天真的只有我**

        看到了这个从来未见过的浏览器我便明白了这些年来天真的其实只有我而已……而VS,比起3个月前的那个VS,有过之而无不及……先说安装包,功能明显就增加了。揭开了这个NSIS安装包的安装脚本,平心而论还是很简单干净的。没有什么奇技淫巧在里面,只是干干净净的把VS平台的文件连带着720浏览器的文件简简单单大大方方的释放到了一个合适的位置上而已:<br>

[![](https://p1.ssl.qhimg.com/t0161ccfc1ebfd625a1.png)](http://blogs.360.cn/360safe/files/2015/12/06%E5%AE%89%E8%A3%85720%E6%B5%8F%E8%A7%88%E5%99%A8.png)

        如果至此打住,那也仅算是搞搞裙带关系而已。但随着测试的深入,上次分析中提到的刷流量的元凶再一次的出现在我们的视野里。<br>        书接上回,上文书我们说到VS竞技游戏平台下了个resource.exe回来释放刷流量木马后台静默刷流量:<br>

[![](https://p1.ssl.qhimg.com/t012f58c27e7beb4611.png)](http://blogs.360.cn/360safe/files/2015/09/009_%E5%85%B3%E7%B3%BB.png)

        显然,劳苦功高的resource.exe现在的工作更加繁忙了。下载的文件也多了:<br>

[![](https://p2.ssl.qhimg.com/t014c65f9a6d3103bea.png)](http://blogs.360.cn/360safe/files/2015/12/07%E4%B8%8B%E8%BD%BD.png)

        resource.exe把下回来的文件都堆在了%APPDATA%fx目录下,我们先来张合影————1、2、3,茄子~~~<br>

[![](https://p5.ssl.qhimg.com/t0181de056eb36f8ba1.png)](http://blogs.360.cn/360safe/files/2015/12/09%E5%90%88%E5%BD%B1.png)

**        **

**        00000010b 逐个说明<strong style="font-weight: bold">**</strong>**<br>**

**        a) config.ini**<br>

        先看看最简单的config.ini,明文文本文件,给大家看看内容相信大家也就都懂了。<br>

[![](https://p5.ssl.qhimg.com/t01b7b6a1a917c2d75d.png)](http://blogs.360.cn/360safe/files/2015/12/08config.png)

**        b) dwm.exe和dvdata.dll******<br>        dwm.exe其实就是个loader,负责加载dvdata.dll。而dvdata.dll的三个导出函数:MyStart负责调用StartGameTask函数,StartGameTask负责获取配置文件和上传用户信息,StartGameTaskLine则负责刷流量。具体的分析前文书中已经交代过这里也不必赘述。<br>**        c) vrunner.exe和mini.dll**<br>        vrunner.exe和上面的dwm.exe类似,也是一个loader,运行后便加载mini.dll并获取StopDoingTask函数。<br>

[![](https://p2.ssl.qhimg.com/t01b940fc7cd9f9b70a.png)](https://p2.ssl.qhimg.com/t01b940fc7cd9f9b70a.png)

[![](https://p3.ssl.qhimg.com/t014c21065e74a2df3e.png)](http://blogs.360.cn/360safe/files/2015/12/11-Get-StopDoingTask.png)

        而这个函数的作用仅仅是向服务器发送一个打点记录信息而已<br>

[![](https://p4.ssl.qhimg.com/t01829bae63ed3e7901.png)](http://blogs.360.cn/360safe/files/2015/12/12-mini_internetopen.png)

[![](https://p3.ssl.qhimg.com/t018510266e3245585c.png)](http://blogs.360.cn/360safe/files/2015/12/13-mini_HTTP%E6%89%93%E7%82%B9.png)

        而同时,mini.dll的另一个函数StartWebTask也会被调用<br>

[![](https://p1.ssl.qhimg.com/t01abd28ae537a5cc89.png)](http://blogs.360.cn/360safe/files/2015/12/14-mini_StartWebTask.png)

        同样也有一个打点访问<br>

[![](https://p1.ssl.qhimg.com/t01a7e3ec5c1ce905bb.png)](http://blogs.360.cn/360safe/files/2015/12/15-mini_InternetConnect.png)

[![](https://p1.ssl.qhimg.com/t01fedad7e9e0ebfaeb.png)](http://blogs.360.cn/360safe/files/2015/12/16-mini_Request.png)

        另外,还会获取一个config配置文件,作用很简单————弹出广告窗口<br>

[![](https://p1.ssl.qhimg.com/t01a336ed5df67f1372.png)](http://blogs.360.cn/360safe/files/2015/12/17-mini_Request_config.png)

[![](https://p4.ssl.qhimg.com/t0124395ab997e97080.png)](http://blogs.360.cn/360safe/files/2015/12/18-mini_ShowWind.png)

**d) room.exe******<br>        room.exe是一个执行任务的坚挺进程,根据在线的任务列表,通过解析JSON数据来执行指定的任务<br>

[![](https://p5.ssl.qhimg.com/t013b490fd98bcd7e9a.png)](http://blogs.360.cn/360safe/files/2015/12/20-room_url.png)

[![](https://p4.ssl.qhimg.com/t01122110b2c7d421a4.png)](http://blogs.360.cn/360safe/files/2015/12/21-room_parse.png)

        当前返回的task内容如下:<br>

[![](https://p0.ssl.qhimg.com/t01de94907a8f0f073d.png)](http://blogs.360.cn/360safe/files/2015/12/19-room_task.png)

        由此可见,目前的任务是在VSClient.exe进程退出之后去打开指定的网页来实现刷广告(目前打开的是VS自己的网站)。<br>**        e) svchost.exe**<br>        最后说这个svchost.exe,是因为实在是从“面相”上看就实在让人无法不怀疑他的身份……而其代码也是非常的切合其身份。<br>

[![](https://p2.ssl.qhimg.com/t01412846d2eff9e04e.png)](http://blogs.360.cn/360safe/files/2015/12/22-svchost-urls.png)        这只是些下载地址而已,而真正下载的又是些什么呢?<br>

[![](https://p1.ssl.qhimg.com/t0103a7cfc8b6a6cc74.png)](http://blogs.360.cn/360safe/files/2015/12/30-svchost-360chrome.png)

[![](https://p4.ssl.qhimg.com/t01376ca34f0a1a098a.png)](http://blogs.360.cn/360safe/files/2015/12/31-svchost-360se.png)

[![](https://p5.ssl.qhimg.com/t0154856c4bb42cc9f9.png)](http://blogs.360.cn/360safe/files/2015/12/32-svchost-liebao.png)

[![](https://p1.ssl.qhimg.com/t01411236d3bdb948bb.png)](http://blogs.360.cn/360safe/files/2015/12/33-svchost-chrome.png)

[![](https://p2.ssl.qhimg.com/t013f16f84962589b0d.png)](http://blogs.360.cn/360safe/files/2015/12/34-svchost-tw.png)

[![](https://p2.ssl.qhimg.com/t0194bb3745dcfd3cf1.png)](http://blogs.360.cn/360safe/files/2015/12/35-svchost-ff.png)

        看到了好多浏览器的名字,作用其实很简单,**替换系统现有浏览器的主程序,而其自身的功能也很简单————加网址参数调用原本的浏览器主程序达到改首页的目的,很难相像,国内一家上市公司,会通过这种恶劣而又低技术的手法来劫持用户浏览器。**并且劫持的这些文件并没有打“Guangzhou WeiSi Software CO.,ltd”的签名,而之前作恶的程序都是带有这个签名的,显然是做了坏事怕被人发现。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](http://blogs.360.cn/360safe/files/2015/12/QQ%E6%88%AA%E5%9B%BE20151231102333.jpg)

[![](https://p4.ssl.qhimg.com/t0190ba318dc006b6e6.png)](http://blogs.360.cn/360safe/files/2015/12/40-svchost-%E6%9B%BF%E6%8D%A2.png)        当然,最简单粗暴的手段也是用了的。来,再张合影,1、2、3,前妻,呃,不对,田七~~~~~<br>

[![](https://p1.ssl.qhimg.com/t01995dd89742f44411.png)](http://blogs.360.cn/360safe/files/2015/12/05%E6%94%B9%E9%A6%96%E9%A1%B5%E5%A4%A7%E5%90%88%E5%BD%B1.png)

**        ****00000011b 能力越大责任越大**

With gread power comes great responsibility!作为一家上市公司,目的不该是上市圈钱,而应该是肩负了更大的责任,尽力与广大的股民实现共赢。刷着流量、推广浏览器、点击网页广告、用各种办法篡改浏览器的首页……这真的该是一家上市公司该有的作为么?还请三思吧…        …
