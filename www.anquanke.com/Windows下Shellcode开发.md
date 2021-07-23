> 原文链接: https://www.anquanke.com//post/id/222280 


# Windows下Shellcode开发


                                阅读量   
                                **216330**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t016964a934e99510b9.jpg)](https://p3.ssl.qhimg.com/t016964a934e99510b9.jpg)

> 平台

**vc6.0 vs2005 vs2008 vs2010 vs2012 vs2013 vs2015 vs2017**

> 创建

**Win32程序控制台**

## 一、shellcode编写原则

### <a class="reference-link" name="1.%E4%BF%AE%E6%94%B9%E7%A8%8B%E5%BA%8F%E5%85%A5%E5%8F%A3"></a>1.修改程序入口

编译时编译器会自动生成的代码，对编写shellcode产生干扰，所以需要清除
<li>
**1.** 修改程序入口点（VS位例子）程序员源代码如下：
<pre><code class="lang-cpp hljs">#include &lt;windows.h&gt;
#pragma comment(linker, "/ENTRY:EntryMain")
int EntryMain()
`{`
    return 0;
`}`
</code></pre>
</li>
在**Release**模式下
- **工程属性(右键项目)-&gt;配置属性-&gt;链接器-&gt;高级-&gt;入口点 处设置入口函数名称**
<li>添加如下代码
<pre><code class="lang-cpp hljs">#pragma comment(linker, "/ENTRY:EntryName")
</code></pre>
在**Debug**模式下几乎不可能改变，因为MSVCRT.lib中某些对象文件的唯一链接器引用。链接器定义的实际入口点名称不是main，而是mainCRTStartup。不过方法如下，**缺点就是要保留main函数**，这样就无法达到自定义程序入口的目的
</li>
<li>
**工程属性(右键项目)-&gt;配置属性-&gt;链接器-&gt;高级-&gt;入口点** 处设置入口函数名称，然后在 **工程属性(右键项目)-&gt;配置属性-&gt;链接器-&gt;输入-&gt;强制符号引用** 将值设置为：`_mainCRTStartup`（x86）或 `mainCRTStartup`（x64）</li>
<li>也可以添加如下代码
<pre><code class="lang-cpp hljs">#pragma comment(linker, "/ENTRY:wmainCRTStartup ") // wmain will be called
#pragma comment(linker, "/ENTRY:mainCRTStartup  ") // main will be called
</code></pre>
但是这样只能调用`wmain`和`main`
这样ida反汇编：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0176d259a9857d4d7d.png)
</li><li>
**2.**关闭缓冲区安全检查（GS检查）**依旧是在release下进行****工程属性(右键项目) -&gt;c/c++-&gt;代码生成-&gt;安全检查，设置为禁用安全检查**[![](https://p2.ssl.qhimg.com/t0132d739c1b1931f4d.png)](https://p2.ssl.qhimg.com/t0132d739c1b1931f4d.png)这个时候就只有一个函数了
</li>
这样将shellcode写入到函数中就不会因为其他函数造成干扰

### ~~2.设置工程兼容WindowsXP~~

我也很想设置好这个但是：配置完了过后，再切换到原来的工具集将丢失头文件的路径，要重新导入，修复的话很麻烦，尽量不要选择这个
<li>在visual studio installer 里面添加对 c++的WindowsXP支持[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014085b6030de788ab.png)
</li>
<li>
**工程属性(右键项目) -&gt;常规-&gt;平台工具集-&gt;设置为含有当前vs年份+WindowsXP**，如：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01407823d306a5dde3.png)
</li>
<li>
**工程属性(右键项目) -&gt;c/c++-&gt;代码生成-&gt;运行库：多线程调试MTD(Debug) 或 MT(Release)**这样就能保证程序能在windowsxp下运行</li>
### <a class="reference-link" name="3.%E5%85%B3%E9%97%AD%E7%94%9F%E6%88%90%E6%B8%85%E5%8D%95"></a>3.关闭生成清单

程序使用PEid之类的工具的话会发现EP段有三个段

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0170de93ccd5564e7f.png)

理想情况下应该只保留代码段，这样便于直接提取代码段得到shellcode，其中.rsrc就是vs默认的生成清单段

清楚过程如下：

**工程属性(右键项目) -&gt;链接器-&gt;清单文件-&gt;生成清单：否**

