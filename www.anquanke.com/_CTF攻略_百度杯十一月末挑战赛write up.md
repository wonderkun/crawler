> 原文链接: https://www.anquanke.com//post/id/85057 


# 【CTF攻略】百度杯十一月末挑战赛write up


                                阅读量   
                                **118443**
                            
                        |
                        
                                                                                    



**<br>**

**[![](https://p1.ssl.qhimg.com/t013d7b6925a1f65ec3.jpg)](https://p1.ssl.qhimg.com/t013d7b6925a1f65ec3.jpg)**

**<br>**

**前言**

这是i春秋学院百度杯十一月末最后一场比赛的write up，以战国魏事记为故事背景，由4个小故事:三家分晋、败走邯郸、鬼谷门徒、窃符救赵组成。答题者需要破解这些密码，才能拿到最后的flag。

 

**出题背景**

**1. 三家分晋**

赵襄子，韩康子与魏桓子的商议被智伯的间谍偷偷记录了下来，所有的信息都在存储在下面的pcap包中，你能找出他们谈论的内容吗？

**2. 败走邯郸**

齐将田忌、孙膑率兵围攻魏国国都大梁，途径一险关，有重兵把守，孙膑计上心头，决定伪造了魏王手谕，以期兵不血刃地拿下该据点。你能帮助他们伪造一封魏王的手谕吗？

**3. 鬼谷门徒**

孙膑知道，要想击败庞涓，不仅要让他被胜利冲昏头脑，无法保持清醒，更重要的是要利用庞涓用兵布阵的缺陷，请帮助孙膑击败庞涓。

**4.窃符救赵**

魏王宠妾如姬为了帮助信陵君夺取兵符，潜入魏王寝宫。但是当年魏王     为了预防兵符被盗，命人打造了许多形状一样，但与真兵符材料不同的假兵符，所以信陵君每次从如姬那取到的都是假兵符。那么，信陵君如何才能得到真的兵符呢？

 

**开始答题**

**签到题**

Md5解密得admin

 

**小常识**

按照题目要求



```
0x94 = 148
0x4664 = 18020
Flag`{`148,18020`}`
```



**回归原始**

八位一组，2进制转换成10进制然后转字符得flag

 

挑战题-战国魏事记

挑战题·战国魏国

**<br>**

**第一关**

下载pcap数据包后用wireshark打开

发现有很多请求以HTTP请求为主

筛选http请求

[![](https://p4.ssl.qhimg.com/t01a5a7de20cc4079ba.png)](https://p4.ssl.qhimg.com/t01a5a7de20cc4079ba.png)

前几个是访问第一关的请求

往下拉发现有很多一样的请求

随便打开其中一个

[![](https://p3.ssl.qhimg.com/t01307b24914899ed4b.png)](https://p3.ssl.qhimg.com/t01307b24914899ed4b.png)

发现了user-agent为sqlmap，可以知道此时正在用sqlmap进行注入

继续观察发现可注的参数中cookie的user参数最为可疑

但是经过了一些编码

经过多次测试编码方式为先base64编码在进行rot13编码所以我们可以反向解码

Wireshark没找到比较好的方法去批量导出特定数据，所以用python直接对文件进行明文查找

[![](https://p2.ssl.qhimg.com/t01a5f0165dd9ec8ecb.png)](https://p2.ssl.qhimg.com/t01a5f0165dd9ec8ecb.png)

取出cookie中user参数值进行解码

[![](https://p1.ssl.qhimg.com/t01ae11f160987c2ca7.png)](https://p1.ssl.qhimg.com/t01ae11f160987c2ca7.png)

得到明文注入语句

看payload可知，正在用时间盲注注入message表sqlmap的注入特点是当找到正确的字符时会进行!=不等于判断，所以可以查找这个关键字

 

[![](https://p2.ssl.qhimg.com/t019bc31ad066145e37.png)](https://p2.ssl.qhimg.com/t019bc31ad066145e37.png)

修改一下脚本

[![](https://p1.ssl.qhimg.com/t01ade1d797069cf4e7.png)](https://p1.ssl.qhimg.com/t01ade1d797069cf4e7.png)

得到密码，最后的0需要去掉是uid的值，我们需要的是message字段值

最后提交获得下一关地址

my_password_is_ilovedaliang

 

**第二关**

下载txt文件

是一段php代码这个代码其实是第三关的源码，在这一关我们可以不用管它是什么内容

下载后紧接着上传这个文件 看提示什么

[![](https://p3.ssl.qhimg.com/t016225c10d6900460b.png)](https://p3.ssl.qhimg.com/t016225c10d6900460b.png)

提示：校验时是有一段salt值

接着找到一个备份文件

[![](https://p3.ssl.qhimg.com/t01b494346d6fa141a8.png)](https://p3.ssl.qhimg.com/t01b494346d6fa141a8.png)

POST提交饶过waf

用vim  -r ***.swp恢复一下得到

[![](https://p5.ssl.qhimg.com/t010dd2c999687954ae.png)](https://p5.ssl.qhimg.com/t010dd2c999687954ae.png)

这里给出了默认的salt是ilovedaliang，或者你可以自定义salt

我们在尾部直接添加ilovedaliang试试

添加尾部数据时最好用python写入因为最后面有rn 直接编辑的话会覆盖掉

[![](https://p5.ssl.qhimg.com/t01b667bc8592fd8769.png)](https://p5.ssl.qhimg.com/t01b667bc8592fd8769.png)

但是还是失败了，提示：

[![](https://p5.ssl.qhimg.com/t01bc14ac611e09b4d1.png)](https://p5.ssl.qhimg.com/t01bc14ac611e09b4d1.png)

文件不能相同

所以意思很明白了，需要给出内容不一样但md5一样的

这里用win下的一个md5碰撞工具

fastcoll_v1.0.0.5.exe

需要你给出一个前缀文件，程序会生成两个md5一样的文件并且前缀文件内容不变

[![](https://p5.ssl.qhimg.com/t01c0cc47edbc9c1bfe.png)](https://p5.ssl.qhimg.com/t01c0cc47edbc9c1bfe.png)

[![](https://p4.ssl.qhimg.com/t01bff6be4bfc63b92a.png)](https://p4.ssl.qhimg.com/t01bff6be4bfc63b92a.png)

接着选msg1文件进行上传然后，取出msg2的后缀内容用postfix_salt参数请求

[![](https://p5.ssl.qhimg.com/t01116ed6327eadbce5.png)](https://p5.ssl.qhimg.com/t01116ed6327eadbce5.png)

url把0x换成百分号

burp提交

[![](https://p0.ssl.qhimg.com/t015fcfb5e74f76f365.png)](https://p0.ssl.qhimg.com/t015fcfb5e74f76f365.png)

[![](https://p2.ssl.qhimg.com/t01a8e0eada1fa95108.png)](https://p2.ssl.qhimg.com/t01a8e0eada1fa95108.png)

得到第三关地址

<br>

**第三关**

****

页面没有什么提示

[![](https://p2.ssl.qhimg.com/t014c68f41fbbe09916.png)](https://p2.ssl.qhimg.com/t014c68f41fbbe09916.png)

Set cookie user

想到第二关的txt文件

读代码发现有很多看似没有用的代码 而且strpos这里饶不过去

这里其实要利用一个刚爆不久的cve漏洞

[![](https://p3.ssl.qhimg.com/t010f321accb418ae1c.png)](https://p3.ssl.qhimg.com/t010f321accb418ae1c.png)

发现这里有点可疑，我是从来没有用过，会不会是这里导致的漏洞？于是用这个函数关键字搜索

[![](https://p0.ssl.qhimg.com/t0159178a5377069fb0.png)](https://p0.ssl.qhimg.com/t0159178a5377069fb0.png)

[https://www.cdxy.me/?p=682](https://www.cdxy.me/?p=682)

这里给出了一个测试脚本，发现测试脚本的代码跟 txt里的很相似，证明了txt中那些看似没用的代码其实都是漏洞触发的前提

直接用文中给出的序列化字符串提交就可以到下一关

[![](https://p0.ssl.qhimg.com/t0155c137981b219d92.png)](https://p0.ssl.qhimg.com/t0155c137981b219d92.png)

[![](https://p3.ssl.qhimg.com/t018bd195a42a354fde.png)](https://p3.ssl.qhimg.com/t018bd195a42a354fde.png)

[![](https://p1.ssl.qhimg.com/t01732d23f1188be02c.png)](https://p1.ssl.qhimg.com/t01732d23f1188be02c.png)

 

**第四关**

需给出ip port imgurl 猜测后台会发送请求

但是测试发现给出外网ip后一直加载最后挂掉 vps 上也没有收到请求

但是127.0.0.1是不会挂掉

猜测无法出外网

那测试一下看有没有命令注入

[![](https://p1.ssl.qhimg.com/t01ce33d4e9dcc015f3.png)](https://p1.ssl.qhimg.com/t01ce33d4e9dcc015f3.png)

路径猜测为默认路径，提交

[![](https://p0.ssl.qhimg.com/t01d4b3421992c50905.png)](https://p0.ssl.qhimg.com/t01d4b3421992c50905.png)

成功创建，证明有命令注入漏洞

接着写入一句话

用base64解码写入

[![](https://p5.ssl.qhimg.com/t01211a9150ff2472d5.png)](https://p5.ssl.qhimg.com/t01211a9150ff2472d5.png)

[![](https://p0.ssl.qhimg.com/t01e0f3a99ed6ee9d91.png)](https://p0.ssl.qhimg.com/t01e0f3a99ed6ee9d91.png)

[![](https://p2.ssl.qhimg.com/t016e7ed3d2c374abca.png)](https://p2.ssl.qhimg.com/t016e7ed3d2c374abca.png)

刚开始一直没找到flag文件，后面搜索了一下

[![](https://p0.ssl.qhimg.com/t015c54ebd94c735208.png)](https://p0.ssl.qhimg.com/t015c54ebd94c735208.png)

原来是在代码文件里面

[![](https://p3.ssl.qhimg.com/t010cf12eb8c881e220.png)](https://p3.ssl.qhimg.com/t010cf12eb8c881e220.png)

End

<br style="text-align: left">
