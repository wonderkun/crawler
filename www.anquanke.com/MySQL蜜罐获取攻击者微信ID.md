> 原文链接: https://www.anquanke.com//post/id/215696 


# MySQL蜜罐获取攻击者微信ID


                                阅读量   
                                **149666**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0127c51c84073ef433.png)](https://p3.ssl.qhimg.com/t0127c51c84073ef433.png)



## 前言

前些日子有人问到我溯源反制方面的问题，我就想到了MySQL任意文件读取这个洞，假设你在内网发现或扫到了一些MySQL的弱口令，你会去连吗？



## 原理

MySQL中 load data local infile ‘/etc/passwd’ into table test fields terminated by ‘\n’; 语句可以读取客户端本地文件并插进表中，那么我们可以伪造一个恶意的服务器，向连接服务器的客户端发送读取文件的payload。这个技术并不新鲜，但是合理利用就能起到一些不错的成果。

利用

抓个包看看连MySQL时客户端和服务端通信的两个关键点：

服务端先返回了版本、salt等信息：

[![](https://p4.ssl.qhimg.com/t0187281f647de09468.png)](https://p4.ssl.qhimg.com/t0187281f647de09468.png)

客户端向服务端发送账号密码信息后，服务端返回了认证成功的包：

[![](https://p3.ssl.qhimg.com/t012ccd4bba01a34a07.png)](https://p3.ssl.qhimg.com/t012ccd4bba01a34a07.png)

至此，我们只需等待客户端再发一个包，我们就能发送读取文件的payload了，再看看读取文件这个包：

[![](https://p0.ssl.qhimg.com/t0121380694259a48dc.png)](https://p0.ssl.qhimg.com/t0121380694259a48dc.png)

这里000001是指数据包的序号，fb是指包的类型，最后一个框是指要读取的文件名，而最前面的14是指文件名的长度（从fb开始，16进制），所以payload则是chr(len(filename) + 1) + “\x00\x00\x01\xFB” + filename

在能够实现任意文件读取的情况下，我们最希望的就是能读到与攻击者相关的信息。日常生活中，大家几乎都会使用微信，而如果攻击者没有做到办公—渗透环境分离的话，我们就有希望获取到攻击者的微信ID

Windows下，微信默认的配置文件放在C:\Users\username\Documents\WeChat Files\中，在里面翻翻能够发现 C:\Users\username\Documents\WeChat Files\All Users\config\config.data 中含有微信ID：

[![](https://p5.ssl.qhimg.com/t011fd861c12f50cef0.png)](https://p5.ssl.qhimg.com/t011fd861c12f50cef0.png)

而获取这个文件还需要一个条件，那就是要知道攻击者的电脑用户名，用户名一般有可能出现在一些日志文件里，我们需要寻找一些比较通用、文件名固定的文件。经过测试，发现一般用过一段时间的电脑在 C:\Windows\PFRO.log 中较大几率能找到用户名。

[![](https://p5.ssl.qhimg.com/t0114c01c63f28d8c3f.png)](https://p5.ssl.qhimg.com/t0114c01c63f28d8c3f.png)



## 伪装

攻击者进入内网后常常会进行主机发现和端口扫描，如果扫到MySQL了，是有可能进行爆破的，如果蜜罐不能让扫描器识别出是弱口令，那就没啥用了，所以还需要抓下扫描器的包。

这里以超级弱口令检查工具为例，首先在本地起一个正常的MySQL服务，wireshark抓包看看扫描器有哪些请求：

[![](https://p0.ssl.qhimg.com/t01c549f74c6c572d48.png)](https://p0.ssl.qhimg.com/t01c549f74c6c572d48.png)

可以看到，这款工具在验证完密码后还发了5个查询包，如果结果不对的话，是无法识别出弱口令的，那么我们将服务器的响应数据提取出来，放进程序里，当收到这些请求后，就返回对应的包：

[![](https://p0.ssl.qhimg.com/t0127b8ce8da2d1d5ef.png)](https://p0.ssl.qhimg.com/t0127b8ce8da2d1d5ef.png)

这样就能让扫描器也可以正常识别：

[![](https://p0.ssl.qhimg.com/t01dff13a5806837827.png)](https://p0.ssl.qhimg.com/t01dff13a5806837827.png)



## 效果

当攻击者发现存在弱口令的时候，大概率会连上去看看，如果使用navicat的话，就能读取到文件：

[![](https://p4.ssl.qhimg.com/t01d93e3d8ed19038ec.png)](https://p4.ssl.qhimg.com/t01d93e3d8ed19038ec.png)

写了个简单的web来显示攻击者的微信ID，扫一扫就能加上TA

[![](https://p2.ssl.qhimg.com/t01abb43f1ad6b5522c.png)](https://p2.ssl.qhimg.com/t01abb43f1ad6b5522c.png)



## 思考

除了获取微信ID，我们还能获取哪些有价值的东西呢？
<li>
<section>chrome的login data，虽然无法解密出密码，但是还是可以获取到对方的一些账号的
‘C:/Users/’ + username + ‘/AppData/Local/Google/Chrome/User Data/Default/Login Data’
</section>
</li>
<li>
<section>chrome的历史记录
‘C:/Users/’ + username + ‘/AppData/Local/Google/Chrome/User Data/Default/History’
</section>
</li>
<li>
<section>用户的NTLM Hash（Bettercap + responder）
\\ip\test
</section>
</li>
详情：[https://www.colabug.com/2019/0408/5936906/](https://www.colabug.com/2019/0408/5936906/)

[![](https://p3.ssl.qhimg.com/t011d3bde1fa9ca8ec2.png)](https://p3.ssl.qhimg.com/t011d3bde1fa9ca8ec2.png)
<li>
<section>……
</section>
</li>
待解决问题：
<li>
<section>同一出口IP的不同攻击者的信息如何区分
</section>
</li>
<li>
<section>读取的文件较大时，客户端会分段传输，如何完整获取
</section>
</li>
<li>
<section>前端有点bug，不管了，能用就行了
关于其他可利用的点和以上待解决问题欢迎大家留言讨论，最后，源码我上传到GitHub了，有需要的朋友请自取：
[https://github.com/qigpig/MysqlHoneypot](https://github.com/qigpig/MysqlHoneypot)
</section>
</li>


## 参考链接

[1] [https://www.colabug.com/2019/0408/5936906/](https://www.colabug.com/2019/0408/5936906/)

[2] [https://github.com/ev0A/Mysqlist](https://github.com/ev0A/Mysqlist)
