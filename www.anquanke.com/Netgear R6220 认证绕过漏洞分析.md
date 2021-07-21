> 原文链接: https://www.anquanke.com//post/id/227623 


# Netgear R6220 认证绕过漏洞分析


                                阅读量   
                                **130782**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



## 00-前言

依据cve/zdi等平台发布的漏洞信息，借助补丁对比技术，对Netgear r6220认证绕过漏洞进行研究，涉及漏洞的发现过程、成因分析、POC编写。



## 01-简介

1、漏洞描述：https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-17137

```
This vulnerability allows network-adjacent attackers to bypass authentication on affected installations of NETGEAR AC1200 R6220 Firmware version 1.1.0.86 Smart WiFi Router. Authentication is not required to exploit this vulnerability. The specific flaw exists within the processing of path strings. By inserting a null byte into the path, the user can skip most authentication checks. An attacker can leverage this vulnerability to bypass authentication on the system.
```

2、关键点：netgear r6220、版本1.1.0.86及之前、认证绕过、路径字符串中null字节

3、通过认证绕过，可访问一些受限页面，会造成敏感信息泄漏，扩大被攻击面



## 02-准备

1、确定待比较版本：[netgear中国站点](http://support.netgear.cn/doucument/Detail.asp?id=2294)存在1.1.0.86和1.1.0.92这两个版本（以下简称86版和92版），由上述漏洞描述可知86版是有漏洞版本，而[92版的版本说明](http://support.netgear.cn/doucument/Version.asp?id=5224)中提及修复了[PSV-2019-0109](https://kb.netgear.com/000061516/Security-Advisory-for-HTTP-Authentication-Bypass-on-the-R6220-PSV-2019-0109)（netgear自家的漏洞编号），综合上述信息，选择86与92为对比版本

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014135.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014135.jpg)

2、固件下载：

Version 1.1.0.86（有漏洞）：[http://support.netgear.cn/Upfilepath/R6220-V1.1.0.86.img](http://support.netgear.cn/Upfilepath/R6220-V1.1.0.86.img)<br>
Version 1.1.0.92（已修复）：[http://support.netgear.cn/Upfilepath/R6220-V1.1.0.92_1.0.1_BETA.img](http://support.netgear.cn/Upfilepath/R6220-V1.1.0.92_1.0.1_BETA.img)

3、相关工具

```
- 漏洞对比：ida 6.8 + bindiff 4.3
- 静态分析：ida 6.8
- http发包：burpsuite
- 文件系统提取：Ubuntu 18.04下binwalk
```

4、ps：因手头正好有一台1.1.0.68（86之前）的netgear r6220，因此省去了固件模拟的步骤



## 03-补丁对比

> bindiff的用法自行学习，本文不再赘述

1、按相似度不为1，从上到下依次看，略过库函数，重点看sub_xxx这种未命名函数

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014138.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014138.jpg)

2、运气比较好，看了第一个sub_4094c8 vs sub_409548 就找到了敏感位置，这两个函数代码块比较多（500+），故bindiff中并未完全展开，如下所示：二者有6处不同，右-92版比左-86版多了两个代码块，重点看这两种

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014139.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014139.jpg)

3、依次查看黄色代码块（即有变化的），直到发现如下：右侧出现了a00，即00字符串。

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014142.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014142.jpg)

4、联想漏洞描述中“By inserting a null byte into the path……”，此处比较可疑，ida中重点看一下（已修复的92版）

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014137.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014137.jpg)

向上追溯，可推断strstr的参数1为uri，若发现00字符，则最终跳往如下：明显进入了处理错误的流程

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-14135.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-14135.jpg)

5、经过如上分析，可基本断定补丁所修补的地方，接下来需进一步分析程序，来看漏洞如何出现，又该如何触发

6、PS：补丁对比本身也是要看运气的，首先要从众多函数中找到已修改且敏感的函数，再找函数中修改过的代码块，再结合漏洞信息来判定，如果不是，则周而复始再看其他的，也比较耗时



