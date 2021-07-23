> 原文链接: https://www.anquanke.com//post/id/176532 


# Windows调试艺术——断点和反调试（上）


                                阅读量   
                                **232939**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t012fbfe5dde50a97bc.jpg)](https://p4.ssl.qhimg.com/t012fbfe5dde50a97bc.jpg)



《Windows调试艺术》主要是记录我自己学习的windows知识，并希望尽可能将这些东西在某些实际方面体现出来。恰好最近我在为学校的新生校赛出题，想着来个反调试的”大杂烩”，里面有几个反调试技术恰好是基于前面几篇的内容，这一次我们就将之前学习过的PEB、SEH等等的知识用到反调试的实际应用上。

需要的知识基础：
- [Windows调试艺术——利用LDR寻找dll基址](https://www.anquanke.com/post/id/173586)
- [Windows调试艺术——从0开始的异常处理（上）](https://www.anquanke.com/post/id/175293)
- [Windows调试艺术——从0开始的异常处理（下）](https://www.anquanke.com/post/id/175753)


## 基于中断、异常的反调试

### <a class="reference-link" name="%E5%88%A9%E7%94%A8SEH%E5%92%8C%E8%BD%AF%E4%BB%B6%E6%96%AD%E7%82%B9%E6%9C%BA%E5%88%B6%E5%AE%9E%E7%8E%B0%E5%8F%8D%E8%B0%83%E8%AF%95"></a>利用SEH和软件断点机制实现反调试

首先简单回忆一下SEH的处理，当用户引发了一个异常时，程序会遍历当前线程的SEH链表来检查能否处理该异常，如果能，就将该异常交给异常处理例程进行处理，并在处理完成后重新执行异常代码。SEH链表的头部保存在FS:[0]中，越晚设置的SEH越早处理，我们可以用以下的代码装载自己的SEH

```
push seh                                        //将自己的SEH函数地址压栈
push DWORD ptr fs : [0]            //将之前的SEH头压栈
mov DWORD ptr fs : [0], esp    //esp指向的地方恰好构成了新的EXCEPTION_REGISTRATION_RECORD
```

再来回忆一下断点的知识，我们的od下的软件断点，实际上是将下断点处的指令替换为0xCC（也就是INT 3），当程序跑到这里，发现这是个异常，然后根据IDT（中断描述符表）去寻找相应的中断处理例程，再经过异常分发，从而实现断点的功能。

```
假设在此处下断点
C645 FC 00 mov byte ptr [ebp-4],0
53 PUSH EBX
断点后的指令应为
CC int 3
45 FC 00 被识别为其他指令
53 PUSH EBX
```

但是我们会发现，在使用od下断点时，指令在我们这边并没有看到改变，另外，我们下的断点处并没有执行。如果按照之前的理论的话这条指令由于被覆盖成了0xCC所以”废”了才对，指令不应该停留在此，之后应该直接去执行45 FC 00才对，而这又会引发一个新的问题，这个45 FC 00到底是不是个可以识别的指令，不是的话该怎么办，是的话程序逻辑错了怎么办？

第一个问题很简单，实际上调试器给我们做了”伪装”，实际上指令已经变了，只不过展示给用户的还是C645 FC 00，而第二、三个问题就稍微复杂一些了，为了解决这个问题，我们就需要恶补一点关于软件断点的知识了。

当调试器遇见INT 3时，首先会执行类似初始化的操作，在《英特尔IA-32架构软件开发手册》中我们可以找到相应的代码，为了理解方便，这里我写了效果相同的伪代码

```
if (中断向量号 not in 中断向量表)
    General_Protection_Exception()
if (栈 not have sizeof(cs)+sizeof(eip))
    Stack_Exception()
else 
    IF=0
    TF=0
    AC=0
    push cs
    push eip
    cs =对应异常处理例程的cs
    eip=对应异常处理例程的eip
```

上面的处理实际上在栈里维护了一个结构，它保存着相关寄存器的信息，也被叫做TRAP_FRAME陷阱帧，而之后就该进入中断处理例程了。我们可以用windbg来查看具体的函数，注意要在内核调试状态，命令如下

```
!idt
uf Trap3地址
```

这里有很多操作就不再一一详细论述，但比起其他的中断处理例程，显然它多出了如下的部分

```
mov     ebx, [ebp+68h]      
dec     ebx                  
mov     ecx, 3                
mov     eax, 80000003h      
call    CommonDispatchException
```

这里的ebx实际上就是之前压栈的eip了，dec令其自减1，也就是说之前本来指向45 FC 00的eip又重新指向了INT 3了，之后当我们恢复执行时，调试器再将INT 3位置的hex填充回C6，程序也就恢复”正常”了，这就解决了我们之前的两个问题。

但是问题就又来了，你程序恢复正常，可用户那可没取消这个断点啊！有过调试经验的人都知道，我们下了断点后，执行过去断点还在那，不会取消，可按照上面的逻辑INT 3已经被”修复”了，之后应该没有了才对。 这个问题也很简单，调试器会维护一个记录断点信息的文件（如VC6的文件是.opt），当我们执行过一个断点后，调试器设置一个标志位的硬件断点，当执行完下断点的指令后再次中断，这次中断就会将记录的断点信息全部设置一遍，也就解决了这个问题。

有了上面的知识，我们就可以开始构思一个简单的反调试软件了，既然调试器是用int 3实现软件断点，那我们也完全可以用个假的int 3来骗调试，让它误以为此处应该进行中断处理（如果在非调试器下，则会因为INT 3指令进入异常处理），然后陷入我们提前布置好的陷阱，由于各个调试器的具体处理略有差异，所以具体调试情况可能略有出入，以下均使用VS调试器进行

```
bool anti_debug() `{`
    BOOL flag = FALSE;
    __asm `{`
        push my_seh
        push DWORD ptr fs : [0]
        mov DWORD ptr fs : [0], esp
        __emit(0xcc)
        mov flag, 1
        jmp remove_seh
my_seh :
        mov eax, dword ptr ss : [esp + 0xc];
        mov dword ptr ds : [eax + 0xb8], remove_seh
        xor eax, eax
        retn
remove_seh:
        pop dword ptr fs : [0]
        add esp, 4
    `}`
    return flag;
`}`
```

上面代码中，__emit()函数相当于将里面的hex转换为指令，0xCC自然就是INT 3了，首先我们将自己的SEH处理函数my_seh装载了，然后设置了假的断点。如果是在调试器内，INT3就被很平常的执行了，然后直接下一句将flag置为1，最终用remove_seh卸载了我们的seh，如图所示，在vs调试器中我们成功将flag置为了1。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws4.sinaimg.cn/large/006tNc79ly1g1zzov6i99j30bg02mwem.jpg)

而在非调试器环境下由于INT 3会进入我们的my_seh中，先是拿到了EXCEPTION_REGISTRATION_RECORD的地址，将我们卸载自己seh的remove_seh装载进去，现在的SEH链表的第一个处理函数就是我们的remove_seh了，再次触发断点异常时我们自己的SEH函数就被卸载了，程序也就正常执行下去了。注意，这里的esp+0xc是实际计算出来的，如果你改了代码此处也需要修改，不改或者改错的话就会导致SEH始终是之前的SEH，也就是会无限循环处理该异常。

同样我们也可以将这个思路放到函数隐藏上，我们可以将自己的函数伪装成SEH的处理函数，然后我们在执行过程中故意设置一个异常，迫使程序进入SEH处理函数，如下图代码所示

```
bool seh()
`{`
    bool bDebugging = false;
    __asm
    `{`
            push getFlag
            push DWORD ptr fs : [0]
            mov DWORD ptr fs : [0], esp
            __emit(0xcc)

    `}`
    return bDebugging;
`}`

int main()
`{`
    scanf_s("%s", &amp;a, 25);
    seh();
    printf("bye~~~~~");

    return 0;
`}`
```

其中getFlag也就是我们的关键函数，我们生成可执行文件并用ida打开

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws2.sinaimg.cn/large/006tNc79ly1g20uj5kv59j307903e0sx.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws2.sinaimg.cn/large/006tNc79ly1g20ujp2sg1j306h020749.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws3.sinaimg.cn/large/006tNc79ly1g20ujvhn4jj304s024t8o.jpg)

可以看到我们的函数被隐藏了起来，不太容易被发现了，而如果用od调试的话，会因为od会“无视”INT 3，反而导致调试者进不去关键函数了，成功提高了程序被逆向的难度。不过这里还是要注意处理无限循环的问题，因为我们的函数如果没有修复断点异常的话就会导致程序再次执行断点进行无限循环，导致程序崩溃。

当然，我们还可以更变态一点，使用多层SEH，每一层的SEH都对应一部分的解密函数，这样调试者就很难理清里面的关系了

```
void seh3()
`{`
    printf("this is seh3");
    Sleep(1000000);
`}`
void seh2()
`{`
    printf("this is seh2");
    __asm
    `{`
        push seh3
        push DWORD ptr fs : [0]
        mov DWORD ptr fs : [0],esp
        __emit(0xcc)

    `}`
`}`
void seh1 ()
`{`
    printf("this is seh1");
    __asm
    `{`
        push seh2
        push DWORD ptr fs : [0]
        mov DWORD ptr fs : [0], esp
        __emit(0xcc)
    `}`
`}`

int main()
`{`
    printf("welcome to skctf");
    __asm
    `{`
        push seh1
        push DWORD ptr fs : [0]
        mov DWORD ptr fs : [0], esp
        __emit(0xcc)
        pop dword ptr fs : [0]
        add esp, 4
    `}`
    printf("bye");

`}`
```

至于会输出什么大家可以猜猜，要注意这里的多重SEH的卸载是很难操作的，所以我最后是让程序sleep，防止无限循环。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8UnhandledExceptionFilter%E4%B8%8E%E8%BD%AF%E4%BB%B6%E6%96%AD%E7%82%B9%E6%9C%BA%E5%88%B6%E5%AE%9E%E7%8E%B0%E5%8F%8D%E8%B0%83%E8%AF%95"></a>利用UnhandledExceptionFilter与软件断点机制实现反调试

UnhandledExceptionFilter我们在之前的文章中也详细说了，实际上它就是SEH的”不得已”处理例程，只有当seh链上的处理函数都无法处理异常时才会触发，我们可以把它看作是SEH的一种特殊情况，我们可以通过以下代码设定我们自定义的UnhandledExceptionFilter，至于详细的执行过程可以参考之前的文章

```
UnhandledExceptionFilter（function_name）
```

思路和上面的一样，同样是利用调试器对于断点的处理机制进行构造，代码如下：

```
LONG WINAPI Exception(
    _In_ struct _EXCEPTION_POINTERS *ExceptionInfo
    ) `{`
    ExceptionInfo-&gt;ContextRecord-&gt;Eip += 5;
    return EXCEPTION_CONTINUE_EXECUTION;
`}`
bool CheckDebug() `{`
    bool flag = false;
    __asm `{`
        __emit(0xCC);
        mov flag, 1
    `}`
    return flag;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws1.sinaimg.cn/large/006tNc79ly1g203jnb773j30a003ljrj.jpg)

当程序被调试时，如图所示，0xcc相当于被忽视，flag被设置为1。而在正常运行时，由于断点触发SEH处理，我们并没有可以解决该异常的处理函数，所以调用了Exception函数。

Exception函数设置了EXCEPTION_POINTERS结构，这个结构我们也详细说过了，这里主要是调整EIP的值实现跳过INT 3，要不然的话又会触发无限循环的断点异常。

### <a class="reference-link" name="0xCC%E6%A3%80%E6%B5%8B"></a>0xCC检测

我们说了软件断点会让原本位置的指令替换成0xcc进而实现中断，那如果我们正在调试一个windows GUI程序的话，我们是不是会经常在比如MessageBox、GetDlgltemText等API处下断点？那我们只需要利用指针指向这些函数指令的起始地址，检测是否为0xcc即可实现反调试，代码如下：

```
bool CheckDebug()) 
`{`
    bool flag = false;
    PBYTE pCC = (PBYTE)MessageBoxW;
    if (*pCC == 0xCC)
    `{`
        flag = 1;
    `}`
    return flag;
`}`
```

那我们又可以从这个基础上出发，如果说我们划定一块代码区域，那这一片区域的0xcc的数量是不是应该是个固定的值？如果调试者下了断点，那就会导致这个数量变化。

```
bool CheckDebug_Checksum()
`{`
    bool flag = FALSE;
    __asm `{`
        call CHECKBEGIN
begin:
        pop esi
        mov ecx, 0x15           
        xor eax, eax           
        xor ebx, ebx
check:
        movzx ebx, byte ptr ds : [esi]
        add eax, ebx
        rol eax, 1
        inc esi
        loop check
        cmp eax, 0x1859a602
        je _NOT_DEBUGGING
        mov flag, 1
_NOT_DEBUGGING:
    `}`
    return flag;
`}`
```

CHECKBEGIN的开始我们pop了esi，实际上就是拿到了当前的代码的地址，ecx作为循环的计数器，接着清空了eax和ebx为之后做准备

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws3.sinaimg.cn/large/006tNc79ly1g20u4wrb2qj307t020mx4.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws3.sinaimg.cn/large/006tNc79ly1g20u5283d9j303z00wglf.jpg)

check部分就是靠着esi拿到了每一条指令的十六进制码，最终经过处理后和我们设定的值比较，如果不是的话就说明程序的汇编代码被修改过了，存在调试器。

### <a class="reference-link" name="GetLastError"></a>GetLastError

这个函数我们在之前的格蠹汇编练习题中提到过，我们也解释了相关的WER机制，简单的说，这个函数就是将最后一个错误汇报给我们，那我们可以先设置一个error，然后执行一个仅在调试器中有意义的函数，如果error变了，说明函数错了，我们没在调试器中，如果没变，说明函数正常执行了，那就是在调试器中了。

```
bool CheckDebug()
`{`
    DWORD error = 11111;
     bool flag = false;
  SetLastError(error);
    OutputDebugString("  ");
    if (GetLastError() == error)
    `{`
        flag = 1;
    `}`
    return flag
`}`
```

OutputDebugString函数是在调试器中输出一段话的意思，如果在非调试状态下自然就失效了，失效了就会导致last error发生变化，也就和我们最开始设定的error不同啦。

### <a class="reference-link" name="INT%202D"></a>INT 2D

我们说过一般调试器使用INT 3来实现断点机制，但INT 2D同样能够实现断点功能，只不过它一般用作内核调试时的断点指令，但是其实在用户态它一样可以发挥作用，不过要注意的是有些调试器对齐处理有所差别，不过无伤大雅，我们将之前的INT 3改为INT 2D，可以看到效果相同。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws2.sinaimg.cn/large/006tNc79ly1g227xazbk9j30e0089q3x.jpg)



## 硬件断点的反调试

上面我们详细说明了软件断点的机制并且了解了基于软件断点的反调试技术，下面让我们看看硬件断点的相关知识。

大家对ESP定律脱壳应该都不陌生，在PUSHAD后我们会下一个叫做”数据访问断点”的特殊断点，当程序访问这段数据时，就会断下来等待我们的调试。现在如果是我们来设计这个功能，我们能够用0xcc来实现吗？显然不能，0xcc作为指令有它的”先天缺陷” —— 它必须要执行（被当作代码）才能触发。那我们来构思一种断点机制，它可以保存地址，只要是对这个地址进行了操作，不管是读写还是执行，我们就断下来，这不就可以实现在数据处下断点的功能了吗？

这其实就是硬件断点的精髓，Windows采用了DR0～DR7的8个调试器来实现硬件断点，它们各自承担着不同的职能：
- DR0～DR3，调试地址寄存器，顾名思义是用来存放地址的，即然有4个说明我们的硬件断点理论上最多有四个
- DR6（DR4等价于RR6），调试状态寄存器，它向调试器的断点异常处理程序提供断点的详细信息
- DR7（DR5等价于DR7），调试控制寄存器，它对应许多标志位，实现了区分不同的硬件断点
当我们下一个硬件断点时，断点又可以分为以下的三类：
- 代码访问断点，也就是我们的调试地址寄存器指向的是代码段的一句指令，运行到此处时就会触发断点。听起来和软件断点似乎没有什么不同，但要注意，我们并没有用0xcc去覆盖指令，这就意味着我们不需要复杂的操作来善后，更关键的是，当我们下软件断点时，因为要覆盖，所以要覆盖的指令必须先存在，如果碰到SMC类的程序（如果不知道的朋友可以当作是代码边执行边生成，并不是一次性出现了全部代码）就会碰到下不上断点的尴尬处境，而硬件断点因为是地址，哪怕某个时刻该地址的指令还没被加载，也一样可以下断点。另外，大家最熟悉的单步调试实际上也是用了这个原理。
- 数据访问断点，我们的调试地址寄存器指向的是一段数据，一旦数据被修改被访问我们就可以立刻断下来，是用来监测全局变量、局部变量的好帮手
- I/O访问断点，对于此类断点在用户态调试时用的并不多，但是对于经常和io打交道的驱动程序来说就很常用了。
通过上面的说明，我们应该很容易想到预防硬件断点的反调试手段，即然你用的是寄存器表示，我只需要看看你寄存器的值是不是空就可以判断你是不是下过硬件断点了

```
BOOL CheckDebug()
`{`
      bool flag;

        CONTEXT context;  
    HANDLE hThread = GetCurrentThread();  
    context.ContextFlags = CONTEXT_DEBUG_REGISTERS;  
    GetThreadContext(hThread, &amp;context); 

    if (context.Dr0 != 0 || context.Dr1 != 0 || context.Dr2 != 0 || context.Dr3!=0)   
    `{`  
        flag = 1;

    `}`  
    return flag;  
`}`
```



## 基于PEB等的反调试

### <a class="reference-link" name="BeingDebugged"></a>BeingDebugged

PEB即Thread Environment Block，线程环境块，我们之前说过了几个它的重要成员，我们提到过偏移为0×002的BeingDebugged是标示进程是否处于被调试状态的一个标志位，那我们自然可以用它来探测了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws4.sinaimg.cn/large/006tKfTcly1g14rov93xfj30sy0iatd3.jpg)

代码如下：

```
bool CheckDebug() `{`
    bool bDebugged = false;
    __asm `{`
        MOV EAX, DWORD PTR FS : [0x30]
            MOV AL, BYTE PTR DS : [EAX + 2]
            MOV bDebugged, AL
    `}`
    return bDebugged;
`}`
```

FS:[30]也就是PEB的地址，+2也就是拿到了BeingDebugged的值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws3.sinaimg.cn/large/006tNc79ly1g204fyz7fqj30al03pt93.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws1.sinaimg.cn/large/006tNc79ly1g204fyf6uej30al03pt93.jpg)

可以看到在调试状态下确实返回了1

实际上微软为我们封装了一个专门的API — IsDebuggerPresent()，我们在使用时可以直接用它，有兴趣的朋友可以看看它的反汇编代码，会发现和我们写的几乎一模一样。

### <a class="reference-link" name="NtGlobalFlag"></a>NtGlobalFlag

当我们处于调试状态时，实际上会创建一个调试堆（这部分内容大概可能也许会在不久之后的《Windows调试艺术》中详细解释），我们可以通过检查堆的情况来判断程序是否被调试，NtGlobalFlag就是这样一个标志位，它实际上表示了堆的状态，如果它的0x70，也就是说明有调试器了，代码如下

```
bool CheckDebug() `{`
    int nNtFlag = 0;
    __asm `{`
        MOV EAX, DWORD PTR FS : [0x30]
        MOV EAX, DWORD PTR DS : [EAX + 0x68]
        MOV nNtFlag, EAX
    `}`
  if(nNtFlag==0x70)
        nNtFlag=1
   return nNtFlag
`}`
```

### <a class="reference-link" name="ProcessHeap"></a>ProcessHeap

当然，即然堆发生了改变，那我们也可以直接用ProcessHeap的属性来查看是否处于调试状态。主要运用的是ForceFlags和Flags两个标志位，但由于在不同版本的windows上偏移不同，这里就不再给出具体代码了。

### <a class="reference-link" name="ParentProcess"></a>ParentProcess

我们随手编写一个测试程序test，分别在vs调试器、正常状态下打开，运用以下命令来查看父进程的ID

```
wmic process where Name="test.exe" get ParentProcessId
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws3.sinaimg.cn/large/006tNc79ly1g20vtzokj9j30gr045weu.jpg)

可以看到父进程是明显不同的，这是因为对于调试器来说，程序被调试也就是说要在它的掌控之下，所以程序必然是它的子进程，而正常状态下，程序的父进程一般都是explorer.exe，我们只需要利用这一点监测当前程序的父进程也就可以实现反调试了

微软提供给了我们如下的函数，虽然还是未公开的，但已经被人研究透了

```
NTSTATUS WINAPI NtQueryInformationProcess(
  __in       HANDLE ProcessHandle,
  __in       PROCESSINFOCLASS ProcessInformationClass,
  __out      PVOID ProcessInformation,
  __in       ULONG ProcessInformationLength,
  __out_opt  PULONG ReturnLength
);
```

它的第二个参数说对应的结构体如下，其中Reserved3也就是父进程的ID

```
typedef struct _PROCESS_BASIC_INFORMATION `{`

    PVOID Reserved1;
    PPEB PebBaseAddress;
    PVOID Reserved2[2];
    ULONG_PTR UniqueProcessId;
    PVOID Reserved3;
`}` PROCESS_BASIC_INFORMATION;
```

因为本身出题我用到了这项技术，为了避免泄题，就只给简单的函数调用的伪代码了

```
flag = false
pid = GetCurrentProcessID 
hp = OpenProcess
NtQueryInformationProcess()
pp = OpenProcess()
if(Reserved3 != xxxx)
  flag = 1
return flag
```



## 总结

上面就是根据我们前面几篇的《Windows调试艺术》学到的知识能够实现的反调试手段了，其实反调试的手段还有很多很多，以后随着文章的更新，还会为继续总结这部分的知识。

代码参考 ： [https://github.com/alphaSeclab/anti-debug](https://github.com/alphaSeclab/anti-debug)
