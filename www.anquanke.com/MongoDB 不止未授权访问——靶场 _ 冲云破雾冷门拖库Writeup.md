> 原文链接: https://www.anquanke.com//post/id/95844 


# MongoDB 不止未授权访问——靶场 | 冲云破雾冷门拖库Writeup


                                阅读量   
                                **209565**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">11</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t019e9932cef3a795c8.jpg)](https://p4.ssl.qhimg.com/t019e9932cef3a795c8.jpg)

## 0x00 前戏

这是一个玩起来相当有意思的靶场，不需要太刁钻的姿势，主要考验的是逻辑推理能力和细节观察能力，漏洞场景常见，却又不能拿扫描器盲扫，还原的时候深度研究了下nosql，尽量真实的还原了企业的漏洞事件。为了增加体验的乐趣，在剧情上也加了点草料，让大家渗透的同时不失边角乐趣。

还没有玩过这个靶场的同学可以先去 [这里](https://pockr.org/bug-environment/detail?environment_no=env_75b82b98ffedbe0035) 体验一番再来看writeup。

**先爆一组数据**

从元旦开放靶场到现在，上线刚好20天，凭票入场人数120…

[![](https://p1.ssl.qhimg.com/t01faa662cdaceda1e7.png)](https://p1.ssl.qhimg.com/t01faa662cdaceda1e7.png)

从日志统计来看，靶场入口处UV1404个

[![](https://p3.ssl.qhimg.com/t01df922c3408d9bf30.jpg)](https://p3.ssl.qhimg.com/t01df922c3408d9bf30.jpg)

渗透到靶场「puokr内部账号系统」的UV238个

[![](https://p2.ssl.qhimg.com/t01b3c46318abbe7207.jpg)](https://p2.ssl.qhimg.com/t01b3c46318abbe7207.jpg)

提交正确题解的有4个..

[![](https://p0.ssl.qhimg.com/t0153d80e1c7143ced8.jpg)](https://p0.ssl.qhimg.com/t0153d80e1c7143ced8.jpg)

我们来看题解



## 0x01 解黏去缚，茅塞顿开

拿到首页发现没有什么东西可以交互，只有一个按了五次会调戏你的按钮。

[![](https://p5.ssl.qhimg.com/t0147d929b0d6444188.png)](https://p5.ssl.qhimg.com/t0147d929b0d6444188.png)

很多人的惯性是在这里就开始各种工具扫描器齐上阵了……<br>
实际上这个位置只有静态页，我把真正要“攻击”的服务放在了另一台…

1）从开发者工具中查看静态文件，两个js文件和一个css文件全部有程序作者信息。

[![](https://p5.ssl.qhimg.com/t0188a2e63ef4758ba8.jpg)](https://p5.ssl.qhimg.com/t0188a2e63ef4758ba8.jpg)

2）找到h5活动页作者<br>
这里有一个叫“ph0t0grapher”的人，就是这个h5活动页的主要程序员了，那么程序员爱用什么网站呢？github，stackoverflow，csdn等。有了靶场思路之后，我先提前把信息埋在了github上。

3）查找“ph0t0grapher”

[![](https://p4.ssl.qhimg.com/t014c9cd2bb27698631.jpg)](https://p4.ssl.qhimg.com/t014c9cd2bb27698631.jpg)

4）查看“ph0t0grapher”，点进去看下他的repo:

[![](https://p2.ssl.qhimg.com/t01a9198201296489d9.jpg)](https://p2.ssl.qhimg.com/t01a9198201296489d9.jpg)

5）查找敏感信息<br>
“huodong”的repo恰好就是靶场入口的全部代码，看下他的其他repo、fork的不用太关注，个人主页也没啥信息，剩下的那个是node.js编写的发邮件的demo，发现下面代码:

[![](https://p3.ssl.qhimg.com/t011113e2f8a44f4244.jpg)](https://p3.ssl.qhimg.com/t011113e2f8a44f4244.jpg)

6）查找commit信息<br>
这里看到了邮件的用户名密码认证信息是从config文件中读取的，然而回到上一层目录发现并没有config相关的目录和文件，再看下这个repo的commit信息:

[![](https://p2.ssl.qhimg.com/t0128c9228835d93247.jpg)](https://p2.ssl.qhimg.com/t0128c9228835d93247.jpg)

这两条commit message提示了作者在后来才添加了config相关文件，并且config相关文件也是在最后才删除的，那么作者很可能在添加config相关文件之前直接把邮箱账号密码写到程序中并提交了。直接点第二个commit验证这一点:

[![](https://p4.ssl.qhimg.com/t01ca5da27620f17005.jpg)](https://p4.ssl.qhimg.com/t01ca5da27620f17005.jpg)

成功拿到“liuyan”的邮箱，从host信息中看到是腾讯企业邮箱，直接从“exmail.qq.com”登录。至此第一步完成。

> 这一步卡住了一批人，主要原因是思路没有跳出，认为靶场入口一定存在某些可利用的漏洞。实际上在我们渗透测试的时候也是需要从收集资产收集信息开始。
 

## 0x02 眼见为虚，愿者上钩

登录邮箱后，从收件箱中看到下面几封邮件:

[![](https://p5.ssl.qhimg.com/t01d863b253dc795cf9.jpg)](https://p5.ssl.qhimg.com/t01d863b253dc795cf9.jpg)

有发版通知，有领导视察通知，有APP上线不成功的通知，且还被转发过，转发给了chenguanxi、wuyanzu、liudehua等很多人。

[![](https://p1.ssl.qhimg.com/t01f0629abfff43f403.jpg)](https://p1.ssl.qhimg.com/t01f0629abfff43f403.jpg)

[![](https://p4.ssl.qhimg.com/t012f3025a1ba078c6e.jpg)](https://p4.ssl.qhimg.com/t012f3025a1ba078c6e.jpg)

我们重点关注下这条被转发给很多人的邮件，这个邮件iOS开发一定很熟悉，这是一封伪造iOS APP审核失败的邮件。公司客服“liuyan”看到了这个邮件，凭经验转发知会给了研发团队相关人员。这是常见的二次钓鱼场景。

发件邮箱是gmail，点击链接跳到了一个ip地址上，输入任何信息点登录按钮都没有反应。

[![](https://p1.ssl.qhimg.com/t01c29d3359302f80b7.jpg)](https://p1.ssl.qhimg.com/t01c29d3359302f80b7.jpg)

“liuyan”转发了这封邮件给很多人，那么只要有人信以为真，就会填入用户名密码去尝试登录。

攻破这个钓鱼系统，黑到后台，拿到更多的账号。这里有一个文件遍历漏洞，我们可以去尝试常用文件名和路径，也可以用扫描器。

[![](https://p1.ssl.qhimg.com/t014f14fe35934dceaf.jpg)](https://p1.ssl.qhimg.com/t014f14fe35934dceaf.jpg)

很快我们扫到了 www.zip 这个文件，下载下来是整个钓鱼站的源代码

[![](https://p4.ssl.qhimg.com/t015614c1369536d9a1.jpg)](https://p4.ssl.qhimg.com/t015614c1369536d9a1.jpg)

其中 post.php是账号密码上传的代码，打开看一下:

[![](https://p4.ssl.qhimg.com/t018b1d355f61d4b80f.jpg)](https://p4.ssl.qhimg.com/t018b1d355f61d4b80f.jpg)

钓鱼黑客直接把密码存到了网站根目录下的data/password.txt中，直接访问之:

[![](https://p4.ssl.qhimg.com/t014cc40ed7c1ad9154.jpg)](https://p4.ssl.qhimg.com/t014cc40ed7c1ad9154.jpg)

看到了“chenguanxi”的邮箱账号密码就在其中。

到这里第二步结束。



## 0x03 冲云破雾，水到渠成

登录chenguanxi邮箱查看邮件:

[![](https://p5.ssl.qhimg.com/t01db0425b0604b9d07.jpg)](https://p5.ssl.qhimg.com/t01db0425b0604b9d07.jpg)

这些邮件都很有趣，暂且不表。有一封邮件暴露了公司某管理系统的后台地址:

[![](https://p4.ssl.qhimg.com/t015042a417fb823e43.jpg)](https://p4.ssl.qhimg.com/t015042a417fb823e43.jpg)

进入后发现有登录注册两个页面，其中注册时要校验工号，邮件中也有提到用工号注册，爆破工号也无效。(一般公司会把工号限制的非常死，防止爆破)。

[![](https://p0.ssl.qhimg.com/t017b5660021dc5e802.jpg)](https://p0.ssl.qhimg.com/t017b5660021dc5e802.jpg)

再看回刚才的邮件，发现有一封邮件提到了MongoDB:

[![](https://p1.ssl.qhimg.com/t012ddf754e3f687109.jpg)](https://p1.ssl.qhimg.com/t012ddf754e3f687109.jpg)

这里面提到了MongoDB的未授权访问，MongoDB并没有开放在外网。

百度搜索下MongoDB注入，根据目标语言(node.js)特性选择`{`“$ne”: null`}`这样的payload去尝试，登录页面不能直接绕过进入系统，但是注册页面可以绕过工号验证。payload:

```
`{`
  "username": "test",
  "password": "111111",
  "jobnumber":  `{`"$ne": null`}`
`}`
```

[![](https://p3.ssl.qhimg.com/t01eea67a0f7cf222d8.jpg)](https://p3.ssl.qhimg.com/t01eea67a0f7cf222d8.jpg)

成功注册用户并登陆系统，你会看到你自己能管理的服务器，公共服务器和一个ip地址为6.6.6.6的服务器。

[![](https://p1.ssl.qhimg.com/t01e8fa513705d94883.jpg)](https://p1.ssl.qhimg.com/t01e8fa513705d94883.jpg)

6.6.6.6的密码为随机生成，可以作为唯一标识证明自己亲自入侵成功进入系统。做到此步骤的小伙伴已经很6，但是还有一个注入点。

继续看系统。在登录进去后的服务器列表页面中给了相应的提示:“你负责的测试服务器都会在这里展示，生产服务器请联系管理员获取”。也就是说我们是看不到管理员服务器的，但他们应该在数据库中。 在前端console中，我故意打出了这样的数据结构(console中直接打印出数据结构也是程序员经常疏忽的点):

[![](https://p2.ssl.qhimg.com/t01ea0b29d6758a8440.jpg)](https://p2.ssl.qhimg.com/t01ea0b29d6758a8440.jpg)

从中可以看出服务器的owner是以数组的形式存的。为了过滤掉admin服务器，只显示自己的和public服务器，很可能用了$where语句，并使用JavaScript语句进行过滤，比较常见的过滤方式是判断字符串的indexOf。那么我们尝试闭合indexOf，构造payload，这一步确实要对MongoDB和JavaScript都比较了解才能做出。

payload：

```
')&gt;0|| this.owners.indexOf('admin
```

[![](https://p5.ssl.qhimg.com/t013145f8382d90687a.jpg)](https://p5.ssl.qhimg.com/t013145f8382d90687a.jpg)

成功拿到admin服务器，靶场Writeup结束。



## 0x04 彩蛋

1）思路设计阶段

[![](https://p3.ssl.qhimg.com/t015ac2023a06a67d04.png)](https://p3.ssl.qhimg.com/t015ac2023a06a67d04.png)

2）邮件剧情设计（为配合人设，想了好久的签名）

[![](https://p1.ssl.qhimg.com/t013c7a23248cd5ca83.png)](https://p1.ssl.qhimg.com/t013c7a23248cd5ca83.png)

3）邮件附件设计

[![](https://p5.ssl.qhimg.com/t01ff69a73e3aeb26bf.png)](https://p5.ssl.qhimg.com/t01ff69a73e3aeb26bf.png)

**[直达靶场](https://pockr.org/bug-environment/detail?environment_no=env_75b82b98ffedbe0035)**
