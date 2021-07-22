> 原文链接: https://www.anquanke.com//post/id/175753 


# Windows调试艺术——从0开始的异常处理（下）


                                阅读量   
                                **303556**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0163fe78263af4ce59.jpg)](https://p5.ssl.qhimg.com/t0163fe78263af4ce59.jpg)



windows调试艺术主要是记录我自己学习的windows知识，并希望尽可能将这些东西在某些实际方面体现出来。

要阅读本文章的小伙伴建议先看看《windows调试艺术》的前两篇文章来了解一下前置知识

[Windows调试艺术——从0开始的异常处理（上）](https://www.anquanke.com/post/id/175293)

[Windows调试艺术——利用LDR寻找dll基址](https://www.anquanke.com/post/id/173586)

上一篇我们详细的了解了windows对于硬件和软件异常的不同处理过程以及相似的分发机制，但windows的异常管理远没有那么简单，还包括了SEH、VEH、安全措施等的重要知识，这次就来进行一下补充。要特别说明一下，作为windows最核心的部分之一，异常的大部分内容微软并没有公布，在加之笔者水平有限，所以在一些地方的了解还有很多欠缺，希望有能力的朋友能提出和我共同将windows异常这部分的内容总结完善。



## SEH

SEH（structure exception handle）即结构化异常处理，往大了说它是整个Windows异常处理体系的一种称呼，往小了说它是维护异常体系的一个具体结构。在之前的文中提到了FS寄存器的0偏移直接指向了TEB，TEB的第一个结构是TIB，而TIB的0也就是ExceptionList，也就是异常处理链表的头节点，其结构如下。

```
typedef struct _EXCEPTION_REGISTRATION_RECORD
`{`
  struct _EXCEPTION_REGISTRATION_RECORD *Next;
  PEXCEPTION_ROUTINE Handler;
`}`EXCEPTION_REGISTRATION_RECORD
```

Next指向了下一个SEH节点，而Handler实际上就是我们具体的来处理该异常的函数了，我们也把它叫做异常处理回调函数。如果大家还记得数据结构的知识的话很显然这就是个简单的链表，而该链表只允许在头节点来进行删除和增添操作，且FS的0一直指向头节点，这就说明，越新的函数越接近头节点，系统会维护链表最后的next指向0xFFFFFFFF，回调函数的模版如下：

```
__cdecl _except_handler( struct _EXCEPTION_RECORD *ExceptionRecord,
                        void * EstablisherFrame,
                        struct _CONTEXT *ContextRecord,
                        void * DispatcherContext);
```

### <a class="reference-link" name="SEH%E5%AE%89%E8%A3%85"></a>SEH安装

通过之前的讲解我们可以知道SEH是基于线程的一种处理机制，而它又依赖于栈进行存储和查找，所以也被称作是基于栈帧的异常处理机制。在windows操作系统下的基础栈布局如下所示

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws2.sinaimg.cn/large/006tKfTcly1g1iohrp7o5j30j80o00tk.jpg)

通过这样的布局我们也可以推断出来，SEH的装载甚至还在函数的序言之前，具体的装载代码如下：

```
push offset SEHandler
push fs:[0]
mov fs:[0],esp
```

先向栈中压入了Handler和当前的节点，他们就又构成了一个EXCEPTION_REGISTRATION_RECORD结构，而esp指向栈顶，正好就是新的EXCEPTION_REGISTRATION_RECORD，将它付给fs:[0]也就是让SEH的头节点变成了刚刚加入的新节点。

卸载过程其实就是恢复栈平衡，代码如下

```
mov esp,dword ptr fs:[0]
pop dword ptr fs:[0]
```

要注意，SEH异常的安装实际上从main函数之前就开始了，当我们在启动一个进程时，实际的启动位置也就是kernel!32BaseProcessStartThunk，而在这个函数内就已经开始有try、catch结构了，线程的启动函数kernel!32BaseThreadStart也是如此

```
VOID BaseThreadStart(PTHREAD_START_ROUTINE pfnStartAddr, PVOID pvParam) `{`
    __try`{`
        ExitThread((pfnStartAddr)(pvParam));
    `}`
    __except (UnhandledExceptionFilter(GetExceptionInformation()))`{`
        ExitProcess(GetExceptionCode());
    `}`
`}`
```

实际上这里的try catch结构构成的异常回调函数就是常说的top level，即顶层异常处理，它们也是SEH链的最后一部分，并且可以看到，它们的except还存在一个叫做UnhandledFilter函数，和字面上的意思相似，这是用来实现异常过滤的函数，这是非常重要的一个函数，我们后面会细讲。

### <a class="reference-link" name="RltDispatchExeption"></a>RltDispatchExeption

当我们的异常分发到了RtlDispatchException函数时，就会根据线程注册的SEH来处理该异常，之前的处理实际上都是简单的”打包”和”描述”的过程，到了这一步才开始真正的异常处理。为了个更好的理解这个过程，这里笔者给出了简化版的RltDispatchExeption伪代码，简单描绘一下该函数的执行过程，伪代码由笔者根据逆向和资料自行编写，有错误之处还望大家指出

```
if VEH异常处理例程 != Exception_continue_search
    goto end_func

else
    limit = 栈的limit
    seh = 借助FS寄存器获取SEH的头节点
    while(seh!=-1):
        if SEH节点不在栈中 || SEH节点位置没有按ULONG对齐 || Handler在栈中
            goto end_func
        else
            seh = 当前seh指向的下一个seh
    seh = 借助FS寄存器获取SEH的头节点
    while(seh!=-1):
        if(检查safeseh)
            goto end_func
        else
            return_value = 执行该seh的handler
            switch(return_value):
                case 处理成功:
                    flag=1
                    goto end_func
                case 没法处理:
                    seh = 当前seh指向的下一个seh
                case 处理时再次遭遇异常
                    设置标记，做内嵌异常处理
                    goto    end_func


end_func:
    调用VEH的continue handler
    return
```

函数执行过程中实际上大部分的代码都是在对SEH机制进行检查，其主要包括了SEHOP和SafeSEH等，这里先暂且略过，在后面会放在一起讲。除去检查外，我们可以概括步骤如下：
- 调用VEH ExceptionHandler进行处理，成功则结束，否则进行SEH
<li>遍历SEH节点，对每一个Handler进行RtlExceptionHandlerForException，根据返回值执行不同操作
<ul>
- ExceptionContinueExecution，表示异常已经被处理过了，接下来就可以回到之前的异常现场（借助之前讲过的Context）再执行试试了。但是这里就有两个重要的问题了，我们的回调函数真的成功处理了这个异常吗？我们的context被修改了怎么办？第一个问题的很简单 —— 不知道，系统是很”傻”的，只要你返回了这个值它就认为你成功了，而如果你压根就没处理还返回就会造成下次再执行还是错的，还是触发异常处理，进而陷入无限处理这个异常的循环状态。 第二个问题更简单了，被修改就完蛋了，不但异常没处理好，还搞出来个任意地址返回
- ExceptionContinueSearch，表示这个节点的handler处理不了这个异常，此时就会借助Next指针去寻找下一个节点接着去处理
- ExceptionNestedException，这个是最让人无奈的，意思是处理异常时又引发了一个新的异常，如果是内核态遇到了这个问题就直接game over蓝屏了，如果是用户态的话就成了”嵌套”异常，也就是会在此处再次进行异常处理
- ExceptionCollidedUnwind，这个和上面的类似，不过上面是异常处理时遇到了麻烦，而这个是在恢复现场的时候遇到了不测，这个”恢复现场”的过程也叫做展开，下面会具体说明。这个结果非常罕见，因为恢复现场的工作时系统来完成的，处理得非常严谨。
### <a class="reference-link" name="%E6%A0%88%E5%B1%95%E5%BC%80"></a>栈展开

在SEH的处理体系中，如果所有的异常回调函数都无法处理某个异常时，系统会让发生异常的线程中所有的回调函数一个执行的机会，主要是为了实现清理、释放资源，保存异常的信息等功能，这也就是栈展开的基本概念，下面我们具体来看一下它。

还记得上一篇文中提到的EXCEPTION_RECORD结构吗？它有个ExceptionFLags的标志位，我们之前没有仔细提，实际上它就会在这里发挥作用，0代表着可修复的异常，1表示不可修复的异常，2则表示展开操作，通常在用户态的异常不会涉及到1，一般是在异常嵌套或者是内核异常时会用到。当某个异常遍历完SEH链后依然没有能够执行的话，就会将该标志位置为2，并将ExceptionCode设置为ST0ATUS_UNWIND，来执行栈展开操作。

RtlUnwind函数通常用来实现该功能，其函数原型如下：

```
RtlUnwind(EXCEPTION_REGISTRATION VirtualTargetFrame,INT * TargetPC,EXCEPTION_RECORD ExceptionRecord,INT ReturnValue)
```
- VirtualTargetFrame指向的是SEH链的EXECEPTION_REGISTRATION结构，表示要在哪个节点停止并进行展开操作
- TargetPC是调用RtlUnwind后的返回地址，如果是0则直接跳转至下一条指令
- Exception_record，当前异常的EXCEPTION_RECORD结构
因为栈展开的详细过程较难理解且过于复杂，有兴趣的读者可以自行搜索相关资料学习

### <a class="reference-link" name="UnhandledExceptionFilter%E5%87%BD%E6%95%B0"></a>UnhandledExceptionFilter函数

未处理异常过滤函数，简称为UEF函数，这可以说是异常处理的最后一道防线了，他也是异常处理和windows error report交接的关键，首先来看看这个函数的大致流程
<li>错误的预处理，主要是对三个方面的检查：
<ul>
- 是否存在着嵌套异常？上面说过了嵌套异常是一种非常难处理的情况，如果处理的不好就很难再恢复原始的状态了，于是这种情况下UEF函数会直接调用NtTerminateProcess结束当前的进程
- 是否是违例访问？还记得我们上一次windbg分析格蠹汇编的练习题吗？出现了0xc0000005的错误码，这就是EXCEPTION_ACCESS_VIOLATION，也就是所谓的违例访问。这种情况下UEF函数会尝试去通过更改页属性的方式去修复错误，当然如果你访问的是绝对不该访问的页，那UEF就无法解决了。
- DebugPort有没有？DebugPort在异常分发的过程中起到了标志着调试器是否开启的任务，一旦UEF检测到了DebugPort那它就不会处理该异常，而是返回一个ExceptionContinueSearch，而它作为最后的异常处理也没有处理该异常的话自然也就进入了第二次的异常分发，成功使调试器接手该异常- 根据程序的设置直接结束进程。windows提供了SetErrorMode的api用来设置某个标志位，一旦设置了，那那就不会出现任何的错误提示，程序直接结束。判断当前进程是否在job（以后会详细总结）中，如果在而且设置了未处理异常时直接结束，那就直接杀掉进程。
- 查看是否设置了JIT调试，如果是就开始进行调试。在上一章里我们实际设置并借助JIT进行了分析，实际上JIT的响应就是发生在UEF函数中的
- 弹出异常信息。此时程序会加载faultrep.all，调用ReportFault函数来汇报错误，如果设置了错误报告或者是非常严重的错误会弹出error窗口询问用户是否要发送错误报告，而其余情况下就会弹出我们熟知的application error
当然我们也可以设置自己的UEF函数，我们可以通过SetUnhandledExceptionFilter函数来设置，UEF会在上面说的两步之间执行我们自定义的代码，还可以根据具体的返回值在后面执行不同的操作，而这也就是之前提到的try 、catch构成的top level，顶层异常处理函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ws3.sinaimg.cn/large/006tKfTcly1g1lurzupb8j30u0112tkt.jpg)

​ 图片来自《windows核心编程》



## VEH

VEH（Vectored Exception Handling）也就是向量化异常处理，是windows在xp之后新加入的一种异常处理机制，我们在RltDispatchException已经看到过它在异常处理时的调用过程了，下面就看看它的具体实现流程。

首先VEH也需要注册回调函数，而且也同样是用链表的结构来维护的。注册函数的原型如下

```
WINBASEAPI PVOID WINAPI AddVectoredExceptionHandler(ULONG FirtstHandler,PVECTORED_EXCEPTION_HANDLER VectoreHandler)

```

第一个参数是一个标志位，它用来标示注册的回调函数是在链表的头还是尾，0是插入尾部，非0则是插入头部，第二个参数是回调函数的地址，它会返回一个VectoredHandlerHandle，用于之后卸载回调函数。

回调函数的原型如下

```
LONG CALLBACK Vectorhandler()

```

在RltDispatchException的过程中VEH将会优先于SEH调用，如果回调函数成功解决了问题和SEH相似，都会返回ExceptionContinueExecution表示异常处理完毕，然后借助CONTEXT的内容恢复上下文，跳过SEH继续执行程序，如果失败了就遍历VEH链表寻找解决方法，如果所有的回调函数都不能处理的话再将执行权归还，继续向下执行SEH的相关内容。

可能到这有人就有疑问了，这不就是SEH的翻版吗，为什么微软还要搞个这玩意？实际上这和SEH相比有很多的不同之处，它俩有着相似的”外表”，却有着不同的”内在”。

最明显的就是优先级的不同，这里的优先级有两个含义，一是VEH比起SEH更加优先调用，二是VEH可以自行设置回调函数的位置。一不必多说，VEH会调用得更早，二就很有意思了，我们已经知道了SEH会不管三七二十一把我们最后定义的异常回调函数放到链表头部，也就是说顺序被写死了，我们如果想让某个异常回调函数优先进行处理是不可能的，而VEH由于可以自定义插入的位置，我们就可以实现一定程度上的自定义处理顺序了。

其次可以看到VEH和SEH注册的原理是完全不同的，SEH最终落在了栈上，而实际上VEH保存在了ntdll中，这就又导致了SEH只能是针对某个线程进行异常处理（因为每个线程维护着自己的栈结构），而VEH则可以对整个进程进行处理。

最后VEH的收尾也要更加简单，SEH因为占用了栈空间，调用回调函数时会有栈展开的问题，处理非常复杂，而VEH和一般的函数无异了。



## 异常的保护机制

我们已经详细了解了整个异常的执行流程，我们不难发现，以ntdll作为基础的VEH并不容易被我们利用，但以栈作为基础的SEH本身具有很大的危险性，我们可以利用各种手段对栈上SEH节点进行覆盖重写，再次执行异常处理操作时就会将执行权给到了我们用来覆盖的函数上，这实际上在以前是很常见的windows栈溢出手段，当然，除了这种方法外还有许许多多的利用手段，可见这样的异常处理机制还是不够完善的。为了解决这些问题，微软逐步加入了Safe SEH、SEHOP、VCH等来弥补。

### <a class="reference-link" name="Safe%20SEH"></a>Safe SEH

SafeSEH又叫做软件DEP，是一种在软件层面实现的对SEH的保护机制，它需要操作系统和编译器的双重支持，在vs2013及以后的版本中会自动启用 /SafeSEH 链接选项来使用SafeSEH。也正是因为该项技术使得以往简单的覆盖异常处理句柄的漏洞利用几乎失效了

在加载PE文件时，SafeSEH将定位合法的SEH表的地址（如果该映像不支持SafeSEH的话则地址为0），然后是用共享内存中的一个随机数进行加密处理，程序中所有的异常处理函数的地址提取出来汇总放入SEH表，并将该表放入程序映像中，还会将将加密后的SEH函数表地址，IMAGE的开始地址，IMAGE的长度，合法SEH函数的个数，作为一条记录放入ntdll（ntdll模块是进行异常分发的模块）的加载模块数据内存中,每次调用异常处理函数时都会进行校验，只有二者一致才能够正常进行，该处理由RtlDispatchException() 开始，首先会经历两次检查，分别是：
- 检查异常处理链是否在当前的栈中，不是则终止
- 检查异常处理函数的指针是否指向栈，是则终止
通过两次检查后会调用RtlIsValidHandler() 来进行异常的有效性检查，08年的black hat给出了该函数的细节

```
BOOL RtlIsValidHandler( handler )
`{`
    if (handler is in the loaded image)      // 是否在loaded的空间内
    `{`
        if (image has set the IMAGE_DLLCHARACTERISTICS_NO_SEH flag) //是否设置了忽略异常
            return FALSE;                  
        if (image has a SafeSEH table)       // 是否含有SEH表
            if (handler found in the table)  // 异常处理函数地址是否表中
                return TRUE;
            else
                return FALSE;
        if (image is a .NET assembly with the ILonl    y flag set)
            return FALSE;                    
    `}`

    if (handler is on non-executable page)   // handler是否在不可执行页上
    `{`
        if (ExecuteDispatchEnable bit set in the process flags) //DEP是否开启
            return TRUE;                     
        else
            raise ACCESS_VIOLATION;          
    `}`

    if (handler is not in an image)          // handler是否在未加载空间
    `{`
        if (ImageDispatchEnable bit set in the process flags) //设置的标志位是否允许
            return TRUE;                     
        else
            return FALSE;
    `}`
    return TRUE;                             /s/ 允许执行异常处理函数
`}`
```

代码中的ExecuteDispatchEnable和ImageDispatchEnable位标志是内核KPROCESS结构的一部分，这两个位用来控制当异常处理函数在不可以执行内存或者不在异常模块的映像（IMAGE）内时，是否执行异常处理函数。这两个位的值可以在运行时修改，不过默认情况下如果进程的DEP被关闭，则这两个位置1，如果进程的DEP是开启状态，则这两个位被置0。

通过源码我们可以看出，RtlIsValidHandler() 函数只会在以下几种情况执行异常处理函数
<li>在进程的DEP是开启的情况下
<ul>
- 异常处理函数和进程映像的SafeSEH表匹配且没有NO_SEH标志。
- 异常处理函数在进程映像的可执行页，并且没有NO_SEH标志，没有SafeSEH表，没有.NET的ILonly标志。- 异常处理函数和进程映像的SafeSEH表匹配没有NO_SEH标志。
- 异常处理函数在进程映像的可执行页，并且没有NO_SEH标志，没有SafeSEH表，没有.NET的ILonly标志。
- 异常处理函数不在当前进程的映像里面，但是不在当前线程的堆栈上。
### <a class="reference-link" name="SEHOP"></a>SEHOP

全称为Structured Exception Handler Overwrite Protection（结构化异常处理覆盖保护），这是专门用来检测SEH是否被劫持的一项技术，我们在上面的RltDispatchExeption实际上已经提到过一些SEHOP的检测过程了，这里我们来具体说一说

```
HKEY_LOCAL_MACHINESYSTEMCurrentControlSetControlSession Managerkernel
```

你可以在该表项下找到DisableExceptionChainValidation的键，它标示着你的计算机是否开启了该功能。

我们再次回到RltDispatchExeption来看看它的具体操作，代码来自Vistasp1

```
// Skip the chain validation if the DisableExceptionChainValidation bit is set
if (process_flags &amp; 0x40 == 0)
`{`
    // Skip the validation if there are no SEH records on the linked list
    if (record != 0xFFFFFFFF)
    `{`
        // Walk the SEH linked list
        do
        `{`
            // 1、The record must be on the stack
            if (record &lt; stack_bottom || record &gt; stack_top)
                goto corruption;

            // 2、The end of the record must be on the stack
            if ((char*)record + sizeof(EXCEPTION_REGISTRATION) &gt; stack_top)
                goto corruption;

            // 3、The record must be 4 byte aligned
            if ((record &amp; 3) != 0)
                goto corruption;

            handler = record-&gt;handler;
            // 4、The handler must not be on the stack
            if (handler &gt;= stack_bottom &amp;&amp; handler &lt; stack_top)
                goto corruption;

            record = record-&gt;next;
        `}` while (record != 0xFFFFFFFF);

        // End of chain reached
        // Is bit 9 set in the TEB-&gt;SameTebFlags field? This bit is set in
        // ntdll!RtlInitializeExceptionChain, which registers
        // FinalExceptionHandler as an SEH handler when a new thread starts.
        if ((TEB-&gt;word_at_offset_0xFCA &amp; 0x200) != 0) `{`
            // 5、The final handler must be ntdll!FinalExceptionHandler
            if (handler != &amp;FinalExceptionHandler)
                goto corruption;
        `}`
    `}` // end if (record != 0xFFFFFFFF)
`}`
```

大家可自行阅读代码，概括来说主要是对以下几点的检测：
- SEH节点必须在栈上
- SEH节点的Handle必须不在栈上
- 最后的SEH节点的Handle必须是ntdll!FinalExceptionHandler，也就是咱们上面说的异常的最后一站
- 最后的SEH节点的Next指针必须为0xffffffff
可以看到SEHOP的防御十分的严格，但并不代表它就一定安全了，我们还是可以通过各种手段进行绕过，关于如何绕过的内容在以后的《windows调试艺术》中还会有，这里就先不展开了。
