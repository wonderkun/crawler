> 原文链接: https://www.anquanke.com//post/id/83423 


# linux-inject：注入代码到运行的Linux进程中


                                阅读量   
                                **150178**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[]()

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t018afdf427df0f3d3d.jpg)](https://p4.ssl.qhimg.com/t018afdf427df0f3d3d.jpg)

最近,我遇到了[linux-inject](https://github.com/gaffe23/linux-inject/),它是一个注入程序,可以注入一个.so文件到一个运行中的应用程序进程中。类似于LD_PRELOAD环境变量所实现的功能,但它可以在程序运行过程中进行动态注入,而LD_PRELOAD是定义在程序运行前优先加载的动态链接库。事实上,linux-inject并不取代任何功能。换句话说,可以看成是忽略了LP_PRELOAD.

它的文档很匮乏,理由可能是开发人员认为大多数使用这个程序的用户不会是这个领域的新手,他们应当知道该怎么做。然而可能部分人并不是目标受众,我当时花了很久才弄清楚需要做什么,因此我希望这篇文章能够帮助别人。

我们首先需要克隆并且构建它:

```
git clone https://github.com/gaffe23/linux-inject.git
cd linux-inject
make
```

完成后,我们就可以开始这个例子了。打开另一个终端(这样你有两个可以自由使用),cd到你克隆linux-inject的目录,然后

```
cd ~/workspace/linux-inject,运行./sample-target。
```

回到第一个终端,运行

```
sudo ./inject -n sample-target sample-library.so。
```

这些都是什么意思呢,注入sample-library.so到一个进程中,进程是通过-n name指定的sample-target。如果你需要注入到指定PID的进程,你可以使用-p PID的方式。

但这有可能无法工作,因为Linux3.4中有一个名为[Yama](https://www.kernel.org/doc/Documentation/security/Yama.txt)的安全模块可以禁用 ptrace-based代码注入(或者是在代码注入期间有其他的拦截方式)。要想让它在这种情况下正常工作,你需要运行这些命令之一(出于安全考虑,我更喜欢第二个):再次尝试注入,你会在sample-target输出的“sleeping…”中看到“I just got loaded”。

```
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope # 允许任何进程注入代码到相同用户启动的进程中,root用户可以注入所有进程echo 2 | sudo tee /proc/sys/kernel/yama/ptrace_scope # 只允许root用户注入代码
```



如果你想注入自己写的代码,我必须要警告你:一些应用程序(例如VLC播放器)可能会发生段错误,因此你在编写代码的时候需要考虑到可能发生崩溃的情况。

做个简单演示,我们可以尝试注入这段代码:

```
#include &lt;stdio.h&gt;__attribute__((constructor))void hello() `{`    puts("Hello world!");`}`
```

这段C语言代码应该很容易理解,__attribute__((constructor))可能会使人迷惑。它的意思是说在函数库加载之后尽快运行这个函数。换句话说,这个函数就是要注入到进程中的代码。

编译是很简单的,没有什么特别的要求:

```
gcc -shared -fPIC -o libhello.so hello.c
```

首先需要运行sample-target,然后我们尝试注入:

```
sudo ./inject -n sample-target libhello.so
```

在长串的“sleeping…”中你应该会看到“Hello world!”。

不过还有一个问题,注入会中断程序流程。如果你尝试循环puts("Hello world!");,它会不断打印"Hello world!",主程序在注入的library结束之前不会恢复运行。也就是说,你不会再看到“sleeping…”。

要解决这个问题,你可以将注入的代码运行在单独的线程中,例如下面这段修改的代码:

```
#include &lt;stdio.h&gt;
#include &lt;unistd.h&gt;
#include &lt;pthread.h&gt;
void* thread(void* a) `{`
    while (1) `{`
        puts("Hello world!");
        usleep(1000000);
    `}`
    return NULL;
`}`
__attribute__((constructor))
void hello() `{`
    pthread_t t;
    pthread_create(&amp;t, NULL, thread, NULL);
`}`
```



它应该可以正常工作。但如果你注入sample-target,因为sample-target并没有链接libpthread这个库,因此,任何使用pthread的函数都不能正常工作。当然,如果你通过添加参数-lpthread链接了libpthread,它会正常工作。

如果我们不想重新编译目标程序,我们也可以使用一个linux-inject所依赖的函数:__libc_dlopen_mode()。为什么不是dlopen(),因为dlopen()需要链接libdl,而__libc_dlopen_mode()包含在标准C库中(这里是glibc).

这里是代码样例:

```
#include &lt;stdio.h&gt;
#include &lt;unistd.h&gt;
#include &lt;pthread.h&gt;
#include &lt;dlfcn.h&gt;
/* Forward declare these functions */
void* __libc_dlopen_mode(const char*, int);
void* __libc_dlsym(void*, const char*);
int   __libc_dlclose(void*);
void* thread(void* a) `{`
    while (1) `{`
        puts("Hello world!");
        usleep(1000000);
    `}`
`}`
__attribute__((constructor))
void hello() `{`
    /* Note libpthread.so.0. For some reason,
       using the symbolic link (libpthread.so) will not work */
    void* pthread_lib = __libc_dlopen_mode("libpthread.so.0", RTLD_LAZY);
    int(*pthread_lib_create)(void*,void*,void*(*)(void*),void*);
    pthread_t t;
    *(void**)(&amp;pthread_lib_create) = __libc_dlsym(pthread_lib, "pthread_create");
    pthread_lib_create(&amp;t, NULL, thread, NULL);
    __libc_dlclose(pthread_lib);
`}`
```

如果你没用过 dl*函数,这段代码看起来会非常吃力。但你可以查阅[相关文档](http://linux.die.net/man/3/dlopen),自己去寻求解释当然会理解的更深。

基于以上,你将可以注入自己的代码到运行中的Linux进程中。Have fun!
