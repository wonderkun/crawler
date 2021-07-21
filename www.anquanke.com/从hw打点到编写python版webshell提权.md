> 原文链接: https://www.anquanke.com//post/id/242573 


# 从hw打点到编写python版webshell提权


                                阅读量   
                                **542316**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t011dde4ccb9a1d9297.jpg)](https://p2.ssl.qhimg.com/t011dde4ccb9a1d9297.jpg)



摸到一个某信息管理平台

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012fa562ebc07d3f39.png)

[![](https://p5.ssl.qhimg.com/t01845defc90750fb59.jpg)](https://p5.ssl.qhimg.com/t01845defc90750fb59.jpg)

开局一个登录框，那么尝试sql注入和弱口令爆破，从返回包中可以看出存在用户名枚举

[![](https://p3.ssl.qhimg.com/t01d5e6295ff3a4f03d.png)](https://p3.ssl.qhimg.com/t01d5e6295ff3a4f03d.png)

尝试注入测试发现后端存在检测，试了几十个常见的测试手机号还无法枚举到用户名后，遂放弃此路

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01308abca986e306b2.jpg)

通过报错页面的信息，和url格式，我当时判断的是这是一个 java mvc模型的站点，也给后面埋了个坑

[![](https://p4.ssl.qhimg.com/t01f127060947434379.png)](https://p4.ssl.qhimg.com/t01f127060947434379.png)

于是开始翻看静态资源，熟悉的文件名格式，确认过眼神，这是vue的资源

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b43e81f87b0291a5.png)

根据以往的经验，VUE项目的关键代码存在于生成的以app开头的js文件中，所以通常遇到vue项目的目标，只需翻看其app开头的js文件，即可通过其内容大致了解到它的功能点。

[![](https://p0.ssl.qhimg.com/t01fd59b50cacd00a2f.png)](https://p0.ssl.qhimg.com/t01fd59b50cacd00a2f.png)

于是打开那个app开头的js文件，我个人是非常喜欢将js代码粘贴到Pycharm里面，然后按 Ctrl + Alt + L 来格式化代码，再慢慢的审阅寻找线索。

经过仔细的查看js代码，发现一处疑似后台主页的跳转url

[![](https://p1.ssl.qhimg.com/t01479a734b65ab99a1.png)](https://p1.ssl.qhimg.com/t01479a734b65ab99a1.png)

直接粘贴至浏览器打开，进到了一个后台页面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e202bb6a4c7a2d3c.png)

在熟悉它里面的功能点时，发现这只是一个框架页面，跟后端交互获取数据时仍需要验证用户身份

于是我灵机一动，猜测 url的company_id提交的可能就是用户凭证，所以直接在Pycharm使用字符串查找功能查找，没想到真的找到了一串md5值，看起来像是凭证，大喜之后将其补上到url后再访问

[![](https://p5.ssl.qhimg.com/t01aca7d20b6430cbf0.png)](https://p5.ssl.qhimg.com/t01aca7d20b6430cbf0.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017d0fe81a7c152466.jpg)

获得了一个用户身份的后台（看右边的成员和部门那里已经与前面不同）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010b3becfdd3050ca5.png)

但继续摸功能点后，发现只是个测试用户的身份

[![](https://p2.ssl.qhimg.com/t0158b48c021b2e47b8.png)](https://p2.ssl.qhimg.com/t0158b48c021b2e47b8.png)

找到一处上传点，但是上传过去发现没有数据包响应

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e08a1af724211f03.png)

于是查看浏览器控制台信息，发现是被同源策略给限制了，那么这里通过功能点直接上传是行不通的，除非你通过他的域名访问，我这里反查了ip查不到对应的域名

[![](https://p5.ssl.qhimg.com/t01970b2fb3861a65ae.png)](https://p5.ssl.qhimg.com/t01970b2fb3861a65ae.png)

这个时候可以手动构造文件上传表单， 然后浏览器打开上传

[![](https://p3.ssl.qhimg.com/t01c41c58480091b57b.png)](https://p3.ssl.qhimg.com/t01c41c58480091b57b.png)

发包过去之后，是我天真了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013097e2348132aada.png)

报了一个404回来，开始怀疑人生当中，不过后面想了想，我刚才访问的是82端口，提交上传的接口是8082端口，难不成这里面有问题？本着死磕到底的精神，我颤抖的手敲了敲键盘，在burp的重放功能那将8082端口改为了82端口，再尝试发包

[![](https://p3.ssl.qhimg.com/t01eb2bf44f33e46464.jpg)](https://p3.ssl.qhimg.com/t01eb2bf44f33e46464.jpg)

回包果真不一样了，貌似是被后端接受了，但是却没有返回上传成功的文件路径，我怀疑是没有上传成功

[![](https://p3.ssl.qhimg.com/t01c701639633e61d97.png)](https://p3.ssl.qhimg.com/t01c701639633e61d97.png)

于是掏出了我的大*，不对，是我的祖传字典，用于测试上传文件对象的键名

[![](https://p0.ssl.qhimg.com/t01ffaea6b8dcd92fdd.png)](https://p0.ssl.qhimg.com/t01ffaea6b8dcd92fdd.png)

我晕，原来上传的文件对象键名就是 file

[![](https://p1.ssl.qhimg.com/t01031e9b222a2868d0.png)](https://p1.ssl.qhimg.com/t01031e9b222a2868d0.png)

将文件字典键名改为file, 文件名改为 .jsp后缀再上传，成功上传了

[![](https://p0.ssl.qhimg.com/t01d1427d7735069613.png)](https://p0.ssl.qhimg.com/t01d1427d7735069613.png)

于是赶紧上传个冰蝎的webshell,发现被拦了，难不成存在waf ？

[![](https://p3.ssl.qhimg.com/t0154aa9654fe8025d4.png)](https://p3.ssl.qhimg.com/t0154aa9654fe8025d4.png)

[![](https://p4.ssl.qhimg.com/t01f5c5a7c288493783.jpg)](https://p4.ssl.qhimg.com/t01f5c5a7c288493783.jpg)

那么先上传个打印字符串的短小代码，发现上传成功了也顺利访问了可是却不解析？？？

[![](https://p0.ssl.qhimg.com/t013e9199b928af1675.png)](https://p0.ssl.qhimg.com/t013e9199b928af1675.png)

我尼玛直接怀疑人生，这不是tomcat应用服务器吗，怎么可能不解析jsp

[![](https://p5.ssl.qhimg.com/t01598a05f0934ede43.jpg)](https://p5.ssl.qhimg.com/t01598a05f0934ede43.jpg)

后面在测试其他文件名时，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f2c2bb7fd0f7c030.png)

发现解析php，这就离谱，tomcat + php还有这种搭配？麻烦搞懂的朋友告诉我

[![](https://p2.ssl.qhimg.com/t01f46831e525d608c6.png)](https://p2.ssl.qhimg.com/t01f46831e525d608c6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f1547a15f8b26554.jpg)

蚁剑链接之，发现是 apache权限，内核3.10

[![](https://p4.ssl.qhimg.com/t01c3e9fe49b407d852.png)](https://p4.ssl.qhimg.com/t01c3e9fe49b407d852.png)

其实这个时候通常都是上代理打内网的了，不过后面遇到了更诡异的事，我上传了frp 客户端做代理时，发现连接到服务端后几十秒就断了，再查看文件时，权限已经变成了 000

[![](https://p3.ssl.qhimg.com/t0110342ee49982c6f2.png)](https://p3.ssl.qhimg.com/t0110342ee49982c6f2.png)

看来是应该有某种防护软件？这是块硬骨头啊

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0138e0ab1b50fa74a6.jpg)

然后开始打算提权，一般提权通用性比较高的就是内核提权，但是不太建议这种提权方式，因为溢出类的内核提权都有一定的偶然性，容易把服务器打宕机

查看了下进程，很惊喜的发现python 以root权限运行了一个程序，有着django开发经验的我一眼就看出了这就是django,

[![](https://p3.ssl.qhimg.com/t01cdb93bb72f1f6ea1.png)](https://p3.ssl.qhimg.com/t01cdb93bb72f1f6ea1.png)

然后访问其8000端口，是一个 swagger 接口页面。

[![](https://p4.ssl.qhimg.com/t012ff8ab20a141830e.png)](https://p4.ssl.qhimg.com/t012ff8ab20a141830e.png)

这时随便访问个不存在的路由

[![](https://p3.ssl.qhimg.com/t01f91261677e73de6c.png)](https://p3.ssl.qhimg.com/t01f91261677e73de6c.png)

通过报错信息得知这真的是django，并且开起了debug功能，开启后修改源代码会自动重启应用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a60ca47cc9f2522d.gif)

心中大喜直接奔去寻找这个django项目的目录，很巧的是项目目录里的所有文件都具有777的权限，所以能改写视图函数，我添加了红框中的代码，大致意思就是当访问 test/ 路由时，返回字符串 “Hello Django”

[![](https://p1.ssl.qhimg.com/t01a1a02797a027b33d.png)](https://p1.ssl.qhimg.com/t01a1a02797a027b33d.png)

再去浏览器访问 test 路由，成功执行了我自定义的视图函数

[![](https://p0.ssl.qhimg.com/t011f7ceefdeb305e1e.png)](https://p0.ssl.qhimg.com/t011f7ceefdeb305e1e.png)

于是这时候 python 版的webshell就出来了

[![](https://p5.ssl.qhimg.com/t01cb1bb3b01b5deef4.png)](https://p5.ssl.qhimg.com/t01cb1bb3b01b5deef4.png)

去查看执行效果，ok提权成功

[![](https://p2.ssl.qhimg.com/t013ca28df89454c780.png)](https://p2.ssl.qhimg.com/t013ca28df89454c780.png)

当我开始漫游时，问题又出现了，应该是流量特征太明显被 waf 拦了

[![](https://p2.ssl.qhimg.com/t01009c7c106dc77a3f.png)](https://p2.ssl.qhimg.com/t01009c7c106dc77a3f.png)

[![](https://p5.ssl.qhimg.com/t0199cada168a561975.jpg)](https://p5.ssl.qhimg.com/t0199cada168a561975.jpg)

然后我又把视图函数改了下，添加base64编码传输

[![](https://p3.ssl.qhimg.com/t01d6d9537ffac4c65c.png)](https://p3.ssl.qhimg.com/t01d6d9537ffac4c65c.png)

完美

[![](https://p1.ssl.qhimg.com/t0119b098262cfef8cd.png)](https://p1.ssl.qhimg.com/t0119b098262cfef8cd.png)

随便几行代码写了个方便点的利用工具

[![](https://p1.ssl.qhimg.com/t0174a8b3b067db0c24.png)](https://p1.ssl.qhimg.com/t0174a8b3b067db0c24.png)

本次外网打点到此结束，如有打码不严请勿复现

[![](https://p4.ssl.qhimg.com/t01516834b2c0047282.png)](https://p4.ssl.qhimg.com/t01516834b2c0047282.png)
