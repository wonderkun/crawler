> 原文链接: https://www.anquanke.com//post/id/221906 


# 透明部落样本payload分析


                                阅读量   
                                **189527**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t019d5492d0b987da3a.png)](https://p3.ssl.qhimg.com/t019d5492d0b987da3a.png)



## 背景信息

“透明部落”是一个南亚(可能是巴基斯坦)来源具有政府背景的APT组织，其长期针对周边国家和地区的军队和政府机构实施定向攻击，其和南亚“响尾蛇”APT组织属于两个相互 “敌对”的APT组织。<br>
样本信息

由于没有找到docx的md5所以也无法获取到样本只能从宏样本释放的payload进行分析。

• 档案名称：TrayIcos.exe<br>
• 文件类型：适用于MS Windows（GUI）Intel 80386 32位的PE32可执行文件<br>
• 档案大小：2.4 MB（2519552位元组）<br>
• MD5：18ACD5EBED316061F885F54F82F00017<br>
• 签名：Microsoft Visual C ++ 8



## 静态分析

初步先使用ida打开观看下大体的内容，下图展示的大概就是获取资源然后进行解密等操作

[![](https://p5.ssl.qhimg.com/t01f1d76276491c76a1.png)](https://p5.ssl.qhimg.com/t01f1d76276491c76a1.png)

下面这张图如果有经验的话可以发现这是利用了CLR进行内存中加载.NET程序，没有经验也没有关系后面也都会提到。

[![](https://p0.ssl.qhimg.com/t0101d32e3f9819f9dd.png)](https://p0.ssl.qhimg.com/t0101d32e3f9819f9dd.png)

下面就是实现C++运行donet的代码

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



## 动态调试

有了大体的认识之后我们可以开始用OD调试看看里面具体的细节，首先我们可以来到程序的入口点，不是VC的入口点，而是进入main函数里面的代码。发现调用了OleInitialize这个函数，这个函数的作用是初始化COM库。所以后面肯定使用到了COM库。

[![](https://p3.ssl.qhimg.com/t01c31fee43a40142ac.png)](https://p3.ssl.qhimg.com/t01c31fee43a40142ac.png)

下面是这种操作mov了一大堆的指令然后再调用了一个call

[![](https://p1.ssl.qhimg.com/t01bf480d8eedb9a7f9.png)](https://p1.ssl.qhimg.com/t01bf480d8eedb9a7f9.png)

进入这个call里面观看，这个函数就是取到了之前mov的数组进行解密了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b2cae5cdfa4fec3c.png)

那么我们直接来到return 看看返回值，可以很明显发现这解密出了字符串

[![](https://p3.ssl.qhimg.com/t0154ef4a5c9d75ad2b.png)](https://p3.ssl.qhimg.com/t0154ef4a5c9d75ad2b.png)

所以我把这个函数命名为DecString

[![](https://p2.ssl.qhimg.com/t01cfcfece295624837.png)](https://p2.ssl.qhimg.com/t01cfcfece295624837.png)

下面是获取环境变量`Cor_Enable_Profiling`的值如果和0x41B2A0做比较如果不等于则会继续走下面，等于则跳转走另一分支,另一分支就是直接结束程序。所以我们走遍历模块的。

[![](https://p3.ssl.qhimg.com/t01bf7483b86c7d2d14.png)](https://p3.ssl.qhimg.com/t01bf7483b86c7d2d14.png)

下面的api就是在创建快照

[![](https://p2.ssl.qhimg.com/t016f98eba36fe86e45.png)](https://p2.ssl.qhimg.com/t016f98eba36fe86e45.png)

遍历模块和解密字符串

[![](https://p2.ssl.qhimg.com/t010e905f997aa0fa1e.png)](https://p2.ssl.qhimg.com/t010e905f997aa0fa1e.png)

解密出来mscorjit.dll，这个dll是donet的，所以遍历模块应该是为了找到这个dll

[![](https://p3.ssl.qhimg.com/t0114b138a6b90e6508.png)](https://p3.ssl.qhimg.com/t0114b138a6b90e6508.png)

这一段汇编就是strcmp，不熟悉的可以多看看

[![](https://p5.ssl.qhimg.com/t01c886e380a33ffdbe.png)](https://p5.ssl.qhimg.com/t01c886e380a33ffdbe.png)

如果找到一样的则关闭句柄，并且return

[![](https://p0.ssl.qhimg.com/t01c243a3e2392dc486.png)](https://p0.ssl.qhimg.com/t01c243a3e2392dc486.png)

然后下面又在找这个dll clrjit.dll

[![](https://p1.ssl.qhimg.com/t015c91f41c54478be5.png)](https://p1.ssl.qhimg.com/t015c91f41c54478be5.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010afeb4515bfd4ca8.png)

下面的代码就是一直循环在找那两个dll

[![](https://p3.ssl.qhimg.com/t019df4ada0912a460e.png)](https://p3.ssl.qhimg.com/t019df4ada0912a460e.png)

当最后没有找到的话就会来到后面的解析资源的操作<br>
遍历模块没看懂的话可以看看MSDN遍历模块

[![](https://p0.ssl.qhimg.com/t01ada87cfe81a87e73.png)](https://p0.ssl.qhimg.com/t01ada87cfe81a87e73.png)

这里是在找资源了

[![](https://p1.ssl.qhimg.com/t01365cb8af0be164a1.png)](https://p1.ssl.qhimg.com/t01365cb8af0be164a1.png)

然后先malloc一个资源大小 然后又new了一个0x40022的大小

[![](https://p3.ssl.qhimg.com/t0175cb564eb2ac07c6.png)](https://p3.ssl.qhimg.com/t0175cb564eb2ac07c6.png)

很明显下面是个if else 就是下面这样的汇编格式，到这里内存空间就申请完了，下面就是拷贝资源了吧

cmp<br>
jxx<br>
ELSE_BEGIN:<br>
…<br>
jmp ELSE_END<br>
….<br>
ELSE_END：

[![](https://p5.ssl.qhimg.com/t015d5fdec8aa1dd2d4.png)](https://p5.ssl.qhimg.com/t015d5fdec8aa1dd2d4.png)

这个函数主要做的就是把资源拷贝到new出来的空间

[![](https://p5.ssl.qhimg.com/t0113cbe709079ddba3.png)](https://p5.ssl.qhimg.com/t0113cbe709079ddba3.png)

这个是按照1024个字节拷贝到malloc这个内存中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010cc076da2a576c56.png)

这里在取模sizeofRes也就是拷贝不足1024个字节的资源到malloc申请的空间中

[![](https://p3.ssl.qhimg.com/t0181ec8c4fb024c414.png)](https://p3.ssl.qhimg.com/t0181ec8c4fb024c414.png)

释放资源后，malloc了一个空间，这个空间就是放解密后的资源数据

[![](https://p4.ssl.qhimg.com/t0166fa177720fe0ca6.png)](https://p4.ssl.qhimg.com/t0166fa177720fe0ca6.png)

看看下面解密函数栈，第一个是刚刚malloc的空间，也就是解密数据要放的空间。第二个是之前malloc的大小。第三个是之前mallco空间的地址(加密的数据)，最后一个是资源的大小。

[![](https://p0.ssl.qhimg.com/t0122313457dc11838e.png)](https://p0.ssl.qhimg.com/t0122313457dc11838e.png)

解密后的资源不难看出有一个PE

[![](https://p4.ssl.qhimg.com/t01a7249ff3db0fe344.png)](https://p4.ssl.qhimg.com/t01a7249ff3db0fe344.png)

再后面也没啥看的大概就是准备donet的环境，把该有的dll加载起来然后用C++调用这个PE文件，有兴趣的可以看看

[![](https://p4.ssl.qhimg.com/t01180f988772548b18.png)](https://p4.ssl.qhimg.com/t01180f988772548b18.png)

现在我把那个PE给dump出来看看

[![](https://p5.ssl.qhimg.com/t011a3bfee038da75f4.png)](https://p5.ssl.qhimg.com/t011a3bfee038da75f4.png)

使用PE解析工具看看发现资源里面还藏了个PE

[![](https://p4.ssl.qhimg.com/t01f1da893b13ecfc49.png)](https://p4.ssl.qhimg.com/t01f1da893b13ecfc49.png)

既然这样这个dll就没啥必要看了大概功能就是释放执行里面的PE还是个Loader，用dnspy把资源保存出来

[![](https://p1.ssl.qhimg.com/t011de6df323f0e0679.png)](https://p1.ssl.qhimg.com/t011de6df323f0e0679.png)

一看就是被混淆了的使用工具de4dot.exe去除试试

[![](https://p4.ssl.qhimg.com/t015e8a27b60627c77c.png)](https://p4.ssl.qhimg.com/t015e8a27b60627c77c.png)

去完混淆后基本能很好的看懂了

[![](https://p3.ssl.qhimg.com/t0174391d016fd61ec9.png)](https://p3.ssl.qhimg.com/t0174391d016fd61ec9.png)

这里就是远控的的代码地方了 donet的感兴趣的自己可以看看还是比较简单的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019bc07b1b8b176f65.png)

VT查了下最里层的Payload还没有被查

[![](https://p5.ssl.qhimg.com/t01026449527e5db317.png)](https://p5.ssl.qhimg.com/t01026449527e5db317.png)



## 样本来源

[cyberstanc](https://cyberstanc.com/blog/a-look-into-apt36-transparent-tribe/)
