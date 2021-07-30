> 原文链接: https://www.anquanke.com//post/id/246659 


# Linksys EA6100 固件解密分析


                                阅读量   
                                **38599**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01e5b45ddf27e18abb.jpg)](https://p1.ssl.qhimg.com/t01e5b45ddf27e18abb.jpg)



## 0x01 前言

这一次来分享一个对固件解密的文章<br>
在一次分析固件的过程中，看到了Linksys EA6100 的一款固件，很不幸，这款固件被加密了，这里接下来将固件解密的过程来做个梳理。



## 0x02 固件信息

首先在固件的下载界面查看固件的版本，这里有两个版本，先不管那么多，全都下载下来，拿到固件 “ FW_EA6100_1.1.6.181939_prod.gpg.img “ ，我看到固件名字，感觉很奇怪，第一次到固件以 “ .gpg.img” 为结尾的固件包，正常的固件包是以 “img”、“bin”、“chk” 为结尾。bing 搜索，发现只能搜到gpg的的相关信息，在了解完了gpg信息后，知道了这是一个为文件生成签名、管理密钥以及验证签名的工具。因此固件很有可能是使用GPG生成的密钥进行加密的。



## 0x03 判断是否被加密

这里介绍以下判断固件是否加密的一种方式。<br>
我们使用的是binwalk来分析<br>
根据binwalk的熵分析，可以看到固件处于加密的状态。

> 熵是用于表达混乱程度的名词，熵值可以表达系统中蕴含的能量，也可用于表达信息中的不确定性。

根据下面的图形可以了解到，“ FW_EA6100_1.1.6.181939_prod.gpg.img ” 固件的熵值几乎为1，属于高熵，说明固件处于被加密的状态。

[![](https://p3.ssl.qhimg.com/t013438ba89047e00f9.png)](https://p3.ssl.qhimg.com/t013438ba89047e00f9.png)

如下图所示，这是一个没有加密的NetGear WiFi拓展器的固件，可以看到熵值在有一个小片段有剧烈的上下波动，说明这部分的固件并没有被加密。

[![](https://p4.ssl.qhimg.com/t01dc1f962bda135c9e.png)](https://p4.ssl.qhimg.com/t01dc1f962bda135c9e.png)



## 0x04 固件分析

使用binwalk 看一下固件的信息，因为固件被加密了，所以啥都看不到。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fd5a1456ff5c88d6.png)

同时万能的 file 也识别不出来

[![](https://p4.ssl.qhimg.com/t0122b021527f911896.png)](https://p4.ssl.qhimg.com/t0122b021527f911896.png)

当我正在思考下一步该怎么做的时候，发现了下载固件页面中有这么一段话。

> **IMPORTANT:** It is **highly recommended** to upgrade the firmware of your router using the **Auto Update** feature. However, if you prefer to do manual updates and your router is on **1.1.5.162431 or older, YOU MUST download &amp; update your router using firmware version 1.1.5.172244 first before loading the latest firmware**.

在更新最新固件的时候，需要先下载 Ver. 1.1.5 (Build 172244) 作为中间件，来升级到最新的固件，这个设备的最新固件就是Ver. 1.1.6，但是这个固件是加密的，一般来说，需要中间件的情况是用于提供密钥来解密最新的固件，并且FW_EA6100_1.1.5.172244_prod.img 中是没有 “gpg” 后缀的，说明这个固件并没有被加密，这样一来就说的通了。

根据实际的分析情况来看，这个固件确实没有被加密，可以识别出来文件系统是用 jffs2 压缩方式进行压缩的。<br>
查看固件的组成结构

[![](https://p3.ssl.qhimg.com/t010be518563be1c0dc.png)](https://p3.ssl.qhimg.com/t010be518563be1c0dc.png)

计算固件熵值

[![](https://p1.ssl.qhimg.com/t014b495802191eb8ae.png)](https://p1.ssl.qhimg.com/t014b495802191eb8ae.png)

file 查看

[![](https://p1.ssl.qhimg.com/t016f0cbc54fd396b1f.png)](https://p1.ssl.qhimg.com/t016f0cbc54fd396b1f.png)

接下来我们直接使用 binwlk -Me 来提取固件jffs2-root 文件系统。

[![](https://p3.ssl.qhimg.com/t01f1fcab684724a18a.png)](https://p3.ssl.qhimg.com/t01f1fcab684724a18a.png)

我们将 Ver. 1.1.5 (Build 172244) 的固件成功解开了，在这里，我们先了解一下gpg 生成密钥的形式是什么样的。

[![](https://p3.ssl.qhimg.com/t0137c21cc6794b23e8.png)](https://p3.ssl.qhimg.com/t0137c21cc6794b23e8.png)

然后我就在固件中包含pub 、rsa 字符串的文件，很不幸，一无所获，找到的都是一些无关的文件。<br>
于是我开始检索一些其他的密钥保存的格式之后，一般都是下面的这种方式

> <p>——-BEGIN RSA PRIVATE KEY——- # 私钥内容<br>
… (private key in base64 encoding) …<br>
——-END RSA PRIVATE KEY——-<br>
——-BEGIN CERTIFICATE——- # 证书信息<br>
… (certificate in base64 PEM encoding) …<br>
——-END CERTIFICATE——-</p>

于是顺着这个思路，我终于找到了类似 gpg 密钥的文件了，幸运的 “ keydata ” 文件

[![](https://p1.ssl.qhimg.com/t01fa69e4bc532691f7.png)](https://p1.ssl.qhimg.com/t01fa69e4bc532691f7.png)

首先将keydata 加载到 系统中的 gpg 中，然后再进行对固件包解密

[![](https://p4.ssl.qhimg.com/t018cd90aa599fbefd9.png)](https://p4.ssl.qhimg.com/t018cd90aa599fbefd9.png)

我们成功的得到了解密后的文件，使用binwalk 识别一下固件的信息。

[![](https://p1.ssl.qhimg.com/t0165c67b7d20fb5282.png)](https://p1.ssl.qhimg.com/t0165c67b7d20fb5282.png)

现在用binwalk 就可以完全的解开固件包了

[![](https://p2.ssl.qhimg.com/t01d68863c670b50633.png)](https://p2.ssl.qhimg.com/t01d68863c670b50633.png)



## 0x05总结

本片文章主要是讲解对固件如何解密的一种方法，这种固件就是以前的固件没有加密，但是后面的固件加密了，在需要解密的情况下，就需要一个中间过渡版本的固件，这个过渡版本的固件中带有解密程序，然后对最新的固件进行解密。

这里还对固件的文件系统进行了简单的分析，虽然没有发现显著的漏洞，但是这里也简单描述一下。<br>
在/etc/init.d/service_httpd.sh 文件中了解到了lighttpd是设备web组件，以及web组件启动的过程。<br>
lighttpd 文件是在/usr/sbin/中<br>
/etc/init.d/中包含了设备启动初始化所有的启动文件，并且包含一些密钥信息。<br>
/www/ui/cgi/ 文件夹中有一些cgi 文件，但是经过分析，并没有发现有异常的风险点。<br>
/www/ui/local 文件夹中主要包含的是路由器设备的前端的html一些文件。<br>
逆向分析了一下lighttpd，并没有发现一些风险点，可能是对lighttpd 框架了解的不多，等拜读一下源码，了解那里是二次开发的地方，再来分析这个组件。
