> 原文链接: https://www.anquanke.com//post/id/172997 


# Globelmposter 3变种病毒详细分析报告


                                阅读量   
                                **367239**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">15</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t015314316b5a9f0de7.png)](https://p5.ssl.qhimg.com/t015314316b5a9f0de7.png)



## 0x1 Globelmposter 3勒索病毒简介

Globelmposter是一种比较活跃且变种比较多的病毒，其主要攻击手段是采用RSA加密算法加密本地磁盘下的所有文件，如果想要解密文件必须获取病毒作者手中的私钥信息，故这种病毒的危害性相对比较大。中了这种病毒的主机的主要特征就是，文件名会被加上Tigger444、Techno、DOC、CHAK、FREEMAN、TRUE、RESERVER、ALCO、Dragon444等后缀，在被加密的文件夹下会生成一个txt文档，记载着勒索信息及用户ID识别信息，用户需要将该ID发送给作者并支付一定数额的赎金方可获得解密程序，解锁被加密的数据文件。



## 0x2 GlobeImposter勒索病毒逆向分析

下面是针对近期爆发的GlobeImposter3.0样本进行的逆向分析（样本采集时间大概是在2019年2月份左右）。经过默安科技安全研究员郑斯碟分析，其主要行为包括：

[![](https://p5.ssl.qhimg.com/t01f5595507e9d8a0ce.png)](https://p5.ssl.qhimg.com/t01f5595507e9d8a0ce.png)

### 0x0 勒索病毒加密逻辑说明

该勒索病毒使用的是两对RSA密钥。其中一对RSA密钥我们将其姑且称为黑客密钥，黑客密钥的私钥在黑客手上，而公钥则放在病毒程序里用于加密客户端上随机生成的RSA密钥。病毒程序将会使用这个用户密钥中的公钥对用户硬盘上的文件进行加密，而私钥信息则会由病毒程序通过黑客公钥进行加密，生成用户ID。用户主机被感染后，如果想恢复数据文件则需要向攻击者提供用户ID和一定的金钱。攻击者获取到这个用户ID后，通过自身掌握的黑客私钥对用户ID进行解密，获得其中的用户密钥，然后使用用户私钥对用户机子上被加密的文件进行解密。

以下是详细的分析过程

### 0x1 拷贝病毒文件到指定目录

该病毒执行后会先定位自身所在的文件目录，然后将自身拷贝到C:\Users\Administrator\AppData\Local目录

[![](https://p1.ssl.qhimg.com/t01a5551d9845d44509.png)](https://p1.ssl.qhimg.com/t01a5551d9845d44509.png)

查看C:\Users\Administrator\AppData\Local

[![](https://p5.ssl.qhimg.com/t019e5ac5756af45ee7.png)](https://p5.ssl.qhimg.com/t019e5ac5756af45ee7.png)

### 0x2 计算用户ID并写入到public目录下

向C:\Users\Public\文件目录下写入用于加密文件的公钥信息以及用户ID信息，文件名为黑客公钥的hash值。

00409B4B函数为计算用户ID的入口

[![](https://p3.ssl.qhimg.com/t0112646a03fff7f222.png)](https://p3.ssl.qhimg.com/t0112646a03fff7f222.png)

跟进函数00409B4B

[![](https://p3.ssl.qhimg.com/t01ec60894f126b6cda.png)](https://p3.ssl.qhimg.com/t01ec60894f126b6cda.png)

跟进Sub_40A116函数，在这里生成随机rsa密钥对

[![](https://p4.ssl.qhimg.com/t01e1009d3dce0b433f.png)](https://p4.ssl.qhimg.com/t01e1009d3dce0b433f.png)

这里是将用户密钥拼接上.Tigger4444,然后使用黑客公钥将用户密钥信息进行加密。函数409FDE是rsa加密算法入口函数。

[![](https://p5.ssl.qhimg.com/t01efbc145c06c51962.png)](https://p5.ssl.qhimg.com/t01efbc145c06c51962.png)

以下是rsa加密函数部分源码

[![](https://p2.ssl.qhimg.com/t01b166da7aabb6b705.png)](https://p2.ssl.qhimg.com/t01b166da7aabb6b705.png)

在函数sub4027bc中对用户ID进行计算

[![](https://p3.ssl.qhimg.com/t014fce38126478266b.png)](https://p3.ssl.qhimg.com/t014fce38126478266b.png)

用户ID计算总结：

在函数Sub_40A116中，随机生成一对RSA密钥，然后将密钥拼接上.Tigger4444等字符串用黑客公钥进行加密，将加密后的文本作为参数传入sub_4027bc函数中，进行一些逻辑运算，最终计算出用户ID值，随后将用户ID写入到public目录下的一个文件中。该文件为

C:\Users\Public\E93F1BCB76F7967D37EB95F05095BDC21391A049734A9DEB06741C6FAF1C1107.txt

文件内容为

[![](https://p5.ssl.qhimg.com/t0180a797f9a11c6828.png)](https://p5.ssl.qhimg.com/t0180a797f9a11c6828.png)

上面一串为随机生成的rsa密钥对中的公钥信息，下面是用户ID。

### 0x3 生成勒索说明文件

计算用户ID，并将勒索信息和用户ID写入到HOW_TO_BACK_FILES.txt文件中。

[![](https://p5.ssl.qhimg.com/t01dfad924864c8948e.png)](https://p5.ssl.qhimg.com/t01dfad924864c8948e.png)<br>
HOW_TO_BACK_FILES.txt文件中的内容

[![](https://p1.ssl.qhimg.com/t01bc816df60b2a8bd2.png)](https://p1.ssl.qhimg.com/t01bc816df60b2a8bd2.png)

### 0x4 创建注册表项，设置开机自启动

病毒程序通过操作注册表，添加一下表项，将病毒程序设置为开机自启。路径是：

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce\BrowserUpdateCheck

[![](https://p3.ssl.qhimg.com/t017b130c4097dde5c2.png)](https://p3.ssl.qhimg.com/t017b130c4097dde5c2.png)

执行这一操作的函数调用流程是：

[![](https://p0.ssl.qhimg.com/t011a02619424667ec2.png)](https://p0.ssl.qhimg.com/t011a02619424667ec2.png)

病毒程序在sub_409524函数中对注册表项进行了添加操作，以下是sub_409524函数的相关源码

[![](https://p2.ssl.qhimg.com/t01d373a5a32b92fafa.png)](https://p2.ssl.qhimg.com/t01d373a5a32b92fafa.png)

### 0x5 加密文件

加密逻辑说明：

该勒索病毒用的是两对RSA密钥。其中一对RSA密钥我们将其姑且称为黑客密钥，黑客密钥的私钥在黑客手上，而公钥则放在病毒程序里用于加密客户端上随机生成的RSA密钥。病毒程序将会使用这个用户密钥中的公钥对用户硬盘上的文件进行加密，而私钥信息则会由病毒程序通过黑客公钥进行加密，生成用户ID。用户主机被感染后，如果想恢复数据文件则需要向攻击者提供用户ID和一定的金钱。攻击者获取到这个用户ID后，通过自身掌握的黑客私钥对用户ID进行解密，获得其中的用户密钥，然后使用用户私钥对用户机子上被加密的文件进行解密。

下面是具体的加密过程：

首先病毒程序会通过GetDriveTpye函数判断受害者主机上的磁盘类型。这里根据编号3，2，4可以判断该病毒支持对硬盘、移动硬盘、网络硬盘进行加密。

[![](https://p5.ssl.qhimg.com/t01a4dfe0d8b4fcb8d2.png)](https://p5.ssl.qhimg.com/t01a4dfe0d8b4fcb8d2.png)

接下来病毒程序会新建一个线程用于文件加密操作，线程方法名为__Tigger.004096EB，其三个参数分别为：当前盘符路径，加密key，用户ID。

[![](https://p5.ssl.qhimg.com/t01590830895280f1fc.png)](https://p5.ssl.qhimg.com/t01590830895280f1fc.png)

通过对__Tiger44.004096EB函数进行断点跟踪，我们知道，这里调用了RSA加密函数，对文件进行加密。遍历分区下所有的文件（c:/*）使用RSA加密算法对文件进行加密，并修改文件扩展名为.Tigger4444

[![](https://p2.ssl.qhimg.com/t014093f78c03946f5b.png)](https://p2.ssl.qhimg.com/t014093f78c03946f5b.png)

循环遍历所有文件，并对文件进行加密，改后缀名。

[![](https://p1.ssl.qhimg.com/t01c551a6033f8b8777.png)](https://p1.ssl.qhimg.com/t01c551a6033f8b8777.png)

这里判断下遍历的文件中是否含有自身的病毒文件，如果有，则不加密。

[![](https://p3.ssl.qhimg.com/t01e619841e42f0a166.png)](https://p3.ssl.qhimg.com/t01e619841e42f0a166.png)

rsa加密的具体位置

[![](https://p0.ssl.qhimg.com/t011ddd7b12d4fabf3d.png)](https://p0.ssl.qhimg.com/t011ddd7b12d4fabf3d.png)

加密流程梳理

[![](https://p4.ssl.qhimg.com/t017bb3b85dc6cab5b0.png)](https://p4.ssl.qhimg.com/t017bb3b85dc6cab5b0.png)

通过该调用图我们知道在函数sub_408D8B中调用了sub_409FDE函数，使用rsa加密算法对文件进行了加密。而sub_40116函数中也调用了sub_409FDE，这是做什么用呢？通过上面的分析我们知道，这是对用户密钥信息进行加密，也调用了RSA加密算法。所以这里使用rsa加密算法一共由两处，一处是用于加密密钥，一处是用于加密数据文件。其中加密文本使用的是用户端生成的公钥，而加密用户密钥使用的是黑客公钥。

### 0x6 新建bat文件，清除远程登入日志

病毒程序在加密结束后会在tmp目录下生成一个bat文件，

[![](https://p4.ssl.qhimg.com/t01c1d9864fbc276a42.png)](https://p4.ssl.qhimg.com/t01c1d9864fbc276a42.png)

具体的内容如下：

```
@echo off

vssadmin.exe Delete Shadows /All /Quiet

reg delete "HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Default" /va /f

reg delete "HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers" /f

reg add "HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\Servers"

cd %userprofile%\documents\

attrib Default.rdp -s -h

del Default.rdp

for /F "tokens=*" %1 in ('wevtutil.exe el') DO wevtutil.exe cl "%1"
```



其功能主要是删除卷影副本，清除远程登入日志。

以下是创建生成bat文件的位置，函数00409449：

[![](https://p4.ssl.qhimg.com/t0167a986fc6a43455b.png)](https://p4.ssl.qhimg.com/t0167a986fc6a43455b.png)

### 0x7 删除自身病毒文件

病毒程序在结束进程前会删除自身文件

[![](https://p2.ssl.qhimg.com/t01e6bde6686ceb0fbb.png)](https://p2.ssl.qhimg.com/t01e6bde6686ceb0fbb.png)

以下是函数00409509处的代码

[![](https://p5.ssl.qhimg.com/t0188ef1530917ffec3.png)](https://p5.ssl.qhimg.com/t0188ef1530917ffec3.png)

### 0x8 为什么被加密的后的文件无法被解密

因为病毒程序在加密硬盘文件的时候使用的是随机生成的rsa密钥进行加密的，并且使用了黑客的另一个rsa公钥对这对随机生成的rsa密钥进行加密。由于用户密钥被加密，只有用黑客的私钥才能够解密用户密钥，获取用户私钥，解密文件。



## 0x3 可能的植入手段及防护手段

目前勒索病毒的植入方式主要有三种方式：

1、通过服务器弱密码攻击植入。如3389远程密码爆破，之前版本的勒索病毒就曾搭载过该shellcode进行横向传播。

2、通过水坑网站进行植入，攻击者会事先分析某一群体经常浏览的网站，对该网站进行攻击，并将病毒下载地址植入到网站页面上，伪装成合法软件，诱导用户进行下载运行。

3、通过服务器漏洞进行植入，如JBOSS漏洞（CVE-2017-12149、CVE-2010-0738）、WebLogic漏洞（CVE-2017-10271）、Tomcat漏洞利用等。

针对以上勒索病毒的植入手段，默安科技建议：
1. 正对服务器配置进行必要基线检查
1. 关闭不必要对外开放的端口，如3389，445，139等端口
1. 检查服务器登陆密码是否采用弱口令
1. 针对服务器上用到的各种web中间件的漏洞应及时打升级补丁。