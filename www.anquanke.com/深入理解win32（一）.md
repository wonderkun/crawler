> 原文链接: https://www.anquanke.com//post/id/259450 


# 深入理解win32（一）


                                阅读量   
                                **117730**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01e94717568627114f.jpg)](https://p3.ssl.qhimg.com/t01e94717568627114f.jpg)



## 前言

Win32是指Microsoft Windows操作系统的32位环境，与Win64 都为Windows常见环境。如今的Win32操作系统可以一边听音乐，一边编程，一边打印文档。Win32操作系统是一个典型的多线程操作系统。

从单线程到多进程是操作系统发展的一种必然趋势，当年的DOS系统属于单任务操作系统，最优秀的程序员也只能通过驻留内存的方式实现所谓的”多任务”，而如今的Win32操作系统却可以一边听音乐，一边编程，一边打印文档。

理解多线程及其同步、互斥等通信方式是理解现代操作系统的关键一环，当我们精通了Win32多线程程序设计后，理解和学习其它操作系统的多任务控制也非常容易。许多程序员从来没有学习过嵌入式系统领域著名的操作系统VxWorks，但是立马就能在上面做开发，大概要归功于平时在Win32多线程上下的功夫。

因此，学习Win32多线程不仅对理解Win32本身有重要意义，而且对学习和领会其它操作系统也有触类旁通的作用。

今天带来的是win32里面最基础的一些知识，事件、消息以及消息处理函数



## 事件与消息

事件：Windows中的事件是一个“动作”，这个动作可能是用户操作应用程序产生的，也可能是Windows自己产生的

消息：用来描述动作，具体描述动作到底做了什么事。例如：这个动作在什么时候产生、哪个应用产生的、在什么位置产生的等等

消息本身是作为一个记录传递给应用程序的，这个记录（一般在 C/C++/汇编 中称为“结构体”）中包含了消息的类型以及其他信息。例如，对单击鼠标所产生的消息来说，这个记录（结构体）中包含了单击鼠标的消息号（WM_LBUTTONDOWN）、单击鼠标时的坐标(由X,Y值连接而成的一个32位整数)。

消息对应的结构体为MSG，具体结构如下

### <a class="reference-link" name="MSG%E7%BB%93%E6%9E%84"></a>MSG结构

```
typedef struct tagMSG `{`    
  HWND   hwnd;     
  UINT   message;     
  WPARAM wParam;     
  LPARAM lParam;     
  DWORD  time;     
  POINT  pt;     
`}` MSG, *PMSG;
```

> <ul>
- **hwnd**
</ul>
Handle to the window whose window procedure receives the message.
hwnd表示消息所属的窗口，这里可以理解为一个唯一的标识，一个消息一般与某个窗口相关联，在windows中HWND类型变量通常来表示窗口。
<ul>
- **message**
</ul>
Specifies the message identifier. Applications can only use the low word; the high word is reserved by the system.
windows中消息是由一个数值进行表示的，但是数值不方便记忆，所以windows将消息对应的数值定义为WM_XXX宏（WM == Windows Message）
鼠标左键按下 WM_LBUTTONDOWN 键盘按下 WM_KEYDOWN，message就是消息类型
<ul>
- **wParam**
</ul>
Specifies additional information about the message. The exact meaning depends on the value of the **message** member.
<ul>
- **lParam**
</ul>
Specifies additional information about the message. The exact meaning depends on the value of the **message** member.
32位消息的特定附加信息,具体表示什么取决于message
<ul>
- **time**
</ul>
Specifies the time at which the message was posted.
消息创建时的时间
<ul>
- **pt**
</ul>
Specifies the cursor position, in screen coordinates, when the message was posted.
记录鼠标所在分辨率的坐标



## 系统消息队列与应用消息队列

当事件传入过后封装为MSG形成消息，因为这时候所有队列都是一起的，这里的结构跟之前C++提到的`vector`类似，但是这里是先进先出，即不是封闭的。当消息传入之后，windows首先会对这些消息通过hwnd进行分类，以区分不同应用的不同消息。

[![](https://p1.ssl.qhimg.com/t012e9cbe43f82fb430.png)](https://p1.ssl.qhimg.com/t012e9cbe43f82fb430.png)

[![](https://p4.ssl.qhimg.com/t018624438aaff73578.png)](https://p4.ssl.qhimg.com/t018624438aaff73578.png)

这里在进行应用消息队列的区分后，windows会从这个队列中取出消息，注意这里应用程序随时会进行更改，所以这里windows做的是一个取消息的循环，即从消息队列中一直取消息出来。再取消息之后，会进行消息的判断，这个判断就是判断消息所进行的操作是不是我这个应用程序所设置的一些操作（例如一个消息框，我在其他空白区域点击的时候都不会进行操作，当我点击发送这个按钮的时候，windows才会执行相应的操作），如果跟应用程序所设置的操作相同，就调用应用程序的相关函数，如果不是的话，就交付给windows进行处理。

这里消息的整个过程可以总结如下；

> 事件 -&gt; MSG -&gt; 系统消息队列 -&gt; 应用消息队列 -&gt; 循环取出消息 -&gt;处理消息

[![](https://p5.ssl.qhimg.com/t01211620f6160bb592.png)](https://p5.ssl.qhimg.com/t01211620f6160bb592.png)



## 第一个图形界面程序

`WNDCLASS`用于创建窗口，看一下MSDN的解释

> The **WNDCLASS** structure contains the window class attributes that are registered by the [**RegisterClass**](winclass_70s3.htm) function.

这里说了`WNDCLASS`这个结构体包含了许多windows里面的类，需要用`RegisterClass`这个函数进行注册

看一下`WNDCLASS`这个结构体

### <a class="reference-link" name="WNDCLASS%E7%BB%93%E6%9E%84"></a>WNDCLASS结构

```
typedef struct _WNDCLASS `{` 
    UINT       style; 
    WNDPROC    lpfnWndProc;     //窗口的消息处理函数
    int        cbClsExtra; 
    int        cbWndExtra; 
    HINSTANCE  hInstance;     //窗口属于的应用程序
    HICON      hIcon;     //窗口图片标识
    HCURSOR    hCursor;     //鼠标形状
    HBRUSH     hbrBackground;     //窗口背景色
    LPCTSTR    lpszMenuName;     //菜单名字
    LPCTSTR    lpszClassName;     //结构体名字
`}` WNDCLASS, *PWNDCLASS;
```

首先定义一下结构体里面的成员，这里其他三个成员都已经定义好，但是这个`WindowProc`即窗口过程函数有点特殊

[![](https://p0.ssl.qhimg.com/t014d572b97e7b9eaa8.png)](https://p0.ssl.qhimg.com/t014d572b97e7b9eaa8.png)

`WindowProc`的结构如下

> The **WindowProc** function is an application-defined function that processes messages sent to a window. The **WNDPROC** type defines a pointer to this callback function. **WindowProc** is a placeholder for the application-defined function name.

```
LRESULT CALLBACK WindowProc(
  HWND hwnd,      // handle to window
  UINT uMsg,      // message identifier
  WPARAM wParam,  // first message parameter
  LPARAM lParam   // second message parameter
);
```

然后写一个对应结构的`WindowProc`，代码如下：

```
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
    `}`                                
    return DefWindowProc(hwnd,uMsg,wParam,lParam);                                
`}`
```

然后创建窗口，这里注意一下类名，windows系统自带了一些类名，如使用`button`的话就会生成一个按钮，而我们不想使用windows自带的窗口，所以在这里类名就需要填自己创建的

```
// 创建窗口                              
HWND hwnd = CreateWindow(                              
    className,                //类名        
    TEXT("我的第一个窗口"),                //窗口标题        
    WS_OVERLAPPEDWINDOW,                //窗口外观样式         
    10,                //相对于父窗口的X坐标        
    10,                //相对于父窗口的Y坐标        
    600,                //窗口的宽度          
    300,                //窗口的高度          
    NULL,                //父窗口句柄，为NULL          
    NULL,                //菜单句柄，为NULL          
    hInstance,                //当前应用程序的句柄          
    NULL);                //附加数据一般为NULL        

if(hwnd == NULL)                    //是否创建成功          
    return 0;
```

这里直接编译运行没有报错但是没有窗口运行起来，回头找一下原因

[![](https://p0.ssl.qhimg.com/t01b0174f94b33c8af3.png)](https://p0.ssl.qhimg.com/t01b0174f94b33c8af3.png)

上面提到过`WNDCLASS`这个结构体是需要定义很多个成员的，但是并不是每个成员都必须要定义，所以在之前只能定义了几个成员

[![](https://p1.ssl.qhimg.com/t013a70f7ee91bc687c.png)](https://p1.ssl.qhimg.com/t013a70f7ee91bc687c.png)

再往下走到`RegisterClass`这个函数，到msdn看一下定义

> RegisterClass
The **RegisterClass** function registers a window class for subsequent use in calls to the [**CreateWindow**](windows_33jr.htm) or [**CreateWindowEx**](windows_1w6w.htm) function.
**Note** The **RegisterClass** function has been superseded by the [**RegisterClassEx**](winclass_0wc8.htm) function. You can still use **RegisterClass**, however, if you do not need to set the class small icon.

```
ATOM RegisterClass(
  CONST WNDCLASS *lpWndClass  // class data
);
```

> Parameters
<ul>
- **lpWndClass**
</ul>
[in] Pointer to a [**WNDCLASS**](winclass_8yk2.htm) structure. You must fill the structure with the appropriate class attributes before passing it to the function.

注意看一下这个下面的定义，`You must fill the structure with the appropriate class attributes before passing it to the function.`，也就是说无论用不用`WNDCLASS`这个结构体的成员，都要给成员附上值

那么这里直接给`WNDCLASS`定义成0即可

[![](https://p1.ssl.qhimg.com/t0101ede5572f6fcd26.png)](https://p1.ssl.qhimg.com/t0101ede5572f6fcd26.png)

这里查看一下`WNDCLASS wndclass;`和`WNDCLASS wndclass = `{`0`}`;`的区别，`WNDCLASS wndclass`相当于直接创建了一个结构体`wndclass`，并没有对结构体中的成员进行任何的操作，所以没有压栈出栈的操作，自然也没有反汇编；而`WNDCLASS wndclass = `{`0`}``相当于给结构体里面的每个成员都赋初始值为0，所以有反汇编出现

[![](https://p2.ssl.qhimg.com/t017f0bf3dcfd6df6f0.png)](https://p2.ssl.qhimg.com/t017f0bf3dcfd6df6f0.png)

[![](https://p0.ssl.qhimg.com/t01fd5b764f34877d52.png)](https://p0.ssl.qhimg.com/t01fd5b764f34877d52.png)

修改之后这里就可以弹出窗口

[![](https://p5.ssl.qhimg.com/t01b436b733ec965c6e.png)](https://p5.ssl.qhimg.com/t01b436b733ec965c6e.png)

这里点击缩小、放大、关闭都能够有对应的操作，但是这里我们并没有写这些函数，是因为我们使用了一个windows的回调函数，我们之前在分析的时候提到过一些不是应用程序需要的操作就不会调用应用程序自己的函数，而会交给操作系统去处理，所以这里就必须要返回一个`DefWindowsProc()`交付给windows处理

另外一个点`lpfnWndProc`并不是调用了`WindowsProc`这个函数，而是通过一个指针指向了`WindowsProc`这个函数，等待着windows调用，这就称为回调函数

[![](https://p3.ssl.qhimg.com/t015152ef5fae2fc10d.png)](https://p3.ssl.qhimg.com/t015152ef5fae2fc10d.png)

[![](https://p5.ssl.qhimg.com/t01d5715b5c27a24c9a.png)](https://p5.ssl.qhimg.com/t01d5715b5c27a24c9a.png)

这里我们在f5运行程序之后，点击关闭我们生成的这个程序之后，发现程序并没有退出，到任务管理器里面看这个进程还在

[![](https://p1.ssl.qhimg.com/t018a9558cd997b1f69.png)](https://p1.ssl.qhimg.com/t018a9558cd997b1f69.png)

每一个消息都有一个对应的编号，来到回调函数f12跟进去查看

[![](https://p2.ssl.qhimg.com/t01e6814cd15af41240.png)](https://p2.ssl.qhimg.com/t01e6814cd15af41240.png)



## windows消息范围说明

0 ～ WM_USER – 1系统消息

WM_USER ～ 0x7FFF自定义窗口类整数消息

WM_APP ～ 0xBFFF应用程序自定义消息

0xC000 ～ 0xFFFF应用程序字符串消息

0xFFFF以后 系统应用保留



## WindowProc结构探究

我们知道`WindowProc`的结构如下所示

```
LRESULT CALLBACK WindowProc(
  HWND hwnd,       // handle to window
  UINT uMsg,       // WM_CREATE
  WPARAM wParam,   // not used
  LPARAM lParam    // creation data (LPCREATESTRUCT)
);
```

探究以下`WM_CREATE`函数中`wParam`和`lParam`的用法

> <ul>
<li>
**wParam**This parameter is not used.</li>
<li>
**lParam**Pointer to a [**CREATESTRUCT**](windows_06lu.htm) structure that contains information about the window being created.</li>
</ul>

这里可以看到`wParam`这个参数是不使用的，`lParam`这个参数指向的是一个结构体`CREATESTRUCT`，这里继续探究`CREATESTRUCT`这个结构体

创建一个结构体指针看一下结构体里面有哪些成员

[![](https://p3.ssl.qhimg.com/t01ccd2249994b16e0c.png)](https://p3.ssl.qhimg.com/t01ccd2249994b16e0c.png)

打印一下`lpszclass`看一下

[![](https://p4.ssl.qhimg.com/t01007db8c5aefbf6f8.png)](https://p4.ssl.qhimg.com/t01007db8c5aefbf6f8.png)

再探究一个函数`WM_MOVE`，首先打印它的id，可以看到这里id为3

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d0f107e3e89572ff.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017fb9b0960dcfcdf9.png)

继续msdn查看`WM_MOVE`的结构中的`wParam`和`lParam`

> <ul>
- **wParam**
</ul>
This parameter is not used.
<ul>
- **lParam**
</ul>
Specifies the x and y coordinates of the upper-left corner of the client area of the window. The low-order word contains the x-coordinate while the high-order word contains the y coordinate.

这里同样`wParam`是不使用的，`lParam`表示窗口的坐标，并且低位表示x坐标，高位表示y坐标

这里看到msdn已经给我们给出了使用的方法，这里直接调用一下

[![](https://p4.ssl.qhimg.com/t014d1a36aa0cfcebd0.png)](https://p4.ssl.qhimg.com/t014d1a36aa0cfcebd0.png)

写一个输出函数

[![](https://p1.ssl.qhimg.com/t01e881ecc9f52a7afb.png)](https://p1.ssl.qhimg.com/t01e881ecc9f52a7afb.png)

[![](https://p1.ssl.qhimg.com/t0115296c50e44c10cf.png)](https://p1.ssl.qhimg.com/t0115296c50e44c10cf.png)

继续探究`WM_SIZE`，这里跟之前不一样的是`wParam`在`WM_SIZE`里面是有意义的，这里先不细说，还是先看`lParam`属性

[![](https://p2.ssl.qhimg.com/t01a565118d5c471495.png)](https://p2.ssl.qhimg.com/t01a565118d5c471495.png)

> <ul>
<li>
**lParam**The low-order word of **lParam** specifies the new width of the client area.
The high-order word of **lParam** specifies the new height of the client area.
</li>
</ul>

还是熟悉的配方，只不过这里是低位为宽，高位为高，打印一下`wParam`和`lParam`属性

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fb2b1769a6ab0d8d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0112d50dc72b0cd113.png)

这里发现`wParam`属性始终为0，这里回到定义的地方看一下，当窗口最大化、最小化操作时这个值才会变化

[![](https://p5.ssl.qhimg.com/t01276667da26d29efc.png)](https://p5.ssl.qhimg.com/t01276667da26d29efc.png)

这里再分别把`lParam`属性的低位和高位分别打印出来如下图所示

[![](https://p3.ssl.qhimg.com/t01f1a010d4624f87b4.png)](https://p3.ssl.qhimg.com/t01f1a010d4624f87b4.png)

[![](https://p2.ssl.qhimg.com/t0110c1fd345c016d53.png)](https://p2.ssl.qhimg.com/t0110c1fd345c016d53.png)
