> 原文链接: https://www.anquanke.com//post/id/86513 


# 【技术分享】旧瓶新酒之ngx_lua &amp; fail2ban实现主动诱捕


                                阅读量   
                                **83764**
                            
                        |
                        
                                                                                    



**[![](https://p1.ssl.qhimg.com/t014e74dce33d0b3a48.jpg)](https://p1.ssl.qhimg.com/t014e74dce33d0b3a48.jpg)**

**前言**

服务器承担着业务运行及数据存储的重要作用，因此极易成为攻击者的首要目标。如何对业务服务器的安全进行防护，及时找出针对系统的攻击，并阻断攻击，最大程度地降低主机系统安全的风险程度，是企业安全从业人员面临的一个问题。

**本篇原创文章主要通过介绍ngx_lua &amp; fail2ban实现主动诱捕从而达到主机防护的效果。**

<br>

**ngx_lua &amp; fail2ban实现主动诱捕**

用过主机层WAF的朋友对ngx_lua_waf应该都不陌生，做过SSH防暴力破解的同学应该对fail2ban也有耳闻。

常见的开源主机WAF有 mod_security、naxsi、ngx_lua_waf 这三个，ngx_lua_waf 性能高和易用性较强，基本上零配置，只需要维护规则，常见的攻击类型就都能防御，相对来说是比较省心的选择。同时，基于lua脚本编写模块也很快捷，甚至可以实现一些复杂的业务层逻辑安全控制。当然，选择春哥的openresty也可以，如果选择openresty就不需要再单独安装lua相关的组件了。

这里我们简单介绍一下安装过程，用nginx或者tengine都可以，需要安装LuaJIT，操作系统需要安装zlib,zlib-devel,openssl,openssl-devel,pcre,pcre-devel。LuaJIT安装成功后，如下图所示。

[![](https://p0.ssl.qhimg.com/t019569639bb96724a3.png)](https://p0.ssl.qhimg.com/t019569639bb96724a3.png)

Tengine编译参数如下：



```
--prefix=/usr/local/nginx 
--with-http_lua_module 
--with-luajit-lib=/usr/local/luajit/lib/ --with-luajit-inc=/usr/local/luajit/include/luajit-2.0/ --with-ld-opt=-Wl,-rpath,/usr/local/luajit/lib
```

下载ngx_lua_waf，下载地址为https://github.com/loveshell/ngx_lua_waf，解压后放在/usr/local/nginx/conf目录下，可重命名为指定名称如waf，修改ngx_lua_waf配置文件config.lua，路径根据实际安装情况定。



```
RulePath = "/usr/local/nginx/conf/waf/wafconf/"
attacklog = "on"
logdir = "/usr/local/nginx/logs/waf"
```

需要注意logdir指向的目录不存在，需要手工创建，创建后需要修改所属权限，否则防护日志无权限写入。

nginx主配置文件nginx.conf的http段中添加如下内容。



```
lua_package_path "/usr/local/nginx/conf/waf/?.lua";
lua_shared_dict limit 10m;
init_by_lua_file  /usr/local/nginx/conf/waf/init.lua; 
access_by_lua_file /usr/local/nginx/conf/waf/waf.lua;
```

检查nginx配置/usr/local/nginx/sbin/nginx –t，如果没问题重启nginx既可生效。

Fail2ban安装我们就不做过多介绍了，安装配置都比较简单，不过fail2ban的经典用法基本都是用来做SSH防暴力破解的，那么fail2ban到底和ngx_lua_waf有什么关系呢？其实，看一下fail2ban的原理，通过正则匹配SSH日志中的关键字，根据达到定义的触发规则次数，调用iptables将攻击IP ban掉一定的时间。

[![](https://p4.ssl.qhimg.com/t01a38d406f4cbe8e7d.png)](https://p4.ssl.qhimg.com/t01a38d406f4cbe8e7d.png)

相信大家也都想到了，既然能通过匹配SSH日志，web日志肯定也是能匹配到的，只不过是要定义相关匹配规则而已，fail2ban本身也支持apache和vsftp。针对其他的应用系统也一样，分析场景，编写好规则就可以了。

[![](https://p3.ssl.qhimg.com/t01f20258a9a058ad0b.png)](https://p3.ssl.qhimg.com/t01f20258a9a058ad0b.png)

[![](https://p0.ssl.qhimg.com/t018afac6e0c39d9adb.png)](https://p0.ssl.qhimg.com/t018afac6e0c39d9adb.png)

说了这么多，这里才是我们的重点，我们的目的是主动诱捕具有针对性的攻击行为，主动诱捕是相对于传统蜜罐，传统蜜罐是被动的诱使攻击者访问，再对其行为进行记录。主动诱捕是指将具有针对性的攻击行为主动转向蜜罐网络，对攻击者几乎是透明的，不知不觉就进入到了我们的蜜罐网络中。

为什么要采用主动诱捕的方式来进行防御呢，大家可能都有这个体会，我们的应用系统每天都会受到很多攻击，但99%可能都是盲目的扫描探测，只有不到1%可能才是具有针对性的攻击，而我们真正关心的其实就是这1%的针对性攻击，1%的有效数据被99%的垃圾数据覆盖，对分析造成了很大的干扰。

要让主动诱捕真正发挥作用，我们首先要梳理好业务场景，梳理出哪些场景下的攻击是真正具有威胁性的，根据实际情况编写好规则，当攻击行为触发规则，筛选出攻击IP并调用iptables转发到蜜罐网络中。根据不同需求，蜜罐网络中可以KILLCHAIN进行跟踪和分析，也可以根据业务进行攻击行为分析，进而调整整体安全策略，达到有效防御。

当然，蜜罐网络要做好隔离，否则会造成很大的安全隐患，技术也是一把双刃剑，iptables可以将攻击IP流量转发到蜜罐网络，相信大家也想到了利用iptables实现端口复用，绕过一些端口访问控制。因此，要想做到更好的防御，就要比攻击者更了解自己的系统。

以上为悬镜安全实验室原创文章，如需转载请标注：[](http://www.xmirror.cn/)[http://lab.xmirror.cn/atc/2017/07/19/xmirror-security.html](http://lab.xmirror.cn/atc/2017/07/19/xmirror-security.html)    


