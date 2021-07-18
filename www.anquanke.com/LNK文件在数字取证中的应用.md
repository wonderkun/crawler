
# LNK文件在数字取证中的应用


                                阅读量   
                                **767928**
                            
                        |
                        
                                                                                                                                    ![](./img/199689/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者fireeye，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2020/02/the-missing-lnk-correlating-user-search-lnk-files.html](https://www.fireeye.com/blog/threat-research/2020/02/the-missing-lnk-correlating-user-search-lnk-files.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/199689/t01445f525008a056b1.png)](./img/199689/t01445f525008a056b1.png)



## 0x00 前言

数字取证分析人员通常会使用LNK快捷方式文件来恢复关于最近访问文件（包括访问后被删除的文件）的元数据，在最近一次调查过程中，FireEye Mandiant发现了一些LNK文件，这些文件与攻击者访问过的系统文件有关（包括在Windows Explorer中的搜索痕迹）。根据我们的经验，这种新的分析技术可以结合到数字取证中。在本文中，我们将与大家分享相关研究成果，更全面地了解攻击者在目标系统上的行为及目标。此外，这些研究成果还可用于内部威胁案例，以确认搜索文件及打开文件的具体路径。



## 0x01 Windows LNK文件

`.lnk`扩展名与Shell Item文件有关，这种二进制格式的文件中包含一些信息，在Windows Shell（[图形用户接口](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-shllink/16cb4ca1-9339-4d0c-a68d-bf1d6cc0f943)）中可以用来访问其他数据对象。

LNK快捷方式文件是其中一种Shell Item，当用户通过支持该功能的应用程序访问文件时，Windows操作系统会自动创建这类文件，但这些文件也可以由用户手动创建。LNK快捷方式文件通常包含已访问文件的一些元素据，比如文件名、文件大小、原始路径、时间戳、卷及系统信息（如驱动器类型及系统主机名）、网络信息（如网络共享路径）。幸运的是，我们可以使用一些工具来解析这些文件。在Mandiant公司内部，我们通常会利用FireEye Endpoint Security来解析LNK文件，识别可疑的用户搜索项。在本文中，我们使用的是Eric Zimmerman开发的[LECmd](https://github.com/EricZimmerman/LECmd)。`LECmd.exe`提供的命令行参数如下图所示：

[![](./img/199689/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c7f9b184a2bc00b3.png)

图1. `LECmd.exe`命令行选项

在安全取证中，LNK快捷方式文件的元数据解析可应用于多个场景，比如梳理系统上的用户行为轨迹，或者搜索已删除的恶意软件的相关信息。



## 0x02 用户搜索LNK文件

Mandiant最近发现了无法正常识别的一种LNK文件，这些文件来自于Windows Server 2012 R2系统，涉及到的路径如图2所示。我们根据扩展名及文件路径，猜测这些文件属于LNK快捷方式文件，但并不熟悉文件中的内容。

```
C:\Users\&lt;user&gt;\AppData\Roaming\Microsoft\Windows\Recent\passw.lnk

C:\Users\&lt;user&gt;\AppData\Roaming\Microsoft\Windows\Recent\gov.lnk
```

图2. 特殊LNK文件的完整路径

在之前的处理案例中，取证人员会使用LNK快捷方式文件名来推测用户打开了名为`passw`或者`gov`的文件，然后使用LECmd之类的工具来提取其他元数据，这样就能获取已访问文件的完整文件路径、文件的访问时间戳以及其他取证信息。

然而，我们并没有从这些LNK文件中获取预期的元数据。LECmd对`passw.lnk`的处理结果如图3所示（为了方便演示，这里省略了部分信息）：

```
LECmd version 1.3.2.1

Author: Eric Zimmerman (saericzimmerman@gmail.com)
https://github.com/EricZimmerman/LECmd

--- Header ---
  Target created:
  Target modified:
  Target accessed:

  File size: 0
  Flags: HasTargetIdList, IsUnicode, DisableKnownFolderTracking
  File attributes: 0
  Icon index: 0
  Show window: SwNormal (Activates and displays the window. The window is restored to its original size and position if the window is minimized or maximized.)

--- Target ID information (Format: Type ==&gt; Value) ---

  Absolute path: Search Folder\passw

  -Users property view ==&gt; Search Folder
  &gt;&gt; Property store (Format: GUID\ID Description ==&gt; Value)
     d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutoList  ==&gt; VT_STREAM not implemented (yet) See extension block section for contents for now
     d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutolistCacheTime  ==&gt; 1849138729510
     d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutolistCacheKey  ==&gt; Search Results in Local Disk (C:)0

  -Variable: Users property view ==&gt; passw
  &gt;&gt; Property store (Format: GUID\ID Description ==&gt; Value)
     1e3ee840-bc2b-476c-8237-2acd1a839b22\2      (Description not available)         ==&gt; VT_STREAM not implemented
     1e3ee840-bc2b-476c-8237-2acd1a839b22\8      (Description not available)         ==&gt; passw
     28636aa6-953d-11d2-b5d6-00c04fd918d0\11     Item Type                           ==&gt; Stack
     28636aa6-953d-11d2-b5d6-00c04fd918d0\25     SFGAO Flags                         ==&gt; 805306372
     b725f130-47ef-101a-a5f1-02608c9eebac\10     Item Name Display                   ==&gt; passw

--- End Target ID information ---

--- Extra blocks information ---

&gt;&gt; Property store data block (Format: GUID\ID Description ==&gt; Value)
   (Property store is empty)
```

图3. `LECmd.exe`对`passw.lnk`的处理结果

需要注意的是，上图中我们并没有在LNK快捷文件中找到预期的信息，然而却在`Target ID Information`中却找到了一些有趣的字符串，包括`Search Folder\passw`以及`Search Results in Local Disk (C:)`。为了方便比较，我们也使用标准的LNK快捷文件来测试，输出结果如图4所示，注意其中包含目标文件时间戳、文件大小、完整文件路径以及其他文件元数据（我们也隐去了部分信息，以便展示）。

```
LECmd version 1.3.2.1

Author: Eric Zimmerman (saericzimmerman@gmail.com)
https://github.com/EricZimmerman/LECmd

--- Header ---
  Target created:  2020-01-21 19:34:28
  Target modified: 2020-01-21 19:34:28
  Target accessed: 2020-01-22 21:25:12

  File size: 4
  Flags: HasTargetIdList, HasLinkInfo, HasRelativePath, HasWorkingDir, IsUnicode, DisableKnownFolderTracking
  File attributes: FileAttributeArchive
  Icon index: 0
  Show window: SwNormal (Activates and displays the window. The window is restored to its original size and position if the window is minimized or maximized.)

Relative Path: ..\..\..\..\..\Desktop\test.txt
Working Directory: C:\Users\&lt;username&gt;\Desktop

--- Link information ---
Flags: VolumeIdAndLocalBasePath

&gt;&gt;Volume information
  Drive type: Fixed storage media (Hard drive)
  Serial number: &lt;serial number&gt;
  Label: OSDisk
  Local path: C:\Users\&lt;username&gt;\Desktop\test.txt

--- Target ID information (Format: Type ==&gt; Value) ---
  Absolute path: My Computer\Desktop\test.txt

  -Root folder: GUID ==&gt; My Computer

  -Root folder: GUID ==&gt; Desktop

  -File ==&gt; test.txt
    Short name: test.txt
    Modified: 2020-01-21 19:34:30
    Extension block count: 1

    --------- Block 0 (Beef0004) ---------
    Long name: test.txt
    Created: 2020-01-21 19:34:30
    Last access: 2020-01-21 19:34:32
    MFT entry/sequence #: 108919/8 (0x1A977/0x8)

--- End Target ID information ---

--- Extra blocks information ---

&gt;&gt; Tracker database block
   Machine ID: &lt;hostname&gt;
   MAC Address: &lt;mac address&gt;
   MAC Vendor: INTEL
   Creation: 2020-01-21 15:19:59

   Volume Droid: &lt;volume&gt;
   Volume Droid Birth: &lt;volume&gt;
   File Droid: &lt;file&gt;
   File Droid birth: &lt;file&gt;
```

图4. `LECmd.exe`对标准LNK快捷文件`test.txt`的处理结果

幸运的是，在研究过程中我们还使用了Harlan Carvey提供的[RegRipper](https://code.google.com/archive/p/regripper/downloads)来解析用户的`NTUSER.DAT`注册表文件，查看了`WorldWheelQuery`键值，该键值中包含用户在资源管理器（Explorer）中的详细搜索历史记录。在查看后，我们发现`passw.lnk`文件变得越来越有趣。我们发现历史搜索结果中包含LNK文件中的同一个关键词：`passw`。

```
wordwheelquery v.20100330
(NTUSER.DAT) Gets contents of user's WordWheelQuery key

Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery
LastWrite Time Wed Nov 13 06:51:46 2019 (UTC)

 Searches listed in MRUListEx order

14   Secret                         
6    passw                         
13   ccc                           
12   bbb                           
11   aaa                           
10   *.cfg                         
9    apple                         
8    dni                           
7    private                         
4    gov                           
5    air                           
3    intelsat                      
2    adhealthcheck                 
1    *.ps1                         
0    global

```

图5. 从用户`NTUSER.DAT`注册表文件中提取的`WorldWheelQuery`键值

通过`WorldWheelQuery`注册表键值，我们根据`MRUListEx`顺序发现`passw`这个关键词在用户资源管理器的最近搜索历史记录中排名第二位。`MRUListEx`是注册表中的一个值，按顺序给出了最近常被访问的一些元素，本质上就是资源管理器中的搜索顺序。`passw`同时也是特殊LNK文件的文件名，该文件中还包含`Search Results in Local Disk (C:)`字符串（如图3所示）。根据这些细节，我们似乎能推测这些LNK文件的创建与用户资源管理器的搜索行为有关。因此，我们将这些文件标记为“用户搜索LNK文件”。



## 0x03 抽丝剥茧

当我们使用用户资源管理器搜索历史记录中包含的关键词在系统中搜索LNK文件后，我们发现这些词都与用户搜索LNK文件有关。我们识别出了这类LNK文件以及相应的文件创建和修改时间戳，如图6所示。需要注意的是，虽然我们通过`WorldWheelQuery`注册表键值找到了15个搜索结果，但只找到了4个用户搜索LNK文件。

```
2019-11-09 08:33:14    Created Modified
C:\Users\&lt;user&gt;\AppData\Roaming\Microsoft\Windows\Recent\gov.lnk

2019-11-09 09:29:11    Created
2019-11-09 09:29:37    Modified
C:\Users\&lt;user&gt;\AppData\Roaming\Microsoft\Windows\Recent\private.lnk

2019-11-09 08:38:29    Created
2019-11-13 06:47:56    Modified
C:\Users\&lt;user&gt;\AppData\Roaming\Microsoft\Windows\Recent\passw.lnk

2019-11-13 06:57:03    Created
2019-11-13 06:57:25    Modified
C:\Users\&lt;user&gt;\AppData\Roaming\Microsoft\Windows\Recent\Secret.lnk
```

图6. `WorldWheelQuery`资源管理器搜索关键词所对应的LNK文件

此外，我们还注意到有一些LNK文件的创建时间相同，并且这些文件具有相似的文件名。比如，有两个LNK文件的创建时间都为`2019-11-09 08:38:29 UTC`，如图7所示。

```
C:\Users\&lt;user&gt;\AppData\Roaming\Microsoft\Windows\Recent\passw.lnk

C:\Users\&lt;user&gt;\AppData\Roaming\Microsoft\Windows\Recent\password.lnk
```

图7. 创建时间相同的LNK文件

进一步测试后，我们发现当用户使用资源管理器搜索，并且打开搜索结果中的文件后，系统就会创建用户搜索LNK文件。如果用户没有打开搜索结果中的文件，系统就不会创建用户搜索LNK文件。

在这个案例中，`password.lnk`文件中包含目标文件元数据（与正常LNK快捷方式文件所包含的数据类似），也引用了`T:\`目录中名为`password.txt`的目标文件。前文提到过，`passw.lnk`只包含用户搜索LNK文件元数据，包括绝对路径`Search Folder\passw`，也引用了`Search Results in Local Disk (C:)`。然而，这种目录上的差异点其实一点也不意外。

LNK快捷文件中包含最近访问文件的元数据，我们发现这一点同样适用于用户搜索LNK文件。根据`passw.lnk`不同的创建及修改时间戳，我们可知用户至少在另一种情况下搜索过`passw`（但我们并不清楚这两次搜索间是否还有其他搜索行为），并且从搜索结果中打开过一个文件。我们可以在图8中的`passw`用户搜索LNK文件中，通过查看时间戳来确认这一点：

```
2019-11-09 08:38:29    Created
2019-11-13 06:47:56    Modified
C:\Users\&lt;user&gt;\AppData\Roaming\Microsoft\Windows\Recent\passw.lnk
```

图8. `passw.lnk`创建及修改时间戳

第二次搜索`passw`的行为发生在2019年11月13日。在这次搜索中，用户再次使用Windows资源管理器来搜索`passw`关键词，但这次是在`C:\`驱动器上下文中搜索（即在本地磁盘`C:`中搜索），然后点击名为`password2.txt`的文档。LECmd对`password2.lnk`的分析结果如图9所示（这里为了保证结果清晰及保护客户隐私，我们隐去了部分信息）。需要注意的是，用户搜索LNK文件中包含的信息同样包含在同时创建的LNK快捷方式文件中。`passw.lnk`的搜索上下文以及`password2.lnk`的完整文件路径位置都一样，均为`C:\`。

```
LECmd version 1.3.2.1

Author: Eric Zimmerman (saericzimmerman@gmail.com)
https://github.com/EricZimmerman/LECmd

--- Header ---
  Target created:  2015-11-09 22:14:10
  Target modified: 2010-01-11 16:57:11
  Target accessed: 2015-11-09 22:14:10

  File size: 19
  Flags: HasTargetIdList, HasLinkInfo, HasRelativePath, HasWorkingDir, IsUnicode, DisableKnownFolderTracking
  File attributes: FileAttributeArchive
  Icon index: 0
  Show window: SwNormal (Activates and displays the window. The window is restored to its original size and position if the window is minimized or maximized.)

Relative Path: ..\..\..\..\..\..\..\&lt;file path&gt;\password2.txt
Working Directory: C:\&lt;file path&gt;

--- Link information ---
Flags: VolumeIdAndLocalBasePath, CommonNetworkRelativeLinkAndPathSuffix

&gt;&gt;Volume information
  Drive type: Fixed storage media (Hard drive)
  Serial number: &lt;serial number&gt;
  Label: (No label)

  Network share information
    Share name: \\&lt;hostname&gt;\&lt;top level folder&gt;
    Provider type: &lt;provider type&gt;
    Share flags: ValidNetType

  Local path: C:\&lt;top level folder&gt;\
  Common path: &lt;file path&gt;\password2.txt

--- Target ID information (Format: Type ==&gt; Value) ---

  Absolute path: Search Folder\passw\password2

  -Users property view ==&gt; Search Folder
  &gt;&gt; Property store (Format: GUID\ID Description ==&gt; Value)
     d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutoList  ==&gt; VT_STREAM not implemented (yet) See extension block section for contents for now
     d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutolistCacheTime  ==&gt; 1849138729510
     d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutolistCacheKey  ==&gt; Search Results in Local Disk (C:)0

  -Variable: Users property view ==&gt; passw
  &gt;&gt; Property store (Format: GUID\ID Description ==&gt; Value)
     1e3ee840-bc2b-476c-8237-2acd1a839b22\2      (Description not available)         ==&gt; VT_STREAM not implemented
     1e3ee840-bc2b-476c-8237-2acd1a839b22\8      (Description not available)         ==&gt; passw
     28636aa6-953d-11d2-b5d6-00c04fd918d0\11     Item Type                           ==&gt; Stack
     28636aa6-953d-11d2-b5d6-00c04fd918d0\25     SFGAO Flags                         ==&gt; 805306372
     b725f130-47ef-101a-a5f1-02608c9eebac\10     Item Name Display                   ==&gt; passw

  -Variable: Users property view ==&gt; password2
  &gt;&gt; Property store (Format: GUID\ID Description ==&gt; Value)
     49691c90-7e17-101a-a91c-08002b2ecda9\3      Search Rank                         ==&gt; 0
     28636aa6-953d-11d2-b5d6-00c04fd918d0\25     SFGAO Flags                         ==&gt; 1077936503
     28636aa6-953d-11d2-b5d6-00c04fd918d0\32     Delegate ID List                    ==&gt; VT_VECTOR data not implemented (yet) See extension block section for contents for now
     28636aa6-953d-11d2-b5d6-00c04fd918d0\11     Item Type                           ==&gt; .txt
     28636aa6-953d-11d2-b5d6-00c04fd918d0\24     Parsing Name                        ==&gt; password2.txt
     446d16b1-8dad-4870-a748-402ea43d788c\100    Thumbnail Cache Id                  ==&gt; 7524032674880659487
     1e3ee840-bc2b-476c-8237-2acd1a839b22\12     (Description not available)         ==&gt; Null
     1e3ee840-bc2b-476c-8237-2acd1a839b22\20     (Description not available)         ==&gt; 1
     1e3ee840-bc2b-476c-8237-2acd1a839b22\3      (Description not available)         ==&gt; document
     1e3ee840-bc2b-476c-8237-2acd1a839b22\17     (Description not available)         ==&gt; {1685D4AB-A51B-4AF1-A4E5-CEE87002431D}.Merge Any
     1e3ee840-bc2b-476c-8237-2acd1a839b22\8      (Description not available)         ==&gt; C:\&lt;file path&gt;\password2.txt
     b725f130-47ef-101a-a5f1-02608c9eebac\4      Item Type Text                      ==&gt; Text Document
     b725f130-47ef-101a-a5f1-02608c9eebac\10     Item Name Display                   ==&gt; password2
     b725f130-47ef-101a-a5f1-02608c9eebac\12     Size                                ==&gt; 19
     b725f130-47ef-101a-a5f1-02608c9eebac\14     Date Modified                       ==&gt; 01/11/2010 16:57:11
     006fdbaa-864f-4d1c-a8e8-e62772e454fe\11     (Description not available)         ==&gt; 59
     006fdbaa-864f-4d1c-a8e8-e62772e454fe\13     (Description not available)         ==&gt; 1077936423
     cf5be8c0-236c-4ad3-bace-cd608a2748d7\100    (Description not available)         ==&gt; True
     e3e0584c-b788-4a5a-bb20-7f5a44c9acdd\6      Item Folder Path Display            ==&gt; C:\&lt;file path&gt;

--- End Target ID information ---

--- Extra blocks information ---

&gt;&gt; Property store data block (Format: GUID\ID Description ==&gt; Value)
   (Property store is empty)

&gt;&gt; Tracker database block
   Machine ID: &lt;hostname&gt;
   MAC Address: &lt;mac address&gt;
   MAC Vendor: VMWARE
   Creation: 2019-11-13 04:29:24

   Volume Droid: &lt;volume&gt;
   Volume Droid Birth: &lt;volume&gt;
   File Droid: &lt;file&gt;
   File Droid birth: &lt;file&gt;
```

图9. `LECmd.exe`对`password2.lnk`的分析结果

这里要注意的是，用户搜索LNK文件只与搜索关键字有关，与搜索上下文无关。这意味着再一次搜索同一个关键词时（比如`passw`），用户在搜索结果中打开了文件，但由于处在不同的驱动器及目录中，因此更改了用户搜索LNK文件的修改时间戳及其中包含的搜索上下文。这与LNK快捷方式文件保持一致，这类文件只依赖简单文件名，而非完整文件路径。



## 0x04 时间戳

根据Windows注册表中`WorldWheelQuery`键值的结构以及可用的时间戳信息，之前取证人员只能使用注册表键值的最近修改时间来确定最近搜索关键词的搜索时间。根据我们对用户搜索LNK文件的分析，现在如果用户在搜索关键词后，从结果中打开了某个文件，那么取证人员就可以使用新的时间戳来判断精确的搜索时间。如果更进一步，我们可以将用户搜索LNK文件与`WorldWheelQuery` `MRUlistEx`注册表键值结合起来，推测用户执行的搜索顺序。比如，由于上文案例中用户搜索了`gov`（`WorldWheelQuery`索引值为`4`）、`passw`（索引值`6`）以及`private`（索引值`7`），我们可以推测出用户还搜索过`air`（索引值为`5`），但没有从搜索结果中打开任何文件。



## 0x05 总结

LNK快捷方式文件已经是一种可靠的取证方法，可以用来判断用户对文件及相关文件元数据的访问时间。通过用户搜索LNK文件，现在我们可以进一步丰富资源管理器的搜索历史，当用户执行搜索操作并打开搜索结果文件后，我们就获得更详细的时间戳信息。
