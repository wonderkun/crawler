> 原文链接: https://www.anquanke.com//post/id/221402 


# Windows下利用IoDriverObjectType控制内核驱动加载的探索与研究


                                阅读量   
                                **170810**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01c4da69953fa1a629.jpg)](https://p0.ssl.qhimg.com/t01c4da69953fa1a629.jpg)



在edr或者其他类型的安全软件我们通常要监测当前系统的内核驱动的加载，通常使用的方法是PsSetLoadImageNotifyRoutine设置模块加载回调例程来监控ring3模块以及ring0模块的加载，回调函数 eLoadImageNotifyRoutine 的第二个参数判断，如果 PID是0 ，则表示加载驱动，如果PID非零，则表示加载DLL。此方法的优点是：

<strong>更底层<br>
方法简单通用</strong>

缺点当然也就是函数太底层，第二就是方法太通用几乎做过进程、线程监控的搞安全内核开发的人基本都晓得，也很容易被发现，而且也会被摘链，而失效。第三到回调函数这步骤的时候有可能内核已经被加载，被加载的内核驱动的入口点已经执行完毕。<br>
本篇文章将会探索一种新方法去监测并且控制内核模块的加载。首先我们要讲解内核加载驱动的过程。<br>
写一个demo的驱动，然后使用VMware双机调试来调试驱动。(VMware双机调试的方法如果不会可以baidu)

[![](https://p1.ssl.qhimg.com/t015db21caf7560b3df.png)](https://p1.ssl.qhimg.com/t015db21caf7560b3df.png)

连接被调试虚拟机后，在windbg里输入sxe ld demo驱动的名字.sys

[![](https://p5.ssl.qhimg.com/t013fbddcc1c5283421.png)](https://p5.ssl.qhimg.com/t013fbddcc1c5283421.png)

然后go，如果加载系统要加载这个驱动windbg会自动停下来。

[![](https://p1.ssl.qhimg.com/t011fe172d885b040d6.png)](https://p1.ssl.qhimg.com/t011fe172d885b040d6.png)

然后输入kb

[![](https://p3.ssl.qhimg.com/t0133ac7da8d4df1974.png)](https://p3.ssl.qhimg.com/t0133ac7da8d4df1974.png)

可以看到内核里加载的时候会开启一个单独的线程去加载驱动

```
# RetAddr : Args to Child : Call Site

00 fffff800`04b1748d : fffff880`0456b8a0 fffff880`031ac0d0 00000000`00000001 fffff800`04b74dfe : nt!DebugService2+0x5
01 fffff800`04b74ecb : fffff880`031ac000 fffffa80`016de070 fffff880`0456b9b8 00000000`00000007 : nt!DbgLoadImageSymbols+0x4d
02 fffff800`04e47bfd : fffffa80`00eeee20 fffff8a0`0000001c fffff800`04d84a30 fffff880`0456b888 : nt!DbgLoadImageSymbolsUnicode+0x2b
03 fffff800`04e6286b : fffff880`031ac000 fffff880`0456b8f8 00000000`00000000 fffff880`0456b8d8 : nt!MiDriverLoadSucceeded+0x2bd
04 fffff800`04e64ebd : fffff880`0456b9b8 00000000`00000000 00000000`00000000 00000000`00000000 : nt!MmLoadSystemImage+0x80b
05 fffff800`04e65875 : 00000000`00000001 00000000`00000000 00000000`00000000 fffffa80`0231c1e0 : nt!IopLoadDriver+0x44d
06 fffff800`04a8b161 : fffff800`00000000 ffffffff`8000077c fffff800`04e65820 fffffa80`006db040 : nt!IopLoadUnloadDriver+0x55
07 fffff800`04d21166 : 00000000`00000000 fffffa80`006db040 00000000`00000080 fffffa80`006b71d0 : nt!ExpWorkerThread+0x111
08 fffff800`04a5c486 : fffff800`04bf6e80 fffffa80`006db040 fffffa80`006da680 00000000`00000000 : nt!PspSystemThreadStartup+0x5a
09 00000000`00000000 : fffff880`0456c000 fffff880`04566000 fffff880`0456ae60 00000000`00000000 : nt!KiStartSystemThread+0x16
```

这是调试的时候被断点断下来的堆栈，我们需要回到加载驱动的地方，所以要打开源代码，在驱动的入口点DriverEntry按F9设置断点。

[![](https://p0.ssl.qhimg.com/t019802e51c6c4435c1.png)](https://p0.ssl.qhimg.com/t019802e51c6c4435c1.png)

然后f5继续执行，之后就会停在驱动的入口点

[![](https://p4.ssl.qhimg.com/t01d02ac988273fe099.png)](https://p4.ssl.qhimg.com/t01d02ac988273fe099.png)

紫红色表示已经运行到断点位置。<br>
当我们使用!process 命令时会看到当前上下文是system

[![](https://p5.ssl.qhimg.com/t01a6529743269d5282.png)](https://p5.ssl.qhimg.com/t01a6529743269d5282.png)

再次使用kb可以发现现在执行到入口点的栈的上下文是

[![](https://p3.ssl.qhimg.com/t01075667c9dec49936.png)](https://p3.ssl.qhimg.com/t01075667c9dec49936.png)

```
01 fffff880`0456b960 fffff800`04e65875 nt!IopLoadDriver+0xa07
02 fffff880`0456bc30 fffff800`04a8b161 nt!IopLoadUnloadDriver+0x55
03 fffff880`0456bc70 fffff800`04d21166 nt!ExpWorkerThread+0x111
04 fffff880`0456bd00 fffff800`04a5c486 nt!PspSystemThreadStartup+0x5a
05 fffff880`0456bd40 00000000`00000000 nt!KiStartSystemThread+0x16
```

可以发现在 nt!IopLoadDriver+0xa07的位置是执行入口点<br>
使用U命令，可以查看汇编代码

```
fffff80004e6546e 488bd6 mov rdx,rsi
fffff80004e65471 488bcb mov rcx,rbx
fffff80004e65474 ff5358 call qword ptr [rbx+58h]
fffff80004e65477 4c8b15627bdaff mov r10,qword ptr [nt!PnpEtwHandle (fffff80004c0cfe0)]
fffff80004e6547e 8bf8 mov edi,eax
```

** call qword ptr [rbx+58h]**这句代码就是执行被加载驱动的模块入口点函数

看汇编代码第一个参数rcx就是rbx,大致我们可以明确的就是rbx就是DriverEntry的DRIVER_OBJECT参数，所以就有了rbx+58h就是DRIVER_OBJECT的DriverInit，为了印证我们的猜测，在IDA下看rbx就是DRIVER_OBJECT的结构体，而这里的call执行的就是DriverInit

[![](https://p5.ssl.qhimg.com/t018c947323f956b798.png)](https://p5.ssl.qhimg.com/t018c947323f956b798.png)

**Call v29-&gt;DriverInit(v29, v32);**

有了这样的过程，我们是不是就可以探索新的方法去控制驱动的加载呢？答案是肯定的。查看IDA，可以发现在执行驱动入口点之前这个过程内核会处理很多东西，比如分配内存啊，创建驱动的内核对象啊，驱动的权限的判断，创建内核镜像啊等等操作，凡是可以控制的地方我们都可以研究下，今天我们主要研究是内核Object这个东西，众所周知windows内部管理着很多的Object，windows专门有个内核对象管理器，我们通常说的文件、进程、线程、管道、油槽、内核Image等等都属于Object,windows在使用额时候总是会先CreateObject 然后在插入这个Object到object管理器中，成功了才会继续执行，所以在加载内核模块镜像的时候也一定会创建一个Object，然后在插入这个对象。

因为**DRIVER_OBEJCT**就是一个Object，我们可以通过追踪**DRIVER_OBEJCT**的生成来劫持控制驱动的加载。

查看IDA分析过程，对**IopLoadDriver**的函数分析可以发现，在调用入口点之上确实有个ObInsertObject的函数，而且该函数插入的就是DERIVER_OBJECT对象

[![](https://p2.ssl.qhimg.com/t0127aaac26c843181d.png)](https://p2.ssl.qhimg.com/t0127aaac26c843181d.png)

**v10 = ObInsertObject(v21, 0i64, 1u, 0, 0i64, &amp;Handle);**

有了这个函数我们就可以控制对象了，怎么控制呢？答案很简单，对象的回调函数。

**ObInsertObject**的函数内部是会经过每种对象类型对象的回调函数设置的。下面分析怎么到达过滤回调callback的。

**在ObInsertObject内部会先调用ObInsertObjectEx函数**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e42c47642e75d034.png)

在**ObInsertObjectEx**内部会调用**ObpCreateHandle**

[![](https://p3.ssl.qhimg.com/t0133623f6d60a172dd.png)](https://p3.ssl.qhimg.com/t0133623f6d60a172dd.png)

此时的第一个参数是0，而在ObpCreateHandle函数内部会调用<br>**v51 = ObpPreInterceptHandleCreate(Objecta, Attributes, &amp;v70, &amp;ThreadCallbackListHead);**

[![](https://p3.ssl.qhimg.com/t01832292ff3f8e987f.png)](https://p3.ssl.qhimg.com/t01832292ff3f8e987f.png)

** ObpPreInterceptHandleCreate**函数就是我之前说的在调用当前对象类型的callback函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01421d89891a28773c.png)

所以**调用路径**是

[![](https://p1.ssl.qhimg.com/t01f569a8469bf46fca.png)](https://p1.ssl.qhimg.com/t01f569a8469bf46fca.png)

有ObInsertObject就一定会有ObCreateObject这个函数，往上继续翻阅就会看到

[![](https://p1.ssl.qhimg.com/t018ff61f9fdacd7751.png)](https://p1.ssl.qhimg.com/t018ff61f9fdacd7751.png)

```
v10 = ObCreateObject(
              KeGetCurrentThread()-&gt;PreviousMode,
              IoDriverObjectType,
              &amp;ObjectAttributes,
              0,
              0i64,
              0x188u,
              0,
              0,
              &amp;v74),
```

创建的是**IoDriverObjectType**这种类型的对象，理论上是可以在代码上对**IoDriverObjectType**注册**callback**，而且这个对象微软是可以外部直接链接的，不需要使用搜索的方法去寻找这个对象类型，下面就是检验理论猜想。

在之前的demo实例在加上一段代码注册回调

```
Globals.ob_operation_registrations.ObjectType = IoDriverObjectType;
   Globals.ob_operation_registrations.Operations |= OB_OPERATION_HANDLE_CREATE;
   Globals.ob_operation_registrations.Operations |= OB_OPERATION_HANDLE_DUPLICATE;
   Globals.ob_operation_registrations.PreOperation = CBTdPreOperationCallback;
   Globals.ob_operation_registrations.PostOperation = CBTdPostOperationCallback;
   Globals.ob_registration.Version                    = ObGetFilterVersion();
   Globals.ob_registration.OperationRegistrationCount = 1;
   //CBObRegistration.Altitude                   = CBAltitude;
   Globals.ob_registration.RegistrationContext        = NULL;
   Globals.ob_registration.OperationRegistration      = &amp;(Globals.ob_operation_registrations);     

   Status = ObRegisterCallbacks (
       &amp;(Globals.ob_registration),
       &amp;(Globals.registration_handle)       // save the registration handle to remove callbacks later
       ); 
   if ( NT_SUCCESS(Status))
   `{`
       Globals.ob_protect_installed = TRUE;
   `}`
```

然后继续使用双机调试，在入口点下断点

[![](https://p2.ssl.qhimg.com/t01fda79451c7cd1195.png)](https://p2.ssl.qhimg.com/t01fda79451c7cd1195.png)

进入断点后，继续单步F10，执行过注册后status返回0表示注册成功（**注意这里我是用了一些hack手法所以成功了，方法暂时不公开**）

[![](https://p1.ssl.qhimg.com/t013c62d51d930d2d01.png)](https://p1.ssl.qhimg.com/t013c62d51d930d2d01.png)

显示驱动启动成功

[![](https://p0.ssl.qhimg.com/t01f1685a94864704aa.png)](https://p0.ssl.qhimg.com/t01f1685a94864704aa.png)

在我们设置的回调函数的地方下断点，看看加载驱动的时候是否会进入回调，在虚拟机里安装sysmon这个软件，他是会加载一个文件驱动的。

[![](https://p0.ssl.qhimg.com/t016eb045805c576ce2.png)](https://p0.ssl.qhimg.com/t016eb045805c576ce2.png)

成功断下来了

[![](https://p4.ssl.qhimg.com/t01dde8fa3969dd5a5e.png)](https://p4.ssl.qhimg.com/t01dde8fa3969dd5a5e.png)

查看PreInfo-&gt;Object<br>
使用dt nt!_DRIVER_OBJECT PreInfo-&gt;Object

[![](https://p3.ssl.qhimg.com/t017a2a687cb2c3218a.png)](https://p3.ssl.qhimg.com/t017a2a687cb2c3218a.png)

确实是sysmon的驱动sysmonDrv,他的入口点是sysmonDrv+1e058，看来这个方法确实有效，接下来我们要把driver_init设置为0，尝试修改<br>**Eq xxxxxxx 0 修改成0**

[![](https://p5.ssl.qhimg.com/t016cb924d3d70a9443.png)](https://p5.ssl.qhimg.com/t016cb924d3d70a9443.png)

接下来直接f5，成功蓝屏

[![](https://p1.ssl.qhimg.com/t01bd0623e9038f97fb.png)](https://p1.ssl.qhimg.com/t01bd0623e9038f97fb.png)

因为我们把入口点设置为0，所以一到执行入口点就蓝屏，说明我们可以从代码上控制驱动加载。Kb后显示堆栈，驱动执行路径

[![](https://p5.ssl.qhimg.com/t015631bbbb50659b44.png)](https://p5.ssl.qhimg.com/t015631bbbb50659b44.png)

**<a class="reference-link" name="RetAddr%20:%20Args%20to%20Child%20:%20Call%20Site"></a>RetAddr : Args to Child : Call Site**

```
00 fffff800`042b3477 : fffffa80`029c81c0 fffffa80`029c81c0 00000000`00000000 00000000`000007ff : 0x0
01 fffff800`042b3875 : 00000000`00000001 00000000`00000000 00000000`00000000 fffffa80`029c82f8 : nt!IopLoadDriver+0xa07
02 fffff800`03ed9161 : fffff8a0`00000000 ffffffff`80000f54 fffff800`042b3820 fffffa80`00711680 : nt!IopLoadUnloadDriver+0x55
03 fffff800`0416f166 : 00000000`00000000 fffffa80`00711680 00000000`00000080 fffffa80`006ed1d0 : nt!ExpWorkerThread+0x111
04 fffff800`03eaa486 : fffff800`04044e80 fffffa80`00711680 fffffa80`00711b60 00000000`00000000 : nt!PspSystemThreadStartup+0x5a
05 00000000`00000000 : fffff880`0457a000 fffff880`04574000 fffff880`04578590 00000000`00000000 : nt!KiStartSystemThread+0x16
```

也就是**call 0** ，我们设置的驱动入口下面我就方便修改demo驱动代码去控制驱动的加载了入口点。<br>
在**CBTdPreOperationCallback**的函数里加一个修改DriverInit的数值，然后赋值为我们自定义的FakeDriverEntry函数

[![](https://p4.ssl.qhimg.com/t015920a0ca61e9f08e.png)](https://p4.ssl.qhimg.com/t015920a0ca61e9f08e.png)

[![](https://p1.ssl.qhimg.com/t01bc412d6480652ed9.png)](https://p1.ssl.qhimg.com/t01bc412d6480652ed9.png)

实现FakeDriverEntry函数如下：

[![](https://p2.ssl.qhimg.com/t01fbe50bc13333e741.png)](https://p2.ssl.qhimg.com/t01fbe50bc13333e741.png)

下面再次开启双机调试，同样在虚拟机里执行**sysmon –i**

[![](https://p5.ssl.qhimg.com/t01f51b513c04b73672.png)](https://p5.ssl.qhimg.com/t01f51b513c04b73672.png)

[![](https://p1.ssl.qhimg.com/t0137475b0046342c29.png)](https://p1.ssl.qhimg.com/t0137475b0046342c29.png)

断点断在了回调函数的**DRIVER_OBJECT** pDriverObj = DRIVER_OBJECT**)PreInfo-&gt;Object;**<br>
查看PDriverObj对象

[![](https://p4.ssl.qhimg.com/t012983ab27a141ef9e.png)](https://p4.ssl.qhimg.com/t012983ab27a141ef9e.png)

U 入口点的函数**u 0xfffff880`02ac2058**

[![](https://p0.ssl.qhimg.com/t01dd3c80a3ae2f34b5.png)](https://p0.ssl.qhimg.com/t01dd3c80a3ae2f34b5.png)

下面单步执行后会修改sysmonDrv驱动的DriverInit入口点<br>
同时在FakeDriverEntry下断点

[![](https://p5.ssl.qhimg.com/t0127bbb142f946ab95.png)](https://p5.ssl.qhimg.com/t0127bbb142f946ab95.png)

直接f5, 断点就直接断在了我们的Fake函数里

[![](https://p0.ssl.qhimg.com/t01a32ba581b1ac5267.png)](https://p0.ssl.qhimg.com/t01a32ba581b1ac5267.png)

使用kb命令查看堆栈

[![](https://p4.ssl.qhimg.com/t0196f3630de87f12d1.png)](https://p4.ssl.qhimg.com/t0196f3630de87f12d1.png)

确实执行了call，继续F5，这时我们观察sysmon命令行返回

[![](https://p2.ssl.qhimg.com/t011d6c1d1e576a1da1.png)](https://p2.ssl.qhimg.com/t011d6c1d1e576a1da1.png)

<strong>Sysmon installed.<br>
SysmonDrv installed.<br>
StartService failed for SysmonDrv<br>
Failed to start the driver:<br>
Stopping the service failed:</strong>

Sysmon的驱动加载失败了，说明成功的控制了驱动的加载，从而证明了这种方案的可行。

```
总结，有些知识是已经众所周知的，但是更多的新的方法是需要我们在这些知识点反复研究反复揣摩，反复猜想，然后加以论证，才能获得意想不到额结果，当然今天这个注册回调不是随便就可以注册的，需要反复逆向去修改标志位实现的hack的方法去实现注册回调，具体读者自行研究，我这里只提供方法可行性。
```
