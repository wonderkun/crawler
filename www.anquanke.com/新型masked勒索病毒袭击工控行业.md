> 原文链接: https://www.anquanke.com//post/id/188715 


# 新型masked勒索病毒袭击工控行业


                                阅读量   
                                **569579**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01f631731e9f2b8cef.jpg)](https://p0.ssl.qhimg.com/t01f631731e9f2b8cef.jpg)



10月9号总部设在荷兰海牙的欧洲刑警组织与国际刑警组织共同发布报告《2019互联网有组织犯罪威胁评估》，报告指出数据已成为网络犯罪分子的主机攻击目标，勒索软件仍是网络安全最大威胁，全球各界需要加强合作，联合打击网络犯罪

尽管全球勒索病毒的总量有所下降，但是有组织有目的针对企业的勒索病毒攻击确实越来越多，给全球造成了巨大的经济损失，勒索软件仍然是网络安全最大的威胁，成为作案范围最广、造成经济损失最严重的网络犯罪形式

朋友发来一个消息，问我中了哪个家族的勒索病毒，如下所示：

[![](https://p1.ssl.qhimg.com/t019fbe486becb66b8a.png)](https://p1.ssl.qhimg.com/t019fbe486becb66b8a.png)

随后朋友发来了勒索的相关信息和病毒样本，此勒索病毒运行之后会修改桌面背景，如下所示：

[![](https://p1.ssl.qhimg.com/t01a3918594c65e2bf6.png)](https://p1.ssl.qhimg.com/t01a3918594c65e2bf6.png)

在每个加密的文件目录下，会生成两个超文件HTML的勒索提示文件，如下所示：

[![](https://p1.ssl.qhimg.com/t01ae577a825a83b96b.png)](https://p1.ssl.qhimg.com/t01ae577a825a83b96b.png)

超文本文件HTML的内容，如下所示：

[![](https://p4.ssl.qhimg.com/t018d109d4cb586c507.png)](https://p4.ssl.qhimg.com/t018d109d4cb586c507.png)

使用TOR打开勒索病毒解密网站，如下所示：

[![](https://p3.ssl.qhimg.com/t0100de69e1942eb95b.png)](https://p3.ssl.qhimg.com/t0100de69e1942eb95b.png)

上面显示了RUSH GANG 1.3，要解密文件，只能通过邮件联系黑客，黑客的邮件联系方式：

[backupyourfiles@420blaze.it](mailto:backupyourfiles@420blaze.it)

该勒索病毒使用了反调试的方法，阻止安全分析人员对样本进行调试分析，如下所示：

[![](https://p2.ssl.qhimg.com/t01bd50b4e03fd028c1.png)](https://p2.ssl.qhimg.com/t01bd50b4e03fd028c1.png)

设置自启动注册表项

HKEY_CURRENT_USERSoftwareMicrosoftWindowsCurrentVersionRun，如下所示：

[![](https://p0.ssl.qhimg.com/t01c8369f11a5c4f772.png)](https://p0.ssl.qhimg.com/t01c8369f11a5c4f772.png)

遍历主机磁盘，如下所示：

[![](https://p2.ssl.qhimg.com/t01aef9ef222cb12d8c.png)](https://p2.ssl.qhimg.com/t01aef9ef222cb12d8c.png)

生成勒索提示超文件HTML文件，如下所示：

[![](https://p5.ssl.qhimg.com/t01c967bf68714ac7f2.png)](https://p5.ssl.qhimg.com/t01c967bf68714ac7f2.png)

将解密出来的勒索提示信息写入到HTML文件中，如下所示：

[![](https://p4.ssl.qhimg.com/t0174459fefeb5e2f22.png)](https://p4.ssl.qhimg.com/t0174459fefeb5e2f22.png)

然后遍历磁盘文件进行加密，加密后的文件后缀为masked，如下所示：

[![](https://p3.ssl.qhimg.com/t01b12ff75b8d14aa85.png)](https://p3.ssl.qhimg.com/t01b12ff75b8d14aa85.png)

此前已经有好几位工控安全的朋友前来咨询我，勒索病毒针对工控行业的攻击似乎也越来越多了，各位工控企业一定要做好勒索病毒的防范措施，以防被勒索病毒勒索加密，千万不能掉以轻心，黑客无时无刻不在寻找着新的攻击目标

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/teM-A-keapn5CKpWr-4G7A)
