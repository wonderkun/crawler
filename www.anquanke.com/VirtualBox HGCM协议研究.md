> 原文链接: https://www.anquanke.com//post/id/238643 


# VirtualBox HGCM协议研究


                                阅读量   
                                **171255**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0169ca5f34f2306385.png)](https://p1.ssl.qhimg.com/t0169ca5f34f2306385.png)



## 0x00 前言

最近开始研究VirtualBox虚拟机逃逸漏洞，针对于VirtualBox的虚拟机逃逸，我们重点关注它的`HGCM（host-guest communication mechanism）协议`，本文将结合源码分析和动态调试来分析此协议，最后我们还将实现一个HGCM协议的调用库。



## 0x01 VirtualBox 通信协议

### <a class="reference-link" name="%E5%BC%95%E8%A8%80"></a>引言

VirtualBox中一个名为`HGCM`的协议相当于一个`RPC`，其作用是可以让Guest里的程序通过接口调用`Host`中的服务程序中的函数。该协议的接口封装在`vboxguest`驱动程序中。

在Guest系统中，通过`VBoxGuestAdditions.iso`安装了一个名为`vboxguest`的驱动程序，该驱动程序主要就是提供接口给`Guset`系统里的程序，用于与`Host`主机进行通信。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a3d2f1624c2176a1.png)

除了`vboxguest`驱动，Guset还安装有`vboxsf`驱动和`vboxvideo`，其中`vboxsf`仍然使用的是`vboxguest`的接口，而`vboxvideo`则是`VirtualBox`虚拟出来的显示设备的驱动程序，独立于前面两个驱动。由此可见，Guest与Host之前的通信关键在于`vboxguest`驱动，因此，我们的研究将从该驱动出发。

该驱动源码位于`src\VBox\Additions\common\VBoxGuest`目录，以Linux系统为例，其源文件为`VBoxGuest-linux.c`，首先从`file_operations`结构体可以看到有哪些操作

```
static struct file_operations   g_FileOpsUser =
`{`
    owner:          THIS_MODULE,
    open:           vgdrvLinuxOpen,
    release:        vgdrvLinuxRelease,
#ifdef HAVE_UNLOCKED_IOCTL
    unlocked_ioctl: vgdrvLinuxIOCtl,
#else
    ioctl:          vgdrvLinuxIOCtl,
#endif
`}`;
```

### <a class="reference-link" name="GUEST%20IOCTL"></a>GUEST IOCTL

可以看到定义了`vgdrvLinuxIOCtl`用于进行接口的访问，跟踪该函数，可以发现其调用了`vgdrvLinuxIOCtlSlow`函数，

