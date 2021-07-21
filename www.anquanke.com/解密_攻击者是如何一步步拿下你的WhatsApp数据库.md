> 原文链接: https://www.anquanke.com//post/id/82655 


# 解密：攻击者是如何一步步拿下你的WhatsApp数据库


                                阅读量   
                                **72462**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01c0ed5f644a2f9809.jpg)](http://image.3001.net/images/20151006/14441366194874.jpg!small)



针对已root过的安卓移动设备,本文主要讲解远程攻击并解密WhatsApp数据库的详细过程。另外,这再一次提醒我们,对移动设备进行root(安卓)或越狱(iOS),将使用户暴露在黑客攻击之下。

几小时前,网络上发布了一个有趣的文章《[如何远程破解并解密WhatsApp数据库[ROOT]](http://null-byte.wonderhowto.com/how-to/hack-and-decrypt-whatsapp-database-remotely-root-0165015/)》,文中解释了如何从一个root过的安卓系统中提取并解密WhatsApp数据库。尽管通常情况下WhatsApp非常安全,但对安卓设备的root处理将可能使用户暴露在攻击风险之中。

接下来,就让我们一步一步看看作者(使用匿名[F.E.A.R.](http://creator.wonderhowto.com/feardie/))所提出的攻击场景。

步骤1:利用并获取安卓设备的访问权限

正如[这篇指南](http://null-byte.wonderhowto.com/how-to/hack-android-using-kali-updated-and-faq-0164704/)中所解释的,如果安卓设备通过使用Meterpeter命令进行了root,那么这一阶段将变得很简单。



[![](https://p3.ssl.qhimg.com/t0105cb928e31872f00.jpg)](http://image.3001.net/images/20151006/14441368764056.jpg!small)





[![](https://p2.ssl.qhimg.com/t01484360cefa37e99b.jpg)](http://image.3001.net/images/20151006/14441368891790.jpg!small)



为了攻击并解密WhatsApp数据库,攻击者需要一个存在于数据文件夹中的密钥文件,而访问该文件的唯一途径就是拥有root权限。此外,该密钥文件是解密WhatsApp数据库所必不可少的。

步骤2:下载数据库

使用下列命令通过Meterpreter下载数据库:



[![](https://p2.ssl.qhimg.com/t0198fbf80cf9381edb.jpg)](http://image.3001.net/images/20151006/14441370227810.jpg!small)

 



步骤3:提取解密密钥

解密WhatsApp数据库所必需的密钥文件中存储了两套解密密钥,即实际的加密密钥K和一个名为IV的初始化向量。值得一提的是,WhatsApp密钥文件存储在一个安全的位置。下面这些都是提取密钥文件的命令:

正如F.E.A.R.所解释的,这是最困难的部分,特别是如果目标手机用户是有经验且熟练的用户,因为他必须已经安装[SuperSU](https://play.google.com/store/apps/details?id=eu.chainfire.supersu&amp;hl=it)应用程序。

如何诱导受害者安装SuperSU?

可以看一下用户[bart](http://creator.wonderhowto.com/bartvelp/)发布的[这篇教程](http://null-byte.wonderhowto.com/how-to/make-your-malicious-android-app-be-more-),里面解释了如何伪装一个后门应用程序。不过,如果下列场景中的受害者并非是一个有经验的或熟练的用户,那么事情将变得更加简单:

执行以下命令来访问密钥文件夹,并提取解密密钥。

步骤4:下载解密密钥文件到root目录

下载提取的密钥文件到root目录,该目录中还含有加密的WhatsApp数据库:

步骤5:解密WhatsApp数据库

文章中报道了2种不同的方法来解密WhatsApp:

(1)使用Linux命令:每次复制并粘贴一条命令,不要将它们写成一个脚本文件,否则它将不能正常工作:

如果第4行命令不能工作,那么就按下面的指令操作:

(2)第二种方法基于简单的Windows WhatsApp查看器应用程序,可以看一下[原文](http://null-byte.wonderhowto.com/how-to/hack-and-decrypt-whatsapp-database-remotely-root-0165015/)。

这是又一次的教训,对移动设备进行root(安卓)或越狱(iOS),将使用户暴露在黑客攻击之下。
