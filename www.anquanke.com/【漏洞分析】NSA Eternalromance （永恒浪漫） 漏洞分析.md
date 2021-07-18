
# 【漏洞分析】NSA Eternalromance （永恒浪漫） 漏洞分析


                                阅读量   
                                **129909**
                            
                        |
                        
                                                                                    



**[![](./img/85918/t01973c96a737e38720.png)](./img/85918/t01973c96a737e38720.png)**

**传送门**

****

[**【漏洞分析】MS 17-010：NSA Eternalblue SMB 漏洞分析**](http://bobao.360.cn/learning/detail/3738.html)



**1 环境**

**EXPLOIT：**

Eternalromance-1.3.0

**TARGET：**

windows xp sp3

**FILE：**

srv.sys 5.1.2600.5512

**<br>**

**2 Exploit使用**

我们可以发现工具包中有两个Eternalromance, 一个1.4.0, 另外一个是1.3.0。经过我一翻折腾也没有把1.4.0跑起来。无奈试了下1.3.0发现竟然能成功运行。因此便有了这篇分析。大家可能都会用fuzzbunch这个命令行了。但是我们调试的时候总不能调一次都要重新输入TargetIp等那些配置吧。告诉大家一个省劲的方法。首先fuzzbunch按正常流程走一遍。在最后跑起exp的时候，在Log目录下会生成一个xml的配置文件。然后大家就可以用Eternalromance.1.3.0 –inconfig “xml路径” 来调用了。还有就是你也可以改exploit下的那个配置文件不过你得填非常多的参数。

**<br>**

**3 基础知识**

不想看的同学可以直接跳到 3.5 漏洞相关的重点那里

**3.1 SMB Message structure**

SMB Messages are divisible into three parts:

*** fixed-length header**

*** variable length parameter block**

*** variable length data block**

header的结构如下：

```
SMB_Header
   {
   UCHAR  Protocol[4];
   UCHAR  Command;
   SMB_ERROR Status;
   UCHAR  Flags;
   USHORT Flags2;
   USHORT PIDHigh;
   UCHAR  SecurityFeatures[8];
   USHORT Reserved;
   USHORT TID;
   USHORT PIDLow;
   USHORT UID;
   USHORT MID;
   }
```

更详细见 ([https://msdn.microsoft.com/en-us/library/ee441702.aspx](https://msdn.microsoft.com/en-us/library/ee441702.aspx) )

**3.2 SMB_COM_TRANSACTION (0x25)**

为事务处理协议的传输子协议服务。这些命令可以用于CIFS文件系统内部通信的邮箱和命名管道。如果出书的数据超过了会话建立时规定的MaxBufferSize，必须使用SMB_COM_TRANSACTION_SECONDARY命令来传输超出的部分：SMB_Data.Trans_Data和SMB_Data.Trans_Parameter。这两部分在初始化消息中没有固定。

如果客户端没有发送完所有的SMB_Data.Trans_Data，会将DataCount设置为小于TotalDataCount的一个值。同样的，如果SMB_Data.Trans_Parameters没有发送完，会设置ParameterCount为一个小于TotalParameterCount的值。参数部分优先级高于数据部分，客户端在每个消息中应该尽量多的发送数据。服务器应该可以接收无序到达的SMB_Data.Trans_Parameters 和 SMB_Data.Trans_Data，不论是大量还是少量的数据。

在请求和响应消息中，SMB_Data.Trans_Parameters和SMB_Data.Trans_Data的位置和长度都是由SMB_Parameters.ParameterOffset、SMB_Parameters.ParameterCount,SMB_Parameters.DataOffset和SMB_Parameters.DataCount决定。另外需要说明的是，SMB_Parameters.ParameterDisplacement和SMB_Parameters.DataDisplacement可以用来改变发送数据段的序号。服务器应该优先发送SMB_Data.Trans_Parameters。客户端应该准备好组装收到的SMB_Data.Trans_Parameters和SMB_Data.Trans_Data，即使它们是乱序到达的。

The PID, MID, TID, and UID MUST be the same for all requests and responses that are part of the same transaction.

更详细看 ([https://msdn.microsoft.com/en-us/library/ee441489.aspx](https://msdn.microsoft.com/en-us/library/ee441489.aspx) )

**3.3 SMB_COM_TRANSACTION_SECONDARY(0x26)**

此命令用来完成SMB_COM_TRANSACTION中未传输完毕数据的传输。在请求和响应消息中，SMB_Data.Trans_Parameters和SMB_Data.Trans_Data的位置和长度都是由SMB_Parameters.ParameterOffset、SMB_Parameters.ParameterCount,SMB_Parameters.DataOffset和SMB_Parameters.DataCount决定。另外需要说明的是，SMB_Parameters.ParameterDisplacement和SMB_Parameters.DataDisplacement可以用来改变发送数据段的序号。服务器应该优先发送SMB_Data.Trans_Parameters。客户端应该准备好组装收到的SMB_Data.Trans_Parameters和SMB_Data.Trans_Data，即使它们是乱序到达的。

更详细看 ([https://msdn.microsoft.com/en-us/library/ee441949.aspx](https://msdn.microsoft.com/en-us/library/ee441949.aspx) )

**3.4 SMB_COM_WRITE_ANDX (0x2F)**

结构如图：

[![](./img/85918/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011fda792f0f66b20a.png)

更详细看 ([https://msdn.microsoft.com/en-us/library/ee441848.aspx](https://msdn.microsoft.com/en-us/library/ee441848.aspx) )

**3.5 总结下漏洞相关的重点**

客户端处理SMB_COM_TRANSACTION命令的时候如果数据大小超过MaxBufferSize，则需要使用SMB_COM_TRANSACTION_SECONDARY传输剩下的数据。

对于作为同一Transcation部分的所有请求和响应，PID，MID，TID和UID必须相同。

**<br>**

**4 漏洞分析**

**4.1 SrvSmbTransactionSecondary**

结合上一节的重点中提到的。

如果我们先发送了一个数据大小大于MaxBufferSize的SMB_COM_TRANSACTION数据包。那么接下来肯定是要发送SMB_COM_TRANSACTION_SECONDARY来传输剩余的数据，那么服务器在收到处理SMB_COM_TRANSACTION_SECONDARY这个命令的时候肯定会找他对应的那个Transcation。同时服务器也可能同时收到很多个包含SMB_COM_TRANSACTION_SECONDARY命令的数据包。怎么定位某个MB_COM_TRANSACTION_SECONDARY数据包对应的SMB_COM_TRANSACTION数据包呢？重点里也提到了。如果MB_COM_TRANSACTION_SECONDARY数据包中的PID,MID,TID和UID和SMB_COM_TRANSACTION数据包中的相同，那么就认为是同一部分的请求。

代码是这么实现的。

```
int __thiscall SrvSmbTransactionSecondary(int this)
{
  int v1; // ebx@1
  int pSmbParamter; // edi@1
  TRANSCATION *pTransation; // eax@1 MAPDST
  unsigned int ParameterDisplayment; // ecx@10 MAPDST
  size_t ParameterSize; // eax@10 MAPDST
  size_t DataSize; // edx@10 MAPDST
  int pTransList; // [sp+Ch] [bp-24h]@1
  PERESOURCE Resource; // [sp+18h] [bp-18h]@26
  struct _ERESOURCE *Resourcea; // [sp+18h] [bp-18h]@30
  int pSmbHeader; // [sp+1Ch] [bp-14h]@1
  int ParameterOffset; // [sp+20h] [bp-10h]@10
  int DataOffset; // [sp+28h] [bp-8h]@10
  v1 = this;
  pSmbParamter = *(_DWORD *)(this + 0x6C);
  pSmbHeader = *(_DWORD *)(this + 0x68);
  pTransList = *(_DWORD *)(this + 0x4C);
  //
  // 首先查找SMB_COM_TRANSACTION_SECONDARY对应的SMB_COM_TRANSACTION
  //
  pTransation = (TRANSCATION *)SrvFindTransaction(pTransList, pSmbHeader, 0);
  if ( !pTransation )
  {
    return 2;
  }
  if ( !*(_BYTE *)(pTransation-&gt;field_10 + 0x98) )
  {
    ParameterDisplayment = *(_WORD *)(pSmbParamter + 9);
    ParameterOffset = *(_WORD *)(pSmbParamter + 7);
    ParameterSize = *(_WORD *)(pSmbParamter + 5);
    DataOffset = *(_WORD *)(pSmbParamter + 0xD);
    DataSize = *(_WORD *)(pSmbParamter + 0xB);
    DataDisplayment = *(_WORD *)(pSmbParamter + 0xF);
    if ( pTransation-&gt;field_93 )
    {
        //...
    }
    else
    {
      //Check
      Resource = *(PERESOURCE *)(*(_DWORD *)(v1 + 0x60) + 0x10);
      if ( ParameterSize + ParameterOffset &gt; *(_DWORD *)(*(_DWORD *)(v1 + 0x60) + 0x10)
        || DataOffset + DataSize &gt; (unsigned int)Resource
        || ParameterSize + ParameterDisplayment &gt; pTransation-&gt;TotalParameterCount
        || DataSize + DataDisplayment &gt; pTransation-&gt;TotalDataCount )
      {
         //CheckFaild
      }
      else
      {
        if ( pTransation-&gt;field_94 != 1 )
        {
          //
          // 这里将SMB_COM_TRANSACTION_SECONDARY传过来的Parameter和Data都保存
          // 到Transaction中
          //
          //拷贝Parameter Buffer
          if ( ParameterSize )
            _memmove(
              (void *)(ParameterDisplayment + pTransation-&gt;ParameterBuffer),
              (const void *)(pSmbHeader + ParameterOffset),
              ParameterSize);                   // parameter
          //复制Data Buffer,这里注意下，下面会提到！！
          if ( DataSize )
            _memmove(
              (void *)(DataDisplayment + pTransation-&gt;DataBuffer),
              (const void *)(pSmbHeader + DataOffset),
              DataSize);                        // data
          return 2;
        }
      }
    }
  }
  return 1;
}
```

这个SMB_COM_TRANSACTION_SECONDARY命令的处理函数的大体流程就是首先查找SMB_COM_TRANSACTION_SECONDARY对应的SMB_COM_TRANSACTION如果找到就将SMB_COM_TRANSACTION_SECONDARY中的Parameter和Data都复制到SMB_COM_TRANSACTION中去。

**4.2 SrvFindTransaction**

下面来看下查找的逻辑SrvFindTransaction:

```
int __stdcall SrvFindTransaction(int a1, int pSmbHeaderOrMid, int a3)
{
  SMB_HEADER *pSmbHeader_; // edi@1
  struct _ERESOURCE *v4; // ebx@4
  _DWORD **pTransList; // edx@4
  _DWORD *i; // ecx@4
  TRANSCATION *v7; // eax@5
  int v9; // esi@14
  pSmbHeader_ = (SMB_HEADER *)pSmbHeaderOrMid;
  //
  // command 0x2f is SUM_CMD_WRITE_ANDX
  // a3 = SUM_CMD_WRITE_ANDX-&gt;Fid
  //
  if ( *(_BYTE *)(pSmbHeaderOrMid + 4) == 0x2F )
    pSmbHeaderOrMid = a3;
  else
    LOWORD(pSmbHeaderOrMid) = *(_WORD *)(pSmbHeaderOrMid + 0x1E);
  v4 = (struct _ERESOURCE *)(a1 + 0x130);
  ExAcquireResourceExclusiveLite((PERESOURCE)(a1 + 0x130), 1u);
  pTransList = (_DWORD **)(*(_DWORD *)(a1 + 0xF4) + 8);
  for ( i = *pTransList; ; i = (_DWORD *)*i )
  {
    if ( i == pTransList )
    {
      //
      // 查到最后了退出
      //
      ExReleaseResourceLite(v4);
      return 0;
    }
    //
    // 这里是对比TID，PID，UID,MID
    // 这里注意这个MID,如果命令是SUM_CMD_WRITE_ANDX MID就是SUM_CMD_WRITE_ANDX MID数据包中的Fid
    //
    v7 = (TRANSCATION *)(i - 6);
    if ( *((_WORD *)i + 47) == pSmbHeader_-&gt;TID
      &amp;&amp; v7-&gt;ProcessId == pSmbHeader_-&gt;PIDLow
      &amp;&amp; v7-&gt;UserId == pSmbHeader_-&gt;UID
      &amp;&amp; v7-&gt;MutiplexId == (_WORD)pSmbHeaderOrMid )// MutilplexId如果名令时SMB_CMD_WRITE_ANDX那么这里是Fid
    {
      break;
    }
  }
  if ( BYTE1(v7-&gt;field_0) == 2 )
  {
    _InterlockedExchangeAdd((volatile signed __int32 *)(v7-&gt;field_8 + 4), 1u);
    v9 = (int)(i - 6);
  }
  else
  {
    v9 = 0;
  }
  ExReleaseResourceLite(v4);
  return v9;
}
```

大家可以看下逻辑。重点在这里如果命令是SMB_CMD_WRITE_ANDX(0x2f)话那么MID的对比就不一样了，这里是用Transaction-&gt;MID和SMB_CMD_WRITE_ANDX-&gt;Fid比较。如果一样返回pTransaction。那么问题来了。如果服务器端正好有一个其他的Transaction-&gt;MID恰好和SMB_CMD_WRITE_ANDX-&gt;Fid的相等那么将会返回一个错误的pTransaction。很经典的类型混淆。

处理SUM_CMD_WRITE_ANDX的函数SrvSmbWriteAndX代码如下:

```
signed int __thiscall SrvSmbWriteAndX(int this)
{
    ...略
      pTrans = (TRANSCATION *)SrvFindTransaction(pTransList, pSmbTranscationBuffer, Fid);
      pTrans_ = pTrans;
      if ( !pTrans )
      {
        if ( (unsigned int)SrvWmiEnableLevel &gt;= 2 &amp;&amp; SrvWmiEnableFlags &amp; 1 &amp;&amp; KeGetCurrentIrql() &lt; 2u )
          WPP_SF_(64, &amp;unk_1E1CC);
        v40 = "d:\xpsp\base\fs\srv\smbrdwrt.c";
        v37 = 3216;
        goto LABEL_69;
      }
      if ( pTrans-&gt;TotalDataCount - pTrans-&gt;nTransDataCounts &lt; v11 )
      {
        SrvCloseTransaction(pTrans);
        SrvDereferenceTransaction(pTrans_);
        _SrvSetSmbError2(v1, 0x80000005, 0, 3238, (int)"d:\xpsp\base\fs\srv\smbrdwrt.c");
        StatusCode = 0x80000005;
        goto LABEL_100;
      }
      v31 = Size;
      qmemcpy((void *)pTrans-&gt;DataBuffer, VirtualAddress, Size);
      //
      // ！！！！这里将DataBuffer指针给增加了！！！！
      //
      pTrans_-&gt;DataBuffer += Size;
      pTrans_-&gt;nTransDataCounts += v31;
    ...略
}
```

看到pTrans_-&amp;gt;DataBuffer += Size这句相信大家就能明白了。这里将DataBuffer的指针增大了。再处理此Transcation的SMB_COM_TRANSACTION_SECONDARY命令的时候也就是SrvSmbTransactionSecondary中复制Data的memcpy可就越界了！！！！！

所以此漏洞可以总结成类型混淆造成的越界写。

**4.3 Exploit数据包**

通过对Exploit抓包我们可以看到其漏洞触发过程。

首先发送SMB_COM_TRANSACTION命令创建一个TID=2049 PID=0 UID=2049 MID=16385(0x4001)的Transcation：

[![](./img/85918/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f0e95b5749b0608e.png)

然后发送SMB_CMD_WRITE_ANDX命令还增加pTrans_-&amp;gt;DataBuffer这个指针：

[![](./img/85918/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01aa2cb84850da9d56.png)

**<br>**

**5 漏洞利用**

从上面描述可以看出，该漏洞为类型混淆导致的越界写漏洞。前期通过spray 使多个TRANSACTION相邻，然后让其中一个TRANSACTION触发该漏洞，再通过该TRANSACTION越界写其相邻的TRANSACTION

spary 最终 memory view:

[![](./img/85918/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012e6576a28a96ff64.png)

spray的目的是构造出下出三个相邻的transaction, 其中write_transaction 主要用于写操作，leak_transaction 主要用于信息泄露，而control_transaction为触发漏洞的transaction,触发之后其他InData字段会增加0x200, 以致于可写的范围可以向后延伸0x200.利用于这点可以写与其相依的write_transaction的InData字段。从面达到任意地址写的效果。

注: 本次调试中 control_transaction地址为：0x58b90, write_transaction地址为: 0x59c38, leak_transaction地址为:0x5ace0

其中TRANSACTION 结构部份如下：

```
typedef struct _TRANSACTION {
    //...
    /*+0xc*/     LPVOID Connection;
    //...
    /*+0x34*/    LPWORD InSetup;
    //...
    /*+0x40*/    LPBYTE OutParameters;
    /*+0x44*/    LPBYTE InData; /*写的目的地址*/
    /*+0x48*/   LPBYTE OutData; /*读的目的地址*/
    //...
    /*+0x60*/   DWORD DataCount; /*控制可读的长度*/
    /*+0x64*/   DWORD TotalDataCount
    }TRANSACTION
```

写操作：

```
SMB_PROCESSOR_RETURN_TYPE SrvSmbTransactionSecondary (
    SMB_PROCESSOR_PARAMETERS
    )
{
    //...
    request = (PREQ_TRANSACTION_SECONDARY)WorkContext-&gt;RequestParameters;
    header = WorkContext-&gt;RequestHeader;
    transaction = SrvFindTransaction( connection, header, 0 );
    //...
    dataOffset = SmbGetUshort( &amp;request-&gt;DataOffset );
    dataCount = SmbGetUshort( &amp;request-&gt;DataCount );
    dataDisplacement = SmbGetUshort( &amp;request-&gt;DataDisplacement );
    //...
    // Copy the parameter and data bytes that arrived in this SMB.
    //...
    if ( dataCount != 0 ) {
        RtlMoveMemory(
            transaction-&gt;InData + dataDisplacement,
            (PCHAR)header + dataOffset,
            dataCount);
    }
    //...
}
```

读操作：

```
VOID SrvCompleteExecuteTransaction (
    IN OUT PWORK_CONTEXT WorkContext,
    IN SMB_TRANS_STATUS ResultStatus)
{
    //...
    transaction = WorkContext-&gt;Parameters.Transaction;
    header = WorkContext-&gt;ResponseHeader;
    transactionCommand = (UCHAR)SmbGetUshort( &amp;transaction-&gt;InSetup[0] );
    //...
        // Copy the appropriate parameter and data bytes into the message.
        if ( paramLength != 0 ) {
            RtlMoveMemory( paramPtr, transaction-&gt;OutParameters, paramLength );
        }
        if ( dataLength != 0 ) {
            RtlMoveMemory( dataPtr, transaction-&gt;OutData, dataLength );
        }
    //...
}
```

从exp运行的log可以看出该漏洞利用分为两部份：信息泄露 与 代码执行

[![](./img/85918/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013548a68038b8c8ca.png)

**5.1 信息泄露**

需要泄露的信息包括 Transaction2Dispatch Table基址 与 一块NonePagedPool Buffer地址. 通过修改Transaction2Dispatch Table中的函数指针来执行 shellcode， 其中NonePagedPool Buffer就是用于存放shellcode.

**5.1.1 泄露Transaction2Dispatch Table基址**

从exp运行的log可以看出首先泄露CONNECTION结构基址：CONNECTION地址存放于TRANSACTION-&amp;gt;Connection字段。看到这，你可能已经想到该怎么做了：直接利用constrol transaction的0x200字节的越界能力修改write_transaction的DataCount字段让其可以越界读leak_transaction上的内容，从而读出TRANSACTION-&amp;gt;Connection。 但exp作者却并没有这么做，这里并不打算深究其原因，或许是有其他限制，或许不是。

作者这里利用了另一种复杂不少方法，通过另一种方法修改 write_transaction的DataCount字段。

**5.1.1.1 write_transaction初始状态如下:**

[![](./img/85918/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01640474a166d43c96.png)

可以看出CONNECTION地址为：89a29c18，OutData为0x5acd4 (== 59c38+0x109c)已经是write_transaction的末尾，所以其DataCount为0,表示不可读。

**5.1.1.2 修改write_transaction-&gt;DataCount**

首先 修改write_transaction的InSetup为0x23，这点通过control_transaction很容易完成。之后发包触发写write_transaction操作，会走到：

```
SMB_STATUS SRVFASTCALL ExecuteTransaction (
    IN OUT PWORK_CONTEXT WorkContext)
{
    //...
    transaction = WorkContext-&gt;Parameters.Transaction;
    //...
            command = SmbGetUshort(&amp;transaction-&gt;InSetup[0]);
            //...
            switch( command ) {
            case TRANS_TRANSACT_NMPIPE:
                resultStatus = SrvTransactNamedPipe( WorkContext );
                break;
            case TRANS_PEEK_NMPIPE: //0x23
                resultStatus = SrvPeekNamedPipe( WorkContext );
                break;
            case TRANS_CALL_NMPIPE:
                resultStatus = SrvCallNamedPipe( WorkContext );
                break;
            //...
        }
        //...
}
```

由于之前已经将write_transaction的InSetup修改为0x23, 所以会call SrvPeekNamedPipe。

```
# ChildEBP RetAddr               
00 b21f8d44 b24cdcce srv!ExecuteTransaction+0x23b (FPO: [0,0,0])
01 b21f8d7c b248a836 srv!SrvSmbTransactionSecondary+0x2f1 (FPO: [Non-Fpo])
02 b21f8d88 b249ad98 srv!SrvProcessSmb+0xb7 (FPO: [0,0,0])
03 b21f8dac 805c7160 srv!WorkerThread+0x11e (FPO: [Non-Fpo])
04 b21f8ddc 80542dd2 nt!PspSystemThreadStartup+0x34 (FPO: [Non-Fpo])
05 00000000 00000000 nt!KiThreadStartup+0x16
SrvPeekNamedPipe() 调用IoCallDriver最终调到 RestartPeekNamedPipe()函数 
VOID SRVFASTCALL RestartPeekNamedPipe (
    IN OUT PWORK_CONTEXT WorkContext)
{
    //...
    //
    // Success.  Generate and send the response.
    //
    transaction = WorkContext-&gt;Parameters.Transaction;
    pipePeekBuffer = (PFILE_PIPE_PEEK_BUFFER)transaction-&gt;OutParameters;
    readDataAvailable = (USHORT)pipePeekBuffer-&gt;ReadDataAvailable;
    messageLength = (USHORT)pipePeekBuffer-&gt;MessageLength;
    namedPipeState = (USHORT)pipePeekBuffer-&gt;NamedPipeState;
    //
    // ... then copy them back in the new format.
    //
    respPeekNmPipe = (PRESP_PEEK_NMPIPE)pipePeekBuffer;
    SmbPutAlignedUshort(
        &amp;respPeekNmPipe-&gt;ReadDataAvailable,
        readDataAvailable
        );
    SmbPutAlignedUshort(
        &amp;respPeekNmPipe-&gt;MessageLength,
        messageLength
        );
    SmbPutAlignedUshort(
        &amp;respPeekNmPipe-&gt;NamedPipeState,
        namedPipeState
        );
    //
    // Send the response.  Set the output counts.
    //
    // NT return to us 4 ULONGS of parameter bytes, followed by data.
    // We return to the client 6 parameter bytes.
    //
    transaction-&gt;SetupCount = 0;
    transaction-&gt;ParameterCount = 6;
    transaction-&gt;DataCount = WorkContext-&gt;Irp-&gt;IoStatus.Information - (4 * sizeof(ULONG));
    //...
}
```

该函数最终会修改Transaction-&amp;gt;DataCount 为 0x23c。

```
kd&gt; ub
srv!RestartPeekNamedPipe+0x42:
b7700137 66895004        mov     word ptr [eax+4],dx
b770013b 83614c00        and     dword ptr [ecx+4Ch],0
b770013f c7415406000000  mov     dword ptr [ecx+54h],6
b7700146 8b4678          mov     eax,dword ptr [esi+78h]
b7700149 8b401c          mov     eax,dword ptr [eax+1Ch]
b770014c 83e810          sub     eax,10h
b770014f 85ff            test    edi,edi
b7700151 894160          mov     dword ptr [ecx+60h],eax
kd&gt; ?ecx+0x60
Evaluate expression: 367768 = 00059c98
kd&gt; r eax
eax=0000023c
kd&gt; dd 00059c38
00059c38  109c020c 00000000 ffdff500 89a29c18
00059c48  e1ed9900 e15e2960 0005acf8 00058ba8
00059c58  00020000 00059cd0 00002307 00000001
00059c68  00000000 00059cd4 8993b3e5 00059cd4
00059c78  00059d14 ffdff500 0005acd4 00000000
00059c88  00000000 00000006 00000000 00000ff0
00059c98  0000023c 00000000 00000001 00000000
00059ca8  00000101 08000000 0800cee6 00000000
kd&gt; k
 # ChildEBP RetAddr  
00 b7c0ed88 b76dad98 srv!RestartPeekNamedPipe+0x5f
01 b7c0edac 805c6160 srv!WorkerThread+0x11e
02 b7c0eddc 80541dd2 nt!PspSystemThreadStartup+0x34
03 00000000 00000000 nt!KiThreadStartup+0x16
```

至此，已经成功修改了write_transaction的DataCount值，之后便可以越界读出 leak_transacion-&amp;gt;Connection值: 89a29c18。

**5.1.1.3 SRV global data pointer**

```
kd&gt; dds 89a29c18
89a29c18  02580202
89a29c1c  0000001d
89a29c20  00000000
89a29c24  00000000
89a29c28  00000000
89a29c2c  00000000
89a29c30  00000000
89a29c34  00000000
89a29c38  00000000
89a29c3c  b76d8bec srv!SrvGlobalSpinLocks+0x3c
89a29c40  899d0020
89a29c44  000005b3
89a29c48  8976c200
89a29c4c  00004000
89a29c50  10000100
89a29c54  00000000
89a29c58  8988e010
89a29c5c  89aedc30
89a29c60  89a7d898
89a29c64  0001ffff
```

其中srv!SrvGlobalSpinLocks+0x3c 就是所谓的 SRV global data pointer ：b76d8bec

**5.1.1.4 Locating function tables**

```
kd&gt; dds b76d8bec-0x654
b76d8598  b7709683 srv!SrvSmbOpen2
b76d859c  b76f62a8 srv!SrvSmbFindFirst2
b76d85a0  b76f74e5 srv!SrvSmbFindNext2
b76d85a4  b76f6309 srv!SrvSmbQueryFsInformation
b76d85a8  b7707293 srv!SrvSmbSetFsInformation
b76d85ac  b77041ad srv!SrvSmbQueryPathInformation
b76d85b0  b7703ce7 srv!SrvSmbSetPathInformation
b76d85b4  b77025ad srv!SrvSmbQueryFileInformation
b76d85b8  b770367f srv!SrvSmbSetFileInformation
b76d85bc  b7705c85 srv!SrvSmbFsctl
b76d85c0  b7706419 srv!SrvSmbIoctl2
b76d85c4  b7705c85 srv!SrvSmbFsctl
b76d85c8  b7705c85 srv!SrvSmbFsctl
b76d85cc  b77047bb srv!SrvSmbCreateDirectory2
b76d85d0  b7709a51 srv!SrvTransactionNotImplemented
b76d85d4  b7709a51 srv!SrvTransactionNotImplemented
b76d85d8  b76fb144 srv!SrvSmbGetDfsReferral
b76d85dc  b76faf7e srv!SrvSmbReportDfsInconsistency
b76d85e0  00000000
```

**5.1.2 泄露Npp Buffer (shellcode buffer)**

这里又得回到ExecuteTransaction函数：

```
SMB_STATUS SRVFASTCALL ExecuteTransaction (
    IN OUT PWORK_CONTEXT WorkContext)
{
    //...
    header = WorkContext-&amp;gt;ResponseHeader;
    response = (PRESP_TRANSACTION)WorkContext-&amp;gt;ResponseParameters;
    ntResponse = (PRESP_NT_TRANSACTION)WorkContext-&amp;gt;ResponseParameters;
    //
    // Setup output pointers
    //
    if ( transaction-&amp;gt;OutParameters == NULL ) {
        //
        // Parameters will go into the SMB buffer.  Calculate the pointer
        // then round it up to the next DWORD address.
        //
        transaction-&amp;gt;OutParameters = (PCHAR)(transaction-&amp;gt;OutSetup +
            transaction-&amp;gt;MaxSetupCount);
        offset = (transaction-&amp;gt;OutParameters - (PCHAR)header + 3) &amp;amp; ~3;
        transaction-&amp;gt;OutParameters = (PCHAR)header + offset;
    }
    if ( transaction-&amp;gt;OutData == NULL ) {
        //
        // Data will go into the SMB buffer.  Calculate the pointer
        // then round it up to the next DWORD address.
        //
        transaction-&amp;gt;OutData = transaction-&amp;gt;OutParameters +
            transaction-&amp;gt;MaxParameterCount;
        offset = (transaction-&amp;gt;OutData - (PCHAR)header + 3) &amp;amp; ~3;
        transaction-&amp;gt;OutData = (PCHAR)header + offset;
    }
            //...
            command = SmbGetUshort(&amp;amp;transaction-&amp;gt;InSetup[0]);
            //...
            switch( command ) {
            case TRANS_TRANSACT_NMPIPE:
                resultStatus = SrvTransactNamedPipe( WorkContext );
                break;
            case TRANS_PEEK_NMPIPE:
                resultStatus = SrvPeekNamedPipe( WorkContext );
                break;
            //...
}
```

这在这个函数里有这么一个逻辑，当transaction-&amp;gt;OutParameters==NULL里，会将PWORK_CONTEXT-&amp;gt;ResponseHeader加上一定的offset赋于它，PWORK_CONTEXT-&amp;gt;ResponseHeader就是个NonePagedPool.

```
kd&gt; ub eip
srv!ExecuteTransaction+0x60:
b76e8d05 46              inc     esi
b76e8d06 50              push    eax
b76e8d07 d1e0            shl     eax,1
b76e8d09 2bc2            sub     eax,edx
b76e8d0b 8d440803        lea     eax,[eax+ecx+3]
b76e8d0f 83e0fc          and     eax,0FFFFFFFCh
b76e8d12 03c2            add     eax,edx
b76e8d14 894640          mov     dword ptr [esi+40h],eax
kd&gt; dd 5ace0
0005ace0  109c020c 00000000 89b2c948 89a29c18
0005acf0  e1ed9900 e15e2960 0005bda0 00059c50
0005ad00  00020000 0005ad78 00002361 40010036
0005ad10  00000000 0005ad0c 8993fa25 0005ad7c
0005ad20  8993fa28 0005ad7c b76d84ec 00000004
0005ad30  00000000 00000000 00000000 00000010
0005ad40  00000000 00000000 00000100 00000000
0005ad50  00000101 08000000 0800cee6 0000004b
kd&gt; ? esi+0x40
Evaluate expression: 372000 = 0005ad20
kd&gt; r eax
eax=8993fa28
```

**5.1.2.1 transaction-&gt;OutParameters=NULL**

Transaction 初始状态下OutParameters并不为NULL：

```
kd&gt; dd 5ace0
0005ace0  109c020c 00000000 89b2c948 89a29c18
0005acf0  e1ed9900 e15e2960 0005bda0 00059c50
0005ad00  00020000 0005ad78 00002361 00000001
0005ad10  00000000 0005ad7c 00000000 0005ad7c
0005ad20  0005adbc 0005ad7c 0005bd7c 00000000
0005ad30  00000000 00000000 00000000 00000fc0
0005ad40  00000000 00000040 00000000 00000000
0005ad50  00000101 08000000 0800cee6 0000004b
```

这里通过write_transaction越界 写 leak_transaction-&amp;gt;OutParameters为NULL, 然后发包触发写leak_transaction操作，之后leak_transaction-&amp;gt;OutParameters便为一 Npp Buffer值了。

**5.1.2.2 leak_transaction-&gt;OutData = &amp;leak_transaction-&gt;OutParameters**

这里要事先泄露leak_transaction的基址，其实也不难，通过读leak_transaction的OutData 或 OutParameters 或 InData 字段的值再减去一定的偏移便得到了基址，使leak_transaction-&amp;gt;OutData = &amp;amp;leak_transaction-&amp;gt;OutParameters之后，发包触发leak_transaction读操作便将该Npp buffer地址泄露出来了。

**5.1.2.3 写shellcode到Npp Buffer**

将control_transaction-&amp;gt;OutData设为Npp Buffer+0x100地址，然后发包发送shellcode，便将shellcode写到了Npp Buffer+0x100内。

**5.2 代码执行**

至此，直接将Npp buffer+0x100写到之前泄露出来的函数表里

```
kd&gt; dds b76d8598
b76d8598  b7709683 srv!SrvSmbOpen2
b76d859c  b76f62a8 srv!SrvSmbFindFirst2
b76d85a0  b76f74e5 srv!SrvSmbFindNext2
b76d85a4  b76f6309 srv!SrvSmbQueryFsInformation
b76d85a8  b7707293 srv!SrvSmbSetFsInformation
b76d85ac  b77041ad srv!SrvSmbQueryPathInformation
b76d85b0  b7703ce7 srv!SrvSmbSetPathInformation
b76d85b4  b77025ad srv!SrvSmbQueryFileInformation
b76d85b8  b770367f srv!SrvSmbSetFileInformation
b76d85bc  b7705c85 srv!SrvSmbFsctl
b76d85c0  b7706419 srv!SrvSmbIoctl2
b76d85c4  b7705c85 srv!SrvSmbFsctl
b76d85c8  b7705c85 srv!SrvSmbFsctl
b76d85cc  b77047bb srv!SrvSmbCreateDirectory2
b76d85d0  8993fb28
b76d85d4  b7709a51 srv!SrvTransactionNotImplemented
b76d85d8  b76fb144 srv!SrvSmbGetDfsReferral
b76d85dc  b76faf7e srv!SrvSmbReportDfsInconsistency
b76d85e0  00000000
```

之后发包就能触发该函数调用：

```
kd&gt; k
 # ChildEBP RetAddr  
WARNING: Frame IP not in any known module. Following frames may be wrong.
00 b72b4cf0 b76e8d76 0x8993fb28
01 b72b4d04 b76e341f srv!ExecuteTransaction+0xdb
02 b72b4d7c b76ca836 srv!SrvSmbTransaction+0x7ac
03 b72b4d88 b76dad98 srv!SrvProcessSmb+0xb7
04 b72b4dac 805c6160 srv!WorkerThread+0x11e
05 b72b4ddc 80541dd2 nt!PspSystemThreadStartup+0x34
06 00000000 00000000 nt!KiThreadStartup+0x16
```



**6 关于补丁**

了解了漏洞原理之后修补都很简单了。只要在srv!SrvFindTransaction里面判断一下SMB COMMAND的类型是否一致就好了。

修补前



```
TRANSCATION *__fastcall SrvFindTransaction(int pConnect, SMB_HEADER *Fid, __int16 a3)
{
  _DWORD **pTransList; // eax@4
  _DWORD *v6; // ebx@4
  PDEVICE_OBJECT v7; // ecx@5
  TRANSCATION *pTransaction; // esi@6
  char Command_Trans; // al@10
  char Command_header; // dl@10
  __int16 MIDorFID; // [sp+Ch] [bp-Ch]@2
  struct _ERESOURCE *Resource; // [sp+14h] [bp-4h]@4
  if ( Fid-&gt;Command == 0x2F )
    MIDorFID = a3;
  else
    MIDorFID = Fid-&gt;MID;
  Resource = (struct _ERESOURCE *)(pConnect + 0x19C);
  ExAcquireResourceExclusiveLite((PERESOURCE)(pConnect + 0x19C), 1u);
  pTransList = (_DWORD **)(*(_DWORD *)(pConnect + 0x160) + 8);
  v6 = *pTransList;
  if ( *pTransList == pTransList )
    goto LABEL_14;
  v7 = WPP_GLOBAL_Control;
  while ( 1 )
  {
    pTransaction = (TRANSCATION *)(v6 - 6);
    if ( *((_WORD *)v6 + 49) == Fid-&gt;TID
      &amp;&amp; pTransaction-&gt;PID == Fid-&gt;PID
      &amp;&amp; pTransaction-&gt;UID == Fid-&gt;UID
      &amp;&amp; pTransaction-&gt;MID == MIDorFID )
    {
      break;
    }
LABEL_13:
    v6 = (_DWORD *)*v6;
    if ( v6 == (_DWORD *)(*(_DWORD *)(pConnect + 0x160) + 8) )
      goto LABEL_14;
  }
  //
  // 这里添加了对COMMAND的比较。比较pTransaction和请求中SMB_HEADER中的COMMAND进行对比
  //
  Command_Trans = pTransaction-&gt;Command;
  Command_header = Fid-&gt;Command;
  if ( Command_Trans != Command_header )
  {
    if ( (PDEVICE_OBJECT *)v7 != &amp;WPP_GLOBAL_Control )
    {
      WPP_SF_qDD(v7-&gt;AttachedDevice, v7-&gt;CurrentIrp, (_BYTE)v6 - 24, Command_header, Command_Trans);
      v7 = WPP_GLOBAL_Control;
    }
    goto LABEL_13;
  }
  if ( BYTE1(pTransaction-&gt;field_0) == 2 )
  {
    _InterlockedIncrement((volatile signed __int32 *)(pTransaction-&gt;field_8 + 4));
    goto LABEL_15;
  }
LABEL_14:
  pTransaction = 0;
LABEL_15:
  ExReleaseResourceLite(Resource);
  return pTransaction;
}
```

补丁点就是if ( Command_Trans != Command_header )看注释的地方。

<br>

**7 总结**

总之，这个漏洞还是非常好的，远程任意地址写，还可以信息泄露。威力很大。

<br>

**8 联系作者**

[**pgboy 微博**](http://weibo.com/pgboy1988)

[**zhong_sf 微博**](http://weibo.com/2641521260)

如果你感觉排版不舒服可以去[**这里**](https://github.com/progmboy/vul_analyze_doc)下载原始的markdown文件。

<br>



**传送门**

****

[**【漏洞分析】MS 17-010：NSA Eternalblue SMB 漏洞分析**](http://bobao.360.cn/learning/detail/3738.html)

<br>
