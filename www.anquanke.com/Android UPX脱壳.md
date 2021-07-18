
# Android UPX脱壳


                                阅读量   
                                **809184**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/197643/t01839cfcea0830fd08.jpg)](./img/197643/t01839cfcea0830fd08.jpg)



## 写在前面

因为我不是pc平台过来的，而是直接从Android入门的，所以upx壳其实一开始并不了解，后来接触到，但是可以直接动态调试或者做个内存快照，对我来说加没加upx其实对我逆向分析影响不大。另一方面upx壳因为开源且其实有很多脱壳的教程，所以一直觉得有些过时、保护力度不足，似乎不值得花太多时间再去深入。但是有些公司的面试官不这么觉得，似乎对于他来说，你说会写vmp但是不了解upx脱壳修复很可笑，所以趁着假期把这个坑补上。

基于快速解决问题的原则，搜了一些upx脱壳的文章，大概可以分为两类。<br>
1：是基于你熟悉upx源码的情况下，梳理出逻辑和数据结构，dump修复等。<br>
2：是基于经验、特征，直接定位特征代码，断点、dump修复等。

对于1是我想要的，但是大概看了下upx源码似乎还挺大，Android加upx壳问题很多且并没有修复，加上没想过修复upx壳的bug(我的强迫症比较严重，如果看完源码我很难能停下不去修复bug)，所以最后放弃了这条路。

对于2，找到的一些文章很多是pc平台的，Android的还是较少的，且似乎有些藏着掖着的嫌疑，当然也许是个人的主观判断，我也不想再搜或者去推敲不明确的地方，不如直接自己来吧，看能不能黑盒推理出来。



## 分析

找了个第三方app内加了upx壳的so，没有clone upx对自己的so加壳。

首先看一下这个加了upx壳的so的数据结构，第一个可读可执行的段包含了代码段，干脆就叫代码段吧。

代码段大小为136728=0x21618，加载到内存是4096/一页对齐，那么占用内存大小为0x22000。而接下来的数据段在内存中偏移是0x3dee8，那么起始页应该是0x3d000，0x3d000-0x22000=0x1b000，数据段和代码段隔了27页，太不正常了，一般编译出来的so相隔1页，所以应该是upx改的，但是这个数据段的偏移是编译时确定的，upx肯定不可能反汇编所有代码修改偏移，所以这个数据段的偏移是没有问题的，而且p_offset=0x21ee8，和p_vaddr也是相差一页的。所以可以推理出应该是改了代码段的大小，原来的代码段大小肯定不是0x21618，应该是在0x3b000-0x3d000之间(考虑到一般正常so会设置一页的间隔，那么可以缩小范围到0x3b000-0x3c000之间)。

### <a class="reference-link" name="%E4%B8%BA%E4%BB%80%E4%B9%88%E6%95%B0%E6%8D%AE%E6%AE%B5%E7%9A%84%E5%81%8F%E7%A7%BB%E6%98%AF%E4%B8%8D%E8%83%BD%E6%94%B9%E7%9A%84"></a>为什么数据段的偏移是不能改的

如果对elf不是特别熟悉的话，这里我以一个正常的so为例来看下为什么说这个数据段的偏移是不能改的，

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015e0de78b8c57fcd8.png)

代码中从是偏移为3f004的地址取数据，这是经过ida优化的，实际指令含义不是这样，我们去掉优化(当然这样也还没完全去掉优化，你可以自己再解析指令，0x3a8c0是存储在指令后面的，现在是条LDR伪指令)。

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010a928deea7f626e6.png)

可以看到R1寄存器存储的是0x3a8c0，0x3a8c0+0x4740+4(流水线)=0x3f004。指向的是.data节(这个节在数据段)。

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0177c90edf75075613.png)

通过上面的例子可以发现代码中取数据是写死的偏移值，而这个.data中的数据实际是在so文件的0x23000偏移开始的，但是在内存中是加载到0x3f000偏移处的。

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01407c6fdcf00d3209.png)

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015926961c0d6ce290.png)

所以这个偏移值在代码里面写死了，除非反汇编所有代码，解析出所有对内存的访问修改偏移值，基本上是不现实的，因为有花指令、运行时确定pc等操作会导致反汇编无法正确区分汇编指令和数据(这也是写arm vmp遇到无法完美解决的问题)。所以.data以至整个数据段都是要符合这个偏移的。

### <a class="reference-link" name="%E8%A7%82%E5%AF%9F%E5%86%85%E5%AD%98"></a>观察内存

经过推理得出代码段大小被修改了，结合着之前听说的upx壳的原理，那么应该是真实代码段被压缩或者加解了，之后会覆盖内存中的代码段。

写一个app把so加载到内存中