[![](https://p2.ssl.qhimg.com/t01c4c87287e20b9e43.png)](https://p2.ssl.qhimg.com/t01c4c87287e20b9e43.png)

### <a class="reference-link" name="4.%E5%87%BD%E6%95%B0%E5%8A%A8%E6%80%81%E8%B0%83%E7%94%A8"></a>4.函数动态调用

> 这里以弹出MessageBox位例子

```
#pragma comment(linker, "/ENTRY:EntryName")//手动设置了入口点就不需要加这句 
#include &lt;windows.h&gt;

int EntryName()
`{`
    MessageBox(NULL, NULL, NULL, NULL);
    return 0;
`}`
```

编译前执行操作 **工程属性(右键项目) -&gt;C/C++-&gt;语言-&gt;符合模式：否**

对CTF中二进制的朋友应该明白：类似在Linux上的`plt`和`got`的转换，在windows下，函数调用是通过`user32.dll`或者`kernel32.dll`来实现的，中间存在一个寻找地址的操作，而这个操作又是通过编译器实现的，这样程序员只需要记住名字就可以调用库中的函数了。

在ida中通过汇编就可以说明这一点：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c85e0292e353a22f.png)

但是shellcode的编写选用调用函数的话，就必须知道相对偏移才能正确获得函数的内存地址，所以shellcode要杜绝绝对地址的直接调用，如将上面的程序变为shellcode时，在汇编中直接`call call dword ptr ds:[0x00E02000]`(x32dbg调试中的语句)**是要避免的**，所以函数要先获得的动态地址，然后再调用。

**GetProcAddress函数**

[官方文档](https://docs.microsoft.com/en-us/cpp/build/getprocaddress?view=msvc-160)

作用：在指定动态连接库中获得指定的要导出函数地址

实例：

```
#pragma comment(linker, "/ENTRY:EntryName") 
#include &lt;windows.h&gt;

int EntryName()
`{`
    //MessageBox(NULL, NULL, NULL, NULL);
    GetProcAddress(LoadLibraryA("user32.dll"), "MessageBoxA");
    return 0;
`}`
```

之前的程序经过调试，确定`MessageBox`是在`user32.dll`中，所以在第一个参数加载`user32.dll`，第二个参数填写函数名称，但是`MessageBox`有两种重载`MessageBoxA`（Ascii）和`MessageBoxW`（Wchar?），这里选择Ascii的版本(`MessageBoxA`)

dll导出表也可以使用**PEid**查看

在 **子系统-&gt;输出表** 中

[![](https://p4.ssl.qhimg.com/t015a81be73f5d21298.png)](https://p4.ssl.qhimg.com/t015a81be73f5d21298.png)

那么可以通过内嵌汇编来调用函数

```
#pragma comment(linker, "/ENTRY:EntryName") 
#include &lt;windows.h&gt;

int EntryName()
`{`
    //MessageBox(NULL, NULL, NULL, NULL);
    LPVOID lp = GetProcAddress(LoadLibraryA("user32.dll"), "MessageBoxA");
    char *ptrData = "Hello Shellcode";
    __asm
    `{`
        push 0
        push 0
        mov ebx,ptrData
        push ebx
        push 0
        mov eax,lp
        call eax
    `}`
    return 0;
`}`
```

这样提取出来的shellcode就不含编译器参杂的动态调用偏移

现在规范化

可以将鼠标移到函数上，ctrl+鼠标左键进入函数定义，然后自定义一个函数指针，格式如下：

```
int EntryName()
`{`    
    typedef HANDLE (WINAPI *FN_CreateFileA)
        (
            __in     LPCSTR lpFileName,
            __in     DWORD dwDesiredAccess,
            __in     DWORD dwShareMode,
            __in_opt LPSECURITY_ATTRIBUTES lpSecurityAttributes,
            __in     DWORD dwCreationDisposition,
            __in     DWORD dwFlagsAndAttributes,
            __in_opt HANDLE hTemplateFile
        );
    FN_CreateFileA fn_CreateFileA;
    fn_CreateFileA = (FN_CreateFileA)GetProcAddress(LoadLibraryA("kernel32.dll"), "CreateFileA");
    fn_CreateFileA("Shellcode.txt", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 0, NULL);

    return 0;
`}`
```

同理也可以这样设置`printf`

```
typedef  int (__CRTDECL *FN_printf)
        (char const* const _Format, ...);
    FN_printf fn_printf;
    fn_printf = (FN_printf)GetProcAddress(LoadLibraryA("msvcrt.dll"), "printf");
    fn_printf("%s\n", "hello shellcode");
```

我们在编写shellcode使用`GetProcAddress`和`LoadLibraryA`两个函数时，怎么找到这两个函数的地址呢？

### 5.获得`GetProcAddress`地址和`LoadLibraryA("kerner32.dll")`结果

**获得`LoadLibraryA("kerner32.dll")`结果**

**PEB**

进程环境信息块，全称：Process Envirorment Block Structure。MSDN:[https://docs.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb，包含了一写进程的信息。](https://docs.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb%EF%BC%8C%E5%8C%85%E5%90%AB%E4%BA%86%E4%B8%80%E5%86%99%E8%BF%9B%E7%A8%8B%E7%9A%84%E4%BF%A1%E6%81%AF%E3%80%82)

```
typedef struct _PEB `{`
  BYTE                          Reserved1[2];    /*0x00*/
  BYTE                          BeingDebugged;    /*0x02*/
  BYTE                          Reserved2[1];    /*0x03*/
  PVOID                         Reserved3[2];    /*0x04*/
  PPEB_LDR_DATA                 Ldr;            /*0x0c*/
  PRTL_USER_PROCESS_PARAMETERS  ProcessParameters;
  PVOID                         Reserved4[3];
  PVOID                         AtlThunkSListPtr;
  PVOID                         Reserved5;
  ULONG                         Reserved6;
  PVOID                         Reserved7;
  ULONG                         Reserved8;
  ULONG                         AtlThunkSListPtr32;
  PVOID                         Reserved9[45];
  BYTE                          Reserved10[96];
  PPS_POST_PROCESS_INIT_ROUTINE PostProcessInitRoutine;
  BYTE                          Reserved11[128];
  PVOID                         Reserved12[1];
  ULONG                         SessionId;
`}` PEB, *PPEB;
```

**fs寄存器**

在80386及之后的处理器 又增加了两个寄存器 **FS 寄存器**和 GS寄存器

其中FS寄存器的作用是：

|偏移|说明
|------
|000|指向SEH链指针
|004|线程堆栈顶部
|008|线程堆栈底部
|00C|SubSystemTib
|010|FiberData
|014|ArbitraryUserPointer
|018|FS段寄存器在内存中的镜像地址
|020|进程PID
|024|线程ID
|02C|指向线程局部存储指针
|030|PEB结构地址（进程结构）
|034|上个错误号

所以获得fs:[0x30]就可以获得PEB的信息

得到PEB信息后，在使用**PEB-&gt;Ldr**来获取其他信息

**PEB-&gt;Ldr**

msdn：[https://docs.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb_ldr_data](https://docs.microsoft.com/en-us/windows/win32/api/winternl/ns-winternl-peb_ldr_data)

```
typedef struct _PEB_LDR_DATA `{`
  BYTE       Reserved1[8];    /*0x00*/
  PVOID      Reserved2[3];    /*0x08*/
  LIST_ENTRY InMemoryOrderModuleList;    /*0x14*/
`}` PEB_LDR_DATA, *PPEB_LDR_DATA;
```

注意**InMemoryOrderModuleList**

> The head of a doubly-linked list that contains the loaded modules for the process. Each item in the list is a pointer to an **LDR_DATA_TABLE_ENTRY** structure. For more information, see Remarks.

双向链接列表的头部，该列表包含该进程已加载的模块。列表中的每个项目都是指向**LDR_DATA_TABLE_ENTRY**结构的指针。有关更多信息，请参见备注。

备注

```
/*LIST_ENTRY*/
typedef struct _LIST_ENTRY `{`
   struct _LIST_ENTRY *Flink;
   struct _LIST_ENTRY *Blink;
`}` LIST_ENTRY, *PLIST_ENTRY, *RESTRICTED_POINTER PRLIST_ENTRY;

/*LDR_DATA_TABLE_ENTRY*/
typedef struct _LDR_DATA_TABLE_ENTRY `{`
    PVOID Reserved1[2];                /*0x00*/
    LIST_ENTRY InMemoryOrderLinks;    /*0x08*/
    PVOID Reserved2[2];                /*0x10*/
    PVOID DllBase;                    /*0x14*/
    PVOID EntryPoint;
    PVOID Reserved3;
    UNICODE_STRING FullDllName;
    BYTE Reserved4[8];
    PVOID Reserved5[3];
    union `{`
        ULONG CheckSum;
        PVOID Reserved6;
    `}`;
    ULONG TimeDateStamp;
`}` LDR_DATA_TABLE_ENTRY, *PLDR_DATA_TABLE_ENTRY;
```

**_LDR_DATA_TABLE_ENTRY**中我们就可以得到DLL文件的基址（DllBase），从而得到偏移。

那么以上代码可为

```
xor eax,eax            ;清空eax
mov eax,fs:[0x30]    ;eax = PEB
mov eax,[eax+0xc]    ;eax = PEB-&gt;Ldr
;一个BYTE：1字节，一个PVOID：4字节
;所以Ldr的偏移位=2*1+1+1+2*4=12=0xc
mov eax,[eax+0x14]    ;eax = PEB-&gt;Ldr.InMemoryOrderModuleList
mov eax,[eax]        ;·struct _LIST_ENTRY *Flink;·访问的
;将eax=下一个模块的地址，从而切换模块
;1. .exe程序 -&gt; 2.ntdll.dlls
mov eax,[eax]        ;2.ntdll.dll-&gt;3.kernel32.dll
mov eax,[eax+0x10]    ;kernel32.dll-&gt;DllBase
ret                    ;返回eax寄存器
```

到这里我们就可以成功获得DLL文件的基址，也就是实现了**获得`LoadLibraryA("kerner32.dll")`结果**

**获得`GetProcAddress`地址**

**预备知识**

这里简单说下PE文件头，msdn：[https://docs.microsoft.com/en-us/windows/win32/debug/pe-format](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format)

```
typedef struct IMAGE_DOS_HEADER`{`
      WORD e_magic;            //DOS头的标识，为4Dh和5Ah。分别为字母MZ
      WORD e_cblp;
      WORD e_cp;
      WORD e_crlc;
      WORD e_cparhdr;
      WORD e_minalloc;
      WORD e_maxalloc;
      WORD e_ss;
      WORD e_sp;
      WORD e_csum;
      WORD e_ip;
      WORD e_cs;
      WORD e_lfarlc;
      WORD e_ovno;
      WORD e_res[4];
      WORD e_oemid;
      WORD e_oeminfo;
      WORD e_res2[10];
      DWORD e_lfanew;             //指向IMAGE_NT_HEADERS的所在
`}`IMAGE_DOS_HEADER, *PIMAGE_DOS_HEADER;
```

其中**e_lfanew**指向**IMAGE_NT_HEADERS**的所在

**IMAGE_NT_HEADERS**

分为32位和64位两个版本，这里讲32位，[https://docs.microsoft.com/zh-cn/windows/win32/api/winnt/ns-winnt-image_nt_headers32](https://docs.microsoft.com/zh-cn/windows/win32/api/winnt/ns-winnt-image_nt_headers32)

```
typedef struct _IMAGE_NT_HEADERS `{`
  DWORD                   Signature;
  IMAGE_FILE_HEADER       FileHeader;
  IMAGE_OPTIONAL_HEADER32 OptionalHeader;
`}` IMAGE_NT_HEADERS32, *PIMAGE_NT_HEADERS32;
```
- Signature四字节大小的签名去定义PE文件，标志为：”PE\x00\x00”
- FileHeaderIMAGE_FILE_HEADER结构体来说e明文件头
- OptionalHeader文件的可选头
这里用的到的是**OptionalHeader**，因为它定义了很多程序的基础数据

```
typedef struct _IMAGE_OPTIONAL_HEADER `{`
  WORD                 Magic;
  BYTE                 MajorLinkerVersion;
  BYTE                 MinorLinkerVersion;
  DWORD                SizeOfCode;
  DWORD                SizeOfInitializedData;
  DWORD                SizeOfUninitializedData;
  DWORD                AddressOfEntryPoint;
  DWORD                BaseOfCode;
  DWORD                BaseOfData;
  DWORD                ImageBase;
  DWORD                SectionAlignment;
  DWORD                FileAlignment;
  WORD                 MajorOperatingSystemVersion;
  WORD                 MinorOperatingSystemVersion;
  WORD                 MajorImageVersion;
  WORD                 MinorImageVersion;
  WORD                 MajorSubsystemVersion;
  WORD                 MinorSubsystemVersion;
  DWORD                Win32VersionValue;
  DWORD                SizeOfImage;
  DWORD                SizeOfHeaders;
  DWORD                CheckSum;
  WORD                 Subsystem;
  WORD                 DllCharacteristics;
  DWORD                SizeOfStackReserve;
  DWORD                SizeOfStackCommit;
  DWORD                SizeOfHeapReserve;
  DWORD                SizeOfHeapCommit;
  DWORD                LoaderFlags;
  DWORD                NumberOfRvaAndSizes;
  IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
`}` IMAGE_OPTIONAL_HEADER32, *PIMAGE_OPTIONAL_HEADER32;
```

其中用得到的是：DataDirectory

> <pre><code class="hljs nginx">DataDirectory
</code></pre>
A pointer to the first [IMAGE_DATA_DIRECTORY](https://docs.microsoft.com/en-us/windows/desktop/api/winnt/ns-winnt-image_data_directory) structure in the data directory.
The index number of the desired directory entry. This parameter can be one of the following values.

通过这个成员我们可以查看一些结构体的偏移和大小，其中**IMAGE_DATA_DIRECTORY**如下

```
typedef struct _IMAGE_DATA_DIRECTORY `{`
  DWORD VirtualAddress;
  DWORD Size;
`}` IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
```

如：**IMAGE_DIRECTORY_ENTRY_EXPORT**，这是一个PE文件的导出表，里面记录了加载函数的信息，内容大致如下

[![](https://p5.ssl.qhimg.com/t01febe8588309d59ec.png)](https://p5.ssl.qhimg.com/t01febe8588309d59ec.png)

之后找到这个：**_IMAGE_EXPORT_DIRECTORY**

```
typedef struct _IMAGE_EXPORT_DIRECTORY `{`
    DWORD   Characteristics;
    DWORD   TimeDateStamp;
    WORD    MajorVersion;
    WORD    MinorVersion;
    DWORD   Name;
    DWORD   Base;
    DWORD   NumberOfFunctions;
    DWORD   NumberOfNames;
    DWORD   AddressOfFunctions;     // RVA from base of image
    DWORD   AddressOfNames;         // RVA from base of image
    DWORD   AddressOfNameOrdinals;  // RVA from base of image
`}` IMAGE_EXPORT_DIRECTORY, *PIMAGE_EXPORT_DIRECTORY;
```

就可以用`AddressOfFunctions` `AddressOfNames` `AddressOfNameOrdinals`来找到函数了

**通过基址找到`GetProcAddress`**

```
FARPROC _GetProcAddress(HMODULE hMouduleBase)
`{`
    //由之前找到的DllBase来得到DOS头的地址
    PIMAGE_DOS_HEADER lpDosHeader = 
        (PIMAGE_DOS_HEADER)hMouduleBase;

    //找到 IMAGE_NT_HEADERS 的所在
    PIMAGE_NT_HEADERS32 lpNtHeader = 
        (PIMAGE_NT_HEADERS)((DWORD)hMouduleBase + lpDosHeader-&gt;e_lfanew);

    if (!lpNtHeader-&gt;OptionalHeader//检查可选文件头的导出表大小是否 不为空
            .DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].Size)
    `{`
        return NULL;
    `}`
    if (!lpNtHeader-&gt;OptionalHeader//检查可选文件头的导出表的偏移是否 不为空
            .DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress)
    `{`
        return NULL;
    `}`


    PIMAGE_EXPORT_DIRECTORY lpExport = //获得_IMAGE_EXPORT_DIRECTORY对象
        (PIMAGE_EXPORT_DIRECTORY)((DWORD)hMouduleBase + (DWORD)lpNtHeader-&gt;OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);

    //下面变量均是RVA,要加上hModuleBase这个基址
    PDWORD lpdwFunName =
        (PDWORD)((DWORD)hMouduleBase + (DWORD)lpExport-&gt;AddressOfNames);
    PWORD lpword =
        (PWORD)((DWORD)hMouduleBase + (DWORD)lpExport-&gt;AddressOfNameOrdinals);
    PDWORD lpdwFunAddr =
        (PDWORD)((DWORD)hMouduleBase + (DWORD)lpExport-&gt;AddressOfFunctions);
    //DWORD   AddressOfFunctions;      指向输出函数地址的RVA
    //DWORD   AddressOfNames;          指向输出函数名字的RVA
    //DWORD   AddressOfNameOrdinals;   指向输出函数序号的RVA

    DWORD dwLoop = 0;//遍历查找函数
    FARPROC pRet = NULL;
    for (; dwLoop &lt;= lpExport-&gt;NumberOfNames-1;dwLoop++)
    `{`
        char *pFunName = (char*)(lpdwFunName[dwLoop] + (DWORD)hMouduleBase);//char *pFunName = lpwdFunName[0] = "func1";
        if (pFunName[0] == 'G'&amp;&amp;
            pFunName[1] == 'e'&amp;&amp;
            pFunName[2] == 't'&amp;&amp;
            pFunName[3] == 'P'&amp;&amp;
            pFunName[4] == 'r'&amp;&amp;
            pFunName[5] == 'o'&amp;&amp;
            pFunName[6] == 'c'&amp;&amp;
            pFunName[7] == 'A'&amp;&amp;
            pFunName[8] == 'd'&amp;&amp;
            pFunName[9] == 'd'&amp;&amp;
            pFunName[10] == 'r'&amp;&amp;
            pFunName[11] == 'e'&amp;&amp;
            pFunName[12] == 's'&amp;&amp;
            pFunName[13] == 's')
            //if(strcmp(pFunName,"GetProcAddress"))
        `{`
            pRet = (FARPROC)(lpdwFunAddr[lpword[dwLoop]] + (DWORD)hMouduleBase);
            break;
        `}`
    `}`
    return pRet;
`}`
```

```
;这里原作者是寻找SwapMouseButton函数
;将最后一段汇编参数修改为MessageBoxA的16位小端序
;即可找到MessageBoxA函数的地址
xor ecx, ecx
mov eax, fs:[ecx + 0x30] ; EAX = PEB
mov eax, [eax + 0xc]     ; EAX = PEB-&gt;Ldr
mov esi, [eax + 0x14]    ; ESI = PEB-&gt;Ldr.InMemOrder
lodsd                    ; EAX = Second module
xchg eax, esi            ; EAX = ESI, ESI = EAX
lodsd                    ; EAX = Third(kernel32)
mov ebx, [eax + 0x10]    ; EBX = Base address

mov edx, [ebx + 0x3c]    ; EDX = DOS-&gt;e_lfanew
add edx, ebx             ; EDX = PE Header
mov edx, [edx + 0x78]    ; EDX = Offset export table
add edx, ebx             ; EDX = Export table
mov esi, [edx + 0x20]    ; ESI = Offset namestable
add esi, ebx             ; ESI = Names table
xor ecx, ecx             ; EXC = 0

Get_Function:

inc ecx                              ; Increment the ordinal
lodsd                                ; Get name offset
add eax, ebx                         ; Get function name
cmp dword ptr[eax], 0x50746547       ; GetP
jnz Get_Function
cmp dword ptr[eax + 0x4], 0x41636f72 ; rocA
jnz Get_Function
cmp dword ptr[eax + 0x8], 0x65726464 ; ddre
jnz Get_Function
mov esi, [edx + 0x24]                ; ESI = Offset ordinals
add esi, ebx                         ; ESI = Ordinals table
mov cx, [esi + ecx * 2]              ; Number of function
dec ecx
mov esi, [edx + 0x1c]                ; Offset address table
add esi, ebx                         ; ESI = Address table
mov edx, [esi + ecx * 4]             ; EDX = Pointer(offset)
add edx, ebx                         ; EDX = GetProcAddress

xor ecx, ecx    ; ECX = 0
push ebx        ; Kernel32 base address
push edx        ; GetProcAddress
push ecx        ; 0
push 0x41797261 ; aryA
push 0x7262694c ; Libr
push 0x64616f4c ; Load
push esp        ; "LoadLibrary"
push ebx        ; Kernel32 base address
call edx        ; GetProcAddress(LL)

add esp, 0xc    ; pop "LoadLibrary"
pop ecx         ; ECX = 0
push eax        ; EAX = LoadLibrary
push ecx
mov cx, 0x6c6c  ; ll
push ecx
push 0x642e3233 ; 32.d
push 0x72657375 ; user
push esp        ; "user32.dll"
call eax        ; LoadLibrary("user32.dll")

add esp, 0x10                  ; Clean stack
mov edx, [esp + 0x4]           ; EDX = GetProcAddress
xor ecx, ecx                   ; ECX = 0
push ecx
mov ecx, 0x616E6F74            ; tona
push ecx
sub dword ptr[esp + 0x3], 0x61 ; Remove "a"
push 0x74754265                ; eBut
push 0x73756F4D                ; Mous
push 0x70617753                ; Swap
push esp                       ; "SwapMouseButton"
push eax                       ; user32.dll address
call edx                       ; GetProc(SwapMouseButton)
```

### <a class="reference-link" name="6.%E5%B0%8F%E7%BB%86%E8%8A%82"></a>6.小细节
- 避免全局变量（包括static之类的）的使用这违反了避免对地址直接调用的原则
- 确保API的DLL被加载（显式加载）这个可以在一般情况下写好程序，使用PEid查看输入表，就可以知道在那个DLL调用了那个函数。也可以使用vs的跳转到定义或msdn查询


## 二、整合：shellcode开发框架

### <a class="reference-link" name="0.%E5%88%9B%E5%BB%BA%E7%A8%8B%E5%BA%8F"></a>0.创建程序

新建项目-&gt;控制台应用-&gt;能同时选择控制台应用和空项目最好；不能的话选择控制台应用

编译器选择**release**版本

关闭生成清单：**工程属性(右键项目) -&gt;链接器-&gt;清单文件-&gt;生成清单：否**

关闭缓冲区检查：**工程属性(右键项目) -&gt;c/c++-&gt;代码生成-&gt;安全检查，设置为禁用安全检查**

关闭调试信息：**工程属性(右键项目) -&gt;链接器-&gt;调试-&gt;生成调试信息：否**

设置函数入口：`#pragma comment(linker, "/ENTRY:EntryName")`

### <a class="reference-link" name="1.%E9%9D%99%E6%80%81%E6%B3%A8%E5%85%A5%E6%A1%86%E6%9E%B6"></a>1.静态注入框架

<a class="reference-link" name="1.%E7%BC%96%E5%86%99%E4%BB%A3%E7%A0%81"></a>**1.编写代码**

正常的功能

```
#include &lt;windows.h&gt;
int main()
`{`
    CreateFileA("shellcode.txt", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 0, NULL);
    MessageBoxA(NULL, "Hello shellcode!", "shell", MB_OK);
    return 0;
`}`
```

**实现：**

前面讲过了，shellcode要避免对地址的直接调用，所以我们需要使用`GetProcAddress`和`LoadLibraryA`，所以将之前的getKernel32和getProcAddress导入到程序中

```
DWORD getKernel32();
FARPROC getProcAddress(HMODULE hMouduleBase);
```

<a class="reference-link" name="2.%E5%AE%9E%E7%8E%B0CreateFileA"></a>**2.实现CreateFileA**

对`CreateFileA`实现动态调用，先创建函数指针，然后声明一个对象

```
fn_CreateFileA = (FN_CreateFileA)GetProcAddress(LoadLibraryA("kernel32.dll"), "CreateFileA");
```

声明对象时：1.要调用`GetProcAddress`，2.第一个参数：LoadLibraryA(“kernel32.dll”)，3.第二个参数：”CreateFileA”字符串。

**1。** 使用动态调用`GetProcAddress`

按照之前的方法，代码如下：

```
typedef FARPROC (WINAPI *FN_GetProcAddress)
        (
            _In_ HMODULE hModule,
            _In_ LPCSTR lpProcName
        );
    FN_GetProcAddress fn_GetProcAddress = (FN_GetProcAddress)getProcAddress((HMODULE)getKernel32());
```

动态调用的是自己的函数`getProcAddress`(getProcAddress又是通过getkernel32和**PE文件头**找到的)，这样在`CreateFileA`的动态调用里面的参数就可以填fn_GetProcAddress

**2。**第一个参数：LoadLibraryA(“kernel32.dll”)

直接使用`getkernel32`汇编代码

**3。**第二个参数：”CreateFileA”字符串。

因为直接填写字符串会被编译器认为是静态变量，而我们要避免静态变量，所以要新建变量

```
char szFuncName[] = `{` 'C','r','e','a','t','e','F','i','l','e','A',0 `}`;
```

所以，最后我们的代码是这样的：

```
typedef FARPROC (WINAPI *FN_GetProcAddress)
        (
            _In_ HMODULE hModule,
            _In_ LPCSTR lpProcName
        );
    FN_GetProcAddress fn_GetProcAddress = (FN_GetProcAddress)getProcAddress((HMODULE)getKernel32());

    typedef HANDLE(WINAPI *FN_CreateFileA)
        (
            __in     LPCSTR lpFileName,
            __in     DWORD dwDesiredAccess,
            __in     DWORD dwShareMode,
            __in_opt LPSECURITY_ATTRIBUTES lpSecurityAttributes,
            __in     DWORD dwCreationDisposition,
            __in     DWORD dwFlagsAndAttributes,
            __in_opt HANDLE hTemplateFile
            );

    char szFuncName[] = `{` 'C','r','e','a','t','e','F','i','l','e','A',0 `}`;
    char szNewFile[] = `{` 'S','h','e','l','l','c','o','d','e','.','t','x','t',0`}`;
    FN_CreateFileA fn_CreateFileA = (FN_CreateFileA)fn_GetProcAddress((HMODULE)getKernel32(), szFuncName);
    fn_CreateFileA(szNewFile, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 0, NULL);
```

<a class="reference-link" name="3.%E5%AE%9E%E7%8E%B0MessageBoxA()"></a>**3.实现MessageBoxA()**

和上面CreateFileA实现不同的是，MessageBoxA是位于**User32.dll**中的，所以要动态加载`LoadLibraryA`

```
typedef HMODULE(WINAPI *FN_LoadLibraryA)
        (
            _In_ LPCSTR lpLibFileName
        );
    char szLoadLibrary[]= `{` 'L','o','a','d','L','i','b','r','a','r','y','A' ,0`}`;
    FN_LoadLibraryA fn_LoadLibraryA=(FN_LoadLibraryA)fn_GetProcAddress((HMODULE)getKernel32(),szLoadLibrary);
```

这样`LoadLibraryA`被替换为了`fn_LoadLibraryA`

然后再载入DLL为文件

```
char szUser32[] = `{` 'U','s','e','r','3','2','.','d','l','l' `}`;
    char szMsgBox[] = `{` 'M','e','s','s','a','g','e','B','o','x','A' `}`;
    FN_MessageBoxA fn_MessageBoxA = (FN_MessageBoxA)fn_GetProcAddress((HMODULE)fn_LoadLibraryA(szUser32),szMsgBox);
```

最终的代码如下：

```
//动态加载LoadLibraryA函数
    typedef HMODULE(WINAPI *FN_LoadLibraryA)
        (
            _In_ LPCSTR lpLibFileName
        );
    char szLoadLibrary[]= `{` 'L','o','a','d','L','i','b','r','a','r','y','A' ,0`}`;
    FN_LoadLibraryA fn_LoadLibraryA=(FN_LoadLibraryA)fn_GetProcAddress((HMODULE)getKernel32(),szLoadLibrary);
    //动态加载MessageBoxA函数
    typedef int (WINAPI *FN_MessageBoxA)
        (
            _In_opt_ HWND hWnd,
            _In_opt_ LPCSTR lpText,
            _In_opt_ LPCSTR lpCaption,
            _In_ UINT uType
        );
    char szUser32[] = `{` 'U','s','e','r','3','2','.','d','l','l' `}`;
    char szMsgBox[] = `{` 'M','e','s','s','a','g','e','B','o','x','A' `}`;
    //载入DLL文件
    FN_MessageBoxA fn_MessageBoxA = (FN_MessageBoxA)fn_GetProcAddress((HMODULE)fn_LoadLibraryA(szUser32),szMsgBox);
    //调用函数
    char szMsgBoxContent[] = `{` 'H','e','l','l','o',' ','s','h','e','l','l','c','o','d','e','!' ,0 `}`;
    char szMsgBoxTitle[] = `{` 's','h','e','l','l',0 `}`;
    fn_MessageBoxA(NULL,szMsgBoxContent,szMsgBoxTitle, 0);
```

<a class="reference-link" name="4.%E6%9C%80%E7%BB%88%E7%9A%84%E6%BA%90%E4%BB%A3%E7%A0%81"></a>**4.最终的源代码**

```
#pragma comment(linker, "/ENTRY:MainEntry")
#include &lt;windows.h&gt;

DWORD getKernel32();
FARPROC getProcAddress(HMODULE hMouduleBase);

int MainEntry()
`{`
    //CreateFileA("shellcode.txt", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 0, NULL);
    typedef FARPROC (WINAPI *FN_GetProcAddress)
        (
            _In_ HMODULE hModule,
            _In_ LPCSTR lpProcName
        );
    FN_GetProcAddress fn_GetProcAddress = (FN_GetProcAddress)getProcAddress((HMODULE)getKernel32());

    typedef HANDLE(WINAPI *FN_CreateFileA)
        (
            __in     LPCSTR lpFileName,
            __in     DWORD dwDesiredAccess,
            __in     DWORD dwShareMode,
            __in_opt LPSECURITY_ATTRIBUTES lpSecurityAttributes,
            __in     DWORD dwCreationDisposition,
            __in     DWORD dwFlagsAndAttributes,
            __in_opt HANDLE hTemplateFile
            );

    char szCreateFileA[] = `{` 'C','r','e','a','t','e','F','i','l','e','A',0 `}`;
    char szNewFile[] = `{` 'S','h','e','l','l','c','o','d','e','.','t','x','t',0`}`;
    FN_CreateFileA fn_CreateFileA = (FN_CreateFileA)fn_GetProcAddress((HMODULE)getKernel32(), szCreateFileA);
    fn_CreateFileA(szNewFile, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 0, NULL);

    typedef HMODULE(WINAPI *FN_LoadLibraryA)
        (
            _In_ LPCSTR lpLibFileName
        );
    char szLoadLibrary[]= `{` 'L','o','a','d','L','i','b','r','a','r','y','A' ,0`}`;
    FN_LoadLibraryA fn_LoadLibraryA=(FN_LoadLibraryA)fn_GetProcAddress((HMODULE)getKernel32(),szLoadLibrary);

    typedef int (WINAPI *FN_MessageBoxA)
        (
            _In_opt_ HWND hWnd,
            _In_opt_ LPCSTR lpText,
            _In_opt_ LPCSTR lpCaption,
            _In_ UINT uType
        );
    char szUser32[] = `{` 'U','s','e','r','3','2','.','d','l','l' `}`;
    char szMsgBox[] = `{` 'M','e','s','s','a','g','e','B','o','x','A' `}`;
    FN_MessageBoxA fn_MessageBoxA = (FN_MessageBoxA)fn_GetProcAddress((HMODULE)fn_LoadLibraryA(szUser32),szMsgBox);

    char szMsgBoxContent[] = `{` 'H','e','l','l','o',' ','s','h','e','l','l','c','o','d','e','!' ,0 `}`;
    char szMsgBoxTitle[] = `{` 's','h','e','l','l',0 `}`;
    fn_MessageBoxA(NULL,szMsgBoxContent,szMsgBoxTitle, 0);
    //MessageBoxA(NULL, "Hello shellcode!", "shell", MB_OK);
    return 0;
`}`

__declspec(naked) DWORD getKernel32()
`{`
    __asm
    `{`
        mov eax, fs:[0x30]
        mov eax, [eax + 0xc]
        mov eax, [eax + 0x14]
        mov eax, [eax]
        mov eax, [eax]
        mov eax, [eax + 0x10]
        ret
    `}`
`}`

FARPROC getProcAddress(HMODULE hMouduleBase)
`{`
    //由之前找到的DllBase来得到DOS头的地址
    PIMAGE_DOS_HEADER lpDosHeader =
        (PIMAGE_DOS_HEADER)hMouduleBase;

    //找到 IMAGE_NT_HEADERS 的所在
    PIMAGE_NT_HEADERS32 lpNtHeader =
        (PIMAGE_NT_HEADERS)((DWORD)hMouduleBase + lpDosHeader-&gt;e_lfanew);

    if (!lpNtHeader-&gt;OptionalHeader//检查可选文件头的导出表大小是否 不为空
        .DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].Size)
    `{`
        return NULL;
    `}`
    if (!lpNtHeader-&gt;OptionalHeader//检查可选文件头的导出表的偏移是否 不为空
        .DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress)
    `{`
        return NULL;
    `}`


    PIMAGE_EXPORT_DIRECTORY lpExport = //获得_IMAGE_EXPORT_DIRECTORY对象
        (PIMAGE_EXPORT_DIRECTORY)((DWORD)hMouduleBase + (DWORD)lpNtHeader-&gt;OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);

    //下面变量均是RVA,要加上hModuleBase
    PDWORD lpdwFunName =
        (PDWORD)((DWORD)hMouduleBase + (DWORD)lpExport-&gt;AddressOfNames);
    PWORD lpword =
        (PWORD)((DWORD)hMouduleBase + (DWORD)lpExport-&gt;AddressOfNameOrdinals);
    PDWORD lpdwFunAddr =
        (PDWORD)((DWORD)hMouduleBase + (DWORD)lpExport-&gt;AddressOfFunctions);
    //DWORD   AddressOfFunctions;      指向输出函数地址的RVA
    //DWORD   AddressOfNames;          指向输出函数名字的RVA
    //DWORD   AddressOfNameOrdinals;   指向输出函数序号的RVA

    DWORD dwLoop = 0;//遍历查找函数
    FARPROC pRet = NULL;
    for (; dwLoop &lt;= lpExport-&gt;NumberOfNames - 1; dwLoop++)
    `{`
        char *pFunName = (char*)(lpdwFunName[dwLoop] + (DWORD)hMouduleBase);//char *pFunName = lpwdFunName[0] = "func1";
        if (pFunName[0] == 'G'&amp;&amp;
            pFunName[1] == 'e'&amp;&amp;
            pFunName[2] == 't'&amp;&amp;
            pFunName[3] == 'P'&amp;&amp;
            pFunName[4] == 'r'&amp;&amp;
            pFunName[5] == 'o'&amp;&amp;
            pFunName[6] == 'c'&amp;&amp;
            pFunName[7] == 'A'&amp;&amp;
            pFunName[8] == 'd'&amp;&amp;
            pFunName[9] == 'd'&amp;&amp;
            pFunName[10] == 'r'&amp;&amp;
            pFunName[11] == 'e'&amp;&amp;
            pFunName[12] == 's'&amp;&amp;
            pFunName[13] == 's')
            //if(strcmp(pFunName,"GetProcAddress"))
        `{`
            pRet = (FARPROC)(lpdwFunAddr[lpword[dwLoop]] + (DWORD)hMouduleBase);
            break;
        `}`
    `}`
    return pRet;
`}`
```

<a class="reference-link" name="5.%E6%8F%90%E5%8F%96shellcode%E5%B9%B6%E9%9D%99%E6%80%81%E6%A4%8D%E5%85%A5%EF%BC%88%E7%94%9F%E6%88%90%E6%A1%86%E6%9E%B6%EF%BC%89"></a>**5.提取shellcode并静态植入（生成框架）**

使用PEid来获得程序偏移量，从而得到程序加载到的地方

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cf6eec4fee77d86d.png)

然后使用十六进制编辑器打开编写的程序，这里我用的是HxD，跳转到程序入口，也就是上面的偏移量

[![](https://p3.ssl.qhimg.com/t019926f8cf3909d1f3.png)](https://p3.ssl.qhimg.com/t019926f8cf3909d1f3.png)

这里长度不能太短了，能把要执行的代码包裹完就行，这里选择到0x660的位置。

这样我们就得到了他的二进制代码，即shellcode

然后我们实现静态插入，这里我用PEView来测试

也是使用PEid来获得程序偏移量（0x400），然后在十六进制编辑器中转到，覆盖为我们上面shellcode

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010b4205d601aa61b9.png)

保存后运行：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0137aabf705ae87e0c.png)

这里成功创建了Shellcode.txt文件，然后成功弹出了MessageBox，但是字节填入过多，导致错误的参数被填入，我们这里是对PE文件进行直接覆盖，导致文件偏移计算有问题，最后乱码。

[![](https://p1.ssl.qhimg.com/t01f0300804a4e62384.png)](https://p1.ssl.qhimg.com/t01f0300804a4e62384.png)

### <a class="reference-link" name="2.%E5%88%A9%E7%94%A8%E5%87%BD%E6%95%B0%E5%9C%B0%E5%9D%80%E5%B7%AE%E6%8F%90%E5%8F%96shellcode"></a>2.利用函数地址差提取shellcode

<a class="reference-link" name="1.%E9%A2%84%E5%A4%87%E7%9F%A5%E8%AF%86"></a>**1.预备知识**

**单文件中函数的位置**

这里要明白两种概念，函数定义、函数声明、函数编译的顺序

```
#include &lt;iostream&gt;
int Plus(int , int );//函数声明
int main()
`{`
    std::cout &lt;&lt; "&gt; "&lt;&lt;Plus(1,2)&lt;&lt;std::endl;
`}`

int Plus(int a, int b)//函数定义
`{`
    return a + b;
`}`
```

**函数声明：**把函数的名字、函数类型以及形参类型、个数和顺序通知编译系统，以便在调用该函数时系统按此进行对照检查（例如函数名是否正确，实参与形参的类型和个数是否一致）。

**函数定义：**函数功能的确立，包括指定函数名，函数值类型、形参类型、函数体等，它是一个完整的、独立的函数单位。

**函数编译的顺序**

这个在vs里面关掉优化，代码是如下

```
#include &lt;windows.h&gt;
#include &lt;stdio.h&gt;

int Plus(int , int );
int Div(int, int);

int main()
`{`
    Plus(2, 3);
    Div(2, 3);
    return 0;
`}`

int Div(int a, int b)
`{`
    puts("Divds");
    return a - b;
`}`

int Plus(int a, int b)
`{`
    puts("Plus");
    return a + b;
`}`
```

在IDA中观察，发现函数生成的顺序和声明的顺序不一样，起决定作用的是定义顺序。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016f7d770002a0198f.png)

利用编译顺序，将一直两端函数的地址做差，就能得到两函数之间的代码段的相对位置和程序代码段的大小

**多文件函数生成位置的关系**

项目文件如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b2045705b22ceb13.png)

```
//A.cpp
#include "A.h"
#include &lt;stdio.h&gt;
void FuncA()
`{`
    puts("This Is FuncA");
`}`
```

```
//B.cpp
#include "B.h"
#include &lt;stdio.h&gt;
void FuncB()
`{`
    puts("This Is FuncB");
`}`
```

```
//main.cpp
#include &lt;iostream&gt;
#include "A.h"
#include "B.h"
int main()
`{`
    FuncA();
    FuncB();
`}`
```

在IDA中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c993e1a437fcb11b.png)

发现顺序是FuncA FuncB main，交换调用顺序和include的顺序，发现生成顺序依然没有改变。

其实编译顺序是由编译器的配置文件决定的，文件后缀名为：`.vcxproj`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019ac32cd351d65f6a.png)

修改上面cpp的顺序就修改函数生成顺序了

<a class="reference-link" name="2.%E7%BC%96%E5%86%99%E4%BB%A3%E7%A0%81"></a>**2.编写代码**

还是按照创建程序的步骤建立一个项目，**但是不要关闭调试信息**

在项目里面添加一个 header.h 0.entry.cpp a_start.cpp z_end.cpp，这样文件排序可以很直观的找到代码而且默认的编译顺序是0-9,a-Z

要实现的功能：0.entry.cpp提取shellcode，a_start.cpp z_end.cpp生成shellcode

header.h

```
#pragma once
#ifndef HEAD_H
#define HEAD_H

#include &lt;windows.h&gt;

void ShellcodeStart();
void ShellcodeEntry();
void ShellcodeEnd();
DWORD getKernel32();
FARPROC getProcAddress(HMODULE hMouduleBase);

#endif // !HEAD_D
```

0.entry.cpp

> IO交互部分，不参与shellcode的部分

```
#pragma comment(linker, "/ENTRY:MainEntry")
#include &lt;stdio.h&gt;
#include &lt;Windows.h&gt;
#include "header.h"

void CreateShellcode()//创建文件并写入
`{`
    typedef  int (__CRTDECL *FN_printf)
        (char const* const _Format, ...);
    FN_printf fn_printf;
    fn_printf = (FN_printf)GetProcAddress(LoadLibraryA("msvcrt.dll"), "printf");

    HANDLE hBin = CreateFileA("sh.bin", GENERIC_ALL, 0, NULL, CREATE_ALWAYS, 0, NULL);
    if (hBin == INVALID_HANDLE_VALUE)
    `{`
        fn_printf("Wrong in Generic\n");
        return;
    `}`
    DWORD dwLen = (DWORD)ShellcodeEnd - (DWORD)ShellcodeStart;
    DWORD dwWriter;
    WriteFile(hBin, ShellcodeStart, dwLen, &amp;dwWriter, NULL);
    CloseHandle(hBin);

`}`

int MainEntry()
`{`
    CreateShellcode();
    return 0;
`}`
```

a_start.cpp

> 利用两函数做差就可以得到ShellcodeEnrtry的代码
（ShellcodeStart – ShellcodeEnd = getKernel32+getProcAddress+ShellcodeEntry）
，最后通过0.entry.cpp写入到bin文件

```
#include &lt;windows.h&gt;
#include "header.h"
__declspec(naked) void ShellcodeStart()
`{`
    __asm
    `{`
        jmp ShellcodeEntry
    `}`
`}`

__declspec(naked) DWORD getKernel32()
`{`
    __asm
    `{`
        mov eax, fs:[0x30]
        mov eax, [eax + 0xc]
        mov eax, [eax + 0x14]
        mov eax, [eax]
        mov eax, [eax]
        mov eax, [eax + 0x10]
        ret
    `}`
`}`

FARPROC getProcAddress(HMODULE hMouduleBase)
`{`
    //由之前找到的DllBase来得到DOS头的地址
    PIMAGE_DOS_HEADER lpDosHeader =
        (PIMAGE_DOS_HEADER)hMouduleBase;

    //找到 IMAGE_NT_HEADERS 的所在
    PIMAGE_NT_HEADERS32 lpNtHeader =
        (PIMAGE_NT_HEADERS)((DWORD)hMouduleBase + lpDosHeader-&gt;e_lfanew);

    if (!lpNtHeader-&gt;OptionalHeader//检查可选文件头的导出表大小是否 不为空
        .DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].Size)
    `{`
        return NULL;
    `}`
    if (!lpNtHeader-&gt;OptionalHeader//检查可选文件头的导出表的偏移是否 不为空
        .DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress)
    `{`
        return NULL;
    `}`


    PIMAGE_EXPORT_DIRECTORY lpExport = //获得_IMAGE_EXPORT_DIRECTORY对象
        (PIMAGE_EXPORT_DIRECTORY)((DWORD)hMouduleBase + (DWORD)lpNtHeader-&gt;OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);

    //下面变量均是RVA,要加上hModuleBase
    PDWORD lpdwFunName =
        (PDWORD)((DWORD)hMouduleBase + (DWORD)lpExport-&gt;AddressOfNames);
    PWORD lpword =
        (PWORD)((DWORD)hMouduleBase + (DWORD)lpExport-&gt;AddressOfNameOrdinals);
    PDWORD lpdwFunAddr =
        (PDWORD)((DWORD)hMouduleBase + (DWORD)lpExport-&gt;AddressOfFunctions);
    //DWORD   AddressOfFunctions;      指向输出函数地址的RVA
    //DWORD   AddressOfNames;          指向输出函数名字的RVA
    //DWORD   AddressOfNameOrdinals;   指向输出函数序号的RVA

    DWORD dwLoop = 0;//遍历查找函数
    FARPROC pRet = NULL;
    for (; dwLoop &lt;= lpExport-&gt;NumberOfNames - 1; dwLoop++)
    `{`
        char *pFunName = (char*)(lpdwFunName[dwLoop] + (DWORD)hMouduleBase);//char *pFunName = lpwdFunName[0] = "func1";
        if (pFunName[0] == 'G'&amp;&amp;
            pFunName[1] == 'e'&amp;&amp;
            pFunName[2] == 't'&amp;&amp;
            pFunName[3] == 'P'&amp;&amp;
            pFunName[4] == 'r'&amp;&amp;
            pFunName[5] == 'o'&amp;&amp;
            pFunName[6] == 'c'&amp;&amp;
            pFunName[7] == 'A'&amp;&amp;
            pFunName[8] == 'd'&amp;&amp;
            pFunName[9] == 'd'&amp;&amp;
            pFunName[10] == 'r'&amp;&amp;
            pFunName[11] == 'e'&amp;&amp;
            pFunName[12] == 's'&amp;&amp;
            pFunName[13] == 's')
            //if(strcmp(pFunName,"GetProcAddress"))
        `{`
            pRet = (FARPROC)(lpdwFunAddr[lpword[dwLoop]] + (DWORD)hMouduleBase);
            break;
        `}`
    `}`
    return pRet;
`}`

void ShellcodeEntry()
`{`
    typedef FARPROC(WINAPI *FN_GetProcAddress)
        (
            _In_ HMODULE hModule,
            _In_ LPCSTR lpProcName
            );
    FN_GetProcAddress fn_GetProcAddress = (FN_GetProcAddress)getProcAddress((HMODULE)getKernel32());

    typedef HMODULE(WINAPI *FN_LoadLibraryA)
        (
            _In_ LPCSTR lpLibFileName
            );
    char szLoadLibrary[] = `{` 'L','o','a','d','L','i','b','r','a','r','y','A' ,0 `}`;
    FN_LoadLibraryA fn_LoadLibraryA = (FN_LoadLibraryA)fn_GetProcAddress((HMODULE)getKernel32(), szLoadLibrary);

    typedef int (WINAPI *FN_MessageBoxA)
        (
            _In_opt_ HWND hWnd,
            _In_opt_ LPCSTR lpText,
            _In_opt_ LPCSTR lpCaption,
            _In_ UINT uType
            );
    char szUser32[] = `{` 'U','s','e','r','3','2','.','d','l','l',0 `}`;
    char szMsgBox[] = `{` 'M','e','s','s','a','g','e','B','o','x','A',0 `}`;
    FN_MessageBoxA fn_MessageBoxA = (FN_MessageBoxA)fn_GetProcAddress((HMODULE)fn_LoadLibraryA(szUser32), szMsgBox);

    char szMsgBoxContent[] = `{` 'H','e','l','l','o',0 `}`;
    char szMsgBoxTitle[] = `{` 't','i','t','l','e',0 `}`;
    fn_MessageBoxA(NULL, szMsgBoxContent, szMsgBoxTitle, 0);
    //MessageBoxA(NULL, "Hello", "title", MB_OK);
`}`
```

z_end.cpp

> 标志shellcode的结束

```
#include &lt;windows.h&gt;
#include "header.h"
void ShellcodeEnd()`{``}`
```

<a class="reference-link" name="3.%E6%95%88%E6%9E%9C"></a>**3.效果**

最后生成的bin文件是一串二进制代码，需要shellcode加载器才能运行，接下来就编写shellcode加载器

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018bc9711f9ed888fa.png)

### <a class="reference-link" name="3.%E5%8A%A0%E8%BD%BD%E5%99%A8"></a>3.加载器

我们编写的shellcode实际上只是一串二进制代码，必须包含在一个程序中才能运行起来，应为加载器只需要讲二进制文件跑起来就行了，所以不需要再遵守shellcode编写原则

```
#include &lt;stdio.h&gt;
#include &lt;windows.h&gt;
int main(int argc, char *argv[])
`{`
    //1-代开文件并读取
    HANDLE hFile = CreateFileA(argv[1], GENERIC_READ, 0, NULL, OPEN_ALWAYS, 0, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
    `{`
        printf("Open file wrong\n");
        return -1;
    `}`
    DWORD dwSize;
    dwSize = GetFileSize(hFile, 0);
    //2-将文件内容加载到一个内存中
    LPVOID lpAddress = VirtualAlloc(NULL,dwSize,MEM_COMMIT,PAGE_EXECUTE_READWRITE);
    if (lpAddress == NULL)
    `{`
        printf("VirtualAlloc error : %d", GetLastError());
        CloseHandle(hFile);
        return -1;
    `}`
    DWORD dwRead;
    ReadFile(hFile, lpAddress, dwSize,&amp;dwRead,0);
    //3-使用汇编转到shellcode
    __asm
    `{`
        call lpAddress
    `}`
    _flushall();
    system("pause");
`}`
```

> 其实shellcode就是从汇编提取出来的机器码，当把shellcode加载到内存中，我们也可以使用函数的方式调用，
将汇编改为`((void(*)(void))lpAddress)();`，这样也能成功执行shellcode

### <a class="reference-link" name="4.%E5%AF%B9%E6%A1%86%E6%9E%B6%E8%BF%9B%E8%A1%8C%E4%BC%98%E5%8C%96"></a>4.对框架进行优化

目前我们只实现了一个函数，但是要实现更加复杂的功能（如反弹一个远程shell）的话就必须，因此我们需要加以改进

<a class="reference-link" name="1.%E5%88%9B%E5%BB%BA%E4%B8%80%E4%B8%AA%E5%A4%B4%E6%96%87%E4%BB%B6%EF%BC%8C%E5%B0%86shellcode%E7%9A%84%E5%87%BD%E6%95%B0%EF%BC%88Start%E5%92%8CEnd%E4%B9%8B%E9%97%B4%EF%BC%89%E5%8E%9F%E5%9E%8B%E6%94%BE%E5%88%B0%E8%BF%99%E9%87%8C%E9%9D%A2"></a>**1.创建一个头文件，将shellcode的函数（Start和End之间）原型放到这里面**

```
#pragma once
#include &lt;windows.h&gt;
typedef FARPROC(WINAPI *FN_GetProcAddress)
(
    _In_ HMODULE hModule,
    _In_ LPCSTR lpProcName
    );

typedef HMODULE(WINAPI *FN_LoadLibraryA)
(
    _In_ LPCSTR lpLibFileName
    );

typedef int (WINAPI *FN_MessageBoxA)
(
    _In_opt_ HWND hWnd,
    _In_opt_ LPCSTR lpText,
    _In_opt_ LPCSTR lpCaption,
    _In_ UINT uType
    );
```

之后定义一个结构体并声明

```
typedef struct _FUNCIONS
`{`
    FN_GetProcAddress fn_GetProcAddress;
    FN_LoadLibraryA fn_LoadLibraryA;
    FN_MessageBoxA fn_MessageBoxA;
`}`FUNCIONS, *PFUNCIONS;
```

这样就能在ShellcodeEntry中调用函数了

<a class="reference-link" name="2.%E5%AF%BB%E6%89%BE%E5%87%BD%E6%95%B0%E5%9C%B0%E5%9D%80"></a>**2.寻找函数地址**

由于函数的声明在api.h文件中了，所以要重新寻址

那么我们在a_start上定义如下函数

```
void InitFunctions(PFUNCIONS pFn)
`{`
    pFn-&gt;fn_GetProcAddress = (FN_GetProcAddress)getProcAddress((HMODULE)getKernel32());
    char szLoadLibrary[] = `{` 'L','o','a','d','L','i','b','r','a','r','y','A' ,0 `}`;
    pFn-&gt;fn_LoadLibraryA = (FN_LoadLibraryA)pFn-&gt;fn_GetProcAddress((HMODULE)getKernel32(), szLoadLibrary);

    //MessageBoxA
    char szUser32[] = `{` 'U','s','e','r','3','2','.','d','l','l', 0 `}`;
    char szMsgBox[] = `{` 'M','e','s','s','a','g','e','B','o','x','A' ,0 `}`;
    pFn-&gt;fn_MessageBoxA = (FN_MessageBoxA)pFn-&gt;fn_GetProcAddress((HMODULE)pFn-&gt;fn_LoadLibraryA(szUser32), szMsgBox);
`}`
```

修改后的ShellcodeEntry函数

```
void ShellcodeEntry()
`{`
    char szMsgBoxContent[] = `{` 'H','e','l','l','o',0 `}`;
    char szMsgBoxTitle[] = `{` 't','o','p',0 `}`;
    FUNCIONS fn;
    InitFunctions(&amp;fn);
    fn.fn_MessageBoxA(NULL, szMsgBoxContent, szMsgBoxTitle, MB_OK);
`}`
```

**//记得添加相应的头文件**

之后要添加函数的话：

**1.**将函数原型和声明添加到api.h；**2.**在初始化函数部分设置寻址；**3.**在ShellcodeEntry中调用

<a class="reference-link" name="3.%E5%B0%86%E6%89%80%E6%9C%89%E7%9A%84%E5%87%BD%E6%95%B0%E5%8A%9F%E8%83%BD%E5%AE%9E%E7%8E%B0%E6%94%BE%E5%88%B0%E5%8F%A6%E4%B8%80%E4%B8%AA%E6%96%87%E4%BB%B6%E4%B8%AD"></a>**3.将所有的函数功能实现放到另一个文件中**

在header.h中添加`void CreateConfig(PFUNCIONS pFn)`函数定义

创建一个b_work.cpp，在文件中可以实现MessageBoxA的功能

```
void MessageboxA(PFUNCIONS pFn)
`{`
    char szMsgBoxContent[] = `{` 'H','e','l','l','o',0 `}`;
    char szMsgBoxTitle[] = `{` 't','o','p',0 `}`;
    pFn-&gt;fn_MessageBoxA(NULL, szMsgBoxContent, szMsgBoxTitle, MB_OK);
`}`
```

最后在a_start的ShellcodeEntry中调用

```
void ShellcodeEntry()
`{`
    FUNCIONS fn;
    InitFunctions(&amp;fn);
    MessageboxA(&amp;fn);
`}`
```



## 相关知识
- PE文件结构
- exe程序入口
- 函数指针
- c++函数调用
- c++联合编译


## 参考文章
- [使用VS2015更改应用程序的入口点](https://www.yuanmacha.com/18756856217.html)
- [freebuf公开课-VS平台C/C++高效shellcode编程技术实战](https://www.bilibili.com/video/BV1y4411k7ch)
- [windows下shellcode编写入门](https://blog.csdn.net/x_nirvana/article/details/68921334)
- [新手分享_再谈FS寄存器](https://bbs.pediy.com/thread-226524.htm)
- [Windows平台shellcode开发入门（二）](https://www.freebuf.com/articles/system/94774.html)
- [Windows(x86与x64) Shellcode技术研究](https://www.anquanke.com/post/id/97601)