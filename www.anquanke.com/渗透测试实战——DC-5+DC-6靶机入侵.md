> 原文链接: https://www.anquanke.com//post/id/178958 


# 渗透测试实战——DC-5+DC-6靶机入侵


                                阅读量   
                                **345544**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t019ecca362b738b02d.jpg)](https://p4.ssl.qhimg.com/t019ecca362b738b02d.jpg)



## 前言

hello，大家好！爱写靶机文章的我又来了…最近工作忙到飞起，根本没空忙自己的事情..所以迟迟没有更新，这次给大家带来的是DC-5、DC-6的靶机wp，本来准备把 DC-2-DC-4的一起写的，结果发现已经有小伙伴抢先写了



## 靶机下载/安装

DC-5: [http://www.five86.com/dc-5.html](http://www.five86.com/dc-5.html)

DC-6: [http://www.five86.com/dc-6.html](http://www.five86.com/dc-6.html)

[![](https://p4.ssl.qhimg.com/t01351a978df3aefbc6.png)](https://p4.ssl.qhimg.com/t01351a978df3aefbc6.png)

[![](https://p0.ssl.qhimg.com/t01b205743db491f2c2.png)](https://p0.ssl.qhimg.com/t01b205743db491f2c2.png)



## 实战

### <a class="reference-link" name="DC-5"></a>DC-5

老规矩探测一下靶机 IP

[![](https://p4.ssl.qhimg.com/t012cc8049a951f16b8.png)](https://p4.ssl.qhimg.com/t012cc8049a951f16b8.png)

下一步nmap探测一下端口开放情况，

[![](https://p3.ssl.qhimg.com/t0141bc72925a6fb113.png)](https://p3.ssl.qhimg.com/t0141bc72925a6fb113.png)

可以看到靶机开放了3个端口，分别是 80、111、50614

我们还是先看看 80端口

[![](https://p5.ssl.qhimg.com/t011d6a1c15a54ea52b.png)](https://p5.ssl.qhimg.com/t011d6a1c15a54ea52b.png)

可以看到非常简单的几个页面，还是一样用目录拆解工具跑一波，小弟这里使用的是gobuster

[![](https://p2.ssl.qhimg.com/t018f33f3a696d4d230.png)](https://p2.ssl.qhimg.com/t018f33f3a696d4d230.png)

小弟刚开始的时候就草草的看了一下，但是没发现什么，就把目光盯在111端口的 rpc服务上了，以为靶机是通过挂在盘解的，然后试了一下看了一下感觉不对，没什么进展。然后又重新跑了一遍目录，重新开始查看跑出来的结果，查看 /footer.php，如图

[![](https://p3.ssl.qhimg.com/t01036c46300f186fa9.png)](https://p3.ssl.qhimg.com/t01036c46300f186fa9.png)

发现每次访问这个后面的年份都会改变，如图：

[![](https://p4.ssl.qhimg.com/t011e3d6c25944b1468.png)](https://p4.ssl.qhimg.com/t011e3d6c25944b1468.png)

[![](https://p1.ssl.qhimg.com/t0195857760d64a0428.png)](https://p1.ssl.qhimg.com/t0195857760d64a0428.png)

然后在查看 /thankyou.php 文件时，发现了这个

[![](https://p3.ssl.qhimg.com/t01eee4a2e29a55e98c.png)](https://p3.ssl.qhimg.com/t01eee4a2e29a55e98c.png)

可以看到该php在底部直接调用了/footer.php，

（注：这里是直接调用，不是写在底部，因为跟 上面一样，每次访问年份都在变化。）

应该是使用php的 ‘include()’ 函数来包含了 ‘footer.php’ 文件，这样直接导致了LFI漏洞，下面我们来测试一下漏洞是否真的存在和看一下是否会过滤包含进来的文件，<br>
如图：

[![](https://p3.ssl.qhimg.com/t012c657b060488c99b.png)](https://p3.ssl.qhimg.com/t012c657b060488c99b.png)

可以看到的确存在该漏洞并且没有过滤包含进来的内容，下面我们怎么通过LFI漏洞拿shell呐？

通过第一步的端口探测中可以看到，该web服务使用的是nginx服务，大家都知道我们在网站上的每一步操作都是会被写入log文件内的，那么我们就可以通过log来拿 shell，

操作如下：

**第一步**

[![](https://p2.ssl.qhimg.com/t01139666927716e6b9.png)](https://p2.ssl.qhimg.com/t01139666927716e6b9.png)

随意写入个get的cmdshell

代码为：&lt;?php passthru($_GET[‘cmd’]); ?&gt;

**第二步**

直接包含nginx log的地址就行

[![](https://p2.ssl.qhimg.com/t019ed18212893e1f99.png)](https://p2.ssl.qhimg.com/t019ed18212893e1f99.png)

这个地址是Linux默认的

最后一步，我们带上cmd命令

[![](https://p3.ssl.qhimg.com/t01d03ef6d5e6372356.png)](https://p3.ssl.qhimg.com/t01d03ef6d5e6372356.png)

本次使用命令是连接攻击者电脑的5555端口

[![](https://p5.ssl.qhimg.com/t0181a8f74245fa55e7.png)](https://p5.ssl.qhimg.com/t0181a8f74245fa55e7.png)

成功拿到webshell

参考地址：[https://roguecod3r.wordpress.com/2014/03/17/lfi-to-shell-exploiting-apache-access-log/](https://roguecod3r.wordpress.com/2014/03/17/lfi-to-shell-exploiting-apache-access-log/)

下一步我们就是提权了，老规矩 在/tmp目录下上提权辅助脚本

[![](https://p5.ssl.qhimg.com/t0112742d53e488bd1a.png)](https://p5.ssl.qhimg.com/t0112742d53e488bd1a.png)

跑完以后发现了一个熟悉的面孔。。。

[![](https://p0.ssl.qhimg.com/t01c12508ad941415d9.png)](https://p0.ssl.qhimg.com/t01c12508ad941415d9.png)

screen 前段时间在某个环境上看到过，并且也通过其提权成功了，下面我们也使用该程序完成提权工作吧，

搜索 screen，找到了 利用程序

地址：[https://www.exploit-db.com/exploits/41154](https://www.exploit-db.com/exploits/41154)

[![](https://p5.ssl.qhimg.com/t014e749f1d837dcc00.png)](https://p5.ssl.qhimg.com/t014e749f1d837dcc00.png)

但是这个脚本直接执行是出错的，我们需要完成以下几个工作

第一步

把该bash文件的上面一部分c语言代码单独复制出来，如图

[![](https://p4.ssl.qhimg.com/t01d634bd84976999df.png)](https://p4.ssl.qhimg.com/t01d634bd84976999df.png)

然后在本地编译它，编译命令 .sh里有

“gcc -fPIC -shared -ldl -o /tmp/libhax.so /tmp/libhax.c”

第二步

把下面一个c语言 代码也单独复制出来编

[![](https://p2.ssl.qhimg.com/t0142e11a25765f62ed.png)](https://p2.ssl.qhimg.com/t0142e11a25765f62ed.png)

命令：“gcc -o /tmp/rootshell /tmp/rootshell.c”

第三步

修改原来的那个bash文件，如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01999f0864f35f3cf0.png)

最后把这3个文件全部都上传到靶机上面，如图

[![](https://p1.ssl.qhimg.com/t01ff5e32e1be3a3169.png)](https://p1.ssl.qhimg.com/t01ff5e32e1be3a3169.png)

然后执行该bash，发现出错。

[![](https://p2.ssl.qhimg.com/t01751535d4211b27a4.png)](https://p2.ssl.qhimg.com/t01751535d4211b27a4.png)

最后通过搜索发现是因为 该sh开发作者是使用 Windows环境 开发，

用vi打开该sh文件，使用 :set ff=unix 保存，即可解决该问题

参考地址：[https://blog.csdn.net/ooooooobh/article/details/82766547](https://blog.csdn.net/ooooooobh/article/details/82766547)

最后 成功拿到root权限，如图

[![](https://p4.ssl.qhimg.com/t01fa94b3a3809bfc66.png)](https://p4.ssl.qhimg.com/t01fa94b3a3809bfc66.png)

拿到flag

[![](https://p4.ssl.qhimg.com/t0168896245239935fb.png)](https://p4.ssl.qhimg.com/t0168896245239935fb.png)



### <a class="reference-link" name="DC-6"></a>DC-6

老规矩，探测靶机IP

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01db6d0f1cfdf7bdfa.png)

下一步探测 靶机端口 开放情况，如图

[![](https://p4.ssl.qhimg.com/t016d5b3ab206c6a80c.png)](https://p4.ssl.qhimg.com/t016d5b3ab206c6a80c.png)

可以看到 [http://wordy/](http://wordy/)

我们添加一下hosts文件

[![](https://p3.ssl.qhimg.com/t01f97010f363e61463.png)](https://p3.ssl.qhimg.com/t01f97010f363e61463.png)

访问如图：

[![](https://p3.ssl.qhimg.com/t01654d0cf32be460d1.png)](https://p3.ssl.qhimg.com/t01654d0cf32be460d1.png)

通过上图，可以很明显的看出是个wp，

不用 怀疑，

直接使用wpscan —url [http://wordy/](http://wordy/) -e

查找网站 上的所有用户

[![](https://p0.ssl.qhimg.com/t015a7e6534174f380d.png)](https://p0.ssl.qhimg.com/t015a7e6534174f380d.png)

[![](https://p5.ssl.qhimg.com/t018ffee739cb353f31.png)](https://p5.ssl.qhimg.com/t018ffee739cb353f31.png)

保存 用户

[![](https://p5.ssl.qhimg.com/t011f02207b9ff8fdda.png)](https://p5.ssl.qhimg.com/t011f02207b9ff8fdda.png)

下一步根据上面下载地址处作者的提示，我们生产一个字典包

[![](https://p3.ssl.qhimg.com/t010103bac28c95ce72.png)](https://p3.ssl.qhimg.com/t010103bac28c95ce72.png)

就这样一条小命令，让我们省去了几年的爆破时间，我真的是谢谢你全家啊 哈哈哈哈

[![](https://p5.ssl.qhimg.com/t0185f4114c3dd998f5.png)](https://p5.ssl.qhimg.com/t0185f4114c3dd998f5.png)

下一步直接爆破 其web账户把

[![](https://p2.ssl.qhimg.com/t01acb18df3a15c3a7d.png)](https://p2.ssl.qhimg.com/t01acb18df3a15c3a7d.png)

小等一会，成功破解出来了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b695bf519f0ed4d0.png)

账户 mark – helpdesk01

成功登陆后台，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0165e429d77e58379c.png)

但是因为是普通用户权限，无法直接写shell，我们继续看看

然后发现了这个，

[![](https://p4.ssl.qhimg.com/t01ea48083b590978ba.png)](https://p4.ssl.qhimg.com/t01ea48083b590978ba.png)

通过搜索，发现其有一个csrf的漏洞

[![](https://p4.ssl.qhimg.com/t01f8dfede649c1d650.png)](https://p4.ssl.qhimg.com/t01f8dfede649c1d650.png)

地址：[https://www.exploit-db.com/exploits/45274](https://www.exploit-db.com/exploits/45274)

我们直接复制html进行修改

[![](https://p5.ssl.qhimg.com/t01c75783eb18880bb0.png)](https://p5.ssl.qhimg.com/t01c75783eb18880bb0.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011d7c486342b7c34c.png)

但是改完以后怎么样都无法成功弹shell，

然后小弟就搜索该cve号，找到一篇复现文章，地址：[https://github.com/aas-n/CVE/blob/6079ec210cef36d7632dde411b3e611a2de99b43/CVE-2018-15877/README.md](https://github.com/aas-n/CVE/blob/6079ec210cef36d7632dde411b3e611a2de99b43/CVE-2018-15877/README.md)

测试如图：

[![](https://p2.ssl.qhimg.com/t01809afd6ddd0ff622.png)](https://p2.ssl.qhimg.com/t01809afd6ddd0ff622.png)

可以看到漏洞说的确存在的，那么我们下一步就弹shell吧

[![](https://p3.ssl.qhimg.com/t01502b9edb04aa9e59.png)](https://p3.ssl.qhimg.com/t01502b9edb04aa9e59.png)

成功拿到了shell，

下面我们进行进一步操作

[![](https://p4.ssl.qhimg.com/t01f8841021ed24f3df.png)](https://p4.ssl.qhimg.com/t01f8841021ed24f3df.png)

拿到账号密码

graham : GSo7isUM1D4

我们使用拿到的账号密码登陆ssh

[![](https://p0.ssl.qhimg.com/t01238d704f65222c34.png)](https://p0.ssl.qhimg.com/t01238d704f65222c34.png)

下面提权

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e1ca726a45ed1e5c.png)

可以看到 “backups.sh” 不需要密码，即可修改

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0119d6ea185c1cbd8a.png)

这里下一步，相信看过小弟前面的文章的小伙伴就知道怎么操作了，我这里也就不详细说了，操作如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0171984dd24b5e3336.png)

到了这里我们还不是root权限，下面我们继续提权，如图

[![](https://p5.ssl.qhimg.com/t01ca228d2d9f896482.png)](https://p5.ssl.qhimg.com/t01ca228d2d9f896482.png)

可以看到其有安装nmap，且为root权限，无需密码

这里的绕过方法如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e9ab94ef547ae79a.png)

先写一个nmap插件nse，如上图

下面只需要nmap加载其就可以，如图

[![](https://p2.ssl.qhimg.com/t010cb4f429e107d9fd.png)](https://p2.ssl.qhimg.com/t010cb4f429e107d9fd.png)

下面拿flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011e9cdf3079be01a3.png)

本靶机完！



## 结语

希望您也能不看文章自己实战一下。祝您及家人身体健康，感谢观看！
