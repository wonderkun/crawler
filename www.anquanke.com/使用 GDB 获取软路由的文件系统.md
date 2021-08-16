> 原文链接: https://www.anquanke.com//post/id/249993 


# 使用 GDB 获取软路由的文件系统


                                阅读量   
                                **23046**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01f6ebaf3c720237f5.png)](https://p1.ssl.qhimg.com/t01f6ebaf3c720237f5.png)



作者：Hcamael@知道创宇404实验室**<br>**

最近在研究某款软路由，能在其官网下载到其软路由的ISO镜像，镜像解压可以获取到rootfs，但是该rootfs无法解压出来文件系统，怀疑是经过了某种加密。

把软路由器安装到PVE上，启动后也无法获取到Linux Shell的权限，只能看到该路由厂商自行开发的一个路由器Console界面。可以开启telnet/ssh，可以设置其密码，但是连接后同样是Console界面。

这种情况下对该软路由进行黑盒研究，难度非常大，是为下策，不是无可奈何的情况下不考虑该方案。

所以要先研究该怎样获取到该路由的文件系统，首先想到的方法是去逆向vmlinux，既然在不联网的情况下能正常跑起来这个软路由，说明本地肯定具备正常解密的所有条件，缺的只是其加密方法和rootfs格式。在通常情况下处理解密的代码位于vmlinux，所以只要能逆向出rootfs的加解密逻辑，就可以在本地自行解压该文件系统了。

该思路的难度不大，但是工作量非常大，是为中策，作为备选方案。

因为该软路由是被安装在PVE上，使用kvm启动，所以可以使用gdb对其内核进行调试，也可以通过gdb修改程序内存和寄存器的值。从而达到任意命令执行的目的，获取Linux Shell。



## 使用GDB调试软路由

在PVE界面的`Monitor`选项中输入`gdbserver`，默认情况下即可开启gdbserver，监听服务器的1234端口。

获取vmlinux：`extract-vmlinux boot/vmlinuz &gt; /tmp/vmlinux`。

gdb进行调试：`gdb /tmp/vmlinux`。

然后挂上远程的gdbserver：`target remote x.x.x.x:1234`。

大多数情况下，断下来的地址都是为`0xFFFFFFFFxxxxxxxx`，该地址为内核地址，然后在gdb界面输入`continue`，让其继续运行。

想要获取Linux Shell，那么就需要执行一句获取Shell的shellcode，但是不管是执行反连shell还是bind shell的shellcode都太长了。为了缩减shellcode的长度，可以让shellcode执行一句`execve("/bin/sh", ["/bin/sh","-c","/usr/sbin/telnetd -l /bin/sh -p xxxxx"], 0)`命令（当然已经确定了存在`telnetd`，和其路径）。

下面为上述shellcode的大致代码(测试的目标为x86_64系统)：

```
0x00: /bin/sh\x00
0x08: -c\x00
0x10: cmd
0x100: 0x00
0x108: 0x08
0x110: 0x10
0x118: 0
mov rdi, 0x00
mov rsi, 0x100
xor rdx, rdx
xor rax, rax
mov al, 59
syscall
```

不过因为使用的是gdb，可以对程序内存寄存器进行修改，所以不需要这么长的shellcode，只需要执行下面的命令：

```
set *0x00=xxxx
set *0x04=xxxx
......
set $rdi=0x00
set $rsi=0x100
set $rdx=0
set $rax=59
set *((int *)$rip)=0x050F(syscall)
```

这里建议只对用户态代码进行修改，如果直接改内核态的代码，容易让系统崩溃。

接下来的步骤就是如何进入用户态，首先需要增加软路由的负载，可以访问一下路由器的Web服务，或者执行一些会长时间运行的程序（比如`ping`），然后按`ctrl+c`，中断程序运行，重复N次，如果不是运气不好的情况下，会很快断在一个地址开头不是`0xffffffff`的地址，这就是用户态程序的地址空间了。

接下来可以往栈、数据段内存写入我们要执行的命令，然后修改寄存器，修改当前`pc`值为`syscall`指令，再输入`contiune`，系统就会运行你想执行的命令了。

理论上该思路没啥问题，但是在实际测试的过程中发现了一些小问题。

在测试过程中，程序中断的用户态代码是`/bin/bash`的程序段，或者是`libc`的程序段，当修改代码段的代码时，不会像平常调试普通程序那样，修改的只是映射的内存代码，当程序退出后，修改的代码随同映射的内存一起释放了。当一个新的`bash`程序运行时，内存重新进行了映射，所以使用gdb修改当前程序的上下文，并不会影响到之后运行的程序。但是在调试内核的时候，进入用户态后，访问到的是该程序的真正内存区域，代码一经修改，除非系统重启，不然每次运行相同的程序，都将会运行修改后的代码。

所以按照上述理论修改了`/bin/bash`代码段的指令，执行了`/bin/sh -c "/usr/sbin/telnetd -l /bin/bash"`命令之后，`bash`这个程序实际的代码已经被破坏了，所以在该命令成功开启了`telnet`服务后，每当有用户连接这个`telnet`服务，根据`bash`程序代码被破坏的程度，程序将会有不同的异常（运气好，破坏的代码不重要，则不会影响到后续使用。运气不好，破坏的代码很重要，则可能无法再运行`bash`程序）。

比如下面这个测试案例：

```
?  ~ telnet 10.11.33.115 33333
Trying 10.11.33.115...
Connected to 10.11.33.115.
Escape character is '^]'.
bash-4.4# id
Connection closed by foreign host.
```

用户能成功连接到`telnet`服务，服务的banner正常显示，但是当执行`id`命令时，`telnet`服务却断开了连接，按照上述的分析，猜测是`bash`程序被修改的代码段位于`bash`程序处理用户输入的命令的函数中，所以当用户想执行`id`命令时，程序将会奔溃，导致`telnet`服务断开连接。

如果修改的代码位于`libc`的程序段，那将会造成更严重的后果，不仅是`telnet`服务甚至是操作系统的其他服务，运行到该`libc`的代码时，都会崩溃导致程序异常。

因为上述的原因，所以应该稍微修改一下思路，经过多次测试，发现最稳定，最不容易影响系统正常运行的思路如下：
1. 在代码段搜索`syscall`指令，比如：`find /h upaddr,lowaddr,0x050F`。
1. 然后把pc修改到该地址，`set $pc=0xAAAAAA`。
PS: 如果不修改指令，按原来的思路做，只需要把命令改成`telnetd -l /bin/sh`，用户连接到`telnetd`服务，执行命令时，将不会出现异常导致连接断开。不过这种方法治标不治本，只作为应急使用。



## 一键操作

准备写个gdb插件，一句指令完成我上述的流程。

选择开发一个gef的插件，在开发前收集了一些资料。

首先是参数寄存器：

```
arch/ABI     arg1  arg2  arg3  arg4  arg5  arg6  arg7  Notes
──────────────────────────────────────────────────────────────────
arm/OABI      a1    a2    a3    a4    v1    v2    v3
arm/EABI      r0    r1    r2    r3    r4    r5    r6
arm64         x0    x1    x2    x3    x4    x5    -
blackfin      R0    R1    R2    R3    R4    R5    -
i386          ebx   ecx   edx   esi   edi   ebp   -
ia64          out0  out1  out2  out3  out4  out5  -
mips/o32      a0    a1    a2    a3    -     -     -     See below
mips/n32,64   a0    a1    a2    a3    a4    a5    -
parisc        r26   r25   r24   r23   r22   r21   -
s390          r2    r3    r4    r5    r6    r7    -
s390x         r2    r3    r4    r5    r6    r7    -
sparc/32      o0    o1    o2    o3    o4    o5    -
sparc/64      o0    o1    o2    o3    o4    o5    -
x86_64        rdi   rsi   rdx   r10   r8    r9    -
x32           rdi   rsi   rdx   r10   r8    r9    -
```

然后是系统调用指令：

```
arm/OABI   swi NR               -           a1     NR is syscall #
arm/EABI   swi 0x0              r7          r0
arm64      svc #0               x8          x0
blackfin   excpt 0x0            P0          R0
i386       int $0x80            eax         eax.                 0x80CD
ia64       break 0x100000       r15         r8     See below
mips       syscall              v0          v0     See below
parisc     ble 0x100(%sr2, %r0) r20         r28
s390       svc 0                r1          r2     See below
s390x      svc 0                r1          r2     See below
sparc/32   t 0x10               g1          o0
sparc/64   t 0x6d               g1          o0
x86_64     syscall              rax         rax    See below     0x050F
x32        syscall              rax         rax    See below
```

然后收集了一些架构`execve`的系统调用号：

```
execve:
arm64/h8300/hexagon/ia64/m68k/nds32/nios2/openrisc/riscv32/riscv64/c6x/tile/tile64/unicore32/score/metag: 221
arm/i386/powerpc64/powerpc/s390x/s390/arc/csky/parisc/sh/xtensa/avr32/blackfin/cris/frv/sh64/mn10300/m32r: 11
armoabi: 9437195
x86_64/alpha/sparc/sparc64: 59
x32:  1073742344
mips64: 5057
mips64n32: 6057
mipso32: 4011
microblaze: 1033
xtensa:    117
```

最后得到如下所示的代码：

```
@register_command
class ExecveCommand(GenericCommand):
    """use execve do anything cmd"""
    _cmdline_ = "execve"
    _syntax_  = "`{`:s`}` [cmd]|set addr [address]".format(_cmdline_)
    _example_ = "`{`:s`}` /usr/sbin/telnetd -l /bin/bash -p 23333\n`{`:s`}` set addr 0x7fb4360748ae".format(_cmdline_)
    _aliases_ = ["exec",]
    def __init__(self):
        super().__init__(complete=gdb.COMPLETE_FILENAME)
        self.findAddr = None
        return

    @only_if_gdb_running
    def do_invoke(self, argv):
        '''
        mips/arm todo
        '''
        if len(argv) &gt; 0:
            if argv[0] == "debug":
                # debug = 1
                dofunc = print
                argv = argv[1:]
            elif argv[0] == "set":
                if argv[1] == "addr":
                    self.findAddr = int(argv[2], 16)
                    info("set success")
                return
            else:
                # debug = 0
                dofunc = gdb.execute
        else:
            err("The lack of argv.")
            return
        cmd = " ".join(argv)
        cmd = [b"/bin/sh", b"-c", cmd.encode()]
        # print(current_arch.sp)
        # print(current_arch.pc)
        # print(current_arch.ptrsize)
        # print(endian_str())
        # print(current_arch.syscall_instructions)
        # print(current_arch.syscall_register)
        # print(current_arch.special_registers)
        # print(current_arch.function_parameters)
        # print(current_arch.arch)
        # print(current_arch.get_ith_parameter)
        # print(current_arch.gpr_registers)
        # print(current_arch.get_ra)
        # write_memory
        try:
            rsp = current_arch.sp
            nowpc = self.findAddr or current_arch.pc
        except gdb.error as e:
            err("%s Please start first."%e)
            return
        bit = current_arch.ptrsize
        if current_arch.arch == "X86":
            arg0 = "$rdi" if bit == 8 else "$ebx"
            arg1 = "$rsi" if bit == 8 else "$ecx"
            arg2 = "$rdx" if bit == 8 else "$edx"
            sysreg = current_arch.syscall_register
            sysreg_value = 59 if bit == 8 else 11
            syscall_instr = 0x050F if bit == 8 else 0x80CD
        else:
            err("%s can't implementation." % current_arch.arch)
            return
        spc = nowpc &amp; (~0xFFF)
        res = gdb.execute("find /h %s,%s,%s"%(spc, spc+0x10000, syscall_instr), to_string=True)
        if "patterns found." not in res:
            err("can't find syscall. Please break in libc.")
            return
        newpc = res.splitlines()[0]
        endian_symbol = endian_str()
        endian = "little" if endian_symbol == "&lt;" else "big"
        startaddr = rsp + 0x100
        args_list = []
        # cmd write to stack
        for cstr in cmd:
            args_list.append(startaddr)
            cstr += b"\x00" * (4 - (len(cstr) % 4))
            length = len(cstr)
            write_memory(startaddr, cstr, length)
            startaddr += length
            # for i in range(0, len(cstr), 4):
            #     t = hex(struct.unpack(endian_symbol+'I', cstr[i:i+4])[0])
            #     dofunc("set  *(%s)=%s"%(hex(startaddr), t))
                # startaddr += 4
        args_list.append(0)
        # set cmd point (rsi)
        rsiAddr = rsp + 0x50
        endian = "little" if endian_str() == "&lt;" else "big"
        addrvalue = b""
        for addr in args_list:
            addrvalue += addr.to_bytes(bit, endian)
        write_memory(rsiAddr, addrvalue, len(addrvalue))
            # for i in range(0, len(addr), 4):
            #     t = hex(struct.unpack(endian_symbol+'I', addr[i:i+4])[0])
            #     dofunc("set  *(%s+%d)=%s"%(hex(rsiAddr), i, t))
            # rsiAddr += bit

        # set first arguments.
        dofunc("set %s=%s"%(arg0, hex(args_list[0])))
        # set second arguments
        dofunc("set %s=%s"%(arg1, hex(rsp + 0x50)))
        # set third arguments
        dofunc("set %s=0"%arg2)
        # set syscall register
        dofunc("set %s=%s"%(sysreg, sysreg_value))
        # set $pc=$sp
        dofunc("set $pc=%s"%newpc)
        # set *$pc
        # dofunc("set *(int *)$pc=%s"%hex(syscall_instr))
        # show context
        # dofunc("context")
        # continue
        dofunc("c")
        return
```



# <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

来实际试一试：

[![](https://p4.ssl.qhimg.com/t01b55f6f852908b69b.png)](https://p4.ssl.qhimg.com/t01b55f6f852908b69b.png)
