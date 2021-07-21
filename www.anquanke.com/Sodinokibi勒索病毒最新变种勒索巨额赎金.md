> 原文链接: https://www.anquanke.com//post/id/194460 


# Sodinokibi勒索病毒最新变种勒索巨额赎金


                                阅读量   
                                **1306890**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t017e28de5dc98f1ccc.jpg)](https://p1.ssl.qhimg.com/t017e28de5dc98f1ccc.jpg)



Sodinokibi勒索病毒在国内首次被发现于2019年4月份，2019年5月24日首次在意大利被发现，在意大利被发现使用RDP攻击的方式进行传播感染，这款病毒被称为GandCrab勒索病毒的接班人，在短短几个月的时间内，已经在全球大范围传播，近日此勒索病毒最新的变种，采用进程注入的方式，将勒索病毒核心代码注入到正常进程中执行勒索加密文件操作

今年六月一号，在GandCrab勒索病毒运营团队停止更新之后，就马上接管了之前GandCrab的传播渠道，经过近半年的发展，这款勒索病毒此前使用了多种传播渠道进行传播扩散，如下所示：

OracleWeblogic Server漏洞<br>
FlashUAF漏洞<br>
RDP攻击<br>
垃圾邮件<br>
水坑攻击<br>
漏洞利用工具包和恶意广告下载（RIG Exploit Kit等）

前两天笔者生病休息了两三天，今天稍微有点好转，最近两天内有好几个朋友咨询Sodinokibi勒索病毒相关问题，是不是又有新的变种出现了？事实上笔者在11月27号的时候就曾捕获到了一批新的Sodinokibi勒索病毒的最新变种，这批Sodinokibi勒索病毒与此前捕获到的Sodinokibi勒索病毒不同，都是DLL文件，不是EXE程序，预感未来几天可能这款勒索病毒会使用进程注入的方式加载这批DLL进行传播感染，这批DLL应该就是勒索病毒团伙新生成的一批勒索病毒核心Payload，用于注入进程使用的

周日，笔者又发现在论坛上有人上传了一个Sodinokibi勒索病毒的最新的样本，如下所示：

[![](https://p0.ssl.qhimg.com/t0140dbe6f7477e96da.png)](https://p0.ssl.qhimg.com/t0140dbe6f7477e96da.png)

上面显示勒索的金额，一台主机最高达4万美金，如下所示：

[![](https://p3.ssl.qhimg.com/t01e401f7e306547825.png)](https://p3.ssl.qhimg.com/t01e401f7e306547825.png)

此样本被人同时在29号的不同时间段上传到了在线分析网站上，猜测这款新的变种可能是29号左右开始传播的，如下所示：

[![](https://p1.ssl.qhimg.com/t01c260bcda7bc5f0c8.png)](https://p1.ssl.qhimg.com/t01c260bcda7bc5f0c8.png)

通过关联，发现此勒索病毒关联到一个服务器IP地址：45.141.84.22，通过微步在线进行查询，如下所示：

[![](https://p4.ssl.qhimg.com/t019d82e2ecd8ff80f5.png)](https://p4.ssl.qhimg.com/t019d82e2ecd8ff80f5.png)

服务器IP地址位于：俄罗斯

此勒索病毒运行之后会启动一个正常进程，笔者主机上启动是vbc.exe进程，如下所示：

[![](https://p2.ssl.qhimg.com/t0112bab28b50400b28.png)](https://p2.ssl.qhimg.com/t0112bab28b50400b28.png)

启动之后，如下所示：

[![](https://p4.ssl.qhimg.com/t0162c09ef309ff522e.png)](https://p4.ssl.qhimg.com/t0162c09ef309ff522e.png)

然后将勒索病毒核心代码注入到启动的vbc.exe进程中执行，如下所示：

[![](https://p3.ssl.qhimg.com/t01c3bd6ecfff497797.png)](https://p3.ssl.qhimg.com/t01c3bd6ecfff497797.png)

将Sodinokibi勒索病毒的核心代码DUMP下来，如下所示：

[![](https://p3.ssl.qhimg.com/t01708b4eca689f24c2.png)](https://p3.ssl.qhimg.com/t01708b4eca689f24c2.png)

加密之后的文件后缀名，如下所示：

[![](https://p2.ssl.qhimg.com/t01f9502085688c3e6f.png)](https://p2.ssl.qhimg.com/t01f9502085688c3e6f.png)

会修改桌面背景图片，如下所示：

[![](https://p1.ssl.qhimg.com/t012d0928039a764aa1.png)](https://p1.ssl.qhimg.com/t012d0928039a764aa1.png)

同时笔者在虚拟机中测试这款勒索病毒的时候有可能会触发蓝屏，可能是注入和结束进程的时候导致的，如下所示：

[![](https://p4.ssl.qhimg.com/t016d62e7db7dc83aaf.png)](https://p4.ssl.qhimg.com/t016d62e7db7dc83aaf.png)

勒索提示信息文件，如下所示：

[![](https://p0.ssl.qhimg.com/t01ddc1d7442947b004.png)](https://p0.ssl.qhimg.com/t01ddc1d7442947b004.png)

获取的样本pdb信息

D:\Coding\!avBTDF17с\bin\Debugrwenc_exe_x86_debug.pdb，猜测最新的版本主要还是为了免杀!av,将核心代码注入正常进程，这批新的变种应该最早是在20号左右编译，27开始传播，29号扩大传播

针对企业的勒索病毒攻击越来越多了，具有很强的针对性，攻击手法也是多种多样，旧的勒索病毒不断变种，新型的勒索病毒又不断出现，基本上每天都有勒索病毒的变种被发现，同时经常有不同的企业被勒索病毒攻击的新闻曝光，真的是数不甚数，随着BTC等虚拟货币的流行，未来勒索病毒的攻击会不会持续增多？勒索病毒已经成为了全球网络安全最大的威胁，各企业要做好相应的防范措施，提高企业员工安全意识，以防中招

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/DSNltCdq8uRmXXxv4eJoJg)
