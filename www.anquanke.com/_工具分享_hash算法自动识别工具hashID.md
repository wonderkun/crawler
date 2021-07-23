> 原文链接: https://www.anquanke.com//post/id/86695 


# 【工具分享】hash算法自动识别工具hashID


                                阅读量   
                                **262766**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：github.com
                                <br>原文地址：[https://github.com/psypanda/hashID](https://github.com/psypanda/hashID)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t01edfd4f255fb186f8.jpg)](https://p4.ssl.qhimg.com/t01edfd4f255fb186f8.jpg)**



**简介**

****

这个工具是用来代替[hash-identifier](http://code.google.com/p/hash-identifier/)的，因为hash-identifier已经过时啦！

hashID是用**Python3**写成，它通过正则表达式可识别**220多种**hash类型。可识别的hash详情列表可以点[这里](http://psypanda.github.io/hashID/hashinfo.xlsx)。

hashID**不仅可识别单个hash，还可解析单个文件中的hash，或者某目录下的多个文件中的hash**。同时hashID还支持[hashcat](https://hashcat.net/oclhashcat/)模式和[JohnTheRipper](http://www.openwall.com/john/)格式输出。

<br>

**安装方法**



**pip**

hashID还可以通过[PyPi](https://pypi.python.org/pypi/hashID)安装，升级，卸载。

```
$ pip install hashid
$ pip install --upgrade hashid
$ pip uninstall hashid
```

hashID在支持Python 2 ≥ **2.7**.x 或者 Python 3 ≥** 3.3**的平台都可以轻松上手！

**git clone**

你还可以通过clone这个repository来安装

```
$ sudo apt-get install python3 git
$ git clone https://github.com/psypanda/hashid.git
$ cd hashid
$ sudo install -g 0 -o 0 -m 0644 doc/man/hashid.7 /usr/share/man/man7/
$ sudo gzip /usr/share/man/man7/hashid.7
```



**使用方法**



```
$ ./hashid.py [-h] [-e] [-m] [-j] [-o FILE] [--version] INPUT
```

[![](https://p4.ssl.qhimg.com/t018f118e8a7205a01f.png)](https://p4.ssl.qhimg.com/t018f118e8a7205a01f.png)

```
$ ./hashid.py '$P$8ohUJ.1sdFw09/bMaAQPTGDNi2BIUt1'
Analyzing '$P$8ohUJ.1sdFw09/bMaAQPTGDNi2BIUt1'
[+] Wordpress ≥ v2.6.2
[+] Joomla ≥ v2.5.18
[+] PHPass' Portable Hash

$ ./hashid.py -mj '$racf$*AAAAAAAA*3c44ee7f409c9a9b'
Analyzing '$racf$*AAAAAAAA*3c44ee7f409c9a9b'
[+] RACF [Hashcat Mode: 8500][JtR Format: racf]

$ ./hashid.py hashes.txt
--File 'hashes.txt'--
Analyzing '*85ADE5DDF71E348162894C71D73324C043838751'
[+] MySQL5.x
[+] MySQL4.1
Analyzing '$2a$08$VPzNKPAY60FsAbnq.c.h5.XTCZtC1z.j3hnlDFGImN9FcpfR1QnLq'
[+] Blowfish(OpenBSD)
[+] Woltlab Burning Board 4.x
[+] bcrypt
--End of file 'hashes.txt'--
```



**相关资料**

****

[http://pythonhosted.org/passlib/index.html](http://pythonhosted.org/passlib/index.html)

[http://openwall.info/wiki/john](http://openwall.info/wiki/john)

[http://openwall.info/wiki/john/sample-hashes](http://openwall.info/wiki/john/sample-hashes)

[http://hashcat.net/wiki/doku.php?id=example_hashes](http://hashcat.net/wiki/doku.php?id=example_hashes)



**相关推荐**



另外还有一款在线的hash识别工具也不错哦。在没有命令行环境的时候，打开浏览器就可以用。

[https://www.onlinehashcrack.com/hash-identification.php](https://www.onlinehashcrack.com/hash-identification.php)
