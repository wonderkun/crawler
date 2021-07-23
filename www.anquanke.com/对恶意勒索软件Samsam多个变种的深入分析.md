> 原文链接: https://www.anquanke.com//post/id/145920 


# 对恶意勒索软件Samsam多个变种的深入分析


                                阅读量   
                                **178410**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：www.crowdstrike.com
                                <br>原文地址：[https://www.crowdstrike.com/blog/an-in-depth-analysis-of-samsam-ransomware-and-boss-spider/](https://www.crowdstrike.com/blog/an-in-depth-analysis-of-samsam-ransomware-and-boss-spider/)

译文仅供参考，具体内容表达以及含义原文为准

## [![](https://p4.ssl.qhimg.com/t011886b0b2310e1216.png)](https://p4.ssl.qhimg.com/t011886b0b2310e1216.png)

## 一、概述

本文主要对恶意软件Samsam进行深入分析，该恶意软件是由BOSS SPIDER开发和运营，这一组织的活动被CrowdStrike® Falcon Intelligence™持续追踪。该恶意软件不同变种的感染链和执行流都不尽相同，我们会在本文中进行详细分析。该恶意软件使用外部工具（例如批处理脚本、Mimikatz和包括PsExec、Sdelete在内的系统内部实用程序）来实现勒索软件的传播和清除工作。在某些情况下，勒索软件会将加密方式与运行程序文件一同投递，其中的运行程序文件用于加载和执行内存中的恶意软件。此外，该恶意软件还具有反取证功能，分析人员如果想要从被感染的系统中恢复勒索软件Payload是有一定难度的。尽管恶意软件采取了一些措施来逃避检测，但使用Falcon Prevent可以在该恶意软件家族对系统中文件进行加密之前及时地检测到这一行为并进行阻止。



## 二、感染过程

这种勒索软件家族的投递方法发生过多次变化。早期的勒索软件变种会使用凭据自动收集程序（例如Mimikatz）从活动目录（Active Directory）中收集凭据，为列表中的每个用户生成RSA公钥，并将Payload与以下文件一起部署：<br>
1、PSExec：系统内部实用工具中的一个合法工具，用于在远程系统上执行应用程序；<br>
2、备份删除帮助程序：该文件负责遍历所有连接到被感染主机的驱动器，在这里（[https://docs.google.com/document/d/1FzJkhSsKV6vTLNewaduhwkum1WDfGjXg0zu4sU78O6M/edit#heading=h.gw8tkwt73pza](https://docs.google.com/document/d/1FzJkhSsKV6vTLNewaduhwkum1WDfGjXg0zu4sU78O6M/edit#heading=h.gw8tkwt73pza) 对其进行了详细分析；<br>
3、暴露的账户列表；<br>
4、包含每个账户的唯一RSA公钥的文件夹；<br>
5、四个批处理脚本，负责将文件复制到每台被感染主机，并加载Payload：<br>
(1) 第一个文件：将Samsam的Payload和相应的公钥复制到%WINDIR%system32中，并执行命令“vssadmin delete shadows /all /quiet”；<br>
(2) 第二个文件：将备份删除帮助程序复制到C:Windows目录下；<br>
(3) 第三个文件：利用psexec远程执行删除帮助程序；<br>
(4) 第四个文件：利用psexec远程执行Payload，提供相应的公钥作为Payload的参数。<br>
如上所述，公钥和备份删除命令都没有保存在Payload之中。在Samsam恶意软件的其他变种中，密钥和备份删除命令都嵌入在Payload之中。后者的投递机制与前者有很大不同。后者的变种并没有使用大量文件来部署Payload，而是使用了运行程序和批处理脚本来进行相应的加密和部署，具体如下：<br>
1、运行程序：负责解密和加载Payload，在这里（ [https://docs.google.com/document/d/1FzJkhSsKV6vTLNewaduhwkum1WDfGjXg0zu4sU78O6M/edit#heading=h.nb6vvs2dujx9](https://docs.google.com/document/d/1FzJkhSsKV6vTLNewaduhwkum1WDfGjXg0zu4sU78O6M/edit#heading=h.nb6vvs2dujx9) ）对其进行了详细分析；<br>
2、批处理脚本：加载运行程序文件，并向其提供以下参数：<br>
(1) &lt;password&gt;：用于解密和加密Payload；<br>
(2) &lt;path&gt;：被解密的Payload用于投放附加文件；<br>
(3) &lt;totalprice&gt;：被解密的Payload使用，动态生成启动画面；<br>
(4) &lt;priceperhost&gt;：被解密的Payload使用，动态生成启动画面。<br>
在一些Samsam变种中，也有独立的Payload，不需要任何参数或帮助程序。<br>
如前所述，Payload可以通过多种方式传递并加载到系统中。我们后面将更加详细地对Payload和一些帮助程序文件展开分析。



## 三、技术分析

### <a class="reference-link" name="3.1%20%E5%A4%87%E4%BB%BD%E5%88%A0%E9%99%A4%E5%B8%AE%E5%8A%A9%E7%A8%8B%E5%BA%8F"></a>备份删除帮助程序

该文件负责对被感染计算机上的文件系统进行遍历，并将其目标放在与数据备份相关扩展名的文件上（详见附录A）。该程序的目的是确保系统上的文件被加密后，无法使用备份来恢复文件。在这里需要注意，如果计算机连接了任何共享驱动器，该程序也将删除这些文件夹中的相应程序。<br>
在被批处理脚本加载之后，该文件将递归遍历全部驱动器中的每个目录。如果目录名称包含字符串“backup”，程序就将会进一步遍历该目录中的所有文件，并执行以下操作：<br>
1、将文件属性设置为FILE_ATTRIBUTE_NORMAL，这样就能确保文件可以被删除，而不会引发异常；<br>
2、在设置文件属性后，逐一删除文件；<br>
3、在所有文件都被删除后，删除目录本身。<br>
对于所有其他目录，一旦找到目标文件，程序就会通过执行以下操作，来确保它可以删除该文件：<br>
1、检查文件是否被锁定，确保没有句柄到进程访问的文件，这样文件可以在READ模式下打开。如果检查通过，就将该文件删除。<br>
2、如果上述检查失败，程序将结束与该文件关联的进程。<br>
(1) 通过以下命令，调用tasklist.exe，在系统上生成正在运行进程的列表：tasklist /v /fo csv<br>
(2) 查找列表，寻找与该文件名相同的进程。如果找到，将使用以下命令调用taskkill.exe来终止进程：taskkill /f /pid &lt;目标进程的进程ID &gt;<br>
一旦该进程被终止，相应的文件就会被删除。<br>
以下是tasklist命令输出的部分结果：<br>[![](https://www.crowdstrike.com/blog/wp-content/uploads/2018/05/figure1.png)](https://www.crowdstrike.com/blog/wp-content/uploads/2018/05/figure1.png)

### 运行程序

运行程序负责解密并加载内存中的Payload。该文件需要密码作为参数，用于解密过程。一旦由批处理脚本加载后，运行程序将在当前工作目录内查找扩展名为“.stubbin”的文件。该文件是实际加密后的Payload，一旦找到后，运行程序将读取内存中的内容，并立即从磁盘上删除加密的.stubbin文件。事实上，Payload会被解密，并完全加载到内存中，这样就导致难以恢复解密的勒索软件Payload。<br>
一旦内容被读取，运行程序会使用Rijndael算法对其进行解密。该算法需要首先输入密码和盐（Salt），从而生成解密密钥和初始化向量（IV）。其中，盐的值为“Ivan Medvedev”，该值在使用此算法的多个二进制文件（包括合法文件和恶意文件）中都有出现过。有了这两个输入，运行程序会生成一个32字节的密钥和16字节的初始化向量（IV），然后使用它来对Payload进行解密。需要注意的是，从批处理文件传递的任何附加参数都将传递给解密的Payload。运行程序随后负责调用Payload的入口点，从而在内存中执行。

我们分析了多个变种中的Payload，其中的一个主要区别是RSA公钥是否嵌入在Payload之中。如前所述，负责加载Payload的批处理脚本会将公钥以参数的方式传递给它，然后将其读取到变量之中，以备后续在执行过程中使用。本节将详细解释勒索软件是如何加密被感染主机上的文件的。

### 提取资源

在加载后，Samsam首先解析其自身的资源部分，并提取资源名称。针对每个名称，它会确保扩展名为“.exe”，并检查当前目录中是否有与资源名称相同的文件。如果存在，它将从磁盘中删除该文件，并以4096字节的块为单位，读取资源部分的内容并将其写入到当前目录之中。截至目前，在完成提取过程后，我们最多可以看到两个不同的文件：selfdel.exe和del.exe。在这里需要注意，在击杀链的早期阶段，我们可以将当前目录下具有静态名称的这两个文件作为检测目标，检测其投放的特定活动。<br>
在文件被写入磁盘后，Payload会启动一个新的线程来执行selfdel.exe，我们稍后在“自我删除”这一节中会进行更详细地分析。接下来，Payload将递归遍历所有连接到被感染主机的驱动器中的所有目录。

### 文件系统遍历

Payload在进行遍历搜索文件时，会跳过如下目录：

```
C:Windows
Reference AssembliesMicrosoft
Recycle.bin
```

其原因是为了确保执行流的顺畅。由于C:Windows目录下都是系统文件，.NET框架所需的文件都在Reference AssembliesMicrosoft目录下，因此就无需再对这些文件夹进行搜索。而至于回收站Recycle.bin，我们推测可能是因为绝大多数勒索软件首先都会对该目录进行遍历搜索，因此一些安全防护产品会通过检测对该目录的遍历来发现恶意软件行为，所以在该恶意软件中就跳过了这一目录。通过跳过Recycle.bin，Samsam可以避开这种检测方法，并继续对文件进行加密。<br>
附录A中列出了Samsam的目标文件扩展名列表。当恶意软件找到列表中扩展名的文件时，会判断文件大小。如果文件不大于100MB（104857600字节），那么Payload会立即调用加密子例程。如果文件大于100MB，会进行如下判断和操作：<br>
1、如果文件&gt;100MB且&lt;=250MB，它会将文件的完整路径附加到列表mylist250中；<br>
2、如果文件&gt;250MB且&lt;=500MB，它会将文件的完整路径附加到列表mylist500中；<br>
3、如果文件&gt;500MB且&lt;=1GB，它会将文件的完整路径附加到列表mylist1000中；<br>
4、如果文件&gt;1GB，它会将文件的完整路径附加到列表mylistbig中。<br>
所有不大于100MB的目标文件会首先被加密，随后Payload再对这些列表中的文件进行加密。这一设计可能是为了防止勒索软件进程被提早终止，希望能够尽可能多地加密文件。在加密完所有不大于100MB的文件后，恶意软件也会按照列表的先后顺序，先加密mylist250中的文件，然后是mylist500，之后是mylist1000，最后是mylistbig。一旦上述所有文件都成功被加密，Payload将会清除内存中的这些列表。<br>
在Samsam的其他一些变种中，不存在这种按照文件大小分批加密的行为。这些变种只使用一个列表，来记录连接到被感染主机的所有驱动器中的所有目标文件。随后，会调用文件加密子例程，对其进行加密。

### 文件加密过程

对于每个文件，Payload会执行以下检查：<br>
1、当前文件的大小是否小于驱动器的可用空间，如果小于，Payload将会跳过此文件，开始处理下一个文件；<br>
2、当前文件的大小是否大于0；<br>
3、公钥变量是否为空，如果没有公钥，那么就无法进行加密。<br>
如果上述的任何一个检查不符合条件，Payload都会跳到处理下一个文件。<br>
接下来，我们发现有两类不同的变种，它们的加密方式也有所不同。

### 变种A

对于每个文件，子例程首先检查当前目录中是否存在名为&lt;目标文件名&gt;.&lt;加密后扩展名&gt;的文件，加密后文件的扩展名始终是“.encryptedRSA”。如果存在，则执行以下步骤：<br>
(1) 检查.encryptedRSA文件的大小。如果该文件大小大于目标文件，则子例程将会删除目标文件，并开始处理下一个文件。在这里，如果满足条件，就假设该文件已经被Samsam加密，因此就删除了原始目标文件。<br>
(2) 如果.encryptedRSA文件大小小于或等于目标文件，子例程将删除.encryptedRSA文件。由于实际加密会导致生成的文件大小大于原始文件，因此.encryptedRSA文件大小必然会大于目标文件。在这里，如果满足条件，就假设该.encryptedRSA文件不是实际加密的文件，并对其进行删除。在删除之后，目标文件会立即被加密。

### 变种B

如果子例程找到名为&lt;目标文件名&gt;.encryptedRSA的文件，则立即跳过该目标文件。它不会对加密后文件的大小进行检查，也没有尝试删除任何目标文件。请注意，子例程会跳到下一个文件，从而让当前文件保持不变，这一点非常重要。也就意味着，如果系统中每个文件，都相应创建了扩展名为“.encryptedRSA”的任意大小文件，那么恶意软件就不会对其进行加密，而是直接跳过。我们在分析过程中进行了实际测试，并确认了这一结论的正确性。

### 文件加密方式

恶意软件Samsam使用AES标准来加密文件。针对每个文件，它会生成一个随机的64字节签名秘钥（Signaturekey）、一个16字节秘钥和一个16字节初始化向量（IV）。恶意软件还会创建一个以“&lt;target filename&gt;.encryptedRSA”为名称的空文件，并向其中写入3072个NULL字节。在稍后的执行流程中，该文件将作为生成的加密文件中头部占位符。然后，Payload通过使用重启管理器API（Restart Manager API）以确定当前运行的进程或服务是否对目标文件存在打开的句柄。详细步骤如下：<br>
1、调用RmStartSession，启动一个新的会话管理器，从而为新会话提供了会话句柄；<br>
2、RmRegisterResources使用该句柄，将目标文件注册为新会话的资源；<br>
3、RmGetList使用该句柄来获取当前正在使用的资源（目标文件）的进程列表；<br>
4、会话管理器以RmEndSession结束；<br>
5、针对所有锁定目标文件的进程，将其进程ID附加到一个文件中，然后将文件传递给一个负责终止这些进程的子例程。<br>
一旦目标文件句柄从其他进程中释放，加密子例程就会以每次读取10KB（10240字节）的块的方式，读取其在内存缓冲区中的内容。接下来，子例程使用AES（CBC模式）加密缓冲区中的内容，并将其写入到.encryptedRSA文件中第3073字节之后（头部占位符之后）的位置。在当前文件加密完成后，就会生成新的文件头。

### 文件头

恶意软件使用一个随机生成的签名秘钥，针对加密内容，生成其基于哈希的消息认证码（HMAC）散列。并将该值与inArray一起以Base64编码，写入到文件头之中。以下是文件头的具体结构：

```
&lt;MtAeSKeYForFile&gt;
&lt;Key&gt;：包含随机生成的以RSA公钥加密的16字节秘钥，并使用Base64编码&lt;/Key&gt;
&lt;IV&gt;：包含随机生成的16字节初始化向量，以相同的方式加密和编码&lt;/IV&gt;
&lt;Value&gt;：包含前面提到过的inArray &lt;/Value&gt;
&lt;EncryptedKey&gt;：包含64字节签名秘钥，该签名秘钥是随机生成的，以相同方式加密和编码&lt;/Encrypted&gt;
&lt;OriginalFileLength&gt;：包含原始目标文件的文件大小&lt;/OriginalFileLength&gt;
&lt;/MtAeSKeYForFile&gt;
```

相应的RSA私钥将负责解密文件头中的每个值，并解密文件内容。以下是一个被Samsam恶意软件加密的文件中的文件头：<br>[![](https://www.crowdstrike.com/blog/wp-content/uploads/2018/05/Figure2-1024x694.png)](https://www.crowdstrike.com/blog/wp-content/uploads/2018/05/Figure2-1024x694.png)<br>
当文件加密后，原始文件将被从磁盘中删除。

### 投放赎金通知

在每个文件被加密后，Payload将在当前目录中投放一个名为“HELP_DECRYPT_YOUR_FILES”的文本文件，下图为该文本文件的内容：<br>[![](https://www.crowdstrike.com/blog/wp-content/uploads/2018/05/Figure3-1024x832.png)](https://www.crowdstrike.com/blog/wp-content/uploads/2018/05/Figure3-1024x832.png)<br>
在某些情况下，具有相同内容的HELP_DECRYPT_YOUR_FILES.html也会被投放在当前目录中。Samsam恶意软件的所有变种都有一个奇怪的行为，针对每个被加密的文件都会投放一次赎金通知。因此，在多个文件被加密的目录中，会出现多个该文本文件或HTML文件。

### 自我删除

如前文所说，Payload会解析其资源部分，提取两个可执行文件，并将其写入到当前目录。这两个可执行文件的详情如下：<br>
文件名：selfdel.exe<br>
大小：5632<br>
MD5：710A45E007502B8F42A27EE05DCD2FBA<br>
SHA256： 32445C921079AA3E26A376D70EF6550BAFEB1F6B0B7037EF152553BB5DAD116F<br>
编译：Wed, Dec 2 2015, 22:24:42 – 32 Bit .NET AnyCPU EXE<br>
版本：1.0.0.0

文件名：del.exe<br>
大小：155736<br>
MD5：E189B5CE11618BB7880E9B09D53A588F<br>
SHA256： 97D27E1225B472A63C88AC9CFB813019B72598B9DD2D70FE93F324F7D034FB95<br>
编译：Sat, Jan 14 2012, 23:06:53 – 32 Bit EXE<br>
版本：1.61<br>
签名：有效<br>
主体：Microsoft Corporation<br>
发布者：Microsoft Code Signing PCA<br>
内部名称：sdelete<br>
产品名称：Sysinternal Sdelete

可执行文件del.exe是一个合法的系统内部程序，用于从磁盘中删除文件。可执行文件selfdel.exe则是由Payload在新线程中调用。它首先会检查名为samsa.exe的进程是否正在执行，如果不是，则会立即退出。接下来，等待3秒钟，然后执行以下命令：del.exe -p 16 samsam.exe。该命令会调用合法的实用程序del.exe，从而从磁盘中删除samsam.exe。然而，删除文件的操作只会标记相应的MFT表，实际的文件内容仍然保留。为了解决这一问题，实用工具会对硬盘上的相应位置进行覆盖，“-p 16”参数表示覆盖16次，这样就确保没有任何途径能对已经删除的samsam.exe进行恢复。这一技术只适用于独立Payload的变种，不适用于使用运行程序解密并执行内存中Payload的变种。<br>
一旦Payload被删除，selfdel.exe会休眠30秒，然后从磁盘中删除del.exe。该可执行文件不会删除其自身。



## 四、总结

Samsam恶意软件会收集用户凭据，生成唯一的RSA公钥，以确保每个受感染用户能够通过付费来解密文件。此外，该恶意软件的一些变种会对可执行文件进行清除，另一些变种完全在内存中运行，因此分析人员难以从磁盘上或内存中收集到其Payload。因此，这是一个非常有分析价值的恶意软件。



## 五、附录A

### 

### 目标备份文件扩展名列表

.abk, .ac, .back, .backup, .backupdb, .bak, .bb, .bk, .bkc, .bke, .bkf, .bkn, .bkp, .bpp, .bup, .cvt, .dbk, .dtb, .fb, .fbw, .fkc, .jou, .mbk, .old, .rpb, .sav, .sbk, .sik, .spf, .spi, .swp, .tbk, .tib, .tjl, .umb, .vbk, .vib, .vmdk, .vrb, .wbk

### 

### 目标扩展名

.jin, .xls, .xlsx, .pdf, .doc, .docx, .ppt, .pptx, .log, .txt, .gif, .png, .conf, .data, .dat, .dwg, .asp, .aspx, .html, .tif, .htm, .php, .jpg, .jsp, .js, .cnf, .cs, .vb, .vbs, .mdb, .mdf, .bak, .bkf, .java, .jar, .war, .pem, .pfx, .rtf, .pst, .dbx, .mp3, .mp4, .mpg, .bin, .nvram, .vmdk, .vmsd, .vmx, .vmxf, .vmsn, .vmem, .gz, .3dm, .3ds, .zip, .rar, .3fr, .3g2, .3gp, .3pr, .7z, .ab4, .accdb, .accde, .accdr, .accdt, .ach, .acr, .act, .adb, .ads, .agdl, .ai, .ait, .al, .apj, .arw, .asf, .asm, .asx, .avi, .awg, .back, .backup, .backupdb, .pbl, .bank, .bay, .bdb, .bgt, .bik, .bkp, .blend, .bpw, .c, .cdf, .cab, .chm, .cdr, .cdr3, .cdr4, .cdr5, .cdr6, .cdrw, .cdx, .ce1, .ce2, .cer, .cfp, .cgm, .cib, .class, .cls, .cmt, .cpi, .cpp, .cr2, .craw, .crt, .crw, .csh, .csl, .csv, .dac, .db, .db3, .dbf, .db-journal, .dc2, .dcr, .dcs, .ddd, .ddoc, .ddrw, .dds, .der, .des, .design, .dgc, .djvu, .dng, .dot, .docm, .dotm, .dotx, .drf, .drw, .dtd, .dxb, .dxf, .jse, .dxg, .eml, .eps, .erbsql, .erf, .exf, .fdb, .ffd, .fff, .fh, .fmb, .fhd, .fla, .flac, .flv, .fpx, .fxg, .gray, .grey, .gry, .h, .hbk, .hpp, .ibank, .ibd, .ibz, .idx, .iif, .iiq, .incpas, .indd, .jpe, .jpeg, .kc2, .kdbx, .kdc, .key, .kpdx, .lua, .m, .m4v, .max, .mdc, .mef, .mfw, .mmw, .moneywell, .mos, .mov, .mrw, .msg, .myd, .nd, .ndd, .nef, .nk2, .nop, .nrw, .ns2, .ns3, .ns4, .nsd, .nsf, .nsg, .nsh, .nwb, .nx2, .nxl, .nyf, .oab, .obj, .odb, .odc, .odf, .odg, .odm, .odp, .ods, .odt, .oil, .orf, .ost, .otg, .oth, .otp, .ots, .ott, .p12, .p7b, .p7c, .pab, .pages, .pas, .pat, .pcd, .pct, .pdb, .pdd, .pef, .pl, .plc, .pot, .potm, .potx, .ppam, .pps, .ppsm, .ppsx, .pptm, .prf, .ps, .psafe3, .psd, .pspimage, .ptx, .py, .qba, .qbb, .qbm, .qbr, .qbw, .qbx, .qby, .r3d, .raf, .rat, .raw, .rdb, .rm, .rw2, .rwl, .rwz, .s3db, .sas7bdat, .say, .sd0, .sda, .sdf, .sldm, .sldx, .sql, .sqlite, .sqlite3, .sqlitedb, .sr2, .srf, .srt, .srw, .st4, .st5, .st6, .st7, .st8, .std, .sti, .stw, .stx, .svg, .swf, .sxc, .sxd, .sxg, .sxi, .sxi, .sxm, .sxw, .tex, .tga, .thm, .tlg, .vob, .wallet, .wav, .wb2, .wmv, .wpd, .wps, .x11, .x3f, .xis, .xla, .xlam, .xlk, .xlm, .xlr, .xlsb, .xlsm, .xlt, .xltm, .xltx, .xlw, .ycbcra, .yuv

原文链接：[https://www.crowdstrike.com/blog/an-in-depth-analysis-of-samsam-ransomware-and-boss-spider/](https://www.crowdstrike.com/blog/an-in-depth-analysis-of-samsam-ransomware-and-boss-spider/)
