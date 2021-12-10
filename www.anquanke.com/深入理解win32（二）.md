> 原文链接: https://www.anquanke.com//post/id/260799 


# 深入理解win32（二）


                                阅读量   
                                **50623**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01e94717568627114f.jpg)](https://p3.ssl.qhimg.com/t01e94717568627114f.jpg)



## 前言

上一节中我们初始了win32中的事件、消息以及消息处理函数，这节我们来探究一下win32的入口函数、ESP以及回调函数以及如何在od里面找到这几个结构。



## 关于入口函数

### <a class="reference-link" name="WinMain%E7%BB%93%E6%9E%84"></a>WinMain结构

WinMain函数主要包含了以下几个成员

```
int WINAPI WinMain(
  HINSTANCE hInstance,      // handle to current instance
  HINSTANCE hPrevInstance,  // handle to previous instance
  LPSTR lpCmdLine,          // command line
  int nCmdShow              // show state
);
```

> <ul>
<li>
**hInstance**[in] Handle to the current instance of the application.</li>
<li>
**hPrevInstance**[in] Handle to the previous instance of the application. This parameter is always NULL.</li>
<li>
**lpCmdLine**[in] Pointer to a null-terminated string specifying the command line for the application, excluding the program name. To retrieve the entire command line, use the ) function.</li>
<li>
**nCmdShow**is a flag that says whether the main application window will be minimized, maximized, or shown normally.</li>
</ul>

`hInstance`被称为实例句柄，当它被加载到内存时，操作系统会根据这个值来识别可执行文件。`hPrevInstance`本来在16位windows中使用，现在已经废弃，一直为空。`IpCmdLine`包含作为`Unicode`字符串的命令行参数。`nCmdShow`表示主应用程序窗口是最大化、最小化还是正常显示。

这里说下`IpCmdLine`的具体作用，当我们打开cmd使用程序执行命令的时候在后面执行的命令就是通过这个`IpCmdLine`传入

在上一节中我们已经编写程序进行了事件与消息的实现，那么这里我们直接编译生成exe拿到win10中用`DebugView`进行运行查看

```
int APIENTRY WinMain(HINSTANCE hInstance,
                     HINSTANCE hPrevInstance,
                     LPSTR     lpCmdLine,
                     int       nCmdShow)
`{`
    hAppInstance = hInstance;

    //窗口的类名                

    TCHAR className[] = "My First Window";                 

     //创建一个自己的窗口

    WNDCLASS wndclass = `{`0`}`;        
    wndclass.hbrBackground = (HBRUSH)COLOR_MENU;                        //窗口的背景色            
    wndclass.lpfnWndProc = WindowProc;                        //窗口过程函数            
    wndclass.lpszClassName = className;                        //窗口类的名字            
    wndclass.hInstance = hInstance;                        //定义窗口类的应用程序的实例句柄            


    //注册
    RegisterClass(&amp;wndclass);

    // 创建窗口                              
    HWND hwnd = CreateWindow(                              
    className,                            //类名        
    TEXT("我的第一个窗口"),                //窗口标题        
    WS_OVERLAPPEDWINDOW,                //窗口外观样式         
    10,                                    //相对于父窗口的X坐标        
    10,                                    //相对于父窗口的Y坐标        
    600,                                //窗口的宽度          
    300,                                //窗口的高度          
    NULL,                                //父窗口句柄，为NULL          
    NULL,                                //菜单句柄，为NULL          
    hInstance,                            //当前应用程序的句柄          
    NULL);                                //附加数据一般为NULL        

    if(hwnd == NULL)                    //是否创建成功          
        return 0;      

    CreateButton(hwnd);

    // 显示窗口              
    ShowWindow(hwnd, SW_SHOW);              

    //消息循环
    MSG msg;              
    while(GetMessage(&amp;msg, NULL, 0, 0))              
    `{`              
        TranslateMessage(&amp;msg);          
        DispatchMessage(&amp;msg);          
    `}`              



    return 0;
`}`
```