```
static int vgdrvLinuxIOCtlSlow(struct file *pFilp, unsigned int uCmd, unsigned long ulArg, PVBOXGUESTSESSION pSession)
`{`
    int                 rc;
    VBGLREQHDR          Hdr;
    PVBGLREQHDR         pHdr;
    uint32_t            cbBuf;

    Log6(("vgdrvLinuxIOCtlSlow: pFilp=%p uCmd=%#x ulArg=%p pid=%d/%d\n", pFilp, uCmd, (void *)ulArg, RTProcSelf(), current-&gt;pid));

    /*
     * Read the header.
     */
    if (RT_FAILURE(RTR0MemUserCopyFrom(&amp;Hdr, ulArg, sizeof(Hdr))))
    `{`
        Log(("vgdrvLinuxIOCtlSlow: copy_from_user(,%#lx,) failed; uCmd=%#x\n", ulArg, uCmd));
        return -EFAULT;
    `}`
    if (RT_UNLIKELY(Hdr.uVersion != VBGLREQHDR_VERSION))
    `{`
        Log(("vgdrvLinuxIOCtlSlow: bad header version %#x; uCmd=%#x\n", Hdr.uVersion, uCmd));
        return -EINVAL;
    `}`

    /*
     * Buffer the request.
     * Note! The header is revalidated by the common code.
     */
    cbBuf = RT_MAX(Hdr.cbIn, Hdr.cbOut);
    if (RT_UNLIKELY(cbBuf &gt; _1M*16))
    `{`
        Log(("vgdrvLinuxIOCtlSlow: too big cbBuf=%#x; uCmd=%#x\n", cbBuf, uCmd));
        return -E2BIG;
    `}`
    if (RT_UNLIKELY(   Hdr.cbIn &lt; sizeof(Hdr)
                    || (cbBuf != _IOC_SIZE(uCmd) &amp;&amp; _IOC_SIZE(uCmd) != 0)))
    `{`
        Log(("vgdrvLinuxIOCtlSlow: bad ioctl cbBuf=%#x _IOC_SIZE=%#x; uCmd=%#x\n", cbBuf, _IOC_SIZE(uCmd), uCmd));
        return -EINVAL;
    `}`
    pHdr = RTMemAlloc(cbBuf);
    if (RT_UNLIKELY(!pHdr))
    `{`
        LogRel(("vgdrvLinuxIOCtlSlow: failed to allocate buffer of %d bytes for uCmd=%#x\n", cbBuf, uCmd));
        return -ENOMEM;
    `}`
    if (RT_FAILURE(RTR0MemUserCopyFrom(pHdr, ulArg, Hdr.cbIn)))
    `{`
        Log(("vgdrvLinuxIOCtlSlow: copy_from_user(,%#lx, %#x) failed; uCmd=%#x\n", ulArg, Hdr.cbIn, uCmd));
        RTMemFree(pHdr);
        return -EFAULT;
    `}`
    if (Hdr.cbIn &lt; cbBuf)
        RT_BZERO((uint8_t *)pHdr + Hdr.cbIn, cbBuf - Hdr.cbIn);

    /*
     * Process the IOCtl.
     */
    rc = VGDrvCommonIoCtl(uCmd, &amp;g_DevExt, pSession, pHdr, cbBuf);
    .........................................................
```

可以看到，函数中首先将用户传入的数据转为`VBGLREQHDR          Hdr;`结构体，该结构体定义如下

```
typedef struct VBGLREQHDR
`{`
    /** IN: The request input size, and output size if cbOut is zero.
     * @sa VMMDevRequestHeader::size  */
    uint32_t        cbIn;
    /** IN: Structure version (VBGLREQHDR_VERSION)
     * @sa VMMDevRequestHeader::version */
    uint32_t        uVersion;
    /** IN: The VMMDev request type, set to VBGLREQHDR_TYPE_DEFAULT unless this is a
     * kind of VMMDev request.
     * @sa VMMDevRequestType, VMMDevRequestHeader::requestType */
    uint32_t        uType;
    /** OUT: The VBox status code of the operation, out direction only. */
    int32_t         rc;
    /** IN: The output size.  This is optional - set to zero to use cbIn as the
     * output size. */
    uint32_t        cbOut;
    /** Reserved / filled in by kernel, MBZ.
     * @sa VMMDevRequestHeader::fRequestor */
    uint32_t        uReserved;
`}` VBGLREQHDR;
```

然后判断一些信息是否符合要求，这里，归纳如下

```
Hdr.uVersion = VBGLREQHDR_VERSION
Hdr.cbIn和Hdr.cbOut不能大于_1M*16
```

检查通过后，执行`rc = VGDrvCommonIoCtl(uCmd, &amp;g_DevExt, pSession, pHdr, cbBuf);`，进入`VGDrvCommonIoCtl`函数，该函数位于`VBoxGuest.cpp`源文件

```
int VGDrvCommonIoCtl(uintptr_t iFunction, PVBOXGUESTDEVEXT pDevExt, PVBOXGUESTSESSION pSession, PVBGLREQHDR pReqHdr, size_t cbReq)
`{`
    uintptr_t const iFunctionStripped = VBGL_IOCTL_CODE_STRIPPED(iFunction);
    int rc;
...............................................................
   /*
     * Deal with variably sized requests first.
     */
    rc = VINF_SUCCESS;
    if (   iFunctionStripped == VBGL_IOCTL_CODE_STRIPPED(VBGL_IOCTL_VMMDEV_REQUEST(0))
        || iFunctionStripped == VBGL_IOCTL_CODE_STRIPPED(VBGL_IOCTL_VMMDEV_REQUEST_BIG) )
    `{`
        ........
    `}`
    else if (RT_LIKELY(pReqHdr-&gt;uType == VBGLREQHDR_TYPE_DEFAULT))
    `{`
        if (iFunctionStripped == VBGL_IOCTL_CODE_STRIPPED(VBGL_IOCTL_LOG(0)))
        `{`
            ........
        `}`
#ifdef VBOX_WITH_HGCM
        else if (iFunction == VBGL_IOCTL_IDC_HGCM_FAST_CALL) /* (is variable size, but we don't bother encoding it) */
        `{`
            .........
        `}`
        else if (   iFunctionStripped == VBGL_IOCTL_CODE_STRIPPED(VBGL_IOCTL_HGCM_CALL(0))
# if ARCH_BITS == 64
                 || iFunctionStripped == VBGL_IOCTL_CODE_STRIPPED(VBGL_IOCTL_HGCM_CALL_32(0))
# endif
                )
        `{`
            ...........
        `}`
        else if (iFunctionStripped == VBGL_IOCTL_CODE_STRIPPED(VBGL_IOCTL_HGCM_CALL_WITH_USER_DATA(0)))
        `{`
            ..........
        `}`
#endif /* VBOX_WITH_HGCM */
        else
        `{`
            switch (iFunction)
            `{`
```

由于我们想要进入HGCM相关的处理分支里，因此，想要满足`pReqHdr-&gt;uType == VBGLREQHDR_TYPE_DEFAULT`

```
switch (iFunction)
            `{`
............................................
#ifdef VBOX_WITH_HGCM
                case VBGL_IOCTL_HGCM_CONNECT:
                    REQ_CHECK_SIZES(VBGL_IOCTL_HGCM_CONNECT);
                    pReqHdr-&gt;rc = vgdrvIoCtl_HGCMConnect(pDevExt, pSession, (PVBGLIOCHGCMCONNECT)pReqHdr);
                    break;

                case VBGL_IOCTL_HGCM_DISCONNECT:
                    REQ_CHECK_SIZES(VBGL_IOCTL_HGCM_DISCONNECT);
                    pReqHdr-&gt;rc = vgdrvIoCtl_HGCMDisconnect(pDevExt, pSession, (PVBGLIOCHGCMDISCONNECT)pReqHdr);
                    break;
#endif
```

这里的`iFunction`值就是我们在ioctl中传入的cmd，当cmd为`VBGL_IOCTL_HGCM_CONNECT`或者`VBGL_IOCTL_HGCM_DISCONNECT`时，可以建立或者断开一个`HGCM`服务。在一般情况下，使用HGCM调用Host中的服务时，要经过三个步骤`VBGL_IOCTL_HGCM_CONNECT`-&gt;`VBGL_IOCTL_HGCM_CALL`-&gt;`VBGL_IOCTL_HGCM_DISCONNECT`，即打开服务-&gt;调用函数-&gt;关闭服务。可以在`src\VBox\HostServices`目录下看到这些服务以及它们的源码

```
src\VBox\HostServices
    DragAndDrop
    GuestControl
    GuestProperties
    HostChannel
    SharedClipboard
    SharedFolders
    SharedOpenGL
```

从这些服务名大致能知道它们的作用，其中`SharedClipboard`用于在Host和Guest之间共享`粘贴板`，`SharedFolders`用于共享`文件夹`，而`SharedOpenGL`用于`3D图形加速`。<br>
继续分析HGCM服务的调用

```
pReqHdr-&gt;rc = vgdrvIoCtl_HGCMConnect(pDevExt, pSession, (PVBGLIOCHGCMCONNECT)pReqHdr);
```

可以知道此时将`pReqHdr`这个`VBGLREQHDR`结构体指针强制转换为`VBGLIOCHGCMCONNECT`结构体指针，该结构体定义如下

```
typedef struct VBGLIOCHGCMCONNECT
`{`
    /** The header. */
    VBGLREQHDR                  Hdr;
    union
    `{`
        struct
        `{`
            HGCMServiceLocation Loc;
        `}` In;
        struct
        `{`
            uint32_t            idClient;
        `}` Out;
    `}` u;
`}` VBGLIOCHGCMCONNECT, RT_FAR *PVBGLIOCHGCMCONNECT;

/**
 * HGCM service location.
 * @ingroup grp_vmmdev_req
 */
typedef struct HGCMSERVICELOCATION
`{`
    /** Type of the location. */
    HGCMServiceLocationType type;

    union
    `{`
        HGCMServiceLocationHost host;
    `}` u;
`}` HGCMServiceLocation;

typedef enum
`{`
    VMMDevHGCMLoc_Invalid    = 0,
    VMMDevHGCMLoc_LocalHost  = 1,
    VMMDevHGCMLoc_LocalHost_Existing = 2,
    VMMDevHGCMLoc_SizeHack   = 0x7fffffff
`}` HGCMServiceLocationType;

/**
 * HGCM host service location.
 * @ingroup grp_vmmdev_req
 */
typedef struct
`{`
    char achName[128]; /**&lt; This is really szName. */
`}` HGCMServiceLocationHost;
```

### <a class="reference-link" name="VBGL_IOCTL_HGCM_CONNECT"></a>VBGL_IOCTL_HGCM_CONNECT

#### <a class="reference-link" name="VbglR0HGCMInternalConnect"></a>VbglR0HGCMInternalConnect

进入`vgdrvIoCtl_HGCMConnect`函数,

```
static int vgdrvIoCtl_HGCMConnect(PVBOXGUESTDEVEXT pDevExt, PVBOXGUESTSESSION pSession, PVBGLIOCHGCMCONNECT pInfo)
`{`
    int rc;
    HGCMCLIENTID idClient = 0;

    /*
     * The VbglHGCMConnect call will invoke the callback if the HGCM
     * call is performed in an ASYNC fashion. The function is not able
     * to deal with cancelled requests.
     */
    Log(("VBOXGUEST_IOCTL_HGCM_CONNECT: %.128s\n",
         pInfo-&gt;u.In.Loc.type == VMMDevHGCMLoc_LocalHost || pInfo-&gt;u.In.Loc.type == VMMDevHGCMLoc_LocalHost_Existing
         ? pInfo-&gt;u.In.Loc.u.host.achName : "&lt;not local host&gt;"));

    rc = VbglR0HGCMInternalConnect(&amp;pInfo-&gt;u.In.Loc, pSession-&gt;fRequestor, &amp;idClient,
                                   vgdrvHgcmAsyncWaitCallback, pDevExt, RT_INDEFINITE_WAIT);
    Log(("VBOXGUEST_IOCTL_HGCM_CONNECT: idClient=%RX32 (rc=%Rrc)\n", idClient, rc));
    if (RT_SUCCESS(rc))
    `{`
        /*
         * Append the client id to the client id table.
         * If the table has somehow become filled up, we'll disconnect the session.
         */
        unsigned i;
        RTSpinlockAcquire(pDevExt-&gt;SessionSpinlock);
        for (i = 0; i &lt; RT_ELEMENTS(pSession-&gt;aHGCMClientIds); i++)
            if (!pSession-&gt;aHGCMClientIds[i])
            `{`
                pSession-&gt;aHGCMClientIds[i] = idClient;
                break;
            `}`
        RTSpinlockRelease(pDevExt-&gt;SessionSpinlock);
        if (i &gt;= RT_ELEMENTS(pSession-&gt;aHGCMClientIds))
        `{`
            LogRelMax(32, ("VBOXGUEST_IOCTL_HGCM_CONNECT: too many HGCMConnect calls for one session!\n"));
            VbglR0HGCMInternalDisconnect(idClient, pSession-&gt;fRequestor, vgdrvHgcmAsyncWaitCallback, pDevExt, RT_INDEFINITE_WAIT);

            pInfo-&gt;u.Out.idClient = 0;
            return VERR_TOO_MANY_OPEN_FILES;
        `}`
    `}`
    pInfo-&gt;u.Out.idClient = idClient;
    return rc;
`}`
```

从该函数可以看出，它将调用`VbglR0HGCMInternalConnect`函数，然后返回一个`idClient`即客户端号，并将该号码缓存到`pSession-&gt;aHGCMClientIds`数组中，同时将其返回给Guest中的请求程序。我们继续跟进`VbglR0HGCMInternalConnect`函数

```
DECLR0VBGL(int) VbglR0HGCMInternalConnect(HGCMServiceLocation const *pLoc, uint32_t fRequestor, HGCMCLIENTID *pidClient,
                                          PFNVBGLHGCMCALLBACK pfnAsyncCallback, void *pvAsyncData, uint32_t u32AsyncData)
`{`
    int rc;
    if (   RT_VALID_PTR(pLoc)
        &amp;&amp; RT_VALID_PTR(pidClient)
        &amp;&amp; RT_VALID_PTR(pfnAsyncCallback))
    `{`
        /* Allocate request */
        VMMDevHGCMConnect *pHGCMConnect = NULL;
        rc = VbglR0GRAlloc((VMMDevRequestHeader **)&amp;pHGCMConnect, sizeof(VMMDevHGCMConnect), VMMDevReq_HGCMConnect);
        if (RT_SUCCESS(rc))
        `{`
            /* Initialize request memory */
            pHGCMConnect-&gt;header.header.fRequestor = fRequestor;

            pHGCMConnect-&gt;header.fu32Flags = 0;

            memcpy(&amp;pHGCMConnect-&gt;loc, pLoc, sizeof(pHGCMConnect-&gt;loc));
            pHGCMConnect-&gt;u32ClientID = 0;

            /* Issue request */
            rc = VbglR0GRPerform (&amp;pHGCMConnect-&gt;header.header);
            if (RT_SUCCESS(rc))
            `{`
                /* Check if host decides to process the request asynchronously. */
                if (rc == VINF_HGCM_ASYNC_EXECUTE)
                `{`
                    /* Wait for request completion interrupt notification from host */
                    pfnAsyncCallback(&amp;pHGCMConnect-&gt;header, pvAsyncData, u32AsyncData);
                `}`

                rc = pHGCMConnect-&gt;header.result;
                if (RT_SUCCESS(rc))
                    *pidClient = pHGCMConnect-&gt;u32ClientID;
            `}`
            VbglR0GRFree(&amp;pHGCMConnect-&gt;header.header);
        `}`
    `}`
    else
        rc = VERR_INVALID_PARAMETER;
    return rc;
`}`
```

该函数主要是新建了一个结构体，并从最开始`ioctl`操作中传入的结构体中复制`HGCMServiceLocation`结构体数据，然后传入`VbglR0GRPerform`函数。<br>
VbglR0GRPerform函数实际上就是一个对`in`和`out`汇编指令的封装，操作IO接口，可以知道，其请求的端口地址为`g_vbgldata.portVMMDev + VMMDEV_PORT_OFF_REQUEST`

#### <a class="reference-link" name="VbglR0GRPerform"></a>VbglR0GRPerform

```
DECLR0VBGL(int) VbglR0GRPerform(VMMDevRequestHeader *pReq)
`{`
    int rc = vbglR0Enter();
    if (RT_SUCCESS(rc))
    `{`
        if (pReq)
        `{`
            RTCCPHYS PhysAddr = VbglR0PhysHeapGetPhysAddr(pReq);
            if (   PhysAddr != 0
                &amp;&amp; PhysAddr &lt; _4G) /* Port IO is 32 bit. */
            `{`
                ASMOutU32(g_vbgldata.portVMMDev + VMMDEV_PORT_OFF_REQUEST, (uint32_t)PhysAddr);
                /* Make the compiler aware that the host has changed memory. */
                ASMCompilerBarrier();
                rc = pReq-&gt;rc;
            `}`
            else
                rc = VERR_VBGL_INVALID_ADDR;
        `}`
        else
            rc = VERR_INVALID_PARAMETER;
    `}`
    return rc;
`}`
```

通过查找`VMMDEV_PORT_OFF_REQUEST`的引用，可以发现`src\VBox\Devices\VMMDev\VMMDev.cpp`文件，可以知道这是VirtualBox虚拟出来的IO设备,在`vmmdevIOPortRegionMap`函数中，通过`PDMDevHlpIOPortRegister`函数为`VMMDEV_PORT_OFF_REQUEST`IO端口注册了一个处理函数。

```
static DECLCALLBACK(int) vmmdevIOPortRegionMap(PPDMDEVINS pDevIns, PPDMPCIDEV pPciDev, uint32_t iRegion,
                                               RTGCPHYS GCPhysAddress, RTGCPHYS cb, PCIADDRESSSPACE enmType)
`{`
    LogFlow(("vmmdevIOPortRegionMap: iRegion=%d GCPhysAddress=%RGp cb=%RGp enmType=%d\n", iRegion, GCPhysAddress, cb, enmType));
    RT_NOREF3(iRegion, cb, enmType);
    PVMMDEV pThis = RT_FROM_MEMBER(pPciDev, VMMDEV, PciDev);

    Assert(enmType == PCI_ADDRESS_SPACE_IO);
    Assert(iRegion == 0);
    AssertMsg(RT_ALIGN(GCPhysAddress, 8) == GCPhysAddress, ("Expected 8 byte alignment. GCPhysAddress=%#x\n", GCPhysAddress));

    /*
     * Register our port IO handlers.
     */
    int rc = PDMDevHlpIOPortRegister(pDevIns, (RTIOPORT)GCPhysAddress + VMMDEV_PORT_OFF_REQUEST, 1,
                                     pThis, vmmdevRequestHandler, NULL, NULL, NULL, "VMMDev Request Handler");
```

因此我们在Guset中的`ASMOutU32(g_vbgldata.portVMMDev + VMMDEV_PORT_OFF_REQUEST, (uint32_t)PhysAddr);`请求最终被传入到虚拟设备中的`vmmdevRequestHandler`函数中进行处理。

#### <a class="reference-link" name="vmmdevRequestHandler"></a>vmmdevRequestHandler

```
/**
 * @callback_method_impl`{`FNIOMIOPORTOUT,
 * Port I/O write andler for the generic request interface.`}`
 */
static DECLCALLBACK(int) vmmdevRequestHandler(PPDMDEVINS pDevIns, void *pvUser, RTIOPORT Port, uint32_t u32, unsigned cb)
`{`
    uint64_t tsArrival;
    STAM_GET_TS(tsArrival);

    RT_NOREF2(Port, cb);
    PVMMDEV pThis = (VMMDevState *)pvUser;

    /*
     * The caller has passed the guest context physical address of the request
     * structure. We'll copy all of it into a heap buffer eventually, but we
     * will have to start off with the header.
     */
    VMMDevRequestHeader requestHeader;
    RT_ZERO(requestHeader);
    PDMDevHlpPhysRead(pDevIns, (RTGCPHYS)u32, &amp;requestHeader, sizeof(requestHeader));

.........................................................
            if (pRequestHeader)
            `{`
                memcpy(pRequestHeader, &amp;requestHeader, sizeof(VMMDevRequestHeader));

                /* Try lock the request if it's a HGCM call and not crossing a page boundrary.
                   Saves on PGM interaction. */
                VMMDEVREQLOCK   Lock   = `{` NULL, `{` 0, NULL `}` `}`;
                PVMMDEVREQLOCK  pLock  = NULL;
                size_t          cbLeft = requestHeader.size - sizeof(VMMDevRequestHeader);
                if (cbLeft)
                `{`
                    ...............................
                `}`

                /*
                 * Feed buffered request thru the dispatcher.
                 */
                uint32_t fPostOptimize = 0;
                PDMCritSectEnter(&amp;pThis-&gt;CritSect, VERR_IGNORED);
                rcRet = vmmdevReqDispatcher(pThis, pRequestHeader, u32, tsArrival, &amp;fPostOptimize, &amp;pLock);
                PDMCritSectLeave(&amp;pThis-&gt;CritSect);
```

请求将被传入`vmmdevReqDispatcher`函数进行调度

```
/**
 * Dispatch the request to the appropriate handler function.
 *
 * @returns Port I/O handler exit code.
 * @param   pThis           The VMM device instance data.
 * @param   pReqHdr         The request header (cached in host memory).
 * @param   GCPhysReqHdr    The guest physical address of the request (for
 *                          HGCM).
 * @param   tsArrival       The STAM_GET_TS() value when the request arrived.
 * @param   pfPostOptimize  HGCM optimizations, VMMDEVREQDISP_POST_F_XXX.
 * @param   ppLock          Pointer to the lock info pointer (latter can be
 *                          NULL).  Set to NULL if HGCM takes lock ownership.
 */
static int vmmdevReqDispatcher(PVMMDEV pThis, VMMDevRequestHeader *pReqHdr, RTGCPHYS GCPhysReqHdr,
                               uint64_t tsArrival, uint32_t *pfPostOptimize, PVMMDEVREQLOCK *ppLock)
`{`
    int rcRet = VINF_SUCCESS;
    Assert(*pfPostOptimize == 0);

    switch (pReqHdr-&gt;requestType)
    `{`
    ...........................................
#ifdef VBOX_WITH_HGCM
        case VMMDevReq_HGCMConnect:
            vmmdevReqHdrSetHgcmAsyncExecute(pThis, GCPhysReqHdr, *ppLock);
            pReqHdr-&gt;rc = vmmdevReqHandler_HGCMConnect(pThis, pReqHdr, GCPhysReqHdr);
            Assert(pReqHdr-&gt;rc == VINF_HGCM_ASYNC_EXECUTE || RT_FAILURE_NP(pReqHdr-&gt;rc));
            if (RT_SUCCESS(pReqHdr-&gt;rc))
                *pfPostOptimize |= VMMDEVREQDISP_POST_F_NO_WRITE_OUT;
            break;

        case VMMDevReq_HGCMDisconnect:
            vmmdevReqHdrSetHgcmAsyncExecute(pThis, GCPhysReqHdr, *ppLock);
            pReqHdr-&gt;rc = vmmdevReqHandler_HGCMDisconnect(pThis, pReqHdr, GCPhysReqHdr);
            Assert(pReqHdr-&gt;rc == VINF_HGCM_ASYNC_EXECUTE || RT_FAILURE_NP(pReqHdr-&gt;rc));
            if (RT_SUCCESS(pReqHdr-&gt;rc))
                *pfPostOptimize |= VMMDEVREQDISP_POST_F_NO_WRITE_OUT;
            break;

# ifdef VBOX_WITH_64_BITS_GUESTS
        case VMMDevReq_HGCMCall64:
# endif
        case VMMDevReq_HGCMCall32:
            vmmdevReqHdrSetHgcmAsyncExecute(pThis, GCPhysReqHdr, *ppLock);
            pReqHdr-&gt;rc = vmmdevReqHandler_HGCMCall(pThis, pReqHdr, GCPhysReqHdr, tsArrival, ppLock);
            Assert(pReqHdr-&gt;rc == VINF_HGCM_ASYNC_EXECUTE || RT_FAILURE_NP(pReqHdr-&gt;rc));
            if (RT_SUCCESS(pReqHdr-&gt;rc))
                *pfPostOptimize |= VMMDEVREQDISP_POST_F_NO_WRITE_OUT;
            break;

        case VMMDevReq_HGCMCancel:
            pReqHdr-&gt;rc = vmmdevReqHandler_HGCMCancel(pThis, pReqHdr, GCPhysReqHdr);
            break;

        case VMMDevReq_HGCMCancel2:
            pReqHdr-&gt;rc = vmmdevReqHandler_HGCMCancel2(pThis, pReqHdr);
            break;
#endif /* VBOX_WITH_HGCM */
...........................................
```

在`VMMDevReq_HGCMConnect`时，使用`vmmdevReqHdrSetHgcmAsyncExecute`函数设置异步返回值，这样Guset系统驱动的`VbglR0HGCMInternalConnect`函数时将通过`pfnAsyncCallback(&amp;pHGCMConnect-&gt;header, pvAsyncData, u32AsyncData);`等待设备这里的操作完成并获取结果；设备这里将调用`vmmdevReqHandler_HGCMConnect`连接HGCM服务，继续跟踪，

#### <a class="reference-link" name="vmmdevReqHandler_HGCMConnect"></a>vmmdevReqHandler_HGCMConnect

```
/** Handle VMMDevHGCMConnect request.
 *
 * @param   pThis           The VMMDev instance data.
 * @param   pHGCMConnect    The guest request (cached in host memory).
 * @param   GCPhys          The physical address of the request.
 */
int vmmdevHGCMConnect(PVMMDEV pThis, const VMMDevHGCMConnect *pHGCMConnect, RTGCPHYS GCPhys)
`{`
    int rc = VINF_SUCCESS;

    PVBOXHGCMCMD pCmd = vmmdevHGCMCmdAlloc(pThis, VBOXHGCMCMDTYPE_CONNECT, GCPhys, pHGCMConnect-&gt;header.header.size, 0,
                                           pHGCMConnect-&gt;header.header.fRequestor);
    if (pCmd)
    `{`
        vmmdevHGCMConnectFetch(pHGCMConnect, pCmd);

        /* Only allow the guest to use existing services! */
        ASSERT_GUEST(pHGCMConnect-&gt;loc.type == VMMDevHGCMLoc_LocalHost_Existing);
        pCmd-&gt;u.connect.pLoc-&gt;type = VMMDevHGCMLoc_LocalHost_Existing;

        vmmdevHGCMAddCommand(pThis, pCmd);
        rc = pThis-&gt;pHGCMDrv-&gt;pfnConnect(pThis-&gt;pHGCMDrv, pCmd, pCmd-&gt;u.connect.pLoc, &amp;pCmd-&gt;u.connect.u32ClientID);
        if (RT_FAILURE(rc))
            vmmdevHGCMRemoveCommand(pThis, pCmd);
    `}`
    else
    `{`
        rc = VERR_NO_MEMORY;
    `}`

    return rc;
`}`
```

函数中主要是调用了`rc = pThis-&gt;pHGCMDrv-&gt;pfnConnect(pThis-&gt;pHGCMDrv, pCmd, pCmd-&gt;u.connect.pLoc, &amp;pCmd-&gt;u.connect.u32ClientID);`进行服务连接，其中pThis在`vmmdevIOPortRegionMap`函数中初始化

```
PVMMDEV pThis = RT_FROM_MEMBER(pPciDev, VMMDEV, PciDev);
```

pThis-&gt;pHGCMDrv在`vmmdevConstruct`函数中被初始化

```
pThis-&gt;pHGCMDrv = PDMIBASE_QUERY_INTERFACE(pThis-&gt;pDrvBase, PDMIHGCMCONNECTOR);
```

通过调试，可以知道`pThis-&gt;pHGCMDrv-&gt;pfnConnect`最终指向的是`iface_hgcmConnect`函数

```
In file: /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Devices/VMMDev/VMMDevHGCM.cpp
   450         /* Only allow the guest to use existing services! */
   451         ASSERT_GUEST(pHGCMConnect-&gt;loc.type == VMMDevHGCMLoc_LocalHost_Existing);
   452         pCmd-&gt;u.connect.pLoc-&gt;type = VMMDevHGCMLoc_LocalHost_Existing;
   453 
   454         vmmdevHGCMAddCommand(pThis, pCmd);
 ► 455         rc = pThis-&gt;pHGCMDrv-&gt;pfnConnect(pThis-&gt;pHGCMDrv, pCmd, pCmd-&gt;u.connect.pLoc, &amp;pCmd-&gt;u.connect.u32ClientID);
   456         if (RT_FAILURE(rc))
   457             vmmdevHGCMRemoveCommand(pThis, pCmd);
   458     `}`
   459     else
   460     `{`
pwndbg&gt; s
   599 /* HGCM connector interface */
   600 
   601 static DECLCALLBACK(int) iface_hgcmConnect(PPDMIHGCMCONNECTOR pInterface, PVBOXHGCMCMD pCmd,
   602                                            PHGCMSERVICELOCATION pServiceLocation,
   603                                            uint32_t *pu32ClientID)
 ► 604 `{`
```

其中iface_hgcmConnect函数源码如下

#### <a class="reference-link" name="iface_hgcmConnect"></a>iface_hgcmConnect

```
static DECLCALLBACK(int) iface_hgcmConnect(PPDMIHGCMCONNECTOR pInterface, PVBOXHGCMCMD pCmd,
                                           PHGCMSERVICELOCATION pServiceLocation,
                                           uint32_t *pu32ClientID)
`{`
    Log9(("Enter\n"));

    PDRVMAINVMMDEV pDrv = RT_FROM_MEMBER(pInterface, DRVMAINVMMDEV, HGCMConnector);

    if (    !pServiceLocation
        || (   pServiceLocation-&gt;type != VMMDevHGCMLoc_LocalHost
            &amp;&amp; pServiceLocation-&gt;type != VMMDevHGCMLoc_LocalHost_Existing))
    `{`
        return VERR_INVALID_PARAMETER;
    `}`

    /* Check if service name is a string terminated by zero*/
    size_t cchInfo = 0;
    if (RTStrNLenEx(pServiceLocation-&gt;u.host.achName, sizeof(pServiceLocation-&gt;u.host.achName), &amp;cchInfo) != VINF_SUCCESS)
    `{`
        return VERR_INVALID_PARAMETER;
    `}`

    if (!pDrv-&gt;pVMMDev || !pDrv-&gt;pVMMDev-&gt;hgcmIsActive())
        return VERR_INVALID_STATE;
    return HGCMGuestConnect(pDrv-&gt;pHGCMPort, pCmd, pServiceLocation-&gt;u.host.achName, pu32ClientID);
`}`
```

这里，对于`pServiceLocation-&gt;type`字段，其值必须为`VMMDevHGCMLoc_LocalHost`或者`VMMDevHGCMLoc_LocalHost_Existing`。检查通过以后，就会继续调用`HGCMGuestConnect`函数<br>
而`HGCMGuestConnect`函数是将数据封装为消息，然后调用`hgcmMsgPost`，`hgcmMsgPost`最后会调用`hgcmMsgPostInternal`函数向`HGCMThread`实例发送消息

#### <a class="reference-link" name="hgcmMsgPostInternal"></a>hgcmMsgPostInternal

```
DECLINLINE(int) hgcmMsgPostInternal(HGCMMsgCore *pMsg, PHGCMMSGCALLBACK pfnCallback, bool fWait)
`{`
    LogFlow(("MAIN::hgcmMsgPostInternal: pMsg = %p, pfnCallback = %p, fWait = %d\n", pMsg, pfnCallback, fWait));
    Assert(pMsg);

    pMsg-&gt;Reference(); /* paranoia? */

    int rc = pMsg-&gt;Thread()-&gt;MsgPost(pMsg, pfnCallback, fWait);

    pMsg-&gt;Dereference();

    LogFlow(("MAIN::hgcmMsgPostInternal: pMsg = %p, rc = %Rrc\n", pMsg, rc));
    return rc;
`}`
```

通过gdb调试

```
In file: /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Main/src-client/HGCMThread.cpp
   697     LogFlow(("MAIN::hgcmMsgPostInternal: pMsg = %p, pfnCallback = %p, fWait = %d\n", pMsg, pfnCallback, fWait));
   698     Assert(pMsg);
   699 
   700     pMsg-&gt;Reference(); /* paranoia? */
   701 
 ► 702     int rc = pMsg-&gt;Thread()-&gt;MsgPost(pMsg, pfnCallback, fWait);
   703 
   704     pMsg-&gt;Dereference();
   705 
   706     LogFlow(("MAIN::hgcmMsgPostInternal: pMsg = %p, rc = %Rrc\n", pMsg, rc));
   707     return rc;
pwndbg&gt; p pMsg-&gt;Thread()-&gt;MsgPost
$11 = `{`int (HGCMThread * const, HGCMMsgCore *, PHGCMMSGCALLBACK, bool)`}` 0x7fe5d8646a5c &lt;HGCMThread::MsgPost(HGCMMsgCore*, int (*)(int, HGCMMsgCore*), bool)&gt;
```

HGCMThread::MsgPost函数只是简单的将消息插入到消息队列，当HGCMThread的线程取出消息时，便会进行处理。HGCMThread的主线程函数为`hgcmThread`

#### <a class="reference-link" name="hgcmThread"></a>hgcmThread

```
/* The main HGCM thread handler. */
static DECLCALLBACK(void) hgcmThread(HGCMThread *pThread, void *pvUser)
`{`
    LogFlowFunc(("pThread = %p, pvUser = %p\n", pThread, pvUser));

    NOREF(pvUser);

    bool fQuit = false;

    while (!fQuit)
    `{`
        HGCMMsgCore *pMsgCore;
        int rc = hgcmMsgGet(pThread, &amp;pMsgCore);

        if (RT_FAILURE(rc))
        `{`
            /* The error means some serious unrecoverable problem in the hgcmMsg/hgcmThread layer. */
            AssertMsgFailed(("%Rrc\n", rc));
            break;
        `}`

        uint32_t u32MsgId = pMsgCore-&gt;MsgId();

        switch (u32MsgId)
        `{`
            case HGCM_MSG_CONNECT:
            `{`
                HGCMMsgMainConnect *pMsg = (HGCMMsgMainConnect *)pMsgCore;

                LogFlowFunc(("HGCM_MSG_CONNECT pszServiceName %s, pu32ClientId %p\n",
                             pMsg-&gt;pszServiceName, pMsg-&gt;pu32ClientId));

                /* Resolve the service name to the pointer to service instance.
                 */
                HGCMService *pService;
                rc = HGCMService::ResolveService(&amp;pService, pMsg-&gt;pszServiceName);

                if (RT_SUCCESS(rc))
                `{`
                    /* Call the service instance method. */
                    rc = pService-&gt;CreateAndConnectClient(pMsg-&gt;pu32ClientId,
                                                          0,
                                                          pMsg-&gt;pHGCMPort-&gt;pfnGetRequestor(pMsg-&gt;pHGCMPort, pMsg-&gt;pCmd),
                                                          pMsg-&gt;pHGCMPort-&gt;pfnIsCmdRestored(pMsg-&gt;pHGCMPort, pMsg-&gt;pCmd));

                    /* Release the service after resolve. */
                    pService-&gt;ReleaseService();
                `}`
            `}` break;

            case HGCM_MSG_DISCONNECT:
            `{`
```

当收到`HGCM_MSG_CONNECT`消息时，调用`HGCMService::ResolveService(&amp;pService, pMsg-&gt;pszServiceName)`得到对应服务的句柄，该函数实际上就是一个链表查找的过程

```
/** The method obtains a referenced pointer to the service with
 *  specified name. The caller must call ReleaseService when
 *  the pointer is no longer needed.
 *
 * @param ppSvc          Where to store the pointer to the service.
 * @param pszServiceName The name of the service.
 * @return VBox rc.
 * @thread main HGCM
 */
/* static */ int HGCMService::ResolveService(HGCMService **ppSvc, const char *pszServiceName)
`{`
    LogFlowFunc(("ppSvc = %p name = %s\n",
                 ppSvc, pszServiceName));

    if (!ppSvc || !pszServiceName)
    `{`
        return VERR_INVALID_PARAMETER;
    `}`

    HGCMService *pSvc = sm_pSvcListHead;

    while (pSvc)
    `{`
        if (strcmp(pSvc-&gt;m_pszSvcName, pszServiceName) == 0)
        `{`
            break;
        `}`

        pSvc = pSvc-&gt;m_pSvcNext;
    `}`

    LogFlowFunc(("lookup in the list is %p\n", pSvc));

    if (pSvc == NULL)
    `{`
        *ppSvc = NULL;
        return VERR_HGCM_SERVICE_NOT_FOUND;
    `}`

    pSvc-&gt;ReferenceService();

    *ppSvc = pSvc;

    return VINF_SUCCESS;
`}`
```

而该服务链表是在`HGCM_MSG_LOAD`时通过`LoadService`初始化的

```
case HGCM_MSG_LOAD:
            `{`
                HGCMMsgMainLoad *pMsg = (HGCMMsgMainLoad *)pMsgCore;

                LogFlowFunc(("HGCM_MSG_LOAD pszServiceName = %s, pMsg-&gt;pszServiceLibrary = %s, pMsg-&gt;pUVM = %p\n",
                             pMsg-&gt;pszServiceName, pMsg-&gt;pszServiceLibrary, pMsg-&gt;pUVM));

                rc = HGCMService::LoadService(pMsg-&gt;pszServiceLibrary, pMsg-&gt;pszServiceName, pMsg-&gt;pUVM, pMsg-&gt;pHgcmPort);
            `}` break;
```

其中`LoadService`函数就是加载对应的名称的`动态库`，然后将句柄存储到链表中。<br>
ResolveService得到服务模块句柄以后，就通过`CreateAndConnectClient`函数调用模块中初始化的函数

```
if (RT_SUCCESS(rc))
                `{`
                    /* Call the service instance method. */
                    rc = pService-&gt;CreateAndConnectClient(pMsg-&gt;pu32ClientId,
                                                          0,
                                                          pMsg-&gt;pHGCMPort-&gt;pfnGetRequestor(pMsg-&gt;pHGCMPort, pMsg-&gt;pCmd),
                                                          pMsg-&gt;pHGCMPort-&gt;pfnIsCmdRestored(pMsg-&gt;pHGCMPort, pMsg-&gt;pCmd));

                    /* Release the service after resolve. */
                    pService-&gt;ReleaseService();
                `}`
```

CreateAndConnectClient函数如下

```
/* Create a new client instance and connect it to the service.
 *
 * @param pu32ClientIdOut If not NULL, then the method must generate a new handle for the client.
 *                        If NULL, use the given 'u32ClientIdIn' handle.
 * @param u32ClientIdIn   The handle for the client, when 'pu32ClientIdOut' is NULL.
 * @param fRequestor      The requestor flags, VMMDEV_REQUESTOR_LEGACY if not available.
 * @param fRestoring      Set if we're restoring a saved state.
 * @return VBox status code.
 */
int HGCMService::CreateAndConnectClient(uint32_t *pu32ClientIdOut, uint32_t u32ClientIdIn, uint32_t fRequestor, bool fRestoring)
`{`
    LogFlowFunc(("pu32ClientIdOut = %p, u32ClientIdIn = %d, fRequestor = %#x, fRestoring = %d\n",
                 pu32ClientIdOut, u32ClientIdIn, fRequestor, fRestoring));

    /* Allocate a client information structure. */
    HGCMClient *pClient = new (std::nothrow) HGCMClient(fRequestor);

    if (!pClient)
    `{`
        Log1WarningFunc(("Could not allocate HGCMClient!!!\n"));
        return VERR_NO_MEMORY;
    `}`

    uint32_t handle;

    if (pu32ClientIdOut != NULL)
    `{`
        handle = hgcmObjGenerateHandle(pClient);
    `}`
    else
    `{`
        handle = hgcmObjAssignHandle(pClient, u32ClientIdIn);
    `}`

    LogFlowFunc(("client id = %d\n", handle));

    AssertRelease(handle);

    /* Initialize the HGCM part of the client. */
    int rc = pClient-&gt;Init(this);

    if (RT_SUCCESS(rc))
    `{`
        /* Call the service. */
        HGCMMsgCore *pCoreMsg;

        rc = hgcmMsgAlloc(m_pThread, &amp;pCoreMsg, SVC_MSG_CONNECT, hgcmMessageAllocSvc);

        if (RT_SUCCESS(rc))
        `{`
            HGCMMsgSvcConnect *pMsg = (HGCMMsgSvcConnect *)pCoreMsg;

            pMsg-&gt;u32ClientId = handle;
            pMsg-&gt;fRequestor = fRequestor;
            pMsg-&gt;fRestoring = fRestoring;

            rc = hgcmMsgSend(pMsg);

            if (RT_SUCCESS(rc))
            `{`
                /* Add the client Id to the array. */
                if (m_cClients == m_cClientsAllocated)
                `{`
                    const uint32_t cDelta = 64;

                    /* Guards against integer overflow on 32bit arch and also limits size of m_paClientIds array to 4GB*/
                    if (m_cClientsAllocated &lt; UINT32_MAX / sizeof(m_paClientIds[0]) - cDelta)
                    `{`
                        uint32_t *paClientIdsNew;

                        paClientIdsNew = (uint32_t *)RTMemRealloc(m_paClientIds,
                                                                  (m_cClientsAllocated + cDelta) * sizeof(m_paClientIds[0]));
                        Assert(paClientIdsNew);

                        if (paClientIdsNew)
                        `{`
                            m_paClientIds = paClientIdsNew;
                            m_cClientsAllocated += cDelta;
                        `}`
                        else
                        `{`
                            rc = VERR_NO_MEMORY;
                        `}`
                    `}`
                    else
                    `{`
                        rc = VERR_NO_MEMORY;
                    `}`
                `}`

                m_paClientIds[m_cClients] = handle;
                m_cClients++;
            `}`
        `}`
    `}`

    if (RT_FAILURE(rc))
    `{`
        hgcmObjDeleteHandle(handle);
    `}`
    else
    `{`
        if (pu32ClientIdOut != NULL)
        `{`
            *pu32ClientIdOut = handle;
        `}`

        ReferenceService();
    `}`

    LogFlowFunc(("rc = %Rrc\n", rc));
    return rc;
`}`
```

可以知道，模块的id值最终被存入`m_paClientIds[m_cClients]`，同时通过`*pu32ClientIdOut = handle;`将值返回。<br>
整个过程大概描述如下

[![](https://p4.ssl.qhimg.com/t014e8eb668bcd7d8e6.png)](https://p4.ssl.qhimg.com/t014e8eb668bcd7d8e6.png)

### <a class="reference-link" name="VBGL_IOCTL_HGCM_CALL"></a>VBGL_IOCTL_HGCM_CALL

在分析完`VBGL_IOCTL_HGCM_CONNECT`操作以后，接下来就是分析`VBGL_IOCTL_HGCM_CALL`，其路线与前面分析的类似，首先会将IOCTL传入的数据指针转为`PVBGLIOCHGCMCALL`类型

#### <a class="reference-link" name="PVBGLIOCHGCMCALL"></a>PVBGLIOCHGCMCALL

```
/**
 * For VBGL_IOCTL_HGCM_CALL and VBGL_IOCTL_HGCM_CALL_WITH_USER_DATA.
 *
 * @note This is used by alot of HGCM call structures.
 */
typedef struct VBGLIOCHGCMCALL
`{`
    /** Common header. */
    VBGLREQHDR  Hdr;
    /** Input: The id of the caller. */
    uint32_t    u32ClientID;
    /** Input: Function number. */
    uint32_t    u32Function;
    /** Input: How long to wait (milliseconds) for completion before cancelling the
     * call.  This is ignored if not a VBGL_IOCTL_HGCM_CALL_TIMED or
     * VBGL_IOCTL_HGCM_CALL_TIMED_32 request. */
    uint32_t    cMsTimeout;
    /** Input: Whether a timed call is interruptible (ring-0 only).  This is ignored
     * if not a VBGL_IOCTL_HGCM_CALL_TIMED or VBGL_IOCTL_HGCM_CALL_TIMED_32
     * request, or if made from user land. */
    bool        fInterruptible;
    /** Explicit padding, MBZ. */
    uint8_t     bReserved;
    /** Input: How many parameters following this structure.
     *
     * The parameters are either HGCMFunctionParameter64 or HGCMFunctionParameter32,
     * depending on whether we're receiving a 64-bit or 32-bit request.
     *
     * The current maximum is 61 parameters (given a 1KB max request size,
     * and a 64-bit parameter size of 16 bytes).
     *
     * @note This information is duplicated by Hdr.cbIn, but it's currently too much
     *       work to eliminate this. */
    uint16_t    cParms;
    /* Parameters follow in form HGCMFunctionParameter aParms[cParms] */
`}` VBGLIOCHGCMCALL, RT_FAR *PVBGLIOCHGCMCALL;
```

经过一些列调用，会来到`vgdrvIoCtl_HGCMCallInner`函数

#### <a class="reference-link" name="vgdrvIoCtl_HGCMCallInner"></a>vgdrvIoCtl_HGCMCallInner

```
static int vgdrvIoCtl_HGCMCallInner(PVBOXGUESTDEVEXT pDevExt, PVBOXGUESTSESSION pSession, PVBGLIOCHGCMCALL pInfo,
                                    uint32_t cMillies, bool fInterruptible, bool f32bit, bool fUserData,
                                    size_t cbExtra, size_t cbData)
`{`
    const uint32_t  u32ClientId = pInfo-&gt;u32ClientID;
    uint32_t        fFlags;
    size_t          cbActual;
    unsigned        i;
    int             rc;

    /*
     * Some more validations.
     */
    if (RT_LIKELY(pInfo-&gt;cParms &lt;= VMMDEV_MAX_HGCM_PARMS)) /* (Just make sure it doesn't overflow the next check.) */
    `{` /* likely */`}`
    else
    `{`
        LogRel(("VBOXGUEST_IOCTL_HGCM_CALL: cParm=%RX32 is not sane\n", pInfo-&gt;cParms));
        return VERR_INVALID_PARAMETER;
    `}`

    cbActual = cbExtra + sizeof(*pInfo);
#ifdef RT_ARCH_AMD64
    if (f32bit)
        cbActual += pInfo-&gt;cParms * sizeof(HGCMFunctionParameter32);
    else
#endif
        cbActual += pInfo-&gt;cParms * sizeof(HGCMFunctionParameter);
    if (RT_LIKELY(cbData &gt;= cbActual))
    `{` /* likely */`}`
    else
    `{`
        LogRel(("VBOXGUEST_IOCTL_HGCM_CALL: cbData=%#zx (%zu) required size is %#zx (%zu)\n",
               cbData, cbData, cbActual, cbActual));
        return VERR_INVALID_PARAMETER;
    `}`
    pInfo-&gt;Hdr.cbOut = (uint32_t)cbActual;

 ........................................................

        else
            rc = VbglR0HGCMInternalCall(pInfo, cbInfo, fFlags, pSession-&gt;fRequestor,
                                        vgdrvHgcmAsyncWaitCallback, pDevExt, cMillies);
    `}`
.............................................................
    return rc;
`}`
```

从中可以看到`cbActual += pInfo-&gt;cParms * sizeof(HGCMFunctionParameter);`，并且该值最后赋值`pInfo-&gt;Hdr.cbOut = (uint32_t)cbActual;`，由此可见`pInfo-&gt;cParms`代表需要调用的函数的参数个数，而pInfo结构体下方就是cParms个`HGCMFunctionParameter`结构体对象。与`VBGL_IOCTL_HGCM_CONNECT`类似，最后驱动也是通过`IO端口操作`将数据发送到Host中的虚拟设备中，然后在设备的`vmmdevReqDispatcher`函数中处理。<br>
如下代码

```
# ifdef VBOX_WITH_64_BITS_GUESTS
        case VMMDevReq_HGCMCall64:
# endif
        case VMMDevReq_HGCMCall32:
            vmmdevReqHdrSetHgcmAsyncExecute(pThis, GCPhysReqHdr, *ppLock);
            pReqHdr-&gt;rc = vmmdevReqHandler_HGCMCall(pThis, pReqHdr, GCPhysReqHdr, tsArrival, ppLock);
            Assert(pReqHdr-&gt;rc == VINF_HGCM_ASYNC_EXECUTE || RT_FAILURE_NP(pReqHdr-&gt;rc));
            if (RT_SUCCESS(pReqHdr-&gt;rc))
                *pfPostOptimize |= VMMDEVREQDISP_POST_F_NO_WRITE_OUT;
            break;
```

该操作仍然是异步处理，需要等待处理完成后回调函数响应，将结果通过IO端口传回Guest。操作主要是调用`vmmdevHGCMCall`来对相应的service里的函数进行调用。

#### <a class="reference-link" name="vmmdevHGCMCall"></a>vmmdevHGCMCall

```
/**
 * Handles VMMDevHGCMCall request.
 *
 * @returns VBox status code that the guest should see.
 * @param   pThis           The VMMDev instance data.
 * @param   pHGCMCall       The request to handle (cached in host memory).
 * @param   cbHGCMCall      Size of the entire request (including HGCM parameters).
 * @param   GCPhys          The guest physical address of the request.
 * @param   enmRequestType  The request type. Distinguishes 64 and 32 bit calls.
 * @param   tsArrival       The STAM_GET_TS() value when the request arrived.
 * @param   ppLock          Pointer to the lock info pointer (latter can be
 *                          NULL).  Set to NULL if HGCM takes lock ownership.
 */
int vmmdevHGCMCall(PVMMDEV pThis, const VMMDevHGCMCall *pHGCMCall, uint32_t cbHGCMCall, RTGCPHYS GCPhys,
                   VMMDevRequestType enmRequestType, uint64_t tsArrival, PVMMDEVREQLOCK *ppLock)
`{`
.............................................................
        rc = vmmdevHGCMCallFetchGuestParms(pThis, pCmd, pHGCMCall, cbHGCMCall, enmRequestType, cbHGCMParmStruct);
        if (RT_SUCCESS(rc))
        `{`
            /* Copy guest data to host parameters, so HGCM services can use the data. */
            rc = vmmdevHGCMInitHostParameters(pThis, pCmd, (uint8_t const *)pHGCMCall);
            if (RT_SUCCESS(rc))
            `{`
                /*
                 * Pass the function call to HGCM connector for actual processing
                 */
                vmmdevHGCMAddCommand(pThis, pCmd);

#if 0 /* DONT ENABLE - for performance hacking. */
                if (    pCmd-&gt;u.call.u32Function == 9
                    &amp;&amp;  pCmd-&gt;u.call.cParms      == 5)
                `{`
                    vmmdevHGCMRemoveCommand(pThis, pCmd);

                    if (pCmd-&gt;pvReqLocked)
                    `{`
                        VMMDevHGCMRequestHeader volatile *pHeader = (VMMDevHGCMRequestHeader volatile *)pCmd-&gt;pvReqLocked;
                        pHeader-&gt;header.rc = VINF_SUCCESS;
                        pHeader-&gt;result    = VINF_SUCCESS;
                        pHeader-&gt;fu32Flags |= VBOX_HGCM_REQ_DONE;
                    `}`
                    else
                    `{`
                        VMMDevHGCMRequestHeader *pHeader = (VMMDevHGCMRequestHeader *)pHGCMCall;
                        pHeader-&gt;header.rc = VINF_SUCCESS;
                        pHeader-&gt;result    = VINF_SUCCESS;
                        pHeader-&gt;fu32Flags |= VBOX_HGCM_REQ_DONE;
                        PDMDevHlpPhysWrite(pThis-&gt;pDevInsR3, GCPhys, pHeader,  sizeof(*pHeader));
                    `}`
                    vmmdevHGCMCmdFree(pThis, pCmd);
                    return VINF_HGCM_ASYNC_EXECUTE; /* ignored, but avoids assertions. */
                `}`
#endif

                rc = pThis-&gt;pHGCMDrv-&gt;pfnCall(pThis-&gt;pHGCMDrv, pCmd,
                                              pCmd-&gt;u.call.u32ClientID, pCmd-&gt;u.call.u32Function,
                                              pCmd-&gt;u.call.cParms, pCmd-&gt;u.call.paHostParms, tsArrival);
...................................................
    return rc;
`}`
```

可以看出，vmmdevHGCMCall中首先是使用`vmmdevHGCMCallFetchGuestParms`函数和`vmmdevHGCMInitHostParameters`函数，将参数从Guest中拷贝到了设备本地缓冲区中，然后通过`pThis-&gt;pHGCMDrv-&gt;pfnCall`调用了对应的函数。<br>
通过调试

```
In file: /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/Devices/VMMDev/VMMDevHGCM.cpp
   1107                 `}`
   1108 #endif
   1109 
   1110                 rc = pThis-&gt;pHGCMDrv-&gt;pfnCall(pThis-&gt;pHGCMDrv, pCmd,
   1111                                               pCmd-&gt;u.call.u32ClientID, pCmd-&gt;u.call.u32Function,
 ► 1112                                               pCmd-&gt;u.call.cParms, pCmd-&gt;u.call.paHostParms, tsArrival);
   1113 
   1114                 if (rc == VINF_HGCM_ASYNC_EXECUTE)
   1115                 `{`
   1116                     /*
   1117                      * Done.  Just update statistics and return.
pwndbg&gt; s
   638 `}`
   639 
   640 static DECLCALLBACK(int) iface_hgcmCall(PPDMIHGCMCONNECTOR pInterface, PVBOXHGCMCMD pCmd, uint32_t u32ClientID,
   641                                         uint32_t u32Function, uint32_t cParms, PVBOXHGCMSVCPARM paParms, uint64_t tsArrival)

```

可以知道该函数指针指向的是`iface_hgcmCall`函数

#### <a class="reference-link" name="iface_hgcmCall"></a>iface_hgcmCall

```
static DECLCALLBACK(int) iface_hgcmCall(PPDMIHGCMCONNECTOR pInterface, PVBOXHGCMCMD pCmd, uint32_t u32ClientID,
                                        uint32_t u32Function, uint32_t cParms, PVBOXHGCMSVCPARM paParms, uint64_t tsArrival)
`{`
    Log9(("Enter\n"));

    PDRVMAINVMMDEV pDrv = RT_FROM_MEMBER(pInterface, DRVMAINVMMDEV, HGCMConnector);

    if (!pDrv-&gt;pVMMDev || !pDrv-&gt;pVMMDev-&gt;hgcmIsActive())
        return VERR_INVALID_STATE;

    return HGCMGuestCall(pDrv-&gt;pHGCMPort, pCmd, u32ClientID, u32Function, cParms, paParms, tsArrival);
`}`
```

该函数简单的调用了`HGCMGuestCall`函数，而`HGCMGuestCall`函数继续调用`HGCMService::GuestCall`函数，同样也是通过`hgcmMsgPost`将消息挂到队列中，等待`hgcmServiceThread`线程取出消息并处理。

```
/*
 * The service thread. Loads the service library and calls the service entry points.
 */
DECLCALLBACK(void) hgcmServiceThread(HGCMThread *pThread, void *pvUser)
`{`
    HGCMService *pSvc = (HGCMService *)pvUser;
    AssertRelease(pSvc != NULL);
       /* Cache required information to avoid unnecessary pMsgCore access. */
        uint32_t u32MsgId = pMsgCore-&gt;MsgId();

        switch (u32MsgId)
        `{`
           case SVC_MSG_GUESTCALL:
            `{`
                HGCMMsgCall *pMsg = (HGCMMsgCall *)pMsgCore;

                LogFlowFunc(("SVC_MSG_GUESTCALL u32ClientId = %d, u32Function = %d, cParms = %d, paParms = %p\n",
                             pMsg-&gt;u32ClientId, pMsg-&gt;u32Function, pMsg-&gt;cParms, pMsg-&gt;paParms));

                HGCMClient *pClient = (HGCMClient *)hgcmObjReference(pMsg-&gt;u32ClientId, HGCMOBJ_CLIENT);

                if (pClient)
                `{`
                    pSvc-&gt;m_fntable.pfnCall(pSvc-&gt;m_fntable.pvService, (VBOXHGCMCALLHANDLE)pMsg, pMsg-&gt;u32ClientId,
                                            HGCM_CLIENT_DATA(pSvc, pClient), pMsg-&gt;u32Function,
                                            pMsg-&gt;cParms, pMsg-&gt;paParms, pMsg-&gt;tsArrival);

                    hgcmObjDereference(pClient);
                `}`
                else
                `{`
                    rc = VERR_HGCM_INVALID_CLIENT_ID;
                `}`
            `}` break;
```

代码中，通过`HGCMClient *pClient = (HGCMClient *)hgcmObjReference(pMsg-&gt;u32ClientId, HGCMOBJ_CLIENT);`获取到了`HGCMClient`服务对象，然后通过`pSvc-&gt;m_fntable.pfnCall`进入了对应服务的处理函数。<br>
调试如下

```
In file: /home/sea/Desktop/VirtualBox-6.0.0/src/VBox/HostServices/SharedClipboard/service.cpp
   407                                    void *pvClient,
   408                                    uint32_t u32Function,
   409                                    uint32_t cParms,
   410                                    VBOXHGCMSVCPARM paParms[],
   411                                    uint64_t tsArrival)
 ► 412 `{`
   413     RT_NOREF_PV(tsArrival);
   414     int rc = VINF_SUCCESS;
   415 
   416     LogRel2(("svcCall: u32ClientID = %d, fn = %d, cParms = %d, pparms = %d\n",
   417              u32ClientID, u32Function, cParms, paParms));
```

此时我们进入的是`SharedClipboard`服务的程序`svcCall`函数。对于`HostServices`目录下的各种服务都有一个`svcCall`函数的实现，由此可见，`svcCall`函数是服务程序的处理机入口。从代码可以看出这个函数是在`VBoxHGCMSvcLoad`中注册的

```
extern "C" DECLCALLBACK(DECLEXPORT(int)) VBoxHGCMSvcLoad (VBOXHGCMSVCFNTABLE *ptable)
`{`
    int rc = VINF_SUCCESS;
            g_pHelpers = ptable-&gt;pHelpers;

            ptable-&gt;cbClient = sizeof (VBOXCLIPBOARDCLIENTDATA);

            ptable-&gt;pfnUnload     = svcUnload;
            ptable-&gt;pfnConnect    = svcConnect;
            ptable-&gt;pfnDisconnect = svcDisconnect;
            ptable-&gt;pfnCall       = svcCall;
            ptable-&gt;pfnHostCall   = svcHostCall;
            ptable-&gt;pfnSaveState  = svcSaveState;
            ptable-&gt;pfnLoadState  = svcLoadState;
            ptable-&gt;pfnRegisterExtension  = svcRegisterExtension;
            ptable-&gt;pfnNotify     = NULL;
            ptable-&gt;pvService     = NULL;

            /* Service specific initialization. */
            rc = svcInit ();
.................................................
```

至此，我们对于`VBGL_IOCTL_HGCM_CALL`调用Service中的函数的整个流程也有所清楚了。

### <a class="reference-link" name="VBGL_IOCTL_IDC_DISCONNECT"></a>VBGL_IOCTL_IDC_DISCONNECT

对于`VBGL_IOCTL_IDC_DISCONNECT`，流程与前面类似，比较简单，调用了对应服务的`DisconnectClient`函数，然后使用`hgcmObjDereference(pClient);`将服务句柄从设备缓存列表中移除。

```
case HGCM_MSG_DISCONNECT:
            `{`
                HGCMMsgMainDisconnect *pMsg = (HGCMMsgMainDisconnect *)pMsgCore;

                LogFlowFunc(("HGCM_MSG_DISCONNECT u32ClientId = %d\n",
                             pMsg-&gt;u32ClientId));

                HGCMClient *pClient = (HGCMClient *)hgcmObjReference(pMsg-&gt;u32ClientId, HGCMOBJ_CLIENT);

                if (!pClient)
                `{`
                    rc = VERR_HGCM_INVALID_CLIENT_ID;
                    break;
                `}`

                /* The service the client belongs to. */
                HGCMService *pService = pClient-&gt;pService;

                /* Call the service instance to disconnect the client. */
                rc = pService-&gt;DisconnectClient(pMsg-&gt;u32ClientId, false);

                hgcmObjDereference(pClient);
            `}` break;
```

至此，我们对HGCM协议已经有了进一步的深刻了解。



## 0x02 HGCM调用库封装

经过上面的协议源代码分析，我们可以很轻松的写出HGCM的调用方法，国外`niklasb`大牛已经做了一个python版的封装库名为[3dpwn](https://github.com/niklasb/3dpwn/)，而这里，我们自己同样实现了一个C语言版

### <a class="reference-link" name="hgcm.h"></a>hgcm.h

```
#ifndef HGM_HELPER_H
#define HGM_HELPER_H

#define VBGLREQHDR_VERSION 0x10001
#define VBGLREQHDR_TYPE_DEFAULT 0
#define VERR_INTERNAL_ERROR -225

#define VBGL_IOCTL_CODE_SIZE(func, size) (0xc0005600 + (size&lt;&lt;16) + func)

#define VBGL_IOCTL_HGCM_CONNECT                    VBGL_IOCTL_CODE_SIZE(4, VBGL_IOCTL_HGCM_CONNECT_SIZE)
#define VBGL_IOCTL_HGCM_CONNECT_SIZE               sizeof(VBGLIOCHGCMCONNECT)

# define VBGL_IOCTL_HGCM_DISCONNECT                 VBGL_IOCTL_CODE_SIZE(5, VBGL_IOCTL_HGCM_DISCONNECT_SIZE)
# define VBGL_IOCTL_HGCM_DISCONNECT_SIZE            sizeof(VBGLIOCHGCMDISCONNECT)

#define IOCTL_HGCM_CALL 7

/** Guest Physical Memory Address; limited to 64 bits.*/
typedef uint64_t                RTGCPHYS64;
/** Unsigned integer which can contain a 64 bits GC pointer. */
typedef uint64_t                RTGCUINTPTR64;
/** Guest context pointer, 64 bits.
 */
typedef RTGCUINTPTR64           RTGCPTR64;

typedef uint8_t bool;


typedef struct VBGLREQHDR
`{`
    /** IN: The request input size, and output size if cbOut is zero.
     * @sa VMMDevRequestHeader::size  */
    uint32_t        cbIn;
    /** IN: Structure version (VBGLREQHDR_VERSION)
     * @sa VMMDevRequestHeader::version */
    uint32_t        uVersion;
    /** IN: The VMMDev request type, set to VBGLREQHDR_TYPE_DEFAULT unless this is a
     * kind of VMMDev request.
     * @sa VMMDevRequestType, VMMDevRequestHeader::requestType */
    uint32_t        uType;
    /** OUT: The VBox status code of the operation, out direction only. */
    int32_t         rc;
    /** IN: The output size.  This is optional - set to zero to use cbIn as the
     * output size. */
    uint32_t        cbOut;
    /** Reserved / filled in by kernel, MBZ.
     * @sa VMMDevRequestHeader::fRequestor */
    uint32_t        uReserved;
`}` VBGLREQHDR;

/**
 * HGCM host service location.
 * @ingroup grp_vmmdev_req
 */
typedef struct
`{`
    char achName[128]; /**&lt; This is really szName. */
`}` HGCMServiceLocationHost;

typedef enum
`{`
    VMMDevHGCMLoc_Invalid    = 0,
    VMMDevHGCMLoc_LocalHost  = 1,
    VMMDevHGCMLoc_LocalHost_Existing = 2,
    VMMDevHGCMLoc_SizeHack   = 0x7fffffff
`}` HGCMServiceLocationType;

/**
 * HGCM service location.
 * @ingroup grp_vmmdev_req
 */
typedef struct HGCMSERVICELOCATION
`{`
    /** Type of the location. */
    HGCMServiceLocationType type;

    union
    `{`
        HGCMServiceLocationHost host;
    `}` u;
`}` HGCMServiceLocation;

typedef struct VBGLIOCHGCMCONNECT
`{`
    /** The header. */
    VBGLREQHDR                  Hdr;
    union
    `{`
        struct
        `{`
            HGCMServiceLocation Loc;
        `}` In;
        struct
        `{`
            uint32_t            idClient;
        `}` Out;
    `}` u;
`}` VBGLIOCHGCMCONNECT;

/**
 * For VBGL_IOCTL_HGCM_CALL and VBGL_IOCTL_HGCM_CALL_WITH_USER_DATA.
 *
 * @note This is used by alot of HGCM call structures.
 */
typedef struct VBGLIOCHGCMCALL
`{`
    /** Common header. */
    VBGLREQHDR  Hdr;
    /** Input: The id of the caller. */
    uint32_t    u32ClientID;
    /** Input: Function number. */
    uint32_t    u32Function;
    /** Input: How long to wait (milliseconds) for completion before cancelling the
     * call.  This is ignored if not a VBGL_IOCTL_HGCM_CALL_TIMED or
     * VBGL_IOCTL_HGCM_CALL_TIMED_32 request. */
    uint32_t    cMsTimeout;
    /** Input: Whether a timed call is interruptible (ring-0 only).  This is ignored
     * if not a VBGL_IOCTL_HGCM_CALL_TIMED or VBGL_IOCTL_HGCM_CALL_TIMED_32
     * request, or if made from user land. */
    bool        fInterruptible;
    /** Explicit padding, MBZ. */
    uint8_t     bReserved;
    /** Input: How many parameters following this structure.
     *
     * The parameters are either HGCMFunctionParameter64 or HGCMFunctionParameter32,
     * depending on whether we're receiving a 64-bit or 32-bit request.
     *
     * The current maximum is 61 parameters (given a 1KB max request size,
     * and a 64-bit parameter size of 16 bytes).
     *
     * @note This information is duplicated by Hdr.cbIn, but it's currently too much
     *       work to eliminate this. */
    uint16_t    cParms;
    /* Parameters follow in form HGCMFunctionParameter aParms[cParms] */
`}` VBGLIOCHGCMCALL;



/**
 * HGCM parameter type.
 */
typedef enum
`{`
    VMMDevHGCMParmType_Invalid            = 0,
    VMMDevHGCMParmType_32bit              = 1,
    VMMDevHGCMParmType_64bit              = 2,
    VMMDevHGCMParmType_PhysAddr           = 3,  /**&lt; @deprecated Doesn't work, use PageList. */
    VMMDevHGCMParmType_LinAddr            = 4,  /**&lt; In and Out */
    VMMDevHGCMParmType_LinAddr_In         = 5,  /**&lt; In  (read;  host&lt;-guest) */
    VMMDevHGCMParmType_LinAddr_Out        = 6,  /**&lt; Out (write; host-&gt;guest) */
    VMMDevHGCMParmType_LinAddr_Locked     = 7,  /**&lt; Locked In and Out */
    VMMDevHGCMParmType_LinAddr_Locked_In  = 8,  /**&lt; Locked In  (read;  host&lt;-guest) */
    VMMDevHGCMParmType_LinAddr_Locked_Out = 9,  /**&lt; Locked Out (write; host-&gt;guest) */
    VMMDevHGCMParmType_PageList           = 10, /**&lt; Physical addresses of locked pages for a buffer. */
    VMMDevHGCMParmType_Embedded           = 11, /**&lt; Small buffer embedded in request. */
    VMMDevHGCMParmType_ContiguousPageList = 12, /**&lt; Like PageList but with physically contiguous memory, so only one page entry. */
    VMMDevHGCMParmType_SizeHack           = 0x7fffffff
`}` HGCMFunctionParameterType;

#  pragma pack(4)

typedef struct
`{`
    HGCMFunctionParameterType type;
    union
    `{`
        uint32_t   value32;
        uint64_t   value64;
        struct
        `{`
            uint32_t size;

            union
            `{`
                RTGCPHYS64 physAddr;
                RTGCPTR64  linearAddr;
            `}` u;
        `}` Pointer;
        struct
        `{`
            uint32_t size;   /**&lt; Size of the buffer described by the page list. */
            uint32_t offset; /**&lt; Relative to the request header, valid if size != 0. */
        `}` PageList;
        struct
        `{`
            uint32_t fFlags : 8;        /**&lt; VBOX_HGCM_F_PARM_*. */
            uint32_t offData : 24;      /**&lt; Relative to the request header, valid if cb != 0. */
            uint32_t cbData;            /**&lt; The buffer size. */
        `}` Embedded;
    `}` u;
`}` HGCMFunctionParameter64;


typedef struct VBGLIOCHGCMDISCONNECT
`{`
    /** The header. */
    VBGLREQHDR          Hdr;
    union
    `{`
        struct
        `{`
            uint32_t    idClient;
        `}` In;
    `}` u;
`}` VBGLIOCHGCMDISCONNECT;

#endif
```

### <a class="reference-link" name="hgcm.c"></a>hgcm.c

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;stdint.h&gt;
#include &lt;string.h&gt;
#include &lt;unistd.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sys/ioctl.h&gt;
#include &lt;stdarg.h&gt;
#include "hgcm.h"

void die(char *msg) `{`
   perror(msg);
   exit(-1);
`}`


//device fd
int fd;

int hgcm_connect(const char *service_name) `{`
   VBGLIOCHGCMCONNECT data = `{`
      .Hdr.cbIn = sizeof(VBGLIOCHGCMCONNECT),
      .Hdr.uVersion = VBGLREQHDR_VERSION,
      .Hdr.uType = VBGLREQHDR_TYPE_DEFAULT,
      .Hdr.rc = VERR_INTERNAL_ERROR,
      .Hdr.cbOut = sizeof(VBGLREQHDR) + sizeof(uint32_t),
      .Hdr.uReserved = 0,
      .u.In.Loc.type = VMMDevHGCMLoc_LocalHost_Existing
   `}`;
   memset(data.u.In.Loc.u.host.achName,0,128);
   strncpy(data.u.In.Loc.u.host.achName,service_name,128);
   ioctl(fd,VBGL_IOCTL_HGCM_CONNECT,&amp;data);
   if (data.Hdr.rc) `{` //error
      return -1;
   `}`
   return data.u.Out.idClient;
`}`

HGCMFunctionParameter64 arg_buf[0x100];

int hgcm_call(int client_id,int func,char *params_fmt,...) `{`
   va_list ap;
   char *p,*bval,*type;
   uint32_t ival;
   uint64_t lval;
   HGCMFunctionParameter64 params;
   uint16_t index = 0;

   va_start(ap,params_fmt);
   for(p = params_fmt;*p;p++) `{`
      if(*p!='%') `{`
         continue;
      `}`

      switch (*++p) `{`
         case 'u': //整数类型
            ival = va_arg(ap,uint32_t);
            params.type = VMMDevHGCMParmType_32bit;
            params.u.value64 = 0;
            params.u.value32 = ival;
            arg_buf[index++] = params;
            break;
         case 'l':
            lval = va_arg(ap,uint64_t);
            params.type = VMMDevHGCMParmType_64bit;
            params.u.value64 = lval;
            arg_buf[index++] = params;
         case 'b': //buffer类型
            type = va_arg(ap,char *);
            bval = va_arg(ap,char *);
            ival = va_arg(ap,uint32_t);
            if (!strcmp(type,"in")) `{`
               params.type = VMMDevHGCMParmType_LinAddr_In;
            `}` else if (!strcmp(type,"out")) `{`
               params.type = VMMDevHGCMParmType_LinAddr_Out;
            `}` else `{`
               params.type = VMMDevHGCMParmType_LinAddr;
            `}`
            params.u.Pointer.size = ival;
            params.u.Pointer.u.linearAddr = (uintptr_t)bval;
            arg_buf[index++] = params;
            break;
      `}`
   `}`
   va_end(ap);
   //printf("params count=%d\n",index);
   uint8_t *data_buf = (uint8_t *)malloc(sizeof(VBGLIOCHGCMCALL) + sizeof(HGCMFunctionParameter64)*index);
   VBGLIOCHGCMCALL data = `{`
      .Hdr.cbIn = sizeof(VBGLIOCHGCMCALL) + sizeof(HGCMFunctionParameter64)*index,
      .Hdr.uVersion = VBGLREQHDR_VERSION,
      .Hdr.uType = VBGLREQHDR_TYPE_DEFAULT,
      .Hdr.rc = VERR_INTERNAL_ERROR,
      .Hdr.cbOut = sizeof(VBGLIOCHGCMCALL) + sizeof(HGCMFunctionParameter64)*index,
      .Hdr.uReserved = 0,
      .u32ClientID = client_id,
      .u32Function = func,
      .cMsTimeout = 100000, //忽略
      .fInterruptible = 0,
      .bReserved = 0,
      .cParms = index
   `}`;
   memcpy(data_buf,&amp;data,sizeof(VBGLIOCHGCMCALL));
   memcpy(data_buf+sizeof(VBGLIOCHGCMCALL),arg_buf,sizeof(HGCMFunctionParameter64)*index);

   /*for (int i=0;i&lt;sizeof(VBGLIOCHGCMCALL)+sizeof(HGCMFunctionParameter64)*index;i++) `{`
      printf("%02x",data_buf[i]);
   `}`
   printf("\n");*/

   ioctl(fd,VBGL_IOCTL_CODE_SIZE(IOCTL_HGCM_CALL,sizeof(VBGLIOCHGCMCALL) + sizeof(HGCMFunctionParameter64)*index),data_buf);
   int error = ((VBGLIOCHGCMCALL *)data_buf)-&gt;Hdr.rc;
   free(data_buf);

   if (error) `{` //error
      return error;
   `}`
   /*for (int i=0;i&lt;sizeof(VBGLIOCHGCMCALL)+sizeof(HGCMFunctionParameter64)*index;i++) `{`
      printf("%02x",data_buf[i]);
   `}`
   printf("\n");*/

   return 0;
`}`

int hgcm_disconnect(int client_id) `{`
   VBGLIOCHGCMDISCONNECT data = `{`
      .Hdr.cbIn = sizeof(VBGLIOCHGCMDISCONNECT),
      .Hdr.uVersion = VBGLREQHDR_VERSION,
      .Hdr.uType = VBGLREQHDR_TYPE_DEFAULT,
      .Hdr.rc = VERR_INTERNAL_ERROR,
      .Hdr.cbOut = sizeof(VBGLREQHDR),
      .Hdr.uReserved = 0,
      .u.In.idClient = client_id,
   `}`;
   ioctl(fd,VBGL_IOCTL_HGCM_DISCONNECT,&amp;data);
   if (data.Hdr.rc) `{` //error
      return -1;
   `}`
   return 0;
`}`

int main() `{`
   //打开设备
   fd = open("/dev/vboxuser",O_RDWR);
   if (fd == -1) `{`
      die("open device error");
   `}`
   int idClient = hgcm_connect("VBoxGuestPropSvc");
   printf("idClient=%d\n",idClient);
   char ans[0x100] = `{`0`}`;
   int ret = hgcm_call(idClient,2,"%b%b","in","foo",4,"in","bar",4);
   ret = hgcm_call(idClient,1,"%b%b%u%u","in","foo",4,"out",ans,0x100,0,0);

   printf("%s\n",ans);
   printf("%d\n",hgcm_disconnect(idClient));
`}`
```



## 0x03 感想

学习漏洞挖掘，不应该只依赖于现成的库或工具，就像本文，虽然`niklasb`大牛已经封装了`3dpwn`库，但是对于我们研究员来说，还是得先自己弄懂，自己动手写工具，才能明白其本质。



## 0x04 参考链接

[Investigating generic problems with the Linux Guest Additions](https://www.virtualbox.org/wiki/LinuxAdditionsDebug)<br>[corelabs-Breaking_Out_of_VirtualBox_through_3D_Acceleration-Francisco_Falcon.pdf](https://www.coresecurity.com/sites/default/files/private-files/publications/2016/05/corelabs-Breaking_Out_of_VirtualBox_through_3D_Acceleration-Francisco_Falcon.pdf)
