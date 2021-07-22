> 原文链接: https://www.anquanke.com//post/id/151898 


# 如何使用 IDAPython 寻找漏洞


                                阅读量   
                                **248328**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：somersetrecon.com
                                <br>原文地址：[https://www.somersetrecon.com/blog/2018/7/6/introduction-to-idapython-for-vulnerability-hunting](https://www.somersetrecon.com/blog/2018/7/6/introduction-to-idapython-for-vulnerability-hunting)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01c3a6e7965f46643b.jpg)](https://p3.ssl.qhimg.com/t01c3a6e7965f46643b.jpg)

## 概览

IDAPython是一个强大的工具，可用于自动化繁琐复杂的逆向工程任务。虽然已经有很多关于使用IDAPython来简化基本的逆向工程的文章，但是很少有关于使用IDAPython来帮助审查二进制文件以发现漏洞的文章。因为这不是一个新想法(HalvarFlake在2001年提出了关于使用IDA脚本自动化漏洞研究的文章)，所以没有更多关于这个主题的文章是有点令人惊讶的。这可能部分是因为在现代操作系统上执行利用操作所需的复杂性日益增加。但是，能够将部分漏洞研究过程自动化仍然很有价值。

在这篇文章中，我们将开始介绍如何使用基本的IDAPython技术来检测危险的代码，它们常常导致堆栈缓冲区溢出。在这篇博文中，我将使用[http://pwnable[.]kr](http://pwnable%5B.%5Dkr)中的“ascii_easy”二进制文件自动检测基本堆栈缓冲区溢出。虽然这个二进制文件足够小，可以完全手动逆向，但它是一个很好的示例，可以将相同的IDAPython技术应用到更大、更复杂的二进制文件中。



## 开始

在开始编写IDAPython之前，我们必须首先确定希望脚本查找什么内容。在本例中，我选择了具有最简单类型漏洞之一的二进制文件，这是由使用“strcpy”将用户控制的字符串复制到堆栈缓冲区所造成的堆栈缓冲区溢出。既然我们已经知道了我们要寻找什么，我们就可以开始考虑如何自动查找这些类型的漏洞了。

为了达到目的，我们将把它分成两个步骤：
1. 查找可能导致堆栈缓冲区溢出的所有函数调用(在本例中是”strcpy”)
1. 分析函数调用的使用以确定使用是否符合条件(可能导致可利用的溢出)


## 查找函数调用

为了找到对“strcpy”函数的所有调用，我们必须首先定位“strcpy”函数本身。使用IDAPython API提供的功能很容易做到这一点。使用下面的代码，我们可以打印出二进制文件中的所有函数名：

```
for functionAddr in Functions():    
   print(GetFunctionName(functionAddr))
```

在ascii_easy二进制文件上运行这个IDAPython脚本会给出以下输出。我们可以看到所有的函数名都打印在IDA Pro的输出窗口中。

[![](https://p5.ssl.qhimg.com/t0150e39aa327816515.png)](https://p5.ssl.qhimg.com/t0150e39aa327816515.png)

接下来，我们添加代码来过滤函数列表，以便找到我们感兴趣的‘strcpy’函数。简单的字符串比较将在这里发挥作用。由于我们通常处理的函数类似，但由于导入函数的命名方式略有不同(例如示例程序中的“strcpy” vs“_strcpy”)，所以最好检查子串，而不是确切的字符串。

在前面的代码的基础上，我们现在有了以下代码：

```
for functionAddr in Functions():    
    if “strcpy” in GetFunctionName(functionAddr):        
        print hex(functionAddr)
```

现在我们找到了要找的函数，我们必须确定所有调用它的位置。这涉及到几个步骤。首先，我们得到所有对“strcpy”的交叉引用，然后检查每个交叉引用，找出哪些交叉引用是实际的`strcpy’函数调用。把所有这些放在一起，我们就会得到下面这段代码：

```
for functionAddr in Functions():    
    # Check each function to look for strcpy        
    if "strcpy" in GetFunctionName(functionAddr): 
        xrefs = CodeRefsTo(functionAddr, False)                
        # Iterate over each cross-reference
        for xref in xrefs:                            
            # Check to see if this cross-reference is a function call                            
            if GetMnem(xref).lower() == "call":           
                print hex(xref)
```

对ascii_easy二进制文件运行这个命令将生成二进制文件中所有的“strcpy”调用。结果如下：

[![](https://p4.ssl.qhimg.com/t017753e09748e5af80.png)](https://p4.ssl.qhimg.com/t017753e09748e5af80.png)



## 函数调用分析

现在，通过上面的代码，我们知道如何在程序中获取所有调用的地址。虽然在ascii_easy应用程序中，只有一个对“strcpy”的调用(碰巧它也是易受攻击的)，但许多应用程序都会有大量对“strcpy”的调用(大量的调用并不容易受到攻击)，因此我们需要某种方法来分析对“strcpy”的调用，以便对更容易受到攻击的函数调用进行优先级排序。

可利用缓冲区溢出的一个常见特征是，它们常常涉及堆栈缓冲区。虽然利用堆和其他地方的缓冲区溢出是可能的，但是堆栈缓冲区溢出是一种更简单的利用途径。

这涉及到对strcpy函数的目标参数的一些分析。我们知道目标参数是strcpy函数的第一个参数，我们可以从函数调用的反汇编中找到这个参数。以下是对strcpy调用的反汇编。

[![](https://p3.ssl.qhimg.com/t01f87eaf5f2728b64b.png)](https://p3.ssl.qhimg.com/t01f87eaf5f2728b64b.png)

在分析上面的代码时，有两种方法可以找到_strcpy函数的目标参数。第一种方法是依赖自动IDA Pro分析，它自动注释已知的函数参数。正如我们在上面的截图中所看到的，IDA Pro自动检测到了_strcpy函数的“dest”参数，并在将参数推送到堆栈中的指令处用注释将其标记为dest参数。

检测函数参数的另一种简单方法是向后移动汇编代码，从函数调用开始寻找“push”指令。每当我们找到一条指令，我们就可以增加一个计数器，直到找到我们正在寻找的参数的索引为止。在这种情况下，由于我们正在寻找恰巧是第一个参数的“dest”参数，该方法将在函数调用之前的“push”指令的第一个实例处停止。

在这两种情况下，当我们向后遍历代码时，我们必须小心识别破坏顺序代码流的某些指令。诸如“ret”和“jmp”之类的指令会导致代码流的更改，从而难以准确识别参数。此外，我们还必须确保不会在当前函数的开始处向后遍历代码。现在，我们将在搜索参数时简单地识别非顺序代码流的实例，如果找到任何非顺序代码流实例，则停止搜索。

我们将使用第二种方法查找参数(寻找被推到堆栈中的参数)。为了以这种方式帮助我们找到参数，我们应该创建一个帮助函数，这个函数将从函数调用的地址向后跟踪推送到堆栈中的参数，并返回与指定参数对应的操作数。

因此，对于上面调用ascii_easy中的_strcpy的示例，我们的帮助函数将返回值“eax”，因为“eax”寄存器在将strcpy作为参数推送到堆栈中时，存储它的目标参数为_strcpy。结合使用一些基本的python和IDAPython API，我们可以构建一个函数来实现这一点，如下所示。

```
def find_arg(addr, arg_num):
   # Get the start address of the function that we are in
   function_head = GetFunctionAttr(addr, idc.FUNCATTR_START)    
   steps = 0
   arg_count = 0
   # It is unlikely the arguments are 100 instructions away, include this as a safety check
   while steps &lt; 100:    
       steps = steps + 1
       # Get the previous instruction
       addr = idc.PrevHead(addr)  
       # Get the name of the previous instruction
       op = GetMnem(addr).lower()         
       # Check to ensure that we haven’t reached anything that breaks sequential code flow        
       if op in ("ret", "retn", "jmp", "b") or addr &lt; function_head:
           return
       if op == "push":
           arg_count = arg_count + 1
           if arg_count == arg_num:
               # Return the operand that was pushed to the stack
               return GetOpnd(addr, 0)
```

使用这个帮助函数，我们能够确定在调用_strcpy之前使用了“eax”寄存器来存储目标参数。为了确定eax在被推入堆栈时是否指向堆栈缓冲区，我们现在必须继续尝试跟踪“eax”中的值来自何处。为了做到这一点，我们使用了类似于以前帮助函数中使用的搜索循环：

```
# Assume _addr is the address of the call to _strcpy 
# Assume opnd is “eax” 
# Find the start address of the function that we are searching in
function_head = GetFunctionAttr(_addr, idc.FUNCATTR_START)
addr = _addr 
while True:
   _addr = idc.PrevHead(_addr)
   _op = GetMnem(_addr).lower()    
   if _op in ("ret", "retn", "jmp", "b") or _addr &lt; function_head:
       break
   elif _op == "lea" and GetOpnd(_addr, 0) == opnd:
       # We found the destination buffer, check to see if it is in the stack
       if is_stack_buffer(_addr, 1):
           print "STACK BUFFER STRCOPY FOUND at 0x%X" % addr
           break
   # If we detect that the register that we are trying to locate comes from some other register
   # then we update our loop to begin looking for the source of the data in that other register
   elif _op == "mov" and GetOpnd(_addr, 0) == opnd:
       op_type = GetOpType(_addr, 1)
       if op_type == o_reg:
           opnd = GetOpnd(_addr, 1)
           addr = _addr
       else:
           break
```

在上面的代码中，我们通过汇编代码执行向后搜索，查找保存目标缓冲区的寄存器获取其值的指令。代码还执行许多其他检查，比如检查，以确保我们没有搜索过函数的开始，也没有执行任何可能导致代码流更改的指令。代码还试图追溯任何其他寄存器的值，这些寄存器可能是我们最初搜索的寄存器的来源。例如，代码试图说明下面演示的情况。

```
... 
lea ebx [ebp-0x24] 
... 
mov eax, ebx
...
push eax
...
```

此外，在上面的代码中，我们引用了函数is_stack_buffer()。这个函数是这个脚本的最后一部分，在IDA API中没有定义。这是一个额外的帮助函数，我们将编写它来帮助我们寻找bug。这个函数的目的非常简单：给定指令的地址和操作数的索引，报告变量是否是堆栈缓冲区。虽然IDA API没有直接为我们提供这种功能，但它确实为我们提供了通过其他方式检查这一功能的能力。使用get_stkvar函数并检查结果是否为None或对象，我们能够有效地检查操作数是否是堆栈变量。我们可以在下面的代码中看到我们的帮助函数：

```
def is_stack_buffer(addr, idx):
   inst = DecodeInstruction(addr)
   return get_stkvar(inst[idx], inst[idx].addr) != None
```

请注意，上面的帮助函数与IDA7 API不兼容。在我们的下一篇博文中，我们将介绍一种新的方法来检查参数是否是堆栈缓冲区，同时保持与所有最新版本的IDA API的兼容性。

现在，我们可以将所有这些放到一个脚本中，如下所示，以便找到使用strcpy的所有实例，以便将数据复制到堆栈缓冲区中。有了这些，我们就可以将这些功能扩展到除了strcpy之外，还可以扩展到类似的功能，如strcat、printf等(请参阅[Microsoft禁止的函数列表](https://msdn.microsoft.com/en-us/library/bb288454.aspx))，以及向我们的脚本添加额外的分析。这个脚本的完整版在文章的底部可以找到。运行脚本可以成功地找到易受攻击的strcpy，如下所示。

[![](https://p5.ssl.qhimg.com/t0163832cb47113e3a4.png)](https://p5.ssl.qhimg.com/t0163832cb47113e3a4.png)



## 脚本

```
def is_stack_buffer(addr, idx):
   inst = DecodeInstruction(addr)
   return get_stkvar(inst[idx], inst[idx].addr) != None 

def find_arg(addr, arg_num):
   # Get the start address of the function that we are in
   function_head = GetFunctionAttr(addr, idc.FUNCATTR_START)    
   steps = 0
   arg_count = 0
   # It is unlikely the arguments are 100 instructions away, include this as a safety check
   while steps &lt; 100:    
       steps = steps + 1
       # Get the previous instruction
       addr = idc.PrevHead(addr)  
       # Get the name of the previous instruction        
       op = GetMnem(addr).lower() 
       # Check to ensure that we havent reached anything that breaks sequential code flow        
       if op in ("ret", "retn", "jmp", "b") or addr &lt; function_head:            
           return
       if op == "push":
           arg_count = arg_count + 1
           if arg_count == arg_num:
               #Return the operand that was pushed to the stack 
               return GetOpnd(addr, 0) 

for functionAddr in Functions():
   # Check each function to look for strcpy
   if "strcpy" in GetFunctionName(functionAddr): 
       xrefs = CodeRefsTo(functionAddr, False)
       # Iterate over each cross-reference
       for xref in xrefs:
           # Check to see if this cross-reference is a function call
           if GetMnem(xref).lower() == "call":
               # Since the dest is the first argument of strcpy
               opnd = find_arg(xref, 1) 
               function_head = GetFunctionAttr(xref, idc.FUNCATTR_START)
               addr = xref
               _addr = xref                
               while True:
                   _addr = idc.PrevHead(_addr)
                   _op = GetMnem(_addr).lower()                    
                   if _op in ("ret", "retn", "jmp", "b") or _addr &lt; function_head:
                       break
                   elif _op == "lea" and GetOpnd(_addr, 0) == opnd:
                       # We found the destination buffer, check to see if it is in the stack
                       if is_stack_buffer(_addr, 1):
                           print "STACK BUFFER STRCOPY FOUND at 0x%X" % addr                            break
                   # If we detect that the register that we are trying to locate comes from some other register
                   # then we update our loop to begin looking for the source of the data in that other register
                   elif _op == "mov" and GetOpnd(_addr, 0) == opnd:
                       op_type = GetOpType(_addr, 1)
                       if op_type == o_reg:
                           opnd = GetOpnd(_addr, 1)
                           addr = _addr
                       else:
                           break
```

完整的脚本在：[https://github.com/Somerset-Recon/blog/blob/master/into_vr_script.py[](https://github.com/Somerset-Recon/blog/blob/master/into_vr_script.py)](https://github.com/Somerset-Recon/blog/blob/master/into_vr_script.py%5B%5D(https://github.com/Somerset-Recon/blog/blob/master/into_vr_script.py)%E3%80%82)。

审核人：yiwang   编辑：边边