```
c948e000-c9491000 r-xp 00000000 103:37 693882                            /data/app/com.zhuo.tong.elf_fix-rnY3xpLMrzuqsfXFyaWTRw==/lib/arm/libxx.so
c9491000-c94ca000 r-xp 00000000 00:00 0
c94ca000-c94cb000 ---p 00000000 00:00 0
c94cb000-c94cd000 r--p 00021000 103:37 693882                            /data/app/com.zhuo.tong.elf_fix-rnY3xpLMrzuqsfXFyaWTRw==/lib/arm/libxx.so
c94cd000-c94ce000 rw-p 00023000 103:37 693882                            /data/app/com.zhuo.tong.elf_fix-rnY3xpLMrzuqsfXFyaWTRw==/lib/arm/libxx.so
c94ce000-c9521000 rw-p 00000000 00:00 0                                  [anon:.bss]
```

0xc94ca000-0xc948e000=0x3c000,符合之前的推测：0x3b000-0x3c000之间。所以这部分才是真实的代码段。数据段的起始就是c94cb000+0xee8，再加上内存占用344964，得到0xC952026C，内存对齐后得到0xC9521000，刚好对的上。所以可以把0xc948e000-0xc9521000都dump下来(修改内存权限，间隔的部分没有读的权限)，也可以不dump c94ce000-c9521000，因为这部分是bss节，不占用so空间，也可以只dump代码段0xc948e000-0xc94ca000。

dump的区间不同那么修复起来也是有些差别的。为了文章逻辑不乱掉，把修复放在后面。

### <a class="reference-link" name="%E9%AA%8C%E8%AF%81"></a>验证

对dump下来的文件进行验证，拖入ida，忽略解析错误。

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01da91d6f190d5abff.png)

未脱壳之前的so，导出了JNI_OnLoad,记下地址，跳到dump的so的相应地址。

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01857a4f0f275827f1.png)

可以确定已经解密出真实的指令了，所以对于dump来说完全是可以脱离其他分析、调试的。



## 修复

dump下来的so包含指令，但是ida等反编译工具不能自动识别修复，所以修复的事情就需要自己来做了。我dump的范围是0xc948e000-0xc94ce000,把整个代码段、数据段都dump下来了，这是最麻烦的一种方式，因为有好几个地方都要修复。

### <a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E7%A8%8B%E5%BA%8F%E5%A4%B4%E5%92%8C%E8%8A%82%E8%A1%A8"></a>修复程序头和节表

1、首先修复程序头代码段的大小，其实直接指定为0x3c000也可以，当然可以更精确一些，

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01acf3b9a6d0af534c.png)

从0x3c000倒着找非0的值，例如可以是0x3bf9f或者0x3bfa0，因为代码段最后是.rodata，一般存放的是字符串。本来正常编译出来的so，.rodata之后是填充的0到一页。所以这个代码段的大小不用很精确，只要保证正确即可，因为.rodata不影响后面的节的修复。

2、因为dump的时候包含了全0的一页，所以代码段和数据段的间隔为0了。

```
c94ca000-c94cb000 ---p 00000000 00:00 0
```

那么相应的数据段的p_offset就改成和p_vaddr一致即可，都为0x3DEE8。

因为DYNAMIC段和数据段在一起，同样的也需要修复程序头中的p_offset，就改成和p_vaddr一致即可。

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0121629f1480d0a412.png)

修复后如上图。

3、程序头已经修复好了，接下来就可以修复section/节表了。已经写好自动修复的代码，根据程序头、.dynamic重建plt、got、.fini_array等。

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a32bd8b756d18e39.png)

一些不在.dynamic的节通过其他节来确定，比如程序头还有.ARM.exidx节的信息，那么根据.plt节确定.text节的开头，通过.ARM.exidx节确定.text节的结尾，当然这个.text节还包含.ARM.extab节，但是不影响解析和执行。最终能自动修复的节有：<br>
.dynsym、.dynstr、.hash、.rel.dyn、.rel.plt、.text、.ARM.exidx、.rodata、.fini_array、.init_array、.dynamic、.got、.data、.bss、.data.rel.ro、.shstrtab。

以上都是可以自动修复且重要的节，一些其他不重要的比如.comment、.note.gnu.gold-ve等编译器、gnu相关的节也可以通过字符串和其他节的区间来确定，不过没什么必要，因为这些节对解析和执行无影响。

修复之后，ida已经可以不报错的正常解析so了，

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0151d495b052aa7403.png)

导入导出函数已经能解析。

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018c5b2a09b0ebfd61.png)

段和节也能正确解析。

### <a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E9%87%8D%E5%AE%9A%E4%BD%8D%E6%95%B0%E6%8D%AE"></a>修复重定位数据

现在这个so修复后可以被ida等正常解析、反编译，但还不能正常运行，因为.data、.got等节中的数据被写入绝对地址了，那么需要对这些重定位后的数据进行还原。

