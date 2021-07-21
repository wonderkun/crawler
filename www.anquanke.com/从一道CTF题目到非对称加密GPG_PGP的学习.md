> 原文链接: https://www.anquanke.com//post/id/228129 


# 从一道CTF题目到非对称加密GPG/PGP的学习


                                阅读量   
                                **110349**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01e67ca11e91929df0.png)](https://p3.ssl.qhimg.com/t01e67ca11e91929df0.png)



## 前言

偶尔看到一道CTF题目，**[BSidesSF2019]bWF0cnlvc2hrYQ**，过程中有用到一种加密。那就是GPG，据了解这是一种非对称加密方式。

好奇心驱使下，开始搜集学习这个加密方式的学习资料。



## 什么是GPG？

简介：

1991年，程序员Phil Zimmermann为了避开政府的监视，开发了加密软件PGP。因为这个软件非常好用，迅速流传开来成为许多程序员的必备工具。但是，它是商业软不能自由使用。所以，自由软件基金会决定，开发一个PGP的替代品取名为GnuPG，因此GPG就诞生了。GPG是GNU Privacy Guard的缩写，是自由软件基金会的GNU计划的一部分。它是一种基于密钥的加密方式，使用了一对密钥对消息进行加密和解密，来保证消息的安全传输。一开始，用户通过数字证书认证软件生成一对公钥和私钥。任何其他想给该用户发送加密消息的用户，需要先从证书机构的公共目录获取接收者的公钥，然后用公钥加密信息，再发送给接收者。当接收者收到加密消息后，他可以用自己的私钥来解密。

再提一下，非对称加密的定义吧，**公钥用于加密、私钥用于解密。使用公钥加密过的信息只能由配对的私钥解开。这种加密方式叫做非对称加密。**

简单来说：公钥相当于我们的银行账号，是公开的，别人可以给我们汇钱。

私钥相当于银行卡和存折，不能乱放，可以通过这个提我们的钱。

非对称加密的过程就是：小A要给小B汇钱，那么小B必须将自己的银行账号(公钥)给公开，然后小A拿到B的公钥后，通过银行给他打了一笔钱，这里的银行就相当于小B的公钥的加密方式，然后小B不是直接拿到这笔钱，而是要使用银行卡(私钥)通过银行将这笔钱取出来。

如图所示

[![](https://p4.ssl.qhimg.com/t01709ebd2d03d3e28b.png)](https://p4.ssl.qhimg.com/t01709ebd2d03d3e28b.png)

关于对称加密的理解

小A给小D写张纸条，上面写着“这个世界上根本就没有奥特曼”但是不希望在传递过程中被别人看到。

[![](https://p4.ssl.qhimg.com/t01ffc7faf4ad232908.png)](https://p4.ssl.qhimg.com/t01ffc7faf4ad232908.png)

但是中间这些传纸条的人比较闲，想看他们的纸条上写了什么。小A于是和小D约定好了，使用密钥3加密她的消息，将字母向下移动3个字母。因此，A将是D，B将是E，等等。如果使用简单的密钥3进行加密，并使用密钥3进行解密，则他们的乱码加密消息很容易破解。有人可以通过尝试所有可能的组合来“强行使用”钥匙。换句话说，他们可以持续猜测，直到获得答案以解密邮件为止。

[![](https://p4.ssl.qhimg.com/t01f1005086c87c77f4.png)](https://p4.ssl.qhimg.com/t01f1005086c87c77f4.png)

这是著名的凯撒密码，使用这种加密方式来传输重要消息，是不安全的。

这是前置知识，下面就开始学习怎么使用GPG。



## 怎么使用？

安装的话，Linux发行版默认安装的gpg，这个是在终端使用的。还可以安装GUI软件——kgpg

```
sudo apt-get install kgpg
```

笔者这里使用的Terminal命令行。

### <a class="reference-link" name="%E5%BC%80%E5%A7%8B%E4%BD%BF%E7%94%A8"></a>开始使用

**1.生成密钥对**

```
gpg --gen-key
```

[![](https://p2.ssl.qhimg.com/t01e4d707466bc196e5.png)](https://p2.ssl.qhimg.com/t01e4d707466bc196e5.png)

在此过程中，会提示你设置一个密码。

**2.公钥/私钥的导出和导入**

公钥的导出：

```
gpg -o keyfilename --export mykeyID
```

如果没有mykeyID则是备份所有的公钥，-o表示输出到文件keyfilename中，如果加上-a的参数则输出文本格式( ASCII )的信息，否则输出的是二进制格式信息。

私钥的导出：

```
gpg -o keyfilename --export-secret-keys mykeyID
```

如果没有mykeyID则是备份所有的私钥，-o表示输出到文件keyfilename中，如果加上-a的参数则输出文本格式的信息，否则输出的是二进制格式信息。

[![](https://p4.ssl.qhimg.com/t01c9e18f89e7578573.png)](https://p4.ssl.qhimg.com/t01c9e18f89e7578573.png)

密钥的导入：

```
gpg --import filename
```

PS：无论是私钥的导入还是导出，都需要输入密码。<br>
使用`gpg --list-keys`命令查看是否成功导入了密钥。

[![](https://p2.ssl.qhimg.com/t016e00208bb30b3af0.png)](https://p2.ssl.qhimg.com/t016e00208bb30b3af0.png)

**3.加密文件**

3.1非对称加密

```
gpg -a --output m0re.gpg -r m0re.lxj@qq.com -e m0re.txt
```

其中参数：<br>`-a` 表示输出文本文件格式。 `--output` 指定输出（即加密后）的文件名。 `-r` 指定信息的接收者（`recipient`）公钥的`uid`，可以是名字也可以是`email`地址。 `-e` 表示这次要执行的是加密（`encrypt`）操作。<br>
执行完毕之后会在当前文件夹产生文件 m0re.gpg，这个就是被加密之后的文件。

[![](https://p5.ssl.qhimg.com/t017e89cbb598deab38.png)](https://p5.ssl.qhimg.com/t017e89cbb598deab38.png)

3.2对称加密

`gpg`也可以进行对称加密<br>`gpg`有个`-c`参数，只进行对称加密。

```
gpg -o m0re.gpg -c m0re.png
```

此时不需要密钥，密码也可以自己随意设定。

**4.解密文件**

```
gpg -d m0re.gpg
```

输入密码。即可解密成功。

[![](https://p4.ssl.qhimg.com/t01e591e1fb34a6dae3.png)](https://p4.ssl.qhimg.com/t01e591e1fb34a6dae3.png)

还有一中方法是利用工具——PGPTool，这个在下面解题会说到。

**5.删除密钥**

命令

```
gpg --delete-secret-keys [emailaddress]
```

[![](https://p5.ssl.qhimg.com/t012527b016cbda9bae.png)](https://p5.ssl.qhimg.com/t012527b016cbda9bae.png)

**6.对文件进行数字签名**

第一种签名方法<br>
使用命令

```
gpg -a -b m0re.txt
```

自动生成一个文件名为`m0re.txt.asc`的加密后的文件<br>`-a` 表示输出文本文件格式。 `-b` 表示以生成独立的签名文件的方式进行签名。<br>
一般发送者将信息文件和签名文件一同发给接收者。接收者利用签名文件来验证信息文件。<br>
检验命令

```
gpg --verify m0re.txt.asc
```

出现下图所示的样子即可。

[![](https://p3.ssl.qhimg.com/t01bddd08e7a003492e.png)](https://p3.ssl.qhimg.com/t01bddd08e7a003492e.png)

如果不是这样的，那么表示信息文件被人恶意改动。或者不是我本人发出。<br>
第二种签名方法<br>
如果不想生成一个独立的签名文件，则还可以用如下的命令进行签名：

```
gpg -a --clearsign m0re.txt
```

跟方法1不同的地方是用参数`–clearsign` 替代了参数 `-b`。参数 `clearsign` 表示将签名和原信息合并在一起，并生成一个新文件。<br>
命令运行后同样会生成一个文件 m0re.txt.asc，内容如下

```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

芜湖起飞～
-----BEGIN PGP SIGNATURE-----

iQGzBAEBCgAdFiEEFyHZb/vph9hAiDnAZVWJTjMZ80cFAl/8TsEACgkQZVWJTjMZ
80fYMwv/TqvBzhf3aawl51nNUqLRaFdvULTgDc0PqgEcIubcdQ91MFLgoVZxPiw4
Me1NuaHX8yxTXonxP8DmfVCJwAMwjYev/qvhNEnbHTFICgVapP81vIuDztZco6Ga
v3kyITSfwaHjLDnzf6aZH6oJQyQIyupnNmWTFIjXYM0h36RPC9sB13fjFv7QKqZJ
NuOLcWuhwaDygKhelDzGriPmoNPltcj0CMqqs+FkBy0PeaJMQymGMZGqlK5THl07
B7NXKFoFk4WgGkFBAQVEVrSnrpokvhpxCl8z25ni2gd52jUoche2Z1gEsOeAYNke
y2mJ/4+PJngKxep4rGzqamxSIQz3lpXcpZv8eECLDkEajrDorwIaKFsQwUGaDVtB
C2s5LqGd2KxjxHccZYQ30ki3uxI4hjI0zMif0jw6kCtzw7jWdVOihFix4iggw8QJ
Z2+id18t0Tx+wKtF16dUy9SIpk5U5eaAMQUp/PmhPClJUwS4rWQtNpnGs0SwIaoS
bf0mPckV
=DjMX
-----END PGP SIGNATURE-----
```

复制内容到一个人文本文件中`hello.txt`<br>
再进行验证`gpg --verify hello.txt`<br>
如图即是无误的信息。

[![](https://p5.ssl.qhimg.com/t01ab64f84222694ca3.png)](https://p5.ssl.qhimg.com/t01ab64f84222694ca3.png)

**7.常用参数**

```
-s, --sign [文件名]           生成一份签字
--clearsign [文件名]      生成一份明文签字
-b, --detach-sign             生成一份分离的签字
-e, --encrypt                 加密数据
-c, --symmetric               仅使用对称加密
-d, --decrypt                 解密数据(默认)
--verify                  验证签字
--list-keys               列出密钥
--list-sigs               列出密钥和签字
--check-sigs              列出并检查密钥签字
--fingerprint             列出密钥和指纹
-K, --list-secret-keys        列出私钥
--gen-key                 生成一副新的密钥对
--delete-keys             从公钥钥匙环里删除密钥
--delete-secret-keys      从私钥钥匙环里删除密钥
--sign-key                为某把密钥添加签字
--lsign-key               为某把密钥添加本地签字
--edit-key                编辑某把密钥或为其添加签字
--gen-revoke              生成一份吊销证书
--export                  导出密钥
--send-keys               把密钥导出到某个公钥服务器上
--recv-keys               从公钥服务器上导入密钥
--search-keys             在公钥服务器上搜寻密钥
--refresh-keys            从公钥服务器更新所有的本地密钥
--import                  导入/合并密钥
--card-status             打印卡状态
--card-edit               更改卡上的数据
--change-pin              更改卡的 PIN
--update-trustdb          更新信任度数据库
--print-md 算法 [文件]    使用指定的散列算法打印报文散列值

选项：

-a, --armor                   输出经 ASCII 封装
-r, --recipient 某甲          为收件者“某甲”加密
-u, --local-user              使用这个用户标识来签字或解密
-z N                          设定压缩等级为 N (0 表示不压缩)
--textmode                使用标准的文本模式
-o, --output                  指定输出文件
-v, --verbose                 详细模式
-n, --dry-run                 不做任何改变
-i, --interactive             覆盖前先询问
--openpgp                 行为严格遵循 OpenPGP 定义
--pgp2                    生成与 PGP 2.x 兼容的报文
```



## BSidesSF2019——bWF0cnlvc2hrYQ==

GPG的学习到此为一段落，下面把那一道CTF题目复现一下。这道题目的wp在网上也没有找到特别详细的。所以花的时间多了一点。<br>
后来发现在BUUCTF上面有这道题目。<br>
题目复现地址——[BUUCTF](https://buuoj.cn/challenges#%5BBSidesSF2019%5DbWF0cnlvc2hrYQ)<br>
题目是base64编码，解出是`matryoshka`翻译则是俄罗斯套娃

[![](https://p5.ssl.qhimg.com/t01d0c1f51586af0011.jpg)](https://p5.ssl.qhimg.com/t01d0c1f51586af0011.jpg)

下载得到的附件是eml文件，这里我没有去找查看eml的工具，所以跟大佬的wp，通过QQ邮箱发送邮件，并选择eml附件给自己。<br>
然后预览附件

[![](https://p2.ssl.qhimg.com/t0134cb1976dfd8ab78.png)](https://p2.ssl.qhimg.com/t0134cb1976dfd8ab78.png)

将附件下载下来，可以得到hack.gpg这个加密文件。还有一个私钥文件。

```
-----BEGIN PGP PRIVATE KEY BLOCK-----

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
=Hhg6
-----END PGP PRIVATE KEY BLOCK-----
```

[![](https://p5.ssl.qhimg.com/t010ce0dcd9cd0ebca1.png)](https://p5.ssl.qhimg.com/t010ce0dcd9cd0ebca1.png)

现在就差密码了。这个点卡了我好久，因为网上的资料显示直接得到密码，但是不理解为什么，后来就找到了GitHub中的一个师傅写的wp。<br>
说是在QQ邮箱中不显示头像，头像是个二维码。可以在记事本中打开eml文件搜索face，找到头像的base64编码。然后进行转换图片，即可得到二维码

[![](https://p0.ssl.qhimg.com/t01444d4e5e55756d27.png)](https://p0.ssl.qhimg.com/t01444d4e5e55756d27.png)

```
Face:iVBORw0KGgoAAAANSUhEUgAAADAAAAAwAQMAAABtzGvEAAAABlBMVEX///8AAABVwtN+AAAACXBI WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4wMBBAIZ8ky8pwAAAJRJREFUGFdlzbEJwzAQBdAzB04T khE0gzqrkVYRZIEMIHAgawiyyqWJS69g8AhqXIT8FPERI1evfAQ0GaAV4ZCFK4bS5HH+49OWNu4Q 7pKwArjf4DJARG0kUlAWY3PFcsUcoLjyMhSV5ShsJ8XhMHuuIAr3z0UBfP/MijD1FspQOiNmh6cT
 bUjNTRF2j/NUAfg4vle+pY6V5XCWRiUAAAAASUVORK5CYII=
```

进行base64转图片得到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c8c197b7fe5378bc.png)

扫描得到`h4ck_the_plan3t`<br>
猜测就是密码了。<br>
尝试进行解密，这里介绍一个工具。GPGTool<br>
先导入密钥

[![](https://p1.ssl.qhimg.com/t015567e66eb12efcee.png)](https://p1.ssl.qhimg.com/t015567e66eb12efcee.png)

然后选择Decrypt file，选择hack.gpg，输入密码，即可得到解密后的文件。

[![](https://p3.ssl.qhimg.com/t01876f88b1a252394e.png)](https://p3.ssl.qhimg.com/t01876f88b1a252394e.png)

`hack4.zip`——&gt;`file.bin`，<br>
首先查看是什么文件，看到数据文件，先尝试了binwalk

[![](https://p2.ssl.qhimg.com/t01073055fd7184a591.png)](https://p2.ssl.qhimg.com/t01073055fd7184a591.png)

lzip文件，所以我使用010editor打开看一下。

[![](https://p0.ssl.qhimg.com/t0173ba01a12115c4a5.png)](https://p0.ssl.qhimg.com/t0173ba01a12115c4a5.png)

百度搜索lzip的内容，但是确实少之又少。直到我找到wp，删除前11个字节，lzip文件的开头应当是lzip。即`4C5A4950`开头。<br>
解压该文件，注意使用lzip命令，kali默认不安装，所以需要手动安装

```
apt-get install lzip
```

[![](https://p0.ssl.qhimg.com/t012cac939d83780c11.png)](https://p0.ssl.qhimg.com/t012cac939d83780c11.png)

发现是PDF文件，该文件后缀查看。

[![](https://p0.ssl.qhimg.com/t01cfe2b06a7a08be42.png)](https://p0.ssl.qhimg.com/t01cfe2b06a7a08be42.png)

这个是WindowsXP的经典桌面壁纸。<br>
原图——[维基百科](https://en.wikipedia.org/wiki/Bliss_(image)<br>
仔细看白云的部分，会发现有明显的跟切割似的地方。从PDF里将图片提取出来，然后使用stegslove打开，在blue通道的2和3，看到非常类似二维码

[![](https://p1.ssl.qhimg.com/t018ac645adb2b96a13.png)](https://p1.ssl.qhimg.com/t018ac645adb2b96a13.png)

然后是双图的考点，记得提前保存原图。<br>
导入在维基百科下载的原图。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0168056eaa6c0beeea.png)

保存一下，然后扫描二维码得到

```
/Td6WFoAAATm1rRGAgAhARwAAAAQz1jM4ELCAORdABhgwwZfNTLh1bKR4pwkkcJw0DSEZd2BcWATAJkrMgnKT8nBgYQaCPtrzORiOeUVq7DDoe9feCLt9PG-MT9ZCLwmtpdfvW0n17pie8v0h7RS4dO/yb7JHn7sFqYYnDWZere/6BI3AiyraCtQ6qZmYZnHemfLVXmCXHan5fN6IiJL7uJdoJBZC3Rb1hiH1MdlFQ/1uOwaoglBdswAGo99HbOhsSFS5gGqo6WQ2dzK3E7NcYP2YIQxS9BGibr4Qulc6e5CaCHAZ4pAhfLVTYoN5R7l/cWvU3mLOSPUkELK6StPUBd0AABBU17Cf970JQABgALDhQEApzo4PbHEZ/sCAAAAAARZWg==
```

进行base64编码，即可看到开头明显的7z，所以猜测这是压缩包。

[![](https://p2.ssl.qhimg.com/t01d982e686b5d33365.png)](https://p2.ssl.qhimg.com/t01d982e686b5d33365.png)

但是在转换过程，一直没有成功。base64解码后转数据实现不了，太菜了呀。就借用了写出来wp的师傅的文件。[点击下载](https://firebasestorage.googleapis.com/v0/b/gitbook-28427.appspot.com/o/assets%2F-LSy8sGto5CLNupxyVZc%2F-L_ArNCgFVPyxHrFjWiV%2F-L_B6H0Z9oXSS-4-5AHx%2Fout.7z?alt=media&amp;token=b4c51146-5a2d-4813-a2f1-0cd19cc84091)

[![](https://p2.ssl.qhimg.com/t013849d3e2852ec28e.png)](https://p2.ssl.qhimg.com/t013849d3e2852ec28e.png)

按照自上而下的顺序来`binary-octal-decimal-hex-ascii`<br>
得到base64编码为`Nlc/TyVBN11SY0ZDL2EuP1lzcSFCallwdERmMCEz`<br>
进行解码得到：`6W?O%A7]RcFC/a.?Ysq!BjYptDf0!3`<br>
在进行base85解码：`CTF`{`delat_iz_muhi_slona`}``

[![](https://p3.ssl.qhimg.com/t01bb8ca22e7a611237.png)](https://p3.ssl.qhimg.com/t01bb8ca22e7a611237.png)



## 总结

这次学到了知识有：<br>
1.GPG非对称加密<br>
2.lzip隐写<br>
3.复习了 双图隐写



## 参考文章

[https://tuanlinh.gitbook.io/ctf/bsidessf-2019-ctf#forensic-bwf-0-cnlvc-2-hryq](https://tuanlinh.gitbook.io/ctf/bsidessf-2019-ctf#forensic-bwf-0-cnlvc-2-hryq)<br>[https://reverseltf.wordpress.com/2019/08/01/bsidessf2018-matryoshkas-revenge-writeup/](https://reverseltf.wordpress.com/2019/08/01/bsidessf2018-matryoshkas-revenge-writeup/)<br>[https://en.wikipedia.org/wiki/Lzip](https://en.wikipedia.org/wiki/Lzip)<br>[https://www.yuque.com/kshare/2019/c6b7ee54-5894-49b0-b810-304abd2eb47d](https://www.yuque.com/kshare/2019/c6b7ee54-5894-49b0-b810-304abd2eb47d)
