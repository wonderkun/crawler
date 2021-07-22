> 原文链接: https://www.anquanke.com//post/id/194303 


# 跟小黑学漏洞利用开发之SEH+Egghunter


                                阅读量   
                                **1261119**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t015c9727782b25b66c.png)](https://p5.ssl.qhimg.com/t015c9727782b25b66c.png)



本篇缓冲区漏洞利用开发计划在egghunter之后发出，但是由于各种原因耽误了。本篇我们将不再依赖于mona插件帮助我们寻找可使用地址，只是希望大家理解——工具永远只是辅助，技术才是本质的道理。

同时本篇引入利用Fuzz模糊测试，带领大家领略从Fuzz到exploit全流程，利用程序依然采用vulnserver漏洞演示程序。攻击指令“GMON”，我们需要创建针对GMON指令SPIKE模板，稍后进行模糊测试该指令

模板内容如下：

[![](https://p3.ssl.qhimg.com/t0185f8a803cdee77f7.png)](https://p3.ssl.qhimg.com/t0185f8a803cdee77f7.png)



## 利用SPIKE模糊测试

使用模板，我使用SPIKE的generic_send_tcp解释器在短时间内模糊了应用程序。

[![](https://p4.ssl.qhimg.com/t013eb5ac27ab67a021.png)](https://p4.ssl.qhimg.com/t013eb5ac27ab67a021.png)

如下图当发送至5000字节时候程序失去连接崩溃

[![](https://p0.ssl.qhimg.com/t0119060a01d2b89590.png)](https://p0.ssl.qhimg.com/t0119060a01d2b89590.png)



## 分析崩溃原因

执行此代码导致应用程序崩溃。正如我们看到，EIP没有被41覆盖

[![](https://p2.ssl.qhimg.com/t01b593b9f38f6e7cad.png)](https://p2.ssl.qhimg.com/t01b593b9f38f6e7cad.png)

通过观察SEH，可以看到SEH记录被A覆盖。因此，这导致了应用程序崩溃原因。

[![](https://p1.ssl.qhimg.com/t017231071b5a59fbe6.png)](https://p1.ssl.qhimg.com/t017231071b5a59fbe6.png)



## 编写POC脚本

通过前面分析要验证导致崩溃的缓冲区长度，我们已经写了下面的POC脚本，其中包含5000个字节。

[![](https://p4.ssl.qhimg.com/t01ff12ffb32b941c42.png)](https://p4.ssl.qhimg.com/t01ff12ffb32b941c42.png)

执行POC脚本成功复现了崩溃。

[![](https://p3.ssl.qhimg.com/t0194ba3c7cce86604c.png)](https://p3.ssl.qhimg.com/t0194ba3c7cce86604c.png)



## 分析偏移量

为了确定覆盖SEH的偏移量，我们使用!mona pc 5000生成了一个5000字节的唯一字符串，然后修改了代码。

[![](https://p3.ssl.qhimg.com/t01d531143dfb9a4f30.png)](https://p3.ssl.qhimg.com/t01d531143dfb9a4f30.png)

使用!mona findmsp，发现nSEH记录被3495字节的偏移量覆盖。

[![](https://p2.ssl.qhimg.com/t01834265b7f0bb471d.png)](https://p2.ssl.qhimg.com/t01834265b7f0bb471d.png)

然后，我将漏洞利用修改为以下内容。

[![](https://p3.ssl.qhimg.com/t01cc01dbb4f2b5422d.png)](https://p3.ssl.qhimg.com/t01cc01dbb4f2b5422d.png)

如图所示，偏移量正确。nSEH被4 B覆盖，而4 C覆盖了SEH。

[![](https://p5.ssl.qhimg.com/t01965c6dc852e40e3e.png)](https://p5.ssl.qhimg.com/t01965c6dc852e40e3e.png)



## 分析坏字节

如该图所示，D的缓冲区位空间不足以将所有坏字节存储于B和C后面。因此我们需方放入A缓冲区中。修改如下代码

[![](https://p3.ssl.qhimg.com/t0198333dd4d9c1ba4f.png)](https://p3.ssl.qhimg.com/t0198333dd4d9c1ba4f.png)

可以看出，除了0x00空字节外，没有其他坏字节被找到。

[![](https://p1.ssl.qhimg.com/t01205d16d34316eb97.png)](https://p1.ssl.qhimg.com/t01205d16d34316eb97.png)



## 寻找包含pop、pop、ret地址

这里我们不一定必须使用mona插件中的!mona she，我们可以利用调试插件——checksec，帮助我们来完成查找，通过分析vulnserver中essfunc.dll。起始地址62500000到62508000.因此我们只需要寻找此地址内包含pop、pop、ret指令即可。

[![](https://p3.ssl.qhimg.com/t01f3c17a26c1185fc2.png)](https://p3.ssl.qhimg.com/t01f3c17a26c1185fc2.png)

如图所示地址非常符合我们的要求

[![](https://p1.ssl.qhimg.com/t018b00c855df7f6d3d.png)](https://p1.ssl.qhimg.com/t018b00c855df7f6d3d.png)

下面显示了更新的代码。

[![](https://p3.ssl.qhimg.com/t01271d66908cc42efc.png)](https://p3.ssl.qhimg.com/t01271d66908cc42efc.png)

我们调整后的代码进行攻击尝试有效，并且SEH被我们刚刚找到包含POP POP RET指令的地址所覆盖。

[![](https://p4.ssl.qhimg.com/t011956e029400ac078.png)](https://p4.ssl.qhimg.com/t011956e029400ac078.png)

通过按SHIFT + F9传递异常，我们被重定向到POP POP RET指令的地址。

[![](https://p3.ssl.qhimg.com/t01ea8de3c478618c14.png)](https://p3.ssl.qhimg.com/t01ea8de3c478618c14.png)

进入POP POP RET指令将我们重定向到nSEH记录，该记录包含B的4个字节。

[![](https://p2.ssl.qhimg.com/t01cb7ac2151c8ddb95.png)](https://p2.ssl.qhimg.com/t01cb7ac2151c8ddb95.png)



## 利用回跳技术

下一步将使用跳转指令更改这4个B，将我重定向到我的shellcode。但是，如上所述，我不能使用D的缓冲区，因为它只有二十多个字节长。即使是利用egghunter，这也不够，因为它需要32个字节的空间。由于A的缓冲区位于4个B的缓冲区的正上方，因此不得不跳回去。为此，无法进行“长跳”操作，因为对应opcode的长度为5个字节。仅有4个字节的空间的nSEH不能满足要求。相反，我跳回了50个字节，就像之前的文章一样（不知道的小伙伴可以回看跟小黑学漏洞利用开发之egghunter）。下面显示了我使用的代码。

[![](https://p2.ssl.qhimg.com/t01cd67e18229f03c74.png)](https://p2.ssl.qhimg.com/t01cd67e18229f03c74.png)

如此处所示，回跳起了作用。下一步是将egghunter代码放在此位置。

[![](https://p5.ssl.qhimg.com/t016587822a16744151.png)](https://p5.ssl.qhimg.com/t016587822a16744151.png)



## Egghunter

我们使用!mona egg -t HACK生成egghunter代码。

[![](https://p5.ssl.qhimg.com/t01577e17e1db8ce3fc.png)](https://p5.ssl.qhimg.com/t01577e17e1db8ce3fc.png)

在使用egghunter之前，我们必须先确定egghunter代码之前A的偏移量。为此，进行了一个简单的计算：A的原始3495字节+向回跳转的Opcode占用2字节-向后跳转的距离为50字节= A *3447字节。下面我们重新调整代码。

[![](https://p4.ssl.qhimg.com/t01addf993fc2c44f33.png)](https://p4.ssl.qhimg.com/t01addf993fc2c44f33.png)

重定向和计算正常，当前指令指向egghunter。如图所示。

[![](https://p2.ssl.qhimg.com/t01197266a00eae8853.png)](https://p2.ssl.qhimg.com/t01197266a00eae8853.png)



## 生成shellcode&amp;存放shellcode

然后，我们使用MSFvenom生成了一个shellcode。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0147de050f7a38c03c.png)

由于A的剩余缓冲区仍然很大，因此决定将egghunter代码和shellcode放在GMON命令之后。



## 漏洞攻击

下面为大致执行流程。

[![](https://p4.ssl.qhimg.com/t0124f3c99dd8be5f0c.png)](https://p4.ssl.qhimg.com/t0124f3c99dd8be5f0c.png)

执行最终的利用代码后，egghunter在GMON命令之后成功定位了egg / tag和shellcode 。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0151bf9052bad2bf76.png)

Shellcode运行，依旧在目标机器开启在4444 / tcp监听端口。最后要做的是连接到此端口以Getshell。

[![](https://p4.ssl.qhimg.com/t01a193acd1115c8e04.png)](https://p4.ssl.qhimg.com/t01a193acd1115c8e04.png)
