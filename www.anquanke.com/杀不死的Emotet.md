> 原文链接: https://www.anquanke.com//post/id/222639 


# 杀不死的Emotet


                                阅读量   
                                **324490**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01d96112358b808e05.jpg)](https://p2.ssl.qhimg.com/t01d96112358b808e05.jpg)



## 介绍

Emotet是一种计算机恶意软件程序，最初以银行木马程序的形式开发。目的是访问外部设备并监视敏感的私有数据。众所周知，Emotet会欺骗基本的防病毒程序并将其隐藏。一旦被感染，该恶意软件就会像计算机蠕虫一样传播，并试图渗透到网络中的其他计算机。<br>
样本信息<br>
MD5：589ded5798b2dcf227b56142122a6375<br>
File Type: Win32 EXE<br>
Detection: Trojan:Win32/EmotetCrypt.ARJ!MTB



## 静态分析

使用Exeinfo查看下是没用通用壳特征的

[![](https://p4.ssl.qhimg.com/t013ae97ccadedc93f2.png)](https://p4.ssl.qhimg.com/t013ae97ccadedc93f2.png)

发现有个挺奇怪的资源rcdata\1E55

[![](https://p5.ssl.qhimg.com/t0139d181be0665e1d0.png)](https://p5.ssl.qhimg.com/t0139d181be0665e1d0.png)

使用ida打开通过这些鬼东东还是可以识别是MFC的程序，MFC的程序用户代码一般都在头部，如果有界面的话还是可以使用xspy进行解析找到按钮事件和定时器等的

[![](https://p5.ssl.qhimg.com/t0172377409adc5db2e.png)](https://p5.ssl.qhimg.com/t0172377409adc5db2e.png)



## 动态分析

对于MFC程序我一般是在ida里面头部找到用户代码下断点，或者通过xspy来找到按钮的事件来分析函数。这里的话我找到了一段比较感兴趣的用户代码，我们在调试器里面下断点到402f78

[![](https://p4.ssl.qhimg.com/t01afefa7a4d5438cc8.png)](https://p4.ssl.qhimg.com/t01afefa7a4d5438cc8.png)

这个函数先初始化了变量V7就是我们之前在资源里面看到的值还记得吗？0x1E55==7765<br>
然后在对字符串进行拼接LdrAccessResource LdrAccessResource LdrFindResource_U<br>
并且获取了LdrFindResource_U这个函数地址

[![](https://p3.ssl.qhimg.com/t018c5a40a2e14d54e3.png)](https://p3.ssl.qhimg.com/t018c5a40a2e14d54e3.png)

下面这块代码就是在调用上面的API寻找资源，然后申请内存空间然后解密

[![](https://p4.ssl.qhimg.com/t01361571dfb369962a.png)](https://p4.ssl.qhimg.com/t01361571dfb369962a.png)

调试到使用LdrFindResource_U加载资源的函数

[![](https://p5.ssl.qhimg.com/t01b5b483516076610b.png)](https://p5.ssl.qhimg.com/t01b5b483516076610b.png)

LdrFindResource_U和LdrAccessResource都是从NTdll中导出的API,LdrFindResource_U会根据资源ID找到相应的资源,如果找到,则返回相应的句柄,后续应该使用LdrAccessResource来使用该句柄。下面就是函数的声明，到这里也基本都知道流程了。

[![](https://p3.ssl.qhimg.com/t01e2ae59c615bf9537.png)](https://p3.ssl.qhimg.com/t01e2ae59c615bf9537.png)

[![](https://p4.ssl.qhimg.com/t01bbc3862dc31a71c9.png)](https://p4.ssl.qhimg.com/t01bbc3862dc31a71c9.png)

```
/*
NTSTATUS NTAPI  LdrFindResource_U (PVOID BaseAddress, PLDR_RESOURCE_INFO ResourceInfo, ULONG Level, PIMAGE_RESOURCE_DATA_ENTRY *ResourceDataEntry)
NTSTATUS NTAPI  LdrAccessResource (IN PVOID BaseAddress, IN PIMAGE_RESOURCE_DATA_ENTRY ResourceDataEntry, OUT PVOID *Resource OPTIONAL, OUT PULONG Size OPTIONAL)
*/
status = LdrFindResource_U(DllHandle, (ULONG_PTR*)&amp;IdPath, 3, &amp;DataEntry);
        if (NT_SUCCESS(status)) `{`
            status = LdrAccessResource(DllHandle, DataEntry, (PVOID*)&amp;Data, &amp;SizeOfData);
            if (NT_SUCCESS(status)) `{`
                if (DataSize) `{`
                    *DataSize = SizeOfData;
                `}`
            `}`
        `}`
```

这个函数里面就是真正的解密算法，看起来像改的RC4算法，把一个字符串算出一个值来

[![](https://p5.ssl.qhimg.com/t0170f25cc049d1f26d.png)](https://p5.ssl.qhimg.com/t0170f25cc049d1f26d.png)

[![](https://p5.ssl.qhimg.com/t01686645f72c36f847.png)](https://p5.ssl.qhimg.com/t01686645f72c36f847.png)

[![](https://p3.ssl.qhimg.com/t016e7cf051fc5aceb3.png)](https://p3.ssl.qhimg.com/t016e7cf051fc5aceb3.png)

下面一个函数就在解密资源了

[![](https://p0.ssl.qhimg.com/t01de0f5ca78b3dbf73.png)](https://p0.ssl.qhimg.com/t01de0f5ca78b3dbf73.png)

解密之后上面是代码下面是一个PE

[![](https://p5.ssl.qhimg.com/t019ff66bf741f4d21c.png)](https://p5.ssl.qhimg.com/t019ff66bf741f4d21c.png)

在资源解密的开头下断点，这些代码就是个PEloader感兴趣的话可以调试看看，这里就不浪费篇章讲解了

[![](https://p2.ssl.qhimg.com/t01b9ee8527cb14c49c.png)](https://p2.ssl.qhimg.com/t01b9ee8527cb14c49c.png)



## payloder

### <a class="reference-link" name="%E6%A0%B7%E6%9C%AC%E4%BF%A1%E6%81%AF"></a>样本信息

MD5：F24497D3168A8464E4F13AB4E45458E8<br>
File type: Win32 DLL

#### <a class="reference-link" name="%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90"></a>静态分析

发现是个dll，点进去10004070进去看

[![](https://p2.ssl.qhimg.com/t010ce4ce972763e51b.png)](https://p2.ssl.qhimg.com/t010ce4ce972763e51b.png)

又是个PE，开始dump吧，猜个这个dll没有功能就是loader

[![](https://p2.ssl.qhimg.com/t011752735800764300.png)](https://p2.ssl.qhimg.com/t011752735800764300.png)

dump下来的PE还有个可爱的图标

[![](https://p0.ssl.qhimg.com/t01a0500317a8a034d0.png)](https://p0.ssl.qhimg.com/t01a0500317a8a034d0.png)

### <a class="reference-link" name="%E6%A0%B7%E6%9C%AC%E4%BF%A1%E6%81%AF"></a>样本信息

MD5: 4434F871965FB050F1E4BA9361562466<br>
File type: Win32 DLL

#### <a class="reference-link" name="%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90"></a>静态分析

从入口进去，可以发现这个函数像是被平坦化了的。被平坦化了的函数一般使用符号执行来解决比较好吧？(PS:还有其他好的办法请告诉我谢谢)。看到这种情况我还是打算好好的用OD调试+ida看吧，目前从ida这里看不出来啥。

[![](https://p5.ssl.qhimg.com/t01ff827291516717e4.png)](https://p5.ssl.qhimg.com/t01ff827291516717e4.png)

[![](https://p0.ssl.qhimg.com/t0199c36ba1326987df.png)](https://p0.ssl.qhimg.com/t0199c36ba1326987df.png)

#### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E5%88%86%E6%9E%90"></a>动态分析

先从入口点进入平坦化的函数内部看看 406550

[![](https://p2.ssl.qhimg.com/t0140df4104a6327429.png)](https://p2.ssl.qhimg.com/t0140df4104a6327429.png)

[![](https://p2.ssl.qhimg.com/t011ffdc3a6d7626e9f.png)](https://p2.ssl.qhimg.com/t011ffdc3a6d7626e9f.png)

进入后经过一系列比较走到的第一个函数406fb0

[![](https://p0.ssl.qhimg.com/t015b42346e1303fc53.png)](https://p0.ssl.qhimg.com/t015b42346e1303fc53.png)

406fb0内部有一个函数经过交叉引用发现被调用很多次，但有不是库的，一般可以认为和解密有关，注意看他的模式一般都是mov ecx，xxxxxx 然后再call 406fb0

[![](https://p3.ssl.qhimg.com/t01a69811c810efcb5b.png)](https://p3.ssl.qhimg.com/t01a69811c810efcb5b.png)

进入函数内部也确实可以看出ecx做了一些运算

[![](https://p3.ssl.qhimg.com/t01c9ab4efbdf9366c4.png)](https://p3.ssl.qhimg.com/t01c9ab4efbdf9366c4.png)

动态调试可以发现是在找dll地址(handle) 0A2CE093Fh这个的值对应的是kerenl32.dll

[![](https://p2.ssl.qhimg.com/t01fc1a247cc418cff6.png)](https://p2.ssl.qhimg.com/t01fc1a247cc418cff6.png)

[![](https://p4.ssl.qhimg.com/t01c0f7da2e80584bb3.png)](https://p4.ssl.qhimg.com/t01c0f7da2e80584bb3.png)

获取到dll地址后，然后就返回到上个函数可以看到sub_403ED0这个函数也是交叉引用很多的，发现使用了上个函数返回的dll地址，还有一个参数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01457cb8c1237fa1b4.png)

这个函数内部的功能就是加载dll的函数 4FEE74F4h对应的就是GetPorcessHeap

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015268be3678844018.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01554d12fe034ad0e9.png)

说了这么多肯定不是为了手动调试，那样太累了还是体力活，而且效果也不咋滴。所以我把这算法给扣了下来

```
#include &lt;windows.h&gt;
void LibCrc(WCHAR* v2);
void FuncCrc(char* v1);
int main(int argc,char* argv)
`{`
    LibCrc(L"kernel32.dll");
    FuncCrc("GetProcessHeap");
`}`                         
void LibCrc(WCHAR* v3) `{`
    unsigned int v4;
    int v6 = 0;
        if (*v3)
        `{`
            do
            `{`
                v4 = (unsigned __int16)*v3;
                if (v4 &gt;= 0x41 &amp;&amp; v4 &lt;= 0x5A)
                    v4 += 32;
                ++v3;
                v6 = (v6 &lt;&lt; 16) + (v6 &lt;&lt; 6) + v4 - v6;
            `}` while (*v3);
        `}`
        void* crc = (void*)(v6 ^ 0x2DB0EF4D);
        printf("%X\r\n", crc);  
`}`
void FuncCrc(char* v1) `{`
    char *i;
    int v3; 
    v3 = 0;
    for (i = v1; *i; v3 = (v3 &lt;&lt; 16) + (v3 &lt;&lt; 6) + (char)*(i - 1) - v3)
        ++i;
    printf("%X\r\n", v3 ^ 0xBDB9B51);
`}`
```

嘿嘿结果也是对的，之后可以把常用的dll名字和函数名字跑一下出来crc。然后使用脚本对ida脚本对函数进行标注，但是在之前最后把平坦化给去除了。

[![](https://p3.ssl.qhimg.com/t01590617d501a20df4.png)](https://p3.ssl.qhimg.com/t01590617d501a20df4.png)

[![](https://p3.ssl.qhimg.com/t019a6f403b0713729e.png)](https://p3.ssl.qhimg.com/t019a6f403b0713729e.png)

#### <a class="reference-link" name="%E7%AC%A6%E5%8F%B7%E6%89%A7%E8%A1%8C%E5%8E%BB%E9%99%A4%E5%B9%B3%E5%9D%A6%E5%8C%96"></a>符号执行去除平坦化

文章参考链接利用符号执行去除控制流平坦化<br>
参考的github链接deflat<br>
符号执行第一步先把得到和ida一样的cfg图

```
filename=r"D:\code\py\env\flat_control_flow\_01CD0000"
project=angr.Project(filename, load_options=`{`'auto_load_libs': False`}`)
cfg = project.analyses.CFGFast(normalize=True, force_complete_scan=False)
target_function = cfg.functions.get(start_addr)

#转为ida一样的cfg图
supergraph = am_graph.to_supergraph(target_function.transition_graph)
```

然后分块 寻找序言 ret 主分发器 寻找真实块和nop块

```
# 寻找序言 ret
prologue_node=None
retn_node_list=[]
for node in supergraph.nodes():
    if supergraph.in_degree(node)==0:
        prologue_node=node
    if supergraph.out_degree(node) == 0 :
        retn_node_list.append(node)

#寻找主分发器
main_dispatcher_node_list=[]
main_dispatcher_node_list.append(list(supergraph.successors(prologue_node))[0])
main_dispatcher_node_list.append(list(supergraph.successors(main_dispatcher_node_list[0]))[0])

# 寻找真实块和nop块
def get_relevant_nop_nodes(supergraph, main_dispatcher_node_list, prologue_node, retn_node_list):

    relevant_nodes = []
    nop_nodes = []
    for node in supergraph.nodes():
        if supergraph.has_edge(node, main_dispatcher_node_list[0]) and node.size &gt; 8:
            relevant_nodes.append(node)
            continue
        if supergraph.has_edge(node, main_dispatcher_node_list[1]) and node.size &gt; 8:
            relevant_nodes.append(node)
            continue
        if node.addr == prologue_node.addr:
            continue
        for main_dispatcher_node in main_dispatcher_node_list:
            if node.addr == main_dispatcher_node.addr:
                continue
        for retn_node in retn_node_list:
            if node.addr == retn_node.addr:
                continue
        nop_nodes.append(node)
    return relevant_nodes, nop_nodes
```

进行符号执行把块给关联起来

```
def symbolic_execution(project, relevant_block_addrs, start_addr, hook_addrs=None, modify_value=None, inspect=False):
    def retn_procedure(state):
        ip = state.solver.eval(state.regs.ip)
        project.unhook(ip)
        return
    def statement_inspect(state):
        expressions = list(
            state.scratch.irsb.statements[state.inspect.statement].expressions)
        if len(expressions) != 0 and isinstance(expressions[0], pyvex.expr.ITE):
            state.scratch.temps[expressions[0].cond.tmp] = modify_value
            state.inspect._breakpoints['statement'] = []
    if hook_addrs is not None:
        skip_length = 4
        if project.arch.name in ARCH_X86:
            skip_length = 5
        for hook_addr in hook_addrs:
            project.hook(hook_addr, retn_procedure, length=skip_length)
    state = project.factory.blank_state(addr=start_addr, remove_options=`{`
                                        angr.sim_options.LAZY_SOLVES`}`)
    if inspect:
        state.inspect.b(
            'statement', when=angr.state_plugins.inspect.BP_BEFORE, action=statement_inspect)
    sm = project.factory.simulation_manager(state)
    sm.step()
    while len(sm.active) &gt; 0:
        for active_state in sm.active:
            if active_state.addr in relevant_block_addrs:
                return active_state.addr
        sm.step()
    return None
```

找到关系后就是patch修复了



## 总结

这里最后也没有给出标注ida或者OD函数的脚本，还有完整的修复平坦化的脚本。因为这些东西都不是通用的，给出了没有太大的意义(PS：其实是自己不想整了)。有兴趣的可以继续整下去。
