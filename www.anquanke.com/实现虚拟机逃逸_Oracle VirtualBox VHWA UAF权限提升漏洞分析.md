> 原文链接: https://www.anquanke.com//post/id/209365 


# 实现虚拟机逃逸：Oracle VirtualBox VHWA UAF权限提升漏洞分析


                                阅读量   
                                **216797**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者starlabs，文章来源：starlabs.sg
                                <br>原文地址：[https://starlabs.sg/blog/2020/06/oracle-virtualbox-vhwa-use-after-free-privilege-escalation-vulnerability/](https://starlabs.sg/blog/2020/06/oracle-virtualbox-vhwa-use-after-free-privilege-escalation-vulnerability/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01e315aa363200fe9c.png)](https://p1.ssl.qhimg.com/t01e315aa363200fe9c.png)



## 一、前言

我在STAR Labs进行为期一个月的实习期间，主要负责对VirturalBox的分析，在此过程中我学到了许多关于漏洞挖掘、漏洞分类、根本原因分析和漏洞利用的只是。在这篇文章中，将详细介绍我在实习期间发现的一个UAF漏洞，以及我如何利用该漏洞编写虚拟机逃逸漏洞利用的细节。在撰写本文时，产品的最新版本是VirtualBox 6.1.2 r135662。



## 二、建立环境

这篇文章所使用的测试环境是Windows 10宿主机和Windows 7虚拟机。在测试环境中，我们将虚拟机配置为使用VBoxVGA图形控制器，并且选中“启用2D视频加速”的选项。

在发现任何漏洞或者编写任何漏洞利用之前，我们应该首先创建一个调试环境，以便于定位引起崩溃的根本原因并对漏洞利用进行调试。VirtualBox受到进程加固的保护，因此在VirtualBox的发行版本中，不可能（或者很难）将用户级别调试器附加到VirtualBox进程中。但幸运的是，VirtualBox是一个开源软件，可以编译一个未经加固的调试版本，而这样的版本就允许附加调试器了。我的导师anhdaden使用了附加调试器的VirtualBox 6.1.0 r135406版本，这对于我直接进行调试很有帮助。

在这里，引用[@_niklasb](https://github.com/_niklasb)的描述：

[![](https://p1.ssl.qhimg.com/t01bd1467a68e064c81.png)](https://p1.ssl.qhimg.com/t01bd1467a68e064c81.png)

最后，我们还需要掌握一些关于编写Windows内核驱动程序的知识。这对于漏洞利用来说是必要的，因为我们将在虚拟机中与宿主机模拟的设备进行交互，而这些设备只能在内核级访问。在编写WDM驱动程序的过程中，我们参考了以下资料：

[https://web.archive.org/web/20080514132017/](https://web.archive.org/web/20080514132017/)

[http://www.catch22.net/tuts/kernel1.asp](http://www.catch22.net/tuts/kernel1.asp)

我们并不需要对这一领域有太过深入的掌握，就可以理解漏洞利用的过程。



## 三、背景

我们所发现的漏洞位于宿主机与虚拟机的共享内存接口（HGSMI）提供的VirtualBox视频加速（VBVA）功能中。要使用这个功能，虚拟机内核驱动程序需要映射物理地址`0xE0000000`以执行内存映射的I/O（MMIO）。虚拟机需要使用格式化的HGSMI命令写入物理地址`0xE0000000`的VRAM缓冲区，指示其正在使用哪个通道，以及其他详细信息。之后，虚拟机应向IO接口`VGA_PORT_HGSMI_GUEST`(0x3d0)发送输出指令，以允许模拟设备开始处理。我们可以使用`HGSMIBufferProcess`函数看到详细信息。为了避免产生额外的工作量，我利用了voidsecurity针对这一攻击面编写的另一个漏洞的漏洞利用代码。

对于VBVA服务，它是由`vbvaChannelHandler`函数负责处理。这里支持发送多种VBVA命令，但其中的一个`VBVA_VHWA_CMD`命令中存在问题，该命令用于视频硬件加速（VHWA）。通过使用调试器跟踪函数调用，我们可以确定VHWA命令的实际处理程序。

```
vbvaChannelHandler
  |_ vbvaVHWAHandleCommand
      |_ vbvaVHWACommandSubmit(Inner)
          |_ pThisCC-&gt;pDrv-&gt;pfnVHWACommandProcess = Display::i_handleVHWACommandProcess
              |_ pFramebuffer-&gt;ProcessVHWACommand = VBoxOverlayFrameBuffer.ProcessVHWACommand
                  |_ mOverlay.onVHWACommand = VBoxQGLOverlay::onVHWACommand
                      |_ mCmdPipe.postCmd = VBoxVHWACommandElementProcessor::postCmd
                          |_ pCmd-&gt;setData
                          |_ RTListAppend(&amp;mCommandList, &amp;pCmd-&gt;ListNode);

*once command is added to list, it is then processed

VBoxQGLOverlay::onVHWACommandEvent
 |_ mCmdPipe.getCmd
 |_ processCmd = VBoxQGLOverlay::processCmd
     |_ vboxDoVHWACmd = VBoxQGLOverlay::vboxDoVHWACmd
         |_ vboxDoVHWACmdExec = VBoxQGLOverlay::vboxDoVHWACmdExec
```

`VBoxQGLOverlay::vboxDoVHWACmdExec`将会是最重要的一个函数，因为其中包含VHWA命令的处理内容。



## 四、漏洞分析

现在，我们已经大致熟悉了代码，接下来就可以深入研究易受攻击的VHWA命令。在`VBoxQGLOverlay::vboxDoVHWACmdExec`中，有各种命令可以对对象进行分配、删除和操作，CTF挑战者可能对这块比较熟悉。

```
// src/VBox/Frontends/VirtualBox/src/VBoxFBOverlay.cpp:4669

void VBoxQGLOverlay::vboxDoVHWACmdExec(void RT_UNTRUSTED_VOLATILE_GUEST *pvCmd, int /*VBOXVHWACMD_TYPE*/ enmCmdInt, bool fGuestCmd)
`{`
    struct VBOXVHWACMD RT_UNTRUSTED_VOLATILE_GUEST *pCmd = (struct VBOXVHWACMD RT_UNTRUSTED_VOLATILE_GUEST *)pvCmd;
    VBOXVHWACMD_TYPE enmCmd = (VBOXVHWACMD_TYPE)enmCmdInt;

    switch (enmCmd)
    `{`
...
        case VBOXVHWACMD_TYPE_SURF_CREATE:
        `{`
            VBOXVHWACMD_SURF_CREATE RT_UNTRUSTED_VOLATILE_GUEST *pBody = VBOXVHWACMD_BODY(pCmd, VBOXVHWACMD_SURF_CREATE);
            Assert(!mGlOn == !mOverlayImage.hasSurfaces());
            initGl();
            makeCurrent();
            vboxSetGlOn(true);
            pCmd-&gt;rc = mOverlayImage.vhwaSurfaceCreate(pBody);
...
        case VBOXVHWACMD_TYPE_SURF_OVERLAY_UPDATE:
        `{`
            VBOXVHWACMD_SURF_OVERLAY_UPDATE RT_UNTRUSTED_VOLATILE_GUEST *pBody = VBOXVHWACMD_BODY(pCmd, VBOXVHWACMD_SURF_OVERLAY_UPDATE);
            Assert(!mGlOn == !mOverlayImage.hasSurfaces());
            initGl();
            makeCurrent();
            pCmd-&gt;rc = mOverlayImage.vhwaSurfaceOverlayUpdate(pBody);
...
```

我们所分析的漏洞位于`VBOXVHWACMD_TYPE_SURF_CREATE`中。当使用`VBOXVHWACMD_TYPE_SURF_CREATE`命令时，将会调用`VBoxVHWAImage::vhwaSurfaceCreate`，它可以创建一个新的`VBoxVHWASurfaceBase`对象。指向该`VBoxVHWASurfaceBase`对象的指针将存储在调用对象的`mSurfHandleTable`成员中，该成员只是由句柄索引的指针数组。

```
// src/VBox/Frontends/VirtualBox/src/VBoxFBOverlay.cpp:2287

int VBoxVHWAImage::vhwaSurfaceCreate(struct VBOXVHWACMD_SURF_CREATE RT_UNTRUSTED_VOLATILE_GUEST *pCmd)
`{`
...
    VBoxVHWASurfaceBase *surf = NULL;
...
        if (format.isValid())
        `{`
            surf = new VBoxVHWASurfaceBase(this,
                                           surfSize,
                                           primaryRect,
                                           QRect(0, 0, surfSize.width(), surfSize.height()),
                                           mViewport,
                                           format,
                                           pSrcBltCKey, pDstBltCKey, pSrcOverlayCKey, pDstOverlayCKey,
#ifdef VBOXVHWA_USE_TEXGROUP
                                           0,
#endif
                                           fFlags);
        `}`
...
        handle = mSurfHandleTable.put(surf);
        pCmd-&gt;SurfInfo.hSurf = (VBOXVHWA_SURFHANDLE)handle;
```

但是，当启用了某些命令标志，而没有创建新的`VBoxVHWASurfaceBase`对象时，会将`surf`设置为已经存在的`VBoxVHWASurfaceBase`对象。

```
// src/VBox/Frontends/VirtualBox/src/VBoxFBOverlay.cpp:2287

int VBoxVHWAImage::vhwaSurfaceCreate(struct VBOXVHWACMD_SURF_CREATE RT_UNTRUSTED_VOLATILE_GUEST *pCmd)
`{`
...
    VBoxVHWASurfaceBase *surf = NULL;
...
    if (pCmd-&gt;SurfInfo.surfCaps &amp; VBOXVHWA_SCAPS_PRIMARYSURFACE)
    `{`
        bNoPBO = true;
        bPrimary = true;
        VBoxVHWASurfaceBase *pVga = vgaSurface(); /* == mDisplay.getVGA() == mDisplay.mSurfVGA */
...
                        surf = pVga;
...
        handle = mSurfHandleTable.put(surf);
        pCmd-&gt;SurfInfo.hSurf = (VBOXVHWA_SURFHANDLE)handle;
```

当我们跟随这个代码路径时，发现`mSurfHandleTable`将会保存对`mDisplay`对象的`mSurfVGA`的引用。但是，这个`mSurfVGA`成员可以在其他功能实现期间（例如：调整大小的功能）被替换。虚拟机可以触发对屏幕大小的调整，在屏幕大小调整后，将会执行以下代码。

```
// src/VBox/Frontends/VirtualBox/src/VBoxFBOverlay.cpp:3752

void VBoxVHWAImage::resize(const VBoxFBSizeInfo &amp;size)
`{`
...
    VBoxVHWASurfaceBase *pDisplay = mDisplay.setVGA(NULL);
    if (pDisplay)
        delete pDisplay;
...
    pDisplay = new VBoxVHWASurfaceBase(this,
                                       dispSize,
                                       dispRect,
                                       dispRect,
                                       dispRect, /* we do not know viewport at the stage of precise, set as a
                                                    disp rect, it will be updated on repaint */
                                       format,
                                       NULL, NULL, NULL, NULL,
#ifdef VBOXVHWA_USE_TEXGROUP
                                       0,
#endif
                                       0 /* VBOXVHWAIMG_TYPE fFlags */);
```

尽管`mDisplay`成员的`mSurfVGA`已经释放，并使用新的分配进行更新，但是`mSurfHandleTable`仍然将保留指向已释放的旧`VBoxVHWASurfaceBase`对象的指针。这样将会产生一个“释放后使用”（UAF）的场景，因为其他VHWA命令（例如：VBOXVHWACMD_TYPE_SURF_OVERLAY_UPDATE）仍然可以通过其句柄访问这个释放后的指针，并进行各种操作。

```
// src/VBox/Frontends/VirtualBox/src/VBoxFBOverlay.cpp:2823

int VBoxVHWAImage::vhwaSurfaceOverlayUpdate(struct VBOXVHWACMD_SURF_OVERLAY_UPDATE RT_UNTRUSTED_VOLATILE_GUEST *pCmd)
`{`
    VBoxVHWASurfaceBase *pSrcSurf = handle2Surface(pCmd-&gt;u.in.hSrcSurf); /*pSrcSurf = freed chunk*/
    AssertReturn(pSrcSurf, VERR_INVALID_PARAMETER);
    VBoxVHWASurfList *pList = pSrcSurf-&gt;getComplexList();
...
```

如果要从虚拟机内核驱动程序执行调整大小的操作，可以使用另一个VBVA命令来替代VHWA命令（`VBVA_VHWA_CMD`）。`VBVA_INFO_SCREEN`命令会以调用调整大小为结束，从而让我们能够触发UAF。

```
// src/VBox/Devices/Graphics/DevVGA_VBVA.cpp:2444

static DECLCALLBACK(int) vbvaChannelHandler(void *pvHandler, uint16_t u16ChannelInfo,
                                            void RT_UNTRUSTED_VOLATILE_GUEST *pvBuffer, HGSMISIZE cbBuffer)
`{`
...
    switch (u16ChannelInfo)
    `{`
...
        case VBVA_INFO_SCREEN:
            rc = VERR_INVALID_PARAMETER;
            if (cbBuffer &gt;= sizeof(VBVAINFOSCREEN))
                rc = vbvaInfoScreen(pThisCC, (VBVAINFOSCREEN RT_UNTRUSTED_VOLATILE_GUEST *)pvBuffer);
            break;
```

```
vbvaInfoScreen
 |_ vbvaResize
     |_ pThisCC-&gt;pDrv-&gt;pfnVBVAResize = Display::i_displayVBVAResize
```



## 五、漏洞利用

### <a class="reference-link" name="5.1%20%E5%A0%86%E5%96%B7%E5%B0%84"></a>5.1 堆喷射

考虑到我们发现的UAF漏洞的性质，漏洞利用的第一步需要通过另一个受控制的分配来回收释放后的分配。由于我们的宿主机是Windows 10计算机，所以堆将会经过低分片堆（LFH）和各种各样令人困惑的机制处理。我们有一种相对可靠的方式来进行回收分配，就是在VirtualBox代码中找到一个原语，该原语允许虚拟机具有与`VBoxVHWASurfaceBase`相同大小的分配，同时还允许我们控制分配的内容。最后使用的一个原语是`drvNATNetworkUp_AllocBuf`，它在发送以太网帧时被调用。我在这里直接使用了导师编写的用于堆喷射的代码，从而节约了用来理解以太网协议的很多时间。要了解该原语，我们需要为其分配16字节对齐的大小，用于存储来自虚拟机的数据。下图说明了堆喷射的用法：

[![](https://p0.ssl.qhimg.com/t01b198a328ed51e93b.png)](https://p0.ssl.qhimg.com/t01b198a328ed51e93b.png)

### <a class="reference-link" name="5.2%20rip%E6%8E%A7%E5%88%B6"></a>5.2 rip控制

通过堆喷射，我们可以控制损坏的`VBoxVHWASurfaceBase`对象的`vtable`成员。那么，我们如何利用它来实现rip控制呢？<br>
在检查`VBoxVHWASurfaceBase`的有效`vtable`时，我们注意到，其中唯一包含的条目是指向向量删除析构函数的函数指针。因此，一旦我们知道可以写入的内存区域地址，就可以编写一个伪造的`vtable`，以替换该`vtable`成员，使其指向受控制的`vtable`，并通过`VBOXVHWACMD_TYPE_SURF_DESTROY` VHWA命令删除`VBoxVHWASurfaceBase`对象，从而是我们可以控制指令指针`rip`。

[![](https://p1.ssl.qhimg.com/t01d185a91632be95c9.png)](https://p1.ssl.qhimg.com/t01d185a91632be95c9.png)

目前，我们必须先实现信息泄露，然后才能继续实现漏洞利用。

### <a class="reference-link" name="5.3%20%E8%8E%B7%E5%8F%96%E4%BF%A1%E6%81%AF%E6%B3%84%E9%9C%B2"></a>5.3 获取信息泄露

我花费了很长的时间来查看各种VHWA命令，以寻找是否可能让某些指针泄露回虚拟机的VRAM。最后，我发现这是一个死胡同。经过一些尝试，anhdaden带我走上了寻找信息泄露的正确道路。这种技术基于虚拟机能够在内存中控制的VRAM MMIO缓冲区（如前所述）。我的虚拟机配置为256MB视频内存，VRAM缓冲区的大小已经达到了0x10000000字节。有了如此巨大的空间，我们就可以猜测宿主机中该缓冲区的虚拟地址了。在重新启动几次虚拟机后，我注意到缓冲区分配在如下的几个地址上：

```
start             end
0x00000000ACB0000-0x00000001ACB0000
0x00000000AEE0000-0x00000001AEE0000
0x00000000B4F0000-0x00000001B4F0000
0x00000000B1A0000-0x00000001B1A0000
0x00000000ADE0000-0x00000001ADE0000
0x00000000A670000-0x00000001A670000
0x00000000B0B0000-0x00000001B0B0000
0x00000000AC10000-0x00000001AC10000
```

这个范围非常巨大，即使我们猜测地址类似于0x00000000C000000，但它也仍然位于VRAM缓冲区内。有了这些信息后，我们就可以构建更好的原语来泄露DLL地址，并可能形成任意读/写原语。

但是，仍然有一个小问题，尽管我们知道可控的VRAM缓冲区中可能存在一个类似于0x00000000C000000的任意地址，但是我们不知道这个地址与缓冲区起始位置的偏移量。幸运的是，有一种方法可以解决这个问题。

我们来看看`VBoxVHWAImage::vhwaSurfaceOverlayUpdate`函数，该函数实现了`VBOXVHWACMD_TYPE_SURF_OVERLAY_UPDATE`命令。由于源代码具有许多实际上内联的函数调用，同时还包括编译后已优化的其他宏，因此我发现，使用反编译器来检查函数会更加容易一些。

```
// src/VBox/Frontends/VirtualBox/src/VBoxFBOverlay.cpp:2823

signed __int64 __fastcall VBoxVHWAImage::vhwaSurfaceOverlayUpdate(__int64 _this, uint8_t *_pCmd)
`{`
...
  pSrcSurf = *(VBoxVHWASurfaceBase **)(*(_QWORD *)(_this + 72) + 8i64 * (unsigned int)*((_QWORD *)_pCmd + 4));
...
  pList = (__int64 ***)pSrcSurf-&gt;mComplexList;              /* [1] */
...
  if ( _bittest(&amp;v24, 9u) )
  `{`
...
  `}`
  else
  `{`
...
    if ( _bittest(&amp;v25, 0xEu) )
      *(_QWORD *)(pList + 0x18) = pSrcSurf;                 /* [2] */
...
`}`
```

查看其中的[1]行，`pList`是从`VBoxVHWASurfaceBase`对象`pSrcSurf`中获取的指针。通过之前的堆喷射，我们可以控制`pList`的值。

随后，在[2]行中，取消引用`pList`，并将偏移量为0x18的成员设置为指向`pSrcSurf`的指针。如果我们可以将`pList`设置为指向VRAM缓冲区，那么我们就可以从堆中泄露指针！此外，如果`pList = 0x00000000C000000`，则指针将放置在`0x00000000C000018`处，我们可以扫描内存中的这一更改，并根据VRAM中指针的索引来计算VRAM缓冲区的基址。

```
// src/VBox/Frontends/VirtualBox/src/VBoxFBOverlay.cpp:2823

signed __int64 __fastcall VBoxVHWAImage::vhwaSurfaceOverlayUpdate(__int64 _this, uint8_t *_pCmd)
`{`
...
  for ( i = **(__int64 ***)pList; i != *(__int64 **)pList; i = (__int64 *)*i )
    VBoxVHWAImage::vhwaDoSurfaceOverlayUpdate(this, pDstSurf, (VBoxVHWASurfaceBase *)i[2], pCmd);
...
```

值得注意的是，`pList`的第一个成员应该是指向单链列表的有效指针，否则如上面的代码所示，虚拟机在遍历时会发生崩溃。因此，地址`0x00000000C000000`应该包含一个有效的链表指针。在不知道VRAM缓冲区基址的情况下，解决这一问题的简单方法是在VRAM上喷射`0x00000000C000000`，这样就可以可靠地防止崩溃的发生。

```
uint64_t* v = (uint64_t*)&amp;vram[0x1000];
    for (int i = 0; i &lt; 0x6000000 / 8; i++) `{`
        v[i] = 0x00000000C000000;
    `}`
```

### <a class="reference-link" name="5.4%20DLL%E4%BF%A1%E6%81%AF%E6%B3%84%E9%9C%B2"></a>5.4 DLL信息泄露

至此，我们已经知道了VRAM缓冲区的基址，并且也将其泄露到堆中。仅凭这些信息，我们仍然无法将rip更改为有意义的地址。我们需要创建一个DLL信息泄露，让我们能够进入到ROP链中，并执行一些有意义的代码。为实现这一目标，我再次使用了`VBOXVHWACMD_TYPE_SURF_OVERLAY_UPDATE`。

```
// src/VBox/Frontends/VirtualBox/src/VBoxFBOverlay.cpp:2823

signed __int64 __fastcall VBoxVHWAImage::vhwaSurfaceOverlayUpdate(__int64 _this, uint8_t *_pCmd)
`{`
...
  for ( i = **(__int64 ***)pList; i != *(__int64 **)pList; i = (__int64 *)*i )
    VBoxVHWAImage::vhwaDoSurfaceOverlayUpdate(this, pDstSurf, (VBoxVHWASurfaceBase *)i[2], pCmd);
...
```

如前所示，`VBoxVHWAImage::vhwaSurfaceOverlayUpdate`遍历`pList`的第一个成员指向的单链表（由我们控制），并在每个链表节点的0x10偏移量处的`VBoxVHWASurfaceBase`指针上调用`VBoxVHWAImage::vhwaDoSurfaceOverlayUpdate`。

```
__int64 __fastcall VBoxVHWAImage::vhwaDoSurfaceOverlayUpdate(__int64 _this, VBoxVHWASurfaceBase *_pDstSurf, VBoxVHWASurfaceBase *_pSrcSurf, _DWORD *pCmd)
`{`
...
  if ( _bittest(&amp;v9, 0xCu) )
  `{`
    result = _pSrcSurf-&gt;field_90;
    _pSrcSurf-&gt;field_78 = result;
  `}`
...
`}`
```

在`VBoxVHWAImage::vhwaDoSurfaceOverlayUpdate`中，实现了上述操作，在这里我们控制指针`_pSrcSurf`的值。通过上面的代码片段，我们可以将一个值从某个内存地址复制到另一个较低的内存地址。但这对我们有什么用呢？

[![](https://p4.ssl.qhimg.com/t01243860d5e5621e24.png)](https://p4.ssl.qhimg.com/t01243860d5e5621e24.png)

在阅读[@_niklasb](https://github.com/_niklasb)的其他幻灯片时，他提到在Windows宿主机上，与VRAM缓冲区直接相邻的内存区域是另一个包含有关VRAM缓冲区本身的某些元数据的区域。我们可以在调试器中验证上述发现，实际上，内存区域已设置为具有读/写权限。将这一点与我们刚刚讨论过的原语结合在一起，我们就可以将“VRam”指针（指向`VBoxDD.dll`的指针）重复复制到较低的地址。由于这个元数据与虚拟机可读取的VRAM缓冲区相邻，因此我们只需将DLL指针“拖动”到页边界上，就可以直接进入到我们的VRAM中。然后，我们就能轻松地从内存中读取该指针！<br>
实现的过程要稍微复杂一些，但是总体思路是在VRAM内形成一个有效的链表，该链表针对递减的地址反复调用`VBoxVHWAImage::vhwaDoSurfaceOverlayUpdate`。

[![](https://p1.ssl.qhimg.com/t019cd949c16e0ff463.png)](https://p1.ssl.qhimg.com/t019cd949c16e0ff463.png)

另外，这种技术非常适用于内存转储。

[![](https://p4.ssl.qhimg.com/t015944abe3cc125cad.gif)](https://p4.ssl.qhimg.com/t015944abe3cc125cad.gif)

如果这样就结束任务，那么破坏元数据的多余指针将会导致宿主机产生蓝屏（BSOD）。因此，应该重复使用相同的技术，将多余的指针归零。

### <a class="reference-link" name="5.5%20rop2win"></a>5.5 rop2win

有了DLL泄露后，我们现在就可以编写一个ROP链来调用`VirtualAlloc`，分配一个RWX区域，将我们的Shellcode复制到该区域并跳转。为了从析构函数调用转到我们的ROP链，我们可以将`rip`设置为错误值，从而导致崩溃，并检查寄存器的状态。在这种情况下，`rax`的值指向我们的VRAM缓冲区。因此，可以使用以下小工具来转到我们的ROP链。

```
In 6.1.2 r135662 (Release ver.)

0x0000000180042b3e: xchg eax, esp; ror byte ptr [rax - 0x75], 0x5c; and al, 0x30; add rsp, 0x20; pop rdi; ret;
```

这样一来，我们就完成了全部的漏洞利用链！由于过程中破坏了元数据，因此虚拟机将无法继续正常运行，但我们已经可以成功弹出了计算器。

演示视频：[https://starlabs.sg/blog/2020/VBoxVHWASurfaceBase-demo.mp4](https://starlabs.sg/blog/2020/VBoxVHWASurfaceBase-demo.mp4)



## 六、参考

[1] [https://googleprojectzero.blogspot.com/2017/08/bypassing-virtualbox-process-hardening.html](https://googleprojectzero.blogspot.com/2017/08/bypassing-virtualbox-process-hardening.html)<br>
[2] [https://www.virtualbox.org/wiki/Windows%20build%20instructions](https://www.virtualbox.org/wiki/Windows%20build%20instructions)<br>
[3] [https://github.com/phoenhex/files/blob/master/slides/thinking_outside_the_virtualbox.pdf](https://github.com/phoenhex/files/blob/master/slides/thinking_outside_the_virtualbox.pdf)<br>
[4] [http://www.catch22.net/tuts/kernel1.asp](http://www.catch22.net/tuts/kernel1.asp)<br>
[5] [https://www.voidsecurity.in/2018/08/from-compiler-optimization-to-code.html](https://www.voidsecurity.in/2018/08/from-compiler-optimization-to-code.html)<br>
[6] [https://github.com/phoenhex/files/blob/master/slides/unboxing_your_virtualboxes.pdf](https://github.com/phoenhex/files/blob/master/slides/unboxing_your_virtualboxes.pdf)
