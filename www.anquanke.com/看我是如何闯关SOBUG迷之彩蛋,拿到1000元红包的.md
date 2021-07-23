> 原文链接: https://www.anquanke.com//post/id/83843 


# 看我是如何闯关SOBUG迷之彩蛋,拿到1000元红包的


                                阅读量   
                                **103515**
                            
                        |
                        
                                                                                    



(附通关名单)<br>

**注:本文由SOBUG彩蛋游戏第一位通关的id_No2015429撰写。**

今天早上10点,终于等来SOBUG安全平台彩蛋游戏的开始。没想到,最终成为第一个通关的人(大牛们这个时候也许在忙工作^_^)。以下是我通关过程的writeup。



[![](https://p0.ssl.qhimg.com/t0136950631dd5c1c62.png)](https://p0.ssl.qhimg.com/t0136950631dd5c1c62.png)

**第一关:**

根据提示“这可以是一张图片,也可以是别的什么”。让我首先想到了应该是写隐术(参加过ctf的都应该会想到)。因此,我首先修改下图片文件后缀为.rar。解压发现了第一个文本:1.txt。



[![](https://p2.ssl.qhimg.com/t0111abe20483da2f7d.png)](https://p2.ssl.qhimg.com/t0111abe20483da2f7d.png)

根据提示“一个是两个,两个是一个”,猜测应该图片还隐藏着什么文件。这时我想到了用binwalk测下。



[![](https://p2.ssl.qhimg.com/t01c5ff234c3c1964be.png)](https://p2.ssl.qhimg.com/t01c5ff234c3c1964be.png)

实践证明我的猜想是对的,可以看出,附加了两个rar压缩包。(其实在刚开始的时候,可以直接用binwalk或者winhex等工具查看图片,就能发现包含两个rar压缩包)。根据起始偏移0x236B7,用winhex将最后一个rar提取出来。



[![](https://p3.ssl.qhimg.com/t010fadd31e9f6ace60.png)](https://p3.ssl.qhimg.com/t010fadd31e9f6ace60.png)

解压得到通关口令:SobugSogood0428,嘿嘿终于到手了~~



[![](https://p5.ssl.qhimg.com/t016075039e374868a7.png)](https://p5.ssl.qhimg.com/t016075039e374868a7.png)

**第二关:**

这么简单肯定不会结束的^_^,接着玩,去拿更大的红包。

根据提示“colin***ky@aol.com  这个邮箱名的背后!除此以外,就没有太多线索了,建议细心加耐心!”,只有个昵称,没有其他的线索,那首先想到的一定是社工手段了。因此,到社工库去查一查。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fc77b9ba6d9a2e98.png)

这时我在想,key要不是在这些密码泄露的网站账户信息里,要不就是这些邮箱里。所以用这些泄露的账号和密码来逐个登录这些网站和邮箱。可结果不是密码不正确,就是没有任何信息。之后,我猜会不会是在qq或者微信上呢。然后根据colin***ky和邮箱分别找到了运维哥们儿的qq和微信。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a7a7b5e86b38b848.png)

可是依旧没什么有用的线索。这时候,我想来想去,觉得线索肯定还是只在colin***ky,会不会是在别的网站上,密码是198***2。之后,用谷歌搜了下colin***ky。看第二个网址: http://bbs.x-kicks.com/space-uid-304562.html。突然想到通关文档里有个‘’用脚都能想到“,刚开始就觉得这句话有点怪,现在大概能猜到应该就是在提示这个“新新球鞋论坛”



[![](https://p5.ssl.qhimg.com/t01bbcd4210e8e746fe.png)](https://p5.ssl.qhimg.com/t01bbcd4210e8e746fe.png)

好的,接着玩,看到这个好久没更新过信息的id,为何在4月20号跟新了信息?有问题,我觉得线索一定在这里。之后,用社工库的账号colin***ky和密码19****2,登录竟然成功了。在联系方式处,看到了有用的线索。



[![](https://p3.ssl.qhimg.com/t01bc2a83b7166cabdc.png)](https://p3.ssl.qhimg.com/t01bc2a83b7166cabdc.png)



[![](https://p2.ssl.qhimg.com/t01662853d07b648b7a.png)](https://p2.ssl.qhimg.com/t01662853d07b648b7a.png)

luzHfQSmGESDYqMC@pass.com这个不是邮箱地址,根据pass,猜测应该是个密码,根据@xxx.com猜测应该是邮箱的密码。这里首先想到的,就是用colin***ky@aol.com这个邮箱去登录(不然就不会给这个邮箱提示了^_^)。密码:luzHfQSmGESDYqMC,登录成功啦。哇靠。

把收件箱,发件箱都看了一遍。发现草稿里保存的一封邮件,应该是重要提示。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0173f25a7c05c4195f.jpg)

提示“用这个邮箱把密钥和微信号发过去”,最终应该是通过邮件来确认的。但是,密钥Key是什么呢。这里看到“两个时间”字体被加粗了。眼前一亮,嗯,这个应该是线索。考虑了下,邮件里那个些和会和时间有关呢?找来找去,那就只有Events这个菜单了。但是,Event显示为空。这时展开下拉按钮,点击“Calendar”,出现了信息。正好是4月28日和4月18日。这一定就是key了。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01319e3a9514e7945f.jpg)



[![](https://p2.ssl.qhimg.com/t01ddaa4fa1a2aacbfc.jpg)](https://p2.ssl.qhimg.com/t01ddaa4fa1a2aacbfc.jpg)

<br>

两天的内容拼在一起是:

U09CVUfmlrDlubPlj7A05pyIMjjml6XmrKLov47kvaDnmoTliLDmnaU2SDdKR0pJS0pINks2RzdKSEZENkdIRjc2SDhINyAoRU5EKQ==

Base64解码后正好是:

SOBUG新平台4月28日欢迎你的到来6H7JGJIKJH6K6G7JHFD6GHF76H8H7 (END)

和我的微信一起用这个邮箱,发送给hd@sobug.com。至此,通关结束。1000元红包终于拿到手啦,哈哈。

这次闯关我觉得是够烧脑的了,需要很细心地去捕捉每一个细节所释放的信息,如果中间漏过一点,可能就要走不少弯路了。这和漏洞测试实际上是一个道理,再安全的保护,只要细心+耐心去找,一定能够找到可以被利用的地方。或许是运气好吧,不管怎样,我的目的最终达到啦。按照自己逻辑走,让每一个线索和细节成为下一站的指引,真的是一件很兴奋的事啊。以后希望多一点这样的好玩的游戏,也预祝SOBUG新平台成功上线,让更多的白帽子来做有意思和有意义的事。

**小编有话说:**

其实SOBUG做这样一款游戏的初衷有两个,一个当然是为新平台的上线促活引流,另外则是希望大家和厂商的安全意识和责任意识得到提高。这个游戏的核心环节就是社工库,如果没有社工库的密码泄露,根本没有办法去猜测、知晓一个陌生账号的密码习惯、参加的论坛、留下的足迹等等。一个人的爱好、习惯本身就属于自己人生的记录,没有人能够干涉。而我们相信,这样的世界,是美好的。

我们不反对社工库的公开,正是它的存在才使得人们意识到自己的信息是如此脆弱。我们希望,有更多的厂商能够负起责任,保护好用户的个人信息,把皮带扎紧。

毕竟,一切非你情我愿的的脱裤,都是耍流氓。

**附通关名单:**

第一名:id_No2015429 (作者本人)|12:05 (500元现金+500元SOBUG积分) 

第二名:做个好人 |15:04(300元现金+300元SOBUG积分)

第三名:FireKy1in |16:50 (10-30元支付宝红包)

第四名:01dDriver |17:42 (10-30元支付宝红包)

第五名:snRNA |17:44 (10-30元支付宝红包)

祝贺以上同学,奖励将于近期微信发放。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015148983c010c0452.png)
