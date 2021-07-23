> 原文链接: https://www.anquanke.com//post/id/236492 


# 一次被MSRC坑的经历


                                阅读量   
                                **216812**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01c65993e5bb8a9a97.jpg)](https://p4.ssl.qhimg.com/t01c65993e5bb8a9a97.jpg)



## 前言

这个漏洞真的是被微软坑了，虽然即使微软认了也没多少钱，但是这么一搞钱也没了，CVE也没了。什么原因造成的？具体是因为之前我们提交了一个报告，没有给他具体的exp，怎么泄露出信息。他说要把报告关了，后面我们重新整出了可以泄露出信息的PoC，我以为他的意思是让我们重新打开一个报告，谁知道他是让我们在原有的报告上重新上传一份附件。然后现在MSRC把整个功能移除了。再然后总共提交的两个报告都被关了。本来都懒得发文章，这次发出来也只是吐槽下。



## 漏洞详情

这个漏洞就是一个普通的越界读的漏洞。就简单的给大家分析下看下吧。emmm，这个漏洞是我的小伙伴[@lm0963](https://github.com/lm0963)费了点精力分析的，现在不多说就上代码。漏洞点在msrawimage_store的组件中。

```
1.     __int64 __fastcall sub_18005BE40(__int64 a1, __int64 a2, int a3, int a4)  
2.      
3.    ……  
4.      v7 = 0;  
5.      do  
6.      `{`  
7.        v22 = 0;  
8.        v8 = *(_QWORD *)(a2 + 56);  
9.        v9 = (unsigned int *)(*(_QWORD *)(a2 + 0x50) + v7); // v9 point to a heap buffer, in this case the size of the heap buffer is 0x7e4.  
10.        ……  
11.        for ( i = 0; i &lt; *(_DWORD *)(a2 + 0x2C); ++v9 ) // *(a2 + 0x2c) is under our control, it is 0x700 in this case, offset 0x2151c in poc.x3f. So the maximum value of v9 is *(a2 + 0x50) + v21 * *(a2 + 0x30) + *(a2 + 0x2c) = *(a2 + 0x50) + 0x1 * 0x100 + 0x700 = *(a2 + 0x50) + 0x800 &gt; *(a2 + 0x50) + 0x7e4
12.        `{`  
13.          v12 = *v9; // Out-Of-Bounds Read here  
14.          …… // Some operations on image pixels. Due to the use of random data on the out-of-bounds heap, it will be garbled  
15.        `}`  
16.        v7 += v21; // v21 is under our control, it is 0x1 in this case. Offset  0x21520 in poc.x3f  
17.        ++v6;  
18.      `}`  
19.      while ( v6 &lt; *(_DWORD *)(a2 + 0x30) );  // *(a2 + 0x30) is under our control too, it is 0x100, offset 0x21518 in poc.x3f  
20.    `}`  
21.    return sub_180085760((unsigned __int64)&amp;v20 ^ v24);
```

上面就是简单的漏洞点分析，下面贴下漏洞崩溃信息的图片。

[![](https://p0.ssl.qhimg.com/t01c860d2819f73676f.png)](https://p0.ssl.qhimg.com/t01c860d2819f73676f.png)

[![](https://p1.ssl.qhimg.com/t01434809d26f675d7c.png)](https://p1.ssl.qhimg.com/t01434809d26f675d7c.png)

下面是信息泄露的截图，你可以看到每次打开图片泄露出的像素都是不一样的。

[![](https://p5.ssl.qhimg.com/t0164882ced835db0d2.png)](https://p5.ssl.qhimg.com/t0164882ced835db0d2.png)



## 结尾

再吐槽下，微软有时候是真的坑！赏金降到1/5不说，连oob read要实际泄露信息他们才修。
