> 原文链接: https://www.anquanke.com//post/id/86606 


# 【病毒分析】假勒索真愤青：永久摧毁文件的israbye病毒分析


                                阅读量   
                                **76404**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t018c69b53851e1d7be.png)](https://p4.ssl.qhimg.com/t018c69b53851e1d7be.png)



**简介**

****

近期，360安全中心发现国内流入一款名为israbye的“伪勒索病毒”。与普通勒索病毒完全不同的是，israbye会**彻底摧毁文件**，即使付钱也无法恢复。而且，病毒想要的也根本不是钱。

<br>

**一探究竟**

****

该病毒在受害电脑展示的信息称可保证免费恢复文件，但前提是——“**等他们收复巴勒斯坦，收复艾克萨……**”此病毒的传播目的似乎是为了传递某种主张。上述信息除了英文版本外，还罕见地对应了一段希伯来语，再结合“END OF ISRAEL（以色列的终结）”的标题，并不是以钱财为目的的勒索病毒。

值得注意的是，被israbye病毒破坏的文件也不存在恢复的可能性。它会把文件内容将统一替换成“Fuck-israel, *** You Will never Recover your Files Until Israel disepeare”（其中星号为病毒从中毒机器中获取的用户名），而文件后缀则被更改为.israbye。这种方式下“加密”的文件，终究是等不到恢复的那一天的。

此病毒使用VS2012编写，从病毒程序中记录的pdb信息来看，病毒作者的用户名为Ahmed：

 [![](https://p5.ssl.qhimg.com/t014635e6efccbb8d25.png)](https://p5.ssl.qhimg.com/t014635e6efccbb8d25.png)

执行后，病毒首先会获取系统的启动目录和临时目录，并将自身复制到临时目录下命名为ClickMe.exe，之后向启动目录下释放**cry.exe**、**cur.exe**、**lock.exe**、**index.exe**四个程序：

 [![](https://p4.ssl.qhimg.com/t01615337b6298112ae.png)](https://p4.ssl.qhimg.com/t01615337b6298112ae.png)

释放完成后，先加密当前用户目录，之后再遍历磁盘电脑所有盘符，循环加密所有文件（循环从1开始，即跳过C盘不加密）：

 [![](https://p2.ssl.qhimg.com/t01e76b750c8406790d.png)](https://p2.ssl.qhimg.com/t01e76b750c8406790d.png)

最后就是启动刚刚释放的四个程序并删除自身：

 [![](https://p4.ssl.qhimg.com/t0155b586cb34e88d7b.png)](https://p4.ssl.qhimg.com/t0155b586cb34e88d7b.png)

病毒释放的四个衍生程序也是各司其职，工作比较单一。

衍生物cry.exe负责调用修改壁纸：

 [![](https://p5.ssl.qhimg.com/t011bff82015fcc7641.png)](https://p5.ssl.qhimg.com/t011bff82015fcc7641.png)

 [![](https://p2.ssl.qhimg.com/t018b51c4b5b179f750.png)](https://p2.ssl.qhimg.com/t018b51c4b5b179f750.png)

衍生物cur.exe负责在鼠标指针后添加一个“**END OF ISRAEL**”的小尾巴

 [![](https://p0.ssl.qhimg.com/t013e43a4cb9dd67e0c.png)](https://p0.ssl.qhimg.com/t013e43a4cb9dd67e0c.png)

[![](https://p3.ssl.qhimg.com/t01a7b7b47d89448c81.png)](https://p3.ssl.qhimg.com/t01a7b7b47d89448c81.png)

衍生物index.exe负责弹出信息说明窗口，并释放并播放一段bgm

 [![](https://p2.ssl.qhimg.com/t01c20310371d420fbb.png)](https://p2.ssl.qhimg.com/t01c20310371d420fbb.png)

 [![](https://p2.ssl.qhimg.com/t01e09d3e281d737961.png)](https://p2.ssl.qhimg.com/t01e09d3e281d737961.png)

衍生物lock.exe则负责“解决掉”一些分析人员的常用工具，同时启动上面的index.exe和病毒主程序“ClickMe.exe”

 [![](https://p1.ssl.qhimg.com/t017dfa29b9f2f84638.png)](https://p1.ssl.qhimg.com/t017dfa29b9f2f84638.png)

 [![](https://p3.ssl.qhimg.com/t011d1a0af640901718.png)](https://p3.ssl.qhimg.com/t011d1a0af640901718.png)



**真相大白**

****

最后，我们回到病毒母体的加密函数部分，这也就是我们称其为“伪勒索病毒”的关键点——病毒实际上根本就没有“加密”你的文件，仅仅是将文件内容替换为“Fuck-israel, *** You Will never Recover your Files Until Israel disepeare”而已。

 [![](https://p1.ssl.qhimg.com/t01807daa5a198ea174.png)](https://p1.ssl.qhimg.com/t01807daa5a198ea174.png)

由此可见，虽然病毒声称要等到以色列毁灭（Israel disepeare）的那一天才能恢复你的文件，但很显然以这样的方式来“加密”文件，是无论等到哪一天都无法恢复的。

据360安全卫士监控的数据，israbye病毒在国内传播量很小，但如果不慎中招就会遭遇数据永久损坏的严重后果。360安全卫士已第一时间拦截查杀此病毒，建议用户保持安全软件开启，就能够避免中招。

[![](https://p1.ssl.qhimg.com/t0154faefb3e471ff4f.png)](https://p1.ssl.qhimg.com/t0154faefb3e471ff4f.png)


