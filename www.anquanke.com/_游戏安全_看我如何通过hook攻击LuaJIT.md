> 原文链接: https://www.anquanke.com//post/id/86958 


# 【游戏安全】看我如何通过hook攻击LuaJIT


                                阅读量   
                                **295895**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：nickcano.com
                                <br>原文地址：[https://nickcano.com/hooking-luajit/](https://nickcano.com/hooking-luajit/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t010cb9f01757ffb85d.png)](https://p3.ssl.qhimg.com/t010cb9f01757ffb85d.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

****

如果你在游戏行业摸爬滚打已久，你肯定听说过Lua这个名词。作为一门强大的脚本语言，Lua已经嵌入到数千种视频游戏中，提供了各种API接口，以便工程人员在游戏客户端以及服务器上添加各种功能。

我会不断强调一个观点：为了让攻击技术更加便捷、更加可靠以及更加高效，最好的方法就是攻击游戏引擎，而不是攻击游戏本身。Hook一大堆函数、定位一大堆地址本身是个很好的办法，然而这意味着只要游戏更新版本，你就需要更新你所使用的偏移量。相反，如果你hook了游戏使用的那些库，这些问题就会迎刃而解。

Lua的普及性使得它成为hook的理想目标。此外，由于游戏开发者使用Lua来添加内容及功能，因此游戏所包含的Lua环境就成为拥有大量功能的强大主机环境。

出于性能要求，使用[LuaJIT](http://luajit.org/)来替代vanilla Lua是非常常见的场景。因此，在本文中我会探讨如何攻击LuaJIT。只要稍作修改，这种攻击技术也可以应用于vanilla Lua。

<br>

**二、注入Lua代码**

****

为了创建Lua环境，我们需要调用luaL_newstate返回一个lua_State对象，然后将其作为参数，调用luaL_openlibs即可。有人可能想通过劫持luaL_newstate的执行来注入代码，然而这种方法并不能奏效。因为此时程序库还没有加载，因此加载脚本不会起到任何作用。然而，我们可以劫持**luaopen_jit**函数，这个函数正是打开程序库时所调用的最后一个函数（参考[此处](https://github.com/LuaDist/luajit/blob/master/src/lib_init.c#L18-L30)）。

动态链接LuaJIT时，我们可以查找**导出表**来定位这个函数：

[![](https://p0.ssl.qhimg.com/t013a3bab7b01871fa8.png)](https://p0.ssl.qhimg.com/t013a3bab7b01871fa8.png)

静态链接LuaJIT时，我们可以使用一些特征字符串来进行定位：

[![](https://p1.ssl.qhimg.com/t0150953daf1408d0e2.png)](https://p1.ssl.qhimg.com/t0150953daf1408d0e2.png)

一旦找到这个函数，hook就不是件难事。然而，在hook之前，我们需要找到两个函数：**luaL_loadfilex**这个函数用来加载我们的Lua脚本，**lua_pcall**这个函数用来执行Lua脚本。动态链接时，我们可以在导出表中找到这两个函数；静态链接时，我们可以使用“=stdin”字符串来定位第一个函数（参考[此处](https://github.com/LuaDist/luajit/blob/master/src/lj_load.c#L99)）：

[![](https://p1.ssl.qhimg.com/t01a4bfc5ca1627c4ac.png)](https://p1.ssl.qhimg.com/t01a4bfc5ca1627c4ac.png)

定位第二个函数需要多费点功夫，因为该函数没有关联某个特征字符串。然而幸运的是，该函数在内部调用时（参考此处），位于“=(debug command)”之后：

[![](https://p2.ssl.qhimg.com/t01546c1df8f7b99f5d.png)](https://p2.ssl.qhimg.com/t01546c1df8f7b99f5d.png)

注意，上图中我们还能观察到**luaL_loadbuffer**函数的地址，牢记这一点，回头要用到。

识别出这些地址后，我们就可以开始写hook代码了：

```
typedef void* lua_State;

typedef int (*_luaL_loadfilex)(lua_State *L, const char *filename, const char *mode);
_luaL_loadfilex luaL_loadfilex;

typedef int (*_luaopen_jit)(lua_State *L);
_luaopen_jit luaopen_jit_original;

typedef int (*_lua_pcall)(lua_State *L, int nargs, int nresults, int errfunc);
_lua_pcall lua_pcall;

int luaopen_jit_hook(lua_State *L)
`{`
    int ret_val = luaopen_jit_original(L);
    luaL_loadfilex(L, "C:\test.lua", NULL) || lua_pcall(L, 0, -1, 0);
    return ret_val;
`}`

BOOL APIENTRY DllMain(HMODULE mod, DWORD reason, LPVOID res)
`{`
    switch (reason) `{`
    case DLL_PROCESS_ATTACH: `{`
            luaL_loadfilex = (_luaL_loadfilex)LOADFILEEX_ADDR;
            lua_pcall = (_lua_pcall)PCALL_ADDR;
            HookCode(OPENJIT_ADDR, luaopen_jit_hook, (void**)&amp;luaopen_jit_original);
            break;
        `}`
    `}`
    return TRUE;
`}`
```

我的hook代码如上所示，使用的是自己开发的hook引擎。你可以使用[Detours](https://www.microsoft.com/en-us/research/project/detours/)或者自己的引擎。需要牢记的是，hook点应该位于DLL中，以便注入到进程中。

现在，创建Lua环境时，“**C:test.lua**”就会被加载到这个环境中。通常情况下，我首先会注入代码，使用**debug.sethook**来劫持对Lua函数的所有调用以及相应的参数，以便后续分析：



```
lua jit.off()
FILEPATH = "C:LuaJitHookLogs" STARTINGTIME = os.clock() GDUMPED = false
function dumpGlobals() local fname = FILEPATH .. "globals" .. STARTING_TIME .. ".txt" local globalsFile = io.open(fname, "w") globalsFile:write(table.show(G, "G")) globalsFile:flush() globalsFile:close() end
function trace(event, line) local info = debug.getinfo(2)
if not info then return end
if not info.name then return end
if string.len(info.name) &lt;= 1 then return end
if (not GDUMPED) then
    dumpGlobals()
    GDUMPED = true
end
local fname = FILE_PATH .. "trace_" .. STARTING_TIME .. ".txt"
local traceFile = io.open(fname, "a")
traceFile:write(info.name .. "()n")
local a = 1
while true do
    local name, value = debug.getlocal(2, a)
    if not name then break end
    if not value then break end
    traceFile:write(tostring(name) .. ": " .. tostring(value) .. "n")
    a = a + 1
end
traceFile:flush()
traceFile:close()
end debug.sethook(trace, "c")
```

这段代码可以提取到一堆有价值的全局信息以及跟踪信息，存放在“**C:LuaJitHookLogs**”目录下。

<br>

**三、详细分析**

****

如果你非常熟悉Lua，你可以跳过这个部分，不然的话，你可以跟着我分析这个脚本的具体内容。

首先，我调用了jit.off函数，因为debug库无法劫持由jit引擎实时编译的那些调用代码。

在dumpGlobals函数内部，我将名为_G的表打印出来。这是个全局对象表，Lua使用这个表来跟踪全局域内的所有内容，并将跟踪结果以“key, value”键值对形式保存在该表中。你肯定能够想到，这个表的价值非常高。根据你的具体情况，你可能需要晚一点再调用dumpGlobals函数，因为有些游戏在调用第一个函数时并没有把所有的全局变量分配完毕。

我使用了**debug.sethook(trace, "c")**语句，使Lua在每个函数调用完成之前调用trace这个函数。在trace函数内部，我调用了**debug.getinfo(2)**以获取被劫持的函数名称。由于trace函数为当前正在使用的函数，也就是说该函数在栈上的级别为1，因此被劫持的函数的级别为2。然后我循环调用了debug.getlocal(2, a)，其中a的值从1开始不断累加，直至该语句返回空值（nil）为止。通过这种方式，我们可以循环遍历级别为2的栈，找到所有的本地变量，并将查找结果以键值对的形式保存起来。对某个游戏这样处理后，我找到了如下信息，你可以根据这些信息猜到这是哪个游戏：

```
type()
(*temporary): table: 074FA7D0
`{`
    IsDestroyed = false,
    NumOfSpawnDisables = 0,
    SpawnOrderMinionNames = 
    `{`
        "Super",
        "Melee",
        "Cannon",
        "Caster",
    `}`,
    WillSpawnSuperMinion = 0,
`}`
```

我们可以调用type来确定对象的类型，但对象本身就可以告诉我们关于该游戏的一些有趣信息。

如果我们愿意的话，我们可以使用debug.setlocal将参数改成某些函数。

<br>

**四、劫持Lua代码**

****

在许多情况下，我们需要劫持整个Lua脚本。通过这种方式，我们不需要将跟踪结果拼接起来，就可以详细分析游戏所用的脚本，理解脚本具体功能。Lua代码可以以文件或者缓冲区的形式加载到LuaJIT环境中。由于分析磁盘上的文件比较容易，因此我们会重点关注使用缓冲区的这种情况以及luaL_loadbuffer这个函数。

这个函数实际上有两种表现形式：分别为luaL_loadbuffer以及luaL_loadbufferex。这两个函数基本相同，第一个函数会调用第二个函数，只不过会把最后一个参数设为NULL（[参考此处](https://github.com/LuaDist/luajit/blob/master/src/lj_load.c#L146-L155)）。你可以会认为，只要hook luaL_loadbufferex这个函数，我们就可以搞定这两种情况，然而事实并非如此。由于LuaJIT主要是针对性能优化而设计的，因此通常情况下luaL_loadbufferex会以内联形式使用。然而，这两个函数最终都会调用如下这个函数（[参考此处](https://github.com/LuaDist/luajit/blob/master/src/lj_load.c#L48-L62)）：

```
int lua_loadx(lua_State *L, lua_Reader reader, void *data, const char *chunkname, const char *mode);
```

LuaJIT偏向于使用内联代码，导致这个函数也变成内联形式。然而，这里最有用的是lua_Reader reader，这个回调函数知道如何将void *data转换为包含Lua代码的缓冲区。当LuaJIT加载位于缓冲区中的代码时，reader变为reader_string的地址（[参考此处](https://github.com/LuaDist/luajit/blob/master/src/lj_load.c#L127-L135)），而void *data所指向的char*字符串即为具体的Lua代码。

**reader_string**不是内联函数，因为它的地址可以作为回调指针来传递，因此我们可以在luaL_loadbuffer内部找到这个地址：

[![](https://p3.ssl.qhimg.com/t01f995a7aaeabaf8df.png)](https://p3.ssl.qhimg.com/t01f995a7aaeabaf8df.png)

利用这个地址，我们可以构造一个hook，来劫持并显示已加载的所有Lua缓冲区：

```
typedef const char* (*_reader_string)(lua_State *L, void *ud, size_t *size);
_reader_string reader_string_original;

const char* reader_string_hook(lua_State *L, void *ud, size_t *size)
`{`
    if (((size_t*)ud)[1] &gt; 0)
        MessageBoxA(NULL, ((char**)ud)[0], "LuaJITHook", MB_OK);
    return reader_string_original(L, ud, size);
`}`

// from DllMain DLL_PROCESS_ATTACH
HookCode(READERSTRING_ADDR, reader_string_hook, (void**)&amp;reader_string_original);
```

当然使用对话框来显示并不是优雅的解决办法，不要在意这个细节，你理解我的意思就可以了。

<br>

**五、总结**

****

这种方法非常强大。许多游戏提供了Lua脚本功能，可以实现自动化、拉高游戏视图以及ESP（透视）黑科技等。不同的游戏使用Lua的方法有所不同，但他们的工作原理都与本文的例子相似。

你可以在这段hook代码的基础上进行修改，添加扫描功能，自动定位这些函数，比如，你可以使用[XenoScan](https://github.com/nickcano/XenoScan)这个库来完成这个任务。

如果你有什么意见或者建议，可以随时发表评论，也可以关注我的[推特](https://twitter.com/nickcano93)了解我最新发布的信息。
