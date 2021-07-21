> 原文链接: https://www.anquanke.com//post/id/85673 


# 【技术分享】看我如何黑掉西部数码的NAS设备（含演示视频）


                                阅读量   
                                **89165**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：exploitee.rs
                                <br>原文地址：[https://blog.exploitee.rs/2017/hacking_wd_mycloud/](https://blog.exploitee.rs/2017/hacking_wd_mycloud/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p3.ssl.qhimg.com/t012e98154f34f168f5.jpg)](https://p3.ssl.qhimg.com/t012e98154f34f168f5.jpg)

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**传送门**

[**【技术分享】动手教你来挖西部数据NAS的漏洞**](http://bobao.360.cn/learning/detail/3611.html)

**<br>**

**一、前言**

在我们的安全研究工作中，有时候是我们主动去找设备安全漏洞，有时候是设备自动找上我们。今天我们要谈的是后一种情况：关于我们在西部数据NAS（网络附加存储，Networked Attached Storage）设备方面的安全研究工作。

去年年中时，我（Zenofex）需要为我的Plex媒体播放器寻找一款支持硬件解码的NAS设备。经过一番研究，我最终订购了西部数据的一款NAS：MyCloud PR4100。这款设备满足我的一切需求，同时也得到了一个朋友的强烈推荐。在将NAS添加到我的网络环境中、首次访问设备的管理页面后，我对在缺乏安全审计下将新设备添加到网络这一过程感到越来越厌烦。因此我打开NAS的SSH接口，研究一下其内部的Web服务器的工作机制。

<br>

**二、登录认证绕过漏洞**

我找到的第一个漏洞是登录认证绕过漏洞，这个漏洞存在于一段通过cookie或PHP session变量实现用户登录检查的代码中。使用cookie进行验证并不一定是不好的，但在西数MyCloud登陆界面上这种方法实现上存在漏洞。仔细阅读以下代码：

代码文件：/lib/login_checker.php

```
function login_check()
`{`
        $ret = 0;
        if (isset($_SESSION['username']))
        `{`
                if (isset($_SESSION['username']) &amp;&amp; $_SESSION['username'] != "")
                $ret = 2; //login, normal user
                if ($_SESSION['isAdmin'] == 1)
                        $ret = 1; //login, admin
        `}`
        else if (isset($_COOKIE['username']))
        `{`
                if (isset($_COOKIE['username']) &amp;&amp; $_COOKIE['username'] != "")
                $ret = 2; //login, normal user
                if ($_COOKIE['isAdmin'] == 1)
                        $ret = 1; //login, admin
        `}`
        return $ret;
`}`
```

上述代码中包含一个login_check函数，为所有的后端PHP脚本提供服务，用来对用户进行预认证检查。上述代码存在两个路径，一个用来检查“username”及“isAdmin”会话值，另一个尝试使用cookie值完成同样工作。由于cookie是由用户提供的，因此攻击者可利用cookie尝试攻击。上述代码的工作流程可以归结为：

1、若“username”变量存在且值不为空，则用户以普通权限登录。

2、若“isAdmin”变量设置为1，则用户以管理员权限登陆。

这意味着只要登录检查过程涉及到PHP脚本，攻击者就可以使用2个精心构造的cookie值绕过登录检查。

在我写这篇文章的过程中，西数发布了一个新的固件，修复了上述漏洞。然而这个补丁同样存在登录验证绕过漏洞。以下为打过补丁的代码片段：

文件：/var/www/web/lib/login_checker.php 

```
20 function login_check()
 21 `{`
 22         $ret = 0;
 23 
 24         if (isset($_SESSION['username']))
 25         `{`
 26                 if (isset($_SESSION['username']) &amp;&amp; $_SESSION['username'] != "")
 27                 $ret = 2; //login, normal user
 28 
 29                 if ($_SESSION['isAdmin'] == 1)
 30                         $ret = 1; //login, admin
 31         `}`
 32         else if (isset($_COOKIE['username']))
 33         `{`
 34                 if (isset($_COOKIE['username']) &amp;&amp; $_COOKIE['username'] != "")
 35                 $ret = 2; //login, normal user
 36 
 37                 if ($_COOKIE['isAdmin'] == 1)
 38                         $ret = 1; //login, admin
 39 
 40                 if (wto_check($_COOKIE['username']) === 0) //wto check fail
 41                         $ret = 0;
 42         `}`
 43 
 44         return $ret;
 45 `}`
 46 ?&gt;
```

在新的代码中，调用了一个新的方法“wto_check()”（第40行）。该方法运行了设备上的一个程序，以用户提供的用户名及用户IP作为参数。如果用户当前处于已登录未超时状态，则函数返回1，否则返回0（代表用户未登录）。“wto_check()”方法具体代码如下：

文件：/var/www/web/lib/login_checker.php 

```
3 /*
  4   return value: 1: Login, 0: No login
  5 */
  6 function wto_check($username)
  7 `{`
  8         if (empty($username))
  9                 return 0;
 10 
 11         exec(sprintf("wto -n "%s" -i '%s' -c", escapeshellcmd($username), $_SERVER["REMOTE_ADDR"]), $login_status);
 12         if ($login_status[0] === "WTO CHECK OK")
 13                 return 1;
 14         else
 15                 return 0;
 16 `}`
 17 
 18 /* ret: 0: no login, 1: login, admin, 2: login, normal user */
```

上述代码中，第11行调用了wto程序，参数为用户名及IP地址。代码存在的问题是对PHP中“escapeshellcmd()”函数的错误使用，该函数本来是用来处理整个命令字符串的，而不单单是处理一个参数。具体来说，“escapeshellcmd()”函数没有对引号进行转义，攻击者可以跳出参数的转义限制（本例中是“-n”参数），将新的参数传递给程序。基于这一点，我们可以添加新的参数，自行决定用户登录状态，而不需要实际检查用户是否登录成功。虽然我们不认为简单地判断IP地址和登录超时就足以确定用户的登录状态，但此例中，编写这段代码的程序员应该使用“escapeshellarg()”函数来达到这一目的，该函数可以对二进制参数进行过滤，同时可以转义引号。本例中，相对于使用“escapeshellcmd()”函数，使用“escapeshellarg()”函数可以阻止这类攻击的生效。

<br>

**三、命令注入漏洞**

WDCloud Web服务的主要功能实际上是由设备上的CGI脚本进行处理的。大多数脚本使用的是相同的模式，它们从请求中提取post/get/cookie值，在PHP调用中使用这些值来执行shell命令。在大多数情况下，这些命令会直接使用用户提供的输入，很少或基本没有对输入进行处理。比如，我们检查从设备中提取的代码：

文件：php/users.php

```
15 $username = $_COOKIE['username'];
16 exec("wto -n "$username" -g", $ret);
```

上述代码从超全局变量（superglobal）COOKIE中提取值（该值包括用户通过请求提交的cookie数组索引），将值赋到本地变量“$username”中，随后传递给PHP的“exec()”函数，最终作为一个参数由wto使用。由于这个过程中不涉及对用户提交数据的处理，因此如果我们使用如下类似的用户名：

```
username=$(touch /tmp/1)
```

那么执行命令就会变为：

```
wto -n "$(touch /tmp/1)" -g
```

最终服务器会执行用户提交的内部命令。

因为代码使用了双引号对参数进行封装，而我们使用了“$(COMMANDHERE)”这中格式的语法，因此“touch /tmp/1”命令会先于“wto”命令执行，执行的返回结果会作为“wto”命令的“-n”参数。这种类型的命令注入漏洞经常可以在针对Web的攻击脚本中看到。此类攻击通常会被认证过程所阻拦，但在本例中，结合前面的认证绕过漏洞我们就可以轻松达成攻击目的。另外，需要注意的是，上述执行的命令都是利用Web服务器来完成的，注入命令会获得与Web服务器一致的权限，本例中为root权限。

<br>

**四、其他漏洞**

上述漏洞看起来已经很严重了，然而在Web服务中还存在许多漏洞，有些与认证绕过漏洞一样，我们很容易就可以找出来（以注释形式标出）：

文件：addons/ftp_download.php

```
6 //include ("../lib/login_checker.php");
7 //
8 ///* login_check() return 0: no login, 1: login, admin, 2: login, normal user */
9 //if (login_check() == 0)
10 //`{`
11 //      echo json_encode($r);
12 //      exit;
13 //`}`
```

有些漏洞更具有功能性，如以下代码存在漏洞，允许非认证用户上传文件到myCloud设备中。

文件：addons/upload.php

```
2 //if(!isset($_REQUEST['name'])) throw new Exception('Name required');
3 //if(!preg_match('/^[-a-z0-9_][-a-z0-9_.]*$/i', $_REQUEST['name'])) throw new Exception('Name error');
4 //
5 //if(!isset($_REQUEST['index'])) throw new Exception('Index required');
6 //if(!preg_match('/^[0-9]+$/', $_REQUEST['index'])) throw new Exception('Index error');
7 //
8 //if(!isset($_FILES['file'])) throw new Exception('Upload required');
9 //if($_FILES['file']['error'] != 0) throw new Exception('Upload error');
10 
11 $path = str_replace('//','/',$_REQUEST['folder']);
12 $filename = str_replace('\','',$_REQUEST['name']);
13 $target =  $path . $filename . '-' . $_REQUEST['index'];
14 
15 //$target =  $_REQUEST['folder'] . $_REQUEST['name'] . '-' . $_REQUEST['index'];
16 
17 move_uploaded_file($_FILES['file']['tmp_name'], $target);
18 
19 
20 //$handle = fopen("/tmp/debug.txt", "w+");
21 //fwrite($handle, $_FILES['file']['tmp_name']);
22 //fwrite($handle, "n");
23 //fwrite($handle, $target);
24 //fclose($handle);
25 
26 // Might execute too quickly.
27 sleep(1);
```

上面代码漏洞包括未对用户进行认证检查，在上传文件时直接使用用户提供的路径确定文件的本地存放路径。

除了本文中列出的漏洞之外，我们在wiki中还收集了MyCloud Web服务的其他漏洞。我们的目标是厂商能够尽快对漏洞进行修复，然而，大量严重漏洞的发现意味着我们在厂商发布补丁后，还需要重新对产品进行评估。

<br>

**五、责任说明**

我们通常会与厂商合作以确保漏洞的正确披露时间。然而，在参观了维加斯黑帽大会的“Pwnie Awards”后，我们更加了解了厂商在安全社区中的“声誉”。在忽略了用户提交的一组严重漏洞报告的前提下，厂商依然获得了“Pwnie for Lamest Vendor Response”奖项。忽略这些漏洞会导致存在漏洞的设备更久地暴露在互联网中，在漏洞细节披露后这些设备会更加危险。因此我们尝试向社区告知这些安全警告，希望用户能将漏洞设备从互联网中下线，并尽可能地限制设备的访问渠道。经过这些披露过程后，我们公开了我们的研究细节，希望这样能够加速厂商给用户提供补丁。

<br>

**六、漏洞统计**

1x 登录认证绕过漏洞

1x 任意文件写入漏洞

13x 未授权远程命令执行漏洞

70x 已授权远程命令执行漏洞（可以与登录认证绕过漏洞配合使用）

<br>

**七、影响范围**

大多数漏洞影响了西部数据MyCloud产品的所有类别。包括以下类别：

```
My Cloud
My Cloud Gen 2
My Cloud Mirror
My Cloud PR2100
My Cloud PR4100
My Cloud EX2 Ultra
My Cloud EX2
My Cloud EX4
My Cloud EX2100
My Cloud EX4100
My Cloud DL2100
My Cloud DL4100
```

<br>

**八、更多信息**

西数MyCloud产品漏洞的详细列表及细节可以访问[Exploitee.rs Wiki](https://www.exploitee.rs/index.php/Western_Digital_MyCloud)查看。

关注[@Exploiteers](https://twitter.com/exploiteers)可接受wiki中西数产品的相关内容。

<br>

**九、漏洞视频**



**传送门**

[**【技术分享】动手教你来挖西部数据NAS的漏洞**](http://bobao.360.cn/learning/detail/3611.html)


