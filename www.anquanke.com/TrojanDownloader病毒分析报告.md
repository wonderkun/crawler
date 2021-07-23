> 原文链接: https://www.anquanke.com//post/id/161100 


# TrojanDownloader病毒分析报告


                                阅读量   
                                **295490**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t010e16f85fa9c95fa2.jpg)](https://p2.ssl.qhimg.com/t010e16f85fa9c95fa2.jpg)

## 零 前言

TrojanDownloader(中文名：文件下载者病毒)主要通过游戏外挂等方式传播。是一款比较早期的病毒样本，已知最早的入库时间是在2008年，其本身危害性不高，但是由于他的作用，其危害性体现在其所下载的恶意代码上。



## 一 目录
- 1.目录
- 2.样本信息
- 3.行为分析
- 4.样本分析
- 5.技术上的总结


## 二 样本分析
- 1.样本名称：sample.WSDump.exe
- 2.样本md5：25a1eb3d3f8767a86050d16c226f9912
- 3.是否加壳：UPX
- 4.编写语言：VC++6.0
- 5.样本来源：网络获取


## 三 行为分析

病毒首先创建互斥体121212，和判断自身文件是否存在，如果存在就启用网络套接字以便执行下一步操作。如果不存在则退出程序。<br>[![](https://i.imgur.com/Up7dPhZ.png)](https://i.imgur.com/Up7dPhZ.png)

在执行体函数中，程序首先初始化一些服务控制器的状态信息，然后创建”Net CLR”的互斥体，接着枚举二进制资源，加载hra33.dll这个dll文件，接下来分别创建三个线程，执行不同的操作。<br>[![](https://i.imgur.com/UfiDvfo.png)](https://i.imgur.com/UfiDvfo.png)



## 四 样本分析

### <a class="reference-link" name="ExecuteFun"></a>ExecuteFun

这个函数是程序的主要执行部分。
- 设置serviceStatus状态
[![](https://i.imgur.com/FLYazwS.png)](https://i.imgur.com/FLYazwS.png)
- 更新资源
- 加载hra33.dll这个动态链接库文件
- 创建三个线程
[![](https://i.imgur.com/Kj8IAzt.png)](https://i.imgur.com/Kj8IAzt.png)

### <a class="reference-link" name="UpdateSource"></a>UpdateSource

这个函数主要是用于更新资源的，但是由于注册表Services.Net CLR不存在导致函数提前退出。<br>[![](https://i.imgur.com/PvxVeFO.png)](https://i.imgur.com/PvxVeFO.png)
- 根据Service注册表下Net CLR文件，创建新文件
[![](https://i.imgur.com/eO39k7g.png)](https://i.imgur.com/eO39k7g.png)
- 然后利用跟新资源的方式让其像一个可执行文件
[![](https://i.imgur.com/A91JbCZ.png)](https://i.imgur.com/A91JbCZ.png)

### <a class="reference-link" name="Thread_1"></a>Thread_1

利用od跟入Thread_1函数。
- 获取本地主机的名称和地址
[![](https://i.imgur.com/4QH59S2.png)](https://i.imgur.com/4QH59S2.png)
- 获取本地网关
[![](https://i.imgur.com/uJrXKab.png)](https://i.imgur.com/uJrXKab.png)<br>[![](https://i.imgur.com/2JGKjbK.png)](https://i.imgur.com/2JGKjbK.png)
- 这里有个病毒作者的错误，本来他想的是如果主机用户是管理员则执行这个判断，但是他直接引用的是字符串，造成判断无效，所有用户都成立
[![](https://i.imgur.com/7VJTb4v.png)](https://i.imgur.com/7VJTb4v.png)
- 利用上面得到的本地网关地址，和用户名及密码作为参数传入CreateFileAndExecuteFun(emmmm不像是真的)。
[![](https://i.imgur.com/dk8oKbI.png)](https://i.imgur.com/dk8oKbI.png)

### <a class="reference-link" name="CreateFileAndExecuteFun"></a>CreateFileAndExecuteFun

程序先与远程主机利用ipc$漏洞创建一个共享的命名管道，用IPC$,连接者甚至可以与目标主机建立一个空的连接而无需用户名与密码(当然,对方机器必须开了ipc$共享,否则你是连接不上的)，而利用这个空的连接，连接者还可以得到目标主机上的用户列表(不过负责的管理员会禁止导出用户列表的)。还可以访问共享资源,并使用一些字典工具，进行密码探测，以至于获得更高的权限。然后黑客从服务端可以利用nc等软件向主机发送一个shell。
- 创建映射方式，以便后期的文件操作，通过WNetAddConnection2A API将共享目录映射为本地磁盘，之后即可按本地文件形式访问文件，最后断开连接。[参考：[http://blog.sina.com.cn/s/blog_672355630102vnwa.html](http://blog.sina.com.cn/s/blog_672355630102vnwa.html)]
[![](https://i.imgur.com/QtFlY04.png)](https://i.imgur.com/QtFlY04.png)
- 把本地文件复制到共享文件的C-E盘
[![](https://i.imgur.com/8jUIjNa.png)](https://i.imgur.com/8jUIjNa.png)

### <a class="reference-link" name="Thread_2"></a>Thread_2
- 获取本地时间和20130221进行比较，如果大于则创建Thread3这个线程执行
[![](https://i.imgur.com/SisWINB.png)](https://i.imgur.com/SisWINB.png)<br>[![](https://i.imgur.com/UFTq1t2.png)](https://i.imgur.com/UFTq1t2.png)

### <a class="reference-link" name="Thread_3"></a>Thread_3
<li>判断链接192.168.1.107是否正常<br>[![](https://i.imgur.com/2pjgCY0.png)](https://i.imgur.com/2pjgCY0.png)
</li>
<li>利用switch 通过接收不同的指令，来决定执行的操作，如下图<br>[![](https://i.imgur.com/PaexMGd.png)](https://i.imgur.com/PaexMGd.png)<ul>
<li>16号：<br>[![](https://i.imgur.com/y4CgGAP.png)](https://i.imgur.com/y4CgGAP.png)
</li>
<li>18号：<br>[![](https://i.imgur.com/Sm9E6nA.png)](https://i.imgur.com/Sm9E6nA.png)
</li>
<li>20号：<br>[![](https://i.imgur.com/UQHocaf.png)](https://i.imgur.com/UQHocaf.png)
</li>
<li>6号：<br>[![](https://i.imgur.com/J1PSmYE.png)](https://i.imgur.com/J1PSmYE.png)
</li>
<li>2号：<br>[![](https://i.imgur.com/4o89JYA.png)](https://i.imgur.com/4o89JYA.png)
</li>
<li>3号：<br>[![](https://i.imgur.com/2Gjuiwp.png)](https://i.imgur.com/2Gjuiwp.png)
</li>
<li>4号：<br>[![](https://i.imgur.com/viggCZX.png)](https://i.imgur.com/viggCZX.png)
</li>
### <a class="reference-link" name="IsConnectFun()"></a>IsConnectFun()
<li>解Base编码得到IP地址：192.168.1.107:83<br>[![](https://i.imgur.com/S6nBGNh.png)](https://i.imgur.com/S6nBGNh.png)
</li>
### <a class="reference-link" name="GetInformationFun"></a>GetInformationFun
<li>识别出当前系统版本信息<br>[![](https://i.imgur.com/UITUJTP.png)](https://i.imgur.com/UITUJTP.png)
</li>
<li>读取注册表，查看CPU的频率<br>[![](https://i.imgur.com/eALSKAq.png)](https://i.imgur.com/eALSKAq.png)<br>[![](https://i.imgur.com/aw2pDqE.png)](https://i.imgur.com/aw2pDqE.png)<br>[![](https://i.imgur.com/ddttIFX.png)](https://i.imgur.com/ddttIFX.png)
</li>
<li>调用 GlobalMemoryStatusEx获取内存信息，<br>[![](https://i.imgur.com/UdVhHfo.png)](https://i.imgur.com/UdVhHfo.png)
</li>
<li>查看网络适配器情况<br>[![](https://i.imgur.com/CCkwTgW.png)](https://i.imgur.com/CCkwTgW.png)
</li>


## 五 技术上的总结

调试程序比较难的地方在于跟入CreateThread创建的线程中，因为OD是单线程调试器，所以不会直接跟入创建的线程(子线程)中，我们采用Sleep函数来跟入线程函数中。
- 找到线程所指向的函数，在函数开头下断
<li>修改调用CreateThread函数下一条语句，写入如下部分
<pre><code class="hljs css">push 100000  ;将Slepp的参数压入
Call Kernel32.Sleep
</code></pre>
</li>
- f8执行，函数自动断在线程函数刚刚下断的地方。
参考自：[https://blog.csdn.net/whatday/article/details/9059281](https://blog.csdn.net/whatday/article/details/9059281)

关于ipc$的使用，参考自[https://blog.csdn.net/smithjackhack/article/details/78559970](https://blog.csdn.net/smithjackhack/article/details/78559970)
