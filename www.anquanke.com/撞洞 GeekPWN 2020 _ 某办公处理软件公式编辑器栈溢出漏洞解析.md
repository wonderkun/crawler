> 原文链接: https://www.anquanke.com//post/id/225441 


# 撞洞 GeekPWN 2020 | 某办公处理软件公式编辑器栈溢出漏洞解析


                                阅读量   
                                **147699**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01585df1124aace462.jpg)](https://p0.ssl.qhimg.com/t01585df1124aace462.jpg)



## 01 漏洞说明

在挖掘公式编辑器漏洞的过程中，找到了一些空指针解引用、内存越界访问、栈溢出等类型的漏洞。经过分析确认，找到的栈溢出漏洞同GeekPwn 2020参赛人员所提交的栈溢出代码执行漏洞为同一个。

今天主要针对该栈溢出漏洞进行分析、说明。

**影响版本：某办公处理软件 2019版 11.1.0.10132<br>**<br>**漏洞类型：栈溢出<br>**



## 02 详情

### <a class="reference-link" name="crash%20dump%E5%88%86%E6%9E%90"></a>crash dump分析

利用windbg分析产生的crash dump文件，打开后通过命令`!analyze -v`显示如下：

```
FOLLOWUP_IP: 
   EqnEdit+362bc
   004362bc 8945f0          mov     dword ptr [ebp-10h],eax

   NTGLOBALFLAG:  22800000

   APPLICATION_VERIFIER_FLAGS:  0

   APP:  eqnedit.exe

   ANALYSIS_VERSION: 6.3.9600.17237 (debuggers(dbg).140716-0327) x86fre

   LAST_CONTROL_TRANSFER:  from 00431085 to 004362bc

   FAULTING_THREAD:  00000760

   PRIMARY_PROBLEM_CLASS:  INVALID_POINTER_WRITE

   BUGCHECK_STR:  APPLICATION_FAULT_INVALID_POINTER_WRITE
```

触发崩溃地址的指令是`mov     dword ptr [ebp-10h],eax`，查看对应地址的伪代码如下所示：

[![](https://p3.ssl.qhimg.com/t01357b940598de8f55.png)](https://p3.ssl.qhimg.com/t01357b940598de8f55.png)

很明显，经过虚函数调用后，result的指针地址被改变，导致在写入的时候触发异常。在汇编层面，result等同于ebp指针，因此在经过上层函数调用后，ebp指针被修改。这里很可能是存在栈溢出，因为在一个函数最终返回时，基本上都会调用类似以下序列的汇编指令：

```
mov esp,ebp
pop ebp
retn
```

因此如果产生了栈溢出但是没有覆盖返回地址仅仅覆盖了部分ebp指针指向的内容时，就可能会产生如上的异常效果。

那么接下来就是分析通过`v9[8]`到底调用了哪个函数。

### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E5%88%86%E6%9E%90"></a>调试分析

找到对应触发崩溃的文件，利用windbg调试EqnEdit.exe程序，在`004362B6`下断点，输出eax的值，结果如下：

[![](https://p4.ssl.qhimg.com/t013686b2a015584fb0.png)](https://p4.ssl.qhimg.com/t013686b2a015584fb0.png)

查看对应的函数如下：

[![](https://p5.ssl.qhimg.com/t01838c85d2a97b7ca3.png)](https://p5.ssl.qhimg.com/t01838c85d2a97b7ca3.png)

经过分析后，ida反编译内容如下：

[![](https://p2.ssl.qhimg.com/t017b45c6153721e0af.png)](https://p2.ssl.qhimg.com/t017b45c6153721e0af.png)

而关键的进行越界写的操作就在函数sub_43ECFA中，ida伪代码如下：

[![](https://p1.ssl.qhimg.com/t019878db263870f3ff.png)](https://p1.ssl.qhimg.com/t019878db263870f3ff.png)

可以看出整个函数逻辑如下，在函数sub_43EBDF中，读取MTEF数据的单个字节作为index，在sub_43ECFA中，通过计算后，将index转换为循环次数，不断地从缓冲区中读取数据，并写入到栈上。如果index值过大将导致缓冲区溢出，覆盖返回地址，最终可能导致任意代码执行。

那么关键函数sub_43EBDF又是如何被调用的，查看崩溃时的调用栈如下：

```
0018f330 004362bc eqnedit+0x362bc
0018f34c 00431085 eqnedit+0x31085
0018f374 004362b9 eqnedit+0x362b9
0018f3a0 0043727a eqnedit+0x3727a
0018f3d8 004362b9 eqnedit+0x362b9
0018f404 00431085 eqnedit+0x31085
0018f42c 004362b9 eqnedit+0x362b9
0018f458 0043727a eqnedit+0x3727a
0018f490 004362b9 eqnedit+0x362b9
0018f4bc 00431085 eqnedit+0x31085
0018f4e4 004362b9 eqnedit+0x362b9
0018f510 00433c91 eqnedit+0x33c91
0018f534 00433700 eqnedit+0x33700
0018f58c 0042c7a1 eqnedit+0x2c7a1
0018f5b0 00407a6b eqnedit+0x7a6b
```

在函数sub_43622d中，对读取的数据进行判断后进行调用对应的处理函数，如下：

[![](https://p2.ssl.qhimg.com/t01f46cd0781c3524ed.png)](https://p2.ssl.qhimg.com/t01f46cd0781c3524ed.png)

而在`case 4`情况下才会调用sub_43EBDF，此时读取的tag值为5，查看MathType 6.9 SDK，如下：

[![](https://p3.ssl.qhimg.com/t01b7106b34a7cc54ab.png)](https://p3.ssl.qhimg.com/t01b7106b34a7cc54ab.png)

看来是在解析MATRIX record的过程中产生栈溢出漏洞。

经过分析后，发现该漏洞完全可以利用，由于公式编辑器没有开启重定位，也就不需要绕过ASLR，通过一定的ROP技术绕过DEP即可，而且程序里导入了`WinExec`函数，利用起来会更加便利，效果见视频。



## 03 漏洞修复

目前，在最新版的WPS 2021版中，已将该漏洞修复，限定了循环拷贝的次数小于等于8，伪代码如下：

[![](https://p5.ssl.qhimg.com/t01f1df49137e7bd7e0.png)](https://p5.ssl.qhimg.com/t01f1df49137e7bd7e0.png)



## 04 视频演示

[https://www.bilibili.com/video/BV1Fy4y1B7EM](https://www.bilibili.com/video/BV1Fy4y1B7EM)
