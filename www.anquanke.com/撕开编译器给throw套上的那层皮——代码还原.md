> 原文链接: https://www.anquanke.com//post/id/208939 


# 撕开编译器给throw套上的那层皮——代码还原


                                阅读量   
                                **189013**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0111d5175a71aa45ac.jpg)](https://p5.ssl.qhimg.com/t0111d5175a71aa45ac.jpg)



## 1、前言

做软件开发的同事或多或少都用过throw，而我是个例外，我第一次“真正接触”throw，是在一次dmp的分析中，追踪异常数据时，深入的挖了下，觉得里边有些东西对大家在开发中遇到异常时，可能会有些帮助。本文经过简单的逆向分析，弄清楚有关于throw的全貌，使得你将来无论是使用throw还是分析dmp时，都如鱼得水，游刃有余。撰以小文，与君分享。



## 2、实验分析过程

写了个简单的demo如下，完全是为了演示throw，演示环境为VS2010，X86，Release；

```
class MyBaseException
`{`
public:
       MyBaseException()
       `{`
              std::cout&lt;&lt;"BaseException"&lt;&lt;std::endl;
       `}`
`}`;

class MyException:public MyBaseException
`{`
private:
       int m_a;
       int m_b;
       int m_c;
       char m_name[100];
public:
       MyException(const char * str,int a,int b,int c)
       `{`
              strcpy_s(m_name,100,str);
              m_a = a;
              m_b = b;
              m_c = c;
       `}`

       int get_a()`{`return m_a;`}`
       virtual int get_b()`{`return m_b;`}`
       virtual int get_c()`{`return m_c;`}`
       virtual char * get_name()`{`return m_name;`}`
`}`;

int main()
`{`
       throw MyException("exception_demo",1,2,3);
       return 0;
`}`
```

运行之后，不出意外是这样子的，如下图所示

[![](https://p2.ssl.qhimg.com/t01a7bda7e6ab2f6c48.png)](https://p2.ssl.qhimg.com/t01a7bda7e6ab2f6c48.png)

[![](https://p3.ssl.qhimg.com/t01b36f32cf954c8169.png)](https://p3.ssl.qhimg.com/t01b36f32cf954c8169.png)

直接点击”调试“按钮即可，说明下，我习惯用Windbg调试和分析问题，所以我将Windbg设置为JIT了。这边看个人喜好；由于我的设置，我这里默认拉起来的就是Windbg了；来看下拉起来的样子，如上右图所示；下边就可以开始分析了；

看过我之前的文章的同学都可能会想到我常用的两个命令”.exr -1”和”.ecxr”，可这里他不灵了，不信你看：

```
0:000&gt; .exr -1
Last event was not an exception
0:000&gt; .ecxr
Unable to get exception context, HRESULT 0x8000FFFF
```

留个小小的思考题，为什么在这里，这两个命令突然失效了？答案文末给出。既然这招行不通，那就先看看调用栈，如下：

```
0:000&gt; kb
# ChildEBP RetAddr  Args to Child
00 00fff3d0 76f314ad ffffffff 00000003 00000000 ntdll!NtTerminateProcess+0xc
01 00fff4a8 75725902 00000003 77e8f3b0 ffffffff ntdll!RtlExitUserProcess+0xbd
02 00fff4bc 715e7997 00000003 00fff50c 715e7ab0 KERNEL32!ExitProcessImplementation+0x12
03 00fff4c8 715e7aaf 00000003 30b17962 00000000 MSVCR100!__crtExitProcess+0x17
04 00fff50c 7161bf47 00000003 00000001 00000000 MSVCR100!doexit+0xfb
05 00fff520 7164d707 00000003 7164383d 30b17936 MSVCR100!_exit+0x11
06 00fff528 7164383d 30b17936 00000000 00000000 MSVCR100!abort+0x32
07 00fff558 00911897 00fff5fc 7664ba90 00fff62c MSVCR100!terminate+0x33 
08 00fff560 7664ba90 00fff62c 255e6b41 00000000 test!__CxxUnhandledExceptionFilter+0x3c
09 00fff5fc 76f829b8 00fff62c 76f563d2 00fffe60 KERNELBASE!UnhandledExceptionFilter+0x1a0
0a 00fffe60 76f47bf4 ffffffff 76f68ff3 00000000 ntdll!__RtlUserThreadStart+0x3adc3
0b 00fffe70 00000000 00911684 01191000 00000000 ntdll!_RtlUserThreadStart+0x1b
```

且先不管这个栈帧是否合理，我看见了一个关键的API——KERNELBASE!UnhandledExceptionFilter，之所以说他关键，是因为他是异常分发中SEH链上的最后”守墓人”；其原型如下：

```
LONG UnhandledExceptionFilter( _EXCEPTION_POINTERS *ExceptionInfo ); 
typedef struct _EXCEPTION_POINTERS
`{` 
    PEXCEPTION_RECORD ExceptionRecord; 
    PCONTEXT ContextRecord; 
`}` EXCEPTION_POINTERS, *PEXCEPTION_POINTERS;

https://docs.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-unhandledexceptionfilter
```

好，那我们就来看下这里边的数据，如下：

```
0:000:x86&gt; dt _EXCEPTION_POINTERS 00fff62c
msvcr100!_EXCEPTION_POINTERS
   +0x000 ExceptionRecord  : 0x00fff768 _EXCEPTION_RECORD
   +0x004 ContextRecord    : 0x00fff7b8 _CONTEXT
0:000:x86&gt; dt _EXCEPTION_RECORD  0x00fff768
msvcr100!_EXCEPTION_RECORD
   +0x000 ExceptionCode    : 0xe06d7363
   +0x004 ExceptionFlags   : 1
   +0x008 ExceptionRecord  : (null)
   +0x00c ExceptionAddress : 0x765b4402 Void
   +0x010 NumberParameters : 3
   +0x014 ExceptionInformation : [15] 0x19930520
0:000:x86&gt; dt _CONTEXT 0x00fff7b8
msvcr100!_CONTEXT
   +0x000 ContextFlags     : 0x1007f
   +0x004 Dr0              : 0
   +0x008 Dr1              : 0
   +0x00c Dr2              : 0
   +0x010 Dr3              : 0
   +0x014 Dr6              : 0
   +0x018 Dr7              : 0
   +0x01c FloatSave        : _FLOATING_SAVE_AREA
   +0x08c SegGs            : 0x2b
   +0x090 SegFs            : 0x53
   +0x094 SegEs            : 0x2b
   +0x098 SegDs            : 0x2b
   +0x09c Edi              : 0x9133d4
   +0x0a0 Esi              : 1
   +0x0a4 Ebx              : 0
   +0x0a8 Edx              : 0
   +0x0ac Ecx              : 3
   +0x0b0 Eax              : 0xfffc98
   +0x0b4 Ebp              : 0xfffcf0
   +0x0b8 Eip              : 0x765b4402
   +0x0bc SegCs            : 0x23
   +0x0c0 EFlags           : 0x212
   +0x0c4 Esp              : 0xfffc98
   +0x0c8 SegSs            : 0x2b
   +0x0cc ExtendedRegisters : [512]
```

数据看上去一切都正常，此时大家伙都知道了，该用.ecxr命令了。其实这里有个很方便的命令，它可以直接处理_EXCEPTION_POINTERS *，一步到位，用法如下：

```
0:000:x86&gt; .exptr 00fff62c
----- Exception record at 00fff768:
ExceptionAddress: 765b4402 (KERNELBASE!RaiseException+0x00000062)
   ExceptionCode: e06d7363 (C++ EH exception)
  ExceptionFlags: 00000001
NumberParameters: 3
   Parameter[0]: 19930520
   Parameter[1]: 00fffd38
   Parameter[2]: 00912400
  pExceptionObject: 00fffd38
  _s_ThrowInfo    : 00912400
  Type            : class MyException
  Type            : class MyBaseException
----- Context record at 00fff7b8:
eax=00fffc98 ebx=00000000 ecx=00000003 edx=00000000 esi=00000001 edi=009133d4
eip=765b4402 esp=00fffc98 ebp=00fffcf0 iopl=0         nv up ei pl nz ac po nc
cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000212
KERNELBASE!RaiseException+0x62:
765b4402 8b4c2454        mov     ecx,dword ptr [esp+54h] ss:002b:00fffcec=255e6225
```

注意看，它在ExceptionCode后边直接提示了这是个“C++ EH exception”，它是怎么知道的？在回答这个问题前，先来看一下e06d7363这个数字的特性：

```
0:000:x86&gt; .formats e06d7363
Evaluate expression:
  Hex:     e06d7363
  Decimal: -529697949
  Octal:   34033271543
  Binary:  11100000 01101101 01110011 01100011
  Chars:   .msc
  Time:    ***** Invalid
  Float:   low -6.84405e+019 high 0
  Double:  1.86029e-314
```

哦，原来他的字符解释是”.msc”，Windbg就是借此判断它是C++异常的，如果此还不足以说明问题，后边我们还会看到最本质的；此时你应该有很多疑问，比如_s_ThrowInfo是什么？为什么会出现”class MyException”和”class MyBaseException”字符串？别急，下边我们一步一步的揭开这些谜团。源码中throw在被编译器处理过会是下边这个样子：

```
;throw MyException("exception_demo",1,2,3);
... 省略  
00911078 6800249100      push    offset test+0x2400 (00912400)
0091107d 8d4588          lea     eax,[ebp-78h]                 //这个是MyException栈对象的地址
00911080 50              push    eax
00911081 c7458c01000000  mov     dword ptr [ebp-74h],1
00911088 c7459002000000  mov     dword ptr [ebp-70h],2
0091108f c7459403000000  mov     dword ptr [ebp-6Ch],3
00911096 e8050c0000      call    test+0x1ca0 (00911ca0)        //根据
```

栈回溯可知,这个是CxxThrowException()

出现了一个非常关键的调用，CxxThrowException()，且这个函数有两个参数；依照目前的证据的话，我们有理由推测throw被编译器处理过后便是调用的CxxThrowException()。那这个函数的原型甚至源码是啥样的呢？如下：

```
0:000:x86&gt; uf _CxxThrowException
715e86e8 8bff            mov     edi,edi
715e86ea 55              push    ebp
715e86eb 8bec            mov     ebp,esp
715e86ed 83ec20          sub     esp,20h
715e86f0 8b4508          mov     eax,dword ptr [ebp+8]                   ;arg1
715e86f3 56              push    esi
715e86f4 57              push    edi
715e86f5 6a08            push    8
715e86f7 59              pop     ecx
715e86f8 be34875e71      mov     esi,offset msvcr100!ExceptionTemplate (715e8734) ;下边有dmp出这块内存的数据
715e86fd 8d7de0          lea     edi,[ebp-20h]
715e8700 f3a5            rep movs dword ptr es:[edi],dword ptr [esi]    ;从ExceptionTemplate中拷贝8*4=0x20字节的数据
715e8702 8945f8          mov     dword ptr [ebp-8],eax                  ;用arg1替代从ExceptionTemplate中拷贝过来的对应偏移的数据
715e8705 8b450c          mov     eax,dword ptr [ebp+0Ch]                ;arg2
715e8708 5f              pop     edi
715e8709 8945fc          mov     dword ptr [ebp-4],eax                  ;用arg2替代从ExceptionTemplate中拷贝过来的对应偏移的数据
715e870c 5e              pop     esi
715e870d 85c0            test    eax,eax
715e870f 7409            je      msvcr100!_CxxThrowException+0x35 (715e871a)
715e8711 f60008          test    byte ptr [eax],8
715e8714 0f856a440100    jne     msvcr100!_CxxThrowException+0x2e (715fcb84)
715e871a 8d45f4          lea     eax,[ebp-0Ch]
715e871d 50              push    eax                                    ;lpArguments
715e871e ff75f0          push    dword ptr [ebp-10h]                    ;nNumberOfArguments
715e8721 ff75e4          push    dword ptr [ebp-1Ch]                    ;dwExceptionFlags
715e8724 ff75e0          push    dword ptr [ebp-20h]                    ;dwExceptionCode
715e8727 ff1508105c71    call    dword ptr [msvcr100!_imp__RaiseException (715c1008)]
715e872d c9              leave
715e872e c20800          ret     8

715fcb84 c745f400409901  mov     dword ptr [ebp-0Ch],1994000h
715fcb8b e98abbfeff      jmp     msvcr100!_CxxThrowException+0x35 (715e871a)

0:000:x86&gt; dd 715e8734 l8
715e8734  e06d7363 00000001 00000000 00000000
715e8744  00000003 19930520 00000000 00000000
```

根据”call dword ptr [msvcr100!_imp__RaiseException (715c1008)]”这行调用，我们可以推测出来ExceptionTemplate这个未知结构体的大致字段如下：

```
struct ExceptionTemplate
`{`
    DWORD dwExceptionCode            ;e06d7363 ---- .msc
    DWORD dwExceptionFlags           ;00000001
    DWORD xxxx_0                     ;00000000
    DWORD xxxx_0                     ;00000000
    DWORD nNumberOfArguments         ;00000003
    DWORD lpArguments[3]             ;19930520 00000000 00000000
`}`
```

综合上边的分析我们可得如下的C代码：

```
arg1为throw后边的异常对象的地址----这个可直接从上边的函数调用中推测出来；
arg2为_s_ThrowInfo对象的地址----这个是从.exptr给出的结论中推测出来的；

_CxxThrowException(ExceptionObject *arg1,s_ThrowInfo *arg2)
`{`   
    struct ExceptionTemplate temp = msvcr100!ExceptionTemplate;
    temp.lpArguments[1] = arg1;
    temp.lpArguments[2] = arg2;
    if(*(DWORD*)arg2 &amp; 8)
    `{`
         temp.lpArguments[0]=0x1994000
    `}`
    return RaiseException(temp.dwExceptionCode, temp.dwExceptionFlags,temp.nNumberOfArguments,temp. lpArguments);
`}`
```

我们来简单看下这个异常对象是不是我们throw出的那个，

```
0:000:x86&gt; dd 00fffd38
00fffd38  00912150 00000001 00000002 00000003
00fffd48  65637865 6f697470 65645f6e 00006f6d
00fffd58  00000000

0:000:x86&gt; da 00fffd48
00fffd48  "exception_demo"

0:000:x86&gt; dps 00912150
00912150  00911000 test+0x1000
00912154  00911010 test+0x1010
00912158  00911020 test+0x1020
0091215c  00000000
```

数据分别是我们传入的1,2,3和 “exception_demo”，另外虚表也是对得上的。我这里没有生成pdb，生成了的话，这里是直接可以看到符号解析之后的名字的，当然没有也是分析各种dmp时常遇到的情况。再来分分析下这个s_ThrowInfo为何方神圣。

```
0:000:x86&gt; dt _s_ThrowInfo 00912400
msvcr100!_s_ThrowInfo
   +0x000 attributes       : 0
   +0x004 pmfnUnwind       : (null)
   +0x008 pForwardCompat   : (null)
   +0x00c pCatchableTypeArray : 0x009123f4 _s_CatchableTypeArray
0:000:x86&gt; dt _s_CatchableTypeArray 0x009123f4
msvcr100!_s_CatchableTypeArray
   +0x000 nCatchableTypes  : 0n2
   +0x004 arrayOfCatchableTypes : [0] 0x009123bc _s_CatchableType
0:000:x86&gt; dd 0x009123f4 l3
009123f4  00000002 009123bc 009123d8
0:000:x86&gt; dt 0x009123bc _s_CatchableType
msvcr100!_s_CatchableType
   +0x000 properties       : 0
   +0x004 pType            : 0x00913038 TypeDescriptor
   +0x008 thisDisplacement : PMD
   +0x014 sizeOrOffset     : 0n116
   +0x018 copyFunction     : 0x009110a0     void  +0
0:000:x86&gt; dt 0x00913038 _TypeDescriptor
msvcr100!_TypeDescriptor
   +0x000 pVFTable         : 0x00912120 Void
   +0x004 spare            : (null)
   +0x008 name             : [0]  ".?AVMyException@@"
0:000:x86&gt; dt 009123d8 _s_CatchableType
msvcr100!_s_CatchableType
   +0x000 properties       : 0
   +0x004 pType            : 0x00913054 TypeDescriptor
   +0x008 thisDisplacement : PMD
   +0x014 sizeOrOffset     : 0n1
   +0x018 copyFunction     : (null)
0:000:x86&gt; dt 0x00913054 _TypeDescriptor
msvcr100!_TypeDescriptor
   +0x000 pVFTable         : 0x00912120 Void
   +0x004 spare            : (null)
   +0x008 name             : [0]  ".?AVMyBaseException@@"
第一处的copyFunction后边有个地址，我看反汇编看一下里边的内容：
0:000:x86&gt; u 009110a0 l20
test+0x10a0:
009110a0 55              push    ebp
009110a1 8bec            mov     ebp,esp
009110a3 8bc1            mov     eax,ecx
009110a5 8b4d08          mov     ecx,dword ptr [ebp+8]                        
009110a8 c70050219100    mov     dword ptr [eax],offset test+0x2150 (00912150)
009110ae 8b5104          mov     edx,dword ptr [ecx+4]
009110b1 56              push    esi
009110b2 895004          mov     dword ptr [eax+4],edx
009110b5 8b5108          mov     edx,dword ptr [ecx+8]
009110b8 57              push    edi
009110b9 895008          mov     dword ptr [eax+8],edx
009110bc 8b510c          mov     edx,dword ptr [ecx+0Ch]
009110bf 8d7110          lea     esi,[ecx+10h]
009110c2 8d7810          lea     edi,[eax+10h]
009110c5 b919000000      mov     ecx,19h
009110ca 89500c          mov     dword ptr [eax+0Ch],edx
009110cd f3a5            rep movs dword ptr es:[edi],dword ptr [esi]
009110cf 5f              pop     edi
009110d0 5e              pop     esi
009110d1 5d              pop     ebp
009110d2 c20400          ret     4
```

这个函数是啥？这个函数是MyException类的构造函数；

经过上边分析，我们知道了s_ThrowInfo记录的是类的静态信息，如这个类的名字，继承的父类是谁，其构造函数做了什么事情等等信息；这个有啥用呢？这个在做dmp分析时，光有一个ExceptionObject是没太大意义的，因为做分析或者做逆向最大的工作就是分析出字段名字、作用；所以如果能够记录下该ExceptionObject所对应的类型，那对应分析crash就非常有帮助了；



## 3、被Windbg隐藏的意外惊喜

难道每次分析dmp时，都要做手动解析吗？都要先找到UnhandledExceptionFilter,然后找到其传入的两个参数，然后才能使用.ecxr来分析吗？当然不是，有些情况你压根就找不到UnhandledExceptionFilter函数，为啥？造成这个问题的情况很多，比如栈回溯失败，故意破坏了栈帧，dmp栈时失败了等等各种问题。那这样的话，又如何分析呢？方法还是有的，因为我们已经逆向分析出了ExceptionTemplate，有了这个，我们就能去找数据；往RaiseException上一级调用回溯下就可以，举例如下：

00 00fffcf0 715e872d e06d7363 00000001 00000003 KERNELBASE!RaiseException+0x62<br>
很多情况下，拿到dmp进行栈回溯，只有一行，这便是栈回溯失败的例子，不要担心，看见e06d7363你就知道这是个C++异常了。简单查看下内存数据就得到ExceptionTemplate了；

```
0:000:x86&gt; dd 00fffcf0
00fffcf0  00fffd28 715e872d e06d7363 00000001
00fffd00  00000003 00fffd1c e06d7363 00000001
00fffd10  00000000 00000000 00000003 19930520
00fffd20  00fffd38 00912400 00fffdb0 0091109b
00fffd30  00fffd38 00912400 00912150 00000001
00fffd40  00000002 00000003 65637865 6f697470
00fffd50  65645f6e 00006f6d 00000000 00fffd88
00fffd60  715dd1af 019d392c 019d3981 00fffd80
```

往高地址找一下e06d7363，找到的便是ExceptionTemplate对象了，然后改怎么分析就怎么分析了；其实这个便是_CxxThrowException()调用RaiseException()在栈上生成的那个临时的ExceptionTemplate对象；每次都一大把dt，还要写上一对压根就不太好记忆的结构体的名字，太麻烦了，Windbg善解人意的一面又显示出来了，提供了一个现成的命令，当然在Windbg的帮助文档里是没有提及这个命令的具体用法的，不过还好，我教你呀；

```
0:000:x86&gt; !cppexr 00fffd08
  pExceptionObject: 00fffd38
  _s_ThrowInfo    : 00912400
  Type            : class MyException
  Type            : class MyBaseException
```

干净利落，给出的信息简明扼要；



## 4、思考题的答案：

这两个命令当然不起作用啦，因为这不是dmp，而是处于调试状态，不像在dmp文件中那样按照指定格式记录了相应的数据，在此时Windbg找不到相应的数据，所以就失效了；
