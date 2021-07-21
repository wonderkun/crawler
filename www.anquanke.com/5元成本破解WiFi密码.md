> 原文链接: https://www.anquanke.com//post/id/238610 


# 5元成本破解WiFi密码


                                阅读量   
                                **231960**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01f352c0b60b72c75a.png)](https://p3.ssl.qhimg.com/t01f352c0b60b72c75a.png)



近期，发现某平台公然出现钓鱼WiFi教程内容，热度很高，不仅教程详细，作者更是将此软件进行了开源操作，相较于早年前的破解WiFi事件门槛更低，而更让人惊讶的是视频评论区，有不少用户分享着自己的破解心得，而在移动互联网迅速发展，智能手机、平板电脑的普及，WiFi已成为用户生活中不可或缺的一部分，WiFi安全问题更值得我们正视。

[![](https://p5.ssl.qhimg.com/t018f7e4acde6f15eac.png)](https://p5.ssl.qhimg.com/t018f7e4acde6f15eac.png)



## 成本5元的WiFi自动化钓鱼

**钓鱼WiFi原理**

对目标路由器及客户端进行攻击，客户端与路由器断联，再诱导连接虚假钓鱼WiFi从而窃取密码。

**钓鱼WiFi搭建过程**

综合网络的攻击教程来看，目前主要在固件有所区别，一部分固件是集成WiFi+攻击方式+钓鱼网站，一部分是WiFi固件与攻击固件分开。

使用软件工具，将钓鱼网站写入物联网开发板，不同作者的钓鱼内容不同，其展示内容有所区别。部分固件是集成了攻击模式和钓鱼网站，安装驱动和集成固件即可完成钓鱼WiFi制作。

[![](https://p5.ssl.qhimg.com/t0199997d71fbfab5dc.png)](https://p5.ssl.qhimg.com/t0199997d71fbfab5dc.png)

**钓鱼WiFi的攻击过程**

物联网开发板开启WiFi后，首先连接该WiFi并进入管理后台，扫描附近WiFi。对目标路由器WiFi-1及客户端进行攻击，此时连接WiFi-1的设备会与WiFi断开连接。伪造钓鱼使用的同名WiFi-1，事主连接钓鱼WiFi-1后，由于使用了WiFi- Portal认证，会跳出指定的认证链接（钓鱼链接），事主在钓鱼WiFi写入路由器密码后，密码被窃取。

备注：Portal认证是无线WiFi或者WLAN网络作为网络接入控制使用，实现需要联网的终端设备需要认证才能接入互联网。

**钓鱼WiFi可能出现的危害**

[![](https://p3.ssl.qhimg.com/t01c381bf6d2fa5fde7.png)](https://p3.ssl.qhimg.com/t01c381bf6d2fa5fde7.png)



## 个人用户如何防范被钓鱼呢？

n根据已有资料看，目前此种攻击手段主要是针对路由器2.4G。在使用双模路由器时，可同时开启2.4G和5G。

n不要轻易连接公共WiFi，小心被钓鱼。

[![](https://p1.ssl.qhimg.com/t0176dbf8506ef41c06.png)](https://p1.ssl.qhimg.com/t0176dbf8506ef41c06.png)