当然这里可以只dump代码段，使用加壳的so的数据段，通过观察可以发现upx壳并没有修改数据段，那么使用数据段进行替换，测试是可行的。

还可以自己写一个linker或者直接拿系统的linker源码修改或者修改linker可执行文件，加载这个upx壳的so不执行重定位。为什么可以这么做呢，简单看了upx壳的指令，发现mprotect等都是通过系统调用/软中断实现的，基于这个结果我反推一下。为什么不直接使用mprotect等函数呢，因为这个upx壳像是寄生在这个宿主so一样，要使用这些导入函数需要借助宿主的got表、plt等，那么就需要解析so，确定got表中mprotect函数的地址，这是理想情况，宿主导入表存在所需要的函数，但是如果宿主没有引用导入这些函数岂不是就gg了，如果加入一项到got表，那么后面的.bss的偏移不就被改变了，参考上面的为什么偏移不能改变。所以反推或者我从实现者的角度考虑应该是直接使用软中断，既然壳没有使用导入函数，那么不进行重定位、写入函数地址到got表，并不影响壳的执行，也就是说壳还是能解密还原真实的代码到内存中。

为了完整解决这里就不采用偷懒的方式了，直接对重定位后的数据进行还原。<br>
做法可以有两种.<br>
1、比如修复好了节表，那么获取.fini_array、.data、.init_array、.data.rel.ro、.got表的数据逐项校验值是否在基址和内存中so结束地址，如果在这个范围内就用值-基址，覆盖值即可。当然这样会漏掉got表中外部导入的函数，需要自己再解析下那些是导入的外部函数/数据，指向plt的偏移。

2、根据DT_JMPREL和DT_REL确认那些重定位的数据，修复方式是一样的。

经过修复后确实可以，但是可能存在一个问题，就是dump时机造成的影响，因为.data中的也存在可重定位的数据，比如指针等，那么就是说这个数据不只可读还可写，dump下来的可能不是原始的被重定位后的数据而是程序自身逻辑写入的其他数据了。

### <a class="reference-link" name="init%E5%87%BD%E6%95%B0%E7%9A%84%E4%BF%AE%E5%A4%8D"></a>init函数的修复

经过以上的修复就可以正确运行了吗，其实还不一定，因为还有一个init函数没有修复，原来导出的init函数是upx壳的入口函数：

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01640e7cff63421b72.png)

而经过以上修复之后：

[![](./img/197643/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01941556a69a484428.png)

把一个函数给截断了，肯定无法正确执行。为什么会这样？也可以反推一下，壳还原代码之后可以直接调用真实的init函数执行，不需要还原重写init函数的地址，也没意义。所以dump下来的dynamic还是壳的init函数的地址。

这个函数的地址的重新定位，黑盒能做到应该只能是以下两种方式：<br>
1、反汇编之后查找所有的无参函数，这还真是一个概率性的事情，理论上一个无参的且没有被其他任何函数引用的就应该是了，但是取决于存不存在其它的一样行为的函数，或者函数多不多，当然这个可以借助ida的api实现。所以只能说有几率能找到真正的init函数。

2、把init函数指向一个无参不影响程序逻辑的函数(如果存在)或者从dynamic去掉init函数。运行测试，如果正常运行说明可能这个init函数没做什么有意义的事情，可能就是为了能加壳，听说加upx壳必须有init函数，不过其实可以解析.dynamic确定和下一个节有没有padding，有padding的话插入一个即可，当然没有这么做是太麻烦还是兼容性问题不好推测，需要数据测试。

我这个样本去掉init函数后可以正常运行，所以算我运气好。如果不能的话，我想应该需要动态调试一下了，既然知道了都是通过系统调用实现的函数，那么根据系统调用号确定下行为，再恢复真实指令后，观察pc寄存器，第一次跳到内存中的代码段中地址应该就是init函数的地址，减去基址即可得到偏移。



## 总结

可见这种加壳方式似乎并不难，基本上完全黑盒就可以脱壳了。当然也可能是因为已经对elf数据结构、linker有了一定了解，所以觉得不难，无法完全客观的判断。

这只是我自己的一种脱upx壳的方式，不一定是好的也不一定适合其他人。我想应该还是思路和推理更重要一些吧，其实很多问题、事情可以类似的推理出来，没做过不代表不会做、不能做。

除了init函数外，其他的dump、程序头修复、节表修复都可以自动完成，整理之后上代码。init函数的自动确定难点在于都是系统调用不好hook，根据特征确定的话不算自动化，稍微变形的壳就识别不了了。也许可以再模拟执行的环境中试试，hook系统调用，比如当mprotect系统调用后且是操作的代码段，那么检查pc的值，当是代码段的值时记录下来，就是init函数的地址。或者拦截mprotect系统调用，把代码段改成不可执行，这样执行到init函数的时候异常，捕获异常或者分析日志得到地址就是init函数地址。
