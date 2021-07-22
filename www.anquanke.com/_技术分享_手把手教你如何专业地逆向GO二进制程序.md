> 原文链接: https://www.anquanke.com//post/id/85694 


# 【技术分享】手把手教你如何专业地逆向GO二进制程序


                                阅读量   
                                **662841**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：rednaga.io
                                <br>原文地址：[https://rednaga.io/2016/09/21/reversing_go_binaries_like_a_pro/](https://rednaga.io/2016/09/21/reversing_go_binaries_like_a_pro/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t0124f60c9f601870a2.png)](https://p2.ssl.qhimg.com/t0124f60c9f601870a2.png)



翻译：[啦咔呢](http://bobao.360.cn/member/contribute?uid=79699134)

预估稿费：170RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



GO二进制程序很不可思议，至少今天一切从它讲起。当深入研究一些名为Rex的Linux恶意软件时，我意识到比起我想要的，我可能需要先理解更多的东西。就在前一周，我一直在逆向用go语言编写的Linux Lady，由于它不是一个剥离过的二进制文件，所以这很容易。显然，二进制文件是相当大的，也有许多我并不在乎的多余方法，虽然我真的只是不明白为什么。老实说，我还没有深入到Golang代码，也没有真正在Go中写很多代码，所以从表面意义上来看，这些信息有部分可能是错误的; 因为这只是我在逆向一些ELF格式Go二进制程序的经验！如果你不想读整篇文章或者只想滚动到底部去获得一个完整报告的链接，那么只需点这里。

为了解释我的案例，我要使用一个非常简单的“Hello，World！”的例子并且我还参考了Rex恶意软件。代码和Make文件非常简单；

**Hello.go**



```
package main
import "fmt"
func main() `{`
    fmt.Println("Hello, World!")
`}`
```

**Makefile**



```
all:
GOOS=linux GOARCH=386 go build -o hello-stripped -ldflags "-s" hello.go
GOOS=linux GOARCH=386 go build -o hello-normal hello.go
```

因为我在OSX机器上做这些工作，显然需要上面的GOOS和GOARCH变量来正确地交叉编译。第一行还添加了ldflags剥离二进制文件的选项。这样我们可以用剥离和不剥离的两种方式来分析相同的可执行文件。之后复制这些文件，运行make，然后在反汇编器中打开你所选择的文件，对于这个博客，我打算使用IDA Pro。如果我们在IDA Pro中打开未剥离过的二进制文件，我们可以看到如下；

[![](https://p4.ssl.qhimg.com/t012e7c6dda93064b51.png)](https://p4.ssl.qhimg.com/t012e7c6dda93064b51.png)

那么，我们的5行代码已经转化成2058个函数。越过所有运行时执行的代码，我们在main()函数上也没有什么有趣的事发生。如果进一步深究，发现其实我们感兴趣的代码实际是在main_main里面；

[![](https://p4.ssl.qhimg.com/t010fbcccb0d27aff0a.png)](https://p4.ssl.qhimg.com/t010fbcccb0d27aff0a.png)

这样很好，因为我真的不想看过多的代码。加载的字符串看起来也有点奇怪，虽然IDA似乎已经很好地识别了必要的字节。我们可以很容易地看到加载字符串实际上是一组三个mov指令；



```
String load（字符串加载）
mov     ebx, offset aHelloWorld ; "Hello, World!"
mov     [esp+3Ch+var_14], ebx ; 把字符串放到该位置上
mov     [esp+3Ch+var_10], 0Dh ; 字符串长度
```

这并不是完全颠覆性的，虽然我其实不假思索的说我以前就已经看到过这样的事情。我们也需要继续注意它，因为之后这将继续处理。引起我注意的另一个代码是runtime_morestack_context的调用;



```
morestack_context
loc_80490CB:
call    runtime_morestack_noctxt
jmp     main_main
```

这种风格的代码块似乎总是在函数的结尾，它似乎总是循环回到同一个函数的顶部。这可以通过查看对此函数的交叉引用来验证。好了，现在我们知道IDA Pro可以处理未剥离的二进制文件，让我们加载相同的代码，但是这次是剥离的版本。

[![](https://p0.ssl.qhimg.com/t01fc37205cbe2bed0e.png)](https://p0.ssl.qhimg.com/t01fc37205cbe2bed0e.png)

我们随即看到了一些结果，好吧，让我们姑且把它们称为“差异”。这里有1329个函数定义，现在通过查看导航工具栏看到一些未定义的代码。幸运的是，IDA仍然能够找到我们想寻找的字符串加载，然而这个函数现在似乎不太好处理。

[![](https://p5.ssl.qhimg.com/t01c3438d878209a417.png)](https://p5.ssl.qhimg.com/t01c3438d878209a417.png)

我们现在没有更多的函数名称了，然而，函数名称似乎保留在二进制特定的节里，如果我们给main.main做一个字符串搜索（这将呈现在前面屏幕截图的main_main函数，因为IDA遇到并识别了一个“ . ”）；



```
.gopclntab
.gopclntab：0813E174 db 6Dh; m
.gopclntab：0813E175 db 61h; a
.gopclntab：0813E176 db 69h; i
.gopclntab：0813E177 db 6Eh; n
.gopclntab：0813E178 db 2Eh; .
.gopclntab：0813E179 db 6Dh; m
.gopclntab：0813E17A db 61h; a
.gopclntab：0813E17B db 69h; i
.gopclntab：0813E17C db 6Eh; n
```

好了，这里看起来有些遗留的东西需要去研究。在深入挖掘谷歌搜索结果后进入gopclntab和关于这的推特-一个友好的逆向朋友George (Egor?)Zaytsev给我看了他的IDA Pro的脚本重命名函数并添加类型信息。浏览了这些之后，很容易理解这个部分的格式，所以我在一些功能上复制了他的脚本。基本代码如下所示，非常简单，我们看.gopclntab段并跳过前8个字节。然后我们创建一个指针（Qword或Dword，根据二进制是否是64位）。第一组数据实际上给出了.gopclntab表的大小，所以我们知道离进入这个结构有多远。现在我们可以开始处理其余的数据，这些数据出现在（函数）name_offset 后面的function_offset。当我们创建指向这些偏移的指针，并告诉IDA创建字符串，我们只需要确保我们不会传递给MakeString任何损坏的字符，因此我们使用该clean_function_name函数去除任何不好的地方。

**renamer.py**



```
def create_pointer(addr, force_size=None):
    if force_size is not 4 and (idaapi.get_inf_structure().is_64bit() or force_size is 8):
        MakeQword(addr)
return Qword(addr), 8
    else:
MakeDword(addr)
return Dword(addr), 4
STRIP_CHARS = [ '(', ')', '[', ']', '`{`', '`}`', ' ', '"' ]
REPLACE_CHARS = ['.', '*', '-', ',', ';', ':', '/', 'xb7' ]
def clean_function_name(str):
    # Kill generic 'bad' characters
    str = filter(lambda x: x in string.printable, str)
    for c in STRIP_CHARS:
        str = str.replace(c, '')
    for c in REPLACE_CHARS:
        str = str.replace(c, '_')
    return str
def renamer_init():
    renamed = 0
    gopclntab = ida_segment.get_segm_by_name('.gopclntab')
    if gopclntab is not None:
        # Skip unimportant header and goto section size
        addr = gopclntab.startEA + 8
        size, addr_size = create_pointer(addr)
        addr += addr_size
        # Unsure if this end is correct
        early_end = addr + (size * addr_size * 2)
        while addr &lt; early_end:
            func_offset, addr_size = create_pointer(addr)
            name_offset, addr_size = create_pointer(addr + addr_size)
            addr += addr_size * 2
            func_name_addr = Dword(name_offset + gopclntab.startEA + addr_size) + gopclntab.startEA
            func_name = GetString(func_name_addr)
            MakeStr(func_name_addr, func_name_addr + len(func_name))
            appended = clean_func_name = clean_function_name(func_name)
            debug('Going to remap function at 0x%x with %s - cleaned up as %s' % (func_offset, func_name, clean_func_name))
            if ida_funcs.get_func_name(func_offset) is not None:
                if MakeName(func_offset, clean_func_name):
                    renamed += 1
                else:
                    error('clean_func_name error %s' % clean_func_name)
    return renamed
def main():
    renamed = renamer_init()
    info('Found and successfully renamed %d functions!' % renamed)
```

上面的代码将不会真正运行（不用担心，完整的代码可在这个报告找到），但它总体是希望足够简单到可以通读和理解全过程。然而，这仍然不能解决IDA Pro不知道所有函数的问题。所以这将创建没有被引用的指针。我们现在知道函数的开头，然而我最终看到了（我认为是）一个更简单的方法来定义应用程序中的所有函数。我们可以通过利用runtime_morestack_noctxt函数来定义所有的函数。因为每个函数都使用了这个函数（基本上，它有一个edgecase），如果我们找到这个函数并向后遍历这个函数的交叉引用，那么我们将知道每个函数的位置。对吧？我们已经知道每个函数是从我们刚才解析的段开始的，对吧？好了，现在我们知道函数的结尾，并且在调用之后的下一条指令runtime_morestack_noctxt给我们一个到函数顶部的跳转。这意味着我们应该能够快速地给出一个函数开头和结尾的边界，这就是IDA在从解析函数名称进行区分时所需要的。如果我们打开交叉引用runtime_morestack_noctxt函数的窗口，我们将看到有更多的未定义节也在调用这个函数。总共有1774处引用这个函数的地方，其中的1329个函数已经是从IDA为我们定义出来的，而这由下面的图像显示：

[![](https://p1.ssl.qhimg.com/t01be04488ea5c483a1.png)](https://p1.ssl.qhimg.com/t01be04488ea5c483a1.png)

在深入探究多个二进制文件之后，我们可以看到runtime_morestack_noctext总是调用runtime_morestack（随着上下文）。这是我之前引用的edgecase，所以在这两个函数之间，我们应该能够看到二进制中使用其他函数的交叉引用。看两个函数中较大的一个，即runtime_more_stack，多个二进制文件往往有一个有趣的布局；

[![](https://p3.ssl.qhimg.com/t01c3e8bcbce219cb2d.png)](https://p3.ssl.qhimg.com/t01c3e8bcbce219cb2d.png)

我注意到的部分是mov large dword ptr ds:1003h, 0，这在我看到的所有64位二进制文件中似乎是比较固定的。而在交叉编译后我注意到32位二进制文件使用mov qword ptr ds:1003h，因此我们需要寻找一种模式去创建一个“钩子”来向后遍历。幸运的是，我没有看到IDA Pro定义这个特定函数的失败实例，我们并不需要花费太多的脑力来绘制它或自己去定义它。所以，说得够多了，让我写一些代码来找到这个函数；



```
find_runtime_morestack.py
def create_runtime_ms():
    debug('Attempting to find runtime_morestack function for hooking on...')
    text_seg = ida_segment.get_segm_by_name('.text')
    # This code string appears to work for ELF32 and ELF64 AFAIK
    runtime_ms_end = ida_search.find_text(text_seg.startEA, 0, 0, "word ptr ds:1003h, 0", SEARCH_DOWN)
    runtime_ms = ida_funcs.get_func(runtime_ms_end)
    if idc.MakeNameEx(runtime_ms.startEA, "runtime_morecontext", SN_PUBLIC):
        debug('Successfully found runtime_morecontext')
    else:
        debug('Failed to rename function @ 0x%x to runtime_morestack' % runtime_ms.startEA)
    return runtime_ms
```

找到函数后，我们可以递归遍历所有的函数调用，任何不在定义列表里的函数，我们现在都可以定义。这是因为结构总是出现；



```
golang_undefined_function_example
.text:08089910        ; 函数开头 –然而当前IDA Pro没定义
.text:08089910 loc_8089910:                            ; CODE XREF: .text:0808994B
.text:08089910                                        ; DATA XREF: sub_804B250+1A1
.text:08089910                 mov     ecx, large gs:0
.text:08089917                 mov     ecx, [ecx-4]
.text:0808991D                 cmp     esp, [ecx+8]
.text:08089920                 jbe     short loc_8089946
.text:08089922                 sub     esp, 4
.text:08089925                 mov     ebx, [edx+4]
.text:08089928                 mov     [esp], ebx
.text:0808992B                 cmp     dword ptr [esp], 0
.text:0808992F                 jz      short loc_808993E
.text:08089931
.text:08089931 loc_8089931:                            ; CODE XREF: .text:08089944
.text:08089931                 add     dword ptr [esp], 30h
.text:08089935                 call    sub_8052CB0
.text:0808993A                 add     esp, 4
.text:0808993D                 retn
.text:0808993E ; ---------------------------------------------------------------------------
.text:0808993E
.text:0808993E loc_808993E:                            ; CODE XREF: .text:0808992F
.text:0808993E                 mov     large ds:0, eax
.text:08089944                 jmp     short loc_8089931
.text:08089946 ; ---------------------------------------------------------------------------
.text:08089946
.text:08089946 loc_8089946:                            ; CODE XREF: .text:08089920
.text:08089946                 call    runtime_morestack ; "函数底部, 调用runtime_morestack
.text:0808994B                 jmp     short loc_8089910 ; 跳回函数“顶部”
```

上面的代码段是一个随机未定义的函数，这是我从已经编译剥离的示例应用程序中提取。基本上通过向后遍历每个未定义的函数，我们将在类似0x0808994B 执行call runtime_morestack后的地方停留。从这里我们将跳到下一个指令，并确保它是我们当前的跳转，如果条件为真，我们可以假设这是一个函数的开始。在这个例子（或几乎每个我运行的测试案例）都表明这是真的。跳转到0x08089910是函数的开始，所以现在我们有MakeFunction函数需要的两个参数：



```
traverse_functions.py
def is_simple_wrapper(addr):
    if GetMnem(addr) == 'xor' and GetOpnd(addr, 0) == 'edx' and  GetOpnd(addr, 1) == 'edx':
        addr = FindCode(addr, SEARCH_DOWN)
        if GetMnem(addr) == 'jmp' and GetOpnd(addr, 0) == 'runtime_morestack':
            return True
    return False
def create_runtime_ms():
    debug('Attempting to find runtime_morestack function for hooking on...')
    text_seg = ida_segment.get_segm_by_name('.text')
    # 这个代码字符串出现在ELF32 and ELF64 AFAIK
    runtime_ms_end = ida_search.find_text(text_seg.startEA, 0, 0, "word ptr ds:1003h, 0", SEARCH_DOWN)
    runtime_ms = ida_funcs.get_func(runtime_ms_end)
    if idc.MakeNameEx(runtime_ms.startEA, "runtime_morestack", SN_PUBLIC):
        debug('Successfully found runtime_morestack')
    else:
        debug('Failed to rename function @ 0x%x to runtime_morestack' % runtime_ms.startEA)
    return runtime_ms
def traverse_xrefs(func):
    func_created = 0
    if func is None:
        return func_created
    # 初始化
    func_xref = ida_xref.get_first_cref_to(func.startEA)
    # 尝试去遍历交叉引用
    while func_xref != 0xffffffffffffffff:
        # 检查这里是否已经有一个函数
        if ida_funcs.get_func(func_xref) is None:
            # 确保指令位像一个跳转
            func_end = FindCode(func_xref, SEARCH_DOWN)
            if GetMnem(func_end) == "jmp":
                # 确保我们正在跳回“上面”
                func_start = GetOperandValue(func_end, 0)
                if func_start &lt; func_xref:
                    if idc.MakeFunction(func_start, func_end):
                        func_created += 1
                    else:
                        # 如果失败，我们应该将其添加到失败函数列表
                        # 然后创建一个小“封装”函数并回到该函数的交叉引用
                        error('Error trying to create a function @ 0x%x - 0x%x' %(func_start, func_end))
        else:
            xref_func = ida_funcs.get_func(func_xref)
            # 简单的封装经常是runtime_morestack_noctxt，然而有时候却不是...
            if is_simple_wrapper(xref_func.startEA):
                debug('Stepping into a simple wrapper')
                func_created += traverse_xrefs(xref_func)
            if ida_funcs.get_func_name(xref_func.startEA) is not None and 'sub_' not in ida_funcs.get_func_name(xref_func.startEA):
                debug('Function @0x%x already has a name of %s; skipping...' % (func_xref, ida_funcs.get_func_name(xref_func.startEA)))
            else:
                debug('Function @ 0x%x already has a name %s' % (xref_func.startEA, ida_funcs.get_func_name(xref_func.startEA)))
        func_xref = ida_xref.get_next_cref_to(func.startEA, func_xref) 
    return func_created
def find_func_by_name(name):
    text_seg = ida_segment.get_segm_by_name('.text')
    for addr in Functions(text_seg.startEA, text_seg.endEA):
        if name == ida_funcs.get_func_name(addr):
            return ida_funcs.get_func(addr)
    return None
def runtime_init():
    func_created = 0
    if find_func_by_name('runtime_morestack') is not None:
        func_created += traverse_xrefs(find_func_by_name('runtime_morestack'))
        func_created += traverse_xrefs(find_func_by_name('runtime_morestack_noctxt'))
    else:
        runtime_ms = create_runtime_ms()
        func_created = traverse_xrefs(runtime_ms)
    return func_created
```

该代码有点冗长，但希望注释和概念足够清楚。它可能不需要显式地向后递归，但我是在理解runtime_morestack_noctxt（edgecase）是我会遇到的唯一的edgecase这点之前写的这篇文章。这原先是由is_simple_wrapper函数处理的。无论如何，运行这种风格的代码解决了找到IDA Pro丢失的所有额外函数。我们可以看到，它创造了一个更简洁的体验去更好地进行逆向工程； 

[![](https://p5.ssl.qhimg.com/t01f8f848d4c588930a.png)](https://p5.ssl.qhimg.com/t01f8f848d4c588930a.png)

它也允许我们使用类似Diaphora的工具，因为我们可以使用相同的名称去指定目标函数，如果我们也关心的话。我个人发现这对恶意软件或其他任何你不在乎框架/运行时函数的目标是非常有用的。你可以非常轻松地为二进制区分编写的自定义代码，例如在Linux恶意软件“Rex”的一切，因为都属于该命名空间！现在到最后一个在逆向恶意软件时我想解决的问题，字符串加载！老实说我不是100％肯定IDA如何检测大多数的字符串加载，可能通过某种形式的风格？或者也许是因为它可以检测基于字符0结尾处的字符串？无论如何，Go程序似乎使用某种类型的字符串表，不需要null字符。它们可以显示为字母数字顺序，也按字符串长度大小分组。这意味着我们看到它们在那里，但经常不会碰到它们正确断言为字符串，或者我们看到它们被称为极大的字符串块。“你好世界”的例子不好说明这点，所以我会展开Rex恶意软件的main.main函数来说明；

[![](https://p0.ssl.qhimg.com/t01735ab9f9d5fb2808.png)](https://p0.ssl.qhimg.com/t01735ab9f9d5fb2808.png)

我不想给所有的代码添加注释，所以我只注释了前几行，然后指向箭头处应该有指针指向一个正确的字符串。我们可以看到几个不同的用例，有时目标寄存器似乎改变了。然而，确实有一种我们可以寻找的组织模式。将指针移动到寄存器中，然后使用该寄存器压入一个（双）字指针，随后加载字符串的长度。绑定一些python代码来寻找模式，类似下面的伪代码；

**string_hunting.py**



```
#目前它通常是ebx，但在理论上可以是任何东西 - 见ebp
VALID_REGS = ['ebx', 'ebp']
#目前它通常是esp，但在理论上可以是任何东西 - 见eax
VALID_DEST = ['esp', 'eax', 'ecx', 'edx']
def is_string_load(addr):
    patterns = []
    #检查第一部分
    if GetMnem(addr) == 'mov':
        #可能是unk_或asc_，忽略的可能是loc_或inside []
        if GetOpnd(addr, 0) in VALID_REGS and not ('[' in GetOpnd(addr, 1) or 'loc_' in GetOpnd(addr, 1)) and('offset ' in GetOpnd(addr, 1) or 'h' in GetOpnd(addr, 1)):
            from_reg = GetOpnd(addr, 0)
            #检查第二部分
            addr_2 = FindCode(addr, SEARCH_DOWN)
            try:
                dest_reg = GetOpnd(addr_2, 0)[GetOpnd(addr_2, 0).index('[') + 1:GetOpnd(addr_2, 0).index('[') + 4]
            except ValueError:
                return False
            if GetMnem(addr_2) == 'mov' and dest_reg in VALID_DEST and ('[%s' % dest_reg) in GetOpnd(addr_2, 0) and GetOpnd(addr_2, 1) == from_reg:
                #检查最后一部分，可以改进
                addr_3 = FindCode(addr_2, SEARCH_DOWN)
                if GetMnem(addr_3) == 'mov' and (('[%s+' % dest_reg) in GetOpnd(addr_3, 0) or GetOpnd(addr_3, 0) in VALID_DEST) and 'offset ' not in GetOpnd(addr_3, 1) and 'dword ptr ds' not in GetOpnd(addr_3, 1):
                    try:
                        dumb_int_test = GetOperandValue(addr_3, 1)
                        if dumb_int_test &gt; 0 and dumb_int_test &lt; sys.maxsize:
                            return True
                    except ValueError:
                        return False
def create_string(addr, string_len):
    debug('Found string load @ 0x%x with length of %d' % (addr, string_len))
    #如果我们发现错误的区域，这可能是过分积极的...
    if GetStringType(addr) is not None and GetString(addr) is not None and len(GetString(addr)) != string_len:
        debug('It appears that there is already a string present @ 0x%x' % addr)
        MakeUnknown(addr, string_len, DOUNK_SIMPLE)
    if GetString(addr) is None and MakeStr(addr, addr + string_len):
        return True
    else:
        #如果某些东西已经被部分分析（不正确），我们需要MakeUnknown它
        MakeUnknown(addr, string_len, DOUNK_SIMPLE)
        if MakeStr(addr, addr + string_len):
            return True
        debug('Unable to make a string @ 0x%x with length of %d' % (addr, string_len))
    return False
```

上面的代码可能被优化，但在我所需的示例中它能正常工作。剩下的就是创建另一个函数，它通过所有定义的代码段来寻找字符串加载。然后我们可以使用指向字符串的指针和字符串长度来定义一个新的字符串MakeStr。在我最终使用的代码中，您需要确保IDA Pro没有错误地创建字符串，因为它有时会错误地尝试。当表中的字符串包含空字符时这种情况有时会发生。然而，在使用上面的代码后，我们发现了；

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019d15f1e04ce5c165.png)

这是一个更好的代码片段。在我们把所有这些函数放在一起后，我们就有了IDA Pro 的golang_loader_assist.py模块。需要提醒的是，我只在几个版本的IDA Pro OSX测试这个脚本，大部分测试版本是6.95。还有很多可以优化地方，或者重写一些较少的代码。有了这一切，我想开源此代码，让其他人可以来使用，并希望有所收获。还要注意的是，这个脚本可能会很慢让你很痛苦，这取决于idb文件大小，在OSX El Capitan（10.11.6）2.2 GHz Intel Core i7上使用IDA Pro 6.95，字符串分析方面可能需要一段时间。我经常发现，单独运行不同的方法可以防止IDA锁定。希望这篇文章和代码对某些人有帮助，祝您愉快！
