
# DDG挖矿僵尸网络病毒最新变种分析


                                阅读量   
                                **418457**
                            
                        |
                        
                                                                                    



[![](./img/202574/t01b8363df3ddf2f5e1.jpg)](./img/202574/t01b8363df3ddf2f5e1.jpg)

近期，公司攻防实验室接到客户反馈服务器异常卡顿，疑似感染挖矿病毒，经过安全工程师分析之后确定感染了DDG挖矿病毒，版本为5019和5020。

黑客通过SSH爆破或漏洞攻击利用进行入侵，入侵成功后会执行远程下载名为i.sh的shell脚本，DDG5019和5020版本区别在于是否使用UPX加壳。

[![](./img/202574/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.3001.net/images/20200407/1586251826_5e8c483215cbe.png!small)

以下是对该病毒进行的若干研究和分析，如有疏漏和错误，欢迎广大读者指正。



## i.sh脚本

该脚本主要功能是写入定时任务用于持久化，下载ddgs母体二进制文件，分为32位和64位；之后将下载的ddgs病毒母体重命名为mbdh139c，赋予权限并执行；清除历史版本的进程。

[![](./img/202574/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.3001.net/images/20200407/1586251833_5e8c483961635.png!small)

而此次的5020的i.sh版本中的下载链接替换成了域名的形式，并且每次访问域名都会随机替换。

[![](./img/202574/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.3001.net/images/20200407/1586251847_5e8c4847c4bad.png!small)



## ddgs

ddg母体的主要功能有自我文件拷贝、下载挖矿进程、使用漏洞感染其他设备。

此次捕获的ddg病毒母体相比之前400X的版本有些许变化，首先是去掉了main__backdoor_background和main__backdoor_injectSSHKey两个函数，即去掉了之前所用的后门功能。

[![](./img/202574/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.3001.net/images/20200407/1586251866_5e8c485a13f46.png!small)

之前版本使用了hashicorp的go开源库memberlist来构建分布式网络，在5020中也去掉了，使得病毒母体整体文件大小缩小了不少，可能更有利于传输。

[![](./img/202574/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.3001.net/images/20200407/1586251871_5e8c485fa1996.png!small)

5020版本中新增了自我文件拷贝，随机命名的功能。

[![](./img/202574/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.3001.net/images/20200407/1586251876_5e8c486420b0c.png!small)

程序中使用的漏洞利用模块也是沿用了之前版本（CVE-2017-11610、CVE-2019-7238、redis、SSH），并无新增远程漏洞利用方式。

[![](./img/202574/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.3001.net/images/20200407/1586251880_5e8c486897a5d.png!small)



## 挖矿程序

首先ddg母体会通过main_NewMinerd下载创建新的挖矿进程，然后main__minerd_Update对挖矿程序进行更新，最后调用main__minerd_killOtherMiners清除竞争对手的挖矿木马。

[![](./img/202574/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.3001.net/images/20200407/1586251885_5e8c486d02b48.png!small)

挖矿程序使用的是xmrig编译的

[![](./img/202574/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://image.3001.net/images/20200407/1586251889_5e8c4871a9651.png!small)



## 清除方案

1、清除到定时任务，相应的定时任务文件

/var/spool/cron/root

/var/spool/cron/crontabs/root

/etc/cron.d/root

2、删除及结束掉DDG母体相关文件和进程，如下

/usr/bin/mbch139c

/usr/libexec/mbch139c

/usr/local/bin/mbch139c

/tmp/mbch139c

ps -ef | grep -v grep | egrep ‘mbch139c’ | awk ‘{print $2}’ | xargs kill -9

3、查找相应的挖矿程序并删除及结束掉挖矿进程，如下

删除在临时目录下/tmp/netflix文件

ps -ef | grep -v grep | egrep ‘netflix’ | awk ‘{print $2}’ | xargs kill -9

安全建议

1、对于redis、SSH使用高强度的密码

2、及时修复Redis、Nexus Repository Manager、Supervisord服务相关的高危漏洞。

IOCs

URL：

ddg 5020

hxxp://111.229.129.150:39127/i.sh

hxxp://111.229.129.150:39127/static/5020/ddgs.i686

hxxp://111.229.129.150:39127/static/5020/ddgs.x86_64

hxxp://111.229.129.150:39127/static/netflix

ddg 5019

hxxp://111.229.129.150:39127/i.sh

hxxp://111.229.129.150:39127/static/5019/ddgs.i686

hxxp://111.229.129.150:39127/static/5019/ddgs.x86_64

## 


