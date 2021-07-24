> 原文链接: https://www.anquanke.com//post/id/158818 


# Chakra OP_NewScObjArray Type Confusion远程代码执行漏洞分析与利用


                                阅读量   
                                **173831**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t0113296b189609b298.jpg)](https://p3.ssl.qhimg.com/t0113296b189609b298.jpg)

## 1.漏洞描述

漏洞编号：无<br>
影响版本：Chakra &lt;=  1.10.0

此漏洞是我去年11月份发现的，在今年的七月微软的发布版本中被修掉。该漏洞成因在于：Interpreter在执行OP_NewScObjArray操作码指令时处理不当，在OP_NewScObjArray_Impl函数内有一个结构体之间的强制转换，导致了类型混淆，成功利用该漏洞可导致远程代码执行。



## 2.测试环境

```

```

### 3.2 漏洞成因

## 4.漏洞利用
- – 小堆 (0 &lt; size &lt;= 0x300)：每隔0x10为一个堆桶（步长为0x10),对齐方式：0x10 实现方式：size =&gt; 堆桶的 map 映射。 例如：0x10、0x20、0x30… 一共(0x300 / 0x10 = 0x30个堆桶）
- – 中堆 (0x300 &lt; size &lt;= 0x2000)：每隔0x100为一个堆桶（步长为0x100),对齐方式：0x100 实现方式：size =&gt; 堆桶的 map 映射。例如：0x400、0x500、0x600…一共(0x2000-0x300 / 0x100 = 0x1D个堆桶）
- – 大堆 (size &gt; 0x2000)：对齐方式：0x10 实现方式：堆桶之间的链表串连。
```

```

由于 0x10177 &gt; 0x2000 的内存大小在大堆范畴，所以由大堆来分配内存。

综合 1），2），3），及其深入分析之后，要能够精准控制内存的堆喷，越界写一些内存关键数据（如：长度、数据存储指针等），选用array进行堆喷可以满足要求，本利用中选择越界修改array的长度来实现漏洞利用。堆喷之后的内存结构如下：

完整的漏洞利用步骤如下：<br>
a. 触发漏洞之后，pre_trigger_arr的长度被修改为一个指针，此时pre_trigger_arr可越界写，但不能越界读。<br>
b. 通过pre_trigger_arr越界写，修改trigger_arr的长度，此时trigger_arr可越界读写。<br>
c. 通过trigger_arr越界读，可泄露fill_leak_arr中的任意一个元素对象的地址。<br>
d. 通过pre_trigger_arr越界写，修改trigger_arr的数据存储指针为DataView对象地址偏移，把DataView数据头伪造成trigger_arr的元素数据。<br>
e. 通过trigger_arr正常的写，修改DataView的arrayBuffer的数据指针。<br>
f. 通过DataView正常读取，可达到任意地址读写的目的。



## 5.漏洞演示

a. 通过任意地址读写，泄露chakra.dll的基地址。<br>
b. 通过调用GetProcAddress函数，泄露msvcrt.dll中malloc函数的地址。<br>
c. 通过调用GetProcAddress函数，泄露kernel32.dll中WinExec函数的地址。<br style="box-sizing: border-box;">[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bjyt.s3.addops.soft.360.cn/blog/20180903/upload_3eb3badbcc31f7ef19d797cfdd445532.gif)



## 6.漏洞补丁

补丁前：

补丁后：

从上面补丁前后的对比可知，补丁后OP_NewScObjArray_Impl函数代码中有问题的代码被优化掉了。



## 7.exp
- [exp地址](https://github.com/bo13oy/ChakraCore/tree/master/%231)


## 8.参考链接
- [ChakraCore v1.8.0](https://github.com/Microsoft/ChakraCore/releases/tag/v1.8.0)
- [pwnjs](https://github.com/theori-io/pwnjs)