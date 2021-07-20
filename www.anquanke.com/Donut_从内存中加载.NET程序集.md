> 原文链接: https://www.anquanke.com//post/id/178099 


# Donut：从内存中加载.NET程序集


                                阅读量   
                                **216959**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者modexp，文章来源：modexp.wordpress.com
                                <br>原文地址：[https://modexp.wordpress.com/2019/05/10/dotnet-loader-shellcode/](https://modexp.wordpress.com/2019/05/10/dotnet-loader-shellcode/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0141d61ec2c3121675.jpg)](https://p1.ssl.qhimg.com/t0141d61ec2c3121675.jpg)



## 0x00 前言

我们可以在运行微软Windows系统的大多数设备上看到.NET Framework的身影，.NET在针对Windows设备的攻击（红队）以及防御（蓝队）场景中也深受大家欢迎。2015年，微软将[AMSI（Antimalware Scan Interface）](https://docs.microsoft.com/en-us/windows/desktop/AMSI/antimalware-scan-interface-portal)与执行脚本（VBScript、JScript、PowerShell）的各种Windows组件集成在一起。大约在同一时间，PowerShell中也添加了增强型日志记录或者[Script Block Logging](https://www.fireeye.com/blog/threat-research/2016/02/greater_visibilityt.html)功能，用来捕捉执行脚本的的所有内容，从而解决攻击者使用的任何混淆技术。为了能在红蓝对抗中占据上风，红队必须直接使用程序集（assembly），进一步深入.Net Framework。程序集通常采用C#语言开发，可以为蓝队提供PowerShell支持的所有功能，并且还具备内存加载和执行的独特优势。在本文中，我将向大家简单介绍Donut这款工具，当我们提供一个.NET程序集、类名、方法以及其他可选参数时，[Donut](https://github.com/TheWover/donut)将生成一段位置无关代码（PIC）或者shellcode，可以从内存中加载.NET程序集。我和[TheWover](https://github.com/TheWover/)共同合作开发了这款工具，此外TheWover也写了介绍donut的一篇[文章](https://thewover.github.io/Introducing-Donut/)，欢迎大家参考。

[![](https://p2.ssl.qhimg.com/t01b5b38be3f4fde1b7.png)](https://p2.ssl.qhimg.com/t01b5b38be3f4fde1b7.png)



## 0x01 CLR托管接口

CLR（Common Language Runtime）是一个虚拟机组件，微软从v1.0版Framework（2002年发布）就开始提供[ICorRuntimeHost](https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/hosting/icorruntimehost-interface)接口，用来托管.NET程序集。该接口在2006年发布的v2.0版Framework中被[ICLRRuntimeHost](https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/hosting/iclrruntimehost-interface)所替代，而后者又在2009年发布的v4.0版Framew中被[ICLRMetaHost](https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/hosting/iclrmetahost-interface)替代。虽然已被弃用，但`ICorRuntimeHost`目前仍是从内存中加载程序集的最简单方法。我们可以使用多种方法来实例化该接口，最常用的有如下几种方法：
<li>
[CoInitializeEx](https://docs.microsoft.com/en-us/windows/desktop/api/combaseapi/nf-combaseapi-coinitializeex)以及[CoCreateInstance](https://docs.microsoft.com/en-us/windows/desktop/api/combaseapi/nf-combaseapi-cocreateinstance)
</li>
<li>
[CorBindToRuntime](https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/hosting/corbindtoruntime-function)或者[CorBindToRuntimeEx](https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/hosting/corbindtoruntimeex-function)
</li>
<li>
[CLRCreateInstance](https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/hosting/clrcreateinstance-function)以及[ICLRRuntimeInfo](https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/hosting/iclrruntimeinfo-interface)
</li>
`CorBindToRuntime`以及`CorBindToRuntimeEx`执行的是同样的操作，但`CorBindToRuntimeEx`函数可以让我们指定CLR的具体行为。使用`CLRCreateInstance`时我们不必初始化COM（Component Object Model），但v4.0版之前的Framework并没有实现该函数。如下C++代码可以从内存中加载.NET程序集：

```
#include &lt;windows.h&gt;
#include &lt;oleauto.h&gt;
#include &lt;mscoree.h&gt;
#include &lt;comdef.h&gt;

#include &lt;cstdio&gt;
#include &lt;cstdint&gt;
#include &lt;cstring&gt;
#include &lt;cstdlib&gt;
#include &lt;sys/stat.h&gt;

#import "mscorlib.tlb" raw_interfaces_only

void rundotnet(void *code, size_t len) `{`
    HRESULT                  hr;
    ICorRuntimeHost          *icrh;
    IUnknownPtr              iu;
    mscorlib::_AppDomainPtr  ad;
    mscorlib::_AssemblyPtr   as;
    mscorlib::_MethodInfoPtr mi;
    VARIANT                  v1, v2;
    SAFEARRAY                *sa;
    SAFEARRAYBOUND           sab;

    printf("CoCreateInstance(ICorRuntimeHost).n");
    hr = CoInitializeEx(NULL, COINIT_MULTITHREADED);

    hr = CoCreateInstance(
      CLSID_CorRuntimeHost, 
      NULL, 
      CLSCTX_ALL,
      IID_ICorRuntimeHost, 
      (LPVOID*)&amp;icrh);

    if(FAILED(hr)) return;

    printf("ICorRuntimeHost::Start()n");
    hr = icrh-&gt;Start();
    if(SUCCEEDED(hr)) `{`
      printf("ICorRuntimeHost::GetDefaultDomain()n");
      hr = icrh-&gt;GetDefaultDomain(&amp;iu);
      if(SUCCEEDED(hr)) `{`
        printf("IUnknown::QueryInterface()n");
        hr = iu-&gt;QueryInterface(IID_PPV_ARGS(&amp;ad));
        if(SUCCEEDED(hr)) `{`
          sab.lLbound   = 0;
          sab.cElements = len;
          printf("SafeArrayCreate()n");
          sa = SafeArrayCreate(VT_UI1, 1, &amp;sab);
          if(sa != NULL) `{`
            CopyMemory(sa-&gt;pvData, code, len);
            printf("AppDomain::Load_3()n");
            hr = ad-&gt;Load_3(sa, &amp;as);
            if(SUCCEEDED(hr)) `{`
              printf("Assembly::get_EntryPoint()n");
              hr = as-&gt;get_EntryPoint(&amp;mi);
              if(SUCCEEDED(hr)) `{`
                v1.vt    = VT_NULL;
                v1.plVal = NULL;
                printf("MethodInfo::Invoke_3()n");
                hr = mi-&gt;Invoke_3(v1, NULL, &amp;v2);
                mi-&gt;Release();
              `}`
              as-&gt;Release();
            `}`
            SafeArrayDestroy(sa);
          `}`
          ad-&gt;Release();
        `}`
        iu-&gt;Release();
      `}`
      icrh-&gt;Stop();
    `}`
    icrh-&gt;Release();
`}`

int main(int argc, char *argv[])
`{`
    void *mem;
    struct stat fs;
    FILE *fd;

    if(argc != 2) `{`
      printf("usage: rundotnet &lt;.NET assembly&gt;n");
      return 0;
    `}`

    // 1. get the size of file
    stat(argv[1], &amp;fs);

    if(fs.st_size == 0) `{`
      printf("file is empty.n");
      return 0;
    `}`

    // 2. try open assembly
    fd = fopen(argv[1], "rb");
    if(fd == NULL) `{`
      printf("unable to open "%s".n", argv[1]);
      return 0;
    `}`
    // 3. allocate memory 
    mem = malloc(fs.st_size);
    if(mem != NULL) `{`
      // 4. read file into memory
      fread(mem, 1, fs.st_size, fd);
      // 5. run the program from memory
      rundotnet(mem, fs.st_size);
      // 6. free memory
      free(mem);
    `}`
    // 7. close assembly
    fclose(fd);

    return 0;
`}`
```

如下是C#版的“Hello, World!”程序，当使用`csc.exe`编译后能生成一个.NET程序集，可以用来测试加载器。

```
// A Hello World! program in C#.
using System;
namespace HelloWorld
`{`
    class Hello 
    `{`
        static void Main() 
        `{`
            Console.WriteLine("Hello World!");
        `}`
    `}`
`}`
```

编译并运行这些代码后，我们可以得到如下输出：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010f54b6db1046b88b.png)

这是执行.NET程序集的基本方式，其中并没有考虑到Framework的具体版本。shellcode的实现有点不一样，会解析`CorBindToRuntime`以及`CLRCreateInstance`的地址（这与[subTee](https://twitter.com/subtee)开发的[AssemblyLoader](https://github.com/caseysmithrc/AssemblyLoader)类似）。如果成功解析`CLRCreateInstance`，并且调用后返回`E_NOTIMPL`或者“Not implemented”，我们就会执行`CorBindToRuntime`（其中`pwszVersion`参数设置为NULL），请求可用的最新版本。如果我们使用`CorBindToRuntime`请求系统当前不支持的某个版本，那么运行shellcode的托管进程可能会弹出错误消息。比如，当Windows 7系统只支持v3.5.30729.5420版时，如果我们请求v4.0.30319，就会看到如下错误信息：

[![](https://p4.ssl.qhimg.com/t01cc2d939e72d2d611.png)](https://p4.ssl.qhimg.com/t01cc2d939e72d2d611.png)

大家可能有疑问，为什么之前使用的OLE函数没有在shellcode中使用。除了OLE32之外，OLE函数有时候会在其他DLL中引用，比如COMBASE。xGetProcAddress可以处理转发引用，但至少目前为止，shellcode使用的是`CorBindToRuntime`以及`CLRCreateInstance`。在新版框架中，我们还可以使用`CoCreateInstance`。



## 0x02 定义.NET类型

在非托管（unmanaged）C++程序中，我们可以使用`#import`指令来访问类型（Types）。前文代码使用的是在`mscorlib.tlb`中定义的`_AppDomain`、`_Assembly`以及`_MethodInfo`接口。然而问题在于，在公开版的Windows SDK中并没有定义这些接口。为了在较低级语言（如汇编语言或者C）中使用.NET类型，我们首先得手动定义这些接口。我们可以使用[LoadTypeLib](https://docs.microsoft.com/en-us/windows/desktop/api/oleauto/nf-oleauto-loadtypelib) API来枚举类型信息，该函数会返回指向[ITypeLib](https://docs.microsoft.com/en-us/windows/desktop/api/oaidl/nn-oaidl-itypelib)接口的一个指针。该接口可以提取相关信息，比如库接口、方法以及变量。我发现[Olewoo](http://www.benf.org/other/olewoo/index.html)这款工具可以用来查看`mscorlib.tlb`信息。如果我们忽略面向对象编程（OOP）方面的相关信息，比如类、对象、继承、封装、抽象、多态……等，我们可以从底层来分析接口，毕竟接口只是指向某种数据结构的一个指针，而该数据结构包含指向函数/方法的指针而已。除了[phplib](https://github.com/embedthis/phplib/blob/master/ext/com_dotnet/com_dotnet.c)中的一个文件之外（该文件定义了`_AppDomain`接口），我无法在网上找到所需接口的定义。根据找到的示例，我构造了加载程序集所需的其他接口。如下即为`_AppDomain`接口中的某个方法：

```
HRESULT (STDMETHODCALLTYPE *InvokeMember_3)(
          IType        *This,
          BSTR         name,
          BindingFlags invokeAttr,
          IBinder      *Binder,
          VARIANT      Target,
          SAFEARRAY    *args,
          VARIANT      *pRetVal);
```

虽然shellcode中没有使用`IBinder`接口的任何方法，我们可以将类型安全地改成`void *`，但为了以后使用方便，我还是定义了如下接口。`DUMMY_METHOD`宏简单定义了一个函数指针：

```
typedef struct _Binder IBinder;

    #undef DUMMY_METHOD
    #define DUMMY_METHOD(x) HRESULT ( STDMETHODCALLTYPE *dummy_##x )(IBinder *This)

    typedef struct _BinderVtbl `{`
        HRESULT ( STDMETHODCALLTYPE *QueryInterface )(
          IBinder * This,
          /* [in] */ REFIID riid,
          /* [iid_is][out] */ void **ppvObject);

        ULONG ( STDMETHODCALLTYPE *AddRef )(
          IBinder * This);

        ULONG ( STDMETHODCALLTYPE *Release )(
          IBinder * This);

        DUMMY_METHOD(GetTypeInfoCount);
        DUMMY_METHOD(GetTypeInfo);
        DUMMY_METHOD(GetIDsOfNames);
        DUMMY_METHOD(Invoke);
        DUMMY_METHOD(ToString);
        DUMMY_METHOD(Equals);
        DUMMY_METHOD(GetHashCode);
        DUMMY_METHOD(GetType);
        DUMMY_METHOD(BindToMethod);
        DUMMY_METHOD(BindToField);
        DUMMY_METHOD(SelectMethod);
        DUMMY_METHOD(SelectProperty);
        DUMMY_METHOD(ChangeType);
        DUMMY_METHOD(ReorderArgumentArray);
    `}` BinderVtbl;

    typedef struct _Binder `{`
      BinderVtbl *lpVtbl;
    `}` Binder;
```

我在[payload.h](https://github.com/TheWover/donut/blob/master/payload/payload.h)中定义了内存加载程序集所需的方法。



## 0x03 Donut实例

我们会将shellcode与某个数据块实例绑定在一起，这个数据块可以看成shellcode的“数据段”（data segment），其中包含解析API之前待加载的DLL名、API字符串对应的64位哈希、内存加载.NET程序集的相关COM GUID，如果实例和模块存储在staging服务器上，那么数据段也可以包含实例对应的解密秘钥。许多使用C语言编写的shellcode都倾向于在栈上存储字符串，但像[FireEye Labs Obfuscated String Solver](https://github.com/fireeye/flare-floss)之类的工具可以轻易恢复这些信息，帮助我们更好分析代码。当涉及代码位置排列时，在独立的数据块中保存字符串就能体现出优势。我们可以在保持功能的同时修改代码，并且永远不需要处理“只读”的立即值，这些值将使整个过程变得复杂，大大增加代码量。在`call`操作码（opcode）之后以及`pop ecx` / `pop rcx`之前我们使用的结构如下所示。在x86以及x86-64 shellcode中我们使用了`fastcall`约定，使代码便于加载指向保存在`ecx`或`rcx`寄存器中实例的指针。

```
typedef struct _DONUT_INSTANCE `{`
    uint32_t    len;                          // total size of instance
    DONUT_CRYPT key;                          // decrypts instance
    // everything from here is encrypted

    int         dll_cnt;                      // the number of DLL to load before resolving API
    char        dll_name[DONUT_MAX_DLL][32];  // a list of DLL strings to load
    uint64_t    iv;                           // the 64-bit initial value for maru hash
    int         api_cnt;                      // the 64-bit hashes of API required for instance to work

    union `{`
      uint64_t  hash[48];                     // holds up to 48 api hashes
      void     *addr[48];                     // holds up to 48 api addresses
      // include prototypes only if header included from payload.h
      #ifdef PAYLOAD_H
      struct `{`
        // imports from kernel32.dll
        LoadLibraryA_t             LoadLibraryA;
        GetProcAddress_t           GetProcAddress;
        VirtualAlloc_t             VirtualAlloc;             
        VirtualFree_t              VirtualFree;  

        // imports from oleaut32.dll
        SafeArrayCreate_t          SafeArrayCreate;          
        SafeArrayCreateVector_t    SafeArrayCreateVector;    
        SafeArrayPutElement_t      SafeArrayPutElement;      
        SafeArrayDestroy_t         SafeArrayDestroy;         
        SysAllocString_t           SysAllocString;           
        SysFreeString_t            SysFreeString;            

        // imports from wininet.dll
        InternetCrackUrl_t         InternetCrackUrl;         
        InternetOpen_t             InternetOpen;             
        InternetConnect_t          InternetConnect;          
        InternetSetOption_t        InternetSetOption;        
        InternetReadFile_t         InternetReadFile;         
        InternetCloseHandle_t      InternetCloseHandle;      
        HttpOpenRequest_t          HttpOpenRequest;          
        HttpSendRequest_t          HttpSendRequest;          
        HttpQueryInfo_t            HttpQueryInfo;

        // imports from mscoree.dll
        CorBindToRuntime_t         CorBindToRuntime;
        CLRCreateInstance_t        CLRCreateInstance;
      `}`;
      #endif
    `}` api;

    // GUID required to load .NET assembly
    GUID xCLSID_CLRMetaHost;
    GUID xIID_ICLRMetaHost;  
    GUID xIID_ICLRRuntimeInfo;
    GUID xCLSID_CorRuntimeHost;
    GUID xIID_ICorRuntimeHost;
    GUID xIID_AppDomain;

    DONUT_INSTANCE_TYPE type;  // PIC or URL 

    struct `{`
      char url[DONUT_MAX_URL];
      char req[16];            // just a buffer for "GET"
    `}` http;

    uint8_t     sig[DONUT_MAX_NAME];          // string to hash
    uint64_t    mac;                          // to verify decryption ok

    DONUT_CRYPT mod_key;       // used to decrypt module
    uint64_t    mod_len;       // total size of module

    union `{`
      PDONUT_MODULE p;         // for URL
      DONUT_MODULE  x;         // for PIC
    `}` module;
`}` DONUT_INSTANCE, *PDONUT_INSTANCE;
```



## 0x04 Donut模块

.NET使用模块（Module）这种数据结构来存储程序集。模块可以与实例（Instance）一起存储，或者存放在shellcode能够提取的staging服务器上。模块中包含程序集、类名、方法以及可选参数。`sig`值包含随机8字节字符串，当使用`Maru`哈希函数处理时，会生成64bit值，该值与`mac`值相等。这种方式可以用来验证模块的解密是否成功。模块秘钥存放在内嵌于shellcode的实例中。

```
// everything required for a module goes into the following structure
typedef struct _DONUT_MODULE `{`
    DWORD   type;                                   // EXE or DLL
    WCHAR   runtime[DONUT_MAX_NAME];                // runtime version
    WCHAR   domain[DONUT_MAX_NAME];                 // domain name to use
    WCHAR   cls[DONUT_MAX_NAME];                    // name of class and optional namespace
    WCHAR   method[DONUT_MAX_NAME];                 // name of method to invoke
    DWORD   param_cnt;                              // number of parameters to method
    WCHAR   param[DONUT_MAX_PARAM][DONUT_MAX_NAME]; // string parameters passed to method
    CHAR    sig[DONUT_MAX_NAME];                    // random string to verify decryption
    ULONG64 mac;                                    // to verify decryption ok
    DWORD   len;                                    // size of .NET assembly
    BYTE    data[4];                                // .NET assembly file
`}` DONUT_MODULE, *PDONUT_MODULE;
```



## 0x05 随机秘钥

在Windows上，[CryptGenRandom](https://docs.microsoft.com/en-us/windows/desktop/api/wincrypt/nf-wincrypt-cryptgenrandom)可以生成密码学上安全的随机值，在Linux上，我们可以使用`/dev/urandom`（不使用`/dev/random`，该设备会阻塞读取请求）。Thomas Huhn在关于`urandom`的一篇[文章](https://www.2uo.de/myths-about-urandom)中提到`/dev/urandom`是Linux上随机数据流的首选。我们在Donut中使用[CreateRandom](https://github.com/TheWover/donut/blob/master/donut.c)来生成随机秘钥，建议大家参考使用。



## 0x05 随机字符串

除非用户手动指定，否则我们会使用随机字符串来生成应用程序域（Application Domain）名。如果donut模块存放在staging服务器上，也会生成随机名。负责该操作的函数为[GenRandomString](https://github.com/TheWover/donut/blob/master/donut.c)，其中用到了`CreateRandom`生成的随机字节，配合“HMN34P67R9TWCXYF”字符串生成了最终字符串（这个魔术字符串来源于stackoverflow上的一篇[帖子](https://stackoverflow.com/a/27459196)）。



## 0x06 对称加密

对合（involution）函数是指自己是自己逆函数的函数，许多工具会使用对合函数来混淆代码。如果大家之前逆向分析过恶意软件，那么肯定对异或（XOR）函数非常熟悉，这种函数非常简单，使用场景也非常广泛。此外，[Noekeon](https://tinycrypt.wordpress.com/2017/01/11/asmcodes-noekeon/)分组加密是一种非线性加密，也是较为复杂的对合方式。Donut并没有使用对合加密方式，而是使用[Chaskey](https://mouha.be/chaskey/)分组密码（Counter（CTR）模式）来加密模块，其中解密秘钥内嵌在shellcode中。如果Donut模块来自于staging服务器，那么想知道其中所包含的具体信息的唯一方法就是恢复shellcode，寻找`CreateRandom`函数的脆弱点或者打破Chaskey加密算法。

```
static void chaskey(void *mk, void *p) `{`
    uint32_t i,*w=p,*k=mk;

    // add 128-bit master key
    for(i=0;i&lt;4;i++) w[i]^=k[i];

    // apply 16 rounds of permutation
    for(i=0;i&lt;16;i++) `{`
      w[0] += w[1],
      w[1]  = ROTR32(w[1], 27) ^ w[0],
      w[2] += w[3],
      w[3]  = ROTR32(w[3], 24) ^ w[2],
      w[2] += w[1],
      w[0]  = ROTR32(w[0], 16) + w[3],
      w[3]  = ROTR32(w[3], 19) ^ w[0],
      w[1]  = ROTR32(w[1], 25) ^ w[2],
      w[2]  = ROTR32(w[2], 16);
    `}`
    // add 128-bit master key
    for(i=0;i&lt;4;i++) w[i]^=k[i];
`}`
```

之所以选择使用Chaskey算法，是因为该算法简洁紧凑，易于实现，并且不包含容易被检测的常量特征。Chaskey的主要缺点是使用人数较少，因此并没有像AES那样在密码学上被广泛分析。当2014发布Chaskey算法时，官方推荐的加密轮次为8次。2015年，已经有针对7轮加密的攻击技术出现，这表明官方推荐的加密轮次并不是一个足够安全的边界。针对此攻击，设计人员提高了加密轮次，建议使用12轮加密，这里Donut使用的是16轮加密的长期支持（LTS）版本。



## 0x07 API哈希

如果在内存扫描之前已经掌握API字符串哈希，那么Donut就非常容易被检测出来。我们[建议](https://modexp.wordpress.com/2017/08/05/shellcode-maru-hash/)在Windows API哈希中使用分组加密方式，增加哈希过程中的熵（entropy），以便进一步规避针对代码的检测机制。Donut使用的是`Maru`哈希函数，该函数基于`Speck`分组加密算法，使用的是Davies-Meyer构建和填充方式，这种方式与MD4及MD5类似。Speck随机生成了一个64bit初始值（IV），以明文方式使用该值来加密，秘钥为API字符串。

```
static uint64_t speck(void *mk, uint64_t p) `{`
    uint32_t k[4], i, t;
    union `{`
      uint32_t w[2];
      uint64_t q;
    `}` x;

    // copy 64-bit plaintext to local buffer
    x.q = p;

    // copy 128-bit master key to local buffer
    for(i=0;i&lt;4;i++) k[i]=((uint32_t*)mk)[i];

    for(i=0;i&lt;27;i++) `{`
      // donut_encrypt 64-bit plaintext
      x.w[0] = (ROTR32(x.w[0], 8) + x.w[1]) ^ k[0];
      x.w[1] =  ROTR32(x.w[1],29) ^ x.w[0];

      // create next 32-bit subkey
      t = k[3];
      k[3] = (ROTR32(k[1], 8) + k[0]) ^ i;
      k[0] =  ROTR32(k[0],29) ^ k[3];
      k[1] = k[2]; k[2] = t;
    `}`
    // return 64-bit ciphertext
    return x.q;
`}`
```



## 0x08 总结

Donut提供了通过shellcode实现CLR注入的一种方法，红队可以基于此建模，从攻击方和防御方角度构建分析和缓解的整体框架。这个过程中肯定会有恶意软件开发者和攻击人员会滥用这款工具，但我们坚信整体优点依然能弥补带来的不足（但愿如此），大家可以访问[此处](https://github.com/TheWover/donut)获取源代码。
