> 原文链接: https://www.anquanke.com//post/id/211497 


# 逆向分析微软IFEO镜像劫持从ring3到ring0的实现机理


                                阅读量   
                                **145045**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01f85cacd3d6547ad0.jpg)](https://p3.ssl.qhimg.com/t01f85cacd3d6547ad0.jpg)



```
IFEO（Image File Execution Options ）是设置在Windows注册表中，创建IFEO注册表项的目的是让开发人员可以选择调试他们的软件，是为了开发人员可以使用注册表项将任何程序附加到任何可执行文件，但是很多被利用了去实现进程注入。很多只知道ring3的部分机制，但是并不知道完整的机制，今天们就来分析下它的ring3到ring0的整个过程的机理。
```

开发一个小的**test.exe**解析命令行，为了方便上调试器调试加上**Messagebox** 弹框

[![](https://p2.ssl.qhimg.com/t019f8ad8852b187b31.png)](https://p2.ssl.qhimg.com/t019f8ad8852b187b31.png)

编译后，我们可以修改注册表演示下**IFFO**<br>`**HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\`{`name of the executable`}`**`<br>
加个**notepad.exe**的项目然后添加**Debugger**的**keyvalue**<br>**`“Debugger”=”`{`full path to the debugger`}`”`**

[![](https://p2.ssl.qhimg.com/t0122eda6de879a8e98.png)](https://p2.ssl.qhimg.com/t0122eda6de879a8e98.png)

[![](https://p0.ssl.qhimg.com/t01743d331d9e34d8fc.png)](https://p0.ssl.qhimg.com/t01743d331d9e34d8fc.png)

然后我们在**windows**左下角搜索框输入**notepad**

[![](https://p1.ssl.qhimg.com/t01113bc1ae3dd8d9fc.png)](https://p1.ssl.qhimg.com/t01113bc1ae3dd8d9fc.png)

然后启动**notepad.exe**,这时我们的**test.exe**就会被启动了。

[![](https://p1.ssl.qhimg.com/t01b5c448d0853ed229.png)](https://p1.ssl.qhimg.com/t01b5c448d0853ed229.png)

**今天的目的就是来分析下这种机制的原理。**

把上述代码继续改造的**MessageBox**去掉，加直接启动**notepad.exe**的启动参数里的进程

[![](https://p2.ssl.qhimg.com/t01d7cd9d0f259a382a.png)](https://p2.ssl.qhimg.com/t01d7cd9d0f259a382a.png)

[![](https://p1.ssl.qhimg.com/t010dd568da45f43fb6.png)](https://p1.ssl.qhimg.com/t010dd568da45f43fb6.png)

然后上**ollydbg**调试运行。

[![](https://p1.ssl.qhimg.com/t01deb38c8da5165894.png)](https://p1.ssl.qhimg.com/t01deb38c8da5165894.png)

启动后对**CreatPorcessW**下断点输入命令: **bp CreatPorcessW**

断点停下来

[![](https://p4.ssl.qhimg.com/t01984608f1d84f40f2.png)](https://p4.ssl.qhimg.com/t01984608f1d84f40f2.png)

继续F8 然后F7进入

`**775F1054  |.  E8 22010100   CALL kernel32.CreateProcessInternalW**`

通过`IDA`查看**CreateProcessInternalW**前面基本都是一些字符串拷贝的动作

[![](https://p2.ssl.qhimg.com/t017d6da4575cdec314.png)](https://p2.ssl.qhimg.com/t017d6da4575cdec314.png)

[![](https://p3.ssl.qhimg.com/t012d1d7493bf5635f3.png)](https://p3.ssl.qhimg.com/t012d1d7493bf5635f3.png)

在**Ollydbg**开始阶段就直接**F8**单步运行过去

接着就是创建环境

[![](https://p5.ssl.qhimg.com/t013ab92486d2e7908d.png)](https://p5.ssl.qhimg.com/t013ab92486d2e7908d.png)

这些也直接单步走过，当我们单步到这里的时候

[![](https://p2.ssl.qhimg.com/t01ae557fe884f5fbff.png)](https://p2.ssl.qhimg.com/t01ae557fe884f5fbff.png)

调试器在这里下断点

[![](https://p5.ssl.qhimg.com/t019b97686ab4e08ca9.png)](https://p5.ssl.qhimg.com/t019b97686ab4e08ca9.png)

然后**F8**

[![](https://p5.ssl.qhimg.com/t01326c6d11042c21d5.png)](https://p5.ssl.qhimg.com/t01326c6d11042c21d5.png)

发现`NtCreateUserProcess(&amp;Process, &amp;ThreadHandle, 0x2000000, 0x2000000, v188, v189, v64, 1, v60, &amp;v194, &amp;v347)`;<br>
函数的**eax**的返回值是**0xC0000039**，也就是说这里调用内核去创建的时候是直接失败的，<br>
返回值是`STATUS_OBJECT_PATH_INVALID` 意识就是说路径对象无效，通过分析第九个参数结构体的数据发现路径确实没有任何问题

[![](https://p5.ssl.qhimg.com/t0116c95dceba05c412.png)](https://p5.ssl.qhimg.com/t0116c95dceba05c412.png)

我们可以做个对比实验，把**IFEO**的对应注册表**Debugger**删除后再运行调试

下面是正常情况下把注册表删除了后的运行

[![](https://p0.ssl.qhimg.com/t01f65a2c928ae82791.png)](https://p0.ssl.qhimg.com/t01f65a2c928ae82791.png)

参数基本一模一样，然后直接**F8** 单步运行，结果出现了返回值`eax == 0`

[![](https://p0.ssl.qhimg.com/t01fb2a1fed28ab13b1.png)](https://p0.ssl.qhimg.com/t01fb2a1fed28ab13b1.png)

也就是**STATUS_SUCCES**,没有**debugger**注册表键值的时候**NtCreateUserProcess**内核返回值是`0`，现在我们大致可以猜测内核里也对这个IFEO位置的注册表键值做了处理，为了搞清楚内核如何处理，直接上**windbg**用虚拟机进行双机调试，调试内核。

[![](https://p1.ssl.qhimg.com/t0152178e7369fa292d.png)](https://p1.ssl.qhimg.com/t0152178e7369fa292d.png)

[![](https://p4.ssl.qhimg.com/t0157e208121a8a3c91.png)](https://p4.ssl.qhimg.com/t0157e208121a8a3c91.png)

接下来在**NtCreateUserProcess**上下断点，当Ollydbg里执行`NtCreadtUserProcess`时**windbg**里断点停下来

[![](https://p5.ssl.qhimg.com/t013f9bf02ec7c67f04.png)](https://p5.ssl.qhimg.com/t013f9bf02ec7c67f04.png)

有个最简单的方法就是不断的尝试单步进入函数后单步**Call**返回值为**0xC0000039**的函数，最后经过反复的实现发现**NtCreateUserProcess**内在调用`**PspAllocateProcess**`函数时返回**0xC0000039**

[![](https://p1.ssl.qhimg.com/t0120c9f5bdba981366.png)](https://p1.ssl.qhimg.com/t0120c9f5bdba981366.png)

在**fffff800`0412651f** 出下断点

[![](https://p3.ssl.qhimg.com/t01c2d92ae440a82eea.png)](https://p3.ssl.qhimg.com/t01c2d92ae440a82eea.png)

运行后断下

[![](https://p2.ssl.qhimg.com/t01d3e592c239f9c27b.png)](https://p2.ssl.qhimg.com/t01d3e592c239f9c27b.png)

调试器停在了<br>`call    nt!PspAllocateProcess (fffff8000412852c)`，**F10** 后查看**eax**值`r eax`，显示

[![](https://p3.ssl.qhimg.com/t010fb1a96d9f72ad2b.png)](https://p3.ssl.qhimg.com/t010fb1a96d9f72ad2b.png)

也就是说在这个函数里可能会涉及处理注册表的过程，用**ida**打开**ntkrnlmap.exe**的内核文件，慢慢查看会发现有这么一段代码

[![](https://p4.ssl.qhimg.com/t01ea34557179741261.png)](https://p4.ssl.qhimg.com/t01ea34557179741261.png)

**在这段代码里判断IFEOKEY 是否有对应Debugger注册表设置，往上面翻会发现IFEOKey打开的就是当前进程名的IFEOKey的注册表**

[![](https://p0.ssl.qhimg.com/t010fc3e858af748624.png)](https://p0.ssl.qhimg.com/t010fc3e858af748624.png)

`RtlpOpenImageFileOptionsKey`调用了`RtlpOpenBaseImageFileOptionsKey`，`RtlpOpenBaseImageFileOptionsKey`会`ZwOpenKey IFEO`注册表

[![](https://p4.ssl.qhimg.com/t01e48f3d83bbef5936.png)](https://p4.ssl.qhimg.com/t01e48f3d83bbef5936.png)

[![](https://p0.ssl.qhimg.com/t01ec426cd5f3f83c54.png)](https://p0.ssl.qhimg.com/t01ec426cd5f3f83c54.png)

为了验证我们的结果，在`RtlQueryImageFileKeyOption`函数下断点

[![](https://p5.ssl.qhimg.com/t010df46767373d23a2.png)](https://p5.ssl.qhimg.com/t010df46767373d23a2.png)

进入 `RtlQueryImageFileKeyOption`函数单步执行到`ZwQueryValueKey`时，F10后

查看**rsi**里的值

[![](https://p3.ssl.qhimg.com/t01f3bc01fe44986b34.png)](https://p3.ssl.qhimg.com/t01f3bc01fe44986b34.png)

会发现此时读取到**Debugger**的设置注册表，然后返回到调用之前的下面一句指令：

[![](https://p0.ssl.qhimg.com/t011e0a2c6f789ba65a.png)](https://p0.ssl.qhimg.com/t011e0a2c6f789ba65a.png)

判断**eax**是否是**0**,此时函数返回值就是**0**，然后就进入了

[![](https://p1.ssl.qhimg.com/t01753c87af7adf2285.png)](https://p1.ssl.qhimg.com/t01753c87af7adf2285.png)

`mov r12d,0xC00000039h`<br>
最后把 **r12d** 赋值给了**eax**返回

[![](https://p2.ssl.qhimg.com/t018f22020e3e977ac9.png)](https://p2.ssl.qhimg.com/t018f22020e3e977ac9.png)

就是最后我看到创建进程失败了，错误号**0xC00000039**

[![](https://p2.ssl.qhimg.com/t01a8adcbb5bf1f8497.png)](https://p2.ssl.qhimg.com/t01a8adcbb5bf1f8497.png)

当前者失败后，**ring3** 层就进入了

[![](https://p2.ssl.qhimg.com/t014c13adb3339cef30.png)](https://p2.ssl.qhimg.com/t014c13adb3339cef30.png)

`76B4F75F   .  FF15 5006B176 CALL DWORD PTR DS:[&lt;&amp;ntdll.LdrQueryImageFileKeyOption&gt;]   ;  ntdll.LdrQueryImageFileKeyOption`<br>
函数去读取**IFEO**的**Debugger**注册表

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0175ba6e8b3e3479ab.png)

获取了数据后，解析参数成功后就把当前进程的路径加载**Debugger**对应的进程后面作为一个参数组合成一个启动进程参数

[![](https://p3.ssl.qhimg.com/t01f15fee5563fa05d5.png)](https://p3.ssl.qhimg.com/t01f15fee5563fa05d5.png)

在上图可以看到两个路径被加到一起。构造的的新参数就是<br>`UNICODE "C:\Users\Administrator\Desktop\test.exe C:\Windows\System32\notepad.exe"`<br>
最后`goto LABEL_87`重新组建进程参数环境去执行新的进程，又会进入`NtCreateUserProcess`，但这时启动的是**test.exe**

[![](https://p5.ssl.qhimg.com/t01aca9bf3a7bb53f42.png)](https://p5.ssl.qhimg.com/t01aca9bf3a7bb53f42.png)

这时返回值就是**0**了，创建成功

[![](https://p1.ssl.qhimg.com/t01bcbf65f66f131a83.png)](https://p1.ssl.qhimg.com/t01bcbf65f66f131a83.png)

```
至此整个过程就分析完毕了，微软的IFEO机制本来是给开发人员调试程序用的，后来慢慢被恶意软件用来镜像劫持，在微软的官方msdn里有一段描述说使用DEBUG_ONLY_THIS_PROCESS和DEBUG_PROCESS方式 CreateProcess时是不会读取注册表去劫持的，而实际测试时确实如此，具体原理读者可以自行分析。

特别申明：逆向分析调试是一种武器，切莫用于非法途径。
```
