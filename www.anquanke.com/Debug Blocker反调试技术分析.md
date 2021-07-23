> 原文链接: https://www.anquanke.com//post/id/100115 


# Debug Blocker反调试技术分析


                                阅读量   
                                **121145**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0123a7d3d1733a611f.png)](https://p5.ssl.qhimg.com/t0123a7d3d1733a611f.png)

## 一、    前言

Debug Blocker是一种比较繁琐的反调试技术，常常应用在一些PE保护器中，

在CTF逆向题目中，也常有出现。本文结合一个Debug Blocker的示例程序，讲解该反调试技术的原理，然后以一道CTF逆向题目为例，使用两种方法进行逆向。

本文章示例可以在这里下载：https://github.com/b1ngoo/crack



## 二、    原理

### （1）定义及特征

Debug Blocker技术是进程以调试模式运行自身或者其他可执行文件的技术。在一般运用该技术的程序中，父进程作为调试器，通过调用CreateProcess函数的方式以调试模式创建子进程，这时子进程就作为被调试者，调试者和被调试者执行不同的代码。看如下示例程序（示例程序来自于逆向工程核心原理附带源码）：

[![](https://p3.ssl.qhimg.com/t011563e0c3fe795e44.png)](https://p3.ssl.qhimg.com/t011563e0c3fe795e44.png)

在上面这个例子中，父进程在控制台中打印出了Parent Process，然后创建子进程调用MessageBox() API弹窗。

由于在Windows中，一个进程无法被多个调试器进行调试，所以如果关键算法代码运行于被调试的子进程中，因为子进程与父进程之间构成调试者与被调试者的关系，就自然的形成了反调试作用，使得我们难以动态调试。

值得注意的是，调试器-被调试者关系中，被调试进程中发生的所有异常均由调试器处理。如果被调试的子进程故意触发某个异常，该异常会被交付到调试器进行处理，在异常会被处理之前，子进程无法接着运行。另一方面，如果终止调试进程，被调试进程也会随之终止。以上等等特征，使得Debug Blocker可以作为一种反调试的技术。

接下来，我们结合源码进行分析该技术作用的具体过程。

### （2）代码分析

示例程序源码来自于《逆向工程核心原理》57章示例代码。

首先从整体上看看这个代码：

```
void DoParentProcess(); // 父进程函数

void DoChildProcess();  // 子进程函数



void _tmain(int argc, TCHAR *argv[])

`{`

    HANDLE      hMutex = NULL;


    if( !(hMutex = CreateMutex(NULL, FALSE, DEF_MUTEX_NAME)) )

    `{`

        printf("CreateMutex() failed! [%d]\n", GetLastError()); // 创建mutex失败

        return;

    `}`


    // 检查mutex，判断子进程和父进程

    if( ERROR_ALREADY_EXISTS != GetLastError() )

        DoParentProcess();

    else

        DoChildProcess();

`}`
```

整个代码结构十分简单（该程序只是一个示例），包括主函数，父进程函数DoParentProcess()和子进程函数DoChildProcess()。在主函数中，通过创建同名互斥体的方式判断进程是以子进程出现还是以父进程出现：当程序以父进程首先运行的时候，创建一个DEF_MUTEX_NAME互斥体，此时GetLastError为0：

[![](https://p4.ssl.qhimg.com/t0148a3220518b8097c.png)](https://p4.ssl.qhimg.com/t0148a3220518b8097c.png)

并且ERROR_ALREADY_EXISTS在WinError.h头文件中定义为：

[![](https://p1.ssl.qhimg.com/t01276219d984ebb7b0.png)](https://p1.ssl.qhimg.com/t01276219d984ebb7b0.png)

如果是子进程，由于父进程已经创建了互斥体对象，会报Last Error=183，就会进入子进程函数分支。

接着进入DoParentProcess()，首选是通过CreateProcess() API的方式创建调试进程：

```
// 创建调试进程

    GetModuleFileName(

        GetModuleHandle(NULL),

        szPath,

        MAX_PATH);


    if( !CreateProcess(

            NULL,

            szPath,

            NULL, NULL,

            FALSE,

            DEBUG_PROCESS | DEBUG_ONLY_THIS_PROCESS,  // 调试进程参数

            NULL, NULL,

            &amp;si,

            &amp;pi) )

    `{`

        printf("CreateProcess() failed! [%d]\n", GetLastError());

        return;

    `}`


printf("Parent Process\n");
```

创建进程没有问题的话打印字符串并进入一个死循环，在每个循环中，开始都用WaitForDebugEvent() API等待子进程异常出现。在这个判断Debug事件类型位置下断点，观察dwDebugEventCode的变化：

[![](https://p4.ssl.qhimg.com/t01619b834a33731c3f.png)](https://p4.ssl.qhimg.com/t01619b834a33731c3f.png)

可以看到第一次dwDebugEventCode=3，可以知道这是一个CREATE_PROCESS_DEBUG_EVENT事件：

[![](https://p5.ssl.qhimg.com/t011d39895e00de7b77.png)](https://p5.ssl.qhimg.com/t011d39895e00de7b77.png)

这是被调试进程运行时最初发生的事件。这时候我们看看子进程函数：

```
void DoChildProcess()

`{`

    // 需要在Ollydbg中修改

    __asm

    `{`

       nop

       nop

    `}`


    MessageBox(NULL, L"ChildProcess", L"TEST", MB_OK);

`}`
```

其实为了达到反调试的目的，子进程函数需要在编译连接为可执行文件后，在Ollydbg中进行修改。需要修改三个地方：
- nop修改为8D C0（LEA EAX,EAX非法指令）
- PUSH “Child Process”指令这两个字节也修改为8D C0
- 将MessageBox()函数调用过程指令（共20个字节）与0x7F进行异或
[![](https://p0.ssl.qhimg.com/t0189f8cb3f5f27c8d4.png)](https://p0.ssl.qhimg.com/t0189f8cb3f5f27c8d4.png)

在子进程运行过程中，我们只关心子进程的EXCEPTION_DEBUG_EVENT事件，并且异常类型为EXCEPTION_ILLEGAL_INSTRUCTION（非法指令），这个错误是由于我们故意在子进程函数开始位置写下LEA EAX，EAX非法指令导致的，这个指令异常的原因是由于指令格式不对，第二个操作数需要是内存。

在上面那个图片中，第一个LEA EAX,EAX出现在地址0x0040103F位置，这个位置是硬编码的，所以该程序没有支持基址重定位，可以在FFI工具中看一下基址重定位目录：

[![](https://p0.ssl.qhimg.com/t017b336b50bef60878.png)](https://p0.ssl.qhimg.com/t017b336b50bef60878.png)

如果在子进程在0x0040103F发生非法指令异常，该异常会被提交到父进程处理，处理代码如下：

```
if( dwExcpAddr == EXCP_ADDR_1 )  // 第一次非法指令异常

                `{`

                    // decoding

                    ReadProcessMemory(  // 读子进程内存空间

                        pi.hProcess,

                        (LPCVOID)(dwExcpAddr + 2),

                        pBuf,

                        DECODING_SIZE,

                        NULL);


                    for(DWORD i = 0; i &lt; DECODING_SIZE; i++)  // 进行异或解码

                        pBuf[i] ^= DECODING_KEY;


                    WriteProcessMemory( // 写回子进程内存空间

                        pi.hProcess,

                        (LPVOID)(dwExcpAddr + 2),

                        pBuf,

                        DECODING_SIZE,

                        NULL);

                   

                    // 修改EIP

                    ctx.ContextFlags = CONTEXT_FULL;

                    GetThreadContext(pi.hThread, &amp;ctx);

                    ctx.Eip += 2;

                    SetThreadContext(pi.hThread, &amp;ctx);

                `}`
```

整个代码逻辑十分清楚，就是一个读子进程内存空间，然后解码并写回的过程，最后调整一下EIP。处理完异常之后，通过ContinueDebugEvent让子进程接着执行：

```
ContinueDebugEvent(de.dwProcessId, de.dwThreadId, DBG_CONTINUE);  // 异常处理完毕，接着执行子进程
```

解码完毕后，子进程接着执行，这时候会发生第二次非法指令异常，位置在0x00401048，这时候的处理方法就比较简单了，直接patch就可以。

综上所述，Debug Blocker反调试技术可以看做是一个动态Patch的过程，子进程函数如果直接静态用IDA看的话，由于没有Patch，所以这段代码是被加密的。如果尝试调试子进程的话，由于存在调试者-被调试者的关系，导致子进程无法被调试器Attach。

不过还是有办法解决的，接下来部分我将结合一道运用Debug Blocker的CTF逆向题目，使用两种方法进行逆向。



## 三、    例题

这个题目来自于CFF 2016的一个逆向题目：软件密码破解-2。现在在一位大

师傅做的OJ（Jarvis OJ）上可以做。这里给出题目程序和我打好patch的程序：[https://github.com/b1ngoo/crack](https://github.com/b1ngoo/crack)  经过patch后的程序可以在IDA 7.0中反编译。

这个题目网上已经有不少WriteUp了，不过基本都是看懂这个程序流程之后，手动打Patch再看子进程做的，这种方法对付这种关键算法比较简单的程序还挺方便的，如果难一点，需要动态调试这个子进程代码就不行了，这里两种方法都介绍一下吧。

### （1）方法1

这种方法使得我们可以直接调试子进程，大致顺序如下：
- 将子进程要分析的代码设置为无限循环
- 将父进程与从子进程中分离（Detach）
- 使用Ollydbg附加子进程进行调试
首先Ollydbg加载题目程序，调试的时候尽量用原版的OD调试，因为吾爱OD或者其他插件可能会导致一些异常被忽略（比如Strong OD插件），在0x 004013BF位置下断点看子进程的hProcess，输入，然后断下来：

[![](https://p2.ssl.qhimg.com/t01f66a042abce82725.png)](https://p2.ssl.qhimg.com/t01f66a042abce82725.png)

记下这个值hProcess=0x2C，接着执行，接着在0x004013FC位置下断点，记录ThreadId=0xF6C和ProcessId=0x224（不同环境中其值并不相同）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012a300341a8438e1c.png)

这个时候，子进程的代码已经被父进程修复过了，如果现在接着执行ContinueDebugEvent()函数，子进程就会接着正常执行了，现在就是我们调试这个子进程的机会。

通过OD对父进程的进程空间进行修改，再次执行WriteProcessMemory() API将子进程的添加一个无限循环，方法如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c127881183bf3e03.png)

然后调用ContinueDebugEvent函数让子进程再次跑起来：

[![](https://p5.ssl.qhimg.com/t012963ed1b38937fa8.png)](https://p5.ssl.qhimg.com/t012963ed1b38937fa8.png)

为了让OD可以Attach子进程进行调试，需要解除父进程与子进程的调试者-被调试者的关系，我们可以使用DebugActiveProcessStop() API进行Detach（分离）：

[![](https://p3.ssl.qhimg.com/t0191369c7278c17656.png)](https://p3.ssl.qhimg.com/t0191369c7278c17656.png)

依次执行这些指令，就可以解除父进程与子进程的调试者-被调试者的关系，然后使用OD附加子进程调试，如果遇到系统断点直接F9运行，然后F12暂停，OD就在当前运行的代码位置暂定了：

[![](https://p1.ssl.qhimg.com/t016b237be598079313.png)](https://p1.ssl.qhimg.com/t016b237be598079313.png)

然后根据静态分析的结果，将前面无限循环的两个字节写回就可以了：

[![](https://p4.ssl.qhimg.com/t01a6ccdc217e4de846.png)](https://p4.ssl.qhimg.com/t01a6ccdc217e4de846.png)

接着就可以愉快的调试了，具体算法说明看下面静态部分方法2吧。

### （2）方法2

这个方法就是看IDA，结合OD动态调试搞懂sub_401180函数，然后就可以知道这个程序的逻辑是这样的：

直接执行程序，通过输入传参的方式，执行流到第一个分支，进入sub_401180函数，在该函数中，通过CreateProcess函数运行自身，并通过命令行的传参的方式把输入传给该程序，执行流进入第二个分支。接着通过WriteProcessMemory对该程序进行动态patch，将程序改为真正的样子，保证其正常执行。然后在第二个分支对输入与某个字符串逐字节异或，并每一位加1。将得到的运算结果通过OutputDebugString函数传回父进程，父进程通过ReadProcessMemory将返回值读入Buffer，最后与程序硬编码的值进行比对，比对成功返回1，否则返回-1。

所以解决方法就是我们手动修复子进程分支，修复完毕后程序就可以反编译了，算法十分简单：

[![](https://p0.ssl.qhimg.com/t01db4ad1e4fa917d20.png)](https://p0.ssl.qhimg.com/t01db4ad1e4fa917d20.png)

然后根据正向算法写出逆向算法即可，我用python模仿了一下正向过程，并且给出了逆向的代码：

```
# -*- coding:utf-8 -*-


# reverse

a = [0x65 ,0x6C, 0x63, 0x6F, 0x6D, 0x65, 0x20, 0x74, 0x6F, 0x20, 0x43, 0x46, 0x46, 0x20, 0x74, 0x65, 0x73, 0x74, 0x21]

b = [0x25,0x5c,0x5c,0x2b,0x2f,0x5d,0x19,0x36,0x2c,0x64,0x72,0x76,0x80,0x66,0x4e,0x52] # 被比较的

flag = ""

for i in range(16):

    b[i] = b[i] - 1

    flag += chr(b[i]^a[i])

print flag


''' encrypt


a = "AAAAAAAAAAAAAAAA"

a = [ord(i) for i in a]

print a

b = []

c = [0x65 ,0x6C, 0x63, 0x6F, 0x6D, 0x65, 0x20, 0x74, 0x6F, 0x20, 0x43, 0x46, 0x46, 0x20, 0x74, 0x65, 0x73, 0x74, 0x21]

for i in range(len(a)):

    t = a[i]^c[i]

    t = t + 1

    b.append(hex(t))

print b


'''
```

带入看看，发现结果是正确的：

[![](https://p3.ssl.qhimg.com/t0161e81b378b590cf2.png)](https://p3.ssl.qhimg.com/t0161e81b378b590cf2.png)






