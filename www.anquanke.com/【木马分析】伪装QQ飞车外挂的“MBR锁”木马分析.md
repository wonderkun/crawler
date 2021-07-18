
# 【木马分析】伪装QQ飞车外挂的“MBR锁”木马分析


                                阅读量   
                                **92306**
                            
                        |
                        
                                                                                    



****

**[![](./img/85541/t0180b5e72586800a6d.jpg)](./img/85541/t0180b5e72586800a6d.jpg)**

**0x1 前言**

在过完年开工之际，黑产从业者也回到了他们的工作岗位上，在短短的一周内，相继爆发了“纵情”敲诈者以及伪装QQ飞车外挂的“MBR”敲诈者两款国产敲诈者木马。国产敲诈者在敲诈金额，技术手段以及加密方式上都远远落后于国外的敲诈者木马，但国产敲诈者的最大优点就是能把握住卖点，比如以游戏外挂作为噱头。除此之外，国产敲诈者还喜欢诱导用户关闭杀软以达到所谓的“最佳体验”。可以说，国产敲诈者胜在了“套路”。

本文分析的国产敲诈者即为伪造QQ飞车外挂的“MBR”敲诈者。据受害者称，想使用该QQ飞车外挂软件就必须输入注册码，在向某群管理员索取注册码并输入注册后，计算机立即并被锁住，要求添加一QQ号（3489709452）获取解锁密码。受害计算机如下图所示。

[![](./img/85541/t01aa78620ba540a470.png)](./img/85541/t01aa78620ba540a470.png)

图1 受害计算机界面

可见，计算机并未正常启动，受害者遭遇的就是常见的“MBR”锁。

<br>

**0x2 样本分析**

回到最初的QQ飞车外挂，外挂界面很常见，需要输入注册码才能正常使用。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0168bdf22903678304.png)

图2 外挂界面

细观该外挂界面，发现其和某盾加密处理后的程序界面相似，遍历字符串也能发现一些与某盾加密相关的字符串。因此可以断定该外挂软件使用某盾加密保护，使用者只有输入正确的注册码才能获得相应的功能。由于某盾加密强度高，在不持有密码的情况下很难对受保护的软件进行破解，这也导致外挂使用者需要找管理员要开启密码的情况。急切渴望使用外挂的受害者们在得到开启密码一定是欣喜若狂的，他们一定不知道开启后才是噩梦的开始。

前面提到了某盾加密“在不持有密码的情况下很难对受保护的软件进行破解”，之所以提及“不持有密码的情况下”，是因为即使在拥有密码的情况下，某盾加密对程序的保护也比较特殊。在本例中，进程会在同目录下创建一个名为“飞车通杀辅助VIP2.exe”的程序，并调用ShellExecute函数运行该程序。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b229a7cfa3b7ce63.png)

图3 运行“飞车通杀辅助VIP2.exe”

但实际上，在磁盘中，也就是该路径下并不存在这个文件。这也是某盾加密为了防止加密视频播放时被提取而采取的策略。某盾加密会调用自身SDK中名为“CreateVirtualFileA”的函数在内存中创建文件，而不是直接让文件“落地”，这其实也稍微加大了分析的难度，分析者必须对程序进行patch以使创建的文件“落地”。

patch的位置即“CreateVirtualFileA”函数。根据某盾加密逻辑，程序会首先调用“CreateVirtualFileA”函数创建虚拟文件，然后使用WriteFile函数将解密后的数据写入文件。使用CreateFile函数patch掉“CreateVirtualFileA”可使文件落地。如图所示。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c7fe3a34e05a739a.png)

图4 patch前

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0179d47ed3c04896ef.png)

图5 patch后

对程序进行patch后，执行MBR修改功能的敲诈者主体就“落地”了。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01faa864d265f64fce.png)

图6 “落地”的恶意程序

该程序也是一款定制的程序，可以看出作者只是将一些定制的模块拼接起来构成一个敲诈者木马。从字符串中可以看出，定制者可以自定义MBR加密的密码以及显示在屏幕上的文字。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011be2d0a6e9e851b4.png)

图7 表示可以自定义定制的字符串

之后就是常规的锁MBR流程，打开磁盘0并读取前512字节，也就是主引导记录。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eaa9645e27809fb6.png)

图8 打开磁盘0 

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0173ffdf3d1392d048.png)

图9 读取主引导记录

之后程序会将原本的主引导代码保存到磁盘0偏移0x400起始的位置，该位置是磁盘0的第三扇区。此举用于备份初始的MBR代码，当受害者输入正确的密码之后，就会将备份的MBR代码恢复到第一扇区中，以保证系统能够正常启动。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016c0d8b9803f77ab4.png)

图10 设置偏移

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018b5ff5c35dc3cab1.png)

图11 备份最初的MBR代码

之后程序就会修改主引导记录，修改后的主引导记录如下图所示。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0107e3d77c6f4d8632.png)

图12 被篡改的MBR代码

反汇编MBR代码可以看到密码比较的流程以及之后的处理流程。首先通过int 16h中断获取用户输入，并将存储输入结果。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cfdf7bcb76f5f4c0.png)

图13 获取并存储输入

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017c2d09748469ec63.png)

图14 比较输入与密码

通过查看存放密码的地址可以发现密码为“ O0 ” （即空格，大写字母O，数字0，空格）。在比对成功之后，将通过int 13h中断读取存储在第3扇区的最初的MBR代码并将其写入到第1扇区，以恢复系统的正常使用。

[![](./img/85541/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e4db299e5f958bac.png)

图15 恢复MBR

<br>

**0x3 总结**

通过该样本可以看出，国产敲诈者在技术上并不高深，而且习惯于拼接各种软件或模块，以达到其恶意目的。这些模块虽然互相独立且功能有限，但经过组合之后成为一个功能强大且自保能力强的恶意软件。而这些国产敲诈者也牢牢抓住一些特定用户的注意力，披着外挂的外衣干这坏事，让人措手不及。对于陌生的软件，用户应该慎点，在中毒后也不要轻易添加qq交付赎金，应向杀软方面进行及时反馈以恢复系统的使用。360安全卫士独家推出了“反勒索服务”，用户在安装360安全卫士并开启该服务的情况下，如果防不住各类敲诈者病毒，360负责替用户赔付赎金。
