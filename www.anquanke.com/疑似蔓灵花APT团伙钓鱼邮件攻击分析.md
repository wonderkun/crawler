> 原文链接: https://www.anquanke.com//post/id/96375 


# 疑似蔓灵花APT团伙钓鱼邮件攻击分析


                                阅读量   
                                **237249**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01362e76ec2e0ac9e2.jpg)](https://p2.ssl.qhimg.com/t01362e76ec2e0ac9e2.jpg)

## 背景

近期，360安全监测与响应中心协助用户处理了多起非常有针对性的邮件钓鱼攻击事件，发现了客户邮件系统中大量被投递的钓鱼邮件，被攻击的企业局限于某个重要敏感的行业。360威胁情报中心与360安全监测与响应中心在本文中对本次的钓鱼邮件攻击活动的过程与细节进行揭露，希望企业组织能够引起重视采取必要的应对措施。



## 钓鱼攻击过程

### 钓鱼骗取企业内某用户邮箱密码

上个月某一天，某敏感工业企业邮箱用户收到一份发自mailservicegroup[@]126.com的钓鱼邮件，钓鱼邮件仿冒企业的信息技术中心通知目标用户，声称其邮件账户登录异常，并提示通过“安全链接”验证邮件账户：

[![](https://p2.ssl.qhimg.com/t01f9d983455747ad23.png)](https://p2.ssl.qhimg.com/t01f9d983455747ad23.png)

如果用户访问了该链接会被攻击者收集邮箱用户名以及密码，钓鱼页面观感上与企业的邮箱登录页面高度一致，如果不仔细看对应的URL非常容易上钩。相关钓鱼链接：

```
mail.[被钓鱼企业域名].cn.url.cpasses.char.encoding-http-blog.index.frontend.jtjs.subdomain.alert.check.random-security.018745ssss.url.0j0i67k1j0i131k1j0i20i263k1.0.yqzbceh5jue.enc.http.checksum.webaccess.alert.check.verify.fozanpharma.com
```

### 通过骗取的用户邮箱账号向其它用户发送带有病毒附件的邮件

随后，攻击者会利用收集到的企业邮箱账户向企业内其他用户发送带有病毒附件的邮件，并诱导用户执行病毒附件。由于使用了钓鱼获取的真实企业邮箱账户，看起来来源可信的邮件非常容易导致其它企业邮箱用户被诱导执行恶意附件。

攻击者分别发送伪装成Office Word文档图标和JPG图片的两个病毒样本，并在文件名中加入大量空格以防止目标用户发现文件后缀，从而诱导用户打开执行：

[![](https://p0.ssl.qhimg.com/t018c80d34dac881cc3.png)](https://p0.ssl.qhimg.com/t018c80d34dac881cc3.png)

实际上为可执行程序：

[![](https://p5.ssl.qhimg.com/t012e6d48cfbb76cd67.png)](https://p5.ssl.qhimg.com/t012e6d48cfbb76cd67.png)



## 恶意代码分析

### 恶意附件分析

伪装为Office Word文档和JPG图片的病毒附件最终释放执行相同的木马后门，我们选择伪装为Office Word文档的样本进行分析：

病毒附件Technical Points for review.exe是使用WinRAR生成的自解压程序，该自解压程序的运行逻辑为：在C:\intel\logs目录下释放mobisynce.exe及一个与样本相同名称的正常Office Word文档，然后执行EXE病毒文件同时打开Office Word文档以迷惑受攻击者：

病毒附件执行逻辑：

[![](https://p0.ssl.qhimg.com/t015c8695378e2dac4d.png)](https://p0.ssl.qhimg.com/t015c8695378e2dac4d.png)

打开的诱饵文档内容：

[![](https://p1.ssl.qhimg.com/t01bb13ff72536239f5.png)](https://p1.ssl.qhimg.com/t01bb13ff72536239f5.png)

### mobisynce.exe分析

伪装成Office Word文档的病毒程序最终会在C:\intel\logs目录下释放执行mobisynce.exe，mobisynce.exe运行后首先会对程序中的加密字符串通过与单字节秘钥相加解密出需要使用的字符串：

[![](https://p2.ssl.qhimg.com/t01ed7f85bd0fe564dd.png)](https://p2.ssl.qhimg.com/t01ed7f85bd0fe564dd.png)

紧接着查找当前进程列表名中是否有包含”avg”字符串的进程来判断是否存在avg相关的杀毒软件：

[![](https://p4.ssl.qhimg.com/t0131e18f524ddd43b1.png)](https://p4.ssl.qhimg.com/t0131e18f524ddd43b1.png)

如果不存在与avg相关的杀软进程，则创建新线程，并在该线程中判断是否存在注册表启动项“HKCU\Software\Microsoft\Windows\CurrentVersion\Run\igfxmsw”，以此避免重复执行后续的后门功能，如果不存在该注册表项，则创建后门进程并通过管道的方式接收执行后续的攻击者指令：

[![](https://p2.ssl.qhimg.com/t017e0318688e363681.png)](https://p2.ssl.qhimg.com/t017e0318688e363681.png)

创建注册表启动项“HKCU\Software\Microsoft\Windows\CurrentVersion\Run\igfxmsw”，并设置mobisynce.exe为自启动：

[![](https://p3.ssl.qhimg.com/t01bf3a155efedfec08.png)](https://p3.ssl.qhimg.com/t01bf3a155efedfec08.png)

最后，mobisynce.exe尝试连接C&amp;C控制服务器：wingames2015.com

[![](https://p4.ssl.qhimg.com/t01434d300640250b0a.png)](https://p4.ssl.qhimg.com/t01434d300640250b0a.png)

如果连接成功则开始搜集系统信息并拼装成HTTP GET请求，发送到C&amp;C服务器的ldtvtvqs/accept.php?页面：

[![](https://p0.ssl.qhimg.com/t01ffcd571e881d750d.png)](https://p0.ssl.qhimg.com/t01ffcd571e881d750d.png)

发送的受害主机信息：

[![](https://p1.ssl.qhimg.com/t0175ef9a8572c57b8a.png)](https://p1.ssl.qhimg.com/t0175ef9a8572c57b8a.png)

GET请求中的各参数含义：

[![](https://p2.ssl.qhimg.com/t01d114a8c45aa478b6.jpg)](https://p2.ssl.qhimg.com/t01d114a8c45aa478b6.jpg)

最后，mobisynce.exe会循环监听执行后门命令，具体逻辑为当C&amp;C服务器向木马发送含有”Yes file”字符串的指令时，木马会在指令中提取”[”与”]”中间的命令，并通过ShellExcuteA函数执行该命令：

[![](https://p5.ssl.qhimg.com/t015220f608b60fd1d2.png)](https://p5.ssl.qhimg.com/t015220f608b60fd1d2.png)

根据360网络研究院的大网数据，对于wingames2015.com C&amp;C域名访问在2018年1月3日达到过一个高峰，暗示在这个时间点攻击者曾经发动过一大波攻击：

[![](https://p4.ssl.qhimg.com/t013e9b4379f4ec9e39.png)](https://p4.ssl.qhimg.com/t013e9b4379f4ec9e39.png)



## 溯源和关联

### 钓鱼URL域名信息

钓鱼链接根域名： fozanpharma.com<br>
IP地址： 104.219.248.10<br>
IP归属地：美国亚利桑那州凤凰城<br>
域名创建时间：2017-09-22 14:57:32<br>
域名过期时间：2018-09-22 14:57:32<br>
域名更新时间：2017-09-22 14:57:33

### fozanpharma.com下的其它钓鱼链接

经过后期关联分析，360威胁情报中心与360安全监测与响应中心发现同一域名下针对我国其他三个组织机构的钓鱼邮箱链接：

[![](https://p4.ssl.qhimg.com/t01130e2fbfd8a491ac.png)](https://p4.ssl.qhimg.com/t01130e2fbfd8a491ac.png)

### 与蔓灵花APT团伙的关联分析

360公司曾在2016年11月发布了《中国再次发现来自海外的黑客攻击：蔓灵花攻击行动》（详见参考资料[1]），360威胁情报中心随后发现，伪装为JPG图片的病毒样本所释放的诱饵图片文件也被披露的蔓灵花APT组织使用过：

[![](https://p5.ssl.qhimg.com/t01d0380c4925474ee9.png)](https://p5.ssl.qhimg.com/t01d0380c4925474ee9.png)

并且在后门程序mobisynce.exe中使用的查找avg杀软的相关代码片段与蔓灵花APT组织使用的恶意代码中的代码片段也高度一致：

[![](https://p1.ssl.qhimg.com/t01ffebd6b8e86e1ab6.png)](https://p1.ssl.qhimg.com/t01ffebd6b8e86e1ab6.png)

考虑到我们在背景描述中描述的攻击者动机等因素，我们推测本次的攻击者或与蔓灵花APT团伙可能相关，但目前来看证据还不够充分，希望安全社区来共同完善拼图。



## 总结

从此次攻击者实施的钓鱼邮件攻击来看，攻击者显然尝试利用受害企业员工对信息安全的重视（提示用户邮箱登录异常），并使用最简单的欺骗手法尝试收集员工企业邮箱的用户名密码，再利用正规企业用户邮箱的信任关系发动第二次钓鱼攻击，希望渗透企业员工的计算机系统以获取了相关敏感信息。

360安全监测与响应中心再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。



## IOC

[![](https://p3.ssl.qhimg.com/t01260f5623f435d2b3.jpg)](https://p3.ssl.qhimg.com/t01260f5623f435d2b3.jpg)<br>
参考资料<br>
[1] [https://www.anquanke.com/post/id/84910](https://www.anquanke.com/post/id/84910)
