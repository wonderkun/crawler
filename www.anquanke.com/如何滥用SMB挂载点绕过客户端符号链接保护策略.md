> 原文链接: https://www.anquanke.com//post/id/169132 


# 如何滥用SMB挂载点绕过客户端符号链接保护策略


                                阅读量   
                                **186902**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/dm/1024_640_/t016d6dd79f0ac2ae41.jpg)](https://p4.ssl.qhimg.com/dm/1024_640_/t016d6dd79f0ac2ae41.jpg)



## 0x00 概述

本文简要介绍了SMBv2中的一个有趣特性，可能用于横向渗透或者红方行动中。之前我曾专门花时间研究Windows上的符号链接（symbolic link）攻击，当时我仔细研究过SMB服务器。从SMBv2开始，该协议就已支持符号链接（特别是NTFS 重解析点（Reparse Point）格式）。如果SMB服务器在共享目录中遇到NTFS符号链接，则会提取[REPARSE_DATA_BUFFER](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/ntifs/ns-ntifs-_reparse_data_buffer)结构，然后遵循SMBv2[协议](https://msdn.microsoft.com/en-us/library/cc246482.aspx)中相应[规范](https://msdn.microsoft.com/en-us/library/cc246542.aspx)将该信息返回给客户端。

[![](https://p0.ssl.qhimg.com/t01b17ca3ef84f7a9a3.png)](https://p0.ssl.qhimg.com/t01b17ca3ef84f7a9a3.png)

客户端操作系统负责解析`REPARSE_DATA_BUFFER`数据，然后再从本地访问。这意味着符号链接只能引用客户端已经能够访问的文件。实际上，虽然默认情况下Windows没有启用符号链接本地解析功能，我还是找到了绕过客户端策略的一种方法，能够本地解析符号链接。目前微软拒绝修复这个绕过问题，如果大家感兴趣可以访问[此处](https://bugs.chromium.org/p/project-zero/issues/detail?id=138)了解官方回复。



## 0x01 问题描述

我发现有一点非常有趣，虽然`IO_REPARSE_TAG_SYMLINK`会在客户端上处理，但如果服务器遇到`IO_REPARSE_TAG_MOUNT_POINT`重解析点，则会到服务器上去解析。因此，如果我们能在共享目录中设置挂载点（mout point），就可以访问服务器上的任意固定位置（即使该位置没有直接共享出来）。这种场景在横向渗透中非常有用，但问题在于，我们如何在无法本地访问硬盘的情况下添加挂载点？



## 0x02 具体分析

首先我们尝试一下通过UNC路径创建挂载点，可以在CMD中使用`MKLINK`命令，结果如下所示：

[![](https://p0.ssl.qhimg.com/t015481caeff07914f0.png)](https://p0.ssl.qhimg.com/t015481caeff07914f0.png)

输出信息表示系统不支持在远程服务器上设置挂载点。这一点也能够理解，因为在远程驱动器上设置挂载点可能会导致不可预期后果。我们可以猜测一下，要么该协议不支持设置重解析点，要么做了些限制，只允许符号链接。如果想了解协议具体支持的功能，我们可以查看协议规范。设置重解析点需要向某个文件发送[FSCTL_SET_REPARSE_POINT](https://msdn.microsoft.com/en-us/library/windows/desktop/aa364595%28v=vs.85%29.aspx) IO控制代码（control code），因此我们可以参考[SMB2 IOCTL](https://msdn.microsoft.com/en-us/library/cc246545.aspx)命令，查看其中是否存在与控制代码有关的信息。

一番搜索后，我们可以看到协议的确支持`FSCTL_SET_REPARSE_POINT`，并且协议规范中有如下描述（[§3.3.5.15.13](https://msdn.microsoft.com/en-us/library/jj217271.aspx)）：

> 当服务器收到包含包含SMB2头部的请求，并且Command值等于SMB2 IOCTL、`CtlCode`等于`FSCTL_SET_REPARSE_POINT`时，那么消息处理过程如下：
根据[MS-FSCC] section 2.3.65规范，如果`FSCTL_SET_REPARSE_POINT`中的`ReparseTag`字段不等于`IO_REPARSE_TAG_SYMLINK`，那么服务器**应该**验证调用方的确有权限执行这个`FSCTL`。如果调用方不具备所需的权限，那么服务器**必须**拒绝该调用，返回`STATUS_ACCESS_DENIED`错误代码。

根据上述文字，貌似服务器只需要显示检查`IO_REPARSE_TAG_SYMLINK`即可，如果不匹配该标签，则会执行其他检查操作判断请求是否允许，但并没有提到服务器会设置另一个标签来显式禁止请求。也许系统内置的`MKLINK`工具不能处理这种场景，换个工具试试？这里我们可以尝试下`CreateMountPoint`工具（来自于我的[symboliclink-testing-tools](https://github.com/googleprojectzero/symboliclink-testing-tools)项目），看能不能成功。

[![](https://p3.ssl.qhimg.com/t013228befe6d298591.png)](https://p3.ssl.qhimg.com/t013228befe6d298591.png)

`CreateMountPoint`工具并没有显示之前的错误（“只支持本地NTFS卷”），但返回了拒绝访问错误。这与§3.3.5.15.13中的描述相符，如果隐式检查失败，应当返回拒绝访问错误。当然协议规范中并没有表明需要执行哪些检查，我认为这时候应该派上反编译工具，分析一下SMBv2驱动（`srv2.sys`）的具体实现。

我使用IDA来查找`IO_REPARSE_TAG_SYMLINK`对应的立即数（immediate value，这里为`0xA000000C`），根据分析结果，貌似系统在查找其他标志时，会先会查找这个值。在Windows 10 1809系统的驱动中，我只在`Smb2ValidateIoctl`找到一处匹配值，相关代码大致如下：

```
NTSTATUS Smb2ValidateIoctl(SmbIoctlRequest* request) `{`
  // ...
  switch(request-&gt;IoControlCode) `{`
    case FSCTL_SET_REPARSE_POINT:
      REPARSE_DATA_BUFFER* reparse = (REPARSE_DATA_BUFFER*)request-&gt;Buffer;
      // Validate length etc.
      if (reparse-&gt;ReparseTag != IO_REPARSE_TAG_SYMLINK &amp;&amp;
          !request-&gt;SomeOffset-&gt;SomeByteValue) `{`
          return STATUS_ACCESS_DENIED;
      `}`

      // Complete FSCTL_SET_REPARSE_POINT request.
    `}`
`}`
```

上述代码首先从IOCTL请求中提取数据，如果标志不等于`IO_REPARSE_TAG_SYMLINK`并且请求中某些字节值不等于0，那么就会返回`STATUS_ACCESS_DENIED`错误。如果想跟踪这个值的来源，有时候会比较棘手，但其实我只需要在IDA中将变量偏移值作为立即数来搜索，通常就能得出结论。这里对应的立即数为`0x200`，我们可以只搜索`MOV`指令。最终我在`Smb2ExecuteSessionSetupReal`中找到了一条指令：`MOV [RCX+0x200], AL`，这似乎就是我们想要的结果。系统会使用`Smb2IsAdmin`函数的返回值来设置该变量，而该函数只会检查调用方令牌中是否包含`BUILTIN\Administrators`组。因此貌似只要我们是主机上的管理员，就可以在远程共享上设置任意重解析点。我们需要验证这一点：

[![](https://p2.ssl.qhimg.com/t012415f23582ebf25d.png)](https://p2.ssl.qhimg.com/t012415f23582ebf25d.png)

以管理员账户测试时我们能创建挂载点，并且dir UNC路径时，我们也能看到相应的Windows目录。虽然我测试的是本地admin共享，但这适用于其他共享，并且也能访问指向远程服务器的挂载点。



## 0x03 总结

这种技巧是否有用武之地？这种方法需要管理员访问权限，因此这并不是一种权限提升技术。此外，如果我们具备远程管理员访问权限，那么我们肯定会利用该权限执行其他操作。然而，如果目标主机禁用了admin共享，或者目标环境中有些监控机制，可以监控`ADMIN$`或者`C$`，但我们具备有些共享的写入权限，那么横向渗透中我们就可以使用这种方法完全控制其他驱动器。

我发现之前没有人分析过这一点，或者也有看可能是我搜索不够全面，毕竟在网上搜索SMB以及挂载点时，得到的结果大多与SAMBA配置有关。有时候系统出于安全考虑，不会公开某些处理逻辑，我们可以大胆假设小心求证，这个例子就是非常典型的一次实验。虽然`MKLINK`之类的工具提示我们无法设置远程挂载点，但进一步分析、查看代码后，我们自己可以找到更为有趣的一些细节。