## 04-简单测试

1、binwalk从固件中提取出文件系统，其web根目录有如下文件，随手测试几个

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-14138.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-14138.jpg)

2、/currentsetting.htm可直接访问，无需经过认证

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014131.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014131.jpg)

3、/index.htm则需要经过认证

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-14141.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-14141.jpg)

4、联系漏洞描述“The specific flaw exists within the processing of path strings. By inserting a null byte into the path, the user can skip most authentication checks.”，漏洞可能发生在此处对uri的处理中。



## 05-漏洞分析

> 基于92已修复版本的web程序，其位于文件系统下/usr/sbin/mini_httpd

1、通过bindiff定位到大概位置**（上述步骤4）**：92版sub_409548函数中strstr检测%00处

2、向上回溯，如下：j跳转到一个循环，将某标志置为0（mips的流水线效应），并取了一堆字符串的首地址

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014136.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014136.jpg)

3、off_422c10处是字符串数组，这些html无需认证就可访问

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014144.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014144.jpg)

4、循环中遍历uri中是否出现这个html文件，若出现，则将标志置1

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014141.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014141.jpg)

5、上述补丁对比时，发现有一个strstr来判断uri中是否出现%00，若没发现，则继续调用sub_404ad4并传参uri

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014140.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014140.jpg)

6、sub_404ad4中，逐个字符来检测uri中是否出现%，并对其后的两个字符作进一步处理，大概可推测是URL解码的操作，查看处理函数sub_404a80可验证上述猜想

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014134.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014134.jpg)

7、注意，上述分析都是基于92版即已修复版本的，在86有漏洞版本中，并没有strstr对%00的过滤，如上述bindiff截图所示

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014142.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014142.jpg)



## 06-构造POC

1、有漏洞版本中：没有验证%00是否存在，直接进行了URL的解码处理，因此%00可以导致字符串的截断，结合成因分析步骤3/4中循环检测currentsetting.html等字符串的操作，可构造如下poc

```
GET /index.htm%00currentsetting.htm HTTP/1.1
Host: 192.168.1.1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Connection: close
```

2、认证绕过的逻辑

```
1. uri为：`/index.htm%00currentsetting.htm`
2. 程序先检测uri，确实存在`currentsetting.html`这种无需认证就可访问web文件
3. 随后未检测%00便进行URL解码，产生00截断，此时uri为：`/index.htm`，前面已经经过了检测，故正常进行访问
4. %00前是真正要访问的web文件，%00后是为了绕过认证而特意添加的“合法后缀”，程序处理逻辑有误，故造成认证绕过
```

3、如burp测试时，直接访问/index.htm会提示401，而通过poc可绕过认证

[![](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014143.jpg)](https://note-1252764528.cos.ap-chengdu.myqcloud.com/2021-01-06-014143.jpg)



## 07-小结

这个漏洞原理比较简单，简单捋一下<br>
1、认证时逻辑有误，导致认证绕过<br>
2、读取受限文件，若文件中包含密码等信息则造成敏感信息泄漏<br>
3、不管在LAN端还是WAN端，都扩大了被攻击面

官方的修复看起来有些草率，既然是null byte的截断漏洞，就直接strstr检测%00，有种“黑名单”的思想，但换一种角度想，代码更新迭代至今，这种修复方式也是无可奈何



## 08-参考

1、ZDI漏洞通告：[https://www.zerodayinitiative.com/advisories/ZDI-19-866/](https://www.zerodayinitiative.com/advisories/ZDI-19-866/)<br>
2、官方补丁说明：[https://kb.netgear.com/000061516/Security-Advisory-for-HTTP-Authentication-Bypass-on-the-R6220-PSV-2019-0109](https://kb.netgear.com/000061516/Security-Advisory-for-HTTP-Authentication-Bypass-on-the-R6220-PSV-2019-0109)

`From 新概念研究中心`