[![](https://p2.ssl.qhimg.com/t01fadb78786ed9fe6a.png)](https://p2.ssl.qhimg.com/t01fadb78786ed9fe6a.png)

[![](https://p5.ssl.qhimg.com/t0168543ba3f2e40a6d.png)](https://p5.ssl.qhimg.com/t0168543ba3f2e40a6d.png)

### <a class="reference-link" name="win32%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E5%85%A5%E5%8F%A3%E8%AF%86%E5%88%AB"></a>win32应用程序入口识别

这里首先改成release版本编译

[![](https://p0.ssl.qhimg.com/t01e61f6065fff5f5f3.png)](https://p0.ssl.qhimg.com/t01e61f6065fff5f5f3.png)

拖入od，这里并不是我们写的入口程序的地址

[![](https://p1.ssl.qhimg.com/t019ade72c74d572df1.png)](https://p1.ssl.qhimg.com/t019ade72c74d572df1.png)

在`WinMain`执行之前下断点查看堆栈，发现调用`WinMain()`的是`WinMainCRTStartup()`这个函数

[![](https://p3.ssl.qhimg.com/t014ec540e6a7397df3.png)](https://p3.ssl.qhimg.com/t014ec540e6a7397df3.png)

od往下跟，找到`GetModuleHandleA`这个函数

[![](https://p1.ssl.qhimg.com/t01884f3ca9e1730002.png)](https://p1.ssl.qhimg.com/t01884f3ca9e1730002.png)

**<a class="reference-link" name="GetModuleHandleA"></a>GetModuleHandleA**

看一下MSDN里对`GetModuleHandleA`的描述

```
HMODULE GetModuleHandleA(
  LPCSTR lpModuleName
);
```

> The name of the loaded module (either a .dll or .exe file). If the file name extension is omitted, the default library extension .dll is appended. The file name string can include a trailing point character (.) to indicate that the module name has no extension. The string does not have to specify a path. When specifying a path, be sure to use backslashes (), not forward slashes (/). The name is compared (case independently) to the names of modules currently mapped into the address space of the calling process.
If this parameter is NULL, **GetModuleHandle** returns a handle to the file used to create the calling process (.exe file).
The **GetModuleHandle** function does not retrieve handles for modules that were loaded using the **LOAD_LIBRARY_AS_DATAFILE** flag. For more information, see [LoadLibraryEx](https://docs.microsoft.com/en-us/windows/desktop/api/libloaderapi/nf-libloaderapi-loadlibraryexa).

此函数用来加载模块的名称，如果参数为NULL，则返回exe的句柄

继续跟这个函数，这里的`GetModuleHandleA`用的是间接call，指向一个地址

[![](https://p1.ssl.qhimg.com/t01a3d2d5a5a6059c54.png)](https://p1.ssl.qhimg.com/t01a3d2d5a5a6059c54.png)

[![](https://p2.ssl.qhimg.com/t01b1bf0c6153f99f31.png)](https://p2.ssl.qhimg.com/t01b1bf0c6153f99f31.png)

这里跟到这个地址，发现这里又指向一个地址，地址里面存储的是`KERNEL32`这个dll的`GetModuleHandleA`这个函数

[![](https://p2.ssl.qhimg.com/t01ca62527f4cd74c1d.png)](https://p2.ssl.qhimg.com/t01ca62527f4cd74c1d.png)

这里点击回车跟进这个函数查看

[![](https://p2.ssl.qhimg.com/t01a291dc9872d93e6c.png)](https://p2.ssl.qhimg.com/t01a291dc9872d93e6c.png)

这里发现`retn 10`，也就是4个参数，那么几乎可以确定这个函数就是我们要找的入口函数

[![](https://p5.ssl.qhimg.com/t01a1cae4d17dc25b62.png)](https://p5.ssl.qhimg.com/t01a1cae4d17dc25b62.png)

这里往上看一个细节，这里首先把内存的值传给了ecx，再把ecx的值压入堆栈，那么这里肯定就不是寄存器传参。一般使用寄存器传参的不会有从内存赋值给ecx的操作

[![](https://p4.ssl.qhimg.com/t0114491d833293b265.png)](https://p4.ssl.qhimg.com/t0114491d833293b265.png)



## ESP寻址

这里首先说一下ESP的概念，我们知道在汇编层面中有许多个标志寄存器，在这些标志寄存器里面ESP和EBP可以说是成对存在的

ESP：栈指针寄存器 (extended stack pointer) ，永远指向系统栈最上面一个栈帧的栈顶。<br>
EBP：基址指针寄存器(extended base pointer), 永远指向系统栈最上面一个栈帧的栈底。

我们如果要往一个栈里面存放数据，首先需要在栈里面申请空间，然后调整esp和ebp

例如在这个地方我根据汇编语句画出堆栈图，在执行push 0x5，push 0xc和push0x9的操作的时候，esp就会相应的减少12，对应的十六进制就是10，所以ESP就从0019FEE4 – 10 = 0019FED8，也就是说如果要往栈里面存入数据，esp的值就是栈顶的地址值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b84262f82f0bdddf.jpg)

F2断点到函数位置

[![](https://p3.ssl.qhimg.com/t01115d28d6b00c4ee1.png)](https://p3.ssl.qhimg.com/t01115d28d6b00c4ee1.png)

查看堆栈里面的值，发现有四个参数，因为压栈顺序为`_stdcall`内平栈，从右往左入栈，那么第一个参数就是`hInstance`即`ImageBase`，第二个参数为`hPrevInstance`永远为NULL，第三个参数为`IpCmdLine`为命令行参数，第四个参数为`nCmdShow`为最大最小化还是正常显示

这里的`0019FEE4`里面存的就是函数调用完成后返回的地址，即`00401783`

[![](https://p3.ssl.qhimg.com/t01b9520a0383cbd949.png)](https://p3.ssl.qhimg.com/t01b9520a0383cbd949.png)

这里注意一下，之前提升堆栈都是通过`push ebp`，`mov ebp,esp`提升堆栈，但是在`release`版本中可能使用的是esp寻址，直接使用`sub esp,0x98`提升堆栈而`ebp`不变

这里提升堆栈过后，`esp+0x98`的地址存的就是函数的返回地址，如果要找第一个参数就是`esp+0x9C`

[![](https://p5.ssl.qhimg.com/t015f0eaebf528d08c7.png)](https://p5.ssl.qhimg.com/t015f0eaebf528d08c7.png)

所以如果使用esp寻址的话，esp的值是随时要变化的，所以在堆栈寻址的时候要时刻注意esp的变化



## 窗口回调函数

DllMain只是在Windows系统里注册的一个回调函数（call back）

早期的SDK版本中，DllMain是叫做DllEntryPoint

DllMain 是Dll 的缺省入口函数，DLLMain 负责Dll装载时的初始化及卸载的收尾工作，每当一个新的进程或者该进程的新的线程访问 DLL 或访问DLL 的每一个进程或线程不再使用DLL时，都会调用 DLLMain。

使用 TerminateProcess 或 TerminateThread 结束进程或者线程，不会调用DLLMain。

有些DLL并没有提供DllMain函数，也能成功引用DLL，这是因为Windows在找不到DllMain的时候，系统会引入一个缺省DllMain函数版本。

缺省的DllMain函数在 HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs 键值中。

DllMain函数的原型

```
BOOL  WINAPI  DllMain( HINSTANCE  hinstDLL,  DWORD  fdwReason,  LPVOID  lpvReserved );

BOOL  APIENTRY  DLLMain(HANDLE hModule,DWORD ul_reason_for_call,LPVOID  lpReserved)

`{`

switch(ul_reason_for_call)

`{`
case DLL_PROCESS_ATTACH:
case DLL_THREAD_ATTACH:
case DLL_THREAD_DETACH:
case DLL_PROCESS_DETACH:
`}`

return TRUE;

`}`
```

参数：

hModule：

是动态库被调用时所传递来的一个指向自己的句柄(实际上，它是指向_DGROUP段的一个选择符)；

ul_reason_for_call：

是一个说明动态库被调原因的标志。当进程或线程装入或卸载动态连接库的时候，操作系统调用入口函数，并说明动态连接

> <p>DLL_PROCESS_ATTACH<br>
进程被调用<br>
DLL_THREAD_ATTACH<br>
线程被调用<br>
DLL_PROCESS_DETACH<br>
进程被停止<br>
DLL_THREAD_DETACH<br>
线程被停止</p>

lpReserved：是一个被系统所保留的参数；

> <p>DLL_PROCESS_ATTACH<br>
每个进程第一次调用DLL文件被映射到进程的地址空间时，传递的fdwReason参数为DLL_PROCESS_ATTACH。<br>
这进程再次调用操作系统只会增加DLL的使用次数。<br>
DLL_THREAD_ATTACH<br>
进程中的每次建立线程，都会用值DLL_THREAD_ATTACH调用DllMain函数，哪怕是线程中建立线程也一样。<br>
DLL_PROCESS_DETACH<br>
当DLL被从进程的地址空间解除映射时，系统调用了它的DllMain，传递的fdwReason值是DLL_PROCESS_DETACH。</p>

◆FreeLibrary解除DLL映射（有几个LoadLibrary，就要有几个FreeLibrary）<br>
◆进程结束而解除DLL映射，在进程结束前还没有解除DLL的映射，进程结束后会解除DLL映射。

用TerminateProcess终结进程，系统就不会用DLL_PROCESS_DETACH来调用DLL的DllMain函数。

注意：当用DLL_PROCESS_ATTACH调用DLL的DllMain函数时，如果返回FALSE，说明没有初始化成功，系统仍会用DLL_PROCESS_DETACH调用DLL的DllMain函数。

DLL_THREAD_DETACH

线程调用ExitThread来结束线程（线程函数返回时，系统也会自动调用ExitThread），用DLL_THREAD_DETACH来调用DllMain函数。

注意：用TerminateThread来结束线程，系统就不会用值DLL_THREAD_DETACH来调DLL的DllMain函数。

早期的SDK版本中，DllMain是叫做DllEntryPoint。其实Dll的入口函数名是可以自己定义的。

窗口回调函数的结构

```
wndclass.lpfnWndProc = WindowProc;
```

而`wndclass`是通过`RegisterClass`注册进去的，那么我们继续在od里面跟到`RegisterClass`这个函数，在push参数前面下一个断点

[![](https://p0.ssl.qhimg.com/t01d874e2f2e2e8f0cf.png)](https://p0.ssl.qhimg.com/t01d874e2f2e2e8f0cf.png)

F8单步跟下去，得到eax的值为`0019FEC0`，这个地址就是我们要找的结构

[![](https://p0.ssl.qhimg.com/t01dbdbf6564f1f89f0.png)](https://p0.ssl.qhimg.com/t01dbdbf6564f1f89f0.png)

点击右键在堆栈窗口中跟随，这里可以看到堆栈窗口中是有10个值

[![](https://p5.ssl.qhimg.com/t019480534a9f4f3ec5.png)](https://p5.ssl.qhimg.com/t019480534a9f4f3ec5.png)

在`WNDCLASS`中，第二个成员`lpfnWndProc`就是我们找的回调函数，地址为`004010F0`

```
typedef struct _WNDCLASS `{` 
    UINT       style; 
    WNDPROC    lpfnWndProc; 
    int        cbClsExtra; 
    int        cbWndExtra; 
    HINSTANCE  hInstance; 
    HICON      hIcon; 
    HCURSOR    hCursor; 
    HBRUSH     hbrBackground; 
    LPCTSTR    lpszMenuName; 
    LPCTSTR    lpszClassName; 
`}` WNDCLASS, *PWNDCLASS;
```

[![](https://p5.ssl.qhimg.com/t019b0f2d67813ff5a2.png)](https://p5.ssl.qhimg.com/t019b0f2d67813ff5a2.png)



## 具体事件处理

首先看一下具体事件处理的代码

```
LRESULT CALLBACK WindowProc(                                      
                            IN  HWND hwnd,          
                            IN  UINT uMsg,          
                            IN  WPARAM wParam,          
                            IN  LPARAM lParam          
                            )      
`{`                                      
    switch(uMsg)                                
    `{`                                
        //窗口消息                            
    case WM_CREATE:                                 
        `{`                            
            DbgPrintf("WM_CREATE %d %d\n",wParam,lParam);                        
            CREATESTRUCT* createst = (CREATESTRUCT*)lParam;                        
            DbgPrintf("CREATESTRUCT %s\n",createst-&gt;lpszClass);                        

            return 0;                        
        `}`                            
    case WM_MOVE:                                
        `{`                            
            DbgPrintf("WM_MOVE %d %d\n",wParam,lParam);                        
            POINTS points = MAKEPOINTS(lParam);                        
            DbgPrintf("X Y %d %d\n",points.x,points.y);                        

            return 0;                        
        `}`                            
    case WM_SIZE:                                
        `{`                            
            DbgPrintf("WM_SIZE %d %d\n",wParam,lParam);                        
            int newWidth  = (int)(short) LOWORD(lParam);                            
            int newHeight  = (int)(short) HIWORD(lParam);                           
            DbgPrintf("WM_SIZE %d %d\n",newWidth,newHeight);                        

            return 0;                        
        `}`                            
    case WM_DESTROY:                                
        `{`                            
            DbgPrintf("WM_DESTROY %d %d\n",wParam,lParam);                        
            PostQuitMessage(0);                        

            return 0;                        
        `}`                            
        //键盘消息                            
    case WM_KEYUP:                                
        `{`                            
            DbgPrintf("WM_KEYUP %d %d\n",wParam,lParam);                        

            return 0;                        
        `}`                            
    case WM_KEYDOWN:                                
        `{`                            
            DbgPrintf("WM_KEYDOWN %d %d\n",wParam,lParam);                        

            return 0;                        
        `}`                            
        //鼠标消息                            
    case WM_LBUTTONDOWN:                                
        `{`                            
            DbgPrintf("WM_LBUTTONDOWN %d %d\n",wParam,lParam);                        
            POINTS points = MAKEPOINTS(lParam);                        
            DbgPrintf("WM_LBUTTONDOWN %d %d\n",points.x,points.y);                        

            return 0;                        
        `}`

        //子进程鼠标信息
    case WM_COMMAND:                                
        `{`                                
            switch(LOWORD(wParam))                            
            `{`                            
                case 1001:                        
                    MessageBox(hwnd,"Hello Button 1","Demo",MB_OK);                    
                    return 0;                    
                case 1002:                        
                    MessageBox(hwnd,"Hello Button 2","Demo",MB_OK);                    
                    return 0;                    
                case 1003:                        
                    MessageBox(hwnd,"Hello Button 3","Demo",MB_OK);                    
                    return 0;                    
            `}`        
        `}`
    `}`                    

        return DefWindowProc(hwnd,uMsg,wParam,lParam);                                
`}`
```

这里继续往下找，比如我要弄清楚一个函数的具体功能，这里就以`WM_LBUTTONDOWN`为例

[![](https://p3.ssl.qhimg.com/t01c2607248661d4a05.png)](https://p3.ssl.qhimg.com/t01c2607248661d4a05.png)

`WM_LBUTTONDOWN`对应的编号为`0x0201`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01231e7a9d855885cd.png)

在回调函数的地方下个断点，这里的`[esp+0x8]`就是消息的类型

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cf86d26c7b97b917.png)

加一个条件为消息类型是`WM_LBUTTONDOWN`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015abbd43e948d53dc.png)

运行一下，当我点击右键的时候程序还是会照常运行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f3b4bc96a2851bd9.png)

当我点击左键的时候它暂停了

[![](https://p2.ssl.qhimg.com/t01db126b66779117fc.png)](https://p2.ssl.qhimg.com/t01db126b66779117fc.png)

F8单步往下跟就可以找到鼠标左键按钮处理的函数

[![](https://p3.ssl.qhimg.com/t011020778ae030f466.png)](https://p3.ssl.qhimg.com/t011020778ae030f466.png)
